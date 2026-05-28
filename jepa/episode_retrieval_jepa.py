from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
STAGE2_PUBLIC = 0.5779449757

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def block_sid(rows: pd.DataFrame, block: np.ndarray) -> str:
    return str(rows.iloc[int(block[0])]["subject_id"])


def block_label_stats(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[block]
    rates = np.nanmean(vals, axis=0)
    rates = np.nan_to_num(rates, nan=0.5)
    ent = -(rates * np.log(adv.clip(rates)) + (1.0 - rates) * np.log(adv.clip(1.0 - rates)))
    first = vals[0]
    last = vals[-1]
    change = last - first
    return np.r_[rates, ent, first, last, change].astype(np.float32)


def standardize_train_query(train_desc: np.ndarray, query_desc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(np.nan_to_num(train_desc, nan=0.0, posinf=0.0, neginf=0.0))
    qu = scaler.transform(np.nan_to_num(query_desc, nan=0.0, posinf=0.0, neginf=0.0))
    return tr.astype(np.float32), qu.astype(np.float32)


def knn_label_latent(
    train_desc: np.ndarray,
    query_desc: np.ndarray,
    label_latent: np.ndarray,
    train_sids: list[str],
    query_sids: list[str],
    k: int,
    same_subject_boost: float = 0.15,
) -> tuple[np.ndarray, np.ndarray]:
    tr, qu = standardize_train_query(train_desc, query_desc)
    out = np.zeros((len(qu), label_latent.shape[1]), dtype=np.float32)
    meta = np.zeros((len(qu), 6), dtype=np.float32)
    train_sids_arr = np.asarray(train_sids)
    for i, q in enumerate(qu):
        dist = np.sqrt(((tr - q[None, :]) ** 2).mean(axis=1))
        same = train_sids_arr == query_sids[i]
        adjusted = dist - same_subject_boost * same.astype(float)
        order = np.argsort(adjusted)[: min(k, len(adjusted))]
        raw_d = dist[order]
        tau = float(np.median(raw_d) + 1e-6)
        weights = np.exp(-raw_d / max(tau, 1e-6))
        weights = weights / max(float(weights.sum()), 1e-12)
        out[i] = np.average(label_latent[order], axis=0, weights=weights).astype(np.float32)
        meta[i] = np.array(
            [
                raw_d[0],
                raw_d.mean(),
                raw_d.std() if len(raw_d) > 1 else 0.0,
                float(same[order].mean()),
                float(np.max(weights)),
                float(-(weights * np.log(np.clip(weights, 1e-8, 1.0))).sum()),
            ],
            dtype=np.float32,
        )
    return out, meta


def assign_episode_features(
    store: dict[str, np.ndarray],
    n_rows: int,
    prefix: str,
    row_indices: list[np.ndarray],
    donor_latent: np.ndarray,
    meta: np.ndarray,
    actual_pred_gap: np.ndarray | None = None,
) -> None:
    columns = [f"{prefix}_pos", f"{prefix}_len"]
    for target in TARGETS:
        for stat in ["rate", "entropy", "first", "last", "change"]:
            columns.append(f"{prefix}_{stat}_{target}")
    columns.extend(f"{prefix}_{name}" for name in ["dmin", "dmean", "dstd", "same_frac", "wmax", "went"])
    if actual_pred_gap is not None:
        columns.append(f"{prefix}_actual_pred_gap")

    data: dict[str, np.ndarray] = {}
    for col in columns:
        if col not in store:
            store[col] = np.full(n_rows, np.nan, dtype=np.float32)
        data[col] = store[col]

    for block_i, idxs in enumerate(row_indices):
        idxs = np.asarray(idxs, dtype=int)
        rel = np.linspace(0.0, 1.0, len(idxs)) if len(idxs) > 1 else np.zeros(len(idxs))
        for local, row_i in enumerate(idxs):
            data[f"{prefix}_pos"][row_i] = rel[local]
            data[f"{prefix}_len"][row_i] = len(idxs)
            for j, target in enumerate(TARGETS):
                data[f"{prefix}_rate_{target}"][row_i] = donor_latent[block_i, j]
                data[f"{prefix}_entropy_{target}"][row_i] = donor_latent[block_i, 7 + j]
                data[f"{prefix}_first_{target}"][row_i] = donor_latent[block_i, 14 + j]
                data[f"{prefix}_last_{target}"][row_i] = donor_latent[block_i, 21 + j]
                data[f"{prefix}_change_{target}"][row_i] = donor_latent[block_i, 28 + j]
            for k, name in enumerate(["dmin", "dmean", "dstd", "same_frac", "wmax", "went"]):
                data[f"{prefix}_{name}"][row_i] = meta[block_i, k]
            if actual_pred_gap is not None:
                data[f"{prefix}_actual_pred_gap"][row_i] = actual_pred_gap[block_i]


def build_features_for_blocks(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    train_indices: np.ndarray,
    pred_blocks: list[np.ndarray],
    lengths: dict[str, list[int]],
    alpha: float,
) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    known = adv.known_mask_for_train(rows, train_indices)
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=240)
    if not train_blocks or not pred_blocks:
        return {}
    train_desc = np.vstack([bcj.summarize_z(z, b) for b in train_blocks])
    train_labels = np.vstack([block_label_stats(y, b) for b in train_blocks])
    train_sids = [block_sid(rows, b) for b in train_blocks]
    query_sids = [block_sid(rows, b) for b in pred_blocks]
    actual_desc = np.vstack([bcj.summarize_z(z, b) for b in pred_blocks])
    pred_desc = bcj.predict_block_summary(rows, z, y, base_all, train_indices, pred_blocks, lengths, alpha=alpha)
    mix_desc = 0.5 * actual_desc + 0.5 * pred_desc
    actual_pred_gap = np.sqrt(((actual_desc - pred_desc) ** 2).mean(axis=1))

    outputs: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for query_name, query_desc in [("actual", actual_desc), ("pred", pred_desc), ("mix", mix_desc)]:
        for k in [5, 15, 40]:
            donor, meta = knn_label_latent(train_desc, query_desc, train_labels, train_sids, query_sids, k=k)
            outputs[f"{query_name}_k{k}"] = (donor, meta, actual_pred_gap)
    return outputs


def build_episode_retrieval_features(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    repeats: int = 14,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    lengths = adv.actual_lengths_by_subject(rows)
    train_feat = train[SUB_KEY + TARGETS].copy()
    sub_feat = sub[SUB_KEY].copy()
    for alpha in [20.0, 80.0]:
        alpha_label = str(alpha).replace(".", "p")
        train_block_feature_data: dict[str, np.ndarray] = {}
        cover = np.zeros(len(train), dtype=int)
        for _fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=282400 + int(alpha))):
            val_blocks = adv.contiguous_val_blocks(rows, val_idx)
            if not val_blocks:
                continue
            features = build_features_for_blocks(rows, z, y, base_all, tr_idx, val_blocks, lengths, alpha)
            row_indices = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
            for name, (donor, meta, gap) in features.items():
                assign_episode_features(train_block_feature_data, len(train), f"er_a{alpha_label}_{name}", row_indices, donor, meta, gap)
            for idxs in row_indices:
                cover[idxs] += 1
            print(f"episode-retrieval alpha={alpha:g} {fold}: val_blocks={len(val_blocks)} covered={int((cover > 0).sum())}", flush=True)
        train_block_feature = pd.DataFrame(train_block_feature_data, index=np.arange(len(train)))
        train_feat = pd.concat([train_feat, train_block_feature], axis=1)

        sub_blocks = adv.submission_blocks(train, sub, rows)
        sub_features = build_features_for_blocks(rows, z, y, base_all, np.arange(len(train)), sub_blocks, lengths, alpha)
        sub_block_feature_data: dict[str, np.ndarray] = {}
        sub_row_indices = [rows.iloc[b]["sub_idx"].to_numpy(dtype=int) for b in sub_blocks]
        for name, (donor, meta, gap) in sub_features.items():
            assign_episode_features(sub_block_feature_data, len(sub), f"er_a{alpha_label}_{name}", sub_row_indices, donor, meta, gap)
        sub_block_feature = pd.DataFrame(sub_block_feature_data, index=np.arange(len(sub)))
        sub_feat = pd.concat([sub_feat, sub_block_feature], axis=1)
    return train_feat.copy(), sub_feat.copy()


def axis_stats(file_name: str) -> dict[str, float]:
    try:
        base_sub = pd.read_csv(adv.BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        cand = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        base_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
        move = adv.logit(cand[TARGETS].to_numpy(dtype=float)) - base_logit
        bad_parts = []
        weights = []
        for bad_name, score in [
            ("submission_jepa_latent_residual_probe.csv", 0.5812273278),
            ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862),
        ]:
            bad = pd.read_csv(OUT / bad_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
            bad_parts.append(adv.logit(bad[TARGETS].to_numpy(dtype=float)) - base_logit)
            weights.append(max(score - STAGE2_PUBLIC, 1e-9))
        bad_axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(weights))
        good = pd.read_csv(OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        good_axis = adv.logit(good[TARGETS].to_numpy(dtype=float)) - base_logit
        out = {}
        for prefix, axis in [("jepa_bad", bad_axis), ("raw_good", good_axis)]:
            m = move.reshape(-1)
            a = axis.reshape(-1)
            out[f"{prefix}_ratio"] = float(np.dot(m, a) / max(float(np.dot(a, a)), 1e-12))
            out[f"{prefix}_cos"] = float(np.dot(m, a) / max(float(np.linalg.norm(m) * np.linalg.norm(a)), 1e-12))
        return out
    except Exception:
        return {"jepa_bad_ratio": np.nan, "jepa_bad_cos": np.nan, "raw_good_ratio": np.nan, "raw_good_cos": np.nan}


def scan_and_submit(train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cols = broad.finite_numeric_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, TARGETS, top_n=55)
    pre.to_csv(OUT / "episode_retrieval_jepa_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = broad.loss_col(y[:, j], base[:, j])
        for c_value in [0.02, 0.05, 0.10, 0.20]:
            corrected = broad.oof_corrected(train_feat, base, target, feature, mode, c_value)
            losses = [broad.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": broad.loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_feat, y, base, corrected, j))
            else:
                row.update({"mean_delta": 0.0, "median_delta": 0.0, "p25_delta": 0.0, "p75_delta": 0.0, "win_rate": 0.0, "mean_selected_weight": 0.0, "zero_weight_rate": 1.0})
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.00035 and row["mean_delta"] <= -0.00005 and row["win_rate"] >= 0.62)
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.56)
            rows.append(row)
    scan = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    scan.to_csv(OUT / "episode_retrieval_jepa_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, file_name: str, scale: float) -> tuple[np.ndarray, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
        used = []
        for op in ops.itertuples(index=False):
            target = str(op.target)
            if target in {u["target"] for u in used}:
                continue
            j = TARGETS.index(target)
            w = float(op.best_weight) * scale
            corrected = broad.oof_corrected(train_feat, pred, target, str(op.feature), str(op.mode), float(op.c_value))
            pred[:, j] = adv.clip((1.0 - w) * pred[:, j] + w * corrected)
            sub_corr = broad.fit_corrected(train_feat, sub_feat, pred, sub_pred, target, str(op.feature), str(op.mode), float(op.c_value))
            sub_pred[:, j] = adv.clip((1.0 - w) * sub_pred[:, j] + w * sub_corr)
            used.append({"target": target, "feature": str(op.feature), "mode": str(op.mode), "c_value": float(op.c_value), "base_weight": float(op.best_weight), "scaled_weight": w, "delta_vs_base": float(op.delta_vs_base), "mean_delta": float(op.mean_delta), "win_rate": float(op.win_rate)})
        out = base_sub.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / file_name, index=False)
        pd.DataFrame(used).to_csv(OUT / file_name.replace("submission_", "").replace(".csv", "_ops.csv"), index=False)
        return pred, pd.DataFrame(used)

    strict = scan[(scan["passes_strict"]) & (scan["best_weight"] > 0)].sort_values("delta_vs_base")
    no_q2 = strict[~strict["target"].eq("Q2")]
    top = scan[scan["best_weight"] > 0].sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    specs = []
    for label, ops in [("strict", strict), ("strict_noq2", no_q2), ("top_probe", top)]:
        for scale in [0.35, 0.5, 0.75, 1.0]:
            specs.append((label, ops, scale))
    summary_rows = []
    base_loss = adv.mean_loss(y, base)
    for label, ops, scale in specs:
        scale_label = str(scale).replace(".", "p")
        file_name = f"submission_episode_retrieval_jepa_{label}_scale{scale_label}.csv"
        pred, used = apply_ops(ops, file_name, scale)
        mloss = adv.mean_loss(y, pred)
        summary_rows.append({"candidate": file_name, "class": label, "scale": scale, "ops": int(len(used)), "oof_loss": mloss, "oof_delta_vs_stage2": mloss - base_loss, **axis_stats(file_name)})
    summary = pd.DataFrame(summary_rows).sort_values(["jepa_bad_ratio", "oof_delta_vs_stage2"])
    summary.to_csv(OUT / "episode_retrieval_jepa_candidate_summary.csv", index=False)
    return scan, summary


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, names = bcj.build_day_latent(rows, canvas)
    pd.DataFrame({"latent": names}).to_csv(OUT / "episode_retrieval_jepa_latent_meta.csv", index=False)
    train_feat, sub_feat = build_episode_retrieval_features(train, sub, rows, z, y, base_all)
    train_feat.to_parquet(OUT / "episode_retrieval_jepa_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / "episode_retrieval_jepa_submission_features.parquet", index=False)
    scan, summary = scan_and_submit(train_feat, sub_feat, base, base_sub)
    report = [
        "# Episode Retrieval JEPA",
        "",
        "Hidden block is treated as an episode. The target encoder is the actual raw block canvas latent; the context encoder predicts expected block latent. Both are used to retrieve similar labeled train episodes, and the donor label distribution becomes a residual feature.",
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(60).to_csv(index=False),
    ]
    (OUT / "episode_retrieval_jepa_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
