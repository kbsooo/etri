from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SLEEP_TARGETS = ["S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    value: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


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


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(args.base_oof))
    submission = normalize_keys(pd.read_csv(args.base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return prediction_matrix(oof), submission_matrix(submission)


def build_joined_frames(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    master = normalize_keys(pd.read_parquet(args.master_path))
    base_oof, base_test = load_base_predictions(args, train, sample)

    keep_master = [
        col
        for col in master.columns
        if col not in TARGET_COLUMNS + ["role"]
    ]
    train_x = train.merge(master[keep_master], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_x = sample[KEY_COLUMNS].merge(master[keep_master], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_x["date"].isna().any() or test_x["date"].isna().any():
        raise ValueError("Some rows failed to join with master features")

    train_x, test_x = add_engineered_sleep_features(train_x, test_x, base_oof, base_test)
    return train_x, test_x, base_oof, base_test


def add_engineered_sleep_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_oof: np.ndarray,
    base_test: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_df = pd.concat(
        [
            train_df.assign(_split="train", _row=np.arange(len(train_df))),
            test_df.assign(_split="test", _row=np.arange(len(test_df))),
        ],
        ignore_index=True,
    )
    lifelog_dt = pd.to_datetime(all_df["lifelog_date"])
    all_df["weekday"] = lifelog_dt.dt.weekday.astype(float)
    all_df["is_weekend"] = lifelog_dt.dt.weekday.isin([5, 6]).astype(float)
    all_df["weekday_sin"] = np.sin(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["weekday_cos"] = np.cos(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["day_ord"] = lifelog_dt.map(pd.Timestamp.toordinal).astype(float)
    all_df = all_df.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_df["sub_day_index"] = all_df.groupby("subject_id").cumcount().astype(float)
    denom = all_df.groupby("subject_id")["sub_day_index"].transform("max").replace(0.0, 1.0)
    all_df["sub_day_position"] = all_df["sub_day_index"] / denom
    all_df = all_df.sort_values(["_split", "_row"]).reset_index(drop=True)

    pred_all = np.vstack([base_oof, base_test])
    for target_i, target in enumerate(TARGET_COLUMNS):
        pred = np.clip(pred_all[:, target_i], EPS, 1.0 - EPS)
        all_df[f"base_pred_{target}"] = pred
        all_df[f"base_logit_{target}"] = np.log(pred / (1.0 - pred))

    rank_source = [
        "tst_min",
        "sleep_eff",
        "sol_proxy_min",
        "n_awakenings",
        "n_awakenings_long",
        "longest_block_min",
        "night_hr_mean",
        "night_rmssd",
        "night_sdnn",
        "night_pnn50",
        "mlight_night_mean",
        "mlight_night_max",
        "mlight_night_h_bright",
        "wlight_night_mean",
        "wlight_night_max",
        "wlight_night_h_bright",
        "prebed_video_sec",
        "prebed_sns_sec",
        "prebed_messenger_sec",
    ]
    grouped = all_df.groupby("subject_id", sort=False)
    new_cols = {}
    for col in rank_source:
        if col not in all_df.columns:
            continue
        values = pd.to_numeric(all_df[col], errors="coerce")
        new_cols[f"sleep_rank__{col}"] = grouped[col].rank(method="average", pct=True)
        new_cols[f"sleep_center__{col}"] = values - grouped[col].transform("mean")
    if new_cols:
        all_df = pd.concat([all_df, pd.DataFrame(new_cols, index=all_df.index)], axis=1)

    train_out = all_df[all_df["_split"].eq("train")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"].eq("test")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out


def sleep_feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    tokens = [
        "tst",
        "sleep",
        "sol",
        "awak",
        "longest",
        "night_hr",
        "night_rmssd",
        "night_sdnn",
        "night_pnn50",
        "mlight_night",
        "wlight_night",
        "prebed",
        "weekday",
        "is_weekend",
        "sub_day",
        "base_pred_",
        "base_logit_",
    ]
    blocked = set(KEY_COLUMNS + TARGET_COLUMNS + ["date", "sleep_onset", "wake_time"])
    numeric_cols = [
        col
        for col in df.columns
        if col not in blocked
        and any(token in col for token in tokens)
        and pd.api.types.is_numeric_dtype(df[col])
    ]
    return sorted(dict.fromkeys(numeric_cols)), ["subject_id"]


def make_model(spec: ModelSpec, numeric_cols: list[str], categorical_cols: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler()), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ]
    )
    if spec.kind == "logreg":
        model = LogisticRegression(C=spec.value, solver="lbfgs", max_iter=5000)
    elif spec.kind == "hgb":
        model = HistGradientBoostingClassifier(
            max_iter=80,
            learning_rate=0.03,
            l2_regularization=spec.value,
            max_leaf_nodes=7,
            random_state=2026,
        )
    else:
        raise ValueError(f"Unknown model kind: {spec.kind}")
    return make_pipeline(preprocessor, model)


def fit_predict(model: Pipeline, train_x: pd.DataFrame, y: np.ndarray, eval_x: pd.DataFrame) -> np.ndarray:
    classes = np.unique(y)
    if len(classes) < 2:
        return np.full(len(eval_x), float(classes[0]), dtype=float)
    model.fit(train_x, y)
    return model.predict_proba(eval_x)[:, 1]


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_x, test_x, base_oof, base_test = build_joined_frames(args)
    y = train_x[TARGET_COLUMNS]
    folds = make_subject_time_folds(train_x, args.folds)
    numeric_cols, categorical_cols = sleep_feature_columns(train_x)
    specs = [ModelSpec(f"logreg_C{value:g}", "logreg", value) for value in parse_float_list(args.logreg_cs)]
    specs.extend(ModelSpec(f"hgb_l2_{value:g}", "hgb", value) for value in parse_float_list(args.hgb_l2s))
    weights = parse_float_list(args.blend_weights)

    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    candidate_rows = []
    candidate_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    best_by_target: dict[str, dict] = {}

    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name}")
        model_oof = base_oof.copy()
        model_test = base_test.copy()
        for target in SLEEP_TARGETS:
            target_i = TARGET_COLUMNS.index(target)
            for train_idx, val_idx in folds:
                model = make_model(spec, numeric_cols, categorical_cols)
                model_oof[val_idx, target_i] = fit_predict(
                    model,
                    train_x.iloc[train_idx],
                    train_x.iloc[train_idx][target].astype(int).to_numpy(),
                    train_x.iloc[val_idx],
                )
            final_model = make_model(spec, numeric_cols, categorical_cols)
            model_test[:, target_i] = fit_predict(final_model, train_x, train_x[target].astype(int).to_numpy(), test_x)

        for weight in weights:
            name = f"{spec.name}_w{weight:g}"
            blended_oof = base_oof.copy()
            blended_test = base_test.copy()
            for target in SLEEP_TARGETS:
                target_i = TARGET_COLUMNS.index(target)
                blended_oof[:, target_i] = np.clip(
                    (1.0 - weight) * base_oof[:, target_i] + weight * model_oof[:, target_i],
                    EPS,
                    1.0 - EPS,
                )
                blended_test[:, target_i] = np.clip(
                    (1.0 - weight) * base_test[:, target_i] + weight * model_test[:, target_i],
                    EPS,
                    1.0 - EPS,
                )
            candidate_cache[name] = (blended_oof, blended_test)
            avg, per_target = average_loss(y, blended_oof)
            candidate_rows.append({"name": name, "spec": spec.name, "weight": weight, "avg_log_loss": avg, **per_target})
            for target in SLEEP_TARGETS:
                target_i = TARGET_COLUMNS.index(target)
                value = per_target[target]
                current = best_by_target.get(target)
                if current is None or value < current["log_loss"]:
                    folds_improved = 0
                    for fold_i, (_, val_idx) in enumerate(folds):
                        cand_fold = target_loss(y, blended_oof, target_i, val_idx)
                        folds_improved += int(cand_fold < base_fold_target[target][fold_i])
                    best_by_target[target] = {
                        "target": target,
                        "log_loss": value,
                        "base_log_loss": base_targets[target],
                        "delta_vs_base": base_targets[target] - value,
                        "candidate": name,
                        "spec": spec.name,
                        "weight": weight,
                        "folds_improved": folds_improved,
                    }

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        if target in best_by_target:
            selected = best_by_target[target]
            used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
            if used:
                final_oof[:, target_i] = candidate_cache[selected["candidate"]][0][:, target_i]
                final_test[:, target_i] = candidate_cache[selected["candidate"]][1][:, target_i]
            selection_rows.append({**selected, "used": bool(used)})
        else:
            selection_rows.append(
                {
                    "target": target,
                    "log_loss": base_targets[target],
                    "base_log_loss": base_targets[target],
                    "delta_vs_base": 0.0,
                    "candidate": "base",
                    "spec": "base",
                    "weight": 0.0,
                    "folds_improved": 0,
                    "used": False,
                }
            )

    scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selection_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_sleep_selection.csv", index=False)

    oof_df = train_x[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_sleep_metric_decoder.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_sleep_metric_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "feature_count": len(numeric_cols) + len(categorical_cols),
        "numeric_features": numeric_cols,
        "selection": selection_rows,
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "sleep_metric_decoder_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection[["target", "candidate", "log_loss", "base_log_loss", "delta_vs_base", "folds_improved", "used"]].to_string(index=False))
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sleep-metric focused decoder blended into a strong base candidate.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--base-oof", default="outputs/blend_guarded_graph_min3/oof_candidate_probability_blend.csv")
    parser.add_argument("--base-submission", default="outputs/blend_guarded_graph_min3/submission_candidate_probability_blend.csv")
    parser.add_argument("--output-dir", default="outputs/sleep_metric_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--logreg-cs", default="0.1,0.2,0.5,1.0")
    parser.add_argument("--hgb-l2s", default="1,2,5")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.15,0.2,0.3,0.4,0.5")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.0001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
