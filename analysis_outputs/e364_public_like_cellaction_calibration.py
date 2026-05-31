#!/usr/bin/env python3
"""E364: public-like calibration stress for E363 cell-action candidates.

Question:
    E363 found a wide local basin around the E362 hidden lifestyle-state action.
    Is the selected cell action public-like, or is the E363 gate too permissive?

JEPA/data2vec translation:
    context = candidate movement anatomy, known public-good/bad movement axes,
              and row-level own-latent lifestyle exposure
    target  = known public-survival delta relative to E247
    action  = keep E363, or replace it only if another E363-neighborhood action
              is both locally robust and more public-like under fixed sensors

The public LB observations are used as a small diagnostic sensor.  This does
not tune a numeric public target and does not create arbitrary blends.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
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
from e357_public_survival_contrast_latent import (  # noqa: E402
    KEY,
    TARGETS,
    add_axis_features,
    align_delta,
    feature_columns as movement_feature_columns,
    load_known,
    locate,
    logit_frame,
    make_axes,
    movement_features,
    safe_spearman,
)
from e359_rowplacement_action_health_probe import clip_prob  # noqa: E402


RNG_SEED = 20260531 + 364
ANCHOR_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
UPLOAD_PREFIX = "submission_e364_publiclike_cellaction"

E363_SCORES_IN = OUT / "e363_cell_action_robustness_scores.csv"
E363_SELECTION_IN = OUT / "e363_cell_action_robustness_selection.csv"

KNOWN_OUT = OUT / "e364_public_like_cellaction_known.csv"
LOOCV_OUT = OUT / "e364_public_like_cellaction_loocv.csv"
LOO_PRED_OUT = OUT / "e364_public_like_cellaction_loo_predictions.csv"
SCORES_OUT = OUT / "e364_public_like_cellaction_scores.csv"
SELECTION_OUT = OUT / "e364_public_like_cellaction_selection.csv"
REPORT_OUT = OUT / "e364_public_like_cellaction_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    cols = [c for c in KEY + TARGETS if c in frame.columns]
    payload = pd.util.hash_pandas_object(frame[cols], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def make_model(model_name: str):
    if model_name == "ridge_10":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if model_name == "ridge_1":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if model_name == "knn3":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=3, weights="distance"))
    if model_name == "extratrees":
        return ExtraTreesRegressor(
            n_estimators=160,
            min_samples_leaf=2,
            max_features=0.70,
            random_state=RNG_SEED,
            n_jobs=1,
        )
    raise ValueError(model_name)


def good_low(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return (-v.fillna(v.median())).rank(pct=True)


def good_high(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return v.fillna(v.median()).rank(pct=True)


def loocv_public_sensor(known: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    x = train[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        pred = np.full(len(train), np.nan, dtype=np.float64)
        for tr_idx, va_idx in LeaveOneOut().split(x):
            model = make_model(model_name)
            model.fit(x.iloc[tr_idx], y[tr_idx])
            pred[va_idx] = float(model.predict(x.iloc[va_idx])[0])
        rows.append(
            {
                "model": model_name,
                "known_rows": int(len(train)),
                "feature_count": int(len(cols)),
                "loo_spearman": safe_spearman(y, pred),
                "loo_mae": float(np.mean(np.abs(pred - y))),
                "pred_std": float(np.std(pred)),
            }
        )
        for i, rec in train.iterrows():
            pred_rows.append(
                {
                    "model": model_name,
                    "basename": rec["basename"],
                    "public_lb": rec["public_lb"],
                    "delta_vs_e247": rec["delta_vs_e247"],
                    "loo_pred_delta": pred[i],
                    "abs_error": abs(float(pred[i] - y[i])),
                }
            )
    diag = pd.DataFrame(rows).sort_values(["loo_spearman", "loo_mae"], ascending=[False, True]).reset_index(drop=True)
    pred_frame = pd.DataFrame(pred_rows)
    diag.to_csv(LOOCV_OUT, index=False)
    pred_frame.to_csv(LOO_PRED_OUT, index=False)
    return diag, pred_frame


def public_axis_summaries(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    bad_tokens = ("bad", "e216", "e267", "e323", "ordinal", "final9", "broad_stage2")
    good_tokens = ("e95", "e101", "mixmin", "e176", "old_frontier")
    pos_cols = [c for c in out.columns if c.startswith("posproj_")]
    cos_cols = [c for c in out.columns if c.startswith("cos_")]
    bad_pos = [c for c in pos_cols if any(tok in c for tok in bad_tokens)]
    good_pos = [c for c in pos_cols if any(tok in c for tok in good_tokens)]
    bad_cos = [c for c in cos_cols if any(tok in c for tok in bad_tokens)]
    good_cos = [c for c in cos_cols if any(tok in c for tok in good_tokens)]
    out["public_bad_axis_sum"] = out[bad_pos].sum(axis=1) if bad_pos else 0.0
    out["public_bad_axis_max"] = out[bad_pos].max(axis=1) if bad_pos else 0.0
    out["public_good_axis_sum"] = out[good_pos].sum(axis=1) if good_pos else 0.0
    out["public_bad_good_gap"] = out["public_bad_axis_sum"] - out["public_good_axis_sum"]
    out["public_bad_cos_max"] = out[bad_cos].max(axis=1) if bad_cos else 0.0
    out["public_good_cos_max"] = out[good_cos].max(axis=1) if good_cos else 0.0
    return out


def score_e363_pool(anchor: pd.DataFrame, known: pd.DataFrame, axes: dict[str, np.ndarray], cols: list[str]) -> pd.DataFrame:
    raw = pd.read_csv(E363_SCORES_IN).replace([np.inf, -np.inf], np.nan)
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for rec in raw.to_dict("records"):
        path = locate(rec.get("file"))
        if path is None or str(path) in seen:
            continue
        seen.add(str(path))
        delta = align_delta(path, anchor)
        deltas[path.name] = delta
        rows.append(
            {
                "variant": rec.get("variant", path.stem),
                "family": rec.get("family", ""),
                "file": rel(path),
                "basename": path.name,
                **movement_features(delta),
            }
        )
    movement = pd.DataFrame(rows)
    movement = add_axis_features(movement, deltas, axes)

    blocked = set(movement.columns) - {"variant", "family", "file", "basename"}
    pool = raw.drop(columns=[c for c in blocked if c in raw.columns], errors="ignore").merge(
        movement,
        on=["variant", "family", "file", "basename"],
        how="inner",
    )
    pool = public_axis_summaries(pool)

    train = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    x = train[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    pred_cols: list[str] = []
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name)
        model.fit(x, y)
        col = f"e364_pred_public_delta_{model_name}"
        pool[col] = np.asarray(model.predict(xp), dtype=np.float64)
        pred_cols.append(col)
    pool["e364_pred_public_delta_mean"] = pool[pred_cols].mean(axis=1)
    pool["e364_pred_public_delta_std"] = pool[pred_cols].std(axis=1).fillna(0.0)
    pool["e364_pred_public_delta_max"] = pool[pred_cols].max(axis=1)

    if "rowstate_bad_minus_good_exposure" not in pool:
        pool["rowstate_bad_minus_good_exposure"] = 0.0
    if "rowstate_pred_public_loss_mean" not in pool:
        pool["rowstate_pred_public_loss_mean"] = 0.0
    if "e363_robust_score" not in pool:
        pool["e363_robust_score"] = 0.0
    if "pred_delta_vs_current_p90" not in pool:
        pool["pred_delta_vs_current_p90"] = 0.0
    if "e363_submission_gate" not in pool:
        pool["e363_submission_gate"] = False

    pool["e364_public_like_score"] = (
        1.15 * good_low(pool["e364_pred_public_delta_mean"])
        + 0.75 * good_low(pool["e364_pred_public_delta_std"])
        + 0.95 * good_low(pool["public_bad_axis_sum"])
        + 0.55 * good_low(pool["public_bad_good_gap"])
        + 0.90 * good_low(pool["rowstate_pred_public_loss_mean"])
        + 0.80 * good_low(pool["rowstate_bad_minus_good_exposure"])
        + 0.90 * good_high(pool["e363_robust_score"])
        + 0.55 * good_low(pool["pred_delta_vs_current_p90"])
    )
    pool = pool.sort_values("e364_public_like_score", ascending=False).reset_index(drop=True)
    pool.to_csv(SCORES_OUT, index=False)
    return pool


def copy_uploadsafe(path: Path, variant: str) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    frame = pd.read_csv(path)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(variant, 70)}_{short_hash(frame)}_uploadsafe.csv"
    frame.to_csv(out, index=False)
    return out


def select_candidate(pool: pd.DataFrame) -> pd.DataFrame:
    e363_sel = pd.read_csv(E363_SELECTION_IN).iloc[0]
    selected_variant = str(e363_sel["variant"])
    selected_file = str(e363_sel["file"]) if "file" in e363_sel else str(e363_sel.get("source_path", ""))
    base = pool[pool["variant"].astype(str).eq(selected_variant)].head(1)
    if base.empty and selected_file:
        base = pool[pool["file"].astype(str).eq(selected_file)].head(1)
    if base.empty:
        base = pool.head(1)
    base_row = base.iloc[0]

    pass_pool = pool[pool["e363_submission_gate"].fillna(False).astype(bool)].copy()
    if pass_pool.empty:
        pass_pool = pool.copy()

    # This gate is relative to the already selected E363 point.  A replacement
    # must not buy score by moving closer to known bad public axes or by raising
    # row-state public-risk.  The margins are deliberately loose enough to keep
    # the sensor diagnostic rather than hard-coding the selected row.
    pass_pool["e364_public_like_gate"] = (
        (pass_pool["e364_pred_public_delta_mean"] <= float(base_row["e364_pred_public_delta_mean"]) + 5.0e-5)
        & (pass_pool["e364_pred_public_delta_std"] <= float(base_row["e364_pred_public_delta_std"]) + 2.5e-4)
        & (pass_pool["public_bad_axis_sum"] <= float(base_row["public_bad_axis_sum"]) + 0.12)
        & (pass_pool["rowstate_pred_public_loss_mean"] <= float(base_row["rowstate_pred_public_loss_mean"]) + 2.5e-4)
        & (pass_pool["rowstate_bad_minus_good_exposure"] <= float(base_row["rowstate_bad_minus_good_exposure"]) + 0.035)
        & (pass_pool["e363_robust_score"] >= max(0.50, float(base_row["e363_robust_score"]) - 0.08))
    )
    gated = pass_pool[pass_pool["e364_public_like_gate"]].copy()
    if gated.empty:
        top = base_row.copy()
        decision = "keep_e363_selected"
        reason = "No E363 candidate improved the public-like sensor while preserving E363 row-state and bad-axis margins."
    else:
        top = gated.sort_values("e364_public_like_score", ascending=False).iloc[0].copy()
        score_gain = float(top["e364_public_like_score"] - base_row["e364_public_like_score"])
        same_family = str(top.get("family", "")) == str(base_row.get("family", ""))
        if str(top["variant"]) == selected_variant:
            decision = "keep_e363_selected"
            reason = "The original E363 selected action remains the strongest public-like candidate after known-public calibration."
        elif same_family or score_gain >= 0.25:
            decision = "select_e364_public_like_replacement"
            reason = (
                "A candidate inside the E363 basin keeps the local E363 gate and has lower known-public-like risk "
                "under movement-axis plus row-state sensors."
            )
        else:
            top = base_row.copy()
            decision = "keep_e363_selected"
            reason = (
                "A different family ranked slightly higher, but the gain was not large enough to override the "
                "source-law preservation prior from E363."
            )

    src = locate(top["file"])
    if src is None:
        raise FileNotFoundError(str(top["file"]))
    upload = copy_uploadsafe(src, str(top["variant"]))
    top = top.to_dict()
    top.update(
        {
            "decision": decision,
            "reason": reason,
            "e363_selected_variant": selected_variant,
            "e363_selected_e364_score": float(base_row["e364_public_like_score"]),
            "e363_selected_pred_public_delta_mean": float(base_row["e364_pred_public_delta_mean"]),
            "selected_uploadsafe_file": rel(upload),
        }
    )
    out = pd.DataFrame([top])
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(known: pd.DataFrame, diag: pd.DataFrame, pool: pd.DataFrame, selected: pd.DataFrame, feature_cols: list[str]) -> None:
    sel = selected.iloc[0]
    top_cols = [
        "variant",
        "family",
        "e364_public_like_score",
        "e364_pred_public_delta_mean",
        "e364_pred_public_delta_std",
        "public_bad_axis_sum",
        "public_bad_good_gap",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "e363_robust_score",
        "pred_delta_vs_current_p90",
        "e363_submission_gate",
        "file",
    ]
    known_cols = [
        "basename",
        "public_lb",
        "delta_vs_e247",
        "available",
        "cell_l1",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S3",
        "public_bad_axis_sum",
        "public_good_axis_sum",
    ]
    family = (
        pool.groupby("family")
        .agg(
            n=("family", "size"),
            e363_submit=("e363_submission_gate", "sum"),
            e364_score_mean=("e364_public_like_score", "mean"),
            pred_public_mean=("e364_pred_public_delta_mean", "mean"),
            bad_axis_mean=("public_bad_axis_sum", "mean"),
            rowstate_loss_mean=("rowstate_pred_public_loss_mean", "mean"),
        )
        .sort_values("e364_score_mean", ascending=False)
        .reset_index()
    )
    lines = [
        "# E364 Public-Like Cell-Action Calibration",
        "",
        "## Question",
        "",
        "E363 found many locally robust E362-neighborhood cell actions. Which of them still looks sane when viewed through fixed known-public movement axes and hidden lifestyle row-state exposure?",
        "",
        "## Method",
        "",
        "- Anchor: E247 public-best submission.",
        "- Context view: output logit movement anatomy, projections onto known public-good/bad axes, and E363 row-state/story latent exposure.",
        "- Target view: known public delta versus E247 for available public-observed submissions.",
        "- Anti-collapse: leave-one-public-file-out public sensor; candidate replacement is allowed only if it clears E363's own local gate and does not increase bad-axis or row-state risk beyond E363-selected margins.",
        "",
        "## Inputs",
        "",
        f"- known public rows available locally: `{int(known['available'].fillna(False).sum())}`",
        f"- public-sensor feature columns: `{len(feature_cols)}`",
        f"- E363 candidate rows scored: `{len(pool)}`",
        f"- E363 submission-gate rows: `{int(pool['e363_submission_gate'].fillna(False).sum())}`",
        "",
        "## Public Sensor LOO",
        "",
        md_table(diag, n=10, floatfmt=".9f"),
        "",
        "## Known Public Axis Summary",
        "",
        md_table(known[[c for c in known_cols if c in known.columns]].sort_values("public_lb"), n=20, floatfmt=".9f"),
        "",
        "## E363 Family Summary",
        "",
        md_table(family, n=20, floatfmt=".9f"),
        "",
        "## Top E363 Public-Like Candidates",
        "",
        md_table(pool[[c for c in top_cols if c in pool.columns]].head(30), n=30, floatfmt=".9f"),
        "",
        "## Decision",
        "",
        md_table(
            selected[
                [
                    "decision",
                    "variant",
                    "family",
                    "selected_uploadsafe_file",
                    "e364_public_like_score",
                    "e363_selected_e364_score",
                    "e364_pred_public_delta_mean",
                    "e363_selected_pred_public_delta_mean",
                    "public_bad_axis_sum",
                    "rowstate_bad_minus_good_exposure",
                    "reason",
                ]
            ],
            n=5,
            floatfmt=".9f",
        ),
        "",
        "## Interpretation",
        "",
        "- If E364 keeps the E363 selected point, E363's target-scale source law is not contradicted by known public axes; the next useful experiment should seek a genuinely new row-state/action law, not a nearby public-risk rerank.",
        "- If E364 selects another same-family point, the hidden lifestyle action appears to have a local basin but needs calibrated amplitude.",
        "- If E364 selects a different family only by a large margin, E363's source-law preservation prior weakens and donor-graft structure becomes a credible next submission branch.",
        "",
        "## Files",
        "",
        f"- `{rel(KNOWN_OUT)}`",
        f"- `{rel(LOOCV_OUT)}`",
        f"- `{rel(LOO_PRED_OUT)}`",
        f"- `{rel(SCORES_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    anchor = logit_frame(OUT / ANCHOR_FILE)
    known, known_deltas, _ = load_known(anchor)
    axes = make_axes(known_deltas)
    known = add_axis_features(known, known_deltas, axes)
    known = public_axis_summaries(known)
    known.to_csv(KNOWN_OUT, index=False)

    feature_cols = movement_feature_columns(known)
    diag, _ = loocv_public_sensor(known, feature_cols)
    pool = score_e363_pool(anchor, known, axes, feature_cols)
    selected = select_candidate(pool)
    write_report(known, diag, pool, selected, feature_cols)

    sel = selected.iloc[0]
    print(f"known_available={int(known['available'].fillna(False).sum())} feature_cols={len(feature_cols)} pool={len(pool)}")
    print(diag.round(9).to_string(index=False))
    print(
        selected[
            [
                "decision",
                "variant",
                "family",
                "e364_public_like_score",
                "e363_selected_e364_score",
                "e364_pred_public_delta_mean",
                "public_bad_axis_sum",
                "rowstate_bad_minus_good_exposure",
                "selected_uploadsafe_file",
            ]
        ].round(9).to_string(index=False)
    )
    print(f"reason={sel['reason']}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
