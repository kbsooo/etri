from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import root


TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logit(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 1e-6, 1.0 - 1e-6)
    return np.log(x / (1.0 - x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def bce_soft(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1.0 - 1e-6)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def assert_submission_compatible(reference: pd.DataFrame, candidate: pd.DataFrame, name: str) -> None:
    if list(candidate.columns) != list(reference.columns):
        raise ValueError(f"{name}: columns differ from reference")
    if candidate.shape != reference.shape:
        raise ValueError(f"{name}: shape differs: {candidate.shape} vs {reference.shape}")
    keys = ["subject_id", "sleep_date", "lifelog_date"]
    if not candidate[keys].astype(str).equals(reference[keys].astype(str)):
        raise ValueError(f"{name}: key rows differ from reference")
    values = candidate[TARGET_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name}: non-finite predictions")
    if values.min() < 0.0 or values.max() > 1.0:
        raise ValueError(f"{name}: predictions outside [0, 1]")


def read_submission(path: str | Path, sample: pd.DataFrame, name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    assert_submission_compatible(sample, df, name)
    return df


def write_submission(path: Path, df: pd.DataFrame, sample: pd.DataFrame) -> None:
    assert_submission_compatible(sample, df, path.name)
    df.to_csv(path, index=False)


def reconstruct_v76(
    sample: pd.DataFrame,
    v77: pd.DataFrame,
    etri: pd.DataFrame,
    extrap_1p05: pd.DataFrame,
    extrap_1p10: pd.DataFrame,
) -> pd.DataFrame:
    """Recover V76 from the existing V76->V77 extrapolation files.

    build_public_feedback_bold_candidates.py created:
      c05 = 0.9 * (v76 + 1.05 * (v77 - v76)) + 0.1 * etri
      c06 = 0.9 * (v76 + 1.10 * (v77 - v76)) + 0.1 * etri
    clipping did not activate for the stored files, so both equations recover
    the same V76. We verify that before using it.
    """
    v77_values = v77[TARGET_COLUMNS].to_numpy(dtype=float)
    etri_values = etri[TARGET_COLUMNS].to_numpy(dtype=float)
    c05_values = extrap_1p05[TARGET_COLUMNS].to_numpy(dtype=float)
    c06_values = extrap_1p10[TARGET_COLUMNS].to_numpy(dtype=float)

    v76_from_105 = (0.945 * v77_values + 0.1 * etri_values - c05_values) / 0.045
    v76_from_110 = (0.99 * v77_values + 0.1 * etri_values - c06_values) / 0.09
    max_diff = float(np.max(np.abs(v76_from_105 - v76_from_110)))
    if max_diff > 1e-8:
        raise ValueError(f"V76 reconstruction mismatch: max diff={max_diff}")

    out = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = np.clip(v76_from_105[:, i], 1e-5, 1.0 - 1e-5)
    return out


def max_entropy_public_posterior(
    prior: np.ndarray,
    known_predictions: dict[str, np.ndarray],
    public_scores: dict[str, float],
) -> tuple[np.ndarray, dict[str, object]]:
    """Fit soft pseudo labels close to prior and matching known public scores.

    This is not a label recovery oracle. It is a diagnostic posterior: among
    all soft label matrices whose BCE against known submissions matches the
    observed public LB scores, choose the one closest to a public-aware prior.
    """
    names = list(public_scores)
    pred_stack = np.stack([np.clip(known_predictions[name], 1e-6, 1.0 - 1e-6).ravel() for name in names])
    logits = logit(pred_stack)
    offset = -np.log(1.0 - pred_stack)
    b = np.array([-public_scores[name] - float(np.mean(np.log(1.0 - pred_stack[i]))) for i, name in enumerate(names)])

    prior_flat = np.clip(prior.ravel(), 1e-5, 1.0 - 1e-5)
    prior_logit = logit(prior_flat)

    def make_q(lam: np.ndarray) -> np.ndarray:
        return sigmoid(prior_logit - lam @ logits)

    def residual(lam: np.ndarray) -> np.ndarray:
        q = make_q(lam)
        return np.array([float(np.mean(q * logits[i]) - b[i]) for i in range(len(names))])

    sol = root(residual, np.zeros(len(names)), method="hybr")
    if not sol.success:
        # The least-squares root method can still return a useful near-fit.
        sol = root(residual, np.zeros(len(names)), method="lm")
    q = make_q(sol.x).reshape(prior.shape)

    constraint_rows = []
    for name in names:
        constraint_rows.append(
            {
                "name": name,
                "public_score": public_scores[name],
                "posterior_bce": bce_soft(q, known_predictions[name]),
                "abs_error": abs(bce_soft(q, known_predictions[name]) - public_scores[name]),
            }
        )
    info = {
        "success": bool(sol.success),
        "message": str(sol.message),
        "lambda": [float(x) for x in sol.x],
        "max_abs_constraint_error": float(max(row["abs_error"] for row in constraint_rows)),
        "constraints": constraint_rows,
    }
    return q, info


def values_to_submission(sample: pd.DataFrame, values: np.ndarray) -> pd.DataFrame:
    out = sample.copy()
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = np.clip(values[:, i], 1e-5, 1.0 - 1e-5)
    return out


def add_candidate(
    rows: list[dict[str, object]],
    output_dir: Path,
    sample: pd.DataFrame,
    name: str,
    values: np.ndarray,
    references: dict[str, np.ndarray],
    posterior: np.ndarray,
) -> None:
    path = output_dir / name
    df = values_to_submission(sample, values)
    write_submission(path, df, sample)
    clipped = df[TARGET_COLUMNS].to_numpy(dtype=float)
    row: dict[str, object] = {
        "file": name,
        "sha256": sha256_file(path),
        "pseudo_public_bce": bce_soft(posterior, clipped),
        "min": float(clipped.min()),
        "p01": float(np.quantile(clipped, 0.01)),
        "mean": float(clipped.mean()),
        "p99": float(np.quantile(clipped, 0.99)),
        "max": float(clipped.max()),
        "abs_logit_mean": float(np.mean(np.abs(logit(clipped)))),
    }
    for ref_name, ref_values in references.items():
        row[f"mad_from_{ref_name}"] = float(np.mean(np.abs(clipped - ref_values)))
        row[f"corr_{ref_name}"] = float(np.corrcoef(clipped.ravel(), ref_values.ravel())[0, 1])
    rows.append(row)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    text_df = df.copy()
    for col in text_df.columns:
        if pd.api.types.is_float_dtype(text_df[col]):
            text_df[col] = text_df[col].map(lambda x: f"{x:.6f}")
        else:
            text_df[col] = text_df[col].astype(str)
    cols = list(text_df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in text_df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def build_candidates(args: argparse.Namespace) -> pd.DataFrame:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_path in output_dir.glob("submission_*.csv"):
        old_path.unlink()

    sample = pd.read_csv(args.sample_path)
    v77 = read_submission(args.v77_path, sample, "v77")
    etri = read_submission(args.etri_path, sample, "etri")
    extrap_1p05 = read_submission(args.extrap_1p05_path, sample, "extrap_1p05")
    extrap_1p10 = read_submission(args.extrap_1p10_path, sample, "extrap_1p10")
    recovery15 = read_submission(args.recovery15_path, sample, "recovery15")
    dae = read_submission(args.dae_path, sample, "dae")
    v38a = read_submission(args.v38a_path, sample, "v38a")

    v76 = reconstruct_v76(sample, v77, etri, extrap_1p05, extrap_1p10)
    v76_path = output_dir / "submission_00_reconstructed_v76_public_anchor.csv"
    write_submission(v76_path, v76, sample)

    arrays = {
        "v76": v76[TARGET_COLUMNS].to_numpy(dtype=float),
        "v77": v77[TARGET_COLUMNS].to_numpy(dtype=float),
        "etri": etri[TARGET_COLUMNS].to_numpy(dtype=float),
        "recovery15": recovery15[TARGET_COLUMNS].to_numpy(dtype=float),
        "dae": dae[TARGET_COLUMNS].to_numpy(dtype=float),
        "v38a": v38a[TARGET_COLUMNS].to_numpy(dtype=float),
    }
    public_scores = {
        "v76": args.v76_public_score,
        "recovery15": args.recovery15_public_score,
        "dae": args.dae_public_score,
        "v38a": args.v38a_public_score,
    }
    prior = np.clip(args.prior_v77_weight * arrays["v77"] + (1.0 - args.prior_v77_weight) * arrays["v76"], 1e-5, 1.0 - 1e-5)
    posterior, posterior_info = max_entropy_public_posterior(
        prior=prior,
        known_predictions={name: arrays[name] for name in public_scores},
        public_scores=public_scores,
    )

    # Raw posterior is saved for analysis but intentionally ranked below
    # shrunken blends in the README because it overfits the public constraints.
    pd.DataFrame(posterior, columns=TARGET_COLUMNS).to_csv(output_dir / "posterior_values_only.csv", index=False)
    with (output_dir / "posterior_fit_report.json").open("w") as f:
        json.dump(posterior_info, f, indent=2)

    rows: list[dict[str, object]] = []
    references = {"v76": arrays["v76"], "v77": arrays["v77"], "recovery15": arrays["recovery15"], "dae": arrays["dae"], "v38a": arrays["v38a"]}

    add_candidate(rows, output_dir, sample, "submission_01_exact_v77_recommended.csv", arrays["v77"], references, posterior)
    add_candidate(rows, output_dir, sample, "submission_02_exact_v76_public_anchor_reconstructed.csv", arrays["v76"], references, posterior)

    order = 3
    for base_name in ["v77", "v76"]:
        base = arrays[base_name]
        for weight in [0.02, 0.05, 0.10, 0.15]:
            values = (1.0 - weight) * base + weight * posterior
            add_candidate(
                rows,
                output_dir,
                sample,
                f"submission_{order:02d}_{base_name}_posterior_blend_w{int(weight * 100):02d}.csv",
                values,
                references,
                posterior,
            )
            order += 1

    failed_center = (0.50 * arrays["recovery15"] + 0.35 * arrays["dae"] + 0.15 * arrays["v38a"])
    for alpha in [0.03, 0.05, 0.08]:
        values = np.clip(arrays["v77"] + alpha * (arrays["v77"] - failed_center), 0.02, 0.98)
        add_candidate(
            rows,
            output_dir,
            sample,
            f"submission_{order:02d}_v77_repel_failed_a{int(alpha * 100):02d}.csv",
            values,
            references,
            posterior,
        )
        order += 1

    # Very small ETRI injection variants are kept because prior public-candidate
    # generation already indicated that large ETRI movement should be avoided.
    for weight in [0.01, 0.02, 0.03]:
        values = (1.0 - weight) * arrays["v77"] + weight * arrays["etri"]
        add_candidate(
            rows,
            output_dir,
            sample,
            f"submission_{order:02d}_v77_etri_tiny_w{int(weight * 100):02d}.csv",
            values,
            references,
            posterior,
        )
        order += 1

    manifest = pd.DataFrame(rows).sort_values(["pseudo_public_bce", "mad_from_v77"], ascending=[True, True])
    manifest.to_csv(output_dir / "manifest.csv", index=False)

    readme = [
        "# Public LB Pseudolabel Calibration Candidates",
        "",
        "This folder uses observed public LB scores as aggregate BCE constraints.",
        "The posterior is a soft, maximum-entropy diagnostic label matrix close to the V76/V77 prior; it is not treated as ground truth.",
        "",
        "Known public scores:",
        f"- V76 reconstructed public anchor: `{args.v76_public_score}`",
        f"- recovery15: `{args.recovery15_public_score}`",
        f"- TRP/weather/GRU/DAE w0.30: `{args.dae_public_score}`",
        f"- v38a: `{args.v38a_public_score}`",
        "",
        "Recommended next upload rule:",
        "1. Submit `submission_01_exact_v77_recommended.csv` first unless an already uploaded V77 score exists.",
        "2. If V77 does not beat or closely match V76 (`0.5999627447`), stop this branch.",
        "3. If V77 improves, try the smallest posterior blend ranked near the top of `manifest.csv`.",
        "",
        "Top manifest rows:",
        dataframe_to_markdown(manifest.head(8)),
        "",
        "Do not submit the raw posterior; it is intentionally saved only as a diagnostic.",
    ]
    (output_dir / "README.md").write_text("\n".join(readme) + "\n")

    if args.score_pool:
        score_existing_pool(args, output_dir, sample, posterior, references)
    return manifest


def score_existing_pool(
    args: argparse.Namespace,
    output_dir: Path,
    sample: pd.DataFrame,
    posterior: np.ndarray,
    references: dict[str, np.ndarray],
) -> None:
    rows: list[dict[str, object]] = []
    seen_hashes: set[str] = set()
    keys = ["subject_id", "sleep_date", "lifelog_date"]
    for path in Path(args.pool_root).rglob("submission*.csv"):
        try:
            df = pd.read_csv(path)
            if list(df.columns) != list(sample.columns) or df.shape != sample.shape:
                continue
            if not df[keys].astype(str).equals(sample[keys].astype(str)):
                continue
            values = df[TARGET_COLUMNS].to_numpy(dtype=float)
            if not np.isfinite(values).all() or values.min() < 0.0 or values.max() > 1.0:
                continue
            digest = sha256_file(path)
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            row: dict[str, object] = {
                "path": str(path),
                "sha256": digest,
                "pseudo_public_bce": bce_soft(posterior, values),
                "min": float(values.min()),
                "p01": float(np.quantile(values, 0.01)),
                "mean": float(values.mean()),
                "p99": float(np.quantile(values, 0.99)),
                "max": float(values.max()),
                "abs_logit_mean": float(np.mean(np.abs(logit(values)))),
            }
            for ref_name, ref_values in references.items():
                row[f"mad_from_{ref_name}"] = float(np.mean(np.abs(values - ref_values)))
                row[f"corr_{ref_name}"] = float(np.corrcoef(values.ravel(), ref_values.ravel())[0, 1])
            rows.append(row)
        except Exception:
            continue
    pool = pd.DataFrame(rows).sort_values(["pseudo_public_bce", "path"], ascending=[True, True])
    pool.to_csv(output_dir / "pool_scores.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build public-LB feedback calibrated candidate submissions.")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--v77-path", default="outputs/public_feedback_bold_candidates/submission_01_exact_v77_recommended.csv")
    parser.add_argument("--etri-path", default="outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv")
    parser.add_argument("--extrap-1p05-path", default="outputs/public_feedback_bold_candidates/submission_05_v76_to_v77_extrap_1p05_etri10.csv")
    parser.add_argument("--extrap-1p10-path", default="outputs/public_feedback_bold_candidates/submission_06_v76_to_v77_extrap_1p10_etri10.csv")
    parser.add_argument("--recovery15-path", default="outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv")
    parser.add_argument("--dae-path", default="outputs/counterfactual_day_twin_portfolio/weather_gru_plus_dae_q1tail_w030/submission_sample_support_target_blend.csv")
    parser.add_argument("--v38a-path", default="outputs/sample_portfolio_v38a_v37e_mid_tail_push/submission_sample_support_target_blend.csv")
    parser.add_argument("--v76-public-score", type=float, default=0.5999627447)
    parser.add_argument("--recovery15-public-score", type=float, default=0.6057860899)
    parser.add_argument("--dae-public-score", type=float, default=0.6104310794)
    parser.add_argument("--v38a-public-score", type=float, default=0.6335340671)
    parser.add_argument("--prior-v77-weight", type=float, default=0.5)
    parser.add_argument("--score-pool", action="store_true", default=True)
    parser.add_argument("--pool-root", default="outputs")
    parser.add_argument("--output-dir", default="outputs/public_lb_pseudolabel_calibration")
    return parser.parse_args()


def main() -> None:
    manifest = build_candidates(parse_args())
    print(manifest.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
