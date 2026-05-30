#!/usr/bin/env python3
"""E274: target-specific human diary energy audit.

E273 rejected broad diary-state feature dumping. This experiment keeps the
part that survived: target-specific JEPA residual/prediction energies.

Question:
Can a small set of diary energy axes pass subject/dateblock local stress and
produce a public-free-promotable candidate against the current E247 frontier?

No public LB is used. Generated submissions are local candidates only; they
must pass the E272 promotion rule before being recommended.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    build_features,
    evaluate_models,
    movement_anatomy,
    score_candidates,
    selected_models,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


FEATURE_PATH = OUT / "e273_human_diary_state_jepa_audit_features.parquet"
SCAN_OUT = OUT / "e274_target_specific_diary_energy_scan.csv"
AXIS_OUT = OUT / "e274_target_specific_diary_energy_selected_axes.csv"
SCORE_OUT = OUT / "e274_target_specific_diary_energy_candidate_scores.csv"
ANATOMY_OUT = OUT / "e274_target_specific_diary_energy_candidate_anatomy.csv"
CELLS_OUT = OUT / "e274_target_specific_diary_energy_selected_cells.csv"
REPORT_OUT = OUT / "e274_target_specific_diary_energy_report.md"

RNG = 20260531 + 274
EPS = 1.0e-6


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def state_feature_cols(df: pd.DataFrame) -> list[str]:
    meta = set(KEYS + TARGETS + [
        "split",
        "dateblock_group",
        "subject_order",
        "weekday",
        "is_weekend",
        "lifelog_dom",
        "lifelog_month",
        "weekday_sin",
        "weekday_cos",
        "dom_sin",
        "dom_cos",
        "month_sin",
        "month_cos",
    ])
    cols: list[str] = []
    for col in df.columns:
        if col in meta or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        if col.startswith("diary_state_k"):
            continue
        if (
            col.endswith("_energy")
            or "_pc" in col
            or col.startswith("jepa_resid_")
            or col.startswith("jepa_prednorm_")
            or col.startswith("diary_state_pc")
            or col == "diary_state_energy"
        ):
            cols.append(col)
    return sorted(set(cols))


def base_matrix(frame: pd.DataFrame, columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    base_cols = ["weekday_sin", "weekday_cos", "is_weekend", "subject_order", "dom_sin", "dom_cos", "month_sin", "month_cos"]
    base = frame[base_cols].astype(float).reset_index(drop=True)
    dummies = pd.get_dummies(frame["subject_id"].astype(str), prefix="subj", dtype=float).reset_index(drop=True)
    out = pd.concat([base, dummies], axis=1)
    if columns is not None:
        out = out.reindex(columns=columns, fill_value=0.0)
        return out, columns
    return out, out.columns.tolist()


def fit_predict(x_tr: pd.DataFrame | np.ndarray, y_tr: np.ndarray, x_va: pd.DataFrame | np.ndarray) -> np.ndarray:
    y_tr = np.asarray(y_tr, dtype=int)
    if len(np.unique(y_tr)) < 2:
        p = float(np.clip(np.mean(y_tr), 0.02, 0.98))
        return np.full(len(x_va), p, dtype=np.float64)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(with_mean=False),
        LogisticRegression(C=0.18, solver="liblinear", max_iter=1000),
    )
    model.fit(x_tr, y_tr)
    return model.predict_proba(x_va)[:, 1]


def robust_z(train: pd.Series, values: pd.Series) -> tuple[np.ndarray, float, float]:
    tr = pd.to_numeric(train, errors="coerce").astype(float)
    val = pd.to_numeric(values, errors="coerce").astype(float)
    med = float(np.nanmedian(tr))
    q75 = float(np.nanpercentile(tr, 75))
    q25 = float(np.nanpercentile(tr, 25))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(np.nanstd(tr))
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = 1.0
    z = ((val - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0).clip(-8.0, 8.0)
    return z.to_numpy(dtype=np.float64), med, scale


def fold_scores_for_axis(train: pd.DataFrame, target: str, feature: str, group_col: str) -> dict[str, float]:
    groups = train[group_col].astype(str).to_numpy()
    uniq = np.unique(groups)
    if len(uniq) < 2:
        return {"delta": np.nan, "win_rate": np.nan, "folds": 0}
    cv = GroupKFold(n_splits=min(5, len(uniq)))
    y = train[target].to_numpy(dtype=int)
    pred_base = np.zeros(len(train), dtype=np.float64)
    pred_feat = np.zeros(len(train), dtype=np.float64)
    fold_deltas: list[float] = []
    for tr_idx, va_idx in cv.split(train, y, groups=groups):
        tr = train.iloc[tr_idx]
        va = train.iloc[va_idx]
        xb_tr, base_cols = base_matrix(tr)
        xb_va, _ = base_matrix(va, base_cols)
        z_tr, med, scale = robust_z(tr[feature], tr[feature])
        z_va = ((pd.to_numeric(va[feature], errors="coerce").astype(float) - med) / scale).replace(
            [np.inf, -np.inf], 0.0
        ).fillna(0.0).clip(-8.0, 8.0).to_numpy(dtype=np.float64)
        xf_tr = xb_tr.copy()
        xf_va = xb_va.copy()
        xf_tr[feature] = z_tr
        xf_va[feature] = z_va
        pb = fit_predict(xb_tr, tr[target].to_numpy(dtype=int), xb_va)
        pf = fit_predict(xf_tr, tr[target].to_numpy(dtype=int), xf_va)
        pred_base[va_idx] = pb
        pred_feat[va_idx] = pf
        fold_deltas.append(
            log_loss(
                va[target].to_numpy(dtype=int),
                clip_prob(pf),
                labels=[0, 1],
            )
            - log_loss(
                va[target].to_numpy(dtype=int),
                clip_prob(pb),
                labels=[0, 1],
            )
        )
    return {
        "delta": float(log_loss(y, clip_prob(pred_feat), labels=[0, 1]) - log_loss(y, clip_prob(pred_base), labels=[0, 1])),
        "win_rate": float(np.mean(np.asarray(fold_deltas) < 0.0)),
        "folds": int(len(fold_deltas)),
    }


def scan_axes(features: pd.DataFrame) -> pd.DataFrame:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    cols = state_feature_cols(features)
    rows: list[dict[str, object]] = []
    for target in TARGETS:
        y = train[target].to_numpy(dtype=int)
        for feature in cols:
            z_all, _, _ = robust_z(train[feature], train[feature])
            q_low = np.quantile(z_all, 0.25)
            q_high = np.quantile(z_all, 0.75)
            low = y[z_all <= q_low]
            high = y[z_all >= q_high]
            if len(low) < 8 or len(high) < 8:
                continue
            lift = float(np.mean(high) - np.mean(low))
            subj = fold_scores_for_axis(train, target, feature, "subject_id")
            date = fold_scores_for_axis(train, target, feature, "dateblock_group")
            z_test, _, _ = robust_z(train[feature], features[features["split"].eq("test")][feature])
            train_test_gap = float(abs(np.nanmean(z_test) - np.nanmean(z_all)))
            shift_p90 = float(abs(np.nanpercentile(z_test, 90) - np.nanpercentile(z_all, 90)))
            boundary_signal = 0.0
            rows.append(
                {
                    "target": target,
                    "feature": feature,
                    "label_high_minus_low": lift,
                    "abs_label_lift": abs(lift),
                    "subject_delta": subj["delta"],
                    "subject_win_rate": subj["win_rate"],
                    "dateblock_delta": date["delta"],
                    "dateblock_win_rate": date["win_rate"],
                    "train_test_mean_gap": train_test_gap,
                    "train_test_p90_gap": shift_p90,
                    "boundary_signal": boundary_signal,
                    "direction": int(np.sign(lift)) if abs(lift) > 1.0e-12 else 0,
                }
            )
    scan = pd.DataFrame(rows)
    if scan.empty:
        return scan
    boundary = pd.read_csv(OUT / "e273_human_diary_state_jepa_audit_boundary.csv")
    boundary_map = boundary.set_index("feature")["abs_boundary_signal"].to_dict()
    scan["boundary_signal"] = scan["feature"].map(boundary_map).fillna(0.0).astype(float)
    scan["action_gate"] = (
        (scan["direction"].ne(0))
        & (scan["abs_label_lift"] >= 0.11)
        & (scan["dateblock_delta"] < -0.001)
        & (scan["subject_delta"] < 0.030)
        & (scan["train_test_mean_gap"] <= 1.25)
    )
    scan["diagnostic_gate"] = (
        ~scan["action_gate"]
        & (scan["direction"].ne(0))
        & (scan["abs_label_lift"] >= 0.16)
        & (scan["boundary_signal"] >= 0.55)
        & (scan["dateblock_delta"] < 0.020)
        & (scan["train_test_mean_gap"] <= 1.50)
    )
    scan["local_axis_score"] = (
        -scan["dateblock_delta"].clip(upper=0.05)
        -0.35 * scan["subject_delta"].clip(upper=0.08)
        +0.010 * scan["abs_label_lift"]
        +0.0010 * scan["boundary_signal"]
        -0.0015 * scan["train_test_mean_gap"]
    )
    return scan.sort_values(
        ["action_gate", "diagnostic_gate", "local_axis_score", "abs_label_lift"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)


def select_axes(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return scan
    pool = scan[scan["action_gate"] | scan["diagnostic_gate"]].copy()
    if pool.empty:
        pool = scan.sort_values(["dateblock_delta", "abs_label_lift"], ascending=[True, False]).head(20).copy()
        pool["fallback_only"] = True
    else:
        pool["fallback_only"] = False
    selected_rows: list[pd.Series] = []
    used: set[tuple[str, str]] = set()
    for _, row in pool.sort_values("local_axis_score", ascending=False).iterrows():
        key = (str(row["target"]), str(row["feature"]))
        if key in used:
            continue
        selected_rows.append(row)
        used.add(key)
        if len(selected_rows) >= 24:
            break
    return pd.DataFrame(selected_rows).reset_index(drop=True)


def apply_axis_moves(
    base: pd.DataFrame,
    features: pd.DataFrame,
    axes: pd.DataFrame,
    config: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    test_keys = test[KEYS].copy()
    base_keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        test_keys[col] = pd.to_datetime(test_keys[col]).dt.strftime("%Y-%m-%d")
        base_keys[col] = pd.to_datetime(base_keys[col]).dt.strftime("%Y-%m-%d")
    if not test_keys.equals(base_keys):
        raise RuntimeError("E273 test keys do not align with current submission")

    logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    original = logits.copy()
    cell_rows: list[dict[str, object]] = []
    n_axes = int(config["n_axes"])
    top_each = int(config["top_each"])
    amp = float(config["amp"])
    cap = float(config["cap"])
    targets = set(config.get("targets", TARGETS))
    use_diag = bool(config.get("include_diagnostic", True))
    pool = axes[axes["target"].isin(targets)].copy()
    if not use_diag:
        pool = pool[pool["action_gate"].astype(bool)]
    pool = pool.sort_values("local_axis_score", ascending=False).head(n_axes)

    for _, row in pool.iterrows():
        target = str(row["target"])
        target_idx = TARGETS.index(target)
        feature = str(row["feature"])
        direction = int(row["direction"])
        if direction == 0:
            continue
        z_test, _, _ = robust_z(train[feature], test[feature])
        effect = direction * z_test
        if not np.isfinite(effect).any():
            continue
        order_hi = np.argsort(effect)[::-1]
        order_lo = np.argsort(effect)
        chosen = np.zeros(len(test), dtype=bool)
        chosen[order_hi[:top_each]] = True
        chosen[order_lo[:top_each]] = True
        scale = np.clip(float(row["abs_label_lift"]) / 0.20, 0.45, 1.60)
        raw_delta = amp * scale * np.clip(effect / 2.5, -1.0, 1.0)
        delta = np.where(chosen, raw_delta, 0.0)
        before = logits[:, target_idx].copy()
        logits[:, target_idx] = np.clip(logits[:, target_idx] + delta, original[:, target_idx] - cap, original[:, target_idx] + cap)
        applied = logits[:, target_idx] - before
        for idx in np.where(np.abs(applied) > 1.0e-12)[0]:
            cell_rows.append(
                {
                    "candidate_id": str(config["candidate_id"]),
                    "row_idx": int(idx),
                    "subject_id": test.loc[idx, "subject_id"],
                    "sleep_date": test.loc[idx, "sleep_date"],
                    "lifelog_date": test.loc[idx, "lifelog_date"],
                    "target": target,
                    "feature": feature,
                    "axis_direction": direction,
                    "axis_abs_label_lift": float(row["abs_label_lift"]),
                    "axis_dateblock_delta": float(row["dateblock_delta"]),
                    "axis_subject_delta": float(row["subject_delta"]),
                    "axis_boundary_signal": float(row["boundary_signal"]),
                    "feature_effect": float(effect[idx]),
                    "logit_delta": float(applied[idx]),
                }
            )

    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    return out, pd.DataFrame(cell_rows)


def materialize_candidates(scan: pd.DataFrame, axes: pd.DataFrame) -> tuple[list[str], pd.DataFrame]:
    base = load_sub(CURRENT)
    features = pd.read_parquet(FEATURE_PATH)
    configs = [
        {
            "candidate_id": "action_only_top12_soft",
            "n_axes": 12,
            "top_each": 8,
            "amp": 0.030,
            "cap": 0.035,
            "include_diagnostic": False,
            "targets": TARGETS,
        },
        {
            "candidate_id": "energy_top18_balanced",
            "n_axes": 18,
            "top_each": 10,
            "amp": 0.040,
            "cap": 0.050,
            "include_diagnostic": True,
            "targets": TARGETS,
        },
        {
            "candidate_id": "q_sleep_subjective_top12",
            "n_axes": 12,
            "top_each": 12,
            "amp": 0.045,
            "cap": 0.055,
            "include_diagnostic": True,
            "targets": ["Q1", "Q2", "Q3"],
        },
        {
            "candidate_id": "q3_boundary_energy_top8",
            "n_axes": 8,
            "top_each": 18,
            "amp": 0.050,
            "cap": 0.060,
            "include_diagnostic": True,
            "targets": ["Q3"],
        },
        {
            "candidate_id": "s_objective_energy_top12",
            "n_axes": 12,
            "top_each": 10,
            "amp": 0.035,
            "cap": 0.045,
            "include_diagnostic": True,
            "targets": ["S1", "S2", "S3", "S4"],
        },
    ]
    files: list[str] = []
    all_cells: list[pd.DataFrame] = []
    for cfg in configs:
        out, cells = apply_axis_moves(base, features, axes, cfg)
        h = short_hash(out)
        filename = f"submission_e274_{cfg['candidate_id']}_{h}.csv"
        out.to_csv(OUT / filename, index=False)
        files.append(filename)
        if not cells.empty:
            cells["submission_file"] = filename
            all_cells.append(cells)
    cell_frame = pd.concat(all_cells, ignore_index=True) if all_cells else pd.DataFrame()
    cell_frame.to_csv(CELLS_OUT, index=False)
    return files, cell_frame


def audit_candidates(files: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    all_files = [CURRENT, *files]
    candidates = build_features(all_files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    anatomy = movement_anatomy(all_files, sample)
    scores.to_csv(SCORE_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return scores, anatomy, selected_models(model_df)


def write_report(scan: pd.DataFrame, axes: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, selected_models_df: pd.DataFrame, cells: pd.DataFrame) -> None:
    strict = int(scores["strict_promote_gate"].sum()) if not scores.empty else 0
    promoted = scores[scores["strict_promote_gate"].astype(bool)] if not scores.empty else pd.DataFrame()
    best = scores.iloc[0] if not scores.empty else None
    action_count = int(scan["action_gate"].sum()) if not scan.empty else 0
    diagnostic_count = int(scan["diagnostic_gate"].sum()) if not scan.empty else 0

    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "changed_rows_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
    ]
    scan_cols = [
        "target",
        "feature",
        "action_gate",
        "diagnostic_gate",
        "local_axis_score",
        "abs_label_lift",
        "dateblock_delta",
        "subject_delta",
        "boundary_signal",
        "train_test_mean_gap",
    ]
    lines = [
        "# E274 Target-Specific Diary Energy Audit",
        "",
        "## Question",
        "",
        "After E273 rejected broad diary-state modeling, can target-specific diary energy axes create a public-free-promotable candidate?",
        "",
        "## Local Axis Scan",
        "",
        f"- scanned axis-target rows: `{len(scan)}`",
        f"- action-gate axes: `{action_count}`",
        f"- diagnostic-gate axes: `{diagnostic_count}`",
        f"- selected axes for materialization: `{len(axes)}`",
        "",
        "### Top Axes",
        "",
        md_table(axes[scan_cols] if not axes.empty else axes, n=30),
        "",
        "## Public-Free Promotion Audit",
        "",
        f"- selected E272-style selector models: `{len(selected_models_df)}`",
        f"- strict promote count: `{strict}`",
    ]
    if best is not None:
        lines.extend([
            f"- best local candidate: `{best['basename']}` -> `{best['promotion_decision']}`",
            f"- best mean/p90 delta vs E247: `{float(best['pred_delta_vs_current_mean']):.9f}` / `{float(best['pred_delta_vs_current_p90']):.9f}`",
        ])
    lines.extend([
        "",
        "### Candidate Scores",
        "",
        md_table(scores[score_cols], n=40) if not scores.empty else "_empty_",
        "",
        "### Movement Anatomy",
        "",
        md_table(anatomy[anatomy_cols], n=40) if not anatomy.empty else "_empty_",
        "",
        "## Decision",
        "",
    ])
    if strict and not promoted.empty:
        lines.append("At least one E274 candidate clears the strict public-free promotion gate. This should be reviewed as a possible next submission, with the file above as the current priority.")
    else:
        lines.append("No E274 candidate clears the strict public-free promotion gate. The target-specific diary energy is locally informative but not yet submission-grade.")
    lines.extend([
        "",
        "Interpretation: a broad human diary latent failed in E273; E274 asks whether the surviving axes can be translated into target-specific probability movement. If the score table says `too_small_to_submit`, the axis is a real story but below public-free resolution. If it says `block_or_reject`, the axis likely repeats a known bad movement geometry.",
        "",
        "## Files",
        "",
        f"- `{SCAN_OUT.name}`",
        f"- `{AXIS_OUT.name}`",
        f"- `{SCORE_OUT.name}`",
        f"- `{ANATOMY_OUT.name}`",
        f"- `{CELLS_OUT.name}`",
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    features = pd.read_parquet(FEATURE_PATH)
    scan = scan_axes(features)
    scan.to_csv(SCAN_OUT, index=False)
    axes = select_axes(scan)
    axes.to_csv(AXIS_OUT, index=False)
    files, cells = materialize_candidates(scan, axes)
    scores, anatomy, selected_models_df = audit_candidates(files)
    write_report(scan, axes, scores, anatomy, selected_models_df, cells)
    print(REPORT_OUT)
    print("selected axes", len(axes), "generated", len(files))
    print(scores[[
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
