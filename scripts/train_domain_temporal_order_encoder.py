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
    choose_device,
    dataframe_to_markdown,
    embedding_geometry,
    load_tokens,
    make_day_index,
    normalize_values,
    select_channel_indices,
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


def build_adjacent_pairs(keys: pd.DataFrame) -> np.ndarray:
    ordered = keys.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date"])
    pairs = []
    for _, group in ordered.groupby("subject_id", sort=False):
        idx = group["_idx"].to_numpy(np.int64)
        pairs.extend((int(a), int(b)) for a, b in zip(idx[:-1], idx[1:]))
    if not pairs:
        raise ValueError("No adjacent same-subject day pairs")
    return np.array(pairs, dtype=np.int64)


class TemporalOrderModel(nn.Module):
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
        self.order_head = nn.Sequential(
            nn.LayerNorm(d_model * 4),
            nn.Linear(d_model * 4, d_model * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 2, 1),
        )

    def forward_pair(
        self,
        first_values: torch.Tensor,
        first_masks: torch.Tensor,
        second_values: torch.Tensor,
        second_masks: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z1, _ = self.encoder(first_values, first_masks)
        z2, _ = self.encoder(second_values, second_masks)
        features = torch.cat([z1, z2, z2 - z1, z1 * z2], dim=1)
        logits = self.order_head(features).squeeze(1)
        return logits, z1, z2


def split_pairs(n: int, seed: int, val_fraction: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_val = max(1, int(round(n * val_fraction)))
    return idx[n_val:], idx[:n_val]


def encode_all(model: TemporalOrderModel, values: np.ndarray, masks: np.ndarray, batch_size: int, device: torch.device) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            xb = torch.tensor(values[start : start + batch_size], dtype=torch.float32, device=device)
            mb = torch.tensor(masks[start : start + batch_size], dtype=torch.float32, device=device)
            z, _ = model.encoder(xb, mb)
            out.append(z.detach().cpu().numpy())
    return np.nan_to_num(np.vstack(out).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def evaluate_order(model: TemporalOrderModel, pairs: np.ndarray, values: torch.Tensor, masks: torch.Tensor, args: argparse.Namespace, device: torch.device) -> dict[str, float]:
    model.eval()
    losses = []
    correct = 0
    total = 0
    with torch.no_grad():
        for start in range(0, len(pairs), args.batch_size):
            batch_pairs = pairs[start : start + args.batch_size]
            forward = torch.ones(len(batch_pairs), dtype=torch.float32, device=device)
            rev = torch.zeros(len(batch_pairs), dtype=torch.float32, device=device)
            a = torch.tensor(batch_pairs[:, 0], dtype=torch.long, device=device)
            b = torch.tensor(batch_pairs[:, 1], dtype=torch.long, device=device)
            logits_f, _, _ = model.forward_pair(values[a], masks[a], values[b], masks[b])
            logits_r, _, _ = model.forward_pair(values[b], masks[b], values[a], masks[a])
            logits = torch.cat([logits_f, logits_r])
            labels = torch.cat([forward, rev])
            loss = nn.functional.binary_cross_entropy_with_logits(logits, labels)
            pred = (torch.sigmoid(logits) >= 0.5).float()
            correct += int((pred == labels).sum().detach().cpu())
            total += int(labels.numel())
            losses.append(float(loss.detach().cpu()))
    return {"val_loss": float(np.mean(losses)), "val_accuracy": float(correct / max(1, total))}


def train_one(values: np.ndarray, masks: np.ndarray, pairs: np.ndarray, args: argparse.Namespace, seed: int, device: torch.device) -> tuple[np.ndarray, dict]:
    seed_everything(seed)
    train_pair_idx, val_pair_idx = split_pairs(len(pairs), seed, args.val_fraction)
    train_pairs = pairs[train_pair_idx]
    val_pairs = pairs[val_pair_idx]
    model = TemporalOrderModel(
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
    pair_ds = TensorDataset(torch.tensor(train_pairs, dtype=torch.long))
    loader = DataLoader(pair_ds, batch_size=args.batch_size, shuffle=True, drop_last=False)
    all_values = torch.tensor(values, dtype=torch.float32)
    all_masks = torch.tensor(masks, dtype=torch.float32)
    val_values = all_values.to(device)
    val_masks = all_masks.to(device)
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total = 0.0
        correct = 0
        seen = 0
        for (pair_batch,) in loader:
            pair_np = pair_batch.numpy()
            flip = np.random.default_rng(seed + epoch + seen).random(len(pair_np)) < 0.5
            first = pair_np[:, 0].copy()
            second = pair_np[:, 1].copy()
            labels = np.ones(len(pair_np), dtype=np.float32)
            first[flip], second[flip] = second[flip], first[flip]
            labels[flip] = 0.0
            first_t = torch.tensor(first, dtype=torch.long)
            second_t = torch.tensor(second, dtype=torch.long)
            label_t = torch.tensor(labels, dtype=torch.float32, device=device)
            x1 = all_values[first_t].to(device)
            m1 = all_masks[first_t].to(device)
            x2 = all_values[second_t].to(device)
            m2 = all_masks[second_t].to(device)
            x1, m1 = augment(x1, m1, args)
            x2, m2 = augment(x2, m2, args)
            logits, _, _ = model.forward_pair(x1, m1, x2, m2)
            loss = nn.functional.binary_cross_entropy_with_logits(logits, label_t)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            pred = (torch.sigmoid(logits) >= 0.5).float()
            correct += int((pred == label_t).sum().detach().cpu())
            seen += len(pair_np)
            total += float(loss.detach().cpu()) * len(pair_np)
        val = evaluate_order(model, val_pairs, val_values, val_masks, args, device)
        history.append(
            {
                "epoch": epoch,
                "train_loss": total / max(1, seen),
                "train_accuracy": correct / max(1, seen),
                **val,
            }
        )
    z = encode_all(model, values, masks, args.batch_size, device)
    return z, {
        "seed": int(seed),
        "train_pairs": int(len(train_pairs)),
        "val_pairs": int(len(val_pairs)),
        "final_train_loss": float(history[-1]["train_loss"]),
        "final_train_accuracy": float(history[-1]["train_accuracy"]),
        "final_val_loss": float(history[-1]["val_loss"]),
        "final_val_accuracy": float(history[-1]["val_accuracy"]),
        "best_val_loss": float(min(row["val_loss"] for row in history)),
        "best_val_accuracy": float(max(row["val_accuracy"] for row in history)),
        "history": history,
    }


def run(args: argparse.Namespace) -> None:
    tokens = load_tokens(Path(args.token_path))
    base_values = tokens["values"].astype(np.float32)
    base_masks = tokens["mask"].astype(np.float32)
    groups = tokens["channel_groups"].astype(str)
    keys = make_day_index(tokens)
    pairs = build_adjacent_pairs(keys)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    views = [view.strip() for view in args.views.split(",") if view.strip()]
    normalizations = [name.strip() for name in args.normalizations.split(",") if name.strip()]
    seeds = [int(seed) for seed in args.seeds]
    device = choose_device(args.device)
    summary_rows = []
    for normalization in normalizations:
        for view in views:
            idx = select_channel_indices(groups, view)
            masks = base_masks[:, idx, :]
            values = normalize_values(base_values[:, idx, :], masks, keys, normalization)
            view_dir = output_dir / normalization / view
            view_dir.mkdir(parents=True, exist_ok=True)
            seed_embeddings = []
            view_reports = []
            for seed in seeds:
                z, report = train_one(values, masks, pairs, args, seed, device)
                metrics = {
                    "normalization": normalization,
                    "view": view,
                    "device": str(device),
                    "channels_selected": int(len(idx)),
                    "channel_groups_selected": sorted(pd.Series(groups[idx]).unique().tolist()),
                    "embedding_dim": int(z.shape[1]),
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
    summary.to_csv(output_dir / "temporal_order_summary.csv", index=False)
    final = {
        "token_path": args.token_path,
        "views": views,
        "normalizations": normalizations,
        "seeds": seeds,
        "device": str(device),
        "config": {
            "patch_len": args.patch_len,
            "d_model": args.d_model,
            "epochs": args.epochs,
            "token_drop_prob": args.token_drop_prob,
            "channel_drop_prob": args.channel_drop_prob,
        },
        "summary": summary.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    display_cols = [
        "normalization",
        "view",
        "seed",
        "best_val_loss",
        "best_val_accuracy",
        "final_val_accuracy",
        "subject_centroid_leakage",
        "train_sample_mean_l2",
        "temporal_locality_gap",
        "embedding_effective_rank",
    ]
    md = [
        "# Domain Temporal Order Encoder",
        "",
        "## Purpose",
        "",
        "Train a target-free direction encoder by predicting whether two adjacent same-subject days are in chronological order or reversed.",
        "",
        "## Config",
        "",
        f"- Device: `{device}`",
        f"- Views: `{', '.join(views)}`",
        f"- Normalizations: `{', '.join(normalizations)}`",
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
        "Promote this branch only if late-fusing it with the current reconstruction branch beats the contrastive event+cross_modal branch.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train temporal order encoders over domain tokens.")
    parser.add_argument("--token-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_temporal_order_encoder_v1")
    parser.add_argument("--views", default="event+cross_modal")
    parser.add_argument("--normalizations", default="subject_channel_token")
    parser.add_argument("--seeds", type=int, nargs="+", default=[2026, 2027])
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--val-fraction", type=float, default=0.18)
    parser.add_argument("--patch-len", type=int, default=4)
    parser.add_argument("--d-model", type=int, default=24)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--temporal-layers", type=int, default=1)
    parser.add_argument("--channel-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.10)
    parser.add_argument("--lr", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--token-drop-prob", type=float, default=0.06)
    parser.add_argument("--channel-drop-prob", type=float, default=0.06)
    parser.add_argument("--noise-std", type=float, default=0.01)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
