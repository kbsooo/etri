from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
MERGE_COLUMNS = ["subject_id", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


DEFAULT_LATENTS = {
    "global_only_event": "outputs/domain_masked_patch_encoder_v1/only_event/embeddings_mean.parquet",
    "global_event_cross_missing": "outputs/domain_masked_patch_encoder_v1/event_cross_missing/embeddings_mean.parquet",
    "subject_token_event_cross_missing": "outputs/domain_masked_patch_encoder_v2_subject_norm/subject_channel_token/event_cross_missing/embeddings_mean.parquet",
}


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in KEY_COLUMNS:
        if col in out:
            out[col] = out[col].astype(str)
    if "lifelog_date" in out:
        out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    if "sleep_date" in out:
        out["sleep_date"] = pd.to_datetime(out["sleep_date"]).dt.strftime("%Y-%m-%d")
    return out


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_parts: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(int), n_folds)
        for fold, chunk in enumerate(chunks):
            val_parts[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    folds = []
    for part in val_parts:
        val_idx = np.array(sorted(part), dtype=int)
        folds.append((np.setdiff1d(all_idx, val_idx), val_idx))
    return folds


def subject_prior(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean()
    sums = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    counts = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    rates = (sums + alpha * global_rate) / (counts + alpha)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=float)
    for i, subject in enumerate(eval_part["subject_id"].astype(str)):
        pred[i] = rates.loc[subject].to_numpy(float) if subject in rates.index else global_rate.to_numpy(float)
    return np.clip(pred, EPS, 1.0 - EPS)


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    losses = {}
    for i, target in enumerate(TARGET_COLUMNS):
        losses[target] = float(log_loss(y_true[target].astype(int), np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1]))
    return float(np.mean(list(losses.values()))), losses


def load_latent_table(path: Path, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    latent = pd.read_parquet(path).copy()
    latent["subject_id"] = latent["subject_id"].astype(str)
    latent["lifelog_date"] = pd.to_datetime(latent["lifelog_date"]).dt.strftime("%Y-%m-%d")
    z_cols = [col for col in latent.columns if col.startswith("z_")]
    if not z_cols:
        raise ValueError(f"No z_* latent columns in {path}")
    train_x = train[KEY_COLUMNS].merge(latent[MERGE_COLUMNS + z_cols], on=MERGE_COLUMNS, how="left", validate="one_to_one")
    sample_x = sample[KEY_COLUMNS].merge(latent[MERGE_COLUMNS + z_cols], on=MERGE_COLUMNS, how="left", validate="one_to_one")
    if train_x[z_cols].isna().all(axis=1).any() or sample_x[z_cols].isna().all(axis=1).any():
        raise ValueError(f"Latent keys do not cover train/sample for {path}")
    return train_x, sample_x, z_cols


def subject_deviation_features(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    z_cols: list[str],
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fit = train_x.iloc[fit_idx].copy()
    eval_part = train_x.iloc[eval_idx].copy()
    global_center = fit[z_cols].median(axis=0, skipna=True).fillna(0.0)
    centers = fit.groupby("subject_id")[z_cols].median()

    def transform(part: pd.DataFrame) -> np.ndarray:
        values = part[z_cols].to_numpy(float)
        center_rows = []
        for subject in part["subject_id"].astype(str):
            center_rows.append(centers.loc[subject].to_numpy(float) if subject in centers.index else global_center.to_numpy(float))
        return values - np.vstack(center_rows)

    return transform(fit), transform(eval_part), transform(sample_x)


def absolute_features(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    z_cols: list[str],
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        train_x.iloc[fit_idx][z_cols].to_numpy(float),
        train_x.iloc[eval_idx][z_cols].to_numpy(float),
        sample_x[z_cols].to_numpy(float),
    )


def feature_views(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    z_cols: list[str],
    fit_idx: np.ndarray,
    eval_idx: np.ndarray,
) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    abs_fit, abs_eval, abs_sample = absolute_features(train_x, sample_x, z_cols, fit_idx, eval_idx)
    dev_fit, dev_eval, dev_sample = subject_deviation_features(train_x, sample_x, z_cols, fit_idx, eval_idx)
    return {
        "absolute": (abs_fit, abs_eval, abs_sample),
        "deviation": (dev_fit, dev_eval, dev_sample),
        "absolute_plus_deviation": (
            np.concatenate([abs_fit, dev_fit], axis=1),
            np.concatenate([abs_eval, dev_eval], axis=1),
            np.concatenate([abs_sample, dev_sample], axis=1),
        ),
    }


def fit_probe(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    prior_eval: np.ndarray,
    prior_sample: np.ndarray,
    c_value: float,
    blend: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        return prior_eval, prior_sample
    model = make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        StandardScaler(),
        LogisticRegression(C=c_value, max_iter=2000, solver="lbfgs"),
    )
    model.fit(x_fit, y_fit.astype(int))
    pred_eval = model.predict_proba(x_eval)[:, 1]
    pred_sample = model.predict_proba(x_sample)[:, 1]
    pred_eval = blend * pred_eval + (1.0 - blend) * prior_eval
    pred_sample = blend * pred_sample + (1.0 - blend) * prior_sample
    return np.clip(pred_eval, EPS, 1.0 - EPS), np.clip(pred_sample, EPS, 1.0 - EPS)


def write_prediction(path: Path, keys: pd.DataFrame, pred: np.ndarray, oof: bool) -> None:
    out = keys[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        out[f"pred_{target}" if oof else target] = np.clip(pred[:, i], EPS, 1.0 - EPS)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def parse_latents(items: list[str]) -> dict[str, Path]:
    if not items:
        return {name: Path(path) for name, path in DEFAULT_LATENTS.items()}
    parsed = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Latent spec must be name=path, got {item}")
        name, path = item.split("=", 1)
        parsed[name] = Path(path)
    return parsed


def run(args: argparse.Namespace) -> None:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    latent_specs = parse_latents(args.latent)
    folds = make_subject_time_folds(train, args.n_folds)
    c_values = [float(v) for v in args.c_values]
    blends = [float(v) for v in args.blends]

    all_oof: dict[str, np.ndarray] = {"subject_prior": np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)}
    all_sample_folds: dict[str, list[np.ndarray]] = {"subject_prior": []}
    fold_rows = []

    latent_tables = {
        name: load_latent_table(path, train, sample)
        for name, path in latent_specs.items()
    }

    for fold_i, (fit_idx, eval_idx) in enumerate(folds, 1):
        fit_frame = train.iloc[fit_idx]
        eval_frame = train.iloc[eval_idx]
        prior_eval_all = subject_prior(fit_frame, eval_frame, args.prior_alpha)
        prior_sample_all = subject_prior(fit_frame, sample, args.prior_alpha)
        all_oof["subject_prior"][eval_idx] = prior_eval_all
        all_sample_folds["subject_prior"].append(prior_sample_all)
        for latent_name, (train_x, sample_x, z_cols) in latent_tables.items():
            views = feature_views(train_x, sample_x, z_cols, fit_idx, eval_idx)
            for view_name, (x_fit, x_eval, x_sample) in views.items():
                for c_value in c_values:
                    for blend in blends:
                        source = f"{latent_name}__{view_name}__c{c_value:g}_b{blend:g}"
                        all_oof.setdefault(source, np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float))
                        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
                        for target_i, target in enumerate(TARGET_COLUMNS):
                            y_fit = fit_frame[target].to_numpy(int)
                            y_eval = eval_frame[target].to_numpy(int)
                            pred_eval, pred_sample = fit_probe(
                                x_fit,
                                y_fit,
                                x_eval,
                                x_sample,
                                prior_eval_all[:, target_i],
                                prior_sample_all[:, target_i],
                                c_value,
                                blend,
                            )
                            all_oof[source][eval_idx, target_i] = pred_eval
                            fold_sample[:, target_i] = pred_sample
                            fold_rows.append(
                                {
                                    "fold": fold_i,
                                    "source": source,
                                    "latent": latent_name,
                                    "feature_view": view_name,
                                    "c": c_value,
                                    "blend": blend,
                                    "target": target,
                                    "loss": float(log_loss(y_eval, pred_eval, labels=[0, 1])),
                                }
                            )
                        all_sample_folds.setdefault(source, []).append(fold_sample)

    all_sample = {name: np.mean(parts, axis=0) for name, parts in all_sample_folds.items()}
    score_rows = []
    for source, pred in all_oof.items():
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        row = {"source": source, "avg_log_loss": avg, **per}
        score_rows.append(row)
    scores = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)
    scores.to_csv(output_dir / "probe_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "fold_target_losses.csv", index=False)

    best_source = str(scores.iloc[0]["source"])
    write_prediction(output_dir / "oof_best.csv", train, all_oof[best_source], oof=True)
    write_prediction(output_dir / "probe_submission_best.csv", sample, all_sample[best_source], oof=False)

    prior_avg, prior_per = average_log_loss(train[TARGET_COLUMNS], all_oof["subject_prior"])
    report = {
        "latent_specs": {name: str(path) for name, path in latent_specs.items()},
        "n_folds": args.n_folds,
        "prior_alpha": args.prior_alpha,
        "c_values": c_values,
        "blends": blends,
        "subject_prior_avg_log_loss": prior_avg,
        "subject_prior_per_target": prior_per,
        "best_source": best_source,
        "best_avg_log_loss": float(scores.iloc[0]["avg_log_loss"]),
        "best_delta_vs_subject_prior": float(scores.iloc[0]["avg_log_loss"] - prior_avg),
        "top_scores": scores.head(20).to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Domain SSL Latent Frozen Probe",
        "",
        "## Purpose",
        "",
        "Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.",
        "",
        "## Baseline",
        "",
        f"- Subject-prior avg logloss: `{prior_avg:.6f}`",
        "",
        "## Best",
        "",
        f"- Source: `{best_source}`",
        f"- Avg logloss: `{float(scores.iloc[0]['avg_log_loss']):.6f}`",
        f"- Delta vs subject prior: `{float(scores.iloc[0]['avg_log_loss'] - prior_avg):.6f}`",
        "",
        "## Top Scores",
        "",
        dataframe_to_markdown(scores.head(12)),
        "",
        "## Decision Rule",
        "",
        "Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Frozen probes for label-free domain SSL latents.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_ssl_latent_frozen_probe_v1")
    parser.add_argument("--latent", action="append", default=[], help="Latent spec as name=path. Defaults to selected domain SSL candidates.")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.03, 0.1, 0.3])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
