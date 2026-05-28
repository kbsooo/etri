from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

SEMANTIC_K = 10
ROUTINE_K = 8
CONTEXTS = ["past_label", "prior_label", "bidir_label", "prior_raw", "prior_all", "full_strict"]
TARGET_STAGE_WEIGHT = {"Q1": 1.0, "Q2": 1.0, "Q3": 1.0, "S1": 1.0, "S2": 1.35, "S3": 1.35, "S4": 1.0}
BLEND_GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])
MODES = ["global_z", "subject_center", "subject_z", "subject_rank", "missing"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import jepa_friendly_atlas as atlas  # noqa: E402


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def entropy_prob(prob: np.ndarray) -> np.ndarray:
    pp = np.clip(prob, 1e-9, 1.0)
    ent = -(pp * np.log(pp)).sum(axis=1)
    return ent / max(float(np.log(prob.shape[1])), 1e-12)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = adv.clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], p[:, j]) for j in range(len(TARGETS))]))


@dataclass
class Codebook:
    scaler: StandardScaler
    pca: PCA | None
    model: MiniBatchKMeans
    k: int


def fit_codebook(x: np.ndarray, k: int, seed: int, pca_budget: int = 24) -> tuple[Codebook, np.ndarray]:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite(x))
    pca = None
    if xs.shape[1] > pca_budget and xs.shape[0] > pca_budget + 2:
        pca = PCA(n_components=pca_budget, svd_solver="randomized", random_state=seed + 17)
        xs = pca.fit_transform(xs)
    km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=20, batch_size=256)
    proto = km.fit_predict(xs).astype(int)
    return Codebook(scaler=scaler, pca=pca, model=km, k=k), proto


def predict_codebook(codebook: Codebook, x: np.ndarray) -> np.ndarray:
    xs = codebook.scaler.transform(finite(x))
    if codebook.pca is not None:
        xs = codebook.pca.transform(xs)
    return codebook.model.predict(xs).astype(int)


def proto_rate_matrix(proto: np.ndarray, rates: np.ndarray, k: int) -> np.ndarray:
    global_rate = rates.mean(axis=0)
    out = np.zeros((k, rates.shape[1]), dtype=np.float32)
    for cid in range(k):
        mask = proto == cid
        out[cid] = rates[mask].mean(axis=0) if mask.any() else global_rate
    return np.clip(out, 1e-4, 1.0 - 1e-4)


def fit_proto_probs(
    train_ctx: np.ndarray,
    pred_ctx: np.ndarray,
    train_proto: np.ndarray,
    k: int,
    c_value: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    prior = np.bincount(train_proto, minlength=k).astype(np.float32)
    prior = (prior + 1e-3) / float(prior.sum() + 1e-3 * k)
    if np.unique(train_proto).size < 2:
        return np.tile(prior, (len(train_ctx), 1)), np.tile(prior, (len(pred_ctx), 1))
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_ctx))
    pr = scaler.transform(finite(pred_ctx))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=1200, random_state=seed)
    clf.fit(tr, train_proto)

    def mapped_prob(mat: np.ndarray) -> np.ndarray:
        raw = clf.predict_proba(mat).astype(np.float32)
        prob = np.full((mat.shape[0], k), 1e-6, dtype=np.float32)
        for col_i, cls in enumerate(clf.classes_):
            prob[:, int(cls)] = raw[:, col_i]
        return prob / prob.sum(axis=1, keepdims=True)

    return mapped_prob(tr), mapped_prob(pr)


def fit_ridge_rate(
    train_ctx: np.ndarray,
    pred_ctx: np.ndarray,
    train_sem_prob: np.ndarray,
    pred_sem_prob: np.ndarray,
    train_raw_prob: np.ndarray,
    pred_raw_prob: np.ndarray,
    train_rate: np.ndarray,
    alpha: float,
) -> np.ndarray:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_ctx))
    pr = scaler.transform(finite(pred_ctx))
    x_train = np.hstack([tr, train_sem_prob, train_raw_prob])
    x_pred = np.hstack([pr, pred_sem_prob, pred_raw_prob])
    model = Ridge(alpha=float(alpha), solver="svd")
    model.fit(x_train, train_rate)
    return adv.clip(model.predict(x_pred))


def block_label_rates(y: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    return np.vstack([atlas.label_rate(y, b) for b in blocks]).astype(np.float32)


def make_feature_dict(
    ctx: str,
    sem_prob: np.ndarray,
    raw_prob: np.ndarray,
    sem_rate: np.ndarray,
    raw_rate: np.ndarray,
    ridge_rate: np.ndarray,
    base_block: np.ndarray,
    base_row: np.ndarray,
) -> dict[str, float]:
    blend_rate = adv.clip(0.50 * sem_rate + 0.20 * raw_rate + 0.30 * ridge_rate)
    out: dict[str, float] = {
        f"segj_{ctx}_sem_entropy": float(entropy_prob(sem_prob[None, :])[0]),
        f"segj_{ctx}_sem_maxprob": float(np.max(sem_prob)),
        f"segj_{ctx}_raw_entropy": float(entropy_prob(raw_prob[None, :])[0]),
        f"segj_{ctx}_raw_maxprob": float(np.max(raw_prob)),
        f"segj_{ctx}_s23_blend_mean": float(0.5 * (blend_rate[TARGETS.index("S2")] + blend_rate[TARGETS.index("S3")])),
        f"segj_{ctx}_s3_minus_s2": float(blend_rate[TARGETS.index("S3")] - blend_rate[TARGETS.index("S2")]),
    }
    for cid, prob in enumerate(sem_prob):
        out[f"segj_{ctx}_semprob_{cid:02d}"] = float(prob)
    for cid, prob in enumerate(raw_prob):
        out[f"segj_{ctx}_rawprob_{cid:02d}"] = float(prob)
    for j, target in enumerate(TARGETS):
        out[f"segj_{ctx}_sem_{target}"] = float(sem_rate[j])
        out[f"segj_{ctx}_raw_{target}"] = float(raw_rate[j])
        out[f"segj_{ctx}_ridge_{target}"] = float(ridge_rate[j])
        out[f"segj_{ctx}_blend_{target}"] = float(blend_rate[j])
        out[f"segj_{ctx}_blend_minus_blockbase_{target}"] = float(blend_rate[j] - base_block[j])
        out[f"segj_{ctx}_blend_minus_rowbase_{target}"] = float(blend_rate[j] - base_row[j])
    return out


def expand_blocks_to_rows(
    rows: pd.DataFrame,
    base_all: np.ndarray,
    blocks: list[np.ndarray],
    context_outputs: dict[str, dict[str, np.ndarray]],
    row_index_name: str,
) -> pd.DataFrame:
    feature_rows: list[dict[str, float | int]] = []
    for block_i, block in enumerate(blocks):
        block = np.asarray(block, dtype=int)
        rel = np.linspace(0.0, 1.0, len(block)) if len(block) > 1 else np.zeros(len(block), dtype=float)
        base_block = base_all[block].mean(axis=0)
        base_std = base_all[block].std(axis=0)
        for local_i, global_pos in enumerate(block):
            row: dict[str, float | int] = {
                row_index_name: int(rows.iloc[int(global_pos)][row_index_name]),
                "segj_len": int(len(block)),
                "segj_relpos": float(rel[local_i]),
                "segj_edge_dist": float(min(rel[local_i], 1.0 - rel[local_i])),
                "segj_base_mean": float(base_block.mean()),
                "segj_base_std_mean": float(base_std.mean()),
            }
            for j, target in enumerate(TARGETS):
                row[f"segj_block_base_{target}"] = float(base_block[j])
                row[f"segj_block_base_std_{target}"] = float(base_std[j])
            base_row = base_all[int(global_pos)]
            for ctx, values in context_outputs.items():
                row.update(
                    make_feature_dict(
                        ctx=ctx,
                        sem_prob=values["sem_prob"][block_i],
                        raw_prob=values["raw_prob"][block_i],
                        sem_rate=values["sem_rate"][block_i],
                        raw_rate=values["raw_rate"][block_i],
                        ridge_rate=values["ridge_rate"][block_i],
                        base_block=base_block,
                        base_row=base_row,
                    )
                )
            feature_rows.append(row)
    return pd.DataFrame(feature_rows)


def predict_block_feature_frame(
    rows: pd.DataFrame,
    z: np.ndarray,
    canvas: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    known: np.ndarray,
    train_blocks: list[np.ndarray],
    pred_blocks: list[np.ndarray],
    seed: int,
    row_index_name: str,
) -> tuple[pd.DataFrame, dict[str, float]]:
    if not train_blocks or not pred_blocks:
        return pd.DataFrame(), {"train_blocks": float(len(train_blocks)), "pred_blocks": float(len(pred_blocks))}

    train_rate = block_label_rates(y, train_blocks)
    semantic_target = atlas.build_target_matrix("label_rate", rows, z, canvas, y, train_blocks)
    routine_target = atlas.build_target_matrix("raw_mean", rows, z, canvas, y, train_blocks)
    semantic_cb, semantic_proto = fit_codebook(semantic_target, SEMANTIC_K, seed=seed + 101)
    routine_cb, routine_proto = fit_codebook(routine_target, ROUTINE_K, seed=seed + 202)
    semantic_proto_rate = proto_rate_matrix(semantic_proto, train_rate, SEMANTIC_K)
    routine_proto_rate = proto_rate_matrix(routine_proto, train_rate, ROUTINE_K)

    train_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
    pred_parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in pred_blocks]
    context_outputs: dict[str, dict[str, np.ndarray]] = {}
    for ctx_i, ctx in enumerate(CONTEXTS):
        train_ctx = np.vstack([atlas.build_context(p, ctx) for p in train_parts]).astype(np.float32)
        pred_ctx = np.vstack([atlas.build_context(p, ctx) for p in pred_parts]).astype(np.float32)
        train_sem_prob, pred_sem_prob = fit_proto_probs(
            train_ctx, pred_ctx, semantic_proto, SEMANTIC_K, c_value=0.85, seed=seed + 300 + ctx_i
        )
        train_raw_prob, pred_raw_prob = fit_proto_probs(
            train_ctx, pred_ctx, routine_proto, ROUTINE_K, c_value=0.70, seed=seed + 400 + ctx_i
        )
        ridge_rate = fit_ridge_rate(
            train_ctx=train_ctx,
            pred_ctx=pred_ctx,
            train_sem_prob=train_sem_prob,
            pred_sem_prob=pred_sem_prob,
            train_raw_prob=train_raw_prob,
            pred_raw_prob=pred_raw_prob,
            train_rate=train_rate,
            alpha=45.0 if ctx in {"past_label", "prior_label", "bidir_label"} else 80.0,
        )
        context_outputs[ctx] = {
            "sem_prob": pred_sem_prob,
            "raw_prob": pred_raw_prob,
            "sem_rate": adv.clip(pred_sem_prob @ semantic_proto_rate),
            "raw_rate": adv.clip(pred_raw_prob @ routine_proto_rate),
            "ridge_rate": adv.clip(ridge_rate),
        }

    audit: dict[str, float] = {
        "train_blocks": float(len(train_blocks)),
        "pred_blocks": float(len(pred_blocks)),
        "semantic_proto_entropy": float(entropy_prob((np.bincount(semantic_proto, minlength=SEMANTIC_K) / len(semantic_proto))[None, :])[0]),
        "routine_proto_entropy": float(entropy_prob((np.bincount(routine_proto, minlength=ROUTINE_K) / len(routine_proto))[None, :])[0]),
    }
    try:
        pred_semantic_target = atlas.build_target_matrix("label_rate", rows, z, canvas, y, pred_blocks)
        pred_sem_proto = predict_codebook(semantic_cb, pred_semantic_target)
        sem_pred = context_outputs["prior_label"]["sem_prob"].argmax(axis=1)
        audit["prior_label_sem_proto_acc"] = float((sem_pred == pred_sem_proto).mean())
    except Exception:
        audit["prior_label_sem_proto_acc"] = np.nan

    feature_frame = expand_blocks_to_rows(rows, base_all, pred_blocks, context_outputs, row_index_name=row_index_name)
    return feature_frame, audit


def build_subject_episode_features(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    canvas: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    repeats: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lengths = adv.actual_lengths_by_subject(rows)
    fold_frames = []
    audit_rows = []
    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=317000)):
        known = adv.known_mask_for_train(rows, tr_idx)
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=220)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        frame, audit = predict_block_feature_frame(
            rows=rows,
            z=z,
            canvas=canvas,
            y=y,
            base_all=base_all,
            known=known,
            train_blocks=train_blocks,
            pred_blocks=val_blocks,
            seed=317000 + fold_i * 31,
            row_index_name="train_idx",
        )
        if not frame.empty:
            fold_frames.append(frame)
        audit_rows.append({"fold": fold, **audit})
        print(
            f"segj fold={fold} train_blocks={len(train_blocks)} val_blocks={len(val_blocks)} "
            f"covered_frames={len(fold_frames)}",
            flush=True,
        )

    if os.environ.get("SEGJ_COVERAGE_PASS", "1") == "1":
        for chunk_i, (tr_idx, val_idx) in enumerate(broad.qlp.make_subject_blocks(train)):
            fold = f"subject_chunk_{chunk_i:02d}"
            known = adv.known_mask_for_train(rows, tr_idx)
            train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=220)
            val_blocks = adv.contiguous_val_blocks(rows, val_idx)
            frame, audit = predict_block_feature_frame(
                rows=rows,
                z=z,
                canvas=canvas,
                y=y,
                base_all=base_all,
                known=known,
                train_blocks=train_blocks,
                pred_blocks=val_blocks,
                seed=318000 + chunk_i * 31,
                row_index_name="train_idx",
            )
            if not frame.empty:
                fold_frames.append(frame)
            audit_rows.append({"fold": fold, **audit})
            print(
                f"segj coverage fold={fold} train_blocks={len(train_blocks)} val_blocks={len(val_blocks)} "
                f"covered_frames={len(fold_frames)}",
                flush=True,
            )

    if fold_frames:
        raw_train = pd.concat(fold_frames, ignore_index=True)
        grouped = raw_train.groupby("train_idx", sort=True).mean(numeric_only=True)
        counts = raw_train.groupby("train_idx", sort=True).size()
    else:
        grouped = pd.DataFrame(index=np.arange(len(train)))
        counts = pd.Series(0, index=np.arange(len(train)))
    train_values = grouped.drop(columns=["train_idx"], errors="ignore").reindex(np.arange(len(train))).reset_index(drop=True)
    train_feat = pd.concat([train[SUB_KEY + TARGETS].reset_index(drop=True), train_values], axis=1)
    train_feat["segj_oof_count"] = counts.reindex(np.arange(len(train))).fillna(0).to_numpy(dtype=float)

    full_known = adv.known_mask_for_train(rows, np.arange(len(train)))
    full_train_blocks = adv.make_training_blocks(rows, y, np.arange(len(train)), lengths, max_blocks_per_subject=280)
    sub_blocks = adv.submission_blocks(train, sub, rows)
    sub_raw, sub_audit = predict_block_feature_frame(
        rows=rows,
        z=z,
        canvas=canvas,
        y=y,
        base_all=base_all,
        known=full_known,
        train_blocks=full_train_blocks,
        pred_blocks=sub_blocks,
        seed=319999,
        row_index_name="sub_idx",
    )
    sub_grouped = sub_raw.groupby("sub_idx", sort=True).mean(numeric_only=True)
    sub_values = sub_grouped.drop(columns=["sub_idx"], errors="ignore").reindex(np.arange(len(sub))).reset_index(drop=True)
    sub_feat = pd.concat([sub[SUB_KEY].reset_index(drop=True), sub_values], axis=1)
    sub_feat["segj_oof_count"] = 1.0
    audit_rows.append({"fold": "submission_full_fit", **sub_audit})
    audit_df = pd.DataFrame(audit_rows)
    return train_feat, sub_feat, audit_df


def numeric_feature_cols(df: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + SUB_KEY + KEY + ["segj_oof_count"])
    cols = []
    for col in df.columns:
        if col in excluded:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def corr(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 60:
        return np.nan
    aa = a[ok]
    bb = b[ok]
    if np.std(aa) <= 1e-12 or np.std(bb) <= 1e-12:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def prefilter_features(train_feat: pd.DataFrame, base: np.ndarray, top_n: int) -> pd.DataFrame:
    cols = numeric_feature_cols(train_feat)
    y = train_feat[TARGETS].to_numpy(dtype=int)
    rows = []
    for target in TARGETS:
        j = TARGETS.index(target)
        residual = y[:, j].astype(float) - base[:, j]
        for col in cols:
            for mode in MODES:
                try:
                    x_ref, _ = broad.transform_pair(train_feat, train_feat, col, mode)
                except Exception:
                    continue
                r = corr(x_ref, residual)
                if np.isfinite(r):
                    rows.append({"target": target, "feature": col, "mode": mode, "corr": r, "abs_corr": abs(r)})
    pre = pd.DataFrame(rows).sort_values(["target", "abs_corr"], ascending=[True, False])
    return pre.groupby("target", group_keys=False).head(top_n).reset_index(drop=True)


def transformed_matrix(
    fit_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    features: list[tuple[str, str]],
) -> tuple[np.ndarray, np.ndarray]:
    fit_parts = []
    pred_parts = []
    for feature, mode in features:
        a, b = broad.transform_pair(fit_rows, pred_rows, feature, mode)
        fit_parts.append(a)
        pred_parts.append(b)
    if not fit_parts:
        return np.zeros((len(fit_rows), 0)), np.zeros((len(pred_rows), 0))
    return np.column_stack(fit_parts), np.column_stack(pred_parts)


def corrected_oof_and_submission(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub: np.ndarray,
    target: str,
    features: list[tuple[str, str]],
    c_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    j = TARGETS.index(target)
    y = train_feat[target].to_numpy(dtype=int)
    oof = np.zeros(len(train_feat), dtype=float)
    for tr_idx, val_idx in broad.qlp.make_subject_blocks(train_feat):
        fit_rows = train_feat.iloc[tr_idx].copy()
        val_rows = train_feat.iloc[val_idx].copy()
        x_tr_extra, x_val_extra = transformed_matrix(fit_rows, val_rows, features)
        x_tr = np.column_stack([adv.logit(base[tr_idx, j]), x_tr_extra])
        x_val = np.column_stack([adv.logit(base[val_idx, j]), x_val_extra])
        scaler = StandardScaler()
        x_tr = scaler.fit_transform(np.nan_to_num(x_tr, nan=0.0, posinf=0.0, neginf=0.0))
        x_val = scaler.transform(np.nan_to_num(x_val, nan=0.0, posinf=0.0, neginf=0.0))
        if y[tr_idx].min() == y[tr_idx].max():
            oof[val_idx] = float(y[tr_idx].mean())
            continue
        clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=1000)
        clf.fit(x_tr, y[tr_idx])
        oof[val_idx] = clf.predict_proba(x_val)[:, 1]

    x_all_extra, x_sub_extra = transformed_matrix(train_feat, sub_feat, features)
    x_all = np.column_stack([adv.logit(base[:, j]), x_all_extra])
    x_sub = np.column_stack([adv.logit(base_sub[:, j]), x_sub_extra])
    scaler = StandardScaler()
    x_all = scaler.fit_transform(np.nan_to_num(x_all, nan=0.0, posinf=0.0, neginf=0.0))
    x_sub = scaler.transform(np.nan_to_num(x_sub, nan=0.0, posinf=0.0, neginf=0.0))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=1000)
    clf.fit(x_all, y)
    return adv.clip(oof), adv.clip(clf.predict_proba(x_sub)[:, 1])


def scan_residual_features(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub_arr: np.ndarray,
    top_n: int = 70,
) -> tuple[pd.DataFrame, dict[tuple[str, int, float], tuple[np.ndarray, np.ndarray, list[tuple[str, str]]]]]:
    pre = prefilter_features(train_feat, base, top_n=top_n)
    pre.to_csv(OUT / "subject_episode_graph_jepa_prefilter.csv", index=False)
    y = train_feat[TARGETS].to_numpy(dtype=int)
    rows = []
    cache: dict[tuple[str, int, float], tuple[np.ndarray, np.ndarray, list[tuple[str, str]]]] = {}
    for target in TARGETS:
        j = TARGETS.index(target)
        target_pre = pre[pre["target"].eq(target)].sort_values("abs_corr", ascending=False)
        pairs = [(str(r.feature), str(r.mode)) for r in target_pre.itertuples(index=False)]
        seen = set()
        unique_pairs = []
        for pair in pairs:
            if pair in seen:
                continue
            seen.add(pair)
            unique_pairs.append(pair)
        base_loss = loss_col(y[:, j], base[:, j])
        for n_feat in [3, 5, 8, 12, 16, 24]:
            features = unique_pairs[: min(n_feat, len(unique_pairs))]
            if not features:
                continue
            for c_value in [0.02, 0.05, 0.10, 0.20]:
                corrected, corrected_sub = corrected_oof_and_submission(
                    train_feat, sub_feat, base, base_sub_arr, target, features, c_value
                )
                cache[(target, n_feat, c_value)] = (corrected, corrected_sub, features)
                losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in BLEND_GRID]
                best_i = int(np.argmin(losses))
                best_weight = float(BLEND_GRID[best_i])
                rows.append(
                    {
                        "target": target,
                        "target_weight": TARGET_STAGE_WEIGHT[target],
                        "n_features": n_feat,
                        "c_value": c_value,
                        "base_loss": base_loss,
                        "corrected_loss": loss_col(y[:, j], corrected),
                        "best_weight": best_weight,
                        "best_loss": float(losses[best_i]),
                        "delta_vs_base": float(losses[best_i] - base_loss),
                        "weighted_delta": float((losses[best_i] - base_loss) * TARGET_STAGE_WEIGHT[target]),
                        "features": "|".join([f"{f}:{m}" for f, m in features]),
                    }
                )
        print(f"segj scan target={target} candidates={len(rows)}", flush=True)
    scan = pd.DataFrame(rows).sort_values(["weighted_delta", "delta_vs_base"]).reset_index(drop=True)
    return scan, cache


def add_guardrails(
    scan: pd.DataFrame,
    cache: dict[tuple[str, int, float], tuple[np.ndarray, np.ndarray, list[tuple[str, str]]]],
    train_feat: pd.DataFrame,
    base: np.ndarray,
) -> pd.DataFrame:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    guarded = scan.copy()
    for col in ["mean_delta", "median_delta", "p25_delta", "p75_delta", "win_rate", "mean_selected_weight", "zero_weight_rate"]:
        guarded[col] = np.nan
    top_rows = guarded[guarded["delta_vs_base"] < 0].groupby("target", group_keys=False).head(8)
    for idx, row in top_rows.iterrows():
        key = (str(row["target"]), int(row["n_features"]), float(row["c_value"]))
        corrected = cache[key][0]
        stats = broad.repeated_subject_guardrail(
            train_feat,
            y,
            base,
            corrected,
            TARGETS.index(str(row["target"])),
        )
        for col, val in stats.items():
            guarded.loc[idx, col] = val
    guarded["passes_loose"] = (
        (guarded["delta_vs_base"] <= -0.00015)
        & (guarded["mean_delta"].fillna(1.0) < 0.0)
        & (guarded["win_rate"].fillna(0.0) >= 0.56)
        & (guarded["best_weight"] > 0)
    )
    guarded["passes_strict"] = (
        (guarded["delta_vs_base"] <= -0.00035)
        & (guarded["mean_delta"].fillna(1.0) <= -0.00010)
        & (guarded["win_rate"].fillna(0.0) >= 0.62)
        & (guarded["best_weight"] > 0)
    )
    return guarded.sort_values(["passes_strict", "passes_loose", "weighted_delta", "delta_vs_base"], ascending=[False, False, True, True])


def select_ops(scan: pd.DataFrame, mode: str) -> pd.DataFrame:
    ops = []
    seen = set()
    if mode == "strict":
        source = scan[scan["passes_strict"]].sort_values(["weighted_delta", "delta_vs_base"])
    elif mode == "loose_s23":
        source = scan[
            scan["passes_strict"]
            | (
                scan["target"].isin(["S2", "S3"])
                & (scan["delta_vs_base"] <= -0.00012)
                & (scan["win_rate"].fillna(0.0) >= 0.54)
                & (scan["best_weight"] > 0)
            )
        ].sort_values(["weighted_delta", "delta_vs_base"])
    elif mode == "top_negative":
        source = scan[(scan["delta_vs_base"] < 0) & (scan["best_weight"] > 0)].sort_values(["weighted_delta", "delta_vs_base"])
    else:
        raise ValueError(mode)
    for row in source.itertuples(index=False):
        target = str(row.target)
        if target in seen:
            continue
        ops.append(row._asdict())
        seen.add(target)
    return pd.DataFrame(ops)


def build_candidate_arrays(
    ops: pd.DataFrame,
    cache: dict[tuple[str, int, float], tuple[np.ndarray, np.ndarray, list[tuple[str, str]]]],
    base: np.ndarray,
    base_sub_arr: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    pred = base.copy()
    sub_pred = base_sub_arr.copy()
    detail_rows = []
    if ops.empty:
        return pred, sub_pred, pd.DataFrame()
    for row in ops.itertuples(index=False):
        target = str(row.target)
        j = TARGETS.index(target)
        corrected, corrected_sub, features = cache[(target, int(row.n_features), float(row.c_value))]
        w = float(row.best_weight)
        pred[:, j] = adv.clip((1.0 - w) * base[:, j] + w * corrected)
        sub_pred[:, j] = adv.clip((1.0 - w) * base_sub_arr[:, j] + w * corrected_sub)
        detail_rows.append(
            {
                "target": target,
                "n_features": int(row.n_features),
                "c_value": float(row.c_value),
                "best_weight": w,
                "delta_vs_base": float(row.delta_vs_base),
                "win_rate": float(row.win_rate) if np.isfinite(float(row.win_rate)) else np.nan,
                "features": "|".join([f"{f}:{m}" for f, m in features]),
            }
        )
    return pred, sub_pred, pd.DataFrame(detail_rows)


def emit_scaled_submissions(
    variant: str,
    base: np.ndarray,
    base_sub_df: pd.DataFrame,
    pred: np.ndarray,
    sub_pred: np.ndarray,
    y: np.ndarray,
    scales: list[float],
) -> pd.DataFrame:
    rows = []
    base_loss = mean_loss(y, base)
    base_logit = adv.logit(base)
    pred_move = adv.logit(pred) - base_logit
    base_sub_arr = base_sub_df[TARGETS].to_numpy(dtype=float)
    sub_base_logit = adv.logit(base_sub_arr)
    sub_move = adv.logit(sub_pred) - sub_base_logit
    for scale in scales:
        oof_scaled = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + scale * pred_move))))
        sub_scaled = adv.clip(1.0 / (1.0 + np.exp(-(sub_base_logit + scale * sub_move))))
        file_name = f"submission_subject_episode_graph_jepa_{variant}_scale{str(scale).replace('.', 'p')}.csv"
        out = base_sub_df.copy()
        out[TARGETS] = sub_scaled
        out.to_csv(OUT / file_name, index=False)
        oof_loss = mean_loss(y, oof_scaled)
        target_losses = {f"loss_{t}": loss_col(y[:, j], oof_scaled[:, j]) for j, t in enumerate(TARGETS)}
        rows.append(
            {
                "variant": variant,
                "candidate": file_name,
                "scale": scale,
                "oof_loss": oof_loss,
                "oof_delta_vs_stage2": oof_loss - base_loss,
                **target_losses,
                **adv.public_axis_for(file_name),
            }
        )
    return pd.DataFrame(rows)


def emit_raw_rescue_combos(base_sub_df: pd.DataFrame) -> pd.DataFrame:
    raw_path = OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
    segj_path = OUT / "submission_subject_episode_graph_jepa_strict_scale1p0.csv"
    if not raw_path.exists() or not segj_path.exists():
        return pd.DataFrame()
    raw = pd.read_csv(raw_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    segj = pd.read_csv(segj_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = base_sub_df.sort_values(KEY).reset_index(drop=True)
    base_logit = adv.logit(base[TARGETS].to_numpy(dtype=float))
    raw_move = adv.logit(raw[TARGETS].to_numpy(dtype=float)) - base_logit
    segj_move = adv.logit(segj[TARGETS].to_numpy(dtype=float)) - base_logit
    configs = [
        (1.00, 0.25),
        (1.00, 0.35),
        (1.00, 0.50),
        (0.75, 0.35),
        (0.75, 0.50),
        (1.25, 0.25),
    ]
    rows = []
    for raw_w, segj_w in configs:
        arr = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + raw_w * raw_move + segj_w * segj_move))))
        file_name = (
            "submission_subject_episode_graph_jepa_rawrescue"
            f"_raw{str(raw_w).replace('.', 'p')}_segj{str(segj_w).replace('.', 'p')}.csv"
        )
        out = base.copy()
        out[TARGETS] = arr
        out.to_csv(OUT / file_name, index=False)
        move = adv.logit(arr) - base_logit
        rows.append(
            {
                "candidate": file_name,
                "raw_weight": raw_w,
                "segj_weight": segj_w,
                "move_norm": float(np.linalg.norm(move)),
                "raw_cos": float(
                    np.dot(move.reshape(-1), raw_move.reshape(-1))
                    / max(float(np.linalg.norm(move) * np.linalg.norm(raw_move)), 1e-12)
                ),
                "segj_cos": float(
                    np.dot(move.reshape(-1), segj_move.reshape(-1))
                    / max(float(np.linalg.norm(move) * np.linalg.norm(segj_move)), 1e-12)
                ),
                **adv.public_axis_for(file_name),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    audit: pd.DataFrame,
    scan: pd.DataFrame,
    selected: pd.DataFrame,
    candidates: pd.DataFrame,
    combos: pd.DataFrame,
) -> None:
    lines = [
        "# Subject Episode Graph JEPA",
        "",
        "This experiment treats each submission-like hidden segment as an episode node.",
        "",
        "- JEPA target 1: `label_rate` semantic codebook with K=10.",
        "- JEPA target 2: `raw_mean` routine codebook with K=8.",
        "- Context: surrounding known labels, base predictions, rhythm/raw canvas summaries, position, and gaps.",
        "- Use: no direct probability averaging from JEPA latents; exported probabilities are residual probes on JEPA-derived features.",
        "- Stage emphasis: S2/S3 are prioritized during operation ranking, not by changing the official metric.",
        "",
        "## Block Audit",
        "",
        audit.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(40).to_csv(index=False),
        "",
        "## Selected Ops",
        "",
        selected.to_csv(index=False),
        "",
        "## Candidate Submissions",
        "",
        candidates.sort_values(["oof_delta_vs_stage2", "bad_axis_projection_ratio"]).to_csv(index=False),
        "",
        "## Raw-Rescue + SEGJ Combos",
        "",
        combos.to_csv(index=False),
    ]
    (OUT / "subject_episode_graph_jepa_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    repeats = int(os.environ.get("SEGJ_REPEATS", "8"))
    reuse = os.environ.get("SEGJ_REUSE", "0") == "1"
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y_full = adv.train_label_matrix(rows, train)
    y_train = train[TARGETS].to_numpy(dtype=int)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)

    train_feature_path = OUT / "subject_episode_graph_jepa_train_features.parquet"
    sub_feature_path = OUT / "subject_episode_graph_jepa_submission_features.parquet"
    audit_path = OUT / "subject_episode_graph_jepa_block_audit.csv"
    if reuse and train_feature_path.exists() and sub_feature_path.exists() and audit_path.exists():
        train_feat = pd.read_parquet(train_feature_path)
        sub_feat = pd.read_parquet(sub_feature_path)
        audit = pd.read_csv(audit_path)
    else:
        train_feat, sub_feat, audit = build_subject_episode_features(
            train=train,
            sub=sub,
            rows=rows,
            z=z,
            canvas=canvas,
            y=y_full,
            base_all=base_all,
            repeats=repeats,
        )
        train_feat.to_parquet(train_feature_path, index=False)
        sub_feat.to_parquet(sub_feature_path, index=False)
        audit.to_csv(audit_path, index=False)
    print(f"segj features train={train_feat.shape} sub={sub_feat.shape}", flush=True)

    base_sub_arr = base_sub[TARGETS].to_numpy(dtype=float)
    scan, cache = scan_residual_features(train_feat, sub_feat, base, base_sub_arr, top_n=70)
    scan = add_guardrails(scan, cache, train_feat, base)
    scan.to_csv(OUT / "subject_episode_graph_jepa_scan.csv", index=False)

    candidate_frames = []
    selected_frames = []
    for variant in ["strict", "loose_s23", "top_negative"]:
        ops = select_ops(scan, variant)
        pred, sub_pred, detail = build_candidate_arrays(ops, cache, base, base_sub_arr)
        if detail.empty:
            continue
        detail.insert(0, "variant", variant)
        selected_frames.append(detail)
        candidate_frames.append(
            emit_scaled_submissions(variant, base, base_sub, pred, sub_pred, y_train, scales=[0.35, 0.50, 0.75, 1.00])
        )

    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    candidates = pd.concat(candidate_frames, ignore_index=True) if candidate_frames else pd.DataFrame()
    combos = emit_raw_rescue_combos(base_sub)
    selected.to_csv(OUT / "subject_episode_graph_jepa_selected_ops.csv", index=False)
    candidates.to_csv(OUT / "subject_episode_graph_jepa_candidate_summary.csv", index=False)
    combos.to_csv(OUT / "subject_episode_graph_jepa_rawrescue_combo_summary.csv", index=False)
    write_report(audit, scan, selected, candidates, combos)

    print("SEGJ candidate summary")
    if not candidates.empty:
        print(candidates.sort_values(["oof_delta_vs_stage2", "bad_axis_projection_ratio"]).head(20).round(9).to_string(index=False), flush=True)
    print("SEGJ selected ops")
    if not selected.empty:
        print(selected.to_string(index=False), flush=True)
    print("SEGJ raw-rescue combos")
    if not combos.empty:
        print(combos.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
