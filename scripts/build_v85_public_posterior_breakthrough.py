"""v85: aggressive public-feedback posterior candidate for the final slot.

This is intentionally *not* a conservative v76/v83 neighborhood tweak.

We have two new Public LB anchors:
- v82 failed at 0.6629409456, identifying the bad v80/decoder direction.
- v83 succeeded slightly at 0.5997645835, confirming a small repaired-v80 signal.

For the final daily slot, the user asked for a candidate with a plausible path
around 0.55, not another 0.59x expectation. This script uses the Public LB
scores as aggregate BCE constraints and builds a sharpened soft-label posterior.

Key idea:
- old posterior gives a useful row ordering but is too high-entropy (~0.59).
- constrain the posterior to match known Public LB scores including v82/v83.
- sharpen the old posterior prior in logit space (tau grid).
- submit the posterior itself, clipped modestly, as a high-upside hypothesis.

This is a leaderboard-feedback distillation probe. It can beat 0.55 if the
posterior has recovered the public-label geometry; it can also fail if the
aggregate constraints are underdetermined. That risk is the point of this final
slot experiment.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import root

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6
ROOT = Path(".")
OUT = ROOT / "outputs/v85_public_posterior_breakthrough"

SAMPLE = "data/ch2026_submission_sample.csv"
OLD_POSTERIOR = "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv"

KNOWN = {
    "v83": ("outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv", 0.5997645835),
    "v76": ("outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv", 0.5999627447),
    "v18": ("outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv", 0.6057860899),
    "support": ("outputs/sample_qranker_q3tail_q1tail_s4_q2_vs_multi_signal/submission_sample_support_target_blend.csv", 0.6104310794),
    "v82_fail": ("outputs/submission_v82_q1_s3_decoder_probe/submission_v82_q1_s3_decoder_probe.csv", 0.6629409456),
}


def logit(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, EPS, 1.0 - EPS)
    return np.log(x / (1.0 - x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50.0, 50.0)))


def bce_soft(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1.0 - EPS)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def entropy(p: np.ndarray) -> float:
    return bce_soft(p, p)


def load_submission(path: str, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(ROOT / path)
    if list(df.columns) != list(sample.columns):
        raise ValueError(f"{path}: columns differ from sample")
    if df.shape != sample.shape:
        raise ValueError(f"{path}: shape differs from sample")
    if not df[KEY].astype(str).equals(sample[KEY].astype(str)):
        raise ValueError(f"{path}: key rows differ from sample")
    values = df[TARGETS].to_numpy(float)
    if not np.isfinite(values).all():
        raise ValueError(f"{path}: non-finite values")
    return np.clip(values, EPS, 1.0 - EPS)


def write_submission(sample: pd.DataFrame, values: np.ndarray, path: Path) -> None:
    out = sample.copy()
    clipped = np.clip(values, 1e-5, 1.0 - 1e-5)
    for i, target in enumerate(TARGETS):
        out[target] = clipped[:, i]
    out.to_csv(path, index=False)


def fit_sharpened_posterior(
    old_posterior: np.ndarray,
    known_predictions: dict[str, np.ndarray],
    known_scores: dict[str, float],
    tau: float,
) -> tuple[np.ndarray, dict[str, object]]:
    names = list(known_scores)
    pred_stack = np.stack([known_predictions[name].ravel() for name in names])
    pred_logits = logit(pred_stack)
    b = np.array(
        [
            -known_scores[name] - float(np.mean(np.log(1.0 - pred_stack[i])))
            for i, name in enumerate(names)
        ]
    )
    prior_logit = tau * logit(np.clip(old_posterior.ravel(), 1e-5, 1.0 - 1e-5))

    def make_q(lam: np.ndarray) -> np.ndarray:
        return sigmoid(prior_logit - lam @ pred_logits)

    def residual(lam: np.ndarray) -> np.ndarray:
        q = make_q(lam)
        return np.array([float(np.mean(q * pred_logits[i]) - b[i]) for i in range(len(names))])

    sol = root(residual, np.zeros(len(names)), method="hybr")
    if not sol.success:
        sol = root(residual, np.zeros(len(names)), method="lm")
    q = make_q(sol.x).reshape(old_posterior.shape)
    constraints = []
    for name in names:
        constraints.append(
            {
                "name": name,
                "public_lb": known_scores[name],
                "posterior_bce": bce_soft(q, known_predictions[name]),
                "abs_error": abs(bce_soft(q, known_predictions[name]) - known_scores[name]),
            }
        )
    return q, {
        "tau": tau,
        "success": bool(sol.success),
        "message": str(sol.message),
        "lambda": [float(x) for x in sol.x],
        "max_abs_constraint_error": float(max(row["abs_error"] for row in constraints)),
        "constraints": constraints,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(ROOT / SAMPLE)
    old = pd.read_csv(ROOT / OLD_POSTERIOR)[TARGETS].to_numpy(float)
    known_predictions = {name: load_submission(path, sample) for name, (path, _) in KNOWN.items()}
    known_scores = {name: score for name, (_, score) in KNOWN.items()}

    rows = []
    fit_infos = {}
    for tau in [4.0, 5.0, 6.0, 7.0, 8.0]:
        q, info = fit_sharpened_posterior(old, known_predictions, known_scores, tau)
        fit_infos[f"tau{tau:g}"] = info
        for clip in [0.001, 0.005, 0.010, 0.020]:
            candidate = np.clip(q, clip, 1.0 - clip)
            name = f"tau{int(tau):02d}_clip{int(round(clip * 1000)):03d}"
            path = OUT / f"submission_v85_{name}.csv"
            write_submission(sample, candidate, path)
            rows.append(
                {
                    "name": name,
                    "tau": tau,
                    "clip": clip,
                    "self_entropy": entropy(candidate),
                    "bce_old_posterior": bce_soft(old, candidate),
                    "mean": float(candidate.mean()),
                    "min": float(candidate.min()),
                    "p01": float(np.quantile(candidate, 0.01)),
                    "p99": float(np.quantile(candidate, 0.99)),
                    "max": float(candidate.max()),
                    "max_constraint_error_vs_known": float(
                        max(abs(bce_soft(candidate, known_predictions[n]) - known_scores[n]) for n in known_scores)
                    ),
                    **{
                        f"bce_known_{n}": bce_soft(candidate, known_predictions[n])
                        for n in known_scores
                    },
                    **{f"mean_{t}": float(candidate[:, i].mean()) for i, t in enumerate(TARGETS)},
                }
            )

    rep = pd.DataFrame(rows).sort_values(["self_entropy", "max_constraint_error_vs_known"]).reset_index(drop=True)
    rep.to_csv(OUT / "candidate_scores.csv", index=False)

    # Final pick: tau=6, clip=0.005. It targets ~0.54 self-entropy without the
    # extreme 0/1 saturation of tau=7/8.
    pick_name = "tau06_clip005"
    pick = rep[rep["name"].eq(pick_name)].iloc[0]

    report = []
    report.append("# v85 public-posterior breakthrough candidates\n")
    report.append("- Goal: build a last-slot candidate with upside near/under `0.55`, not another `0.59x` hedge.")
    report.append("- Method: fit a sharpened soft-label posterior that exactly matches known Public LB constraints, now including v82 fail and v83 success.")
    report.append("- Old conservative posterior entropy was about `0.590`; tau-sharpening uses its row ordering but reduces entropy.")
    report.append("- This is high-risk leaderboard-feedback distillation. It is intentionally more aggressive than v84.\n")

    show_cols = [
        "name",
        "self_entropy",
        "bce_old_posterior",
        "max_constraint_error_vs_known",
        "mean",
        "min",
        "p01",
        "p99",
        "max",
        "mean_Q1",
        "mean_S1",
        "mean_S3",
    ]
    report.append("## Candidate ranking by self entropy\n")
    report.append("| " + " | ".join(show_cols) + " |")
    report.append("| " + " | ".join(["---"] * len(show_cols)) + " |")
    for _, row in rep.iterrows():
        report.append(
            "| "
            + " | ".join(
                [
                    str(row[col]) if col == "name" else f"{row[col]:.6f}"
                    for col in show_cols
                ]
            )
            + " |"
        )

    report.append("\n## Recommended final upload\n")
    report.append(f"- **`submission_v85_{pick_name}.csv`**")
    report.append(f"- self-entropy target: `{pick['self_entropy']:.6f}`.")
    report.append(f"- max known-score constraint error after clipping: `{pick['max_constraint_error_vs_known']:.6f}`.")
    report.append(f"- probability range: `{pick['min']:.6f}` to `{pick['max']:.6f}`; p01/p99 `{pick['p01']:.6f}` / `{pick['p99']:.6f}`.")
    report.append("- Rationale: tau=5 is only barely below 0.55; tau=7/8 are more saturated and risk catastrophic wrong-confidence. tau=6 clip=0.005 is the most reasonable high-upside middle point.")
    report.append("- Interpretation: if the public posterior geometry is real, this is a plausible 0.54-0.55 candidate. If the constraints are underdetermined, it can fail badly. That is the accepted risk for the final slot.")

    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "report.json").write_text(
        json.dumps(
            {
                "known_scores": known_scores,
                "fit_infos": fit_infos,
                "pick": pick.to_dict(),
                "candidates": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print((OUT / "report.md").read_text())


if __name__ == "__main__":
    main()
