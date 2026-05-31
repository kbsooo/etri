#!/usr/bin/env python3
"""E348: specificity audit for E347 lifestyle-state claims.

E347 promoted a safer E344 neighborhood candidate because its action was
non-randomly aligned with the learned lifestyle-state teacher.  The suspicious
part is that almost every audited candidate had a perfect state-null dominance
and the same dominant axis: ``rs01_Q1_jepa_resid_dateblock``.

This audit asks a stricter question:

    Does the E347 movement align with that lifestyle state more than with
    calendar-only, non-Q1 residual, own-latent, random, or public-bad controls?

No new model is trained and no public LB is used.  The goal is to decide
whether the E347 priority should be trusted, demoted to "generic stateful
E344-family", or replaced by a nearby more specific candidate.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e347_lifestyle_state_candidate_reaudit import (  # noqa: E402
    load_candidate,
    load_lifestyle_teacher,
    locate,
    movement_entropy,
    normalize_dates,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


RNG_SEED = 20260531 + 348
EPS = 1.0e-12
RANDOM_CONTROL_COLS = 128
PERM_REPS = 128

E347_SCORE = OUT / "e347_lifestyle_state_candidate_reaudit_scores.csv"
SCORE_OUT = OUT / "e348_lifestyle_state_specificity_scores.csv"
CONTROL_OUT = OUT / "e348_lifestyle_state_specificity_controls.csv"
REPORT_OUT = OUT / "e348_lifestyle_state_specificity_report.md"
UPLOAD_PREFIX = "submission_e348_specific_lifestyle"
E347_UPLOAD = OUT / "submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv"

warnings.filterwarnings("ignore", message="An input array is constant")

CONTROL_FILES = [
    ("public_bad_e323", "submission_e323_5508f966_uploadsafe.csv"),
    ("public_bad_e216", "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"),
    ("public_bad_e267", "submission_e267_humansocial_tail_balanced_2936100f.csv"),
    ("public_bad_e256", "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"),
    ("mild_e95", "submission_e95_hardtail_541e3973.csv"),
    ("mild_e101", "submission_e101_q2s3tail_177569bc.csv"),
    ("mild_mixmin", "submission_mixmin_0c916bb4.csv"),
    ("severe_final9", "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"),
    ("severe_stage2", "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"),
]


def stable_seed(*parts: object) -> int:
    digest = hashlib.sha1("|".join(map(str, parts)).encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def spearman_abs(a: np.ndarray, b: np.ndarray) -> float:
    corr = pd.Series(np.asarray(a, dtype=np.float64)).corr(pd.Series(np.asarray(b, dtype=np.float64)), method="spearman")
    return 0.0 if not np.isfinite(corr) else abs(float(corr))


def signed_spearman(a: np.ndarray, b: np.ndarray) -> float:
    corr = pd.Series(np.asarray(a, dtype=np.float64)).corr(pd.Series(np.asarray(b, dtype=np.float64)), method="spearman")
    return 0.0 if not np.isfinite(corr) else float(corr)


def max_view_corr(score: np.ndarray, latent: pd.DataFrame, cols: Iterable[str]) -> tuple[float, str, float]:
    vals: list[tuple[float, str, float]] = []
    for col in cols:
        signed = signed_spearman(score, latent[col].to_numpy(dtype=np.float64))
        vals.append((abs(signed), col, signed))
    if not vals:
        return 0.0, "", 0.0
    vals.sort(key=lambda item: item[0], reverse=True)
    return vals[0]


def top_enrichment_abs(score: np.ndarray, latent: pd.DataFrame, cols: Iterable[str]) -> tuple[float, str, float]:
    x = np.asarray(score, dtype=np.float64)
    if np.max(x) <= EPS:
        return 0.0, "", 0.0
    k = min(max(16, int(np.ceil(0.20 * len(x)))), len(x) - 1)
    active = np.zeros(len(x), dtype=bool)
    active[np.argsort(-x)[:k]] = True
    vals: list[tuple[float, str, float]] = []
    for col in cols:
        arr = latent[col].to_numpy(dtype=np.float64)
        diff = float(np.mean(arr[active]) - np.mean(arr[~active]))
        vals.append((abs(diff), col, diff))
    if not vals:
        return 0.0, "", 0.0
    vals.sort(key=lambda item: item[0], reverse=True)
    return vals[0]


def control_thresholds(score: np.ndarray, q1_state: np.ndarray, seed_key: str) -> dict[str, float]:
    rng = np.random.default_rng(stable_seed("controls", seed_key))
    random_corrs = []
    for _ in range(RANDOM_CONTROL_COLS):
        random_corrs.append(spearman_abs(score, rng.normal(size=len(score))))
    perm_corrs = []
    for _ in range(PERM_REPS):
        perm_corrs.append(spearman_abs(score, q1_state[rng.permutation(len(q1_state))]))
    return {
        "random_corr_p95": float(np.quantile(random_corrs, 0.95)),
        "random_corr_max": float(np.max(random_corrs)),
        "permuted_q1_corr_p95": float(np.quantile(perm_corrs, 0.95)),
        "permuted_q1_corr_max": float(np.max(perm_corrs)),
    }


def movement_row_score(delta: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "row_l2": np.sqrt(np.mean(delta**2, axis=1)),
        "row_l1": np.mean(np.abs(delta), axis=1),
        "signed_mean": np.mean(delta, axis=1),
        "q1_abs": np.abs(delta[:, TARGETS.index("Q1")]),
        "q2_abs": np.abs(delta[:, TARGETS.index("Q2")]),
        "q3_abs": np.abs(delta[:, TARGETS.index("Q3")]),
    }


def make_candidate_rows(e347: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "role",
        "family",
        "basename",
        "file",
        "local_mean",
        "local_p90",
        "local_bad_axis",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "e347_gate",
        "e347_rank_score",
    ]
    keep = e347[[c for c in cols if c in e347.columns]].copy()
    keep["candidate_group"] = "e347_family"
    rows = [keep]
    for role, name in CONTROL_FILES:
        path = locate(name)
        if path is None:
            continue
        rows.append(
            pd.DataFrame(
                [
                    {
                        "role": role,
                        "family": "control",
                        "basename": path.name,
                        "file": rel(path),
                        "candidate_group": "public_control",
                    }
                ]
            )
        )
    out = pd.concat(rows, ignore_index=True, sort=False)
    out["path"] = out["file"].map(locate)
    out = out[out["path"].notna()].drop_duplicates("basename", keep="first").reset_index(drop=True)
    return out


def score_one(row: pd.Series, base_logit: np.ndarray, sample: pd.DataFrame, latent: pd.DataFrame, views: dict[str, list[str]], q1_col: str) -> dict[str, object]:
    path = Path(row["path"])
    cand = load_candidate(path, sample)
    delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    scores = movement_row_score(delta)
    primary = scores["row_l2"]
    q1_state = latent[q1_col].to_numpy(dtype=np.float64)

    full_corr, full_col, full_signed = max_view_corr(primary, latent, views["full"])
    q1_corr = spearman_abs(primary, q1_state)
    q1_signed = signed_spearman(primary, q1_state)
    q1_enrich, _, q1_enrich_signed = top_enrichment_abs(primary, latent, [q1_col])
    own_corr, own_col, own_signed = max_view_corr(primary, latent, views["own"])
    nonq1_corr, nonq1_col, nonq1_signed = max_view_corr(primary, latent, views["residual_nonq1"])
    calendar_corr, calendar_col, calendar_signed = max_view_corr(primary, latent, views["calendar"])
    signed_q1_corr = spearman_abs(scores["signed_mean"], q1_state)
    q1_target_corr = spearman_abs(scores["q1_abs"], q1_state)
    thresholds = control_thresholds(primary, q1_state, str(row["basename"]))
    negative_control_max = max(
        calendar_corr,
        thresholds["random_corr_p95"],
        thresholds["permuted_q1_corr_p95"],
    )
    broader_control_max = max(
        own_corr,
        nonq1_corr,
        calendar_corr,
        thresholds["random_corr_p95"],
        thresholds["permuted_q1_corr_p95"],
    )
    q1_specificity_margin = q1_corr - negative_control_max
    q1_broader_margin = q1_corr - broader_control_max
    state_specificity_score = float(
        0.35 * min(max(q1_corr / 0.35, 0.0), 1.0)
        + 0.20 * min(max(q1_enrich / 0.75, 0.0), 1.0)
        + 0.20 * min(max(q1_specificity_margin / 0.10, 0.0), 1.0)
        + 0.15 * float(q1_corr >= thresholds["permuted_q1_corr_p95"] + 0.03)
        + 0.10 * float(q1_corr >= calendar_corr + 0.03)
    )
    out = row.drop(labels=["path"]).to_dict()
    out.update(
        {
            "full_state_corr_abs": full_corr,
            "full_state_corr_col": full_col,
            "full_state_corr_signed": full_signed,
            "q1_state_corr_abs": q1_corr,
            "q1_state_corr_signed": q1_signed,
            "q1_state_enrich_abs": q1_enrich,
            "q1_state_enrich_signed": q1_enrich_signed,
            "own_state_corr_abs": own_corr,
            "own_state_corr_col": own_col,
            "own_state_corr_signed": own_signed,
            "nonq1_residual_corr_abs": nonq1_corr,
            "nonq1_residual_corr_col": nonq1_col,
            "nonq1_residual_corr_signed": nonq1_signed,
            "calendar_corr_abs": calendar_corr,
            "calendar_corr_col": calendar_col,
            "calendar_corr_signed": calendar_signed,
            "signed_mean_q1_state_corr_abs": signed_q1_corr,
            "q1_target_q1_state_corr_abs": q1_target_corr,
            "random_corr_p95": thresholds["random_corr_p95"],
            "random_corr_max": thresholds["random_corr_max"],
            "permuted_q1_corr_p95": thresholds["permuted_q1_corr_p95"],
            "permuted_q1_corr_max": thresholds["permuted_q1_corr_max"],
            "negative_control_max_corr": negative_control_max,
            "broader_control_max_corr": broader_control_max,
            "q1_specificity_margin": q1_specificity_margin,
            "q1_broader_specificity_margin": q1_broader_margin,
            "q1_specificity_pass": bool(q1_corr >= thresholds["permuted_q1_corr_p95"] + 0.03 and q1_corr >= calendar_corr + 0.03),
            "broad_state_not_specific": bool(q1_broader_margin <= 0.02),
            "state_specificity_score": state_specificity_score,
            "row_l2_entropy": movement_entropy(primary),
            "row_l2_q80": float(np.quantile(primary, 0.80)),
            "row_l2_max": float(np.max(primary)),
        }
    )
    return out


def choose_specific_candidate(scores: pd.DataFrame) -> pd.DataFrame:
    work = scores.copy()
    for col in [
        "local_p90",
        "local_bad_axis",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "e347_gate",
    ]:
        if col not in work:
            work[col] = np.nan
    work["e348_gate"] = (
        work["candidate_group"].eq("e347_family")
        & (work["local_p90"].fillna(1.0) <= -0.000049)
        & (work["local_bad_axis"].fillna(9.0) <= 0.01475)
        & (work["public_analog_risk_score"].fillna(9.0) <= 0.0450)
        & (work["public_analog_survival_score"].fillna(0.0) >= 0.48)
        & work["q1_specificity_pass"].astype(bool)
        & (~work["broad_state_not_specific"].astype(bool))
    )
    work["e348_rank_score"] = (
        3.0 * work["state_specificity_score"].fillna(0.0)
        + 2.0 * work["public_analog_survival_score"].fillna(0.0)
        - 10.0 * work["public_analog_risk_score"].fillna(1.0)
        - 1000.0 * work["local_p90"].fillna(0.0)
        - 25.0 * work["local_bad_axis"].fillna(0.0)
        + 0.50 * work["q1_specificity_margin"].fillna(0.0)
    )
    return work.sort_values(["e348_gate", "e348_rank_score"], ascending=[False, False]).reset_index(drop=True)


def materialize(selected: pd.Series) -> Path | None:
    if not bool(selected.get("e348_gate", False)):
        return None
    src = locate(selected["file"])
    if src is None:
        return None
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    if E347_UPLOAD.exists():
        e347 = pd.read_csv(E347_UPLOAD)
        if frame.equals(e347):
            return E347_UPLOAD
    tag = safe_id(str(selected["role"]), 56)
    out = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() == out.resolve():
        return out
    shutil.copyfile(src, out)
    return out


def write_report(scores: pd.DataFrame, selected_path: Path | None) -> None:
    top_cols = [
        "role",
        "candidate_group",
        "e348_gate",
        "e348_rank_score",
        "state_specificity_score",
        "q1_state_corr_abs",
        "q1_state_enrich_abs",
        "q1_specificity_margin",
        "q1_broader_specificity_margin",
        "q1_specificity_pass",
        "broad_state_not_specific",
        "calendar_corr_abs",
        "nonq1_residual_corr_abs",
        "own_state_corr_abs",
        "random_corr_p95",
        "permuted_q1_corr_p95",
        "public_analog_survival_score",
        "public_analog_risk_score",
        "local_p90",
        "local_bad_axis",
    ]
    top_cols = [c for c in top_cols if c in scores.columns]
    e347_rows = scores[scores["candidate_group"].eq("e347_family")].copy()
    controls = scores[scores["candidate_group"].eq("public_control")].copy()
    gate_count = int(scores["e348_gate"].sum()) if "e348_gate" in scores else 0
    best = scores.iloc[0].to_dict() if len(scores) else {}
    selected_text = rel(selected_path) if selected_path is not None else "none"
    e347_selected = scores[scores["role"].eq("e344_nullsafe_top5")].head(1)
    e347_specific = {}
    if len(e347_selected):
        e347_specific = e347_selected.iloc[0].to_dict()
    lines = [
        "# E348 Lifestyle-State Specificity Audit",
        "",
        "## Question",
        "",
        "Is E347's Q1 dateblock lifestyle-state alignment specific enough to justify priority, or is it a generic property of the whole E344/E345 movement family?",
        "",
        "## Method",
        "",
        "- Re-score E347 candidates and public-control movements against separate latent views.",
        "- Positive view: `rs01_Q1_jepa_resid_dateblock`.",
        "- Negative controls: calendar-only max correlation, non-Q1 residual max correlation, own-latent max correlation, random Gaussian columns, and permuted Q1 state.",
        "- Public LB is not used.",
        "",
        "## Top Rows",
        "",
        md_table(scores[top_cols], n=20, floatfmt=".9f"),
        "",
        "## E347 Family",
        "",
        md_table(e347_rows[top_cols], n=16, floatfmt=".9f"),
        "",
        "## Public Controls",
        "",
        md_table(controls[top_cols], n=12, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        f"- E348 gate pass count: `{gate_count}`.",
        f"- Best role: `{best.get('role', '')}`.",
        f"- Selected upload-safe file: `{selected_text}`.",
        f"- E347 selected q1 specificity margin: `{float(e347_specific.get('q1_specificity_margin', np.nan)):.9f}`.",
        f"- E347 selected broader specificity margin: `{float(e347_specific.get('q1_broader_specificity_margin', np.nan)):.9f}`.",
        "",
    ]
    if gate_count:
        lines.extend(
            [
                "At least one E347-family row remains specific to the Q1 dateblock residual state after calendar, random, and permuted-state controls.",
                "If the selected row is still the top row, E347 priority is strengthened. If a different row is selected, E347 should be replaced by the E348 upload-safe row.",
            ]
        )
    else:
        lines.extend(
            [
                "No row passes the stricter specificity gate.",
                "This would demote E347's statefulness claim: the movement may still be a useful E344-family candidate, but the hidden lifestyle-state evidence is not specific enough to drive submission priority.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(CONTROL_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    sample = normalize_dates(base[KEYS].copy())
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(sample)
    q1_col = "rs01_Q1_jepa_resid_dateblock"
    if q1_col not in latent.columns:
        raise RuntimeError(f"missing expected state column: {q1_col}")
    views = {
        "full": state_cols,
        "own": [c for c in state_cols if c not in residual_cols],
        "residual_nonq1": [c for c in residual_cols if c != q1_col],
        "calendar": calendar_cols,
    }

    e347 = pd.read_csv(E347_SCORE)
    candidates = make_candidate_rows(e347)
    rows = []
    for _, row in candidates.iterrows():
        rows.append(score_one(row, base_logit, sample, latent, views, q1_col))
    scored = choose_specific_candidate(pd.DataFrame(rows))
    selected_path = materialize(scored.iloc[0]) if len(scored) else None
    scored["selected_uploadsafe_file"] = ""
    if selected_path is not None and len(scored):
        scored.loc[0, "selected_uploadsafe_file"] = rel(selected_path)
    scored.to_csv(SCORE_OUT, index=False)
    scored[scored["candidate_group"].eq("public_control")].to_csv(CONTROL_OUT, index=False)
    write_report(scored, selected_path)
    print(f"wrote {rel(SCORE_OUT)} {scored.shape}")
    print(f"wrote {rel(CONTROL_OUT)}")
    print(f"wrote {rel(REPORT_OUT)}")
    if selected_path is not None:
        print(f"selected {rel(selected_path)}")
    else:
        print("selected none")


if __name__ == "__main__":
    main()
