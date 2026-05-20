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


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def load_candidates(items: list[str]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for item in items:
        parts = item.split(":")
        if len(parts) != 2:
            raise ValueError("--candidate entries must be name:oof_path")
        candidates.append(Candidate(parts[0], Path(parts[1])))
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


def per_target_log_loss(y: pd.DataFrame, pred: np.ndarray, indices: np.ndarray | None = None) -> dict[str, float]:
    if indices is None:
        indices = np.arange(len(y))
    out = {}
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, i], labels=[0, 1]))
    out["avg"] = float(np.mean([out[target] for target in TARGET_COLUMNS]))
    return out


def bootstrap_improvement(
    base_loss: np.ndarray,
    candidate_loss: np.ndarray,
    seed: int,
    n_bootstrap: int,
) -> dict[str, float]:
    diff = base_loss - candidate_loss
    if len(diff) == 0:
        return {"improvement": 0.0, "p025": 0.0, "p500": 0.0, "p975": 0.0}
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(diff), len(diff))
        boot[i] = float(diff[idx].mean())
    return {
        "improvement": float(diff.mean()),
        "p025": float(np.quantile(boot, 0.025)),
        "p500": float(np.quantile(boot, 0.500)),
        "p975": float(np.quantile(boot, 0.975)),
    }


def add_panel_columns(train: pd.DataFrame) -> pd.DataFrame:
    ordered = train.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["subject_day_index"] = ordered.groupby("subject_id").cumcount()
    subject_max = ordered.groupby("subject_id")["subject_day_index"].transform("max").replace(0, 1)
    ordered["subject_position"] = ordered["subject_day_index"] / subject_max
    ordered["subject_count"] = ordered.groupby("subject_id")["subject_day_index"].transform("max") + 1
    ordered["reverse_index"] = ordered["subject_count"] - ordered["subject_day_index"] - 1
    return ordered.sort_values("_idx").drop(columns="_idx").reset_index(drop=True)


def make_blocks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    blocks: dict[str, np.ndarray] = {}
    blocks["all"] = np.arange(len(frame), dtype=int)
    blocks["early_third"] = frame.index[frame["subject_position"] < 1 / 3].to_numpy(dtype=int)
    blocks["mid_third"] = frame.index[(frame["subject_position"] >= 1 / 3) & (frame["subject_position"] < 2 / 3)].to_numpy(dtype=int)
    blocks["late_third"] = frame.index[frame["subject_position"] >= 2 / 3].to_numpy(dtype=int)
    blocks["tail_20pct"] = frame.index[frame["subject_position"] >= 0.8].to_numpy(dtype=int)
    for subject, group in frame.groupby("subject_id", sort=True):
        blocks[f"subject_{subject}"] = group.index.to_numpy(dtype=int)
    return blocks


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *body])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = add_panel_columns(normalize_keys(pd.read_csv(args.train_path)))
    y = train[TARGET_COLUMNS]
    blocks = make_blocks(train)
    block_names = ["all", "early_third", "mid_third", "late_third", "tail_20pct"]

    loaded: dict[str, dict[str, object]] = {}
    for candidate in load_candidates(args.candidates):
        oof = normalize_keys(pd.read_csv(candidate.oof_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{candidate.name} OOF keys do not match train keys: {candidate.oof_path}")
        pred = prediction_matrix(oof)
        loaded[candidate.name] = {
            "pred": pred,
            "row_loss": row_losses(y, pred),
            "overall": per_target_log_loss(y, pred),
        }
    if args.baseline not in loaded:
        raise ValueError(f"Baseline not loaded: {args.baseline}")

    base = loaded[args.baseline]
    summary_rows = []
    block_rows = []
    target_rows = []

    for name, item in loaded.items():
        pred = item["pred"]  # type: ignore[assignment]
        row_loss = item["row_loss"]  # type: ignore[assignment]
        overall = item["overall"]  # type: ignore[assignment]
        base_loss = base["row_loss"]  # type: ignore[assignment]

        block_scores = {}
        block_deltas = {}
        block_boots = {}
        for block_name in block_names:
            idx = blocks[block_name]
            score = per_target_log_loss(y, pred, idx)["avg"]  # type: ignore[arg-type]
            base_score = per_target_log_loss(y, base["pred"], idx)["avg"]  # type: ignore[arg-type]
            boot = bootstrap_improvement(base_loss[idx], row_loss[idx], args.seed, args.bootstrap)  # type: ignore[index]
            block_scores[block_name] = score
            block_deltas[block_name] = base_score - score
            block_boots[block_name] = boot
            block_rows.append(
                {
                    "name": name,
                    "block": block_name,
                    "n_rows": int(len(idx)),
                    "avg_log_loss": score,
                    "delta_vs_baseline": block_deltas[block_name],
                    "improvement_p025": boot["p025"],
                    "improvement": boot["improvement"],
                    "improvement_p975": boot["p975"],
                }
            )

        subject_deltas = []
        for subject, group in train.groupby("subject_id", sort=True):
            idx = group.index.to_numpy(dtype=int)
            score = per_target_log_loss(y, pred, idx)["avg"]  # type: ignore[arg-type]
            base_score = per_target_log_loss(y, base["pred"], idx)["avg"]  # type: ignore[arg-type]
            subject_deltas.append(base_score - score)

        late_idx = blocks["late_third"]
        late_target_delta = {}
        for target_i, target in enumerate(TARGET_COLUMNS):
            target_score = float(log_loss(y.iloc[late_idx][target], pred[late_idx, target_i], labels=[0, 1]))  # type: ignore[index]
            base_target_score = float(log_loss(y.iloc[late_idx][target], base["pred"][late_idx, target_i], labels=[0, 1]))  # type: ignore[index]
            late_target_delta[target] = base_target_score - target_score
            target_rows.append(
                {
                    "name": name,
                    "target": target,
                    "late_log_loss": target_score,
                    "late_delta_vs_baseline": late_target_delta[target],
                }
            )

        promote = (
            block_boots["all"]["p025"] > 0
            and block_deltas["late_third"] >= -args.max_block_regression
            and block_deltas["tail_20pct"] >= -args.max_tail_regression
            and min(subject_deltas) >= -args.max_subject_regression
            and min(late_target_delta.values()) >= -args.max_late_target_regression
        )
        summary_rows.append(
            {
                "name": name,
                "avg_log_loss": overall["avg"],  # type: ignore[index]
                "overall_p025": block_boots["all"]["p025"],
                "overall_improvement": block_boots["all"]["improvement"],
                "early_delta": block_deltas["early_third"],
                "mid_delta": block_deltas["mid_third"],
                "late_delta": block_deltas["late_third"],
                "tail20_delta": block_deltas["tail_20pct"],
                "late_p025": block_boots["late_third"]["p025"],
                "tail20_p025": block_boots["tail_20pct"]["p025"],
                "worst_subject_delta": float(min(subject_deltas)),
                "worst_late_target_delta": float(min(late_target_delta.values())),
                "promote": bool(promote),
            }
        )

    summary = pd.DataFrame(summary_rows).sort_values(["promote", "avg_log_loss"], ascending=[False, True]).reset_index(drop=True)
    block_df = pd.DataFrame(block_rows)
    target_df = pd.DataFrame(target_rows)
    summary.to_csv(output_dir / "block_candidate_summary.csv", index=False)
    block_df.to_csv(output_dir / "block_scores.csv", index=False)
    target_df.to_csv(output_dir / "late_target_scores.csv", index=False)

    report = {
        "baseline": args.baseline,
        "promotion_rule": {
            "overall_p025": "> 0",
            "late_delta": f">= {-args.max_block_regression}",
            "tail20_delta": f">= {-args.max_tail_regression}",
            "worst_subject_delta": f">= {-args.max_subject_regression}",
            "worst_late_target_delta": f">= {-args.max_late_target_regression}",
        },
        "summary": summary.to_dict(orient="records"),
    }
    (output_dir / "block_oof_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# Block OOF diagnostics",
        "",
        f"- Baseline: `{args.baseline}`",
        "- Blocks are per-subject chronological train thirds plus the final 20% tail.",
        "- Positive deltas mean the candidate improves over baseline.",
        "",
        "## Candidate summary",
        "",
        dataframe_to_markdown(summary),
        "",
        "## Block scores",
        "",
        dataframe_to_markdown(block_df[block_df["block"].isin(block_names)]),
        "",
        "## Late-block target deltas",
        "",
        dataframe_to_markdown(target_df),
        "",
    ]
    (output_dir / "block_oof_report.md").write_text("\n".join(md), encoding="utf-8")
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OOF diagnostics for public/private-like chronological block shift.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--output-dir", default="outputs/block_oof_diagnostics")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", dest="candidates", action="append", required=True)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-block-regression", type=float, default=0.0015)
    parser.add_argument("--max-tail-regression", type=float, default=0.0025)
    parser.add_argument("--max-subject-regression", type=float, default=0.006)
    parser.add_argument("--max-late-target-regression", type=float, default=0.010)
    return parser.parse_args()


if __name__ == "__main__":
    main()
