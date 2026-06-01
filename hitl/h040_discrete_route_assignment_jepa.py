#!/usr/bin/env python3
"""H040: discrete route-assignment HS-JEPA.

H012 validated a hidden public-equation world.  H036/H037/H038/H039 then showed
that smooth post-H012 translators fail: local cells, ray amplitudes, memory
transition amplifiers, and nullspace projections cannot safely move away from
H012.

H040 changes the unit of action.

    context = H012 public equation + H036 public world + H014/H038 human memory
              state + failed-translator action-health sensors
    target  = a discrete route assignment for each row/row-target:
              public-equation route, memory/private route, rollback route, hold
    action  = materialize whole-row route switches instead of independent cell
              tweaks

If this works, the missing translator is not a continuous vector field; it is a
public/private route decoder.  If it fails, simple row-route assignment is also
dead and the next high-upside move must solve public equations directly with
private/public subset variables rather than edit H012.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h040_discrete_route_assignment_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_LB = 0.5681234831


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def h036_module(name: str = "h036_for_h040") -> object:
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
    h036 = h036_module("h036_for_h040_loader")
    return h036.load_sub(name, sample)


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


def array_from_cells(cells: pd.DataFrame, col: str, n_rows: int, default: float | None = None) -> np.ndarray:
    mat = np.full((n_rows, len(TARGETS)), np.nan, dtype=np.float64)
    for rec in cells[["row", "target_i", col]].to_dict("records"):
        mat[int(rec["row"]), int(rec["target_i"])] = float(rec[col])
    if np.isnan(mat).any():
        if default is None:
            raise ValueError(f"incomplete matrix for {col}")
        mat = np.nan_to_num(mat, nan=default)
    return mat


def load_runtime() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    h012_df = load_sub(H012)
    sample = h012_df[KEYS].copy()
    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = load_sub(E247, sample)[TARGETS].to_numpy(dtype=np.float64)

    cells = pd.read_csv(HITL / "h038_memory_transition_world_translator_jepa" / "h038_cell_state.csv")
    cells["target_i"] = cells["target"].map({t: i for i, t in enumerate(TARGETS)}).astype(int)
    cells = cells.sort_values(["row", "target_i"]).reset_index(drop=True)
    if len(cells) != len(sample) * len(TARGETS):
        raise ValueError(f"bad h038 cell state size: {len(cells)}")

    for col in [
        "posterior_prob",
        "memory_prob_full",
        "memory_prob_state",
        "memory_prob_date",
        "world_q_cond",
        "cell_world_score",
        "row_public_prob",
        "posterior_gain",
        "memory_alignment",
        "row_full_reliability_q",
        "private_safe_score",
        "public_conflict_core_score",
        "rollback_cost_score",
        "transition_exception_score",
        "transition_repair_score",
        "transition_row_score",
    ]:
        if col not in cells.columns:
            cells[col] = 0.0
        cells[col] = cells[col].fillna(0.0)
    for col in ["h012_changed", "support", "memory_agrees_h012", "memory_disagrees_h012", "world_opposes_memory"]:
        if col not in cells.columns:
            cells[col] = False
        cells[col] = cells[col].fillna(False).astype(bool)

    route_probs = {
        "h012": h012_prob,
        "e247": e247_prob,
        "posterior": clip_prob(array_from_cells(cells, "posterior_prob", len(sample), default=0.5)),
        "world": clip_prob(array_from_cells(cells, "world_q_cond", len(sample), default=0.5)),
        "memory": clip_prob(array_from_cells(cells, "memory_prob_full", len(sample), default=0.5)),
        "memory_state": clip_prob(array_from_cells(cells, "memory_prob_state", len(sample), default=0.5)),
        "memory_date": clip_prob(array_from_cells(cells, "memory_prob_date", len(sample), default=0.5)),
    }
    route_probs["posterior_world"] = clip_prob(0.55 * route_probs["posterior"] + 0.45 * route_probs["world"])
    route_probs["world_memory_exception"] = clip_prob(0.65 * route_probs["world"] + 0.35 * route_probs["memory"])
    route_probs["posterior_memory_exception"] = clip_prob(0.70 * route_probs["posterior"] + 0.30 * route_probs["memory"])

    weights = {
        "world": np.clip(array_from_cells(cells, "cell_world_score", len(sample), default=0.0), 0.0, None),
        "posterior": np.clip(array_from_cells(cells, "posterior_gain", len(sample), default=0.0), 0.0, None),
        "memory": np.clip(array_from_cells(cells, "private_safe_score", len(sample), default=0.0), 0.0, None),
    }
    weights["route"] = 0.55 * weights["world"] + 0.30 * weights["posterior"] + 0.15 * weights["memory"]
    return sample, h012_prob, e247_prob, cells, route_probs, weights


def build_row_state(sample: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    gb = cells.groupby("row", sort=True)
    row = sample.copy()
    row["row"] = np.arange(len(sample))
    row["sleep_date"] = pd.to_datetime(row["sleep_date"])
    row["lifelog_date"] = pd.to_datetime(row["lifelog_date"])
    aggs = gb.agg(
        row_public_prob=("row_public_prob", "mean"),
        cell_world_score_mean=("cell_world_score", "mean"),
        cell_world_score_max=("cell_world_score", "max"),
        posterior_gain_sum=("posterior_gain", "sum"),
        posterior_gain_mean=("posterior_gain", "mean"),
        support_count=("support", "sum"),
        h012_changed_count=("h012_changed", "sum"),
        memory_disagree_rate=("memory_disagrees_h012", "mean"),
        memory_agree_rate=("memory_agrees_h012", "mean"),
        world_opposes_memory_rate=("world_opposes_memory", "mean"),
        row_full_reliability_q=("row_full_reliability_q", "mean"),
        private_safe_score=("private_safe_score", "mean"),
        public_conflict_core_score=("public_conflict_core_score", "mean"),
        rollback_cost_score=("rollback_cost_score", "mean"),
        transition_exception_score=("transition_exception_score", "mean"),
        transition_repair_score=("transition_repair_score", "mean"),
        transition_row_score=("transition_row_score", "mean"),
        memory_alignment=("memory_alignment", "mean"),
    ).reset_index()
    row = row.merge(aggs, on="row", how="left")
    for col in aggs.columns:
        if col != "row":
            row[col] = row[col].fillna(0.0)

    row = row.sort_values(["subject_id", "sleep_date", "lifelog_date", "row"]).reset_index(drop=True)
    row["subject_pos"] = row.groupby("subject_id").cumcount()
    row["subject_n"] = row.groupby("subject_id")["row"].transform("size")
    row["subject_pos_frac"] = row["subject_pos"] / np.maximum(row["subject_n"] - 1, 1)
    row["sleep_gap_prev"] = (
        row.groupby("subject_id")["sleep_date"].diff().dt.days.fillna(999).astype(float).clip(-999, 999)
    )
    row["sleep_gap_next"] = (
        row.groupby("subject_id")["sleep_date"].diff(-1).abs().dt.days.fillna(999).astype(float).clip(-999, 999)
    )
    for col in ["row_public_prob", "transition_exception_score", "private_safe_score", "memory_disagree_rate"]:
        row[f"{col}_prev_delta"] = row[col] - row.groupby("subject_id")[col].shift(1).fillna(row[col])
        row[f"{col}_next_delta"] = row[col] - row.groupby("subject_id")[col].shift(-1).fillna(row[col])
    row = row.sort_values("row").reset_index(drop=True)

    row["public_route_score"] = np.clip(
        0.24 * rank01(row["row_public_prob"])
        + 0.20 * rank01(row["cell_world_score_mean"])
        + 0.14 * rank01(row["support_count"])
        + 0.14 * rank01(row["posterior_gain_sum"])
        + 0.12 * rank01(row["transition_exception_score"])
        + 0.08 * rank01(row["public_conflict_core_score"])
        + 0.08 * rank01(row["memory_disagree_rate"]),
        0.0,
        1.0,
    )
    row["private_memory_route_score"] = np.clip(
        0.24 * rank01(row["private_safe_score"])
        + 0.18 * rank01(row["memory_agree_rate"])
        + 0.16 * rank01(row["row_full_reliability_q"])
        + 0.14 * rank01(row["transition_repair_score"])
        + 0.12 * rank01(row["rollback_cost_score"])
        + 0.10 * rank01(row["row_public_prob"], high=False)
        + 0.06 * rank01(row["memory_alignment"]),
        0.0,
        1.0,
    )
    row["transition_exception_route_score"] = np.clip(
        0.24 * rank01(row["transition_exception_score"])
        + 0.20 * rank01(row["memory_disagree_rate"])
        + 0.18 * rank01(row["world_opposes_memory_rate"])
        + 0.14 * rank01(row["cell_world_score_max"])
        + 0.12 * rank01(np.abs(row["row_public_prob_prev_delta"]) + np.abs(row["memory_disagree_rate_prev_delta"]))
        + 0.08 * rank01(row["posterior_gain_sum"])
        + 0.04 * rank01(row["support_count"]),
        0.0,
        1.0,
    )
    row["route_uncertainty_score"] = np.clip(
        0.34 * (1.0 - np.abs(row["row_public_prob"] - 0.5) * 2.0).clip(0.0, 1.0)
        + 0.22 * rank01(row["memory_disagree_rate"])
        + 0.20 * rank01(row["transition_exception_score"])
        + 0.14 * rank01(row["support_count"])
        + 0.10 * rank01(row["cell_world_score_mean"]),
        0.0,
        1.0,
    )
    row.to_csv(OUT / "h040_row_route_state.csv", index=False)
    return row


def row_mask(row_state: pd.DataFrame, score_col: str, count: int, mode: str) -> np.ndarray:
    n = len(row_state)
    count = int(min(max(count, 0), n))
    mask = np.zeros(n, dtype=bool)
    if count == 0:
        return mask
    if mode == "high":
        chosen = row_state.nlargest(count, score_col)["row"].to_numpy(dtype=int)
    elif mode == "low":
        chosen = row_state.nsmallest(count, score_col)["row"].to_numpy(dtype=int)
    else:
        raise ValueError(mode)
    mask[chosen] = True
    return mask


def subject_balanced_mask(row_state: pd.DataFrame, score_col: str, per_subject: int, mode: str) -> np.ndarray:
    mask = np.zeros(len(row_state), dtype=bool)
    for _, part in row_state.groupby("subject_id", sort=True):
        count = int(min(max(per_subject, 0), len(part)))
        if count <= 0:
            continue
        if mode == "high":
            chosen = part.nlargest(count, score_col)["row"].to_numpy(dtype=int)
        elif mode == "low":
            chosen = part.nsmallest(count, score_col)["row"].to_numpy(dtype=int)
        else:
            raise ValueError(mode)
        mask[chosen] = True
    return mask


def cell_mask_for_rows(
    row_bool: np.ndarray,
    cells: pd.DataFrame,
    mode: str,
    target_group: str,
) -> np.ndarray:
    mat = np.zeros((len(row_bool), len(TARGETS)), dtype=bool)
    if not np.any(row_bool):
        return mat
    flat = cells["row"].to_numpy(dtype=int)
    target_i = cells["target_i"].to_numpy(dtype=int)
    base = row_bool[flat]
    if target_group == "all":
        tmask = np.ones(len(cells), dtype=bool)
    elif target_group == "Q":
        tmask = cells["target"].isin(["Q1", "Q2", "Q3"]).to_numpy(dtype=bool)
    elif target_group == "S":
        tmask = cells["target"].isin(["S1", "S2", "S3", "S4"]).to_numpy(dtype=bool)
    elif target_group == "Q2S1S2S4":
        tmask = cells["target"].isin(["Q2", "S1", "S2", "S4"]).to_numpy(dtype=bool)
    elif target_group == "S124":
        tmask = cells["target"].isin(["S1", "S2", "S4"]).to_numpy(dtype=bool)
    else:
        raise ValueError(target_group)

    if mode == "all":
        cmask = base & tmask
    elif mode == "support":
        cmask = base & tmask & cells["support"].to_numpy(dtype=bool)
    elif mode == "exception":
        cmask = (
            base
            & tmask
            & cells["support"].to_numpy(dtype=bool)
            & (
                cells["memory_disagrees_h012"].to_numpy(dtype=bool)
                | (cells["transition_exception_score"].to_numpy(dtype=np.float64) >= 0.62)
            )
        )
    elif mode == "world_high":
        thresh = float(np.quantile(cells["cell_world_score"].to_numpy(dtype=np.float64), 0.76))
        cmask = base & tmask & (cells["cell_world_score"].to_numpy(dtype=np.float64) >= thresh)
    else:
        raise ValueError(mode)
    mat[flat[cmask], target_i[cmask]] = True
    return mat


def apply_route(
    prob: np.ndarray,
    base_prob: np.ndarray,
    route_prob: np.ndarray,
    mask: np.ndarray,
    alpha: float,
) -> None:
    if not np.any(mask):
        return
    z = logit(prob)
    z_base = logit(base_prob)
    z_route = logit(route_prob)
    z[mask] = (1.0 - alpha) * z_base[mask] + alpha * z_route[mask]
    prob[mask] = sigmoid(z[mask])


def candidate_metrics(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    route_probs: dict[str, np.ndarray],
    weights: dict[str, np.ndarray],
) -> dict[str, float]:
    changed = np.abs(prob - h012_prob) > 1.0e-7
    changed_rows = np.max(changed, axis=1)
    return {
        "changed_cells_vs_h012": int(changed.sum()),
        "changed_rows_vs_h012": int(changed_rows.sum()),
        "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
        "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - logit(h012_prob)))),
        "max_abs_logit_move_h012": float(np.max(np.abs(logit(prob) - logit(h012_prob)))),
        "world_cell_delta_vs_h012": weighted_delta(prob, h012_prob, route_probs["world"], weights["world"]),
        "posterior_delta_vs_h012": weighted_delta(prob, h012_prob, route_probs["posterior"], weights["posterior"]),
        "memory_delta_vs_h012": weighted_delta(prob, h012_prob, route_probs["memory"], weights["memory"]),
        "route_delta_vs_h012": weighted_delta(prob, h012_prob, route_probs["posterior_world"], weights["route"]),
        "row_route_complete_rate": float(
            np.mean((changed.sum(axis=1)[changed_rows] >= 4).astype(float)) if changed_rows.any() else 0.0
        ),
    }


def generate_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    cells: pd.DataFrame,
    row_state: pd.DataFrame,
    route_probs: dict[str, np.ndarray],
    weights: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    generated: set[str] = set()

    def materialize(
        family: str,
        route_public: str,
        public_rows: np.ndarray,
        public_mode: str,
        alpha_public: float,
        route_private: str = "h012",
        private_rows: np.ndarray | None = None,
        private_mode: str = "support",
        alpha_private: float = 0.0,
        target_group: str = "all",
    ) -> None:
        prob = h012_prob.copy()
        private_rows = np.zeros(len(sample), dtype=bool) if private_rows is None else private_rows.copy()
        private_rows = private_rows & ~public_rows
        if route_private != "h012" and alpha_private > 0.0:
            pmask = cell_mask_for_rows(private_rows, cells, private_mode, target_group)
            apply_route(prob, h012_prob, route_probs[route_private], pmask, alpha_private)
        qmask = cell_mask_for_rows(public_rows, cells, public_mode, target_group)
        apply_route(prob, h012_prob, route_probs[route_public], qmask, alpha_public)

        metrics = candidate_metrics(prob, h012_prob, route_probs, weights)
        if metrics["changed_cells_vs_h012"] == 0:
            return
        candidate_id = safe_id(
            f"h040_{family}_{route_public}_p{int(public_rows.sum())}_{public_mode}_"
            f"a{alpha_public:g}_{route_private}_v{int(private_rows.sum())}_{private_mode}_"
            f"b{alpha_private:g}_{target_group}_{short_hash(prob)}"
        )
        if candidate_id in generated:
            return
        generated.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        row_route_score = (
            -metrics["world_cell_delta_vs_h012"]
            -0.65 * metrics["posterior_delta_vs_h012"]
            -0.25 * metrics["route_delta_vs_h012"]
            +0.00008 * metrics["row_route_complete_rate"]
        )
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": family,
                "route_public": route_public,
                "public_rows": int(public_rows.sum()),
                "public_mode": public_mode,
                "alpha_public": float(alpha_public),
                "route_private": route_private,
                "private_rows": int(private_rows.sum()),
                "private_mode": private_mode,
                "alpha_private": float(alpha_private),
                "target_group": target_group,
                "row_route_score": float(row_route_score),
                **metrics,
            }
        )

    public_counts = [10, 20, 35, 55, 80, 110, 140]
    for score_col, family_prefix in [
        ("public_route_score", "public_route"),
        ("transition_exception_route_score", "transition_exception"),
        ("route_uncertainty_score", "uncertain_public"),
    ]:
        for count in public_counts:
            rows_public = row_mask(row_state, score_col, count, "high")
            for route in ["posterior", "world", "posterior_world", "posterior_memory_exception"]:
                for mode in ["all", "support", "exception", "world_high"]:
                    for alpha in [0.25, 0.45, 0.70]:
                        materialize(family_prefix, route, rows_public, mode, alpha)

    for count in [10, 25, 45, 70, 100]:
        rows_private = row_mask(row_state, "private_memory_route_score", count, "high")
        for route in ["memory", "memory_state", "e247"]:
            for mode in ["all", "support"]:
                for alpha in [0.18, 0.35, 0.55]:
                    materialize("private_memory_route", "h012", np.zeros(len(sample), dtype=bool), "all", 0.0, route, rows_private, mode, alpha)

    for public_count in [20, 35, 55, 80]:
        rows_public = row_mask(row_state, "public_route_score", public_count, "high")
        rows_exception = row_mask(row_state, "transition_exception_route_score", public_count, "high")
        for private_count in [10, 25, 45]:
            rows_private = row_mask(row_state, "private_memory_route_score", private_count, "high")
            for rows_pub, family in [(rows_public, "public_private_switch"), (rows_exception, "exception_private_switch")]:
                for route_pub in ["posterior", "world", "posterior_world"]:
                    for route_priv in ["memory", "e247"]:
                        for mode in ["support", "exception"]:
                            materialize(family, route_pub, rows_pub, mode, 0.70, route_priv, rows_private, "support", 0.25)
                            materialize(family, route_pub, rows_pub, mode, 0.45, route_priv, rows_private, "support", 0.18)

    for per_subject in [1, 2, 3, 5]:
        pub = subject_balanced_mask(row_state, "public_route_score", per_subject, "high")
        exc = subject_balanced_mask(row_state, "transition_exception_route_score", per_subject, "high")
        priv = subject_balanced_mask(row_state, "private_memory_route_score", per_subject, "high")
        for pub_rows, family in [(pub, "subject_public_route"), (exc, "subject_exception_route")]:
            for route in ["posterior", "posterior_world", "world"]:
                for alpha in [0.45, 0.70]:
                    materialize(family, route, pub_rows, "support", alpha, "memory", priv, "support", 0.18)
                    materialize(family, route, pub_rows, "all", alpha, "e247", priv, "support", 0.18)

    for group in ["Q", "S", "Q2S1S2S4", "S124"]:
        rows_public = row_mask(row_state, "public_route_score", 80, "high")
        rows_exception = row_mask(row_state, "transition_exception_route_score", 55, "high")
        for route in ["posterior", "world", "posterior_world"]:
            for alpha in [0.45, 0.70]:
                materialize("target_group_route", route, rows_public, "support", alpha, target_group=group)
                materialize("target_group_exception", route, rows_exception, "exception", alpha, target_group=group)

    scores = pd.DataFrame(rows).drop_duplicates("candidate_id")
    if scores.empty:
        return scores

    scores["pre_h024_proxy_score"] = (
        scores["world_cell_delta_vs_h012"].rank(method="average", pct=True)
        +0.75 * scores["posterior_delta_vs_h012"].rank(method="average", pct=True)
        +0.35 * scores["route_delta_vs_h012"].rank(method="average", pct=True)
        -0.20 * scores["row_route_complete_rate"].rank(method="average", pct=True)
    )
    keep_parts = []
    for family, part in scores.groupby("family"):
        keep_n = min(len(part), 35)
        keep_parts.append(part.nsmallest(keep_n, "pre_h024_proxy_score"))
    scores = pd.concat(keep_parts, ignore_index=True)
    scores = scores.nsmallest(min(len(scores), 420), "pre_h024_proxy_score").reset_index(drop=True)
    scores.to_csv(OUT / "h040_generated_candidates.csv", index=False)
    return scores


def score_candidates(candidate_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h036 = h036_module("h036_for_h040_scores")
    h024_features = pd.DataFrame()
    h024_models = pd.DataFrame()
    h024_preds = pd.DataFrame()
    h025_scores = pd.DataFrame()
    h025_cells = pd.DataFrame()
    if candidate_scores.empty:
        return candidate_scores, h024_features, h024_models, h025_cells

    h024_features, h024_models, h024_preds = h036.h024_score_candidates(candidate_scores)
    h024_features.to_csv(OUT / "h040_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h040_h024_model_scores.csv", index=False)
    h024_preds.to_csv(OUT / "h040_h024_candidate_predictions.csv", index=False)
    if not h024_preds.empty:
        candidate_scores = candidate_scores.merge(h024_preds, on="resolved_path", how="left")

    h025_scores, h025_cells = h036.h025_score_candidates(candidate_scores)
    h025_scores.to_csv(OUT / "h040_h025_candidate_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h040_h025_top_cells.csv", index=False)
    if not h025_scores.empty:
        keep_cols = [
            "file",
            "h025_score",
            "pred_gain_top1200_sum",
            "pred_gain_mean_moved",
            "pred_positive_rate_moved",
            "ood_abs_delta_rate",
        ]
        candidate_scores = candidate_scores.merge(
            h025_scores[[c for c in keep_cols if c in h025_scores.columns]], on="file", how="left"
        )

    margin = candidate_scores.get(
        "pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=candidate_scores.index)
    ).fillna(0.02)
    support = candidate_scores.get(
        "pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=candidate_scores.index)
    ).fillna(0.0)
    h025 = candidate_scores.get("h025_score", pd.Series(1.0, index=candidate_scores.index)).fillna(1.0)
    candidate_scores["h040_score"] = (
        0.95 * candidate_scores["world_cell_delta_vs_h012"].rank(method="average", pct=True)
        +0.70 * candidate_scores["posterior_delta_vs_h012"].rank(method="average", pct=True)
        +0.45 * margin.rank(method="average", pct=True)
        +0.35 * h025.rank(method="average", pct=True)
        -0.25 * support
        -0.10 * candidate_scores["row_route_complete_rate"].rank(method="average", pct=True)
    )
    candidate_scores = candidate_scores.sort_values(["h040_score", "world_cell_delta_vs_h012"]).reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h040_candidate_scores.csv", index=False)
    return candidate_scores, h024_features, h024_models, h025_cells


def rowperm_for_selected(candidate_scores: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame()
    h036 = h036_module("h036_for_h040_rowperm")
    selected = str(candidate_scores.iloc[0]["resolved_path"])
    out = h036.run_rowperm_stress(selected)
    out.to_csv(OUT / "h040_selected_h025_rowperm_stress.csv", index=False)
    return out


def decision_frame(candidate_scores: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if candidate_scores.empty:
        return pd.DataFrame(
            [{"decision": "no_candidate", "promote": False, "reason": "no route candidate generated"}]
        )
    selected = candidate_scores.iloc[0]
    pre_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    pre_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    h025_score = float(selected.get("h025_score", np.nan))
    world_delta = float(selected.get("world_cell_delta_vs_h012", np.nan))
    posterior_delta = float(selected.get("posterior_delta_vs_h012", np.nan))
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))

    promote = bool(
        np.isfinite(world_delta)
        and world_delta < -0.00012
        and np.isfinite(posterior_delta)
        and posterior_delta < -0.00004
        and np.isfinite(pre_margin)
        and pre_margin < -0.00010
        and np.isfinite(pre_support)
        and pre_support >= 0.55
        and np.isfinite(h025_score)
        and h025_score < 0.0
        and rowperm_p <= 0.35
    )
    reasons = []
    if not np.isfinite(world_delta) or world_delta >= -0.00012:
        reasons.append("weak world gain")
    if not np.isfinite(posterior_delta) or posterior_delta >= -0.00004:
        reasons.append("weak posterior gain")
    if not np.isfinite(pre_margin) or pre_margin >= -0.00010:
        reasons.append("H024 pre-H012 does not prefer over H012")
    if not np.isfinite(pre_support) or pre_support < 0.55:
        reasons.append("H024 support below 55%")
    if not np.isfinite(h025_score) or h025_score >= 0.0:
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
                "world_cell_delta_vs_h012": world_delta,
                "posterior_delta_vs_h012": posterior_delta,
                "pre_h012_h024_margin_vs_h012_median": pre_margin,
                "pre_h012_h024_support_better_than_h012": pre_support,
                "h025_score": h025_score,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(row_state: pd.DataFrame, candidate_scores: pd.DataFrame, decision: pd.DataFrame) -> None:
    lines = []
    lines.append("# H040 Discrete Route-Assignment HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "Can post-H012 translation be solved by assigning whole rows to discrete public/private routes "
        "instead of applying smooth local cell projections?\n"
    )
    lines.append("## External observation absorbed\n")
    lines.append(
        "- Attached V106 note reports `submission_v106_sleep_state_conditioned_memory.csv` public LB "
        "`0.5703952266`, using same-subject date + sleep-state + sensor-quality memory. This supports "
        "repeated-subject human-state memory, but H012 is still better by `0.0022717435`.\n"
    )
    lines.append("## Row route state\n")
    lines.append(f"- rows: `{len(row_state)}`\n")
    lines.append(f"- mean public-route score: `{row_state['public_route_score'].mean():.9f}`\n")
    lines.append(f"- mean private-memory score: `{row_state['private_memory_route_score'].mean():.9f}`\n")
    lines.append(f"- mean transition-exception score: `{row_state['transition_exception_route_score'].mean():.9f}`\n")
    lines.append("\nTop public-route rows:\n")
    lines.append(md_table(row_state.sort_values("public_route_score", ascending=False)[[
        "row",
        "subject_id",
        "sleep_date",
        "public_route_score",
        "private_memory_route_score",
        "transition_exception_route_score",
        "support_count",
        "memory_disagree_rate",
        "row_public_prob",
    ]], 12))
    lines.append("\n\n## Candidate ranking\n")
    keep = [
        c
        for c in [
            "candidate_id",
            "family",
            "route_public",
            "public_rows",
            "public_mode",
            "alpha_public",
            "route_private",
            "private_rows",
            "world_cell_delta_vs_h012",
            "posterior_delta_vs_h012",
            "route_delta_vs_h012",
            "changed_cells_vs_h012",
            "row_route_complete_rate",
            "pre_h012_h024_margin_vs_h012_median",
            "pre_h012_h024_support_better_than_h012",
            "h025_score",
            "pred_gain_top1200_sum",
            "h040_score",
        ]
        if c in candidate_scores.columns
    ]
    lines.append(md_table(candidate_scores[keep].head(20), 20) if keep else "_empty_")
    lines.append("\n\nDecision:\n")
    lines.append(md_table(decision, 1))
    lines.append(
        "\n\n## Interpretation\n"
        "- If H024/H025 still reject the best route candidates, simple row-level public/private assignment is not enough.\n"
        "- If route candidates improve world/posterior proxies but fail action-health, H012 remains a locked public-equation basin.\n"
        "- The next big-bet direction after failure is to resample hidden public/private subset equations directly, not to continue H012 by local edits.\n"
    )
    (OUT / "h040_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, h012_prob, _e247_prob, cells, route_probs, weights = load_runtime()
    row_state = build_row_state(sample, cells)
    candidate_scores = generate_candidates(sample, h012_prob, cells, row_state, route_probs, weights)
    candidate_scores, h024_features, h024_models, h025_cells = score_candidates(candidate_scores)
    rowperm = rowperm_for_selected(candidate_scores)
    decision = decision_frame(candidate_scores, rowperm)
    decision.to_csv(OUT / "h040_decision.csv", index=False)

    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copy2(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h040_decision.csv", index=False)

    write_report(row_state, candidate_scores, decision)
    if not candidate_scores.empty:
        print(f"H040 selected: {candidate_scores.iloc[0]['candidate_id']}")
        print(f"H040 selected world delta: {float(candidate_scores.iloc[0]['world_cell_delta_vs_h012']):.9f}")
        print(f"H040 decision: {decision.iloc[0]['decision']}")
    else:
        print("H040 generated no candidates")


if __name__ == "__main__":
    main()
