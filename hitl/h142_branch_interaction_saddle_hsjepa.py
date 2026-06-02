#!/usr/bin/env python3
"""H142: branch-interaction saddle equation HS-JEPA.

H139, H140, and H141 define a small action algebra:

    H141 = common core
    H139 = common core + row207 H088-heavy branch
    H140 = common core + row135 repair branch

H142 asks whether the true public/private equation is neither endpoint.  During
the first grid pass, any nonzero co-activation of the two optional branches
created a large route cost.  H142 therefore promotes a balanced co-activation
barrier probe: if public still likes it, the route diagnostic is hallucinating;
if public punishes it, the solver should treat row207 and row135 as XOR-style
branches rather than additive actions.
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
OUT = HITL / "h142_branch_interaction_saddle_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H139_PATH = HITL / "h139_role_atom_assignment_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h139mod_h142", H139_PATH)
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
    for path in OUT.glob("submission_h142_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h142_branchsaddle_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h142_branchbarrier_*.csv"):
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


def branch_score(rec: dict[str, object]) -> float:
    h088 = float(rec["delta_h088_vs_h136"])
    margin = float(rec["delta_margin_vs_h136"])
    h098 = float(rec["delta_h098_vs_h136"])
    route = float(rec["delta_route_vs_h136"])
    alpha = float(rec["alpha_row207"])
    beta = float(rec["beta_row135"])
    interior = 0.30 <= alpha <= 0.90 and 0.30 <= beta <= 0.90
    return (
        15.0 * max(-h088, 0.0)
        + 36.0 * max(margin, 0.0)
        - 900.0 * max(h098, 0.0)
        - 620.0 * max(route, 0.0)
        + 0.0060 * bool(rec["h142_branch_saddle_pass"])
        + 0.0025 * interior
        - 0.0007 * abs(alpha - beta)
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
    core = moves["h141"]
    branch207 = moves["h139"] - core
    branch135 = moves["h140"] - core

    grid = [0.0, 0.20, 0.35, 0.50, 0.65, 0.80, 1.00, 1.15]
    rows = []
    materialized: list[tuple[dict[str, object], np.ndarray, np.ndarray, pd.DataFrame]] = []
    seen: set[str] = set()
    h136_eval = evals["h136"]
    h141_eval = evals["h141"]
    for alpha in grid:
        for beta in grid:
            if alpha == 0.0 and beta == 0.0:
                continue
            if alpha == 0.0 or beta == 0.0:
                continue
            move = core + alpha * branch207 + beta * branch135
            prob = h130mod.materialize(base_prob, move)
            hash_id = short_hash(prob)
            if hash_id in seen:
                continue
            seen.add(hash_id)
            evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            changed = changed_cells(moves["h136"], move)
            axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
            rec = {
                "candidate_id": f"h142_a{str(alpha).replace('.', 'p')}_b{str(beta).replace('.', 'p')}_{hash_id}",
                "alpha_row207": float(alpha),
                "beta_row135": float(beta),
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
            rec["h142_branch_saddle_pass"] = bool(
                0.20 < alpha < 1.05
                and 0.20 < beta < 1.05
                and rec["delta_h088_vs_h136"] <= -0.00185
                and rec["delta_margin_vs_h136"] >= 0.00030
                and rec["delta_h098_vs_h136"] <= 0.00000195
                and rec["delta_route_vs_h136"] <= 0.00000295
                and rec["changed_cells_vs_h136"] <= 5
            )
            rec["h142_coactivation_route_barrier"] = bool(
                0.20 <= alpha <= 0.80
                and 0.20 <= beta <= 0.80
                and rec["delta_route_vs_h136"] >= 0.00000350
            )
            rec["h142_balanced_barrier_probe_pass"] = bool(
                abs(alpha - beta) <= 0.05
                and 0.35 <= alpha <= 0.65
                and 0.35 <= beta <= 0.65
                and rec["delta_h088_vs_h136"] <= -0.00195
                and rec["delta_margin_vs_h136"] >= 0.00035
                and rec["delta_h098_vs_h136"] <= 0.00000185
                and rec["delta_route_vs_h136"] <= 0.00000375
                and rec["changed_cells_vs_h136"] <= 5
            )
            rec["h142_branch_saddle_score"] = branch_score(rec)
            rows.append(rec)
            materialized.append((rec, prob, move, changed))

    scored = pd.DataFrame(rows).sort_values(
        [
            "h142_branch_saddle_pass",
            "h142_balanced_barrier_probe_pass",
            "h142_branch_saddle_score",
            "delta_h098_vs_h136",
        ],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    if scored.empty:
        raise RuntimeError("H142 produced no branch interaction candidates")
    selected = scored.iloc[0].to_dict()
    selected_tuple = next(item for item in materialized if item[0]["candidate_id"] == selected["candidate_id"])
    selected_rec, selected_prob, _selected_move, selected_cells = selected_tuple
    hash_id = str(selected["candidate_id"]).split("_")[-1]
    local_path = OUT / f"submission_{selected['candidate_id']}.csv"
    root_prefix = "branchsaddle" if bool(selected["h142_branch_saddle_pass"]) else "branchbarrier"
    root_path = ROOT / f"submission_h142_{root_prefix}_{hash_id}_uploadsafe.csv"
    h085mod.write_submission(sample, selected_prob, local_path)
    shutil.copyfile(local_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    selected.update(
        {
            "h142_local_path": str(local_path.resolve()),
            "h142_root_uploadsafe_path": str(root_path.resolve()),
                "h142_worldview": (
                "balanced co-activation route-barrier probe: common core plus partial "
                "row207 toxicity relief and partial row135 margin repair"
            ),
            **{f"root_{key}": value for key, value in validation.items()},
        }
    )

    eval_summary = []
    for key, evald in evals.items():
        eval_summary.append({"source": key, **{metric: float(value) for metric, value in evald.items()}})

    scored.to_csv(OUT / "h142_branch_grid_scores.csv", index=False)
    pd.DataFrame([selected]).to_csv(OUT / "h142_decision.csv", index=False)
    selected_cells.insert(0, "candidate_id", selected["candidate_id"])
    selected_cells.to_csv(OUT / "h142_selected_cells.csv", index=False)
    pd.DataFrame(eval_summary).to_csv(OUT / "h142_source_evaluations.csv", index=False)

    cols = [
        "candidate_id",
        "alpha_row207",
        "beta_row135",
        "changed_cells_vs_h136",
        "delta_h088_vs_h136",
        "delta_margin_vs_h136",
        "delta_h098_vs_h136",
        "delta_route_vs_h136",
        "delta_h088_vs_h141",
        "delta_margin_vs_h141",
        "h142_branch_saddle_pass",
        "h142_balanced_barrier_probe_pass",
        "h142_coactivation_route_barrier",
        "h142_branch_saddle_score",
    ]
    report = f"""# H142 Branch-Interaction Saddle HS-JEPA

Question: are H139 and H140 endpoints of a 2D public/private equation, or does
co-activation of their optional branches trigger a route-toxicity barrier?

Source decomposition:

```text
H141 = common core
H139 = H141 + row207 H088-heavy branch
H140 = H141 + row135 repair branch
H142 = H141 + alpha * row207_branch + beta * row135_branch
```

Selected candidate:

{md_table(pd.DataFrame([selected])[cols + ['h142_root_uploadsafe_path']], 1)}

Selected cells:

{md_table(selected_cells, 20)}

Top branch grid:

{md_table(scored[cols], 30)}

Interpretation:

The grid did not find a clean route-safe saddle.  Even small co-activation of
row207 and row135 creates a route-cost jump.  H142 therefore becomes a
co-activation barrier probe, not a safe endpoint candidate.

```text
if H142 is good: the local route barrier is false and additive branch equations
                 can unlock a larger hidden state.
if H142 is bad:  row207 and row135 are XOR-style branches; do not add them.
```

Public sensor reading:

- H142 > H139/H140/H141: route toxicity is a false local diagnostic and
  additive branch equations should be expanded.
- H139 > H142: row207 should be stronger and row135 is unnecessary.
- H140 > H142: row135 should be stronger and row207 remains diagnostic.
- H141 > H142: optional branches are over-corrections; keep common core only.
"""
    (OUT / "h142_report.md").write_text(report, encoding="utf-8")

    print(f"H142 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(scored[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    run()
