from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class Source:
    name: str
    oof_path: Path
    submission_path: Path


@dataclass(frozen=True)
class Variant:
    name: str
    source: str
    anchor_source: str | None = None
    source_weight: float = 1.0
    blend_method: str = "none"
    temperature: float = 1.0
    clip_low: float = EPS
    clip_high: float = 1.0 - EPS
    prior_shrink: float = 0.0


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1.0 - EPS)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")["panel_position"].to_numpy(float)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")["panel_position"].to_numpy(float)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out["panel_position"] = train_pos
    sample_out["panel_position"] = sample_pos
    return train_out, sample_out


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    bins = np.asarray([0.0, 1 / 3, 2 / 3, 0.8, 1.000001], dtype=float)
    train_bin = np.digitize(train["panel_position"].to_numpy(float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(float), bins) - 1
    train_frac = np.bincount(train_bin, minlength=len(bins) - 1).astype(float) / len(train)
    sample_frac = np.bincount(sample_bin, minlength=len(bins) - 1).astype(float) / len(sample)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros_like(train_frac), where=train_frac > 0)
    weights = ratio[train_bin]
    return weights / weights.mean()


def row_logloss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1.0 - y) * np.log1p(-pred)).mean(axis=1)


def avg_logloss(y: np.ndarray, pred: np.ndarray, weights: np.ndarray | None = None) -> float:
    losses = []
    for target_i in range(len(TARGET_COLUMNS)):
        loss = -(y[:, target_i] * np.log(pred[:, target_i]) + (1.0 - y[:, target_i]) * np.log1p(-pred[:, target_i]))
        if weights is None:
            losses.append(float(loss.mean()))
        else:
            losses.append(float(np.average(loss, weights=weights)))
    return float(np.mean(losses))


def transform(pred: np.ndarray, variant: Variant, prior: np.ndarray) -> np.ndarray:
    out = pred.copy()
    if variant.temperature != 1.0:
        out = sigmoid(safe_logit(out) / variant.temperature)
    if variant.prior_shrink > 0:
        out = (1.0 - variant.prior_shrink) * out + variant.prior_shrink * prior[None, :]
    out = np.clip(out, variant.clip_low, variant.clip_high)
    return np.clip(out, EPS, 1.0 - EPS)


def blend_predictions(anchor_pred: np.ndarray, source_pred: np.ndarray, variant: Variant) -> np.ndarray:
    source_weight = float(variant.source_weight)
    if not 0.0 <= source_weight <= 1.0:
        raise ValueError(f"source_weight must be in [0, 1]: {variant.name}")
    anchor_weight = 1.0 - source_weight
    if variant.blend_method == "prob":
        return anchor_weight * anchor_pred + source_weight * source_pred
    if variant.blend_method == "logit":
        return sigmoid(anchor_weight * safe_logit(anchor_pred) + source_weight * safe_logit(source_pred))
    raise ValueError(f"Unknown blend_method for anchored variant {variant.name}: {variant.blend_method}")


def variant_predictions(loaded: dict[str, dict[str, np.ndarray]], variant: Variant, prior: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if variant.source not in loaded:
        raise KeyError(variant.source)
    source = loaded[variant.source]
    if variant.anchor_source is None:
        oof_pred = source["oof"]
        sub_pred = source["submission"]
    else:
        if variant.anchor_source not in loaded:
            raise KeyError(variant.anchor_source)
        anchor = loaded[variant.anchor_source]
        oof_pred = blend_predictions(anchor["oof"], source["oof"], variant)
        sub_pred = blend_predictions(anchor["submission"], source["submission"], variant)
    return transform(oof_pred, variant, prior), transform(sub_pred, variant, prior)


def stats(values: np.ndarray) -> dict[str, float]:
    logits = safe_logit(values)
    return {
        "min": float(values.min()),
        "p01": float(np.quantile(values, 0.01)),
        "p05": float(np.quantile(values, 0.05)),
        "mean": float(values.mean()),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
        "max": float(values.max()),
        "abs_logit_mean": float(np.abs(logits).mean()),
        "extreme_005_995": float(((values < 0.005) | (values > 0.995)).mean()),
    }


def sources() -> list[Source]:
    return [
        Source(
            "oldbalanced",
            Path("outputs/sample_oldbalanced_plus_q1fastmid_vs_multi_signal/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_oldbalanced_plus_q1fastmid_vs_multi_signal/submission_sample_support_target_blend.csv"),
        ),
        Source(
            "v17_robust",
            Path("outputs/sample_weighted_targetwise_portfolio_v17_robust/oof_sample_weighted_targetwise_blend.csv"),
            Path("outputs/sample_weighted_targetwise_portfolio_v17_robust/submission_sample_weighted_targetwise_blend.csv"),
        ),
        Source(
            "v18_q3tail",
            Path("outputs/sample_portfolio_v18_q3tail_w100/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_portfolio_v18_q3tail_w100/submission_sample_support_target_blend.csv"),
        ),
        Source(
            "v35e",
            Path("outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/submission_sample_support_target_blend.csv"),
        ),
        Source(
            "v38a_bad_lb",
            Path("outputs/sample_portfolio_v38a_v37e_mid_tail_push/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_portfolio_v38a_v37e_mid_tail_push/submission_sample_support_target_blend.csv"),
        ),
    ]


def variants() -> list[Variant]:
    return [
        Variant("01_oldbalanced_raw_safest", "oldbalanced"),
        Variant("02_v17_robust_raw", "v17_robust"),
        Variant("03_v18_q3tail_raw", "v18_q3tail"),
        Variant("04_v17_robust_temp125_clip01", "v17_robust", temperature=1.25, clip_low=0.01, clip_high=0.99),
        Variant("05_v18_q3tail_temp125_clip01", "v18_q3tail", temperature=1.25, clip_low=0.01, clip_high=0.99),
        Variant("06_v17_robust_temp150_clip02", "v17_robust", temperature=1.50, clip_low=0.02, clip_high=0.98),
        Variant("07_oldbalanced_temp125_clip02", "oldbalanced", temperature=1.25, clip_low=0.02, clip_high=0.98),
        Variant("08_v17_robust_prior10_temp125_clip01", "v17_robust", temperature=1.25, clip_low=0.01, clip_high=0.99, prior_shrink=0.10),
        Variant("09_v35e_temp150_clip02_control", "v35e", temperature=1.50, clip_low=0.02, clip_high=0.98),
        Variant("10_v38a_temp200_clip02_recovery_probe", "v38a_bad_lb", temperature=2.00, clip_low=0.02, clip_high=0.98, prior_shrink=0.10),
        Variant("11_v18_old10_prob_blend", "v18_q3tail", anchor_source="oldbalanced", source_weight=0.90, blend_method="prob"),
        Variant("12_v18_old20_prob_blend", "v18_q3tail", anchor_source="oldbalanced", source_weight=0.80, blend_method="prob"),
        Variant("13_v18_old30_prob_blend", "v18_q3tail", anchor_source="oldbalanced", source_weight=0.70, blend_method="prob"),
        Variant("14_v17_old20_logit_blend", "v17_robust", anchor_source="oldbalanced", source_weight=0.80, blend_method="logit"),
        Variant("15_v18_old15_prob_blend", "v18_q3tail", anchor_source="oldbalanced", source_weight=0.85, blend_method="prob"),
    ]


def main() -> None:
    train = normalize_keys(pd.read_csv("data/ch2026_metrics_train.csv"))
    sample = normalize_keys(pd.read_csv("data/ch2026_submission_sample.csv"))
    train, sample = add_panel_position(train, sample)
    weights = sample_position_weights(train, sample)
    y = train[TARGET_COLUMNS].to_numpy(float)
    prior = train[TARGET_COLUMNS].mean().to_numpy(float)
    output_dir = Path("outputs/lb_feedback_recovery_uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded = {}
    for source in sources():
        if not source.oof_path.exists() or not source.submission_path.exists():
            continue
        oof = normalize_keys(pd.read_csv(source.oof_path))
        submission = normalize_keys(pd.read_csv(source.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"OOF key mismatch: {source.name}")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"Submission key mismatch: {source.name}")
        loaded[source.name] = {
            "oof_frame": oof,
            "submission_frame": submission,
            "oof": prediction_matrix(oof),
            "submission": submission_matrix(submission),
        }

    rows = []
    for variant in variants():
        if variant.source not in loaded:
            continue
        if variant.anchor_source is not None and variant.anchor_source not in loaded:
            continue
        oof_pred, sub_pred = variant_predictions(loaded, variant, prior)

        oof_out = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
        sub_out = sample[KEY_COLUMNS].copy()
        for target_i, target in enumerate(TARGET_COLUMNS):
            oof_out[f"pred_{target}"] = oof_pred[:, target_i]
            sub_out[target] = sub_pred[:, target_i]
        oof_path = output_dir / f"oof_{variant.name}.csv"
        sub_path = output_dir / f"submission_{variant.name}.csv"
        oof_out.to_csv(oof_path, index=False)
        sub_out.to_csv(sub_path, index=False)

        row = {
            "variant": variant.name,
            "source": variant.source,
            "anchor_source": variant.anchor_source,
            "source_weight": variant.source_weight,
            "blend_method": variant.blend_method,
            "temperature": variant.temperature,
            "clip_low": variant.clip_low,
            "clip_high": variant.clip_high,
            "prior_shrink": variant.prior_shrink,
            "uniform_oof_cv": avg_logloss(y, oof_pred),
            "sample_weighted_oof_cv": avg_logloss(y, oof_pred, weights),
            "oof_path": str(oof_path),
            "submission_path": str(sub_path),
            **stats(sub_pred),
        }
        rows.append(row)

    report = pd.DataFrame(rows).sort_values(
        ["extreme_005_995", "sample_weighted_oof_cv", "abs_logit_mean"],
        ascending=[True, True, True],
    )
    report.to_csv(output_dir / "recovery_upload_report.csv", index=False)
    (output_dir / "recovery_upload_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
