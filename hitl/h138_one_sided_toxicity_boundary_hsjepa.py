#!/usr/bin/env python3
"""H138: one-sided toxicity boundary HS-JEPA solver.

H137 showed that H135's completion tail is not a globally reversible vector.
Some counterfield moves improve the H088 stress diagnostic, but H088 alone is
not an action-grade decoder because aggressive moves can spend route/H098 and
margin budget.

H138 asks a sharper question:

    Can a small H088-relief action become public/private safe when paired with
    a separate margin-repair action?

This treats the HS-JEPA decoder as a row-target assignment/equation solver:
row207 S2 is a toxicity-relief field, while row135 Q3/S2 is tested as a
boundary repair field.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h138_one_sided_toxicity_boundary_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H137_PATH = HITL / "h137_tail_toxicity_counterfield_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h137mod_h138", H137_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H137_PATH}")
h137mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h137mod
SPEC.loader.exec_module(h137mod)

h136mod = h137mod.h136mod
h130mod = h137mod.h130mod
h126mod = h137mod.h126mod
h102mod = h137mod.h102mod
h085mod = h137mod.h085mod
h118mod = h137mod.h118mod

TARGETS = h137mod.TARGETS
TOL = h137mod.TOL


@dataclass(frozen=True)
class ActionRef:
    name: str
    role: str
    path: Path
    worldview: str


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    actions: tuple[str, ...]
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h138_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h138_boundary_*.csv"):
        path.unlink()


def load_move(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h136mod.evaluate_matrix(
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


def changed_cells(base_move: np.ndarray, move: np.ndarray) -> pd.DataFrame:
    rows = []
    for row, tidx in np.argwhere(np.abs(move - base_move) > 1.0e-12):
        rows.append(
            {
                "row": int(row),
                "target_index": int(tidx),
                "target": TARGETS[int(tidx)],
                "delta_logit_vs_h136": float(move[row, tidx] - base_move[row, tidx]),
                "new_logit_move": float(move[row, tidx]),
            }
        )
    return pd.DataFrame(rows).sort_values(["row", "target_index"]).reset_index(drop=True)


def action_score(row: dict[str, object]) -> float:
    d_route = float(row["delta_route"])
    d_h098 = float(row["delta_h098"])
    d_h088 = float(row["delta_h088"])
    d_margin = float(row["delta_margin"])
    h088_relief = max(-d_h088, 0.0)
    margin_gain = max(d_margin, 0.0)
    margin_loss = max(-d_margin, 0.0)
    stress_only_ratio = h088_relief / (abs(d_margin) + abs(d_route) + abs(d_h098) + 1.0e-9)
    stress_only_penalty = 0.00035 if d_margin < 0.0 and stress_only_ratio > 4.0 else 0.0
    return (
        7.5 * h088_relief
        + 18.0 * margin_gain
        - 30.0 * margin_loss
        - 650.0 * max(d_h098, 0.0)
        - 420.0 * max(d_route, 0.0)
        - 10.0 * stress_only_penalty
    )


def candidate_score(row: dict[str, object]) -> float:
    score = action_score(row)
    if float(row["delta_margin"]) >= 0.0 and float(row["delta_h088"]) <= -0.00050:
        score += 0.0030
    if float(row["delta_h098"]) <= 0.00000160:
        score += 0.0007
    if float(row["delta_route"]) <= 0.00000300:
        score += 0.0007
    if int(row["changed_cells_vs_h136"]) <= 3:
        score += 0.0005
    if float(row["delta_margin"]) < -0.00005:
        score -= 0.0040
    return score


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, _model_scores, _props = h118mod.prepare_context()
    h136 = load_move(ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv", sample, base_prob)
    start_eval = evaluate_matrix(h136, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)

    action_refs = [
        ActionRef(
            "r207_s2_toxicity_relief",
            "toxicity_relief",
            HITL / "h137_tail_toxicity_counterfield_hsjepa/submission_h137_counter_r207_S2_f0p25_g0p25_2bea533f.csv",
            "row207 S2 lowers H088 but is unsafe alone because it spends margin",
        ),
        ActionRef(
            "r135_q3s2_margin_repair_g025",
            "margin_repair",
            HITL / "h137_tail_toxicity_counterfield_hsjepa/submission_h137_counter_r135_Q3S2_f0p6_g0p25_baeb4807.csv",
            "row135 Q3/S2 repairs margin with small H088 relief",
        ),
        ActionRef(
            "r135_q3s2_margin_repair_g05",
            "margin_repair",
            HITL / "h137_tail_toxicity_counterfield_hsjepa/submission_h137_counter_r135_Q3S2_f0p6_g0p5_09427c97.csv",
            "stronger row135 Q3/S2 repair; better margin but larger H098 cost",
        ),
        ActionRef(
            "r135_q3s2_soft_repair",
            "soft_margin_repair",
            HITL / "h137_tail_toxicity_counterfield_hsjepa/submission_h137_counter_r135_Q3S2_f0p25_g0p25_74e8fb79.csv",
            "weaker row135 Q3/S2 repair used as low-cost boundary control",
        ),
        ActionRef(
            "r131_s1s2_stress_decoy",
            "stress_decoy",
            HITL / "h137_tail_toxicity_counterfield_hsjepa/submission_h137_counter_r131_S1S2_f0p25_g0p25_3f2e0739.csv",
            "stress decoy: should be rejected if H088-only shortcuts are toxic",
        ),
    ]
    action_moves = {ref.name: load_move(ref.path, sample, base_prob) for ref in action_refs}

    action_rows = []
    for ref in action_refs:
        move = action_moves[ref.name]
        evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        rec = {
            "name": ref.name,
            "role": ref.role,
            "worldview": ref.worldview,
            "changed_cells_vs_h136": int((np.abs(move - h136) > 1.0e-12).sum()),
            "delta_route": float(evald["route"] - start_eval["route"]),
            "delta_h098": float(evald["h098"] - start_eval["h098"]),
            "delta_h088": float(evald["h088"] - start_eval["h088"]),
            "delta_margin": float(evald["margin"] - start_eval["margin"]),
            "route": float(evald["route"]),
            "h098": float(evald["h098"]),
            "h088": float(evald["h088"]),
            "margin": float(evald["margin"]),
        }
        rec["h138_action_score"] = action_score(rec)
        action_rows.append(rec)
    action_df = pd.DataFrame(action_rows).sort_values("h138_action_score", ascending=False)

    candidate_specs = [
        CandidateSpec(
            "margin_only_g025",
            ("r135_q3s2_margin_repair_g025",),
            "tests whether row135 repair alone is action-grade without row207 toxicity relief",
        ),
        CandidateSpec(
            "margin_only_g05",
            ("r135_q3s2_margin_repair_g05",),
            "tests stronger margin repair without toxicity relief",
        ),
        CandidateSpec(
            "toxicity_relief_only",
            ("r207_s2_toxicity_relief",),
            "H137 baseline: H088 relief without repair should be stress-only",
        ),
        CandidateSpec(
            "boundary_pair_g025",
            ("r207_s2_toxicity_relief", "r135_q3s2_margin_repair_g025"),
            "toxicity relief plus low-cost margin repair should be the safest assignment field",
        ),
        CandidateSpec(
            "boundary_pair_g05",
            ("r207_s2_toxicity_relief", "r135_q3s2_margin_repair_g05"),
            "toxicity relief plus stronger repair tests whether margin can buy extra H088 relief",
        ),
        CandidateSpec(
            "boundary_pair_soft",
            ("r207_s2_toxicity_relief", "r135_q3s2_soft_repair"),
            "lower-cost repair tests whether tiny margin is enough",
        ),
        CandidateSpec(
            "stress_decoy_pair",
            ("r207_s2_toxicity_relief", "r131_s1s2_stress_decoy"),
            "negative-control pair; should be rejected by one-sided boundary scoring",
        ),
    ]

    h136_prob = h130mod.materialize(base_prob, h136)
    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs:
        move = h136.copy()
        for action_name in spec.actions:
            move = move + (action_moves[action_name] - h136)
        prob = h130mod.materialize(base_prob, move)
        evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        selected = changed_cells(h136, move)
        axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
        rec = {
            "candidate_id": safe_id(f"h138_{spec.name}_{short_hash(prob)}", 128),
            "spec": spec.name,
            "actions": "|".join(spec.actions),
            "worldview": spec.worldview,
            "changed_cells_vs_h136": int((np.abs(move - h136) > 1.0e-12).sum()),
            "changed_cells_vs_h136_prob": int((np.abs(prob - h136_prob) > TOL).sum()),
            "delta_route": float(evald["route"] - start_eval["route"]),
            "delta_h098": float(evald["h098"] - start_eval["h098"]),
            "delta_h088": float(evald["h088"] - start_eval["h088"]),
            "delta_margin": float(evald["margin"] - start_eval["margin"]),
            "route": float(evald["route"]),
            "h098": float(evald["h098"]),
            "h088": float(evald["h088"]),
            "margin": float(evald["margin"]),
            "h102_cum_h088_axis_cos": float(axis["h102_cum_h088_axis_cos"]),
            "h102_cum_good_bad_margin": float(axis["h102_cum_good_bad_margin"]),
        }
        rec["h138_candidate_score"] = candidate_score(rec)
        rec["passes_one_sided_boundary"] = bool(
            rec["delta_margin"] >= 0.0
            and rec["delta_h088"] <= -0.00050
            and rec["delta_h098"] <= 0.00000160
            and rec["delta_route"] <= 0.00000300
        )
        path = OUT / f"submission_{rec['candidate_id']}.csv"
        h085mod.write_submission(sample, prob, path)
        validation = h085mod.validate_submission(path, sample, base_prob)
        rec["file"] = path.name
        rec["resolved_path"] = str(path.resolve())
        rec.update({f"validation_{key}": value for key, value in validation.items()})
        candidate_rows.append(rec)
        if not selected.empty:
            selected = selected.copy()
            selected.insert(0, "candidate_id", rec["candidate_id"])
            selected_frames.append(selected)

    candidates = pd.DataFrame(candidate_rows).sort_values(
        ["passes_one_sided_boundary", "h138_candidate_score", "delta_h098"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    if candidates.empty:
        raise RuntimeError("H138 produced no candidates")
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h138_boundary_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    root_validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h138_one_sided_boundary_assignment",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        **selected,
        **{f"root_{key}": value for key, value in root_validation.items()},
    }

    action_df.to_csv(OUT / "h138_action_metrics.csv", index=False)
    candidates.to_csv(OUT / "h138_candidates.csv", index=False)
    if selected_frames:
        pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h138_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h138_decision.csv", index=False)

    report_cols = [
        "candidate_id",
        "spec",
        "actions",
        "changed_cells_vs_h136",
        "delta_route",
        "delta_h098",
        "delta_h088",
        "delta_margin",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "passes_one_sided_boundary",
        "h138_candidate_score",
        "file",
    ]
    report = f"""# H138 One-Sided Toxicity Boundary HS-JEPA

Question: can H137's H088 relief become action-grade only when paired with a
separate margin-repair assignment?

Start field: H136.

Start equation values:

- route: `{start_eval['route']:.12f}`
- H098/model: `{start_eval['h098']:.12f}`
- H088: `{start_eval['h088']:.12f}`
- margin: `{start_eval['margin']:.12f}`

Action atoms:

{md_table(action_df, 20)}

Candidates:

{md_table(candidates[report_cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation:

H138 is not an H088-minimizer.  It promotes only a one-sided boundary action
whose H088 relief survives after margin, route, and H098 constraints.  The
selected field should be read as:

```text
H136 safe row-state core
+ row207 S2 toxicity relief
+ row135 Q3/S2 margin repair
= boundary-safe row-target assignment hypothesis
```

Public interpretation:

- H138 > H137 and H136: toxicity relief is real but needs a repair head.
- H137 > H138: row135 repair is false and H088 relief should remain local.
- H136 > H138: counterfields are stress diagnostics, not action-grade.
"""
    (OUT / "h138_report.md").write_text(report, encoding="utf-8")

    print(f"H138 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(candidates[report_cols].to_string(index=False))


if __name__ == "__main__":
    run()
