#!/usr/bin/env python3
"""H088: public/private dual-state value gate HS-JEPA.

H087 showed a value-law conflict: the best posterior-moving route decoder can
hurt H018's hard-world state, while hard/source decoders preserve the hard state
but reduce posterior gain.  H088 therefore treats that conflict as signal.

Worldview:

    H085 posterior and H018 hard-world are not two estimates of one target.
    They are two latent human-state heads.  A cell/route is actionable only when
    a route-conditioned value law gives a Pareto improvement under both heads.

If this wins, HS-JEPA needs a public/private dual-head gate before decoding.
If it fails, the hard-world posterior is diagnostic but not an action-grade
private-state target.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h088_dual_state_value_gate_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H087_PATH = HITL / "h087_route_value_law_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h087mod", H087_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H087_PATH}")
h087mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h087mod
SPEC.loader.exec_module(h087mod)

TARGETS = h087mod.TARGETS
KEYS = h087mod.KEYS
TOL = h087mod.TOL
BASE_FILE = h087mod.BASE_FILE


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h088_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h088_dual_state_gate_*_uploadsafe.csv"):
        path.unlink()


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h087mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h087mod.md_table(frame, n=n)


def build_dual_actions(actions: pd.DataFrame) -> pd.DataFrame:
    out = actions.copy()
    pareto = (
        (out["posterior_delta_sum"] < -1.0e-8)
        & (out["hard_delta_sum"] < -1.0e-8)
        & (out["source_proxy_sum"] <= 2.0e-6)
        & (out["mean_bad_same_rank"] <= 0.72)
    )
    out["dual_pareto"] = pareto.astype(int)
    out["posterior_positive_penalty"] = (out["posterior_delta_sum"] > 0.0).astype(float)
    out["hard_positive_penalty"] = (out["hard_delta_sum"] > 0.0).astype(float)
    out["source_positive_penalty"] = (out["source_proxy_sum"] > 0.0).astype(float)
    out["dual_score"] = (
        0.25 * out["posterior_gain_rank"]
        + 0.25 * out["hard_gain_rank"]
        + 0.18 * out["source_gain_rank"]
        + 0.10 * out["resp_gain_rank"]
        + 0.08 * out["assignment_rank"]
        + 0.06 * out["h082_rank"]
        + 0.04 * out["bad_avoid_rank"]
        + 0.04 * out["scale_rank"]
        + 0.10 * out["dual_pareto"]
        - 0.25 * out["posterior_positive_penalty"]
        - 0.25 * out["hard_positive_penalty"]
        - 0.12 * out["source_positive_penalty"]
    )
    out["value_law_score"] = out["dual_score"]
    return out.sort_values("dual_score", ascending=False).reset_index(drop=True)


def spec_list() -> list[h087mod.CandidateSpec]:
    return [
        h087mod.CandidateSpec(
            name="dual_pareto_all_c980_r180_q95",
            target_group="all",
            value_modes=("triad_consensus", "hard_source_bridge", "h085_hard_bridge", "q_source_bridge", "hard_q", "hard_binary_edge"),
            max_routes=180,
            max_cells=980,
            max_rows=180,
            q2_cap=95,
            max_per_subject=30,
            min_action_score=0.0,
            alpha=1.10,
            cap=1.95,
            novelty_bonus="dual_public_private_pareto",
        ),
        h087mod.CandidateSpec(
            name="dual_pareto_nonq2_c860_r175",
            target_group="nonq2",
            value_modes=("triad_consensus", "hard_source_bridge", "h085_hard_bridge", "q_source_bridge", "hard_q"),
            max_routes=175,
            max_cells=860,
            max_rows=175,
            q2_cap=0,
            max_per_subject=30,
            min_action_score=0.0,
            alpha=1.12,
            cap=1.90,
            novelty_bonus="dual_private_nonq2",
        ),
        h087mod.CandidateSpec(
            name="dual_pareto_objective_c760_r165",
            target_group="objective",
            value_modes=("triad_consensus", "hard_source_bridge", "h085_hard_bridge", "q_source_bridge"),
            max_routes=165,
            max_cells=760,
            max_rows=165,
            q2_cap=0,
            max_per_subject=28,
            min_action_score=0.0,
            alpha=1.15,
            cap=1.80,
            novelty_bonus="dual_objective_state",
        ),
        h087mod.CandidateSpec(
            name="dual_pareto_qroute_c430_r150_q110",
            target_group="q_route",
            value_modes=("h085_hard_bridge", "hard_source_bridge", "triad_consensus", "hard_binary_edge", "hard_q"),
            max_routes=150,
            max_cells=430,
            max_rows=150,
            q2_cap=110,
            max_per_subject=24,
            min_action_score=0.0,
            alpha=1.18,
            cap=2.10,
            novelty_bonus="dual_q_route",
        ),
        h087mod.CandidateSpec(
            name="dual_pareto_aggressive_c1180_r205_q120",
            target_group="all",
            value_modes=("triad_consensus", "hard_source_bridge", "h085_hard_bridge", "q_source_bridge", "hard_q", "hard_binary_edge"),
            max_routes=205,
            max_cells=1180,
            max_rows=205,
            q2_cap=120,
            max_per_subject=34,
            min_action_score=0.0,
            alpha=1.22,
            cap=2.15,
            novelty_bonus="dual_aggressive",
        ),
    ]


def target_allowed(targets: list[str], group: str) -> bool:
    return h087mod.target_allowed(targets, group)


def select_dual_actions(actions: pd.DataFrame, spec: h087mod.CandidateSpec) -> pd.DataFrame:
    selected = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    candidates = actions[
        actions["value_mode"].isin(spec.value_modes)
        & (actions["dual_pareto"] == 1)
    ].sort_values("dual_score", ascending=False)

    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        targets = [t for t in str(rec["targets"]).split(",") if t]
        if not target_allowed(targets, spec.target_group):
            continue
        if row in used_rows:
            continue
        if len(selected) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        if n_cells + int(rec["n_cells"]) > spec.max_cells:
            continue
        if q2_cells + int(rec["q2_cells"]) > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        n_cells += int(rec["n_cells"])
        q2_cells += int(rec["q2_cells"])

    return pd.DataFrame(selected)


def add_h088_score(metrics: dict[str, object]) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    source_agree = float(metrics["source_agree_rate"])
    h082 = float(metrics["h082_ratio"])
    scale = float(metrics["selected_cells"]) / (250 * 7)
    score = (
        420.0 * (-posterior)
        + 360.0 * (-hard)
        + 180.0 * (-source)
        + 120.0 * (-resp)
        + 0.14 * source_agree
        + 0.12 * h082
        + 0.12 * min(scale / 0.55, 1.0)
        - 0.38 * bad
        - 0.18 * max(float(metrics["mean_bad_same_rank"]) - 0.50, 0.0)
    )
    metrics["h088_score"] = score
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h087mod.h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    cell = h087mod.build_cell_table()
    route_actions = build_dual_actions(h087mod.build_route_actions(cell))
    route_actions.to_csv(OUT / "h088_dual_route_actions.csv", index=False)

    candidate_rows = []
    all_selected_actions = []
    all_selected_cells = []
    for spec in spec_list():
        selected_actions = select_dual_actions(route_actions, spec)
        if selected_actions.empty:
            continue
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h088_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, spec, path)
        metrics = add_h088_score(metrics)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H088 candidates")
    candidates = candidates.sort_values("h088_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h088_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h088_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h088_selected_cells.csv", index=False)

    decision = candidates.iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h088_dual_state_gate_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h088_decision.csv", index=False)

    top_actions = route_actions.head(40)[
        [
            "route_id",
            "row",
            "subject_id",
            "sleep_date",
            "route_name",
            "targets",
            "value_mode",
            "dual_score",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
            "dual_pareto",
            "assignment_route_score",
            "mean_h082_cell",
            "mean_bad_same_rank",
        ]
    ]

    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    report = f"""# H088 Public/Private Dual-State Value Gate HS-JEPA

Question: are H085 posterior and H018 hard-world two latent heads that should be
Pareto-gated before decoding route actions?

Worldview:

- H087 exposed a conflict between posterior-friendly and hard-world-friendly
  value laws.
- H088 only accepts route-actions whose value law improves both heads locally.
- This is not a blend tweak: it changes the HS-JEPA decoder from one hidden
  state to a public/private dual-head gate.

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_dual_state_value_gate_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | posterior and hard-world are separate latent heads; decode only Pareto-safe route actions |

Candidates:

{md_table(trimmed, n=20)}

Top Dual Route Actions:

{md_table(top_actions, n=40)}

Interpretation rule:

- If H088 improves by >= 0.001, HS-JEPA needs a dual public/private value gate.
- If H088 is weaker than H087/H071, hard-world is useful as a diagnostic but
  too conservative as an action-grade head.
- If H088 loses badly, the public-equation hard-world posterior is likely an
  overfit artifact for action selection.
"""
    (OUT / "h088_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
