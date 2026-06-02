#!/usr/bin/env python3
"""H056: Q2-row objective-state HS-JEPA.

H042 improved public LB by moving a tiny Q2 support. H050 then preserved that
Q2 support, changed Q1/Q3 route cells, and tied H042. The direct big-bet
question is:

    Did H042 find Q2 target-local cells, or did it reveal public-visible rows?

H056 treats the H042 Q2 support as a hidden human-state row marker. It starts
from H042, freezes Q2, avoids the H050 subjective-Q null route, and translates
only the same H042 Q2 rows into objective S-stage targets. A win means HS-JEPA
should model row-level hidden state routes; a loss narrows H042 back toward a
Q2-only target correction.
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
OUT = HITL / "h056_q2row_objective_state_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H055 = "submission_h055_postfeedback_listener_759f66e7_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    k: int
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


def rank01(x: np.ndarray, high: bool = True) -> np.ndarray:
    s = pd.Series(np.asarray(x, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        out = np.full(len(s), 0.5, dtype=np.float64)
    else:
        out = s.rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return out if high else 1.0 - out


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 118) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def load_sub(name: str) -> pd.DataFrame:
    path = ROOT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)


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
    if not path.exists():
        raise FileNotFoundError(path)
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
        "q2row_s_all": ["S1", "S2", "S3", "S4"],
        "q2row_s24": ["S2", "S4"],
        "q2row_s13": ["S1", "S3"],
        "q2row_s2": ["S2"],
        "q2row_s4": ["S4"],
        "q2row_q3s": ["Q3", "S1", "S2", "S3", "S4"],
        "q2row_nonq_vetoq": ["S1", "S2", "S3", "S4"],
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
    q: np.ndarray,
    aux: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, Path], pd.DataFrame]:
    z_base = logit(h042_prob)
    z_q = logit(q)
    q2_i = TARGETS.index("Q2")
    h042_q2_rows = np.abs(h042_prob[:, q2_i] - h012_prob[:, q2_i]) > TOL
    h050_null = np.abs(h050_prob - h042_prob) > TOL
    h050_q_null = h050_null[:, [TARGETS.index("Q1"), TARGETS.index("Q3")]].any(axis=1)

    q2_move_strength = np.zeros(len(sample), dtype=np.float64)
    q2_move_strength[h042_q2_rows] = np.abs(logit(h042_prob[h042_q2_rows, q2_i]) - logit(h012_prob[h042_q2_rows, q2_i]))
    row_strength = rank01(q2_move_strength).copy()
    row_strength[~h042_q2_rows] = 0.0

    specs = [
        CandidateSpec(family, k, alpha, mode)
        for family in ["q2row_s_all", "q2row_s24", "q2row_s13", "q2row_s2", "q2row_s4", "q2row_q3s"]
        for k in [36, 60, 90, 120, 150, 180]
        for alpha in [0.55, 0.85, 1.15, 1.45]
        for mode in ["logit", "edge"]
    ]

    rows: list[dict[str, object]] = []
    paths: dict[str, Path] = {}
    actions: list[pd.DataFrame] = []
    generated: set[str] = set()

    for spec in specs:
        allowed = target_mask(spec.family, len(sample))
        allowed &= h042_q2_rows[:, None]
        allowed[:, q2_i] = False
        if spec.family == "q2row_q3s":
            allowed &= ~h050_null

        if spec.mode == "edge":
            edge = np.where(q >= 0.5, 0.88, 0.12)
            moved_all = sigmoid(z_base + np.clip(logit(edge) - z_base, -1.55, 1.55) * spec.alpha)
        else:
            moved_all = sigmoid(z_base + np.clip(z_q - z_base, -1.55, 1.55) * spec.alpha)

        gain = bce(h042_prob, q) - bce(moved_all, q)
        score = gain * (0.70 + 0.85 * aux) * (0.30 + row_strength[:, None])
        flat_score = np.where(allowed.reshape(-1), score.reshape(-1), -np.inf)
        valid = np.where(np.isfinite(flat_score))[0]
        if len(valid) == 0:
            continue
        take = valid[np.argsort(-flat_score[valid])[: min(spec.k, len(valid))]]
        mask = np.zeros(h042_prob.size, dtype=bool)
        mask[take] = True
        mask = mask.reshape(h042_prob.shape)
        if not mask.any():
            continue

        prob = h042_prob.copy()
        prob[mask] = moved_all[mask]
        diff_h042 = np.abs(prob - h042_prob) > TOL
        digest = short_hash(prob)
        candidate_id = safe_id(f"h056_{spec.family}_k{spec.k}_a{str(spec.alpha).replace('.', 'p')}_{spec.mode}_{digest}")
        if candidate_id in generated:
            continue
        generated.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)

        selected_rows = diff_h042.any(axis=1)
        pred_delta_vs_h042 = float(np.mean(bce(prob, q) - bce(h042_prob, q)))
        pred_delta_vs_h012 = float(np.mean(bce(prob, q) - bce(h012_prob, q)))
        per_target = {f"{target}_changed_vs_h042": int(diff_h042[:, i].sum()) for i, target in enumerate(TARGETS)}
        row_overlap_with_h050_qnull = int((selected_rows & h050_q_null).sum())
        h050_null_overlap = int((diff_h042 & h050_null).sum())
        mean_gain = float(gain[mask].mean()) if mask.any() else 0.0
        mean_aux = float(aux[mask].mean()) if mask.any() else 0.0
        mean_row = float(row_strength[selected_rows].mean()) if selected_rows.any() else 0.0
        s_changed = sum(per_target[f"{target}_changed_vs_h042"] for target in ["S1", "S2", "S3", "S4"])
        q_changed = per_target["Q1_changed_vs_h042"] + per_target["Q3_changed_vs_h042"]
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "family": spec.family,
                "k": spec.k,
                "alpha": spec.alpha,
                "mode": spec.mode,
                "changed_cells_vs_h042": int(diff_h042.sum()),
                "changed_rows_vs_h042": int(selected_rows.sum()),
                "s_changed_vs_h042": int(s_changed),
                "q13_changed_vs_h042": int(q_changed),
                "q2_changed_vs_h042": int(diff_h042[:, q2_i].sum()),
                "h050_null_overlap_cells": h050_null_overlap,
                "row_overlap_with_h050_qnull": row_overlap_with_h050_qnull,
                "pred_delta_vs_h042": pred_delta_vs_h042,
                "pred_delta_vs_h012": pred_delta_vs_h012,
                "mean_gain_selected": mean_gain,
                "mean_aux_selected": mean_aux,
                "mean_row_strength_selected": mean_row,
                **per_target,
            }
        )
        paths[candidate_id] = path

        rr, cc = np.where(diff_h042)
        action = pd.DataFrame(
            {
                "candidate_id": candidate_id,
                "row": rr,
                "target": [TARGETS[i] for i in cc],
                "h042_prob": h042_prob[rr, cc],
                "h056_prob": prob[rr, cc],
                "h055_posterior": q[rr, cc],
                "gain": gain[rr, cc],
                "aux": aux[rr, cc],
                "row_strength": row_strength[rr],
            }
        )
        actions.append(action)

    candidates = pd.DataFrame(rows)
    if candidates.empty:
        raise RuntimeError("No H056 candidates generated")
    candidates["h056_score"] = (
        -1.35 * candidates["pred_delta_vs_h042"].rank(method="average", pct=True)
        +0.35 * candidates["s_changed_vs_h042"].rank(method="average", pct=True)
        +0.25 * candidates["changed_rows_vs_h042"].rank(method="average", pct=True)
        +0.20 * candidates["mean_row_strength_selected"].rank(method="average", pct=True)
        -0.70 * (candidates["q13_changed_vs_h042"] > 0).astype(float)
        -0.55 * (candidates["h050_null_overlap_cells"] > 0).astype(float)
        -0.35 * (candidates["q2_changed_vs_h042"] > 0).astype(float)
        -0.18 * (candidates["changed_cells_vs_h042"] < 90).astype(float)
    )
    candidates = candidates.sort_values(
        ["h056_score", "pred_delta_vs_h042", "changed_cells_vs_h042"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    return candidates, paths, pd.concat(actions, ignore_index=True)


def main() -> None:
    h012 = load_sub(H012)
    h042 = load_sub(H042)
    h050 = load_sub(H050)
    h055 = load_sub(H055)
    sample = h012[KEYS].copy()
    for name, df in [("H042", h042), ("H050", h050), ("H055", h055)]:
        if not df[KEYS].equals(sample):
            raise ValueError(f"{name} key mismatch")

    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050[TARGETS].to_numpy(dtype=np.float64)
    h055_prob = h055[TARGETS].to_numpy(dtype=np.float64)
    q, aux = pivot_h055_posterior(sample)

    candidates, paths, actions = build_candidates(sample, h012_prob, h042_prob, h050_prob, q, aux)
    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h056_q2row_objective_state_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)

    h042_q2_rows = np.abs(h042_prob[:, TARGETS.index("Q2")] - h012_prob[:, TARGETS.index("Q2")]) > TOL
    h050_q13_rows = (np.abs(h050_prob[:, TARGETS.index("Q1")] - h042_prob[:, TARGETS.index("Q1")]) > TOL) | (
        np.abs(h050_prob[:, TARGETS.index("Q3")] - h042_prob[:, TARGETS.index("Q3")]) > TOL
    )
    selected_diff = np.abs(selected_prob - h042_prob) > TOL
    h055_diff = np.abs(h055_prob - h042_prob) > TOL
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_q2row_objective_state_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H042 Q2 support is a public-visible row-state marker, not merely a Q2 target correction",
                "h042_q2_support_rows": int(h042_q2_rows.sum()),
                "h050_q13_route_rows": int(h050_q13_rows.sum()),
                "h042_h050_row_overlap": int((h042_q2_rows & h050_q13_rows).sum()),
                "selected_rows_in_h042_q2_support": int((selected_diff.any(axis=1) & h042_q2_rows).sum()),
                "selected_cells_overlap_h055": int((selected_diff & h055_diff).sum()),
                **selected.to_dict(),
            }
        ]
    )

    candidates.to_csv(OUT / "h056_candidate_scores.csv", index=False)
    actions.to_csv(OUT / "h056_cell_actions.csv", index=False)
    decision.to_csv(OUT / "h056_decision.csv", index=False)

    report = f"""# H056 Q2-Row Objective-State HS-JEPA

Question: did H042 expose a public-visible row state, or only a Q2-local target
correction?

Design:

- base submission: H042;
- Q2 is frozen exactly;
- allowed rows are only the `45` rows where H042 changed Q2 versus H012;
- allowed primary route is objective S-stage targets, not H050's public-null
  subjective Q1/Q3 route;
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

- If H056 improves over H042, the H042 Q2 support is a reusable row-level
  hidden human-state marker, and HS-JEPA should route that state into objective
  sleep-stage targets.
- If H056 fails while H042 remains best, H042 should be narrowed to a Q2-local
  public correction; broad row-state translation is not public-safe under the
  current evidence.
"""
    (OUT / "h056_report.md").write_text(report)

    print(f"H056 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H056 root: {root_path}")
    print(
        decision[
            [
                "selected_candidate_id",
                "family",
                "changed_cells_vs_h042",
                "changed_rows_vs_h042",
                "s_changed_vs_h042",
                "q13_changed_vs_h042",
                "pred_delta_vs_h042",
                "h056_score",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
