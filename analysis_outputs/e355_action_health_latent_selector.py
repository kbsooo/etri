#!/usr/bin/env python3
"""E355: action-health latent selector over the compact lifestyle-state basin.

Question:
    E354 showed that the current E247/E256 support boundary is not an
    independent support action on top of E351.  Can we instead learn the hidden
    "action health" representation from the experiment archive itself?

JEPA/data2vec translation:
    context = candidate movement geometry, target mix, reference-axis geometry,
              and human/social action descriptors
    target  = outcome representation: visibility, public-analog risk,
              Q1 lifestyle specificity, and bad-axis margin
    action  = choose, or reject, a point inside the E350/E351 compact
              lifestyle-state plateau

No public LB is used.  Known public observations enter only through already
materialized public-analog risk columns from earlier public-free audits.
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
from sklearn.model_selection import GroupKFold
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


RNG_SEED = 20260531 + 355
EPS = 1.0e-12
UPLOAD_PREFIX = "submission_e355_actionhealth"

ARCHIVE_SPECS = [
    ("E347", OUT / "e347_lifestyle_state_candidate_reaudit_scores.csv"),
    ("E349", OUT / "e349_e347_target_cell_ablation_scores.csv"),
    ("E350", OUT / "e350_compact_state_plateau_scores.csv"),
    ("E353", OUT / "e353_public_tangent_neutralization_scores.csv"),
    ("E354", OUT / "e354_e247_support_lifestyle_graft_scores.csv"),
]

POOL_IN = OUT / "e351_robust_plateau_selector_ranked.csv"
SCENARIOS_IN = OUT / "e352_selector_sensitivity_scenarios.csv"

ARCHIVE_OUT = OUT / "e355_action_health_latent_archive.csv"
DIAG_OUT = OUT / "e355_action_health_latent_diagnostics.csv"
PRED_OUT = OUT / "e355_action_health_plateau_predictions.csv"
SELECT_OUT = OUT / "e355_action_health_selection.csv"
REPORT_OUT = OUT / "e355_action_health_latent_selector_report.md"


TARGET_COMPONENTS = [
    "y_visibility",
    "y_risk_good",
    "y_q1_specificity",
    "y_bad_margin",
]

CAT_FEATURE_CANDIDATES = [
    "exp_id",
    "target_set",
    "row_mask",
    "cell_mask",
    "sign_mask",
    "family",
    "source_family",
    "operation",
    "method",
    "axis_set",
    "guard_group",
    "source",
    "opposite_only",
]

EXCLUDE_FEATURE_TOKENS = [
    "pred_delta",
    "pred_beats",
    "strict_promote",
    "info_sensor",
    "below_resolution",
    "block_gate",
    "gate",
    "selected",
    "public_analog_risk",
    "risk_delta",
    "risk_not",
    "specificity",
    "q1_state",
    "nonq1",
    "permuted",
    "state_corr",
    "state_enrich",
    "state_specificity",
    "local_mean",
    "local_p90",
    "local_bad",
    "p90_gain",
    "p90_margin",
    "bad_axis_margin",
    "e351_",
    "e350_plateau_gate",
    "e350_local_gate",
    "e349_gate",
    "e347_gate",
    "e353_local_gate",
    "e354_local_gate",
    "plateau_support",
    "same_threshold",
    "same_alpha",
    "near_threshold",
    "alpha_support",
    "support_actual",
    "support_interference_delta",
    "support_alignment_delta",
    "dominance",
    "null_",
    "actual_",
    "target_health",
    "y_",
]


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


def pct_high(series: pd.Series) -> pd.Series:
    return series.astype(float).rank(pct=True, method="average")


def pct_low(series: pd.Series) -> pd.Series:
    return (-series.astype(float)).rank(pct=True, method="average")


def safe_num(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[col], errors="coerce")


def first_existing(frame: pd.DataFrame, names: list[str], default: float = np.nan) -> pd.Series:
    out = pd.Series(default, index=frame.index, dtype="float64")
    for name in names:
        if name in frame:
            s = pd.to_numeric(frame[name], errors="coerce")
            out = out.where(out.notna(), s)
    return out


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


def read_archive() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for exp_id, path in ARCHIVE_SPECS:
        if not path.exists():
            continue
        df = pd.read_csv(path).replace([np.inf, -np.inf], np.nan)
        df["exp_id"] = exp_id
        if "local_p90" in df and "pred_delta_vs_current_p90" not in df:
            df["pred_delta_vs_current_p90"] = df["local_p90"]
        if "local_mean" in df and "pred_delta_vs_current_mean" not in df:
            df["pred_delta_vs_current_mean"] = df["local_mean"]
        if "local_bad_axis" in df and "incremental_bad_axis_vs_current" not in df:
            df["incremental_bad_axis_vs_current"] = df["local_bad_axis"]
        if "file" not in df:
            df["file"] = ""
        if "basename" not in df:
            df["basename"] = df["file"].astype(str).map(lambda x: Path(x).name)
        frames.append(df)
    if not frames:
        raise RuntimeError("No archive score files found")
    out = pd.concat(frames, ignore_index=True, sort=False).replace([np.inf, -np.inf], np.nan)
    out = out[~out["basename"].astype(str).eq("")].copy()
    out = out[~out["basename"].astype(str).eq("nan")].copy()

    out["y_visibility"] = -first_existing(out, ["pred_delta_vs_current_p90", "local_p90"])
    out["y_mean_visibility"] = -first_existing(out, ["pred_delta_vs_current_mean", "local_mean"])
    out["y_beats"] = first_existing(out, ["pred_beats_current_rate"], default=np.nan)
    out["y_risk_good"] = -safe_num(out, "public_analog_risk_score")
    out["y_q1_specificity"] = safe_num(out, "q1_specificity_margin")
    out["y_bad_margin"] = 0.015 - first_existing(out, ["incremental_bad_axis_vs_current", "local_bad_axis"], default=np.nan).abs()

    full_mask = out[TARGET_COMPONENTS].notna().all(axis=1)
    full = out[full_mask].copy()
    if full.empty:
        raise RuntimeError("No rows with full action-health target components")

    full["visibility_pct"] = pct_high(full["y_visibility"])
    full["risk_pct"] = pct_high(full["y_risk_good"])
    full["q1_pct"] = pct_high(full["y_q1_specificity"])
    full["bad_pct"] = pct_high(full["y_bad_margin"])
    if "pred_beats_current_rate" in full:
        full["beats_pct"] = pct_high(safe_num(full, "pred_beats_current_rate").fillna(0.0))
    else:
        full["beats_pct"] = 0.5
    full["y_action_health"] = (
        1.45 * full["visibility_pct"]
        + 1.25 * full["risk_pct"]
        + 1.10 * full["q1_pct"]
        + 1.00 * full["bad_pct"]
        + 0.35 * full["beats_pct"]
    ) / 5.15
    full["e355_reference_gate"] = (
        (full["y_visibility"] >= 5.0e-5)
        & (full["y_bad_margin"] >= 0.0)
        & (full["y_risk_good"] >= -0.04485)
        & (full["y_q1_specificity"] >= 0.28)
    )
    full.to_csv(ARCHIVE_OUT, index=False)
    return full.reset_index(drop=True)


def feature_columns(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_cols: list[str] = []
    for col in frame.columns:
        low = col.lower()
        if col in {"file", "basename", "source_file", "selected_uploadsafe_file"}:
            continue
        if any(token in low for token in EXCLUDE_FEATURE_TOKENS):
            continue
        if pd.api.types.is_numeric_dtype(frame[col]):
            if frame[col].notna().sum() >= 10 and frame[col].nunique(dropna=True) > 1:
                numeric_cols.append(col)
    cat_cols = [c for c in CAT_FEATURE_CANDIDATES if c in frame.columns and frame[c].notna().sum() >= 10]
    return numeric_cols, cat_cols


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
            n_estimators=320,
            min_samples_leaf=4,
            max_features=0.75,
            random_state=RNG_SEED,
            n_jobs=-1,
        )
    elif model_name == "randomforest":
        estimator = RandomForestRegressor(
            n_estimators=260,
            min_samples_leaf=4,
            max_features=0.75,
            random_state=RNG_SEED + 17,
            n_jobs=-1,
        )
    else:
        raise ValueError(model_name)
    return make_pipeline(ColumnTransformer(transformers, remainder="drop"), estimator)


def latent_diagnostics(archive: pd.DataFrame, numeric_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    groups = archive["exp_id"].astype(str).to_numpy()
    n_groups = archive["exp_id"].nunique()
    n_splits = min(5, int(n_groups))
    if n_splits < 2:
        pd.DataFrame().to_csv(DIAG_OUT, index=False)
        return pd.DataFrame()

    target_cols = [*TARGET_COMPONENTS, "y_action_health"]
    for target in target_cols:
        y = archive[target].astype(float).to_numpy()
        for model_name in ["extratrees", "randomforest"]:
            oof = np.full(len(archive), np.nan, dtype=float)
            cv = GroupKFold(n_splits=n_splits)
            for tr, va in cv.split(archive, groups=groups):
                model = make_model(numeric_cols, cat_cols, model_name)
                model.fit(archive.iloc[tr][numeric_cols + cat_cols], y[tr])
                oof[va] = model.predict(archive.iloc[va][numeric_cols + cat_cols])
            rows.append(
                {
                    "target": target,
                    "model": model_name,
                    "rows": int(len(archive)),
                    "groups": int(n_groups),
                    "oof_spearman": safe_spearman(y, oof),
                    "oof_mae": float(np.nanmean(np.abs(oof - y))),
                    "target_mean": float(np.nanmean(y)),
                    "target_std": float(np.nanstd(y)),
                    "feature_count": int(len(numeric_cols) + len(cat_cols)),
                    "numeric_feature_count": int(len(numeric_cols)),
                    "cat_feature_count": int(len(cat_cols)),
                }
            )
    diag = pd.DataFrame(rows).sort_values(["target", "oof_spearman"], ascending=[True, False]).reset_index(drop=True)
    diag.to_csv(DIAG_OUT, index=False)
    return diag


def load_pool() -> pd.DataFrame:
    pool = pd.read_csv(POOL_IN).replace([np.inf, -np.inf], np.nan).copy()
    pool["exp_id"] = "E350_POOL"
    pool["pool_gate"] = pool["e350_plateau_gate"].fillna(False).astype(bool) & pool["e351_compat_gate"].fillna(False).astype(bool)
    return pool[pool["pool_gate"]].copy().reset_index(drop=True)


def e352_rates() -> pd.DataFrame:
    if not SCENARIOS_IN.exists():
        return pd.DataFrame(columns=["variant", "e352_top1_rate", "e352_top3_rate"])
    scen = pd.read_csv(SCENARIOS_IN)
    total = max(len(scen), 1)
    rows: dict[str, dict[str, float]] = {}
    for rec in scen.to_dict("records"):
        top = str(rec.get("top_variant", ""))
        if top:
            rows.setdefault(top, {"top1": 0.0, "top3": 0.0})["top1"] += 1.0
        top3_raw = str(rec.get("top3_variants", ""))
        normalized = top3_raw.replace("[", "").replace("]", "").replace("'", "").replace(",", "|")
        for token in normalized.split("|"):
            var = token.strip()
            if var:
                rows.setdefault(var, {"top1": 0.0, "top3": 0.0})["top3"] += 1.0
    out = pd.DataFrame(
        [
            {"variant": key, "e352_top1_rate": val["top1"] / total, "e352_top3_rate": val["top3"] / total}
            for key, val in rows.items()
        ]
    )
    return out


def train_predict_world(
    archive: pd.DataFrame,
    pool: pd.DataFrame,
    numeric_cols: list[str],
    cat_cols: list[str],
    train_mask: pd.Series,
    world: str,
    model_name: str,
) -> pd.DataFrame:
    train = archive[train_mask].copy()
    if len(train) < 30 or train["exp_id"].nunique() < 1:
        return pd.DataFrame()
    out = pool[["variant", "basename", "file"]].copy()
    out["world"] = world
    out["model"] = model_name
    for target in TARGET_COMPONENTS:
        y = train[target].astype(float).to_numpy()
        model = make_model(numeric_cols, cat_cols, model_name)
        model.fit(train[numeric_cols + cat_cols], y)
        out[f"pred_{target}"] = model.predict(pool[numeric_cols + cat_cols])
    # Percentile inside the selection pool: the absolute scale of each target is
    # not stable across training worlds, but its ordering is the useful latent.
    out["pred_visibility_pct"] = pct_high(out["pred_y_visibility"])
    out["pred_risk_pct"] = pct_high(out["pred_y_risk_good"])
    out["pred_q1_pct"] = pct_high(out["pred_y_q1_specificity"])
    out["pred_bad_pct"] = pct_high(out["pred_y_bad_margin"])
    out["world_action_score"] = (
        1.45 * out["pred_visibility_pct"]
        + 1.25 * out["pred_risk_pct"]
        + 1.10 * out["pred_q1_pct"]
        + 1.00 * out["pred_bad_pct"]
    ) / 4.80
    out["world_rank"] = out["world_action_score"].rank(ascending=False, method="min")
    return out


def plateau_predictions(archive: pd.DataFrame, pool: pd.DataFrame, numeric_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:
    worlds = {
        "non_e350": ~archive["exp_id"].eq("E350"),
        "pre_plateau": archive["exp_id"].isin(["E347", "E349"]),
        "failure_boundary": archive["exp_id"].isin(["E353", "E354"]),
        "all_archive": pd.Series(True, index=archive.index),
    }
    pred_frames: list[pd.DataFrame] = []
    for world, mask in worlds.items():
        for model_name in ["extratrees"]:
            pred = train_predict_world(archive, pool, numeric_cols, cat_cols, mask, world, model_name)
            if not pred.empty:
                pred_frames.append(pred)
    if not pred_frames:
        raise RuntimeError("No plateau prediction worlds were generated")
    long = pd.concat(pred_frames, ignore_index=True)
    long.to_csv(OUT / "e355_action_health_plateau_predictions_long.csv", index=False)

    agg = (
        long.groupby(["variant", "basename", "file"], as_index=False)
        .agg(
            e355_world_count=("world_action_score", "size"),
            e355_score_mean=("world_action_score", "mean"),
            e355_score_std=("world_action_score", "std"),
            e355_rank_mean=("world_rank", "mean"),
            e355_rank_worst=("world_rank", "max"),
            e355_top1_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 1))),
            e355_top3_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 3))),
            e355_top5_rate=("world_rank", lambda s: float(np.mean(np.asarray(s) <= 5))),
            pred_visibility_mean=("pred_y_visibility", "mean"),
            pred_risk_good_mean=("pred_y_risk_good", "mean"),
            pred_q1_specificity_mean=("pred_y_q1_specificity", "mean"),
            pred_bad_margin_mean=("pred_y_bad_margin", "mean"),
        )
        .reset_index(drop=True)
    )
    rates = e352_rates()
    if len(rates):
        agg = agg.merge(rates, on="variant", how="left")
    else:
        agg["e352_top1_rate"] = np.nan
        agg["e352_top3_rate"] = np.nan
    metric_cols = [
        "variant",
        "basename",
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
        "e351_compat_gate",
    ]
    metric_cols = [c for c in metric_cols if c in pool.columns]
    agg = agg.merge(pool[metric_cols].drop_duplicates("basename"), on=["variant", "basename"], how="left")
    agg["e355_stability_score"] = (
        1.20 * agg["e355_score_mean"].rank(pct=True)
        + 1.00 * (-agg["e355_rank_mean"]).rank(pct=True)
        + 0.85 * agg["e355_top3_rate"]
        + 0.45 * agg["e355_top5_rate"]
        + 0.45 * agg["e352_top3_rate"].fillna(0.0)
        - 0.35 * agg["e355_score_std"].fillna(0.0).rank(pct=True)
    )
    agg = agg.sort_values(["e355_stability_score", "e355_top3_rate", "e355_rank_mean"], ascending=[False, False, True]).reset_index(drop=True)
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
    e351 = pred[pred["variant"].eq("compact_t75_s1.005_s3a0.25")]
    e351_rank = int(e351.index[0] + 1) if len(e351) else -1
    top = pred.iloc[0].copy()
    selected_path: Path | None = None
    decision = "no_new_candidate"
    reason = "E355 does not beat the existing E351 robust-center file with enough independent stability."

    if top["variant"] == "compact_t75_s1.005_s3a0.25":
        decision = "confirm_e351"
        reason = "E355 action-health latent selects the existing E351 robust-center candidate."
    else:
        # A new candidate must be a strong multi-world winner and not merely an
        # action-health model preference that contradicts the prior E352 selector
        # stability audit.
        e351_score = float(e351["e355_stability_score"].iloc[0]) if len(e351) else -np.inf
        improvement = float(top["e355_stability_score"] - e351_score)
        public_risk_ok = float(top.get("public_analog_risk_score", 9.0)) <= 0.04478
        p90_ok = float(top.get("pred_delta_vs_current_p90", 1.0)) <= -5.0e-5
        q1_ok = float(top.get("q1_specificity_margin", 0.0)) >= 0.31
        e352_ok = float(top.get("e352_top3_rate", 0.0)) >= 0.12
        top3_ok = float(top.get("e355_top3_rate", 0.0)) >= 0.50
        rank_ok = float(top.get("e355_rank_worst", 999.0)) <= 12.0
        if improvement >= 0.08 and public_risk_ok and p90_ok and q1_ok and e352_ok and top3_ok and rank_ok:
            selected_path = materialize_selection(top)
            decision = "select_new_uploadsafe"
            reason = "A non-E351 plateau point wins the action-health latent and passes conservative public-free gates."

    row = top.to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "e351_e355_rank": e351_rank,
            "selected_uploadsafe_file": rel(selected_path) if selected_path is not None else "",
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECT_OUT, index=False)
    return out, selected_path


def write_report(archive: pd.DataFrame, diag: pd.DataFrame, pred: pd.DataFrame, selection: pd.DataFrame, selected: Path | None) -> None:
    top_cols = [
        "variant",
        "threshold_frac",
        "scale",
        "s3_alpha",
        "e355_stability_score",
        "e355_score_mean",
        "e355_score_std",
        "e355_rank_mean",
        "e355_rank_worst",
        "e355_top1_rate",
        "e355_top3_rate",
        "e355_top5_rate",
        "e352_top1_rate",
        "e352_top3_rate",
        "pred_delta_vs_current_p90",
        "public_analog_risk_score",
        "q1_specificity_margin",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "e351_robust_score",
    ]
    top_cols = [c for c in top_cols if c in pred.columns]
    sel = selection.iloc[0]
    selected_text = rel(selected) if selected is not None else "none"
    archive_summary = (
        archive.groupby("exp_id", as_index=False)
        .agg(
            rows=("basename", "size"),
            reference_gate_rate=("e355_reference_gate", "mean"),
            visibility_mean=("y_visibility", "mean"),
            risk_good_mean=("y_risk_good", "mean"),
            q1_specificity_mean=("y_q1_specificity", "mean"),
            action_health_mean=("y_action_health", "mean"),
        )
        .sort_values("exp_id")
    )
    lines = [
        "# E355 Action-Health Latent Selector",
        "",
        "## Question",
        "",
        "After E354 rejected the direct E247-support graft, can the hidden action-health state be learned from the candidate archive and used to choose a safer point inside the E350/E351 compact lifestyle-state basin?",
        "",
        "## Method",
        "",
        "- Context view: candidate movement geometry, target movement shares, reference-axis geometry, and high-level recipe descriptors.",
        "- Target representation: p90 visibility, public-analog risk, Q1 lifestyle specificity, and bad-axis margin.",
        "- Anti-collapse check: leave-experiment-out diagnostics plus multiple prediction worlds for the E350 plateau.",
        "- Candidate action: select only inside the existing E350/E351 plateau; no arbitrary new blend or prior tweak.",
        "",
        "## Decision",
        "",
        f"- archive rows with full target representation: `{len(archive)}`",
        f"- selection pool rows: `{len(pred)}`",
        f"- decision: `{sel['decision']}`",
        f"- selected upload-safe file: `{selected_text}`",
        f"- top E355 variant: `{sel['variant']}`",
        f"- E351 E355 rank: `{int(sel['e351_e355_rank'])}`",
        f"- reason: {sel['reason']}",
        "",
        "## Archive Summary",
        "",
        md_table(archive_summary, n=20, floatfmt=".9f"),
        "",
        "## Latent Diagnostics",
        "",
        md_table(diag, n=20, floatfmt=".9f") if len(diag) else "_empty_",
        "",
        "## Top Plateau Predictions",
        "",
        md_table(pred[top_cols], n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if str(sel["decision"]) == "select_new_uploadsafe":
        lines.extend(
            [
                "E355 found a non-E351 plateau point that is preferred by the learned action-health latent.",
                "This is a submission candidate because it remains inside the existing compact lifestyle-state basin and passes conservative local gates.",
            ]
        )
    elif str(sel["decision"]) == "confirm_e351":
        lines.extend(
            [
                "The learned action-health latent selects the same robust-center candidate as E351.",
                "This strengthens E351 as the practical public-free candidate and argues against another local selector tweak.",
            ]
        )
    else:
        lines.extend(
            [
                "The learned action-health latent does not produce a sufficiently stable non-E351 replacement.",
                "This is a useful negative result: the current archive can diagnose action health, but it does not yet create a new action beyond the E351 robust center.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(ARCHIVE_OUT)}`",
            f"- `{rel(DIAG_OUT)}`",
            f"- `{rel(PRED_OUT)}`",
            f"- `{rel(SELECT_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    archive = read_archive()
    numeric_cols, cat_cols = feature_columns(archive)
    diag = latent_diagnostics(archive, numeric_cols, cat_cols)
    pool = load_pool()
    # Align missing feature columns in the pool to archive columns.  The
    # imputer handles missing values; explicit columns keep sklearn schemas
    # identical between train and predict.
    for col in numeric_cols + cat_cols:
        if col not in pool:
            pool[col] = np.nan
    pred = plateau_predictions(archive, pool, numeric_cols, cat_cols)
    selection, selected = select_candidate(pred)
    write_report(archive, diag, pred, selection, selected)
    print(f"archive rows: {len(archive)}")
    print(f"feature cols: {len(numeric_cols) + len(cat_cols)}")
    print(f"selection pool: {len(pred)}")
    print(f"decision: {selection['decision'].iloc[0]}")
    print(f"selected: {rel(selected) if selected is not None else 'none'}")
    print(pred.head(12)[["variant", "e355_stability_score", "e355_rank_mean", "e355_top3_rate", "e352_top3_rate"]].to_string(index=False))
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
