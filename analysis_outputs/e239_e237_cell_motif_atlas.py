#!/usr/bin/env python3
"""E239: motif atlas for the E237 learned Q3 cells.

E237 survived local stress by rolling back exactly 25 Q3 cells from E224 to
E154. E238 fixed the public-score decoder, but scalar LB feedback alone cannot
tell whether those cells are a real hidden motif or another top-k shortcut.

This script does not train a model and does not create a submission. It asks a
small JEPA-style representation question: what context features make the E237
target cells unusual, and how do they differ from the E230 hand-prune cells?
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402
import e238_e237_public_feedback_decoder as e238  # noqa: E402


RNG = 20260530 + 239
EPS = 1.0e-12
Q3_IDX = TARGETS.index("Q3")

ROW_OUT = OUT / "e239_e237_cell_motif_atlas_rows.csv"
ENRICH_OUT = OUT / "e239_e237_cell_motif_atlas_enrichment.csv"
GROUP_OUT = OUT / "e239_e237_cell_motif_atlas_group_counts.csv"
OVERLAP_OUT = OUT / "e239_e237_cell_motif_atlas_overlap.csv"
REPORT_OUT = OUT / "e239_e237_cell_motif_atlas_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def bool_delta_rows(a: np.ndarray, b: np.ndarray, target_idx: int = Q3_IDX, tol: float = 1.0e-10) -> np.ndarray:
    za = logit(a[:, target_idx])
    zb = logit(b[:, target_idx])
    return np.abs(za - zb) > tol


def add_train_adjacency(sample: pd.DataFrame) -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    out = sample[KEYS].copy()
    out["sleep_date"] = pd.to_datetime(out["sleep_date"])
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"])
    out["global_row_idx"] = np.arange(len(out))
    out["subject_test_pos"] = (
        out.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id").cumcount().reindex(out.index).astype(float)
    )
    out["subject_test_size"] = out.groupby("subject_id")["subject_id"].transform("size").astype(float)
    out["subject_test_pos_frac"] = out["subject_test_pos"] / np.maximum(out["subject_test_size"] - 1.0, 1.0)
    out["distance_to_test_edge"] = np.minimum(
        out["subject_test_pos"],
        out["subject_test_size"] - 1.0 - out["subject_test_pos"],
    )
    out["near_test_edge_2"] = (out["distance_to_test_edge"] <= 2.0).astype(float)
    out["near_test_edge_5"] = (out["distance_to_test_edge"] <= 5.0).astype(float)

    prev_gaps: list[float] = []
    next_gaps: list[float] = []
    min_gaps: list[float] = []
    between_flags: list[float] = []
    for _, rec in out.iterrows():
        dates = train.loc[train["subject_id"].astype(str).eq(str(rec["subject_id"])), "lifelog_date"].sort_values()
        cur = rec["lifelog_date"]
        prev_dates = dates[dates <= cur]
        next_dates = dates[dates >= cur]
        prev_gap = float("nan") if prev_dates.empty else float((cur - prev_dates.iloc[-1]).days)
        next_gap = float("nan") if next_dates.empty else float((next_dates.iloc[0] - cur).days)
        candidates = [x for x in [prev_gap, next_gap] if np.isfinite(x)]
        prev_gaps.append(prev_gap)
        next_gaps.append(next_gap)
        min_gaps.append(float(min(candidates)) if candidates else float("nan"))
        between_flags.append(float(np.isfinite(prev_gap) and np.isfinite(next_gap)))
    out["prev_train_gap"] = prev_gaps
    out["next_train_gap"] = next_gaps
    out["min_train_gap"] = min_gaps
    out["between_train_runs"] = between_flags
    out["gap_adjacent_1"] = (out["min_train_gap"] <= 1.0).astype(float)
    out["gap_adjacent_2"] = (out["min_train_gap"] <= 2.0).astype(float)
    out["lifelog_ordinal"] = out["lifelog_date"].map(pd.Timestamp.toordinal).astype(float)
    return out


def permutation_diff(
    values: pd.Series,
    selected: pd.Series,
    *,
    n_perm: int = 5000,
    seed: int = RNG,
) -> dict[str, float]:
    vals = pd.to_numeric(values, errors="coerce").to_numpy(dtype=np.float64)
    sel = selected.to_numpy(dtype=bool)
    mask = np.isfinite(vals)
    vals = vals[mask]
    sel = sel[mask]
    n = len(vals)
    k = int(sel.sum())
    if n == 0 or k == 0 or k == n:
        return {
            "n_valid": float(n),
            "selected_n": float(k),
            "selected_mean": float("nan"),
            "population_mean": float("nan"),
            "diff": float("nan"),
            "lift": float("nan"),
            "perm_p_two_sided": float("nan"),
            "z": float("nan"),
        }
    obs_sel = float(np.mean(vals[sel]))
    obs_pop = float(np.mean(vals))
    obs = obs_sel - obs_pop
    rng = np.random.default_rng(seed)
    sims = np.empty(n_perm, dtype=np.float64)
    indices = np.arange(n)
    for i in range(n_perm):
        pick = rng.choice(indices, size=k, replace=False)
        sims[i] = float(np.mean(vals[pick]) - obs_pop)
    p = float((1.0 + np.sum(np.abs(sims) >= abs(obs))) / (n_perm + 1.0))
    sd = float(np.std(sims))
    z = float(obs / (sd + EPS))
    return {
        "n_valid": float(n),
        "selected_n": float(k),
        "selected_mean": obs_sel,
        "population_mean": obs_pop,
        "diff": obs,
        "lift": float(obs_sel / (obs_pop + EPS)),
        "perm_p_two_sided": p,
        "z": z,
    }


def categorical_enrichment(rows: pd.DataFrame, selector: str, column: str) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for value in sorted(rows[column].dropna().astype(str).unique()):
        indicator = rows[column].astype(str).eq(value).astype(float)
        stat = permutation_diff(indicator, rows[selector].astype(bool), seed=RNG + hash((selector, column, value)) % 10000)
        out.append(
            {
                "selector": selector,
                "feature_type": "category",
                "feature": column,
                "level": value,
                **stat,
            }
        )
    return pd.DataFrame(out)


def continuous_enrichment(rows: pd.DataFrame, selector: str, features: list[str]) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for i, feature in enumerate(features):
        if feature not in rows.columns:
            continue
        stat = permutation_diff(rows[feature], rows[selector].astype(bool), seed=RNG + i * 17 + len(selector))
        out.append(
            {
                "selector": selector,
                "feature_type": "continuous",
                "feature": feature,
                "level": "",
                **stat,
            }
        )
    return pd.DataFrame(out)


def overlap_table(rows: pd.DataFrame, selectors: list[str]) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for i, a in enumerate(selectors):
        aa = rows[a].astype(bool).to_numpy()
        for b in selectors[i:]:
            bb = rows[b].astype(bool).to_numpy()
            inter = int(np.sum(aa & bb))
            union = int(np.sum(aa | bb))
            out.append(
                {
                    "selector_a": a,
                    "selector_b": b,
                    "n_a": int(np.sum(aa)),
                    "n_b": int(np.sum(bb)),
                    "intersection": inter,
                    "jaccard": float(inter / union) if union else 0.0,
                    "a_recall": float(inter / max(np.sum(aa), 1)),
                    "b_recall": float(inter / max(np.sum(bb), 1)),
                }
            )
    return pd.DataFrame(out)


def build_rows() -> pd.DataFrame:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    sample_keys = sample[KEYS].copy()
    sample_keys["row_idx"] = np.arange(len(sample_keys))

    e95 = load_prob(e238.E95_FILE, sample)
    e154 = load_prob(e238.E154_FILE, sample)
    e224 = load_prob(e238.E224_FILE, sample)
    e237 = load_prob(e238.E237_FILE, sample)
    e230_swing25 = load_prob(e238.E230_SWING25_FILE, sample)
    e230_risk21 = load_prob(e238.E230_RISK21_FILE, sample)
    e230_risk13 = load_prob(e238.E230_RISK13_FILE, sample)

    _, _, sub_long, _ = e232.build_long_frames()
    q3 = sub_long[sub_long["task_name"].eq("q3_e224")].copy().sort_values("row_idx").reset_index(drop=True)
    if len(q3) != len(sample):
        raise RuntimeError(f"q3 row mismatch: {len(q3)} != {len(sample)}")
    if not q3["row_idx"].to_numpy(dtype=int).tolist() == list(range(len(sample))):
        raise RuntimeError("q3 row_idx is not contiguous")

    rows = q3.copy()
    rows = rows.merge(sample_keys, on=["row_idx", "subject_id"], how="left", validate="one_to_one")
    rows = rows.merge(add_train_adjacency(sample)[["subject_id", "sleep_date", "lifelog_date", "global_row_idx", "subject_test_pos", "subject_test_size", "subject_test_pos_frac", "distance_to_test_edge", "near_test_edge_2", "near_test_edge_5", "prev_train_gap", "next_train_gap", "min_train_gap", "between_train_runs", "gap_adjacent_1", "gap_adjacent_2", "lifelog_ordinal"]], on=["subject_id", "sleep_date", "lifelog_date"], how="left", validate="one_to_one")

    z95 = logit(e95[:, Q3_IDX])
    z154 = logit(e154[:, Q3_IDX])
    z224 = logit(e224[:, Q3_IDX])
    z237 = logit(e237[:, Q3_IDX])
    rows["p_e95_q3"] = e95[:, Q3_IDX]
    rows["p_e154_q3"] = e154[:, Q3_IDX]
    rows["p_e224_q3"] = e224[:, Q3_IDX]
    rows["p_e237_q3"] = e237[:, Q3_IDX]
    rows["logit_e224_minus_e154_q3"] = z224 - z154
    rows["abs_logit_e224_minus_e154_q3"] = np.abs(z224 - z154)
    rows["logit_e237_minus_e224_q3"] = z237 - z224
    rows["abs_logit_e237_minus_e224_q3"] = np.abs(z237 - z224)
    rows["logit_e224_minus_e95_q3"] = z224 - z95
    rows["abs_logit_e224_minus_e95_q3"] = np.abs(z224 - z95)
    rows["e224_q3_abs_rank"] = rows["abs_logit_e224_minus_e154_q3"].rank(method="first", ascending=False)

    rows["e237_drop"] = bool_delta_rows(e237, e224)
    rows["e230_swing25"] = bool_delta_rows(e230_swing25, e224)
    rows["e230_risk21"] = bool_delta_rows(e230_risk21, e224)
    rows["e230_risk13"] = bool_delta_rows(e230_risk13, e224)
    rows["e237_overlap_swing25"] = rows["e237_drop"] & rows["e230_swing25"]
    rows["e237_overlap_risk21"] = rows["e237_drop"] & rows["e230_risk21"]
    rows["e237_only_not_swing25"] = rows["e237_drop"] & ~rows["e230_swing25"]
    rows["e237_only_not_risk21"] = rows["e237_drop"] & ~rows["e230_risk21"]
    rows["e230_risk21_only_not_e237"] = rows["e230_risk21"] & ~rows["e237_drop"]
    rows["e230_swing25_only_not_e237"] = rows["e230_swing25"] & ~rows["e237_drop"]

    rows["e224_top_abs_25"] = rows["e224_q3_abs_rank"].le(25).astype(float)
    rows["e224_top_abs_50"] = rows["e224_q3_abs_rank"].le(50).astype(float)
    rows["e237_drop_direction_down"] = (rows["logit_e237_minus_e224_q3"] < 0).astype(float)
    rows["e237_drops_to_e154"] = (
        np.abs(rows["p_e237_q3"].to_numpy(dtype=float) - rows["p_e154_q3"].to_numpy(dtype=float)) <= 1.0e-10
    ).astype(float)
    return rows


def main() -> None:
    rows = build_rows()
    selectors = [
        "e237_drop",
        "e230_swing25",
        "e230_risk21",
        "e237_only_not_swing25",
        "e237_only_not_risk21",
        "e237_overlap_swing25",
        "e237_overlap_risk21",
        "e230_risk21_only_not_e237",
    ]
    selectors = [s for s in selectors if s in rows.columns and int(rows[s].sum()) >= 3]

    continuous_features = [
        "abs_logit_step",
        "logit_step",
        "base_prob",
        "full_prob",
        "prob_gap",
        "base_margin",
        "full_margin",
        "subject_pos_frac",
        "subject_test_pos_frac",
        "distance_to_test_edge",
        "near_test_edge_2",
        "near_test_edge_5",
        "prev_train_gap",
        "next_train_gap",
        "min_train_gap",
        "between_train_runs",
        "gap_adjacent_1",
        "gap_adjacent_2",
        "abs_logit_e224_minus_e154_q3",
        "abs_logit_e224_minus_e95_q3",
        "abs_logit_e237_minus_e224_q3",
        "e224_top_abs_25",
        "e224_top_abs_50",
        "e215_pred_norm",
        "e215_resid_norm",
        "e215_resid_abs_mean",
        "e215_pred_to_context_cos",
        "e215_pred_pc10",
        "e215_resid_pc10",
        "e215_deep_resid_abs_mean",
        "e215_quiet_resid_abs_mean",
        "e208_pred_norm",
        "e208_resid_self_norm",
        "e208_resid_nn_norm",
        "e208_resid_self_abs_mean",
        "e208_pred_to_self_cos",
        "e208_pred_to_nn_cos",
        "e208_nn_target_dist",
        "e208_pred_pc14",
        "e208_resid_self_pc10",
        "e208_s2_pred_norm",
    ]
    categorical_features = ["subject_id", "lifelog_weekday", "sleep_weekday"]

    enrich_parts: list[pd.DataFrame] = []
    for selector in selectors:
        enrich_parts.append(continuous_enrichment(rows, selector, continuous_features))
        for column in categorical_features:
            enrich_parts.append(categorical_enrichment(rows, selector, column))
    enrich = pd.concat(enrich_parts, ignore_index=True)
    enrich["abs_z"] = enrich["z"].abs()
    enrich = enrich.sort_values(["selector", "abs_z", "perm_p_two_sided"], ascending=[True, False, True])

    group_rows: list[dict[str, Any]] = []
    for selector in selectors:
        sel = rows[selector].astype(bool)
        for subject, part in rows.groupby("subject_id"):
            group_rows.append(
                {
                    "selector": selector,
                    "group_type": "subject_id",
                    "group": str(subject),
                    "selected_n": int(sel.loc[part.index].sum()),
                    "group_n": int(len(part)),
                    "selected_rate": float(sel.loc[part.index].mean()),
                }
            )
        for weekday, part in rows.groupby("lifelog_weekday"):
            group_rows.append(
                {
                    "selector": selector,
                    "group_type": "lifelog_weekday",
                    "group": str(int(weekday)),
                    "selected_n": int(sel.loc[part.index].sum()),
                    "group_n": int(len(part)),
                    "selected_rate": float(sel.loc[part.index].mean()),
                }
            )
    groups = pd.DataFrame(group_rows).sort_values(["selector", "selected_n", "selected_rate"], ascending=[True, False, False])
    overlaps = overlap_table(rows, selectors)

    rows.to_csv(ROW_OUT, index=False)
    enrich.to_csv(ENRICH_OUT, index=False)
    groups.to_csv(GROUP_OUT, index=False)
    overlaps.to_csv(OVERLAP_OUT, index=False)

    top_enrich = enrich[enrich["selector"].eq("e237_drop")].head(18)
    top_only = enrich[enrich["selector"].eq("e237_only_not_swing25")].head(12)
    top_risk_only = enrich[enrich["selector"].eq("e230_risk21_only_not_e237")].head(12)
    e237_rows = rows[rows["e237_drop"]].sort_values("abs_logit_e237_minus_e224_q3", ascending=False)

    e237_summary = {
        "e237_n": int(rows["e237_drop"].sum()),
        "e230_swing25_n": int(rows["e230_swing25"].sum()),
        "e230_risk21_n": int(rows["e230_risk21"].sum()),
        "overlap_swing25": int((rows["e237_drop"] & rows["e230_swing25"]).sum()),
        "overlap_risk21": int((rows["e237_drop"] & rows["e230_risk21"]).sum()),
        "e237_only_not_swing25": int(rows["e237_only_not_swing25"].sum()),
        "e237_only_not_risk21": int(rows["e237_only_not_risk21"].sum()),
        "e237_top_abs25_rate": float(rows.loc[rows["e237_drop"], "e224_top_abs_25"].mean()),
        "e237_near_edge2_rate": float(rows.loc[rows["e237_drop"], "near_test_edge_2"].mean()),
        "population_near_edge2_rate": float(rows["near_test_edge_2"].mean()),
        "e237_gap_adjacent2_rate": float(rows.loc[rows["e237_drop"], "gap_adjacent_2"].mean()),
        "population_gap_adjacent2_rate": float(rows["gap_adjacent_2"].mean()),
    }

    lines = [
        "# E239 E237 Cell Motif Atlas",
        "",
        "## Observation",
        "",
        "E237 is a 25-cell Q3-only rollback from E224 to E154. This audit asks whether those cells have a visible hidden-context motif or whether the learned gate reduced to top-k amplitude.",
        "",
        "## Summary",
        "",
    ]
    for key, value in e237_summary.items():
        if isinstance(value, float):
            lines.append(f"- `{key}`: `{value:.9f}`")
        else:
            lines.append(f"- `{key}`: `{value}`")
    lines += [
        "",
        "## Selector Overlap",
        "",
        md_table(overlaps, n=30),
        "",
        "## Top E237 Enrichments",
        "",
        md_table(
            top_enrich,
            ["selector", "feature_type", "feature", "level", "selected_n", "selected_mean", "population_mean", "diff", "lift", "z", "perm_p_two_sided"],
            n=18,
        ),
        "",
        "## E237-Only Versus E230 Swing Motif",
        "",
        md_table(
            top_only,
            ["selector", "feature_type", "feature", "level", "selected_n", "selected_mean", "population_mean", "diff", "lift", "z", "perm_p_two_sided"],
            n=12,
        ),
        "",
        "## E230 Risk-Only Motif",
        "",
        md_table(
            top_risk_only,
            ["selector", "feature_type", "feature", "level", "selected_n", "selected_mean", "population_mean", "diff", "lift", "z", "perm_p_two_sided"],
            n=12,
        ),
        "",
        "## E237 Rows",
        "",
        md_table(
            e237_rows,
            [
                "row_idx",
                "subject_id",
                "sleep_date",
                "lifelog_date",
                "p_e224_q3",
                "p_e237_q3",
                "abs_logit_e224_minus_e154_q3",
                "abs_logit_e237_minus_e224_q3",
                "e230_swing25",
                "e230_risk21",
                "subject_test_pos_frac",
                "distance_to_test_edge",
                "min_train_gap",
                "e215_resid_abs_mean",
                "e208_nn_target_dist",
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
        "Use this atlas as a falsification layer for E237 public feedback. If E237 wins, enrichments with low permutation p-value become candidate hidden motifs to rebuild as target-aware JEPA context. If E237 loses, any strong motif here is a shortcut warning rather than a submission lane.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")

    print(f"[E239 rows] {ROW_OUT}")
    print(f"[E239 enrichment] {ENRICH_OUT}")
    print(f"[E239 report] {REPORT_OUT}")
    print(pd.Series(e237_summary).to_string())


if __name__ == "__main__":
    main()
