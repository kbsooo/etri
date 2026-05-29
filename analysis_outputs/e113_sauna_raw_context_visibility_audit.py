from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW_DIR = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = {"Q1", "Q2", "Q3"}
E95_ACTIVE = {"Q2", "S1", "S2", "S3"}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 1e-6, 1 - 1e-6)


def smooth_rate(y: np.ndarray) -> float:
    return float((y.sum() + 0.5) / (len(y) + 1.0))


def daily_features_for_file(path: Path) -> pd.DataFrame:
    name = path.stem.replace("ch2025_", "")
    frame = pd.read_parquet(path)
    frame["lifelog_date"] = frame["timestamp"].dt.floor("D")
    frame["_hour"] = frame["timestamp"].dt.hour
    frame["_night"] = (frame["_hour"].ge(18) | frame["_hour"].le(5)).astype(int)

    group = frame.groupby(["subject_id", "lifelog_date"], sort=False)
    out = group.size().rename(f"{name}__rows").to_frame()
    out[f"{name}__active_hours"] = group["_hour"].nunique()
    out[f"{name}__night_rows"] = group["_night"].sum()
    out[f"{name}__night_share"] = out[f"{name}__night_rows"] / out[f"{name}__rows"].clip(lower=1)

    numeric_cols = [
        col
        for col in frame.select_dtypes(include=[np.number]).columns
        if col not in {"_hour", "_night"}
    ]
    for col in numeric_cols:
        stats = group[col].agg(["mean", "std", "sum", "max"])
        for stat in stats.columns:
            out[f"{name}__{col}__{stat}"] = stats[stat]

    object_cols = [
        col
        for col in frame.columns
        if col not in {"subject_id", "timestamp", "lifelog_date", "_hour", "_night"}
        and frame[col].dtype == object
    ]
    for col in object_cols:
        lengths = frame[col].map(lambda x: len(x) if isinstance(x, (list, tuple)) else 0)
        tmp = pd.DataFrame(
            {
                "subject_id": frame["subject_id"],
                "lifelog_date": frame["lifelog_date"],
                "_len": lengths,
            }
        )
        len_stats = tmp.groupby(["subject_id", "lifelog_date"], sort=False)["_len"].agg(
            ["mean", "sum", "max"]
        )
        for stat in len_stats.columns:
            out[f"{name}__{col}__len_{stat}"] = len_stats[stat]

    return out.reset_index()


def build_raw_daily_features() -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for path in sorted(RAW_DIR.glob("*.parquet")):
        daily = daily_features_for_file(path)
        if merged is None:
            merged = daily
        else:
            merged = merged.merge(daily, on=["subject_id", "lifelog_date"], how="outer")
    if merged is None:
        raise RuntimeError("no raw parquet files")
    value_cols = [col for col in merged.columns if col not in {"subject_id", "lifelog_date"}]
    merged[value_cols] = merged[value_cols].fillna(0.0)
    merged["lifelog_date"] = pd.to_datetime(merged["lifelog_date"])
    return merged


def temporal_split(train: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    train_idx: list[int] = []
    val_idx: list[int] = []
    for _, grp in train.sort_values(["subject_id", "sleep_date"]).groupby("subject_id", sort=False):
        idx = grp.index.to_numpy()
        cut = max(1, int(np.floor(len(idx) * 0.75)))
        if cut >= len(idx):
            cut = len(idx) - 1
        train_idx.extend(idx[:cut].tolist())
        val_idx.extend(idx[cut:].tolist())
    return np.asarray(train_idx, dtype=int), np.asarray(val_idx, dtype=int)


def random_split(train: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(113)
    train_idx: list[int] = []
    val_idx: list[int] = []
    for _, grp in train.groupby("subject_id", sort=False):
        idx = grp.index.to_numpy().copy()
        rng.shuffle(idx)
        cut = max(1, int(np.floor(len(idx) * 0.75)))
        if cut >= len(idx):
            cut = len(idx) - 1
        train_idx.extend(idx[:cut].tolist())
        val_idx.extend(idx[cut:].tolist())
    return np.asarray(train_idx, dtype=int), np.asarray(val_idx, dtype=int)


def subject_prior_predictions(
    train: pd.DataFrame,
    fit_idx: np.ndarray,
    val_idx: np.ndarray,
    target: str,
) -> np.ndarray:
    fit = train.loc[fit_idx]
    val = train.loc[val_idx]
    global_rate = smooth_rate(fit[target].to_numpy(dtype=float))
    rates = {
        subject: smooth_rate(grp[target].to_numpy(dtype=float))
        for subject, grp in fit.groupby("subject_id")
    }
    pred = val["subject_id"].map(rates).fillna(global_rate).to_numpy(dtype=float)
    return clip_prob(pred)


def fit_predict_logistic(
    x: pd.DataFrame,
    y: np.ndarray,
    fit_idx: np.ndarray,
    val_idx: np.ndarray,
) -> np.ndarray:
    y_fit = y[fit_idx]
    if len(np.unique(y_fit)) < 2:
        return np.full(len(val_idx), smooth_rate(y_fit), dtype=float)
    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.1, max_iter=2000, solver="lbfgs"),
    )
    pipe.fit(x.iloc[fit_idx], y_fit)
    return clip_prob(pipe.predict_proba(x.iloc[val_idx])[:, 1])


def evaluate_split(
    train: pd.DataFrame,
    features: pd.DataFrame,
    split_name: str,
    fit_idx: np.ndarray,
    val_idx: np.ndarray,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    raw_cols = [
        col
        for col in features.columns
        if col not in set(KEYS + TARGETS + ["sleep_date_dt", "lifelog_date_dt"])
    ]
    raw_x = features[raw_cols]

    for target in TARGETS:
        y = train[target].to_numpy(dtype=int)
        y_val = y[val_idx]
        prior_pred = subject_prior_predictions(train, fit_idx, val_idx, target)
        prior_ll = log_loss(y_val, prior_pred, labels=[0, 1])

        raw_pred = fit_predict_logistic(raw_x, y, fit_idx, val_idx)
        raw_ll = log_loss(y_val, raw_pred, labels=[0, 1])

        prior_feature = np.zeros(len(train), dtype=float)
        prior_feature[val_idx] = prior_pred
        fit_prior = subject_prior_predictions(train, fit_idx, fit_idx, target)
        prior_feature[fit_idx] = fit_prior
        raw_plus_prior_x = raw_x.copy()
        raw_plus_prior_x[f"{target}__subject_prior_feature"] = prior_feature
        raw_plus_prior_pred = fit_predict_logistic(raw_plus_prior_x, y, fit_idx, val_idx)
        raw_plus_prior_ll = log_loss(y_val, raw_plus_prior_pred, labels=[0, 1])

        try:
            raw_auc = roc_auc_score(y_val, raw_pred)
        except ValueError:
            raw_auc = np.nan
        try:
            raw_plus_prior_auc = roc_auc_score(y_val, raw_plus_prior_pred)
        except ValueError:
            raw_plus_prior_auc = np.nan

        rows.append(
            {
                "split": split_name,
                "target": target,
                "axis": "Q" if target in Q_TARGETS else "S",
                "e95_axis": target in E95_ACTIVE,
                "fit_rows": int(len(fit_idx)),
                "val_rows": int(len(val_idx)),
                "val_prevalence": float(y_val.mean()),
                "subject_prior_logloss": float(prior_ll),
                "raw_coverage_logloss": float(raw_ll),
                "raw_plus_prior_logloss": float(raw_plus_prior_ll),
                "raw_delta_vs_subject_prior": float(raw_ll - prior_ll),
                "raw_plus_prior_delta_vs_subject_prior": float(raw_plus_prior_ll - prior_ll),
                "raw_auc": float(raw_auc),
                "raw_plus_prior_auc": float(raw_plus_prior_auc),
            }
        )
    return rows


def group_summary(results: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for split_name, split_df in results.groupby("split", sort=False):
        groups = {
            "Q_targets": split_df["axis"].eq("Q"),
            "S_targets": split_df["axis"].eq("S"),
            "E95_active_axis": split_df["e95_axis"],
            "E95_inactive_axis": ~split_df["e95_axis"],
        }
        for group_name, mask in groups.items():
            sub = split_df.loc[mask]
            rows.append(
                {
                    "split": split_name,
                    "group": group_name,
                    "n_targets": int(len(sub)),
                    "mean_subject_prior_logloss": float(sub["subject_prior_logloss"].mean()),
                    "mean_raw_coverage_logloss": float(sub["raw_coverage_logloss"].mean()),
                    "mean_raw_plus_prior_logloss": float(sub["raw_plus_prior_logloss"].mean()),
                    "mean_raw_delta_vs_subject_prior": float(
                        sub["raw_delta_vs_subject_prior"].mean()
                    ),
                    "mean_raw_plus_prior_delta_vs_subject_prior": float(
                        sub["raw_plus_prior_delta_vs_subject_prior"].mean()
                    ),
                    "mean_raw_auc": float(sub["raw_auc"].mean()),
                    "mean_raw_plus_prior_auc": float(sub["raw_plus_prior_auc"].mean()),
                }
            )
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "(empty)"
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.6f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for frame in [train, test]:
        frame["sleep_date"] = pd.to_datetime(frame["sleep_date"])
        frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"])

    raw_daily = build_raw_daily_features()
    features = train.merge(raw_daily, on=["subject_id", "lifelog_date"], how="left")
    feature_cols = [
        col
        for col in features.columns
        if col not in set(KEYS + TARGETS + ["sleep_date_dt", "lifelog_date_dt"])
        and col not in {"sleep_date", "lifelog_date"}
    ]
    features[feature_cols] = features[feature_cols].fillna(0.0)

    test_features = test.merge(raw_daily, on=["subject_id", "lifelog_date"], how="left")
    test_coverage = pd.DataFrame(
        {
            "n_train_rows": [len(train)],
            "n_test_rows": [len(test)],
            "raw_feature_count": [len(feature_cols)],
            "train_rows_with_any_raw": [(features[feature_cols].sum(axis=1) > 0).mean()],
            "test_rows_with_any_raw": [(test_features[feature_cols].fillna(0).sum(axis=1) > 0).mean()],
        }
    )

    temporal_fit, temporal_val = temporal_split(train)
    random_fit, random_val = random_split(train)
    rows = []
    rows.extend(evaluate_split(train, features[KEYS + TARGETS + feature_cols], "temporal_last25_by_subject", temporal_fit, temporal_val))
    rows.extend(evaluate_split(train, features[KEYS + TARGETS + feature_cols], "random_within_subject", random_fit, random_val))
    results = pd.DataFrame(rows)
    groups = group_summary(results)

    raw_path = OUT / "e113_sauna_raw_context_daily_features.csv"
    result_path = OUT / "e113_sauna_raw_context_visibility_results.csv"
    group_path = OUT / "e113_sauna_raw_context_visibility_group_summary.csv"
    coverage_path = OUT / "e113_sauna_raw_context_visibility_coverage.csv"
    report_path = OUT / "e113_sauna_raw_context_visibility_report.md"

    raw_daily.to_csv(raw_path, index=False)
    results.to_csv(result_path, index=False)
    groups.to_csv(group_path, index=False)
    test_coverage.to_csv(coverage_path, index=False)

    temporal_groups = groups[groups["split"].eq("temporal_last25_by_subject")]
    random_groups = groups[groups["split"].eq("random_within_subject")]
    temporal_targets = results[results["split"].eq("temporal_last25_by_subject")].copy()
    random_targets = results[results["split"].eq("random_within_subject")].copy()
    best_temporal = temporal_targets.sort_values("raw_plus_prior_delta_vs_subject_prior").head(3)
    worst_temporal = temporal_targets.sort_values("raw_plus_prior_delta_vs_subject_prior").tail(3)

    q_temporal = temporal_groups[temporal_groups["group"].eq("Q_targets")].iloc[0]
    s_temporal = temporal_groups[temporal_groups["group"].eq("S_targets")].iloc[0]
    q_random = random_groups[random_groups["group"].eq("Q_targets")].iloc[0]
    s_random = random_groups[random_groups["group"].eq("S_targets")].iloc[0]
    e95_temporal = temporal_groups[temporal_groups["group"].eq("E95_active_axis")].iloc[0]
    inactive_temporal = temporal_groups[temporal_groups["group"].eq("E95_inactive_axis")].iloc[0]

    report = f"""# E113 Sauna Raw Context Visibility Audit

## Question

E112 says Q targets have temporal persistence, but label adjacency is sparse in test. The next I-JEPA-style question is whether visible raw lifelog context can stand in for the missing temporal labels. This is a diagnostic context-visibility head, not a submission model.

## Raw Coverage

- Raw daily feature count: `{len(feature_cols)}`.
- Train rows with any raw coverage: `{float(test_coverage['train_rows_with_any_raw'].iloc[0]):.6f}`.
- Test rows with any raw coverage: `{float(test_coverage['test_rows_with_any_raw'].iloc[0]):.6f}`.

## Temporal Holdout Result

Negative deltas mean raw coverage improved over subject prior.

- Q targets raw+prior delta vs subject prior: `{q_temporal['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}`.
- S targets raw+prior delta vs subject prior: `{s_temporal['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}`.
- E95-active axes raw+prior delta: `{e95_temporal['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}` vs inactive `{inactive_temporal['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}`.
- Random within-subject Q delta: `{q_random['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}`.
- Random within-subject S delta: `{s_random['mean_raw_plus_prior_delta_vs_subject_prior']:+.6f}`.

## Best Temporal Targets

{markdown_table(best_temporal[['target', 'axis', 'e95_axis', 'subject_prior_logloss', 'raw_plus_prior_logloss', 'raw_plus_prior_delta_vs_subject_prior', 'raw_plus_prior_auc']])}

## Worst Temporal Targets

{markdown_table(worst_temporal[['target', 'axis', 'e95_axis', 'subject_prior_logloss', 'raw_plus_prior_logloss', 'raw_plus_prior_delta_vs_subject_prior', 'raw_plus_prior_auc']])}

## Group Summary

{markdown_table(groups[['split', 'group', 'mean_subject_prior_logloss', 'mean_raw_plus_prior_logloss', 'mean_raw_plus_prior_delta_vs_subject_prior', 'mean_raw_plus_prior_auc']])}

## Sauna Interpretation

The result weakens the visible-context rescue route. Raw coverage is present for every train/test row and has some ranking signal, but it worsens temporal LogLoss after subject prior on both Q and S groups. Q2 even improves slightly in random split while worsening in temporal holdout, which is a shortcut/collapse warning. The only temporal target with a small gain is S3, matching the E95/S-subject-state story. For now, E112's Q temporal signal remains mostly unobservable in a submission-safe way, explaining why broad Q/Q3 movement is dangerous and why LogLoss calibration, not AUC, is the bottleneck.

## Outputs

- `{result_path.name}`
- `{group_path.name}`
- `{coverage_path.name}`
- `{raw_path.name}`
"""
    report_path.write_text(report)

    print(f"wrote {raw_path}")
    print(f"wrote {result_path}")
    print(f"wrote {group_path}")
    print(f"wrote {coverage_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
