from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

FILES = {
    "mixmin": "submission_mixmin_0c916bb4.csv",
    "e72_failed_sparse": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "e85_conservative_floor": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86_structure_retention": "submission_e86_e85_consensus_a3f7c96f.csv",
    "e89_diffuse_tail": "submission_e89_e72decontam_00d7807f.csv",
    "e90_row_coherent": "submission_e90_e72pareto_28925de5.csv",
    "e95_frontier_hardtail": "submission_e95_hardtail_541e3973.csv",
    "e101_q2s3_rollback": "submission_e101_q2s3tail_177569bc.csv",
    "e108_win_amp050": "submission_e108_if_e101win_amp050_079aab57.csv",
    "e108_win_strict_amp038": "submission_e108_if_e101win_strict_amp038_64514c53.csv",
}

PUBLIC_LB = {
    "mixmin": 0.5763066405,
    "e72_failed_sparse": 0.5764077772,
    "e95_frontier_hardtail": 0.5762913298,
}


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 1e-6, 1 - 1e-6)


def logit(x: np.ndarray) -> np.ndarray:
    x = clip(x)
    return np.log(x / (1 - x))


def entropy(x: np.ndarray) -> np.ndarray:
    x = clip(x)
    return -(x * np.log(x) + (1 - x) * np.log(1 - x))


def load_frame(name: str) -> pd.DataFrame:
    path = OUT / FILES[name]
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    return frame[KEYS + TARGETS].copy()


def target_shares(abs_delta: np.ndarray) -> dict[str, float]:
    per_target = abs_delta.sum(axis=0)
    total = float(per_target.sum())
    if total <= 0:
        return {f"share_{target}": 0.0 for target in TARGETS}
    return {f"share_{target}": float(per_target[i] / total) for i, target in enumerate(TARGETS)}


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    av = a.reshape(-1)
    bv = b.reshape(-1)
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom <= 0:
        return math.nan
    return float(np.dot(av, bv) / denom)


def summarize_pair(
    candidate_name: str,
    base_name: str,
    frames: dict[str, pd.DataFrame],
    e95_probs: np.ndarray,
    e95_from_mixmin_logit_delta: np.ndarray,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    cand = frames[candidate_name][TARGETS].to_numpy(dtype=np.float64)
    base = frames[base_name][TARGETS].to_numpy(dtype=np.float64)
    prob_delta = cand - base
    abs_prob = np.abs(prob_delta)
    logit_delta = logit(cand) - logit(base)
    abs_logit = np.abs(logit_delta)
    active = abs_prob > 1e-7
    active_rows = active.any(axis=1)

    e95_extreme = (e95_probs <= 0.15) | (e95_probs >= 0.85)
    e95_confident = (e95_probs <= 0.25) | (e95_probs >= 0.75)
    q_mask = np.array([target.startswith("Q") for target in TARGETS], dtype=bool)
    s_mask = ~q_mask
    q2s3_mask = np.array([target in {"Q2", "S3"} for target in TARGETS], dtype=bool)
    s123_mask = np.array([target in {"S1", "S2", "S3"} for target in TARGETS], dtype=bool)

    shares = target_shares(abs_prob)
    total_l1 = float(abs_prob.sum())
    row_active_counts = active.sum(axis=1)
    subject_counts = (
        frames[candidate_name].loc[active_rows, "subject_id"].value_counts().to_dict()
        if active_rows.any()
        else {}
    )

    row = {
        "candidate": candidate_name,
        "base": base_name,
        "public_lb": PUBLIC_LB.get(candidate_name, math.nan),
        "public_delta_vs_mixmin": (
            PUBLIC_LB.get(candidate_name, math.nan) - PUBLIC_LB["mixmin"]
            if candidate_name in PUBLIC_LB
            else math.nan
        ),
        "active_cells": int(active.sum()),
        "active_rows": int(active_rows.sum()),
        "subjects_touched": int(len(subject_counts)),
        "max_active_cells_per_row": int(row_active_counts.max()) if len(row_active_counts) else 0,
        "max_active_rows_per_subject": int(max(subject_counts.values())) if subject_counts else 0,
        "l1_prob": total_l1,
        "mean_abs_prob": float(abs_prob.mean()),
        "max_abs_prob": float(abs_prob.max()),
        "l1_logit": float(abs_logit.sum()),
        "mean_abs_logit": float(abs_logit.mean()),
        "max_abs_logit": float(abs_logit.max()),
        "entropy_mean_delta": float((entropy(cand) - entropy(base)).mean()),
        "q_l1_share": float(abs_prob[:, q_mask].sum() / total_l1) if total_l1 else 0.0,
        "s_l1_share": float(abs_prob[:, s_mask].sum() / total_l1) if total_l1 else 0.0,
        "q2s3_l1_share": float(abs_prob[:, q2s3_mask].sum() / total_l1) if total_l1 else 0.0,
        "s123_l1_share": float(abs_prob[:, s123_mask].sum() / total_l1) if total_l1 else 0.0,
        "e95_extreme_l1_share": float(abs_prob[e95_extreme].sum() / total_l1) if total_l1 else 0.0,
        "e95_confident_l1_share": float(abs_prob[e95_confident].sum() / total_l1) if total_l1 else 0.0,
        "cosine_with_e95_from_mixmin": (
            cosine(logit_delta, e95_from_mixmin_logit_delta) if base_name == "mixmin" else math.nan
        ),
    }
    row.update(shares)

    details: list[dict[str, object]] = []
    for j, target in enumerate(TARGETS):
        target_active = active[:, j]
        details.append(
            {
                "candidate": candidate_name,
                "base": base_name,
                "target": target,
                "active_cells": int(target_active.sum()),
                "l1_prob": float(abs_prob[:, j].sum()),
                "mean_abs_prob": float(abs_prob[:, j].mean()),
                "max_abs_prob": float(abs_prob[:, j].max()),
                "mean_signed_prob_delta": float(prob_delta[:, j].mean()),
                "l1_logit": float(abs_logit[:, j].sum()),
                "entropy_mean_delta": float((entropy(cand[:, j]) - entropy(base[:, j])).mean()),
                "e95_confident_l1_share": (
                    float(abs_prob[:, j][e95_confident[:, j]].sum() / abs_prob[:, j].sum())
                    if abs_prob[:, j].sum() > 0
                    else 0.0
                ),
            }
        )
    return row, details


def main() -> None:
    frames = {name: load_frame(name) for name in FILES}
    for name, frame in frames.items():
        if not frames["mixmin"][KEYS].equals(frame[KEYS]):
            raise ValueError(f"key mismatch for {name}")

    e95_probs = frames["e95_frontier_hardtail"][TARGETS].to_numpy(dtype=np.float64)
    e95_from_mixmin_logit_delta = logit(e95_probs) - logit(
        frames["mixmin"][TARGETS].to_numpy(dtype=np.float64)
    )

    rows: list[dict[str, object]] = []
    details: list[dict[str, object]] = []
    for candidate_name in FILES:
        for base_name in ["mixmin", "e95_frontier_hardtail"]:
            if candidate_name == base_name:
                continue
            row, detail = summarize_pair(
                candidate_name,
                base_name,
                frames,
                e95_probs,
                e95_from_mixmin_logit_delta,
            )
            rows.append(row)
            details.extend(detail)

    summary = pd.DataFrame(rows).sort_values(["base", "l1_prob", "candidate"])
    target_detail = pd.DataFrame(details).sort_values(["base", "candidate", "target"])

    summary_path = OUT / "e111_sauna_frontier_movement_atlas_summary.csv"
    detail_path = OUT / "e111_sauna_frontier_movement_atlas_target_detail.csv"
    report_path = OUT / "e111_sauna_frontier_movement_atlas_report.md"
    summary.to_csv(summary_path, index=False)
    target_detail.to_csv(detail_path, index=False)

    vs_mixmin = summary[summary["base"].eq("mixmin")].copy()
    vs_e95 = summary[summary["base"].eq("e95_frontier_hardtail")].copy()
    known = vs_mixmin[vs_mixmin["candidate"].isin(PUBLIC_LB)].copy()

    e101 = vs_e95[vs_e95["candidate"].eq("e101_q2s3_rollback")].iloc[0]
    e72 = vs_mixmin[vs_mixmin["candidate"].eq("e72_failed_sparse")].iloc[0]
    e95 = vs_mixmin[vs_mixmin["candidate"].eq("e95_frontier_hardtail")].iloc[0]
    e89 = vs_e95[vs_e95["candidate"].eq("e89_diffuse_tail")].iloc[0]

    report = f"""# E111 Sauna Frontier Movement Atlas

## Question

If the E95 plateau is a hard-tail calibration phenomenon, public-positive movement should look less like a broad model upgrade and more like a sparse target/cell risk edit. This audit observes only submission geometry: no new model, no CV, no feature generation.

## Key Observations

- Known public anchors versus mixmin:
  - E72 failed sparse movement: public delta `{e72['public_delta_vs_mixmin']:+.10f}`, active cells `{int(e72['active_cells'])}`, L1 prob `{e72['l1_prob']:.6f}`, Q-share `{e72['q_l1_share']:.6f}`, S-share `{e72['s_l1_share']:.6f}`, Q2/S3 share `{e72['q2s3_l1_share']:.6f}`, E95-confident share `{e72['e95_confident_l1_share']:.6f}`, cosine with E95 direction `{e72['cosine_with_e95_from_mixmin']:.6f}`.
  - E95 frontier hardtail: public delta `{e95['public_delta_vs_mixmin']:+.10f}`, active cells `{int(e95['active_cells'])}`, L1 prob `{e95['l1_prob']:.6f}`, Q-share `{e95['q_l1_share']:.6f}`, S-share `{e95['s_l1_share']:.6f}`, Q2/S3 share `{e95['q2s3_l1_share']:.6f}`, E95-confident share `{e95['e95_confident_l1_share']:.6f}`.
- E101 relative to E95 changes only `{int(e101['active_cells'])}` cells across `{int(e101['active_rows'])}` rows, Q2/S3 share `{e101['q2s3_l1_share']:.6f}`, S-target share `{e101['s_l1_share']:.6f}`, entropy delta `{e101['entropy_mean_delta']:+.10f}`.
- Full E89 relative to E95 has active cells `{int(e89['active_cells'])}`, L1 prob `{e89['l1_prob']:.6f}`, Q2/S3 share `{e89['q2s3_l1_share']:.6f}`, E95-confident share `{e89['e95_confident_l1_share']:.6f}`.

## Sauna Interpretation

The strange point sharpens: public-positive E95 is not a high-magnitude global model movement. It is target-axis surgery. E72 failed with broad Q/Q3/S4 contamination and low directional cosine to E95, while E95 keeps almost all movement on the S side plus a tiny Q2 component. E101 is even more surgical: it asks only whether E95's selective Q2/S3 cells should roll back toward the older mixmin geometry. Full E89 remains a larger diffuse-tail move, not a cleaner strict successor.

## Belief Update

- Strengthen: the 0.576 plateau is shaped by target-axis hard-tail calibration, especially Q2/S3/S-family movement, not by generic capacity.
- Weaken: broad movement along an apparently good latent/structure direction should be trusted without target/cell tail stress.
- Next kill-test: submit E101, because it is the smallest public sensor that can falsify whether E95's Q2/S3 hardtail localization is over-tight.

## Outputs

- `{summary_path.name}`
- `{detail_path.name}`
"""
    report_path.write_text(report)
    print(f"wrote {summary_path}")
    print(f"wrote {detail_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
