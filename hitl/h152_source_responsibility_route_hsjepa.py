#!/usr/bin/env python3
"""H152: source-responsibility row-route HS-JEPA solver.

H149/H150 translate source actions at cell level.  H152 makes the decoder more
JEPA-like: a row must choose a source-action route, then choose the target
subset inside that route.  This tests whether the missing correction translator
is source responsibility rather than more cell filtering.
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
OUT = HITL / "h152_source_responsibility_route_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H150_PATH = HITL / "h150_bundle_listener_stress_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h150mod_h152", H150_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H150_PATH}")
h150mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h150mod
SPEC.loader.exec_module(h150mod)

h149mod = h150mod.h149mod
h148mod = h150mod.h148mod
h085mod = h150mod.h085mod
TARGETS = h150mod.TARGETS
BASE_FILE = h150mod.BASE_FILE
TOL = h150mod.TOL

SOURCE_FILES = [
    "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv",
    "submission_h075_antibad_transport_f6863945_uploadsafe.csv",
    "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv",
    "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv",
    "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
    "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
    "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
    "submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv",
]


@dataclass(frozen=True)
class RouteSpec:
    name: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    max_per_source: int
    max_per_row_cells: int
    amp: float
    min_positive_variants: int
    max_positive_delta: float
    require_frontier_negative: bool
    require_no_pre_negative: bool
    description: str


ROUTE_SPECS = [
    RouteSpec(
        name="route_responsibility_upside",
        max_cells=430,
        max_rows=165,
        max_per_subject=112,
        max_per_target=96,
        max_per_source=150,
        max_per_row_cells=5,
        amp=0.64,
        min_positive_variants=8,
        max_positive_delta=0.00024,
        require_frontier_negative=False,
        require_no_pre_negative=False,
        description="row-source route assignment with broad listener consensus",
    ),
    RouteSpec(
        name="route_responsibility_consensus",
        max_cells=360,
        max_rows=155,
        max_per_subject=98,
        max_per_target=82,
        max_per_source=120,
        max_per_row_cells=4,
        amp=0.60,
        min_positive_variants=9,
        max_positive_delta=0.00012,
        require_frontier_negative=False,
        require_no_pre_negative=True,
        description="source route must survive no-pre-H listener",
    ),
    RouteSpec(
        name="route_responsibility_frontier_guard",
        max_cells=300,
        max_rows=140,
        max_per_subject=88,
        max_per_target=70,
        max_per_source=100,
        max_per_row_cells=4,
        amp=0.58,
        min_positive_variants=9,
        max_positive_delta=0.00006,
        require_frontier_negative=True,
        require_no_pre_negative=True,
        description="route assignment only when frontier-only listener also agrees",
    ),
]


def locate(name: str | Path) -> Path | None:
    return h085mod.locate(name)


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(x)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(values, high=high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h152_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h152_source_route_*.csv"):
        path.unlink()


def load_sub(path: Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return h085mod.load_sub(path, sample)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    h085mod.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    return h085mod.validate_submission(path, sample, base_prob)


def movement_from_file(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(-1)


def fit_listener_worlds(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, dict[str, object]]]:
    obs = h148mod.collect_public_observations(sample)
    moves = {row["file"]: movement_from_file(Path(row["resolved_path"]), sample, base_prob) for row in obs.to_dict("records")}
    for file_name in SOURCE_FILES + h148mod.CANDIDATE_FILES:
        path = locate(file_name)
        if path is None:
            continue
        try:
            load_sub(path, sample)
        except Exception:
            continue
        moves[file_name] = movement_from_file(path, sample, base_prob)
    features = h149mod.build_bundle_features(sample, base_prob)
    models = {spec.name: h150mod.fit_variant(obs, moves, features, spec) for spec in h150mod.variant_specs()}
    return obs, moves, models


def gradients(models: dict[str, dict[str, object]], n_cells: int) -> dict[str, np.ndarray]:
    return {name: h150mod.gradient(model, n_cells) for name, model in models.items()}


def route_pred(move: np.ndarray, idx: np.ndarray, grads: dict[str, np.ndarray]) -> dict[str, float]:
    out = {}
    for name, grad in grads.items():
        out[f"{name}_pred_delta"] = float(np.sum(grad[idx] * move[idx]))
    vals = np.array(list(out.values()), dtype=np.float64)
    out["robust_positive_variant_count"] = int((vals < 0).sum())
    out["robust_mean_pred_delta"] = float(vals.mean())
    out["robust_min_pred_delta"] = float(vals.min())
    out["robust_max_pred_delta"] = float(vals.max())
    return out


def build_route_candidates(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    moves: dict[str, np.ndarray],
    models: dict[str, dict[str, object]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_rows, n_targets = base_prob.shape
    grads = gradients(models, n_rows * n_targets)
    h088 = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    rows = []
    cell_rows = []
    for source_file in SOURCE_FILES:
        if source_file not in moves:
            continue
        move = moves[source_file]
        h088_same = (move * h088) > 0
        h088_penalty = h088_same.astype(float) * rank01(np.abs(h088), high=True)
        benefit_matrix = np.vstack([-grad * move for grad in grads.values()])
        pos_frac = (benefit_matrix > 0).mean(axis=0)
        mean_benefit = benefit_matrix.mean(axis=0)
        min_benefit = benefit_matrix.min(axis=0)
        allfull = benefit_matrix[list(grads).index("all_full")]
        frontier = benefit_matrix[list(grads).index("frontier_only")]
        no_pre = benefit_matrix[list(grads).index("no_pre_h")]

        for row_idx in range(n_rows):
            row_flat = np.arange(row_idx * n_targets, (row_idx + 1) * n_targets)
            changed = row_flat[np.abs(move[row_flat]) > TOL]
            if len(changed) == 0:
                continue
            base_masks = {
                "consensus_any": changed[
                    (pos_frac[changed] >= 0.70)
                    & (mean_benefit[changed] > 0)
                    & (allfull[changed] > 0)
                    & (h088_penalty[changed] <= 0.98)
                ],
                "frontier_safe": changed[
                    (pos_frac[changed] >= 0.65)
                    & (mean_benefit[changed] > 0)
                    & (frontier[changed] > 0)
                    & (h088_penalty[changed] <= 0.95)
                ],
                "no_pre_safe": changed[
                    (pos_frac[changed] >= 0.70)
                    & (mean_benefit[changed] > 0)
                    & (no_pre[changed] > 0)
                    & (h088_penalty[changed] <= 0.98)
                ],
            }
            # Add group-specific route variants so a row can choose a Q or S
            # target route without mixing source identities cell-by-cell.
            base_masks["q_route"] = base_masks["consensus_any"][(base_masks["consensus_any"] % n_targets) <= 2]
            base_masks["s_route"] = base_masks["consensus_any"][(base_masks["consensus_any"] % n_targets) >= 3]

            for mode, idx in base_masks.items():
                idx = np.asarray(sorted(set(idx.tolist())), dtype=int)
                if len(idx) == 0:
                    continue
                pred = route_pred(move, idx, grads)
                target_list = [TARGETS[int(i % n_targets)] for i in idx]
                route_benefit = float(mean_benefit[idx].sum())
                route_min_benefit = float(min_benefit[idx].min())
                route_h088_penalty = float(h088_penalty[idx].mean())
                route_score = (
                    -1200.0 * pred["robust_mean_pred_delta"]
                    - 700.0 * min(pred["robust_max_pred_delta"], 0.0)
                    + 0.18 * pred["robust_positive_variant_count"]
                    + 4500.0 * route_benefit
                    + 1000.0 * route_min_benefit
                    - 0.35 * route_h088_penalty
                    + 0.08 * min(len(idx), 4)
                    + 0.04 * (len(set(target_list)) >= 2)
                )
                rec = {
                    "source_file": source_file,
                    "row": int(row_idx),
                    "subject_id": sample.loc[row_idx, "subject_id"],
                    "sleep_date": sample.loc[row_idx, "sleep_date"],
                    "lifelog_date": sample.loc[row_idx, "lifelog_date"],
                    "mode": mode,
                    "flat_indices": ",".join(str(int(i)) for i in idx),
                    "targets": ",".join(target_list),
                    "n_cells": int(len(idx)),
                    "n_targets": int(len(set(target_list))),
                    "route_benefit": route_benefit,
                    "route_min_benefit": route_min_benefit,
                    "route_h088_penalty": route_h088_penalty,
                    "route_score": float(route_score),
                    **pred,
                }
                rows.append(rec)
                for flat_idx in idx:
                    cell_rows.append(
                        {
                            "source_file": source_file,
                            "row": int(row_idx),
                            "mode": mode,
                            "flat_idx": int(flat_idx),
                            "target": TARGETS[int(flat_idx % n_targets)],
                            "source_move": float(move[flat_idx]),
                            "pos_frac": float(pos_frac[flat_idx]),
                            "mean_benefit": float(mean_benefit[flat_idx]),
                            "min_benefit": float(min_benefit[flat_idx]),
                            "frontier_benefit": float(frontier[flat_idx]),
                            "no_pre_benefit": float(no_pre[flat_idx]),
                            "h088_penalty": float(h088_penalty[flat_idx]),
                        }
                    )
    route_df = pd.DataFrame(rows).sort_values("route_score", ascending=False).reset_index(drop=True)
    cell_df = pd.DataFrame(cell_rows)
    return route_df, cell_df


def select_routes(route_df: pd.DataFrame, spec: RouteSpec) -> pd.DataFrame:
    candidates = route_df[
        (route_df["robust_positive_variant_count"] >= spec.min_positive_variants)
        & (route_df["robust_max_pred_delta"] <= spec.max_positive_delta)
    ].copy()
    if spec.require_frontier_negative:
        candidates = candidates[candidates["frontier_only_pred_delta"] < 0].copy()
    if spec.require_no_pre_negative:
        candidates = candidates[candidates["no_pre_h_pred_delta"] < 0].copy()
    candidates = candidates.sort_values("route_score", ascending=False)

    selected = []
    used_rows: set[int] = set()
    cells_used = 0
    per_subject: dict[str, int] = {}
    per_target: dict[str, int] = {}
    per_source: dict[str, int] = {}
    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        idx = [int(x) for x in str(rec["flat_indices"]).split(",") if x != ""]
        if not idx:
            continue
        targets = [TARGETS[i % len(TARGETS)] for i in idx]
        if len(idx) > spec.max_per_row_cells:
            idx = idx[: spec.max_per_row_cells]
            targets = [TARGETS[i % len(TARGETS)] for i in idx]
            rec["flat_indices"] = ",".join(str(i) for i in idx)
            rec["targets"] = ",".join(targets)
            rec["n_cells"] = len(idx)
        subject = str(rec["subject_id"])
        source = str(rec["source_file"])
        if cells_used + len(idx) > spec.max_cells:
            continue
        if len(selected) >= spec.max_rows:
            continue
        if per_subject.get(subject, 0) + len(idx) > spec.max_per_subject:
            continue
        if per_source.get(source, 0) + len(idx) > spec.max_per_source:
            continue
        if any(per_target.get(t, 0) + targets.count(t) > spec.max_per_target for t in set(targets)):
            continue
        selected.append(rec)
        used_rows.add(row)
        cells_used += len(idx)
        per_subject[subject] = per_subject.get(subject, 0) + len(idx)
        per_source[source] = per_source.get(source, 0) + len(idx)
        for target in targets:
            per_target[target] = per_target.get(target, 0) + 1
    return pd.DataFrame(selected)


def materialize(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    selected_routes: pd.DataFrame,
    moves: dict[str, np.ndarray],
    spec: RouteSpec,
) -> tuple[np.ndarray, pd.DataFrame]:
    base_flat = base_prob.reshape(-1)
    new_flat = base_flat.copy()
    selected_cells = []
    for rec in selected_routes.to_dict("records"):
        source = str(rec["source_file"])
        move = moves[source]
        idx = [int(x) for x in str(rec["flat_indices"]).split(",") if x != ""]
        for flat_idx in idx:
            row = flat_idx // len(TARGETS)
            target_idx = flat_idx % len(TARGETS)
            old = float(new_flat[flat_idx])
            new_flat[flat_idx] = sigmoid(logit(base_flat[flat_idx]) + spec.amp * move[flat_idx])
            selected_cells.append(
                {
                    "source_file": source,
                    "row": row,
                    "subject_id": sample.loc[row, "subject_id"],
                    "sleep_date": sample.loc[row, "sleep_date"],
                    "lifelog_date": sample.loc[row, "lifelog_date"],
                    "target_index": target_idx,
                    "target": TARGETS[target_idx],
                    "flat_idx": flat_idx,
                    "h057_prob": float(base_flat[flat_idx]),
                    "source_move": float(move[flat_idx]),
                    "old_prob": old,
                    "new_prob": float(new_flat[flat_idx]),
                    "amp": spec.amp,
                    "route_mode": rec["mode"],
                    "route_score": rec["route_score"],
                }
            )
    return new_flat.reshape(base_prob.shape), pd.DataFrame(selected_cells)


def candidate_metrics(file_name: str, move: np.ndarray, models: dict[str, dict[str, object]], h088_move: np.ndarray) -> dict[str, object]:
    rec = h150mod.candidate_metric_row(file_name, move, models, h088_move)
    pred_cols = [f"{name}_pred_delta" for name in models]
    vals = np.array([rec[col] for col in pred_cols], dtype=np.float64)
    rec["robust_positive_variant_count"] = int((vals < 0).sum())
    rec["robust_mean_pred_delta"] = float(vals.mean())
    rec["robust_min_pred_delta"] = float(vals.min())
    rec["robust_max_pred_delta"] = float(vals.max())
    return rec


def run() -> None:
    cleanup_previous_outputs()
    base_path = locate(BASE_FILE)
    if base_path is None:
        raise FileNotFoundError(BASE_FILE)
    sample = load_sub(base_path)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)
    obs, moves, models = fit_listener_worlds(sample, base_prob)
    route_df, route_cell_df = build_route_candidates(sample, base_prob, moves, models)
    route_df.to_csv(OUT / "h152_route_candidates.csv", index=False)
    route_cell_df.to_csv(OUT / "h152_route_cell_candidates.csv", index=False)
    obs.to_csv(OUT / "h152_public_observations_used.csv", index=False)

    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    decision_rows = []
    candidate_rows = []
    selected_frames = []
    for spec in ROUTE_SPECS:
        selected_routes = select_routes(route_df, spec)
        new_prob, selected_cells = materialize(sample, base_prob, selected_routes, moves, spec)
        hash_id = short_hash(new_prob)
        local_path = OUT / f"submission_h152_{spec.name}_{hash_id}.csv"
        write_submission(sample, new_prob, local_path)
        move = movement_from_file(local_path, sample, base_prob)
        metric = candidate_metrics(local_path.name, move, models, h088_move)
        validation = validate_submission(local_path, sample, base_prob)
        selected_routes.to_csv(OUT / f"h152_selected_routes_{spec.name}.csv", index=False)
        selected_cells.to_csv(OUT / f"h152_selected_cells_{spec.name}.csv", index=False)
        selected_frames.append(selected_cells.assign(spec=spec.name))
        rec = {
            "spec": spec.name,
            "description": spec.description,
            "local_path": str(local_path.resolve()),
            "hash": hash_id,
            "selected_routes": int(len(selected_routes)),
            "selected_cells": int(len(selected_cells)),
            "selected_rows": int(selected_cells["row"].nunique()) if not selected_cells.empty else 0,
            "selected_source_mix": selected_cells["source_file"].value_counts().to_dict() if not selected_cells.empty else {},
            "selected_target_mix": selected_cells["target"].value_counts().to_dict() if not selected_cells.empty else {},
            **{f"validation_{k}": v for k, v in validation.items()},
            **{f"metric_{k}": v for k, v in metric.items() if k != "file"},
        }
        decision_rows.append(rec)
        candidate_rows.append(metric | {"spec": spec.name})

    # Compare with current H149-H151 candidates.
    for file_name in [
        "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
        "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
        "submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv",
    ]:
        path = locate(file_name)
        if path is None:
            continue
        move = movement_from_file(path, sample, base_prob)
        candidate_rows.append(candidate_metrics(file_name, move, models, h088_move) | {"spec": "reference"})

    candidate_scores = pd.DataFrame(candidate_rows)
    candidate_scores = candidate_scores.sort_values(
        ["robust_positive_variant_count", "robust_mean_pred_delta", "h088_move_cosine"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h152_candidate_scores.csv", index=False)

    decisions = pd.DataFrame(decision_rows)
    decisions["decision_score"] = (
        -1000.0 * decisions["metric_robust_mean_pred_delta"]
        - 300.0 * np.maximum(decisions["metric_robust_max_pred_delta"], 0.0)
        + 0.12 * decisions["metric_robust_positive_variant_count"]
        - 0.35 * decisions["metric_h088_move_cosine"]
        + 0.0005 * decisions["selected_cells"]
    )
    decisions = decisions.sort_values("decision_score", ascending=False).reset_index(drop=True)
    best = decisions.iloc[0].to_dict()
    best_local = Path(str(best["local_path"]))
    root_path = ROOT / f"submission_h152_source_route_{best['spec']}_{best['hash']}_uploadsafe.csv"
    shutil.copyfile(best_local, root_path)
    root_validation = validate_submission(root_path, sample, base_prob)
    decisions.loc[0, "root_uploadsafe_path"] = str(root_path.resolve())
    for key, value in root_validation.items():
        decisions.loc[0, f"root_{key}"] = value
    decisions.to_csv(OUT / "h152_decision.csv", index=False)
    if selected_frames:
        pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h152_all_selected_cells.csv", index=False)

    report = f"""# H152 Source-Responsibility Row-Route HS-JEPA

Date: 2026-06-03

## Question

H149/H150 select source actions mostly at cell level. H152 asks whether the
decoder should instead assign one source-action route per row, then select a
target subset inside that route.

```text
row context -> source responsibility -> target route subset -> correction
```

## Route Specs

{md_table(pd.DataFrame([spec.__dict__ for spec in ROUTE_SPECS]), 10)}

## Promoted Decision

{md_table(decisions.head(3), 3)}

## Candidate Comparison

{md_table(candidate_scores[["spec", "file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta", "robust_min_pred_delta", "robust_max_pred_delta"]], 20)}

## Top Route Candidates

{md_table(route_df[["source_file", "row", "subject_id", "sleep_date", "mode", "targets", "n_cells", "route_score", "robust_positive_variant_count", "robust_mean_pred_delta", "robust_max_pred_delta"]], 30)}

## Interpretation

H152 is a row-route assignment counterfactual:

- if H152 beats H149/H150 offline or publicly, source responsibility is the
  missing decoder layer;
- if H152 is weaker, H149/H150's cell-level mixing is not the immediate
  bottleneck, and the next big bet should move to public/private subset
  factorization or new target-route states.
"""
    (OUT / "h152_report.md").write_text(report, encoding="utf-8")

    print(f"H152 promoted: {root_path}")
    print(decisions[["spec", "selected_cells", "selected_rows", "metric_robust_mean_pred_delta", "metric_h088_move_cosine", "root_uploadsafe_path"]].head(3).to_string(index=False))
    print(candidate_scores[["spec", "file", "robust_positive_variant_count", "robust_mean_pred_delta", "h088_move_cosine"]].head(10).to_string(index=False))


if __name__ == "__main__":
    run()
