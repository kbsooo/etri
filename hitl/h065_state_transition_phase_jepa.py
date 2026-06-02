#!/usr/bin/env python3
"""H065: State-transition phase HS-JEPA.

H057 validated a compact 45-row full non-Q2 human-state vector. H059 then tried
to spread that same vector to same-subject temporal neighbors, which is a broad
episode-copy worldview.

H065 tests the opposite: nearby rows may be *transition phases*, not copies.
Rows before and after a validated seed can require different target routes. The
context is the H064 contrastive state graph; the target representation is the
H061 post-H057 posterior; the action is phase-specific non-Q2 movement with Q2
frozen.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h065_state_transition_phase_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
NON_Q2 = [t for t in TARGETS if t != "Q2"]
EPS = 1.0e-6

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H062 = "submission_h062_h057seed_rowstate_expand_23beb8eb_uploadsafe.csv"
H063 = "submission_h063_humancontext_seed_2c748a8e_uploadsafe.csv"
H064 = "submission_h064_contrastive_state_graph_d09a5363_uploadsafe.csv"


@dataclass(frozen=True)
class PhaseSpec:
    family: str
    k_rows: int
    alpha: float
    mode: str
    target_rule: str
    max_per_subject: int
    max_abs_seed_distance: int


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    return out


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = ROOT / name if not Path(name).is_absolute() else Path(name)
    df = key_frame(pd.read_csv(path)).sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def support_rows_by_diff(a: np.ndarray, b: np.ndarray, targets: list[str]) -> np.ndarray:
    ix = [TARGETS.index(t) for t in targets]
    changed = np.abs(a[:, ix] - b[:, ix]) > 1.0e-12
    return np.where(changed.any(axis=1))[0]


def changed_rows(path: str, base_prob: np.ndarray, sample: pd.DataFrame) -> set[int]:
    root_path = ROOT / path
    if not root_path.exists():
        return set()
    prob = load_sub(root_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return set(np.where((np.abs(prob - base_prob) > 1.0e-12).any(axis=1))[0].tolist())


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def phase_offsets(sample: pd.DataFrame, seed_rows: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seed_set = set(seed_rows.tolist())
    for _, sub in sample.reset_index().groupby("subject_id", sort=False):
        idx = sub["index"].to_numpy(dtype=int)
        subject_seeds = np.array([r for r in seed_rows if r in set(idx.tolist())], dtype=int)
        for row in idx:
            if len(subject_seeds) == 0:
                nearest = -1
                signed = 999
            else:
                nearest = int(min(subject_seeds, key=lambda s: (abs(row - s), s)))
                signed = int(row - nearest)
            if row in seed_set:
                phase = "seed"
            elif signed < 0:
                phase = "pre"
            elif signed > 0:
                phase = "post"
            else:
                phase = "none"
            rows.append(
                {
                    "row": row,
                    "nearest_seed_row": nearest,
                    "signed_seed_offset": signed,
                    "abs_seed_distance": abs(signed) if abs(signed) < 900 else 999,
                    "phase": phase,
                    "phase_near": float(phase in {"pre", "post"} and abs(signed) <= 3),
                }
            )
    return pd.DataFrame(rows).sort_values("row").reset_index(drop=True)


def rank_pct(values: pd.Series) -> pd.Series:
    return values.astype(float).rank(method="average", pct=True)


def phase_target_weights(row_scores: pd.DataFrame) -> pd.DataFrame:
    gain_cols = [f"{t}_gain" for t in NON_Q2]
    pool = row_scores[
        (row_scores["is_h057_seed"] == 0)
        & (row_scores["is_h050_null"] == 0)
        & (row_scores["phase"].isin(["pre", "post"]))
        & (row_scores["abs_seed_distance"] <= 3)
        & ((row_scores["h062_changed_row"] == 1) | (row_scores["h063_changed_row"] == 1))
    ].copy()
    rows = []
    for phase in ["pre", "post"]:
        ph = pool[pool["phase"] == phase]
        if ph.empty:
            means = pd.Series({col: 1.0 for col in gain_cols})
        else:
            means = ph[gain_cols].mean().clip(lower=0.0)
            if float(means.max()) <= 0:
                means = pd.Series({col: 1.0 for col in gain_cols})
        weights = means / max(float(means.max()), EPS)
        order = weights.sort_values(ascending=False).index.tolist()
        for col in gain_cols:
            target = col.replace("_gain", "")
            rows.append(
                {
                    "phase": phase,
                    "target": target,
                    "mean_gain": float(means[col]),
                    "phase_weight": float(weights[col]),
                    "rank": int(order.index(col) + 1),
                    "in_top3": int(col in order[:3]),
                    "in_top4": int(col in order[:4]),
                    "training_rows": int(len(ph)),
                }
            )
    return pd.DataFrame(rows)


def build_row_scores(sample: pd.DataFrame, h042: np.ndarray, h057: np.ndarray, q061: np.ndarray) -> pd.DataFrame:
    h064_scores = pd.read_csv(HITL / "h064_contrastive_state_graph_jepa" / "h064_row_scores.csv")
    h064_scores = key_frame(h064_scores)
    seed_rows = support_rows_by_diff(h057, h042, NON_Q2)
    offsets = phase_offsets(sample, seed_rows)
    rows = h064_scores.merge(offsets, on="row", how="left", validate="one_to_one")

    h062_rows = changed_rows(H062, h057, sample)
    h063_rows = changed_rows(H063, h057, sample)
    h064_rows = changed_rows(H064, h057, sample)
    rows["h062_changed_row"] = rows["row"].isin(h062_rows).astype(int)
    rows["h063_changed_row"] = rows["row"].isin(h063_rows).astype(int)
    rows["h064_changed_row"] = rows["row"].isin(h064_rows).astype(int)

    gain_cols = [f"{t}_gain" for t in NON_Q2]
    weights = phase_target_weights(rows)
    route_score = np.zeros(len(rows), dtype=np.float64)
    for i, rec in rows.iterrows():
        phase = str(rec["phase"])
        if phase not in {"pre", "post"}:
            continue
        phw = weights[weights["phase"] == phase].set_index("target")["phase_weight"].to_dict()
        route_score[i] = sum(max(float(rec[f"{t}_gain"]), 0.0) * float(phw.get(t, 0.0)) for t in NON_Q2)
    rows["phase_route_gain"] = route_score
    rows["phase_route_rank"] = rank_pct(rows["phase_route_gain"])
    rows["h064_rank"] = rank_pct(rows["h064_row_score"])
    rows["graph_rank"] = rank_pct(rows["graph_consensus"])
    rows["contrast_rank"] = rank_pct(rows["contrast_consensus"])
    rows["gain_rank2"] = rank_pct(rows["row_gain_to_q061_nonq2"])
    rows["h065_row_score"] = (
        0.24 * rows["h064_rank"]
        + 0.18 * rows["graph_rank"]
        + 0.18 * rows["contrast_rank"]
        + 0.14 * rows["gain_rank2"]
        + 0.14 * rows["phase_route_rank"]
        + 0.08 * rows["h062_changed_row"]
        + 0.10 * rows["h063_changed_row"]
        + 0.09 * rows["h064_changed_row"]
        + 0.07 * rows["phase_near"]
        - 0.50 * rows["is_h050_null"]
        - 0.45 * rows["is_h057_seed"]
    )
    rows["positive_route_targets"] = (rows[gain_cols] > 0).sum(axis=1)
    return rows.sort_values("h065_row_score", ascending=False).reset_index(drop=True)


def select_rows(row_scores: pd.DataFrame, spec: PhaseSpec) -> pd.DataFrame:
    df = row_scores.copy()
    df = df[(df["is_h057_seed"] == 0) & (df["is_h050_null"] == 0)]
    if spec.family == "phase_near_union":
        df = df[(df["abs_seed_distance"] <= spec.max_abs_seed_distance) & (df["phase"].isin(["pre", "post"]))]
        df = df[(df["h062_changed_row"] == 1) | (df["h063_changed_row"] == 1) | (df["h064_changed_row"] == 1)]
    elif spec.family == "phase_h064_core":
        df = df[
            (df["h064_changed_row"] == 1)
            & (df["phase"].isin(["pre", "post"]))
            & (df["abs_seed_distance"] <= spec.max_abs_seed_distance)
        ]
    elif spec.family == "phase_graph_near":
        df = df[(df["abs_seed_distance"] <= spec.max_abs_seed_distance) & (df["phase"].isin(["pre", "post"]))]
        cutoff = df["h064_row_score"].quantile(0.55) if len(df) else np.inf
        df = df[df["h064_row_score"] >= cutoff]
    elif spec.family == "phase_far_control":
        df = df[(df["abs_seed_distance"] > 3) & (df["phase"].isin(["pre", "post"]))]
        df = df[(df["h062_changed_row"] == 1) | (df["h063_changed_row"] == 1) | (df["h064_changed_row"] == 1)]
    else:
        raise ValueError(spec.family)

    out = []
    counts: dict[str, int] = {}
    for rec in df.sort_values("h065_row_score", ascending=False).to_dict("records"):
        subject = str(rec["subject_id"])
        if counts.get(subject, 0) >= spec.max_per_subject:
            continue
        out.append(rec)
        counts[subject] = counts.get(subject, 0) + 1
        if len(out) >= spec.k_rows:
            break
    return pd.DataFrame(out)


def effective_scale(target: str, phase: str, target_rule: str, weights: pd.DataFrame) -> float:
    if phase not in {"pre", "post"}:
        return 0.0
    row = weights[(weights["phase"] == phase) & (weights["target"] == target)]
    if row.empty:
        return 0.0
    rec = row.iloc[0]
    if target_rule == "phase_top3":
        return float(rec["in_top3"])
    if target_rule == "phase_top4":
        return float(rec["in_top4"])
    if target_rule == "phase_weighted":
        return float(rec["phase_weight"])
    if target_rule == "phase_weighted_gainpos":
        return float(rec["phase_weight"])
    raise ValueError(target_rule)


def apply_scaled_move(base: float, target: float, alpha: float, scale: float, mode: str) -> float:
    eff = max(0.0, min(1.75, alpha * scale))
    if eff <= 0.0:
        return float(base)
    if mode == "prob":
        return float(clip_prob((1.0 - eff) * base + eff * target))
    if mode == "logit":
        return float(clip_prob(sigmoid((1.0 - eff) * logit(np.array([base])) + eff * logit(np.array([target]))))[0])
    raise ValueError(mode)


def make_candidate(
    spec: PhaseSpec,
    sample: pd.DataFrame,
    h057: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
    weights: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object], pd.DataFrame]:
    selected = select_rows(row_scores, spec)
    prob = h057.copy()
    if selected.empty:
        return prob, {}, selected
    gain_lookup = row_scores.set_index("row")
    changed_cells = 0
    target_counts = {target: 0 for target in TARGETS}
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        phase = str(rec["phase"])
        for target in NON_Q2:
            gain = float(gain_lookup.loc[row, f"{target}_gain"])
            if spec.target_rule.endswith("gainpos") and gain <= 0:
                continue
            scale = effective_scale(target, phase, spec.target_rule, weights)
            if scale <= 0:
                continue
            j = TARGETS.index(target)
            new_value = apply_scaled_move(h057[row, j], q061[row, j], spec.alpha, scale, spec.mode)
            if abs(new_value - h057[row, j]) > 1.0e-12:
                prob[row, j] = new_value
                changed_cells += 1
                target_counts[target] += 1

    selected_rows = selected["row"].astype(int).tolist()
    h062_set = set(row_scores.loc[row_scores["h062_changed_row"] == 1, "row"].astype(int))
    h063_set = set(row_scores.loc[row_scores["h063_changed_row"] == 1, "row"].astype(int))
    h064_set = set(row_scores.loc[row_scores["h064_changed_row"] == 1, "row"].astype(int))
    h050_null_set = set(row_scores.loc[row_scores["is_h050_null"] == 1, "row"].astype(int))
    delta = float((bce(prob, q061) - bce(h057, q061)).mean())
    changed = np.abs(prob - h057) > 1.0e-12
    meta = {
        "candidate_id": "",
        "family": spec.family,
        "k_rows": spec.k_rows,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "target_rule": spec.target_rule,
        "max_per_subject": spec.max_per_subject,
        "max_abs_seed_distance": spec.max_abs_seed_distance,
        "selected_rows": ",".join(map(str, selected_rows)),
        "selected_row_count": len(selected_rows),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "q2_changed_vs_h057": int(changed[:, TARGETS.index("Q2")].sum()),
        "posterior_delta_vs_h057": delta,
        "mean_h065_row_score": float(selected["h065_row_score"].mean()),
        "mean_h064_row_score": float(selected["h064_row_score"].mean()),
        "mean_phase_route_gain": float(selected["phase_route_gain"].mean()),
        "pre_rows": int((selected["phase"] == "pre").sum()),
        "post_rows": int((selected["phase"] == "post").sum()),
        "phase_balance": float(min((selected["phase"] == "pre").sum(), (selected["phase"] == "post").sum()) / max(len(selected), 1)),
        "episode_near_rate": float((selected["phase_near"] > 0).mean()),
        "selected_subjects": int(selected["subject_id"].nunique()),
        "h050_null_rows_selected": len(set(selected_rows) & h050_null_set),
        "h062_overlap_rows": len(set(selected_rows) & h062_set),
        "h063_overlap_rows": len(set(selected_rows) & h063_set),
        "h064_overlap_rows": len(set(selected_rows) & h064_set),
        "mean_targets_per_row": float(int(changed.sum()) / max(len(selected_rows), 1)),
        "target_specificity": float(1.0 - abs((int(changed.sum()) / max(len(selected_rows), 1)) - 4.0) / 4.0),
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(target_counts.get(target, 0))
    return prob, meta, selected


def validate_upload(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = load_sub(path, sample)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    changed = np.abs(prob - h057_prob) > 1.0e-12
    return {
        "path": str(path),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(prob.min()),
        "max_prob": float(prob.max()),
        "q2_changed_vs_h057_validation": int(changed[:, TARGETS.index("Q2")].sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and prob.min() >= 0.0
            and prob.max() <= 1.0
            and int(changed[:, TARGETS.index("Q2")].sum()) == 0
        ),
    }


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h065_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h065_state_transition_phase_*_uploadsafe.csv"):
        path.unlink()


def main() -> None:
    cleanup_previous_outputs()

    sample = load_sub(H057)
    h042_df = load_sub(H042, sample)
    h057_df = load_sub(H057, sample)
    h042 = h042_df[TARGETS].to_numpy(dtype=np.float64)
    h057 = h057_df[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)

    row_scores = build_row_scores(sample, h042, h057, q061)
    weights = phase_target_weights(row_scores)
    row_scores.to_csv(OUT / "h065_row_scores.csv", index=False)
    weights.to_csv(OUT / "h065_phase_target_weights.csv", index=False)

    specs: list[PhaseSpec] = []
    for family in ["phase_near_union", "phase_h064_core", "phase_graph_near", "phase_far_control"]:
        for rule in ["phase_top3", "phase_top4", "phase_weighted", "phase_weighted_gainpos"]:
            for k_rows in [24, 36, 48, 60, 72]:
                for alpha in [0.75, 1.0, 1.15]:
                    for mode in ["logit", "prob"]:
                        max_dist = 3 if family != "phase_far_control" else 8
                        specs.append(
                            PhaseSpec(
                                family=family,
                                k_rows=k_rows,
                                alpha=alpha,
                                mode=mode,
                                target_rule=rule,
                                max_per_subject=8,
                                max_abs_seed_distance=max_dist,
                            )
                        )

    metas = []
    selected_snapshots: dict[str, pd.DataFrame] = {}
    candidate_probs: dict[str, np.ndarray] = {}
    for spec in specs:
        prob, meta, selected = make_candidate(spec, sample, h057, q061, row_scores, weights)
        if not meta or meta["changed_cells_vs_h057"] == 0:
            continue
        digest = short_hash(prob)
        candidate_id = (
            f"h065_{spec.family}_r{meta['selected_row_count']}_{spec.target_rule}_"
            f"a{str(spec.alpha).replace('.', 'p')}_{spec.mode}_{digest}"
        )
        file = f"submission_{candidate_id}.csv"
        path = OUT / file
        write_submission(sample, prob, path)
        meta["candidate_id"] = candidate_id
        meta["file"] = file
        meta["resolved_path"] = str(path)
        candidate_probs[candidate_id] = prob
        selected_snapshots[candidate_id] = selected
        metas.append(meta)

    cand = pd.DataFrame(metas)
    if cand.empty:
        raise RuntimeError("no H065 candidates generated")

    cand = cand.drop_duplicates(subset=["candidate_id"]).reset_index(drop=True)
    cand["posterior_rank"] = (-cand["posterior_delta_vs_h057"]).rank(method="average", pct=True)
    cand["h065_rank"] = cand["mean_h065_row_score"].rank(method="average", pct=True)
    cand["context_rank"] = cand["mean_h064_row_score"].rank(method="average", pct=True)
    cand["overlap_strength"] = (
        cand["h062_overlap_rows"] / cand["selected_row_count"].clip(lower=1)
        + cand["h063_overlap_rows"] / cand["selected_row_count"].clip(lower=1)
        + cand["h064_overlap_rows"] / cand["selected_row_count"].clip(lower=1)
    ) / 3.0
    cand["size_score"] = 1.0 - (cand["changed_cells_vs_h057"] - 240).abs() / 360.0
    cand["size_score"] = cand["size_score"].clip(lower=0.0, upper=1.0)
    cand["family_penalty"] = np.where(cand["family"].eq("phase_far_control"), 0.25, 0.0)
    cand["h065_score"] = (
        0.22 * cand["posterior_rank"]
        + 0.18 * cand["h065_rank"]
        + 0.14 * cand["context_rank"]
        + 0.12 * cand["phase_balance"]
        + 0.10 * cand["overlap_strength"]
        + 0.20 * cand["target_specificity"].clip(lower=0.0, upper=1.0)
        + 0.08 * cand["size_score"]
        - cand["family_penalty"]
        - 0.50 * (cand["h050_null_rows_selected"] > 0).astype(float)
        - 0.50 * (cand["q2_changed_vs_h057"] > 0).astype(float)
    )
    cand = cand.sort_values("h065_score", ascending=False).reset_index(drop=True)
    cand.to_csv(OUT / "h065_candidate_scores.csv", index=False)

    selected_meta = cand.iloc[0].to_dict()
    selected_id = str(selected_meta["candidate_id"])
    selected_path = Path(str(selected_meta["resolved_path"]))
    root_file = f"submission_h065_state_transition_phase_{short_hash(candidate_probs[selected_id])}_uploadsafe.csv"
    root_path = ROOT / root_file
    shutil.copyfile(selected_path, root_path)
    upload = validate_upload(root_path, sample, h057)
    selected_meta.update(upload)
    selected_meta["root_uploadsafe_path"] = str(root_path)
    selected_meta["decision"] = "promote_state_transition_phase_sensor"
    selected_meta["worldview"] = (
        "H057 seed-neighbor rows are transition phases with phase-specific target routes, "
        "not copies of the seed full-vector state"
    )

    decision = pd.DataFrame([selected_meta])
    decision.to_csv(OUT / "h065_decision.csv", index=False)
    selected_snapshots[selected_id].to_csv(OUT / "h065_selected_rows.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "h057_seed_rows": int(len(support_rows_by_diff(h057, h042, NON_Q2))),
                "candidate_rows": int(((row_scores["is_h057_seed"] == 0) & (row_scores["is_h050_null"] == 0)).sum()),
                "near_transition_rows": int(
                    (
                        (row_scores["is_h057_seed"] == 0)
                        & (row_scores["is_h050_null"] == 0)
                        & (row_scores["phase"].isin(["pre", "post"]))
                        & (row_scores["abs_seed_distance"] <= 3)
                    ).sum()
                ),
                "pre_near_rows": int(((row_scores["phase"] == "pre") & (row_scores["abs_seed_distance"] <= 3)).sum()),
                "post_near_rows": int(((row_scores["phase"] == "post") & (row_scores["abs_seed_distance"] <= 3)).sum()),
                "promoted_file": root_file,
                "promoted_candidate": selected_id,
                "promoted_changed_cells": int(selected_meta["changed_cells_vs_h057"]),
                "promoted_selected_rows": int(selected_meta["selected_row_count"]),
                "promoted_posterior_delta": float(selected_meta["posterior_delta_vs_h057"]),
            }
        ]
    )
    summary.to_csv(OUT / "h065_summary.csv", index=False)

    report = f"""# H065 State-Transition Phase HS-JEPA

Question: are H057's neighboring same-subject rows copies of the seed state, or
pre/post transition phases that need different target routes?

Design:

- base: H057 public frontier;
- positive representation: H057's `45` full-vector state rows;
- context: H064 contrastive state graph plus H062/H063 expansion evidence;
- target representation: H061 post-H057 posterior `q061`;
- action: freeze Q2 and move only phase-specific non-Q2 target routes;
- route learning: derive separate pre/post target weights from near non-seed
  rows that both have expansion evidence and are close to H057 seeds.

Phase target weights:

{md_table(weights.sort_values(["phase", "rank"]), 20)}

Summary:

{md_table(summary)}

Decision:

{md_table(decision)}

Top candidates:

{md_table(cand[["candidate_id", "family", "target_rule", "selected_row_count", "changed_cells_vs_h057", "posterior_delta_vs_h057", "phase_balance", "mean_targets_per_row", "h062_overlap_rows", "h063_overlap_rows", "h064_overlap_rows", "h065_score"]], 20)}

Selected rows:

{md_table(selected_snapshots[selected_id][["row", "subject_id", "sleep_date", "phase", "signed_seed_offset", "abs_seed_distance", "h065_row_score", "h064_row_score", "phase_route_gain", "h062_changed_row", "h063_changed_row", "h064_changed_row"]], 80)}

Interpretation rule:

- If H065 improves over H057/H064, broad episode-copy was the wrong abstraction:
  HS-JEPA needs a transition-phase decoder around validated human-state seeds.
- If H065 fails while H062/H063/H064 improve, the phase-specific target route is
  too sparse or the learned pre/post route is wrong.
- If H065, H062, H063, and H064 all fail, H057 is likely a compact public-specific
  row-state and same-subject neighbor expansion should be demoted.
"""
    (OUT / "h065_report.md").write_text(report, encoding="utf-8")

    print(report)


if __name__ == "__main__":
    main()
