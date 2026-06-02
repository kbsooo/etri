#!/usr/bin/env python3
"""H079: forced episode-state HS-JEPA.

H078 tried to expand H077 hard-tail conflicts with public-action-positive
companion cells. The companion set almost disappeared. That can mean either:

1. hard-tail is truly sparse, or
2. the public-action sensor is itself too cell-local and cannot see the whole
   human state.

H079 deliberately tests the second possibility. It treats H077 rows as visible
anchors of a bad-night / recovery episode and propagates a correction field to
same-row companions and, in some variants, adjacent subject-days.

This is not a safe blend. It is a falsification test for episode-level human
state propagation.
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


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
H077_OUT = HITL / "h077_hardtail_conflict_route_jepa"
OUT = HITL / "h079_forced_episode_state_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TOL = 1.0e-12


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H077MOD = import_module(HITL / "h077_hardtail_conflict_route_jepa.py", "h077mod_for_h079")
H071MOD = H077MOD.H071MOD
H074MOD = H077MOD.H074MOD


@dataclass(frozen=True)
class H079Spec:
    name: str
    source_candidate: str
    seed_targets: str
    neighbor_targets: str
    max_seed_rows: int
    seed_alpha: float
    neighbor_alpha: float
    neighbor_radius: int
    max_per_subject: int
    keep_seed_hardtail: bool
    q2_companion: bool


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H071MOD.rank01(np.asarray(values, dtype=np.float64), high=high)


def logit(x: np.ndarray) -> np.ndarray:
    return H071MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H071MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H071MOD.bce(prob, q)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H071MOD.clip_prob(x)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h079_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h079_forced_episode_*_uploadsafe.csv"):
        path.unlink()


def load_h077_cells() -> pd.DataFrame:
    path = H077_OUT / "h077_selected_cells.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def candidate_specs() -> list[H079Spec]:
    top16 = "h077_conflict_cell_top16_123f6665"
    top8 = "h077_conflict_cell_top8_d68f58f3"
    mixed5 = "h077_monster_mixed_top5_38bd8eb7"
    return [
        H079Spec("top16_seed_fullrow_a035", top16, "all", "none", 15, 0.35, 0.00, 0, 5, True, True),
        H079Spec("top16_seed_fullrow_a060", top16, "all", "none", 15, 0.60, 0.00, 0, 5, True, True),
        H079Spec("top16_seed_nonq2_a055", top16, "nonq2", "none", 15, 0.55, 0.00, 0, 5, True, False),
        H079Spec("top16_seed_stage_a075", top16, "stage", "none", 15, 0.75, 0.00, 0, 5, True, False),
        H079Spec("top16_episode_stage_n015", top16, "stage", "stage", 15, 0.55, 0.15, 1, 5, True, False),
        H079Spec("top16_episode_nonq2_n020", top16, "nonq2", "nonq2", 15, 0.45, 0.20, 1, 5, True, False),
        H079Spec("top16_episode_all_n012", top16, "all", "all", 15, 0.32, 0.12, 1, 5, True, True),
        H079Spec("top8_seed_fullrow_a060", top8, "all", "none", 8, 0.60, 0.00, 0, 4, True, True),
        H079Spec("top8_episode_all_n018", top8, "all", "all", 8, 0.42, 0.18, 1, 4, True, True),
        H079Spec("mixed5_seed_fullrow_a070", mixed5, "all", "none", 5, 0.70, 0.00, 0, 3, True, True),
        H079Spec("mixed5_episode_nonq2_n025", mixed5, "nonq2", "nonq2", 5, 0.55, 0.25, 1, 3, True, False),
    ]


def target_set(name: str) -> list[str]:
    if name == "none":
        return []
    if name == "all":
        return list(TARGETS)
    if name == "nonq2":
        return list(NON_Q2)
    if name == "stage":
        return list(S_TARGETS)
    if name == "qstage":
        return ["Q2", "S1", "S2", "S3", "S4"]
    raise ValueError(name)


def seed_rows_for(h077_cells: pd.DataFrame, spec: H079Spec) -> pd.DataFrame:
    src = h077_cells[h077_cells["candidate_id"].astype(str).eq(spec.source_candidate)].copy()
    if src.empty:
        return src
    rows = (
        src.groupby(["row", "subject_id", "sleep_date"], as_index=False)
        .agg(
            seed_cells=("flat_index", "nunique"),
            seed_targets=("target", lambda x: ",".join(sorted(set(map(str, x))))),
            seed_public_gain=("h076_public_action_gain", "sum"),
            seed_value_loss=("h076_value_gain", lambda x: -float(np.asarray(x, dtype=float).sum())),
            seed_bad_same=("h074_bad_same_rank", "mean"),
            seed_bad_opp=("h074_bad_opp_rank", "mean"),
            seed_shortcut=("latent_shortcut_energy", "mean"),
            seed_outside_h069=("outside_h069_cell", "sum"),
        )
        .sort_values(["seed_public_gain", "seed_cells"], ascending=[False, False])
        .reset_index(drop=True)
    )
    selected = []
    subject_counts: dict[str, int] = {}
    for rec in rows.to_dict("records"):
        subject = str(rec["subject_id"])
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        if len(selected) >= spec.max_seed_rows:
            break
    out = pd.DataFrame(selected)
    if not out.empty:
        out["seed_row_rank"] = rank01(out["seed_public_gain"].to_numpy())
    return out


def neighbor_rows(sample: pd.DataFrame, seed_rows: pd.DataFrame, radius: int) -> pd.DataFrame:
    if radius <= 0 or seed_rows.empty:
        return seed_rows.iloc[0:0].copy()
    sample_order = sample.reset_index().rename(columns={"index": "row"})
    sample_order["sleep_dt"] = pd.to_datetime(sample_order["sleep_date"])
    rows = []
    seed_set = set(seed_rows["row"].astype(int).tolist())
    for subject, group in sample_order.sort_values(["subject_id", "sleep_dt"]).groupby("subject_id", sort=False):
        records = group.to_dict("records")
        pos_by_row = {int(rec["row"]): idx for idx, rec in enumerate(records)}
        for seed_row in sorted(seed_set.intersection(pos_by_row.keys())):
            seed_pos = pos_by_row[seed_row]
            for offset in range(-radius, radius + 1):
                if offset == 0:
                    continue
                pos = seed_pos + offset
                if 0 <= pos < len(records):
                    rec = records[pos].copy()
                    rec["anchor_seed_row"] = seed_row
                    rec["episode_offset"] = offset
                    rows.append(rec)
    if not rows:
        return seed_rows.iloc[0:0].copy()
    out = pd.DataFrame(rows).drop_duplicates(["row", "anchor_seed_row", "episode_offset"])
    out = out[~out["row"].astype(int).isin(seed_set)].copy()
    return out


def seed_cell_values(h077_cells: pd.DataFrame, spec: H079Spec) -> pd.DataFrame:
    src = h077_cells[h077_cells["candidate_id"].astype(str).eq(spec.source_candidate)].copy()
    if src.empty or not spec.keep_seed_hardtail:
        return src.iloc[0:0].copy()
    src = src.sort_values(["h076_public_action_gain", "h076_value_gain"], ascending=[False, True])
    src = src.drop_duplicates("flat_index", keep="first").reset_index(drop=True)
    src["h079_role"] = "seed_hardtail"
    src["h079_new_prob"] = src["h076_new_prob"].to_numpy(dtype=np.float64)
    src["h079_alpha"] = 1.0
    return src


def add_q061_move(
    rows: pd.DataFrame,
    role: str,
    targets: list[str],
    alpha: float,
    mats: dict[str, np.ndarray],
) -> pd.DataFrame:
    if rows.empty or not targets or alpha <= 0:
        return pd.DataFrame()
    records = []
    target_to_ix = {target: i for i, target in enumerate(TARGETS)}
    h057 = mats["h057"]
    q061 = mats["q061"]
    for row in rows["row"].astype(int).tolist():
        for target in targets:
            tidx = target_to_ix[target]
            base = float(h057[row, tidx])
            q = float(q061[row, tidx])
            new_prob = float(sigmoid(logit(np.array([base])) + alpha * (logit(np.array([q])) - logit(np.array([base]))))[0])
            records.append(
                {
                    "row": row,
                    "target": target,
                    "target_index": tidx,
                    "flat_index": row * len(TARGETS) + tidx,
                    "h057_prob": base,
                    "q061": q,
                    "h079_role": role,
                    "h079_new_prob": new_prob,
                    "h079_alpha": alpha,
                }
            )
    return pd.DataFrame(records)


def select_cells(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    h077_cells: pd.DataFrame,
    spec: H079Spec,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_rows = seed_rows_for(h077_cells, spec)
    if seed_rows.empty:
        return seed_rows, seed_rows.iloc[0:0].copy(), pd.DataFrame()
    seed_targets = target_set(spec.seed_targets)
    if not spec.q2_companion:
        seed_targets = [target for target in seed_targets if target != "Q2"]
    neighbor_targets = target_set(spec.neighbor_targets)
    if not spec.q2_companion:
        neighbor_targets = [target for target in neighbor_targets if target != "Q2"]

    hardtail = seed_cell_values(h077_cells, spec)
    companion = add_q061_move(seed_rows, "seed_q061_companion", seed_targets, spec.seed_alpha, mats)
    neighbors = neighbor_rows(sample, seed_rows, spec.neighbor_radius)
    neighbor_moves = add_q061_move(neighbors, "episode_neighbor_q061", neighbor_targets, spec.neighbor_alpha, mats)
    cell_sel = pd.concat([hardtail, companion, neighbor_moves], ignore_index=True, sort=False)
    if cell_sel.empty:
        return seed_rows, neighbors, cell_sel
    role_priority = {"seed_hardtail": 3, "seed_q061_companion": 2, "episode_neighbor_q061": 1}
    cell_sel["h079_role_priority"] = cell_sel["h079_role"].map(role_priority).fillna(0).astype(int)
    # Keep hard-tail values over companion q061 values on duplicated seed cells.
    cell_sel = (
        cell_sel.sort_values(["flat_index", "h079_role_priority"], ascending=[True, False])
        .drop_duplicates("flat_index", keep="first")
        .sort_values(["h079_role_priority", "row", "target_index"], ascending=[False, True, True])
        .reset_index(drop=True)
    )
    return seed_rows, neighbors, cell_sel


def evaluate(
    prob: np.ndarray,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    seed_rows: pd.DataFrame,
    neighbors: pd.DataFrame,
    cell_sel: pd.DataFrame,
    spec: H079Spec,
) -> dict[str, object]:
    h057 = mats["h057"]
    q061 = mats["q061"]
    changed = np.abs(prob - h057) > TOL
    x = (bce(prob, q061) - bce(h057, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (logit(prob) - logit(h057)).reshape(-1)
    bad_cos = {f"bad_cos_{H074MOD.safe_stem(name)}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    role_counts = cell_sel["h079_role"].value_counts().to_dict() if len(cell_sel) else {}
    target_counts = cell_sel["target"].value_counts().to_dict() if len(cell_sel) else {}
    seed_set = set(seed_rows["row"].astype(int).tolist()) if len(seed_rows) else set()
    changed_rows = set(np.where(changed.any(axis=1))[0].astype(int).tolist())
    meta: dict[str, object] = {
        "candidate_id": "",
        "spec_name": spec.name,
        "source_candidate": spec.source_candidate,
        "seed_targets": spec.seed_targets,
        "neighbor_targets": spec.neighbor_targets,
        "max_seed_rows": spec.max_seed_rows,
        "seed_alpha": spec.seed_alpha,
        "neighbor_alpha": spec.neighbor_alpha,
        "neighbor_radius": spec.neighbor_radius,
        "max_per_subject": spec.max_per_subject,
        "keep_seed_hardtail": spec.keep_seed_hardtail,
        "q2_companion": spec.q2_companion,
        "seed_rows": int(len(seed_rows)),
        "neighbor_rows": int(neighbors["row"].nunique()) if len(neighbors) else 0,
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(len(changed_rows)),
        "changed_seed_rows": int(len(changed_rows.intersection(seed_set))),
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_abs_prob_move_vs_h057": float(np.abs(prob - h057).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(prob - h057).max()),
        "mean_seed_public_gain": float(seed_rows["seed_public_gain"].mean()) if len(seed_rows) else 0.0,
        "sum_seed_public_gain": float(seed_rows["seed_public_gain"].sum()) if len(seed_rows) else 0.0,
        "mean_seed_bad_same": float(seed_rows["seed_bad_same"].mean()) if len(seed_rows) else 1.0,
        "mean_seed_bad_opp": float(seed_rows["seed_bad_opp"].mean()) if len(seed_rows) else 0.0,
        "mean_seed_shortcut": float(seed_rows["seed_shortcut"].mean()) if len(seed_rows) else 1.0,
        "selected_subjects": int(seed_rows["subject_id"].nunique()) if len(seed_rows) else 0,
        "selected_rows": ",".join(map(str, sorted(changed_rows))),
        "seed_row_list": ",".join(map(str, sorted(seed_set))),
        "role_templates": ";".join(f"{k}:{v}" for k, v in sorted(role_counts.items())),
        "target_templates": ";".join(f"{k}:{v}" for k, v in sorted(target_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return meta


def apply_candidate(
    spec: H079Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    h077_cells: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_rows, neighbors, cell_sel = select_cells(sample, mats, h077_cells, spec)
    prob = mats["h057"].copy()
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = float(rec["h079_new_prob"])
    prob = clip_prob(prob)
    meta = evaluate(prob, sample, mats, beta, bad_vecs, seed_rows, neighbors, cell_sel, spec)
    return prob, meta, seed_rows, neighbors, cell_sel


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    h077_cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seed_diag = []
    neighbor_diag = []
    cell_diag = []
    seen: set[str] = set()
    for spec in candidate_specs():
        prob, meta, seed_rows, neighbors, cell_sel = apply_candidate(spec, sample, mats, beta, bad_vecs, h077_cells)
        if meta["changed_cells_vs_h057"] <= 0:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h079_{spec.name}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
        if len(seed_rows):
            seed_diag.append(seed_rows.assign(candidate_id=cid))
        if len(neighbors):
            neighbor_diag.append(neighbors.assign(candidate_id=cid))
        if len(cell_sel):
            cell_diag.append(cell_sel.assign(candidate_id=cid))

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H079 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["scale_rank"] = rank01(np.minimum(cand["changed_cells_vs_h057"].to_numpy(), 160))
    cand["episode_rank"] = rank01(cand["neighbor_rows"].to_numpy() + cand["seed_rows"].to_numpy())
    cand["posterior_violation"] = np.maximum(cand["posterior_delta_vs_h057"].to_numpy(), 0.0)
    cand["h079_score"] = (
        0.24 * cand["action_rank"]
        + 0.16 * cand["responsibility_rank"]
        + 0.12 * cand["posterior_rank"]
        + 0.11 * cand["bad_avoid_rank"]
        + 0.11 * cand["scale_rank"]
        + 0.09 * cand["episode_rank"]
        + 0.07 * rank01(cand["sum_seed_public_gain"].to_numpy())
        + 0.05 * rank01(-cand["mean_seed_shortcut"].to_numpy())
        - 0.10 * (cand["max_abs_prob_move_vs_h057"] > 0.25).astype(float)
        - 0.06 * cand["posterior_violation"].clip(0, 0.01) / 0.01
    )
    cand = cand.sort_values(["h079_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    seed_all = pd.concat(seed_diag, ignore_index=True) if seed_diag else pd.DataFrame()
    neighbor_all = pd.concat(neighbor_diag, ignore_index=True) if neighbor_diag else pd.DataFrame()
    cell_all = pd.concat(cell_diag, ignore_index=True) if cell_diag else pd.DataFrame()
    return cand, probs, seed_all, neighbor_all, cell_all


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    cand: pd.DataFrame,
    seed_diag: pd.DataFrame,
    neighbor_diag: pd.DataFrame,
    cell_diag: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    cell_cols = [
        "candidate_id",
        "row",
        "target",
        "h079_role",
        "h079_alpha",
        "h057_prob",
        "q061",
        "h076_new_prob",
        "h079_new_prob",
    ]
    parts = [
        "# H079 Forced Episode-State HS-JEPA",
        "",
        "Question: can H077 hard-tail anchors be the visible part of a whole-row or adjacent-day human episode?",
        "",
        "Design:",
        "",
        "- preserve H077 hard-tail seed cells;",
        "- force q061-style companion movement on same-row targets;",
        "- optionally propagate a damped field to adjacent subject-days;",
        "- interpret public movement as evidence for or against episode-level hidden state.",
        "",
        "Candidates:",
        "",
        md_table(cand, 30),
        "",
        "Seed rows:",
        "",
        md_table(seed_diag.head(80), 80) if len(seed_diag) else "(none)",
        "",
        "Neighbor rows:",
        "",
        md_table(neighbor_diag.head(80), 80) if len(neighbor_diag) else "(none)",
        "",
        "Selected cells:",
        "",
        md_table(cell_diag[[c for c in cell_cols if c in cell_diag.columns]].head(140), 140) if len(cell_diag) else "(none)",
        "",
        "Decision:",
        "",
        md_table(decision),
    ]
    (OUT / "h079_report.md").write_text("\n".join(parts))


def main() -> None:
    cleanup_previous_outputs()
    sample, _latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    h077_cells = load_h077_cells()
    cand, probs, seed_diag, neighbor_diag, cell_diag = candidate_sweep(sample, mats, beta, bad_vecs, h077_cells)

    bigbet = cand[
        (cand["public_action_pred_delta_vs_h057"] <= -0.0012)
        & (cand["changed_cells_vs_h057"] >= 45)
        & (cand["max_positive_bad_cosine"] <= 0.012)
        & (cand["posterior_delta_vs_h057"] <= 0.0025)
    ].sort_values(["public_action_pred_delta_vs_h057", "h079_score"], ascending=[True, False])
    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        decision_name = "promote_forced_episode_state_bigbet"
        worldview = "H077 hard-tail anchors are visible cells of a same-row/episode human state"
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_forced_episode_state_diagnostic"
        worldview = "forced episode state did not clear the big-bet gate; use as falsification sensor only"

    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h079_forced_episode_{digest}_uploadsafe.csv"
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
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    cand.to_csv(OUT / "h079_candidate_scores.csv", index=False)
    seed_diag.to_csv(OUT / "h079_seed_rows.csv", index=False)
    neighbor_diag.to_csv(OUT / "h079_neighbor_rows.csv", index=False)
    cell_diag.to_csv(OUT / "h079_selected_cells.csv", index=False)
    decision.to_csv(OUT / "h079_decision.csv", index=False)
    write_report(cand, seed_diag, neighbor_diag, cell_diag, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "decision",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "seed_rows",
                "neighbor_rows",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "max_positive_bad_cosine",
                "max_abs_prob_move_vs_h057",
                "role_templates",
                "target_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
