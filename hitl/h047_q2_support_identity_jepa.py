#!/usr/bin/env python3
"""H047: Q2 support-identity posterior HS-JEPA.

H046 rejected route-specific Q2 amplitude/sign bifurcation. The surviving
question is more discrete:

    which rows should belong to the public-positive Q2 phase support?

H047 treats candidate supports as observations. Good H043/H045 supports and
bad H046 bifurcated supports become contrastive supervision for a row-level
Q2 support identity posterior. The materialized action returns to one Q2 phase
direction; only the support is newly inferred.
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
OUT = HITL / "h047_q2_support_identity_jepa"
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
    support_source: str
    k: int
    alpha: float
    core_alpha: float
    tail_alpha: float
    changed_cells: int
    changed_rows: int
    h042_overlap_cells: int
    h043_overlap_cells: int
    h045_overlap_cells: int
    h042_jaccard: float
    h043_jaccard: float
    h045_jaccard: float
    support_score_mean: float
    support_score_min: float
    support_score_sum: float
    contrast_mean: float
    route_public_mean: float
    route_private_mean: float
    route_q2regime_mean: float
    mean_abs_logit_move: float
    max_abs_logit_move: float
    mean_abs_prob_move: float
    max_abs_prob_move: float
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


h045 = import_module(HITL / "h045_conditional_route_action_decoder_jepa.py", "h045_for_h047")
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


def candidate_quality(df: pd.DataFrame) -> pd.Series:
    full = df["full_known_cond_margin_vs_h012_median"].fillna(0.002)
    support = df["full_known_cond_support_better_than_h012"].fillna(0.0)
    pre = df["pre_h042_cond_margin_vs_h012_median"].fillna(0.002)
    route = df["route_equation_delta_vs_h012"].fillna(0.002)
    h025 = df.get("h025_score", pd.Series(1.0, index=df.index)).fillna(1.0)
    h024 = df.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.002, index=df.index)).fillna(0.002)
    quality = (
        -1.35 * full.rank(method="average", pct=True)
        -0.75 * pre.rank(method="average", pct=True)
        -0.65 * route.rank(method="average", pct=True)
        -0.45 * h025.rank(method="average", pct=True)
        -0.25 * h024.rank(method="average", pct=True)
        +0.95 * support
    )
    return (quality - quality.mean()) / (quality.std() + 1.0e-12)


def load_support_observations(sample: pd.DataFrame, h012_prob: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    frames = []
    h045_scores = pd.read_csv(HITL / "h045_conditional_route_action_decoder_jepa" / "h045_candidate_scores.csv")
    h045_scores["obs_source"] = "h045"
    frames.append(h045_scores)
    h046_scores = pd.read_csv(HITL / "h046_q2_bifurcated_regime_decoder_jepa" / "h046_candidate_scores.csv")
    h046_scores["obs_source"] = "h046"
    frames.append(h046_scores)
    obs = pd.concat(frames, ignore_index=True)
    obs = obs.drop_duplicates("resolved_path", keep="first").reset_index(drop=True)
    obs["support_quality"] = candidate_quality(obs)

    masks = []
    kept_rows = []
    for rec in obs.to_dict("records"):
        path = Path(str(rec["resolved_path"]))
        if not path.exists():
            continue
        prob = h036.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        mask = np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
        masks.append(mask.astype(np.float64))
        kept_rows.append(rec)
    kept = pd.DataFrame(kept_rows)
    mat = np.vstack(masks) if masks else np.zeros((0, len(sample)), dtype=np.float64)
    kept.to_csv(OUT / "h047_support_observations.csv", index=False)
    return kept, mat, kept["support_quality"].to_numpy(dtype=np.float64)


def row_support_posterior(
    obs: pd.DataFrame,
    support_matrix: np.ndarray,
    quality: np.ndarray,
    route: pd.DataFrame,
    state: dict[str, np.ndarray],
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h043_prob: np.ndarray,
    h045_prob: np.ndarray,
) -> pd.DataFrame:
    centered = support_matrix - support_matrix.mean(axis=0, keepdims=True)
    direct = centered.T @ quality / (np.sum(np.abs(centered), axis=0) + 1.0e-9)
    direct = np.nan_to_num(direct)

    h042_support = np.abs(h042_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h043_support = np.abs(h043_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h045_support = np.abs(h045_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    phase_abs = np.abs(state["phase_dir_q2"])
    route_public = route["h044_public_transition_score"].to_numpy(dtype=np.float64)
    route_private = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    q2regime = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    h042like = route["h044_h042_like_score"].to_numpy(dtype=np.float64)
    phase_energy = route["h044_phase_energy_score"].to_numpy(dtype=np.float64)

    feature_pred = (
        0.30 * rank01(q2regime)
        + 0.23 * rank01(h042like)
        + 0.20 * rank01(phase_energy)
        + 0.16 * rank01(route_public)
        - 0.14 * rank01(route_private)
        + 0.18 * h042_support.astype(float)
        + 0.10 * h045_support.astype(float)
        + 0.06 * h043_support.astype(float)
    )
    posterior = (
        0.48 * rank01(direct)
        + 0.30 * rank01(feature_pred)
        + 0.12 * h045_support.astype(float)
        + 0.07 * h042_support.astype(float)
        + 0.03 * rank01(phase_abs)
    )
    out = route[KEYS].copy() if set(KEYS).issubset(route.columns) else pd.DataFrame({"row": np.arange(len(route))})
    out["row"] = np.arange(len(route))
    out["h047_direct_support_contrast"] = direct
    out["h047_feature_support_prior"] = feature_pred
    out["h047_support_posterior"] = posterior
    out["h047_phase_abs"] = phase_abs
    out["h047_h042_support"] = h042_support
    out["h047_h043_support"] = h043_support
    out["h047_h045_support"] = h045_support
    out["h047_public_score"] = route_public
    out["h047_private_score"] = route_private
    out["h047_q2regime_score"] = q2regime
    out.to_csv(OUT / "h047_row_support_posterior.csv", index=False)
    return out


def build_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h043_prob: np.ndarray,
    h045_prob: np.ndarray,
    state: dict[str, np.ndarray],
    route: pd.DataFrame,
    posterior: pd.DataFrame,
) -> pd.DataFrame:
    z012 = state["z_h012"]
    phase = state["phase_dir_q2"]
    allowed = state["support_q2"]
    h042_support = posterior["h047_h042_support"].to_numpy(dtype=bool)
    h043_support = posterior["h047_h043_support"].to_numpy(dtype=bool)
    h045_support = posterior["h047_h045_support"].to_numpy(dtype=bool)
    score = posterior["h047_support_posterior"].to_numpy(dtype=np.float64)
    contrast = posterior["h047_direct_support_contrast"].to_numpy(dtype=np.float64)
    h042_delta = logit(h042_prob)[:, Q2_I] - z012[:, Q2_I]
    generated: set[str] = set()
    specs: list[CandidateSpec] = []

    def add(rows_alpha: dict[int, float], family: str, support_source: str, k: int, alpha: float, core_alpha: float, tail_alpha: float) -> None:
        z = z012.copy()
        for row, a in rows_alpha.items():
            z[row, Q2_I] = z012[row, Q2_I] + a * phase[row]
        prob = sigmoid(z)
        changed_mask = np.abs(prob - h012_prob) > 1.0e-7
        q2_changed = changed_mask[:, Q2_I]
        changed = int(changed_mask.sum())
        if changed == 0 or np.max(np.abs(prob - h045_prob)) < 1.0e-12:
            return
        cid = safe_id(f"h047_{family}_c{changed}_{short_hash(prob)}")
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)

        idx = np.where(q2_changed)[0]
        delta = logit(prob)[:, Q2_I] - z012[:, Q2_I]
        h042_overlap = int(np.logical_and(q2_changed, h042_support).sum())
        h043_overlap = int(np.logical_and(q2_changed, h043_support).sum())
        h045_overlap = int(np.logical_and(q2_changed, h045_support).sum())
        h042_union = int(np.logical_or(q2_changed, h042_support).sum())
        h043_union = int(np.logical_or(q2_changed, h043_support).sum())
        h045_union = int(np.logical_or(q2_changed, h045_support).sum())
        expected, _proj, _resid, _ratio = h043.tangent_delta(prob, h012_prob, h042_prob)
        specs.append(
            CandidateSpec(
                candidate_id=cid,
                family=family,
                support_source=support_source,
                k=k,
                alpha=alpha,
                core_alpha=core_alpha,
                tail_alpha=tail_alpha,
                changed_cells=changed,
                changed_rows=int(np.max(changed_mask, axis=1).sum()),
                h042_overlap_cells=h042_overlap,
                h043_overlap_cells=h043_overlap,
                h045_overlap_cells=h045_overlap,
                h042_jaccard=float(h042_overlap / h042_union) if h042_union else 0.0,
                h043_jaccard=float(h043_overlap / h043_union) if h043_union else 0.0,
                h045_jaccard=float(h045_overlap / h045_union) if h045_union else 0.0,
                support_score_mean=float(score[idx].mean()) if len(idx) else 0.0,
                support_score_min=float(score[idx].min()) if len(idx) else 0.0,
                support_score_sum=float(score[idx].sum()) if len(idx) else 0.0,
                contrast_mean=float(contrast[idx].mean()) if len(idx) else 0.0,
                route_public_mean=float(route.loc[idx, "h044_public_transition_score"].mean()) if len(idx) else 0.0,
                route_private_mean=float(route.loc[idx, "h044_private_routine_score"].mean()) if len(idx) else 0.0,
                route_q2regime_mean=float(route.loc[idx, "h044_public_q2_regime_score"].mean()) if len(idx) else 0.0,
                mean_abs_logit_move=float(np.mean(np.abs(delta))),
                max_abs_logit_move=float(np.max(np.abs(delta))),
                mean_abs_prob_move=float(np.mean(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                max_abs_prob_move=float(np.max(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                tangent_expected_delta=expected,
                resolved_path=str(path),
            )
        )

    allowed_base = allowed & (posterior["h047_private_score"].to_numpy(dtype=np.float64) <= np.quantile(posterior["h047_private_score"], 0.82))
    for k in [35, 45, 55, 65, 75, 90, 105]:
        rows = top_indices(score, k, allowed_base)
        for alpha in [0.42, 0.50, 0.58, 0.66, 0.78, 0.92]:
            add({int(r): alpha for r in rows}, f"support_top{k}_a{alpha:g}", "posterior_top", k, alpha, alpha, 0.0)

    h042_idx = np.where(h042_support)[0]
    outside = allowed_base & ~h042_support
    for tail_k in [8, 14, 22, 34, 48, 64]:
        tail = top_indices(score, tail_k, outside)
        for core_alpha in [0.50, 0.58, 0.66, 0.78, 0.92]:
            for tail_alpha in [0.06, 0.10, 0.14, 0.22, 0.32, 0.44]:
                mask = {int(r): core_alpha for r in h042_idx}
                mask.update({int(r): tail_alpha for r in tail})
                add(mask, f"h042core_support_tail{tail_k}_a{core_alpha:g}_{tail_alpha:g}", "h042_core_plus_posterior_tail", len(mask), 0.0, core_alpha, tail_alpha)

    # The H046 lesson: do not flip private tails. Instead, only veto low
    # posterior/private-heavy rows from H043/H045 supports.
    for base_name, base_support in {"h043": h043_support, "h045": h045_support}.items():
        for q in [0.35, 0.45, 0.55, 0.65]:
            keep = base_support & (score >= np.quantile(score[base_support], q))
            rows = np.where(keep)[0]
            for alpha in [0.50, 0.58, 0.66, 0.78, 0.92]:
                add({int(r): alpha for r in rows}, f"{base_name}_support_sieve_q{q:g}_a{alpha:g}", f"{base_name}_sieve", len(rows), alpha, alpha, 0.0)

    out = pd.DataFrame([s.__dict__ for s in specs])
    if not out.empty:
        out.to_csv(OUT / "h047_generated_candidates.csv", index=False)
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
                "component_count": 1 + int(rec["tail_alpha"] > 0 and "tail" in str(rec["family"])),
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
        out.to_csv(OUT / "h047_candidate_pre_scores.csv", index=False)
    return out


def conditional_score(scored_raw: pd.DataFrame, rt: dict[str, object], atoms: list[object], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray, route: pd.DataFrame) -> pd.DataFrame:
    known = h045.known_augmented_features(rt, atoms, h012_prob, h042_prob, h043_prob, route)
    decoder_scores, decoder_loo = h045.evaluate_decoders(known)
    cand = h045.candidate_conditional_features(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    pred = h045.predict_candidates(known, cand, decoder_scores)
    scored = h045.score_candidates(scored_raw, pred)
    decoder_scores.to_csv(OUT / "h047_conditional_decoder_scores.csv", index=False)
    decoder_loo.to_csv(OUT / "h047_conditional_decoder_loo.csv", index=False)
    return scored


def rank_h047(scored: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return scored
    meta_cols = [
        "candidate_id",
        "support_source",
        "k",
        "alpha",
        "core_alpha",
        "tail_alpha",
        "h042_overlap_cells",
        "h043_overlap_cells",
        "h045_overlap_cells",
        "h042_jaccard",
        "h043_jaccard",
        "h045_jaccard",
        "support_score_mean",
        "support_score_min",
        "support_score_sum",
        "contrast_mean",
        "route_public_mean",
        "route_private_mean",
        "route_q2regime_mean",
        "tangent_expected_delta",
    ]
    out = scored.merge(generated[[c for c in meta_cols if c in generated.columns]], on="candidate_id", how="left")
    h045_dec = pd.read_csv(HITL / "h045_conditional_route_action_decoder_jepa" / "h045_decision.csv").iloc[0]
    full_margin = out["full_known_cond_margin_vs_h012_median"].fillna(0.01)
    pre_margin = out["pre_h042_cond_margin_vs_h012_median"].fillna(0.01)
    route_delta = out["route_equation_delta_vs_h012"].fillna(0.01)
    h025 = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    support = out["full_known_cond_support_better_than_h012"].fillna(0.0)
    score_mean = out["support_score_mean"].fillna(0.0)
    h045_j = out["h045_jaccard"].fillna(0.0)
    out["h047_support_identity_score"] = (
        1.30 * full_margin.rank(method="average", pct=True)
        + 0.52 * pre_margin.rank(method="average", pct=True)
        + 0.70 * route_delta.rank(method="average", pct=True)
        + 0.42 * h025.rank(method="average", pct=True)
        + 0.30 * h024.rank(method="average", pct=True)
        - 0.42 * support
        - 0.22 * score_mean.rank(method="average", pct=True)
        + 0.12 * h045_j.rank(method="average", pct=True)
    )
    beats_h045_axes = (
        (out["full_known_cond_margin_vs_h012_median"] < float(h045_dec["full_known_cond_margin_vs_h012_median"])).astype(int)
        + (out["route_equation_delta_vs_h012"] < float(h045_dec["route_equation_delta_vs_h012"])).astype(int)
        + (out["h025_score"] < float(h045_dec["h025_score"])).astype(int)
        + (out["pre_h012_h024_margin_vs_h012_median"] < float(h045_dec["pre_h012_h024_margin_vs_h012_median"])).astype(int)
    )
    out["h047_beats_h045_axes"] = beats_h045_axes
    out["h047_promotable"] = (
        (out["changed_cells_vs_h012"].between(40, 115))
        & (out["full_known_cond_margin_vs_h012_median"] < -0.00011)
        & (out["full_known_cond_support_better_than_h012"] >= 0.58)
        & (out["pre_h042_cond_margin_vs_h012_median"] < 0.00012)
        & (out["route_equation_delta_vs_h012"] < -0.00016)
        & (out["h025_score"] < 0.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00090)
        & ((out["h047_beats_h045_axes"] >= 2) | (out["h045_jaccard"] < 0.80))
    )
    out = out.sort_values(["h047_promotable", "h047_support_identity_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h047_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        out = pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no scored candidates"}])
        out.to_csv(OUT / "h047_decision.csv", index=False)
        return out
    selected = scored.iloc[0].copy()
    promote = bool(selected.get("h047_promotable", False))
    source = Path(str(selected["resolved_path"]))
    suffix = str(selected["candidate_id"]).rsplit("_", 1)[-1]
    root_path = ROOT / f"submission_h047_q2_support_identity_{suffix}_uploadsafe.csv"
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
        "reason": "support identity posterior gate passed" if promote else "no support-identity candidate beat H045 gate",
        "expected_relation": "beats H045 if Q2 support identity is the missing hidden state",
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
        "h045_jaccard",
        "support_score_mean",
        "h047_beats_h045_axes",
        "h047_support_identity_score",
        "h047_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h047_decision.csv", index=False)
    return out


def write_report(obs: pd.DataFrame, posterior: pd.DataFrame, generated: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame) -> None:
    lines = [
        "# H047 Q2 Support-Identity Posterior HS-JEPA",
        "",
        "Question: after rejecting Q2 amplitude bifurcation, can we infer the hidden Q2 support identity directly?",
        "",
        f"- support observations: `{len(obs)}`",
        f"- generated candidates: `{len(generated)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- promotable candidates: `{int(scored['h047_promotable'].sum()) if 'h047_promotable' in scored else 0}`",
        "",
        "Top row support posterior:",
        "",
        md_table(
            posterior[
                [
                    "row",
                    "h047_support_posterior",
                    "h047_direct_support_contrast",
                    "h047_feature_support_prior",
                    "h047_h042_support",
                    "h047_h043_support",
                    "h047_h045_support",
                    "h047_public_score",
                    "h047_private_score",
                ]
            ].sort_values("h047_support_posterior", ascending=False).head(20)
        ),
        "",
        "Top H047 candidates:",
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
                    "h045_jaccard",
                    "h047_beats_h045_axes",
                    "h047_promotable",
                    "h047_support_identity_score",
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
        "- If promoted, support identity is the next hidden-state variable after H046 killed amplitude bifurcation.",
        "- If not promoted, current evidence says H045's route-pruned support is still a stronger next public sensor than a new contrastive support posterior.",
    ]
    (OUT / "h047_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob, h043_prob, h045_prob = load_anchor_probs()
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = h045.build_route_context(rt, state, h012_prob, h042_prob, h043_prob)
    obs, support_matrix, quality = load_support_observations(sample, h012_prob)
    posterior = row_support_posterior(obs, support_matrix, quality, route, state, h012_prob, h042_prob, h043_prob, h045_prob)
    generated = build_candidates(sample, h012_prob, h042_prob, h043_prob, h045_prob, state, route, posterior)
    known_aug, decoder_scores, _ = h043.known_features_with_h042(rt, atoms, h042_prob)
    pre = candidate_frame(generated, rt, sample, h012_prob, state)
    scored_raw, _ = h042.score_candidates(rt, atoms, pre, known_aug, decoder_scores)
    scored_cond = conditional_score(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    scored = rank_h047(scored_cond, generated)
    decision = select_and_copy(scored, sample)
    write_report(obs, posterior, generated, scored, decision)
    print("H047 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H047 decision:", decision.iloc[0]["decision"])
    print("H047 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
