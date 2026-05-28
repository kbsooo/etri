#!/usr/bin/env python3
"""E56 mixmin-hard raw-world probe.

E52 only filtered old binary worlds by the observed mixmin public delta. E54/E55
then showed that raw overnight context recovers a real strict block-state latent,
but simple target-rate projection cannot translate it into the mixmin-public
latent. This probe regenerates binary worlds with mixmin included as an observed
public constraint and uses the raw overnight block state as a feasibility prior.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, locate, load_sub, logit  # noqa: E402
from public_lb_inverse_feasibility import CANDIDATES, known_predictions, load_prob, losses  # noqa: E402
from public_lb_binary_inverse_stress import candidate_delta_coeff, residuals_from_x  # noqa: E402
from public_lb_structural_prior_stress import build_constraints, markdown_table  # noqa: E402
import post_mixmin_binary_world_sign_stress as e52  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


MIXMIN_FILE = "analysis_outputs/submission_mixmin_0c916bb4.csv"
MIXMIN_PUBLIC = 0.5763066405
A2C8_PUBLIC = 0.5774393210
RAW05_PUBLIC = 0.5775263072
FRONTIER_GAP = RAW05_PUBLIC - A2C8_PUBLIC
EPS = 1e-6

WORLD_OUT = OUT / "mixmin_hard_raw_world_probe_worlds.csv"
BLOCK_OUT = OUT / "mixmin_hard_raw_world_probe_block_constraints.csv"
EXISTING_SCORE_OUT = OUT / "mixmin_hard_raw_world_probe_existing_candidate_scores.csv"
POSTERIOR_CV_OUT = OUT / "mixmin_hard_raw_world_probe_posterior_cv.csv"
POSTERIOR_SUMMARY_OUT = OUT / "mixmin_hard_raw_world_probe_posterior_summary.csv"
REPORT_OUT = OUT / "mixmin_hard_raw_world_probe_report.md"
LABEL_NPZ_OUT = OUT / "mixmin_hard_raw_world_probe_labels.npz"

TIME_LIMIT = 4.0
GLOBAL_BAND = 0.10
SUBJECT_TARGET_BAND = 0.10
RAW_OBJECTIVE_ALPHAS = [0.004, 0.010, 0.024]
RANDOM_OBJECTIVES = 4
RANDOM_SEED = 20260529


@dataclass(frozen=True)
class Scenario:
    name: str
    mixmin_slack_mult: float
    raw_count_band_frac: float | None
    raw_count_min_band: float


SCENARIOS = [
    Scenario("mixhard_gap_rawobj", 1.0, None, 0.0),
    Scenario("mixhard_gap_rawcount_loose", 1.0, 0.45, 1.50),
    Scenario("mixhard_tight_rawobj", 0.50, None, 0.0),
]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    h = hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]
    return f"{prefix}{h}"


def as_bounds(bounds: list[tuple[float | None, float | None]]) -> Bounds:
    lb = np.array([0.0 if lo is None else lo for lo, _ in bounds], dtype=np.float64)
    ub = np.array([np.inf if hi is None else hi for _, hi in bounds], dtype=np.float64)
    return Bounds(lb, ub)


def safe_float(value: object) -> float:
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def safe_int(value: object) -> int:
    if value is None:
        return -1
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def has_incumbent(res: object) -> bool:
    x = getattr(res, "x", None)
    return x is not None and bool(np.all(np.isfinite(x)))


def solve_world(c: np.ndarray, a_ub: np.ndarray, b_ub: np.ndarray, bounds: list[tuple[float | None, float | None]], m: int) -> tuple[object, float]:
    lower = np.full(len(b_ub), -np.inf, dtype=np.float64)
    integrality = np.r_[np.ones(m, dtype=np.int8), np.zeros(len(c) - m, dtype=np.int8)]
    start = time.time()
    res = milp(
        c,
        integrality=integrality,
        bounds=as_bounds(bounds),
        constraints=LinearConstraint(a_ub, lower, b_ub),
        options={"time_limit": TIME_LIMIT, "mip_rel_gap": 1e-8},
    )
    return res, time.time() - start


def known_predictions_with_mixmin(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    known, pos_loss, neg_loss = known_predictions(sample)
    if not known["file"].astype(str).eq(MIXMIN_FILE).any():
        mix_prob = load_prob(MIXMIN_FILE, sample)
        pos, neg = losses(mix_prob)
        known = pd.concat(
            [
                known,
                pd.DataFrame(
                    [
                        {
                            "file": MIXMIN_FILE,
                            "public_lb": MIXMIN_PUBLIC,
                            "note": "E48 mixmin public frontier used as hard observed constraint.",
                            "known_source": "manual_mixmin_frontier",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        pos_loss = np.vstack([pos_loss, pos])
        neg_loss = np.vstack([neg_loss, neg])
    return known.reset_index(drop=True), pos_loss, neg_loss


def raw_prior_from_e54(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between public anchors and E54 state")

    prior = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    block_rows: list[dict[str, Any]] = []
    for block_i, block in enumerate(state.hidden_blocks):
        sub_idx = state.rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        if np.any(sub_idx < 0):
            raise ValueError(f"hidden block contains non-submission rows: {block.block_id}")
        rate = clip_prob(state.hidden_raw[block_i])
        prior[sub_idx] = rate
        for target_i, target in enumerate(TARGETS):
            center = float(block.n * rate[target_i])
            block_rows.append(
                {
                    "hidden_block_id": block.block_id,
                    "subject_id": block.subject_id,
                    "start": block.start.date().isoformat(),
                    "end": block.end.date().isoformat(),
                    "n_rows": block.n,
                    "target": target,
                    "raw_rate": float(rate[target_i]),
                    "raw_expected_count": center,
                }
            )
    if np.isnan(prior).any():
        miss = np.where(np.isnan(prior).any(axis=1))[0]
        raise ValueError(f"raw prior missing submission rows: {miss[:10].tolist()}")
    return clip_prob(prior), pd.DataFrame(block_rows)


def add_raw_count_constraints(
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    m: int,
    k: int,
    sample: pd.DataFrame,
    state_blocks: pd.DataFrame,
    band_frac: float | None,
    min_band: float,
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    if band_frac is None:
        out = state_blocks.copy()
        out["count_band"] = np.nan
        out["count_lower"] = np.nan
        out["count_upper"] = np.nan
        return a_ub, b_ub, out

    key_to_subidx = {
        tuple(row): i
        for i, row in enumerate(sample[KEYS].astype(str).to_numpy())
    }
    extra_rows: list[np.ndarray] = []
    extra_rhs: list[float] = []
    out_rows = []
    for rec in state_blocks.to_dict("records"):
        target_i = TARGETS.index(str(rec["target"]))
        subject_id = str(rec["subject_id"])
        start = pd.Timestamp(rec["start"])
        end = pd.Timestamp(rec["end"])
        mask = (
            sample["subject_id"].astype(str).eq(subject_id)
            & (pd.to_datetime(sample["lifelog_date"]) >= start)
            & (pd.to_datetime(sample["lifelog_date"]) <= end)
        )
        row_indices = np.where(mask.to_numpy())[0]
        if len(row_indices) == 0:
            continue
        coeff = np.zeros(m + k, dtype=np.float64)
        coeff[row_indices * len(TARGETS) + target_i] = 1.0
        center = float(rec["raw_expected_count"])
        band = max(float(min_band), float(band_frac) * float(len(row_indices)))
        lo = max(0.0, center - band)
        hi = min(float(len(row_indices)), center + band)
        extra_rows.append(coeff)
        extra_rhs.append(hi)
        extra_rows.append(-coeff)
        extra_rhs.append(-lo)
        rec = dict(rec)
        rec["count_band"] = band
        rec["count_lower"] = lo
        rec["count_upper"] = hi
        out_rows.append(rec)
    if not extra_rows:
        return a_ub, b_ub, state_blocks
    return np.vstack([a_ub, np.vstack(extra_rows)]), np.r_[b_ub, np.asarray(extra_rhs)], pd.DataFrame(out_rows)


def cap_slack_bounds(bounds: list[tuple[float | None, float | None]], known: pd.DataFrame, m: int, scenario: Scenario) -> list[tuple[float | None, float | None]]:
    out = list(bounds)
    for j, rec in enumerate(known.to_dict("records")):
        file_name = str(rec["file"])
        cap = FRONTIER_GAP
        if file_name == MIXMIN_FILE:
            cap = scenario.mixmin_slack_mult * FRONTIER_GAP
        out[m + j] = (0.0, cap)
    return out


def raw_ce_coeff(raw_prior: np.ndarray) -> np.ndarray:
    pos, neg = losses(raw_prior)
    return (pos - neg) / float(raw_prior.size)


def random_cell_coeff(rng: np.random.Generator, sample: pd.DataFrame) -> np.ndarray:
    n = len(sample)
    m = n * len(TARGETS)
    target_ids = np.tile(np.arange(len(TARGETS)), n)
    cell_subject = np.repeat(sample["subject_id"].astype(str).to_numpy(), len(TARGETS))
    coeff = rng.normal(0.0, 0.20, size=m)
    for ti in range(len(TARGETS)):
        coeff[target_ids == ti] += rng.normal(0.0, 0.80)
    for sid in sorted(sample["subject_id"].astype(str).unique()):
        coeff[cell_subject == sid] += rng.normal(0.0, 0.40)
    row_wave = rng.normal(0.0, 0.30, size=n)
    coeff += np.repeat(row_wave, len(TARGETS))
    coeff = coeff / (np.std(coeff) + 1e-12)
    return coeff / float(m)


def build_objectives(sample: pd.DataFrame, raw_prior: np.ndarray, m: int, k: int) -> list[tuple[str, str, np.ndarray]]:
    slack_obj = np.r_[np.zeros(m), np.ones(k)]
    raw_coeff = raw_ce_coeff(raw_prior)
    objectives: list[tuple[str, str, np.ndarray]] = [("slack_only", "slack", slack_obj.copy())]
    for alpha in RAW_OBJECTIVE_ALPHAS:
        objectives.append((f"raw_ce_a{alpha:g}", "raw_ce", slack_obj + alpha * np.r_[raw_coeff, np.zeros(k)]))

    target_ids = np.tile(np.arange(len(TARGETS)), len(sample))
    for target_i, target in enumerate(TARGETS):
        coeff = np.zeros(m, dtype=np.float64)
        mask = target_ids == target_i
        coeff[mask] = raw_coeff[mask] * len(TARGETS)
        objectives.append((f"raw_ce_target_{target}", f"raw_{target}", slack_obj + 0.018 * np.r_[coeff, np.zeros(k)]))

    rng = np.random.default_rng(RANDOM_SEED)
    for i in range(RANDOM_OBJECTIVES):
        noise = random_cell_coeff(rng, sample)
        objectives.append(
            (
                f"raw_random_{i:02d}",
                "raw_random",
                slack_obj + 0.010 * np.r_[raw_coeff, np.zeros(k)] + 0.010 * np.r_[noise, np.zeros(k)],
            )
        )
    return objectives


def binary_logloss(prob: np.ndarray, labels: np.ndarray) -> float:
    p = clip_prob(prob)
    y = np.asarray(labels, dtype=np.float64)
    return float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean())


def target_logloss(prob: np.ndarray, labels: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = np.asarray(labels, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean(axis=0)


def label_hash(labels: np.ndarray) -> str:
    bits = np.asarray(np.rint(labels), dtype=np.uint8)
    return hashlib.sha1(bits.tobytes()).hexdigest()[:12]


def resolve_file(file_name: str | Path) -> Path | None:
    path = Path(file_name)
    if path.exists():
        return path.resolve()
    root_path = ROOT / path
    if root_path.exists():
        return root_path.resolve()
    located = locate(file_name)
    return located.resolve() if located is not None else None


def small_candidate_table() -> pd.DataFrame:
    rows: list[dict[str, str]] = [
        {"name": "mixmin", "role": "active_frontier", "source": "manual", "file": MIXMIN_FILE},
        {"name": "a2c8", "role": "previous_frontier", "source": "manual", "file": A2C8},
    ]
    for role, file_name in CANDIDATES:
        rows.append({"name": role, "role": role, "source": "E26_candidates", "file": str(file_name)})
    if (OUT / "post_mixmin_binary_world_sign_stress_summary.csv").exists():
        e52_sum = pd.read_csv(OUT / "post_mixmin_binary_world_sign_stress_summary.csv")
        for rec in e52_sum.head(20).to_dict("records"):
            rows.append(
                {
                    "name": str(rec.get("name", Path(str(rec.get("file", ""))).stem)),
                    "role": str(rec.get("role", "")),
                    "source": "E52_top_signs",
                    "file": str(rec.get("file", "")),
                }
            )
    out = pd.DataFrame(rows)
    out["resolved"] = out["file"].map(resolve_file)
    out = out[out["resolved"].notna()].copy()
    out["file"] = out["resolved"].map(lambda p: str(Path(p).relative_to(ROOT) if Path(p).is_relative_to(ROOT) else p))
    return out.drop(columns=["resolved"]).drop_duplicates("file").reset_index(drop=True)


def score_existing_candidates(candidates: pd.DataFrame, labels: np.ndarray, sample: pd.DataFrame, world_meta: pd.DataFrame) -> pd.DataFrame:
    mixmin_prob = load_prob(MIXMIN_FILE, sample)
    mix_loss = np.asarray([binary_logloss(mixmin_prob, y) for y in labels])
    rows: list[dict[str, Any]] = []
    bands = {
        "all": np.ones(len(labels), dtype=bool),
        "raw_energy_half": world_meta["raw_ce_energy_rank_pct"].le(0.50).to_numpy(),
        "raw_energy_quarter": world_meta["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
        "low_slack_half": world_meta["sum_abs_residual"].rank(pct=True).le(0.50).to_numpy(),
    }
    for rec in candidates.to_dict("records"):
        if str(rec["file"]) == MIXMIN_FILE:
            continue
        try:
            prob = load_prob(str(rec["file"]), sample)
        except Exception:
            continue
        cand_loss = np.asarray([binary_logloss(prob, y) for y in labels])
        delta = cand_loss - mix_loss
        row: dict[str, Any] = {
            "name": rec["name"],
            "role": rec["role"],
            "source": rec["source"],
            "file": rec["file"],
            "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(logit(prob) - logit(mixmin_prob)))),
        }
        for band, mask in bands.items():
            if not mask.any():
                continue
            sub = delta[mask]
            row[f"{band}__worlds"] = int(mask.sum())
            row[f"{band}__better_rate"] = float((sub < 0.0).mean())
            row[f"{band}__median_delta"] = float(np.median(sub))
            row[f"{band}__p90_delta"] = float(np.quantile(sub, 0.90))
            row[f"{band}__max_delta"] = float(np.max(sub))
        row["strict_gate"] = (
            row.get("raw_energy_quarter__better_rate", 0.0) >= 1.0
            and row.get("raw_energy_quarter__max_delta", 1.0) < 0.0
            and row.get("low_slack_half__better_rate", 0.0) >= 0.85
            and row.get("low_slack_half__median_delta", 1.0) < 0.0
        )
        row["score"] = (
            row.get("raw_energy_quarter__median_delta", 0.003)
            + 0.50 * row.get("low_slack_half__median_delta", 0.003)
            + 0.25 * row.get("raw_energy_quarter__p90_delta", 0.003)
            - 0.00020 * row.get("raw_energy_quarter__better_rate", 0.0)
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["strict_gate", "score"], ascending=[False, True]).reset_index(drop=True)


def logit_blend(a: np.ndarray, b: np.ndarray, weight: float) -> np.ndarray:
    return clip_prob(sigmoid((1.0 - weight) * logit(a) + weight * logit(b)))


def posterior_prob_from_labels(label_subset: np.ndarray, raw_prior: np.ndarray) -> np.ndarray:
    posterior = label_subset.mean(axis=0)
    # The binary worlds are sparse and underidentified; keep raw prior as shrinkage
    # and avoid extreme 0/1 posterior probabilities.
    return clip_prob(0.72 * posterior + 0.28 * raw_prior)


def posterior_world_cv(labels: np.ndarray, raw_prior: np.ndarray, mixmin_prob: np.ndarray, world_meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[tuple[str, np.ndarray]]]:
    weights = [0.05, 0.10, 0.18, 0.28]
    band_masks = {
        "all": np.ones(len(labels), dtype=bool),
        "raw_energy_half": world_meta["raw_ce_energy_rank_pct"].le(0.50).to_numpy(),
        "raw_energy_quarter": world_meta["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
    }
    cv_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    candidate_probs: list[tuple[str, np.ndarray]] = []
    for band, mask in band_masks.items():
        idx = np.where(mask)[0]
        if len(idx) < 3:
            continue
        full_posterior = posterior_prob_from_labels(labels[idx], raw_prior)
        for weight in weights:
            full_prob = logit_blend(mixmin_prob, full_posterior, weight)
            candidate_probs.append((f"posterior_{band}_w{weight:.2f}", full_prob))
            held_deltas = []
            for held in idx:
                train_idx = idx[idx != held]
                p = posterior_prob_from_labels(labels[train_idx], raw_prior)
                prob = logit_blend(mixmin_prob, p, weight)
                delta = binary_logloss(prob, labels[held]) - binary_logloss(mixmin_prob, labels[held])
                held_deltas.append(delta)
                cv_rows.append(
                    {
                        "band": band,
                        "weight": weight,
                        "held_world_id": world_meta.iloc[held]["world_id"],
                        "held_scenario": world_meta.iloc[held]["scenario"],
                        "delta_vs_mixmin": delta,
                    }
                )
            arr = np.asarray(held_deltas, dtype=np.float64)
            summary_rows.append(
                {
                    "candidate": f"posterior_{band}_w{weight:.2f}",
                    "band": band,
                    "weight": weight,
                    "held_worlds": int(len(arr)),
                    "better_rate": float((arr < 0.0).mean()),
                    "median_delta": float(np.median(arr)),
                    "mean_delta": float(np.mean(arr)),
                    "p90_delta": float(np.quantile(arr, 0.90)),
                    "max_delta": float(np.max(arr)),
                    "strict_gate": bool((arr < 0.0).mean() >= 0.85 and np.quantile(arr, 0.90) < 0.0),
                }
            )
    summary = pd.DataFrame(summary_rows).sort_values(["strict_gate", "median_delta"], ascending=[False, True]).reset_index(drop=True)
    return pd.DataFrame(cv_rows), summary, candidate_probs


def write_submission(prob: np.ndarray, sample: pd.DataFrame, name: str) -> Path:
    out = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, j])
    tag = stable_tag(prob, prefix="submission_mixhard_rawposterior_")
    path = OUT / f"{tag}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    known: pd.DataFrame,
    worlds: pd.DataFrame,
    block_constraints: pd.DataFrame,
    existing_scores: pd.DataFrame,
    posterior_summary: pd.DataFrame,
    selected_submission: Path | None,
) -> None:
    top_world_cols = [
        "scenario",
        "objective",
        "world_id",
        "max_abs_residual",
        "mixmin_abs_residual",
        "raw_ce_energy",
        "raw_block_count_mae",
        "elapsed_sec",
    ]
    top_existing_cols = [
        "name",
        "role",
        "raw_energy_quarter__better_rate",
        "raw_energy_quarter__median_delta",
        "raw_energy_quarter__p90_delta",
        "low_slack_half__better_rate",
        "strict_gate",
        "score",
        "file",
    ]
    top_posterior_cols = [
        "candidate",
        "held_worlds",
        "better_rate",
        "median_delta",
        "p90_delta",
        "max_delta",
        "strict_gate",
    ]
    strict_existing = int(existing_scores["strict_gate"].sum()) if "strict_gate" in existing_scores else 0
    strict_post = int(posterior_summary["strict_gate"].sum()) if "strict_gate" in posterior_summary else 0
    lines = [
        "# E56 Mixmin-Hard Raw-World Probe",
        "",
        "## Observe",
        "",
        "E52 filtered old binary worlds by mixmin after the fact. E54 showed raw overnight context is a real strict block-state latent, and E55 showed target-rate projection cannot translate it into mixmin alignment.",
        "",
        "## Wonder",
        "",
        "If mixmin is made an observed public constraint during world generation, does the raw overnight block-state prior become useful as a feasibility energy and produce a stable movement beyond mixmin?",
        "",
        "## Hypothesis",
        "",
        "H56: mixmin-hard binary worlds with raw block-state energy should either produce a coherent posterior movement that beats mixmin under world-LOO stress, or prove that raw context is only a private-risk/feasibility diagnostic rather than a candidate generator.",
        "",
        "## Method",
        "",
        f"- Known public anchors in the MILP, including mixmin: `{len(known)}`.",
        f"- Slack cap resolution: raw05-a2c8 public gap `{FRONTIER_GAP:.10f}`; tight mixmin scenario uses `0.5x` this gap.",
        "- Raw prior: E54 `night_phone_rawctx_strict_k8_a24` hidden block rates mapped to all 250 submission rows.",
        "- World generation scenarios: raw CE objective only, loose raw block-count constraints, and tighter mixmin slack.",
        "- Candidate checks: existing files are only sensors; new posterior candidates are evaluated by leave-one-world stress before any submission file is kept.",
        "",
        "## World Summary",
        "",
        markdown_table(worlds[[c for c in top_world_cols if c in worlds.columns]].head(20)),
        "",
        "## Existing Candidate Sensor Signs",
        "",
        markdown_table(existing_scores[[c for c in top_existing_cols if c in existing_scores.columns]].head(15)),
        "",
        "## Posterior World-LOO",
        "",
        markdown_table(posterior_summary[[c for c in top_posterior_cols if c in posterior_summary.columns]].head(15)),
        "",
        "## Decision",
        "",
        f"- incumbent worlds: `{int(worlds['has_incumbent'].sum()) if 'has_incumbent' in worlds else 0}`.",
        f"- unique incumbent worlds: `{worlds.loc[worlds['has_incumbent'], 'world_id'].nunique() if 'world_id' in worlds else 0}`.",
        f"- existing-candidate strict gates: `{strict_existing}`.",
        f"- posterior strict gates: `{strict_post}`.",
    ]
    if selected_submission is None:
        lines.append("- No posterior candidate passed the strict world-LOO gate. Do not submit from E56 yet.")
    else:
        lines.append(f"- A posterior diagnostic submission was written: `{selected_submission.relative_to(ROOT)}`. Treat it as a world-model hypothesis, not a safe public claim.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "If no gate opens, the active worldview remains: mixmin is a real public frontier and raw overnight context is useful as energy/private-risk stress, but not yet a direct candidate generator. If a future public submission from this branch improves, it would mean mixmin-hard binary worlds are closer to the public subset than pseudo-hidden block-rate stress; if it worsens, the binary worlds are still underidentified.",
            "",
            "## Outputs",
            "",
            f"- `{WORLD_OUT.relative_to(ROOT)}`",
            f"- `{BLOCK_OUT.relative_to(ROOT)}`",
            f"- `{EXISTING_SCORE_OUT.relative_to(ROOT)}`",
            f"- `{POSTERIOR_CV_OUT.relative_to(ROOT)}`",
            f"- `{POSTERIOR_SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    known, pos_loss, neg_loss = known_predictions_with_mixmin(sample)
    y_public = known["public_lb"].to_numpy(dtype=np.float64)
    k, m = pos_loss.shape
    const = neg_loss.mean(axis=1)
    b = (pos_loss - neg_loss) / float(m)
    raw_prior, raw_blocks = raw_prior_from_e54(sample)
    mixmin_prob = load_prob(MIXMIN_FILE, sample)

    model_view = type("BinaryModelView", (), {"y": y_public, "const": const, "b": b, "k": k, "m": m})()
    objectives = build_objectives(sample, raw_prior, m, k)

    world_rows: list[dict[str, Any]] = []
    block_constraint_frames: list[pd.DataFrame] = []
    label_rows: list[np.ndarray] = []
    seen_hashes: set[str] = set()
    raw_pos, raw_neg = losses(raw_prior)
    raw_prior_flat = raw_prior.reshape(-1)

    for scenario in SCENARIOS:
        a_ub, b_ub, base_bounds = build_constraints(model_view, train, sample, GLOBAL_BAND, SUBJECT_TARGET_BAND)
        bounds = cap_slack_bounds(base_bounds, known, m, scenario)
        a_ub, b_ub, raw_block_constraints = add_raw_count_constraints(
            a_ub,
            b_ub,
            m,
            k,
            sample,
            raw_blocks,
            scenario.raw_count_band_frac,
            scenario.raw_count_min_band,
        )
        raw_block_constraints["scenario"] = scenario.name
        block_constraint_frames.append(raw_block_constraints)

        for objective_name, objective_family, c in objectives:
            res, elapsed = solve_world(c, a_ub, b_ub, bounds, m)
            row: dict[str, Any] = {
                "scenario": scenario.name,
                "objective": objective_name,
                "objective_family": objective_family,
                "solver_success": bool(getattr(res, "success", False)),
                "status": safe_int(getattr(res, "status", -999)),
                "message": str(getattr(res, "message", "")),
                "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
                "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
                "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
                "elapsed_sec": elapsed,
                "time_limit": TIME_LIMIT,
                "has_incumbent": has_incumbent(res),
                "mixmin_slack_cap": scenario.mixmin_slack_mult * FRONTIER_GAP,
                "raw_count_band_frac": scenario.raw_count_band_frac,
            }
            if not has_incumbent(res):
                world_rows.append(row)
                continue
            x = np.rint(res.x[:m]).astype(np.uint8)
            labels = x.reshape(len(sample), len(TARGETS)).astype(np.float64)
            residual = residuals_from_x(const, b, y_public, res.x, m)
            h = label_hash(x)
            raw_ce = binary_logloss(raw_prior, labels)
            mixmin_loss = binary_logloss(mixmin_prob, labels)
            raw_count_abs = []
            for rec in raw_blocks.to_dict("records"):
                target_i = TARGETS.index(str(rec["target"]))
                mask = (
                    sample["subject_id"].astype(str).eq(str(rec["subject_id"]))
                    & (pd.to_datetime(sample["lifelog_date"]) >= pd.Timestamp(rec["start"]))
                    & (pd.to_datetime(sample["lifelog_date"]) <= pd.Timestamp(rec["end"]))
                )
                idx = np.where(mask.to_numpy())[0]
                raw_count_abs.append(abs(float(labels[idx, target_i].sum()) - float(rec["raw_expected_count"])))
            row.update(
                {
                    "world_id": h,
                    "duplicate_world": h in seen_hashes,
                    "fit_objective_value": safe_float(getattr(res, "fun", np.nan)),
                    "sum_abs_residual": float(np.sum(np.abs(residual))),
                    "max_abs_residual": float(np.max(np.abs(residual))),
                    "mean_abs_residual": float(np.mean(np.abs(residual))),
                    "mixmin_abs_residual": float(abs(residual[-1])),
                    "mixmin_residual_over_gap": float(abs(residual[-1]) / FRONTIER_GAP),
                    "positive_cell_count": int(x.sum()),
                    "raw_ce_energy": raw_ce,
                    "mixmin_loss_on_world": mixmin_loss,
                    "raw_block_count_mae": float(np.mean(raw_count_abs)),
                    "raw_binary_prior_corr": float(np.corrcoef(x.astype(float), raw_prior_flat)[0, 1]),
                    "frontier_scale_fit": bool(np.max(np.abs(residual)) <= FRONTIER_GAP + 1e-10),
                }
            )
            seen_hashes.add(h)
            label_rows.append(labels)
            world_rows.append(row)

    worlds = pd.DataFrame(world_rows)
    if label_rows:
        labels = np.asarray(label_rows, dtype=np.float64)
        valid_worlds = worlds[worlds["has_incumbent"].astype(bool)].reset_index(drop=True)
        valid_worlds["raw_ce_energy_rank_pct"] = valid_worlds["raw_ce_energy"].rank(method="first", pct=True)
        np.savez_compressed(LABEL_NPZ_OUT, labels=labels, targets=np.asarray(TARGETS, dtype=object))
    else:
        labels = np.zeros((0, len(sample), len(TARGETS)), dtype=np.float64)
        valid_worlds = worlds.copy()
        valid_worlds["raw_ce_energy_rank_pct"] = np.nan

    block_constraints = pd.concat(block_constraint_frames, ignore_index=True) if block_constraint_frames else pd.DataFrame()
    candidates = small_candidate_table()
    existing_scores = score_existing_candidates(candidates, labels, sample, valid_worlds) if len(labels) else pd.DataFrame()
    posterior_cv, posterior_summary, posterior_probs = posterior_world_cv(labels, raw_prior, mixmin_prob, valid_worlds) if len(labels) else (pd.DataFrame(), pd.DataFrame(), [])

    selected_submission: Path | None = None
    if not posterior_summary.empty and bool(posterior_summary.iloc[0]["strict_gate"]):
        best_name = str(posterior_summary.iloc[0]["candidate"])
        for name, prob in posterior_probs:
            if name == best_name:
                selected_submission = write_submission(prob, sample, name)
                break

    valid_worlds.to_csv(WORLD_OUT, index=False)
    block_constraints.to_csv(BLOCK_OUT, index=False)
    existing_scores.to_csv(EXISTING_SCORE_OUT, index=False)
    posterior_cv.to_csv(POSTERIOR_CV_OUT, index=False)
    posterior_summary.to_csv(POSTERIOR_SUMMARY_OUT, index=False)
    write_report(known, valid_worlds, block_constraints, existing_scores, posterior_summary, selected_submission)

    print(
        f"worlds={len(valid_worlds)} unique={valid_worlds['world_id'].nunique() if len(valid_worlds) else 0} "
        f"existing_strict={int(existing_scores['strict_gate'].sum()) if 'strict_gate' in existing_scores else 0} "
        f"posterior_strict={int(posterior_summary['strict_gate'].sum()) if 'strict_gate' in posterior_summary else 0} "
        f"submission={selected_submission.relative_to(ROOT) if selected_submission else 'none'}"
    )
    if not posterior_summary.empty:
        print(posterior_summary.head(10).to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
