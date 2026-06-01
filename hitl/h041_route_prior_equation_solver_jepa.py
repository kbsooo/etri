#!/usr/bin/env python3
"""H041: route-prior public/private equation solver HS-JEPA.

H040 killed the simple route materializer: route state creates large
public-world proxy gains, but post-hoc row-route edits are rejected by H024.

H041 moves the same route latent one layer earlier:

    context = known public LB equations + H040 human-state route scores
    target  = hidden public subset and row-target label world
    action  = infer the public equation posterior with route priors inside the
              sampler, then test whether the resulting posterior yields an
              H012-compatible action

If this works, route is not an edit gate; it is a prior over the hidden public
world.  If it fails, the next jump must be a different equation formulation,
not another row/cell route materialization.
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
OUT = HITL / "h041_route_prior_equation_solver_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_LB = 0.5681234831


@dataclass(frozen=True)
class RouteWorldConfig:
    q_source: str
    row_prior: str
    subset_size: int
    label_mode: str
    particles: int


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def h036_module(name: str = "h036_for_h041") -> object:
    return import_module(HITL / "h036_global_public_world_solver_jepa.py", name)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def rank01(x: np.ndarray | pd.Series, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high else 1.0 - r


def normalize_prior(x: np.ndarray, floor: float = 0.02, power: float = 1.0) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=np.nanmedian(arr[np.isfinite(arr)]) if np.isfinite(arr).any() else 0.0)
    r = rank01(arr)
    p = floor + np.power(np.clip(r, 0.0, 1.0), power)
    p = np.clip(p, floor, None)
    return p / p.sum()


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:8]


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


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return h036_module("h036_for_h041_loader").load_sub(name, sample)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def weighted_delta(prob: np.ndarray, base: np.ndarray, q: np.ndarray, weight: np.ndarray) -> float:
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim == 1:
        w = np.repeat(w[:, None], len(TARGETS), axis=1)
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)
    w = np.clip(w, 0.0, None)
    if float(w.sum()) <= 1.0e-12:
        w = np.ones_like(base)
    return float(np.sum(w * (bce(prob, q) - bce(base, q))) / np.sum(w))


def pivot_cells(path: Path, value_col: str, sample: pd.DataFrame) -> np.ndarray:
    h036 = h036_module("h036_for_h041_pivot")
    return h036.pivot_cell_table(path, value_col, sample)


def load_route_system() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    h036 = h036_module("h036_for_h041_system")
    known, sample, h012_prob, pred_by_file = h036.load_system()
    e247_prob = load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    return known, h012_prob, e247_prob, sample, pred_by_file, {}


def build_route_q_sources(sample: pd.DataFrame, h012_prob: np.ndarray, e247_prob: np.ndarray) -> dict[str, np.ndarray]:
    h036 = h036_module("h036_for_h041_q")
    q_sources = h036.build_q_sources(sample, h012_prob)

    h012posterior = pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    memory = pivot_cells(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv", "memory_prob_full", sample)
    row_state = pd.read_csv(HITL / "h040_discrete_route_assignment_jepa" / "h040_row_route_state.csv")
    row_state = row_state.sort_values("row").reset_index(drop=True)
    public = row_state["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    transition = row_state["transition_exception_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = row_state["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]

    z_h012 = logit(h012_prob)
    z_posterior_world = 0.55 * logit(h012posterior) + 0.45 * logit(h036world)
    z_public = z_h012 + np.clip(public, 0.0, 1.0) * (z_posterior_world - z_h012)
    z_transition = z_h012 + np.clip(transition, 0.0, 1.0) * (logit(h036world) - z_h012)
    z_private_tempered = z_public - 0.45 * np.clip(private, 0.0, 1.0) * (z_public - logit(memory))

    q_sources["h041_route_public_q"] = sigmoid(z_public)
    q_sources["h041_route_transition_q"] = sigmoid(z_transition)
    q_sources["h041_route_private_tempered_q"] = sigmoid(z_private_tempered)
    q_sources["h041_route_public_hardmix"] = clip_prob(
        0.50 * h012posterior + 0.30 * h036world + 0.20 * h012_prob
    )
    q_sources["h041_route_memory_contrast_q"] = clip_prob(
        0.62 * h036world + 0.23 * h012posterior + 0.15 * (1.0 - memory)
    )
    q_sources["h041_e247_phase_q"] = sigmoid(logit(e247_prob) + 0.88 * (logit(h012posterior) - logit(e247_prob)))
    return {k: clip_prob(v) for k, v in q_sources.items()}


def build_route_row_priors(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    h036 = h036_module("h036_for_h041_priors")
    priors = h036.build_row_priors(sample)
    row = pd.read_csv(HITL / "h040_discrete_route_assignment_jepa" / "h040_row_route_state.csv")
    row = row.sort_values("row").reset_index(drop=True)
    if len(row) != len(sample):
        raise ValueError("H040 row state length mismatch")

    public = row["public_route_score"].to_numpy(dtype=np.float64)
    transition = row["transition_exception_route_score"].to_numpy(dtype=np.float64)
    private = row["private_memory_route_score"].to_numpy(dtype=np.float64)
    uncertainty = row["route_uncertainty_score"].to_numpy(dtype=np.float64)
    support = row["support_count"].to_numpy(dtype=np.float64)
    disagree = row["memory_disagree_rate"].to_numpy(dtype=np.float64)
    row_public = row["row_public_prob"].to_numpy(dtype=np.float64)
    reliability = row["row_full_reliability_q"].to_numpy(dtype=np.float64)

    route_specs = {
        "h041_public_route": public,
        "h041_transition_exception": transition,
        "h041_public_x_transition": public * (0.4 + transition),
        "h041_public_not_private": public * (1.05 - 0.65 * private),
        "h041_uncertain_public": uncertainty * (0.55 + public),
        "h041_support_public": public * (0.3 + support / max(float(np.max(support)), 1.0)),
        "h041_memory_disagree_public": public * (0.4 + disagree),
        "h041_world_public_prior": row_public * (0.45 + public),
        "h041_reliable_transition": transition * (0.35 + reliability),
        "h041_private_inverse": 1.1 - private + 0.25 * public,
    }
    for name, score in route_specs.items():
        priors[name] = normalize_prior(score, floor=0.018, power=1.35)
        priors[f"{name}_sharp"] = normalize_prior(score, floor=0.010, power=2.15)
    return priors


def make_configs(q_sources: dict[str, np.ndarray], row_priors: dict[str, np.ndarray]) -> list[RouteWorldConfig]:
    q_keep = [
        "h012",
        "h012posterior",
        "posterior_vector_mid",
        "h041_route_public_q",
        "h041_route_transition_q",
        "h041_route_private_tempered_q",
        "h041_route_public_hardmix",
        "h041_route_memory_contrast_q",
        "h041_e247_phase_q",
    ]
    q_names = [q for q in q_keep if q in q_sources]
    prior_keep = [
        "uniform",
        "h041_public_route",
        "h041_public_route_sharp",
        "h041_transition_exception",
        "h041_transition_exception_sharp",
        "h041_public_x_transition",
        "h041_public_not_private",
        "h041_uncertain_public",
        "h041_support_public",
        "h041_memory_disagree_public",
        "h041_world_public_prior",
        "h041_reliable_transition",
        "h041_private_inverse",
    ]
    prior_names = [p for p in prior_keep if p in row_priors]
    configs: list[RouteWorldConfig] = []
    for q_name in q_names:
        for prior_name in prior_names:
            for size in [55, 75, 95, 125, 155, 190, 230]:
                configs.append(RouteWorldConfig(q_name, prior_name, size, "sample", 18))
                configs.append(RouteWorldConfig(q_name, prior_name, size, "temperature_sample", 12))
                configs.append(RouteWorldConfig(q_name, prior_name, size, "map", 4))
    return configs


def sample_worlds(
    configs: list[RouteWorldConfig],
    q_sources: dict[str, np.ndarray],
    row_priors: dict[str, np.ndarray],
    d0_rows: np.ndarray,
    d1_adj: np.ndarray,
    actual_delta: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    h036 = h036_module("h036_for_h041_sample")
    h036_configs = [
        h036.WorldConfig(cfg.q_source, cfg.row_prior, cfg.subset_size, cfg.label_mode, cfg.particles)
        for cfg in configs
    ]
    return h036.sample_worlds(h036_configs, q_sources, row_priors, d0_rows, d1_adj, actual_delta)


def config_lofo_summary(particle_df: pd.DataFrame, preds: np.ndarray, actual_delta: np.ndarray) -> pd.DataFrame:
    rows = []
    file_count = len(actual_delta)
    pred64 = preds.astype(np.float64)
    for keys, part in particle_df.groupby(["q_source", "row_prior", "subset_size", "label_mode"], sort=False):
        idx = part["particle"].to_numpy(dtype=int)
        if len(idx) == 0:
            continue
        pred = pred64[idx]
        errors = []
        for j in range(file_count):
            train_cols = [c for c in range(file_count) if c != j]
            train_mae = np.mean(np.abs(pred[:, train_cols] - actual_delta[None, train_cols]), axis=1)
            take = np.argsort(train_mae)[: min(24, len(train_mae))]
            temp = max(0.00004, float(np.quantile(train_mae[take], 0.75) - np.min(train_mae[take])) / 3.0)
            w = np.exp(-(train_mae[take] - np.min(train_mae[take])) / temp)
            w = w / w.sum()
            pred_holdout = float(np.sum(w * pred[take, j]))
            errors.append(abs(pred_holdout - float(actual_delta[j])))
        rows.append(
            {
                "q_source": keys[0],
                "row_prior": keys[1],
                "subset_size": int(keys[2]),
                "label_mode": keys[3],
                "particles": len(idx),
                "best_mae": float(part["mae"].min()),
                "median_mae": float(part["mae"].median()),
                "best_spearman": float(part["spearman"].max()),
                "lofo_mae": float(np.mean(errors)),
                "lofo_max_abs": float(np.max(errors)),
            }
        )
    out = pd.DataFrame(rows).sort_values(["lofo_mae", "best_mae"]).reset_index(drop=True)
    out.to_csv(OUT / "h041_world_config_lofo_summary.csv", index=False)
    return out


def posterior_from_route_configs(
    particle_df: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
    h012_prob: np.ndarray,
    config_summary: pd.DataFrame,
    top_config_n: int = 48,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    keep = config_summary.head(min(top_config_n, len(config_summary))).copy()
    key_cols = ["q_source", "row_prior", "subset_size", "label_mode"]
    tagged = particle_df.merge(keep[key_cols + ["lofo_mae", "lofo_max_abs"]], on=key_cols, how="inner")
    if tagged.empty:
        tagged = particle_df.copy()
        tagged["lofo_mae"] = float(config_summary["lofo_mae"].median()) if len(config_summary) else tagged["mae"]
        tagged["lofo_max_abs"] = tagged["max_abs"]
    tagged["actual_mae"] = tagged["mae"]
    tagged["selection_mae"] = (
        0.58 * tagged["mae"].to_numpy(dtype=np.float64)
        + 0.32 * tagged["lofo_mae"].to_numpy(dtype=np.float64)
        + 0.10 * tagged["max_abs"].to_numpy(dtype=np.float64)
    )
    post = tagged.copy()
    post["mae"] = post["selection_mae"]
    h036 = h036_module("h036_for_h041_post")
    q_post, q_cond, row_post, top_worlds = h036.posterior_from_worlds(post, masks, labels, h012_prob, top_n=1800)
    for col in ["actual_mae", "selection_mae", "lofo_mae", "lofo_max_abs"]:
        if col not in top_worlds.columns:
            top_worlds = top_worlds.merge(tagged[["particle", col]], on="particle", how="left")
    top_worlds.to_csv(OUT / "h041_top_worlds.csv", index=False)
    return q_post, q_cond, row_post, top_worlds


def build_posterior_tables(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    q_post: np.ndarray,
    q_cond: np.ndarray,
    row_post: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    h036 = h036_module("h036_for_h041_tables")
    cell, row = h036.build_posterior_tables(sample, h012_prob, q_post, q_cond, row_post)
    route = pd.read_csv(HITL / "h040_discrete_route_assignment_jepa" / "h040_row_route_state.csv").sort_values("row")
    row = row.merge(
        route[
            [
                "row",
                "public_route_score",
                "private_memory_route_score",
                "transition_exception_route_score",
                "route_uncertainty_score",
                "support_count",
                "memory_disagree_rate",
            ]
        ],
        on="row",
        how="left",
    )
    cell = cell.merge(
        route[
            [
                "row",
                "public_route_score",
                "private_memory_route_score",
                "transition_exception_route_score",
                "route_uncertainty_score",
            ]
        ],
        on="row",
        how="left",
    )
    cell.to_csv(OUT / "h041_route_world_posterior_cells.csv", index=False)
    row.to_csv(OUT / "h041_route_world_posterior_rows.csv", index=False)
    return cell, row


def expected_delta_for_prob(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    top_worlds: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
) -> tuple[float, float]:
    h036 = h036_module("h036_for_h041_expected")
    return h036.expected_delta_for_prob(prob, h012_prob, top_worlds, masks, labels)


def generate_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    e247_prob: np.ndarray,
    q_cond: np.ndarray,
    row_post: np.ndarray,
    cell_table: pd.DataFrame,
    top_worlds: pd.DataFrame,
    masks: np.ndarray,
    labels: np.ndarray,
) -> pd.DataFrame:
    h012posterior = pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    route = pd.read_csv(HITL / "h040_discrete_route_assignment_jepa" / "h040_row_route_state.csv").sort_values("row")
    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_cond = logit(q_cond)
    z_post = logit(h012posterior)
    z_world = logit(h036world)
    ray = z_h012 - z_e247
    support = np.abs(ray) > 1.0e-8
    agree_ray = np.sign(z_cond - z_h012) == np.sign(ray)
    row_public = row_post[:, None]
    route_public = route["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    route_exception = route["transition_exception_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]
    flat_score = (
        row_public
        * (0.55 + route_public)
        * np.abs(z_cond - z_h012)
        * (0.70 + 0.30 * agree_ray.astype(float))
        * (1.15 - 0.35 * private)
    ).reshape(-1)
    rows = []
    generated: set[str] = set()

    def materialize(family: str, target_z: np.ndarray, alpha: float, mask: np.ndarray) -> None:
        if not np.any(mask):
            return
        z = z_h012.copy()
        z[mask] = (1.0 - alpha) * z_h012[mask] + alpha * target_z[mask]
        prob = sigmoid(z)
        changed = int(np.sum(np.abs(prob - h012_prob) > 1.0e-7))
        if changed == 0:
            return
        candidate_id = safe_id(f"h041_{family}_a{alpha:g}_c{changed}_{short_hash(prob)}")
        if candidate_id in generated:
            return
        generated.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        delta, dispersion = expected_delta_for_prob(prob, h012_prob, top_worlds, masks, labels)
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": family,
                "alpha": float(alpha),
                "changed_cells_vs_h012": changed,
                "changed_rows_vs_h012": int(np.sum(np.max(np.abs(prob - h012_prob), axis=1) > 1.0e-7)),
                "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - z_h012))),
                "max_abs_logit_move_h012": float(np.max(np.abs(logit(prob) - z_h012))),
                "route_equation_delta_vs_h012": delta,
                "route_equation_delta_iqr": dispersion,
                "h012posterior_delta_vs_h012": weighted_delta(prob, h012_prob, h012posterior, np.abs(z_post - z_h012)),
                "h036world_delta_vs_h012": weighted_delta(prob, h012_prob, h036world, np.abs(z_world - z_h012)),
            }
        )

    n_rows = len(sample)
    flat_order = np.argsort(-flat_score)
    for k in [80, 140, 240, 420, 700, 1050]:
        mask = np.zeros(h012_prob.shape, dtype=bool)
        mask.reshape(-1)[flat_order[: min(k, len(flat_order))]] = True
        for alpha in [0.18, 0.32, 0.50, 0.72]:
            materialize(f"route_celltop_k{k}", z_cond, alpha, mask)

    score_mat = flat_score.reshape(n_rows, len(TARGETS))
    route_row_score = (
        row_post
        * (0.55 + route["public_route_score"].to_numpy(dtype=np.float64))
        * (0.65 + route["transition_exception_route_score"].to_numpy(dtype=np.float64))
        * (1.15 - 0.35 * route["private_memory_route_score"].to_numpy(dtype=np.float64))
    )
    row_order = np.argsort(-route_row_score)
    for r_count in [12, 24, 40, 65, 95]:
        row_mask = np.zeros(n_rows, dtype=bool)
        row_mask[row_order[:r_count]] = True
        for mode in ["all", "support", "agree_support", "top3"]:
            mask = np.zeros(h012_prob.shape, dtype=bool)
            if mode == "all":
                mask[row_mask, :] = True
            elif mode == "support":
                mask[row_mask, :] = support[row_mask, :]
            elif mode == "agree_support":
                mask[row_mask, :] = support[row_mask, :] & agree_ray[row_mask, :]
            else:
                for r in np.where(row_mask)[0]:
                    top_t = np.argsort(-score_mat[r])[:3]
                    mask[r, top_t] = True
            for alpha in [0.22, 0.40, 0.62]:
                materialize(f"route_rows_r{r_count}_{mode}", z_cond, alpha, mask)

    # Phase-preserving alternatives: the route posterior is used only to choose
    # cells, while the target stays closer to H012's known successful phase.
    phase_target = 0.60 * z_cond + 0.25 * z_post + 0.15 * z_world
    for k in [120, 260, 520, 900]:
        mask = np.zeros(h012_prob.shape, dtype=bool)
        chosen = flat_order[: min(k, len(flat_order))]
        mask.reshape(-1)[chosen] = True
        mask &= support & agree_ray
        for alpha in [0.20, 0.36, 0.55]:
            materialize(f"phase_preserve_support_k{k}", phase_target, alpha, mask)

    scores = pd.DataFrame(rows)
    if scores.empty:
        return scores
    scores["pre_h024_proxy_score"] = (
        scores["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        +0.65 * scores["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        +0.55 * scores["h036world_delta_vs_h012"].rank(method="average", pct=True)
        +0.15 * scores["mean_abs_logit_move_h012"].rank(method="average", pct=True)
    )
    scores = scores.nsmallest(min(280, len(scores)), "pre_h024_proxy_score").reset_index(drop=True)
    scores.to_csv(OUT / "h041_generated_candidates.csv", index=False)
    return scores


def score_candidates(candidate_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    h036 = h036_module("h036_for_h041_scores")
    if candidate_scores.empty:
        return candidate_scores, pd.DataFrame()
    h024_features, h024_models, h024_preds = h036.h024_score_candidates(candidate_scores)
    h024_features.to_csv(OUT / "h041_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h041_h024_model_scores.csv", index=False)
    h024_preds.to_csv(OUT / "h041_h024_candidate_predictions.csv", index=False)
    if not h024_preds.empty:
        candidate_scores = candidate_scores.merge(h024_preds, on="resolved_path", how="left")
    h025_scores, h025_cells = h036.h025_score_candidates(candidate_scores)
    h025_scores.to_csv(OUT / "h041_h025_candidate_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h041_h025_top_cells.csv", index=False)
    if not h025_scores.empty:
        keep = [
            "file",
            "h025_score",
            "pred_gain_top1200_sum",
            "pred_gain_mean_moved",
            "pred_positive_rate_moved",
            "ood_abs_delta_rate",
        ]
        candidate_scores = candidate_scores.merge(h025_scores[[c for c in keep if c in h025_scores]], on="file", how="left")

    margin = candidate_scores.get(
        "pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=candidate_scores.index)
    ).fillna(0.02)
    support = candidate_scores.get(
        "pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=candidate_scores.index)
    ).fillna(0.0)
    h025 = candidate_scores.get("h025_score", pd.Series(1.0, index=candidate_scores.index)).fillna(1.0)
    candidate_scores["h041_score"] = (
        candidate_scores["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        +0.75 * candidate_scores["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        +0.60 * margin.rank(method="average", pct=True)
        +0.35 * h025.rank(method="average", pct=True)
        -0.28 * support
    )
    candidate_scores = candidate_scores.sort_values(["h041_score", "route_equation_delta_vs_h012"]).reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h041_candidate_scores.csv", index=False)
    return candidate_scores, h025_scores


def rowperm_for_selected(candidate_scores: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame()
    h036 = h036_module("h036_for_h041_rowperm")
    selected = str(candidate_scores.iloc[0]["resolved_path"])
    rowperm = h036.run_rowperm_stress(selected)
    rowperm.to_csv(OUT / "h041_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decision_frame(candidate_scores: pd.DataFrame, config_summary: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no materialized candidate"}])
    selected = candidate_scores.iloc[0]
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))
    route_best = config_summary[config_summary["row_prior"].astype(str).str.startswith("h041")]["lofo_mae"].min()
    uniform_best = config_summary[config_summary["row_prior"].astype(str).eq("uniform")]["lofo_mae"].min()
    route_lofo_gain = float(uniform_best - route_best) if np.isfinite(route_best) and np.isfinite(uniform_best) else np.nan
    eq_delta = float(selected.get("route_equation_delta_vs_h012", np.nan))
    post_delta = float(selected.get("h012posterior_delta_vs_h012", np.nan))
    margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    h025 = float(selected.get("h025_score", np.nan))
    promote = bool(
        np.isfinite(eq_delta)
        and eq_delta < -0.00035
        and np.isfinite(post_delta)
        and post_delta < -0.00008
        and np.isfinite(margin)
        and margin < -0.00010
        and np.isfinite(support)
        and support >= 0.55
        and np.isfinite(h025)
        and h025 < 0.0
        and rowperm_p <= 0.35
    )
    reasons = []
    if not np.isfinite(eq_delta) or eq_delta >= -0.00035:
        reasons.append("weak route-equation gain")
    if not np.isfinite(post_delta) or post_delta >= -0.00008:
        reasons.append("weak H012 posterior gain")
    if not np.isfinite(margin) or margin >= -0.00010:
        reasons.append("H024 pre-H012 does not prefer over H012")
    if not np.isfinite(support) or support < 0.55:
        reasons.append("H024 support below 55%")
    if not np.isfinite(h025) or h025 >= 0.0:
        reasons.append("H025 train action-health not positive")
    if rowperm_p > 0.35:
        reasons.append("row permutation stress weak")
    return pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "family": selected["family"],
                "route_equation_delta_vs_h012": eq_delta,
                "h012posterior_delta_vs_h012": post_delta,
                "pre_h012_h024_margin_vs_h012_median": margin,
                "pre_h012_h024_support_better_than_h012": support,
                "h025_score": h025,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "route_lofo_gain_vs_uniform": route_lofo_gain,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(
    known: pd.DataFrame,
    config_summary: pd.DataFrame,
    top_worlds: pd.DataFrame,
    row_table: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    route_configs = config_summary[config_summary["row_prior"].astype(str).str.startswith("h041")]
    uniform_configs = config_summary[config_summary["row_prior"].astype(str).eq("uniform")]
    route_best = float(route_configs["lofo_mae"].min()) if len(route_configs) else np.nan
    uniform_best = float(uniform_configs["lofo_mae"].min()) if len(uniform_configs) else np.nan
    lines = []
    lines.append("# H041 Route-Prior Public/Private Equation Solver HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "Can H040 route state help when used inside hidden public-subset equation inference, "
        "rather than as a post-hoc edit gate?\n"
    )
    lines.append("## Public-equation fit\n")
    lines.append(f"- known public sensors used: `{len(known)}`\n")
    lines.append(f"- best route-prior LOFO MAE: `{route_best:.9f}`\n")
    lines.append(f"- best uniform LOFO MAE: `{uniform_best:.9f}`\n")
    if np.isfinite(route_best) and np.isfinite(uniform_best):
        lines.append(f"- route LOFO gain vs uniform: `{uniform_best - route_best:.9f}`\n")
    lines.append("\nTop config families:\n")
    lines.append(md_table(config_summary.head(16), 16))
    lines.append("\n\nTop worlds:\n")
    keep_world = [
        c
        for c in [
            "particle",
            "q_source",
            "row_prior",
            "subset_size",
            "label_mode",
            "actual_mae",
            "selection_mae",
            "lofo_mae",
            "spearman",
            "posterior_weight",
        ]
        if c in top_worlds.columns
    ]
    lines.append(md_table(top_worlds[keep_world].head(14), 14))
    lines.append("\n\nTop posterior rows:\n")
    keep_row = [
        "row",
        "subject_id",
        "sleep_date",
        "world_public_prob",
        "mean_cell_world_score",
        "public_route_score",
        "transition_exception_route_score",
        "private_memory_route_score",
        "support_count",
        "memory_disagree_rate",
    ]
    lines.append(md_table(row_table[[c for c in keep_row if c in row_table.columns]].head(14), 14))
    lines.append("\n\nCandidate ranking:\n")
    keep_cand = [
        c
        for c in [
            "candidate_id",
            "family",
            "alpha",
            "changed_cells_vs_h012",
            "route_equation_delta_vs_h012",
            "h012posterior_delta_vs_h012",
            "h036world_delta_vs_h012",
            "pre_h012_h024_margin_vs_h012_median",
            "pre_h012_h024_support_better_than_h012",
            "h025_score",
            "pred_gain_top1200_sum",
            "h041_score",
        ]
        if c in candidate_scores.columns
    ]
    lines.append(md_table(candidate_scores[keep_cand].head(18), 18) if keep_cand else "_empty_")
    lines.append("\n\nDecision:\n")
    lines.append(md_table(decision, 1))
    lines.append(
        "\n\n## Interpretation\n"
        "- If route LOFO improves over uniform but candidates fail H024/H025, route is a real public-subset prior but not enough to decode actions.\n"
        "- If route LOFO does not improve, H040's route latent is only descriptive and should not guide future equation solvers.\n"
        "- Promotion requires both equation-level evidence and action-health survival because H012 is a locked public-equation phase point.\n"
    )
    (OUT / "h041_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    h036 = h036_module("h036_for_h041_main")
    known, sample, h012_prob, pred_by_file = h036.load_system()
    e247_prob = load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    files, d0_rows, d1_adj, actual_delta = h036.build_delta_tensors(known, pred_by_file, h012_prob)
    q_sources = build_route_q_sources(sample, h012_prob, e247_prob)
    row_priors = build_route_row_priors(sample)
    configs = make_configs(q_sources, row_priors)
    pd.DataFrame([cfg.__dict__ for cfg in configs]).to_csv(OUT / "h041_world_configs.csv", index=False)

    particle_df, masks, labels, preds = sample_worlds(configs, q_sources, row_priors, d0_rows, d1_adj, actual_delta)
    particle_df.to_csv(OUT / "h041_world_particles.csv", index=False)
    pred_df = pd.DataFrame(preds, columns=[f"pred_delta_{Path(f).stem}" for f in files])
    pred_df.insert(0, "particle", np.arange(len(pred_df)))
    pred_df.to_csv(OUT / "h041_world_predicted_deltas.csv", index=False)

    config_summary = config_lofo_summary(particle_df, preds, actual_delta)
    q_post, q_cond, row_post, top_worlds = posterior_from_route_configs(
        particle_df, masks, labels, h012_prob, config_summary, top_config_n=48
    )
    cell_table, row_table = build_posterior_tables(sample, h012_prob, q_post, q_cond, row_post)
    candidate_scores = generate_candidates(sample, h012_prob, e247_prob, q_cond, row_post, cell_table, top_worlds, masks, labels)
    candidate_scores, _h025_scores = score_candidates(candidate_scores)
    rowperm = rowperm_for_selected(candidate_scores)
    decision = decision_frame(candidate_scores, config_summary, rowperm)
    decision.to_csv(OUT / "h041_decision.csv", index=False)
    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copy2(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h041_decision.csv", index=False)
    known.to_csv(OUT / "h041_known_public_sensors.csv", index=False)
    write_report(known, config_summary, top_worlds, row_table, candidate_scores, decision)
    if not candidate_scores.empty:
        print(f"H041 selected: {candidate_scores.iloc[0]['candidate_id']}")
        print(f"H041 selected equation delta: {float(candidate_scores.iloc[0]['route_equation_delta_vs_h012']):.9f}")
        print(f"H041 decision: {decision.iloc[0]['decision']}")
    else:
        print("H041 generated no candidates")


if __name__ == "__main__":
    main()
