#!/usr/bin/env python3
"""H140: sensor-dropout role frontier HS-JEPA selector.

H139 selected the strongest H088-relief triad.  That is useful, but H088 is a
stress diagnostic, not an action head.  H140 asks the opposite question:

    Which H139 role assignment survives when the H088 sensor is partially
    dropped out and the solver prioritizes margin, H098 safety, route safety,
    simplicity, and row207 ablation?

The selected candidate is a public/private equation bet, not a blend.  It
chooses a different role frontier from the H139 candidate set.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h140_sensor_dropout_role_frontier_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h140", H139_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H139_PATH}")
h139mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h139mod
SPEC.loader.exec_module(h139mod)

h118mod = h139mod.h118mod
h085mod = h139mod.h085mod
TARGETS = h139mod.TARGETS


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h140_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h140_roledrop_*.csv"):
        path.unlink()


def add_view_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["n_rows"] = out["rows"].astype(str).str.count(",") + 1
    out["has207"] = out["rows"].astype(str).str.contains("207")
    out["has131"] = out["rows"].astype(str).str.contains("131")
    out["has135"] = out["rows"].astype(str).str.contains("135")
    out["has70"] = out["rows"].astype(str).str.contains("70")

    out["view_h088_stress"] = (
        12.0 * (-out["delta_h088"])
        + 22.0 * out["delta_margin"]
        - 800.0 * np.maximum(out["delta_h098"], 0.0)
        - 500.0 * np.maximum(out["delta_route"], 0.0)
    )
    out["view_no_h088"] = (
        32.0 * out["delta_margin"]
        - 1300.0 * np.maximum(out["delta_h098"], 0.0)
        - 850.0 * np.maximum(out["delta_route"], 0.0)
        - 0.0010 * np.maximum(out["changed_cells_vs_h136"] - 2, 0)
    )
    out["view_h098_tight"] = (
        10.0 * (-out["delta_h088"])
        + 20.0 * out["delta_margin"]
        - 2200.0 * np.maximum(out["delta_h098"] - 0.0000008, 0.0)
        - 900.0 * np.maximum(out["delta_route"], 0.0)
        - 0.0007 * np.maximum(out["changed_cells_vs_h136"] - 2, 0)
    )
    out["view_route_tight"] = (
        10.0 * (-out["delta_h088"])
        + 22.0 * out["delta_margin"]
        - 1400.0 * np.maximum(out["delta_route"] - 0.0000015, 0.0)
        - 1000.0 * np.maximum(out["delta_h098"], 0.0)
        - 0.0005 * np.maximum(out["changed_cells_vs_h136"] - 2, 0)
    )
    out["view_simplicity_dropout"] = (
        8.0 * (-out["delta_h088"])
        + 24.0 * out["delta_margin"]
        - 900.0 * np.maximum(out["delta_h098"], 0.0)
        - 650.0 * np.maximum(out["delta_route"], 0.0)
        + 0.0015 * (~out["has207"])
        + 0.0008 * (out["changed_cells_vs_h136"] <= 2)
        - 0.0010 * out["has135"]
    )
    views = [
        "view_h088_stress",
        "view_no_h088",
        "view_h098_tight",
        "view_route_tight",
        "view_simplicity_dropout",
    ]
    for view in views:
        out[f"{view}_rank"] = out[view].rank(ascending=False, method="min")
    rank_cols = [f"{view}_rank" for view in views]
    out["mean_view_rank"] = out[rank_cols].mean(axis=1)
    out["max_view_rank"] = out[rank_cols].max(axis=1)
    out["h140_sensor_dropout_survival"] = (
        (31.0 - out["mean_view_rank"])
        + 0.25 * (31.0 - out["max_view_rank"])
        + 1000.0 * np.maximum(out["delta_margin"], 0.0)
        - 400.0 * np.maximum(out["delta_h098"] - 0.0000015, 0.0)
        + 0.40 * (out["changed_cells_vs_h136"] <= 2)
        + 0.20 * (~out["has207"])
    )
    out["h140_passes_dropout_gate"] = (
        (out["delta_margin"] >= 0.00025)
        & (out["delta_h088"] <= -0.00125)
        & (out["delta_h098"] <= 0.00000180)
        & (out["delta_route"] <= 0.00000270)
        & (~out["has207"])
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    _pool, _public, sample, base_prob, *_rest = h118mod.prepare_context()
    candidates_path = HITL / "h139_role_atom_assignment_equation_hsjepa/h139_candidates.csv"
    if not candidates_path.exists():
        raise FileNotFoundError(candidates_path)
    candidates = pd.read_csv(candidates_path)
    scored = add_view_scores(candidates)
    scored = scored.sort_values(
        ["h140_passes_dropout_gate", "h140_sensor_dropout_survival", "mean_view_rank"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    selected = scored.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    if not selected_path.exists():
        raise FileNotFoundError(selected_path)
    selected_prob = h085mod.load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    hash_id = short_hash(selected_prob)

    local_path = OUT / f"submission_h140_{selected['candidate_id']}_{hash_id}.csv"
    root_path = ROOT / f"submission_h140_roledrop_{hash_id}_uploadsafe.csv"
    shutil.copyfile(selected_path, local_path)
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected["h140_local_path"] = str(local_path.resolve())
    selected["h140_root_uploadsafe_path"] = str(root_path.resolve())
    selected["h140_worldview"] = (
        "sensor-dropout role frontier: H088-heavy row207 tail is ablated; "
        "surviving assignment uses margin/H098/route robust roles"
    )
    selected.update({f"root_{key}": value for key, value in validation.items()})

    scored.to_csv(OUT / "h140_sensor_dropout_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h140_decision.csv", index=False)

    view_cols = [
        "candidate_id",
        "atoms",
        "rows",
        "changed_cells_vs_h136",
        "delta_h088",
        "delta_margin",
        "delta_h098",
        "delta_route",
        "has207",
        "h140_passes_dropout_gate",
        "h140_sensor_dropout_survival",
        "mean_view_rank",
        "max_view_rank",
        "view_h088_stress",
        "view_no_h088",
        "view_h098_tight",
        "view_route_tight",
        "view_simplicity_dropout",
    ]
    report = f"""# H140 Sensor-Dropout Role Frontier HS-JEPA

Question: is H139's row207-heavy H088 relief action-grade, or did it over-select
the H088 stress diagnostic?

H140 deliberately re-ranks H139 candidates under sensor-dropout views:

- H088-heavy stress view
- no-H088 margin/H098 view
- H098-tight view
- route-tight view
- simplicity / row207 dropout view

Selected candidate:

{md_table(pd.DataFrame([selected])[view_cols + ['h140_root_uploadsafe_path']], 1)}

Top frontier:

{md_table(scored[view_cols], 30)}

Interpretation:

H140 selects a row207-ablated frontier:

```text
row131 S2 = toxicity relief
row70 Q3 = margin repair
row135 Q3/S2 = additional repair
row207 S2 = deliberately dropped out
```

Public interpretation:

- H140 > H139: H139 over-selected H088/row207; robust public/private safety is
  better captured by margin/H098/route survival.
- H139 > H140: row207 H088 relief is real action-grade signal.
- H136 > both: role atoms remain diagnostics, not submission actions.
"""
    (OUT / "h140_report.md").write_text(report, encoding="utf-8")
    print(f"H140 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(scored[view_cols].head(20).to_string(index=False))


if __name__ == "__main__":
    run()
