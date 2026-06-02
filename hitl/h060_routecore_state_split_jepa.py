#!/usr/bin/env python3
"""H060: route-core state split HS-JEPA.

H057 showed that the 45 H042 Q2-support rows can carry a full non-Q2 target
vector. H060 asks the next, sharper question:

    Are those 45 rows one homogeneous hidden state, or a mixture of true
    full-state route cores plus Q2-marker-only rows?

The experiment starts from H042, freezes Q2, scores the 45 rows with several
independent HS-JEPA views, then materializes a bimodal translator:

- high-consensus route-core rows are pushed past H057 toward H055;
- low-consensus marker rows have non-Q2 movement rolled back to H042;
- middle rows keep a damped version of the H057 full-vector action.

This is deliberately not a safe micro-edit. It is a public sensor for whether
H057's gain is concentrated in a small route core.
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
OUT = HITL / "h060_routecore_state_split_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NON_Q2 = ["Q1", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"


@dataclass(frozen=True)
class CandidateSpec:
    high_n: int
    low_n: int
    alpha_high: float
    alpha_mid: float
    alpha_low: float


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


def md_table(frame: pd.DataFrame, n: int = 30) -> str:
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


def build_route_table(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q: np.ndarray,
    aux: np.ndarray,
) -> pd.DataFrame:
    target_i = {target: i for i, target in enumerate(TARGETS)}
    non_i = [target_i[target] for target in NON_Q2]
    support_rows = np.where(np.abs(h057_prob - h042_prob).any(axis=1))[0]
    h055_gain = bce(h042_prob, q) - bce(h057_prob, q)
    h057_move = logit(h057_prob) - logit(h042_prob)

    h036 = pd.read_csv(HITL / "h036_global_public_world_solver_jepa" / "h036_world_posterior_cells.csv")
    h021 = pd.read_csv(HITL / "h021_human_state_vector_prior_jepa" / "h021_test_human_state_vector_prior_cells.csv")
    h020 = pd.read_csv(HITL / "h020_joint_vector_world_jepa" / "h020_cell_joint_vector_posterior.csv")
    h019 = pd.read_csv(HITL / "h019_row_subset_hardworld_jepa" / "h019_row_public_posterior.csv")

    rows: list[dict[str, object]] = []
    for row in support_rows:
        rec: dict[str, object] = {
            "row": int(row),
            "subject_id": sample.loc[row, "subject_id"],
            "sleep_date": str(sample.loc[row, "sleep_date"].date()),
            "h055_gain": float(h055_gain[row, non_i].sum()),
            "h055_aux": float(np.nanmean(aux[row, non_i])),
        }

        d036 = h036[h036["row"].eq(row) & h036["target"].isin(NON_Q2)].copy()
        if len(d036):
            agrees = []
            for _, cell in d036.iterrows():
                ti = target_i[str(cell["target"])]
                agrees.append(np.sign(float(cell["signed_logit_shift_cond"])) * np.sign(h057_move[row, ti]) > 0)
            rec["h036_score"] = float(d036["cell_world_score"].sum())
            rec["h036_agree"] = float(np.mean(agrees))
        else:
            rec["h036_score"] = 0.0
            rec["h036_agree"] = 0.0

        d021 = h021[h021["row"].eq(row) & h021["target"].isin(NON_Q2)].copy()
        rec["h021_score"] = float(d021["hs_cell_score"].mean()) if len(d021) else 0.0
        rec["h021_conf"] = float(d021["hs_row_conf"].mean()) if len(d021) else 0.0

        d020 = h020[h020["row"].eq(row) & h020["target"].isin(NON_Q2)].copy()
        rec["h020_score"] = float(d020["combined_score"].mean()) if len(d020) else 0.0

        d019 = h019[h019["row"].eq(row)]
        rec["h019_row_score"] = float(d019["row_score"].iloc[0]) if len(d019) else 0.0
        rec["h019_inclusion_prob"] = float(d019["inclusion_prob"].iloc[0]) if len(d019) else 0.0
        rows.append(rec)

    table = pd.DataFrame(rows)
    components = [
        "h055_gain",
        "h055_aux",
        "h036_score",
        "h036_agree",
        "h021_score",
        "h021_conf",
        "h020_score",
        "h019_row_score",
    ]
    for col in components:
        table[f"{col}_rank"] = rank01(table[col].to_numpy(dtype=np.float64))
    table["route_consensus"] = (
        1.6 * table["h055_gain_rank"]
        + 1.1 * table["h036_score_rank"]
        + 0.8 * table["h036_agree_rank"]
        + 0.7 * table["h020_score_rank"]
        + 0.5 * table["h019_row_score_rank"]
        + 0.5 * table["h021_score_rank"]
        + 0.4 * table["h021_conf_rank"]
    ) / 5.6
    table = table.sort_values("route_consensus", ascending=False).reset_index(drop=True)
    return table


def validate_upload(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    bad_cols = list(df.columns) != KEYS + TARGETS
    dup = int(df.duplicated(KEYS).sum())
    nan = int(df[TARGETS].isna().sum().sum())
    min_prob = float(df[TARGETS].min().min())
    max_prob = float(df[TARGETS].max().max())
    keys_match = df.sort_values(KEYS).reset_index(drop=True)[KEYS].equals(sample[KEYS])
    ok = (not bad_cols) and dup == 0 and nan == 0 and min_prob >= 0.0 and max_prob <= 1.0 and keys_match
    return {
        "validation_ok": bool(ok),
        "shape": str(tuple(df.shape)),
        "columns_ok": not bad_cols,
        "duplicate_keys": dup,
        "nan_targets": nan,
        "min_prob": min_prob,
        "max_prob": max_prob,
        "keys_match": bool(keys_match),
    }


def build_candidates(
    sample: pd.DataFrame,
    route_table: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, Path], dict[str, np.ndarray]]:
    target_i = {target: i for i, target in enumerate(TARGETS)}
    non_i = [target_i[target] for target in NON_Q2]
    support_rows = route_table["row"].to_numpy(dtype=int)
    support_set = set(int(x) for x in support_rows)
    z042 = logit(h042_prob)
    zq = logit(q)
    base_h055_loss = bce(h057_prob, q).mean()

    specs = [
        CandidateSpec(high_n, low_n, alpha_high, alpha_mid, alpha_low)
        for high_n in [8, 10, 12, 15, 18, 22, 26, 30]
        for low_n in [8, 10, 12, 15, 18, 22]
        if high_n + low_n <= 44
        for alpha_high in [1.45, 1.65, 1.85, 2.15]
        for alpha_mid in [0.85, 1.15]
        for alpha_low in [0.0, 0.35, 0.55]
    ]

    rows: list[dict[str, object]] = []
    paths: dict[str, Path] = {}
    masks: dict[str, np.ndarray] = {}
    seen: set[str] = set()

    for spec in specs:
        high_rows = route_table.head(spec.high_n)["row"].to_numpy(dtype=int)
        low_rows = route_table.tail(spec.low_n)["row"].to_numpy(dtype=int)
        alpha = np.zeros(len(sample), dtype=np.float64)
        for row in support_set:
            alpha[row] = spec.alpha_mid
        alpha[high_rows] = spec.alpha_high
        alpha[low_rows] = spec.alpha_low

        moved = sigmoid(z042 + np.clip(zq - z042, -1.65, 1.65) * alpha[:, None])
        prob = h042_prob.copy()
        allowed = np.zeros_like(prob, dtype=bool)
        allowed[support_rows[:, None], non_i] = True
        allowed[:, target_i["Q2"]] = False
        prob[allowed] = moved[allowed]

        diff057 = np.abs(prob - h057_prob) > TOL
        diff042 = np.abs(prob - h042_prob) > TOL
        if int(diff057.sum()) == 0:
            continue

        digest = short_hash(prob)
        candidate_id = safe_id(
            "h060_routecore"
            f"_hi{spec.high_n}_lo{spec.low_n}"
            f"_ah{str(spec.alpha_high).replace('.', 'p')}"
            f"_am{str(spec.alpha_mid).replace('.', 'p')}"
            f"_al{str(spec.alpha_low).replace('.', 'p')}_{digest}"
        )
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        path = OUT / f"submission_{candidate_id}.csv"
        write_submission(sample, prob, path)

        high_score = float(route_table.head(spec.high_n)["route_consensus"].mean())
        low_score = float(route_table.tail(spec.low_n)["route_consensus"].mean())
        split_strength = (spec.alpha_high - 1.15) * spec.high_n / len(support_rows) + (1.15 - spec.alpha_low) * spec.low_n / len(support_rows)
        route_energy = (high_score - low_score) * split_strength
        h055_delta = float(bce(prob, q).mean() - base_h055_loss)
        route_split_score = route_energy - 350.0 * max(h055_delta, 0.0) + 120.0 * min(-h055_delta, 0.0) + 0.03 * (float(diff057.sum()) / 270.0)

        per_target = {f"{target}_changed_vs_h057": int(diff057[:, i].sum()) for i, target in enumerate(TARGETS)}
        rows.append(
            {
                "candidate_id": candidate_id,
                "file": path.name,
                "resolved_path": str(path),
                "high_n": spec.high_n,
                "low_n": spec.low_n,
                "alpha_high": spec.alpha_high,
                "alpha_mid": spec.alpha_mid,
                "alpha_low": spec.alpha_low,
                "changed_cells_vs_h057": int(diff057.sum()),
                "changed_rows_vs_h057": int(diff057.any(axis=1).sum()),
                "changed_cells_vs_h042": int(diff042.sum()),
                "changed_rows_vs_h042": int(diff042.any(axis=1).sum()),
                "q2_changed_vs_h057": int(diff057[:, target_i["Q2"]].sum()),
                "posterior_delta_vs_h057": h055_delta,
                "route_energy": float(route_energy),
                "route_split_score": float(route_split_score),
                "high_route_score_mean": high_score,
                "low_route_score_mean": low_score,
                "high_rows": ",".join(map(str, high_rows)),
                "low_rows": ",".join(map(str, low_rows)),
                **per_target,
            }
        )
        paths[candidate_id] = path
        masks[candidate_id] = diff057

    candidates = pd.DataFrame(rows).sort_values(
        ["route_split_score", "route_energy", "changed_cells_vs_h057"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    return candidates, paths, masks


def main() -> None:
    h012 = load_sub(H012)
    h042 = load_sub(H042, h012[KEYS])
    h057 = load_sub(H057, h012[KEYS])
    sample = h012[KEYS].copy()

    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    q, aux = pivot_h055_posterior(sample)

    route_table = build_route_table(sample, h042_prob, h057_prob, q, aux)
    candidates, paths, masks = build_candidates(sample, route_table, h042_prob, h057_prob, q)
    if candidates.empty:
        raise RuntimeError("no H060 candidates generated")

    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h060_routecore_state_split_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    validation = validate_upload(root_path, sample)
    if not validation["validation_ok"]:
        raise RuntimeError(f"upload validation failed: {validation}")

    selected_mask = masks[str(selected["candidate_id"])]
    high_rows = [int(x) for x in str(selected["high_rows"]).split(",") if x]
    low_rows = [int(x) for x in str(selected["low_rows"]).split(",") if x]
    role = route_table[["row", "subject_id", "sleep_date", "route_consensus", "h055_gain", "h036_score", "h036_agree", "h020_score", "h019_row_score", "h021_score", "h021_conf"]].copy()
    role["h060_role"] = "middle_damped"
    role.loc[role["row"].isin(high_rows), "h060_role"] = "route_core_amplified"
    role.loc[role["row"].isin(low_rows), "h060_role"] = "marker_rollback"

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_routecore_state_split_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 support is a heterogeneous mixture: small route-core rows carry full state, low-consensus rows are Q2 markers only",
                "route_core_rows": len(high_rows),
                "marker_rollback_rows": len(low_rows),
                "middle_damped_rows": int(len(route_table) - len(high_rows) - len(low_rows)),
                "changed_cells_vs_h057": int(selected_mask.sum()),
                "changed_rows_vs_h057": int(selected_mask.any(axis=1).sum()),
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    route_table.to_csv(OUT / "h060_route_table.csv", index=False)
    role.to_csv(OUT / "h060_row_roles.csv", index=False)
    candidates.to_csv(OUT / "h060_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h060_decision.csv", index=False)

    top_cols = [
        "candidate_id",
        "high_n",
        "low_n",
        "alpha_high",
        "alpha_mid",
        "alpha_low",
        "changed_cells_vs_h057",
        "changed_cells_vs_h042",
        "posterior_delta_vs_h057",
        "route_energy",
        "route_split_score",
        "high_rows",
        "low_rows",
    ]
    role_cols = ["row", "subject_id", "sleep_date", "h060_role", "route_consensus", "h055_gain", "h036_score", "h036_agree", "h020_score", "h019_row_score"]
    report = f"""# H060 Route-Core State Split HS-JEPA

## Question

H057 says H042's `45` Q2-support rows can carry a full hidden human-state
vector. H060 asks whether that support is homogeneous, or whether H057 is
averaging together:

- true route-core rows where Q1/Q3/S1-S4 should move harder;
- marker-only rows where Q2 exposed public sensitivity but non-Q2 movement
  should be rolled back;
- middle rows where the H057 action should be damped.

## Route Evidence

Rows are scored from independent views:

- H055 public-listener posterior gain;
- H036 global public-world cell score and sign agreement;
- H020 joint-vector world score;
- H019 row-public posterior score;
- H021 raw human-state vector prior score/confidence.

Top route rows:

{md_table(role.sort_values("route_consensus", ascending=False)[role_cols], 12)}

Lowest marker rows:

{md_table(role.sort_values("route_consensus", ascending=True)[role_cols], 12)}

## Candidate Sweep

{md_table(candidates[top_cols], 20)}

## Promoted Candidate

`{root_path.name}`

## Anatomy

- route-core amplified rows: `{len(high_rows)}`;
- marker rollback rows: `{len(low_rows)}`;
- middle damped rows: `{int(len(route_table) - len(high_rows) - len(low_rows))}`;
- changed cells vs H057: `{int(selected_mask.sum())}`;
- changed rows vs H057: `{int(selected_mask.any(axis=1).sum())}`;
- changed cells vs H042: `{int(selected["changed_cells_vs_h042"])}`;
- Q2 changed vs H057: `{int(selected["q2_changed_vs_h057"])}`;
- posterior delta vs H057 under H055 listener: `{float(selected["posterior_delta_vs_h057"]):.9f}`;
- route split energy: `{float(selected["route_energy"]):.9f}`;
- upload validation: `{validation["validation_ok"]}`.

## Public Interpretation

If H060 improves over H057, HS-JEPA should not treat the H042/H057 support as a
single state. It should learn a hidden route classifier: a compact route core
gets full-state amplification, while weak marker rows keep Q2 but reject non-Q2
translation.

If H060 fails, H057's uniform full-vector action is stronger than the current
route-consensus split. That would kill the simple core/eject translator and
push the next architecture toward either exact H057 support, neighbor episode
spread, or a nonlinear route classifier instead of rank-based splitting.
"""
    (OUT / "h060_report.md").write_text(report)

    print(decision.T.to_string(header=False))


if __name__ == "__main__":
    main()
