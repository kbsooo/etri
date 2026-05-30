from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


OUT_DIR = Path("analysis_outputs")
FEATURE_PATH = OUT_DIR / "e262_human_social_day_features.parquet"
SELECTED_ROWS_PATH = OUT_DIR / "e257_e247_e256_cell_contrast_selected_rows.csv"
TOP_CELLS_PATH = OUT_DIR / "e260_post_e247_next_slot_top_cells.csv"

REPORT_PATH = OUT_DIR / "e263_human_social_public_tail_context_report.md"
GROUP_CONTEXT_PATH = OUT_DIR / "e263_human_social_public_tail_group_context.csv"
ROW_CONTEXT_PATH = OUT_DIR / "e263_human_social_public_tail_row_context.csv"
FEATURE_RANK_PATH = OUT_DIR / "e263_human_social_public_tail_feature_rank.csv"


MANUAL_FEATURES = [
    "human_social_overstim_late",
    "human_late_cognitive_load",
    "human_routine_anchor",
    "human_commute_mobility",
    "human_physical_fatigue",
    "human_sleep_onset_risk",
    "human_public_social_presence",
    "usage_late_call_time",
    "usage_late_social_msg_time",
    "usage_late_search_browser_time",
    "usage_presleep_search_browser_time",
    "usage_presleep_social_msg_time",
    "usage_presleep_media_time",
    "usage_presleep_religion_routine_time",
    "usage_day_religion_routine_time",
    "charge_m_charging_mean_presleep",
    "screen_m_screen_use_mean_late",
    "screen_m_screen_use_mean_presleep",
    "gps_speed_mean_deepnight",
    "gps_speed_mean_evening",
    "pedo_step_sum_presleep",
    "hr_heart_rate_mean_mean_day",
    "light_m_light_mean_presleep",
    "wlight_light_mean_presleep",
    "ambience_music_late",
    "ambience_speech_morning",
    "ambience_inside_public_afternoon",
]


def robust_z(s: pd.Series, ref: pd.Series) -> pd.Series:
    ref = pd.to_numeric(ref, errors="coerce")
    med = ref.median()
    mad = (ref - med).abs().median()
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale < 1e-12:
        scale = ref.std(ddof=0)
    if not np.isfinite(scale) or scale < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    z = (pd.to_numeric(s, errors="coerce") - med) / scale
    return z.clip(-20.0, 20.0)


def percentile_against_ref(value: float, ref: pd.Series) -> float:
    ref = pd.to_numeric(ref, errors="coerce").dropna()
    if len(ref) == 0 or not np.isfinite(value):
        return np.nan
    return float((ref <= value).mean())


def make_markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_none_"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v) for v in row] for row in view.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    features = pd.read_parquet(FEATURE_PATH)
    selected = pd.read_csv(SELECTED_ROWS_PATH)
    top_cells = pd.read_csv(TOP_CELLS_PATH)

    features["lifelog_date"] = pd.to_datetime(features["lifelog_date"]).dt.strftime("%Y-%m-%d")
    selected["lifelog_date"] = pd.to_datetime(selected["lifelog_date"]).dt.strftime("%Y-%m-%d")
    top_cells["lifelog_date"] = pd.to_datetime(top_cells["lifelog_date"]).dt.strftime("%Y-%m-%d")

    key_cols = ["row_idx", "subject_id", "lifelog_date", "group"]
    selected_key = selected[key_cols].drop_duplicates()
    merged = selected_key.merge(
        features,
        on=["subject_id", "lifelog_date"],
        how="left",
        validate="many_to_one",
    )
    if merged["split"].isna().any():
        missing = merged[merged["split"].isna()][key_cols]
        raise RuntimeError(f"Missing human-social features for selected rows:\n{missing}")

    numeric_cols = [
        c
        for c in features.columns
        if c not in {"subject_id", "sleep_date", "lifelog_date", "lifelog_date_only", "split"}
        and pd.api.types.is_numeric_dtype(features[c])
    ]
    feature_cols = [c for c in MANUAL_FEATURES if c in features.columns]
    feature_cols += [c for c in numeric_cols if c.startswith("human_") and c not in feature_cols]
    feature_cols = list(dict.fromkeys(feature_cols))

    test_ref = features[features["split"] == "test"].copy()
    row_records = []
    for _, row in merged.iterrows():
        subject_ref = test_ref[test_ref["subject_id"] == row["subject_id"]]
        for feat in feature_cols:
            value = row[feat]
            row_records.append(
                {
                    "row_idx": row["row_idx"],
                    "subject_id": row["subject_id"],
                    "lifelog_date": row["lifelog_date"],
                    "group": row["group"],
                    "feature": feat,
                    "value": value,
                    "test_robust_z": robust_z(pd.Series([value]), test_ref[feat]).iloc[0],
                    "subject_test_percentile": percentile_against_ref(value, subject_ref[feat]),
                    "global_test_percentile": percentile_against_ref(value, test_ref[feat]),
                }
            )
    row_context = pd.DataFrame(row_records)

    group_context = (
        row_context.groupby(["group", "feature"], as_index=False)
        .agg(
            n=("row_idx", "nunique"),
            mean_value=("value", "mean"),
            mean_test_robust_z=("test_robust_z", "mean"),
            mean_abs_test_robust_z=("test_robust_z", lambda x: float(np.nanmean(np.abs(x)))),
            mean_subject_test_percentile=("subject_test_percentile", "mean"),
            mean_global_test_percentile=("global_test_percentile", "mean"),
        )
        .sort_values(["group", "mean_abs_test_robust_z"], ascending=[True, False])
    )

    group_pivot = group_context.pivot(index="feature", columns="group", values="mean_test_robust_z")
    for group in ["common", "e247_only", "e256_only"]:
        if group not in group_pivot.columns:
            group_pivot[group] = np.nan
    feature_rank = group_pivot.reset_index()
    feature_rank["e256_minus_e247only_z"] = feature_rank["e256_only"] - feature_rank["e247_only"]
    feature_rank["e256_minus_common_z"] = feature_rank["e256_only"] - feature_rank["common"]
    feature_rank["e256_separation_score"] = (
        feature_rank["e256_minus_e247only_z"].abs().fillna(0)
        + feature_rank["e256_minus_common_z"].abs().fillna(0)
    )
    feature_rank = feature_rank.sort_values("e256_separation_score", ascending=False)

    top_e256_rows = top_cells[
        (top_cells["pair_id"] == "e256_vs_e247")
        & (top_cells["e257_group"] == "e256_only")
    ][
        [
            "row_idx",
            "target",
            "subject_id",
            "lifelog_date",
            "action",
            "prob_delta",
            "swing",
            "expected_focus",
            "support_prob_focus",
        ]
    ].copy()
    top_e256_rows["lifelog_date"] = pd.to_datetime(top_e256_rows["lifelog_date"]).dt.strftime("%Y-%m-%d")

    focus_feats = feature_rank.head(12)["feature"].tolist()
    focus_context = row_context[
        row_context["row_idx"].isin(top_e256_rows["row_idx"]) & row_context["feature"].isin(focus_feats)
    ].copy()
    focus_context = focus_context.sort_values(["row_idx", "test_robust_z"], key=lambda s: s.abs() if s.name == "test_robust_z" else s)

    ROW_CONTEXT_PATH.write_text("", encoding="utf-8")
    row_context.to_csv(ROW_CONTEXT_PATH, index=False)
    group_context.to_csv(GROUP_CONTEXT_PATH, index=False)
    feature_rank.to_csv(FEATURE_RANK_PATH, index=False)

    e256_top_features = feature_rank.head(15)[
        [
            "feature",
            "common",
            "e247_only",
            "e256_only",
            "e256_minus_e247only_z",
            "e256_minus_common_z",
            "e256_separation_score",
        ]
    ]

    e256_group_focus = group_context[group_context["group"] == "e256_only"].sort_values(
        "mean_abs_test_robust_z", ascending=False
    ).head(15)

    common_group_focus = group_context[group_context["group"] == "common"].sort_values(
        "mean_abs_test_robust_z", ascending=False
    ).head(8)

    report = f"""# E263 Human/Social Context Around Public-Tail Q3 Cells

## Question

E256 lost to E247 on public. Are the four E256-only high-amplitude Q3 cells just numeric smoothing artifacts, or do they sit on recognizable human lifestyle states?

This does not use hidden public labels. It joins E257/E260 Q3 cell groups to the E262 human-social day representation.

## Main Read

- The E256-only group is tiny (`4` rows), so this is a hypothesis generator, not proof.
- The useful object is a JEPA target candidate: predict public-tail cell risk from human diary context, rather than predicting raw app/sensor values.
- If these rows have coherent lifestyle signatures, the next JEPA experiment should mask lifestyle families and predict `Q3 tail-risk / smoothing-validity` as a latent target.

## Top E256-Separating Human/Social Features

{make_markdown_table(e256_top_features, 15)}

## E256-Only Group: Largest Lifestyle Outliers

{make_markdown_table(e256_group_focus[['feature','n','mean_value','mean_test_robust_z','mean_abs_test_robust_z','mean_subject_test_percentile','mean_global_test_percentile']], 15)}

## Common E247/E256 Core: Lifestyle Contrast

{make_markdown_table(common_group_focus[['feature','n','mean_value','mean_test_robust_z','mean_abs_test_robust_z','mean_subject_test_percentile','mean_global_test_percentile']], 8)}

## Four E256-Only Public-Swing Cells

{make_markdown_table(top_e256_rows, 10)}

## Interpretation

E247/E256 should no longer be treated as only a prediction-smoothing story. The public-sensitive Q3 cells can now be inspected as human-day states: late social/contact load, presleep cognitive load, routine/charging stability, commute or deep-night movement, and sensor-measured fatigue.

The next high-value JEPA version should use:

1. context: non-target human diary features from E262, with masks by lifestyle family.
2. target representation: Q3 cell-tail state from E247/E256/E260, not raw Q3 label or raw app reconstruction.
3. LeJEPA health checks: subject/date-block stress, train/test lifestyle shift, and public-anchor group contrast.

## Falsification Rule

This branch dies if an OOF analogue cannot predict held-out Q3 tail-risk better than subject/date priors, or if the learned lifestyle-tail latent only predicts subject identity/train-test split.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {GROUP_CONTEXT_PATH}")
    print(f"wrote {ROW_CONTEXT_PATH}")
    print(f"wrote {FEATURE_RANK_PATH}")


if __name__ == "__main__":
    main()
