#!/usr/bin/env python3
"""E118 E101 flank-label support audit.

SAUNA question:
E101 remains the next public sensor after E117, but why should those 50 Q2/S3
cells matter? E102 found weak hidden-block edge locality, E105 found only weak
subject-prior support, and E114 rejected raw-context support. The remaining
cheap visible context is train-label flanks around each hidden block.

This script asks whether those flanks pre-validate the hard labels that would
make E101 beat E95. If flank priors improve over subject priors, E101 becomes
more than a public sensor. If they do not, E101 stays an information-rich but
externally unresolved hidden-label test.
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
import e102_e101_active_cell_structure_audit as e102  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS, KEYS  # noqa: E402


E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
EDGE_PER_CELL = MIXMIN_PUBLIC - E95_PUBLIC
N_ALL_CELLS = 250 * 7

CELL_OUT = OUT / "e118_e101_flank_label_support_cells.csv"
SUMMARY_OUT = OUT / "e118_e101_flank_label_support_summary.csv"
NULL_OUT = OUT / "e118_e101_flank_label_support_null.csv"
STRUCTURE_OUT = OUT / "e118_e101_flank_label_support_structure.csv"
REPORT_OUT = OUT / "e118_e101_flank_label_support_report.md"

Q2S3 = ["Q2", "S3"]
EPS = 1.0e-9


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


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = np.clip(np.asarray(p_new, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    p_base = np.clip(np.asarray(p_base, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return delta_y1, delta_y0


def beta_smooth(prior: float, labels: list[float], weights: list[float], pseudo: float = 2.0) -> float:
    clean = [(float(y), float(w)) for y, w in zip(labels, weights) if np.isfinite(y) and np.isfinite(w) and w > 0]
    if not clean:
        return float(prior)
    denom = pseudo + sum(w for _, w in clean)
    numer = pseudo * float(prior) + sum(y * w for y, w in clean)
    return float(np.clip(numer / denom, 1.0e-4, 1.0 - 1.0e-4))


def hard_endpoint_prob(label: float, fallback: float) -> float:
    if not np.isfinite(label):
        return float(fallback)
    return 0.85 if int(label) == 1 else 0.15


def nearest_label(row: pd.Series) -> float:
    prev_ok = bool(row["has_prev_label"])
    next_ok = bool(row["has_next_label"])
    if prev_ok and next_ok:
        if float(row["prev_gap_days"]) <= float(row["next_gap_days"]):
            return float(row["prev_y"])
        return float(row["next_y"])
    if prev_ok:
        return float(row["prev_y"])
    if next_ok:
        return float(row["next_y"])
    return np.nan


def edge_label(row: pd.Series) -> float:
    prev_ok = bool(row["has_prev_label"])
    next_ok = bool(row["has_next_label"])
    if prev_ok and next_ok:
        left_dist = int(row["pos_in_block"])
        right_dist = int(row["block_n_rows"] - 1 - row["pos_in_block"])
        return float(row["prev_y"] if left_dist <= right_dist else row["next_y"])
    return nearest_label(row)


def add_flank_context(cells: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    rows = hbr.all_rows(train, pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]))
    rows = rows.sort_values(hbr.SORT_KEY).reset_index(drop=True)
    y = hbr.train_label_matrix(rows, train)

    global_prior = {target: float(train[target].mean()) for target in TARGETS}
    subject_prior = {
        (str(sid), target): float(g[target].mean())
        for sid, g in train.groupby("subject_id", sort=False)
        for target in TARGETS
    }
    subject_count = {str(sid): int(len(g)) for sid, g in train.groupby("subject_id", sort=False)}
    train_pos_by_subject = {
        str(sid): g.index[g["split"].eq("train")].to_numpy(dtype=int)
        for sid, g in rows.groupby("subject_id", sort=False)
    }

    records: list[dict[str, Any]] = []
    for rec in cells.to_dict("records"):
        sid = str(rec["subject_id"])
        target = str(rec["target"])
        j = TARGETS.index(target)
        gpos = int(rec["global_pos"])
        train_positions = train_pos_by_subject[sid]
        before = train_positions[train_positions < gpos]
        after = train_positions[train_positions > gpos]
        prev_idx = int(before[-1]) if len(before) else -1
        next_idx = int(after[0]) if len(after) else -1
        prev_y = float(y[prev_idx, j]) if prev_idx >= 0 else np.nan
        next_y = float(y[next_idx, j]) if next_idx >= 0 else np.nan
        row_date = pd.Timestamp(rec["lifelog_date"])
        prev_date = pd.Timestamp(rows.loc[prev_idx, "lifelog_date"]) if prev_idx >= 0 else pd.NaT
        next_date = pd.Timestamp(rows.loc[next_idx, "lifelog_date"]) if next_idx >= 0 else pd.NaT
        prev_gap_days = float((row_date - prev_date).days) if prev_idx >= 0 else np.nan
        next_gap_days = float((next_date - row_date).days) if next_idx >= 0 else np.nan
        subj_p = subject_prior[(sid, target)]
        rec.update(
            {
                "global_prior_y1": global_prior[target],
                "subject_prior_y1": subj_p,
                "subject_train_count": subject_count[sid],
                "prev_y": prev_y,
                "next_y": next_y,
                "has_prev_label": bool(prev_idx >= 0),
                "has_next_label": bool(next_idx >= 0),
                "prev_gap_days": prev_gap_days,
                "next_gap_days": next_gap_days,
                "prev_gap_pos": float(gpos - prev_idx) if prev_idx >= 0 else np.nan,
                "next_gap_pos": float(next_idx - gpos) if next_idx >= 0 else np.nan,
                "both_flanks": bool(prev_idx >= 0 and next_idx >= 0),
                "prev_only": bool(prev_idx >= 0 and next_idx < 0),
                "next_only": bool(prev_idx < 0 and next_idx >= 0),
                "flank_conflict": bool(prev_idx >= 0 and next_idx >= 0 and int(prev_y) != int(next_y)),
                "flank_agree": bool(prev_idx >= 0 and next_idx >= 0 and int(prev_y) == int(next_y)),
                "min_flank_gap_days": float(np.nanmin([prev_gap_days, next_gap_days])),
            }
        )
        records.append(rec)
    return pd.DataFrame(records)


def add_support_priors(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    p_cols: dict[str, list[float]] = {
        "global": [],
        "subject": [],
        "prev_beta": [],
        "next_beta": [],
        "nearest_beta": [],
        "both_equal_beta": [],
        "both_distance_beta": [],
        "edge_endpoint_beta": [],
        "nearest_hard085": [],
        "conflict_flat": [],
    }
    for _, row in out.iterrows():
        subj = float(row["subject_prior_y1"])
        glob = float(row["global_prior_y1"])
        prev_y = float(row["prev_y"]) if bool(row["has_prev_label"]) else np.nan
        next_y = float(row["next_y"]) if bool(row["has_next_label"]) else np.nan
        prev_w = 1.0 / max(float(row["prev_gap_days"]), 1.0) if bool(row["has_prev_label"]) else np.nan
        next_w = 1.0 / max(float(row["next_gap_days"]), 1.0) if bool(row["has_next_label"]) else np.nan
        near_y = nearest_label(row)
        edge_y = edge_label(row)

        p_cols["global"].append(glob)
        p_cols["subject"].append(subj)
        p_cols["prev_beta"].append(beta_smooth(subj, [prev_y], [prev_w], pseudo=2.0))
        p_cols["next_beta"].append(beta_smooth(subj, [next_y], [next_w], pseudo=2.0))
        p_cols["nearest_beta"].append(beta_smooth(subj, [near_y], [1.0], pseudo=2.0))
        p_cols["both_equal_beta"].append(beta_smooth(subj, [prev_y, next_y], [1.0, 1.0], pseudo=2.0))
        p_cols["both_distance_beta"].append(beta_smooth(subj, [prev_y, next_y], [prev_w, next_w], pseudo=2.0))
        p_cols["edge_endpoint_beta"].append(beta_smooth(subj, [edge_y], [1.0], pseudo=2.0))
        p_cols["nearest_hard085"].append(hard_endpoint_prob(near_y, subj))
        if bool(row["flank_conflict"]):
            p_cols["conflict_flat"].append(0.5)
        else:
            p_cols["conflict_flat"].append(beta_smooth(subj, [prev_y, next_y], [prev_w, next_w], pseudo=2.0))

    for name, vals in p_cols.items():
        out[f"p_y1_{name}"] = np.asarray(vals, dtype=np.float64)
        support = np.where(out["support_label"].to_numpy(dtype=int) == 1, out[f"p_y1_{name}"], 1.0 - out[f"p_y1_{name}"])
        out[f"support_probability_{name}"] = support
        out[f"expected_delta_{name}"] = (
            out[f"p_y1_{name}"] * out["delta_y1"]
            + (1.0 - out[f"p_y1_{name}"]) * out["delta_y0"]
        )
    return out


def summarize_prior(cells: pd.DataFrame, prior: str, n_sim: int = 200000, seed: int = 260991) -> dict[str, Any]:
    seed_offset = sum((i + 1) * ord(ch) for i, ch in enumerate(prior))
    rng = np.random.default_rng(seed + seed_offset)
    p = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    d1 = cells["delta_y1"].to_numpy(dtype=np.float64)
    d0 = cells["delta_y0"].to_numpy(dtype=np.float64)
    sim_y = rng.random((n_sim, len(cells))) < p.reshape(1, -1)
    sim_delta = np.where(sim_y, d1.reshape(1, -1), d0.reshape(1, -1)).sum(axis=1)
    threshold_edge = -EDGE_PER_CELL * N_ALL_CELLS
    q2 = cells["target"].eq("Q2").to_numpy()
    s3 = cells["target"].eq("S3").to_numpy()
    top10 = cells.sort_values("flip_benefit", ascending=False).head(10).index
    return {
        "prior": prior,
        "expected_delta_active_sum": float(cells[f"expected_delta_{prior}"].sum()),
        "expected_delta_per_all_cells": float(cells[f"expected_delta_{prior}"].sum() / N_ALL_CELLS),
        "beat_e95_probability": float(np.mean(sim_delta < 0.0)),
        "match_e95_mixmin_edge_probability": float(np.mean(sim_delta <= threshold_edge)),
        "p05_active_delta": float(np.quantile(sim_delta, 0.05)),
        "p50_active_delta": float(np.quantile(sim_delta, 0.50)),
        "p95_active_delta": float(np.quantile(sim_delta, 0.95)),
        "mean_support_probability": float(cells[f"support_probability_{prior}"].mean()),
        "q2_support_probability": float(cells.loc[q2, f"support_probability_{prior}"].mean()),
        "s3_support_probability": float(cells.loc[s3, f"support_probability_{prior}"].mean()),
        "top10_flip_support_probability": float(cells.loc[top10, f"support_probability_{prior}"].mean()),
    }


def structure_metrics(cells: pd.DataFrame, selected: np.ndarray) -> dict[str, float]:
    sub = cells.loc[selected].copy()
    both = sub["both_flanks"].astype(bool)
    conflict = sub["flank_conflict"].astype(bool)
    edge = sub["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"])
    return {
        "both_flanks_rate": float(both.mean()),
        "prev_only_rate": float(sub["prev_only"].astype(bool).mean()),
        "flank_conflict_rate": float(conflict.mean()),
        "conflict_given_both_rate": float(conflict.sum() / max(both.sum(), 1)),
        "edge_or_near_edge_rate": float(edge.mean()),
        "edge_and_conflict_rate": float((edge & conflict).mean()),
        "mean_min_flank_gap_days": float(sub["min_flank_gap_days"].mean()),
        "gap_le1_rate": float((sub["min_flank_gap_days"] <= 1).mean()),
    }


def permutation_structure_null(cells: pd.DataFrame, n_perm: int = 20000, seed: int = 260991) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    active = cells["active"].to_numpy(bool)
    target_counts = cells.loc[active].groupby("target").size().to_dict()
    pools = {target: cells.index[cells["target"].eq(target)].to_numpy(dtype=int) for target in Q2S3}
    obs = structure_metrics(cells, active)
    sims = {k: [] for k in obs}
    for _ in range(n_perm):
        sel = np.zeros(len(cells), dtype=bool)
        for target, count in target_counts.items():
            sel[rng.choice(pools[target], size=int(count), replace=False)] = True
        vals = structure_metrics(cells, sel)
        for k, v in vals.items():
            sims[k].append(v)
    rows: list[dict[str, Any]] = []
    low_metrics = {"mean_min_flank_gap_days"}
    for metric, observed in obs.items():
        arr = np.asarray(sims[metric], dtype=np.float64)
        if metric in low_metrics:
            p_one_sided = float((np.sum(arr <= observed) + 1.0) / (len(arr) + 1.0))
            direction = "low_is_concentrated"
        else:
            p_one_sided = float((np.sum(arr >= observed) + 1.0) / (len(arr) + 1.0))
            direction = "high_is_concentrated"
        rows.append(
            {
                "metric": metric,
                "observed": float(observed),
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


def write_report(cells: pd.DataFrame, summary: pd.DataFrame, nulls: pd.DataFrame, structure: pd.DataFrame) -> None:
    subject_row = summary[summary["prior"].eq("subject")].iloc[0]
    best_row = summary.sort_values("beat_e95_probability", ascending=False).iloc[0]
    flank_rows = summary[summary["prior"].isin(["nearest_beta", "both_distance_beta", "edge_endpoint_beta", "conflict_flat", "nearest_hard085"])]
    active = cells[cells["active"]].copy()
    by_target = (
        active.groupby("target")
        .agg(
            cells=("target", "size"),
            both_flanks_rate=("both_flanks", "mean"),
            conflict_rate=("flank_conflict", "mean"),
            edge_or_near_edge_rate=("pos_bin", lambda s: float(s.isin(["left_edge", "right_edge", "near_edge", "single"]).mean())),
            subject_support=("support_probability_subject", "mean"),
            best_flank_support=(f"support_probability_{best_row['prior']}", "mean"),
        )
        .reset_index()
    )
    strongest_null = nulls.head(8)
    useful = bool(best_row["beat_e95_probability"] > subject_row["beat_e95_probability"] + 0.05)
    certified = bool(best_row["expected_delta_per_all_cells"] < 0.0)
    if useful and certified:
        interpretation = (
            "Train-label flank context materially improves the E101 hard-label prior over subject prior. "
            "It is strong enough to make E101 locally favorable under this visible transition-state prior."
        )
    elif useful:
        interpretation = (
            "Train-label flank context materially improves the E101 hard-label prior over subject prior, "
            "but the expected delta is still positive. E101 is less of a pure public sensor than before, "
            "yet it is not locally certified."
        )
    else:
        interpretation = (
            "Train-label flank context does not materially improve over subject prior. E101 remains a "
            "high-information public sensor about hidden local S3/Q2 labels, not a locally certified file."
        )
    report = f"""# E118 E101 Flank-Label Support Audit

## Question

E102 found weak edge locality for E101's `50` active Q2/S3 cells. E105 showed
that subject priors make the active hard-label world less implausible than
global priors. E114 showed raw context does not pre-validate that world.

This audit asks whether the simplest remaining visible context, train-label
flanks around each hidden block, supports the hard labels that would make E101
beat E95.

## Prior Summary

{md_table(summary[['prior','expected_delta_per_all_cells','beat_e95_probability','match_e95_mixmin_edge_probability','mean_support_probability','s3_support_probability','top10_flip_support_probability']], '.6f')}

## Target Breakdown

{md_table(by_target, '.6f')}

## Active-Cell Structure Versus Target-Count Null

{md_table(strongest_null, '.6f')}

## Structure Counts

{md_table(structure, '.6f')}

## Interpretation

- Best flank-like prior: `{best_row['prior']}` with beat-E95 probability `{best_row['beat_e95_probability']:.6f}`.
- Subject prior beat-E95 probability: `{subject_row['beat_e95_probability']:.6f}`.
- Best flank expected delta per all cells: `{best_row['expected_delta_per_all_cells']:.9f}`.
- Subject expected delta per all cells: `{subject_row['expected_delta_per_all_cells']:.9f}`.
- {interpretation}

## Decision

No submission is created. If E101 is submitted, this audit should be used as a
belief update, not as a post-hoc license to change branches:

- if E101 wins, the win strengthens an edge/flank transition-state reading of
  the `50` active cells and the E116 decoder should decide the E108 branch;
- if E101 ties or loses, the visible flank support was not strong enough to
  certify the file, so do not rescue the same rollback line by increasing
  amplitude or claiming train flanks had already proved it.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    train, sample = hbr.read_data()
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    meta = e102.build_hidden_row_meta(train, sample)
    all_cells = e102.build_cell_atlas(sample, meta)
    all_cells = add_flank_context(all_cells, train)

    d1, d0 = hard_loss_deltas(all_cells["prob_e101"].to_numpy(), all_cells["prob_e95"].to_numpy())
    all_cells["delta_y1"] = d1
    all_cells["delta_y0"] = d0
    active = all_cells["active"].to_numpy(bool)
    support_label = np.where(all_cells["delta_y1"] <= all_cells["delta_y0"], 1, 0)
    all_cells["support_label"] = support_label
    all_cells["support_delta"] = np.minimum(all_cells["delta_y1"], all_cells["delta_y0"])
    all_cells["adverse_delta"] = np.maximum(all_cells["delta_y1"], all_cells["delta_y0"])
    all_cells["flip_benefit"] = all_cells["adverse_delta"] - all_cells["support_delta"]
    active_cells = all_cells[active].copy().reset_index(drop=True)
    active_cells = add_support_priors(active_cells)

    priors = [
        "global",
        "subject",
        "prev_beta",
        "next_beta",
        "nearest_beta",
        "both_equal_beta",
        "both_distance_beta",
        "edge_endpoint_beta",
        "nearest_hard085",
        "conflict_flat",
    ]
    summary = pd.DataFrame([summarize_prior(active_cells, p) for p in priors]).sort_values(
        ["beat_e95_probability", "expected_delta_per_all_cells"], ascending=[False, True]
    )
    nulls = permutation_structure_null(all_cells)
    structure = pd.DataFrame(
        [
            {"metric": "active_cells", "value": float(len(active_cells))},
            {"metric": "q2_active_cells", "value": float(active_cells["target"].eq("Q2").sum())},
            {"metric": "s3_active_cells", "value": float(active_cells["target"].eq("S3").sum())},
            {"metric": "both_flanks_rate", "value": float(active_cells["both_flanks"].mean())},
            {"metric": "prev_only_rate", "value": float(active_cells["prev_only"].mean())},
            {"metric": "flank_conflict_rate", "value": float(active_cells["flank_conflict"].mean())},
            {
                "metric": "conflict_given_both_rate",
                "value": float(active_cells["flank_conflict"].sum() / max(active_cells["both_flanks"].sum(), 1)),
            },
            {
                "metric": "edge_or_near_edge_rate",
                "value": float(active_cells["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"]).mean()),
            },
            {"metric": "mean_min_flank_gap_days", "value": float(active_cells["min_flank_gap_days"].mean())},
            {"metric": "gap_le1_rate", "value": float((active_cells["min_flank_gap_days"] <= 1).mean())},
        ]
    )

    active_cells.to_csv(CELL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    structure.to_csv(STRUCTURE_OUT, index=False)
    write_report(active_cells, summary, nulls, structure)

    print(f"wrote {CELL_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {NULL_OUT}")
    print(f"wrote {STRUCTURE_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
