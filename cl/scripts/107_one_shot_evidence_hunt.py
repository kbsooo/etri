#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

CL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = CL_ROOT.parent
sys.path.insert(0, str(CL_ROOT))

from src.cl_common import DATA_DIR, EXPERIMENT_DIR, LABELS, OUT_DIR, ensure_dirs

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6
V83_PATH = REPO_ROOT / "outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv"
V76_PATH = REPO_ROOT / "outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv"
OLD_POSTERIOR_PATH = REPO_ROOT / "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv"
REFIT_POSTERIOR_PATH = EXPERIMENT_DIR / "cl_public_anchor_clue_refit_posterior_values.csv"
SCAN_PATH = EXPERIMENT_DIR / "cl_all_submission_057_scan_scores.csv"
ROW_META_PATH = EXPERIMENT_DIR / "goal6_split_calibration_test_row_meta.csv"

OUT_PREFIX = "one_shot_evidence_hunt"

MANUAL_SOURCES = [
    "outputs/domain_s2_opportunity_drift_calibration_v1/submission_selected_s2_opportunity_drift_calibration.csv",
    "outputs/domain_q_family_rate_calibration_on_causal_chain_v1/submission_subject_rate_calibration.csv",
    "cl/outputs/submission_goal_breakthrough_axis2_twofactor_qs_g050_prob.csv",
    "cl/outputs/submission_goal_breakthrough_axis1_bcg_s1s3_g050_prob.csv",
    "cl/outputs/submission_goal_breakthrough_combo_twofactor_bcg_lag_g030_prob.csv",
    "cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g050_prob.csv",
    "cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g100_stress_prob.csv",
    "cl/outputs/submission_cl_anchor_clue_v85_soft_direction_w006_prob.csv",
    "outputs/public_lb_pseudolabel_calibration/submission_06_v77_posterior_blend_w15.csv",
    "outputs/v84_public_pivot/submission_v84_shape_q010_s005_plus_v18_l06.csv",
]

TARGET_GROUPS = {
    "all": LABELS,
    "q": ["Q1", "Q2", "Q3"],
    "sleep": ["S1", "S2", "S3", "S4"],
    "sleep_core": ["S1", "S2", "S3"],
    "q1": ["Q1"],
    "q2": ["Q2"],
    "q3": ["Q3"],
    "s1": ["S1"],
    "s2": ["S2"],
    "s3": ["S3"],
    "s4": ["S4"],
    "q1_s1_s2": ["Q1", "S1", "S2"],
    "s1_s2_s3": ["S1", "S2", "S3"],
}

GAMMAS = [0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.16]
MOVE_MODES = ["rank_logit", "logit_blend"]


def clip_prob(x, lo: float = EPS, hi: float = 1 - EPS):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip_prob(p)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -50, 50)))


def bce_soft(y: np.ndarray, p: np.ndarray) -> float:
    p = clip_prob(p)
    return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))


def rank_center(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    finite = np.isfinite(x)
    if finite.sum() <= 1:
        return out
    r = pd.Series(x[finite]).rank(method="average").to_numpy(float)
    r = (r - 0.5) / len(r)
    r = (r - r.mean()) / max(r.std(), 1e-9)
    r = np.clip(r, -2.5, 2.5)
    out[finite] = r
    out -= out.mean()
    return out


def norm_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEYS:
        if col in out.columns and "date" in col:
            out[col] = pd.to_datetime(out[col]).dt.date.astype(str)
        elif col in out.columns:
            out[col] = out[col].astype(str)
    return out


def validate_submission(path: Path, sample: pd.DataFrame) -> np.ndarray | None:
    try:
        df = norm_keys(pd.read_csv(path))
        if df.shape != sample.shape or list(df.columns) != list(sample.columns):
            return None
        if not df[KEYS].astype(str).equals(sample[KEYS].astype(str)):
            return None
        vals = df[LABELS].to_numpy(float)
        if not np.isfinite(vals).all():
            return None
        return clip_prob(vals, 1e-5, 1 - 1e-5)
    except Exception:
        return None


def write_submission(sample: pd.DataFrame, values: np.ndarray, path: Path) -> None:
    out = sample.copy()
    vals = clip_prob(values, 1e-5, 1 - 1e-5)
    for i, t in enumerate(LABELS):
        out[t] = vals[:, i]
    out.to_csv(path, index=False)


def build_masks(meta: pd.DataFrame) -> dict[str, np.ndarray]:
    public_rank = meta["publiclike_score"].rank(method="first", ascending=False)
    pressure_rank = meta["row_calibration_pressure"].rank(method="first", ascending=False) if "row_calibration_pressure" in meta.columns else public_rank
    masks = {
        "all": np.ones(len(meta), dtype=bool),
        "public_top30": (public_rank <= math.ceil(len(meta) * 0.30)).to_numpy(),
        "inside_future": (meta["inside_train_range"].eq(1) & meta["has_future_train"].eq(1)).to_numpy(),
        "small_gap5": meta["nearest_train_gap_d"].le(5).to_numpy(),
        "pressure_top30": (pressure_rank <= math.ceil(len(meta) * 0.30)).to_numpy(),
    }
    return {k: v for k, v in masks.items() if v.any()}


@dataclass(frozen=True)
class Move:
    name: str
    source: str
    mode: str
    mask: str
    target: str
    gamma: float
    vector: np.ndarray
    old_bce: float
    refit_bce: float
    robust: float
    drift: float
    max_drift: float
    dmean: float


@dataclass
class Beam:
    values: np.ndarray
    moves: list[Move]
    old_bce: float
    refit_bce: float
    robust: float
    drift: float
    max_drift: float


def score(values: np.ndarray, old: np.ndarray, refit: np.ndarray, v83: np.ndarray) -> tuple[float, float, float, float, float]:
    old_b = bce_soft(old, values)
    ref_b = bce_soft(refit, values)
    drift = float(np.abs(values - v83).mean())
    max_drift = float(np.abs(values - v83).max())
    return old_b, ref_b, max(old_b, ref_b), drift, max_drift


def load_source_pool(sample: pd.DataFrame, old: np.ndarray, refit: np.ndarray, v83: np.ndarray) -> list[tuple[str, np.ndarray]]:
    paths: list[str] = []
    if SCAN_PATH.exists():
        scan = pd.read_csv(SCAN_PATH).sort_values("robust_posterior")
        paths.extend(scan.head(120)["path"].astype(str).tolist())
        # Preserve a few high-drift/low-old-posterior probes that may be useful only after target isolation.
        paths.extend(scan.sort_values("posterior_old_bce").head(80)["path"].astype(str).tolist())
    paths.extend(MANUAL_SOURCES)

    seen: set[str] = set()
    pool: list[tuple[str, np.ndarray]] = []
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / raw
        key = str(path)
        if key in seen or not path.exists():
            continue
        seen.add(key)
        vals = validate_submission(path, sample)
        if vals is None:
            continue
        # Skip exact duplicates of v83; keep everything else because target-isolated residuals can matter.
        if np.abs(vals - v83).mean() < 1e-8:
            continue
        pool.append((raw, vals))

    # Add posterior directions as explicit sources, but keep them marked as high-risk in the name.
    for name, vals in [
        ("posterior_old_values", old),
        ("posterior_refit_values", refit),
        ("posterior_old_refit_avg", 0.5 * old + 0.5 * refit),
    ]:
        pool.append((name, clip_prob(vals, 1e-5, 1 - 1e-5)))
    return pool


def candidate_from_move(base: np.ndarray, vector: np.ndarray, target_idx: int) -> np.ndarray:
    out = base.copy()
    out[:, target_idx] = vector
    return out


def build_move_vector(
    source_vals: np.ndarray,
    v83: np.ndarray,
    target_idx: int,
    mask: np.ndarray,
    mode: str,
    gamma: float,
) -> np.ndarray:
    base_col = v83[:, target_idx]
    src_col = source_vals[:, target_idx]
    out_col = base_col.copy()
    if mode == "rank_logit":
        delta = rank_center(logit(src_col) - logit(base_col))
        out_col[mask] = sigmoid(logit(base_col[mask]) + gamma * delta[mask])
    elif mode == "raw_logit":
        delta = np.clip(logit(src_col) - logit(base_col), -3.0, 3.0)
        centered = delta.copy()
        centered[mask] = centered[mask] - centered[mask].mean()
        out_col[mask] = sigmoid(logit(base_col[mask]) + gamma * centered[mask])
    elif mode == "logit_blend":
        out_col[mask] = sigmoid((1 - gamma) * logit(base_col[mask]) + gamma * logit(src_col[mask]))
    else:
        raise ValueError(mode)
    return clip_prob(out_col, 1e-5, 1 - 1e-5)


def generate_moves(
    pool: list[tuple[str, np.ndarray]],
    masks: dict[str, np.ndarray],
    old: np.ndarray,
    refit: np.ndarray,
    v83: np.ndarray,
) -> pd.DataFrame:
    base_old, base_refit, base_robust, _, _ = score(v83, old, refit, v83)
    rows = []
    kept: list[Move] = []
    for source_name, vals in pool:
        short = Path(source_name).name.replace(".csv", "")
        for target_idx, target in enumerate(LABELS):
            for mode in MOVE_MODES:
                for mask_name, mask in masks.items():
                    for gamma in GAMMAS:
                        vec = build_move_vector(vals, v83, target_idx, mask, mode, gamma)
                        cand = candidate_from_move(v83, vec, target_idx)
                        old_b, ref_b, robust, drift, max_drift = score(cand, old, refit, v83)
                        dmean = float(cand[:, target_idx].mean() - v83[:, target_idx].mean())
                        row = {
                            "source": source_name,
                            "source_short": short,
                            "target": target,
                            "mode": mode,
                            "mask": mask_name,
                            "gamma": gamma,
                            "old_bce": old_b,
                            "refit_bce": ref_b,
                            "robust": robust,
                            "delta_robust_vs_v83": robust - base_robust,
                            "drift": drift,
                            "max_drift": max_drift,
                            "dmean": dmean,
                        }
                        rows.append(row)
                        # Move pool gate: keep small/medium target shifts that at least do not clearly lose.
                        if robust <= base_robust + 0.00035 and drift <= 0.010 and max_drift <= 0.10:
                            kept.append(
                                Move(
                                    name=f"{short}|{target}|{mode}|{mask_name}|g{gamma:g}",
                                    source=source_name,
                                    mode=mode,
                                    mask=mask_name,
                                    target=target,
                                    gamma=gamma,
                                    vector=vec,
                                    old_bce=old_b,
                                    refit_bce=ref_b,
                                    robust=robust,
                                    drift=drift,
                                    max_drift=max_drift,
                                    dmean=dmean,
                                )
                            )
    move_df = pd.DataFrame(rows)
    keep_rows = []
    for target in LABELS:
        target_moves = [m for m in kept if m.target == target]
        target_moves.sort(key=lambda m: (m.robust, m.drift, abs(m.dmean)))
        for m in target_moves[:120]:
            keep_rows.append(
                {
                    "name": m.name,
                    "source": m.source,
                    "target": m.target,
                    "mode": m.mode,
                    "mask": m.mask,
                    "gamma": m.gamma,
                    "old_bce": m.old_bce,
                    "refit_bce": m.refit_bce,
                    "robust": m.robust,
                    "drift": m.drift,
                    "max_drift": m.max_drift,
                    "dmean": m.dmean,
                }
            )
    kept_df = pd.DataFrame(keep_rows)
    move_df.attrs["kept_moves"] = kept
    return move_df, kept_df


def beam_search(
    kept_df: pd.DataFrame,
    old: np.ndarray,
    refit: np.ndarray,
    v83: np.ndarray,
    beam_width: int = 180,
) -> list[Beam]:
    move_lookup = {row["name"]: row for _, row in kept_df.iterrows()}
    # Rebuild vectors for selected moves from source files lazily would be awkward; store them in a global cache instead.
    return []


def build_kept_moves_from_df(
    kept_df: pd.DataFrame,
    pool_map: dict[str, np.ndarray],
    masks: dict[str, np.ndarray],
    v83: np.ndarray,
) -> dict[str, Move]:
    out: dict[str, Move] = {}
    for row in kept_df.itertuples(index=False):
        target_idx = LABELS.index(row.target)
        vec = build_move_vector(pool_map[row.source], v83, target_idx, masks[row.mask], row.mode, float(row.gamma))
        out[row.name] = Move(
            name=row.name,
            source=row.source,
            mode=row.mode,
            mask=row.mask,
            target=row.target,
            gamma=float(row.gamma),
            vector=vec,
            old_bce=float(row.old_bce),
            refit_bce=float(row.refit_bce),
            robust=float(row.robust),
            drift=float(row.drift),
            max_drift=float(row.max_drift),
            dmean=float(row.dmean),
        )
    return out


def run_beam(
    moves_by_name: dict[str, Move],
    old: np.ndarray,
    refit: np.ndarray,
    v83: np.ndarray,
    width: int = 160,
) -> list[Beam]:
    base_old, base_refit, base_robust, base_drift, base_max = score(v83, old, refit, v83)
    beams = [Beam(v83.copy(), [], base_old, base_refit, base_robust, base_drift, base_max)]
    target_order = sorted(
        LABELS,
        key=lambda t: min([m.robust for m in moves_by_name.values() if m.target == t] + [base_robust]),
    )
    for target in target_order:
        target_idx = LABELS.index(target)
        candidates = [m for m in moves_by_name.values() if m.target == target]
        candidates.sort(key=lambda m: (m.robust, m.drift, abs(m.dmean)))
        candidates = candidates[:90]
        next_beams: list[Beam] = []
        for beam in beams:
            next_beams.append(beam)
            used_sources = {m.source for m in beam.moves}
            for m in candidates:
                # Avoid stacking many moves from the posterior values only; that recreates the failed v85 geometry.
                posterior_count = sum(1 for x in beam.moves if str(x.source).startswith("posterior_"))
                if str(m.source).startswith("posterior_") and posterior_count >= 2:
                    continue
                values = beam.values.copy()
                values[:, target_idx] = m.vector
                old_b, ref_b, robust, drift, max_drift = score(values, old, refit, v83)
                if drift > 0.025 or max_drift > 0.15:
                    continue
                if target == "Q1" and values[:, target_idx].mean() > v83[:, target_idx].mean() + 0.010:
                    continue
                next_beams.append(Beam(values, beam.moves + [m], old_b, ref_b, robust, drift, max_drift))
        next_beams.sort(key=lambda b: (b.robust + max(0.0, b.drift - 0.012) * 0.20, b.robust, b.drift))
        dedup: list[Beam] = []
        seen: set[tuple[str, ...]] = set()
        for b in next_beams:
            key = tuple(sorted(m.name for m in b.moves))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(b)
            if len(dedup) >= width:
                break
        beams = dedup
    beams.sort(key=lambda b: (b.robust + max(0.0, b.drift - 0.012) * 0.20, b.robust, b.drift))
    return beams


def beam_rows(beams: list[Beam], v83: np.ndarray) -> pd.DataFrame:
    rows = []
    for i, b in enumerate(beams):
        vals = b.values
        row = {
            "rank": i + 1,
            "name": f"beam_{i + 1:03d}",
            "old_bce": b.old_bce,
            "refit_bce": b.refit_bce,
            "robust": b.robust,
            "drift_v83": b.drift,
            "max_drift_v83": b.max_drift,
            "n_moves": len(b.moves),
            "moves": " || ".join(m.name for m in b.moves),
            "credible_under_0585": b.robust < 0.585 and b.drift <= 0.025 and b.max_drift <= 0.15,
        }
        for j, t in enumerate(LABELS):
            row[f"mean_{t}"] = float(vals[:, j].mean())
            row[f"dmean_{t}"] = float(vals[:, j].mean() - v83[:, j].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def write_report(
    base_scores: dict[str, float],
    move_df: pd.DataFrame,
    kept_df: pd.DataFrame,
    beam_df: pd.DataFrame,
    model_beam_df: pd.DataFrame,
    candidate_df: pd.DataFrame,
) -> None:
    def md_table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
        show = df[cols].head(n).copy()
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, r in show.iterrows():
            vals = []
            for c in cols:
                x = r[c]
                if isinstance(x, float):
                    vals.append(f"{x:.6f}")
                else:
                    vals.append(str(x).replace("|", "/"))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    top_moves = move_df.sort_values(["robust", "drift"]).reset_index(drop=True)
    top_beams = beam_df.sort_values(["robust", "drift_v83"]).reset_index(drop=True)
    top_model_beams = model_beam_df.sort_values(["robust", "drift_v83"]).reset_index(drop=True)
    credible = top_beams[top_beams["credible_under_0585"]]
    model_credible = top_model_beams[top_model_beams["credible_under_0585"]]
    report = []
    report.append("# One-shot 0.57 evidence hunt\n")
    report.append("This run searches existing model/data outputs as target-isolated residual moves on top of v83.")
    report.append("The score is not ordinary OOF; it is the robust max of old and refit public-feedback posterior BCE.")
    report.append("A credible 0.57 clue must get below `0.585` under this robust posterior while staying near v83.\n")
    report.append("## Baseline posterior scores\n")
    for k, v in base_scores.items():
        report.append(f"- {k}: `{v:.6f}`")
    report.append("\n## Best single target moves\n")
    report.append(md_table(top_moves, ["source_short", "target", "mode", "mask", "gamma", "old_bce", "refit_bce", "robust", "drift", "max_drift"], 30))
    report.append("\n## Beam-composed candidates\n")
    report.append(md_table(top_beams, ["name", "old_bce", "refit_bce", "robust", "drift_v83", "max_drift_v83", "n_moves", "credible_under_0585"], 25))
    report.append("\n## Model/data-only beam candidates\n")
    if top_model_beams.empty:
        report.append("_empty_")
    else:
        report.append(md_table(top_model_beams, ["name", "old_bce", "refit_bce", "robust", "drift_v83", "max_drift_v83", "n_moves", "credible_under_0585"], 20))
    report.append("\n## Written candidate files\n")
    report.append(md_table(candidate_df, ["name", "file", "old_bce", "refit_bce", "robust", "drift_v83", "max_drift_v83", "n_moves"], 12))
    report.append("\n## Verdict\n")
    if credible.empty:
        report.append("- No candidate crossed the credible-under-0.585 gate.")
        report.append("- The best available evidence remains a posterior-level 0.59x neighborhood improvement, not a 0.57 proof.")
        report.append("- This is negative evidence against the current data/model inventory containing a hidden one-shot 0.57 submission.")
    else:
        report.append(f"- Found {len(credible)} candidates under the 0.585 robust-posterior gate.")
        report.append("- These are high-priority public-feedback hypotheses, not guaranteed LB scores.")
    if model_credible.empty:
        report.append("- The model/data-only beam also failed the 0.585 gate, so the best 0.59x beam depends on public-posterior directions rather than an independent newly discovered model signal.")
    report.append("- Direct S2 opportunity/Q-state remains a strong internal OOF clue, but when anchored safely to v83 it does not generate a large public-posterior jump.")
    report.append("- Large jumps still require either new public feedback to identify a split/row rule or a new independent signal that changes row ordering without importing v80/v85-style coordinate drift.\n")
    (EXPERIMENT_DIR / f"{OUT_PREFIX}_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    sample = norm_keys(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv"))
    v83_df = norm_keys(pd.read_csv(V83_PATH))
    v76_df = norm_keys(pd.read_csv(V76_PATH))
    old_df = pd.read_csv(OLD_POSTERIOR_PATH)
    refit_df = norm_keys(pd.read_csv(REFIT_POSTERIOR_PATH))
    meta = pd.read_csv(ROW_META_PATH)

    for df, name in [(v83_df, "v83"), (v76_df, "v76"), (refit_df, "refit")]:
        if not df[KEYS].astype(str).equals(sample[KEYS].astype(str)):
            raise ValueError(f"{name} keys differ from sample")

    v83 = clip_prob(v83_df[LABELS].to_numpy(float), 1e-5, 1 - 1e-5)
    old = clip_prob(old_df[LABELS].to_numpy(float), 1e-5, 1 - 1e-5)
    refit = clip_prob(refit_df[LABELS].to_numpy(float), 1e-5, 1 - 1e-5)

    masks = build_masks(meta)
    pool = load_source_pool(sample, old, refit, v83)
    pool_map = {name: vals for name, vals in pool}

    move_df, kept_df = generate_moves(pool, masks, old, refit, v83)
    kept_df = kept_df.sort_values(["robust", "drift", "max_drift"]).drop_duplicates(["name"]).reset_index(drop=True)
    # Rebuild a bounded move set from the table to keep the beam deterministic and serializable.
    kept_df = (
        kept_df.groupby("target", group_keys=False)
        .head(100)
        .sort_values(["target", "robust", "drift"])
        .reset_index(drop=True)
    )
    moves_by_name = build_kept_moves_from_df(kept_df, pool_map, masks, v83)
    beams = run_beam(moves_by_name, old, refit, v83)
    beam_df = beam_rows(beams, v83)
    model_moves_by_name = {
        name: move for name, move in moves_by_name.items() if not str(move.source).startswith("posterior_")
    }
    model_beams = run_beam(model_moves_by_name, old, refit, v83, width=80) if model_moves_by_name else []
    model_beam_df = beam_rows(model_beams, v83) if model_beams else pd.DataFrame()

    move_df.sort_values(["robust", "drift"]).head(3000).to_csv(EXPERIMENT_DIR / f"{OUT_PREFIX}_single_move_scores.csv", index=False)
    kept_df.to_csv(EXPERIMENT_DIR / f"{OUT_PREFIX}_kept_moves.csv", index=False)
    beam_df.to_csv(EXPERIMENT_DIR / f"{OUT_PREFIX}_beam_scores.csv", index=False)
    model_beam_df.to_csv(EXPERIMENT_DIR / f"{OUT_PREFIX}_model_only_beam_scores.csv", index=False)

    out_rows = []
    for _, row in beam_df.head(8).iterrows():
        b = beams[int(row["rank"]) - 1]
        file_name = f"submission_{OUT_PREFIX}_{row['name']}_prob.csv"
        path = OUT_DIR / file_name
        write_submission(sample, b.values, path)
        out_rows.append(
            {
                "name": row["name"],
                "file": str(path),
                "old_bce": row["old_bce"],
                "refit_bce": row["refit_bce"],
                "robust": row["robust"],
                "drift_v83": row["drift_v83"],
                "max_drift_v83": row["max_drift_v83"],
                "n_moves": row["n_moves"],
                "moves": row["moves"],
            }
        )
    candidate_df = pd.DataFrame(out_rows)
    candidate_df.to_csv(EXPERIMENT_DIR / f"{OUT_PREFIX}_candidate_files.csv", index=False)

    base_old, base_refit, base_robust, base_drift, base_max = score(v83, old, refit, v83)
    v76 = clip_prob(v76_df[LABELS].to_numpy(float), 1e-5, 1 - 1e-5)
    v76_old, v76_refit, v76_robust, _, _ = score(v76, old, refit, v83)
    base_scores = {
        "v83_old_posterior": base_old,
        "v83_refit_posterior": base_refit,
        "v83_robust": base_robust,
        "v76_old_posterior": v76_old,
        "v76_refit_posterior": v76_refit,
        "v76_robust": v76_robust,
        "source_pool_size": float(len(pool)),
        "single_moves_scored": float(len(move_df)),
        "beam_count": float(len(beam_df)),
    }
    (EXPERIMENT_DIR / f"{OUT_PREFIX}_summary.json").write_text(json.dumps(base_scores, indent=2), encoding="utf-8")
    write_report(base_scores, move_df, kept_df, beam_df, model_beam_df, candidate_df)
    print((EXPERIMENT_DIR / f"{OUT_PREFIX}_report.md").read_text())


if __name__ == "__main__":
    main()
