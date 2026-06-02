#!/usr/bin/env python3
"""H091: learned lifestyle-action latent HS-JEPA.

H089 showed that hand-scored lifestyle state mostly re-explains H088.  H090
showed that directly opening lifestyle white-space is locally unsafe.  H091
therefore changes the JEPA target:

    context: human/social lifestyle state + row/route structure
    target: hidden action/value-head quality inferred from H085/H018/H082/H071

The model is deliberately trained with subject-group OOF predictions.  A route
action is selected only if a lifestyle context encoder can predict, from other
subjects, that this context should receive an action-grade value law.

This is closer to the HS-JEPA paper claim: the architecture predicts a hidden
human-state representation before it decodes probabilities.
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
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h091_learned_lifestyle_action_latent_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h089mod = import_module(HITL / "h089_lifestyle_transition_gate_hsjepa.py", "h089mod_for_h091")
h090mod = import_module(HITL / "h090_lifestyle_white_space_hsjepa.py", "h090mod_for_h091")
h087mod = h089mod.h087mod
h088mod = h089mod.h088mod

TARGETS = h089mod.TARGETS
KEYS = h089mod.KEYS
BASE_FILE = h089mod.BASE_FILE
TOL = h087mod.TOL

HEADS = ["public", "private", "objective", "q2", "overall"]


@dataclass(frozen=True)
class H091Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_learned_score: float
    max_h088_overlap: float
    min_cells_for_root: int
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h091_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h091_learned_lifestyle_latent_*_uploadsafe.csv"):
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
    return h089mod.parse_targets(text)


def target_allowed(targets: list[str], group: str) -> bool:
    return h089mod.target_allowed(targets, group)


def build_route_actions(sample: pd.DataFrame) -> pd.DataFrame:
    state = h089mod.build_transition_state(sample)
    cell = h087mod.build_cell_table()
    route_actions = h088mod.build_dual_actions(h087mod.build_route_actions(cell))
    route_actions = h089mod.add_lifestyle_scores(route_actions, state)
    route_actions = h090mod.add_overlap_and_white_score(route_actions)
    return route_actions


def build_target_matrix(actions: pd.DataFrame) -> pd.DataFrame:
    out = actions.copy()
    out["target_public"] = (
        0.44 * out["posterior_gain_rank"]
        + 0.22 * out["source_gain_rank"]
        + 0.13 * out["resp_gain_rank"]
        + 0.10 * out["posterior_safe"]
        + 0.06 * out["bad_avoid_rank"]
        + 0.05 * out["h082_rank"]
        - 0.20 * (out["posterior_delta_sum"].astype(float) > 1.0e-6).astype(float)
        - 0.12 * (out["source_proxy_sum"].astype(float) > 3.0e-6).astype(float)
    )
    out["target_private"] = (
        0.42 * out["hard_gain_rank"]
        + 0.20 * out["dual_pareto"]
        + 0.14 * out["hard_safe"]
        + 0.10 * out["bad_avoid_rank"]
        + 0.08 * out["source_gain_rank"]
        + 0.06 * out["h082_rank"]
        - 0.24 * (out["hard_delta_sum"].astype(float) > 1.0e-6).astype(float)
        - 0.10 * (out["mean_bad_same_rank"].astype(float) > 0.72).astype(float)
    )
    out["target_objective"] = (
        0.32 * out["source_gain_rank"]
        + 0.22 * out["h082_rank"]
        + 0.14 * out["is_objective_route"]
        + 0.12 * out["hard_gain_rank"]
        + 0.10 * out["posterior_gain_rank"]
        + 0.10 * out["source_safe"]
        - 0.16 * (out["source_proxy_sum"].astype(float) > 3.0e-6).astype(float)
    )
    out["target_q2"] = (
        0.22 * out["has_q2"]
        + 0.20 * out["posterior_gain_rank"]
        + 0.18 * out["hard_gain_rank"]
        + 0.14 * out["source_gain_rank"]
        + 0.10 * out["posterior_safe"]
        + 0.08 * out["hard_safe"]
        + 0.08 * out["bad_avoid_rank"]
        - 0.14 * (out["mean_bad_same_rank"].astype(float) > 0.72).astype(float)
    )
    out["target_overall"] = (
        0.28 * out["target_public"]
        + 0.28 * out["target_private"]
        + 0.18 * out["target_objective"]
        + 0.12 * out["target_q2"]
        + 0.08 * out["assignment_rank"]
        + 0.06 * out["human_route_support_rank"]
    )
    for col in [f"target_{head}" for head in HEADS]:
        out[col] = np.clip(out[col].to_numpy(dtype=np.float64), 0.0, 1.0)
    return out


def feature_columns(actions: pd.DataFrame) -> tuple[list[str], list[str]]:
    forbidden_prefixes = (
        "posterior_",
        "hard_",
        "source_gain",
        "resp_gain",
        "dual_",
        "target_",
        "h087_",
        "h088_",
        "h089_",
        "h090_",
        "white_state",
        "bad_cos_",
    )
    forbidden_exact = {
        "route_id",
        "subject_id",
        "subject_id_state",
        "sleep_date",
        "sleep_date_state",
        "lifelog_date",
        "targets",
        "target_group_key",
        "target_indices",
        "decoder_head",
        "decoder_head_score",
        "decoder_head_margin",
        "value_law_score",
        "source_proxy_sum",
        "posterior_delta_sum",
        "hard_delta_sum",
        "resp_delta_sum",
        "mean_abs_move",
        "max_abs_move",
        "source_agree_rate",
        "source_safe",
        "hard_safe",
        "posterior_safe",
        "posterior_mode",
        "private_mode",
        "posterior_gain_pos",
        "hard_gain_pos",
        "source_gain_pos",
        "resp_gain_pos",
        "posterior_gain_rank",
        "hard_gain_rank",
        "source_gain_rank",
        "resp_gain_rank",
        "bad_avoid_rank",
        "mean_bad_same_rank",
        "mean_h085_score",
        "mean_hard_confidence",
        "mean_hard_combined",
        "mean_resp_action",
        "mean_resp_lift",
        "source_agrees_h085_rate",
    }
    candidate_numeric = []
    candidate_categorical = []
    for col in actions.columns:
        if col in forbidden_exact:
            continue
        if any(col.startswith(prefix) for prefix in forbidden_prefixes):
            continue
        if pd.api.types.is_numeric_dtype(actions[col]):
            candidate_numeric.append(col)
        elif col in {"route_name", "value_mode", "family_top", "human_best_family", "lifestyle_head"}:
            candidate_categorical.append(col)
    return candidate_numeric, candidate_categorical


def build_feature_frame(actions: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> pd.DataFrame:
    num = actions[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    cats = pd.get_dummies(actions[categorical_cols].fillna("__NA__").astype(str), prefix=categorical_cols, dtype=float)
    return pd.concat([num.reset_index(drop=True), cats.reset_index(drop=True)], axis=1)


def model_factory(seed: int, kind: str) -> object:
    if kind == "extra":
        return ExtraTreesRegressor(
            n_estimators=260,
            max_depth=9,
            min_samples_leaf=7,
            max_features=0.72,
            random_state=seed,
            n_jobs=-1,
        )
    if kind == "forest":
        return RandomForestRegressor(
            n_estimators=220,
            max_depth=10,
            min_samples_leaf=8,
            max_features=0.70,
            random_state=seed,
            n_jobs=-1,
        )
    raise ValueError(kind)


def fit_oof_latent(actions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    target_cols = [f"target_{head}" for head in HEADS]
    numeric_cols, categorical_cols = feature_columns(actions)
    x = build_feature_frame(actions, numeric_cols, categorical_cols)
    y = actions[target_cols].to_numpy(dtype=np.float64)
    groups = actions["subject_id"].astype(str).to_numpy()
    unique_groups = np.unique(groups)
    n_splits = min(5, len(unique_groups))
    split = GroupKFold(n_splits=n_splits)

    seeds = [(91091, "extra"), (91092, "extra"), (91093, "forest")]
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
        out[f"learned_{head}_oof"] = np.clip(oof[:, i], 0.0, 1.0)
        out[f"learned_{head}_full"] = np.clip(full_pred[:, i], 0.0, 1.0)
        out[f"learned_{head}"] = 0.78 * out[f"learned_{head}_oof"] + 0.22 * out[f"learned_{head}_full"]

    head_mat = out[[f"learned_{head}" for head in HEADS[:-1]]].to_numpy(dtype=float)
    head_ix = head_mat.argmax(axis=1)
    out["learned_head"] = [HEADS[i] for i in head_ix]
    out["learned_head_score"] = head_mat.max(axis=1)
    sorted_head = np.sort(head_mat, axis=1)
    out["learned_head_margin"] = sorted_head[:, -1] - sorted_head[:, -2]
    out["learned_latent_score"] = (
        0.50 * out["learned_overall"]
        + 0.20 * out["learned_head_score"]
        + 0.12 * out["human_route_support_rank"]
        + 0.08 * out["assignment_rank"]
        + 0.06 * out["white_space_rank"]
        + 0.04 * out["h082_rank"]
    )

    rows = []
    for i, head in enumerate(HEADS):
        target = y[:, i]
        pred = out[f"learned_{head}_oof"].to_numpy(dtype=float)
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
    return out.sort_values("learned_latent_score", ascending=False).reset_index(drop=True), diag, numeric_cols, categorical_cols


def spec_list() -> list[H091Spec]:
    return [
        H091Spec(
            name="learned_dual_broad_c1120_r190_q110",
            profile="dual_broad",
            target_group="all",
            max_routes=190,
            max_cells=1120,
            max_rows=190,
            q2_cap=110,
            max_per_subject=34,
            min_learned_score=0.650,
            max_h088_overlap=1.00,
            min_cells_for_root=300,
            alpha=1.14,
            cap=2.05,
            novelty="learned_lifestyle_dual_head_support",
        ),
        H091Spec(
            name="learned_switch_broad_c1180_r205_q125",
            profile="head_switch",
            target_group="all",
            max_routes=205,
            max_cells=1180,
            max_rows=205,
            q2_cap=125,
            max_per_subject=36,
            min_learned_score=0.635,
            max_h088_overlap=1.00,
            min_cells_for_root=300,
            alpha=1.18,
            cap=2.15,
            novelty="learned_value_head_switch",
        ),
        H091Spec(
            name="learned_white_rescue_c520_r150_q75",
            profile="white_rescue",
            target_group="all",
            max_routes=150,
            max_cells=520,
            max_rows=150,
            q2_cap=75,
            max_per_subject=24,
            min_learned_score=0.610,
            max_h088_overlap=0.50,
            min_cells_for_root=120,
            alpha=1.20,
            cap=2.10,
            novelty="learned_lifestyle_white_space_rescue",
        ),
        H091Spec(
            name="learned_private_c850_r180_q70",
            profile="private",
            target_group="all",
            max_routes=180,
            max_cells=850,
            max_rows=180,
            q2_cap=70,
            max_per_subject=30,
            min_learned_score=0.625,
            max_h088_overlap=1.00,
            min_cells_for_root=250,
            alpha=1.12,
            cap=1.95,
            novelty="learned_private_stable_head",
        ),
        H091Spec(
            name="learned_public_transition_c820_r175_q115",
            profile="public",
            target_group="all",
            max_routes=175,
            max_cells=820,
            max_rows=175,
            q2_cap=115,
            max_per_subject=30,
            min_learned_score=0.625,
            max_h088_overlap=1.00,
            min_cells_for_root=250,
            alpha=1.22,
            cap=2.20,
            novelty="learned_public_transition_head",
        ),
        H091Spec(
            name="learned_objective_c760_r170",
            profile="objective",
            target_group="objective",
            max_routes=170,
            max_cells=760,
            max_rows=170,
            q2_cap=0,
            max_per_subject=28,
            min_learned_score=0.610,
            max_h088_overlap=1.00,
            min_cells_for_root=200,
            alpha=1.16,
            cap=1.95,
            novelty="learned_objective_body_head",
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


def allowed_by_profile(rec: dict[str, object], spec: H091Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not target_allowed(targets, spec.target_group):
        return False
    if float(rec["learned_latent_score"]) < spec.min_learned_score:
        return False
    if float(rec["h088_cell_overlap_ratio"]) > spec.max_h088_overlap:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.76:
        return False
    mode = str(rec["value_mode"])
    if not mode_matches_profile(mode, spec.profile):
        return False

    profile = spec.profile
    head = str(rec["learned_head"])
    if profile == "dual_broad":
        return bool(
            float(rec["dual_pareto"]) > 0.5
            and float(rec["posterior_delta_sum"]) <= 1.0e-6
            and float(rec["hard_delta_sum"]) <= 1.0e-6
        )
    if profile == "head_switch":
        return bool(
            (head == "public" and mode in h089mod.POSTERIOR_MODES and float(rec["posterior_delta_sum"]) <= 1.0e-6)
            or (head == "private" and mode in h089mod.PRIVATE_MODES and float(rec["hard_delta_sum"]) <= 1.0e-6)
            or (head == "objective" and float(rec["is_objective_route"]) > 0 and float(rec["source_proxy_sum"]) <= 3.0e-6)
            or (head == "q2" and float(rec["has_q2"]) > 0 and float(rec["posterior_delta_sum"]) <= 2.0e-6)
        )
    if profile == "white_rescue":
        return bool(
            float(rec["h088_cell_overlap_ratio"]) <= 0.50
            and float(rec["h087_cell_overlap_ratio"]) <= 0.55
            and float(rec["posterior_delta_sum"]) <= 2.0e-6
            and float(rec["hard_delta_sum"]) <= 2.0e-6
        )
    if profile == "private":
        return bool(head == "private" and float(rec["hard_delta_sum"]) <= 1.0e-6)
    if profile == "public":
        return bool(head in {"public", "q2"} and float(rec["posterior_delta_sum"]) <= 1.0e-6)
    if profile == "objective":
        return bool(
            head == "objective"
            and float(rec["is_objective_route"]) > 0
            and float(rec["source_proxy_sum"]) <= 3.0e-6
        )
    raise ValueError(profile)


def select_actions(actions: pd.DataFrame, spec: H091Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("learned_latent_score", ascending=False).to_dict("records"):
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


def add_h091_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    scale = float(metrics["selected_cells"]) / (250 * 7)

    if selected_actions.empty:
        mean_learned = 0.0
        mean_head = 0.0
        overlap88 = 0.0
        overlap87 = 0.0
        head_mix = ""
    else:
        mean_learned = float(selected_actions["learned_latent_score"].mean())
        mean_head = float(selected_actions["learned_head_score"].mean())
        overlap88 = float(selected_actions["h088_cell_overlap_ratio"].mean())
        overlap87 = float(selected_actions["h087_cell_overlap_ratio"].mean())
        head_mix = ";".join(
            f"{k}:{v}" for k, v in selected_actions["learned_head"].value_counts().sort_index().items()
        )

    score = (
        350.0 * (-posterior)
        + 330.0 * (-hard)
        + 170.0 * (-source)
        + 115.0 * (-resp)
        + 0.15 * mean_learned
        + 0.10 * mean_head
        + 0.08 * min(scale / 0.55, 1.0)
        + 0.04 * (1.0 - overlap88)
        + 0.03 * (1.0 - overlap87)
        - 0.40 * bad
        - 0.16 * max(float(metrics["mean_bad_same_rank"]) - 0.52, 0.0)
    )
    metrics.update(
        {
            "h091_score": score,
            "mean_learned_latent_score": mean_learned,
            "mean_learned_head_score": mean_head,
            "mean_action_h088_overlap": overlap88,
            "mean_action_h087_overlap": overlap87,
            "learned_head_mix": head_mix,
        }
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h087mod.h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    cell = h087mod.build_cell_table()
    raw_actions = build_route_actions(sample)
    actions = build_target_matrix(raw_actions)
    learned_actions, diag, numeric_cols, categorical_cols = fit_oof_latent(actions)
    learned_actions.to_csv(OUT / "h091_learned_route_actions.csv", index=False)
    diag.to_csv(OUT / "h091_latent_diagnostics.csv", index=False)
    pd.DataFrame({"numeric_features": numeric_cols + [""] * max(0, len(categorical_cols) - len(numeric_cols)),
                  "categorical_features": categorical_cols + [""] * max(0, len(numeric_cols) - len(categorical_cols))}).to_csv(
        OUT / "h091_feature_manifest.csv", index=False
    )

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
            min_action_score=spec.min_learned_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h091_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update({"profile": spec.profile, "h091_novelty": spec.novelty})
        metrics = add_h091_metrics(metrics, selected_actions, selected_cells)
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
        raise RuntimeError("no H091 candidates")
    candidates = candidates.sort_values("h091_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h091_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h091_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h091_selected_cells.csv", index=False)

    decision_pool = candidates[candidates["selected_cells"] >= candidates["min_cells_for_root"]].copy()
    if decision_pool.empty:
        decision_pool = candidates.copy()
    decision = decision_pool.sort_values("h091_score", ascending=False).iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h091_learned_lifestyle_latent_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h091_decision.csv", index=False)

    top_actions = learned_actions.head(50)[
        [
            "route_id",
            "row",
            "subject_id",
            "route_name",
            "targets",
            "value_mode",
            "learned_head",
            "learned_latent_score",
            "learned_overall_oof",
            "learned_head_score",
            "h088_cell_overlap_ratio",
            "h087_cell_overlap_ratio",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
            "dual_pareto",
        ]
    ]
    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    report = f"""# H091 Learned Lifestyle-Action Latent HS-JEPA

Question: can a subject-held-out lifestyle context encoder predict the hidden
route/action/value-head quality that hand-scored H089/H090 could not safely
decode?

Worldview:

- H089: lifestyle context explains H088 but mostly overlaps it.
- H090: direct lifestyle white-space actions are unsafe.
- H091: learn the hidden action/value-head target from H085/H018/H082/H071
  agreement using only lifestyle context and row/route structure, then decode
  only where the learned latent and value-head safety agree.

OOF Latent Diagnostics:

{md_table(diag, n=10)}

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_learned_lifestyle_action_latent_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | lifestyle context predicts hidden action/value-head representation before probability decoding |

Candidates:

{md_table(trimmed, n=20)}

Top Learned Route Actions:

{md_table(top_actions, n=50)}

Interpretation rule:

- If H091 improves by >= 0.001, HS-JEPA v1 should include a learned
  lifestyle-action latent target before value decoding.
- If H091 ties H088/H089, the learned context is explanatory but not a
  breakthrough action target yet.
- If H091 loses badly, hand-engineered lifestyle context is insufficient and
  the next architecture must learn directly from raw sequence/log blocks.
"""
    (OUT / "h091_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(diag.to_string(index=False))
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
