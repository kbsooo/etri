#!/usr/bin/env python3
"""E361: amplitude restore stress for E360 healthy row placements.

Question:
    E360 found row placements with much healthier row-state public-survival, but
    they lost E272 p90 visibility.  Is this only an amplitude problem?

JEPA/data2vec translation:
    context = E360 learned row-action placement
    target  = visible action representation under E272 plus row-state survival
    action  = scale or target-rebalance the same placement, then verify

No public LB is used.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e359_rowplacement_action_health_probe import (  # noqa: E402
    KEY,
    TARGETS,
    clip_prob,
    load_source,
    logit,
    selector_scores,
    sigmoid,
)
from e360_learned_row_action_health_generator import (  # noqa: E402
    rowstate_public_scores,
)
from e358_rowstate_public_survival_audit import load_anchor, load_row_state  # noqa: E402


UPLOAD_PREFIX = "submission_e361_rowaction_amprestore"
E360_SCORES = OUT / "e360_learned_row_action_health_scores.csv"

CANDIDATE_OUT = OUT / "e361_rowaction_amplitude_restore_candidates.csv"
SCORE_OUT = OUT / "e361_rowaction_amplitude_restore_scores.csv"
SELECTION_OUT = OUT / "e361_rowaction_amplitude_restore_selection.csv"
REPORT_OUT = OUT / "e361_rowaction_amplitude_restore_report.md"


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def pct_rank_good(values: pd.Series | np.ndarray, higher_is_better: bool = True) -> pd.Series:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if not higher_is_better:
        s = -s
    return s.rank(pct=True, method="average").fillna(0.5)


def target_multiplier(policy: str, amp: float) -> np.ndarray:
    mult = np.ones(len(TARGETS), dtype=np.float64)
    movers = ["Q1", "Q2", "Q3", "S1", "S3"]
    if policy == "global":
        for target in movers:
            mult[TARGETS.index(target)] = amp
    elif policy == "no_s3":
        for target in ["Q1", "Q2", "Q3", "S1"]:
            mult[TARGETS.index(target)] = amp
        mult[TARGETS.index("S3")] = 1.0
    elif policy == "q_heavy":
        for target in ["Q1", "Q2", "Q3"]:
            mult[TARGETS.index(target)] = amp
        mult[TARGETS.index("S1")] = 1.0 + 0.50 * (amp - 1.0)
        mult[TARGETS.index("S3")] = 1.0
    elif policy == "s1_heavy":
        for target in ["Q1", "Q2", "Q3"]:
            mult[TARGETS.index(target)] = 1.0 + 0.65 * (amp - 1.0)
        mult[TARGETS.index("S1")] = amp
        mult[TARGETS.index("S3")] = 1.0
    elif policy == "q1s1":
        for target in ["Q1", "S1"]:
            mult[TARGETS.index(target)] = amp
        for target in ["Q2", "Q3"]:
            mult[TARGETS.index(target)] = 1.0 + 0.45 * (amp - 1.0)
        mult[TARGETS.index("S3")] = 1.0
    else:
        raise ValueError(policy)
    return mult


def source_rows(scores: pd.DataFrame) -> pd.DataFrame:
    pool = scores.copy()
    pool["source_rank_score"] = (
        1.00 * pct_rank_good(-pool["rowstate_pred_public_loss_mean"])
        + 0.85 * pct_rank_good(-pool["rowstate_pred_public_loss_std"])
        + 0.75 * pct_rank_good(-pool["rowstate_bad_minus_good_exposure"])
        + 0.65 * pct_rank_good(-pool["pred_delta_vs_current_p90"])
        + 0.40 * pct_rank_good(0.015 - pool["incremental_bad_axis_vs_current"].abs())
    )
    chosen = []
    for rule, frame in [
        ("top_actual", pool.sort_values("e360_actual_score", ascending=False).head(12)),
        ("best_rowloss", pool.sort_values("rowstate_pred_public_loss_mean").head(10)),
        ("best_p90", pool.sort_values("pred_delta_vs_current_p90").head(8)),
        ("balanced", pool.sort_values("source_rank_score", ascending=False).head(12)),
    ]:
        tmp = frame.copy()
        tmp["source_rule"] = rule
        chosen.append(tmp)
    out = pd.concat(chosen, ignore_index=True).drop_duplicates("file").reset_index(drop=True)
    return out.head(32)


def write_candidate(anchor: pd.DataFrame, anchor_logit: np.ndarray, base_delta: np.ndarray, rec: pd.Series, amp: float, policy: str) -> dict[str, Any]:
    mult = target_multiplier(policy, amp)
    delta = base_delta * mult[None, :]
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
    variant = f"{rec['variant']}__amp{amp:.2f}_{policy}"
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 104)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    absd = np.abs(delta)
    target_abs = absd.sum(axis=0)
    total = float(target_abs.sum())
    row_abs = absd.sum(axis=1)
    row: dict[str, Any] = {
        "variant": variant,
        "source_variant": rec["variant"],
        "source_rule": rec.get("source_rule", ""),
        "source_id": rec.get("source_id", ""),
        "policy_family": rec.get("policy_family", ""),
        "target_policy": rec.get("target_policy", ""),
        "restore_policy": policy,
        "amp": amp,
        "file": rel(path),
        "basename": path.name,
        "move_l1": float(absd.sum()),
        "move_l2": float(np.linalg.norm(delta.reshape(-1))),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
        "changed_rows_vs_e247": int((row_abs > 1.0e-12).sum()),
        "changed_cells_vs_e247": int((absd > 1.0e-12).sum()),
        "source_e360_p90": float(rec["pred_delta_vs_current_p90"]),
        "source_e360_rowloss": float(rec["rowstate_pred_public_loss_mean"]),
        "source_e360_exposure": float(rec["rowstate_bad_minus_good_exposure"]),
    }
    for i, target in enumerate(TARGETS):
        row[f"abs_{target}"] = float(target_abs[i])
        row[f"share_{target}"] = float(target_abs[i] / total) if total > 0 else 0.0
    return row


def generate_candidates(anchor: pd.DataFrame, anchor_logit: np.ndarray, scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    seen = set()
    scales = [1.05, 1.12, 1.20, 1.30, 1.42, 1.56, 1.72]
    policies = ["global", "no_s3", "q_heavy", "s1_heavy", "q1s1"]
    for _, rec in source_rows(scores).iterrows():
        path = ROOT / str(rec["file"])
        sub = load_source(path, anchor)
        base_delta = logit(sub[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        for amp in scales:
            for policy in policies:
                row = write_candidate(anchor, anchor_logit, base_delta, rec, amp, policy)
                if row["basename"] in seen:
                    Path(ROOT / row["file"]).unlink(missing_ok=True)
                    continue
                seen.add(row["basename"])
                rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def select(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["e361_actual_score"] = (
        1.35 * pct_rank_good(-out["pred_delta_vs_current_p90"])
        + 1.15 * pct_rank_good(-out["rowstate_pred_public_loss_mean"])
        + 0.90 * pct_rank_good(-out["rowstate_pred_public_loss_std"])
        + 0.90 * pct_rank_good(-out["rowstate_bad_minus_good_exposure"])
        + 0.85 * pct_rank_good(0.015 - out["incremental_bad_axis_vs_current"].abs())
        + 0.30 * pct_rank_good(-out["amp"])
    ) / 5.45
    out["e361_submission_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00082)
        & (out["rowstate_pred_public_loss_std"] <= 0.00055)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.145)
    )
    out["e361_visibility_restored_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["rowstate_pred_public_loss_mean"] <= out["source_e360_rowloss"] + 0.00018)
    )
    ranked = out.sort_values(["e361_submission_gate", "e361_actual_score"], ascending=[False, False]).reset_index(drop=True)
    passed = ranked[ranked["e361_submission_gate"]].head(1)
    if passed.empty:
        selected = ranked.head(1).copy()
        selected["decision"] = "no_amprestore_submission"
        selected["selected_uploadsafe_file"] = "none"
        selected["reason"] = "Amplitude restore did not clear strict visibility plus row-state health gates."
    else:
        selected = passed.copy()
        src = ROOT / str(selected.iloc[0]["file"])
        frame = pd.read_csv(src)
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(selected.iloc[0]['variant']), 72)}_{short_hash(frame)}_uploadsafe.csv"
        shutil.copyfile(src, upload)
        selected["decision"] = "select_amprestore_probe"
        selected["selected_uploadsafe_file"] = rel(upload)
        selected["reason"] = "Amplitude-restored row-action placement passed strict gates."
    selected.to_csv(SELECTION_OUT, index=False)
    ranked.to_csv(SCORE_OUT, index=False)
    return selected


def write_report(scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "variant",
        "source_id",
        "policy_family",
        "restore_policy",
        "amp",
        "e361_submission_gate",
        "e361_visibility_restored_gate",
        "e361_actual_score",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "source_e360_p90",
        "source_e360_rowloss",
        "move_l1",
        "share_S3",
        "file",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    summary = (
        scored.groupby(["restore_policy", "amp"], dropna=False)
        .agg(
            n=("variant", "count"),
            submit=("e361_submission_gate", "sum"),
            restored=("e361_visibility_restored_gate", "sum"),
            strict=("strict_promote_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_rowloss=("rowstate_pred_public_loss_mean", "min"),
            best_actual=("e361_actual_score", "max"),
        )
        .reset_index()
        .sort_values(["submit", "restored", "best_actual"], ascending=[False, False, False])
    )
    lines = [
        "# E361 Row-Action Amplitude Restore Stress",
        "",
        "## Question",
        "",
        "E360 made row-state healthier but too small. Can simple amplitude restoration recover visibility without destroying row-state health?",
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "e361_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Scale/Policy Summary",
        "",
        md_table(summary, n=60, floatfmt=".9f"),
        "",
        "## Top Actual-Stress Candidates",
        "",
        md_table(scored[top_cols].head(50), n=50, floatfmt=".9f"),
        "",
        "## Gate-Passing Candidates",
        "",
        md_table(scored[scored["e361_submission_gate"]][top_cols], n=50, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- A pass would mean E360 had found the right row placement, and only amplitude was missing.",
        "- No pass means the health/visibility tradeoff is not a simple scale problem. The next generator must change the cell/target action itself, not only row placement or amplitude.",
        "",
        "## Counts",
        "",
        f"- candidates: `{len(scored)}`",
        f"- strict output candidates: `{int(scored['strict_promote_gate'].sum())}`",
        f"- visibility-restored candidates: `{int(scored['e361_visibility_restored_gate'].sum())}`",
        f"- submission-gate candidates: `{int(scored['e361_submission_gate'].sum())}`",
        "",
        "## Files",
        "",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    e360 = pd.read_csv(E360_SCORES).replace([np.inf, -np.inf], np.nan)
    candidates = generate_candidates(anchor, anchor_logit, e360)
    selected_cols = selector_scores(candidates, anchor)
    scored = rowstate_public_scores(selected_cols, anchor, anchor_logit, state, base_cols, story_cols)
    selected = select(scored)
    scored = pd.read_csv(SCORE_OUT)
    write_report(scored, selected)
    print(f"candidates={len(candidates)}")
    print(selected[["decision", "variant", "selected_uploadsafe_file", "e361_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
