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
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402


LATENT_BUDGET = 16
PROTO_K = 10


def slope_of(mat: np.ndarray) -> np.ndarray:
    if len(mat) <= 1:
        return np.zeros(mat.shape[1], dtype=np.float32)
    x = np.linspace(-0.5, 0.5, len(mat), dtype=np.float32)
    denom = float(np.sum(x * x))
    return ((x[:, None] * mat).sum(axis=0) / max(denom, 1e-9)).astype(np.float32)


def block_label_state(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[block]
    rates = np.nanmean(vals, axis=0)
    rates = np.nan_to_num(rates, nan=0.5)
    ent = -(rates * np.log(adv.clip(rates)) + (1.0 - rates) * np.log(adv.clip(1.0 - rates)))
    first = vals[0]
    last = vals[-1]
    change = last - first
    return np.r_[rates, ent, first, last, change].astype(np.float32)


def block_context_parts(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    block_pos: np.ndarray,
    known_label_mask: np.ndarray,
) -> dict[str, np.ndarray]:
    block_pos = np.asarray(block_pos, dtype=int)
    sid = str(rows.iloc[int(block_pos[0])]["subject_id"])
    subject_idx = rows["subject_id"].astype(str).eq(sid).to_numpy()
    subject_pos = np.where(subject_idx)[0]
    block_set = set(int(p) for p in block_pos)
    known_subject = np.array([p for p in subject_pos if known_label_mask[p] and p not in block_set], dtype=int)
    before = known_subject[known_subject < block_pos.min()]
    after = known_subject[known_subject > block_pos.max()]
    before_tail = before[-14:]
    after_head = after[:14]

    def summarize_ctx(indices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if len(indices) == 0:
            return (
                np.zeros(z.shape[1], dtype=np.float32),
                np.zeros(z.shape[1], dtype=np.float32),
                np.zeros(z.shape[1], dtype=np.float32),
            )
        vals = z[indices]
        return vals.mean(axis=0).astype(np.float32), vals.std(axis=0).astype(np.float32), slope_of(vals)

    def summarize_label(indices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if len(indices) == 0:
            return (
                np.full(len(TARGETS), 0.5, dtype=np.float32),
                np.zeros(len(TARGETS), dtype=np.float32),
                np.full(len(TARGETS), 0.5, dtype=np.float32),
                np.zeros(len(TARGETS), dtype=np.float32),
            )
        vals = y[indices]
        return (
            np.nanmean(vals, axis=0).astype(np.float32),
            np.isfinite(vals).mean(axis=0).astype(np.float32),
            base_all[indices].mean(axis=0).astype(np.float32),
            base_all[indices].std(axis=0).astype(np.float32),
        )

    meta = np.array(
        [
            len(block_pos),
            rows.iloc[block_pos]["subject_phase"].mean(),
            rows.iloc[block_pos]["is_weekend"].mean(),
            rows.iloc[block_pos]["dow"].mean() / 6.0,
            float(block_pos.min() - subject_pos.min()) / max(len(subject_pos), 1),
            float(subject_pos.max() - block_pos.max()) / max(len(subject_pos), 1),
            float(block_pos.min() - before_tail[-1]) if len(before_tail) else 99.0,
            float(after_head[0] - block_pos.max()) if len(after_head) else 99.0,
        ],
        dtype=np.float32,
    )
    bb_mean, bb_std, bb_slope = summarize_ctx(before_tail)
    aa_mean, aa_std, aa_slope = summarize_ctx(after_head)
    kk_mean, kk_std, kk_slope = summarize_ctx(known_subject)
    lbl_b_mean, lbl_b_cov, lbl_b_base, lbl_b_std = summarize_label(before_tail)
    lbl_a_mean, lbl_a_cov, lbl_a_base, lbl_a_std = summarize_label(after_head)
    lbl_k_mean, lbl_k_cov, lbl_k_base, lbl_k_std = summarize_label(known_subject)
    block_visible = np.r_[
        base_all[block_pos].mean(axis=0),
        base_all[block_pos].std(axis=0),
        z[block_pos].mean(axis=0),
        z[block_pos].std(axis=0),
    ].astype(np.float32)

    return {
        "meta": meta,
        "before_after_z": np.r_[bb_mean, bb_std, bb_slope, aa_mean, aa_std, aa_slope].astype(np.float32),
        "known_z": np.r_[kk_mean, kk_std, kk_slope].astype(np.float32),
        "before_after_label": np.r_[lbl_b_mean, lbl_b_cov, lbl_b_base, lbl_b_std, lbl_a_mean, lbl_a_cov, lbl_a_base, lbl_a_std].astype(np.float32),
        "known_label": np.r_[lbl_k_mean, lbl_k_cov, lbl_k_base, lbl_k_std].astype(np.float32),
        "visible_target": block_visible,
    }


def build_context_variant(parts: dict[str, np.ndarray], name: str) -> np.ndarray:
    if name == "current_visible_target":
        blocks = ["meta", "before_after_z", "known_z", "before_after_label", "known_label", "visible_target"]
    elif name == "strict_surround":
        blocks = ["meta", "before_after_z", "known_z", "before_after_label", "known_label"]
    elif name == "strict_rawonly":
        blocks = ["meta", "before_after_z", "known_z"]
    elif name == "strict_labelonly":
        blocks = ["meta", "before_after_label", "known_label"]
    elif name == "strict_prior":
        blocks = ["meta", "known_z", "known_label"]
    else:
        raise ValueError(name)
    return np.concatenate([parts[b] for b in blocks]).astype(np.float32)


def fit_transform_target(train_mat: np.ndarray, val_mat: np.ndarray, budget: int) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(np.nan_to_num(train_mat, nan=0.0, posinf=0.0, neginf=0.0))
    va = scaler.transform(np.nan_to_num(val_mat, nan=0.0, posinf=0.0, neginf=0.0))
    k = min(budget, tr.shape[0] - 1, tr.shape[1])
    if k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=297001)
        tr = pca.fit_transform(tr)
        va = pca.transform(va)
    return tr.astype(np.float32), va.astype(np.float32)


def fit_predict(train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, alpha: float = 25.0) -> np.ndarray:
    scaler = StandardScaler()
    tr = scaler.fit_transform(np.nan_to_num(train_x, nan=0.0, posinf=0.0, neginf=0.0))
    va = scaler.transform(np.nan_to_num(val_x, nan=0.0, posinf=0.0, neginf=0.0))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(tr, train_y)
    return model.predict(va).astype(np.float32)


def repr_metrics(true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    sse = float(np.sum((true - pred) ** 2))
    mean = true.mean(axis=0, keepdims=True)
    sst = float(np.sum((true - mean) ** 2))
    r2 = 1.0 - sse / max(sst, 1e-12)
    denom = np.linalg.norm(true, axis=1) * np.linalg.norm(pred, axis=1)
    cos = np.mean(np.sum(true * pred, axis=1) / np.maximum(denom, 1e-12))
    rmse = float(np.sqrt(np.mean((true - pred) ** 2)))
    return {"r2": r2, "cos": float(cos), "rmse": rmse}


def make_proto_assignments(train_z: np.ndarray, all_z: np.ndarray) -> np.ndarray:
    model = MiniBatchKMeans(n_clusters=PROTO_K, random_state=297123, batch_size=256, n_init=10)
    model.fit(train_z)
    return model.predict(all_z).astype(np.int32)


def proto_hist(tokens: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = tokens[np.asarray(block, dtype=int)]
    hist = np.bincount(vals, minlength=PROTO_K).astype(np.float32)
    return hist / max(float(hist.sum()), 1.0)


def proto_trans(tokens: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = tokens[np.asarray(block, dtype=int)]
    mat = np.zeros((PROTO_K, PROTO_K), dtype=np.float32)
    if len(vals) > 1:
        for a, b in zip(vals[:-1], vals[1:]):
            mat[int(a), int(b)] += 1.0
        mat /= max(float(mat.sum()), 1.0)
    return mat.reshape(-1)


def window_state(z: np.ndarray, block: np.ndarray) -> np.ndarray:
    # Layout from block_canvas_jepa.build_day_latent:
    # full 32, mobile 18, wear 14, 4 windows * 10 = 40
    win = z[np.asarray(block, dtype=int)][:, 64:104]
    return np.r_[win.mean(axis=0), win.std(axis=0), slope_of(win)].astype(np.float32)


def modality_state(z: np.ndarray, block: np.ndarray) -> np.ndarray:
    mat = z[np.asarray(block, dtype=int)]
    mobile = mat[:, 32:50]
    wear = mat[:, 50:64]
    mobile_mean = mobile.mean(axis=0)
    wear_mean = wear.mean(axis=0)
    diff = mobile_mean[:14] - wear_mean
    return np.r_[mobile_mean, wear_mean, diff].astype(np.float32)


def mean_latent(z: np.ndarray, block: np.ndarray) -> np.ndarray:
    return z[np.asarray(block, dtype=int)].mean(axis=0).astype(np.float32)


def collect_raw_targets(name: str, z: np.ndarray, y: np.ndarray, blocks: list[np.ndarray], tokens: np.ndarray) -> np.ndarray:
    if name == "mean_latent":
        return np.vstack([mean_latent(z, b) for b in blocks]).astype(np.float32)
    if name == "window_state":
        return np.vstack([window_state(z, b) for b in blocks]).astype(np.float32)
    if name == "modality_state":
        return np.vstack([modality_state(z, b) for b in blocks]).astype(np.float32)
    if name == "proto_hist":
        return np.vstack([proto_hist(tokens, b) for b in blocks]).astype(np.float32)
    if name == "proto_trans":
        return np.vstack([proto_trans(tokens, b) for b in blocks]).astype(np.float32)
    if name == "label_state":
        return np.vstack([block_label_state(y, b) for b in blocks]).astype(np.float32)
    raise ValueError(name)


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)
    lengths = adv.actual_lengths_by_subject(rows)

    context_variants = ["current_visible_target", "strict_surround", "strict_rawonly", "strict_labelonly", "strict_prior"]
    repr_names = ["mean_latent", "window_state", "modality_state", "proto_hist", "proto_trans", "label_state"]

    rows_out = []
    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=4, seed=297000)):
        known = adv.known_mask_for_train(rows, tr_idx)
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=160)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not train_blocks or not val_blocks:
            continue
        train_visible_rows = np.where(known)[0]
        tokens = make_proto_assignments(z[train_visible_rows], z)

        train_parts = [block_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
        val_parts = [block_context_parts(rows, z, y, base_all, b, known) for b in val_blocks]
        train_label = np.vstack([block_label_state(y, b) for b in train_blocks]).astype(np.float32)
        val_label = np.vstack([block_label_state(y, b) for b in val_blocks]).astype(np.float32)

        print(f"jepa-ready {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)
        for repr_name in repr_names:
            train_raw = collect_raw_targets(repr_name, z, y, train_blocks, tokens)
            val_raw = collect_raw_targets(repr_name, z, y, val_blocks, tokens)
            train_repr, val_repr = fit_transform_target(train_raw, val_raw, LATENT_BUDGET)
            # Label recoverability from true representation: representation richness audit.
            label_true_pred = fit_predict(train_repr, train_label, val_repr, alpha=15.0)
            label_true_stats = repr_metrics(val_label[:, :7], label_true_pred[:, :7])
            for ctx_name in context_variants:
                train_ctx = np.vstack([build_context_variant(p, ctx_name) for p in train_parts]).astype(np.float32)
                val_ctx = np.vstack([build_context_variant(p, ctx_name) for p in val_parts]).astype(np.float32)
                val_repr_pred = fit_predict(train_ctx, train_repr, val_ctx, alpha=25.0)
                repr_stats = repr_metrics(val_repr, val_repr_pred)
                label_pred = fit_predict(train_repr, train_label, val_repr_pred, alpha=15.0)
                rate_stats = repr_metrics(val_label[:, :7], label_pred[:, :7])
                full_label_stats = repr_metrics(val_label, label_pred)
                rows_out.append(
                    {
                        "fold": fold,
                        "representation": repr_name,
                        "context_variant": ctx_name,
                        "train_blocks": len(train_blocks),
                        "val_blocks": len(val_blocks),
                        "repr_r2": repr_stats["r2"],
                        "repr_cos": repr_stats["cos"],
                        "repr_rmse": repr_stats["rmse"],
                        "rate_chain_r2": rate_stats["r2"],
                        "rate_chain_cos": rate_stats["cos"],
                        "rate_chain_rmse": rate_stats["rmse"],
                        "label_chain_r2": full_label_stats["r2"],
                        "label_chain_cos": full_label_stats["cos"],
                        "repr_to_true_rate_r2": label_true_stats["r2"],
                        "repr_to_true_rate_cos": label_true_stats["cos"],
                    }
                )

    fold_df = pd.DataFrame(rows_out)
    fold_df.to_csv(OUT / "jepa_ready_data_audit_folds.csv", index=False)
    summary = (
        fold_df.groupby(["representation", "context_variant"], as_index=False)
        .agg(
            repr_r2=("repr_r2", "mean"),
            repr_cos=("repr_cos", "mean"),
            rate_chain_r2=("rate_chain_r2", "mean"),
            rate_chain_cos=("rate_chain_cos", "mean"),
            label_chain_r2=("label_chain_r2", "mean"),
            repr_to_true_rate_r2=("repr_to_true_rate_r2", "mean"),
            repr_to_true_rate_cos=("repr_to_true_rate_cos", "mean"),
        )
    )
    summary["strict_rank_score"] = 0.55 * summary["rate_chain_r2"] + 0.25 * summary["repr_r2"] + 0.20 * summary["repr_to_true_rate_r2"]
    summary = summary.sort_values(["context_variant", "strict_rank_score"], ascending=[True, False]).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_ready_data_audit_summary.csv", index=False)

    pivot = summary.pivot(index="representation", columns="context_variant", values="rate_chain_r2")
    gap_rows = []
    for repr_name in pivot.index:
        current = float(pivot.loc[repr_name].get("current_visible_target", np.nan))
        strict = float(pivot.loc[repr_name].get("strict_surround", np.nan))
        rawonly = float(pivot.loc[repr_name].get("strict_rawonly", np.nan))
        labelonly = float(pivot.loc[repr_name].get("strict_labelonly", np.nan))
        prior = float(pivot.loc[repr_name].get("strict_prior", np.nan))
        gap_rows.append(
            {
                "representation": repr_name,
                "current_visible_target_rate_chain_r2": current,
                "strict_surround_rate_chain_r2": strict,
                "strict_gap": current - strict,
                "strict_rawonly_rate_chain_r2": rawonly,
                "strict_labelonly_rate_chain_r2": labelonly,
                "strict_prior_rate_chain_r2": prior,
            }
        )
    gap = pd.DataFrame(gap_rows).sort_values("strict_surround_rate_chain_r2", ascending=False)
    gap.to_csv(OUT / "jepa_ready_data_audit_gap.csv", index=False)

    report = [
        "# JEPA Ready Data Audit",
        "",
        "This audit asks a stricter question than earlier JEPA-style experiments: if the hidden block itself is not visible, which data representation is still predictable from surrounding context, and does that predicted representation preserve label information?",
        "",
        "## Interpretation Rule",
        "",
        "- `current_visible_target`: partly-JEPA, because target-block raw/base information is visible.",
        "- `strict_surround`: closer to JEPA, because only surrounding context and position are visible.",
        "- `strict_rawonly`: only surrounding sensor-state latent.",
        "- `strict_labelonly`: only surrounding label/base statistics.",
        "- `strict_prior`: subject routine prior only.",
        "",
        "## Best Representations Under Strict Surround",
        "",
        summary[summary["context_variant"].eq("strict_surround")].head(20).to_csv(index=False),
        "",
        "## Visibility Gap",
        "",
        gap.to_csv(index=False),
        "",
        "## Recommendations",
        "",
        "1. If `strict_gap` is large, that representation is not a true JEPA target here; it depends on target-block-visible raw signal.",
        "2. If `strict_surround_rate_chain_r2` stays strong, the representation is JEPA-ready and should be the next target latent.",
        "3. If `strict_prior` is also strong, the data is better cast as subject routine tokens/prototypes rather than a raw hidden canvas.",
        "",
        "## Files",
        "",
        "- `jepa_ready_data_audit_folds.csv`",
        "- `jepa_ready_data_audit_summary.csv`",
        "- `jepa_ready_data_audit_gap.csv`",
    ]
    (OUT / "jepa_ready_data_audit_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary[summary["context_variant"].eq("strict_surround")].head(20).to_string(index=False), flush=True)
    print("\nvisibility gap")
    print(gap.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
