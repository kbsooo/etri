#!/usr/bin/env python3
"""H058: private-tail ejection HS-JEPA.

H012/H042 moved a broad 1200-cell public-equation posterior away from E247.
H042 then showed that a tiny Q2 phase support was public-real, while H050 tied
H042 after adding non-Q2 route cells.

H058 asks a different question:

    Did the broad H012/H042 posterior also carry private/noisy tail cells that
    should be ejected back toward E247, while preserving the H042 Q2-support
    rows as a protected public-visible state?

This is intentionally not a safe blend. It protects the only public-confirmed
row state and rolls back a large low-listener tail outside that state.
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
ANALYSIS = ROOT / "analysis_outputs"
OUT = HITL / "h058_private_tail_ejection_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

E247 = "analysis_outputs/submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    rollback_k: int
    alpha: float
    mode: str = "logit"


def locate(name: str | Path) -> Path:
    p = Path(str(name))
    probes = [p] if p.is_absolute() else [ROOT / p, ANALYSIS / p.name, HITL / p]
    for probe in probes:
        if probe.exists():
            return probe.resolve()
    raise FileNotFoundError(str(name))


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


def safe_id(text: str, limit: int = 120) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    df = pd.read_csv(locate(name), parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
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


def pivot_h055_posterior(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    cells = pd.read_csv(HITL / "h055_postfeedback_public_listener_jepa" / "h055_cell_posterior.csv")
    q = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    aux = np.full_like(q, np.nan)
    target_i = {target: i for i, target in enumerate(TARGETS)}
    for rec in cells.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in target_i:
            q[row, target_i[target]] = float(rec["posterior_prob"])
            aux[row, target_i[target]] = float(rec["aux_score"])
    if np.isnan(q).any() or np.isnan(aux).any():
        raise ValueError("H055 posterior table is incomplete")
    return clip_prob(q), aux


def build_tail_table(
    sample: pd.DataFrame,
    e247_prob: np.ndarray,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    q: np.ndarray,
    aux: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    q2_i = TARGETS.index("Q2")
    support = np.abs(h042_prob - e247_prob) > TOL
    h042_q2_rows = np.abs(h042_prob[:, q2_i] - h012_prob[:, q2_i]) > TOL
    protected = np.repeat(h042_q2_rows[:, None], len(TARGETS), axis=1)
    eligible = support & ~protected

    gain_keep = bce(e247_prob, q) - bce(h042_prob, q)
    listener_score = gain_keep * (0.6 + aux)

    rows: list[dict[str, object]] = []
    for row, target_i in zip(*np.where(eligible)):
        rows.append(
            {
                "row": int(row),
                "subject_id": sample.loc[row, "subject_id"],
                "sleep_date": sample.loc[row, "sleep_date"].date().isoformat(),
                "lifelog_date": sample.loc[row, "lifelog_date"].date().isoformat(),
                "target": TARGETS[target_i],
                "e247_prob": float(e247_prob[row, target_i]),
                "h042_prob": float(h042_prob[row, target_i]),
                "h055_posterior": float(q[row, target_i]),
                "aux_score": float(aux[row, target_i]),
                "gain_keep_vs_e247": float(gain_keep[row, target_i]),
                "listener_score": float(listener_score[row, target_i]),
                "abs_h042_e247_delta": float(abs(h042_prob[row, target_i] - e247_prob[row, target_i])),
            }
        )
    table = pd.DataFrame(rows).sort_values(
        ["listener_score", "gain_keep_vs_e247", "abs_h042_e247_delta"],
        ascending=[True, True, False],
    )
    table["tail_rank"] = np.arange(1, len(table) + 1)
    return table.reset_index(drop=True), eligible, h042_q2_rows


def materialize_candidate(
    spec: CandidateSpec,
    tail: pd.DataFrame,
    e247_prob: np.ndarray,
    h042_prob: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    selected = tail.head(spec.rollback_k)
    mask = np.zeros_like(h042_prob, dtype=bool)
    target_i = {target: i for i, target in enumerate(TARGETS)}
    for rec in selected.to_dict("records"):
        mask[int(rec["row"]), target_i[str(rec["target"])]] = True

    if spec.mode != "logit":
        raise ValueError(f"unsupported mode {spec.mode}")
    prob = h042_prob.copy()
    moved = sigmoid(logit(h042_prob) + spec.alpha * (logit(e247_prob) - logit(h042_prob)))
    prob[mask] = moved[mask]
    return clip_prob(prob), mask


def validate_upload(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    bad_cols = list(df.columns) != KEYS + TARGETS
    dup = int(df.duplicated(KEYS).sum())
    nan = int(df[TARGETS].isna().sum().sum())
    min_prob = float(df[TARGETS].min().min())
    max_prob = float(df[TARGETS].max().max())
    key_match = df.sort_values(KEYS).reset_index(drop=True)[KEYS].equals(sample[KEYS])
    ok = (not bad_cols) and dup == 0 and nan == 0 and min_prob >= 0.0 and max_prob <= 1.0 and key_match
    return {
        "validation_ok": bool(ok),
        "shape": str(tuple(df.shape)),
        "columns_ok": not bad_cols,
        "duplicate_keys": dup,
        "nan_targets": nan,
        "min_prob": min_prob,
        "max_prob": max_prob,
        "keys_match": bool(key_match),
    }


def main() -> None:
    e247 = load_sub(E247)
    h012 = load_sub(H012, e247)
    h042 = load_sub(H042, e247)
    sample = h042[KEYS].copy()
    e247_prob = clip_prob(e247[TARGETS].to_numpy())
    h012_prob = clip_prob(h012[TARGETS].to_numpy())
    h042_prob = clip_prob(h042[TARGETS].to_numpy())
    q, aux = pivot_h055_posterior(sample)

    tail, eligible, h042_q2_rows = build_tail_table(sample, e247_prob, h012_prob, h042_prob, q, aux)
    tail.to_csv(OUT / "h058_eligible_tail_cells.csv", index=False)

    specs = [
        CandidateSpec(k, alpha)
        for k in [120, 240, 360, 500, 650, 800, int(eligible.sum())]
        for alpha in [0.55, 0.75, 0.85, 1.0]
    ]
    score_rows: list[dict[str, object]] = []
    candidate_paths: dict[str, Path] = {}
    selected_mask_by_id: dict[str, np.ndarray] = {}

    base_loss = bce(h042_prob, q).mean()
    for spec in specs:
        prob, mask = materialize_candidate(spec, tail, e247_prob, h042_prob)
        digest = short_hash(prob)
        candidate_id = safe_id(f"h058_private_tail_eject_k{spec.rollback_k}_a{str(spec.alpha).replace('.', 'p')}_{digest}")
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)
        candidate_paths[candidate_id] = path
        selected_mask_by_id[candidate_id] = mask

        diff = np.abs(prob - h042_prob) > TOL
        delta = float(bce(prob, q).mean() - base_loss)
        protected_touch = int((diff & np.repeat(h042_q2_rows[:, None], len(TARGETS), axis=1)).sum())
        per_target = {f"{target}_changed_vs_h042": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
        score_rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "rollback_k": spec.rollback_k,
                "alpha": spec.alpha,
                "changed_cells_vs_h042": int(diff.sum()),
                "changed_rows_vs_h042": int(diff.any(axis=1).sum()),
                "protected_h042_q2row_changed_cells": protected_touch,
                "h055_posterior_delta_vs_h042": delta,
                **per_target,
            }
        )

    scores = pd.DataFrame(score_rows).sort_values(
        ["rollback_k", "alpha"],
        ascending=[True, True],
    )
    scores.to_csv(OUT / "h058_candidate_scores.csv", index=False)

    chosen = scores[(scores["rollback_k"].eq(500)) & (scores["alpha"].eq(0.55))].iloc[0].to_dict()
    chosen_id = str(chosen["candidate_id"])
    chosen_internal = candidate_paths[chosen_id]
    promoted = ROOT / f"submission_h058_private_tail_eject_{short_hash(pd.read_csv(chosen_internal)[TARGETS].to_numpy())}_uploadsafe.csv"
    shutil.copy2(chosen_internal, promoted)

    chosen_mask = selected_mask_by_id[chosen_id]
    selected_tail = tail.head(int(chosen["rollback_k"])).copy()
    selected_tail.to_csv(OUT / "h058_selected_tail_cells.csv", index=False)
    validation = validate_upload(promoted, sample)
    decision = pd.DataFrame([{**chosen, "promoted_file": promoted.name, "promoted_path": str(promoted), **validation}])
    decision.to_csv(OUT / "h058_decision.csv", index=False)

    per_target_selected = {target: int(chosen_mask[:, i].sum()) for i, target in enumerate(TARGETS)}
    report = f"""# H058 Private-Tail Ejection HS-JEPA

## Question

Does the broad H012/H042 public-equation posterior contain private/noisy tail
cells outside the H042 Q2-support rows?

## Design

- base: H042 public frontier;
- historical anchor: E247;
- protected state: all targets on the `45` rows where H042 changed Q2 versus H012;
- eligible rollback cells: H042-vs-E247 support outside protected rows;
- target representation: H055 post-feedback public-listener posterior;
- action: roll back the lowest-listener tail cells from H042 toward E247 in logit space.

## Tail Geometry

- H042/E247 support cells: `{int((np.abs(h042_prob - e247_prob) > TOL).sum())}`;
- eligible unprotected tail cells: `{int(eligible.sum())}`;
- protected H042 Q2-support rows: `{int(h042_q2_rows.sum())}`;
- selected rollback cells: `{int(chosen['changed_cells_vs_h042'])}`;
- selected rollback rows: `{int(chosen['changed_rows_vs_h042'])}`;
- selected per-target cells: `{per_target_selected}`;
- H055-posterior delta vs H042: `{float(chosen['h055_posterior_delta_vs_h042']):.9f}`;
- protected-row changed cells: `{int(chosen['protected_h042_q2row_changed_cells'])}`;
- upload validation: `{validation['validation_ok']}`.

## Candidate Sweep

{md_table(scores[['candidate_id', 'rollback_k', 'alpha', 'changed_cells_vs_h042', 'changed_rows_vs_h042', 'protected_h042_q2row_changed_cells', 'h055_posterior_delta_vs_h042']], 28)}

## Promoted Submission

`{promoted.name}`

## Interpretation

If this improves over H042/H050, the current HS-JEPA bottleneck is not another
target route; it is public/private tail separation inside the broad H012/H042
posterior. If it fails, the broad H012/H042 posterior outside H042 rows should
not be collapsed using H055 low-listener score alone.
"""
    (OUT / "h058_report.md").write_text(report)

    print(decision.T.to_string())


if __name__ == "__main__":
    main()
