from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class Candidate:
    name: str
    oof_path: Path
    submission_path: Path


@dataclass(frozen=True)
class StackSpec:
    feature_set: str
    c_value: float

    @property
    def name(self) -> str:
        return f"stack_{self.feature_set}_C{self.c_value:g}"


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def logit(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, EPS, 1.0 - EPS)
    return np.log(clipped / (1.0 - clipped))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def default_candidates() -> list[Candidate]:
    return [
        Candidate(
            "latent_temporal",
            Path("outputs/latent_decoder/oof_targetwise_temporal_blend.csv"),
            Path("outputs/latent_decoder/submission_latent_decoder_targetwise_temporal.csv"),
        ),
        Candidate(
            "robust_safe",
            Path("outputs/robust_safe_ensemble/oof_robust_safe_ensemble.csv"),
            Path("outputs/robust_safe_ensemble/submission_robust_safe_ensemble.csv"),
        ),
        Candidate(
            "q_ranker",
            Path("outputs/q_ranker_decoder_tuned/oof_q_ranker_with_baseline_s.csv"),
            Path("outputs/q_ranker_decoder_tuned/submission_q_ranker_with_baseline_s.csv"),
        ),
        Candidate(
            "master_temporal",
            Path("outputs/master_aggressive_decoder_fast/oof_temporal_master_oof_blend.csv"),
            Path("outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv"),
        ),
        Candidate(
            "graph_original",
            Path("outputs/graph_diffusion_decoder/oof_graph_diffusion_decoder.csv"),
            Path("outputs/graph_diffusion_decoder/submission_graph_diffusion_decoder.csv"),
        ),
        Candidate(
            "graph_subjectless",
            Path("outputs/graph_diffusion_decoder_subjectless_long/oof_graph_diffusion_decoder.csv"),
            Path("outputs/graph_diffusion_decoder_subjectless_long/submission_graph_diffusion_decoder.csv"),
        ),
        Candidate(
            "graph_variant",
            Path("outputs/graph_diffusion_variant_ensemble/oof_graph_diffusion_variant_ensemble.csv"),
            Path("outputs/graph_diffusion_variant_ensemble/submission_graph_diffusion_variant_ensemble.csv"),
        ),
    ]


def load_candidates(args: argparse.Namespace) -> list[Candidate]:
    if not args.candidates:
        return default_candidates()
    out = []
    for item in args.candidates:
        parts = item.split(":")
        if len(parts) != 3:
            raise ValueError("--candidates entries must be name:oof_path:submission_path")
        out.append(Candidate(parts[0], Path(parts[1]), Path(parts[2])))
    return out


def load_prediction_bank(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray]:
    names = []
    oof_blocks = []
    sub_blocks = []
    for candidate in load_candidates(args):
        if not candidate.oof_path.exists() or not candidate.submission_path.exists():
            continue
        oof = normalize_keys(pd.read_csv(candidate.oof_path))
        submission = normalize_keys(pd.read_csv(candidate.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{candidate.name} OOF keys do not match train keys: {candidate.oof_path}")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{candidate.name} submission keys do not match sample keys: {candidate.submission_path}")
        names.append(candidate.name)
        oof_blocks.append(np.clip(prediction_matrix(oof), EPS, 1.0 - EPS))
        sub_blocks.append(np.clip(submission_matrix(submission), EPS, 1.0 - EPS))
    if not oof_blocks:
        raise RuntimeError("No prediction candidates were loaded")
    return names, np.stack(oof_blocks, axis=1), np.stack(sub_blocks, axis=1)


def panel_features(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
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
    dates = pd.to_datetime(all_rows["lifelog_date"])
    all_rows["weekday"] = dates.dt.weekday.astype(float)
    all_rows["weekday_sin"] = np.sin(2.0 * np.pi * all_rows["weekday"] / 7.0)
    all_rows["weekday_cos"] = np.cos(2.0 * np.pi * all_rows["weekday"] / 7.0)
    subject_dummies = pd.get_dummies(all_rows["subject_id"], prefix="subject", dtype=float)
    all_rows = pd.concat([all_rows, subject_dummies], axis=1)
    feature_cols = ["panel_index", "panel_position", "weekday_sin", "weekday_cos", *subject_dummies.columns.tolist()]
    restored = all_rows.sort_index()
    train_x = restored[restored["_split"].eq("train")].sort_values("_row")[feature_cols].to_numpy(dtype=float)
    test_x = restored[restored["_split"].eq("test")].sort_values("_row")[feature_cols].to_numpy(dtype=float)
    return train_x, test_x, feature_cols


def build_stack_features(
    pred_bank: np.ndarray,
    panel_x: np.ndarray,
    target_i: int,
    feature_set: str,
) -> np.ndarray:
    logits = logit(pred_bank)
    same_logits = logits[:, :, target_i]
    same_probs = pred_bank[:, :, target_i]
    same_stats = np.column_stack(
        [
            same_logits.mean(axis=1),
            same_logits.std(axis=1),
            same_logits.min(axis=1),
            same_logits.max(axis=1),
            same_probs.mean(axis=1),
            same_probs.std(axis=1),
        ]
    )
    if feature_set == "same_target":
        return np.column_stack([same_logits, same_stats])
    graph_context = logits[:, -1, :]
    if feature_set == "same_context":
        return np.column_stack([same_logits, same_stats, graph_context, panel_x])
    target_means = logits.mean(axis=1)
    target_stds = logits.std(axis=1)
    if feature_set == "all_targets":
        return np.column_stack([logits.reshape(len(logits), -1), target_means, target_stds, panel_x])
    raise ValueError(f"Unknown feature set: {feature_set}")


def fit_predict_logreg(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, c_value: float) -> np.ndarray:
    classes = np.unique(y_train)
    if len(classes) < 2:
        return np.full(len(x_eval), float(classes[0]), dtype=float)
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(imputer.fit_transform(x_train))
    x_eval_scaled = scaler.transform(imputer.transform(x_eval))
    model = LogisticRegression(C=c_value, solver="lbfgs", max_iter=5000)
    model.fit(x_train_scaled, y_train)
    return model.predict_proba(x_eval_scaled)[:, 1]


def stack_oof_and_test(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    pred_bank: np.ndarray,
    sub_bank: np.ndarray,
    panel_train: np.ndarray,
    panel_test: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    spec: StackSpec,
) -> tuple[np.ndarray, np.ndarray]:
    y = train[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        x_all = build_stack_features(pred_bank, panel_train, target_i, spec.feature_set)
        for train_idx, val_idx in folds:
            oof[val_idx, target_i] = fit_predict_logreg(
                x_all[train_idx],
                y.loc[train_idx, target].to_numpy(),
                x_all[val_idx],
                spec.c_value,
            )
        x_test = build_stack_features(sub_bank, panel_test, target_i, spec.feature_set)
        test[:, target_i] = fit_predict_logreg(
            x_all,
            y[target].to_numpy(),
            x_test,
            spec.c_value,
        )
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, i) for i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


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
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    candidate_names, pred_bank, sub_bank = load_prediction_bank(args, train, sample)
    panel_train, panel_test, panel_cols = panel_features(train, sample)
    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_name = args.base_candidate
    if base_name not in candidate_names:
        raise ValueError(f"Base candidate not loaded: {base_name}; loaded={candidate_names}")
    base_i = candidate_names.index(base_name)
    base_oof = pred_bank[:, base_i, :]
    base_test = sub_bank[:, base_i, :]
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    specs = [StackSpec(feature_set, c_value) for feature_set in parse_str_list(args.feature_sets) for c_value in parse_float_list(args.c_values)]
    blend_weights = parse_float_list(args.blend_weights)
    stack_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    candidate_rows = []
    best_by_target: dict[str, dict] = {}
    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name}")
        stack_oof, stack_test = stack_oof_and_test(train, sample, pred_bank, sub_bank, panel_train, panel_test, folds, spec)
        stack_cache[spec.name] = (stack_oof, stack_test)
        for weight in blend_weights:
            blended = np.clip(weight * stack_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
            avg, per_target = average_loss(y, blended)
            row = {
                "name": f"blend_w{weight:g}_{spec.name}",
                "stack_name": spec.name,
                "feature_set": spec.feature_set,
                "c_value": spec.c_value,
                "blend_weight": weight,
                "avg_log_loss": avg,
                **per_target,
            }
            candidate_rows.append(row)
            for target_i, target in enumerate(TARGET_COLUMNS):
                value = per_target[target]
                current = best_by_target.get(target)
                if current is None or value < current["log_loss"]:
                    fold_improvements = 0
                    for _, val_idx in folds:
                        base_fold = target_loss(y, base_oof, target_i, val_idx)
                        cand_fold = target_loss(y, blended, target_i, val_idx)
                        fold_improvements += int(base_fold > cand_fold)
                    best_by_target[target] = {
                        "target": target,
                        "log_loss": value,
                        "base_log_loss": base_targets[target],
                        "delta_vs_base": base_targets[target] - value,
                        "stack_name": spec.name,
                        "feature_set": spec.feature_set,
                        "c_value": spec.c_value,
                        "blend_weight": weight,
                        "folds_improved": fold_improvements,
                    }

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selected_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        stack_oof, stack_test = stack_cache[selected["stack_name"]]
        weight = float(selected["blend_weight"])
        used = selected["delta_vs_base"] > 0 and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = np.clip(weight * stack_oof[:, target_i] + (1.0 - weight) * base_oof[:, target_i], EPS, 1.0 - EPS)
            final_test[:, target_i] = np.clip(weight * stack_test[:, target_i] + (1.0 - weight) * base_test[:, target_i], EPS, 1.0 - EPS)
        selected_rows.append({**selected, "used": bool(used)})

    candidate_scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selected_rows)
    final_avg, final_targets = average_loss(y, final_oof)

    candidate_scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_stack_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_prediction_stack_decoder.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_prediction_stack_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_candidate": base_name,
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "candidate_names": candidate_names,
        "panel_features": panel_cols,
        "selection": selected_rows,
        "top_candidates": candidate_scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "prediction_stack_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Prediction stack decoder report",
        "",
        f"- Base candidate: `{base_name}`",
        f"- Base CV: {base_avg:.6f}",
        f"- Final CV: {final_avg:.6f}",
        f"- Loaded candidates: {', '.join(candidate_names)}",
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(candidate_scores.head(15)[["name", "avg_log_loss", *TARGET_COLUMNS]]),
        "",
    ]
    (output_dir / "prediction_stack_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Second-stage decoder over robust OOF prediction banks.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/prediction_stack_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--base-candidate", default="graph_variant")
    parser.add_argument("--feature-sets", default="same_target,same_context,all_targets")
    parser.add_argument("--c-values", default="0.01,0.03,0.1,0.3,1")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=3)
    parser.add_argument("--candidates", nargs="*", default=None, help="Optional name:oof_path:submission_path entries.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
