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


CONFIGS = [
    ("submission_like", "label_rate", 10, "past_label"),
    ("submission_like", "label_rate", 8, "past_label"),
    ("submission_like", "label_rate", 10, "prior_label"),
    ("submission_like", "raw_mean", 8, "prior_label"),
    ("submission_like", "teacher_hybrid", 10, "past_label"),
    ("fixed_2", "label_rate", 10, "prior_label"),
    ("fixed_4", "label_rate", 10, "prior_label"),
    ("fixed_6", "label_state", 8, "prior_label"),
]


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def transform(train_x: np.ndarray, val_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    va = scaler.transform(finite(val_x))
    k = min(24, tr.shape[0] - 1, tr.shape[1])
    if 1 < k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=300101)
        tr = pca.fit_transform(tr)
        va = pca.transform(va)
    return tr.astype(np.float32), va.astype(np.float32)


def fit_prob(train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, k: int) -> np.ndarray | None:
    if np.unique(train_y).size < 2:
        return None
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    va = scaler.transform(finite(val_x))
    clf = LogisticRegression(C=0.75, max_iter=900, solver="lbfgs", random_state=300201)
    clf.fit(tr, train_y)
    raw = clf.predict_proba(va).astype(np.float32)
    prob = np.full((len(val_x), k), 1e-6, dtype=np.float32)
    for col_i, cls in enumerate(clf.classes_):
        prob[:, int(cls)] = raw[:, col_i]
    return prob / prob.sum(axis=1, keepdims=True)


def blocks_for_mode(
    mode: str,
    rows: pd.DataFrame,
    y: np.ndarray,
    tr_idx: np.ndarray,
    val_idx: np.ndarray,
    lengths: dict[str, list[int]],
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    if mode == "submission_like":
        return adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=160), adv.contiguous_val_blocks(rows, val_idx)
    length = int(mode.split("_")[1])
    return (
        atlas.fixed_blocks(rows, y, tr_idx, length, max_blocks_per_subject=120),
        atlas.fixed_blocks(rows, y, val_idx, length, max_blocks_per_subject=80),
    )


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = finite(y_true).reshape(-1)
    y_pred = finite(y_pred).reshape(-1)
    sse = float(np.sum((y_true - y_pred) ** 2))
    sst = float(np.sum((y_true - y_true.mean()) ** 2))
    return 1.0 - sse / max(sst, 1e-12)


def corr_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = finite(y_true).reshape(-1)
    b = finite(y_pred).reshape(-1)
    if np.std(a) < 1e-8 or np.std(b) < 1e-8:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)
    lengths = adv.actual_lengths_by_subject(rows)

    pred_rows = []
    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=4, seed=300000)):
        known = adv.known_mask_for_train(rows, tr_idx)
        for block_mode, family, k, ctx in CONFIGS:
            train_blocks, val_blocks = blocks_for_mode(block_mode, rows, y, tr_idx, val_idx, lengths)
            if len(train_blocks) <= k * 4 or len(val_blocks) < 6:
                continue
            train_target = atlas.build_target_matrix(family, rows, z, canvas, y, train_blocks)
            val_target = atlas.build_target_matrix(family, rows, z, canvas, y, val_blocks)
            train_feat, val_feat = transform(train_target, val_target)
            km = MiniBatchKMeans(n_clusters=k, random_state=300301 + k, batch_size=256, n_init=10)
            train_proto = km.fit_predict(train_feat).astype(int)
            val_proto = km.predict(val_feat).astype(int)
            if np.bincount(train_proto, minlength=k).min() < 2:
                continue
            train_rate = np.vstack([atlas.label_rate(y, b) for b in train_blocks]).astype(np.float32)
            val_rate = np.vstack([atlas.label_rate(y, b) for b in val_blocks]).astype(np.float32)
            proto_rate = np.zeros((k, len(TARGETS)), dtype=np.float32)
            fallback = train_rate.mean(axis=0)
            for cid in range(k):
                mask = train_proto == cid
                proto_rate[cid] = train_rate[mask].mean(axis=0) if mask.any() else fallback
            train_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
            val_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in val_blocks]
            train_ctx = np.vstack([atlas.build_context(p, ctx) for p in train_parts]).astype(np.float32)
            val_ctx = np.vstack([atlas.build_context(p, ctx) for p in val_parts]).astype(np.float32)
            prob = fit_prob(train_ctx, train_proto, val_ctx, k)
            if prob is None:
                continue
            pred_rate = prob @ proto_rate
            oracle_rate = proto_rate[val_proto]
            for row_i in range(len(val_blocks)):
                for j, target in enumerate(TARGETS):
                    pred_rows.append(
                        {
                            "fold": fold,
                            "block_mode": block_mode,
                            "family": family,
                            "k": k,
                            "context_variant": ctx,
                            "target": target,
                            "true_rate": float(val_rate[row_i, j]),
                            "pred_rate": float(pred_rate[row_i, j]),
                            "oracle_rate": float(oracle_rate[row_i, j]),
                        }
                    )
            print(f"targetwise {fold} {block_mode} {family} k={k} ctx={ctx}", flush=True)

    rows_df = pd.DataFrame(pred_rows)
    rows_df.to_csv(OUT / "jepa_friendly_targetwise_rows.csv", index=False)
    summary_rows = []
    for keys, g in rows_df.groupby(["block_mode", "family", "k", "context_variant", "target"], sort=False):
        true = g["true_rate"].to_numpy(float)
        pred = g["pred_rate"].to_numpy(float)
        oracle = g["oracle_rate"].to_numpy(float)
        summary_rows.append(
            {
                "block_mode": keys[0],
                "family": keys[1],
                "k": keys[2],
                "context_variant": keys[3],
                "target": keys[4],
                "n": len(g),
                "pred_r2": r2_score(true, pred),
                "oracle_r2": r2_score(true, oracle),
                "pred_corr": corr_score(true, pred),
                "oracle_corr": corr_score(true, oracle),
                "pred_rmse": float(np.sqrt(np.mean((true - pred) ** 2))),
                "oracle_rmse": float(np.sqrt(np.mean((true - oracle) ** 2))),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["pred_r2", "oracle_r2"], ascending=False)
    summary.to_csv(OUT / "jepa_friendly_targetwise_summary.csv", index=False)
    pivot = summary.pivot_table(
        index=["block_mode", "family", "k", "context_variant"],
        columns="target",
        values="pred_r2",
        aggfunc="mean",
    ).reset_index()
    pivot["mean_pred_r2"] = pivot[TARGETS].mean(axis=1)
    pivot = pivot.sort_values("mean_pred_r2", ascending=False)
    pivot.to_csv(OUT / "jepa_friendly_targetwise_pivot.csv", index=False)

    report = [
        "# JEPA-Friendly Targetwise Probe",
        "",
        "Selected atlas candidates were rerun and evaluated per target.",
        "",
        "## Best Per-Target Rows",
        "",
        summary.head(40).to_csv(index=False),
        "",
        "## Candidate Pivot",
        "",
        pivot.to_csv(index=False),
        "",
        "## Files",
        "",
        "- `jepa_friendly_targetwise_rows.csv`",
        "- `jepa_friendly_targetwise_summary.csv`",
        "- `jepa_friendly_targetwise_pivot.csv`",
    ]
    (OUT / "jepa_friendly_targetwise_report.md").write_text("\n".join(report), encoding="utf-8")
    print("TARGETWISE TOP")
    print(summary.head(40).to_string(index=False), flush=True)
    print("\nPIVOT")
    print(pivot.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
