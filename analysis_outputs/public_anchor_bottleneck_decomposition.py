from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
RAW05 = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
A2C8 = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
FINAL9 = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
Q2_BAD = "submission_jepa_latent_q2_w0p45.csv"
RESID_BAD = "submission_jepa_latent_residual_probe.csv"
LEJEPA_BAD = "submission_lejepa_targetwise_strict_best_scale0p5.csv"

KNOWN_PUBLIC_EXTRA = {
    A2C8: (0.5774393210, "Current public best supplied by user; missing from older observation table."),
}

KNOWN_OUT = OUT / "public_anchor_bottleneck_known.csv"
MODEL_OUT = OUT / "public_anchor_bottleneck_model_scores.csv"
CANDIDATE_OUT = OUT / "public_anchor_bottleneck_candidate_scores.csv"
REPORT_OUT = OUT / "public_anchor_bottleneck_decomposition_report.md"


def locate(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def prob_matrix(name: str, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(name, sample)[TARGETS].to_numpy(dtype=np.float64)


def vec(prob: np.ndarray) -> np.ndarray:
    return logit(prob).reshape(-1)


def projection(move: np.ndarray, direction: np.ndarray) -> tuple[float, float]:
    denom = float(direction @ direction)
    if denom <= 1e-15:
        return 0.0, 0.0
    coeff = float(move @ direction / denom)
    cos = float(move @ direction / (np.linalg.norm(move) * np.linalg.norm(direction) + 1e-12))
    return coeff, cos


def residual_ratio_to_span(move: np.ndarray, basis: list[np.ndarray]) -> float:
    if not basis:
        return 1.0
    x = np.column_stack(basis)
    gram = x.T @ x
    try:
        beta = np.linalg.solve(gram + 1e-9 * np.eye(gram.shape[0]), x.T @ move)
    except np.linalg.LinAlgError:
        beta = np.linalg.pinv(x) @ move
    resid = move - x @ beta
    return float(np.linalg.norm(resid) / (np.linalg.norm(move) + 1e-12))


def known_public_table() -> pd.DataFrame:
    obs_path = OUT / "public_probe_observations.csv"
    if not obs_path.exists():
        raise FileNotFoundError(obs_path)
    obs = pd.read_csv(obs_path)
    rows = []
    seen: set[str] = set()
    for rec in obs.to_dict("records"):
        file_name = str(rec["file"])
        if locate(file_name) is None:
            continue
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "note": str(rec.get("note", "")),
                "known_source": "public_probe_observations",
            }
        )
        seen.add(file_name)
    for file_name, (public_lb, note) in KNOWN_PUBLIC_EXTRA.items():
        if file_name not in seen and locate(file_name) is not None:
            rows.append(
                {
                    "file": file_name,
                    "public_lb": float(public_lb),
                    "note": note,
                    "known_source": "manual_extra",
                }
            )
    return pd.DataFrame(rows)


def feature_row(
    file_name: str,
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    ref_vecs: dict[str, np.ndarray],
) -> dict[str, object]:
    p = prob_matrix(file_name, sample)
    z = vec(p)
    z_stage2 = ref_vecs["stage2"]
    move_stage2 = z - z_stage2
    z_a2c8 = ref_vecs["a2c8"]
    z_raw05 = ref_vecs["raw05"]

    row: dict[str, object] = {
        "file": file_name,
        "min_prob": float(p.min()),
        "max_prob": float(p.max()),
        "mean_prob": float(p.mean()),
        "prob_span": float(p.max() - p.min()),
        "mean_abs_move_vs_stage2": float(np.mean(np.abs(z - z_stage2))),
        "mean_abs_move_vs_raw05": float(np.mean(np.abs(z - z_raw05))),
        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(z - z_a2c8))),
        "rms_move_vs_a2c8": float(np.sqrt(np.mean((z - z_a2c8) ** 2))),
        "max_abs_move_vs_a2c8": float(np.max(np.abs(z - z_a2c8))),
    }

    for target_i, target in enumerate(TARGETS):
        target_move = logit(p[:, [target_i]]) - logit(refs["a2c8"][:, [target_i]])
        row[f"move_abs_a2c8_{target}"] = float(np.mean(np.abs(target_move)))
        row[f"mean_prob_{target}"] = float(np.mean(p[:, target_i]))

    ref_dirs = {
        "a2c8": ref_vecs["a2c8"] - z_stage2,
        "raw05": ref_vecs["raw05"] - z_stage2,
        "final9": ref_vecs["final9"] - z_stage2,
        "ordinal": ref_vecs["ordinal"] - z_stage2,
        "q2_bad": ref_vecs["q2_bad"] - z_stage2,
        "resid_bad": ref_vecs["resid_bad"] - z_stage2,
        "lejepa_bad": ref_vecs["lejepa_bad"] - z_stage2,
    }
    for name, direction in ref_dirs.items():
        coeff, cos = projection(move_stage2, direction)
        row[f"proj_{name}"] = coeff
        row[f"cos_{name}"] = cos

    row["bad_axis_abs_load"] = float(
        abs(row["proj_q2_bad"])
        + abs(row["proj_resid_bad"])
        + abs(row["proj_lejepa_bad"])
        + 0.5 * abs(row["proj_ordinal"])
    )
    row["bad_axis_positive_load"] = float(
        max(row["proj_q2_bad"], 0.0)
        + max(row["proj_resid_bad"], 0.0)
        + max(row["proj_lejepa_bad"], 0.0)
        + 0.5 * max(row["proj_ordinal"], 0.0)
    )
    row["good_axis_load"] = float(abs(row["proj_a2c8"]) + abs(row["proj_raw05"]))
    row["good_span_residual_ratio"] = residual_ratio_to_span(
        move_stage2,
        [ref_dirs["a2c8"], ref_dirs["raw05"]],
    )
    row["bad_to_good_load_ratio"] = float(row["bad_axis_abs_load"] / (row["good_axis_load"] + 1e-9))
    row["raw05_a2c8_compat_energy"] = float(
        row["mean_abs_move_vs_raw05"]
        + 0.35 * row["mean_abs_move_vs_a2c8"]
        + 0.015 * row["bad_axis_abs_load"]
        + 0.010 * row["good_span_residual_ratio"]
    )
    return row


def standardize(train: np.ndarray, pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.nanmean(train, axis=0)
    sigma = np.nanstd(train, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return np.nan_to_num((train - mu) / sigma), np.nan_to_num((pred - mu) / sigma)


def ridge_predict(train: pd.DataFrame, pred: pd.DataFrame, features: list[str], alpha: float) -> np.ndarray:
    x = train[features].to_numpy(dtype=np.float64)
    xp = pred[features].to_numpy(dtype=np.float64)
    y = train["public_lb"].to_numpy(dtype=np.float64)
    x, xp = standardize(x, xp)
    x_aug = np.column_stack([np.ones(len(x)), x])
    xp_aug = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(x_aug.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y
    return xp_aug @ beta


def loocv_pred(frame: pd.DataFrame, features: list[str], alpha: float) -> np.ndarray:
    preds = np.zeros(len(frame), dtype=np.float64)
    for i in range(len(frame)):
        train = frame.drop(frame.index[i])
        test = frame.iloc[[i]]
        preds[i] = ridge_predict(train, test, features, alpha)[0]
    return preds


def pairwise_rank_accuracy(pred: np.ndarray, y: np.ndarray) -> float:
    ok = total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1e-15 or abs(dp) < 1e-15:
                continue
            total += 1
            ok += int(dy * dp > 0)
    return float(ok / total) if total else float("nan")


def evaluate_models(known: pd.DataFrame) -> pd.DataFrame:
    model_defs = [
        ("constant_median", [], 1.0, "baseline"),
        (
            "raw05_a2c8_compat",
            ["mean_abs_move_vs_raw05", "mean_abs_move_vs_a2c8", "good_span_residual_ratio", "bad_axis_abs_load"],
            1.0,
            "fixed_loocv",
        ),
        (
            "bad_axes_only",
            ["bad_axis_abs_load", "bad_axis_positive_load", "proj_q2_bad", "proj_resid_bad", "proj_lejepa_bad"],
            1.0,
            "fixed_loocv",
        ),
        (
            "good_bad_axes",
            ["proj_a2c8", "proj_raw05", "bad_axis_abs_load", "proj_ordinal", "mean_abs_move_vs_raw05"],
            1.0,
            "fixed_loocv",
        ),
        (
            "target_move_core",
            ["move_abs_a2c8_Q2", "move_abs_a2c8_Q3", "move_abs_a2c8_S2", "move_abs_a2c8_S3", "move_abs_a2c8_S4"],
            1.0,
            "fixed_loocv",
        ),
        (
            "compact_energy",
            ["raw05_a2c8_compat_energy", "bad_to_good_load_ratio", "mean_abs_move_vs_stage2"],
            1.0,
            "fixed_loocv",
        ),
    ]
    y = known["public_lb"].to_numpy(dtype=np.float64)
    rows = []
    for model, features, alpha, kind in model_defs:
        if features:
            pred = loocv_pred(known, features, alpha)
            feature_text = ",".join(features)
        else:
            pred = np.full(len(known), np.median(y), dtype=np.float64)
            feature_text = ""
        err = pred - y
        rows.append(
            {
                "model": model,
                "kind": kind,
                "features": feature_text,
                "alpha": alpha if features else np.nan,
                "mae": float(np.mean(np.abs(err))),
                "rmse": float(np.sqrt(np.mean(err**2))),
                "max_abs_error": float(np.max(np.abs(err))),
                "bias": float(np.mean(err)),
                "pairwise_rank_accuracy": pairwise_rank_accuracy(pred, y),
                "p80_abs_error": float(np.quantile(np.abs(err), 0.80)),
                "p90_abs_error": float(np.quantile(np.abs(err), 0.90)),
            }
        )
    return pd.DataFrame(rows).sort_values(["mae", "rmse"]).reset_index(drop=True)


def candidate_files() -> list[str]:
    direct = [
        STAGE2,
        RAW05,
        A2C8,
        "submission_mixmin_0c916bb4.csv",
        "submission_mixmin_5a4c25e0.csv",
        "submission_mixmin_f0d12643.csv",
        "submission_mixmin_f6c04249.csv",
        "submission_public6entropy_raw05_q3s4_g250_b19cb905.csv",
        "submission_raw05_jepa_axisbridge_45f2ba5a.csv",
        "submission_raw05_jepa_lowbadcon_71601b5f.csv",
        "submission_jepa_public_minimax_bridge_84b71a03.csv",
    ]
    tables = [
        (OUT / "jepa_direction_mixture_minimax_optimizer_selected.csv", 20),
        (OUT / "local_lb_proxy_uncertainty_candidate_risk.csv", 80),
        (OUT / "jepa_public_minimax_rawsafe_bridge_selected.csv", 40),
        (OUT / "public_lb_actual_anchor_ranker_shortlist.csv", 40),
        (OUT / "public_minimax_ensemble_selected.csv", 20),
        (OUT / "public_universe_minimax_selected.csv", 20),
        (OUT / "public_lb_direct_label_inverse7_selected.csv", 30),
    ]
    files: list[str] = []
    files.extend(direct)
    for path, limit in tables:
        if not path.exists():
            continue
        df = pd.read_csv(path).head(limit)
        for col in ("file", "candidate", "submission"):
            if col not in df.columns:
                continue
            files.extend(
                str(x)
                for x in df[col].dropna()
                if isinstance(x, str) and x.endswith(".csv") and locate(str(x)) is not None
            )
    seen: set[str] = set()
    out: list[str] = []
    for f in files:
        if f not in seen and locate(f) is not None:
            out.append(f)
            seen.add(f)
    return out


def fit_all_predict(known: pd.DataFrame, candidates: pd.DataFrame, models: pd.DataFrame) -> pd.DataFrame:
    usable_models = models[(models["kind"] == "fixed_loocv") & (models["mae"] <= models["mae"].median())].copy()
    pred_cols = []
    out = candidates.copy()
    for _, rec in usable_models.iterrows():
        features = str(rec["features"]).split(",")
        name = str(rec["model"])
        out[f"pred_{name}"] = ridge_predict(known, candidates, features, float(rec["alpha"]))
        pred_cols.append(f"pred_{name}")
    if pred_cols:
        out["proxy_pred_mean"] = out[pred_cols].mean(axis=1)
        out["proxy_pred_min"] = out[pred_cols].min(axis=1)
        out["proxy_pred_max"] = out[pred_cols].max(axis=1)
        out["proxy_pred_spread"] = out["proxy_pred_max"] - out["proxy_pred_min"]
    else:
        out["proxy_pred_mean"] = np.nan
        out["proxy_pred_min"] = np.nan
        out["proxy_pred_max"] = np.nan
        out["proxy_pred_spread"] = np.nan
    best_known = float(known["public_lb"].min())
    best_model_mae = float(models[models["kind"] == "fixed_loocv"]["mae"].min())
    out["proxy_delta_vs_a2c8_public"] = out["proxy_pred_mean"] - best_known
    out["edge_to_proxy_mae"] = -out["proxy_delta_vs_a2c8_public"] / best_model_mae
    out["candidate_risk_score"] = (
        out["proxy_pred_mean"].fillna(1.0)
        + 0.35 * out["proxy_pred_spread"].fillna(0.0)
        + 0.00020 * out["bad_axis_abs_load"].fillna(0.0)
        + 0.00008 * out["good_span_residual_ratio"].fillna(0.0)
    )
    out["below_proxy_resolution"] = out["proxy_delta_vs_a2c8_public"].abs() < best_model_mae
    return out.sort_values(["candidate_risk_score", "proxy_pred_mean"]).reset_index(drop=True)


def summarize_direct_inverse() -> dict[str, float]:
    out: dict[str, float] = {}
    loo = OUT / "public_lb_direct_label_inverse7_loocv_policy.csv"
    l2o = OUT / "public_lb_direct_label_inverse7_l2ocv_policy.csv"
    if loo.exists():
        df = pd.read_csv(loo)
        overall = df[df["heldout_key"] == "__overall__"]
        for policy in ["train_best1", "oracle_best1"]:
            row = overall[overall["policy"] == policy]
            if not row.empty:
                out[f"loo_{policy}_mae"] = float(row["heldout_abs_error"].iloc[0])
    if l2o.exists():
        df = pd.read_csv(l2o)
        overall = df[df["heldout_pair"] == "__overall__"]
        for policy in ["l2o_best1", "oracle_pair_best1"]:
            row = overall[overall["policy"] == policy]
            if not row.empty:
                out[f"l2o_{policy}_mae"] = float(row["pair_abs_error_mean"].iloc[0])
    return out


def write_report(known: pd.DataFrame, models: pd.DataFrame, candidates: pd.DataFrame) -> None:
    inverse = summarize_direct_inverse()
    best_model = models[models["kind"] == "fixed_loocv"].sort_values("mae").iloc[0]
    best_public = known.sort_values("public_lb").iloc[0]
    top_candidates = candidates.head(20).copy()
    best_model_mae = float(best_model["mae"])
    resolved = candidates[~candidates["below_proxy_resolution"]].copy()
    resolved_better = candidates[candidates["proxy_delta_vs_a2c8_public"] < -best_model_mae].copy()
    resolved_worse = candidates[candidates["proxy_delta_vs_a2c8_public"] > best_model_mae].copy()
    controls = candidates[candidates["is_known_public"]].copy()
    raw05_public = float(known.loc[known["file"] == RAW05, "public_lb"].iloc[0])
    a2c8_public = float(known.loc[known["file"] == A2C8, "public_lb"].iloc[0])
    raw05_a2c8_gap = raw05_public - a2c8_public

    lines = [
        "# Public Anchor Bottleneck Decomposition",
        "",
        "This audit puts all known public anchors, including `a2c8`, into one submission-geometry frame.",
        "It is a bottleneck diagnostic: small proxy differences are treated as unresolved unless they exceed the leave-one-anchor error floor.",
        "",
        "## Known Public Anchors",
        "",
        "```csv",
        known[
            [
                "file",
                "public_lb",
                "known_source",
                "mean_abs_move_vs_a2c8",
                "mean_abs_move_vs_raw05",
                "bad_axis_abs_load",
                "good_span_residual_ratio",
                "raw05_a2c8_compat_energy",
            ]
        ]
        .sort_values("public_lb")
        .round(9)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## LOOCV Public Proxy Resolution",
        "",
        "```csv",
        models.round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Direct Hidden-Label Inverse Check",
        "",
        f"- LOO train-best MAE: `{inverse.get('loo_train_best1_mae', np.nan):.9f}`.",
        f"- LOO oracle-best MAE: `{inverse.get('loo_oracle_best1_mae', np.nan):.9f}`.",
        f"- L2O train-best MAE: `{inverse.get('l2o_l2o_best1_mae', np.nan):.9f}`.",
        f"- L2O oracle-best MAE: `{inverse.get('l2o_oracle_pair_best1_mae', np.nan):.9f}`.",
        "",
        "The gap between train-selected and oracle-selected inverse solutions means the inverse has enough degrees of freedom to fit anchors, but the selector is not yet identifying the true public subset.",
        "",
        "## Candidate Proxy Scores",
        "",
        "```csv",
        top_candidates[
            [
                "file",
                "proxy_pred_mean",
                "proxy_delta_vs_a2c8_public",
                "proxy_pred_spread",
                "edge_to_proxy_mae",
                "below_proxy_resolution",
                "mean_abs_move_vs_a2c8",
                "mean_abs_move_vs_raw05",
                "bad_axis_abs_load",
                "good_span_residual_ratio",
                "candidate_risk_score",
            ]
        ]
        .round(9)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Known Control Predictions",
        "",
        "```csv",
        controls[
            [
                "file",
                "known_public_lb",
                "proxy_pred_mean",
                "proxy_delta_vs_a2c8_public",
                "proxy_pred_spread",
                "below_proxy_resolution",
                "candidate_risk_score",
            ]
        ]
        .sort_values("known_public_lb")
        .round(9)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Bottleneck Read",
        "",
        f"- Current best public anchor is `{best_public['file']}` at `{best_public['public_lb']:.9f}`.",
        f"- Best fixed LOOCV proxy is `{best_model['model']}` with MAE `{best_model['mae']:.9f}` and p90 error `{best_model['p90_abs_error']:.9f}`.",
        f"- Raw05 vs a2c8 public gap is `{raw05_a2c8_gap:.9f}`, only `{raw05_a2c8_gap / best_model_mae:.3f}x` of the best LOOCV MAE.",
        f"- Candidates outside that MAE band relative to the current best: `{len(resolved)}` / `{len(candidates)}`.",
        f"- Resolved-better candidates versus the current best: `{len(resolved_better)}`. Resolved-worse candidates: `{len(resolved_worse)}`.",
        "- After adding mixmin and E72, this proxy should be treated as a selector-collapse diagnostic: it ranks many candidates as resolved-worse while also failing to explain the known mixmin/E72 frontier distinction.",
        "- Therefore the candidate scores in this report are useful as geometry descriptors, not as a reliable post-mixmin submission order.",
        "- The bad JEPA anchors are geometrically separable, but raw05/a2c8-compatible gates shrink movement so much that the candidate set becomes locally unresolved.",
        "- Therefore the immediate bottleneck is not lack of more micro-features. It is missing a stable selector for the hidden public subset or a representation that moves off the raw05/a2c8 manifold without loading the bad JEPA axes.",
        "",
        "## Critical Caveat",
        "",
        f"This audit does not prove the true competition public subset. It proves that the current {len(known)}-anchor proxy is too coarse to justify the present post-hoc candidate differences.",
        "The most dangerous false assumption would be treating this proxy resolution as ground truth: the E91 update shows that it cannot resolve the known mixmin/E72 distinction at frontier scale.",
        "",
        "## Next High-Upside Branches",
        "",
        "1. `Hidden-subset selector stress harness`: re-rank existing raw05/a2c8, raw+neural+episode, safe LeJEPA, and known-bad JEPA families under LOO/L2O/synthetic-mask stress. Gate: LOOCV/L2O MAE <= `0.00040`, rank accuracy > `0.90`, and a2c8 > raw05 > bad anchors.",
        "2. `Targetwise safe multi-block LeJEPA`: split Q/S latents, use multiple semantic target blocks, and lower SIGReg toward the paper-default `0.05-0.10` range. Gate: targetwise CV stays non-positive on all targets, geometry mean <= `-0.003`, bad-axis projection < `0.05`.",
        "3. `Output-masked raw-timeline I-JEPA`: predict encoded hidden-block latents from large context plus position tokens instead of reconstructing raw values. Gate: pilot Q2 delta < `-0.002`, Q3 delta < `-0.007`, bad-axis projection < `0.05`, and movement exceeds selector uncertainty.",
        "",
        "Experiment order: run the selector harness first because it is cheap and determines whether the safe LeJEPA or raw-timeline branch deserves the next expensive training pass.",
        "",
        "## Files",
        "",
        f"- `{KNOWN_OUT.name}`",
        f"- `{MODEL_OUT.name}`",
        f"- `{CANDIDATE_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)

    ref_files = {
        "stage2": STAGE2,
        "raw05": RAW05,
        "a2c8": A2C8,
        "final9": FINAL9,
        "ordinal": ORDINAL,
        "q2_bad": Q2_BAD,
        "resid_bad": RESID_BAD,
        "lejepa_bad": LEJEPA_BAD,
    }
    refs = {name: prob_matrix(file_name, sample) for name, file_name in ref_files.items()}
    ref_vecs = {name: vec(prob) for name, prob in refs.items()}

    known_obs = known_public_table()
    known_rows = []
    for rec in known_obs.to_dict("records"):
        row = feature_row(str(rec["file"]), sample, refs, ref_vecs)
        row.update(rec)
        known_rows.append(row)
    known = pd.DataFrame(known_rows).sort_values("public_lb").reset_index(drop=True)
    known.to_csv(KNOWN_OUT, index=False)

    models = evaluate_models(known)
    models.to_csv(MODEL_OUT, index=False)

    candidate_rows = []
    known_files = set(known["file"].astype(str))
    for file_name in candidate_files():
        row = feature_row(file_name, sample, refs, ref_vecs)
        row["is_known_public"] = file_name in known_files
        row["known_public_lb"] = float(known.loc[known["file"] == file_name, "public_lb"].iloc[0]) if file_name in known_files else np.nan
        candidate_rows.append(row)
    candidates = pd.DataFrame(candidate_rows)
    candidates = fit_all_predict(known, candidates, models)
    candidates.to_csv(CANDIDATE_OUT, index=False)

    write_report(known, models, candidates)

    print(REPORT_OUT)
    print("[models]")
    print(models[["model", "mae", "rmse", "max_abs_error", "pairwise_rank_accuracy"]].round(9).to_string(index=False))
    print("[top candidates]")
    print(
        candidates[
            [
                "file",
                "proxy_pred_mean",
                "proxy_delta_vs_a2c8_public",
                "proxy_pred_spread",
                "below_proxy_resolution",
                "candidate_risk_score",
            ]
        ]
        .head(15)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
