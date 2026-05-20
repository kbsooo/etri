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
class CalendarSpec:
    c_value: float

    @property
    def name(self) -> str:
        return f"calendar_label_C{self.c_value:g}"


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def add_date_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    date = pd.to_datetime(out["lifelog_date"])
    out["_date_ord"] = date.map(pd.Timestamp.toordinal).astype(float)
    out["_dow"] = date.dt.dayofweek.astype(int)
    out["_dow_sin"] = np.sin(2.0 * np.pi * out["_dow"] / 7.0)
    out["_dow_cos"] = np.cos(2.0 * np.pi * out["_dow"] / 7.0)
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
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    out = all_rows.sort_index()
    train_panel = out[out["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    test_panel = out[out["_split"].eq("test")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    test_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_panel
    test_out[["panel_index", "panel_position"]] = test_panel
    return train_out, test_out


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


def smoothed_rate(labels: np.ndarray, global_rate: float, alpha: float) -> float:
    if len(labels) == 0:
        return global_rate
    return float((labels.sum() + alpha * global_rate) / (len(labels) + alpha))


def temporal_subject_features(
    source: pd.DataFrame,
    eval_frame: pd.DataFrame,
    target: str,
    bandwidths: list[float],
    alpha: float,
    exclude_self: bool,
) -> np.ndarray:
    global_rate = float(source[target].mean())
    grouped = {
        str(subject): group.sort_values("_date_ord").reset_index(drop=True)
        for subject, group in source.groupby("subject_id", sort=False)
    }
    rows = []
    for _, row in eval_frame.iterrows():
        subject = str(row["subject_id"])
        date_ord = float(row["_date_ord"])
        group = grouped.get(subject)
        if group is None or group.empty:
            rows.append([global_rate, global_rate, 0.0, 99.0, 0.0, 99.0, 0.0, 99.0, *([global_rate, 0.0] * len(bandwidths))])
            continue
        dates = group["_date_ord"].to_numpy(dtype=float)
        labels = group[target].to_numpy(dtype=float)
        mask = np.ones(len(group), dtype=bool)
        if exclude_self:
            same_key = (
                group["subject_id"].astype(str).eq(subject).to_numpy()
                & group["sleep_date"].astype(str).eq(str(row["sleep_date"])).to_numpy()
                & group["lifelog_date"].astype(str).eq(str(row["lifelog_date"])).to_numpy()
            )
            mask &= ~same_key
        dates = dates[mask]
        labels = labels[mask]
        if len(labels) == 0:
            rows.append([global_rate, global_rate, 0.0, 99.0, 0.0, 99.0, 0.0, 99.0, *([global_rate, 0.0] * len(bandwidths))])
            continue
        subject_rate = smoothed_rate(labels, global_rate, alpha)
        signed = dates - date_ord
        abs_dist = np.abs(signed)
        prev_mask = signed < 0
        next_mask = signed > 0
        if prev_mask.any():
            prev_pos = np.where(prev_mask)[0][np.argmin(abs_dist[prev_mask])]
            prev_label = float(labels[prev_pos])
            prev_gap = float(abs_dist[prev_pos])
        else:
            prev_label = subject_rate
            prev_gap = 99.0
        if next_mask.any():
            next_pos = np.where(next_mask)[0][np.argmin(abs_dist[next_mask])]
            next_label = float(labels[next_pos])
            next_gap = float(abs_dist[next_pos])
        else:
            next_label = subject_rate
            next_gap = 99.0
        nearest_pos = int(np.argmin(abs_dist))
        nearest_label = float(labels[nearest_pos])
        nearest_gap = float(abs_dist[nearest_pos])
        feats = [
            global_rate,
            subject_rate,
            prev_label,
            min(prev_gap, 99.0),
            next_label,
            min(next_gap, 99.0),
            nearest_label,
            min(nearest_gap, 99.0),
        ]
        for bandwidth in bandwidths:
            weights = np.exp(-abs_dist / bandwidth)
            weight_sum = float(weights.sum())
            feats.extend([subject_rate if weight_sum <= 1e-12 else float((weights * labels).sum() / weight_sum), weight_sum])
        rows.append(feats)
    return np.asarray(rows, dtype=float)


def calendar_label_features(
    source: pd.DataFrame,
    eval_frame: pd.DataFrame,
    target: str,
    bandwidths: list[float],
    alpha: float,
    exclude_self: bool,
) -> np.ndarray:
    global_rate = float(source[target].mean())
    source_dates = source["_date_ord"].to_numpy(dtype=float)
    source_subjects = source["subject_id"].astype(str).to_numpy()
    source_dow = source["_dow"].to_numpy(dtype=int)
    labels = source[target].to_numpy(dtype=float)
    rows = []
    for _, row in eval_frame.iterrows():
        subject = str(row["subject_id"])
        date_ord = float(row["_date_ord"])
        dow = int(row["_dow"])
        mask = np.ones(len(source), dtype=bool)
        if exclude_self:
            same_key = (
                source["subject_id"].astype(str).eq(subject).to_numpy()
                & source["sleep_date"].astype(str).eq(str(row["sleep_date"])).to_numpy()
                & source["lifelog_date"].astype(str).eq(str(row["lifelog_date"])).to_numpy()
            )
            mask &= ~same_key
        date_delta = np.abs(source_dates - date_ord)
        other_subject = source_subjects != subject
        exact = mask & (date_delta <= 0.1)
        exact_other = exact & other_subject
        dow_mask = mask & (source_dow == dow)
        dow_other = dow_mask & other_subject
        feats = [
            global_rate,
            smoothed_rate(labels[exact], global_rate, alpha),
            float(exact.sum()),
            smoothed_rate(labels[exact_other], global_rate, alpha),
            float(exact_other.sum()),
            smoothed_rate(labels[dow_mask], global_rate, alpha),
            float(dow_mask.sum()),
            smoothed_rate(labels[dow_other], global_rate, alpha),
            float(dow_other.sum()),
        ]
        for bandwidth in bandwidths:
            weights = np.exp(-date_delta / bandwidth) * mask.astype(float)
            other_weights = weights * other_subject.astype(float)
            weight_sum = float(weights.sum())
            other_weight_sum = float(other_weights.sum())
            feats.extend(
                [
                    global_rate if weight_sum <= 1e-12 else float((weights * labels).sum() / weight_sum),
                    weight_sum,
                    global_rate if other_weight_sum <= 1e-12 else float((other_weights * labels).sum() / other_weight_sum),
                    other_weight_sum,
                ]
            )
        rows.append(feats)
    return np.asarray(rows, dtype=float)


def fit_predict(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, c_value: float) -> np.ndarray:
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


def make_feature_matrix(
    source: pd.DataFrame,
    eval_frame: pd.DataFrame,
    target: str,
    target_i: int,
    base_values: np.ndarray,
    bandwidths: list[float],
    alpha: float,
    exclude_self: bool,
) -> np.ndarray:
    subject_feats = temporal_subject_features(source, eval_frame, target, bandwidths, alpha, exclude_self)
    calendar_feats = calendar_label_features(source, eval_frame, target, bandwidths, alpha, exclude_self)
    static_feats = eval_frame[["panel_index", "panel_position", "_dow_sin", "_dow_cos"]].to_numpy(dtype=float)
    return np.column_stack([subject_feats, calendar_feats, base_values[:, target_i], safe_logit(base_values[:, target_i]), static_feats])


def calendar_oof_and_test(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_oof: np.ndarray,
    base_test: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    bandwidths: list[float],
    spec: CalendarSpec,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            source = train.iloc[train_idx].reset_index(drop=True)
            fit_frame = train.iloc[train_idx].reset_index(drop=True)
            val_frame = train.iloc[val_idx].reset_index(drop=True)
            x_fit = make_feature_matrix(source, fit_frame, target, target_i, base_oof[train_idx], bandwidths, alpha, exclude_self=True)
            x_val = make_feature_matrix(source, val_frame, target, target_i, base_oof[val_idx], bandwidths, alpha, exclude_self=False)
            oof[val_idx, target_i] = fit_predict(x_fit, fit_frame[target].astype(int).to_numpy(), x_val, spec.c_value)
        x_full = make_feature_matrix(train, train, target, target_i, base_oof, bandwidths, alpha, exclude_self=True)
        x_sample = make_feature_matrix(train, sample, target, target_i, base_test, bandwidths, alpha, exclude_self=False)
        test[:, target_i] = fit_predict(x_full, train[target].astype(int).to_numpy(), x_sample, spec.c_value)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda v: "" if pd.isna(v) else f"{v:.6f}")
        else:
            display[col] = display[col].map(lambda v: "" if pd.isna(v) else str(v))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *body])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = add_date_features(normalize_keys(pd.read_csv(args.train_path)))
    sample = add_date_features(normalize_keys(pd.read_csv(args.sample_path)))
    train, sample = add_panel_position(train, sample)
    base_oof, base_test = load_base_predictions(args, train, sample)
    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    bandwidths = parse_float_list(args.bandwidths)
    specs = [CalendarSpec(c_value) for c_value in parse_float_list(args.c_values)]
    blend_weights = parse_float_list(args.blend_weights)
    decoder_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    candidate_rows = []
    best_by_target: dict[str, dict] = {}

    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name}")
        decoder_oof, decoder_test = calendar_oof_and_test(train, sample, base_oof, base_test, folds, bandwidths, spec, args.alpha)
        decoder_cache[spec.name] = (decoder_oof, decoder_test)
        for weight in blend_weights:
            blended = np.clip(weight * decoder_oof + (1.0 - weight) * base_oof, EPS, 1.0 - EPS)
            avg, per_target = average_loss(y, blended)
            row = {
                "name": f"blend_w{weight:g}_{spec.name}",
                "decoder_name": spec.name,
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
                    folds_improved = 0
                    for fold_i, (_, val_idx) in enumerate(folds):
                        cand_fold = target_loss(y, blended, target_i, val_idx)
                        folds_improved += int(cand_fold < base_fold_target[target][fold_i])
                    best_by_target[target] = {
                        "target": target,
                        "log_loss": value,
                        "base_log_loss": base_targets[target],
                        "delta_vs_base": base_targets[target] - value,
                        "decoder_name": spec.name,
                        "c_value": spec.c_value,
                        "blend_weight": weight,
                        "folds_improved": folds_improved,
                    }

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        decoder_oof, decoder_test = decoder_cache[selected["decoder_name"]]
        weight = float(selected["blend_weight"])
        used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = np.clip(weight * decoder_oof[:, target_i] + (1.0 - weight) * base_oof[:, target_i], EPS, 1.0 - EPS)
            final_test[:, target_i] = np.clip(weight * decoder_test[:, target_i] + (1.0 - weight) * base_test[:, target_i], EPS, 1.0 - EPS)
        selection_rows.append({**selected, "used": bool(used)})

    candidate_scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selection_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    candidate_scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_calendar_label_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_calendar_label_decoder.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_calendar_label_decoder.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_candidates": candidate_scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "calendar_label_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Calendar Label Decoder Report",
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
        dataframe_to_markdown(candidate_scores.head(12)),
        "",
    ]
    (output_dir / "calendar_label_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe calendar/cross-subject label decoder blended into a base prediction.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/calendar_label_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--alpha", type=float, default=10.0)
    parser.add_argument("--bandwidths", default="1,2,3,5,7,14")
    parser.add_argument("--c-values", default="0.01,0.03,0.1,0.3,1,3,10")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.00005)
    return parser.parse_args()


if __name__ == "__main__":
    main()
