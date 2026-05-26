from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
DATA = ROOT / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray | pd.Series) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), 1e-5, 1 - 1e-5)


def neighbor_records(ref: pd.DataFrame, rows: pd.DataFrame, pred: np.ndarray | None, include_y: bool) -> pd.DataFrame:
    out = []
    by_subject = {
        str(sid): g.sort_values("lifelog_date")[["lifelog_date"] + TARGETS].reset_index(drop=True)
        for sid, g in ref.groupby("subject_id", sort=False)
    }
    rows = rows.reset_index(drop=True)
    for i, row in rows.iterrows():
        sid = str(row["subject_id"])
        day = row["lifelog_date"]
        hist = by_subject.get(sid)
        if hist is None or hist.empty:
            for j, target in enumerate(TARGETS):
                rec = {
                    "row_index": i,
                    "subject_id": sid,
                    "lifelog_date": day,
                    "target": target,
                    "category": "none",
                    "neighbor_label": np.nan,
                    "prev_label": np.nan,
                    "next_label": np.nan,
                    "prev_dist": np.nan,
                    "next_dist": np.nan,
                    "gap": np.nan,
                }
                if pred is not None:
                    rec["pred"] = float(pred[i, j])
                if include_y:
                    rec["y"] = int(row[target])
                out.append(rec)
            continue

        days = (hist["lifelog_date"] - day).dt.days.to_numpy(dtype=float)
        keep = days != 0
        hist = hist.loc[keep].reset_index(drop=True)
        days = days[keep]
        prev_idx = np.where(days < 0)[0]
        next_idx = np.where(days > 0)[0]

        for j, target in enumerate(TARGETS):
            y_hist = hist[target].to_numpy(dtype=float)
            prev_label = next_label = prev_dist = next_dist = np.nan
            if len(prev_idx):
                pidx = prev_idx[np.argmax(days[prev_idx])]
                prev_label = float(y_hist[pidx])
                prev_dist = abs(float(days[pidx]))
            if len(next_idx):
                nidx = next_idx[np.argmin(days[next_idx])]
                next_label = float(y_hist[nidx])
                next_dist = abs(float(days[nidx]))

            if not np.isnan(prev_label) and not np.isnan(next_label):
                gap = prev_dist + next_dist
                if prev_label == next_label:
                    category = f"same_{int(prev_label)}"
                    neighbor_label = prev_label
                else:
                    category = "different"
                    neighbor_label = np.nan
            elif not np.isnan(prev_label) or not np.isnan(next_label):
                gap = np.nan
                category = "one_side"
                neighbor_label = prev_label if not np.isnan(prev_label) else next_label
            else:
                gap = np.nan
                category = "none"
                neighbor_label = np.nan

            rec = {
                "row_index": i,
                "subject_id": sid,
                "lifelog_date": day,
                "target": target,
                "category": category,
                "neighbor_label": neighbor_label,
                "prev_label": prev_label,
                "next_label": next_label,
                "prev_dist": prev_dist,
                "next_dist": next_dist,
                "gap": gap,
            }
            if pred is not None:
                rec["pred"] = float(pred[i, j])
            if include_y:
                rec["y"] = int(row[target])
            out.append(rec)
    return pd.DataFrame(out)


def cv_neighbor_audit(train: pd.DataFrame) -> pd.DataFrame:
    folds = d.make_folds(train, "subject_blocks")
    all_records = []
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        ref = train.iloc[tr_idx].copy()
        val = train.iloc[val_idx].copy()
        pred = cal.temporal_base(ref, val)
        rec = neighbor_records(ref, val, pred, include_y=True)
        rec["fold_id"] = fold_id
        all_records.append(rec)
    recs = pd.concat(all_records, ignore_index=True)
    recs.to_csv(OUT / "neighbor_consistency_cv_records.csv", index=False)

    rows = []
    for keys, g in recs.groupby(["target", "category"], dropna=False):
        target, category = keys
        y = g["y"].to_numpy(dtype=int)
        pred = clip(g["pred"])
        row = {
            "target": target,
            "category": category,
            "n": len(g),
            "y_rate": float(y.mean()),
            "pred_mean": float(pred.mean()),
            "base_logloss": float(log_loss(y, pred, labels=[0, 1])),
            "median_gap": float(g["gap"].median()) if g["gap"].notna().any() else np.nan,
        }
        if category in {"same_0", "same_1"}:
            label = int(category[-1])
            weak = np.full(len(g), 0.75 if label else 0.25)
            strong = np.full(len(g), 0.90 if label else 0.10)
            row["force_weak_logloss"] = float(log_loss(y, weak, labels=[0, 1]))
            row["force_strong_logloss"] = float(log_loss(y, strong, labels=[0, 1]))
            row["actual_matches_neighbor"] = float((y == label).mean())
        else:
            row["force_weak_logloss"] = np.nan
            row["force_strong_logloss"] = np.nan
            row["actual_matches_neighbor"] = np.nan
        rows.append(row)

    summary = pd.DataFrame(rows).sort_values(["target", "category"])
    summary.to_csv(OUT / "neighbor_consistency_cv_summary.csv", index=False)

    pooled = []
    for category, g in recs.groupby("category"):
        y = g["y"].to_numpy(dtype=int)
        pred = clip(g["pred"])
        row = {
            "target": "ALL",
            "category": category,
            "n": len(g),
            "y_rate": float(y.mean()),
            "pred_mean": float(pred.mean()),
            "base_logloss": float(log_loss(y, pred, labels=[0, 1])),
            "median_gap": float(g["gap"].median()) if g["gap"].notna().any() else np.nan,
        }
        if category in {"same_0", "same_1"}:
            label = int(category[-1])
            weak = np.full(len(g), 0.75 if label else 0.25)
            strong = np.full(len(g), 0.90 if label else 0.10)
            row["force_weak_logloss"] = float(log_loss(y, weak, labels=[0, 1]))
            row["force_strong_logloss"] = float(log_loss(y, strong, labels=[0, 1]))
            row["actual_matches_neighbor"] = float((y == label).mean())
        pooled.append(row)
    pooled_df = pd.DataFrame(pooled).sort_values("category")
    pooled_df.to_csv(OUT / "neighbor_consistency_cv_pooled.csv", index=False)
    return summary


def assign_submission_blocks(all_keys: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in all_keys.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        g = g.reset_index(drop=True)
        block_id = 0
        in_block = False
        for _, row in g.iterrows():
            if row["split"] == "submission":
                if not in_block:
                    block_id += 1
                    in_block = True
                rows.append({"subject_id": sid, "lifelog_date": row["lifelog_date"], "sub_block": block_id})
            else:
                in_block = False
    return pd.DataFrame(rows)


def submission_neighbor_audit(train: pd.DataFrame, sub: pd.DataFrame, pred_file: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred = pd.read_csv(pred_file, parse_dates=["sleep_date", "lifelog_date"])
    pred_matrix = pred[TARGETS].to_numpy(dtype=float)
    recs = neighbor_records(train, sub, pred_matrix, include_y=False)
    train_keys = train[KEY + ["sleep_date"]].copy()
    train_keys["split"] = "train"
    sub_keys = sub[KEY + ["sleep_date"]].copy()
    sub_keys["split"] = "submission"
    blocks = assign_submission_blocks(pd.concat([train_keys, sub_keys], ignore_index=True))
    recs = recs.merge(blocks, on=KEY, how="left")
    recs.to_csv(OUT / "neighbor_consistency_submission_records.csv", index=False)

    summary_rows = []
    for keys, g in recs.groupby(["subject_id", "sub_block", "target"], dropna=False):
        sid, block, target = keys
        first = g.sort_values("lifelog_date").iloc[0]
        last = g.sort_values("lifelog_date").iloc[-1]
        same = g[g["category"].isin(["same_0", "same_1"])]
        neighbor_label = same["neighbor_label"].iloc[0] if not same.empty else np.nan
        pred_mean = float(g["pred"].mean())
        contradiction = False
        if not np.isnan(neighbor_label):
            contradiction = bool((neighbor_label == 1 and pred_mean < 0.35) or (neighbor_label == 0 and pred_mean > 0.65))
        summary_rows.append(
            {
                "subject_id": sid,
                "sub_block": int(block),
                "target": target,
                "n_days": len(g),
                "start": first["lifelog_date"],
                "end": last["lifelog_date"],
                "dominant_category": g["category"].mode().iloc[0],
                "neighbor_label": neighbor_label,
                "pred_mean": pred_mean,
                "pred_min": float(g["pred"].min()),
                "pred_max": float(g["pred"].max()),
                "median_gap": float(g["gap"].median()) if g["gap"].notna().any() else np.nan,
                "contradiction": contradiction,
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["subject_id", "sub_block", "target"])
    summary.to_csv(OUT / "neighbor_consistency_submission_summary.csv", index=False)
    return recs, summary


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    cv_summary = cv_neighbor_audit(train)
    _, sub_summary = submission_neighbor_audit(train, sub, OUT / "submission_conservative_sensor_blend_missing.csv")
    pooled = pd.read_csv(OUT / "neighbor_consistency_cv_pooled.csv")
    contradictions = sub_summary[sub_summary["contradiction"]]

    print("\nCV pooled neighbor consistency")
    print(pooled.round(5).to_string(index=False))
    print("\nCV same-neighbor target summary")
    same = cv_summary[cv_summary["category"].isin(["same_0", "same_1"])]
    print(same.round(5).to_string(index=False))
    print("\nSubmission contradiction flags")
    if contradictions.empty:
        print("none")
    else:
        print(contradictions.to_string(index=False))


if __name__ == "__main__":
    main()
