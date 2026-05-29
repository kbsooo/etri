#!/usr/bin/env python3
"""E165: LeJEPA-style bad-axis geometry stress for E164 broad candidates.

E164 found many broad post-E95 candidates, but known-public bad LeJEPA also
passes the broad-edge gate. This audit rejects shortcut/collapse candidates by
asking whether E164's broad rows live in the span of known public-bad moves.

No public labels are fitted and no submission is generated.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit, locate  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


E164_SUMMARY = OUT / "e164_universe_broad_edge_screen_summary.csv"
SCORED_OUT = OUT / "e165_broad_edge_bad_axis_geometry_scored.csv"
SHORTLIST_OUT = OUT / "e165_broad_edge_bad_axis_geometry_shortlist.csv"
REPORT_OUT = OUT / "e165_broad_edge_bad_axis_geometry_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"

BAD_PUBLIC = {
    "a2c8": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "stage2": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "ordinal": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "final9": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "e72": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "q2_bad": "submission_jepa_latent_q2_w0p45.csv",
    "lejepa_bad": "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "resid_bad": "submission_jepa_latent_residual_probe.csv",
}

REFERENCE_PUBLIC = {
    E95_FILE: 0.5762913298,
    E101_FILE: 0.5763003660,
    MIXMIN_FILE: 0.5763066405,
    "submission_e72_topabs50_q2s3_gate_4e48cba2.csv": 0.5764077772,
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def binary_entropy(p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= 1.0e-15:
        return 0.0
    return float(np.dot(aa, bb) / den)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), floatfmt)


def load_prob(file_name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    frame = load_sub(file_name, sample)
    return clip_prob(frame[TARGETS].to_numpy(dtype=np.float64))


def bad_axes(sample: pd.DataFrame, z_e95: np.ndarray) -> tuple[list[str], np.ndarray]:
    names: list[str] = []
    vecs: list[np.ndarray] = []
    for name, file_name in BAD_PUBLIC.items():
        if locate(file_name) is None:
            continue
        p = load_prob(file_name, sample)
        v = (logit(p) - z_e95).reshape(-1)
        norm = float(np.linalg.norm(v))
        if norm <= 1.0e-15:
            continue
        names.append(name)
        vecs.append(v / norm)
    if not vecs:
        raise RuntimeError("no bad axes loaded")
    return names, np.vstack(vecs)


def span_energy(move: np.ndarray, basis_rows: np.ndarray) -> tuple[float, float]:
    v = np.asarray(move, dtype=np.float64).reshape(-1)
    norm = float(np.linalg.norm(v))
    if norm <= 1.0e-15:
        return 0.0, 1.0
    # Orthonormalize row-basis through SVD of B.T.
    u, s, _ = np.linalg.svd(basis_rows.T, full_matrices=False)
    rank = int(np.sum(s > 1.0e-10))
    if rank == 0:
        return 0.0, 1.0
    q = u[:, :rank]
    proj = q @ (q.T @ v)
    energy = float(np.linalg.norm(proj) / norm)
    resid = float(np.linalg.norm(v - proj) / norm)
    return energy, resid


def path_to_load(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


def score() -> tuple[pd.DataFrame, dict[str, Any]]:
    e164 = pd.read_csv(E164_SUMMARY)
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e95 = load_prob(E95_FILE, sample)
    z_e95 = logit(e95)
    e154 = load_prob(E154_FILE, sample)
    e101 = load_prob(E101_FILE, sample)
    mixmin = load_prob(MIXMIN_FILE, sample)

    bad_names, bad_basis = bad_axes(sample, z_e95)
    axis_e154 = (logit(e154) - z_e95).reshape(-1)
    axis_e101 = (logit(e101) - z_e95).reshape(-1)
    axis_mixmin = (logit(mixmin) - z_e95).reshape(-1)

    selected = e164[
        e164["candidate_gate"].fillna(False)
        | e164["broad_edge_gate"].fillna(False)
        | e164["file"].isin(REFERENCE_PUBLIC)
    ].copy()
    rows: list[dict[str, Any]] = []
    for row in selected.itertuples(index=False):
        path = path_to_load(str(row.path))
        try:
            pred = load_prob(path, sample)
        except Exception:
            continue
        move = (logit(pred) - z_e95).reshape(-1)
        norm = float(np.linalg.norm(move))
        bad_cos = {f"cos_bad_{name}": cosine(move, bad_basis[i]) for i, name in enumerate(bad_names)}
        max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
        max_bad_cos = float(bad_cos[f"cos_bad_{max_bad_name}"])
        bad_energy, bad_resid = span_energy(move, bad_basis)
        entropy_delta = float(np.mean(binary_entropy(pred) - binary_entropy(e95)))
        rec: dict[str, Any] = {
            "path": str(row.path),
            "file": str(row.file),
            "family": str(row.family),
            "known_public_lb": getattr(row, "known_public_lb"),
            "known_delta_vs_e95": getattr(row, "known_delta_vs_e95"),
            "e164_candidate_gate": bool(getattr(row, "candidate_gate")),
            "e164_broad_edge_gate": bool(getattr(row, "broad_edge_gate")),
            "e164_broad_edge_score": float(getattr(row, "broad_edge_score")),
            "e164_expected_delta_vs_e95": float(getattr(row, "vs_e95_expected_delta_focus_mean")),
            "e164_cells_to_flip_expected": int(getattr(row, "vs_e95_cells_to_flip_expected_focus_mean")),
            "move_norm_vs_e95": norm,
            "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move))),
            "max_abs_logit_move_vs_e95": float(np.max(np.abs(move))),
            "entropy_delta_vs_e95": entropy_delta,
            "bad_span_energy": bad_energy,
            "bad_span_residual": bad_resid,
            "max_bad_axis": max_bad_name,
            "max_bad_cos": max_bad_cos,
            "cos_e154_axis": cosine(move, axis_e154),
            "cos_e101_axis": cosine(move, axis_e101),
            "cos_mixmin_axis": cosine(move, axis_mixmin),
        }
        rec.update(bad_cos)
        rec["geometry_health_gate"] = bool(
            rec["e164_candidate_gate"]
            and rec["bad_span_energy"] < 0.60
            and rec["max_bad_cos"] < 0.50
            and rec["entropy_delta_vs_e95"] > -0.015
        )
        rows.append(rec)
    scored = pd.DataFrame(rows)
    stats = {
        "bad_axes": ",".join(bad_names),
        "input_rows": int(len(e164)),
        "selected_rows": int(len(selected)),
        "scored_rows": int(len(scored)),
        "e164_candidate_rows_scored": int(scored["e164_candidate_gate"].sum()) if not scored.empty else 0,
        "geometry_health_rows": int(scored["geometry_health_gate"].sum()) if not scored.empty else 0,
    }
    return scored, stats


def write_outputs(scored: pd.DataFrame, stats: dict[str, Any]) -> None:
    shortlist = scored.sort_values(
        ["geometry_health_gate", "e164_broad_edge_score", "bad_span_energy"],
        ascending=[False, False, True],
    ).head(120)
    known = scored[scored["known_public_lb"].notna()].sort_values("known_public_lb").copy()
    scored.to_csv(SCORED_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)

    health = scored[scored["geometry_health_gate"].fillna(False)].copy()
    known_bad_broad = known[known["known_delta_vs_e95"].gt(0) & known["e164_broad_edge_gate"].fillna(False)].copy()

    lines = [
        "# E165 Broad Edge Bad-Axis Geometry",
        "",
        "## Question",
        "",
        "Do E164 broad candidates represent a new broad world law, or do they fall into known public-bad/collapse geometry?",
        "",
        "## Summary",
        "",
        f"- bad axes used: `{stats['bad_axes']}`.",
        f"- E164 rows: `{stats['input_rows']}`; selected/scored rows: `{stats['selected_rows']}` / `{stats['scored_rows']}`.",
        f"- E164 candidate-gate rows scored: `{stats['e164_candidate_rows_scored']}`.",
        f"- geometry-health survivor rows: `{stats['geometry_health_rows']}`.",
        f"- known public-bad broad rows: `{len(known_bad_broad)}`.",
        "",
        "## Known-Public Calibration",
        "",
        md_table(
            known,
            [
                "file",
                "known_public_lb",
                "known_delta_vs_e95",
                "e164_broad_edge_gate",
                "e164_candidate_gate",
                "geometry_health_gate",
                "e164_expected_delta_vs_e95",
                "bad_span_energy",
                "bad_span_residual",
                "max_bad_axis",
                "max_bad_cos",
                "entropy_delta_vs_e95",
                "cos_e154_axis",
            ],
            30,
        ),
        "",
        "## Geometry-Health Survivors",
        "",
        md_table(
            health.sort_values("e164_broad_edge_score", ascending=False),
            [
                "file",
                "family",
                "e164_broad_edge_score",
                "e164_expected_delta_vs_e95",
                "bad_span_energy",
                "bad_span_residual",
                "max_bad_axis",
                "max_bad_cos",
                "entropy_delta_vs_e95",
                "cos_e154_axis",
                "cos_e101_axis",
                "mean_abs_logit_move_vs_e95",
            ],
            50,
        ),
        "",
        "## Top Scored Rows",
        "",
        md_table(
            shortlist,
            [
                "file",
                "family",
                "geometry_health_gate",
                "e164_broad_edge_score",
                "e164_expected_delta_vs_e95",
                "bad_span_energy",
                "bad_span_residual",
                "max_bad_axis",
                "max_bad_cos",
                "entropy_delta_vs_e95",
                "cos_e154_axis",
                "cos_e101_axis",
                "mean_abs_logit_move_vs_e95",
            ],
            50,
        ),
        "",
        "## Decision",
        "",
        "A broad edge is only actionable if it is also geometrically healthy against known public-bad axes. Rows that are broad but high-energy in the bad span are evidence for collapse/shortcut, not submissions.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scored, stats = score()
    write_outputs(scored, stats)
    print(stats)
    cols = [
        "file",
        "family",
        "geometry_health_gate",
        "e164_broad_edge_score",
        "e164_expected_delta_vs_e95",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "entropy_delta_vs_e95",
        "cos_e154_axis",
    ]
    print(scored.sort_values(["geometry_health_gate", "e164_broad_edge_score"], ascending=[False, False])[cols].head(40).to_string(index=False))


if __name__ == "__main__":
    main()
