#!/usr/bin/env python3
"""E289: target-specific lifestyle-slice audit.

E288 found that the broad human/social lifestyle bundle is reconstructable but
unsafe as one shared feature block. This experiment keeps the human theory but
changes the target:

    broad lifestyle state -> target-specific slice -> tiny E247-current edit

Each target slice must first beat matched train nulls for that target. Only
then is it materialized as a small calibration delta on the current E247
submission and compared to row/subject/dateblock null submissions.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, normalized_mutual_info_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e289_target_specific_lifestyle_slice_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    build_context_views,
    build_story_matrix,
    clip_prob,
    fit_predict_test,
    groups_for,
    label_cv_loss,
    load_frames,
    make_latent,
    md_table,
    oof_multi_ridge,
    shuffled_matrix,
    stable_seed,
)
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 289
N_TRAIN_NULL_REPS = 18
N_TEST_NULL_REPS = 5
MAX_SELECTED_SLICES = 10
SCALES = [0.25, 0.50]
MATERIALIZE_MODES = ["centered", "raw"]
CAP = 0.080

SLICE_OUT = OUT / "e289_target_specific_lifestyle_slice_summary.csv"
TARGET_NULL_OUT = OUT / "e289_target_specific_lifestyle_slice_target_nulls.csv"
CANDIDATE_OUT = OUT / "e289_target_specific_lifestyle_slice_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e289_target_specific_lifestyle_slice_governor_summary.csv"
SCORE_OUT = OUT / "e289_target_specific_lifestyle_slice_scores.csv"
NULL_MAP_OUT = OUT / "e289_target_specific_lifestyle_slice_null_map.csv"
REPORT_OUT = OUT / "e289_target_specific_lifestyle_slice_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 92) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def prep_test_meta(frame: pd.DataFrame) -> pd.DataFrame:
    meta = frame[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    meta["subject_id"] = meta["subject_id"].astype(str)
    return meta.reset_index(drop=True)


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    keys = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    keys["subject_id"] = keys["subject_id"].astype(str)
    return keys.reset_index(drop=True)


def base_label_matrix_all(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    def make(df: pd.DataFrame) -> pd.DataFrame:
        pieces = []
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
        ]:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                pieces.append(pd.to_numeric(df[col], errors="coerce").fillna(0.0).rename(col))
        subj = pd.get_dummies(df["subject_id"].astype(str), prefix="subj", dtype=float)
        return pd.concat(pieces + [subj], axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)

    x_train = make(train_df).reset_index(drop=True)
    x_test = make(test_df).reset_index(drop=True)
    x_train, x_test = x_train.align(x_test, join="outer", axis=1, fill_value=0.0)
    return x_train.reset_index(drop=True), x_test.reset_index(drop=True)


def cluster6(
    train_lat: pd.DataFrame,
    test_lat: pd.DataFrame,
    train_subjects: pd.Series,
    view_id: str,
    split_name: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    km = KMeans(n_clusters=6, random_state=stable_seed("e289", view_id, split_name, "k6"), n_init=20)
    tr = km.fit_predict(train_lat)
    te = km.predict(test_lat)
    p = np.bincount(tr, minlength=6).astype(float)
    q = np.bincount(te, minlength=6).astype(float)
    p = p / max(p.sum(), 1.0)
    q = q / max(q.sum(), 1.0)
    diag = {
        "cluster6_train_test_js": float(jensenshannon(p + 1.0e-9, q + 1.0e-9, base=2.0)),
        "cluster6_subject_nmi": float(normalized_mutual_info_score(train_subjects.astype(str).to_numpy(), tr)),
    }
    return tr, te, diag


def rep_frames(train_lat: pd.DataFrame, test_lat: pd.DataFrame, tr_cluster: np.ndarray, te_cluster: np.ndarray) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    tr_pc = train_lat.reset_index(drop=True)
    te_pc = test_lat.reset_index(drop=True)
    tr_cl = pd.get_dummies(pd.Series(tr_cluster).astype(str), prefix="life_c6", dtype=float)
    te_cl = pd.get_dummies(pd.Series(te_cluster).astype(str), prefix="life_c6", dtype=float)
    tr_cl, te_cl = tr_cl.align(te_cl, join="outer", axis=1, fill_value=0.0)
    return {
        "pc": (tr_pc, te_pc),
        "cluster6": (tr_cl.reset_index(drop=True), te_cl.reset_index(drop=True)),
    }


def target_slice_stress(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    reps: dict[str, tuple[pd.DataFrame, pd.DataFrame]],
    tr_cluster: np.ndarray,
    view_id: str,
    split_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = groups_for(train_df, split_name).reset_index(drop=True)
    mode_groups = {
        "row": groups,
        "subject": groups_for(train_df, "subject5").reset_index(drop=True),
        "dateblock": groups_for(train_df, "dateblock5").reset_index(drop=True),
    }
    base_losses = {t: label_cv_loss(base_x, train_df[t].to_numpy(dtype=int), groups) for t in TARGETS}
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []

    for rep_id, (rep_train, _rep_test) in reps.items():
        actual_x = pd.concat([base_x.reset_index(drop=True), rep_train.reset_index(drop=True)], axis=1)
        for target in TARGETS:
            y = train_df[target].to_numpy(dtype=int)
            actual_loss = label_cv_loss(actual_x, y, groups)
            actual_delta = float(actual_loss - base_losses[target])
            null_vals = []
            rng = np.random.default_rng(stable_seed("e289target", view_id, split_name, rep_id, target))
            for mode, mgroups in mode_groups.items():
                for rep in range(N_TRAIN_NULL_REPS):
                    if rep_id == "pc":
                        shuffled = shuffled_matrix(rep_train.to_numpy(), mode, mgroups, rng)
                        nx = pd.concat(
                            [base_x.reset_index(drop=True), pd.DataFrame(shuffled, columns=rep_train.columns)],
                            axis=1,
                        )
                    else:
                        shuffled_cluster = shuffled_matrix(tr_cluster.reshape(-1, 1), mode, mgroups, rng).ravel().astype(int)
                        cl = pd.get_dummies(pd.Series(shuffled_cluster).astype(str), prefix="life_c6", dtype=float)
                        nx = pd.concat([base_x.reset_index(drop=True), cl.reset_index(drop=True)], axis=1)
                        nx = nx.reindex(columns=actual_x.columns, fill_value=0.0)
                    null_delta = float(label_cv_loss(nx, y, groups) - base_losses[target])
                    null_vals.append(null_delta)
                    null_rows.append(
                        {
                            "view_id": view_id,
                            "split": split_name,
                            "rep": rep_id,
                            "target": target,
                            "mode": mode,
                            "null_rep": rep,
                            "null_delta": null_delta,
                        }
                    )
            null_arr = np.asarray(null_vals, dtype=np.float64)
            dominance = float(np.mean(actual_delta < null_arr)) if len(null_arr) else 0.0
            mode_dom = {}
            for mode in ["row", "subject", "dateblock"]:
                vals = [r["null_delta"] for r in null_rows if r["view_id"] == view_id and r["split"] == split_name and r["rep"] == rep_id and r["target"] == target and r["mode"] == mode]
                mode_dom[f"{mode}_dominance"] = float(np.mean(actual_delta < np.asarray(vals, dtype=np.float64))) if vals else 0.0
            rows.append(
                {
                    "slice_id": f"{target}_{view_id}_{split_name}_{rep_id}",
                    "target": target,
                    "view_id": view_id,
                    "split": split_name,
                    "rep": rep_id,
                    "base_loss": base_losses[target],
                    "slice_loss": actual_loss,
                    "actual_delta": actual_delta,
                    "null_q20": float(np.quantile(null_arr, 0.20)),
                    "null_median": float(np.median(null_arr)),
                    "null_best": float(np.min(null_arr)),
                    "dominance": dominance,
                    **mode_dom,
                    "target_gate": bool(
                        actual_delta < -0.0015
                        and dominance >= 0.85
                        and min(mode_dom.values()) >= 0.70
                        and actual_delta < float(np.median(null_arr))
                    ),
                }
            )
    return rows, null_rows


def fit_prob_model(x: pd.DataFrame, y: np.ndarray):
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.35, max_iter=1200, solver="lbfgs"),
    )
    model.fit(x, y)
    return model


def target_delta_for_test(
    train_df: pd.DataFrame,
    target: str,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    rep_train: pd.DataFrame,
    rep_test: pd.DataFrame,
    mode: str,
) -> np.ndarray:
    y = train_df[target].to_numpy(dtype=int)
    x_base_tr = base_train.reset_index(drop=True)
    x_base_te = base_test.reset_index(drop=True)
    x_aug_tr = pd.concat([x_base_tr, rep_train.reset_index(drop=True)], axis=1)
    x_aug_te = pd.concat([x_base_te, rep_test.reset_index(drop=True)], axis=1)
    x_aug_tr, x_aug_te = x_aug_tr.align(x_aug_te, join="outer", axis=1, fill_value=0.0)
    x_base_tr, x_base_te = x_base_tr.align(x_base_te, join="outer", axis=1, fill_value=0.0)
    base_model = fit_prob_model(x_base_tr, y)
    aug_model = fit_prob_model(x_aug_tr, y)
    delta = logit(aug_model.predict_proba(x_aug_te)[:, 1]) - logit(base_model.predict_proba(x_base_te)[:, 1])
    delta = np.clip(delta, -CAP, CAP)
    if mode == "centered":
        delta = delta - float(np.median(delta))
        delta = np.clip(delta, -CAP, CAP)
    elif mode != "raw":
        raise ValueError(mode)
    return delta


def write_candidate(base: pd.DataFrame, target: str, delta: np.ndarray, candidate_id: str, scale: float) -> Path:
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    t_idx = TARGETS.index(target)
    logits[:, t_idx] = logits[:, t_idx] + scale * np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e289_lifeslice_{safe_id(candidate_id)}_s{int(scale*100):03d}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def write_null_candidate(base: pd.DataFrame, target: str, delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int, scale: float) -> Path:
    rng = np.random.default_rng(stable_seed("e289null", source_path.name, mode, rep, scale))
    values = np.asarray(delta, dtype=np.float64).copy()
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values))]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            shuffled[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += scale * shuffled
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e289null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def materialize(
    base: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    cache: dict[tuple[str, str], dict[str, Any]],
    slice_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    gated = slice_summary[slice_summary["target_gate"].astype(bool)].copy()
    if gated.empty:
        # Keep the audit concrete by stress-testing only the strongest target slices.
        gated = slice_summary.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_SELECTED_SLICES).copy()
    else:
        gated = gated.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_SELECTED_SLICES).copy()

    sample = base[KEYS].copy()
    meta = prep_test_meta(test_df)
    candidate_paths: list[Path] = []
    candidate_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []

    for _, row in gated.iterrows():
        key = (str(row["view_id"]), str(row["split"]))
        rep_id = str(row["rep"])
        target = str(row["target"])
        reps = cache[key]["reps"]
        rep_train, rep_test = reps[rep_id]
        for mode in MATERIALIZE_MODES:
            delta = target_delta_for_test(train_df, target, base_train, base_test, rep_train, rep_test, mode)
            if np.max(np.abs(delta)) < 1.0e-12:
                continue
            for scale in SCALES:
                candidate_id = f"{target}_{row['view_id']}_{row['split']}_{rep_id}_{mode}"
                path = write_candidate(base, target, delta, candidate_id, scale)
                candidate_paths.append(path)
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "basename": path.name,
                        "source_path": rel(path),
                        "target": target,
                        "view_id": row["view_id"],
                        "split": row["split"],
                        "rep": rep_id,
                        "delta_mode": mode,
                        "scale": scale,
                        "train_actual_delta": float(row["actual_delta"]),
                        "train_dominance": float(row["dominance"]),
                        "train_min_mode_dominance": float(min(row["row_dominance"], row["subject_dominance"], row["dateblock_dominance"])),
                        "delta_mean": float(np.mean(delta)),
                        "delta_std": float(np.std(delta)),
                        "delta_p90_abs": float(np.quantile(np.abs(delta), 0.90)),
                        "delta_max_abs": float(np.max(np.abs(delta))),
                        "changed_cells_vs_current": int(np.count_nonzero(np.abs(delta) > 1.0e-12)),
                        "l1_logit_delta_vs_current": float(np.sum(np.abs(scale * delta))),
                    }
                )
                for null_mode in ["row", "subject", "dateblock"]:
                    for rep in range(N_TEST_NULL_REPS):
                        null_path = write_null_candidate(base, target, delta, path, meta, null_mode, rep, scale)
                        null_rows.append(
                            {
                                "source_basename": path.name,
                                "null_basename": null_path.name,
                                "null_path": rel(null_path),
                                "mode": null_mode,
                                "rep": rep,
                            }
                        )

    candidate_meta = pd.DataFrame(candidate_rows)
    null_map = pd.DataFrame(null_rows)
    if candidate_meta.empty:
        return candidate_meta, null_map, pd.DataFrame()

    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_paths = [ROOT / p for p in null_map["null_path"].tolist()]
    score_features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, score_features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(candidate_meta["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidate_meta.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these_null = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].mean()) if len(these_null) else 1.0
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        ready = bool(old_strict and null_strict_rate <= 0.10 and p90_dominance >= 0.80 and mean_dominance >= 0.70 and worst_mode >= 0.55)
        rows.append(
            {
                **cand.to_dict(),
                "old_promotion_decision": a.get("promotion_decision", ""),
                "old_strict_promote": old_strict,
                "actual_mean": float(a["pred_delta_vs_current_mean"]),
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": float(a["pred_delta_vs_current_p90"]),
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "actual_p90", "p90_dominance"],
            ascending=[False, False, True, False],
        ).reset_index(drop=True)
    return candidate_meta, null_map, governor


def write_report(slice_summary: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame) -> None:
    gates = slice_summary[slice_summary["target_gate"].astype(bool)] if not slice_summary.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    lines = [
        "# E289 Target-Specific Lifestyle Slice Audit",
        "",
        "## Question",
        "",
        "Does the E288 lifestyle bundle become useful when split by target, and can a surviving slice be safely materialized on E247 without public LB?",
        "",
        "## Target Slice Stress",
        "",
        f"- slice rows: `{len(slice_summary)}`",
        f"- target-gate rows: `{len(gates)}`",
        "",
        md_table(
            slice_summary.sort_values(["target_gate", "actual_delta"], ascending=[False, True])[
                [
                    "slice_id",
                    "target",
                    "actual_delta",
                    "null_median",
                    "null_best",
                    "dominance",
                    "row_dominance",
                    "subject_dominance",
                    "dateblock_dominance",
                    "target_gate",
                ]
            ],
            n=40,
        ),
        "",
        "## Materialization Governor",
        "",
        f"- candidates: `{len(candidates)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "target",
                    "view_id",
                    "split",
                    "rep",
                    "delta_mode",
                    "scale",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "final_decision",
                ]
            ] if not governor.empty else governor,
            n=50,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E289 candidate is public-free ready. Submit only the top ready row as a scarce-LB hypothesis test.")
    else:
        lines.append("No E289 candidate is public-free ready. Keep target-specific lifestyle slices as diagnostics until they pass the current-anchor matched-null governor.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This experiment is stricter than E288. A target can improve locally and still fail if the resulting current-submission delta is too small, selector-adverse, or reproducible by row/subject/dateblock shuffles.",
            "",
            "## Files",
            "",
            f"- `{SLICE_OUT.name}`",
            f"- `{TARGET_NULL_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base_features, raw, stories, feature_frames = load_frames()
    story_matrix, _story_meta = build_story_matrix(base_features, stories, feature_frames)
    views = build_context_views(base_features, raw)
    train_mask = base_features["split"].eq("train").to_numpy()
    train_df = base_features.loc[train_mask].reset_index(drop=True)
    test_df = base_features.loc[~train_mask].reset_index(drop=True)
    y_story = story_matrix.loc[train_mask].reset_index(drop=True)
    base_train, base_test = base_label_matrix_all(train_df, test_df)

    all_slices: list[dict[str, Any]] = []
    all_target_nulls: list[dict[str, Any]] = []
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    for view_id, context in views.items():
        x_train = context.loc[train_mask].reset_index(drop=True)
        x_test = context.loc[~train_mask].reset_index(drop=True)
        for split_name in ["subject5", "dateblock5"]:
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_multi_ridge(x_train, y_story, groups)
            pred_test = fit_predict_test(x_train, y_story, x_test)
            train_lat, test_lat, _diag = make_latent(pred_train, pred_test)
            tr_cluster, te_cluster, _cdiag = cluster6(train_lat, test_lat, train_df["subject_id"], view_id, split_name)
            reps = rep_frames(train_lat, test_lat, tr_cluster, te_cluster)
            cache[(view_id, split_name)] = {"reps": reps, "tr_cluster": tr_cluster, "te_cluster": te_cluster}
            rows, null_rows = target_slice_stress(train_df, base_train, reps, tr_cluster, view_id, split_name)
            all_slices.extend(rows)
            all_target_nulls.extend(null_rows)

    slice_summary = pd.DataFrame(all_slices)
    target_nulls = pd.DataFrame(all_target_nulls)
    if not slice_summary.empty:
        slice_summary = slice_summary.sort_values(["target_gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)

    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    sample = current[KEYS].copy()
    if not prep_test_meta(test_df)[KEYS].equals(normalize_keys(sample)):
        raise RuntimeError("E289 test features do not align with current submission")
    candidates, null_map, governor = materialize(current, train_df, test_df, base_train, base_test, cache, slice_summary)

    slice_summary.to_csv(SLICE_OUT, index=False)
    target_nulls.to_csv(TARGET_NULL_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(slice_summary, candidates, governor)

    print(f"slice_rows={len(slice_summary)}")
    print(f"target_gates={int(slice_summary['target_gate'].sum()) if not slice_summary.empty else 0}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"best_slice_delta={slice_summary['actual_delta'].min():.9f}" if not slice_summary.empty else "best_slice_delta=nan")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
