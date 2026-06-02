#!/usr/bin/env python3
"""H050: target-route phase residual HS-JEPA.

H042 proved that a tiny Q2-only phase action is public-real. H049 then asked
whether that Q2 support can be translated into Q3/S row-vector echoes.

H050 asks a different, larger question:

    Was Q2 merely the first visible target-route phase, or are there other
    target-specific residual phases after H042?

The experiment starts from H042, freezes Q2 exactly, and searches target-route
phase actions on Q1/Q3/S1-S4. A win would mean HS-JEPA should model target
routes as separate hidden action channels, not as one row-vector echo.
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
OUT = HITL / "h050_target_route_phase_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
Q2_I = TARGETS.index("Q2")
NON_Q2_TARGETS = ["Q1", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H042_LB = 0.5679048248


@dataclass(frozen=True)
class PhaseSpec:
    family: str
    source: str
    target_group: str
    k: int
    alpha: float
    agree_only: bool


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h050")
h042 = import_module(HITL / "h042_action_coupled_equation_solver_jepa.py", "h042_for_h050")

# Reuse H042 sensors, but keep all helper output inside the H050 folder.
h042.OUT = OUT


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


def load_anchor_probs() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    h012 = pd.read_csv(ROOT / H012, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    h042_df = pd.read_csv(ROOT / H042, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    if not h012[KEYS].equals(h042_df[KEYS]):
        raise ValueError("H012 and H042 key order mismatch")
    return h012[KEYS].copy(), h012[TARGETS].to_numpy(dtype=np.float64), h042_df[TARGETS].to_numpy(dtype=np.float64)


def top_flat(score: np.ndarray, k: int, allowed: np.ndarray) -> np.ndarray:
    flat = np.nan_to_num(np.asarray(score, dtype=np.float64).reshape(-1), nan=-np.inf)
    ok = allowed.reshape(-1)
    flat = flat.copy()
    flat[~ok] = -np.inf
    valid = np.where(np.isfinite(flat))[0]
    take = valid[np.argsort(-flat[valid])[: min(k, len(valid))]]
    return take


def target_mask(target_group: str, n_rows: int) -> np.ndarray:
    group_map = {
        "Q1": ["Q1"],
        "Q3": ["Q3"],
        "S1": ["S1"],
        "S2": ["S2"],
        "S3": ["S3"],
        "S4": ["S4"],
        "Q": ["Q1", "Q3"],
        "S": ["S1", "S2", "S3", "S4"],
        "S13": ["S1", "S3"],
        "S24": ["S2", "S4"],
        "Q3S3": ["Q3", "S3"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
        "ALL_NON_Q2": NON_Q2_TARGETS,
    }
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for target in group_map[target_group]:
        mask[:, TARGETS.index(target)] = True
    return mask


def build_phase_state(rt: dict[str, object], sample: pd.DataFrame, h012_prob: np.ndarray) -> dict[str, object]:
    e247 = rt["e247_prob"]
    h012post = h042.pivot_cells(HITL / "h012_public_equation_jepa_jackpot" / "h012_cell_posterior.csv", "posterior_prob", sample)
    h036world = h042.pivot_cells(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv", "world_q_cond", sample)
    h041world_path = HITL / "h041_route_prior_equation_solver_jepa" / "h041_route_world_posterior_cells.csv"
    if h041world_path.exists():
        h041world = h042.pivot_cells(h041world_path, "world_q_cond", sample)
    else:
        h041world = rt["q_cond"]

    route = rt["route"].sort_values("row").reset_index(drop=True)
    z_h012 = logit(h012_prob)
    z_e247 = logit(e247)
    z_cond = logit(rt["q_cond"])
    z_post = logit(h012post)
    z_h036 = logit(h036world)
    z_h041 = logit(h041world)

    sources = {
        "route_phase": 0.52 * z_cond + 0.24 * z_post + 0.24 * z_h036,
        "world_phase": 0.56 * z_h036 + 0.24 * z_cond + 0.20 * z_h012,
        "route_world_mid": 0.40 * z_cond + 0.35 * z_h041 + 0.25 * z_h036,
        "posterior_mid": 0.45 * z_post + 0.35 * z_cond + 0.20 * z_h036,
    }

    public = route["public_route_score"].to_numpy(dtype=np.float64)[:, None]
    private = route["private_memory_route_score"].to_numpy(dtype=np.float64)[:, None]
    transition = route["transition_exception_route_score"].to_numpy(dtype=np.float64)[:, None]
    row_public = np.asarray(rt["row_post"], dtype=np.float64)[:, None]
    support = np.abs(z_h012 - z_e247) > 1.0e-8
    world_abs = np.abs(z_cond - z_h012)
    public_score = row_public * (0.45 + public) * (0.65 + transition) * world_abs * (1.18 - 0.38 * private)
    ray = z_h012 - z_e247
    source_scores = {}
    source_allowed = {}
    for name, z_target in sources.items():
        direction = z_target - z_h012
        agree = np.sign(direction) == np.sign(ray)
        source_scores[name] = public_score * (0.65 + 0.35 * agree.astype(float)) * np.abs(direction)
        source_allowed[name] = support & (np.abs(direction) > 1.0e-8)
    return {
        "h012post": h012post,
        "h036world": h036world,
        "z_h012": z_h012,
        "sources": sources,
        "scores": source_scores,
        "allowed": source_allowed,
        "agree": {name: np.sign(z_target - z_h012) == np.sign(ray) for name, z_target in sources.items()},
    }


def materialize_candidates(
    rt: dict[str, object],
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    state: dict[str, object],
) -> pd.DataFrame:
    z_base = logit(h042_prob)
    z_h012 = state["z_h012"]
    generated: set[str] = set()
    rows: list[dict[str, object]] = []

    h042_changed = np.abs(h042_prob - h012_prob) > 1.0e-7
    h042_route_delta, _ = h042.expected_delta_for_prob(h042_prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])

    def build(spec: PhaseSpec) -> None:
        z_target = state["sources"][spec.source]
        score = state["scores"][spec.source]
        allowed = state["allowed"][spec.source] & target_mask(spec.target_group, len(sample))
        allowed[:, Q2_I] = False
        if spec.agree_only:
            allowed &= state["agree"][spec.source]
        take = top_flat(score, spec.k, allowed)
        if len(take) == 0:
            return
        z = z_base.copy()
        flat_z = z.reshape(-1)
        flat_base = z_base.reshape(-1)
        flat_target = z_target.reshape(-1)
        flat_z[take] = flat_base[take] + spec.alpha * (flat_target[take] - z_h012.reshape(-1)[take])
        move = np.clip(z - z_base, -1.35, 1.35)
        prob = sigmoid(z_base + move)
        changed_h012 = np.abs(prob - h012_prob) > 1.0e-7
        changed_h042 = np.abs(prob - h042_prob) > 1.0e-7
        if int(changed_h042.sum()) == 0:
            return
        cid = safe_id(
            f"h050_{spec.family}_{spec.source}_{spec.target_group}_k{spec.k}_a{spec.alpha:g}_"
            f"{'agree' if spec.agree_only else 'free'}_{short_hash(prob)}"
        )
        if cid in generated:
            return
        generated.add(cid)
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        route_delta, route_disp = h042.expected_delta_for_prob(prob, h012_prob, rt["top_worlds"], rt["masks"], rt["labels"])
        rows.append(
            {
                "candidate_id": cid,
                "file": path.name,
                "resolved_path": str(path),
                "family": spec.family,
                "components": f"{spec.source}:{spec.target_group}:k{spec.k}:a{spec.alpha:g}:{'agree' if spec.agree_only else 'free'}",
                "component_count": 1,
                "source": spec.source,
                "target_group": spec.target_group,
                "k": spec.k,
                "alpha": spec.alpha,
                "agree_only": spec.agree_only,
                "changed_cells_vs_h012": int(changed_h012.sum()),
                "changed_rows_vs_h012": int(np.max(changed_h012, axis=1).sum()),
                "changed_cells_vs_h042": int(changed_h042.sum()),
                "changed_rows_vs_h042": int(np.max(changed_h042, axis=1).sum()),
                "q2_changed_cells_vs_h042": int(changed_h042[:, Q2_I].sum()),
                "non_q2_changed_cells_vs_h042": int(changed_h042.sum() - changed_h042[:, Q2_I].sum()),
                "h042_overlap_cells": int(np.logical_and(changed_h012, h042_changed).sum()),
                "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - logit(h012_prob)))),
                "max_abs_logit_move_h012": float(np.max(np.abs(logit(prob) - logit(h012_prob)))),
                "mean_abs_prob_move_h042": float(np.mean(np.abs(prob - h042_prob))),
                "max_abs_prob_move_h042": float(np.max(np.abs(prob - h042_prob))),
                "route_equation_delta_vs_h012": route_delta,
                "route_delta_gain_vs_h042": float(route_delta - h042_route_delta),
                "route_equation_delta_iqr": route_disp,
                "h012posterior_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h012post"], np.abs(logit(state["h012post"]) - logit(h012_prob))
                ),
                "h036world_delta_vs_h012": h042.weighted_delta(
                    prob, h012_prob, state["h036world"], np.abs(logit(state["h036world"]) - logit(h012_prob))
                ),
            }
        )

    specs: list[PhaseSpec] = []
    single_targets = ["Q1", "Q3", "S1", "S2", "S3", "S4"]
    groups = single_targets + ["Q", "S", "S13", "S24", "Q3S3", "Q3S", "ALL_NON_Q2"]
    for source in ["route_phase", "world_phase", "route_world_mid", "posterior_mid"]:
        for group in groups:
            ks = [12, 24, 45, 70, 110] if group in single_targets else [28, 56, 96, 150, 220]
            for k in ks:
                for alpha in [0.04, 0.075, 0.12, 0.19, 0.30]:
                    specs.append(PhaseSpec("target_phase", source, group, k, alpha, True))
                    if alpha in [0.075, 0.19]:
                        specs.append(PhaseSpec("target_phase", source, group, k, alpha, False))

    # Add a few deliberately larger target-route claims. These are not safe
    # tweaks; they test whether objective-stage targets have their own phase.
    for source in ["world_phase", "route_world_mid"]:
        for group in ["S", "Q3S", "ALL_NON_Q2"]:
            for k in [260, 340]:
                for alpha in [0.075, 0.12]:
                    specs.append(PhaseSpec("large_route_phase", source, group, k, alpha, True))

    for spec in specs:
        build(spec)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["pre_score"] = (
        out["route_equation_delta_vs_h012"].rank(method="average", pct=True)
        + 0.55 * out["route_delta_gain_vs_h042"].rank(method="average", pct=True)
        + 0.45 * out["h036world_delta_vs_h012"].rank(method="average", pct=True)
        + 0.25 * out["mean_abs_prob_move_h042"].rank(method="average", pct=True)
    )
    out = out.nsmallest(min(360, len(out)), "pre_score").reset_index(drop=True)
    out.to_csv(OUT / "h050_generated_candidates.csv", index=False)
    return out


def known_features_with_h042(rt: dict[str, object], atoms: list[object], h042_prob: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    known = h042.build_action_feature_table(rt, atoms)
    h042_row = h042.action_features(h042_prob, rt, atoms, H042, "known_public_h042")
    h042_row["public_lb"] = H042_LB
    h042_row["delta_vs_h012"] = H042_LB - h042.H012_LB
    known_aug = pd.concat([known, pd.DataFrame([h042_row])], ignore_index=True)
    known_aug = known_aug.drop_duplicates("file", keep="last").reset_index(drop=True)
    known_aug.to_csv(OUT / "h050_known_action_features_with_h042.csv", index=False)
    decoder_scores, _decoder_loo = h042.evaluate_action_decoders(known_aug)
    return known_aug, decoder_scores


def score_h050(scored_raw: pd.DataFrame, generated: pd.DataFrame) -> pd.DataFrame:
    if scored_raw.empty:
        return scored_raw
    cols = [
        "candidate_id",
        "source",
        "target_group",
        "k",
        "alpha",
        "agree_only",
        "changed_cells_vs_h042",
        "changed_rows_vs_h042",
        "q2_changed_cells_vs_h042",
        "non_q2_changed_cells_vs_h042",
        "route_delta_gain_vs_h042",
        "mean_abs_prob_move_h042",
        "max_abs_prob_move_h042",
    ]
    out = scored_raw.merge(generated[cols], on="candidate_id", how="left", suffixes=("", "_gen"))
    full_action = out.get("full_known_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    full_support = out.get("full_known_action_support_better_than_h012", pd.Series(0.0, index=out.index)).fillna(0.0)
    pre_action = out.get("pre_h012_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    route_gain = out["route_delta_gain_vs_h042"].fillna(0.01)
    route = out["route_equation_delta_vs_h012"].fillna(0.01)
    h036world = out["h036world_delta_vs_h012"].fillna(0.01)
    h025 = out.get("h025_score", pd.Series(2.0, index=out.index)).fillna(2.0)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.02, index=out.index)).fillna(0.02)
    changed = out["non_q2_changed_cells_vs_h042"].fillna(999)
    out["h050_target_route_score"] = (
        0.78 * full_action.rank(method="average", pct=True)
        + 0.58 * route_gain.rank(method="average", pct=True)
        + 0.50 * route.rank(method="average", pct=True)
        + 0.40 * h036world.rank(method="average", pct=True)
        + 0.32 * h025.rank(method="average", pct=True)
        + 0.18 * h024.rank(method="average", pct=True)
        + 0.12 * changed.rank(method="average", pct=True)
        + 0.18 * pre_action.rank(method="average", pct=True)
        - 0.28 * full_support
    )
    out["h050_worldview_promotable"] = (
        (out["q2_changed_cells_vs_h042"] == 0)
        & (out["non_q2_changed_cells_vs_h042"] >= 20)
        & (out["non_q2_changed_cells_vs_h042"] <= 260)
        & (out["route_delta_gain_vs_h042"] < -0.000015)
        & (out["route_equation_delta_vs_h012"] < -0.000150)
        & (out["full_known_action_support_better_than_h012"] >= 0.50)
        & (out["h025_score"] < 0.75)
    )
    # H024 stays a warning, not a hard veto, because H042 proved H024 can reject
    # a public-real target-isolated phase.
    out = out.sort_values(
        ["h050_worldview_promotable", "h050_target_route_score", "route_delta_gain_vs_h042"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    out.to_csv(OUT / "h050_candidate_scores.csv", index=False)
    out.head(80).to_csv(OUT / "h050_candidate_scores_ranked.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        out = pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no generated candidates"}])
        out.to_csv(OUT / "h050_decision.csv", index=False)
        return out
    selected = scored.iloc[0].copy()
    source = Path(str(selected["resolved_path"]))
    promote = bool(selected.get("h050_worldview_promotable", False))
    reason = "target-route residual gate passed" if promote else "no candidate passed H050 target-route gate"
    root_path = ROOT / f"submission_h050_target_route_phase_{short_hash(h036.load_sub(str(source), sample)[TARGETS].to_numpy(dtype=np.float64))}_uploadsafe.csv"
    if promote:
        shutil.copy2(source, root_path)
    out = pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": source.name,
                "selected_resolved_path": str(source),
                "root_uploadsafe_path": str(root_path) if promote else "",
                "reason": reason,
                "expected_relation": "beats H042 only if non-Q2 target-route phase exists after Q2 is frozen",
                **{
                    col: selected.get(col, np.nan)
                    for col in [
                        "source",
                        "target_group",
                        "k",
                        "alpha",
                        "agree_only",
                        "changed_cells_vs_h012",
                        "changed_cells_vs_h042",
                        "non_q2_changed_cells_vs_h042",
                        "route_equation_delta_vs_h012",
                        "route_delta_gain_vs_h042",
                        "h036world_delta_vs_h012",
                        "full_known_action_margin_vs_h012_median",
                        "full_known_action_support_better_than_h012",
                        "pre_h012_action_margin_vs_h012_median",
                        "pre_h012_h024_margin_vs_h012_median",
                        "pre_h012_h024_support_better_than_h012",
                        "h025_score",
                        "h050_target_route_score",
                        "h050_worldview_promotable",
                    ]
                },
            }
        ]
    )
    out.to_csv(OUT / "h050_decision.csv", index=False)
    return out


def write_report(scored: pd.DataFrame, decision: pd.DataFrame, decoder_scores: pd.DataFrame) -> None:
    top_cols = [
        "candidate_id",
        "source",
        "target_group",
        "k",
        "alpha",
        "changed_cells_vs_h042",
        "route_delta_gain_vs_h042",
        "route_equation_delta_vs_h012",
        "full_known_action_margin_vs_h012_median",
        "full_known_action_support_better_than_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "h025_score",
        "h050_target_route_score",
        "h050_worldview_promotable",
    ]
    lines = [
        "# H050 Target-Route Phase Residual HS-JEPA",
        "",
        "Question: after the H042 Q2 phase win, do non-Q2 target routes have their own public-relevant residual phase?",
        "",
        "Design:",
        "",
        "- base = H042 current public best;",
        "- freeze Q2 exactly;",
        "- generate Q1/Q3/S1-S4 target-phase actions from route/world/posterior sources;",
        "- score with H042 action decoder after adding H042 public feedback, route-world equation, H024, and H025.",
        "",
        "Decision:",
        "",
        md_table(decision),
        "",
        "Top decoder fits after adding H042 public feedback:",
        "",
        md_table(decoder_scores.head(8)),
        "",
        "Top candidates:",
        "",
        md_table(scored[[c for c in top_cols if c in scored.columns]].head(24) if not scored.empty else scored),
        "",
        "Interpretation rule:",
        "",
        "- If the promoted file improves public LB, HS-JEPA needs target-specific action routes beyond Q2.",
        "- If it fails materially, H042 remains a Q2-local phase result and non-Q2 action should require an independent route signal.",
        "",
    ]
    (OUT / "h050_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob = load_anchor_probs()
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = build_phase_state(rt, sample, h012_prob)
    generated = materialize_candidates(rt, sample, h012_prob, h042_prob, state)
    known_aug, decoder_scores = known_features_with_h042(rt, atoms, h042_prob)
    scored_raw, _h025 = h042.score_candidates(rt, atoms, generated, known_aug, decoder_scores)
    scored = score_h050(scored_raw, generated)
    decision = select_and_copy(scored, sample)
    write_report(scored, decision, decoder_scores)
    print("H050 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H050 decision:", decision.iloc[0]["decision"])
    print("H050 reason:", decision.iloc[0]["reason"])
    if str(decision.iloc[0].get("root_uploadsafe_path", "")):
        print("H050 root:", decision.iloc[0]["root_uploadsafe_path"])


if __name__ == "__main__":
    main()
