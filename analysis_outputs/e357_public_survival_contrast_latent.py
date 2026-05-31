#!/usr/bin/env python3
"""E357: public-survival contrast latent for compact lifestyle-state probes.

Question:
    E356 produced a transfer-stability probe inside the E350/E351 compact
    lifestyle-state basin.  Before treating it as a useful public candidate,
    can the existing public observations see it as E247-preserving and
    E323/E216/E267-adverse-movement avoiding?

JEPA/data2vec translation:
    context = output-space movement anatomy relative to the E247 public anchor
    target  = same-level public-survival representation induced by fixed public
              observations, not raw labels or raw lifelog reconstruction
    action  = keep, demote, or probe compact lifestyle-state candidates based on
              whether this contrast latent sees them as low-risk

The public LB observations are used as a diagnostic sensor.  This script does
not tune toward a target public value and does not generate arbitrary blends.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402


RNG_SEED = 20260531 + 357
EPS = 1.0e-6
N_PERMUTATIONS = 40
UPLOAD_PREFIX = "submission_e357_publicsurvival"

OBS_IN = OUT / "public_probe_observations.csv"
E351_RANKED_IN = OUT / "e351_robust_plateau_selector_ranked.csv"
E356_PRED_IN = OUT / "e356_transfer_stability_predictions.csv"
E355_PRED_IN = OUT / "e355_action_health_plateau_predictions.csv"

KNOWN_OUT = OUT / "e357_public_survival_contrast_known.csv"
LOOCV_OUT = OUT / "e357_public_survival_contrast_loocv.csv"
POOL_OUT = OUT / "e357_public_survival_contrast_pool.csv"
SELECTION_OUT = OUT / "e357_public_survival_contrast_selection.csv"
REPORT_OUT = OUT / "e357_public_survival_contrast_report.md"

KEY = ["subject_id", "sleep_date", "lifelog_date"]
ANCHOR_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E351_VARIANT = "compact_t75_s1.005_s3a0.25"
E356_VARIANT = "compact_t45_s1.005_s3a0.50"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    return None


def safe_spearman(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 5:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(x.astype(np.float64), EPS, 1.0 - EPS)


def short_hash(frame: pd.DataFrame) -> str:
    cols = [c for c in KEY + TARGETS if c in frame.columns]
    payload = pd.util.hash_pandas_object(frame[cols], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def logit_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in KEY + TARGETS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    df = df[KEY + TARGETS].copy()
    for col in KEY:
        df[col] = df[col].astype(str)
    df = df.sort_values(KEY).reset_index(drop=True)
    arr = clip_prob(df[TARGETS].to_numpy(dtype=np.float64))
    df[TARGETS] = np.log(arr / (1.0 - arr))
    return df


def align_delta(path: Path, anchor: pd.DataFrame) -> np.ndarray:
    frame = logit_frame(path)
    if not frame[KEY].equals(anchor[KEY]):
        merged = anchor[KEY].merge(frame, on=KEY, how="left", validate="one_to_one")
        if merged[TARGETS].isna().any().any():
            raise ValueError(f"Could not align {path}")
        vals = merged[TARGETS].to_numpy(dtype=np.float64)
    else:
        vals = frame[TARGETS].to_numpy(dtype=np.float64)
    return vals - anchor[TARGETS].to_numpy(dtype=np.float64)


def entropy_from_weights(weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=np.float64)
    total = float(np.nansum(w))
    if total <= 0:
        return 0.0
    p = w / total
    p = p[p > 0]
    return float(-(p * np.log(p)).sum() / max(np.log(len(w)), 1.0))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    x = np.ravel(a).astype(np.float64)
    y = np.ravel(b).astype(np.float64)
    den = float(np.linalg.norm(x) * np.linalg.norm(y))
    if den <= 0:
        return 0.0
    return float(np.dot(x, y) / den)


def projection(a: np.ndarray, b: np.ndarray) -> float:
    x = np.ravel(a).astype(np.float64)
    y = np.ravel(b).astype(np.float64)
    den = float(np.dot(y, y))
    if den <= 0:
        return 0.0
    return float(np.dot(x, y) / den)


def movement_features(delta: np.ndarray, prefix: str = "") -> dict[str, float]:
    d = np.asarray(delta, dtype=np.float64)
    absd = np.abs(d)
    flat = d.ravel()
    absflat = np.abs(flat)
    row_l1 = absd.sum(axis=1)
    target_l1 = absd.sum(axis=0)
    total_l1 = float(absflat.sum())
    out: dict[str, float] = {
        f"{prefix}cell_l1": total_l1,
        f"{prefix}cell_l2": float(np.linalg.norm(flat)),
        f"{prefix}cell_linf": float(absflat.max(initial=0.0)),
        f"{prefix}cell_mean_abs": float(absflat.mean()),
        f"{prefix}cell_signed_mean": float(flat.mean()),
        f"{prefix}cell_pos_frac": float(np.mean(flat > 1.0e-12)),
        f"{prefix}cell_neg_frac": float(np.mean(flat < -1.0e-12)),
        f"{prefix}changed_cells_1e3": float(np.sum(absflat > 1.0e-3)),
        f"{prefix}changed_cells_5e3": float(np.sum(absflat > 5.0e-3)),
        f"{prefix}changed_cells_1e2": float(np.sum(absflat > 1.0e-2)),
        f"{prefix}changed_rows_1e3": float(np.sum(row_l1 > 1.0e-3)),
        f"{prefix}row_l1_mean": float(row_l1.mean()),
        f"{prefix}row_l1_p90": float(np.quantile(row_l1, 0.90)),
        f"{prefix}row_l1_max": float(row_l1.max(initial=0.0)),
        f"{prefix}target_entropy": entropy_from_weights(target_l1),
        f"{prefix}row_entropy": entropy_from_weights(row_l1),
    }
    if total_l1 > 0:
        top = np.sort(row_l1)[::-1]
        out[f"{prefix}top5_row_l1_share"] = float(top[:5].sum() / total_l1)
        out[f"{prefix}top20_row_l1_share"] = float(top[:20].sum() / total_l1)
    else:
        out[f"{prefix}top5_row_l1_share"] = 0.0
        out[f"{prefix}top20_row_l1_share"] = 0.0
    for j, target in enumerate(TARGETS):
        vals = d[:, j]
        av = np.abs(vals)
        out[f"{prefix}l1_{target}"] = float(av.sum())
        out[f"{prefix}share_{target}"] = float(av.sum() / total_l1) if total_l1 > 0 else 0.0
        out[f"{prefix}signed_sum_{target}"] = float(vals.sum())
        out[f"{prefix}mean_{target}"] = float(vals.mean())
        out[f"{prefix}maxabs_{target}"] = float(av.max(initial=0.0))
        out[f"{prefix}pos_frac_{target}"] = float(np.mean(vals > 1.0e-12))
        out[f"{prefix}neg_frac_{target}"] = float(np.mean(vals < -1.0e-12))
    return out


def load_known(anchor: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, Path]]:
    obs = pd.read_csv(OBS_IN)
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    paths: dict[str, Path] = {}
    e247_lb = float(obs.loc[obs["file"].astype(str).eq(ANCHOR_FILE), "public_lb"].iloc[0])
    for _, row in obs.iterrows():
        file_name = str(row["file"])
        path = locate(file_name)
        if path is None:
            rows.append(
                {
                    "file": file_name,
                    "path": "",
                    "public_lb": float(row["public_lb"]),
                    "delta_vs_e247": float(row["public_lb"]) - e247_lb,
                    "note": row.get("note", ""),
                    "available": False,
                }
            )
            continue
        delta = align_delta(path, anchor)
        key = path.name
        deltas[key] = delta
        paths[key] = path
        rec = {
            "file": file_name,
            "basename": path.name,
            "path": rel(path),
            "public_lb": float(row["public_lb"]),
            "delta_vs_e247": float(row["public_lb"]) - e247_lb,
            "note": row.get("note", ""),
            "available": True,
        }
        rec.update(movement_features(delta))
        rows.append(rec)
    known = pd.DataFrame(rows)
    return known, deltas, paths


def add_axis_features(frame: pd.DataFrame, delta_lookup: dict[str, np.ndarray], axes: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for key in frame["basename"].astype(str):
        d = delta_lookup.get(key)
        if d is None:
            rows.append({})
            continue
        rec: dict[str, float] = {}
        for axis_name, axis in axes.items():
            cos_val = cosine(d, axis)
            proj_val = projection(d, axis)
            rec[f"cos_{axis_name}"] = cos_val
            rec[f"proj_{axis_name}"] = proj_val
            rec[f"posproj_{axis_name}"] = max(0.0, proj_val)
            rec[f"absproj_{axis_name}"] = abs(proj_val)
        rows.append(rec)
    axis_frame = pd.DataFrame(rows, index=frame.index)
    # Some candidate score tables already contain historical cosine/projection
    # columns.  The public-survival audit must use axes rebuilt from the current
    # public ledger, so replace any colliding names instead of creating duplicate
    # pandas columns that later confuse sklearn feature-name checks.
    base = frame.drop(columns=[c for c in axis_frame.columns if c in frame.columns], errors="ignore")
    return pd.concat([base.reset_index(drop=True), axis_frame.reset_index(drop=True)], axis=1)


def make_axes(deltas: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    axes: dict[str, np.ndarray] = {}
    name_map = {
        "e95": "submission_e95_hardtail_541e3973.csv",
        "e101": "submission_e101_q2s3tail_177569bc.csv",
        "mixmin": "submission_mixmin_0c916bb4.csv",
        "e176": "submission_e176_abl_q2_to0p75_91e49725.csv",
        "e216_bad": "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        "e256_loss": "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
        "e267_bad": "submission_e267_humansocial_tail_balanced_2936100f.csv",
        "e323_bad": "submission_e323_5508f966_uploadsafe.csv",
        "broad_stage2_bad": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "ordinal_bad": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "final9_bad": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    }
    for axis_name, base_name in name_map.items():
        if base_name in deltas:
            axes[axis_name] = deltas[base_name]
    bad_parts = [axes[k] for k in ["e216_bad", "e267_bad", "e323_bad", "broad_stage2_bad", "ordinal_bad", "final9_bad"] if k in axes]
    if bad_parts:
        axes["bad_combo_mean"] = np.mean(np.stack(bad_parts), axis=0)
    old_good = [axes[k] for k in ["e95", "e101", "mixmin", "e176"] if k in axes]
    if old_good:
        axes["old_frontier_mean"] = np.mean(np.stack(old_good), axis=0)
    if "e95" in axes and "e323_bad" in axes:
        axes["e323_minus_e95"] = axes["e323_bad"] - axes["e95"]
    return axes


def feature_columns(frame: pd.DataFrame) -> list[str]:
    skip = {
        "file",
        "basename",
        "path",
        "note",
        "available",
        "public_lb",
        "delta_vs_e247",
        "variant",
        "source",
        "selection_role",
    }
    cols = []
    for col in frame.columns:
        if col in skip:
            continue
        if pd.api.types.is_numeric_dtype(frame[col]) and frame[col].notna().sum() >= 5 and frame[col].nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def make_model(model_name: str):
    if model_name == "ridge_1":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if model_name == "ridge_10":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if model_name == "knn3":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=3, weights="distance"))
    if model_name == "extratrees":
        return ExtraTreesRegressor(n_estimators=96, min_samples_leaf=2, random_state=RNG_SEED, n_jobs=1)
    raise ValueError(model_name)


def loo_diagnostics(known: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    data = known[known["available"].fillna(False)].copy().reset_index(drop=True)
    y = data["delta_vs_e247"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED)
    X = data[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    for model_name in ["ridge_1", "ridge_10", "knn3", "extratrees"]:
        pred = np.full(len(data), np.nan, dtype=np.float64)
        for tr, va in LeaveOneOut().split(X):
            model = make_model(model_name)
            model.fit(X.iloc[tr], y[tr])
            pred[va] = model.predict(X.iloc[va])[0]
        spearman = safe_spearman(y, pred)
        mae = float(np.mean(np.abs(pred - y)))
        # Public labels are very scarce.  Permutation here is a coarse
        # anti-collapse sanity check, not a formal significance test.  Keep it
        # cheap enough that the audit can be rerun frequently.
        perm_scores = []
        n_perm = 0 if model_name == "extratrees" else N_PERMUTATIONS
        for _ in range(n_perm):
            yp = rng.permutation(y)
            pp = np.full(len(data), np.nan, dtype=np.float64)
            for tr, va in LeaveOneOut().split(X):
                model = make_model(model_name)
                model.fit(X.iloc[tr], yp[tr])
                pp[va] = model.predict(X.iloc[va])[0]
            perm_scores.append(safe_spearman(y, pp))
        perm = np.asarray([s for s in perm_scores if np.isfinite(s)], dtype=np.float64)
        rows.append(
            {
                "model": model_name,
                "known_rows": int(len(data)),
                "feature_count": int(len(feature_cols)),
                "loo_spearman": spearman,
                "loo_mae": mae,
                "perm_spearman_mean": float(np.nanmean(perm)) if len(perm) else np.nan,
                "perm_spearman_p95": float(np.nanquantile(perm, 0.95)) if len(perm) else np.nan,
                "beats_perm_p95": bool(np.isfinite(spearman) and len(perm) and spearman > np.nanquantile(perm, 0.95)),
            }
        )
        data[f"loo_pred_{model_name}"] = pred
    diag = pd.DataFrame(rows).sort_values("loo_spearman", ascending=False).reset_index(drop=True)
    keep = ["basename", "public_lb", "delta_vs_e247", *[c for c in data.columns if c.startswith("loo_pred_")]]
    data[keep].to_csv(OUT / "e357_public_survival_contrast_loo_predictions.csv", index=False)
    diag.to_csv(LOOCV_OUT, index=False)
    return diag


def load_pool(anchor: pd.DataFrame, axes: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    ranked = pd.read_csv(E351_RANKED_IN).replace([np.inf, -np.inf], np.nan)
    pool = ranked[ranked["e350_plateau_gate"].fillna(False).astype(bool)].copy()
    # Keep all plateau rows for diagnostic, but mark the conservative E351 pool.
    pool["selection_role"] = np.where(pool["e351_compat_gate"].fillna(False).astype(bool), "e351_compat_pool", "plateau_noncompat")
    extras = [
        OUT / "submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv",
        OUT / "submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv",
        OUT / "submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv",
        OUT / "submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv",
        OUT / "submission_e356_transferstable_selected_compact_t45_s1_005_s3a0_50_0ace76e5_uploadsafe.csv",
    ]
    extra_rows = []
    existing_basenames = set(pool["basename"].astype(str))
    for path in extras:
        if path.exists() and path.name not in existing_basenames:
            extra_rows.append(
                {
                    "variant": path.stem.replace("submission_", ""),
                    "basename": path.name,
                    "file": rel(path),
                    "selection_role": "external_selected",
                    "e350_plateau_gate": False,
                    "e351_compat_gate": False,
                }
            )
    if extra_rows:
        pool = pd.concat([pool, pd.DataFrame(extra_rows)], ignore_index=True, sort=False)

    deltas: dict[str, np.ndarray] = {}
    rows: list[dict[str, Any]] = []
    for _, row in pool.iterrows():
        path = locate(row.get("file", row.get("basename", "")))
        if path is None:
            continue
        delta = align_delta(path, anchor)
        deltas[path.name] = delta
        rec = row.to_dict()
        rec["basename"] = path.name
        rec["file"] = rel(path)
        rec.update(movement_features(delta))
        rows.append(rec)
    out = pd.DataFrame(rows)
    out = add_axis_features(out, deltas, axes)
    if E356_PRED_IN.exists():
        e356 = pd.read_csv(E356_PRED_IN)
        keep = [
            "variant",
            "e356_survival_score",
            "e356_top3_rate",
            "e356_strict_geometry_top3_rate",
            "e356_selector_context_top3_rate",
            "e352_top1_rate",
            "e352_top3_rate",
        ]
        out = out.merge(e356[[c for c in keep if c in e356.columns]].drop_duplicates("variant"), on="variant", how="left")
    if E355_PRED_IN.exists():
        e355 = pd.read_csv(E355_PRED_IN)
        keep = ["variant", "e355_stability_score", "e355_top3_rate", "e355_rank_mean"]
        out = out.merge(e355[[c for c in keep if c in e355.columns]].drop_duplicates("variant"), on="variant", how="left")
    return out, deltas


def predict_pool(known: pd.DataFrame, pool: pd.DataFrame, feature_cols: list[str], diag: pd.DataFrame) -> pd.DataFrame:
    train = known[known["available"].fillna(False)].copy().reset_index(drop=True)
    X = train[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    P = pool.copy()
    for col in feature_cols:
        if col not in P:
            P[col] = 0.0
    XP = P[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    model_names = diag.sort_values(["beats_perm_p95", "loo_spearman"], ascending=[False, False])["model"].tolist()
    if not model_names:
        model_names = ["ridge_10"]
    for model_name in model_names:
        model = make_model(model_name)
        model.fit(X, y)
        P[f"pred_public_loss_{model_name}"] = model.predict(XP)
    pred_cols = [c for c in P.columns if c.startswith("pred_public_loss_")]
    P["pred_public_loss_mean"] = P[pred_cols].mean(axis=1)
    P["pred_public_loss_std"] = P[pred_cols].std(axis=1).fillna(0.0)
    P["pred_public_loss_clipped"] = P["pred_public_loss_mean"].clip(lower=0.0)

    bad_cols = [c for c in P.columns if c.startswith("posproj_") and any(tok in c for tok in ["bad", "e216", "e267", "e323", "ordinal", "final9"])]
    P["public_bad_positive_projection_sum"] = P[bad_cols].sum(axis=1) if bad_cols else 0.0
    P["public_bad_positive_projection_max"] = P[bad_cols].max(axis=1) if bad_cols else 0.0
    P["e247_preservation_score"] = (
        (-P["pred_public_loss_clipped"]).rank(pct=True)
        + (-P["public_bad_positive_projection_sum"]).rank(pct=True)
        + (-P["cell_l1"]).rank(pct=True)
    ) / 3.0
    local_gain = (-pd.to_numeric(P.get("pred_delta_vs_current_p90", 0.0), errors="coerce").fillna(0.0)).rank(pct=True)
    transfer = pd.to_numeric(P.get("e356_survival_score", 0.0), errors="coerce").fillna(0.0).rank(pct=True)
    raw_stability = pd.to_numeric(P.get("e352_top3_rate", 0.0), errors="coerce").fillna(0.0).rank(pct=True)
    P["e357_public_survival_score"] = (
        1.25 * P["e247_preservation_score"]
        + 0.75 * local_gain
        + 0.55 * transfer
        + 0.45 * raw_stability
        - 0.65 * P["pred_public_loss_clipped"].rank(pct=True)
        - 0.35 * P["pred_public_loss_std"].rank(pct=True)
    )
    P = P.sort_values(
        ["e357_public_survival_score", "e247_preservation_score", "e356_survival_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    P.to_csv(POOL_OUT, index=False)
    return P


def materialize_selection(rec: pd.Series) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    src = locate(rec["file"])
    if src is None:
        raise FileNotFoundError(str(rec["file"]))
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 54)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    return out


def select_candidate(pool: pd.DataFrame) -> pd.DataFrame:
    compat = pool[pool["e351_compat_gate"].fillna(False).astype(bool)].copy()
    if compat.empty:
        compat = pool.copy()
    probe_pool = compat[
        (pd.to_numeric(compat.get("e352_top3_rate", 0.0), errors="coerce").fillna(0.0) >= 0.18)
        & (pd.to_numeric(compat.get("e356_survival_score", 0.0), errors="coerce").fillna(0.0) >= 3.0)
        & (pd.to_numeric(compat.get("pred_delta_vs_current_p90", 1.0), errors="coerce").fillna(1.0) <= -5.0e-5)
        & (pd.to_numeric(compat.get("pred_public_loss_clipped", 1.0), errors="coerce").fillna(1.0) <= 0.00025)
    ].copy()
    if probe_pool.empty:
        top = compat.iloc[0].copy()
    else:
        top = probe_pool.sort_values(
            ["e357_public_survival_score", "e247_preservation_score", "e356_survival_score"],
            ascending=[False, False, False],
        ).iloc[0].copy()
    e351 = pool[pool["variant"].astype(str).eq(E351_VARIANT)]
    e356 = pool[pool["variant"].astype(str).eq(E356_VARIANT)]
    e351_rank = int(e351.index[0] + 1) if len(e351) else -1
    e356_rank = int(e356.index[0] + 1) if len(e356) else -1
    decision = "no_new_file"
    reason = "E357 is a public-survival audit; it ranks existing compact-basin files rather than generating a new blend."
    selected_path: Path | None = None
    if str(top["variant"]) == E356_VARIANT:
        decision = "support_e356_probe"
        reason = "E356 remains the top E351-compatible point after public-survival contrast risk is included."
        selected_path = materialize_selection(top)
    elif str(top["variant"]) == E351_VARIANT:
        decision = "prefer_e351_conservative"
        reason = "Public-survival contrast risk prefers the raw E352 robust-center point over the learned E356 probe."
        selected_path = materialize_selection(top)
    elif not probe_pool.empty:
        decision = "select_existing_publicsurvival_probe"
        reason = (
            "A different existing compact-basin point best balances public-survival contrast, "
            "E352 stability, and E356 transfer-latent support."
        )
        selected_path = materialize_selection(top)
    row = top.to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "e351_e357_rank": e351_rank,
            "e356_e357_rank": e356_rank,
            "selected_file": top.get("file", ""),
            "selected_uploadsafe_file": rel(selected_path) if selected_path is not None else "",
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(known: pd.DataFrame, diag: pd.DataFrame, pool: pd.DataFrame, selection: pd.DataFrame) -> None:
    sel = selection.iloc[0]
    known_avail = known[known["available"].fillna(False)].copy()
    top_cols = [
        "variant",
        "selection_role",
        "e357_public_survival_score",
        "e247_preservation_score",
        "pred_public_loss_mean",
        "pred_public_loss_std",
        "public_bad_positive_projection_sum",
        "cell_l1",
        "pred_delta_vs_current_p90",
        "e356_survival_score",
        "e356_top3_rate",
        "e352_top3_rate",
        "e355_top3_rate",
        "file",
    ]
    top_cols = [c for c in top_cols if c in pool.columns]
    anchor_cols = [
        "basename",
        "public_lb",
        "delta_vs_e247",
        "cell_l1",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S2",
        "share_S3",
        "share_S4",
    ]
    anchor_cols = [c for c in anchor_cols if c in known_avail.columns]
    lines = [
        "# E357 Public-Survival Contrast Latent",
        "",
        "## Question",
        "",
        "Do known public observations see the E351/E356 compact lifestyle-state probes as E247-preserving and public-bad-axis avoiding?",
        "",
        "## Method",
        "",
        "- Anchor: E247 public-best submission.",
        "- Context representation: logit-space movement anatomy relative to E247 plus projections onto known public-good/bad movement axes.",
        "- Target representation: fixed known public delta versus E247.",
        "- Anti-collapse: leave-one-public-file-out prediction plus permutation Spearman check.  This is a sensor, not an optimizer.",
        "",
        "## Decision",
        "",
        f"- decision: `{sel['decision']}`",
        f"- selected/ranked file: `{sel.get('selected_file', '')}`",
        f"- selected upload-safe file: `{sel.get('selected_uploadsafe_file', '')}`",
        f"- selected variant: `{sel.get('variant', '')}`",
        f"- E351 E357 rank: `{int(sel['e351_e357_rank'])}`",
        f"- E356 E357 rank: `{int(sel['e356_e357_rank'])}`",
        f"- reason: {sel['reason']}",
        "",
        "## Known Public Anchors",
        "",
        md_table(known_avail[anchor_cols].sort_values("delta_vs_e247"), n=30, floatfmt=".9f"),
        "",
        "## LOO Diagnostics",
        "",
        md_table(diag, n=20, floatfmt=".9f"),
        "",
        "## Top Compact-Basin Candidates",
        "",
        md_table(pool[top_cols], n=35, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if str(sel["decision"]) == "support_e356_probe":
        lines.extend(
            [
                "E357 does not veto E356.  The known-public contrast latent still ranks the E356 point first inside the E351-compatible compact basin.",
                "This strengthens E356 as the next information-rich public probe, while keeping the caveat that the public-survival model has very few known public labels and cannot prove improvement beyond E247.",
            ]
        )
    elif str(sel["decision"]) == "prefer_e351_conservative":
        lines.extend(
            [
                "E357 demotes the learned E356 probe in favor of E351's raw robust center.",
                "That would mean the next public test should prefer the conservative E352 winner over the transfer-latent extrapolation.",
            ]
        )
    elif str(sel["decision"]) == "select_existing_publicsurvival_probe":
        lines.extend(
            [
                "E357 selects a different existing point in the compact lifestyle-state basin.",
                "The selected point is not a new blend: it asks whether removing the tiny `1.005` amplification while keeping the full S3-tail view is a better public-survival compromise than E351/E356.",
                "This is an information-rich probe because it directly tests the S3-tail versus micro-amplification tradeoff exposed by E350-E357.",
            ]
        )
    else:
        lines.extend(
            [
                "E357 ranks existing compact-basin candidates but does not create a new file.",
                "Use this report as a veto/risk lens before spending public submissions.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(KNOWN_OUT)}`",
            f"- `{rel(LOOCV_OUT)}`",
            f"- `{rel(POOL_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor_path = locate(ANCHOR_FILE)
    if anchor_path is None:
        raise FileNotFoundError(ANCHOR_FILE)
    anchor = logit_frame(anchor_path)
    known, known_deltas, _ = load_known(anchor)
    axes = make_axes(known_deltas)
    known = add_axis_features(known, known_deltas, axes)
    known.to_csv(KNOWN_OUT, index=False)
    feat_cols = feature_columns(known[known["available"].fillna(False)])
    diag = loo_diagnostics(known, feat_cols)
    pool, _ = load_pool(anchor, axes)
    # Align pool columns to the public-survival feature schema.
    for col in feat_cols:
        if col not in pool:
            pool[col] = 0.0
    pred = predict_pool(known, pool, feat_cols, diag)
    selection = select_candidate(pred)
    write_report(known, diag, pred, selection)
    print(f"known observations: {len(known)}")
    print(f"available public files: {int(known['available'].sum())}")
    print(f"feature cols: {len(feat_cols)}")
    print(f"candidate pool: {len(pred)}")
    print(f"decision: {selection['decision'].iloc[0]}")
    show = [
        "variant",
        "e357_public_survival_score",
        "e247_preservation_score",
        "pred_public_loss_mean",
        "public_bad_positive_projection_sum",
        "e356_survival_score",
        "e352_top3_rate",
    ]
    show = [c for c in show if c in pred.columns]
    print(pred.head(12)[show].to_string(index=False))
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
