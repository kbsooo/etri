from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ANCHOR_FILE = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"


def default_observations_path() -> Path:
    return OUT / "public_probe_observations.csv"


def load_public_observations(path: Path) -> pd.DataFrame:
    if path.exists():
        obs = pd.read_csv(path)
    else:
        base = pd.read_csv(OUT / "public_lb_observations.csv")
        obs = base[["file", "public_lb"]].copy()
        obs["note"] = base.get("note", "")
        obs.to_csv(path, index=False)
    obs = obs.dropna(subset=["file", "public_lb"]).copy()
    obs["file"] = obs["file"].astype(str)
    obs["public_lb"] = obs["public_lb"].astype(float)
    return obs


def load_probe_catalog() -> pd.DataFrame:
    rows = []
    rows.append({"file": ANCHOR_FILE, "probe": "anchor", "targets_changed": ""})
    rows.append({"file": STAGE2_FILE, "probe": "full_stage2", "targets_changed": ",".join(TARGETS)})
    for name in [
        "public_target_switch_probes.csv",
        "public_anchor_stage2_blend_candidates.csv",
        "public_gated_blend_candidates.csv",
        "public_presleep_q3_candidates.csv",
        "public_presleep_multitarget_candidates.csv",
        "public_presleep_blend_candidates.csv",
        "public_ordinal_q_constraint_candidates.csv",
    ]:
        path = OUT / name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        for row in df.to_dict("records"):
            rows.append(
                {
                    "file": str(row.get("file", "")),
                    "probe": str(row.get("probe", row.get("mode", ""))),
                    "targets_changed": str(row.get("targets_changed", "")),
                }
            )
    cat = pd.DataFrame(rows).drop_duplicates("file")
    for target in TARGETS:
        cat[f"x_{target}"] = cat["targets_changed"].apply(lambda s, t=target: float(t in [p for p in str(s).split(",") if p]))
    cat["is_target_switch"] = cat[[f"x_{t}" for t in TARGETS]].sum(axis=1).between(1, 7)
    return cat


def design_matrix(obs: pd.DataFrame, cat: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame, float]:
    anchor_rows = obs[obs["file"].eq(ANCHOR_FILE)]
    if anchor_rows.empty:
        raise ValueError(f"missing anchor public score for {ANCHOR_FILE}")
    anchor_public = float(anchor_rows.iloc[0]["public_lb"])
    merged = obs.merge(cat, on="file", how="left", suffixes=("", "_catalog"))
    merged = merged[~merged["file"].eq(ANCHOR_FILE)].copy()
    merged = merged[merged["is_target_switch"].fillna(False)].copy()
    x_cols = [f"x_{t}" for t in TARGETS]
    x = merged[x_cols].to_numpy(dtype=float)
    y = merged["public_lb"].to_numpy(dtype=float) - anchor_public
    return x, y, merged, anchor_public


def ridge_solution(x: np.ndarray, y: np.ndarray, prior: np.ndarray, ridge: float) -> tuple[np.ndarray, np.ndarray]:
    p = len(prior)
    xtx = x.T @ x + ridge * np.eye(p)
    rhs = x.T @ y + ridge * prior
    beta = np.linalg.solve(xtx, rhs)
    cov = np.linalg.inv(xtx)
    return beta, cov


def oof_prior() -> np.ndarray:
    cat_path = OUT / "public_target_switch_probes.csv"
    if not cat_path.exists():
        return np.zeros(len(TARGETS), dtype=float)
    df = pd.read_csv(cat_path)
    priors = []
    for target in TARGETS:
        row = df[df["probe"].eq(f"stage2only_{target.lower()}")]
        if row.empty:
            priors.append(0.0)
        else:
            priors.append(float(row.iloc[0]["oof_delta_vs_anchor"]))
    return np.asarray(priors, dtype=float)


def summarize_solution(beta: np.ndarray, cov: np.ndarray, prior: np.ndarray, x: np.ndarray, y: np.ndarray, merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    target_df = pd.DataFrame(
        {
            "target": TARGETS,
            "estimated_public_contribution": beta,
            "ridge_prior_oof_delta": prior,
            "shrink_vs_oof_prior_ratio": np.divide(beta, prior, out=np.full_like(beta, np.nan), where=np.abs(prior) > 1e-12),
            "posterior_linear_se": se,
        }
    )
    if len(x):
        fitted = x @ beta
        residual = y - fitted
        fit_df = merged[["file", "probe", "targets_changed", "public_lb"]].copy()
        fit_df["delta_vs_anchor"] = y
        fit_df["fitted_delta_vs_anchor"] = fitted
        fit_df["residual"] = residual
    else:
        fit_df = pd.DataFrame(columns=["file", "probe", "targets_changed", "public_lb", "delta_vs_anchor", "fitted_delta_vs_anchor", "residual"])
    return target_df, fit_df


def candidate_design_scores(cat: pd.DataFrame, x_existing: np.ndarray, cov: np.ndarray) -> pd.DataFrame:
    x_cols = [f"x_{t}" for t in TARGETS]
    rows = []
    existing_keys = {tuple(row.tolist()) for row in x_existing} if len(x_existing) else set()
    for row in cat.to_dict("records"):
        if row["file"] in {ANCHOR_FILE, STAGE2_FILE}:
            continue
        x = np.asarray([float(row[f"x_{t}"]) for t in TARGETS], dtype=float)
        if not x.any() or x.all():
            continue
        key = tuple(x.tolist())
        already_same_design = key in existing_keys
        variance = float(x @ cov @ x)
        information_gain = float(x @ cov @ cov @ x / max(1e-12, 1.0 + variance))
        orth_to_full = float(np.linalg.norm(x - x.mean() * np.ones_like(x)) / max(np.linalg.norm(x), 1e-12))
        rows.append(
            {
                "file": row["file"],
                "probe": row.get("probe", ""),
                "targets_changed": row.get("targets_changed", ""),
                "already_same_design_observed": already_same_design,
                "pred_delta_uncertainty": float(np.sqrt(max(variance, 0.0))),
                "expected_variance_reduction": information_gain,
                "orthogonality_to_full_stage2": orth_to_full,
                "n_targets_changed": int(x.sum()),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["already_same_design_observed", "expected_variance_reduction", "orthogonality_to_full_stage2"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observations", type=Path, default=default_observations_path())
    parser.add_argument("--ridge", type=float, default=1.0)
    args = parser.parse_args()

    obs = load_public_observations(args.observations)
    cat = load_probe_catalog()
    x, y, merged, anchor_public = design_matrix(obs, cat)
    prior = oof_prior()
    beta, cov = ridge_solution(x, y, prior, args.ridge)
    target_df, fit_df = summarize_solution(beta, cov, prior, x, y, merged)
    next_df = candidate_design_scores(cat, x, cov)

    target_df.to_csv(OUT / "public_probe_target_contribution_estimate.csv", index=False)
    fit_df.to_csv(OUT / "public_probe_observation_fit.csv", index=False)
    next_df.to_csv(OUT / "public_probe_next_design_scores.csv", index=False)

    print(f"anchor_public={anchor_public:.10f}")
    print("\ntarget contribution estimate")
    print(target_df.round(9).to_string(index=False))
    print("\nobservation fit")
    print(fit_df.round(9).to_string(index=False))
    print("\nnext design scores")
    print(next_df.head(15).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
