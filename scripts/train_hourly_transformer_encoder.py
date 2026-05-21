from __future__ import annotations

import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path

# macOS conda/brew stacks can load separate OpenMP runtimes through torch and
# scikit-learn. This script is an offline local experiment, so we allow the
# duplicate runtime and pin CPU thread pools while torch itself still uses MPS.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from train_pruned_state_decoder import average_log_loss, drift_vs_reference, subject_prior, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, KEY_COLUMNS, SEED, TARGET_COLUMNS, make_subject_time_folds, normalize_keys


@dataclass(frozen=True)
class ViewSpec:
    name: str
    mode: str
    tokens: tuple[str, ...] = ()


class DayTransformerEncoder(nn.Module):
    def __init__(self, n_features: int, n_tokens: int, d_model: int, n_heads: int, n_layers: int, dropout: float) -> None:
        super().__init__()
        self.input_proj = nn.Linear(n_features, d_model)
        self.cls = nn.Parameter(torch.zeros(1, 1, d_model))
        self.pos = nn.Parameter(torch.zeros(1, n_tokens + 1, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)
        self.reconstruct = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Linear(d_model, n_features),
        )
        nn.init.normal_(self.cls, std=0.02)
        nn.init.normal_(self.pos, std=0.02)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch = x.shape[0]
        tokens = self.input_proj(x)
        cls = self.cls.expand(batch, -1, -1)
        encoded = self.encoder(torch.cat([cls, tokens], dim=1) + self.pos[:, : tokens.shape[1] + 1])
        encoded = self.norm(encoded)
        return encoded[:, 0], self.reconstruct(encoded[:, 1:])


class DayGRUEncoder(nn.Module):
    def __init__(self, n_features: int, d_model: int, dropout: float) -> None:
        super().__init__()
        self.input_proj = nn.Linear(n_features, d_model)
        self.gru = nn.GRU(
            input_size=d_model,
            hidden_size=d_model,
            num_layers=1,
            batch_first=True,
            dropout=0.0,
        )
        self.norm = nn.LayerNorm(d_model)
        self.reconstruct = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, n_features),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        token = self.input_proj(x)
        encoded, hidden = self.gru(token)
        encoded = self.norm(encoded)
        cls = self.norm(hidden[-1])
        return cls, self.reconstruct(encoded)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda value: f"{float(value):.6f}")
    headers = [str(col) for col in out.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in out.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in out.columns) + " |")
    return "\n".join(lines)


def parse_views(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def view_specs() -> dict[str, ViewSpec]:
    return {
        "full": ViewSpec("full", "all"),
        "no_gps": ViewSpec("no_gps", "drop", ("gps", "lat", "lon")),
        "no_phone": ViewSpec("no_phone", "drop", ("screen", "charging", "ac", "scr")),
        "no_sleep": ViewSpec("no_sleep", "drop", ("hr", "pedo", "step", "cal", "light", "still")),
        "no_missingness": ViewSpec("no_missingness", "drop_missing"),
        "only_core": ViewSpec(
            "only_core",
            "only",
            ("ratio", "screen", "charging", "step", "speed", "hr", "light", "gps", "amb_", "agree"),
        ),
        "only_rhythm": ViewSpec("only_rhythm", "only", ("still", "screen", "charging", "hr", "light", "step")),
        "only_cross_modal": ViewSpec("only_cross_modal", "only", ("agree", "only_act", "only_ped", "amb_", "gps", "screen")),
        "only_event": ViewSpec("only_event", "only", ("ev_",)),
        "no_event": ViewSpec("no_event", "drop", ("ev_",)),
    }


def numeric_feature_columns(frame: pd.DataFrame) -> list[str]:
    blocked = {"subject_id", "date", "lifelog_date", "hod", "in_keys"}
    return [
        col
        for col in frame.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(frame[col])
    ]


def select_columns(columns: list[str], spec: ViewSpec) -> list[str]:
    if spec.mode == "all":
        return columns
    lower = {col: col.lower() for col in columns}
    if spec.mode == "drop":
        selected = [col for col in columns if not any(token in lower[col] for token in spec.tokens)]
    elif spec.mode == "only":
        selected = [col for col in columns if any(token in lower[col] for token in spec.tokens)]
    elif spec.mode == "drop_missing":
        selected = [col for col in columns if not col.endswith("__isna") and "missing" not in lower[col]]
    else:
        raise ValueError(f"Unknown view mode: {spec.mode}")
    if not selected:
        raise ValueError(f"View {spec.name} selected no columns")
    return selected


def load_hourly_table(args: argparse.Namespace) -> pd.DataFrame:
    base_path = args.token_table_path or args.hourly_path
    base = pd.read_parquet(base_path).copy()
    base["date"] = pd.to_datetime(base["date"]).dt.strftime("%Y-%m-%d")
    if args.token_col != "hod":
        base = base.rename(columns={args.token_col: "hod"})
    table = base

    optional_paths = [] if args.token_table_path else [
        (args.coherence_path, "coh__"),
        (args.hrv_path, "hrv__"),
        (args.ambience_path, "amb__"),
    ]
    for raw_path, prefix in optional_paths:
        if not raw_path:
            continue
        path = Path(raw_path)
        if not path.exists():
            continue
        extra = pd.read_parquet(path).copy()
        extra["date"] = pd.to_datetime(extra["date"]).dt.strftime("%Y-%m-%d")
        rename = {
            col: f"{prefix}{col}"
            for col in extra.columns
            if col not in {"subject_id", "date", "hod"}
        }
        extra = extra.rename(columns=rename)
        table = table.merge(extra, on=["subject_id", "date", "hod"], how="left", validate="one_to_one")

    table["subject_id"] = table["subject_id"].astype(str)
    table["hod"] = table["hod"].astype(int)
    return table


def all_day_keys(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    train_keys = train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train)))
    sample_keys = sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample)))
    keys = pd.concat([train_keys, sample_keys], ignore_index=True)
    keys["date"] = keys["lifelog_date"].astype(str)
    keys["_date"] = pd.to_datetime(keys["lifelog_date"])
    keys = keys.sort_values(["_split", "_row"]).reset_index(drop=True)

    ordered = keys.sort_values(["subject_id", "_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    keys = keys.merge(
        ordered[["_split", "_row", "panel_index", "panel_position"]],
        on=["_split", "_row"],
        how="left",
        validate="one_to_one",
    )
    return keys


def build_sequence_tensor(
    hourly: pd.DataFrame,
    keys: pd.DataFrame,
    spec: ViewSpec,
    tokens_per_day: int,
    add_deviation_features: bool,
) -> tuple[np.ndarray, list[str], dict[str, float]]:
    base_cols = numeric_feature_columns(hourly)
    selected_base = select_columns(base_cols, spec)

    numeric = hourly[["subject_id", "date", "hod"] + selected_base].copy()
    skeleton = keys[["subject_id", "date"]].loc[keys.index.repeat(tokens_per_day)].reset_index(drop=True)
    skeleton["hod"] = np.tile(np.arange(tokens_per_day), len(keys)).astype(int)
    indexed = skeleton.merge(numeric, on=["subject_id", "date", "hod"], how="left", validate="one_to_one")

    values = indexed[selected_base].replace([np.inf, -np.inf], np.nan)
    observed = values.notna().astype(float)
    observed.columns = [f"{col}__isna" for col in selected_base]
    observed = 1.0 - observed

    medians = values.median(axis=0, skipna=True).fillna(0.0)
    filled = values.fillna(medians).astype(float)
    scaler = StandardScaler()
    scaled = pd.DataFrame(scaler.fit_transform(filled), columns=selected_base)
    scaled = scaled.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    dev_parts = []
    if add_deviation_features:
        baseline_keys = indexed[["subject_id", "hod"]].reset_index(drop=True)
        keyed = pd.concat([baseline_keys, scaled], axis=1)
        mean = keyed.groupby(["subject_id", "hod"], sort=False)[selected_base].transform("mean")
        std = keyed.groupby(["subject_id", "hod"], sort=False)[selected_base].transform("std").replace(0.0, np.nan)
        z = ((scaled - mean) / std).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        z = z.clip(-6.0, 6.0)
        dev_parts.append(z.add_prefix("devz__"))
        dev_parts.append(z.abs().add_prefix("devabs__"))

    hod = indexed["hod"].to_numpy(float)
    aux = pd.DataFrame(
        {
            "time__hod_sin": np.sin(2.0 * np.pi * hod / float(tokens_per_day)),
            "time__hod_cos": np.cos(2.0 * np.pi * hod / float(tokens_per_day)),
        }
    )
    day_repeats = np.repeat(keys[["_date", "panel_index", "panel_position"]].to_numpy(object), tokens_per_day, axis=0)
    weekday = pd.to_datetime(day_repeats[:, 0]).weekday.to_numpy(float)
    aux["time__weekday_sin"] = np.sin(2.0 * np.pi * weekday / 7.0)
    aux["time__weekday_cos"] = np.cos(2.0 * np.pi * weekday / 7.0)
    aux["time__panel_index"] = np.asarray(day_repeats[:, 1], dtype=float)
    aux["time__panel_position"] = np.asarray(day_repeats[:, 2], dtype=float)
    aux["missing__token_frac"] = observed.mean(axis=1).to_numpy(float)

    feature_frame = pd.concat([scaled, *dev_parts, observed.reset_index(drop=True), aux], axis=1)
    feature_frame = feature_frame.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if spec.mode == "drop_missing":
        cols = [col for col in feature_frame.columns if "__isna" not in col and not col.startswith("missing__")]
        feature_frame = feature_frame[cols]

    expected_rows = len(keys) * tokens_per_day
    if len(feature_frame) != expected_rows:
        raise ValueError(f"Sequence row mismatch: {len(feature_frame)} != {expected_rows}")
    arr = feature_frame.to_numpy(np.float32)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    arr = np.clip(arr, -8.0, 8.0).reshape(len(keys), tokens_per_day, feature_frame.shape[1])
    diagnostics = {
        "n_days": float(len(keys)),
        "n_base_features": float(len(selected_base)),
        "n_token_features": float(feature_frame.shape[1]),
        "mean_missing_fraction": float(aux["missing__token_frac"].mean()),
        "add_deviation_features": float(add_deviation_features),
    }
    return arr, feature_frame.columns.tolist(), diagnostics


def train_ssl_encoder(
    x: np.ndarray,
    args: argparse.Namespace,
    device: torch.device,
) -> tuple[np.ndarray, list[float]]:
    seed_everything(args.seed)
    tensor = torch.tensor(x, dtype=torch.float32)
    dataset = TensorDataset(tensor)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, drop_last=False)
    if args.encoder_type == "transformer":
        model = DayTransformerEncoder(
            n_features=x.shape[2],
            n_tokens=x.shape[1],
            d_model=args.d_model,
            n_heads=args.n_heads,
            n_layers=args.n_layers,
            dropout=args.dropout,
        ).to(device)
    elif args.encoder_type == "gru":
        model = DayGRUEncoder(
            n_features=x.shape[2],
            d_model=args.d_model,
            dropout=args.dropout,
        ).to(device)
    else:
        raise ValueError(f"Unknown encoder_type: {args.encoder_type}")
    encoder_params = sum(parameter.numel() for parameter in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    history: list[float] = []
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        total_count = 0
        for (batch,) in loader:
            batch = batch.to(device)
            mask = torch.rand(batch.shape[:2], device=device) < args.mask_prob
            if not mask.any():
                mask[:, random.randrange(batch.shape[1])] = True
            noisy = batch.clone()
            if args.noise_std > 0:
                noisy = noisy + torch.randn_like(noisy) * args.noise_std
            noisy[mask] = 0.0
            _, recon = model(noisy)
            masked_loss = (recon[mask] - batch[mask]).pow(2).mean()
            all_loss = (recon - batch).pow(2).mean()
            loss = masked_loss + args.all_token_loss_weight * all_loss
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total_loss += float(loss.detach().cpu()) * len(batch)
            total_count += len(batch)
        history.append(total_loss / max(1, total_count))

    model.eval()
    embeddings: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(x), args.batch_size):
            batch = torch.tensor(x[start : start + args.batch_size], dtype=torch.float32, device=device)
            cls, _ = model(batch)
            embeddings.append(cls.detach().cpu().numpy())
    embedding = np.vstack(embeddings).astype(np.float32)
    embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)
    embedding = np.clip(embedding, -20.0, 20.0)
    return embedding, history, encoder_params


def sanitize_probe_matrix(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(values, -20.0, 20.0)


def fit_logreg_probe(
    x_fit: np.ndarray,
    y_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    c_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(np.unique(y_fit)) < 2:
        value = float(y_fit[0])
        return np.full(len(x_eval), value), np.full(len(x_sample), value)
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000, random_state=SEED)
    model.fit(x_fit, y_fit)
    return model.predict_proba(x_eval)[:, 1], model.predict_proba(x_sample)[:, 1]


def fit_ridge_residual(
    x_fit: np.ndarray,
    residual_fit: np.ndarray,
    x_eval: np.ndarray,
    x_sample: np.ndarray,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    model = Ridge(alpha=alpha, random_state=SEED)
    model.fit(x_fit, residual_fit)
    return model.predict(x_eval), model.predict(x_sample)


def evaluate_embedding_probe(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    z_train: np.ndarray,
    z_sample: np.ndarray,
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    folds = make_subject_time_folds(train, args.n_folds)
    candidate_oof: dict[str, np.ndarray] = {}
    candidate_sample: dict[str, np.ndarray] = {}

    for alpha in args.prior_alphas:
        name = f"subject_prior_a{alpha:g}".replace(".", "p")
        oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
        sample_folds = []
        for fold in folds:
            oof[fold.val_idx] = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], alpha)
            sample_folds.append(subject_prior(train.iloc[fold.train_idx], sample, alpha))
        candidate_oof[name] = np.clip(oof, EPS, 1.0 - EPS)
        candidate_sample[name] = np.clip(np.mean(sample_folds, axis=0), EPS, 1.0 - EPS)

    for c_value in args.c_values:
        for blend in args.logreg_blends:
            name = f"transformer_logreg_c{c_value:g}_w{blend:g}".replace(".", "p")
            oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
            sample_folds = []
            for fold in folds:
                scaler = StandardScaler()
                x_fit = sanitize_probe_matrix(scaler.fit_transform(z_train[fold.train_idx]))
                x_eval = sanitize_probe_matrix(scaler.transform(z_train[fold.val_idx]))
                x_sample = sanitize_probe_matrix(scaler.transform(z_sample))
                prior_eval = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.probe_prior_alpha)
                prior_sample = subject_prior(train.iloc[fold.train_idx], sample, args.probe_prior_alpha)
                fold_pred = np.zeros((len(fold.val_idx), len(TARGET_COLUMNS)), dtype=float)
                fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
                for target_i, target in enumerate(TARGET_COLUMNS):
                    pred_eval, pred_sample = fit_logreg_probe(
                        x_fit,
                        train.iloc[fold.train_idx][target].to_numpy(int),
                        x_eval,
                        x_sample,
                        c_value,
                    )
                    fold_pred[:, target_i] = (1.0 - blend) * prior_eval[:, target_i] + blend * pred_eval
                    fold_sample[:, target_i] = (1.0 - blend) * prior_sample[:, target_i] + blend * pred_sample
                oof[fold.val_idx] = fold_pred
                sample_folds.append(fold_sample)
            candidate_oof[name] = np.clip(oof, EPS, 1.0 - EPS)
            candidate_sample[name] = np.clip(np.mean(sample_folds, axis=0), EPS, 1.0 - EPS)

    for ridge_alpha in args.ridge_alphas:
        for blend in args.ridge_blends:
            name = f"transformer_ridge_resid_a{ridge_alpha:g}_w{blend:g}".replace(".", "p")
            oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
            sample_folds = []
            for fold in folds:
                scaler = StandardScaler()
                x_fit = sanitize_probe_matrix(scaler.fit_transform(z_train[fold.train_idx]))
                x_eval = sanitize_probe_matrix(scaler.transform(z_train[fold.val_idx]))
                x_sample = sanitize_probe_matrix(scaler.transform(z_sample))
                prior_fit = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.train_idx], args.probe_prior_alpha)
                prior_eval = subject_prior(train.iloc[fold.train_idx], train.iloc[fold.val_idx], args.probe_prior_alpha)
                prior_sample = subject_prior(train.iloc[fold.train_idx], sample, args.probe_prior_alpha)
                fold_pred = np.zeros((len(fold.val_idx), len(TARGET_COLUMNS)), dtype=float)
                fold_sample = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
                for target_i, target in enumerate(TARGET_COLUMNS):
                    residual = train.iloc[fold.train_idx][target].to_numpy(float) - prior_fit[:, target_i]
                    pred_eval, pred_sample = fit_ridge_residual(x_fit, residual, x_eval, x_sample, ridge_alpha)
                    fold_pred[:, target_i] = prior_eval[:, target_i] + blend * pred_eval
                    fold_sample[:, target_i] = prior_sample[:, target_i] + blend * pred_sample
                oof[fold.val_idx] = fold_pred
                sample_folds.append(fold_sample)
            candidate_oof[name] = np.clip(oof, EPS, 1.0 - EPS)
            candidate_sample[name] = np.clip(np.mean(sample_folds, axis=0), EPS, 1.0 - EPS)

    rows = []
    for name, pred in candidate_oof.items():
        avg, per_target = average_log_loss(train[TARGET_COLUMNS], pred)
        rows.append({"source": name, "avg_log_loss": avg, **per_target})
    score_df = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    return score_df, candidate_oof, candidate_sample


def targetwise_prediction(
    score_df: pd.DataFrame,
    candidates_oof: dict[str, np.ndarray],
    candidates_sample: dict[str, np.ndarray],
    train: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, dict[str, str], dict[str, float]]:
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    sample = np.zeros((next(iter(candidates_sample.values())).shape[0], len(TARGET_COLUMNS)), dtype=float)
    source_by_target: dict[str, str] = {}
    loss_by_target: dict[str, float] = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        best_source = None
        best_loss = math.inf
        for source, pred in candidates_oof.items():
            loss = float(log_loss(train[target].to_numpy(int), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
            if loss < best_loss:
                best_loss = loss
                best_source = source
        if best_source is None:
            raise RuntimeError(f"No source selected for {target}")
        oof[:, target_i] = candidates_oof[best_source][:, target_i]
        sample[:, target_i] = candidates_sample[best_source][:, target_i]
        source_by_target[target] = best_source
        loss_by_target[target] = best_loss
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(sample, EPS, 1.0 - EPS), source_by_target, loss_by_target


def device_for_training() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def run(args: argparse.Namespace) -> None:
    seed_everything(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    hourly = load_hourly_table(args)
    keys = all_day_keys(train, sample)

    device = device_for_training()
    requested_views = parse_views(args.views)
    specs = view_specs()
    unknown = sorted(set(requested_views) - set(specs))
    if unknown:
        raise ValueError(f"Unknown views: {unknown}. Available: {sorted(specs)}")

    all_reports = []
    best_view_name = ""
    best_score = math.inf
    best_oof = None
    best_sample = None
    best_candidates: dict[str, np.ndarray] = {}
    best_sample_candidates: dict[str, np.ndarray] = {}

    for view_name in requested_views:
        view_dir = output_dir / view_name
        view_dir.mkdir(parents=True, exist_ok=True)
        x, feature_names, seq_diag = build_sequence_tensor(
            hourly,
            keys,
            specs[view_name],
            tokens_per_day=args.tokens_per_day,
            add_deviation_features=args.add_deviation_features,
        )
        z_all, loss_history, encoder_params = train_ssl_encoder(x, args, device)
        z_train = z_all[: len(train)]
        z_sample = z_all[len(train) :]
        np.savez_compressed(
            view_dir / "embeddings.npz",
            train=z_train,
            sample=z_sample,
            all=z_all,
            feature_names=np.array(feature_names, dtype=object),
        )

        score_df, candidates_oof, candidates_sample = evaluate_embedding_probe(train, sample, z_train, z_sample, args)
        target_oof, target_sample, target_sources, target_losses = targetwise_prediction(
            score_df, candidates_oof, candidates_sample, train
        )
        target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
        best_global = score_df.iloc[0]
        global_source = str(best_global["source"])
        drift_global = drift_vs_reference(
            sample,
            candidates_sample[global_source],
            Path(args.reference_submission) if args.reference_submission else None,
        )
        drift_target = drift_vs_reference(
            sample,
            target_sample,
            Path(args.reference_submission) if args.reference_submission else None,
        )

        score_df.to_csv(view_dir / "probe_scores.csv", index=False)
        write_prediction(view_dir / "oof_best_global.csv", train, candidates_oof[global_source], oof=True)
        write_prediction(view_dir / "submission_best_global.csv", sample, candidates_sample[global_source], oof=False)
        write_prediction(view_dir / "oof_targetwise.csv", train, target_oof, oof=True)
        write_prediction(view_dir / "submission_targetwise.csv", sample, target_sample, oof=False)

        report = {
            "view": view_name,
            "encoder_type": args.encoder_type,
            "encoder_params": int(encoder_params),
            "device": str(device),
            "sequence": seq_diag,
            "n_features": len(feature_names),
            "epochs": args.epochs,
            "final_ssl_loss": float(loss_history[-1]),
            "best_global_source": global_source,
            "best_global_avg_log_loss": float(best_global["avg_log_loss"]),
            "best_global_per_target": {target: float(best_global[target]) for target in TARGET_COLUMNS},
            "targetwise_avg_log_loss": float(target_avg),
            "targetwise_per_target": {target: float(target_per[target]) for target in TARGET_COLUMNS},
            "targetwise_sources": target_sources,
            "targetwise_source_losses": target_losses,
            "drift_vs_reference_best_global": drift_global,
            "drift_vs_reference_targetwise": drift_target,
            "ssl_loss_history": [float(v) for v in loss_history],
        }
        (view_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        top_table = score_df.head(8)
        md = [
            f"# Hourly Transformer Encoder - {view_name}",
            "",
            "## Representation",
            "",
            f"- Encoder type: `{args.encoder_type}`",
            f"- Encoder params: `{encoder_params}`",
            f"- Days: `{int(seq_diag['n_days'])}`",
            f"- Token shape: `{args.tokens_per_day} x {len(feature_names)}`",
            f"- Base hourly features selected: `{int(seq_diag['n_base_features'])}`",
            f"- Mean token missing fraction: `{seq_diag['mean_missing_fraction']:.6f}`",
            f"- Device: `{device}`",
            f"- SSL final loss: `{loss_history[-1]:.6f}`",
            "",
            "## Probe Scores",
            "",
            dataframe_to_markdown(top_table),
            "",
            "## Target-Wise Selection",
            "",
            f"- Target-wise avg logloss: `{target_avg:.6f}`",
            f"- Drift vs reference: `{drift_target.get('mean_abs_drift', float('nan')):.6f}`",
            "",
            dataframe_to_markdown(pd.DataFrame([{"target": k, "source": v, "loss": target_losses[k]} for k, v in target_sources.items()])),
            "",
            "## Interpretation",
            "",
            "This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.",
        ]
        (view_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
        all_reports.append(report)

        view_best_score = min(float(best_global["avg_log_loss"]), float(target_avg))
        if view_best_score < best_score:
            best_score = view_best_score
            best_view_name = view_name
            if float(best_global["avg_log_loss"]) <= float(target_avg):
                best_oof = candidates_oof[global_source]
                best_sample = candidates_sample[global_source]
            else:
                best_oof = target_oof
                best_sample = target_sample
            best_candidates = candidates_oof
            best_sample_candidates = candidates_sample

    if best_oof is None or best_sample is None:
        raise RuntimeError("No best prediction was produced")

    summary_rows = []
    for report in all_reports:
        summary_rows.append(
            {
                "view": report["view"],
                "encoder_type": report["encoder_type"],
                "encoder_params": report["encoder_params"],
                "ssl_loss": report["final_ssl_loss"],
                "best_global": report["best_global_avg_log_loss"],
                "targetwise": report["targetwise_avg_log_loss"],
                "drift_global": report["drift_vs_reference_best_global"].get("mean_abs_drift"),
                "drift_targetwise": report["drift_vs_reference_targetwise"].get("mean_abs_drift"),
            }
        )
    summary_df = pd.DataFrame(summary_rows).sort_values("targetwise").reset_index(drop=True)
    summary_df.to_csv(output_dir / "summary_scores.csv", index=False)
    write_prediction(output_dir / "oof_hourly_transformer_best.csv", train, best_oof, oof=True)
    write_prediction(output_dir / "submission_hourly_transformer_best.csv", sample, best_sample, oof=False)

    best_avg, best_per = average_log_loss(train[TARGET_COLUMNS], best_oof)
    diagnostics = {
        "best_view": best_view_name,
        "best_avg_log_loss": best_avg,
        "best_per_target": best_per,
        "views": all_reports,
        "summary": summary_rows,
        "drift_vs_reference_best": drift_vs_reference(sample, best_sample, Path(args.reference_submission) if args.reference_submission else None),
    }
    (output_dir / "report.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    md = [
        "# Hourly Sequence Encoder v1",
        "",
        "## Goal",
        "",
        "Replace the tabular-pruned encoder branch with a sequence-first representation: one subject-day becomes token sequence, and a tiny sequence encoder learns a day embedding from masked-token reconstruction before any label decoder sees the 450 labels.",
        "",
        "## View Comparison",
        "",
        dataframe_to_markdown(summary_df),
        "",
        "## Best Candidate",
        "",
        f"- Best view: `{best_view_name}`",
        f"- OOF avg logloss: `{best_avg:.6f}`",
        f"- Drift vs reference: `{diagnostics['drift_vs_reference_best'].get('mean_abs_drift', float('nan')):.6f}`",
        "",
        "## Target Loss",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": k, "loss": v} for k, v in best_per.items()])),
        "",
        "## Decision",
        "",
        "This run is an encoder validity test, not a final submission strategy. Adoption requires the sequence latent to beat the subject-prior residual scaffold or reveal a view-specific target signal that can be reused in the decoder.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a self-supervised hourly sequence day encoder.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--hourly-path", default="artifacts/03_hourly_grid.parquet")
    parser.add_argument("--token-table-path", default="")
    parser.add_argument("--token-col", default="hod")
    parser.add_argument("--tokens-per-day", type=int, default=24)
    parser.add_argument("--coherence-path", default="artifacts/09_coherence_hourly.parquet")
    parser.add_argument("--hrv-path", default="artifacts/07_hrv_hourly.parquet")
    parser.add_argument("--ambience-path", default="artifacts/08_ambience_hourly_buckets.parquet")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/hourly_transformer_encoder_v1")
    parser.add_argument("--views", default="full,no_gps,no_phone,no_sleep,only_core")
    parser.add_argument("--add-deviation-features", action="store_true")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--encoder-type", choices=["transformer", "gru"], default="transformer")
    parser.add_argument("--d-model", type=int, default=64)
    parser.add_argument("--n-heads", type=int, default=4)
    parser.add_argument("--n-layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.10)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--mask-prob", type=float, default=0.25)
    parser.add_argument("--noise-std", type=float, default=0.02)
    parser.add_argument("--all-token-loss-weight", type=float, default=0.10)
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
