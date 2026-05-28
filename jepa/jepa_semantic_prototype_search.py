from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import jepa_ready_data_audit as audit  # noqa: E402


PCA_BUDGET = 16
PROTOTYPE_KS = [4, 6, 8, 10]
CONTEXT_VARIANTS = ["strict_surround", "strict_labelonly", "strict_prior"]
FAMILY_NAMES = [
    "label_rate_only",
    "label_state",
    "window_state",
    "modality_state",
    "mean_latent",
    "hybrid_raw",
    "hybrid_oracle",
]


def label_rate_only(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[np.asarray(block, dtype=int)]
    rates = np.nanmean(vals, axis=0)
    return np.nan_to_num(rates, nan=0.5).astype(np.float32)


def local_block_meta(rows: pd.DataFrame, block: np.ndarray) -> np.ndarray:
    part = rows.iloc[np.asarray(block, dtype=int)]
    return np.array(
        [
            len(block),
            part["subject_phase"].mean(),
            part["is_weekend"].mean(),
            part["dow"].mean() / 6.0,
        ],
        dtype=np.float32,
    )


def build_family_feature(name: str, rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, block: np.ndarray) -> np.ndarray:
    if name == "label_rate_only":
        return label_rate_only(y, block)
    if name == "label_state":
        return audit.block_label_state(y, block)
    if name == "window_state":
        return np.r_[audit.window_state(z, block), local_block_meta(rows, block)].astype(np.float32)
    if name == "modality_state":
        return np.r_[audit.modality_state(z, block), local_block_meta(rows, block)].astype(np.float32)
    if name == "mean_latent":
        return np.r_[audit.mean_latent(z, block), local_block_meta(rows, block)].astype(np.float32)
    if name == "hybrid_raw":
        return np.r_[audit.window_state(z, block), audit.modality_state(z, block), local_block_meta(rows, block)].astype(np.float32)
    if name == "hybrid_oracle":
        return np.r_[
            audit.block_label_state(y, block),
            audit.window_state(z, block),
            audit.modality_state(z, block),
            local_block_meta(rows, block),
        ].astype(np.float32)
    raise ValueError(name)


def build_matrix(name: str, rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    return np.vstack([build_family_feature(name, rows, z, y, b) for b in blocks]).astype(np.float32)


def transform_for_clustering(train_x: np.ndarray, val_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(np.nan_to_num(train_x, nan=0.0, posinf=0.0, neginf=0.0))
    va = scaler.transform(np.nan_to_num(val_x, nan=0.0, posinf=0.0, neginf=0.0))
    k = min(PCA_BUDGET, tr.shape[0] - 1, tr.shape[1])
    if k >= 2 and k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=297007)
        tr = pca.fit_transform(tr)
        va = pca.transform(va)
    return tr.astype(np.float32), va.astype(np.float32)


def rate_metrics(true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    sse = float(np.sum((true - pred) ** 2))
    mean = true.mean(axis=0, keepdims=True)
    sst = float(np.sum((true - mean) ** 2))
    r2 = 1.0 - sse / max(sst, 1e-12)
    rmse = float(np.sqrt(np.mean((true - pred) ** 2)))
    denom = np.linalg.norm(true, axis=1) * np.linalg.norm(pred, axis=1)
    cos = np.mean(np.sum(true * pred, axis=1) / np.maximum(denom, 1e-12))
    return {"r2": r2, "rmse": rmse, "cos": float(cos)}


def safe_log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    eps = 1e-6
    y_prob = np.clip(y_prob, eps, 1.0 - eps)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)
    labels = np.arange(y_prob.shape[1])
    return float(log_loss(y_true, y_prob, labels=labels))


def len_bucket(length: int) -> str:
    if length <= 2:
        return "short_1_2"
    if length <= 4:
        return "mid_3_4"
    return "long_5p"


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)
    lengths = adv.actual_lengths_by_subject(rows)

    fold_rows = []
    bucket_rows = []
    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=4, seed=297000)):
        known = adv.known_mask_for_train(rows, tr_idx)
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=160)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not train_blocks or not val_blocks:
            continue
        print(f"semantic-proto {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)

        train_parts = [audit.block_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
        val_parts = [audit.block_context_parts(rows, z, y, base_all, b, known) for b in val_blocks]
        train_label_rate = np.vstack([label_rate_only(y, b) for b in train_blocks]).astype(np.float32)
        val_label_rate = np.vstack([label_rate_only(y, b) for b in val_blocks]).astype(np.float32)
        val_lengths = np.array([len(b) for b in val_blocks], dtype=int)

        for family in FAMILY_NAMES:
            train_raw = build_matrix(family, rows, z, y, train_blocks)
            val_raw = build_matrix(family, rows, z, y, val_blocks)
            train_feat, val_feat = transform_for_clustering(train_raw, val_raw)

            for k in PROTOTYPE_KS:
                if train_feat.shape[0] <= k * 3:
                    continue
                km = MiniBatchKMeans(n_clusters=k, random_state=297100 + k, batch_size=256, n_init=10)
                train_proto = km.fit_predict(train_feat)
                val_proto = km.predict(val_feat)

                proto_rate = np.zeros((k, len(TARGETS)), dtype=np.float32)
                proto_count = np.bincount(train_proto, minlength=k).astype(np.float32)
                for cid in range(k):
                    mask = train_proto == cid
                    if mask.any():
                        proto_rate[cid] = train_label_rate[mask].mean(axis=0)
                    else:
                        proto_rate[cid] = train_label_rate.mean(axis=0)
                oracle_val_rate = proto_rate[val_proto]
                oracle_stats = rate_metrics(val_label_rate, oracle_val_rate)

                for ctx_name in CONTEXT_VARIANTS:
                    train_ctx = np.vstack([audit.build_context_variant(p, ctx_name) for p in train_parts]).astype(np.float32)
                    val_ctx = np.vstack([audit.build_context_variant(p, ctx_name) for p in val_parts]).astype(np.float32)
                    ctx_scaler = StandardScaler()
                    train_ctx_s = ctx_scaler.fit_transform(np.nan_to_num(train_ctx, nan=0.0, posinf=0.0, neginf=0.0))
                    val_ctx_s = ctx_scaler.transform(np.nan_to_num(val_ctx, nan=0.0, posinf=0.0, neginf=0.0))

                    clf = LogisticRegression(
                        C=1.0,
                        max_iter=1200,
                        solver="lbfgs",
                        random_state=297200 + k,
                    )
                    clf.fit(train_ctx_s, train_proto)
                    val_prob = clf.predict_proba(val_ctx_s).astype(np.float32)
                    val_pred = np.argmax(val_prob, axis=1)

                    pred_val_rate = val_prob @ proto_rate
                    pred_stats = rate_metrics(val_label_rate, pred_val_rate)

                    fold_rows.append(
                        {
                            "fold": fold,
                            "family": family,
                            "k": k,
                            "context_variant": ctx_name,
                            "proto_logloss": safe_log_loss(val_proto, val_prob),
                            "proto_acc": float(accuracy_score(val_proto, val_pred)),
                            "oracle_rate_r2": oracle_stats["r2"],
                            "oracle_rate_rmse": oracle_stats["rmse"],
                            "pred_rate_r2": pred_stats["r2"],
                            "pred_rate_rmse": pred_stats["rmse"],
                            "pred_rate_cos": pred_stats["cos"],
                            "prototype_balance_min": float(proto_count.min()),
                            "prototype_balance_entropy": float(
                                -(proto_count / proto_count.sum() * np.log(np.clip(proto_count / proto_count.sum(), 1e-9, 1.0))).sum()
                            ),
                        }
                    )

                    for n in range(len(val_blocks)):
                        bucket_rows.append(
                            {
                                "fold": fold,
                                "family": family,
                                "k": k,
                                "context_variant": ctx_name,
                                "length": int(val_lengths[n]),
                                "len_bucket": len_bucket(int(val_lengths[n])),
                                "true_proto": int(val_proto[n]),
                                "pred_proto": int(val_pred[n]),
                                "proto_correct": float(val_pred[n] == val_proto[n]),
                                "sample_logloss": float(-np.log(np.clip(val_prob[n, val_proto[n]], 1e-6, 1.0))),
                                "rate_sqerr": float(np.mean((val_label_rate[n] - pred_val_rate[n]) ** 2)),
                            }
                        )

    fold_df = pd.DataFrame(fold_rows)
    bucket_df = pd.DataFrame(bucket_rows)
    fold_df.to_csv(OUT / "jepa_semantic_prototype_search_folds.csv", index=False)
    bucket_df.to_csv(OUT / "jepa_semantic_prototype_search_bucket_rows.csv", index=False)

    summary = (
        fold_df.groupby(["family", "k", "context_variant"], as_index=False)
        .agg(
            proto_logloss=("proto_logloss", "mean"),
            proto_acc=("proto_acc", "mean"),
            oracle_rate_r2=("oracle_rate_r2", "mean"),
            pred_rate_r2=("pred_rate_r2", "mean"),
            pred_rate_rmse=("pred_rate_rmse", "mean"),
            pred_rate_cos=("pred_rate_cos", "mean"),
            prototype_balance_min=("prototype_balance_min", "mean"),
            prototype_balance_entropy=("prototype_balance_entropy", "mean"),
        )
    )
    summary["semantic_jepa_score"] = (
        -0.45 * summary["proto_logloss"]
        + 0.20 * summary["proto_acc"]
        + 0.20 * summary["pred_rate_r2"]
        + 0.10 * summary["oracle_rate_r2"]
        + 0.05 * summary["pred_rate_cos"]
    )
    summary = summary.sort_values(["context_variant", "semantic_jepa_score"], ascending=[True, False]).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_semantic_prototype_search_summary.csv", index=False)

    bucket_summary = (
        bucket_df.groupby(["family", "k", "context_variant", "len_bucket"], as_index=False)
        .agg(
            proto_acc=("proto_correct", "mean"),
            proto_logloss=("sample_logloss", "mean"),
            rate_mse=("rate_sqerr", "mean"),
            n=("length", "size"),
        )
    ).sort_values(["context_variant", "family", "k", "len_bucket"])
    bucket_summary.to_csv(OUT / "jepa_semantic_prototype_search_lenbucket.csv", index=False)

    report = [
        "# JEPA Semantic Prototype Search",
        "",
        "Goal: find hidden-block target representations that are more JEPA-like than raw block reconstruction. Each candidate family is clustered into K semantic prototypes; strict context then predicts prototype probabilities, and those probabilities are mapped back to 7 target rates.",
        "",
        "## Reading Guide",
        "",
        "- `proto_logloss`: how well strict context predicts the hidden block prototype.",
        "- `proto_acc`: top-1 prototype accuracy.",
        "- `oracle_rate_r2`: if the true prototype were known, how much label-rate structure it preserves.",
        "- `pred_rate_r2`: after context predicts prototype probabilities, how much label-rate structure survives.",
        "- `semantic_jepa_score`: coarse ranking score for JEPA-readiness.",
        "",
        "## Top Rows",
        "",
        summary.head(30).to_csv(index=False),
        "",
        "## Length Bucket Summary",
        "",
        bucket_summary.head(60).to_csv(index=False),
        "",
        "## Candidate Interpretation",
        "",
        "1. If coarse K works better than large K, the hidden target should be a small semantic codebook, not a detailed raw latent.",
        "2. If longer blocks improve prototype predictability, the next JEPA should enlarge the target episode scale.",
        "3. If `hybrid_oracle` dominates but raw-only families lag, raw sensors alone do not expose the semantic state; distillation from label-informed prototypes is the next step.",
        "4. If `strict_labelonly` beats `strict_surround`, surrounding raw context is noisy and should be gated or compressed before prediction.",
        "",
        "## Files",
        "",
        "- `jepa_semantic_prototype_search_folds.csv`",
        "- `jepa_semantic_prototype_search_summary.csv`",
        "- `jepa_semantic_prototype_search_lenbucket.csv`",
        "- `jepa_semantic_prototype_search_bucket_rows.csv`",
    ]
    (OUT / "jepa_semantic_prototype_search_report.md").write_text("\n".join(report), encoding="utf-8")

    print(summary.head(30).to_string(index=False), flush=True)
    print("\nlength bucket head")
    print(bucket_summary.head(60).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
