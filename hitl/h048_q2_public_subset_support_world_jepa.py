#!/usr/bin/env python3
"""H048: Q2 public-subset support-world HS-JEPA.

H047 inferred Q2 support identity from candidate support masks. H048 asks a
stronger question:

    is that support identity also a prior over the hidden public subset?

The experiment inserts H047's row support posterior into the public-world
sampler as a row prior, then materializes only Q2-local phase actions from the
resulting public-subset rows. This is not another amplitude tweak; it is a
joint support/world-assignment test.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h048_q2_public_subset_support_world_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q2_I = TARGETS.index("Q2")
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H043 = "submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv"
H045 = "submission_h045_condroute_q2regime75_a0.66_5988dfb9_uploadsafe.csv"
H047 = "submission_h047_q2_support_identity_98737e9b_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"


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
    h042_jaccard: float
    h047_jaccard: float
    h045_jaccard: float
    support_mean: float
    world_mean: float
    joint_mean: float
    route_public_mean: float
    route_private_mean: float
    mean_abs_logit_move: float
    max_abs_logit_move: float
    mean_abs_prob_move: float
    max_abs_prob_move: float
    tangent_expected_delta: float
    world_expected_delta: float
    world_expected_iqr: float
    resolved_path: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h047 = import_module(HITL / "h047_q2_support_identity_jepa.py", "h047_for_h048")
h041 = import_module(HITL / "h041_route_prior_equation_solver_jepa.py", "h041_for_h048")
h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h048")

h047.OUT = OUT
h047.h045.OUT = OUT
h047.h043.OUT = OUT
h047.h044.OUT = OUT
h047.h042.OUT = OUT
h041.OUT = OUT
h042 = h047.h042
h043 = h047.h043
h045 = h047.h045


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


def rank01(x: np.ndarray | pd.Series, high: bool = True) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    s = pd.Series(arr).replace([np.inf, -np.inf], np.nan).fillna(np.nanmedian(arr[np.isfinite(arr)]) if np.isfinite(arr).any() else 0.0)
    if s.nunique(dropna=True) <= 1:
        out = np.full(len(s), 0.5, dtype=np.float64)
    else:
        out = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return out if high else 1.0 - out


def normalize_prior(x: np.ndarray, floor: float = 0.012, power: float = 1.0) -> np.ndarray:
    r = rank01(np.asarray(x, dtype=np.float64))
    p = floor + np.power(np.clip(r, 0.0, 1.0), power)
    p = np.clip(p, floor, None)
    return p / p.sum()


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


def jaccard(a: np.ndarray, b: np.ndarray) -> float:
    inter = int(np.logical_and(a, b).sum())
    union = int(np.logical_or(a, b).sum())
    return float(inter / union) if union else 0.0


def load_anchor_probs() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    h012 = h036.load_sub(H012)
    sample = h012[KEYS].copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h036.load_sub(H042, sample)[TARGETS].to_numpy(dtype=np.float64)
    h043_prob = h036.load_sub(H043, sample)[TARGETS].to_numpy(dtype=np.float64)
    h045_prob = h036.load_sub(H045, sample)[TARGETS].to_numpy(dtype=np.float64)
    h047_prob = h036.load_sub(H047, sample)[TARGETS].to_numpy(dtype=np.float64)
    return sample, h012_prob, h042_prob, h043_prob, h045_prob, h047_prob


def build_h048_q_sources(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    h042_prob: np.ndarray,
    h047_prob: np.ndarray,
    state: dict[str, np.ndarray],
    posterior: pd.DataFrame,
) -> dict[str, np.ndarray]:
    q_sources = h041.build_route_q_sources(sample, h012_prob, e247_prob)
    z012 = logit(h012_prob)
    phase = state["phase_dir_q2"]
    support_score = posterior["h047_support_posterior"].to_numpy(dtype=np.float64)
    q2_weight = np.clip(0.20 + 0.82 * rank01(support_score), 0.0, 1.0)

    z_support = z012.copy()
    z_support[:, Q2_I] = z012[:, Q2_I] + q2_weight * phase
    q_sources["h048_q2_support_phase_q"] = sigmoid(z_support)

    z_coretail = z012.copy()
    z_coretail[:, Q2_I] = 0.55 * logit(h047_prob)[:, Q2_I] + 0.30 * logit(h042_prob)[:, Q2_I] + 0.15 * z_support[:, Q2_I]
    q_sources["h048_q2_coretail_q"] = sigmoid(z_coretail)

    z_soft = z012.copy()
    z_soft[:, Q2_I] = z012[:, Q2_I] + np.clip(rank01(support_score) - 0.20, 0.0, 1.0) * 0.62 * phase
    q_sources["h048_q2_public_soft_q"] = sigmoid(z_soft)
    return {k: clip_prob(v) for k, v in q_sources.items()}


def build_h048_row_priors(sample: pd.DataFrame, posterior: pd.DataFrame) -> dict[str, np.ndarray]:
    priors = h041.build_route_row_priors(sample)
    support = posterior["h047_support_posterior"].to_numpy(dtype=np.float64)
    direct = posterior["h047_direct_support_contrast"].to_numpy(dtype=np.float64)
    public = posterior["h047_public_score"].to_numpy(dtype=np.float64)
    private = posterior["h047_private_score"].to_numpy(dtype=np.float64)
    q2regime = posterior["h047_q2regime_score"].to_numpy(dtype=np.float64)
    h042_support = posterior["h047_h042_support"].to_numpy(dtype=bool).astype(float)
    h045_support = posterior["h047_h045_support"].to_numpy(dtype=bool).astype(float)

    specs = {
        "h048_support_identity": support,
        "h048_support_identity_sharp": support,
        "h048_support_direct": direct,
        "h048_support_public": support * (0.45 + public),
        "h048_support_public_not_private": support * (0.50 + public) * (1.15 - 0.45 * private),
        "h048_support_q2regime": support * (0.45 + q2regime),
        "h048_core_tail_prior": support + 0.22 * h042_support + 0.11 * h045_support,
        "h048_public_core_tail": support * (0.40 + public) + 0.18 * h042_support,
    }
    for name, score in specs.items():
        power = 2.05 if name.endswith("_sharp") else 1.35
        priors[name] = normalize_prior(score, floor=0.010, power=power)
    return priors


def make_configs(q_sources: dict[str, np.ndarray], row_priors: dict[str, np.ndarray]) -> list[object]:
    q_keep = [
        "h012",
        "h012posterior",
        "posterior_vector_mid",
        "h041_route_public_q",
        "h041_route_private_tempered_q",
        "h048_q2_support_phase_q",
        "h048_q2_coretail_q",
        "h048_q2_public_soft_q",
    ]
    prior_keep = [
        "uniform",
        "h041_public_route",
        "h041_public_not_private",
        "h041_memory_disagree_public",
        "h048_support_identity",
        "h048_support_identity_sharp",
        "h048_support_public",
        "h048_support_public_not_private",
        "h048_support_q2regime",
        "h048_core_tail_prior",
        "h048_public_core_tail",
    ]
    configs = []
    for q_name in [q for q in q_keep if q in q_sources]:
        for prior_name in [p for p in prior_keep if p in row_priors]:
            for size in [45, 59, 75, 95, 125, 155, 190]:
                configs.append(h036.WorldConfig(q_name, prior_name, size, "sample", 10))
                configs.append(h036.WorldConfig(q_name, prior_name, size, "temperature_sample", 7))
                configs.append(h036.WorldConfig(q_name, prior_name, size, "map", 3))
    return configs


def posterior_from_configs(
    particle_df: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
    h012_prob: np.ndarray,
    config_summary: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    support_configs = config_summary[config_summary["row_prior"].astype(str).str.startswith("h048")].head(36)
    general_configs = config_summary.head(36)
    key_cols = ["q_source", "row_prior", "subset_size", "label_mode"]
    keep = pd.concat([support_configs, general_configs], ignore_index=True).drop_duplicates(key_cols)
    tagged = particle_df.merge(keep[key_cols + ["lofo_mae", "lofo_max_abs"]], on=key_cols, how="inner")
    if tagged.empty:
        tagged = particle_df.copy()
        tagged["lofo_mae"] = float(config_summary["lofo_mae"].median()) if len(config_summary) else tagged["mae"]
        tagged["lofo_max_abs"] = tagged["max_abs"]
    tagged["actual_mae"] = tagged["mae"]
    tagged["selection_mae"] = (
        0.52 * tagged["mae"].to_numpy(dtype=np.float64)
        + 0.38 * tagged["lofo_mae"].to_numpy(dtype=np.float64)
        + 0.10 * tagged["max_abs"].to_numpy(dtype=np.float64)
    )
    post = tagged.copy()
    post["mae"] = post["selection_mae"]
    q_post, q_cond, row_post, top_worlds = h036.posterior_from_worlds(post, masks, labels, h012_prob, top_n=1500)
    for col in ["actual_mae", "selection_mae", "lofo_mae", "lofo_max_abs"]:
        if col not in top_worlds.columns:
            top_worlds = top_worlds.merge(tagged[["particle", col]], on="particle", how="left")
    top_worlds.to_csv(OUT / "h048_top_worlds.csv", index=False)
    return q_post, q_cond, row_post, top_worlds


def build_world_tables(sample: pd.DataFrame, h012_prob: np.ndarray, q_post: np.ndarray, q_cond: np.ndarray, row_post: np.ndarray, posterior: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cell, row = h036.build_posterior_tables(sample, h012_prob, q_post, q_cond, row_post)
    add_cols = [
        "row",
        "h047_support_posterior",
        "h047_direct_support_contrast",
        "h047_public_score",
        "h047_private_score",
        "h047_q2regime_score",
        "h047_h042_support",
        "h047_h045_support",
    ]
    row = row.merge(posterior[[c for c in add_cols if c in posterior.columns]], on="row", how="left")
    cell = cell.merge(posterior[[c for c in add_cols if c in posterior.columns]], on="row", how="left")
    cell.to_csv(OUT / "h048_world_posterior_cells.csv", index=False)
    row.to_csv(OUT / "h048_world_posterior_rows.csv", index=False)
    return cell, row


def build_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h045_prob: np.ndarray,
    h047_prob: np.ndarray,
    state: dict[str, np.ndarray],
    posterior: pd.DataFrame,
    row_post: np.ndarray,
    top_worlds: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    z012 = state["z_h012"]
    phase = state["phase_dir_q2"]
    support_allowed = state["support_q2"]
    support = posterior["h047_support_posterior"].to_numpy(dtype=np.float64)
    public = posterior["h047_public_score"].to_numpy(dtype=np.float64)
    private = posterior["h047_private_score"].to_numpy(dtype=np.float64)
    q2regime = posterior["h047_q2regime_score"].to_numpy(dtype=np.float64)
    h042_support = np.abs(h042_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h045_support = np.abs(h045_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    h047_support = np.abs(h047_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7
    joint = (
        0.36 * rank01(row_post)
        + 0.30 * rank01(support)
        + 0.17 * rank01(public)
        + 0.13 * rank01(q2regime)
        - 0.12 * rank01(private)
        + 0.11 * h042_support.astype(float)
        + 0.08 * h047_support.astype(float)
    )
    allowed = support_allowed & (private <= np.quantile(private, 0.84))
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
        if changed == 0:
            return
        cid = safe_id(f"h048_{family}_c{changed}_{short_hash(prob)}")
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        idx = np.where(q2_changed)[0]
        delta = logit(prob)[:, Q2_I] - z012[:, Q2_I]
        tangent_delta, _proj, _resid, _ratio = h043.tangent_delta(prob, h012_prob, h042_prob)
        world_delta, world_iqr = h036.expected_delta_for_prob(prob, h012_prob, top_worlds, masks, labels)
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
                h042_jaccard=jaccard(q2_changed, h042_support),
                h047_jaccard=jaccard(q2_changed, h047_support),
                h045_jaccard=jaccard(q2_changed, h045_support),
                support_mean=float(support[idx].mean()) if len(idx) else 0.0,
                world_mean=float(row_post[idx].mean()) if len(idx) else 0.0,
                joint_mean=float(joint[idx].mean()) if len(idx) else 0.0,
                route_public_mean=float(public[idx].mean()) if len(idx) else 0.0,
                route_private_mean=float(private[idx].mean()) if len(idx) else 0.0,
                mean_abs_logit_move=float(np.mean(np.abs(delta))),
                max_abs_logit_move=float(np.max(np.abs(delta))),
                mean_abs_prob_move=float(np.mean(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                max_abs_prob_move=float(np.max(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                tangent_expected_delta=tangent_delta,
                world_expected_delta=world_delta,
                world_expected_iqr=world_iqr,
                resolved_path=str(path),
            )
        )

    h042_idx = np.where(h042_support)[0]
    outside_h042 = allowed & ~h042_support
    for tail_k in [6, 10, 14, 20, 28, 40]:
        tail = top_indices(joint, tail_k, outside_h042)
        for core_alpha in [0.58, 0.66, 0.78, 0.92]:
            for tail_alpha in [0.06, 0.10, 0.16, 0.24, 0.34, 0.46]:
                rows = {int(r): core_alpha for r in h042_idx}
                rows.update({int(r): tail_alpha for r in tail})
                add(rows, f"h042core_world_tail{tail_k}_a{core_alpha:g}_{tail_alpha:g}", "h042_core_plus_world_tail", len(rows), 0.0, core_alpha, tail_alpha)

    for k in [45, 53, 59, 68, 75, 90]:
        rows = top_indices(joint, k, allowed)
        for alpha in [0.50, 0.58, 0.66, 0.78, 0.92]:
            add({int(r): alpha for r in rows}, f"world_support_top{k}_a{alpha:g}", "world_support_top", k, alpha, alpha, 0.0)

    for base_name, base in {"h047": h047_support, "h045": h045_support}.items():
        for q in [0.30, 0.42, 0.55, 0.68]:
            keep = base & allowed & (joint >= np.quantile(joint[base], q))
            rows = np.where(keep)[0]
            for alpha in [0.50, 0.58, 0.66, 0.78]:
                add({int(r): alpha for r in rows}, f"{base_name}_world_sieve_q{q:g}_a{alpha:g}", f"{base_name}_world_sieve", len(rows), alpha, alpha, 0.0)

    out = pd.DataFrame([s.__dict__ for s in specs])
    if not out.empty:
        out.to_csv(OUT / "h048_generated_candidates.csv", index=False)
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
                "h048_world_delta_vs_h012": float(rec["world_expected_delta"]),
                "h048_world_iqr": float(rec["world_expected_iqr"]),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out.to_csv(OUT / "h048_candidate_pre_scores.csv", index=False)
    return out


def conditional_score(scored_raw: pd.DataFrame, rt: dict[str, object], atoms: list[object], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray, route: pd.DataFrame) -> pd.DataFrame:
    known = h045.known_augmented_features(rt, atoms, h012_prob, h042_prob, h043_prob, route)
    decoder_scores, decoder_loo = h045.evaluate_decoders(known)
    cand = h045.candidate_conditional_features(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    pred = h045.predict_candidates(known, cand, decoder_scores)
    scored = h045.score_candidates(scored_raw, pred)
    decoder_scores.to_csv(OUT / "h048_conditional_decoder_scores.csv", index=False)
    decoder_loo.to_csv(OUT / "h048_conditional_decoder_loo.csv", index=False)
    return scored


def rank_h048(scored: pd.DataFrame, generated: pd.DataFrame, config_summary: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return scored
    meta_cols = [
        "candidate_id",
        "support_source",
        "k",
        "alpha",
        "core_alpha",
        "tail_alpha",
        "h042_jaccard",
        "h047_jaccard",
        "h045_jaccard",
        "support_mean",
        "world_mean",
        "joint_mean",
        "route_public_mean",
        "route_private_mean",
        "tangent_expected_delta",
        "world_expected_delta",
        "world_expected_iqr",
    ]
    out = scored.merge(generated[[c for c in meta_cols if c in generated.columns]], on="candidate_id", how="left")
    support_best = config_summary[config_summary["row_prior"].astype(str).str.startswith("h048")]["lofo_mae"].min()
    uniform_best = config_summary[config_summary["row_prior"].astype(str).eq("uniform")]["lofo_mae"].min()
    out["h048_support_lofo_gain_vs_uniform"] = float(uniform_best - support_best) if np.isfinite(support_best) and np.isfinite(uniform_best) else np.nan

    full = out["full_known_cond_margin_vs_h012_median"].fillna(0.01)
    pre = out["pre_h042_cond_margin_vs_h012_median"].fillna(0.01)
    route = out["route_equation_delta_vs_h012"].fillna(0.01)
    world = out["h048_world_delta_vs_h012"].fillna(0.01)
    h025 = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    support = out["full_known_cond_support_better_than_h012"].fillna(0.0)
    joint = out["joint_mean"].fillna(0.0)
    out["h048_world_support_score"] = (
        1.26 * full.rank(method="average", pct=True)
        + 0.55 * pre.rank(method="average", pct=True)
        + 0.64 * route.rank(method="average", pct=True)
        + 0.45 * world.rank(method="average", pct=True)
        + 0.36 * h025.rank(method="average", pct=True)
        + 0.28 * h024.rank(method="average", pct=True)
        - 0.35 * support
        - 0.18 * joint.rank(method="average", pct=True)
    )
    out["h048_promotable"] = (
        (out["changed_cells_vs_h012"].between(42, 95))
        & (out["full_known_cond_margin_vs_h012_median"] < -0.00014)
        & (out["full_known_cond_support_better_than_h012"] >= 0.58)
        & (out["pre_h042_cond_margin_vs_h012_median"] < 0.00005)
        & (out["route_equation_delta_vs_h012"] < -0.00016)
        & (out["h048_world_delta_vs_h012"] < -0.00004)
        & (out["h025_score"] < 0.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00085)
        & (out["h048_support_lofo_gain_vs_uniform"].fillna(-1.0) > -0.00003)
    )
    out = out.sort_values(["h048_promotable", "h048_world_support_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h048_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        out = pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no scored candidates"}])
        out.to_csv(OUT / "h048_decision.csv", index=False)
        return out
    selected = scored.iloc[0].copy()
    promote = bool(selected.get("h048_promotable", False))
    source = Path(str(selected["resolved_path"]))
    suffix = str(selected["candidate_id"]).rsplit("_", 1)[-1]
    root_path = ROOT / f"submission_h048_q2_public_subset_support_{suffix}_uploadsafe.csv"
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
        "reason": "public-subset support world gate passed" if promote else "support-world candidate did not clear joint gate",
        "expected_relation": "beats H047 if Q2 support identity is also a public-subset prior",
    }
    for col in [
        "changed_cells_vs_h012",
        "full_known_cond_margin_vs_h012_median",
        "full_known_cond_support_better_than_h012",
        "pre_h042_cond_margin_vs_h012_median",
        "route_equation_delta_vs_h012",
        "h048_world_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "h025_score",
        "h042_jaccard",
        "h047_jaccard",
        "h045_jaccard",
        "joint_mean",
        "h048_support_lofo_gain_vs_uniform",
        "h048_world_support_score",
        "h048_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h048_decision.csv", index=False)
    return out


def write_report(config_summary: pd.DataFrame, top_worlds: pd.DataFrame, row_table: pd.DataFrame, generated: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame) -> None:
    support_cfg = config_summary[config_summary["row_prior"].astype(str).str.startswith("h048")]
    uniform_cfg = config_summary[config_summary["row_prior"].astype(str).eq("uniform")]
    support_best = float(support_cfg["lofo_mae"].min()) if len(support_cfg) else np.nan
    uniform_best = float(uniform_cfg["lofo_mae"].min()) if len(uniform_cfg) else np.nan
    lines = [
        "# H048 Q2 Public-Subset Support-World HS-JEPA",
        "",
        "Question: is H047 support identity also a hidden public-subset prior?",
        "",
        "Public-world fit:",
        "",
        f"- best H048 support-prior LOFO MAE: `{support_best:.9f}`",
        f"- best uniform LOFO MAE: `{uniform_best:.9f}`",
        f"- support LOFO gain vs uniform: `{uniform_best - support_best:.9f}`" if np.isfinite(support_best) and np.isfinite(uniform_best) else "- support LOFO gain vs uniform: `nan`",
        "",
        "Top config families:",
        "",
        md_table(config_summary.head(16), 16),
        "",
        "Top worlds:",
        "",
        md_table(top_worlds[[c for c in ["particle", "q_source", "row_prior", "subset_size", "label_mode", "actual_mae", "selection_mae", "lofo_mae", "spearman", "posterior_weight"] if c in top_worlds.columns]].head(16), 16),
        "",
        "Top public-support rows:",
        "",
        md_table(row_table[[c for c in ["row", "subject_id", "sleep_date", "world_public_prob", "h047_support_posterior", "h047_public_score", "h047_private_score", "h047_q2regime_score", "h047_h042_support", "h047_h045_support"] if c in row_table.columns]].sort_values(["world_public_prob", "h047_support_posterior"], ascending=False).head(20), 20),
        "",
        f"- generated candidates: `{len(generated)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- promotable candidates: `{int(scored['h048_promotable'].sum()) if 'h048_promotable' in scored else 0}`",
        "",
        "Top H048 candidates:",
        "",
        md_table(scored[[c for c in ["candidate_id", "changed_cells_vs_h012", "full_known_cond_margin_vs_h012_median", "full_known_cond_support_better_than_h012", "pre_h042_cond_margin_vs_h012_median", "route_equation_delta_vs_h012", "h048_world_delta_vs_h012", "pre_h012_h024_margin_vs_h012_median", "h025_score", "h042_jaccard", "h047_jaccard", "h048_promotable", "h048_world_support_score"] if c in scored.columns]].head(20), 20) if not scored.empty else "_empty_",
        "",
        "Decision:",
        "",
        md_table(decision),
        "",
        "Interpretation:",
        "",
        "- If promoted and public improves, H047 support identity is not only a Q2 action support; it is also a public-subset prior.",
        "- If no candidate promotes, support identity may still be real locally, but current public-world assignment does not improve action translation.",
        "- If public later rejects the promoted file, the public-subset prior is overfitting local world equations and H047 exact support remains the cleaner sensor.",
    ]
    (OUT / "h048_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob, h043_prob, h045_prob, h047_prob = load_anchor_probs()
    e247_prob = h036.load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = h045.build_route_context(rt, state, h012_prob, h042_prob, h043_prob)
    posterior = pd.read_csv(HITL / "h047_q2_support_identity_jepa" / "h047_row_support_posterior.csv")
    if len(posterior) != len(sample):
        raise ValueError("H047 posterior length mismatch")

    known, _sample2, _h012_2, pred_by_file = h036.load_system()
    files, d0_rows, d1_adj, actual_delta = h036.build_delta_tensors(known, pred_by_file, h012_prob)
    q_sources = build_h048_q_sources(sample, h012_prob, e247_prob, h042_prob, h047_prob, state, posterior)
    row_priors = build_h048_row_priors(sample, posterior)
    configs = make_configs(q_sources, row_priors)
    pd.DataFrame([cfg.__dict__ for cfg in configs]).to_csv(OUT / "h048_world_configs.csv", index=False)

    particle_df, masks, labels, preds = h036.sample_worlds(configs, q_sources, row_priors, d0_rows, d1_adj, actual_delta)
    particle_df.to_csv(OUT / "h048_world_particles.csv", index=False)
    pred_df = pd.DataFrame(preds, columns=[f"pred_delta_{Path(f).stem}" for f in files])
    pred_df.insert(0, "particle", np.arange(len(pred_df)))
    pred_df.to_csv(OUT / "h048_world_predicted_deltas.csv", index=False)
    config_summary = h041.config_lofo_summary(particle_df, preds, actual_delta)
    legacy_lofo = OUT / "h041_world_config_lofo_summary.csv"
    if legacy_lofo.exists():
        legacy_lofo.unlink()
    config_summary.to_csv(OUT / "h048_world_config_lofo_summary.csv", index=False)
    q_post, q_cond, row_post, top_worlds = posterior_from_configs(particle_df, masks, labels, h012_prob, config_summary)
    _cell_table, row_table = build_world_tables(sample, h012_prob, q_post, q_cond, row_post, posterior)

    generated = build_candidates(sample, h012_prob, h042_prob, h045_prob, h047_prob, state, posterior, row_post, top_worlds, masks, labels)
    known_aug, decoder_scores, _ = h043.known_features_with_h042(rt, atoms, h042_prob)
    pre = candidate_frame(generated, rt, sample, h012_prob, state)
    scored_raw, _ = h042.score_candidates(rt, atoms, pre, known_aug, decoder_scores)
    scored_cond = conditional_score(scored_raw, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    scored = rank_h048(scored_cond, generated, config_summary)
    decision = select_and_copy(scored, sample)
    known.to_csv(OUT / "h048_known_public_sensors.csv", index=False)
    write_report(config_summary, top_worlds, row_table, generated, scored, decision)
    print("H048 selected:", decision.iloc[0].get("selected_candidate_id", ""))
    print("H048 decision:", decision.iloc[0]["decision"])
    print("H048 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
