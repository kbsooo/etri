#!/usr/bin/env python3
"""E330: target-residual lifestyle latent.

E328 showed that a broad own-lifestyle latent is real but not predictive.
This experiment narrows the target:

    visible context -> target-specific base-residual state

The teacher is not raw lifelog reconstruction. For each target and blocked
split, it is the residual left after a subject/calendar base model. Masked
lifestyle views then predict that residual under the same blocked split.

Promotion requires three things:
    - target-specific label improvement against the base model;
    - row/subject/dateblock shuffled residual nulls do not reproduce it;
    - any materialized E247 edit is not E323-like.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import (  # noqa: E402
    E247,
    E323,
    build_views,
    clip_prob,
    load_frames,
    load_sub_frame,
    md_table,
    normalize_dates,
    require_aligned,
    safe_id,
    sigmoid,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 330
NULL_REPS = 8
RIDGE_ALPHA = 12.0
MAX_SELECTED = 8
SCALES = [0.20, 0.40, 0.65]
CAP = 0.070
EPS = 1.0e-12

SUMMARY_OUT = OUT / "e330_target_residual_lifestyle_latent_summary.csv"
NULL_OUT = OUT / "e330_target_residual_lifestyle_latent_null_summary.csv"
CANDIDATE_OUT = OUT / "e330_target_residual_lifestyle_latent_candidate_summary.csv"
SCORE_OUT = OUT / "e330_target_residual_lifestyle_latent_candidate_scores.csv"
ANATOMY_OUT = OUT / "e330_target_residual_lifestyle_latent_candidate_anatomy.csv"
REPORT_OUT = OUT / "e330_target_residual_lifestyle_latent_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_spearman(a: np.ndarray, b: np.ndarray) -> float:
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 4 or len(np.unique(np.round(x, 12))) < 2 or len(np.unique(np.round(y, 12))) < 2:
        return 0.0
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else 0.0


def train_mask(df: pd.DataFrame) -> np.ndarray:
    return df["split"].eq("train").to_numpy()


def groups_for(df: pd.DataFrame, split_name: str) -> pd.Series:
    if split_name == "subject":
        return df["subject_id"].astype(str)
    if split_name == "dateblock":
        return df["dateblock_group"].astype(str)
    raise ValueError(split_name)


def base_label_matrix_all(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    def make(df: pd.DataFrame) -> pd.DataFrame:
        pieces: list[pd.Series | pd.DataFrame] = []
        for col in [
            "weekday",
            "is_weekend",
            "subject_order",
            "lifelog_dom",
            "lifelog_month",
            "weekday_sin",
            "weekday_cos",
            "dom_sin",
            "dom_cos",
            "month_sin",
            "month_cos",
        ]:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                pieces.append(pd.to_numeric(df[col], errors="coerce").fillna(0.0).rename(col))
        pieces.append(pd.get_dummies(df["subject_id"].astype(str), prefix="sid", dtype=float))
        return pd.concat(pieces, axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)

    x_train = make(train_df).reset_index(drop=True)
    x_test = make(test_df).reset_index(drop=True)
    x_train, x_test = x_train.align(x_test, join="outer", axis=1, fill_value=0.0)
    return x_train.reset_index(drop=True), x_test.reset_index(drop=True)


def fit_logistic_predict(x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    if len(np.unique(y_train)) < 2:
        return np.full(len(x_pred), float(np.mean(y_train)), dtype=np.float64)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(with_mean=False),
        LogisticRegression(C=0.30, solver="liblinear", max_iter=1400),
    )
    model.fit(x_train, y_train)
    return clip_prob(model.predict_proba(x_pred)[:, 1])


def oof_proba(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(x, y, groups):
        pred[va_idx] = fit_logistic_predict(x.iloc[tr_idx], y[tr_idx], x.iloc[va_idx])
    return clip_prob(pred)


def cv_logloss(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> float:
    pred = oof_proba(x, y, groups)
    return float(log_loss(y, pred, labels=[0, 1]))


def oof_ridge_scalar(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> tuple[np.ndarray, np.ndarray, float]:
    x = x.reset_index(drop=True)
    y = np.asarray(y, dtype=np.float64)
    pred = np.zeros(len(y), dtype=np.float64)
    if x.shape[1] == 0:
        pred[:] = float(np.mean(y))
        return pred, pred.copy(), 0.0
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(x, y, groups):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
        model.fit(x.iloc[tr_idx], y[tr_idx])
        pred[va_idx] = model.predict(x.iloc[va_idx])
    full = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
    full.fit(x, y)
    pred_full = np.asarray(full.predict(x), dtype=np.float64)
    try:
        r2 = float(r2_score(y, pred))
    except ValueError:
        r2 = 0.0
    return pred, pred_full, r2


def fit_ridge_full_predict(x_train: pd.DataFrame, y_train: np.ndarray, x_test: pd.DataFrame) -> np.ndarray:
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
    model.fit(x_train.reset_index(drop=True), np.asarray(y_train, dtype=np.float64))
    return np.asarray(model.predict(x_test.reset_index(drop=True)), dtype=np.float64)


def shuffled_feature(values: np.ndarray, mode: str, groups: pd.Series, rng: np.random.Generator) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if mode == "row":
        return arr[rng.permutation(len(arr))]
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e330_targetresid_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def score_paths(paths: list[Path]) -> pd.DataFrame:
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path], base: pd.DataFrame) -> pd.DataFrame:
    current = logit(base[TARGETS].to_numpy(dtype=np.float64))
    e323 = logit(load_sub_frame(E323, base[KEYS])[TARGETS].to_numpy(dtype=np.float64))
    bad = e323 - current
    rows: list[dict[str, object]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        move = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current
        denom = float(np.linalg.norm(move) * np.linalg.norm(bad) + EPS)
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - base[TARGETS].to_numpy(dtype=np.float64)))),
                "cos_with_e323_bad_delta": float(np.sum(move * bad) / denom) if denom else 0.0,
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad_delta", "l1_ratio_to_e323_delta", "basename"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def make_candidate_paths(
    selected: pd.DataFrame,
    state: pd.DataFrame,
    base_x_train: pd.DataFrame,
    base_x_test: pd.DataFrame,
    pred_store: dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]],
) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    train = state[state["split"].eq("train")].reset_index(drop=True)
    test = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    base = load_sub_frame(E247, test[KEYS])
    logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    paths: list[Path] = []
    rows: list[dict[str, object]] = []

    for _, rec in selected.head(MAX_SELECTED).iterrows():
        target = str(rec["target"])
        view_id = str(rec["view_id"])
        split_name = str(rec["split"])
        key = (target, view_id, split_name)
        if key not in pred_store:
            continue
        pred_train, pred_test = pred_store[key]
        y = train[target].astype(int).to_numpy()
        target_idx = TARGETS.index(target)
        x_aug_train = pd.concat(
            [base_x_train.reset_index(drop=True), pd.Series(pred_train, name="target_resid_state")],
            axis=1,
        )
        x_aug_test = pd.concat(
            [base_x_test.reset_index(drop=True), pd.Series(pred_test, name="target_resid_state")],
            axis=1,
        )
        p_base = fit_logistic_predict(base_x_train, y, base_x_test)
        p_aug = fit_logistic_predict(x_aug_train, y, x_aug_test)
        raw_delta = np.clip(logit(p_aug) - logit(p_base), -CAP, CAP)
        if np.nanstd(raw_delta) < 1.0e-12:
            continue
        for scale in SCALES:
            cand_logits = logits.copy()
            cand_logits[:, target_idx] += scale * raw_delta
            candidate_id = f"{target}_{view_id}_{split_name}_s{str(scale).replace('.', 'p')}"
            path = write_submission(base, cand_logits, candidate_id)
            paths.append(path)
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "file": rel(path),
                    "basename": path.name,
                    "target": target,
                    "view_id": view_id,
                    "split": split_name,
                    "scale": scale,
                    "source_actual_delta": float(rec["actual_delta"]),
                    "source_dominance": float(rec["dominance"]),
                    "source_placebo_adjusted": float(rec["placebo_adjusted_vs_median"]),
                    "changed_rows": int((np.abs(raw_delta) > 1.0e-12).sum()),
                    "changed_cells": int((np.abs(raw_delta) > 1.0e-12).sum()),
                    "mean_abs_logit_move": float(np.mean(np.abs(scale * raw_delta))),
                    "max_abs_logit_move": float(np.max(np.abs(scale * raw_delta))),
                }
            )

    # Also try one tiny combo if several targets survive. This is still local-only.
    combo = selected.head(3)
    if len(combo) >= 2:
        combo_logits = logits.copy()
        combo_parts = []
        for _, rec in combo.iterrows():
            target = str(rec["target"])
            key = (target, str(rec["view_id"]), str(rec["split"]))
            if key not in pred_store:
                continue
            pred_train, pred_test = pred_store[key]
            y = train[target].astype(int).to_numpy()
            target_idx = TARGETS.index(target)
            x_aug_train = pd.concat([base_x_train.reset_index(drop=True), pd.Series(pred_train, name="target_resid_state")], axis=1)
            x_aug_test = pd.concat([base_x_test.reset_index(drop=True), pd.Series(pred_test, name="target_resid_state")], axis=1)
            p_base = fit_logistic_predict(base_x_train, y, base_x_test)
            p_aug = fit_logistic_predict(x_aug_train, y, x_aug_test)
            raw_delta = np.clip(logit(p_aug) - logit(p_base), -CAP, CAP)
            combo_logits[:, target_idx] += 0.30 * raw_delta
            combo_parts.append(f"{target}:{rec['view_id']}:{rec['split']}")
        if combo_parts:
            path = write_submission(base, combo_logits, "combo_top_target_resid_s0p30")
            paths.append(path)
            move = combo_logits - logits
            rows.append(
                {
                    "candidate_id": "combo_top_target_resid_s0p30",
                    "file": rel(path),
                    "basename": path.name,
                    "target": ",".join(sorted(set(str(t) for t in combo["target"]))),
                    "view_id": ";".join(combo_parts),
                    "split": "combo",
                    "scale": 0.30,
                    "source_actual_delta": float(combo["actual_delta"].mean()),
                    "source_dominance": float(combo["dominance"].mean()),
                    "source_placebo_adjusted": float(combo["placebo_adjusted_vs_median"].mean()),
                    "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                    "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                    "mean_abs_logit_move": float(np.mean(np.abs(move))),
                    "max_abs_logit_move": float(np.max(np.abs(move))),
                }
            )

    cand = pd.DataFrame(rows)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, paths, base


def write_report(
    summary: pd.DataFrame,
    nulls: pd.DataFrame,
    selected: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current.get("promotion_decision", pd.Series(dtype=str)).eq("promote_candidate")] if len(non_current) else pd.DataFrame()
    e323_safe = anatomy[anatomy["cos_with_e323_bad_delta"] <= 0.05] if len(anatomy) else pd.DataFrame()
    safe_promoted = promoted[promoted["basename"].isin(set(e323_safe["basename"]))] if len(promoted) and len(e323_safe) else pd.DataFrame()
    lines = [
        "# E330 Target-Residual Lifestyle Latent",
        "",
        "## Question",
        "",
        "After E328 rejected a broad lifestyle latent, can lifestyle context predict target-specific base-residual states under blocked stress?",
        "",
        "## Construction",
        "",
        "- Teacher: per-target residual after a subject/calendar base model under the same blocked split.",
        "- Context: masked lifestyle views from family JEPA features, story bundle, raw day features, and combined views.",
        "- Student: Ridge predicts the residual state OOF by subject or dateblock.",
        "- Evaluation: label logloss improvement versus base, plus row/subject/dateblock shuffled residual-state nulls.",
        "",
        "## Top Residual-State Rows",
        "",
        md_table(summary.sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]), n=30, floatfmt=".9f"),
        "",
        "## Selected Local Gates",
        "",
        md_table(selected, n=20, floatfmt=".9f"),
        "",
        "## Null Summary",
        "",
        md_table(nulls.sort_values(["target", "view_id", "split", "mode", "rep"]).head(80), n=80, floatfmt=".9f"),
        "",
        "## Candidate Probes",
        "",
        md_table(candidates, n=30, floatfmt=".9f"),
        "",
        "## Public-Free Selector Scores",
        "",
    ]
    if len(non_current):
        cols = [
            "basename",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        lines.append(md_table(non_current[cols], n=40, floatfmt=".9f"))
    else:
        lines.append("_no candidates_")
    lines.extend(["", "## E323-Negative Anatomy", ""])
    lines.append(md_table(anatomy, n=40, floatfmt=".9f") if len(anatomy) else "_no candidates_")
    lines.extend(["", "## Decision", ""])
    if len(safe_promoted):
        best = safe_promoted.iloc[0]
        lines.append(
            f"`{best['basename']}` clears the public-free selector and is E323-negative by movement cosine. Treat it as the next information-rich candidate only after a fresh matched-null movement stress."
        )
    elif int(summary["gate"].sum()) == 0:
        lines.append(
            "No target-residual lifestyle state survived label and null gates. This rejects the simple target-specific residual latent as a direct route."
        )
    elif not len(non_current):
        lines.append(
            "Some target-residual states survived local gates, but no materialized candidate was created. Use the surviving rows as diagnostics only."
        )
    else:
        lines.append(
            "Target-specific residual states exist locally, but their E247 materializations are not submission-grade under the public-free selector and E323-negative anatomy check."
        )
    lines.extend(
        [
            "",
            f"- gated residual-state rows: `{int(summary['gate'].sum())}`",
            f"- generated candidates: `{len(candidates)}`",
            f"- selector-promoted candidates: `{int(non_current['strict_promote_gate'].sum()) if len(non_current) else 0}`",
            f"- E323-negative candidates: `{len(e323_safe)}`",
            "",
            "## Files",
            "",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{NULL_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    mask = train_mask(state)
    train = state.loc[mask].reset_index(drop=True)
    test = state.loc[~mask].sort_values(KEYS).reset_index(drop=True)

    for name, view in views.items():
        require_aligned(state, normalize_dates(pd.concat([state[KEYS], view], axis=1)), f"view_{name}")

    base_x_train, base_x_test = base_label_matrix_all(train, test)
    view_ids = ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]
    train_views = {k: v.loc[mask].reset_index(drop=True) for k, v in views.items() if k in view_ids}
    test_views = {k: v.loc[~mask].reset_index(drop=True) for k, v in views.items() if k in view_ids}

    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    pred_store: dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]] = {}
    for split_name in ["subject", "dateblock"]:
        groups = groups_for(train, split_name).reset_index(drop=True)
        null_groups = {
            "row": groups,
            "subject": groups_for(train, "subject").reset_index(drop=True),
            "dateblock": groups_for(train, "dateblock").reset_index(drop=True),
        }
        for target in TARGETS:
            y = train[target].astype(int).to_numpy()
            base_oof = oof_proba(base_x_train, y, groups)
            teacher = y.astype(float) - base_oof
            base_loss = cv_logloss(base_x_train, y, groups)
            for view_id in view_ids:
                x_view_train = train_views[view_id]
                x_view_test = test_views[view_id]
                pred_oof, _pred_full_train, r2 = oof_ridge_scalar(x_view_train, teacher, groups)
                pred_test = fit_ridge_full_predict(x_view_train, teacher, x_view_test)
                pred_store[(target, view_id, split_name)] = (pred_oof, pred_test)
                feature = pd.Series(pred_oof, name="target_resid_state")
                x_aug = pd.concat([base_x_train.reset_index(drop=True), feature], axis=1)
                aug_loss = cv_logloss(x_aug, y, groups)
                actual_delta = float(aug_loss - base_loss)
                null_vals = []
                rng = np.random.default_rng(stable_seed("e330null", target, view_id, split_name))
                for mode, mgroups in null_groups.items():
                    for rep in range(NULL_REPS):
                        shuf = shuffled_feature(pred_oof, mode, mgroups, rng)
                        nx = pd.concat([base_x_train.reset_index(drop=True), pd.Series(shuf, name="target_resid_state")], axis=1)
                        null_delta = float(cv_logloss(nx, y, groups) - base_loss)
                        null_vals.append(null_delta)
                        null_rows.append(
                            {
                                "target": target,
                                "view_id": view_id,
                                "split": split_name,
                                "mode": mode,
                                "rep": rep,
                                "null_delta": null_delta,
                            }
                        )
                null_arr = np.asarray(null_vals, dtype=np.float64)
                dominance = float(np.mean(actual_delta < null_arr))
                placebo_adjusted = actual_delta - float(np.median(null_arr))
                rows.append(
                    {
                        "target": target,
                        "view_id": view_id,
                        "split": split_name,
                        "context_cols": int(x_view_train.shape[1]),
                        "teacher_resid_std": float(np.std(teacher)),
                        "student_oof_r2": r2,
                        "student_spearman": safe_spearman(pred_oof, teacher),
                        "base_loss": base_loss,
                        "aug_loss": aug_loss,
                        "actual_delta": actual_delta,
                        "null_best": float(np.min(null_arr)),
                        "null_median": float(np.median(null_arr)),
                        "null_q20": float(np.quantile(null_arr, 0.20)),
                        "dominance": dominance,
                        "placebo_adjusted_vs_median": placebo_adjusted,
                        "gate": bool(actual_delta < -0.0005 and dominance >= 0.85 and placebo_adjusted < -0.00025),
                    }
                )

    summary = pd.DataFrame(rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    selected = summary[summary["gate"]].copy()
    if len(selected) == 0:
        selected = summary[(summary["actual_delta"] < 0.0) & (summary["dominance"] >= 0.75)].head(MAX_SELECTED).copy()
    else:
        selected = selected.head(MAX_SELECTED).copy()

    candidates, paths, base = make_candidate_paths(selected, state, base_x_train, base_x_test, pred_store)
    if paths:
        scores = score_paths(paths)
        anatomy = candidate_anatomy(paths, base)
    else:
        scores = pd.DataFrame()
        anatomy = pd.DataFrame()

    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(summary, nulls, selected, candidates, scores, anatomy)

    print(REPORT_OUT)
    print("[top summary]")
    print(summary.head(20).round(9).to_string(index=False))
    if len(scores):
        print("[scores]")
        print(scores[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].head(20).round(9).to_string(index=False))
    if len(anatomy):
        print("[anatomy]")
        print(anatomy.head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
