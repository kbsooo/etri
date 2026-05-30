#!/usr/bin/env python3
"""E204: map what each post-E176 follow-up actually corrects.

E203 separates E176 into broad body and compact tail. E204 overlays the current
follow-up candidates on that anatomy, so a future E176 score routes to a
candidate for the right reason rather than by name or scalar score alone.

No submission is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-12
METRIC_DENOM = 250 * len(TARGETS)

FILES = {
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e176": "submission_e176_abl_q2_to0p75_91e49725.csv",
    "e172_safety": "submission_e172_vis_pos_all_keep0p25_d90f4407.csv",
    "e174_q2_reopen": "submission_e174_ro_fc_top75_to1p0_95638e73.csv",
    "e154_counterworld": "submission_e154_s3repair_9f2e2e73.csv",
    "e144_tail_control": "submission_e144_activeboundary_d7b4b331.csv",
}

CELLS = OUT / "e179_e176_critical_cell_visibility_cells.csv"
OUT_SUMMARY = OUT / "e204_e176_followup_correction_map_summary.csv"
OUT_COMPONENTS = OUT / "e204_e176_followup_correction_map_components.csv"
OUT_REPORT = OUT / "e204_e176_followup_correction_map_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()

    def render(v: Any) -> str:
        if isinstance(v, float):
            return f"{v:.12g}"
        return str(v)

    def clean(s: str) -> str:
        return s.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(str(c)) for c in view.columns) + " |",
        "| " + " | ".join("---" for _ in view.columns) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(render(row[c])) for c in view.columns) + " |")
    return "\n".join(lines)


def load_submissions() -> dict[str, pd.DataFrame]:
    dfs: dict[str, pd.DataFrame] = {}
    for name, file_name in FILES.items():
        df = pd.read_csv(OUT / file_name)
        dfs[name] = df
    ref = dfs["e176"][KEYS]
    for name, df in dfs.items():
        if not df[KEYS].equals(ref):
            raise ValueError(f"key mismatch for {name}")
    return dfs


def logloss_delta(p_old: np.ndarray, p_new: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p_old = np.clip(p_old.astype(float), 1e-6, 1 - 1e-6)
    p_new = np.clip(p_new.astype(float), 1e-6, 1 - 1e-6)
    y_prob = y_prob.astype(float)
    ll_old = -(y_prob * np.log(p_old) + (1.0 - y_prob) * np.log1p(-p_old))
    ll_new = -(y_prob * np.log(p_new) + (1.0 - y_prob) * np.log1p(-p_new))
    return ll_new - ll_old


def cell_values(df: pd.DataFrame, cells: pd.DataFrame) -> np.ndarray:
    return np.array([df.at[int(r.sub_idx), str(r.target)] for r in cells.itertuples()], dtype=float)


def summarize_candidate(name: str, dfs: dict[str, pd.DataFrame], cells: pd.DataFrame) -> dict[str, Any]:
    e95 = dfs["e95"]
    e176 = dfs["e176"]
    cand = dfs[name]
    e176_move_mat = e176[TARGETS].to_numpy(dtype=float) - e95[TARGETS].to_numpy(dtype=float)
    follow_mat = cand[TARGETS].to_numpy(dtype=float) - e176[TARGETS].to_numpy(dtype=float)
    e176_moved = np.abs(e176_move_mat) > EPS
    follow_moved = np.abs(follow_mat) > EPS
    overlap = e176_moved & follow_moved
    off_body = (~e176_moved) & follow_moved
    rollback = overlap & (np.sign(follow_mat) == -np.sign(e176_move_mat))
    amplify = overlap & (np.sign(follow_mat) == np.sign(e176_move_mat))
    changed_rows = np.flatnonzero(follow_moved.any(axis=1))

    old = cell_values(e176, cells)
    new = cell_values(cand, cells)
    follow = new - old
    base = cell_values(e95, cells)
    e176_delta = old - base
    cell_changed = np.abs(follow) > EPS
    cell_rollback = cell_changed & (np.sign(follow) == -np.sign(e176_delta))
    capped_rollback = np.where(cell_rollback, np.minimum(np.abs(follow), np.abs(e176_delta)), 0.0)
    focus_delta = logloss_delta(old, new, cells["p_y1_focus_mean"].to_numpy(dtype=float))
    visible_delta = logloss_delta(old, new, cells["p_y1_visible_mean"].to_numpy(dtype=float))

    total_follow_abs = float(np.abs(follow_mat[follow_moved]).sum())
    in_follow_abs = float(np.abs(follow_mat[overlap]).sum())
    off_follow_abs = float(np.abs(follow_mat[off_body]).sum())
    rollback_abs = float(np.abs(follow_mat[rollback]).sum())
    amplify_abs = float(np.abs(follow_mat[amplify]).sum())
    e176_abs = float(np.abs(e176_move_mat[e176_moved]).sum())
    return {
        "candidate": name,
        "n_changed_cells_vs_e176": int(follow_moved.sum()),
        "n_changed_rows_vs_e176": int(len(changed_rows)),
        "n_overlap_e176_cells": int(overlap.sum()),
        "n_off_e176_cells": int(off_body.sum()),
        "off_e176_abs_share": off_follow_abs / total_follow_abs if total_follow_abs else 0.0,
        "rollback_abs_share_in_overlap": rollback_abs / in_follow_abs if in_follow_abs else 0.0,
        "amplify_abs_share_in_overlap": amplify_abs / in_follow_abs if in_follow_abs else 0.0,
        "e176_body_rollback_fraction": float(capped_rollback.sum() / np.abs(e176_delta).sum()),
        "expected_focus_delta_on_e176_cells": float(focus_delta.sum()),
        "expected_visible_delta_on_e176_cells": float(visible_delta.sum()),
        "metric_focus_delta_on_e176_cells": float(focus_delta.sum() / METRIC_DENOM),
        "metric_visible_delta_on_e176_cells": float(visible_delta.sum() / METRIC_DENOM),
        "changed_e176_cell_count": int(cell_changed.sum()),
        "rollback_e176_cell_count": int(cell_rollback.sum()),
        "top33_changed_count": int((cell_changed & (cells["swing_rank"].to_numpy() <= 33)).sum()),
        "top33_rollback_count": int((cell_rollback & (cells["swing_rank"].to_numpy() <= 33)).sum()),
        "total_follow_abs": total_follow_abs,
        "in_e176_follow_abs": in_follow_abs,
        "off_e176_follow_abs": off_follow_abs,
        "rollback_abs": rollback_abs,
        "amplify_abs": amplify_abs,
        "e176_total_abs": e176_abs,
    }


def component_masks(cells: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "full": pd.Series(True, index=cells.index),
        "primary_s": cells["target"].isin(["S1", "S3", "S4"]),
        "q2": cells["target"].eq("Q2"),
        "only_s": cells["target_group"].eq("S"),
        "between_train_runs": cells["between_train_runs"].astype(bool),
        "top33": cells["swing_rank"] <= 33,
        "top8": cells["swing_rank"] <= 8,
        "top33_low_visible": (cells["swing_rank"] <= 33) & (cells["support_probability_visible_mean"] < 0.30),
        "body_not_top33": cells["swing_rank"] > 33,
        "primary_s_not_top33": cells["target"].isin(["S1", "S3", "S4"]) & (cells["swing_rank"] > 33),
        "visible_low": cells["support_probability_visible_mean"] < 0.30,
        "visible_high": cells["support_probability_visible_mean"] >= 0.50,
        "id06_id07": cells["subject_id"].isin(["id06", "id07"]),
    }


def summarize_component(name: str, comp: str, mask: pd.Series, dfs: dict[str, pd.DataFrame], cells: pd.DataFrame) -> dict[str, Any]:
    if not bool(mask.any()):
        return {"candidate": name, "component": comp, "n_cells": 0}
    sub = cells.loc[mask].copy()
    old = cell_values(dfs["e176"], sub)
    new = cell_values(dfs[name], sub)
    base = cell_values(dfs["e95"], sub)
    follow = new - old
    e176_delta = old - base
    changed = np.abs(follow) > EPS
    rollback = changed & (np.sign(follow) == -np.sign(e176_delta))
    amplify = changed & (np.sign(follow) == np.sign(e176_delta))
    capped_rollback = np.where(rollback, np.minimum(np.abs(follow), np.abs(e176_delta)), 0.0)
    focus_delta = logloss_delta(old, new, sub["p_y1_focus_mean"].to_numpy(dtype=float))
    visible_delta = logloss_delta(old, new, sub["p_y1_visible_mean"].to_numpy(dtype=float))
    follow_abs = float(np.abs(follow[changed]).sum())
    e176_abs = float(np.abs(e176_delta).sum())
    return {
        "candidate": name,
        "component": comp,
        "n_cells": int(len(sub)),
        "n_changed_cells": int(changed.sum()),
        "n_rollback_cells": int(rollback.sum()),
        "n_amplify_cells": int(amplify.sum()),
        "follow_abs": follow_abs,
        "rollback_abs": float(np.abs(follow[rollback]).sum()),
        "amplify_abs": float(np.abs(follow[amplify]).sum()),
        "rollback_abs_share": float(np.abs(follow[rollback]).sum() / follow_abs) if follow_abs else 0.0,
        "component_rollback_fraction": float(capped_rollback.sum() / e176_abs) if e176_abs else 0.0,
        "expected_focus_delta": float(focus_delta.sum()),
        "expected_visible_delta": float(visible_delta.sum()),
        "metric_focus_delta": float(focus_delta.sum() / METRIC_DENOM),
        "metric_visible_delta": float(visible_delta.sum() / METRIC_DENOM),
        "mean_support_visible": float(sub["support_probability_visible_mean"].mean()),
        "swing_share": float(sub["swing"].sum() / cells["swing"].sum()),
        "e72_active_rate": float(sub["e72_active"].mean()),
    }


def classify_summary(row: pd.Series) -> str:
    off = float(row["off_e176_abs_share"])
    rollback = float(row["rollback_abs_share_in_overlap"])
    body_rollback = float(row["e176_body_rollback_fraction"])
    focus = float(row["expected_focus_delta_on_e176_cells"])
    top33 = int(row["top33_rollback_count"])
    if off >= 0.50:
        return "counterworld_new_axis"
    if off >= 0.25 and body_rollback >= 0.75:
        return "counterworld_body_exit"
    if rollback >= 0.75 and focus > 0:
        return "safety_rollback_costs_e176_body"
    if rollback >= 0.75:
        return "safety_rollback"
    if top33 >= 10 and body_rollback < 0.50:
        return "tail_repair_probe"
    if rollback <= 0.25 and off < 0.20:
        return "same_family_amplitude_probe"
    return "mixed_followup"


def write_report(summary: pd.DataFrame, components: pd.DataFrame) -> None:
    e172 = summary.loc[summary["candidate"].eq("e172_safety")].iloc[0]
    e154 = summary.loc[summary["candidate"].eq("e154_counterworld")].iloc[0]
    e174 = summary.loc[summary["candidate"].eq("e174_q2_reopen")].iloc[0]

    focus = components.pivot(index="component", columns="candidate", values="metric_focus_delta")
    rollback = components.pivot(index="component", columns="candidate", values="component_rollback_fraction")

    lines = [
        "# E204 E176 Follow-up Correction Map",
        "",
        "## Question",
        "",
        "If E176 lands in a tie/loss band, which existing follow-up actually corrects E176's body-tail failure mode?",
        "",
        "## Result",
        "",
        "The current follow-up files ask different questions; they are not interchangeable.",
        "",
        f"- E172 is a same-family rollback: rollback share in E176 overlap `{e172['rollback_abs_share_in_overlap']:.6f}`, off-E176 abs share `{e172['off_e176_abs_share']:.6f}`.",
        f"- E154 is a counter-world: off-E176 abs share `{e154['off_e176_abs_share']:.6f}`, so it is not just a tail repair.",
        f"- E174 is an amplitude probe: off-E176 abs share `{e174['off_e176_abs_share']:.6f}`, Q2-focused by construction, and should wait for a clean E176 win.",
        "",
        "Interpretation: if E176 ties or small-loses, E172 is coherent because it rolls back the same family rather than introducing a new axis. If E176 branch/hard-loses, E154 is coherent because it exits the E176 body rather than pretending the same body only needs Q2 amplitude. E174 is not the default rescue; it asks a second-order Q2 amplitude question.",
        "",
        "## Candidate Summary",
        "",
        md_table(
            summary,
            [
                "candidate",
                "role",
                "n_changed_cells_vs_e176",
                "n_changed_rows_vs_e176",
                "n_overlap_e176_cells",
                "n_off_e176_cells",
                "off_e176_abs_share",
                "rollback_abs_share_in_overlap",
                "e176_body_rollback_fraction",
                "metric_focus_delta_on_e176_cells",
                "metric_visible_delta_on_e176_cells",
                "top33_changed_count",
                "top33_rollback_count",
            ],
            n=20,
        ),
        "",
        "## Component Metric-Scale Expected Delta: candidate vs E176 on E176 cells",
        "",
        md_table(focus.reset_index(), n=30),
        "",
        "## Component Rollback Fraction",
        "",
        md_table(rollback.reset_index(), n=30),
        "",
        "## Component Detail",
        "",
        md_table(
            components.sort_values(["component", "candidate"]),
            [
                "candidate",
                "component",
                "n_changed_cells",
                "n_rollback_cells",
                "rollback_abs_share",
                "component_rollback_fraction",
                "metric_focus_delta",
                "metric_visible_delta",
                "mean_support_visible",
                "e72_active_rate",
            ],
            n=80,
        ),
        "",
        "## Decision",
        "",
        "No submission is created. E204 locks the follow-up interpretation: E172 is same-family safety after tie/small-loss, E154 is the branch escape after adverse loss, and E174 is only a paired Q2 amplitude probe after broad-body validation.",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    dfs = load_submissions()
    cells = pd.read_csv(CELLS)
    followups = ["e172_safety", "e174_q2_reopen", "e154_counterworld", "e144_tail_control", "e95"]
    summary_rows = [summarize_candidate(name, dfs, cells) for name in followups]
    summary = pd.DataFrame(summary_rows)
    summary["role"] = summary.apply(classify_summary, axis=1)
    summary = summary.sort_values(
        "candidate",
        key=lambda s: s.map(
            {
                "e172_safety": "1",
                "e154_counterworld": "2",
                "e174_q2_reopen": "3",
                "e144_tail_control": "4",
                "e95": "5",
            }
        ).fillna(s),
    ).reset_index(drop=True)

    masks = component_masks(cells)
    comp_rows = []
    for name in followups:
        for comp, mask in masks.items():
            comp_rows.append(summarize_component(name, comp, mask, dfs, cells))
    components = pd.DataFrame(comp_rows)
    summary.to_csv(OUT_SUMMARY, index=False)
    components.to_csv(OUT_COMPONENTS, index=False)
    write_report(summary, components)
    print(f"wrote {OUT_SUMMARY}")
    print(f"wrote {OUT_COMPONENTS}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
