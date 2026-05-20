from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class Source:
    name: str
    oof_path: Path


@dataclass(frozen=True)
class Window:
    name: str
    lo: float
    hi: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_sources(items: list[str]) -> list[Source]:
    out: list[Source] = []
    for item in items:
        parts = item.split(":", 1)
        if len(parts) != 2:
            raise ValueError("--source entries must be name:oof_path")
        out.append(Source(parts[0], Path(parts[1])))
    return out


def parse_windows(value: str) -> list[Window]:
    out: list[Window] = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        out.append(Window(name, float(lo), float(hi)))
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out["panel_position"] = train_pos["panel_position"]
    sample_out["panel_position"] = sample_pos["panel_position"]
    return train_out, sample_out


def sample_support_mask(frame: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    frame_bin = np.digitize(frame["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_counts = np.bincount(sample_bin, minlength=len(bins) - 1)
    return (sample_counts > 0)[frame_bin]


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if weights.mean() > 0:
        weights = weights / weights.mean()
    return weights.astype(float)


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing prediction columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def blend_values(base: np.ndarray, source: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = base + weight * (source - base)
    elif mode == "logit":
        out = sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base)))
    else:
        raise ValueError(f"Unknown mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def row_losses(y_arr: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def weighted_bootstrap(diff: np.ndarray, weights: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    weights = np.clip(weights.astype(float), 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    prob = weights / weights.sum()
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(diff), size=len(diff), replace=True, p=prob)
        boot[i] = float(diff[idx].mean())
    return {
        "p025": float(np.quantile(boot, 0.025)),
        "p500": float(np.quantile(boot, 0.500)),
        "p975": float(np.quantile(boot, 0.975)),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_raw = normalize_keys(pd.read_csv(args.train_path))
    sample_raw = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train_raw, sample_raw)
    bins = np.asarray(parse_float_list(args.position_bins), dtype=float)
    bins[-1] = bins[-1] + 1e-6
    support = sample_support_mask(train, sample, bins)
    weights = sample_position_weights(train, sample, bins)

    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    if not base_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    base_pred = prediction_matrix(base_oof)
    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    base_loss = row_losses(y_arr, base_pred)

    windows = parse_windows(args.windows)
    rows = []
    for source in parse_sources(args.sources):
        oof = normalize_keys(pd.read_csv(source.oof_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{source.name} OOF keys do not match train keys")
        source_pred = prediction_matrix(oof)
        for window in windows:
            in_window = (train["panel_position"].to_numpy(dtype=float) >= window.lo) & (
                train["panel_position"].to_numpy(dtype=float) < window.hi
            )
            mask = support & in_window
            if not mask.any():
                continue
            for target_i, target in enumerate(TARGET_COLUMNS):
                for weight in parse_float_list(args.weights):
                    final = base_pred.copy()
                    final[:, target_i] = base_pred[:, target_i]
                    blended = blend_values(base_pred[:, target_i], source_pred[:, target_i], weight, args.mode)
                    final[mask, target_i] = blended[mask]
                    cand_loss = row_losses(y_arr, final)
                    diff = base_loss - cand_loss
                    boot = weighted_bootstrap(diff, weights, args.seed, args.bootstrap)
                    target_base = log_loss(y_arr[:, target_i], base_pred[:, target_i], labels=[0, 1])
                    target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1])
                    weighted_target_base = log_loss(y_arr[:, target_i], base_pred[:, target_i], labels=[0, 1], sample_weight=weights)
                    weighted_target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1], sample_weight=weights)
                    row = {
                        "source": source.name,
                        "target": target,
                        "window": window.name,
                        "weight": weight,
                        "applied_rows": int(mask.sum()),
                        "uniform_improvement": float(diff.mean()),
                        "uniform_avg_log_loss": float(cand_loss.mean()),
                        "weighted_improvement": float(np.average(diff, weights=weights)),
                        "weighted_p025": boot["p025"],
                        "weighted_p500": boot["p500"],
                        "weighted_p975": boot["p975"],
                        "target_delta": float(target_base - target_cand),
                        "weighted_target_delta": float(weighted_target_base - weighted_target_cand),
                    }
                    for block_name, lo, hi in [("mid", 1 / 3, 2 / 3), ("late", 2 / 3, 1.01), ("tail20", 0.8, 1.01)]:
                        idx = train.index[(train["panel_position"] >= lo) & (train["panel_position"] < hi)].to_numpy(dtype=int)
                        row[f"{block_name}_delta"] = float(diff[idx].mean()) if len(idx) else 0.0
                    rows.append(row)

    results = pd.DataFrame(rows)
    results = results.sort_values(["weighted_p025", "weighted_improvement"], ascending=[False, False]).reset_index(drop=True)
    results.to_csv(output_dir / "position_window_target_scores.csv", index=False)
    print(results.head(args.print_top).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search target/window blends under submission panel-position support.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--source", dest="sources", action="append", required=True)
    parser.add_argument("--output-dir", default="outputs/position_window_target_search")
    parser.add_argument("--weights", default="1.0,0.8,0.65,0.5,0.3")
    parser.add_argument("--mode", default="logit", choices=["prob", "logit"])
    parser.add_argument("--windows", default="mid:0.3333333333:0.6666666667,tail:0.8:1.000001,mid_tail:0.3333333333:1.000001")
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--print-top", type=int, default=30)
    return parser.parse_args()


if __name__ == "__main__":
    main()
