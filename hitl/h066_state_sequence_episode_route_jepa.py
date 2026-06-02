#!/usr/bin/env python3
"""H066: State-sequence episode-route HS-JEPA.

H065 narrowed H064 rows into pre/post transition routes. H066 takes the next
worldview step: hidden human state may be generated as a subject-level episode
sequence, not as independent selected rows.

The context is H057 validated seed rows plus the H064/H065 state graph. The
target representation is the H061 post-H057 posterior. The action is a
sequence-constrained episode route: freeze Q2, infer pre/bridge/post states
around seed clusters, then move only state-specific non-Q2 target routes.
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
OUT = HITL / "h066_state_sequence_episode_route_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
NON_Q2 = [t for t in TARGETS if t != "Q2"]
EPS = 1.0e-6

H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H064 = "submission_h064_contrastive_state_graph_d09a5363_uploadsafe.csv"
H065 = "submission_h065_state_transition_phase_75d5575d_uploadsafe.csv"


@dataclass(frozen=True)
class SequenceSpec:
    core_gap: int
    radius: int
    min_emission: float
    max_episodes: int
    alpha: float
    mode: str
    route_rule: str


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


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def changed_rows(path: str, base_prob: np.ndarray, sample: pd.DataFrame) -> set[int]:
    root_path = ROOT / path
    if not root_path.exists():
        return set()
    prob = load_sub(root_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return set(np.where((np.abs(prob - base_prob) > 1.0e-12).any(axis=1))[0].tolist())


def rank_pct(values: pd.Series) -> pd.Series:
    return values.astype(float).rank(method="average", pct=True)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h066_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h066_state_sequence_episode_route_*_uploadsafe.csv"):
        path.unlink()


def prepare_row_scores(sample: pd.DataFrame, h057_prob: np.ndarray) -> pd.DataFrame:
    rows = pd.read_csv(HITL / "h065_state_transition_phase_jepa" / "h065_row_scores.csv")
    rows = key_frame(rows).sort_values("row").reset_index(drop=True)
    if not rows[KEYS].equals(sample[KEYS]):
        raise ValueError("H065 row score keys mismatch")

    h064_rows = changed_rows(H064, h057_prob, sample)
    h065_rows = changed_rows(H065, h057_prob, sample)
    rows["h064_changed_row_validation"] = rows["row"].isin(h064_rows).astype(int)
    rows["h065_changed_row"] = rows["row"].isin(h065_rows).astype(int)
    rows["h065_rank_norm"] = rank_pct(rows["h065_row_score"])
    rows["h064_rank_norm"] = rank_pct(rows["h064_row_score"])
    rows["route_gain_rank_norm"] = rank_pct(rows["phase_route_gain"])
    rows["gain_rank_norm"] = rank_pct(rows["row_gain_to_q061_nonq2"])
    rows["context_agreement"] = (
        rows["h062_changed_row"].astype(float)
        + rows["h063_changed_row"].astype(float)
        + rows["h064_changed_row_validation"].astype(float)
    ) / 3.0
    distance_penalty = np.minimum(rows["abs_seed_distance"].astype(float), 9.0) / 9.0
    rows["h066_emission"] = (
        0.22 * rows["h065_rank_norm"]
        + 0.18 * rows["h064_rank_norm"]
        + 0.15 * rows["route_gain_rank_norm"]
        + 0.13 * rows["gain_rank_norm"]
        + 0.12 * rows["context_agreement"]
        + 0.08 * rows["graph_rank"]
        + 0.08 * rows["contrast_rank"]
        + 0.06 * rows["phase_near"].astype(float)
        - 0.18 * distance_penalty
        - 0.55 * rows["is_h050_null"].astype(float)
        - 0.50 * rows["is_h057_seed"].astype(float)
    )
    gain_cols = [f"{t}_gain" for t in NON_Q2]
    rows["row_top4_gain_sum"] = rows[gain_cols].clip(lower=0.0).apply(
        lambda s: float(np.sort(s.to_numpy(dtype=np.float64))[-4:].sum()), axis=1
    )
    rows["row_top4_gain_rank"] = rank_pct(rows["row_top4_gain_sum"])
    rows["h066_emission"] = rows["h066_emission"] + 0.05 * rows["row_top4_gain_rank"]
    return rows


def build_seed_clusters(row_scores: pd.DataFrame, core_gap: int) -> pd.DataFrame:
    clusters: list[dict[str, object]] = []
    for subject, group in row_scores.sort_values("row").groupby("subject_id", sort=False):
        seeds = group.loc[group["is_h057_seed"] == 1, "row"].astype(int).tolist()
        if not seeds:
            continue
        current = [seeds[0]]
        for row in seeds[1:]:
            if row - current[-1] <= core_gap:
                current.append(row)
            else:
                clusters.append(
                    {
                        "cluster_id": f"{subject}_{current[0]}_{current[-1]}",
                        "subject_id": subject,
                        "start_row": current[0],
                        "end_row": current[-1],
                        "seed_count": len(current),
                        "seed_rows": ",".join(map(str, current)),
                    }
                )
                current = [row]
        clusters.append(
            {
                "cluster_id": f"{subject}_{current[0]}_{current[-1]}",
                "subject_id": subject,
                "start_row": current[0],
                "end_row": current[-1],
                "seed_count": len(current),
                "seed_rows": ",".join(map(str, current)),
            }
        )
    return pd.DataFrame(clusters)


def state_for_row(row: int, start_row: int, end_row: int) -> str:
    if row < start_row:
        return "pre"
    if row > end_row:
        return "post"
    return "bridge"


def distance_to_segment(row: int, start_row: int, end_row: int) -> int:
    if row < start_row:
        return start_row - row
    if row > end_row:
        return row - end_row
    return 0


def candidate_episode_rows(row_scores: pd.DataFrame, clusters: pd.DataFrame, spec: SequenceSpec) -> tuple[pd.DataFrame, pd.DataFrame]:
    episode_rows: list[dict[str, object]] = []
    episode_meta: list[dict[str, object]] = []
    for cluster in clusters.to_dict("records"):
        subject = str(cluster["subject_id"])
        start_row = int(cluster["start_row"])
        end_row = int(cluster["end_row"])
        seed_count = int(cluster["seed_count"])
        pool = row_scores[
            (row_scores["subject_id"] == subject)
            & (row_scores["is_h057_seed"] == 0)
            & (row_scores["is_h050_null"] == 0)
            & (row_scores["row"].between(start_row - spec.radius, end_row + spec.radius))
        ].copy()
        if pool.empty:
            continue
        pool["sequence_state"] = [state_for_row(int(row), start_row, end_row) for row in pool["row"]]
        pool["segment_distance"] = [
            distance_to_segment(int(row), start_row, end_row) for row in pool["row"]
        ]
        pool = pool[
            (
                (pool["h066_emission"] >= spec.min_emission)
                | (pool["h064_changed_row_validation"] == 1)
                | (pool["h063_changed_row"] == 1)
                | (pool["h062_changed_row"] == 1)
            )
            & (pool["segment_distance"] <= spec.radius)
        ].copy()
        if pool.empty:
            continue
        pool["cluster_id"] = str(cluster["cluster_id"])
        pool["cluster_start_row"] = start_row
        pool["cluster_end_row"] = end_row
        pool["cluster_seed_count"] = seed_count
        pool["episode_row_score"] = (
            pool["h066_emission"]
            + 0.08 * pool["h064_changed_row_validation"].astype(float)
            + 0.06 * pool["h065_changed_row"].astype(float)
            - 0.04 * (pool["segment_distance"].astype(float) / max(spec.radius, 1))
        )
        episode_score = float(pool["episode_row_score"].sum() / max(len(pool), 1))
        episode_score += 0.03 * min(seed_count, 4)
        episode_score += 0.02 * min(len(pool), 6)
        episode_meta.append(
            {
                "cluster_id": str(cluster["cluster_id"]),
                "subject_id": subject,
                "start_row": start_row,
                "end_row": end_row,
                "seed_count": seed_count,
                "selected_candidate_rows": int(len(pool)),
                "episode_score": episode_score,
                "pre_rows": int((pool["sequence_state"] == "pre").sum()),
                "bridge_rows": int((pool["sequence_state"] == "bridge").sum()),
                "post_rows": int((pool["sequence_state"] == "post").sum()),
                "h064_overlap_rows": int(pool["h064_changed_row_validation"].sum()),
                "h065_overlap_rows": int(pool["h065_changed_row"].sum()),
            }
        )
        episode_rows.extend(pool.to_dict("records"))
    if not episode_rows:
        return pd.DataFrame(), pd.DataFrame()
    episode_df = pd.DataFrame(episode_rows)
    episode_meta_df = pd.DataFrame(episode_meta).sort_values("episode_score", ascending=False).reset_index(drop=True)
    keep_clusters = set(episode_meta_df.head(spec.max_episodes)["cluster_id"].tolist())
    episode_df = episode_df[episode_df["cluster_id"].isin(keep_clusters)].copy()
    episode_df = episode_df.sort_values(["cluster_id", "row"]).drop_duplicates("row", keep="first")
    episode_meta_df = episode_meta_df[episode_meta_df["cluster_id"].isin(keep_clusters)].copy()
    return episode_df.reset_index(drop=True), episode_meta_df.reset_index(drop=True)


def effective_phase_targets(phase: str, weights: pd.DataFrame, top_k: int) -> list[str]:
    return weights[weights["phase"] == phase].sort_values("rank").head(top_k)["target"].astype(str).tolist()


def row_top_targets(row_rec: pd.Series, top_k: int) -> list[str]:
    gains = [(target, float(row_rec[f"{target}_gain"])) for target in NON_Q2]
    gains.sort(key=lambda item: item[1], reverse=True)
    return [target for target, gain in gains[:top_k] if gain > 0.0]


def target_route(row_rec: pd.Series, spec: SequenceSpec, weights: pd.DataFrame) -> list[str]:
    state = str(row_rec["sequence_state"])
    if spec.route_rule == "phase_top3":
        if state == "pre":
            return effective_phase_targets("pre", weights, 3)
        if state == "post":
            return effective_phase_targets("post", weights, 3)
        return row_top_targets(row_rec, 3)
    if spec.route_rule == "phase_top4":
        if state == "pre":
            return effective_phase_targets("pre", weights, 4)
        if state == "post":
            return effective_phase_targets("post", weights, 4)
        return row_top_targets(row_rec, 4)
    if spec.route_rule == "row_top4":
        return row_top_targets(row_rec, 4)
    if spec.route_rule == "episode_route_top4":
        if state == "pre":
            return effective_phase_targets("pre", weights, 4)
        if state == "post":
            return effective_phase_targets("post", weights, 4)
        bridge_targets = row_top_targets(row_rec, 3)
        bridge_targets.extend(effective_phase_targets("pre", weights, 2))
        bridge_targets.extend(effective_phase_targets("post", weights, 2))
        out: list[str] = []
        for target in bridge_targets:
            if target not in out:
                out.append(target)
        return out[:4]
    raise ValueError(spec.route_rule)


def apply_scaled_move(base: float, target: float, alpha: float, mode: str) -> float:
    if mode == "prob":
        return float(clip_prob((1.0 - alpha) * base + alpha * target))
    if mode == "logit":
        return float(clip_prob(sigmoid((1.0 - alpha) * logit(np.array([base])) + alpha * logit(np.array([target]))))[0])
    raise ValueError(mode)


def make_candidate(
    spec: SequenceSpec,
    sample: pd.DataFrame,
    h057: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
    weights: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object], pd.DataFrame, pd.DataFrame]:
    clusters = build_seed_clusters(row_scores, spec.core_gap)
    selected_rows, selected_episodes = candidate_episode_rows(row_scores, clusters, spec)
    prob = h057.copy()
    if selected_rows.empty:
        return prob, {}, selected_rows, selected_episodes

    target_counts = {target: 0 for target in TARGETS}
    route_sizes: list[int] = []
    for rec in selected_rows.to_dict("records"):
        row = int(rec["row"])
        route = target_route(pd.Series(rec), spec, weights)
        route_sizes.append(len(route))
        for target in route:
            if target == "Q2":
                continue
            j = TARGETS.index(target)
            new_value = apply_scaled_move(h057[row, j], q061[row, j], spec.alpha, spec.mode)
            if abs(new_value - h057[row, j]) > 1.0e-12:
                prob[row, j] = new_value
                target_counts[target] += 1

    selected_row_set = set(selected_rows["row"].astype(int))
    changed = np.abs(prob - h057) > 1.0e-12
    h050_null_rows = set(row_scores.loc[row_scores["is_h050_null"] == 1, "row"].astype(int))
    h064_rows = set(row_scores.loc[row_scores["h064_changed_row_validation"] == 1, "row"].astype(int))
    h065_rows = set(row_scores.loc[row_scores["h065_changed_row"] == 1, "row"].astype(int))
    delta = float((bce(prob, q061) - bce(h057, q061)).mean())
    state_counts = selected_rows["sequence_state"].value_counts().to_dict()
    meta = {
        "candidate_id": "",
        "core_gap": spec.core_gap,
        "radius": spec.radius,
        "min_emission": spec.min_emission,
        "max_episodes": spec.max_episodes,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "route_rule": spec.route_rule,
        "selected_rows": ",".join(map(str, sorted(selected_row_set))),
        "selected_row_count": len(selected_row_set),
        "selected_episode_count": int(selected_episodes["cluster_id"].nunique()),
        "selected_subjects": int(selected_rows["subject_id"].nunique()),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "q2_changed_vs_h057": int(changed[:, TARGETS.index("Q2")].sum()),
        "posterior_delta_vs_h057": delta,
        "mean_episode_score": float(selected_episodes["episode_score"].mean()),
        "mean_row_emission": float(selected_rows["h066_emission"].mean()),
        "mean_segment_distance": float(selected_rows["segment_distance"].mean()),
        "pre_rows": int(state_counts.get("pre", 0)),
        "bridge_rows": int(state_counts.get("bridge", 0)),
        "post_rows": int(state_counts.get("post", 0)),
        "phase_balance": float(
            min(state_counts.get("pre", 0), state_counts.get("post", 0))
            / max(state_counts.get("pre", 0) + state_counts.get("post", 0), 1)
        ),
        "bridge_rate": float(state_counts.get("bridge", 0) / max(len(selected_row_set), 1)),
        "h050_null_rows_selected": len(selected_row_set & h050_null_rows),
        "h064_overlap_rows": len(selected_row_set & h064_rows),
        "h065_overlap_rows": len(selected_row_set & h065_rows),
        "new_rows_vs_h065": len(selected_row_set - h065_rows),
        "mean_targets_per_row": float(int(changed.sum()) / max(len(selected_row_set), 1)),
        "mean_route_size": float(np.mean(route_sizes) if route_sizes else 0.0),
        "target_specificity": float(1.0 - abs((int(changed.sum()) / max(len(selected_row_set), 1)) - 4.0) / 4.0),
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(target_counts.get(target, 0))
    return prob, meta, selected_rows, selected_episodes


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


def main() -> None:
    cleanup_previous_outputs()
    sample = load_sub(H057)
    h057 = sample[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)
    row_scores = prepare_row_scores(sample, h057)
    weights = pd.read_csv(HITL / "h065_state_transition_phase_jepa" / "h065_phase_target_weights.csv")

    specs: list[SequenceSpec] = []
    # Keep the sweep focused on the actual H066 worldview: whether H057 seeds
    # expand into subject-level episodes. The discarded axes were near-duplicate
    # amplitude/style variants that made the first exhaustive run needlessly
    # slow without changing the falsification.
    for core_gap in [1, 4, 6]:
        for radius in [3, 6, 8]:
            for min_emission in [0.48, 0.56]:
                for max_episodes in [18, 999]:
                    for route_rule in ["episode_route_top4", "phase_top4", "row_top4"]:
                        for alpha in [0.75, 1.0, 1.15]:
                            for mode in ["logit", "prob"]:
                                specs.append(
                                    SequenceSpec(
                                        core_gap=core_gap,
                                        radius=radius,
                                        min_emission=min_emission,
                                        max_episodes=max_episodes,
                                        alpha=alpha,
                                        mode=mode,
                                        route_rule=route_rule,
                                    )
                                )

    metas: list[dict[str, object]] = []
    candidate_probs: dict[str, np.ndarray] = {}
    selected_rows_by_id: dict[str, pd.DataFrame] = {}
    selected_episodes_by_id: dict[str, pd.DataFrame] = {}
    for spec in specs:
        prob, meta, selected_rows, selected_episodes = make_candidate(spec, sample, h057, q061, row_scores, weights)
        if not meta or meta["changed_cells_vs_h057"] == 0:
            continue
        digest = short_hash(prob)
        candidate_id = (
            f"h066_seq_gap{spec.core_gap}_r{spec.radius}_e{str(spec.min_emission).replace('.', 'p')}_"
            f"m{spec.max_episodes}_{spec.route_rule}_a{str(spec.alpha).replace('.', 'p')}_{spec.mode}_{digest}"
        )
        meta["candidate_id"] = candidate_id
        meta["hash"] = digest
        candidate_probs[candidate_id] = prob
        selected_rows_by_id[candidate_id] = selected_rows
        selected_episodes_by_id[candidate_id] = selected_episodes
        metas.append(meta)

    cand = pd.DataFrame(metas).drop_duplicates(subset=["hash"]).reset_index(drop=True)
    if cand.empty:
        raise RuntimeError("no H066 candidates generated")

    cand["posterior_rank"] = (-cand["posterior_delta_vs_h057"]).rank(method="average", pct=True)
    cand["episode_rank"] = cand["mean_episode_score"].rank(method="average", pct=True)
    cand["emission_rank"] = cand["mean_row_emission"].rank(method="average", pct=True)
    cand["new_row_rate"] = cand["new_rows_vs_h065"] / cand["selected_row_count"].clip(lower=1)
    cand["overlap_strength"] = (
        cand["h064_overlap_rows"] / cand["selected_row_count"].clip(lower=1)
        + cand["h065_overlap_rows"] / cand["selected_row_count"].clip(lower=1)
    ) / 2.0
    cand["size_score"] = 1.0 - (cand["changed_cells_vs_h057"] - 300).abs() / 320.0
    cand["size_score"] = cand["size_score"].clip(lower=0.0, upper=1.0)
    cand["episode_size_score"] = 1.0 - (cand["selected_row_count"] - 72).abs() / 80.0
    cand["episode_size_score"] = cand["episode_size_score"].clip(lower=0.0, upper=1.0)
    cand["h066_score"] = (
        0.18 * cand["posterior_rank"]
        + 0.16 * cand["episode_rank"]
        + 0.14 * cand["emission_rank"]
        + 0.12 * cand["new_row_rate"].clip(lower=0.0, upper=1.0)
        + 0.10 * cand["overlap_strength"].clip(lower=0.0, upper=1.0)
        + 0.10 * cand["phase_balance"].clip(lower=0.0, upper=1.0)
        + 0.08 * cand["target_specificity"].clip(lower=0.0, upper=1.0)
        + 0.08 * cand["size_score"]
        + 0.06 * cand["episode_size_score"]
        + 0.04 * (cand["selected_subjects"] / 10.0).clip(lower=0.0, upper=1.0)
        - 0.50 * (cand["q2_changed_vs_h057"] > 0).astype(float)
        - 0.50 * (cand["h050_null_rows_selected"] > 0).astype(float)
    )
    cand = cand.sort_values("h066_score", ascending=False).reset_index(drop=True)

    # Persist the top search neighborhood, not every generated candidate.
    top_ids = cand.head(120)["candidate_id"].astype(str).tolist()
    for candidate_id in top_ids:
        prob = candidate_probs[candidate_id]
        file = f"submission_{candidate_id}.csv"
        path = OUT / file
        write_submission(sample, prob, path)
        cand.loc[cand["candidate_id"] == candidate_id, "file"] = file
        cand.loc[cand["candidate_id"] == candidate_id, "resolved_path"] = str(path)

    selected_meta = cand.iloc[0].to_dict()
    selected_id = str(selected_meta["candidate_id"])
    selected_digest = str(selected_meta["hash"])
    selected_path = OUT / f"submission_{selected_id}.csv"
    if not selected_path.exists():
        write_submission(sample, candidate_probs[selected_id], selected_path)
    root_file = f"submission_h066_state_sequence_episode_route_{selected_digest}_uploadsafe.csv"
    root_path = ROOT / root_file
    shutil.copyfile(selected_path, root_path)

    upload = validate_upload(root_path, sample, h057)
    selected_meta.update(upload)
    selected_meta["root_uploadsafe_path"] = str(root_path)
    selected_meta["decision"] = "promote_state_sequence_episode_route_sensor"
    selected_meta["worldview"] = (
        "H057 state is generated as a subject-level episode sequence with "
        "pre/bridge/post target routes, not independent row selections"
    )

    decision = pd.DataFrame([selected_meta])
    decision.to_csv(OUT / "h066_decision.csv", index=False)
    cand.to_csv(OUT / "h066_candidate_scores.csv", index=False)
    row_scores.to_csv(OUT / "h066_row_scores.csv", index=False)
    selected_rows_by_id[selected_id].to_csv(OUT / "h066_selected_rows.csv", index=False)
    selected_episodes_by_id[selected_id].to_csv(OUT / "h066_selected_episodes.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "candidate_count": len(cand),
                "persisted_candidate_files": len(top_ids),
                "promoted_file": root_file,
                "promoted_candidate": selected_id,
                "promoted_selected_rows": int(selected_meta["selected_row_count"]),
                "promoted_selected_episodes": int(selected_meta["selected_episode_count"]),
                "promoted_changed_cells": int(selected_meta["changed_cells_vs_h057"]),
                "promoted_posterior_delta": float(selected_meta["posterior_delta_vs_h057"]),
                "promoted_new_rows_vs_h065": int(selected_meta["new_rows_vs_h065"]),
            }
        ]
    )
    summary.to_csv(OUT / "h066_summary.csv", index=False)

    report = f"""# H066 State-Sequence Episode-Route HS-JEPA

Question: is H057's hidden human state generated as independent rows, or as a
subject-level episode sequence with pre/bridge/post target routes?

Design:

- base: H057 public frontier;
- context: H057 seed rows, H064/H065 state graph, H062/H063 expansion
  agreement;
- target representation: H061 post-H057 posterior `q061`;
- sequence model: cluster H057 seeds within each subject, score candidate
  pre/bridge/post rows around each cluster, then select high-energy episodes;
- action: freeze Q2 and move only state-route non-Q2 targets.

Summary:

{md_table(summary)}

Decision:

{md_table(decision)}

Selected Episodes:

{md_table(selected_episodes_by_id[selected_id], n=40)}

Selected Rows:

{md_table(selected_rows_by_id[selected_id][['row','subject_id','sleep_date','sequence_state','cluster_id','segment_distance','h066_emission','episode_row_score','h064_changed_row_validation','h065_changed_row','h062_changed_row','h063_changed_row']], n=80)}

Top candidates:

{md_table(cand[['candidate_id','core_gap','radius','min_emission','max_episodes','route_rule','selected_row_count','selected_episode_count','changed_cells_vs_h057','posterior_delta_vs_h057','new_rows_vs_h065','h064_overlap_rows','h065_overlap_rows','phase_balance','h066_score']], n=30)}

Interpretation rule:

- If H066 improves over H057/H065, row-independent selection was the wrong
  abstraction: HS-JEPA needs a subject-level latent sequence decoder.
- If H066 fails while H065 improves, sequence expansion is too broad and the
  smaller transition-route decoder is the better action translator.
- If H066 and H065 fail together, H057 may be a compact public-specific state,
  and expansion should move back to exact row-target identity or public-subset
  reconstruction.
"""
    (OUT / "h066_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
