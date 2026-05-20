from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    oof_path: Path
    submission_path: Path


@dataclass(frozen=True)
class WindowSpec:
    name: str
    lo: float
    hi: float


@dataclass(frozen=True)
class MetaSpec:
    feature_set: str
    c_value: float

    @property
    def name(self) -> str:
        return f"{self.feature_set}_C{self.c_value:g}"


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_candidate(value: str) -> CandidateSpec:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError("--candidate entries must be name:oof_path:submission_path")
    return CandidateSpec(parts[0], Path(parts[1]), Path(parts[2]))


def parse_windows(value: str) -> list[WindowSpec]:
    windows: list[WindowSpec] = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        windows.append(WindowSpec(name=name, lo=float(lo), hi=float(hi)))
    if not windows:
        raise ValueError("At least one window is required")
    return windows


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred_cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(pred_cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing prediction columns: {missing}")
    return np.clip(oof[pred_cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    missing = sorted(set(TARGET_COLUMNS) - set(submission.columns))
    if missing:
        raise ValueError(f"Submission file missing target columns: {missing}")
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_prediction_bank(
    args: argparse.Namespace,
    train: pd.DataFrame,
    sample: pd.DataFrame,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    names: list[str] = []
    oof_blocks: list[np.ndarray] = []
    sub_blocks: list[np.ndarray] = []
    for spec_text in args.candidate:
        spec = parse_candidate(spec_text)
        if not spec.oof_path.exists():
            raise FileNotFoundError(spec.oof_path)
        if not spec.submission_path.exists():
            raise FileNotFoundError(spec.submission_path)
        oof = normalize_keys(pd.read_csv(spec.oof_path))
        submission = normalize_keys(pd.read_csv(spec.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} OOF keys do not match train keys: {spec.oof_path}")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} submission keys do not match sample keys: {spec.submission_path}")
        names.append(spec.name)
        oof_blocks.append(prediction_matrix(oof))
        sub_blocks.append(submission_matrix(submission))
    if args.baseline not in names:
        raise ValueError(f"Baseline candidate is not loaded: {args.baseline}; loaded={names}")
    return names, np.stack(oof_blocks, axis=1), np.stack(sub_blocks, axis=1)


def add_panel_features(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, list[str]]:
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
    feature_cols = [
        "panel_index",
        "panel_position",
        "weekday_sin",
        "weekday_cos",
        *subject_dummies.columns.tolist(),
    ]
    restored = all_rows.sort_index()
    train_panel = restored[restored["_split"].eq("train")].sort_values("_row").reset_index(drop=True)
    sample_panel = restored[restored["_split"].eq("test")].sort_values("_row").reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_panel[["panel_index", "panel_position"]]
    sample_out[["panel_index", "panel_position"]] = sample_panel[["panel_index", "panel_position"]]
    return (
        train_out,
        sample_out,
        train_panel[feature_cols].to_numpy(dtype=float),
        sample_panel[feature_cols].to_numpy(dtype=float),
        feature_cols,
    )


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    buckets: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            buckets[fold].extend(chunk.tolist())
    return [np.array(sorted(bucket), dtype=int) for bucket in buckets]


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


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


def build_features(
    pred_bank: np.ndarray,
    panel_x: np.ndarray,
    target_i: int,
    feature_set: str,
) -> np.ndarray:
    logits = safe_logit(pred_bank)
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
    target_means = logits.mean(axis=1)
    target_stds = logits.std(axis=1)
    if feature_set == "same_context":
        return np.column_stack([same_logits, same_stats, target_means, target_stds, panel_x])
    if feature_set == "all_targets":
        return np.column_stack([logits.reshape(len(logits), -1), target_means, target_stds, panel_x])
    raise ValueError(f"Unknown feature set: {feature_set}")


def target_row_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1.0 - y) * np.log1p(-pred))


def average_log_loss(y_arr: np.ndarray, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {}
    losses = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        loss = float(target_row_loss(y_arr[:, target_i], pred[:, target_i]).mean())
        per_target[target] = loss
        losses.append(loss)
    return float(np.mean(losses)), per_target


def window_mask(frame: pd.DataFrame, window: WindowSpec) -> np.ndarray:
    pos = frame["panel_position"].to_numpy(dtype=float)
    return (pos >= window.lo) & (pos < window.hi)


def build_window_meta_predictions(
    y_arr: np.ndarray,
    train_bank: np.ndarray,
    test_bank: np.ndarray,
    panel_train: np.ndarray,
    panel_test: np.ndarray,
    folds: list[np.ndarray],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    target_i: int,
    spec: MetaSpec,
    min_train_rows: int,
) -> tuple[np.ndarray, np.ndarray] | None:
    if len(train_idx) < min_train_rows:
        return None
    if len(np.unique(y_arr[train_idx, target_i])) < 2:
        return None
    x_all = build_features(train_bank, panel_train, target_i, spec.feature_set)
    x_test = build_features(test_bank, panel_test, target_i, spec.feature_set)
    oof = np.full(len(train_bank), np.nan, dtype=float)
    for val_fold in folds:
        val_idx = np.intersect1d(train_idx, val_fold, assume_unique=False)
        if len(val_idx) == 0:
            continue
        tr_idx = np.setdiff1d(train_idx, val_fold, assume_unique=False)
        if len(tr_idx) < min_train_rows:
            continue
        oof[val_idx] = fit_predict_logreg(x_all[tr_idx], y_arr[tr_idx, target_i], x_all[val_idx], spec.c_value)
    if np.isnan(oof[train_idx]).any():
        return None
    test_pred = np.array([], dtype=float)
    if len(test_idx) > 0:
        test_pred = fit_predict_logreg(x_all[train_idx], y_arr[train_idx, target_i], x_test[test_idx], spec.c_value)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test_pred, EPS, 1.0 - EPS)


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


def bootstrap_improvement(row_delta: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(row_delta), size=(n_bootstrap, len(row_delta)))
    values = row_delta[idx].mean(axis=1)
    return {
        "improvement_p025": float(np.quantile(values, 0.025)),
        "improvement_p500": float(np.quantile(values, 0.500)),
        "improvement_p975": float(np.quantile(values, 0.975)),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample, panel_train, panel_test, panel_cols = add_panel_features(train, sample)
    candidate_names, train_bank, test_bank = load_prediction_bank(args, train, sample)
    base_i = candidate_names.index(args.baseline)
    base_oof = train_bank[:, base_i, :].copy()
    base_test = test_bank[:, base_i, :].copy()
    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    folds = make_subject_time_folds(train, args.folds)
    windows = parse_windows(args.windows)
    specs = [MetaSpec(feature_set, c_value) for feature_set in parse_str_list(args.feature_sets) for c_value in parse_float_list(args.c_values)]
    blend_weights = parse_float_list(args.blend_weights)
    subject_groups = {str(subject): group.index.to_numpy(dtype=int) for subject, group in train.groupby("subject_id", sort=True)}

    base_avg, base_targets = average_log_loss(y_arr, base_oof)
    final_oof = base_oof.copy()
    final_test = base_test.copy()
    option_rows = []
    selected_rows = []

    for target_i, target in enumerate(TARGET_COLUMNS):
        base_loss = target_row_loss(y_arr[:, target_i], base_oof[:, target_i])
        for window in windows:
            idx = np.flatnonzero(window_mask(train, window))
            test_idx = np.flatnonzero(window_mask(sample, window))
            if args.require_sample_support and len(test_idx) == 0:
                selected_rows.append(
                    {
                        "target": target,
                        "window": window.name,
                        "used": False,
                        "reason": "no_sample_rows",
                        "n_train": len(idx),
                        "n_sample": len(test_idx),
                    }
                )
                continue
            best = None
            for spec in specs:
                built = build_window_meta_predictions(
                    y_arr,
                    train_bank,
                    test_bank,
                    panel_train,
                    panel_test,
                    folds,
                    idx,
                    test_idx,
                    target_i,
                    spec,
                    args.min_train_rows,
                )
                if built is None:
                    continue
                meta_oof, meta_test = built
                for weight in blend_weights:
                    if weight <= 0:
                        continue
                    candidate = base_oof[:, target_i].copy()
                    candidate[idx] = np.clip(
                        weight * meta_oof[idx] + (1.0 - weight) * base_oof[idx, target_i],
                        EPS,
                        1.0 - EPS,
                    )
                    row_delta = np.zeros(len(train), dtype=float)
                    row_delta[idx] = base_loss[idx] - target_row_loss(y_arr[idx, target_i], candidate[idx])
                    fold_deltas = []
                    for fold_idx in folds:
                        fold_window_idx = np.intersect1d(idx, fold_idx, assume_unique=False)
                        if len(fold_window_idx) > 0:
                            fold_deltas.append(float(row_delta[fold_window_idx].mean()))
                    subject_deltas = [
                        float(row_delta[np.intersect1d(idx, subject_idx, assume_unique=False)].mean())
                        for subject_idx in subject_groups.values()
                        if len(np.intersect1d(idx, subject_idx, assume_unique=False)) > 0
                    ]
                    window_delta = float(row_delta[idx].mean())
                    target_delta = float(row_delta.mean())
                    folds_improved = int(sum(delta > 0 for delta in fold_deltas))
                    worst_subject_delta = float(min(subject_deltas)) if subject_deltas else 0.0
                    worst_fold_delta = float(min(fold_deltas)) if fold_deltas else 0.0
                    stress_floor = min(worst_fold_delta, worst_subject_delta)
                    option_score = target_delta + args.stress_weight * min(0.0, stress_floor)
                    row = {
                        "target": target,
                        "window": window.name,
                        "n_train": len(idx),
                        "n_sample": len(test_idx),
                        "spec": spec.name,
                        "feature_set": spec.feature_set,
                        "c_value": spec.c_value,
                        "blend_weight": weight,
                        "window_delta": window_delta,
                        "target_delta": target_delta,
                        "folds_improved": folds_improved,
                        "worst_fold_delta": worst_fold_delta,
                        "worst_subject_delta": worst_subject_delta,
                        "option_score": option_score,
                    }
                    option_rows.append(row)
                    passes = (
                        window_delta >= args.min_window_delta
                        and folds_improved >= args.min_window_folds_improved
                        and worst_subject_delta >= -args.max_subject_window_regression
                        and worst_fold_delta >= -args.max_fold_window_regression
                    )
                    if not passes:
                        continue
                    if best is None or (option_score, target_delta, window_delta) > (
                        best["option_score"],
                        best["target_delta"],
                        best["window_delta"],
                    ):
                        best = {
                            **row,
                            "meta_oof": meta_oof,
                            "meta_test": meta_test,
                        }
            if best is None:
                selected_rows.append(
                    {
                        "target": target,
                        "window": window.name,
                        "used": False,
                        "reason": "no_passing_option",
                        "n_train": len(idx),
                        "n_sample": len(test_idx),
                    }
                )
                continue
            weight = float(best["blend_weight"])
            final_oof[idx, target_i] = np.clip(
                weight * best["meta_oof"][idx] + (1.0 - weight) * base_oof[idx, target_i],
                EPS,
                1.0 - EPS,
            )
            if len(test_idx) > 0:
                final_test[test_idx, target_i] = np.clip(
                    weight * best["meta_test"] + (1.0 - weight) * base_test[test_idx, target_i],
                    EPS,
                    1.0 - EPS,
                )
            selected_rows.append(
                {
                    "target": target,
                    "window": window.name,
                    "used": True,
                    "reason": "selected",
                    **{key: best[key] for key in best if key not in {"meta_oof", "meta_test"}},
                }
            )

    option_df = pd.DataFrame(option_rows)
    selection = pd.DataFrame(selected_rows)
    if not option_df.empty:
        option_df = option_df.sort_values(["option_score", "target_delta", "window_delta"], ascending=[False, False, False])
    option_df.to_csv(output_dir / "windowed_stack_options.csv", index=False)
    selection.to_csv(output_dir / "windowed_stack_selection.csv", index=False)

    final_avg, final_targets = average_log_loss(y_arr, final_oof)
    base_row_loss = np.column_stack(
        [target_row_loss(y_arr[:, i], base_oof[:, i]) for i in range(len(TARGET_COLUMNS))]
    ).mean(axis=1)
    final_row_loss = np.column_stack(
        [target_row_loss(y_arr[:, i], final_oof[:, i]) for i in range(len(TARGET_COLUMNS))]
    ).mean(axis=1)
    row_delta = base_row_loss - final_row_loss
    fold_deltas = [float(row_delta[fold_idx].mean()) for fold_idx in folds]
    subject_deltas = {subject: float(row_delta[idx].mean()) for subject, idx in subject_groups.items()}
    blocks = {
        "early": np.flatnonzero(train["panel_position"].to_numpy(dtype=float) < 1 / 3),
        "mid": np.flatnonzero((train["panel_position"].to_numpy(dtype=float) >= 1 / 3) & (train["panel_position"].to_numpy(dtype=float) < 2 / 3)),
        "late": np.flatnonzero(train["panel_position"].to_numpy(dtype=float) >= 2 / 3),
        "tail20": np.flatnonzero(train["panel_position"].to_numpy(dtype=float) >= 0.8),
    }
    block_deltas = {name: float(row_delta[idx].mean()) for name, idx in blocks.items() if len(idx) > 0}
    boot = bootstrap_improvement(row_delta, args.seed, args.bootstrap)

    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_windowed_prediction_stack_decoder.csv"
    oof.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_windowed_prediction_stack_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "baseline": args.baseline,
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "improvement": float(base_avg - final_avg),
        "fold_deltas": fold_deltas,
        "subject_deltas": subject_deltas,
        "block_deltas": block_deltas,
        "bootstrap": boot,
        "candidate_names": candidate_names,
        "panel_features": panel_cols,
        "args": vars(args),
    }
    (output_dir / "windowed_prediction_stack_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = [
        "# Windowed prediction stack decoder report",
        "",
        f"- Baseline: `{args.baseline}`",
        f"- Base CV: `{base_avg:.6f}`",
        f"- Final CV: `{final_avg:.6f}`",
        f"- Improvement: `{base_avg - final_avg:.6f}`",
        f"- Bootstrap p025: `{boot['improvement_p025']:.6f}`",
        f"- Require sample support: `{args.require_sample_support}`",
        "",
        "## Selected Windows",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top Options",
        "",
        dataframe_to_markdown(option_df.head(30)) if not option_df.empty else "_No options._",
        "",
    ]
    (output_dir / "windowed_prediction_stack_report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f} improvement={base_avg - final_avg:.6f} p025={boot['improvement_p025']:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe windowed meta decoder over OOF prediction banks.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument(
        "--windows",
        default="early:0:0.333333,mid:0.333333:0.666667,late_mid:0.666667:0.8,tail20:0.8:1.000001",
    )
    parser.add_argument("--feature-sets", default="same_target,same_context,all_targets")
    parser.add_argument("--c-values", default="0.003,0.01,0.03,0.1,0.3")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--min-train-rows", type=int, default=24)
    parser.add_argument("--min-window-delta", type=float, default=0.0005)
    parser.add_argument("--min-window-folds-improved", type=int, default=2)
    parser.add_argument("--max-subject-window-regression", type=float, default=0.025)
    parser.add_argument("--max-fold-window-regression", type=float, default=0.015)
    parser.add_argument("--stress-weight", type=float, default=0.20)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--require-sample-support", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
