#!/usr/bin/env python3
"""H044: human-route split of the Q2 phase manifold.

H042 proved a small Q2 phase move can beat H012. H043 then asked whether the
move extends from 45 to 105 Q2 cells. H044 asks a different question:

    Is the Q2 phase action tied to a human-state route, not merely a top-k
    score surface?

The bet is that the public-positive Q2 action lives in rows with public-route,
transition-exception, and memory-disagreement structure, while private-routine
rows should be damped or excluded. This is a direct HS-JEPA translation:

    context = human-state route geometry + H042 public action response
    target  = Q2 phase action support under hidden public/private regimes
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
OUT = HITL / "h044_q2_human_route_split_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q2_I = TARGETS.index("Q2")
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H043 = "submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    regime: str
    changed_cells: int
    changed_rows: int
    core_rows: int
    tail_rows: int
    core_alpha: float
    tail_alpha: float
    route_public_mean: float
    route_private_mean: float
    route_transition_mean: float
    route_memory_disagree_mean: float
    route_regime_mean: float
    h042_overlap_cells: int
    h042_jaccard: float
    h043_overlap_cells: int
    h043_jaccard: float
    h042_distance_l2: float
    h043_distance_l2: float
    tangent_expected_delta: float
    mean_abs_logit_move: float
    max_abs_logit_move: float
    mean_abs_prob_move: float
    max_abs_prob_move: float
    resolved_path: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h043 = import_module(HITL / "h043_q2_phase_manifold_jepa.py", "h043_for_h044")
h043.OUT = OUT
h043.h042.OUT = OUT
h036 = h043.h036
h042 = h043.h042


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 118) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


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


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def rank01(x: np.ndarray, high_good: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64))
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
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


def load_h043_prob(sample: pd.DataFrame) -> np.ndarray:
    return h036.load_sub(ROOT / H043, sample)[TARGETS].to_numpy(dtype=np.float64)


def route_scores(rt: dict[str, object], state: dict[str, np.ndarray], h042_prob: np.ndarray, h043_prob: np.ndarray, h012_prob: np.ndarray) -> pd.DataFrame:
    route = rt["route"].sort_values("row").reset_index(drop=True).copy()
    h042_support = np.abs(h042_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h043_support = np.abs(h043_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    phase_energy = np.abs(state["phase_dir_q2"]) * state["score_q2"]

    public = route["public_route_score"].to_numpy(dtype=np.float64)
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)
    transition = route["transition_exception_route_score"].to_numpy(dtype=np.float64)
    uncertainty = route["route_uncertainty_score"].to_numpy(dtype=np.float64)
    world_col = "world_public_prob" if "world_public_prob" in route.columns else "row_public_prob"
    world = route[world_col].to_numpy(dtype=np.float64)
    memory = route["memory_disagree_rate"].to_numpy(dtype=np.float64)
    support = route["support_count"].to_numpy(dtype=np.float64)

    route["h044_public_transition_score"] = (
        0.24 * rank01(world)
        + 0.24 * rank01(public)
        + 0.20 * rank01(transition)
        + 0.13 * rank01(memory)
        + 0.10 * rank01(support)
        + 0.09 * rank01(uncertainty)
        - 0.18 * rank01(private)
    )
    route["h044_private_routine_score"] = (
        0.42 * rank01(private)
        + 0.20 * rank01(public, high_good=False)
        + 0.16 * rank01(transition, high_good=False)
        + 0.12 * rank01(world, high_good=False)
        + 0.10 * rank01(memory, high_good=False)
    )
    route["h044_phase_energy_score"] = rank01(phase_energy)

    cols = [
        world_col,
        "public_route_score",
        "private_memory_route_score",
        "transition_exception_route_score",
        "route_uncertainty_score",
        "support_count",
        "memory_disagree_rate",
    ]
    mu = route.loc[h042_support, cols].mean()
    sd = route[cols].std().replace(0, 1.0)
    dist = ((route[cols] - mu) / sd).pow(2).mean(axis=1).pow(0.5).to_numpy(dtype=np.float64)
    route["h044_h042_like_score"] = rank01(-dist)
    route["h044_public_q2_regime_score"] = (
        0.38 * route["h044_public_transition_score"]
        + 0.27 * route["h044_h042_like_score"]
        + 0.22 * route["h044_phase_energy_score"]
        - 0.17 * route["h044_private_routine_score"]
    )
    route["h042_q2_support"] = h042_support
    route["h043_q2_support"] = h043_support
    route.to_csv(OUT / "h044_route_regime_scores.csv", index=False)
    return route


def materialize_candidates(
    rt: dict[str, object],
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h043_prob: np.ndarray,
    state: dict[str, np.ndarray],
    route: pd.DataFrame,
) -> pd.DataFrame:
    z_h012 = state["z_h012"]
    phase_dir = state["phase_dir_q2"]
    allowed = state["support_q2"]
    h042_support = route["h042_q2_support"].to_numpy(dtype=bool)
    h043_support = route["h043_q2_support"].to_numpy(dtype=bool)
    h042_delta = logit(h042_prob)[:, Q2_I] - z_h012[:, Q2_I]
    h043_delta = logit(h043_prob)[:, Q2_I] - z_h012[:, Q2_I]
    scores = {
        "pubtrans": route["h044_public_transition_score"].to_numpy(dtype=np.float64),
        "h042like": route["h044_h042_like_score"].to_numpy(dtype=np.float64),
        "q2regime": route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64),
        "phaseenergy": route["h044_phase_energy_score"].to_numpy(dtype=np.float64),
    }
    private = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    generated: set[str] = set()
    specs: list[CandidateSpec] = []

    def build(mask_alpha: dict[int, float], family: str, regime: str, core_rows: int, tail_rows: int, core_alpha: float, tail_alpha: float) -> None:
        z = z_h012.copy()
        for row, alpha in mask_alpha.items():
            z[row, Q2_I] = z_h012[row, Q2_I] + alpha * phase_dir[row]
        prob = sigmoid(z)
        if np.max(np.abs(prob - h043_prob)) < 1.0e-12:
            return
        changed_mask = np.abs(prob - h012_prob) > 1.0e-7
        changed = int(changed_mask.sum())
        if changed == 0:
            return
        cid = safe_id(f"h044_{family}_c{changed}_{short_hash(prob)}")
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)

        q2_changed = changed_mask[:, Q2_I]
        changed_idx = np.where(q2_changed)[0]
        h042_union = np.logical_or(q2_changed, h042_support).sum()
        h043_union = np.logical_or(q2_changed, h043_support).sum()
        h042_overlap = int(np.logical_and(q2_changed, h042_support).sum())
        h043_overlap = int(np.logical_and(q2_changed, h043_support).sum())
        delta = logit(prob)[:, Q2_I] - z_h012[:, Q2_I]
        h042_dist = delta - h042_delta
        h043_dist = delta - h043_delta
        expected, _projection, _resid, _ratio = h043.tangent_delta(prob, h012_prob, h042_prob)
        specs.append(
            CandidateSpec(
                candidate_id=cid,
                family=family,
                regime=regime,
                changed_cells=changed,
                changed_rows=int(np.max(changed_mask, axis=1).sum()),
                core_rows=core_rows,
                tail_rows=tail_rows,
                core_alpha=core_alpha,
                tail_alpha=tail_alpha,
                route_public_mean=float(route.loc[changed_idx, "public_route_score"].mean()),
                route_private_mean=float(route.loc[changed_idx, "private_memory_route_score"].mean()),
                route_transition_mean=float(route.loc[changed_idx, "transition_exception_route_score"].mean()),
                route_memory_disagree_mean=float(route.loc[changed_idx, "memory_disagree_rate"].mean()),
                route_regime_mean=float(route.loc[changed_idx, "h044_public_q2_regime_score"].mean()),
                h042_overlap_cells=h042_overlap,
                h042_jaccard=float(h042_overlap / h042_union) if h042_union else 0.0,
                h043_overlap_cells=h043_overlap,
                h043_jaccard=float(h043_overlap / h043_union) if h043_union else 0.0,
                h042_distance_l2=float(np.sqrt(np.mean(h042_dist * h042_dist))),
                h043_distance_l2=float(np.sqrt(np.mean(h043_dist * h043_dist))),
                tangent_expected_delta=expected,
                mean_abs_logit_move=float(np.mean(np.abs(delta))),
                max_abs_logit_move=float(np.max(np.abs(delta))),
                mean_abs_prob_move=float(np.mean(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                max_abs_prob_move=float(np.max(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                resolved_path=str(path),
            )
        )

    # A) Pure human-route top-k supports, not simple H043 top-k.
    for regime, score in scores.items():
        for k in [38, 45, 55, 65, 75, 90, 105, 120]:
            rows = top_indices(score, k, allowed)
            for alpha in [0.50, 0.58, 0.66, 0.78, 0.92]:
                build({int(r): alpha for r in rows}, f"{regime}_top{k}_a{alpha:g}", regime, k, 0, alpha, 0.0)

    # B) H043 support split by human route: test whether the 105-cell branch
    # should be pruned to transition/public rows.
    for regime, score in scores.items():
        for k in [45, 55, 65, 75, 85, 95]:
            rows = top_indices(score, k, allowed & h043_support)
            for alpha in [0.58, 0.66, 0.78, 0.90, 1.05]:
                build({int(r): alpha for r in rows}, f"h043support_{regime}_top{k}_a{alpha:g}", regime, k, 0, alpha, 0.0)

    # C) Validated H042 core plus a human-route tail. This explicitly asks
    # whether the tail beyond H042 should be route-selected, not q2-score-selected.
    h042_idx = np.where(h042_support)[0]
    for regime, score in scores.items():
        tail_allowed = allowed & ~h042_support & (private <= np.quantile(private, 0.72))
        for tail_k in [10, 18, 28, 40, 55, 70]:
            tail_rows = top_indices(score, tail_k, tail_allowed)
            for core_alpha in [0.58, 0.66, 0.78, 0.92]:
                for tail_alpha in [0.08, 0.14, 0.22, 0.32, 0.44]:
                    mask = {int(r): core_alpha for r in h042_idx}
                    mask.update({int(r): tail_alpha for r in tail_rows})
                    build(
                        mask,
                        f"h042core{core_alpha:g}_{regime}_tail{tail_k}_b{tail_alpha:g}",
                        regime,
                        len(h042_idx),
                        tail_k,
                        core_alpha,
                        tail_alpha,
                    )

    # D) Private-routine veto: preserve public/transition rows and remove the
    # most private tail inside H043 support.
    public_gate = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    for private_q in [0.55, 0.62, 0.70, 0.78]:
        eligible = allowed & h043_support & (private <= np.quantile(private, private_q))
        rows = top_indices(public_gate, 120, eligible)
        for alpha in [0.58, 0.66, 0.78, 0.90]:
            build({int(r): alpha for r in rows}, f"h043_privateveto_q{private_q:g}_a{alpha:g}", "private_veto", len(rows), 0, alpha, 0.0)

    out = pd.DataFrame([s.__dict__ for s in specs])
    if not out.empty:
        out.to_csv(OUT / "h044_generated_candidates.csv", index=False)
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
                "component_count": 1 + int(rec["tail_rows"] > 0),
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
        out.to_csv(OUT / "h044_candidate_pre_scores.csv", index=False)
    return out


def score_h044(candidates: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    meta_cols = [
        "candidate_id",
        "regime",
        "core_rows",
        "tail_rows",
        "core_alpha",
        "tail_alpha",
        "route_public_mean",
        "route_private_mean",
        "route_transition_mean",
        "route_memory_disagree_mean",
        "route_regime_mean",
        "h042_overlap_cells",
        "h042_jaccard",
        "h043_overlap_cells",
        "h043_jaccard",
        "h042_distance_l2",
        "h043_distance_l2",
        "tangent_expected_delta",
    ]
    out = candidates.merge(generated[meta_cols], on="candidate_id", how="left")
    action = out.get("pre_h012_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    route_delta = out["route_equation_delta_vs_h012"].fillna(0.01)
    h025_score = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    h024_margin = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    changed = out["changed_cells_vs_h012"].fillna(999)
    private_mean = out["route_private_mean"].fillna(0.8)
    regime_mean = out["route_regime_mean"].fillna(0.0)
    h042_dist = out["h042_distance_l2"].fillna(0.4)
    h043_dist = out["h043_distance_l2"].fillna(0.4)
    h043_jaccard = out["h043_jaccard"].fillna(0.0)
    h042_jaccard = out["h042_jaccard"].fillna(0.0)

    out["h044_route_split_score"] = (
        1.05 * action.rank(method="average", pct=True)
        + 0.85 * route_delta.rank(method="average", pct=True)
        + 0.55 * h025_score.rank(method="average", pct=True)
        + 0.35 * h024_margin.rank(method="average", pct=True)
        + 0.28 * h042_dist.rank(method="average", pct=True)
        + 0.20 * h043_dist.rank(method="average", pct=True)
        + 0.20 * changed.rank(method="average", pct=True)
        + 0.22 * private_mean.rank(method="average", pct=True)
        - 0.36 * regime_mean.rank(method="average", pct=True)
        - 0.20 * h042_jaccard
        - 0.12 * h043_jaccard
    )
    out["h044_promotable"] = (
        (out["changed_cells_vs_h012"] <= 125)
        & (out["pre_h012_action_margin_vs_h012_median"] < -0.000055)
        & (out["pre_h012_action_support_better_than_h012"] >= 0.50)
        & (out["route_equation_delta_vs_h012"] < -0.000145)
        & (out["h025_score"] < 0.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00085)
        & (out["h042_distance_l2"] <= 0.12)
        & (out["route_regime_mean"] >= 0.58)
    )
    out = out.sort_values(["h044_promotable", "h044_route_split_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h044_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no candidates"}])
    selected = scored.iloc[0].copy()
    source = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"{source.stem}_uploadsafe.csv"
    promote = bool(selected.get("h044_promotable", False))
    if promote:
        prob = h036.load_sub(str(source), sample)[TARGETS].to_numpy(dtype=np.float64)
        write_submission(sample, prob, root_path)
    dec = {
        "decision": "promote" if promote else "do_not_promote",
        "promote": promote,
        "selected_candidate_id": selected["candidate_id"],
        "selected_file": source.name,
        "selected_resolved_path": str(source),
        "root_uploadsafe_path": str(root_path) if promote else "",
        "public_anchor": H042,
        "expected_relation": "beats H042 if Q2 phase is human-route conditioned",
        "reason": "route-split Q2 gate passed; copied root uploadsafe candidate" if promote else "no candidate passed H044 route-split gate",
    }
    for col in [
        "changed_cells_vs_h012",
        "regime",
        "core_rows",
        "tail_rows",
        "core_alpha",
        "tail_alpha",
        "route_public_mean",
        "route_private_mean",
        "route_transition_mean",
        "route_memory_disagree_mean",
        "route_regime_mean",
        "pre_h012_action_margin_vs_h012_median",
        "pre_h012_action_support_better_than_h012",
        "route_equation_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "pre_h012_h024_support_better_than_h012",
        "h025_score",
        "h042_jaccard",
        "h043_jaccard",
        "h042_distance_l2",
        "h043_distance_l2",
        "tangent_expected_delta",
        "h044_route_split_score",
        "h044_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h044_decision.csv", index=False)
    return out


def write_report(generated: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame, decoder_scores: pd.DataFrame) -> None:
    lines = [
        "# H044 Q2 Human-Route Split HS-JEPA",
        "",
        "## Question",
        "",
        "Is the Q2 phase action tied to public/transition human-state routes rather than a simple Q2 top-k surface?",
        "",
        "## Candidate Search",
        "",
        f"- generated candidates: `{len(generated)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- promotable candidates: `{int(scored['h044_promotable'].sum()) if 'h044_promotable' in scored else 0}`",
        "",
        "Top decoder fits after adding H042 public feedback:",
        "",
        md_table(decoder_scores.head(8)),
        "",
        "Top H044 candidates:",
        "",
        md_table(
            scored[
                [
                    "candidate_id",
                    "regime",
                    "changed_cells_vs_h012",
                    "core_rows",
                    "tail_rows",
                    "core_alpha",
                    "tail_alpha",
                    "route_regime_mean",
                    "route_private_mean",
                    "pre_h012_action_margin_vs_h012_median",
                    "route_equation_delta_vs_h012",
                    "pre_h012_h024_margin_vs_h012_median",
                    "h025_score",
                    "h042_jaccard",
                    "h043_jaccard",
                    "h042_distance_l2",
                    "h043_distance_l2",
                    "h044_promotable",
                    "h044_route_split_score",
                ]
            ].head(20)
            if not scored.empty
            else scored
        ),
        "",
        "## Decision",
        "",
        md_table(decision),
        "",
        "## Interpretation",
        "",
        "- If promoted and public-positive, Q2 phase is a human-route-conditioned latent action, not just a probability surface.",
        "- If promoted but public-negative, H042/H043 public movement is not explained by the current public/transition/private route geometry.",
        "- If no candidate is promoted, H043 remains the best Q2 phase public sensor and route splitting must be rethought at a different layer.",
        "",
    ]
    (OUT / "h044_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob = h043.load_anchor_probs()
    h043_prob = load_h043_prob(sample)
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = route_scores(rt, state, h042_prob, h043_prob, h012_prob)
    generated = materialize_candidates(rt, sample, h012_prob, h042_prob, h043_prob, state, route)
    known_aug, decoder_scores, _decoder_loo = h043.known_features_with_h042(rt, atoms, h042_prob)
    pre = candidate_frame(generated, rt, sample, h012_prob, state)
    scored_raw, _h025 = h042.score_candidates(rt, atoms, pre, known_aug, decoder_scores)
    scored = score_h044(scored_raw, generated)
    decision = select_and_copy(scored, sample)
    write_report(generated, scored, decision, decoder_scores)
    print("H044 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H044 decision:", decision.iloc[0]["decision"])
    print("H044 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
