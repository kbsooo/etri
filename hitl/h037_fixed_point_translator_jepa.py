#!/usr/bin/env python3
"""H037: fixed-point translator HS-JEPA.

H036 found a non-random hidden public-world posterior, but direct movement
toward its conditional labels left the H012 action basin.  H037 tests a sharper
translator hypothesis:

    The missing action is not "move to the world posterior".
    It is "translate world pressure through H012's successful ray".

So H037 keeps H012's support fixed.  It only changes amplitudes on cells that
H012 already moved from E247, and every change stays on the E247 -> H012 ray:
aligned cells can move a little farther, conflict cells can be damped, and
mixed actions can trade those two.  If this works, H012 is not merely a locked
point; it is a fixed-point action manifold with a reusable amplitude law.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h037_fixed_point_translator_jepa"
ANALYSIS = ROOT / "analysis_outputs"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def locate(name: str | Path) -> Path | None:
    path = Path(str(name))
    probes = [path] if path.is_absolute() else [path, ROOT / path, ANALYSIS / path, HITL / path]
    for probe in probes:
        if probe.exists():
            return probe.resolve()
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        keep.append(ch if ch.isalnum() or ch in "._-" else "_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(prob, 12).tobytes()).hexdigest()[:8]


def rank_pct(x: pd.Series | np.ndarray) -> pd.Series:
    s = pd.Series(np.asarray(x, dtype=np.float64))
    if s.nunique(dropna=True) <= 1:
        return pd.Series(np.full(len(s), 0.5))
    return s.rank(method="average", pct=True)


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


def load_h036_world(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    q = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    cell_score = np.zeros_like(q)
    row_public = np.zeros(len(sample), dtype=np.float64)
    target_idx = {t: i for i, t in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        row = int(rec["row"])
        t_i = target_idx[str(rec["target"])]
        q[row, t_i] = float(rec["world_q_cond"])
        cell_score[row, t_i] = float(rec["cell_world_score"])
        row_public[row] = max(row_public[row], float(rec["row_public_prob"]))
    if np.isnan(q).any():
        raise ValueError("H036 q_cond is incomplete")
    return clip_prob(q), cell_score, row_public


def weighted_delta(prob: np.ndarray, base: np.ndarray, q: np.ndarray, weight: np.ndarray) -> float:
    w = np.asarray(weight, dtype=np.float64)
    w = np.where(np.isfinite(w), w, 0.0)
    if w.ndim == 1:
        w = np.repeat(w[:, None], len(TARGETS), axis=1)
    w = np.clip(w, 0.0, None)
    if float(w.sum()) <= 1.0e-12:
        w = np.ones_like(base)
    return float(np.sum(w * (bce(prob, q) - bce(base, q))) / np.sum(w))


def make_candidate(
    sample: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    gamma: np.ndarray,
    changed_mask: np.ndarray,
    candidate_id: str,
) -> tuple[Path, np.ndarray]:
    z_e247 = logit(e247_prob)
    z_h012 = logit(h012_prob)
    z = z_h012.copy()
    z[changed_mask] = z_e247[changed_mask] + gamma[changed_mask] * (z_h012[changed_mask] - z_e247[changed_mask])
    prob = h012_prob.copy()
    prob[changed_mask] = sigmoid(z[changed_mask])
    path = OUT / f"submission_{candidate_id}_{short_hash(prob)}.csv"
    write_submission(sample, prob, path)
    return path, prob


def generate_candidates(
    sample: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    q_cond: np.ndarray,
    cell_score: np.ndarray,
    row_public: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    z_e247 = logit(e247_prob)
    z_h012 = logit(h012_prob)
    z_q = logit(q_cond)
    support = np.abs(h012_prob - e247_prob) > 1.0e-6
    ray = z_h012 - z_e247
    world_from_h012 = z_q - z_h012
    aligned = support & (np.sign(ray) == np.sign(world_from_h012))
    conflict = support & (np.sign(ray) != np.sign(world_from_h012))
    row_weight = np.repeat(row_public[:, None], len(TARGETS), axis=1)
    world_weight = 0.55 * row_weight + 0.45 * (cell_score / (np.nanmax(cell_score) + 1.0e-12))
    world_weight = np.where(support, world_weight, 0.0)
    score = cell_score + 0.25 * row_weight + 0.05 * np.abs(ray)
    flat_order = np.argsort(-score.reshape(-1))
    align_order = np.argsort(-np.where(aligned, score, -np.inf).reshape(-1))
    conflict_order = np.argsort(-np.where(conflict, score, -np.inf).reshape(-1))
    n_cells = h012_prob.size
    rows = []
    align_rows = []
    generated: set[str] = set()

    def add_family(family: str, gammas: dict[int, float]) -> None:
        gamma = np.ones_like(h012_prob)
        changed = np.zeros_like(support, dtype=bool)
        for flat_idx, val in gammas.items():
            if 0 <= flat_idx < n_cells:
                r = flat_idx // len(TARGETS)
                t = flat_idx % len(TARGETS)
                if support[r, t]:
                    gamma[r, t] = val
                    changed[r, t] = abs(val - 1.0) > 1.0e-12
        if not changed.any():
            return
        cid = safe_id(f"h037_{family}_c{int(changed.sum())}")
        if cid in generated:
            return
        generated.add(cid)
        path, prob = make_candidate(sample, e247_prob, h012_prob, gamma, changed, cid)
        rows.append(
            {
                "candidate_id": path.stem.replace("submission_", ""),
                "file": path.name,
                "resolved_path": str(path),
                "family": family,
                "changed_cells": int(changed.sum()),
                "changed_rows": int(np.sum(changed.any(axis=1))),
                "new_support_cells": int(np.sum(changed & ~support)),
                "support_cells_changed": int(np.sum(changed & support)),
                "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - z_h012))),
                "world_row_delta_vs_h012": weighted_delta(prob, h012_prob, q_cond, row_public),
                "world_cell_delta_vs_h012": weighted_delta(prob, h012_prob, q_cond, world_weight),
                "support_world_cell_delta_vs_h012": weighted_delta(
                    prob, h012_prob, q_cond, np.where(support, world_weight, 0.0)
                ),
                "ray_cosine": float(
                    np.sum((logit(prob) - z_h012) * ray)
                    / (np.linalg.norm(logit(prob) - z_h012) * np.linalg.norm(ray) + 1.0e-12)
                ),
            }
        )

    for k in [40, 80, 140, 220, 360, 520, 760]:
        chosen = [i for i in align_order[: min(k, len(align_order))] if np.isfinite(score.reshape(-1)[i])]
        for g in [1.015, 1.03, 1.06, 1.10, 1.16]:
            add_family(f"align_amp_k{k}_g{g:g}", {int(i): g for i in chosen})

    for k in [30, 60, 100, 160, 240, 297]:
        chosen = [i for i in conflict_order[: min(k, len(conflict_order))] if np.isfinite(score.reshape(-1)[i])]
        for g in [0.92, 0.84, 0.72, 0.55, 0.35]:
            add_family(f"conflict_damp_k{k}_g{g:g}", {int(i): g for i in chosen})

    for ka in [140, 260, 420, 700]:
        a_chosen = [i for i in align_order[: min(ka, len(align_order))] if np.isfinite(score.reshape(-1)[i])]
        for kc in [60, 120, 220]:
            c_chosen = [i for i in conflict_order[: min(kc, len(conflict_order))] if np.isfinite(score.reshape(-1)[i])]
            for ga, gc in [(1.03, 0.84), (1.06, 0.72), (1.10, 0.55)]:
                gammas = {int(i): ga for i in a_chosen}
                gammas.update({int(i): gc for i in c_chosen})
                add_family(f"dual_a{ka}_c{kc}_ga{ga:g}_gc{gc:g}", gammas)

    for target in TARGETS:
        t_i = TARGETS.index(target)
        target_flat = [r * len(TARGETS) + t_i for r in range(len(sample)) if support[r, t_i]]
        target_flat = sorted(target_flat, key=lambda i: score.reshape(-1)[i], reverse=True)
        for k in [35, 70, 120, len(target_flat)]:
            chosen = target_flat[: min(k, len(target_flat))]
            for g in [0.88, 0.94, 1.03, 1.07]:
                add_family(f"target_{target}_ray_k{k}_g{g:g}", {int(i): g for i in chosen})

    row_order = np.argsort(-row_public)
    for r_count in [15, 30, 50, 80, 120]:
        chosen_rows = row_order[:r_count]
        chosen = []
        for r in chosen_rows:
            for t_i in range(len(TARGETS)):
                if support[r, t_i]:
                    chosen.append(int(r * len(TARGETS) + t_i))
        for g in [0.90, 0.96, 1.04, 1.08]:
            add_family(f"rowpublic_r{r_count}_g{g:g}", {int(i): g for i in chosen})

    # Small direct q-pulls, still restricted to H012 support.  This is included
    # as a negative/contrastive translator: if it wins, direct q was not the
    # problem; if it fails, ray-preservation is the more important constraint.
    for k in [80, 180, 360, 700, 1000]:
        chosen = [i for i in flat_order[: min(k, len(flat_order))] if support.reshape(-1)[i]]
        for alpha in [0.03, 0.06, 0.10, 0.16]:
            z = z_h012.copy()
            mask = np.zeros_like(support, dtype=bool)
            for i in chosen:
                r = int(i) // len(TARGETS)
                t = int(i) % len(TARGETS)
                mask[r, t] = True
            if not mask.any():
                continue
            z[mask] = (1.0 - alpha) * z_h012[mask] + alpha * z_q[mask]
            prob = h012_prob.copy()
            prob[mask] = sigmoid(z[mask])
            cid = safe_id(f"h037_support_qpull_k{k}_a{alpha:g}_c{int(mask.sum())}")
            if cid in generated:
                continue
            generated.add(cid)
            path = OUT / f"submission_{cid}_{short_hash(prob)}.csv"
            write_submission(sample, prob, path)
            rows.append(
                {
                    "candidate_id": path.stem.replace("submission_", ""),
                    "file": path.name,
                    "resolved_path": str(path),
                    "family": f"support_qpull_k{k}",
                    "changed_cells": int(mask.sum()),
                    "changed_rows": int(np.sum(mask.any(axis=1))),
                    "new_support_cells": 0,
                    "support_cells_changed": int(mask.sum()),
                    "mean_abs_prob_move_h012": float(np.mean(np.abs(prob - h012_prob))),
                    "max_abs_prob_move_h012": float(np.max(np.abs(prob - h012_prob))),
                    "mean_abs_logit_move_h012": float(np.mean(np.abs(logit(prob) - z_h012))),
                    "world_row_delta_vs_h012": weighted_delta(prob, h012_prob, q_cond, row_public),
                    "world_cell_delta_vs_h012": weighted_delta(prob, h012_prob, q_cond, world_weight),
                    "support_world_cell_delta_vs_h012": weighted_delta(
                        prob, h012_prob, q_cond, np.where(support, world_weight, 0.0)
                    ),
                    "ray_cosine": float(
                        np.sum((logit(prob) - z_h012) * ray)
                        / (np.linalg.norm(logit(prob) - z_h012) * np.linalg.norm(ray) + 1.0e-12)
                    ),
                }
            )

    summary_rows = []
    for name, mask in [
        ("support", support),
        ("aligned_support", aligned),
        ("conflict_support", conflict),
        ("outside_support_high_world", (~support) & (cell_score >= np.quantile(cell_score.reshape(-1), 0.99))),
    ]:
        summary_rows.append(
            {
                "region": name,
                "cells": int(mask.sum()),
                "cell_score_sum": float(cell_score[mask].sum()) if mask.any() else 0.0,
                "cell_score_mean": float(cell_score[mask].mean()) if mask.any() else 0.0,
                "targets": str({t: int(mask[:, i].sum()) for i, t in enumerate(TARGETS)}),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h037")
    h024_features, h024_models, h024_preds = h036.h024_score_candidates(candidates)
    scored = candidates.copy()
    if not h024_preds.empty:
        scored = scored.merge(h024_preds, on="resolved_path", how="left")
    h025_scores, h025_cells = h036.h025_score_candidates(scored)
    if not h025_scores.empty:
        keep = [
            "file",
            "h025_score",
            "pred_gain_top1200_sum",
            "pred_gain_mean_moved",
            "pred_positive_rate_moved",
            "ood_abs_delta_rate",
        ]
        scored = scored.merge(h025_scores[[c for c in keep if c in h025_scores.columns]], on="file", how="left")
    h024_margin = scored.get("pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=scored.index)).fillna(0.01)
    h024_support = scored.get("pre_h012_h024_support_better_than_h012", pd.Series(0.0, index=scored.index)).fillna(0.0)
    h025_score = scored.get("h025_score", pd.Series(0.0, index=scored.index)).fillna(0.0)
    scored["h037_score"] = (
        rank_pct(scored["world_cell_delta_vs_h012"])
        + rank_pct(scored["support_world_cell_delta_vs_h012"])
        + rank_pct(h024_margin)
        + rank_pct(h025_score)
        - 0.50 * h024_support
        + 0.20 * rank_pct(scored["max_abs_prob_move_h012"])
    )
    scored = scored.sort_values(["h037_score", "world_cell_delta_vs_h012"]).reset_index(drop=True)
    return scored, h024_features, h024_models, h025_cells


def run_rowperm(selected_file: str) -> pd.DataFrame:
    h036 = import_module(HITL / "h036_global_public_world_solver_jepa.py", "h036_for_h037_rowperm")
    return h036.run_rowperm_stress(selected_file)


def decide(scored: pd.DataFrame, rowperm: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no candidates generated"}])
    selected = scored.iloc[0]
    pre_margin = float(selected.get("pre_h012_h024_margin_vs_h012_median", np.nan))
    pre_support = float(selected.get("pre_h012_h024_support_better_than_h012", np.nan))
    world_cell = float(selected["world_cell_delta_vs_h012"])
    world_row = float(selected["world_row_delta_vs_h012"])
    rowperm_p = 1.0
    rowperm_real = np.nan
    if not rowperm.empty:
        rowperm_real = float(rowperm["real_top1200_sum"].iloc[0])
        rowperm_p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm_real))
    promote = bool(
        world_cell < -0.00020
        and world_row < -0.00008
        and np.isfinite(pre_margin)
        and pre_margin < -0.00010
        and np.isfinite(pre_support)
        and pre_support >= 0.60
        and rowperm_p <= 0.35
    )
    reasons = []
    if world_cell >= -0.00020:
        reasons.append("world-cell gain too small")
    if world_row >= -0.00008:
        reasons.append("world-row gain too small")
    if not np.isfinite(pre_margin) or pre_margin >= -0.00010:
        reasons.append("H024 pre-H012 margin not below H012")
    if not np.isfinite(pre_support) or pre_support < 0.60:
        reasons.append("H024 support below 60%")
    if rowperm_p > 0.35:
        reasons.append("H025 row permutation stress weak")
    return pd.DataFrame(
        [
            {
                "decision": "promote" if promote else "do_not_promote",
                "promote": promote,
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "world_row_delta_vs_h012": world_row,
                "world_cell_delta_vs_h012": world_cell,
                "pre_h012_h024_margin_vs_h012_median": pre_margin,
                "pre_h012_h024_support_better_than_h012": pre_support,
                "rowperm_real_top1200_sum": rowperm_real,
                "rowperm_p_perm_ge_real": rowperm_p,
                "reason": "; ".join(reasons) if reasons else "all promotion gates passed",
            }
        ]
    )


def write_report(
    align_summary: pd.DataFrame,
    scored: pd.DataFrame,
    decision: pd.DataFrame,
    rowperm: pd.DataFrame,
) -> None:
    lines = []
    lines.append("# H037 Fixed-Point Translator HS-JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "Can H036's hidden public-world pressure be translated through H012's successful E247-to-H012 ray, "
        "without opening new support cells or leaving the H012 action basin?\n"
    )
    lines.append("## Alignment summary\n")
    lines.append(md_table(align_summary, len(align_summary)))
    lines.append("\n\n## Gate counts\n")
    h024_margin = scored.get("pre_h012_h024_margin_vs_h012_median", pd.Series(np.nan, index=scored.index))
    h024_support = scored.get("pre_h012_h024_support_better_than_h012", pd.Series(np.nan, index=scored.index))
    gate_counts = pd.DataFrame(
        [
            {
                "candidates": len(scored),
                "world_cell_lt_-0.0002": int((scored["world_cell_delta_vs_h012"] < -0.0002).sum())
                if not scored.empty
                else 0,
                "world_row_lt_-0.00008": int((scored["world_row_delta_vs_h012"] < -0.00008).sum())
                if not scored.empty
                else 0,
                "h024_margin_negative": int((h024_margin < 0.0).sum()),
                "h024_support_ge_0.6": int((h024_support >= 0.60).sum()),
                "world_and_h024_negative": int(
                    ((scored["world_cell_delta_vs_h012"] < -0.0002) & (h024_margin < 0.0)).sum()
                )
                if not scored.empty
                else 0,
            }
        ]
    )
    lines.append(md_table(gate_counts, 1))
    lines.append("\n\n## Candidate ranking\n")
    keep = [
        c
        for c in [
            "candidate_id",
            "family",
            "changed_cells",
            "world_row_delta_vs_h012",
            "world_cell_delta_vs_h012",
            "pre_h012_h024_pred_public_median",
            "pre_h012_h024_margin_vs_h012_median",
            "pre_h012_h024_support_better_than_h012",
            "h025_score",
            "pred_gain_top1200_sum",
            "h037_score",
        ]
        if c in scored.columns
    ]
    lines.append(md_table(scored[keep].head(20), 20) if keep else "_empty_")
    lines.append("\n\n## Row-permutation stress\n")
    if rowperm.empty:
        lines.append("_empty_")
    else:
        p = float(np.mean(rowperm["perm_top1200_sum"].to_numpy(dtype=np.float64) >= rowperm["real_top1200_sum"].iloc[0]))
        lines.append(f"- rowperm p(perm >= real): `{p:.9f}`\n")
        lines.append(md_table(rowperm.head(8), 8))
    lines.append("\n\n## Decision\n")
    lines.append(md_table(decision, 1))
    lines.append(
        "\n\n## Interpretation\n"
        "- Passing would mean H012 is a reusable fixed-point ray, not a single locked file.\n"
        "- Failing means the translator must model more than support-preserving amplitude: exact route, calibration, or private/public split remains missing.\n"
    )
    (OUT / "h037_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    h012 = load_sub(H012)
    sample = h012[KEYS].copy()
    e247 = load_sub(E247, sample)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    e247_prob = e247[TARGETS].to_numpy(dtype=np.float64)
    q_cond, cell_score, row_public = load_h036_world(sample)

    candidates, align_summary = generate_candidates(sample, e247_prob, h012_prob, q_cond, cell_score, row_public)
    candidates.to_csv(OUT / "h037_generated_candidates.csv", index=False)
    align_summary.to_csv(OUT / "h037_alignment_summary.csv", index=False)

    scored, h024_features, h024_models, h025_cells = score_candidates(candidates)
    scored.to_csv(OUT / "h037_candidate_scores.csv", index=False)
    h024_features.to_csv(OUT / "h037_h024_features.csv", index=False)
    h024_models.to_csv(OUT / "h037_h024_model_scores.csv", index=False)
    if not h025_cells.empty:
        h025_cells.to_csv(OUT / "h037_h025_top_cells.csv", index=False)

    rowperm = pd.DataFrame()
    if not scored.empty:
        rowperm = run_rowperm(str(scored.iloc[0]["resolved_path"]))
        rowperm.to_csv(OUT / "h037_selected_h025_rowperm_stress.csv", index=False)

    decision = decide(scored, rowperm)
    decision.to_csv(OUT / "h037_decision.csv", index=False)
    if bool(decision.iloc[0].get("promote", False)):
        selected_path = Path(str(decision.iloc[0]["selected_resolved_path"]))
        root_name = selected_path.name.replace(".csv", "_uploadsafe.csv")
        shutil.copy2(selected_path, ROOT / root_name)
        decision.loc[0, "promoted_root_file"] = root_name
        decision.to_csv(OUT / "h037_decision.csv", index=False)

    write_report(align_summary, scored, decision, rowperm)
    print(f"H037 candidates: {len(scored)}")
    if not scored.empty:
        print(f"H037 selected: {scored.iloc[0]['candidate_id']}")
        print(f"H037 selected world cell delta: {float(scored.iloc[0]['world_cell_delta_vs_h012']):.9f}")
    print(f"H037 decision: {decision.iloc[0]['decision']} - {decision.iloc[0]['reason']}")


if __name__ == "__main__":
    main()
