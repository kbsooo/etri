from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

STAGE2_PUBLIC = 0.5779449757
PUBLIC_FEEDBACK = {
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
}

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def finite_float(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def zscale_fit_transform(x: np.ndarray, n_components: int, seed: int) -> tuple[np.ndarray, StandardScaler, PCA]:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite_float(x))
    k = min(n_components, xs.shape[0] - 1, xs.shape[1])
    pca = PCA(n_components=k, random_state=seed, svd_solver="randomized")
    z = pca.fit_transform(xs)
    return z.astype(np.float32), scaler, pca


def ridge_predict(context: np.ndarray, target: np.ndarray, alpha: float = 30.0) -> np.ndarray:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite_float(context))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xs, finite_float(target))
    return model.predict(xs)


def neighbor_matrix(rows: pd.DataFrame, z: np.ndarray, shifts: list[int]) -> tuple[np.ndarray, list[str]]:
    parts = []
    names = []
    sids = rows["subject_id"].astype(str).to_numpy()
    dates = pd.to_datetime(rows["lifelog_date"]).to_numpy()
    for shift in shifts:
        arr = np.zeros_like(z)
        gap = np.full((len(rows), 1), 99.0, dtype=np.float32)
        valid = np.zeros((len(rows), 1), dtype=np.float32)
        for _sid, idx in rows.groupby("subject_id", sort=False).indices.items():
            ii = np.asarray(idx, dtype=int)
            for local, row_i in enumerate(ii):
                other_local = local + shift
                if 0 <= other_local < len(ii):
                    other_i = ii[other_local]
                    arr[row_i] = z[other_i]
                    gap[row_i, 0] = abs((pd.Timestamp(dates[row_i]) - pd.Timestamp(dates[other_i])).days)
                    valid[row_i, 0] = 1.0
        parts.extend([arr, gap, valid])
        prefix = f"shift_{shift:+d}"
        names.extend([f"{prefix}_z{i:02d}" for i in range(z.shape[1])] + [f"{prefix}_gap", f"{prefix}_valid"])
    subject_mean = np.zeros_like(z)
    subject_std = np.zeros_like(z)
    for _sid, idx in rows.groupby("subject_id", sort=False).indices.items():
        ii = np.asarray(idx, dtype=int)
        subject_mean[ii] = z[ii].mean(axis=0, keepdims=True)
        subject_std[ii] = z[ii].std(axis=0, keepdims=True)
    parts.extend([subject_mean, subject_std])
    names.extend([f"subject_mean_z{i:02d}" for i in range(z.shape[1])] + [f"subject_std_z{i:02d}" for i in range(z.shape[1])])
    cal = np.column_stack(
        [
            rows["subject_phase"].to_numpy(dtype=float),
            rows["is_weekend"].to_numpy(dtype=float),
            np.sin(2.0 * np.pi * rows["dow"].to_numpy(dtype=float) / 7.0),
            np.cos(2.0 * np.pi * rows["dow"].to_numpy(dtype=float) / 7.0),
        ]
    )
    parts.append(cal)
    names.extend(["phase", "weekend", "dow_sin", "dow_cos"])
    return np.hstack(parts).astype(np.float32), names


def add_latent_block(out: pd.DataFrame, prefix: str, arr: np.ndarray, max_cols: int | None = None) -> None:
    k = arr.shape[1] if max_cols is None else min(max_cols, arr.shape[1])
    for i in range(k):
        out[f"{prefix}_{i:02d}"] = arr[:, i]


def build_neighbor_jepa(rows: pd.DataFrame, canvas: np.ndarray, n_pca: int = 32) -> pd.DataFrame:
    flat = canvas.reshape(len(rows), -1)
    z, _scaler, _pca = zscale_fit_transform(flat, n_pca, seed=270101)
    out = rows[SUB_KEY + ["split", "train_idx", "sub_idx"]].copy()
    add_latent_block(out, "rtday_target", z, 16)
    variants = {
        "both": [-2, -1, 1, 2],
        "prev": [-3, -2, -1],
        "next": [1, 2, 3],
    }
    for name, shifts in variants.items():
        ctx, _ctx_names = neighbor_matrix(rows, z, shifts)
        pred = ridge_predict(ctx, z, alpha=50.0)
        err = z - pred
        add_latent_block(out, f"rtday_{name}_pred", pred, 16)
        add_latent_block(out, f"rtday_{name}_err", err, 16)
        add_latent_block(out, f"rtday_{name}_abserr", np.abs(err), 12)
        out[f"rtday_{name}_err_norm"] = np.linalg.norm(err, axis=1)
        out[f"rtday_{name}_target_norm"] = np.linalg.norm(z, axis=1)
        out[f"rtday_{name}_pred_norm"] = np.linalg.norm(pred, axis=1)
        denom = np.linalg.norm(z, axis=1) * np.linalg.norm(pred, axis=1)
        out[f"rtday_{name}_cos"] = np.sum(z * pred, axis=1) / np.maximum(denom, 1e-8)
    return out


def build_modality_bridge(rows: pd.DataFrame, canvas: np.ndarray) -> pd.DataFrame:
    mobile = canvas[:, :9, :, :].reshape(len(rows), -1)
    wear = canvas[:, 9:, :, :].reshape(len(rows), -1)
    z_m, _sm, _pm = zscale_fit_transform(mobile, 20, seed=270211)
    z_w, _sw, _pw = zscale_fit_transform(wear, 16, seed=270212)
    out = rows[SUB_KEY + ["split", "train_idx", "sub_idx"]].copy()
    pred_w = ridge_predict(z_m, z_w, alpha=40.0)
    err_w = z_w - pred_w
    pred_m = ridge_predict(z_w, z_m, alpha=40.0)
    err_m = z_m - pred_m
    add_latent_block(out, "rtmod_wear_target", z_w, 12)
    add_latent_block(out, "rtmod_mobile_target", z_m, 12)
    add_latent_block(out, "rtmod_m2w_pred", pred_w, 12)
    add_latent_block(out, "rtmod_m2w_err", err_w, 12)
    add_latent_block(out, "rtmod_m2w_abserr", np.abs(err_w), 12)
    add_latent_block(out, "rtmod_w2m_pred", pred_m, 12)
    add_latent_block(out, "rtmod_w2m_err", err_m, 12)
    add_latent_block(out, "rtmod_w2m_abserr", np.abs(err_m), 12)
    for prefix, err, tgt, pred in [("m2w", err_w, z_w, pred_w), ("w2m", err_m, z_m, pred_m)]:
        out[f"rtmod_{prefix}_err_norm"] = np.linalg.norm(err, axis=1)
        out[f"rtmod_{prefix}_target_norm"] = np.linalg.norm(tgt, axis=1)
        out[f"rtmod_{prefix}_pred_norm"] = np.linalg.norm(pred, axis=1)
        denom = np.linalg.norm(tgt, axis=1) * np.linalg.norm(pred, axis=1)
        out[f"rtmod_{prefix}_cos"] = np.sum(tgt * pred, axis=1) / np.maximum(denom, 1e-8)
    return out


def window_summary(canvas: np.ndarray, bins: slice) -> np.ndarray:
    x = canvas[:, :, bins, :]
    mean = x.mean(axis=2)
    std = x.std(axis=2)
    mx = x.max(axis=2)
    mn = x.min(axis=2)
    energy = np.sqrt((x**2).mean(axis=2))
    return np.concatenate([mean, std, mx, mn, energy], axis=1).reshape(len(canvas), -1)


def build_window_bridge(rows: pd.DataFrame, canvas: np.ndarray) -> pd.DataFrame:
    windows = {
        "day": slice(0, 12),       # 12:00-18:00
        "evening": slice(12, 24),  # 18:00-24:00
        "night": slice(24, 40),    # 00:00-08:00
        "morning": slice(40, 48),  # 08:00-12:00
    }
    summaries = {name: window_summary(canvas, sl) for name, sl in windows.items()}
    z = {}
    for name, mat in summaries.items():
        z[name], _s, _p = zscale_fit_transform(mat, 16, seed=270300 + len(name))
    out = rows[SUB_KEY + ["split", "train_idx", "sub_idx"]].copy()
    context = np.hstack([z["day"], z["evening"], z["morning"]])
    target = z["night"]
    pred = ridge_predict(context, target, alpha=50.0)
    err = target - pred
    add_latent_block(out, "rtwin_night_target", target, 12)
    add_latent_block(out, "rtwin_context", context, 16)
    add_latent_block(out, "rtwin_night_pred", pred, 12)
    add_latent_block(out, "rtwin_night_err", err, 12)
    add_latent_block(out, "rtwin_night_abserr", np.abs(err), 12)
    out["rtwin_night_err_norm"] = np.linalg.norm(err, axis=1)
    out["rtwin_night_target_norm"] = np.linalg.norm(target, axis=1)
    out["rtwin_night_pred_norm"] = np.linalg.norm(pred, axis=1)
    denom = np.linalg.norm(target, axis=1) * np.linalg.norm(pred, axis=1)
    out["rtwin_night_cos"] = np.sum(target * pred, axis=1) / np.maximum(denom, 1e-8)
    # Sensor-family night anomaly summaries keep interpretability when PCA signs are unstable.
    mobile_night = canvas[:, :9, 24:40, :]
    wear_night = canvas[:, 9:, 24:40, :]
    out["rtwin_mobile_night_energy"] = np.sqrt((mobile_night**2).mean(axis=(1, 2, 3)))
    out["rtwin_wear_night_energy"] = np.sqrt((wear_night**2).mean(axis=(1, 2, 3)))
    out["rtwin_wear_mobile_energy_ratio"] = out["rtwin_wear_night_energy"] / np.maximum(out["rtwin_mobile_night_energy"], 1e-6)
    return out


def public_feedback_axis(file_name: str) -> dict[str, float]:
    try:
        stage2 = pd.read_csv(adv.BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        cand_path = OUT / file_name
        cand = pd.read_csv(cand_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        stage2_logit = adv.logit(stage2[TARGETS].to_numpy(dtype=float))
        move = adv.logit(cand[TARGETS].to_numpy(dtype=float)) - stage2_logit
        bad_parts = []
        weights = []
        for bad_name, score in PUBLIC_FEEDBACK.items():
            path = OUT / bad_name
            if not path.exists():
                continue
            bad = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
            bad_move = adv.logit(bad[TARGETS].to_numpy(dtype=float)) - stage2_logit
            bad_parts.append(bad_move)
            weights.append(max(score - STAGE2_PUBLIC, 1e-9))
        if not bad_parts:
            return {"jepa_bad_axis_ratio": np.nan, "jepa_bad_axis_cos": np.nan}
        axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(weights))
        flat_move = move.reshape(-1)
        flat_axis = axis.reshape(-1)
        denom = max(float(np.dot(flat_axis, flat_axis)), 1e-12)
        cos = float(np.dot(flat_move, flat_axis) / max(np.linalg.norm(flat_move) * np.linalg.norm(flat_axis), 1e-12))
        return {
            "jepa_bad_axis_ratio": float(np.dot(flat_move, flat_axis) / denom),
            "jepa_bad_axis_cos": cos,
        }
    except Exception:
        return {"jepa_bad_axis_ratio": np.nan, "jepa_bad_axis_cos": np.nan}


def scan_and_submit(train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cols = broad.finite_numeric_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, TARGETS, top_n=35)
    pre.to_csv(OUT / "raw_timeline_jepa_rescue_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = broad.loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20, 0.50]:
            corrected = broad.oof_corrected(train_feat, base, target, feature, mode, c_value)
            losses = [broad.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": broad.loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_feat, y, base, corrected, j))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.56)
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.00035 and row["mean_delta"] <= -0.00005 and row["win_rate"] >= 0.62)
            rows.append(row)
    scan = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    scan.to_csv(OUT / "raw_timeline_jepa_rescue_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, file_name: str) -> tuple[np.ndarray, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
        used = []
        for op in ops.itertuples(index=False):
            target = str(op.target)
            if target in {u["target"] for u in used}:
                continue
            j = TARGETS.index(target)
            corrected = broad.oof_corrected(train_feat, pred, target, str(op.feature), str(op.mode), float(op.c_value))
            pred[:, j] = adv.clip((1.0 - float(op.best_weight)) * pred[:, j] + float(op.best_weight) * corrected)
            sub_corr = broad.fit_corrected(train_feat, sub_feat, pred, sub_pred, target, str(op.feature), str(op.mode), float(op.c_value))
            sub_pred[:, j] = adv.clip((1.0 - float(op.best_weight)) * sub_pred[:, j] + float(op.best_weight) * sub_corr)
            used.append(
                {
                    "target": target,
                    "feature": str(op.feature),
                    "mode": str(op.mode),
                    "c_value": float(op.c_value),
                    "weight": float(op.best_weight),
                    "delta_vs_base": float(op.delta_vs_base),
                    "mean_delta": float(op.mean_delta),
                    "win_rate": float(op.win_rate),
                }
            )
        out = base_sub.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / file_name, index=False)
        pd.DataFrame(used).to_csv(OUT / file_name.replace("submission_", "").replace(".csv", "_ops.csv"), index=False)
        return pred, pd.DataFrame(used)

    strict = scan[(scan["passes_strict"]) & (scan["best_weight"] > 0)].sort_values("delta_vs_base")
    loose = scan[((scan["passes_strict"] | scan["passes_loose"]) & (scan["best_weight"] > 0))].sort_values(["passes_strict", "delta_vs_base"], ascending=[False, True])
    top = scan[scan["best_weight"] > 0].sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    candidates = []
    for label, ops, file_name in [
        ("strict", strict, "submission_raw_timeline_jepa_rescue_strict.csv"),
        ("loose", loose, "submission_raw_timeline_jepa_rescue_loose.csv"),
        ("top_probe", top, "submission_raw_timeline_jepa_rescue_top_probe.csv"),
    ]:
        pred, used = apply_ops(ops, file_name)
        mean_loss = adv.mean_loss(y, pred)
        row = {
            "candidate": file_name,
            "class": label,
            "ops": int(len(used)),
            "oof_loss": mean_loss,
            "oof_delta_vs_stage2": mean_loss - adv.mean_loss(y, base),
            **adv.public_axis_for(file_name),
            **public_feedback_axis(file_name),
        }
        candidates.append(row)
    summary = pd.DataFrame(candidates)
    summary.to_csv(OUT / "raw_timeline_jepa_rescue_candidate_summary.csv", index=False)
    cv_rows = []
    for r in summary.itertuples(index=False):
        pred_file = OUT / str(r.candidate)
        sub = pd.read_csv(pred_file)
        cv_rows.append({"candidate": str(r.candidate), "ops": int(r.ops), "oof_loss": float(r.oof_loss), "oof_delta_vs_stage2": float(r.oof_delta_vs_stage2)})
    pd.DataFrame(cv_rows).to_csv(OUT / "raw_timeline_jepa_rescue_cv_estimate.csv", index=False)
    return scan, summary


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, _base_all = adv.build_row_representation(train, sub, base, base_sub)
    canvas, sensors = adv.build_raw_canvas(rows)
    parts = [
        build_neighbor_jepa(rows, canvas),
        build_modality_bridge(rows, canvas),
        build_window_bridge(rows, canvas),
    ]
    feat = parts[0]
    for part in parts[1:]:
        feat = feat.merge(part.drop(columns=SUB_KEY + ["split", "train_idx", "sub_idx"]), left_index=True, right_index=True)
    train_part = feat[feat["split"].eq("train")].sort_values("train_idx").reset_index(drop=True)
    sub_part = feat[feat["split"].eq("submission")].sort_values("sub_idx").reset_index(drop=True)
    train_feat = train[SUB_KEY + TARGETS].merge(train_part.drop(columns=["split", "train_idx", "sub_idx"]), on=SUB_KEY, how="left")
    sub_feat = sub[SUB_KEY].merge(sub_part.drop(columns=["split", "train_idx", "sub_idx"]), on=SUB_KEY, how="left")
    train_feat.to_parquet(OUT / "raw_timeline_jepa_rescue_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / "raw_timeline_jepa_rescue_submission_features.parquet", index=False)
    scan, summary = scan_and_submit(train_feat, sub_feat, base, base_sub)
    report = [
        "# Raw Timeline JEPA Rescue",
        "",
        "Public feedback says previous JEPA residual moves were harmful. This run changes the raw objective from same-day patch prediction to subject-neighbor day prediction, mobile/wearable bridge prediction, and day/evening-to-night rectangle prediction.",
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(40).to_csv(index=False),
        "",
        "## Public Feedback Used As Bad Axis",
        "",
        pd.DataFrame([{"candidate": k, "public_lb": v, "delta_vs_stage2_public": v - STAGE2_PUBLIC} for k, v in PUBLIC_FEEDBACK.items()]).to_csv(index=False),
    ]
    (OUT / "raw_timeline_jepa_rescue_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
