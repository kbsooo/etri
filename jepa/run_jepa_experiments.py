from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(ANALYSIS))
import broad_feature_addon_builder as stage2  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_base() -> tuple[np.ndarray, pd.DataFrame]:
    base_oof = ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
    base_sub = ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
    return clip(np.load(base_oof)), pd.read_csv(base_sub, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def numeric_feature_cols(df: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + SUB_KEY + ["split"])
    cols: list[str] = []
    for col in df.columns:
        if col in excluded:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def fit_scale(train: pd.DataFrame, sub: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    all_df = pd.concat([train[cols], sub[cols]], axis=0, ignore_index=True)
    med = all_df.median(numeric_only=True).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    all_vals = all_df.replace([np.inf, -np.inf], np.nan).fillna(med).to_numpy(dtype=float)
    scaler = StandardScaler()
    all_x = scaler.fit_transform(all_vals)
    all_x = np.nan_to_num(all_x, nan=0.0, posinf=0.0, neginf=0.0)
    return all_x[: len(train)], all_x[len(train) :]


def time_token(name: str) -> str:
    for token in ["pre6h", "pre5h", "pre4h", "pre3h", "pre2h", "pre1h", "early", "morning", "afternoon", "evening", "late", "all"]:
        if token in name:
            return token
    return "other"


def sensor_token(col: str) -> str:
    prefix, rest = col.split("__", 1) if "__" in col else ("base", col)
    if prefix in {"proxy", "quiet", "wifi", "ble"}:
        return prefix
    if prefix == "presleep":
        for token in ["hr", "mlight", "wlight", "charge", "screen", "usage", "ble", "wifi", "activity", "ambience"]:
            if token in rest:
                return f"presleep_{token}"
        return "presleep_other"
    if prefix == "prectx":
        for token in ["hr", "mlight", "wlight", "charge", "screen", "usage", "ble", "wifi", "activity", "ambience"]:
            if token in rest:
                return f"prectx_{token}"
        return "prectx_other"
    for token in [
        "phone_charge",
        "phone_activity",
        "phone_light",
        "phone_screen",
        "watch_hr",
        "watch_light",
        "watch_pedo",
        "usage",
        "wifi",
        "ble",
        "gps",
        "ambience",
    ]:
        if rest.startswith(token) or token in rest:
            return token
    return prefix


def make_groups(cols: list[str]) -> dict[str, dict[str, list[int]]]:
    schemes: dict[str, dict[str, list[int]]] = {"modality": {}, "time": {}, "sensor_time": {}, "prefix": {}}
    for idx, col in enumerate(cols):
        prefix = col.split("__", 1)[0] if "__" in col else "base"
        sensor = sensor_token(col)
        t = time_token(col)
        keys = {
            "modality": sensor,
            "time": t,
            "sensor_time": f"{sensor}__{t}",
            "prefix": prefix,
        }
        for scheme, key in keys.items():
            schemes[scheme].setdefault(key, []).append(idx)

    filtered: dict[str, dict[str, list[int]]] = {}
    for scheme, groups in schemes.items():
        min_cols = 4 if scheme == "sensor_time" else 8
        keep = {name: idxs for name, idxs in groups.items() if len(idxs) >= min_cols}
        if scheme == "sensor_time":
            keep = dict(sorted(keep.items(), key=lambda kv: len(kv[1]), reverse=True)[:30])
        filtered[scheme] = keep
    return filtered


def pca_latents(x_all: np.ndarray, groups: dict[str, list[int]], max_components: int) -> tuple[dict[str, np.ndarray], list[dict[str, object]]]:
    latents: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []
    n = x_all.shape[0]
    for name, idxs in groups.items():
        block = x_all[:, idxs]
        n_comp = int(min(max_components, max(1, len(idxs) // 8), block.shape[1], n - 1))
        if n_comp < 1:
            continue
        pca = PCA(n_components=n_comp, random_state=260991)
        z = pca.fit_transform(block)
        z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)
        latents[name] = z
        rows.append(
            {
                "group": name,
                "columns": len(idxs),
                "components": n_comp,
                "explained_variance": float(np.sum(pca.explained_variance_ratio_)),
            }
        )
    return latents, rows


def add_latent_prediction_features(
    out: dict[str, np.ndarray],
    scheme: str,
    x_all: np.ndarray,
    groups: dict[str, list[int]],
    max_components: int,
    alpha: float,
) -> list[dict[str, object]]:
    latents, pca_rows = pca_latents(x_all, groups, max_components=max_components)
    names = sorted(latents)
    if len(names) < 3:
        return pca_rows
    concat = np.concatenate([latents[n] for n in names], axis=1)
    context_scaler = StandardScaler()
    concat = context_scaler.fit_transform(concat)
    concat = np.nan_to_num(concat, nan=0.0, posinf=0.0, neginf=0.0)

    offsets: dict[str, tuple[int, int]] = {}
    pos = 0
    for name in names:
        k = latents[name].shape[1]
        offsets[name] = (pos, pos + k)
        pos += k

    for name in names:
        start, end = offsets[name]
        target = concat[:, start:end]
        context = np.concatenate([concat[:, :start], concat[:, end:]], axis=1)
        pred = Ridge(alpha=alpha, solver="lsqr").fit(context, target).predict(context)
        if pred.ndim == 1:
            pred = pred.reshape(-1, 1)
        if target.ndim == 1:
            target = target.reshape(-1, 1)
        resid = target - pred
        target_norm = np.linalg.norm(target, axis=1)
        pred_norm = np.linalg.norm(pred, axis=1)
        resid_norm = np.linalg.norm(resid, axis=1)
        denom = np.maximum(target_norm * pred_norm, 1e-9)
        cos = np.sum(target * pred, axis=1) / denom
        safe_name = name.replace("/", "_").replace(" ", "_")
        base = f"jepa_{scheme}__{safe_name}"
        out[f"{base}__target_norm"] = target_norm
        out[f"{base}__pred_norm"] = pred_norm
        out[f"{base}__resid_norm"] = resid_norm
        out[f"{base}__resid_abs_mean"] = np.mean(np.abs(resid), axis=1)
        out[f"{base}__cos"] = cos
        for k in range(min(3, target.shape[1])):
            out[f"{base}__target_pc{k}"] = target[:, k]
            out[f"{base}__pred_pc{k}"] = pred[:, k]
            out[f"{base}__resid_pc{k}"] = resid[:, k]
    for row in pca_rows:
        row["scheme"] = scheme
    return pca_rows


def add_image_grid_features(out: dict[str, np.ndarray], x_all: np.ndarray, cols: list[str], min_cell_cols: int = 3) -> pd.DataFrame:
    sensors = sorted({sensor_token(c) for c in cols})
    times = ["early", "morning", "afternoon", "evening", "late", "all", "pre6h", "pre3h", "pre2h", "pre1h", "other"]
    cell_map: dict[tuple[str, str], list[int]] = {}
    for idx, col in enumerate(cols):
        cell_map.setdefault((sensor_token(col), time_token(col)), []).append(idx)

    cells = [(s, t, idxs) for (s, t), idxs in cell_map.items() if len(idxs) >= min_cell_cols and s in sensors and t in times]
    rows: list[dict[str, object]] = []
    for sensor, t, idxs in cells:
        cell_value = x_all[:, idxs].mean(axis=1)
        row_context = []
        col_context = []
        for tt in times:
            if tt != t and (sensor, tt) in cell_map and len(cell_map[(sensor, tt)]) >= min_cell_cols:
                row_context.append(x_all[:, cell_map[(sensor, tt)]].mean(axis=1))
        for ss in sensors:
            if ss != sensor and (ss, t) in cell_map and len(cell_map[(ss, t)]) >= min_cell_cols:
                col_context.append(x_all[:, cell_map[(ss, t)]].mean(axis=1))
        if len(row_context) + len(col_context) < 3:
            continue
        context = np.column_stack(row_context + col_context)
        pred = Ridge(alpha=10.0, solver="lsqr").fit(context, cell_value).predict(context)
        resid = cell_value - pred
        safe = f"{sensor}__{t}".replace("/", "_")
        out[f"jepa_grid__{safe}__value"] = cell_value
        out[f"jepa_grid__{safe}__pred"] = pred
        out[f"jepa_grid__{safe}__resid"] = resid
        rows.append({"cell": safe, "columns": len(idxs), "context_width": context.shape[1], "resid_std": float(np.std(resid))})
    return pd.DataFrame(rows)


def add_temporal_features(out: dict[str, np.ndarray], rows: pd.DataFrame, x_all: np.ndarray) -> pd.DataFrame:
    z = PCA(n_components=min(16, x_all.shape[0] - 1, x_all.shape[1]), random_state=260991).fit_transform(x_all)
    z = StandardScaler().fit_transform(z)
    z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)
    context = np.zeros((len(rows), z.shape[1] * 2 + 4), dtype=float)
    meta_rows = []
    order = rows.sort_values(["subject_id", "lifelog_date"]).index.to_numpy()
    sorted_rows = rows.loc[order].reset_index()
    z_sorted = z[order]
    for sid, sub_df in sorted_rows.groupby("subject_id", sort=False):
        local_pos = sub_df.index.to_numpy()
        original_idx = sub_df["index"].to_numpy()
        for i, pos in enumerate(local_pos):
            prev_z = z_sorted[local_pos[i - 1]] if i > 0 else np.zeros(z.shape[1])
            next_z = z_sorted[local_pos[i + 1]] if i + 1 < len(local_pos) else np.zeros(z.shape[1])
            prev_gap = 0.0
            next_gap = 0.0
            if i > 0:
                prev_gap = float((sub_df.iloc[i]["lifelog_date"] - sub_df.iloc[i - 1]["lifelog_date"]).days)
            if i + 1 < len(local_pos):
                next_gap = float((sub_df.iloc[i + 1]["lifelog_date"] - sub_df.iloc[i]["lifelog_date"]).days)
            context[original_idx, :] = np.r_[prev_z, next_z, prev_gap, next_gap, float(i), float(len(local_pos))]
    pred = Ridge(alpha=20.0, solver="lsqr").fit(context, z).predict(context)
    resid = z - pred
    out["jepa_temporal__neighbor_resid_norm"] = np.linalg.norm(resid, axis=1)
    out["jepa_temporal__neighbor_resid_abs_mean"] = np.mean(np.abs(resid), axis=1)
    out["jepa_temporal__neighbor_pred_norm"] = np.linalg.norm(pred, axis=1)
    out["jepa_temporal__neighbor_target_norm"] = np.linalg.norm(z, axis=1)
    out["jepa_temporal__neighbor_cos"] = np.sum(z * pred, axis=1) / np.maximum(np.linalg.norm(z, axis=1) * np.linalg.norm(pred, axis=1), 1e-9)
    for k in range(min(6, z.shape[1])):
        out[f"jepa_temporal__target_pc{k}"] = z[:, k]
        out[f"jepa_temporal__pred_pc{k}"] = pred[:, k]
        out[f"jepa_temporal__resid_pc{k}"] = resid[:, k]
    meta_rows.append({"latent_components": int(z.shape[1]), "context_width": int(context.shape[1])})
    return pd.DataFrame(meta_rows)


def make_jepa_features(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    cols = numeric_feature_cols(pd.concat([train_feat, sub_feat], axis=0, ignore_index=True))
    x_tr, x_sub = fit_scale(train_feat, sub_feat, cols)
    x_all = np.vstack([x_tr, x_sub])
    all_rows = pd.concat([train_feat[SUB_KEY], sub_feat[SUB_KEY]], axis=0, ignore_index=True)
    all_rows["lifelog_date"] = pd.to_datetime(all_rows["lifelog_date"])

    groups_by_scheme = make_groups(cols)
    feature_map: dict[str, np.ndarray] = {}
    pca_meta: list[dict[str, object]] = []
    print("building modality JEPA features", flush=True)
    pca_meta += add_latent_prediction_features(feature_map, "modality", x_all, groups_by_scheme["modality"], 6, 10.0)
    print("building time JEPA features", flush=True)
    pca_meta += add_latent_prediction_features(feature_map, "time", x_all, groups_by_scheme["time"], 6, 10.0)
    print("building sensor_time JEPA features", flush=True)
    pca_meta += add_latent_prediction_features(feature_map, "sensor_time", x_all, groups_by_scheme["sensor_time"], 4, 15.0)
    print("building prefix JEPA features", flush=True)
    pca_meta += add_latent_prediction_features(feature_map, "prefix", x_all, groups_by_scheme["prefix"], 6, 10.0)
    print("building image-grid JEPA features", flush=True)
    grid_meta = add_image_grid_features(feature_map, x_all, cols)
    print("building temporal JEPA features", flush=True)
    temporal_meta = add_temporal_features(feature_map, all_rows, x_all)

    feature_df = pd.concat([all_rows.reset_index(drop=True), pd.DataFrame(feature_map)], axis=1)
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan)
    train_keys = train_feat[SUB_KEY].reset_index(drop=True)
    sub_keys = sub_feat[SUB_KEY].reset_index(drop=True)
    train_out = train_keys.merge(feature_df, on=SUB_KEY, how="left")
    sub_out = sub_keys.merge(feature_df, on=SUB_KEY, how="left")

    meta = {
        "input_feature_count": len(cols),
        "jepa_feature_count": int(feature_df.shape[1] - len(SUB_KEY)),
        "groups": {k: {kk: len(vv) for kk, vv in groups_by_scheme[k].items()} for k in groups_by_scheme},
        "pca_meta_rows": len(pca_meta),
        "grid_cells": int(len(grid_meta)),
        "temporal": temporal_meta.to_dict(orient="records"),
    }
    pd.DataFrame(pca_meta).to_csv(OUT / "jepa_pca_group_meta.csv", index=False)
    grid_meta.to_csv(OUT / "jepa_grid_meta.csv", index=False)
    return train_out, sub_out, meta


@dataclass(frozen=True)
class SelectedOp:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float


def scan_features(train_raw: pd.DataFrame, jepa_train: pd.DataFrame, base: np.ndarray, top_n: int = 12) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = train_raw[SUB_KEY + TARGETS].merge(jepa_train, on=SUB_KEY, how="left")
    cols = broad.finite_numeric_cols(df)
    y = df[TARGETS].to_numpy(dtype=int)
    pre = broad.prefilter(df, base, cols, TARGETS, top_n=top_n)
    pre.to_csv(OUT / "jepa_single_feature_prefilter.csv", index=False)
    print(f"prefiltered {len(pre)} candidates from {len(cols)} JEPA features", flush=True)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.20]:
            corrected = broad.oof_corrected(df, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": c_value,
                "base_loss": base_loss,
                "corrected_loss": loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(df, y, base, corrected, j))
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
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.58)
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.0004 and row["mean_delta"] <= -0.00015 and row["win_rate"] >= 0.65)
            rows.append(row)
        if len(rows) % 48 == 0:
            print(f"scanned {len(rows)} corrected candidates", flush=True)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / "jepa_single_feature_results.csv", index=False)
    result.groupby("target", group_keys=False).head(15).to_csv(OUT / "jepa_single_feature_top.csv", index=False)
    result[result["passes_loose"]].to_csv(OUT / "jepa_single_feature_selected.csv", index=False)
    return df, result


def choose_ops(result: pd.DataFrame, max_targets: int = 7) -> list[SelectedOp]:
    selected = result[result["passes_strict"]].copy()
    if selected.empty:
        selected = result[result["passes_loose"]].copy()
    if selected.empty:
        selected = result[(result["best_weight"] > 0) & (result["delta_vs_base"] < -0.00025) & (result["mean_delta"] < 0)].copy()
    if selected.empty:
        return []
    selected = selected.sort_values(["passes_strict", "passes_loose", "mean_delta", "delta_vs_base"], ascending=[False, False, True, True])
    ops: list[SelectedOp] = []
    seen: set[str] = set()
    for row in selected.itertuples(index=False):
        target = str(row.target)
        if target in seen:
            continue
        ops.append(SelectedOp(target, str(row.feature), str(row.mode), float(row.c_value), float(row.best_weight)))
        seen.add(target)
        if len(ops) >= max_targets:
            break
    return ops


def apply_ops_oof(df: pd.DataFrame, base: np.ndarray, ops: list[SelectedOp]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        j = TARGETS.index(op.target)
        corrected = broad.oof_corrected(df, out, op.target, op.feature, op.mode, op.c_value)
        out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_ops_submission(train_df: pd.DataFrame, sub_df: pd.DataFrame, base_oof: np.ndarray, base_sub: pd.DataFrame, ops: list[SelectedOp]) -> pd.DataFrame:
    pred = base_sub[TARGETS].to_numpy(dtype=float)
    ref = base_oof.copy()
    for op in ops:
        j = TARGETS.index(op.target)
        corrected_sub = broad.fit_corrected(train_df, sub_df, ref, pred, op.target, op.feature, op.mode, op.c_value)
        pred[:, j] = clip((1.0 - op.weight) * pred[:, j] + op.weight * corrected_sub)
        corrected_ref = broad.fit_corrected(train_df, train_df, ref, ref, op.target, op.feature, op.mode, op.c_value)
        ref[:, j] = clip((1.0 - op.weight) * ref[:, j] + op.weight * corrected_ref)
    out = base_sub.copy()
    out[TARGETS] = clip(pred)
    return out


def write_report(meta: dict[str, object], result: pd.DataFrame, ops: list[SelectedOp], cv: pd.DataFrame) -> None:
    top = result.head(15)[
        ["target", "feature", "mode", "c_value", "best_weight", "delta_vs_base", "mean_delta", "win_rate", "passes_strict", "passes_loose"]
    ]
    def simple_table(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, row in df.iterrows():
            vals = []
            for col in cols:
                val = row[col]
                if isinstance(val, float):
                    vals.append(f"{val:.9g}")
                else:
                    vals.append(str(val))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    lines = [
        "# JEPA Experiments",
        "",
        "This folder contains JEPA-style latent prediction experiments adapted to the sleep/lifelog tabular data.",
        "",
        "## Feature Families",
        "",
        f"- Input feature count: `{meta['input_feature_count']}`",
        f"- JEPA-derived feature count: `{meta['jepa_feature_count']}`",
        f"- Image-like sensor/time grid cells: `{meta['grid_cells']}`",
        "- Families: modality block prediction, time-block prediction, sensor-time cell prediction, prefix block prediction, image-grid row/column prediction, subject temporal-neighbor prediction.",
        "",
        "## Best Single-Feature Residual Scans",
        "",
        simple_table(top),
        "",
        "## Selected Combined Candidate",
        "",
    ]
    if ops:
        lines.extend([f"- {op.target}: `{op.feature}` / `{op.mode}` / C={op.c_value} / w={op.weight}" for op in ops])
    else:
        lines.append("- No JEPA feature passed the guarded selection threshold.")
    lines += ["", "## CV Estimate", "", simple_table(cv), ""]
    (OUT / "jepa_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    base_oof, base_sub = read_base()
    y = train_raw[TARGETS].to_numpy(dtype=int)

    jepa_train, jepa_sub, meta = make_jepa_features(train_feat, sub_feat)
    jepa_train.to_parquet(OUT / "train_jepa_features.parquet", index=False)
    jepa_sub.to_parquet(OUT / "submission_jepa_features.parquet", index=False)
    (OUT / "jepa_feature_meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    scan_df, result = scan_features(train_raw, jepa_train, base_oof, top_n=12)
    ops = choose_ops(result)
    pred = apply_ops_oof(scan_df, base_oof, ops) if ops else base_oof.copy()
    cv_rows = []
    for j, target in enumerate(TARGETS):
        cv_rows.append(
            {
                "target": target,
                "base_loss": loss_col(y[:, j], base_oof[:, j]),
                "candidate_loss": loss_col(y[:, j], pred[:, j]),
                "delta_vs_base": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base_oof[:, j]),
            }
        )
    cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base_oof), "candidate_loss": mean_loss(y, pred), "delta_vs_base": mean_loss(y, pred) - mean_loss(y, base_oof)})
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / "jepa_selected_cv_estimate.csv", index=False)
    np.save(OUT / "jepa_selected_oof.npy", pred)

    train_df = train_raw[SUB_KEY + TARGETS].merge(jepa_train, on=SUB_KEY, how="left")
    sub_df = sub_raw[SUB_KEY].merge(jepa_sub, on=SUB_KEY, how="left")
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sample[SUB_KEY])
    if ops:
        submission = apply_ops_submission(train_df, sub_df, base_oof, base_sub, ops)
    else:
        submission = base_sub.copy()
    submission.to_csv(OUT / "submission_jepa_selected.csv", index=False)
    pd.DataFrame([op.__dict__ for op in ops]).to_csv(OUT / "jepa_selected_ops.csv", index=False)
    write_report(meta, result, ops, cv)
    print(cv.round(9).to_string(index=False))
    print(result.head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
