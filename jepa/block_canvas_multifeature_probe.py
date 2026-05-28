from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
STAGE2_PUBLIC = 0.5779449757

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def transformed_matrix(
    fit_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    features: list[tuple[str, str]],
) -> tuple[np.ndarray, np.ndarray]:
    fit_parts = []
    pred_parts = []
    for feature, mode in features:
        a, b = broad.transform_pair(fit_rows, pred_rows, feature, mode)
        fit_parts.append(a)
        pred_parts.append(b)
    if not fit_parts:
        return np.zeros((len(fit_rows), 0)), np.zeros((len(pred_rows), 0))
    return np.column_stack(fit_parts), np.column_stack(pred_parts)


def subject_folds(df: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    return list(broad.qlp.make_subject_blocks(df))


def corrected_oof(
    df: pd.DataFrame,
    sub_df: pd.DataFrame,
    base: np.ndarray,
    base_sub: np.ndarray,
    target: str,
    features: list[tuple[str, str]],
    c_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    j = TARGETS.index(target)
    y = df[target].to_numpy(dtype=int)
    oof = np.zeros(len(df), dtype=float)
    for tr_idx, val_idx in subject_folds(df):
        train_rows = df.iloc[tr_idx].copy()
        val_rows = df.iloc[val_idx].copy()
        x_tr_extra, x_val_extra = transformed_matrix(train_rows, val_rows, features)
        x_tr = np.column_stack([adv.logit(base[tr_idx, j]), x_tr_extra])
        x_val = np.column_stack([adv.logit(base[val_idx, j]), x_val_extra])
        scaler = StandardScaler()
        x_tr = scaler.fit_transform(np.nan_to_num(x_tr, nan=0.0, posinf=0.0, neginf=0.0))
        x_val = scaler.transform(np.nan_to_num(x_val, nan=0.0, posinf=0.0, neginf=0.0))
        if y[tr_idx].min() == y[tr_idx].max():
            oof[val_idx] = y[tr_idx].mean()
            continue
        clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=800)
        clf.fit(x_tr, y[tr_idx])
        oof[val_idx] = clf.predict_proba(x_val)[:, 1]

    x_all_extra, x_sub_extra = transformed_matrix(df, sub_df, features)
    x_all = np.column_stack([adv.logit(base[:, j]), x_all_extra])
    x_sub = np.column_stack([adv.logit(base_sub[:, j]), x_sub_extra])
    scaler = StandardScaler()
    x_all = scaler.fit_transform(np.nan_to_num(x_all, nan=0.0, posinf=0.0, neginf=0.0))
    x_sub = scaler.transform(np.nan_to_num(x_sub, nan=0.0, posinf=0.0, neginf=0.0))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=800)
    clf.fit(x_all, y)
    sub = clf.predict_proba(x_sub)[:, 1]
    return adv.clip(oof), adv.clip(sub)


def axis_stats(sub_pred: np.ndarray, base_sub_df: pd.DataFrame) -> dict[str, float]:
    base = adv.logit(base_sub_df[TARGETS].to_numpy(dtype=float))
    move = adv.logit(sub_pred) - base
    bad_files = [
        ("submission_jepa_latent_residual_probe.csv", 0.5812273278 - STAGE2_PUBLIC),
        ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862 - STAGE2_PUBLIC),
    ]
    bad_parts = []
    weights = []
    for file_name, weight in bad_files:
        df = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        bad_parts.append(adv.logit(df[TARGETS].to_numpy(dtype=float)) - base)
        weights.append(max(weight, 1e-9))
    bad_axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(weights))
    raw = pd.read_csv(OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    good_axis = adv.logit(raw[TARGETS].to_numpy(dtype=float)) - base
    out: dict[str, float] = {}
    for name, axis in [("jepa_bad", bad_axis), ("raw_good", good_axis)]:
        m = move.reshape(-1)
        a = axis.reshape(-1)
        out[f"{name}_ratio"] = float(np.dot(m, a) / max(float(np.dot(a, a)), 1e-12))
        out[f"{name}_cos"] = float(np.dot(m, a) / max(float(np.linalg.norm(m) * np.linalg.norm(a)), 1e-12))
    return out


def choose_feature_sets(scan: pd.DataFrame, k: int) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    for target in TARGETS:
        rows = scan[(scan["target"].eq(target)) & (scan["best_weight"] > 0)].sort_values(
            ["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True]
        )
        picked: list[tuple[str, str]] = []
        seen = set()
        for row in rows.itertuples(index=False):
            key = (str(row.feature), str(row.mode))
            if key in seen:
                continue
            picked.append(key)
            seen.add(key)
            if len(picked) >= k:
                break
        out[target] = picked
    return out


def build_variant(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub_arr: np.ndarray,
    feature_sets: dict[str, list[tuple[str, str]]],
    c_value: float,
    no_q2: bool,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    pred = base.copy()
    sub_pred = base_sub_arr.copy()
    rows = []
    for target in TARGETS:
        j = TARGETS.index(target)
        if no_q2 and target == "Q2":
            rows.append({"target": target, "features": 0, "c_value": c_value, "blend_weight": 0.0, "target_loss": broad.loss_col(y[:, j], pred[:, j]), "delta_vs_base": 0.0})
            continue
        corr, sub_corr = corrected_oof(train_feat, sub_feat, base, base_sub_arr, target, feature_sets[target], c_value)
        losses = [broad.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corr) for w in broad.GRID]
        best_i = int(np.argmin(losses))
        w = float(broad.GRID[best_i])
        base_loss = broad.loss_col(y[:, j], base[:, j])
        if losses[best_i] >= base_loss:
            w = 0.0
        pred[:, j] = adv.clip((1.0 - w) * base[:, j] + w * corr)
        sub_pred[:, j] = adv.clip((1.0 - w) * base_sub_arr[:, j] + w * sub_corr)
        rows.append(
            {
                "target": target,
                "features": len(feature_sets[target]),
                "c_value": c_value,
                "blend_weight": w,
                "target_loss": broad.loss_col(y[:, j], pred[:, j]),
                "delta_vs_base": broad.loss_col(y[:, j], pred[:, j]) - base_loss,
            }
        )
    return adv.clip(pred), adv.clip(sub_pred), pd.DataFrame(rows)


def emit_scaled(
    name_prefix: str,
    base: np.ndarray,
    base_sub_df: pd.DataFrame,
    pred: np.ndarray,
    sub_pred: np.ndarray,
    y: np.ndarray,
    scales: list[float],
) -> list[dict[str, float | str]]:
    rows = []
    base_loss = adv.mean_loss(y, base)
    base_logit = adv.logit(base)
    sub_base = base_sub_df[TARGETS].to_numpy(dtype=float)
    sub_base_logit = adv.logit(sub_base)
    move = adv.logit(pred) - base_logit
    sub_move = adv.logit(sub_pred) - sub_base_logit
    for scale in scales:
        out_oof = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + scale * move))))
        out_sub = adv.clip(1.0 / (1.0 + np.exp(-(sub_base_logit + scale * sub_move))))
        file_name = f"submission_{name_prefix}_scale{str(scale).replace('.', 'p')}.csv"
        out = base_sub_df.copy()
        out[TARGETS] = out_sub
        out.to_csv(OUT / file_name, index=False)
        mloss = adv.mean_loss(y, out_oof)
        rows.append(
            {
                "candidate": file_name,
                "scale": scale,
                "oof_loss": mloss,
                "oof_delta_vs_stage2": mloss - base_loss,
                **axis_stats(out_sub, base_sub_df),
            }
        )
    return rows


def main() -> None:
    train, _sub, base, base_sub = adv.read_data()
    y = train[TARGETS].to_numpy(dtype=int)
    train_feat = pd.read_parquet(OUT / "block_canvas_jepa_train_features.parquet")
    sub_feat = pd.read_parquet(OUT / "block_canvas_jepa_submission_features.parquet")
    scan = pd.read_csv(OUT / "block_canvas_jepa_scan.csv")
    base_sub_arr = base_sub[TARGETS].to_numpy(dtype=float)
    summary_rows = []
    detail_frames = []
    for k in [3, 5, 8]:
        feature_sets = choose_feature_sets(scan, k)
        for c_value in [0.02, 0.05, 0.10]:
            for no_q2 in [True, False]:
                pred, sub_pred, details = build_variant(train_feat, sub_feat, base, base_sub_arr, feature_sets, c_value, no_q2=no_q2)
                label = f"block_canvas_multifeature_k{k}_c{str(c_value).replace('.', 'p')}_{'noq2' if no_q2 else 'all'}"
                details.insert(0, "variant", label)
                detail_frames.append(details)
                rows = emit_scaled(label, base, base_sub, pred, sub_pred, y, [0.35, 0.5, 0.75, 1.0])
                for row in rows:
                    row["variant"] = label
                    row["k"] = k
                    row["c_value"] = c_value
                    row["no_q2"] = no_q2
                summary_rows.extend(rows)
    summary = pd.DataFrame(summary_rows).sort_values(["jepa_bad_ratio", "oof_delta_vs_stage2"])
    details = pd.concat(detail_frames, ignore_index=True)
    summary.to_csv(OUT / "block_canvas_multifeature_candidate_summary.csv", index=False)
    details.to_csv(OUT / "block_canvas_multifeature_target_details.csv", index=False)
    report = [
        "# Block-Canvas Multi-Feature Probe",
        "",
        "Uses several Block-Canvas JEPA anomaly features jointly per target, with subject-block OOF logistic probes and scaled logit residual export.",
        "",
        "## Candidate Summary",
        "",
        summary.head(80).to_csv(index=False),
        "",
        "## Target Details",
        "",
        details.head(100).to_csv(index=False),
    ]
    (OUT / "block_canvas_multifeature_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(30).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
