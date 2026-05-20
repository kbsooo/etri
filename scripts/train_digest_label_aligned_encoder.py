from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))

from train_s2_sleep_retrieval_encoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    make_subject_time_folds,
    merge_feature_tables,
    normalize_keys,
    safe_logit,
    select_group_columns,
    sigmoid,
)


@dataclass(frozen=True)
class EncoderSpec:
    name: str
    encoder: str
    target_mode: str
    components: int
    alpha: float
    scale: float
    max_delta: float


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(part) for part in value.split(",") if part.strip()]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def average_log_loss(train: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: float(log_loss(train[target].to_numpy(int), np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def make_specs(args: argparse.Namespace) -> list[EncoderSpec]:
    specs = []
    for encoder in [part.strip() for part in args.encoders.split(",") if part.strip()]:
        for mode in [part.strip() for part in args.target_modes.split(",") if part.strip()]:
            for components in parse_int_list(args.components):
                for alpha in parse_float_list(args.alphas):
                    for scale in parse_float_list(args.scales):
                        for max_delta in parse_float_list(args.max_deltas):
                            name = f"{encoder}_{mode}_c{components}_a{alpha:g}_s{scale:g}_d{max_delta:g}"
                            specs.append(EncoderSpec(name, encoder, mode, components, alpha, scale, max_delta))
    return specs


def residual_target(y: np.ndarray, anchor: np.ndarray, mode: str) -> np.ndarray:
    if mode == "logit_soft":
        smooth = 0.10 + 0.80 * y.astype(float)
        return safe_logit(smooth) - safe_logit(anchor)
    if mode == "logit_hard":
        smooth = 0.04 + 0.92 * y.astype(float)
        return safe_logit(smooth) - safe_logit(anchor)
    if mode == "prob":
        return y.astype(float) - anchor
    raise ValueError(f"Unknown target mode: {mode}")


def preprocess_fit(x: np.ndarray, min_std: float) -> tuple[SimpleImputer, StandardScaler, np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_imp = imputer.fit_transform(x)
    x_scaled = scaler.fit_transform(x_imp)
    std = np.nanstd(x_scaled, axis=0)
    keep = np.where(std > min_std)[0]
    if keep.size == 0:
        raise ValueError("No non-constant features after preprocessing")
    out = np.nan_to_num(x_scaled[:, keep], nan=0.0, posinf=0.0, neginf=0.0)
    return imputer, scaler, keep, np.clip(out, -8.0, 8.0).astype(np.float32)


def preprocess_apply(x: np.ndarray, imputer: SimpleImputer, scaler: StandardScaler, keep: np.ndarray) -> np.ndarray:
    out = scaler.transform(imputer.transform(x))[:, keep]
    out = np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(out, -8.0, 8.0).astype(np.float32)


def fit_latent_encoder(
    x_fit: np.ndarray,
    target_fit: np.ndarray,
    x_eval: np.ndarray,
    spec: EncoderSpec,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_components = min(spec.components, x_fit.shape[0] - 1, x_fit.shape[1])
    if spec.encoder == "none" or n_components <= 0:
        return x_fit, x_eval
    if spec.encoder == "pls":
        encoder = PLSRegression(n_components=n_components, scale=False, max_iter=1000)
        encoder.fit(x_fit, target_fit)
        return encoder.transform(x_fit).astype(np.float32), encoder.transform(x_eval).astype(np.float32)
    if spec.encoder == "pca":
        encoder = PCA(n_components=n_components, random_state=seed, svd_solver="full")
        encoder.fit(x_fit)
        return encoder.transform(x_fit).astype(np.float32), encoder.transform(x_eval).astype(np.float32)
    if spec.encoder == "plspca":
        pls_components = max(1, n_components // 2)
        pca_components = max(1, n_components - pls_components)
        pls = PLSRegression(n_components=min(pls_components, x_fit.shape[0] - 1, x_fit.shape[1]), scale=False, max_iter=1000)
        pca = PCA(n_components=min(pca_components, x_fit.shape[0] - 1, x_fit.shape[1]), random_state=seed, svd_solver="full")
        pls.fit(x_fit, target_fit)
        pca.fit(x_fit)
        fit_z = np.concatenate([pls.transform(x_fit), pca.transform(x_fit)], axis=1)
        eval_z = np.concatenate([pls.transform(x_eval), pca.transform(x_eval)], axis=1)
        return fit_z.astype(np.float32), eval_z.astype(np.float32)
    raise ValueError(f"Unknown encoder: {spec.encoder}")


def fit_predict(
    x_fit_raw: np.ndarray,
    x_eval_raw: np.ndarray,
    y_fit: np.ndarray,
    anchor_fit: np.ndarray,
    anchor_eval: np.ndarray,
    spec: EncoderSpec,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    target = residual_target(y_fit, anchor_fit, spec.target_mode)
    z_fit, z_eval = fit_latent_encoder(x_fit_raw, target, x_eval_raw, spec, seed)
    model = Ridge(alpha=spec.alpha, solver="svd")
    model.fit(z_fit, target)
    delta = np.clip(model.predict(z_eval), -spec.max_delta, spec.max_delta)
    if spec.target_mode == "prob":
        pred = np.clip(anchor_eval + spec.scale * delta, EPS, 1.0 - EPS)
    else:
        pred = sigmoid(safe_logit(anchor_eval) + spec.scale * delta)
    return pred, z_fit, z_eval


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    lines = [
        "| " + " | ".join(display.columns) + " |",
        "| " + " | ".join(["---"] * len(display.columns)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy())
    return "\n".join(lines)


def build_feature_matrix(train: pd.DataFrame, sample: pd.DataFrame, groups: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_x, sample_x = merge_feature_tables(train, sample)
    all_cols = train_x.columns.tolist()
    selected: list[str] = []
    for group in [part.strip() for part in groups.split(",") if part.strip()]:
        selected.extend(select_group_columns(all_cols, group))
    selected = sorted(dict.fromkeys(selected))
    if not selected:
        raise ValueError("No digest feature columns selected")
    return train_x[selected], sample_x[selected], selected


def train_encoder_sources(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    anchor_oof_frame = normalize_keys(pd.read_csv(args.anchor_oof))
    anchor_sub_frame = normalize_keys(pd.read_csv(args.anchor_submission))
    if not anchor_oof_frame[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Anchor OOF keys do not match train")
    if not anchor_sub_frame[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Anchor submission keys do not match sample")
    anchor_oof = prediction_matrix(anchor_oof_frame)
    anchor_sub = submission_matrix(anchor_sub_frame)
    train_x, sample_x, feature_cols = build_feature_matrix(train, sample, args.groups)
    x_train_all = train_x.replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    x_sample_all = sample_x.replace([np.inf, -np.inf], np.nan).to_numpy(np.float32)
    y = train[TARGET_COLUMNS].to_numpy(float)
    folds = make_subject_time_folds(train, args.folds)
    specs = make_specs(args)
    oof_by_spec = {spec.name: anchor_oof.copy() for spec in specs}

    fold_rows = []
    for fold_id, fold in enumerate(folds, start=1):
        imputer, scaler, keep, x_fit = preprocess_fit(x_train_all[fold.train_idx], args.min_feature_std)
        x_val = preprocess_apply(x_train_all[fold.val_idx], imputer, scaler, keep)
        for spec in specs:
            pred, _, _ = fit_predict(
                x_fit,
                x_val,
                y[fold.train_idx],
                anchor_oof[fold.train_idx],
                anchor_oof[fold.val_idx],
                spec,
                args.seed + fold_id,
            )
            oof_by_spec[spec.name][fold.val_idx] = pred
        fold_rows.append({"fold": fold_id, "train_rows": int(len(fold.train_idx)), "valid_rows": int(len(fold.val_idx)), "kept_features": int(len(keep))})
        print(f"fold={fold_id} complete kept_features={len(keep)}")

    rows = []
    anchor_score, anchor_per = average_log_loss(train, anchor_oof)
    rows.append({"name": "anchor_noop", "avg_log_loss": anchor_score, **anchor_per})
    for spec in specs:
        score, per = average_log_loss(train, oof_by_spec[spec.name])
        rows.append(
            {
                "name": spec.name,
                "encoder": spec.encoder,
                "target_mode": spec.target_mode,
                "components": spec.components,
                "alpha": spec.alpha,
                "scale": spec.scale,
                "max_delta": spec.max_delta,
                "avg_log_loss": score,
                **per,
            }
        )
    scores = pd.DataFrame(rows).sort_values("avg_log_loss", ascending=True).reset_index(drop=True)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)

    imputer, scaler, keep, x_fit_full = preprocess_fit(x_train_all, args.min_feature_std)
    x_sample = preprocess_apply(x_sample_all, imputer, scaler, keep)
    spec_by_name = {spec.name: spec for spec in specs}
    targetwise_names = [str(scores.sort_values(target).iloc[0]["name"]) for target in TARGET_COLUMNS]
    export_names = list(dict.fromkeys([*scores.head(args.full_fit_top_k)["name"].astype(str).tolist(), *targetwise_names]))
    exported: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for rank, name in enumerate(export_names):
        if name == "anchor_noop":
            pred_sub = anchor_sub.copy()
            oof_pred = anchor_oof.copy()
        else:
            spec = spec_by_name[name]
            pred_sub, _, _ = fit_predict(x_fit_full, x_sample, y, anchor_oof, anchor_sub, spec, args.seed)
            oof_pred = oof_by_spec[name]
        safe = name.replace(".", "p").replace("-", "m")
        oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
        sub = sample[KEY_COLUMNS].copy()
        for i, target in enumerate(TARGET_COLUMNS):
            oof[f"pred_{target}"] = oof_pred[:, i]
            sub[target] = pred_sub[:, i]
        oof.to_csv(output_dir / f"oof_rank{rank + 1:02d}_{safe}.csv", index=False)
        sub.to_csv(output_dir / f"submission_rank{rank + 1:02d}_{safe}.csv", index=False)
        exported[name] = (oof_pred, pred_sub)

    targetwise_oof = anchor_oof.copy()
    targetwise_sub = anchor_sub.copy()
    targetwise_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        row = scores.sort_values(target).iloc[0].to_dict()
        name = str(row["name"])
        oof_pred, sub_pred = exported[name]
        targetwise_oof[:, target_i] = oof_pred[:, target_i]
        targetwise_sub[:, target_i] = sub_pred[:, target_i]
        targetwise_rows.append({"target": target, **row})
    targetwise_score, targetwise_per = average_log_loss(train, targetwise_oof)
    targetwise_oof_frame = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    targetwise_sub_frame = sample[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        targetwise_oof_frame[f"pred_{target}"] = targetwise_oof[:, i]
        targetwise_sub_frame[target] = targetwise_sub[:, i]
    targetwise_oof_frame.to_csv(output_dir / "oof_targetwise_digest_label_aligned_encoder.csv", index=False)
    targetwise_sub_frame.to_csv(output_dir / "submission_targetwise_digest_label_aligned_encoder.csv", index=False)
    pd.DataFrame(targetwise_rows).to_csv(output_dir / "targetwise_selection.csv", index=False)

    report = {
        "best": scores.iloc[0].to_dict(),
        "anchor_score": {"avg_log_loss": anchor_score, **anchor_per},
        "targetwise_score": {"avg_log_loss": targetwise_score, **targetwise_per},
        "targetwise_selection": targetwise_rows,
        "feature_count": len(feature_cols),
        "folds": fold_rows,
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Digest label-aligned encoder",
        "",
        f"- Anchor OOF: `{anchor_score:.6f}`",
        f"- Best OOF: `{scores.iloc[0]['avg_log_loss']:.6f}`",
        f"- Target-wise OOF: `{targetwise_score:.6f}`",
        f"- feature count: `{len(feature_cols)}`",
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(scores.head(12)[["name", "avg_log_loss", *TARGET_COLUMNS]]),
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(pd.DataFrame(targetwise_rows)[["target", "name", "avg_log_loss", *TARGET_COLUMNS]]),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"best={scores.iloc[0]['name']} avg_log_loss={scores.iloc[0]['avg_log_loss']:.6f}")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a shared digest encoder-decoder for label-aligned residual prediction.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--anchor-oof", default="outputs/conditional_latent_routing_v25_joint_all_digest/oof_conditional_latent_routing.csv")
    parser.add_argument("--anchor-submission", default="outputs/conditional_latent_routing_v25_joint_all_digest/submission_conditional_latent_routing.csv")
    parser.add_argument("--output-dir", default="outputs/digest_label_aligned_encoder_v1")
    parser.add_argument("--groups", default="phone_recovery,social_rhythm,body_recovery,modality_desync")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--encoders", default="pls,pca,plspca")
    parser.add_argument("--target-modes", default="logit_soft,prob")
    parser.add_argument("--components", default="4,8,16,32")
    parser.add_argument("--alphas", default="10,30,100,300")
    parser.add_argument("--scales", default="0.025,0.05,0.075,0.1,0.15,0.2")
    parser.add_argument("--max-deltas", default="0.1,0.2,0.35")
    parser.add_argument("--min-feature-std", type=float, default=1e-6)
    parser.add_argument("--full-fit-top-k", type=int, default=12)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    train_encoder_sources(parse_args())


if __name__ == "__main__":
    main()
