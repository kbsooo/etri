#!/usr/bin/env python3
"""E291: lifestyle block-state assignment audit.

E290 showed a strong train row-placement law but no test-safe rowwise
materialization. This audit moves the hidden target up one level:

    row placement -> subject/calendar/lifestyle block state assignment

The question is whether Q3/S4 lifestyle corrections are tied to test-visible
blocks such as date blocks, weekday/weekend rhythm, month/payday phase, or
lifestyle latent bins. A candidate is only considered if the block-state law
beats train matched block nulls and then beats E247-current matched null
submissions.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e291_lifestyle_block_state_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, groups_for, md_table, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import (  # noqa: E402
    CAP,
    normalize_keys,
    prep_test_meta,
)
from e290_lifestyle_row_placement_law_audit import (  # noqa: E402
    align_columns,
    build_lifestyle_cache,
    cell_nll,
    fit_predict_prob,
    row_features,
    selected_slices,
)
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 291
N_TRAIN_NULL_REPS = 48
N_TEST_NULL_REPS = 5
MAX_BLOCK_POLICIES = 10
BLOCK_FRACS = [0.20, 0.35, 0.50, 0.70]
SCALES = [0.25, 0.50]
DELTA_MODES = ["raw", "centered"]

BLOCK_OUT = OUT / "e291_lifestyle_block_state_train_summary.csv"
CANDIDATE_OUT = OUT / "e291_lifestyle_block_state_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e291_lifestyle_block_state_governor_summary.csv"
SCORE_OUT = OUT / "e291_lifestyle_block_state_scores.csv"
NULL_MAP_OUT = OUT / "e291_lifestyle_block_state_null_map.csv"
REPORT_OUT = OUT / "e291_lifestyle_block_state_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 92) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def folds_for(groups: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    n_splits = min(5, int(groups.nunique()))
    if n_splits < 2:
        return []
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=groups.astype(str).to_numpy()))


def make_block_model() -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(C=0.28, solver="lbfgs", class_weight="balanced", max_iter=1800)),
        ]
    )


def crossfit_block_score(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> np.ndarray:
    score = np.full(len(y), np.nan, dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            score[va_idx] = float(np.mean(y_tr))
            continue
        model = make_block_model()
        model.fit(x.iloc[tr_idx], y_tr)
        score[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return np.nan_to_num(score, nan=float(np.mean(y)))


def score_metrics(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    prevalence = float(np.mean(y))
    if len(np.unique(y)) < 2:
        return {"prevalence": prevalence, "auc": np.nan, "ap": np.nan, "ap_lift": np.nan}
    ap = float(average_precision_score(y, score))
    return {"prevalence": prevalence, "auc": float(roc_auc_score(y, score)), "ap": ap, "ap_lift": ap - prevalence}


def phase_labels(frame: pd.DataFrame) -> pd.Series:
    dom = pd.to_numeric(frame.get("lifelog_dom", pd.Series(15, index=frame.index)), errors="coerce").fillna(15).astype(int)
    labels = np.where(dom <= 5, "pay_start", np.where(dom >= 25, "month_end", "mid_month"))
    return pd.Series(labels, index=frame.index)


def lifestyle_bin(rep_train: pd.DataFrame, rep_test: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    rep_train = rep_train.reset_index(drop=True)
    rep_test = rep_test.reset_index(drop=True)
    if rep_train.shape[1] == 0:
        return pd.Series("life0", index=rep_train.index), pd.Series("life0", index=rep_test.index)
    if any(c.startswith("life_c6_") for c in rep_train.columns):
        tr = rep_train.to_numpy(dtype=np.float64).argmax(axis=1)
        te = rep_test.reindex(columns=rep_train.columns, fill_value=0.0).to_numpy(dtype=np.float64).argmax(axis=1)
        return pd.Series([f"c{v}" for v in tr]), pd.Series([f"c{v}" for v in te])
    vals = pd.to_numeric(rep_train.iloc[:, 0], errors="coerce").fillna(0.0)
    qs = np.unique(np.quantile(vals, [0.25, 0.50, 0.75]))
    if len(qs) == 0:
        return pd.Series("pcbin0", index=rep_train.index), pd.Series("pcbin0", index=rep_test.index)
    tr = np.digitize(vals.to_numpy(dtype=np.float64), qs, right=True)
    te_vals = pd.to_numeric(rep_test.iloc[:, 0], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    te = np.digitize(te_vals, qs, right=True)
    return pd.Series([f"pcbin{v}" for v in tr]), pd.Series([f"pcbin{v}" for v in te])


def block_keys(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    rep_train: pd.DataFrame,
    rep_test: pd.DataFrame,
) -> dict[str, tuple[pd.Series, pd.Series]]:
    tr_life, te_life = lifestyle_bin(rep_train, rep_test)
    tr_subj = train_df["subject_id"].astype(str).reset_index(drop=True)
    te_subj = test_df["subject_id"].astype(str).reset_index(drop=True)
    train_weekday = pd.to_numeric(train_df.get("weekday", pd.Series(0, index=train_df.index)), errors="coerce").fillna(0).astype(int).astype(str)
    test_weekday = pd.to_numeric(test_df.get("weekday", pd.Series(0, index=test_df.index)), errors="coerce").fillna(0).astype(int).astype(str)
    train_weekend = pd.to_numeric(train_df.get("is_weekend", pd.Series(0, index=train_df.index)), errors="coerce").fillna(0).astype(int).astype(str)
    test_weekend = pd.to_numeric(test_df.get("is_weekend", pd.Series(0, index=test_df.index)), errors="coerce").fillna(0).astype(int).astype(str)
    tr_phase = phase_labels(train_df).reset_index(drop=True)
    te_phase = phase_labels(test_df).reset_index(drop=True)
    return {
        "dateblock": (
            train_df["dateblock_group"].astype(str).reset_index(drop=True),
            test_df["dateblock_group"].astype(str).reset_index(drop=True),
        ),
        "subject_weekday": (
            tr_subj + "_wd" + train_weekday.reset_index(drop=True),
            te_subj + "_wd" + test_weekday.reset_index(drop=True),
        ),
        "subject_weekend": (
            tr_subj + "_we" + train_weekend.reset_index(drop=True),
            te_subj + "_we" + test_weekend.reset_index(drop=True),
        ),
        "subject_month_phase": (
            tr_subj + "_" + tr_phase,
            te_subj + "_" + te_phase,
        ),
        "subject_lifestyle_bin": (
            tr_subj + "_" + tr_life.astype(str).reset_index(drop=True),
            te_subj + "_" + te_life.astype(str).reset_index(drop=True),
        ),
    }


def aggregate_block_features(row_x: pd.DataFrame, frame: pd.DataFrame, block_key: pd.Series, benefit: np.ndarray) -> pd.DataFrame:
    work = row_x.copy()
    drop_cols = [c for c in work.columns if c.startswith("subj_")]
    work = work.drop(columns=drop_cols, errors="ignore")
    numeric_cols = [c for c in work.columns if pd.api.types.is_numeric_dtype(work[c])]
    priority = [c for c in numeric_cols if c.startswith(("model_", "life_", "meta_", "subj_", "dateblock_"))]
    if len(priority) < 12:
        priority = numeric_cols
    priority = priority[:80]
    tmp = work[priority].copy()
    tmp["__block"] = block_key.astype(str).to_numpy()
    aggs = tmp.groupby("__block")[priority].agg(["mean", "std", "min", "max"])
    aggs.columns = [f"{c}_{a}" for c, a in aggs.columns]
    aggs = aggs.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    meta = frame.assign(__block=block_key.astype(str).to_numpy()).groupby("__block").agg(
        subject_id=("subject_id", lambda s: s.astype(str).mode().iloc[0] if len(s.astype(str).mode()) else str(s.iloc[0])),
        dateblock_group=("dateblock_group", lambda s: s.astype(str).mode().iloc[0] if len(s.astype(str).mode()) else str(s.iloc[0])),
        n_rows=("subject_id", "size"),
    )
    ben = pd.DataFrame({"__block": block_key.astype(str).to_numpy(), "benefit": benefit}).groupby("__block").agg(
        benefit_mean=("benefit", "mean"),
        benefit_min=("benefit", "min"),
        benefit_good_rate=("benefit", lambda s: float(np.mean(np.asarray(s) < 0.0))),
    )
    out = meta.join(ben, how="left").join(aggs, how="left").reset_index().rename(columns={"__block": "block_key"})
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def aggregate_test_block_features(row_x: pd.DataFrame, frame: pd.DataFrame, block_key: pd.Series) -> pd.DataFrame:
    work = row_x.copy()
    drop_cols = [c for c in work.columns if c.startswith("subj_")]
    work = work.drop(columns=drop_cols, errors="ignore")
    numeric_cols = [c for c in work.columns if pd.api.types.is_numeric_dtype(work[c])]
    priority = [c for c in numeric_cols if c.startswith(("model_", "life_", "meta_", "subj_", "dateblock_"))]
    if len(priority) < 12:
        priority = numeric_cols
    priority = priority[:80]
    tmp = work[priority].copy()
    tmp["__block"] = block_key.astype(str).to_numpy()
    aggs = tmp.groupby("__block")[priority].agg(["mean", "std", "min", "max"])
    aggs.columns = [f"{c}_{a}" for c, a in aggs.columns]
    meta = frame.assign(__block=block_key.astype(str).to_numpy()).groupby("__block").agg(
        subject_id=("subject_id", lambda s: s.astype(str).mode().iloc[0] if len(s.astype(str).mode()) else str(s.iloc[0])),
        dateblock_group=("dateblock_group", lambda s: s.astype(str).mode().iloc[0] if len(s.astype(str).mode()) else str(s.iloc[0])),
        n_rows=("subject_id", "size"),
    )
    out = meta.join(aggs, how="left").reset_index().rename(columns={"__block": "block_key"})
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def select_blocks(score: np.ndarray, frac: float) -> np.ndarray:
    n_select = max(1, int(round(len(score) * float(frac))))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(score)[::-1][:n_select]] = True
    return selected


def block_delta(
    y: np.ndarray,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    row_block: pd.Series,
    block_table: pd.DataFrame,
    block_selected: np.ndarray,
) -> float:
    selected_blocks = set(block_table.loc[block_selected, "block_key"].astype(str))
    row_selected = row_block.astype(str).isin(selected_blocks).to_numpy()
    pred = np.asarray(base_prob, dtype=np.float64).copy()
    pred[row_selected] = aug_prob[row_selected]
    return float(log_loss(y, pred, labels=[0, 1]) - log_loss(y, base_prob, labels=[0, 1]))


def shuffle_block_scores(score: np.ndarray, mode: str, block_table: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    values = np.asarray(score, dtype=np.float64)
    if mode == "row":
        return values[rng.permutation(len(values))]
    group_col = "subject_id" if mode == "subject" else "dateblock_group"
    out = values.copy()
    for _, idx in block_table[group_col].astype(str).groupby(block_table[group_col].astype(str)).indices.items():
        idx_arr = np.asarray(idx, dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    return out


def train_block_stress(
    y: np.ndarray,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    row_block: pd.Series,
    block_table: pd.DataFrame,
    score: np.ndarray,
    frac: float,
    rng: np.random.Generator,
) -> dict[str, float]:
    selected = select_blocks(score, frac)
    actual = block_delta(y, base_prob, aug_prob, row_block, block_table, selected)
    null_rows = []
    for mode in ["row", "subject", "dateblock"]:
        for rep in range(N_TRAIN_NULL_REPS):
            s = shuffle_block_scores(score, mode, block_table, rng)
            null_selected = select_blocks(s, frac)
            null_rows.append({"mode": mode, "delta": block_delta(y, base_prob, aug_prob, row_block, block_table, null_selected)})
    null = pd.DataFrame(null_rows)
    vals = null["delta"].to_numpy(dtype=np.float64)
    out: dict[str, float] = {
        "block_frac": float(frac),
        "selected_blocks": float(np.count_nonzero(selected)),
        "selected_rows": float(row_block.astype(str).isin(set(block_table.loc[selected, "block_key"].astype(str))).sum()),
        "actual_delta": actual,
        "null_q20": float(np.quantile(vals, 0.20)),
        "null_median": float(np.median(vals)),
        "null_best": float(np.min(vals)),
        "dominance": float(np.mean(actual < vals)),
        "placebo_adjusted_vs_median": float(actual - np.median(vals)),
    }
    for mode in ["row", "subject", "dateblock"]:
        mvals = null.loc[null["mode"].eq(mode), "delta"].to_numpy(dtype=np.float64)
        out[f"{mode}_dominance"] = float(np.mean(actual < mvals))
        out[f"{mode}_null_best"] = float(np.min(mvals))
    out["block_gate"] = float(
        actual < -0.00025
        and out["dominance"] >= 0.80
        and min(out["row_dominance"], out["subject_dominance"], out["dateblock_dominance"]) >= 0.58
        and actual <= out["null_q20"] - 1.0e-5
    )
    return out


def build_slice_oof_components(
    train_df: pd.DataFrame,
    base_train: pd.DataFrame,
    target: str,
    rep_train: pd.DataFrame,
    split_name: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    y = train_df[target].to_numpy(dtype=int)
    groups = groups_for(train_df, split_name).reset_index(drop=True)
    x_base = base_train.reset_index(drop=True)
    x_aug = pd.concat([x_base, rep_train.reset_index(drop=True)], axis=1)
    x_base_a, x_aug_a = align_columns(x_base, x_aug)
    from e290_lifestyle_row_placement_law_audit import oof_prob  # local import avoids namespace clutter

    base_oof = oof_prob(x_base_a, y, groups)
    aug_oof = oof_prob(x_aug_a, y, groups)
    benefit = cell_nll(y, aug_oof) - cell_nll(y, base_oof)
    row_x = row_features(base_train, rep_train, target, base_oof, aug_oof, train_df)
    return base_oof, aug_oof, benefit, row_x


def build_test_components(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    target: str,
    rep_train: pd.DataFrame,
    rep_test: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    y = train_df[target].to_numpy(dtype=int)
    x_base_tr = base_train.reset_index(drop=True)
    x_base_te = base_test.reset_index(drop=True)
    x_aug_tr = pd.concat([x_base_tr, rep_train.reset_index(drop=True)], axis=1)
    x_aug_te = pd.concat([x_base_te, rep_test.reset_index(drop=True)], axis=1)
    base_test_prob = fit_predict_prob(x_base_tr, y, x_base_te)
    aug_test_prob = fit_predict_prob(x_aug_tr, y, x_aug_te)
    raw_delta = np.clip(logit(aug_test_prob) - logit(base_test_prob), -CAP, CAP)
    centered_delta = np.clip(raw_delta - float(np.median(raw_delta)), -CAP, CAP)
    row_x = row_features(base_test, rep_test, target, base_test_prob, aug_test_prob, test_df)
    return base_test_prob, aug_test_prob, raw_delta, centered_delta, row_x


def run_block_audit(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    cache: dict[tuple[str, str], dict[str, Any]],
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    rng = np.random.default_rng(RNG_SEED)
    rows: list[dict[str, Any]] = []
    block_cache: dict[str, dict[str, Any]] = {}
    for _, sl in selected_slices().iterrows():
        target = str(sl["target"])
        view_id = str(sl["view_id"])
        split_name = str(sl["split"])
        rep_id = str(sl["rep"])
        rep_train, rep_test = cache[(view_id, split_name)]["reps"][rep_id]
        y = train_df[target].to_numpy(dtype=int)
        base_oof, aug_oof, benefit, train_row_x = build_slice_oof_components(
            train_df, base_train, target, rep_train, split_name
        )
        test_base_prob, test_aug_prob, raw_delta, centered_delta, test_row_x = build_test_components(
            train_df, test_df, base_train, base_test, target, rep_train, rep_test
        )
        for block_scheme, (train_block, test_block) in block_keys(train_df, test_df, rep_train, rep_test).items():
            block_table = aggregate_block_features(train_row_x, train_df, train_block, benefit)
            test_table = aggregate_test_block_features(test_row_x, test_df, test_block)
            if len(block_table) < 12 or block_table["benefit_good_rate"].nunique() < 2:
                continue
            label_defs = {
                "mean_good": block_table["benefit_mean"].to_numpy(dtype=np.float64) < 0.0,
                "strong35": block_table["benefit_mean"].to_numpy(dtype=np.float64)
                <= float(np.quantile(block_table["benefit_mean"].to_numpy(dtype=np.float64), 0.35)),
            }
            unavailable_cols = {
                "block_key",
                "subject_id",
                "dateblock_group",
                "benefit_mean",
                "benefit_min",
                "benefit_good_rate",
            }
            feature_cols = [
                c
                for c in block_table.columns
                if c not in unavailable_cols
                and pd.api.types.is_numeric_dtype(block_table[c])
            ]
            for label_mode, label_bool in label_defs.items():
                labels = label_bool.astype(int)
                if len(np.unique(labels)) < 2:
                    continue
                for cv_group_name, cv_groups in {
                    "subject_cv": block_table["subject_id"].astype(str),
                    "dateblock_cv": block_table["dateblock_group"].astype(str),
                }.items():
                    if cv_groups.nunique() < 2:
                        continue
                    score = crossfit_block_score(block_table[feature_cols], labels, cv_groups)
                    metrics = score_metrics(labels, score)
                    base_rec: dict[str, Any] = {
                        "policy_id": f"{target}_{view_id}_{split_name}_{rep_id}_{block_scheme}_{label_mode}_{cv_group_name}",
                        "slice_id": sl["slice_id"],
                        "target": target,
                        "view_id": view_id,
                        "split": split_name,
                        "rep": rep_id,
                        "block_scheme": block_scheme,
                        "label_mode": label_mode,
                        "cv_group": cv_group_name,
                        "n_blocks": int(len(block_table)),
                        "n_good_blocks": int(labels.sum()),
                        "n_train_rows": int(len(train_df)),
                        "base_loss": float(log_loss(y, base_oof, labels=[0, 1])),
                        "aug_loss": float(log_loss(y, aug_oof, labels=[0, 1])),
                        "full_aug_delta": float(log_loss(y, aug_oof, labels=[0, 1]) - log_loss(y, base_oof, labels=[0, 1])),
                        "benefit_mean": float(np.mean(benefit)),
                        "slice_train_delta": float(sl["actual_delta"]),
                        "slice_train_dominance": float(sl["dominance"]),
                        **metrics,
                    }
                    for frac in BLOCK_FRACS:
                        stress = train_block_stress(y, base_oof, aug_oof, train_block, block_table, score, frac, rng)
                        rows.append({**base_rec, **stress, "block_gate_bool": bool(stress["block_gate"])})
                    block_cache[base_rec["policy_id"]] = {
                        "target": target,
                        "block_scheme": block_scheme,
                        "feature_cols": feature_cols,
                        "block_table": block_table,
                        "test_table": test_table,
                        "train_block": train_block,
                        "test_block": test_block,
                        "labels": labels,
                        "cv_group": cv_group_name,
                        "raw_delta": raw_delta,
                        "centered_delta": centered_delta,
                    }
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values(
            ["block_gate_bool", "actual_delta", "dominance", "auc"],
            ascending=[False, True, False, False],
        ).reset_index(drop=True)
    return summary, block_cache


def write_candidate(
    base: pd.DataFrame,
    target: str,
    row_block: pd.Series,
    test_blocks: pd.DataFrame,
    block_score: np.ndarray,
    frac: float,
    delta: np.ndarray,
    scale: float,
    candidate_id: str,
) -> tuple[Path, np.ndarray]:
    selected_blocks = set(test_blocks.loc[select_blocks(block_score, frac), "block_key"].astype(str))
    row_selected = row_block.astype(str).isin(selected_blocks).to_numpy()
    selected_delta = np.where(row_selected, scale * np.asarray(delta, dtype=np.float64), 0.0)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += selected_delta
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    path = OUT / f"submission_e291_lifeblock_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, selected_delta


def write_null_candidate(base: pd.DataFrame, target: str, selected_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("e291null", source_path.name, mode, rep))
    values = np.asarray(selected_delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values))]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += shuffled
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e291null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def materialize(block_summary: pd.DataFrame, block_cache: dict[str, dict[str, Any]], current: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = block_summary[block_summary["block_gate_bool"].astype(bool)].copy()
    if selected.empty:
        selected = block_summary.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_BLOCK_POLICIES).copy()
    else:
        selected = selected.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_BLOCK_POLICIES).copy()
    meta = prep_test_meta(test_df)
    candidate_paths: list[Path] = []
    candidate_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    score_cache: dict[str, np.ndarray] = {}
    for _, row in selected.iterrows():
        policy_id = str(row["policy_id"])
        cache = block_cache[policy_id]
        if policy_id not in score_cache:
            x_train = cache["block_table"][cache["feature_cols"]]
            x_test = cache["test_table"].reindex(columns=["block_key", "subject_id", "dateblock_group", *cache["feature_cols"]], fill_value=0.0)[cache["feature_cols"]]
            x_train, x_test = align_columns(x_train, x_test)
            model = make_block_model()
            model.fit(x_train, cache["labels"])
            score_cache[policy_id] = model.predict_proba(x_test)[:, 1]
        block_score = score_cache[policy_id]
        for delta_mode, delta in [("raw", cache["raw_delta"]), ("centered", cache["centered_delta"])]:
            if delta_mode not in DELTA_MODES:
                continue
            for scale in SCALES:
                candidate_id = f"{policy_id}_bf{int(float(row['block_frac'])*100):02d}_{delta_mode}_s{int(scale*100):03d}"
                path, selected_delta = write_candidate(
                    current,
                    str(row["target"]),
                    cache["test_block"],
                    cache["test_table"],
                    block_score,
                    float(row["block_frac"]),
                    delta,
                    scale,
                    candidate_id,
                )
                candidate_paths.append(path)
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "basename": path.name,
                        "source_path": rel(path),
                        "policy_id": policy_id,
                        "target": row["target"],
                        "view_id": row["view_id"],
                        "split": row["split"],
                        "rep": row["rep"],
                        "block_scheme": row["block_scheme"],
                        "label_mode": row["label_mode"],
                        "cv_group": row["cv_group"],
                        "block_frac": float(row["block_frac"]),
                        "delta_mode": delta_mode,
                        "scale": scale,
                        "train_actual_delta": float(row["actual_delta"]),
                        "train_dominance": float(row["dominance"]),
                        "train_min_mode_dominance": float(min(row["row_dominance"], row["subject_dominance"], row["dateblock_dominance"])),
                        "test_selected_rows": int(np.count_nonzero(np.abs(selected_delta) > 1.0e-12)),
                        "test_delta_mean": float(np.mean(selected_delta)),
                        "test_delta_p90_abs": float(np.quantile(np.abs(selected_delta), 0.90)),
                        "test_delta_l1": float(np.sum(np.abs(selected_delta))),
                    }
                )
                for null_mode in ["row", "subject", "dateblock"]:
                    for rep in range(N_TEST_NULL_REPS):
                        null_path = write_null_candidate(current, str(row["target"]), selected_delta, path, meta, null_mode, rep)
                        null_rows.append(
                            {
                                "source_basename": path.name,
                                "null_basename": null_path.name,
                                "null_path": rel(null_path),
                                "mode": null_mode,
                                "rep": rep,
                            }
                        )

    candidate_meta = pd.DataFrame(candidate_rows)
    null_map = pd.DataFrame(null_rows)
    if candidate_meta.empty:
        return candidate_meta, null_map, pd.DataFrame()

    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_paths = [ROOT / p for p in null_map["null_path"].tolist()]
    score_features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, score_features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(candidate_meta["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidate_meta.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these_null = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].mean()) if len(these_null) else 1.0
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        for _, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        ready = bool(old_strict and null_strict_rate <= 0.10 and p90_dominance >= 0.80 and mean_dominance >= 0.70 and worst_mode >= 0.55)
        rows.append(
            {
                **cand.to_dict(),
                "old_promotion_decision": a.get("promotion_decision", ""),
                "old_strict_promote": old_strict,
                "actual_mean": float(a["pred_delta_vs_current_mean"]),
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": float(a["pred_delta_vs_current_p90"]),
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "actual_p90", "p90_dominance"],
            ascending=[False, False, True, False],
        ).reset_index(drop=True)
    return candidate_meta, null_map, governor


def write_report(block_summary: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame) -> None:
    gates = block_summary[block_summary["block_gate_bool"].astype(bool)] if not block_summary.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    lines = [
        "# E291 Lifestyle Block-State Assignment Audit",
        "",
        "## Question",
        "",
        "Can Q3/S4 lifestyle corrections be assigned by hidden subject/calendar/lifestyle block state rather than rowwise gates?",
        "",
        "## Train Block Stress",
        "",
        f"- block policy rows: `{len(block_summary)}`",
        f"- block gates: `{len(gates)}`",
        "",
        md_table(
            block_summary[
                [
                    "policy_id",
                    "target",
                    "block_scheme",
                    "label_mode",
                    "cv_group",
                    "block_frac",
                    "n_blocks",
                    "full_aug_delta",
                    "actual_delta",
                    "null_median",
                    "dominance",
                    "row_dominance",
                    "subject_dominance",
                    "dateblock_dominance",
                    "block_gate_bool",
                ]
            ] if not block_summary.empty else block_summary,
            n=50,
        ),
        "",
        "## Materialization Governor",
        "",
        f"- candidates: `{len(candidates)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "target",
                    "block_scheme",
                    "label_mode",
                    "cv_group",
                    "block_frac",
                    "delta_mode",
                    "scale",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "final_decision",
                ]
            ] if not governor.empty else governor,
            n=60,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E291 candidate is public-free ready. Submit only the top ready candidate as the next scarce-LB test.")
    else:
        lines.append("No E291 candidate is public-free ready. Keep block-state assignment as a diagnostic unless a future invariant beats matched nulls.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit asks whether the missing test invariant is a coarser human lifestyle block. If it fails, the bottleneck is not just row smoothing; even block-level lifestyle states are not yet enough to certify a probability move.",
            "",
            "## Files",
            "",
            f"- `{BLOCK_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_df, test_df, base_train, base_test, cache = build_lifestyle_cache()
    block_summary, block_cache = run_block_audit(train_df, test_df, base_train, base_test, cache)
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    if not prep_test_meta(test_df)[KEYS].equals(normalize_keys(current[KEYS])):
        raise RuntimeError("E291 test features do not align with current submission")
    candidates, null_map, governor = materialize(block_summary, block_cache, current, test_df)
    block_summary.to_csv(BLOCK_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(block_summary, candidates, governor)
    print(f"block_policy_rows={len(block_summary)}")
    print(f"block_gates={int(block_summary['block_gate_bool'].sum()) if not block_summary.empty else 0}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"best_block_delta={block_summary['actual_delta'].min():.9f}" if not block_summary.empty else "best_block_delta=nan")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
