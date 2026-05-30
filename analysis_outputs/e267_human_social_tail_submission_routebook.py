#!/usr/bin/env python3
"""E267: routebook for human/social tail materialization candidates.

E266 produced multiple lifestyle-conditioned Q3/S4 cell-tail files. This
script separates three different questions:

1. score-balanced next file,
2. sharp low-cell sensor,
3. broad support sensor.

The recommended file is copied to a stable E267 name so the public result can
be interpreted as a pre-registered social-lifelog/JEPA hypothesis, not as a
post-hoc pick among many siblings.
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

SELECTED_IN = OUT / "e266_human_social_tail_materialization_selected.csv"
PRIORITY_OUT = OUT / "e267_human_social_tail_submission_priority.csv"
MOVEMENT_OUT = OUT / "e267_human_social_tail_submission_movement.csv"
REPORT_OUT = OUT / "e267_human_social_tail_submission_routebook_report.md"

RECOMMENDED_SOURCE = (
    "submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_"
    "contrast_q0p10_drop_global_top50_2936100f.csv"
)
RECOMMENDED_OUT = OUT / "submission_e267_humansocial_tail_balanced_2936100f.csv"

REFERENCES = {
    "e247_public_best": "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv",
    "e256_same_family_loss": "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
    "e224_body": "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv",
    "e95_hardtail": "submission_e95_hardtail_541e3973.csv",
}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    xx = clip_prob(x)
    return np.log(xx / (1.0 - xx))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 20, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda v: "" if pd.isna(v) else f"{float(v):{floatfmt}}")
    headers = list(view.columns)
    rows = view.astype(str).values.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def submission_digest(name: str) -> str:
    match = re.search(r"_([0-9a-f]{8})\.csv$", name)
    return match.group(1) if match else Path(name).stem[-8:]


def load_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in [*KEYS, *TARGETS] if c not in df.columns]
    if missing:
        raise RuntimeError(f"{path} missing columns: {missing}")
    return df[KEYS + TARGETS].copy()


def movement_against(candidate: pd.DataFrame, reference: pd.DataFrame, ref_name: str) -> dict[str, float | int | str]:
    if len(candidate) != len(reference) or not candidate[KEYS].equals(reference[KEYS]):
        raise RuntimeError(f"row/key mismatch against {ref_name}")
    cand = clip_prob(candidate[TARGETS].to_numpy())
    ref = clip_prob(reference[TARGETS].to_numpy())
    delta = cand - ref
    logit_delta = logit(cand) - logit(ref)
    abs_delta = np.abs(delta)
    moved = abs_delta > 1.0e-12
    out: dict[str, float | int | str] = {
        "reference": ref_name,
        "moved_cells_vs_ref": int(moved.sum()),
        "moved_rows_vs_ref": int(np.any(moved, axis=1).sum()),
        "mean_abs_prob_delta_vs_ref": float(abs_delta.mean()),
        "max_abs_prob_delta_vs_ref": float(abs_delta.max()),
        "mean_abs_logit_delta_vs_ref": float(np.abs(logit_delta).mean()),
        "max_abs_logit_delta_vs_ref": float(np.abs(logit_delta).max()),
    }
    for j, target in enumerate(TARGETS):
        out[f"{target}_moved_vs_ref"] = int(moved[:, j].sum())
        out[f"{target}_mean_abs_prob_delta_vs_ref"] = float(abs_delta[:, j].mean())
        out[f"{target}_max_abs_prob_delta_vs_ref"] = float(abs_delta[:, j].max())
    return out


def add_route_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pred_digest"] = out["submission_file"].map(submission_digest)
    out["total_dropped_cells"] = out["q3_dropped_cells"].astype(int) + out["s4_dropped_cells"].astype(int)
    out["expected_ok"] = out["expected_loss_vs_e224"] <= 0.0
    out["actual_expected_ok"] = out["actual_expected_delta_vs_e224"] <= 0.0
    out["support_ok"] = out["support_gain_vs_e224"] >= 0.0020
    out["adverse_ok"] = out["adverse_reduction_vs_e224"] >= 0.00030
    out["actual_adverse_ok"] = out["actual_adverse_reduction_vs_e224"] >= 0.00025
    out["q3_not_topcell_fragile"] = out["q3_top1_over_abs_expected"] <= 0.75
    out["not_too_broad"] = out["total_dropped_cells"] <= 50
    out["e230_overlap_ok"] = out["e230_q3_risk_top21_overlap"] >= 4
    out["balanced_gate"] = (
        out["expected_ok"]
        & out["actual_expected_ok"]
        & out["support_ok"]
        & out["adverse_ok"]
        & out["actual_adverse_ok"]
        & out["q3_not_topcell_fragile"]
        & out["not_too_broad"]
        & out["e230_overlap_ok"]
    )
    out["sharp_gate"] = (
        (out["total_dropped_cells"] <= 26)
        & (out["expected_loss_vs_e224"] <= -0.000020)
        & (out["support_gain_vs_e224"] >= 0.0020)
        & (out["q3_top1_over_abs_expected"] <= 0.75)
    )
    out["support_sensor_gate"] = (
        (out["support_gain_vs_e224"] >= 0.0045)
        & (out["adverse_reduction_vs_e224"] >= 0.00040)
        & (out["e230_q3_risk_top21_overlap"] >= 6)
    )

    # This is intentionally not the E237 score. E237 rewards broad support
    # sensors; this survival score penalizes positive expected loss and broad
    # cell count because E265 showed broad gates are too easy.
    pos_expected = np.maximum(out["expected_loss_vs_e224"].astype(float), 0.0)
    broad = np.maximum(out["total_dropped_cells"].astype(float) - 50.0, 0.0)
    out["social_jepa_survival_score"] = (
        out["expected_ok"].astype(float)
        + out["actual_expected_ok"].astype(float)
        + 1.5 * np.minimum(out["adverse_reduction_vs_e224"].astype(float) / 0.00045, 1.0)
        + 1.5 * np.minimum(out["actual_adverse_reduction_vs_e224"].astype(float) / 0.00040, 1.0)
        + 1.2 * np.minimum(out["support_gain_vs_e224"].astype(float) / 0.00450, 1.0)
        + 0.8 * np.minimum(out["actual_support_gain_vs_e224"].astype(float) / 0.00400, 1.0)
        + 0.6 * np.minimum(out["e230_q3_risk_top21_overlap"].astype(float) / 6.0, 1.0)
        + 0.5 * out["q3_not_topcell_fragile"].astype(float)
        + 0.3 * out["not_too_broad"].astype(float)
        - 1.5 * (pos_expected / 0.000020)
        - 0.6 * (broad / 25.0)
    )
    return out


def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["canonical_preference"] = 5
    out.loc[out["submission_file"].eq(RECOMMENDED_SOURCE), "canonical_preference"] = 0
    out.loc[out["policy"].eq("drop_global_top50"), "canonical_preference"] = np.minimum(
        out.loc[out["policy"].eq("drop_global_top50"), "canonical_preference"], 1
    )
    out.loc[out["policy"].eq("drop_each_top25"), "canonical_preference"] = np.minimum(
        out.loc[out["policy"].eq("drop_each_top25"), "canonical_preference"], 2
    )
    out["duplicate_prediction_count"] = out.groupby("pred_digest")["pred_digest"].transform("size")
    out = out.sort_values(
        ["social_jepa_survival_score", "balanced_gate", "canonical_preference", "e237_score"],
        ascending=[False, False, True, False],
    )
    return out.groupby("pred_digest", as_index=False, sort=False).head(1).reset_index(drop=True)


def write_report(priority: pd.DataFrame, movement: pd.DataFrame, recommended: pd.Series) -> None:
    top_cols = [
        "route_label",
        "candidate_id",
        "submission_file",
        "social_jepa_survival_score",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "e230_q3_risk_top21_overlap",
        "total_dropped_cells",
        "duplicate_prediction_count",
    ]
    movement_cols = [
        "submission_file",
        "reference",
        "moved_cells_vs_ref",
        "moved_rows_vs_ref",
        "Q3_moved_vs_ref",
        "S4_moved_vs_ref",
        "mean_abs_logit_delta_vs_ref",
        "max_abs_logit_delta_vs_ref",
    ]
    report = f"""# E267 Human/Social Tail Submission Routebook

## Question

E266 produced 22 lifestyle-conditioned Q3/S4 materializations. Which one should be used as a public sensor if only one file is submitted?

## Decision

Recommended next social/JEPA file:

`{RECOMMENDED_OUT.name}`

Source file:

`{recommended['submission_file']}`

This is the balanced `2936100f` prediction: `25` Q3 cells and `25` S4 cells are rolled back toward E154 using the E264/E266 human-core late-lifelog cell-tail representation.

## Why This One

- It keeps expected loss versus E224 non-positive: `{recommended['expected_loss_vs_e224']:.9f}`.
- It reduces adverse capacity versus E224: `{recommended['adverse_reduction_vs_e224']:.9f}`.
- It improves support mass versus E224: `{recommended['support_gain_vs_e224']:.9f}`.
- It also survives actual-vs-E95 stress: expected `{recommended['actual_expected_delta_vs_e224']:.9f}`, adverse reduction `{recommended['actual_adverse_reduction_vs_e224']:.9f}`, support gain `{recommended['actual_support_gain_vs_e224']:.9f}`.
- It is not the broadest support sensor. The broader `c1e018aa` file has higher E237 score but positive expected loss and 75 dropped cells, which is too close to the E265 broad-gate failure mode.
- It is more informative than the sharp `95bf3a1c` file because it keeps much more support/adverse movement while still avoiding positive expected loss.

## Top Canonical Candidates

{md_table(priority, top_cols, 12)}

## Movement Against Known Anchors

{md_table(movement, movement_cols, 30)}

## Public LB Interpretation

- If this beats E247 `0.5761589494`, the strongest read is that human/social day state is a missing Q3/S4 tail law, not just a numeric feature-NN smoothing artifact.
- If it lands between E247 and E256 `0.5762805676`, the lifestyle state is real but weaker than E247's exact Q3 smoothing/body interaction.
- If it is near or worse than E95 `0.5762913298`, E266's materialization stress is likely overfitting the E224/E154 local geometry; next step should be a direct human/social overlay on E247 rather than another E224-family rollback.

## Hidden-World Bet

The bet is that some Q3/S4 tail errors correspond to human days: presleep cognitive load, social-message load, routine/commute rhythm, charging/screen/onset fragmentation, and sensor coverage jointly mark when the E224 body should be trusted or rolled back. This is JEPA-style because the model does not reconstruct raw app usage; it predicts the hidden target representation "which row-target cells are unsafe to keep" from partial human-day context.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    if not SELECTED_IN.exists():
        raise RuntimeError(f"missing {SELECTED_IN}; run E266 first")
    selected = pd.read_csv(SELECTED_IN)
    selected = selected[selected["submission_file"].astype(str).str.len() > 0].copy()
    selected = add_route_scores(selected)
    canonical = canonicalize(selected)

    canonical["route_label"] = "candidate"
    canonical.loc[canonical["submission_file"].eq(RECOMMENDED_SOURCE), "route_label"] = "submit_1_balanced"
    canonical.loc[canonical["sharp_gate"].astype(bool), "route_label"] = canonical.loc[
        canonical["sharp_gate"].astype(bool), "route_label"
    ].where(canonical.loc[canonical["sharp_gate"].astype(bool), "route_label"].eq("submit_1_balanced"), "sharp_sensor")
    canonical.loc[canonical["support_sensor_gate"].astype(bool), "route_label"] = canonical.loc[
        canonical["support_sensor_gate"].astype(bool), "route_label"
    ].where(
        canonical.loc[canonical["support_sensor_gate"].astype(bool), "route_label"].eq("submit_1_balanced"),
        "support_sensor",
    )

    source = OUT / RECOMMENDED_SOURCE
    if not source.exists():
        raise RuntimeError(f"recommended source missing: {source}")
    shutil.copyfile(source, RECOMMENDED_OUT)

    rec = canonical[canonical["submission_file"].eq(RECOMMENDED_SOURCE)]
    if rec.empty:
        raise RuntimeError(f"recommended source not present in canonical table: {RECOMMENDED_SOURCE}")
    recommended = rec.iloc[0]

    candidate = load_submission(RECOMMENDED_OUT)
    movement_rows: list[dict[str, object]] = []
    for ref_name, ref_file in REFERENCES.items():
        ref_path = OUT / ref_file
        if ref_path.exists():
            row = movement_against(candidate, load_submission(ref_path), ref_name)
            row["submission_file"] = RECOMMENDED_OUT.name
            movement_rows.append(row)
    movement = pd.DataFrame(movement_rows)

    canonical.to_csv(PRIORITY_OUT, index=False)
    movement.to_csv(MOVEMENT_OUT, index=False)
    write_report(canonical, movement, recommended)

    print(f"recommended={RECOMMENDED_OUT}")
    print(f"priority_rows={len(canonical)} movement_rows={len(movement)}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
