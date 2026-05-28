from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sample_block_ids  # noqa: E402


CONTEXT_TARGETS = ["Q1", "Q2", "S1", "S2", "S3"]
TARGET_BLOCK = ["Q3", "S4"]
CONTEXT_IDX = np.asarray([TARGETS.index(t) for t in CONTEXT_TARGETS], dtype=int)
TARGET_IDX = np.asarray([TARGETS.index(t) for t in TARGET_BLOCK], dtype=int)

RANKER = OUT / "public_lb_actual_anchor_ranker_scores.csv"
LOCAL_CANDIDATES = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
PRIORITY = OUT / "final_jepa_candidate_priority_20260527.csv"

OUT_MODEL_CV = OUT / "jepa_context_target_compatibility_model_cv.csv"
OUT_SCORES = OUT / "jepa_context_target_compatibility_scores.csv"
OUT_KNOWN = OUT / "jepa_context_target_compatibility_known_validation.csv"
OUT_LOOCV = OUT / "jepa_context_target_compatibility_lb_loocv.csv"
OUT_REPORT = OUT / "jepa_context_target_compatibility_report.md"


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(file_name)


def read_submission(file_name: str, sample_key: pd.DataFrame) -> np.ndarray:
    frame = pd.read_csv(locate(file_name), parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(
        drop=True
    )
    if not frame[KEY].reset_index(drop=True).equals(sample_key.reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def poly_context_features(context: np.ndarray) -> np.ndarray:
    context = np.asarray(context, dtype=np.float64)
    parts = [context]
    pairs = []
    for i in range(context.shape[1]):
        for j in range(i + 1, context.shape[1]):
            pairs.append(context[:, i] * context[:, j])
    parts.append(np.column_stack(pairs))
    q_count = context[:, 0] + context[:, 1]
    s_count = context[:, 2] + context[:, 3] + context[:, 4]
    all_count = q_count + s_count
    parts.append(np.column_stack([q_count, s_count, all_count, q_count * s_count]))
    return np.column_stack(parts)


def fit_ridge(train_x: np.ndarray, train_y: np.ndarray, pred_x: np.ndarray, alpha: float = 2.0) -> np.ndarray:
    mu = train_x.mean(axis=0)
    sd = train_x.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    x = (train_x - mu) / sd
    xp = (pred_x - mu) / sd
    x_aug = np.column_stack([np.ones(len(x)), x])
    xp_aug = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(x_aug.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ train_y
    return np.clip(xp_aug @ beta, 1e-4, 1.0 - 1e-4)


def soft_ce(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    y = clip(y)
    p = clip(p)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def soft_kl(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    q = clip(q)
    p = clip(p)
    return q * (np.log(q) - np.log(p)) + (1.0 - q) * (np.log(1.0 - q) - np.log(1.0 - p))


def row_logloss(y: np.ndarray, p: np.ndarray) -> float:
    return float(soft_ce(y, p).mean())


def model_cv(train: pd.DataFrame) -> pd.DataFrame:
    rows = []
    y_all = train[TARGET_BLOCK].to_numpy(dtype=np.float64)
    x_all = poly_context_features(train[CONTEXT_TARGETS].to_numpy(dtype=np.float64))
    global_rate = np.tile(y_all.mean(axis=0, keepdims=True), (len(y_all), 1))
    rows.append(
        {
            "fold_type": "all_rows_baseline",
            "fold": "global_rate",
            "n_valid": len(y_all),
            "model_loss": row_logloss(y_all, global_rate),
            "baseline_loss": row_logloss(y_all, global_rate),
            "delta_vs_baseline": 0.0,
            "Q3_loss": float(soft_ce(y_all[:, [0]], global_rate[:, [0]]).mean()),
            "S4_loss": float(soft_ce(y_all[:, [1]], global_rate[:, [1]]).mean()),
        }
    )

    for sid in sorted(train["subject_id"].astype(str).unique()):
        valid = train["subject_id"].astype(str).eq(sid).to_numpy()
        tr = ~valid
        pred = fit_ridge(x_all[tr], y_all[tr], x_all[valid])
        base = np.tile(y_all[tr].mean(axis=0, keepdims=True), (valid.sum(), 1))
        rows.append(
            {
                "fold_type": "leave_subject_out",
                "fold": sid,
                "n_valid": int(valid.sum()),
                "model_loss": row_logloss(y_all[valid], pred),
                "baseline_loss": row_logloss(y_all[valid], base),
                "delta_vs_baseline": row_logloss(y_all[valid], pred) - row_logloss(y_all[valid], base),
                "Q3_loss": float(soft_ce(y_all[valid, [0]], pred[:, [0]]).mean()),
                "S4_loss": float(soft_ce(y_all[valid, [1]], pred[:, [1]]).mean()),
            }
        )

    train_sorted = train.sort_values(KEY).reset_index(drop=True)
    x_time = poly_context_features(train_sorted[CONTEXT_TARGETS].to_numpy(dtype=np.float64))
    y_time = train_sorted[TARGET_BLOCK].to_numpy(dtype=np.float64)
    for fold in range(5):
        valid = (np.arange(len(train_sorted)) % 5) == fold
        tr = ~valid
        pred = fit_ridge(x_time[tr], y_time[tr], x_time[valid])
        base = np.tile(y_time[tr].mean(axis=0, keepdims=True), (valid.sum(), 1))
        rows.append(
            {
                "fold_type": "date_interleave_5fold",
                "fold": str(fold),
                "n_valid": int(valid.sum()),
                "model_loss": row_logloss(y_time[valid], pred),
                "baseline_loss": row_logloss(y_time[valid], base),
                "delta_vs_baseline": row_logloss(y_time[valid], pred) - row_logloss(y_time[valid], base),
                "Q3_loss": float(soft_ce(y_time[valid, [0]], pred[:, [0]]).mean()),
                "S4_loss": float(soft_ce(y_time[valid, [1]], pred[:, [1]]).mean()),
            }
        )
    cv = pd.DataFrame(rows)
    cv.to_csv(OUT_MODEL_CV, index=False)
    return cv


def candidate_files() -> list[str]:
    files: list[str] = []
    for path in (LOCAL_CANDIDATES, PRIORITY, RANKER):
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "file" in frame.columns:
            files.extend(frame["file"].dropna().astype(str).tolist())
    keep: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if file_name in seen:
            continue
        try:
            locate(file_name)
        except FileNotFoundError:
            continue
        seen.add(file_name)
        keep.append(file_name)
    return keep


def block_metrics(values: np.ndarray, block_ids: np.ndarray) -> tuple[float, float, float]:
    means = []
    p90s = []
    variances = []
    for block_id in pd.unique(block_ids):
        mask = block_ids == block_id
        block = values[mask]
        means.append(float(np.mean(block)))
        p90s.append(float(np.quantile(block, 0.90)))
        variances.append(float(np.var(block)))
    return float(np.mean(means)), float(np.mean(p90s)), float(np.mean(variances))


def score_candidates(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    sample_key = sample[KEY].sort_values(KEY).reset_index(drop=True)
    y = train[TARGET_BLOCK].to_numpy(dtype=np.float64)
    x = poly_context_features(train[CONTEXT_TARGETS].to_numpy(dtype=np.float64))
    sample_blocks = sample_block_ids(train, sample)

    rows = []
    for file_name in candidate_files():
        arr = read_submission(file_name, sample_key)
        context = arr[:, CONTEXT_IDX]
        target = arr[:, TARGET_IDX]
        implied = fit_ridge(x, y, poly_context_features(context))
        kl = soft_kl(implied, target)
        ce = soft_ce(implied, target)
        abs_logit = np.abs(logit(implied) - logit(target))
        block_kl_mean, block_kl_p90, _ = block_metrics(kl.mean(axis=1), sample_blocks)
        block_target_var_mean, _, _ = block_metrics(target.mean(axis=1), sample_blocks)
        rows.append(
            {
                "file": file_name,
                "compat_kl_mean": float(kl.mean()),
                "compat_ce_mean": float(ce.mean()),
                "compat_abslogit_mean": float(abs_logit.mean()),
                "compat_q3_kl": float(kl[:, 0].mean()),
                "compat_s4_kl": float(kl[:, 1].mean()),
                "compat_q3_abslogit": float(abs_logit[:, 0].mean()),
                "compat_s4_abslogit": float(abs_logit[:, 1].mean()),
                "compat_block_kl_mean": block_kl_mean,
                "compat_block_kl_p90_mean": block_kl_p90,
                "compat_block_target_var_mean": block_target_var_mean,
                "compat_implied_q3_mean": float(implied[:, 0].mean()),
                "compat_implied_s4_mean": float(implied[:, 1].mean()),
                "candidate_q3_mean": float(target[:, 0].mean()),
                "candidate_s4_mean": float(target[:, 1].mean()),
                "candidate_context_mean": float(context.mean()),
            }
        )
    scores = pd.DataFrame(rows)
    raw = scores[scores["file"].eq("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv")]
    if len(raw) == 1:
        raw_row = raw.iloc[0]
        for col in [
            "compat_kl_mean",
            "compat_ce_mean",
            "compat_abslogit_mean",
            "compat_q3_kl",
            "compat_s4_kl",
            "compat_block_kl_p90_mean",
            "compat_block_target_var_mean",
        ]:
            scores[f"{col}_delta_vs_raw05"] = scores[col] - float(raw_row[col])
    scores.to_csv(OUT_SCORES, index=False)
    return scores


def add_lb_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in [
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "actual_anchor_score_final",
    ]:
        out[col] = pd.to_numeric(out.get(col), errors="coerce").fillna(0.0)
    out["abs_delta_vs_raw05_rawaxis"] = out["delta_vs_raw05_rawaxis"].abs()
    out["abs_bad_residual_axis_ratio"] = out["bad_residual_axis_ratio"].abs()
    for col in [
        "compat_kl_mean_delta_vs_raw05",
        "compat_abslogit_mean_delta_vs_raw05",
        "compat_block_kl_p90_mean_delta_vs_raw05",
        "compat_q3_kl_delta_vs_raw05",
        "compat_s4_kl_delta_vs_raw05",
    ]:
        out[col] = pd.to_numeric(out.get(col), errors="coerce").fillna(0.0)
        out[f"abs_{col}"] = out[col].abs()
    return out


def fit_predict_ridge(train: pd.DataFrame, valid: pd.DataFrame, features: list[str], alpha: float = 1.0) -> np.ndarray:
    x = train[features].to_numpy(dtype=np.float64)
    y = train["known_public"].to_numpy(dtype=np.float64)
    xp = valid[features].to_numpy(dtype=np.float64)
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    x = (x - mu) / sd
    xp = (xp - mu) / sd
    x_aug = np.column_stack([np.ones(len(x)), x])
    xp_aug = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(x_aug.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y
    return xp_aug @ beta


def lb_loocv(merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    known = add_lb_features(merged[merged["known_public"].notna()].copy()).reset_index(drop=True)
    model_defs = {
        "axes_baseline": ["abs_delta_vs_raw05_rawaxis", "abs_bad_residual_axis_ratio", "mean_abs_move_vs_raw05"],
        "compat_only": [
            "compat_kl_mean_delta_vs_raw05",
            "compat_abslogit_mean_delta_vs_raw05",
            "compat_block_kl_p90_mean_delta_vs_raw05",
        ],
        "compat_abs_only": [
            "abs_compat_kl_mean_delta_vs_raw05",
            "abs_compat_abslogit_mean_delta_vs_raw05",
            "abs_compat_block_kl_p90_mean_delta_vs_raw05",
        ],
        "axes_plus_compat": [
            "abs_delta_vs_raw05_rawaxis",
            "abs_bad_residual_axis_ratio",
            "mean_abs_move_vs_raw05",
            "compat_kl_mean_delta_vs_raw05",
            "compat_abslogit_mean_delta_vs_raw05",
            "compat_block_kl_p90_mean_delta_vs_raw05",
        ],
        "axes_plus_compat_abs": [
            "abs_delta_vs_raw05_rawaxis",
            "abs_bad_residual_axis_ratio",
            "mean_abs_move_vs_raw05",
            "abs_compat_kl_mean_delta_vs_raw05",
            "abs_compat_abslogit_mean_delta_vs_raw05",
            "abs_compat_block_kl_p90_mean_delta_vs_raw05",
        ],
    }
    pred_table = known[["file", "known_public"]].copy()
    rows = []
    y = known["known_public"].to_numpy(dtype=np.float64)
    for name, features in model_defs.items():
        pred = np.zeros(len(known), dtype=np.float64)
        for holdout in range(len(known)):
            tr = known.drop(index=holdout)
            valid = known.iloc[[holdout]]
            pred[holdout] = fit_predict_ridge(tr, valid, features)[0]
        err = pred - y
        pred_table[name] = pred
        pred_table[f"{name}_error"] = err
        rows.append(
            {
                "model": name,
                "features": ",".join(features),
                "mae": float(np.mean(np.abs(err))),
                "rmse": float(np.sqrt(np.mean(err**2))),
                "max_abs_error": float(np.max(np.abs(err))),
                "bias": float(err.mean()),
                "spearman": float(pd.Series(pred).corr(pd.Series(y), method="spearman")),
                "kendall": float(pd.Series(pred).corr(pd.Series(y), method="kendall")),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["mae", "rmse"]).reset_index(drop=True)
    pred_table.to_csv(OUT_KNOWN, index=False)
    summary.to_csv(OUT_LOOCV, index=False)
    return summary, pred_table


def write_report(cv: pd.DataFrame, scores: pd.DataFrame, loocv: pd.DataFrame, known_pred: pd.DataFrame) -> None:
    ranker = pd.read_csv(RANKER)
    local = pd.read_csv(LOCAL_CANDIDATES) if LOCAL_CANDIDATES.exists() else pd.DataFrame()
    merged = scores.merge(ranker, on="file", how="left")
    if not local.empty:
        local_cols = [
            "file",
            "rank",
            "tier",
            "raw05_relative_lb_proxy_mean",
            "raw05_relative_delta_vs_raw05_public",
            "lejepa_residual_health",
            "lejepa_combined_rank",
            "actual_anchor_score_final",
            "bad_residual_axis_ratio",
        ]
        merged = merged.merge(
            local[[c for c in local_cols if c in local.columns]],
            on="file",
            how="left",
            suffixes=("", "_local"),
        )
        for col in ["actual_anchor_score_final", "bad_residual_axis_ratio"]:
            local_col = f"{col}_local"
            if local_col in merged.columns:
                merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(
                    pd.to_numeric(merged[local_col], errors="coerce")
                )
    top_cols = [
        "file",
        "rank",
        "tier",
        "compat_kl_mean_delta_vs_raw05",
        "compat_abslogit_mean_delta_vs_raw05",
        "compat_block_kl_p90_mean_delta_vs_raw05",
        "raw05_relative_lb_proxy_mean",
        "actual_anchor_score_final",
        "bad_residual_axis_ratio",
        "lejepa_residual_health",
    ]
    top = merged[merged["rank"].notna()].sort_values(
        ["compat_kl_mean_delta_vs_raw05", "compat_abslogit_mean_delta_vs_raw05"]
    )
    cv_summary = (
        cv[cv["fold_type"].ne("all_rows_baseline")]
        .groupby("fold_type", as_index=False)
        .agg(
            folds=("fold", "count"),
            mean_model_loss=("model_loss", "mean"),
            mean_baseline_loss=("baseline_loss", "mean"),
            mean_delta=("delta_vs_baseline", "mean"),
            max_delta=("delta_vs_baseline", "max"),
        )
    )
    lines = [
        "# JEPA Context-Target Compatibility Audit",
        "",
        "This audit fits a train-label context->target block model: context = Q1/Q2/S1/S2/S3, target block = Q3/S4. Candidate submissions are scored by how compatible their Q3/S4 probabilities are with their own context block.",
        "",
        "## Train CV",
        "",
        "```csv",
        cv_summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Public-Anchor LOOCV With Compatibility Features",
        "",
        "```csv",
        loocv.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Known Public Predictions",
        "",
        "```csv",
        known_pred.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Current Candidate Compatibility Ranking",
        "",
        "```csv",
        top[[c for c in top_cols if c in top.columns]].head(24).round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    cv = model_cv(train)
    scores = score_candidates(train, sample)
    ranker = pd.read_csv(RANKER)
    merged = scores.merge(ranker, on="file", how="left")
    loocv, known_pred = lb_loocv(merged)
    write_report(cv, scores, loocv, known_pred)

    print("[train_cv]")
    print(pd.read_csv(OUT_MODEL_CV).groupby("fold_type").agg({"model_loss": "mean", "baseline_loss": "mean", "delta_vs_baseline": "mean"}).round(10).to_string())
    print("\n[lb_loocv]")
    print(loocv.round(10).to_string(index=False))
    print("\n[top_compat_candidates]")
    local = pd.read_csv(LOCAL_CANDIDATES)
    show = scores.merge(local, on="file", how="inner").sort_values(
        ["compat_kl_mean_delta_vs_raw05", "compat_abslogit_mean_delta_vs_raw05"]
    )
    cols = [
        "rank",
        "file",
        "tier",
        "compat_kl_mean_delta_vs_raw05",
        "compat_abslogit_mean_delta_vs_raw05",
        "compat_block_kl_p90_mean_delta_vs_raw05",
        "raw05_relative_lb_proxy_mean",
        "actual_anchor_score_final",
        "bad_residual_axis_ratio",
    ]
    print(show[cols].head(16).round(10).to_string(index=False))
    print(f"\nwrote: {OUT_MODEL_CV}")
    print(f"wrote: {OUT_SCORES}")
    print(f"wrote: {OUT_KNOWN}")
    print(f"wrote: {OUT_LOOCV}")
    print(f"wrote: {OUT_REPORT}")


if __name__ == "__main__":
    main()
