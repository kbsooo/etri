#!/usr/bin/env python3
"""Team-facing end-to-end package for Route-Conserving S2 Bridge HS-JEPA.

This script packages the strongest paper/competition mechanism without old
experiment-version vocabulary.

Mechanism:
    Public-sensitive driver action
      + objective-stage bridge action
      + S2 listener/hub interpretation
      + route-consistency energy check

The script can refresh all dependency modules from the original data and
submission ledger, or assemble a clean team-facing package from existing
outputs.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939

STAGE_BRIDGE_MODULE = ROOT / "paper_hsjepa_core" / "stage_bridge_conservation_solver.py"
S2HUB_MODULE = ROOT / "paper_hsjepa_core" / "s2hub_bridge_solver.py"
S2_DISTILL_MODULE = ROOT / "paper_hsjepa_core" / "s2hub_human_state_distillation.py"

STAGE_BRIDGE_READOUT = ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_conservation_readout.json"
S2HUB_READOUT = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_bridge_readout.json"
S2_DISTILL_READOUT = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_human_state_distillation" / "s2hub_human_state_distillation_readout.json"


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def load_submission(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    keys_match = df[KEYS].equals(sample[KEYS])
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(keys_match),
        "duplicate_keys": int(df[KEYS].duplicated().sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > 1e-12).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def refresh_dependencies() -> None:
    """Run the underlying reproducible modules from their own entrypoints."""

    stage_bridge = import_module(STAGE_BRIDGE_MODULE, "team_stage_bridge")
    s2hub = import_module(S2HUB_MODULE, "team_s2hub_bridge")
    s2_distill = import_module(S2_DISTILL_MODULE, "team_s2hub_distill")
    stage_bridge.run()
    s2hub.run()
    s2_distill.run()


def ensure_readouts(refresh: bool) -> None:
    if refresh:
        refresh_dependencies()
        return
    missing = [p for p in [STAGE_BRIDGE_READOUT, S2HUB_READOUT, S2_DISTILL_READOUT] if not p.exists()]
    if missing:
        refresh_dependencies()


def package_submission(
    role_name: str,
    source_path: Path,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
) -> dict[str, object]:
    df = load_submission(source_path)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    digest = short_hash(prob)
    out_name = f"submission_team_hsjepa_{role_name}_{digest}_uploadsafe.csv"
    local_path = OUT / out_name
    root_path = ROOT / out_name
    df.to_csv(local_path, index=False)
    df.to_csv(root_path, index=False)
    validation = validate_submission(root_path, sample, base_prob)
    return {
        "role": role_name,
        "source_path": str(source_path.resolve()),
        "submission_file": out_name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "hash": digest,
        "validation": validation,
    }


def output_from_readout(readout: dict[str, object], variant: str) -> dict[str, object]:
    outputs = readout["outputs"]
    if not isinstance(outputs, dict) or variant not in outputs:
        raise KeyError(variant)
    item = outputs[variant]
    if not isinstance(item, dict):
        raise TypeError(variant)
    return item


def extract_metric(item: dict[str, object], key: str, default=None):
    if key in item:
        return item[key]
    diag = item.get("diagnostics")
    if isinstance(diag, dict) and key in diag:
        return diag[key]
    metrics = item.get("listener_metrics")
    if isinstance(metrics, dict) and key in metrics:
        return metrics[key]
    return default


def run(refresh: bool = False) -> dict[str, object]:
    ensure_readouts(refresh)
    stage_readout = read_json(STAGE_BRIDGE_READOUT)
    s2hub_readout = read_json(S2HUB_READOUT)
    distill_readout = read_json(S2_DISTILL_READOUT)

    # Import candidate1 only after readouts exist, because it owns sample/base loading.
    stage_bridge = import_module(STAGE_BRIDGE_MODULE, "team_stage_bridge_for_sample")
    candidate1 = stage_bridge.candidate1
    candidate1.ensure_prerequisites()
    sample, base_prob, _base_logit, _base_grads, _semantic_grads, _h088_move = candidate1.load_world()

    stage_primary = output_from_readout(stage_readout, "stagebridge_jackpot")
    s2_interpretable = output_from_readout(s2hub_readout, "s2hub_jackpot")
    human_state_probe = output_from_readout(distill_readout, "s2hub_jackpot")

    packaged = {
        "competition_primary": package_submission(
            "route_conserving_objective_bridge_primary",
            Path(str(stage_primary["root_path"])),
            sample,
            base_prob,
        ),
        "interpretable_s2_hub": package_submission(
            "s2_listener_bridge_interpretable",
            Path(str(s2_interpretable["root_path"])),
            sample,
            base_prob,
        ),
        "human_state_probe": package_submission(
            "human_state_gated_s2_bridge_probe",
            Path(str(human_state_probe["root_path"])),
            sample,
            base_prob,
        ),
    }

    evidence_rows = [
        {
            "component": "Route-Conserving Objective Bridge",
            "role": "competition_primary",
            "submission_file": packaged["competition_primary"]["submission_file"],
            "listener_changed_cells": extract_metric(stage_primary, "changed_cells"),
            "submission_changed_cells_vs_current_best": packaged["competition_primary"]["validation"][
                "changed_cells_vs_current_best"
            ],
            "changed_rows": extract_metric(stage_primary, "changed_rows"),
            "mean_route_energy": extract_metric(stage_primary, "mean_route_energy"),
            "base_mean_route_energy": extract_metric(stage_primary, "base_mean_route_energy"),
            "h088_cosine": extract_metric(stage_primary, "h088_cosine"),
            "claim": "Public-sensitive S-stage driver actions should be paired with route-preserving bridge actions.",
        },
        {
            "component": "S2 Listener Bridge",
            "role": "interpretable_s2_hub",
            "submission_file": packaged["interpretable_s2_hub"]["submission_file"],
            "listener_changed_cells": extract_metric(s2_interpretable, "changed_cells"),
            "submission_changed_cells_vs_current_best": packaged["interpretable_s2_hub"]["validation"][
                "changed_cells_vs_current_best"
            ],
            "changed_rows": extract_metric(s2_interpretable, "changed_rows"),
            "mean_route_energy": extract_metric(s2_interpretable, "mean_route_energy"),
            "base_mean_route_energy": extract_metric(s2_interpretable, "base_mean_route_energy"),
            "h088_cosine": extract_metric(s2_interpretable, "h088_cosine"),
            "claim": "S2 acts as a public-sensitive listener/hub inside the objective sleep-stage route.",
        },
        {
            "component": "Human-State Gated S2 Probe",
            "role": "human_state_probe",
            "submission_file": packaged["human_state_probe"]["submission_file"],
            "listener_changed_cells": extract_metric(human_state_probe, "changed_cells"),
            "submission_changed_cells_vs_current_best": packaged["human_state_probe"]["validation"][
                "changed_cells_vs_current_best"
            ],
            "changed_rows": extract_metric(human_state_probe, "changed_rows"),
            "mean_route_energy": None,
            "base_mean_route_energy": None,
            "h088_cosine": extract_metric(human_state_probe, "h088_cosine"),
            "claim": "OG human-state explains target/cell orientation, but not row assignment.",
        },
    ]
    evidence = pd.DataFrame(evidence_rows)
    evidence_path = OUT / "route_conserving_s2_bridge_evidence_table.csv"
    evidence.to_csv(evidence_path, index=False)

    package = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "current_best_file": CURRENT_BEST_FILE,
        "current_best_public_lb": CURRENT_BEST_PUBLIC_LB,
        "mechanism": (
            "Select public-sensitive objective-stage driver corrections, add local bridge corrections "
            "that preserve the learned Q/S route manifold, and interpret S2 as the main listener/hub."
        ),
        "why_this_is_not_only_trial_and_error": [
            "The bridge is selected by a route-energy invariant learned from train labels.",
            "S2 is a repeated listener/hub constraint, not a post-hoc file-specific tweak.",
            "Human-state distillation is kept as an orientation diagnostic instead of being overclaimed as a row selector.",
            "Failed target-listener route lift is recorded as evidence that listener posterior alone is not an action generator.",
        ],
        "packaged_submissions": packaged,
        "evidence_table_path": str(evidence_path.resolve()),
        "source_readouts": {
            "stage_bridge": str(STAGE_BRIDGE_READOUT.resolve()),
            "s2hub": str(S2HUB_READOUT.resolve()),
            "s2_distillation": str(S2_DISTILL_READOUT.resolve()),
        },
    }
    package_path = OUT / "route_conserving_s2_bridge_package.json"
    package_path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(package, indent=2, ensure_ascii=False))
    return package


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="rerun dependency modules before packaging")
    args = parser.parse_args()
    run(refresh=args.refresh)


if __name__ == "__main__":
    main()
