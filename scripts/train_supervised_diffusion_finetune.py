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
from sklearn.metrics import log_loss
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etri_diffusion.model import DayDenoisingDiffusionEncoder


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


class SupervisedDiffusionModel(nn.Module):
    def __init__(self, encoder: DayDenoisingDiffusionEncoder, dropout: float, head_hidden: int) -> None:
        super().__init__()
        self.encoder = encoder
        if head_hidden > 0:
            self.head = nn.Sequential(
                nn.LayerNorm(encoder.latent_dim),
                nn.Dropout(dropout),
                nn.Linear(encoder.latent_dim, head_hidden),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(head_hidden, len(TARGET_COLUMNS)),
            )
        else:
            self.head = nn.Sequential(
                nn.LayerNorm(encoder.latent_dim),
                nn.Dropout(dropout),
                nn.Linear(encoder.latent_dim, len(TARGET_COLUMNS)),
            )

    def clean_latent(self, x: torch.Tensor, mask: torch.Tensor, subject_idx: torch.Tensor) -> torch.Tensor:
        t0 = torch.zeros(x.shape[0], device=x.device, dtype=torch.long)
        _, latent = self.encoder(x * mask, mask, subject_idx, t0)
        return latent

    def forward(self, x: torch.Tensor, mask: torch.Tensor, subject_idx: torch.Tensor) -> torch.Tensor:
        return self.head(self.clean_latent(x, mask, subject_idx))


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def choose_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
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


def load_tensor_dataset(input_dir: Path) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, dict]:
    arr = np.load(input_dir / "hourly_tensor.npz")
    day_index = normalize_keys(pd.read_csv(input_dir / "day_index.csv"))
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
    assert_unique_keys(day_index, "day_index")
    return arr["x"].astype(np.float32), arr["mask"].astype(np.float32), day_index, metadata


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
    return train, sample, train_aligned["_day_idx"].to_numpy(dtype=np.int64), sample_aligned["_day_idx"].to_numpy(dtype=np.int64)


def make_subject_time_folds(train_df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    if n_folds < 2:
        raise ValueError("--folds must be at least 2")
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    ordered = train_df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())

    all_indices = np.arange(len(train_df))
    folds = []
    for fold_indices in val_indices:
        val_idx = np.array(sorted(fold_indices), dtype=np.int64)
        train_idx = np.setdiff1d(all_indices, val_idx, assume_unique=False)
        folds.append((train_idx.astype(np.int64), val_idx))
    return folds


def diffusion_schedule(steps: int, device: torch.device) -> torch.Tensor:
    betas = torch.linspace(1e-4, 0.02, steps, device=device)
    alphas = 1.0 - betas
    return torch.cumprod(alphas, dim=0)


def modality_groups(metadata: dict) -> dict[str, torch.Tensor]:
    groups: dict[str, list[int]] = {}
    for idx, modality in enumerate(metadata["channel_modalities"]):
        base = modality.replace("_dev", "")
        groups.setdefault(base, []).append(idx)
    return {key: torch.tensor(value, dtype=torch.long) for key, value in groups.items()}


def corrupt_batch(
    x: torch.Tensor,
    mask: torch.Tensor,
    alpha_bars: torch.Tensor,
    groups: dict[str, torch.Tensor],
    entry_dropout: float,
    hour_dropout_prob: float,
    modality_dropout_prob: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    batch, hours, _ = x.shape
    t = torch.randint(0, len(alpha_bars), (batch,), device=x.device)
    alpha = alpha_bars[t].view(batch, 1, 1)
    noise = torch.randn_like(x)
    x_t = torch.sqrt(alpha) * x + torch.sqrt(1.0 - alpha) * noise

    condition_mask = mask.clone()
    if entry_dropout > 0:
        condition_mask = condition_mask * (torch.rand_like(condition_mask) > entry_dropout).float()
    if hour_dropout_prob > 0:
        for i in range(batch):
            if torch.rand((), device=x.device) < hour_dropout_prob:
                length = int(torch.randint(1, 5, (), device=x.device).item())
                start = int(torch.randint(0, max(hours - length + 1, 1), (), device=x.device).item())
                condition_mask[i, start : start + length, :] = 0.0
    if modality_dropout_prob > 0 and groups:
        group_items = list(groups.items())
        for i in range(batch):
            if torch.rand((), device=x.device) < modality_dropout_prob:
                _, indices = random.choice(group_items)
                condition_mask[i, :, indices.to(x.device)] = 0.0
    return x_t * condition_mask, condition_mask, noise, t


def weighted_noise_loss(
    pred: torch.Tensor,
    target_noise: torch.Tensor,
    observed_mask: torch.Tensor,
    channel_weights: torch.Tensor,
) -> torch.Tensor:
    weights = channel_weights.view(1, 1, -1)
    denom = (observed_mask * weights).sum().clamp_min(1.0)
    return (((pred - target_noise) ** 2) * observed_mask * weights).sum() / denom


def build_subject_indices(day_index: pd.DataFrame, subject_mode: str) -> tuple[np.ndarray, dict[str, int], int]:
    subjects = sorted(day_index["subject_id"].unique().tolist())
    subject_map = {sid: i for i, sid in enumerate(subjects)}
    if subject_mode == "zero":
        return np.zeros(len(day_index), dtype=np.int64), subject_map, 1
    return day_index["subject_id"].map(subject_map).to_numpy(dtype=np.int64).copy(), subject_map, len(subjects)


def build_model(args: argparse.Namespace, channels: int, n_subjects: int) -> SupervisedDiffusionModel:
    encoder = DayDenoisingDiffusionEncoder(
        channels=channels,
        n_subjects=n_subjects,
        d_model=args.d_model,
        latent_dim=args.latent_dim,
        n_layers=args.layers,
        n_heads=args.heads,
        dropout=args.dropout,
    )
    return SupervisedDiffusionModel(encoder=encoder, dropout=args.head_dropout, head_hidden=args.head_hidden)


def load_encoder_checkpoint(model: SupervisedDiffusionModel, checkpoint_path: Path | None) -> dict[str, object]:
    if checkpoint_path is None:
        return {"checkpoint_path": None, "loaded_keys": 0, "skipped_keys": []}
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    state = checkpoint.get("model_state_dict", checkpoint)
    target_state = model.encoder.state_dict()
    compatible = {}
    skipped = []
    for key, value in state.items():
        if key in target_state and tuple(target_state[key].shape) == tuple(value.shape):
            compatible[key] = value
        else:
            skipped.append(key)
    model.encoder.load_state_dict(compatible, strict=False)
    return {
        "checkpoint_path": str(checkpoint_path),
        "loaded_keys": int(len(compatible)),
        "skipped_keys": skipped,
    }


def positive_weight_tensor(y: np.ndarray, mode: str, device: torch.device) -> torch.Tensor | None:
    if mode == "none":
        return None
    pos = y.sum(axis=0)
    neg = y.shape[0] - pos
    weights = np.divide(neg, np.maximum(pos, 1.0))
    weights = np.clip(weights, 0.25, 4.0).astype(np.float32)
    return torch.from_numpy(weights).to(device)


def make_optimizer(model: SupervisedDiffusionModel, args: argparse.Namespace) -> torch.optim.Optimizer:
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


def make_auxiliary_day_indices(
    mode: str,
    labeled_train_rows: np.ndarray,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
) -> np.ndarray:
    if mode == "train_only":
        values = train_day_idx[labeled_train_rows]
    elif mode == "train_sample":
        values = np.concatenate([train_day_idx[labeled_train_rows], sample_day_idx])
    elif mode == "all":
        values = np.arange(int(max(train_day_idx.max(), sample_day_idx.max())) + 1, dtype=np.int64)
    else:
        raise ValueError(f"Unknown auxiliary mode: {mode}")
    return np.unique(values.astype(np.int64))


def average_log_loss(y_true: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    clipped = np.clip(pred, EPS, 1.0 - EPS)
    per_target = {
        target: float(log_loss(y_true[target].to_numpy(), clipped[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


@torch.no_grad()
def predict_day_indices(
    model: SupervisedDiffusionModel,
    x: torch.Tensor,
    mask: torch.Tensor,
    subject_idx: torch.Tensor,
    day_indices: np.ndarray,
    batch_size: int,
    device: torch.device,
) -> np.ndarray:
    model.eval()
    preds = []
    loader = DataLoader(TensorDataset(torch.from_numpy(day_indices.astype(np.int64))), batch_size=batch_size, shuffle=False)
    for (idx_cpu,) in loader:
        idx = idx_cpu.to(device)
        logits = model(x[idx], mask[idx], subject_idx[idx])
        preds.append(torch.sigmoid(logits).detach().cpu().numpy())
    return np.clip(np.concatenate(preds, axis=0), EPS, 1.0 - EPS)


def fold_epoch(
    model: SupervisedDiffusionModel,
    optimizer: torch.optim.Optimizer,
    supervised_loader: DataLoader,
    auxiliary_loader: DataLoader,
    tensors: dict[str, torch.Tensor],
    alpha_bars: torch.Tensor,
    groups: dict[str, torch.Tensor],
    channel_weights: torch.Tensor,
    criterion: nn.Module,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[float, float]:
    model.train()
    denoise_iter = iter(auxiliary_loader)
    supervised_losses: list[float] = []
    denoise_losses: list[float] = []
    for day_idx_cpu, y_cpu in supervised_loader:
        day_idx = day_idx_cpu.to(device)
        y_batch = y_cpu.to(device)
        logits = model(tensors["x"][day_idx], tensors["mask"][day_idx], tensors["subject_idx"][day_idx])
        supervised_loss = criterion(logits, y_batch)

        if args.denoise_weight > 0:
            try:
                (aux_idx_cpu,) = next(denoise_iter)
            except StopIteration:
                denoise_iter = iter(auxiliary_loader)
                (aux_idx_cpu,) = next(denoise_iter)
            aux_idx = aux_idx_cpu.to(device)
            xb = tensors["x"][aux_idx]
            mb = tensors["mask"][aux_idx]
            sb = tensors["subject_idx"][aux_idx]
            x_cond, cond_mask, noise, t = corrupt_batch(
                xb,
                mb,
                alpha_bars,
                groups,
                entry_dropout=args.entry_dropout,
                hour_dropout_prob=args.hour_dropout_prob,
                modality_dropout_prob=args.modality_dropout_prob,
            )
            pred_noise, _ = model.encoder(x_cond, cond_mask, sb, t)
            denoise_loss = weighted_noise_loss(pred_noise, noise, mb, channel_weights)
        else:
            denoise_loss = supervised_loss.detach() * 0.0

        loss = args.supervised_weight * supervised_loss + args.denoise_weight * denoise_loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        optimizer.step()

        supervised_losses.append(float(supervised_loss.detach().cpu()))
        denoise_losses.append(float(denoise_loss.detach().cpu()))
    return float(np.mean(supervised_losses)), float(np.mean(denoise_losses))


def train_one_fold(
    fold_id: int,
    train_rows: np.ndarray,
    val_rows: np.ndarray,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    train_y: pd.DataFrame,
    tensors: dict[str, torch.Tensor],
    metadata: dict,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[np.ndarray, dict[str, object], dict[str, object]]:
    seed_everything(args.seed + fold_id)
    model = build_model(args, channels=tensors["x"].shape[-1], n_subjects=int(tensors["n_subjects"].item())).to(device)
    load_info = load_encoder_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)

    y_all = train_y[TARGET_COLUMNS].to_numpy(dtype=np.float32)
    train_labels = y_all[train_rows]
    pos_weight = positive_weight_tensor(train_labels, args.pos_weight_mode, device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = make_optimizer(model, args)

    supervised_loader = DataLoader(
        TensorDataset(torch.from_numpy(train_day_idx[train_rows].astype(np.int64)), torch.from_numpy(train_labels)),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    aux_indices = make_auxiliary_day_indices(args.auxiliary_days, train_rows, train_day_idx, sample_day_idx)
    auxiliary_loader = DataLoader(
        TensorDataset(torch.from_numpy(aux_indices)),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    alpha_bars = diffusion_schedule(args.diffusion_steps, device)
    groups = modality_groups(metadata)
    channel_weights = tensors["channel_weights"]
    fold_rows = []
    best_score = float("inf")
    best_epoch = 0
    best_state = None
    patience_left = args.patience

    iterator = range(1, args.epochs + 1)
    if args.progress:
        iterator = tqdm(iterator, desc=f"fold {fold_id}/{args.folds}", leave=False)
    for epoch in iterator:
        train_bce, denoise = fold_epoch(
            model=model,
            optimizer=optimizer,
            supervised_loader=supervised_loader,
            auxiliary_loader=auxiliary_loader,
            tensors=tensors,
            alpha_bars=alpha_bars,
            groups=groups,
            channel_weights=channel_weights,
            criterion=criterion,
            args=args,
            device=device,
        )
        val_pred = predict_day_indices(model, tensors["x"], tensors["mask"], tensors["subject_idx"], train_day_idx[val_rows], args.batch_size, device)
        val_score, val_targets = average_log_loss(train_y.iloc[val_rows], val_pred)
        fold_rows.append(
            {
                "fold": fold_id,
                "epoch": epoch,
                "train_bce": train_bce,
                "denoise_loss": denoise,
                "val_avg_log_loss": val_score,
                **{f"val_{target}": value for target, value in val_targets.items()},
            }
        )
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
    pred = predict_day_indices(model, tensors["x"], tensors["mask"], tensors["subject_idx"], train_day_idx[val_rows], args.batch_size, device)
    score, per_target = average_log_loss(train_y.iloc[val_rows], pred)
    fold_report = {
        "fold": fold_id,
        "train_rows": int(len(train_rows)),
        "valid_rows": int(len(val_rows)),
        "auxiliary_days": int(len(aux_indices)),
        "best_epoch": int(best_epoch),
        "best_val_avg_log_loss": float(best_score),
        "final_val_avg_log_loss": float(score),
        "per_target": per_target,
        "checkpoint_load": load_info,
    }
    return pred, fold_report, {"training_log": fold_rows}


def train_full_model(
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    train_y: pd.DataFrame,
    tensors: dict[str, torch.Tensor],
    metadata: dict,
    args: argparse.Namespace,
    device: torch.device,
    epochs: int,
) -> tuple[np.ndarray, dict[str, object]]:
    seed_everything(args.seed + 10000)
    model = build_model(args, channels=tensors["x"].shape[-1], n_subjects=int(tensors["n_subjects"].item())).to(device)
    load_info = load_encoder_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)

    y_all = train_y[TARGET_COLUMNS].to_numpy(dtype=np.float32)
    pos_weight = positive_weight_tensor(y_all, args.pos_weight_mode, device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = make_optimizer(model, args)
    supervised_loader = DataLoader(
        TensorDataset(torch.from_numpy(train_day_idx.astype(np.int64).copy()), torch.from_numpy(y_all.copy())),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    aux_indices = np.unique(np.concatenate([train_day_idx, sample_day_idx]).astype(np.int64))
    auxiliary_loader = DataLoader(TensorDataset(torch.from_numpy(aux_indices)), batch_size=args.batch_size, shuffle=True, drop_last=False)
    alpha_bars = diffusion_schedule(args.diffusion_steps, device)
    groups = modality_groups(metadata)
    channel_weights = tensors["channel_weights"]
    log_rows = []
    iterator = range(1, epochs + 1)
    if args.progress:
        iterator = tqdm(iterator, desc="full model", leave=False)
    for epoch in iterator:
        train_bce, denoise = fold_epoch(
            model=model,
            optimizer=optimizer,
            supervised_loader=supervised_loader,
            auxiliary_loader=auxiliary_loader,
            tensors=tensors,
            alpha_bars=alpha_bars,
            groups=groups,
            channel_weights=channel_weights,
            criterion=criterion,
            args=args,
            device=device,
        )
        log_rows.append({"epoch": epoch, "train_bce": train_bce, "denoise_loss": denoise})
    pred = predict_day_indices(model, tensors["x"], tensors["mask"], tensors["subject_idx"], sample_day_idx, args.batch_size, device)
    report = {
        "epochs": int(epochs),
        "auxiliary_days": int(len(aux_indices)),
        "training_log": log_rows,
        "checkpoint_load": load_info,
    }
    return pred, report


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
    oof.to_csv(output_dir / "oof_supervised_diffusion_finetune.csv", index=False)

    submission = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        submission[target] = np.clip(test_pred[:, i], EPS, 1.0 - EPS)
    submission.to_csv(output_dir / "submission_supervised_diffusion_finetune.csv", index=False)

    fold_df = pd.DataFrame(fold_reports)
    fold_df.to_csv(output_dir / "fold_scores.csv", index=False)
    train_log_df = pd.concat(
        [pd.DataFrame(item["training_log"]) for item in training_logs],
        ignore_index=True,
    )
    train_log_df.to_csv(output_dir / "training_log.csv", index=False)

    score = {"name": "supervised_diffusion_finetune", "avg_log_loss": avg, **per_target}
    pd.DataFrame([score]).to_csv(output_dir / "score.csv", index=False)
    report = {
        "score": score,
        "folds": fold_reports,
        "full_model": full_report,
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Supervised diffusion fine-tune",
        "",
        f"- Average log-loss: `{avg:.6f}`",
        f"- Auxiliary days in OOF folds: `{args.auxiliary_days}`",
        f"- Init checkpoint: `{args.init_checkpoint or ''}`",
        "",
        "## Target scores",
        "",
        "| target | log_loss |",
        "| --- | --- |",
    ]
    for target in TARGET_COLUMNS:
        lines.append(f"| {target} | {per_target[target]:.6f} |")
    lines.extend(
        [
            "",
            "## Fold scores",
            "",
            "| fold | valid_rows | auxiliary_days | best_epoch | final_val_avg_log_loss |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in fold_reports:
        lines.append(
            f"| {row['fold']} | {row['valid_rows']} | {row['auxiliary_days']} | "
            f"{row['best_epoch']} | {row['final_val_avg_log_loss']:.6f} |"
        )
    (output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune the diffusion day encoder with a supervised label head.")
    parser.add_argument("--input-dir", default="outputs/diffusion_encoder")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/supervised_diffusion_finetune")
    parser.add_argument("--init-checkpoint", default="outputs/diffusion_encoder/checkpoints/day_diffusion_encoder.pt")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-folds", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--full-epochs", type=int, default=0)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--min-delta", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=96)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--latent-dim", type=int, default=64)
    parser.add_argument("--layers", type=int, default=3)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--head-dropout", type=float, default=0.2)
    parser.add_argument("--head-hidden", type=int, default=0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--encoder-lr-scale", type=float, default=0.25)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--diffusion-steps", type=int, default=100)
    parser.add_argument("--entry-dropout", type=float, default=0.08)
    parser.add_argument("--hour-dropout-prob", type=float, default=0.35)
    parser.add_argument("--modality-dropout-prob", type=float, default=0.30)
    parser.add_argument("--supervised-weight", type=float, default=1.0)
    parser.add_argument("--denoise-weight", type=float, default=0.05)
    parser.add_argument("--auxiliary-days", choices=["train_sample", "train_only", "all"], default="train_sample")
    parser.add_argument("--pos-weight-mode", choices=["none", "train"], default="none")
    parser.add_argument("--subject-mode", choices=["id", "zero"], default="id")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--progress", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    x_np, mask_np, day_index, metadata = load_tensor_dataset(Path(args.input_dir))
    train, sample, train_day_idx, sample_day_idx = align_rows(day_index, Path(args.train_path), Path(args.sample_path))
    subject_idx_np, subject_map, n_subjects = build_subject_indices(day_index, args.subject_mode)
    device = choose_device(args.device)
    x = torch.from_numpy(x_np).to(device)
    mask = torch.from_numpy(mask_np).to(device)
    subject_idx = torch.from_numpy(subject_idx_np).to(device)
    observed_rate = mask.mean(dim=(0, 1)).clamp_min(1e-3)
    channel_weights = (1.0 / torch.sqrt(observed_rate)).clamp(0.5, 5.0)
    channel_weights = channel_weights / channel_weights.mean()
    tensors = {
        "x": x,
        "mask": mask,
        "subject_idx": subject_idx,
        "channel_weights": channel_weights,
        "n_subjects": torch.tensor(n_subjects),
    }

    folds = make_subject_time_folds(train, args.folds)
    if args.max_folds > 0:
        folds = folds[: args.max_folds]
    oof_pred = np.full((len(train), len(TARGET_COLUMNS)), np.nan, dtype=float)
    fold_reports = []
    training_logs = []
    for fold_id, (train_rows, val_rows) in enumerate(folds, start=1):
        pred, fold_report, train_log = train_one_fold(
            fold_id=fold_id,
            train_rows=train_rows,
            val_rows=val_rows,
            train_day_idx=train_day_idx,
            sample_day_idx=sample_day_idx,
            train_y=train,
            tensors=tensors,
            metadata=metadata,
            args=args,
            device=device,
        )
        oof_pred[val_rows] = pred
        fold_reports.append(fold_report)
        training_logs.append(train_log)
        print(f"fold={fold_id} score={fold_report['final_val_avg_log_loss']:.6f} best_epoch={fold_report['best_epoch']}")

    if np.isnan(oof_pred).any():
        missing_rows = int(np.isnan(oof_pred).any(axis=1).sum())
        raise ValueError(f"OOF predictions are incomplete; missing rows={missing_rows}. Use all folds for scoring.")

    if args.full_epochs > 0:
        full_epochs = args.full_epochs
    else:
        best_epochs = [int(row["best_epoch"]) for row in fold_reports if int(row["best_epoch"]) > 0]
        full_epochs = int(np.median(best_epochs)) if best_epochs else args.epochs
    test_pred, full_report = train_full_model(
        train_day_idx=train_day_idx,
        sample_day_idx=sample_day_idx,
        train_y=train,
        tensors=tensors,
        metadata=metadata,
        args=args,
        device=device,
        epochs=full_epochs,
    )
    full_report["subject_map"] = subject_map
    write_outputs(output_dir, train, sample, oof_pred, test_pred, fold_reports, training_logs, full_report, args)
    avg, per_target = average_log_loss(train, oof_pred)
    print(f"avg_log_loss={avg:.6f}")
    print("target_scores=" + json.dumps(per_target, sort_keys=True))
    print(f"saved: {output_dir / 'submission_supervised_diffusion_finetune.csv'}")


if __name__ == "__main__":
    main()
