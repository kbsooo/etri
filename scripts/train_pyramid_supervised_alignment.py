from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import log_loss
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etri_diffusion.pyramid_model import PyramidDayEncoder


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


class PyramidResidualClassifier(nn.Module):
    def __init__(self, encoder: PyramidDayEncoder, dropout: float, hidden: int, max_delta: float) -> None:
        super().__init__()
        self.encoder = encoder
        self.max_delta = max_delta
        if hidden > 0:
            self.head = nn.Sequential(
                nn.LayerNorm(encoder.latent_dim),
                nn.Dropout(dropout),
                nn.Linear(encoder.latent_dim, hidden),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden, len(TARGET_COLUMNS)),
            )
        else:
            self.head = nn.Sequential(
                nn.LayerNorm(encoder.latent_dim),
                nn.Dropout(dropout),
                nn.Linear(encoder.latent_dim, len(TARGET_COLUMNS)),
            )
        final = self.head[-1]
        if isinstance(final, nn.Linear):
            nn.init.zeros_(final.weight)
            nn.init.zeros_(final.bias)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        slot_features: torch.Tensor,
        event_tokens: torch.Tensor,
        event_mask: torch.Tensor,
        prototype_mixture: torch.Tensor,
        day_context: torch.Tensor,
        base_logits: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, dict[str, torch.Tensor]]:
        out = self.encoder(x, mask, slot_features, event_tokens, event_mask, prototype_mixture, day_context)
        delta = self.max_delta * torch.tanh(self.head(out["latent"]))
        return base_logits + delta, delta, out


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def choose_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def assert_unique_keys(df: pd.DataFrame, name: str) -> None:
    dupes = df.duplicated(KEY_COLUMNS).sum()
    if dupes:
        raise ValueError(f"{name} has duplicated key rows: {dupes}")


def safe_logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values.astype(np.float32), EPS, 1.0 - EPS)
    return np.log(clipped / (1.0 - clipped)).astype(np.float32)


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def load_dataset(input_dir: Path) -> dict[str, np.ndarray | pd.DataFrame | dict]:
    arr = np.load(input_dir / "encoder_day_pyramid.npz")
    day_index = normalize_keys(pd.read_csv(input_dir / "day_index.csv"))
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
    assert_unique_keys(day_index, "day_index")
    return {
        "x": arr["x"].astype(np.float32),
        "mask": arr["mask"].astype(np.float32),
        "actual": arr["actual"].astype(np.float32),
        "actual_mask": arr["actual_mask"].astype(np.float32),
        "delta": arr["delta"].astype(np.float32),
        "event_tokens": arr["event_tokens"].astype(np.float32),
        "event_mask": arr["event_mask"].astype(np.float32),
        "prototype_mixture": arr["prototype_mixture"].astype(np.float32),
        "day_context": arr["day_context"].astype(np.float32),
        "slot_features": arr["slot_features"].astype(np.float32),
        "day_index": day_index,
        "metadata": metadata,
    }


def align_rows(day_index: pd.DataFrame, train_path: Path, sample_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    train = normalize_keys(pd.read_csv(train_path))
    sample = normalize_keys(pd.read_csv(sample_path))
    assert_unique_keys(train, "train")
    assert_unique_keys(sample, "sample")
    lookup = day_index.reset_index(names="_day_idx")[KEY_COLUMNS + ["_day_idx"]]
    train_aligned = train.merge(lookup, on=KEY_COLUMNS, how="left", validate="one_to_one")
    sample_aligned = sample.merge(lookup, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_aligned["_day_idx"].isna().any():
        missing = train_aligned[train_aligned["_day_idx"].isna()][KEY_COLUMNS].head().to_dict(orient="records")
        raise ValueError(f"Train rows missing from day_index, examples: {missing}")
    if sample_aligned["_day_idx"].isna().any():
        missing = sample_aligned[sample_aligned["_day_idx"].isna()][KEY_COLUMNS].head().to_dict(orient="records")
        raise ValueError(f"Sample rows missing from day_index, examples: {missing}")
    return train, sample, train_aligned["_day_idx"].to_numpy(np.int64), sample_aligned["_day_idx"].to_numpy(np.int64)


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(train_df), dtype=np.int64)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=np.int64)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def subject_prior_prob(train_part: pd.DataFrame, eval_part: pd.DataFrame, alpha: float) -> np.ndarray:
    global_rate = train_part[TARGET_COLUMNS].mean().clip(EPS, 1.0 - EPS)
    subject_sum = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    subject_count = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    subject_rate = (subject_sum + alpha * global_rate) / (subject_count + alpha)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=np.float32)
    global_values = global_rate.to_numpy(np.float32)
    for row_i, subject in enumerate(eval_part["subject_id"].astype(str)):
        if subject in subject_rate.index:
            pred[row_i] = subject_rate.loc[subject, TARGET_COLUMNS].to_numpy(np.float32)
        else:
            pred[row_i] = global_values
    return np.clip(pred, EPS, 1.0 - EPS)


def make_model(args: argparse.Namespace, metadata: dict) -> PyramidResidualClassifier:
    shape = metadata["shape"]
    encoder = PyramidDayEncoder(
        input_channels=shape["input_channels"],
        base_channels=shape["base_channels"],
        slot_feature_dim=len(metadata["slot_feature_names"]),
        event_dim=shape["event_dim"],
        prototype_k=shape["prototype_k"],
        n_prototype_groups=shape["prototype_groups"],
        day_context_dim=len(metadata["day_context_names"]),
        slots=shape["slots"],
        d_model=args.d_model,
        latent_dim=args.latent_dim,
        n_layers=args.layers,
        n_heads=args.heads,
        dropout=args.encoder_dropout,
    )
    return PyramidResidualClassifier(encoder, dropout=args.head_dropout, hidden=args.head_hidden, max_delta=args.max_delta)


def load_checkpoint(model: PyramidResidualClassifier, checkpoint_path: Path | None) -> dict[str, object]:
    if checkpoint_path is None:
        return {"checkpoint_path": None, "loaded_keys": 0, "skipped_keys": []}
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    state = checkpoint.get("model_state_dict", checkpoint)
    target = model.encoder.state_dict()
    compatible = {}
    skipped = []
    for key, value in state.items():
        if key in target and tuple(target[key].shape) == tuple(value.shape):
            compatible[key] = value
        else:
            skipped.append(key)
    model.encoder.load_state_dict(compatible, strict=False)
    return {"checkpoint_path": str(checkpoint_path), "loaded_keys": len(compatible), "skipped_keys": skipped}


def make_optimizer(model: PyramidResidualClassifier, args: argparse.Namespace) -> torch.optim.Optimizer:
    if args.encoder_lr_scale <= 0:
        for param in model.encoder.parameters():
            param.requires_grad = False
        return torch.optim.AdamW(model.head.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    return torch.optim.AdamW(
        [
            {"params": model.encoder.parameters(), "lr": args.lr * args.encoder_lr_scale},
            {"params": model.head.parameters(), "lr": args.lr},
        ],
        weight_decay=args.weight_decay,
    )


def tensor_batch(values: np.ndarray, indices: torch.Tensor, device: torch.device) -> torch.Tensor:
    return torch.from_numpy(values[indices.detach().cpu().numpy()]).to(device=device, dtype=torch.float32)


def corrupt_batch(
    x: torch.Tensor,
    mask: torch.Tensor,
    actual_mask: torch.Tensor,
    event_mask: torch.Tensor,
    prototype_mixture: torch.Tensor,
    base_channels: int,
    entry_dropout: float,
    slot_dropout_prob: float,
    channel_dropout_prob: float,
    event_dropout: float,
    prototype_noise: float,
    noise_std: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    corrupted = x.clone()
    corrupted_mask = mask.clone()
    batch, slots, _ = x.shape
    device = x.device
    hidden = (torch.rand(batch, slots, base_channels, device=device) < entry_dropout) & (actual_mask > 0.5)
    if slot_dropout_prob > 0:
        for row in range(batch):
            if torch.rand((), device=device) < slot_dropout_prob:
                length = int(torch.randint(3, 25, (), device=device).item())
                start = int(torch.randint(0, max(slots - length + 1, 1), (), device=device).item())
                hidden[row, start : start + length] |= actual_mask[row, start : start + length] > 0.5
    if channel_dropout_prob > 0:
        for row in range(batch):
            if torch.rand((), device=device) < channel_dropout_prob:
                width = int(torch.randint(4, min(base_channels, 25), (), device=device).item())
                cols = torch.randperm(base_channels, device=device)[:width]
                hidden[row, :, cols] |= actual_mask[row, :, cols] > 0.5

    for block in [0, 2, 3]:
        start = block * base_channels
        end = start + base_channels
        corrupted[:, :, start:end] = torch.where(hidden, torch.zeros_like(corrupted[:, :, start:end]), corrupted[:, :, start:end])
        corrupted_mask[:, :, start:end] = torch.where(hidden, torch.zeros_like(corrupted_mask[:, :, start:end]), corrupted_mask[:, :, start:end])
    observed_start = 4 * base_channels
    observed_end = observed_start + base_channels
    corrupted[:, :, observed_start:observed_end] = torch.where(
        hidden,
        torch.zeros_like(corrupted[:, :, observed_start:observed_end]),
        corrupted[:, :, observed_start:observed_end],
    )
    if noise_std > 0:
        visible = (~hidden).float()
        for block in [0, 2, 3]:
            start = block * base_channels
            end = start + base_channels
            corrupted[:, :, start:end] = corrupted[:, :, start:end] + torch.randn_like(corrupted[:, :, start:end]) * noise_std * visible
    corrupted_event_mask = event_mask.clone()
    if event_dropout > 0:
        corrupted_event_mask = corrupted_event_mask * (torch.rand_like(corrupted_event_mask) > event_dropout).float()
    corrupted_proto = prototype_mixture.clone()
    if prototype_noise > 0:
        noisy = torch.clamp(corrupted_proto + torch.randn_like(corrupted_proto) * prototype_noise, min=1e-4)
        corrupted_proto = noisy / noisy.sum(dim=2, keepdim=True).clamp_min(1e-4)
    return corrupted, corrupted_mask, hidden.float(), corrupted_event_mask, corrupted_proto


def reconstruction_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    observed_mask: torch.Tensor,
    hidden_mask: torch.Tensor,
    channel_weights: torch.Tensor,
) -> torch.Tensor:
    weights = channel_weights.view(1, 1, -1)
    hidden_weight = torch.where(hidden_mask > 0.5, torch.ones_like(hidden_mask), torch.full_like(hidden_mask, 0.25))
    total_weight = observed_mask * hidden_weight * weights
    return (((pred - target) ** 2) * total_weight).sum() / total_weight.sum().clamp_min(1.0)


def model_inputs(
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    day_idx: torch.Tensor,
    slot_features: torch.Tensor,
    device: torch.device,
    corrupted: bool,
    args: argparse.Namespace,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor | None, torch.Tensor | None, torch.Tensor | None]:
    x = tensor_batch(model_data["x"], day_idx, device)
    mask = tensor_batch(model_data["mask"], day_idx, device)
    actual_mask = tensor_batch(model_data["actual_mask"], day_idx, device)
    event_tokens = tensor_batch(model_data["event_tokens"], day_idx, device)
    event_mask = tensor_batch(model_data["event_mask"], day_idx, device)
    prototype = tensor_batch(model_data["prototype_mixture"], day_idx, device)
    day_context = tensor_batch(model_data["day_context"], day_idx, device)
    hidden = None
    if corrupted:
        x, mask, hidden, event_mask, prototype = corrupt_batch(
            x,
            mask,
            actual_mask,
            event_mask,
            prototype,
            int(model_data["metadata"]["shape"]["base_channels"]),
            args.entry_dropout,
            args.slot_dropout_prob,
            args.channel_dropout_prob,
            args.event_dropout,
            args.prototype_noise,
            args.noise_std,
        )
    return x, mask, slot_features, event_tokens, event_mask, prototype, day_context, actual_mask, hidden


@torch.no_grad()
def predict_rows(
    model: PyramidResidualClassifier,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    day_indices: np.ndarray,
    base_logits: np.ndarray,
    batch_size: int,
    device: torch.device,
) -> np.ndarray:
    model.eval()
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    preds = []
    loader = DataLoader(
        TensorDataset(torch.from_numpy(day_indices.astype(np.int64)), torch.from_numpy(base_logits.astype(np.float32))),
        batch_size=batch_size,
        shuffle=False,
    )
    for day_idx, base_cpu in loader:
        x, mask, sf, events, event_mask, proto, context, _, _ = model_inputs(model_data, day_idx, slot_features, device, False, argparse.Namespace())
        logits, _, _ = model(x, mask, sf, events, event_mask, proto, context, base_cpu.to(device))
        preds.append(torch.sigmoid(logits).detach().cpu().numpy())
    return np.clip(np.concatenate(preds, axis=0), EPS, 1.0 - EPS)


def train_epoch(
    model: PyramidResidualClassifier,
    optimizer: torch.optim.Optimizer,
    supervised_loader: DataLoader,
    auxiliary_loader: DataLoader,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    slot_features: torch.Tensor,
    channel_weights: torch.Tensor,
    args: argparse.Namespace,
    device: torch.device,
) -> dict[str, float]:
    model.train()
    aux_iter = iter(auxiliary_loader)
    sup_losses: list[float] = []
    aux_losses: list[float] = []
    delta_losses: list[float] = []
    for day_idx_cpu, y_cpu, base_cpu in supervised_loader:
        day_idx = day_idx_cpu.to(device)
        y = y_cpu.to(device)
        base_logits = base_cpu.to(device)
        x, mask, sf, events, event_mask, proto, context, _, _ = model_inputs(
            model_data, day_idx, slot_features, device, args.supervised_corruption, args
        )
        logits, label_delta, _ = model(x, mask, sf, events, event_mask, proto, context, base_logits)
        supervised = F.binary_cross_entropy_with_logits(logits, y)
        delta_penalty = label_delta.pow(2).mean()
        aux_loss = supervised.detach() * 0.0

        if args.denoise_weight > 0:
            try:
                (aux_day_idx_cpu,) = next(aux_iter)
            except StopIteration:
                aux_iter = iter(auxiliary_loader)
                (aux_day_idx_cpu,) = next(aux_iter)
            aux_day_idx = aux_day_idx_cpu.to(device)
            ax, amask, asf, aevents, aevent_mask, aproto, acontext, actual_mask, hidden = model_inputs(
                model_data, aux_day_idx, slot_features, device, True, args
            )
            clean_actual = tensor_batch(model_data["actual"], aux_day_idx, device)
            clean_delta = tensor_batch(model_data["delta"], aux_day_idx, device)
            zero_base = torch.zeros((aux_day_idx.shape[0], len(TARGET_COLUMNS)), device=device)
            _, _, aux_out = model(ax, amask, asf, aevents, aevent_mask, aproto, acontext, zero_base)
            actual_loss = reconstruction_loss(aux_out["actual_pred"], clean_actual, actual_mask, hidden, channel_weights)
            delta_loss = reconstruction_loss(aux_out["delta_pred"], clean_delta, actual_mask, hidden, channel_weights)
            aux_loss = actual_loss + args.delta_recon_weight * delta_loss

        loss = supervised + args.residual_l2 * delta_penalty + args.denoise_weight * aux_loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        optimizer.step()
        sup_losses.append(float(supervised.detach().cpu()))
        aux_losses.append(float(aux_loss.detach().cpu()))
        delta_losses.append(float(delta_penalty.detach().cpu()))
    return {
        "supervised_loss": float(np.mean(sup_losses)),
        "aux_loss": float(np.mean(aux_losses)),
        "delta_penalty": float(np.mean(delta_losses)),
    }


def train_one_fold(
    fold_id: int,
    train_rows: np.ndarray,
    val_rows: np.ndarray,
    train: pd.DataFrame,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[np.ndarray, dict[str, object], dict[str, list[dict[str, float]]]]:
    seed_everything(args.seed + fold_id)
    model = make_model(args, model_data["metadata"]).to(device)
    load_info = load_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)
    optimizer = make_optimizer(model, args)
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    observed_rate = model_data["actual_mask"].mean(axis=(0, 1)).clip(1e-3, None)
    channel_weights = torch.from_numpy((1.0 / np.sqrt(observed_rate)).clip(0.5, 5.0).astype(np.float32)).to(device)
    channel_weights = channel_weights / channel_weights.mean().clamp_min(1e-6)

    prior_train = subject_prior_prob(train.iloc[train_rows], train.iloc[train_rows], args.prior_alpha)
    prior_val = subject_prior_prob(train.iloc[train_rows], train.iloc[val_rows], args.prior_alpha)
    y = train[TARGET_COLUMNS].to_numpy(np.float32)
    supervised_loader = DataLoader(
        TensorDataset(
            torch.from_numpy(train_day_idx[train_rows].astype(np.int64).copy()),
            torch.from_numpy(y[train_rows].copy()),
            torch.from_numpy(safe_logit(prior_train)),
        ),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    if args.auxiliary_days == "train_only":
        aux_indices = np.unique(train_day_idx[train_rows])
    elif args.auxiliary_days == "train_sample":
        aux_indices = np.unique(np.concatenate([train_day_idx[train_rows], sample_day_idx]))
    elif args.auxiliary_days == "all":
        aux_indices = np.arange(model_data["x"].shape[0], dtype=np.int64)
    else:
        raise ValueError(f"Unknown auxiliary days: {args.auxiliary_days}")
    auxiliary_loader = DataLoader(TensorDataset(torch.from_numpy(aux_indices)), batch_size=args.batch_size, shuffle=True)

    best_score = float("inf")
    best_state = None
    best_epoch = 0
    patience_left = args.patience
    log_rows: list[dict[str, float]] = []
    iterator = range(1, args.epochs + 1)
    if args.progress:
        iterator = tqdm(iterator, desc=f"fold {fold_id}/{args.folds}", leave=False)
    for epoch in iterator:
        train_stats = train_epoch(model, optimizer, supervised_loader, auxiliary_loader, model_data, slot_features, channel_weights, args, device)
        val_pred = predict_rows(model, model_data, train_day_idx[val_rows], safe_logit(prior_val), args.batch_size, device)
        val_score, val_targets = average_log_loss(train.iloc[val_rows], val_pred)
        row = {"fold": fold_id, "epoch": epoch, "val_avg_log_loss": val_score, **train_stats, **{f"val_{k}": v for k, v in val_targets.items()}}
        log_rows.append(row)
        if val_score + args.min_delta < best_score:
            best_score = val_score
            best_epoch = epoch
            best_state = copy.deepcopy(model.state_dict())
            patience_left = args.patience
        else:
            patience_left -= 1
        if patience_left <= 0:
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    pred = predict_rows(model, model_data, train_day_idx[val_rows], safe_logit(prior_val), args.batch_size, device)
    score, per_target = average_log_loss(train.iloc[val_rows], pred)
    return pred, {
        "fold": fold_id,
        "train_rows": int(len(train_rows)),
        "valid_rows": int(len(val_rows)),
        "auxiliary_days": int(len(aux_indices)),
        "best_epoch": int(best_epoch),
        "best_val_avg_log_loss": float(best_score),
        "final_val_avg_log_loss": float(score),
        "per_target": per_target,
        "checkpoint_load": load_info,
    }, {"training_log": log_rows}


def train_full_model(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    args: argparse.Namespace,
    device: torch.device,
    epochs: int,
) -> tuple[np.ndarray, dict[str, object]]:
    seed_everything(args.seed + 10000)
    model = make_model(args, model_data["metadata"]).to(device)
    load_info = load_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)
    optimizer = make_optimizer(model, args)
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    observed_rate = model_data["actual_mask"].mean(axis=(0, 1)).clip(1e-3, None)
    channel_weights = torch.from_numpy((1.0 / np.sqrt(observed_rate)).clip(0.5, 5.0).astype(np.float32)).to(device)
    channel_weights = channel_weights / channel_weights.mean().clamp_min(1e-6)
    prior_train = subject_prior_prob(train, train, args.prior_alpha)
    prior_sample = subject_prior_prob(train, sample, args.prior_alpha)
    y = train[TARGET_COLUMNS].to_numpy(np.float32)
    supervised_loader = DataLoader(
        TensorDataset(torch.from_numpy(train_day_idx.astype(np.int64).copy()), torch.from_numpy(y.copy()), torch.from_numpy(safe_logit(prior_train))),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    aux_indices = np.unique(np.concatenate([train_day_idx, sample_day_idx]).astype(np.int64))
    auxiliary_loader = DataLoader(TensorDataset(torch.from_numpy(aux_indices)), batch_size=args.batch_size, shuffle=True)
    log_rows = []
    for _ in range(epochs):
        log_rows.append(train_epoch(model, optimizer, supervised_loader, auxiliary_loader, model_data, slot_features, channel_weights, args, device))
    pred = predict_rows(model, model_data, sample_day_idx, safe_logit(prior_sample), args.batch_size, device)
    return pred, {"epochs": int(epochs), "training_log": log_rows, "checkpoint_load": load_info}


def write_outputs(
    output_dir: Path,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    oof_pred: np.ndarray,
    test_pred: np.ndarray,
    fold_reports: list[dict[str, object]],
    training_logs: list[dict[str, object]],
    full_report: dict[str, object],
    args: argparse.Namespace,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    avg, per_target = average_log_loss(train, oof_pred)
    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = np.clip(oof_pred[:, i], EPS, 1.0 - EPS)
    oof.to_csv(output_dir / "oof_pyramid_supervised_alignment.csv", index=False)
    submission = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        submission[target] = np.clip(test_pred[:, i], EPS, 1.0 - EPS)
    submission.to_csv(output_dir / "submission_pyramid_supervised_alignment.csv", index=False)
    pd.DataFrame(fold_reports).to_csv(output_dir / "fold_scores.csv", index=False)
    pd.concat([pd.DataFrame(item["training_log"]) for item in training_logs], ignore_index=True).to_csv(
        output_dir / "training_log.csv", index=False
    )
    score = {"name": "pyramid_supervised_alignment", "avg_log_loss": avg, **per_target}
    pd.DataFrame([score]).to_csv(output_dir / "score.csv", index=False)
    report = {"score": score, "folds": fold_reports, "full_model": full_report, "args": vars(args)}
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Pyramid supervised alignment",
        "",
        f"- Average log-loss: `{avg:.6f}`",
        f"- Init checkpoint: `{args.init_checkpoint}`",
        f"- Prior alpha: `{args.prior_alpha}`",
        f"- Full model epochs: `{full_report['epochs']}`",
        "",
        "## Target scores",
        "",
        "| target | log_loss |",
        "| --- | --- |",
    ]
    for target in TARGET_COLUMNS:
        lines.append(f"| {target} | {per_target[target]:.6f} |")
    lines.extend(["", "## Fold scores", "", "| fold | valid_rows | best_epoch | final_val_avg_log_loss |", "| --- | --- | --- | --- |"])
    for row in fold_reports:
        lines.append(f"| {row['fold']} | {row['valid_rows']} | {row['best_epoch']} | {row['final_val_avg_log_loss']:.6f} |")
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supervised residual alignment for the 5-minute Pyramid Day Encoder.")
    parser.add_argument("--input-dir", default="outputs/encoder_day_pyramid")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/pyramid_supervised_alignment_v1")
    parser.add_argument("--init-checkpoint", default="outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-folds", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--full-epochs", type=int, default=0)
    parser.add_argument("--patience", type=int, default=9)
    parser.add_argument("--min-delta", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--d-model", type=int, default=96)
    parser.add_argument("--latent-dim", type=int, default=128)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--encoder-dropout", type=float, default=0.15)
    parser.add_argument("--head-dropout", type=float, default=0.25)
    parser.add_argument("--head-hidden", type=int, default=64)
    parser.add_argument("--max-delta", type=float, default=1.2)
    parser.add_argument("--prior-alpha", type=float, default=10.0)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--encoder-lr-scale", type=float, default=0.02)
    parser.add_argument("--weight-decay", type=float, default=2e-4)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--residual-l2", type=float, default=0.03)
    parser.add_argument("--denoise-weight", type=float, default=0.02)
    parser.add_argument("--delta-recon-weight", type=float, default=0.75)
    parser.add_argument("--entry-dropout", type=float, default=0.08)
    parser.add_argument("--slot-dropout-prob", type=float, default=0.35)
    parser.add_argument("--channel-dropout-prob", type=float, default=0.20)
    parser.add_argument("--event-dropout", type=float, default=0.15)
    parser.add_argument("--prototype-noise", type=float, default=0.03)
    parser.add_argument("--noise-std", type=float, default=0.03)
    parser.add_argument("--supervised-corruption", action="store_true")
    parser.add_argument("--auxiliary-days", choices=["train_sample", "train_only", "all"], default="train_sample")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--progress", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_data = load_dataset(Path(args.input_dir))
    train, sample, train_day_idx, sample_day_idx = align_rows(model_data["day_index"], Path(args.train_path), Path(args.sample_path))
    device = choose_device(args.device)
    folds = make_subject_time_folds(train, args.folds)
    if args.max_folds > 0:
        folds = folds[: args.max_folds]
    oof_pred = np.full((len(train), len(TARGET_COLUMNS)), np.nan, dtype=float)
    fold_reports = []
    training_logs = []
    for fold_id, (train_rows, val_rows) in enumerate(folds, start=1):
        pred, fold_report, train_log = train_one_fold(
            fold_id, train_rows, val_rows, train, train_day_idx, sample_day_idx, model_data, args, device
        )
        oof_pred[val_rows] = pred
        fold_reports.append(fold_report)
        training_logs.append(train_log)
        print(f"fold={fold_id} score={fold_report['final_val_avg_log_loss']:.6f} best_epoch={fold_report['best_epoch']}")
    if np.isnan(oof_pred).any():
        missing = int(np.isnan(oof_pred).any(axis=1).sum())
        raise ValueError(f"OOF predictions are incomplete; missing rows={missing}. Use all folds for scoring.")
    if args.full_epochs > 0:
        full_epochs = args.full_epochs
    else:
        best_epochs = [int(row["best_epoch"]) for row in fold_reports if int(row["best_epoch"]) > 0]
        full_epochs = int(np.median(best_epochs)) if best_epochs else args.epochs
    test_pred, full_report = train_full_model(train, sample, train_day_idx, sample_day_idx, model_data, args, device, full_epochs)
    write_outputs(output_dir, train, sample, oof_pred, test_pred, fold_reports, training_logs, full_report, args)
    avg, per_target = average_log_loss(train, oof_pred)
    print(f"avg_log_loss={avg:.6f}")
    print("target_scores=" + json.dumps(per_target, sort_keys=True))
    print(f"saved: {output_dir / 'submission_pyramid_supervised_alignment.csv'}")


if __name__ == "__main__":
    main()
