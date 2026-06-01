#!/usr/bin/env python3
"""H031: memory-conflict public-core HS-JEPA.

The V106 note says same-subject sleep-state/sensor-quality memory is a strong
world model. H014 then showed a sharper fact: most H012 public-equation gain
lives where that memory *disagrees* with H012, especially on S targets.

H031 flips the old "memory-compatible regularization" assumption. It treats
high-gain memory-disagreement cells as the public-equation core and asks whether
we can improve H012 by amplifying that core, paying budget with low-gain
memory-agree cells, or isolating the core as a smaller causal claim.
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
OUT = HITL / "h031_memory_conflict_public_core_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H012_LB = 0.5681234831

H014_DIR = HITL / "h014_sleep_state_memory_posterior_audit"
H030_DIR = HITL / "h030_rowtarget_identity_equation_jepa"


@dataclass(frozen=True)
class RouteSpec:
    family: str
    target_group: str
    core_k: int
    core_alpha: float
    rollback_k: int = 0
    rollback_alpha: float = 0.0
    base: str = "h012"


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def safe_id(text: str, limit: int = 116) -> str:
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
    return import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h031")


def load_base(h024: object) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    h012_df = h024.load_sub(H012)
    sample = h012_df[KEYS].copy()
    e247_df = h024.load_sub(E247, sample)
    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = e247_df[TARGETS].to_numpy(dtype=np.float64)
    h012_delta = logit(h012_prob) - logit(e247_prob)
    return sample, e247_df, h012_df, e247_prob, h012_prob, h012_delta


def load_cell_state(sample: pd.DataFrame, e247_prob: np.ndarray, h012_prob: np.ndarray) -> pd.DataFrame:
    cells = pd.read_csv(H014_DIR / "h014_memory_cells.csv")
    cells["target"] = cells["target"].astype(str)
    if not {"row", "target", "memory_disagrees_h012", "posterior_gain"}.issubset(cells.columns):
        raise ValueError("H014 memory cells are missing required columns")

    identity_path = H030_DIR / "h030_cell_identity_state.csv"
    if identity_path.exists():
        ident = pd.read_csv(identity_path)
        keep = [
            "row",
            "target",
            "score_identity_combo",
            "score_joint_vector_cell",
            "score_public_row_subset",
            "score_h012_posterior",
        ]
        ident = ident[[c for c in keep if c in ident.columns]].copy()
        cells = cells.merge(ident, on=["row", "target"], how="left")
    for col in ["score_identity_combo", "score_joint_vector_cell", "score_public_row_subset", "score_h012_posterior"]:
        if col not in cells.columns:
            cells[col] = 0.5
        cells[col] = cells[col].fillna(0.5)

    z_e247 = logit(e247_prob)
    z_h012 = logit(h012_prob)
    flat_rows = []
    for row in range(e247_prob.shape[0]):
        for ti, target in enumerate(TARGETS):
            flat_rows.append(
                {
                    "row": row,
                    "target": target,
                    "target_i": ti,
                    "e247_prob_check": e247_prob[row, ti],
                    "h012_prob_check": h012_prob[row, ti],
                    "h012_abs_logit_delta_check": abs(z_h012[row, ti] - z_e247[row, ti]),
                }
            )
    frame = pd.DataFrame(flat_rows)
    cells = frame.merge(cells, on=["row", "target"], how="left")
    cells["h012_changed"] = cells["h012_changed"].fillna(False).astype(bool)
    cells["memory_agrees_h012"] = cells["memory_agrees_h012"].fillna(False).astype(bool)
    cells["memory_disagrees_h012"] = cells["memory_disagrees_h012"].fillna(False).astype(bool)
    for col in [
        "posterior_gain",
        "memory_alignment",
        "memory_alignment_q",
        "row_full_reliability_q",
        "private_safe_score",
        "cell_score",
        "posterior_logit_delta",
        "memory_logit_delta",
    ]:
        if col not in cells.columns:
            cells[col] = 0.0
        cells[col] = cells[col].fillna(0.0)

    changed = cells["h012_changed"].to_numpy(dtype=bool)
    cells["gain_rank"] = 0.0
    cells.loc[changed, "gain_rank"] = rank01(cells.loc[changed, "posterior_gain"])
    cells["abs_move_rank"] = rank01(cells["h012_abs_logit_delta_check"])
    cells["anti_memory_rank"] = rank01(-cells["memory_alignment"])
    cells["low_gain_rank"] = rank01(cells["posterior_gain"], high=False)
    cells["target_group_Q"] = cells["target"].isin(["Q1", "Q2", "Q3"]).astype(float)
    cells["target_group_S"] = cells["target"].isin(["S1", "S2", "S3", "S4"]).astype(float)
    cells["target_group_S124"] = cells["target"].isin(["S1", "S2", "S4"]).astype(float)
    cells["target_group_Q3S"] = cells["target"].isin(["Q3", "S1", "S2", "S3", "S4"]).astype(float)

    disagree = cells["memory_disagrees_h012"].astype(float)
    agree = cells["memory_agrees_h012"].astype(float)
    cells["public_conflict_core_score"] = np.clip(
        0.34 * cells["gain_rank"]
        + 0.22 * disagree
        + 0.16 * cells["anti_memory_rank"]
        + 0.12 * cells["score_identity_combo"]
        + 0.08 * cells["score_joint_vector_cell"]
        + 0.08 * cells["abs_move_rank"],
        0.0,
        1.0,
    )
    cells["public_conflict_s_route_score"] = np.clip(
        cells["public_conflict_core_score"] * (0.65 + 0.35 * cells["target_group_S124"]),
        0.0,
        1.0,
    )
    cells["rollback_cost_score"] = np.clip(
        0.30 * agree
        + 0.28 * cells["low_gain_rank"]
        + 0.17 * cells["memory_alignment_q"]
        + 0.15 * cells["private_safe_score"]
        + 0.10 * cells["row_full_reliability_q"],
        0.0,
        1.0,
    )
    cells["h031_cell_role"] = np.where(
        (cells["h012_changed"]) & (cells["memory_disagrees_h012"]) & (cells["gain_rank"] >= 0.55),
        "conflict_core",
        np.where(
            (cells["h012_changed"]) & (cells["memory_agrees_h012"]) & (cells["gain_rank"] <= 0.45),
            "agree_cost",
            "other",
        ),
    )
    cells.to_csv(OUT / "h031_cell_state.csv", index=False)
    return cells


def target_mask(cells: pd.DataFrame, group: str) -> np.ndarray:
    if group == "all":
        return np.ones(len(cells), dtype=bool)
    mapping = {
        "S": ["S1", "S2", "S3", "S4"],
        "S124": ["S1", "S2", "S4"],
        "S12": ["S1", "S2"],
        "S2S4": ["S2", "S4"],
        "Q3S": ["Q3", "S1", "S2", "S3", "S4"],
        "Q3S3": ["Q3", "S3"],
        "Q": ["Q1", "Q2", "Q3"],
        "Q3": ["Q3"],
    }
    if group not in mapping:
        raise KeyError(group)
    return cells["target"].isin(mapping[group]).to_numpy(dtype=bool)


def pick_indices(
    cells: pd.DataFrame,
    score_col: str,
    k: int,
    group: str,
    require_changed: bool = True,
    require_disagree: bool = False,
    require_agree: bool = False,
) -> np.ndarray:
    mask = target_mask(cells, group).copy()
    if require_changed:
        mask &= cells["h012_changed"].to_numpy(dtype=bool)
    if require_disagree:
        mask &= cells["memory_disagrees_h012"].to_numpy(dtype=bool)
    if require_agree:
        mask &= cells["memory_agrees_h012"].to_numpy(dtype=bool)
    pool = cells[mask].copy()
    if pool.empty or k <= 0:
        return np.asarray([], dtype=int)
    pool = pool.sort_values(score_col, ascending=False).head(k)
    return (pool["row"].to_numpy(dtype=int) * len(TARGETS) + pool["target_i"].to_numpy(dtype=int)).astype(int)


def route_specs() -> list[RouteSpec]:
    specs: list[RouteSpec] = []
    for group in ["all", "S", "S124", "S12", "S2S4", "Q3S"]:
        for k in [60, 120, 240, 360, 520, 714]:
            for alpha in [0.05, 0.10, 0.18, 0.28, 0.40]:
                specs.append(RouteSpec("conflict_amp", group, k, alpha))
    for group in ["all", "S124", "Q3S"]:
        for k in [120, 240, 360, 520]:
            for rb_k in [60, 120, 240, 360]:
                for alpha in [0.08, 0.16, 0.28]:
                    specs.append(RouteSpec("conflict_swap", group, k, alpha, rb_k, 0.35))
                    specs.append(RouteSpec("conflict_swap", group, k, alpha, rb_k, 0.65))
    for group in ["all", "S124", "Q", "Q3S3"]:
        for rb_k in [60, 120, 240, 360, 486]:
            for rb_alpha in [0.20, 0.40, 0.70, 1.0]:
                specs.append(RouteSpec("agree_cost_rollback", group, 0, 0.0, rb_k, rb_alpha))
    for group in ["all", "S124", "Q3S"]:
        for k in [120, 240, 360, 520, 714]:
            specs.append(RouteSpec("core_only_from_e247", group, k, 1.00, base="e247"))
            specs.append(RouteSpec("core_over_from_e247", group, k, 1.15, base="e247"))
    return specs


def write_submission(template: pd.DataFrame, prob: np.ndarray, candidate_id: str) -> Path:
    out = template.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h031_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_candidates(
    sample: pd.DataFrame,
    e247_df: pd.DataFrame,
    h012_df: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    h012_delta: np.ndarray,
    cells: pd.DataFrame,
) -> pd.DataFrame:
    e247_z = logit(e247_prob).reshape(-1)
    h012_z = logit(h012_prob).reshape(-1)
    h012_dir = h012_z - e247_z
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for spec in route_specs():
        if spec.family in {"conflict_amp", "conflict_swap"}:
            score_col = "public_conflict_s_route_score" if spec.target_group in {"S", "S124", "S12", "S2S4"} else "public_conflict_core_score"
            core_idx = pick_indices(cells, score_col, spec.core_k, spec.target_group, require_disagree=True)
        elif spec.family in {"core_only_from_e247", "core_over_from_e247"}:
            score_col = "public_conflict_core_score"
            core_idx = pick_indices(cells, score_col, spec.core_k, spec.target_group, require_disagree=True)
        else:
            core_idx = np.asarray([], dtype=int)
        rb_idx = (
            pick_indices(cells, "rollback_cost_score", spec.rollback_k, spec.target_group, require_agree=True)
            if spec.rollback_k > 0
            else np.asarray([], dtype=int)
        )

        if spec.family in {"core_only_from_e247", "core_over_from_e247"}:
            out_z = e247_z.copy()
            if len(core_idx) == 0:
                continue
            out_z[core_idx] = e247_z[core_idx] + spec.core_alpha * h012_dir[core_idx]
            base_df = e247_df
        else:
            out_z = h012_z.copy()
            base_df = h012_df
            if len(core_idx):
                out_z[core_idx] = out_z[core_idx] + spec.core_alpha * h012_dir[core_idx]
            if len(rb_idx):
                out_z[rb_idx] = out_z[rb_idx] - spec.rollback_alpha * h012_dir[rb_idx]
        out_prob = sigmoid(out_z).reshape(e247_prob.shape)
        digest = hashlib.sha1(np.round(out_prob, 12).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        candidate_id = (
            f"{spec.family}_{spec.target_group}_core{spec.core_k}_a{spec.core_alpha:g}"
            f"_rb{spec.rollback_k}_r{spec.rollback_alpha:g}_{spec.base}"
        )
        path = write_submission(base_df, out_prob, candidate_id)
        move_h012 = logit(out_prob).reshape(-1) - h012_z
        move_e247 = logit(out_prob).reshape(-1) - e247_z
        denom = float(np.linalg.norm(move_e247) * np.linalg.norm(h012_dir) + 1.0e-12)
        changed_vs_h012 = np.abs(out_prob - h012_prob) > 1.0e-6
        changed_vs_e247 = np.abs(out_prob - e247_prob) > 1.0e-6
        core_score_mean = float(cells.iloc[core_idx]["public_conflict_core_score"].mean()) if len(core_idx) else 0.0
        rollback_score_mean = float(cells.iloc[rb_idx]["rollback_cost_score"].mean()) if len(rb_idx) else 0.0
        rows.append(
            {
                "file": f"hitl/h031_memory_conflict_public_core_jepa/{path.name}",
                "resolved_path": str(path),
                "candidate_id": candidate_id,
                "family": spec.family,
                "target_group": spec.target_group,
                "core_k": int(len(core_idx)),
                "core_alpha": spec.core_alpha,
                "rollback_k": int(len(rb_idx)),
                "rollback_alpha": spec.rollback_alpha,
                "base": spec.base,
                "core_score_mean": core_score_mean,
                "rollback_score_mean": rollback_score_mean,
                "changed_cells_vs_h012": int(changed_vs_h012.sum()),
                "changed_rows_vs_h012": int(changed_vs_h012.any(axis=1).sum()),
                "changed_cells_vs_e247": int(changed_vs_e247.sum()),
                "changed_rows_vs_e247": int(changed_vs_e247.any(axis=1).sum()),
                "mean_abs_prob_vs_h012": float(np.mean(np.abs(out_prob - h012_prob))),
                "max_abs_prob_vs_h012": float(np.max(np.abs(out_prob - h012_prob))),
                "mean_abs_logit_vs_h012": float(np.mean(np.abs(move_h012))),
                "max_abs_logit_vs_h012": float(np.max(np.abs(move_h012))),
                "cos_e247_to_h012": float(move_e247 @ h012_dir / denom),
                "proj_e247_to_h012": float(move_e247 @ h012_dir / (h012_dir @ h012_dir + 1.0e-12)),
                "mean_abs_logit_move": float(np.mean(np.abs(move_h012))),
            }
        )
    variants = pd.DataFrame(rows)
    variants.to_csv(OUT / "h031_generated_candidates.csv", index=False)
    return variants


def score_with_h024(h024: object, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
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
    var_rows["source"] = "h031_variant"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True)
    features = h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h031_h024_features.csv", index=False)
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
    model_scores, loo_preds = h024.evaluate_known_models(known_features[["file", "public_lb"]], features, cols_by_set)
    model_scores.to_csv(OUT / "h031_h024_model_scores.csv", index=False)
    loo_preds.to_csv(OUT / "h031_h024_known_loo_predictions.csv", index=False)
    candidate_scores, pred_samples = h024.score_candidates(known_features[["file", "public_lb"]], features, model_scores, cols_by_set)
    pred_samples.to_csv(OUT / "h031_h024_prediction_samples.csv", index=False)
    scored = variants.merge(candidate_scores, on="file", how="left", suffixes=("", "_h024"))
    scored["margin_vs_h012_pred"] = scored["pred_public_median"] - H012_LB
    scored["risk_width"] = scored["pred_public_p90"] - scored["pred_public_p10"]
    scored["h031_action_score"] = (
        scored["pred_public_median"].fillna(0.59)
        + 0.50 * scored["risk_width"].fillna(0.02)
        - 0.00020 * scored["support_better_than_h012"].fillna(0.0)
        + 0.00012 * np.maximum(scored["max_abs_prob_vs_h012"].fillna(0.0) - 0.12, 0.0)
        + 0.00008 * np.maximum(scored["changed_cells_vs_h012"].fillna(0.0) - 700.0, 0.0) / 700.0
    )
    scored = scored.sort_values(["h031_action_score", "pred_public_median"]).reset_index(drop=True)
    scored.to_csv(OUT / "h031_candidate_scores.csv", index=False)
    return scored, model_scores, features, cols_by_set


def public_perm_stress(h024: object, selected: pd.Series, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known = h024.read_public_observations()
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    null = h024.permutation_stress(
        known_features[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h031_selected_h024_public_perm_stress.csv", index=False)
    return null


def rowperm_stress(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h031")
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
    rowperm.to_csv(OUT / "h031_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def summarize_families(scored: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame()
    rows = []
    for (family, group), part in scored.groupby(["family", "target_group"], dropna=False):
        best = part.iloc[0]
        rows.append(
            {
                "family": family,
                "target_group": group,
                "n": len(part),
                "best_candidate_id": best["candidate_id"],
                "best_pred_public_median": float(best["pred_public_median"]),
                "best_margin_vs_h012": float(best["margin_vs_h012_pred"]),
                "best_support_better_than_h012": float(best["support_better_than_h012"]),
                "best_risk_width": float(best["risk_width"]),
                "median_pred_public": float(part["pred_public_median"].median()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["best_pred_public_median", "best_risk_width"]).reset_index(drop=True)
    out.to_csv(OUT / "h031_family_summary.csv", index=False)
    return out


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h031_candidates", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pred_public_median"]) <= H012_LB - 0.00055
        and float(selected["support_better_than_h012"]) >= 0.45
        and float(selected["risk_width"]) <= 0.0065
        and public_perm_p <= 0.20
        and rowperm_p <= 0.45
        and float(selected["max_abs_prob_vs_h012"]) <= 0.30
    )
    if not gate:
        return "diagnostic_only_memory_conflict_core_not_action_safe", None
    source = Path(str(selected["resolved_path"]))
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
    out = ROOT / f"submission_h031_memory_conflict_core_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return "primary_memory_conflict_public_core", out


def write_report(
    cells: pd.DataFrame,
    variants: pd.DataFrame,
    scored: pd.DataFrame,
    family: pd.DataFrame,
    model_scores: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    changed = cells[cells["h012_changed"]].copy()
    conflict = changed[changed["memory_disagrees_h012"]].copy()
    agree = changed[changed["memory_agrees_h012"]].copy()
    total_gain = float(changed["posterior_gain"].sum())
    target_summary = (
        changed.groupby("target")
        .agg(
            changed_cells=("target", "size"),
            posterior_gain=("posterior_gain", "sum"),
            disagree_cells=("memory_disagrees_h012", "sum"),
            agree_cells=("memory_agrees_h012", "sum"),
        )
        .reset_index()
    )
    target_summary["disagree_gain_share"] = [
        float(changed[(changed["target"] == t) & (changed["memory_disagrees_h012"])]["posterior_gain"].sum() / max(g, 1.0e-12))
        for t, g in zip(target_summary["target"], target_summary["posterior_gain"])
    ]
    target_summary["total_gain_share"] = target_summary["posterior_gain"] / max(total_gain, 1.0e-12)
    target_summary = target_summary.sort_values("posterior_gain", ascending=False)
    target_summary.to_csv(OUT / "h031_target_conflict_summary.csv", index=False)

    lines: list[str] = []
    lines.append("# H031 Memory-Conflict Public-Core HS-JEPA\n\n")
    lines.append("## Question\n\n")
    lines.append(
        "V106-style same-subject memory is strong, but H014 showed that H012's public-equation gain mostly lives where that memory disagrees. "
        "H031 asks whether those memory-conflict cells are the real public core that should be amplified or protected, rather than pruned.\n\n"
    )
    lines.append("## Observation\n\n")
    lines.append(f"- H012 changed cells: `{len(changed)}`\n")
    lines.append(f"- memory-disagree cells: `{len(conflict)}` with gain share `{float(conflict['posterior_gain'].sum() / max(total_gain, 1.0e-12)):.9f}`\n")
    lines.append(f"- memory-agree cells: `{len(agree)}` with gain share `{float(agree['posterior_gain'].sum() / max(total_gain, 1.0e-12)):.9f}`\n")
    lines.append("- target conflict summary:\n\n")
    lines.append(md_table(target_summary, 10) + "\n\n")
    lines.append("## Experiment\n\n")
    lines.append(
        "Generated candidate routes around H012: conflict-core amplification, conflict-core plus agree-cost rollback, agree-cost rollback alone, "
        "and core-only reconstruction from E247. The route score combines posterior gain, memory disagreement, anti-memory alignment, row-target identity, and joint-vector support.\n\n"
    )
    lines.append("## Result\n\n")
    lines.append(f"- generated candidates: `{len(variants)}`\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n\n")
    lines.append("## Family Summary\n\n")
    lines.append(md_table(family, 25) + "\n\n" if not family.empty else "_empty_\n\n")
    lines.append("## Top Candidates\n\n")
    cols = [
        "candidate_id",
        "family",
        "target_group",
        "pred_public_median",
        "pred_public_p10",
        "pred_public_p90",
        "margin_vs_h012_pred",
        "support_better_than_h012",
        "risk_width",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "file",
    ]
    lines.append(md_table(scored[[c for c in cols if c in scored.columns]], 25) + "\n\n" if not scored.empty else "_empty_\n\n")
    lines.append("## H024/H025 Stress\n\n")
    if not model_scores.empty:
        top = model_scores.iloc[0]
        lines.append(
            f"- best H024 decoder: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"LOO MAE `{top['loo_mae']:.9f}`, Spearman `{top['loo_spearman']:.9f}`, pairwise `{top['loo_pair_acc']:.9f}`\n"
        )
    if not scored.empty:
        selected = scored.iloc[0]
        lines.append(f"- selected diagnostic: `{selected['candidate_id']}`\n")
        lines.append(f"- selected predicted margin vs H012: `{float(selected['margin_vs_h012_pred']):.9f}`\n")
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns and not scored.empty:
        selected = scored.iloc[0]
        real_margin = float(selected["pred_public_median"] - H012_LB)
        p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
        lines.append(f"- H024 public-score permutation p(lower margin): `{p:.9f}`\n")
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- H025 row-permutation p(higher top1200 gain): `{p:.9f}`\n")
        lines.append(f"- real H025 top1200 gain: `{float(rowperm['real_top1200_sum'].iloc[0]):.9f}`\n")
    elif not rowperm.empty and "error" in rowperm.columns:
        lines.append(f"- H025 row-permutation stress error: `{rowperm['error'].iloc[0]}`\n")
    lines.append("\n## Interpretation\n\n")
    if promoted is None:
        lines.append(
            "Conflict-core amplification did not survive the action-health stresses. "
            "The memory-disagree observation remains an explanation of H012, not a safe post-H012 action. "
            "V106 memory is therefore positioned as a contrastive view: useful to expose H012's public-core cells, "
            "but not a replacement or mechanical amplifier for them.\n\n"
        )
    else:
        lines.append(
            "Conflict-core amplification survived the action-health stresses. "
            "This would mean H012 was under-amplified on public-equation event cells and the promoted file should be treated "
            "as a high-information public test of the memory-conflict public-core world model.\n\n"
        )
    lines.append("## Files\n\n")
    for path in [
        OUT / "h031_cell_state.csv",
        OUT / "h031_target_conflict_summary.csv",
        OUT / "h031_generated_candidates.csv",
        OUT / "h031_candidate_scores.csv",
        OUT / "h031_family_summary.csv",
        OUT / "h031_h024_model_scores.csv",
        OUT / "h031_selected_h024_public_perm_stress.csv",
        OUT / "h031_selected_h025_rowperm_stress.csv",
    ]:
        lines.append(f"- `{path.relative_to(ROOT)}`\n")
    (OUT / "h031_report.md").write_text("".join(lines), encoding="utf-8")


def main() -> None:
    h024 = load_h024()
    sample, e247_df, h012_df, e247_prob, h012_prob, h012_delta = load_base(h024)
    cells = load_cell_state(sample, e247_prob, h012_prob)
    variants = generate_candidates(sample, e247_df, h012_df, e247_prob, h012_prob, h012_delta, cells)
    if variants.empty:
        scored = pd.DataFrame()
        model_scores = pd.DataFrame()
        features = pd.DataFrame()
        cols_by_set: dict[str, list[str]] = {}
    else:
        scored, model_scores, features, cols_by_set = score_with_h024(h024, variants)
    family = summarize_families(scored)
    selected = scored.iloc[0] if len(scored) else None
    if selected is not None and len(features):
        public_perm = public_perm_stress(h024, selected, features, cols_by_set)
        rowperm = rowperm_stress(selected)
    else:
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
    decision, promoted = decide(scored, public_perm, rowperm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_candidate_id": None if selected is None else selected["candidate_id"],
                "selected_file": None if selected is None else selected["file"],
                "selected_pred_public_median": None if selected is None else float(selected["pred_public_median"]),
                "selected_support_better_than_h012": None if selected is None else float(selected["support_better_than_h012"]),
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h031_decision.csv", index=False)
    write_report(cells, variants, scored, family, model_scores, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h031_decision.csv").to_string(index=False))
    if len(scored):
        cols = [
            "candidate_id",
            "family",
            "target_group",
            "pred_public_median",
            "pred_public_p10",
            "pred_public_p90",
            "margin_vs_h012_pred",
            "support_better_than_h012",
            "risk_width",
            "file",
        ]
        print(scored[cols].head(15).to_string(index=False))
    print(OUT / "h031_report.md")


if __name__ == "__main__":
    main()
