from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class GraphSpec:
    bandwidth: float
    sigma: float
    label_shrink: float

    @property
    def name(self) -> str:
        return f"graph_bw{self.bandwidth:g}_sig{self.sigma:g}_sh{self.label_shrink:g}"


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def make_subject_time_folds(df: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = df.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(df))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def load_frames(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    master = normalize_keys(pd.read_parquet(args.master_path))
    latents = normalize_keys(pd.read_parquet(args.latent_path))
    latent_cols = [col for col in latents.columns if col.startswith("z_")]
    latent_features = latents[KEY_COLUMNS + latent_cols + ["day_index_subject"]]
    all_features = master.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
    numeric_cols = [
        col
        for col in all_features.columns
        if col not in KEY_COLUMNS + TARGET_COLUMNS + ["role", "date"]
        and pd.api.types.is_numeric_dtype(all_features[col])
    ]
    keep_tokens = [
        "hr",
        "sleep",
        "tst",
        "eff",
        "sol",
        "awak",
        "gps",
        "home",
        "light",
        "screen",
        "step",
        "outings",
        "prebed",
        "app_",
        "amb_",
        "coherence",
        "agree",
        "day_index",
    ]
    feature_cols = [
        col
        for col in numeric_cols
        if col.startswith("z_") or col.startswith("latent__") or any(token in col for token in keep_tokens)
    ]
    feature_cols = sorted(dict.fromkeys(feature_cols))
    train_joined = train.merge(all_features[KEY_COLUMNS + feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    test_joined = sample[KEY_COLUMNS].merge(all_features[KEY_COLUMNS + feature_cols], on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_joined[feature_cols].isna().all(axis=1).any() or test_joined[feature_cols].isna().all(axis=1).any():
        raise ValueError("Some rows failed to join graph features")
    train_joined["_date_ord"] = pd.to_datetime(train_joined["lifelog_date"]).map(pd.Timestamp.toordinal).astype(float)
    test_joined["_date_ord"] = pd.to_datetime(test_joined["lifelog_date"]).map(pd.Timestamp.toordinal).astype(float)
    return train_joined, test_joined, feature_cols


def feature_matrix(train_df: pd.DataFrame, test_df: pd.DataFrame, feature_cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    raw = pd.concat([train_df[feature_cols], test_df[feature_cols]], ignore_index=True)
    x = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(raw)
    x = StandardScaler().fit_transform(x)
    return x[: len(train_df)].astype(np.float32), x[len(train_df) :].astype(np.float32)


def subject_rates(train_part: pd.DataFrame, alpha: float) -> tuple[pd.DataFrame, np.ndarray]:
    global_rate = train_part[TARGET_COLUMNS].mean()
    subject_sum = train_part.groupby("subject_id")[TARGET_COLUMNS].sum()
    subject_count = train_part.groupby("subject_id")[TARGET_COLUMNS].count()
    rates = (subject_sum + alpha * global_rate) / (subject_count + alpha)
    return rates, global_rate.to_numpy(dtype=float)


def graph_predict_eval(
    train_part: pd.DataFrame,
    eval_part: pd.DataFrame,
    x_train_part: np.ndarray,
    x_eval: np.ndarray,
    spec: GraphSpec,
    alpha: float,
) -> np.ndarray:
    rates, global_rate = subject_rates(train_part, alpha)
    y = train_part[TARGET_COLUMNS].to_numpy(dtype=float)
    subject_train = train_part["subject_id"].to_numpy()
    train_ord = train_part["_date_ord"].to_numpy(dtype=float)
    eval_ord = eval_part["_date_ord"].to_numpy(dtype=float)
    pred = np.zeros((len(eval_part), len(TARGET_COLUMNS)), dtype=float)
    for row_i, row in enumerate(eval_part.itertuples(index=False)):
        subject = getattr(row, "subject_id")
        ids = np.where(subject_train == subject)[0]
        base = rates.loc[subject].to_numpy(dtype=float) if subject in rates.index else global_rate
        if len(ids) == 0:
            pred[row_i] = base
            continue
        time_dist = np.abs(train_ord[ids] - eval_ord[row_i])
        feature_dist = np.linalg.norm(x_train_part[ids] - x_eval[row_i], axis=1)
        weights = np.exp(-time_dist / spec.bandwidth) * np.exp(-(feature_dist**2) / (2.0 * spec.sigma * spec.sigma))
        if weights.sum() <= 1e-12:
            pred[row_i] = base
            continue
        label_estimate = (weights[:, None] * y[ids]).sum(axis=0) / weights.sum()
        pred[row_i] = (1.0 - spec.label_shrink) * label_estimate + spec.label_shrink * base
    return np.clip(pred, EPS, 1.0 - EPS)


def graph_oof_and_test(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    x_train: np.ndarray,
    x_test: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    spec: GraphSpec,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    oof = np.zeros((len(train_df), len(TARGET_COLUMNS)), dtype=float)
    for train_idx, val_idx in folds:
        oof[val_idx] = graph_predict_eval(
            train_part=train_df.iloc[train_idx].reset_index(drop=True),
            eval_part=train_df.iloc[val_idx].reset_index(drop=True),
            x_train_part=x_train[train_idx],
            x_eval=x_train[val_idx],
            spec=spec,
            alpha=alpha,
        )
    test_pred = graph_predict_eval(train_df.reset_index(drop=True), test_df.reset_index(drop=True), x_train, x_test, spec, alpha)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test_pred, EPS, 1.0 - EPS)


def load_base_predictions(args: argparse.Namespace, train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    base_submission = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof[KEY_COLUMNS].equals(train_df[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_submission[KEY_COLUMNS].equals(test_df[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    base_train = np.column_stack([base_oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    base_test = base_submission[TARGET_COLUMNS].to_numpy(dtype=float)
    return np.clip(base_train, EPS, 1.0 - EPS), np.clip(base_test, EPS, 1.0 - EPS)


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
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_df, test_df, feature_cols = load_frames(args)
    x_train, x_test = feature_matrix(train_df, test_df, feature_cols)
    folds = make_subject_time_folds(train_df, args.folds)
    base_oof, base_test = load_base_predictions(args, train_df, test_df)
    y = train_df[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)

    specs = [
        GraphSpec(bandwidth=bw, sigma=sigma, label_shrink=shrink)
        for bw in parse_float_list(args.bandwidths)
        for sigma in parse_float_list(args.sigmas)
        for shrink in parse_float_list(args.label_shrinks)
    ]
    blend_weights = parse_float_list(args.blend_weights)
    candidate_rows = []
    graph_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    best_by_target: dict[str, dict] = {}

    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name}")
        graph_oof, graph_test = graph_oof_and_test(train_df, test_df, x_train, x_test, folds, spec, args.alpha)
        graph_cache[spec.name] = (graph_oof, graph_test)
        for weight in blend_weights:
            candidate = np.clip(weight * graph_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
            avg, per_target = average_loss(y, candidate)
            row = {
                "name": f"blend_w{weight:g}_{spec.name}",
                "graph_name": spec.name,
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
                        cand_fold = target_loss(y, candidate, target_i, val_idx)
                        fold_improvements += int(base_fold > cand_fold)
                    best_by_target[target] = {
                        "target": target,
                        "log_loss": value,
                        "base_log_loss": base_targets[target],
                        "delta_vs_base": base_targets[target] - value,
                        "graph_name": spec.name,
                        "blend_weight": weight,
                        "folds_improved": fold_improvements,
                    }

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selected_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        graph_oof, graph_test = graph_cache[selected["graph_name"]]
        weight = float(selected["blend_weight"])
        use_candidate = selected["delta_vs_base"] > 0 and selected["folds_improved"] >= args.min_target_folds_improved
        if use_candidate:
            final_oof[:, target_i] = np.clip(weight * graph_oof[:, target_i] + (1.0 - weight) * base_oof[:, target_i], EPS, 1.0 - EPS)
            final_test[:, target_i] = np.clip(weight * graph_test[:, target_i] + (1.0 - weight) * base_test[:, target_i], EPS, 1.0 - EPS)
        selected_rows.append({**selected, "used": bool(use_candidate)})

    candidate_scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selected_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    candidate_scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_graph_selection.csv", index=False)

    oof_df = train_df[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_df.to_csv(output_dir / "oof_graph_diffusion_decoder.csv", index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission.to_csv(output_dir / "submission_graph_diffusion_decoder.csv", index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "feature_count": len(feature_cols),
        "selection": selected_rows,
        "top_candidates": candidate_scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "graph_diffusion_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Graph diffusion decoder report",
        "",
        f"- Base CV: {base_avg:.6f}",
        f"- Final CV: {final_avg:.6f}",
        f"- Feature count: {len(feature_cols)}",
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
    (output_dir / "graph_diffusion_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(f"saved report: {output_dir / 'graph_diffusion_report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diffusion-latent graph label propagation decoder.")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder/day_latents.parquet")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/robust_safe_ensemble/oof_robust_safe_ensemble.csv")
    parser.add_argument("--base-submission", default="outputs/robust_safe_ensemble/submission_robust_safe_ensemble.csv")
    parser.add_argument("--output-dir", default="outputs/graph_diffusion_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=10.0)
    parser.add_argument("--bandwidths", default="1,2,3,5,7,10,14")
    parser.add_argument("--sigmas", default="1.5,2.5,4,7,99")
    parser.add_argument("--label-shrinks", default="0,0.25,0.5,0.75")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=3)
    return parser.parse_args()


if __name__ == "__main__":
    main()
