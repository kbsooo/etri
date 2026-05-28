from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

ANCHOR = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
ANCHOR_OOF = "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
ORDINAL_OOF = "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy"
PUBLIC2D0 = "submission_public2dblend_budget0p0.csv"
PUBLIC2D0_OOF = "final_public2dblend_budget0p0_oof.npy"
PROJ0 = "submission_projblend_cap0p0.csv"
PROJ0_OOF = "final_projblend_cap0p0_oof.npy"

CONSTRAINT_FILES = [ANCHOR, STAGE2, ORDINAL]
CONSTRAINT_OOFS = [ANCHOR_OOF, STAGE2_OOF, ORDINAL_OOF]
PRIORS = [
    ("stage2", STAGE2, STAGE2_OOF),
    ("public2d0", PUBLIC2D0, PUBLIC2D0_OOF),
    ("proj0", PROJ0, PROJ0_OOF),
    ("anchor", ANCHOR, ANCHOR_OOF),
]
GAMMAS = [0.25, 0.50, 0.75, 1.00]


@dataclass
class ProjectionResult:
    prob: np.ndarray
    lam: np.ndarray
    residual: np.ndarray
    iterations: int
    converged: bool


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def cross_entropy(q: np.ndarray, pred: np.ndarray) -> float:
    qq = clip(q).reshape(-1)
    pp = clip(pred).reshape(-1)
    return float(np.mean(-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))))


def score_features(pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip(pred).reshape(-1)
    intercept = -np.log(1.0 - p)
    coef = np.log((1.0 - p) / p)
    return intercept, coef


def scores_from_labels(y: np.ndarray, preds: list[np.ndarray]) -> np.ndarray:
    yy = y.reshape(-1).astype(float)
    out = []
    for pred in preds:
        intercept, coef = score_features(pred)
        out.append(float(np.mean(intercept + coef * yy)))
    return np.asarray(out, dtype=float)


def expected_scores(q: np.ndarray, preds: list[np.ndarray]) -> np.ndarray:
    qq = q.reshape(-1).astype(float)
    out = []
    for pred in preds:
        intercept, coef = score_features(pred)
        out.append(float(np.mean(intercept + coef * qq)))
    return np.asarray(out, dtype=float)


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def load_public_scores() -> np.ndarray:
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    return np.asarray([float(obs[file_name]) for file_name in CONSTRAINT_FILES], dtype=float)


def solve_projection(prior: np.ndarray, constraint_preds: list[np.ndarray], target_scores: np.ndarray) -> ProjectionResult:
    prior_vec = clip(prior).reshape(-1)
    z0 = logit(prior_vec)
    intercepts = []
    coefs = []
    for pred in constraint_preds:
        intercept, coef = score_features(pred)
        intercepts.append(intercept)
        coefs.append(coef)
    coef_mat = np.vstack(coefs).T
    target_moments = np.asarray(target_scores, dtype=float) - np.asarray([x.mean() for x in intercepts], dtype=float)
    lam = np.zeros(coef_mat.shape[1], dtype=float)
    converged = False
    residual = np.full(coef_mat.shape[1], np.nan)
    for it in range(80):
        q = sigmoid(z0 + coef_mat @ lam)
        moments = coef_mat.T @ q / len(q)
        residual = target_moments - moments
        if float(np.max(np.abs(residual))) < 1e-10:
            converged = True
            break
        weight = q * (1.0 - q)
        jac = (coef_mat.T * weight) @ coef_mat / len(q)
        jac += 1e-8 * np.eye(jac.shape[0])
        step = np.linalg.solve(jac, residual)
        step_norm = float(np.linalg.norm(step))
        if step_norm > 8.0:
            step *= 8.0 / step_norm
        lam += step
    q = sigmoid(z0 + coef_mat @ lam)
    moments = coef_mat.T @ q / len(q)
    residual = target_moments - moments
    return ProjectionResult(q.reshape(prior.shape), lam, residual, it + 1, converged)


def geometry_like_folds(train: pd.DataFrame, n_repeats: int = 8, target_frac: float = 0.24) -> list[tuple[np.ndarray, np.ndarray, str]]:
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    import geometry_mask_cv_experiments as geom

    return geom.geometry_folds(train, sub, n_repeats=n_repeats, target_frac=target_frac, seed=260526)


def evaluate_fold_projection(
    train: pd.DataFrame,
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    folds: list[tuple[np.ndarray, np.ndarray, str]],
) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for _tr_idx, val_idx, name in folds:
        y_val = y[val_idx]
        prior_val = prior[val_idx]
        pred_val = [p[val_idx] for p in constraint_preds]
        target_scores = scores_from_labels(y_val, pred_val)
        fit = solve_projection(prior_val, pred_val, target_scores)
        base_loss = mean_loss(y_val, prior_val)
        proj_loss = mean_loss(y_val, fit.prob)
        row: dict[str, float | str | bool | int] = {
            "fold": name,
            "rows": int(len(val_idx)),
            "base_loss": base_loss,
            "projected_loss": proj_loss,
            "delta": proj_loss - base_loss,
            "iterations": fit.iterations,
            "converged": fit.converged,
            "max_abs_constraint_residual": float(np.max(np.abs(fit.residual))),
        }
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y_val[:, j], fit.prob[:, j]) - loss_col(y_val[:, j], prior_val[:, j])
        rows.append(row)
    return pd.DataFrame(rows)


def gamma_prob(prior: np.ndarray, full: np.ndarray, gamma: float) -> np.ndarray:
    return clip(sigmoid(logit(prior) + gamma * (logit(full) - logit(prior))))


def tag_gamma(gamma: float) -> str:
    return f"g{int(round(gamma * 100)):03d}"


def table_text(df: pd.DataFrame) -> str:
    return "```\n" + df.to_string(index=False) + "\n```"


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    constraint_subs = [load_sub(name)[TARGETS].to_numpy(dtype=float) for name in CONSTRAINT_FILES]
    constraint_oofs = [clip(np.load(OUT / name)) for name in CONSTRAINT_OOFS]
    public_scores = load_public_scores()
    oof_scores = scores_from_labels(y, constraint_oofs)

    summary_rows = []
    integrity_rows = []
    candidate_rows = []
    fold_frames = []

    for prior_tag, prior_sub_name, prior_oof_name in PRIORS:
        if not (OUT / prior_sub_name).exists() or not (OUT / prior_oof_name).exists():
            continue
        prior_sub_df = load_sub(prior_sub_name)
        prior_sub = prior_sub_df[TARGETS].to_numpy(dtype=float)
        prior_oof = clip(np.load(OUT / prior_oof_name))

        public_fit = solve_projection(prior_sub, constraint_subs, public_scores)
        oof_fit = solve_projection(prior_oof, constraint_oofs, oof_scores)
        fold_eval = evaluate_fold_projection(train, prior_oof, constraint_oofs, geometry_like_folds(train))
        fold_eval["prior"] = prior_tag
        fold_frames.append(fold_eval)

        for gamma in GAMMAS:
            sub_prob = gamma_prob(prior_sub, public_fit.prob, gamma)
            oof_prob = gamma_prob(prior_oof, oof_fit.prob, gamma)
            tag = f"{prior_tag}_{tag_gamma(gamma)}"
            out = prior_sub_df.copy()
            out[TARGETS] = sub_prob
            out = out.sort_values(KEY).reset_index(drop=True)
            assert out[KEY].equals(sample[KEY])
            assert out[TARGETS].isna().sum().sum() == 0
            assert out.duplicated(KEY).sum() == 0
            sub_file = f"submission_public_entropyproj_{tag}.csv"
            oof_file = f"final_public_entropyproj_{tag}_oof.npy"
            out.to_csv(OUT / sub_file, index=False)
            np.save(OUT / oof_file, oof_prob)

            expected_public_scores = expected_scores(sub_prob, constraint_subs)
            expected_oof_scores = expected_scores(oof_prob, constraint_oofs)
            public_self_expected_loss = cross_entropy(public_fit.prob, sub_prob)
            public_projection_entropy = cross_entropy(public_fit.prob, public_fit.prob)
            oof_loss = mean_loss(y, oof_prob)
            prior_loss = mean_loss(y, prior_oof)
            row: dict[str, float | str | bool | int] = {
                "file": sub_file,
                "oof_file": oof_file,
                "prior": prior_tag,
                "gamma": gamma,
                "prior_oof_loss": prior_loss,
                "oof_loss": oof_loss,
                "oof_delta_vs_prior": oof_loss - prior_loss,
                "oof_delta_vs_stage2": oof_loss - mean_loss(y, clip(np.load(OUT / STAGE2_OOF))),
                "public_fit_converged": public_fit.converged,
                "oof_fit_converged": oof_fit.converged,
                "public_fit_iterations": public_fit.iterations,
                "oof_fit_iterations": oof_fit.iterations,
                "public_fit_max_abs_residual": float(np.max(np.abs(public_fit.residual))),
                "oof_fit_max_abs_residual": float(np.max(np.abs(oof_fit.residual))),
                "submission_abs_delta_mean_vs_prior": float(np.abs(sub_prob - prior_sub).mean()),
                "submission_abs_delta_p90_vs_prior": float(np.quantile(np.abs(sub_prob - prior_sub), 0.90)),
                "public_self_expected_loss": public_self_expected_loss,
                "public_projection_entropy": public_projection_entropy,
                "public_crossentropy_gap": public_self_expected_loss - public_projection_entropy,
                "submission_abs_delta_mean_vs_full_projection": float(np.abs(sub_prob - public_fit.prob).mean()),
                "submission_min": float(sub_prob.min()),
                "submission_max": float(sub_prob.max()),
            }
            for name, expected, observed in zip(CONSTRAINT_FILES, expected_public_scores, public_scores, strict=True):
                short = "anchor" if name == ANCHOR else "stage2" if name == STAGE2 else "ordinal"
                row[f"expected_public_{short}"] = float(expected)
                row[f"public_residual_{short}"] = float(expected - observed)
            for name, expected, observed in zip(CONSTRAINT_FILES, expected_oof_scores, oof_scores, strict=True):
                short = "anchor" if name == ANCHOR else "stage2" if name == STAGE2 else "ordinal"
                row[f"expected_oof_{short}"] = float(expected)
                row[f"oof_constraint_residual_{short}"] = float(expected - observed)
            summary_rows.append(row)
            candidate_rows.append(
                {
                    "file": sub_file,
                    "targets_changed": "entropy_projection",
                    "donor": "public_entropy_projection",
                    "mask": "all",
                    "weight": gamma,
                    "source_file": "public_entropy_projection_summary.csv",
                }
            )
            drow = {
                "file": sub_file,
                "rows": len(out),
                "dups": int(out.duplicated(KEY).sum()),
                "na": int(out[TARGETS].isna().sum().sum()),
                "min_prob": float(out[TARGETS].min().min()),
                "max_prob": float(out[TARGETS].max().max()),
            }
            for j, target in enumerate(TARGETS):
                drow[f"{target}_delta_vs_prior"] = loss_col(y[:, j], oof_prob[:, j]) - loss_col(y[:, j], prior_oof[:, j])
                drow[f"{target}_delta_vs_stage2"] = loss_col(y[:, j], oof_prob[:, j]) - loss_col(y[:, j], clip(np.load(OUT / STAGE2_OOF))[:, j])
            integrity_rows.append(drow)

    summary = (
        pd.DataFrame(summary_rows)
        .sort_values(["oof_loss", "public_self_expected_loss", "submission_abs_delta_mean_vs_prior"])
        .reset_index(drop=True)
    )
    summary.to_csv(OUT / "public_entropy_projection_summary.csv", index=False)
    pd.DataFrame(candidate_rows).to_csv(OUT / "public_entropy_projection_candidates.csv", index=False)
    pd.DataFrame(integrity_rows).to_csv(OUT / "public_entropy_projection_integrity_and_deltas.csv", index=False)
    if fold_frames:
        folds = pd.concat(fold_frames, ignore_index=True)
        folds.to_csv(OUT / "public_entropy_projection_geometry_analogue.csv", index=False)
        fold_summary = (
            folds.groupby("prior")
            .agg(
                folds=("fold", "count"),
                mean_base_loss=("base_loss", "mean"),
                mean_projected_loss=("projected_loss", "mean"),
                mean_delta=("delta", "mean"),
                win_rate=("delta", lambda s: float((s < 0).mean())),
                max_constraint_residual=("max_abs_constraint_residual", "max"),
            )
            .reset_index()
        )
        fold_summary.to_csv(OUT / "public_entropy_projection_geometry_analogue_summary.csv", index=False)

    report = []
    report.append("# Public Entropy Projection Report\n")
    report.append("Public LB scores are treated as aggregate linear constraints on the hidden binary labels.\n")
    report.append("\n## Constraint Scores\n")
    for name, public, oof in zip(CONSTRAINT_FILES, public_scores, oof_scores, strict=True):
        report.append(f"- `{name}`: public `{public:.10f}`, train OOF analogue `{oof:.9f}`\n")
    report.append("\n## Best Generated Rows\n")
    display = summary[
        [
            "file",
            "prior",
            "gamma",
            "oof_loss",
            "oof_delta_vs_stage2",
            "public_self_expected_loss",
            "public_crossentropy_gap",
            "submission_abs_delta_mean_vs_prior",
            "submission_min",
            "submission_max",
            "public_fit_max_abs_residual",
        ]
    ].head(12)
    report.append(table_text(display.round(9)))
    report.append("\n\n## Geometry Analogue\n")
    if fold_frames:
        report.append(table_text(fold_summary.round(9)))
    report.append("\n")
    (OUT / "public_entropy_projection_report.md").write_text("".join(report))

    print("[entropy projection summary]")
    print(summary.head(20).round(9).to_string(index=False))
    if fold_frames:
        print("\n[geometry analogue]")
        print(fold_summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
