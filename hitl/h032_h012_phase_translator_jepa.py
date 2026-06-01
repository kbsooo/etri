#!/usr/bin/env python3
"""H032: H012 phase-translator HS-JEPA.

H030/H031 narrowed the bottleneck: row-target identity and memory-conflict cells
explain much of H012, but direct amplification does not preserve the basin.

H032 asks a different question. Maybe H012 is not a cell-selection discovery
alone; maybe it is a phase point on the E247 -> public-posterior route: a
specific target route, top-k support, and probability amplitude translator.

The experiment generates a dense phase diagram around the original H012
posterior target, then scores those variants with public sensors that withhold
H012's public score. If the translator is real, H012 or a stronger sibling
should be recoverable by state/action geometry without using H012's LB as a
label. If not, H012 is a narrower public-equation needle than the current
translator can learn.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import re
import shutil
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h032_h012_phase_translator_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831

H012_DIR = HITL / "h012_public_equation_jepa_jackpot"
H014_DIR = HITL / "h014_sleep_state_memory_posterior_audit"
H030_DIR = HITL / "h030_rowtarget_identity_equation_jepa"


@dataclass(frozen=True)
class PhaseSpec:
    score_name: str
    target_group: str
    k: int
    alpha: float
    curve: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def safe_id(text: str, limit: int = 120) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rank01(values: pd.Series | np.ndarray, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if float(s.std()) < 1.0e-15:
        return np.full(len(s), 0.5, dtype=np.float64)
    r = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high else 1.0 - r


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = clip_prob(q)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def md_table(frame: pd.DataFrame, n: int = 30) -> str:
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


def load_h024() -> object:
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h032")


def load_base(h024: object) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    h012_df = h024.load_sub(H012)
    sample = h012_df[KEYS].copy()
    e247_df = h024.load_sub(E247, sample)
    e247_prob = e247_df[TARGETS].to_numpy(dtype=np.float64)
    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    q = load_h012_posterior(e247_prob.shape)
    return sample, e247_df, h012_df, e247_prob, h012_prob, q


def load_h012_posterior(shape: tuple[int, int]) -> np.ndarray:
    df = pd.read_csv(H012_DIR / "h012_cell_posterior.csv")
    q = np.zeros(shape, dtype=np.float64)
    for rec in df.to_dict("records"):
        q[int(rec["row"]), TARGETS.index(str(rec["target"]))] = float(rec["posterior_prob"])
    if np.any(q <= 0.0):
        raise ValueError("Incomplete H012 posterior map")
    return clip_prob(q)


def target_mask(cells: pd.DataFrame, group: str) -> np.ndarray:
    mapping = {
        "all": TARGETS,
        "Q": ["Q1", "Q2", "Q3"],
        "S": ["S1", "S2", "S3", "S4"],
        "S124": ["S1", "S2", "S4"],
        "S12": ["S1", "S2"],
        "S2S4": ["S2", "S4"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
        "Q3": ["Q3"],
    }
    if group not in mapping:
        raise KeyError(group)
    return cells["target"].isin(mapping[group]).to_numpy(dtype=bool)


def load_cell_state(e247_prob: np.ndarray, h012_prob: np.ndarray, q: np.ndarray) -> pd.DataFrame:
    post = pd.read_csv(H012_DIR / "h012_cell_posterior.csv")
    post["target"] = post["target"].astype(str)

    mem_path = H014_DIR / "h014_memory_cells.csv"
    if mem_path.exists():
        mem = pd.read_csv(mem_path)
        keep = [
            "row",
            "target",
            "memory_disagrees_h012",
            "memory_agrees_h012",
            "memory_alignment_q",
            "private_safe_score",
            "posterior_gain",
            "row_full_reliability_q",
        ]
        post = post.merge(mem[[c for c in keep if c in mem.columns]], on=["row", "target"], how="left")

    ident_path = H030_DIR / "h030_cell_identity_state.csv"
    if ident_path.exists():
        ident = pd.read_csv(ident_path)
        keep = [
            "row",
            "target",
            "score_identity_combo",
            "score_no_h012_combo",
            "score_joint_vector_cell",
            "score_public_row_subset",
            "score_memory_public_combo",
        ]
        post = post.merge(ident[[c for c in keep if c in ident.columns]], on=["row", "target"], how="left")

    z_e247 = logit(e247_prob)
    z_h012 = logit(h012_prob)
    z_q = logit(q)
    h012_abs = np.abs(z_h012 - z_e247)
    q_abs = np.abs(z_q - z_e247)
    target_to_i = {t: i for i, t in enumerate(TARGETS)}

    post["target_i"] = post["target"].map(target_to_i).astype(int)
    post["h012_prob"] = [h012_prob[int(r), int(c)] for r, c in post[["row", "target_i"]].to_numpy()]
    post["e247_prob"] = [e247_prob[int(r), int(c)] for r, c in post[["row", "target_i"]].to_numpy()]
    post["q_prob"] = [q[int(r), int(c)] for r, c in post[["row", "target_i"]].to_numpy()]
    post["h012_abs_logit_delta"] = [h012_abs[int(r), int(c)] for r, c in post[["row", "target_i"]].to_numpy()]
    post["q_abs_logit_delta"] = [q_abs[int(r), int(c)] for r, c in post[["row", "target_i"]].to_numpy()]
    post["h012_changed"] = np.abs(post["h012_prob"] - post["e247_prob"]) > 1.0e-6
    post["h012_reproduction_error"] = np.abs(logit(post["h012_prob"]) - ((1.0 - 0.7) * logit(post["e247_prob"]) + 0.7 * logit(post["q_prob"])))

    defaults = {
        "memory_disagrees_h012": False,
        "memory_agrees_h012": False,
        "memory_alignment_q": 0.5,
        "private_safe_score": 0.5,
        "posterior_gain": 0.0,
        "row_full_reliability_q": 0.5,
        "score_identity_combo": 0.5,
        "score_no_h012_combo": 0.5,
        "score_joint_vector_cell": 0.5,
        "score_public_row_subset": 0.5,
        "score_memory_public_combo": 0.5,
    }
    for col, default in defaults.items():
        if col not in post.columns:
            post[col] = default
        post[col] = post[col].fillna(default)
    post["memory_disagrees_h012"] = post["memory_disagrees_h012"].astype(bool)
    post["memory_agrees_h012"] = post["memory_agrees_h012"].astype(bool)

    post["cell_score_rank"] = rank01(post["cell_score"])
    post["q_abs_rank"] = rank01(post["q_abs_logit_delta"])
    post["h012_abs_rank"] = rank01(post["h012_abs_logit_delta"])
    post["posterior_gain_rank"] = rank01(post["posterior_gain"])
    post["anti_memory_rank"] = rank01(-post["memory_alignment_q"])
    post["identity_phase_score"] = np.clip(
        0.45 * post["cell_score_rank"]
        + 0.25 * post["score_identity_combo"]
        + 0.15 * post["score_joint_vector_cell"]
        + 0.10 * post["score_public_row_subset"]
        + 0.05 * post["h012_abs_rank"],
        0.0,
        1.0,
    )
    post["memory_conflict_phase_score"] = np.clip(
        0.34 * post["cell_score_rank"]
        + 0.22 * post["memory_disagrees_h012"].astype(float)
        + 0.16 * post["anti_memory_rank"]
        + 0.16 * post["score_identity_combo"]
        + 0.12 * post["posterior_gain_rank"],
        0.0,
        1.0,
    )
    post["route_translator_score"] = np.clip(
        0.34 * post["cell_score_rank"]
        + 0.24 * post["score_no_h012_combo"]
        + 0.18 * post["score_memory_public_combo"]
        + 0.12 * post["direction_consistency"]
        + 0.12 * post["q_abs_rank"],
        0.0,
        1.0,
    )
    post.to_csv(OUT / "h032_cell_phase_state.csv", index=False)
    return post


def phase_specs() -> list[PhaseSpec]:
    specs: list[PhaseSpec] = []
    score_names = ["cell_score", "identity_phase_score", "memory_conflict_phase_score", "route_translator_score"]
    groups = ["all", "S", "Q", "S124", "S12", "S2S4", "Q3S"]
    ks = [120, 240, 400, 600, 800, 1000, 1200, 1400, 1600, 1750]
    alphas = [0.35, 0.50, 0.60, 0.70, 0.80, 0.95, 1.10]
    curves = ["uniform", "consistency", "score_soft", "target_route"]
    for score_name in score_names:
        for group in groups:
            for k in ks:
                for alpha in alphas:
                    for curve in curves:
                        specs.append(PhaseSpec(score_name, group, k, alpha, curve))
    return specs


def pick_cells(cells: pd.DataFrame, spec: PhaseSpec) -> np.ndarray:
    mask = target_mask(cells, spec.target_group).copy()
    pool = cells[mask].copy()
    if pool.empty:
        return np.asarray([], dtype=int)
    pool = pool.sort_values(spec.score_name, ascending=False).head(min(spec.k, len(pool)))
    return (pool["row"].to_numpy(dtype=int) * len(TARGETS) + pool["target_i"].to_numpy(dtype=int)).astype(int)


def curve_multiplier(cells: pd.DataFrame, spec: PhaseSpec, idx: np.ndarray) -> np.ndarray:
    if len(idx) == 0:
        return np.asarray([], dtype=np.float64)
    selected = cells.set_index(cells["row"] * len(TARGETS) + cells["target_i"]).loc[idx]
    mult = np.full(len(idx), spec.alpha, dtype=np.float64)
    if spec.curve == "uniform":
        return mult
    if spec.curve == "consistency":
        return mult * np.clip(selected["direction_consistency"].to_numpy(dtype=np.float64), 0.0, 1.0) ** 0.75
    if spec.curve == "score_soft":
        local = rank01(selected[spec.score_name])
        return mult * (0.55 + 0.45 * local)
    if spec.curve == "target_route":
        target = selected["target"].astype(str).to_numpy()
        route = np.ones(len(idx), dtype=np.float64)
        route[np.isin(target, ["Q1", "Q2"])] *= 0.82
        route[np.isin(target, ["Q3"])] *= 0.93
        route[np.isin(target, ["S1", "S2", "S4"])] *= 1.06
        route[np.isin(target, ["S3"])] *= 0.96
        return mult * route
    raise KeyError(spec.curve)


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h032_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_phase_candidates(
    e247_df: pd.DataFrame,
    h012_df: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    q: np.ndarray,
    cells: pd.DataFrame,
) -> pd.DataFrame:
    z_base = logit(e247_prob).reshape(-1)
    z_q = logit(q).reshape(-1)
    z_h012 = logit(h012_prob).reshape(-1)
    q_dir = z_q - z_base
    h012_dir = z_h012 - z_base
    rows: list[dict[str, Any]] = []
    seen: set[str] = {
        hashlib.sha1(np.round(h012_prob, 12).tobytes()).hexdigest()[:12],
        hashlib.sha1(np.round(e247_prob, 12).tobytes()).hexdigest()[:12],
    }

    # Include exact current H012 as the basin anchor in the phase table.
    rows.append(
        {
            "file": H012,
            "resolved_path": str((ROOT / H012).resolve()),
            "candidate_id": "anchor_h012_actual",
            "family": "anchor",
            "score_name": "anchor",
            "target_group": "all",
            "k": 1200,
            "alpha": 0.70,
            "curve": "actual",
            "changed_cells_vs_h012": 0,
            "changed_cells_vs_e247": int(np.sum(np.abs(h012_prob - e247_prob) > 1.0e-6)),
            "max_abs_prob_vs_h012": 0.0,
            "mean_abs_prob_vs_h012": 0.0,
            "cos_e247_to_h012": 1.0,
            "proj_e247_to_h012": 1.0,
            "phase_loss_delta_vs_e247": float(np.mean(bce(h012_prob, q) - bce(e247_prob, q))),
            "phase_loss_delta_vs_h012": 0.0,
        }
    )

    for spec in phase_specs():
        idx = pick_cells(cells, spec)
        if len(idx) == 0:
            continue
        mult = curve_multiplier(cells, spec, idx)
        out_z = z_base.copy()
        out_z[idx] = z_base[idx] + mult * q_dir[idx]
        out_prob = sigmoid(out_z).reshape(e247_prob.shape)
        digest = hashlib.sha1(np.round(out_prob, 12).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        candidate_id = f"{spec.score_name}_{spec.target_group}_k{spec.k}_a{spec.alpha:g}_{spec.curve}"
        path = write_submission(e247_df, out_prob, candidate_id)
        move = logit(out_prob).reshape(-1) - z_base
        denom = float(np.linalg.norm(move) * np.linalg.norm(h012_dir) + 1.0e-12)
        changed_vs_h012 = np.abs(out_prob - h012_prob) > 1.0e-6
        changed_vs_e247 = np.abs(out_prob - e247_prob) > 1.0e-6
        rows.append(
            {
                "file": f"hitl/h032_h012_phase_translator_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": candidate_id,
                "family": "phase",
                "score_name": spec.score_name,
                "target_group": spec.target_group,
                "k": int(len(idx)),
                "alpha": spec.alpha,
                "curve": spec.curve,
                "changed_cells_vs_h012": int(changed_vs_h012.sum()),
                "changed_rows_vs_h012": int(changed_vs_h012.any(axis=1).sum()),
                "changed_cells_vs_e247": int(changed_vs_e247.sum()),
                "changed_rows_vs_e247": int(changed_vs_e247.any(axis=1).sum()),
                "max_abs_prob_vs_h012": float(np.max(np.abs(out_prob - h012_prob))),
                "mean_abs_prob_vs_h012": float(np.mean(np.abs(out_prob - h012_prob))),
                "max_abs_prob_vs_e247": float(np.max(np.abs(out_prob - e247_prob))),
                "mean_abs_prob_vs_e247": float(np.mean(np.abs(out_prob - e247_prob))),
                "cos_e247_to_h012": float(move @ h012_dir / denom),
                "proj_e247_to_h012": float(move @ h012_dir / (h012_dir @ h012_dir + 1.0e-12)),
                "phase_loss_delta_vs_e247": float(np.mean(bce(out_prob, q) - bce(e247_prob, q))),
                "phase_loss_delta_vs_h012": float(np.mean(bce(out_prob, q) - bce(h012_prob, q))),
            }
        )
    variants = pd.DataFrame(rows)
    variants.to_csv(OUT / "h032_generated_phase_candidates.csv", index=False)
    return variants


def h024_feature_table(h024: object, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    known = h024.read_public_observations()
    refs = h024.build_reference_pack()
    known_rows = [
        {
            "file": rec["file"],
            "resolved_path": str(h024.locate(rec["file"]) or rec["file"]),
            "source": "known_public",
        }
        for rec in known.to_dict("records")
    ]
    var_rows = variants[["file", "resolved_path", "candidate_id", "family"]].copy()
    var_rows["source"] = "h032_phase"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True).drop_duplicates("file", keep="last")
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h032_h024_features.csv", index=False)

    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    blocked = {
        "file",
        "resolved_path",
        "source",
        "pool_file",
        "pool_resolved_path",
        "pool_candidate_id",
        "pool_family",
        "pool_source",
        "pool_known_public_lb",
        "known_public_lb",
        "public_lb",
    }
    cols = h024.numeric_feature_cols(known_features, blocked)
    cols_by_set = h024.feature_sets(cols)
    return known, features, cols_by_set


def ridge_predict_one(
    h024: object,
    known: pd.DataFrame,
    features: pd.DataFrame,
    cols: list[str],
    alpha: float,
) -> np.ndarray:
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    return h024.ridge_fit_predict(
        known_features[cols].to_numpy(dtype=np.float64),
        known_features["public_lb"].to_numpy(dtype=np.float64),
        features[cols].to_numpy(dtype=np.float64),
        alpha,
    )


def score_phase_candidates(
    h024: object,
    variants: pd.DataFrame,
    known: pd.DataFrame,
    features: pd.DataFrame,
    cols_by_set: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    model_no_h012, loo_no_h012 = h024.evaluate_known_models(known_no_h012[["file", "public_lb"]], features, cols_by_set)
    model_full, loo_full = h024.evaluate_known_models(known[["file", "public_lb"]], features, cols_by_set)
    model_no_h012.to_csv(OUT / "h032_pre_h012_h024_model_scores.csv", index=False)
    loo_no_h012.to_csv(OUT / "h032_pre_h012_h024_loo_predictions.csv", index=False)
    model_full.to_csv(OUT / "h032_full_h024_model_scores.csv", index=False)
    loo_full.to_csv(OUT / "h032_full_h024_loo_predictions.csv", index=False)

    pred_cols: dict[str, np.ndarray] = {}
    for set_name, alpha in [
        ("state", 100.0),
        ("state", 10.0),
        ("geometry", 100.0),
        ("geometry", 10.0),
    ]:
        if set_name not in cols_by_set:
            continue
        key = f"pre_{set_name}_a{alpha:g}"
        pred_cols[key] = ridge_predict_one(h024, known_no_h012, features, cols_by_set[set_name], alpha)
    for set_name, alpha in [("state", 100.0), ("geometry", 100.0)]:
        if set_name not in cols_by_set:
            continue
        key = f"full_{set_name}_a{alpha:g}"
        pred_cols[key] = ridge_predict_one(h024, known, features, cols_by_set[set_name], alpha)

    pred_frame = features[["file"]].copy()
    for key, pred in pred_cols.items():
        pred_frame[key] = pred
    pred_frame.to_csv(OUT / "h032_direct_decoder_predictions.csv", index=False)

    scored = variants.merge(pred_frame, on="file", how="left")
    scored["pre_state_best"] = scored[[c for c in scored.columns if c.startswith("pre_state")]].min(axis=1)
    scored["pre_state_mean"] = scored[[c for c in scored.columns if c.startswith("pre_state")]].mean(axis=1)
    scored["pre_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("pre_geometry")]].mean(axis=1)
    scored["full_state_mean"] = scored[[c for c in scored.columns if c.startswith("full_state")]].mean(axis=1)
    scored["full_geometry_mean"] = scored[[c for c in scored.columns if c.startswith("full_geometry")]].mean(axis=1)
    h012_pre_state = float(scored.loc[scored["candidate_id"].eq("anchor_h012_actual"), "pre_state_mean"].iloc[0])
    h012_phase_loss = float(scored.loc[scored["candidate_id"].eq("anchor_h012_actual"), "phase_loss_delta_vs_e247"].iloc[0])
    scored["pre_state_margin_vs_h012_pred"] = scored["pre_state_mean"] - h012_pre_state
    scored["phase_loss_margin_vs_h012"] = scored["phase_loss_delta_vs_e247"] - h012_phase_loss
    scored["h032_translator_score"] = (
        scored["pre_state_mean"].fillna(0.60)
        + 0.18 * np.maximum(scored["pre_geometry_mean"].fillna(0.60) - H012_LB, -0.03)
        + 0.08 * np.maximum(scored["full_state_mean"].fillna(0.60) - H012_LB, -0.02)
        + 0.025 * np.maximum(scored["phase_loss_margin_vs_h012"].fillna(0.01), 0.0)
        + 0.015 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0.0) - 0.18, 0.0)
        + 0.00002 * np.maximum(scored["changed_cells_vs_h012"].fillna(0.0) - 500, 0.0) / 500.0
    )
    scored = scored.sort_values(["h032_translator_score", "pre_state_mean", "phase_loss_delta_vs_e247"]).reset_index(drop=True)
    scored.to_csv(OUT / "h032_phase_candidate_scores.csv", index=False)
    return scored, model_no_h012, model_full


def public_perm_stress(h024: object, selected: pd.Series, known: pd.DataFrame, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known_no_h012 = known[known["file"] != H012].copy().reset_index(drop=True)
    null = h024.permutation_stress(
        known_no_h012[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h032_selected_pre_h012_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    if str(selected["candidate_id"]) == "anchor_h012_actual":
        out = pd.DataFrame([{"skipped": "selected_is_existing_h012_anchor"}])
        out.to_csv(OUT / "h032_selected_h025_rowperm_stress.csv", index=False)
        return out
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h032")
        rt26 = h026.prepare_runtime()
        rowperm = rt26.h025.row_permutation_candidate_stress(
            rt26.action_model,
            rt26.action_cols,
            str(selected["resolved_path"]),
            rt26.h012_prob,
            rt26.test_pcs,
            rt26.sample,
            n_perm=300,
        )
    except Exception as exc:  # pragma: no cover - diagnostic fallback.
        rowperm = pd.DataFrame([{"error": repr(exc)}])
    rowperm.to_csv(OUT / "h032_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h032_candidates", None
    selected = scored.iloc[0]
    if str(selected["candidate_id"]) == "anchor_h012_actual":
        return "diagnostic_only_translator_recovers_h012_anchor", None
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        selected_margin = float(selected["pre_state_mean"] - scored.loc[scored["candidate_id"].eq("anchor_h012_actual"), "pre_state_mean"].iloc[0])
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= selected_margin))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pre_state_margin_vs_h012_pred"]) <= -0.00035
        and float(selected["phase_loss_margin_vs_h012"]) <= 0.00020
        and float(selected["max_abs_prob_vs_h012"]) <= 0.16
        and public_perm_p <= 0.25
        and rowperm_p <= 0.35
    )
    if not gate:
        return "diagnostic_only_no_phase_sibling_clears_stress", None
    src = Path(str(selected["resolved_path"]))
    dst = ROOT / f"submission_h032_phase_translator_{safe_id(str(selected['candidate_id']), 72)}_uploadsafe.csv"
    shutil.copyfile(src, dst)
    return "promote_h032_phase_translator_big_bet", dst


def summarize(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (score_name, group, curve), part in scored.groupby(["score_name", "target_group", "curve"], dropna=False):
        best = part.iloc[0]
        rows.append(
            {
                "score_name": score_name,
                "target_group": group,
                "curve": curve,
                "n": len(part),
                "best_candidate_id": best["candidate_id"],
                "best_pre_state_mean": float(best["pre_state_mean"]),
                "best_pre_state_margin_vs_h012_pred": float(best["pre_state_margin_vs_h012_pred"]),
                "best_phase_loss_margin_vs_h012": float(best["phase_loss_margin_vs_h012"]),
                "best_changed_cells_vs_h012": int(best["changed_cells_vs_h012"]),
                "best_max_abs_prob_vs_h012": float(best["max_abs_prob_vs_h012"]),
            }
        )
    out = pd.DataFrame(rows).sort_values(["best_pre_state_mean", "best_phase_loss_margin_vs_h012"]).reset_index(drop=True)
    out.to_csv(OUT / "h032_family_summary.csv", index=False)
    return out


def write_report(
    cells: pd.DataFrame,
    scored: pd.DataFrame,
    family: pd.DataFrame,
    model_no_h012: pd.DataFrame,
    model_full: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    anchor = scored[scored["candidate_id"].eq("anchor_h012_actual")].iloc[0]
    selected = scored.iloc[0] if not scored.empty else None
    exact_repro = cells.sort_values("cell_score", ascending=False).head(1200)
    lines = [
        "# H032 H012 Phase-Translator HS-JEPA\n\n",
        "## Question\n\n",
        "H012 may be a phase point, not just a set of public-core cells. Can a state/action decoder that withholds H012's public score recover H012 or a stronger sibling from a dense E247-to-posterior phase diagram?\n\n",
        "## H012 Reproduction Check\n\n",
        f"- top-1200 H012-score cells reproduction max logit error: `{exact_repro['h012_reproduction_error'].max():.9f}`\n",
        f"- generated phase candidates including anchor: `{len(scored)}`\n",
        f"- anchor H012 phase loss delta vs E247: `{float(anchor['phase_loss_delta_vs_e247']):.9f}`\n",
        f"- anchor pre-H012 state mean prediction: `{float(anchor['pre_state_mean']):.9f}`\n",
        f"- anchor pre-H012 geometry mean prediction: `{float(anchor['pre_geometry_mean']):.9f}`\n\n",
        "## Decoder Health\n\n",
    ]
    if not model_no_h012.empty:
        top = model_no_h012.iloc[0]
        lines.append(
            f"- best pre-H012 decoder: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"LOO MAE `{top['loo_mae']:.9f}`, Spearman `{top['loo_spearman']:.9f}`, pairwise `{top['loo_pair_acc']:.9f}`\n"
        )
    state_rows = model_no_h012[model_no_h012["feature_set"].eq("state")].head(3)
    lines.append("- pre-H012 state decoder rows:\n\n")
    lines.append(md_table(state_rows[["feature_set", "alpha", "loo_mae", "loo_spearman", "loo_pair_acc"]], 3) + "\n\n")
    lines.append("## Selected Phase Point\n\n")
    if selected is not None:
        cols = [
            "candidate_id",
            "score_name",
            "target_group",
            "k",
            "alpha",
            "curve",
            "pre_state_mean",
            "pre_state_margin_vs_h012_pred",
            "pre_geometry_mean",
            "phase_loss_margin_vs_h012",
            "changed_cells_vs_h012",
            "max_abs_prob_vs_h012",
            "file",
        ]
        lines.append(md_table(scored[[c for c in cols if c in scored.columns]], 24) + "\n\n")
    lines.append("## Family Summary\n\n")
    lines.append(md_table(family, 24) + "\n\n")
    lines.append("## Stress\n\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n")
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns and selected is not None:
        selected_margin = float(selected["pre_state_margin_vs_h012_pred"])
        p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= selected_margin))
        lines.append(f"- pre-H012 public-score permutation p(lower margin): `{p:.9f}`\n")
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{p:.9f}`\n")
        lines.append(f"- real H025 top1200 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    elif not rowperm.empty:
        lines.append(f"- H025 row-permutation stress: `{rowperm.iloc[0].to_dict()}`\n")
    lines.append("\n## Interpretation\n\n")
    if decision == "diagnostic_only_translator_recovers_h012_anchor":
        lines.append(
            "The phase translator recovers the existing H012 anchor as the best point. "
            "That is positive architecture evidence: the H012 action is not arbitrary under the state/action view. "
            "It is negative submission evidence: the dense phase map did not find a stronger sibling.\n\n"
        )
    elif promoted is None:
        lines.append(
            "The phase map found non-anchor siblings, but none cleared the H012-relative stress gate. "
            "The translator is still too weak to move away from H012 safely.\n\n"
        )
    else:
        lines.append(
            "A non-anchor phase sibling cleared the stress gate. This is a high-information public test of the claim that H012's translator is learnable and not a one-file needle.\n\n"
        )
    lines.append("## Files\n\n")
    for path in [
        OUT / "h032_cell_phase_state.csv",
        OUT / "h032_generated_phase_candidates.csv",
        OUT / "h032_phase_candidate_scores.csv",
        OUT / "h032_family_summary.csv",
        OUT / "h032_pre_h012_h024_model_scores.csv",
        OUT / "h032_direct_decoder_predictions.csv",
        OUT / "h032_selected_pre_h012_public_perm_stress.csv",
        OUT / "h032_selected_h025_rowperm_stress.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h032_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    _, e247_df, h012_df, e247_prob, h012_prob, q = load_base(h024)
    cells = load_cell_state(e247_prob, h012_prob, q)
    variants = generate_phase_candidates(e247_df, h012_df, e247_prob, h012_prob, q, cells)
    known, features, cols_by_set = h024_feature_table(h024, variants)
    scored, model_no_h012, model_full = score_phase_candidates(h024, variants, known, features, cols_by_set)
    family = summarize(scored)
    selected = scored.iloc[0]
    public_perm = public_perm_stress(h024, selected, known, features, cols_by_set)
    rowperm = rowperm_stress(selected)
    decision, promoted = decide(scored, public_perm, rowperm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_pre_state_mean": selected["pre_state_mean"],
                "selected_pre_state_margin_vs_h012_pred": selected["pre_state_margin_vs_h012_pred"],
                "selected_phase_loss_margin_vs_h012": selected["phase_loss_margin_vs_h012"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h032_decision.csv", index=False)
    write_report(cells, scored, family, model_no_h012, model_full, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h032_decision.csv").to_string(index=False))
    print(scored.head(15).to_string(index=False))
    print(OUT / "h032_report.md")


if __name__ == "__main__":
    main()
