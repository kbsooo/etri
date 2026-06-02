#!/usr/bin/env python3
"""H092: raw day-block action latent HS-JEPA.

H091 learned a strong lifestyle-action latent, but it mostly rediscovered the
H087/H088 basin. H092 removes the hand-built story layer from the context:

    context: raw sensor/app/activity day-block state + row/route structure
    target: hidden route-action/value-head quality from H085/H018/H082/H071
    decoder: route-conditioned value law selected by the learned raw latent

This is a sharper HS-JEPA test. If raw daily behavior predicts a lower-overlap
action support, the missing breakthrough is a raw human-state encoder. If it
collapses back to H087/H088, the bottleneck is not context discovery but value
translation from discovered state to probabilities.
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
OUT = HITL / "h092_raw_dayblock_action_latent_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h091mod = import_module(HITL / "h091_learned_lifestyle_action_latent_hsjepa.py", "h091mod_for_h092")
h013mod = import_module(HITL / "h013_raw_human_state_jepa_gate.py", "h013mod_for_h092")
h087mod = h091mod.h087mod
h089mod = h091mod.h089mod
h088mod = h091mod.h088mod

TARGETS = h091mod.TARGETS
KEYS = h091mod.KEYS
BASE_FILE = h091mod.BASE_FILE
HEADS = h091mod.HEADS
TOL = h087mod.TOL


@dataclass(frozen=True)
class H092Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_raw_score: float
    max_h088_overlap: float
    min_transition_q: float
    min_cells_for_root: int
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h092_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h092_raw_dayblock_latent_*_uploadsafe.csv"):
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
    return h091mod.target_allowed(targets, group)


def sum_matching(frame: pd.DataFrame, tokens: tuple[str, ...]) -> np.ndarray:
    cols = [c for c in frame.columns if all(tok in c for tok in tokens)]
    if not cols:
        return np.zeros(len(frame), dtype=np.float64)
    return frame[cols].to_numpy(dtype=np.float64).sum(axis=1)


def zscore_frame(values: pd.DataFrame) -> pd.DataFrame:
    arr = values.to_numpy(dtype=np.float64)
    mu = np.nanmean(arr, axis=0)
    sd = np.nanstd(arr, axis=0)
    sd = np.where(sd < 1.0e-9, 1.0, sd)
    z = np.nan_to_num((arr - mu) / sd, nan=0.0, posinf=0.0, neginf=0.0)
    return pd.DataFrame(z, columns=values.columns, index=values.index)


def build_raw_day_state(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    _rows, _daily, features = h013mod.build_human_state_features()
    features = features.copy()
    for key in KEYS:
        features[key] = pd.to_datetime(features[key]) if key.endswith("_date") else features[key].astype(str)
    test = features[features["split"].eq("test")].copy()
    test = test.sort_values(KEYS).reset_index(drop=True)
    sample_keys = sample[KEYS].copy()
    for key in KEYS:
        sample_keys[key] = pd.to_datetime(sample_keys[key]) if key.endswith("_date") else sample_keys[key].astype(str)
    if not test[KEYS].reset_index(drop=True).equals(sample_keys.reset_index(drop=True)):
        raise ValueError("raw feature test keys do not match sample")

    id_cols = set(KEYS + ["split", "date"] + TARGETS)
    raw_cols = [c for c in test.columns if c not in id_cols and pd.api.types.is_numeric_dtype(test[c])]
    state = test[KEYS].copy()
    state.insert(0, "row", np.arange(len(state), dtype=int))
    numeric = test[raw_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    numeric = numeric.loc[:, numeric.nunique(dropna=False) > 1]
    z = zscore_frame(numeric)

    # Compact behavior factors. They are not direct label rules; they are raw
    # context coordinates used to predict hidden route-action quality.
    semantic = pd.DataFrame(index=test.index)
    semantic["raw_phone_arousal"] = rank01(
        sum_matching(numeric, ("usage_cat_chat",))
        + 0.8 * sum_matching(numeric, ("usage_cat_call",))
        + 0.5 * sum_matching(numeric, ("usage_cat_media",))
        + 0.4 * sum_matching(numeric, ("screen_m_screen_use", "prebed"))
        + 0.3 * sum_matching(numeric, ("screen_m_screen_use", "late"))
    )
    semantic["raw_finance_pressure"] = rank01(
        sum_matching(numeric, ("usage_cat_finance",))
        + 0.6 * numeric.get("payday_25_window", pd.Series(0.0, index=numeric.index)).to_numpy(dtype=float)
        + 0.4 * numeric.get("is_month_end", pd.Series(0.0, index=numeric.index)).to_numpy(dtype=float)
    )
    semantic["raw_religion_weekend"] = rank01(
        sum_matching(numeric, ("usage_cat_religion",))
        + 0.5 * numeric.get("is_weekend", pd.Series(0.0, index=numeric.index)).to_numpy(dtype=float)
    )
    semantic["raw_work_search_load"] = rank01(
        sum_matching(numeric, ("usage_cat_work",))
        + 0.5 * sum_matching(numeric, ("usage_cat_search_news",))
    )
    semantic["raw_mobility_load"] = rank01(
        sum_matching(numeric, ("pedo_step", "sum"))
        + sum_matching(numeric, ("pedo_distance", "sum"))
        + 0.8 * sum_matching(numeric, ("gps_speed_max",))
        + 0.5 * sum_matching(numeric, ("m_activity_active",))
    )
    semantic["raw_body_load"] = rank01(
        sum_matching(numeric, ("w_hr_high_rate",))
        + 0.5 * sum_matching(numeric, ("w_hr_mean",))
        + 0.5 * sum_matching(numeric, ("pedo_burned_calories", "sum"))
    )
    semantic["raw_light_exposure"] = rank01(
        sum_matching(numeric, ("phone_light_m_light",))
        + sum_matching(numeric, ("watch_light_w_light",))
    )
    semantic["raw_home_anchor"] = rank01(
        sum_matching(numeric, ("charge_m_charging",))
        + sum_matching(numeric, ("wifi_list_len",))
        + 0.5 * sum_matching(numeric, ("ble_list_len",)),
        high=True,
    )
    semantic["raw_outdoor_social"] = rank01(
        sum_matching(numeric, ("gps_points",))
        + sum_matching(numeric, ("ambience_list_len",))
        + 0.3 * semantic["raw_mobility_load"].to_numpy(dtype=float)
    )
    semantic["raw_screen_no_mobility"] = rank01(
        semantic["raw_phone_arousal"].to_numpy(dtype=float) - semantic["raw_mobility_load"].to_numpy(dtype=float)
    )

    compact_cols = list(semantic.columns)
    compact = pd.concat([z, semantic], axis=1)
    rows: list[pd.DataFrame] = []
    for _, group in state.join(compact).sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        g = group.copy()
        vals = g[compact.columns].to_numpy(dtype=np.float64)
        prev = np.vstack([vals[0:1], vals[:-1]])
        nxt = np.vstack([vals[1:], vals[-1:]])
        med = np.nanmedian(vals, axis=0, keepdims=True)
        g["raw_prev_delta"] = np.mean(np.abs(vals - prev), axis=1)
        g["raw_next_delta"] = np.mean(np.abs(nxt - vals), axis=1)
        g["raw_two_sided_delta"] = 0.55 * g["raw_prev_delta"] + 0.45 * g["raw_next_delta"]
        g["raw_acceleration"] = np.mean(np.abs(nxt - 2.0 * vals + prev), axis=1)
        g["raw_subject_novelty"] = np.mean(np.abs(vals - med), axis=1)
        g["raw_subject_day_pos"] = np.arange(len(g), dtype=float)
        g["raw_subject_edge_prox"] = np.maximum(
            1.0 - np.minimum(g["raw_subject_day_pos"], len(g) - 1 - g["raw_subject_day_pos"]) / 4.0,
            0.0,
        )
        rows.append(g)
    state_full = pd.concat(rows, ignore_index=True).sort_values("row").reset_index(drop=True)
    state_full["raw_transition_energy"] = (
        0.32 * rank01(state_full["raw_two_sided_delta"].to_numpy())
        + 0.24 * rank01(state_full["raw_acceleration"].to_numpy())
        + 0.24 * rank01(state_full["raw_subject_novelty"].to_numpy())
        + 0.10 * state_full["raw_phone_arousal"].to_numpy(dtype=float)
        + 0.10 * state_full["raw_outdoor_social"].to_numpy(dtype=float)
    )
    state_full["raw_transition_q"] = rank01(state_full["raw_transition_energy"].to_numpy())
    raw_feature_cols = list(compact.columns) + [
        "raw_prev_delta",
        "raw_next_delta",
        "raw_two_sided_delta",
        "raw_acceleration",
        "raw_subject_novelty",
        "raw_subject_day_pos",
        "raw_subject_edge_prox",
        "raw_transition_energy",
        "raw_transition_q",
    ]
    state_full[["row", *KEYS, *raw_feature_cols]].to_csv(OUT / "h092_raw_day_state.csv", index=False)
    pd.DataFrame(
        {
            "feature": raw_feature_cols,
            "feature_type": ["raw_z_or_semantic"] * len(raw_feature_cols),
            "semantic_compact": [int(c in compact_cols) for c in raw_feature_cols],
        }
    ).to_csv(OUT / "h092_raw_feature_manifest.csv", index=False)
    return state_full[["row", *KEYS, *raw_feature_cols]], raw_feature_cols


def build_route_actions(sample: pd.DataFrame) -> pd.DataFrame:
    actions = h091mod.build_route_actions(sample)
    return h091mod.build_target_matrix(actions)


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
            n_estimators=320,
            max_depth=10,
            min_samples_leaf=6,
            max_features=0.64,
            random_state=seed,
            n_jobs=-1,
        )
    if kind == "forest":
        return RandomForestRegressor(
            n_estimators=240,
            max_depth=11,
            min_samples_leaf=7,
            max_features=0.62,
            random_state=seed,
            n_jobs=-1,
        )
    raise ValueError(kind)


def fit_oof_raw_latent(actions: pd.DataFrame, raw_feature_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    target_cols = [f"target_{head}" for head in HEADS]
    x, numeric_cols, categorical_cols = build_feature_frame(actions, raw_feature_cols)
    y = actions[target_cols].to_numpy(dtype=np.float64)
    groups = actions["subject_id"].astype(str).to_numpy()
    unique_groups = np.unique(groups)
    split = GroupKFold(n_splits=min(5, len(unique_groups)))

    seeds = [(92091, "extra"), (92092, "extra"), (92093, "forest")]
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
    for i, head in enumerate(HEADS):
        out[f"raw_{head}_oof"] = np.clip(oof[:, i], 0.0, 1.0)
        out[f"raw_{head}_full"] = np.clip(full_pred[:, i], 0.0, 1.0)
        out[f"raw_{head}"] = 0.78 * out[f"raw_{head}_oof"] + 0.22 * out[f"raw_{head}_full"]

    head_mat = out[[f"raw_{head}" for head in HEADS[:-1]]].to_numpy(dtype=float)
    head_ix = head_mat.argmax(axis=1)
    out["raw_head"] = [HEADS[i] for i in head_ix]
    out["raw_head_score"] = head_mat.max(axis=1)
    sorted_head = np.sort(head_mat, axis=1)
    out["raw_head_margin"] = sorted_head[:, -1] - sorted_head[:, -2]
    out["raw_latent_score"] = (
        0.50 * out["raw_overall"]
        + 0.18 * out["raw_head_score"]
        + 0.10 * out["raw_transition_q"]
        + 0.08 * out["assignment_rank"]
        + 0.06 * out["h082_rank"]
        + 0.04 * (1.0 - out["h088_cell_overlap_ratio"])
        + 0.04 * out["raw_subject_novelty"].pipe(rank01)
    )

    rows = []
    for i, head in enumerate(HEADS):
        target = y[:, i]
        pred = out[f"raw_{head}_oof"].to_numpy(dtype=float)
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
    return out.sort_values("raw_latent_score", ascending=False).reset_index(drop=True), diag, numeric_cols, categorical_cols


def spec_list() -> list[H092Spec]:
    return [
        H092Spec(
            name="raw_dual_broad_c1120_r190_q110",
            profile="dual_broad",
            target_group="all",
            max_routes=190,
            max_cells=1120,
            max_rows=190,
            q2_cap=110,
            max_per_subject=34,
            min_raw_score=0.620,
            max_h088_overlap=1.00,
            min_transition_q=0.00,
            min_cells_for_root=300,
            alpha=1.14,
            cap=2.05,
            novelty="raw_dayblock_predicts_dual_action_support",
        ),
        H092Spec(
            name="raw_switch_c1160_r205_q125",
            profile="head_switch",
            target_group="all",
            max_routes=205,
            max_cells=1160,
            max_rows=205,
            q2_cap=125,
            max_per_subject=36,
            min_raw_score=0.610,
            max_h088_overlap=1.00,
            min_transition_q=0.00,
            min_cells_for_root=300,
            alpha=1.18,
            cap=2.15,
            novelty="raw_dayblock_value_head_switch",
        ),
        H092Spec(
            name="raw_transition_white_c620_r165_q95",
            profile="white_rescue",
            target_group="all",
            max_routes=165,
            max_cells=620,
            max_rows=165,
            q2_cap=95,
            max_per_subject=26,
            min_raw_score=0.575,
            max_h088_overlap=0.62,
            min_transition_q=0.56,
            min_cells_for_root=140,
            alpha=1.20,
            cap=2.10,
            novelty="raw_transition_opens_low_overlap_support",
        ),
        H092Spec(
            name="raw_private_body_c850_r180_q65",
            profile="private",
            target_group="all",
            max_routes=180,
            max_cells=850,
            max_rows=180,
            q2_cap=65,
            max_per_subject=30,
            min_raw_score=0.595,
            max_h088_overlap=1.00,
            min_transition_q=0.00,
            min_cells_for_root=240,
            alpha=1.12,
            cap=1.95,
            novelty="raw_body_context_private_stable_head",
        ),
        H092Spec(
            name="raw_public_arousal_c840_r180_q120",
            profile="public",
            target_group="all",
            max_routes=180,
            max_cells=840,
            max_rows=180,
            q2_cap=120,
            max_per_subject=30,
            min_raw_score=0.595,
            max_h088_overlap=1.00,
            min_transition_q=0.46,
            min_cells_for_root=240,
            alpha=1.22,
            cap=2.20,
            novelty="raw_phone_arousal_public_head",
        ),
        H092Spec(
            name="raw_objective_mobility_c760_r170",
            profile="objective",
            target_group="objective",
            max_routes=170,
            max_cells=760,
            max_rows=170,
            q2_cap=0,
            max_per_subject=28,
            min_raw_score=0.575,
            max_h088_overlap=1.00,
            min_transition_q=0.00,
            min_cells_for_root=200,
            alpha=1.16,
            cap=1.95,
            novelty="raw_mobility_body_objective_head",
        ),
    ]


def mode_matches_profile(mode: str, profile: str) -> bool:
    if profile in {"dual_broad", "head_switch", "white_rescue"}:
        return True
    if profile == "public":
        return mode in h089mod.POSTERIOR_MODES
    if profile == "private":
        return mode in h089mod.PRIVATE_MODES
    if profile == "objective":
        return mode in h089mod.PRIVATE_MODES | h089mod.POSTERIOR_MODES
    raise ValueError(profile)


def allowed_by_profile(rec: dict[str, object], spec: H092Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not target_allowed(targets, spec.target_group):
        return False
    if float(rec["raw_latent_score"]) < spec.min_raw_score:
        return False
    if float(rec["h088_cell_overlap_ratio"]) > spec.max_h088_overlap:
        return False
    if float(rec["raw_transition_q"]) < spec.min_transition_q:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.76:
        return False
    mode = str(rec["value_mode"])
    if not mode_matches_profile(mode, spec.profile):
        return False

    head = str(rec["raw_head"])
    if spec.profile == "dual_broad":
        return bool(
            float(rec["dual_pareto"]) > 0.5
            and float(rec["posterior_delta_sum"]) <= 1.0e-6
            and float(rec["hard_delta_sum"]) <= 1.0e-6
        )
    if spec.profile == "head_switch":
        return bool(
            (head == "public" and mode in h089mod.POSTERIOR_MODES and float(rec["posterior_delta_sum"]) <= 1.0e-6)
            or (head == "private" and mode in h089mod.PRIVATE_MODES and float(rec["hard_delta_sum"]) <= 1.0e-6)
            or (head == "objective" and float(rec["is_objective_route"]) > 0 and float(rec["source_proxy_sum"]) <= 3.0e-6)
            or (head == "q2" and float(rec["has_q2"]) > 0 and float(rec["posterior_delta_sum"]) <= 2.0e-6)
        )
    if spec.profile == "white_rescue":
        return bool(
            float(rec["h088_cell_overlap_ratio"]) <= spec.max_h088_overlap
            and float(rec["h087_cell_overlap_ratio"]) <= 0.70
            and float(rec["posterior_delta_sum"]) <= 2.0e-6
            and float(rec["hard_delta_sum"]) <= 2.0e-6
        )
    if spec.profile == "private":
        return bool(head == "private" and float(rec["hard_delta_sum"]) <= 1.0e-6)
    if spec.profile == "public":
        return bool(head in {"public", "q2"} and float(rec["posterior_delta_sum"]) <= 1.0e-6)
    if spec.profile == "objective":
        return bool(
            head == "objective"
            and float(rec["is_objective_route"]) > 0
            and float(rec["source_proxy_sum"]) <= 3.0e-6
        )
    raise ValueError(spec.profile)


def select_actions(actions: pd.DataFrame, spec: H092Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("raw_latent_score", ascending=False).to_dict("records"):
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


def add_h092_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    scale = float(metrics["selected_cells"]) / (250 * 7)
    if selected_actions.empty:
        mean_raw = 0.0
        mean_head = 0.0
        mean_transition = 0.0
        mean_novelty = 0.0
        overlap88 = 0.0
        overlap87 = 0.0
        head_mix = ""
    else:
        mean_raw = float(selected_actions["raw_latent_score"].mean())
        mean_head = float(selected_actions["raw_head_score"].mean())
        mean_transition = float(selected_actions["raw_transition_q"].mean())
        mean_novelty = float(rank01(selected_actions["raw_subject_novelty"].to_numpy(dtype=float)).mean())
        overlap88 = float(selected_actions["h088_cell_overlap_ratio"].mean())
        overlap87 = float(selected_actions["h087_cell_overlap_ratio"].mean())
        head_mix = ";".join(f"{k}:{v}" for k, v in selected_actions["raw_head"].value_counts().sort_index().items())

    score = (
        350.0 * (-posterior)
        + 320.0 * (-hard)
        + 170.0 * (-source)
        + 115.0 * (-resp)
        + 0.13 * mean_raw
        + 0.10 * mean_head
        + 0.07 * mean_transition
        + 0.05 * mean_novelty
        + 0.08 * min(scale / 0.55, 1.0)
        + 0.05 * (1.0 - overlap88)
        + 0.03 * (1.0 - overlap87)
        - 0.40 * bad
        - 0.16 * max(float(metrics["mean_bad_same_rank"]) - 0.52, 0.0)
    )
    metrics.update(
        {
            "h092_score": score,
            "mean_raw_latent_score": mean_raw,
            "mean_raw_head_score": mean_head,
            "mean_raw_transition_q": mean_transition,
            "mean_raw_subject_novelty_rank": mean_novelty,
            "mean_action_h088_overlap": overlap88,
            "mean_action_h087_overlap": overlap87,
            "raw_head_mix": head_mix,
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
    raw_state, raw_feature_cols = build_raw_day_state(sample)
    route_actions = build_route_actions(sample)
    actions = route_actions.merge(raw_state.drop(columns=KEYS), on="row", how="left", validate="many_to_one")
    actions[raw_feature_cols] = actions[raw_feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    learned_actions, diag, numeric_cols, categorical_cols = fit_oof_raw_latent(actions, raw_feature_cols)
    action_snapshot_cols = [
        "route_id",
        "row",
        "subject_id",
        "route_name",
        "targets",
        "value_mode",
        "raw_head",
        "raw_latent_score",
        "raw_overall_oof",
        "raw_head_score",
        "raw_transition_q",
        "raw_phone_arousal",
        "raw_mobility_load",
        "raw_body_load",
        "h088_cell_overlap_ratio",
        "h087_cell_overlap_ratio",
        "posterior_delta_sum",
        "hard_delta_sum",
        "source_proxy_sum",
        "dual_pareto",
    ]
    learned_actions.head(5000)[[c for c in action_snapshot_cols if c in learned_actions.columns]].to_csv(
        OUT / "h092_raw_route_actions_top5000.csv",
        index=False,
    )
    diag.to_csv(OUT / "h092_latent_diagnostics.csv", index=False)
    pd.DataFrame(
        {
            "numeric_features": numeric_cols + [""] * max(0, len(categorical_cols) - len(numeric_cols)),
            "categorical_features": categorical_cols + [""] * max(0, len(numeric_cols) - len(categorical_cols)),
        }
    ).to_csv(OUT / "h092_model_feature_manifest.csv", index=False)

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
            min_action_score=spec.min_raw_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h092_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update({"profile": spec.profile, "h092_novelty": spec.novelty})
        metrics = add_h092_metrics(metrics, selected_actions, selected_cells)
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
        raise RuntimeError("no H092 candidates")
    candidates = candidates.sort_values("h092_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h092_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h092_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h092_selected_cells.csv", index=False)

    decision_pool = candidates[candidates["selected_cells"] >= candidates["min_cells_for_root"]].copy()
    low_overlap = decision_pool[decision_pool["mean_action_h088_overlap"] <= 0.80].copy()
    if not low_overlap.empty:
        decision_pool = low_overlap
    if decision_pool.empty:
        decision_pool = candidates.copy()
    decision = decision_pool.sort_values("h092_score", ascending=False).iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h092_raw_dayblock_latent_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h092_decision.csv", index=False)

    top_actions = learned_actions.head(60)[
        [
            "route_id",
            "row",
            "subject_id",
            "route_name",
            "targets",
            "value_mode",
            "raw_head",
            "raw_latent_score",
            "raw_overall_oof",
            "raw_head_score",
            "raw_transition_q",
            "raw_phone_arousal",
            "raw_mobility_load",
            "raw_body_load",
            "h088_cell_overlap_ratio",
            "h087_cell_overlap_ratio",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
            "dual_pareto",
        ]
    ]
    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    report = f"""# H092 Raw Day-Block Action Latent HS-JEPA

Question: can raw sensor/app/activity day-block context predict hidden
route-action/value-head quality without the hand-built human-story layer?

Worldview:

- H091 learned a healthy lifestyle-action latent, but it mostly selected the
  H087/H088 basin.
- H092 uses raw app/screen/charge/activity/GPS/Wi-Fi/BLE/light/heart/pedometer
  context plus within-subject day transitions.
- The target representation is action/value-head quality, not raw value
  reconstruction and not direct label prediction.

OOF Raw Latent Diagnostics:

{md_table(diag, n=10)}

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_raw_dayblock_action_latent_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | raw day-block context predicts hidden action/value-head representation before probability decoding |

Candidates:

{md_table(trimmed, n=20)}

Top Raw Route Actions:

{md_table(top_actions, n=60)}

Interpretation rule:

- If H092 improves by >= 0.001, raw human day-block state is an action-grade
  HS-JEPA context and should replace hand-built story scoring upstream.
- If H092 ties H091/H088 with high overlap, raw context is explanatory but
  still trapped in the known value-law basin.
- If low-overlap H092 loses, raw lifestyle novelty alone is not enough; the
  next breakthrough must change the value target or solve row-target
  assignment globally.
"""
    (OUT / "h092_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(diag.to_string(index=False))
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
