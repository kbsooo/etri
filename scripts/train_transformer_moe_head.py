from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from build_hourly_transformer_view_ensemble import collect_prediction_pairs, prediction_matrix
from train_hourly_transformer_encoder import dataframe_to_markdown
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, safe_logit, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[["subject_id", "sleep_date", "lifelog_date"]].assign(_split="train", _row=np.arange(len(train))),
            sample[["subject_id", "sleep_date", "lifelog_date"]].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows["_date"] = pd.to_datetime(all_rows["lifelog_date"])
    ordered = all_rows.sort_values(["subject_id", "_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    all_rows = all_rows.merge(ordered[["_split", "_row", "panel_index", "panel_position"]], on=["_split", "_row"], how="left")
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    return pd.concat([train.reset_index(drop=True), train_pos], axis=1), pd.concat([sample.reset_index(drop=True), sample_pos], axis=1)


def load_sources(input_dirs: list[Path]) -> tuple[list[str], np.ndarray, np.ndarray]:
    pairs = collect_prediction_pairs(input_dirs)
    names, oof_list, sub_list = [], [], []
    for name, oof_path, sub_path in pairs:
        names.append(f"{oof_path.parents[1].name}__{name}")
        oof_list.append(prediction_matrix(oof_path, target_prefix=True))
        sub_list.append(prediction_matrix(sub_path, target_prefix=False))
    return names, np.stack(oof_list, axis=0), np.stack(sub_list, axis=0)


def source_score_table(train: pd.DataFrame, names: list[str], source_oof: np.ndarray) -> pd.DataFrame:
    rows = []
    for i, name in enumerate(names):
        avg, per = average_log_loss(train[TARGET_COLUMNS], source_oof[i])
        rows.append({"source": name, "avg_log_loss": avg, **per})
    return pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)


def targetwise_best(train: pd.DataFrame, sample: pd.DataFrame, names: list[str], source_oof: np.ndarray, source_sub: np.ndarray) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    oof = np.zeros((len(train), len(TARGET_COLUMNS)))
    sub = np.zeros((len(sample), len(TARGET_COLUMNS)))
    rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        losses = [
            float(log_loss(train[target].to_numpy(int), source_oof[source_i, :, target_i], labels=[0, 1]))
            for source_i in range(len(names))
        ]
        best_i = int(np.argmin(losses))
        oof[:, target_i] = source_oof[best_i, :, target_i]
        sub[:, target_i] = source_sub[best_i, :, target_i]
        rows.append({"target": target, "source": names[best_i], "loss": losses[best_i]})
    return np.clip(oof, EPS, 1 - EPS), np.clip(sub, EPS, 1 - EPS), pd.DataFrame(rows)


def meta_features(
    source_pred: np.ndarray,
    target_i: int,
    panel_position: np.ndarray,
    prior: np.ndarray,
) -> np.ndarray:
    target_logits = safe_logit(source_pred[:, :, target_i].T)
    target_probs = source_pred[:, :, target_i].T
    mean_logit = target_logits.mean(axis=1, keepdims=True)
    std_logit = target_logits.std(axis=1, keepdims=True)
    min_prob = target_probs.min(axis=1, keepdims=True)
    max_prob = target_probs.max(axis=1, keepdims=True)
    panel = panel_position.reshape(-1, 1)
    return np.concatenate([target_logits, mean_logit, std_logit, min_prob, max_prob, panel, prior.reshape(-1, 1)], axis=1)


def train_nested_moe(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    names: list[str],
    source_oof: np.ndarray,
    source_sub: np.ndarray,
    c_value: float,
    prior_alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    folds = make_subject_time_folds(train, 5)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)))
    sample_folds = []
    train_panel = train["panel_position"].to_numpy(float)
    sample_panel = sample["panel_position"].to_numpy(float)
    for fold in folds:
        fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)))
        prior_fit_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], prior_alpha)
        prior_eval_all = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], prior_alpha)
        prior_sub_all = subject_prior(train.iloc[fold.train_idx], sample, prior_alpha)
        for target_i, target in enumerate(TARGET_COLUMNS):
            x_fit = meta_features(source_oof[:, fold.train_idx], target_i, train_panel[fold.train_idx], prior_fit_all[:, target_i])
            x_eval = meta_features(source_oof[:, fold.val_idx], target_i, train_panel[fold.val_idx], prior_eval_all[:, target_i])
            x_sub = meta_features(source_sub, target_i, sample_panel, prior_sub_all[:, target_i])
            scaler = StandardScaler()
            x_fit = scaler.fit_transform(x_fit)
            x_eval = scaler.transform(x_eval)
            x_sub = scaler.transform(x_sub)
            y_fit = train.iloc[fold.train_idx][target].to_numpy(int)
            if len(np.unique(y_fit)) < 2:
                pred_eval = np.full(len(fold.val_idx), float(y_fit[0]))
                pred_sub = np.full(len(sample), float(y_fit[0]))
            else:
                model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=2026)
                model.fit(x_fit, y_fit)
                pred_eval = model.predict_proba(x_eval)[:, 1]
                pred_sub = model.predict_proba(x_sub)[:, 1]
            oof[fold.val_idx, target_i] = pred_eval
            fold_sample[:, target_i] = pred_sub
        sample_folds.append(fold_sample)
    return np.clip(oof, EPS, 1 - EPS), np.clip(np.mean(sample_folds, axis=0), EPS, 1 - EPS)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    names, source_oof, source_sub = load_sources([Path(item) for item in args.input_dirs])

    score_df = source_score_table(train, names, source_oof)
    tw_oof, tw_sub, tw_select = targetwise_best(train, sample, names, source_oof, source_sub)
    tw_avg, tw_per = average_log_loss(train[TARGET_COLUMNS], tw_oof)

    rows = [{"source": "targetwise_best_source", "avg_log_loss": tw_avg, **tw_per}]
    predictions = {"targetwise_best_source": (tw_oof, tw_sub)}
    for c_value in args.c_values:
        moe_oof, moe_sub = train_nested_moe(train, sample, names, source_oof, source_sub, c_value, args.prior_alpha)
        avg, per = average_log_loss(train[TARGET_COLUMNS], moe_oof)
        name = f"nested_moe_logreg_c{c_value:g}".replace(".", "p")
        rows.append({"source": name, "avg_log_loss": avg, **per})
        predictions[name] = (moe_oof, moe_sub)

    result_df = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    best_name = str(result_df.iloc[0]["source"])
    best_oof, best_sub = predictions[best_name]
    drift = drift_vs_reference(sample, best_sub, Path(args.reference_submission) if args.reference_submission else None)

    score_df.to_csv(output_dir / "expert_source_scores.csv", index=False)
    result_df.to_csv(output_dir / "moe_scores.csv", index=False)
    tw_select.to_csv(output_dir / "targetwise_best_selection.csv", index=False)
    write_prediction(output_dir / "oof_transformer_moe_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_transformer_moe_best.csv", sample, best_sub, oof=False)

    report = {
        "best_source": best_name,
        "best_avg_log_loss": float(result_df.iloc[0]["avg_log_loss"]),
        "drift_vs_reference": drift,
        "n_experts": len(names),
        "scores": result_df.to_dict(orient="records"),
        "targetwise_selection": tw_select.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Transformer Expert MoE Head v1",
        "",
        "## Result",
        "",
        f"- Best source: `{best_name}`",
        f"- OOF avg logloss: `{float(result_df.iloc[0]['avg_log_loss']):.6f}`",
        f"- Drift vs v83 reference: `{drift.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Experts: `{len(names)}`",
        "",
        "## MoE Scores",
        "",
        dataframe_to_markdown(result_df),
        "",
        "## Full-OOF Targetwise Expert Diagnostic",
        "",
        dataframe_to_markdown(tw_select),
        "",
        "## Top Expert Sources",
        "",
        dataframe_to_markdown(score_df.head(12)),
        "",
        "The nested MoE head is intentionally small: it sees only Transformer expert logits, their dispersion, panel position, and a fold-safe subject prior. If this does not beat source selection, the bottleneck is token representation rather than head capacity.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a small nested MoE head over Transformer tokenization experts.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument(
        "--input-dirs",
        nargs="+",
        default=[
            "outputs/hourly_transformer_encoder_v1",
            "outputs/hourly_transformer_encoder_v1_extra",
            "outputs/multires10_transformer_encoder_v1",
            "outputs/multires30_transformer_encoder_v1",
        ],
    )
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/transformer_moe_head_v1")
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.01, 0.03, 0.10, 0.30])
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
