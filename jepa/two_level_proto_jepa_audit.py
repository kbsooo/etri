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
import jepa_friendly_atlas as atlas  # noqa: E402


CONTEXTS = ["prior_label", "past_label", "future_label", "bidir_label", "prior_raw", "prior_all", "full_strict"]
COARSE_SPECS = [("raw_mean", 4), ("raw_mean", 8), ("hybrid_raw", 4), ("teacher_hybrid", 10)]
SEMANTIC_SPECS = [("label_rate", 8), ("label_rate", 10), ("label_state", 8), ("label_state", 10)]
PCA_BUDGET = 24


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def transform(train_x: np.ndarray, val_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    va = scaler.transform(finite(val_x))
    k = min(PCA_BUDGET, tr.shape[0] - 1, tr.shape[1])
    if 1 < k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=299001)
        tr = pca.fit_transform(tr)
        va = pca.transform(va)
    return tr.astype(np.float32), va.astype(np.float32)


def one_hot(labels: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros((len(labels), k), dtype=np.float32)
    out[np.arange(len(labels)), labels.astype(int)] = 1.0
    return out


def fit_probs(train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray] | None:
    if np.unique(train_y).size < 2:
        return None
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    va = scaler.transform(finite(val_x))
    clf = LogisticRegression(C=0.75, max_iter=900, solver="lbfgs", random_state=299101)
    clf.fit(tr, train_y)

    def expand(raw: np.ndarray) -> np.ndarray:
        prob = np.full((raw.shape[0], k), 1e-6, dtype=np.float32)
        for col_i, cls in enumerate(clf.classes_):
            prob[:, int(cls)] = raw[:, col_i]
        prob = prob / prob.sum(axis=1, keepdims=True)
        return prob

    return expand(clf.predict_proba(tr)), expand(clf.predict_proba(va))


def safe_logloss(y_true: np.ndarray, prob: np.ndarray) -> float:
    prob = np.clip(prob, 1e-6, 1.0)
    prob = prob / prob.sum(axis=1, keepdims=True)
    return float(log_loss(y_true, prob, labels=np.arange(prob.shape[1])))


def rate_metrics(true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    true = finite(true)
    pred = finite(pred)
    sse = float(np.sum((true - pred) ** 2))
    mean = true.mean(axis=0, keepdims=True)
    sst = float(np.sum((true - mean) ** 2))
    denom = np.linalg.norm(true, axis=1) * np.linalg.norm(pred, axis=1)
    return {
        "r2": 1.0 - sse / max(sst, 1e-12),
        "rmse": float(np.sqrt(np.mean((true - pred) ** 2))),
        "cos": float(np.mean(np.sum(true * pred, axis=1) / np.maximum(denom, 1e-12))),
    }


def proto_rates(train_proto: np.ndarray, train_rate: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros((k, len(TARGETS)), dtype=np.float32)
    fallback = train_rate.mean(axis=0)
    for cid in range(k):
        mask = train_proto == cid
        out[cid] = train_rate[mask].mean(axis=0) if mask.any() else fallback
    return out


def fit_prototypes(
    family: str,
    k: int,
    rows: pd.DataFrame,
    z: np.ndarray,
    canvas: np.ndarray,
    y: np.ndarray,
    train_blocks: list[np.ndarray],
    val_blocks: list[np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
    train_target = atlas.build_target_matrix(family, rows, z, canvas, y, train_blocks)
    val_target = atlas.build_target_matrix(family, rows, z, canvas, y, val_blocks)
    train_feat, val_feat = transform(train_target, val_target)
    if len(train_feat) <= k * 4:
        return None
    km = MiniBatchKMeans(n_clusters=k, random_state=299201 + k, batch_size=256, n_init=10)
    train_proto = km.fit_predict(train_feat).astype(int)
    val_proto = km.predict(val_feat).astype(int)
    counts = np.bincount(train_proto, minlength=k)
    if counts.min() < 2:
        return None
    return train_proto, val_proto, train_feat, val_feat


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)
    lengths = adv.actual_lengths_by_subject(rows)

    out_rows = []
    for tr_idx, val_idx, fold in adv.geom.geometry_folds(train, sub, n_repeats=4, seed=299000):
        known = adv.known_mask_for_train(rows, tr_idx)
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=160)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if len(train_blocks) < 80 or len(val_blocks) < 8:
            continue
        print(f"two-level {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)

        train_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
        val_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in val_blocks]
        train_rate = np.vstack([atlas.label_rate(y, b) for b in train_blocks]).astype(np.float32)
        val_rate = np.vstack([atlas.label_rate(y, b) for b in val_blocks]).astype(np.float32)
        ctx_train = {c: np.vstack([atlas.build_context(p, c) for p in train_parts]).astype(np.float32) for c in CONTEXTS}
        ctx_val = {c: np.vstack([atlas.build_context(p, c) for p in val_parts]).astype(np.float32) for c in CONTEXTS}

        coarse_cache = {}
        for coarse_family, coarse_k in COARSE_SPECS:
            proto = fit_prototypes(coarse_family, coarse_k, rows, z, canvas, y, train_blocks, val_blocks)
            if proto is not None:
                coarse_cache[(coarse_family, coarse_k)] = proto

        semantic_cache = {}
        for semantic_family, semantic_k in SEMANTIC_SPECS:
            proto = fit_prototypes(semantic_family, semantic_k, rows, z, canvas, y, train_blocks, val_blocks)
            if proto is not None:
                semantic_cache[(semantic_family, semantic_k)] = proto

        for ctx in CONTEXTS:
            for semantic_family, semantic_k in semantic_cache:
                sem_train, sem_val, _sem_train_feat, _sem_val_feat = semantic_cache[(semantic_family, semantic_k)]
                sem_rate = proto_rates(sem_train, train_rate, semantic_k)
                oracle_stats = rate_metrics(val_rate, sem_rate[sem_val])
                direct = fit_probs(ctx_train[ctx], sem_train, ctx_val[ctx], semantic_k)
                if direct is not None:
                    _train_prob, direct_val_prob = direct
                    pred_stats = rate_metrics(val_rate, direct_val_prob @ sem_rate)
                    out_rows.append(
                        {
                            "fold": fold,
                            "context_variant": ctx,
                            "semantic_family": semantic_family,
                            "semantic_k": semantic_k,
                            "coarse_family": "none",
                            "coarse_k": 0,
                            "mode": "direct_semantic",
                            "semantic_logloss": safe_logloss(sem_val, direct_val_prob),
                            "semantic_acc": float(accuracy_score(sem_val, direct_val_prob.argmax(axis=1))),
                            "oracle_rate_r2": oracle_stats["r2"],
                            "pred_rate_r2": pred_stats["r2"],
                            "pred_rate_rmse": pred_stats["rmse"],
                            "pred_rate_cos": pred_stats["cos"],
                        }
                    )
                for coarse_family, coarse_k in coarse_cache:
                    coarse_train, coarse_val, _coarse_train_feat, _coarse_val_feat = coarse_cache[(coarse_family, coarse_k)]
                    coarse_probs = fit_probs(ctx_train[ctx], coarse_train, ctx_val[ctx], coarse_k)
                    if coarse_probs is None:
                        continue
                    coarse_train_prob, coarse_val_prob = coarse_probs
                    variants = {
                        "coarse_prob_only": (coarse_train_prob, coarse_val_prob),
                        "context_plus_coarse_prob": (
                            np.hstack([ctx_train[ctx], coarse_train_prob]),
                            np.hstack([ctx_val[ctx], coarse_val_prob]),
                        ),
                        "context_plus_true_coarse_train": (
                            np.hstack([ctx_train[ctx], one_hot(coarse_train, coarse_k)]),
                            np.hstack([ctx_val[ctx], coarse_val_prob]),
                        ),
                    }
                    for mode, (tr_aug, va_aug) in variants.items():
                        sem_pred = fit_probs(tr_aug, sem_train, va_aug, semantic_k)
                        if sem_pred is None:
                            continue
                        _sem_train_prob, sem_val_prob = sem_pred
                        pred_stats = rate_metrics(val_rate, sem_val_prob @ sem_rate)
                        out_rows.append(
                            {
                                "fold": fold,
                                "context_variant": ctx,
                                "semantic_family": semantic_family,
                                "semantic_k": semantic_k,
                                "coarse_family": coarse_family,
                                "coarse_k": coarse_k,
                                "mode": mode,
                                "semantic_logloss": safe_logloss(sem_val, sem_val_prob),
                                "semantic_acc": float(accuracy_score(sem_val, sem_val_prob.argmax(axis=1))),
                                "oracle_rate_r2": oracle_stats["r2"],
                                "pred_rate_r2": pred_stats["r2"],
                                "pred_rate_rmse": pred_stats["rmse"],
                                "pred_rate_cos": pred_stats["cos"],
                            }
                        )

    folds = pd.DataFrame(out_rows)
    folds.to_csv(OUT / "two_level_proto_jepa_folds.csv", index=False)
    summary = (
        folds.groupby(["context_variant", "semantic_family", "semantic_k", "coarse_family", "coarse_k", "mode"], as_index=False)
        .agg(
            folds=("fold", "nunique"),
            semantic_logloss=("semantic_logloss", "mean"),
            semantic_acc=("semantic_acc", "mean"),
            oracle_rate_r2=("oracle_rate_r2", "mean"),
            pred_rate_r2=("pred_rate_r2", "mean"),
            pred_rate_rmse=("pred_rate_rmse", "mean"),
            pred_rate_cos=("pred_rate_cos", "mean"),
        )
    )
    summary["two_level_score"] = (
        0.30 * np.maximum(summary["pred_rate_r2"], 0)
        + 0.25 * np.maximum(summary["oracle_rate_r2"], 0)
        + 0.20 * summary["semantic_acc"]
        - 0.15 * summary["semantic_logloss"]
        + 0.10 * summary["pred_rate_cos"]
    )
    summary = summary.sort_values("two_level_score", ascending=False).reset_index(drop=True)
    summary.to_csv(OUT / "two_level_proto_jepa_summary.csv", index=False)

    direct = summary[summary["mode"].eq("direct_semantic")][
        ["context_variant", "semantic_family", "semantic_k", "semantic_logloss", "semantic_acc", "pred_rate_r2"]
    ].rename(columns={
        "semantic_logloss": "direct_logloss",
        "semantic_acc": "direct_acc",
        "pred_rate_r2": "direct_pred_rate_r2",
    })
    aug = summary[~summary["mode"].eq("direct_semantic")].merge(
        direct,
        on=["context_variant", "semantic_family", "semantic_k"],
        how="left",
    )
    aug["delta_logloss_vs_direct"] = aug["semantic_logloss"] - aug["direct_logloss"]
    aug["delta_pred_rate_r2_vs_direct"] = aug["pred_rate_r2"] - aug["direct_pred_rate_r2"]
    aug = aug.sort_values(["delta_pred_rate_r2_vs_direct", "two_level_score"], ascending=[False, False])
    aug.to_csv(OUT / "two_level_proto_jepa_vs_direct.csv", index=False)

    report = [
        "# Two-Level Prototype JEPA Audit",
        "",
        "This tests the atlas hypothesis: a predictable coarse raw routine code should help predict a semantic target code.",
        "",
        "## Best Overall",
        "",
        summary.head(30).to_csv(index=False),
        "",
        "## Best Improvements Over Direct Semantic Prediction",
        "",
        aug.head(30).to_csv(index=False),
        "",
        "## Files",
        "",
        "- `two_level_proto_jepa_folds.csv`",
        "- `two_level_proto_jepa_summary.csv`",
        "- `two_level_proto_jepa_vs_direct.csv`",
    ]
    (OUT / "two_level_proto_jepa_report.md").write_text("\n".join(report), encoding="utf-8")
    print("TWO LEVEL TOP")
    print(summary.head(30).to_string(index=False), flush=True)
    print("\nVS DIRECT")
    print(aug.head(30).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
