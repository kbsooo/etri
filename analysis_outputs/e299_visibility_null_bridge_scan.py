#!/usr/bin/env python3
"""E299: search the visibility/null-rarity cliff without using public LB.

E298 showed a hard gap: selector-visible candidates were null-common, and
null-rare candidates were below action resolution. This script does not invent a
new model. It asks whether the gap is a coarse scale-grid artifact by rescaling
the nearest governed materializations in logit space and re-running the matched
null governor.

If this finds a ready candidate, it is a public-free submission candidate. If it
does not, it is evidence that the next breakthrough must change placement
geometry rather than tune amplitude.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e299_visibility_null_bridge_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import load_frames  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

ATLAS_IN = OUT / "e298_materialization_outcome_all.csv"
CANDIDATE_OUT = OUT / "e299_visibility_null_bridge_candidates.csv"
PREFILTER_OUT = OUT / "e299_visibility_null_bridge_prefilter.csv"
GOVERNOR_OUT = OUT / "e299_visibility_null_bridge_governor.csv"
SCORE_OUT = OUT / "e299_visibility_null_bridge_scores.csv"
NULL_MAP_OUT = OUT / "e299_visibility_null_bridge_null_map.csv"
REPORT_OUT = OUT / "e299_visibility_null_bridge_report.md"

MAX_BASES_PER_LANE = 10
MAX_NULL_EVAL = 90
N_TEST_NULL_REPS = 7

UP_MULTS = [1.015, 1.025, 1.035, 1.050, 1.070, 1.100, 1.140, 1.200, 1.300]
DOWN_MULTS = [0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.99]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 80) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def scale_token(mult: float) -> str:
    return f"m{mult:.3f}".replace(".", "p")


def as_bool(value: Any) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, columns: list[str], n: int = 20) -> str:
    if df.empty:
        return "_없음_"
    view = df.loc[:, columns].head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
    view = view.fillna("").astype(str)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in view.to_numpy()]
    return "\n".join([header, sep, *rows])


def candidate_path(row: pd.Series) -> Path | None:
    for col in ["source_path", "basename"]:
        if col not in row or pd.isna(row[col]):
            continue
        raw = Path(str(row[col]))
        candidates = [raw, ROOT / raw, OUT / raw.name]
        for path in candidates:
            if path.exists():
                return path
    return None


def align_meta_to_current() -> pd.DataFrame:
    base, _raw, *_rest = load_frames()
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = prep_test_meta(test_df)
    merged = normalize_keys(current[KEYS]).merge(meta, on=KEYS, how="left", validate="one_to_one")
    if merged["dateblock_group"].isna().any():
        raise RuntimeError("Could not align dateblock metadata to current")
    return merged.reset_index(drop=True)


def load_prob(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    return df


def source_logit_delta(path: Path, current: pd.DataFrame) -> tuple[np.ndarray, dict[str, float]]:
    cand = load_prob(path, current)
    delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))
    abs_by_target = np.mean(np.abs(delta), axis=0)
    return delta, {
        f"mean_abs_delta_{target}": float(abs_by_target[i])
        for i, target in enumerate(TARGETS)
    }


def write_candidate(current: pd.DataFrame, delta: np.ndarray, source_tag: str, mult: float) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + mult * np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e299_bridge_{safe_id(source_tag)}_{scale_token(mult)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def write_null_candidate(current: pd.DataFrame, applied_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(int(hashlib.sha1(f"{source_path.name}|{mode}|{rep}".encode()).hexdigest()[:8], 16))
    values = np.asarray(applied_delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    else:
        raise ValueError(mode)

    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + shuffled
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e299null_{safe_id(source_path.stem, 86)}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def source_tag(row: pd.Series) -> str:
    base = str(row["basename"])
    base = re.sub(r"_[0-9a-f]{8}\.csv$", "", base)
    base = re.sub(r"submission_", "", base)
    return base


def select_base_rows(atlas: pd.DataFrame) -> pd.DataFrame:
    df = atlas.copy()
    for col in ["selector_visible", "null_rare", "edge_ok", "p90_ok", "mean_ok", "worst_mode_ok"]:
        df[col] = df[col].map(as_bool)
    for col in ["actual_p90", "null_strict_rate", "p90_dominance", "mean_dominance", "worst_mode_p90_dominance", "readiness_distance"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["path_exists"] = df.apply(lambda r: candidate_path(r) is not None, axis=1)
    df = df[df["path_exists"]].copy()

    null_edge_lane = df[
        df["null_rare"]
        & df["p90_ok"]
        & df["mean_ok"]
        & df["worst_mode_ok"]
        & df["actual_p90"].between(-5.1e-5, -1.5e-5, inclusive="both")
    ].sort_values(["actual_p90", "readiness_distance"]).head(MAX_BASES_PER_LANE)

    visible_lownull_lane = df[
        df["selector_visible"]
        & df["edge_ok"]
        & (df["null_strict_rate"] <= 0.25)
    ].sort_values(["null_strict_rate", "actual_p90"]).head(MAX_BASES_PER_LANE)

    visible_common_lane = df[
        df["selector_visible"]
        & df["edge_ok"]
        & (df["null_strict_rate"] >= 0.40)
        & df["p90_dominance"].ge(0.80)
    ].sort_values(["actual_p90", "null_strict_rate"]).head(MAX_BASES_PER_LANE)

    picked = []
    for lane_name, part in [
        ("null_rare_edge_near", null_edge_lane),
        ("visible_low_null_near", visible_lownull_lane),
        ("visible_common_scale_down", visible_common_lane),
    ]:
        p = part.copy()
        p["bridge_lane"] = lane_name
        picked.append(p)
    out = pd.concat(picked, ignore_index=True, sort=False)
    return out.drop_duplicates("basename").reset_index(drop=True)


def generate_candidates(base_rows: pd.DataFrame, current: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    for _, row in base_rows.iterrows():
        path = candidate_path(row)
        if path is None:
            continue
        base_delta, target_stats = source_logit_delta(path, current)
        lane = str(row["bridge_lane"])
        if lane == "null_rare_edge_near":
            mults = UP_MULTS
        else:
            mults = DOWN_MULTS
        tag = source_tag(row)
        for mult in mults:
            out_path = write_candidate(current, base_delta, f"{lane}_{tag}", mult)
            applied = mult * base_delta
            deltas[out_path.name] = applied
            rows.append(
                {
                    "basename": out_path.name,
                    "source_path": rel(out_path),
                    "bridge_lane": lane,
                    "source_basename": str(row["basename"]),
                    "source_experiment": str(row["experiment"]),
                    "source_target": str(row["target_norm"]),
                    "source_family": str(row["family"]),
                    "source_quadrant": str(row["outcome_quadrant"]),
                    "source_failure_mode": str(row["failure_mode"]),
                    "multiplier": float(mult),
                    "source_actual_p90": float(row["actual_p90"]),
                    "source_null_strict_rate": float(row["null_strict_rate"]),
                    "nonzero_cells": int(np.count_nonzero(np.abs(applied) > 1.0e-12)),
                    "nonzero_rows": int(np.count_nonzero(np.max(np.abs(applied), axis=1) > 1.0e-12)),
                    "mean_abs_delta": float(np.mean(np.abs(applied))),
                    "max_abs_delta": float(np.max(np.abs(applied))),
                    **target_stats,
                }
            )
    return pd.DataFrame(rows), deltas


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in candidate_meta["basename"]]
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    score_cols = [
        "basename",
        "promotion_decision",
        "strict_promote_gate",
        "info_sensor_gate",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    merged = candidate_meta.merge(scores[score_cols], on="basename", how="left")
    return merged.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    info = prefilter[
        (~prefilter["strict_promote_gate"].map(as_bool))
        & prefilter["info_sensor_gate"].map(as_bool)
        & prefilter["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    source_best = (
        prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["bridge_lane", "source_basename"], as_index=False)
        .head(2)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 2),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 4),
            source_best,
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL)
    return selected.drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()

    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        applied = deltas[basename]
        source_path = OUT / basename
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_TEST_NULL_REPS):
                null_path = write_null_candidate(current, applied, source_path, meta, mode, rep)
                null_paths.append(null_path)
                null_rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": null_path.name,
                        "null_path": rel(null_path),
                        "mode": mode,
                        "rep": rep,
                    }
                )

    null_map = pd.DataFrame(null_rows)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
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
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].map(as_bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        for _, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        ready = bool(
            old_strict
            and null_strict_rate <= 0.10
            and p90_dominance >= 0.80
            and mean_dominance >= 0.70
            and worst_mode >= 0.55
        )
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
                "final_decision": "public_free_submission_ready"
                if ready
                else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "actual_p90", "mean_dominance"],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(base_rows: pd.DataFrame, prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    lane_summary = (
        governor.groupby("bridge_lane", dropna=False)
        .agg(
            n=("basename", "count"),
            ready=("public_free_submission_ready", "sum"),
            old_strict=("old_strict_promote", "sum"),
            min_null_strict_rate=("null_strict_rate", "min"),
            best_actual_p90=("actual_p90", "min"),
            best_actual_mean=("actual_mean", "min"),
            best_p90_dominance=("p90_dominance", "max"),
            best_mean_dominance=("mean_dominance", "max"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        if not governor.empty
        else pd.DataFrame()
    )
    near_cols = [
        "bridge_lane",
        "source_experiment",
        "source_target",
        "source_family",
        "multiplier",
        "old_strict_promote",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "public_free_submission_ready",
        "basename",
    ]
    lines = [
        "# E299 Visibility/Null Bridge Scan",
        "",
        "Public LB는 사용하지 않았다. E298 near-miss 후보를 logit-space로 미세 rescale하고 matched null governor를 다시 적용했다.",
        "",
        "## Counts",
        "",
        f"- base rows: `{len(base_rows)}`",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict prefilter candidates: `{int(prefilter['strict_promote_gate'].map(as_bool).sum()) if not prefilter.empty else 0}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        "## Lane Summary",
        "",
        md_table(
            lane_summary,
            [
                "bridge_lane",
                "n",
                "ready",
                "old_strict",
                "min_null_strict_rate",
                "best_actual_p90",
                "best_actual_mean",
                "best_p90_dominance",
                "best_mean_dominance",
                "best_worst_mode",
            ],
            n=20,
        ),
        "",
        "## Best Governor Rows",
        "",
        md_table(governor, near_cols, n=30),
        "",
        "## Interpretation",
        "",
    ]
    if len(ready):
        lines += [
            "- A public-free ready bridge exists. This is the next candidate lane to inspect for movement anatomy and duplicate risk.",
        ]
    else:
        lines += [
            "- No rescaled near-miss crossed `selector-visible + null-rare`.",
            "- The E298 gap is not just a coarse amplitude-grid artifact for the tested near-miss families.",
            "- Next work should change placement geometry or train the action outcome target, not run another scale sweep.",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(PREFILTER_OUT)}`",
        f"- `{rel(GOVERNOR_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    atlas = pd.read_csv(ATLAS_IN)
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    meta = align_meta_to_current()
    base_rows = select_base_rows(atlas)
    candidate_meta, deltas = generate_candidates(base_rows, current)
    prefilter = score_prefilter(candidate_meta, current) if not candidate_meta.empty else candidate_meta
    selected = select_for_null(prefilter)
    selected, null_map, governor = run_governor(selected, deltas, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())

    candidate_meta.to_csv(CANDIDATE_OUT, index=False)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not null_map.empty:
        null_map.to_csv(NULL_MAP_OUT, index=False)
    write_report(base_rows, prefilter, selected, governor)

    ready_n = int(governor["public_free_submission_ready"].map(as_bool).sum()) if not governor.empty else 0
    strict_n = int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0
    print(f"base_rows={len(base_rows)} generated={len(prefilter)} strict={strict_n} null_eval={len(selected)} ready={ready_n}")
    if not governor.empty:
        print(f"best_null={governor['null_strict_rate'].min():.6f} best_p90={governor['actual_p90'].min():.9f}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
