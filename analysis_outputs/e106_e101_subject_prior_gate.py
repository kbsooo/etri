#!/usr/bin/env python3
"""E106 E101 subject-prior gate audit.

E105 showed that E101 is not favorable under global train priors, but it becomes
closer to live under subject priors, with most swing mass in S3. This script
tests the falsifiable follow-up:

Can the E105 subject-prior signal select a smaller E101-style rollback that is
healthier than full E101, or is subject prior useful only for interpreting the
pending public result?

No public labels are fitted. Candidates start from E95 and move selected E101
active cells toward mixmin.
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
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e104_e101_amplitude_pareto_cliff as e104  # noqa: E402


CELLS_IN = OUT / "e105_e101_public_label_breakeven_cells.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
SCAN_OUT = OUT / "e106_e101_subject_prior_gate_scan.csv"
SUMMARY_OUT = OUT / "e106_e101_subject_prior_gate_summary.csv"
PRIOR_OUT = OUT / "e106_e101_subject_prior_gate_prior.csv"
REPORT_OUT = OUT / "e106_e101_subject_prior_gate_report.md"
SUBMISSION_PREFIX = "submission_e106_subjgate"

EPS = 1.0e-6
N_SIMS = 80_000
RNG_SEED = 106
ALPHAS = [0.25, 0.50, 0.75, 1.00]
TOP_KS = [8, 12, 16, 20, 23, 25, 30, 35, 40, 45, 50]
SUPPORT_QS = [0.25, 0.40, 0.50, 0.60, 0.70, 0.80]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
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


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e106_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": tag, **rec})


def cells_to_mask(cells: pd.DataFrame, selector: pd.Series | np.ndarray, n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    selected = cells[np.asarray(selector, dtype=bool)].copy()
    for rec in selected.to_dict("records"):
        mask[int(rec["sub_idx"]), TARGETS.index(str(rec["target"]))] = True
    return mask


def selector_specs(cells: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    active = cells[cells["active"].astype(bool)].copy().reset_index(drop=True)
    specs: list[tuple[str, np.ndarray]] = []

    specs.append(("active_all", np.ones(len(active), dtype=bool)))
    specs.append(("active_s3_all", active["target"].eq("S3").to_numpy()))
    specs.append(("active_q2_all", active["target"].eq("Q2").to_numpy()))
    specs.append(("subject_expected_negative", active["subject_expected_delta"].lt(0.0).to_numpy()))
    specs.append(("global_expected_negative", active["global_expected_delta"].lt(0.0).to_numpy()))
    specs.append(("subject_beats_global_support", active["subject_support_probability"].gt(active["global_support_probability"]).to_numpy()))
    specs.append(("edge_or_near", active["edge_distance"].astype(float).le(1.0).to_numpy()))
    specs.append(("s3_subject_expected_negative", (active["target"].eq("S3") & active["subject_expected_delta"].lt(0.0)).to_numpy()))
    specs.append(("s3_high_subject_support_0p80", (active["target"].eq("S3") & active["subject_support_probability"].ge(0.80)).to_numpy()))
    specs.append(("s3_high_subject_support_0p90", (active["target"].eq("S3") & active["subject_support_probability"].ge(0.90)).to_numpy()))

    for q in SUPPORT_QS:
        cut = float(active["subject_support_probability"].quantile(q))
        specs.append((f"subject_support_q{q:.2f}", active["subject_support_probability"].ge(cut).to_numpy()))
        s3 = active["target"].eq("S3")
        if s3.any():
            s3_cut = float(active.loc[s3, "subject_support_probability"].quantile(q))
            specs.append((f"s3_subject_support_q{q:.2f}", (s3 & active["subject_support_probability"].ge(s3_cut)).to_numpy()))

    rank_fields = {
        "subject_expected_best": active["subject_expected_delta"].to_numpy(dtype=np.float64),
        "global_expected_best": active["global_expected_delta"].to_numpy(dtype=np.float64),
        "support_prob_best": -active["subject_support_probability"].to_numpy(dtype=np.float64),
        "flip_x_support_best": -(
            active["flip_benefit"].to_numpy(dtype=np.float64)
            * active["subject_support_probability"].to_numpy(dtype=np.float64)
        ),
        "flip_benefit_best": -active["flip_benefit"].to_numpy(dtype=np.float64),
    }
    for name, values in rank_fields.items():
        order = np.argsort(values)
        for k in TOP_KS:
            if k > len(active):
                continue
            selected = np.zeros(len(active), dtype=bool)
            selected[order[:k]] = True
            specs.append((f"{name}_top{k}", selected))

    unique: list[tuple[str, np.ndarray]] = []
    seen: set[bytes] = set()
    for name, mask in specs:
        mask = np.asarray(mask, dtype=bool)
        if mask.sum() == 0:
            continue
        key = mask.tobytes()
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, mask))
    return unique


def build_refs(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    refs = e101.build_refs(sample)
    refs["e101"] = load_pred(E101_FILE, sample)
    return refs


def build_candidates(
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], pd.DataFrame]:
    refs = build_refs(sample)
    tail_state = e101.e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    cells = pd.read_csv(CELLS_IN)
    active = cells[cells["active"].astype(bool)].copy().reset_index(drop=True)

    e95_logit = logit(refs["e95"])
    mixmin_logit = logit(refs["mixmin"])
    rollback = mixmin_logit - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for name in ["mixmin", "e95", "e101", "e89", "e85", "e86", "e90"]:
        add_pred(rows, preds, seen, refs[name], {"strategy": "control", "source": name})

    for selector_name, selector_mask in selector_specs(active):
        full_mask = cells_to_mask(active, selector_mask, len(sample))
        selected = active[selector_mask].copy()
        move_cells = int((full_mask & (np.abs(rollback) > 1.0e-12)).sum())
        if move_cells == 0:
            continue
        target_scope = "+".join(TARGETS[j] for j in np.where(full_mask.any(axis=0))[0])
        for alpha in ALPHAS:
            pred = clip_prob(sigmoid(e95_logit + float(alpha) * rollback * full_mask))
            add_pred(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "subject_prior_gate",
                    "source": "e95",
                    "fallback": "mixmin",
                    "selector": selector_name,
                    "target_scope": target_scope,
                    "graft_alpha": float(alpha),
                    "selected_cells": int(full_mask.sum()),
                    "selected_rows": int(np.any(full_mask, axis=1).sum()),
                    "move_cells": move_cells,
                    "selected_s3_cells": int(selected["target"].eq("S3").sum()),
                    "selected_q2_cells": int(selected["target"].eq("Q2").sum()),
                    "subject_support_mean": float(selected["subject_support_probability"].mean()),
                    "global_support_mean": float(selected["global_support_probability"].mean()),
                    "subject_expected_delta_e101_basis": float(selected["subject_expected_delta"].sum() / (250 * len(TARGETS))),
                    "global_expected_delta_e101_basis": float(selected["global_expected_delta"].sum() / (250 * len(TARGETS))),
                    "flip_benefit_share": float(selected["flip_benefit"].sum() / active["flip_benefit"].sum()),
                },
            )
    return pd.DataFrame(rows), preds, refs, tail_state, active


def hard_label_prior_summary(
    scan: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    active: pd.DataFrame,
) -> pd.DataFrame:
    idxs = scan["pred_index"].drop_duplicates().astype(int).tolist()
    n_all = 250 * len(TARGETS)
    row_idx = active["sub_idx"].astype(int).to_numpy()
    target_idx = active["target"].map({t: i for i, t in enumerate(TARGETS)}).astype(int).to_numpy()

    p95 = refs["e95"][row_idx, target_idx]
    d0_by_pred: list[np.ndarray] = []
    d1_by_pred: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    for pred_idx in idxs:
        pred = preds[pred_idx][row_idx, target_idx]
        d1 = np.log(np.clip(p95, EPS, 1.0 - EPS) / np.clip(pred, EPS, 1.0 - EPS))
        d0 = np.log(np.clip(1.0 - p95, EPS, 1.0 - EPS) / np.clip(1.0 - pred, EPS, 1.0 - EPS))
        d0_by_pred.append(d0)
        d1_by_pred.append(d1)

        support_label = np.where(d1 < d0, 1, 0)
        support_delta = np.minimum(d0, d1)
        adverse_delta = np.maximum(d0, d1)
        global_pi = active["global_prior_y1"].to_numpy(dtype=np.float64)
        subject_pi = active["subject_prior_y1"].to_numpy(dtype=np.float64)
        global_expected = global_pi * d1 + (1.0 - global_pi) * d0
        subject_expected = subject_pi * d1 + (1.0 - subject_pi) * d0

        rows.append(
            {
                "pred_index": pred_idx,
                "active_delta_cells": int(np.sum(np.abs(pred - p95) > 1.0e-12)),
                "support_label_1_cells": int(support_label.sum()),
                "support_label_0_cells": int((support_label == 0).sum()),
                "all_support_delta_vs_e95": float(support_delta.sum() / n_all),
                "all_adverse_delta_vs_e95": float(adverse_delta.sum() / n_all),
                "global_prior_expected_delta_vs_e95": float(global_expected.sum() / n_all),
                "subject_prior_expected_delta_vs_e95": float(subject_expected.sum() / n_all),
            }
        )

    rng = np.random.default_rng(RNG_SEED)
    prior_pi = {
        "global": active["global_prior_y1"].to_numpy(dtype=np.float64),
        "subject": active["subject_prior_y1"].to_numpy(dtype=np.float64),
    }
    d0_mat = np.vstack(d0_by_pred)
    diff_mat = np.vstack(d1_by_pred) - d0_mat
    for prior_name, pi in prior_pi.items():
        labels = (rng.random((N_SIMS, len(active))) < pi).astype(np.float64)
        deltas = (labels @ diff_mat.T + d0_mat.sum(axis=1)) / n_all
        for j, pred_idx in enumerate(idxs):
            rows[j][f"{prior_name}_prior_p_beats_e95"] = float(np.mean(deltas[:, j] < 0.0))
            rows[j][f"{prior_name}_prior_p_beats_e101_edge"] = float(np.mean(deltas[:, j] < -0.0000153107))
            rows[j][f"{prior_name}_prior_q05"] = float(np.quantile(deltas[:, j], 0.05))
            rows[j][f"{prior_name}_prior_q50"] = float(np.quantile(deltas[:, j], 0.50))
            rows[j][f"{prior_name}_prior_q95"] = float(np.quantile(deltas[:, j], 0.95))

    return pd.DataFrame(rows)


def mark_subject_graft_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    out["is_graft"] = out["strategy"].eq("subject_prior_gate")
    e95_control_tail = float(
        out.loc[
            out["strategy"].eq("control") & out["source"].eq("e95"),
            "e72_adverse_positive_exposure_all",
        ].min()
    )
    out["is_strict_like"] = (
        out["is_graft"].fillna(False).astype(bool)
        & out["nonanchor_evaluated"].fillna(False).astype(bool)
        & out["strict_gate"].fillna(False).astype(bool)
        & (out["all_delta_vs_mixmin"] < -2.0e-5)
        & (out["hidden_q2s3_mean_minus_base"] < 0.0)
        & (out["world_support_minus_base"] < 0.0)
        & (out["block_q2s3_beats_base_rate"] >= 0.50)
        & (out["e72_adverse_positive_exposure_all"] <= e95_control_tail + 5.0e-7)
    )
    return out


def attach_e106_flags(scan: pd.DataFrame, prior: pd.DataFrame) -> pd.DataFrame:
    out = scan.merge(prior, on="pred_index", how="left")
    out = e104.attach_flags(out)
    e101_ref = out[out["strategy"].eq("control") & out["source"].eq("e101")].iloc[0]
    variant = out["strategy"].eq("subject_prior_gate")
    out["subject_expected_gain_vs_e101"] = (
        out["subject_prior_expected_delta_vs_e95"] - float(e101_ref["subject_prior_expected_delta_vs_e95"])
    )
    out["global_expected_gain_vs_e101"] = (
        out["global_prior_expected_delta_vs_e95"] - float(e101_ref["global_prior_expected_delta_vs_e95"])
    )
    out["subject_beat_gain_vs_e101"] = (
        out["subject_prior_p_beats_e95"] - float(e101_ref["subject_prior_p_beats_e95"])
    )
    out["global_beat_gain_vs_e101"] = (
        out["global_prior_p_beats_e95"] - float(e101_ref["global_prior_p_beats_e95"])
    )
    out["prior_healthier_than_e101"] = (
        variant
        & (out["subject_expected_gain_vs_e101"] <= -1.0e-8)
        & (out["global_expected_gain_vs_e101"] <= 1.0e-8)
        & (out["subject_beat_gain_vs_e101"] >= -1.0e-12)
    )
    out["e106_replaces_e101"] = (
        variant
        & out["e101_pass"].fillna(False).astype(bool)
        & out["prior_healthier_than_e101"].fillna(False).astype(bool)
        & (out["mean_vs_e95_broad_plausible"] <= float(e101_ref["mean_vs_e95_broad_plausible"]) + 1.0e-8)
        & (out["p95_vs_e95_broad_plausible"] <= float(e101_ref["p95_vs_e95_broad_plausible"]) + 1.0e-10)
        & (out["beat_e95_rate_broad_plausible"] >= float(e101_ref["beat_e95_rate_broad_plausible"]) - 1.0e-12)
    )
    out["e106_interesting_but_not_replacement"] = (
        variant
        & out["e101_pass"].fillna(False).astype(bool)
        & out["prior_healthier_than_e101"].fillna(False).astype(bool)
        & ~out["e106_replaces_e101"].fillna(False).astype(bool)
    )
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("subject_prior_gate")].copy()
    rows: list[dict[str, Any]] = []
    for selector, g in variants.groupby("selector", sort=False):
        pass_rows = g[g["e101_pass"].fillna(False).astype(bool)]
        prior_rows = g[g["prior_healthier_than_e101"].fillna(False).astype(bool)]
        replace_rows = g[g["e106_replaces_e101"].fillna(False).astype(bool)]
        interesting_rows = g[g["e106_interesting_but_not_replacement"].fillna(False).astype(bool)]
        best_subject = g.sort_values("subject_prior_expected_delta_vs_e95").iloc[0]
        best_transfer = g.sort_values(["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]).iloc[0]
        rows.append(
            {
                "selector": selector,
                "rows": len(g),
                "e101_pass_rows": len(pass_rows),
                "prior_healthier_rows": len(prior_rows),
                "replacement_rows": len(replace_rows),
                "interesting_nonreplacement_rows": len(interesting_rows),
                "selected_cells_min": int(g["selected_cells"].min()),
                "selected_cells_max": int(g["selected_cells"].max()),
                "best_subject_alpha": float(best_subject["graft_alpha"]),
                "best_subject_expected_vs_e95": float(best_subject["subject_prior_expected_delta_vs_e95"]),
                "best_subject_p_beats_e95": float(best_subject["subject_prior_p_beats_e95"]),
                "best_subject_mean_vs_e95": float(best_subject["mean_vs_e95_broad_plausible"]),
                "best_subject_p95_vs_e95": float(best_subject["p95_vs_e95_broad_plausible"]),
                "best_subject_beat_rate": float(best_subject["beat_e95_rate_broad_plausible"]),
                "best_transfer_alpha": float(best_transfer["graft_alpha"]),
                "best_transfer_mean_vs_e95": float(best_transfer["mean_vs_e95_broad_plausible"]),
                "best_transfer_p95_vs_e95": float(best_transfer["p95_vs_e95_broad_plausible"]),
                "best_transfer_beat_rate": float(best_transfer["beat_e95_rate_broad_plausible"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["replacement_rows", "interesting_nonreplacement_rows", "best_subject_expected_vs_e95"],
        ascending=[False, False, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e106_replaces_e101"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        [
            "p95_vs_e95_broad_plausible",
            "mean_vs_e95_broad_plausible",
            "subject_prior_expected_delta_vs_e95",
            "active_cells_vs_e95",
        ],
        ascending=[True, True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, selected_path: Path | None) -> None:
    controls = scan[scan["strategy"].eq("control")].copy()
    variants = scan[scan["strategy"].eq("subject_prior_gate")].copy()
    healthier = variants[variants["prior_healthier_than_e101"].fillna(False).astype(bool)].copy()
    interesting = variants[variants["e106_interesting_but_not_replacement"].fillna(False).astype(bool)].copy()
    replacements = variants[variants["e106_replaces_e101"].fillna(False).astype(bool)].copy()
    best_subject = variants.sort_values("subject_prior_expected_delta_vs_e95").head(15)
    best_transfer = variants.sort_values(["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]).head(15)

    control_cols = [
        "source",
        "active_delta_cells",
        "all_delta_vs_mixmin",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "global_prior_expected_delta_vs_e95",
        "global_prior_p_beats_e95",
        "subject_prior_expected_delta_vs_e95",
        "subject_prior_p_beats_e95",
    ]
    row_cols = [
        "tag",
        "selector",
        "graft_alpha",
        "selected_cells",
        "selected_s3_cells",
        "subject_support_mean",
        "e101_pass",
        "prior_healthier_than_e101",
        "e106_replaces_e101",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "subject_prior_expected_delta_vs_e95",
        "subject_prior_p_beats_e95",
        "global_prior_expected_delta_vs_e95",
        "global_prior_p_beats_e95",
    ]

    interp = (
        "At least one subject-prior-gated rollback replaces E101 under the strict E106 gate."
        if len(replacements)
        else "No subject-prior-gated rollback replaces E101. Subject prior improves label-world interpretation, but it should not be used as a pre-feedback candidate generator."
    )

    report = f"""# E106 E101 Subject-Prior Gate

## Question

E105 says E101 is global-prior adverse but closer to live under subject priors.
This audit asks whether subject-prior support can select a smaller E101-style
rollback that is healthier than full E101 before public feedback.

## Result

- variant rows: `{len(variants)}`
- E101-pass variants: `{int(variants['e101_pass'].fillna(False).sum())}`
- prior-healthier variants: `{int(variants['prior_healthier_than_e101'].fillna(False).sum())}`
- interesting non-replacements: `{len(interesting)}`
- replacement rows: `{len(replacements)}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`

## Controls

{md_table(controls[control_cols].sort_values('all_delta_vs_mixmin'), '.9f')}

## Selector Summary

{md_table(summary.head(30), '.9f')}

## Best Subject-Prior Rows

{md_table(best_subject[row_cols], '.9f')}

## Best Broad-Transfer Rows

{md_table(best_transfer[row_cols], '.9f')}

## Prior-Healthier Rows

{md_table(healthier.sort_values(['e101_pass', 'subject_prior_expected_delta_vs_e95'], ascending=[False, True]).head(30)[row_cols], '.9f')}

## Replacement Rows

{md_table(replacements[row_cols], '.9f')}

## Interpretation

{interp}
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, tail_state, active = build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    scan = mark_subject_graft_flags(scan)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    prior = hard_label_prior_summary(scan, preds, refs, active)
    scan = attach_e106_flags(scan, prior)
    summary = summarize(scan)
    selected_path = materialize(scan, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    prior.to_csv(PRIOR_OUT, index=False)
    write_report(scan, summary, selected_path)

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {PRIOR_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
