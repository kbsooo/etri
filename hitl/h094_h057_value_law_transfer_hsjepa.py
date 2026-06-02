#!/usr/bin/env python3
"""H094: H057 value-law transfer HS-JEPA.

H093 weakened the low-overlap support-discovery hypothesis. H094 therefore
changes the JEPA target, not the context:

    context: raw day-block + human/social state + route/action metadata
    target: the sparse row-target value law revealed by H057 vs H042
    decoder: transfer that value law to non-H057 cells inside the known
             public/private route basin

If this wins, H057 was not only a good submission; it was a sparse sensor for a
generalizable hidden human-state value law. If it fails, the H057 law is local
and the next 0.53-scale bet needs a new support/assignment mechanism.
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
OUT = HITL / "h094_h057_value_law_transfer_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h093mod = import_module(HITL / "h093_masked_lowoverlap_support_hsjepa.py", "h093mod_for_h094")
h092mod = h093mod.h092mod
h091mod = h093mod.h091mod
h089mod = h093mod.h089mod
h087mod = h093mod.h087mod

TARGETS = h093mod.TARGETS
KEYS = h093mod.KEYS
BASE_FILE = h093mod.BASE_FILE
TOL = h087mod.TOL
VALUE_HEADS = ["h057_echo", "known_public", "known_private", "known_objective", "known_q2", "overall"]

H042_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H012_FILE = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"


@dataclass(frozen=True)
class H094Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_value_score: float
    min_echo: float
    min_known_basin: float
    max_h057_cell_overlap: float
    min_cells_for_root: int
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h094_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h094_value_law_transfer_*_uploadsafe.csv"):
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


def load_prob(name: str, sample: pd.DataFrame) -> np.ndarray:
    return h087mod.h085mod.load_sub(name, sample)[TARGETS].to_numpy(dtype=np.float64)


def support_from_file(kind: str) -> set[tuple[int, str]]:
    if kind == "h093":
        directory = HITL / "h093_masked_lowoverlap_support_hsjepa"
    elif kind == "h092":
        directory = HITL / "h092_raw_dayblock_action_latent_hsjepa"
    elif kind == "h091":
        directory = HITL / "h091_learned_lifestyle_action_latent_hsjepa"
    elif kind == "h088":
        directory = HITL / "h088_dual_state_value_gate_hsjepa"
    elif kind == "h087":
        directory = HITL / "h087_route_value_law_hsjepa"
    else:
        raise ValueError(kind)
    decision = pd.read_csv(directory / f"{kind}_decision.csv").iloc[0]
    selected = pd.read_csv(directory / f"{kind}_selected_cells.csv")
    selected = selected[selected["candidate_id"].astype(str).eq(str(decision["candidate_id"]))]
    return {(int(row), str(target)) for row, target in zip(selected["row"], selected["target"])}


def add_h057_feedback_metrics(actions: pd.DataFrame, sample: pd.DataFrame, base_prob: np.ndarray, cell: pd.DataFrame) -> pd.DataFrame:
    h042 = load_prob(H042_FILE, sample)
    h050 = load_prob(H050_FILE, sample)
    h012 = load_prob(H012_FILE, sample)

    h057_from_h042 = np.abs(base_prob - h042) > TOL
    h050_from_h042 = np.abs(h050 - h042) > TOL
    h012_from_h057 = np.abs(h012 - base_prob) > TOL
    h042_from_h012_q2 = np.abs(h042[:, TARGETS.index("Q2")] - h012[:, TARGETS.index("Q2")]) > TOL
    h057_state_rows = h057_from_h042.any(axis=1)
    h050_rows = h050_from_h042.any(axis=1)

    h057_logit_move = h087mod.logit(base_prob) - h087mod.logit(h042)
    h050_logit_move = h087mod.logit(h050) - h087mod.logit(h042)

    cell_lookup = cell.set_index(["row", "target"], drop=False)
    rows: list[dict[str, float]] = []
    for rec in actions[["row", "targets", "value_mode"]].to_dict("records"):
        row = int(rec["row"])
        targets = parse_targets(rec["targets"])
        cells = [(row, target) for target in targets]
        denom = max(len(cells), 1)
        target_ix = np.array([TARGETS.index(target) for target in targets], dtype=int)

        h057_hits = np.array([h057_from_h042[row, ix] for ix in target_ix], dtype=float) if len(target_ix) else np.array([], dtype=float)
        h050_hits = np.array([h050_from_h042[row, ix] for ix in target_ix], dtype=float) if len(target_ix) else np.array([], dtype=float)
        h012_hits = np.array([h012_from_h057[row, ix] for ix in target_ix], dtype=float) if len(target_ix) else np.array([], dtype=float)
        nonq2_rate = float(np.mean([target != "Q2" for target in targets])) if targets else 0.0

        route_cell = cell_lookup.loc[(row, targets), :].copy() if len(targets) > 1 else cell_lookup.loc[[(row, targets[0])], :].copy()
        raw_move = h087mod.value_mode_move(route_cell, str(rec["value_mode"]))
        ref_move = h057_logit_move[row, target_ix] if len(target_ix) else np.array([], dtype=float)
        ref_nonzero = np.abs(ref_move) > 1.0e-10
        if ref_nonzero.any():
            align = np.sign(raw_move[ref_nonzero]) * np.sign(ref_move[ref_nonzero]) > 0
            capture = np.minimum(np.abs(raw_move[ref_nonzero]) / (np.abs(ref_move[ref_nonzero]) + 1.0e-6), 1.8)
            h057_align = float(np.mean(align.astype(float)))
            h057_capture = float(np.mean(capture * align.astype(float)))
        else:
            h057_align = 0.5
            h057_capture = 0.0

        h050_ref = h050_logit_move[row, target_ix] if len(target_ix) else np.array([], dtype=float)
        h050_nonzero = np.abs(h050_ref) > 1.0e-10
        if h050_nonzero.any():
            h050_align = float(np.mean((np.sign(raw_move[h050_nonzero]) * np.sign(h050_ref[h050_nonzero]) > 0).astype(float)))
        else:
            h050_align = 0.5

        rows.append(
            {
                "h057_cell_overlap_ratio": float(h057_hits.sum() / denom),
                "h050_cell_overlap_ratio": float(h050_hits.sum() / denom),
                "h012_cell_overlap_ratio": float(h012_hits.sum() / denom),
                "h057_state_row": float(h057_state_rows[row]),
                "h050_state_row": float(h050_rows[row]),
                "h042_q2_seed_row": float(h042_from_h012_q2[row]),
                "h057_nonq2_route_score": float(h057_state_rows[row]) * nonq2_rate,
                "h057_value_alignment": h057_align,
                "h057_value_capture": h057_capture,
                "h050_value_alignment": h050_align,
            }
        )

    metrics = pd.DataFrame(rows)
    out = pd.concat([actions.reset_index(drop=True), metrics], axis=1)
    out["h057_teacher_target"] = np.clip(
        0.52 * out["h057_cell_overlap_ratio"]
        + 0.24 * out["h057_nonq2_route_score"]
        + 0.10 * out["h057_value_alignment"] * out["h057_state_row"]
        + 0.08 * out["h050_cell_overlap_ratio"]
        + 0.06 * out["h042_q2_seed_row"] * out["has_q2"],
        0.0,
        1.0,
    )
    out["known_basin_score"] = np.clip(
        0.28 * out["max_known_overlap_ratio"]
        + 0.18 * out["mean_known_overlap_ratio"]
        + 0.20 * out["h088_cell_overlap_ratio"]
        + 0.14 * out["h087_cell_overlap_ratio"]
        + 0.10 * out["h091_cell_overlap_ratio"]
        + 0.10 * out["h092_cell_overlap_ratio"],
        0.0,
        1.0,
    )
    out["known_public_target"] = np.clip(
        0.30 * out["known_basin_score"]
        + 0.26 * out["posterior_gain_rank"]
        + 0.16 * out["source_gain_rank"]
        + 0.12 * out["posterior_safe"]
        + 0.08 * out["h057_teacher_target"]
        + 0.08 * out["bad_avoid_rank"],
        0.0,
        1.0,
    )
    out["known_private_target"] = np.clip(
        0.30 * out["known_basin_score"]
        + 0.26 * out["hard_gain_rank"]
        + 0.16 * out["dual_pareto"]
        + 0.12 * out["hard_safe"]
        + 0.08 * out["h057_teacher_target"]
        + 0.08 * out["bad_avoid_rank"],
        0.0,
        1.0,
    )
    out["known_objective_target"] = np.clip(
        0.28 * out["known_basin_score"]
        + 0.22 * out["is_objective_route"]
        + 0.22 * out["source_gain_rank"]
        + 0.14 * out["h082_rank"]
        + 0.08 * out["source_safe"]
        + 0.06 * out["h057_teacher_target"],
        0.0,
        1.0,
    )
    out["known_q2_target"] = np.clip(
        0.28 * out["known_basin_score"]
        + 0.22 * out["has_q2"]
        + 0.20 * out["posterior_gain_rank"]
        + 0.14 * out["hard_gain_rank"]
        + 0.08 * out["h042_q2_seed_row"]
        + 0.08 * out["bad_avoid_rank"],
        0.0,
        1.0,
    )
    out["known_overall_target"] = np.clip(
        0.28 * out["h057_teacher_target"]
        + 0.22 * out["known_public_target"]
        + 0.22 * out["known_private_target"]
        + 0.12 * out["known_objective_target"]
        + 0.08 * out["known_q2_target"]
        + 0.08 * out["known_basin_score"],
        0.0,
        1.0,
    )
    return out


def feature_columns(actions: pd.DataFrame, raw_feature_cols: list[str]) -> tuple[list[str], list[str]]:
    forbidden_prefixes = (
        "target_",
        "h057_",
        "h050_",
        "h012_",
        "known_",
        "masked_",
        "raw_",
    )
    allow_raw = set(raw_feature_cols)
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
        "learned_head",
        "masked_head",
        "value_law_score",
        "dual_score",
        "source_proxy_sum",
        "posterior_delta_sum",
        "hard_delta_sum",
        "resp_delta_sum",
        "h057_teacher_target",
        "known_public_target",
        "known_private_target",
        "known_objective_target",
        "known_q2_target",
        "known_overall_target",
        "known_basin_score",
        "h088_cell_overlap_ratio",
        "h087_cell_overlap_ratio",
        "h091_cell_overlap_ratio",
        "h092_cell_overlap_ratio",
        "max_known_overlap_ratio",
        "mean_known_overlap_ratio",
        "min_known_overlap_ratio",
        "known_outside_rate",
        "known_white_rank",
    }
    categorical_allow = {"route_name", "value_mode", "family_top", "human_best_family", "lifestyle_head"}
    numeric_cols: list[str] = []
    categorical_cols: list[str] = []
    for col in actions.columns:
        if col in forbidden_exact:
            continue
        if col not in allow_raw and any(col.startswith(prefix) for prefix in forbidden_prefixes):
            continue
        if pd.api.types.is_numeric_dtype(actions[col]):
            numeric_cols.append(col)
        elif col in categorical_allow:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols


def build_feature_frame(actions: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> pd.DataFrame:
    num = actions[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    cats = pd.get_dummies(actions[categorical_cols].fillna("__NA__").astype(str), prefix=categorical_cols, dtype=float)
    return pd.concat([num.reset_index(drop=True), cats.reset_index(drop=True)], axis=1)


def model_factory(seed: int, kind: str) -> object:
    if kind == "extra":
        return ExtraTreesRegressor(
            n_estimators=140,
            max_depth=9,
            min_samples_leaf=5,
            max_features=0.66,
            random_state=seed,
            n_jobs=-1,
        )
    if kind == "forest":
        return RandomForestRegressor(
            n_estimators=110,
            max_depth=10,
            min_samples_leaf=6,
            max_features=0.64,
            random_state=seed,
            n_jobs=-1,
        )
    raise ValueError(kind)


def fit_h057_value_latent(
    actions: pd.DataFrame,
    raw_feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    target_cols = [
        "h057_teacher_target",
        "known_public_target",
        "known_private_target",
        "known_objective_target",
        "known_q2_target",
        "known_overall_target",
    ]
    numeric_cols, categorical_cols = feature_columns(actions, raw_feature_cols)
    x = build_feature_frame(actions, numeric_cols, categorical_cols)
    y = actions[target_cols].to_numpy(dtype=np.float64)
    groups = actions["subject_id"].astype(str).to_numpy()
    split = GroupKFold(n_splits=min(4, len(np.unique(groups))))
    seeds = [(94091, "extra"), (94092, "forest")]

    oof_sum = np.zeros_like(y, dtype=np.float64)
    full_sum = np.zeros_like(y, dtype=np.float64)
    for seed, kind in seeds:
        fold = np.zeros_like(y, dtype=np.float64)
        for train_idx, valid_idx in split.split(x, y, groups):
            model = model_factory(seed, kind)
            model.fit(x.iloc[train_idx], y[train_idx])
            fold[valid_idx] = np.clip(model.predict(x.iloc[valid_idx]), 0.0, 1.0)
        oof_sum += fold
        full = model_factory(seed + 100, kind)
        full.fit(x, y)
        full_sum += np.clip(full.predict(x), 0.0, 1.0)

    oof = oof_sum / len(seeds)
    full_pred = full_sum / len(seeds)
    out = actions.copy()
    for i, head in enumerate(VALUE_HEADS):
        out[f"value_{head}_oof"] = np.clip(oof[:, i], 0.0, 1.0)
        out[f"value_{head}_full"] = np.clip(full_pred[:, i], 0.0, 1.0)
        out[f"value_{head}"] = 0.78 * out[f"value_{head}_oof"] + 0.22 * out[f"value_{head}_full"]

    head_mat = out[[f"value_{head}" for head in VALUE_HEADS[:-1]]].to_numpy(dtype=float)
    head_ix = head_mat.argmax(axis=1)
    out["value_head"] = [VALUE_HEADS[i] for i in head_ix]
    out["value_head_score"] = head_mat.max(axis=1)
    sorted_head = np.sort(head_mat, axis=1)
    out["value_head_margin"] = sorted_head[:, -1] - sorted_head[:, -2]
    out["h094_latent_score"] = np.clip(
        0.38 * out["value_h057_echo"]
        + 0.26 * out["value_overall"]
        + 0.14 * out["known_basin_score"]
        + 0.08 * out["value_head_score"]
        + 0.06 * out["assignment_rank"]
        + 0.04 * out["h082_rank"]
        + 0.04 * out["bad_avoid_rank"],
        0.0,
        1.0,
    )

    rows: list[dict[str, object]] = []
    for i, head in enumerate(VALUE_HEADS):
        target = y[:, i]
        pred = out[f"value_{head}_oof"].to_numpy(dtype=float)
        rows.append(
            {
                "head": head,
                "target_mean": float(target.mean()),
                "pred_mean": float(pred.mean()),
                "pred_std": float(pred.std()),
                "spearman_oof": spearman(target, pred),
                "auc_top25_oof": safe_auc(target >= np.quantile(target, 0.75), pred),
                "auc_top10_oof": safe_auc(target >= np.quantile(target, 0.90), pred),
            }
        )
    return out.sort_values("h094_latent_score", ascending=False).reset_index(drop=True), pd.DataFrame(rows), numeric_cols, categorical_cols


def add_h094_action_score(actions: pd.DataFrame) -> pd.DataFrame:
    out = actions.copy()
    mode_public = out["value_mode"].astype(str).isin(h089mod.POSTERIOR_MODES).astype(float)
    mode_private = out["value_mode"].astype(str).isin(h089mod.PRIVATE_MODES).astype(float)
    h057_transfer = np.clip(
        out["value_h057_echo"].to_numpy(dtype=float)
        * (1.0 - 0.68 * out["h057_cell_overlap_ratio"].to_numpy(dtype=float))
        * (0.72 + 0.28 * out["known_basin_score"].to_numpy(dtype=float)),
        0.0,
        1.0,
    )
    out["h057_transfer_score"] = h057_transfer
    out["value_mode_match"] = np.maximum.reduce(
        [
            out["value_known_public"].to_numpy(dtype=float) * mode_public.to_numpy(dtype=float),
            out["value_known_private"].to_numpy(dtype=float) * mode_private.to_numpy(dtype=float),
            out["value_known_objective"].to_numpy(dtype=float) * out["is_objective_route"].to_numpy(dtype=float),
            out["value_known_q2"].to_numpy(dtype=float) * out["has_q2"].to_numpy(dtype=float),
        ]
    )
    out["h094_value_score"] = (
        0.28 * out["h057_transfer_score"]
        + 0.18 * out["h094_latent_score"]
        + 0.16 * out["known_basin_score"]
        + 0.11 * out["value_mode_match"]
        + 0.10 * out["posterior_gain_rank"]
        + 0.08 * out["hard_gain_rank"]
        + 0.05 * out["source_gain_rank"]
        + 0.04 * out["assignment_rank"]
        - 0.12 * (out["mean_bad_same_rank"].astype(float) > 0.74).astype(float)
        - 0.10 * (out["source_proxy_sum"].astype(float) > 5.0e-6).astype(float)
        - 0.08 * (out["posterior_delta_sum"].astype(float) > 4.0e-6).astype(float)
        - 0.08 * (out["hard_delta_sum"].astype(float) > 4.0e-6).astype(float)
    )
    return out.sort_values("h094_value_score", ascending=False).reset_index(drop=True)


def spec_list() -> list[H094Spec]:
    return [
        H094Spec(
            name="h057_transfer_known_basin_c1150_r220_q120",
            profile="known_basin_transfer",
            target_group="all",
            max_routes=220,
            max_cells=1150,
            max_rows=220,
            q2_cap=120,
            max_per_subject=36,
            min_value_score=0.470,
            min_echo=0.005,
            min_known_basin=0.50,
            max_h057_cell_overlap=0.05,
            min_cells_for_root=350,
            alpha=1.22,
            cap=2.15,
            novelty="h057_sparse_teacher_transfers_to_known_basin",
        ),
        H094Spec(
            name="h057_nonq2_state_transfer_c980_r210",
            profile="nonq2_state",
            target_group="nonq2",
            max_routes=210,
            max_cells=980,
            max_rows=210,
            q2_cap=0,
            max_per_subject=34,
            min_value_score=0.460,
            min_echo=0.004,
            min_known_basin=0.45,
            max_h057_cell_overlap=0.05,
            min_cells_for_root=280,
            alpha=1.24,
            cap=2.10,
            novelty="h057_nonq2_row_state_generalization",
        ),
        H094Spec(
            name="h057_public_private_bridge_c1050_r215_q110",
            profile="public_private_bridge",
            target_group="all",
            max_routes=215,
            max_cells=1050,
            max_rows=215,
            q2_cap=110,
            max_per_subject=34,
            min_value_score=0.460,
            min_echo=0.004,
            min_known_basin=0.46,
            max_h057_cell_overlap=0.08,
            min_cells_for_root=320,
            alpha=1.16,
            cap=2.02,
            novelty="h057_echo_selects_public_private_value_head",
        ),
        H094Spec(
            name="h057_objective_body_transfer_c820_r185",
            profile="objective",
            target_group="objective",
            max_routes=185,
            max_cells=820,
            max_rows=185,
            q2_cap=0,
            max_per_subject=30,
            min_value_score=0.445,
            min_echo=0.003,
            min_known_basin=0.42,
            max_h057_cell_overlap=0.06,
            min_cells_for_root=220,
            alpha=1.20,
            cap=1.95,
            novelty="h057_echo_transfers_to_objective_body_state",
        ),
        H094Spec(
            name="h057_q2_seed_reopen_c540_r160_q145",
            profile="q2_reopen",
            target_group="q2_route",
            max_routes=160,
            max_cells=540,
            max_rows=160,
            q2_cap=145,
            max_per_subject=26,
            min_value_score=0.440,
            min_echo=0.003,
            min_known_basin=0.40,
            max_h057_cell_overlap=0.05,
            min_cells_for_root=120,
            alpha=1.26,
            cap=2.25,
            novelty="h057_q2_seed_rows_imply_second_q2_route",
        ),
        H094Spec(
            name="h057_aggressive_value_transfer_c1450_r240_q150",
            profile="aggressive",
            target_group="all",
            max_routes=240,
            max_cells=1450,
            max_rows=240,
            q2_cap=150,
            max_per_subject=40,
            min_value_score=0.445,
            min_echo=0.003,
            min_known_basin=0.40,
            max_h057_cell_overlap=0.10,
            min_cells_for_root=450,
            alpha=1.34,
            cap=2.35,
            novelty="aggressive_h057_value_law_public_private_transfer",
        ),
    ]


def mode_matches_profile(mode: str, profile: str) -> bool:
    if profile in {"known_basin_transfer", "aggressive"}:
        return True
    if profile == "nonq2_state":
        return mode in h089mod.POSTERIOR_MODES | h089mod.PRIVATE_MODES
    if profile == "public_private_bridge":
        return mode in {"triad_consensus", "q_source_bridge", "hard_source_bridge", "h085_hard_bridge", "hard_q", "h085_q"}
    if profile == "objective":
        return mode in h089mod.POSTERIOR_MODES | h089mod.PRIVATE_MODES
    if profile == "q2_reopen":
        return mode in h089mod.POSTERIOR_MODES | {"hard_binary_edge", "hard_q"}
    raise ValueError(profile)


def allowed_by_profile(rec: dict[str, object], spec: H094Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not target_allowed(targets, spec.target_group):
        return False
    if float(rec["h094_value_score"]) < spec.min_value_score:
        return False
    if float(rec["h057_transfer_score"]) < spec.min_echo:
        return False
    if float(rec["known_basin_score"]) < spec.min_known_basin:
        return False
    if float(rec["h057_cell_overlap_ratio"]) > spec.max_h057_cell_overlap:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.78:
        return False
    mode = str(rec["value_mode"])
    if not mode_matches_profile(mode, spec.profile):
        return False

    if spec.profile == "known_basin_transfer":
        return bool(
            float(rec["posterior_delta_sum"]) <= 3.0e-6
            and float(rec["source_proxy_sum"]) <= 7.0e-6
        )
    if spec.profile == "nonq2_state":
        return bool(
            "Q2" not in set(targets)
            and float(rec["value_h057_echo"]) >= spec.min_echo
            and float(rec["posterior_delta_sum"]) <= 5.0e-6
        )
    if spec.profile == "public_private_bridge":
        head = str(rec["value_head"])
        return bool(
            (
                head in {"known_public", "h057_echo", "overall"}
                and mode in h089mod.POSTERIOR_MODES
                and float(rec["posterior_delta_sum"]) <= 4.0e-6
            )
            or (
                head in {"known_private", "overall"}
                and mode in h089mod.PRIVATE_MODES
                and float(rec["hard_delta_sum"]) <= 4.0e-6
            )
        )
    if spec.profile == "objective":
        return bool(
            float(rec["is_objective_route"]) > 0
            and float(rec["value_known_objective"]) >= 0.35
            and float(rec["source_proxy_sum"]) <= 8.0e-6
        )
    if spec.profile == "q2_reopen":
        return bool(
            "Q2" in set(targets)
            and float(rec["value_known_q2"]) >= 0.32
            and float(rec["posterior_delta_sum"]) <= 6.0e-6
        )
    if spec.profile == "aggressive":
        return bool(
            float(rec["posterior_delta_sum"]) <= 8.0e-6
            and float(rec["hard_delta_sum"]) <= 8.0e-6
            and float(rec["source_proxy_sum"]) <= 1.0e-5
        )
    raise ValueError(spec.profile)


def select_actions(actions: pd.DataFrame, spec: H094Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("h094_value_score", ascending=False).to_dict("records"):
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


def selected_overlap(selected_cells: pd.DataFrame, ref: set[tuple[int, str]]) -> float:
    if selected_cells.empty:
        return 0.0
    cells = [(int(row), str(target)) for row, target in zip(selected_cells["row"], selected_cells["target"])]
    return float(sum(cell in ref for cell in cells) / max(len(cells), 1))


def add_h094_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    scale = float(metrics["selected_cells"]) / (250 * 7)
    refs = {name: support_from_file(name) for name in ["h087", "h088", "h091", "h092", "h093"]}

    if selected_actions.empty:
        mean_echo = 0.0
        mean_basin = 0.0
        mean_h057_overlap = 0.0
        mean_mode_match = 0.0
        head_mix = ""
    else:
        mean_echo = float(selected_actions["h057_transfer_score"].mean())
        mean_basin = float(selected_actions["known_basin_score"].mean())
        mean_h057_overlap = float(selected_actions["h057_cell_overlap_ratio"].mean())
        mean_mode_match = float(selected_actions["value_mode_match"].mean())
        head_mix = ";".join(f"{k}:{v}" for k, v in selected_actions["value_head"].value_counts().sort_index().items())

    overlaps = {f"selected_overlap_{name}": selected_overlap(selected_cells, ref) for name, ref in refs.items()}
    score = (
        360.0 * (-posterior)
        + 260.0 * (-hard)
        + 160.0 * (-source)
        + 110.0 * (-resp)
        + 0.18 * mean_echo
        + 0.15 * mean_basin
        + 0.11 * mean_mode_match
        + 0.08 * min(scale / 0.62, 1.0)
        + 0.05 * (1.0 - mean_h057_overlap)
        - 0.42 * bad
        - 0.15 * max(float(metrics["mean_bad_same_rank"]) - 0.54, 0.0)
    )
    metrics.update(
        {
            "h094_score": score,
            "mean_h057_transfer_score": mean_echo,
            "mean_known_basin_score": mean_basin,
            "mean_h057_cell_overlap_ratio": mean_h057_overlap,
            "mean_value_mode_match": mean_mode_match,
            "value_head_mix": head_mix,
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
    route_actions = h093mod.build_route_actions(sample)
    actions = route_actions.merge(raw_state.drop(columns=KEYS), on="row", how="left", validate="many_to_one")
    actions[raw_feature_cols] = actions[raw_feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    actions = add_h057_feedback_metrics(actions, sample, base_prob, cell)
    learned_actions, diag, numeric_cols, categorical_cols = fit_h057_value_latent(actions, raw_feature_cols)
    learned_actions = add_h094_action_score(learned_actions)

    snapshot_cols = [
        "route_id",
        "row",
        "subject_id",
        "route_name",
        "targets",
        "value_mode",
        "value_head",
        "h094_value_score",
        "h057_transfer_score",
        "known_basin_score",
        "h057_cell_overlap_ratio",
        "value_h057_echo_oof",
        "value_h057_echo",
        "value_overall",
        "posterior_delta_sum",
        "hard_delta_sum",
        "source_proxy_sum",
        "dual_pareto",
    ]
    learned_actions.head(5000)[[c for c in snapshot_cols if c in learned_actions.columns]].to_csv(
        OUT / "h094_value_route_actions_top5000.csv",
        index=False,
    )
    diag.to_csv(OUT / "h094_value_latent_diagnostics.csv", index=False)
    pd.DataFrame(
        {
            "numeric_features": numeric_cols + [""] * max(0, len(categorical_cols) - len(numeric_cols)),
            "categorical_features": categorical_cols + [""] * max(0, len(numeric_cols) - len(categorical_cols)),
        }
    ).to_csv(OUT / "h094_feature_manifest.csv", index=False)

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
            min_action_score=spec.min_value_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h094_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update(
            {
                "profile": spec.profile,
                "h094_novelty": spec.novelty,
                "min_cells_for_root": int(spec.min_cells_for_root),
            }
        )
        metrics = add_h094_metrics(metrics, selected_actions, selected_cells)
        candidate_rows.append(metrics)

        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H094 candidates")
    candidates = candidates.sort_values("h094_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h094_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h094_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h094_selected_cells.csv", index=False)

    decision_pool = candidates[candidates["selected_cells"] >= candidates["min_cells_for_root"]].copy()
    transfer_pool = decision_pool[decision_pool["mean_h057_cell_overlap_ratio"] <= 0.18].copy()
    if not transfer_pool.empty:
        decision_pool = transfer_pool
    if decision_pool.empty:
        decision_pool = candidates.copy()
    decision = decision_pool.sort_values("h094_score", ascending=False).iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h094_value_law_transfer_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h094_decision.csv", index=False)

    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    top_actions = learned_actions.head(60)[[c for c in snapshot_cols if c in learned_actions.columns]]
    report = f"""# H094 H057 Value-Law Transfer HS-JEPA

Question: can the sparse H057 vs H042 public feedback be used as a teacher for a
generalizable hidden value-law, then transferred to non-H057 cells inside the
known public/private support basin?

Worldview:

- H093 made low-overlap support discovery look too sparse.
- H057 is reinterpreted as a sparse public sensor: Q2 seed rows imply a
  non-Q2 row-state value law.
- The JEPA target is not label prediction. It is the hidden H057 value-state
  representation predicted from raw day-block, human/social state, and route
  context.
- The decoder avoids directly replaying H057 cells and transfers the predicted
  value law into known H087/H088/H091/H092 support.

OOF Value Latent Diagnostics:

{md_table(diag, n=10)}

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_h057_value_law_transfer_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | H057 is a sparse teacher for a transferable hidden value law |

Candidates:

{md_table(trimmed, n=20)}

Top H094 Route Actions:

{md_table(top_actions, n=60)}

Interpretation rule:

- If H094 improves by >= 0.001, HS-JEPA should treat public-LB feedback as a
  sparse teacher and learn a context-to-value-law latent before decoding.
- If H094 is close to H057/H087 but not better, the H057 law is real but already
  saturated locally.
- If H094 loses badly, H057 is not a generalizable value law; it is a local
  row-target assignment event, and the next big bet must solve support/route
  assignment rather than value transfer.
"""
    (OUT / "h094_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(diag.to_string(index=False))
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
