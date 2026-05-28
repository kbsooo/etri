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

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import jepa_friendly_atlas as atlas  # noqa: E402


GROUPS: dict[str, list[str]] = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q_only": ["Q1", "Q2", "Q3"],
    "stage_only": ["S1", "S2", "S3", "S4"],
    "s23_only": ["S2", "S3"],
    "core_q_s23": ["Q1", "Q2", "Q3", "S2", "S3"],
}
STRENGTHS = [0.15, 0.25, 0.35, 0.50, 0.75, 1.00]
SCALES = [0.35, 0.50, 0.75, 1.00]


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = adv.clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], p[:, j]) for j in range(len(TARGETS))]))


def block_rates(y: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    rates = []
    for block in blocks:
        vals = y[np.asarray(block, dtype=int)]
        rate = np.nanmean(vals, axis=0)
        rates.append(np.nan_to_num(rate, nan=0.5))
    return np.vstack(rates).astype(np.float32)


def block_sid(rows: pd.DataFrame, block: np.ndarray) -> str:
    return str(rows.iloc[int(block[0])]["subject_id"])


def desc_actual(z: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    return np.vstack([bcj.summarize_z(z, b) for b in blocks]).astype(np.float32)


def desc_context(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    blocks: list[np.ndarray],
    known: np.ndarray,
    variant: str,
) -> np.ndarray:
    parts = [atlas.rich_context_parts(rows, z, y, base_all, b, known) for b in blocks]
    return np.vstack([atlas.build_context(p, variant) for p in parts]).astype(np.float32)


def reduce_dim(train_x: np.ndarray, query_x: np.ndarray, seed: int, budget: int = 64) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    qu = scaler.transform(finite(query_x))
    k = min(budget, tr.shape[0] - 2, tr.shape[1])
    if k >= 8 and k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=seed)
        tr = pca.fit_transform(tr)
        qu = pca.transform(qu)
    return tr.astype(np.float32), qu.astype(np.float32)


def knn_rates(
    train_x: np.ndarray,
    query_x: np.ndarray,
    train_rate: np.ndarray,
    train_sids: list[str],
    query_sids: list[str],
    k: int,
    seed: int,
) -> np.ndarray:
    tr, qu = reduce_dim(train_x, query_x, seed=seed, budget=56)
    train_sids_arr = np.asarray(train_sids)
    out = np.zeros((len(qu), len(TARGETS)), dtype=np.float32)
    for i, q in enumerate(qu):
        dist = np.sqrt(((tr - q[None, :]) ** 2).mean(axis=1))
        same = train_sids_arr == query_sids[i]
        adjusted = dist - 0.10 * same.astype(float)
        order = np.argsort(adjusted)[: min(k, len(adjusted))]
        raw_d = dist[order]
        tau = float(np.median(raw_d) + 1e-6)
        weights = np.exp(-raw_d / max(tau, 1e-6))
        weights = weights / max(float(weights.sum()), 1e-12)
        out[i] = np.average(train_rate[order], axis=0, weights=weights).astype(np.float32)
    return adv.clip(out)


def ridge_rates(train_x: np.ndarray, query_x: np.ndarray, train_rate: np.ndarray, alpha: float, seed: int) -> np.ndarray:
    tr, qu = reduce_dim(train_x, query_x, seed=seed, budget=72)
    model = Ridge(alpha=float(alpha), solver="svd")
    model.fit(tr, train_rate)
    return adv.clip(model.predict(qu))


def proto_rates(train_x: np.ndarray, query_x: np.ndarray, train_rate: np.ndarray, k: int, seed: int) -> np.ndarray:
    if len(train_rate) < k * 4:
        return np.tile(train_rate.mean(axis=0), (len(query_x), 1))
    rate_scaler = StandardScaler()
    rate_x = rate_scaler.fit_transform(train_rate)
    km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=20, batch_size=256)
    proto = km.fit_predict(rate_x)
    proto_rate = np.zeros((k, train_rate.shape[1]), dtype=np.float32)
    global_rate = train_rate.mean(axis=0)
    for cid in range(k):
        mask = proto == cid
        proto_rate[cid] = train_rate[mask].mean(axis=0) if mask.any() else global_rate
    tr, qu = reduce_dim(train_x, query_x, seed=seed + 13, budget=72)
    if np.unique(proto).size < 2:
        return np.tile(global_rate, (len(query_x), 1))
    clf = LogisticRegression(C=0.7, solver="lbfgs", max_iter=1000, random_state=seed + 29)
    clf.fit(tr, proto)
    raw = clf.predict_proba(qu).astype(np.float32)
    prob = np.full((len(qu), k), 1e-6, dtype=np.float32)
    for col_i, cls in enumerate(clf.classes_):
        prob[:, int(cls)] = raw[:, col_i]
    prob = prob / prob.sum(axis=1, keepdims=True)
    return adv.clip(prob @ proto_rate)


def context_label_rates(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    blocks: list[np.ndarray],
    known: np.ndarray,
    part_name: str,
) -> np.ndarray:
    out = []
    for block in blocks:
        parts = atlas.rich_context_parts(rows, z, y, base_all, block, known)
        vals = parts[part_name][: len(TARGETS)]
        out.append(np.nan_to_num(vals, nan=0.5))
    return adv.clip(np.vstack(out).astype(np.float32))


def fit_predict_rate_methods(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    train_indices: np.ndarray,
    train_blocks: list[np.ndarray],
    query_blocks: list[np.ndarray],
    lengths: dict[str, list[int]],
    seed: int,
) -> dict[str, np.ndarray]:
    known = adv.known_mask_for_train(rows, train_indices)
    train_rate = block_rates(y, train_blocks)
    train_sids = [block_sid(rows, b) for b in train_blocks]
    query_sids = [block_sid(rows, b) for b in query_blocks]

    actual_train = desc_actual(z, train_blocks)
    actual_query = desc_actual(z, query_blocks)
    pred_query = bcj.predict_block_summary(rows, z, y, base_all, train_indices, query_blocks, lengths, alpha=50.0)
    pred_train = bcj.predict_block_summary(rows, z, y, base_all, train_indices, train_blocks, lengths, alpha=50.0)
    ctx_train = desc_context(rows, z, y, base_all, train_blocks, known, "prior_all")
    ctx_query = desc_context(rows, z, y, base_all, query_blocks, known, "prior_all")
    label_ctx_train = desc_context(rows, z, y, base_all, train_blocks, known, "bidir_label")
    label_ctx_query = desc_context(rows, z, y, base_all, query_blocks, known, "bidir_label")

    descs: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "actual": (actual_train, actual_query),
        "pred": (pred_train, pred_query),
        "mix": (0.5 * actual_train + 0.5 * pred_train, 0.5 * actual_query + 0.5 * pred_query),
        "ctx": (ctx_train, ctx_query),
        "actual_ctx": (np.hstack([actual_train, ctx_train]), np.hstack([actual_query, ctx_query])),
        "label_ctx": (label_ctx_train, label_ctx_query),
    }

    methods: dict[str, np.ndarray] = {
        "ctx_prior_label": context_label_rates(rows, z, y, base_all, query_blocks, known, "prior_label"),
        "ctx_past_label": context_label_rates(rows, z, y, base_all, query_blocks, known, "past_label"),
        "ctx_future_label": context_label_rates(rows, z, y, base_all, query_blocks, known, "future_label"),
    }
    methods["ctx_bidir_label"] = adv.clip(0.5 * methods["ctx_past_label"] + 0.5 * methods["ctx_future_label"])

    for desc_i, (name, (tr_x, qu_x)) in enumerate(descs.items()):
        for k in [5, 15, 40]:
            methods[f"{name}_knn{k}"] = knn_rates(tr_x, qu_x, train_rate, train_sids, query_sids, k=k, seed=seed + desc_i * 100 + k)
        for alpha in [10.0, 50.0, 150.0]:
            methods[f"{name}_ridge{int(alpha)}"] = ridge_rates(tr_x, qu_x, train_rate, alpha=alpha, seed=seed + desc_i * 100 + int(alpha))
        methods[f"{name}_proto10"] = proto_rates(tr_x, qu_x, train_rate, k=10, seed=seed + desc_i * 100 + 10)
        methods[f"{name}_blend_knn15_ridge50"] = adv.clip(
            0.55 * methods[f"{name}_knn15"] + 0.45 * methods[f"{name}_ridge50"]
        )
        methods[f"{name}_blend_prior_knn15"] = adv.clip(
            0.55 * methods["ctx_prior_label"] + 0.45 * methods[f"{name}_knn15"]
        )
        methods[f"{name}_blend_prior_ridge50"] = adv.clip(
            0.55 * methods["ctx_prior_label"] + 0.45 * methods[f"{name}_ridge50"]
        )

    return methods


@dataclass
class BlockRecord:
    indices: np.ndarray
    methods: dict[str, np.ndarray]


def build_oof_records(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    cv_mode: str,
    repeats: int,
) -> list[BlockRecord]:
    lengths = adv.actual_lengths_by_subject(rows)
    records: list[BlockRecord] = []
    if cv_mode == "subject_chunk":
        folds = [(tr, va, f"subject_chunk_{i:02d}") for i, (tr, va) in enumerate(broad.qlp.make_subject_blocks(train))]
    elif cv_mode == "geometry":
        folds = list(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=322000))
    else:
        raise ValueError(cv_mode)
    for fold_i, (tr_idx, val_idx, fold) in enumerate(folds):
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=260)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not train_blocks or not val_blocks:
            continue
        methods = fit_predict_rate_methods(
            rows=rows,
            z=z,
            y=y,
            base_all=base_all,
            train_indices=tr_idx,
            train_blocks=train_blocks,
            query_blocks=val_blocks,
            lengths=lengths,
            seed=322000 + fold_i * 101,
        )
        for block_i, block in enumerate(val_blocks):
            idx = rows.iloc[block]["train_idx"].to_numpy(dtype=int)
            records.append(BlockRecord(indices=idx, methods={name: rate[block_i] for name, rate in methods.items()}))
        covered = len(set(np.concatenate([r.indices for r in records]))) if records else 0
        print(f"tecount {cv_mode} fold={fold} train_blocks={len(train_blocks)} val_blocks={len(val_blocks)} covered={covered}", flush=True)
    return records


def build_submission_records(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
) -> list[BlockRecord]:
    lengths = adv.actual_lengths_by_subject(rows)
    train_indices = np.arange(len(train))
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=320)
    sub_blocks = adv.submission_blocks(train, sub, rows)
    methods = fit_predict_rate_methods(
        rows=rows,
        z=z,
        y=y,
        base_all=base_all,
        train_indices=train_indices,
        train_blocks=train_blocks,
        query_blocks=sub_blocks,
        lengths=lengths,
        seed=329999,
    )
    records = []
    for block_i, block in enumerate(sub_blocks):
        idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
        records.append(BlockRecord(indices=idx, methods={name: rate[block_i] for name, rate in methods.items()}))
    return records


def shift_to_mean(p: np.ndarray, target_mean: float) -> np.ndarray:
    target = float(np.clip(target_mean, 1e-4, 1.0 - 1e-4))
    logits = adv.logit(p)
    lo, hi = -12.0, 12.0
    for _ in range(35):
        mid = 0.5 * (lo + hi)
        m = float(np.mean(1.0 / (1.0 + np.exp(-(logits + mid)))))
        if m < target:
            lo = mid
        else:
            hi = mid
    return adv.clip(1.0 / (1.0 + np.exp(-(logits + 0.5 * (lo + hi)))))


def apply_count_solver(
    base: np.ndarray,
    records: list[BlockRecord],
    method: str,
    group: str,
    strength: float,
    scale: float,
) -> np.ndarray:
    out = base.copy()
    target_set = set(GROUPS[group])
    for record in records:
        idx = record.indices
        if method not in record.methods:
            continue
        rate = record.methods[method]
        for j, target in enumerate(TARGETS):
            if target not in target_set:
                continue
            p0 = base[idx, j]
            base_mean = float(np.mean(p0))
            target_mean = (1.0 - strength) * base_mean + strength * float(rate[j])
            shifted = shift_to_mean(p0, target_mean)
            move = adv.logit(shifted) - adv.logit(p0)
            out[idx, j] = adv.clip(1.0 / (1.0 + np.exp(-(adv.logit(p0) + scale * move))))
    return adv.clip(out)


def candidate_axis(base_sub_df: pd.DataFrame, file_name: str) -> dict[str, float]:
    try:
        return adv.public_axis_for(file_name)
    except Exception:
        return {"bad_axis_projection_ratio": np.nan, "good_axis_projection_ratio": np.nan}


def scan_candidates(
    records: list[BlockRecord],
    base: np.ndarray,
    y: np.ndarray,
    method_names: list[str],
    cv_mode: str,
) -> pd.DataFrame:
    rows = []
    base_loss = mean_loss(y, base)
    for method_i, method in enumerate(method_names):
        for group in GROUPS:
            for strength in STRENGTHS:
                for scale in SCALES:
                    pred = apply_count_solver(base, records, method, group, strength, scale)
                    oof = mean_loss(y, pred)
                    row = {
                        "cv_mode": cv_mode,
                        "method": method,
                        "group": group,
                        "strength": strength,
                        "scale": scale,
                        "oof_loss": oof,
                        "oof_delta_vs_stage2": oof - base_loss,
                    }
                    for j, target in enumerate(TARGETS):
                        row[f"loss_{target}"] = loss_col(y[:, j], pred[:, j])
                    rows.append(row)
        if (method_i + 1) % 8 == 0:
            print(f"tecount scan {cv_mode}: methods={method_i + 1}/{len(method_names)}", flush=True)
    return pd.DataFrame(rows).sort_values(["oof_loss", "oof_delta_vs_stage2"]).reset_index(drop=True)


def emit_top_submissions(
    scan: pd.DataFrame,
    sub_records: list[BlockRecord],
    base_sub_df: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    base_sub = base_sub_df[TARGETS].to_numpy(dtype=float)
    emitted = []
    seen = set()
    for row in scan.itertuples(index=False):
        key = (str(row.method), str(row.group), float(row.strength), float(row.scale))
        if key in seen:
            continue
        seen.add(key)
        if len(emitted) >= top_n:
            break
        sub_pred = apply_count_solver(base_sub, sub_records, str(row.method), str(row.group), float(row.strength), float(row.scale))
        file_name = (
            "submission_transductive_episode_count_jepa"
            f"_{str(row.cv_mode)}"
            f"_{str(row.method)}"
            f"_{str(row.group)}"
            f"_st{str(row.strength).replace('.', 'p')}"
            f"_sc{str(row.scale).replace('.', 'p')}.csv"
        )
        safe_name = file_name.replace("/", "_").replace("+", "p")
        out = base_sub_df.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / safe_name, index=False)
        emitted.append(
            {
                "candidate": safe_name,
                "cv_mode": str(row.cv_mode),
                "method": str(row.method),
                "group": str(row.group),
                "strength": float(row.strength),
                "scale": float(row.scale),
                "oof_loss": float(row.oof_loss),
                "oof_delta_vs_stage2": float(row.oof_delta_vs_stage2),
                **candidate_axis(base_sub_df, safe_name),
            }
        )
    return pd.DataFrame(emitted)


def write_report(chunk_scan: pd.DataFrame, geom_scan: pd.DataFrame, candidates: pd.DataFrame) -> None:
    lines = [
        "# Transductive Episode Count JEPA",
        "",
        "This is a stronger JEPA use than residual features: predict a hidden episode's 7-label block rate first, then solve row-level probabilities so each block matches that latent count/rate.",
        "",
        "Rate estimators tested:",
        "- observed raw block descriptor retrieval",
        "- context-predicted block descriptor retrieval",
        "- actual/predicted descriptor mixtures",
        "- strict label-context descriptors",
        "- ridge, KNN, semantic prototype, and prior blends",
        "",
        "## Subject-Chunk CV Top",
        "",
        chunk_scan.head(40).to_csv(index=False),
        "",
        "## Geometry CV Top",
        "",
        geom_scan.head(40).to_csv(index=False),
        "",
        "## Emitted Candidates",
        "",
        candidates.to_csv(index=False),
    ]
    (OUT / "transductive_episode_count_jepa_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    repeats = int(os.environ.get("TECOUNT_GEOM_REPEATS", "5"))
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y_full = adv.train_label_matrix(rows, train)
    y_train = train[TARGETS].to_numpy(dtype=int)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)

    chunk_records = build_oof_records(train, sub, rows, z, y_full, base_all, cv_mode="subject_chunk", repeats=repeats)
    geom_records = build_oof_records(train, sub, rows, z, y_full, base_all, cv_mode="geometry", repeats=repeats)
    method_names = sorted(chunk_records[0].methods.keys())

    chunk_scan = scan_candidates(chunk_records, base, y_train, method_names, cv_mode="subject_chunk")
    chunk_scan.to_csv(OUT / "transductive_episode_count_jepa_subject_chunk_scan.csv", index=False)

    geom_covered = sorted(set(np.concatenate([r.indices for r in geom_records]))) if geom_records else []
    if geom_covered:
        geom_base = base[geom_covered]
        geom_y = y_train[geom_covered]
        remapped = []
        pos_map = {idx: pos for pos, idx in enumerate(geom_covered)}
        for rec in geom_records:
            remapped.append(BlockRecord(indices=np.array([pos_map[int(i)] for i in rec.indices], dtype=int), methods=rec.methods))
        geom_scan = scan_candidates(remapped, geom_base, geom_y, method_names, cv_mode="geometry")
    else:
        geom_scan = pd.DataFrame()
    geom_scan.to_csv(OUT / "transductive_episode_count_jepa_geometry_scan.csv", index=False)

    sub_records = build_submission_records(train, sub, rows, z, y_full, base_all)
    # Emit both aggressive subject-chunk winners and geometry winners because their error modes differ.
    chunk_top = chunk_scan.head(18)
    geom_top = geom_scan.head(12) if not geom_scan.empty else pd.DataFrame()
    combined_scan = pd.concat([chunk_top, geom_top], ignore_index=True).drop_duplicates(
        ["cv_mode", "method", "group", "strength", "scale"]
    )
    candidates = emit_top_submissions(combined_scan, sub_records, base_sub, top_n=30)
    candidates.to_csv(OUT / "transductive_episode_count_jepa_candidate_summary.csv", index=False)
    write_report(chunk_scan, geom_scan, candidates)

    print("TECOUNT candidates")
    print(candidates.to_string(index=False), flush=True)
    print("TECOUNT subject_chunk top")
    print(chunk_scan.head(20).to_string(index=False), flush=True)
    if not geom_scan.empty:
        print("TECOUNT geometry top")
        print(geom_scan.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
