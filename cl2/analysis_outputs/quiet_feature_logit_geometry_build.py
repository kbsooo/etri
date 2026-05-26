from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

import sys

sys.path.append(str(Path(__file__).resolve().parent))
import geometry_mask_cv_experiments as geom  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def add_ref_z(rows: pd.DataFrame, ref: pd.DataFrame, feature: str) -> np.ndarray:
    out = np.full(len(rows), np.nan, dtype=float)
    row_sids = rows["subject_id"].astype(str).to_numpy()
    for sid, ref_g in ref.groupby("subject_id", sort=False):
        idx = np.where(row_sids == str(sid))[0]
        if idx.size == 0:
            continue
        vals = ref_g[feature].to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1)) if vals.size > 1 else np.nan
        raw = rows.iloc[idx][feature].to_numpy(dtype=float)
        out[idx] = (raw - mean) / std if np.isfinite(std) and std > 0 else raw - mean
    fill = float(np.nanmedian(out)) if np.isfinite(out).any() else 0.0
    return np.where(np.isfinite(out), out, fill)


def fit_corrected(
    train_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    target: str,
    feature: str,
    c_value: float,
) -> np.ndarray:
    j = TARGETS.index(target)
    z_tr = add_ref_z(train_rows, train_rows, feature)
    z_pr = add_ref_z(pred_rows, train_rows, feature)
    x_tr = np.column_stack([logit(train_base[:, j]), z_tr])
    x_pr = np.column_stack([logit(pred_base[:, j]), z_pr])
    y = train_rows[target].to_numpy(dtype=int)
    if y.min() == y.max():
        return np.full(len(pred_rows), float(y.mean()))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=500)
    clf.fit(x_tr, y)
    return clip(clf.predict_proba(x_pr)[:, 1])


def apply_candidates(
    ref_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    ref_base: np.ndarray,
    pred_base: np.ndarray,
    candidates: pd.DataFrame,
) -> np.ndarray:
    out = pred_base.copy()
    for row in candidates.itertuples(index=False):
        target = str(row.target)
        j = TARGETS.index(target)
        corrected = fit_corrected(ref_rows, pred_rows, ref_base, pred_base, target, str(row.feature), float(row.c_value))
        out[:, j] = clip((1.0 - float(row.best_weight)) * pred_base[:, j] + float(row.best_weight) * corrected)
    return clip(out)


def estimate(train: pd.DataFrame, base: np.ndarray, candidate: np.ndarray, out_path: Path, candidates: pd.DataFrame) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    source = {str(row.target): f"{row.feature}|C={row.c_value}|w={row.best_weight}" for row in candidates.itertuples(index=False)}
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = loss_col(y[:, j], base[:, j])
        cand_loss = loss_col(y[:, j], candidate[:, j])
        rows.append(
            {
                "target": target,
                "current_loss": base_loss,
                "candidate_loss": cand_loss,
                "delta_vs_current": cand_loss - base_loss,
                "source": source.get(target, "unchanged"),
            }
        )
    df = pd.DataFrame(rows)
    df.loc[len(df)] = {
        "target": "mean",
        "current_loss": float(df["current_loss"].mean()),
        "candidate_loss": float(df["candidate_loss"].mean()),
        "delta_vs_current": float(df["candidate_loss"].mean() - df["current_loss"].mean()),
        "source": "target_mean",
    }
    df.to_csv(out_path, index=False)
    return df


def geometry_check(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, train_feat: pd.DataFrame, base: np.ndarray, candidates: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    folds = geom.geometry_folds(train_raw, sub_raw, n_repeats=10)
    y_all = train_feat[TARGETS].to_numpy(dtype=int)
    rows = []
    for tr_idx, val_idx, fold in folds:
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        b_ref = base[tr_idx]
        b_val = base[val_idx]
        c_val = apply_candidates(ref, val, b_ref, b_val, candidates)
        y = y_all[val_idx]
        row = {
            "fold": fold,
            "base_mean": float(np.mean([loss_col(y[:, j], b_val[:, j]) for j in range(len(TARGETS))])),
            "candidate_mean": float(np.mean([loss_col(y[:, j], c_val[:, j]) for j in range(len(TARGETS))])),
        }
        row["delta_mean"] = row["candidate_mean"] - row["base_mean"]
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y[:, j], c_val[:, j]) - loss_col(y[:, j], b_val[:, j])
        rows.append(row)
        print(f"[quiet geometry] {fold} val={len(val_idx)} delta={row['delta_mean']:.6f}", flush=True)
    df = pd.DataFrame(rows)
    summary = {
        "fold": "summary",
        "base_mean": float(df["base_mean"].mean()),
        "candidate_mean": float(df["candidate_mean"].mean()),
        "delta_mean": float(df["delta_mean"].mean()),
    }
    for target in TARGETS:
        summary[f"{target}_delta"] = float(df[f"{target}_delta"].mean())
    df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    df.to_csv(out_path, index=False)
    return df


def build_submission(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base_oof: np.ndarray,
    base_sub_path: Path,
    candidates: pd.DataFrame,
    out_path: Path,
) -> pd.DataFrame:
    out = pd.read_csv(base_sub_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[KEY].equals(sample[KEY])
    base_sub = out[TARGETS].to_numpy(dtype=float)
    pred = apply_candidates(train_feat, sub_feat, base_oof, base_sub, candidates)
    out[TARGETS] = pred
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(KEY).sum() == 0
    assert ((out[TARGETS] >= 0).all().all() and (out[TARGETS] <= 1).all().all())
    out.to_csv(out_path, index=False)
    return out


def selected_candidates(path: Path, targets: list[str] | None, weight_scale: float) -> pd.DataFrame:
    selected = pd.read_csv(path)
    if targets:
        selected = selected[selected["target"].isin(targets)]
    selected = selected.sort_values(["target", "delta_vs_base"]).groupby("target", as_index=False).head(1)
    selected["best_weight"] = (selected["best_weight"].astype(float) * float(weight_scale)).clip(0.0, 1.0)
    return selected.sort_values("target").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy")
    parser.add_argument("--base-sub", type=Path, default=OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv")
    parser.add_argument("--selected", type=Path, default=OUT / "current_0p578_quiet_logit_selected.csv")
    parser.add_argument("--prefix", default="hybrid_0p573_quiet_logit")
    parser.add_argument("--targets", default="")
    parser.add_argument("--weight-scale", type=float, default=1.0)
    args = parser.parse_args()

    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub_raw = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    quiet = pd.read_parquet(OUT / "quiet_window_residual_features.parquet")
    train_feat = train_raw.merge(quiet, on=KEY, how="left")
    sub_feat = sub_raw.merge(quiet, on=KEY, how="left")
    targets = [t for t in args.targets.split(",") if t] or None
    candidates = selected_candidates(args.selected, targets, args.weight_scale)
    candidates.to_csv(OUT / f"{args.prefix}_selected.csv", index=False)
    base = clip(np.load(args.base_oof))
    candidate_oof = apply_candidates(train_feat, train_feat, base, base, candidates)
    np.save(OUT / f"final_{args.prefix}_oof.npy", candidate_oof)
    estimate_df = estimate(train_feat, base, candidate_oof, OUT / f"{args.prefix}_cv_estimate.csv", candidates)
    geometry = geometry_check(train_raw, sub_raw, train_feat, base, candidates, OUT / f"{args.prefix}_geometry.csv")
    sub = build_submission(train_feat, sub_feat, base, args.base_sub, candidates, OUT / f"submission_{args.prefix}.csv")
    print("candidates")
    print(candidates.to_string(index=False))
    print(estimate_df.round(9).to_string(index=False))
    print("geometry")
    print(geometry.tail(1).round(9).to_string(index=False))
    print("wrote", OUT / f"submission_{args.prefix}.csv")
    print("range", float(sub[TARGETS].min().min()), float(sub[TARGETS].max().max()))


if __name__ == "__main__":
    main()
