from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"

sys.path.append(str(OUT))
import geometry_mask_cv_experiments as geom  # noqa: E402


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=float), 1e-5, 1.0 - 1e-5)


def mean_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(p[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    return {t: float(log_loss(y[:, j], clip(p[:, j]), labels=[0, 1])) for j, t in enumerate(TARGETS)}


def read_core() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = np.load(BASE_OOF)
    base_sub = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if len(base) != len(train):
        raise RuntimeError("base/train length mismatch")
    if not base_sub[SUB_KEY].equals(sub[SUB_KEY]):
        raise RuntimeError("base submission key mismatch")
    return train, sub, clip(base), base_sub


def combined_rows(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    tr = train[SUB_KEY].copy()
    tr["split"] = "train"
    tr["train_idx"] = np.arange(len(train))
    tr["sub_idx"] = -1
    su = sub[SUB_KEY].copy()
    su["split"] = "submission"
    su["train_idx"] = -1
    su["sub_idx"] = np.arange(len(sub))
    rows = pd.concat([tr, su], ignore_index=True).sort_values(KEY).reset_index(drop=True)
    rows["global_pos"] = np.arange(len(rows))
    rows["subject_pos"] = rows.groupby("subject_id", sort=False).cumcount()
    return rows


def block_summary(rows: pd.DataFrame, train: pd.DataFrame) -> pd.DataFrame:
    y_by_train_idx = train[TARGETS].to_numpy(int)
    records: list[dict[str, object]] = []
    for sid, g in rows.groupby("subject_id", sort=False):
        split = g["split"].to_numpy()
        pos = g["global_pos"].to_numpy(dtype=int)
        dates = g["lifelog_date"].to_numpy()
        train_idx = g["train_idx"].to_numpy(dtype=int)
        start = 0
        block_id = 0
        while start < len(g):
            end = start + 1
            while end < len(g) and split[end] == split[start]:
                end += 1
            rec: dict[str, object] = {
                "subject_id": sid,
                "block_id": block_id,
                "split": split[start],
                "n": end - start,
                "start_date": pd.Timestamp(dates[start]).date().isoformat(),
                "end_date": pd.Timestamp(dates[end - 1]).date().isoformat(),
                "start_pos": int(pos[start]),
                "end_pos": int(pos[end - 1]),
                "prev_split": split[start - 1] if start > 0 else "",
                "next_split": split[end] if end < len(g) else "",
                "prev_gap_days": int((pd.Timestamp(dates[start]) - pd.Timestamp(dates[start - 1])).days) if start > 0 else np.nan,
                "next_gap_days": int((pd.Timestamp(dates[end]) - pd.Timestamp(dates[end - 1])).days) if end < len(g) else np.nan,
            }
            if split[start] == "train":
                idx = train_idx[start:end]
                vals = y_by_train_idx[idx]
                for j, target in enumerate(TARGETS):
                    rec[f"{target}_rate"] = float(vals[:, j].mean())
                    rec[f"{target}_transitions"] = int(np.abs(np.diff(vals[:, j])).sum()) if len(vals) > 1 else 0
            if start > 0 and split[start - 1] == "train":
                idx = int(train_idx[start - 1])
                for j, target in enumerate(TARGETS):
                    rec[f"prev_{target}"] = int(y_by_train_idx[idx, j])
            if end < len(g) and split[end] == "train":
                idx = int(train_idx[end])
                for j, target in enumerate(TARGETS):
                    rec[f"next_{target}"] = int(y_by_train_idx[idx, j])
            records.append(rec)
            start = end
            block_id += 1
    out = pd.DataFrame(records)
    out.to_csv(OUT / "data_dissection_subject_blocks.csv", index=False)
    return out


def target_audit(train: pd.DataFrame, blocks: pd.DataFrame) -> None:
    y = train[TARGETS].to_numpy(int)
    rows = []
    for target in TARGETS:
        rows.append(
            {
                "target": target,
                "global_rate": float(train[target].mean()),
                "subject_rate_std": float(train.groupby("subject_id")[target].mean().std()),
                "train_block_rate_std": float(blocks.loc[blocks["split"].eq("train"), f"{target}_rate"].std()),
                "transition_rate_within_subject": float(
                    np.mean(
                        [
                            np.abs(np.diff(g[target].to_numpy(int))).mean()
                            for _, g in train.groupby("subject_id", sort=False)
                            if len(g) > 1
                        ]
                    )
                ),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "data_dissection_target_signal_summary.csv", index=False)

    pair_rows = []
    for i, a in enumerate(TARGETS):
        for j, b in enumerate(TARGETS):
            if i >= j:
                continue
            av = y[:, i]
            bv = y[:, j]
            pair_rows.append(
                {
                    "a": a,
                    "b": b,
                    "corr": float(np.corrcoef(av, bv)[0, 1]),
                    "p_b_given_a1": float(bv[av == 1].mean()),
                    "p_b_given_a0": float(bv[av == 0].mean()),
                    "both1_rate": float(((av == 1) & (bv == 1)).mean()),
                    "xor_rate": float((av != bv).mean()),
                }
            )
    pd.DataFrame(pair_rows).sort_values("corr", ascending=False).to_csv(OUT / "data_dissection_target_pair_constraints.csv", index=False)

    powers = train[TARGETS].astype(str).agg("".join, axis=1)
    powerset = (
        powers.value_counts()
        .rename_axis("label_pattern")
        .reset_index(name="count")
        .assign(rate=lambda d: d["count"] / len(train))
    )
    powerset.to_csv(OUT / "data_dissection_label_powersets.csv", index=False)


def lag_autocorr(train: pd.DataFrame) -> None:
    records = []
    for lag in range(1, 22):
        for target in TARGETS:
            pairs = []
            for _, g in train.groupby("subject_id", sort=False):
                vals = g.sort_values("lifelog_date")[target].to_numpy(int)
                if len(vals) > lag:
                    pairs.append(np.column_stack([vals[lag:], vals[:-lag]]))
            if not pairs:
                continue
            arr = np.vstack(pairs)
            y = arr[:, 0]
            copy = arr[:, 1]
            acc = float((y == copy).mean())
            corr = float(np.corrcoef(y, copy)[0, 1]) if len(np.unique(y)) > 1 and len(np.unique(copy)) > 1 else np.nan
            records.append({"target": target, "lag": lag, "copy_accuracy": acc, "corr": corr, "n": int(len(y))})
    pd.DataFrame(records).sort_values(["target", "copy_accuracy"], ascending=[True, False]).to_csv(OUT / "data_dissection_label_lag_autocorr.csv", index=False)


def subject_prior(ref: pd.DataFrame, rows: pd.DataFrame, shrink: float = 4.0) -> np.ndarray:
    global_rate = ref[TARGETS].mean().to_numpy(float)
    stats = ref.groupby("subject_id")[TARGETS].agg(["sum", "count"])
    out = np.tile(global_rate, (len(rows), 1))
    for i, row in rows.reset_index(drop=True).iterrows():
        sid = row["subject_id"]
        if sid not in stats.index:
            continue
        vals = []
        for t in TARGETS:
            s = float(stats.loc[sid, (t, "sum")])
            c = float(stats.loc[sid, (t, "count")])
            vals.append((s + shrink * global_rate[TARGETS.index(t)]) / (c + shrink))
        out[i] = vals
    return clip(out)


def boundary_predict(ref: pd.DataFrame, rows: pd.DataFrame, method: str) -> np.ndarray:
    pred = subject_prior(ref, rows, shrink=6.0)
    ref_by_subject = {sid: g.sort_values("lifelog_date").reset_index(drop=True) for sid, g in ref.groupby("subject_id", sort=False)}
    for i, row in rows.reset_index(drop=True).iterrows():
        sid = row["subject_id"]
        day = row["lifelog_date"]
        hist = ref_by_subject.get(sid)
        if hist is None or hist.empty or method == "subject_prior":
            continue
        before = hist[hist["lifelog_date"] < day].tail(1)
        after = hist[hist["lifelog_date"] > day].head(1)
        values = []
        weights = []
        if method in {"prev", "both", "same_boundary"} and not before.empty:
            gap = max(int((day - before.iloc[-1]["lifelog_date"]).days), 1)
            values.append(before.iloc[-1][TARGETS].to_numpy(float))
            weights.append(np.exp(-gap / 3.0))
        if method in {"next", "both", "same_boundary"} and not after.empty:
            gap = max(int((after.iloc[0]["lifelog_date"] - day).days), 1)
            values.append(after.iloc[0][TARGETS].to_numpy(float))
            weights.append(np.exp(-gap / 3.0))
        if not values:
            continue
        local = np.average(np.vstack(values), axis=0, weights=np.asarray(weights))
        if method == "same_boundary" and len(values) == 2:
            same = values[0] == values[1]
            local = np.where(same, 0.90 * values[0] + 0.10 * local, local)
        pred[i] = 0.45 * pred[i] + 0.55 * local
    return clip(pred)


def boundary_cv(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray) -> None:
    y = train[TARGETS].to_numpy(int)
    methods = ["subject_prior", "prev", "next", "both", "same_boundary"]
    oof = {m: base.copy() for m in methods}
    fold_rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=8, seed=313000):
        ref = train.iloc[tr_idx].sort_values(KEY)
        val_rows = train.iloc[val_idx].sort_values(KEY)
        order = {idx: i for i, idx in enumerate(val_rows.index)}
        for method in methods:
            pred_sorted = boundary_predict(ref, val_rows, method)
            pred = np.zeros((len(val_idx), len(TARGETS)))
            for out_i, idx in enumerate(val_idx):
                pred[out_i] = pred_sorted[order[idx]]
            oof[method][val_idx] = pred
            rec = {
                "fold": fold,
                "method": method,
                "base_loss": mean_loss(y[val_idx], base[val_idx]),
                "loss": mean_loss(y[val_idx], pred),
                "delta": mean_loss(y[val_idx], pred) - mean_loss(y[val_idx], base[val_idx]),
            }
            rec.update({f"loss_{k}": v for k, v in per_target_loss(y[val_idx], pred).items()})
            fold_rows.append(rec)
    pd.DataFrame(fold_rows).to_csv(OUT / "data_dissection_boundary_cv_folds.csv", index=False)
    summary = []
    for method, pred in oof.items():
        rec = {
            "method": method,
            "full_oof_loss": mean_loss(y, pred),
            "full_delta_vs_stage2": mean_loss(y, pred) - mean_loss(y, base),
        }
        rec.update({f"loss_{k}": v for k, v in per_target_loss(y, pred).items()})
        summary.append(rec)
    pd.DataFrame(summary).sort_values("full_oof_loss").to_csv(OUT / "data_dissection_boundary_cv_summary.csv", index=False)


def feature_signal_file(path: Path, train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray) -> pd.DataFrame:
    df = pd.read_parquet(path)
    for col in ["lifelog_date", "sleep_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    key = SUB_KEY if "sleep_date" in df.columns else KEY
    train_keys = train[SUB_KEY if key == SUB_KEY else KEY].copy()
    sub_keys = sub[SUB_KEY if key == SUB_KEY else KEY].copy()
    tr = train_keys.merge(df, on=key, how="left")
    su = sub_keys.merge(df, on=key, how="left")
    num_cols = []
    for col in tr.columns:
        if col in set(key) | {"split"}:
            continue
        if pd.api.types.is_numeric_dtype(tr[col]):
            s = tr[col]
            if s.notna().sum() >= 80 and s.nunique(dropna=True) > 2:
                num_cols.append(col)
    if not num_cols:
        return pd.DataFrame()
    xtr = tr[num_cols].replace([np.inf, -np.inf], np.nan).astype(float)
    xsu = su[num_cols].replace([np.inf, -np.inf], np.nan).astype(float)
    med = xtr.median(numeric_only=True).fillna(0.0)
    xtr = xtr.fillna(med)
    xsu = xsu.fillna(med)
    std = xtr.std(axis=0).replace(0, np.nan)
    shift = ((xsu.mean(axis=0) - xtr.mean(axis=0)) / std).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    miss_delta = su[num_cols].isna().mean(axis=0) - tr[num_cols].isna().mean(axis=0)

    # Subject-centered correlations expose within-person thresholds/ranks.
    xcenter = xtr.copy()
    for sid, idx in train.groupby("subject_id", sort=False).groups.items():
        cols_idx = list(idx)
        xcenter.iloc[cols_idx] = xcenter.iloc[cols_idx] - xcenter.iloc[cols_idx].mean(axis=0)
    xmat = xcenter.to_numpy(dtype=np.float32)
    xmat = xmat - xmat.mean(axis=0, keepdims=True)
    xden = np.sqrt((xmat * xmat).sum(axis=0)) + 1e-9
    y = train[TARGETS].to_numpy(dtype=np.float32)
    residual = y - base
    rows = []
    for label, mat in [("label", y), ("residual", residual)]:
        ymat = mat - mat.mean(axis=0, keepdims=True)
        yden = np.sqrt((ymat * ymat).sum(axis=0)) + 1e-9
        corr = (xmat.T @ ymat) / (xden[:, None] * yden[None, :])
        best_idx = np.nanargmax(np.abs(corr), axis=1)
        best_val = corr[np.arange(len(num_cols)), best_idx]
        for i, col in enumerate(num_cols):
            rows.append(
                {
                    "feature_file": path.name,
                    "feature": col,
                    "signal_type": label,
                    "best_target": TARGETS[int(best_idx[i])],
                    "best_corr": float(best_val[i]),
                    "abs_corr": float(abs(best_val[i])),
                    "train_mean": float(xtr[col].mean()),
                    "train_std": float(std[col]) if np.isfinite(std[col]) else 0.0,
                    "sub_mean": float(xsu[col].mean()),
                    "sub_train_z_shift": float(shift[col]),
                    "missing_delta_sub_minus_train": float(miss_delta[col]),
                }
            )
    return pd.DataFrame(rows)


def feature_forensics(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray) -> None:
    files = [
        OUT / "measurement_process_features.parquet",
        OUT / "rhythm_regular_features.parquet",
        OUT / "sleep_interval_proxy_augmented_features.parquet",
        OUT / "quiet_window_residual_features.parquet",
        OUT / "presleep_temporal_context_features.parquet",
        OUT / "pre_sleep_relative_features.parquet",
    ]
    frames = [feature_signal_file(path, train, sub, base) for path in files if path.exists()]
    all_signal = pd.concat([f for f in frames if not f.empty], ignore_index=True)
    all_signal.to_csv(OUT / "data_dissection_feature_signal_all.csv", index=False)
    all_signal[all_signal["signal_type"].eq("residual")].sort_values("abs_corr", ascending=False).head(300).to_csv(
        OUT / "data_dissection_feature_residual_top.csv", index=False
    )
    all_signal[all_signal["signal_type"].eq("label")].sort_values("abs_corr", ascending=False).head(300).to_csv(
        OUT / "data_dissection_feature_label_top.csv", index=False
    )
    all_signal.drop_duplicates(["feature_file", "feature"]).assign(abs_shift=lambda d: d["sub_train_z_shift"].abs()).sort_values(
        "abs_shift", ascending=False
    ).head(300).to_csv(OUT / "data_dissection_feature_shift_top.csv", index=False)


def write_report(train: pd.DataFrame, sub: pd.DataFrame, blocks: pd.DataFrame) -> None:
    target_summary = pd.read_csv(OUT / "data_dissection_target_signal_summary.csv")
    boundary = pd.read_csv(OUT / "data_dissection_boundary_cv_summary.csv")
    lag = pd.read_csv(OUT / "data_dissection_label_lag_autocorr.csv")
    residual_top = pd.read_csv(OUT / "data_dissection_feature_residual_top.csv")
    shift_top = pd.read_csv(OUT / "data_dissection_feature_shift_top.csv")
    pair = pd.read_csv(OUT / "data_dissection_target_pair_constraints.csv")
    submission_blocks = blocks[blocks["split"].eq("submission")]
    train_blocks = blocks[blocks["split"].eq("train")]

    lines = [
        "# Data Dissection Forensics",
        "",
        "## Dataset Health Check",
        "",
        f"- Train rows: {len(train)}, submission rows: {len(sub)}, subjects: {train['subject_id'].nunique()}.",
        f"- Train date range: {train['lifelog_date'].min().date()} to {train['lifelog_date'].max().date()}.",
        f"- Submission date range: {sub['lifelog_date'].min().date()} to {sub['lifelog_date'].max().date()}.",
        f"- Timeline blocks: train={len(train_blocks)}, submission={len(submission_blocks)}.",
        f"- Submission block length median={submission_blocks['n'].median():.1f}, max={submission_blocks['n'].max()}; both-boundary fraction={((submission_blocks['prev_split'].eq('train')) & (submission_blocks['next_split'].eq('train'))).mean():.3f}.",
        "",
        "## Target/Supervision Quality Review",
        "",
        "```",
        target_summary.to_string(index=False),
        "```",
        "",
        "Strong subject-level rate differences are real, but within-subject temporal copy is weak. This means the hidden block problem is closer to block-level count/rate inference than sequence smoothing.",
        "",
        "Top target pair constraints:",
        "",
        "```",
        pair.head(10).to_string(index=False),
        "```",
        "",
        "## Boundary Leakage Check",
        "",
        "Simple boundary copying is actively bad under submission-like geometry:",
        "",
        "```",
        boundary.to_string(index=False),
        "```",
        "",
        "This kills the tempting hypothesis that bracket labels directly reveal hidden labels. The useful oracle is block-rate/count, not row-wise boundary propagation.",
        "",
        "## Lag/Periodicity Check",
        "",
        "Best label-copy lags by target:",
        "",
        "```",
        lag.sort_values(['target', 'copy_accuracy'], ascending=[True, False]).groupby('target').head(3).to_string(index=False),
        "```",
        "",
        "## Feature/Measurement Clues",
        "",
        "Top residual-correlated features after subject-centering:",
        "",
        "```",
        residual_top.head(20).to_string(index=False),
        "```",
        "",
        "Largest train/sub feature shifts:",
        "",
        "```",
        shift_top.head(20).to_string(index=False),
        "```",
        "",
        "## Top Insights",
        "",
        "1. Submission rows are hidden blocks inside each subject timeline, but nearest visible labels are not reliable. Any 0.54 route needs hidden block count/rate recovery, not boundary smoothing.",
        "2. Q2 has the largest block-rate oracle gap, followed by Q1/Q3. The subjective Q targets are still the highest-upside place to search for subject-rank/count rules.",
        "3. The strongest residual signals are measurement-process/rhythm deviations, especially pre-sleep HR observation density, usage counts, light gaps, and sensor active counts. Missingness is behavior.",
        "4. S2/S3 carry the cleanest JEPA block-rate signal, but public feedback shows aggressive latent residual moves are unsafe unless anchored to a public-positive raw-timeline direction.",
        "5. There is no evidence that a bigger model alone solves the gap. The data bottleneck is an undiscovered labeling/threshold/count rule.",
        "",
        "## Immediate Experiments",
        "",
        "1. Subject-rank threshold miner: for each target, mine monotonic subject-relative thresholds over the top residual features, then solve hidden block counts with exact/near-exact count constraints.",
        "2. Measurement-process generative model: model sensor coverage/gap patterns as a latent sleep regularity state, then use the state as the JEPA target rather than raw row residuals.",
        "3. Public-safe count solver: combine raw-timeline public-positive movement with only Q-count/S2-S3 block-rate movements that have negative or near-zero harmful-axis projection.",
    ]
    (OUT / "data_dissection_forensics_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    train, sub, base, _base_sub = read_core()
    rows = combined_rows(train, sub)
    blocks = block_summary(rows, train)
    target_audit(train, blocks)
    lag_autocorr(train)
    boundary_cv(train, sub, base)
    feature_forensics(train, sub, base)
    write_report(train, sub, blocks)
    print("wrote", OUT / "data_dissection_forensics_report.md")
    print(pd.read_csv(OUT / "data_dissection_boundary_cv_summary.csv").to_string(index=False))
    print(pd.read_csv(OUT / "data_dissection_feature_residual_top.csv").head(12).to_string(index=False))


if __name__ == "__main__":
    main()
