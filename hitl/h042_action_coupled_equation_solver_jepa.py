#!/usr/bin/env python3
"""H042: action-coupled public/private equation solver HS-JEPA.

H041 showed that H040 route state improves hidden public-world inference, but
posterior-first materialization still leaves the H012 action basin.

H042 changes the target again:

    context = known public LB interventions + human-state route atoms
    target  = hidden public/private action response, not only hidden labels
    action  = choose upload probability moves as coefficients on route atoms

If this works, the action decoder should predict a candidate below H012 and
H024/H025 should agree that the action stays healthy.  If it fails, the next
decoder must be more than a ridge over route-action coordinates.
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
OUT = HITL / "h042_action_coupled_equation_solver_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_LB = 0.5681234831


@dataclass(frozen=True)
class ActionAtom:
    name: str
    group: str
    direction: np.ndarray
    mask: np.ndarray
    strength: float


@dataclass(frozen=True)
class RidgeFit:
    feature_set: str
    alpha: float
    cols: list[str]
    intercept: float
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray
    loo_mae: float
    loo_rmse: float
    loo_spearman: float
    loo_pair_acc: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def h036_module(name: str = "h036_for_h042") -> object:
    return import_module(HITL / "h036_global_public_world_solver_jepa.py", name)


def h041_module(name: str = "h041_for_h042") -> object:
    return import_module(HITL / "h041_route_prior_equation_solver_jepa.py", name)


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


def safe_id(text: str, limit: int = 96) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


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


def pivot_cells(path: Path, value_col: str, sample: pd.DataFrame) -> np.ndarray:
    h036 = h036_module("h036_for_h042_pivot")
    return h036.pivot_cell_table(path, value_col, sample)


def weighted_delta(prob: np.ndarray, base: np.ndarray, q: np.ndarray, weight: np.ndarray) -> float:
    w = np.asarray(weight, dtype=np.float64)
    if w.ndim == 1:
        w = np.repeat(w[:, None], len(TARGETS), axis=1)
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)
    w = np.clip(w, 0.0, None)
    if float(w.sum()) <= 1.0e-12:
        w = np.ones_like(base)
    return float(np.sum(w * (bce(prob, q) - bce(base, q))) / np.sum(w))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy(dtype=np.float64)
    rb = pd.Series(b).rank(method="average").to_numpy(dtype=np.float64)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def pairwise_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    total = 0
    ok = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1.0e-12:
                continue
            total += 1
            ok += int(np.sign(dy) == np.sign(dp))
    return float(ok / total) if total else float("nan")


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    mu = np.nanmean(x, axis=0)
    sd = np.nanstd(x, axis=0)
    sd = np.where(sd < 1.0e-12, 1.0, sd)
    xz = np.nan_to_num((x - mu) / sd)
    xa = np.column_stack([np.ones(len(xz)), xz])
    penalty = np.eye(xa.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    beta_all = np.linalg.pinv(xa.T @ xa + penalty) @ xa.T @ y
    return float(beta_all[0]), beta_all[1:], mu, sd


def predict_ridge(x: np.ndarray, fit: RidgeFit) -> np.ndarray:
    xz = np.nan_to_num((x - fit.mu) / fit.sd)
    return fit.intercept + xz @ fit.beta


def config_lofo_summary(particle_df: pd.DataFrame, preds: np.ndarray, actual_delta: np.ndarray) -> pd.DataFrame:
    rows = []
    file_count = len(actual_delta)
    pred64 = preds.astype(np.float64)
    for keys, part in particle_df.groupby(["q_source", "row_prior", "subset_size", "label_mode"], sort=False):
        idx = part["particle"].to_numpy(dtype=int)
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
    out.to_csv(OUT / "h042_world_config_lofo_summary.csv", index=False)
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
    h036 = h036_module("h036_for_h042_post")
    q_post, q_cond, row_post, top_worlds = h036.posterior_from_worlds(post, masks, labels, h012_prob, top_n=1800)
    top_worlds.to_csv(OUT / "h042_top_worlds.csv", index=False)
    return q_post, q_cond, row_post, top_worlds


def per_world_deltas(prob: np.ndarray, h012_prob: np.ndarray, top: pd.DataFrame, masks: np.ndarray, labels: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    h = clip_prob(h012_prob)
    idx = top["particle"].to_numpy(dtype=int)
    mask_top = masks[idx].astype(np.float64)
    label_top = labels[idx].astype(np.float64)
    d0 = (-np.log(1.0 - p) + np.log(1.0 - h)).sum(axis=1)
    adj = logit(h) - logit(p)
    denom = mask_top.sum(axis=1) * len(TARGETS)
    base = mask_top @ d0
    add = np.einsum("wr,wrt,rt->w", mask_top, label_top, adj, optimize=True)
    return (base + add) / denom


def expected_delta_for_prob(
    prob: np.ndarray, h012_prob: np.ndarray, top: pd.DataFrame, masks: np.ndarray, labels: np.ndarray
) -> tuple[float, float]:
    per_world = per_world_deltas(prob, h012_prob, top, masks, labels)
    w = top["posterior_weight"].to_numpy(dtype=np.float64)
    return float(np.sum(w * per_world)), float(np.quantile(per_world, 0.90) - np.quantile(per_world, 0.10))


def rebuild_route_world():
    h036 = h036_module("h036_for_h042_system")
    h041 = h041_module("h041_for_h042_system")
    known, sample, h012_prob, pred_by_file = h036.load_system()
    e247_prob = h036.load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)
    files, d0_rows, d1_adj, actual_delta = h036.build_delta_tensors(known, pred_by_file, h012_prob)
    q_sources = h041.build_route_q_sources(sample, h012_prob, e247_prob)
    row_priors = h041.build_route_row_priors(sample)
    configs = h041.make_configs(q_sources, row_priors)
    pd.DataFrame([c.__dict__ for c in configs]).to_csv(OUT / "h042_world_configs.csv", index=False)
    particle_df, masks, labels, preds = h041.sample_worlds(configs, q_sources, row_priors, d0_rows, d1_adj, actual_delta)
    config_summary = config_lofo_summary(particle_df, preds, actual_delta)
    q_post, q_cond, row_post, top_worlds = posterior_from_route_configs(
        particle_df, masks, labels, h012_prob, config_summary
    )
    route = pd.read_csv(HITL / "h040_discrete_route_assignment_jepa" / "h040_row_route_state.csv").sort_values("row")
    h036_cell, h036_row = h036.build_posterior_tables(sample, h012_prob, q_post, q_cond, row_post)
    h036_cell = h036_cell.merge(
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
    h036_row = h036_row.merge(
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
    h036_cell.to_csv(OUT / "h042_route_world_posterior_cells.csv", index=False)
    h036_row.to_csv(OUT / "h042_route_world_posterior_rows.csv", index=False)
    return {
        "known": known,
        "sample": sample,
        "h012_prob": h012_prob,
        "e247_prob": e247_prob,
        "pred_by_file": pred_by_file,
        "files": files,
        "actual_delta": actual_delta,
        "q_cond": q_cond,
        "q_post": q_post,
        "row_post": row_post,
        "top_worlds": top_worlds,
        "masks": masks,
        "labels": labels,
        "route": route.reset_index(drop=True),
        "config_summary": config_summary,
    }


def top_mask(score: np.ndarray, k: int, allowed: np.ndarray | None = None) -> np.ndarray:
    s = np.nan_to_num(np.asarray(score, dtype=np.float64), nan=-np.inf)
    if allowed is None:
        allowed = np.ones_like(s, dtype=bool)
    flat_s = s.reshape(-1).copy()
    flat_allowed = allowed.reshape(-1)
    flat_s[~flat_allowed] = -np.inf
    valid = np.where(np.isfinite(flat_s))[0]
    if len(valid) == 0:
        return np.zeros_like(s, dtype=bool)
    take = valid[np.argsort(-flat_s[valid])[: min(k, len(valid))]]
    out = np.zeros_like(flat_allowed, dtype=bool)
    out[take] = True
    return out.reshape(s.shape)


def build_atoms(rt: dict[str, object]) -> list[ActionAtom]:
    sample = rt["sample"]
    h012_prob = rt["h012_prob"]
    e247_prob = rt["e247_prob"]
    q_cond = rt["q_cond"]
    route = rt["route"]
    n_rows = len(sample)
    h012posterior = pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    memory = pivot_cells(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv", "memory_prob_full", sample)
    h038_cells = pd.read_csv(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv").sort_values(
        ["row", "target_i"]
    )
    memory_disagree = h038_cells["memory_disagrees_h012"].to_numpy(dtype=bool).reshape(n_rows, len(TARGETS))
    world_opposes_memory = h038_cells["world_opposes_memory"].to_numpy(dtype=bool).reshape(n_rows, len(TARGETS))

    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_cond = logit(q_cond)
    z_post = logit(h012posterior)
    z_world = logit(h036world)
    z_memory = logit(memory)
    z_phase = 0.52 * z_cond + 0.24 * z_post + 0.24 * z_world
    z_public = 0.62 * z_cond + 0.25 * z_post + 0.13 * z_h012
    ray = z_h012 - z_e247
    support = np.abs(ray) > 1.0e-8
    agree_ray = np.sign(z_cond - z_h012) == np.sign(ray)
    public = route["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]
    transition = route["transition_exception_route_score"].to_numpy(dtype=np.float64)[:, None]
    row_public = np.asarray(rt["row_post"], dtype=np.float64)[:, None]
    world_abs = np.abs(z_cond - z_h012)
    public_score = row_public * (0.45 + public) * world_abs * (1.15 - 0.45 * private)
    phase_score = public_score * support * (0.75 + 0.25 * agree_ray)
    exception_score = public_score * (0.5 + transition) * (memory_disagree | world_opposes_memory)
    private_score = (0.35 + private) * support * np.abs(z_memory - z_h012)

    atoms: list[ActionAtom] = []

    def add_atom(name: str, group: str, target_z: np.ndarray, mask: np.ndarray) -> None:
        direction = np.zeros_like(z_h012)
        direction[mask] = target_z[mask] - z_h012[mask]
        strength = float(np.linalg.norm(direction.reshape(-1)))
        if strength <= 1.0e-8:
            return
        atoms.append(ActionAtom(name=name, group=group, direction=direction, mask=mask.copy(), strength=strength))

    for k in [120, 240, 420, 700]:
        add_atom(f"public_cell_k{k}", "public", z_public, top_mask(public_score, k))
    for k in [120, 260, 520]:
        add_atom(f"phase_support_k{k}", "phase", z_phase, top_mask(phase_score, k, support & agree_ray))
    for k in [90, 180, 340]:
        add_atom(f"exception_world_k{k}", "exception", z_world, top_mask(exception_score, k, support & (memory_disagree | world_opposes_memory)))
    for k in [120, 260, 520]:
        add_atom(f"private_memory_k{k}", "private", z_memory, top_mask(private_score, k, support))
        add_atom(f"private_rollback_k{k}", "private", z_e247, top_mask(private_score, k, support))

    score_mat = public_score.reshape(n_rows, len(TARGETS))
    row_score = (
        np.asarray(rt["row_post"], dtype=np.float64)
        * (0.5 + route["public_route_score"].to_numpy(dtype=np.float64))
        * (0.6 + route["transition_exception_route_score"].to_numpy(dtype=np.float64))
        * (1.15 - 0.35 * route["private_memory_route_score"].to_numpy(dtype=np.float64))
    )
    for r_count in [12, 24, 40, 70]:
        row_mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
        rows = np.argsort(-row_score)[:r_count]
        row_mask[rows, :] = True
        add_atom(f"route_row_all_r{r_count}", "row", z_phase, row_mask)
        top3 = np.zeros_like(row_mask)
        for r in rows:
            top3[r, np.argsort(-score_mat[r])[:3]] = True
        add_atom(f"route_row_top3_r{r_count}", "row", z_phase, top3)

    for target in ["Q2", "S1", "S3", "S4"]:
        t_i = TARGETS.index(target)
        allowed = np.zeros_like(support)
        allowed[:, t_i] = True
        for k in [45, 90, 150]:
            add_atom(f"target_{target}_phase_k{k}", f"target_{target}", z_phase, top_mask(public_score, k, allowed & support))

    atom_frame = pd.DataFrame(
        [{"name": a.name, "group": a.group, "changed_cells": int(a.mask.sum()), "strength": a.strength} for a in atoms]
    )
    atom_frame.to_csv(OUT / "h042_action_atoms.csv", index=False)
    return atoms


def action_features(
    prob: np.ndarray,
    rt: dict[str, object],
    atoms: list[ActionAtom],
    file_name: str,
    source: str,
) -> dict[str, object]:
    h012_prob = rt["h012_prob"]
    e247_prob = rt["e247_prob"]
    sample = rt["sample"]
    q_cond = rt["q_cond"]
    h012posterior = pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    memory = pivot_cells(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv", "memory_prob_full", sample)
    route = rt["route"]
    z_h012 = logit(h012_prob)
    dz = logit(prob) - z_h012
    flat = dz.reshape(-1)
    public = route["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]
    transition = route["transition_exception_route_score"].to_numpy(dtype=np.float64)[:, None]
    row_public = np.asarray(rt["row_post"], dtype=np.float64)[:, None]
    support = np.abs(z_h012 - logit(e247_prob)) > 1.0e-8
    h038_cells = pd.read_csv(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv").sort_values(
        ["row", "target_i"]
    )
    memory_disagree = h038_cells["memory_disagrees_h012"].to_numpy(dtype=bool).reshape(h012_prob.shape)
    out: dict[str, object] = {
        "file": file_name,
        "source": source,
        "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
        "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(dz))),
        "max_abs_logit_move_h012": float(np.max(np.abs(dz))),
        "changed_cells_h012_1e6": int(np.sum(np.abs(prob - h012_prob) > 1.0e-6)),
        "changed_rows_h012_1e6": int(np.sum(np.max(np.abs(prob - h012_prob), axis=1) > 1.0e-6)),
        "route_world_delta": expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])[0],
        "route_world_dispersion": expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])[1],
        "h012posterior_delta": weighted_delta(prob, h012_prob, h012posterior, np.abs(logit(h012posterior) - z_h012)),
        "h036world_delta": weighted_delta(prob, h012_prob, h036world, np.abs(logit(h036world) - z_h012)),
        "memory_delta": weighted_delta(prob, h012_prob, memory, np.abs(logit(memory) - z_h012)),
        "public_weight_abs_move": float(np.mean(np.abs(dz) * public)),
        "private_weight_abs_move": float(np.mean(np.abs(dz) * private)),
        "transition_weight_abs_move": float(np.mean(np.abs(dz) * transition)),
        "row_public_weight_abs_move": float(np.mean(np.abs(dz) * row_public)),
        "support_abs_move": float(np.mean(np.abs(dz[support]))) if np.any(support) else 0.0,
        "memory_disagree_abs_move": float(np.mean(np.abs(dz[memory_disagree]))) if np.any(memory_disagree) else 0.0,
        "public_private_balance": float(np.mean(np.abs(dz) * public) - np.mean(np.abs(dz) * private)),
    }
    world_dir = (logit(q_cond) - z_h012).reshape(-1)
    ray = (z_h012 - logit(e247_prob)).reshape(-1)
    for name, vec in [("world", world_dir), ("h012_ray", ray)]:
        denom = float(np.linalg.norm(vec) * np.linalg.norm(flat) + 1.0e-12)
        out[f"cos_{name}"] = float(np.dot(flat, vec) / denom)
        out[f"proj_{name}"] = float(np.dot(flat, vec) / (np.dot(vec, vec) + 1.0e-12))
    for target in TARGETS:
        t_i = TARGETS.index(target)
        out[f"mean_abs_logit_move_{target}"] = float(np.mean(np.abs(dz[:, t_i])))
        out[f"mean_signed_logit_move_{target}"] = float(np.mean(dz[:, t_i]))
        out[f"changed_cells_{target}"] = int(np.sum(np.abs(prob[:, t_i] - h012_prob[:, t_i]) > 1.0e-6))
    for atom in atoms:
        avec = atom.direction.reshape(-1)
        denom = float(np.dot(avec, avec) + 1.0e-12)
        coord = float(np.dot(flat, avec) / denom)
        cos = float(np.dot(flat, avec) / (np.linalg.norm(flat) * np.linalg.norm(avec) + 1.0e-12))
        out[f"coord_{atom.name}"] = coord
        out[f"cos_{atom.name}"] = cos
    return out


def build_action_feature_table(rt: dict[str, object], atoms: list[ActionAtom]) -> pd.DataFrame:
    rows = []
    for file_name, prob in rt["pred_by_file"].items():
        rows.append(action_features(prob, rt, atoms, file_name, "known_public"))
    out = pd.DataFrame(rows)
    out = out.merge(rt["known"][["file", "public_lb"]], on="file", how="left")
    out["delta_vs_h012"] = out["public_lb"] - H012_LB
    out.to_csv(OUT / "h042_known_action_features.csv", index=False)
    return out


def feature_sets(cols: list[str]) -> dict[str, list[str]]:
    coord_cols = [c for c in cols if c.startswith("coord_")]
    cos_cols = [c for c in cols if c.startswith("cos_")]
    compact = [c for c in cols if not c.startswith("coord_") and not c.startswith("cos_")]
    world = [c for c in compact if "delta" in c or "world" in c or "public" in c or "private" in c or "transition" in c]
    return {
        "compact": compact,
        "coords": coord_cols,
        "coords_plus_world": coord_cols + world,
        "coords_cos_compact": coord_cols + cos_cols + compact,
    }


def evaluate_action_decoders(known_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    blocked = {"file", "source", "public_lb", "delta_vs_h012"}
    numeric_cols = [
        c
        for c in known_features.columns
        if c not in blocked and pd.api.types.is_numeric_dtype(known_features[c]) and known_features[c].nunique(dropna=True) > 1
    ]
    y = known_features["delta_vs_h012"].to_numpy(dtype=np.float64)
    sets = feature_sets(numeric_cols)
    rows = []
    pred_rows = []
    for set_name, cols in sets.items():
        cols = [c for c in cols if c in numeric_cols]
        if len(cols) < 3:
            continue
        x = known_features[cols].to_numpy(dtype=np.float64)
        for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
            loo = np.zeros(len(y), dtype=np.float64)
            for i in range(len(y)):
                train = np.ones(len(y), dtype=bool)
                train[i] = False
                intercept, beta, mu, sd = fit_ridge(x[train], y[train], alpha)
                fit = RidgeFit(set_name, alpha, cols, intercept, beta, mu, sd, np.nan, np.nan, np.nan, np.nan)
                loo[i] = predict_ridge(x[[i]], fit)[0]
            fit_intercept, fit_beta, fit_mu, fit_sd = fit_ridge(x, y, alpha)
            rows.append(
                {
                    "feature_set": set_name,
                    "alpha": alpha,
                    "n_features": len(cols),
                    "loo_mae": float(np.mean(np.abs(loo - y))),
                    "loo_rmse": float(np.sqrt(np.mean((loo - y) ** 2))),
                    "loo_spearman": spearman(y, loo),
                    "loo_pair_acc": pairwise_accuracy(y, loo),
                }
            )
            for file_name, actual, pred in zip(known_features["file"].astype(str), y, loo):
                pred_rows.append(
                    {
                        "file": file_name,
                        "feature_set": set_name,
                        "alpha": alpha,
                        "actual_delta": float(actual),
                        "loo_pred_delta": float(pred),
                        "loo_abs_error": float(abs(pred - actual)),
                    }
                )
    score = pd.DataFrame(rows).sort_values(["loo_mae", "loo_rmse"]).reset_index(drop=True)
    pred = pd.DataFrame(pred_rows)
    score.to_csv(OUT / "h042_action_decoder_scores.csv", index=False)
    pred.to_csv(OUT / "h042_action_decoder_loo_predictions.csv", index=False)
    null = action_decoder_permutation_null(known_features, numeric_cols, score["loo_mae"].min() if len(score) else np.nan)
    null.to_csv(OUT / "h042_action_decoder_permutation_null.csv", index=False)
    return score, pred


def best_loo_for_y(known_features: pd.DataFrame, numeric_cols: list[str], y: np.ndarray) -> float:
    sets = feature_sets(numeric_cols)
    best = np.inf
    for set_name, cols in sets.items():
        cols = [c for c in cols if c in numeric_cols]
        if len(cols) < 3:
            continue
        x = known_features[cols].to_numpy(dtype=np.float64)
        for alpha in [0.1, 1.0, 10.0, 100.0]:
            loo = np.zeros(len(y), dtype=np.float64)
            for i in range(len(y)):
                train = np.ones(len(y), dtype=bool)
                train[i] = False
                intercept, beta, mu, sd = fit_ridge(x[train], y[train], alpha)
                fit = RidgeFit(set_name, alpha, cols, intercept, beta, mu, sd, np.nan, np.nan, np.nan, np.nan)
                loo[i] = predict_ridge(x[[i]], fit)[0]
            best = min(best, float(np.mean(np.abs(loo - y))))
    return best


def action_decoder_permutation_null(known_features: pd.DataFrame, numeric_cols: list[str], real_best: float) -> pd.DataFrame:
    rng = np.random.default_rng(2042042)
    y = known_features["delta_vs_h012"].to_numpy(dtype=np.float64)
    rows = []
    for i in range(120):
        perm_y = rng.permutation(y)
        rows.append({"perm": i, "best_null_loo_mae": best_loo_for_y(known_features, numeric_cols, perm_y)})
    out = pd.DataFrame(rows)
    out["real_best_loo_mae"] = real_best
    out["perm_le_real"] = out["best_null_loo_mae"] <= real_best
    return out


def predict_candidates_with_action_decoder(
    known_features: pd.DataFrame, candidate_features: pd.DataFrame, decoder_scores: pd.DataFrame
) -> pd.DataFrame:
    blocked = {"file", "source", "public_lb", "delta_vs_h012"}
    numeric_cols = [
        c
        for c in known_features.columns
        if c not in blocked and pd.api.types.is_numeric_dtype(known_features[c]) and known_features[c].nunique(dropna=True) > 1
    ]
    sets = feature_sets(numeric_cols)
    top_models = decoder_scores.sort_values(["loo_mae", "loo_rmse"]).head(12)
    pred_rows = []
    h012_row = known_features[known_features["file"] == H012]
    pre_known = known_features[known_features["file"] != H012].copy()
    for m in top_models.to_dict("records"):
        cols = [c for c in sets[str(m["feature_set"])] if c in numeric_cols]
        if len(cols) < 3:
            continue
        alpha = float(m["alpha"])
        for tag, train_df in [("full_known", known_features), ("pre_h012", pre_known)]:
            x_train = train_df[cols].to_numpy(dtype=np.float64)
            y_train = train_df["delta_vs_h012"].to_numpy(dtype=np.float64)
            intercept, beta, mu, sd = fit_ridge(x_train, y_train, alpha)
            fit = RidgeFit(str(m["feature_set"]), alpha, cols, intercept, beta, mu, sd, np.nan, np.nan, np.nan, np.nan)
            cand_pred = predict_ridge(candidate_features[cols].to_numpy(dtype=np.float64), fit)
            h012_pred = (
                float(predict_ridge(h012_row[cols].to_numpy(dtype=np.float64), fit)[0]) if len(h012_row) else 0.0
            )
            for file_name, pred in zip(candidate_features["file"].astype(str), cand_pred):
                pred_rows.append(
                    {
                        "file": file_name,
                        "model_tag": tag,
                        "feature_set": str(m["feature_set"]),
                        "alpha": alpha,
                        "pred_delta": float(pred),
                        "pred_h012_delta": h012_pred,
                        "pred_margin_vs_h012": float(pred - h012_pred),
                    }
                )
    pred = pd.DataFrame(pred_rows)
    if pred.empty:
        return pd.DataFrame()
    agg = (
        pred.groupby(["file", "model_tag"])
        .agg(
            action_pred_delta_median=("pred_delta", "median"),
            action_pred_delta_p10=("pred_delta", lambda x: float(np.quantile(x, 0.10))),
            action_pred_delta_p90=("pred_delta", lambda x: float(np.quantile(x, 0.90))),
            action_margin_vs_h012_median=("pred_margin_vs_h012", "median"),
            action_margin_vs_h012_p10=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.10))),
            action_margin_vs_h012_p90=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.90))),
            action_support_better_than_h012=("pred_margin_vs_h012", lambda x: float(np.mean(np.asarray(x) < 0.0))),
            action_model_count=("pred_margin_vs_h012", "size"),
        )
        .reset_index()
    )
    parts = []
    for tag in ["full_known", "pre_h012"]:
        part = agg[agg["model_tag"] == tag].drop(columns=["model_tag"]).copy()
        parts.append(part.rename(columns={c: f"{tag}_{c}" for c in part.columns if c != "file"}))
    wide = parts[0]
    for part in parts[1:]:
        wide = wide.merge(part, on="file", how="outer")
    return wide


def generate_candidates(rt: dict[str, object], atoms: list[ActionAtom]) -> pd.DataFrame:
    sample = rt["sample"]
    h012_prob = rt["h012_prob"]
    z_h012 = logit(h012_prob)
    generated: set[str] = set()
    rows: list[dict[str, object]] = []

    def materialize(family: str, components: list[tuple[ActionAtom, float]]) -> None:
        z = z_h012.copy()
        for atom, coef in components:
            z += coef * atom.direction
        move = np.clip(z - z_h012, -3.2, 3.2)
        prob = sigmoid(z_h012 + move)
        changed = int(np.sum(np.abs(prob - h012_prob) > 1.0e-7))
        if changed == 0:
            return
        candidate_id = safe_id(f"h042_{family}_c{changed}_{short_hash(prob)}")
        if candidate_id in generated:
            return
        generated.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        route_delta, route_disp = expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])
        h012posterior = pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
        h036world = pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": family,
                "components": "+".join(f"{a.name}:{coef:g}" for a, coef in components),
                "component_count": len(components),
                "changed_cells_vs_h012": changed,
                "changed_rows_vs_h012": int(np.sum(np.max(np.abs(prob - h012_prob), axis=1) > 1.0e-7)),
                "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                "mean_abs_logit_move_h012": float(np.mean(np.abs(move))),
                "max_abs_logit_move_h012": float(np.max(np.abs(move))),
                "route_equation_delta_vs_h012": route_delta,
                "route_equation_delta_iqr": route_disp,
                "h012posterior_delta_vs_h012": weighted_delta(
                    prob, h012_prob, h012posterior, np.abs(logit(h012posterior) - z_h012)
                ),
                "h036world_delta_vs_h012": weighted_delta(prob, h012_prob, h036world, np.abs(logit(h036world) - z_h012)),
            }
        )

    single_scales = [0.08, 0.14, 0.22, 0.34, 0.50]
    for atom in atoms:
        for scale in single_scales:
            materialize(f"{atom.name}_s{scale:g}", [(atom, scale)])

    groups: dict[str, list[ActionAtom]] = {}
    for atom in atoms:
        groups.setdefault(atom.group, []).append(atom)
    for public_atom in groups.get("public", [])[:4] + groups.get("phase", [])[:4]:
        for private_atom in groups.get("private", [])[:4]:
            for s1, s2 in [(0.16, 0.08), (0.24, 0.10), (0.34, 0.14), (0.46, 0.18)]:
                materialize(f"joint_public_private_{public_atom.name}_{private_atom.name}_{s1:g}_{s2:g}", [(public_atom, s1), (private_atom, s2)])
        for exc_atom in groups.get("exception", [])[:3]:
            for s1, s2 in [(0.16, 0.08), (0.24, 0.12), (0.34, 0.18)]:
                materialize(f"joint_public_exception_{public_atom.name}_{exc_atom.name}_{s1:g}_{s2:g}", [(public_atom, s1), (exc_atom, s2)])

    for phase_atom in groups.get("phase", [])[:3]:
        for exc_atom in groups.get("exception", [])[:3]:
            for priv_atom in groups.get("private", [])[:3]:
                for s1, s2, s3 in [(0.18, 0.10, 0.06), (0.28, 0.14, 0.08)]:
                    materialize(
                        f"triple_phase_exception_private_{phase_atom.name}_{exc_atom.name}_{priv_atom.name}_{s1:g}_{s2:g}_{s3:g}",
                        [(phase_atom, s1), (exc_atom, s2), (priv_atom, s3)],
                    )

    # Target-route bets: they deliberately couple subjective and objective
    # target routes rather than smoothing all seven labels together.
    target_atoms = [a for a in atoms if a.group.startswith("target_")]
    for i, atom_a in enumerate(target_atoms):
        for atom_b in target_atoms[i + 1 :]:
            if atom_a.group == atom_b.group:
                continue
            for s1, s2 in [(0.18, 0.12), (0.30, 0.18)]:
                materialize(f"target_route_{atom_a.name}_{atom_b.name}_{s1:g}_{s2:g}", [(atom_a, s1), (atom_b, s2)])

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["pre_action_proxy_score"] = (
        out["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        + 0.75 * out["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        + 0.55 * out["h036world_delta_vs_h012"].rank(method="average", pct=True)
        + 0.20 * out["mean_abs_logit_move_h012"].rank(method="average", pct=True)
    )
    out = out.nsmallest(min(520, len(out)), "pre_action_proxy_score").reset_index(drop=True)
    out.to_csv(OUT / "h042_generated_candidates.csv", index=False)
    return out


def score_candidates(rt: dict[str, object], atoms: list[ActionAtom], candidates: pd.DataFrame, known_features: pd.DataFrame, decoder_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        return candidates, pd.DataFrame()
    cand_feature_rows = []
    for rec in candidates.to_dict("records"):
        prob = h036_module("h036_for_h042_load_candidate").load_sub(rec["resolved_path"], rt["sample"])[TARGETS].to_numpy(
            dtype=np.float64
        )
        cand_feature_rows.append(action_features(prob, rt, atoms, str(rec["file"]), "h042_candidate"))
    cand_features = pd.DataFrame(cand_feature_rows)
    cand_features.to_csv(OUT / "h042_candidate_action_features.csv", index=False)
    action_preds = predict_candidates_with_action_decoder(known_features, cand_features, decoder_scores)
    action_preds.to_csv(OUT / "h042_candidate_action_predictions.csv", index=False)
    if not action_preds.empty:
        candidates = candidates.merge(action_preds, on="file", how="left")

    action_margin = candidates.get(
        "pre_h012_action_margin_vs_h012_median", pd.Series(0.01, index=candidates.index)
    ).fillna(0.01)
    action_support = candidates.get(
        "pre_h012_action_support_better_than_h012", pd.Series(0.0, index=candidates.index)
    ).fillna(0.0)
    candidates["h042_pre_h024_score"] = (
        action_margin.rank(method="average", pct=True)
        + 0.60 * candidates["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        + 0.45 * candidates["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        + 0.20 * candidates["mean_abs_logit_move_h012"].rank(method="average", pct=True)
        - 0.25 * action_support
    )
    candidates = candidates.nsmallest(min(240, len(candidates)), "h042_pre_h024_score").reset_index(drop=True)

    h036 = h036_module("h036_for_h042_scores")
    h024_features, h024_models, h024_preds = h036.h024_score_candidates(candidates)
    h024_features.to_csv(OUT / "h042_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h042_h024_model_scores.csv", index=False)
    h024_preds.to_csv(OUT / "h042_h024_candidate_predictions.csv", index=False)
    if not h024_preds.empty:
        candidates = candidates.merge(h024_preds, on="resolved_path", how="left")
    h025_scores, h025_cells = h036.h025_score_candidates(candidates)
    h025_scores.to_csv(OUT / "h042_h025_candidate_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h042_h025_top_cells.csv", index=False)
    if not h025_scores.empty:
        keep = [
            "file",
            "h025_score",
            "pred_gain_top1200_sum",
            "pred_gain_mean_moved",
            "pred_positive_rate_moved",
            "ood_abs_delta_rate",
        ]
        candidates = candidates.merge(h025_scores[[c for c in keep if c in h025_scores.columns]], on="file", how="left")
    margin = candidates.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.02, index=candidates.index)).fillna(0.02)
    support = candidates.get("pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=candidates.index)).fillna(0.0)
    h025 = candidates.get("h025_score", pd.Series(1.0, index=candidates.index)).fillna(1.0)
    candidates["h042_score"] = (
        action_margin.rank(method="average", pct=True)
        + 0.65 * candidates["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        + 0.50 * margin.rank(method="average", pct=True)
        + 0.35 * h025.rank(method="average", pct=True)
        + 0.20 * candidates["mean_abs_logit_move_h012"].rank(method="average", pct=True)
        - 0.25 * action_support
        - 0.25 * support
    )
    candidates = candidates.sort_values(["h042_score", "route_equation_delta_vs_h012"]).reset_index(drop=True)
    candidates.to_csv(OUT / "h042_candidate_scores.csv", index=False)
    return candidates, h025_scores


def rowperm_for_selected(candidate_scores: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame()
    h036 = h036_module("h036_for_h042_rowperm")
    selected = str(candidate_scores.iloc[0]["resolved_path"])
    rowperm = h036.run_rowperm_stress(selected)
    rowperm.to_csv(OUT / "h042_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decision_frame(candidate_scores: pd.DataFrame, decoder_scores: pd.DataFrame, decoder_null: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no generated candidate"}])
    selected = candidate_scores.iloc[0]
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))
    best_loo = float(decoder_scores["loo_mae"].min()) if len(decoder_scores) else np.nan
    decoder_perm_p = (
        float(np.mean(decoder_null["best_null_loo_mae"].to_numpy(dtype=np.float64) <= best_loo))
        if len(decoder_null) and np.isfinite(best_loo)
        else 1.0
    )
    action_margin = float(selected.get("pre_h012_action_margin_vs_h012_median", np.nan))
    action_support = float(selected.get("pre_h012_action_support_better_than_h012", np.nan))
    route_delta = float(selected.get("route_equation_delta_vs_h012", np.nan))
    h024_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    h024_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    h025 = float(selected.get("h025_score", np.nan))
    promote = bool(
        np.isfinite(action_margin)
        and action_margin < -0.00035
        and np.isfinite(action_support)
        and action_support >= 0.50
        and np.isfinite(route_delta)
        and route_delta < -0.00035
        and np.isfinite(h024_margin)
        and h024_margin < -0.00010
        and np.isfinite(h024_support)
        and h024_support >= 0.55
        and np.isfinite(h025)
        and h025 < 0.0
        and rowperm_p <= 0.35
        and decoder_perm_p <= 0.20
    )
    reasons = []
    if not np.isfinite(action_margin) or action_margin >= -0.00035:
        reasons.append("action-coupled decoder does not predict enough gain")
    if not np.isfinite(action_support) or action_support < 0.50:
        reasons.append("action decoder support below 50%")
    if not np.isfinite(route_delta) or route_delta >= -0.00035:
        reasons.append("weak route-equation gain")
    if not np.isfinite(h024_margin) or h024_margin >= -0.00010:
        reasons.append("H024 pre-H012 does not prefer candidate")
    if not np.isfinite(h024_support) or h024_support < 0.55:
        reasons.append("H024 support below 55%")
    if not np.isfinite(h025) or h025 >= 0.0:
        reasons.append("H025 action-health not positive")
    if rowperm_p > 0.35:
        reasons.append("row permutation stress weak")
    if decoder_perm_p > 0.20:
        reasons.append("action decoder not sufficiently beyond permutation null")
    return pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "family": selected["family"],
                "components": selected["components"],
                "pre_h012_action_margin_vs_h012_median": action_margin,
                "pre_h012_action_support_better_than_h012": action_support,
                "route_equation_delta_vs_h012": route_delta,
                "pre_h012_h024_margin_vs_h012_median": h024_margin,
                "pre_h012_h024_support_better_than_h012": h024_support,
                "h025_score": h025,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "best_action_decoder_loo_mae": best_loo,
                "action_decoder_perm_p": decoder_perm_p,
                "reason": "; ".join(reasons) if reasons else "all gates passed",
            }
        ]
    )


def maybe_promote(decision: pd.DataFrame) -> None:
    if decision.empty or not bool(decision.loc[0, "promote"]):
        return
    src = Path(str(decision.loc[0, "selected_resolved_path"]))
    out = ROOT / f"{src.stem}_uploadsafe.csv"
    shutil.copy2(src, out)
    decision.loc[0, "promoted_root_file"] = out.name


def write_report(
    rt: dict[str, object],
    atoms: list[ActionAtom],
    decoder_scores: pd.DataFrame,
    decoder_null: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    best_loo = float(decoder_scores["loo_mae"].min()) if len(decoder_scores) else np.nan
    perm_p = (
        float(np.mean(decoder_null["best_null_loo_mae"].to_numpy(dtype=np.float64) <= best_loo))
        if len(decoder_null) and np.isfinite(best_loo)
        else np.nan
    )
    lines = [
        "# H042 Action-Coupled Public/Private Equation Solver HS-JEPA",
        "",
        "## Question",
        "",
        "Can the missing post-H012 decoder be learned by making upload action",
        "coefficients first-class variables, rather than first estimating hidden",
        "public labels and then pulling H012 toward a posterior?",
        "",
        "## Action Decoder Fit",
        "",
        f"- known public sensors used: `{len(rt['known'])}`",
        f"- action atoms: `{len(atoms)}`",
        f"- best action decoder LOO MAE: `{best_loo:.9f}`",
        f"- action decoder permutation p: `{perm_p:.9f}`",
        "",
        "Top action decoder fits:",
        "",
        md_table(decoder_scores[["feature_set", "alpha", "n_features", "loo_mae", "loo_rmse", "loo_spearman", "loo_pair_acc"]], 14),
        "",
        "Top action atoms:",
        "",
        md_table(pd.read_csv(OUT / "h042_action_atoms.csv").sort_values("strength", ascending=False), 16),
        "",
        "## Candidate Ranking",
        "",
        md_table(
            candidate_scores[
                [
                    "candidate_id",
                    "family",
                    "component_count",
                    "changed_cells_vs_h012",
                    "pre_h012_action_margin_vs_h012_median",
                    "pre_h012_action_support_better_than_h012",
                    "route_equation_delta_vs_h012",
                    "pre_h012_h024_margin_vs_h012_median",
                    "pre_h012_h024_support_better_than_h012",
                    "h025_score",
                    "h042_score",
                ]
            ],
            18,
        )
        if not candidate_scores.empty
        else "_empty_",
        "",
        "## Decision",
        "",
        md_table(decision, 5),
        "",
        "## Interpretation",
        "",
        "- If the action decoder beats permutation nulls but candidates fail H024/H025,",
        "  action response is learnable but still not sufficient to identify a safe",
        "  upload action.",
        "- If the action decoder itself fails, known public LB actions do not support",
        "  a stable route-action equation at this granularity.",
        "- Promotion requires action-equation gain, route-world gain, H024 agreement,",
        "  and H025 row/action-health agreement together.",
    ]
    (OUT / "h042_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    rt = rebuild_route_world()
    atoms = build_atoms(rt)
    known_features = build_action_feature_table(rt, atoms)
    decoder_scores, _ = evaluate_action_decoders(known_features)
    decoder_null = pd.read_csv(OUT / "h042_action_decoder_permutation_null.csv")
    candidates = generate_candidates(rt, atoms)
    candidate_scores, _ = score_candidates(rt, atoms, candidates, known_features, decoder_scores)
    rowperm = rowperm_for_selected(candidate_scores)
    decision = decision_frame(candidate_scores, decoder_scores, decoder_null, rowperm)
    maybe_promote(decision)
    decision.to_csv(OUT / "h042_decision.csv", index=False)
    write_report(rt, atoms, decoder_scores, decoder_null, candidate_scores, decision)
    if not decision.empty:
        print(f"H042 selected: {decision.loc[0, 'selected_candidate_id']}")
        print(f"H042 decision: {decision.loc[0, 'decision']}")
        print(f"H042 reason: {decision.loc[0, 'reason']}")


if __name__ == "__main__":
    main()
