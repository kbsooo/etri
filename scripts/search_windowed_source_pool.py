from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


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


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_windows(value: str) -> list[Window]:
    windows: list[Window] = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        windows.append(Window(name=name, lo=float(lo), hi=float(hi)))
    return windows


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


def sample_support_mask(frame: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    frame_bin = np.digitize(frame["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_counts = np.bincount(sample_bin, minlength=len(bins) - 1)
    return (sample_counts > 0)[frame_bin]


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    buckets: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            buckets[fold].extend(chunk.tolist())
    return [np.array(sorted(bucket), dtype=int) for bucket in buckets]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"missing prediction columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def blend_column(base: np.ndarray, source: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = base + weight * (source - base)
    elif mode == "logit":
        out = sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base)))
    else:
        raise ValueError(f"unknown mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def row_losses(y_arr: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def target_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1.0 - y) * np.log1p(-pred))


def bootstrap_p025(delta: np.ndarray, weights: np.ndarray, seed: int, n_bootstrap: int) -> float:
    if n_bootstrap <= 0:
        return float("nan")
    weights = np.clip(weights.astype(float), 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    prob = weights / weights.sum()
    rng = np.random.default_rng(seed)
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(delta), size=len(delta), replace=True, p=prob)
        values[i] = float(delta[idx].mean())
    return float(np.quantile(values, 0.025))


def excluded(path: Path, patterns: list[str]) -> bool:
    text = str(path)
    return any(fnmatch.fnmatch(text, pattern) or pattern in text for pattern in patterns)


def infer_submission_path(oof_path: Path) -> str:
    name = oof_path.name
    if name.startswith("oof_"):
        candidate = oof_path.with_name("submission_" + name.removeprefix("oof_"))
        if candidate.exists():
            return str(candidate)
    submissions = sorted(oof_path.parent.glob("submission_*.csv"))
    if len(submissions) == 1:
        return str(submissions[0])
    return ""


def discover_sources(args: argparse.Namespace) -> list[Path]:
    paths: set[Path] = set()
    for pattern in args.source_glob:
        paths.update(Path().glob(pattern))
    sources = [
        path
        for path in paths
        if path.is_file()
        and path.suffix == ".csv"
        and not excluded(path, args.exclude)
    ]
    return sorted(sources)


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
    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    if not base_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("base OOF keys do not match train keys")
    base_pred = prediction_matrix(base_oof)
    base_row_loss = row_losses(y_arr, base_pred)
    base_target_losses = [target_loss(y_arr[:, i], base_pred[:, i]) for i in range(len(TARGET_COLUMNS))]
    folds = make_subject_time_folds(train, args.folds)
    subject_groups = {
        str(subject): group.index.to_numpy(dtype=int)
        for subject, group in train.groupby("subject_id", sort=True)
    }
    block_indices = {
        "mid": train.index[(train["panel_position"] >= 1 / 3) & (train["panel_position"] < 2 / 3)].to_numpy(dtype=int),
        "late_mid": train.index[(train["panel_position"] >= 2 / 3) & (train["panel_position"] < 0.8)].to_numpy(dtype=int),
        "tail20": train.index[train["panel_position"] >= 0.8].to_numpy(dtype=int),
    }
    windows = parse_windows(args.windows)
    blend_weights = parse_float_list(args.weights)
    modes = [mode.strip() for mode in args.modes.split(",") if mode.strip()]

    rows: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    for source_path in discover_sources(args):
        try:
            source_oof = normalize_keys(pd.read_csv(source_path))
            if not source_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
                raise ValueError("key mismatch")
            source_pred = prediction_matrix(source_oof)
        except Exception as exc:
            skipped.append({"source_oof": str(source_path), "reason": str(exc)})
            continue
        for window in windows:
            in_window = (train["panel_position"].to_numpy(dtype=float) >= window.lo) & (
                train["panel_position"].to_numpy(dtype=float) < window.hi
            )
            mask = support & in_window
            if not mask.any():
                continue
            for target_i, target in enumerate(TARGET_COLUMNS):
                source_col = source_pred[:, target_i]
                for weight in blend_weights:
                    for mode in modes:
                        blended = blend_column(base_pred[:, target_i], source_col, weight, mode)
                        target_delta = base_target_losses[target_i] - target_loss(y_arr[:, target_i], blended)
                        row_delta = np.zeros(len(train), dtype=float)
                        row_delta[mask] = target_delta[mask] / len(TARGET_COLUMNS)
                        uniform_delta = float(row_delta.mean())
                        weighted_delta = float(np.average(row_delta, weights=weights))
                        if weighted_delta < args.min_weighted_delta:
                            continue
                        fold_deltas = [float(row_delta[idx].mean()) for idx in folds]
                        subject_deltas = [float(row_delta[idx].mean()) for idx in subject_groups.values()]
                        mid_delta = float(row_delta[block_indices["mid"]].mean()) if len(block_indices["mid"]) else 0.0
                        late_mid_delta = (
                            float(row_delta[block_indices["late_mid"]].mean()) if len(block_indices["late_mid"]) else 0.0
                        )
                        tail20_delta = (
                            float(row_delta[block_indices["tail20"]].mean()) if len(block_indices["tail20"]) else 0.0
                        )
                        worst_subject_delta = float(min(subject_deltas)) if subject_deltas else 0.0
                        folds_improved = int(sum(delta > 0 for delta in fold_deltas))
                        if uniform_delta < args.min_uniform_delta:
                            continue
                        if folds_improved < args.min_folds:
                            continue
                        if worst_subject_delta < args.min_worst_subject_delta:
                            continue
                        if mid_delta < args.min_mid_delta:
                            continue
                        if late_mid_delta < args.min_late_mid_delta:
                            continue
                        if tail20_delta < args.min_tail20_delta:
                            continue
                        rows.append(
                            {
                                "source_oof": str(source_path),
                                "source_submission": infer_submission_path(source_path),
                                "target": target,
                                "window": window.name,
                                "weight": float(weight),
                                "mode": mode,
                                "applied_rows": int(mask.sum()),
                                "uniform_delta": uniform_delta,
                                "weighted_delta": weighted_delta,
                                "folds_improved": folds_improved,
                                "mid_delta": mid_delta,
                                "late_mid_delta": late_mid_delta,
                                "tail20_delta": tail20_delta,
                                "worst_subject_delta": worst_subject_delta,
                                "fold_deltas": json.dumps(fold_deltas),
                                "has_submission_pair": bool(infer_submission_path(source_path)),
                            }
                        )

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(["weighted_delta", "uniform_delta"], ascending=[False, False]).reset_index(drop=True)
        if args.bootstrap_top > 0 and args.bootstrap > 0:
            p025_values: list[float] = [float("nan")] * len(result)
            top = result.head(args.bootstrap_top)
            for idx, row in top.iterrows():
                source_pred = prediction_matrix(normalize_keys(pd.read_csv(row["source_oof"])))
                target_i = TARGET_COLUMNS.index(str(row["target"]))
                window = next(item for item in windows if item.name == row["window"])
                in_window = (train["panel_position"].to_numpy(dtype=float) >= window.lo) & (
                    train["panel_position"].to_numpy(dtype=float) < window.hi
                )
                mask = support & in_window
                blended = blend_column(
                    base_pred[:, target_i],
                    source_pred[:, target_i],
                    float(row["weight"]),
                    str(row["mode"]),
                )
                target_delta = base_target_losses[target_i] - target_loss(y_arr[:, target_i], blended)
                row_delta = np.zeros(len(train), dtype=float)
                row_delta[mask] = target_delta[mask] / len(TARGET_COLUMNS)
                p025_values[idx] = bootstrap_p025(row_delta, weights, args.seed + idx, args.bootstrap)
            result["weighted_p025"] = p025_values
            result = result.sort_values(
                ["weighted_p025", "weighted_delta", "uniform_delta"],
                ascending=[False, False, False],
                na_position="last",
            ).reset_index(drop=True)

    result.to_csv(output_dir / "windowed_source_pool_scores.csv", index=False)
    pd.DataFrame(skipped).to_csv(output_dir / "skipped_sources.csv", index=False)
    print(result.head(args.print_top).to_string(index=False) if not result.empty else "no candidates")
    print(f"scored={len(result)} skipped={len(skipped)} saved={output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fast screen target/window corrections across a large OOF source pool.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-glob", action="append", default=["outputs/*/oof_*.csv"])
    parser.add_argument(
        "--exclude",
        action="append",
        default=[
            "forward_label_prior",
            "forward_prior",
            "bidirectional_label_prior",
            "with_forward_prior",
            "relaxed_subject",
            "public_feedback",
            "subject_adaptive_smoothing",
        ],
    )
    parser.add_argument("--windows", default="mid:0.3333333333:0.6666666667,late_mid:0.6666666667:0.8,tail20:0.8:1.000001,mid_tail:0.3333333333:1.000001")
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--weights", default="0.03,0.05,0.08,0.1,0.15,0.2,0.3,0.5,0.65,0.8,1.0")
    parser.add_argument("--modes", default="logit,prob")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--min-weighted-delta", type=float, default=0.00001)
    parser.add_argument("--min-uniform-delta", type=float, default=-0.00005)
    parser.add_argument("--min-folds", type=int, default=2)
    parser.add_argument("--min-worst-subject-delta", type=float, default=-0.0010)
    parser.add_argument("--min-mid-delta", type=float, default=-0.00025)
    parser.add_argument("--min-late-mid-delta", type=float, default=-0.00025)
    parser.add_argument("--min-tail20-delta", type=float, default=-0.00025)
    parser.add_argument("--bootstrap-top", type=int, default=200)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--print-top", type=int, default=40)
    return parser.parse_args()


if __name__ == "__main__":
    main()
