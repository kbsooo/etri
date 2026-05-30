#!/usr/bin/env python3
"""E203: pre-public component knockout stress for E176.

E202 says E176 should not be read as Q2-only. E203 asks a sharper question:
which components are necessary for the E176 worldview, and which components
mainly carry unresolved hard-tail risk?

No submission is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

PUBLIC_EDGE_E95_OVER_MIXMIN = 0.5763066405 - 0.5762913298

CELLS = OUT / "e179_e176_critical_cell_visibility_cells.csv"
COMPONENT = OUT / "e202_e176_component_responsibility_component_summary.csv"
SUBJECT = OUT / "e202_e176_component_responsibility_subject_summary.csv"

OUT_COMPONENTS = OUT / "e203_e176_component_knockout_stress_components.csv"
OUT_TARGETS = OUT / "e203_e176_component_knockout_stress_target_table.csv"
OUT_REPORT = OUT / "e203_e176_component_knockout_stress_report.md"


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


def cells_to_cover(delta: pd.Series, edge: float = PUBLIC_EDGE_E95_OVER_MIXMIN) -> int:
    """Minimum cells needed for cumulative expected gain to exceed a public edge."""
    beneficial = np.sort(delta.loc[delta < 0].to_numpy())
    if beneficial.size == 0:
        return -1
    csum = np.cumsum(beneficial)
    hits = np.flatnonzero(csum <= -edge)
    if hits.size == 0:
        return -1
    return int(hits[0] + 1)


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    if len(values) == 0:
        return float("nan")
    w = weights.astype(float).to_numpy()
    if float(np.abs(w).sum()) == 0.0:
        return float(values.mean())
    return float(np.average(values.astype(float).to_numpy(), weights=w))


def summarize(name: str, desc: str, mask: pd.Series, full: pd.DataFrame) -> dict[str, Any]:
    g = full.loc[mask].copy()
    full_focus = float(full["expected_delta_focus_mean"].sum())
    full_visible = float(full["expected_delta_visible_mean"].sum())
    full_swing = float(full["swing"].sum())
    full_top33 = int((full["swing_rank"] <= 33).sum())
    full_top8 = int((full["swing_rank"] <= 8).sum())
    if g.empty:
        return {
            "component": name,
            "description": desc,
            "n_cells": 0,
            "n_rows": 0,
            "targets": "",
            "subjects": "",
            "expected_delta_focus": 0.0,
            "expected_focus_share": 0.0,
            "drop_remaining_focus_delta": full_focus,
            "drop_remaining_focus_share": 1.0,
            "expected_delta_visible": 0.0,
            "expected_visible_share": 0.0,
            "swing_share": 0.0,
            "top33_coverage": 0.0,
            "top8_coverage": 0.0,
            "cells_to_cover_e95_edge_focus": -1,
            "support_visible_swing_weighted": float("nan"),
            "support_focus_swing_weighted": float("nan"),
            "all_prior_support_rate": float("nan"),
            "prior_split_rate": float("nan"),
            "flank_conflict_rate": float("nan"),
            "e72_active_rate": float("nan"),
            "between_train_runs_rate": float("nan"),
            "mean_safe_density": float("nan"),
        }

    focus = float(g["expected_delta_focus_mean"].sum())
    visible = float(g["expected_delta_visible_mean"].sum())
    swing = float(g["swing"].sum())
    top33 = int((g["swing_rank"] <= 33).sum())
    top8 = int((g["swing_rank"] <= 8).sum())
    drop_focus = full_focus - focus
    return {
        "component": name,
        "description": desc,
        "n_cells": int(len(g)),
        "n_rows": int(g["sub_idx"].nunique()),
        "targets": ",".join(sorted(g["target"].unique())),
        "subjects": ",".join(sorted(g["subject_id"].unique())),
        "expected_delta_focus": focus,
        "expected_focus_share": focus / full_focus if full_focus else float("nan"),
        "drop_remaining_focus_delta": drop_focus,
        "drop_remaining_focus_share": drop_focus / full_focus if full_focus else float("nan"),
        "expected_delta_visible": visible,
        "expected_visible_share": visible / full_visible if full_visible else float("nan"),
        "swing_share": swing / full_swing if full_swing else float("nan"),
        "top33_coverage": top33 / full_top33 if full_top33 else 0.0,
        "top8_coverage": top8 / full_top8 if full_top8 else 0.0,
        "cells_to_cover_e95_edge_focus": cells_to_cover(g["expected_delta_focus_mean"]),
        "support_visible_swing_weighted": weighted_mean(g["support_probability_visible_mean"], g["swing"]),
        "support_focus_swing_weighted": weighted_mean(g["support_probability_focus_mean"], g["swing"]),
        "all_prior_support_rate": float(g["all_prior_support"].mean()),
        "prior_split_rate": float(g["prior_split"].mean()),
        "flank_conflict_rate": float(g["flank_conflict"].mean()),
        "e72_active_rate": float(g["e72_active"].mean()),
        "between_train_runs_rate": float(g["between_train_runs"].mean()),
        "mean_safe_density": float(g["all_safe_density"].mean()),
    }


def component_role(row: pd.Series) -> str:
    share = float(row["expected_focus_share"])
    drop_share = float(row["drop_remaining_focus_share"])
    top33 = float(row["top33_coverage"])
    visible = float(row["support_visible_swing_weighted"])
    cells = int(row["cells_to_cover_e95_edge_focus"])
    e72 = float(row["e72_active_rate"])

    if share >= 0.55 and drop_share <= 0.45:
        return "necessary_body"
    if share >= 0.30 and cells > 0 and cells <= 8:
        return "compact_edge_carrier"
    if top33 >= 0.35 and visible < 0.30:
        return "hard_tail_uncertain"
    if share < 0.15 and top33 < 0.10:
        return "secondary_or_guard"
    if e72 >= 0.45:
        return "e72_tail_risk"
    return "mixed_component"


def build_components(cells: pd.DataFrame) -> pd.DataFrame:
    target = cells["target"]
    top_subjects = {"id06", "id07"}
    masks: list[tuple[str, str, Callable[[pd.DataFrame], pd.Series]]] = [
        ("full", "all E176-vs-E95 moved cells", lambda d: pd.Series(True, index=d.index)),
        ("only_Q", "Q targets only", lambda d: d["target_group"].eq("Q")),
        ("only_S", "S targets only", lambda d: d["target_group"].eq("S")),
        ("drop_Q", "all except Q targets", lambda d: ~d["target_group"].eq("Q")),
        ("drop_S", "all except S targets", lambda d: ~d["target_group"].eq("S")),
        ("only_Q2", "Q2 only", lambda d: d["target"].eq("Q2")),
        ("drop_Q2", "all except Q2", lambda d: ~d["target"].eq("Q2")),
        ("only_primary_S", "S3/S1/S4 primary S-stage body", lambda d: d["target"].isin(["S3", "S1", "S4"])),
        ("drop_primary_S", "all except S3/S1/S4", lambda d: ~d["target"].isin(["S3", "S1", "S4"])),
        ("only_S3", "S3 only", lambda d: d["target"].eq("S3")),
        ("drop_S3", "all except S3", lambda d: ~d["target"].eq("S3")),
        ("only_S1", "S1 only", lambda d: d["target"].eq("S1")),
        ("drop_S1", "all except S1", lambda d: ~d["target"].eq("S1")),
        ("only_S4", "S4 only", lambda d: d["target"].eq("S4")),
        ("drop_S4", "all except S4", lambda d: ~d["target"].eq("S4")),
        ("only_between_train_runs", "between-train-runs rows only", lambda d: d["between_train_runs"].astype(bool)),
        ("drop_between_train_runs", "all except between-train-runs rows", lambda d: ~d["between_train_runs"].astype(bool)),
        ("only_top33", "top33 swing cells only", lambda d: d["swing_rank"] <= 33),
        ("drop_top33", "all except top33 swing cells", lambda d: d["swing_rank"] > 33),
        ("only_top8", "top8 swing cells only", lambda d: d["swing_rank"] <= 8),
        ("drop_top8", "all except top8 swing cells", lambda d: d["swing_rank"] > 8),
        ("only_id06_id07", "top swing subjects id06/id07", lambda d: d["subject_id"].isin(top_subjects)),
        ("drop_id06_id07", "all except top swing subjects id06/id07", lambda d: ~d["subject_id"].isin(top_subjects)),
        (
            "only_visible_high",
            "visible support probability >= 0.50",
            lambda d: d["support_probability_visible_mean"] >= 0.50,
        ),
        (
            "only_visible_low",
            "visible support probability < 0.30",
            lambda d: d["support_probability_visible_mean"] < 0.30,
        ),
    ]
    rows = [summarize(name, desc, fn(cells), cells) for name, desc, fn in masks]
    out = pd.DataFrame(rows)
    out["role"] = out.apply(component_role, axis=1)
    out = out.sort_values(
        ["component"],
        key=lambda s: s.map({"full": "000_full"}).fillna(s),
    ).reset_index(drop=True)
    return out


def build_target_table(cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target, g in cells.groupby("target", sort=False):
        rows.append(summarize(str(target), f"target {target}", cells["target"].eq(target), cells))
    out = pd.DataFrame(rows)
    out["rank_expected_share"] = out["expected_focus_share"].abs().rank(ascending=False, method="first").astype(int)
    out["rank_top33"] = out["top33_coverage"].rank(ascending=False, method="first").astype(int)
    out["rank_visible_support"] = out["support_visible_swing_weighted"].rank(ascending=False, method="first").astype(int)
    out["role"] = out.apply(component_role, axis=1)
    return out.sort_values("rank_expected_share").reset_index(drop=True)


def write_report(components: pd.DataFrame, targets: pd.DataFrame) -> None:
    full = components.loc[components["component"].eq("full")].iloc[0]
    only_s = components.loc[components["component"].eq("only_S")].iloc[0]
    only_q2 = components.loc[components["component"].eq("only_Q2")].iloc[0]
    primary_s = components.loc[components["component"].eq("only_primary_S")].iloc[0]
    top33 = components.loc[components["component"].eq("only_top33")].iloc[0]
    drop_top33 = components.loc[components["component"].eq("drop_top33")].iloc[0]
    between = components.loc[components["component"].eq("only_between_train_runs")].iloc[0]
    drop_between = components.loc[components["component"].eq("drop_between_train_runs")].iloc[0]

    role_summary = components["role"].value_counts().rename_axis("role").reset_index(name="n_components")

    lines = [
        "# E203 E176 Component Knockout Stress",
        "",
        "## Question",
        "",
        "If E176's public score is a sensor, which internal component must be alive for the sensor to matter, and which component mostly explains tail risk?",
        "",
        "## Result",
        "",
        "E176 has a necessary broad body, but its public fragility is concentrated in a much smaller critical-cell layer.",
        "",
        f"- Full E176 moved-cell focus delta is `{full['expected_delta_focus']:.12g}` in the E179 cell prior.",
        f"- S-only carries `{only_s['expected_focus_share']:.6f}` of that focus delta; Q2-only carries only `{only_q2['expected_focus_share']:.6f}`.",
        f"- Primary S-stage body S3/S1/S4 carries `{primary_s['expected_focus_share']:.6f}`.",
        f"- Between-train-runs rows carry `{between['expected_focus_share']:.6f}`; dropping them leaves only `{drop_between['expected_focus_share']:.6f}` of the body.",
        f"- Top33 swing cells carry `{top33['expected_focus_share']:.6f}` of the expected body but have visible support `{top33['support_visible_swing_weighted']:.6f}`.",
        f"- Dropping top33 still leaves `{drop_top33['expected_focus_share']:.6f}` of focus body, so top33 is a tail-resolution layer rather than the whole signal.",
        "",
        "Interpretation: if E176 wins, the result primarily validates a broad S-stage / between-train-runs body. If it ties or loses, the most plausible failure is not that the body is absent; it is that the compact hard-tail layer cancelled the body.",
        "",
        "## Component Knockouts",
        "",
        md_table(
            components,
            [
                "component",
                "role",
                "n_cells",
                "n_rows",
                "targets",
                "expected_focus_share",
                "drop_remaining_focus_share",
                "expected_visible_share",
                "swing_share",
                "top33_coverage",
                "top8_coverage",
                "cells_to_cover_e95_edge_focus",
                "support_visible_swing_weighted",
                "e72_active_rate",
                "between_train_runs_rate",
            ],
            n=40,
        ),
        "",
        "## Target Knockouts",
        "",
        md_table(
            targets,
            [
                "component",
                "role",
                "n_cells",
                "n_rows",
                "expected_focus_share",
                "drop_remaining_focus_share",
                "top33_coverage",
                "top8_coverage",
                "cells_to_cover_e95_edge_focus",
                "support_visible_swing_weighted",
                "e72_active_rate",
                "between_train_runs_rate",
            ],
            n=20,
        ),
        "",
        "## Role Counts",
        "",
        md_table(role_summary),
        "",
        "## Decision",
        "",
        "No submission is created. E203 strengthens the rule that E176 feedback must be read as a body-vs-tail observation. Post-E176 follow-up should only ask Q2 amplitude if E176 wins cleanly enough to first validate the broad S-stage body.",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cells = pd.read_csv(CELLS)
    components = build_components(cells)
    targets = build_target_table(cells)
    components.to_csv(OUT_COMPONENTS, index=False)
    targets.to_csv(OUT_TARGETS, index=False)
    write_report(components, targets)
    print(f"wrote {OUT_COMPONENTS}")
    print(f"wrote {OUT_TARGETS}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
