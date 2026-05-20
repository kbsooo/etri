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
class Source:
    name: str
    oof_path: Path
    submission_path: Path


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_source(value: str) -> Source:
    parts = value.split("=", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid source spec: {value}")
    name, rest = parts
    paths = rest.split(",", 1)
    if len(paths) != 2:
        raise ValueError(f"Invalid source paths: {value}")
    return Source(name=name.strip(), oof_path=Path(paths[0]), submission_path=Path(paths[1]))


def simplex_weights(n_sources: int, step: float) -> np.ndarray:
    ticks = int(round(1.0 / step))
    if not np.isclose(ticks * step, 1.0):
        raise ValueError("--step must divide 1.0")
    weights: list[list[float]] = []

    def rec(prefix: list[int], remaining: int, slots: int) -> None:
        if slots == 1:
            weights.append([*prefix, remaining])
            return
        for value in range(remaining + 1):
            rec([*prefix, value], remaining - value, slots - 1)

    rec([], ticks, n_sources)
    return np.array(weights, dtype=float) * step


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def score_target(y: np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(y, np.clip(pred, EPS, 1.0 - EPS), labels=[0, 1]))


def best_weight_for_target(y: np.ndarray, source_preds: np.ndarray, grid: np.ndarray) -> tuple[np.ndarray, float]:
    # source_preds shape: rows x sources
    blended = source_preds @ grid.T
    losses = np.array([score_target(y, blended[:, i]) for i in range(blended.shape[1])])
    best_idx = int(np.argmin(losses))
    return grid[best_idx], float(losses[best_idx])


def average_score(y_frame: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: score_target(y_frame[target].to_numpy(int), pred[:, i])
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    lines = [
        "| " + " | ".join(display.columns) + " |",
        "| " + " | ".join(["---"] * len(display.columns)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy())
    return "\n".join(lines)


def build_portfolio(args: argparse.Namespace) -> None:
    sources = [parse_source(value) for value in args.source]
    if len(sources) < 2:
        raise ValueError("At least two sources are required")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    oof_frames = {source.name: normalize_keys(pd.read_csv(source.oof_path)) for source in sources}
    sub_frames = {source.name: normalize_keys(pd.read_csv(source.submission_path)) for source in sources}
    base_name = sources[0].name
    base_oof = oof_frames[base_name]
    base_sub = sub_frames[base_name]
    for source in sources[1:]:
        if not base_oof[KEY_COLUMNS].equals(oof_frames[source.name][KEY_COLUMNS]):
            raise ValueError(f"OOF key mismatch for {source.name}")
        if not base_sub[KEY_COLUMNS].equals(sub_frames[source.name][KEY_COLUMNS]):
            raise ValueError(f"Submission key mismatch for {source.name}")

    oof_stack = np.stack([prediction_matrix(oof_frames[source.name]) for source in sources], axis=2)
    sub_stack = np.stack([submission_matrix(sub_frames[source.name]) for source in sources], axis=2)
    grid = simplex_weights(len(sources), args.step)

    global_rows = []
    global_pred = np.zeros((len(base_oof), len(TARGET_COLUMNS)), dtype=float)
    global_sub = np.zeros((len(base_sub), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        y = base_oof[target].to_numpy(int)
        weights, loss = best_weight_for_target(y, oof_stack[:, target_i, :], grid)
        global_pred[:, target_i] = oof_stack[:, target_i, :] @ weights
        global_sub[:, target_i] = sub_stack[:, target_i, :] @ weights
        row = {"target": target, "log_loss": loss}
        row.update({f"w_{source.name}": float(weights[i]) for i, source in enumerate(sources)})
        global_rows.append(row)

    global_score, global_per_target = average_score(base_oof, global_pred)

    groups = base_oof["subject_id"].astype(str).to_numpy()
    guarded_pred = np.zeros_like(global_pred)
    guarded_rows = []
    for heldout in sorted(pd.unique(groups)):
        train_mask = groups != heldout
        valid_mask = groups == heldout
        for target_i, target in enumerate(TARGET_COLUMNS):
            weights, train_loss = best_weight_for_target(
                base_oof.loc[train_mask, target].to_numpy(int),
                oof_stack[train_mask, target_i, :],
                grid,
            )
            guarded_pred[valid_mask, target_i] = oof_stack[valid_mask, target_i, :] @ weights
            valid_loss = score_target(
                base_oof.loc[valid_mask, target].to_numpy(int),
                guarded_pred[valid_mask, target_i],
            )
            row = {
                "heldout_subject": heldout,
                "target": target,
                "train_log_loss": train_loss,
                "valid_log_loss": valid_loss,
                "valid_rows": int(valid_mask.sum()),
            }
            row.update({f"w_{source.name}": float(weights[i]) for i, source in enumerate(sources)})
            guarded_rows.append(row)
    guarded_score, guarded_per_target = average_score(base_oof, guarded_pred)

    global_oof = base_oof[KEY_COLUMNS + TARGET_COLUMNS].copy()
    guarded_oof = base_oof[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = base_sub[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        global_oof[f"pred_{target}"] = np.clip(global_pred[:, i], EPS, 1.0 - EPS)
        guarded_oof[f"pred_{target}"] = np.clip(guarded_pred[:, i], EPS, 1.0 - EPS)
        submission[target] = np.clip(global_sub[:, i], EPS, 1.0 - EPS)

    global_oof.to_csv(output_dir / "oof_latent_source_weighted_portfolio.csv", index=False)
    guarded_oof.to_csv(output_dir / "oof_subject_guarded_latent_source_weighted_portfolio.csv", index=False)
    submission.to_csv(output_dir / "submission_latent_source_weighted_portfolio.csv", index=False)
    pd.DataFrame(global_rows).to_csv(output_dir / "global_target_weights.csv", index=False)
    pd.DataFrame(guarded_rows).to_csv(output_dir / "subject_guarded_target_weights.csv", index=False)
    pd.DataFrame(
        [
            {"name": "global_weighted", "avg_log_loss": global_score, **global_per_target},
            {"name": "subject_guarded", "avg_log_loss": guarded_score, **guarded_per_target},
        ]
    ).to_csv(output_dir / "score.csv", index=False)

    report = {
        "sources": [source.name for source in sources],
        "step": args.step,
        "global": {"avg_log_loss": global_score, "per_target": global_per_target, "weights": global_rows},
        "subject_guarded": {"avg_log_loss": guarded_score, "per_target": guarded_per_target},
        "paths": {
            "submission": str(output_dir / "submission_latent_source_weighted_portfolio.csv"),
            "global_oof": str(output_dir / "oof_latent_source_weighted_portfolio.csv"),
            "subject_guarded_oof": str(output_dir / "oof_subject_guarded_latent_source_weighted_portfolio.csv"),
        },
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Latent source weighted portfolio",
        "",
        f"- Global OOF: `{global_score:.6f}`",
        f"- Subject-guarded OOF: `{guarded_score:.6f}`",
        "",
        "## Global target weights",
        "",
        dataframe_to_markdown(pd.DataFrame(global_rows)),
        "",
        "## Scores",
        "",
        dataframe_to_markdown(pd.read_csv(output_dir / "score.csv")),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"global={global_score:.6f} subject_guarded={guarded_score:.6f}")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a target-wise convex blend of latent-derived prediction sources.")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="name=oof_path,submission_path. Repeat for each source.",
    )
    parser.add_argument("--output-dir", default="outputs/latent_source_weighted_portfolio_v1")
    parser.add_argument("--step", type=float, default=0.05)
    return parser.parse_args()


def main() -> None:
    build_portfolio(parse_args())


if __name__ == "__main__":
    main()
