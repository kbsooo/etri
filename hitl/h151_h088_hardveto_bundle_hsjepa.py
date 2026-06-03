#!/usr/bin/env python3
"""H151: H088-hard-veto bundle listener HS-JEPA.

H150 role-holdout showed that H088 is not predicted correctly when removed:
the model mistakes the H088 world for a beneficial action.  That means H088 is
not just another bad anchor; it is a non-substitutable toxicity sensor.

H151 keeps the bundle-listener worldview but treats H088 same-direction cells
as a hard veto unless multiple listener worlds strongly agree on benefit.
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
OUT = HITL / "h151_h088_hardveto_bundle_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H150_PATH = HITL / "h150_bundle_listener_stress_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h150mod_h151", H150_PATH)
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
    for path in OUT.glob("submission_h151_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h151_h088_hardveto_*.csv"):
        path.unlink()


def movement_from_file(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    prob = h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(-1)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    h085mod.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    return h085mod.validate_submission(path, sample, base_prob)


def candidate_metric_row(file_name: str, move: np.ndarray, models: dict[str, dict[str, object]], h088_move: np.ndarray) -> dict[str, object]:
    return h150mod.candidate_metric_row(file_name, move, models, h088_move)


def run() -> None:
    cleanup_previous_outputs()
    base_path = locate(BASE_FILE)
    if base_path is None:
        raise FileNotFoundError(BASE_FILE)
    sample = h085mod.load_sub(base_path)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)
    base_flat = base_prob.reshape(-1)

    obs = h148mod.collect_public_observations(sample)
    moves = {row["file"]: movement_from_file(Path(row["resolved_path"]), sample, base_prob) for row in obs.to_dict("records")}
    features = h149mod.build_bundle_features(sample, base_prob)
    h088_file = "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"
    h088_move = moves[h088_file]

    # Refit the same listener worlds as H150 so H151 is directly comparable.
    models = {spec.name: h150mod.fit_variant(obs, moves, features, spec) for spec in h150mod.variant_specs()}
    h150_source_path = HITL / "h150_bundle_listener_stress_hsjepa/h150_source_cell_scores.csv"
    if not h150_source_path.exists():
        raise FileNotFoundError(h150_source_path)
    source = pd.read_csv(h150_source_path)
    source["hard_h088_veto"] = (
        source["h088_same_direction"].astype(bool)
        & (source["h088_penalty"] > 0.35)
        & (source["pos_frac"] < 0.95)
    )
    source["h151_score"] = (
        source["score"]
        + 0.70 * source["pos_frac"]
        + 5000.0 * source["mean_benefit"]
        + 1500.0 * source["frontier_benefit"]
        + 1000.0 * source["no_pre_benefit"]
        - 1.50 * source["hard_h088_veto"].astype(float)
        - 0.90 * source["h088_penalty"]
    )
    source = source.sort_values(
        ["flat_idx", "hard_h088_veto", "h151_score", "pos_frac"],
        ascending=[True, True, False, False],
    ).drop_duplicates("flat_idx", keep="first")

    gated = source[
        (~source["hard_h088_veto"])
        & (source["pos_frac"] >= 0.70)
        & (source["mean_benefit"] > 0)
        & (source["allfull_benefit"] > 0)
        & (source["no_pre_benefit"] > -1.0e-6)
        & (source["h151_score"] >= source["h151_score"].quantile(0.50))
    ].sort_values("h151_score", ascending=False)
    if len(gated) < 180:
        gated = source[
            (~source["hard_h088_veto"])
            & (source["pos_frac"] >= 0.62)
            & (source["mean_benefit"] > 0)
            & (source["h151_score"] >= source["h151_score"].quantile(0.45))
        ].sort_values("h151_score", ascending=False)

    selected_rows = []
    per_subject: dict[str, int] = {}
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    max_cells = 360
    max_rows = 160
    max_per_subject = 100
    max_per_target = 88
    max_per_row = 5
    for rec in gated.to_dict("records"):
        if len(selected_rows) >= max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        if len({int(x["row"]) for x in selected_rows}) >= max_rows and row not in per_row:
            continue
        if per_subject.get(subject, 0) >= max_per_subject:
            continue
        if per_target.get(target, 0) >= max_per_target:
            continue
        if per_row.get(row, 0) >= max_per_row:
            continue
        selected_rows.append(rec)
        per_subject[subject] = per_subject.get(subject, 0) + 1
        per_target[target] = per_target.get(target, 0) + 1
        per_row[row] = per_row.get(row, 0) + 1

    selected = pd.DataFrame(selected_rows)
    new_flat = base_flat.copy()
    if not selected.empty:
        idx = selected["flat_idx"].to_numpy(dtype=int)
        amp = 0.58
        new_flat[idx] = sigmoid(logit(base_flat[idx]) + amp * selected["source_move"].to_numpy(dtype=np.float64))
        selected["amp"] = amp
        selected["new_prob"] = new_flat[idx]
    new_prob = new_flat.reshape(base_prob.shape)
    hash_id = short_hash(new_prob)
    local_path = OUT / f"submission_h151_h088_hardveto_bundle_{hash_id}.csv"
    root_path = ROOT / f"submission_h151_h088_hardveto_bundle_{hash_id}_uploadsafe.csv"
    write_submission(sample, new_prob, local_path)
    shutil.copyfile(local_path, root_path)
    validation = validate_submission(root_path, sample, base_prob)

    h151_move = movement_from_file(root_path, sample, base_prob)
    h150_path = locate("submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv")
    h149_path = locate("submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv")
    comparison_rows = []
    for name, path in [
        (root_path.name, root_path),
        ("submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv", h150_path),
        ("submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv", h149_path),
    ]:
        if path is None:
            continue
        move = movement_from_file(path, sample, base_prob)
        comparison_rows.append(candidate_metric_row(name, move, models, h088_move))
    comparison = pd.DataFrame(comparison_rows)
    comparison["robust_positive_variant_count"] = (comparison[[f"{name}_pred_delta" for name in models]] < 0).sum(axis=1)
    comparison["robust_mean_pred_delta"] = comparison[[f"{name}_pred_delta" for name in models]].mean(axis=1)
    comparison.to_csv(OUT / "h151_candidate_comparison.csv", index=False)
    selected.to_csv(OUT / "h151_selected_cells.csv", index=False)
    source.to_csv(OUT / "h151_source_cell_scores.csv", index=False)

    metric = candidate_metric_row(root_path.name, h151_move, models, h088_move)
    decision = {
        "candidate_file": root_path.name,
        "candidate_path": str(root_path.resolve()),
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
        "selected_source_mix": selected["source_file"].value_counts().to_dict() if not selected.empty else {},
        "selected_target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
        "worldview": (
            "H088 is a non-substitutable toxicity sensor; same-direction cells are "
            "vetoed unless listener consensus is extremely strong."
        ),
        "failure_interpretation": (
            "If H151 underperforms H149/H150 offline or publicly, then the H088 "
            "axis is better as a soft penalty than a hard veto."
        ),
        **{f"validation_{k}": v for k, v in validation.items()},
        **{f"metric_{k}": v for k, v in metric.items() if k != "file"},
    }
    pd.DataFrame([decision]).to_csv(OUT / "h151_decision.csv", index=False)

    report = f"""# H151 H088-Hard-Veto Bundle HS-JEPA

Date: 2026-06-03

## Question

H150 role-holdout showed that removing H088 makes the listener equation predict
H088 in the wrong direction. H151 asks:

```text
Should H088 be a hard toxicity veto rather than a learned bad-anchor component?
```

## Candidate

{md_table(pd.DataFrame([decision]), 1)}

## H149/H150/H151 Comparison

{md_table(comparison[["file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta", "all_full_pred_delta", "no_pre_h_pred_delta", "frontier_only_pred_delta", "human_social_only_pred_delta"]], 10)}

Source mix:

{md_table(selected["source_file"].value_counts().rename_axis("source_file").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

Target mix:

{md_table(selected["target"].value_counts().rename_axis("target").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

## Interpretation

H151 is not meant to dominate H149 on upside.  It is a structural counterfactual:

- H149 = high-upside bundle listener, soft H088 penalty;
- H150 = robust consensus across listener worlds;
- H151 = hard H088 toxicity veto.

If H151 becomes the safest offline candidate, H088 should be formalized in
HS-JEPA as a hard anti-shortcut constraint.  If H149/H150 remain better, H088
should stay a stress diagnostic / soft toxicity energy.
"""
    (OUT / "h151_report.md").write_text(report, encoding="utf-8")

    print(f"H151 candidate: {root_path}")
    print(f"selected cells: {len(selected)}")
    print(comparison[["file", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta"]].to_string(index=False))


if __name__ == "__main__":
    run()
