#!/usr/bin/env python3
"""E281: JEPA-style story-state row selector audit.

E280 found stories that look transferable, but direct public-boundary edits are
blocked by E279. This audit converts the top stories into a target-free JEPA
problem:

    context families -> hidden story-state representation

Then it asks whether the predicted story state helps label CV more than matched
row/subject/dateblock shuffles. No public LB is used and no submission is made.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

E273_FEATURES = OUT / "e273_human_diary_state_jepa_audit_features.parquet"
E280_SUMMARY = OUT / "e280_story_transfer_alignment_summary.csv"
SOCIAL_FEATURES = OUT / "e268_human_social_story_features.parquet"
CASH_FEATURES = OUT / "e270_payday_cashflow_story_features.parquet"

SUMMARY_OUT = OUT / "e281_story_state_jepa_row_selector_summary.csv"
TARGET_OUT = OUT / "e281_story_state_jepa_row_selector_target_detail.csv"
NULL_OUT = OUT / "e281_story_state_jepa_row_selector_nulls.csv"
REPORT_OUT = OUT / "e281_story_state_jepa_row_selector_report.md"

RNG_SEED = 20260531 + 281
TOP_N = 6
N_REPS = 25


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, n: int = 25, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def prep_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    base = prep_dates(pd.read_parquet(E273_FEATURES))
    base = base.sort_values(KEYS).reset_index(drop=True)
    stories = pd.read_csv(E280_SUMMARY).head(TOP_N).copy()
    feature_frames = {
        "human_social": prep_dates(pd.read_parquet(SOCIAL_FEATURES)).sort_values(KEYS).reset_index(drop=True),
        "cashflow": prep_dates(pd.read_parquet(CASH_FEATURES)).sort_values(KEYS).reset_index(drop=True),
    }
    for source, frame in feature_frames.items():
        if not base[KEYS].equals(frame[KEYS]):
            raise RuntimeError(f"{source} story features do not align with E273 features")
    return base, stories, feature_frames


def base_label_matrix(df: pd.DataFrame) -> pd.DataFrame:
    pieces = []
    for col in ["weekday", "is_weekend", "subject_order", "lifelog_dom", "lifelog_month"]:
        if col in df.columns:
            pieces.append(pd.to_numeric(df[col], errors="coerce").fillna(0.0).rename(col))
    if "weekday_sin" in df.columns:
        pieces.append(pd.to_numeric(df["weekday_sin"], errors="coerce").fillna(0.0))
    if "weekday_cos" in df.columns:
        pieces.append(pd.to_numeric(df["weekday_cos"], errors="coerce").fillna(0.0))
    subj = pd.get_dummies(df["subject_id"].astype(str), prefix="subj", dtype=float)
    mat = pd.concat(pieces + [subj], axis=1)
    return mat.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def context_columns(df: pd.DataFrame, story_id: str, mapped_family: str) -> list[str]:
    blocked = {story_id, f"{story_id}_subj_z", f"{story_id}_abs_subj_z", f"{story_id}_active"}
    non_features = set(KEYS + TARGETS + ["split", "dateblock_group", "subject_id"])
    cols = []
    for col in df.columns:
        if col in non_features or col in blocked:
            continue
        if mapped_family and mapped_family in col:
            continue
        if story_id in col:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        cols.append(col)
    return cols


def story_score(story_row: pd.Series, feature_frames: dict[str, pd.DataFrame]) -> tuple[str, np.ndarray]:
    frame = feature_frames[str(story_row["source"])]
    story_id = str(story_row["story_id"])
    candidates = [f"{story_id}_subj_z", story_id, f"{story_id}_active"]
    for col in candidates:
        if col in frame.columns:
            score = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
            return col, score.to_numpy(dtype=np.float64)
    raise RuntimeError(f"missing story score for {story_id}")


def split_groups(df: pd.DataFrame, split_name: str) -> pd.Series:
    if split_name == "subject5":
        return df["subject_id"].astype(str)
    if split_name == "dateblock5":
        return df["dateblock_group"].astype(str)
    raise ValueError(split_name)


def make_folds(groups: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    n_groups = groups.nunique()
    n_splits = min(5, int(n_groups))
    if n_splits < 2:
        raise RuntimeError("not enough groups for GroupKFold")
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=groups))


def ridge_oof_state(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    for train_idx, valid_idx in make_folds(groups):
        model = make_pipeline(StandardScaler(), Ridge(alpha=8.0))
        model.fit(x.iloc[train_idx], y[train_idx])
        pred[valid_idx] = model.predict(x.iloc[valid_idx])
    return pred


def cv_logloss_with_extra(x_base: pd.DataFrame, extra: np.ndarray | None, y: np.ndarray, groups: pd.Series) -> float:
    preds = np.zeros(len(y), dtype=np.float64)
    folds = make_folds(groups)
    if extra is None:
        x_all = x_base
    else:
        x_all = x_base.copy()
        x_all["story_state_pred"] = np.asarray(extra, dtype=np.float64)

    for train_idx, valid_idx in folds:
        y_train = y[train_idx]
        if len(np.unique(y_train)) < 2:
            prior = float(np.mean(y_train))
            preds[valid_idx] = prior
            continue
        model = make_pipeline(StandardScaler(), LogisticRegression(C=0.35, max_iter=1000, solver="lbfgs"))
        model.fit(x_all.iloc[train_idx], y_train)
        preds[valid_idx] = model.predict_proba(x_all.iloc[valid_idx])[:, 1]
    return float(log_loss(y, clip_prob(preds), labels=[0, 1]))


def shuffled_feature(values: np.ndarray, mode: str, groups: pd.Series, rng: np.random.Generator) -> np.ndarray:
    out = np.asarray(values, dtype=np.float64).copy()
    if mode == "row":
        return out[rng.permutation(len(out))]
    if mode in {"subject", "dateblock"}:
        shuffled = out.copy()
        for _, idx in groups.groupby(groups).groups.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            shuffled[idx_arr] = out[idx_arr][rng.permutation(len(idx_arr))]
        return shuffled
    raise ValueError(mode)


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def run_story_audit(base: pd.DataFrame, story_row: pd.Series, feature_frames: dict[str, pd.DataFrame]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    score_col, score = story_score(story_row, feature_frames)
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    y_state = score[train_mask]
    ctx_cols = context_columns(base, str(story_row["story_id"]), str(story_row["mapped_family"]))
    x_context = base.loc[train_mask, ctx_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0).reset_index(drop=True)
    x_label = base_label_matrix(train)

    summary_rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []

    for split_name in ["subject5", "dateblock5"]:
        groups = split_groups(train, split_name).reset_index(drop=True)
        state_pred = ridge_oof_state(x_context, y_state, groups)
        state_r2 = float(r2_score(y_state, state_pred))
        state_corr = float(np.corrcoef(y_state, state_pred)[0, 1]) if np.std(state_pred) > 1.0e-9 and np.std(y_state) > 1.0e-9 else 0.0

        target_deltas = []
        target_base_losses = []
        target_state_losses = []
        target_best = ""
        for target in TARGETS:
            y = train[target].to_numpy(dtype=int)
            base_loss = cv_logloss_with_extra(x_label, None, y, groups)
            state_loss = cv_logloss_with_extra(x_label, state_pred, y, groups)
            delta = state_loss - base_loss
            target_deltas.append(delta)
            target_base_losses.append(base_loss)
            target_state_losses.append(state_loss)
            target_rows.append(
                {
                    "story_id": story_row["story_id"],
                    "source": story_row["source"],
                    "mapped_family": story_row["mapped_family"],
                    "split": split_name,
                    "target": target,
                    "base_loss": base_loss,
                    "state_loss": state_loss,
                    "delta_logloss": delta,
                    "state_oof_r2": state_r2,
                    "state_oof_corr": state_corr,
                    "context_cols": len(ctx_cols),
                }
            )
        target_best = TARGETS[int(np.argmin(target_deltas))]
        actual_delta_mean = float(np.mean(target_deltas))
        actual_delta_best = float(np.min(target_deltas))

        rng = np.random.default_rng(stable_seed(story_row["story_id"], split_name))
        null_deltas = []
        for mode in ["row", "subject", "dateblock"]:
            mode_groups = split_groups(train, "subject5" if mode == "subject" else "dateblock5")
            for rep in range(N_REPS):
                shuffled = shuffled_feature(state_pred, mode, mode_groups.reset_index(drop=True), rng)
                losses = []
                for target in TARGETS:
                    y = train[target].to_numpy(dtype=int)
                    base_loss = target_base_losses[TARGETS.index(target)]
                    null_loss = cv_logloss_with_extra(x_label, shuffled, y, groups)
                    losses.append(null_loss - base_loss)
                null_delta = float(np.mean(losses))
                null_deltas.append(null_delta)
                null_rows.append(
                    {
                        "story_id": story_row["story_id"],
                        "source": story_row["source"],
                        "mapped_family": story_row["mapped_family"],
                        "split": split_name,
                        "mode": mode,
                        "rep": rep,
                        "null_delta_mean": null_delta,
                    }
                )

        null_arr = np.asarray(null_deltas, dtype=np.float64)
        dominance = float(np.mean(actual_delta_mean < null_arr)) if len(null_arr) else np.nan
        summary_rows.append(
            {
                "story_id": story_row["story_id"],
                "source": story_row["source"],
                "mapped_family": story_row["mapped_family"],
                "score_col": score_col,
                "split": split_name,
                "context_cols": len(ctx_cols),
                "state_oof_r2": state_r2,
                "state_oof_corr": state_corr,
                "actual_delta_mean": actual_delta_mean,
                "actual_delta_best": actual_delta_best,
                "actual_best_target": target_best,
                "null_q20": float(np.quantile(null_arr, 0.20)),
                "null_median": float(np.median(null_arr)),
                "null_best": float(np.min(null_arr)),
                "dominance": dominance,
                "placebo_adjusted_vs_median": actual_delta_mean - float(np.median(null_arr)),
                "placebo_adjusted_vs_best": actual_delta_mean - float(np.min(null_arr)),
                "jepa_story_gate": bool(state_r2 > 0.10 and actual_delta_mean < 0.0 and dominance >= 0.80),
            }
        )

    return summary_rows, target_rows, null_rows


def write_report(summary: pd.DataFrame, target_detail: pd.DataFrame, nulls: pd.DataFrame) -> None:
    gate = summary[summary["jepa_story_gate"]].copy()
    both = (
        gate.groupby("story_id")["split"].nunique().reset_index(name="gate_split_count").query("gate_split_count >= 2")
        if not gate.empty
        else pd.DataFrame(columns=["story_id", "gate_split_count"])
    )
    lines = [
        "# E281 Story-State JEPA Row Selector Audit",
        "",
        "## Question",
        "",
        "Can the strongest human/social stories become target-free JEPA representations whose row placement survives local null checks?",
        "",
        "## Method",
        "",
        f"- Top E280 stories tested: `{summary['story_id'].nunique()}`",
        f"- For each story, predict its subject-normalized story score from all other numeric diary-state context columns, excluding the mapped family.",
        "- Evaluate predicted story state as one extra feature on a calendar/subject baseline for all 7 labels.",
        f"- Matched nulls: `{N_REPS}` row, subject, and dateblock shuffles per story/split.",
        "- No public LB, no submission.",
        "",
        "## Summary",
        "",
        f"- story/split rows: `{len(summary)}`",
        f"- JEPA story gate rows: `{len(gate)}`",
        f"- stories passing both subject and dateblock gates: `{len(both)}`",
        "",
        "## Story/Split Results",
        "",
        md_table(
            summary[
                [
                    "story_id",
                    "mapped_family",
                    "split",
                    "state_oof_r2",
                    "state_oof_corr",
                    "actual_delta_mean",
                    "actual_delta_best",
                    "actual_best_target",
                    "null_median",
                    "null_best",
                    "dominance",
                    "jepa_story_gate",
                ]
            ].sort_values(["jepa_story_gate", "actual_delta_mean"], ascending=[False, True]),
            n=30,
        ),
        "",
        "## Best Target Rows",
        "",
        md_table(
            target_detail.sort_values("delta_logloss")[
                [
                    "story_id",
                    "mapped_family",
                    "split",
                    "target",
                    "delta_logloss",
                    "state_oof_r2",
                    "state_oof_corr",
                ]
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(both):
        names = ", ".join(both["story_id"].astype(str).tolist())
        lines.append(f"Stories passing both local gates: `{names}`. These still need a separate materialization governor before any public LB use.")
    elif len(gate):
        lines.append("Some story/split gates pass, but no story passes both subject and dateblock gates. Treat them as directional diagnostics, not submission candidates.")
    else:
        lines.append("No top story passed the JEPA row-selector gate. The social stories remain useful for interpretation, but direct JEPA-story materialization is blocked for now.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "- `e281_story_state_jepa_row_selector_summary.csv`",
            "- `e281_story_state_jepa_row_selector_target_detail.csv`",
            "- `e281_story_state_jepa_row_selector_nulls.csv`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    base, stories, feature_frames = load_frames()
    all_summary: list[dict[str, object]] = []
    all_targets: list[dict[str, object]] = []
    all_nulls: list[dict[str, object]] = []
    for _, story_row in stories.iterrows():
        summary_rows, target_rows, null_rows = run_story_audit(base, story_row, feature_frames)
        all_summary.extend(summary_rows)
        all_targets.extend(target_rows)
        all_nulls.extend(null_rows)

    summary = pd.DataFrame(all_summary).sort_values(["jepa_story_gate", "actual_delta_mean"], ascending=[False, True])
    target_detail = pd.DataFrame(all_targets).sort_values("delta_logloss")
    nulls = pd.DataFrame(all_nulls)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(summary, target_detail, nulls)

    print(f"stories={summary['story_id'].nunique()}")
    print(f"story_split_rows={len(summary)}")
    print(f"jepa_story_gate_rows={int(summary['jepa_story_gate'].sum())}")
    both = summary[summary["jepa_story_gate"]].groupby("story_id")["split"].nunique()
    print(f"both_split_gate_stories={int((both >= 2).sum()) if len(both) else 0}")
    print(f"best_delta={summary['actual_delta_mean'].min():.9f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
