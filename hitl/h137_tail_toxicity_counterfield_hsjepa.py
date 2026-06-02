#!/usr/bin/env python3
"""H137: tail-toxicity counterfield HS-JEPA diagnostic.

H136 pruned H135's completion tail.  The next stronger question is whether the
tail is merely unnecessary, or whether it is actively wrong and should be moved
in the opposite direction.

Hypothesis:

    If H135's row135/207 completion tail is a public-punished action-toxicity
    field, then H136 plus an anti-tail/counter-tail should improve stress
    equations without losing the row164 route core.

This script deliberately treats H088/H018 as diagnostics, not action heads.  It
materializes a diagnostic candidate only after recording that the linear
anti-tail direction is locally unstable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import itertools
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h137_tail_toxicity_counterfield_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H136_PATH = HITL / "h136_benefit_toxicity_factorized_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h136mod_h137", H136_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H136_PATH}")
h136mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h136mod
SPEC.loader.exec_module(h136mod)

h135mod = h136mod.h135mod
h134mod = h136mod.h134mod
h133mod = h136mod.h133mod
h132mod = h136mod.h132mod
h130mod = h136mod.h130mod
h126mod = h136mod.h126mod
h123mod = h136mod.h123mod
h118mod = h136mod.h118mod
h102mod = h136mod.h102mod
h085mod = h136mod.h085mod

TARGETS = h136mod.TARGETS
TOL = h136mod.TOL


@dataclass(frozen=True)
class H137Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    amp: float
    cap: float
    pool_top: int
    min_score: float
    min_residual_gap: float
    max_residual_toxicity: float
    min_residual_safety: float
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    max_curv_marg: float
    max_h088_hard_cosine: float
    worldview: str


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h137_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h137_tailtox_*.csv"):
        path.unlink()


def root_submission_paths() -> dict[str, Path]:
    paths = h136mod.root_submission_paths()
    paths["h136"] = ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv"
    return paths


def load_move(name: str, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    path = root_submission_paths()[name]
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def known_hashes(sample: pd.DataFrame) -> set[str]:
    hashes: set[str] = set()
    for path in ROOT.glob("submission_h*_uploadsafe.csv"):
        try:
            df = h085mod.load_sub(path, sample)
            hashes.add(short_hash(df[TARGETS].to_numpy(dtype=np.float64)))
        except Exception:
            continue
    return hashes


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


def spec_for_eval() -> H137Spec:
    return H137Spec(
        name="h136_tailtox_counterfield",
        group="tail_toxicity_counterfield",
        max_cells=34,
        max_rows=26,
        max_per_subject=30,
        max_per_target=24,
        amp=1.0,
        cap=0.22,
        pool_top=220,
        min_score=0.0,
        min_residual_gap=-0.60,
        max_residual_toxicity=1.00,
        min_residual_safety=0.20,
        max_bad_weighted_pos=0.0008,
        max_bad_max_pos=0.0025,
        max_h088_cos=-0.055,
        min_good_margin=0.147,
        route_pred_cap=-0.000630,
        h098_pred_cap=-0.000016,
        max_curv_marg=0.000070,
        max_h088_hard_cosine=-0.018,
        worldview="H135 completion tail is not just removed; it may define a counterfield whose opposite direction tests action toxicity",
    )


def broad_bundle_spec() -> h135mod.H135Spec:
    return h135mod.H135Spec(
        name="proxy_h137_counterfield",
        group="tail_toxicity_counterfield",
        start_name="h136",
        row_source="all_q1_bundle_rows",
        target_mode="q3s_companion",
        max_bundle_size=2,
        frac_values=(0.25, 0.35, 0.50, 0.60),
        max_steps=4,
        min_step_score=0.0,
        min_non_h088_passes=0,
        max_cells=34,
        max_rows=26,
        max_per_subject=30,
        max_per_target=24,
        amp=1.0,
        cap=0.22,
        pool_top=220,
        min_score=0.0,
        min_residual_gap=-0.60,
        max_residual_toxicity=1.00,
        min_residual_safety=0.20,
        max_bad_weighted_pos=0.0008,
        max_bad_max_pos=0.0025,
        max_h088_cos=-0.055,
        min_good_margin=0.147,
        route_pred_cap=-0.000630,
        h098_pred_cap=-0.000016,
        max_curv_marg=0.000070,
        max_h088_hard_cosine=-0.018,
        min_component_gain=0.0,
        min_companion_score=0.250,
        min_proposal_abs=0.010,
        min_bundle_score=0.43,
        h088_weight=0.0020,
        margin_weight=0.020,
        worldview="broad bundle pool for H137 counterfield diagnostics",
    )


def previous_moves(sample: pd.DataFrame, base_prob: np.ndarray, moves: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    prev = h136mod.previous_moves(sample, base_prob, {name: moves[name] for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133", "h134", "h135"]})
    prev["h136"] = moves["h136"].reshape(-1)
    return prev


def make_selected(catalog: pd.DataFrame, move_mat: np.ndarray) -> pd.DataFrame:
    selected = h130mod.make_selected(catalog, move_mat)
    if selected.empty:
        return selected
    selected["h137_actual_move"] = selected["h130_actual_move"]
    selected["h112_move"] = selected["h137_actual_move"].to_numpy(dtype=np.float64)
    return selected


def tail_cells(tail: np.ndarray) -> list[dict[str, object]]:
    rows = []
    for row, tidx in np.argwhere(np.abs(tail) > 1.0e-12):
        rows.append({"row": int(row), "target_index": int(tidx), "target": TARGETS[int(tidx)], "tail_move": float(tail[row, tidx])})
    return rows


def delta_row(kind: str, label: str, beta: float, move_mat: np.ndarray, start: np.ndarray, start_eval: dict[str, float], evald: dict[str, float]) -> dict[str, object]:
    return {
        "kind": kind,
        "label": label,
        "beta": float(beta),
        "changed_cells_vs_h136": int((np.abs(move_mat - start) > 1.0e-12).sum()),
        "route": evald["route"],
        "h098": evald["h098"],
        "curv_marg": evald["curv_marg"],
        "h088": evald["h088"],
        "margin": evald["margin"],
        "badw": evald["badw"],
        "badmax": evald["badmax"],
        "delta_route": evald["route"] - start_eval["route"],
        "delta_h098": evald["h098"] - start_eval["h098"],
        "delta_curv_marg": evald["curv_marg"] - start_eval["curv_marg"],
        "delta_h088": evald["h088"] - start_eval["h088"],
        "delta_margin": evald["margin"] - start_eval["margin"],
    }


def anti_bundle_move(start: np.ndarray, bundle: dict[str, object], gamma: float, cap: float) -> np.ndarray:
    out = start.copy()
    for op in bundle["ops"]:
        row = int(op["row"])
        tidx = int(op["target_index"])
        old = float(start[row, tidx])
        forward = float(op["new_move"])
        out[row, tidx] = float(np.clip(old - gamma * (forward - old), -cap, cap))
    return out


def candidate_score(metrics: dict[str, object]) -> float:
    return (
        300.0 * (-float(metrics["model_pred_delta_vs_h057"]))
        + 285.0 * (-float(metrics["route_basis_pred_delta_vs_h057"]))
        + 120.0 * (-float(metrics["h118_curv_marginal_vs_zero"]))
        + 0.10 * float(metrics["h102_cum_good_bad_margin"])
        + 0.07 * max(-float(metrics["h102_cum_h088_axis_cos"]), 0.0)
        + 0.14 * float(metrics["selected_mean_residual_safety"])
        + 0.11 * float(metrics["selected_mean_residual_gap"])
        - 0.16 * float(metrics["selected_mean_residual_toxicity"])
        + 7.0 * max(-float(metrics["h137_delta_h088"]), 0.0)
        + 6.0 * max(float(metrics["h137_delta_margin"]), 0.0)
        - 28.0 * max(-float(metrics["h137_delta_margin"]), 0.0)
        - 20.0 * max(float(metrics["h137_delta_h098"]), 0.0)
        - 15.0 * max(float(metrics["h137_delta_route"]), 0.0)
        - 18.0 * max(float(metrics["hard_diag_delta_vs_h057"]), 0.0)
    )


def run() -> None:
    cleanup_previous_outputs()
    spec = spec_for_eval()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    moves = {name: load_move(name, sample, base_prob) for name in ["h122", "h124", "h126", "h127", "h128", "h129", "h130", "h131", "h132", "h133", "h134", "h135", "h136"]}
    previous = previous_moves(sample, base_prob, moves)
    known = known_hashes(sample)
    start = moves["h136"]
    tail = moves["h135"] - moves["h136"]
    start_eval = evaluate_matrix(start, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)

    tail_df = pd.DataFrame(tail_cells(tail))
    rows = []
    raw_candidates = []
    for beta in [-0.50, -0.25, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00]:
        move_mat = start - beta * tail
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        rec = delta_row("linear_tail", f"tail_beta_{beta:g}", beta, move_mat, start, start_eval, evald)
        rec["h137_linear_stability"] = (
            8.0 * max(-rec["delta_h088"], 0.0)
            + 3.0 * max(rec["delta_margin"], 0.0)
            - 14.0 * max(rec["delta_h098"], 0.0)
            - 10.0 * max(rec["delta_route"], 0.0)
            - 1.5 * max(-rec["delta_margin"], 0.0)
        )
        rows.append(rec)
        if beta in {0.25, 0.50, 0.75}:
            raw_candidates.append((rec, move_mat, f"antitail_b{str(beta).replace('.', 'p')}"))

    bundle_rows = h133mod.collect_bundle_rows(catalog, moves["h131"])
    q1_rows = h134mod.collect_q1_rows(bundle_rows)
    cell_pool, bundle_pool = h135mod.build_bundle_pool(catalog, start, q1_rows, broad_bundle_spec())
    bundle_diag = []
    for bundle in bundle_pool.head(60).to_dict("records"):
        if int(bundle["row"]) == 164:
            continue
        forward = h135mod.apply_bundle(start, bundle)
        forward_eval = evaluate_matrix(forward, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        frow = delta_row("forward_bundle", str(bundle["bundle_id"]), float(bundle["frac"]), forward, start, start_eval, forward_eval)
        frow.update({"bundle_row": int(bundle["row"]), "bundle_targets": str(bundle["targets"]), "bundle_score": float(bundle["h135_bundle_score"])})
        bundle_diag.append(frow)
        for gamma in [0.25, 0.50, 1.00]:
            anti = anti_bundle_move(start, bundle, gamma, spec.cap)
            anti_eval = evaluate_matrix(anti, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            arow = delta_row("anti_bundle", f"{bundle['bundle_id']}_g{gamma:g}", gamma, anti, start, start_eval, anti_eval)
            arow.update({"bundle_row": int(bundle["row"]), "bundle_targets": str(bundle["targets"]), "bundle_score": float(bundle["h135_bundle_score"])})
            arow["h137_counterfield_score"] = (
                10.0 * max(-arow["delta_h088"], 0.0)
                + 4.0 * max(arow["delta_margin"], 0.0)
                - 14.0 * max(arow["delta_h098"], 0.0)
                - 10.0 * max(arow["delta_route"], 0.0)
                - 1.5 * max(-arow["delta_margin"], 0.0)
                + 0.0006 * float(bundle["h135_bundle_score"])
            )
            bundle_diag.append(arow)
            if (
                arow["h137_counterfield_score"] > -0.00002
                and anti_eval["route"] <= spec.route_pred_cap
                and anti_eval["h098"] <= spec.h098_pred_cap
                and anti_eval["h088"] <= spec.max_h088_cos
                and anti_eval["margin"] >= spec.min_good_margin
            ):
                raw_candidates.append((arow, anti, f"counter_{safe_id(str(bundle['bundle_id']), 40)}_g{str(gamma).replace('.', 'p')}"))

    candidate_rows = []
    selected_frames = []
    emitted: set[str] = set()
    for rec, move_mat, label in raw_candidates:
        prob = h130mod.materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        if hash_id in known or hash_id in emitted:
            continue
        emitted.add(hash_id)
        candidate_id = safe_id(f"h137_{label}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        selected_cells = make_selected(catalog, move_mat)
        axis = h102mod.cumulative_axis_metrics(move_mat.reshape(-1), bad_axes, bad_moves, good_moves)
        evald = evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
        diag = {
            "h118_zero_curv": -0.0002616634510263019,
            "h118_curv_pred_delta_vs_h057": evald["curv_marg"] - 0.0002616634510263019,
            "h118_curv_marginal_vs_zero": evald["curv_marg"],
            "h118_mean_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).mean()),
            "h118_max_forbidden_same": float(selected_cells.get("h117_forbidden_same", pd.Series([0.0])).astype(float).max()),
            "h118_mean_forbidden_pressure": float(selected_cells.get("h117_forbidden_pressure", pd.Series([0.0])).astype(float).mean()),
            "h118_mean_veto_score": float(selected_cells.get("h118_forbidden_veto_score", pd.Series([1.0])).astype(float).mean()),
            "h118_selected_rows": int(selected_cells["row"].nunique()),
            "h137_start_field": "h136",
            "h137_candidate_kind": rec["kind"],
            "h137_candidate_label": rec["label"],
            "h137_beta": float(rec["beta"]),
            "h137_changed_cells_vs_h136": int(rec["changed_cells_vs_h136"]),
            "h137_delta_route": float(evald["route"] - start_eval["route"]),
            "h137_delta_h098": float(evald["h098"] - start_eval["h098"]),
            "h137_delta_curv_marg": float(evald["curv_marg"] - start_eval["curv_marg"]),
            "h137_delta_h088": float(evald["h088"] - start_eval["h088"]),
            "h137_delta_margin": float(evald["margin"] - start_eval["margin"]),
        }
        metrics = h118mod.evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected_cells,
            cell,
            sample,
            base_prob,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            spec,
            path,
            axis,
            diag,
            previous,
        )
        h088_cos = float(metrics.get("h118_h088_cosine", 0.0))
        if h088_cos > spec.max_h088_hard_cosine:
            continue
        metrics["h137_worldview"] = spec.worldview
        metrics["h137_fit_feature_set"] = fit.feature_set
        metrics["h137_fit_alpha"] = fit.alpha
        metrics["h137_fit_score"] = fit.score
        metrics["h137_score"] = candidate_score(metrics)
        candidate_rows.append(metrics)
        sel = selected_cells.copy()
        if "candidate_id" in sel.columns:
            sel = sel.drop(columns=["candidate_id"])
        sel.insert(0, "candidate_id", candidate_id)
        selected_frames.append(sel)

    tail_df.to_csv(OUT / "h137_tail_cells.csv", index=False)
    pd.DataFrame(rows).to_csv(OUT / "h137_linear_antitail_sweep.csv", index=False)
    pd.DataFrame(bundle_diag).to_csv(OUT / "h137_bundle_counterfield_sweep.csv", index=False)
    catalog.to_csv(OUT / "h137_catalog.csv", index=False)
    bundle_pool.drop(columns=["ops"]).to_csv(OUT / "h137_bundle_pool.csv", index=False)
    cell_pool.to_csv(OUT / "h137_cell_pool.csv", index=False)
    model_scores.to_csv(OUT / "h137_curvature_model_scores.csv", index=False)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        report = f"""# H137 Tail-Toxicity Counterfield HS-JEPA

No candidate passed the H137 materialization/evaluation gate.

Tail cells:

{md_table(tail_df, 20)}

Linear anti-tail sweep:

{md_table(pd.DataFrame(rows), 20)}

Bundle counterfield sweep:

{md_table(pd.DataFrame(bundle_diag).sort_values("h137_counterfield_score", ascending=False) if bundle_diag else pd.DataFrame(), 40)}

Interpretation:

The H135 tail is not a linear reversible toxicity direction.  H136's pruning is
more plausible than anti-tail inversion unless public feedback says otherwise.
"""
        (OUT / "h137_report.md").write_text(report, encoding="utf-8")
        print("H137 promoted no candidate")
        print(pd.DataFrame(rows).to_string(index=False))
        return

    candidates = candidates.sort_values(["h137_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    candidates.to_csv(OUT / "h137_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h137_selected_cells.csv", index=False)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h137_tailtox_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h137_tail_toxicity_counterfield_diagnostic",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["h137_worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }
    pd.DataFrame([decision]).to_csv(OUT / "h137_decision.csv", index=False)

    cols = [
        "candidate_id",
        "h137_candidate_kind",
        "h137_candidate_label",
        "selected_cells",
        "changed_rows_vs_h057",
        "h137_changed_cells_vs_h136",
        "h137_delta_route",
        "h137_delta_h098",
        "h137_delta_h088",
        "h137_delta_margin",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "h137_score",
        "file",
    ]
    report = f"""# H137 Tail-Toxicity Counterfield HS-JEPA

Question: is H135's completion tail just unnecessary, or should its direction
be inverted as an action-toxicity counterfield?

Tail cells:

{md_table(tail_df, 20)}

Linear anti-tail sweep:

{md_table(pd.DataFrame(rows), 20)}

Bundle counterfield sweep:

{md_table(pd.DataFrame(bundle_diag).sort_values("h137_counterfield_score", ascending=False), 40)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H137 beats H136/H135 publicly, tail toxicity is directional and HS-JEPA
  needs a counterfield decoder, not just pruning.
- If H136 beats H137, the tail is one-sided/nonlinear toxicity; pruning is the
  right action and anti-tail inversion is wrong.
- If H135 beats both, the tail was actually route-completion signal.
"""
    (OUT / "h137_report.md").write_text(report, encoding="utf-8")
    print("H137 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
