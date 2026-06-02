#!/usr/bin/env python3
"""H143: XOR branch assignment HS-JEPA.

H142 showed that co-activating row207 and row135 branches creates a route
barrier.  H143 turns that negative finding into a solver rule:

    choose row207 branch OR row135 branch, never both.

The full endpoints already exist:

- H139 = common core + full row207 branch
- H140 = common core + full row135 branch

H143 therefore ranks the XOR branch frontier but promotes the best novel
non-endpoint candidate.  If the novel softened row207 candidate beats H139
publicly, the row207 branch is real but over-amplified.  If H139 beats H143,
the full row207 endpoint remains the correct XOR assignment.
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
OUT = HITL / "h143_xor_branch_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h143", H139_PATH)
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
    for path in OUT.glob("submission_h143_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h143_xorbranch_*.csv"):
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


def known_hashes(sample: pd.DataFrame) -> set[str]:
    hashes: set[str] = set()
    for path in ROOT.glob("submission_h*_uploadsafe.csv"):
        try:
            prob = h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
            hashes.add(short_hash(prob))
        except Exception:
            continue
    return hashes


def xor_score(rec: dict[str, object]) -> float:
    h088 = float(rec["delta_h088_vs_h136"])
    margin = float(rec["delta_margin_vs_h136"])
    h098 = float(rec["delta_h098_vs_h136"])
    route = float(rec["delta_route_vs_h136"])
    gamma = float(rec["gamma"])
    return (
        16.0 * max(-h088, 0.0)
        + 34.0 * max(margin, 0.0)
        - 900.0 * max(h098, 0.0)
        - 650.0 * max(route, 0.0)
        + 0.0030 * (0.20 <= gamma <= 1.00)
        - 0.0010 * max(gamma - 1.00, 0.0)
    )


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, _model_scores, _props = h118mod.prepare_context()
    known = known_hashes(sample)

    paths = {
        "h136": ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv",
        "h139": ROOT / "submission_h139_roleatoms_bf2b3e77_uploadsafe.csv",
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

    branches = {
        "row207": moves["h139"] - moves["h141"],
        "row135": moves["h140"] - moves["h141"],
    }
    grid = [-0.25, 0.20, 0.35, 0.50, 0.65, 0.80, 1.00, 1.15, 1.30]
    rows = []
    materialized: dict[str, tuple[np.ndarray, pd.DataFrame]] = {}
    for branch_name, branch_move in branches.items():
        for gamma in grid:
            move = moves["h141"] + gamma * branch_move
            prob = h130mod.materialize(base_prob, move)
            hash_id = short_hash(prob)
            evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            changed = changed_cells(moves["h136"], move)
            axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
            rec = {
                "candidate_id": f"h143_{branch_name}_g{str(gamma).replace('.', 'p').replace('-', 'm')}_{hash_id}",
                "branch": branch_name,
                "gamma": float(gamma),
                "hash": hash_id,
                "known_endpoint_or_existing": bool(hash_id in known),
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
            rec["h143_xor_branch_pass"] = bool(
                rec["changed_cells_vs_h136"] <= 4
                and rec["delta_h088_vs_h136"] <= -0.00200
                and rec["delta_margin_vs_h136"] >= 0.00015
                and rec["delta_h098_vs_h136"] <= 0.00000175
                and rec["delta_route_vs_h136"] <= 0.00000280
                and 0.20 <= gamma <= 1.00
            )
            rec["h143_xor_branch_score"] = xor_score(rec)
            rows.append(rec)
            materialized[rec["candidate_id"]] = (prob, changed)

    scored = pd.DataFrame(rows).sort_values(
        [
            "known_endpoint_or_existing",
            "h143_xor_branch_pass",
            "h143_xor_branch_score",
            "delta_h098_vs_h136",
        ],
        ascending=[True, False, False, True],
    ).reset_index(drop=True)
    if scored.empty:
        raise RuntimeError("H143 produced no XOR candidates")

    selected = scored.iloc[0].to_dict()
    selected_prob, selected_cells = materialized[str(selected["candidate_id"])]
    hash_id = str(selected["hash"])
    local_path = OUT / f"submission_{selected['candidate_id']}.csv"
    root_path = ROOT / f"submission_h143_xorbranch_{hash_id}_uploadsafe.csv"
    h085mod.write_submission(sample, selected_prob, local_path)
    h085mod.write_submission(sample, selected_prob, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected.update(
        {
            "h143_local_path": str(local_path.resolve()),
            "h143_root_uploadsafe_path": str(root_path.resolve()),
            "h143_worldview": (
                "XOR branch assignment: activate one optional branch after the "
                "common core; promote best novel non-endpoint candidate"
            ),
            **{f"root_{key}": value for key, value in validation.items()},
        }
    )

    selected_cells.insert(0, "candidate_id", selected["candidate_id"])
    scored.to_csv(OUT / "h143_xor_branch_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h143_decision.csv", index=False)
    selected_cells.to_csv(OUT / "h143_selected_cells.csv", index=False)

    cols = [
        "candidate_id",
        "branch",
        "gamma",
        "known_endpoint_or_existing",
        "changed_cells_vs_h136",
        "delta_h088_vs_h136",
        "delta_margin_vs_h136",
        "delta_h098_vs_h136",
        "delta_route_vs_h136",
        "h143_xor_branch_pass",
        "h143_xor_branch_score",
    ]
    report = f"""# H143 XOR Branch Assignment HS-JEPA

Question: if H142's co-activation barrier is real, which optional branch should
the solver activate after the H141 common core?

Search space:

```text
H141 + gamma * row207_branch
H141 + gamma * row135_branch
```

Known endpoints are kept in the ranking but not promoted as a new root file.

Selected novel XOR candidate:

{md_table(pd.DataFrame([selected])[cols + ['h143_root_uploadsafe_path']], 1)}

Selected cells:

{md_table(selected_cells, 20)}

XOR frontier:

{md_table(scored[cols], 30)}

Interpretation:

The raw score still prefers the known H139 endpoint, but the best novel
non-endpoint is a softened row207 branch.  This makes H143 a direct amplitude
test:

```text
H139 = full row207 branch
H143 = softened row207 branch
H140 = row135 branch
H141 = no optional branch
```

Public sensor reading:

- H143 > H139: row207 is real but over-amplified; build calibrated XOR branch
  amplitudes.
- H139 > H143: full row207 is the correct XOR assignment.
- H140 > H143/H139: row135 is the correct branch.
- H141 > all optional branches: common core only.
"""
    (OUT / "h143_report.md").write_text(report, encoding="utf-8")

    print(f"H143 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(scored[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    run()
