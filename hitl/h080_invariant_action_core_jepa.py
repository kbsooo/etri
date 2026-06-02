#!/usr/bin/env python3
"""H080: invariant action-core HS-JEPA.

H079 tests whether H077 hard-tail anchors should spread into short episodes.
H080 takes a different big bet: the missing public/private state is the
intersection of several HS-JEPA views, not one new local decoder.

Target representation:

    previous HS-JEPA candidate movements
      -> multi-view direction consensus
      -> public/private invariant action core
      -> correction field

This is deliberately not a tiny blend. It asks whether H071 assignment, H074
anti-shortcut, H076 route-value, and H079 episode views point to a shared
hidden action field that is more private-safe than any one source.
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
OUT = HITL / "h080_invariant_action_core_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12

SOURCE_DEFS = [
    ("h071", HITL / "h071_rowtarget_assignment_solver_jepa" / "h071_candidate_scores.csv", "h071_score", 5),
    ("h074", HITL / "h074_anti_shortcut_state_inversion_jepa" / "h074_candidate_scores.csv", "h074_score", 5),
    ("h076", HITL / "h076_route_specific_value_decoder_jepa" / "h076_candidate_scores.csv", "h076_score", 6),
    ("h079", HITL / "h079_forced_episode_state_jepa" / "h079_candidate_scores.csv", "h079_score", 4),
]


@dataclass(frozen=True)
class H080Spec:
    name: str
    value_mode: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_sources: int
    min_families: int
    min_consensus: float
    min_cell_score: float
    max_bad_same_rank: float
    h079_mode: str
    outside_h069: bool
    row_expand: bool
    row_count: int
    alpha: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H071MOD = import_module(HITL / "h071_rowtarget_assignment_solver_jepa.py", "h071mod_for_h080")


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
    for path in OUT.glob("submission_h080_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h080_invariant_core_*_uploadsafe.csv"):
        path.unlink()


def candidate_specs() -> list[H080Spec]:
    return [
        H080Spec("allfamily_source_core_c900", "source_mean", 900, 190, 75, 26, 6, 3, 0.66, 0.54, 0.68, "any", False, False, 0, 0.95),
        H080Spec("private_safe_outside_c760", "source_q061_hybrid", 760, 180, 42, 24, 4, 2, 0.62, 0.56, 0.52, "any", True, False, 0, 1.05),
        H080Spec("non_episode_invariant_c680", "source_mean", 680, 170, 55, 24, 5, 3, 0.68, 0.55, 0.62, "exclude_row", False, False, 0, 1.00),
        H080Spec("episode_confirmed_core_c420", "source_q061_hybrid", 420, 72, 42, 14, 3, 2, 0.58, 0.50, 0.70, "row", False, False, 0, 0.90),
        H080Spec("strict_allfamily_hard_c1100", "source_mean", 1100, 220, 95, 30, 7, 4, 0.74, 0.52, 0.72, "any", False, False, 0, 1.18),
        H080Spec("rowcore_fullvector_r80", "source_q061_hybrid", 760, 80, 80, 16, 3, 2, 0.55, 0.48, 0.68, "any", False, True, 80, 0.72),
        H080Spec("rowcore_non_episode_r70", "source_q061_hybrid", 620, 70, 70, 14, 3, 2, 0.58, 0.50, 0.62, "exclude_row", False, True, 70, 0.78),
    ]


def load_prob(path: Path, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(path)
    if list(df.columns) != list(sample.columns) + TARGETS:
        expected = KEYS + TARGETS
        if list(df.columns) != expected:
            raise ValueError(f"unexpected columns for {path}: {list(df.columns)}")
    for key in KEYS:
        if not df[key].astype(str).equals(sample[key].astype(str)):
            raise ValueError(f"key mismatch for {path}: {key}")
    return df[TARGETS].to_numpy(dtype=np.float64)


def select_source_rows() -> pd.DataFrame:
    rows = []
    seen: set[str] = set()
    for family, score_path, score_col, top_n in SOURCE_DEFS:
        if not score_path.exists():
            continue
        df = pd.read_csv(score_path)
        if "resolved_path" not in df:
            continue
        if score_col in df:
            rank_a = df.sort_values(score_col, ascending=False).head(top_n)
        else:
            rank_a = df.head(top_n)
        rank_b = df.sort_values("public_action_pred_delta_vs_h057").head(max(2, top_n // 2))
        for _, rec in pd.concat([rank_a, rank_b], ignore_index=True).iterrows():
            path = Path(str(rec["resolved_path"]))
            if not path.exists() or str(path) in seen:
                continue
            seen.add(str(path))
            action = float(rec.get("public_action_pred_delta_vs_h057", 0.0))
            bad = float(rec.get("max_positive_bad_cosine", 0.0))
            score = float(rec.get(score_col, 0.5))
            reliability = np.clip((-action + 0.00025) / 0.00125, 0.15, 1.80)
            reliability *= float(np.clip(1.0 - 20.0 * max(bad, 0.0), 0.25, 1.0))
            rows.append(
                {
                    "family": family,
                    "source_id": str(rec.get("candidate_id", path.stem)),
                    "score_col": score_col,
                    "score": score,
                    "public_action_pred_delta_vs_h057": action,
                    "max_positive_bad_cosine": bad,
                    "weight": float(reliability),
                    "path": str(path),
                }
            )
    if not rows:
        raise RuntimeError("no H080 sources found")
    return pd.DataFrame(rows)


def bad_cell_features(mats: dict[str, np.ndarray], bad_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    h057 = mats["h057"]
    q061 = mats["q061"]
    base_dir = np.sign((logit(q061) - logit(h057)).reshape(-1))
    base_dir = np.where(base_dir == 0, 1.0, base_dir)
    same = np.zeros_like(base_dir, dtype=np.float64)
    opp = np.zeros_like(base_dir, dtype=np.float64)
    for vec in bad_vecs.values():
        signed = base_dir * np.asarray(vec, dtype=np.float64)
        same += np.maximum(signed, 0.0)
        opp += np.maximum(-signed, 0.0)
    denom = max(len(bad_vecs), 1)
    same = same / denom
    opp = opp / denom
    return pd.DataFrame(
        {
            "flat_index": np.arange(base_dir.size, dtype=int),
            "h080_bad_same_raw": same,
            "h080_bad_opp_raw": opp,
            "h080_bad_same_rank": rank01(np.log1p(same)),
            "h080_bad_opp_rank": rank01(np.log1p(opp)),
            "h080_bad_margin_rank": rank01(np.log1p(np.maximum(opp - same, 0.0))),
        }
    )


def h079_membership() -> pd.DataFrame:
    decision_path = HITL / "h079_forced_episode_state_jepa" / "h079_decision.csv"
    cell_path = HITL / "h079_forced_episode_state_jepa" / "h079_selected_cells.csv"
    if not decision_path.exists() or not cell_path.exists():
        return pd.DataFrame({"flat_index": np.arange(1750), "h079_cell": 0.0, "h079_row": 0.0})
    decision = pd.read_csv(decision_path)
    selected_id = str(decision.iloc[0]["selected_candidate_id"])
    cells = pd.read_csv(cell_path)
    cells = cells[cells["candidate_id"].astype(str).eq(selected_id)].copy()
    if cells.empty:
        return pd.DataFrame({"flat_index": np.arange(1750), "h079_cell": 0.0, "h079_row": 0.0})
    row_set = set(cells["row"].astype(int).tolist())
    all_flat = pd.DataFrame({"flat_index": np.arange(250 * len(TARGETS), dtype=int)})
    all_flat["row"] = all_flat["flat_index"] // len(TARGETS)
    all_flat["h079_row"] = all_flat["row"].isin(row_set).astype(float)
    all_flat["h079_cell"] = all_flat["flat_index"].isin(set(cells["flat_index"].astype(int))).astype(float)
    role = cells[["flat_index", "h079_role"]].drop_duplicates("flat_index")
    all_flat = all_flat.merge(role, on="flat_index", how="left")
    all_flat["h079_role"] = all_flat["h079_role"].fillna("")
    return all_flat[["flat_index", "h079_cell", "h079_row", "h079_role"]]


def aggregate_sources(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    sources: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    h057 = mats["h057"]
    q061 = mats["q061"]
    h057_logit = logit(h057).reshape(-1)
    source_weight = np.zeros(h057.size, dtype=np.float64)
    source_count = np.zeros(h057.size, dtype=np.float64)
    sign_sum = np.zeros(h057.size, dtype=np.float64)
    move_sum = np.zeros(h057.size, dtype=np.float64)
    action_sum = np.zeros(h057.size, dtype=np.float64)
    posterior_sum = np.zeros(h057.size, dtype=np.float64)
    family_hits = {family: np.zeros(h057.size, dtype=np.float64) for family in sorted(set(sources["family"]))}
    source_meta = []

    for rec in sources.to_dict("records"):
        prob = load_prob(Path(str(rec["path"])), sample)
        changed = (np.abs(prob - h057) > TOL).reshape(-1)
        if not changed.any():
            continue
        weight = float(rec["weight"])
        move = logit(prob).reshape(-1) - h057_logit
        cell_delta = (bce(prob, q061) - bce(h057, q061)).reshape(-1)
        source_weight[changed] += weight
        source_count[changed] += 1.0
        sign_sum[changed] += weight * np.sign(move[changed])
        move_sum[changed] += weight * move[changed]
        action_sum[changed] += weight * cell_delta[changed] * beta[changed]
        posterior_sum[changed] += weight * cell_delta[changed]
        family_hits[str(rec["family"])][changed] = 1.0
        source_meta.append({**rec, "changed_cells": int(changed.sum())})

    denom = np.maximum(source_weight, 1.0e-12)
    family_count = np.zeros(h057.size, dtype=np.float64)
    for hits in family_hits.values():
        family_count += hits

    table = pd.DataFrame(
        {
            "flat_index": np.arange(h057.size, dtype=int),
            "row": np.arange(h057.size, dtype=int) // len(TARGETS),
            "target_index": np.arange(h057.size, dtype=int) % len(TARGETS),
            "source_count": source_count,
            "source_weight": source_weight,
            "source_family_count": family_count,
            "source_consensus": np.abs(sign_sum) / denom,
            "source_mean_move": move_sum / denom,
            "source_action_delta": action_sum / denom,
            "source_posterior_delta": posterior_sum / denom,
        }
    )
    table["target"] = table["target_index"].map(dict(enumerate(TARGETS)))
    for family, hits in family_hits.items():
        table[f"hit_{family}"] = hits
    return table, pd.DataFrame(source_meta)


def build_cell_table(
    sample: pd.DataFrame,
    latent: pd.DataFrame,
    mats: dict[str, np.ndarray],
    bad_vecs: dict[str, np.ndarray],
    source_agg: pd.DataFrame,
) -> pd.DataFrame:
    base = latent.copy()
    if "flat_index" not in base:
        base["flat_index"] = base["row"].astype(int) * len(TARGETS) + base["target_index"].astype(int)
    keep_cols = [
        "flat_index",
        "row",
        "subject_id",
        "sleep_date",
        "lifelog_date",
        "target",
        "target_index",
        "h057_prob",
        "q061",
        "cell_q061_gain",
        "public_score",
        "invariant_score",
        "private_safe_score",
        "latent_shortcut_energy",
        "bad_pressure_rank",
        "h068_cell_health",
        "outside_h069_cell",
        "outside_h070_cell",
        "is_h050_null",
    ]
    keep_cols = [col for col in keep_cols if col in base.columns]
    table = base[keep_cols].merge(source_agg, on=["flat_index", "row", "target", "target_index"], how="left")
    table = table.merge(bad_cell_features(mats, bad_vecs), on="flat_index", how="left")
    table = table.merge(h079_membership(), on="flat_index", how="left")
    table = table.fillna(0.0)
    for col in ["h079_role"]:
        if col in table:
            table[col] = table[col].astype(str).replace("0.0", "")

    table["h080_cell_score"] = (
        0.19 * rank01(-table["source_action_delta"].to_numpy())
        + 0.14 * rank01(-table["source_posterior_delta"].to_numpy())
        + 0.13 * rank01(table["source_family_count"].to_numpy())
        + 0.11 * table["source_consensus"].to_numpy(dtype=float)
        + 0.10 * rank01(table["public_score"].to_numpy())
        + 0.09 * rank01(table["invariant_score"].to_numpy())
        + 0.08 * rank01(table["private_safe_score"].to_numpy())
        + 0.07 * rank01(table["h068_cell_health"].to_numpy())
        + 0.07 * table["h080_bad_opp_rank"].to_numpy(dtype=float)
        + 0.04 * table["outside_h069_cell"].to_numpy(dtype=float)
        - 0.13 * table["h080_bad_same_rank"].to_numpy(dtype=float)
        - 0.12 * rank01(table["latent_shortcut_energy"].to_numpy())
        - 0.08 * table["is_h050_null"].to_numpy(dtype=float)
        - 0.05 * (table["target"].astype(str) == "Q2").astype(float).to_numpy()
    )
    table.loc[table["cell_q061_gain"] <= 0, "h080_cell_score"] -= 0.70
    table.loc[table["source_count"] <= 0, "h080_cell_score"] -= 0.80
    return table.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def filter_pool(table: pd.DataFrame, spec: H080Spec) -> pd.DataFrame:
    pool = table[
        (table["source_count"] >= spec.min_sources)
        & (table["source_family_count"] >= spec.min_families)
        & (table["source_consensus"] >= spec.min_consensus)
        & (table["h080_cell_score"] >= spec.min_cell_score)
        & (table["h080_bad_same_rank"] <= spec.max_bad_same_rank)
        & (table["cell_q061_gain"] > 0)
        & (table["is_h050_null"] <= 0)
    ].copy()
    if spec.outside_h069:
        pool = pool[pool["outside_h069_cell"] > 0].copy()
    if spec.h079_mode == "row":
        pool = pool[pool["h079_row"] > 0].copy()
    elif spec.h079_mode == "cell":
        pool = pool[pool["h079_cell"] > 0].copy()
    elif spec.h079_mode == "exclude_row":
        pool = pool[pool["h079_row"] <= 0].copy()
    elif spec.h079_mode == "exclude_cell":
        pool = pool[pool["h079_cell"] <= 0].copy()
    if pool.empty:
        return pool
    return pool.sort_values(["h080_cell_score", "source_family_count", "source_consensus"], ascending=[False, False, False])


def greedy_select(pool: pd.DataFrame, spec: H080Spec) -> pd.DataFrame:
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


def row_expand_select(pool: pd.DataFrame, table: pd.DataFrame, spec: H080Spec) -> pd.DataFrame:
    if pool.empty:
        return pool
    row_scores = (
        pool.groupby(["row", "subject_id"], as_index=False)
        .agg(
            row_score=("h080_cell_score", "mean"),
            row_cells=("flat_index", "nunique"),
            row_families=("source_family_count", "mean"),
            row_action=("source_action_delta", "sum"),
            row_bad_same=("h080_bad_same_rank", "mean"),
        )
        .sort_values(["row_score", "row_cells", "row_action"], ascending=[False, False, True])
    )
    chosen = []
    subject_counts: dict[str, int] = {}
    for rec in row_scores.to_dict("records"):
        subject = str(rec["subject_id"])
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        chosen.append(int(rec["row"]))
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        if len(chosen) >= spec.row_count:
            break
    expanded = table[
        table["row"].isin(chosen)
        & (table["cell_q061_gain"] > 0)
        & (table["h080_bad_same_rank"] <= spec.max_bad_same_rank)
        & (table["is_h050_null"] <= 0)
    ].copy()
    expanded["h080_row_expanded"] = 1.0
    return greedy_select(expanded.sort_values(["row", "target_index"]), spec)


def materialize(selected: pd.DataFrame, spec: H080Spec, mats: dict[str, np.ndarray]) -> np.ndarray:
    prob = mats["h057"].copy()
    h057_logit = logit(mats["h057"])
    q061_move = logit(mats["q061"]) - h057_logit
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        source_move = float(rec.get("source_mean_move", 0.0))
        if spec.value_mode == "source_mean":
            move = source_move
        elif spec.value_mode == "q061":
            move = float(q061_move[row, tidx])
        elif spec.value_mode == "source_q061_hybrid":
            move = 0.60 * source_move + 0.40 * float(q061_move[row, tidx])
        else:
            raise ValueError(spec.value_mode)
        prob[row, tidx] = float(sigmoid(np.array([h057_logit[row, tidx] + spec.alpha * move]))[0])
    return clip_prob(prob)


def apply_spec(table: pd.DataFrame, spec: H080Spec, mats: dict[str, np.ndarray]) -> tuple[np.ndarray, pd.DataFrame]:
    pool = filter_pool(table, spec)
    if spec.row_expand:
        selected = row_expand_select(pool, table, spec)
    else:
        selected = greedy_select(pool, spec)
    if selected.empty:
        return mats["h057"].copy(), selected
    prob = materialize(selected, spec, mats)
    selected = selected.copy()
    selected["h080_value_mode"] = spec.value_mode
    selected["h080_alpha"] = spec.alpha
    return prob, selected


def evaluate(
    prob: np.ndarray,
    selected: pd.DataFrame,
    spec: H080Spec,
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
    family_hits = {}
    for family in ["h071", "h074", "h076", "h079"]:
        col = f"hit_{family}"
        if col in selected:
            family_hits[family] = int(selected[col].sum())
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "value_mode": spec.value_mode,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "min_sources": spec.min_sources,
        "min_families": spec.min_families,
        "min_consensus": spec.min_consensus,
        "min_cell_score": spec.min_cell_score,
        "max_bad_same_rank": spec.max_bad_same_rank,
        "h079_mode": spec.h079_mode,
        "outside_h069": spec.outside_h069,
        "row_expand": spec.row_expand,
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
        "mean_consensus": float(selected["source_consensus"].mean()) if len(selected) else 0.0,
        "mean_h080_cell_score": float(selected["h080_cell_score"].mean()) if len(selected) else 0.0,
        "mean_bad_same_rank": float(selected["h080_bad_same_rank"].mean()) if len(selected) else 1.0,
        "mean_bad_opp_rank": float(selected["h080_bad_opp_rank"].mean()) if len(selected) else 0.0,
        "mean_shortcut": float(selected["latent_shortcut_energy"].mean()) if len(selected) else 1.0,
        "h079_cell_overlap": int(selected["h079_cell"].sum()) if len(selected) else 0,
        "h079_row_overlap": int(selected["h079_row"].sum()) if len(selected) else 0,
        "outside_h069_cells": int(selected["outside_h069_cell"].sum()) if len(selected) else 0,
        "h050_null_selected": int(selected["is_h050_null"].sum()) if len(selected) else 0,
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, sorted(selected["row"].astype(int).unique()))) if len(selected) else "",
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        "source_family_hits": ";".join(f"{k}:{v}" for k, v in sorted(family_hits.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def candidate_sweep(
    table: pd.DataFrame,
    sample: pd.DataFrame,
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
        if meta["changed_cells_vs_h057"] <= 0:
            continue
        cid = f"h080_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        cells.append(selected.assign(candidate_id=cid))

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H080 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 900))
    cand["consensus_rank"] = rank01(cand["mean_consensus"].to_numpy())
    cand["family_rank"] = rank01(cand["mean_family_count"].to_numpy())
    cand["posterior_violation"] = np.maximum(cand["posterior_delta_vs_h057"].to_numpy(), 0.0)
    cand["h080_score"] = (
        0.23 * cand["action_rank"]
        + 0.17 * cand["posterior_rank"]
        + 0.15 * cand["responsibility_rank"]
        + 0.12 * cand["bad_avoid_rank"]
        + 0.10 * cand["scale_rank"]
        + 0.09 * cand["consensus_rank"]
        + 0.07 * cand["family_rank"]
        + 0.04 * rank01(-cand["mean_bad_same_rank"].to_numpy())
        + 0.03 * rank01(cand["outside_h069_cells"].to_numpy())
        - 0.06 * (cand["max_abs_prob_move_vs_h057"] > 0.22).astype(float)
        - 0.08 * cand["posterior_violation"].clip(0, 0.01) / 0.01
    )
    cand = cand.sort_values(["h080_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    selected_cells = pd.concat(cells, ignore_index=True) if cells else pd.DataFrame()
    return cand, probs, selected_cells


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(cand: pd.DataFrame, sources: pd.DataFrame, selected_cells: pd.DataFrame, decision: pd.DataFrame) -> None:
    cell_cols = [
        "candidate_id",
        "row",
        "subject_id",
        "sleep_date",
        "target",
        "source_count",
        "source_family_count",
        "source_consensus",
        "source_action_delta",
        "source_posterior_delta",
        "h080_cell_score",
        "h080_bad_same_rank",
        "h080_bad_opp_rank",
        "h079_cell",
        "h079_row",
        "h080_value_mode",
        "h080_alpha",
    ]
    parts = [
        "# H080 Invariant Action-Core HS-JEPA",
        "",
        "Question: do H071 assignment, H074 anti-shortcut, H076 route-value, and H079 episode views share a private-safe action core?",
        "",
        "Design:",
        "",
        "- treat prior HS-JEPA submissions as latent views, not as blend ingredients;",
        "- aggregate row-target movement direction, action contribution, posterior contribution, and family agreement;",
        "- select cells or rows where multiple views agree and bad-anchor geometry stays controlled;",
        "- materialize a consensus correction field from source movement and q061.",
        "",
        "Source views:",
        "",
        md_table(sources, 40),
        "",
        "Candidates:",
        "",
        md_table(cand, 40),
        "",
        "Selected cells sample:",
        "",
        md_table(selected_cells[[c for c in cell_cols if c in selected_cells.columns]].head(160), 160) if len(selected_cells) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h080_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    sources = select_source_rows()
    source_agg, source_meta = aggregate_sources(sample, mats, beta, sources)
    table = build_cell_table(sample, latent, mats, bad_vecs, source_agg)
    cand, probs, selected_cells = candidate_sweep(table, sample, mats, beta, bad_vecs)

    bigbet = cand[
        (cand["public_action_pred_delta_vs_h057"] <= -0.0012)
        & (cand["changed_cells_vs_h057"] >= 250)
        & (cand["posterior_delta_vs_h057"] <= 0.0001)
        & (cand["max_positive_bad_cosine"] <= 0.004)
    ].copy()
    if len(bigbet):
        selected = bigbet.sort_values(["h080_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).iloc[0]
        decision_name = "promote_invariant_action_core_bigbet"
        worldview = "multiple HS-JEPA views share a private-safe invariant action core"
    else:
        selected = cand.iloc[0]
        decision_name = "promote_invariant_action_core_diagnostic"
        worldview = "consensus action core is measurable but did not clear every big-bet guardrail"

    selected_id = str(selected["candidate_id"])
    root_file = ROOT / f"submission_h080_invariant_core_{selected['hash']}_uploadsafe.csv"
    shutil.copy2(Path(str(selected["resolved_path"])), root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    decision = pd.DataFrame([{**selected.to_dict(), **validation}])
    decision.insert(0, "worldview", worldview)
    decision.insert(0, "root_uploadsafe_path", str(root_file.resolve()))
    decision.insert(0, "selected_resolved_path", str(selected["resolved_path"]))
    decision.insert(0, "selected_file", str(selected["file"]))
    decision.insert(0, "selected_candidate_id", selected_id)
    decision.insert(0, "decision", decision_name)

    source_meta.to_csv(OUT / "h080_source_views.csv", index=False)
    table.to_csv(OUT / "h080_cell_table.csv", index=False)
    cand.to_csv(OUT / "h080_candidate_scores.csv", index=False)
    selected_cells.to_csv(OUT / "h080_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h080_decision.csv", index=False)
    write_report(cand, source_meta, selected_cells, decision)

    print(f"selected={selected_id}")
    print(f"root={root_file}")
    print(decision[["decision", "public_action_pred_delta_vs_h057", "posterior_delta_vs_h057", "changed_cells_vs_h057", "max_positive_bad_cosine", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
