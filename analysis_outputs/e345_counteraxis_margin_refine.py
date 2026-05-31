#!/usr/bin/env python3
"""E345: margin refinement for the E344 counter-axis lifestyle latent.

E344 produced the first full local-gate submission candidate, but its bad-axis
margin is narrow.  This experiment does not search a new model family.  It
stress-tests the exact E344 world model by asking whether the same hidden
lifestyle-state + E315 counter-axis structure has a stable neighborhood.

If the E344 candidate is a real local basin, small changes to counter weight
and veto strength should keep selector visibility while widening either p90 or
bad-axis margin.  If it is a knife-edge, strict candidates should disappear or
become movement-null-common.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e345_counteraxis_refine_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e337_residual_lifestyle_cluster_state import bad_axes, cell_bad_veto, center_by_target, cos, target_abs  # noqa: E402
from e344_counter_axis_signtransfer import select_counter_sources, select_e342_sources  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 345
EPS = 1.0e-12
CAP = 0.18
MAX_E342_SOURCES = 8
MAX_COUNTER_SOURCES = 4
MAX_NULL_CANDIDATES = 40
NULL_REPS = 4

SOURCE_OUT = OUT / "e345_counteraxis_refine_sources.csv"
CANDIDATE_OUT = OUT / "e345_counteraxis_refine_candidates.csv"
SCORE_OUT = OUT / "e345_counteraxis_refine_scores.csv"
ANATOMY_OUT = OUT / "e345_counteraxis_refine_anatomy.csv"
MOVE_NULL_OUT = OUT / "e345_counteraxis_refine_movement_nulls.csv"
REPORT_OUT = OUT / "e345_counteraxis_refine_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.extend([ROOT / raw, OUT / raw.name, OUT / str(path_or_name)])
    for path in candidates:
        if path.exists():
            return path
    return None


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    cand = load_sub_frame(path, base[KEYS]).sort_values(KEYS).reset_index(drop=True)
    return logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0)))
    path = OUT / f"submission_e345_counterrefine_{safe_id(candidate_id, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def entropy(weights: np.ndarray) -> float:
    x = np.abs(np.asarray(weights, dtype=np.float64))
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def target_mask(names: list[str]) -> np.ndarray:
    mask = np.zeros((1, len(TARGETS)), dtype=np.float64)
    for name in names:
        mask[:, TARGETS.index(name)] = 1.0
    return mask


def refine_variants(source: np.ndarray, counter: np.ndarray, weight: float, veto_strength: float, e323_bad: np.ndarray, e216_bad: np.ndarray) -> dict[str, np.ndarray]:
    patch = float(weight) * np.asarray(counter, dtype=np.float64)
    bad_mask = ((source * e323_bad) > 0.0) | ((source * e216_bad) > 0.0)
    source_active = np.sum(np.abs(source), axis=1, keepdims=True) > EPS
    no_q2 = patch.copy()
    no_q2[:, TARGETS.index("Q2")] = 0.0
    q1_q2_s1 = patch * target_mask(["Q1", "Q2", "S1"])
    q1_s1 = patch * target_mask(["Q1", "S1"])
    joint = source + patch
    variants = {
        "joint_cellveto": cell_bad_veto(joint, e323_bad, e216_bad, strength=veto_strength),
        "joint_centered": center_by_target(cell_bad_veto(joint, e323_bad, e216_bad, strength=veto_strength)),
        "counter_veto_add": source + cell_bad_veto(patch, e323_bad, e216_bad, strength=veto_strength),
        "badcell_patch": source + patch * bad_mask,
        "source_rows_only": source + patch * source_active,
        "preserve_q2_cellveto": cell_bad_veto(source + no_q2, e323_bad, e216_bad, strength=veto_strength),
        "q1q2s1_counter": cell_bad_veto(source + q1_q2_s1, e323_bad, e216_bad, strength=veto_strength),
        "q1s1_counter": cell_bad_veto(source + q1_s1, e323_bad, e216_bad, strength=veto_strength),
    }
    return {name: val for name, val in variants.items() if float(np.sum(np.abs(val))) > EPS}


def source_pools() -> tuple[pd.DataFrame, pd.DataFrame]:
    e342 = select_e342_sources().head(MAX_E342_SOURCES).copy()
    counters = select_counter_sources()
    counters = counters[counters["family"].eq("e315_human_ready_composition")].copy()
    counters = counters.sort_values(
        ["incremental_bad_axis_vs_current", "pred_delta_vs_current_p90"],
        ascending=[True, True],
    ).head(MAX_COUNTER_SOURCES)
    sources = pd.concat(
        [
            e342.assign(pool="e342"),
            counters.assign(pool="counter"),
        ],
        ignore_index=True,
        sort=False,
    )
    sources.to_csv(SOURCE_OUT, index=False)
    return e342.reset_index(drop=True), counters.reset_index(drop=True)


def materialize_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    base = load_current()
    base_logit, e323_bad, e216_bad = bad_axes(base)
    e342_sources, counters = source_pools()
    if e342_sources.empty or counters.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base, base_logit, e323_bad, e216_bad

    delta_cache: dict[str, np.ndarray] = {}

    def get_delta(rec: dict[str, Any]) -> np.ndarray:
        name = str(rec["basename"])
        if name not in delta_cache:
            path = locate(rec.get("file", name))
            if path is None:
                raise FileNotFoundError(name)
            delta_cache[name] = load_delta(path, base, base_logit)
        return delta_cache[name]

    weights = [0.075, 0.085, 0.095, 0.100, 0.105, 0.115, 0.125, 0.140, 0.160]
    veto_strengths = [0.15, 0.20, 0.25, 0.30, 0.35, 0.45]
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for src in e342_sources.to_dict("records"):
        src_delta = get_delta(src)
        src_rows = np.sum(np.abs(src_delta), axis=1) > EPS
        for counter in counters.to_dict("records"):
            counter_delta = get_delta(counter)
            counter_rows = np.sum(np.abs(counter_delta), axis=1) > EPS
            overlap_rows = int((src_rows & counter_rows).sum())
            for weight in weights:
                for veto_strength in veto_strengths:
                    for variant, direction in refine_variants(src_delta, counter_delta, weight, veto_strength, e323_bad, e216_bad).items():
                        if float(np.max(np.abs(direction))) > CAP * 1.80:
                            continue
                        candidate_id = (
                            f"e342_{Path(src['basename']).stem[:34]}"
                            f"__ctr_{Path(counter['basename']).stem[:34]}"
                            f"__w{weight:.3f}_v{veto_strength:.2f}_{variant}"
                        )
                        path = write_candidate(base, base_logit, direction, candidate_id)
                        paths.append(path)
                        row_abs = np.sum(np.abs(direction), axis=1)
                        rows.append(
                            {
                                "candidate_id": candidate_id,
                                "file": rel(path),
                                "basename": path.name,
                                "recipe": "e344_margin_refine",
                                "variant": variant,
                                "counter_weight": float(weight),
                                "veto_strength": float(veto_strength),
                                "e342_source": src["basename"],
                                "counter_source": counter["basename"],
                                "e342_source_mean": float(src["pred_delta_vs_current_mean"]),
                                "e342_source_p90": float(src["pred_delta_vs_current_p90"]),
                                "e342_source_bad_axis": float(src["incremental_bad_axis_vs_current"]),
                                "counter_source_mean": float(counter["pred_delta_vs_current_mean"]),
                                "counter_source_p90": float(counter["pred_delta_vs_current_p90"]),
                                "counter_source_bad_axis": float(counter["incremental_bad_axis_vs_current"]),
                                "expected_bad_axis_linear": float(src["incremental_bad_axis_vs_current"]) + weight * float(counter["incremental_bad_axis_vs_current"]),
                                "source_active_rows": int(src_rows.sum()),
                                "counter_active_rows": int(counter_rows.sum()),
                                "source_counter_overlap_rows": overlap_rows,
                                "changed_rows": int(np.any(np.abs(direction) > EPS, axis=1).sum()),
                                "changed_cells": int((np.abs(direction) > EPS).sum()),
                                "row_energy_entropy": entropy(row_abs),
                                "mean_abs_logit_delta": float(np.mean(np.abs(direction))),
                                "max_abs_logit_delta": float(np.max(np.abs(direction))),
                                "l1_logit_delta": float(np.sum(np.abs(direction))),
                                "cos_with_e323_bad": cos(direction, e323_bad),
                                "cos_with_e216_bad": cos(direction, e216_bad),
                                **target_abs(direction),
                            }
                        )
    candidates = pd.DataFrame(rows).drop_duplicates("basename").reset_index(drop=True)
    keep = set(candidates["basename"])
    paths = [p for p in paths if p.name in keep]
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths, base, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(path) for path in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores = scores.drop_duplicates("basename", keep="first").reset_index(drop=True)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": cos(delta, e323_bad),
                "cos_with_e216_bad": cos(delta, e216_bad),
                "signed_bad_overlap": float(np.mean((delta * e323_bad > 0.0) | (delta * e216_bad > 0.0))),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_parquet(OUT / "e273_human_diary_state_jepa_audit_features.parquet")
    meta_cols = [c for c in ["subject_id", "dateblock_group", "weekday", "is_weekend", "subject_order"] if c in state.columns and c not in KEYS]
    meta = state[state["split"].eq("test")][KEYS + meta_cols].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    aligned = keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if aligned[meta_cols].isna().any().any():
        raise RuntimeError("test metadata alignment failed")
    return aligned.reset_index(drop=True)


def permute_within_groups(delta: np.ndarray, groups: pd.Series, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64)
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def null_delta(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return arr[rng.permutation(arr.shape[0]), :]
    if mode == "target_perm":
        return arr[:, rng.permutation(arr.shape[1])]
    if mode == "sign_flip":
        return -arr
    if mode == "row_sign":
        return arr * rng.choice([-1.0, 1.0], size=(arr.shape[0], 1))
    if mode == "cell_perm":
        flat = arr.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(arr.shape)
    if mode == "subject_perm":
        return permute_within_groups(arr, meta["subject_id"], seed)
    if mode == "dateblock_perm":
        return permute_within_groups(arr, meta["dateblock_group"], seed)
    raise ValueError(mode)


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    # Stress strict files first, then the best non-strict p90/bad-axis margin
    # files.  E345 is a margin audit, so a narrow bad-axis pass is not enough.
    joined["bad_axis_margin"] = 0.015 - joined["incremental_bad_axis_vs_current"]
    chosen = joined.sort_values(
        ["strict_promote_gate", "bad_axis_margin", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(MAX_NULL_CANDIDATES)
    if chosen.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    NULL_DIR.mkdir(exist_ok=True)
    for rec in chosen.to_dict("records"):
        path = locate(rec.get("file_meta", rec.get("file_score", rec.get("file", ""))))
        if path is None:
            continue
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in modes:
            for rep in range(NULL_REPS):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                out = base.copy()
                out[TARGETS] = clip_prob(expit(np.clip(base_logit + np.clip(nd, -CAP, CAP), -40.0, 40.0)))
                npath = NULL_DIR / f"submission_e345null_{safe_id(Path(rec['basename']).stem, 58)}_{mode}_r{rep}_{short_hash(out)}.csv"
                out.to_csv(npath, index=False)
                null_paths.append(npath)
                null_rows.append({"basename": rec["basename"], "null_basename": npath.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(path) for path in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
                "mode_count": int(part["mode"].nunique()),
                "strict_null_modes": ",".join(sorted(part.loc[part["strict_promote_gate"].astype(bool), "mode"].unique())),
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["actual_strict_promote", "actual_p90_dominance", "actual_mean_dominance", "actual_p90"],
        ascending=[False, False, False, True],
    )
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(candidates: pd.DataFrame, scores: pd.DataFrame, nulls: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta")) if len(non_current) else pd.DataFrame()
    if len(joined):
        joined["bad_axis_margin"] = 0.015 - joined["incremental_bad_axis_vs_current"]
        joined["p90_margin"] = -0.00005 - joined["pred_delta_vs_current_p90"]
    promoted = joined[joined["strict_promote_gate"].astype(bool)] if len(joined) else pd.DataFrame()
    info = joined[joined["info_sensor_gate"].astype(bool)] if len(joined) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_mean_dominance"] >= 0.70)
            & (nulls["actual_p90_dominance"] >= 0.75)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    if len(promoted):
        promote_names = set(promoted["basename"])
        null_safe_promoted = null_safe[null_safe["basename"].isin(promote_names)] if len(null_safe) else pd.DataFrame()
    else:
        null_safe_promoted = pd.DataFrame()
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "bad_axis_margin",
        "p90_margin",
        "variant",
        "counter_weight",
        "veto_strength",
    ]
    lines = [
        "# E345 Counter-Axis Margin Refinement",
        "",
        "## Question",
        "",
        "Is the E344 hidden lifestyle-state + E315 counter-axis candidate a stable local basin, or a narrow knife-edge?",
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe_promoted)}`",
        "",
        "### Strict Selector Candidates",
        "",
        md_table(promoted.sort_values(["p90_margin", "bad_axis_margin"], ascending=[False, False])[score_cols] if len(promoted) else promoted, n=80, floatfmt=".9f"),
        "",
        "### Best Margin Candidates",
        "",
        md_table(joined.sort_values(["strict_promote_gate", "bad_axis_margin", "p90_margin"], ascending=[False, False, False])[score_cols] if len(joined) else joined, n=80, floatfmt=".9f"),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=50, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe_promoted):
        merged = null_safe_promoted.merge(promoted[["basename", "bad_axis_margin", "p90_margin", "pred_delta_vs_current_p90", "incremental_bad_axis_vs_current"]], on="basename", how="left")
        best = merged.sort_values(["p90_margin", "bad_axis_margin"], ascending=[False, False]).iloc[0]
        src_path = locate(best["basename"])
        upload_text = ""
        if src_path is not None:
            tag = str(best["basename"]).replace(".csv", "").split("_")[-1]
            upload_path = OUT / f"submission_e345_counterrefine_lifestyle_{tag}_uploadsafe.csv"
            shutil.copyfile(src_path, upload_path)
            upload_text = f" Use `{rel(upload_path)}` if preferring the refined E345 candidate."
        lines.append(
            f"`{best['basename']}` survives selector and movement-null stress with p90 `{best['pred_delta_vs_current_p90']:.9f}` "
            f"and bad-axis `{best['incremental_bad_axis_vs_current']:.9f}`.{upload_text}"
        )
    elif len(promoted):
        lines.append("Refinement creates strict selector candidates, but none survive movement-null stress. Keep E344 as the safer candidate.")
    elif len(info):
        lines.append("Refinement remains information-sensor only. E344 is a narrow but currently better local candidate.")
    else:
        lines.append("Refinement found no visible neighborhood. This would weaken E344, but that is not observed if E344 itself remains strict.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SOURCE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if CANDIDATE_OUT.exists() and SCORE_OUT.exists() and ANATOMY_OUT.exists():
        candidates = pd.read_csv(CANDIDATE_OUT)
        scores = pd.read_csv(SCORE_OUT).drop_duplicates("basename", keep="first").reset_index(drop=True)
        scores.to_csv(SCORE_OUT, index=False)
        base = load_current()
        base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    else:
        candidates, paths, base, base_logit, e323_bad, e216_bad = materialize_candidates()
        scores = score_paths(paths)
        _anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    if MOVE_NULL_OUT.exists():
        nulls = pd.read_csv(MOVE_NULL_OUT)
    else:
        nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(candidates, scores, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
        joined["bad_axis_margin"] = 0.015 - joined["incremental_bad_axis_vs_current"]
        joined["p90_margin"] = -0.00005 - joined["pred_delta_vs_current_p90"]
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "incremental_bad_axis_vs_current", "bad_axis_margin", "p90_margin", "variant", "counter_weight", "veto_strength"]
        print(joined.sort_values(["strict_promote_gate", "p90_margin", "bad_axis_margin"], ascending=[False, False, False])[cols].head(80).round(9).to_string(index=False))
    if len(nulls):
        print("[movement-null]")
        print(nulls.head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
