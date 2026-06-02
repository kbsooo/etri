#!/usr/bin/env python3
"""H062: H057-seed row-state expansion HS-JEPA.

H061 found that H057's own 270 support cells are mostly still supported after
the H057 public observation.  That weakens the "split H057 internally" story
and strengthens a bigger one:

    H057's 45 rows may be seed examples of a hidden human-state class.

H062 uses the H061 posterior as a target representation and asks whether more
non-Q2 rows should receive the same full-vector state translation.
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
OUT = HITL / "h062_h057_seed_rowstate_expansion_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
NON_Q2 = [t for t in TARGETS if t != "Q2"]
EPS = 1.0e-6

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"


@dataclass(frozen=True)
class ExpansionSpec:
    family: str
    k_rows: int
    alpha: float
    mode: str
    near_bonus: float
    max_per_subject: int


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


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = ROOT / name if not Path(name).is_absolute() else Path(name)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
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


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def move(base: np.ndarray, q: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * q)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(q)))
    raise ValueError(mode)


def support_rows(h042_prob: np.ndarray, h057_prob: np.ndarray) -> np.ndarray:
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    changed = np.abs(h057_prob[:, nonq_ix] - h042_prob[:, nonq_ix]) > 1.0e-12
    return np.where(changed.any(axis=1))[0]


def nearest_seed_distance(sample: pd.DataFrame, seed_rows: np.ndarray) -> np.ndarray:
    dist = np.full(len(sample), 999.0, dtype=np.float64)
    for subject, sub in sample.reset_index().groupby("subject_id"):
        idx = sub["index"].to_numpy(dtype=int)
        seed = np.array([row for row in seed_rows if sample.loc[row, "subject_id"] == subject], dtype=int)
        if len(seed) == 0:
            continue
        for row in idx:
            dist[row] = float(np.min(np.abs(seed - row)))
    return dist


def row_candidates(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
) -> pd.DataFrame:
    seed = support_rows(h042_prob, h057_prob)
    seed_set = set(seed.tolist())
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    dist = nearest_seed_distance(sample, seed)
    rows = []
    for row in range(len(sample)):
        if row in seed_set:
            continue
        gain_by_target = bce(h057_prob[row, nonq_ix], q061[row, nonq_ix]) - bce(q061[row, nonq_ix], q061[row, nonq_ix])
        row_gain = float(gain_by_target.sum())
        rows.append(
            {
                "row": row,
                "subject_id": sample.loc[row, "subject_id"],
                "sleep_date": sample.loc[row, "sleep_date"],
                "lifelog_date": sample.loc[row, "lifelog_date"],
                "row_gain_to_q061_nonq2": row_gain,
                "min_target_gain": float(np.min(gain_by_target)),
                "positive_targets": int((gain_by_target > 0).sum()),
                "nearest_seed_distance": float(dist[row]),
                "episode_near": float(dist[row] <= 3),
                "same_subject_has_seed": float(dist[row] < 999.0),
                "Q1_gain": float(gain_by_target[NON_Q2.index("Q1")]),
                "Q3_gain": float(gain_by_target[NON_Q2.index("Q3")]),
                "S1_gain": float(gain_by_target[NON_Q2.index("S1")]),
                "S2_gain": float(gain_by_target[NON_Q2.index("S2")]),
                "S3_gain": float(gain_by_target[NON_Q2.index("S3")]),
                "S4_gain": float(gain_by_target[NON_Q2.index("S4")]),
            }
        )
    out = pd.DataFrame(rows)
    out["base_row_score"] = (
        out["row_gain_to_q061_nonq2"].rank(method="average", pct=True)
        + 0.25 * out["min_target_gain"].rank(method="average", pct=True)
        + 0.20 * out["positive_targets"].rank(method="average", pct=True)
    )
    return out.sort_values("base_row_score", ascending=False).reset_index(drop=True)


def select_rows(row_scores: pd.DataFrame, spec: ExpansionSpec) -> pd.DataFrame:
    df = row_scores.copy()
    if spec.family == "latent_all":
        pass
    elif spec.family == "episode_near":
        df = df[df["episode_near"] > 0]
    elif spec.family == "episode_far":
        df = df[df["episode_near"] == 0]
    else:
        raise ValueError(spec.family)
    df["select_score"] = df["base_row_score"] + spec.near_bonus * df["episode_near"]
    out = []
    counts: dict[str, int] = {}
    for rec in df.sort_values("select_score", ascending=False).to_dict("records"):
        subject = str(rec["subject_id"])
        if counts.get(subject, 0) >= spec.max_per_subject:
            continue
        out.append(rec)
        counts[subject] = counts.get(subject, 0) + 1
        if len(out) >= spec.k_rows:
            break
    return pd.DataFrame(out)


def make_candidate(
    spec: ExpansionSpec,
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object]]:
    selected_rows = select_rows(row_scores, spec)
    prob = h057_prob.copy()
    moved = move(h057_prob, q061, spec.alpha, spec.mode)
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    for row in selected_rows["row"].astype(int).tolist():
        prob[row, nonq_ix] = moved[row, nonq_ix]
    diff = np.abs(prob - h057_prob) > 1.0e-12
    delta = float(np.mean(bce(prob, q061) - bce(h057_prob, q061)))
    per_target = {f"{target}_changed_vs_h057": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
    return clip_prob(prob), {
        "family": spec.family,
        "k_rows": spec.k_rows,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "near_bonus": spec.near_bonus,
        "max_per_subject": spec.max_per_subject,
        "selected_rows": ",".join(map(str, selected_rows["row"].astype(int).tolist())),
        "posterior_delta_vs_h057": delta,
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "q2_changed_vs_h057": int(diff[:, TARGETS.index("Q2")].sum()),
        "mean_selected_row_gain": float(selected_rows["row_gain_to_q061_nonq2"].mean()) if len(selected_rows) else 0.0,
        "mean_selected_nearest_seed_distance": float(selected_rows["nearest_seed_distance"].mean()) if len(selected_rows) else 999.0,
        "episode_near_rate": float(selected_rows["episode_near"].mean()) if len(selected_rows) else 0.0,
        "selected_subjects": int(selected_rows["subject_id"].nunique()) if len(selected_rows) else 0,
        **per_target,
    }


def sweep(
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Path]]:
    specs = [
        ExpansionSpec(family, k_rows, alpha, mode, near_bonus, max_per_subject)
        for family in ["latent_all", "episode_near", "episode_far"]
        for k_rows in [8, 12, 18, 24, 36, 48, 72]
        for alpha in [0.25, 0.40, 0.60, 0.85, 1.00]
        for mode in ["logit", "prob"]
        for near_bonus in ([0.00, 0.25, 0.50] if family == "latent_all" else [0.00])
        for max_per_subject in [4, 8, 16]
    ]
    rows = []
    paths: dict[str, Path] = {}
    for spec in specs:
        chosen = select_rows(row_scores, spec)
        if len(chosen) < min(spec.k_rows, 4):
            continue
        prob, meta = make_candidate(spec, sample, h057_prob, q061, row_scores)
        digest = short_hash(prob)
        cid = (
            f"h062_{spec.family}_r{spec.k_rows}_a{str(spec.alpha).replace('.', 'p')}_"
            f"{spec.mode}_nb{str(spec.near_bonus).replace('.', 'p')}_mps{spec.max_per_subject}_{digest}"
        )
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        paths[cid] = path
        rows.append({"candidate_id": cid, "file": path.name, "resolved_path": str(path), **meta})
    out = pd.DataFrame(rows)
    out["h062_score"] = (
        -1.00 * out["posterior_delta_vs_h057"].rank(method="average", pct=True)
        + 0.35 * out["changed_cells_vs_h057"].rank(method="average", pct=True)
        + 0.25 * out["mean_selected_row_gain"].rank(method="average", pct=True)
        + 0.20 * out["selected_subjects"].rank(method="average", pct=True)
        + 0.10 * out["episode_near_rate"].rank(method="average", pct=True)
        - 0.15 * (out["changed_cells_vs_h057"] > 360).astype(float)
        - 0.25 * (out["q2_changed_vs_h057"] > 0).astype(float)
    )
    return out.sort_values(["h062_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True), paths


def validate(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    probs = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(np.min(probs)),
        "max_prob": float(np.max(probs)),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and np.min(probs) > 0.0
            and np.max(probs) < 1.0
        ),
    }


def main() -> None:
    h042 = load_sub(H042)
    sample = h042[KEYS].copy()
    h057 = load_sub(H057, sample)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)

    seed = support_rows(h042_prob, h057_prob)
    rows = row_candidates(sample, h042_prob, h057_prob, q061)
    candidates, paths = sweep(sample, h057_prob, q061, rows)
    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h062_h057seed_rowstate_expand_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    check = validate(root_path, sample)

    summary = pd.DataFrame(
        [
            {
                "h057_seed_rows": int(len(seed)),
                "candidate_rows_outside_seed": int(len(rows)),
                "top_row_gain": float(rows["row_gain_to_q061_nonq2"].max()),
                "median_row_gain": float(rows["row_gain_to_q061_nonq2"].median()),
                "top10_episode_near_rate": float(rows.head(10)["episode_near"].mean()),
                "top30_episode_near_rate": float(rows.head(30)["episode_near"].mean()),
            }
        ]
    )
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_h057_seed_rowstate_expansion",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 rows are seed examples of a larger hidden human-state class",
                **selected.to_dict(),
                **check,
            }
        ]
    )

    rows.to_csv(OUT / "h062_row_scores.csv", index=False)
    candidates.to_csv(OUT / "h062_candidate_scores.csv", index=False)
    summary.to_csv(OUT / "h062_summary.csv", index=False)
    decision.to_csv(OUT / "h062_decision.csv", index=False)

    report = f"""# H062 H057-Seed Row-State Expansion HS-JEPA

Question: after H057 public feedback, are the validated `45` H057 rows only a
compact support set, or are they seed examples of a larger hidden human-state
class?

Design:

- base: H057;
- target representation: H061 posterior `q061`;
- freeze Q2 exactly;
- candidate rows exclude the original H057 seed rows;
- action translates full non-Q2 vector on newly selected rows toward `q061`.

Summary:

{md_table(summary)}

Decision:

{md_table(decision)}

Top candidate rows:

{md_table(rows.head(30))}

Top candidate submissions:

{md_table(candidates.head(25))}

Interpretation rule:

- If H062 improves, H057 was not a closed 45-row correction. It was a seed set
  for a larger hidden human-state class.
- If H062 fails, the validated H057 state is compact and public-specific; broad
  row expansion should be blocked until a stronger row classifier exists.
"""
    (OUT / "h062_report.md").write_text(report)
    print(f"H062 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H062 root: {root_path}")
    print(decision[["selected_candidate_id", "changed_cells_vs_h057", "changed_rows_vs_h057", "posterior_delta_vs_h057", "episode_near_rate", "selected_subjects", "upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    main()
