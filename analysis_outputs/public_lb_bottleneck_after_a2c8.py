from __future__ import annotations

from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning, message="Mean of empty slice")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Degrees of freedom <= 0 for slice.")


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from local_lb_proxy_validation import add_derived_features, build_model_scores  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
RAW05_PUBLIC = 0.5775263072
A2C8_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
A2C8_PUBLIC = 0.577439321
TARGET_PUBLIC = 0.54

CALIBRATION_IN = OUT / "public_lb_actual_anchor_ranker_calibration.csv"
FRONTIER_PROXY_IN = OUT / "frontier_cvjepa_surprise_micro_refine_local_proxy.csv"
FRONTIER_SHORT_IN = OUT / "frontier_cvjepa_surprise_micro_refine_shortlist.csv"
COMBO_SUMMARY_IN = OUT / "cross_view_jepa_surprise_combo_summary.csv"
RAW_RESCUE_IN = JEPA / "raw_timeline_jepa_rescue_scaled_candidates.csv"

KNOWN_AUG_OUT = OUT / "public_lb_bottleneck_after_a2c8_known_augmented.csv"
MODEL_OUT = OUT / "public_lb_bottleneck_after_a2c8_model_scores.csv"
A2C8_ERRORS_OUT = OUT / "public_lb_bottleneck_after_a2c8_proxy_errors.csv"
MOVE_OUT = OUT / "public_lb_bottleneck_after_a2c8_move_bounds.csv"
FRONTIER_OUT = OUT / "public_lb_bottleneck_after_a2c8_frontier_focus.csv"
REPORT_OUT = OUT / "public_lb_bottleneck_after_a2c8_report.md"


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(file_name)


def load_submission(file_name: str, sample: pd.DataFrame) -> pd.DataFrame:
    sub = pd.read_csv(locate(file_name), parse_dates=["sleep_date", "lifelog_date"])
    sub = sub.sort_values(KEY).reset_index(drop=True)
    if not sub[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {file_name}")
    return sub


def max_possible_logloss_gain(base: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    """Per-cell best-case gain if every moved probability points toward truth."""
    eps = 1e-15
    p = np.clip(base, eps, 1 - eps)
    q = np.clip(candidate, eps, 1 - eps)
    gain_if_one = np.log(q / p)
    gain_if_zero = np.log((1 - q) / (1 - p))
    return np.maximum(gain_if_one, gain_if_zero)


def movement_bounds(files: list[str]) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    raw = load_submission(RAW05_FILE, sample)
    raw_values = raw[TARGETS].to_numpy(dtype=np.float64)
    rows: list[dict[str, object]] = []

    for file_name in files:
        sub = load_submission(file_name, sample)
        vals = sub[TARGETS].to_numpy(dtype=np.float64)
        diff = vals - raw_values
        gain = max_possible_logloss_gain(raw_values, vals)
        rec: dict[str, object] = {
            "file": file_name,
            "mean_abs_move_vs_raw05": float(np.mean(np.abs(diff))),
            "max_abs_move_vs_raw05": float(np.max(np.abs(diff))),
            "active_cell_rate_gt_1e-9": float(np.mean(np.abs(diff) > 1e-9)),
            "active_cell_rate_gt_1e-4": float(np.mean(np.abs(diff) > 1e-4)),
            "best_case_logloss_gain_if_all_moves_correct": float(np.mean(gain)),
            "best_case_gap_fraction_to_0p54": float(np.mean(gain) / (A2C8_PUBLIC - TARGET_PUBLIC)),
        }
        for j, target in enumerate(TARGETS):
            d = diff[:, j]
            g = gain[:, j]
            rec[f"{target}_mean_abs_move"] = float(np.mean(np.abs(d)))
            rec[f"{target}_max_abs_move"] = float(np.max(np.abs(d)))
            rec[f"{target}_active_gt_1e-4"] = float(np.mean(np.abs(d) > 1e-4))
            rec[f"{target}_best_case_gain"] = float(np.mean(g))
        rows.append(rec)
    return pd.DataFrame(rows)


def append_a2c8_anchor() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    calibration = pd.read_csv(CALIBRATION_IN)
    frontier = pd.read_csv(FRONTIER_PROXY_IN)
    a2c8 = frontier[frontier["file"].eq(A2C8_FILE)].copy()
    if len(a2c8) != 1:
        raise ValueError(f"expected one row for {A2C8_FILE}, got {len(a2c8)}")
    a2c8["known_public"] = A2C8_PUBLIC

    known_aug = pd.concat([calibration, a2c8], ignore_index=True, sort=False)
    known_aug = add_derived_features(known_aug)
    model_scores, known_pred = build_model_scores(known_aug)
    return known_aug, model_scores, known_pred


def frontier_focus() -> pd.DataFrame:
    proxy = pd.read_csv(FRONTIER_PROXY_IN)
    short = pd.read_csv(FRONTIER_SHORT_IN)
    keep_short = [
        "file",
        "label",
        "anchor_name",
        "basis",
        "target_mask",
        "row_gate",
        "cell_gate",
        "direction",
        "weight",
        "cap",
        "active_gate_mean",
    ]
    short = short[[c for c in keep_short if c in short.columns]].drop_duplicates("file")
    out = proxy.merge(short, on="file", how="left", suffixes=("", "_short"))
    cols = [
        "file",
        "label",
        "anchor_name",
        "basis",
        "target_mask",
        "row_gate",
        "cell_gate",
        "direction",
        "weight",
        "cap",
        "active_gate_mean",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "posterior_expected_public_vs_anchor",
        "raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
    ]
    out = out[[c for c in cols if c in out.columns]].copy()
    out["is_submitted_a2c8"] = out["file"].eq(A2C8_FILE)
    out = out.sort_values(
        ["is_submitted_a2c8", "available_raw05_relative_delta_vs_raw05_public"],
        ascending=[False, True],
    )
    return out.head(30).reset_index(drop=True)


def scalar_summary(known_aug: pd.DataFrame, model_scores: pd.DataFrame, known_pred: pd.DataFrame, move: pd.DataFrame) -> dict[str, float | str]:
    old_public = {
        RAW05_FILE: RAW05_PUBLIC,
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
        "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
        "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    }
    a2c8_row = known_aug[known_aug["file"].eq(A2C8_FILE)].iloc[0]
    a2c8_pred = known_pred[known_pred["file"].eq(A2C8_FILE)].iloc[0]
    best = model_scores[model_scores["kind"].eq("leave_one_anchor_out")].sort_values(["mae", "rmse"]).iloc[0]
    move_row = move[move["file"].eq(A2C8_FILE)].iloc[0]
    return {
        "new_best_file": A2C8_FILE,
        "new_best_public": A2C8_PUBLIC,
        "raw05_public": RAW05_PUBLIC,
        "actual_public_delta_vs_raw05": A2C8_PUBLIC - RAW05_PUBLIC,
        "distance_from_0p54": A2C8_PUBLIC - TARGET_PUBLIC,
        "raw05_to_a2c8_gain_fraction_of_0p54_gap": (RAW05_PUBLIC - A2C8_PUBLIC) / (A2C8_PUBLIC - TARGET_PUBLIC),
        "gain_multiplier_needed_vs_last_gain": (A2C8_PUBLIC - TARGET_PUBLIC) / (RAW05_PUBLIC - A2C8_PUBLIC),
        "stage2_public_delta_vs_a2c8": old_public["submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"] - A2C8_PUBLIC,
        "a2c8_available_raw05_relative_delta": float(a2c8_row["available_raw05_relative_delta_vs_raw05_public"]),
        "a2c8_available_raw05_proxy_absolute": RAW05_PUBLIC
        + float(a2c8_row["available_raw05_relative_delta_vs_raw05_public"]),
        "a2c8_available_raw05_proxy_miss_pred_minus_public": RAW05_PUBLIC
        + float(a2c8_row["available_raw05_relative_delta_vs_raw05_public"])
        - A2C8_PUBLIC,
        "a2c8_actual_anchor_score_final": float(a2c8_row["actual_anchor_score_final"]),
        "a2c8_posterior_expected_public_vs_anchor": float(a2c8_row["posterior_expected_public_vs_anchor"]),
        "a2c8_leave_one_anchor_signed_axes_pred": float(a2c8_pred["loocv_ridge_signed_axes_a1"]),
        "a2c8_leave_one_anchor_signed_axes_error": float(a2c8_pred["loocv_ridge_signed_axes_a1_error"]),
        "best_7anchor_loocv_model": str(best["model"]),
        "best_7anchor_loocv_mae": float(best["mae"]),
        "best_7anchor_loocv_rmse": float(best["rmse"]),
        "a2c8_mean_abs_move_vs_raw05": float(move_row["mean_abs_move_vs_raw05"]),
        "a2c8_best_case_gain_if_all_moves_correct": float(move_row["best_case_logloss_gain_if_all_moves_correct"]),
        "a2c8_best_case_gap_fraction_to_0p54": float(move_row["best_case_gap_fraction_to_0p54"]),
    }


def markdown_table(df: pd.DataFrame, cols: list[str], n: int | None = None) -> str:
    sub = df[[c for c in cols if c in df.columns]].copy()
    if n is not None:
        sub = sub.head(n)
    if sub.empty:
        return "_empty_"

    def fmt(value: object) -> str:
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.10f}"
        if pd.isna(value):
            return ""
        return str(value).replace("|", "\\|")

    headers = [str(c) for c in sub.columns]
    rows = [[fmt(value) for value in row] for row in sub.to_numpy(dtype=object)]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]
    header_line = "| " + " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))) + " |"
    sep_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body])


def main() -> None:
    known_aug, model_scores, known_pred = append_a2c8_anchor()
    focus = frontier_focus()
    move = movement_bounds([A2C8_FILE, RAW05_FILE])

    known_aug.to_csv(KNOWN_AUG_OUT, index=False)
    model_scores.to_csv(MODEL_OUT, index=False)
    focus.to_csv(FRONTIER_OUT, index=False)
    move.to_csv(MOVE_OUT, index=False)

    error_cols = [
        "file",
        "known_public",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "available_raw05_relative_delta_vs_raw05_public",
        "loocv_ridge_signed_axes_a1",
        "loocv_ridge_signed_axes_a1_error",
        "loocv_ridge_abs_axes_a1",
        "loocv_ridge_abs_axes_a1_error",
        "loocv_ridge_anchor_gap_a1",
        "loocv_ridge_anchor_gap_a1_error",
    ]
    known_pred[[c for c in error_cols if c in known_pred.columns]].to_csv(A2C8_ERRORS_OUT, index=False)

    summary = scalar_summary(known_aug, model_scores, known_pred, move)
    combo = pd.read_csv(COMBO_SUMMARY_IN) if COMBO_SUMMARY_IN.exists() else pd.DataFrame()
    raw_rescue = pd.read_csv(RAW_RESCUE_IN) if RAW_RESCUE_IN.exists() else pd.DataFrame()

    lines = [
        "# Public LB Bottleneck After A2C8",
        "",
        "## Bottom Line",
        "",
        f"- New best public LB: `{A2C8_FILE}` = `{A2C8_PUBLIC:.9f}`.",
        f"- Improvement vs raw05: `{summary['actual_public_delta_vs_raw05']:.10f}`.",
        f"- Remaining distance to `0.540000000`: `{summary['distance_from_0p54']:.9f}`.",
        f"- The last improvement covers only `{summary['raw05_to_a2c8_gain_fraction_of_0p54_gap']:.4%}` of the remaining 0.54 gap; the same-size gain would need about `{summary['gain_multiplier_needed_vs_last_gain']:.1f}x` more.",
        "",
        "## Validation Bottleneck",
        "",
        f"- Best 7-anchor leave-one-public-anchor proxy: `{summary['best_7anchor_loocv_model']}` MAE/RMSE `{summary['best_7anchor_loocv_mae']:.10f}` / `{summary['best_7anchor_loocv_rmse']:.10f}`.",
        f"- For `a2c8`, the raw05-relative proxy predicted `{summary['a2c8_available_raw05_proxy_absolute']:.10f}`, missing public by `{summary['a2c8_available_raw05_proxy_miss_pred_minus_public']:.10f}`.",
        f"- But the leave-one-anchor signed-axis model predicted `{summary['a2c8_leave_one_anchor_signed_axes_pred']:.10f}`, missing by `{summary['a2c8_leave_one_anchor_signed_axes_error']:.10f}`. This marks `a2c8` as out-of-family for the old six public anchors.",
        "",
        "## Movement Bottleneck",
        "",
        f"- `a2c8` mean absolute move vs raw05 is only `{summary['a2c8_mean_abs_move_vs_raw05']:.10f}` per cell.",
        f"- Even if every moved probability pointed toward the hidden truth, the best-case average logloss gain is `{summary['a2c8_best_case_gain_if_all_moves_correct']:.10f}`, only `{summary['a2c8_best_case_gap_fraction_to_0p54']:.2%}` of the 0.54 gap.",
        "",
        "## Known Public Anchors With A2C8",
        "",
        markdown_table(
            known_aug,
            [
                "file",
                "known_public",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
            ],
        ),
        "",
        "## 7-Anchor Proxy Scores",
        "",
        markdown_table(
            model_scores[model_scores["kind"].eq("leave_one_anchor_out")],
            ["model", "mae", "rmse", "max_abs_error", "bias_mean_pred_minus_public", "pairwise_rank_accuracy"],
        ),
        "",
        "## A2C8 Movement Bounds",
        "",
        markdown_table(
            move,
            [
                "file",
                "mean_abs_move_vs_raw05",
                "max_abs_move_vs_raw05",
                "active_cell_rate_gt_1e-4",
                "best_case_logloss_gain_if_all_moves_correct",
                "best_case_gap_fraction_to_0p54",
            ],
        ),
        "",
        "## Local JEPA Signal vs Public Transfer",
        "",
    ]
    if len(combo):
        lines.extend(
            [
                "Cross-view JEPA surprise features improve local OOF strongly, but the public-safe graft only converts a tiny part of that signal:",
                "",
                markdown_table(
                    combo,
                    [
                        "combo",
                        "base_loss",
                        "candidate_loss",
                        "delta",
                        "subject_half_delta",
                        "subject_half_win_rate",
                        "geometry_delta",
                        "geometry_win_rate",
                    ],
                    n=7,
                ),
                "",
            ]
        )
    if len(raw_rescue):
        lines.extend(
            [
                "Raw timeline JEPA rescue also shows that bigger local moves looked better OOF, while the submitted safe scale was only a public-safe compromise:",
                "",
                markdown_table(
                    raw_rescue,
                    [
                        "candidate",
                        "scale",
                        "oof_loss",
                        "oof_delta_vs_stage2",
                        "bad_axis_projection_ratio",
                        "good_axis_projection_ratio",
                        "jepa_bad_axis_ratio",
                    ],
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Frontier Focus",
            "",
            markdown_table(
                focus,
                [
                    "file",
                    "is_submitted_a2c8",
                    "label",
                    "available_raw05_relative_delta_vs_raw05_public",
                    "available_raw05_relative_model_spread",
                    "actual_anchor_score_final",
                    "posterior_expected_public_vs_anchor",
                    "mean_abs_move_vs_raw05",
                ],
                n=12,
            ),
            "",
            "## Interpretation",
            "",
            "1. The current search is mostly optimizing a very thin public-compatible tangent around raw05. That can produce 1e-4 gains but cannot plausibly produce a 0.037 logloss drop.",
            "2. The local OOF signal is real, but public transfer is bottlenecked by hidden-block distribution shift and by sparse public feedback. Six to seven public anchors are not enough to calibrate new candidate families.",
            "3. To attack 0.54, the next branch must either identify hidden test labels/subsets much more directly, or train a substantially stronger row-level representation whose larger moves survive public-axis validation. Micro-refines around raw05 are now a measurement tool, not the main path.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(REPORT_OUT)


if __name__ == "__main__":
    main()
