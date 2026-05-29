#!/usr/bin/env python3
"""E131 tail-density atom-combo probe.

SAUNA question:
E130 split the E95 neighborhood into two disjoint sets:
local-upside density atoms that are public-tail adverse, and veto-safe atoms
that are too small to matter. This probe asks whether the split is merely
linear: can a local-upside atom be combined with a veto-safe atom, or clipped
on its hard-tail risk cells, to create a material E95 successor?

No labels or public scores are fitted. A submission is materialized only if a
new atom-combo simultaneously beats E95 under local stress, passes the separated
E128/E129 vetoes, and survives the post-E101 sensor-world filter.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402


SCAN_OUT = OUT / "e131_tail_density_atom_combo_probe_scan.csv"
SUMMARY_OUT = OUT / "e131_tail_density_atom_combo_probe_summary.csv"
TRANSFER_OUT = OUT / "e131_tail_density_atom_combo_probe_transfer.csv"
REPORT_OUT = OUT / "e131_tail_density_atom_combo_probe_report.md"
SUBMISSION_PREFIX = "submission_e131_tailatom"

EPS = 1.0e-6
LOCAL_LIMIT = 14
SAFE_LIMIT = 18
MATERIAL_FLOOR = 1.0e-7


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    return hashlib.sha256(np.round(np.asarray(pred, dtype=np.float64), 12).tobytes()).hexdigest()


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen_pred: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
    base_index: int,
) -> None:
    key = pred_key(pred)
    if key in seen_pred:
        pred_index = seen_pred[key]
    else:
        pred_index = len(preds)
        seen_pred[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e131_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def risk_signs(tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    _, _, wrong_is_zero, wrong_is_one = tail_state
    return wrong_is_zero.astype(float) - wrong_is_one.astype(float)


def risk_scalar(delta: np.ndarray, risk_sign: np.ndarray, weights: np.ndarray) -> float:
    adverse = np.maximum(np.asarray(delta, dtype=np.float64) * risk_sign, 0.0)
    w = np.asarray(weights, dtype=np.float64)
    den = float(np.sum(w))
    if den <= 0.0:
        return float(np.mean(adverse))
    return float(np.sum(adverse * w) / den)


def select_atoms(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    variants = scan[scan["strategy"].eq("density_synth")].copy()

    local = variants[
        variants["nonanchor_evaluated"].fillna(False).astype(bool)
        & variants["strict_gate"].fillna(False).astype(bool)
        & variants["all_minus_base"].lt(0.0)
    ].copy()
    local = (
        local.sort_values(
            [
                "all_minus_base",
                "post101_mean_vs_e95_e101_sensor",
                "e72_adverse_positive_exposure_all",
            ],
            ascending=[True, True, True],
        )
        .drop_duplicates(["source", "mask_name", "alpha"])
        .head(LOCAL_LIMIT)
        .reset_index(drop=True)
    )

    # Use separated veto-survivors as correction atoms, but force material rows
    # first. The small local-negative safe rows are included as near-null controls.
    safe_pool = variants[
        variants["gate_strict_veto"].fillna(False).astype(bool)
        & variants["mean_abs_logit_move_vs_e95"].fillna(0.0).gt(0.0)
    ].copy()
    safe_pool["safe_rank_score"] = (
        safe_pool["gate_strict_actionable"].fillna(False).astype(float) * -10.0
        + safe_pool["e72_adverse_positive_exposure_all"].fillna(np.inf)
        + safe_pool["q2s3_delta95_l1"].fillna(np.inf)
        + safe_pool["e101_active_delta95_l1"].fillna(np.inf)
        - 0.25 * safe_pool["tail_equal_law_cosine"].fillna(0.0)
    )
    safe = (
        safe_pool.sort_values(
            [
                "gate_strict_actionable",
                "safe_rank_score",
                "mean_abs_logit_move_vs_e95",
            ],
            ascending=[False, True, False],
        )
        .drop_duplicates(["source", "mask_name", "alpha"])
        .head(SAFE_LIMIT)
        .reset_index(drop=True)
    )

    # Add the best veto-safe local-negative near-null atoms, because E130 showed
    # these are the only safe atoms with the same sign as local improvement.
    safe_local = (
        safe_pool[safe_pool["all_minus_base"].lt(0.0)]
        .sort_values(["all_minus_base", "mean_abs_logit_move_vs_e95"], ascending=[True, False])
        .drop_duplicates(["source", "mask_name", "alpha"])
        .head(4)
    )
    if len(safe_local):
        safe = pd.concat([safe, safe_local], ignore_index=True).drop_duplicates("pred_index").reset_index(drop=True)

    return local, safe


def build_combo_candidates(
    base_rows: pd.DataFrame,
    base_preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame, pd.DataFrame]:
    e130_scan = pd.read_csv(e130.SCAN_OUT)
    local_atoms, safe_atoms = select_atoms(e130_scan)
    if local_atoms.empty or safe_atoms.empty:
        return pd.DataFrame(), base_preds, local_atoms, safe_atoms

    preds = list(base_preds)
    seen_pred = {pred_key(pred): idx for idx, pred in enumerate(preds)}
    e95_index = seen_pred[pred_key(refs["e95"])]
    e95_logit = logit(refs["e95"])
    risk_sign = risk_signs(tail_state)
    risk_weight = (
        1.00 * density["plausible"]
        + 0.75 * density["e101_active"]
        + 0.50 * density["q2s3"]
        + 0.25 * density["tail_equal"]
    )

    rows: list[dict[str, Any]] = []
    loc_scales = [0.35, 0.50, 0.75, 1.00]
    safe_scales = [0.25, 0.50, 0.75, 1.00, 1.50]

    for lrec in local_atoms.to_dict("records"):
        lidx = int(lrec["pred_index"])
        dloc = logit(preds[lidx]) - e95_logit
        loc_risk = risk_scalar(dloc, risk_sign, risk_weight)
        for srec in safe_atoms.to_dict("records"):
            sidx = int(srec["pred_index"])
            dsafe = logit(preds[sidx]) - e95_logit
            safe_risk = risk_scalar(dsafe, risk_sign, risk_weight)
            corr = float(np.sum(dloc * dsafe) / (np.sum(dsafe * dsafe) + 1.0e-15))
            for lscale in loc_scales:
                for sscale in safe_scales:
                    delta = float(lscale) * dloc + float(sscale) * dsafe
                    pred = clip_prob(sigmoid(e95_logit + delta))
                    combo_risk = risk_scalar(delta, risk_sign, risk_weight)
                    add_pred(
                        rows,
                        preds,
                        seen_pred,
                        pred,
                        {
                            "strategy": "atom_combo",
                            "local_pred_index": lidx,
                            "safe_pred_index": sidx,
                            "source": f"{lrec['source']}+{srec['source']}",
                            "local_source": str(lrec["source"]),
                            "safe_source": str(srec["source"]),
                            "local_mask": str(lrec["mask_name"]),
                            "safe_mask": str(srec["mask_name"]),
                            "local_alpha": float(lrec["alpha"]),
                            "safe_alpha": float(srec["alpha"]),
                            "local_scale": float(lscale),
                            "safe_scale": float(sscale),
                            "safe_projection_on_local": corr,
                            "local_risk_scalar": loc_risk,
                            "safe_risk_scalar": safe_risk,
                            "combo_risk_scalar": combo_risk,
                            "clip_quantile": np.nan,
                        },
                        base_index=e95_index,
                    )

        # Independent falsifier: if local risk is concentrated in a few cells,
        # clipping those cells should create the missing overlap. If it does not,
        # the local-upside direction itself is incompatible with the public veto.
        adverse = np.maximum(dloc * risk_sign, 0.0) * risk_weight
        active = np.abs(dloc) > 1.0e-12
        for q in [0.50, 0.70, 0.85, 0.95]:
            if not active.any():
                continue
            cut = float(np.quantile(adverse[active], q))
            keep = ~(adverse >= cut)
            clipped = dloc * keep
            for lscale in [0.50, 0.75, 1.00, 1.25]:
                delta = float(lscale) * clipped
                if float(np.abs(delta).mean()) <= 1.0e-14:
                    continue
                pred = clip_prob(sigmoid(e95_logit + delta))
                add_pred(
                    rows,
                    preds,
                    seen_pred,
                    pred,
                    {
                        "strategy": "risk_clipped_local",
                        "local_pred_index": lidx,
                        "safe_pred_index": -1,
                        "source": str(lrec["source"]),
                        "local_source": str(lrec["source"]),
                        "safe_source": "",
                        "local_mask": str(lrec["mask_name"]),
                        "safe_mask": "",
                        "local_alpha": float(lrec["alpha"]),
                        "safe_alpha": np.nan,
                        "local_scale": float(lscale),
                        "safe_scale": np.nan,
                        "safe_projection_on_local": np.nan,
                        "local_risk_scalar": loc_risk,
                        "safe_risk_scalar": np.nan,
                        "combo_risk_scalar": risk_scalar(delta, risk_sign, risk_weight),
                        "clip_quantile": float(q),
                    },
                    base_index=e95_index,
                )

    return pd.DataFrame(rows), preds, local_atoms, safe_atoms


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].isin(["atom_combo", "risk_clipped_local"])].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["strategy", "local_source", "safe_source"]
    for keys, group in variants.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
        veto = group[group["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        submit = local_and_veto[
            local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
            & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
            & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
            & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
        ]
        best_local = evaluated.sort_values("all_minus_base").head(1)
        best_sensor = evaluated.sort_values("post101_mean_vs_e95_e101_sensor").head(1)
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "veto_actionable": int(len(veto)),
                "local_and_veto": int(len(local_and_veto)),
                "submit_gate": int(len(submit)),
                "best_all_minus_e95": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_sensor_mean_vs_e95": float(best_sensor["post101_mean_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
                "best_sensor_p95_vs_e95": float(best_sensor["post101_p95_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
                "best_tail_exposure": float(best_local["e72_adverse_positive_exposure_all"].iloc[0])
                if len(best_local)
                else np.nan,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["submit_gate", "local_and_veto", "strict", "best_sensor_mean_vs_e95", "best_all_minus_e95"],
        ascending=[False, False, False, True, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[
        scan["strategy"].isin(["atom_combo", "risk_clipped_local"])
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & scan["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        [
            "post101_mean_vs_e95_e101_sensor",
            "post101_p95_vs_e95_e101_sensor",
            "all_minus_base",
            "mean_abs_logit_move_vs_e95",
        ],
        ascending=[True, True, True, False],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(out, index=False)
    return out


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    local_atoms: pd.DataFrame,
    safe_atoms: pd.DataFrame,
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].isin(["atom_combo", "risk_clipped_local"])].copy()
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()

    atom_cols = [
        "pred_index",
        "source",
        "mask_name",
        "alpha",
        "all_minus_base",
        "strict_gate",
        "gate_strict_actionable",
        "mean_abs_logit_move_vs_e95",
        "e72_adverse_positive_exposure_all",
        "tail_equal_law_cosine",
        "post101_mean_vs_e95_e101_sensor",
    ]
    row_cols = [
        "strategy",
        "source",
        "local_mask",
        "safe_mask",
        "local_scale",
        "safe_scale",
        "clip_quantile",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "e72_adverse_positive_exposure_all",
        "mean_abs_logit_move_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
        "tag",
    ]
    decision = (
        f"Materialized `{submission_path.name}`."
        if submission_path is not None
        else "No submission. Local-upside atoms and veto-safe atoms still do not overlap after linear combination or hard-tail risk clipping."
    )

    lines = [
        "# E131 Tail-Density Atom-Combo Probe",
        "",
        "## Question",
        "",
        "E130 found local-upside density atoms and public-veto-safe atoms in separate regions. Is this just a linear-combination problem, or is the E95 successor direction itself missing?",
        "",
        "## Method",
        "",
        "- Select the strongest E130 E95-relative local-strict atoms.",
        "- Select E130 atoms that pass separated transfer-shrinkage vetoes, prioritizing material veto-actionable rows and near-null safe local-negative rows.",
        "- Build logit-space local+safe combinations from E95.",
        "- Independently clip the worst hard-tail-risk cells from each local atom.",
        "- Score only against E95-relative local stress, separated E128/E129 vetoes, and E124 post-E101 transfer filters.",
        "",
        "## Counts",
        "",
        f"- local atoms: `{len(local_atoms)}`",
        f"- safe atoms: `{len(safe_atoms)}`",
        f"- candidate rows: `{len(scan)}`",
        f"- evaluated candidates: `{len(evaluated)}`",
        f"- local strict candidates: `{len(strict)}`",
        f"- veto-actionable candidates: `{len(veto)}`",
        f"- local-strict plus veto-actionable candidates: `{len(local_and_veto)}`",
        f"- final submit-gate candidates: `{len(submit)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Local Atoms",
        "",
        md_table(local_atoms[[c for c in atom_cols if c in local_atoms.columns]], ".9f"),
        "",
        "## Safe Atoms",
        "",
        md_table(safe_atoms[[c for c in atom_cols if c in safe_atoms.columns]], ".9f"),
        "",
        "## Summary",
        "",
        md_table(summary.head(50), ".9f"),
        "",
        "## Best Local Evaluated Candidates",
        "",
        md_table(evaluated.sort_values(["all_minus_base", "all_delta_vs_mixmin"])[row_cols].head(30), ".9f")
        if len(evaluated)
        else "None.",
        "",
        "## Local Strict Plus Veto-Actionable Candidates",
        "",
        md_table(local_and_veto.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(local_and_veto)
        else "None.",
        "",
        "## Submit-Gate Candidates",
        "",
        md_table(submit.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(submit)
        else "None.",
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    base_rows, base_preds, _masks, density = e130.build_candidates(sample, refs)
    rows, preds, local_atoms, safe_atoms = build_combo_candidates(base_rows, base_preds, refs, density, tail_state)
    if rows.empty:
        raise RuntimeError("No E131 rows generated")

    labels, worlds, views, state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    summary = summarize(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, local_atoms, safe_atoms, transfer, submission_path)

    variants = scan[scan["strategy"].isin(["atom_combo", "risk_clipped_local"])]
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)]
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)]
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)]
    submit = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
    ]
    print(
        {
            "rows": int(len(scan)),
            "local_atoms": int(len(local_atoms)),
            "safe_atoms": int(len(safe_atoms)),
            "evaluated": int(len(evaluated)),
            "strict": int(len(strict)),
            "veto_actionable": int(len(veto)),
            "local_and_veto": int(len(local_and_veto)),
            "submit_gate": int(len(submit)),
            "best_all_minus_e95": float(evaluated["all_minus_base"].min()) if len(evaluated) else None,
            "best_sensor_mean_vs_e95": float(
                evaluated["post101_mean_vs_e95_e101_sensor"].min()
            )
            if len(evaluated)
            else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(20).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
