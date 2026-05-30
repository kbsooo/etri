#!/usr/bin/env python3
"""E286: E247 preserve/avoid contrastive latent audit.

E285 found a real human/social boundary around E247/E256 cells, but direct
handwritten add/undo rules were too small or indistinguishable from matched
placebos.  This experiment changes the target from "rank by one story score" to
"predict E247-relative cell identity".

The target is still public-free.  E247, E256, and E284 are treated only as
previously observed cell-body sensors:

    context -> preserve/avoid cell identity -> small E247-relative Q3 action

No public LB is used.  A materialized tensor must beat matched row/subject/
dateblock nulls before it is allowed to become a submission candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e286_e247_preserve_avoid_contrastive_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    evaluate_models,
    score_candidates,
    selected_models,
)
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    feature_row,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message="Inconsistent values: penalty=.*", module="sklearn")

Q3_IDX = TARGETS.index("Q3")
RNG_SEED = 20260531 + 286
N_REPS = 7

CELL_IN = OUT / "e285_e247_residual_human_state_cell_summary.csv"
STATE_IN = OUT / "e282_appentropy_story_state.csv"

LATENT_OUT = OUT / "e286_e247_preserve_avoid_latent_summary.csv"
SOURCE_TRANSFER_OUT = OUT / "e286_e247_preserve_avoid_source_transfer_summary.csv"
CELL_SCORE_OUT = OUT / "e286_e247_preserve_avoid_cell_score_summary.csv"
CANDIDATE_OUT = OUT / "e286_e247_preserve_avoid_candidate_summary.csv"
NULLS_OUT = OUT / "e286_e247_preserve_avoid_nulls.csv"
SCORES_OUT = OUT / "e286_e247_preserve_avoid_scores.csv"
GOVERNOR_OUT = OUT / "e286_e247_preserve_avoid_governor_summary.csv"
REPORT_OUT = OUT / "e286_e247_preserve_avoid_contrastive_latent_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def zscore(values: pd.Series | np.ndarray) -> pd.Series:
    vals = pd.Series(values, dtype=float)
    sd = float(vals.std(ddof=0))
    if sd < 1.0e-12:
        return pd.Series(np.zeros(len(vals)), index=vals.index)
    return (vals - float(vals.mean())) / sd


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 72) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def key_norm(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out.reset_index(drop=True)


def make_model(kind: str, c_value: float = 0.35) -> Pipeline:
    penalty = "l1" if kind == "lr_l1" else "l2"
    solver = "liblinear" if penalty == "l1" else "lbfgs"
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    C=float(c_value),
                    solver=solver,
                    penalty=penalty,
                    class_weight="balanced",
                    max_iter=3000,
                    random_state=RNG_SEED,
                ),
            ),
        ]
    )


@dataclass(frozen=True)
class LabelTask:
    name: str
    positive_mask: pd.Series
    negative_mask: pd.Series
    note: str


def load_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not CELL_IN.exists():
        raise FileNotFoundError(CELL_IN)
    rows = pd.read_csv(CELL_IN).sort_values("row_idx").reset_index(drop=True)
    for col in ["in_e247", "in_e256", "e247_common", "e247_only", "e256_only", "e284_extra"]:
        rows[col] = rows[col].astype(bool)
    sample = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    if len(sample) != len(rows) or not key_norm(sample).equals(key_norm(rows)):
        raise RuntimeError("E286 rows do not align with current sample")
    state = pd.read_csv(STATE_IN)
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if len(meta) != len(rows) or not key_norm(meta).equals(key_norm(rows)):
        raise RuntimeError("E286 state metadata does not align with rows")
    rows["dateblock_group"] = meta["dateblock_group"].astype(str).to_numpy()
    rows["subject_group"] = rows["subject_id"].astype(str)
    return rows, sample


def feature_sets(rows: pd.DataFrame) -> dict[str, list[str]]:
    z_cols = [c for c in rows.columns if c.startswith("z_")]
    state_cols = [
        c
        for c in [
            "app_state_avg_z",
            "app_state_subject_z",
            "app_state_dateblock_z",
            "app_story_score",
            "state_x_amp",
            "story_x_amp",
            "state_z",
            "story_z",
            "state_amp_z",
        ]
        if c in rows.columns
    ]
    geometry_cols = [
        c
        for c in [
            "nn_dist",
            "rollback_amp_abs",
            "single_row_smooth_gain_sum",
            "single_row_smooth_gain_mean",
            "amp_smooth_gain_sum",
            "source_smooth_gain",
            "incoming_smooth_gain_sum",
            "abs_logit_e224_minus_e154_q3",
            "e208_resid_self_abs_mean",
            "e208_nn_target_dist",
            "e208_resid_self_pc10",
            "full_margin",
            "near_test_edge_2",
            "gap_adjacent_2",
            "amp_rank",
            "smooth_sum_rank",
            "smooth_mean_rank",
            "amp_smooth_rank",
            "smooth_z",
            "amp_z",
            "smooth_state_risk",
        ]
        if c in rows.columns
    ]
    oldlaw_cols = [
        c
        for c in ["e284_select_count", "e284_score_sum", "e284_score_max", "e284_top2_count", "e284_score_z"]
        if c in rows.columns
    ]
    sets = {
        "human_social": list(dict.fromkeys([*z_cols, *state_cols])),
        "cell_geometry": list(dict.fromkeys(geometry_cols)),
        "human_plus_geometry": list(dict.fromkeys([*z_cols, *state_cols, *geometry_cols])),
        "human_plus_oldlaw_context": list(dict.fromkeys([*z_cols, *state_cols, *geometry_cols, *oldlaw_cols])),
    }
    return {name: cols for name, cols in sets.items() if cols}


def label_tasks(rows: pd.DataFrame) -> list[LabelTask]:
    risk = rows["e256_only"] | rows["e284_extra"]
    neither = ~rows["in_e247"] & ~rows["in_e256"] & ~rows["e284_extra"]
    return [
        LabelTask(
            "e247_body_vs_risk",
            rows["in_e247"],
            risk,
            "positive=current E247 body, negative=E256-only plus E284 stale-target extras",
        ),
        LabelTask(
            "e247_common_vs_e284_extra",
            rows["e247_common"],
            rows["e284_extra"],
            "positive=E247/E256 common core, negative=E284 old-law extra outside E247",
        ),
        LabelTask(
            "e247_only_vs_e256_only",
            rows["e247_only"],
            rows["e256_only"],
            "positive=E247-only public-positive sibling cells, negative=E256-only sibling additions",
        ),
        LabelTask(
            "e247_body_vs_clean_neither",
            rows["in_e247"],
            neither,
            "diagnostic positive=current E247 body, negative=non-risk outside cells",
        ),
    ]


def split_indices(y: np.ndarray, groups: np.ndarray, split_name: str) -> list[tuple[np.ndarray, np.ndarray]]:
    idx = np.arange(len(y), dtype=int)
    if len(np.unique(y)) < 2:
        return []
    min_class = int(np.min(np.bincount(y.astype(int))))
    if split_name == "stratified":
        n_splits = min(5, min_class)
        if n_splits < 2:
            return []
        splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RNG_SEED)
        return list(splitter.split(idx, y))
    n_groups = len(np.unique(groups))
    n_splits = min(5, n_groups)
    if n_splits < 2:
        return []
    splitter = GroupKFold(n_splits=n_splits)
    return list(splitter.split(idx, y, groups))


def metric_block(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    pred = np.clip(np.asarray(pred, dtype=float), 1.0e-6, 1.0 - 1.0e-6)
    prevalence = float(np.mean(y))
    out = {
        "n_eval": float(len(y)),
        "prevalence": prevalence,
        "ap": float(average_precision_score(y, pred)) if len(np.unique(y)) == 2 else np.nan,
        "logloss": float(log_loss(y, pred, labels=[0, 1])) if len(np.unique(y)) == 2 else np.nan,
    }
    out["auc"] = float(roc_auc_score(y, pred)) if len(np.unique(y)) == 2 else np.nan
    out["ap_lift"] = float(out["ap"] - prevalence) if pd.notna(out["ap"]) else np.nan
    return out


def oof_predict(
    rows: pd.DataFrame,
    label_mask: pd.Series,
    y: np.ndarray,
    cols: list[str],
    model: Pipeline,
    split_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    labeled = rows[label_mask].copy()
    x = labeled[cols].to_numpy(dtype=np.float64)
    if split_name == "subject":
        groups = labeled["subject_group"].astype(str).to_numpy()
    elif split_name == "dateblock":
        groups = labeled["dateblock_group"].astype(str).to_numpy()
    else:
        groups = np.arange(len(labeled), dtype=int)
    folds = split_indices(y, groups, split_name)
    pred = np.full(len(labeled), np.nan, dtype=float)
    covered = np.zeros(len(labeled), dtype=bool)
    for train_idx, test_idx in folds:
        if len(np.unique(y[train_idx])) < 2 or len(np.unique(y[test_idx])) < 2:
            continue
        fit = clone(model)
        fit.fit(x[train_idx], y[train_idx])
        pred[test_idx] = fit.predict_proba(x[test_idx])[:, 1]
        covered[test_idx] = True
    return pred, covered


def permuted_auc_reference(
    rows: pd.DataFrame,
    label_mask: pd.Series,
    y: np.ndarray,
    cols: list[str],
    model: Pipeline,
    split_name: str,
    reps: int = 9,
) -> dict[str, float]:
    rng = np.random.default_rng(RNG_SEED + len(cols) * 17 + len(y))
    aucs: list[float] = []
    aps: list[float] = []
    for rep in range(reps):
        y_perm = y.copy()
        rng.shuffle(y_perm)
        pred, covered = oof_predict(rows, label_mask, y_perm, cols, model, split_name)
        if covered.sum() < 4 or len(np.unique(y_perm[covered])) < 2:
            continue
        metrics = metric_block(y_perm[covered], pred[covered])
        if pd.notna(metrics["auc"]):
            aucs.append(float(metrics["auc"]))
            aps.append(float(metrics["ap"]))
    if not aucs:
        return {"perm_auc_p95": np.nan, "perm_ap_p95": np.nan}
    return {
        "perm_auc_p95": float(np.quantile(aucs, 0.95)),
        "perm_ap_p95": float(np.quantile(aps, 0.95)),
    }


def train_final_predict(rows: pd.DataFrame, label_mask: pd.Series, y: np.ndarray, cols: list[str], model: Pipeline) -> np.ndarray:
    fit = clone(model)
    fit.fit(rows.loc[label_mask, cols].to_numpy(dtype=np.float64), y)
    return fit.predict_proba(rows[cols].to_numpy(dtype=np.float64))[:, 1]


def latent_scan(rows: pd.DataFrame, sets: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    records: list[dict[str, object]] = []
    score_frames: list[pd.DataFrame] = [rows[["row_idx", "subject_id", "sleep_date", "lifelog_date"]].copy()]
    tasks = label_tasks(rows)
    models = {
        "lr_l2_c0p35": make_model("lr_l2", 0.35),
        "lr_l1_c0p22": make_model("lr_l1", 0.22),
    }
    for task in tasks:
        label_mask = (task.positive_mask | task.negative_mask).to_numpy(dtype=bool)
        y = task.positive_mask.loc[label_mask].astype(int).to_numpy()
        if len(np.unique(y)) < 2 or min(np.bincount(y)) < 3:
            continue
        for set_name, cols in sets.items():
            clean_cols = [c for c in cols if c in rows.columns and pd.api.types.is_numeric_dtype(rows[c])]
            if not clean_cols:
                continue
            for model_name, model in models.items():
                split_metrics: list[dict[str, float]] = []
                split_names = ["stratified", "subject", "dateblock"]
                for split_name in split_names:
                    pred, covered = oof_predict(rows, pd.Series(label_mask, index=rows.index), y, clean_cols, model, split_name)
                    if covered.sum() < 4 or len(np.unique(y[covered])) < 2:
                        continue
                    met = metric_block(y[covered], pred[covered])
                    null = permuted_auc_reference(
                        rows,
                        pd.Series(label_mask, index=rows.index),
                        y,
                        clean_cols,
                        model,
                        split_name,
                        reps=9,
                    )
                    rec = {
                        "target_task": task.name,
                        "task_note": task.note,
                        "feature_set": set_name,
                        "model": model_name,
                        "split": split_name,
                        "n_labeled": int(label_mask.sum()),
                        "n_pos": int(y.sum()),
                        "n_neg": int(len(y) - y.sum()),
                        "n_features": int(len(clean_cols)),
                        "covered_rate": float(covered.mean()),
                        **met,
                        **null,
                    }
                    rec["auc_minus_perm_p95"] = float(rec["auc"] - rec["perm_auc_p95"]) if pd.notna(rec["perm_auc_p95"]) else np.nan
                    split_metrics.append(rec)
                    records.append(rec)

                valid = [m for m in split_metrics if pd.notna(m.get("auc"))]
                if not valid:
                    continue
                min_auc = float(np.min([m["auc"] for m in valid]))
                mean_auc = float(np.mean([m["auc"] for m in valid]))
                min_ap_lift = float(np.min([m["ap_lift"] for m in valid]))
                min_perm_margin = float(
                    np.nanmin([m["auc_minus_perm_p95"] for m in valid])
                    if any(pd.notna(m["auc_minus_perm_p95"]) for m in valid)
                    else np.nan
                )
                health = min_auc + 0.25 * mean_auc + 0.40 * min_ap_lift
                if pd.notna(min_perm_margin):
                    health += 0.15 * min_perm_margin
                pred_all = train_final_predict(rows, pd.Series(label_mask, index=rows.index), y, clean_cols, model)
                score_col = f"score_{safe_id(task.name, 20)}_{safe_id(set_name, 18)}_{safe_id(model_name, 12)}"
                score_frames.append(pd.DataFrame({"row_idx": rows["row_idx"], score_col: pred_all}))
                records.append(
                    {
                        "target_task": task.name,
                        "task_note": task.note,
                        "feature_set": set_name,
                        "model": model_name,
                        "split": "aggregate",
                        "n_labeled": int(label_mask.sum()),
                        "n_pos": int(y.sum()),
                        "n_neg": int(len(y) - y.sum()),
                        "n_features": int(len(clean_cols)),
                        "valid_split_count": int(len(valid)),
                        "min_auc": min_auc,
                        "mean_auc": mean_auc,
                        "min_ap_lift": min_ap_lift,
                        "min_auc_minus_perm_p95": min_perm_margin,
                        "latent_health_score": health,
                        "score_col": score_col,
                    }
                )
    latent = pd.DataFrame(records)
    latent = latent.sort_values(
        ["split", "latent_health_score", "min_auc", "mean_auc"],
        ascending=[True, False, False, False],
        na_position="last",
    ).reset_index(drop=True)
    latent.to_csv(LATENT_OUT, index=False)
    scores = score_frames[0]
    for frame in score_frames[1:]:
        scores = scores.merge(frame, on="row_idx", how="left")
    scores.to_csv(CELL_SCORE_OUT, index=False)
    return latent, scores


def source_transfer_scan(rows: pd.DataFrame, sets: dict[str, list[str]]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    train_mask = rows["e247_common"] | rows["e284_extra"]
    train_y = rows["e247_common"].loc[train_mask].astype(int).to_numpy()
    test_mask = rows["e247_only"] | rows["e256_only"]
    test_y = rows["e247_only"].loc[test_mask].astype(int).to_numpy()
    if len(np.unique(train_y)) < 2 or len(np.unique(test_y)) < 2:
        out = pd.DataFrame()
        out.to_csv(SOURCE_TRANSFER_OUT, index=False)
        return out
    models = {
        "lr_l2_c0p35": make_model("lr_l2", 0.35),
        "lr_l1_c0p22": make_model("lr_l1", 0.22),
    }
    for set_name, cols in sets.items():
        clean_cols = [c for c in cols if c in rows.columns and pd.api.types.is_numeric_dtype(rows[c])]
        for model_name, model in models.items():
            fit = clone(model)
            fit.fit(rows.loc[train_mask, clean_cols].to_numpy(dtype=np.float64), train_y)
            pred = fit.predict_proba(rows.loc[test_mask, clean_cols].to_numpy(dtype=np.float64))[:, 1]
            records.append(
                {
                    "source_test": "train_common_vs_e284__test_e247only_vs_e256only",
                    "feature_set": set_name,
                    "model": model_name,
                    "n_train": int(train_mask.sum()),
                    "n_train_pos": int(train_y.sum()),
                    "n_test": int(test_mask.sum()),
                    "n_test_pos": int(test_y.sum()),
                    "n_features": int(len(clean_cols)),
                    **metric_block(test_y, pred),
                    "mean_e247_only_score": float(np.mean(pred[test_y == 1])),
                    "mean_e256_only_score": float(np.mean(pred[test_y == 0])),
                }
            )
    out = pd.DataFrame(records).sort_values(["auc", "ap"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(SOURCE_TRANSFER_OUT, index=False)
    return out


def selected_latents(latent: pd.DataFrame, source_transfer: pd.DataFrame) -> pd.DataFrame:
    agg = latent[latent["split"].eq("aggregate")].copy()
    if agg.empty:
        return agg
    agg["oldlaw_leak_risk"] = agg["feature_set"].astype(str).str.contains("oldlaw", regex=False)
    agg["candidate_rank_score"] = agg["latent_health_score"].fillna(-9.0)
    # Keep the best learned context rows plus geometry controls.  Oldlaw context
    # is diagnostic only unless it is clearly better than non-oldlaw models.
    non_old = agg[~agg["oldlaw_leak_risk"]].sort_values("candidate_rank_score", ascending=False).head(8)
    geom = agg[agg["feature_set"].eq("cell_geometry")].sort_values("candidate_rank_score", ascending=False).head(3)
    human = agg[agg["feature_set"].eq("human_social")].sort_values("candidate_rank_score", ascending=False).head(4)
    old = agg[agg["oldlaw_leak_risk"]].sort_values("candidate_rank_score", ascending=False).head(2)
    keep = pd.concat([non_old, geom, human, old], ignore_index=True).drop_duplicates(
        ["target_task", "feature_set", "model", "score_col"]
    )
    if not source_transfer.empty:
        st = source_transfer[["feature_set", "model", "auc", "ap"]].rename(
            columns={"auc": "source_transfer_auc", "ap": "source_transfer_ap"}
        )
        keep = keep.merge(st, on=["feature_set", "model"], how="left")
    return keep.sort_values(["candidate_rank_score", "source_transfer_auc"], ascending=[False, False]).head(12)


def row_note(rows: pd.DataFrame, undo_idx: np.ndarray, add_idx: np.ndarray) -> dict[str, object]:
    out: dict[str, object] = {
        "undo_count": int(len(undo_idx)),
        "add_count": int(len(add_idx)),
        "undo_idx_list": " ".join(map(str, undo_idx.tolist())),
        "add_idx_list": " ".join(map(str, add_idx.tolist())),
    }
    for prefix, idx in [("undo", undo_idx), ("add", add_idx)]:
        part = rows[rows["row_idx"].isin(set(idx.tolist()))]
        out[f"{prefix}_e247_overlap"] = int(part["in_e247"].sum()) if len(part) else 0
        out[f"{prefix}_e256_overlap"] = int(part["in_e256"].sum()) if len(part) else 0
        out[f"{prefix}_e284_overlap"] = int(part["e284_extra"].sum()) if len(part) else 0
        out[f"{prefix}_smooth_sum"] = float(part["single_row_smooth_gain_sum"].sum()) if len(part) else 0.0
        out[f"{prefix}_mean_amp"] = float(part["rollback_amp_abs"].mean()) if len(part) else np.nan
        out[f"{prefix}_mean_app_state"] = float(part["app_state_avg_z"].mean()) if len(part) else np.nan
        out[f"{prefix}_mean_app_story"] = float(part["app_story_score"].mean()) if len(part) else np.nan
        out[f"{prefix}_mean_state_amp_z"] = float(part["state_amp_z"].mean()) if len(part) else np.nan
    return out


def rank_rows(rows: pd.DataFrame, score: pd.Series, mask: pd.Series, k: int, ascending: bool) -> np.ndarray:
    part = rows[mask].copy()
    score_part = pd.Series(score, index=rows.index).loc[part.index].astype(float)
    ordered = part.assign(_score=score_part).sort_values(["_score", "row_idx"], ascending=[ascending, True])
    return ordered.head(k)["row_idx"].to_numpy(dtype=int)


def apply_candidate(
    current: np.ndarray,
    e224: np.ndarray,
    e154: np.ndarray,
    undo_idx: np.ndarray,
    add_idx: np.ndarray,
    undo_fraction: float,
    add_fraction: float,
) -> np.ndarray:
    pred = current.copy()
    base = logit(pred[:, Q3_IDX])
    if len(undo_idx):
        target_undo = logit(e224[:, Q3_IDX])
        pred[undo_idx, Q3_IDX] = sigmoid(base[undo_idx] + float(undo_fraction) * (target_undo[undo_idx] - base[undo_idx]))
    if len(add_idx):
        target_add = logit(e154[:, Q3_IDX])
        base_after = logit(pred[:, Q3_IDX])
        pred[add_idx, Q3_IDX] = sigmoid(base_after[add_idx] + float(add_fraction) * (target_add[add_idx] - base_after[add_idx]))
    return clip_prob(pred)


def materialize_candidates(rows: pd.DataFrame, sample: pd.DataFrame, latent: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    current = load_sub(CURRENT, sample)[TARGETS].to_numpy(dtype=np.float64)
    e224 = load_sub(e230.E224_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e154 = load_sub(e230.E154_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    score_frame = rows[["row_idx"]].merge(scores, on="row_idx", how="left")
    score_frame = score_frame.set_index(rows.index)
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    in_e247 = rows["in_e247"]
    outside_e247 = ~rows["in_e247"]
    ks = [3, 5, 8, 13]
    for rec in latent.to_dict("records"):
        score_col = str(rec.get("score_col", ""))
        if score_col not in score_frame.columns:
            continue
        raw_score = pd.Series(score_frame[score_col].to_numpy(dtype=float), index=rows.index)
        score_variants = {
            "raw": raw_score,
            "smooth_weighted": zscore(raw_score).to_numpy() + 0.30 * rows["smooth_z"].to_numpy(dtype=float),
            "anti_amp": zscore(raw_score).to_numpy() + 0.25 * rows["smooth_z"].to_numpy(dtype=float) - 0.20 * np.maximum(rows["amp_z"].to_numpy(dtype=float), 0.0),
        }
        for variant_name, variant_score in score_variants.items():
            variant_score = pd.Series(variant_score, index=rows.index, dtype=float)
            for k in ks:
                undo_low = rank_rows(rows, variant_score, in_e247, k, ascending=True)
                undo_high_ctrl = rank_rows(rows, variant_score, in_e247, k, ascending=False)
                add_high = rank_rows(rows, variant_score, outside_e247, k, ascending=False)
                add_low_ctrl = rank_rows(rows, variant_score, outside_e247, k, ascending=True)
                specs = [
                    ("undo_low_preserve", undo_low, np.asarray([], dtype=int), 0.25, 0.0),
                    ("undo_low_preserve", undo_low, np.asarray([], dtype=int), 0.50, 0.0),
                    ("add_high_preserve", np.asarray([], dtype=int), add_high, 0.0, 0.20),
                    ("add_high_preserve", np.asarray([], dtype=int), add_high, 0.0, 0.35),
                    ("swap_low_high", undo_low, add_high, 0.25, 0.20),
                    ("ctrl_undo_high_preserve", undo_high_ctrl, np.asarray([], dtype=int), 0.25, 0.0),
                    ("ctrl_add_low_preserve", np.asarray([], dtype=int), add_low_ctrl, 0.0, 0.20),
                ]
                for action, undo_idx, add_idx, undo_frac, add_frac in specs:
                    if len(undo_idx) == 0 and len(add_idx) == 0:
                        continue
                    pred = apply_candidate(current, e224, e154, undo_idx, add_idx, undo_frac, add_frac)
                    if np.max(np.abs(pred - current)) < 1.0e-12:
                        continue
                    out = sample[KEYS].copy()
                    out[TARGETS] = pred
                    digest = short_hash(out)
                    if digest in seen:
                        continue
                    seen.add(digest)
                    cand_id = (
                        f"{safe_id(str(rec['target_task']), 18)}_{safe_id(str(rec['feature_set']), 18)}_"
                        f"{safe_id(str(rec['model']), 10)}_{variant_name}_{action}_top{k}"
                    )
                    name = f"submission_e286_e247contrast_{safe_id(cand_id, 92)}_{digest}.csv"
                    path = OUT / name
                    out.to_csv(path, index=False)
                    records.append(
                        {
                            "basename": name,
                            "source_path": rel(path),
                            "candidate_id": cand_id,
                            "target_task": rec["target_task"],
                            "feature_set": rec["feature_set"],
                            "model": rec["model"],
                            "score_col": score_col,
                            "score_variant": variant_name,
                            "action": action,
                            "k": int(k),
                            "undo_fraction": float(undo_frac),
                            "add_fraction": float(add_frac),
                            "latent_health_score": float(rec.get("latent_health_score", np.nan)),
                            "min_auc": float(rec.get("min_auc", np.nan)),
                            "mean_auc": float(rec.get("mean_auc", np.nan)),
                            "min_ap_lift": float(rec.get("min_ap_lift", np.nan)),
                            "source_transfer_auc": float(rec.get("source_transfer_auc", np.nan)),
                            **row_note(rows, undo_idx, add_idx),
                        }
                    )
    out_df = pd.DataFrame(records)
    out_df.to_csv(CANDIDATE_OUT, index=False)
    return out_df


def write_null_candidate(base: pd.DataFrame, delta: np.ndarray, meta: pd.DataFrame, source_path: Path, mode: str, rep: int, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    shuffled = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
        values = delta[:, target_idx].copy()
        if mode == "row":
            shuffled[:, target_idx] = values[rng.permutation(len(values))]
        elif mode == "subject":
            for _, idx in meta.groupby("subject_id").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        elif mode == "dateblock":
            for _, idx in meta.groupby("dateblock_group").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        else:
            raise ValueError(mode)
    out = base.copy()
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    out[TARGETS] = clip_prob(sigmoid(base_logits + shuffled))
    stem = source_path.stem.replace("submission_", "")[:82]
    path = NULL_DIR / f"submission_e286null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_nulls(candidates: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    if candidates.empty:
        out = pd.DataFrame()
        out.to_csv(NULLS_OUT, index=False)
        return out
    base = load_sub(CURRENT, sample)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    state = pd.read_csv(STATE_IN)
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if not key_norm(meta).equals(key_norm(base)):
        raise RuntimeError("E286 null metadata does not align with current base")
    records: list[dict[str, object]] = []
    for cand_idx, rec in enumerate(candidates.to_dict("records")):
        path = ROOT / str(rec["source_path"])
        candidate = load_sub(path, base[KEYS])
        delta = logit(candidate[TARGETS].to_numpy(dtype=np.float64)) - base_logits
        if np.max(np.abs(delta)) < 1.0e-12:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                seed = RNG_SEED + cand_idx * 1009 + rep * 97 + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_path = write_null_candidate(base, delta, meta, path, mode, rep, seed)
                records.append(
                    {
                        "source_path": rec["source_path"],
                        "source_basename": rec["basename"],
                        "null_path": rel(null_path),
                        "null_basename": null_path.name,
                        "mode": mode,
                        "rep": rep,
                        "seed": seed,
                    }
                )
    out = pd.DataFrame(records)
    out.to_csv(NULLS_OUT, index=False)
    return out


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        key = rel(path)
        if key in seen:
            continue
        seen.add(key)
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = key
        row["source_path"] = key
        row["basename"] = path.name
        records.append(row)
    return pd.DataFrame(records)


def score_current_anchor(candidates: pd.DataFrame, nulls: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        out = pd.DataFrame()
        out.to_csv(SCORES_OUT, index=False)
        return out, pd.DataFrame()
    known, refs, ref_vecs = build_known_and_refs(sample[KEYS])
    paths = [OUT / CURRENT]
    paths.extend(ROOT / str(path) for path in candidates["source_path"].tolist())
    if not nulls.empty:
        paths.extend(ROOT / str(path) for path in nulls["null_path"].tolist())
    feats = feature_rows(paths, sample[KEYS], refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, feats, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    return scores, selected_models(model_df)


def summarize_governor(scores: pd.DataFrame, candidates: pd.DataFrame, nulls: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or scores.empty:
        out = pd.DataFrame()
        out.to_csv(GOVERNOR_OUT, index=False)
        return out
    actual = scores.merge(candidates, on=["basename", "source_path"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner") if not nulls.empty else pd.DataFrame()
    public_map = known_public_table().set_index("file")["public_lb"].to_dict()
    records: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        matched = null_scores[null_scores["source_basename"].eq(rec["basename"])].copy() if not null_scores.empty else pd.DataFrame()
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        if matched.empty:
            null_strict_rate = np.nan
            p90_dom = np.nan
            mean_dom = np.nan
            worst_mode_dom = np.nan
            placebo_gate = False
            mode_fields: dict[str, object] = {}
        else:
            null_p90 = matched["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            null_mean = matched["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
            p90_dom = float(np.mean(actual_p90 < null_p90))
            mean_dom = float(np.mean(actual_mean < null_mean))
            null_strict_rate = float(matched["strict_promote_gate"].astype(bool).mean())
            mode_fields = {
                "null_p90_q20": float(np.quantile(null_p90, 0.20)),
                "null_p90_median": float(np.median(null_p90)),
                "null_p90_best": float(np.min(null_p90)),
            }
            mode_doms: list[float] = []
            for mode, group in matched.groupby("mode"):
                g_p90 = group["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
                dom = float(np.mean(actual_p90 < g_p90))
                mode_doms.append(dom)
                mode_fields[f"{mode}_p90_dominance"] = dom
                mode_fields[f"{mode}_null_strict_rate"] = float(group["strict_promote_gate"].astype(bool).mean())
            worst_mode_dom = float(min(mode_doms)) if mode_doms else 0.0
            placebo_gate = bool(
                bool(rec["strict_promote_gate"])
                and p90_dom >= 0.85
                and mean_dom >= 0.75
                and worst_mode_dom >= 0.65
                and null_strict_rate <= 0.10
                and actual_p90 <= mode_fields["null_p90_q20"] - 1.0e-6
            )
        public_lb = public_map.get(str(rec["basename"]), np.nan)
        known_public_worse = bool(pd.notna(public_lb) and public_lb >= public_map.get(CURRENT, np.inf))
        if known_public_worse:
            decision = "blocked_known_public_worse"
        elif not bool(rec["strict_promote_gate"]):
            decision = str(rec["promotion_decision"])
        elif not placebo_gate:
            decision = "blocked_by_matched_placebo"
        else:
            decision = "public_free_submission_candidate"
        records.append(
            {
                "basename": rec["basename"],
                "source_path": rec["source_path"],
                "candidate_id": rec["candidate_id"],
                "target_task": rec["target_task"],
                "feature_set": rec["feature_set"],
                "model": rec["model"],
                "score_variant": rec["score_variant"],
                "action": rec["action"],
                "k": int(rec["k"]),
                "undo_count": int(rec["undo_count"]),
                "add_count": int(rec["add_count"]),
                "undo_fraction": float(rec["undo_fraction"]),
                "add_fraction": float(rec["add_fraction"]),
                "latent_health_score": float(rec["latent_health_score"]),
                "min_auc": float(rec["min_auc"]),
                "mean_auc": float(rec["mean_auc"]),
                "min_ap_lift": float(rec["min_ap_lift"]),
                "source_transfer_auc": float(rec["source_transfer_auc"]),
                "old_promotion_decision": rec["promotion_decision"],
                "old_strict_promote": bool(rec["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(rec["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(rec["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(rec["incremental_bad_axis_vs_current"]),
                "null_count": int(len(matched)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_mode_dom,
                "matched_placebo_gate": placebo_gate,
                "public_lb_if_known": public_lb,
                "known_public_worse_than_current": known_public_worse,
                "public_free_submission_ready": bool(decision == "public_free_submission_candidate"),
                "final_decision": decision,
                **mode_fields,
            }
        )
    out = pd.DataFrame(records).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    out.to_csv(GOVERNOR_OUT, index=False)
    return out


def write_report(
    latent: pd.DataFrame,
    source_transfer: pd.DataFrame,
    selected: pd.DataFrame,
    candidates: pd.DataFrame,
    governor: pd.DataFrame,
    selected_models_df: pd.DataFrame,
) -> None:
    agg = latent[latent["split"].eq("aggregate")].copy() if not latent.empty else pd.DataFrame()
    split = latent[~latent["split"].eq("aggregate")].copy() if not latent.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    old_strict = int(governor["old_strict_promote"].astype(bool).sum()) if not governor.empty else 0
    placebo = int(governor["matched_placebo_gate"].astype(bool).sum()) if not governor.empty else 0
    lines = [
        "# E286 E247 Preserve/Avoid Contrastive Latent Audit",
        "",
        "## Question",
        "",
        "Can human/social context learn E247-relative preserve/avoid cell identity strongly enough to create an E247-current Q3 candidate without public LB?",
        "",
        "## Latent Health",
        "",
        md_table(
            agg.sort_values("latent_health_score", ascending=False),
            [
                "target_task",
                "feature_set",
                "model",
                "n_labeled",
                "n_pos",
                "n_neg",
                "valid_split_count",
                "min_auc",
                "mean_auc",
                "min_ap_lift",
                "min_auc_minus_perm_p95",
                "latent_health_score",
                "score_col",
            ],
            n=24,
        ),
        "",
        "## Split-Level Stress",
        "",
        md_table(
            split.sort_values(["target_task", "feature_set", "model", "split"]),
            [
                "target_task",
                "feature_set",
                "model",
                "split",
                "n_labeled",
                "n_pos",
                "n_neg",
                "n_features",
                "covered_rate",
                "auc",
                "ap",
                "ap_lift",
                "perm_auc_p95",
                "auc_minus_perm_p95",
            ],
            n=40,
        ),
        "",
        "## Source-Transfer Stress",
        "",
        md_table(
            source_transfer,
            [
                "source_test",
                "feature_set",
                "model",
                "n_train",
                "n_train_pos",
                "n_test",
                "n_test_pos",
                "auc",
                "ap",
                "mean_e247_only_score",
                "mean_e256_only_score",
            ],
            n=20,
        ),
        "",
        "## Selected Latents For Materialization",
        "",
        md_table(
            selected,
            [
                "target_task",
                "feature_set",
                "model",
                "latent_health_score",
                "min_auc",
                "mean_auc",
                "min_ap_lift",
                "source_transfer_auc",
                "score_col",
            ],
            n=20,
        ),
        "",
        "## Candidate Governor",
        "",
        f"- materialized candidates: `{len(candidates)}`",
        f"- matched-placebo selected models: `{len(selected_models_df)}`",
        f"- old strict-promote candidates: `{old_strict}`",
        f"- matched-placebo gate passes: `{placebo}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor,
            [
                "basename",
                "candidate_id",
                "target_task",
                "feature_set",
                "score_variant",
                "action",
                "k",
                "final_decision",
                "old_promotion_decision",
                "actual_mean",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "worst_mode_p90_dominance",
                "matched_placebo_gate",
            ],
            n=50,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        best = ready.iloc[0]
        lines.append(f"`{best['basename']}` survived the public-free governor. Review it as a scarce-slot candidate.")
    else:
        lines.append(
            "No E286 contrastive preserve/avoid tensor is submission-ready. The learned latent may separate cell identity, but it has not produced an E247-current movement that beats matched nulls."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This test separates representation health from submission translation. If latent AUC is healthy but the governor fails, the human/social state can explain E247 cell identity but still cannot safely move E247 probabilities. If latent AUC is weak, the E247/E256 boundary from E285 is descriptive rather than learnable.",
            "",
            "## Files",
            "",
            f"- `{LATENT_OUT.name}`",
            f"- `{SOURCE_TRANSFER_OUT.name}`",
            f"- `{CELL_SCORE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, sample = load_rows()
    sets = feature_sets(rows)
    latent, scores = latent_scan(rows, sets)
    source_transfer = source_transfer_scan(rows, sets)
    selected = selected_latents(latent, source_transfer)
    candidates = materialize_candidates(rows, sample, selected, scores)
    nulls = generate_nulls(candidates, sample)
    score_df, selected_models_df = score_current_anchor(candidates, nulls, sample)
    governor = summarize_governor(score_df, candidates, nulls)
    write_report(latent, source_transfer, selected, candidates, governor, selected_models_df)

    old_strict = int(governor["old_strict_promote"].sum()) if not governor.empty else 0
    placebo = int(governor["matched_placebo_gate"].sum()) if not governor.empty else 0
    ready = int(governor["public_free_submission_ready"].sum()) if not governor.empty else 0
    print(f"latent_rows={len(latent)}")
    print(f"selected_latents={len(selected)}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(nulls)}")
    print(f"old_strict={old_strict}")
    print(f"matched_placebo={placebo}")
    print(f"ready={ready}")
    if not selected.empty:
        print(
            selected[
                [
                    "target_task",
                    "feature_set",
                    "model",
                    "latent_health_score",
                    "min_auc",
                    "mean_auc",
                    "source_transfer_auc",
                    "score_col",
                ]
            ]
            .head(12)
            .round(6)
            .to_string(index=False)
        )
    if not governor.empty:
        print(
            governor[
                [
                    "candidate_id",
                    "final_decision",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "matched_placebo_gate",
                ]
            ]
            .head(20)
            .round(9)
            .to_string(index=False)
        )
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
