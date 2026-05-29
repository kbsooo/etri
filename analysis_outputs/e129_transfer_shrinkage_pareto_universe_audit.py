#!/usr/bin/env python3
"""E129 transfer-shrinkage Pareto universe audit.

SAUNA question:
E128 showed that transfer-shrinkage components are useful vetoes but not a
single selector. This script asks whether those separated vetoes leave any
existing submission-universe candidate that is both low-risk and materially
different from E95.

No submission is generated.
"""

from __future__ import annotations

import hashlib
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e96_public_miss_budget_tail_scenarios as e96  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS, load_sub, logit, locate  # noqa: E402


CELL_IN = OUT / "e127_transfer_shrinkage_cell_summary.csv"
SUMMARY_OUT = OUT / "e129_transfer_shrinkage_pareto_universe_full.csv"
GATE_OUT = OUT / "e129_transfer_shrinkage_pareto_universe_gate_summary.csv"
SHORTLIST_OUT = OUT / "e129_transfer_shrinkage_pareto_universe_shortlist_summary.csv"
REPORT_OUT = OUT / "e129_transfer_shrinkage_pareto_universe_report.md"

MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"

KNOWN_PUBLIC = {
    E95_FILE: 0.5762913298,
    E101_FILE: 0.5763003660,
    MIXMIN_FILE: 0.5763066405,
    E72_FILE: 0.5764077772,
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
}

SAME_FAMILY_RE = re.compile(
    r"(?:e85|e86|e87|e89|e90|e95|e101|e108|hardtail|decontam|pareto|consensus|inverse_conflict)",
    re.IGNORECASE,
)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 20, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame[cols].head(n).copy()
    lines = [
        "| " + " | ".join(str(c) for c in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for rec in view.to_dict("records"):
        vals: list[str] = []
        for col in view.columns:
            val = rec[col]
            if pd.isna(val):
                vals.append("")
            elif isinstance(val, (float, np.floating)):
                vals.append(format(float(val), floatfmt))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.where(np.isfinite(arr), np.maximum(arr, 0.0), 0.0)
    total = float(arr.sum())
    if total <= 0:
        return np.ones_like(arr) / len(arr)
    return arr / total


def weighted_l1(a: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    return float(np.sum(ww * np.abs(a)))


def weighted_rmse(a: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    return float(np.sqrt(np.sum(ww * a * a)))


def weighted_cosine(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    den = float(np.sqrt(np.sum(ww * a * a) * np.sum(ww * b * b)))
    if den <= 1.0e-15:
        return 0.0
    return float(np.sum(ww * a * b) / den)


def weighted_resid_ratio(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    den = float(np.sqrt(np.sum(ww * b * b)))
    if den <= 1.0e-15:
        return np.nan
    return float(np.sqrt(np.sum(ww * (a - b) ** 2)) / den)


def tensor_key(p: np.ndarray) -> str:
    rounded = np.round(np.asarray(p, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def referenced_submission_paths() -> set[Path]:
    paths: set[Path] = set()
    md_files: list[Path] = []
    md_files.extend(ROOT.glob("*.md"))
    md_files.extend(OUT.glob("*report.md"))
    md_files.extend(JEPA.glob("*report.md"))
    pattern = re.compile(r"((?:analysis_outputs/|jepa/)?(?:[A-Za-z0-9_.-]+/)*submission[A-Za-z0-9_.-]+\.csv)")
    for md in md_files:
        try:
            text = md.read_text(errors="ignore")
        except OSError:
            continue
        for raw in pattern.findall(text):
            rel = Path(raw)
            if raw.startswith("analysis_outputs/") or raw.startswith("jepa/"):
                path = ROOT / rel
                if path.exists():
                    paths.add(path.resolve())
                    continue
            found = locate(rel.name)
            if found is not None:
                paths.add(found.resolve())
    return paths


def collect_candidate_paths() -> tuple[list[Path], int]:
    paths = referenced_submission_paths()
    paths.update(p.resolve() for p in OUT.rglob("submission*.csv"))
    paths.update(p.resolve() for p in JEPA.rglob("submission*.csv"))
    return sorted(paths), len(paths)


def load_prob(path: Path, sample: pd.DataFrame) -> np.ndarray | None:
    try:
        frame = load_sub(path, sample)
    except Exception:
        return None
    return np.clip(frame[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def target_share(flat_delta: np.ndarray, mask: np.ndarray) -> float:
    den = float(np.sum(np.abs(flat_delta)))
    if den <= 1.0e-15:
        return 0.0
    return float(np.sum(np.abs(flat_delta)[mask]) / den)


def build_weights() -> dict[str, np.ndarray]:
    cell = pd.read_csv(CELL_IN)
    return {
        "tail_equal": cell["broad_tail_equal_share"].to_numpy(dtype=np.float64),
        "e101_plausible": cell["e101_plausible_share"].to_numpy(dtype=np.float64),
        "q2s3": cell["target_is_q2s3"].astype(float).to_numpy(dtype=np.float64),
        "e101_active": cell["e101_active"].astype(float).to_numpy(dtype=np.float64),
    }


def scan_universe() -> tuple[pd.DataFrame, dict[str, Any]]:
    sample = load_sub(MIXMIN_FILE).sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    mixmin = load_sub(MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e95 = load_sub(E95_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e101 = load_sub(E101_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e72 = load_sub(E72_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)

    lm_mix = logit(mixmin).reshape(-1)
    lm_e95 = logit(e95).reshape(-1)
    lm_e101 = logit(e101).reshape(-1)
    law = lm_e95 - lm_mix
    weights = build_weights()

    failed_e72_delta = logit(e72) - logit(mixmin)
    wrong_is_zero = failed_e72_delta > 1.0e-9
    wrong_is_one = failed_e72_delta < -1.0e-9

    q_mask = np.array([t.startswith("Q") for t in TARGETS] * mixmin.shape[0], dtype=bool)
    s_mask = ~q_mask
    q2s3_col = np.array([t in {"Q2", "S3"} for t in TARGETS] * mixmin.shape[0], dtype=bool)

    paths, raw_path_count = collect_candidate_paths()
    rows: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    skipped_load = 0
    duplicate = 0

    for path in paths:
        pred = load_prob(path, sample)
        if pred is None:
            skipped_load += 1
            continue
        key = tensor_key(pred)
        if key in seen:
            duplicate += 1
            continue
        seen[key] = str(path)
        flat = logit(pred).reshape(-1)
        move_mix = flat - lm_mix
        move_e95 = flat - lm_e95
        move_e101 = flat - lm_e101
        adverse = e96.adverse_delta_for_e72_direction(
            pred,
            mixmin,
            wrong_is_zero.reshape(mixmin.shape),
            wrong_is_one.reshape(mixmin.shape),
        ).reshape(-1)
        pos_adverse = np.maximum(adverse, 0.0)
        active_e95 = np.abs(move_e95) > 1.0e-9
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        rec: dict[str, Any] = {
            "file": path.name,
            "path": str(rel),
            "known_public_lb": KNOWN_PUBLIC.get(path.name, np.nan),
            "public_delta_vs_e95": (
                KNOWN_PUBLIC[path.name] - KNOWN_PUBLIC[E95_FILE] if path.name in KNOWN_PUBLIC else np.nan
            ),
            "same_family_name": bool(SAME_FAMILY_RE.search(path.name)),
            "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move_e95))),
            "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(move_mix))),
            "changed_cells_vs_e95": int(np.sum(active_e95)),
            "changed_rows_vs_e95": int(np.sum(active_e95.reshape(pred.shape).any(axis=1))),
            "tail_equal_law_cosine": weighted_cosine(move_mix, law, weights["tail_equal"]),
            "tail_equal_law_resid_ratio": weighted_resid_ratio(move_mix, law, weights["tail_equal"]),
            "tail_equal_delta95_l1": weighted_l1(move_e95, weights["tail_equal"]),
            "tail_equal_delta101_l1": weighted_l1(move_e101, weights["tail_equal"]),
            "e101_active_delta95_l1": weighted_l1(move_e95, weights["e101_active"]),
            "q2s3_delta95_l1": weighted_l1(move_e95, weights["q2s3"]),
            "e101_plausible_delta95_l1": weighted_l1(move_e95, weights["e101_plausible"]),
            "e72_adverse_exposure_e101_plausible": weighted_l1(pos_adverse, weights["e101_plausible"]),
            "e72_adverse_exposure_tail_equal": weighted_l1(pos_adverse, weights["tail_equal"]),
            "e95rel_q_l1_share": target_share(move_e95, q_mask),
            "e95rel_s_l1_share": target_share(move_e95, s_mask),
            "e95rel_q2s3_l1_share": target_share(move_e95, q2s3_col),
            "e95rel_rmse_tail_equal": weighted_rmse(move_e95, weights["tail_equal"]),
        }
        rec["transfer_shrinkage_risk_index"] = (
            rec["e101_active_delta95_l1"]
            + rec["q2s3_delta95_l1"]
            + 0.5 * rec["e72_adverse_exposure_e101_plausible"]
            - rec["tail_equal_law_cosine"]
        )
        rows.append(rec)

    info = {
        "raw_path_count": raw_path_count,
        "loaded_unique": len(rows),
        "skipped_load": skipped_load,
        "duplicate": duplicate,
    }
    return pd.DataFrame(rows), info


def apply_gates(scores: pd.DataFrame) -> pd.DataFrame:
    e95 = scores[scores["file"].eq(E95_FILE)].iloc[0]
    e101 = scores[scores["file"].eq(E101_FILE)].iloc[0]
    scores = scores.copy()
    scores["gate_cos95_resid025"] = (
        scores["tail_equal_law_cosine"].ge(0.95)
        & scores["tail_equal_law_resid_ratio"].le(0.25)
    )
    scores["gate_active_q2s3_not_more_than_e101"] = (
        scores["e101_active_delta95_l1"].le(float(e101["e101_active_delta95_l1"]) + 1.0e-12)
        & scores["q2s3_delta95_l1"].le(float(e101["q2s3_delta95_l1"]) + 1.0e-12)
    )
    scores["gate_e72_not_more_than_e95"] = scores["e72_adverse_exposure_e101_plausible"].le(
        float(e95["e72_adverse_exposure_e101_plausible"]) + 1.0e-12
    )
    scores["gate_strict_veto"] = (
        scores["gate_cos95_resid025"]
        & scores["gate_active_q2s3_not_more_than_e101"]
        & scores["gate_e72_not_more_than_e95"]
    )
    scores["gate_relaxed_veto"] = (
        scores["tail_equal_law_cosine"].ge(0.90)
        & scores["tail_equal_law_resid_ratio"].le(0.75)
        & scores["e101_active_delta95_l1"].le(float(e101["e101_active_delta95_l1"]) + 1.0e-12)
        & scores["q2s3_delta95_l1"].le(float(e101["q2s3_delta95_l1"]) + 1.0e-12)
        & scores["e72_adverse_exposure_e101_plausible"].le(1.10 * float(e95["e72_adverse_exposure_e101_plausible"]))
    )
    scores["gate_material_vs_e95"] = (
        scores["mean_abs_logit_move_vs_e95"].ge(float(e101["mean_abs_logit_move_vs_e95"]) - 1.0e-12)
        & scores["changed_cells_vs_e95"].gt(0)
    )
    scores["gate_strict_actionable"] = scores["gate_strict_veto"] & scores["gate_material_vs_e95"]
    scores["gate_strict_novel_actionable"] = scores["gate_strict_actionable"] & ~scores["same_family_name"]
    return scores


def gate_summary(scores: pd.DataFrame, info: dict[str, Any]) -> pd.DataFrame:
    gates = [
        "gate_cos95_resid025",
        "gate_active_q2s3_not_more_than_e101",
        "gate_e72_not_more_than_e95",
        "gate_strict_veto",
        "gate_relaxed_veto",
        "gate_material_vs_e95",
        "gate_strict_actionable",
        "gate_strict_novel_actionable",
    ]
    rows: list[dict[str, Any]] = []
    for gate in gates:
        sub = scores[scores[gate]].copy()
        rows.append(
            {
                "gate": gate,
                "count": len(sub),
                "known_public_count": int(sub["known_public_lb"].notna().sum()),
                "same_family_count": int(sub["same_family_name"].sum()),
                "novel_count": int((~sub["same_family_name"]).sum()),
                "max_mean_abs_logit_vs_e95": float(sub["mean_abs_logit_move_vs_e95"].max()) if not sub.empty else np.nan,
                "min_e72_exposure_e101_plausible": float(sub["e72_adverse_exposure_e101_plausible"].min()) if not sub.empty else np.nan,
            }
        )
    rows.append({"gate": "raw_path_count", "count": info["raw_path_count"]})
    rows.append({"gate": "loaded_unique", "count": info["loaded_unique"]})
    rows.append({"gate": "skipped_load", "count": info["skipped_load"]})
    rows.append({"gate": "duplicate_tensor", "count": info["duplicate"]})
    return pd.DataFrame(rows)


def make_shortlist(scores: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "file",
        "path",
        "known_public_lb",
        "public_delta_vs_e95",
        "same_family_name",
        "gate_strict_veto",
        "gate_relaxed_veto",
        "gate_material_vs_e95",
        "gate_strict_actionable",
        "gate_strict_novel_actionable",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_adverse_exposure_e101_plausible",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "e95rel_q2s3_l1_share",
        "transfer_shrinkage_risk_index",
    ]
    parts = [
        scores[scores["gate_strict_actionable"]].sort_values(
            ["same_family_name", "transfer_shrinkage_risk_index", "mean_abs_logit_move_vs_e95"],
            ascending=[True, True, False],
        ),
        scores[scores["gate_relaxed_veto"] & scores["gate_material_vs_e95"]].sort_values(
            ["same_family_name", "e72_adverse_exposure_e101_plausible", "tail_equal_law_resid_ratio"],
            ascending=[True, True, True],
        ).head(50),
        scores[scores["known_public_lb"].notna()].sort_values("known_public_lb"),
    ]
    out = pd.concat(parts, axis=0, ignore_index=True)
    out = out.drop_duplicates("path")
    return out[fields].reset_index(drop=True)


def write_report(scores: pd.DataFrame, gates: pd.DataFrame, shortlist: pd.DataFrame, info: dict[str, Any]) -> None:
    known_cols = [
        "file",
        "public_delta_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_adverse_exposure_e101_plausible",
        "gate_strict_veto",
    ]
    cand_cols = [
        "file",
        "same_family_name",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_adverse_exposure_e101_plausible",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "gate_strict_actionable",
        "gate_strict_novel_actionable",
    ]
    strict = scores[scores["gate_strict_actionable"]].sort_values(
        ["same_family_name", "transfer_shrinkage_risk_index", "mean_abs_logit_move_vs_e95"],
        ascending=[True, True, False],
    )
    relaxed = scores[scores["gate_relaxed_veto"] & scores["gate_material_vs_e95"]].sort_values(
        ["same_family_name", "e72_adverse_exposure_e101_plausible", "tail_equal_law_resid_ratio"],
        ascending=[True, True, True],
    )
    novel_strict_count = int(scores["gate_strict_novel_actionable"].sum())

    report = f"""# E129 Transfer-shrinkage Pareto universe audit

## Question

E128 says transfer-shrinkage should remain disentangled into veto components.
E129 asks whether those components leave a novel, material, existing candidate
in the documented/local submission universe.

## Scan Scale

- candidate paths collected: `{info['raw_path_count']}`
- unique prediction tensors loaded: `{info['loaded_unique']}`
- duplicate tensors skipped: `{info['duplicate']}`
- load/key mismatch skipped: `{info['skipped_load']}`

## Gate Summary

{md_table(gates, list(gates.columns), n=len(gates), floatfmt='.6f')}

## Known Public Anchors

{md_table(scores[scores['known_public_lb'].notna()].sort_values('known_public_lb'), known_cols, n=20, floatfmt='.6f')}

## Strict Actionable Survivors

{md_table(strict, cand_cols, n=30, floatfmt='.6f')}

## Relaxed Material Survivors

{md_table(relaxed, cand_cols, n=30, floatfmt='.6f')}

## Interpretation

- Strict veto means: tail-equal E95-law cosine >= `0.95`, residual <= `0.25`,
  active/Q2S3 rollback no larger than E101, and E101-compatible E72 exposure
  no larger than E95.
- Material means: at least E101-scale mean absolute logit movement vs E95.
- Novel means the filename is outside the current E85/E86/E87/E89/E90/E95/E101/E108
  same-family hardtail line.

Novel strict actionable survivors: `{novel_strict_count}`.

If this count is zero, the separated vetoes do not reveal a hidden old file.
They only recover already-known same-family conservative edits, so the next
step is new representation/movement rather than another existing-universe rank.

## Decision

No submission is generated by E129. Use this as a universe-level falsification
of "E128 vetoes already imply an existing next file."

## Outputs

- `{SUMMARY_OUT.name}` (local ignored full scan table)
- `{GATE_OUT.name}`
- `{SHORTLIST_OUT.name}`
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    scores, info = scan_universe()
    scores = apply_gates(scores)
    gates = gate_summary(scores, info)
    shortlist = make_shortlist(scores)

    scores.sort_values(
        ["gate_strict_novel_actionable", "gate_strict_actionable", "transfer_shrinkage_risk_index"],
        ascending=[False, False, True],
    ).to_csv(SUMMARY_OUT, index=False)
    gates.to_csv(GATE_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(scores, gates, shortlist, info)

    print("Wrote:")
    for path in [SUMMARY_OUT, GATE_OUT, SHORTLIST_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print("\nGate summary:")
    print(gates.to_string(index=False))
    print("\nStrict actionable survivors:")
    cols = [
        "file",
        "same_family_name",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_adverse_exposure_e101_plausible",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "gate_strict_novel_actionable",
    ]
    strict = scores[scores["gate_strict_actionable"]].sort_values(
        ["same_family_name", "transfer_shrinkage_risk_index", "mean_abs_logit_move_vs_e95"],
        ascending=[True, True, False],
    )
    print(strict[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    main()
