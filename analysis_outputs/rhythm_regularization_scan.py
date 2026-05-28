from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as bfab
import broad_single_feature_residual_probe as broad
import rhythm_regularization_feature_builder as rfb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def ensure_features() -> None:
    path = OUT / "rhythm_regular_features.parquet"
    if path.exists():
        return
    features = rfb.build_features()
    features.to_parquet(path, index=False)


def build_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ensure_features()
    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub_raw = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    rhythm = broad.prefixed_frame(OUT / "rhythm_regular_features.parquet", "rhythm")
    train = train_raw.merge(rhythm, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    sub = sub_raw.merge(rhythm, on=KEY, how="left").sort_values(KEY).reset_index(drop=True)
    return train_raw, sub_raw, train, sub


def finite_rhythm_cols(df: pd.DataFrame) -> list[str]:
    cols = []
    for col in df.columns:
        if not col.startswith("rhythm__rr_"):
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def raw_scan(train_feat: pd.DataFrame, base: np.ndarray, targets: list[str], top_n: int) -> pd.DataFrame:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cols = finite_rhythm_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, targets, top_n)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.03, 0.05, 0.10, 0.20, 0.50]:
            try:
                corrected = broad.oof_corrected(train_feat, base, target, feature, mode, c_value)
            except Exception as exc:
                rows.append(
                    {
                        "target": target,
                        "feature": feature,
                        "mode": mode,
                        "corr": float(cand.corr),
                        "c_value": c_value,
                        "error": repr(exc),
                    }
                )
                continue
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in GRID]
            best_i = int(np.argmin(losses))
            best_weight = float(GRID[best_i])
            rows.append(
                {
                    "target": target,
                    "feature": feature,
                    "mode": mode,
                    "corr": float(cand.corr),
                    "abs_corr": abs(float(cand.corr)),
                    "c_value": c_value,
                    "base_loss": base_loss,
                    "corrected_loss": loss_col(y[:, j], corrected),
                    "best_weight": best_weight,
                    "best_blend_loss": float(losses[best_i]),
                    "delta_vs_base": float(losses[best_i] - base_loss),
                    "error": "",
                }
            )
    raw = pd.DataFrame(rows)
    return raw.sort_values(["delta_vs_base", "best_weight"], ascending=[True, False]).reset_index(drop=True)


def guard_and_geometry(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    base: np.ndarray,
    raw: pd.DataFrame,
    guard_top: int,
) -> pd.DataFrame:
    y = train_raw[TARGETS].to_numpy(dtype=int)
    candidates = raw[(raw["error"].fillna("") == "") & (raw["best_weight"] > 0) & (raw["delta_vs_base"] < 0)].copy()
    candidates = candidates.sort_values(["delta_vs_base", "abs_corr"], ascending=[True, False]).head(guard_top)
    rows = []
    for cand in candidates.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        c_value = float(cand.c_value)
        weight = float(cand.best_weight)
        j = TARGETS.index(target)
        corrected = broad.oof_corrected(train_feat, base, target, feature, mode, c_value)
        guard = broad.repeated_subject_guardrail(train_feat, y, base, corrected, j)
        op = bfab.FeatureOp(target, feature, mode, c_value, weight)
        geom = bfab.geometry_summary(train_raw, sub_raw, train_feat, base, [op])
        pred = base.copy()
        pred[:, j] = clip((1.0 - weight) * base[:, j] + weight * corrected)
        row = cand._asdict()
        row.update(guard)
        row.update(geom)
        row["candidate_mean_loss"] = mean_loss(y, pred)
        row["candidate_mean_delta"] = mean_loss(y, pred) - mean_loss(y, base)
        row["passes_loose"] = bool(
            row["delta_vs_base"] <= -0.00015
            and row["mean_delta"] < 0.0
            and row["win_rate"] >= 0.58
            and row["geometry_delta"] < 0.0
            and row[f"geometry_{target}_delta"] < 0.0
        )
        row["passes_strict"] = bool(
            row["delta_vs_base"] <= -0.00040
            and row["mean_delta"] <= -0.00015
            and row["win_rate"] >= 0.65
            and row["geometry_delta"] <= -0.00010
            and row[f"geometry_{target}_delta"] <= -0.00010
        )
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    guarded = pd.DataFrame(rows)
    return guarded.sort_values(
        ["passes_strict", "passes_loose", "delta_vs_base", "geometry_delta"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def save_single_submission(
    prefix: str,
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base_oof: np.ndarray,
    base_submission: Path,
    row: pd.Series,
) -> Path:
    op = bfab.FeatureOp(
        str(row["target"]),
        str(row["feature"]),
        str(row["mode"]),
        float(row["c_value"]),
        float(row["best_weight"]),
    )
    out = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    pred = out[TARGETS].to_numpy(dtype=float)
    pred = bfab.apply_op_fit_predict(train_feat, sub_feat, base_oof, pred, op)
    out[TARGETS] = clip(pred)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    path = OUT / f"submission_{prefix}.csv"
    out.to_csv(path, index=False)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, required=True)
    parser.add_argument("--base-submission", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--targets", default="Q1,Q2,Q3,S1,S2,S3,S4")
    parser.add_argument("--top-n", type=int, default=35)
    parser.add_argument("--guard-top", type=int, default=70)
    parser.add_argument("--save-strict", action="store_true")
    args = parser.parse_args()

    train_raw, sub_raw, train_feat, sub_feat = build_frames()
    base = clip(np.load(args.base_oof))
    targets = [t for t in args.targets.split(",") if t]
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base_loss = mean_loss(y, base)

    raw = raw_scan(train_feat, base, targets, args.top_n)
    raw.to_csv(OUT / f"{args.prefix}_raw_scan.csv", index=False)
    raw.groupby("target", group_keys=False).head(20).to_csv(OUT / f"{args.prefix}_top_raw_by_target.csv", index=False)

    guarded = guard_and_geometry(train_raw, sub_raw, train_feat, base, raw, args.guard_top)
    guarded.to_csv(OUT / f"{args.prefix}_guarded.csv", index=False)
    if len(guarded):
        guarded.groupby("target", group_keys=False).head(10).to_csv(OUT / f"{args.prefix}_top_guarded_by_target.csv", index=False)
        selected = guarded[guarded["passes_loose"]].copy()
    else:
        selected = pd.DataFrame()
    selected.to_csv(OUT / f"{args.prefix}_selected.csv", index=False)

    saved = []
    if args.save_strict and len(selected):
        for i, row in selected.head(5).reset_index(drop=True).iterrows():
            if not bool(row["passes_strict"]):
                continue
            feature_slug = str(row["feature"]).replace("rhythm__rr_", "").replace("__", "_")[:48]
            sub_prefix = f"{args.prefix}_{i+1:02d}_{row['target']}_{feature_slug}"
            path = save_single_submission(sub_prefix, train_feat, sub_feat, base, args.base_submission, row)
            saved.append(path.name)

    print(f"base_loss={base_loss:.9f} features={len(finite_rhythm_cols(train_feat))} raw_rows={len(raw)} guarded_rows={len(guarded)} selected={len(selected)}")
    if len(guarded):
        show_cols = [
            "target",
            "feature",
            "mode",
            "c_value",
            "best_weight",
            "delta_vs_base",
            "mean_delta",
            "win_rate",
            "geometry_delta",
            "passes_strict",
            "passes_loose",
        ]
        print(guarded[show_cols].head(30).round(6).to_string(index=False))
    if saved:
        print("saved_submissions=" + ",".join(saved))


if __name__ == "__main__":
    main()
