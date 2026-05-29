#!/usr/bin/env python3
"""E117 E95-like neighborhood audit.

SAUNA question:
If E95 survived because the public world prefers S-heavy hard-tail surgery,
then the existing documented submission universe should contain nearby
alternatives with the same anatomy. If it does not, the 0.57629 plateau is less
surprising: the observed frontier is a narrow target-axis/tail compromise, not
an abundant family that a better selector merely failed to rank.

This script does not train or generate a submission. It scans only submission
files already referenced by reports/logs, deduplicates prediction tensors, and
measures movement geometry around mixmin and E95.
"""

from __future__ import annotations

import hashlib
import math
import re
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, locate, load_sub, logit  # noqa: E402
import e94_soft_health_hard_tail_audit as e94  # noqa: E402


MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"

KNOWN_PUBLIC = {
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    MIXMIN_FILE: 0.5763066405,
    E72_FILE: 0.5764077772,
    E95_FILE: 0.5762913298,
}

SUMMARY_OUT = OUT / "e117_e95_like_neighborhood_summary.csv"
SHORTLIST_OUT = OUT / "e117_e95_like_neighborhood_shortlist.csv"
TARGET_OUT = OUT / "e117_e95_like_neighborhood_target_detail.csv"
REPORT_OUT = OUT / "e117_e95_like_neighborhood_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def entropy(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    av = np.asarray(a, dtype=np.float64).reshape(-1)
    bv = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom <= 1.0e-18:
        return math.nan
    return float(np.dot(av, bv) / denom)


def tensor_key(p: np.ndarray) -> str:
    rounded = np.round(np.asarray(p, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def collect_referenced_submission_names() -> list[str]:
    names: set[str] = {MIXMIN_FILE, E72_FILE, E95_FILE, E101_FILE}
    md_files: list[Path] = []
    md_files.extend(ROOT.glob("*.md"))
    md_files.extend(OUT.glob("*report.md"))
    md_files.extend(JEPA.glob("*report.md"))
    pattern = re.compile(r"(?:analysis_outputs/|jepa/)?(submission[A-Za-z0-9_.-]+\.csv)")
    for path in md_files:
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for match in pattern.findall(text):
            names.add(Path(match).name)
    return sorted(names)


def load_prob(name: str, sample: pd.DataFrame) -> np.ndarray | None:
    path = locate(name)
    if path is None:
        return None
    try:
        frame = load_sub(path, sample)
    except Exception:
        return None
    return clip_prob(frame[TARGETS].to_numpy(dtype=np.float64))


def shares(abs_delta: np.ndarray) -> dict[str, float]:
    total = float(abs_delta.sum())
    out: dict[str, float] = {}
    q_mask = np.array([t.startswith("Q") for t in TARGETS], dtype=bool)
    s_mask = ~q_mask
    q2s3_mask = np.array([t in {"Q2", "S3"} for t in TARGETS], dtype=bool)
    s123_mask = np.array([t in {"S1", "S2", "S3"} for t in TARGETS], dtype=bool)
    out["q_l1_share"] = float(abs_delta[:, q_mask].sum() / total) if total else 0.0
    out["s_l1_share"] = float(abs_delta[:, s_mask].sum() / total) if total else 0.0
    out["q2s3_l1_share"] = float(abs_delta[:, q2s3_mask].sum() / total) if total else 0.0
    out["s123_l1_share"] = float(abs_delta[:, s123_mask].sum() / total) if total else 0.0
    for j, target in enumerate(TARGETS):
        out[f"share_{target}"] = float(abs_delta[:, j].sum() / total) if total else 0.0
    return out


def e72_tail_setup(mixmin: np.ndarray, e72: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    delta = logit(e72) - logit(mixmin)
    weight = np.abs(delta)
    wrong_is_zero = delta > 1.0e-9
    wrong_is_one = delta < -1.0e-9
    return delta, weight, wrong_is_zero, wrong_is_one


def e72_adverse_metrics(
    pred: np.ndarray,
    base: np.ndarray,
    e72_weight: np.ndarray,
    wrong_is_zero: np.ndarray,
    wrong_is_one: np.ndarray,
) -> dict[str, float]:
    d0, d1 = e94.hard_loss_deltas(pred, base)
    adverse = np.where(wrong_is_zero, d0, np.where(wrong_is_one, d1, 0.0))
    positive = np.maximum(adverse, 0.0)
    return {
        "e72_adverse_positive_exposure_all": float(np.mean(positive)),
        "e72_adverse_weighted_positive_mean": e94.safe_weighted_mean(positive, e72_weight),
        "e72_adverse_positive_weight_frac": e94.safe_weighted_mean((adverse > 0).astype(float), e72_weight),
        "kl_if_mixmin_calibrated": float(np.mean(base * d1 + (1.0 - base) * d0)),
    }


def row_metrics(
    name: str,
    p: np.ndarray,
    mixmin: np.ndarray,
    e95: np.ndarray,
    e95_dir: np.ndarray,
    e72_weight: np.ndarray,
    wrong_is_zero: np.ndarray,
    wrong_is_one: np.ndarray,
) -> dict[str, object]:
    prob_delta = p - mixmin
    abs_prob = np.abs(prob_delta)
    z_delta = logit(p) - logit(mixmin)
    active = abs_prob > 1.0e-7
    rel_e95_prob = p - e95
    abs_rel_e95 = np.abs(rel_e95_prob)
    rel_e95_active = abs_rel_e95 > 1.0e-7
    rec: dict[str, object] = {
        "file": name,
        "public_lb": KNOWN_PUBLIC.get(name, math.nan),
        "public_delta_vs_e95": (
            KNOWN_PUBLIC[name] - KNOWN_PUBLIC[E95_FILE] if name in KNOWN_PUBLIC else math.nan
        ),
        "active_cells_vs_mixmin": int(active.sum()),
        "active_rows_vs_mixmin": int(active.any(axis=1).sum()),
        "l1_prob_vs_mixmin": float(abs_prob.sum()),
        "mean_abs_prob_vs_mixmin": float(abs_prob.mean()),
        "max_abs_prob_vs_mixmin": float(abs_prob.max()),
        "l1_logit_vs_mixmin": float(np.abs(z_delta).sum()),
        "mean_abs_logit_vs_mixmin": float(np.abs(z_delta).mean()),
        "max_abs_logit_vs_mixmin": float(np.abs(z_delta).max()),
        "entropy_delta_vs_mixmin": float((entropy(p) - entropy(mixmin)).mean()),
        "cosine_with_e95_from_mixmin": cosine(z_delta, e95_dir),
        "active_cells_vs_e95": int(rel_e95_active.sum()),
        "active_rows_vs_e95": int(rel_e95_active.any(axis=1).sum()),
        "l1_prob_vs_e95": float(abs_rel_e95.sum()),
        "max_abs_prob_vs_e95": float(abs_rel_e95.max()),
    }
    rec.update(shares(abs_prob))
    rec.update(
        {
            f"e95rel_{k}": v
            for k, v in shares(abs_rel_e95).items()
        }
    )
    rec.update(e72_adverse_metrics(p, mixmin, e72_weight, wrong_is_zero, wrong_is_one))
    return rec


def target_detail_rows(name: str, p: np.ndarray, mixmin: np.ndarray, e95: np.ndarray) -> Iterable[dict[str, object]]:
    for j, target in enumerate(TARGETS):
        delta = p[:, j] - mixmin[:, j]
        rel = p[:, j] - e95[:, j]
        yield {
            "file": name,
            "target": target,
            "l1_prob_vs_mixmin": float(np.abs(delta).sum()),
            "active_cells_vs_mixmin": int((np.abs(delta) > 1.0e-7).sum()),
            "mean_signed_prob_delta_vs_mixmin": float(delta.mean()),
            "max_abs_prob_vs_mixmin": float(np.abs(delta).max()),
            "l1_prob_vs_e95": float(np.abs(rel).sum()),
            "active_cells_vs_e95": int((np.abs(rel) > 1.0e-7).sum()),
            "mean_signed_prob_delta_vs_e95": float(rel.mean()),
            "max_abs_prob_vs_e95": float(np.abs(rel).max()),
        }


def markdown_table(frame: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    if frame.empty:
        return "_empty_"
    view = frame[cols].head(n).copy()
    headers = [str(c) for c in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in view.to_dict("records"):
        row = []
        for col in view.columns:
            val = rec[col]
            if isinstance(val, (float, np.floating)):
                row.append("" if pd.isna(val) else f"{float(val):.9f}")
            else:
                row.append(str(val))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_prob(MIXMIN_FILE, sample)
    e72 = load_prob(E72_FILE, sample)
    e95 = load_prob(E95_FILE, sample)
    if mixmin is None or e72 is None or e95 is None:
        raise RuntimeError("required anchor file missing")
    e95_dir = logit(e95) - logit(mixmin)
    _, e72_weight, wrong_is_zero, wrong_is_one = e72_tail_setup(mixmin, e72)

    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    seen: dict[str, str] = {}
    resolved = 0
    missing = 0
    duplicate = 0
    for name in collect_referenced_submission_names():
        p = load_prob(name, sample)
        if p is None:
            missing += 1
            continue
        resolved += 1
        key = tensor_key(p)
        if key in seen:
            duplicate += 1
            continue
        seen[key] = name
        rows.append(row_metrics(name, p, mixmin, e95, e95_dir, e72_weight, wrong_is_zero, wrong_is_one))
        target_rows.extend(target_detail_rows(name, p, mixmin, e95))

    summary = pd.DataFrame(rows)
    target_detail = pd.DataFrame(target_rows)
    if summary.empty:
        raise RuntimeError("no submission files resolved")

    e95_row = summary[summary["file"].eq(E95_FILE)].iloc[0]
    e101_row = summary[summary["file"].eq(E101_FILE)].iloc[0] if summary["file"].eq(E101_FILE).any() else None
    e95_l1 = float(e95_row["l1_prob_vs_mixmin"])
    e95_tail = float(e95_row["e72_adverse_positive_exposure_all"])

    non_anchor = summary[~summary["file"].eq(E95_FILE)].copy()
    non_anchor["e95_like_l1_ratio"] = non_anchor["l1_prob_vs_mixmin"] / max(e95_l1, 1.0e-12)
    non_anchor["e95_like_tail_ratio"] = non_anchor["e72_adverse_positive_exposure_all"] / max(e95_tail, 1.0e-12)
    non_anchor["e95_like_score"] = (
        2.0 * (1.0 - non_anchor["cosine_with_e95_from_mixmin"].fillna(-1.0))
        + 2.0 * non_anchor["q_l1_share"]
        + 0.7 * np.abs(np.log(np.clip(non_anchor["e95_like_l1_ratio"], 1.0e-9, None)))
        + 1.0 * np.maximum(non_anchor["e95_like_tail_ratio"] - 1.0, 0.0)
        + 0.2 * np.maximum(0.45 - non_anchor["e95_like_l1_ratio"], 0.0)
    )

    # The "neighborhood" deliberately excludes tiny near-zero files and broad
    # all-target candidates. It asks whether something plausibly comparable to
    # E95 already existed.
    neighborhood = non_anchor[
        non_anchor["l1_prob_vs_mixmin"].between(0.45 * e95_l1, 1.60 * e95_l1)
        & non_anchor["s_l1_share"].ge(0.85)
        & non_anchor["q_l1_share"].le(0.15)
        & non_anchor["cosine_with_e95_from_mixmin"].ge(0.60)
    ].copy()
    neighborhood = neighborhood.sort_values(
        [
            "e95_like_score",
            "e72_adverse_positive_exposure_all",
            "l1_prob_vs_e95",
            "file",
        ]
    ).reset_index(drop=True)

    e95_like_better_tail = neighborhood[
        neighborhood["e72_adverse_positive_exposure_all"].le(e95_tail)
        & neighborhood["l1_prob_vs_e95"].gt(1.0e-9)
    ].copy()
    e95_like_surgical = neighborhood[
        neighborhood["active_cells_vs_e95"].le(250)
        & neighborhood["l1_prob_vs_e95"].gt(1.0e-9)
    ].copy()

    summary = summary.sort_values(
        ["cosine_with_e95_from_mixmin", "s_l1_share", "l1_prob_vs_e95"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    neighborhood.to_csv(SHORTLIST_OUT, index=False)

    known = summary[summary["public_lb"].notna()].sort_values("public_lb")
    top_cols = [
        "file",
        "e95_like_score",
        "cosine_with_e95_from_mixmin",
        "l1_prob_vs_mixmin",
        "l1_prob_vs_e95",
        "q_l1_share",
        "s_l1_share",
        "q2s3_l1_share",
        "e72_adverse_positive_exposure_all",
        "e72_adverse_weighted_positive_mean",
        "active_cells_vs_e95",
    ]
    known_cols = [
        "file",
        "public_lb",
        "public_delta_vs_e95",
        "cosine_with_e95_from_mixmin",
        "l1_prob_vs_mixmin",
        "q_l1_share",
        "s_l1_share",
        "e72_adverse_positive_exposure_all",
    ]

    e101_line = ""
    if e101_row is not None:
        e101_line = (
            f"- E101 is not an E95-like replacement from mixmin; it is an E95-relative "
            f"micro edit: active cells vs E95 `{int(e101_row['active_cells_vs_e95'])}`, "
            f"L1 vs E95 `{float(e101_row['l1_prob_vs_e95']):.6f}`, "
            f"E95-relative Q2/S3 share `{float(e101_row['e95rel_q2s3_l1_share']):.6f}`.\n"
        )

    report = f"""# E117 E95-Like Neighborhood Audit

## Question

If the E95 hardtail law is real but underexploited, does the documented
submission universe contain another E95-shaped candidate already waiting nearby?

## Method

- Collected submission filenames referenced by root notes and generated reports.
- Resolved files with the existing local locator, deduplicated exact prediction tensors.
- Compared each unique candidate to mixmin and E95 using target-axis movement,
  E95-direction cosine, Q/S share, E72-adverse hard-label exposure, and
  E95-relative edit size.

## Scan Scale

- referenced names: `{len(collect_referenced_submission_names())}`
- resolved files: `{resolved}`
- unique prediction tensors: `{len(summary)}`
- duplicate tensors skipped: `{duplicate}`
- unresolved names skipped: `{missing}`

## Key Observations

- E95 L1 vs mixmin: `{e95_l1:.6f}`.
- E95 E72-adverse positive exposure: `{e95_tail:.9f}`.
- E95-like neighborhood count: `{len(neighborhood)}`.
- E95-like candidates with no higher E72-adverse exposure than E95: `{len(e95_like_better_tail)}`.
- E95-relative surgical variants within 250 changed cells: `{len(e95_like_surgical)}`.
{e101_line}
## Known Public Anchors In This Geometry

{markdown_table(known, known_cols, n=12)}

## Closest Non-E95 Neighborhood

{markdown_table(neighborhood, top_cols, n=15)}

## Interpretation

The useful fact is whether the neighborhood is abundant and clean. If many
large S-heavy, E95-aligned, lower-tail candidates existed, the plateau would
look like a selector failure. If the neighborhood is tiny, dominated by already
known E85/E86/E89/E90/E101-family edits, or does not improve hard-tail exposure,
then E95's small public edge is more natural: it sits near a narrow compromise
between retained structure and public-tail damage.

## Belief Update

- Strengthens H110 if E101 appears as a micro edit rather than a standalone
  E95 replacement: public feedback must decide its branch.
- Strengthens the plateau explanation if no untested, lower-tail, E95-like
  neighbor dominates the current frontier anatomy.
- Weakens the idea that "just search the existing submission universe harder"
  is enough to escape the 0.57629 shelf.

## Outputs

- `{SUMMARY_OUT.name}`
- `{SHORTLIST_OUT.name}`
- `{TARGET_OUT.name}`
"""
    REPORT_OUT.write_text(report)

    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {SHORTLIST_OUT}")
    print(f"wrote {TARGET_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
