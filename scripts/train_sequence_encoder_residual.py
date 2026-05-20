from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class SequenceSpec:
    name: str
    encoder: str
    context_days: int
    d_model: int
    dropout: float
    max_delta: float
    lr: float
    weight_decay: float
    residual_penalty: float
    max_epochs: int
    patience: int


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype(str)
    return out


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    try:
        torch.use_deterministic_algorithms(False)
    except Exception:
        pass


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def avg_log_loss(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_pred = np.clip(y_pred, EPS, 1.0 - EPS)
    y_true = y_true.astype(float)
    loss = -(y_true * np.log(y_pred) + (1.0 - y_true) * np.log(1.0 - y_pred))
    return float(loss.mean())


def parse_target_weights(raw: str, default: float = 1.0) -> np.ndarray:
    if not raw:
        return np.ones(len(TARGET_COLUMNS), dtype=np.float32)
    weights = np.full(len(TARGET_COLUMNS), float(default), dtype=np.float32)
    for item in raw.split(","):
        if not item.strip():
            continue
        target, value = item.split(":", 1)
        target = target.strip()
        if target not in TARGET_COLUMNS:
            raise ValueError(f"Unknown target in --target-weights: {target}")
        weights[TARGET_COLUMNS.index(target)] = float(value)
    weights = weights / max(float(weights.mean()), 1e-8)
    return weights.astype(np.float32)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    train_pos = ordered[ordered["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = ordered[ordered["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = sample_pos
    return train_out, sample_out, ordered.reset_index(drop=True)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=int)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def inner_time_split(train_frame: pd.DataFrame, outer_train_idx: np.ndarray, validation_fraction: float) -> tuple[np.ndarray, np.ndarray]:
    ordered = train_frame.iloc[outer_train_idx].reset_index(names="_orig").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    inner_val: list[int] = []
    for _, group in ordered.groupby("subject_id", sort=False):
        n_val = max(1, int(math.ceil(len(group) * validation_fraction)))
        inner_val.extend(group.tail(n_val)["_orig"].tolist())
    inner_val_idx = np.array(sorted(inner_val), dtype=int)
    inner_train_idx = np.setdiff1d(outer_train_idx, inner_val_idx, assume_unique=False)
    if len(inner_train_idx) == 0:
        return outer_train_idx, inner_val_idx
    return inner_train_idx, inner_val_idx


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(args.base_oof))
    submission = normalize_keys(pd.read_csv(args.base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return np.clip(prediction_matrix(oof), EPS, 1.0 - EPS), np.clip(submission_matrix(submission), EPS, 1.0 - EPS)


def panel_table(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    panel = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    panel = normalize_keys(panel)
    panel["_date"] = pd.to_datetime(panel["lifelog_date"])
    panel = panel.sort_values(["subject_id", "_date", "sleep_date"]).reset_index(drop=True)
    panel["panel_row"] = np.arange(len(panel), dtype=int)
    return panel


def compressed_daily_features(master_path: str, panel: pd.DataFrame, n_components: int) -> np.ndarray:
    master = normalize_keys(pd.read_parquet(master_path))
    numeric_cols = [
        col
        for col in master.select_dtypes(include=[np.number]).columns
        if col not in TARGET_COLUMNS and not col.startswith("pred_")
    ]
    merged = panel[KEY_COLUMNS].merge(master[KEY_COLUMNS + numeric_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if merged[numeric_cols].isna().all(axis=1).any():
        raise ValueError("Some panel rows failed to align with master daily features")
    raw = merged[numeric_cols].replace([np.inf, -np.inf], np.nan)
    arr = raw.to_numpy(dtype=float)
    low = np.nanpercentile(arr, 1.0, axis=0)
    high = np.nanpercentile(arr, 99.0, axis=0)
    arr = np.clip(arr, low, high)
    n_comp = min(n_components, arr.shape[1], max(1, arr.shape[0] - 1))
    med = np.nanmedian(arr, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    missing = ~np.isfinite(arr)
    if missing.any():
        arr = arr.copy()
        arr[missing] = np.take(med, np.where(missing)[1])
    mean = arr.mean(axis=0)
    std = arr.std(axis=0)
    std = np.where(std > 1e-8, std, 1.0)
    z = (arr - mean) / std
    _, _, vt = np.linalg.svd(z, full_matrices=False)
    return (z @ vt[:n_comp].T).astype(np.float32)


def make_sequences(panel: pd.DataFrame, daily_features: np.ndarray, context_days: int) -> tuple[np.ndarray, np.ndarray]:
    seq_len = context_days + 1
    n_rows, n_features = daily_features.shape
    out = np.zeros((n_rows, seq_len, n_features + 3), dtype=np.float32)
    valid = np.zeros((n_rows, seq_len), dtype=np.float32)
    index_by_subject: dict[str, list[int]] = {}
    for idx, subject in enumerate(panel["subject_id"].astype(str)):
        index_by_subject.setdefault(subject, []).append(idx)
    for subject_indices in index_by_subject.values():
        for local_pos, panel_idx in enumerate(subject_indices):
            start = max(0, local_pos - context_days)
            history = subject_indices[start : local_pos + 1]
            offset = seq_len - len(history)
            for step_pos, hist_idx in enumerate(history):
                dst = offset + step_pos
                out[panel_idx, dst, :n_features] = daily_features[hist_idx]
                age = len(history) - 1 - step_pos
                out[panel_idx, dst, n_features] = -float(age) / max(context_days, 1)
                out[panel_idx, dst, n_features + 1] = 1.0 if hist_idx == panel_idx else 0.0
                out[panel_idx, dst, n_features + 2] = 1.0
                valid[panel_idx, dst] = 1.0
    return out, valid


class SequenceResidualNet(nn.Module):
    def __init__(self, input_dim: int, spec: SequenceSpec):
        super().__init__()
        self.spec = spec
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, spec.d_model),
            nn.LayerNorm(spec.d_model),
            nn.GELU(),
            nn.Dropout(spec.dropout),
        )
        if spec.encoder == "gru":
            self.encoder = nn.GRU(spec.d_model, spec.d_model, batch_first=True)
            self.kind = "gru"
        elif spec.encoder == "transformer":
            layer = nn.TransformerEncoderLayer(
                d_model=spec.d_model,
                nhead=4,
                dim_feedforward=spec.d_model * 2,
                dropout=spec.dropout,
                batch_first=True,
                activation="gelu",
                norm_first=True,
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=1)
            self.kind = "transformer"
        else:
            raise ValueError(f"Unknown encoder: {spec.encoder}")
        self.head = nn.Sequential(
            nn.LayerNorm(spec.d_model),
            nn.Dropout(spec.dropout),
            nn.Linear(spec.d_model, len(TARGET_COLUMNS)),
        )
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, seq: torch.Tensor, valid: torch.Tensor, base_logits: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = self.input_proj(seq)
        if self.kind == "gru":
            encoded, _ = self.encoder(x)
        else:
            encoded = self.encoder(x, src_key_padding_mask=valid < 0.5)
        lengths = torch.clamp(valid.sum(dim=1).long() - 1, min=0)
        batch_idx = torch.arange(encoded.shape[0], device=encoded.device)
        pooled = encoded[batch_idx, lengths]
        raw_delta = self.head(pooled)
        delta = self.spec.max_delta * torch.tanh(raw_delta)
        return base_logits + delta, delta


def torch_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def train_fixed_epochs(
    spec: SequenceSpec,
    seq: np.ndarray,
    valid: np.ndarray,
    base_logits: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    epochs: int,
    device: torch.device,
    seed: int,
    batch_size: int,
    target_weights: np.ndarray,
) -> SequenceResidualNet:
    set_seed(seed)
    model = SequenceResidualNet(seq.shape[-1], spec).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=spec.lr, weight_decay=spec.weight_decay)
    target_weight_tensor = torch.tensor(target_weights, dtype=torch.float32, device=device)
    dataset = TensorDataset(
        torch.tensor(seq[train_idx], dtype=torch.float32),
        torch.tensor(valid[train_idx], dtype=torch.float32),
        torch.tensor(base_logits[train_idx], dtype=torch.float32),
        torch.tensor(y[train_idx], dtype=torch.float32),
    )
    generator = torch.Generator()
    generator.manual_seed(seed)
    loader = DataLoader(dataset, batch_size=min(batch_size, len(dataset)), shuffle=True, generator=generator)
    model.train()
    for _ in range(max(1, epochs)):
        for batch_seq, batch_valid, batch_base, batch_y in loader:
            batch_seq = batch_seq.to(device)
            batch_valid = batch_valid.to(device)
            batch_base = batch_base.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, delta = model(batch_seq, batch_valid, batch_base)
            bce = nn.functional.binary_cross_entropy_with_logits(logits, batch_y, reduction="none")
            loss = torch.mean(bce * target_weight_tensor) + spec.residual_penalty * torch.mean(delta * delta)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
    return model


@torch.no_grad()
def predict_model(
    model: SequenceResidualNet,
    seq: np.ndarray,
    valid: np.ndarray,
    base_logits: np.ndarray,
    idx: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    preds: list[np.ndarray] = []
    deltas: list[np.ndarray] = []
    for start in range(0, len(idx), batch_size):
        part = idx[start : start + batch_size]
        logits, delta = model(
            torch.tensor(seq[part], dtype=torch.float32, device=device),
            torch.tensor(valid[part], dtype=torch.float32, device=device),
            torch.tensor(base_logits[part], dtype=torch.float32, device=device),
        )
        preds.append(torch.sigmoid(logits).cpu().numpy())
        deltas.append(delta.cpu().numpy())
    return np.vstack(preds), np.vstack(deltas)


def find_best_epoch(
    spec: SequenceSpec,
    seq: np.ndarray,
    valid: np.ndarray,
    base_logits: np.ndarray,
    y: np.ndarray,
    inner_train_idx: np.ndarray,
    inner_val_idx: np.ndarray,
    device: torch.device,
    seed: int,
    batch_size: int,
    target_weights: np.ndarray,
) -> int:
    set_seed(seed)
    model = SequenceResidualNet(seq.shape[-1], spec).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=spec.lr, weight_decay=spec.weight_decay)
    target_weight_tensor = torch.tensor(target_weights, dtype=torch.float32, device=device)
    dataset = TensorDataset(
        torch.tensor(seq[inner_train_idx], dtype=torch.float32),
        torch.tensor(valid[inner_train_idx], dtype=torch.float32),
        torch.tensor(base_logits[inner_train_idx], dtype=torch.float32),
        torch.tensor(y[inner_train_idx], dtype=torch.float32),
    )
    generator = torch.Generator()
    generator.manual_seed(seed)
    loader = DataLoader(dataset, batch_size=min(batch_size, len(dataset)), shuffle=True, generator=generator)
    best_epoch = 1
    best_score = float("inf")
    stale = 0
    for epoch in range(1, spec.max_epochs + 1):
        model.train()
        for batch_seq, batch_valid, batch_base, batch_y in loader:
            batch_seq = batch_seq.to(device)
            batch_valid = batch_valid.to(device)
            batch_base = batch_base.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, delta = model(batch_seq, batch_valid, batch_base)
            bce = nn.functional.binary_cross_entropy_with_logits(logits, batch_y, reduction="none")
            loss = torch.mean(bce * target_weight_tensor) + spec.residual_penalty * torch.mean(delta * delta)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
        pred, _ = predict_model(model, seq, valid, base_logits, inner_val_idx, device, batch_size)
        score = avg_log_loss(y[inner_val_idx], pred)
        if score < best_score - 1e-4:
            best_score = score
            best_epoch = epoch
            stale = 0
        else:
            stale += 1
        if stale >= spec.patience:
            break
    return best_epoch


def write_prediction_files(
    output_dir: Path,
    name: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    oof_pred: np.ndarray,
    test_pred: np.ndarray,
) -> tuple[Path, Path]:
    oof = train[KEY_COLUMNS].copy()
    for target_idx, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = np.clip(oof_pred[:, target_idx], EPS, 1.0 - EPS)
    submission = sample[KEY_COLUMNS].copy()
    for target_idx, target in enumerate(TARGET_COLUMNS):
        submission[target] = np.clip(test_pred[:, target_idx], EPS, 1.0 - EPS)
    oof_path = output_dir / f"oof_{name}.csv"
    submission_path = output_dir / f"submission_{name}.csv"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(submission_path, index=False)
    return oof_path, submission_path


def parse_specs(raw: str) -> list[SequenceSpec]:
    specs: list[SequenceSpec] = []
    for item in raw.split(","):
        if not item.strip():
            continue
        # name:encoder:context:d_model:dropout:max_delta
        name, encoder, context, d_model, dropout, max_delta = item.split(":")
        specs.append(
            SequenceSpec(
                name=name,
                encoder=encoder,
                context_days=int(context),
                d_model=int(d_model),
                dropout=float(dropout),
                max_delta=float(max_delta),
                lr=0.003,
                weight_decay=0.01,
                residual_penalty=0.05,
                max_epochs=220,
                patience=24,
            )
        )
    return specs


def train_one_spec(
    args: argparse.Namespace,
    spec: SequenceSpec,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    panel: pd.DataFrame,
    daily_features: np.ndarray,
    base_oof: np.ndarray,
    base_test: np.ndarray,
    device: torch.device,
    output_dir: Path,
) -> dict:
    seq_all, valid_all = make_sequences(panel, daily_features, spec.context_days)
    train_panel_idx = panel[panel["_split"].eq("train")].sort_values("_row")["panel_row"].to_numpy(dtype=int)
    test_panel_idx = panel[panel["_split"].eq("sample")].sort_values("_row")["panel_row"].to_numpy(dtype=int)
    seq_train = seq_all[train_panel_idx]
    valid_train = valid_all[train_panel_idx]
    seq_test = seq_all[test_panel_idx]
    valid_test = valid_all[test_panel_idx]
    base_logit_train = safe_logit(base_oof).astype(np.float32)
    base_logit_test = safe_logit(base_test).astype(np.float32)
    y = train[TARGET_COLUMNS].to_numpy(dtype=np.float32)
    target_weights = parse_target_weights(args.target_weights, args.target_weight_default)

    folds = make_subject_time_folds(train, args.n_folds)
    oof_pred = np.zeros_like(base_oof, dtype=float)
    fold_rows = []
    for fold_idx, (outer_train_idx, outer_val_idx) in enumerate(folds):
        inner_train_idx, inner_val_idx = inner_time_split(train, outer_train_idx, args.inner_validation_fraction)
        best_epoch = find_best_epoch(
            spec,
            seq_train,
            valid_train,
            base_logit_train,
            y,
            inner_train_idx,
            inner_val_idx,
            device,
            args.seed + 1000 * fold_idx,
            args.batch_size,
            target_weights,
        )
        model = train_fixed_epochs(
            spec,
            seq_train,
            valid_train,
            base_logit_train,
            y,
            outer_train_idx,
            best_epoch,
            device,
            args.seed + 2000 * fold_idx,
            args.batch_size,
            target_weights,
        )
        pred, delta = predict_model(model, seq_train, valid_train, base_logit_train, outer_val_idx, device, args.batch_size)
        oof_pred[outer_val_idx] = pred
        fold_rows.append(
            {
                "name": spec.name,
                "fold": fold_idx,
                "best_epoch": int(best_epoch),
                "fold_log_loss": avg_log_loss(y[outer_val_idx], pred),
                "delta_abs_mean": float(np.abs(delta).mean()),
                "n_train": int(len(outer_train_idx)),
                "n_val": int(len(outer_val_idx)),
            }
        )
        print(spec.name, "fold", fold_idx, "epoch", best_epoch, "loss", fold_rows[-1]["fold_log_loss"])

    full_epochs = int(np.median([row["best_epoch"] for row in fold_rows]))
    full_model = train_fixed_epochs(
        spec,
        seq_train,
        valid_train,
        base_logit_train,
        y,
        np.arange(len(train), dtype=int),
        full_epochs,
        device,
        args.seed + 7777,
        args.batch_size,
        target_weights,
    )
    test_pred, test_delta = predict_model(
        full_model,
        seq_test,
        valid_test,
        base_logit_test,
        np.arange(len(sample), dtype=int),
        device,
        args.batch_size,
    )
    oof_path, submission_path = write_prediction_files(output_dir, spec.name, train, sample, oof_pred, test_pred)

    result = {
        "name": spec.name,
        "encoder": spec.encoder,
        "context_days": spec.context_days,
        "d_model": spec.d_model,
        "dropout": spec.dropout,
        "max_delta": spec.max_delta,
        "full_train_epochs": full_epochs,
        "uniform_oof_cv": avg_log_loss(y, oof_pred),
        "base_uniform_oof_cv": avg_log_loss(y, base_oof),
        "oof_path": str(oof_path),
        "submission_path": str(submission_path),
        "test_delta_abs_mean": float(np.abs(test_delta).mean()),
        "test_min": float(test_pred.min()),
        "test_max": float(test_pred.max()),
        "target_weights": {target: float(target_weights[i]) for i, target in enumerate(TARGET_COLUMNS)},
    }
    pd.DataFrame(fold_rows).to_csv(output_dir / f"fold_report_{spec.name}.csv", index=False)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train tiny fold-safe RNN/Transformer residual encoders over subject day sequences.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--base-oof", default="outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv")
    parser.add_argument("--base-submission", default="outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv")
    parser.add_argument("--output-dir", default="outputs/sequence_encoder_residual")
    parser.add_argument("--specs", default="gru28:gru:28:32:0.30:0.65,gru14:gru:14:24:0.35:0.50,tf28:transformer:28:32:0.35:0.50")
    parser.add_argument("--pca-components", type=int, default=48)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--inner-validation-fraction", type=float, default=0.18)
    parser.add_argument("--batch-size", type=int, default=96)
    parser.add_argument("--max-epochs", type=int, default=140)
    parser.add_argument("--patience", type=int, default=18)
    parser.add_argument("--target-weights", default="")
    parser.add_argument("--target-weight-default", type=float, default=1.0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    device = torch_device(args.device)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample, _ = add_panel_position(train, sample)
    panel = panel_table(train, sample)
    daily = compressed_daily_features(args.master_path, panel, args.pca_components)
    base_oof, base_test = load_base_predictions(args, train, sample)

    results = []
    for raw_spec in parse_specs(args.specs):
        spec = replace(raw_spec, max_epochs=args.max_epochs, patience=args.patience)
        results.append(
            train_one_spec(args, spec, train, sample, panel, daily, base_oof, base_test, device, output_dir)
        )
    report = {
        "device": str(device),
        "pca_components": int(daily.shape[1]),
        "base_oof": args.base_oof,
        "base_submission": args.base_submission,
        "results": results,
        "anti_overfit_controls": [
            "Residual logit head initialized at zero, so training starts from the base predictions.",
            "Outer validation labels are not used for early stopping; epoch is selected on an inner split of the outer-training fold.",
            "Tiny encoders, dropout, AdamW weight decay, gradient clipping, tanh-clamped residual logits, and residual L2 penalty.",
            "OOF predictions are produced by retraining on the full outer-train fold for the inner-selected epoch.",
        ],
    }
    with (output_dir / "sequence_encoder_report.json").open("w") as f:
        json.dump(report, f, indent=2)
    pd.DataFrame(results).to_csv(output_dir / "sequence_encoder_report.csv", index=False)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
