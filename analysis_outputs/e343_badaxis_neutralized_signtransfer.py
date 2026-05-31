#!/usr/bin/env python3
"""E343: bad-axis neutralized sign-transfer latent.

E342 produced the first hidden lifestyle-state coalition whose selector p90
crossed the strict visibility threshold, but it missed promotion because the
incremental bad-axis load was slightly above the 0.015 cap.

This experiment keeps the E342 sign-transfer hypothesis fixed and only asks:

    Is the useful shared lifestyle-state signal separable from the known
    public-bad reference axes?

No public LB is used.  The action is a small projection removal from Q2-bad,
residual-bad, LeJEPA-bad, and ordinal reference directions, followed by the
same selector and movement-null stress used in E342.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e343_badaxis_neutralized_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e337_residual_lifestyle_cluster_state import bad_axes, cell_bad_veto, center_by_target, cos, target_abs  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 343
EPS = 1.0e-12
CAP = 0.18
MAX_SOURCE_CANDIDATES = 28
MAX_NULL_CANDIDATES = 24
NULL_REPS = 4

SOURCE_OUT = OUT / "e343_badaxis_neutralized_sources.csv"
CANDIDATE_OUT = OUT / "e343_badaxis_neutralized_candidates.csv"
SCORE_OUT = OUT / "e343_badaxis_neutralized_scores.csv"
ANATOMY_OUT = OUT / "e343_badaxis_neutralized_anatomy.csv"
MOVE_NULL_OUT = OUT / "e343_badaxis_neutralized_movement_nulls.csv"
REPORT_OUT = OUT / "e343_badaxis_neutralized_report.md"


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
    path = OUT / f"submission_e343_badneutral_{safe_id(candidate_id, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def select_sources() -> pd.DataFrame:
    scores = pd.read_csv(OUT / "e342_signtransfer_scores.csv")
    candidates = pd.read_csv(OUT / "e342_signtransfer_candidates.csv")
    nulls_path = OUT / "e342_signtransfer_movement_nulls.csv"
    nulls = pd.read_csv(nulls_path) if nulls_path.exists() else pd.DataFrame()
    merged = scores[~scores["basename"].eq(CURRENT)].merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    if "file_meta" in merged:
        merged["file"] = merged["file_meta"]
    elif "file_score" in merged:
        merged["file"] = merged["file_score"]
    elif "file" not in merged:
        merged["file"] = merged["basename"].map(lambda x: str(OUT / str(x)))
    if len(nulls):
        merged = merged.merge(nulls, on="basename", how="left", suffixes=("", "_null"))
    for col, default in [
        ("actual_p90_dominance", 0.50),
        ("actual_mean_dominance", 0.50),
        ("null_strict_promote_rate", 1.0),
    ]:
        if col not in merged:
            merged[col] = default
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(default)
    pool = merged[
        (merged["pred_delta_vs_current_p90"] < -0.000045)
        & (merged["pred_beats_current_rate"] >= 0.90)
        & (merged["incremental_bad_axis_vs_current"].abs() > 0.015)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.025)
        & merged["file"].notna()
    ].copy()
    pool["null_health"] = (
        0.45 * pool["actual_p90_dominance"]
        + 0.35 * pool["actual_mean_dominance"]
        + 0.20 * (1.0 - pool["null_strict_promote_rate"].clip(0.0, 1.0))
    )
    pool["visibility_margin"] = -pool["pred_delta_vs_current_p90"]
    pool = pool.sort_values(
        ["visibility_margin", "null_health", "pred_delta_vs_current_mean"],
        ascending=[False, False, True],
    ).head(MAX_SOURCE_CANDIDATES)
    pool.to_csv(SOURCE_OUT, index=False)
    return pool.reset_index(drop=True)


def bad_ref_axes(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    _known, _refs, ref_vecs = build_known_and_refs(sample)
    axes: dict[str, np.ndarray] = {}
    for name in ["q2_bad", "resid_bad", "lejepa_bad", "ordinal"]:
        if name in ref_vecs and "stage2" in ref_vecs:
            axis = np.asarray(ref_vecs[name] - ref_vecs["stage2"], dtype=np.float64).reshape(-1)
            norm = float(np.linalg.norm(axis))
            if norm > EPS:
                axes[name] = axis / norm
    return axes


def project_out(delta: np.ndarray, axes: dict[str, np.ndarray], alpha: float, names: list[str]) -> np.ndarray:
    flat = np.asarray(delta, dtype=np.float64).reshape(-1)
    out = flat.copy()
    for name in names:
        axis = axes.get(name)
        if axis is None:
            continue
        out = out - float(alpha) * float(out @ axis) * axis
    return out.reshape(delta.shape)


def entropy(weights: np.ndarray) -> float:
    x = np.abs(np.asarray(weights, dtype=np.float64))
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def materialize_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    sources = select_sources()
    base = load_current()
    base_logit, e323_bad, e216_bad = bad_axes(base)
    axes = bad_ref_axes(base[KEYS])
    if sources.empty:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), [], base, base_logit, e323_bad, e216_bad

    axis_sets = {
        "q2resid": ["q2_bad", "resid_bad"],
        "q2residle": ["q2_bad", "resid_bad", "lejepa_bad"],
        "allbad": ["q2_bad", "resid_bad", "lejepa_bad", "ordinal"],
    }
    alphas = [0.20, 0.35, 0.50, 0.70, 0.90, 1.10]
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for src in sources.to_dict("records"):
        path = locate(src.get("file", src["basename"]))
        if path is None:
            continue
        delta = load_delta(path, base, base_logit)
        for axis_name, axis_cols in axis_sets.items():
            for alpha in alphas:
                cleaned = project_out(delta, axes, alpha, axis_cols)
                variants = {
                    "proj": cleaned,
                    "proj_cellveto": cell_bad_veto(cleaned, e323_bad, e216_bad, strength=0.35),
                    "proj_centered": center_by_target(cell_bad_veto(cleaned, e323_bad, e216_bad, strength=0.35)),
                }
                for variant, direction in variants.items():
                    if float(np.sum(np.abs(direction))) <= EPS:
                        continue
                    candidate_id = f"{Path(src['basename']).stem[:46]}__{axis_name}_a{alpha:.2f}_{variant}"
                    out_path = write_candidate(base, base_logit, direction, candidate_id)
                    paths.append(out_path)
                    row_abs = np.sum(np.abs(direction), axis=1)
                    rows.append(
                        {
                            "candidate_id": candidate_id,
                            "file": rel(out_path),
                            "basename": out_path.name,
                            "source_basename": src["basename"],
                            "source_mean": float(src["pred_delta_vs_current_mean"]),
                            "source_p90": float(src["pred_delta_vs_current_p90"]),
                            "source_bad_axis": float(src["incremental_bad_axis_vs_current"]),
                            "source_beats": float(src["pred_beats_current_rate"]),
                            "source_null_p90_dom": float(src.get("actual_p90_dominance", np.nan)),
                            "axis_set": axis_name,
                            "alpha": float(alpha),
                            "variant": variant,
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
    candidates = pd.DataFrame(rows).drop_duplicates("basename").sort_values(["source_p90", "axis_set", "alpha", "variant"]).reset_index(drop=True)
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
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
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
                npath = NULL_DIR / f"submission_e343null_{safe_id(Path(rec['basename']).stem, 58)}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def write_report(sources: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, nulls: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_mean_dominance"] >= 0.70)
            & (nulls["actual_p90_dominance"] >= 0.75)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    cand_cols = [
        "basename",
        "source_basename",
        "axis_set",
        "alpha",
        "variant",
        "source_p90",
        "source_bad_axis",
        "mean_abs_logit_delta",
        "share_Q1",
        "share_Q2",
        "share_Q3",
    ]
    lines = [
        "# E343 Bad-Axis Neutralized Sign-Transfer Latent",
        "",
        "## Question",
        "",
        "Can E342's selector-visible hidden lifestyle-state signal be separated from the known public-bad reference axes?",
        "",
        "## Source Near-Misses",
        "",
        f"- source candidates: `{len(sources)}`",
        "",
        md_table(sources[["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current", "actual_p90_dominance"]], n=30, floatfmt=".9f")
        if len(sources)
        else "_empty_",
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe)}`",
        "",
        "### Best Selector Scores",
        "",
        md_table(
            non_current.sort_values(
                ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
                ascending=[False, False, True, True],
            )[score_cols]
            if len(non_current)
            else non_current,
            n=50,
            floatfmt=".9f",
        ),
        "",
        "### Candidate Anatomy",
        "",
        md_table(candidates[cand_cols], n=40, floatfmt=".9f") if len(candidates) else "_empty_",
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=40, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        best = null_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(f"`{best['basename']}` is a submission candidate: bad-axis neutralization preserved selector visibility and survived movement-null stress.")
    elif len(promoted):
        lines.append("Bad-axis neutralization creates selector-promoted candidates, but none survive movement-null stress. The cleaned signal is still not submission-safe.")
    elif len(info):
        lines.append("Bad-axis neutralization lowers risk but also weakens selector visibility. Treat as evidence that the useful E342 signal is partly entangled with bad-axis geometry.")
    else:
        lines.append("Projection removal kills the E342 edge. The hidden state currently cannot be separated cleanly from bad-axis movement.")
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
        sources = pd.read_csv(SOURCE_OUT)
        candidates = pd.read_csv(CANDIDATE_OUT)
        scores = pd.read_csv(SCORE_OUT)
        _anat = pd.read_csv(ANATOMY_OUT)
        base = load_current()
        base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    else:
        candidates, paths, base, base_logit, e323_bad, e216_bad = materialize_candidates()
        sources = pd.read_csv(SOURCE_OUT) if SOURCE_OUT.exists() else pd.DataFrame()
        scores = score_paths(paths)
        _anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    if MOVE_NULL_OUT.exists():
        nulls = pd.read_csv(MOVE_NULL_OUT)
    else:
        nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(sources, candidates, scores, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "incremental_bad_axis_vs_current"]
        print(non_current[cols].head(60).round(9).to_string(index=False))
    if len(nulls):
        print("[movement-null]")
        print(nulls.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
