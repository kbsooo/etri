#!/usr/bin/env python3
"""E298: public-free atlas of materialization outcomes.

The recent human/social/JEPAlike branch produced many plausible stories and
many candidate submissions, but public LB should not be used as the filter.
This script aggregates every current-anchor governor summary that already has
matched-null stress and asks a narrower question:

    Where do candidate translations fail locally?

The output is not a submission generator. It is a map of which story families
are selector-visible, which are null-rare, which are both, and whether any row
or target region is ready without spending public LB.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

GOVERNOR_FILES = [
    OUT / "e279_public_free_governor_summary.csv",
    OUT / "e284_appentropy_decisive_cell_jepa_governor_summary.csv",
    OUT / "e285_e247_residual_human_state_governor_summary.csv",
    OUT / "e286_e247_preserve_avoid_governor_summary.csv",
    OUT / "e287_train_supervised_row_alignment_governor_summary.csv",
    OUT / "e289_target_specific_lifestyle_slice_governor_summary.csv",
    OUT / "e290_lifestyle_row_placement_governor_summary.csv",
    OUT / "e291_lifestyle_block_state_governor_summary.csv",
    OUT / "e292_contrastive_lifestyle_governor_summary.csv",
    OUT / "e293_s4_lownull_governor_summary.csv",
    OUT / "e297_episode_state_materializer_governor.csv",
]

ALL_OUT = OUT / "e298_materialization_outcome_all.csv"
FAMILY_OUT = OUT / "e298_materialization_outcome_family_summary.csv"
NEAR_MISS_OUT = OUT / "e298_materialization_outcome_near_miss.csv"
QUADRANT_OUT = OUT / "e298_materialization_outcome_quadrants.csv"
REPORT_OUT = OUT / "e298_materialization_outcome_report.md"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def experiment_id(path: Path) -> str:
    match = re.search(r"(e\d+)", path.name)
    return match.group(1) if match else "unknown"


def to_bool(value: Any) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y", "promote", "promote_candidate", "ready"}


def first_present(row: pd.Series, cols: list[str], default: str = "") -> str:
    for col in cols:
        if col in row.index and not pd.isna(row[col]):
            text = str(row[col])
            if text and text.lower() != "nan":
                return text
    return default


def num_col(df: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def bool_col(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index, dtype=bool)
    return df[col].map(to_bool).astype(bool)


def normalize(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    df = raw.copy()
    df["experiment"] = experiment_id(path)
    df["source_governor_file"] = rel(path)
    df["basename"] = df.get("basename", df.get("source_path", path.name)).astype(str)

    for col in [
        "actual_mean",
        "actual_p10",
        "actual_p90",
        "actual_beats_current_rate",
        "null_count",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "incremental_bad_axis_vs_current",
    ]:
        df[col] = num_col(df, col)

    for col in ["old_strict_promote", "strict_promote_gate", "public_free_submission_ready"]:
        df[col] = bool_col(df, col)

    if "promotion_decision" not in df.columns:
        df["promotion_decision"] = df.get("old_promotion_decision", "")
    if "final_decision" not in df.columns:
        df["final_decision"] = df.get("final_governor_decision", "")

    df["target_norm"] = df.apply(
        lambda r: first_present(r, ["target", "target_task", "target_kind"], default="multi"),
        axis=1,
    )
    df["family"] = df.apply(
        lambda r: first_present(
            r,
            [
                "episode",
                "rule_family",
                "contrast_policy_id",
                "policy_id",
                "parent_policy_id",
                "view_id",
                "feature_set",
                "action",
                "model",
                "split",
                "rule",
            ],
            default="unknown",
        ),
        axis=1,
    )
    df["story_axis"] = df.apply(
        lambda r: "/".join(
            [
                str(r["experiment"]),
                str(r["target_norm"]),
                str(r["family"]),
                first_present(r, ["rule", "action", "delta_mode", "policy"], default=""),
            ]
        ).rstrip("/"),
        axis=1,
    )

    promotion_text = df["promotion_decision"].astype(str).str.lower()
    final_text = df["final_decision"].astype(str).str.lower()

    df["selector_visible_strict"] = (
        df["old_strict_promote"]
        | df["strict_promote_gate"]
        | promotion_text.str.contains("promote", na=False)
        | final_text.str.contains("ready", na=False)
    )
    df["selector_visible_soft"] = (
        (df["actual_p90"] <= -5e-5)
        & (df["actual_beats_current_rate"].fillna(0.0) >= 0.70)
        & (df["incremental_bad_axis_vs_current"].fillna(1.0) <= 0.0)
    )
    df["selector_visible"] = df["selector_visible_strict"] | df["selector_visible_soft"]

    df["null_rare"] = df["null_strict_rate"].fillna(1.0) <= 0.10
    df["null_common"] = df["null_strict_rate"].fillna(1.0) >= 0.40
    df["p90_ok"] = df["p90_dominance"].fillna(0.0) >= 0.80
    df["mean_ok"] = df["mean_dominance"].fillna(0.0) >= 0.70
    df["worst_mode_ok"] = df["worst_mode_p90_dominance"].fillna(0.0) >= 0.55
    df["edge_ok"] = df["actual_p90"].fillna(1.0) <= -5e-5
    df["old_ready_rule"] = (
        df["selector_visible"]
        & df["null_rare"]
        & df["p90_ok"]
        & df["mean_ok"]
        & df["worst_mode_ok"]
        & df["edge_ok"]
    )

    df["readiness_defects"] = (
        (~df["selector_visible"]).astype(int)
        + (~df["null_rare"]).astype(int)
        + (~df["p90_ok"]).astype(int)
        + (~df["mean_ok"]).astype(int)
        + (~df["worst_mode_ok"]).astype(int)
        + (~df["edge_ok"]).astype(int)
    )

    df["readiness_distance"] = (
        np.maximum(0.0, df["null_strict_rate"].fillna(1.0) - 0.10)
        + np.maximum(0.0, 0.80 - df["p90_dominance"].fillna(0.0))
        + np.maximum(0.0, 0.70 - df["mean_dominance"].fillna(0.0))
        + np.maximum(0.0, 0.55 - df["worst_mode_p90_dominance"].fillna(0.0))
        + np.maximum(0.0, df["actual_p90"].fillna(0.01) + 5e-5) / 0.001
        + (~df["selector_visible"]).astype(float) * 0.50
    )

    conditions = [
        df["old_ready_rule"],
        df["selector_visible"] & df["null_rare"] & ~(df["p90_ok"] & df["mean_ok"] & df["worst_mode_ok"]),
        df["selector_visible"] & df["null_common"],
        df["selector_visible"] & ~df["null_rare"],
        ~df["selector_visible"] & df["null_rare"] & df["edge_ok"],
        ~df["selector_visible"] & df["null_rare"],
        df["edge_ok"],
    ]
    labels = [
        "ready_like",
        "visible_null_rare_but_weak_dominance",
        "visible_but_null_common",
        "visible_but_null_not_rare",
        "null_rare_edge_but_not_visible",
        "null_rare_but_no_selector_edge",
        "directional_edge_only",
    ]
    df["outcome_quadrant"] = np.select(conditions, labels, default="adverse_or_no_edge")

    df["failure_mode"] = np.select(
        [
            df["old_ready_rule"],
            df["selector_visible"] & df["null_common"],
            df["selector_visible"] & ~df["null_rare"],
            df["selector_visible"] & df["null_rare"] & ~df["p90_ok"],
            df["selector_visible"] & df["null_rare"] & ~df["mean_ok"],
            df["selector_visible"] & df["null_rare"] & ~df["worst_mode_ok"],
            ~df["selector_visible"] & df["null_rare"] & df["edge_ok"],
            ~df["selector_visible"] & df["null_rare"],
            df["edge_ok"],
        ],
        [
            "survives_all_public_free_gates",
            "matched_null_hallucination",
            "matched_null_not_rare",
            "p90_dominance_shortfall",
            "mean_dominance_shortfall",
            "mode_instability",
            "edge_not_seen_by_selector",
            "safe_but_too_small_or_wrong_sign",
            "edge_without_null_safety",
        ],
        default="no_local_edge",
    )
    return df


def md_table(df: pd.DataFrame, columns: list[str], n: int = 20) -> str:
    if df.empty:
        return "_없음_"
    view = df.loc[:, columns].head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
    view = view.fillna("").astype(str)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in view.to_numpy()]
    return "\n".join([header, sep, *rows])


def main() -> None:
    frames = []
    missing = []
    for path in GOVERNOR_FILES:
        if path.exists():
            frames.append(normalize(path))
        else:
            missing.append(rel(path))
    if not frames:
        raise SystemExit("No governor summaries found")

    all_df = pd.concat(frames, ignore_index=True, sort=False)
    all_df = all_df.sort_values(["readiness_defects", "readiness_distance", "actual_p90", "basename"])

    family = (
        all_df.groupby(["experiment", "target_norm", "family", "outcome_quadrant"], dropna=False)
        .agg(
            n=("basename", "count"),
            ready_like=("old_ready_rule", "sum"),
            selector_visible=("selector_visible", "sum"),
            null_rare=("null_rare", "sum"),
            best_actual_p90=("actual_p90", "min"),
            best_actual_mean=("actual_mean", "min"),
            median_null_strict_rate=("null_strict_rate", "median"),
            best_p90_dominance=("p90_dominance", "max"),
            best_mean_dominance=("mean_dominance", "max"),
            best_worst_mode_dominance=("worst_mode_p90_dominance", "max"),
            min_readiness_distance=("readiness_distance", "min"),
        )
        .reset_index()
        .sort_values(["ready_like", "selector_visible", "null_rare", "best_actual_p90"], ascending=[False, False, False, True])
    )

    quadrant = (
        all_df.groupby(["experiment", "outcome_quadrant"], dropna=False)
        .agg(
            n=("basename", "count"),
            targets=("target_norm", lambda x: ",".join(sorted(set(map(str, x)))[:8])),
            best_actual_p90=("actual_p90", "min"),
            median_null_strict_rate=("null_strict_rate", "median"),
            min_readiness_distance=("readiness_distance", "min"),
        )
        .reset_index()
        .sort_values(["experiment", "n"], ascending=[True, False])
    )

    near = all_df.head(120).copy()
    ready = all_df[all_df["old_ready_rule"]].copy()
    visible_null_rare = all_df[all_df["selector_visible"] & all_df["null_rare"]].copy()
    visible_null_common = all_df[all_df["selector_visible"] & all_df["null_common"]].copy()
    null_rare_edge = all_df[all_df["null_rare"] & all_df["edge_ok"]].copy()

    keep_cols = [
        "experiment",
        "basename",
        "target_norm",
        "family",
        "outcome_quadrant",
        "failure_mode",
        "readiness_defects",
        "readiness_distance",
        "actual_mean",
        "actual_p90",
        "actual_beats_current_rate",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "selector_visible",
        "old_ready_rule",
        "source_governor_file",
    ]

    all_df.to_csv(ALL_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    near[keep_cols].to_csv(NEAR_MISS_OUT, index=False)
    quadrant.to_csv(QUADRANT_OUT, index=False)

    lines = [
        "# E298 Materialization Outcome Atlas",
        "",
        "Public LB는 사용하지 않았다. 기존 current-anchor governor와 matched-null 결과만 집계했다.",
        "",
        "## 입력",
        "",
        f"- governor files loaded: {len(frames)}",
        f"- candidate rows: {len(all_df)}",
        f"- missing files: {len(missing)}",
        "",
        "## 핵심 카운트",
        "",
        f"- ready_like: {len(ready)}",
        f"- selector_visible: {int(all_df['selector_visible'].sum())}",
        f"- null_rare: {int(all_df['null_rare'].sum())}",
        f"- selector_visible AND null_rare: {len(visible_null_rare)}",
        f"- selector_visible AND null_common: {len(visible_null_common)}",
        f"- null_rare AND edge_ok: {len(null_rare_edge)}",
        "",
        "## Outcome Quadrants",
        "",
        md_table(
            quadrant,
            ["experiment", "outcome_quadrant", "n", "targets", "best_actual_p90", "median_null_strict_rate", "min_readiness_distance"],
            n=80,
        ),
        "",
        "## 가장 가까운 후보들",
        "",
        md_table(
            near,
            [
                "experiment",
                "target_norm",
                "family",
                "outcome_quadrant",
                "failure_mode",
                "readiness_defects",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "mean_dominance",
                "worst_mode_p90_dominance",
                "basename",
            ],
            n=30,
        ),
        "",
        "## 해석",
        "",
    ]

    if len(ready):
        lines += [
            "- public-free ready_like 후보가 존재한다. 다음 단계는 이 후보들이 기존 best 대비 target/row movement가 실질적인지 확인하고, 중복/near-duplicate를 제거하는 것이다.",
        ]
    elif len(visible_null_rare):
        lines += [
            "- 완전 ready_like는 없지만 selector-visible + null-rare 후보가 존재한다.",
            "- 병목은 사회적 state 자체가 아니라 dominance/mode 안정성 또는 edge 크기다. 다음 실험은 이 후보의 row/target placement를 더 보수적으로 재배치하는 것이 맞다.",
        ]
    elif len(null_rare_edge):
        lines += [
            "- null-rare + edge 후보는 있지만 selector가 안정적으로 보지 못한다.",
            "- 이 경우 새 submission보다 selector-visible training target이 필요하다. 즉, JEPA/state가 만든 score를 직접 확률에 넣기보다 '어떤 placement가 governor-visible인가'를 예측해야 한다.",
        ]
    else:
        lines += [
            "- 기존 human/social materialization 중 public-free ready 후보는 없다.",
            "- 특히 selector-visible 후보가 null에서도 흔하게 재현되면, 그 후보는 생활 가설이 틀렸다기보다 확률 번역기가 null hallucination을 만든 것이다.",
        ]

    lines += [
        "",
        "## 다음 행동",
        "",
        "1. public LB 없이 진행한다.",
        "2. ready_like가 없으면 새 사회적 feature를 바로 제출하지 말고, `selector_visible AND null_rare`를 목표로 하는 2-stage translator를 만든다.",
        "3. strong social state는 feature/latent로 유지하되, submission 확률 이동은 governor-visible/null-rare placement만 허용한다.",
        "",
        "## 산출물",
        "",
        f"- `{rel(ALL_OUT)}`",
        f"- `{rel(FAMILY_OUT)}`",
        f"- `{rel(NEAR_MISS_OUT)}`",
        f"- `{rel(QUADRANT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"loaded_governors={len(frames)} candidates={len(all_df)} ready_like={len(ready)}")
    print(f"selector_visible={int(all_df['selector_visible'].sum())} null_rare={int(all_df['null_rare'].sum())}")
    print(f"visible_null_rare={len(visible_null_rare)} null_rare_edge={len(null_rare_edge)}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
