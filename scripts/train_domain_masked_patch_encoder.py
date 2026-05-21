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


DEFAULT_VIEWS = [
    "only_event",
    "only_cross_modal",
    "only_missingness",
    "event_cross_missing",
    "event_cross_phone_missing",
    "no_body",
    "no_gps_radio",
    "full",
]

VIEW_ALIASES = {
    "event_cross_missing": ("event", "cross_modal", "missingness"),
    "event_cross_phone_missing": ("event", "cross_modal", "phone", "missingness"),
}


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
    return pd.DataFrame(
        {
            "subject_id": tokens["subject_id"].astype(str),
            "lifelog_date": tokens["lifelog_date"].astype(str),
        }
    )


class MaskedPatchEncoder(nn.Module):
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
        self.reconstruct = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, patch_len))
        self.norm = nn.LayerNorm(d_model)
        nn.init.normal_(self.patch_pos, std=0.02)
        nn.init.normal_(self.cls, std=0.02)

    def forward(self, values: torch.Tensor, masks: torch.Tensor, patch_drop: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        batch, channels, tokens = values.shape
        patches = values.reshape(batch, channels, self.n_patches, self.patch_len)
        patch_masks = masks.reshape(batch, channels, self.n_patches, self.patch_len)
        inputs = patches
        if patch_drop is not None:
            inputs = inputs.masked_fill(patch_drop[..., None], 0.0)
        token = self.patch_proj(torch.cat([inputs, patch_masks], dim=-1))
        token = token + self.patch_pos[:, None, :, :]
        channel_ids = torch.arange(channels, device=values.device)
        token = token + self.channel_embed(channel_ids)[None, :, None, :]
        temporal = self.temporal_encoder(token.reshape(batch * channels, self.n_patches, -1))
        recon = self.reconstruct(temporal).reshape(batch, channels, self.n_patches, self.patch_len)
        channel_summary = temporal.reshape(batch, channels, self.n_patches, -1).mean(dim=2)
        cls = self.cls.expand(batch, -1, -1)
        encoded = self.channel_encoder(torch.cat([cls, channel_summary], dim=1))
        return self.norm(encoded[:, 0]), recon, patches


def split_indices(n: int, seed: int, val_fraction: float) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    n_val = max(1, int(round(n * val_fraction)))
    return idx[n_val:], idx[:n_val]


def masked_loss(recon: torch.Tensor, target: torch.Tensor, masks: torch.Tensor, patch_drop: torch.Tensor, patch_len: int) -> torch.Tensor:
    obs = masks.reshape(masks.shape[0], masks.shape[1], masks.shape[2] // patch_len, patch_len)
    weight = obs * patch_drop[..., None].float()
    denom = weight.sum().clamp_min(1.0)
    return ((recon - target).pow(2) * weight).sum() / denom


def train_one(values: np.ndarray, masks: np.ndarray, args: argparse.Namespace, seed: int, device: torch.device) -> tuple[np.ndarray, dict]:
    seed_everything(seed)
    train_idx, val_idx = split_indices(len(values), seed, args.val_fraction)
    model = MaskedPatchEncoder(
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
    train_ds = TensorDataset(torch.tensor(values[train_idx], dtype=torch.float32), torch.tensor(masks[train_idx], dtype=torch.float32))
    val_values = torch.tensor(values[val_idx], dtype=torch.float32, device=device)
    val_masks = torch.tensor(masks[val_idx], dtype=torch.float32, device=device)
    loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, drop_last=False)
    n_patches = values.shape[2] // args.patch_len
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total = 0.0
        seen = 0
        for xb, mb in loader:
            xb = xb.to(device)
            mb = mb.to(device)
            noisy = xb + torch.randn_like(xb) * args.noise_std * mb if args.noise_std > 0 else xb
            patch_drop = torch.rand((xb.shape[0], xb.shape[1], n_patches), device=device) < args.mask_prob
            if args.channel_drop_prob > 0:
                patch_drop = patch_drop | (torch.rand((xb.shape[0], xb.shape[1], 1), device=device) < args.channel_drop_prob)
            if not patch_drop.any():
                patch_drop[:, random.randrange(xb.shape[1]), random.randrange(n_patches)] = True
            _, recon, target = model(noisy, mb, patch_drop)
            loss = masked_loss(recon, target, mb, patch_drop, args.patch_len)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += float(loss.detach().cpu()) * len(xb)
            seen += len(xb)
        val_loss = evaluate_loss(model, val_values, val_masks, args, device)
        history.append({"epoch": epoch, "train_loss": total / max(1, seen), "val_loss": val_loss})
    embeddings = encode_all(model, values, masks, args.batch_size, device)
    report = {
        "seed": int(seed),
        "train_days": int(len(train_idx)),
        "val_days": int(len(val_idx)),
        "final_train_loss": float(history[-1]["train_loss"]),
        "final_val_loss": float(history[-1]["val_loss"]),
        "best_val_loss": float(min(row["val_loss"] for row in history)),
        "history": history,
    }
    return embeddings, report


def evaluate_loss(model: MaskedPatchEncoder, values: torch.Tensor, masks: torch.Tensor, args: argparse.Namespace, device: torch.device) -> float:
    model.eval()
    n_patches = values.shape[2] // args.patch_len
    losses = []
    with torch.no_grad():
        for start in range(0, len(values), args.batch_size):
            xb = values[start : start + args.batch_size]
            mb = masks[start : start + args.batch_size]
            patch_drop = torch.rand((xb.shape[0], xb.shape[1], n_patches), device=device) < args.mask_prob
            _, recon, target = model(xb, mb, patch_drop)
            losses.append(float(masked_loss(recon, target, mb, patch_drop, args.patch_len).detach().cpu()))
    return float(np.mean(losses))


def encode_all(model: MaskedPatchEncoder, values: np.ndarray, masks: np.ndarray, batch_size: int, device: torch.device) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            xb = torch.tensor(values[start : start + batch_size], dtype=torch.float32, device=device)
            mb = torch.tensor(masks[start : start + batch_size], dtype=torch.float32, device=device)
            z, _, _ = model(xb, mb, None)
            out.append(z.detach().cpu().numpy())
    return np.nan_to_num(np.vstack(out).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)


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
    if len(train) == 0 or len(sample) == 0:
        return {"train_sample_mean_l2": float("nan"), "train_sample_std_l2": float("nan")}
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
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    views = [view.strip() for view in args.views.split(",") if view.strip()]
    seeds = [int(seed) for seed in args.seeds]
    device = choose_device(args.device)
    summary_rows = []
    for view in views:
        idx = select_channel_indices(groups, view)
        values = base_values[:, idx, :]
        masks = base_masks[:, idx, :]
        view_reports = []
        seed_embeddings = []
        view_dir = output_dir / view
        view_dir.mkdir(parents=True, exist_ok=True)
        for seed in seeds:
            z, report = train_one(values, masks, args, seed, device)
            seed_dir = view_dir / f"seed_{seed}"
            seed_dir.mkdir(parents=True, exist_ok=True)
            np.save(seed_dir / "embeddings.npy", z)
            write_latents(seed_dir / "embeddings.parquet", keys, z)
            report.update(
                {
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
            )
            (seed_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            view_reports.append(report)
            seed_embeddings.append(z)
            summary_rows.append({k: v for k, v in report.items() if k != "history"})
        z_mean = np.mean(seed_embeddings, axis=0).astype(np.float32)
        np.save(view_dir / "embeddings_mean.npy", z_mean)
        write_latents(view_dir / "embeddings_mean.parquet", keys, z_mean)
        view_report = {
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
    summary.to_csv(output_dir / "ssl_summary.csv", index=False)
    final = {
        "token_path": args.token_path,
        "views": views,
        "seeds": seeds,
        "device": str(device),
        "config": {
            "patch_len": args.patch_len,
            "d_model": args.d_model,
            "n_heads": args.n_heads,
            "temporal_layers": args.temporal_layers,
            "channel_layers": args.channel_layers,
            "mask_prob": args.mask_prob,
            "channel_drop_prob": args.channel_drop_prob,
            "epochs": args.epochs,
        },
        "summary": summary.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    display = summary[
        [
            "view",
            "seed",
            "channels_selected",
            "best_val_loss",
            "final_val_loss",
            "subject_centroid_leakage",
            "train_sample_mean_l2",
            "temporal_locality_gap",
            "embedding_effective_rank",
            "embedding_axis_std_mean",
        ]
    ].copy()
    md = [
        "# Domain Masked Patch Encoder v1",
        "",
        "## Purpose",
        "",
        "Train repeatable label-free masked patch encoders on the domain idea token views. This is an encoder experiment only; it does not train a label decoder.",
        "",
        "## Config",
        "",
        f"- Device: `{device}`",
        f"- Views: `{', '.join(views)}`",
        f"- Seeds: `{', '.join(str(s) for s in seeds)}`",
        f"- Patch length: `{args.patch_len}` 30-minute tokens = `{args.patch_len * 30}` minutes",
        f"- d_model: `{args.d_model}`",
        f"- Epochs: `{args.epochs}`",
        "",
        "## Summary",
        "",
        dataframe_to_markdown(display),
        "",
        "## Selection Rule",
        "",
        "Carry forward views that combine low validation reconstruction loss with low train/sample shift and low subject-centroid leakage. Do not promote a view just because it reconstructs well if it mostly identifies the subject.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train label-free masked patch encoders over domain idea token views.")
    parser.add_argument("--token-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/domain_masked_patch_encoder_v1")
    parser.add_argument("--views", default=",".join(DEFAULT_VIEWS))
    parser.add_argument("--seeds", type=int, nargs="+", default=[2026, 2027])
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=96)
    parser.add_argument("--val-fraction", type=float, default=0.18)
    parser.add_argument("--patch-len", type=int, default=4)
    parser.add_argument("--d-model", type=int, default=24)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--temporal-layers", type=int, default=1)
    parser.add_argument("--channel-layers", type=int, default=1)
    parser.add_argument("--dropout", type=float, default=0.10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--mask-prob", type=float, default=0.25)
    parser.add_argument("--channel-drop-prob", type=float, default=0.04)
    parser.add_argument("--noise-std", type=float, default=0.01)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
