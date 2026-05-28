from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

ANCHORS = {
    "anchor578": ("submission_hybrid_0p578_logit_after_subject_final9_strict.csv", 0.5784273528),
    "stage2": ("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", 0.5779449757),
    "ordinal": ("submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv", 0.5783033652),
    "raw05": ("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", 0.5775263072),
    "latent_q2": ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862),
    "latent_resid": ("submission_jepa_latent_residual_probe.csv", 0.5812273278),
}

PRIORS = {
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "stage2": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "efmicro3": "submission_raw05_jepa_efmicro_3eece507.csv",
    "efmicro5": "submission_raw05_jepa_efmicro_5d2d2af0.csv",
    "energyfront": "submission_raw05_jepa_energyfront_a190aa25.csv",
    "siggate": "submission_raw05_jepa_siggate_6d681440.csv",
    "compatband": "submission_raw05_jepa_compatband_e065e98e.csv",
}

TARGET_MASKS = {
    "all": TARGETS,
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3s4": ["Q3", "S4"],
    "ctx": ["Q1", "Q2", "S1", "S2", "S3"],
    "q1q3s34": ["Q1", "Q3", "S3", "S4"],
}

GAMMAS = [0.03, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.50]

FIT_OUT = OUT / "public_lb_six_anchor_entropy_projection_fit.csv"
LOAO_OUT = OUT / "public_lb_six_anchor_entropy_projection_loao.csv"
TARGET_OUT = OUT / "public_lb_six_anchor_entropy_projection_target_summary.csv"
SCAN_OUT = OUT / "public_lb_six_anchor_entropy_projection_scan.csv"
SHORTLIST_OUT = OUT / "public_lb_six_anchor_entropy_projection_shortlist.csv"
INTEGRITY_OUT = OUT / "public_lb_six_anchor_entropy_projection_integrity.csv"
REPORT_OUT = OUT / "public_lb_six_anchor_entropy_projection_report.md"


@dataclass
class Projection:
    q: np.ndarray
    lam: np.ndarray
    expected_scores: np.ndarray
    residual: np.ndarray
    iterations: int
    converged: bool


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray | float) -> np.ndarray:
    p = clip(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA, ROOT):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(file_name)


def read_submission(file_name: str, sample: pd.DataFrame) -> pd.DataFrame:
    frame = pd.read_csv(locate(file_name), parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return frame


def score_parts(pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip(pred).reshape(-1)
    const = -np.log(1.0 - p)
    coef = np.log((1.0 - p) / p)
    return const, coef


def expected_scores(q: np.ndarray, const_mat: np.ndarray, coef_mat: np.ndarray) -> np.ndarray:
    y = clip(q).reshape(-1)
    return const_mat.mean(axis=0) + (coef_mat.T @ y) / len(y)


def solve_projection(
    prior: np.ndarray,
    const_mat: np.ndarray,
    coef_mat: np.ndarray,
    target_scores: np.ndarray,
    max_iter: int = 200,
    tol: float = 1e-11,
) -> Projection:
    z0 = logit(prior).reshape(-1)
    lam = np.zeros(coef_mat.shape[1], dtype=np.float64)
    converged = False
    best_q = sigmoid(z0)
    best_expected = expected_scores(best_q.reshape(prior.shape), const_mat, coef_mat)
    best_resid = target_scores - best_expected
    best_norm = float(np.linalg.norm(best_resid))

    for it in range(max_iter):
        z = z0 + coef_mat @ lam
        q_flat = sigmoid(z)
        exp_scores = expected_scores(q_flat.reshape(prior.shape), const_mat, coef_mat)
        resid = target_scores - exp_scores
        norm = float(np.linalg.norm(resid))
        if norm < best_norm:
            best_norm = norm
            best_q = q_flat
            best_expected = exp_scores
            best_resid = resid
        if float(np.max(np.abs(resid))) < tol:
            converged = True
            best_q = q_flat
            best_expected = exp_scores
            best_resid = resid
            break

        w = q_flat * (1.0 - q_flat)
        jac = (coef_mat.T * w) @ coef_mat / len(q_flat)
        jac += 1e-8 * np.eye(jac.shape[0])
        try:
            step = np.linalg.solve(jac, resid)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(jac) @ resid

        step_norm = float(np.linalg.norm(step))
        if step_norm > 8.0:
            step *= 8.0 / step_norm

        accepted = False
        for scale in [1.0, 0.5, 0.25, 0.1, 0.05, 0.01]:
            trial_lam = lam + scale * step
            trial_q = sigmoid(z0 + coef_mat @ trial_lam)
            trial_resid = target_scores - expected_scores(trial_q.reshape(prior.shape), const_mat, coef_mat)
            if float(np.linalg.norm(trial_resid)) < norm:
                lam = trial_lam
                accepted = True
                break
        if not accepted:
            lam += 0.01 * step

    return Projection(
        q=clip(best_q.reshape(prior.shape)),
        lam=lam,
        expected_scores=best_expected,
        residual=best_resid,
        iterations=it + 1,
        converged=converged,
    )


def blend(prior: np.ndarray, q: np.ndarray, target_names: list[str], gamma: float) -> np.ndarray:
    out = prior.copy()
    idx = [TARGETS.index(t) for t in target_names]
    out[:, idx] = sigmoid((1.0 - gamma) * logit(prior[:, idx]) + gamma * logit(q[:, idx]))
    return clip(out)


def entropy(p: np.ndarray) -> float:
    pp = clip(p)
    return float((-(pp * np.log(pp) + (1.0 - pp) * np.log(1.0 - pp))).mean())


def binary_rate(p: np.ndarray) -> float:
    return float((p >= 0.5).mean())


def target_summary(prior_name: str, prior: np.ndarray, q: np.ndarray) -> pd.DataFrame:
    rows = []
    for j, target in enumerate(TARGETS):
        delta = q[:, j] - prior[:, j]
        rows.append(
            {
                "prior": prior_name,
                "target": target,
                "prior_mean": float(prior[:, j].mean()),
                "projected_mean": float(q[:, j].mean()),
                "mean_delta": float(delta.mean()),
                "mean_abs_delta": float(np.abs(delta).mean()),
                "p90_abs_delta": float(np.quantile(np.abs(delta), 0.90)),
                "prior_ge_0p5_rate": binary_rate(prior[:, j]),
                "projected_ge_0p5_rate": binary_rate(q[:, j]),
                "projected_entropy": entropy(q[:, j]),
            }
        )
    return pd.DataFrame(rows)


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for file_name in files:
        frame = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        probs = frame[TARGETS].to_numpy(dtype=float)
        rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True))),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_probs": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(probs)),
                "max_prob": float(np.nanmax(probs)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)

    anchor_names = list(ANCHORS)
    anchor_files = [ANCHORS[name][0] for name in anchor_names]
    target_scores = np.asarray([ANCHORS[name][1] for name in anchor_names], dtype=np.float64)
    anchor_preds = [read_submission(file_name, sample)[TARGETS].to_numpy(dtype=np.float64) for file_name in anchor_files]
    const_mat = []
    coef_mat = []
    for pred in anchor_preds:
        const, coef = score_parts(pred)
        const_mat.append(const)
        coef_mat.append(coef)
    const_arr = np.vstack(const_mat).T
    coef_arr = np.vstack(coef_mat).T

    fit_rows = []
    loao_rows = []
    target_frames = []
    candidate_rows = []
    saved_files = []

    for prior_name, prior_file in PRIORS.items():
        if not locate(prior_file).exists():
            continue
        prior_frame = read_submission(prior_file, sample)
        prior = prior_frame[TARGETS].to_numpy(dtype=np.float64)
        fit = solve_projection(prior, const_arr, coef_arr, target_scores)
        target_frames.append(target_summary(prior_name, prior, fit.q))
        fit_rows.append(
            {
                "prior": prior_name,
                "prior_file": prior_file,
                "converged": fit.converged,
                "iterations": fit.iterations,
                "max_abs_residual": float(np.max(np.abs(fit.residual))),
                "l2_residual": float(np.linalg.norm(fit.residual)),
                "mean_abs_move": float(np.abs(fit.q - prior).mean()),
                "p90_abs_move": float(np.quantile(np.abs(fit.q - prior), 0.90)),
                "max_abs_move": float(np.abs(fit.q - prior).max()),
                "prior_entropy": entropy(prior),
                "projected_entropy": entropy(fit.q),
            }
            | {f"expected_{name}": float(value) for name, value in zip(anchor_names, fit.expected_scores, strict=True)}
            | {f"residual_{name}": float(value) for name, value in zip(anchor_names, fit.residual, strict=True)}
        )

        for holdout_idx, holdout_name in enumerate(anchor_names):
            keep = [i for i in range(len(anchor_names)) if i != holdout_idx]
            lo_fit = solve_projection(prior, const_arr[:, keep], coef_arr[:, keep], target_scores[keep])
            expected_all = expected_scores(lo_fit.q, const_arr, coef_arr)
            prior_expected_all = expected_scores(prior, const_arr, coef_arr)
            loao_rows.append(
                {
                    "prior": prior_name,
                    "heldout_anchor": holdout_name,
                    "heldout_file": anchor_files[holdout_idx],
                    "known_public": float(target_scores[holdout_idx]),
                    "prior_expected": float(prior_expected_all[holdout_idx]),
                    "prior_error": float(prior_expected_all[holdout_idx] - target_scores[holdout_idx]),
                    "loao_expected": float(expected_all[holdout_idx]),
                    "loao_error": float(expected_all[holdout_idx] - target_scores[holdout_idx]),
                    "fit_max_abs_residual_train_constraints": float(np.max(np.abs(lo_fit.residual))),
                    "fit_mean_abs_move": float(np.abs(lo_fit.q - prior).mean()),
                    "fit_converged": lo_fit.converged,
                }
            )

        for mask_name, targets in TARGET_MASKS.items():
            for gamma in GAMMAS:
                pred = blend(prior, fit.q, targets, gamma)
                tag = stable_tag(f"{prior_name}:{mask_name}:{gamma:.4f}:{','.join(f'{x:.10f}' for x in target_scores)}")
                file_name = f"submission_public6entropy_{prior_name}_{mask_name}_g{int(round(gamma * 1000)):03d}_{tag}.csv"
                out = prior_frame[KEY].copy()
                out[TARGETS] = pred
                out.to_csv(OUT / file_name, index=False)
                saved_files.append(file_name)
                candidate_rows.append(
                    {
                        "file": file_name,
                        "prior": prior_name,
                        "prior_file": prior_file,
                        "target_mask": mask_name,
                        "targets": ",".join(targets),
                        "gamma": gamma,
                        "projection_mean_abs_move": float(np.abs(fit.q - prior).mean()),
                        "candidate_mean_abs_move_vs_prior": float(np.abs(pred - prior).mean()),
                        "candidate_mean_abs_move_vs_projected": float(np.abs(pred - fit.q).mean()),
                        "candidate_entropy": entropy(pred),
                    }
                )

    fit_df = pd.DataFrame(fit_rows).sort_values(["max_abs_residual", "mean_abs_move"]).reset_index(drop=True)
    loao_df = pd.DataFrame(loao_rows)
    target_df = pd.concat(target_frames, ignore_index=True) if target_frames else pd.DataFrame()
    cand_df = pd.DataFrame(candidate_rows)
    proxy = public_proxy_scores(saved_files) if saved_files else pd.DataFrame()
    scan = cand_df.merge(proxy, on="file", how="left")

    if not loao_df.empty:
        loao_summary = loao_df.groupby("prior", as_index=False).agg(
            loao_mae=("loao_error", lambda s: float(np.mean(np.abs(s)))),
            loao_rmse=("loao_error", lambda s: float(np.sqrt(np.mean(np.square(s))))),
            loao_max_abs=("loao_error", lambda s: float(np.max(np.abs(s)))),
            prior_mae=("prior_error", lambda s: float(np.mean(np.abs(s)))),
        )
        scan = scan.merge(loao_summary, on="prior", how="left")

    scan["sixanchor_selection_score"] = (
        scan["posterior_expected_public_vs_anchor"].fillna(1.0)
        + 0.25 * np.abs(scan["delta_vs_raw05_rawaxis"].fillna(0.0))
        + 0.0005 * np.abs(scan["bad_residual_axis_ratio"].fillna(0.0))
        + 0.05 * np.maximum(scan["mean_abs_move_vs_raw05"].fillna(0.0) - 0.0025, 0.0)
        + 0.35 * scan["loao_mae"].fillna(0.001)
    )
    scan = scan.sort_values(
        ["sixanchor_selection_score", "posterior_expected_public_vs_anchor", "mean_abs_move_vs_raw05"],
        ascending=[True, True, True],
    ).reset_index(drop=True)

    # Keep diverse candidates: best overall plus best per prior/mask and low bad-axis probes.
    selected = [
        scan.head(30),
        scan.sort_values(["bad_residual_axis_ratio", "sixanchor_selection_score"], key=lambda s: s.abs() if s.name == "bad_residual_axis_ratio" else s).head(24),
    ]
    for _, group in scan.groupby(["prior", "target_mask"], sort=False):
        selected.append(group.head(2))
    shortlist = pd.concat(selected, ignore_index=True).drop_duplicates("file").head(96).reset_index(drop=True)

    fit_df.to_csv(FIT_OUT, index=False)
    loao_df.to_csv(LOAO_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    integrity(shortlist["file"].astype(str).tolist(), sample).to_csv(INTEGRITY_OUT, index=False)

    loao_summary_print = (
        loao_df.groupby("prior", as_index=False).agg(
            loao_mae=("loao_error", lambda s: float(np.mean(np.abs(s)))),
            loao_rmse=("loao_error", lambda s: float(np.sqrt(np.mean(np.square(s))))),
            loao_max_abs=("loao_error", lambda s: float(np.max(np.abs(s)))),
            prior_mae=("prior_error", lambda s: float(np.mean(np.abs(s)))),
        )
        .sort_values("loao_mae")
        .reset_index(drop=True)
    )

    report = [
        "# Public LB Six-Anchor Entropy Projection",
        "",
        "Uses six known public-LB submissions as linear LogLoss constraints and finds the minimum-KL pseudo-label posterior around each prior.",
        "",
        "## Anchor Constraints",
        "",
        "```csv",
        pd.DataFrame(
            [{"anchor": name, "file": ANCHORS[name][0], "public_lb": ANCHORS[name][1]} for name in anchor_names]
        ).to_csv(index=False).strip(),
        "```",
        "",
        "## Full Constraint Fit By Prior",
        "",
        "```csv",
        fit_df[
            [
                "prior",
                "converged",
                "iterations",
                "max_abs_residual",
                "mean_abs_move",
                "p90_abs_move",
                "projected_entropy",
            ]
        ]
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Leave-One-Anchor-Out Reliability",
        "",
        "```csv",
        loao_summary_print.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Candidate Scan",
        "",
        "```csv",
        scan[
            [
                "file",
                "prior",
                "target_mask",
                "gamma",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
                "loao_mae",
                "sixanchor_selection_score",
            ]
        ]
        .head(24)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Target Drift",
        "",
        "```csv",
        target_df.sort_values(["prior", "mean_abs_delta"], ascending=[True, False])
        .groupby("prior")
        .head(4)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Decision",
        "",
        "- The six-anchor constraints are exactly fit at tiny residual, but LOAO error is the real reliability check.",
        "- If LOAO error stays near the previous local-proxy error scale, use these candidates only as probes.",
        "- Prefer candidates that stay raw05-compatible on public axes; do not trust direct entropy-projected pseudo-labels just because they fit the six observed submissions.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")

    print(f"wrote {FIT_OUT}")
    print(f"wrote {LOAO_OUT}")
    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SHORTLIST_OUT}")
    print(f"saved={len(saved_files)} shortlisted={len(shortlist)}")
    print(loao_summary_print.round(10).to_string(index=False))
    print(scan.head(16).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
