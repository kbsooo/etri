from __future__ import annotations

import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from train_hourly_transformer_encoder import (
    all_day_keys,
    dataframe_to_markdown,
    evaluate_embedding_probe,
    targetwise_prediction,
)
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, write_prediction
from train_s2_sleep_retrieval_encoder import KEY_COLUMNS, SEED, TARGET_COLUMNS, normalize_keys


@dataclass(frozen=True)
class ChannelView:
    name: str
    mode: str
    tokens: tuple[str, ...] = ()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def channel_views() -> dict[str, ChannelView]:
    return {
        "full": ChannelView("full", "all"),
        "no_event": ChannelView("no_event", "drop", ("ev_",)),
        "only_event": ChannelView("only_event", "only", ("ev_",)),
        "no_sleep": ChannelView("no_sleep", "drop", ("hr", "pedo", "step", "cal", "wlight")),
        "only_rhythm": ChannelView("only_rhythm", "only", ("hr", "pedo", "step", "cal", "light", "still", "screen", "charging")),
        "only_cross_modal": ChannelView("only_cross_modal", "only", ("gap", "activity", "coverage", "ev_", "amb_", "gps", "screen")),
        "no_sparse_position": ChannelView("no_sparse_position", "drop", ("lat", "lon", "rssi", "alt")),
    }


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    blocked = {"subject_id", "date", "tok", "hod", "lifelog_date", "sleep_date"}
    return [col for col in frame.columns if col not in blocked and pd.api.types.is_numeric_dtype(frame[col])]


def select_columns(columns: list[str], view: ChannelView) -> list[str]:
    if view.mode == "all":
        return columns
    lower = {col: col.lower() for col in columns}
    if view.mode == "drop":
        selected = [col for col in columns if not any(token in lower[col] for token in view.tokens)]
    elif view.mode == "only":
        selected = [col for col in columns if any(token in lower[col] for token in view.tokens)]
    else:
        raise ValueError(f"Unknown view mode: {view.mode}")
    if not selected:
        raise ValueError(f"View {view.name} selected no channels")
    return selected


def static_context(keys: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    subjects = sorted(keys["subject_id"].astype(str).unique().tolist())
    subject_to_idx = {subject: i for i, subject in enumerate(subjects)}
    subject_idx = keys["subject_id"].astype(str).map(subject_to_idx).to_numpy(np.int64)
    dates = pd.to_datetime(keys["lifelog_date"])
    weekday = dates.dt.weekday.to_numpy(float)
    month = dates.dt.month.to_numpy(float)
    static = np.column_stack(
        [
            np.sin(2.0 * np.pi * weekday / 7.0),
            np.cos(2.0 * np.pi * weekday / 7.0),
            np.sin(2.0 * np.pi * month / 12.0),
            np.cos(2.0 * np.pi * month / 12.0),
            keys["panel_index"].to_numpy(float),
            keys["panel_position"].to_numpy(float),
        ]
    ).astype(np.float32)
    static = np.nan_to_num(static, nan=0.0, posinf=0.0, neginf=0.0)
    return subject_idx, static, subjects


def build_channel_tensor(
    grid: pd.DataFrame,
    keys: pd.DataFrame,
    view: ChannelView,
    tokens_per_day: int,
) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, float]]:
    table = grid.copy()
    table["subject_id"] = table["subject_id"].astype(str)
    table["date"] = pd.to_datetime(table["date"]).dt.strftime("%Y-%m-%d")
    if "tok" not in table.columns:
        raise ValueError("Token table must have a tok column")
    table["tok"] = table["tok"].astype(int)

    base_cols = select_columns(numeric_columns(table), view)
    skeleton = keys[["subject_id", "date"]].loc[keys.index.repeat(tokens_per_day)].reset_index(drop=True)
    skeleton["tok"] = np.tile(np.arange(tokens_per_day), len(keys)).astype(int)
    indexed = skeleton.merge(table[["subject_id", "date", "tok"] + base_cols], on=["subject_id", "date", "tok"], how="left", validate="one_to_one")
    raw = indexed[base_cols].replace([np.inf, -np.inf], np.nan)
    mask = raw.notna().astype(np.float32)
    medians = raw.median(axis=0, skipna=True).fillna(0.0)
    filled = raw.fillna(medians).astype(float)
    scaler = StandardScaler()
    values = pd.DataFrame(scaler.fit_transform(filled), columns=base_cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    values = np.clip(values.to_numpy(np.float32), -8.0, 8.0)
    mask_arr = mask.to_numpy(np.float32)
    n_days = len(keys)
    n_channels = len(base_cols)
    values = values.reshape(n_days, tokens_per_day, n_channels).transpose(0, 2, 1)
    mask_arr = mask_arr.reshape(n_days, tokens_per_day, n_channels).transpose(0, 2, 1)
    diagnostics = {
        "n_days": float(n_days),
        "n_channels": float(n_channels),
        "tokens_per_day": float(tokens_per_day),
        "observed_fraction": float(mask_arr.mean()),
    }
    return values, mask_arr, base_cols, diagnostics


class ChannelPatchTransformer(nn.Module):
    def __init__(
        self,
        n_channels: int,
        n_subjects: int,
        n_static: int,
        tokens_per_day: int,
        patch_len: int,
        d_model: int,
        n_heads: int,
        temporal_layers: int,
        channel_layers: int,
        dropout: float,
    ) -> None:
        super().__init__()
        if tokens_per_day % patch_len != 0:
            raise ValueError("tokens_per_day must be divisible by patch_len")
        self.n_channels = n_channels
        self.patch_len = patch_len
        self.n_patches = tokens_per_day // patch_len
        self.patch_proj = nn.Linear(patch_len * 2, d_model)
        self.temporal_pos = nn.Parameter(torch.zeros(1, self.n_patches, d_model))
        self.channel_embed = nn.Embedding(n_channels, d_model)
        self.subject_embed = nn.Embedding(n_subjects, d_model)
        self.static_proj = nn.Sequential(nn.Linear(n_static, d_model), nn.GELU(), nn.Linear(d_model, d_model))
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model))
        temporal_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.temporal_encoder = nn.TransformerEncoder(temporal_layer, num_layers=temporal_layers)
        channel_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.channel_encoder = nn.TransformerEncoder(channel_layer, num_layers=channel_layers)
        self.norm = nn.LayerNorm(d_model)
        self.reconstruct = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, patch_len))
        nn.init.normal_(self.temporal_pos, std=0.02)
        nn.init.normal_(self.cls, std=0.02)

    def patchify(self, values: torch.Tensor, masks: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, channels, tokens = values.shape
        patches = values.reshape(batch, channels, self.n_patches, self.patch_len)
        patch_masks = masks.reshape(batch, channels, self.n_patches, self.patch_len)
        return patches, patch_masks

    def forward(
        self,
        values: torch.Tensor,
        masks: torch.Tensor,
        subject_idx: torch.Tensor,
        static: torch.Tensor,
        patch_drop: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        patches, patch_masks = self.patchify(values, masks)
        inputs = patches
        if patch_drop is not None:
            inputs = inputs.masked_fill(patch_drop[..., None], 0.0)
        token_input = torch.cat([inputs, patch_masks], dim=-1)
        token = self.patch_proj(token_input)
        token = token + self.temporal_pos[:, None, :, :]
        channel_ids = torch.arange(self.n_channels, device=values.device)
        token = token + self.channel_embed(channel_ids)[None, :, None, :]
        bsz = values.shape[0]
        temporal = self.temporal_encoder(token.reshape(bsz * self.n_channels, self.n_patches, -1))
        recon = self.reconstruct(temporal).reshape(bsz, self.n_channels, self.n_patches, self.patch_len)
        channel_summary = temporal.reshape(bsz, self.n_channels, self.n_patches, -1).mean(dim=2)
        context = self.subject_embed(subject_idx) + self.static_proj(static)
        cls = self.cls.expand(bsz, -1, -1) + context[:, None, :]
        encoded = self.channel_encoder(torch.cat([cls, channel_summary], dim=1))
        encoded = self.norm(encoded)
        return encoded[:, 0], encoded[:, 1:], recon, patches


def device_for_training() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def train_ssl(
    values: np.ndarray,
    masks: np.ndarray,
    subject_idx: np.ndarray,
    static: np.ndarray,
    n_subjects: int,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, list[float]]:
    seed_everything(args.seed)
    dataset = TensorDataset(
        torch.tensor(values, dtype=torch.float32),
        torch.tensor(masks, dtype=torch.float32),
        torch.tensor(subject_idx, dtype=torch.long),
        torch.tensor(static, dtype=torch.float32),
    )
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, drop_last=False)
    model = ChannelPatchTransformer(
        n_channels=values.shape[1],
        n_subjects=n_subjects,
        n_static=static.shape[1],
        tokens_per_day=values.shape[2],
        patch_len=args.patch_len,
        d_model=args.d_model,
        n_heads=args.n_heads,
        temporal_layers=args.temporal_layers,
        channel_layers=args.channel_layers,
        dropout=args.dropout,
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    history: list[float] = []
    n_patches = values.shape[2] // args.patch_len
    for _ in range(args.epochs):
        model.train()
        total = 0.0
        count = 0
        for batch_values, batch_masks, batch_subject, batch_static in loader:
            batch_values = batch_values.to(device)
            batch_masks = batch_masks.to(device)
            batch_subject = batch_subject.to(device)
            batch_static = batch_static.to(device)
            noisy = batch_values
            if args.noise_std > 0:
                noisy = noisy + torch.randn_like(noisy) * args.noise_std * batch_masks
            patch_drop = torch.rand((batch_values.shape[0], batch_values.shape[1], n_patches), device=device) < args.mask_prob
            if args.modality_drop_prob > 0:
                channel_drop = torch.rand((batch_values.shape[0], batch_values.shape[1], 1), device=device) < args.modality_drop_prob
                patch_drop = patch_drop | channel_drop
            if not patch_drop.any():
                patch_drop[:, random.randrange(batch_values.shape[1]), random.randrange(n_patches)] = True
            _, _, recon, target = model(noisy, batch_masks, batch_subject, batch_static, patch_drop=patch_drop)
            obs_patch = batch_masks.reshape(batch_masks.shape[0], batch_masks.shape[1], n_patches, args.patch_len)
            loss_weight = obs_patch.clamp_min(0.0)
            masked_weight = loss_weight * patch_drop[..., None].float()
            masked_denom = masked_weight.sum().clamp_min(1.0)
            masked_loss = ((recon - target).pow(2) * masked_weight).sum() / masked_denom
            all_denom = loss_weight.sum().clamp_min(1.0)
            all_loss = ((recon - target).pow(2) * loss_weight).sum() / all_denom
            loss = masked_loss + args.all_patch_loss_weight * all_loss
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += float(loss.detach().cpu()) * len(batch_values)
            count += len(batch_values)
        history.append(total / max(1, count))

    model.eval()
    embeddings = []
    channel_embeddings = []
    with torch.no_grad():
        for start in range(0, len(values), args.batch_size):
            batch_values = torch.tensor(values[start : start + args.batch_size], dtype=torch.float32, device=device)
            batch_masks = torch.tensor(masks[start : start + args.batch_size], dtype=torch.float32, device=device)
            batch_subject = torch.tensor(subject_idx[start : start + args.batch_size], dtype=torch.long, device=device)
            batch_static = torch.tensor(static[start : start + args.batch_size], dtype=torch.float32, device=device)
            cls, channels, _, _ = model(batch_values, batch_masks, batch_subject, batch_static)
            embeddings.append(cls.detach().cpu().numpy())
            channel_embeddings.append(channels.detach().cpu().numpy())
    z = np.vstack(embeddings).astype(np.float32)
    channel_z = np.concatenate(channel_embeddings, axis=0).astype(np.float32)
    z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)
    channel_z = np.nan_to_num(channel_z, nan=0.0, posinf=0.0, neginf=0.0)
    return z, channel_z, history


def run(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    grid = pd.read_parquet(args.token_table_path)
    keys = all_day_keys(train, sample)
    subject_idx, static, subjects = static_context(keys)
    device = device_for_training()
    requested = [item.strip() for item in args.views.split(",") if item.strip()]
    specs = channel_views()
    unknown = sorted(set(requested) - set(specs))
    if unknown:
        raise ValueError(f"Unknown views: {unknown}. Available: {sorted(specs)}")

    reports = []
    best_view = ""
    best_score = math.inf
    best_oof = None
    best_sample = None
    for view_name in requested:
        view_dir = output_dir / view_name
        view_dir.mkdir(parents=True, exist_ok=True)
        values, masks, channels, diag = build_channel_tensor(grid, keys, specs[view_name], args.tokens_per_day)
        z_all, channel_z_all, history = train_ssl(values, masks, subject_idx, static, len(subjects), args, device)
        z_train = z_all[: len(train)]
        z_sample = z_all[len(train) :]
        channel_z_train = channel_z_all[: len(train)]
        channel_z_sample = channel_z_all[len(train) :]
        np.savez_compressed(
            view_dir / "embeddings.npz",
            train=z_train,
            sample=z_sample,
            all=z_all,
            channel_train=channel_z_train,
            channel_sample=channel_z_sample,
            channel_all=channel_z_all,
            channels=np.array(channels, dtype=object),
            ssl_loss=np.array(history, dtype=float),
        )
        score_df, candidates_oof, candidates_sample = evaluate_embedding_probe(train, sample, z_train, z_sample, args)
        target_oof, target_sample, target_sources, target_losses = targetwise_prediction(score_df, candidates_oof, candidates_sample, train)
        target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
        best_global = score_df.iloc[0]
        global_source = str(best_global["source"])
        drift_global = drift_vs_reference(sample, candidates_sample[global_source], Path(args.reference_submission) if args.reference_submission else None)
        drift_target = drift_vs_reference(sample, target_sample, Path(args.reference_submission) if args.reference_submission else None)
        score_df.to_csv(view_dir / "probe_scores.csv", index=False)
        write_prediction(view_dir / "oof_best_global.csv", train, candidates_oof[global_source], oof=True)
        write_prediction(view_dir / "submission_best_global.csv", sample, candidates_sample[global_source], oof=False)
        write_prediction(view_dir / "oof_targetwise.csv", train, target_oof, oof=True)
        write_prediction(view_dir / "submission_targetwise.csv", sample, target_sample, oof=False)
        report = {
            "view": view_name,
            "device": str(device),
            "channels": channels,
            "tensor": diag,
            "patch_len": args.patch_len,
            "n_patches": args.tokens_per_day // args.patch_len,
            "final_ssl_loss": float(history[-1]),
            "best_global_source": global_source,
            "best_global_avg_log_loss": float(best_global["avg_log_loss"]),
            "best_global_per_target": {target: float(best_global[target]) for target in TARGET_COLUMNS},
            "targetwise_avg_log_loss": float(target_avg),
            "targetwise_per_target": {target: float(target_per[target]) for target in TARGET_COLUMNS},
            "targetwise_sources": target_sources,
            "targetwise_source_losses": target_losses,
            "drift_vs_reference_best_global": drift_global,
            "drift_vs_reference_targetwise": drift_target,
            "ssl_loss_history": [float(v) for v in history],
        }
        (view_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        md = [
            f"# Channel Patch Transformer - {view_name}",
            "",
            "## Representation",
            "",
            f"- Tensor: `values/masks [days={len(keys)}, channels={len(channels)}, tokens={args.tokens_per_day}]`",
            f"- Patch length: `{args.patch_len}`",
            f"- Patches per channel: `{args.tokens_per_day // args.patch_len}`",
            f"- Observed fraction: `{diag['observed_fraction']:.6f}`",
            f"- Device: `{device}`",
            f"- SSL final loss: `{history[-1]:.6f}`",
            "",
            "## Probe Scores",
            "",
            dataframe_to_markdown(score_df.head(8)),
            "",
            "## Target-Wise Selection",
            "",
            f"- Target-wise avg logloss: `{target_avg:.6f}`",
            f"- Drift vs reference: `{drift_target.get('mean_abs_drift', float('nan')):.6f}`",
            "",
            dataframe_to_markdown(pd.DataFrame([{"target": k, "source": v, "loss": target_losses[k]} for k, v in target_sources.items()])),
        ]
        (view_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
        reports.append(report)
        view_best = min(float(best_global["avg_log_loss"]), float(target_avg))
        if view_best < best_score:
            best_score = view_best
            best_view = view_name
            if float(best_global["avg_log_loss"]) <= float(target_avg):
                best_oof = candidates_oof[global_source]
                best_sample = candidates_sample[global_source]
            else:
                best_oof = target_oof
                best_sample = target_sample

    if best_oof is None or best_sample is None:
        raise RuntimeError("No prediction generated")
    summary = pd.DataFrame(
        [
            {
                "view": r["view"],
                "ssl_loss": r["final_ssl_loss"],
                "best_global": r["best_global_avg_log_loss"],
                "targetwise": r["targetwise_avg_log_loss"],
                "drift_global": r["drift_vs_reference_best_global"].get("mean_abs_drift"),
                "drift_targetwise": r["drift_vs_reference_targetwise"].get("mean_abs_drift"),
                "channels": len(r["channels"]),
            }
            for r in reports
        ]
    ).sort_values("targetwise")
    summary.to_csv(output_dir / "summary_scores.csv", index=False)
    write_prediction(output_dir / "oof_channel_patch_transformer_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_channel_patch_transformer_best.csv", sample, best_sample, oof=False)
    avg, per = average_log_loss(train[TARGET_COLUMNS], best_oof)
    final = {
        "best_view": best_view,
        "best_avg_log_loss": float(avg),
        "best_per_target": per,
        "drift_vs_reference_best": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
        "views": reports,
    }
    (output_dir / "report.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    md = [
        "# Channel-Independent Patch Transformer Encoder v1",
        "",
        "## Goal",
        "",
        "Test the SOTA-style data structure for heterogeneous lifelog sequences: value/mask tensor pairs, channel-independent patch encoding, and static context injected into the day CLS token.",
        "",
        "## View Comparison",
        "",
        dataframe_to_markdown(summary),
        "",
        "## Best Candidate",
        "",
        f"- Best view: `{best_view}`",
        f"- OOF avg logloss: `{avg:.6f}`",
        f"- Drift vs v83 reference: `{final['drift_vs_reference_best'].get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Target Loss",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": k, "loss": v} for k, v in per.items()])),
        "",
        "## Decision",
        "",
        "This branch replaces time-wise stacked tokens with channel-independent patch tokens. It is a representation test; adoption depends on whether the latent is more label-readable and less drift-prone than the previous `[B,T,F]` Transformer branch.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a channel-independent patch Transformer day encoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--token-table-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--tokens-per-day", type=int, default=48)
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/channel_patch_transformer_encoder_v1")
    parser.add_argument("--views", default="full,no_event,only_event,no_sleep,only_rhythm,only_cross_modal")
    parser.add_argument("--patch-len", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--d-model", type=int, default=64)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--temporal-layers", type=int, default=1)
    parser.add_argument("--channel-layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--mask-prob", type=float, default=0.25)
    parser.add_argument("--modality-drop-prob", type=float, default=0.03)
    parser.add_argument("--noise-std", type=float, default=0.02)
    parser.add_argument("--all-patch-loss-weight", type=float, default=0.10)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--probe-prior-alpha", type=float, default=8.0)
    parser.add_argument("--prior-alphas", type=float, nargs="+", default=[4.0, 8.0, 16.0])
    parser.add_argument("--c-values", type=float, nargs="+", default=[0.03, 0.10, 0.30])
    parser.add_argument("--logreg-blends", type=float, nargs="+", default=[0.05, 0.10, 0.20, 0.35])
    parser.add_argument("--ridge-alphas", type=float, nargs="+", default=[1.0, 5.0, 20.0])
    parser.add_argument("--ridge-blends", type=float, nargs="+", default=[0.05, 0.10, 0.20, 0.35])
    parser.add_argument("--seed", type=int, default=SEED)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
