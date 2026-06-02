#!/usr/bin/env python3
"""H073: human-social action-health bridge HS-JEPA.

H072 found an important split:

    story -> route assignment          weak under subject-preserving nulls
    story -> H068 action-health rows   useful signal

H073 moves the human-social layer one step upstream. Story-family latents are
trained to predict action-health and shortcut representations first. Only then
are H071 row-route assignments rescored and materialized.

Architecture test:

    C_human -> z_action_health / z_shortcut -> z_assignment -> correction field

The goal is not a small H057 refine. The goal is to test whether human stories
become action-grade when the target representation is action-health instead of
route identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h073_human_action_health_bridge_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-9
TOL = 1.0e-12


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H072MOD = import_module(HITL / "h072_human_social_state_engine_jepa.py", "h072mod_for_h073")
H071MOD = H072MOD.H071MOD


@dataclass(frozen=True)
class H073Spec:
    family: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_score: float
    min_cell_score: float
    novelty: str
    alpha: float
    mode: str
    allowed_routes: tuple[str, ...]


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return values
    if np.nanstd(values) < 1.0e-12:
        return np.full_like(values, 0.5, dtype=np.float64)
    return H071MOD.rank01(np.nan_to_num(values, nan=np.nanmedian(values)), high=high)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yb = np.asarray(y, dtype=float) > 0.5
    if yb.size == 0 or bool(yb.min()) == bool(yb.max()):
        return float("nan")
    return float(roc_auc_score(yb.astype(int), np.nan_to_num(score, nan=0.0)))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = pd.Series(a).rank(method="average").to_numpy(dtype=float)
    br = pd.Series(b).rank(method="average").to_numpy(dtype=float)
    if np.std(ar) < 1.0e-12 or np.std(br) < 1.0e-12:
        return 0.0
    return float(np.corrcoef(ar, br)[0, 1])


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h073_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h073_humanaction_bridge_*_uploadsafe.csv"):
        path.unlink()


def h071_promoted_selection(routes: pd.DataFrame, cells_by_route: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    spec = H071MOD.AssignmentSpec(
        family="assignment_big",
        max_cells=820,
        max_rows=185,
        q2_cap=72,
        max_per_subject=24,
        min_route_score=0.48,
        min_cell_score=0.34,
        novelty="outside_h069",
        alpha=1.0,
        mode="logit",
    )
    return H071MOD.select_assignments(spec, routes, cells_by_route)


def build_cell_frame(
    sample: pd.DataFrame,
    latent: pd.DataFrame,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    family = H072MOD.build_family_features(sample)
    _hyp, hyp_routes = H072MOD.hypothesis_route_table()
    route_pref = H072MOD.normalize_pref(H072MOD.MANUAL_ROUTE_PREF, hyp_routes)
    h071_route_sel, h071_cell_sel = h071_promoted_selection(routes, cells_by_route)
    h071_route_ids = set(h071_route_sel["route_id"].astype(str))
    h072_routes = H072MOD.add_human_route_scores(routes, family, route_pref, h071_route_ids)

    fam_cols = [f"family_{name}" for name in H072MOD.FAMILY_NAMES]
    row_cols = [
        "row",
        "dow",
        "is_weekend",
        "day_of_month",
        "month_start_prox",
        "month_end_prox",
        "payday_25_prox",
        "family_max_score",
        "family_mean_score",
        "family_entropy",
        "arousal_pressure",
        "recovery_pressure",
        "routine_calendar_pressure",
        "objective_measure_pressure",
        *fam_cols,
    ]
    cells = latent.merge(family[row_cols], on="row", how="left", validate="many_to_one").copy()
    cells["h071_selected_cell"] = cells["flat_index"].isin(set(h071_cell_sel["flat_index"].astype(int))).astype(float)
    cells["h071_selected_row"] = cells["row"].isin(set(h071_route_sel["row"].astype(int))).astype(float)
    cells["h073_target_q"] = cells["target"].isin(["Q1", "Q2", "Q3"]).astype(float)
    cells["h073_target_s"] = cells["target"].isin(S_TARGETS).astype(float)
    cells["h073_target_q2"] = (cells["target"] == "Q2").astype(float)
    cells["h073_target_nonq2"] = (cells["target"] != "Q2").astype(float)
    cells["h073_abs_direction"] = np.abs(cells["direction_to_q061"].to_numpy(dtype=float))
    cells = cells.replace([np.inf, -np.inf], 0.0).fillna(0.0)

    score_cols = [
        "flat_index",
        "h071_selected_cell",
        "h071_selected_row",
    ]
    route_cells: dict[str, pd.DataFrame] = {}
    for route_id, frame in cells_by_route.items():
        route_cells[route_id] = frame.merge(cells[score_cols], on="flat_index", how="left").fillna(0.0)
    return cells, h072_routes, route_cells


def feature_matrix(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    x = frame[columns].copy()
    target_dummies = pd.get_dummies(frame["target"], prefix="target", dtype=float)
    return pd.concat([x, target_dummies], axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def fit_oof_regressor(
    frame: pd.DataFrame,
    columns: list[str],
    target: str,
    groups: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, ExtraTreesRegressor, pd.DataFrame, list[str]]:
    x = feature_matrix(frame, columns)
    y = frame[target].to_numpy(dtype=np.float64)
    oof = np.zeros(len(frame), dtype=np.float64)
    fold_rows = []
    folds = GroupKFold(n_splits=5)
    for fold, (tr, va) in enumerate(folds.split(x, y, groups=groups)):
        model = ExtraTreesRegressor(
            n_estimators=260,
            max_depth=7,
            min_samples_leaf=8,
            max_features=0.70,
            random_state=seed + fold,
            n_jobs=-1,
        )
        model.fit(x.iloc[tr], y[tr])
        pred = np.asarray(model.predict(x.iloc[va]), dtype=np.float64)
        oof[va] = pred
        fold_rows.append(
            {
                "fold": fold,
                "target": target,
                "mae": float(mean_absolute_error(y[va], pred)),
                "rmse": float(mean_squared_error(y[va], pred) ** 0.5),
                "spearman": spearman(y[va], pred),
                "auc_if_binary": safe_auc(y[va], pred),
            }
        )
    full_model = ExtraTreesRegressor(
        n_estimators=360,
        max_depth=8,
        min_samples_leaf=6,
        max_features=0.75,
        random_state=seed + 999,
        n_jobs=-1,
    )
    full_model.fit(x, y)
    full = np.asarray(full_model.predict(x), dtype=np.float64)
    return oof, full, full_model, pd.DataFrame(fold_rows), list(x.columns)


def add_bridge_predictions(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    fam_cols = [f"family_{name}" for name in H072MOD.FAMILY_NAMES]
    story_cols = [
        *fam_cols,
        "family_max_score",
        "family_mean_score",
        "family_entropy",
        "arousal_pressure",
        "recovery_pressure",
        "routine_calendar_pressure",
        "objective_measure_pressure",
        "dow",
        "is_weekend",
        "month_start_prox",
        "month_end_prox",
        "payday_25_prox",
        "h073_target_q",
        "h073_target_s",
        "h073_target_q2",
        "h073_target_nonq2",
        "target_index",
    ]
    route_context_cols = [
        "cell_q061_gain",
        "q061_gain_rank",
        "abs_logit_move_to_q061",
        "direction_to_q061",
        "target_prior_weight",
        "story_route_direct",
        "story_route_balance",
        "story_route_no_direct",
        "public_weight",
        "public_responsibility_rank",
        "extension_score",
        "context_overlap",
        "row_q061_gain_from_h057_nonq2",
        "row_top4_gain_rank",
    ]
    route_context_cols = [col for col in route_context_cols if col in cells.columns]
    story_cols = [col for col in story_cols if col in cells.columns]
    groups = cells["subject_id"].astype(str).to_numpy()

    tasks = [
        ("story_to_h068_health", story_cols, "h068_cell_health", 7301),
        ("story_to_h068_selected", story_cols, "h068_selected_cell", 7307),
        ("story_to_shortcut", story_cols, "latent_shortcut_energy", 7311),
        ("story_route_to_h068_health", story_cols + route_context_cols, "h068_cell_health", 7319),
        ("story_route_to_h068_selected", story_cols + route_context_cols, "h068_selected_cell", 7321),
        ("story_route_to_shortcut", story_cols + route_context_cols, "latent_shortcut_energy", 7331),
    ]

    out = cells.copy()
    metric_rows = []
    fold_parts = []
    models: dict[str, object] = {}
    for name, cols, target, seed in tasks:
        oof, full, model, fold_df, feature_cols = fit_oof_regressor(cells, cols, target, groups, seed)
        out[f"{name}_oof"] = oof
        out[f"{name}_full"] = full
        y = cells[target].to_numpy(dtype=np.float64)
        metric_rows.append(
            {
                "task": name,
                "target": target,
                "n_features": len(feature_cols),
                "oof_mae": float(mean_absolute_error(y, oof)),
                "oof_rmse": float(mean_squared_error(y, oof) ** 0.5),
                "oof_spearman": spearman(y, oof),
                "oof_auc_h068_selected": safe_auc(cells["h068_selected_cell"], oof),
                "oof_auc_h071_selected": safe_auc(cells["h071_selected_cell"], oof),
                "oof_auc_h069_selected": safe_auc(cells["h069_selected_cell"], oof),
                "full_auc_h068_selected": safe_auc(cells["h068_selected_cell"], full),
                "full_spearman_target": spearman(y, full),
                "pred_std": float(np.std(full)),
            }
        )
        fold_df["task"] = name
        fold_parts.append(fold_df)
        models[name] = {"model": model, "feature_cols": feature_cols, "base_cols": cols}

    out["h073_story_action_energy"] = (
        0.34 * rank01(out["story_to_h068_selected_full"].to_numpy())
        + 0.24 * rank01(out["story_to_h068_health_full"].to_numpy())
        + 0.18 * rank01(out["story_route_to_h068_selected_full"].to_numpy())
        + 0.16 * rank01(out["story_route_to_h068_health_full"].to_numpy())
        - 0.24 * rank01(out["story_to_shortcut_full"].to_numpy())
        - 0.18 * rank01(out["story_route_to_shortcut_full"].to_numpy())
    )
    out["h073_bridge_cell_score"] = (
        0.28 * rank01(out["h073_story_action_energy"].to_numpy())
        + 0.16 * rank01(out["cell_assignment_score"].to_numpy())
        + 0.13 * rank01(out["h068_cell_health"].to_numpy())
        + 0.11 * rank01(out["public_score"].to_numpy())
        + 0.10 * rank01(out["invariant_score"].to_numpy())
        + 0.08 * rank01(out["cell_q061_gain"].to_numpy())
        + 0.05 * out["outside_h069_cell"].to_numpy(dtype=float)
        + 0.04 * out["outside_h070_cell"].to_numpy(dtype=float)
        + 0.03 * out["h073_target_s"].to_numpy(dtype=float)
        - 0.15 * rank01(out["latent_shortcut_energy"].to_numpy())
        - 0.10 * rank01(out["bad_pressure_rank"].to_numpy())
        - 0.10 * out["is_h050_null"].to_numpy(dtype=float)
        - 0.05 * out["h073_target_q2"].to_numpy(dtype=float)
    )
    out.loc[out["cell_q061_gain"] <= 0, "h073_bridge_cell_score"] -= 0.85
    out.loc[out["is_h050_null"] > 0, "h073_bridge_cell_score"] -= 0.35
    return out, pd.DataFrame(metric_rows), pd.concat(fold_parts, ignore_index=True), models


def shuffle_story_columns(cells: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    fam_cols = [f"family_{name}" for name in H072MOD.FAMILY_NAMES]
    story_cols = [
        *fam_cols,
        "family_max_score",
        "family_mean_score",
        "family_entropy",
        "arousal_pressure",
        "recovery_pressure",
        "routine_calendar_pressure",
        "objective_measure_pressure",
        "dow",
        "is_weekend",
        "month_start_prox",
        "month_end_prox",
        "payday_25_prox",
    ]
    story_cols = [col for col in story_cols if col in cells.columns]
    out = cells.copy()
    row_story = out.drop_duplicates("row")[["row", "subject_id", *story_cols]].sort_values("row").reset_index(drop=True)
    shuffled = row_story.copy()
    for subject in shuffled["subject_id"].astype(str).unique():
        idx = shuffled.index[shuffled["subject_id"].astype(str) == subject].to_numpy()
        perm = rng.permutation(idx)
        shuffled.loc[idx, story_cols] = row_story.loc[perm, story_cols].to_numpy()
    out = out.drop(columns=story_cols).merge(shuffled[["row", *story_cols]], on="row", how="left", validate="many_to_one")
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def prediction_null_stress(cells: pd.DataFrame, models: dict[str, object], n_iter: int = 180) -> pd.DataFrame:
    rng = np.random.default_rng(73073)
    rows = []
    base_tasks = ["story_to_h068_selected", "story_to_h068_health", "story_route_to_h068_selected"]
    for task in base_tasks:
        pred = cells[f"{task}_full"].to_numpy(dtype=float)
        rows.append(
            {
                "iter": -1,
                "task": task,
                "kind": "real",
                "auc_h068_selected": safe_auc(cells["h068_selected_cell"], pred),
                "auc_h071_selected": safe_auc(cells["h071_selected_cell"], pred),
                "spearman_h068_health": spearman(cells["h068_cell_health"], pred),
                "pred_std": float(np.std(pred)),
            }
        )
    for i in range(n_iter):
        shuffled = shuffle_story_columns(cells, rng)
        for task in base_tasks:
            info = models[task]
            x = feature_matrix(shuffled, info["base_cols"])
            x = x.reindex(columns=info["feature_cols"], fill_value=0.0)
            pred = np.asarray(info["model"].predict(x), dtype=float)
            rows.append(
                {
                    "iter": i,
                    "task": task,
                    "kind": "subject_row_permutation",
                    "auc_h068_selected": safe_auc(cells["h068_selected_cell"], pred),
                    "auc_h071_selected": safe_auc(cells["h071_selected_cell"], pred),
                    "spearman_h068_health": spearman(cells["h068_cell_health"], pred),
                    "pred_std": float(np.std(pred)),
                }
            )
    stress = pd.DataFrame(rows)
    summary_rows = []
    for task in base_tasks:
        real = stress[(stress["task"] == task) & (stress["iter"] < 0)].iloc[0]
        null = stress[(stress["task"] == task) & (stress["iter"] >= 0)]
        for metric in ["auc_h068_selected", "auc_h071_selected", "spearman_h068_health"]:
            vals = null[metric].to_numpy(dtype=float)
            summary_rows.append(
                {
                    "task": task,
                    "metric": metric,
                    "real": float(real[metric]),
                    "null_mean": float(np.nanmean(vals)),
                    "null_std": float(np.nanstd(vals)),
                    "null_p95": float(np.nanpercentile(vals, 95)),
                    "z_vs_null": float((float(real[metric]) - np.nanmean(vals)) / (np.nanstd(vals) + EPS)),
                    "p_ge_real": float(np.mean(vals >= float(real[metric]))),
                }
            )
    return stress, pd.DataFrame(summary_rows)


def update_route_scores(
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    score_cols = [
        "flat_index",
        "h073_bridge_cell_score",
        "h073_story_action_energy",
        "story_to_h068_selected_full",
        "story_to_h068_health_full",
        "story_route_to_h068_selected_full",
        "story_route_to_shortcut_full",
    ]
    score_map = cells[score_cols].copy()
    out_cells: dict[str, pd.DataFrame] = {}
    route_rows = []
    for rec in routes.to_dict("records"):
        route_id = str(rec["route_id"])
        use = cells_by_route[route_id].merge(score_map, on="flat_index", how="left").fillna(0.0)
        out_cells[route_id] = use
        route_rows.append(
            {
                **rec,
                "mean_h073_bridge_cell_score": float(use["h073_bridge_cell_score"].mean()),
                "sum_h073_bridge_cell_score": float(use["h073_bridge_cell_score"].sum()),
                "mean_story_action_energy": float(use["h073_story_action_energy"].mean()),
                "mean_story_to_h068_selected": float(use["story_to_h068_selected_full"].mean()),
                "mean_story_to_h068_health": float(use["story_to_h068_health_full"].mean()),
                "mean_story_route_shortcut": float(use["story_route_to_shortcut_full"].mean()),
            }
        )
    out = pd.DataFrame(route_rows)
    out["h073_bridge_rank"] = rank01(out["sum_h073_bridge_cell_score"].to_numpy() / np.sqrt(out["n_cells"].clip(lower=1)))
    out["h073_story_rank"] = rank01(out["mean_story_action_energy"].to_numpy())
    out["h073_shortcut_avoid_rank"] = rank01(-out["mean_story_route_shortcut"].to_numpy())
    out["h073_assignment_rank"] = rank01(out["assignment_route_score"].to_numpy())
    out["h073_public_rank"] = rank01(out["mean_public_score"].to_numpy())
    out["h073_invariant_rank"] = rank01(out["mean_invariant_score"].to_numpy())
    out["h073_route_score"] = (
        0.32 * out["h073_bridge_rank"]
        + 0.18 * out["h073_story_rank"]
        + 0.17 * out["h073_assignment_rank"]
        + 0.10 * out["h073_public_rank"]
        + 0.09 * out["h073_invariant_rank"]
        + 0.08 * out["h073_shortcut_avoid_rank"]
        + 0.04 * rank01(out["outside_h069_cells"].to_numpy())
        + 0.02 * rank01(out["sum_cell_gain"].to_numpy())
    )
    out.loc[out["mean_story_route_shortcut"] > out["mean_story_route_shortcut"].quantile(0.82), "h073_route_score"] -= 0.08
    return out.sort_values(["h073_route_score", "assignment_route_score"], ascending=[False, False]).reset_index(drop=True), out_cells


def h073_specs() -> list[H073Spec]:
    all_routes = tuple(H071MOD.ROUTES)
    return [
        H073Spec("story_action_big", 900, 215, 76, 25, 0.58, 0.32, "outside_h069", 1.0, "logit", all_routes),
        H073Spec("story_action_big", 760, 190, 64, 22, 0.61, 0.34, "outside_h071", 1.0, "logit", all_routes),
        H073Spec("action_private_bridge", 760, 205, 48, 24, 0.57, 0.33, "anti_shortcut", 1.0, "logit", all_routes),
        H073Spec(
            "arousal_action_bridge",
            720,
            190,
            76,
            24,
            0.55,
            0.31,
            "outside_h069",
            1.0,
            "logit",
            ("q3_s_stage", "q_subjective", "q2_s3_tail", "full_state", "nonq2_full", "q3_quality"),
        ),
        H073Spec(
            "stage_health_bridge",
            700,
            200,
            0,
            24,
            0.55,
            0.32,
            "anti_shortcut",
            1.0,
            "logit",
            ("s_stage", "q3_s_stage", "nonq2_full", "s23_core", "s14_edge", "recovery_route"),
        ),
        H073Spec(
            "fullvector_action_state",
            980,
            225,
            88,
            25,
            0.52,
            0.29,
            "outside_h069",
            1.0,
            "logit",
            ("full_state", "nonq2_full", "q3_s_stage", "q_subjective", "s_stage", "recovery_route"),
        ),
    ]


def allowed_by_spec(spec: H073Spec, rec: dict[str, object]) -> bool:
    if spec.allowed_routes and str(rec["route_name"]) not in spec.allowed_routes:
        return False
    if float(rec["h073_route_score"]) < spec.min_route_score:
        return False
    if spec.novelty == "outside_h069" and int(rec["outside_h069_cells"]) < max(1, int(rec["n_cells"]) // 2):
        return False
    if spec.novelty == "outside_h071" and float(rec.get("h071_selected_route", 0.0)) > 0:
        return False
    if spec.novelty == "anti_shortcut" and float(rec["mean_shortcut_energy"]) > 0.42:
        return False
    return True


def select_assignments(
    spec: H073Spec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes.apply(lambda row: allowed_by_spec(spec, row.to_dict()), axis=1)].copy()
    pool = pool.sort_values(["h073_route_score", "mean_h073_bridge_cell_score", "assignment_route_score"], ascending=False)
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    selected_routes = []
    selected_cells = []
    total_cells = 0
    q2_cells = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(used_rows) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        cells = cells_by_route[str(rec["route_id"])].copy()
        cells = cells[cells["h073_bridge_cell_score"] >= spec.min_cell_score]
        cells = cells[cells["cell_q061_gain"] > 0]
        cells = cells[cells["is_h050_null"] == 0]
        if cells.empty:
            continue
        if total_cells + len(cells) > spec.max_cells:
            continue
        new_q2 = int((cells["target"] == "Q2").sum())
        if q2_cells + new_q2 > spec.q2_cap:
            continue
        selected_routes.append(pd.DataFrame([rec]))
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        total_cells += int(len(cells))
        q2_cells += new_q2
        if total_cells >= spec.max_cells * 0.96:
            break
    if not selected_routes:
        return pool.iloc[0:0].copy(), pool.iloc[0:0].copy()
    return pd.concat(selected_routes, ignore_index=True), pd.concat(selected_cells, ignore_index=True)


def apply_candidate(
    spec: H073Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    route_sel, cell_sel = select_assignments(spec, routes, cells_by_route)
    h057_prob = mats["h057"]
    q061 = mats["q061"]
    prob = h057_prob.copy()
    moved = H071MOD.move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]
    prob = H071MOD.clip_prob(prob)
    changed = np.abs(prob - h057_prob) > TOL
    x = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).reshape(-1)
    row_delta = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (H071MOD.logit(prob) - H071MOD.logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    route_counts = route_sel["route_name"].value_counts().to_dict() if len(route_sel) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "max_per_subject": spec.max_per_subject,
        "min_route_score": spec.min_route_score,
        "min_cell_score": spec.min_cell_score,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h070_cells": int(cell_sel["outside_h070_cell"].sum()) if len(cell_sel) else 0,
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "h071_route_overlap": int(route_sel.get("h071_selected_route", pd.Series(dtype=float)).sum()) if len(route_sel) else 0,
        "h070_overlap_cells": int(cell_sel["h070_selected_cell"].sum()) if len(cell_sel) else 0,
        "h069_overlap_cells": int(cell_sel["h069_selected_cell"].sum()) if len(cell_sel) else 0,
        "h068_overlap_cells": int(cell_sel["h068_selected_cell"].sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_h073_route_score": float(route_sel["h073_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_bridge_cell_score": float(cell_sel["h073_bridge_cell_score"].mean()) if len(cell_sel) else 0.0,
        "mean_story_action_energy": float(cell_sel["h073_story_action_energy"].mean()) if len(cell_sel) else 0.0,
        "mean_story_to_h068_selected": float(cell_sel["story_to_h068_selected_full"].mean()) if len(cell_sel) else 0.0,
        "mean_assignment_route_score": float(route_sel["assignment_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return prob, meta


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    null_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    bridge_auc = float(
        null_summary[
            (null_summary["task"] == "story_to_h068_selected") & (null_summary["metric"] == "auc_h068_selected")
        ]["real"].iloc[0]
    )
    bridge_auc_z = float(
        null_summary[
            (null_summary["task"] == "story_to_h068_selected") & (null_summary["metric"] == "auc_h068_selected")
        ]["z_vs_null"].iloc[0]
    )
    for spec in h073_specs():
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 120 or meta["selected_routes"] < 20:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h073_{spec.family}_{spec.novelty}_c{spec.max_cells}_r{spec.max_rows}_q2{spec.q2_cap}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        meta["story_oof_auc_h068_selected"] = bridge_auc
        meta["story_full_auc_z_vs_shuffle"] = bridge_auc_z
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H073 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["bridge_rank"] = rank01(cand["mean_bridge_cell_score"].to_numpy())
    cand["story_rank"] = rank01(cand["mean_story_action_energy"].to_numpy())
    cand["route_rank"] = rank01(cand["mean_h073_route_score"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00080) / 0.00120).clip(0.0, 1.0)
    cand["h073_score"] = (
        0.20 * cand["action_rank"]
        + 0.14 * cand["responsibility_rank"]
        + 0.13 * cand["bridge_rank"]
        + 0.11 * cand["story_rank"]
        + 0.11 * cand["route_rank"]
        + 0.10 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.08 * cand["shortcut_avoid_rank"]
        + 0.05 * cand["bigbet_scale_score"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * cand["bad_avoid_rank"]
        + 0.02 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        - 0.06 * cand["q2_risk"]
        - 0.06 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h073_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(80).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    model_metrics: pd.DataFrame,
    null_summary: pd.DataFrame,
    routes: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    report = "\n".join(
        [
            "# H073 Human-Social Action-Health Bridge HS-JEPA",
            "",
            "Question: does the human-social layer become action-grade when it",
            "predicts H068 action-health/shortcut before H071 route assignment?",
            "",
            "Design:",
            "",
            "- input context: H072 story-family row latents plus target/route context;",
            "- target representation: H068 action-health, H068 selected-cell indicator, shortcut energy;",
            "- decoder: H073 bridge cell score -> H071 route assignment -> H061 q061 correction;",
            "- stress: subject-group OOF, subject-preserving story-feature shuffle, bad-anchor cosine.",
            "",
            "Model metrics:",
            "",
            md_table(model_metrics, 20),
            "",
            "Story placement null summary:",
            "",
            md_table(null_summary, 30),
            "",
            "Top H073 routes:",
            "",
            md_table(
                routes[
                    [
                        "route_id",
                        "row",
                        "subject_id",
                        "sleep_date",
                        "route_name",
                        "n_cells",
                        "h073_route_score",
                        "mean_h073_bridge_cell_score",
                        "mean_story_action_energy",
                        "outside_h069_cells",
                        "mean_shortcut_energy",
                    ]
                ],
                35,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(40), 40),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H073 wins by >= 0.001, `C_human -> z_action_health -> z_assignment` is the preferred HS-JEPA path.",
            "- If H073 loses while H071 wins, human stories help explanation but not action-health materialization.",
            "- If H073 and H072 both lose badly, human-social latents should be used only as diagnostics, not submission decoders.",
            "",
        ]
    )
    (OUT / "h073_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    scored_latent = H071MOD.add_cell_scores(latent)
    routes, cells_by_route = H071MOD.build_route_candidates(latent)
    cells, h072_routes, _route_cells = build_cell_frame(sample, scored_latent, routes, cells_by_route)
    cells, model_metrics, fold_metrics, models = add_bridge_predictions(cells)
    null_stress, null_summary = prediction_null_stress(cells, models)
    h073_routes, h073_cells_by_route = update_route_scores(h072_routes, cells_by_route, cells)
    cand, probs = candidate_sweep(sample, mats, h073_routes, h073_cells_by_route, beta, bad_vecs, null_summary)

    bridge_oof_auc = float(model_metrics.loc[model_metrics["task"].eq("story_to_h068_selected"), "oof_auc_h068_selected"].iloc[0])
    bridge_null_z = float(
        null_summary[
            (null_summary["task"] == "story_to_h068_selected") & (null_summary["metric"] == "auc_h068_selected")
        ]["z_vs_null"].iloc[0]
    )
    bridge_ok = bool(bridge_oof_auc >= 0.62 and bridge_null_z >= 1.0)
    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00090)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00075)
        & (cand["changed_cells_vs_h057"] >= 600)
    ].sort_values(["public_action_pred_delta_vs_h057", "h073_score"], ascending=[True, False])
    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        if bridge_ok:
            decision_name = "promote_humanaction_bridge_architecture_bigbet"
            worldview = "human-social context predicts action-health strongly enough to drive route assignment"
        else:
            decision_name = "promote_humanaction_bridge_sensor_bridge_weak"
            worldview = "human-social action-health bridge creates a large candidate, but bridge diagnostics are not decisive"
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_humanaction_bridge_sensor"
        worldview = "human-social action-health bridge is a diagnostic route, not yet a 0.001-scale action solver"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h073_humanaction_bridge_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": decision_name,
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": worldview,
                "bridge_oof_auc_h068_selected": bridge_oof_auc,
                "bridge_null_z": bridge_null_z,
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    cells.to_csv(OUT / "h073_cell_scores.csv", index=False)
    model_metrics.to_csv(OUT / "h073_model_metrics.csv", index=False)
    fold_metrics.to_csv(OUT / "h073_fold_metrics.csv", index=False)
    null_stress.to_csv(OUT / "h073_story_action_null_stress.csv", index=False)
    null_summary.to_csv(OUT / "h073_story_action_null_summary.csv", index=False)
    h073_routes.to_csv(OUT / "h073_route_candidates.csv", index=False)
    cand.to_csv(OUT / "h073_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h073_decision.csv", index=False)
    write_report(model_metrics, null_summary, h073_routes, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "bridge_oof_auc_h068_selected",
                "bridge_null_z",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "route_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
