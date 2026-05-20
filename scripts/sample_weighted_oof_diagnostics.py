from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class Candidate:
    name: str
    oof_path: Path
    submission_path: Path | None


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def load_candidates(items: list[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in items:
        parts = item.split(":")
        if len(parts) not in {2, 3}:
            raise ValueError("--candidate entries must be name:oof_path[:submission_path]")
        candidates.append(Candidate(parts[0], Path(parts[1]), Path(parts[2]) if len(parts) == 3 else None))
    return candidates


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred_cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(pred_cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file is missing prediction columns: {missing}")
    return np.clip(oof[pred_cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def row_losses(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log(1.0 - pred)).mean(axis=1)


def per_target_log_loss(y: pd.DataFrame, pred: np.ndarray, weights: np.ndarray | None = None) -> dict[str, float]:
    out = {}
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = float(log_loss(y[target].to_numpy(), pred[:, i], labels=[0, 1], sample_weight=weights))
    out["avg"] = float(np.mean([out[target] for target in TARGET_COLUMNS]))
    return out


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="test", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    test_pos = all_rows[all_rows["_split"].eq("test")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = test_pos
    return train_out, sample_out


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if weights.mean() > 0:
        weights = weights / weights.mean()
    table = pd.DataFrame(
        {
            "bin": [f"[{bins[i]:.3f},{bins[i + 1]:.3f})" for i in range(n_bins)],
            "train_frac": train_frac,
            "sample_frac": sample_frac,
            "weight_ratio": ratio,
        }
    )
    return weights.astype(float), table


def weighted_bootstrap_improvement(
    base_loss: np.ndarray,
    candidate_loss: np.ndarray,
    weights: np.ndarray,
    seed: int,
    n_bootstrap: int,
) -> dict[str, float]:
    diff = base_loss - candidate_loss
    weights = np.asarray(weights, dtype=float)
    weights = np.clip(weights, 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    weighted_improvement = float(np.average(diff, weights=weights))
    prob = weights / weights.sum()
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(diff), size=len(diff), replace=True, p=prob)
        boot[i] = float(diff[idx].mean())
    return {
        "weighted_improvement": weighted_improvement,
        "weighted_p025": float(np.quantile(boot, 0.025)),
        "weighted_p500": float(np.quantile(boot, 0.500)),
        "weighted_p975": float(np.quantile(boot, 0.975)),
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

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    bins = np.asarray([float(value) for value in args.position_bins.split(",")], dtype=float)
    bins[-1] = bins[-1] + 1e-6
    weights, bin_table = sample_position_weights(train, sample, bins)
    y = train[TARGET_COLUMNS]

    loaded: dict[str, dict[str, object]] = {}
    for candidate in load_candidates(args.candidates):
        oof = normalize_keys(pd.read_csv(candidate.oof_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{candidate.name} OOF keys do not match train keys: {candidate.oof_path}")
        pred = prediction_matrix(oof)
        loaded[candidate.name] = {
            "candidate": candidate,
            "pred": pred,
            "row_loss": row_losses(y, pred),
            "uniform": per_target_log_loss(y, pred),
            "weighted": per_target_log_loss(y, pred, weights),
        }
    if args.baseline not in loaded:
        raise ValueError(f"Baseline candidate not loaded: {args.baseline}")

    base = loaded[args.baseline]
    rows = []
    target_rows = []
    block_rows = []
    for name, item in loaded.items():
        pred = item["pred"]  # type: ignore[assignment]
        row_loss = item["row_loss"]  # type: ignore[assignment]
        boot = weighted_bootstrap_improvement(base["row_loss"], row_loss, weights, args.seed, args.bootstrap)  # type: ignore[arg-type]
        uniform = item["uniform"]  # type: ignore[assignment]
        weighted = item["weighted"]  # type: ignore[assignment]
        rows.append(
            {
                "name": name,
                "uniform_avg_log_loss": uniform["avg"],  # type: ignore[index]
                "weighted_avg_log_loss": weighted["avg"],  # type: ignore[index]
                "weighted_delta_vs_baseline": boot["weighted_improvement"],
                "weighted_p025": boot["weighted_p025"],
                "weighted_p500": boot["weighted_p500"],
                "weighted_p975": boot["weighted_p975"],
                "promote_weighted": bool(boot["weighted_p025"] > args.min_weighted_p025),
            }
        )
        for target in TARGET_COLUMNS:
            target_rows.append(
                {
                    "name": name,
                    "target": target,
                    "uniform_log_loss": uniform[target],  # type: ignore[index]
                    "weighted_log_loss": weighted[target],  # type: ignore[index]
                    "weighted_delta_vs_baseline": base["weighted"][target] - weighted[target],  # type: ignore[index]
                }
            )
        for block_name, lo, hi in [("mid", 1 / 3, 2 / 3), ("late", 2 / 3, 1.01), ("tail_20pct", 0.8, 1.01)]:
            idx = train.index[(train["panel_position"] >= lo) & (train["panel_position"] < hi)].to_numpy(dtype=int)
            if len(idx) == 0:
                continue
            base_loss = base["row_loss"][idx]  # type: ignore[index]
            cand_loss = row_loss[idx]  # type: ignore[index]
            block_rows.append(
                {
                    "name": name,
                    "block": block_name,
                    "n_rows": int(len(idx)),
                    "delta_vs_baseline": float(base_loss.mean() - cand_loss.mean()),
                }
            )

    summary = pd.DataFrame(rows).sort_values(["promote_weighted", "weighted_avg_log_loss"], ascending=[False, True]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    block_df = pd.DataFrame(block_rows)
    summary.to_csv(output_dir / "sample_weighted_summary.csv", index=False)
    target_df.to_csv(output_dir / "sample_weighted_target_scores.csv", index=False)
    block_df.to_csv(output_dir / "sample_weighted_block_scores.csv", index=False)
    bin_table.to_csv(output_dir / "sample_position_weight_bins.csv", index=False)

    report = {
        "baseline": args.baseline,
        "bin_table": bin_table.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "sample_weighted_oof_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# Sample-weighted OOF diagnostics",
        "",
        f"- Baseline: `{args.baseline}`",
        "- Weights match train rows to the submission sample panel-position distribution.",
        "",
        "## Position bins",
        "",
        dataframe_to_markdown(bin_table),
        "",
        "## Candidate summary",
        "",
        dataframe_to_markdown(summary),
        "",
        "## Target scores",
        "",
        dataframe_to_markdown(target_df),
        "",
        "## Block deltas",
        "",
        dataframe_to_markdown(block_df),
        "",
    ]
    (output_dir / "sample_weighted_oof_report.md").write_text("\n".join(md), encoding="utf-8")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OOF diagnostics weighted to the submission sample panel-position distribution.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/sample_weighted_oof_diagnostics")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", dest="candidates", action="append", required=True)
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--min-weighted-p025", type=float, default=0.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
