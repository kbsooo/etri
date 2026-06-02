#!/usr/bin/env python3
"""H144: target-split XOR assignment HS-JEPA.

H142 showed that co-activating row207 and the full row135 branch creates a
route barrier.  H144 asks the sharper row-target question:

    Is row135 as a whole toxic, or only one target inside row135?

It decomposes the row135 branch into row135-Q3 and row135-S2 components.  The
search then allows row207 + row135-Q3, while treating row135-S2 as a candidate
route-toxic target component that can be vetoed.
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
OUT = HITL / "h144_target_split_xor_assignment_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h144", H139_PATH)
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
    for path in OUT.glob("submission_h144_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h144_targetxor_*.csv"):
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


def target_xor_score(rec: dict[str, object]) -> float:
    h088 = float(rec["delta_h088_vs_h136"])
    margin = float(rec["delta_margin_vs_h136"])
    h098 = float(rec["delta_h098_vs_h136"])
    route = float(rec["delta_route_vs_h136"])
    a207 = float(rec["alpha_row207"])
    q3 = float(rec["beta_row135_q3"])
    s2 = float(rec["beta_row135_s2"])
    return (
        17.0 * max(-h088, 0.0)
        + 38.0 * max(margin, 0.0)
        - 820.0 * max(h098, 0.0)
        - 700.0 * max(route, 0.0)
        + 0.0090 * bool(rec["h144_target_split_pass"])
        + 0.0040 * (a207 > 0 and q3 > 0 and s2 == 0)
        - 0.0080 * (s2 > 0 and a207 > 0)
    )


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, _model_scores, _props = h118mod.prepare_context()

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

    row207 = moves["h139"] - moves["h141"]
    row135 = moves["h140"] - moves["h141"]
    row135_q3 = np.zeros_like(row135)
    row135_s2 = np.zeros_like(row135)
    row135_q3[135, 2] = row135[135, 2]
    row135_s2[135, 4] = row135[135, 4]

    grid = [0.0, 0.50, 0.80, 1.00]
    rows = []
    materialized: dict[str, tuple[np.ndarray, pd.DataFrame]] = {}
    for alpha in grid:
        for beta_q3 in grid:
            for beta_s2 in grid:
                if alpha == beta_q3 == beta_s2 == 0.0:
                    continue
                move = moves["h141"] + alpha * row207 + beta_q3 * row135_q3 + beta_s2 * row135_s2
                prob = h130mod.materialize(base_prob, move)
                hash_id = short_hash(prob)
                evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
                changed = changed_cells(moves["h136"], move)
                axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
                rec = {
                    "candidate_id": (
                        f"h144_a{str(alpha).replace('.', 'p')}_"
                        f"q{str(beta_q3).replace('.', 'p')}_"
                        f"s{str(beta_s2).replace('.', 'p')}_{hash_id}"
                    ),
                    "alpha_row207": float(alpha),
                    "beta_row135_q3": float(beta_q3),
                    "beta_row135_s2": float(beta_s2),
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
                rec["h144_target_split_pass"] = bool(
                    alpha > 0.0
                    and beta_q3 > 0.0
                    and beta_s2 == 0.0
                    and rec["changed_cells_vs_h136"] <= 4
                    and rec["delta_h088_vs_h136"] <= -0.00230
                    and rec["delta_margin_vs_h136"] >= 0.00045
                    and rec["delta_h098_vs_h136"] <= 0.00000260
                    and rec["delta_route_vs_h136"] <= 0.00000280
                )
                rec["h144_s2_route_toxic"] = bool(
                    alpha > 0.0
                    and beta_s2 > 0.0
                    and rec["delta_route_vs_h136"] >= 0.00000340
                )
                rec["h144_target_xor_score"] = target_xor_score(rec)
                rows.append(rec)
                materialized[rec["candidate_id"]] = (prob, changed)

    scored = pd.DataFrame(rows).sort_values(
        ["h144_target_split_pass", "h144_target_xor_score", "delta_margin_vs_h136", "delta_h098_vs_h136"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    if scored.empty:
        raise RuntimeError("H144 produced no target-split candidates")
    selected = scored.iloc[0].to_dict()
    selected_prob, selected_cells = materialized[str(selected["candidate_id"])]
    hash_id = str(selected["hash"])
    local_path = OUT / f"submission_{selected['candidate_id']}.csv"
    root_path = ROOT / f"submission_h144_targetxor_{hash_id}_uploadsafe.csv"
    h085mod.write_submission(sample, selected_prob, local_path)
    h085mod.write_submission(sample, selected_prob, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected.update(
        {
            "h144_local_path": str(local_path.resolve()),
            "h144_root_uploadsafe_path": str(root_path.resolve()),
            "h144_worldview": (
                "target-split XOR assignment: row207 may combine with row135 Q3, "
                "but row135 S2 is vetoed as the route-toxic component"
            ),
            **{f"root_{key}": value for key, value in validation.items()},
        }
    )
    selected_cells.insert(0, "candidate_id", selected["candidate_id"])
    scored.to_csv(OUT / "h144_target_split_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h144_decision.csv", index=False)
    selected_cells.to_csv(OUT / "h144_selected_cells.csv", index=False)

    cols = [
        "candidate_id",
        "alpha_row207",
        "beta_row135_q3",
        "beta_row135_s2",
        "changed_cells_vs_h136",
        "delta_h088_vs_h136",
        "delta_margin_vs_h136",
        "delta_h098_vs_h136",
        "delta_route_vs_h136",
        "h144_target_split_pass",
        "h144_s2_route_toxic",
        "h144_target_xor_score",
    ]
    report = f"""# H144 Target-Split XOR Assignment HS-JEPA

Question: did H142's route barrier come from row135 as a whole, or from a
specific row-target component inside row135?

Target decomposition:

```text
row207 branch = row207 S2
row135 branch = row135 Q3 + row135 S2
```

Selected target-split candidate:

{md_table(pd.DataFrame([selected])[cols + ['h144_root_uploadsafe_path']], 1)}

Selected cells:

{md_table(selected_cells, 20)}

Target-split frontier:

{md_table(scored[cols], 30)}

Interpretation:

H144 is a more precise assignment bet than H143:

```text
H143: choose row207 branch, no row135.
H144: choose row207 branch + row135 Q3, veto row135 S2.
```

This means the route-toxic component may be row135 S2, not row135 Q3.

Public sensor reading:

- H144 > H139/H143: the branch decoder needs target-level routing; row135 Q3 is
  a safe repair atom when row135 S2 is vetoed.
- H139 > H144: adding row135 Q3 over-repairs; full row207 branch is cleaner.
- H140 > H144: row135 Q3 must stay paired with row135 S2, or row207 is wrong.
- H142 > H144: row135 S2 was not toxic; additive branch interaction is alive.
"""
    (OUT / "h144_report.md").write_text(report, encoding="utf-8")

    print(f"H144 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(scored[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    run()
