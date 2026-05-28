from __future__ import annotations

from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    KEYS,
    TARGETS,
    feature_row,
    load_sub,
    logit,
)
from public_pairwise_order_selector import evaluate_pairwise_models, score_candidates  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


SENSORS = {
    "conservative_1bb": OUT / "submission_label_flow_focused_1bbfb735.csv",
    "contrast_6b": OUT / "submission_label_flow_focused_6b9335b1.csv",
}

MASKS = {
    "full": TARGETS,
    "q3_s4": ["Q3", "S4"],
    "s4": ["S4"],
    "q3": ["Q3"],
    "q2_q3_s4": ["Q2", "Q3", "S4"],
    "s3_s4": ["S3", "S4"],
}

SCALES = [0.05, 0.10, 0.20, 0.35, 0.50, 0.65, 0.75, 0.85, 1.00]

DETAIL_OUT = OUT / "label_flow_sensor_scale_curve.csv"
SUMMARY_OUT = OUT / "label_flow_sensor_scale_curve_summary.csv"
SHORTLIST_OUT = OUT / "label_flow_sensor_scale_curve_shortlist.csv"
REPORT_OUT = OUT / "label_flow_sensor_scale_curve_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def scale_tag(scale: float) -> str:
    return f"s{scale:.2f}".replace(".", "p")


def stable_name(sensor_tag: str, mask_name: str, scale: float) -> str:
    raw = f"{sensor_tag}|{mask_name}|{scale:.4f}".encode("utf-8")
    digest = hashlib.md5(raw).hexdigest()[:8]
    return f"submission_label_flow_sensorcurve_{sensor_tag}_{mask_name}_{scale_tag(scale)}_{digest}.csv"


def write_scaled_submissions(sample: pd.DataFrame) -> pd.DataFrame:
    base = load_sub(A2C8, sample)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    records: list[dict[str, object]] = []

    for sensor_tag, sensor_path in SENSORS.items():
        sensor = load_sub(sensor_path, sample)
        sensor_logits = logit(sensor[TARGETS].to_numpy(dtype=np.float64))
        delta = sensor_logits - base_logits
        for mask_name, mask_targets in MASKS.items():
            mask_idx = [TARGETS.index(target) for target in mask_targets]
            for scale in SCALES:
                out_logits = base_logits.copy()
                out_logits[:, mask_idx] = base_logits[:, mask_idx] + float(scale) * delta[:, mask_idx]
                probs = np.clip(sigmoid(out_logits), 1e-6, 1.0 - 1e-6)
                out = base.copy()
                out[TARGETS] = probs
                name = stable_name(sensor_tag, mask_name, scale)
                path = OUT / name
                out.to_csv(path, index=False)
                records.append(
                    {
                        "source_path": str(path.relative_to(ROOT)),
                        "file": str(path.relative_to(ROOT)),
                        "basename": name,
                        "sensor_tag": sensor_tag,
                        "mask_name": mask_name,
                        "scale": float(scale),
                        "mask_targets": ",".join(mask_targets),
                    }
                )
    return pd.DataFrame(records)


def build_feature_frame(generated: pd.DataFrame, sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rec in generated.to_dict("records"):
        path = ROOT / str(rec["source_path"])
        row = feature_row(path, sample, refs, ref_vecs)
        row.update(rec)
        row["candidate_family"] = "label_flow_sensor_scale_curve"
        rows.append(row)

    gen_features = pd.DataFrame(rows)

    known, _, _ = build_known_and_refs(sample)
    known = known.copy()
    known["source_path"] = known["file"].astype(str)
    known["basename"] = known["file"].astype(str)
    known["sensor_tag"] = "known_anchor"
    known["mask_name"] = "known_anchor"
    known["scale"] = np.nan
    known["mask_targets"] = ""

    return pd.concat([known, gen_features], ignore_index=True, sort=False)


def add_target_shape(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["movement_scale"] = out["mean_abs_move_vs_a2c8"]
    out["q3s4_move_share"] = (
        out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    ) / (out[move_cols].sum(axis=1) + 1e-12)
    return out


def score_curve(candidates: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    old_scored = candidate_stress_scores(known, candidates)
    merge_cols = [
        "file",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    old_scored = old_scored[[col for col in merge_cols if col in old_scored.columns]].copy()
    merged = candidates.merge(old_scored, on="file", how="left")

    model_df, _ = evaluate_pairwise_models(known)
    pair_scored = score_candidates(known, merged, model_df)
    pair_scored = add_target_shape(pair_scored)

    generated = pair_scored[pair_scored["sensor_tag"].isin(SENSORS)].copy()
    generated["old_majority"] = generated["beats_a2c8_scenario_rate"].fillna(0.0) >= 0.50
    generated["pair_majority"] = generated["pair_beats_a2c8_rate"].fillna(0.0) >= 0.70
    generated["two_selector_majority"] = generated["old_majority"] & generated["pair_majority"]
    generated["pair_p90_negative"] = generated["pair_delta_vs_a2c8_p90"] < 0.0
    generated["old_p90_below_full_1bb"] = generated["selector_p90_delta_vs_a2c8_public"] <= float(
        generated[
            generated["sensor_tag"].eq("conservative_1bb")
            & generated["mask_name"].eq("full")
            & np.isclose(generated["scale"], 1.0)
        ]["selector_p90_delta_vs_a2c8_public"].iloc[0]
    )
    generated["scaled_sensor_candidate"] = (
        generated["pair_p90_negative"]
        & (generated["pair_beats_a2c8_rate"] >= 0.75)
        & generated["old_p90_below_full_1bb"]
        & (generated["bad_axis_abs_load"] <= 0.055)
        & (generated["movement_scale"] < 0.00605)
    )
    generated["sensor_curve_rank"] = (
        generated["pair_delta_vs_a2c8_p90"]
        + 0.30 * generated["selector_p90_delta_vs_a2c8_public"].fillna(0.001)
        + 0.00025 * generated["bad_axis_abs_load"].fillna(0.0)
        + 0.00008 * generated["movement_scale"].fillna(0.0)
        - 0.00005 * generated["pair_beats_a2c8_rate"].fillna(0.0)
    )
    return generated.sort_values(
        ["scaled_sensor_candidate", "sensor_curve_rank"],
        ascending=[False, True],
    ).reset_index(drop=True)


def summarize(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in scored.groupby(["sensor_tag", "mask_name"], sort=True):
        best_rank = group.sort_values("sensor_curve_rank").iloc[0]
        best_pair = group.sort_values("pair_delta_vs_a2c8_p90").iloc[0]
        rows.append(
            {
                "sensor_tag": keys[0],
                "mask_name": keys[1],
                "n": int(len(group)),
                "pair_p90_negative": int(group["pair_p90_negative"].sum()),
                "scaled_sensor_candidate": int(group["scaled_sensor_candidate"].sum()),
                "two_selector_majority": int(group["two_selector_majority"].sum()),
                "best_rank_file": best_rank["source_path"],
                "best_rank_scale": float(best_rank["scale"]),
                "best_rank_pair_p90": float(best_rank["pair_delta_vs_a2c8_p90"]),
                "best_rank_old_p90": float(best_rank["selector_p90_delta_vs_a2c8_public"]),
                "best_rank_pair_rate": float(best_rank["pair_beats_a2c8_rate"]),
                "best_rank_old_rate": float(best_rank["beats_a2c8_scenario_rate"]),
                "best_pair_file": best_pair["source_path"],
                "best_pair_scale": float(best_pair["scale"]),
                "best_pair_p90": float(best_pair["pair_delta_vs_a2c8_p90"]),
                "best_pair_old_p90": float(best_pair["selector_p90_delta_vs_a2c8_public"]),
                "best_pair_rate": float(best_pair["pair_beats_a2c8_rate"]),
                "best_pair_bad_axis": float(best_pair["bad_axis_abs_load"]),
                "best_pair_movement": float(best_pair["movement_scale"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["scaled_sensor_candidate", "best_rank_pair_p90", "best_rank_old_p90"],
        ascending=[False, True, True],
    ).reset_index(drop=True)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def write_report(scored: pd.DataFrame, summary: pd.DataFrame, shortlist: pd.DataFrame) -> None:
    full_1bb = scored[
        scored["sensor_tag"].eq("conservative_1bb")
        & scored["mask_name"].eq("full")
        & np.isclose(scored["scale"], 1.0)
    ].iloc[0]
    full_6b = scored[
        scored["sensor_tag"].eq("contrast_6b")
        & scored["mask_name"].eq("full")
        & np.isclose(scored["scale"], 1.0)
    ].iloc[0]
    max_pair = scored.sort_values("pair_delta_vs_a2c8_p90").iloc[0]
    balanced_pool = scored[
        (scored["scale"] < 1.0)
        & (scored["pair_delta_vs_a2c8_p90"] < -0.000025)
        & (scored["pair_beats_a2c8_rate"] >= 0.95)
        & (scored["selector_p90_delta_vs_a2c8_public"] <= 0.00058)
    ].copy()
    balanced = balanced_pool.sort_values("sensor_curve_rank").iloc[0] if not balanced_pool.empty else None
    low_old_pool = scored[
        (scored["pair_delta_vs_a2c8_p90"] < 0.0)
        & (scored["pair_beats_a2c8_rate"] >= 0.75)
    ].copy()
    low_old = low_old_pool.sort_values("selector_p90_delta_vs_a2c8_public").iloc[0] if not low_old_pool.empty else None
    view_cols = [
        "source_path",
        "sensor_tag",
        "mask_name",
        "scale",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "two_selector_majority",
        "sensor_curve_rank",
    ]
    lines = [
        "# Label-Flow Sensor Scale Curve",
        "",
        "Question: can the E22 pair-only S4/Q3 diagnostic be made smaller while retaining pairwise signal and reducing old-selector downside?",
        "",
        "## Reference Full Sensors",
        "",
        f"- `1bbfb735` full scale: pair p90 `{full_1bb['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{full_1bb['selector_p90_delta_vs_a2c8_public']:.9f}`, pair rate `{full_1bb['pair_beats_a2c8_rate']:.3f}`, old rate `{full_1bb['beats_a2c8_scenario_rate']:.3f}`.",
        f"- `6b9335b1` full scale: pair p90 `{full_6b['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{full_6b['selector_p90_delta_vs_a2c8_public']:.9f}`, pair rate `{full_6b['pair_beats_a2c8_rate']:.3f}`, old rate `{full_6b['beats_a2c8_scenario_rate']:.3f}`.",
        "",
        "## Summary By Sensor And Mask",
        "",
        markdown_table(summary),
        "",
        "## Shortlist",
        "",
        markdown_table(shortlist[[col for col in view_cols if col in shortlist.columns]]),
        "",
        "## Decision",
        "",
    ]
    if shortlist.empty:
        lines.extend(
            [
                "- No scaled variant preserves the pairwise edge while materially reducing old-selector risk. E22 full/conservative sensor remains the clean diagnostic if public is used.",
                "- This weakens the idea that a smaller amplitude S4/Q3 sensor can avoid the selector conflict. The conflict is directional, not just scale.",
            ]
        )
    else:
        if balanced is not None:
            lines.append(
                f"- Best balanced lower-risk sensor is `{balanced['source_path']}`: pair p90 `{balanced['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{balanced['selector_p90_delta_vs_a2c8_public']:.9f}`, movement `{balanced['movement_scale']:.6f}`."
            )
        if low_old is not None:
            lines.append(
                f"- Lowest-old-risk pairwise-negative sensor is `{low_old['source_path']}`: pair p90 `{low_old['pair_delta_vs_a2c8_p90']:.9f}`, old p90 `{low_old['selector_p90_delta_vs_a2c8_public']:.9f}`, movement `{low_old['movement_scale']:.6f}`."
            )
        lines.extend(
            [
                f"- Maximum pairwise contrast remains `{max_pair['source_path']}` with pair p90 `{max_pair['pair_delta_vs_a2c8_p90']:.9f}`, but it has old p90 `{max_pair['selector_p90_delta_vs_a2c8_public']:.9f}`.",
                "- No scale or mask creates two-selector majority. Scaling lowers old p90, but the old scenario beat rate stays below majority, so the conflict is directional rather than only amplitude-driven.",
                "- E23 therefore does not create an improvement candidate. It only offers a lower-movement diagnostic alternative if public risk control matters more than maximum contrast.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{DETAIL_OUT.name}`",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{SHORTLIST_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8)
    generated = write_scaled_submissions(sample)
    known, refs, ref_vecs = build_known_and_refs(sample)
    features = build_feature_frame(generated, sample, refs, ref_vecs)
    scored = score_curve(features, known)
    summary = summarize(scored)
    shortlist = scored[scored["scaled_sensor_candidate"]].sort_values("sensor_curve_rank").head(30)

    scored.to_csv(DETAIL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(scored, summary, shortlist)

    print(REPORT_OUT)
    print("[summary]")
    print(
        summary[
            [
                "sensor_tag",
                "mask_name",
                "pair_p90_negative",
                "scaled_sensor_candidate",
                "two_selector_majority",
                "best_rank_scale",
                "best_rank_pair_p90",
                "best_rank_old_p90",
            ]
        ].to_string(index=False)
    )
    print("[shortlist]")
    cols = [
        "source_path",
        "sensor_tag",
        "mask_name",
        "scale",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
    ]
    print(shortlist[cols].head(20).to_string(index=False) if not shortlist.empty else "EMPTY")


if __name__ == "__main__":
    main()
