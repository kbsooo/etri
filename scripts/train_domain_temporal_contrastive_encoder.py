from __future__ import annotations

import argparse
import json
import math
import random
import warnings
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message="enable_nested_tensor is True.*", category=UserWarning)


VIEW_ALIASES = {
    "event_cross_missing": ("event", "cross_modal", "missingness"),
    "event_cross_phone_missing": ("event", "cross_modal", "phone", "missingness"),
}
NORMALIZATION_CHOICES = ("global", "subject_channel", "subject_channel_token")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def choose_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_tokens(path: Path) -> dict[str, np.ndarray]:
    arr = np.load(path, allow_pickle=True)
    return {key: arr[key] for key in arr.files}


def select_channel_indices(groups: np.ndarray, view: str) -> np.ndarray:
    groups = groups.astype(str)
    if view == "full":
        keep = np.ones(len(groups), dtype=bool)
    elif view in VIEW_ALIASES:
        keep = np.isin(groups, VIEW_ALIASES[view])
    elif "+" in view:
        keep = np.isin(groups, tuple(part.strip() for part in view.split("+") if part.strip()))
    elif view.startswith("only_"):
        keep = groups == view.removeprefix("only_")
    elif view.startswith("no_"):
        keep = groups != view.removeprefix("no_")
    else:
        raise ValueError(f"Unknown view: {view}")
    idx = np.flatnonzero(keep)
    if len(idx) == 0:
        raise ValueError(f"View {view} selected no channels")
    return idx


def make_day_index(tokens: dict[str, np.ndarray]) -> pd.DataFrame:
    keys = pd.DataFrame(
        {
            "subject_id": tokens["subject_id"].astype(str),
            "lifelog_date": pd.to_datetime(tokens["lifelog_date"].astype(str)).strftime("%Y-%m-%d"),
        }
    )
    return keys


def normalize_values(values: np.ndarray, masks: np.ndarray, keys: pd.DataFrame, mode: str) -> np.ndarray:
    if mode == "global":
        return values.astype(np.float32)
    if mode not in NORMALIZATION_CHOICES:
        raise ValueError(f"Unknown normalization: {mode}")
    out = values.copy()
    subjects = keys["subject_id"].astype(str).to_numpy()
    for subject in sorted(set(subjects)):
        day_idx = np.flatnonzero(subjects == subject)
        subject_values = out[day_idx]
        subject_masks = masks[day_idx].astype(bool)
        observed = np.where(subject_masks, subject_values, np.nan)
        if mode == "subject_channel":
            center = np.nanmedian(observed, axis=(0, 2), keepdims=True)
            scale = np.nanmedian(np.abs(observed - center), axis=(0, 2), keepdims=True)
        else:
            center = np.nanmedian(observed, axis=0, keepdims=True)
            scale = np.nanmedian(np.abs(observed - center), axis=0, keepdims=True)
        center = np.nan_to_num(center, nan=0.0, posinf=0.0, neginf=0.0)
        scale = np.nan_to_num(scale, nan=1.0, posinf=1.0, neginf=1.0)
        out[day_idx] = np.clip((subject_values - center) / np.maximum(scale, 1e-3), -8.0, 8.0) * masks[day_idx]
    return out.astype(np.float32)


def build_positive_indices(keys: pd.DataFrame, mode: str, seed: int) -> np.ndarray:
    if mode == "same_day":
        return np.arange(len(keys), dtype=np.int64)
    ordered = keys.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date"])
    positive = np.arange(len(keys), dtype=np.int64)
    rng = np.random.default_rng(seed)
    for _, group in ordered.groupby("subject_id", sort=False):
        idx = group["_idx"].to_numpy(np.int64)
        if len(idx) < 2:
            continue
        if mode == "adjacent_day":
            for pos, day_idx in enumerate(idx):
                if pos == 0:
                    positive[day_idx] = idx[1]
                elif pos == len(idx) - 1:
                    positive[day_idx] = idx[-2]
                else:
                    positive[day_idx] = idx[pos - 1] if rng.random() < 0.5 else idx[pos + 1]
        elif mode == "nearby_7d":
            for pos, day_idx in enumerate(idx):
                lo = max(0, pos - 7)
                hi = min(len(idx), pos + 8)
                candidates = np.delete(idx[lo:hi], np.flatnonzero(idx[lo:hi] == day_idx))
                positive[day_idx] = int(rng.choice(candidates)) if len(candidates) else day_idx
        else:
            raise ValueError(f"Unknown positive mode: {mode}")
    return positive


class PatchContrastiveEncoder(nn.Module):
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
        if tokens_per_day % patch_len != 0:
            raise ValueError("tokens_per_day must be divisible by patch_len")
        self.n_channels = n_channels
        self.patch_len = patch_len
        self.n_patches = tokens_per_day // patch_len
        self.patch_proj = nn.Linear(patch_len * 2, d_model)
        self.patch_pos = nn.Parameter(torch.zeros(1, self.n_patches, d_model))
        self.channel_embed = nn.Embedding(n_channels, d_model)
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model))
        temporal_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 3,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        channel_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 3,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.temporal_encoder = nn.TransformerEncoder(temporal_layer, num_layers=temporal_layers)
        self.channel_encoder = nn.TransformerEncoder(channel_layer, num_layers=channel_layers)
        self.norm = nn.LayerNorm(d_model)
        self.proj = nn.Sequential(nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, d_model))
        nn.init.normal_(self.patch_pos, std=0.02)
        nn.init.normal_(self.cls, std=0.02)

    def forward(self, values: torch.Tensor, masks: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, channels, _ = values.shape
        patches = values.reshape(batch, channels, self.n_patches, self.patch_len)
        patch_masks = masks.reshape(batch, channels, self.n_patches, self.patch_len)
        token = self.patch_proj(torch.cat([patches, patch_masks], dim=-1))
        token = token + self.patch_pos[:, None, :, :]
        channel_ids = torch.arange(channels, device=values.device)
        token = token + self.channel_embed(channel_ids)[None, :, None, :]
        temporal = self.temporal_encoder(token.reshape(batch * channels, self.n_patches, -1))
        channel_summary = temporal.reshape(batch, channels, self.n_patches, -1).mean(dim=2)
        encoded = self.channel_encoder(torch.cat([self.cls.expand(batch, -1, -1), channel_summary], dim=1))
        z = self.norm(encoded[:, 0])
        return z, nn.functional.normalize(self.proj(z), dim=1)


def augment(values: torch.Tensor, masks: torch.Tensor, args: argparse.Namespace) -> tuple[torch.Tensor, torch.Tensor]:
    x = values
    m = masks
    if args.noise_std > 0:
        x = x + torch.randn_like(x) * args.noise_std * m
    if args.token_drop_prob > 0:
        drop = torch.rand_like(m) < args.token_drop_prob
        x = x.masked_fill(drop, 0.0)
        m = m.masked_fill(drop, 0.0)
    if args.channel_drop_prob > 0:
        channel_drop = torch.rand((x.shape[0], x.shape[1], 1), device=x.device) < args.channel_drop_prob
        x = x.masked_fill(channel_drop, 0.0)
        m = m.masked_fill(channel_drop, 0.0)
    return x, m


def batch_subject_center(z: torch.Tensor, subject_codes: torch.Tensor) -> torch.Tensor:
    out = z.clone()
    for code in torch.unique(subject_codes):
        mask = subject_codes == code
        if int(mask.sum()) >= 2:
            out[mask] = out[mask] - out[mask].mean(dim=0, keepdim=True)
    return out


def contrastive_loss(z_a: torch.Tensor, z_b: torch.Tensor, temperature: float) -> torch.Tensor:
    logits = z_a @ z_b.T / temperature
    target = torch.arange(z_a.shape[0], device=z_a.device)
    return (nn.functional.cross_entropy(logits, target) + nn.functional.cross_entropy(logits.T, target)) * 0.5


def split_indices(n: int, seed: int, val_fraction: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_val = max(1, int(round(n * val_fraction)))
    return idx[n_val:], idx[:n_val]


def encode_all(model: PatchContrastiveEncoder, values: np.ndarray, masks: np.ndarray, batch_size: int, device: torch.device) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            xb = torch.tensor(values[start : start + batch_size], dtype=torch.float32, device=device)
            mb = torch.tensor(masks[start : start + batch_size], dtype=torch.float32, device=device)
            z, _ = model(xb, mb)
            out.append(z.detach().cpu().numpy())
    return np.nan_to_num(np.vstack(out).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)


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
    model = PatchContrastiveEncoder(
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
            z1, p1 = model(x1, m1)
            z2, p2 = model(x2, m2)
            if args.subject_center:
                p1 = nn.functional.normalize(batch_subject_center(p1, sb), dim=1)
                p2 = nn.functional.normalize(batch_subject_center(p2, sb), dim=1)
            loss = contrastive_loss(p1, p2, args.temperature)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += float(loss.detach().cpu()) * len(xb)
            seen += len(xb)
        val_loss = evaluate_loss(model, val_values, val_masks, val_pos_values, val_pos_masks, val_subjects, args, device)
        history.append({"epoch": epoch, "train_loss": total / max(1, seen), "val_loss": val_loss})
    embeddings = encode_all(model, values, masks, args.batch_size, device)
    return embeddings, {
        "seed": int(seed),
        "train_days": int(len(train_idx)),
        "val_days": int(len(val_idx)),
        "final_train_loss": float(history[-1]["train_loss"]),
        "final_val_loss": float(history[-1]["val_loss"]),
        "best_val_loss": float(min(row["val_loss"] for row in history)),
        "history": history,
    }


def evaluate_loss(
    model: PatchContrastiveEncoder,
    values: torch.Tensor,
    masks: torch.Tensor,
    pos_values: torch.Tensor,
    pos_masks: torch.Tensor,
    subjects: torch.Tensor,
    args: argparse.Namespace,
    device: torch.device,
) -> float:
    model.eval()
    losses = []
    with torch.no_grad():
        for start in range(0, len(values), args.batch_size):
            xb = values[start : start + args.batch_size]
            mb = masks[start : start + args.batch_size]
            pb = pos_values[start : start + args.batch_size]
            pm = pos_masks[start : start + args.batch_size]
            sb = subjects[start : start + args.batch_size]
            _, p1 = model(xb, mb)
            _, p2 = model(pb, pm)
            if args.subject_center:
                p1 = nn.functional.normalize(batch_subject_center(p1, sb), dim=1)
                p2 = nn.functional.normalize(batch_subject_center(p2, sb), dim=1)
            losses.append(float(contrastive_loss(p1, p2, args.temperature).detach().cpu()))
    return float(np.mean(losses))


def cosine_rows(z: np.ndarray) -> np.ndarray:
    return z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-8)


def temporal_locality(z: np.ndarray, keys: pd.DataFrame) -> dict[str, float]:
    z_norm = cosine_rows(z)
    adjacent = []
    rng = np.random.default_rng(2026)
    ordered = keys.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date"])
    for _, group in ordered.groupby("subject_id", sort=False):
        idx = group["_idx"].to_numpy()
        adjacent.extend(float((z_norm[a] * z_norm[b]).sum()) for a, b in zip(idx[:-1], idx[1:]))
    random_pairs = []
    for _ in range(max(100, len(adjacent))):
        a, b = rng.choice(len(keys), size=2, replace=False)
        random_pairs.append(float((z_norm[a] * z_norm[b]).sum()))
    return {
        "adjacent_cosine_mean": float(np.mean(adjacent)) if adjacent else float("nan"),
        "random_cosine_mean": float(np.mean(random_pairs)) if random_pairs else float("nan"),
        "temporal_locality_gap": float(np.mean(adjacent) - np.mean(random_pairs)) if adjacent and random_pairs else float("nan"),
    }


def train_sample_shift(z: np.ndarray, keys: pd.DataFrame, train_path: Path, sample_path: Path) -> dict[str, float]:
    split = pd.concat(
        [
            pd.read_csv(train_path)[["subject_id", "lifelog_date"]].assign(split="train"),
            pd.read_csv(sample_path)[["subject_id", "lifelog_date"]].assign(split="sample"),
        ],
        ignore_index=True,
    )
    split["subject_id"] = split["subject_id"].astype(str)
    split["lifelog_date"] = pd.to_datetime(split["lifelog_date"]).dt.strftime("%Y-%m-%d")
    merged = keys.merge(split, on=["subject_id", "lifelog_date"], how="left")
    train = z[merged["split"].to_numpy() == "train"]
    sample = z[merged["split"].to_numpy() == "sample"]
    return {
        "train_sample_mean_l2": float(np.linalg.norm(train.mean(axis=0) - sample.mean(axis=0))),
        "train_sample_std_l2": float(np.linalg.norm(train.std(axis=0) - sample.std(axis=0))),
    }


def subject_centroid_leakage(z: np.ndarray, keys: pd.DataFrame) -> float:
    z_norm = cosine_rows(z)
    subjects = keys["subject_id"].astype(str).to_numpy()
    correct = 0
    total = 0
    for i, subject in enumerate(subjects):
        sims = {}
        for candidate in sorted(set(subjects)):
            mask = subjects == candidate
            if candidate == subject:
                mask[i] = False
            if not mask.any():
                continue
            centroid = z_norm[mask].mean(axis=0)
            centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-8)
            sims[candidate] = float((z_norm[i] * centroid).sum())
        if sims:
            correct += int(max(sims, key=sims.get) == subject)
            total += 1
    return float(correct / total) if total else float("nan")


def embedding_geometry(z: np.ndarray) -> dict[str, float]:
    centered = z - z.mean(axis=0, keepdims=True)
    std = centered.std(axis=0)
    try:
        singular = np.linalg.svd(centered, full_matrices=False, compute_uv=False)
        power = singular**2
        prob = power / max(float(power.sum()), 1e-12)
        entropy = -float(np.sum(prob * np.log(np.maximum(prob, 1e-12))))
        effective_rank = float(np.exp(entropy))
    except np.linalg.LinAlgError:
        effective_rank = float("nan")
    return {
        "embedding_norm_mean": float(np.linalg.norm(z, axis=1).mean()),
        "embedding_axis_std_mean": float(std.mean()),
        "embedding_axis_std_min": float(std.min()),
        "embedding_effective_rank": effective_rank,
    }


def write_latents(path: Path, keys: pd.DataFrame, z: np.ndarray) -> None:
    frame = keys.copy()
    for i in range(z.shape[1]):
        frame[f"z_{i:02d}"] = z[:, i]
    frame.to_parquet(path, index=False)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    tokens = load_tokens(Path(args.token_path))
    base_values = tokens["values"].astype(np.float32)
    base_masks = tokens["mask"].astype(np.float32)
    groups = tokens["channel_groups"].astype(str)
    keys = make_day_index(tokens)
    subjects = keys["subject_id"].astype(str)
    subject_codes = pd.Categorical(subjects).codes.astype(np.int64)
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
    summary.to_csv(output_dir / "contrastive_summary.csv", index=False)
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
            "n_heads": args.n_heads,
            "temporal_layers": args.temporal_layers,
            "channel_layers": args.channel_layers,
            "epochs": args.epochs,
            "temperature": args.temperature,
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
        "channels_selected",
        "best_val_loss",
        "final_val_loss",
        "subject_centroid_leakage",
        "train_sample_mean_l2",
        "temporal_locality_gap",
        "embedding_effective_rank",
    ]
    md = [
        "# Domain Temporal Contrastive Encoder",
        "",
        "## Purpose",
        "",
        "Train target-free contrastive encoders that force day latents to represent behavioral state relations rather than only reconstruct observed token values.",
        "",
        "## Config",
        "",
        f"- Device: `{device}`",
        f"- Views: `{', '.join(views)}`",
        f"- Normalizations: `{', '.join(normalizations)}`",
        f"- Positive modes: `{', '.join(positive_modes)}`",
        f"- Subject-centered projection loss: `{bool(args.subject_center)}`",
        f"- Seeds: `{', '.join(str(s) for s in seeds)}`",
        f"- Patch length: `{args.patch_len}` 30-minute tokens = `{args.patch_len * 30}` minutes",
        f"- d_model: `{args.d_model}`",
        f"- Epochs: `{args.epochs}`",
        "",
        "## Summary",
        "",
        dataframe_to_markdown(summary[display_cols].head(40).copy()),
        "",
        "## Selection Rule",
        "",
        "Promote a contrastive latent only if its frozen label probe beats the reconstruction-SSL probe, not merely because the contrastive validation loss is low.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train target-free temporal contrastive encoders over domain idea token views.")
    parser.add_argument("--token-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_temporal_contrastive_encoder_v1")
    parser.add_argument("--views", default="event_cross_missing,only_event")
    parser.add_argument("--normalizations", default="global,subject_channel_token")
    parser.add_argument("--positive-modes", default="same_day,adjacent_day")
    parser.add_argument("--seeds", type=int, nargs="+", default=[2026, 2027])
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=12)
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
    parser.add_argument("--token-drop-prob", type=float, default=0.08)
    parser.add_argument("--channel-drop-prob", type=float, default=0.08)
    parser.add_argument("--noise-std", type=float, default=0.01)
    parser.add_argument("--subject-center", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
