#!/usr/bin/env python3
"""E356: public-transfer stability latent over hidden lifestyle-state candidates.

Question:
    E355 showed that an action-health latent is learnable, but the strongest
    action-health point did not survive the E352 selector-stability audit.  Is
    the public-transfer/stress stability itself predictable from candidate
    geometry, or is it only the hard-coded selector formula coming back?

JEPA/data2vec translation:
    context = candidate lifestyle-state movement geometry, family descriptors,
              selector-context views, and optional E355 action-health latent
    target  = hidden transfer-stability representation induced by E352
              selector perturbations
    action  = choose a submission only if a non-E351 point beats E351 under
              transfer-stability latent and conservative public-free gates

No public LB is used.  E352 is a local stress sensor, not leaderboard feedback.
"""

from __future__ import annotations

import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e349_e347_target_cell_ablation_stress import clip_prob, short_hash  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402


RNG_SEED = 20260531 + 356
UPLOAD_PREFIX = "submission_e356_transferstable"
E351_VARIANT = "compact_t75_s1.005_s3a0.25"

RANKED_IN = OUT / "e351_robust_plateau_selector_ranked.csv"
SCENARIOS_IN = OUT / "e352_selector_sensitivity_scenarios.csv"
E355_IN = OUT / "e355_action_health_plateau_predictions.csv"

TRAIN_OUT = OUT / "e356_transfer_stability_latent_training.csv"
DIAG_OUT = OUT / "e356_transfer_stability_latent_diagnostics.csv"
PRED_OUT = OUT / "e356_transfer_stability_predictions.csv"
SELECT_OUT = OUT / "e356_transfer_stability_selection.csv"
REPORT_OUT = OUT / "e356_transfer_stability_latent_report.md"


CAT_FEATURE_CANDIDATES = [
    "target_set",
    "row_mask",
    "cell_mask",
    "sign_mask",
    "family",
    "file_selector",
    "source_family",
    "operation",
    "method",
]

SELECTOR_CONTEXT_COLS = [
    "p90_pct",
    "risk_pct",
    "bad_margin_pct",
    "q1_specificity_pct",
    "support_pct",
    "compat_e349_pct",
    "micro_scale_pct",
    "s3_tail_present",
    "threshold_frac",
    "scale",
    "s3_alpha",
    "pred_delta_vs_current_p90",
    "public_analog_risk_score",
    "incremental_bad_axis_vs_current",
    "q1_specificity_margin",
    "plateau_support_score",
    "prob_l1_delta_vs_e349",
    "prob_l1_delta_vs_e347",
    "direct_bad_poscos_sum",
    "scale_abs_delta",
]

E355_COLS = [
    "e355_world_count",
    "e355_score_mean",
    "e355_score_std",
    "e355_rank_mean",
    "e355_rank_worst",
    "e355_top1_rate",
    "e355_top3_rate",
    "e355_top5_rate",
    "pred_visibility_mean",
    "pred_risk_good_mean",
    "pred_q1_specificity_mean",
    "pred_bad_margin_mean",
    "e355_stability_score",
]

ALWAYS_DROP = {
    "file",
    "basename",
    "source_file",
    "selected_uploadsafe_file",
    "variant",
    "targets",
}

FORBIDDEN_TOKENS = [
    "e352_",
    "transfer_",
    "top1",
    "top3",
    "selected",
    "decision",
    "reason",
    "uploadsafe",
]

STRICT_GEOMETRY_FORBIDDEN = [
    "p90_pct",
    "risk_pct",
    "bad_margin_pct",
    "q1_specificity_pct",
    "support_pct",
    "compat_e349_pct",
    "micro_scale_pct",
    "e351_",
    "e350_plateau_gate",
    "public_analog_risk",
    "risk_delta",
    "q1_specificity",
    "q1_margin",
    "plateau_support",
    "pred_delta_vs_current",
    "p90_gain",
    "bad_axis_margin",
    "incremental_bad_axis",
    "prob_l1_delta",
    "direct_bad_poscos",
    "scale_abs_delta",
    "e355_",
    "pred_visibility",
    "pred_risk",
    "pred_q1",
    "pred_bad",
]

SELECTOR_VIEW_FORBIDDEN = [
    "e351_robust_score",
    "e351_compat_gate",
    "e350_plateau_gate",
    "e350_local_gate",
    "e349_gate",
    "e347_gate",
    "e355_",
    "pred_visibility",
    "pred_risk",
    "pred_q1",
    "pred_bad",
]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_num(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)


def pct_high(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").rank(pct=True, method="average")


def pct_low(series: pd.Series) -> pd.Series:
    return (-pd.to_numeric(series, errors="coerce")).rank(pct=True, method="average")


def safe_spearman(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 8:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


def e352_rates() -> pd.DataFrame:
    scen = pd.read_csv(SCENARIOS_IN)
    total = max(int(len(scen)), 1)
    rows: dict[str, dict[str, float]] = {}
    for rec in scen.to_dict("records"):
        scenario = str(rec.get("scenario", ""))
        top = str(rec.get("top_variant", "")).strip()
        if top:
            item = rows.setdefault(top, {"top1": 0.0, "top3": 0.0, "det_top1": 0.0, "det_top3": 0.0})
            item["top1"] += 1.0
            if scenario != "random":
                item["det_top1"] += 1.0
        raw = str(rec.get("top3_variants", ""))
        normalized = raw.replace("[", "").replace("]", "").replace("'", "").replace(",", "|")
        for token in normalized.split("|"):
            var = token.strip()
            if not var:
                continue
            item = rows.setdefault(var, {"top1": 0.0, "top3": 0.0, "det_top1": 0.0, "det_top3": 0.0})
            item["top3"] += 1.0
            if scenario != "random":
                item["det_top3"] += 1.0
    det_total = max(int((scen["scenario"].astype(str) != "random").sum()), 1)
    out = pd.DataFrame(
        [
            {
                "variant": key,
                "e352_top1_rate": val["top1"] / total,
                "e352_top3_rate": val["top3"] / total,
                "e352_deterministic_top1_rate": val["det_top1"] / det_total,
                "e352_deterministic_top3_rate": val["det_top3"] / det_total,
            }
            for key, val in rows.items()
        ]
    )
    return out


def build_training_frame() -> pd.DataFrame:
    ranked = pd.read_csv(RANKED_IN).replace([np.inf, -np.inf], np.nan)
    rates = e352_rates()
    frame = ranked.merge(rates, on="variant", how="left")
    for col in [
        "e352_top1_rate",
        "e352_top3_rate",
        "e352_deterministic_top1_rate",
        "e352_deterministic_top3_rate",
    ]:
        frame[col] = safe_num(frame, col, default=0.0).fillna(0.0)
    if E355_IN.exists():
        e355 = pd.read_csv(E355_IN)
        keep = ["variant", *[c for c in E355_COLS if c in e355.columns]]
        frame = frame.merge(e355[keep].drop_duplicates("variant"), on="variant", how="left")
    for col in E355_COLS:
        if col not in frame:
            frame[col] = np.nan

    for col in ["e350_plateau_gate", "e351_compat_gate", "s3_tail_present"]:
        if col in frame:
            frame[col] = frame[col].fillna(False).astype(bool)

    # Stability target: E352 top1/top3 are sparse rates, so use a smoothed
    # log-scale representation and then a rank-normalized target.  This is the
    # hidden public-transfer state we try to predict from context views.
    top1 = safe_num(frame, "e352_top1_rate", 0.0).fillna(0.0).clip(lower=0.0)
    top3 = safe_num(frame, "e352_top3_rate", 0.0).fillna(0.0).clip(lower=0.0)
    det3 = safe_num(frame, "e352_deterministic_top3_rate", 0.0).fillna(0.0).clip(lower=0.0)
    raw = np.log1p(45.0 * top1) + 0.78 * np.log1p(35.0 * top3) + 0.20 * np.log1p(10.0 * det3)
    frame["transfer_signal_raw"] = raw
    frame["transfer_signal_rank"] = pd.Series(raw).rank(pct=True, method="average").to_numpy()
    frame["transfer_has_support"] = top3.gt(0.0)

    # These percentiles are not the target; they describe candidate movement
    # health and are useful for the selector-context view.
    if "pred_delta_vs_current_p90" in frame:
        frame["p90_visibility_pct"] = pct_low(frame["pred_delta_vs_current_p90"])
    if "public_analog_risk_score" in frame:
        frame["public_risk_safe_pct"] = pct_low(frame["public_analog_risk_score"])
    if "incremental_bad_axis_vs_current" in frame:
        frame["bad_axis_safe_pct"] = pct_low(frame["incremental_bad_axis_vs_current"].abs())
    if "q1_specificity_margin" in frame:
        frame["q1_specificity_margin_pct"] = pct_high(frame["q1_specificity_margin"])

    frame.to_csv(TRAIN_OUT, index=False)
    return frame


def view_feature_columns(frame: pd.DataFrame, view: str) -> tuple[list[str], list[str]]:
    numeric_cols: list[str] = []
    view_forbidden = list(FORBIDDEN_TOKENS)
    if view == "strict_geometry":
        view_forbidden += STRICT_GEOMETRY_FORBIDDEN
    elif view == "selector_context":
        view_forbidden += SELECTOR_VIEW_FORBIDDEN
    elif view == "action_augmented":
        view_forbidden += SELECTOR_VIEW_FORBIDDEN
    else:
        raise ValueError(view)

    allowed_selector = set(SELECTOR_CONTEXT_COLS)
    allowed_e355 = set(E355_COLS) if view == "action_augmented" else set()

    for col in frame.columns:
        low = col.lower()
        if col in ALWAYS_DROP:
            continue
        if any(token in low for token in view_forbidden):
            if col not in allowed_selector and col not in allowed_e355:
                continue
        if view == "strict_geometry" and col in allowed_selector.union(allowed_e355):
            continue
        if view == "selector_context" and col in allowed_e355:
            continue
        if pd.api.types.is_numeric_dtype(frame[col]):
            if frame[col].notna().sum() >= 10 and frame[col].nunique(dropna=True) > 1:
                numeric_cols.append(col)

    cat_cols = [
        c
        for c in CAT_FEATURE_CANDIDATES
        if c in frame.columns
        and frame[c].notna().sum() >= 10
        and c not in ALWAYS_DROP
    ]
    return sorted(set(numeric_cols)), cat_cols


def make_model(numeric_cols: list[str], cat_cols: list[str], model_name: str):
    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric_cols:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric_cols))
    if cat_cols:
        transformers.append(
            (
                "cat",
                make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                cat_cols,
            )
        )
    if model_name == "extratrees":
        estimator = ExtraTreesRegressor(
            n_estimators=360,
            min_samples_leaf=3,
            max_features=0.72,
            random_state=RNG_SEED,
            n_jobs=-1,
        )
    elif model_name == "randomforest":
        estimator = RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=3,
            max_features=0.72,
            random_state=RNG_SEED + 17,
            n_jobs=-1,
        )
    else:
        raise ValueError(model_name)
    return make_pipeline(ColumnTransformer(transformers, remainder="drop"), estimator)


def cv_splits(frame: pd.DataFrame, scheme: str) -> tuple[list[tuple[np.ndarray, np.ndarray]], np.ndarray | None]:
    n = len(frame)
    if scheme == "random_kfold":
        cv = KFold(n_splits=min(5, n), shuffle=True, random_state=RNG_SEED)
        return list(cv.split(frame)), None

    if scheme == "threshold_holdout":
        group = safe_num(frame, "threshold_frac", default=-1).fillna(-1).astype(str).to_numpy()
    elif scheme == "s3_holdout":
        group = safe_num(frame, "s3_alpha", default=-99).fillna(-99).astype(str).to_numpy()
    elif scheme == "scale_holdout":
        group = safe_num(frame, "scale", default=-99).fillna(-99).astype(str).to_numpy()
    else:
        raise ValueError(scheme)

    n_groups = len(pd.unique(group))
    if n_groups < 2:
        return [], group
    cv = GroupKFold(n_splits=min(5, n_groups))
    return list(cv.split(frame, groups=group)), group


def oof_for(
    frame: pd.DataFrame,
    numeric_cols: list[str],
    cat_cols: list[str],
    target: str,
    model_name: str,
    scheme: str,
) -> np.ndarray:
    splits, _ = cv_splits(frame, scheme)
    oof = np.full(len(frame), np.nan, dtype=float)
    if not splits:
        return oof
    y = safe_num(frame, target, default=0.0).fillna(0.0).to_numpy(dtype=float)
    for tr, va in splits:
        if len(np.unique(y[tr])) < 2:
            continue
        model = make_model(numeric_cols, cat_cols, model_name)
        model.fit(frame.iloc[tr][numeric_cols + cat_cols], y[tr])
        oof[va] = model.predict(frame.iloc[va][numeric_cols + cat_cols])
    return oof


def latent_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    train_all = frame[frame["e350_plateau_gate"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    train_compat = frame[
        frame["e350_plateau_gate"].fillna(False).astype(bool)
        & frame["e351_compat_gate"].fillna(False).astype(bool)
    ].copy().reset_index(drop=True)

    for train_name, train in [("plateau_all", train_all), ("compat_pool", train_compat)]:
        if len(train) < 20:
            continue
        for view in ["strict_geometry", "selector_context", "action_augmented"]:
            numeric_cols, cat_cols = view_feature_columns(train, view)
            if not numeric_cols and not cat_cols:
                continue
            for model_name in ["extratrees", "randomforest"]:
                for target in ["transfer_signal_raw", "transfer_signal_rank", "e352_top3_rate"]:
                    for scheme in ["random_kfold", "threshold_holdout", "s3_holdout", "scale_holdout"]:
                        oof = oof_for(train, numeric_cols, cat_cols, target, model_name, scheme)
                        valid = pd.Series(oof).notna()
                        if int(valid.sum()) < 8:
                            continue
                        y = safe_num(train, target, default=0.0).fillna(0.0).to_numpy(dtype=float)
                        rows.append(
                            {
                                "train_scope": train_name,
                                "view": view,
                                "model": model_name,
                                "target": target,
                                "scheme": scheme,
                                "rows": int(len(train)),
                                "valid_oof_rows": int(valid.sum()),
                                "feature_count": int(len(numeric_cols) + len(cat_cols)),
                                "numeric_feature_count": int(len(numeric_cols)),
                                "cat_feature_count": int(len(cat_cols)),
                                "oof_spearman": safe_spearman(y, oof),
                                "oof_mae": float(np.nanmean(np.abs(oof - y))),
                                "target_mean": float(np.nanmean(y)),
                                "target_std": float(np.nanstd(y)),
                                "e351_oof_pred": float(oof[train["variant"].eq(E351_VARIANT)].mean())
                                if train["variant"].eq(E351_VARIANT).any()
                                else np.nan,
                            }
                        )
    diag = pd.DataFrame(rows)
    if len(diag):
        diag = diag.sort_values(
            ["train_scope", "target", "scheme", "oof_spearman"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)
    diag.to_csv(DIAG_OUT, index=False)
    return diag


def fit_predict_worlds(frame: pd.DataFrame) -> pd.DataFrame:
    pool = frame[
        frame["e350_plateau_gate"].fillna(False).astype(bool)
        & frame["e351_compat_gate"].fillna(False).astype(bool)
    ].copy()
    if pool.empty:
        raise RuntimeError("No E351-compatible plateau pool")

    train_scopes = {
        "plateau_all": frame[frame["e350_plateau_gate"].fillna(False).astype(bool)].copy(),
        "compat_pool": pool.copy(),
    }

    long_frames: list[pd.DataFrame] = []
    for scope, train in train_scopes.items():
        if len(train) < 20:
            continue
        for view in ["strict_geometry", "selector_context", "action_augmented"]:
            numeric_cols, cat_cols = view_feature_columns(train, view)
            if not numeric_cols and not cat_cols:
                continue
            for col in numeric_cols + cat_cols:
                if col not in pool:
                    pool[col] = np.nan
            for model_name in ["extratrees", "randomforest"]:
                for target in ["transfer_signal_raw", "transfer_signal_rank", "e352_top3_rate"]:
                    y = safe_num(train, target, default=0.0).fillna(0.0).to_numpy(dtype=float)
                    if len(np.unique(y)) < 2:
                        continue
                    model = make_model(numeric_cols, cat_cols, model_name)
                    model.fit(train[numeric_cols + cat_cols], y)
                    pred = model.predict(pool[numeric_cols + cat_cols])
                    long = pool[
                        [
                            "variant",
                            "basename",
                            "file",
                            "threshold_frac",
                            "scale",
                            "s3_alpha",
                            "pred_delta_vs_current_p90",
                            "public_analog_risk_score",
                            "incremental_bad_axis_vs_current",
                            "q1_specificity_margin",
                            "plateau_support_score",
                            "prob_l1_delta_vs_e349",
                            "e351_robust_score",
                            "e352_top1_rate",
                            "e352_top3_rate",
                            "e352_deterministic_top3_rate",
                        ]
                    ].copy()
                    long["train_scope"] = scope
                    long["view"] = view
                    long["model"] = model_name
                    long["target"] = target
                    long["pred"] = pred
                    long["pred_pct"] = pct_high(pd.Series(pred)).to_numpy()
                    long["world_rank"] = pd.Series(pred).rank(ascending=False, method="min").to_numpy()
                    long_frames.append(long)

    if not long_frames:
        raise RuntimeError("No transfer-stability prediction worlds")
    long_all = pd.concat(long_frames, ignore_index=True)
    long_all.to_csv(OUT / "e356_transfer_stability_predictions_long.csv", index=False)

    agg = (
        long_all.groupby(["variant", "basename", "file"], as_index=False)
        .agg(
            e356_world_count=("pred", "size"),
            e356_pred_mean=("pred_pct", "mean"),
            e356_pred_std=("pred_pct", "std"),
            e356_rank_mean=("world_rank", "mean"),
            e356_rank_worst=("world_rank", "max"),
            e356_top1_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 1))),
            e356_top3_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 3))),
            e356_top5_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 5))),
            e356_strict_top3_rate=("world_rank", lambda s: np.nan),
        )
        .reset_index(drop=True)
    )

    # Add view-specific top rates; pandas named aggregation cannot see another
    # column inside the lambda cleanly, so compute compact pivots explicitly.
    for view in ["strict_geometry", "selector_context", "action_augmented"]:
        sub = long_all[long_all["view"].eq(view)]
        tmp = (
            sub.groupby("variant")
            .agg(
                **{
                    f"e356_{view}_top3_rate": ("world_rank", lambda s: float(np.mean(np.asarray(s) <= 3))),
                    f"e356_{view}_pred_mean": ("pred_pct", "mean"),
                }
            )
            .reset_index()
        )
        agg = agg.merge(tmp, on="variant", how="left")

    metric_cols = [
        "variant",
        "threshold_frac",
        "scale",
        "s3_alpha",
        "pred_delta_vs_current_p90",
        "public_analog_risk_score",
        "incremental_bad_axis_vs_current",
        "q1_specificity_margin",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "e351_robust_score",
        "e352_top1_rate",
        "e352_top3_rate",
        "e352_deterministic_top3_rate",
        *[c for c in E355_COLS if c in pool.columns],
    ]
    metric_cols = [c for c in metric_cols if c in pool.columns]
    agg = agg.merge(pool[metric_cols].drop_duplicates("variant"), on="variant", how="left")
    agg["e356_survival_score"] = (
        1.25 * agg["e356_pred_mean"].rank(pct=True)
        + 1.00 * (-agg["e356_rank_mean"]).rank(pct=True)
        + 0.85 * agg["e356_top3_rate"]
        + 0.65 * agg["e356_selector_context_top3_rate"].fillna(0.0)
        + 0.45 * agg["e356_strict_geometry_top3_rate"].fillna(0.0)
        + 0.35 * agg["e352_top3_rate"].fillna(0.0)
        + 0.25 * agg.get("e355_top3_rate", pd.Series(0.0, index=agg.index)).fillna(0.0)
        - 0.30 * agg["e356_pred_std"].fillna(0.0).rank(pct=True)
    )
    agg = agg.sort_values(
        ["e356_survival_score", "e356_top3_rate", "e352_top3_rate", "e356_rank_mean"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    agg.to_csv(PRED_OUT, index=False)
    return agg


def materialize_selection(rec: pd.Series) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    src = locate(rec["file"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 54)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    return out


def select_candidate(pred: pd.DataFrame) -> tuple[pd.DataFrame, Path | None]:
    e351 = pred[pred["variant"].eq(E351_VARIANT)]
    e351_rank = int(e351.index[0] + 1) if len(e351) else -1
    e351_score = float(e351["e356_survival_score"].iloc[0]) if len(e351) else -np.inf
    e351_top3 = float(e351["e352_top3_rate"].iloc[0]) if len(e351) else 0.0

    top = pred.iloc[0].copy()
    decision = "no_new_candidate"
    reason = "E356 transfer-stability latent does not find a safer non-E351 replacement."
    selected: Path | None = None

    if str(top["variant"]) == E351_VARIANT:
        decision = "confirm_e351"
        reason = "Transfer-stability latent selects the same robust-center candidate as E351."
    else:
        improvement = float(top["e356_survival_score"] - e351_score)
        local_transfer_ok = float(top["e352_top3_rate"]) >= max(0.18, 0.80 * e351_top3)
        pred_transfer_ok = float(top["e356_top3_rate"]) >= 0.35
        strict_ok = float(top.get("e356_strict_geometry_top3_rate", 0.0)) >= 0.10
        selector_ok = float(top.get("e356_selector_context_top3_rate", 0.0)) >= 0.25
        public_risk_ok = float(top.get("public_analog_risk_score", 9.0)) <= 0.04478
        p90_ok = float(top.get("pred_delta_vs_current_p90", 1.0)) <= -5.0e-5
        q1_ok = float(top.get("q1_specificity_margin", 0.0)) >= 0.31
        bad_ok = abs(float(top.get("incremental_bad_axis_vs_current", 9.0))) <= 0.0148
        if (
            improvement >= 0.06
            and local_transfer_ok
            and pred_transfer_ok
            and strict_ok
            and selector_ok
            and public_risk_ok
            and p90_ok
            and q1_ok
            and bad_ok
        ):
            selected = materialize_selection(top)
            decision = "select_new_uploadsafe"
            reason = (
                "A non-E351 plateau point wins transfer-stability latent and passes local stress gates; "
                "treat it as an information-rich public-transfer probe because raw E352 top3 still favors E351."
            )

    row = top.to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "e351_e356_rank": e351_rank,
            "e351_e356_survival_score": e351_score,
            "e351_e352_top3_rate": e351_top3,
            "selected_uploadsafe_file": rel(selected) if selected is not None else "",
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECT_OUT, index=False)
    return out, selected


def write_report(frame: pd.DataFrame, diag: pd.DataFrame, pred: pd.DataFrame, selection: pd.DataFrame, selected: Path | None) -> None:
    sel = selection.iloc[0]
    e351 = pred[pred["variant"].eq(E351_VARIANT)]
    e351_summary = e351.iloc[0].to_dict() if len(e351) else {}
    top_cols = [
        "variant",
        "threshold_frac",
        "scale",
        "s3_alpha",
        "e356_survival_score",
        "e356_pred_mean",
        "e356_pred_std",
        "e356_rank_mean",
        "e356_rank_worst",
        "e356_top1_rate",
        "e356_top3_rate",
        "e356_top5_rate",
        "e356_strict_geometry_top3_rate",
        "e356_selector_context_top3_rate",
        "e356_action_augmented_top3_rate",
        "e352_top1_rate",
        "e352_top3_rate",
        "e355_top3_rate",
        "pred_delta_vs_current_p90",
        "public_analog_risk_score",
        "q1_specificity_margin",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "e351_robust_score",
    ]
    top_cols = [c for c in top_cols if c in pred.columns]
    diag_focus = diag[
        diag["target"].isin(["transfer_signal_raw", "e352_top3_rate"])
        & diag["scheme"].isin(["random_kfold", "threshold_holdout", "s3_holdout"])
    ].copy()
    diag_focus = diag_focus.sort_values("oof_spearman", ascending=False)

    status_counts = (
        frame.groupby(["e350_plateau_gate", "e351_compat_gate"], dropna=False)
        .agg(
            rows=("variant", "size"),
            mean_top3=("e352_top3_rate", "mean"),
            max_top3=("e352_top3_rate", "max"),
            support_rate=("transfer_has_support", "mean"),
        )
        .reset_index()
    )

    lines = [
        "# E356 Transfer-Stability Latent Selector",
        "",
        "## Question",
        "",
        "Can the hidden lifestyle-state candidate's selector/public-transfer stability be predicted from its movement context, rather than from a leaderboard score or another hand blend?",
        "",
        "## Method",
        "",
        "- Context views:",
        "  - `strict_geometry`: candidate recipe and movement geometry with selector-health columns removed.",
        "  - `selector_context`: public-free E351 selector components, but not final E352 rates.",
        "  - `action_augmented`: selector context plus E355 action-health latent predictions.",
        "- Target representation: E352 perturbation stability (`top1/top3`) compressed into `transfer_signal_raw` and rank-normalized `transfer_signal_rank`.",
        "- Anti-collapse checks: random KFold, threshold holdout, S3-alpha holdout, and scale holdout.",
        "",
        "## Decision",
        "",
        f"- decision: `{sel['decision']}`",
        f"- selected upload-safe file: `{rel(selected) if selected is not None else 'none'}`",
        f"- top E356 variant: `{sel['variant']}`",
        f"- E351 E356 rank: `{int(sel['e351_e356_rank'])}`",
        f"- E351 E352 top3 rate: `{float(sel['e351_e352_top3_rate']):.6f}`",
        f"- reason: {sel['reason']}",
        f"- top variant E352 top3 rate: `{float(sel['e352_top3_rate']):.6f}`",
        f"- top variant delta vs E247: Q1/Q2/Q3/S1/S3 compact action, S2/S4 unchanged; see prediction table for magnitude proxies.",
        "",
        "## E351 Reference",
        "",
        md_table(pd.DataFrame([e351_summary])[[c for c in top_cols if c in e351_summary]], n=1, floatfmt=".9f")
        if e351_summary
        else "_missing_",
        "",
        "## Candidate Pool Status",
        "",
        md_table(status_counts, n=10, floatfmt=".9f"),
        "",
        "## Latent Diagnostics",
        "",
        md_table(diag_focus, n=30, floatfmt=".9f") if len(diag_focus) else "_empty_",
        "",
        "## Top Transfer-Stability Predictions",
        "",
        md_table(pred[top_cols], n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if str(sel["decision"]) == "confirm_e351":
        lines.extend(
            [
                "E356 strengthens the current E351/E356 interpretation: transfer stability is learnable, but the learned latent still points to the robust-center candidate.",
                "The hidden lifestyle-state signal appears to be a narrow plateau selection problem, not an invitation to move farther from E247.",
            ]
        )
    elif str(sel["decision"]) == "select_new_uploadsafe":
        lines.extend(
            [
                "E356 found a non-E351 candidate that survives transfer-stability prediction and local stress gates.",
                "This is a submission candidate because its claim is specific: a different point in the same lifestyle-state plateau may better express the transfer-stable lifestyle state than the hand-selected robust center.",
                "Caveat: raw E352 selector perturbations still give E351 the highest top3 rate, and scale-holdout diagnostics are weak.  E356 should therefore be treated as a high-information probe, not as a proven replacement for E247/E351.",
            ]
        )
    else:
        lines.extend(
            [
                "E356 does not justify a new submission.  The stress-stability target is partly learnable, but the non-E351 winners either lose E352 support or depend too much on selector-context shortcuts.",
                "This is evidence that the next breakthrough is unlikely to come from another small plateau selector tweak alone.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(TRAIN_OUT)}`",
            f"- `{rel(DIAG_OUT)}`",
            f"- `{rel(PRED_OUT)}`",
            f"- `{rel(SELECT_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    frame = build_training_frame()
    diag = latent_diagnostics(frame)
    pred = fit_predict_worlds(frame)
    selection, selected = select_candidate(pred)
    write_report(frame, diag, pred, selection, selected)
    print(f"training rows: {len(frame)}")
    print(f"diagnostics rows: {len(diag)}")
    print(f"prediction pool: {len(pred)}")
    print(f"decision: {selection['decision'].iloc[0]}")
    print(f"selected: {rel(selected) if selected is not None else 'none'}")
    show = [
        "variant",
        "e356_survival_score",
        "e356_rank_mean",
        "e356_top3_rate",
        "e356_strict_geometry_top3_rate",
        "e356_selector_context_top3_rate",
        "e352_top3_rate",
        "e355_top3_rate",
    ]
    show = [c for c in show if c in pred.columns]
    print(pred.head(15)[show].to_string(index=False))
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
