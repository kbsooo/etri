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

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from train_pyramid_supervised_alignment import (  # noqa: E402
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    PyramidResidualClassifier,
    average_log_loss,
    choose_device,
    load_checkpoint,
    load_dataset,
    make_model,
    make_optimizer,
    make_subject_time_folds,
    model_inputs,
    normalize_keys,
    reconstruction_loss,
    safe_logit,
    subject_prior_prob,
    tensor_batch,
    align_rows,
)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def prediction_matrix(df: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([df[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(df: pd.DataFrame) -> np.ndarray:
    return np.clip(df[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def load_teacher_predictions(
    teacher_oof_path: str,
    teacher_submission_path: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
) -> tuple[np.ndarray | None, np.ndarray | None]:
    if not teacher_oof_path or not teacher_submission_path:
        return None, None
    oof_path = Path(teacher_oof_path)
    sub_path = Path(teacher_submission_path)
    if not oof_path.exists() or not sub_path.exists():
        return None, None
    oof = normalize_keys(pd.read_csv(oof_path))
    submission = normalize_keys(pd.read_csv(sub_path))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError(f"Teacher OOF keys do not match train keys: {oof_path}")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError(f"Teacher submission keys do not match sample keys: {sub_path}")
    return prediction_matrix(oof), submission_matrix(submission)


def pairwise_label_similarity(y: torch.Tensor) -> torch.Tensor:
    centered = y - y.mean(dim=1, keepdim=True)
    normed = F.normalize(centered, dim=1)
    cosine = normed @ normed.T
    hamming = 1.0 - torch.cdist(y, y, p=1) / y.shape[1]
    sim = 0.5 * (cosine + 1.0) * 0.5 + 0.5 * hamming
    return torch.clamp(sim, 0.0, 1.0)


def similarity_contrastive_loss(latent: torch.Tensor, y: torch.Tensor, temperature: float, min_positive: float) -> torch.Tensor:
    if latent.shape[0] < 3:
        return latent.sum() * 0.0
    z = F.normalize(latent, dim=1)
    logits = z @ z.T / temperature
    logits = logits - torch.eye(logits.shape[0], device=logits.device) * 1e4
    weights = pairwise_label_similarity(y)
    weights = weights * (1.0 - torch.eye(weights.shape[0], device=weights.device))
    weights = torch.where(weights >= min_positive, weights, torch.zeros_like(weights))
    denom = weights.sum(dim=1, keepdim=True)
    valid = denom.squeeze(1) > 0
    if not valid.any():
        return latent.sum() * 0.0
    target = weights / denom.clamp_min(1e-6)
    log_prob = F.log_softmax(logits, dim=1)
    return -(target[valid] * log_prob[valid]).sum(dim=1).mean()


def teacher_kl_loss(logits: torch.Tensor, teacher_prob: torch.Tensor, temperature: float) -> torch.Tensor:
    teacher = torch.clamp(teacher_prob, EPS, 1.0 - EPS)
    scaled_logits = logits / temperature
    scaled_teacher = torch.sigmoid(safe_logit_tensor(teacher) / temperature)
    return F.binary_cross_entropy_with_logits(scaled_logits, scaled_teacher)


def safe_logit_tensor(values: torch.Tensor) -> torch.Tensor:
    values = torch.clamp(values, EPS, 1.0 - EPS)
    return torch.log(values / (1.0 - values))


@torch.no_grad()
def predict_and_encode(
    model: PyramidResidualClassifier,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    day_indices: np.ndarray,
    base_logits: np.ndarray,
    batch_size: int,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    preds = []
    latents = []
    loader = DataLoader(
        TensorDataset(torch.from_numpy(day_indices.astype(np.int64)), torch.from_numpy(base_logits.astype(np.float32))),
        batch_size=batch_size,
        shuffle=False,
    )
    for day_idx, base_cpu in loader:
        x, mask, sf, events, event_mask, proto, context, _, _ = model_inputs(
            model_data, day_idx, slot_features, device, False, argparse.Namespace()
        )
        logits, _, out = model(x, mask, sf, events, event_mask, proto, context, base_cpu.to(device))
        preds.append(torch.sigmoid(logits).detach().cpu().numpy())
        latents.append(out["latent"].detach().cpu().numpy())
    return np.clip(np.concatenate(preds, axis=0), EPS, 1.0 - EPS), np.concatenate(latents, axis=0)


def train_epoch(
    model: PyramidResidualClassifier,
    optimizer: torch.optim.Optimizer,
    supervised_loader: DataLoader,
    auxiliary_loader: DataLoader,
    pseudo_loader: DataLoader | None,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    slot_features: torch.Tensor,
    channel_weights: torch.Tensor,
    args: argparse.Namespace,
    device: torch.device,
) -> dict[str, float]:
    model.train()
    aux_iter = iter(auxiliary_loader)
    pseudo_iter = iter(pseudo_loader) if pseudo_loader is not None else None
    sup_losses: list[float] = []
    contrast_losses: list[float] = []
    denoise_losses: list[float] = []
    pseudo_losses: list[float] = []
    delta_losses: list[float] = []

    for day_idx_cpu, y_cpu, base_cpu, teacher_cpu in supervised_loader:
        day_idx = day_idx_cpu.to(device)
        y = y_cpu.to(device)
        base_logits = base_cpu.to(device)
        teacher = teacher_cpu.to(device)
        x, mask, sf, events, event_mask, proto, context, _, _ = model_inputs(
            model_data, day_idx, slot_features, device, args.supervised_corruption, args
        )
        logits, label_delta, out = model(x, mask, sf, events, event_mask, proto, context, base_logits)
        supervised = F.binary_cross_entropy_with_logits(logits, y)
        contrast = similarity_contrastive_loss(out["latent"], y, args.contrast_temperature, args.min_positive_similarity)
        teacher_loss = teacher_kl_loss(logits, teacher, args.teacher_temperature) if args.teacher_weight > 0 else supervised.detach() * 0.0
        delta_penalty = label_delta.pow(2).mean()

        pseudo_loss = supervised.detach() * 0.0
        if pseudo_iter is not None and args.pseudo_weight > 0:
            try:
                pseudo_day_idx_cpu, pseudo_base_cpu, pseudo_teacher_cpu = next(pseudo_iter)
            except StopIteration:
                pseudo_iter = iter(pseudo_loader)
                pseudo_day_idx_cpu, pseudo_base_cpu, pseudo_teacher_cpu = next(pseudo_iter)
            pseudo_day_idx = pseudo_day_idx_cpu.to(device)
            px, pmask, psf, pevents, pevent_mask, pproto, pcontext, _, _ = model_inputs(
                model_data, pseudo_day_idx, slot_features, device, args.supervised_corruption, args
            )
            pseudo_logits, _, _ = model(px, pmask, psf, pevents, pevent_mask, pproto, pcontext, pseudo_base_cpu.to(device))
            pseudo_loss = teacher_kl_loss(pseudo_logits, pseudo_teacher_cpu.to(device), args.teacher_temperature)

        denoise_loss = supervised.detach() * 0.0
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
            delta_recon = reconstruction_loss(aux_out["delta_pred"], clean_delta, actual_mask, hidden, channel_weights)
            denoise_loss = actual_loss + args.delta_recon_weight * delta_recon

        loss = (
            supervised
            + args.contrast_weight * contrast
            + args.teacher_weight * teacher_loss
            + args.pseudo_weight * pseudo_loss
            + args.denoise_weight * denoise_loss
            + args.residual_l2 * delta_penalty
        )
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
        optimizer.step()

        sup_losses.append(float(supervised.detach().cpu()))
        contrast_losses.append(float(contrast.detach().cpu()))
        denoise_losses.append(float(denoise_loss.detach().cpu()))
        pseudo_losses.append(float(pseudo_loss.detach().cpu()))
        delta_losses.append(float(delta_penalty.detach().cpu()))
    return {
        "supervised_loss": float(np.mean(sup_losses)),
        "contrast_loss": float(np.mean(contrast_losses)),
        "denoise_loss": float(np.mean(denoise_losses)),
        "pseudo_loss": float(np.mean(pseudo_losses)),
        "delta_penalty": float(np.mean(delta_losses)),
    }


def auxiliary_indices(mode: str, model_data: dict[str, np.ndarray | pd.DataFrame | dict], train_day_idx: np.ndarray, train_rows: np.ndarray, sample_day_idx: np.ndarray) -> np.ndarray:
    if mode == "train_only":
        return np.unique(train_day_idx[train_rows])
    if mode == "train_sample":
        return np.unique(np.concatenate([train_day_idx[train_rows], sample_day_idx]))
    if mode == "all":
        return np.arange(model_data["x"].shape[0], dtype=np.int64)
    raise ValueError(f"Unknown auxiliary days: {mode}")


def make_channel_weights(model_data: dict[str, np.ndarray | pd.DataFrame | dict], device: torch.device) -> torch.Tensor:
    observed_rate = model_data["actual_mask"].mean(axis=(0, 1)).clip(1e-3, None)
    channel_weights = torch.from_numpy((1.0 / np.sqrt(observed_rate)).clip(0.5, 5.0).astype(np.float32)).to(device)
    return channel_weights / channel_weights.mean().clamp_min(1e-6)


def train_one_fold(
    fold_id: int,
    train_rows: np.ndarray,
    val_rows: np.ndarray,
    train: pd.DataFrame,
    train_day_idx: np.ndarray,
    sample: pd.DataFrame,
    sample_day_idx: np.ndarray,
    teacher_train: np.ndarray | None,
    teacher_sample: np.ndarray | None,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, dict[str, object], dict[str, list[dict[str, float]]]]:
    seed_everything(args.seed + fold_id)
    model = make_model(args, model_data["metadata"]).to(device)
    load_info = load_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)
    optimizer = make_optimizer(model, args)
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    channel_weights = make_channel_weights(model_data, device)

    prior_train = subject_prior_prob(train.iloc[train_rows], train.iloc[train_rows], args.prior_alpha)
    prior_val = subject_prior_prob(train.iloc[train_rows], train.iloc[val_rows], args.prior_alpha)
    prior_sample = subject_prior_prob(train.iloc[train_rows], sample, args.prior_alpha)
    y = train[TARGET_COLUMNS].to_numpy(np.float32)
    teacher_fold_train = teacher_train[train_rows].astype(np.float32) if teacher_train is not None else y[train_rows].astype(np.float32)

    supervised_loader = DataLoader(
        TensorDataset(
            torch.from_numpy(train_day_idx[train_rows].astype(np.int64).copy()),
            torch.from_numpy(y[train_rows].copy()),
            torch.from_numpy(safe_logit(prior_train)),
            torch.from_numpy(teacher_fold_train.copy()),
        ),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    aux = auxiliary_indices(args.auxiliary_days, model_data, train_day_idx, train_rows, sample_day_idx)
    auxiliary_loader = DataLoader(TensorDataset(torch.from_numpy(aux)), batch_size=args.batch_size, shuffle=True)
    pseudo_loader = None
    if teacher_sample is not None and args.pseudo_weight > 0:
        pseudo_loader = DataLoader(
            TensorDataset(
                torch.from_numpy(sample_day_idx.astype(np.int64).copy()),
                torch.from_numpy(safe_logit(prior_sample)),
                torch.from_numpy(teacher_sample.astype(np.float32).copy()),
            ),
            batch_size=args.batch_size,
            shuffle=True,
        )

    best_score = float("inf")
    best_state = None
    best_epoch = 0
    patience_left = args.patience
    log_rows: list[dict[str, float]] = []
    iterator = range(1, args.epochs + 1)
    if args.progress:
        iterator = tqdm(iterator, desc=f"fold {fold_id}/{args.folds}", leave=False)
    for epoch in iterator:
        stats = train_epoch(model, optimizer, supervised_loader, auxiliary_loader, pseudo_loader, model_data, slot_features, channel_weights, args, device)
        val_pred, _ = predict_and_encode(model, model_data, train_day_idx[val_rows], safe_logit(prior_val), args.batch_size, device)
        val_score, val_targets = average_log_loss(train.iloc[val_rows], val_pred)
        row = {"fold": fold_id, "epoch": epoch, "val_avg_log_loss": val_score, **stats, **{f"val_{k}": v for k, v in val_targets.items()}}
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
    pred, latent = predict_and_encode(model, model_data, train_day_idx[val_rows], safe_logit(prior_val), args.batch_size, device)
    score, per_target = average_log_loss(train.iloc[val_rows], pred)
    report = {
        "fold": fold_id,
        "train_rows": int(len(train_rows)),
        "valid_rows": int(len(val_rows)),
        "auxiliary_days": int(len(aux)),
        "best_epoch": int(best_epoch),
        "best_val_avg_log_loss": float(best_score),
        "final_val_avg_log_loss": float(score),
        "per_target": per_target,
        "checkpoint_load": load_info,
    }
    return pred, latent, report, {"training_log": log_rows}


def train_full_model(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    teacher_train: np.ndarray | None,
    teacher_sample: np.ndarray | None,
    model_data: dict[str, np.ndarray | pd.DataFrame | dict],
    args: argparse.Namespace,
    device: torch.device,
    epochs: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, object]]:
    seed_everything(args.seed + 10000)
    model = make_model(args, model_data["metadata"]).to(device)
    load_info = load_checkpoint(model, Path(args.init_checkpoint) if args.init_checkpoint else None)
    optimizer = make_optimizer(model, args)
    slot_features = torch.from_numpy(model_data["slot_features"]).to(device=device, dtype=torch.float32)
    channel_weights = make_channel_weights(model_data, device)
    prior_train = subject_prior_prob(train, train, args.prior_alpha)
    prior_sample = subject_prior_prob(train, sample, args.prior_alpha)
    y = train[TARGET_COLUMNS].to_numpy(np.float32)
    teacher_full = teacher_train.astype(np.float32) if teacher_train is not None else y.astype(np.float32)
    supervised_loader = DataLoader(
        TensorDataset(
            torch.from_numpy(train_day_idx.astype(np.int64).copy()),
            torch.from_numpy(y.copy()),
            torch.from_numpy(safe_logit(prior_train)),
            torch.from_numpy(teacher_full.copy()),
        ),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=False,
    )
    aux = np.unique(np.concatenate([train_day_idx, sample_day_idx]).astype(np.int64))
    auxiliary_loader = DataLoader(TensorDataset(torch.from_numpy(aux)), batch_size=args.batch_size, shuffle=True)
    pseudo_loader = None
    if teacher_sample is not None and args.pseudo_weight > 0:
        pseudo_loader = DataLoader(
            TensorDataset(
                torch.from_numpy(sample_day_idx.astype(np.int64).copy()),
                torch.from_numpy(safe_logit(prior_sample)),
                torch.from_numpy(teacher_sample.astype(np.float32).copy()),
            ),
            batch_size=args.batch_size,
            shuffle=True,
        )
    log_rows = []
    for _ in range(epochs):
        log_rows.append(train_epoch(model, optimizer, supervised_loader, auxiliary_loader, pseudo_loader, model_data, slot_features, channel_weights, args, device))
    sample_pred, sample_latent = predict_and_encode(model, model_data, sample_day_idx, safe_logit(prior_sample), args.batch_size, device)
    train_pred, train_latent = predict_and_encode(model, model_data, train_day_idx, safe_logit(prior_train), args.batch_size, device)
    report = {"epochs": int(epochs), "training_log": log_rows, "checkpoint_load": load_info}
    return sample_pred, train_latent, sample_latent, report


def write_latent_table(path: Path, day_index: pd.DataFrame, latents_by_day: np.ndarray) -> None:
    z_cols = [f"z_{i:03d}" for i in range(latents_by_day.shape[1])]
    z_df = pd.DataFrame(latents_by_day, columns=z_cols)
    pd.concat([day_index.reset_index(drop=True), z_df], axis=1).to_parquet(path, index=False)


def write_outputs(
    output_dir: Path,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    day_index: pd.DataFrame,
    train_day_idx: np.ndarray,
    sample_day_idx: np.ndarray,
    oof_pred: np.ndarray,
    oof_latent_rows: np.ndarray,
    full_train_latent: np.ndarray,
    full_sample_latent: np.ndarray,
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
    oof.to_csv(output_dir / "oof_label_aligned_encoder.csv", index=False)

    submission = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        submission[target] = np.clip(test_pred[:, i], EPS, 1.0 - EPS)
    submission.to_csv(output_dir / "submission_label_aligned_encoder.csv", index=False)

    full_latents_by_day = np.zeros((len(day_index), full_train_latent.shape[1]), dtype=np.float32)
    full_latents_by_day[train_day_idx] = full_train_latent
    full_latents_by_day[sample_day_idx] = full_sample_latent
    write_latent_table(output_dir / "day_latents_full.parquet", day_index, full_latents_by_day)

    oof_latents_by_day = full_latents_by_day.copy()
    oof_latents_by_day[train_day_idx] = oof_latent_rows
    write_latent_table(output_dir / "day_latents_oof_train_full_test.parquet", day_index, oof_latents_by_day)

    pd.DataFrame(fold_reports).to_csv(output_dir / "fold_scores.csv", index=False)
    pd.concat([pd.DataFrame(item["training_log"]) for item in training_logs], ignore_index=True).to_csv(
        output_dir / "training_log.csv", index=False
    )
    score = {"name": "pyramid_label_aligned_encoder", "avg_log_loss": avg, **per_target}
    pd.DataFrame([score]).to_csv(output_dir / "score.csv", index=False)
    report = {
        "score": score,
        "folds": fold_reports,
        "full_model": full_report,
        "latent_paths": {
            "full": str(output_dir / "day_latents_full.parquet"),
            "oof_train_full_test": str(output_dir / "day_latents_oof_train_full_test.parquet"),
        },
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Pyramid label-aligned encoder",
        "",
        f"- Average log-loss: `{avg:.6f}`",
        f"- Init checkpoint: `{args.init_checkpoint}`",
        f"- Teacher OOF: `{args.teacher_oof}`",
        f"- Teacher submission: `{args.teacher_submission}`",
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
    parser = argparse.ArgumentParser(description="Train a label-aligned Pyramid Encoder with supervised contrastive and teacher consistency objectives.")
    parser.add_argument("--input-dir", default="outputs/encoder_day_pyramid")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/pyramid_label_aligned_encoder_v1")
    parser.add_argument("--init-checkpoint", default="outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt")
    parser.add_argument("--teacher-oof", default="")
    parser.add_argument("--teacher-submission", default="")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-folds", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=45)
    parser.add_argument("--full-epochs", type=int, default=0)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--min-delta", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--d-model", type=int, default=96)
    parser.add_argument("--latent-dim", type=int, default=128)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--encoder-dropout", type=float, default=0.15)
    parser.add_argument("--head-dropout", type=float, default=0.25)
    parser.add_argument("--head-hidden", type=int, default=64)
    parser.add_argument("--max-delta", type=float, default=0.9)
    parser.add_argument("--prior-alpha", type=float, default=10.0)
    parser.add_argument("--lr", type=float, default=3.5e-4)
    parser.add_argument("--encoder-lr-scale", type=float, default=0.015)
    parser.add_argument("--weight-decay", type=float, default=2e-4)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--residual-l2", type=float, default=0.06)
    parser.add_argument("--contrast-weight", type=float, default=0.08)
    parser.add_argument("--contrast-temperature", type=float, default=0.25)
    parser.add_argument("--min-positive-similarity", type=float, default=0.55)
    parser.add_argument("--teacher-weight", type=float, default=0.0)
    parser.add_argument("--pseudo-weight", type=float, default=0.0)
    parser.add_argument("--teacher-temperature", type=float, default=1.5)
    parser.add_argument("--denoise-weight", type=float, default=0.015)
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
    teacher_train, teacher_sample = load_teacher_predictions(args.teacher_oof, args.teacher_submission, train, sample)
    device = choose_device(args.device)
    folds = make_subject_time_folds(train, args.folds)
    if args.max_folds > 0:
        folds = folds[: args.max_folds]
    oof_pred = np.full((len(train), len(TARGET_COLUMNS)), np.nan, dtype=float)
    oof_latent_rows = np.full((len(train), args.latent_dim), np.nan, dtype=np.float32)
    fold_reports = []
    training_logs = []
    for fold_id, (train_rows, val_rows) in enumerate(folds, start=1):
        pred, latent, fold_report, train_log = train_one_fold(
            fold_id,
            train_rows,
            val_rows,
            train,
            train_day_idx,
            sample,
            sample_day_idx,
            teacher_train,
            teacher_sample,
            model_data,
            args,
            device,
        )
        oof_pred[val_rows] = pred
        oof_latent_rows[val_rows] = latent
        fold_reports.append(fold_report)
        training_logs.append(train_log)
        print(f"fold={fold_id} score={fold_report['final_val_avg_log_loss']:.6f} best_epoch={fold_report['best_epoch']}")
    if np.isnan(oof_pred).any() or np.isnan(oof_latent_rows).any():
        raise ValueError("OOF predictions or latents are incomplete. Use all folds for scoring/export.")
    if args.full_epochs > 0:
        full_epochs = args.full_epochs
    else:
        best_epochs = [int(row["best_epoch"]) for row in fold_reports if int(row["best_epoch"]) > 0]
        full_epochs = int(np.median(best_epochs)) if best_epochs else args.epochs
    test_pred, full_train_latent, full_sample_latent, full_report = train_full_model(
        train,
        sample,
        train_day_idx,
        sample_day_idx,
        teacher_train,
        teacher_sample,
        model_data,
        args,
        device,
        full_epochs,
    )
    write_outputs(
        output_dir,
        train,
        sample,
        model_data["day_index"],
        train_day_idx,
        sample_day_idx,
        oof_pred,
        oof_latent_rows,
        full_train_latent,
        full_sample_latent,
        test_pred,
        fold_reports,
        training_logs,
        full_report,
        args,
    )
    avg, per_target = average_log_loss(train, oof_pred)
    print(f"avg_log_loss={avg:.6f}")
    print("target_scores=" + json.dumps(per_target, sort_keys=True))
    print(f"saved: {output_dir / 'submission_label_aligned_encoder.csv'}")


if __name__ == "__main__":
    main()
