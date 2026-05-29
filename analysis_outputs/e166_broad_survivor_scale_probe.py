#!/usr/bin/env python3
"""E166: scale broad E165 survivor directions down into public-risk range.

E164 found broad post-E95 directions. E165 rejected known public-bad broad
directions by bad-axis geometry and left a live survivor set. The obvious
failure mode is that those survivor predictions are too large: submitting a
full all-cell JEPA move would test amplitude/collapse more than the hidden
world law.

This probe asks a smaller question: if E95 moves only a tiny logit-space step
toward an E165 geometry-health survivor, does the broad hard-label edge remain
while known-bad-axis geometry and per-cell amplitude stay controlled?
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402


E165_SHORTLIST = OUT / "e165_broad_edge_bad_axis_geometry_shortlist.csv"
SUMMARY_OUT = OUT / "e166_broad_survivor_scale_probe_summary.csv"
SHORTLIST_OUT = OUT / "e166_broad_survivor_scale_probe_shortlist.csv"
CONTROLS_OUT = OUT / "e166_broad_survivor_scale_probe_controls.csv"
REPORT_OUT = OUT / "e166_broad_survivor_scale_probe_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

NEGATIVE_CONTROLS = {
    "e72_bad_public": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "lejepa_bad_public": "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "q2_bad_public": "submission_jepa_latent_q2_w0p45.csv",
    "a2c8_bad_public": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "raw05_bad_public": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
}

KNOWN_PUBLIC = {
    E95_FILE: 0.5762913298,
    E101_FILE: 0.5763003660,
    MIXMIN_FILE: 0.5763066405,
    "submission_e72_topabs50_q2s3_gate_4e48cba2.csv": 0.5764077772,
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
}

SCALES = [0.005, 0.010, 0.015, 0.020, 0.030, 0.040, 0.050, 0.075, 0.100, 0.150, 0.200]
EPS = 1.0e-15


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), floatfmt)


def load_prob_path(path_value: str | Path, sample: pd.DataFrame) -> np.ndarray:
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    frame = pd.read_csv(path, usecols=KEYS + TARGETS).sort_values(KEYS).reset_index(drop=True)
    if len(frame) != len(sample):
        raise ValueError(f"row count mismatch for {path}")
    if not frame[KEYS].astype(str).reset_index(drop=True).equals(sample[KEYS].astype(str).reset_index(drop=True)):
        raise ValueError(f"key mismatch for {path}")
    return clip_prob(frame[TARGETS].to_numpy(dtype=np.float64))


def source_rows() -> pd.DataFrame:
    shortlist = pd.read_csv(E165_SHORTLIST)
    health = shortlist[shortlist["geometry_health_gate"].fillna(False)].copy()
    top_score = health.sort_values(["e164_broad_edge_score", "bad_span_energy"], ascending=[False, True]).head(14)
    low_bad = health[health["e164_broad_edge_score"].ge(0.02)].sort_values(
        ["bad_span_energy", "e164_broad_edge_score"], ascending=[True, False]
    ).head(6)
    rows = pd.concat([top_score, low_bad], ignore_index=True).drop_duplicates("file")
    rows["source_kind"] = "e165_health_survivor"

    control_rows = []
    for kind, file_name in NEGATIVE_CONTROLS.items():
        match = shortlist[shortlist["file"].eq(file_name)]
        if not match.empty:
            rec = match.iloc[0].to_dict()
        else:
            rec = {
                "path": str(OUT / file_name),
                "file": file_name,
                "family": "known_bad_control",
                "known_public_lb": KNOWN_PUBLIC.get(file_name, np.nan),
                "known_delta_vs_e95": (KNOWN_PUBLIC.get(file_name, np.nan) - KNOWN_PUBLIC[E95_FILE])
                if file_name in KNOWN_PUBLIC
                else np.nan,
                "e164_broad_edge_score": np.nan,
                "e164_expected_delta_vs_e95": np.nan,
                "bad_span_energy": np.nan,
                "max_bad_cos": np.nan,
                "geometry_health_gate": False,
            }
        rec["source_kind"] = kind
        control_rows.append(rec)
    controls = pd.DataFrame(control_rows)
    out = pd.concat([rows, controls], ignore_index=True).drop_duplicates(["file", "source_kind"])
    return out.reset_index(drop=True)


def score_scaled() -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame | None, np.ndarray | None]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = load_prob_path(OUT / E95_FILE, sample)
    z_e95 = logit(e95)
    e101 = load_prob_path(OUT / E101_FILE, sample)
    e154 = load_prob_path(OUT / E154_FILE, sample)
    mixmin = load_prob_path(OUT / MIXMIN_FILE, sample)
    axis_e101 = (logit(e101) - z_e95).reshape(-1)
    axis_e154 = (logit(e154) - z_e95).reshape(-1)
    axis_mixmin = (logit(mixmin) - z_e95).reshape(-1)
    bad_names, bad_basis = e165.bad_axes(sample, z_e95)

    sources = source_rows()
    rows: list[dict[str, Any]] = []
    selected_pred: np.ndarray | None = None
    selected_row: pd.DataFrame | None = None

    for src_rank, source in enumerate(sources.itertuples(index=False), start=1):
        try:
            p_src = load_prob_path(str(source.path), sample)
        except Exception:
            continue
        src_move = logit(p_src) - z_e95
        src_norm = float(np.linalg.norm(src_move))
        for scale in SCALES:
            z = z_e95 + scale * src_move
            pred = clip_prob(sigmoid(z))
            move = (z - z_e95).reshape(-1)
            hard = e164.hard_breadth_metrics(pred, e95, priors)
            bad_cos = {f"cos_bad_{name}": cosine(move, bad_basis[i]) for i, name in enumerate(bad_names)}
            max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
            max_bad_cos = float(bad_cos[f"cos_bad_{max_bad_name}"])
            bad_energy, bad_resid = e165.span_energy(move, bad_basis)
            entropy_delta = float(np.mean(e165.binary_entropy(pred) - e165.binary_entropy(e95)))
            expected_delta = float(hard["expected_delta_focus_mean"])
            abs_expected = abs(expected_delta)
            mean_abs_move = float(np.mean(np.abs(move)))
            max_abs_move = float(np.max(np.abs(move)))
            q2s3_share = e164.target_group_share(move.reshape(len(sample), len(TARGETS)), {"Q2", "S3"})
            top1_ratio = float(hard["top1_over_abs_expected"])
            cells_to_flip = int(hard["cells_to_flip_expected_focus_mean"])
            scaled_sensor_gate = bool(
                expected_delta <= -0.00020
                and cells_to_flip >= 15
                and top1_ratio <= 0.18
                and bad_energy < 0.60
                and max_bad_cos < 0.50
                and -0.0025 <= entropy_delta <= 0.0030
                and 0.002 <= mean_abs_move <= 0.020
                and max_abs_move <= 0.160
                and q2s3_share <= 0.38
                and str(source.source_kind) == "e165_health_survivor"
            )
            material_gate = bool(scaled_sensor_gate and scale <= 0.030)
            sensor_score = (
                max(-expected_delta, 0.0)
                * min(cells_to_flip, 100)
                / 100.0
                * max(1.0 - bad_energy, 0.0)
                / max(top1_ratio, 0.02)
                / max(mean_abs_move / 0.010, 0.35)
            )
            rec: dict[str, Any] = {
                "source_rank": src_rank,
                "source_kind": str(source.source_kind),
                "source_path": str(source.path),
                "source_file": str(source.file),
                "source_family": str(source.family),
                "source_known_public_lb": getattr(source, "known_public_lb", np.nan),
                "source_known_delta_vs_e95": getattr(source, "known_delta_vs_e95", np.nan),
                "source_e164_broad_edge_score": getattr(source, "e164_broad_edge_score", np.nan),
                "source_e164_expected_delta_vs_e95": getattr(source, "e164_expected_delta_vs_e95", np.nan),
                "source_bad_span_energy": getattr(source, "bad_span_energy", np.nan),
                "source_max_bad_cos": getattr(source, "max_bad_cos", np.nan),
                "source_geometry_health_gate": bool(getattr(source, "geometry_health_gate", False)),
                "source_move_norm_vs_e95": src_norm,
                "scale": scale,
                "scaled_expected_delta_focus_mean": expected_delta,
                "scaled_moved_cells": int(hard["moved_cells"]),
                "scaled_moved_rows": int(hard["moved_rows"]),
                "scaled_targets_moved": str(hard["targets_moved"]),
                "scaled_cells_to_flip_expected": cells_to_flip,
                "scaled_cells_for_2e6_guard": int(hard["cells_for_2e6_guard"]),
                "scaled_cells_for_e95_edge": int(hard["cells_for_e95_edge"]),
                "scaled_top1_over_abs_expected": top1_ratio,
                "scaled_top5_over_abs_expected": float(hard["top5_over_abs_expected"]),
                "scaled_support_prob_swing_weighted_focus_mean": float(
                    hard["support_prob_swing_weighted_focus_mean"]
                ),
                "bad_span_energy": bad_energy,
                "bad_span_residual": bad_resid,
                "max_bad_axis": max_bad_name,
                "max_bad_cos": max_bad_cos,
                "entropy_delta_vs_e95": entropy_delta,
                "mean_abs_logit_move_vs_e95": mean_abs_move,
                "max_abs_logit_move_vs_e95": max_abs_move,
                "q2s3_share_vs_e95": q2s3_share,
                "cos_e154_axis": cosine(move, axis_e154),
                "cos_e101_axis": cosine(move, axis_e101),
                "cos_mixmin_axis": cosine(move, axis_mixmin),
                "scaled_sensor_gate": scaled_sensor_gate,
                "material_gate": material_gate,
                "sensor_score": float(sensor_score),
            }
            rec.update(bad_cos)
            rows.append(rec)

    scored = pd.DataFrame(rows)
    if not scored.empty:
        material = scored[scored["material_gate"].fillna(False)].copy()
        if not material.empty:
            material = material.sort_values(["scale", "sensor_score", "scaled_expected_delta_focus_mean"], ascending=[True, False, True])
            choice = material.iloc[[0]].copy()
            p_src = load_prob_path(str(choice.iloc[0]["source_path"]), sample)
            pred = clip_prob(sigmoid(z_e95 + float(choice.iloc[0]["scale"]) * (logit(p_src) - z_e95)))
            digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
            scale_tag = str(float(choice.iloc[0]["scale"])).replace(".", "p").replace("0p", "0p")
            file_name = f"submission_e166_broadsurv_s{scale_tag}_{digest}.csv"
            out_path = OUT / file_name
            sub = sample[KEYS].copy()
            sub[TARGETS] = pred
            sub.to_csv(out_path, index=False)
            choice.loc[:, "materialized_file"] = file_name
            selected_row = choice
            selected_pred = pred

    stats = {
        "sources": int(len(sources)),
        "rows": int(len(scored)),
        "negative_control_rows": int(scored["source_kind"].ne("e165_health_survivor").sum()) if not scored.empty else 0,
        "scaled_sensor_gate_rows": int(scored["scaled_sensor_gate"].sum()) if not scored.empty else 0,
        "material_gate_rows": int(scored["material_gate"].sum()) if not scored.empty else 0,
        "bad_axes": ",".join(bad_names),
        "selected_file": "" if selected_row is None else str(selected_row.iloc[0]["materialized_file"]),
    }
    return scored, stats, selected_row, selected_pred


def write_outputs(scored: pd.DataFrame, stats: dict[str, Any], selected_row: pd.DataFrame | None) -> None:
    scored.to_csv(SUMMARY_OUT, index=False)
    controls = scored[scored["source_kind"].ne("e165_health_survivor")].copy()
    controls.to_csv(CONTROLS_OUT, index=False)
    shortlist = scored.sort_values(
        ["material_gate", "scaled_sensor_gate", "sensor_score", "scale"],
        ascending=[False, False, False, True],
    ).head(120)
    shortlist.to_csv(SHORTLIST_OUT, index=False)

    gated = scored[scored["scaled_sensor_gate"].fillna(False)].copy()
    material = scored[scored["material_gate"].fillna(False)].copy()
    bad_control_gated = controls[controls["scaled_sensor_gate"].fillna(False)].copy()
    selected = pd.DataFrame() if selected_row is None else selected_row

    lines = [
        "# E166 Broad Survivor Scale Probe",
        "",
        "## Question",
        "",
        "Can an E95-to-E165-survivor tiny logit step keep a broad hard-label edge while avoiding known public-bad geometry?",
        "",
        "## Summary",
        "",
        f"- source directions: `{stats['sources']}`.",
        f"- scaled rows scored: `{stats['rows']}`.",
        f"- negative-control scaled rows: `{stats['negative_control_rows']}`.",
        f"- scaled sensor-gate rows: `{stats['scaled_sensor_gate_rows']}`.",
        f"- material-gate rows with scale <= 0.03: `{stats['material_gate_rows']}`.",
        f"- bad axes: `{stats['bad_axes']}`.",
        f"- materialized file: `{stats['selected_file'] or 'none'}`.",
        "",
        "## Selected Materialized Row",
        "",
        md_table(
            selected,
            [
                "materialized_file",
                "source_file",
                "scale",
                "sensor_score",
                "scaled_expected_delta_focus_mean",
                "scaled_cells_to_flip_expected",
                "scaled_top1_over_abs_expected",
                "bad_span_energy",
                "max_bad_axis",
                "max_bad_cos",
                "entropy_delta_vs_e95",
                "mean_abs_logit_move_vs_e95",
                "max_abs_logit_move_vs_e95",
                "q2s3_share_vs_e95",
                "cos_e154_axis",
                "cos_e101_axis",
                "cos_mixmin_axis",
            ],
            5,
        ),
        "",
        "## Top Sensor Rows",
        "",
        md_table(
            shortlist,
            [
                "source_file",
                "scale",
                "scaled_sensor_gate",
                "material_gate",
                "sensor_score",
                "scaled_expected_delta_focus_mean",
                "scaled_cells_to_flip_expected",
                "scaled_top1_over_abs_expected",
                "bad_span_energy",
                "max_bad_axis",
                "max_bad_cos",
                "mean_abs_logit_move_vs_e95",
                "max_abs_logit_move_vs_e95",
                "entropy_delta_vs_e95",
                "q2s3_share_vs_e95",
            ],
            40,
        ),
        "",
        "## Negative-Control Gate Check",
        "",
        md_table(
            controls.sort_values(["scaled_sensor_gate", "sensor_score"], ascending=[False, False]),
            [
                "source_kind",
                "source_file",
                "scale",
                "source_known_public_lb",
                "scaled_sensor_gate",
                "scaled_expected_delta_focus_mean",
                "scaled_cells_to_flip_expected",
                "bad_span_energy",
                "max_bad_axis",
                "max_bad_cos",
                "mean_abs_logit_move_vs_e95",
            ],
            30,
        ),
        "",
        "## Decision",
        "",
        "If the materialized row exists, it is not a JEPA full-model submission. It is a small-amplitude broad-world sensor: E95 remains the anchor, and only a controlled fraction of the broad survivor direction is grafted in. A public win would strengthen the claim that E95 is missing a broad latent branch; a loss would weaken broad-survivor geometry and push the search back to repaired-branch/hidden-label-resolution sensors.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    scored, stats, selected_row, _ = score_scaled()
    write_outputs(scored, stats, selected_row)
    print(REPORT_OUT)
    if stats["selected_file"]:
        print(OUT / stats["selected_file"])


if __name__ == "__main__":
    main()
