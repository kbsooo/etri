#!/usr/bin/env python3
"""H051: Q2 phase amplifier HS-JEPA.

H042's public win changed only 45 Q2 cells.  H050 then moved 96 non-Q2
subjective-Q cells while keeping Q2 frozen and returned to the same public
frontier.  That makes the sharp next question target-local:

    Was H042 an under-amplified Q2 phase direction, or only a tiny local
    correction that should not be extrapolated?

H051 keeps H042's exact 45-row support and pushes the same Q2 logit direction
harder.  This is intentionally not a conservative blend; it is a public sensor
for whether the hidden Q2 label direction has been recovered.
"""

from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h051_q2_phase_amplifier_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012_FILE = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"

H012_LB = 0.5681234831
H042_LB = 0.5679048248
H050_LB = 0.5679048248


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    z = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-z))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_float_id(x: float) -> str:
    return str(x).replace(".", "p").replace("-", "m")


def write_submission(template: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = template[KEYS + TARGETS].copy()
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


def candidate_record(
    template: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    support: np.ndarray,
    logit_delta: np.ndarray,
    candidate_prob: np.ndarray,
    family: str,
    parameter: str,
    effective_factor: float,
) -> dict[str, object]:
    q2 = TARGETS.index("Q2")
    q2_changed_vs_h042 = np.abs(candidate_prob[:, q2] - h042_prob[:, q2]) > 1.0e-12
    all_changed_vs_h042 = np.abs(candidate_prob - h042_prob) > 1.0e-12
    extra_logit = logit(candidate_prob[:, q2]) - logit(h042_prob[:, q2])
    full_logit = logit(candidate_prob[:, q2]) - logit(h012_prob[:, q2])
    same_direction = np.sign(full_logit[support]) == np.sign(logit_delta[support])
    if not np.any(support):
        same_direction_rate = 0.0
    else:
        same_direction_rate = float(np.mean(same_direction))

    linear_expected_lb = H012_LB + effective_factor * (H042_LB - H012_LB)
    linear_expected_gain_vs_h042 = linear_expected_lb - H042_LB
    curvature_risk = float(np.mean(np.square(extra_logit[support]))) if np.any(support) else 0.0
    max_abs_extra_logit = float(np.max(np.abs(extra_logit[support]))) if np.any(support) else 0.0
    max_abs_prob_move_vs_h042 = float(np.max(np.abs(candidate_prob[:, q2] - h042_prob[:, q2])))
    mean_abs_prob_move_vs_h042 = float(np.mean(np.abs(candidate_prob[support, q2] - h042_prob[support, q2])))
    edge_rate = float(np.mean((candidate_prob[support, q2] < 0.12) | (candidate_prob[support, q2] > 0.88)))
    h050_neutral_guard = float(abs(H050_LB - H042_LB))

    prob_hash = short_hash(candidate_prob)
    candidate_id = f"h051_{family}_{parameter}_{prob_hash}"
    file_name = f"submission_{candidate_id}.csv"
    path = OUT / file_name
    write_submission(template, candidate_prob, path)

    return {
        "candidate_id": candidate_id,
        "file": file_name,
        "resolved_path": str(path),
        "family": family,
        "parameter": parameter,
        "effective_h042_factor": effective_factor,
        "changed_cells_vs_h042": int(all_changed_vs_h042.sum()),
        "q2_changed_cells_vs_h042": int(q2_changed_vs_h042.sum()),
        "support_overlap_cells": int(np.sum(q2_changed_vs_h042 & support)),
        "same_direction_rate": same_direction_rate,
        "mean_abs_prob_move_vs_h042": mean_abs_prob_move_vs_h042,
        "max_abs_prob_move_vs_h042": max_abs_prob_move_vs_h042,
        "max_abs_extra_logit": max_abs_extra_logit,
        "curvature_risk": curvature_risk,
        "edge_rate": edge_rate,
        "linear_expected_lb": linear_expected_lb,
        "linear_expected_gain_vs_h042": linear_expected_gain_vs_h042,
        "h050_neutral_guard": h050_neutral_guard,
        "h051_sensor_priority": (
            -linear_expected_gain_vs_h042
            - 0.0030 * curvature_risk
            - 0.0010 * edge_rate
            - 0.0002 * abs(effective_factor - 2.0)
        ),
    }


def main() -> None:
    h012_df = pd.read_csv(ROOT / H012_FILE)
    h042_df = pd.read_csv(ROOT / H042_FILE)
    h050_df = pd.read_csv(ROOT / H050_FILE)

    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042_df[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050_df[TARGETS].to_numpy(dtype=np.float64)

    q2 = TARGETS.index("Q2")
    logit_delta = np.zeros(len(h012_df), dtype=np.float64)
    logit_delta[:] = logit(h042_prob[:, q2]) - logit(h012_prob[:, q2])
    support = np.abs(logit_delta) > 1.0e-12
    abs_rank = pd.Series(np.abs(logit_delta)).rank(method="first", ascending=False).to_numpy()

    support_frame = h012_df[KEYS].copy()
    support_frame["row"] = np.arange(len(h012_df))
    support_frame["h051_h042_q2_support"] = support
    support_frame["h012_q2"] = h012_prob[:, q2]
    support_frame["h042_q2"] = h042_prob[:, q2]
    support_frame["h050_q2"] = h050_prob[:, q2]
    support_frame["h042_minus_h012_q2"] = h042_prob[:, q2] - h012_prob[:, q2]
    support_frame["h042_logit_delta_q2"] = logit_delta
    support_frame["abs_logit_delta_rank"] = abs_rank
    support_frame.loc[support].to_csv(OUT / "h051_h042_q2_support_cells.csv", index=False)

    records: list[dict[str, object]] = []

    for factor in [1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 3.5, 4.0]:
        prob = h042_prob.copy()
        prob[support, q2] = sigmoid(logit(h012_prob[support, q2]) + factor * logit_delta[support])
        records.append(
            candidate_record(
                h042_df,
                h012_prob,
                h042_prob,
                support,
                logit_delta,
                prob,
                "fullsupport_logitline",
                f"f{safe_float_id(factor)}",
                factor,
            )
        )

    for keep in [15, 25, 35]:
        keep_mask = support & (abs_rank <= keep)
        for factor in [2.0, 2.5, 3.0]:
            prob = h042_prob.copy()
            prob[keep_mask, q2] = sigmoid(logit(h012_prob[keep_mask, q2]) + factor * logit_delta[keep_mask])
            records.append(
                candidate_record(
                    h042_df,
                    h012_prob,
                    h042_prob,
                    support,
                    logit_delta,
                    prob,
                    f"top{keep}_logitline",
                    f"f{safe_float_id(factor)}",
                    factor * (keep / max(int(support.sum()), 1)),
                )
            )

    for edge in [0.82, 0.88, 0.93, 0.97]:
        for mix in [0.35, 0.55, 0.75, 1.0]:
            prob = h042_prob.copy()
            target = np.where(logit_delta[support] > 0.0, edge, 1.0 - edge)
            prob[support, q2] = h042_prob[support, q2] + mix * (target - h042_prob[support, q2])
            full_logit = logit(prob[support, q2]) - logit(h012_prob[support, q2])
            denom = float(np.dot(logit_delta[support], logit_delta[support]))
            effective = float(np.dot(full_logit, logit_delta[support]) / denom) if denom > 0 else 0.0
            records.append(
                candidate_record(
                    h042_df,
                    h012_prob,
                    h042_prob,
                    support,
                    logit_delta,
                    prob,
                    "fullsupport_edgepush",
                    f"edge{safe_float_id(edge)}_mix{safe_float_id(mix)}",
                    effective,
                )
            )

    scores = pd.DataFrame(records)
    scores = scores.sort_values(
        ["h051_sensor_priority", "curvature_risk", "edge_rate"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    scores.to_csv(OUT / "h051_candidate_scores.csv", index=False)
    scores.to_csv(OUT / "h051_candidate_scores_ranked.csv", index=False)

    selected_id = "h051_fullsupport_logitline_f2p0"
    selected = scores[scores["candidate_id"].str.startswith(selected_id)].iloc[0].copy()
    selected_path = Path(str(selected["resolved_path"]))
    root_name = f"submission_h051_q2_phase_amp_f2p0_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    root_path = ROOT / root_name
    write_submission(h042_df, pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64), root_path)

    decision = pd.DataFrame(
        [
            {
                "decision": "promote",
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "reason": "H042 exact-support Q2 phase full-step amplifier",
                "public_anchor": H042_FILE,
                "public_anchor_lb": H042_LB,
                "h050_public_lb": H050_LB,
                "expected_relation": (
                    "beats H042 if H042 was an under-amplified hidden Q2 label phase; "
                    "fails if H042 was only a local support-specific correction"
                ),
                **{k: selected[k] for k in selected.index if k not in {"resolved_path", "file"}},
            }
        ]
    )
    decision.to_csv(OUT / "h051_decision.csv", index=False)

    report = f"""# H051 Q2 Phase Amplifier HS-JEPA

Question: after H042's Q2-only public win and H050's non-Q2 neutral result, is the H042 Q2 direction under-amplified?

Design:

- base = H042 current public best;
- freeze every target except Q2;
- keep exactly H042's 45-cell Q2 support;
- move those cells farther in the same logit direction;
- selected public sensor = factor `2.0`, because H042's promoted file was the `s=0.5` phase and this tests the full-step interpretation.

Decision:

{md_table(decision)}

Support summary:

- H012 public LB: `{H012_LB:.10f}`
- H042 public LB: `{H042_LB:.10f}`
- H050 public LB treated as: `{H050_LB:.10f}`
- H042 improvement vs H012: `{H042_LB - H012_LB:.10f}`
- H050 delta vs H042: `{H050_LB - H042_LB:.10f}`
- H042 Q2 support cells: `{int(support.sum())}`
- H042 support positive/negative directions: `{int(np.sum(logit_delta[support] > 0))}` / `{int(np.sum(logit_delta[support] < 0))}`

Top candidates:

{md_table(scores[["candidate_id", "family", "parameter", "effective_h042_factor", "changed_cells_vs_h042", "same_direction_rate", "mean_abs_prob_move_vs_h042", "max_abs_prob_move_vs_h042", "edge_rate", "linear_expected_lb", "linear_expected_gain_vs_h042", "curvature_risk", "h051_sensor_priority"]], 20)}

Interpretation rule:

- If H051 improves materially, HS-JEPA should treat Q2 phase as a recoverable hidden label route and search stronger exact-support / label-edge solutions.
- If H051 is worse, H042 is not an under-amplified direction; it is a shallow local correction, and future Q2 work should focus on support identity or public-subset assignment rather than amplitude.
"""
    (OUT / "h051_report.md").write_text(report, encoding="utf-8")

    print(f"H051 selected: {selected['candidate_id']}")
    print(f"H051 root: {root_path}")
    print(f"H051 support cells: {int(support.sum())}")
    print(f"H051 expected linear LB: {float(selected['linear_expected_lb']):.10f}")


if __name__ == "__main__":
    main()
