#!/usr/bin/env python3
"""H059: episode-spread full-vector HS-JEPA.

H057 gave the first public-positive full-vector row-state result: H042's 45 Q2
support rows can carry Q1/Q3/S1-S4 when Q2 is frozen.

H059 asks the next large question:

    Are those rows isolated events, or are they visible markers of a same-subject
    lifestyle episode that spills into nearby days?

The experiment starts from H057, leaves all H057 anchor rows unchanged, freezes
Q2 everywhere, and propagates the full non-Q2 vector to same-subject neighbor
rows around the H042 Q2 support.
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
OUT = HITL / "h059_episode_spread_fullvector_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    row_mask: str
    family: str
    alpha: float


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


def safe_id(text: str, limit: int = 118) -> str:
    keep = [ch if ch.isalnum() or ch in "._-" else "_" for ch in str(text)]
    return "".join(keep).strip("_")[:limit].strip("_")


def load_sub(name: str, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    df = pd.read_csv(ROOT / name, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 25) -> str:
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


def target_mask(family: str, n_rows: int) -> np.ndarray:
    groups = {
        "full_nonq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "q3s": ["Q3", "S1", "S2", "S3", "S4"],
        "q1s": ["Q1", "S1", "S2", "S3", "S4"],
        "s_all": ["S1", "S2", "S3", "S4"],
        "q13": ["Q1", "Q3"],
    }
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for target in groups[family]:
        mask[:, TARGETS.index(target)] = True
    return mask


def episode_distances(sample: pd.DataFrame, anchor_rows: np.ndarray) -> pd.DataFrame:
    n = len(sample)
    pos_dist = np.full(n, 999, dtype=int)
    signed_pos = np.full(n, 999, dtype=int)
    date_dist = np.full(n, 999, dtype=int)
    signed_date = np.full(n, 999, dtype=int)
    nearest_anchor = np.full(n, -1, dtype=int)

    for _, group in sample.groupby("subject_id", sort=False):
        idx = group.index.to_numpy()
        local_anchor = np.array([i for i in idx if anchor_rows[i]], dtype=int)
        if len(local_anchor) == 0:
            continue
        local_pos = np.arange(len(idx))
        pos_by_row = {row: pos for row, pos in zip(idx, local_pos)}
        anchor_pos = np.array([pos_by_row[row] for row in local_anchor], dtype=int)
        anchor_dates = sample.loc[local_anchor, "sleep_date"].to_numpy(dtype="datetime64[D]")
        for row in idx:
            row_pos = pos_by_row[row]
            dpos = row_pos - anchor_pos
            j = int(np.argmin(np.abs(dpos)))
            pos_dist[row] = abs(int(dpos[j]))
            signed_pos[row] = int(dpos[j])
            row_date = sample.loc[row, "sleep_date"].to_datetime64().astype("datetime64[D]")
            ddate = (row_date - anchor_dates).astype("timedelta64[D]").astype(int)
            k = int(np.argmin(np.abs(ddate)))
            date_dist[row] = abs(int(ddate[k]))
            signed_date[row] = int(ddate[k])
            nearest_anchor[row] = int(local_anchor[j])

    out = sample.copy()
    out["anchor_row"] = anchor_rows
    out["nearest_anchor_row"] = nearest_anchor
    out["pos_dist_to_anchor"] = pos_dist
    out["signed_pos_to_anchor"] = signed_pos
    out["date_dist_to_anchor"] = date_dist
    out["signed_date_to_anchor"] = signed_date
    return out


def row_mask(name: str, dist: pd.DataFrame) -> np.ndarray:
    base = ~dist["anchor_row"].to_numpy(dtype=bool)
    pos = dist["pos_dist_to_anchor"].to_numpy(dtype=int)
    spos = dist["signed_pos_to_anchor"].to_numpy(dtype=int)
    date = dist["date_dist_to_anchor"].to_numpy(dtype=int)
    masks = {
        "pos_r1": base & (pos <= 1),
        "pos_r2": base & (pos <= 2),
        "pos_r3": base & (pos <= 3),
        "date_d1": base & (date <= 1),
        "date_d2": base & (date <= 2),
        "pre_pos1": base & (spos < 0) & (pos <= 1),
        "post_pos1": base & (spos > 0) & (pos <= 1),
        "pre_pos2": base & (spos < 0) & (pos <= 2),
        "post_pos2": base & (spos > 0) & (pos <= 2),
    }
    return masks[name]


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


def build_candidates(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q: np.ndarray,
    aux: np.ndarray,
    dist: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Path], dict[str, np.ndarray]]:
    specs = [
        CandidateSpec(mask, family, alpha)
        for mask in ["pos_r1", "pos_r2", "pos_r3", "date_d1", "date_d2", "pre_pos1", "post_pos1", "pre_pos2", "post_pos2"]
        for family in ["full_nonq2", "q3s", "q1s", "s_all", "q13"]
        for alpha in [0.45, 0.60, 0.75, 0.90, 1.10]
    ]

    base_loss = bce(h057_prob, q).mean()
    z_base = logit(h057_prob)
    z_q = logit(q)
    pos_dist = dist["pos_dist_to_anchor"].to_numpy(dtype=int)
    rows: list[dict[str, object]] = []
    paths: dict[str, Path] = {}
    masks: dict[str, np.ndarray] = {}
    seen: set[str] = set()

    for spec in specs:
        rmask = row_mask(spec.row_mask, dist)
        tmask = target_mask(spec.family, len(sample))
        allowed = rmask[:, None] & tmask
        allowed[:, TARGETS.index("Q2")] = False
        if not np.any(allowed):
            continue

        effective_alpha = np.full(len(sample), spec.alpha, dtype=np.float64)
        effective_alpha[pos_dist == 2] *= 0.55
        effective_alpha[pos_dist == 3] *= 0.35

        moved = sigmoid(z_base + np.clip(z_q - z_base, -1.65, 1.65) * effective_alpha[:, None])
        prob = h057_prob.copy()
        prob[allowed] = moved[allowed]
        diff057 = np.abs(prob - h057_prob) > TOL
        if int(diff057.sum()) == 0:
            continue
        diff042 = np.abs(prob - h042_prob) > TOL
        digest = short_hash(prob)
        candidate_id = safe_id(f"h059_episode_{spec.row_mask}_{spec.family}_a{str(spec.alpha).replace('.', 'p')}_{digest}")
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)

        selected_rows = diff057.any(axis=1)
        per_target = {f"{target}_changed_vs_h057": int(diff057[:, i].sum()) for i, target in enumerate(TARGETS)}
        per_distance = {
            "dist1_rows": int((selected_rows & (pos_dist == 1)).sum()),
            "dist2_rows": int((selected_rows & (pos_dist == 2)).sum()),
            "dist3_rows": int((selected_rows & (pos_dist == 3)).sum()),
        }
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "row_mask": spec.row_mask,
                "family": spec.family,
                "alpha": spec.alpha,
                "changed_cells_vs_h057": int(diff057.sum()),
                "changed_rows_vs_h057": int(selected_rows.sum()),
                "changed_cells_vs_h042": int(diff042.sum()),
                "changed_rows_vs_h042": int(diff042.any(axis=1).sum()),
                "q2_changed_vs_h057": int(diff057[:, TARGETS.index("Q2")].sum()),
                "posterior_delta_vs_h057": float(bce(prob, q).mean() - base_loss),
                "mean_aux_selected": float(np.mean(aux[allowed])),
                **per_distance,
                **per_target,
            }
        )
        paths[candidate_id] = path
        masks[candidate_id] = diff057

    candidates = pd.DataFrame(rows).sort_values(
        ["posterior_delta_vs_h057", "changed_cells_vs_h057"],
        ascending=[True, False],
    ).reset_index(drop=True)
    return candidates, paths, masks


def main() -> None:
    h012 = load_sub(H012)
    h042 = load_sub(H042, h012)
    h057 = load_sub(H057, h012)
    sample = h057[KEYS].copy()
    h012_prob = clip_prob(h012[TARGETS].to_numpy())
    h042_prob = clip_prob(h042[TARGETS].to_numpy())
    h057_prob = clip_prob(h057[TARGETS].to_numpy())
    q, aux = pivot_h055_posterior(sample)

    anchor_rows = np.abs(h042_prob[:, TARGETS.index("Q2")] - h012_prob[:, TARGETS.index("Q2")]) > TOL
    dist = episode_distances(sample, anchor_rows)
    dist.to_csv(OUT / "h059_episode_distance_rows.csv", index=False)

    candidates, paths, masks = build_candidates(sample, h042_prob, h057_prob, q, aux, dist)
    candidates.to_csv(OUT / "h059_candidate_scores.csv", index=False)

    chosen_row = candidates[
        candidates["candidate_id"].str.contains("h059_episode_pos_r3_full_nonq2_a1p1_", regex=False)
    ].iloc[0].to_dict()
    chosen_id = str(chosen_row["candidate_id"])
    chosen_internal = paths[chosen_id]
    chosen_prob = clip_prob(pd.read_csv(chosen_internal)[TARGETS].to_numpy())
    promoted = ROOT / f"submission_h059_episode_r3_fullvector_{short_hash(chosen_prob)}_uploadsafe.csv"
    shutil.copy2(chosen_internal, promoted)

    selected = dist.loc[masks[chosen_id].any(axis=1)].copy()
    selected["selected_new_cells"] = masks[chosen_id].sum(axis=1)[selected.index]
    selected.to_csv(OUT / "h059_selected_episode_rows.csv", index=False)

    validation = validate_upload(promoted, sample)
    decision = pd.DataFrame([{**chosen_row, "promoted_file": promoted.name, "promoted_path": str(promoted), **validation}])
    decision.to_csv(OUT / "h059_decision.csv", index=False)

    report = f"""# H059 Episode-Spread Full-Vector HS-JEPA

## Question

Are H042/H057's public-positive rows isolated events, or visible markers of a
same-subject lifestyle episode that spills into nearby days?

## Design

- base: H057 public frontier (`0.5677475939`);
- anchor rows: the `45` H042 Q2-support rows;
- protected behavior: leave anchor rows exactly as H057 and freeze Q2
  everywhere;
- target representation: H055 post-feedback public-listener posterior;
- action: decode Q1/Q3/S1-S4 on same-subject neighbor rows around the anchor;
- promoted mask: same-subject position radius `3`;
- promoted alpha: `1.10` with distance decay `1.0/0.55/0.35` for distance
  `1/2/3`.

## Candidate Sweep

{md_table(candidates[['candidate_id', 'row_mask', 'family', 'alpha', 'changed_cells_vs_h057', 'changed_rows_vs_h057', 'changed_cells_vs_h042', 'posterior_delta_vs_h057', 'dist1_rows', 'dist2_rows', 'dist3_rows']], 30)}

## Promoted Candidate

`{promoted.name}`

## Anatomy

- anchor rows: `{int(anchor_rows.sum())}`;
- selected added rows vs H057: `{int(chosen_row['changed_rows_vs_h057'])}`;
- selected added cells vs H057: `{int(chosen_row['changed_cells_vs_h057'])}`;
- total changed cells vs H042: `{int(chosen_row['changed_cells_vs_h042'])}`;
- Q2 changed vs H057: `{int(chosen_row['q2_changed_vs_h057'])}`;
- distance rows: d1 `{int(chosen_row['dist1_rows'])}`, d2 `{int(chosen_row['dist2_rows'])}`, d3 `{int(chosen_row['dist3_rows'])}`;
- posterior delta vs H057: `{float(chosen_row['posterior_delta_vs_h057']):.9f}`;
- upload validation: `{validation['validation_ok']}`.

## Public Interpretation

If H059 improves over H057, HS-JEPA should model hidden human state as a
same-subject temporal episode, not a single-row marker. If H059 fails, H057's
45 anchor rows are likely a precise public-positive support and episode spread
should be killed or made much more selective.
"""
    (OUT / "h059_report.md").write_text(report)

    print(decision.T.to_string())


if __name__ == "__main__":
    main()
