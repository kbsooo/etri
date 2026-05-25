#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import pairwise_distances
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs, logloss

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}


def clip(p):
    return np.clip(np.asarray(p, dtype=float), 0.03, 0.97)


def md_table(df: pd.DataFrame, max_rows: int | None = None, floatfmt: str = ".4f") -> str:
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        cells = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                cells.append(format(float(v), floatfmt))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    for d in (train, test):
        d["sleep_date"] = d["sleep_date"].dt.date.astype(str)
        d["lifelog_date"] = d["lifelog_date"].dt.date.astype(str)
    return train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True), test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def key_index(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = key_index(df)
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


def subject_prior(train: pd.DataFrame, valid: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    sm = ((pos + alpha * g) / (cnt + alpha)).to_dict()
    return np.array([sm.get(s, g) for s in valid["subject_id"]], dtype=float)


def load_feature_tables(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).drop_duplicates()
    out = keys.copy()
    specs = [
        ("semantic_topk_features_v2.parquet", "sem", 360),
        ("observation_identity_token_features.parquet", "tok", 500),
        ("external_context_features_v1.parquet", "ext", 120),
        ("goal4_hour_transition_features_v1.parquet", "h4", 260),
        ("goal4_sleep_boundary_rest_features_v1.parquet", "r4", 120),
    ]
    for fname, prefix, max_cols in specs:
        path = FEATURE_DIR / fname
        if not path.exists():
            continue
        d = pd.read_parquet(path)
        if "date" in d.columns and "lifelog_date" not in d.columns:
            d = d.rename(columns={"date": "lifelog_date"})
        d["lifelog_date"] = pd.to_datetime(d["lifelog_date"]).dt.date.astype(str)
        if "sleep_date" in d.columns:
            join = ["subject_id", "sleep_date", "lifelog_date"]
        else:
            join = ["subject_id", "lifelog_date"]
        num = [c for c in d.columns if c not in join and pd.api.types.is_numeric_dtype(d[c])]
        # Prefer raw/deviation columns over subject means; cap to keep NN stable.
        filt = [c for c in num if "__subj_mean" not in c and not c.endswith("_mean_y")]
        if len(filt) > max_cols:
            var = d[filt].replace([np.inf, -np.inf], np.nan).fillna(0).var().sort_values(ascending=False)
            filt = var.head(max_cols).index.tolist()
        d = d[join + filt].rename(columns={c: f"{prefix}__{c}" for c in filt})
        out = out.merge(d, on=join, how="left")
    return out


def same_date_peer(train: pd.DataFrame, valid: pd.DataFrame, target: str, window: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows_p, rows_conf, rows_cov = [], [], []
    train_d = train.copy()
    valid_d = valid.copy()
    train_d["_d"] = pd.to_datetime(train_d["lifelog_date"])
    valid_d["_d"] = pd.to_datetime(valid_d["lifelog_date"])
    global_p = float(train[target].mean())
    for _, r in valid_d.iterrows():
        g = train_d[train_d["subject_id"].ne(r.subject_id)].copy()
        dist = (g["_d"] - r["_d"]).abs().dt.days
        g = g[dist <= window]
        if len(g) == 0:
            rows_p.append(global_p)
            rows_conf.append(0.0)
            rows_cov.append(0)
            continue
        p = float(g[target].mean())
        rows_p.append(p)
        rows_conf.append(float(abs(p - global_p) * min(1.0, len(g) / 5)))
        rows_cov.append(len(g))
    return np.array(rows_p), np.array(rows_conf), np.array(rows_cov)


def subject_pair_offset(train: pd.DataFrame, valid: pd.DataFrame, target: str, max_lag: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    tr = train.copy()
    va = valid.copy()
    tr["_d"] = pd.to_datetime(tr["lifelog_date"])
    va["_d"] = pd.to_datetime(va["lifelog_date"])
    global_p = float(tr[target].mean())
    pair_rows = []
    # Fold-local donor lag search using only train rows.
    for src in sorted(tr["subject_id"].unique()):
        src_g = tr[tr["subject_id"].eq(src)][["_d", target]].drop_duplicates("_d").set_index("_d")
        if len(src_g) < 8:
            continue
        for dst in sorted(tr["subject_id"].unique()):
            if src == dst:
                continue
            dst_g = tr[tr["subject_id"].eq(dst)][["_d", target]].drop_duplicates("_d").set_index("_d")
            best = None
            for lag in range(-max_lag, max_lag + 1):
                shifted = src_g.copy()
                shifted.index = shifted.index + pd.to_timedelta(lag, unit="D")
                joined = dst_g.join(shifted, how="inner", lsuffix="_dst", rsuffix="_src")
                if len(joined) < 8:
                    continue
                acc = float((joined[f"{target}_dst"].astype(int) == joined[f"{target}_src"].astype(int)).mean())
                corr = float(np.corrcoef(joined[f"{target}_dst"], joined[f"{target}_src"])[0, 1]) if joined[f"{target}_dst"].std() > 0 and joined[f"{target}_src"].std() > 0 else 0.0
                score = acc + 0.2 * corr + 0.01 * min(len(joined), 20)
                cand = (score, acc, corr, len(joined), lag)
                if best is None or cand > best:
                    best = cand
            if best is not None:
                score, acc, corr, n, lag = best
                pair_rows.append({"target": target, "src": src, "dst": dst, "lag": lag, "acc": acc, "corr": corr, "n_overlap": n, "score": score})
    pair_df = pd.DataFrame(pair_rows).sort_values("score", ascending=False) if pair_rows else pd.DataFrame()
    preds, confs, covs = [], [], []
    for _, r in va.iterrows():
        cand = pair_df[pair_df["dst"].eq(r.subject_id)].head(3) if len(pair_df) else pd.DataFrame()
        vals, weights = [], []
        for _, pr in cand.iterrows():
            qd = r["_d"] - pd.to_timedelta(int(pr["lag"]), unit="D")
            g = tr[(tr["subject_id"].eq(pr["src"])) & (tr["_d"].eq(qd))]
            if len(g):
                vals.append(float(g[target].iloc[0]))
                weights.append(max(0.0, float(pr["score"])))
        if vals:
            p = float(np.average(vals, weights=weights))
            conf = float(abs(p - 0.5) * min(1.0, sum(weights) / 4))
            preds.append(p)
            confs.append(conf)
            covs.append(len(vals))
        else:
            preds.append(global_p)
            confs.append(0.0)
            covs.append(0)
    return np.array(preds), np.array(confs), np.array(covs), pair_df


def nn_predict(
    train: pd.DataFrame,
    valid: pd.DataFrame,
    target: str,
    feature_cols: list[str],
    k_select: int = 80,
    k_nn: int = 9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    y = train[target].astype(int).to_numpy()
    global_p = float(y.mean())
    if len(feature_cols) == 0 or y.std() < 1e-8:
        return np.full(len(valid), global_p), np.zeros(len(valid)), np.zeros(len(valid)), []
    Xtr_raw = train[feature_cols].replace([np.inf, -np.inf], np.nan)
    Xva_raw = valid[feature_cols].replace([np.inf, -np.inf], np.nan)
    keep = Xtr_raw.notna().mean().loc[lambda s: s > 0.45].index.tolist()
    keep = [c for c in keep if Xtr_raw[c].std(skipna=True) > 1e-8]
    if not keep:
        return np.full(len(valid), global_p), np.zeros(len(valid)), np.zeros(len(valid)), []
    Xtr_raw = Xtr_raw[keep]
    Xva_raw = Xva_raw[keep]
    imputer = SimpleImputer(strategy="median")
    Xtr_i = imputer.fit_transform(Xtr_raw)
    Xva_i = imputer.transform(Xva_raw)
    if Xtr_i.shape[1] > k_select:
        sel = SelectKBest(f_classif, k=min(k_select, Xtr_i.shape[1]))
        Xtr_i = sel.fit_transform(Xtr_i, y)
        Xva_i = sel.transform(Xva_i)
        selected = [c for c, m in zip(keep, sel.get_support()) if m]
    else:
        selected = keep
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(Xtr_i)
    Xva = scaler.transform(Xva_i)
    nn = NearestNeighbors(n_neighbors=min(k_nn, len(train)), metric="euclidean")
    nn.fit(Xtr)
    dist, ind = nn.kneighbors(Xva, return_distance=True)
    lbl = y[ind]
    # Distance-weighted local label rate.
    w = 1.0 / (1.0 + dist)
    p = (lbl * w).sum(axis=1) / np.maximum(w.sum(axis=1), 1e-9)
    consensus = np.abs(lbl.mean(axis=1) - 0.5) * 2
    close = 1.0 / (1.0 + dist.mean(axis=1))
    conf = consensus * close
    return clip(p), conf, np.full(len(valid), k_nn), selected


def score_candidate(y: np.ndarray, anchor: np.ndarray, p: np.ndarray, conf: np.ndarray) -> list[dict]:
    rows = []
    base = float(logloss(y, clip(anchor)))
    for mode, q, weight in [
        ("blend_all_w025", 0.0, 0.25),
        ("top50_w050", 0.50, 0.50),
        ("top30_w060", 0.70, 0.60),
        ("top20_w075", 0.80, 0.75),
        ("top10_w090", 0.90, 0.90),
    ]:
        if q <= 0:
            mask = np.ones(len(y), dtype=bool)
        else:
            thr = np.quantile(conf, q)
            mask = conf >= thr
        pred = anchor.copy()
        pred[mask] = clip(anchor[mask] * (1 - weight) + p[mask] * weight)
        rows.append(
            {
                "mode": mode,
                "coverage": float(mask.mean()),
                "n_moved": int(mask.sum()),
                "logloss": float(logloss(y, pred)),
                "delta_vs_anchor": float(logloss(y, pred) - base),
                "mean_conf_moved": float(np.mean(conf[mask])) if mask.any() else 0.0,
                "mean_abs_move": float(np.mean(np.abs(pred[mask] - anchor[mask]))) if mask.any() else 0.0,
            }
        )
    return rows


def test_candidate_count(train: pd.DataFrame, test: pd.DataFrame, full_features: pd.DataFrame, group_cols: list[str], target: str) -> dict:
    tr = train.merge(full_features, on=KEYS, how="left")
    te = test.merge(full_features, on=KEYS, how="left")
    p, conf, cov, _ = nn_predict(tr, te, target, group_cols, k_select=80, k_nn=9)
    return {
        "test_n": len(test),
        "test_conf_top10_threshold": float(np.quantile(conf, 0.90)),
        "test_top10_rows": int((conf >= np.quantile(conf, 0.90)).sum()),
        "test_top20_rows": int((conf >= np.quantile(conf, 0.80)).sum()),
        "test_mean_conf": float(np.mean(conf)),
        "test_mean_abs_move_from_subject_prior": float(np.mean(np.abs(p - subject_prior(train, test, target)))),
    }


def test_candidate_rows(
    train: pd.DataFrame,
    test: pd.DataFrame,
    full_features: pd.DataFrame,
    group_cols: list[str],
    target: str,
    candidate: str,
    max_rows: int = 25,
) -> pd.DataFrame:
    tr = train.merge(full_features, on=KEYS, how="left")
    te = test.merge(full_features, on=KEYS, how="left")
    p, conf, cov, _ = nn_predict(tr, te, target, group_cols, k_select=80, k_nn=9)
    anchor = subject_prior(train, test, target)
    out = test[KEYS].copy()
    out.insert(0, "candidate", candidate)
    out.insert(1, "target", target)
    out["subject_prior"] = anchor
    out["nn_pred"] = p
    out["move_from_subject_prior"] = p - anchor
    out["abs_move_from_subject_prior"] = np.abs(p - anchor)
    out["confidence"] = conf
    out["conf_rank"] = out["confidence"].rank(method="first", ascending=False).astype(int)
    out["blend_top50_w050"] = clip(anchor * 0.50 + p * 0.50)
    out["blend_top20_w075"] = clip(anchor * 0.25 + p * 0.75)
    out["blend_top10_w090"] = clip(anchor * 0.10 + p * 0.90)
    return out.sort_values(["confidence", "abs_move_from_subject_prior"], ascending=False).head(max_rows)


def main() -> None:
    ensure_dirs()
    train, test = load_labels()
    full_features = load_feature_tables(train, test)
    df = train.merge(full_features, on=KEYS, how="left")
    feature_groups = {
        "semantic_app": [c for c in df.columns if c.startswith("sem__")],
        "identity_token": [c for c in df.columns if c.startswith("tok__")],
        "hour_transition": [c for c in df.columns if c.startswith("h4__")],
        "rest_boundary": [c for c in df.columns if c.startswith("r4__")],
    }
    rows = []
    selected_counter: dict[str, Counter] = {}
    pair_rows = []
    for family, fpath in FOLD_FILES.items():
        cfg = json.loads(fpath.read_text())
        for fold in cfg["folds"]:
            tr0, va0 = split_by_fold(df, fold)
            for target in LABELS:
                y = va0[target].astype(int).to_numpy()
                anchor = subject_prior(tr0, va0, target)
                base_ll = float(logloss(y, clip(anchor)))
                for name, window in [("same_date_peer_w0", 0), ("near_date_peer_w3", 3), ("near_date_peer_w7", 7)]:
                    p, conf, cov = same_date_peer(tr0, va0, target, window=window)
                    for r in score_candidate(y, anchor, p, conf):
                        rows.append({"family": family, "fold": fold.get("name"), "target": target, "candidate": name, "anchor_logloss": base_ll, **r})
                # Subject-pair lag search is intentionally excluded from the
                # default pass; previous broad graph work already covered most
                # cross-subject transfer, and exhaustive pair offsets are slow.
                for gname, cols in feature_groups.items():
                    p, conf, cov, selected = nn_predict(tr0, va0, target, cols)
                    selected_counter.setdefault(f"{gname}:{target}", Counter()).update(selected)
                    for r in score_candidate(y, anchor, p, conf):
                        rows.append({"family": family, "fold": fold.get("name"), "target": target, "candidate": f"nn_{gname}", "anchor_logloss": base_ll, **r})
    res = pd.DataFrame(rows)
    out_csv = EXPERIMENT_DIR / "goal5_055_breakthrough_candidate_scores.csv"
    res.to_csv(out_csv, index=False)
    if pair_rows:
        pd.concat(pair_rows, ignore_index=True).to_csv(EXPERIMENT_DIR / "goal5_subject_pair_offset_top.csv", index=False)
    feat_rows = []
    for key, counter in selected_counter.items():
        group, target = key.split(":", 1)
        for feat, n in counter.most_common(30):
            feat_rows.append({"group": group, "target": target, "feature": feat, "selected_count": n})
    feat_df = pd.DataFrame(feat_rows)
    feat_df.to_csv(EXPERIMENT_DIR / "goal5_nn_selected_feature_counts.csv", index=False)

    agg = (
        res.groupby(["family", "target", "candidate", "mode"], as_index=False)
        .agg(mean_delta=("delta_vs_anchor", "mean"), std_delta=("delta_vs_anchor", "std"), mean_coverage=("coverage", "mean"), mean_move=("mean_abs_move", "mean"))
        .sort_values("mean_delta")
    )
    agg.to_csv(EXPERIMENT_DIR / "goal5_055_breakthrough_candidate_summary.csv", index=False)
    # Candidate is interesting only if it survives mirror/hole and is not only target-leakage.
    best = agg[(agg["family"].isin(["mirror_v1", "hole_v1"])) & (agg["mean_coverage"].between(0.08, 0.55))].copy()
    best = best.sort_values("mean_delta").head(60)
    test_rows = []
    test_detail_parts = []
    seen_test_candidates = set()
    for _, r in best.head(20).iterrows():
        cand = str(r["candidate"])
        target = str(r["target"])
        if cand.startswith("nn_"):
            gname = cand.removeprefix("nn_")
            test_rows.append({"candidate": cand, "target": target, **test_candidate_count(train, test, full_features, feature_groups.get(gname, []), target)})
            key = (cand, target)
            if key not in seen_test_candidates:
                seen_test_candidates.add(key)
                test_detail_parts.append(test_candidate_rows(train, test, full_features, feature_groups.get(gname, []), target, cand))
    test_df = pd.DataFrame(test_rows)
    test_df.to_csv(EXPERIMENT_DIR / "goal5_055_test_candidate_coverage.csv", index=False)
    test_detail_df = pd.concat(test_detail_parts, ignore_index=True) if test_detail_parts else pd.DataFrame()
    test_detail_df.to_csv(EXPERIMENT_DIR / "goal5_055_test_candidate_rows.csv", index=False)

    lines = ["# Goal5 — 0.55 breakthrough clue hunt\n"]
    lines.append("목표는 평균 CV를 조금 올리는 후보가 아니라, test 250 rows 중 일부를 크게 맞힐 수 있는 고상한 단서를 찾는 것이다.\n")
    lines.append("\n## 1. Best subset-moving candidates\n")
    lines.append(md_table(best.round(4), max_rows=40))
    lines.append("\n## 2. Overall candidate ranking\n")
    lines.append(md_table(agg.head(50).round(4), max_rows=50))
    lines.append("\n## 3. Test coverage for top NN candidates\n")
    lines.append(md_table(test_df.round(4), max_rows=30) if len(test_df) else "No NN candidate in top set.")
    lines.append("\n## 4. Top test rows for row-action inspection\n")
    display_cols = [
        "candidate",
        "target",
        "subject_id",
        "lifelog_date",
        "subject_prior",
        "nn_pred",
        "move_from_subject_prior",
        "confidence",
        "conf_rank",
    ]
    lines.append(md_table(test_detail_df[display_cols].round(4), max_rows=40) if len(test_detail_df) else "No test row candidates.")
    lines.append("\n## 5. Repeated selected features\n")
    lines.append(md_table(feat_df.sort_values("selected_count", ascending=False).head(60), max_rows=60) if len(feat_df) else "No selected features.")
    lines.append("\n## 6. Decision\n")
    top = best.head(10)
    if len(top):
        lines.append(
            "- If a candidate shows `mean_delta <= -0.02` on both `hole_v1` and `mirror_v1` with 10-30% coverage, it is a real 0.55-style clue candidate.\n"
        )
        lines.append(
            "- If gains are concentrated in one fold family or one target only, use it as a row-action diagnostic, not as a global submission rule.\n"
        )
        lines.append("- Top rows above should be inspected manually before any submission movement.\n")
    else:
        lines.append("- No high-upside subset rule found under these searches.")
    (EXPERIMENT_DIR / "goal5_055_breakthrough_clue_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {EXPERIMENT_DIR / 'goal5_055_breakthrough_clue_report.md'}")


if __name__ == "__main__":
    main()
