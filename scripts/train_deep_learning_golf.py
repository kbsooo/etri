from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.feature_selection import f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, log_loss
from sklearn.preprocessing import StandardScaler

from train_hourly_transformer_encoder import dataframe_to_markdown, targetwise_prediction
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, KEY_COLUMNS, SEED, TARGET_COLUMNS, make_subject_time_folds, normalize_keys
from train_tiny_deviation_encoder import add_calendar_features, build_daily_features, subject_relative


def load_daily_features(keys: pd.DataFrame, data_dir: Path, cache_path: Path, force: bool) -> pd.DataFrame:
    if cache_path.exists() and not force:
        cached = pd.read_parquet(cache_path).copy()
        for col in ("subject_id", "lifelog_date"):
            cached[col] = cached[col].astype(str)
        return keys.merge(cached, on=["subject_id", "lifelog_date"], how="left")
    return build_daily_features(keys, data_dir, cache_path, force)


@dataclass(frozen=True)
class Spec:
    name: str
    mode: str
    model: str
    top_k: int
    bottleneck: int
    weight_decay: float
    blend: float


class GolfNet(torch.nn.Module):
    def __init__(self, in_dim: int, out_dim: int, model: str, bottleneck: int) -> None:
        super().__init__()
        if model == "linear":
            self.net = torch.nn.Linear(in_dim, out_dim)
        elif model == "lowrank":
            self.net = torch.nn.Sequential(
                torch.nn.Linear(in_dim, bottleneck, bias=False),
                torch.nn.Linear(bottleneck, out_dim),
            )
        elif model == "tiny_mlp":
            self.net = torch.nn.Sequential(
                torch.nn.Linear(in_dim, bottleneck),
                torch.nn.Tanh(),
                torch.nn.Linear(bottleneck, out_dim),
            )
        else:
            raise ValueError(model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def param_count(in_dim: int, out_dim: int, model: str, bottleneck: int) -> int:
    if model == "linear":
        return in_dim * out_dim + out_dim
    if model == "lowrank":
        return in_dim * bottleneck + bottleneck * out_dim + out_dim
    if model == "tiny_mlp":
        return in_dim * bottleneck + bottleneck + bottleneck * out_dim + out_dim
    raise ValueError(model)


def choose_device(requested: str) -> torch.device:
    if requested == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    if requested == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def multi_target_feature_scores(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    scores = np.zeros(x.shape[1], dtype=float)
    counts = np.zeros(x.shape[1], dtype=float)
    for target_i in range(y.shape[1]):
        if len(np.unique(y[:, target_i])) < 2:
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            f_values, _ = f_classif(x, y[:, target_i])
        finite = np.nan_to_num(f_values, nan=0.0, posinf=0.0, neginf=0.0)
        scores += finite
        counts += 1.0
    return scores / np.maximum(counts, 1.0)


def prepare_matrix(
    x_fit_raw: np.ndarray,
    x_eval_raw: np.ndarray,
    x_sample_raw: np.ndarray,
    y_fit: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_fit = scaler.fit_transform(imputer.fit_transform(x_fit_raw))
    x_eval = scaler.transform(imputer.transform(x_eval_raw))
    x_sample = scaler.transform(imputer.transform(x_sample_raw))
    variable = np.nanstd(x_fit, axis=0) > 1e-10
    if not variable.any():
        variable[:] = True
    original_idx = np.flatnonzero(variable)
    x_fit_v = x_fit[:, variable]
    x_eval_v = x_eval[:, variable]
    x_sample_v = x_sample[:, variable]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        scores = multi_target_feature_scores(x_fit_v, y_fit)
    local_keep = np.argsort(scores)[::-1][: min(top_k, x_fit_v.shape[1])]
    keep = original_idx[local_keep]
    return x_fit_v[:, local_keep], x_eval_v[:, local_keep], x_sample_v[:, local_keep], keep


def fit_predict_net(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    spec: Spec,
    device: torch.device,
    epochs: int,
    patience: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED + spec.top_k * 17 + spec.bottleneck * 31)
    order = rng.permutation(len(x_fit))
    valid_n = max(32, int(round(len(order) * 0.18)))
    valid_idx = order[:valid_n]
    train_idx = order[valid_n:]

    x_t = torch.as_tensor(x_fit[train_idx], dtype=torch.float32, device=device)
    y_t = torch.as_tensor(y_fit[train_idx], dtype=torch.float32, device=device)
    x_v = torch.as_tensor(x_fit[valid_idx], dtype=torch.float32, device=device)
    y_v = torch.as_tensor(y_fit[valid_idx], dtype=torch.float32, device=device)

    torch.manual_seed(SEED)
    model = GolfNet(x_fit.shape[1], y_fit.shape[1], spec.model, spec.bottleneck).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.02, weight_decay=spec.weight_decay)
    loss_fn = torch.nn.BCEWithLogitsLoss()
    best_state: dict[str, torch.Tensor] | None = None
    best_loss = float("inf")
    stale = 0
    for _ in range(epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(model(x_t), y_t)
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            val_loss = float(loss_fn(model(x_v), y_v).detach().cpu())
        if val_loss < best_loss - 1e-5:
            best_loss = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        eval_logits = model(torch.as_tensor(x_eval, dtype=torch.float32, device=device)).detach().cpu().numpy()
        sample_logits = model(torch.as_tensor(x_sample, dtype=torch.float32, device=device)).detach().cpu().numpy()
    return 1.0 / (1.0 + np.exp(-np.clip(eval_logits, -50, 50))), 1.0 / (1.0 + np.exp(-np.clip(sample_logits, -50, 50)))


def macro_f1_at_half(y_true: pd.DataFrame, pred: np.ndarray) -> float:
    scores = []
    for i, target in enumerate(TARGET_COLUMNS):
        scores.append(f1_score(y_true[target].to_numpy(int), pred[:, i] >= 0.5, zero_division=0))
    return float(np.mean(scores))


def grouped_abs_drift(
    keys: pd.DataFrame,
    pred: np.ndarray,
    reference_submission: str | None,
    group_col: str,
) -> dict[str, float]:
    if not reference_submission:
        return {}
    ref_path = Path(reference_submission)
    if not ref_path.exists() or group_col not in keys.columns:
        return {}
    reference = normalize_keys(pd.read_csv(ref_path))
    if not reference[KEY_COLUMNS].equals(keys[KEY_COLUMNS]):
        return {}
    frame = keys[[group_col]].copy()
    ref_values = reference[TARGET_COLUMNS].to_numpy(float)
    frame["_drift"] = np.abs(np.clip(pred, EPS, 1 - EPS) - np.clip(ref_values, EPS, 1 - EPS)).mean(axis=1)
    return {str(k): float(v) for k, v in frame.groupby(group_col)["_drift"].mean().to_dict().items()}


def build_specs(args: argparse.Namespace) -> list[Spec]:
    specs: list[Spec] = []
    for mode in args.feature_modes:
        for top_k in args.top_k:
            for blend in args.blends:
                specs.append(Spec(f"{mode}__linear_k{top_k}_b{blend:g}", mode, "linear", top_k, 0, args.weight_decay[0], blend))
                for bottleneck in args.bottlenecks:
                    for wd in args.weight_decay:
                        specs.append(Spec(f"{mode}__lowrank_r{bottleneck}_k{top_k}_wd{wd:g}_b{blend:g}", mode, "lowrank", top_k, bottleneck, wd, blend))
                        specs.append(Spec(f"{mode}__mlp_h{bottleneck}_k{top_k}_wd{wd:g}_b{blend:g}", mode, "tiny_mlp", top_k, bottleneck, wd, blend))
    return specs


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    all_keys = pd.concat([train[KEY_COLUMNS], sample[KEY_COLUMNS]], ignore_index=True)
    all_features = load_daily_features(all_keys, Path(args.data_dir), Path(args.cache_path), args.force_rebuild_cache)
    all_features = add_calendar_features(all_features)
    train_features = all_features.iloc[: len(train)].reset_index(drop=True)
    sample_features = all_features.iloc[len(train) :].reset_index(drop=True)
    feature_cols = [c for c in train_features.columns if c not in KEY_COLUMNS]
    x_all = train_features[feature_cols].to_numpy(float)
    x_sample = sample_features[feature_cols].to_numpy(float)
    train_subjects = train["subject_id"].astype(str).to_numpy(object)
    sample_subjects = sample["subject_id"].astype(str).to_numpy(object)
    y_all = train[TARGET_COLUMNS].to_numpy(float)
    folds = make_subject_time_folds(train, args.n_folds)
    specs = build_specs(args)
    device = choose_device(args.device)

    predictions = {spec.name: np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
    sample_folds = {spec.name: [] for spec in specs}
    selected_rows = []
    fold_rows = []
    prior_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    prior_sample_parts = []
    global_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    global_sample_parts = []

    for fold_i, fold in enumerate(folds, 1):
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.prior_alpha)
        prior_sample_all = subject_prior(train.iloc[fold.train_idx], sample, args.prior_alpha)
        prior_oof[fold.val_idx] = prior_eval_all
        prior_sample_parts.append(prior_sample_all)
        means = train.iloc[fold.train_idx][TARGET_COLUMNS].mean().to_numpy(float)
        global_oof[fold.val_idx] = means[None, :]
        global_sample_parts.append(np.repeat(means[None, :], len(sample), axis=0))

        rel_fit, rel_eval, rel_sample = subject_relative(x_all, x_sample, train_subjects, sample_subjects, fold.train_idx, fold.val_idx)
        raw_fit, raw_eval, raw_sample = x_all[fold.train_idx], x_all[fold.val_idx], x_sample
        mode_cache = {
            "raw": (raw_fit, raw_eval, raw_sample),
            "deviation": (rel_fit, rel_eval, rel_sample),
            "raw_plus_deviation": (
                np.concatenate([raw_fit, rel_fit], axis=1),
                np.concatenate([raw_eval, rel_eval], axis=1),
                np.concatenate([raw_sample, rel_sample], axis=1),
            ),
        }
        y_fit = y_all[fold.train_idx]
        y_eval = y_all[fold.val_idx]
        fold_sample = {spec.name: np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float) for spec in specs}
        for spec in specs:
            x_fit_raw, x_eval_raw, x_s_raw = mode_cache[spec.mode]
            x_fit, x_eval, x_s, keep = prepare_matrix(x_fit_raw, x_eval_raw, x_s_raw, y_fit, spec.top_k)
            pred_eval_raw, pred_sample_raw = fit_predict_net(
                x_fit, y_fit, x_eval, x_s, spec, device, args.epochs, args.patience
            )
            pred_eval = np.clip((1.0 - spec.blend) * prior_eval_all + spec.blend * pred_eval_raw, EPS, 1.0 - EPS)
            pred_sample = np.clip((1.0 - spec.blend) * prior_sample_all + spec.blend * pred_sample_raw, EPS, 1.0 - EPS)
            predictions[spec.name][fold.val_idx] = pred_eval
            fold_sample[spec.name] = pred_sample
            selected_rows.append(
                {
                    "fold": fold_i,
                    "source": spec.name,
                    "mode": spec.mode,
                    "model": spec.model,
                    "top_k": spec.top_k,
                    "bottleneck": spec.bottleneck,
                    "weight_decay": spec.weight_decay,
                    "blend": spec.blend,
                    "params": param_count(x_fit.shape[1], len(TARGET_COLUMNS), spec.model, spec.bottleneck),
                    "selected_feature_indices": " ".join(map(str, keep.tolist())),
                }
            )
            for target_i, target in enumerate(TARGET_COLUMNS):
                fold_rows.append(
                    {
                        "fold": fold_i,
                        "target": target,
                        "source": spec.name,
                        "loss": float(log_loss(y_eval[:, target_i], pred_eval[:, target_i], labels=[0, 1])),
                    }
                )
        for name, pred in fold_sample.items():
            sample_folds[name].append(pred)
        print(f"[golf] fold {fold_i}/{len(folds)} done", flush=True)

    sample_predictions = {name: np.clip(np.mean(parts, axis=0), EPS, 1.0 - EPS) for name, parts in sample_folds.items()}
    baselines = {
        "bias_global": (np.clip(global_oof, EPS, 1 - EPS), np.clip(np.mean(global_sample_parts, axis=0), EPS, 1 - EPS), 7),
        "subject_prior": (np.clip(prior_oof, EPS, 1 - EPS), np.clip(np.mean(prior_sample_parts, axis=0), EPS, 1 - EPS), 7 * train["subject_id"].nunique()),
    }

    score_rows = []
    for name, (pred, sample_pred, params) in baselines.items():
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_pred, Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append(
            {
                "source": name,
                "avg_log_loss": avg,
                "macro_f1_at_0p5": macro_f1_at_half(train[TARGET_COLUMNS], pred),
                "mean_params": params,
                "drift_vs_reference": drift.get("mean_abs_drift"),
                **per,
            }
        )
    for spec in specs:
        pred = np.clip(predictions[spec.name], EPS, 1.0 - EPS)
        predictions[spec.name] = pred
        avg, per = average_log_loss(train[TARGET_COLUMNS], pred)
        drift = drift_vs_reference(sample, sample_predictions[spec.name], Path(args.reference_submission) if args.reference_submission else None)
        score_rows.append(
            {
                "source": spec.name,
                "avg_log_loss": avg,
                "macro_f1_at_0p5": macro_f1_at_half(train[TARGET_COLUMNS], pred),
                "mean_params": param_count(spec.top_k, len(TARGET_COLUMNS), spec.model, spec.bottleneck),
                "drift_vs_reference": drift.get("mean_abs_drift"),
                "mode": spec.mode,
                "model": spec.model,
                "top_k": spec.top_k,
                "bottleneck": spec.bottleneck,
                "weight_decay": spec.weight_decay,
                "blend": spec.blend,
                **per,
            }
        )

    score_df = pd.DataFrame(score_rows).sort_values("avg_log_loss").reset_index(drop=True)
    model_predictions = {**{k: v[0] for k, v in baselines.items()}, **predictions}
    model_sample_predictions = {**{k: v[1] for k, v in baselines.items()}, **sample_predictions}
    target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, model_predictions, model_sample_predictions, train)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    target_drift = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)
    best_global = str(score_df.iloc[0]["source"])
    global_avg, global_per = average_log_loss(train[TARGET_COLUMNS], model_predictions[best_global])
    global_drift = drift_vs_reference(sample, model_sample_predictions[best_global], Path(args.reference_submission) if args.reference_submission else None)
    best_name = "targetwise" if target_avg <= global_avg else best_global
    best_oof = target_oof if best_name == "targetwise" else model_predictions[best_global]
    best_sample = target_sample if best_name == "targetwise" else model_sample_predictions[best_global]
    best_avg = target_avg if best_name == "targetwise" else global_avg
    best_per = target_per if best_name == "targetwise" else global_per
    best_drift = target_drift if best_name == "targetwise" else global_drift
    prior_avg, prior_per = average_log_loss(train[TARGET_COLUMNS], prior_oof)
    best_target_gain_vs_prior = {target: float(prior_per[target] - best_per[target]) for target in TARGET_COLUMNS}
    global_target_gain_vs_prior = {target: float(prior_per[target] - global_per[target]) for target in TARGET_COLUMNS}
    best_subject_drift = grouped_abs_drift(sample, best_sample, args.reference_submission, "subject_id")
    global_subject_drift = grouped_abs_drift(sample, model_sample_predictions[best_global], args.reference_submission, "subject_id")

    score_df.to_csv(output_dir / "golf_scores.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "golf_fold_losses.csv", index=False)
    pd.DataFrame(selected_rows).to_csv(output_dir / "golf_selected_features.csv", index=False)
    pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()]).to_csv(output_dir / "targetwise_selection.csv", index=False)
    write_prediction(output_dir / "oof_deep_learning_golf_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_deep_learning_golf_best.csv", sample, best_sample, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(best_avg),
        "best_per_target": {target: float(best_per[target]) for target in TARGET_COLUMNS},
        "best_drift_vs_reference": best_drift,
        "best_global_source": best_global,
        "best_global_avg_log_loss": float(global_avg),
        "best_global_drift_vs_reference": global_drift,
        "best_global_subject_drift_vs_reference": global_subject_drift,
        "best_global_target_gain_vs_subject_prior": global_target_gain_vs_prior,
        "targetwise_avg_log_loss": float(target_avg),
        "targetwise_drift_vs_reference": target_drift,
        "targetwise_subject_drift_vs_reference": grouped_abs_drift(sample, target_sample, args.reference_submission, "subject_id"),
        "targetwise_sources": target_sources,
        "targetwise_source_losses": target_losses,
        "subject_prior_avg_log_loss": float(prior_avg),
        "best_target_gain_vs_subject_prior": best_target_gain_vs_prior,
        "best_subject_drift_vs_reference": best_subject_drift,
        "n_base_features": len(feature_cols),
        "n_candidates": len(specs) + len(baselines),
        "device": str(device),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Deep Learning Golf v1",
        "",
        "## Goal",
        "",
        "Start the neural encoder-decoder path from the smallest possible parameter counts. This run avoids teacher submissions and uses v83 only as a drift reference.",
        "",
        "## Setup",
        "",
        f"- Device: `{device}`",
        f"- Base daily/window features: `{len(feature_cols)}`",
        "- Input top-k: small supervised fold-local selections only.",
        "- Decoder families: bias-only, subject prior, linear, low-rank rank 1-4, tiny tanh MLP hidden 1-4.",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Subject-prior OOF avg logloss: `{prior_avg:.6f}`",
        f"- Gain vs subject prior: `{prior_avg - best_avg:.6f}`",
        f"- Macro F1 @ 0.5: `{macro_f1_at_half(train[TARGET_COLUMNS], best_oof):.6f}`",
        f"- Drift vs v83 reference: `{best_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Target Gain vs Subject Prior",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "gain": best_target_gain_vs_prior[target]} for target in TARGET_COLUMNS])),
        "",
        "## Subject Drift vs v83",
        "",
        dataframe_to_markdown(pd.DataFrame([{"subject_id": subject, "mean_abs_drift": drift} for subject, drift in best_subject_drift.items()])),
        "",
        "## Top Scores",
        "",
        dataframe_to_markdown(score_df.head(25)),
        "",
        "## Target-Wise Selection",
        "",
        f"- Target-wise avg logloss: `{target_avg:.6f}`",
        f"- Target-wise drift vs v83: `{target_drift.get('mean_abs_drift', float('nan')):.6f}`",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source, "loss": target_losses[target]} for target, source in target_sources.items()])),
        "",
        "## Decision",
        "",
        "This is the minimum-parameter neural floor. If a rank-1/hidden-1 model beats subject prior with low drift, the signal is probably a simple subject-relative axis. If only larger or target-wise selected models win, the branch needs stronger validation before it can be trusted.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deep Learning Golf: minimum-parameter neural decoders.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--data-dir", default="data/ch2025_data_items")
    parser.add_argument("--cache-path", default="outputs/tiny_deviation_encoder_v1/daily_window_features.parquet")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/deep_learning_golf_v1")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--feature-modes", nargs="+", default=["raw", "deviation", "raw_plus_deviation"])
    parser.add_argument("--top-k", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    parser.add_argument("--bottlenecks", type=int, nargs="+", default=[1, 2, 3, 4])
    parser.add_argument("--blends", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.35])
    parser.add_argument("--weight-decay", type=float, nargs="+", default=[0.01, 0.1])
    parser.add_argument("--epochs", type=int, default=350)
    parser.add_argument("--patience", type=int, default=40)
    parser.add_argument("--device", choices=["cpu", "mps", "cuda"], default="mps")
    parser.add_argument("--force-rebuild-cache", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
