from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


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
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = sample_pos
    return train_out, sample_out


def support_mask(frame: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    frame_bin = np.digitize(frame["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    sample_counts = np.bincount(sample_bin, minlength=n_bins)
    frame_counts = np.bincount(frame_bin, minlength=n_bins)
    supported = sample_counts > 0
    mask = supported[frame_bin]
    table = pd.DataFrame(
        {
            "bin": [f"[{bins[i]:.3f},{bins[i + 1]:.3f})" for i in range(n_bins)],
            "train_count": frame_counts,
            "sample_count": sample_counts,
            "sample_supported": supported,
        }
    )
    return mask.astype(bool), table


def position_range_mask(frame: pd.DataFrame, min_position: float, max_position: float) -> np.ndarray:
    positions = frame["panel_position"].to_numpy(dtype=float)
    return (positions >= min_position) & (positions < max_position)


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
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing prediction columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    missing = sorted(set(TARGET_COLUMNS) - set(submission.columns))
    if missing:
        raise ValueError(f"Submission file missing target columns: {missing}")
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def row_loss(y_arr: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def per_target_log_loss(y_arr: np.ndarray, pred: np.ndarray, indices: np.ndarray | None = None) -> dict[str, float]:
    if indices is None:
        indices = np.arange(len(y_arr), dtype=int)
    scores = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        scores[target] = float(log_loss(y_arr[indices, target_i], pred[indices, target_i], labels=[0, 1]))
    scores["avg"] = float(np.mean([scores[target] for target in TARGET_COLUMNS]))
    return scores


def bootstrap_delta(delta: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(delta), size=len(delta))
        values[i] = float(delta[idx].mean())
    return {
        "p025": float(np.quantile(values, 0.025)),
        "p500": float(np.quantile(values, 0.500)),
        "p975": float(np.quantile(values, 0.975)),
    }


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_raw = normalize_keys(pd.read_csv(args.train_path))
    sample_raw = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train_raw, sample_raw)
    bins = np.asarray([float(value) for value in args.position_bins.split(",")], dtype=float)
    bins[-1] = bins[-1] + 1e-6
    train_supported, support_table = support_mask(train, sample, bins)
    sample_supported, _ = support_mask(sample, sample, bins)
    train_range = position_range_mask(train, args.min_position, args.max_position)
    sample_range = position_range_mask(sample, args.min_position, args.max_position)
    if args.respect_sample_support:
        train_supported = train_supported & train_range
        sample_supported = sample_supported & sample_range
    else:
        # Used for explicit panel-position correction experiments. The same
        # position rule is applied to train and submission rows; if the
        # submission has no rows in a local-only window, submission predictions
        # remain unchanged by construction.
        train_supported = train_range
        sample_supported = sample_range

    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    source_oof = normalize_keys(pd.read_csv(args.source_oof))
    base_submission_df = normalize_keys(pd.read_csv(args.base_submission))
    source_submission_df = normalize_keys(pd.read_csv(args.source_submission))
    for name, frame, reference in [
        ("base_oof", base_oof, train),
        ("source_oof", source_oof, train),
        ("base_submission", base_submission_df, sample),
        ("source_submission", source_submission_df, sample),
    ]:
        if not frame[KEY_COLUMNS].equals(reference[KEY_COLUMNS]):
            raise ValueError(f"{name} keys do not match expected keys")

    base_pred = prediction_matrix(base_oof)
    source_pred = prediction_matrix(source_oof)
    base_sub = submission_matrix(base_submission_df)
    source_sub = submission_matrix(source_submission_df)
    final_pred = base_pred.copy()
    final_sub = base_sub.copy()

    target_rows = []
    for target in parse_str_list(args.targets):
        if target not in TARGET_COLUMNS:
            raise ValueError(f"Unknown target: {target}")
        target_i = TARGET_COLUMNS.index(target)
        blended = blend_values(base_pred[:, target_i], source_pred[:, target_i], args.weight, args.mode)
        final_pred[train_supported, target_i] = blended[train_supported]
        blended_sub = blend_values(base_sub[:, target_i], source_sub[:, target_i], args.weight, args.mode)
        final_sub[sample_supported, target_i] = blended_sub[sample_supported]
        target_rows.append(
            {
                "target": target,
                "supported_train_rows": int(train_supported.sum()),
                "supported_sample_rows": int(sample_supported.sum()),
                "range_train_rows": int(train_range.sum()),
                "range_sample_rows": int(sample_range.sum()),
                "min_position": args.min_position,
                "max_position": args.max_position,
                "weight": args.weight,
                "mode": args.mode,
            }
        )

    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    base_loss = row_loss(y_arr, base_pred)
    final_loss = row_loss(y_arr, final_pred)
    delta = base_loss - final_loss
    boot = bootstrap_delta(delta, args.seed, args.bootstrap)
    support_idx = np.flatnonzero(train_supported)
    nonsupport_idx = np.flatnonzero(~train_supported)
    summary = {
        "base_avg": per_target_log_loss(y_arr, base_pred)["avg"],
        "final_avg": per_target_log_loss(y_arr, final_pred)["avg"],
        "improvement": float(delta.mean()),
        "p025": boot["p025"],
        "p500": boot["p500"],
        "p975": boot["p975"],
        "support_delta": float(delta[support_idx].mean()) if len(support_idx) else 0.0,
        "non_support_delta": float(delta[nonsupport_idx].mean()) if len(nonsupport_idx) else 0.0,
    }

    oof = train_raw[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = final_pred[:, target_i]
    oof_path = output_dir / "oof_sample_support_target_blend.csv"
    oof.to_csv(oof_path, index=False)

    submission = sample_raw.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_sub[:, target_i]
    submission_path = output_dir / "submission_sample_support_target_blend.csv"
    submission.to_csv(submission_path, index=False)

    target_df = pd.DataFrame(target_rows)
    target_df.to_csv(output_dir / "sample_support_target_selection.csv", index=False)
    support_table.to_csv(output_dir / "sample_support_bins.csv", index=False)
    report = {
        "summary": summary,
        "target_selection": target_df.to_dict(orient="records"),
        "support_bins": support_table.to_dict(orient="records"),
        "position_range": {
            "min_position": args.min_position,
            "max_position": args.max_position,
            "train_rows": int(train_range.sum()),
            "sample_rows": int(sample_range.sum()),
            "applied_train_rows": int(train_supported.sum()),
            "applied_sample_rows": int(sample_supported.sum()),
        },
        "args": vars(args),
    }
    (output_dir / "sample_support_target_blend_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# Sample-support Target Blend",
        "",
        (
            "The blend is applied only to train/sample panel-position bins that exist in the submission sample."
            if args.respect_sample_support
            else "The blend is applied by the explicit panel-position range, regardless of sample-support bins."
        ),
        f"Position range filter: [{args.min_position:.6f}, {args.max_position:.6f}).",
        "",
        "## Summary",
        "",
        dataframe_to_markdown(pd.DataFrame([summary])),
        "",
        "## Support bins",
        "",
        dataframe_to_markdown(support_table),
        "",
        "## Target selection",
        "",
        dataframe_to_markdown(target_df),
        "",
    ]
    (output_dir / "sample_support_target_blend_report.md").write_text("\n".join(md), encoding="utf-8")
    print(
        f"final={summary['final_avg']:.6f} improvement={summary['improvement']:.6f} "
        f"p025={summary['p025']:.6f} support_delta={summary['support_delta']:.6f}"
    )
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply target blends only in submission-supported panel-position bins.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--source-oof", required=True)
    parser.add_argument("--source-submission", required=True)
    parser.add_argument("--targets", default="S4")
    parser.add_argument("--weight", type=float, default=1.0)
    parser.add_argument("--mode", default="logit", choices=["prob", "logit"])
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--min-position", type=float, default=0.0)
    parser.add_argument("--max-position", type=float, default=1.000001)
    parser.add_argument(
        "--no-sample-support",
        action="store_false",
        dest="respect_sample_support",
        help="Apply the explicit position range even when that bin is absent from the submission sample.",
    )
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.set_defaults(respect_sample_support=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
