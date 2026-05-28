from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY
EPS = hbr.EPS


@dataclass(frozen=True)
class SourceSpec:
    name: str
    train_path: Path
    sub_path: Path
    n_components: int


@dataclass
class BlockRepr:
    target_raw: np.ndarray
    context_raw: np.ndarray
    label_context: np.ndarray
    subject_mean: np.ndarray
    info: dict[str, object]


SOURCE_SPECS = [
    SourceSpec(
        "rt",
        JEPA / "raw_timeline_jepa_rescue_train_features.parquet",
        JEPA / "raw_timeline_jepa_rescue_submission_features.parquet",
        24,
    ),
    SourceSpec(
        "bc",
        JEPA / "block_canvas_jepa_train_features.parquet",
        JEPA / "block_canvas_jepa_submission_features.parquet",
        16,
    ),
    SourceSpec(
        "nb",
        JEPA / "neural_block_canvas_jepa_mps_train_features.parquet",
        JEPA / "neural_block_canvas_jepa_mps_submission_features.parquet",
        12,
    ),
    SourceSpec(
        "sg",
        JEPA / "subject_episode_graph_jepa_train_features.parquet",
        JEPA / "subject_episode_graph_jepa_submission_features.parquet",
        12,
    ),
]

SOURCE_PRESETS = {
    "rt": ["rt"],
    "rt_bc": ["rt", "bc"],
    "rt_bc_nb_sg": ["rt", "bc", "nb", "sg"],
}

BASE_SUBMISSIONS = {
    "stage2": OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "raw05": JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "seq1501": OUT / "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "seqebf": OUT / "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
    "seqd0": OUT / "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
    "pareto03": OUT / "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "rate605": OUT / "submission_hiddenblock_rateprobe_neutral_605de284.csv",
}


def clip(x: np.ndarray | float) -> np.ndarray:
    return hbr.clip(x)


def logit(x: np.ndarray | float) -> np.ndarray:
    return hbr.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return hbr.sigmoid(x)


def stable_tag(text: str) -> str:
    return hbr.stable_tag(text)


def read_feature_source(spec: SourceSpec, rows: pd.DataFrame, train_mask: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    if not spec.train_path.exists() or not spec.sub_path.exists():
        raise FileNotFoundError(f"missing source {spec.name}: {spec.train_path} / {spec.sub_path}")
    train_feat = pd.read_parquet(spec.train_path)
    sub_feat = pd.read_parquet(spec.sub_path)
    train_feat["subject_id"] = train_feat["subject_id"].astype(str)
    sub_feat["subject_id"] = sub_feat["subject_id"].astype(str)
    src = pd.concat([train_feat, sub_feat], ignore_index=True, sort=False)
    src = src.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in src.columns:
            src[col] = pd.to_datetime(src[col])

    excluded = set(KEY + TARGETS + ["split", "hidden_block_id"])
    target_tokens = tuple(TARGETS)
    numeric_cols: list[str] = []
    for col in src.columns:
        if col in excluded:
            continue
        # Avoid pseudo-CV leakage from target-named retrieval summaries.
        if any(tok in col for tok in target_tokens):
            continue
        s = pd.to_numeric(src[col], errors="coerce")
        if s.notna().sum() >= 120 and s.nunique(dropna=True) > 1:
            numeric_cols.append(col)
    if len(numeric_cols) < 2:
        raise ValueError(f"not enough numeric columns for {spec.name}")

    merged = rows[KEY].copy()
    merged["subject_id"] = merged["subject_id"].astype(str)
    merged = merged.merge(src[KEY + numeric_cols], on=KEY, how="left")
    vals = merged[numeric_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    train_vals = vals.loc[train_mask]
    med = train_vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float64)
    scaler = StandardScaler()
    scaler.fit(x[train_mask])
    xs = scaler.transform(x)
    k = min(spec.n_components, xs.shape[1], int(train_mask.sum()) - 1)
    if k < 1:
        raise ValueError(f"invalid PCA dimension for {spec.name}")
    pca = PCA(n_components=k, svd_solver="randomized", random_state=270527 + len(spec.name))
    pca.fit(xs[train_mask])
    z = pca.transform(xs)
    meta = pd.DataFrame(
        {
            "source": spec.name,
            "n_columns": len(numeric_cols),
            "n_components": k,
            "explained_variance": float(np.sum(pca.explained_variance_ratio_)),
            "missing_row_frac": float(vals.isna().all(axis=1).mean()),
        },
        index=[0],
    )
    return meta, z.astype(np.float32), numeric_cols


def build_row_embedding(rows: pd.DataFrame, preset: str) -> tuple[np.ndarray, pd.DataFrame]:
    train_mask = rows["split"].eq("train").to_numpy()
    wanted = set(SOURCE_PRESETS[preset])
    metas = []
    embeds = []
    for spec in SOURCE_SPECS:
        if spec.name not in wanted:
            continue
        meta, z, _cols = read_feature_source(spec, rows, train_mask)
        metas.append(meta.assign(preset=preset))
        embeds.append(z)
    if not embeds:
        raise ValueError(f"empty source preset: {preset}")
    return np.hstack(embeds).astype(np.float32), pd.concat(metas, ignore_index=True)


def agg_stats(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return np.zeros(1, dtype=np.float32)
    if len(x) == 1:
        slope = np.zeros(x.shape[1], dtype=np.float32)
    else:
        slope = (x[-1] - x[0]) / float(len(x) - 1)
    stats = [
        np.nanmean(x, axis=0),
        np.nanstd(x, axis=0),
        np.nanmin(x, axis=0),
        np.nanmax(x, axis=0),
        x[0],
        x[-1],
        slope,
    ]
    return np.nan_to_num(np.concatenate(stats).astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)


def context_positions(rows: pd.DataFrame, block: hbr.Block, known_mask: np.ndarray, radius: int) -> tuple[np.ndarray, np.ndarray]:
    sid = str(block.subject_id)
    subject_mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
    known = np.where(subject_mask & known_mask)[0]
    before = known[known < block.positions.min()]
    after = known[known > block.positions.max()]
    return before[-radius:], after[:radius]


def block_repr(rows: pd.DataFrame, row_z: np.ndarray, y: np.ndarray, block: hbr.Block, known_mask: np.ndarray, radius: int = 7) -> BlockRepr:
    label_ctx, info = hbr.context_info(rows, y, block.positions, known_mask)
    before, after = context_positions(rows, block, known_mask, radius)
    xb = row_z[block.positions]
    target_raw = agg_stats(xb)

    ctx_chunks = []
    for idx in [before, after]:
        if len(idx) == 0:
            ctx_chunks.append(np.zeros(row_z.shape[1] * 7, dtype=np.float32))
        else:
            ctx_chunks.append(agg_stats(row_z[idx]))
    before_mean = row_z[before].mean(axis=0) if len(before) else np.zeros(row_z.shape[1], dtype=np.float32)
    after_mean = row_z[after].mean(axis=0) if len(after) else np.zeros(row_z.shape[1], dtype=np.float32)
    geom = rows.iloc[block.positions][["subject_phase", "dow_sin", "dow_cos", "is_weekend"]].mean().to_numpy(dtype=np.float32)
    context_raw = np.nan_to_num(
        np.concatenate(
            [
                np.array([block.n, len(before), len(after)], dtype=np.float32),
                geom,
                before_mean,
                after_mean,
                after_mean - before_mean,
                *ctx_chunks,
            ]
        ),
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    ).astype(np.float32)
    return BlockRepr(
        target_raw=target_raw,
        context_raw=context_raw,
        label_context=label_ctx,
        subject_mean=np.asarray(info["subject_mean"], dtype=np.float64),
        info=info,
    )


def make_block_reprs(rows: pd.DataFrame, row_z: np.ndarray, y: np.ndarray, blocks: list[hbr.Block], base_known: np.ndarray, hide_self: bool) -> list[BlockRepr]:
    out = []
    for block in blocks:
        known = base_known.copy()
        if hide_self:
            known[block.positions] = False
        out.append(block_repr(rows, row_z, y, block, known))
    return out


def pca_pair(train_x: np.ndarray, hidden_x: np.ndarray, n_components: int, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train_x)
    x_hidden = scaler.transform(hidden_x)
    k = min(n_components, train_x.shape[0] - 1, train_x.shape[1])
    if k < 1:
        return x_train, x_hidden, 1.0
    pca = PCA(n_components=k, svd_solver="randomized", random_state=seed)
    pca.fit(x_train)
    return pca.transform(x_train), pca.transform(x_hidden), float(np.sum(pca.explained_variance_ratio_))


def prepare_matrices(
    train_reprs: list[BlockRepr],
    hidden_reprs: list[BlockRepr],
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    train_target_raw = np.vstack([r.target_raw for r in train_reprs]).astype(np.float64)
    hidden_target_raw = np.vstack([r.target_raw for r in hidden_reprs]).astype(np.float64)
    train_context_raw = np.vstack([r.context_raw for r in train_reprs]).astype(np.float64)
    hidden_context_raw = np.vstack([r.context_raw for r in hidden_reprs]).astype(np.float64)
    train_z, hidden_z, z_ev = pca_pair(train_target_raw, hidden_target_raw, 32, 271001)
    train_ctx_raw, hidden_ctx_raw, c_ev = pca_pair(train_context_raw, hidden_context_raw, 24, 271002)
    train_label = np.vstack([r.label_context for r in train_reprs]).astype(np.float64)
    hidden_label = np.vstack([r.label_context for r in hidden_reprs]).astype(np.float64)
    train_ctx = np.hstack([train_ctx_raw, train_label])
    hidden_ctx = np.hstack([hidden_ctx_raw, hidden_label])
    train_subject = np.vstack([r.subject_mean for r in train_reprs])
    hidden_subject = np.vstack([r.subject_mean for r in hidden_reprs])
    mats = {
        "train_z": train_z,
        "hidden_z": hidden_z,
        "train_ctx": train_ctx,
        "hidden_ctx": hidden_ctx,
        "train_subject": train_subject,
        "hidden_subject": hidden_subject,
    }
    return mats, {"target_repr_ev": z_ev, "context_repr_ev": c_ev}


def donor_mask(blocks: list[hbr.Block], i: int, mode: str) -> np.ndarray:
    base = hbr.donor_mask(blocks, i, "strict_subject" if mode == "strict" else "local_nonoverlap")
    if mode == "same":
        sid = blocks[i].subject_id
        same = np.array([b.subject_id == sid for b in blocks], dtype=bool)
        out = hbr.donor_mask(blocks, i, "local_nonoverlap") & same
        if out.sum() >= 8:
            return out
        return base
    return base


def final_donor_mask(train_blocks: list[hbr.Block], hidden_block: hbr.Block, mode: str) -> np.ndarray:
    out = np.ones(len(train_blocks), dtype=bool)
    if mode == "strict":
        out &= np.array([b.subject_id != hidden_block.subject_id for b in train_blocks], dtype=bool)
    elif mode == "same":
        same = np.array([b.subject_id == hidden_block.subject_id for b in train_blocks], dtype=bool)
        if same.sum() >= 8:
            out &= same
    return out


def predict_target_repr(ctx_train: np.ndarray, z_train: np.ndarray, ctx_one: np.ndarray, donors: np.ndarray, alpha: float = 12.0) -> np.ndarray:
    idx = np.where(donors)[0]
    if len(idx) < 16:
        idx = np.arange(len(z_train))
    scaler = StandardScaler()
    xd = scaler.fit_transform(ctx_train[idx])
    xv = scaler.transform(ctx_one.reshape(1, -1))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xd, z_train[idx])
    return model.predict(xv)[0]


def nearest_rate(X: np.ndarray, rates: np.ndarray, xi: np.ndarray, donors: np.ndarray, k: int) -> np.ndarray:
    idx = np.where(donors)[0]
    if len(idx) == 0:
        return np.full(len(TARGETS), 0.5)
    scaler = StandardScaler()
    xd = scaler.fit_transform(X[idx])
    xv = scaler.transform(xi.reshape(1, -1))[0]
    dist = np.sqrt(np.maximum(((xd - xv) ** 2).mean(axis=1), 0.0))
    take = np.argsort(dist)[: min(k, len(idx))]
    d = dist[take]
    w = 1.0 / np.maximum(d, 1e-4)
    w /= w.sum()
    return clip(w @ rates[idx[take]])


def ridge_rate(X: np.ndarray, rates: np.ndarray, xi: np.ndarray, donors: np.ndarray, alpha: float) -> np.ndarray:
    idx = np.where(donors)[0]
    if len(idx) < 18:
        return np.full(len(TARGETS), 0.5)
    scaler = StandardScaler()
    xd = scaler.fit_transform(X[idx])
    xv = scaler.transform(xi.reshape(1, -1))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xd, rates[idx])
    return clip(model.predict(xv)[0])


def build_jepa_features(z: np.ndarray, ctx: np.ndarray, zhat: np.ndarray) -> dict[str, np.ndarray]:
    resid = z - zhat
    energy = np.sqrt(np.maximum(np.mean(resid**2, axis=1, keepdims=True), 0.0))
    z_norm = np.linalg.norm(z, axis=1, keepdims=True)
    h_norm = np.linalg.norm(zhat, axis=1, keepdims=True)
    cos = (z * zhat).sum(axis=1, keepdims=True) / np.maximum(z_norm * h_norm, 1e-8)
    return {
        "z": z,
        "ctx": ctx,
        "pred": zhat,
        "resid": np.hstack([resid, energy, cos]),
        "z_ctx": np.hstack([z, ctx]),
        "jepa_full": np.hstack([z, zhat, resid, energy, cos, ctx]),
    }


def logit_blend(base: np.ndarray, pred: np.ndarray, weight: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight) * logit(base) + weight * logit(pred)))


def evaluate_preset(
    preset: str,
    rows: pd.DataFrame,
    y: np.ndarray,
    pseudo_blocks: list[hbr.Block],
    hidden_blocks: list[hbr.Block],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], pd.DataFrame]:
    row_z, source_meta = build_row_embedding(rows, preset)
    base_known = hbr.base_known_mask(rows)
    pseudo_reprs = make_block_reprs(rows, row_z, y, pseudo_blocks, base_known, hide_self=True)
    hidden_reprs = make_block_reprs(rows, row_z, y, hidden_blocks, base_known, hide_self=False)
    mats, ev = prepare_matrices(pseudo_reprs, hidden_reprs)
    rates = hbr.true_rates(y, pseudo_blocks)

    preds: dict[str, np.ndarray] = {
        "subject_mean": mats["train_subject"],
    }
    hidden_pred: dict[str, np.ndarray] = {}
    z = mats["train_z"]
    ctx = mats["train_ctx"]
    hz = mats["hidden_z"]
    hctx = mats["hidden_ctx"]

    for mode in ["strict", "local", "same"]:
        zhat = np.zeros_like(z)
        for i in range(len(pseudo_blocks)):
            donors = donor_mask(pseudo_blocks, i, mode)
            zhat[i] = predict_target_repr(ctx, z, ctx[i], donors)
        feats = build_jepa_features(z, ctx, zhat)

        hzhat = np.zeros_like(hz)
        for h, block in enumerate(hidden_blocks):
            donors = final_donor_mask(pseudo_blocks, block, mode)
            hzhat[h] = predict_target_repr(ctx, z, hctx[h], donors)
        hfeats = build_jepa_features(hz, hctx, hzhat)

        method_specs = [
            ("knn_z_k8", "z", "knn", 8),
            ("knn_z_k16", "z", "knn", 16),
            ("knn_resid_k8", "resid", "knn", 8),
            ("knn_full_k8", "jepa_full", "knn", 8),
            ("ridge_zctx_a12", "z_ctx", "ridge", 12.0),
            ("ridge_full_a24", "jepa_full", "ridge", 24.0),
            ("ridge_resid_a12", "resid", "ridge", 12.0),
        ]

        for short, feat_name, kind, param in method_specs:
            name = f"{preset}:{mode}:{short}"
            arr = []
            for i in range(len(pseudo_blocks)):
                donors = donor_mask(pseudo_blocks, i, mode)
                if kind == "knn":
                    arr.append(nearest_rate(feats[feat_name], rates, feats[feat_name][i], donors, int(param)))
                else:
                    arr.append(ridge_rate(feats[feat_name], rates, feats[feat_name][i], donors, float(param)))
            direct = np.vstack(arr)
            preds[name] = direct

            harr = []
            for h, block in enumerate(hidden_blocks):
                donors = final_donor_mask(pseudo_blocks, block, mode)
                if kind == "knn":
                    harr.append(nearest_rate(feats[feat_name], rates, hfeats[feat_name][h], donors, int(param)))
                else:
                    harr.append(ridge_rate(feats[feat_name], rates, hfeats[feat_name][h], donors, float(param)))
            hdirect = np.vstack(harr)
            hidden_pred[name] = hdirect

            for blend_weight in [0.05, 0.10, 0.20, 0.35, 0.50]:
                btag = str(blend_weight).replace(".", "p")
                bname = f"{name}:blend{btag}"
                preds[bname] = logit_blend(mats["train_subject"], direct, blend_weight)
                hidden_pred[bname] = logit_blend(mats["hidden_subject"], hdirect, blend_weight)

        energy_rows = []
        resid = z - zhat
        e = np.sqrt(np.maximum(np.mean(resid**2, axis=1), 0.0))
        for j, target in enumerate(TARGETS):
            vals = rates[:, j]
            energy_rows.append(
                {
                    "preset": preset,
                    "mode": mode,
                    "target": target,
                    "energy_rate_corr": float(np.corrcoef(e, vals)[0, 1]) if np.std(e) > 1e-12 and np.std(vals) > 1e-12 else 0.0,
                }
            )
        pd.DataFrame(energy_rows).to_csv(OUT / f"block_scale_jepa_energy_{preset}_{mode}.csv", index=False)

    summary, target_detail = hbr.summarize_predictions(y, pseudo_blocks, rates, preds)
    summary.insert(0, "preset", preset)
    target_detail.insert(0, "preset", preset)
    hidden_rows = []
    for method, rate in hidden_pred.items():
        for i, block in enumerate(hidden_blocks):
            rec = {
                "preset": preset,
                "method": method,
                "hidden_block_id": block.block_id,
                "subject_id": block.subject_id,
                "n_rows": block.n,
                "start": block.start.date().isoformat(),
                "end": block.end.date().isoformat(),
            }
            for j, target in enumerate(TARGETS):
                rec[f"rate_{target}"] = rate[i, j]
                rec[f"count_{target}"] = rate[i, j] * block.n
            hidden_rows.append(rec)
    meta = source_meta.assign(target_repr_ev=ev["target_repr_ev"], context_repr_ev=ev["context_repr_ev"])
    return summary, target_detail, pd.DataFrame(hidden_rows), hidden_pred, meta


def load_base(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not frame[KEY].equals(sample[KEY]):
        raise ValueError(f"base key mismatch: {path}")
    return frame


def save_candidate(
    base_name: str,
    base_path: Path,
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    hidden_blocks: list[hbr.Block],
    hidden_rate: np.ndarray,
    method: str,
    weight: float,
    target_mask: np.ndarray,
) -> str:
    base = load_base(base_path, sample)
    pred = base[TARGETS].to_numpy(dtype=np.float64)
    for block_i, block in enumerate(hidden_blocks):
        sub_idx = rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        for j, keep in enumerate(target_mask):
            if not keep:
                continue
            pred[sub_idx, j] = clip(sigmoid((1.0 - weight) * logit(pred[sub_idx, j]) + weight * logit(hidden_rate[block_i, j])))
    out = base.copy()
    out[TARGETS] = pred
    method_tag = method.replace(":", "_").replace(".", "p")
    method_tag = method_tag.replace("strict", "str").replace("local", "loc")
    mask_tag = "".join(t.lower() for t, keep in zip(TARGETS, target_mask) if keep)
    wtag = str(weight).replace(".", "p")
    tag = stable_tag(f"{base_name}|{method}|{mask_tag}|{weight}")
    file_name = f"submission_blockscale_jepa_{base_name}_{method_tag}_{mask_tag}_w{wtag}_{tag}.csv"
    out.to_csv(OUT / file_name, index=False)
    return file_name


def build_candidates(
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    hidden_blocks: list[hbr.Block],
    summary: pd.DataFrame,
    target_detail: pd.DataFrame,
    hidden_rates: dict[str, np.ndarray],
) -> list[str]:
    selected = summary[
        (summary["method"].ne("subject_mean"))
        & (~summary["method"].str.endswith(":subject_mean"))
        & (summary["delta_vs_subject_mean"] < -0.004)
    ].head(10)["method"].tolist()
    if not selected:
        selected = summary[
            (summary["method"].ne("subject_mean"))
            & (~summary["method"].str.endswith(":subject_mean"))
        ].head(6)["method"].tolist()

    saved: list[str] = []
    for method in selected:
        if method not in hidden_rates:
            continue
        td = target_detail[target_detail["method"].eq(method)].set_index("target").reindex(TARGETS)
        gain_mask = (td["target_delta_vs_subject_mean"].to_numpy(dtype=float) < -0.0015)
        masks: list[tuple[str, np.ndarray]] = []
        if gain_mask.any():
            masks.append(("gain", gain_mask))
        q3s4 = np.array([t in {"Q3", "S4"} for t in TARGETS], dtype=bool)
        if gain_mask[TARGETS.index("Q3")] or gain_mask[TARGETS.index("S4")]:
            masks.append(("q3s4", q3s4))
        no_q2 = np.array([t != "Q2" for t in TARGETS], dtype=bool)
        if method.startswith("rt_bc") and gain_mask.sum() >= 4:
            masks.append(("noq2", no_q2))
        if not masks:
            continue
        uniq_masks: list[np.ndarray] = []
        for _name, mask in masks:
            if not any(np.array_equal(mask, prev) for prev in uniq_masks):
                uniq_masks.append(mask)

        for base_name, base_path in BASE_SUBMISSIONS.items():
            if not base_path.exists():
                continue
            if base_name == "stage2" and not method.startswith("rt:"):
                continue
            for mask in uniq_masks[:2]:
                for weight in [0.03, 0.05, 0.08]:
                    saved.append(save_candidate(base_name, base_path, sample, rows, hidden_blocks, hidden_rates[method], method, weight, mask))
    return saved


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for file_name in files:
        frame = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        probs = frame[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[KEY].equals(sample[KEY])),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_probs": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(np.min(probs)),
                "max_prob": float(np.max(probs)),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    source_meta: pd.DataFrame,
    summary: pd.DataFrame,
    target_detail: pd.DataFrame,
    hidden_df: pd.DataFrame,
    proxy: pd.DataFrame,
    integ: pd.DataFrame,
    saved: list[str],
) -> None:
    best = summary.head(24)
    best_methods = best["method"].head(8).tolist()
    lines = [
        "# Block-Scale JEPA Target Audit",
        "",
        "JEPA framing: each pseudo-hidden interval is treated as a large target block. The model predicts the block's raw latent representation from surrounding context, then uses target/context compatibility, residual, and energy to estimate hidden label rates.",
        "",
        "## Source Representation",
        "",
        "```csv",
        source_meta.round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Pseudo-Hidden Block Results",
        "",
        "```csv",
        best.round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Target Detail For Best Methods",
        "",
        "```csv",
        target_detail[target_detail["method"].isin(best_methods)].round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Hidden Rate Preview",
        "",
        "```csv",
        hidden_df[hidden_df["method"].isin(best_methods)].head(60).round(6).to_csv(index=False).strip(),
        "```",
    ]
    if saved and not proxy.empty:
        lines.extend(
            [
                "",
                "## Candidate Proxy Shortlist",
                "",
                "```csv",
                proxy.head(30).round(10).to_csv(index=False).strip(),
                "```",
                "",
                "## Integrity",
                "",
                "```csv",
                integ.head(30).round(8).to_csv(index=False).strip(),
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a stricter JEPA translation than row gating: the hidden block is a semantic target block and context predicts its representation before label-rate probing.",
            "- A useful method should improve pseudo-hidden weighted logloss and also stay neutral or favorable on the raw05 public axis.",
            "- If residual/energy methods lose to direct target-representation KNN, the raw block representation carries label signal, but context-prediction compatibility is not yet the public-LB key.",
        ]
    )
    (OUT / "block_scale_jepa_target_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    y = hbr.train_label_matrix(rows, train)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)

    all_summary = []
    all_target = []
    all_hidden = []
    all_meta = []
    hidden_rates: dict[str, np.ndarray] = {}
    for preset in SOURCE_PRESETS:
        summary, target_detail, hidden_df, hidden_pred, source_meta = evaluate_preset(preset, rows, y, pseudo_blocks, hidden_blocks)
        all_summary.append(summary)
        all_target.append(target_detail)
        all_hidden.append(hidden_df)
        all_meta.append(source_meta)
        hidden_rates.update(hidden_pred)

    summary = pd.concat(all_summary, ignore_index=True).sort_values(["weighted_logloss", "rate_rmse_weighted"]).reset_index(drop=True)
    target_detail = pd.concat(all_target, ignore_index=True).sort_values(["target", "target_logloss"]).reset_index(drop=True)
    hidden_df = pd.concat(all_hidden, ignore_index=True)
    source_meta = pd.concat(all_meta, ignore_index=True)

    summary.to_csv(OUT / "block_scale_jepa_target_summary.csv", index=False)
    target_detail.to_csv(OUT / "block_scale_jepa_target_target_detail.csv", index=False)
    hidden_df.to_csv(OUT / "block_scale_jepa_target_hidden_rates.csv", index=False)
    source_meta.to_csv(OUT / "block_scale_jepa_target_source_meta.csv", index=False)

    saved = build_candidates(sample, rows, hidden_blocks, summary, target_detail, hidden_rates)
    proxy = hbr.public_proxy_scores(saved) if saved else pd.DataFrame()
    integ = integrity(saved, sample) if saved else pd.DataFrame()
    if not proxy.empty:
        proxy.to_csv(OUT / "block_scale_jepa_target_candidate_proxy.csv", index=False)
        proxy.head(30).to_csv(OUT / "block_scale_jepa_target_shortlist.csv", index=False)
    if not integ.empty:
        integ.to_csv(OUT / "block_scale_jepa_target_integrity.csv", index=False)

    write_report(source_meta, summary, target_detail, hidden_df, proxy, integ, saved)
    print("[block-scale JEPA] pseudo blocks", len(pseudo_blocks), "hidden blocks", len(hidden_blocks))
    print(summary.head(24).round(8).to_string(index=False))
    if not proxy.empty:
        print("\n[candidate proxy]")
        print(proxy.head(24).round(10).to_string(index=False))
    if not integ.empty:
        bad = integ[(~integ["key_ok"]) | (integ["duplicate_keys"] > 0) | (integ["null_probs"] > 0)]
        print("\n[integrity]", "ok" if bad.empty else bad.to_string(index=False))


if __name__ == "__main__":
    main()
