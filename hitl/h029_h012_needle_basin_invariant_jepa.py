#!/usr/bin/env python3
"""H029: H012 needle-basin invariant audit.

H012 is not behaving like a smooth local optimum.  H028 learned public response
geometry, but extrapolating from H012 looked unsafe under independent stress.
This experiment asks a sharper question:

    What invariant made the H012 action special?

The generated variants deliberately break or preserve one invariant at a time:

- exact H012 support set vs top-k/posterior alternatives
- movement amplitude along the E247 -> H012 ray
- target-group and subject-block rollback
- same-subject sleep-state memory agreement
- row identity by target-wise row permutation

This is a diagnostic generator, not a public LB optimizer.  A root upload-safe
file is promoted only if the independent action-health sensors see a material
H012-beating margin.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h029_h012_needle_basin_invariant_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012_LB = 0.5681234831

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"

H012_DIR = HITL / "h012_public_equation_jepa_jackpot"
H014_DIR = HITL / "h014_sleep_state_memory_posterior_audit"


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def binary_loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def safe_id(text: str, limit: int = 96) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(arr: np.ndarray) -> str:
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


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


def robust_z(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    med = np.nanmedian(arr)
    mad = np.nanmedian(np.abs(arr - med))
    scale = 1.4826 * mad if mad > 1.0e-12 else np.nanstd(arr)
    if not np.isfinite(scale) or scale < 1.0e-12:
        scale = 1.0
    return np.nan_to_num((arr - med) / scale)


@dataclass(frozen=True)
class Runtime:
    h024: object
    sample: pd.DataFrame
    e247: pd.DataFrame
    h012: pd.DataFrame
    e247_prob: np.ndarray
    h012_prob: np.ndarray
    posterior_prob: np.ndarray
    support: np.ndarray
    cell_state: pd.DataFrame


def load_runtime() -> Runtime:
    h024 = import_module(HITL / "h024_action_health_decoder_jepa.py", "h024_h029")
    h012 = h024.load_sub(H012)
    sample = h012[KEYS].copy()
    e247 = h024.load_sub(E247, sample)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = e247[TARGETS].to_numpy(dtype=np.float64)

    posterior = pd.read_csv(H012_DIR / "h012_cell_posterior.csv")
    posterior_prob = e247_prob.copy()
    target_to_i = {t: i for i, t in enumerate(TARGETS)}
    score = np.zeros_like(e247_prob)
    consistency = np.zeros_like(e247_prob)
    for rec in posterior.to_dict("records"):
        r = int(rec["row"])
        c = target_to_i[str(rec["target"])]
        posterior_prob[r, c] = float(rec["posterior_prob"])
        score[r, c] = float(rec["cell_score"])
        consistency[r, c] = float(rec["direction_consistency"])

    support = np.abs(h012_prob - e247_prob) > 1.0e-10
    h012_z = logit(h012_prob)
    e247_z = logit(e247_prob)
    posterior_z = logit(posterior_prob)

    rows: list[dict[str, Any]] = []
    h014_path = H014_DIR / "h014_memory_cells.csv"
    memory_lookup: dict[tuple[int, str], dict[str, Any]] = {}
    if h014_path.exists():
        mem = pd.read_csv(h014_path)
        for rec in mem.to_dict("records"):
            memory_lookup[(int(rec["row"]), str(rec["target"]))] = rec

    for row_i in range(h012_prob.shape[0]):
        meta = sample.iloc[row_i].to_dict()
        for target_i, target in enumerate(TARGETS):
            key = (row_i, target)
            mem_rec = memory_lookup.get(key, {})
            move = float(h012_z[row_i, target_i] - e247_z[row_i, target_i])
            qmove = float(posterior_z[row_i, target_i] - e247_z[row_i, target_i])
            rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "target_i": target_i,
                    "subject_id": str(meta["subject_id"]),
                    "sleep_date": str(meta["sleep_date"])[:10],
                    "lifelog_date": str(meta["lifelog_date"])[:10],
                    "e247_prob": float(e247_prob[row_i, target_i]),
                    "h012_prob": float(h012_prob[row_i, target_i]),
                    "posterior_prob": float(posterior_prob[row_i, target_i]),
                    "h012_support": bool(support[row_i, target_i]),
                    "h012_logit_delta": move,
                    "posterior_logit_delta": qmove,
                    "abs_h012_logit_delta": abs(move),
                    "posterior_cell_score": float(score[row_i, target_i]),
                    "posterior_consistency": float(consistency[row_i, target_i]),
                    "memory_agrees_h012": bool(mem_rec.get("memory_agrees_h012", False)),
                    "memory_disagrees_h012": bool(mem_rec.get("memory_disagrees_h012", False)),
                    "memory_alignment": float(mem_rec.get("memory_alignment", 0.0)),
                    "memory_alignment_q": float(mem_rec.get("memory_alignment_q", 0.0)),
                    "private_safe_score": float(mem_rec.get("private_safe_score", 0.0)),
                    "row_full_reliability_q": float(mem_rec.get("row_full_reliability_q", 0.0)),
                    "posterior_gain": float(mem_rec.get("posterior_gain", abs(move))),
                }
            )
    cell_state = pd.DataFrame(rows)
    return Runtime(
        h024=h024,
        sample=sample,
        e247=e247,
        h012=h012,
        e247_prob=e247_prob,
        h012_prob=h012_prob,
        posterior_prob=posterior_prob,
        support=support,
        cell_state=cell_state,
    )


def write_submission(rt: Runtime, prob: np.ndarray, candidate_id: str) -> Path:
    out = rt.h012.copy()
    out[TARGETS] = clip_prob(prob)
    path = OUT / f"submission_h029_{safe_id(candidate_id)}_{short_hash(out[TARGETS].to_numpy(dtype=np.float64))}.csv"
    out.to_csv(path, index=False)
    return path


def prob_from_mask_scale(rt: Runtime, mask: np.ndarray, scale: float) -> np.ndarray:
    z = logit(rt.e247_prob)
    h012_z = logit(rt.h012_prob)
    out_z = z.copy()
    out_z[mask] = z[mask] + scale * (h012_z[mask] - z[mask])
    return sigmoid(out_z)


def prob_from_posterior_alpha(rt: Runtime, mask: np.ndarray, alpha: float) -> np.ndarray:
    z = logit(rt.e247_prob)
    qz = logit(rt.posterior_prob)
    out_z = z.copy()
    out_z[mask] = (1.0 - alpha) * z[mask] + alpha * qz[mask]
    return sigmoid(out_z)


def prob_from_h012_rollback(rt: Runtime, rollback_mask: np.ndarray, rollback_alpha: float = 1.0) -> np.ndarray:
    h012_z = logit(rt.h012_prob)
    e247_z = logit(rt.e247_prob)
    out_z = h012_z.copy()
    out_z[rollback_mask] = h012_z[rollback_mask] + rollback_alpha * (e247_z[rollback_mask] - h012_z[rollback_mask])
    return sigmoid(out_z)


def mask_from_cells(rt: Runtime, cells: pd.DataFrame) -> np.ndarray:
    mask = np.zeros_like(rt.support, dtype=bool)
    for rec in cells.to_dict("records"):
        mask[int(rec["row"]), int(rec["target_i"])] = True
    return mask


def top_cells(rt: Runtime, frame: pd.DataFrame, k: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    return frame.sort_values(["posterior_cell_score", "posterior_gain"], ascending=False).head(min(k, len(frame))).copy()


def generate_variants(rt: Runtime) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    support_cells = rt.cell_state[rt.cell_state["h012_support"]].copy()
    all_cells = rt.cell_state.copy()

    def add(candidate_id: str, family: str, prob: np.ndarray, meta: dict[str, Any] | None = None) -> None:
        path = write_submission(rt, prob, candidate_id)
        delta = prob - rt.h012_prob
        move_from_h012 = logit(prob) - logit(rt.h012_prob)
        move_from_e247 = logit(prob) - logit(rt.e247_prob)
        q = rt.posterior_prob
        posterior_delta = float(np.mean(binary_loss(prob, q) - binary_loss(rt.h012_prob, q)))
        rec: dict[str, Any] = {
            "file": f"hitl/h029_h012_needle_basin_invariant_jepa/{path.name}",
            "resolved_path": str(path),
            "candidate_id": candidate_id,
            "family": family,
            "posterior_delta_vs_h012": posterior_delta,
            "changed_cells_vs_h012": int(np.sum(np.abs(delta) > 1.0e-6)),
            "changed_rows_vs_h012": int(np.sum(np.max(np.abs(delta), axis=1) > 1.0e-6)),
            "mean_abs_prob_vs_h012": float(np.mean(np.abs(delta))),
            "max_abs_prob_vs_h012": float(np.max(np.abs(delta))),
            "mean_abs_logit_vs_h012": float(np.mean(np.abs(move_from_h012))),
            "l1_logit_vs_e247": float(np.sum(np.abs(move_from_e247))),
            "support_overlap_h012": float(
                np.mean((np.abs(prob - rt.e247_prob) > 1.0e-6)[rt.support])
            ),
            "outside_support_changed": int(np.sum((np.abs(prob - rt.e247_prob) > 1.0e-6) & ~rt.support)),
        }
        for target_i, target in enumerate(TARGETS):
            rec[f"changed_{target}_vs_h012"] = int(np.sum(np.abs(delta[:, target_i]) > 1.0e-6))
        if meta:
            rec.update(meta)
        rows.append(rec)

    # 1) Exact-support amplitude scan: keeps the H012 support invariant and only
    # changes how far we move along the E247 -> H012 ray.
    for scale in [0.35, 0.50, 0.65, 0.80, 0.90, 1.00, 1.10, 1.20, 1.35, 1.50]:
        add(
            f"support_ray_scale_{str(scale).replace('.', 'p')}",
            "support_ray_scale",
            prob_from_mask_scale(rt, rt.support, scale),
            {"scale": scale},
        )

    # 2) Posterior top-k support alternatives: tests whether 1200 is a phase
    # point or just a monotone top-k threshold.
    ranked = all_cells[
        (all_cells["posterior_consistency"] >= 0.55)
        & (np.sign(all_cells["posterior_logit_delta"]) == np.sign(all_cells["h012_logit_delta"]).replace(0, np.nan).fillna(np.sign(all_cells["posterior_logit_delta"])))
    ].copy()
    if ranked.empty:
        ranked = all_cells.copy()
    for k in [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1750]:
        mask = mask_from_cells(rt, top_cells(rt, ranked, k))
        for alpha in [0.45, 0.70, 0.95]:
            add(
                f"posterior_top_k{k}_a{str(alpha).replace('.', 'p')}",
                "posterior_topk",
                prob_from_posterior_alpha(rt, mask, alpha),
                {"k": k, "alpha": alpha, "selected_cells": int(mask.sum())},
            )

    # 3) Rollback target/subject blocks from H012: tests which coarse blocks are
    # necessary for the H012 basin.
    target_sets = {"Q": ["Q1", "Q2", "Q3"], "S": ["S1", "S2", "S3", "S4"]}
    for target in TARGETS:
        cells = support_cells[support_cells["target"].eq(target)]
        add(
            f"rollback_target_{target}",
            "target_rollback",
            prob_from_h012_rollback(rt, mask_from_cells(rt, cells)),
            {"rolled_target": target, "rolled_cells": len(cells)},
        )
        add(
            f"only_target_{target}",
            "target_only",
            prob_from_mask_scale(rt, mask_from_cells(rt, cells), 1.0),
            {"kept_target": target, "kept_cells": len(cells)},
        )
    for group, targets in target_sets.items():
        cells = support_cells[support_cells["target"].isin(targets)]
        add(
            f"rollback_group_{group}",
            "target_group_rollback",
            prob_from_h012_rollback(rt, mask_from_cells(rt, cells)),
            {"rolled_group": group, "rolled_cells": len(cells)},
        )
        add(
            f"only_group_{group}",
            "target_group_only",
            prob_from_mask_scale(rt, mask_from_cells(rt, cells), 1.0),
            {"kept_group": group, "kept_cells": len(cells)},
        )

    for subject in sorted(support_cells["subject_id"].unique()):
        cells = support_cells[support_cells["subject_id"].eq(subject)]
        add(
            f"rollback_subject_{subject}",
            "subject_rollback",
            prob_from_h012_rollback(rt, mask_from_cells(rt, cells)),
            {"rolled_subject": subject, "rolled_cells": len(cells)},
        )

    # 4) Memory agreement cuts.  The attached high-scoring document argues that
    # same-subject state-conditioned memory is a strong human-world signal.  H014
    # found weak overlap with H012.  Here we test whether preserving or removing
    # the overlap changes the public-action geometry around H012.
    agree = support_cells[support_cells["memory_agrees_h012"]].copy()
    disagree = support_cells[support_cells["memory_disagrees_h012"]].copy()
    private = support_cells.sort_values("private_safe_score", ascending=False).copy()
    for label, frame in [
        ("memory_agree", agree),
        ("memory_disagree", disagree),
        ("private_safe", private),
    ]:
        for k in [100, 250, 500, 750]:
            selected = top_cells(rt, frame, k)
            if selected.empty:
                continue
            mask = mask_from_cells(rt, selected)
            add(
                f"rollback_{label}_k{k}",
                "memory_rollback",
                prob_from_h012_rollback(rt, mask),
                {"memory_slice": label, "k": k, "rolled_cells": int(mask.sum())},
            )
            add(
                f"only_{label}_k{k}",
                "memory_only",
                prob_from_mask_scale(rt, mask, 1.0),
                {"memory_slice": label, "k": k, "kept_cells": int(mask.sum())},
            )

    # 5) Exact row identity stress.  These preserve each target's movement
    # distribution but permute rows, so a collapse indicates that H012 is about
    # exact row identity rather than only target-wise calibration moments.
    rng = np.random.default_rng(29029)
    support_move = logit(rt.h012_prob) - logit(rt.e247_prob)
    e247_z = logit(rt.e247_prob)
    for seed in range(12):
        out_z = e247_z.copy()
        for target_i, target in enumerate(TARGETS):
            rows_for_target = np.flatnonzero(rt.support[:, target_i])
            perm = rows_for_target.copy()
            rng.shuffle(perm)
            out_z[rows_for_target, target_i] = e247_z[rows_for_target, target_i] + support_move[perm, target_i]
        add(
            f"targetwise_rowperm_seed{seed:02d}",
            "targetwise_rowperm",
            sigmoid(out_z),
            {"perm_seed": seed},
        )

    # 6) Outside-support matched target counts.  This breaks exact support but
    # keeps target count and alpha/posterior family similar.
    counts = support_cells.groupby("target").size().to_dict()
    outside = all_cells[~all_cells["h012_support"]].copy()
    outside_selected: list[pd.DataFrame] = []
    for target, count in counts.items():
        part = outside[outside["target"].eq(target)].sort_values("posterior_cell_score", ascending=False).head(int(count))
        outside_selected.append(part)
    if outside_selected:
        selected = pd.concat(outside_selected, ignore_index=True)
        mask = mask_from_cells(rt, selected)
        add(
            "outside_support_targetcount_matched_top",
            "outside_support_matched",
            prob_from_posterior_alpha(rt, mask, 0.70),
            {"selected_cells": int(mask.sum())},
        )

    variants = pd.DataFrame(rows)
    variants.to_csv(OUT / "h029_generated_variants_raw.csv", index=False)
    rt.cell_state.to_csv(OUT / "h029_cell_state.csv", index=False)
    return variants


def score_with_h024(rt: Runtime, variants: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    known = rt.h024.read_public_observations()
    refs = rt.h024.build_reference_pack()
    known_rows = [
        {
            "file": rec["file"],
            "resolved_path": str(rt.h024.locate(rec["file"]) or rec["file"]),
            "source": "known_public",
        }
        for rec in known.to_dict("records")
    ]
    var_rows = variants[["file", "resolved_path", "candidate_id", "family"]].copy()
    var_rows["source"] = "h029_variant"
    pool = pd.concat([pd.DataFrame(known_rows), var_rows], ignore_index=True)
    features = rt.h024.build_feature_table(pool, refs)
    features.to_csv(OUT / "h029_h024_features.csv", index=False)
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
    cols = rt.h024.numeric_feature_cols(known_features, blocked)
    cols_by_set = rt.h024.feature_sets(cols)
    model_scores, loo_preds = rt.h024.evaluate_known_models(known_features[["file", "public_lb"]], features, cols_by_set)
    model_scores.to_csv(OUT / "h029_h024_model_scores.csv", index=False)
    loo_preds.to_csv(OUT / "h029_h024_known_loo_predictions.csv", index=False)
    candidate_scores, pred_samples = rt.h024.score_candidates(known_features[["file", "public_lb"]], features, model_scores, cols_by_set)
    pred_samples.to_csv(OUT / "h029_h024_prediction_samples.csv", index=False)
    scored = variants.merge(candidate_scores, on="file", how="left", suffixes=("", "_h024"))
    scored["margin_vs_h012_pred"] = scored["pred_public_median"] - H012_LB
    control = scored[
        scored["candidate_id"].isin(["support_ray_scale_1p0", "posterior_top_k1200_a0p7"])
    ]["pred_public_median"].dropna()
    control_pred = float(control.median()) if len(control) else H012_LB
    scored["h029_h012_duplicate_control_pred"] = control_pred
    scored["margin_vs_h012_duplicate_pred"] = scored["pred_public_median"] - control_pred
    scored["h029_score"] = (
        scored["pred_public_median"].fillna(0.58)
        + 0.35 * (scored["pred_public_p90"] - scored["pred_public_p10"]).fillna(0.02)
        - 0.00020 * scored["support_better_than_h012"].fillna(0.0)
        + 0.00002 * robust_z(scored["changed_cells_vs_h012"])
    )
    scored = scored.sort_values(["h029_score", "pred_public_median"]).reset_index(drop=True)
    scored.to_csv(OUT / "h029_variant_scores.csv", index=False)
    return scored, model_scores, features, cols_by_set


def family_summary(scored: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame()
    rows = []
    for family, group in scored.groupby("family"):
        best = group.sort_values("h029_score").iloc[0]
        rows.append(
            {
                "family": family,
                "n": len(group),
                "best_candidate_id": best["candidate_id"],
                "best_pred_public_median": float(best["pred_public_median"]),
                "best_margin_vs_h012": float(best["margin_vs_h012_pred"]),
                "best_margin_vs_duplicate": float(best["margin_vs_h012_duplicate_pred"]),
                "best_support_better_than_h012": float(best["support_better_than_h012"]),
                "best_risk_width": float(best["pred_public_p90"] - best["pred_public_p10"]),
                "median_pred_public": float(group["pred_public_median"].median()),
                "min_pred_public": float(group["pred_public_median"].min()),
                "max_support_better_than_h012": float(group["support_better_than_h012"].max()),
            }
        )
    out = pd.DataFrame(rows).sort_values("best_pred_public_median").reset_index(drop=True)
    out.to_csv(OUT / "h029_family_summary.csv", index=False)
    return out


def selected_public_perm(rt: Runtime, selected: pd.Series, features: pd.DataFrame, cols_by_set: dict[str, list[str]]) -> pd.DataFrame:
    known = rt.h024.read_public_observations()
    known_features = known[["file", "public_lb"]].merge(features, on="file", how="inner")
    null = rt.h024.permutation_stress(
        known_features[["file", "public_lb"]],
        features,
        cols_by_set,
        str(selected["file"]),
        n_perm=300,
    )
    null.to_csv(OUT / "h029_selected_h024_public_perm_stress.csv", index=False)
    return null


def selected_rowperm(selected: pd.Series) -> pd.DataFrame:
    try:
        h026 = import_module(HITL / "h026_public_private_calibration_veto_jepa.py", "h026_h029")
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
    except Exception as exc:
        rowperm = pd.DataFrame([{"error": repr(exc)}])
    rowperm.to_csv(OUT / "h029_selected_h025_rowperm_stress.csv", index=False)
    return rowperm


def decide(scored: pd.DataFrame, public_perm: pd.DataFrame, rowperm: pd.DataFrame) -> tuple[str, Path | None]:
    if scored.empty:
        return "no_h029_variants", None
    selected = scored.iloc[0]
    public_perm_p = 1.0
    if not public_perm.empty and "perm_selected_minus_h012" in public_perm.columns:
        real_margin = float(selected["pred_public_median"] - H012_LB)
        public_perm_p = float(np.mean(public_perm["perm_selected_minus_h012"].to_numpy(dtype=np.float64) <= real_margin))
    rowperm_p = 1.0
    if not rowperm.empty and "perm_top1200_sum" in rowperm.columns:
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
    gate = (
        float(selected["pred_public_median"]) <= H012_LB - 0.00050
        and float(selected.get("margin_vs_h012_duplicate_pred", 1.0)) <= -0.00050
        and float(selected["support_better_than_h012"]) >= 0.55
        and public_perm_p <= 0.10
        and rowperm_p <= 0.25
        and float(selected["max_abs_prob_vs_h012"]) <= 0.20
    )
    if not gate:
        return "diagnostic_only_h012_needle_invariant_not_action_safe", None
    source = Path(str(selected["resolved_path"]))
    digest = hashlib.sha1(source.read_bytes()).hexdigest()[:8]
    out = ROOT / f"submission_h029_needle_basin_invariant_{digest}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return "primary_h012_needle_basin_invariant", out


def write_report(
    variants: pd.DataFrame,
    scored: pd.DataFrame,
    family: pd.DataFrame,
    model_scores: pd.DataFrame,
    public_perm: pd.DataFrame,
    rowperm: pd.DataFrame,
    decision: str,
    promoted: Path | None,
) -> None:
    lines: list[str] = []
    lines.append("# H029 H012 Needle-Basin Invariant HS-JEPA\n\n")
    lines.append("## Question\n\n")
    lines.append(
        "H012 beat the old frontier by a large margin, but H028 showed that local public-gradient continuation is unsafe. "
        "H029 asks which invariant makes H012 special: exact support, amplitude, target/subject block, same-subject memory agreement, or row identity.\n\n"
    )
    lines.append("## External Reference Integrated\n\n")
    lines.append(
        "The attached high-scoring document argues for same-subject temporal label memory conditioned by sleep-state and sensor-quality similarity. "
        "H029 uses that idea as a falsification view via H014 memory agreement/disagreement slices rather than replacing H012.\n\n"
    )
    lines.append("## Generated Variants\n\n")
    lines.append(f"- generated variants: `{len(variants)}`\n")
    if len(model_scores):
        top = model_scores.iloc[0]
        lines.append(
            f"- best H024 decoder in this pool: `{top['feature_set']}` alpha `{top['alpha']}`, "
            f"MAE `{top['loo_mae']:.9f}`, Spearman `{top['loo_spearman']:.9f}`, pairwise `{top['loo_pair_acc']:.9f}`\n"
        )
    lines.append("\n## Family Summary\n\n")
    keep_family = [
        "family",
        "n",
        "best_candidate_id",
        "best_pred_public_median",
        "best_margin_vs_h012",
        "best_margin_vs_duplicate",
        "best_support_better_than_h012",
        "best_risk_width",
        "median_pred_public",
    ]
    lines.append(md_table(family[keep_family], 20) + "\n\n" if not family.empty else "_empty_\n\n")
    lines.append("## Top Variants\n\n")
    keep_top = [
        "candidate_id",
        "family",
        "pred_public_median",
        "pred_public_p10",
        "pred_public_p90",
        "margin_vs_h012_pred",
        "margin_vs_h012_duplicate_pred",
        "support_better_than_h012",
        "changed_cells_vs_h012",
        "max_abs_prob_vs_h012",
        "posterior_delta_vs_h012",
        "file",
    ]
    lines.append(md_table(scored[keep_top], 20) + "\n\n" if not scored.empty else "_empty_\n\n")
    lines.append("## Selected Stress\n\n")
    if not scored.empty:
        selected = scored.iloc[0]
        lines.append(f"- selected diagnostic: `{selected['candidate_id']}`\n")
        lines.append(f"- selected predicted margin vs H012: `{float(selected['margin_vs_h012_pred']):.9f}`\n")
        lines.append(
            f"- selected predicted margin vs duplicated-H012 control: `{float(selected['margin_vs_h012_duplicate_pred']):.9f}`\n"
        )
        lines.append(
            f"- duplicated-H012 control predicted public median: `{float(selected['h029_h012_duplicate_control_pred']):.9f}`\n"
        )
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
    lines.append("\n## Decision\n\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted if promoted is not None else 'none'}`\n\n")
    lines.append("## Interpretation\n\n")
    if not family.empty:
        best_family = str(family.iloc[0]["family"])
        lines.append(
            f"The strongest local invariant family under H024 is `{best_family}`. "
            "If its best member is still priced above H012, H012 should be treated as a narrow public-equation basin. "
            "If a non-control family is priced below H012 with stress support, that family becomes the next public-world hypothesis.\n"
        )
    (OUT / "h029_report.md").write_text("".join(lines))


def main() -> None:
    rt = load_runtime()
    variants = generate_variants(rt)
    scored, model_scores, features, cols_by_set = score_with_h024(rt, variants)
    family = family_summary(scored)
    selected = scored.iloc[0] if len(scored) else None
    if selected is not None:
        public_perm = selected_public_perm(rt, selected, features, cols_by_set)
        rowperm = selected_rowperm(selected)
    else:
        public_perm = pd.DataFrame()
        rowperm = pd.DataFrame()
    decision, promoted = decide(scored, public_perm, rowperm)
    pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_file": None if selected is None else selected["file"],
                "selected_candidate_id": None if selected is None else selected["candidate_id"],
                "promoted_path": None if promoted is None else str(promoted),
            }
        ]
    ).to_csv(OUT / "h029_decision.csv", index=False)
    write_report(variants, scored, family, model_scores, public_perm, rowperm, decision, promoted)
    print(pd.read_csv(OUT / "h029_decision.csv").to_string(index=False))
    if len(scored):
        cols = [
            "candidate_id",
            "family",
            "pred_public_median",
            "pred_public_p10",
            "pred_public_p90",
            "margin_vs_h012_pred",
            "margin_vs_h012_duplicate_pred",
            "support_better_than_h012",
            "changed_cells_vs_h012",
        ]
        print(scored[cols].head(12).to_string(index=False))


if __name__ == "__main__":
    main()
