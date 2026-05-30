#!/usr/bin/env python3
"""E245: feature-NN1 LeJEPA compatibility audit for the live E237 branch.

E207 said the only regime that looks like a plausible true-JEPA positive-pair
setup is `broad_stage2_pca64 / feature_nn1_all`. E217 did not train on that
regime; it used subject-neighborhood full-row teacher targets and failed as a
submission-grade translator.

This audit asks a smaller falsifiable question before training another model:

Does E237's learned Q3 decisive-cell rollback make the E224 tensor more
compatible with the E207 feature-nearest-neighbor geometry, or is it orthogonal
to that true-JEPA regime?

No submission is created. Public LB is not used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import broad_feature_addon_builder as stage2  # noqa: E402
import e207_lejepa_identifiability_conditions_audit as e207  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
Q3 = TARGETS.index("Q3")
SEED = 20260530 + 245

FILES = {
    "e95_best": OUT / "submission_e95_hardtail_541e3973.csv",
    "e101_q2s3_tail": OUT / "submission_e101_q2s3tail_177569bc.csv",
    "e154_repaired": OUT / "submission_e154_s3repair_9f2e2e73.csv",
    "e166_broad": OUT / "submission_e166_broadsurv_s0p01_d8bfa94b.csv",
    "e176_q2_damped": OUT / "submission_e176_abl_q2_to0p75_91e49725.csv",
    "e216_bad_s2": OUT / "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "e224_clean_jepa_body": OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv",
    "e237_q3_cell_tail": OUT
    / "submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv",
}

SUMMARY_OUT = OUT / "e245_feature_nn1_jepa_compat_summary.csv"
NULL_OUT = OUT / "e245_feature_nn1_jepa_compat_null.csv"
LOCAL_OUT = OUT / "e245_feature_nn1_jepa_compat_local_cells.csv"
REPORT_OUT = OUT / "e245_feature_nn1_jepa_compat_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def md_table(df: pd.DataFrame, n: int = 30) -> str:
    if df.empty:
        return "_empty_"
    shown = df.head(n)
    cols = [str(c) for c in shown.columns]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in shown.iterrows():
        values = []
        for col in shown.columns:
            val = row[col]
            if isinstance(val, float):
                values.append(f"{val:.9g}")
            else:
                values.append(str(val))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def read_sub(path: Path, sub_raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not df[SUB_KEY].equals(sub_raw[SUB_KEY]):
        raise ValueError(f"{path.name}: key/order mismatch after {KEY} sort")
    return df


def submission_nn1_pairs(rows: pd.DataFrame, latent: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sub_global = rows.index[rows["split"].to_numpy() == "submission"].to_numpy(dtype=int)
    sub_pos = rows.loc[sub_global, "row_in_split"].to_numpy(dtype=int)
    sub_z = latent[sub_global]
    nbrs = NearestNeighbors(n_neighbors=2, metric="euclidean")
    nbrs.fit(sub_z)
    dist, ind = nbrs.kneighbors(sub_z)
    i = np.arange(len(sub_pos), dtype=int)
    j = ind[:, 1].astype(int)
    return sub_pos[i], sub_pos[j], dist[:, 1]


def movement_health(name: str, logits: np.ndarray, base_logits: np.ndarray, i: np.ndarray, j: np.ndarray) -> dict[str, object]:
    move = finite(logits - base_logits)
    pair_rmse = float(np.sqrt(np.mean((move[i] - move[j]) ** 2)))
    global_rmse = float(np.sqrt(np.mean(move**2)))
    q3_pair_rmse = float(np.sqrt(np.mean((move[i, Q3] - move[j, Q3]) ** 2)))
    q3_global_rmse = float(np.sqrt(np.mean(move[:, Q3] ** 2)))
    pred_q3_abs = float(np.mean(np.abs(logits[i, Q3] - logits[j, Q3])))
    pred_all_rmse = float(np.sqrt(np.mean((logits[i] - logits[j]) ** 2)))
    cov = e207.covariance_health(move)
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()
    rng = np.random.default_rng(SEED + int(digest[:10], 16) % 100_000)
    proj = e207.projection_moments(move, rng)
    return {
        "candidate": name,
        "movement_global_rmse": global_rmse,
        "movement_pair_rmse": pair_rmse,
        "movement_pair_ratio": pair_rmse / max(global_rmse, 1.0e-12),
        "q3_movement_global_rmse": q3_global_rmse,
        "q3_movement_pair_rmse": q3_pair_rmse,
        "q3_movement_pair_ratio": q3_pair_rmse / max(q3_global_rmse, 1.0e-12),
        "pred_q3_pair_abs": pred_q3_abs,
        "pred_all_pair_rmse": pred_all_rmse,
        "rank_fraction": cov["rank_fraction"],
        "cov_condition": cov["cov_condition"],
        "projection_gauss_score": e207.gaussian_score(proj),
    }


def pair_abs_mean(q3_logit: np.ndarray, i: np.ndarray, j: np.ndarray, pair_mask: np.ndarray | None = None) -> float:
    if pair_mask is None:
        pair_mask = np.ones(len(i), dtype=bool)
    if int(pair_mask.sum()) == 0:
        return float("nan")
    return float(np.mean(np.abs(q3_logit[i[pair_mask]] - q3_logit[j[pair_mask]])))


def rollback_delta(
    rows_to_rollback: np.ndarray,
    e224_q3: np.ndarray,
    e154_q3: np.ndarray,
    i: np.ndarray,
    j: np.ndarray,
) -> dict[str, float]:
    candidate = e224_q3.copy()
    candidate[rows_to_rollback] = e154_q3[rows_to_rollback]
    changed = np.zeros(len(candidate), dtype=bool)
    changed[rows_to_rollback] = True
    affected = changed[i] | changed[j]
    return {
        "global_pair_abs_delta": pair_abs_mean(candidate, i, j) - pair_abs_mean(e224_q3, i, j),
        "affected_pair_abs_delta": pair_abs_mean(candidate, i, j, affected) - pair_abs_mean(e224_q3, i, j, affected),
        "affected_pair_count": float(affected.sum()),
    }


def random_null(
    pool: np.ndarray,
    n_select: int,
    label: str,
    e224_q3: np.ndarray,
    e154_q3: np.ndarray,
    i: np.ndarray,
    j: np.ndarray,
    n_iter: int = 5000,
) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + len(pool) * 17 + n_select)
    rows = []
    for k in range(n_iter):
        chosen = rng.choice(pool, size=n_select, replace=False)
        delta = rollback_delta(chosen, e224_q3, e154_q3, i, j)
        rows.append({"null": label, "iter": k, **delta})
    return pd.DataFrame(rows)


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    rows = e207.make_rows(train_raw, sub_raw)
    broad_space = e207.load_pair_feature_space(train_feat, sub_feat)
    i, j, nn_dist = submission_nn1_pairs(rows, broad_space.x)

    subs = {name: read_sub(path, sub_raw) for name, path in FILES.items() if path.exists()}
    logits = {name: logit(df[TARGETS].to_numpy(dtype=np.float64)) for name, df in subs.items()}
    base = logits["e95_best"]

    summary = pd.DataFrame([movement_health(name, z, base, i, j) for name, z in logits.items()]).sort_values(
        ["movement_pair_ratio", "q3_movement_pair_ratio"],
        ascending=[True, True],
    )

    e224_q3 = logits["e224_clean_jepa_body"][:, Q3]
    e154_q3 = logits["e154_repaired"][:, Q3]
    e237_q3 = logits["e237_q3_cell_tail"][:, Q3]
    changed = np.flatnonzero(np.abs(e237_q3 - e224_q3) > 1.0e-12)
    actual = rollback_delta(changed, e224_q3, e154_q3, i, j)

    potential_amp = np.abs(e224_q3 - e154_q3)
    top50 = np.argsort(-potential_amp)[:50]
    null = pd.concat(
        [
            random_null(np.arange(len(e224_q3)), len(changed), "all_rows", e224_q3, e154_q3, i, j),
            random_null(top50, len(changed), "top50_e224_e154_amp", e224_q3, e154_q3, i, j),
        ],
        ignore_index=True,
    )

    null_summary_rows = []
    for label, part in null.groupby("null"):
        for metric in ["global_pair_abs_delta", "affected_pair_abs_delta"]:
            vals = part[metric].to_numpy(dtype=float)
            obs = actual[metric]
            null_summary_rows.append(
                {
                    "null": label,
                    "metric": metric,
                    "actual": obs,
                    "null_mean": float(vals.mean()),
                    "null_q05": float(np.quantile(vals, 0.05)),
                    "null_q50": float(np.quantile(vals, 0.50)),
                    "null_q95": float(np.quantile(vals, 0.95)),
                    "actual_percentile_low_is_smoother": float((vals <= obs).mean()),
                }
            )
    null_summary = pd.DataFrame(null_summary_rows)

    changed_mask = np.zeros(len(e224_q3), dtype=bool)
    changed_mask[changed] = True
    affected = changed_mask[i] | changed_mask[j]
    local = pd.DataFrame(
        {
            "row_idx": np.arange(len(e224_q3)),
            **{col: subs["e237_q3_cell_tail"][col].to_numpy() for col in SUB_KEY},
            "nn_row_idx": j,
            "nn_dist": nn_dist,
            "e237_changed": changed_mask,
            "pair_source_changed": changed_mask[i],
            "pair_target_changed": changed_mask[j],
            "pair_affected": affected,
            "e224_q3_logit": e224_q3,
            "e154_q3_logit": e154_q3,
            "e237_q3_logit": e237_q3,
            "rollback_logit_step": e154_q3 - e224_q3,
            "e224_pair_abs": np.abs(e224_q3[i] - e224_q3[j]),
            "e237_pair_abs": np.abs(e237_q3[i] - e237_q3[j]),
            "pair_abs_delta": np.abs(e237_q3[i] - e237_q3[j]) - np.abs(e224_q3[i] - e224_q3[j]),
        }
    )

    summary.to_csv(SUMMARY_OUT, index=False)
    null_summary.to_csv(NULL_OUT, index=False)
    local.to_csv(LOCAL_OUT, index=False)

    true_regime = pd.read_csv(OUT / "e207_lejepa_identifiability_conditions_audit_summary.csv")
    true_regime = true_regime[
        (true_regime["latent"] == "broad_stage2_pca64") & (true_regime["pair_regime"] == "feature_nn1_all")
    ].head(1)

    verdict = "supportive" if actual["global_pair_abs_delta"] < 0 and actual["affected_pair_abs_delta"] < 0 else "not_supportive"
    if (
        actual["global_pair_abs_delta"] < 0
        and actual["affected_pair_abs_delta"] < 0
        and (null_summary["actual_percentile_low_is_smoother"] < 0.10).any()
    ):
        verdict = "strong_supportive"

    lines = [
        "# E245 Feature-NN1 JEPA Compatibility Audit",
        "",
        "## Question",
        "",
        "E207 identified `broad_stage2_pca64 / feature_nn1_all` as the only `true_jepa_candidate` positive-pair regime. E245 asks whether the live E237 Q3 decisive-cell rollback is compatible with that regime.",
        "",
        "This is not a submission generator. It is a LeJEPA-style health audit for the E237 hidden-world bet.",
        "",
        "## Verdict",
        "",
        f"- verdict: `{verdict}`",
        f"- E237 changed rows: `{len(changed)}`",
        f"- actual global Q3 NN-pair abs-logit delta: `{actual['global_pair_abs_delta']:.12g}`",
        f"- actual affected Q3 NN-pair abs-logit delta: `{actual['affected_pair_abs_delta']:.12g}`",
        f"- affected directed NN pairs: `{int(actual['affected_pair_count'])}`",
        "",
        "A negative delta means the rollback made feature-nearest-neighbor Q3 logits smoother under the E207 true-JEPA pair regime.",
        "",
        "## E207 Regime Reference",
        "",
        md_table(true_regime[["latent", "pair_regime", "lejepa_readiness", "decision", "rho_abs_mean", "alignment_ratio", "increment_gauss_score", "train_label_consistency"]]),
        "",
        "## Candidate Movement Health",
        "",
        md_table(summary),
        "",
        "## Random Rollback Null",
        "",
        md_table(null_summary),
        "",
        "## Largest Local Pair Changes",
        "",
        md_table(local[local["pair_affected"]].sort_values("pair_abs_delta").head(20)),
        "",
        "## Interpretation",
        "",
        "- If E237 improves NN-pair smoothness versus both all-row and top50-amplitude nulls, that strengthens the view that it is aligned with the only identifiable LeJEPA pair regime.",
        "- If it is neutral or worse, E237 remains a valid tail-discrimination sensor from E242, but not evidence that the E207 feature-neighbor world model is already solving the Q3 tail.",
        "- Public feedback is still required for the final E237 branch decision; E245 only audits representation compatibility.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"verdict={verdict}")
    print(f"changed={len(changed)}")
    print(f"actual_global_delta={actual['global_pair_abs_delta']:.12g}")
    print(f"actual_affected_delta={actual['affected_pair_abs_delta']:.12g}")
    print(summary[["candidate", "movement_pair_ratio", "q3_movement_pair_ratio", "projection_gauss_score"]].to_string(index=False))
    print(null_summary.to_string(index=False))


if __name__ == "__main__":
    main()
