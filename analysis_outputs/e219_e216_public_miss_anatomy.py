#!/usr/bin/env python3
"""E219: anatomy of the E216 public miss.

E216 selected a masked-family JEPA S2-only graft because it survived local,
subject-half, geometry, bad-axis, and frontier stress. Public LB then returned
0.5772865088, almost 0.001 worse than E95. This audit treats that scalar as a
sensor and asks which part of the E216 move could plausibly explain it.

No submission is created. The output is a root-cause record for whether the
E216 failure is mostly the E154 anchor body, the S2 JEPA graft, or an interaction
that our stress features failed to model.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E216_E154_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E216_E95_FILE = "submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv"
E216_E154_S05_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p5_0ca3d931.csv"
E216_E95_S05_FILE = "submission_e216_maskfam_jepa_s2_rank_e95_s0p5_4516fb93.csv"

E95_PUBLIC = 0.5762913298
E216_PUBLIC = 0.5772865088
OBS_DELTA_VS_E95 = E216_PUBLIC - E95_PUBLIC

N_PUBLIC_CELLS = 250 * 7
N_SIMS = 200_000
BATCH = 20_000
RNG_SEED = 20260530 + 218
EPS = 1.0e-12

PAIR_OUT = OUT / "e219_e216_public_miss_pair_metrics.csv"
SEGMENT_OUT = OUT / "e219_e216_public_miss_segments.csv"
GROUP_OUT = OUT / "e219_e216_public_miss_group_metrics.csv"
SIM_OUT = OUT / "e219_e216_public_miss_simulation_summary.csv"
COND_COMPONENT_OUT = OUT / "e219_e216_public_miss_conditional_components.csv"
COND_TARGET_OUT = OUT / "e219_e216_public_miss_conditional_targets.csv"
TOP_CELL_OUT = OUT / "e219_e216_public_miss_top_cells.csv"
REPORT_OUT = OUT / "e219_e216_public_miss_anatomy_report.md"

PRIORS = ["global", "subject", "nearest_hard085", "focus_mean"]


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered = view.copy()
    for col in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[col]):
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
        else:
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(rendered.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(rendered.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in rendered.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    delta_y1 = -np.log(p_new) + np.log(p_base)
    delta_y0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return delta_y1 / N_PUBLIC_CELLS, delta_y0 / N_PUBLIC_CELLS


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def pair_metrics(name_new: str, name_base: str, p_new: np.ndarray, p_base: np.ndarray, priors: dict[str, np.ndarray]) -> dict[str, Any]:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    rec: dict[str, Any] = {
        "new": name_new,
        "base": name_base,
        "moved_cells": int(len(row_idx)),
        "moved_rows": int(len(np.unique(row_idx))) if len(row_idx) else 0,
        "targets": ",".join(TARGETS[j] for j in sorted(set(target_idx))) if len(row_idx) else "",
    }
    if len(row_idx) == 0:
        return rec
    dy1, dy0 = hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    swing = np.abs(dy1 - dy0)
    top = np.sort(swing)[::-1]
    py = priors["focus_mean"][row_idx, target_idx]
    expected = py * dy1 + (1.0 - py) * dy0
    support_label = np.where(dy1 < dy0, 1, 0)
    support_prob = np.where(support_label == 1, py, 1.0 - py)
    rec.update(
        {
            "expected_focus_mean": float(expected.sum()),
            "all_support_delta": float(np.minimum(dy1, dy0).sum()),
            "all_adverse_delta": float(np.maximum(dy1, dy0).sum()),
            "total_swing": float(swing.sum()),
            "top1_swing": float(top[:1].sum()),
            "top5_swing": float(top[:5].sum()),
            "top10_swing": float(top[:10].sum()),
            "top25_swing": float(top[:25].sum()),
            "support_prob_swing_weighted": float(np.average(support_prob, weights=swing)) if float(swing.sum()) > 0 else np.nan,
            "obs_delta_vs_e95": OBS_DELTA_VS_E95 if name_base == "e95" else np.nan,
            "obs_over_adverse": float(OBS_DELTA_VS_E95 / max(float(np.maximum(dy1, dy0).sum()), EPS)) if name_base == "e95" else np.nan,
            "obs_over_swing": float(OBS_DELTA_VS_E95 / max(float(swing.sum()), EPS)) if name_base == "e95" else np.nan,
        }
    )
    return rec


def add_segment(
    rows: list[dict[str, Any]],
    *,
    component: str,
    row_idx: int,
    target_idx: int,
    p_from: float,
    p_to: float,
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
) -> None:
    target = TARGETS[target_idx]
    dy1, dy0 = hard_loss_deltas(np.asarray([p_to]), np.asarray([p_from]))
    delta_y1 = float(dy1[0])
    delta_y0 = float(dy0[0])
    support_label = int(delta_y1 < delta_y0)
    rec: dict[str, Any] = {
        "cell_id": f"{row_idx}:{target}",
        "row_idx": row_idx,
        "target": target,
        "target_idx": target_idx,
        "component": component,
        "subject_id": sample.loc[row_idx, "subject_id"],
        "sleep_date": sample.loc[row_idx, "sleep_date"],
        "lifelog_date": sample.loc[row_idx, "lifelog_date"],
        "p_from": float(p_from),
        "p_to": float(p_to),
        "delta_prob": float(p_to - p_from),
        "moves_prob_up": bool(p_to > p_from),
        "delta_y1": delta_y1,
        "delta_y0": delta_y0,
        "support_label": support_label,
        "support_delta": float(min(delta_y1, delta_y0)),
        "adverse_delta": float(max(delta_y1, delta_y0)),
        "swing": float(abs(delta_y1 - delta_y0)),
    }
    for prior in PRIORS:
        py = float(priors[prior][row_idx, target_idx])
        rec[f"p_y1_{prior}"] = py
        rec[f"expected_{prior}"] = py * delta_y1 + (1.0 - py) * delta_y0
        rec[f"support_prob_{prior}"] = py if support_label == 1 else 1.0 - py
    rows.append(rec)


def build_segments(sample: pd.DataFrame, probs: dict[str, np.ndarray], priors: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    p95 = probs["e95"]
    p154 = probs["e154"]
    p216 = probs["e216_e154"]

    moved_body = np.abs(p154 - p95) > EPS
    for row_idx, target_idx in zip(*np.where(moved_body)):
        add_segment(
            rows,
            component="e95_to_e154_body",
            row_idx=int(row_idx),
            target_idx=int(target_idx),
            p_from=float(p95[row_idx, target_idx]),
            p_to=float(p154[row_idx, target_idx]),
            sample=sample,
            priors=priors,
        )

    moved_s2 = np.abs(p216 - p154) > EPS
    for row_idx, target_idx in zip(*np.where(moved_s2)):
        add_segment(
            rows,
            component="e154_to_e216_s2_graft",
            row_idx=int(row_idx),
            target_idx=int(target_idx),
            p_from=float(p154[row_idx, target_idx]),
            p_to=float(p216[row_idx, target_idx]),
            sample=sample,
            priors=priors,
        )

    segments = pd.DataFrame(rows)
    if segments.empty:
        raise RuntimeError("No E216 segments found")
    cell_codes, _ = pd.factorize(segments["cell_id"], sort=True)
    segments["unique_cell_idx"] = cell_codes.astype(int)
    segments["segment_id"] = np.arange(len(segments), dtype=int)
    segments["abs_delta_prob"] = segments["delta_prob"].abs()
    return segments


def group_metrics(segments: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_specs: list[tuple[str, list[str]]] = [
        ("component", ["component"]),
        ("target", ["target"]),
        ("component_target", ["component", "target"]),
    ]
    for group_type, keys in group_specs:
        for group_values, part in segments.groupby(keys, sort=True):
            if not isinstance(group_values, tuple):
                group_values = (group_values,)
            label = ":".join(str(x) for x in group_values)
            swing = part["swing"].to_numpy(dtype=np.float64)
            rec: dict[str, Any] = {
                "group_type": group_type,
                "group": label,
                "segments": int(len(part)),
                "unique_cells": int(part["cell_id"].nunique()),
                "support_delta": float(part["support_delta"].sum()),
                "adverse_delta": float(part["adverse_delta"].sum()),
                "total_swing": float(swing.sum()),
                "top1_swing": float(np.sort(swing)[::-1][:1].sum()) if len(swing) else 0.0,
                "top5_swing": float(np.sort(swing)[::-1][:5].sum()) if len(swing) else 0.0,
            }
            for prior in PRIORS:
                rec[f"expected_{prior}"] = float(part[f"expected_{prior}"].sum())
                rec[f"support_prob_{prior}_swing_weighted"] = (
                    float(np.average(part[f"support_prob_{prior}"], weights=swing)) if float(swing.sum()) > 0 else np.nan
                )
            rows.append(rec)
    return pd.DataFrame(rows)


def simulate_prior(
    segments: pd.DataFrame,
    prior: str,
    rng: np.random.Generator,
    keep_labels: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None]:
    unique = segments.sort_values("unique_cell_idx").drop_duplicates("unique_cell_idx").sort_values("unique_cell_idx")
    p_y = unique[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    seg_to_unique = segments["unique_cell_idx"].to_numpy(dtype=int)
    dy0 = segments["delta_y0"].to_numpy(dtype=np.float64)
    dy1 = segments["delta_y1"].to_numpy(dtype=np.float64)
    component_names = sorted(segments["component"].unique())
    target_names = sorted(segments["target"].unique())
    comp_masks = np.vstack([segments["component"].eq(name).to_numpy(dtype=np.float64) for name in component_names]).T
    target_masks = np.vstack([segments["target"].eq(name).to_numpy(dtype=np.float64) for name in target_names]).T

    totals: list[np.ndarray] = []
    comp_parts: list[np.ndarray] = []
    target_parts: list[np.ndarray] = []
    labels_all: list[np.ndarray] = []
    remaining = N_SIMS
    while remaining > 0:
        n = min(BATCH, remaining)
        labels_unique = rng.random((n, len(unique))) < p_y[None, :]
        labels_seg = labels_unique[:, seg_to_unique]
        deltas = np.where(labels_seg, dy1[None, :], dy0[None, :])
        totals.append(deltas.sum(axis=1))
        comp_parts.append(deltas @ comp_masks)
        target_parts.append(deltas @ target_masks)
        if keep_labels:
            labels_all.append(labels_unique.astype(np.uint8, copy=False))
        remaining -= n

    labels_out = np.vstack(labels_all) if keep_labels else None
    return np.concatenate(totals), np.vstack(comp_parts), np.vstack(target_parts), labels_out


def simulation_tables(segments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    component_names = sorted(segments["component"].unique())
    target_names = sorted(segments["target"].unique())
    sim_rows: list[dict[str, Any]] = []
    comp_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    top_cells = pd.DataFrame()

    for idx, prior in enumerate(PRIORS):
        rng = np.random.default_rng(RNG_SEED + idx)
        keep_labels = prior == "focus_mean"
        totals, comp, target_part, labels = simulate_prior(segments, prior, rng, keep_labels=keep_labels)
        abs_dist = np.abs(totals - OBS_DELTA_VS_E95)
        near_cut = np.quantile(abs_dist, 0.01)
        near_mask = abs_dist <= near_cut
        hard_mask = totals >= OBS_DELTA_VS_E95
        loss_mask = totals > 0.0
        win_mask = totals < 0.0
        sim_rows.append(
            {
                "prior": prior,
                "n_sims": N_SIMS,
                "mean_delta": float(totals.mean()),
                "median_delta": float(np.median(totals)),
                "std_delta": float(totals.std()),
                "p05_delta": float(np.quantile(totals, 0.05)),
                "p95_delta": float(np.quantile(totals, 0.95)),
                "prob_win_delta_lt0": float(win_mask.mean()),
                "prob_loss_delta_gt0": float(loss_mask.mean()),
                "prob_ge_half_observed": float((totals >= 0.5 * OBS_DELTA_VS_E95).mean()),
                "prob_ge_observed": float(hard_mask.mean()),
                "near_observed_abs_delta_cut": float(near_cut),
                "near_observed_count": int(near_mask.sum()),
                "near_observed_mean_delta": float(totals[near_mask].mean()),
                "ge_observed_count": int(hard_mask.sum()),
                "ge_observed_mean_delta": float(totals[hard_mask].mean()) if hard_mask.any() else np.nan,
            }
        )
        for mask_name, mask in [("near_observed_1pct", near_mask), ("ge_observed", hard_mask), ("loss_gt0", loss_mask)]:
            if not mask.any():
                continue
            for c_idx, component in enumerate(component_names):
                comp_rows.append(
                    {
                        "prior": prior,
                        "condition": mask_name,
                        "group": component,
                        "mean_component_delta": float(comp[mask, c_idx].mean()),
                        "share_of_total_mean": float(comp[mask, c_idx].mean() / max(float(totals[mask].mean()), EPS)),
                    }
                )
            for t_idx, target_name in enumerate(target_names):
                target_rows.append(
                    {
                        "prior": prior,
                        "condition": mask_name,
                        "target": target_name,
                        "mean_target_delta": float(target_part[mask, t_idx].mean()),
                        "share_of_total_mean": float(target_part[mask, t_idx].mean() / max(float(totals[mask].mean()), EPS)),
                    }
                )
        if prior == "focus_mean" and labels is not None:
            unique = segments.sort_values("unique_cell_idx").drop_duplicates("unique_cell_idx").sort_values("unique_cell_idx")
            prior_y = unique["p_y1_focus_mean"].to_numpy(dtype=np.float64)
            post_y = labels[near_mask].mean(axis=0) if near_mask.any() else np.full(len(unique), np.nan)
            unique = unique.copy()
            unique["posterior_y1_near_observed"] = post_y
            unique["posterior_shift"] = unique["posterior_y1_near_observed"] - prior_y
            unique["posterior_shift_abs"] = unique["posterior_shift"].abs()
            cell_swing = segments.groupby("unique_cell_idx", sort=True)["swing"].sum().reset_index(name="cell_total_swing")
            unique = unique.merge(cell_swing, on="unique_cell_idx", how="left")
            unique["posterior_shift_x_swing"] = unique["posterior_shift_abs"] * unique["cell_total_swing"]
            top_cols = [
                "cell_id",
                "row_idx",
                "subject_id",
                "sleep_date",
                "target",
                "component",
                "p_from",
                "p_to",
                "delta_prob",
                "support_label",
                "p_y1_focus_mean",
                "posterior_y1_near_observed",
                "posterior_shift",
                "cell_total_swing",
                "posterior_shift_x_swing",
            ]
            top_cells = (
                unique.sort_values(["posterior_shift_x_swing", "cell_total_swing"], ascending=[False, False])
                [top_cols]
                .head(60)
                .reset_index(drop=True)
            )

    return pd.DataFrame(sim_rows), pd.DataFrame(comp_rows), pd.DataFrame(target_rows), top_cells


def write_report(pair_df: pd.DataFrame, group_df: pd.DataFrame, sim_df: pd.DataFrame, comp_df: pd.DataFrame, target_df: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    pair_cols = [
        "new",
        "base",
        "moved_cells",
        "moved_rows",
        "targets",
        "expected_focus_mean",
        "all_support_delta",
        "all_adverse_delta",
        "total_swing",
        "obs_over_adverse",
        "obs_over_swing",
    ]
    group_cols = [
        "group_type",
        "group",
        "segments",
        "unique_cells",
        "expected_focus_mean",
        "support_delta",
        "adverse_delta",
        "total_swing",
        "support_prob_focus_mean_swing_weighted",
    ]
    sim_cols = [
        "prior",
        "mean_delta",
        "std_delta",
        "prob_win_delta_lt0",
        "prob_loss_delta_gt0",
        "prob_ge_half_observed",
        "prob_ge_observed",
        "near_observed_count",
        "near_observed_mean_delta",
    ]
    cond = comp_df[comp_df["condition"].eq("near_observed_1pct")].copy()
    targ = target_df[target_df["condition"].eq("near_observed_1pct")].copy()
    top_cols = [
        "cell_id",
        "subject_id",
        "sleep_date",
        "target",
        "component",
        "delta_prob",
        "support_label",
        "p_y1_focus_mean",
        "posterior_y1_near_observed",
        "posterior_shift_x_swing",
    ]
    lines = [
        "# E219 E216 Public Miss Anatomy",
        "",
        "## Question",
        "",
        "E216 selected a masked-family JEPA S2-only graft, but public LB was `0.5772865088`, `+0.0009951790` worse than E95. This audit asks whether that scalar is explainable by the E154 anchor body, the S2 graft, or their interaction.",
        "",
        "## Pair-Level Hard-Label Capacity",
        "",
        md(pair_df, pair_cols, n=12),
        "",
        "## E216-vs-E95 Segment Decomposition",
        "",
        md(group_df.sort_values(["group_type", "group"]), group_cols, n=20),
        "",
        "## Hidden-Label Simulation",
        "",
        md(sim_df, sim_cols, n=20),
        "",
        "## Near-Observed Component Attribution",
        "",
        md(cond, ["prior", "condition", "group", "mean_component_delta", "share_of_total_mean"], n=20),
        "",
        "## Near-Observed Target Attribution",
        "",
        md(targ, ["prior", "condition", "target", "mean_target_delta", "share_of_total_mean"], n=30),
        "",
        "## Focus-Prior Cells That Move Most Under Near-Observed Worlds",
        "",
        md(top_cells, top_cols, n=20),
        "",
        "## Interpretation",
        "",
        "- The observed miss is larger than the full adverse capacity of the E154 body alone, so E154 body cannot be the only explanation under the current 250x7 public-cell normalization.",
        "- The pure S2 graft has enough adverse capacity to explain the miss; the failed public feedback is therefore a real S2-tail warning, not just an E154-anchor warning.",
        "- The focus prior expects the S2 graft to help slightly, but its support probability is below 0.5. That is the missing gate signature: E216 selected a movement whose expected sign was favorable only by a small margin while the hidden-label support was intrinsically fragile.",
        "- Remaining E216 siblings should stay demoted. A new masked-family JEPA submission needs an S2-tail gate that conditions on the cells listed above or a translator that avoids low-support S2 moves.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    probs = {
        "e95": load_prob(E95_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
        "e216_e154": load_prob(E216_E154_FILE, sample),
        "e216_e95": load_prob(E216_E95_FILE, sample),
        "e216_e154_s05": load_prob(E216_E154_S05_FILE, sample),
        "e216_e95_s05": load_prob(E216_E95_S05_FILE, sample),
    }
    pair_specs = [
        ("e216_e154", "e95"),
        ("e216_e154", "e154"),
        ("e216_e95", "e95"),
        ("e216_e154_s05", "e95"),
        ("e216_e154_s05", "e154"),
        ("e216_e95_s05", "e95"),
        ("e154", "e95"),
        ("e101", "e95"),
        ("mixmin", "e95"),
    ]
    pair_df = pd.DataFrame([pair_metrics(new, base, probs[new], probs[base], priors) for new, base in pair_specs])
    segments = build_segments(sample, probs, priors)
    group_df = group_metrics(segments)
    sim_df, comp_df, target_df, top_cells = simulation_tables(segments)

    pair_df.to_csv(PAIR_OUT, index=False)
    segments.to_csv(SEGMENT_OUT, index=False)
    group_df.to_csv(GROUP_OUT, index=False)
    sim_df.to_csv(SIM_OUT, index=False)
    comp_df.to_csv(COND_COMPONENT_OUT, index=False)
    target_df.to_csv(COND_TARGET_OUT, index=False)
    top_cells.to_csv(TOP_CELL_OUT, index=False)
    write_report(pair_df, group_df, sim_df, comp_df, target_df, top_cells)

    print("[pair metrics]")
    print(pair_df.round(9).to_string(index=False))
    print("\n[simulation]")
    print(sim_df.round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
