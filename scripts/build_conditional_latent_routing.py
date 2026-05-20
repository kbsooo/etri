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


@dataclass(frozen=True)
class Bin:
    name: str
    lo: float
    hi: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_source(value: str) -> Source:
    name, rest = value.split("=", 1)
    oof_path, submission_path = rest.split(",", 1)
    return Source(name.strip(), Path(oof_path), Path(submission_path))


def parse_bins(value: str) -> list[Bin]:
    bins = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        bins.append(Bin(name=name, lo=float(lo), hi=float(hi)))
    return bins


def parse_weights(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def safe_logit(pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return np.log(pred / (1.0 - pred))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def logit_blend(base: np.ndarray, source: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base))), EPS, 1.0 - EPS)


def target_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(y, np.clip(pred, EPS, 1.0 - EPS), labels=[0, 1]))


def score_frame(train: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per = {
        target: target_loss(train[target].to_numpy(int), pred[:, i])
        for i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per.values()))), per


def intervals_overlap(left_lo: float, left_hi: float, right_lo: float, right_hi: float) -> bool:
    return max(left_lo, right_lo) < min(left_hi, right_hi)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    train_pos = ordered[ordered["_split"].eq("train")].sort_values("_row")["panel_position"].to_numpy(float)
    sample_pos = ordered[ordered["_split"].eq("sample")].sort_values("_row")["panel_position"].to_numpy(float)
    return train_pos, sample_pos


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


def build(args: argparse.Namespace) -> None:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    base_submission = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train")
    if not base_submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    active_targets = [target.strip().upper() for target in args.targets.split(",") if target.strip()]
    unknown_targets = sorted(set(active_targets) - set(TARGET_COLUMNS))
    if unknown_targets:
        raise ValueError(f"Unknown targets in --targets: {unknown_targets}")
    if not active_targets:
        active_targets = TARGET_COLUMNS.copy()
    sources = [parse_source(value) for value in args.source]
    bins = parse_bins(args.bins)
    weights = parse_weights(args.weights)
    train_pos, sample_pos = add_panel_position(train, sample)
    base_pred = prediction_matrix(base_oof)
    base_sub = submission_matrix(base_submission)
    source_frames = {}
    for source in sources:
        oof = normalize_keys(pd.read_csv(source.oof_path))
        submission = normalize_keys(pd.read_csv(source.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"OOF key mismatch: {source.name}")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"Submission key mismatch: {source.name}")
        source_frames[source.name] = {"oof": prediction_matrix(oof), "submission": submission_matrix(submission)}

    def source_allowed_for_target(source_name: str, target: str) -> bool:
        if not args.match_source_prefix:
            return True
        return source_name.lower().startswith(f"{target.lower()}_")

    base_score, base_per = score_frame(train, base_pred)
    candidate_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        if target not in active_targets:
            continue
        y = train[target].to_numpy(int)
        base_loss = base_per[target]
        for source in sources:
            if not source_allowed_for_target(source.name, target):
                continue
            source_oof = source_frames[source.name]["oof"]
            for bin_ in bins:
                train_mask = (train_pos >= bin_.lo) & (train_pos < bin_.hi)
                sample_mask = (sample_pos >= bin_.lo) & (sample_pos < bin_.hi)
                if int(train_mask.sum()) < args.min_train_rows:
                    continue
                if int(sample_mask.sum()) < args.min_sample_rows:
                    continue
                for weight in weights:
                    moved = base_pred[:, target_i].copy()
                    blended = logit_blend(base_pred[:, target_i], source_oof[:, target_i], weight)
                    moved[train_mask] = blended[train_mask]
                    loss = target_loss(y, moved)
                    candidate_rows.append(
                        {
                            "target": target,
                            "source": source.name,
                            "bin": bin_.name,
                            "lo": bin_.lo,
                            "hi": bin_.hi,
                            "weight": weight,
                            "train_rows": int(train_mask.sum()),
                            "sample_rows": int(sample_mask.sum()),
                            "base_log_loss": base_loss,
                            "log_loss": loss,
                            "improvement": base_loss - loss,
                        }
                    )
    candidates = pd.DataFrame(candidate_rows).sort_values("improvement", ascending=False)
    candidates.to_csv(output_dir / "candidate_moves.csv", index=False)

    routed_pred = base_pred.copy()
    routed_sub = base_sub.copy()
    selected = []
    if args.max_moves_per_target <= 1:
        for target in TARGET_COLUMNS:
            if target not in active_targets:
                selected.append({"target": target, "source": "base", "bin": "all", "weight": 0.0, "improvement": 0.0})
                continue
            target_candidates = candidates[
                candidates["target"].eq(target)
                & (candidates["improvement"] >= args.min_improvement)
            ].sort_values("improvement", ascending=False)
            if len(target_candidates) == 0:
                selected.append({"target": target, "source": "base", "bin": "all", "weight": 0.0, "improvement": 0.0})
            else:
                selected.append(target_candidates.iloc[0].to_dict())
    else:
        for target_i, target in enumerate(TARGET_COLUMNS):
            if target not in active_targets:
                selected.append({"target": target, "source": "base", "bin": "all", "weight": 0.0, "improvement": 0.0, "move_index": 0})
                continue
            y = train[target].to_numpy(int)
            current = routed_pred[:, target_i].copy()
            current_loss = target_loss(y, current)
            target_selected = []
            for move_idx in range(args.max_moves_per_target):
                best_row = None
                best_pred = None
                best_loss = current_loss
                for source in sources:
                    if not source_allowed_for_target(source.name, target):
                        continue
                    source_oof = source_frames[source.name]["oof"]
                    for bin_ in bins:
                        if not args.allow_overlap:
                            if any(intervals_overlap(bin_.lo, bin_.hi, float(row["lo"]), float(row["hi"])) for row in target_selected):
                                continue
                        train_mask = (train_pos >= bin_.lo) & (train_pos < bin_.hi)
                        sample_mask = (sample_pos >= bin_.lo) & (sample_pos < bin_.hi)
                        if int(train_mask.sum()) < args.min_train_rows:
                            continue
                        if int(sample_mask.sum()) < args.min_sample_rows:
                            continue
                        for weight in weights:
                            candidate = current.copy()
                            blended = logit_blend(current, source_oof[:, target_i], weight)
                            candidate[train_mask] = blended[train_mask]
                            loss = target_loss(y, candidate)
                            if loss < best_loss - args.min_improvement:
                                best_loss = loss
                                best_pred = candidate
                                best_row = {
                                    "target": target,
                                    "source": source.name,
                                    "bin": bin_.name,
                                    "lo": bin_.lo,
                                    "hi": bin_.hi,
                                    "weight": weight,
                                    "train_rows": int(train_mask.sum()),
                                    "sample_rows": int(sample_mask.sum()),
                                    "base_log_loss": current_loss,
                                    "log_loss": loss,
                                    "improvement": current_loss - loss,
                                    "move_index": move_idx + 1,
                                }
                if best_row is None or best_pred is None:
                    break
                current = best_pred
                current_loss = best_loss
                target_selected.append(best_row)
                selected.append(best_row)
            if not target_selected:
                selected.append({"target": target, "source": "base", "bin": "all", "weight": 0.0, "improvement": 0.0, "move_index": 0})
            routed_pred[:, target_i] = current

    selected_df = pd.DataFrame(selected)

    if args.max_moves_per_target <= 1:
        for _, row in selected_df.iterrows():
            if row["source"] == "base":
                continue
            target_i = TARGET_COLUMNS.index(str(row["target"]))
            train_mask = (train_pos >= float(row["lo"])) & (train_pos < float(row["hi"]))
            sample_mask = (sample_pos >= float(row["lo"])) & (sample_pos < float(row["hi"]))
            source = source_frames[str(row["source"])]
            train_blend = logit_blend(base_pred[:, target_i], source["oof"][:, target_i], float(row["weight"]))
            sample_blend = logit_blend(base_sub[:, target_i], source["submission"][:, target_i], float(row["weight"]))
            routed_pred[train_mask, target_i] = train_blend[train_mask]
            routed_sub[sample_mask, target_i] = sample_blend[sample_mask]
    else:
        for _, row in selected_df.iterrows():
            if row["source"] == "base":
                continue
            target_i = TARGET_COLUMNS.index(str(row["target"]))
            sample_mask = (sample_pos >= float(row["lo"])) & (sample_pos < float(row["hi"]))
            source = source_frames[str(row["source"])]
            sample_blend = logit_blend(routed_sub[:, target_i], source["submission"][:, target_i], float(row["weight"]))
            routed_sub[sample_mask, target_i] = sample_blend[sample_mask]

    routed_score, routed_per = score_frame(train, routed_pred)
    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = sample[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = routed_pred[:, i]
        submission[target] = routed_sub[:, i]
    oof.to_csv(output_dir / "oof_conditional_latent_routing.csv", index=False)
    submission.to_csv(output_dir / "submission_conditional_latent_routing.csv", index=False)
    selected_df.to_csv(output_dir / "selected_moves.csv", index=False)
    pd.DataFrame(
        [
            {"name": "base", "avg_log_loss": base_score, **base_per},
            {"name": "conditional_latent_routing", "avg_log_loss": routed_score, **routed_per},
        ]
    ).to_csv(output_dir / "score.csv", index=False)
    report = {
        "base_score": {"avg_log_loss": base_score, "per_target": base_per},
        "routed_score": {"avg_log_loss": routed_score, "per_target": routed_per},
        "selected_moves": selected_df.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Conditional latent routing",
        "",
        f"- Base OOF: `{base_score:.6f}`",
        f"- Routed OOF: `{routed_score:.6f}`",
        "",
        "## Selected Moves",
        "",
        dataframe_to_markdown(selected_df),
        "",
        "## Scores",
        "",
        dataframe_to_markdown(pd.read_csv(output_dir / "score.csv")),
        "",
        "## Top Candidates",
        "",
        dataframe_to_markdown(candidates.head(20)),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"base={base_score:.6f} routed={routed_score:.6f}")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route target/bin slices to latent-derived sources when they beat the base OOF.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/targetwise_residual_latent_portfolio_v1/oof_targetwise_latent_portfolio_v1.csv")
    parser.add_argument("--base-submission", default="outputs/targetwise_residual_latent_portfolio_v1/submission_targetwise_latent_portfolio_v1.csv")
    parser.add_argument("--source", action="append", required=True, help="name=oof_path,submission_path")
    parser.add_argument("--output-dir", default="outputs/conditional_latent_routing_v1")
    parser.add_argument("--weights", default="0.25,0.5,0.75,1.0")
    parser.add_argument(
        "--bins",
        default="early:0:0.333,mid:0.333:0.666,late_mid:0.666:0.8,tail:0.8:1.000001,late:0.666:1.000001,all:0:1.000001",
    )
    parser.add_argument("--min-train-rows", type=int, default=20)
    parser.add_argument("--min-sample-rows", type=int, default=0)
    parser.add_argument("--min-improvement", type=float, default=0.0002)
    parser.add_argument("--max-moves-per-target", type=int, default=1)
    parser.add_argument("--allow-overlap", action="store_true")
    parser.add_argument("--targets", default=",".join(TARGET_COLUMNS), help="Comma-separated targets to route.")
    parser.add_argument("--match-source-prefix", action="store_true", help="Only allow sources named like '<target>_' for each target.")
    return parser.parse_args()


def main() -> None:
    build(parse_args())


if __name__ == "__main__":
    main()
