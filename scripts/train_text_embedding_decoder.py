from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import onnxruntime as ort
import pandas as pd
from huggingface_hub import HfApi, hf_hub_download
from pandas.errors import PerformanceWarning
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tokenizers import Tokenizer


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class TextModelSpec:
    repo_id: str
    onnx_file: str
    license_name: str


@dataclass(frozen=True)
class SourceSpec:
    name: str
    features: list[str]
    c_value: float
    class_weight: str | None


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return submission[TARGET_COLUMNS].to_numpy(dtype=float)


def score(y: pd.DataFrame, pred: np.ndarray) -> float:
    return float(
        np.mean(
            [
                log_loss(y[target], np.clip(pred[:, i], EPS, 1.0 - EPS), labels=[0, 1])
                for i, target in enumerate(TARGET_COLUMNS)
            ]
        )
    )


def clean_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def iter_list(value: object) -> Iterable[object]:
    if value is None:
        return []
    if isinstance(value, float) and math.isnan(value):
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, list):
        return value
    return []


def extract_usage_texts(path: str) -> list[str]:
    frame = pd.read_parquet(path, columns=["m_usage_stats"])
    labels = set()
    for value in frame["m_usage_stats"].dropna():
        for item in iter_list(value):
            if isinstance(item, dict) and "app_name" in item:
                label = clean_text(item["app_name"])
                if label:
                    labels.add(label)
    return sorted(labels)


def extract_ambience_texts(path: str) -> list[str]:
    frame = pd.read_parquet(path, columns=["m_ambience"])
    labels = set()
    for value in frame["m_ambience"].dropna():
        for item in iter_list(value):
            if hasattr(item, "tolist"):
                item = item.tolist()
            if isinstance(item, (list, tuple)) and len(item) >= 1:
                label = clean_text(item[0])
                if label:
                    labels.add(label)
    return sorted(labels)


def resolve_model(repo_id: str, onnx_file: str) -> TextModelSpec:
    info = HfApi().model_info(repo_id)
    card_data = info.card_data
    if isinstance(card_data, dict):
        license_name = str(card_data.get("license", "")).lower()
    else:
        license_name = str(getattr(card_data, "license", "")).lower()
    if not license_name:
        for tag in info.tags:
            if tag.startswith("license:"):
                license_name = tag.split(":", 1)[1].lower()
                break
    allowed = {"apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause"}
    if license_name not in allowed:
        raise RuntimeError(f"Model license is not in the explicit allowed list: repo={repo_id} license={license_name!r}")
    return TextModelSpec(repo_id=repo_id, onnx_file=onnx_file, license_name=license_name)


def mean_pool(last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    mask = attention_mask[..., None].astype(np.float32)
    pooled = (last_hidden_state * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1.0)
    norm = np.linalg.norm(pooled, axis=1, keepdims=True)
    return pooled / np.maximum(norm, 1e-12)


def encode_texts(texts: list[str], model_spec: TextModelSpec, batch_size: int) -> dict[str, np.ndarray]:
    if not texts:
        return {}
    tokenizer_path = hf_hub_download(model_spec.repo_id, "tokenizer.json")
    onnx_path = hf_hub_download(model_spec.repo_id, model_spec.onnx_file)
    tokenizer = Tokenizer.from_file(tokenizer_path)
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_names = {item.name for item in session.get_inputs()}

    vectors: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        encodings = tokenizer.encode_batch(batch)
        max_len = max(len(encoding.ids) for encoding in encodings)

        def pad(values: list[int], pad_value: int = 0) -> list[int]:
            return values + [pad_value] * (max_len - len(values))

        inputs = {
            "input_ids": np.asarray([pad(encoding.ids) for encoding in encodings], dtype=np.int64),
            "attention_mask": np.asarray([pad(encoding.attention_mask) for encoding in encodings], dtype=np.int64),
            "token_type_ids": np.asarray([pad(encoding.type_ids) for encoding in encodings], dtype=np.int64),
        }
        outputs = session.run(None, {name: values for name, values in inputs.items() if name in input_names})
        vectors.append(mean_pool(outputs[0], inputs["attention_mask"]))
    matrix = np.vstack(vectors).astype(np.float32)
    return {text: matrix[i] for i, text in enumerate(texts)}


def empty_acc(dim: int) -> dict[str, object]:
    return {"sum": np.zeros(dim, dtype=np.float64), "weight": 0.0, "count": 0.0, "max_weight": 0.0, "sumsq_weight": 0.0}


def aggregate_usage(path: str, embeddings: dict[str, np.ndarray], dim: int) -> dict[tuple[str, str, str], dict[str, object]]:
    frame = pd.read_parquet(path)
    acc: dict[tuple[str, str, str], dict[str, object]] = defaultdict(lambda: empty_acc(dim))
    for row in frame.itertuples(index=False):
        timestamp = pd.Timestamp(row.timestamp)
        key = (str(row.subject_id), timestamp.strftime("%Y-%m-%d"), "app")
        bucket = acc[key]
        for item in iter_list(row.m_usage_stats):
            if not isinstance(item, dict):
                continue
            label = clean_text(item.get("app_name", ""))
            if label not in embeddings:
                continue
            try:
                seconds = float(item.get("total_time", 0.0))
            except (TypeError, ValueError):
                seconds = 0.0
            weight = math.log1p(max(seconds, 0.0))
            if weight <= 0.0:
                continue
            bucket["sum"] += embeddings[label] * weight
            bucket["weight"] = float(bucket["weight"]) + weight
            bucket["count"] = float(bucket["count"]) + 1.0
            bucket["max_weight"] = max(float(bucket["max_weight"]), weight)
            bucket["sumsq_weight"] = float(bucket["sumsq_weight"]) + weight * weight
    return acc


def aggregate_ambience(path: str, embeddings: dict[str, np.ndarray], dim: int) -> dict[tuple[str, str, str], dict[str, object]]:
    frame = pd.read_parquet(path)
    acc: dict[tuple[str, str, str], dict[str, object]] = defaultdict(lambda: empty_acc(dim))
    for row in frame.itertuples(index=False):
        timestamp = pd.Timestamp(row.timestamp)
        channels = ["amb"]
        if timestamp.hour < 6 or timestamp.hour >= 22:
            channels.append("amb_night")
        for channel in channels:
            key = (str(row.subject_id), timestamp.strftime("%Y-%m-%d"), channel)
            bucket = acc[key]
            for item in iter_list(row.m_ambience):
                if hasattr(item, "tolist"):
                    item = item.tolist()
                if not isinstance(item, (list, tuple)) or len(item) < 2:
                    continue
                label = clean_text(item[0])
                if label not in embeddings:
                    continue
                try:
                    weight = float(item[1])
                except (TypeError, ValueError):
                    weight = 0.0
                if weight <= 0.0:
                    continue
                bucket["sum"] += embeddings[label] * weight
                bucket["weight"] = float(bucket["weight"]) + weight
                bucket["count"] = float(bucket["count"]) + 1.0
                bucket["max_weight"] = max(float(bucket["max_weight"]), weight)
                bucket["sumsq_weight"] = float(bucket["sumsq_weight"]) + weight * weight
    return acc


def add_embedding_features(
    features: pd.DataFrame,
    all_features: pd.DataFrame,
    channel: str,
    acc: dict[tuple[str, str, str], dict[str, object]],
    n_components: int,
    dim: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    rows = []
    stats = []
    for row in all_features.itertuples(index=False):
        key = (str(row.subject_id), str(row.lifelog_date), channel)
        bucket = acc.get(key)
        if bucket is None or float(bucket["weight"]) <= 0.0:
            rows.append(np.zeros(dim, dtype=np.float64))
            stats.append([0.0, 0.0, 0.0, 0.0])
            continue
        weight = float(bucket["weight"])
        rows.append(np.asarray(bucket["sum"], dtype=np.float64) / weight)
        stats.append([math.log1p(weight), float(bucket["count"]), float(bucket["max_weight"]), float(bucket["sumsq_weight"]) / max(weight * weight, 1e-12)])
    matrix = np.vstack(rows)
    n_comp = min(n_components, matrix.shape[1], max(1, len(matrix) - 1))
    pca = PCA(n_components=n_comp, random_state=2026)
    pcs = pca.fit_transform(matrix)
    pc_cols = [f"{channel}_embed_pc_{i:02d}" for i in range(n_comp)]
    stat_cols = [f"{channel}_embed_log_weight", f"{channel}_embed_count", f"{channel}_embed_max_weight", f"{channel}_embed_weight_hhi"]
    enriched = all_features.copy()
    enriched[pc_cols] = pcs
    enriched[stat_cols] = np.asarray(stats, dtype=float)
    added = pc_cols + stat_cols
    return features.merge(enriched[KEY_COLUMNS + added], on=KEY_COLUMNS, how="left", validate="one_to_one"), enriched, added


def build_base_frame(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0.0, 1.0)
    ordered["panel_position"] = ordered["panel_index"] / denom
    date = pd.to_datetime(ordered["lifelog_date"])
    dow = date.dt.dayofweek.astype(float)
    ordered["dow_sin"] = np.sin(2 * np.pi * dow / 7.0)
    ordered["dow_cos"] = np.cos(2 * np.pi * dow / 7.0)
    ordered["is_weekend"] = dow.isin([5, 6]).astype(float)
    restored = ordered.sort_values(["_split", "_row"])
    train_features = restored[restored["_split"].eq("train")].sort_values("_row")[KEY_COLUMNS + ["panel_index", "panel_position", "dow_sin", "dow_cos", "is_weekend"]].reset_index(drop=True)
    sample_features = restored[restored["_split"].eq("sample")].sort_values("_row")[KEY_COLUMNS + ["panel_index", "panel_position", "dow_sin", "dow_cos", "is_weekend"]].reset_index(drop=True)
    all_features = pd.concat([train_features, sample_features], ignore_index=True)
    return train_features, sample_features, all_features


def add_base_predictions(
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_oof_path: str,
    base_submission_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    oof = normalize_keys(pd.read_csv(base_oof_path))
    submission = normalize_keys(pd.read_csv(base_submission_path))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    train_pred = np.clip(prediction_matrix(oof), EPS, 1.0 - EPS)
    test_pred = np.clip(submission_matrix(submission), EPS, 1.0 - EPS)
    cols = []
    for i, target in enumerate(TARGET_COLUMNS):
        for suffix, train_values, test_values in [
            ("prob", train_pred[:, i], test_pred[:, i]),
            ("logit", safe_logit(train_pred[:, i]), safe_logit(test_pred[:, i])),
        ]:
            col = f"base_{target}_{suffix}"
            features_train[col] = train_values
            features_test[col] = test_values
            cols.append(col)
    return features_train, features_test, cols


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


def train_source(
    spec: SourceSpec,
    features_train: pd.DataFrame,
    features_test: pd.DataFrame,
    labels: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    output_dir: Path,
) -> dict[str, object]:
    x_train = features_train[spec.features].to_numpy(dtype=np.float32)
    x_test = features_test[spec.features].to_numpy(dtype=np.float32)
    y = labels[TARGET_COLUMNS].astype(int)
    oof_pred = np.zeros((len(labels), len(TARGET_COLUMNS)), dtype=float)
    test_pred = np.zeros((len(features_test), len(TARGET_COLUMNS)), dtype=float)
    target_scores = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        target_values = y[target].to_numpy(dtype=int)
        for trn_idx, val_idx in folds:
            if len(np.unique(target_values[trn_idx])) < 2:
                oof_pred[val_idx, target_i] = float(np.mean(target_values[trn_idx]))
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(
                    C=spec.c_value,
                    class_weight=spec.class_weight,
                    max_iter=2500,
                    solver="lbfgs",
                    random_state=2026,
                ),
            )
            model.fit(x_train[trn_idx], target_values[trn_idx])
            oof_pred[val_idx, target_i] = model.predict_proba(x_train[val_idx])[:, 1]
        full_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(
                C=spec.c_value,
                class_weight=spec.class_weight,
                max_iter=2500,
                solver="lbfgs",
                random_state=2026,
            ),
        )
        full_model.fit(x_train, target_values)
        test_pred[:, target_i] = full_model.predict_proba(x_test)[:, 1]
        target_scores[target] = float(log_loss(target_values, np.clip(oof_pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))

    oof_pred = np.clip(oof_pred, EPS, 1.0 - EPS)
    test_pred = np.clip(test_pred, EPS, 1.0 - EPS)
    oof = labels[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = features_test[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = oof_pred[:, i]
        submission[target] = test_pred[:, i]
    oof_path = output_dir / f"oof_{spec.name}.csv"
    submission_path = output_dir / f"submission_{spec.name}.csv"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(submission_path, index=False)
    return {
        "name": spec.name,
        "avg_log_loss": score(y, oof_pred),
        "target_scores": target_scores,
        "n_features": len(spec.features),
        "c_value": spec.c_value,
        "class_weight": spec.class_weight,
        "oof_path": str(oof_path),
        "submission_path": str(submission_path),
    }


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def main() -> None:
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    model_spec = resolve_model(args.model_repo, args.onnx_file)
    usage_texts = extract_usage_texts(args.usage_path)
    ambience_texts = extract_ambience_texts(args.ambience_path)
    all_texts = sorted(set(usage_texts) | set(ambience_texts))
    embeddings = encode_texts(all_texts, model_spec, args.batch_size)
    if not embeddings:
        raise RuntimeError("No text embeddings were generated.")
    dim = len(next(iter(embeddings.values())))

    features_train, features_test, all_features = build_base_frame(train, sample)
    feature_columns = [col for col in features_train.columns if col not in KEY_COLUMNS]
    usage_acc = aggregate_usage(args.usage_path, embeddings, dim)
    ambience_acc = aggregate_ambience(args.ambience_path, embeddings, dim)

    for channel, acc in [("app", usage_acc), ("amb", ambience_acc), ("amb_night", ambience_acc)]:
        all_tmp = all_features.copy()
        train_join, all_enriched, added = add_embedding_features(features_train, all_tmp, channel, acc, args.pca_components, dim)
        test_join = features_test.merge(all_enriched[KEY_COLUMNS + added], on=KEY_COLUMNS, how="left", validate="one_to_one")
        features_train = train_join
        features_test = test_join
        all_features = all_enriched
        feature_columns.extend(added)

    features_train, features_test, base_cols = add_base_predictions(
        features_train,
        features_test,
        train,
        sample,
        args.base_oof,
        args.base_submission,
    )
    feature_columns.extend(base_cols)
    text_feature_columns = [col for col in feature_columns if not col.startswith("base_")]
    all_feature_columns = [col for col in features_train.columns if col not in KEY_COLUMNS]

    features_train[KEY_COLUMNS + all_feature_columns].to_csv(output_dir / "features_train.csv", index=False)
    features_test[KEY_COLUMNS + all_feature_columns].to_csv(output_dir / "features_test.csv", index=False)
    train[KEY_COLUMNS + TARGET_COLUMNS].to_csv(output_dir / "labels_train.csv", index=False)

    specs: list[SourceSpec] = []
    for c_value in parse_float_list(args.c_values):
        c_tag = str(c_value).replace(".", "p")
        specs.append(SourceSpec(f"textembed_only_c{c_tag}", text_feature_columns, c_value, None))
        specs.append(SourceSpec(f"textembed_base_c{c_tag}", all_feature_columns, c_value, None))
        specs.append(SourceSpec(f"textembed_base_bal_c{c_tag}", all_feature_columns, c_value, "balanced"))

    folds = make_subject_time_folds(train, args.n_folds)
    rows = [train_source(spec, features_train, features_test, train, folds, output_dir) for spec in specs]
    report = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    report.to_csv(output_dir / "text_embedding_report.csv", index=False)
    (output_dir / "text_embedding_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "model_repo": model_spec.repo_id,
        "onnx_file": model_spec.onnx_file,
        "license": model_spec.license_name,
        "runtime": "onnxruntime CPUExecutionProvider",
        "n_unique_usage_texts": len(usage_texts),
        "n_unique_ambience_texts": len(ambience_texts),
        "n_unique_encoded_texts": len(all_texts),
        "embedding_dim": dim,
        "pca_components_per_channel": args.pca_components,
        "channels": ["app", "amb", "amb_night"],
        "n_text_features": len(text_feature_columns),
        "n_base_features": len(base_cols),
        "n_total_features": len(all_feature_columns),
        "base_oof": args.base_oof,
        "base_submission": args.base_submission,
        "design_note": "The public pretrained model is used only to embed app names and ambience labels; no external labels are consumed.",
    }
    (output_dir / "feature_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report[["name", "avg_log_loss", "n_features", "class_weight"]].to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train public text-embedding source decoders for app and ambience strings.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--usage-path", default="data/ch2025_data_items/ch2025_mUsageStats.parquet")
    parser.add_argument("--ambience-path", default="data/ch2025_data_items/ch2025_mAmbience.parquet")
    parser.add_argument("--base-oof", default="outputs/master_aggressive_decoder_fast/oof_temporal_master_oof_blend.csv")
    parser.add_argument("--base-submission", default="outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv")
    parser.add_argument("--output-dir", default="outputs/text_embedding_decoder_v77")
    parser.add_argument("--model-repo", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    parser.add_argument("--onnx-file", default="onnx/model_qint8_arm64.onnx")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--pca-components", type=int, default=16)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--c-values", default="0.00003,0.0001,0.0003,0.001,0.003")
    return parser.parse_args()


if __name__ == "__main__":
    main()
