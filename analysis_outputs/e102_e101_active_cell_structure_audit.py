#!/usr/bin/env python3
"""E102 E101 active-cell structure audit.

E101 materialized a small E95-relative Q2/S3 rollback. This audit asks whether
those 50 moved cells are merely a target-amplitude correction or whether they
cluster around subject/calendar/hidden-block structure. No submission is
created; the output is a falsification report for the next branch after E101.
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

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS, KEYS, load_sub, logit  # noqa: E402


E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E89_FILE = "submission_e89_e72decontam_00d7807f.csv"

CELL_OUT = OUT / "e102_e101_active_cell_structure_audit_cells.csv"
BLOCK_OUT = OUT / "e102_e101_active_cell_structure_audit_blocks.csv"
ENRICH_OUT = OUT / "e102_e101_active_cell_structure_audit_enrichment.csv"
PERM_OUT = OUT / "e102_e101_active_cell_structure_audit_permutation.csv"
SUMMARY_OUT = OUT / "e102_e101_active_cell_structure_audit_summary.csv"
REPORT_OUT = OUT / "e102_e101_active_cell_structure_audit_report.md"

Q2S3 = ["Q2", "S3"]
EPS = 1.0e-12


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
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


def len_bin(n: int) -> str:
    if n <= 2:
        return "1-2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    return "11-16"


def pos_bin(pos_in_block: int, n_rows: int) -> str:
    if n_rows <= 1:
        return "single"
    if pos_in_block == 0:
        return "left_edge"
    if pos_in_block == n_rows - 1:
        return "right_edge"
    if min(pos_in_block, n_rows - 1 - pos_in_block) <= 1:
        return "near_edge"
    return "interior"


def context_type(rows: pd.DataFrame, positions: np.ndarray, known_mask: np.ndarray) -> dict[str, Any]:
    sid = str(rows.iloc[int(positions[0])]["subject_id"])
    subject_mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
    known_subject = np.where(subject_mask & known_mask)[0]
    before = known_subject[known_subject < positions.min()]
    after = known_subject[known_subject > positions.max()]
    has_prev = len(before) > 0
    has_next = len(after) > 0
    if has_prev and has_next:
        ctype = "between_train_runs"
    elif has_prev:
        ctype = "after_train_run"
    elif has_next:
        ctype = "before_train_run"
    else:
        ctype = "isolated"
    start = pd.Timestamp(rows.iloc[int(positions.min())]["lifelog_date"])
    end = pd.Timestamp(rows.iloc[int(positions.max())]["lifelog_date"])
    prev_date = pd.Timestamp(rows.iloc[int(before[-1])]["lifelog_date"]) if has_prev else pd.NaT
    next_date = pd.Timestamp(rows.iloc[int(after[0])]["lifelog_date"]) if has_next else pd.NaT
    return {
        "context_type": ctype,
        "has_prev_train": has_prev,
        "has_next_train": has_next,
        "prev_gap_pos": float(positions.min() - before[-1]) if has_prev else np.nan,
        "next_gap_pos": float(after[0] - positions.max()) if has_next else np.nan,
        "prev_gap_days": float((start - prev_date).days) if has_prev else np.nan,
        "next_gap_days": float((next_date - end).days) if has_next else np.nan,
    }


def build_hidden_row_meta(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    rows = hbr.all_rows(train, sample)
    known_mask = hbr.base_known_mask(rows)
    blocks = hbr.make_hidden_blocks(rows)
    records: list[dict[str, Any]] = []
    for block in blocks:
        ctx = context_type(rows, block.positions, known_mask)
        block_rows = rows.iloc[block.positions].reset_index(drop=True)
        n = int(len(block_rows))
        for k, rec in block_rows.iterrows():
            sub_idx = int(rec["sub_idx"])
            records.append(
                {
                    "sub_idx": sub_idx,
                    "hidden_block_id": block.block_id,
                    "subject_id": str(block.subject_id),
                    "lifelog_date": pd.Timestamp(rec["lifelog_date"]),
                    "sleep_date": pd.Timestamp(rec["sleep_date"]),
                    "global_pos": int(rec["global_pos"]),
                    "subject_pos": int(rec["subject_pos"]),
                    "subject_phase": float(rec["subject_phase"]),
                    "dow": int(pd.Timestamp(rec["lifelog_date"]).dayofweek),
                    "is_weekend": int(pd.Timestamp(rec["lifelog_date"]).dayofweek >= 5),
                    "block_n_rows": n,
                    "block_len_bin": len_bin(n),
                    "pos_in_block": int(k),
                    "pos_frac": float(k / max(n - 1, 1)),
                    "edge_distance": int(min(k, n - 1 - k)),
                    "pos_bin": pos_bin(int(k), n),
                    "block_start": pd.Timestamp(block.start),
                    "block_end": pd.Timestamp(block.end),
                    **ctx,
                }
            )
    out = pd.DataFrame(records).sort_values("sub_idx").reset_index(drop=True)
    if len(out) != len(sample):
        raise RuntimeError(f"hidden row metadata has {len(out)} rows, expected {len(sample)}")
    return out


def load_matrix(name: str, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(name, sample)[TARGETS].to_numpy(dtype=np.float64)


def build_cell_atlas(sample: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    e101 = load_matrix(E101_FILE, sample)
    e95 = load_matrix(E95_FILE, sample)
    mixmin = load_matrix(MIXMIN_FILE, sample)
    e72 = load_matrix(E72_FILE, sample)
    e89 = load_matrix(E89_FILE, sample)

    le101 = logit(e101)
    le95 = logit(e95)
    lmix = logit(mixmin)
    le72 = logit(e72)
    le89 = logit(e89)

    recs: list[dict[str, Any]] = []
    for row_i in range(len(sample)):
        for target in Q2S3:
            j = TARGETS.index(target)
            d = float(le101[row_i, j] - le95[row_i, j])
            rollback_axis = float(lmix[row_i, j] - le95[row_i, j])
            shrink_fraction = d / rollback_axis if abs(rollback_axis) > EPS else np.nan
            e95_mix_gap = float(le95[row_i, j] - lmix[row_i, j])
            rec = {
                "sub_idx": row_i,
                "target": target,
                "active": bool(abs(d) > 1.0e-9),
                "prob_e101": float(e101[row_i, j]),
                "prob_e95": float(e95[row_i, j]),
                "prob_mixmin": float(mixmin[row_i, j]),
                "prob_e72": float(e72[row_i, j]),
                "prob_e89": float(e89[row_i, j]),
                "delta_prob_e101_minus_e95": float(e101[row_i, j] - e95[row_i, j]),
                "delta_logit_e101_minus_e95": d,
                "abs_delta_logit_e101_minus_e95": abs(d),
                "logit_gap_e95_minus_mixmin": e95_mix_gap,
                "abs_logit_gap_e95_minus_mixmin": abs(e95_mix_gap),
                "rollback_shrink_fraction_to_mixmin": shrink_fraction,
                "delta_logit_e89_minus_e95": float(le89[row_i, j] - le95[row_i, j]),
                "delta_logit_e72_minus_mixmin": float(le72[row_i, j] - lmix[row_i, j]),
                "active_e95_vs_mixmin": bool(abs(e95_mix_gap) > 1.0e-9),
            }
            recs.append(rec)
    cells = pd.DataFrame(recs).merge(meta, on="sub_idx", how="left", validate="many_to_one")
    if cells["hidden_block_id"].isna().any():
        raise RuntimeError("missing hidden block metadata")
    return cells


def block_summary(cells: pd.DataFrame) -> pd.DataFrame:
    active = cells[cells["active"]].copy()
    base_rows = cells.drop_duplicates("sub_idx")
    block_base = (
        base_rows.groupby("hidden_block_id", sort=False)
        .agg(
            subject_id=("subject_id", "first"),
            context_type=("context_type", "first"),
            block_n_rows=("block_n_rows", "first"),
            block_len_bin=("block_len_bin", "first"),
            has_prev_train=("has_prev_train", "first"),
            has_next_train=("has_next_train", "first"),
            prev_gap_days=("prev_gap_days", "first"),
            next_gap_days=("next_gap_days", "first"),
            rows=("sub_idx", "nunique"),
        )
        .reset_index()
    )
    by_block = (
        active.groupby("hidden_block_id", sort=False)
        .agg(
            active_cells=("active", "size"),
            active_rows=("sub_idx", "nunique"),
            active_q2=("target", lambda s: int((s == "Q2").sum())),
            active_s3=("target", lambda s: int((s == "S3").sum())),
            mean_abs_logit_move=("abs_delta_logit_e101_minus_e95", "mean"),
            mean_rollback_fraction=("rollback_shrink_fraction_to_mixmin", "mean"),
        )
        .reset_index()
    )
    out = block_base.merge(by_block, on="hidden_block_id", how="left")
    for col in ["active_cells", "active_rows", "active_q2", "active_s3"]:
        out[col] = out[col].fillna(0).astype(int)
    out["active_cell_rate_q2s3"] = out["active_cells"] / (2.0 * out["rows"])
    out["active_row_rate"] = out["active_rows"] / out["rows"]
    return out.sort_values(["active_cells", "active_rows", "block_n_rows"], ascending=[False, False, False])


def enrichment_for(df: pd.DataFrame, active_col: str, fields: list[str], unit_name: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    n = len(df)
    n_active = int(df[active_col].sum())
    for field in fields:
        for value, g in df.groupby(field, dropna=False, sort=False):
            total = len(g)
            obs = int(g[active_col].sum())
            p = total / max(n, 1)
            exp = n_active * p
            var = n_active * p * (1.0 - p)
            z = (obs - exp) / np.sqrt(var) if var > 0 else 0.0
            base_rate = total / max(n, 1)
            active_rate = obs / max(n_active, 1)
            lift = active_rate / base_rate if base_rate > 0 else np.nan
            rows.append(
                {
                    "unit": unit_name,
                    "field": field,
                    "value": str(value),
                    "active": obs,
                    "total_in_group": total,
                    "n_active": n_active,
                    "n_total": n,
                    "expected_active": exp,
                    "lift": lift,
                    "z": z,
                }
            )
    return pd.DataFrame(rows).sort_values(["z", "active"], ascending=[False, False])


def permutation_null(cells: pd.DataFrame, n_perm: int = 20000, seed: int = 260991) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    active = cells["active"].to_numpy(bool)
    obs = metrics_for_selection(cells, active)
    target_counts = cells.loc[active].groupby("target").size().to_dict()
    idx_by_target = {target: cells.index[cells["target"].eq(target)].to_numpy(dtype=int) for target in Q2S3}

    sims: dict[str, list[float]] = {k: [] for k in obs}
    for _ in range(n_perm):
        sel = np.zeros(len(cells), dtype=bool)
        for target, count in target_counts.items():
            pool = idx_by_target[target]
            chosen = rng.choice(pool, size=int(count), replace=False)
            sel[chosen] = True
        vals = metrics_for_selection(cells, sel)
        for key, value in vals.items():
            sims[key].append(float(value))

    rows: list[dict[str, Any]] = []
    for metric, obs_value in obs.items():
        arr = np.asarray(sims[metric], dtype=np.float64)
        if metric in {"n_blocks_touched", "n_subjects_touched", "n_rows_touched", "mean_edge_distance"}:
            p_one_sided = float((np.sum(arr <= obs_value) + 1.0) / (len(arr) + 1.0))
            direction = "low_is_concentrated"
        else:
            p_one_sided = float((np.sum(arr >= obs_value) + 1.0) / (len(arr) + 1.0))
            direction = "high_is_concentrated"
        rows.append(
            {
                "metric": metric,
                "observed": float(obs_value),
                "null_mean": float(arr.mean()),
                "null_p05": float(np.quantile(arr, 0.05)),
                "null_p50": float(np.quantile(arr, 0.50)),
                "null_p95": float(np.quantile(arr, 0.95)),
                "p_one_sided": p_one_sided,
                "direction": direction,
                "n_perm": n_perm,
            }
        )
    return pd.DataFrame(rows).sort_values("p_one_sided")


def metrics_for_selection(cells: pd.DataFrame, selected: np.ndarray) -> dict[str, float]:
    sub = cells.loc[selected].copy()
    by_block = sub.groupby("hidden_block_id").size()
    by_subject = sub.groupby("subject_id").size()
    by_row = sub.groupby("sub_idx").size()
    row_targets = sub.groupby("sub_idx")["target"].nunique()
    return {
        "n_blocks_touched": float(sub["hidden_block_id"].nunique()),
        "n_subjects_touched": float(sub["subject_id"].nunique()),
        "n_rows_touched": float(sub["sub_idx"].nunique()),
        "max_cells_per_block": float(by_block.max() if len(by_block) else 0),
        "max_cells_per_subject": float(by_subject.max() if len(by_subject) else 0),
        "max_cells_per_row": float(by_row.max() if len(by_row) else 0),
        "rows_with_both_targets": float((row_targets == 2).sum()),
        "edge_or_near_edge_rate": float(sub["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"]).mean()),
        "mean_edge_distance": float(sub["edge_distance"].mean()),
        "weekend_rate": float(sub["is_weekend"].mean()),
        "between_train_runs_rate": float(sub["context_type"].eq("between_train_runs").mean()),
    }


def build_summary(cells: pd.DataFrame, blocks: pd.DataFrame, perm: pd.DataFrame) -> pd.DataFrame:
    active = cells[cells["active"]].copy()
    row_active = cells.groupby("sub_idx")["active"].any()
    e95_mix_active = cells["active_e95_vs_mixmin"].sum()
    return pd.DataFrame(
        [
            {"metric": "eligible_q2s3_cells", "value": float(len(cells))},
            {"metric": "e101_active_cells", "value": float(len(active))},
            {"metric": "e101_active_rows", "value": float(row_active.sum())},
            {"metric": "e101_active_blocks", "value": float(active["hidden_block_id"].nunique())},
            {"metric": "e101_active_subjects", "value": float(active["subject_id"].nunique())},
            {"metric": "q2_active_cells", "value": float((active["target"] == "Q2").sum())},
            {"metric": "s3_active_cells", "value": float((active["target"] == "S3").sum())},
            {"metric": "e95_mixmin_active_q2s3_cells", "value": float(e95_mix_active)},
            {"metric": "max_active_cells_per_block", "value": float(blocks["active_cells"].max())},
            {
                "metric": "blocks_with_ge3_active_cells",
                "value": float((blocks["active_cells"] >= 3).sum()),
            },
            {
                "metric": "min_perm_p",
                "value": float(perm["p_one_sided"].min()) if not perm.empty else np.nan,
            },
        ]
    )


def write_report(cells: pd.DataFrame, blocks: pd.DataFrame, enrichment: pd.DataFrame, perm: pd.DataFrame, summary: pd.DataFrame) -> None:
    active = cells[cells["active"]].copy()
    top_blocks = blocks[blocks["active_cells"] > 0].head(12)[
        [
            "hidden_block_id",
            "subject_id",
            "context_type",
            "block_n_rows",
            "active_cells",
            "active_rows",
            "active_q2",
            "active_s3",
            "active_cell_rate_q2s3",
        ]
    ]
    top_enrich = enrichment[(enrichment["active"] >= 2) & (enrichment["z"] > 0)].head(15)
    active_by_target = active.groupby("target").agg(cells=("target", "size"), rows=("sub_idx", "nunique")).reset_index()
    shrink = active["rollback_shrink_fraction_to_mixmin"].dropna()
    shrink_text = (
        f"mean={shrink.mean():.6f}, min={shrink.min():.6f}, max={shrink.max():.6f}"
        if len(shrink)
        else "none"
    )

    strongest_perm = perm.head(8)
    n_blocks = int(summary.loc[summary["metric"].eq("e101_active_blocks"), "value"].iloc[0])
    n_subjects = int(summary.loc[summary["metric"].eq("e101_active_subjects"), "value"].iloc[0])
    n_rows = int(summary.loc[summary["metric"].eq("e101_active_rows"), "value"].iloc[0])
    max_block = int(summary.loc[summary["metric"].eq("max_active_cells_per_block"), "value"].iloc[0])
    min_p = float(summary.loc[summary["metric"].eq("min_perm_p"), "value"].iloc[0])

    if min_p < 0.01:
        interpretation = (
            "E101 active cells are not random Q2/S3 amplitude cells under the target-count null. "
            "The next branch should test block/subject-local rollback masks before a generic target shrink."
        )
    elif min_p < 0.10:
        interpretation = (
            "E101 has weak-to-moderate structure concentration. Treat it as an amplitude sensor, but keep "
            "block-local rollback as the next falsification if public improves."
        )
    else:
        interpretation = (
            "E101 does not show strong block/subject concentration beyond target counts. Its cleanest current "
            "meaning is target-axis amplitude rollback rather than a hidden-block selector."
        )

    report = f"""# E102 E101 Active-Cell Structure Audit

## Question

E101 changes only Q2/S3 cells relative to E95. This audit asks whether those
cells are a hidden block/subject/calendar subset or just the cells where E95
differs from mixmin on Q2/S3.

## Core Counts

{md_table(summary, '.6f')}

## Active By Target

{md_table(active_by_target, '.6f')}

Rollback shrink fraction to mixmin among active cells: `{shrink_text}`.

## Top Active Blocks

{md_table(top_blocks, '.6f')}

## Strongest Enrichments

{md_table(top_enrich[['unit','field','value','active','total_in_group','expected_active','lift','z']], '.6f')}

## Target-Count Permutation Null

{md_table(strongest_perm, '.6f')}

## Interpretation

- Active cells touch `{n_blocks}` hidden submission blocks, `{n_subjects}` subjects, and `{n_rows}` rows.
- The largest hidden block contains `{max_block}` active Q2/S3 cells.
- Strongest permutation p-value is `{min_p:.6f}`.
- {interpretation}

## Decision

If E101 improves public, use this audit to decide the follow-up:

- strong concentration: test a block/subject-local E95 rollback mask;
- weak concentration: test a target-axis amplitude line around E101;
- no concentration: do not search handcrafted row masks; move back to block-state JEPA representation.

If E101 worsens public, this audit helps decide whether the failure kills only
generic Q2/S3 amplitude rollback or also the hidden-block-local rollback idea.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    train, sample = hbr.read_data()
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    meta = build_hidden_row_meta(train, sample)
    cells = build_cell_atlas(sample, meta)
    blocks = block_summary(cells)

    row_units = cells.drop_duplicates("sub_idx").copy()
    row_units["active_row"] = row_units["sub_idx"].map(cells.groupby("sub_idx")["active"].any()).astype(bool)
    cell_fields = [
        "target",
        "subject_id",
        "hidden_block_id",
        "context_type",
        "block_len_bin",
        "pos_bin",
        "is_weekend",
    ]
    row_fields = ["subject_id", "hidden_block_id", "context_type", "block_len_bin", "pos_bin", "is_weekend"]
    enrichment = pd.concat(
        [
            enrichment_for(cells, "active", cell_fields, "cell"),
            enrichment_for(row_units, "active_row", row_fields, "row"),
        ],
        ignore_index=True,
    ).sort_values(["z", "active"], ascending=[False, False])
    perm = permutation_null(cells)
    summary = build_summary(cells, blocks, perm)

    cells.to_csv(CELL_OUT, index=False)
    blocks.to_csv(BLOCK_OUT, index=False)
    enrichment.to_csv(ENRICH_OUT, index=False)
    perm.to_csv(PERM_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(cells, blocks, enrichment, perm, summary)

    print(f"wrote {CELL_OUT}")
    print(f"wrote {BLOCK_OUT}")
    print(f"wrote {ENRICH_OUT}")
    print(f"wrote {PERM_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
