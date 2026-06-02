#!/usr/bin/env python3
"""H090: lifestyle white-space HS-JEPA.

H089 found that lifestyle-transition gating mostly re-explains H088: the best
candidate overlaps H088's root cells by more than 90%.  H090 tests the
contrarian hypothesis:

    If HS-JEPA has another jump left, it will come from lifestyle-supported
    row-target white space that the current public/private gate does not touch.

This is intentionally not a safety tweak.  The decoder is allowed to act only
where H087/H088 root actions have low cell overlap, so a win would mean the
human-state context discovers a genuinely new hidden route.  A loss would
falsify the idea that direct lifestyle state can safely open new action space.
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
OUT = HITL / "h090_lifestyle_white_space_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h089mod = import_module(HITL / "h089_lifestyle_transition_gate_hsjepa.py", "h089mod_for_h090")
h087mod = h089mod.h087mod
h088mod = h089mod.h088mod

TARGETS = h089mod.TARGETS
KEYS = h089mod.KEYS
BASE_FILE = h089mod.BASE_FILE
TOL = h087mod.TOL


@dataclass(frozen=True)
class H090Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    max_h088_overlap: float
    max_h087_overlap: float
    min_white_score: float
    min_head_score: float
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h090_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h090_lifestyle_white_space_*_uploadsafe.csv"):
        path.unlink()


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h087mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h087mod.md_table(frame, n=n)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h087mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def parse_targets(text: object) -> list[str]:
    return h089mod.parse_targets(text)


def root_cell_set(kind: str) -> set[tuple[int, str]]:
    if kind == "h088":
        decision = pd.read_csv(HITL / "h088_dual_state_value_gate_hsjepa" / "h088_decision.csv").iloc[0]
        path = HITL / "h088_dual_state_value_gate_hsjepa" / "h088_selected_cells.csv"
    elif kind == "h087":
        decision = pd.read_csv(HITL / "h087_route_value_law_hsjepa" / "h087_decision.csv").iloc[0]
        path = HITL / "h087_route_value_law_hsjepa" / "h087_selected_cells.csv"
    else:
        raise ValueError(kind)
    cells = pd.read_csv(path)
    cells = cells[cells["candidate_id"] == str(decision["candidate_id"])]
    return {(int(row), str(target)) for row, target in zip(cells["row"], cells["target"])}


def add_overlap_and_white_score(actions: pd.DataFrame) -> pd.DataFrame:
    h088_cells = root_cell_set("h088")
    h087_cells = root_cell_set("h087")
    h088_rows = {row for row, _target in h088_cells}
    h087_rows = {row for row, _target in h087_cells}

    overlap_h088 = []
    overlap_h087 = []
    outside_h088 = []
    outside_h087 = []
    for rec in actions[["row", "targets"]].to_dict("records"):
        row = int(rec["row"])
        cells = [(row, target) for target in parse_targets(rec["targets"])]
        denom = max(len(cells), 1)
        ov88 = sum(cell in h088_cells for cell in cells) / denom
        ov87 = sum(cell in h087_cells for cell in cells) / denom
        overlap_h088.append(float(ov88))
        overlap_h087.append(float(ov87))
        outside_h088.append(float(row not in h088_rows))
        outside_h087.append(float(row not in h087_rows))

    out = actions.copy()
    out["h088_cell_overlap_ratio"] = overlap_h088
    out["h087_cell_overlap_ratio"] = overlap_h087
    out["outside_h088_row"] = outside_h088
    out["outside_h087_row"] = outside_h087
    out["white_space_rank"] = rank01(
        0.56 * (1.0 - out["h088_cell_overlap_ratio"].to_numpy(dtype=float))
        + 0.24 * (1.0 - out["h087_cell_overlap_ratio"].to_numpy(dtype=float))
        + 0.12 * out["outside_h088_row"].to_numpy(dtype=float)
        + 0.08 * out["outside_h087_row"].to_numpy(dtype=float)
    )
    out["white_state_score"] = (
        0.22 * out["white_space_rank"]
        + 0.18 * out["decoder_head_score"]
        + 0.14 * out["human_route_support_rank"]
        + 0.12 * out["assignment_rank"]
        + 0.10 * out["source_gain_rank"]
        + 0.09 * out["hard_gain_rank"]
        + 0.08 * out["posterior_gain_rank"]
        + 0.04 * out["h082_rank"]
        + 0.03 * out["bad_avoid_rank"]
        - 0.10 * (out["mean_bad_same_rank"].astype(float) > 0.72).astype(float)
        - 0.08 * (out["source_proxy_sum"].astype(float) > 3.0e-6).astype(float)
    )
    return out.sort_values("white_state_score", ascending=False).reset_index(drop=True)


def spec_list() -> list[H090Spec]:
    return [
        H090Spec(
            name="white_mixed_c760_r175_q105",
            profile="mixed",
            target_group="all",
            max_routes=175,
            max_cells=760,
            max_rows=175,
            q2_cap=105,
            max_per_subject=30,
            max_h088_overlap=0.35,
            max_h087_overlap=0.45,
            min_white_score=0.620,
            min_head_score=0.640,
            alpha=1.22,
            cap=2.20,
            novelty="new_lifestyle_supported_action_space",
        ),
        H090Spec(
            name="white_public_transition_c520_r145_q85",
            profile="public_transition",
            target_group="all",
            max_routes=145,
            max_cells=520,
            max_rows=145,
            q2_cap=85,
            max_per_subject=24,
            max_h088_overlap=0.30,
            max_h087_overlap=0.40,
            min_white_score=0.600,
            min_head_score=0.635,
            alpha=1.26,
            cap=2.25,
            novelty="unseen_volatile_rows_public_head",
        ),
        H090Spec(
            name="white_private_stable_c580_r150_q55",
            profile="private_stable",
            target_group="all",
            max_routes=150,
            max_cells=580,
            max_rows=150,
            q2_cap=55,
            max_per_subject=24,
            max_h088_overlap=0.30,
            max_h087_overlap=0.40,
            min_white_score=0.590,
            min_head_score=0.635,
            alpha=1.16,
            cap=2.05,
            novelty="unseen_routine_rows_private_head",
        ),
        H090Spec(
            name="white_objective_body_c500_r140",
            profile="objective_body",
            target_group="objective",
            max_routes=140,
            max_cells=500,
            max_rows=140,
            q2_cap=0,
            max_per_subject=22,
            max_h088_overlap=0.30,
            max_h087_overlap=0.35,
            min_white_score=0.575,
            min_head_score=0.620,
            alpha=1.20,
            cap=2.00,
            novelty="unseen_sensor_body_objective_head",
        ),
        H090Spec(
            name="white_calendar_q2_c420_r135_q120",
            profile="calendar_q2",
            target_group="q2_route",
            max_routes=135,
            max_cells=420,
            max_rows=135,
            q2_cap=120,
            max_per_subject=20,
            max_h088_overlap=0.35,
            max_h087_overlap=0.45,
            min_white_score=0.555,
            min_head_score=0.610,
            alpha=1.28,
            cap=2.30,
            novelty="unseen_calendar_cashflow_q2_head",
        ),
    ]


def allowed_by_profile(rec: dict[str, object], spec: H090Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not h089mod.target_allowed(targets, spec.target_group):
        return False
    if float(rec["h088_cell_overlap_ratio"]) > spec.max_h088_overlap:
        return False
    if float(rec["h087_cell_overlap_ratio"]) > spec.max_h087_overlap:
        return False
    if float(rec["white_state_score"]) < spec.min_white_score:
        return False
    if float(rec["decoder_head_score"]) < spec.min_head_score:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.78:
        return False

    profile = spec.profile
    head = str(rec["decoder_head"])
    mode = str(rec["value_mode"])
    if profile == "mixed":
        return bool(
            (head == "public_transition" and mode in h089mod.POSTERIOR_MODES and float(rec["posterior_delta_sum"]) <= 2.0e-6)
            or (head == "private_stable" and mode in h089mod.PRIVATE_MODES and float(rec["hard_delta_sum"]) <= 2.0e-6)
            or (head == "objective_body" and float(rec["is_objective_route"]) > 0 and float(rec["source_proxy_sum"]) <= 4.0e-6)
            or (head == "calendar_q2" and float(rec["has_q2"]) > 0 and float(rec["posterior_delta_sum"]) <= 3.0e-6)
        )
    if profile == "public_transition":
        return bool(
            head == "public_transition"
            and float(rec["public_transition_score"]) >= 0.55
            and mode in h089mod.POSTERIOR_MODES
            and float(rec["posterior_delta_sum"]) <= 2.0e-6
        )
    if profile == "private_stable":
        return bool(
            head == "private_stable"
            and mode in h089mod.PRIVATE_MODES
            and float(rec["hard_delta_sum"]) <= 2.0e-6
        )
    if profile == "objective_body":
        return bool(
            head == "objective_body"
            and float(rec["is_objective_route"]) > 0
            and float(rec["source_proxy_sum"]) <= 4.0e-6
        )
    if profile == "calendar_q2":
        return bool(
            head == "calendar_q2"
            and float(rec["has_q2"]) > 0
            and float(rec["posterior_delta_sum"]) <= 4.0e-6
        )
    raise ValueError(profile)


def select_actions(actions: pd.DataFrame, spec: H090Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("white_state_score", ascending=False).to_dict("records"):
        if not allowed_by_profile(rec, spec):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
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


def add_h090_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    scale = float(metrics["selected_cells"]) / (250 * 7)

    if selected_actions.empty:
        mean_white = 0.0
        mean_head = 0.0
        overlap88 = 0.0
        overlap87 = 0.0
        head_mix = ""
    else:
        mean_white = float(selected_actions["white_state_score"].mean())
        mean_head = float(selected_actions["decoder_head_score"].mean())
        overlap88 = float(selected_actions["h088_cell_overlap_ratio"].mean())
        overlap87 = float(selected_actions["h087_cell_overlap_ratio"].mean())
        head_mix = ";".join(f"{k}:{v}" for k, v in selected_actions["decoder_head"].value_counts().sort_index().items())

    score = (
        260.0 * (-posterior)
        + 260.0 * (-hard)
        + 160.0 * (-source)
        + 100.0 * (-resp)
        + 0.17 * mean_white
        + 0.12 * mean_head
        + 0.16 * (1.0 - overlap88)
        + 0.08 * (1.0 - overlap87)
        + 0.06 * min(scale / 0.45, 1.0)
        - 0.42 * bad
        - 0.16 * max(float(metrics["mean_bad_same_rank"]) - 0.52, 0.0)
    )
    metrics.update(
        {
            "h090_score": score,
            "mean_white_state_score": mean_white,
            "mean_decoder_head_score": mean_head,
            "mean_action_h088_overlap": overlap88,
            "mean_action_h087_overlap": overlap87,
            "decoder_head_mix": head_mix,
        }
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h087mod.h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    state = h089mod.build_transition_state(sample)
    state.to_csv(OUT / "h090_lifestyle_transition_state.csv", index=False)
    cell = h087mod.build_cell_table()
    route_actions = h088mod.build_dual_actions(h087mod.build_route_actions(cell))
    route_actions = h089mod.add_lifestyle_scores(route_actions, state)
    route_actions = add_overlap_and_white_score(route_actions)
    route_actions.to_csv(OUT / "h090_white_space_route_actions.csv", index=False)

    candidate_rows: list[dict[str, object]] = []
    all_selected_actions: list[pd.DataFrame] = []
    all_selected_cells: list[pd.DataFrame] = []
    for spec in spec_list():
        selected_actions = select_actions(route_actions, spec)
        if selected_actions.empty:
            continue
        h087_spec = h087mod.CandidateSpec(
            name=spec.name,
            target_group=spec.target_group if spec.target_group != "q2_route" else "all",
            value_modes=tuple(sorted(selected_actions["value_mode"].astype(str).unique())),
            max_routes=spec.max_routes,
            max_cells=spec.max_cells,
            max_rows=spec.max_rows,
            q2_cap=spec.q2_cap,
            max_per_subject=spec.max_per_subject,
            min_action_score=spec.min_white_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h090_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update({"profile": spec.profile, "h090_novelty": spec.novelty})
        metrics = add_h090_metrics(metrics, selected_actions, selected_cells)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H090 candidates")
    candidates = candidates.sort_values("h090_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h090_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h090_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h090_selected_cells.csv", index=False)

    decision_pool = candidates[candidates["selected_cells"] >= 40].copy()
    if decision_pool.empty:
        decision_pool = candidates.copy()
    decision = decision_pool.sort_values("h090_score", ascending=False).iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h090_lifestyle_white_space_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h090_decision.csv", index=False)

    top_actions = route_actions.head(50)[
        [
            "route_id",
            "row",
            "subject_id",
            "route_name",
            "targets",
            "value_mode",
            "decoder_head",
            "white_state_score",
            "h088_cell_overlap_ratio",
            "h087_cell_overlap_ratio",
            "decoder_head_score",
            "human_route_support_rank",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
        ]
    ]
    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    report = f"""# H090 Lifestyle White-Space HS-JEPA

Question: can lifestyle-state context safely open row-target action space that
H087/H088 did not touch?

Worldview:

- H089 mostly re-explained H088, so transition state alone did not yet create a
  new frontier.
- H090 forbids high overlap with H087/H088 root actions and searches only the
  lifestyle-supported white space.
- A win means HS-JEPA has found a new private/public state beyond the current
  public-equation support. A loss means direct lifestyle state is explanatory
  but not strong enough to authorize new actions.

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_lifestyle_white_space_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | hidden human state exists outside current H087/H088 action support |

Candidates:

{md_table(trimmed, n=20)}

Top White-Space Route Actions:

{md_table(top_actions, n=50)}

Interpretation rule:

- If H090 improves by >= 0.001, the next HS-JEPA paper claim is that lifestyle
  context discovers new action support, not just decoder-head choice.
- If H090 loses mildly, lifestyle state is a good explanation layer but should
  remain subordinate to public/private posterior support.
- If H090 loses badly, H087/H088 support is close to the safe frontier and
  white-space actions need a learned latent target instead of direct stories.
"""
    (OUT / "h090_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
