#!/usr/bin/env python3
"""E304: hidden subject/dateblock state JEPA probe.

E303 rejected the current S4 mask-surgery branch: many candidates were
selector-visible, but subject/dateblock nulls could reproduce the mean edge.
This script steps back to the latent object that would have to exist for a real
breakthrough:

    human diary context for a subject/dateblock -> hidden target-rate residual

The target representation is not raw row reconstruction. It is the shrunken
block-level Q/S logit residual after removing the subject prior. We evaluate
whether human/social/JEPA diary context predicts that latent block state under
subject-held and block-held stress, and whether the resulting test block state
explains the S4 placement failures from E299-E303.

No public LB is used. No submission is created.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    build_story_matrix,
    load_frames,
    md_table,
)
from e295_episode_state_jepa_audit import build_episode_matrix  # noqa: E402
from e300_s4_mean_dominance_rescue import load_current_and_meta, rel  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 304
N_NULL_REPS = 24
BLOCK_ALPHA = 4.0

CURRENT = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E299_PARENT = OUT / "submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv"
E300_READY = OUT / "submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv"
E303_BEST = OUT / "submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p16_bd3f44a6.csv"

SUMMARY_OUT = OUT / "e304_hidden_block_state_summary.csv"
TARGET_OUT = OUT / "e304_hidden_block_state_target_metrics.csv"
NULL_OUT = OUT / "e304_hidden_block_state_nulls.csv"
TEST_BLOCK_OUT = OUT / "e304_hidden_block_state_test_blocks.csv"
ALIGN_OUT = OUT / "e304_hidden_block_state_alignment.csv"
REPORT_OUT = OUT / "e304_hidden_block_state_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit_safe(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def spearman_safe(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 3:
        return 0.0
    if len(np.unique(np.round(x, 12))) < 2 or len(np.unique(np.round(y, 12))) < 2:
        return 0.0
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else 0.0


def ensure_numeric(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)


def build_row_views() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame]:
    base, raw, stories, feature_frames = load_frames()
    story_matrix, story_meta = build_story_matrix(base, stories, feature_frames)
    episode_matrix, episode_meta = build_episode_matrix(base, feature_frames)

    meta_cols = set(KEYS + TARGETS + ["split", "dateblock_group", "subject_id"])
    meta_cols.update(c for c in base.columns if c.endswith("_date_only"))
    calendar_cols = [
        c
        for c in [
            "subject_order",
            "weekday",
            "is_weekend",
            "lifelog_dom",
            "lifelog_month",
            "weekday_sin",
            "weekday_cos",
            "dom_sin",
            "dom_cos",
            "month_sin",
            "month_cos",
        ]
        if c in base.columns
    ]
    family_cols = [
        c
        for c in base.columns
        if c not in meta_cols and pd.api.types.is_numeric_dtype(base[c])
    ]
    raw_cols = [
        c
        for c in raw.columns
        if c not in meta_cols and pd.api.types.is_numeric_dtype(raw[c])
    ]
    raw_std = raw.loc[base["split"].eq("train"), raw_cols].std(ddof=0).replace(0, np.nan).dropna()
    raw_keep = raw_std.sort_values(ascending=False).head(120).index.tolist()

    views = {
        "calendar": ensure_numeric(base[calendar_cols]),
        "family_jepa": ensure_numeric(base[family_cols]),
        "story_episode": ensure_numeric(
            pd.concat(
                [
                    story_matrix.add_prefix("story__"),
                    episode_matrix.add_prefix("episode__"),
                ],
                axis=1,
            )
        ),
        "raw_top120": ensure_numeric(raw[raw_keep].add_prefix("raw__")),
    }
    views["human_full"] = ensure_numeric(
        pd.concat(
            [
                views["family_jepa"].add_prefix("fam__"),
                views["story_episode"],
                views["raw_top120"],
            ],
            axis=1,
        )
    )
    story_meta = pd.concat(
        [
            story_meta.assign(kind="story", feature=lambda d: "story__" + d["story"].astype(str)),
            episode_meta.drop_duplicates("episode").assign(kind="episode", feature=lambda d: "episode__" + d["episode"].astype(str)),
        ],
        ignore_index=True,
        sort=False,
    )
    return base, views, story_meta


def aggregate_blocks(base: pd.DataFrame, row_view: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    meta_cols = list(dict.fromkeys(KEYS + ["split", "dateblock_group", "subject_id", "subject_order"]))
    meta = base[meta_cols].rename(
        columns={"subject_order": "__subject_order"}
    )
    work = pd.concat([meta, row_view], axis=1)
    feature_cols = row_view.columns.tolist()
    std_cols = [
        c
        for c in feature_cols
        if "energy" in c
        or "jepa_" in c
        or c.startswith("story__")
        or c.startswith("episode__")
        or c.startswith("raw__")
    ]
    for (split_value, block), part in work.groupby(["split", "dateblock_group"], sort=False):
        rec: dict[str, Any] = {
            "dateblock_group": str(block),
            "subject_id": str(part["subject_id"].iloc[0]),
            "split": str(split_value),
            "n_rows": int(len(part)),
            "block_order": float(part["__subject_order"].min() // 7),
            "subject_order_mean": float(part["__subject_order"].mean()),
            "sleep_start": str(part["sleep_date"].iloc[0]),
            "sleep_end": str(part["sleep_date"].iloc[-1]),
        }
        vals = part[feature_cols]
        means = vals.mean(axis=0)
        for col, val in means.items():
            rec[f"mean__{col}"] = float(val)
        if std_cols:
            stds = vals[std_cols].std(axis=0, ddof=0)
            for col, val in stds.items():
                rec[f"std__{col}"] = float(val)
        rows.append(rec)
    return pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def block_target_residuals(base: pd.DataFrame) -> pd.DataFrame:
    train = base[base["split"].eq("train")].copy()
    subj_prior = train.groupby("subject_id")[TARGETS].mean()
    rows: list[dict[str, Any]] = []
    for block, part in train.groupby("dateblock_group", sort=False):
        subject = str(part["subject_id"].iloc[0])
        n = len(part)
        rec: dict[str, Any] = {
            "dateblock_group": str(block),
            "subject_id": subject,
            "n_rows_target": int(n),
        }
        prior = subj_prior.loc[subject].to_numpy(dtype=np.float64)
        sums = part[TARGETS].sum(axis=0).to_numpy(dtype=np.float64)
        shrunk = (sums + BLOCK_ALPHA * prior) / (n + BLOCK_ALPHA)
        residual = logit_safe(shrunk) - logit_safe(prior)
        prob_resid = shrunk - prior
        for i, target in enumerate(TARGETS):
            rec[f"{target}_block_rate"] = float(sums[i] / max(n, 1))
            rec[f"{target}_subject_prior"] = float(prior[i])
            rec[f"{target}_logit_residual"] = float(residual[i])
            rec[f"{target}_prob_residual"] = float(prob_resid[i])
        rows.append(rec)
    return pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def folds_for(meta: pd.DataFrame, split: str) -> list[tuple[np.ndarray, np.ndarray]]:
    if split == "subject_holdout":
        groups = meta["subject_id"].astype(str)
        n_splits = min(5, groups.nunique())
        return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(meta)), groups=groups))
    if split == "block_random5":
        return list(KFold(n_splits=5, shuffle=True, random_state=stable_seed(split)).split(np.zeros(len(meta))))
    raise ValueError(split)


def model_predict_oof(x: pd.DataFrame, y: np.ndarray, meta: pd.DataFrame, split: str) -> np.ndarray:
    pred = np.zeros_like(y, dtype=np.float64)
    for tr, va in folds_for(meta, split):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=35.0))
        model.fit(x.iloc[tr], y[tr])
        pred[va] = model.predict(x.iloc[va])
    return pred


def metric_rows(y: np.ndarray, pred: np.ndarray, view_id: str, split: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    target_rows: list[dict[str, Any]] = []
    spears = []
    maes = []
    r2s = []
    sign_hits = []
    for i, target in enumerate(TARGETS):
        yy = y[:, i]
        pp = pred[:, i]
        sp = spearman_safe(yy, pp)
        mae = float(mean_absolute_error(yy, pp))
        r2 = float(r2_score(yy, pp)) if len(np.unique(np.round(yy, 12))) >= 2 else 0.0
        sign_hit = float(np.mean(np.sign(yy) == np.sign(pp)))
        spears.append(sp)
        maes.append(mae)
        r2s.append(r2)
        sign_hits.append(sign_hit)
        target_rows.append(
            {
                "view_id": view_id,
                "split": split,
                "target": target,
                "spearman": sp,
                "mae": mae,
                "r2": r2,
                "sign_hit_rate": sign_hit,
                "target_std": float(np.std(yy)),
            }
        )
    summary = {
        "view_id": view_id,
        "split": split,
        "mean_spearman": float(np.mean(spears)),
        "mean_mae": float(np.mean(maes)),
        "mean_r2": float(np.mean(r2s)),
        "mean_sign_hit_rate": float(np.mean(sign_hits)),
        "positive_spearman_targets": int(np.sum(np.asarray(spears) > 0.0)),
        "S4_spearman": float(spears[TARGETS.index("S4")]),
        "S4_mae": float(maes[TARGETS.index("S4")]),
        "S4_sign_hit_rate": float(sign_hits[TARGETS.index("S4")]),
    }
    return summary, target_rows


def shuffle_y(y: np.ndarray, meta: pd.DataFrame, mode: str, rng: np.random.Generator) -> np.ndarray:
    arr = np.asarray(y, dtype=np.float64)
    out = arr.copy()
    if mode == "global":
        return arr[rng.permutation(len(arr))]
    if mode == "within_subject":
        for _, idx in meta.groupby("subject_id").indices.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            if len(idx_arr) > 1:
                out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
        return out
    if mode == "subject_circular":
        for _, idx in meta.groupby("subject_id").indices.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            if len(idx_arr) > 1:
                shift = int(rng.integers(1, len(idx_arr)))
                out[idx_arr] = np.roll(arr[idx_arr], shift=shift, axis=0)
        return out
    raise ValueError(mode)


def evaluate_views(train_blocks: dict[str, pd.DataFrame], target_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[tuple[str, str], np.ndarray]]:
    y_cols = [f"{t}_logit_residual" for t in TARGETS]
    y = target_df[y_cols].to_numpy(dtype=np.float64)
    meta = target_df[["dateblock_group", "subject_id"]].reset_index(drop=True)
    summary_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    preds: dict[tuple[str, str], np.ndarray] = {}

    for view_id, block_frame in train_blocks.items():
        x = block_frame.drop(columns=["dateblock_group", "subject_id", "split", "sleep_start", "sleep_end"], errors="ignore")
        x = ensure_numeric(x)
        for split in ["subject_holdout", "block_random5"]:
            pred = model_predict_oof(x, y, meta, split)
            preds[(view_id, split)] = pred
            summ, targ = metric_rows(y, pred, view_id, split)
            rng = np.random.default_rng(stable_seed(view_id, split, "null"))
            null_scores = []
            for mode in ["global", "within_subject", "subject_circular"]:
                for rep in range(N_NULL_REPS):
                    yn = shuffle_y(y, meta, mode, rng)
                    null_pred = model_predict_oof(x, yn, meta, split)
                    nsumm, _ = metric_rows(yn, null_pred, view_id, split)
                    null_scores.append(nsumm["mean_spearman"])
                    null_rows.append(
                        {
                            "view_id": view_id,
                            "split": split,
                            "mode": mode,
                            "rep": rep,
                            "null_mean_spearman": nsumm["mean_spearman"],
                            "null_S4_spearman": nsumm["S4_spearman"],
                            "null_positive_spearman_targets": nsumm["positive_spearman_targets"],
                        }
                    )
            null_arr = np.asarray(null_scores, dtype=np.float64)
            summ["null_mean_spearman_median"] = float(np.median(null_arr))
            summ["null_mean_spearman_p90"] = float(np.quantile(null_arr, 0.90))
            summ["null_dominance"] = float(np.mean(summ["mean_spearman"] > null_arr))
            summ["representation_gate"] = bool(
                summ["mean_spearman"] > 0.05
                and summ["positive_spearman_targets"] >= 4
                and summ["null_dominance"] >= 0.85
            )
            summary_rows.append(summ)
            target_rows.extend(targ)
    return pd.DataFrame(summary_rows), pd.DataFrame(target_rows), pd.DataFrame(null_rows), preds


def fit_predict_test_blocks(
    train_blocks: dict[str, pd.DataFrame],
    test_blocks: dict[str, pd.DataFrame],
    target_df: pd.DataFrame,
    summary: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    if summary.empty:
        best_view = "human_full"
        best_split = "subject_holdout"
    else:
        best = summary.sort_values(
            ["representation_gate", "null_dominance", "mean_spearman", "S4_spearman"],
            ascending=[False, False, False, False],
        ).iloc[0]
        best_view = str(best["view_id"])
        best_split = str(best["split"])
    y = target_df[[f"{t}_logit_residual" for t in TARGETS]].to_numpy(dtype=np.float64)
    x_train = ensure_numeric(
        train_blocks[best_view].drop(columns=["dateblock_group", "subject_id", "split", "sleep_start", "sleep_end"], errors="ignore")
    )
    x_test = ensure_numeric(
        test_blocks[best_view].drop(columns=["dateblock_group", "subject_id", "split", "sleep_start", "sleep_end"], errors="ignore")
    )
    x_test = x_test.reindex(columns=x_train.columns, fill_value=0.0)
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=35.0))
    model.fit(x_train, y)
    pred = model.predict(x_test)
    out = test_blocks[best_view][["dateblock_group", "subject_id", "split", "n_rows", "block_order", "sleep_start", "sleep_end"]].copy()
    for i, target in enumerate(TARGETS):
        out[f"pred_{target}_logit_residual"] = pred[:, i]
    return out, f"{best_view}/{best_split}"


def candidate_alignment(test_blocks: pd.DataFrame) -> pd.DataFrame:
    current, meta = load_current_and_meta()
    block_pred = test_blocks.set_index("dateblock_group")["pred_S4_logit_residual"].to_dict()
    rows: list[dict[str, Any]] = []
    sources = {
        "E299_parent": E299_PARENT,
        "E300_ready_rejected": E300_READY,
        "E303_best_rejected": E303_BEST,
    }
    current_logits = logit(current[TARGETS].to_numpy(dtype=np.float64))
    for name, path in sources.items():
        if not path.exists():
            continue
        pred = load_sub(path, current).sort_values(KEYS).reset_index(drop=True)
        delta = logit(pred[TARGETS].to_numpy(dtype=np.float64)) - current_logits
        s4 = delta[:, TARGETS.index("S4")]
        tmp = meta[["dateblock_group", "subject_id"]].copy()
        tmp["s4_signed_sum"] = s4
        tmp["s4_abs_sum"] = np.abs(s4)
        block = (
            tmp.groupby(["dateblock_group", "subject_id"], as_index=False)
            .agg(s4_signed_sum=("s4_signed_sum", "sum"), s4_abs_sum=("s4_abs_sum", "sum"), active_rows=("s4_abs_sum", lambda x: int(np.sum(np.asarray(x) > 1.0e-12))))
        )
        block["pred_S4_logit_residual"] = block["dateblock_group"].map(block_pred).fillna(0.0)
        active = block["s4_abs_sum"].to_numpy(dtype=np.float64) > 1.0e-12
        align_signed = spearman_safe(block["s4_signed_sum"].to_numpy(), block["pred_S4_logit_residual"].to_numpy())
        align_abs = spearman_safe(block["s4_abs_sum"].to_numpy(), np.abs(block["pred_S4_logit_residual"].to_numpy()))
        active_pred = float(block.loc[active, "pred_S4_logit_residual"].mean()) if active.any() else 0.0
        inactive_pred = float(block.loc[~active, "pred_S4_logit_residual"].mean()) if (~active).any() else 0.0
        rows.append(
            {
                "source": name,
                "path": rel(path),
                "n_active_blocks": int(active.sum()),
                "n_active_rows": int(block.loc[active, "active_rows"].sum()) if active.any() else 0,
                "signed_alignment_spearman": align_signed,
                "abs_alignment_spearman": align_abs,
                "active_pred_S4_mean": active_pred,
                "inactive_pred_S4_mean": inactive_pred,
                "active_minus_inactive_pred_S4": active_pred - inactive_pred,
                "id07_b9_pred_S4": float(block.loc[block["dateblock_group"].eq("id07_b9"), "pred_S4_logit_residual"].iloc[0])
                if block["dateblock_group"].eq("id07_b9").any()
                else np.nan,
                "id07_b9_s4_signed_sum": float(block.loc[block["dateblock_group"].eq("id07_b9"), "s4_signed_sum"].iloc[0])
                if block["dateblock_group"].eq("id07_b9").any()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def annotate_test_blocks(test_blocks: pd.DataFrame, block_views: dict[str, pd.DataFrame]) -> pd.DataFrame:
    out = test_blocks.copy()
    story_block = block_views.get("story_episode")
    if story_block is None:
        return out
    story_cols = [c for c in story_block.columns if c.startswith("mean__story__") or c.startswith("mean__episode__")]
    story_map = story_block[["dateblock_group", *story_cols]].copy()
    out = out.merge(story_map, on="dateblock_group", how="left", validate="one_to_one")
    labels = []
    for _, row in out.iterrows():
        vals = row[story_cols].astype(float) if story_cols else pd.Series(dtype=float)
        if len(vals) == 0:
            labels.append("")
            continue
        top = vals.sort_values(ascending=False).head(3)
        labels.append("; ".join(f"{idx.replace('mean__', '')}:{val:.2f}" for idx, val in top.items()))
    out["top_human_story_scores"] = labels
    return out


def write_report(summary: pd.DataFrame, target: pd.DataFrame, nulls: pd.DataFrame, test_blocks: pd.DataFrame, alignment: pd.DataFrame, best_view: str) -> None:
    gated = summary[summary["representation_gate"]].copy() if "representation_gate" in summary.columns else pd.DataFrame()
    top_pos = test_blocks.sort_values("pred_S4_logit_residual", ascending=False).head(12)
    top_neg = test_blocks.sort_values("pred_S4_logit_residual").head(12)
    s4_targets = target[target["target"].eq("S4")].sort_values("spearman", ascending=False)
    lines = [
        "# E304 Hidden Block-State JEPA Probe",
        "",
        "Public LB는 사용하지 않았다. 목표는 raw human diary context에서 hidden subject/dateblock target state가 복원되는지 확인하는 것이다.",
        "",
        "## Question",
        "",
        "S4 mask-surgery가 실패한 이유가 placement 문제라면, 좋은 placement는 subject/dateblock 단위의 Q/S residual state로 먼저 복원되어야 한다. E304는 context=생활로그 diary block, target=subject prior를 제거한 block target-rate representation으로 둔 JEPA-style 실험이다.",
        "",
        "## Summary",
        "",
        md_table(summary.sort_values(["representation_gate", "null_dominance", "mean_spearman"], ascending=[False, False, False]), n=20),
        "",
        "## S4 Target Metrics",
        "",
        md_table(s4_targets, n=20),
        "",
        "## Candidate Alignment With Predicted S4 Block State",
        "",
        md_table(alignment.sort_values("active_minus_inactive_pred_S4", ascending=False) if not alignment.empty else alignment, n=20),
        "",
        "## Top Positive Predicted S4 Blocks",
        "",
        md_table(
            top_pos[
                [
                    "dateblock_group",
                    "subject_id",
                    "sleep_start",
                    "sleep_end",
                    "pred_S4_logit_residual",
                    "pred_Q3_logit_residual",
                    "top_human_story_scores",
                ]
            ],
            n=12,
        ),
        "",
        "## Top Negative Predicted S4 Blocks",
        "",
        md_table(
            top_neg[
                [
                    "dateblock_group",
                    "subject_id",
                    "sleep_start",
                    "sleep_end",
                    "pred_S4_logit_residual",
                    "pred_Q3_logit_residual",
                    "top_human_story_scores",
                ]
            ],
            n=12,
        ),
        "",
        "## Decision",
        "",
    ]
    if gated.empty:
        lines.extend(
            [
                "- No block-state representation passes the conservative null dominance gate.",
                "- This means the current raw human diary context does not yet recover hidden target-rate state strongly enough to justify a new S4 placement submission.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one block-state representation passes the null dominance gate.",
                "- This is not a submission by itself. The next step would be a tiny block-prior materializer with E301-style large-null confirmation.",
            ]
        )
    lines.extend(
        [
            f"- Best deployment view for test block annotation: `{best_view}`.",
            "- Candidate alignment columns should be read as diagnostics only. Positive alignment would support a placement story; weak or negative alignment explains why S4 mask edits fail matched nulls.",
            "",
            "## Outputs",
            "",
            f"- `{rel(SUMMARY_OUT)}`",
            f"- `{rel(TARGET_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(TEST_BLOCK_OUT)}`",
            f"- `{rel(ALIGN_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, row_views, _story_meta = build_row_views()
    block_views_all = {view: aggregate_blocks(base, frame) for view, frame in row_views.items()}
    target_df = block_target_residuals(base)

    train_blocks: dict[str, pd.DataFrame] = {}
    test_blocks: dict[str, pd.DataFrame] = {}
    for view, block_frame in block_views_all.items():
        train_part = block_frame[block_frame["split"].eq("train")].merge(
            target_df[["dateblock_group", "subject_id"]],
            on=["dateblock_group", "subject_id"],
            how="inner",
            validate="one_to_one",
        )
        train_part = train_part.merge(target_df, on=["dateblock_group", "subject_id"], how="left", validate="one_to_one")
        feature_cols = [
            c
            for c in train_part.columns
            if c not in set(["n_rows_target", *[f"{t}_block_rate" for t in TARGETS], *[f"{t}_subject_prior" for t in TARGETS], *[f"{t}_logit_residual" for t in TARGETS], *[f"{t}_prob_residual" for t in TARGETS]])
        ]
        train_blocks[view] = train_part[feature_cols].reset_index(drop=True)
        test_blocks[view] = block_frame[block_frame["split"].eq("test")].reset_index(drop=True)

    target_for_eval = target_df.sort_values("dateblock_group").reset_index(drop=True)
    for view in list(train_blocks):
        train_blocks[view] = train_blocks[view].sort_values("dateblock_group").reset_index(drop=True)
    summary, target_metrics, nulls, _preds = evaluate_views(train_blocks, target_for_eval)
    test_pred, best_view = fit_predict_test_blocks(train_blocks, test_blocks, target_for_eval, summary)
    test_pred = annotate_test_blocks(test_pred, test_blocks)
    alignment = candidate_alignment(test_pred)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_metrics.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    test_pred.to_csv(TEST_BLOCK_OUT, index=False)
    alignment.to_csv(ALIGN_OUT, index=False)
    write_report(summary, target_metrics, nulls, test_pred, alignment, best_view)

    gates = int(summary["representation_gate"].sum()) if "representation_gate" in summary.columns else 0
    print(f"views={len(train_blocks)} train_blocks={len(target_for_eval)} gates={gates} best={best_view}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
