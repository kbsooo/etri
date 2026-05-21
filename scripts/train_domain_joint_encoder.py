from __future__ import annotations

import argparse
import json
import random
import sys
import warnings
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.train_domain_temporal_contrastive_encoder import (
    PatchContrastiveEncoder,
    augment,
    batch_subject_center,
    build_positive_indices,
    choose_device,
    contrastive_loss,
    dataframe_to_markdown,
    embedding_geometry,
    load_tokens,
    make_day_index,
    normalize_values,
    select_channel_indices,
    split_indices,
    subject_centroid_leakage,
    temporal_locality,
    train_sample_shift,
    write_latents,
)

warnings.filterwarnings("ignore", message="enable_nested_tensor is True.*", category=UserWarning)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class JointDayEncoder(nn.Module):
    def __init__(
        self,
        n_channels: int,
        tokens_per_day: int,
        patch_len: int,
        d_model: int,
        n_heads: int,
        temporal_layers: int,
        channel_layers: int,
        dropout: float,
    ) -> None:
        super().__init__()
        self.encoder = PatchContrastiveEncoder(
            n_channels=n_channels,
            tokens_per_day=tokens_per_day,
            patch_len=patch_len,
            d_model=d_model,
            n_heads=n_heads,
            temporal_layers=temporal_layers,
            channel_layers=channel_layers,
            dropout=dropout,
        )
        self.n_channels = n_channels
        self.tokens_per_day = tokens_per_day
        self.reconstruct_day = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, d_model * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 2, n_channels * tokens_per_day),
        )

    def forward(self, values: torch.Tensor, masks: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z, p = self.encoder(values, masks)
        recon = self.reconstruct_day(z).reshape(values.shape[0], self.n_channels, self.tokens_per_day)
        return z, p, recon


def day_reconstruction_loss(recon: torch.Tensor, target: torch.Tensor, masks: torch.Tensor) -> torch.Tensor:
    denom = masks.sum().clamp_min(1.0)
    return ((recon - target).pow(2) * masks).sum() / denom


def encode_all(model: JointDayEncoder, values: np.ndarray, masks: np.ndarray, batch_size: int, device: torch.device) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            xb = torch.tensor(values[start : start + batch_size], dtype=torch.float32, device=device)
            mb = torch.tensor(masks[start : start + batch_size], dtype=torch.float32, device=device)
            z, _, _ = model(xb, mb)
            out.append(z.detach().cpu().numpy())
    return np.nan_to_num(np.vstack(out).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def evaluate_loss(
    model: JointDayEncoder,
    values: torch.Tensor,
    masks: torch.Tensor,
    pos_values: torch.Tensor,
    pos_masks: torch.Tensor,
    subjects: torch.Tensor,
    args: argparse.Namespace,
) -> dict[str, float]:
    model.eval()
    total_losses = []
    contrast_losses = []
    recon_losses = []
    with torch.no_grad():
        for start in range(0, len(values), args.batch_size):
            xb = values[start : start + args.batch_size]
            mb = masks[start : start + args.batch_size]
            pb = pos_values[start : start + args.batch_size]
            pm = pos_masks[start : start + args.batch_size]
            sb = subjects[start : start + args.batch_size]
            _, p1, recon = model(xb, mb)
            _, p2, _ = model(pb, pm)
            if args.subject_center:
                p1 = nn.functional.normalize(batch_subject_center(p1, sb), dim=1)
                p2 = nn.functional.normalize(batch_subject_center(p2, sb), dim=1)
            c_loss = contrastive_loss(p1, p2, args.temperature)
            r_loss = day_reconstruction_loss(recon, xb, mb)
            loss = c_loss + args.reconstruction_weight * r_loss
            total_losses.append(float(loss.detach().cpu()))
            contrast_losses.append(float(c_loss.detach().cpu()))
            recon_losses.append(float(r_loss.detach().cpu()))
    return {
        "val_loss": float(np.mean(total_losses)),
        "val_contrastive_loss": float(np.mean(contrast_losses)),
        "val_reconstruction_loss": float(np.mean(recon_losses)),
    }


def train_one(
    values: np.ndarray,
    masks: np.ndarray,
    positive_idx: np.ndarray,
    subject_codes: np.ndarray,
    args: argparse.Namespace,
    seed: int,
    device: torch.device,
) -> tuple[np.ndarray, dict]:
    seed_everything(seed)
    train_idx, val_idx = split_indices(len(values), seed, args.val_fraction)
    model = JointDayEncoder(
        n_channels=values.shape[1],
        tokens_per_day=values.shape[2],
        patch_len=args.patch_len,
        d_model=args.d_model,
        n_heads=args.n_heads,
        temporal_layers=args.temporal_layers,
        channel_layers=args.channel_layers,
        dropout=args.dropout,
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    train_ds = TensorDataset(
        torch.tensor(train_idx, dtype=torch.long),
        torch.tensor(values[train_idx], dtype=torch.float32),
        torch.tensor(masks[train_idx], dtype=torch.float32),
        torch.tensor(subject_codes[train_idx], dtype=torch.long),
    )
    loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, drop_last=True)
    all_values = torch.tensor(values, dtype=torch.float32)
    all_masks = torch.tensor(masks, dtype=torch.float32)
    val_values = all_values[val_idx].to(device)
    val_masks = all_masks[val_idx].to(device)
    val_pos_values = all_values[positive_idx[val_idx]].to(device)
    val_pos_masks = all_masks[positive_idx[val_idx]].to(device)
    val_subjects = torch.tensor(subject_codes[val_idx], dtype=torch.long, device=device)
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total = 0.0
        total_contrast = 0.0
        total_recon = 0.0
        seen = 0
        for idx_b, xb, mb, sb in loader:
            pos_idx = torch.tensor(positive_idx[idx_b.numpy()], dtype=torch.long)
            pb = all_values[pos_idx].to(device)
            pm = all_masks[pos_idx].to(device)
            xb = xb.to(device)
            mb = mb.to(device)
            sb = sb.to(device)
            x1, m1 = augment(xb, mb, args)
            x2, m2 = augment(pb, pm, args)
            _, p1, recon = model(x1, m1)
            _, p2, _ = model(x2, m2)
            if args.subject_center:
                p1 = nn.functional.normalize(batch_subject_center(p1, sb), dim=1)
                p2 = nn.functional.normalize(batch_subject_center(p2, sb), dim=1)
            c_loss = contrastive_loss(p1, p2, args.temperature)
            r_loss = day_reconstruction_loss(recon, xb, mb)
            loss = c_loss + args.reconstruction_weight * r_loss
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += float(loss.detach().cpu()) * len(xb)
            total_contrast += float(c_loss.detach().cpu()) * len(xb)
            total_recon += float(r_loss.detach().cpu()) * len(xb)
            seen += len(xb)
        val = evaluate_loss(model, val_values, val_masks, val_pos_values, val_pos_masks, val_subjects, args)
        history.append(
            {
                "epoch": epoch,
                "train_loss": total / max(1, seen),
                "train_contrastive_loss": total_contrast / max(1, seen),
                "train_reconstruction_loss": total_recon / max(1, seen),
                **val,
            }
        )
    embeddings = encode_all(model, values, masks, args.batch_size, device)
    return embeddings, {
        "seed": int(seed),
        "train_days": int(len(train_idx)),
        "val_days": int(len(val_idx)),
        "final_train_loss": float(history[-1]["train_loss"]),
        "final_val_loss": float(history[-1]["val_loss"]),
        "final_val_contrastive_loss": float(history[-1]["val_contrastive_loss"]),
        "final_val_reconstruction_loss": float(history[-1]["val_reconstruction_loss"]),
        "best_val_loss": float(min(row["val_loss"] for row in history)),
        "history": history,
    }


def run(args: argparse.Namespace) -> None:
    tokens = load_tokens(Path(args.token_path))
    base_values = tokens["values"].astype(np.float32)
    base_masks = tokens["mask"].astype(np.float32)
    groups = tokens["channel_groups"].astype(str)
    keys = make_day_index(tokens)
    subject_codes = pd.Categorical(keys["subject_id"].astype(str)).codes.astype(np.int64)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    views = [view.strip() for view in args.views.split(",") if view.strip()]
    normalizations = [name.strip() for name in args.normalizations.split(",") if name.strip()]
    positive_modes = [name.strip() for name in args.positive_modes.split(",") if name.strip()]
    seeds = [int(seed) for seed in args.seeds]
    device = choose_device(args.device)
    summary_rows = []
    for positive_mode in positive_modes:
        for normalization in normalizations:
            for view in views:
                idx = select_channel_indices(groups, view)
                masks = base_masks[:, idx, :]
                values = normalize_values(base_values[:, idx, :], masks, keys, normalization)
                view_dir = output_dir / positive_mode / normalization / view
                view_dir.mkdir(parents=True, exist_ok=True)
                seed_embeddings = []
                view_reports = []
                for seed in seeds:
                    positive_idx = build_positive_indices(keys, positive_mode, seed)
                    z, report = train_one(values, masks, positive_idx, subject_codes, args, seed, device)
                    metrics = {
                        "positive_mode": positive_mode,
                        "normalization": normalization,
                        "view": view,
                        "device": str(device),
                        "channels_selected": int(len(idx)),
                        "channel_groups_selected": sorted(pd.Series(groups[idx]).unique().tolist()),
                        "embedding_dim": int(z.shape[1]),
                        "reconstruction_weight": float(args.reconstruction_weight),
                        **embedding_geometry(z),
                        "subject_centroid_leakage": subject_centroid_leakage(z, keys),
                        **temporal_locality(z, keys),
                        **train_sample_shift(z, keys, Path(args.train_path), Path(args.sample_path)),
                    }
                    report.update(metrics)
                    seed_dir = view_dir / f"seed_{seed}"
                    seed_dir.mkdir(parents=True, exist_ok=True)
                    np.save(seed_dir / "embeddings.npy", z)
                    write_latents(seed_dir / "embeddings.parquet", keys, z)
                    (seed_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
                    seed_embeddings.append(z)
                    view_reports.append(report)
                    summary_rows.append({k: v for k, v in report.items() if k != "history"})
                z_mean = np.mean(seed_embeddings, axis=0).astype(np.float32)
                np.save(view_dir / "embeddings_mean.npy", z_mean)
                write_latents(view_dir / "embeddings_mean.parquet", keys, z_mean)
                view_report = {
                    "positive_mode": positive_mode,
                    "normalization": normalization,
                    "view": view,
                    "seeds": seeds,
                    "channels_selected": int(len(idx)),
                    "channel_groups_selected": sorted(pd.Series(groups[idx]).unique().tolist()),
                    "mean_embedding_metrics": {
                        "subject_centroid_leakage": subject_centroid_leakage(z_mean, keys),
                        **embedding_geometry(z_mean),
                        **temporal_locality(z_mean, keys),
                        **train_sample_shift(z_mean, keys, Path(args.train_path), Path(args.sample_path)),
                    },
                    "seed_reports": view_reports,
                }
                (view_dir / "report.json").write_text(json.dumps(view_report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = pd.DataFrame(summary_rows).sort_values(["best_val_loss", "train_sample_mean_l2"])
    summary.to_csv(output_dir / "joint_summary.csv", index=False)
    final = {
        "token_path": args.token_path,
        "views": views,
        "normalizations": normalizations,
        "positive_modes": positive_modes,
        "seeds": seeds,
        "device": str(device),
        "subject_center": bool(args.subject_center),
        "config": {
            "patch_len": args.patch_len,
            "d_model": args.d_model,
            "epochs": args.epochs,
            "temperature": args.temperature,
            "reconstruction_weight": args.reconstruction_weight,
            "token_drop_prob": args.token_drop_prob,
            "channel_drop_prob": args.channel_drop_prob,
        },
        "summary": summary.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    display_cols = [
        "positive_mode",
        "normalization",
        "view",
        "seed",
        "best_val_loss",
        "final_val_contrastive_loss",
        "final_val_reconstruction_loss",
        "subject_centroid_leakage",
        "train_sample_mean_l2",
        "temporal_locality_gap",
        "embedding_effective_rank",
    ]
    md = [
        "# Domain Joint Reconstruction Contrastive Encoder",
        "",
        "## Purpose",
        "",
        "Train a target-free multi-objective encoder that keeps reconstruction information while adding adjacent-day behavioral contrast.",
        "",
        "## Config",
        "",
        f"- Device: `{device}`",
        f"- Views: `{', '.join(views)}`",
        f"- Normalizations: `{', '.join(normalizations)}`",
        f"- Positive modes: `{', '.join(positive_modes)}`",
        f"- Subject-centered projection loss: `{bool(args.subject_center)}`",
        f"- Reconstruction weight: `{args.reconstruction_weight}`",
        f"- Seeds: `{', '.join(str(s) for s in seeds)}`",
        f"- d_model: `{args.d_model}`",
        f"- Epochs: `{args.epochs}`",
        "",
        "## Summary",
        "",
        dataframe_to_markdown(summary[display_cols].head(40).copy()),
        "",
        "## Selection Rule",
        "",
        "Promote this joint latent only if its frozen probe beats the separate reconstruction+contrastive concatenation baseline.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train joint reconstruction + temporal contrastive encoders over domain tokens.")
    parser.add_argument("--token-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_joint_encoder_v1")
    parser.add_argument("--views", default="event_cross_missing,only_event")
    parser.add_argument("--normalizations", default="subject_channel_token")
    parser.add_argument("--positive-modes", default="adjacent_day")
    parser.add_argument("--seeds", type=int, nargs="+", default=[2026, 2027])
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=96)
    parser.add_argument("--val-fraction", type=float, default=0.18)
    parser.add_argument("--patch-len", type=int, default=4)
    parser.add_argument("--d-model", type=int, default=24)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--temporal-layers", type=int, default=1)
    parser.add_argument("--channel-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.10)
    parser.add_argument("--lr", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--temperature", type=float, default=0.12)
    parser.add_argument("--reconstruction-weight", type=float, default=0.20)
    parser.add_argument("--token-drop-prob", type=float, default=0.08)
    parser.add_argument("--channel-drop-prob", type=float, default=0.08)
    parser.add_argument("--noise-std", type=float, default=0.01)
    parser.add_argument("--subject-center", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
