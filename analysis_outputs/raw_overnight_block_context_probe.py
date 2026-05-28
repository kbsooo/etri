#!/usr/bin/env python3
"""E54 raw overnight block-context probe.

E53 showed that simple labeled calendar flanks are useful as local energy but
not as a strict, transferable hidden block count-state predictor. This probe
asks the next JEPA question: does the observed raw overnight context of the
hidden block itself rescue strict subject-excluded block rate/count recovery?
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import calendar_flank_block_count_state_probe as e53  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY
EPS = 1e-5

NIGHT_FEATURES = OUT / "overnight_sensor_features_v2.parquet"
MIXMIN = OUT / "submission_mixmin_0c916bb4.csv"
A2C8 = OUT / "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05 = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

SUMMARY_OUT = OUT / "raw_overnight_block_context_probe_summary.csv"
TARGET_OUT = OUT / "raw_overnight_block_context_probe_target_detail.csv"
GEOMETRY_OUT = OUT / "raw_overnight_block_context_probe_geometry.csv"
HIDDEN_OUT = OUT / "raw_overnight_block_context_probe_hidden_alignment.csv"
HIDDEN_TARGET_OUT = OUT / "raw_overnight_block_context_probe_hidden_target_alignment.csv"
REPORT_OUT = OUT / "raw_overnight_block_context_probe_report.md"


@dataclass(frozen=True)
class ViewPack:
    view: str
    n_cols: int
    row_dim: int
    pseudo_raw: np.ndarray
    hidden_raw: np.ndarray
    geometry: dict[str, float | str]


@dataclass(frozen=True)
class MethodSpec:
    name: str
    view: str
    mode: str
    include_ctx: bool
    k: int
    alpha: float
    pseudo_x: np.ndarray
    hidden_x: np.ndarray


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def feature_columns(frame: pd.DataFrame, view: str) -> list[str]:
    base = [c for c in frame.columns if c not in {"subject_id", "lifelog_date"}]
    prefixes = {
        "night_all": ("night_",),
        "night_phone": ("night_phone_", "night_screen_", "night_charging_", "night_usage_"),
        "night_watch": ("night_watch_", "night_hr_"),
        "night_context": ("night_wifi_", "night_ble_", "night_gps_", "night_usage_", "night_ambience_"),
        "night_light": ("night_phone_light_", "night_watch_light_"),
        "night_mobility": ("night_wifi_", "night_ble_", "night_gps_"),
        "night_usage_ambience": ("night_usage_", "night_ambience_"),
        "night_coverage": ("night_",),
    }
    if view not in prefixes:
        raise ValueError(f"unknown view: {view}")
    if view == "night_coverage":
        tokens = ("_count", "_observations", "present_frac", "any_feature_present")
        return [c for c in base if c.startswith("night_") and any(tok in c for tok in tokens)]
    keep = prefixes[view]
    return [c for c in base if c.startswith(keep)]


def load_overnight_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if not NIGHT_FEATURES.exists():
        import overnight_feature_experiments as ov  # noqa: E402

        ov.build_overnight_features()
    night = pd.read_parquet(NIGHT_FEATURES)
    night["subject_id"] = night["subject_id"].astype(str)
    night["lifelog_date"] = pd.to_datetime(night["lifelog_date"])
    merged = rows[["subject_id", "lifelog_date"]].copy()
    merged["subject_id"] = merged["subject_id"].astype(str)
    merged["lifelog_date"] = pd.to_datetime(merged["lifelog_date"])
    merged = merged.merge(night, on=["subject_id", "lifelog_date"], how="left")
    numeric = [c for c in merged.columns if c not in {"subject_id", "lifelog_date"}]
    merged["night_any_feature_present"] = merged[numeric].notna().any(axis=1).astype(float)
    merged["night_feature_present_frac"] = merged[numeric].notna().mean(axis=1).astype(float)
    return merged


def pca_row_embedding(frame: pd.DataFrame, cols: list[str], n_components: int) -> tuple[np.ndarray, int, int]:
    usable = []
    for col in cols:
        s = pd.to_numeric(frame[col], errors="coerce")
        if s.notna().sum() >= 20 and s.nunique(dropna=True) > 1:
            usable.append(col)
    if not usable:
        return np.zeros((len(frame), 1), dtype=np.float64), 0, 1
    vals = frame[usable].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    nan_frac = vals.isna().mean(axis=1).to_numpy(dtype=np.float64).reshape(-1, 1)
    med = vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float64)
    x = StandardScaler().fit_transform(x)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    k = min(n_components, x.shape[0] - 1, x.shape[1])
    if k <= 0:
        z = np.zeros((len(frame), 1), dtype=np.float64)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            z = PCA(n_components=k, svd_solver="randomized", random_state=260529).fit_transform(x)
    z = np.concatenate([z, nan_frac], axis=1)
    return z.astype(np.float64), len(usable), z.shape[1]


def block_raw_vector(rows: pd.DataFrame, row_z: np.ndarray, positions: np.ndarray) -> np.ndarray:
    xb = row_z[positions]
    if len(positions) > 1:
        slope = (xb[-1] - xb[0]) / float(len(positions) - 1)
    else:
        slope = np.zeros(row_z.shape[1], dtype=np.float64)
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
    out = np.concatenate([np.array([len(positions)], dtype=np.float64), geom] + stats)
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


def block_geometry(view: str, n_cols: int, row_dim: int, pseudo_x: np.ndarray, hidden_x: np.ndarray) -> dict[str, float | str]:
    z = StandardScaler().fit_transform(pseudo_x)
    z = np.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)
    cov = (z.T @ z) / max(len(z) - 1, 1)
    eig = np.clip(np.linalg.eigvalsh(cov), 0.0, None)
    eig_sum = float(eig.sum())
    if eig_sum <= 1e-12:
        anisotropy = np.nan
        effective_rank = np.nan
    else:
        probs = eig / eig_sum
        anisotropy = float(eig.max() / eig_sum)
        effective_rank = float(np.exp(-(probs[probs > 0] * np.log(probs[probs > 0])).sum()))
    scaler = StandardScaler().fit(pseudo_x)
    hp = scaler.transform(hidden_x)
    pp = scaler.transform(pseudo_x)
    dist = np.sqrt(np.maximum(((hp[:, None, :] - pp[None, :, :]) ** 2).mean(axis=2), 0.0))
    return {
        "view": view,
        "n_cols": float(n_cols),
        "row_dim": float(row_dim),
        "block_dim": float(pseudo_x.shape[1]),
        "anisotropy": float(anisotropy),
        "effective_rank": float(effective_rank),
        "hidden_nn_dist_median": float(np.median(dist.min(axis=1))),
        "hidden_nn_dist_p90": float(np.quantile(dist.min(axis=1), 0.9)),
    }


def make_view_pack(
    view: str,
    rows: pd.DataFrame,
    frame: pd.DataFrame,
    pseudo_blocks: list[hbr.Block],
    hidden_blocks: list[hbr.Block],
) -> ViewPack:
    cols = feature_columns(frame, view)
    row_z, n_cols, row_dim = pca_row_embedding(frame, cols, n_components=16 if view != "night_coverage" else 8)
    pseudo_x = np.vstack([block_raw_vector(rows, row_z, b.positions) for b in pseudo_blocks])
    hidden_x = np.vstack([block_raw_vector(rows, row_z, b.positions) for b in hidden_blocks])
    return ViewPack(
        view=view,
        n_cols=n_cols,
        row_dim=row_dim,
        pseudo_raw=pseudo_x,
        hidden_raw=hidden_x,
        geometry=block_geometry(view, n_cols, row_dim, pseudo_x, hidden_x),
    )


def donor_mask(blocks: list[hbr.Block], i: int, mode: str) -> np.ndarray:
    target = blocks[i]
    target_positions = set(int(p) for p in target.positions)
    keep = []
    for k, block in enumerate(blocks):
        if k == i:
            keep.append(False)
        elif mode == "strict_subject" and block.subject_id == target.subject_id:
            keep.append(False)
        elif target_positions.intersection(int(p) for p in block.positions):
            keep.append(False)
        else:
            keep.append(True)
    return np.asarray(keep, dtype=bool)


def knn_rate_predict(
    X: np.ndarray,
    rates: np.ndarray,
    xi: np.ndarray,
    fallback: np.ndarray,
    donors: np.ndarray,
    k: int,
    alpha: float,
) -> tuple[np.ndarray, dict[str, float]]:
    idx = np.where(donors)[0]
    if len(idx) == 0:
        return clip(fallback), {"support": 0.0, "dist_median": np.nan, "dist_min": np.nan}
    scaler = StandardScaler()
    xd = scaler.fit_transform(X[idx])
    xv = scaler.transform(xi.reshape(1, -1))[0]
    dist = np.sqrt(np.maximum(((xd - xv) ** 2).mean(axis=1), 0.0))
    order = np.argsort(dist)[: min(k, len(idx))]
    chosen = idx[order]
    d = dist[order]
    weights = 1.0 / np.maximum(d, 1e-3)
    weights = weights / weights.sum()
    local = weights @ rates[chosen]
    eff = float(len(chosen))
    pred = (eff * local + alpha * fallback) / (eff + alpha)
    return clip(pred), {
        "support": float(len(chosen)),
        "dist_median": float(np.median(d)),
        "dist_min": float(np.min(d)),
    }


def make_method_predictions(
    spec: MethodSpec,
    blocks: list[hbr.Block],
    features: list[e53.ProbeFeatures],
    rates: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    pred = np.zeros((len(blocks), len(TARGETS)), dtype=np.float64)
    meta = []
    for i in range(len(blocks)):
        donors = donor_mask(blocks, i, spec.mode)
        fallback = np.asarray(features[i].subject_mean, dtype=np.float64)
        p, m = knn_rate_predict(spec.pseudo_x, rates, spec.pseudo_x[i], fallback, donors, spec.k, spec.alpha)
        pred[i] = p
        meta.append({"method": spec.name, "block_idx": i, **m})
    return pred, pd.DataFrame(meta)


def hidden_method_prediction(
    spec: MethodSpec,
    pseudo_blocks: list[hbr.Block],
    pseudo_features: list[e53.ProbeFeatures],
    rates: np.ndarray,
    hidden_blocks: list[hbr.Block],
    hidden_features: list[e53.ProbeFeatures],
) -> tuple[np.ndarray, pd.DataFrame]:
    pred = np.zeros((len(hidden_blocks), len(TARGETS)), dtype=np.float64)
    meta = []
    for h, block in enumerate(hidden_blocks):
        donors = np.ones(len(pseudo_blocks), dtype=bool)
        if spec.mode == "strict_subject":
            donors &= np.asarray([b.subject_id != block.subject_id for b in pseudo_blocks], dtype=bool)
        fallback = np.asarray(hidden_features[h].subject_mean, dtype=np.float64)
        p, m = knn_rate_predict(spec.pseudo_x, rates, spec.hidden_x[h], fallback, donors, spec.k, spec.alpha)
        pred[h] = p
        meta.append({"method": spec.name, "hidden_idx": h, **m})
    return pred, pd.DataFrame(meta)


def hidden_alignment(
    method: str,
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    hidden_blocks: list[hbr.Block],
    hidden_rate: np.ndarray,
    meta: pd.DataFrame,
) -> tuple[list[dict[str, float | str]], list[dict[str, float | str]]]:
    mixmin = e53.read_submission(MIXMIN)
    a2c8 = e53.read_submission(A2C8)
    raw05 = e53.read_submission(RAW05)
    d_mix = e53.expected_block_delta(sample, rows, hidden_blocks, hidden_rate, mixmin, a2c8)
    d_raw = e53.expected_block_delta(sample, rows, hidden_blocks, hidden_rate, raw05, a2c8)
    block_rows = []
    for i, block in enumerate(hidden_blocks):
        rec = {
            "method": method,
            "hidden_block_id": block.block_id,
            "subject_id": block.subject_id,
            "n_rows": block.n,
            "start": block.start.date().isoformat(),
            "end": block.end.date().isoformat(),
            "expected_mixmin_delta_vs_a2c8": float(d_mix[i].mean()),
            "expected_raw05_delta_vs_a2c8": float(d_raw[i].mean()),
            "support": float(meta.iloc[i]["support"]) if len(meta) else np.nan,
            "dist_median": float(meta.iloc[i]["dist_median"]) if len(meta) else np.nan,
        }
        for j, target in enumerate(TARGETS):
            rec[f"rate_{target}"] = float(hidden_rate[i, j])
            rec[f"mixmin_delta_vs_a2c8_{target}"] = float(d_mix[i, j])
        block_rows.append(rec)
    target_rows = []
    weights = np.asarray([b.n for b in hidden_blocks], dtype=np.float64)
    for j, target in enumerate(TARGETS):
        target_rows.append(
            {
                "method": method,
                "target": target,
                "weighted_mixmin_delta_vs_a2c8": float(np.average(d_mix[:, j], weights=weights)),
                "mean_mixmin_delta_vs_a2c8": float(d_mix[:, j].mean()),
                "mixmin_better_block_rate": float((d_mix[:, j] < 0).mean()),
                "mean_predicted_rate": float(hidden_rate[:, j].mean()),
            }
        )
    return block_rows, target_rows


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    y = hbr.train_label_matrix(rows, train)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    known = hbr.base_known_mask(rows)
    rates = hbr.true_rates(y, pseudo_blocks)
    counts = np.vstack([np.nansum(y[b.positions], axis=0) for b in pseudo_blocks]).astype(np.float64)

    pseudo_features = []
    for block in pseudo_blocks:
        mask = known.copy()
        mask[block.positions] = False
        pseudo_features.append(e53.make_probe_features(rows, y, block.positions, mask))
    hidden_features = [e53.make_probe_features(rows, y, block.positions, known) for block in hidden_blocks]
    pseudo_ctx = np.vstack([f.ctx for f in pseudo_features])
    hidden_ctx = np.vstack([f.ctx for f in hidden_features])

    overnight = load_overnight_rows(rows)
    views = [
        "night_all",
        "night_phone",
        "night_watch",
        "night_context",
        "night_light",
        "night_mobility",
        "night_usage_ambience",
        "night_coverage",
    ]
    packs = [make_view_pack(view, rows, overnight, pseudo_blocks, hidden_blocks) for view in views]
    geometry = pd.DataFrame([pack.geometry for pack in packs])

    pred_subject = np.vstack([f.subject_mean for f in pseudo_features])
    pred_calendar_strict, _ = e53.make_predictions(pseudo_blocks, pseudo_features, rates, "strict_subject")
    pred_calendar_local, _ = e53.make_predictions(pseudo_blocks, pseudo_features, rates, "local_nonoverlap")
    methods: dict[str, np.ndarray] = {
        "subject_mean": pred_subject,
        "calendar_count_strict": pred_calendar_strict,
        "calendar_count_local": pred_calendar_local,
    }
    specs: list[MethodSpec] = []
    for pack in packs:
        for include_ctx in [False, True]:
            for k in [8, 16]:
                name = f"{pack.view}_{'rawctx' if include_ctx else 'raw'}_strict_k{k}_a24"
                px = np.concatenate([pack.pseudo_raw, pseudo_ctx], axis=1) if include_ctx else pack.pseudo_raw
                hx = np.concatenate([pack.hidden_raw, hidden_ctx], axis=1) if include_ctx else pack.hidden_raw
                specs.append(MethodSpec(name, pack.view, "strict_subject", include_ctx, k, 24.0, px, hx))
        name = f"{pack.view}_rawctx_local_k8_a24"
        specs.append(
            MethodSpec(
                name,
                pack.view,
                "local_nonoverlap",
                True,
                8,
                24.0,
                np.concatenate([pack.pseudo_raw, pseudo_ctx], axis=1),
                np.concatenate([pack.hidden_raw, hidden_ctx], axis=1),
            )
        )

    meta_frames = []
    for spec in specs:
        pred, meta = make_method_predictions(spec, pseudo_blocks, pseudo_features, rates)
        methods[spec.name] = pred
        meta_frames.append(meta)
    meta_all = pd.concat(meta_frames, ignore_index=True)

    summary_rows = []
    target_rows = []
    for name, pred in methods.items():
        row, detail = e53.summarize_method(name, pred, y, pseudo_blocks, counts, rates)
        summary_rows.append(row)
        target_rows.extend(detail)
    summary = pd.DataFrame(summary_rows)
    subj_loss = float(summary.loc[summary["method"].eq("subject_mean"), "weighted_row_logloss"].iloc[0])
    subj_count = float(summary.loc[summary["method"].eq("subject_mean"), "weighted_count_nll_per_row"].iloc[0])
    summary["delta_weighted_row_logloss_vs_subject"] = summary["weighted_row_logloss"] - subj_loss
    summary["delta_weighted_count_nll_per_row_vs_subject"] = summary["weighted_count_nll_per_row"] - subj_count
    support = meta_all.groupby("method").agg(support_mean=("support", "mean"), dist_median=("dist_median", "median"))
    summary = summary.merge(support, left_on="method", right_index=True, how="left")
    summary["view"] = summary["method"].str.extract(r"^(night_[a-z_]+?)_(?:raw|rawctx)_")[0].fillna("")
    summary["strict_method"] = summary["method"].str.contains("_strict_").astype(float)
    summary = summary.sort_values(["weighted_row_logloss", "weighted_count_nll_per_row"]).reset_index(drop=True)

    target_detail = pd.DataFrame(target_rows)
    base = target_detail[target_detail["method"].eq("subject_mean")].set_index("target")
    target_detail["delta_row_vs_subject"] = target_detail.apply(
        lambda r: r["target_row_logloss"] - float(base.loc[r["target"], "target_row_logloss"]),
        axis=1,
    )
    target_detail["delta_count_vs_subject"] = target_detail.apply(
        lambda r: r["target_count_nll_per_row"] - float(base.loc[r["target"], "target_count_nll_per_row"]),
        axis=1,
    )
    target_detail = target_detail.sort_values(["target", "target_row_logloss"]).reset_index(drop=True)

    hidden_block_rows = []
    hidden_target_rows = []
    hidden_methods = ["subject_mean", "calendar_count_strict", "calendar_count_local"]
    hidden_methods.extend([m for m in summary["method"].tolist() if m not in hidden_methods][:12])
    hidden_methods = list(dict.fromkeys(hidden_methods))
    hidden_subject = np.vstack([f.subject_mean for f in hidden_features])
    hidden_calendar_strict, hidden_cal_strict_meta = e53.predict_hidden(
        pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, "strict_subject"
    )
    hidden_calendar_local, hidden_cal_local_meta = e53.predict_hidden(
        pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, "local_nonoverlap"
    )
    spec_map = {spec.name: spec for spec in specs}
    for method in hidden_methods:
        if method == "subject_mean":
            hr = hidden_subject
            hm = pd.DataFrame({"support": np.nan, "dist_median": np.nan}, index=range(len(hidden_blocks)))
        elif method == "calendar_count_strict":
            hr = hidden_calendar_strict
            hm = hidden_cal_strict_meta.rename(columns={"support_min": "support"})
            hm["dist_median"] = np.nan
        elif method == "calendar_count_local":
            hr = hidden_calendar_local
            hm = hidden_cal_local_meta.rename(columns={"support_min": "support"})
            hm["dist_median"] = np.nan
        else:
            hr, hm = hidden_method_prediction(
                spec_map[method], pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features
            )
        br, tr = hidden_alignment(method, sample, rows, hidden_blocks, hr, hm)
        hidden_block_rows.extend(br)
        hidden_target_rows.extend(tr)
    hidden = pd.DataFrame(hidden_block_rows)
    hidden_target = pd.DataFrame(hidden_target_rows)
    hidden_by_method = (
        hidden.groupby("method")
        .apply(
            lambda g: pd.Series(
                {
                    "hidden_blocks": len(g),
                    "weighted_mixmin_delta_vs_a2c8": float(np.average(g["expected_mixmin_delta_vs_a2c8"], weights=g["n_rows"])),
                    "mean_mixmin_delta_vs_a2c8": float(g["expected_mixmin_delta_vs_a2c8"].mean()),
                    "mean_raw05_delta_vs_a2c8": float(g["expected_raw05_delta_vs_a2c8"].mean()),
                    "mixmin_better_block_rate": float((g["expected_mixmin_delta_vs_a2c8"] < 0).mean()),
                    "median_support": float(g["support"].median()) if g["support"].notna().any() else np.nan,
                    "median_dist": float(g["dist_median"].median()) if g["dist_median"].notna().any() else np.nan,
                }
            )
        )
        .reset_index()
        .sort_values(["weighted_mixmin_delta_vs_a2c8", "mean_mixmin_delta_vs_a2c8"])
    )

    summary.to_csv(SUMMARY_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    geometry.to_csv(GEOMETRY_OUT, index=False)
    hidden_by_method.to_csv(HIDDEN_OUT, index=False)
    hidden_target.to_csv(HIDDEN_TARGET_OUT, index=False)

    best_strict = summary[summary["method"].str.contains("_strict_")].iloc[0]
    strict_delta = float(best_strict["delta_weighted_row_logloss_vs_subject"])
    best_hidden = hidden_by_method.iloc[0]
    lines = [
        "# E54 Raw Overnight Block Context Probe",
        "",
        "## Observe",
        "",
        "E53 kept calendar-flank state as energy only: local donors improved pseudo-hidden blocks, but strict subject-excluded donors failed. The next question is whether the observed raw overnight block context is the missing representation.",
        "",
        "## Wonder",
        "",
        "Can raw overnight context plus flanks predict hidden block target rates under strict subject exclusion, or does raw context collapse into subject/domain shortcut?",
        "",
        "## Hypothesis",
        "",
        "H54: if raw overnight context encodes the hidden sleep-state generator, raw/ctx block embeddings should beat subject mean and calendar-count strict on pseudo-hidden blocks without using same-subject donors, especially on S targets, and their real hidden rates should explain mixmin with broader target alignment.",
        "",
        "## Method",
        "",
        f"- Pseudo-hidden blocks: `{len(pseudo_blocks)}`; actual hidden blocks: `{len(hidden_blocks)}`.",
        "- Context: `overnight_sensor_features_v2.parquet` feature families compressed to row PCA, aggregated to block mean/std/min/max/first/last/slope, optionally concatenated with labeled flank context.",
        "- Prediction: kNN donor rate posterior with shrinkage to subject mean; strict mode excludes the target subject, local mode is retained only as shortcut diagnostic.",
        "- Stress: pseudo-hidden weighted row LogLoss/count NLL, targetwise recovery, latent geometry, and expected hidden-block CE delta for mixmin/raw05 versus a2c8.",
        "",
        "## Pseudo-Hidden Summary",
        "",
        markdown_table(
            summary,
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_subject",
                "weighted_count_nll_per_row",
                "rate_mae_weighted",
                "support_mean",
                "dist_median",
            ],
            max_rows=18,
        ),
        "",
        "## View Geometry",
        "",
        markdown_table(
            geometry.sort_values(["hidden_nn_dist_median", "anisotropy"]),
            ["view", "n_cols", "row_dim", "block_dim", "anisotropy", "effective_rank", "hidden_nn_dist_median", "hidden_nn_dist_p90"],
            max_rows=12,
        ),
        "",
        "## Best Strict Target Detail",
        "",
    ]
    best_targets = target_detail[target_detail["method"].eq(str(best_strict["method"]))].copy()
    lines.append(
        markdown_table(
            best_targets,
            ["target", "target_row_logloss", "delta_row_vs_subject", "target_count_nll_per_row", "delta_count_vs_subject"],
            max_rows=10,
        )
    )
    lines.extend(
        [
            "",
            "## Hidden-Block Mixmin Alignment",
            "",
            markdown_table(
                hidden_by_method,
                [
                    "method",
                    "weighted_mixmin_delta_vs_a2c8",
                    "mean_mixmin_delta_vs_a2c8",
                    "mean_raw05_delta_vs_a2c8",
                    "mixmin_better_block_rate",
                    "median_support",
                    "median_dist",
                ],
                max_rows=14,
            ),
            "",
            "## Decision",
            "",
        ]
    )
    best_strict_hidden = hidden_by_method[hidden_by_method["method"].eq(str(best_strict["method"]))].iloc[0]
    best_target_bad = best_targets[best_targets["delta_row_vs_subject"] > 0]["target"].tolist()
    best_strict_hidden_delta = float(best_strict_hidden["weighted_mixmin_delta_vs_a2c8"])
    if strict_delta < -0.002 and best_strict_hidden_delta < -0.0002 and not best_target_bad:
        lines.extend(
            [
                f"The best strict raw overnight method `{best_strict['method']}` improves pseudo-hidden row LogLoss by `{strict_delta:+.6f}`. This keeps H54 alive, but it is not a submission by itself; it must survive targetwise S/Q checks and mixmin-relative sign stress.",
                "",
                f"It also gives weighted mixmin delta `{best_strict_hidden_delta:+.6f}` on actual hidden blocks with no targetwise pseudo-hidden regression.",
            ]
        )
    elif strict_delta < -0.002:
        lines.extend(
            [
                f"The best strict raw overnight method `{best_strict['method']}` improves pseudo-hidden row LogLoss by `{strict_delta:+.6f}`, so raw overnight context does recover a real held-out block-state signal.",
                "",
                f"But it fails the public/mixmin translation gate: its actual hidden-block weighted mixmin delta is `{best_strict_hidden_delta:+.6f}`, while the strongest hidden alignment remains `{best_hidden['method']}` at `{float(best_hidden['weighted_mixmin_delta_vs_a2c8']):+.6f}`. Pseudo-hidden target regressions for the best strict method: `{','.join(best_target_bad) if best_target_bad else 'none'}`.",
                "",
                "This splits the world model: raw overnight context is a real strict representation, but it is not the same latent that produced mixmin's public edge. Treat it as a validation-mismatch/private-risk diagnostic, not as a submission source.",
            ]
        )
    else:
        lines.extend(
            [
                f"The best strict raw overnight method `{best_strict['method']}` does not beat subject mean enough: delta `{strict_delta:+.6f}`. Raw overnight context, as compressed here, does not rescue the simple flank-count failure.",
                "",
                f"The strongest hidden alignment is `{best_hidden['method']}` with weighted mixmin delta `{float(best_hidden['weighted_mixmin_delta_vs_a2c8']):+.6f}`, which should be treated as energy only unless pseudo-hidden strict recovery also improves.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TARGET_OUT.relative_to(ROOT)}`",
            f"- `{GEOMETRY_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_TARGET_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        "pseudo_blocks=",
        len(pseudo_blocks),
        "hidden_blocks=",
        len(hidden_blocks),
        "best_strict=",
        best_strict["method"],
        f"{strict_delta:+.6f}",
        "best_hidden=",
        best_hidden["method"],
        f"{float(best_hidden['weighted_mixmin_delta_vs_a2c8']):+.6f}",
    )
    print(summary.head(15).round(6).to_string(index=False))
    print(hidden_by_method.head(12).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
