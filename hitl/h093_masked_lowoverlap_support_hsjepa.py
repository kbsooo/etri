#!/usr/bin/env python3
"""H093: masked low-overlap route-support HS-JEPA.

H092 proved that raw day-block context predicts action-grade route quality, but
the selected cells mostly overlapped the H087/H088/H091/H092 basin. H093 changes
the target representation instead of adding more context:

    context: raw sensor/app/activity day-block state + route structure
    target: action-grade support outside known root selected-cell supports
    decoder: route-conditioned value law materialized only after novelty gates

This is a big-bet falsification test. If H093 improves, the next HS-JEPA claim is
that hidden human state can predict new row-target support beyond the current
public/private basin. If it loses, the breakthrough bottleneck is not raw
context or low-overlap support discovery; it is the value law/public equation
itself.
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
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h093_masked_lowoverlap_support_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h092mod = import_module(HITL / "h092_raw_dayblock_action_latent_hsjepa.py", "h092mod_for_h093")
h091mod = h092mod.h091mod
h087mod = h092mod.h087mod
h089mod = h092mod.h089mod
h088mod = h092mod.h088mod

TARGETS = h092mod.TARGETS
KEYS = h092mod.KEYS
BASE_FILE = h092mod.BASE_FILE
TOL = h087mod.TOL
H093_HEADS = ["white", "white_private", "white_public", "white_objective", "white_q2", "overall"]


@dataclass(frozen=True)
class H093Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_masked_score: float
    max_known_overlap: float
    min_known_white: float
    min_cells_for_root: int
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h093_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h093_masked_lowoverlap_*_uploadsafe.csv"):
        path.unlink()


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h087mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h087mod.md_table(frame, n=n)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h087mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=float) > 0.5
    if len(yy) == 0 or bool(yy.min()) == bool(yy.max()):
        return float("nan")
    return float(roc_auc_score(yy.astype(int), np.nan_to_num(score, nan=0.0)))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = pd.Series(a).rank(method="average").to_numpy(dtype=float)
    br = pd.Series(b).rank(method="average").to_numpy(dtype=float)
    if float(np.nanstd(ar)) < 1.0e-12 or float(np.nanstd(br)) < 1.0e-12:
        return 0.0
    return float(np.corrcoef(ar, br)[0, 1])


def parse_targets(text: object) -> list[str]:
    return h091mod.parse_targets(text)


def target_allowed(targets: list[str], group: str) -> bool:
    if group == "q2_route":
        return "Q2" in set(targets)
    return h091mod.target_allowed(targets, group)


def root_cells(kind: str) -> set[tuple[int, str]]:
    dirs = {
        "h087": HITL / "h087_route_value_law_hsjepa",
        "h088": HITL / "h088_dual_state_value_gate_hsjepa",
        "h091": HITL / "h091_learned_lifestyle_action_latent_hsjepa",
        "h092": HITL / "h092_raw_dayblock_action_latent_hsjepa",
    }
    if kind not in dirs:
        raise ValueError(kind)
    directory = dirs[kind]
    decision = pd.read_csv(directory / f"{kind}_decision.csv").iloc[0]
    selected = pd.read_csv(directory / f"{kind}_selected_cells.csv")
    selected = selected[selected["candidate_id"].astype(str).eq(str(decision["candidate_id"]))]
    return {(int(row), str(target)) for row, target in zip(selected["row"], selected["target"])}


def add_known_support_overlap(actions: pd.DataFrame) -> pd.DataFrame:
    refs = {name: root_cells(name) for name in ["h087", "h088", "h091", "h092"]}
    rows = {name: {row for row, _target in cells} for name, cells in refs.items()}

    overlap: dict[str, list[float]] = {f"{name}_cell_overlap_ratio": [] for name in refs}
    outside: dict[str, list[float]] = {f"outside_{name}_row": [] for name in refs}
    for rec in actions[["row", "targets"]].to_dict("records"):
        row = int(rec["row"])
        cells = [(row, target) for target in parse_targets(rec["targets"])]
        denom = max(len(cells), 1)
        for name, ref_cells in refs.items():
            overlap[f"{name}_cell_overlap_ratio"].append(sum(cell in ref_cells for cell in cells) / denom)
            outside[f"outside_{name}_row"].append(float(row not in rows[name]))

    out = actions.copy()
    for name, values in overlap.items():
        out[name] = values
    for name, values in outside.items():
        out[name] = values

    overlap_cols = [f"{name}_cell_overlap_ratio" for name in refs]
    outside_cols = [f"outside_{name}_row" for name in refs]
    out["max_known_overlap_ratio"] = out[overlap_cols].max(axis=1)
    out["mean_known_overlap_ratio"] = out[overlap_cols].mean(axis=1)
    out["min_known_overlap_ratio"] = out[overlap_cols].min(axis=1)
    out["known_outside_rate"] = out[outside_cols].mean(axis=1)
    out["known_white_rank"] = rank01(
        0.52 * (1.0 - out["max_known_overlap_ratio"].to_numpy(dtype=float))
        + 0.24 * (1.0 - out["mean_known_overlap_ratio"].to_numpy(dtype=float))
        + 0.16 * out["known_outside_rate"].to_numpy(dtype=float)
        + 0.08 * out["white_space_rank"].to_numpy(dtype=float)
    )
    return out


def build_masked_target_matrix(actions: pd.DataFrame) -> pd.DataFrame:
    out = actions.copy()
    safe_public = (
        0.55 * out["posterior_safe"].to_numpy(dtype=float)
        + 0.25 * (out["posterior_delta_sum"].astype(float) <= 2.0e-6).astype(float)
        + 0.20 * (out["source_proxy_sum"].astype(float) <= 4.0e-6).astype(float)
    )
    safe_private = (
        0.55 * out["hard_safe"].to_numpy(dtype=float)
        + 0.25 * (out["hard_delta_sum"].astype(float) <= 2.0e-6).astype(float)
        + 0.20 * (out["mean_bad_same_rank"].astype(float) <= 0.72).astype(float)
    )
    safe_source = (
        0.62 * out["source_safe"].to_numpy(dtype=float)
        + 0.23 * (out["source_proxy_sum"].astype(float) <= 4.0e-6).astype(float)
        + 0.15 * out["h082_rank"].to_numpy(dtype=float)
    )
    novelty = out["known_white_rank"].to_numpy(dtype=float)
    max_overlap = out["max_known_overlap_ratio"].to_numpy(dtype=float)
    bad_penalty = (
        0.18 * (out["mean_bad_same_rank"].astype(float) > 0.72).astype(float)
        + 0.18 * (out["posterior_delta_sum"].astype(float) > 4.0e-6).astype(float)
        + 0.18 * (out["hard_delta_sum"].astype(float) > 4.0e-6).astype(float)
        + 0.16 * (out["source_proxy_sum"].astype(float) > 7.0e-6).astype(float)
        + 0.12 * (max_overlap > 0.92).astype(float)
    )
    route_quality = (
        0.22 * out["assignment_rank"].to_numpy(dtype=float)
        + 0.18 * out["route_score_rank"].to_numpy(dtype=float)
        + 0.16 * out["bad_avoid_rank"].to_numpy(dtype=float)
        + 0.14 * out["h082_rank"].to_numpy(dtype=float)
        + 0.12 * out["scale_rank"].to_numpy(dtype=float)
        + 0.10 * out["outside_rank"].to_numpy(dtype=float)
        + 0.08 * out["shortcut_avoid_rank"].to_numpy(dtype=float)
    )

    out["target_white"] = (
        0.36 * novelty
        + 0.17 * route_quality
        + 0.14 * out["source_gain_rank"].to_numpy(dtype=float)
        + 0.12 * out["hard_gain_rank"].to_numpy(dtype=float)
        + 0.10 * out["posterior_gain_rank"].to_numpy(dtype=float)
        + 0.07 * out["dual_pareto"].to_numpy(dtype=float)
        + 0.04 * safe_source
        - bad_penalty
    )
    out["target_white_private"] = (
        0.34 * novelty
        + 0.25 * out["hard_gain_rank"].to_numpy(dtype=float)
        + 0.14 * safe_private
        + 0.10 * out["dual_pareto"].to_numpy(dtype=float)
        + 0.09 * route_quality
        + 0.08 * out["private_mode"].to_numpy(dtype=float)
        - 0.85 * bad_penalty
    )
    out["target_white_public"] = (
        0.32 * novelty
        + 0.24 * out["posterior_gain_rank"].to_numpy(dtype=float)
        + 0.14 * out["source_gain_rank"].to_numpy(dtype=float)
        + 0.11 * safe_public
        + 0.10 * route_quality
        + 0.09 * out["posterior_mode"].to_numpy(dtype=float)
        - 0.85 * bad_penalty
    )
    out["target_white_objective"] = (
        0.30 * novelty
        + 0.21 * out["source_gain_rank"].to_numpy(dtype=float)
        + 0.18 * out["is_objective_route"].to_numpy(dtype=float)
        + 0.13 * safe_source
        + 0.10 * out["h082_rank"].to_numpy(dtype=float)
        + 0.08 * route_quality
        - 0.70 * bad_penalty
    )
    out["target_white_q2"] = (
        0.30 * novelty
        + 0.20 * out["has_q2"].to_numpy(dtype=float)
        + 0.16 * out["posterior_gain_rank"].to_numpy(dtype=float)
        + 0.14 * out["hard_gain_rank"].to_numpy(dtype=float)
        + 0.10 * safe_public
        + 0.06 * safe_private
        + 0.04 * route_quality
        - 0.80 * bad_penalty
    )
    out["target_overall"] = (
        0.30 * out["target_white"]
        + 0.20 * out["target_white_private"]
        + 0.20 * out["target_white_public"]
        + 0.14 * out["target_white_objective"]
        + 0.10 * out["target_white_q2"]
        + 0.06 * novelty
    )
    for col in [f"target_{head}" for head in H093_HEADS]:
        out[col] = np.clip(out[col].to_numpy(dtype=np.float64), 0.0, 1.0)
    return out


def build_route_actions(sample: pd.DataFrame) -> pd.DataFrame:
    actions = h092mod.build_route_actions(sample)
    actions = add_known_support_overlap(actions)
    return build_masked_target_matrix(actions)


def build_feature_frame(actions: pd.DataFrame, raw_feature_cols: list[str]) -> tuple[pd.DataFrame, list[str], list[str]]:
    route_numeric = [
        "n_cells",
        "q2_cells",
        "s_cells",
        "route_score",
        "assignment_route_score",
        "outside_h069_cells",
        "outside_h070_cells",
        "mean_shortcut_energy",
        "mean_public_score",
        "mean_invariant_score",
        "route_score_rank",
        "assignment_rank",
        "outside_rank",
        "shortcut_avoid_rank",
        "h082_rank",
        "hard_conf_rank",
        "scale_rank",
        "has_q2",
        "has_q",
        "is_objective_route",
        "is_full_state_route",
        "is_recovery_route",
        "posterior_mode",
        "private_mode",
    ]
    route_numeric = [c for c in route_numeric if c in actions.columns]
    numeric_cols = raw_feature_cols + route_numeric
    numeric_cols = [c for c in numeric_cols if c in actions.columns and pd.api.types.is_numeric_dtype(actions[c])]
    categorical_cols = [c for c in ["route_name", "value_mode", "target_group_key"] if c in actions.columns]
    num = actions[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    cats = pd.get_dummies(actions[categorical_cols].fillna("__NA__").astype(str), prefix=categorical_cols, dtype=float)
    return pd.concat([num.reset_index(drop=True), cats.reset_index(drop=True)], axis=1), numeric_cols, categorical_cols


def model_factory(seed: int, kind: str) -> object:
    if kind == "extra":
        return ExtraTreesRegressor(
            n_estimators=300,
            max_depth=10,
            min_samples_leaf=6,
            max_features=0.62,
            random_state=seed,
            n_jobs=-1,
        )
    if kind == "forest":
        return RandomForestRegressor(
            n_estimators=220,
            max_depth=11,
            min_samples_leaf=7,
            max_features=0.60,
            random_state=seed,
            n_jobs=-1,
        )
    raise ValueError(kind)


def fit_oof_masked_latent(actions: pd.DataFrame, raw_feature_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    target_cols = [f"target_{head}" for head in H093_HEADS]
    x, numeric_cols, categorical_cols = build_feature_frame(actions, raw_feature_cols)
    y = actions[target_cols].to_numpy(dtype=np.float64)
    groups = actions["subject_id"].astype(str).to_numpy()
    unique_groups = np.unique(groups)
    split = GroupKFold(n_splits=min(5, len(unique_groups)))

    seeds = [(93091, "extra"), (93092, "extra"), (93093, "forest")]
    oof_sum = np.zeros_like(y, dtype=np.float64)
    pred_sum = np.zeros_like(y, dtype=np.float64)
    for seed, kind in seeds:
        fold_pred = np.zeros_like(y, dtype=np.float64)
        for train_idx, valid_idx in split.split(x, y, groups):
            model = model_factory(seed, kind)
            model.fit(x.iloc[train_idx], y[train_idx])
            fold_pred[valid_idx] = np.clip(model.predict(x.iloc[valid_idx]), 0.0, 1.0)
        oof_sum += fold_pred
        full = model_factory(seed + 100, kind)
        full.fit(x, y)
        pred_sum += np.clip(full.predict(x), 0.0, 1.0)

    oof = oof_sum / len(seeds)
    full_pred = pred_sum / len(seeds)
    out = actions.copy()
    for i, head in enumerate(H093_HEADS):
        out[f"masked_{head}_oof"] = np.clip(oof[:, i], 0.0, 1.0)
        out[f"masked_{head}_full"] = np.clip(full_pred[:, i], 0.0, 1.0)
        out[f"masked_{head}"] = 0.80 * out[f"masked_{head}_oof"] + 0.20 * out[f"masked_{head}_full"]

    head_mat = out[[f"masked_{head}" for head in H093_HEADS[:-1]]].to_numpy(dtype=float)
    head_ix = head_mat.argmax(axis=1)
    out["masked_head"] = [H093_HEADS[i] for i in head_ix]
    out["masked_head_score"] = head_mat.max(axis=1)
    sorted_head = np.sort(head_mat, axis=1)
    out["masked_head_margin"] = sorted_head[:, -1] - sorted_head[:, -2]
    out["masked_latent_score"] = (
        0.48 * out["masked_overall"]
        + 0.17 * out["masked_head_score"]
        + 0.14 * out["masked_white"]
        + 0.09 * out["raw_transition_q"]
        + 0.06 * out["assignment_rank"]
        + 0.06 * out["h082_rank"]
    )

    rows = []
    for i, head in enumerate(H093_HEADS):
        target = y[:, i]
        pred = out[f"masked_{head}_oof"].to_numpy(dtype=float)
        rows.append(
            {
                "head": head,
                "target_mean": float(np.mean(target)),
                "pred_mean": float(np.mean(pred)),
                "pred_std": float(np.std(pred)),
                "spearman_oof": spearman(target, pred),
                "auc_top25_oof": safe_auc(target >= np.quantile(target, 0.75), pred),
                "auc_top10_oof": safe_auc(target >= np.quantile(target, 0.90), pred),
            }
        )
    diag = pd.DataFrame(rows)
    return out.sort_values("masked_latent_score", ascending=False).reset_index(drop=True), diag, numeric_cols, categorical_cols


def spec_list() -> list[H093Spec]:
    return [
        H093Spec(
            name="masked_white_large_c920_r210_q120",
            profile="white_large",
            target_group="all",
            max_routes=210,
            max_cells=920,
            max_rows=210,
            q2_cap=120,
            max_per_subject=34,
            min_masked_score=0.585,
            max_known_overlap=0.78,
            min_known_white=0.48,
            min_cells_for_root=180,
            alpha=1.18,
            cap=2.10,
            novelty="masked_lowoverlap_large_support",
        ),
        H093Spec(
            name="masked_white_bridge_c1080_r220_q125",
            profile="white_bridge",
            target_group="all",
            max_routes=220,
            max_cells=1080,
            max_rows=220,
            q2_cap=125,
            max_per_subject=36,
            min_masked_score=0.565,
            max_known_overlap=0.88,
            min_known_white=0.38,
            min_cells_for_root=260,
            alpha=1.16,
            cap=2.05,
            novelty="masked_lowoverlap_bridge_to_scale",
        ),
        H093Spec(
            name="masked_private_c760_r185_q70",
            profile="white_private",
            target_group="all",
            max_routes=185,
            max_cells=760,
            max_rows=185,
            q2_cap=70,
            max_per_subject=30,
            min_masked_score=0.565,
            max_known_overlap=0.82,
            min_known_white=0.42,
            min_cells_for_root=160,
            alpha=1.12,
            cap=1.95,
            novelty="masked_private_new_support",
        ),
        H093Spec(
            name="masked_public_q2_c760_r180_q135",
            profile="white_public_q2",
            target_group="all",
            max_routes=180,
            max_cells=760,
            max_rows=180,
            q2_cap=135,
            max_per_subject=30,
            min_masked_score=0.565,
            max_known_overlap=0.84,
            min_known_white=0.40,
            min_cells_for_root=160,
            alpha=1.22,
            cap=2.22,
            novelty="masked_public_q2_new_support",
        ),
        H093Spec(
            name="masked_objective_c700_r170",
            profile="white_objective",
            target_group="objective",
            max_routes=170,
            max_cells=700,
            max_rows=170,
            q2_cap=0,
            max_per_subject=28,
            min_masked_score=0.550,
            max_known_overlap=0.84,
            min_known_white=0.38,
            min_cells_for_root=140,
            alpha=1.16,
            cap=2.00,
            novelty="masked_objective_new_support",
        ),
        H093Spec(
            name="masked_extreme_white_c420_r140_q80",
            profile="white_extreme",
            target_group="all",
            max_routes=140,
            max_cells=420,
            max_rows=140,
            q2_cap=80,
            max_per_subject=22,
            min_masked_score=0.530,
            max_known_overlap=0.58,
            min_known_white=0.58,
            min_cells_for_root=70,
            alpha=1.25,
            cap=2.25,
            novelty="masked_extreme_new_support",
        ),
    ]


def mode_matches_profile(mode: str, profile: str) -> bool:
    if profile in {"white_large", "white_bridge", "white_extreme"}:
        return True
    if profile == "white_public_q2":
        return mode in h089mod.POSTERIOR_MODES
    if profile == "white_private":
        return mode in h089mod.PRIVATE_MODES
    if profile == "white_objective":
        return mode in h089mod.PRIVATE_MODES | h089mod.POSTERIOR_MODES
    raise ValueError(profile)


def allowed_by_profile(rec: dict[str, object], spec: H093Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not target_allowed(targets, spec.target_group):
        return False
    if float(rec["masked_latent_score"]) < spec.min_masked_score:
        return False
    if float(rec["max_known_overlap_ratio"]) > spec.max_known_overlap:
        return False
    if float(rec["known_white_rank"]) < spec.min_known_white:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.78:
        return False
    if not mode_matches_profile(str(rec["value_mode"]), spec.profile):
        return False

    head = str(rec["masked_head"])
    mode = str(rec["value_mode"])
    if spec.profile in {"white_large", "white_bridge"}:
        return bool(
            (
                head in {"white", "white_public", "white_q2"}
                and mode in h089mod.POSTERIOR_MODES
                and float(rec["posterior_delta_sum"]) <= 2.5e-6
            )
            or (
                head == "white_private"
                and mode in h089mod.PRIVATE_MODES
                and float(rec["hard_delta_sum"]) <= 2.5e-6
            )
            or (
                head == "white_objective"
                and float(rec["is_objective_route"]) > 0
                and float(rec["source_proxy_sum"]) <= 5.0e-6
            )
            or (
                head == "white"
                and float(rec["dual_pareto"]) > 0.5
                and float(rec["posterior_delta_sum"]) <= 2.5e-6
                and float(rec["hard_delta_sum"]) <= 2.5e-6
            )
        )
    if spec.profile == "white_private":
        return bool(head in {"white_private", "white"} and float(rec["hard_delta_sum"]) <= 2.0e-6)
    if spec.profile == "white_public_q2":
        return bool(
            head in {"white_public", "white_q2", "white"}
            and (float(rec["has_q2"]) > 0 or head != "white_q2")
            and float(rec["posterior_delta_sum"]) <= 3.0e-6
        )
    if spec.profile == "white_objective":
        return bool(
            head in {"white_objective", "white"}
            and float(rec["is_objective_route"]) > 0
            and float(rec["source_proxy_sum"]) <= 5.0e-6
        )
    if spec.profile == "white_extreme":
        return bool(
            float(rec["posterior_delta_sum"]) <= 6.0e-6
            and float(rec["hard_delta_sum"]) <= 6.0e-6
            and float(rec["source_proxy_sum"]) <= 8.0e-6
        )
    raise ValueError(spec.profile)


def select_actions(actions: pd.DataFrame, spec: H093Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("masked_latent_score", ascending=False).to_dict("records"):
        if not allowed_by_profile(rec, spec):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        if n_cells + int(rec["n_cells"]) > spec.max_cells:
            continue
        if q2_cells + int(rec["q2_cells"]) > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        n_cells += int(rec["n_cells"])
        q2_cells += int(rec["q2_cells"])
    return pd.DataFrame(selected)


def selected_cell_overlap(selected_cells: pd.DataFrame, ref: set[tuple[int, str]]) -> float:
    if selected_cells.empty:
        return 0.0
    cells = [(int(row), str(target)) for row, target in zip(selected_cells["row"], selected_cells["target"])]
    return float(sum(cell in ref for cell in cells) / max(len(cells), 1))


def add_h093_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    scale = float(metrics["selected_cells"]) / (250 * 7)
    refs = {name: root_cells(name) for name in ["h087", "h088", "h091", "h092"]}

    if selected_actions.empty:
        mean_masked = 0.0
        mean_head = 0.0
        mean_known = 0.0
        mean_white = 0.0
        head_mix = ""
    else:
        mean_masked = float(selected_actions["masked_latent_score"].mean())
        mean_head = float(selected_actions["masked_head_score"].mean())
        mean_known = float(selected_actions["max_known_overlap_ratio"].mean())
        mean_white = float(selected_actions["known_white_rank"].mean())
        head_mix = ";".join(f"{k}:{v}" for k, v in selected_actions["masked_head"].value_counts().sort_index().items())

    overlaps = {f"selected_cell_overlap_{name}": selected_cell_overlap(selected_cells, ref) for name, ref in refs.items()}
    max_selected_overlap = max(overlaps.values()) if overlaps else 0.0
    score = (
        310.0 * (-posterior)
        + 300.0 * (-hard)
        + 165.0 * (-source)
        + 110.0 * (-resp)
        + 0.18 * mean_masked
        + 0.12 * mean_head
        + 0.17 * mean_white
        + 0.16 * (1.0 - mean_known)
        + 0.11 * (1.0 - max_selected_overlap)
        + 0.07 * min(scale / 0.50, 1.0)
        - 0.42 * bad
        - 0.16 * max(float(metrics["mean_bad_same_rank"]) - 0.54, 0.0)
    )
    metrics.update(
        {
            "h093_score": score,
            "mean_masked_latent_score": mean_masked,
            "mean_masked_head_score": mean_head,
            "mean_action_max_known_overlap": mean_known,
            "mean_action_known_white_rank": mean_white,
            "masked_head_mix": head_mix,
            "max_selected_cell_known_overlap": max_selected_overlap,
            **overlaps,
        }
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h087mod.h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    cell = h087mod.build_cell_table()
    raw_state, raw_feature_cols = h092mod.build_raw_day_state(sample)
    route_actions = build_route_actions(sample)
    actions = route_actions.merge(raw_state.drop(columns=KEYS), on="row", how="left", validate="many_to_one")
    actions[raw_feature_cols] = actions[raw_feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    learned_actions, diag, numeric_cols, categorical_cols = fit_oof_masked_latent(actions, raw_feature_cols)

    snapshot_cols = [
        "route_id",
        "row",
        "subject_id",
        "route_name",
        "targets",
        "value_mode",
        "masked_head",
        "masked_latent_score",
        "masked_overall_oof",
        "masked_head_score",
        "known_white_rank",
        "max_known_overlap_ratio",
        "mean_known_overlap_ratio",
        "raw_transition_q",
        "posterior_delta_sum",
        "hard_delta_sum",
        "source_proxy_sum",
        "dual_pareto",
    ]
    learned_actions.head(5000)[[c for c in snapshot_cols if c in learned_actions.columns]].to_csv(
        OUT / "h093_masked_route_actions_top5000.csv",
        index=False,
    )
    diag.to_csv(OUT / "h093_latent_diagnostics.csv", index=False)
    pd.DataFrame(
        {
            "numeric_features": numeric_cols + [""] * max(0, len(categorical_cols) - len(numeric_cols)),
            "categorical_features": categorical_cols + [""] * max(0, len(numeric_cols) - len(categorical_cols)),
        }
    ).to_csv(OUT / "h093_model_feature_manifest.csv", index=False)

    candidate_rows: list[dict[str, object]] = []
    all_selected_actions: list[pd.DataFrame] = []
    all_selected_cells: list[pd.DataFrame] = []
    for spec in spec_list():
        selected_actions = select_actions(learned_actions, spec)
        if selected_actions.empty:
            continue
        h087_spec = h087mod.CandidateSpec(
            name=spec.name,
            target_group=spec.target_group if spec.target_group != "q2_route" else "all",
            value_modes=tuple(sorted(selected_actions["value_mode"].astype(str).unique())),
            max_routes=spec.max_routes,
            max_cells=spec.max_cells,
            max_rows=spec.max_rows,
            q2_cap=spec.q2_cap,
            max_per_subject=spec.max_per_subject,
            min_action_score=spec.min_masked_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h093_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update({"profile": spec.profile, "h093_novelty": spec.novelty})
        metrics = add_h093_metrics(metrics, selected_actions, selected_cells)
        metrics["min_cells_for_root"] = int(spec.min_cells_for_root)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H093 candidates")
    candidates = candidates.sort_values("h093_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h093_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h093_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h093_selected_cells.csv", index=False)

    decision_pool = candidates[candidates["selected_cells"] >= candidates["min_cells_for_root"]].copy()
    low_overlap = decision_pool[decision_pool["max_selected_cell_known_overlap"] <= 0.82].copy()
    if not low_overlap.empty:
        decision_pool = low_overlap
    if decision_pool.empty:
        decision_pool = candidates.copy()
    decision = decision_pool.sort_values("h093_score", ascending=False).iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h093_masked_lowoverlap_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h093_decision.csv", index=False)

    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    top_actions = learned_actions.head(70)[[c for c in snapshot_cols if c in learned_actions.columns]]
    report = f"""# H093 Masked Low-Overlap Support HS-JEPA

Question: can raw human day-block context predict action-grade support outside
the known H087/H088/H091/H092 selected-cell basin?

Worldview:

- H092 learned raw context well but selected mostly known support.
- H093 changes the JEPA target to masked low-overlap support, so the predictor
  must learn route-action candidates that are both locally action-grade and
  outside the current root supports.
- This is a target-representation bet, not a top-k or alpha tweak.

OOF Masked Latent Diagnostics:

{md_table(diag, n=10)}

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_masked_lowoverlap_support_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | raw context predicts new row-target support beyond known public/private basin |

Candidates:

{md_table(trimmed, n=20)}

Top Masked Route Actions:

{md_table(top_actions, n=70)}

Interpretation rule:

- If H093 improves by >= 0.001, HS-JEPA's breakthrough path is target-support
  masking: the architecture can discover new row-target action support outside
  the known public-equation basin.
- If H093 is near H057/H092 but more novel, the low-overlap latent is real but
  needs a stronger value-law solver.
- If H093 loses badly, low-overlap support is not the missing 0.53 mechanism;
  the next big bet must invert the value law/public equation rather than
  searching more route space.
"""
    (OUT / "h093_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(diag.to_string(index=False))
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
