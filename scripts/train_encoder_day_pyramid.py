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
from tqdm import trange

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etri_diffusion.pyramid_model import PyramidDayEncoder


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]


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


def load_dataset(input_dir: Path) -> dict[str, np.ndarray | pd.DataFrame | dict]:
    arr = np.load(input_dir / "encoder_day_pyramid.npz")
    day_index = pd.read_csv(input_dir / "day_index.csv")
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
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


def tensor_batch(values: np.ndarray, indices: np.ndarray, device: torch.device) -> torch.Tensor:
    return torch.from_numpy(values[indices]).to(device=device, dtype=torch.float32)


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
                hidden[row, start : start + length, :] |= actual_mask[row, start : start + length, :] > 0.5
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
    denom = total_weight.sum().clamp_min(1.0)
    return (((pred - target) ** 2) * total_weight).sum() / denom


def make_model(args: argparse.Namespace, metadata: dict) -> PyramidDayEncoder:
    shape = metadata["shape"]
    return PyramidDayEncoder(
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
        dropout=args.dropout,
    )


@torch.no_grad()
def export_latents(
    model: PyramidDayEncoder,
    data: dict[str, np.ndarray | pd.DataFrame | dict],
    output_dir: Path,
    device: torch.device,
    batch_size: int,
) -> None:
    model.eval()
    x = data["x"]
    mask = data["mask"]
    event_tokens = data["event_tokens"]
    event_mask = data["event_mask"]
    prototype_mixture = data["prototype_mixture"]
    day_context = data["day_context"]
    slot_features = torch.from_numpy(data["slot_features"]).to(device=device, dtype=torch.float32)
    latents: list[np.ndarray] = []
    n = x.shape[0]
    for start in range(0, n, batch_size):
        idx = np.arange(start, min(start + batch_size, n), dtype=np.int64)
        out = model(
            tensor_batch(x, idx, device),
            tensor_batch(mask, idx, device),
            slot_features,
            tensor_batch(event_tokens, idx, device),
            tensor_batch(event_mask, idx, device),
            tensor_batch(prototype_mixture, idx, device),
            tensor_batch(day_context, idx, device),
        )
        latents.append(out["latent"].cpu().numpy())
    z = np.concatenate(latents, axis=0)
    np.save(output_dir / "day_latents.npy", z)
    day_index = data["day_index"].copy().reset_index(drop=True)
    z_cols = [f"z_{i:03d}" for i in range(z.shape[1])]
    z_df = pd.DataFrame(z, columns=z_cols)
    pd.concat([day_index, z_df], axis=1).to_parquet(output_dir / "day_latents.parquet", index=False)


def train(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    data = load_dataset(input_dir)
    metadata = data["metadata"]
    base_channels = int(metadata["shape"]["base_channels"])
    day_index = data["day_index"]
    pairs = build_temporal_pairs(day_index, args.max_positive_offset)
    rng = np.random.default_rng(args.seed)
    device = choose_device(args.device)
    model = make_model(args, metadata).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(args.epochs * args.steps_per_epoch, 1))
    slot_features = torch.from_numpy(data["slot_features"]).to(device=device, dtype=torch.float32)

    observed_rate = data["actual_mask"].mean(axis=(0, 1)).clip(1e-3, None)
    channel_weights = torch.from_numpy((1.0 / np.sqrt(observed_rate)).clip(0.5, 5.0).astype(np.float32)).to(device)
    channel_weights = channel_weights / channel_weights.mean().clamp_min(1e-6)

    log_rows = []
    best_loss = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        losses: list[float] = []
        recon_losses: list[float] = []
        delta_losses: list[float] = []
        contrast_losses: list[float] = []
        progress = trange(args.steps_per_epoch, desc=f"epoch {epoch}/{args.epochs}", leave=False)
        for _ in progress:
            pair_idx = rng.integers(0, len(pairs), size=args.batch_pairs)
            anchor_idx = pairs[pair_idx, 0]
            positive_idx = pairs[pair_idx, 1]
            batch_idx = np.concatenate([anchor_idx, positive_idx]).astype(np.int64)

            xb = tensor_batch(data["x"], batch_idx, device)
            mb = tensor_batch(data["mask"], batch_idx, device)
            actual = tensor_batch(data["actual"], batch_idx, device)
            actual_mask = tensor_batch(data["actual_mask"], batch_idx, device)
            delta = tensor_batch(data["delta"], batch_idx, device)
            event_tokens = tensor_batch(data["event_tokens"], batch_idx, device)
            event_mask = tensor_batch(data["event_mask"], batch_idx, device)
            prototype = tensor_batch(data["prototype_mixture"], batch_idx, device)
            context = tensor_batch(data["day_context"], batch_idx, device)

            x_corrupt, mask_corrupt, hidden, event_mask_corrupt, proto_corrupt = corrupt_batch(
                xb,
                mb,
                actual_mask,
                event_mask,
                prototype,
                base_channels,
                args.entry_dropout,
                args.slot_dropout_prob,
                args.channel_dropout_prob,
                args.event_dropout,
                args.prototype_noise,
                args.noise_std,
            )
            out = model(x_corrupt, mask_corrupt, slot_features, event_tokens, event_mask_corrupt, proto_corrupt, context)
            actual_loss = reconstruction_loss(out["actual_pred"], actual, actual_mask, hidden, channel_weights)
            delta_loss = reconstruction_loss(out["delta_pred"], delta, actual_mask, hidden, channel_weights)
            contrast = contrastive_loss(out["latent"][: args.batch_pairs], out["latent"][args.batch_pairs :], args.temperature)
            latent_l2 = out["latent"].pow(2).mean()
            loss = actual_loss + args.delta_weight * delta_loss + args.contrast_weight * contrast + args.latent_l2 * latent_l2

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            optimizer.step()
            scheduler.step()

            losses.append(float(loss.detach().cpu()))
            recon_losses.append(float(actual_loss.detach().cpu()))
            delta_losses.append(float(delta_loss.detach().cpu()))
            contrast_losses.append(float(contrast.detach().cpu()))
            progress.set_postfix(loss=np.mean(losses[-10:]), recon=np.mean(recon_losses[-10:]), contrast=np.mean(contrast_losses[-10:]))

        row = {
            "epoch": epoch,
            "loss": float(np.mean(losses)),
            "actual_recon_loss": float(np.mean(recon_losses)),
            "delta_recon_loss": float(np.mean(delta_losses)),
            "contrastive_loss": float(np.mean(contrast_losses)),
            "lr": float(scheduler.get_last_lr()[0]),
        }
        log_rows.append(row)
        print(
            f"epoch={epoch} loss={row['loss']:.6f} actual={row['actual_recon_loss']:.6f} "
            f"delta={row['delta_recon_loss']:.6f} contrast={row['contrastive_loss']:.6f}"
        )
        if row["loss"] < best_loss:
            best_loss = row["loss"]
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "args": vars(args),
                    "metadata": metadata,
                    "shape": metadata["shape"],
                    "best_epoch": epoch,
                    "best_loss": best_loss,
                },
                checkpoint_dir / "best_pyramid_encoder.pt",
            )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "args": vars(args),
            "metadata": metadata,
            "shape": metadata["shape"],
            "best_loss": best_loss,
        },
        checkpoint_dir / "last_pyramid_encoder.pt",
    )
    pd.DataFrame(log_rows).to_csv(output_dir / "training_log.csv", index=False)
    (output_dir / "training_config.json").write_text(json.dumps(vars(args), ensure_ascii=False, indent=2), encoding="utf-8")
    export_latents(model, data, output_dir, device, args.export_batch_size)
    report = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "device": str(device),
        "n_pairs": int(len(pairs)),
        "best_loss": float(best_loss),
        "final_loss": float(log_rows[-1]["loss"]),
        "latent_path": str(output_dir / "day_latents.parquet"),
        "checkpoint": str(checkpoint_dir / "last_pyramid_encoder.pt"),
        "objectives": [
            "masked reconstruction of actual 5-minute sensor channels",
            "masked reconstruction of actual-minus-normal-twin delta channels",
            "same-subject neighboring-day contrastive learning",
            "event/prototype/context conditioning with modality dropout corruption",
        ],
    }
    (output_dir / "training_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "training_report.md").write_text(
        "\n".join(
            [
                "# Pyramid Encoder Training Report",
                "",
                f"- device: `{device}`",
                f"- temporal pairs: `{len(pairs)}`",
                f"- best loss: `{best_loss:.6f}`",
                f"- final loss: `{log_rows[-1]['loss']:.6f}`",
                f"- latent path: `{output_dir / 'day_latents.parquet'}`",
                "",
                "## Objectives",
                "",
                "- Masked reconstruction of actual 5-minute sensor channels.",
                "- Masked reconstruction of actual-minus-normal-day-twin deviation channels.",
                "- Same-subject neighboring-day contrastive learning.",
                "- Robustness through slot/channel/event/prototype corruption.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a self-supervised encoder on the 5-minute Encoder Day Pyramid tensor.")
    parser.add_argument("--input-dir", default="outputs/encoder_day_pyramid")
    parser.add_argument("--output-dir", default="outputs/encoder_day_pyramid_ssl_v1")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--steps-per-epoch", type=int, default=80)
    parser.add_argument("--batch-pairs", type=int, default=6)
    parser.add_argument("--export-batch-size", type=int, default=16)
    parser.add_argument("--d-model", type=int, default=96)
    parser.add_argument("--latent-dim", type=int, default=128)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--entry-dropout", type=float, default=0.08)
    parser.add_argument("--slot-dropout-prob", type=float, default=0.45)
    parser.add_argument("--channel-dropout-prob", type=float, default=0.30)
    parser.add_argument("--event-dropout", type=float, default=0.15)
    parser.add_argument("--prototype-noise", type=float, default=0.03)
    parser.add_argument("--noise-std", type=float, default=0.04)
    parser.add_argument("--delta-weight", type=float, default=0.75)
    parser.add_argument("--contrast-weight", type=float, default=0.20)
    parser.add_argument("--latent-l2", type=float, default=1e-4)
    parser.add_argument("--temperature", type=float, default=0.15)
    parser.add_argument("--max-positive-offset", type=int, default=2)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
