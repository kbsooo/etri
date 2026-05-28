from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
RAW05_SUB = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
PARETO_SUB = OUT / "submission_hiddenblock_paretomix_w0.3_b7621063.csv"


@dataclass(frozen=True)
class Block:
    block_id: str
    subject_id: str
    positions: np.ndarray
    split: str
    start: pd.Timestamp
    end: pd.Timestamp

    @property
    def n(self) -> int:
        return int(len(self.positions))


@dataclass
class FeaturePack:
    raw: np.ndarray
    ctx: np.ndarray
    full: np.ndarray
    info: dict[str, np.ndarray | float | str]


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray | float) -> np.ndarray:
    p = clip(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def len_bin(n: int) -> str:
    if n <= 2:
        return "1-2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    return "11-16"


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def read_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return train.sort_values(SORT_KEY).reset_index(drop=True), sample.sort_values(KEY).reset_index(drop=True)


def all_rows(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    tr = train[KEY].copy()
    tr["split"] = "train"
    tr["train_idx"] = np.arange(len(train))
    tr["sub_idx"] = -1
    su = sample[KEY].copy()
    su["split"] = "submission"
    su["train_idx"] = -1
    su["sub_idx"] = np.arange(len(sample))
    rows = pd.concat([tr, su], ignore_index=True).sort_values(SORT_KEY).reset_index(drop=True)
    rows["global_pos"] = np.arange(len(rows))
    rows["subject_id"] = rows["subject_id"].astype(str)
    rows["subject_pos"] = rows.groupby("subject_id", sort=False).cumcount()
    rows["subject_count"] = rows.groupby("subject_id", sort=False)["subject_id"].transform("size")
    rows["subject_phase"] = rows["subject_pos"] / np.maximum(rows["subject_count"] - 1, 1)
    rows["dow"] = rows["lifelog_date"].dt.dayofweek.astype(float)
    rows["dow_sin"] = np.sin(2.0 * np.pi * rows["dow"] / 7.0)
    rows["dow_cos"] = np.cos(2.0 * np.pi * rows["dow"] / 7.0)
    rows["is_weekend"] = (rows["dow"] >= 5).astype(float)
    return rows


def train_label_matrix(rows: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    y = np.full((len(rows), len(TARGETS)), np.nan, dtype=np.float64)
    mask = rows["split"].eq("train").to_numpy()
    idx = rows.loc[mask, "train_idx"].to_numpy(dtype=int)
    y[mask] = train.loc[idx, TARGETS].to_numpy(dtype=np.float64)
    return y


def add_prediction_features(frame: pd.DataFrame, rows: pd.DataFrame, train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    sources: list[tuple[str, Path | None, Path | None]] = [
        ("stage2", BASE_OOF, BASE_SUB),
        ("jepa_selected", JEPA / "jepa_selected_oof.npy", JEPA / "submission_jepa_selected.csv"),
        ("neural_jepa", JEPA / "neural_jepa_oof.npy", JEPA / "submission_neural_jepa_selected.csv"),
        ("rawijepa", JEPA / "rawijepa_oof.npy", JEPA / "submission_rawijepa_selected.csv"),
    ]
    train_key = train[KEY].reset_index(drop=True)
    sample_key = sample[KEY].reset_index(drop=True)
    for prefix, train_path, sub_path in sources:
        if train_path is None or sub_path is None or not train_path.exists() or not sub_path.exists():
            continue
        train_pred = np.load(train_path)
        sub_frame = pd.read_csv(sub_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        if train_pred.shape != (len(train), len(TARGETS)):
            continue
        if not sub_frame[KEY].equals(sample_key):
            raise ValueError(f"submission key mismatch: {sub_path}")
        vals = np.full((len(rows), len(TARGETS)), np.nan, dtype=np.float64)
        tr_mask = rows["split"].eq("train").to_numpy()
        su_mask = rows["split"].eq("submission").to_numpy()
        vals[tr_mask] = train_pred[rows.loc[tr_mask, "train_idx"].to_numpy(dtype=int)]
        vals[su_mask] = sub_frame.loc[rows.loc[su_mask, "sub_idx"].to_numpy(dtype=int), TARGETS].to_numpy(dtype=np.float64)
        if not train_key.equals(train[KEY].reset_index(drop=True)):
            raise ValueError("train key changed unexpectedly")
        for j, target in enumerate(TARGETS):
            frame[f"{prefix}_p_{target}"] = clip(vals[:, j])
            frame[f"{prefix}_logit_{target}"] = logit(vals[:, j])
    return frame


def add_pca_source(
    frame: pd.DataFrame,
    rows: pd.DataFrame,
    path: Path,
    prefix: str,
    n_components: int,
    sub_path: Path | None = None,
) -> pd.DataFrame:
    if not path.exists():
        return frame
    if sub_path is not None and not sub_path.exists():
        return frame
    if sub_path is None:
        src = read_table(path)
    else:
        src = pd.concat([read_table(path), read_table(sub_path)], ignore_index=True)
    src = src.copy()
    src["subject_id"] = src["subject_id"].astype(str)
    keys = KEY if "sleep_date" in src.columns else ["subject_id", "lifelog_date"]
    drop = set(TARGETS + ["split"])
    numeric_cols = []
    for col in src.columns:
        if col in set(keys) | drop:
            continue
        s = pd.to_numeric(src[col], errors="coerce")
        if s.notna().sum() >= 100 and s.nunique(dropna=True) > 1:
            numeric_cols.append(col)
    if len(numeric_cols) < 2:
        return frame
    src_small = src[keys + numeric_cols].copy()
    base = rows[keys].copy()
    merged = base.merge(src_small, on=keys, how="left")
    vals = merged[numeric_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    nan_frac = vals.isna().mean(axis=1).to_numpy(dtype=np.float64)
    med = vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float64)
    x = StandardScaler().fit_transform(x)
    k = min(n_components, x.shape[0] - 1, x.shape[1])
    if k < 1:
        return frame
    z = PCA(n_components=k, svd_solver="randomized", random_state=260991).fit_transform(x)
    add = pd.DataFrame({f"{prefix}_pc{i:02d}": z[:, i] for i in range(k)})
    add[f"{prefix}_nan_frac"] = nan_frac
    return pd.concat([frame.reset_index(drop=True), add.reset_index(drop=True)], axis=1)


def build_row_matrix(train: pd.DataFrame, sample: pd.DataFrame, rows: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    frame = rows[
        KEY
        + [
            "split",
            "train_idx",
            "sub_idx",
            "global_pos",
            "subject_pos",
            "subject_count",
            "subject_phase",
            "dow",
            "dow_sin",
            "dow_cos",
            "is_weekend",
        ]
    ].copy()
    frame = add_prediction_features(frame, rows, train, sample)
    source_specs = [
        (JEPA / "raw_timeline_jepa_rescue_train_features.parquet", "rawtimeline", 32, JEPA / "raw_timeline_jepa_rescue_submission_features.parquet"),
        (JEPA / "episode_retrieval_jepa_train_features.parquet", "episode", 32, JEPA / "episode_retrieval_jepa_submission_features.parquet"),
        (JEPA / "block_canvas_jepa_train_features.parquet", "blockcanvas", 32, JEPA / "block_canvas_jepa_submission_features.parquet"),
        (JEPA / "neural_block_canvas_jepa_mps_train_features.parquet", "neuralblock", 24, JEPA / "neural_block_canvas_jepa_mps_submission_features.parquet"),
        (JEPA / "subject_episode_graph_jepa_train_features.parquet", "subgraph", 20, JEPA / "subject_episode_graph_jepa_submission_features.parquet"),
        (OUT / "deep_sensor_features.parquet", "deepsensor", 48, None),
    ]
    for path, prefix, k, sub_path in source_specs:
        frame = add_pca_source(frame, rows, path, prefix, k, sub_path)
    num_cols = [
        c
        for c in frame.columns
        if c not in set(KEY + ["split", "train_idx", "sub_idx"])
        and pd.api.types.is_numeric_dtype(frame[c])
    ]
    vals = frame[num_cols].replace([np.inf, -np.inf], np.nan)
    med = vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float64)
    x = StandardScaler().fit_transform(x)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return frame, x.astype(np.float32)


def hidden_lengths_by_subject(blocks: pd.DataFrame) -> dict[str, list[int]]:
    hidden = blocks[blocks["split"].eq("submission")].copy()
    out: dict[str, list[int]] = {}
    for sid, g in hidden.groupby("subject_id", sort=False):
        out[str(sid)] = sorted({int(x) for x in g["n"].tolist()})
    return out


def make_pseudo_blocks(rows: pd.DataFrame) -> list[Block]:
    split_blocks = pd.read_csv(OUT / "breakthrough_split_blocks.csv")
    lengths = hidden_lengths_by_subject(split_blocks)
    blocks: list[Block] = []
    for sid, g in rows[rows["split"].eq("train")].groupby("subject_id", sort=False):
        pos = g["global_pos"].to_numpy(dtype=int)
        dates = pd.to_datetime(g["lifelog_date"]).reset_index(drop=True)
        sid_lengths = sorted(set(lengths.get(str(sid), [])))
        sid_blocks: list[Block] = []
        for length in sid_lengths:
            if length > len(pos):
                continue
            stride = max(1, length // 2)
            starts = list(range(0, len(pos) - length + 1, stride))
            if starts[-1] != len(pos) - length:
                starts.append(len(pos) - length)
            for start in starts:
                bpos = pos[start : start + length]
                sid_blocks.append(
                    Block(
                        block_id=f"pseudo_{sid}_l{length}_s{start}",
                        subject_id=str(sid),
                        positions=bpos,
                        split="pseudo",
                        start=pd.Timestamp(dates.iloc[start]),
                        end=pd.Timestamp(dates.iloc[start + length - 1]),
                    )
                )
        if len(sid_blocks) > 80:
            take = np.linspace(0, len(sid_blocks) - 1, 80).round().astype(int)
            sid_blocks = [sid_blocks[int(i)] for i in take]
        blocks.extend(sid_blocks)
    return blocks


def make_hidden_blocks(rows: pd.DataFrame) -> list[Block]:
    out: list[Block] = []
    for sid, g in rows.groupby("subject_id", sort=False):
        split = g["split"].to_numpy()
        pos = g["global_pos"].to_numpy(dtype=int)
        dates = pd.to_datetime(g["lifelog_date"]).reset_index(drop=True)
        start = 0
        block_num = 1
        while start < len(g):
            end = start + 1
            while end < len(g) and split[end] == split[start]:
                end += 1
            if split[start] == "submission":
                out.append(
                    Block(
                        block_id=f"{sid}_b{block_num}",
                        subject_id=str(sid),
                        positions=pos[start:end],
                        split="hidden",
                        start=pd.Timestamp(dates.iloc[start]),
                        end=pd.Timestamp(dates.iloc[end - 1]),
                    )
                )
            block_num += 1
            start = end
    return out


def base_known_mask(rows: pd.DataFrame) -> np.ndarray:
    return rows["split"].eq("train").to_numpy()


def context_info(rows: pd.DataFrame, y: np.ndarray, positions: np.ndarray, known_mask: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray | float | str]]:
    block_set = set(int(p) for p in positions)
    sid = str(rows.iloc[int(positions[0])]["subject_id"])
    subject_mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
    known_subject = np.array(
        [i for i in np.where(subject_mask & known_mask)[0] if i not in block_set],
        dtype=int,
    )
    known_all = np.where(known_mask)[0]
    before = known_subject[known_subject < positions.min()]
    after = known_subject[known_subject > positions.max()]
    prev = y[before[-1]] if len(before) else np.full(len(TARGETS), np.nan)
    nxt = y[after[0]] if len(after) else np.full(len(TARGETS), np.nan)
    subj_vals = y[known_subject] if len(known_subject) else np.empty((0, len(TARGETS)))
    all_vals = y[known_all] if len(known_all) else np.empty((0, len(TARGETS)))
    subject_mean = np.nanmean(subj_vals, axis=0) if len(subj_vals) else np.nanmean(all_vals, axis=0)
    global_mean = np.nanmean(all_vals, axis=0)
    subject_mean = np.nan_to_num(subject_mean, nan=global_mean)
    global_mean = np.nan_to_num(global_mean, nan=0.5)

    def tail_mean(idxs: np.ndarray, n: int) -> np.ndarray:
        if len(idxs) == 0:
            return subject_mean.copy()
        return np.nan_to_num(np.nanmean(y[idxs[-n:]], axis=0), nan=subject_mean)

    def head_mean(idxs: np.ndarray, n: int) -> np.ndarray:
        if len(idxs) == 0:
            return subject_mean.copy()
        return np.nan_to_num(np.nanmean(y[idxs[:n]], axis=0), nan=subject_mean)

    before3 = tail_mean(before, 3)
    before5 = tail_mean(before, 5)
    after3 = head_mean(after, 3)
    after5 = head_mean(after, 5)
    prev_fill = np.where(np.isfinite(prev), prev, subject_mean)
    next_fill = np.where(np.isfinite(nxt), nxt, subject_mean)
    has_prev = np.isfinite(prev).astype(float)
    has_next = np.isfinite(nxt).astype(float)
    row_block = rows.iloc[positions]
    gap_prev = float(positions.min() - before[-1]) if len(before) else 99.0
    gap_next = float(after[0] - positions.max()) if len(after) else 99.0
    geom = np.array(
        [
            len(positions),
            row_block["subject_phase"].mean(),
            row_block["subject_phase"].min(),
            row_block["subject_phase"].max(),
            row_block["dow_sin"].mean(),
            row_block["dow_cos"].mean(),
            row_block["is_weekend"].mean(),
            gap_prev,
            gap_next,
            float(len(before)),
            float(len(after)),
            float(len(known_subject)),
        ],
        dtype=np.float64,
    )
    label_feats = np.concatenate(
        [
            global_mean,
            subject_mean,
            prev_fill,
            next_fill,
            before3,
            before5,
            after3,
            after5,
            0.5 * (prev_fill + next_fill),
            next_fill - prev_fill,
            subject_mean - global_mean,
            has_prev,
            has_next,
        ]
    )
    vec = np.nan_to_num(np.concatenate([geom, label_feats]), nan=0.0, posinf=0.0, neginf=0.0)
    info: dict[str, np.ndarray | float | str] = {
        "subject_id": sid,
        "len_bin": len_bin(len(positions)),
        "subject_mean": clip(subject_mean),
        "global_mean": clip(global_mean),
        "prev": prev,
        "next": nxt,
        "prev_fill": clip(prev_fill),
        "next_fill": clip(next_fill),
        "has_prev": has_prev,
        "has_next": has_next,
    }
    return vec.astype(np.float32), info


def raw_block_vector(rows: pd.DataFrame, row_x: np.ndarray, positions: np.ndarray) -> np.ndarray:
    xb = row_x[positions]
    if len(positions) > 1:
        slope = (xb[-1] - xb[0]) / float(len(positions) - 1)
    else:
        slope = np.zeros(row_x.shape[1], dtype=np.float32)
    stats = [
        np.nanmean(xb, axis=0),
        np.nanstd(xb, axis=0),
        np.nanmin(xb, axis=0),
        np.nanmax(xb, axis=0),
        xb[0],
        xb[-1],
        slope,
    ]
    geom = rows.iloc[positions][["subject_phase", "dow_sin", "dow_cos", "is_weekend"]].mean().to_numpy(dtype=np.float64)
    out = np.concatenate([np.array([len(positions)], dtype=np.float64), geom] + [s.astype(np.float64) for s in stats])
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)


def make_feature_pack(rows: pd.DataFrame, row_x: np.ndarray, y: np.ndarray, block: Block, known_mask: np.ndarray) -> FeaturePack:
    raw = raw_block_vector(rows, row_x, block.positions)
    ctx, info = context_info(rows, y, block.positions, known_mask)
    return FeaturePack(raw=raw, ctx=ctx, full=np.concatenate([raw, ctx]).astype(np.float32), info=info)


def true_rates(y: np.ndarray, blocks: list[Block]) -> np.ndarray:
    return np.vstack([np.nanmean(y[b.positions], axis=0) for b in blocks]).astype(np.float64)


def block_logloss(y_block: np.ndarray, rate: np.ndarray) -> float:
    p = clip(rate)
    ce = -(y_block * np.log(p) + (1.0 - y_block) * np.log(1.0 - p))
    return float(np.nanmean(ce))


def weighted_logloss(y: np.ndarray, blocks: list[Block], pred: np.ndarray) -> float:
    losses = []
    weights = []
    for i, b in enumerate(blocks):
        losses.append(block_logloss(y[b.positions], pred[i]))
        weights.append(len(b.positions))
    return float(np.average(losses, weights=weights))


def target_logloss(y: np.ndarray, blocks: list[Block], pred: np.ndarray, j: int) -> float:
    num = 0.0
    den = 0
    for i, b in enumerate(blocks):
        labels = y[b.positions, j]
        p = clip(pred[i, j])
        num += float((-(labels * np.log(p) + (1.0 - labels) * np.log(1.0 - p))).sum())
        den += len(labels)
    return float(num / max(den, 1))


def donor_mask(blocks: list[Block], i: int, mode: str) -> np.ndarray:
    target = blocks[i]
    target_set = set(int(p) for p in target.positions)
    keep = []
    for k, block in enumerate(blocks):
        if k == i:
            keep.append(False)
            continue
        if mode == "strict_subject" and block.subject_id == target.subject_id:
            keep.append(False)
            continue
        if target_set.intersection(int(p) for p in block.positions):
            keep.append(False)
            continue
        keep.append(True)
    return np.asarray(keep, dtype=bool)


def endpoint_predict(
    i: int,
    blocks: list[Block],
    features: list[FeaturePack],
    rates: np.ndarray,
    mode: str,
    shrink: float = 32.0,
) -> np.ndarray:
    donors = donor_mask(blocks, i, mode)
    pred = np.asarray(features[i].info["subject_mean"], dtype=np.float64).copy()
    info = features[i].info
    prev = np.asarray(info["prev"], dtype=np.float64)
    nxt = np.asarray(info["next"], dtype=np.float64)
    for j in range(len(TARGETS)):
        candidates = donors.copy()
        candidates &= np.array([features[k].info["len_bin"] == info["len_bin"] for k in range(len(blocks))], dtype=bool)
        if np.isfinite(prev[j]):
            candidates &= np.array([np.isfinite(np.asarray(features[k].info["prev"])[j]) and int(np.asarray(features[k].info["prev"])[j]) == int(prev[j]) for k in range(len(blocks))])
        if np.isfinite(nxt[j]):
            candidates &= np.array([np.isfinite(np.asarray(features[k].info["next"])[j]) and int(np.asarray(features[k].info["next"])[j]) == int(nxt[j]) for k in range(len(blocks))])
        idx = np.where(candidates)[0]
        if len(idx) < 4:
            candidates = donors.copy()
            if np.isfinite(prev[j]):
                candidates &= np.array([np.isfinite(np.asarray(features[k].info["prev"])[j]) and int(np.asarray(features[k].info["prev"])[j]) == int(prev[j]) for k in range(len(blocks))])
            if np.isfinite(nxt[j]):
                candidates &= np.array([np.isfinite(np.asarray(features[k].info["next"])[j]) and int(np.asarray(features[k].info["next"])[j]) == int(nxt[j]) for k in range(len(blocks))])
            idx = np.where(candidates)[0]
        if len(idx) < 4 and np.isfinite(prev[j]):
            candidates = donors & np.array([np.isfinite(np.asarray(features[k].info["prev"])[j]) and int(np.asarray(features[k].info["prev"])[j]) == int(prev[j]) for k in range(len(blocks))])
            idx = np.where(candidates)[0]
        if len(idx):
            local = float(np.mean(rates[idx, j]))
            pred[j] = (len(idx) * local + shrink * pred[j]) / (len(idx) + shrink)
    return clip(pred)


def transition_matrix(rows: pd.DataFrame, y: np.ndarray, target_j: int, exclude_positions: set[int], exclude_subject: str | None) -> np.ndarray:
    counts = np.ones((2, 2), dtype=np.float64)
    train_rows = rows[rows["split"].eq("train")]
    for sid, g in train_rows.groupby("subject_id", sort=False):
        if exclude_subject is not None and str(sid) == exclude_subject:
            continue
        pos = g["global_pos"].to_numpy(dtype=int)
        usable = [int(p) for p in pos if int(p) not in exclude_positions and np.isfinite(y[int(p), target_j])]
        for a, b in zip(usable[:-1], usable[1:]):
            counts[int(y[a, target_j]), int(y[b, target_j])] += 1.0
    return counts / counts.sum(axis=1, keepdims=True)


def bridge_rate(prev: float, nxt: float, length: int, trans: np.ndarray, fallback: float) -> float:
    if length <= 0:
        return float(fallback)
    if np.isfinite(prev) and np.isfinite(nxt):
        a = int(prev)
        b = int(nxt)
        denom = np.linalg.matrix_power(trans, length + 1)[a, b]
        if denom <= 1e-12:
            return float(fallback)
        total = 0.0
        for t in range(1, length + 1):
            left = np.linalg.matrix_power(trans, t)[a]
            right = np.linalg.matrix_power(trans, length + 1 - t)[:, b]
            total += float(left[1] * right[1] / denom)
        return total / float(length)
    if np.isfinite(prev):
        dist = np.array([1.0 - int(prev), int(prev)], dtype=np.float64)
        total = 0.0
        for _ in range(length):
            dist = dist @ trans
            total += float(dist[1])
        return total / float(length)
    if np.isfinite(nxt):
        rev = trans / np.maximum(trans.sum(axis=0, keepdims=True), 1e-12)
        dist = np.array([1.0 - int(nxt), int(nxt)], dtype=np.float64)
        total = 0.0
        for _ in range(length):
            dist = dist @ rev.T
            total += float(dist[1])
        return total / float(length)
    return float(fallback)


def markov_predict(i: int, rows: pd.DataFrame, y: np.ndarray, blocks: list[Block], features: list[FeaturePack], mode: str) -> np.ndarray:
    block = blocks[i]
    exclude = {int(p) for p in block.positions}
    exclude_subject = block.subject_id if mode == "strict_subject" else None
    info = features[i].info
    prev = np.asarray(info["prev"], dtype=np.float64)
    nxt = np.asarray(info["next"], dtype=np.float64)
    fallback = np.asarray(info["subject_mean"], dtype=np.float64)
    out = np.zeros(len(TARGETS), dtype=np.float64)
    for j in range(len(TARGETS)):
        trans = transition_matrix(rows, y, j, exclude, exclude_subject)
        out[j] = bridge_rate(prev[j], nxt[j], block.n, trans, fallback[j])
        out[j] = 0.75 * out[j] + 0.25 * fallback[j]
    return clip(out)


def knn_predict(X: np.ndarray, rates: np.ndarray, xi: np.ndarray, donors: np.ndarray, k: int) -> np.ndarray:
    idx = np.where(donors)[0]
    if len(idx) == 0:
        return np.full(len(TARGETS), 0.5, dtype=np.float64)
    scaler = StandardScaler()
    xd = scaler.fit_transform(X[idx])
    xv = scaler.transform(xi.reshape(1, -1))[0]
    dist = np.sqrt(np.maximum(((xd - xv) ** 2).mean(axis=1), 0.0))
    order = np.argsort(dist)[: min(k, len(idx))]
    d = dist[order]
    weights = 1.0 / np.maximum(d, 1e-3)
    weights = weights / weights.sum()
    return clip(weights @ rates[idx[order]])


def ridge_predict(X: np.ndarray, rates: np.ndarray, xi: np.ndarray, donors: np.ndarray, alpha: float) -> np.ndarray:
    idx = np.where(donors)[0]
    if len(idx) < 12:
        return np.full(len(TARGETS), 0.5, dtype=np.float64)
    scaler = StandardScaler()
    xd = scaler.fit_transform(X[idx])
    xv = scaler.transform(xi.reshape(1, -1))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xd, rates[idx])
    return clip(model.predict(xv)[0])


def evaluate_methods(rows: pd.DataFrame, y: np.ndarray, blocks: list[Block], features: list[FeaturePack]) -> dict[str, np.ndarray]:
    rates = true_rates(y, blocks)
    raw_x = np.vstack([f.raw for f in features])
    full_x = np.vstack([f.full for f in features])
    preds: dict[str, np.ndarray] = {
        "global_mean": np.vstack([np.asarray(f.info["global_mean"], dtype=np.float64) for f in features]),
        "subject_mean": np.vstack([np.asarray(f.info["subject_mean"], dtype=np.float64) for f in features]),
    }
    for mode in ["strict_subject", "local_nonoverlap"]:
        preds[f"endpoint_{mode}"] = np.vstack([endpoint_predict(i, blocks, features, rates, mode) for i in range(len(blocks))])
        preds[f"markov_{mode}"] = np.vstack([markov_predict(i, rows, y, blocks, features, mode) for i in range(len(blocks))])
        for k in [8]:
            arr_raw = []
            arr_full = []
            for i in range(len(blocks)):
                donors = donor_mask(blocks, i, mode)
                arr_raw.append(knn_predict(raw_x, rates, raw_x[i], donors, k))
                arr_full.append(knn_predict(full_x, rates, full_x[i], donors, k))
            preds[f"knn_raw_{mode}_k{k}"] = np.vstack(arr_raw)
            preds[f"knn_full_{mode}_k{k}"] = np.vstack(arr_full)
    return preds


def summarize_predictions(y: np.ndarray, blocks: list[Block], true_rate: np.ndarray, preds: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    subject_loss = weighted_logloss(y, blocks, preds["subject_mean"])
    rows = []
    target_rows = []
    lengths = np.asarray([b.n for b in blocks], dtype=np.float64)
    for name, pred in preds.items():
        err = pred - true_rate
        sse = float(np.sum((err ** 2) * lengths[:, None]))
        sst = float(np.sum(((true_rate - np.average(true_rate, axis=0, weights=lengths)) ** 2) * lengths[:, None]))
        row_loss = weighted_logloss(y, blocks, pred)
        rows.append(
            {
                "method": name,
                "blocks": len(blocks),
                "weighted_logloss": row_loss,
                "delta_vs_subject_mean": row_loss - subject_loss,
                "rate_rmse_weighted": float(np.sqrt(np.average(err ** 2, weights=lengths, axis=0).mean())),
                "rate_mae_weighted": float(np.average(np.abs(err), weights=lengths, axis=0).mean()),
                "count_mae_mean": float(np.mean(np.abs(err * lengths[:, None]))),
                "rate_r2_weighted": float(1.0 - sse / max(sst, 1e-12)),
            }
        )
        for j, target in enumerate(TARGETS):
            target_rows.append(
                {
                    "method": name,
                    "target": target,
                    "target_logloss": target_logloss(y, blocks, pred, j),
                    "target_delta_vs_subject_mean": target_logloss(y, blocks, pred, j)
                    - target_logloss(y, blocks, preds["subject_mean"], j),
                    "target_rate_rmse": float(np.sqrt(np.average(err[:, j] ** 2, weights=lengths))),
                    "target_count_mae": float(np.average(np.abs(err[:, j] * lengths), weights=np.ones_like(lengths))),
                }
            )
    return (
        pd.DataFrame(rows).sort_values(["weighted_logloss", "rate_rmse_weighted"]).reset_index(drop=True),
        pd.DataFrame(target_rows).sort_values(["target", "target_logloss"]).reset_index(drop=True),
    )


def final_hidden_prediction(
    method: str,
    train_blocks: list[Block],
    train_features: list[FeaturePack],
    train_rates: np.ndarray,
    hidden_blocks: list[Block],
    hidden_features: list[FeaturePack],
    rows: pd.DataFrame,
    y: np.ndarray,
) -> np.ndarray:
    raw_x = np.vstack([f.raw for f in train_features])
    full_x = np.vstack([f.full for f in train_features])
    hidden_raw = np.vstack([f.raw for f in hidden_features])
    hidden_full = np.vstack([f.full for f in hidden_features])
    out = []
    if method.startswith("endpoint_"):
        mode = method.removeprefix("endpoint_")
        all_blocks = train_blocks + hidden_blocks
        all_features = train_features + hidden_features
        all_rates = np.vstack([train_rates, np.full((len(hidden_blocks), len(TARGETS)), np.nan)])
        for h in range(len(hidden_blocks)):
            i = len(train_blocks) + h
            donors = np.ones(len(all_blocks), dtype=bool)
            donors[len(train_blocks) :] = False
            if mode == "strict_subject":
                sid = hidden_blocks[h].subject_id
                donors[: len(train_blocks)] &= np.array([b.subject_id != sid for b in train_blocks])
            pred = np.asarray(all_features[i].info["subject_mean"], dtype=np.float64).copy()
            info = all_features[i].info
            prev = np.asarray(info["prev"], dtype=np.float64)
            nxt = np.asarray(info["next"], dtype=np.float64)
            for j in range(len(TARGETS)):
                candidates = donors.copy()
                candidates &= np.array([all_features[k].info["len_bin"] == info["len_bin"] for k in range(len(all_blocks))], dtype=bool)
                if np.isfinite(prev[j]):
                    candidates &= np.array([np.isfinite(np.asarray(all_features[k].info["prev"])[j]) and int(np.asarray(all_features[k].info["prev"])[j]) == int(prev[j]) for k in range(len(all_blocks))])
                if np.isfinite(nxt[j]):
                    candidates &= np.array([np.isfinite(np.asarray(all_features[k].info["next"])[j]) and int(np.asarray(all_features[k].info["next"])[j]) == int(nxt[j]) for k in range(len(all_blocks))])
                idx = np.where(candidates[: len(train_blocks)])[0]
                if len(idx):
                    local = float(np.nanmean(train_rates[idx, j]))
                    pred[j] = (len(idx) * local + 32.0 * pred[j]) / (len(idx) + 32.0)
            out.append(clip(pred))
        return np.vstack(out)
    if method.startswith("markov_"):
        mode = method.removeprefix("markov_")
        for h, block in enumerate(hidden_blocks):
            info = hidden_features[h].info
            prev = np.asarray(info["prev"], dtype=np.float64)
            nxt = np.asarray(info["next"], dtype=np.float64)
            fallback = np.asarray(info["subject_mean"], dtype=np.float64)
            pred = np.zeros(len(TARGETS), dtype=np.float64)
            exclude_subject = block.subject_id if mode == "strict_subject" else None
            for j in range(len(TARGETS)):
                trans = transition_matrix(rows, y, j, set(), exclude_subject)
                pred[j] = 0.75 * bridge_rate(prev[j], nxt[j], block.n, trans, fallback[j]) + 0.25 * fallback[j]
            out.append(clip(pred))
        return np.vstack(out)
    if method.startswith("knn_"):
        parts = method.split("_")
        feature_kind = parts[1]
        mode = "_".join(parts[2:-1])
        k = int(parts[-1].removeprefix("k"))
        X = raw_x if feature_kind == "raw" else full_x
        H = hidden_raw if feature_kind == "raw" else hidden_full
        for h, block in enumerate(hidden_blocks):
            donors = np.ones(len(train_blocks), dtype=bool)
            if mode == "strict_subject":
                donors &= np.array([b.subject_id != block.subject_id for b in train_blocks])
            out.append(knn_predict(X, train_rates, H[h], donors, k))
        return np.vstack(out)
    if method.startswith("ridge_"):
        parts = method.split("_")
        feature_kind = parts[1]
        alpha = float(parts[-1].removeprefix("a").replace("p", "."))
        mode = "_".join(parts[2:-1])
        X = raw_x if feature_kind == "raw" else full_x
        H = hidden_raw if feature_kind == "raw" else hidden_full
        for h, block in enumerate(hidden_blocks):
            donors = np.ones(len(train_blocks), dtype=bool)
            if mode == "strict_subject":
                donors &= np.array([b.subject_id != block.subject_id for b in train_blocks])
            out.append(ridge_predict(X, train_rates, H[h], donors, alpha))
        return np.vstack(out)
    if method == "subject_mean":
        return np.vstack([np.asarray(f.info["subject_mean"], dtype=np.float64) for f in hidden_features])
    if method == "global_mean":
        return np.vstack([np.asarray(f.info["global_mean"], dtype=np.float64) for f in hidden_features])
    raise ValueError(f"unsupported method: {method}")


def load_submission(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def save_rate_candidate(
    base_path: Path,
    sample: pd.DataFrame,
    hidden_blocks: list[Block],
    rows: pd.DataFrame,
    hidden_rates: np.ndarray,
    method: str,
    weight: float,
    target_mask: np.ndarray,
) -> str:
    base = load_submission(base_path)
    if not base[KEY].equals(sample[KEY]):
        raise ValueError(f"base key mismatch: {base_path}")
    pred = base[TARGETS].to_numpy(dtype=np.float64)
    for block_i, block in enumerate(hidden_blocks):
        sub_idx = rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        for j in range(len(TARGETS)):
            if not target_mask[j]:
                continue
            pred[sub_idx, j] = clip(sigmoid((1.0 - weight) * logit(pred[sub_idx, j]) + weight * logit(hidden_rates[block_i, j])))
    out = base.copy()
    out[TARGETS] = pred
    base_tag = "raw05" if base_path == RAW05_SUB else "pareto03"
    wtag = str(weight).replace(".", "p")
    mtag = method.replace("strict_subject", "strict").replace("local_nonoverlap", "local").replace(".", "p")
    mask_tag = "".join(t.lower() for t, keep in zip(TARGETS, target_mask) if keep)
    name = f"submission_hiddenblock_rateprobe_{base_tag}_{mtag}_{mask_tag}_w{wtag}_{stable_tag(base_tag + method + mask_tag + str(weight))}.csv"
    out.to_csv(OUT / name, index=False)
    return name


def public_proxy_scores(files: list[str]) -> pd.DataFrame:
    if str(OUT) not in sys.path:
        sys.path.append(str(OUT))
    from hidden_block_latent_audit import expected_delta, load_predictions, projection_ratio, read_submission, sample_block_ids
    from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    posterior = clip(posterior)
    bad_axis = preds["jepa_bad_residual"] - preds["stage2"]
    ordinal_axis = preds["ordinal_q"] - preds["stage2"]
    rows_out = []
    for file_name in files:
        pred = read_submission(OUT / file_name)[TARGETS].to_numpy(dtype=np.float64)
        rows_out.append(
            {
                "file": file_name,
                "posterior_expected_public_vs_anchor": 0.5784273528 + expected_delta(posterior, pred, preds["anchor578"]),
                "raw_axis_expected_public_vs_stage2": 0.5779449757 + expected_delta(raw_q, pred, preds["stage2"]),
                "delta_vs_raw05_rawaxis": expected_delta(raw_q, pred, preds["stage2"]) - expected_delta(raw_q, preds["raw05"], preds["stage2"]),
                "bad_residual_axis_ratio": projection_ratio(pred - preds["stage2"], bad_axis),
                "ordinal_axis_ratio": projection_ratio(pred - preds["stage2"], ordinal_axis),
                "mean_abs_move_vs_raw05": float(np.abs(pred - preds["raw05"]).mean()),
                "min_prob": float(pred.min()),
                "max_prob": float(pred.max()),
            }
        )
    return pd.DataFrame(rows_out).sort_values(["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"])


def write_report(summary: pd.DataFrame, target_detail: pd.DataFrame, hidden_rates: pd.DataFrame, proxy: pd.DataFrame, saved: list[str]) -> None:
    lines = [
        "# Hidden Block Rate Reconstruction Audit",
        "",
        "JEPA framing used here: predict a hidden episode/block target representation (rate/count latent) from context and raw/prediction block features, not row-level reconstruction.",
        "",
        "## Best pseudo-hidden block methods",
        "",
        "```csv",
        summary.head(24).round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Target detail for best methods",
        "",
        "```csv",
        target_detail[target_detail["method"].isin(summary.head(8)["method"])].round(8).to_csv(index=False).strip(),
        "```",
        "",
        "## Hidden block rate predictions",
        "",
        "```csv",
        hidden_rates.head(40).round(6).to_csv(index=False).strip(),
        "```",
    ]
    if saved:
        lines.extend(
            [
                "",
                "## Saved rate-probe candidates",
                "",
                "\n".join(f"- `{name}`" for name in saved),
                "",
                "## Public-proxy scores for saved candidates",
                "",
                "```csv",
                proxy.round(10).to_csv(index=False).strip(),
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A useful hidden-block latent must beat `subject_mean` under pseudo-hidden block logloss, especially in the strict-subject setting.",
            "- If local/non-overlap wins but strict-subject does not, the signal is mainly subject-local and risky for public hidden blocks unless endpoint geometry agrees.",
            "- Candidates generated here are low-weight probes. They should be accepted only if public-axis and scenario robustness do not regress versus raw05/pareto anchors.",
        ]
    )
    (OUT / "hidden_block_rate_reconstruction_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train, sample = read_data()
    rows = all_rows(train, sample)
    y = train_label_matrix(rows, train)
    _frame, row_x = build_row_matrix(train, sample, rows)
    pseudo_blocks = make_pseudo_blocks(rows)
    hidden_blocks = make_hidden_blocks(rows)

    known = base_known_mask(rows)
    pseudo_features = []
    for block in pseudo_blocks:
        mask = known.copy()
        mask[block.positions] = False
        pseudo_features.append(make_feature_pack(rows, row_x, y, block, mask))
    hidden_features = [make_feature_pack(rows, row_x, y, block, known) for block in hidden_blocks]
    rates = true_rates(y, pseudo_blocks)

    preds = evaluate_methods(rows, y, pseudo_blocks, pseudo_features)
    summary, target_detail = summarize_predictions(y, pseudo_blocks, rates, preds)
    summary.to_csv(OUT / "hidden_block_rate_reconstruction_summary.csv", index=False)
    target_detail.to_csv(OUT / "hidden_block_rate_reconstruction_target_detail.csv", index=False)

    block_rows = []
    for i, block in enumerate(pseudo_blocks):
        rec = {
            "block_id": block.block_id,
            "subject_id": block.subject_id,
            "n_rows": block.n,
            "start": block.start.date().isoformat(),
            "end": block.end.date().isoformat(),
        }
        for j, target in enumerate(TARGETS):
            rec[f"true_rate_{target}"] = rates[i, j]
            rec[f"subject_mean_{target}"] = preds["subject_mean"][i, j]
        block_rows.append(rec)
    pd.DataFrame(block_rows).to_csv(OUT / "hidden_block_rate_reconstruction_pseudo_blocks.csv", index=False)

    best_methods = [
        m
        for m in summary["method"].tolist()
        if m not in {"global_mean", "subject_mean"} and ("strict_subject" in m or m.startswith("markov_local") or m.startswith("endpoint_local"))
    ][:5]
    hidden_rows = []
    hidden_rate_by_method: dict[str, np.ndarray] = {}
    for method in best_methods:
        hr = final_hidden_prediction(method, pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, rows, y)
        hidden_rate_by_method[method] = hr
        for i, block in enumerate(hidden_blocks):
            rec = {
                "method": method,
                "hidden_block_id": block.block_id,
                "subject_id": block.subject_id,
                "n_rows": block.n,
                "start": block.start.date().isoformat(),
                "end": block.end.date().isoformat(),
            }
            for j, target in enumerate(TARGETS):
                rec[f"rate_{target}"] = hr[i, j]
                rec[f"count_{target}"] = hr[i, j] * block.n
            hidden_rows.append(rec)
    hidden_rate_df = pd.DataFrame(hidden_rows)
    hidden_rate_df.to_csv(OUT / "hidden_block_rate_reconstruction_hidden_rates.csv", index=False)

    saved: list[str] = []
    best_nonbase = summary[~summary["method"].isin(["global_mean", "subject_mean"])].head(3)["method"].tolist()
    for method in best_nonbase:
        hr = hidden_rate_by_method.get(method)
        if hr is None:
            hr = final_hidden_prediction(method, pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, rows, y)
        td = target_detail[target_detail["method"].eq(method)].copy()
        keep = td.set_index("target").reindex(TARGETS)["target_delta_vs_subject_mean"].to_numpy(dtype=float) < -0.001
        if not keep.any():
            keep = np.ones(len(TARGETS), dtype=bool)
        for base_path in [RAW05_SUB, PARETO_SUB]:
            if not base_path.exists():
                continue
            for weight in [0.05, 0.10, 0.15]:
                saved.append(save_rate_candidate(base_path, sample, hidden_blocks, rows, hr, method, weight, keep))

    proxy = public_proxy_scores(saved) if saved else pd.DataFrame()
    if not proxy.empty:
        proxy.to_csv(OUT / "hidden_block_rate_reconstruction_candidate_proxy.csv", index=False)

    write_report(summary, target_detail, hidden_rate_df, proxy, saved)
    print("[hidden block rate reconstruction] pseudo blocks", len(pseudo_blocks), "hidden blocks", len(hidden_blocks))
    print(summary.head(18).round(8).to_string(index=False))
    if saved:
        print("[saved candidates]")
        print(proxy.head(18).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
