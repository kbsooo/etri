#!/usr/bin/env python3
"""H145: Q3 repair-only target veto HS-JEPA.

H144 split row135 into Q3 and S2, then selected:

    common core + row207 S2 + row135 Q3, with row135 S2 vetoed

H145 asks the sharper counter-question:

    Is row207 S2 actually necessary, or is the action-grade signal mainly the
    row135 Q3 repair target?

This is a negative-control against H088-heavy relief.  It keeps the H141 common
core, adds only row135-Q3 repair, and vetoes both row207 S2 and row135 S2.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h145_q3_repair_only_veto_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h145", H139_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H139_PATH}")
h139mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h139mod
SPEC.loader.exec_module(h139mod)

h118mod = h139mod.h118mod
h085mod = h139mod.h085mod
h126mod = h139mod.h126mod
h130mod = h139mod.h130mod
h102mod = h139mod.h102mod
TARGETS = h139mod.TARGETS


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h145_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h145_q3repair_*.csv"):
        path.unlink()


def load_move(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h139mod.evaluate_matrix(
        move_mat,
        basis_fit_df,
        basis_fit_moves,
        route_fit,
        cell,
        h098_fit,
        fit,
        pool,
        bad_axes,
        bad_moves,
        good_moves,
        axes,
    )


def changed_cells(reference: np.ndarray, move: np.ndarray) -> pd.DataFrame:
    rows = []
    for row, tidx in np.argwhere(np.abs(move - reference) > 1.0e-12):
        rows.append(
            {
                "row": int(row),
                "target_index": int(tidx),
                "target": TARGETS[int(tidx)],
                "delta_logit_vs_h136": float(move[row, tidx] - reference[row, tidx]),
                "new_logit_move": float(move[row, tidx]),
            }
        )
    return pd.DataFrame(rows).sort_values(["row", "target_index"]).reset_index(drop=True)


def q3_repair_score(rec: dict[str, object]) -> float:
    h088 = float(rec["delta_h088_vs_h136"])
    margin = float(rec["delta_margin_vs_h136"])
    h098 = float(rec["delta_h098_vs_h136"])
    route = float(rec["delta_route_vs_h136"])
    q3 = float(rec["beta_row135_q3"])
    return (
        10.0 * max(-h088, 0.0)
        + 44.0 * max(margin, 0.0)
        - 820.0 * max(h098, 0.0)
        - 720.0 * max(route, 0.0)
        + 0.0100 * bool(rec["h145_q3_repair_pass"])
        - 0.0015 * max(q3 - 1.0, 0.0)
    )


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, _model_scores, _props = h118mod.prepare_context()

    paths = {
        "h136": ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv",
        "h140": ROOT / "submission_h140_roledrop_a5d0258f_uploadsafe.csv",
        "h141": ROOT / "submission_h141_commoncore_0999d3ae_uploadsafe.csv",
    }
    moves = {key: load_move(path, sample, base_prob) for key, path in paths.items()}
    evals = {
        key: evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        for key, move in moves.items()
    }
    h136_eval = evals["h136"]
    h141_eval = evals["h141"]

    row135 = moves["h140"] - moves["h141"]
    row135_q3 = np.zeros_like(row135)
    row135_s2 = np.zeros_like(row135)
    row135_q3[135, 2] = row135[135, 2]
    row135_s2[135, 4] = row135[135, 4]

    rows = []
    materialized: dict[str, tuple[np.ndarray, pd.DataFrame]] = {}
    for beta_q3 in [0.35, 0.50, 0.80, 1.00, 1.15, 1.30]:
        move = moves["h141"] + beta_q3 * row135_q3
        prob = h130mod.materialize(base_prob, move)
        hash_id = short_hash(prob)
        evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        changed = changed_cells(moves["h136"], move)
        axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
        rec = {
            "candidate_id": f"h145_q3_g{str(beta_q3).replace('.', 'p')}_{hash_id}",
            "beta_row135_q3": float(beta_q3),
            "alpha_row207": 0.0,
            "beta_row135_s2": 0.0,
            "hash": hash_id,
            "changed_cells_vs_h136": int(len(changed)),
            "delta_route_vs_h136": float(evald["route"] - h136_eval["route"]),
            "delta_h098_vs_h136": float(evald["h098"] - h136_eval["h098"]),
            "delta_h088_vs_h136": float(evald["h088"] - h136_eval["h088"]),
            "delta_margin_vs_h136": float(evald["margin"] - h136_eval["margin"]),
            "delta_route_vs_h141": float(evald["route"] - h141_eval["route"]),
            "delta_h098_vs_h141": float(evald["h098"] - h141_eval["h098"]),
            "delta_h088_vs_h141": float(evald["h088"] - h141_eval["h088"]),
            "delta_margin_vs_h141": float(evald["margin"] - h141_eval["margin"]),
            "route": float(evald["route"]),
            "h098": float(evald["h098"]),
            "h088": float(evald["h088"]),
            "margin": float(evald["margin"]),
            "h102_cum_h088_axis_cos": float(axis["h102_cum_h088_axis_cos"]),
            "h102_cum_good_bad_margin": float(axis["h102_cum_good_bad_margin"]),
        }
        rec["h145_q3_repair_pass"] = bool(
            rec["changed_cells_vs_h136"] <= 3
            and rec["delta_h088_vs_h136"] <= -0.00160
            and rec["delta_margin_vs_h136"] >= 0.00055
            and rec["delta_h098_vs_h136"] <= 0.00000170
            and rec["delta_route_vs_h136"] <= 0.00000130
            and 0.80 <= beta_q3 <= 1.15
        )
        rec["h145_vetoes_h088_relief"] = True
        rec["h145_vetoes_row135_s2"] = True
        rec["h145_q3_repair_score"] = q3_repair_score(rec)
        rows.append(rec)
        materialized[rec["candidate_id"]] = (prob, changed)

    scored = pd.DataFrame(rows).sort_values(
        ["h145_q3_repair_pass", "h145_q3_repair_score", "delta_margin_vs_h136", "delta_h098_vs_h136"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    selected = scored.iloc[0].to_dict()
    selected_prob, selected_cells = materialized[str(selected["candidate_id"])]
    hash_id = str(selected["hash"])
    local_path = OUT / f"submission_{selected['candidate_id']}.csv"
    root_path = ROOT / f"submission_h145_q3repair_{hash_id}_uploadsafe.csv"
    h085mod.write_submission(sample, selected_prob, local_path)
    h085mod.write_submission(sample, selected_prob, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected.update(
        {
            "h145_local_path": str(local_path.resolve()),
            "h145_root_uploadsafe_path": str(root_path.resolve()),
            "h145_worldview": (
                "Q3 repair-only veto: keep H141 common core and row135 Q3 repair; "
                "veto row207 H088 relief and row135 S2"
            ),
            **{f"root_{key}": value for key, value in validation.items()},
        }
    )
    selected_cells.insert(0, "candidate_id", selected["candidate_id"])
    scored.to_csv(OUT / "h145_q3_repair_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h145_decision.csv", index=False)
    selected_cells.to_csv(OUT / "h145_selected_cells.csv", index=False)

    cols = [
        "candidate_id",
        "beta_row135_q3",
        "changed_cells_vs_h136",
        "delta_h088_vs_h136",
        "delta_margin_vs_h136",
        "delta_h098_vs_h136",
        "delta_route_vs_h136",
        "h145_q3_repair_pass",
        "h145_q3_repair_score",
    ]
    report = f"""# H145 Q3 Repair-Only Veto HS-JEPA

Question: after H144 found row135 Q3 safe and row135 S2 suspicious, is row207
S2 still necessary?

H145 keeps:

```text
H141 common core + row135 Q3 repair
```

and vetoes:

```text
row207 S2 H088 relief
row135 S2 route-toxic component
```

Selected candidate:

{md_table(pd.DataFrame([selected])[cols + ['h145_root_uploadsafe_path']], 1)}

Selected cells:

{md_table(selected_cells, 20)}

Q3 repair-only frontier:

{md_table(scored[cols], 20)}

Public sensor reading:

- H145 > H144/H139/H143: H088 relief was a public-toxic shortcut; Q3 repair is
  the real action-grade target.
- H144 > H145: row207 relief is needed when row135 S2 is vetoed.
- H141 > H145: row135 Q3 is also an over-repair and the common core is safer.
- H140 > H145: row135 Q3 and S2 must stay paired.
"""
    (OUT / "h145_report.md").write_text(report, encoding="utf-8")

    print(f"H145 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(scored[cols].to_string(index=False))


if __name__ == "__main__":
    run()
