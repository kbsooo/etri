#!/usr/bin/env python3
"""H046: bifurcated Q2 regime decoder HS-JEPA.

H043/H045 still move Q2 as one phase direction. H046 tests a larger world
model: Q2 phase is conditional on human-state regime.

The visible context is the H044/H045 route latent. The hidden target is not
"which rows should move" but "which regime receives which Q2 action":

    H042-like core          -> strong validated phase move
    public/q2 regime tail   -> weak extension
    private-routine tail    -> veto or small opposite correction

If this is real, conditional route-action features should prefer a bifurcated
candidate over single-alpha top-k supports.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h046_q2_bifurcated_regime_decoder_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q2_I = TARGETS.index("Q2")
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H043 = "submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv"
H045 = "submission_h045_condroute_q2regime75_a0.66_5988dfb9_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    regime: str
    core_alpha: float
    public_alpha: float
    private_alpha: float
    neutral_alpha: float
    public_tail_k: int
    private_tail_k: int
    neutral_tail_k: int
    changed_cells: int
    changed_rows: int
    h042_overlap_cells: int
    h043_overlap_cells: int
    h045_overlap_cells: int
    h042_jaccard: float
    h043_jaccard: float
    h045_jaccard: float
    route_public_mean: float
    route_private_mean: float
    route_q2regime_mean: float
    mean_abs_logit_move: float
    max_abs_logit_move: float
    mean_abs_prob_move: float
    max_abs_prob_move: float
    bifurcation_strength: float
    tangent_expected_delta: float
    resolved_path: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h045 = import_module(HITL / "h045_conditional_route_action_decoder_jepa.py", "h045_for_h046")
h045.OUT = OUT
h045.h043.OUT = OUT
h045.h043.h042.OUT = OUT
h045.h044.OUT = OUT
h045.h044.h043.OUT = OUT
h045.h044.h042.OUT = OUT
h045.h042.OUT = OUT
h043 = h045.h043
h044 = h045.h044
h042 = h045.h042
h036 = h045.h036


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def safe_id(text: str, limit: int = 115) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rank01(x: np.ndarray, high_good: bool = True) -> np.ndarray:
    r = pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high_good else 1.0 - r


def top_indices(score: np.ndarray, k: int, allowed: np.ndarray | None = None) -> np.ndarray:
    s = np.nan_to_num(np.asarray(score, dtype=np.float64), nan=-np.inf)
    if allowed is not None:
        s = s.copy()
        s[~allowed] = -np.inf
    valid = np.where(np.isfinite(s))[0]
    if len(valid) == 0:
        return np.array([], dtype=int)
    return valid[np.argsort(-s[valid])[: min(k, len(valid))]]


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def load_anchor_probs() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sample, h012_prob, h042_prob, h043_prob = h045.load_anchor_probs()
    h045_prob = h036.load_sub(ROOT / H045, sample)[TARGETS].to_numpy(dtype=np.float64)
    return sample, h012_prob, h042_prob, h043_prob, h045_prob


def build_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h043_prob: np.ndarray,
    h045_prob: np.ndarray,
    state: dict[str, np.ndarray],
    route: pd.DataFrame,
) -> pd.DataFrame:
    z012 = state["z_h012"]
    phase = state["phase_dir_q2"]
    allowed = state["support_q2"]
    h042_support = np.abs(h042_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h043_support = np.abs(h043_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h045_support = np.abs(h045_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h042_delta = logit(h042_prob)[:, Q2_I] - z012[:, Q2_I]

    public = route["h044_public_transition_score"].to_numpy(dtype=np.float64)
    private = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    q2regime = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    h042like = route["h044_h042_like_score"].to_numpy(dtype=np.float64)
    phase_energy = route["h044_phase_energy_score"].to_numpy(dtype=np.float64)
    public_not_private = public * (1.0 - private)
    regime_scores = {
        "q2regime": q2regime,
        "public_not_private": public_not_private,
        "h042like_phase": 0.55 * h042like + 0.45 * phase_energy,
        "public_phase": 0.55 * public + 0.45 * phase_energy,
    }

    h042_idx = np.where(h042_support)[0]
    h043_tail = h043_support & ~h042_support
    h045_tail = h045_support & ~h042_support
    private_tail_allowed = allowed & ~h042_support & (private >= np.quantile(private, 0.58))
    neutral_allowed = allowed & ~h042_support & ~private_tail_allowed

    generated: set[str] = set()
    specs: list[CandidateSpec] = []

    def add_candidate(
        alpha_by_row: dict[int, float],
        family: str,
        regime: str,
        core_alpha: float,
        public_alpha: float,
        private_alpha: float,
        neutral_alpha: float,
        public_tail_k: int,
        private_tail_k: int,
        neutral_tail_k: int,
    ) -> None:
        z = z012.copy()
        for row, alpha in alpha_by_row.items():
            z[row, Q2_I] = z012[row, Q2_I] + alpha * phase[row]
        prob = sigmoid(z)
        if np.max(np.abs(prob - h045_prob)) < 1.0e-12:
            return
        changed_mask = np.abs(prob - h012_prob) > 1.0e-7
        q2_changed = changed_mask[:, Q2_I]
        changed = int(changed_mask.sum())
        if changed == 0:
            return
        cid = safe_id(f"h046_{family}_c{changed}_{short_hash(prob)}")
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)

        changed_idx = np.where(q2_changed)[0]
        delta = logit(prob)[:, Q2_I] - z012[:, Q2_I]
        dist = delta - h042_delta
        h042_overlap = int(np.logical_and(q2_changed, h042_support).sum())
        h043_overlap = int(np.logical_and(q2_changed, h043_support).sum())
        h045_overlap = int(np.logical_and(q2_changed, h045_support).sum())
        h042_union = int(np.logical_or(q2_changed, h042_support).sum())
        h043_union = int(np.logical_or(q2_changed, h043_support).sum())
        h045_union = int(np.logical_or(q2_changed, h045_support).sum())
        expected, _proj, _resid, _ratio = h043.tangent_delta(prob, h012_prob, h042_prob)
        signed_private = float(np.mean(delta[changed_idx] * private[changed_idx])) if len(changed_idx) else 0.0
        signed_public = float(np.mean(delta[changed_idx] * public[changed_idx])) if len(changed_idx) else 0.0
        specs.append(
            CandidateSpec(
                candidate_id=cid,
                family=family,
                regime=regime,
                core_alpha=core_alpha,
                public_alpha=public_alpha,
                private_alpha=private_alpha,
                neutral_alpha=neutral_alpha,
                public_tail_k=public_tail_k,
                private_tail_k=private_tail_k,
                neutral_tail_k=neutral_tail_k,
                changed_cells=changed,
                changed_rows=int(np.max(changed_mask, axis=1).sum()),
                h042_overlap_cells=h042_overlap,
                h043_overlap_cells=h043_overlap,
                h045_overlap_cells=h045_overlap,
                h042_jaccard=float(h042_overlap / h042_union) if h042_union else 0.0,
                h043_jaccard=float(h043_overlap / h043_union) if h043_union else 0.0,
                h045_jaccard=float(h045_overlap / h045_union) if h045_union else 0.0,
                route_public_mean=float(route.loc[changed_idx, "h044_public_transition_score"].mean()),
                route_private_mean=float(route.loc[changed_idx, "h044_private_routine_score"].mean()),
                route_q2regime_mean=float(route.loc[changed_idx, "h044_public_q2_regime_score"].mean()),
                mean_abs_logit_move=float(np.mean(np.abs(delta))),
                max_abs_logit_move=float(np.max(np.abs(delta))),
                mean_abs_prob_move=float(np.mean(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                max_abs_prob_move=float(np.max(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                bifurcation_strength=float(abs(signed_public - signed_private) + np.std(list(alpha_by_row.values()))),
                tangent_expected_delta=expected,
                resolved_path=str(path),
            )
        )

    # A) Dual rail: validated H042 core + public tail + private opposite/veto.
    for regime, score in regime_scores.items():
        for public_k in [12, 20, 30, 45, 60]:
            public_tail = top_indices(score, public_k, neutral_allowed & ~h042_support)
            for private_k in [0, 8, 16, 28]:
                private_tail = top_indices(private, private_k, private_tail_allowed & ~np.isin(np.arange(len(private)), public_tail))
                for core_alpha in [0.58, 0.66, 0.78, 0.92]:
                    for public_alpha in [0.08, 0.14, 0.22, 0.32, 0.44]:
                        for private_alpha in ([0.0] if private_k == 0 else [-0.03, -0.06, -0.10]):
                            mask = {int(r): core_alpha for r in h042_idx}
                            mask.update({int(r): public_alpha for r in public_tail})
                            mask.update({int(r): private_alpha for r in private_tail})
                            add_candidate(
                                mask,
                                f"dual_{regime}_pub{public_k}_priv{private_k}_a{core_alpha:g}_{public_alpha:g}_{private_alpha:g}",
                                regime,
                                core_alpha,
                                public_alpha,
                                private_alpha,
                                0.0,
                                public_k,
                                private_k,
                                0,
                            )

    # B) H045 support with non-uniform route amplitude.
    for regime, score in regime_scores.items():
        tail = np.where(h045_tail)[0]
        tail_ranked = tail[np.argsort(-score[tail])]
        for keep_tail in [10, 18, 30]:
            public_tail = tail_ranked[: min(keep_tail, len(tail_ranked))]
            private_tail = top_indices(private, 8, h045_tail & (private >= np.quantile(private, 0.65)))
            for core_alpha in [0.58, 0.66, 0.78, 0.92]:
                for public_alpha in [0.14, 0.22, 0.32, 0.44]:
                    for private_alpha in [0.0, -0.03, -0.06]:
                        mask = {int(r): core_alpha for r in h042_idx}
                        mask.update({int(r): public_alpha for r in public_tail})
                        mask.update({int(r): private_alpha for r in private_tail})
                        add_candidate(
                            mask,
                            f"h045split_{regime}_tail{keep_tail}_a{core_alpha:g}_{public_alpha:g}_{private_alpha:g}",
                            regime,
                            core_alpha,
                            public_alpha,
                            private_alpha,
                            0.0,
                            keep_tail,
                            len(private_tail),
                            0,
                        )

    # C) Three-level regime: public tail, neutral small tail, private veto.
    for regime, score in regime_scores.items():
        for public_k in [20, 35, 55]:
            public_tail = top_indices(score, public_k, neutral_allowed & h043_tail)
            neutral_tail = top_indices(phase_energy, 20, neutral_allowed & ~np.isin(np.arange(len(private)), public_tail))
            private_tail = top_indices(private, 12, private_tail_allowed & h043_tail)
            for core_alpha in [0.66, 0.78, 0.92]:
                for public_alpha in [0.18, 0.28, 0.40]:
                    for neutral_alpha in [0.04, 0.08, 0.12]:
                        for private_alpha in [0.0, -0.04]:
                            mask = {int(r): core_alpha for r in h042_idx}
                            mask.update({int(r): public_alpha for r in public_tail})
                            mask.update({int(r): neutral_alpha for r in neutral_tail})
                            mask.update({int(r): private_alpha for r in private_tail})
                            add_candidate(
                                mask,
                                f"tri_{regime}_pub{public_k}_a{core_alpha:g}_{public_alpha:g}_{neutral_alpha:g}_{private_alpha:g}",
                                regime,
                                core_alpha,
                                public_alpha,
                                private_alpha,
                                neutral_alpha,
                                public_k,
                                len(private_tail),
                                len(neutral_tail),
                            )

    out = pd.DataFrame([s.__dict__ for s in specs])
    if not out.empty:
        out.to_csv(OUT / "h046_generated_candidates.csv", index=False)
    return out


def candidate_frame(generated: pd.DataFrame, rt: dict[str, object], sample: pd.DataFrame, h012_prob: np.ndarray, state: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for rec in generated.to_dict("records"):
        prob = h036.load_sub(rec["resolved_path"], sample)[TARGETS].to_numpy(dtype=np.float64)
        route_delta, route_disp = h042.expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "file": Path(rec["resolved_path"]).name,
                "resolved_path": rec["resolved_path"],
                "family": rec["family"],
                "components": rec["family"],
                "component_count": 3,
                "changed_cells_vs_h012": int(rec["changed_cells"]),
                "changed_rows_vs_h012": int(rec["changed_rows"]),
                "mean_abs_prob_move_h012": float(rec["mean_abs_prob_move"]),
                "max_abs_prob_move_h012": float(rec["max_abs_prob_move"]),
                "mean_abs_logit_move_h012": float(rec["mean_abs_logit_move"]),
                "max_abs_logit_move_h012": float(rec["max_abs_logit_move"]),
                "route_equation_delta_vs_h012": route_delta,
                "route_equation_delta_iqr": route_disp,
                "h012posterior_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h012posterior"], np.abs(logit(state["h012posterior"]) - logit(h012_prob))
                ),
                "h036world_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h036world"], np.abs(logit(state["h036world"]) - logit(h012_prob))
                ),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out.to_csv(OUT / "h046_candidate_pre_scores.csv", index=False)
    return out


def conditional_score(scored_raw: pd.DataFrame, rt: dict[str, object], atoms: list[object], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray, route: pd.DataFrame) -> pd.DataFrame:
    known = h045.known_augmented_features(rt, atoms, h012_prob, h042_prob, h043_prob, route)
    decoder_scores, decoder_loo = h045.evaluate_decoders(known)
    cand = h045.candidate_conditional_features(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    pred = h045.predict_candidates(known, cand, decoder_scores)
    scored = h045.score_candidates(scored_raw, pred)
    decoder_scores.to_csv(OUT / "h046_conditional_decoder_scores.csv", index=False)
    decoder_loo.to_csv(OUT / "h046_conditional_decoder_loo.csv", index=False)
    return scored


def rank_h046(scored: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return scored
    meta_cols = [
        "candidate_id",
        "regime",
        "core_alpha",
        "public_alpha",
        "private_alpha",
        "neutral_alpha",
        "public_tail_k",
        "private_tail_k",
        "neutral_tail_k",
        "h042_overlap_cells",
        "h043_overlap_cells",
        "h045_overlap_cells",
        "h042_jaccard",
        "h043_jaccard",
        "h045_jaccard",
        "route_public_mean",
        "route_private_mean",
        "route_q2regime_mean",
        "bifurcation_strength",
        "tangent_expected_delta",
    ]
    out = scored.merge(generated[[c for c in meta_cols if c in generated.columns]], on="candidate_id", how="left")
    full_margin = out["full_known_cond_margin_vs_h012_median"].fillna(0.01)
    pre_margin = out["pre_h042_cond_margin_vs_h012_median"].fillna(0.01)
    route_delta = out["route_equation_delta_vs_h012"].fillna(0.01)
    h025 = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    changed = out["changed_cells_vs_h012"].fillna(999)
    bif = out["bifurcation_strength"].fillna(0.0)
    out["h046_bifurcated_score"] = (
        1.25 * full_margin.rank(method="average", pct=True)
        + 0.55 * pre_margin.rank(method="average", pct=True)
        + 0.80 * route_delta.rank(method="average", pct=True)
        + 0.45 * h025.rank(method="average", pct=True)
        + 0.35 * h024.rank(method="average", pct=True)
        + 0.20 * changed.rank(method="average", pct=True)
        - 0.28 * out["full_known_cond_support_better_than_h012"].fillna(0.0)
        - 0.16 * out["pre_h042_cond_support_better_than_h012"].fillna(0.0)
        - 0.12 * bif.rank(method="average", pct=True)
    )
    out["h046_promotable"] = (
        (out["changed_cells_vs_h012"].between(45, 115))
        & (out["full_known_cond_margin_vs_h012_median"] < -0.00011)
        & (out["full_known_cond_support_better_than_h012"] >= 0.58)
        & (out["pre_h042_cond_margin_vs_h012_median"] < 0.00010)
        & (out["route_equation_delta_vs_h012"] < -0.00016)
        & (out["h025_score"] < 0.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00090)
        & (out["bifurcation_strength"] > out["bifurcation_strength"].median())
    )
    out = out.sort_values(["h046_promotable", "h046_bifurcated_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h046_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        out = pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no scored candidates"}])
        out.to_csv(OUT / "h046_decision.csv", index=False)
        return out
    selected = scored.iloc[0].copy()
    promote = bool(selected.get("h046_promotable", False))
    source = Path(str(selected["resolved_path"]))
    suffix = str(selected["candidate_id"]).rsplit("_", 1)[-1]
    root_path = ROOT / f"submission_h046_q2_bifurcated_{suffix}_uploadsafe.csv"
    if promote:
        prob = h036.load_sub(source, sample)[TARGETS].to_numpy(dtype=np.float64)
        write_submission(sample, prob, root_path)
    dec = {
        "decision": "promote" if promote else "do_not_promote",
        "promote": promote,
        "selected_candidate_id": selected["candidate_id"],
        "selected_file": selected["file"],
        "selected_resolved_path": str(source),
        "root_uploadsafe_path": str(root_path) if promote else "",
        "reason": "bifurcated Q2 regime gate passed" if promote else "no bifurcated candidate passed H046 gate",
        "expected_relation": "beats H045 if Q2 support needs regime-specific action amplitudes",
    }
    for col in [
        "changed_cells_vs_h012",
        "full_known_cond_margin_vs_h012_median",
        "full_known_cond_support_better_than_h012",
        "pre_h042_cond_margin_vs_h012_median",
        "pre_h042_cond_support_better_than_h012",
        "route_equation_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "h025_score",
        "bifurcation_strength",
        "h046_bifurcated_score",
        "h046_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h046_decision.csv", index=False)
    return out


def write_report(generated: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame) -> None:
    lines = [
        "# H046 Q2 Bifurcated Regime Decoder HS-JEPA",
        "",
        "Question: is Q2 phase a single support/alpha action, or does hidden human-state regime require different amplitudes?",
        "",
        f"- generated candidates: `{len(generated)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- promotable candidates: `{int(scored['h046_promotable'].sum()) if 'h046_promotable' in scored else 0}`",
        "",
        "Top H046 candidates:",
        "",
        md_table(
            scored[
                [
                    "candidate_id",
                    "changed_cells_vs_h012",
                    "full_known_cond_margin_vs_h012_median",
                    "full_known_cond_support_better_than_h012",
                    "pre_h042_cond_margin_vs_h012_median",
                    "route_equation_delta_vs_h012",
                    "pre_h012_h024_margin_vs_h012_median",
                    "h025_score",
                    "bifurcation_strength",
                    "h046_promotable",
                    "h046_bifurcated_score",
                ]
            ].head(20)
            if not scored.empty
            else scored
        ),
        "",
        "Decision:",
        "",
        md_table(decision),
        "",
        "Interpretation:",
        "",
        "- If promoted and public-positive, Q2 route state is an action-amplitude decoder, not merely a support selector.",
        "- If no candidate is promoted, the current Q2 win is better explained by single-support pruning around H042/H045 than by bifurcated private/public amplitudes.",
        "- H024 remains a guardrail: positive H024 margin keeps any promoted file in the Q2-local sensor category, not a general action translator.",
    ]
    (OUT / "h046_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob, h043_prob, h045_prob = load_anchor_probs()
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = h045.build_route_context(rt, state, h012_prob, h042_prob, h043_prob)
    generated = build_candidates(sample, h012_prob, h042_prob, h043_prob, h045_prob, state, route)
    known_aug, decoder_scores, _ = h043.known_features_with_h042(rt, atoms, h042_prob)
    pre = candidate_frame(generated, rt, sample, h012_prob, state)
    scored_raw, _ = h042.score_candidates(rt, atoms, pre, known_aug, decoder_scores)
    scored_cond = conditional_score(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    scored = rank_h046(scored_cond, generated)
    decision = select_and_copy(scored, sample)
    write_report(generated, scored, decision)
    print("H046 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H046 decision:", decision.iloc[0]["decision"])
    print("H046 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
