#!/usr/bin/env python3
"""H057: Q2-row full-vector state HS-JEPA.

H050 tied H042 after adding subjective Q1/Q3 cells, but most of those rows were
outside H042's public-positive Q2 support. H056 tests the conservative
objective-only translation on H042 rows. H057 asks the bigger row-state question:

    If H042 discovered public-visible rows, should the whole non-Q2 target
    vector move on those rows?

The experiment starts from H042, freezes Q2, and moves Q1/Q3/S1-S4 only on the
45 H042 Q2 support rows toward the H055 post-feedback public-listener
posterior. A win would mean HS-JEPA should model rows as complete hidden human
states, not target-specific corrections.
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
OUT = HITL / "h057_q2row_fullvector_state_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H056 = "submission_h056_q2row_objective_state_a4620b89_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    alpha: float
    mode: str


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


def rank01(x: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 118) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def load_sub(name: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / name, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEYS).reset_index(drop=True)


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
    path = HITL / "h055_postfeedback_public_listener_jepa" / "h055_cell_posterior.csv"
    cells = pd.read_csv(path)
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


def target_mask(family: str, n_rows: int) -> np.ndarray:
    groups = {
        "q13": ["Q1", "Q3"],
        "s_all": ["S1", "S2", "S3", "S4"],
        "full_nonq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "q1_s_all": ["Q1", "S1", "S2", "S3", "S4"],
        "q3_s_all": ["Q3", "S1", "S2", "S3", "S4"],
    }
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for target in groups[family]:
        mask[:, TARGETS.index(target)] = True
    return mask


def build_candidates(
    sample: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h056_prob: np.ndarray,
    q: np.ndarray,
    aux: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, Path]]:
    q2_i = TARGETS.index("Q2")
    h042_q2_rows = np.abs(h042_prob[:, q2_i] - h012_prob[:, q2_i]) > TOL
    h050_extra = np.abs(h050_prob - h042_prob) > TOL
    h056_extra = np.abs(h056_prob - h042_prob) > TOL

    q2_strength = np.zeros(len(sample), dtype=np.float64)
    q2_strength[h042_q2_rows] = np.abs(logit(h042_prob[h042_q2_rows, q2_i]) - logit(h012_prob[h042_q2_rows, q2_i]))
    row_strength = rank01(q2_strength).copy()
    row_strength[~h042_q2_rows] = 0.0

    specs = [
        CandidateSpec(family, alpha, mode)
        for family in ["q13", "s_all", "full_nonq2", "q1_s_all", "q3_s_all"]
        for alpha in [0.55, 0.85, 1.15, 1.45]
        for mode in ["logit", "edge"]
    ]

    z_base = logit(h042_prob)
    z_q = logit(q)
    rows: list[dict[str, object]] = []
    paths: dict[str, Path] = {}
    seen: set[str] = set()

    for spec in specs:
        allowed = target_mask(spec.family, len(sample))
        allowed &= h042_q2_rows[:, None]
        allowed[:, q2_i] = False

        if spec.mode == "edge":
            edge = np.where(q >= 0.5, 0.88, 0.12)
            moved_all = sigmoid(z_base + np.clip(logit(edge) - z_base, -1.65, 1.65) * spec.alpha)
        else:
            moved_all = sigmoid(z_base + np.clip(z_q - z_base, -1.65, 1.65) * spec.alpha)

        prob = h042_prob.copy()
        prob[allowed] = moved_all[allowed]
        diff = np.abs(prob - h042_prob) > TOL
        if int(diff.sum()) == 0:
            continue

        gain = bce(h042_prob, q) - bce(prob, q)
        score_cells = gain[allowed]
        digest = short_hash(prob)
        candidate_id = safe_id(f"h057_{spec.family}_a{str(spec.alpha).replace('.', 'p')}_{spec.mode}_{digest}")
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)

        per_target = {f"{target}_changed_vs_h042": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
        selected_rows = diff.any(axis=1)
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": spec.family,
                "alpha": spec.alpha,
                "mode": spec.mode,
                "changed_cells_vs_h042": int(diff.sum()),
                "changed_rows_vs_h042": int(selected_rows.sum()),
                "q2_changed_vs_h042": int(diff[:, q2_i].sum()),
                "q13_changed_vs_h042": int(diff[:, TARGETS.index("Q1")].sum() + diff[:, TARGETS.index("Q3")].sum()),
                "s_changed_vs_h042": int(
                    diff[:, TARGETS.index("S1")].sum()
                    + diff[:, TARGETS.index("S2")].sum()
                    + diff[:, TARGETS.index("S3")].sum()
                    + diff[:, TARGETS.index("S4")].sum()
                ),
                "h050_overlap_cells": int((diff & h050_extra).sum()),
                "h056_overlap_cells": int((diff & h056_extra).sum()),
                "pred_delta_vs_h042": float(np.mean(bce(prob, q) - bce(h042_prob, q))),
                "pred_delta_vs_h050": float(np.mean(bce(prob, q) - bce(h050_prob, q))),
                "pred_delta_vs_h056": float(np.mean(bce(prob, q) - bce(h056_prob, q))),
                "mean_gain_selected": float(np.mean(score_cells)) if len(score_cells) else 0.0,
                "mean_aux_selected": float(np.mean(aux[allowed])) if np.any(allowed) else 0.0,
                "mean_row_strength_selected": float(np.mean(row_strength[selected_rows])) if selected_rows.any() else 0.0,
                **per_target,
            }
        )
        paths[candidate_id] = path

    candidates = pd.DataFrame(rows)
    candidates["h057_score"] = (
        -1.30 * candidates["pred_delta_vs_h042"].rank(method="average", pct=True)
        +0.55 * candidates["changed_cells_vs_h042"].rank(method="average", pct=True)
        +0.35 * candidates["mean_row_strength_selected"].rank(method="average", pct=True)
        +0.20 * candidates["h056_overlap_cells"].rank(method="average", pct=True)
        -0.45 * (candidates["q2_changed_vs_h042"] > 0).astype(float)
        -0.10 * (candidates["family"].eq("q13")).astype(float)
    )
    candidates = candidates.sort_values(
        ["h057_score", "pred_delta_vs_h042", "changed_cells_vs_h042"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    return candidates, paths


def main() -> None:
    h012 = load_sub(H012)
    h042 = load_sub(H042)
    h050 = load_sub(H050)
    h056 = load_sub(H056)
    sample = h012[KEYS].copy()
    for name, df in [("H042", h042), ("H050", h050), ("H056", h056)]:
        if not df[KEYS].equals(sample):
            raise ValueError(f"{name} key mismatch")

    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050[TARGETS].to_numpy(dtype=np.float64)
    h056_prob = h056[TARGETS].to_numpy(dtype=np.float64)
    q, aux = pivot_h055_posterior(sample)

    candidates, paths = build_candidates(sample, h012_prob, h042_prob, h050_prob, h056_prob, q, aux)
    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h057_q2row_fullvector_state_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)

    h042_q2_rows = np.abs(h042_prob[:, TARGETS.index("Q2")] - h012_prob[:, TARGETS.index("Q2")]) > TOL
    h050_q13_rows = (np.abs(h050_prob[:, TARGETS.index("Q1")] - h042_prob[:, TARGETS.index("Q1")]) > TOL) | (
        np.abs(h050_prob[:, TARGETS.index("Q3")] - h042_prob[:, TARGETS.index("Q3")]) > TOL
    )
    selected_diff = np.abs(selected_prob - h042_prob) > TOL
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_q2row_fullvector_state_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H042 support rows encode a complete hidden human-state vector, not only Q2 or S-stage route",
                "h042_q2_support_rows": int(h042_q2_rows.sum()),
                "h050_q13_route_rows": int(h050_q13_rows.sum()),
                "h042_h050_row_overlap": int((h042_q2_rows & h050_q13_rows).sum()),
                "selected_rows_in_h042_q2_support": int((selected_diff.any(axis=1) & h042_q2_rows).sum()),
                **selected.to_dict(),
            }
        ]
    )

    candidates.to_csv(OUT / "h057_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h057_decision.csv", index=False)

    report = f"""# H057 Q2-Row Full-Vector State HS-JEPA

Question: did H050 tie H042 because subjective Q targets are dead, or because
H050 put the target route on the wrong rows?

Design:

- base submission: H042;
- Q2 is frozen exactly;
- allowed rows are only the `45` rows where H042 changed Q2 versus H012;
- allowed promoted route moves the complete non-Q2 vector on those rows:
  Q1/Q3/S1/S2/S3/S4;
- target representation is the H055 post-feedback public-listener posterior.

Row overlap sensors:

- H042 Q2 support rows: `{int(h042_q2_rows.sum())}`;
- H050 Q1/Q3 route rows: `{int(h050_q13_rows.sum())}`;
- overlap: `{int((h042_q2_rows & h050_q13_rows).sum())}`.

Decision:

{md_table(decision)}

Top candidates:

{md_table(candidates.head(25))}

Interpretation rule:

- If H057 improves over H042/H056, HS-JEPA should represent H042 support rows
  as full hidden human-state vectors and route all target families together.
- If H056 improves but H057 fails, the row state is objective-S but not
  subjective-Q.
- If both H056 and H057 fail, H042 should be narrowed to Q2-local support.
"""
    (OUT / "h057_report.md").write_text(report)

    print(f"H057 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H057 root: {root_path}")
    print(
        decision[
            [
                "selected_candidate_id",
                "family",
                "changed_cells_vs_h042",
                "changed_rows_vs_h042",
                "q13_changed_vs_h042",
                "s_changed_vs_h042",
                "pred_delta_vs_h042",
                "h057_score",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
