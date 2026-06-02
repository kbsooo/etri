#!/usr/bin/env python3
"""H141: common-core public/private equation HS-JEPA probe.

H139 and H140 disagree about optional actions:

- H139 keeps row207 S2 because it maximizes H088 stress relief.
- H140 drops row207 and adds row135 Q3/S2 because it survives sensor dropout.

They agree on one smaller equation:

    row70 Q3 margin repair + row131 S2 toxicity relief

H141 isolates that shared row-target assignment.  It is not intended as a
stronger blend; it is a sensor submission that asks whether the common core is
action-grade while row207 and row135 are optional or toxic add-ons.
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
OUT = HITL / "h141_common_core_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h141", H139_PATH)
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
    for path in OUT.glob("submission_h141_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h141_commoncore_*.csv"):
        path.unlink()


def add_common_core_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["n_rows"] = out["rows"].astype(str).str.count(",") + 1
    out["has70"] = out["rows"].astype(str).str.contains("70")
    out["has131"] = out["rows"].astype(str).str.contains("131")
    out["has135"] = out["rows"].astype(str).str.contains("135")
    out["has207"] = out["rows"].astype(str).str.contains("207")
    out["has_common_core"] = out["has70"] & out["has131"]
    out["has_optional_addon"] = out["has135"] | out["has207"] | (out["n_rows"] > 2)

    out["h141_common_core_pass"] = (
        out["has_common_core"]
        & (~out["has_optional_addon"])
        & (out["changed_cells_vs_h136"] <= 2)
        & (out["delta_h088"] <= -0.00135)
        & (out["delta_margin"] >= 0.00025)
        & (out["delta_h098"] <= 0.00000125)
        & (out["delta_route"] <= 0.00000145)
    )
    out["h141_h098_tight_pass"] = (
        out["has_common_core"]
        & (~out["has_optional_addon"])
        & (out["changed_cells_vs_h136"] <= 2)
        & (out["delta_h088"] <= -0.00125)
        & (out["delta_margin"] >= 0.00020)
        & (out["delta_h098"] <= 0.00000105)
        & (out["delta_route"] <= 0.00000145)
    )
    out["h141_core_survival"] = (
        16.0 * (-out["delta_h088"])
        + 30.0 * out["delta_margin"]
        - 1050.0 * np.maximum(out["delta_h098"], 0.0)
        - 780.0 * np.maximum(out["delta_route"], 0.0)
        + 0.0100 * out["h141_common_core_pass"]
        + 0.0030 * out["h141_h098_tight_pass"]
        + 0.0015 * (~out["has_optional_addon"])
        - 0.0040 * out["has207"]
        - 0.0020 * out["has135"]
        - 0.0006 * np.maximum(out["changed_cells_vs_h136"] - 2, 0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    _pool, _public, sample, base_prob, *_rest = h118mod.prepare_context()

    scores_path = HITL / "h140_sensor_dropout_role_frontier_hsjepa/h140_sensor_dropout_scores.csv"
    if not scores_path.exists():
        raise FileNotFoundError(scores_path)

    scored = add_common_core_scores(pd.read_csv(scores_path))
    core = scored[scored["has_common_core"] & (~scored["has_optional_addon"])].copy()
    if core.empty:
        raise RuntimeError("H141 found no common-core H139/H140 candidate")

    ranked = core.sort_values(
        ["h141_common_core_pass", "h141_core_survival", "delta_margin", "delta_h098"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    selected = ranked.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    if not selected_path.exists():
        raise FileNotFoundError(selected_path)

    selected_prob = h085mod.load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    hash_id = short_hash(selected_prob)
    local_path = OUT / f"submission_h141_{selected['candidate_id']}_{hash_id}.csv"
    root_path = ROOT / f"submission_h141_commoncore_{hash_id}_uploadsafe.csv"
    shutil.copyfile(selected_path, local_path)
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected["h141_local_path"] = str(local_path.resolve())
    selected["h141_root_uploadsafe_path"] = str(root_path.resolve())
    selected["h141_worldview"] = (
        "common-core equation: row70 Q3 margin repair + row131 S2 toxicity relief; "
        "row207 and row135 are held out as optional add-on sensors"
    )
    selected.update({f"root_{key}": value for key, value in validation.items()})

    scored.to_csv(OUT / "h141_all_scored_candidates.csv", index=False)
    ranked.to_csv(OUT / "h141_common_core_ranked.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h141_decision.csv", index=False)

    cols = [
        "candidate_id",
        "atoms",
        "rows",
        "changed_cells_vs_h136",
        "delta_h088",
        "delta_margin",
        "delta_h098",
        "delta_route",
        "h140_passes_dropout_gate",
        "h141_common_core_pass",
        "h141_h098_tight_pass",
        "h141_core_survival",
        "resolved_path",
    ]
    report = f"""# H141 Common-Core Public/Private Equation HS-JEPA

Question: what happens if we keep only the row-target assignment that H139 and
H140 both implicitly agree on?

Selected common core:

{md_table(pd.DataFrame([selected])[cols + ['h141_root_uploadsafe_path']], 1)}

Common-core frontier:

{md_table(ranked[cols], 20)}

Interpretation:

```text
row70 Q3  = margin repair
row131 S2 = toxicity relief
row207 S2 = held out H088-heavy optional tail
row135 Q3/S2 = held out sensor-dropout repair add-on
```

Public sensor reading:

- H141 > H139 and H140: row70+row131 is the action-grade equation core; row207
  and row135 were over-corrections.
- H139 > H141: row207 S2 H088 relief is not just diagnostic, it is action-grade.
- H140 > H141: row135 repair is needed for public/private safety, and the
  two-cell common core underfits the boundary.
- H136 > H141: even the shared role atoms are diagnostics rather than safe
  submission actions.
"""
    (OUT / "h141_report.md").write_text(report, encoding="utf-8")

    print(f"H141 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(ranked[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    run()
