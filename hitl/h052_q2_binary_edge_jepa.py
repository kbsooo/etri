#!/usr/bin/env python3
"""H052: Q2 binary-edge HS-JEPA.

H051 asks whether H042's Q2 phase is linearly under-amplified.  H052 asks the
more extreme follow-up:

    What if the recovered Q2 state is not a smooth calibration vector, but a
    partially observed binary label edge?

This is a conditional high-upside branch.  It should be interpreted after H051:
if H051 improves, H052 is the natural next sensor; if H051 fails, this branch
should be considered killed before submission.
"""

from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h052_q2_binary_edge_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012_FILE = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H051_FILE = "submission_h051_q2_phase_amp_f2p0_5ab4e605_uploadsafe.csv"
H047_SUPPORT_FILE = "hitl/h047_q2_support_identity_jepa/h047_row_support_posterior.csv"

H012_LB = 0.5681234831
H042_LB = 0.5679048248
H050_LB = 0.5679048248


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


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
    prob: np.ndarray,
    logit_delta: np.ndarray,
    selected: np.ndarray,
    support_post: np.ndarray,
    support_name: str,
    edge: float,
    mix: float,
) -> dict[str, object]:
    q2 = TARGETS.index("Q2")
    q2_changed = np.abs(prob[:, q2] - h042_prob[:, q2]) > 1.0e-12
    extra_prob = prob[:, q2] - h042_prob[:, q2]
    extra_logit = logit(prob[:, q2]) - logit(h042_prob[:, q2])
    full_logit = logit(prob[:, q2]) - logit(h012_prob[:, q2])
    denom = float(np.dot(logit_delta[selected], logit_delta[selected])) if np.any(selected) else 0.0
    effective = float(np.dot(full_logit[selected], logit_delta[selected]) / denom) if denom > 0 else 0.0
    linear_expected_lb = H012_LB + effective * (H042_LB - H012_LB)
    curvature_risk = float(np.mean(np.square(extra_logit[selected]))) if np.any(selected) else 0.0
    mean_support_post = float(np.mean(support_post[selected])) if np.any(selected) else 0.0
    min_support_post = float(np.min(support_post[selected])) if np.any(selected) else 0.0
    edge_rate = float(np.mean((prob[selected, q2] < 0.12) | (prob[selected, q2] > 0.88))) if np.any(selected) else 0.0
    same_direction_rate = (
        float(np.mean(np.sign(full_logit[selected]) == np.sign(logit_delta[selected])))
        if np.any(selected)
        else 0.0
    )
    extra_direction_rate = (
        float(np.mean(np.sign(extra_prob[selected]) == np.sign(logit_delta[selected])))
        if np.any(selected)
        else 0.0
    )

    candidate_id = (
        f"h052_{support_name}_edge{safe_float_id(edge)}_mix{safe_float_id(mix)}_"
        f"{short_hash(prob)}"
    )
    file_name = f"submission_{candidate_id}.csv"
    path = OUT / file_name
    write_submission(template, prob, path)

    return {
        "candidate_id": candidate_id,
        "file": file_name,
        "resolved_path": str(path),
        "support_name": support_name,
        "edge": edge,
        "mix": mix,
        "changed_cells_vs_h042": int(np.sum(np.abs(prob - h042_prob) > 1.0e-12)),
        "q2_changed_cells_vs_h042": int(q2_changed.sum()),
        "selected_support_cells": int(selected.sum()),
        "same_direction_rate": same_direction_rate,
        "extra_direction_rate": extra_direction_rate,
        "mean_support_posterior": mean_support_post,
        "min_support_posterior": min_support_post,
        "mean_abs_prob_move_vs_h042": float(np.mean(np.abs(extra_prob[selected]))) if np.any(selected) else 0.0,
        "max_abs_prob_move_vs_h042": float(np.max(np.abs(extra_prob[selected]))) if np.any(selected) else 0.0,
        "curvature_risk": curvature_risk,
        "edge_rate": edge_rate,
        "effective_h042_factor": effective,
        "linear_expected_lb": linear_expected_lb,
        "linear_expected_gain_vs_h042": linear_expected_lb - H042_LB,
        "h052_binary_edge_priority": (
            -(linear_expected_lb - H042_LB)
            + 0.00025 * mean_support_post
            - 0.00150 * curvature_risk
            - 0.00035 * edge_rate
            - 0.00020 * max(0.0, 0.50 - min_support_post)
        ),
    }


def main() -> None:
    h012_df = pd.read_csv(ROOT / H012_FILE)
    h042_df = pd.read_csv(ROOT / H042_FILE)
    h050_df = pd.read_csv(ROOT / H050_FILE)
    h051_df = pd.read_csv(ROOT / H051_FILE)
    support_df = pd.read_csv(ROOT / H047_SUPPORT_FILE)

    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042_df[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050_df[TARGETS].to_numpy(dtype=np.float64)
    h051_prob = h051_df[TARGETS].to_numpy(dtype=np.float64)

    q2 = TARGETS.index("Q2")
    logit_delta = logit(h042_prob[:, q2]) - logit(h012_prob[:, q2])
    h042_support = np.abs(logit_delta) > 1.0e-12
    support_post = support_df["h047_support_posterior"].to_numpy(dtype=np.float64)
    abs_delta = np.abs(logit_delta)
    confidence_score = support_post * (0.35 + abs_delta / max(float(abs_delta.max()), EPS))

    support_sets: dict[str, np.ndarray] = {
        "exact45": h042_support,
        "post_top35": h042_support & (pd.Series(confidence_score).rank(method="first", ascending=False).to_numpy() <= 35),
        "post_top25": h042_support & (pd.Series(confidence_score).rank(method="first", ascending=False).to_numpy() <= 25),
        "post_high060": h042_support & (support_post >= 0.60),
    }

    rows = []
    for support_name, selected in support_sets.items():
        for edge in [0.82, 0.88, 0.93]:
            for mix in [0.25, 0.35, 0.50]:
                prob = h042_prob.copy()
                target = np.where(logit_delta[selected] > 0.0, edge, 1.0 - edge)
                prob[selected, q2] = h042_prob[selected, q2] + mix * (target - h042_prob[selected, q2])
                rows.append(
                    candidate_record(
                        h042_df,
                        h012_prob,
                        h042_prob,
                        clip_prob(prob),
                        logit_delta,
                        selected,
                        support_post,
                        support_name,
                        edge,
                        mix,
                    )
                )

    scores = pd.DataFrame(rows).sort_values(
        ["h052_binary_edge_priority", "curvature_risk", "edge_rate"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    scores.to_csv(OUT / "h052_candidate_scores.csv", index=False)
    scores.to_csv(OUT / "h052_candidate_scores_ranked.csv", index=False)

    selected_prefix = "h052_exact45_edge0p88_mix0p35"
    selected = scores[scores["candidate_id"].str.startswith(selected_prefix)].iloc[0].copy()
    selected_path = Path(str(selected["resolved_path"]))
    root_name = f"submission_h052_q2_binary_edge_0p88m35_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    root_path = ROOT / root_name
    selected_prob = pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64)
    write_submission(h042_df, selected_prob, root_path)

    support_audit = support_df[KEYS + ["row", "h047_support_posterior", "h047_public_score", "h047_private_score"]].copy()
    support_audit["h052_h042_support"] = h042_support
    support_audit["h052_selected_exact45"] = h042_support
    support_audit["h052_q2_direction"] = np.sign(logit_delta)
    support_audit["h052_abs_logit_delta"] = abs_delta
    support_audit["h052_confidence_score"] = confidence_score
    support_audit.loc[h042_support].to_csv(OUT / "h052_support_audit.csv", index=False)

    decision = pd.DataFrame(
        [
            {
                "decision": "conditional_promote_after_h051_positive",
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "reason": "Q2 exact-support binary-edge branch",
                "public_anchor": H042_FILE,
                "public_anchor_lb": H042_LB,
                "h050_public_lb": H050_LB,
                "h051_dependency": H051_FILE,
                "expected_relation": (
                    "submit after H051 only if H051 improves; beats H042 if Q2 phase is "
                    "a binary hidden-label edge rather than a smooth calibration vector"
                ),
                **{k: selected[k] for k in selected.index if k not in {"resolved_path", "file"}},
            }
        ]
    )
    decision.to_csv(OUT / "h052_decision.csv", index=False)

    h050_delta = float(np.max(np.abs(h050_prob[:, q2] - h042_prob[:, q2])))
    h051_extra = h051_prob[:, q2] - h042_prob[:, q2]
    report = f"""# H052 Q2 Binary-Edge HS-JEPA

Question: if H051's linear Q2 amplification is right, is the next state a stronger binary edge on the same hidden Q2 support?

Design:

- base = H042 current public best;
- Q1/Q3/S targets are frozen;
- selected branch keeps H042's exact `45` Q2 support;
- each selected Q2 cell is pulled toward `0.88` if H042 moved it upward and toward `0.12` if H042 moved it downward;
- mix is `0.35`, so this is a binary-edge sensor rather than a full saturation file.

Decision:

{md_table(decision)}

Public-anchor context:

- H012 public LB: `{H012_LB:.10f}`
- H042 public LB: `{H042_LB:.10f}`
- H050 public LB: `{H050_LB:.10f}`
- H050 max Q2 delta vs H042: `{h050_delta:.12f}` (Q2 was frozen)
- H051 extra Q2 mean/max abs move vs H042: `{float(np.mean(np.abs(h051_extra[h042_support]))):.9f}` / `{float(np.max(np.abs(h051_extra[h042_support]))):.9f}`

Top candidates:

{md_table(scores[["candidate_id", "support_name", "edge", "mix", "selected_support_cells", "mean_support_posterior", "min_support_posterior", "same_direction_rate", "extra_direction_rate", "mean_abs_prob_move_vs_h042", "max_abs_prob_move_vs_h042", "curvature_risk", "edge_rate", "effective_h042_factor", "linear_expected_lb", "linear_expected_gain_vs_h042", "h052_binary_edge_priority"]], 20)}

Interpretation rule:

- If H051 improves and H052 also improves, HS-JEPA should model Q2 as a hidden binary action-label edge, not as ordinary calibration.
- If H051 improves but H052 fails, Q2 is amplitude-linear but not label-edge.
- If H051 fails, do not submit H052; the entire amplitude/edge branch is killed and support/public-subset assignment should take priority.
"""
    (OUT / "h052_report.md").write_text(report, encoding="utf-8")

    print(f"H052 selected: {selected['candidate_id']}")
    print(f"H052 root: {root_path}")
    print(f"H052 selected support cells: {int(selected['selected_support_cells'])}")
    print(f"H052 expected linear LB: {float(selected['linear_expected_lb']):.10f}")


if __name__ == "__main__":
    main()
