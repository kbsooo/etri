from __future__ import annotations

import argparse
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
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etri_diffusion.model import DayDenoisingDiffusionEncoder


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


def load_dataset(input_dir: Path) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, dict]:
    arr = np.load(input_dir / "hourly_tensor.npz")
    day_index = pd.read_csv(input_dir / "day_index.csv")
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
    return arr["x"].astype(np.float32), arr["mask"].astype(np.float32), day_index, metadata


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


def build_temporal_pairs(day_index: pd.DataFrame, max_offset: int) -> np.ndarray:
    pairs: list[tuple[int, int]] = []
    ordered = day_index.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    for _, group in ordered.groupby("subject_id", sort=False):
        idx = group["_idx"].to_numpy(dtype=np.int64)
        for offset in range(1, max_offset + 1):
            if len(idx) <= offset:
                continue
            pairs.extend((int(a), int(b)) for a, b in zip(idx[:-offset], idx[offset:]))
            pairs.extend((int(b), int(a)) for a, b in zip(idx[:-offset], idx[offset:]))
    if not pairs:
        raise ValueError("No temporal neighbor pairs could be built")
    return np.asarray(pairs, dtype=np.int64)


def contrastive_loss(anchor_z: torch.Tensor, positive_z: torch.Tensor, temperature: float) -> torch.Tensor:
    anchor = F.normalize(anchor_z, dim=1)
    positive = F.normalize(positive_z, dim=1)
    logits = anchor @ positive.T / temperature
    labels = torch.arange(anchor.shape[0], device=anchor.device)
    return 0.5 * (F.cross_entropy(logits, labels) + F.cross_entropy(logits.T, labels))


def encode_clean(
    model: DayDenoisingDiffusionEncoder,
    x: torch.Tensor,
    mask: torch.Tensor,
    subject_idx: torch.Tensor,
) -> torch.Tensor:
    t0 = torch.zeros(x.shape[0], device=x.device, dtype=torch.long)
    _, latent = model(x * mask, mask, subject_idx, t0)
    return latent


def export_latents(
    model: DayDenoisingDiffusionEncoder,
    x: torch.Tensor,
    mask: torch.Tensor,
    subject_idx: torch.Tensor,
    day_index: pd.DataFrame,
    output_dir: Path,
    batch_size: int,
) -> None:
    model.eval()
    latents = []
    loader = DataLoader(TensorDataset(x, mask, subject_idx), batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for xb, mb, sb in loader:
            latents.append(encode_clean(model, xb, mb, sb).cpu().numpy())
    z = np.concatenate(latents, axis=0)
    np.save(output_dir / "day_latents.npy", z)
    latent_df = day_index.copy()
    for i in range(z.shape[1]):
        latent_df[f"z_{i:02d}"] = z[:, i]
    latent_df.to_parquet(output_dir / "day_latents.parquet", index=False)


def train(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    x_np, mask_np, day_index, metadata = load_dataset(input_dir)
    device = choose_device(args.device)
    x = torch.from_numpy(x_np).to(device)
    mask = torch.from_numpy(mask_np).to(device)
    pairs = build_temporal_pairs(day_index, args.max_positive_offset)

    subjects = sorted(day_index["subject_id"].unique().tolist())
    subject_map = {sid: i for i, sid in enumerate(subjects)}
    if args.subject_mode == "zero":
        subject_idx_np = np.zeros(len(day_index), dtype=np.int64)
        n_subjects = 1
    else:
        subject_idx_np = day_index["subject_id"].map(subject_map).to_numpy(dtype=np.int64).copy()
        n_subjects = len(subjects)
    subject_idx = torch.from_numpy(subject_idx_np).to(device)

    observed_rate = mask.mean(dim=(0, 1)).clamp_min(1e-3)
    channel_weights = (1.0 / torch.sqrt(observed_rate)).clamp(0.5, 5.0)
    channel_weights = channel_weights / channel_weights.mean()
    groups = modality_groups(metadata)
    alpha_bars = diffusion_schedule(args.diffusion_steps, device)

    model = DayDenoisingDiffusionEncoder(
        channels=x.shape[-1],
        n_subjects=n_subjects,
        d_model=args.d_model,
        latent_dim=args.latent_dim,
        n_layers=args.layers,
        n_heads=args.heads,
        dropout=args.dropout,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(pairs[:, 0]), torch.from_numpy(pairs[:, 1])),
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
    )
    log_rows = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        denoise_losses: list[float] = []
        contrast_losses: list[float] = []
        progress = tqdm(loader, desc=f"epoch {epoch}/{args.epochs}", leave=False)
        for anchor_idx_cpu, positive_idx_cpu in progress:
            anchor_idx = anchor_idx_cpu.to(device)
            positive_idx = positive_idx_cpu.to(device)
            batch_idx = torch.cat([anchor_idx, positive_idx], dim=0)

            xb = x[batch_idx]
            mb = mask[batch_idx]
            sb = subject_idx[batch_idx]
            x_cond, cond_mask, noise, t = corrupt_batch(
                xb,
                mb,
                alpha_bars,
                groups,
                entry_dropout=args.entry_dropout,
                hour_dropout_prob=args.hour_dropout_prob,
                modality_dropout_prob=args.modality_dropout_prob,
            )
            pred_noise, _ = model(x_cond, cond_mask, sb, t)
            denoise = weighted_noise_loss(pred_noise, noise, mb, channel_weights)

            anchor_z = encode_clean(model, x[anchor_idx], mask[anchor_idx], subject_idx[anchor_idx])
            positive_z = encode_clean(model, x[positive_idx], mask[positive_idx], subject_idx[positive_idx])
            contrast = contrastive_loss(anchor_z, positive_z, args.temperature)
            loss = args.denoise_weight * denoise + args.contrast_weight * contrast

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            optimizer.step()

            denoise_losses.append(float(denoise.detach().cpu()))
            contrast_losses.append(float(contrast.detach().cpu()))
            progress.set_postfix(
                denoise=np.mean(denoise_losses[-10:]),
                contrast=np.mean(contrast_losses[-10:]),
            )

        row = {
            "epoch": epoch,
            "denoise_loss": float(np.mean(denoise_losses)),
            "contrastive_loss": float(np.mean(contrast_losses)),
            "loss": args.denoise_weight * float(np.mean(denoise_losses))
            + args.contrast_weight * float(np.mean(contrast_losses)),
            "lr": args.lr,
        }
        log_rows.append(row)
        print(
            f"epoch={epoch} denoise={row['denoise_loss']:.6f} "
            f"contrast={row['contrastive_loss']:.6f} loss={row['loss']:.6f}"
        )

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "args": vars(args),
        "metadata": metadata,
        "subject_map": subject_map,
        "subject_mode": args.subject_mode,
        "shape": list(x_np.shape),
        "temporal_pairs": int(len(pairs)),
    }
    torch.save(checkpoint, checkpoint_dir / "temporal_contrastive_encoder.pt")
    pd.DataFrame(log_rows).to_csv(output_dir / "training_log.csv", index=False)
    export_latents(model, x, mask, subject_idx, day_index, output_dir, args.batch_size)
    (output_dir / "training_config.json").write_text(json.dumps(checkpoint["args"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved checkpoint: {checkpoint_dir / 'temporal_contrastive_encoder.pt'}")
    print(f"saved latents: {output_dir / 'day_latents.parquet'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a temporal-neighbor contrastive day encoder for ETRI hourly tensors.")
    parser.add_argument("--input-dir", default="outputs/diffusion_encoder")
    parser.add_argument("--output-dir", default="outputs/temporal_contrastive_encoder")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--d-model", type=int, default=96)
    parser.add_argument("--latent-dim", type=int, default=96)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--diffusion-steps", type=int, default=100)
    parser.add_argument("--entry-dropout", type=float, default=0.08)
    parser.add_argument("--hour-dropout-prob", type=float, default=0.35)
    parser.add_argument("--modality-dropout-prob", type=float, default=0.30)
    parser.add_argument("--temperature", type=float, default=0.15)
    parser.add_argument("--denoise-weight", type=float, default=0.5)
    parser.add_argument("--contrast-weight", type=float, default=0.5)
    parser.add_argument("--max-positive-offset", type=int, default=2)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--subject-mode", choices=["id", "zero"], default="zero")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
