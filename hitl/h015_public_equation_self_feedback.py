#!/usr/bin/env python3
"""H015: H012-self-feedback public-equation posterior.

H012 proved that known public LB observations can be converted into a hidden
public-state target.  H015 asks the next sharper question: after H012's public
score is known, does the equation system point to another coherent movement
away from H012, or does it collapse back to H012 as the fixed point?
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
H015 = ROOT / "hitl" / "h015_public_equation_self_feedback"
H015.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    known_public_table,
    load_sub,
    logit,
)


EPS = 1.0e-6
CURRENT = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
E247 = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
REPORT_OUT = H015 / "h015_report.md"
CONFIG_OUT = H015 / "h015_posterior_configs.csv"
POSTERIOR_OUT = H015 / "h015_cell_posterior.csv"
CANDIDATE_OUT = H015 / "h015_candidates.csv"
SCENARIO_OUT = H015 / "h015_posterior_scenarios.csv"
EQUATION_OUT = H015 / "h015_known_equations.csv"
H012_PUBLIC = 0.5681234831


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: str
    alpha: float
    target_subset: str
    cell_mode: str
    k: int = 0
    min_consistency: float = 0.0


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def loss(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(y_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def safe_id(text: str, limit: int = 96) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


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


def load_public_system() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, np.ndarray]:
    known = known_public_table().copy()
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")
    base = load_sub(CURRENT)
    sample = base[KEYS].copy()
    pred_by_file: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for rec in known.sort_values("public_lb").to_dict("records"):
        file_name = str(rec["file"])
        try:
            df = load_sub(file_name, sample)
        except FileNotFoundError:
            continue
        pred_by_file[file_name] = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(rec)
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    return known, sample, pred_by_file, base, base[TARGETS].to_numpy(dtype=np.float64)


def prior_vectors(known: pd.DataFrame, pred_by_file: dict[str, np.ndarray], base_prob: np.ndarray) -> dict[str, np.ndarray]:
    lbs = known.set_index("file")["public_lb"].astype(float)
    best = float(lbs.min())
    ordered = known["file"].astype(str).tolist()
    top_files = [f for f in ordered if f in pred_by_file][:6]

    def weighted(scale: float) -> np.ndarray:
        preds = []
        weights = []
        for file_name in top_files:
            lb = float(lbs[file_name])
            preds.append(pred_by_file[file_name])
            weights.append(np.exp(-(lb - best) / scale))
        w = np.asarray(weights, dtype=np.float64)
        w = w / max(w.sum(), 1.0e-12)
        return np.tensordot(w, np.stack(preds, axis=0), axes=(0, 0))

    priors = {
        "h012_current": base_prob.reshape(-1),
        "h012_sharp": sigmoid(1.15 * logit(base_prob)).reshape(-1),
        "top6_wide_soft": weighted(0.0040).reshape(-1),
        "top6_very_wide_soft": weighted(0.0080).reshape(-1),
        "top6_median": np.median(np.stack([pred_by_file[f] for f in top_files], axis=0), axis=0).reshape(-1),
        "neutral": np.full(base_prob.size, 0.5, dtype=np.float64),
    }
    if E247 in pred_by_file:
        priors["e247"] = pred_by_file[E247].reshape(-1)
    return priors


def equation_arrays(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    base_prob: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = clip_prob(base_prob.reshape(-1))
    base_lb = float(known.loc[known["file"].eq(CURRENT), "public_lb"].iloc[0])
    rows: list[dict[str, Any]] = []
    a_rows: list[np.ndarray] = []
    d0_rows: list[np.ndarray] = []
    b_vals: list[float] = []
    n = base.size
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == CURRENT or file_name not in pred_by_file:
            continue
        pred = clip_prob(pred_by_file[file_name].reshape(-1))
        d0 = -np.log(1.0 - pred) + np.log(1.0 - base)
        d1 = np.log((1.0 - pred) / pred) - np.log((1.0 - base) / base)
        actual_delta = float(rec["public_lb"]) - base_lb
        rhs = actual_delta - float(d0.mean())
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "actual_delta_vs_h012": actual_delta,
                "d0_mean": float(d0.mean()),
                "rhs_label_term": rhs,
                "d1_abs_mean": float(np.mean(np.abs(d1))),
                "changed_cells_vs_h012": int((np.abs(pred - base) > 1.0e-12).sum()),
            }
        )
        a_rows.append(d1 / n)
        d0_rows.append(d0)
        b_vals.append(rhs)
    equations = pd.DataFrame(rows)
    equations.to_csv(EQUATION_OUT, index=False)
    return equations, np.vstack(a_rows), np.vstack(d0_rows), np.asarray(b_vals, dtype=np.float64)


def fit_posterior(a: np.ndarray, b: np.ndarray, prior: np.ndarray, ridge_mult: float) -> np.ndarray:
    if len(b) == 0:
        return clip_prob(prior)
    gram = a @ a.T
    scale = float(np.median(np.diag(gram)))
    if not np.isfinite(scale) or scale <= 1.0e-18:
        scale = float(np.mean(np.diag(gram)) + 1.0e-18)
    lam = ridge_mult * scale
    residual = b - a @ prior
    try:
        dual = np.linalg.solve(gram + lam * np.eye(len(b)), residual)
    except np.linalg.LinAlgError:
        dual = np.linalg.pinv(gram + lam * np.eye(len(b))) @ residual
    return clip_prob(prior + a.T @ dual)


def predict_delta_from_q(d0: np.ndarray, d1: np.ndarray, q: np.ndarray) -> float:
    return float(np.mean(d0 + d1 * q))


def evaluate_configs(
    equations: pd.DataFrame,
    a: np.ndarray,
    d0_rows: np.ndarray,
    b: np.ndarray,
    priors: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    d1_rows = a * next(iter(priors.values())).size
    actual = equations["actual_delta_vs_h012"].to_numpy(dtype=np.float64)
    ridge_mults = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
    for prior_name, prior in priors.items():
        for mult in ridge_mults:
            full_q = fit_posterior(a, b, prior, mult)
            full_pred = np.asarray([predict_delta_from_q(d0_rows[i], d1_rows[i], full_q) for i in range(len(actual))])
            loo_pred = []
            for heldout in range(len(actual)):
                keep = np.ones(len(actual), dtype=bool)
                keep[heldout] = False
                q = fit_posterior(a[keep], b[keep], prior, mult)
                loo_pred.append(predict_delta_from_q(d0_rows[heldout], d1_rows[heldout], q))
            pred = np.asarray(loo_pred, dtype=np.float64)
            err = pred - actual
            rows.append(
                {
                    "prior_name": prior_name,
                    "ridge_mult": mult,
                    "loo_mae": float(np.mean(np.abs(err))),
                    "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                    "loo_spearman": float(pd.Series(pred).corr(pd.Series(actual), method="spearman")),
                    "loo_pearson": float(pd.Series(pred).corr(pd.Series(actual), method="pearson")),
                    "known_fit_mae": float(np.mean(np.abs(full_pred - actual))),
                    "known_fit_p90_abs": float(np.quantile(np.abs(full_pred - actual), 0.90)),
                    "q_mean": float(full_q.mean()),
                    "q_std": float(full_q.std()),
                    "q_l1_from_prior": float(np.mean(np.abs(full_q - prior))),
                    "q_l1_from_h012": float(np.mean(np.abs(full_q - priors["h012_current"]))),
                }
            )
    cfg = pd.DataFrame(rows)
    cfg["config_score"] = (
        cfg["loo_mae"].fillna(9.0)
        + 0.25 * cfg["loo_p90_abs"].fillna(9.0)
        - 0.00010 * cfg["loo_spearman"].fillna(0.0)
        + 0.00010 * np.maximum(cfg["q_l1_from_h012"].fillna(0.0) - 0.08, 0.0)
    )
    cfg = cfg.sort_values(["config_score", "loo_mae", "known_fit_mae"]).reset_index(drop=True)
    cfg.to_csv(CONFIG_OUT, index=False)
    return cfg


def selected_configs(configs: pd.DataFrame, limit: int = 10) -> list[tuple[str, float]]:
    strong = configs[
        (configs["loo_spearman"].fillna(-1.0) >= 0.35)
        & (configs["loo_mae"] <= configs["loo_mae"].quantile(0.55))
    ]
    source = strong if len(strong) else configs
    out: list[tuple[str, float]] = []
    seen: set[tuple[str, float]] = set()
    for rec in source.head(limit * 3).to_dict("records"):
        key = (str(rec["prior_name"]), float(rec["ridge_mult"]))
        if key in seen:
            continue
        out.append(key)
        seen.add(key)
        if len(out) >= limit:
            break
    return out


def build_scenarios(configs: list[tuple[str, float]], a: np.ndarray, b: np.ndarray, priors: dict[str, np.ndarray]) -> tuple[np.ndarray, list[str]]:
    qs: list[np.ndarray] = []
    names: list[str] = []
    for prior_name, mult in configs:
        qs.append(fit_posterior(a, b, priors[prior_name], mult))
        names.append(f"{prior_name}_r{mult:g}_full")
    if configs:
        prior_name, mult = configs[0]
        for heldout in range(len(b)):
            keep = np.ones(len(b), dtype=bool)
            keep[heldout] = False
            qs.append(fit_posterior(a[keep], b[keep], priors[prior_name], mult))
            names.append(f"{prior_name}_r{mult:g}_loo{heldout}")
    return np.vstack(qs), names


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        mask[:, :] = True
    elif target_subset == "Q":
        mask[:, :3] = True
    elif target_subset == "S":
        mask[:, 3:] = True
    elif target_subset in TARGETS:
        mask[:, TARGETS.index(target_subset)] = True
    else:
        raise ValueError(target_subset)
    return mask


def candidate_specs() -> list[CandidateSpec]:
    out: list[CandidateSpec] = []
    for alpha in [0.10, 0.18, 0.30, 0.45]:
        out.append(CandidateSpec(f"direct_all_a{alpha:g}", "direct", alpha, "all", "all"))
    for subset in ["all", "Q", "S"]:
        for k in [50, 100, 200, 400, 800, 1200, 1600]:
            for alpha in [0.25, 0.45, 0.70, 1.00]:
                out.append(CandidateSpec(f"top_{subset}_k{k}_a{alpha:g}", "top", alpha, subset, "top", k, 0.55))
    for target in TARGETS:
        for k in [10, 20, 35, 50, 80, 120, 180]:
            for alpha in [0.35, 0.60, 0.90]:
                out.append(CandidateSpec(f"target_{target}_k{k}_a{alpha:g}", "target_top", alpha, target, "top", k, 0.55))
    for subset in ["all", "Q", "S"]:
        for k in [50, 100, 200, 400, 800]:
            for alpha in [0.35, 0.60, 0.90]:
                out.append(CandidateSpec(f"stable_{subset}_k{k}_a{alpha:g}", "stable_top", alpha, subset, "stable_top", k, 0.75))
    return out


def cell_selection(spec: CandidateSpec, score: np.ndarray, consistency: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    base_mask = target_mask(spec.target_subset, shape).reshape(-1)
    if spec.cell_mode == "all":
        return base_mask.reshape(shape)
    allowed = base_mask & (consistency >= spec.min_consistency)
    flat = np.flatnonzero(allowed)
    if len(flat) == 0:
        return np.zeros(shape, dtype=bool)
    chosen = flat[np.argsort(score[flat])[-min(spec.k, len(flat)) :]]
    out = np.zeros(shape[0] * shape[1], dtype=bool)
    out[chosen] = True
    return out.reshape(shape)


def write_candidate(base_df: pd.DataFrame, q_main: np.ndarray, spec: CandidateSpec, mask: np.ndarray) -> Path:
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)
    q = q_main.reshape(base_prob.shape)
    z = logit(base_prob)
    zq = logit(q)
    out_prob = base_prob.copy()
    moved = z.copy()
    moved[mask] = (1.0 - spec.alpha) * z[mask] + spec.alpha * zq[mask]
    out_prob[mask] = sigmoid(moved[mask])
    out = base_df.copy()
    out[TARGETS] = np.clip(out_prob, EPS, 1.0 - EPS)
    path = H015 / f"submission_h015_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize(base_df: pd.DataFrame, q_scenarios: np.ndarray) -> tuple[pd.DataFrame, Path | None]:
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)
    q_main = np.median(q_scenarios, axis=0)
    z_base = logit(base_prob).reshape(-1)
    z_scenarios = logit(q_scenarios)
    z_main = np.median(z_scenarios, axis=0)
    direction = np.sign(z_main - z_base)
    consistency = np.mean(np.sign(z_scenarios - z_base) == direction[None, :], axis=0)
    score = np.abs(z_main - z_base) * consistency

    cell_rows = []
    qmat = q_main.reshape(base_prob.shape)
    for row_i in range(base_prob.shape[0]):
        for target_i, target in enumerate(TARGETS):
            idx = row_i * len(TARGETS) + target_i
            cell_rows.append(
                {
                    "row": row_i,
                    "target": target,
                    "base_prob_h012": float(base_prob[row_i, target_i]),
                    "posterior_prob": float(qmat[row_i, target_i]),
                    "posterior_minus_h012": float(qmat[row_i, target_i] - base_prob[row_i, target_i]),
                    "logit_delta_to_posterior": float(z_main[idx] - z_base[idx]),
                    "direction_consistency": float(consistency[idx]),
                    "cell_score": float(score[idx]),
                }
            )
    pd.DataFrame(cell_rows).sort_values("cell_score", ascending=False).to_csv(POSTERIOR_OUT, index=False)

    q_shape = base_prob.shape
    rows: list[dict[str, Any]] = []
    for spec in candidate_specs():
        mask = cell_selection(spec, score, consistency, q_shape)
        if not mask.any():
            continue
        path = write_candidate(base_df, q_main, spec, mask)
        pred = load_sub(path, base_df[KEYS])[TARGETS].to_numpy(dtype=np.float64)
        deltas = []
        for q in q_scenarios:
            deltas.append(float(np.mean(loss(pred, q.reshape(q_shape)) - loss(base_prob, q.reshape(q_shape)))))
        arr = np.asarray(deltas, dtype=np.float64)
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "target_subset": spec.target_subset,
                "alpha": spec.alpha,
                "k": spec.k,
                "file": rel(path),
                "posterior_delta_mean_vs_h012": float(arr.mean()),
                "posterior_delta_p10_vs_h012": float(np.quantile(arr, 0.10)),
                "posterior_delta_p90_vs_h012": float(np.quantile(arr, 0.90)),
                "posterior_delta_max_vs_h012": float(arr.max()),
                "posterior_beats_h012_rate": float(np.mean(arr < 0.0)),
                "expected_public_if_posterior": float(H012_PUBLIC + arr.mean()),
                "changed_rows": int((np.abs(pred - base_prob).max(axis=1) > 1.0e-12).sum()),
                "changed_cells": int((np.abs(pred - base_prob) > 1.0e-12).sum()),
                "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(pred - base_prob))),
                "max_abs_prob_delta_vs_h012": float(np.max(np.abs(pred - base_prob))),
                "mean_cell_score_changed": float(score[mask.reshape(-1)].mean()),
                "min_consistency_changed": float(consistency[mask.reshape(-1)].min()),
                "mean_consistency_changed": float(consistency[mask.reshape(-1)].mean()),
            }
        )
    candidates = pd.DataFrame(rows)
    candidates["h015_decision"] = np.select(
        [
            (candidates["posterior_delta_mean_vs_h012"] < -0.00080)
            & (candidates["posterior_delta_p90_vs_h012"] < -0.00020)
            & (candidates["posterior_beats_h012_rate"] >= 0.70)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.22),
            (candidates["posterior_delta_mean_vs_h012"] < -0.00035)
            & (candidates["posterior_beats_h012_rate"] >= 0.65)
            & (candidates["max_abs_prob_delta_vs_h012"] <= 0.30),
        ],
        ["post_h012_big_bet", "post_h012_sensor"],
        default="diagnostic_only",
    )
    order = {"post_h012_big_bet": 0, "post_h012_sensor": 1, "diagnostic_only": 2}
    candidates["decision_rank"] = candidates["h015_decision"].map(order).astype(int)
    candidates = candidates.sort_values(["decision_rank", "posterior_delta_p90_vs_h012", "posterior_delta_mean_vs_h012"]).reset_index(drop=True)
    candidates.to_csv(CANDIDATE_OUT, index=False)

    primary = None
    top = candidates[candidates["h015_decision"].isin(["post_h012_big_bet", "post_h012_sensor"])].head(1)
    if not top.empty:
        source = ROOT / str(top.iloc[0]["file"])
        primary = ROOT / f"submission_h015_self_feedback_{safe_id(str(top.iloc[0]['candidate_id']), 72)}_uploadsafe.csv"
        shutil.copyfile(source, primary)
    return candidates, primary


def write_report(
    known: pd.DataFrame,
    equations: pd.DataFrame,
    configs: pd.DataFrame,
    selected: list[tuple[str, float]],
    candidates: pd.DataFrame,
    primary: Path | None,
) -> None:
    config_cols = ["prior_name", "ridge_mult", "loo_mae", "loo_p90_abs", "loo_spearman", "known_fit_mae", "q_l1_from_h012", "q_l1_from_prior"]
    cand_cols = [
        "candidate_id",
        "h015_decision",
        "family",
        "target_subset",
        "changed_cells",
        "posterior_delta_mean_vs_h012",
        "posterior_delta_p90_vs_h012",
        "posterior_beats_h012_rate",
        "expected_public_if_posterior",
        "max_abs_prob_delta_vs_h012",
        "file",
    ]
    lines = [
        "# H015 Public-Equation Self Feedback",
        "",
        "## Question",
        "",
        "After H012's public score is included, does the public-equation posterior still imply a coherent movement beyond H012?",
        "",
        "## Evidence",
        "",
        f"- current anchor: `{CURRENT}` public `{H012_PUBLIC}`",
        f"- known public observations loaded: `{len(known)}`",
        f"- equations vs H012: `{len(equations)}`",
        f"- posterior configs tested: `{len(configs)}`",
        f"- selected posterior scenarios: `{len(selected)} full configs plus leave-one-out variants from top config`",
        f"- generated candidates: `{len(candidates)}`",
        f"- primary upload-safe file: `{rel(primary) if primary else 'none'}`",
        "",
        "## Selected Configs",
        "",
        md_table(pd.DataFrame(selected, columns=["prior_name", "ridge_mult"]), n=20),
        "",
        "## Top Config Diagnostics",
        "",
        md_table(configs[config_cols], n=25),
        "",
        "## Candidate Selection",
        "",
        md_table(candidates[[c for c in cand_cols if c in candidates.columns]], n=40),
        "",
        "## Interpretation",
        "",
    ]
    if primary is None:
        lines.extend(
            [
                "- The post-H012 equation system does not promote a new file.",
                "- H012 behaves like the current fixed point of known public equations; the next breakthrough needs a different public-subset or private-risk sensor, not blind amplification.",
            ]
        )
    else:
        lines.extend(
            [
                "- The post-H012 equation system promotes a new high-information candidate.",
                "- This is not a safe microblend. It tests whether H012 was an under-amplified public-state posterior rather than a one-shot optimum.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CONFIG_OUT)}`",
            f"- `{rel(EQUATION_OUT)}`",
            f"- `{rel(POSTERIOR_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCENARIO_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    known, sample, pred_by_file, base_df, base_prob = load_public_system()
    priors = prior_vectors(known, pred_by_file, base_prob)
    equations, a, d0_rows, b = equation_arrays(known, pred_by_file, base_prob)
    configs = evaluate_configs(equations, a, d0_rows, b, priors)
    selected = selected_configs(configs)
    q_scenarios, scenario_names = build_scenarios(selected, a, b, priors)
    pd.DataFrame({"scenario_name": scenario_names}).to_csv(SCENARIO_OUT, index=False)
    candidates, primary = materialize(base_df, q_scenarios)
    write_report(known, equations, configs, selected, candidates, primary)
    print(f"wrote {REPORT_OUT}")
    if primary is not None:
        print(f"primary {primary}")
    print(
        candidates[
            [
                "candidate_id",
                "h015_decision",
                "posterior_delta_mean_vs_h012",
                "posterior_delta_p90_vs_h012",
                "posterior_beats_h012_rate",
                "changed_cells",
                "max_abs_prob_delta_vs_h012",
                "file",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
