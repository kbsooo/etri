from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etri_diffusion.model import DayDenoisingDiffusionEncoder


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class ModelSpec:
    name: str
    feature_set: str
    c_value: float
    weight_mode: str


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def choose_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def diffusion_schedule(steps: int, device: torch.device) -> torch.Tensor:
    betas = torch.linspace(1e-4, 0.02, steps, device=device)
    alphas = 1.0 - betas
    return torch.cumprod(alphas, dim=0)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    base_submission = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return prediction_matrix(base_oof), submission_matrix(base_submission)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def load_hourly_tensor(input_dir: Path) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, dict]:
    arrays = np.load(input_dir / "hourly_tensor.npz")
    day_index = normalize_keys(pd.read_csv(input_dir / "day_index.csv"))
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
    return arrays["x"].astype(np.float32), arrays["mask"].astype(np.float32), day_index, metadata


def checkpoint_model(model_dir: Path, device: torch.device) -> tuple[DayDenoisingDiffusionEncoder, dict]:
    checkpoint_path = model_dir / "checkpoints" / "day_diffusion_encoder.pt"
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    cfg = checkpoint.get("args", {})
    shape = checkpoint["shape"]
    subject_mode = checkpoint.get("subject_mode") or cfg.get("subject_mode", "id")
    subject_map = checkpoint.get("subject_map", {})
    n_subjects = 1 if subject_mode == "zero" else max(1, len(subject_map))
    model = DayDenoisingDiffusionEncoder(
        channels=int(shape[-1]),
        n_subjects=n_subjects,
        d_model=int(cfg.get("d_model", 128)),
        latent_dim=int(cfg.get("latent_dim", 64)),
        n_layers=int(cfg.get("layers", 3)),
        n_heads=int(cfg.get("heads", 4)),
        dropout=float(cfg.get("dropout", 0.1)),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, checkpoint


def subject_index_for_checkpoint(day_index: pd.DataFrame, checkpoint: dict, device: torch.device) -> torch.Tensor:
    cfg = checkpoint.get("args", {})
    subject_mode = checkpoint.get("subject_mode") or cfg.get("subject_mode", "id")
    if subject_mode == "zero":
        values = np.zeros(len(day_index), dtype=np.int64)
    else:
        subject_map = checkpoint.get("subject_map", {})
        values = day_index["subject_id"].map(subject_map).fillna(0).to_numpy(dtype=np.int64)
    return torch.from_numpy(values).to(device)


def block_slices() -> dict[str, list[int]]:
    return {
        "all": list(range(24)),
        "sleep": [22, 23, 0, 1, 2, 3, 4, 5],
        "night": [0, 1, 2, 3, 4, 5],
        "morning": [6, 7, 8, 9, 10, 11],
        "afternoon": [12, 13, 14, 15, 16, 17],
        "evening": [18, 19, 20, 21, 22, 23],
    }


def channel_groups(metadata: dict) -> dict[str, np.ndarray]:
    modalities = metadata["channel_modalities"]
    groups: dict[str, list[int]] = {"all": [], "raw": [], "dev": []}
    for idx, modality in enumerate(modalities):
        groups["all"].append(idx)
        if modality.endswith("_dev"):
            groups["dev"].append(idx)
            base = modality[:-4]
        else:
            groups["raw"].append(idx)
            base = modality
        groups.setdefault(base, []).append(idx)
    return {name: np.asarray(indices, dtype=int) for name, indices in groups.items() if indices}


def summarize_error(
    error: np.ndarray,
    mask: np.ndarray,
    prefix: str,
    metadata: dict,
    timestep: int,
) -> dict[str, np.ndarray]:
    groups = channel_groups(metadata)
    blocks = block_slices()
    features: dict[str, np.ndarray] = {}
    for block_name, hours in blocks.items():
        hour_idx = np.asarray(hours, dtype=int)
        for group_name, channel_idx in groups.items():
            err_part = error[:, hour_idx][:, :, channel_idx]
            mask_part = mask[:, hour_idx][:, :, channel_idx]
            denom = mask_part.sum(axis=(1, 2))
            values = np.divide(err_part.sum(axis=(1, 2)), denom, out=np.full(error.shape[0], np.nan, dtype=float), where=denom > 0)
            features[f"dloss__{prefix}__t{timestep:03d}__{block_name}__{group_name}"] = values
    return features


def extract_diffusion_loss_features(args: argparse.Namespace, device: torch.device) -> pd.DataFrame:
    input_dir = Path(args.diffusion_input_dir)
    x_np, mask_np, day_index, metadata = load_hourly_tensor(input_dir)
    if Path(args.cached_feature_path).exists() and not args.recompute_features:
        return normalize_keys(pd.read_parquet(args.cached_feature_path))

    model_dirs = parse_str_list(args.diffusion_model_dirs)
    timesteps = [int(value) for value in parse_str_list(args.timesteps)]
    batch_size = int(args.batch_size)
    all_feature_columns: dict[str, np.ndarray] = {}
    x_cpu = torch.from_numpy(x_np)
    mask_cpu = torch.from_numpy(mask_np)

    for model_dir_value in model_dirs:
        model_dir = Path(model_dir_value)
        prefix = model_dir.name.replace("diffusion_encoder_", "").replace("diffusion_encoder", "base")
        print(f"[diffusion-loss] {model_dir}")
        model, checkpoint = checkpoint_model(model_dir, device)
        subject_idx_all = subject_index_for_checkpoint(day_index, checkpoint, device)
        steps = int(checkpoint.get("args", {}).get("diffusion_steps", 100))
        alpha_bars = diffusion_schedule(steps, device)
        for timestep in timesteps:
            t_value = max(0, min(timestep, steps - 1))
            rng = np.random.default_rng(args.seed + t_value * 1009 + len(prefix) * 17)
            noise_np = rng.standard_normal(size=x_np.shape).astype(np.float32)
            error_chunks = []
            with torch.no_grad():
                for start in range(0, len(x_np), batch_size):
                    end = min(start + batch_size, len(x_np))
                    xb = x_cpu[start:end].to(device)
                    mb = mask_cpu[start:end].to(device)
                    nb = torch.from_numpy(noise_np[start:end]).to(device)
                    alpha = alpha_bars[t_value].view(1, 1, 1)
                    x_t = torch.sqrt(alpha) * xb + torch.sqrt(1.0 - alpha) * nb
                    tb = torch.full((end - start,), t_value, dtype=torch.long, device=device)
                    pred, _ = model(x_t * mb, mb, subject_idx_all[start:end], tb)
                    err = ((pred - nb) ** 2 * mb).detach().cpu().numpy().astype(np.float32)
                    error_chunks.append(err)
            error = np.concatenate(error_chunks, axis=0)
            all_feature_columns.update(summarize_error(error, mask_np, prefix, metadata, t_value))

    feature_df = pd.concat(
        [
            day_index[KEY_COLUMNS + ["split", "weekday", "is_weekend", "day_index_subject"]].copy(),
            pd.DataFrame({name: values.astype(float) for name, values in all_feature_columns.items()}),
        ],
        axis=1,
    )
    Path(args.cached_feature_path).parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_parquet(args.cached_feature_path, index=False)
    return normalize_keys(feature_df)


def add_training_features(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    feature_df: pd.DataFrame,
    base_oof: np.ndarray,
    base_submission: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_x = train.merge(feature_df, on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_x = sample[KEY_COLUMNS].merge(feature_df, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_x["split"].isna().any() or test_x["split"].isna().any():
        raise ValueError("Some rows failed to join diffusion-loss features")

    all_df = pd.concat(
        [
            train_x.assign(_split="train", _row=np.arange(len(train_x))),
            test_x.assign(_split="test", _row=np.arange(len(test_x))),
        ],
        ignore_index=True,
    )
    pred_all = np.vstack([base_oof, base_submission])
    for target_i, target in enumerate(TARGET_COLUMNS):
        pred = np.clip(pred_all[:, target_i], EPS, 1.0 - EPS)
        all_df[f"base_pred_{target}"] = pred
        all_df[f"base_logit_{target}"] = safe_logit(pred)

    all_df["lifelog_dt"] = pd.to_datetime(all_df["lifelog_date"])
    all_df = all_df.sort_values(["subject_id", "lifelog_dt", "sleep_date"]).copy()
    all_df["panel_index"] = all_df.groupby("subject_id").cumcount().astype(float)
    denom = all_df.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    all_df["panel_position"] = all_df["panel_index"] / denom
    all_df = all_df.sort_values(["_split", "_row"]).reset_index(drop=True)

    dloss_cols = sorted(col for col in all_df.columns if col.startswith("dloss__"))
    grouped = all_df.groupby("subject_id", sort=False)
    derived_blocks = []
    for col in dloss_cols:
        values = pd.to_numeric(all_df[col], errors="coerce")
        derived_blocks.append(
            pd.DataFrame(
                {
                    f"dloss_center__{col}": values - grouped[col].transform("mean"),
                    f"dloss_rank__{col}": grouped[col].rank(method="average", pct=True),
                },
                index=all_df.index,
            )
        )
    if derived_blocks:
        all_df = pd.concat([all_df, *derived_blocks], axis=1).copy()

    base_cols = [f"base_logit_{target}" for target in TARGET_COLUMNS] + [f"base_pred_{target}" for target in TARGET_COLUMNS]
    time_cols = ["weekday", "is_weekend", "day_index_subject", "panel_index", "panel_position"]
    time_cols = [col for col in time_cols if col in all_df.columns]
    rank_cols = sorted(col for col in all_df.columns if col.startswith(("dloss_center__", "dloss_rank__")))

    def cols_with_tokens(tokens: list[str], source_cols: list[str]) -> list[str]:
        return sorted(col for col in source_cols if any(token in col for token in tokens))

    sleep_tokens = ["__sleep__", "__night__", "__evening__", "__mActivity", "__mScreenStatus", "__wHr", "__wPedo", "__mGps", "__raw", "__dev", "__all"]
    q_tokens = ["__all__", "__morning__", "__afternoon__", "__evening__", "__mActivity", "__mUsageStats", "__mGps", "__mWifi", "__mBle", "__raw", "__dev"]
    compact_tokens = ["__all__", "__sleep__", "__night__", "__evening__", "__raw", "__dev", "__all"]

    feature_sets = {
        "dloss_compact": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(compact_tokens, dloss_cols))),
        "dloss_sleep": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(sleep_tokens, dloss_cols))),
        "dloss_q": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(q_tokens, dloss_cols))),
        "dloss_rank_compact": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(compact_tokens, dloss_cols + rank_cols))),
        "dloss_rank_sleep": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(sleep_tokens, dloss_cols + rank_cols))),
        "dloss_rank_q": sorted(dict.fromkeys(base_cols + time_cols + cols_with_tokens(q_tokens, dloss_cols + rank_cols))),
    }

    train_out = all_df[all_df["_split"].eq("train")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"].eq("test")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out, feature_sets


def sample_weights(frame: pd.DataFrame, mode: str) -> np.ndarray:
    if mode == "uniform":
        return np.ones(len(frame), dtype=float)
    position = pd.to_numeric(frame["panel_position"], errors="coerce").fillna(0.5).to_numpy(dtype=float)
    if mode == "tail2":
        return 1.0 + 2.0 * position
    if mode == "tail4":
        return 1.0 + 4.0 * position
    if mode == "tail_step":
        return np.where(position >= 0.66, 4.0, np.where(position >= 0.33, 2.0, 1.0))
    raise ValueError(f"Unknown weight mode: {mode}")


def make_model(c_value: float, numeric_cols: list[str]) -> Pipeline:
    return Pipeline(
        [
            (
                "pre",
                ColumnTransformer(
                    [
                        ("num", Pipeline([("impute", SimpleImputer(strategy="median", keep_empty_features=True)), ("scale", StandardScaler())]), numeric_cols),
                        ("cat", OneHotEncoder(handle_unknown="ignore"), ["subject_id"]),
                    ]
                ),
            ),
            ("model", LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000)),
        ]
    )


def fit_predict(
    train_x: pd.DataFrame,
    train_y: np.ndarray,
    eval_x: pd.DataFrame,
    feature_cols: list[str],
    c_value: float,
    weight_mode: str,
) -> np.ndarray:
    classes = np.unique(train_y)
    if len(classes) < 2:
        return np.full(len(eval_x), float(classes[0]), dtype=float)
    model = make_model(c_value, feature_cols)
    weights = sample_weights(train_x, weight_mode)
    model.fit(train_x[feature_cols + ["subject_id"]], train_y, model__sample_weight=weights)
    return np.clip(model.predict_proba(eval_x[feature_cols + ["subject_id"]])[:, 1], EPS, 1.0 - EPS)


def evaluate_decoder(args: argparse.Namespace, train_x: pd.DataFrame, test_x: pd.DataFrame, feature_sets: dict[str, list[str]], base_oof: np.ndarray, base_submission: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    y = train_x[TARGET_COLUMNS]
    folds = make_subject_time_folds(train_x, args.folds)
    base_avg, base_targets = average_loss(y, base_oof)
    target_arg = parse_str_list(args.targets)
    eval_targets = TARGET_COLUMNS if target_arg == ["all"] else target_arg
    unknown_targets = sorted(set(eval_targets) - set(TARGET_COLUMNS))
    if unknown_targets:
        raise ValueError(f"Unknown targets: {unknown_targets}")
    blend_weights = parse_float_list(args.blend_weights)
    blend_modes = parse_str_list(args.blend_modes)
    specs = [
        ModelSpec(f"{feature_set}_C{c_value:g}_{weight_mode}", feature_set, c_value, weight_mode)
        for feature_set in parse_str_list(args.feature_sets)
        for c_value in parse_float_list(args.logreg_cs)
        for weight_mode in parse_str_list(args.weight_modes)
    ]

    candidate_rows = []
    pred_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    best_by_target: dict[str, dict] = {}

    for spec_i, spec in enumerate(specs, start=1):
        if spec.feature_set not in feature_sets:
            raise ValueError(f"Unknown feature set: {spec.feature_set}")
        feature_cols = feature_sets[spec.feature_set]
        print(f"[{spec_i}/{len(specs)}] {spec.name} n_features={len(feature_cols)}")
        model_oof = base_oof.copy()
        model_test = base_submission.copy()
        for target in eval_targets:
            target_i = TARGET_COLUMNS.index(target)
            target_oof = np.zeros(len(train_x), dtype=float)
            for train_idx, val_idx in folds:
                target_oof[val_idx] = fit_predict(
                    train_x.iloc[train_idx],
                    y.iloc[train_idx][target].to_numpy(dtype=int),
                    train_x.iloc[val_idx],
                    feature_cols,
                    spec.c_value,
                    spec.weight_mode,
                )
            model_oof[:, target_i] = target_oof
            model_test[:, target_i] = fit_predict(
                train_x,
                y[target].to_numpy(dtype=int),
                test_x,
                feature_cols,
                spec.c_value,
                spec.weight_mode,
            )

        pred_cache[spec.name] = (model_oof, model_test)
        for blend_mode in blend_modes:
            for weight in blend_weights:
                if blend_mode == "prob":
                    blended = np.clip(weight * model_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
                elif blend_mode == "logit":
                    blended = sigmoid(weight * safe_logit(model_oof) + (1.0 - weight) * safe_logit(base_oof))
                else:
                    raise ValueError(f"Unknown blend mode: {blend_mode}")
                avg, per_target = average_loss(y, blended)
                row = {
                    "name": f"{spec.name}_{blend_mode}_w{weight:g}",
                    "model_name": spec.name,
                    "feature_set": spec.feature_set,
                    "c_value": spec.c_value,
                    "weight_mode": spec.weight_mode,
                    "blend_mode": blend_mode,
                    "blend_weight": weight,
                    "avg_log_loss": avg,
                    "delta_vs_base": base_avg - avg,
                    **per_target,
                }
                candidate_rows.append(row)
                for target_i, target in enumerate(TARGET_COLUMNS):
                    value = per_target[target]
                    current = best_by_target.get(target)
                    if current is None or value < current["log_loss"]:
                        fold_improvements = 0
                        fold_deltas = []
                        for _, val_idx in folds:
                            base_fold = target_loss(y, base_oof, target_i, val_idx)
                            cand_fold = target_loss(y, blended, target_i, val_idx)
                            delta = base_fold - cand_fold
                            fold_deltas.append(delta)
                            fold_improvements += int(delta > 0)
                        best_by_target[target] = {
                            "target": target,
                            "candidate": row["name"],
                            "model_name": spec.name,
                            "feature_set": spec.feature_set,
                            "c_value": spec.c_value,
                            "weight_mode": spec.weight_mode,
                            "blend_mode": blend_mode,
                            "blend_weight": weight,
                            "log_loss": value,
                            "base_log_loss": base_targets[target],
                            "delta_vs_base": base_targets[target] - value,
                            "folds_improved": fold_improvements,
                            "worst_fold_delta": float(np.min(fold_deltas)),
                        }

    final_oof = base_oof.copy()
    final_submission = base_submission.copy()
    selected_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        if target not in best_by_target:
            selected_rows.append(
                {
                    "target": target,
                    "candidate": "base",
                    "model_name": "base",
                    "feature_set": "base",
                    "c_value": np.nan,
                    "weight_mode": "base",
                    "blend_mode": "base",
                    "blend_weight": 0.0,
                    "log_loss": base_targets[target],
                    "base_log_loss": base_targets[target],
                    "delta_vs_base": 0.0,
                    "folds_improved": 0,
                    "worst_fold_delta": 0.0,
                    "used": False,
                }
            )
            continue
        selected = best_by_target[target]
        model_oof, model_test = pred_cache[selected["model_name"]]
        weight = float(selected["blend_weight"])
        if selected["blend_mode"] == "prob":
            cand_oof_target = np.clip(weight * model_oof[:, target_i] + (1.0 - weight) * base_oof[:, target_i], EPS, 1.0 - EPS)
            cand_test_target = np.clip(weight * model_test[:, target_i] + (1.0 - weight) * base_submission[:, target_i], EPS, 1.0 - EPS)
        else:
            cand_oof_target = sigmoid(weight * safe_logit(model_oof[:, target_i]) + (1.0 - weight) * safe_logit(base_oof[:, target_i]))
            cand_test_target = sigmoid(weight * safe_logit(model_test[:, target_i]) + (1.0 - weight) * safe_logit(base_submission[:, target_i]))
        use_candidate = bool(selected["delta_vs_base"] > args.min_target_delta and selected["folds_improved"] >= args.min_target_folds_improved)
        if use_candidate:
            final_oof[:, target_i] = cand_oof_target
            final_submission[:, target_i] = cand_test_target
        selected_rows.append({**selected, "used": use_candidate})

    candidate_scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selected_rows)
    return candidate_scores, selection, final_oof, final_submission


def write_outputs(
    args: argparse.Namespace,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    selection: pd.DataFrame,
    final_oof: np.ndarray,
    final_submission: np.ndarray,
    base_oof: np.ndarray,
) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    y = train[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    final_avg, final_targets = average_loss(y, final_oof)

    candidate_scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_diffusion_loss_residual_decoder.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_diffusion_loss_residual_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection.to_dict(orient="records"),
        "top_candidates": candidate_scores.head(30).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "diffusion_loss_residual_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Diffusion Loss Residual Decoder",
        "",
        f"- Base CV: `{base_avg:.6f}`",
        f"- Final CV: `{final_avg:.6f}`",
        f"- Selected targets: `{','.join(selection.loc[selection['used'], 'target'].tolist())}`",
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(candidate_scores.head(20)[["name", "avg_log_loss", "delta_vs_base", *TARGET_COLUMNS]]),
        "",
    ]
    (output_dir / "diffusion_loss_residual_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(f"saved report: {output_dir / 'diffusion_loss_residual_report.md'}")
    print(f"saved oof: {oof_path}")
    print(f"saved submission: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train residual decoders on diffusion denoising-loss day features.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/multi_signal_qcount_blend_w015_020_015_015/oof_multi_signal_qcount_blend.csv")
    parser.add_argument("--base-submission", default="outputs/multi_signal_qcount_blend_w015_020_015_015/submission_multi_signal_qcount_blend.csv")
    parser.add_argument("--diffusion-input-dir", default="outputs/diffusion_encoder")
    parser.add_argument("--diffusion-model-dirs", default="outputs/diffusion_encoder_id_long,outputs/diffusion_encoder_subjectless_long")
    parser.add_argument("--cached-feature-path", default="outputs/diffusion_loss_features/diffusion_loss_features.parquet")
    parser.add_argument("--recompute-features", action="store_true")
    parser.add_argument("--timesteps", default="10,30,60,90")
    parser.add_argument("--feature-sets", default="dloss_compact,dloss_sleep,dloss_q,dloss_rank_compact,dloss_rank_sleep,dloss_rank_q")
    parser.add_argument("--targets", default="all")
    parser.add_argument("--logreg-cs", default="0.003,0.006,0.01,0.02,0.05")
    parser.add_argument("--weight-modes", default="uniform,tail2,tail4,tail_step")
    parser.add_argument("--blend-weights", default="0.02,0.03,0.05,0.08,0.1,0.15,0.2,0.3,0.5,1.0")
    parser.add_argument("--blend-modes", default="prob,logit")
    parser.add_argument("--min-target-folds-improved", type=int, default=3)
    parser.add_argument("--min-target-delta", type=float, default=0.0)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output-dir", default="outputs/diffusion_loss_residual_on_multi_signal_min3")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    device = choose_device(args.device)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof, base_submission = load_base_predictions(args, train, sample)
    feature_df = extract_diffusion_loss_features(args, device)
    train_x, test_x, feature_sets = add_training_features(train, sample, feature_df, base_oof, base_submission)
    candidate_scores, selection, final_oof, final_submission = evaluate_decoder(args, train_x, test_x, feature_sets, base_oof, base_submission)
    write_outputs(args, train, sample, candidate_scores, selection, final_oof, final_submission, base_oof)


if __name__ == "__main__":
    main()
