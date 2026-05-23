#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ensure_dirs


def q(path) -> str:
    return str(path).replace("'", "''")


def kmeans(x: np.ndarray, k: int, n_iter: int = 80, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = x.shape[0]
    centers = x[rng.choice(n, size=k, replace=False)].copy()
    labels = np.zeros(n, dtype=np.int64)
    for _ in range(n_iter):
        d2 = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = d2.argmin(axis=1)
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        for j in range(k):
            mask = labels == j
            if mask.any():
                centers[j] = x[mask].mean(axis=0)
            else:
                centers[j] = x[rng.integers(0, n)]
    return labels


def entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    out = 0.0
    for c in counts:
        if c:
            p = c / total
            out -= p * math.log(p)
    return out


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    src = FEATURE_DIR / "timebin_1h_features.parquet"
    out_csv = FEATURE_DIR / "behavioral_state_features_k8.csv"
    out_parquet = FEATURE_DIR / "behavioral_state_features_k8.parquet"

    rows = con.execute(f"SELECT * FROM read_parquet('{q(src)}') ORDER BY subject_id, lifelog_date, hour").fetchall()
    cols = [d[0] for d in con.description]
    id_idx = [cols.index("subject_id"), cols.index("lifelog_date"), cols.index("hour")]
    feat_cols = [c for c in cols if c not in {"subject_id", "lifelog_date", "hour"}]
    feat_idx = [cols.index(c) for c in feat_cols]

    ids = [(r[id_idx[0]], r[id_idx[1]], int(r[id_idx[2]])) for r in rows]
    x = np.array([[0.0 if r[i] is None else float(r[i]) for i in feat_idx] for r in rows], dtype=np.float64)
    # log-transform heavy-tailed count/sum channels, then z-score.
    for j, c in enumerate(feat_cols):
        if any(tok in c for tok in ["sum", "count", "_n_"]):
            x[:, j] = np.log1p(np.maximum(x[:, j], 0))
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd[sd == 0] = 1.0
    xz = (x - mu) / sd

    labels = kmeans(xz, k=8, seed=42)

    by_day: dict[tuple[str, str], list[tuple[int, int]]] = defaultdict(list)
    for (sid, date, hour), lab in zip(ids, labels):
        by_day[(sid, date)].append((hour, int(lab)))

    fieldnames = ["subject_id", "lifelog_date"] + [f"state_{i}_ratio" for i in range(8)] + [
        "state_entropy", "state_transition_count", "dominant_state", "night_state_entropy", "night_transition_count"
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (sid, date), seq in sorted(by_day.items()):
            seq = sorted(seq)
            labs = [lab for _, lab in seq]
            counts = Counter(labs)
            night_labs = [lab for h, lab in seq if h >= 21 or h <= 5]
            transitions = sum(1 for a, b in zip(labs, labs[1:]) if a != b)
            night_transitions = sum(1 for a, b in zip(night_labs, night_labs[1:]) if a != b)
            row = {"subject_id": sid, "lifelog_date": date}
            for i in range(8):
                row[f"state_{i}_ratio"] = counts[i] / len(labs)
            row["state_entropy"] = entropy([counts[i] for i in range(8)])
            row["state_transition_count"] = transitions
            row["dominant_state"] = counts.most_common(1)[0][0]
            row["night_state_entropy"] = entropy([Counter(night_labs)[i] for i in range(8)])
            row["night_transition_count"] = night_transitions
            writer.writerow(row)

    con.execute(f"COPY (SELECT * FROM read_csv_auto('{q(out_csv)}')) TO '{q(out_parquet)}' (FORMAT PARQUET)")
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out_parquet)}')").fetchone()[0]
    print(f"wrote {out_parquet} rows={n} cols={len(fieldnames)}")


if __name__ == "__main__":
    main()
