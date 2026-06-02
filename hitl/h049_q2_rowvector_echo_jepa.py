#!/usr/bin/env python3
"""H049: Q2 row-vector echo HS-JEPA.

H042 proved that a tiny Q2 phase action is public-real. H047/H048 then asked
whether the support rows form a hidden Q2 support/public-subset state. H049
raises the stake:

    If Q2 support is a human-state marker, the same rows should carry a weak
    route-consistent echo on Q1/Q3/S1-S4.

The experiment starts from the known public best H042, keeps its Q2 action, and
adds only non-Q2 row-vector echoes. A win means Q2 was a row-level hidden state
marker. A loss means H042 was mostly Q2-local calibration/phase.
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
OUT = HITL / "h049_q2_rowvector_echo_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
Q2_I = TARGETS.index("Q2")
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H043 = "submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv"


@dataclass(frozen=True)
class EchoSpec:
    family: str
    target_source: str
    unit: str
    group: str
    k: int
    alpha: float
    temperature: float
    require_agree: bool


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h042 = import_module(HITL / "h042_action_coupled_equation_solver_jepa.py", "h042_for_h049")
h043 = import_module(HITL / "h043_q2_phase_manifold_jepa.py", "h043_for_h049")
h045 = import_module(HITL / "h045_conditional_route_action_decoder_jepa.py", "h045_for_h049")
h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h049")

# Keep helper output isolated inside the H049 directory.
h042.OUT = OUT
h043.OUT = OUT
h045.OUT = OUT
h045.h042.OUT = OUT
h045.h043.OUT = OUT


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rank01(x: np.ndarray | pd.Series, high: bool = True) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    fill = float(np.nanmedian(arr[np.isfinite(arr)])) if np.isfinite(arr).any() else 0.0
    s = pd.Series(arr).replace([np.inf, -np.inf], np.nan).fillna(fill)
    if s.nunique(dropna=True) <= 1:
        out = np.full(len(s), 0.5, dtype=np.float64)
    else:
        out = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return out if high else 1.0 - out


def safe_id(text: str, limit: int = 118) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def pivot_cell_csv(path: Path, value_col: str) -> np.ndarray:
    df = pd.read_csv(path)
    wide = df.pivot(index="row", columns="target", values=value_col).sort_index()
    return wide[TARGETS].to_numpy(dtype=np.float64)


def load_prob(path_or_name: str | Path, sample: pd.DataFrame | None = None) -> np.ndarray:
    return h036.load_sub(path_or_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def load_state(rt: dict[str, object]) -> dict[str, object]:
    h012 = h036.load_sub(H012)
    sample = h012[KEYS].copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = load_prob(H042, sample)
    h043_prob = load_prob(H043, sample)
    h020_joint = pivot_cell_csv(HITL / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv", "q_joint_vector")
    h048_world = pivot_cell_csv(OUT / "h048_world_posterior_cells.csv" if (OUT / "h048_world_posterior_cells.csv").exists() else HITL / "h048_q2_public_subset_support_world_jepa" / "h048_world_posterior_cells.csv", "world_q_cond")
    h048_rows_path = OUT / "h048_world_posterior_rows.csv"
    if not h048_rows_path.exists():
        h048_rows_path = HITL / "h048_q2_public_subset_support_world_jepa" / "h048_world_posterior_rows.csv"
    h048_rows = pd.read_csv(h048_rows_path).sort_values("row").reset_index(drop=True)

    phase_state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = h045.build_route_context(rt, phase_state, h012_prob, h042_prob, h043_prob)
    return {
        "sample": sample,
        "h012_prob": h012_prob,
        "h042_prob": h042_prob,
        "h043_prob": h043_prob,
        "h020_joint": clip_prob(h020_joint),
        "h048_world": clip_prob(h048_world),
        "h048_rows": h048_rows,
        "phase_state": phase_state,
        "route": route,
    }


def target_group_mask(group: str, n_rows: int) -> np.ndarray:
    targets = {
        "Q": ["Q1", "Q3"],
        "S": ["S1", "S2", "S3", "S4"],
        "QS": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "S14": ["S1", "S4"],
        "S23": ["S2", "S3"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
    }[group]
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for target in targets:
        mask[:, TARGETS.index(target)] = True
    return mask


def echo_targets(state: dict[str, object]) -> dict[str, np.ndarray]:
    h012 = state["h012_prob"]
    joint = state["h020_joint"]
    world = state["h048_world"]
    z012 = logit(h012)
    zj = logit(joint)
    zw = logit(world)
    return {
        "joint": joint,
        "world": world,
        "joint_world_mid": sigmoid(0.50 * zj + 0.50 * zw),
        "joint_world_soft": sigmoid(0.35 * zj + 0.35 * zw + 0.30 * z012),
        "world_tempered": sigmoid(0.62 * zw + 0.38 * z012),
        "joint_tempered": sigmoid(0.62 * zj + 0.38 * z012),
    }


def build_row_scores(state: dict[str, object]) -> pd.DataFrame:
    rows = state["h048_rows"].copy().sort_values("row").reset_index(drop=True)
    route = state["route"].sort_values("row").reset_index(drop=True)
    h042_support = np.asarray(state["phase_state"]["h042_support"], dtype=bool)
    rows["route_public"] = route["h044_public_transition_score"].to_numpy(dtype=np.float64)
    rows["route_private"] = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    rows["route_q2regime"] = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    rows["route_phase"] = route["h044_phase_energy_score"].to_numpy(dtype=np.float64)
    rows["h042_support_runtime"] = h042_support
    rows["support_or_public"] = (
        0.28 * rank01(rows["world_public_prob"])
        + 0.26 * rank01(rows["h047_support_posterior"])
        + 0.18 * rank01(rows["h047_public_score"])
        + 0.14 * rank01(rows["route_public"])
        + 0.10 * rank01(rows["route_q2regime"])
        + 0.12 * rows["h042_support_runtime"].astype(float)
        - 0.10 * rank01(rows["h047_private_score"])
    )
    rows["pure_support"] = (
        0.45 * rank01(rows["h047_support_posterior"])
        + 0.25 * rows["h042_support_runtime"].astype(float)
        + 0.20 * rank01(rows["route_phase"])
        - 0.12 * rank01(rows["route_private"])
    )
    rows["public_not_private"] = (
        0.38 * rank01(rows["world_public_prob"])
        + 0.28 * rank01(rows["h047_public_score"])
        + 0.20 * rank01(rows["route_public"])
        - 0.25 * rank01(rows["h047_private_score"])
        - 0.12 * rank01(rows["route_private"])
    )
    rows.to_csv(OUT / "h049_row_scores.csv", index=False)
    return rows


def materialize_candidate(
    spec: EchoSpec,
    state: dict[str, object],
    row_scores: pd.DataFrame,
    target_prob: np.ndarray,
) -> tuple[dict[str, object], np.ndarray] | None:
    sample = state["sample"]
    h012_prob = state["h012_prob"]
    h042_prob = state["h042_prob"]
    z012 = logit(h012_prob)
    z_base = logit(h042_prob)
    z_target = logit(target_prob)
    n_rows = len(sample)
    h042_support = np.asarray(state["phase_state"]["h042_support"], dtype=bool)
    h047_support = row_scores["h047_support_posterior"].to_numpy(dtype=np.float64) >= row_scores["h047_support_posterior"].quantile(0.72)
    row_score = row_scores[spec.unit].to_numpy(dtype=np.float64)

    group_mask = target_group_mask(spec.group, n_rows)
    direction = z_target - z012
    if spec.require_agree:
        joint_dir = logit(state["h020_joint"]) - z012
        world_dir = logit(state["h048_world"]) - z012
        agree = np.sign(joint_dir) == np.sign(world_dir)
    else:
        agree = np.ones_like(group_mask, dtype=bool)

    if spec.family == "h042_support_rows":
        allowed_rows = h042_support
    elif spec.family == "support_union_rows":
        allowed_rows = h042_support | h047_support
    elif spec.family == "public_rows":
        allowed_rows = np.ones(n_rows, dtype=bool)
    else:
        allowed_rows = h042_support | h047_support

    allowed = group_mask & allowed_rows[:, None] & agree
    if not np.any(allowed):
        return None

    cell_score = np.abs(direction) * (0.18 + rank01(row_score)[:, None])
    cell_score *= allowed
    if spec.family.endswith("_rowtop"):
        take_rows = np.argsort(-np.nan_to_num(row_score, nan=-np.inf))[: min(spec.k, n_rows)]
        mask = np.zeros_like(allowed)
        mask[take_rows, :] = allowed[take_rows, :]
    else:
        flat = cell_score.reshape(-1)
        valid = np.where((flat > 0) & allowed.reshape(-1))[0]
        if len(valid) == 0:
            return None
        take = valid[np.argsort(-flat[valid])[: min(spec.k, len(valid))]]
        mask = np.zeros_like(allowed.reshape(-1), dtype=bool)
        mask[take] = True
        mask = mask.reshape(allowed.shape)

    z = z_base.copy()
    move = np.clip(direction * spec.alpha / max(spec.temperature, 1.0e-6), -0.85, 0.85)
    z[mask] = z_base[mask] + move[mask]
    z[:, Q2_I] = z_base[:, Q2_I]
    prob = sigmoid(z)

    changed_h042 = np.abs(prob - h042_prob) > 1.0e-7
    changed_h012 = np.abs(prob - h012_prob) > 1.0e-7
    non_q2_changed = int(np.sum(changed_h042[:, [i for i in range(len(TARGETS)) if i != Q2_I]]))
    if non_q2_changed == 0:
        return None

    candidate_id = safe_id(
        f"h049_{spec.family}_{spec.target_source}_{spec.unit}_{spec.group}_k{spec.k}_a{spec.alpha:g}_t{spec.temperature:g}_{short_hash(prob)}"
    )
    path = OUT / f"submission_{candidate_id}.csv"
    write_submission(sample, prob, path)

    route_delta, route_iqr = h042.expected_delta_for_prob(
        prob, h012_prob, state["rt"]["top_worlds"], state["rt"]["masks"], state["rt"]["labels"]
    )
    h012posterior = h042.pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = h042.pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    rec = {
        "candidate_id": candidate_id,
        "file": path.name,
        "resolved_path": str(path),
        "family": spec.family,
        "components": f"{spec.target_source}:{spec.unit}:{spec.group}",
        "component_count": 1,
        "target_source": spec.target_source,
        "unit": spec.unit,
        "target_group": spec.group,
        "k": spec.k,
        "alpha": spec.alpha,
        "temperature": spec.temperature,
        "require_agree": spec.require_agree,
        "changed_cells_vs_h012": int(changed_h012.sum()),
        "changed_rows_vs_h012": int(np.sum(np.max(changed_h012, axis=1))),
        "changed_cells_vs_h042": int(changed_h042.sum()),
        "changed_rows_vs_h042": int(np.sum(np.max(changed_h042, axis=1))),
        "non_q2_changed_cells_vs_h042": non_q2_changed,
        "q2_changed_cells_vs_h042": int(np.sum(changed_h042[:, Q2_I])),
        "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
        "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
        "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - z012))),
        "max_abs_logit_move_h012": float(np.max(np.abs(logit(prob) - z012))),
        "mean_abs_prob_move_h042": float(np.mean(np.abs(prob - h042_prob))),
        "max_abs_prob_move_h042": float(np.max(np.abs(prob - h042_prob))),
        "route_equation_delta_vs_h012": route_delta,
        "route_equation_delta_iqr": route_iqr,
        "h012posterior_delta_vs_h012": h042.weighted_delta(
            prob, h012_prob, h012posterior, np.abs(logit(h012posterior) - z012)
        ),
        "h036world_delta_vs_h012": h042.weighted_delta(prob, h012_prob, h036world, np.abs(logit(h036world) - z012)),
    }
    return rec, prob


def generate_candidates(rt: dict[str, object], state: dict[str, object]) -> pd.DataFrame:
    state["rt"] = rt
    row_scores = build_row_scores(state)
    targets = echo_targets(state)
    specs: list[EchoSpec] = []
    for source in ["joint_world_soft", "world_tempered", "joint_tempered"]:
        for unit in ["support_or_public", "public_not_private"]:
            for group in ["QS", "S", "Q3S"]:
                for family, ks in [
                    ("h042_support_rows", [18, 44, 78]),
                    ("support_union_rows", [24, 72, 132]),
                    ("public_rows", [32, 84, 160]),
                    ("support_union_rows_rowtop", [7, 16, 30]),
                ]:
                    for k in ks:
                        for alpha in [0.045, 0.085, 0.150]:
                            specs.append(EchoSpec(family, source, unit, group, k, alpha, 1.0, True))
    rows = []
    seen: set[str] = set()
    for spec in specs:
        out = materialize_candidate(spec, state, row_scores, targets[spec.target_source])
        if out is None:
            continue
        rec, _prob = out
        if rec["candidate_id"] in seen:
            continue
        seen.add(rec["candidate_id"])
        rows.append(rec)
    cand = pd.DataFrame(rows)
    if cand.empty:
        return cand
    cand["pre_echo_score"] = (
        cand["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        + 0.70 * cand["h036world_delta_vs_h012"].rank(method="average", pct=True)
        + 0.45 * cand["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        + 0.20 * cand["changed_cells_vs_h042"].rank(method="average", pct=True)
    )
    cand = cand.nsmallest(min(180, len(cand)), "pre_echo_score").reset_index(drop=True)
    cand.to_csv(OUT / "h049_generated_candidates.csv", index=False)
    return cand


def conditional_rescore(
    pool: pd.DataFrame,
    rt: dict[str, object],
    atoms: list[object],
    state: dict[str, object],
) -> pd.DataFrame:
    route = state["route"]
    known = h045.known_augmented_features(rt, atoms, state["h012_prob"], state["h042_prob"], state["h043_prob"], route)
    decoder_scores, _ = h045.evaluate_decoders(known)
    cand_features = h045.candidate_conditional_features(pool, rt, atoms, state["h012_prob"], state["h042_prob"], state["h043_prob"], route)
    pred = h045.predict_candidates(known, cand_features, decoder_scores)
    scored = h045.score_candidates(pool, pred)
    scored.to_csv(OUT / "h049_candidate_scores.csv", index=False)
    return scored


def select_candidate(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        dec = pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no scored candidate"}])
        dec.to_csv(OUT / "h049_decision.csv", index=False)
        return dec

    out = scored.copy()
    action_margin = out.get("full_known_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    cond_margin = out.get("full_known_cond_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    route = out["route_equation_delta_vs_h012"].fillna(0.01)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    h025 = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    changed = out["changed_cells_vs_h042"].fillna(999)
    support = out.get("full_known_cond_support_better_than_h012", pd.Series(0.0, index=out.index)).fillna(0.0)
    out["h049_echo_score"] = (
        1.10 * route.rank(method="average", pct=True)
        + 0.90 * action_margin.rank(method="average", pct=True)
        + 0.80 * cond_margin.rank(method="average", pct=True)
        + 0.40 * h025.rank(method="average", pct=True)
        + 0.24 * h024.rank(method="average", pct=True)
        + 0.12 * changed.rank(method="average", pct=True)
        - 0.35 * support
    )
    out["h049_worldview_promotable"] = (
        (out["non_q2_changed_cells_vs_h042"] >= 18)
        & (out["route_equation_delta_vs_h012"] < -0.00017)
        & (out["h036world_delta_vs_h012"] < -0.00011)
        & (out["full_known_action_margin_vs_h012_median"] < 0.00012)
        & (out["full_known_cond_margin_vs_h012_median"] < 0.00023)
        & (out["h025_score"] < -3.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.0017)
    )
    out = out.sort_values(["h049_worldview_promotable", "h049_echo_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h049_candidate_scores_ranked.csv", index=False)

    selected = out.iloc[0].copy()
    promote = bool(selected["h049_worldview_promotable"])
    src = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h049_rowvector_echo_{str(selected['candidate_id']).rsplit('_', 1)[-1]}_uploadsafe.csv"
    if promote:
        prob = h036.load_sub(src, sample)[TARGETS].to_numpy(dtype=np.float64)
        write_submission(sample, prob, root_path)

    dec = pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "diagnostic_only",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": src.name,
                "selected_resolved_path": str(src),
                "root_uploadsafe_path": str(root_path) if promote else "",
                "reason": "row-vector echo gate passed" if promote else "non-Q2 echo did not pass worldview gate",
                "expected_relation": "beats H042 only if Q2 support is a row-level hidden human-state marker",
                **{
                    col: selected.get(col, np.nan)
                    for col in [
                        "target_source",
                        "unit",
                        "target_group",
                        "changed_cells_vs_h012",
                        "changed_cells_vs_h042",
                        "non_q2_changed_cells_vs_h042",
                        "route_equation_delta_vs_h012",
                        "h036world_delta_vs_h012",
                        "full_known_action_margin_vs_h012_median",
                        "full_known_action_support_better_than_h012",
                        "full_known_cond_margin_vs_h012_median",
                        "full_known_cond_support_better_than_h012",
                        "pre_h012_h024_margin_vs_h012_median",
                        "h025_score",
                        "h049_echo_score",
                        "h049_worldview_promotable",
                    ]
                },
            }
        ]
    )
    dec.to_csv(OUT / "h049_decision.csv", index=False)
    return dec


def write_report(scored: pd.DataFrame, decision: pd.DataFrame) -> None:
    lines = [
        "# H049 Q2 Row-Vector Echo HS-JEPA",
        "",
        "Question: is the H042 Q2 phase support a row-level hidden human-state marker,",
        "or is it only Q2-local calibration?",
        "",
        "Design:",
        "",
        "- base = H042 current public best;",
        "- keep H042 Q2 exactly;",
        "- add non-Q2 Q/QS/S echoes only on Q2-support/public-row posterior rows;",
        "- echo target = H020 joint-vector posterior and H048 public-world posterior;",
        "- promote only if route/action/conditional/H025/H024 sensors do not jointly reject.",
        "",
        "Decision:",
        "",
        md_table(decision),
        "",
        "Top candidates:",
        "",
        md_table(
            scored[
                [
                    c
                    for c in [
                        "candidate_id",
                        "target_source",
                        "unit",
                        "target_group",
                        "changed_cells_vs_h042",
                        "non_q2_changed_cells_vs_h042",
                        "route_equation_delta_vs_h012",
                        "h036world_delta_vs_h012",
                        "full_known_action_margin_vs_h012_median",
                        "full_known_cond_margin_vs_h012_median",
                        "pre_h012_h024_margin_vs_h012_median",
                        "h025_score",
                        "h049_echo_score",
                        "h049_worldview_promotable",
                    ]
                    if c in scored.columns
                ]
            ],
            24,
        ),
        "",
        "Interpretation rule:",
        "",
        "- If a promoted file improves public LB, H042's Q2 support is a row-level",
        "  hidden human-state/public-subset marker and HS-JEPA should move to",
        "  vector-route action translation.",
        "- If it fails, Q2 phase remains a Q2-local action and non-Q2 target route",
        "  should not be inferred from the current support state.",
    ]
    (OUT / "h049_report.md").write_text("\n".join(lines) + "\n")


def validate_root(path: str) -> None:
    if not path:
        return
    df = pd.read_csv(path)
    required = KEYS + TARGETS
    if list(df.columns) != required:
        raise ValueError(f"bad columns: {list(df.columns)}")
    if df.isna().any().any():
        raise ValueError("NaN in submission")
    if df.duplicated(KEYS).any():
        raise ValueError("duplicate keys")
    vals = df[TARGETS].to_numpy(dtype=np.float64)
    if np.any(vals <= 0.0) or np.any(vals >= 1.0):
        raise ValueError("probability outside open interval")


def main() -> None:
    rt = h042.rebuild_route_world()
    state = load_state(rt)
    atoms = h042.build_atoms(rt)
    known_features = h042.build_action_feature_table(rt, atoms)
    decoder_scores, _ = h042.evaluate_action_decoders(known_features)
    candidates = generate_candidates(rt, state)
    scored_raw, _ = h042.score_candidates(rt, atoms, candidates, known_features, decoder_scores)
    scored = conditional_rescore(scored_raw, rt, atoms, state)
    decision = select_candidate(scored, state["sample"])
    write_report(scored, decision)
    root = str(decision.loc[0, "root_uploadsafe_path"]) if "root_uploadsafe_path" in decision.columns else ""
    validate_root(root)
    print("H049 selected:", decision.loc[0, "selected_candidate_id"])
    print("H049 decision:", decision.loc[0, "decision"])
    print("H049 reason:", decision.loc[0, "reason"])
    if root:
        print("H049 root:", root)


if __name__ == "__main__":
    main()
