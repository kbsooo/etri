#!/usr/bin/env python3
"""E306: within-dateblock S4 row-placement probe.

E304 recovered a plausible S4 hidden block state. E305 failed because a uniform
block-level edit is easy for dateblock nulls to reproduce. This experiment asks
the next sharper question:

    Given a candidate S4-high block, can human/JEPA row context say which row
    inside that block should receive the S4 movement?

No public LB is used. A submission is only considered if it beats matched row,
subject, dateblock, and sign nulls in the local current-anchor governor.
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
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e306_within_block_s4_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, rel, safe_id, short_hash, sigmoid  # noqa: E402
from e303_s4_mean_prior_materializer import score_paths  # noqa: E402
from e304_hidden_block_state_jepa_probe import build_row_views, ensure_numeric  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 306
S4_IDX = TARGETS.index("S4")
N_ROW_NULLS = 96
N_GOV_NULLS = 32
MAX_NULL_EVAL = 20

TEST_BLOCK_PRIOR = OUT / "e304_hidden_block_state_test_blocks.csv"

ROW_CV_OUT = OUT / "e306_within_block_s4_row_cv.csv"
ROW_NULL_OUT = OUT / "e306_within_block_s4_row_nulls.csv"
TEST_ROW_OUT = OUT / "e306_within_block_s4_test_rows.csv"
CANDIDATE_OUT = OUT / "e306_within_block_s4_candidates.csv"
PREFILTER_OUT = OUT / "e306_within_block_s4_prefilter.csv"
GOVERNOR_OUT = OUT / "e306_within_block_s4_governor.csv"
NULL_MAP_OUT = OUT / "e306_within_block_s4_null_map.csv"
SCORE_OUT = OUT / "e306_within_block_s4_scores.csv"
SUMMARY_OUT = OUT / "e306_within_block_s4_summary.csv"
REPORT_OUT = OUT / "e306_within_block_s4_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def md(frame: pd.DataFrame, columns: list[str] | None = None, n: int = 25) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if columns is None else frame.loc[:, [c for c in columns if c in frame.columns]]
    out = view.head(n).copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def zscore(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    std = float(np.nanstd(arr))
    if not np.isfinite(std) or std < 1.0e-12:
        return np.zeros_like(arr, dtype=np.float64)
    return (arr - float(np.nanmean(arr))) / std


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=int)
    ss = np.asarray(score, dtype=np.float64)
    if len(np.unique(yy)) < 2:
        return 0.5
    try:
        return float(roc_auc_score(yy, ss))
    except ValueError:
        return 0.5


def within_block_auc(y: np.ndarray, score: np.ndarray, groups: np.ndarray) -> dict[str, Any]:
    yy = np.asarray(y, dtype=int)
    ss = np.asarray(score, dtype=np.float64)
    gg = np.asarray(groups).astype(str)
    weighted_sum = 0.0
    pair_sum = 0
    block_scores: list[float] = []
    for group in pd.unique(gg):
        idx = np.flatnonzero(gg == group)
        if len(idx) < 2:
            continue
        pos = ss[idx][yy[idx] == 1]
        neg = ss[idx][yy[idx] == 0]
        if len(pos) == 0 or len(neg) == 0:
            continue
        comp = (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()
        pairs = int(len(pos) * len(neg))
        weighted_sum += float(comp) * pairs
        pair_sum += pairs
        block_scores.append(float(comp))
    if pair_sum == 0:
        return {"within_auc_weighted": 0.5, "within_auc_unweighted": 0.5, "mixed_blocks": 0, "pairs": 0}
    return {
        "within_auc_weighted": weighted_sum / pair_sum,
        "within_auc_unweighted": float(np.mean(block_scores)),
        "mixed_blocks": int(len(block_scores)),
        "pairs": int(pair_sum),
    }


def dateblock_center(frame: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    values = ensure_numeric(frame)
    means = values.groupby(base["dateblock_group"].astype(str), sort=False).transform("mean")
    centered = (values - means).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return centered.add_prefix("dbdelta__")


def dateblock_rank(score: pd.Series, groups: pd.Series) -> np.ndarray:
    ranks = score.groupby(groups.astype(str), sort=False).rank(method="average", pct=True)
    return ranks.fillna(0.5).to_numpy(dtype=np.float64) - 0.5


def row_folds(meta: pd.DataFrame, y: np.ndarray, split: str) -> list[tuple[np.ndarray, np.ndarray]]:
    n = len(meta)
    if split == "subject_holdout":
        groups = meta["subject_id"].astype(str)
        return list(GroupKFold(n_splits=min(5, groups.nunique())).split(np.zeros(n), y, groups))
    if split == "dateblock_holdout":
        groups = meta["dateblock_group"].astype(str)
        return list(GroupKFold(n_splits=min(5, groups.nunique())).split(np.zeros(n), y, groups))
    if split == "row_stratified5":
        return list(StratifiedKFold(n_splits=5, shuffle=True, random_state=stable_seed(split)).split(np.zeros(n), y))
    raise ValueError(split)


def fit_row_model(x: pd.DataFrame, y: np.ndarray) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.20, max_iter=1200, solver="lbfgs", class_weight="balanced"),
    ).fit(x, y)


def oof_predict(x: pd.DataFrame, y: np.ndarray, meta: pd.DataFrame, split: str) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    global_mean = float(np.clip(np.mean(y), 1.0e-5, 1.0 - 1.0e-5))
    for tr, va in row_folds(meta, y, split):
        if len(np.unique(y[tr])) < 2:
            pred[va] = global_mean
            continue
        model = fit_row_model(x.iloc[tr], y[tr])
        pred[va] = model.predict_proba(x.iloc[va])[:, 1]
    return np.clip(pred, 1.0e-5, 1.0 - 1.0e-5)


def evaluate_row_views(base: pd.DataFrame, views: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    train_mask = base["split"].eq("train").to_numpy()
    y = base.loc[train_mask, "S4"].astype(int).to_numpy()
    meta = base.loc[train_mask, ["subject_id", "dateblock_group"]].reset_index(drop=True)
    row_views: dict[str, pd.DataFrame] = {
        "calendar": views["calendar"],
        "family_jepa": views["family_jepa"],
        "story_episode": views["story_episode"],
        "family_jepa_dbdelta": dateblock_center(views["family_jepa"], base),
        "story_episode_dbdelta": dateblock_center(views["story_episode"], base),
    }
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for view_id, view in row_views.items():
        x_all = ensure_numeric(view)
        x_train = x_all.loc[train_mask].reset_index(drop=True)
        for split in ["subject_holdout", "dateblock_holdout", "row_stratified5"]:
            pred = oof_predict(x_train, y, meta, split)
            within = within_block_auc(y, pred, meta["dateblock_group"].to_numpy())
            rng = np.random.default_rng(stable_seed(view_id, split, "within_null"))
            null_scores = []
            for rep in range(N_ROW_NULLS):
                shuffled = pred.copy()
                for _, idx in meta.groupby("dateblock_group").indices.items():
                    idx_arr = np.asarray(list(idx), dtype=int)
                    if len(idx_arr) > 1:
                        shuffled[idx_arr] = pred[idx_arr][rng.permutation(len(idx_arr))]
                nwithin = within_block_auc(y, shuffled, meta["dateblock_group"].to_numpy())
                null_scores.append(nwithin["within_auc_weighted"])
                null_rows.append(
                    {
                        "view_id": view_id,
                        "split": split,
                        "rep": rep,
                        "null_within_auc_weighted": nwithin["within_auc_weighted"],
                        "null_within_auc_unweighted": nwithin["within_auc_unweighted"],
                    }
                )
            null_arr = np.asarray(null_scores, dtype=np.float64)
            global_ll = float(log_loss(y, pred, labels=[0, 1]))
            rec = {
                "view_id": view_id,
                "split": split,
                "global_auc": safe_auc(y, pred),
                "global_logloss": global_ll,
                **within,
                "null_median": float(np.median(null_arr)),
                "null_p90": float(np.quantile(null_arr, 0.90)),
                "null_dominance": float(np.mean(within["within_auc_weighted"] > null_arr)),
            }
            rec["row_placement_gate"] = bool(
                rec["within_auc_weighted"] >= 0.530
                and rec["within_auc_unweighted"] >= 0.515
                and rec["null_dominance"] >= 0.80
                and rec["mixed_blocks"] >= 40
            )
            rows.append(rec)
    return pd.DataFrame(rows), pd.DataFrame(null_rows), row_views


def choose_row_view(row_cv: pd.DataFrame) -> tuple[str, str]:
    if row_cv.empty:
        return "story_episode_dbdelta", "dateblock_holdout"
    best = row_cv.sort_values(
        ["row_placement_gate", "null_dominance", "within_auc_weighted", "within_auc_unweighted"],
        ascending=[False, False, False, False],
    ).iloc[0]
    return str(best["view_id"]), str(best["split"])


def fit_predict_test_rows(base: pd.DataFrame, row_views: dict[str, pd.DataFrame], best_view: str) -> pd.DataFrame:
    train_mask = base["split"].eq("train").to_numpy()
    test_mask = base["split"].eq("test").to_numpy()
    y = base.loc[train_mask, "S4"].astype(int).to_numpy()
    x_all = ensure_numeric(row_views[best_view])
    model = fit_row_model(x_all.loc[train_mask].reset_index(drop=True), y)
    pred = np.clip(model.predict_proba(x_all.loc[test_mask].reset_index(drop=True))[:, 1], 1.0e-5, 1.0 - 1.0e-5)
    meta_cols = list(dict.fromkeys(KEYS + ["dateblock_group", "subject_id"]))
    test_rows = base.loc[test_mask, meta_cols].reset_index(drop=True).copy()
    test_rows["row_s4_pred"] = pred
    test_rows["row_s4_centered"] = (
        test_rows["row_s4_pred"] - test_rows.groupby("dateblock_group")["row_s4_pred"].transform("mean")
    )
    test_rows["row_s4_rank_centered"] = dateblock_rank(test_rows["row_s4_pred"], test_rows["dateblock_group"])
    blocks = pd.read_csv(TEST_BLOCK_PRIOR)
    test_rows["block_pred_S4"] = test_rows["dateblock_group"].map(
        blocks.set_index("dateblock_group")["pred_S4_logit_residual"].to_dict()
    ).fillna(0.0)
    test_rows["combined_row_block_score"] = (
        zscore(test_rows["block_pred_S4"].to_numpy())
        + 0.70 * zscore(test_rows["row_s4_centered"].to_numpy())
        + 0.35 * zscore(test_rows["row_s4_rank_centered"].to_numpy())
    )
    test_rows.to_csv(TEST_ROW_OUT, index=False)
    return test_rows


def write_submission(current: pd.DataFrame, delta: np.ndarray, tag: str, null: bool = False) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    base = NULL_DIR if null else OUT
    base.mkdir(exist_ok=True)
    prefix = "submission_e306null" if null else "submission_e306_withinblock_s4"
    path = base / f"{prefix}_{safe_id(tag, 104)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def active_stats(meta: pd.DataFrame, delta_s4: np.ndarray, family: str, tag: str, path: Path) -> dict[str, Any]:
    active = np.abs(delta_s4) > 1.0e-12
    return {
        "basename": path.name,
        "source_path": rel(path),
        "family": family,
        "tag": tag,
        "nonzero_rows": int(active.sum()),
        "pos_rows": int(np.sum(delta_s4 > 1.0e-12)),
        "neg_rows": int(np.sum(delta_s4 < -1.0e-12)),
        "mean_abs_s4_delta": float(np.mean(np.abs(delta_s4))),
        "max_abs_s4_delta": float(np.max(np.abs(delta_s4))) if len(delta_s4) else 0.0,
        "active_block_S4_mean": float(meta.loc[active, "block_pred_S4"].mean()) if active.any() else 0.0,
        "inactive_block_S4_mean": float(meta.loc[~active, "block_pred_S4"].mean()) if (~active).any() else 0.0,
        "active_row_center_mean": float(meta.loc[active, "row_s4_centered"].mean()) if active.any() else 0.0,
        "inactive_row_center_mean": float(meta.loc[~active, "row_s4_centered"].mean()) if (~active).any() else 0.0,
        "active_row_rank_mean": float(meta.loc[active, "row_s4_rank_centered"].mean()) if active.any() else 0.0,
    }


def build_candidates(current: pd.DataFrame, current_meta: pd.DataFrame, test_rows: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    left = normalize_keys(current[KEYS])
    right_keys = normalize_keys(test_rows[KEYS])
    right = pd.concat([right_keys, test_rows.drop(columns=KEYS)], axis=1)
    aligned = left.merge(right, on=KEYS, how="left", validate="one_to_one")
    if aligned["dateblock_group"].isna().any():
        raise RuntimeError("Could not align E306 test row scores to current")
    block_order = (
        aligned[["dateblock_group", "block_pred_S4"]]
        .drop_duplicates("dateblock_group")
        .sort_values("block_pred_S4", ascending=False)
    )
    top_blocks = block_order["dateblock_group"].tolist()
    bottom_blocks = block_order.sort_values("block_pred_S4")["dateblock_group"].tolist()
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}

    def add_delta(tag: str, delta_s4: np.ndarray, family: str) -> None:
        if np.count_nonzero(np.abs(delta_s4) > 1.0e-12) < 2:
            return
        delta = np.zeros((len(current), len(TARGETS)), dtype=np.float64)
        delta[:, S4_IDX] = delta_s4
        path = write_submission(current, delta, tag)
        deltas[path.name] = delta
        rows.append(active_stats(aligned, delta_s4, family, tag, path))

    def top_rows_for_blocks(blocks: list[str], per_block: int, direction: str) -> np.ndarray:
        mask = np.zeros(len(aligned), dtype=bool)
        score_col = "row_s4_centered"
        asc = direction == "low"
        for block in blocks:
            idx = aligned.index[aligned["dateblock_group"].eq(block)].to_numpy()
            if len(idx) == 0:
                continue
            ordered = aligned.loc[idx].sort_values(score_col, ascending=asc).index.to_numpy()
            mask[ordered[: min(per_block, len(ordered))]] = True
        return mask

    amps = [0.018, 0.025, 0.0388, 0.052]
    top_ks = [4, 6, 8, 10, 12, 16]
    per_blocks = [1, 2, 3]
    for k in top_ks:
        for per_block in per_blocks:
            high_mask = top_rows_for_blocks(top_blocks[:k], per_block, "high")
            low_mask = top_rows_for_blocks(bottom_blocks[:k], per_block, "low")
            wrong_high_mask = top_rows_for_blocks(top_blocks[:k], per_block, "low")
            for amp in amps:
                add_delta(f"topblock{k}_rowtop{per_block}_up_a{amp:.4f}", np.where(high_mask, amp, 0.0), "topblock_rowtop")
                add_delta(f"signedblock{k}_row{per_block}_a{amp:.4f}", np.where(high_mask, amp, 0.0) + np.where(low_mask, -amp, 0.0), "signed_block_row")
                add_delta(f"control_topblock{k}_rowbottom{per_block}_up_a{amp:.4f}", np.where(wrong_high_mask, amp, 0.0), "control_wrong_row")

    combined = aligned["combined_row_block_score"].to_numpy(dtype=np.float64)
    row_center = aligned["row_s4_centered"].to_numpy(dtype=np.float64)
    for n in [12, 16, 20, 24, 32, 40, 50]:
        score_order = np.argsort(-combined)
        center_order = np.argsort(-row_center)
        for amp in amps:
            delta_s4 = np.zeros(len(aligned), dtype=np.float64)
            delta_s4[score_order[:n]] = amp
            add_delta(f"global_combined_top{n}_up_a{amp:.4f}", delta_s4, "global_combined_top")
            delta_s4 = np.zeros(len(aligned), dtype=np.float64)
            delta_s4[center_order[:n]] = amp
            add_delta(f"global_rowcenter_top{n}_up_a{amp:.4f}", delta_s4, "global_rowcenter_top")

    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["active_minus_inactive_block_S4"] = frame["active_block_S4_mean"] - frame["inactive_block_S4_mean"]
        frame["active_minus_inactive_row_center"] = frame["active_row_center_mean"] - frame["inactive_row_center_mean"]
        frame.to_csv(CANDIDATE_OUT, index=False)
    else:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
    return frame, deltas


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    pool = strict if not strict.empty else prefilter.copy()
    pool["selection_score"] = (
        pool["pred_delta_vs_current_p90"].fillna(0.0)
        + 0.45 * pool["pred_delta_vs_current_mean"].fillna(0.0)
        - 0.000015 * pool["active_minus_inactive_block_S4"].fillna(0.0)
        - 0.000030 * pool["active_minus_inactive_row_center"].fillna(0.0)
    )
    picks = [
        pool.sort_values("selection_score").head(MAX_NULL_EVAL),
        pool.sort_values("active_minus_inactive_row_center", ascending=False).head(6),
        pool.sort_values("active_minus_inactive_block_S4", ascending=False).head(6),
        pool[pool["family"].eq("control_wrong_row")].sort_values("selection_score").head(4),
    ]
    return pd.concat(picks, ignore_index=True).drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def write_null_candidate(current: pd.DataFrame, delta: np.ndarray, basename: str, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    seed = int(hashlib.sha1(f"{basename}|{mode}|{rep}|e306".encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    values = np.asarray(delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    elif mode == "sign":
        active = np.flatnonzero(np.max(np.abs(values), axis=1) > 1.0e-12)
        flips = rng.choice(np.array([-1.0, 1.0]), size=len(active))
        shuffled[active, :] = values[active, :] * flips[:, None]
    else:
        raise ValueError(mode)
    return write_submission(current, shuffled, f"{Path(basename).stem}_{mode}_r{rep:02d}", null=True)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame()
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = deltas[basename]
        for mode in ["row", "subject", "dateblock", "sign"]:
            for rep in range(N_GOV_NULLS):
                path = write_null_candidate(current, delta, basename, meta, mode, rep)
                null_paths.append(path)
                null_rows.append({"source_basename": basename, "null_basename": path.name, "null_path": rel(path), "mode": mode, "rep": rep})
    null_map = pd.DataFrame(null_rows)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    paths = [OUT / str(b) for b in selected["basename"]]
    scores = score_paths([*paths, *null_paths], current)
    scores.to_csv(SCORE_OUT, index=False)
    cand_scores = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()

    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        p90_vals = these["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        null_strict = float(these["strict_promote_gate"].map(as_bool).mean()) if len(these) else 1.0
        p90_dom = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dom = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_stats: dict[str, float] = {}
        mode_p90 = []
        mode_mean = []
        for mode, part in these.groupby("mode"):
            mp90 = float(np.mean(actual_p90 < part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)))
            mmean = float(np.mean(actual_mean < part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)))
            mode_p90.append(mp90)
            mode_mean.append(mmean)
            mode_stats[f"{mode}_p90_dominance"] = mp90
            mode_stats[f"{mode}_mean_dominance"] = mmean
            mode_stats[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].map(as_bool).mean())
        worst_p90 = float(min(mode_p90)) if mode_p90 else 0.0
        worst_mean = float(min(mode_mean)) if mode_mean else 0.0
        dateblock_p90 = mode_stats.get("dateblock_p90_dominance", 0.0)
        dateblock_mean = mode_stats.get("dateblock_mean_dominance", 0.0)
        ready = bool(
            as_bool(a["strict_promote_gate"])
            and null_strict <= 0.10
            and p90_dom >= 0.80
            and mean_dom >= 0.70
            and worst_p90 >= 0.60
            and worst_mean >= 0.50
            and dateblock_p90 >= 0.65
            and dateblock_mean >= 0.55
        )
        rows.append(
            {
                **cand.to_dict(),
                "actual_strict_promote": as_bool(a["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these)),
                "null_strict_rate": null_strict,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_p90,
                "worst_mode_mean_dominance": worst_mean,
                "public_free_ready": ready,
                "decision": "candidate_ready_needs_64rep_confirm" if ready else "do_not_submit",
                **mode_stats,
            }
        )
    governor = pd.DataFrame(rows).sort_values(
        ["public_free_ready", "null_strict_rate", "dateblock_p90_dominance", "mean_dominance", "actual_p90"],
        ascending=[False, True, False, False, True],
    ).reset_index(drop=True)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return null_map, governor


def write_report(row_cv: pd.DataFrame, nulls: pd.DataFrame, candidates: pd.DataFrame, prefilter: pd.DataFrame, governor: pd.DataFrame, best_view: str, best_split: str) -> None:
    ready = governor[governor["public_free_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    summary = pd.DataFrame(
        [
            {
                "row_views": int(row_cv["view_id"].nunique()) if not row_cv.empty else 0,
                "row_gate_count": int(row_cv["row_placement_gate"].sum()) if not row_cv.empty else 0,
                "best_view": best_view,
                "best_split": best_split,
                "best_within_auc": float(row_cv.sort_values(["row_placement_gate", "null_dominance", "within_auc_weighted"], ascending=[False, False, False]).iloc[0]["within_auc_weighted"]) if not row_cv.empty else np.nan,
                "generated_candidates": len(candidates),
                "old_strict": int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0,
                "null_evaluated": len(governor),
                "ready_32rep": len(ready),
                "best_null_strict_rate": float(governor["null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_dateblock_p90_dominance": float(governor["dateblock_p90_dominance"].max()) if not governor.empty and "dateblock_p90_dominance" in governor.columns else np.nan,
                "best_mean_dominance": float(governor["mean_dominance"].max()) if not governor.empty else np.nan,
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    lines = [
        "# E306 Within-Block S4 Row Placement",
        "",
        "Public LB는 사용하지 않았다. E304 block prior를 직접 평균 이동으로 쓰지 않고, dateblock 내부 row-placement가 실제로 존재하는지 먼저 검증했다.",
        "",
        "## Question",
        "",
        "E305의 실패가 block prior 자체의 실패인가, 아니면 block 안 row identity를 못 맞힌 실패인가? E306은 context=human/JEPA row diary, target=같은 dateblock 안 S4-positive row rank로 둔 JEPA-style row-placement 실험이다.",
        "",
        "## Summary",
        "",
        md(summary),
        "",
        "## Row-Placement Diagnostic",
        "",
        md(row_cv.sort_values(["row_placement_gate", "null_dominance", "within_auc_weighted"], ascending=[False, False, False]), n=20),
        "",
        "## Best Prefilter Candidates",
        "",
        md(
            prefilter,
            [
                "basename",
                "family",
                "nonzero_rows",
                "active_minus_inactive_block_S4",
                "active_minus_inactive_row_center",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "strict_promote_gate",
                "pred_beats_current_rate",
            ],
            n=25,
        ),
        "",
        "## Governor Rows",
        "",
        md(
            governor,
            [
                "basename",
                "family",
                "nonzero_rows",
                "actual_mean",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "mean_dominance",
                "dateblock_p90_dominance",
                "dateblock_mean_dominance",
                "public_free_ready",
                "decision",
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("- A 32-rep public-free row-placement candidate exists. It still needs an independent 64-rep confirmation before public LB use.")
    elif not row_cv.empty and int(row_cv["row_placement_gate"].sum()) == 0:
        lines.extend(
            [
                "- No row-placement representation passed the within-dateblock null gate.",
                "- This weakens the idea that observable human diary rows can reliably choose the S4 row inside a block.",
            ]
        )
    else:
        lines.extend(
            [
                "- Row-placement signal exists locally, but no materialized candidate survived the stricter dateblock null governor.",
                "- The block-state hypothesis remains diagnostic; translating it into S4 probability mass still needs a different action model.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{rel(ROW_CV_OUT)}`",
            f"- `{rel(ROW_NULL_OUT)}`",
            f"- `{rel(TEST_ROW_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(PREFILTER_OUT)}`",
            f"- `{rel(GOVERNOR_OUT)}`",
            f"- `{rel(SUMMARY_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, views, _story_meta = build_row_views()
    row_cv, row_nulls, row_views = evaluate_row_views(base, views)
    row_cv.to_csv(ROW_CV_OUT, index=False)
    row_nulls.to_csv(ROW_NULL_OUT, index=False)
    best_view, best_split = choose_row_view(row_cv)
    test_rows = fit_predict_test_rows(base, row_views, best_view)
    current, current_meta = load_current_and_meta()
    candidates, deltas = build_candidates(current, current_meta, test_rows)
    if candidates.empty:
        prefilter = pd.DataFrame()
        governor = pd.DataFrame()
    else:
        scored = score_paths([OUT / b for b in candidates["basename"]], current)
        keep = [
            "basename",
            "promotion_decision",
            "strict_promote_gate",
            "info_sensor_gate",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        prefilter = candidates.merge(scored[keep], on="basename", how="left")
        prefilter = prefilter.sort_values(
            ["strict_promote_gate", "pred_delta_vs_current_p90", "active_minus_inactive_row_center"],
            ascending=[False, True, False],
        ).reset_index(drop=True)
        prefilter.to_csv(PREFILTER_OUT, index=False)
        selected = select_for_null(prefilter)
        _null_map, governor = run_governor(selected, deltas, current, current_meta)
    write_report(row_cv, row_nulls, candidates, prefilter, governor, best_view, best_split)
    row_gates = int(row_cv["row_placement_gate"].sum()) if not row_cv.empty else 0
    old_strict = int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0
    ready = int(governor["public_free_ready"].map(as_bool).sum()) if not governor.empty else 0
    print(f"row_gates={row_gates} best={best_view}/{best_split} candidates={len(candidates)} old_strict={old_strict} ready={ready}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
