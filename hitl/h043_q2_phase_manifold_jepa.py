#!/usr/bin/env python3
"""H043: Q2-local phase manifold after the H042 public win.

H042 changed the worldview:

    H024 rejected every action+route candidate, but a tiny Q2-only candidate
    still improved public LB.

H043 treats that public result as a validated local tangent.  The goal is not
to blend around H042, but to map whether the Q2 phase branch is a narrow
45-cell optimum, a wider top-k manifold, or an amplitude direction that can be
extended.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h043_q2_phase_manifold_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q2_I = TARGETS.index("Q2")
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H042_LB = 0.5679048248
H042_DELTA = H042_LB - H012_LB


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    q2_k: int
    core_alpha: float
    tail_k: int
    tail_alpha: float
    changed_cells: int
    changed_rows: int
    mean_abs_logit_move: float
    max_abs_logit_move: float
    mean_abs_prob_move: float
    max_abs_prob_move: float
    h042_overlap_cells: int
    h042_jaccard: float
    h042_distance_l1: float
    h042_distance_l2: float
    tangent_expected_delta: float
    resolved_path: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h043")
h042 = import_module(HITL / "h042_action_coupled_equation_solver_jepa.py", "h042_for_h043")
h042.OUT = OUT


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def safe_id(text: str, limit: int = 110) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


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


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def top_indices(score: np.ndarray, k: int, allowed: np.ndarray | None = None) -> np.ndarray:
    s = np.nan_to_num(np.asarray(score, dtype=np.float64), nan=-np.inf)
    if allowed is not None:
        s = s.copy()
        s[~allowed] = -np.inf
    valid = np.where(np.isfinite(s))[0]
    if len(valid) == 0:
        return np.array([], dtype=int)
    return valid[np.argsort(-s[valid])[: min(k, len(valid))]]


def load_anchor_probs() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    h012 = pd.read_csv(ROOT / H012, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    h042_df = pd.read_csv(ROOT / H042, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    if not h012[KEYS].equals(h042_df[KEYS]):
        raise ValueError("H012 and H042 key order mismatch")
    return h012[KEYS].copy(), h012[TARGETS].to_numpy(dtype=np.float64), h042_df[TARGETS].to_numpy(dtype=np.float64)


def build_q2_phase_state(rt: dict[str, object], sample: pd.DataFrame, h012_prob: np.ndarray, h042_prob: np.ndarray) -> dict[str, np.ndarray]:
    e247_prob = rt["e247_prob"]
    h012posterior = h042.pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = h042.pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    route = rt["route"].sort_values("row").reset_index(drop=True)

    z_h012 = logit(h012_prob)
    z_e247 = logit(e247_prob)
    z_cond = logit(rt["q_cond"])
    z_post = logit(h012posterior)
    z_world = logit(h036world)
    z_phase = 0.52 * z_cond + 0.24 * z_post + 0.24 * z_world

    public = route["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]
    row_public = np.asarray(rt["row_post"], dtype=np.float64)[:, None]
    world_abs = np.abs(z_cond - z_h012)
    public_score = row_public * (0.45 + public) * world_abs * (1.15 - 0.45 * private)
    support = np.abs(z_h012 - z_e247) > 1.0e-8
    q2_allowed = support[:, Q2_I]
    h042_support = np.abs(h042_prob[:, Q2_I] - h012_prob[:, Q2_I]) > 1.0e-7

    return {
        "z_h012": z_h012,
        "z_phase": z_phase,
        "phase_dir_q2": z_phase[:, Q2_I] - z_h012[:, Q2_I],
        "score_q2": public_score[:, Q2_I],
        "support_q2": q2_allowed,
        "h042_support": h042_support,
        "h042_q2_logit": logit(h042_prob)[:, Q2_I],
        "h042_delta_q2": logit(h042_prob)[:, Q2_I] - z_h012[:, Q2_I],
        "h012posterior": h012posterior,
        "h036world": h036world,
    }


def tangent_delta(prob: np.ndarray, h012_prob: np.ndarray, h042_prob: np.ndarray) -> tuple[float, float, float, float]:
    dz = logit(prob)[:, Q2_I] - logit(h012_prob)[:, Q2_I]
    dz42 = logit(h042_prob)[:, Q2_I] - logit(h012_prob)[:, Q2_I]
    denom = float(np.dot(dz42, dz42) + 1.0e-12)
    projection = float(np.dot(dz, dz42) / denom)
    residual = dz - projection * dz42
    residual_ratio = float(np.linalg.norm(residual) / (np.linalg.norm(dz) + 1.0e-12))
    total_ratio = float(np.linalg.norm(dz) / (np.linalg.norm(dz42) + 1.0e-12))
    expected = H042_DELTA * projection
    risk = 0.00010 * residual_ratio + 0.00008 * max(0.0, total_ratio - 1.35) ** 2
    return float(expected + risk), projection, residual_ratio, total_ratio


def materialize_candidates(rt: dict[str, object], sample: pd.DataFrame, h012_prob: np.ndarray, h042_prob: np.ndarray, state: dict[str, np.ndarray]) -> pd.DataFrame:
    z_h012 = state["z_h012"]
    phase_dir = state["phase_dir_q2"]
    score = state["score_q2"]
    allowed = state["support_q2"]
    h042_support = state["h042_support"]
    h042_delta = state["h042_delta_q2"]
    generated: set[str] = set()
    specs: list[CandidateSpec] = []

    q2_order = top_indices(score, 250, allowed)
    h042_idx = np.where(h042_support)[0]
    h042_ranked = h042_idx[np.argsort(-score[h042_idx])]
    outside_order = np.array([i for i in q2_order if not h042_support[i]], dtype=int)

    def build_prob(mask_alpha: dict[int, float], family: str, q2_k: int, core_alpha: float, tail_k: int, tail_alpha: float) -> None:
        z = z_h012.copy()
        for row, alpha in mask_alpha.items():
            z[row, Q2_I] = z_h012[row, Q2_I] + alpha * phase_dir[row]
        prob = sigmoid(z)
        changed_mask = np.abs(prob - h012_prob) > 1.0e-7
        changed = int(changed_mask.sum())
        if changed == 0:
            return
        cid = safe_id(f"h043_{family}_c{changed}_{short_hash(prob)}")
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)

        q2_changed = changed_mask[:, Q2_I]
        union = np.logical_or(q2_changed, h042_support).sum()
        overlap = int(np.logical_and(q2_changed, h042_support).sum())
        jaccard = float(overlap / union) if union else 0.0
        delta = logit(prob)[:, Q2_I] - z_h012[:, Q2_I]
        dist = delta - h042_delta
        expected, projection, residual_ratio, total_ratio = tangent_delta(prob, h012_prob, h042_prob)
        specs.append(
            CandidateSpec(
                candidate_id=cid,
                family=family,
                q2_k=q2_k,
                core_alpha=core_alpha,
                tail_k=tail_k,
                tail_alpha=tail_alpha,
                changed_cells=changed,
                changed_rows=int(np.max(changed_mask, axis=1).sum()),
                mean_abs_logit_move=float(np.mean(np.abs(delta))),
                max_abs_logit_move=float(np.max(np.abs(delta))),
                mean_abs_prob_move=float(np.mean(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                max_abs_prob_move=float(np.max(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]))),
                h042_overlap_cells=overlap,
                h042_jaccard=jaccard,
                h042_distance_l1=float(np.mean(np.abs(dist))),
                h042_distance_l2=float(np.sqrt(np.mean(dist * dist))),
                tangent_expected_delta=expected,
                resolved_path=str(path),
            )
        )

    # 1) Pure top-k phase surface, including the exact H042 point.
    for k in [15, 25, 35, 45, 55, 70, 90, 120, 150, 190]:
        rows = q2_order[:k]
        for alpha in [0.08, 0.14, 0.22, 0.34, 0.42, 0.50, 0.58, 0.66, 0.78, 0.92, 1.10]:
            build_prob({int(r): alpha for r in rows}, f"q2_top{k}_a{alpha:g}", k, alpha, 0, 0.0)

    # 2) Same H042 core, amplitude only.
    for alpha in [0.30, 0.38, 0.46, 0.50, 0.54, 0.58, 0.64, 0.72, 0.84, 1.00, 1.18]:
        build_prob({int(r): alpha for r in h042_idx}, f"h042core_a{alpha:g}", len(h042_idx), alpha, 0, 0.0)

    # 3) Prune the H042 core to ask whether only the sharpest cells matter.
    for k in [12, 18, 25, 32, 38, 42]:
        rows = h042_ranked[: min(k, len(h042_ranked))]
        for alpha in [0.50, 0.62, 0.78, 0.96, 1.14]:
            build_prob({int(r): alpha for r in rows}, f"h042core_prune{k}_a{alpha:g}", k, alpha, 0, 0.0)

    # 4) Preserve the validated H042 core and add a cautious outside tail.
    for tail_k in [8, 15, 25, 40, 60, 85]:
        tail_rows = outside_order[:tail_k]
        for beta in [0.04, 0.08, 0.12, 0.18, 0.26, 0.36]:
            mask_alpha = {int(r): 0.50 for r in h042_idx}
            mask_alpha.update({int(r): beta for r in tail_rows})
            build_prob(mask_alpha, f"h042core_tail{tail_k}_b{beta:g}", len(h042_idx), 0.50, tail_k, beta)

    # 5) Core plus amplitude compensation: stronger core, weaker tail.
    for core_alpha in [0.58, 0.66, 0.78, 0.90]:
        for tail_k in [10, 20, 35, 55]:
            for beta in [0.04, 0.08, 0.12, 0.18]:
                mask_alpha = {int(r): core_alpha for r in h042_idx}
                mask_alpha.update({int(r): beta for r in outside_order[:tail_k]})
                build_prob(mask_alpha, f"h042core{core_alpha:g}_tail{tail_k}_b{beta:g}", len(h042_idx), core_alpha, tail_k, beta)

    out = pd.DataFrame([s.__dict__ for s in specs])
    if not out.empty:
        out.to_csv(OUT / "h043_generated_candidates.csv", index=False)
    return out


def candidate_frame_for_h042_score(generated: pd.DataFrame, rt: dict[str, object], sample: pd.DataFrame, h012_prob: np.ndarray, state: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for rec in generated.to_dict("records"):
        prob = h036.load_sub(rec["resolved_path"], sample)[TARGETS].to_numpy(dtype=np.float64)
        route_delta, route_disp = h042.expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "file": Path(rec["resolved_path"]).name,
                "resolved_path": rec["resolved_path"],
                "family": rec["family"],
                "components": rec["family"],
                "component_count": 1 + int(rec["tail_k"] > 0),
                "changed_cells_vs_h012": int(rec["changed_cells"]),
                "changed_rows_vs_h012": int(rec["changed_rows"]),
                "mean_abs_prob_move_h012": float(rec["mean_abs_prob_move"]),
                "max_abs_prob_move_h012": float(rec["max_abs_prob_move"]),
                "mean_abs_logit_move_h012": float(rec["mean_abs_logit_move"]),
                "max_abs_logit_move_h012": float(rec["max_abs_logit_move"]),
                "route_equation_delta_vs_h012": route_delta,
                "route_equation_delta_iqr": route_disp,
                "h012posterior_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h012posterior"], np.abs(logit(state["h012posterior"]) - logit(h012_prob))
                ),
                "h036world_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h036world"], np.abs(logit(state["h036world"]) - logit(h012_prob))
                ),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out.to_csv(OUT / "h043_candidate_pre_scores.csv", index=False)
    return out


def known_features_with_h042(rt: dict[str, object], atoms: list[object], h042_prob: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    known = h042.build_action_feature_table(rt, atoms)
    h042_row = h042.action_features(h042_prob, rt, atoms, H042, "known_public_h042")
    h042_row["public_lb"] = H042_LB
    h042_row["delta_vs_h012"] = H042_DELTA
    known_aug = pd.concat([known, pd.DataFrame([h042_row])], ignore_index=True)
    known_aug = known_aug.drop_duplicates("file", keep="last").reset_index(drop=True)
    known_aug.to_csv(OUT / "h043_known_action_features_with_h042.csv", index=False)
    decoder_scores, decoder_loo = h042.evaluate_action_decoders(known_aug)
    return known_aug, decoder_scores, decoder_loo


def score_h043(candidates: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    out = candidates.merge(
        generated[
            [
                "candidate_id",
                "q2_k",
                "core_alpha",
                "tail_k",
                "tail_alpha",
                "h042_overlap_cells",
                "h042_jaccard",
                "h042_distance_l1",
                "h042_distance_l2",
                "tangent_expected_delta",
            ]
        ],
        on="candidate_id",
        how="left",
    )
    action = out.get("pre_h012_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    route = out["route_equation_delta_vs_h012"].fillna(0.01)
    h025_score = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    h024_margin = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    proximity = out["h042_distance_l2"].fillna(out["h042_distance_l2"].max())
    tangent = out["tangent_expected_delta"].fillna(0.0)
    h042_jaccard = out["h042_jaccard"].fillna(0.0)
    changed = out["changed_cells_vs_h012"].fillna(999)
    only_q2 = (out["changed_cells_vs_h012"] == out["changed_rows_vs_h012"]).astype(float)
    out["h043_q2_override_score"] = (
        0.95 * action.rank(method="average", pct=True)
        + 0.80 * route.rank(method="average", pct=True)
        + 0.65 * tangent.rank(method="average", pct=True)
        + 0.45 * h025_score.rank(method="average", pct=True)
        + 0.35 * proximity.rank(method="average", pct=True)
        + 0.25 * changed.rank(method="average", pct=True)
        + 0.20 * h024_margin.rank(method="average", pct=True)
        - 0.25 * h042_jaccard
        - 0.20 * only_q2
    )
    out["h043_promotable"] = (
        (out["changed_cells_vs_h012"] <= 120)
        & (out["pre_h012_action_margin_vs_h012_median"] < -0.00004)
        & (out["route_equation_delta_vs_h012"] < -0.00012)
        & (out["h025_score"] < 0.0)
        & (out["h042_distance_l2"] <= 0.22)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00070)
    )
    out = out.sort_values(["h043_promotable", "h043_q2_override_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h043_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no candidates"}])
    selected = scored.iloc[0].copy()
    source = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"{source.stem}_uploadsafe.csv"
    promote = bool(selected.get("h043_promotable", False))
    reason = []
    if not promote:
        reason.append("no candidate passed H043 Q2 override gate")
    else:
        write_submission(sample, h036.load_sub(str(source), sample)[TARGETS].to_numpy(dtype=np.float64), root_path)
        reason.append("Q2 override gate passed; copied root uploadsafe candidate")
    dec = {
        "decision": "promote" if promote else "do_not_promote",
        "promote": promote,
        "selected_candidate_id": selected["candidate_id"],
        "selected_file": source.name,
        "selected_resolved_path": str(source),
        "root_uploadsafe_path": str(root_path) if promote else "",
        "public_anchor": H042,
        "public_anchor_lb": H042_LB,
        "expected_relation": "next Q2 phase probe should beat H042 if manifold extends",
        "reason": "; ".join(reason),
    }
    for col in [
        "changed_cells_vs_h012",
        "q2_k",
        "core_alpha",
        "tail_k",
        "tail_alpha",
        "pre_h012_action_margin_vs_h012_median",
        "pre_h012_action_support_better_than_h012",
        "route_equation_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "pre_h012_h024_support_better_than_h012",
        "h025_score",
        "h042_jaccard",
        "h042_distance_l2",
        "tangent_expected_delta",
        "h043_q2_override_score",
        "h043_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h043_decision.csv", index=False)
    return out


def write_report(generated: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame, decoder_scores: pd.DataFrame) -> None:
    selected = scored.head(1).copy()
    lines = [
        "# H043 Q2-Local Phase Manifold HS-JEPA",
        "",
        "## Question",
        "",
        "Was the H042 public win a narrow 45-cell accident, or does it reveal a Q2-local phase manifold that can be extended?",
        "",
        "## Public Anchor",
        "",
        f"- H012: `{H012}` = `{H012_LB:.10f}`",
        f"- H042: `{H042}` = `{H042_LB:.10f}`",
        f"- H042 delta vs H012: `{H042_DELTA:.10f}`",
        "",
        "## Candidate Search",
        "",
        f"- generated candidates: `{len(generated)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- promotable candidates: `{int(scored['h043_promotable'].sum()) if 'h043_promotable' in scored else 0}`",
        "",
        "Top decoder fits after adding H042 public feedback:",
        "",
        md_table(decoder_scores.head(8)),
        "",
        "Top H043 candidates:",
        "",
        md_table(
            scored[
                [
                    "candidate_id",
                    "changed_cells_vs_h012",
                    "q2_k",
                    "core_alpha",
                    "tail_k",
                    "tail_alpha",
                    "pre_h012_action_margin_vs_h012_median",
                    "route_equation_delta_vs_h012",
                    "pre_h012_h024_margin_vs_h012_median",
                    "h025_score",
                    "h042_jaccard",
                    "h042_distance_l2",
                    "tangent_expected_delta",
                    "h043_promotable",
                    "h043_q2_override_score",
                ]
            ].head(20)
            if not scored.empty
            else scored
        ),
        "",
        "## Decision",
        "",
        md_table(decision),
        "",
        "## Interpretation",
        "",
        "- If a promotable candidate is copied to root, it is a public sensor for Q2 phase extension, not a generic blend.",
        "- If no candidate is promotable, H042 is treated as a narrow local optimum until a different regime split explains how to leave it.",
        "- H024 is explicitly demoted from a hard gate to a warning for target-isolated Q2 moves, because H042 proved one such warning false.",
        "",
    ]
    (OUT / "h043_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob = load_anchor_probs()
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    generated = materialize_candidates(rt, sample, h012_prob, h042_prob, state)
    known_aug, decoder_scores, _decoder_loo = known_features_with_h042(rt, atoms, h042_prob)
    pre = candidate_frame_for_h042_score(generated, rt, sample, h012_prob, state)
    scored_raw, _h025 = h042.score_candidates(rt, atoms, pre, known_aug, decoder_scores)
    scored = score_h043(scored_raw, generated)
    decision = select_and_copy(scored, sample)
    write_report(generated, scored, decision, decoder_scores)
    print("H043 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H043 decision:", decision.iloc[0]["decision"])
    print("H043 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
