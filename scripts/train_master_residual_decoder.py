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
EPS = 1e-5


CORE_COLUMNS = [
    "mlight_night_h_bright",
    "mlight_night_max",
    "mlight_mean",
    "mlight_max",
    "longest_block_min",
    "tst_min",
    "sleep_eff",
    "sol_proxy_min",
    "n_awakenings",
    "n_awakenings_long",
    "night_hr_mean",
    "night_rmssd",
    "night_sdnn",
    "gps_home_ratio",
    "gps_elsewhere_ratio",
    "wifi_novelty_ratio",
    "wifi_core_hit",
    "ble_novelty_ratio",
    "ble_core_hit",
    "outings",
    "mob_stationary_min",
    "mob_vehicle_min",
    "mob_walk_min",
    "agree_rate",
    "only_act_rate",
    "only_ped_rate",
    "amb_night_silence",
    "amb_vehicle",
    "amb_music",
    "amb_speech",
    "prebed_sns_sec",
    "prebed_video_sec",
    "prebed_messenger_sec",
    "z_abs_mean",
    "z_abs_night",
    "z_abs_lateNight",
    "z_night_hr_mean",
    "z_lateNight_hr_mean",
    "z_night_step_sum",
    "z_night_gps_speed_mean",
    "z_earlyAM_step_sum",
]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    feature_set: str
    value: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


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


def load_joined(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    master = normalize_keys(pd.read_parquet(args.master_path))
    keep = [col for col in master.columns if col not in TARGET_COLUMNS + ["role"]]
    train_x = train.merge(master[keep], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_x = sample[KEY_COLUMNS].merge(master[keep], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_x["date"].isna().any() or test_x["date"].isna().any():
        raise ValueError("Some rows failed to join with master features")

    latent_path = Path(args.latent_path)
    if latent_path.exists():
        latents = normalize_keys(pd.read_parquet(latent_path))
        latent_cols = [col for col in latents.columns if col.startswith("z_")]
        renamed = {col: f"latent__{col}" for col in latent_cols}
        latent_features = latents[KEY_COLUMNS + latent_cols].rename(columns=renamed)
        train_x = train_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_x = test_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")

    base_oof, base_test = load_base_predictions(args, train, sample)
    train_x, test_x = add_engineered_features(train_x, test_x, base_oof, base_test)
    return train_x, test_x, base_oof, base_test


def add_engineered_features(
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
    date = pd.to_datetime(all_df["lifelog_date"])
    all_df["weekday"] = date.dt.weekday.astype(float)
    all_df["is_weekend"] = date.dt.weekday.isin([5, 6]).astype(float)
    all_df["weekday_sin"] = np.sin(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["weekday_cos"] = np.cos(2.0 * np.pi * all_df["weekday"] / 7.0)
    all_df["date_ord"] = date.map(pd.Timestamp.toordinal).astype(float)
    all_df = all_df.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_df["panel_index"] = all_df.groupby("subject_id").cumcount().astype(float)
    denom = all_df.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    all_df["panel_position"] = all_df["panel_index"] / denom
    all_df = all_df.sort_values(["_split", "_row"]).reset_index(drop=True)

    pred_all = np.vstack([base_oof, base_test])
    for target_i, target in enumerate(TARGET_COLUMNS):
        pred = np.clip(pred_all[:, target_i], EPS, 1.0 - EPS)
        all_df[f"base_pred_{target}"] = pred
        all_df[f"base_logit_{target}"] = safe_logit(pred)

    numeric_source = [
        col
        for col in all_df.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["date", "_split", "_row"]
        and pd.api.types.is_numeric_dtype(all_df[col])
    ]
    numeric_source = sorted(dict.fromkeys(numeric_source))
    grouped = all_df.groupby("subject_id", sort=False)
    new_cols: dict[str, pd.Series] = {}
    for col in numeric_source:
        values = pd.to_numeric(all_df[col], errors="coerce")
        miss_rate = float(values.isna().mean())
        if 0.0 < miss_rate < 1.0:
            new_cols[f"miss__{col}"] = values.isna().astype(float)
        finite = values[np.isfinite(values)]
        if len(finite) and finite.min() >= 0 and finite.quantile(0.95) > 10:
            new_cols[f"log1p__{col}"] = np.log1p(values)
        if not col.startswith("base_") and col not in {"weekday", "is_weekend", "date_ord", "panel_index", "panel_position"}:
            new_cols[f"sub_center__{col}"] = values - grouped[col].transform("mean")
            new_cols[f"sub_rank__{col}"] = grouped[col].rank(method="average", pct=True)
    if new_cols:
        all_df = pd.concat([all_df, pd.DataFrame(new_cols, index=all_df.index)], axis=1)

    train_out = all_df[all_df["_split"].eq("train")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    test_out = all_df[all_df["_split"].eq("test")].sort_values("_row").drop(columns=["_split", "_row"]).reset_index(drop=True)
    return train_out, test_out


def feature_sets(frame: pd.DataFrame) -> dict[str, tuple[list[str], list[str]]]:
    blocked = set(KEY_COLUMNS + TARGET_COLUMNS + ["date", "sleep_onset", "wake_time"])
    numeric_cols = [
        col
        for col in frame.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(frame[col])
    ]
    base_cols = [col for col in numeric_cols if col.startswith("base_")]
    time_cols = ["weekday", "is_weekend", "weekday_sin", "weekday_cos", "date_ord", "panel_index", "panel_position"]
    time_cols = [col for col in time_cols if col in frame.columns]
    core_cols = []
    for col in CORE_COLUMNS:
        core_cols.extend([col, f"miss__{col}", f"log1p__{col}", f"sub_center__{col}", f"sub_rank__{col}"])
    core_cols = [col for col in dict.fromkeys(core_cols) if col in frame.columns]
    rankdev_cols = [col for col in numeric_cols if col.startswith(("sub_center__", "sub_rank__", "miss__", "log1p__"))]
    latent_cols = [col for col in numeric_cols if col.startswith("latent__")]
    all_numeric = sorted(dict.fromkeys(numeric_cols))
    sets = {
        "base_only": (sorted(dict.fromkeys(base_cols + time_cols)), ["subject_id"]),
        "core": (sorted(dict.fromkeys(base_cols + core_cols + time_cols)), ["subject_id"]),
        "rankdev": (sorted(dict.fromkeys(base_cols + rankdev_cols + time_cols)), ["subject_id"]),
        "all": (all_numeric, ["subject_id"]),
        "nosubject_rankdev": (sorted(dict.fromkeys(base_cols + rankdev_cols + time_cols)), []),
    }
    if latent_cols:
        sets["latent_core"] = (sorted(dict.fromkeys(base_cols + latent_cols + core_cols + time_cols)), ["subject_id"])
    return sets


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
            learning_rate=0.025,
            max_leaf_nodes=7,
            min_samples_leaf=20,
            l2_regularization=spec.value,
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
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def train_model_oof_test(
    train_x: pd.DataFrame,
    test_x: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    spec: ModelSpec,
    sets: dict[str, tuple[list[str], list[str]]],
) -> tuple[np.ndarray, np.ndarray]:
    numeric_cols, categorical_cols = sets[spec.feature_set]
    oof = np.zeros((len(train_x), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(test_x), len(TARGET_COLUMNS)), dtype=float)
    y = train_x[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            model = make_model(spec, numeric_cols, categorical_cols)
            oof[val_idx, target_i] = fit_predict(
                model,
                train_x.iloc[train_idx],
                y.loc[train_idx, target].to_numpy(),
                train_x.iloc[val_idx],
            )
        full_model = make_model(spec, numeric_cols, categorical_cols)
        test[:, target_i] = fit_predict(full_model, train_x, y[target].to_numpy(), test_x)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
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
    train_x, test_x, base_oof, base_test = load_joined(args)
    folds = make_subject_time_folds(train_x, args.folds)
    sets = feature_sets(train_x)
    selected_sets = [name for name in parse_str_list(args.feature_sets) if name in sets]
    specs = [ModelSpec(f"logreg_{feature_set}_C{c:g}", "logreg", feature_set, c) for feature_set in selected_sets for c in parse_float_list(args.logreg_cs)]
    specs.extend(ModelSpec(f"hgb_{feature_set}_l2{v:g}", "hgb", feature_set, v) for feature_set in selected_sets for v in parse_float_list(args.hgb_l2s))
    weights = parse_float_list(args.blend_weights)
    y = train_x[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    candidate_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    rows = []
    best_by_target: dict[str, dict] = {}
    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name} ({len(sets[spec.feature_set][0])} numeric)")
        model_oof, model_test = train_model_oof_test(train_x, test_x, folds, spec, sets)
        for weight in weights:
            name = f"blend_w{weight:g}_{spec.name}"
            blended_oof = np.clip(weight * model_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
            blended_test = np.clip(weight * model_test + (1.0 - weight) * base_test, EPS, 1.0 - EPS)
            candidate_cache[name] = (blended_oof, blended_test)
            avg, per_target = average_loss(y, blended_oof)
            rows.append({"name": name, "spec": spec.name, "kind": spec.kind, "feature_set": spec.feature_set, "value": spec.value, "blend_weight": weight, "avg_log_loss": avg, **per_target})
            for target_i, target in enumerate(TARGET_COLUMNS):
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
                        "kind": spec.kind,
                        "feature_set": spec.feature_set,
                        "value": spec.value,
                        "blend_weight": weight,
                        "folds_improved": folds_improved,
                    }

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = candidate_cache[selected["candidate"]][0][:, target_i]
            final_test[:, target_i] = candidate_cache[selected["candidate"]][1][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    scores = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selection_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_master_residual_selection.csv", index=False)

    oof_df = train_x[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_master_residual_decoder.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_master_residual_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "feature_set_sizes": {name: len(cols) for name, (cols, _) in sets.items()},
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "master_residual_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Master Residual Decoder Report",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Final avg logloss: `{final_avg:.6f}`",
        f"- Target promotion rule: delta >= `{args.min_delta:g}` and improved folds >= `{args.min_target_folds_improved}/{args.folds}`",
        "",
        "## Selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top Candidates",
        "",
        dataframe_to_markdown(scores.head(12)),
        "",
    ]
    (output_dir / "master_residual_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Residual decoder over master lifelog features plus base prediction logits.")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/master_residual_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--feature-sets", default="base_only,core,rankdev,latent_core")
    parser.add_argument("--logreg-cs", default="0.003,0.01,0.03,0.1,0.3,1")
    parser.add_argument("--hgb-l2s", default="5,15,50")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.00005)
    return parser.parse_args()


if __name__ == "__main__":
    main()
