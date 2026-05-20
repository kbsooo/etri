from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-6


def safe_feature_name(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(value))[:80]


def masked_mean(values: np.ndarray, mask: np.ndarray, axis: tuple[int, ...]) -> np.ndarray:
    denom = mask.sum(axis=axis).clip(EPS)
    return (values * mask).sum(axis=axis) / denom


def masked_std(values: np.ndarray, mask: np.ndarray, axis: tuple[int, ...], mean: np.ndarray) -> np.ndarray:
    expanded = mean
    for ax in sorted(axis):
        expanded = np.expand_dims(expanded, ax)
    denom = mask.sum(axis=axis).clip(EPS)
    return np.sqrt((((values - expanded) ** 2) * mask).sum(axis=axis) / denom)


def masked_max(values: np.ndarray, mask: np.ndarray, axis: tuple[int, ...]) -> np.ndarray:
    safe = np.where(mask > 0, values, -np.inf)
    out = safe.max(axis=axis)
    return np.where(np.isfinite(out), out, 0.0)


def add_matrix_features(
    features: dict[str, np.ndarray],
    prefix: str,
    matrix: np.ndarray,
    names: list[str],
) -> None:
    for i, name in enumerate(names):
        features[f"{prefix}__{safe_feature_name(name)}"] = matrix[:, i]


def modality_indices(modalities: list[str]) -> dict[str, np.ndarray]:
    out: dict[str, list[int]] = {}
    for i, modality in enumerate(modalities):
        out.setdefault(modality, []).append(i)
    return {name: np.asarray(indices, dtype=int) for name, indices in out.items()}


def daypart_masks(slots: int, bin_minutes: int) -> dict[str, np.ndarray]:
    minutes = np.arange(slots) * bin_minutes
    return {
        "late_night": (minutes < 360),
        "morning": (minutes >= 360) & (minutes < 720),
        "afternoon": (minutes >= 720) & (minutes < 1080),
        "evening": (minutes >= 1080) & (minutes < 1320),
        "night": (minutes >= 1320),
    }


def build_features(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((input_dir / "tensor_metadata.json").read_text(encoding="utf-8"))
    arr = np.load(input_dir / "encoder_day_pyramid.npz")
    day_index = pd.read_csv(input_dir / "day_index.csv")
    actual = arr["actual"].astype(np.float32)
    actual_mask = arr["actual_mask"].astype(np.float32)
    normal = arr["normal_twin"].astype(np.float32)
    normal_mask = arr["normal_twin_mask"].astype(np.float32)
    delta = arr["delta"].astype(np.float32)
    abs_delta = arr["abs_delta"].astype(np.float32)
    gap_since = arr["gap_since"].astype(np.float32)
    event_tokens = arr["event_tokens"].astype(np.float32)
    event_mask = arr["event_mask"].astype(np.float32)
    prototype_mixture = arr["prototype_mixture"].astype(np.float32)
    prototype_features = arr["prototype_features"].astype(np.float32)
    day_context = arr["day_context"].astype(np.float32)

    channel_names = metadata["base_channel_names"]
    modalities = metadata["base_channel_modalities"]
    group_indices = modality_indices(modalities)
    slots = int(metadata["shape"]["slots"])
    bin_minutes = int(metadata["bin_minutes"])
    features: dict[str, np.ndarray] = {}

    coverage = actual_mask.mean(axis=1)
    normal_coverage = normal_mask.mean(axis=1)
    actual_mean = masked_mean(actual, actual_mask, axis=(1,))
    actual_std = masked_std(actual, actual_mask, axis=(1,), mean=actual_mean)
    actual_max = masked_max(actual, actual_mask, axis=(1,))
    delta_mean = masked_mean(delta, actual_mask, axis=(1,))
    delta_std = masked_std(delta, actual_mask, axis=(1,), mean=delta_mean)
    abs_delta_mean = masked_mean(abs_delta, actual_mask, axis=(1,))
    abs_delta_max = masked_max(abs_delta, actual_mask, axis=(1,))
    gap_mean = gap_since.mean(axis=1)
    gap_max = gap_since.max(axis=1)

    add_matrix_features(features, "ch_cov", coverage, channel_names)
    add_matrix_features(features, "ch_normcov", normal_coverage, channel_names)
    add_matrix_features(features, "ch_actual_mean", actual_mean, channel_names)
    add_matrix_features(features, "ch_actual_std", actual_std, channel_names)
    add_matrix_features(features, "ch_actual_max", actual_max, channel_names)
    add_matrix_features(features, "ch_delta_mean", delta_mean, channel_names)
    add_matrix_features(features, "ch_delta_std", delta_std, channel_names)
    add_matrix_features(features, "ch_abs_delta_mean", abs_delta_mean, channel_names)
    add_matrix_features(features, "ch_abs_delta_max", abs_delta_max, channel_names)
    add_matrix_features(features, "ch_gap_mean", gap_mean, channel_names)
    add_matrix_features(features, "ch_gap_max", gap_max, channel_names)

    for modality, idx in group_indices.items():
        mod_mask = actual_mask[:, :, idx]
        features[f"mod_cov__{safe_feature_name(modality)}"] = mod_mask.mean(axis=(1, 2))
        features[f"mod_abs_delta_mean__{safe_feature_name(modality)}"] = masked_mean(abs_delta[:, :, idx], mod_mask, axis=(1, 2))
        features[f"mod_abs_delta_max__{safe_feature_name(modality)}"] = masked_max(abs_delta[:, :, idx], mod_mask, axis=(1, 2))
        features[f"mod_delta_mean__{safe_feature_name(modality)}"] = masked_mean(delta[:, :, idx], mod_mask, axis=(1, 2))
        features[f"mod_gap_mean__{safe_feature_name(modality)}"] = gap_since[:, :, idx].mean(axis=(1, 2))
        for daypart, slot_mask in daypart_masks(slots, bin_minutes).items():
            part_mask = mod_mask[:, slot_mask, :]
            features[f"mod_{daypart}_abs_delta__{safe_feature_name(modality)}"] = masked_mean(
                abs_delta[:, slot_mask, :][:, :, idx],
                part_mask,
                axis=(1, 2),
            )
            features[f"mod_{daypart}_cov__{safe_feature_name(modality)}"] = part_mask.mean(axis=(1, 2))

    event_feature_names = metadata["event_feature_names"]
    type_cols = [i for i, name in enumerate(event_feature_names) if name.startswith("type__")]
    event_count = event_mask.sum(axis=1)
    features["event_count"] = event_count
    features["event_density"] = event_count / max(event_tokens.shape[1], 1)
    if type_cols:
        type_values = event_tokens[:, :, type_cols] * event_mask[:, :, None]
        type_counts = type_values.sum(axis=1)
        type_names = [event_feature_names[i].replace("type__", "") for i in type_cols]
        add_matrix_features(features, "event_type_count", type_counts, type_names)
        intensity_idx = event_feature_names.index("intensity") if "intensity" in event_feature_names else None
        abs_delta_idx = event_feature_names.index("abs_delta") if "abs_delta" in event_feature_names else None
        for col_i, type_name in enumerate(type_names):
            type_mask = type_values[:, :, col_i]
            denom = type_mask.sum(axis=1).clip(EPS)
            if intensity_idx is not None:
                features[f"event_intensity_mean__{safe_feature_name(type_name)}"] = (
                    event_tokens[:, :, intensity_idx] * type_mask
                ).sum(axis=1) / denom
                features[f"event_intensity_max__{safe_feature_name(type_name)}"] = np.where(
                    type_mask.max(axis=1) > 0,
                    np.where(type_mask > 0, event_tokens[:, :, intensity_idx], -np.inf).max(axis=1),
                    0.0,
                )
            if abs_delta_idx is not None:
                features[f"event_abs_delta_mean__{safe_feature_name(type_name)}"] = (
                    event_tokens[:, :, abs_delta_idx] * type_mask
                ).sum(axis=1) / denom

    for group_i, group_name in enumerate(metadata["prototype_group_names"]):
        for k in range(prototype_mixture.shape[2]):
            features[f"proto_mix__{safe_feature_name(group_name)}__k{k}"] = prototype_mixture[:, group_i, k]
        for feature_i, feature_name in enumerate(metadata["prototype_feature_names"]):
            features[f"proto_feat__{safe_feature_name(group_name)}__{safe_feature_name(feature_name)}"] = prototype_features[:, group_i, feature_i]

    for i, name in enumerate(metadata["day_context_names"]):
        features[f"day_context__{safe_feature_name(name)}"] = day_context[:, i]

    numeric = pd.DataFrame(features)
    numeric = numeric.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(np.float32)
    out = pd.concat([day_index.reset_index(drop=True), numeric], axis=1)
    out.to_parquet(output_dir / "day_summary_features.parquet", index=False)

    report = {
        "rows": int(len(out)),
        "features": int(numeric.shape[1]),
        "input_dir": str(input_dir),
        "output_path": str(output_dir / "day_summary_features.parquet"),
        "feature_blocks": {
            "channel": int(sum(name.startswith("ch_") for name in numeric.columns)),
            "modality_daypart": int(sum(name.startswith("mod_") for name in numeric.columns)),
            "event": int(sum(name.startswith("event_") for name in numeric.columns)),
            "prototype": int(sum(name.startswith("proto_") for name in numeric.columns)),
            "context": int(sum(name.startswith("day_context") for name in numeric.columns)),
        },
    }
    (output_dir / "day_summary_features_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "day_summary_features_report.md").write_text(
        "\n".join(
            [
                "# Encoder day summary features",
                "",
                f"- rows: `{report['rows']}`",
                f"- numeric features: `{report['features']}`",
                f"- output: `{report['output_path']}`",
                "",
                "## Feature blocks",
                "",
                *[f"- {name}: {count}" for name, count in report["feature_blocks"].items()],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tabular summaries from the Encoder Day Pyramid tensor.")
    parser.add_argument("--input-dir", default="outputs/encoder_day_pyramid")
    parser.add_argument("--output-dir", default="outputs/encoder_day_pyramid")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build_features(Path(args.input_dir), Path(args.output_dir))
