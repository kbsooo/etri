#!/usr/bin/env python3
"""H054: objective S24 route-inversion HS-JEPA.

H050 tested a post-H042 non-Q2 subjective-Q route and public feedback tied H042.
That creates a new constraint:

    context = H042 Q2 public win + H050 subjective-Q public null
    target  = hidden target-route family that public actually hears after Q2
    action  = invert from subjective Q route to objective S2/S4 route

This is intentionally not a small blend.  It asks whether the Q2 hidden human
state is translated through objective sleep-stage targets rather than Q1/Q3.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h054_objective_s24_route_inversion_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H050_LB = 0.5679048248
H042_LB = 0.5679048248


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha1(np.round(frame[TARGETS].to_numpy(dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def load_submission(path: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    df = pd.read_csv(p)
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {p}")
    return df


def changed_by_target(a: pd.DataFrame, b: pd.DataFrame) -> dict[str, int]:
    diff = (a[TARGETS] - b[TARGETS]).abs() > 1.0e-12
    return {target: int(diff[target].sum()) for target in TARGETS}


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


def select_objective_s24_candidate(scores: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    df = scores.copy()
    eligible = df[
        df["target_group"].eq("S24")
        & (df["non_q2_changed_cells_vs_h042"] >= 140)
        & (df["q2_changed_cells_vs_h042"] == 0)
        & (df["route_delta_gain_vs_h042"] < -0.00015)
        & (df["full_known_action_support_better_than_h012"] >= 0.5)
        & (df["h025_score"] < -3.0)
    ].copy()
    if eligible.empty:
        raise RuntimeError("no eligible S24 route-inversion candidate")

    eligible["h054_route_inversion_score"] = (
        -1.10 * eligible["route_delta_gain_vs_h042"].rank(method="average", pct=True)
        -0.80 * eligible["full_known_action_margin_vs_h012_median"].rank(method="average", pct=True)
        -0.70 * eligible["h025_score"].rank(method="average", pct=True)
        -0.30 * eligible["h012posterior_delta_vs_h012"].rank(method="average", pct=True)
        +0.35 * eligible["full_known_action_support_better_than_h012"]
        -0.15 * eligible["pre_h012_h024_margin_vs_h012_median"].rank(method="average", pct=True)
    )
    eligible = eligible.sort_values(
        [
            "h054_route_inversion_score",
            "route_delta_gain_vs_h042",
            "h025_score",
            "non_q2_changed_cells_vs_h042",
        ],
        ascending=[False, True, True, False],
    ).reset_index(drop=True)
    return eligible.iloc[0], eligible


def main() -> None:
    h012 = load_submission(H012)
    h042 = load_submission(H042, h012[KEYS])
    h050 = load_submission(H050, h012[KEYS])

    scores_path = HITL / "h050_target_route_phase_jepa" / "h050_candidate_scores.csv"
    scores = pd.read_csv(scores_path)
    selected, eligible = select_objective_s24_candidate(scores)
    source_path = Path(str(selected["resolved_path"]))
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    candidate = load_submission(source_path, h012[KEYS])

    digest = short_hash(candidate)
    root_name = f"submission_h054_objective_s24_route_inversion_{digest}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(source_path, root_path)

    audit = []
    for label, base in [("h012", h012), ("h042", h042), ("h050", h050)]:
        per_target = changed_by_target(candidate, base)
        audit.append(
            {
                "compare_to": label,
                "changed_cells_total": int(sum(per_target.values())),
                **{f"{target}_changed": per_target[target] for target in TARGETS},
            }
        )
    audit_df = pd.DataFrame(audit)

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_objective_route_inversion",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(source_path),
                "root_uploadsafe_path": str(root_path),
                "reason": "H050 subjective-Q route tied H042; test objective S2/S4 translation instead",
                "public_anchor": H042,
                "public_anchor_lb": H042_LB,
                "h050_public_lb": H050_LB,
                "expected_relation": "beats H042 if hidden Q2 state routes into objective S2/S4 rather than Q1/Q3",
                "source": str(selected["source"]),
                "target_group": str(selected["target_group"]),
                "k": int(selected["k"]),
                "alpha": float(selected["alpha"]),
                "agree_only": bool(selected["agree_only"]),
                "changed_cells_vs_h012": int(selected["changed_cells_vs_h012"]),
                "changed_cells_vs_h042": int(selected["changed_cells_vs_h042"]),
                "non_q2_changed_cells_vs_h042": int(selected["non_q2_changed_cells_vs_h042"]),
                "route_delta_gain_vs_h042": float(selected["route_delta_gain_vs_h042"]),
                "route_equation_delta_vs_h012": float(selected["route_equation_delta_vs_h012"]),
                "full_known_action_margin_vs_h012_median": float(
                    selected["full_known_action_margin_vs_h012_median"]
                ),
                "full_known_action_support_better_than_h012": float(
                    selected["full_known_action_support_better_than_h012"]
                ),
                "pre_h012_h024_margin_vs_h012_median": float(selected["pre_h012_h024_margin_vs_h012_median"]),
                "h025_score": float(selected["h025_score"]),
                "h054_route_inversion_score": float(selected["h054_route_inversion_score"]),
            }
        ]
    )

    eligible.to_csv(OUT / "h054_objective_s24_eligible_candidates.csv", index=False)
    audit_df.to_csv(OUT / "h054_upload_audit.csv", index=False)
    decision.to_csv(OUT / "h054_decision.csv", index=False)

    report = f"""# H054 Objective S24 Route-Inversion HS-JEPA

Question: if H050's subjective Q1/Q3 route tied H042, is the post-Q2 hidden
state actually translated through objective S2/S4 targets?

Design:

- base = H042 current public anchor;
- freeze Q2 exactly as H042;
- reject H050's subjective-Q route as public-neutral;
- promote the strongest eligible S24 objective route from H050's candidate
  surface using route gain, full-known action support, and H025 action-health.

Decision:

{md_table(decision)}

Upload audit:

{md_table(audit_df)}

Top eligible S24 candidates:

{md_table(eligible[[
    "candidate_id",
    "source",
    "target_group",
    "k",
    "alpha",
    "agree_only",
    "changed_cells_vs_h042",
    "route_delta_gain_vs_h042",
    "full_known_action_margin_vs_h012_median",
    "full_known_action_support_better_than_h012",
    "pre_h012_h024_margin_vs_h012_median",
    "h025_score",
    "h054_route_inversion_score",
]], n=25)}

Interpretation rule:

- If H054 improves over H042/H050, HS-JEPA's target-route decoder should treat
  Q2 as the public-visible anchor and objective S2/S4 as the downstream route.
- If H054 fails, the S24 action-health signal is not enough for public and the
  next non-Q2 attempt should not recycle H050 target-route candidates.
"""
    (OUT / "h054_report.md").write_text(report)
    print(f"H054 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H054 root: {root_path}")
    print("Audit:")
    print(audit_df.to_string(index=False))


if __name__ == "__main__":
    main()
