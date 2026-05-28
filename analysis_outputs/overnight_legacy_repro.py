from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import overnight_feature_experiments as ofe  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
KEY = ofe.KEY


def prepare_legacy() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_parquet(OUT / "train_deep_features.parquet")
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet")
    night = pd.read_parquet(OUT / "overnight_sensor_features.parquet")
    night_cols = [c for c in night.columns if c not in KEY]
    train = train.merge(night, on=KEY, how="left")
    sub = sub.merge(night, on=KEY, how="left")
    for frame in [train, sub]:
        frame["night_any_feature_present"] = frame[night_cols].notna().any(axis=1).astype(float)
        frame["night_feature_present_frac"] = frame[night_cols].notna().mean(axis=1).astype(float)
    return train, sub


def fit_predict_legacy(train_rows: pd.DataFrame, rows: pd.DataFrame, group: str):
    cols = ofe.feature_columns(train_rows, group)
    pipe, cols = ofe.make_pipeline(cols)
    pipe.fit(train_rows[cols], train_rows[ofe.TARGETS])
    return ofe.proba_matrix(pipe, rows, cols)


def nested_blend_legacy(train: pd.DataFrame, group: str):
    original_fit_predict = ofe.fit_predict
    try:
        ofe.fit_predict = fit_predict_legacy
        return ofe.nested_blend(train, group)
    finally:
        ofe.fit_predict = original_fit_predict


def make_submission_legacy(train: pd.DataFrame, sub: pd.DataFrame, group: str, weights: pd.Series) -> pd.DataFrame:
    original_fit_predict = ofe.fit_predict
    try:
        ofe.fit_predict = fit_predict_legacy
        return ofe.make_submission(train, sub, group, weights)
    finally:
        ofe.fit_predict = original_fit_predict


def main() -> None:
    train, sub = prepare_legacy()
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    groups = ["overnight_phone", "overnight_all"]
    rows = []
    weights = []
    for group in groups:
        result, weight = nested_blend_legacy(train, group)
        rows.append(result)
        weights.append(weight)
    results = pd.concat(rows, ignore_index=True).sort_values(["mean", "group", "model"])
    weight_frame = pd.concat(weights, ignore_index=True)
    results.to_csv(OUT / "overnight_legacy_nested_results.csv", index=False)
    weight_frame.to_csv(OUT / "overnight_legacy_nested_weights.csv", index=False)

    phone_sensor_q1 = results[
        results["group"].eq("overnight_phone") & results["model"].eq("sensor_only")
    ].iloc[0]["Q1"]
    phone_blend = results[
        results["group"].eq("overnight_phone") & results["model"].eq("nested_blend")
    ].iloc[0]
    all_blend = results[
        results["group"].eq("overnight_all") & results["model"].eq("nested_blend")
    ].iloc[0]
    summary = pd.DataFrame(
        [
            {"target": "Q1", "source": "legacy_overnight_phone_sensor_only", "cv_loss": float(phone_sensor_q1)},
            {"target": "S1", "source": "legacy_overnight_phone_nested_blend", "cv_loss": float(phone_blend["S1"])},
            {"target": "S3", "source": "legacy_overnight_all_nested_blend", "cv_loss": float(all_blend["S3"])},
        ]
    )
    summary.to_csv(OUT / "overnight_legacy_key_losses.csv", index=False)

    print(results.round(6).to_string(index=False))
    print("\nKey legacy losses")
    print(summary.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
