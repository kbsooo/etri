#!/usr/bin/env python3
"""H081: conflict-ridge HS-JEPA.

H080 showed that multi-view invariant consensus is safe but too weak: the best
candidate only reached a predicted public-action delta around -0.000656.

The hidden clue in H080 is the opposite set: cells where the public-action
sensor is strongly positive while the q061 posterior is strongly negative.
H077 found this sparsely. H081 asks whether that conflict is itself a hidden
public/private ridge.

If H081 wins, q061 is not a universal posterior guardrail. It is wrong on a
public-tail route. If H081 loses, the conflict ridge is sensor overfit and
future HS-JEPA decoders must keep q061/posterior as a hard constraint.
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
H080_OUT = HITL / "h080_invariant_action_core_jepa"
OUT = HITL / "h081_conflict_ridge_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12


@dataclass(frozen=True)
class H081Spec:
    name: str
    target_group: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_sources: int
    min_families: int
    min_action_gain: float
    min_posterior_conflict: float
    max_bad_same_rank: float
    h079_mode: str
    outside_h069: bool
    alpha: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H080MOD = import_module(HITL / "h080_invariant_action_core_jepa.py", "h080mod_for_h081")
H071MOD = H080MOD.H071MOD


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H071MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def logit(x: np.ndarray) -> np.ndarray:
    return H071MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H071MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H071MOD.bce(prob, q)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H071MOD.clip_prob(x)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h081_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h081_conflict_ridge_*_uploadsafe.csv"):
        path.unlink()


def target_group(name: str) -> list[str]:
    if name == "all":
        return list(TARGETS)
    if name == "nonq2":
        return list(NON_Q2)
    if name == "stage":
        return list(S_TARGETS)
    if name == "q2stage":
        return ["Q2", "S1", "S2", "S3", "S4"]
    if name == "q2s3":
        return ["Q2", "S3"]
    raise ValueError(name)


def candidate_specs() -> list[H081Spec]:
    return [
        H081Spec("top80_h079_tail", "all", 80, 42, 30, 8, 3, 1, 0.000070, 0.0030, 0.80, "row", False, 1.00),
        H081Spec("top160_conflict_all", "all", 160, 95, 55, 16, 3, 1, 0.000035, 0.0028, 0.82, "any", False, 1.00),
        H081Spec("top260_conflict_all", "all", 260, 145, 80, 22, 2, 1, 0.000018, 0.0024, 0.84, "any", False, 0.92),
        H081Spec("top340_conflict_all", "all", 340, 175, 95, 26, 2, 1, 0.000012, 0.0018, 0.86, "any", False, 0.82),
        H081Spec("nonq2_conflict_c260", "nonq2", 260, 150, 0, 22, 2, 1, 0.000012, 0.0016, 0.86, "any", False, 0.88),
        H081Spec("q2stage_conflict_c180", "q2stage", 180, 110, 65, 18, 2, 1, 0.000018, 0.0020, 0.84, "any", False, 0.95),
        H081Spec("outside_conflict_c260", "all", 260, 150, 75, 22, 2, 1, 0.000012, 0.0016, 0.84, "any", True, 0.90),
        H081Spec("non_episode_conflict_c240", "all", 240, 140, 70, 22, 2, 1, 0.000012, 0.0016, 0.86, "exclude_row", False, 0.90),
    ]


def build_or_load_cell_table(sample: pd.DataFrame, latent: pd.DataFrame, mats: dict[str, np.ndarray], beta: np.ndarray, bad_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    path = H080_OUT / "h080_cell_table.csv"
    if path.exists():
        return pd.read_csv(path)
    sources = H080MOD.select_source_rows()
    source_agg, source_meta = H080MOD.aggregate_sources(sample, mats, beta, sources)
    table = H080MOD.build_cell_table(sample, latent, mats, bad_vecs, source_agg)
    H080_OUT.mkdir(parents=True, exist_ok=True)
    source_meta.to_csv(H080_OUT / "h080_source_views.csv", index=False)
    table.to_csv(path, index=False)
    return table


def conflict_pool(table: pd.DataFrame, spec: H081Spec) -> pd.DataFrame:
    pool = table[
        table["target"].astype(str).isin(target_group(spec.target_group))
        & (table["source_count"] >= spec.min_sources)
        & (table["source_family_count"] >= spec.min_families)
        & (table["source_action_delta"] <= -spec.min_action_gain)
        & (table["source_posterior_delta"] >= spec.min_posterior_conflict)
        & (table["h080_bad_same_rank"] <= spec.max_bad_same_rank)
        & (table["is_h050_null"] <= 0)
    ].copy()
    if spec.q2_cap == 0:
        pool = pool[pool["target"].astype(str) != "Q2"].copy()
    if spec.outside_h069:
        pool = pool[pool["outside_h069_cell"] > 0].copy()
    if spec.h079_mode == "row":
        pool = pool[pool["h079_row"] > 0].copy()
    elif spec.h079_mode == "cell":
        pool = pool[pool["h079_cell"] > 0].copy()
    elif spec.h079_mode == "exclude_row":
        pool = pool[pool["h079_row"] <= 0].copy()
    if pool.empty:
        return pool

    pool["h081_conflict_score"] = (
        0.34 * rank01(-pool["source_action_delta"].to_numpy())
        + 0.19 * rank01(pool["source_posterior_delta"].to_numpy())
        + 0.12 * rank01(pool["source_count"].to_numpy())
        + 0.10 * rank01(pool["source_family_count"].to_numpy())
        + 0.09 * pool["h080_bad_opp_rank"].to_numpy(dtype=float)
        + 0.07 * pool["h079_row"].to_numpy(dtype=float)
        + 0.06 * pool["outside_h069_cell"].to_numpy(dtype=float)
        - 0.13 * pool["h080_bad_same_rank"].to_numpy(dtype=float)
        - 0.08 * rank01(pool["latent_shortcut_energy"].to_numpy())
    )
    return pool.sort_values(["h081_conflict_score", "source_action_delta"], ascending=[False, True])


def greedy_select(pool: pd.DataFrame, spec: H081Spec) -> pd.DataFrame:
    selected = []
    rows_seen: set[int] = set()
    subject_counts: dict[str, int] = {}
    q2_count = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec.get("subject_id", ""))
        target = str(rec["target"])
        if len(selected) >= spec.max_cells:
            break
        if len(rows_seen) >= spec.max_rows and row not in rows_seen:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject and row not in rows_seen:
            continue
        if target == "Q2" and q2_count >= spec.q2_cap:
            continue
        selected.append(rec)
        rows_seen.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        if target == "Q2":
            q2_count += 1
    return pd.DataFrame(selected)


def materialize(selected: pd.DataFrame, spec: H081Spec, mats: dict[str, np.ndarray]) -> np.ndarray:
    prob = mats["h057"].copy()
    h057_logit = logit(mats["h057"])
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        move = float(rec["source_mean_move"])
        prob[row, tidx] = float(sigmoid(np.array([h057_logit[row, tidx] + spec.alpha * move]))[0])
    return clip_prob(prob)


def apply_spec(table: pd.DataFrame, spec: H081Spec, mats: dict[str, np.ndarray]) -> tuple[np.ndarray, pd.DataFrame]:
    pool = conflict_pool(table, spec)
    selected = greedy_select(pool, spec)
    if selected.empty:
        return mats["h057"].copy(), selected
    prob = materialize(selected, spec, mats)
    selected = selected.copy()
    selected["h081_alpha"] = spec.alpha
    selected["h081_target_group"] = spec.target_group
    return prob, selected


def evaluate(
    prob: np.ndarray,
    selected: pd.DataFrame,
    spec: H081Spec,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> dict[str, object]:
    h057 = mats["h057"]
    q061 = mats["q061"]
    changed = np.abs(prob - h057) > TOL
    x = (bce(prob, q061) - bce(h057, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (logit(prob) - logit(h057)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:24]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(v, 0.0) for v in bad_cos.values()] + [0.0])
    target_counts = selected["target"].value_counts().to_dict() if len(selected) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "target_group": spec.target_group,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "min_sources": spec.min_sources,
        "min_families": spec.min_families,
        "min_action_gain": spec.min_action_gain,
        "min_posterior_conflict": spec.min_posterior_conflict,
        "max_bad_same_rank": spec.max_bad_same_rank,
        "h079_mode": spec.h079_mode,
        "outside_h069": spec.outside_h069,
        "alpha": spec.alpha,
        "selected_cells": int(len(selected)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057).max()),
        "mean_source_count": float(selected["source_count"].mean()) if len(selected) else 0.0,
        "mean_family_count": float(selected["source_family_count"].mean()) if len(selected) else 0.0,
        "mean_source_action_delta": float(selected["source_action_delta"].mean()) if len(selected) else 0.0,
        "sum_source_action_delta": float(selected["source_action_delta"].sum()) if len(selected) else 0.0,
        "mean_source_posterior_delta": float(selected["source_posterior_delta"].mean()) if len(selected) else 0.0,
        "sum_source_posterior_delta": float(selected["source_posterior_delta"].sum()) if len(selected) else 0.0,
        "mean_conflict_score": float(selected["h081_conflict_score"].mean()) if len(selected) else 0.0,
        "mean_bad_same_rank": float(selected["h080_bad_same_rank"].mean()) if len(selected) else 1.0,
        "mean_bad_opp_rank": float(selected["h080_bad_opp_rank"].mean()) if len(selected) else 0.0,
        "h079_cell_overlap": int(selected["h079_cell"].sum()) if len(selected) else 0,
        "h079_row_overlap": int(selected["h079_row"].sum()) if len(selected) else 0,
        "outside_h069_cells": int(selected["outside_h069_cell"].sum()) if len(selected) else 0,
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, sorted(selected["row"].astype(int).unique()))) if len(selected) else "",
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def candidate_sweep(
    table: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame]:
    rows = []
    probs = {}
    cells = []
    seen: set[str] = set()
    for spec in candidate_specs():
        prob, selected = apply_spec(table, spec, mats)
        if selected.empty:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        meta = evaluate(prob, selected, spec, mats, beta, bad_vecs)
        cid = f"h081_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        cells.append(selected.assign(candidate_id=cid))

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H081 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["conflict_rank"] = rank01(cand["sum_source_posterior_delta"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 300))
    cand["h079_rank"] = rank01(cand["h079_row_overlap"].to_numpy())
    cand["h081_score"] = (
        0.29 * cand["action_rank"]
        + 0.16 * cand["conflict_rank"]
        + 0.14 * cand["responsibility_rank"]
        + 0.13 * cand["bad_avoid_rank"]
        + 0.10 * cand["scale_rank"]
        + 0.07 * cand["h079_rank"]
        + 0.06 * rank01(cand["mean_conflict_score"].to_numpy())
        + 0.05 * rank01(-cand["mean_bad_same_rank"].to_numpy())
        - 0.08 * (cand["max_abs_prob_move_vs_h057"] > 0.20).astype(float)
    )
    cand = cand.sort_values(["h081_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected_cells = pd.concat(cells, ignore_index=True) if cells else pd.DataFrame()
    return cand, probs, selected_cells


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(cand: pd.DataFrame, selected_cells: pd.DataFrame, decision: pd.DataFrame) -> None:
    cell_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "target",
        "source_count",
        "source_family_count",
        "source_action_delta",
        "source_posterior_delta",
        "h081_conflict_score",
        "h080_bad_same_rank",
        "h080_bad_opp_rank",
        "h079_cell",
        "h079_row",
        "h081_alpha",
        "h081_target_group",
    ]
    parts = [
        "# H081 Conflict-Ridge HS-JEPA",
        "",
        "Question: are cells where public-action and q061 posterior disagree a hidden public/private tail state?",
        "",
        "Design:",
        "",
        "- start from H080 source-view cell table;",
        "- select cells with negative public-action contribution but positive q061-posterior conflict;",
        "- materialize source-view movement instead of forcing q061 compatibility;",
        "- interpret public feedback as a decision on whether q061 is a hard guardrail or only a smooth prior.",
        "",
        "Candidates:",
        "",
        md_table(cand, 40),
        "",
        "Selected cells sample:",
        "",
        md_table(selected_cells[[c for c in cell_cols if c in selected_cells.columns]].head(180), 180) if len(selected_cells) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h081_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    table = build_or_load_cell_table(sample, latent, mats, beta, bad_vecs)
    cand, probs, selected_cells = candidate_sweep(table, mats, beta, bad_vecs)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())

    bigbet = cand[
        (cand["public_action_pred_delta_vs_h057"] <= -0.0012)
        & (cand["changed_cells_vs_h057"] >= 40)
        & (cand["max_positive_bad_cosine"] <= 0.020)
    ].copy()
    if len(bigbet):
        selected = bigbet.sort_values(["h081_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).iloc[0]
        decision_name = "promote_conflict_ridge_bigbet"
        worldview = "q061 posterior fails on a public-tail conflict ridge"
    else:
        selected = cand.iloc[0]
        decision_name = "promote_conflict_ridge_diagnostic"
        worldview = "conflict ridge is measurable but did not clear the action gate"

    selected_id = str(selected["candidate_id"])
    root_file = ROOT / f"submission_h081_conflict_ridge_{selected['hash']}_uploadsafe.csv"
    shutil.copy2(Path(str(selected["resolved_path"])), root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    decision = pd.DataFrame([{**selected.to_dict(), **validation}])
    decision.insert(0, "worldview", worldview)
    decision.insert(0, "root_uploadsafe_path", str(root_file.resolve()))
    decision.insert(0, "selected_resolved_path", str(selected["resolved_path"]))
    decision.insert(0, "selected_file", str(selected["file"]))
    decision.insert(0, "selected_candidate_id", selected_id)
    decision.insert(0, "decision", decision_name)

    cand.to_csv(OUT / "h081_candidate_scores.csv", index=False)
    selected_cells.to_csv(OUT / "h081_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h081_decision.csv", index=False)
    write_report(cand, selected_cells, decision)

    print(f"selected={selected_id}")
    print(f"root={root_file}")
    print(decision[["decision", "public_action_pred_delta_vs_h057", "posterior_delta_vs_h057", "changed_cells_vs_h057", "max_positive_bad_cosine", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
