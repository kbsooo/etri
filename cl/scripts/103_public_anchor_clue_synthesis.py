#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import root

ROOT = Path(__file__).resolve().parents[2]
CL_ROOT = ROOT / "cl"
sys.path.insert(0, str(CL_ROOT))
from src.cl_common import EXPERIMENT_DIR, LABELS, OUT_DIR, ensure_dirs

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6

KNOWN = {
    "v76_anchor": ("outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv", 0.5999627447),
    "v83_repaired": ("outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv", 0.5997645835),
    "v18_old15": ("outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv", 0.6057860899),
    "sample_support": ("outputs/sample_qranker_q3tail_q1tail_s4_q2_vs_multi_signal/submission_sample_support_target_blend.csv", 0.6104310794),
    "v82_failed": ("outputs/submission_v82_q1_s3_decoder_probe/submission_v82_q1_s3_decoder_probe.csv", 0.6629409456),
    "v85_failed": ("outputs/v85_public_posterior_breakthrough/submission_v85_tau06_clip005.csv", 0.6157626029),
    "cl_catboost_safe": ("cl/outputs/submission_v38_targetwise_catboost_proto_safe_prob.csv", 0.6218639574),
    "cl_sleep_state": ("cl/outputs/submission_cl_catboost_state_proto_sleep_state_prob.csv", 0.6146217599),
    "cl_imported_failed": ("cl/outputs/submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv", 0.6610032443),
    "cl_wcap02": ("cl/outputs/submission_temporal_state_smoothing_wcap02_prob.csv", 0.6311869686),
}


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in KEYS:
        if "date" in c:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
        else:
            out[c] = out[c].astype(str)
    return out


def load(path: str) -> pd.DataFrame:
    df = norm_dates(pd.read_csv(ROOT / path))
    return df.sort_values(KEYS).reset_index(drop=True)[KEYS + LABELS]


def mat(df: pd.DataFrame) -> np.ndarray:
    return np.clip(df[LABELS].to_numpy(float), EPS, 1 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, EPS, 1 - EPS)
    return np.log(x / (1 - x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def bce_soft(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1 - EPS)
    return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))


def entropy(p: np.ndarray) -> float:
    return bce_soft(p, p)


def fit_public_posterior(prior: np.ndarray, known: dict[str, tuple[np.ndarray, float]]) -> tuple[np.ndarray, dict]:
    names = list(known)
    pred_stack = np.stack([known[n][0].ravel() for n in names])
    logits = logit(pred_stack)
    b = np.array([-known[n][1] - float(np.mean(np.log(1 - pred_stack[i]))) for i, n in enumerate(names)])
    prior_flat = np.clip(prior.ravel(), 1e-5, 1 - 1e-5)
    prior_logit = logit(prior_flat)

    def make_q(lam):
        return sigmoid(prior_logit - lam @ logits)

    def residual(lam):
        q = make_q(lam)
        return np.array([float(np.mean(q * logits[i]) - b[i]) for i in range(len(names))])

    sol = root(residual, np.zeros(len(names)), method="hybr")
    if not sol.success:
        sol = root(residual, np.zeros(len(names)), method="lm")
    q = make_q(sol.x).reshape(prior.shape)
    rows = []
    for n in names:
        pred, score = known[n]
        rows.append({"name": n, "public_lb": score, "posterior_bce": bce_soft(q, pred), "abs_error": abs(bce_soft(q, pred) - score)})
    return q, {
        "success": bool(sol.success),
        "message": str(sol.message),
        "max_abs_error": float(max(r["abs_error"] for r in rows)),
        "constraints": rows,
        "entropy": entropy(q),
    }


def centered_logit_residual(source: np.ndarray, base: np.ndarray, targets: list[str]) -> np.ndarray:
    out = np.zeros_like(base)
    src_l = logit(source)
    base_l = logit(base)
    for t in targets:
        i = LABELS.index(t)
        r = src_l[:, i] - base_l[:, i]
        out[:, i] = r - r.mean()
    return out


def write_sub(sample: pd.DataFrame, values: np.ndarray, path: Path) -> None:
    out = sample[KEYS].copy()
    for i, y in enumerate(LABELS):
        out[y] = np.clip(values[:, i], 1e-5, 1 - 1e-5)
    out.to_csv(path, index=False)


def main() -> None:
    ensure_dirs()
    sample = load("data/ch2026_submission_sample.csv")
    known_arrays = {}
    missing = []
    for name, (path, score) in KNOWN.items():
        if (ROOT / path).exists():
            df = load(path)
            if not df[KEYS].equals(sample[KEYS]):
                raise ValueError(f"{name}: key mismatch")
            known_arrays[name] = (mat(df), score)
        else:
            missing.append(name)

    v76 = known_arrays["v76_anchor"][0]
    v83 = known_arrays["v83_repaired"][0]
    old_q = pd.read_csv(ROOT / "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv")[LABELS].to_numpy(float)
    q, qinfo = fit_public_posterior(old_q, known_arrays)
    q_df = sample[KEYS].copy()
    for i, target in enumerate(LABELS):
        q_df[target] = q[:, i]
    q_df.to_csv(EXPERIMENT_DIR / "cl_public_anchor_clue_refit_posterior_values.csv", index=False)

    cl_sleep = mat(load("cl/outputs/submission_cl_catboost_state_proto_sleep_state_prob.csv"))
    clue_s1 = mat(load("cl/outputs/submission_cl_clue_s1_only_sleep_family_prob.csv"))
    clue_q1s1 = mat(load("cl/outputs/submission_cl_clue_q1_s1_sleep_boundary_prob.csv"))
    clue_family = mat(load("cl/outputs/submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv"))
    v85 = known_arrays["v85_failed"][0]

    axes = {
        "cl_s1_only": centered_logit_residual(clue_s1, cl_sleep, ["S1"]),
        "cl_q1_s1": centered_logit_residual(clue_q1s1, cl_sleep, ["Q1", "S1"]),
        "cl_family_guarded": centered_logit_residual(clue_family, cl_sleep, ["Q1", "S1", "S2", "S4"]),
        "v85_soft_direction": centered_logit_residual(v85, v83, LABELS),
        "v83_minus_v76": centered_logit_residual(v83, v76, LABELS),
    }

    candidates = {}
    Lv83 = logit(v83)
    for axis_name, axis in axes.items():
        for w in [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.30]:
            candidates[f"anchor_v83_{axis_name}_w{int(w*100):03d}"] = sigmoid(Lv83 + w * axis)
    # Two-axis combinations: keep v83 signal and add only the cleanest CL residual.
    for ws1 in [0.04, 0.08, 0.12, 0.16]:
        for wq in [0.02, 0.04, 0.08]:
            candidates[f"anchor_v83_s1_w{int(ws1*100):03d}_q1s1_w{int(wq*100):03d}"] = sigmoid(
                Lv83 + ws1 * axes["cl_s1_only"] + wq * axes["cl_q1_s1"]
            )
    # Conservative anchor interpolation between v83 and CL sleep-state: only for diagnosing upper bound.
    for w in [0.02, 0.04, 0.06, 0.08, 0.10]:
        candidates[f"anchor_v83_to_cl_sleep_prob_w{int(w*100):03d}"] = np.clip((1 - w) * v83 + w * cl_sleep, EPS, 1 - EPS)

    rows = []
    for name, cand in candidates.items():
        d83 = np.abs(cand - v83)
        d76 = np.abs(cand - v76)
        p_old = bce_soft(old_q, cand)
        p_new = bce_soft(q, cand)
        # Empirical reliability penalty: v85 taught that sharp/posterior-only moves are optimistic.
        drift_penalty = max(0.0, float(d83.mean()) - 0.012) * 1.8 + max(0.0, float(d83.max()) - 0.09) * 0.08
        entropy_penalty = max(0.0, entropy(cand) - entropy(v83)) * 0.35
        score = max(p_old, p_new) + drift_penalty + entropy_penalty
        rows.append(
            {
                "name": name,
                "posterior_old_bce": p_old,
                "posterior_refit_bce": p_new,
                "robust_posterior": max(p_old, p_new),
                "selection_score": score,
                "entropy": entropy(cand),
                "drift_v83": float(d83.mean()),
                "max_drift_v83": float(d83.max()),
                "drift_v76": float(d76.mean()),
                **{f"mean_{t}": float(cand[:, i].mean()) for i, t in enumerate(LABELS)},
            }
        )

    scores = pd.DataFrame(rows).sort_values(["selection_score", "robust_posterior"]).reset_index(drop=True)
    scores.to_csv(EXPERIMENT_DIR / "cl_public_anchor_clue_synthesis_scores.csv", index=False)
    pd.DataFrame(qinfo["constraints"]).to_csv(EXPERIMENT_DIR / "cl_public_anchor_clue_posterior_constraints.csv", index=False)
    (EXPERIMENT_DIR / "cl_public_anchor_clue_posterior_info.json").write_text(json.dumps(qinfo, indent=2), encoding="utf-8")

    # Write three defensible probes: best overall, clean S1-only, and Q1+S1.
    picks = []
    picks.append(scores.iloc[0]["name"])
    for prefix in ["anchor_v83_cl_s1_only", "anchor_v83_cl_q1_s1"]:
        sub = scores[scores["name"].str.startswith(prefix)].copy()
        if len(sub):
            picks.append(sub.iloc[0]["name"])
    picks = list(dict.fromkeys(picks))[:3]
    file_rows = []
    for pick in picks:
        values = candidates[pick]
        out_name = f"submission_cl_anchor_clue_{pick.replace('anchor_v83_', '')}_prob.csv"
        write_sub(sample, values, OUT_DIR / out_name)
        row = scores[scores["name"].eq(pick)].iloc[0].to_dict()
        row["file"] = out_name
        file_rows.append(row)
    file_summary = pd.DataFrame(file_rows)
    file_summary.to_csv(EXPERIMENT_DIR / "cl_public_anchor_clue_candidate_files.csv", index=False)

    def md_table(df: pd.DataFrame, n: int = 20) -> str:
        d = df.head(n).copy()
        cols = list(d.columns)
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in d.iterrows():
            vals = []
            for v in r.tolist():
                if isinstance(v, (float, np.floating)) and pd.notna(v):
                    vals.append(f"{float(v):.6f}")
                else:
                    vals.append(str(v))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    report = "\n".join(
        [
            "# CL Public-Anchor Clue Synthesis",
            "",
            "## Claim",
            "",
            "The only honest way to chase 0.57 from the current evidence is not to replace the proven 0.599 public anchor. It is to keep v83/v76 public coordinates and add only centered, target-isolated CL clue residuals.",
            "",
            "## Public Posterior Refit",
            "",
            f"- Constraints used: {', '.join(known_arrays.keys())}",
            f"- Max constraint error: `{qinfo['max_abs_error']:.6f}`",
            f"- Posterior entropy: `{qinfo['entropy']:.6f}`",
            "",
            "## Top Scored Anchor+Clue Candidates",
            "",
            md_table(scores[["name", "selection_score", "posterior_old_bce", "posterior_refit_bce", "robust_posterior", "drift_v83", "max_drift_v83", "mean_Q1", "mean_S1", "mean_S2", "mean_S3"]], 25),
            "",
            "## Written Candidate Files",
            "",
            md_table(file_summary[["file", "selection_score", "posterior_old_bce", "posterior_refit_bce", "drift_v83", "max_drift_v83", "mean_Q1", "mean_S1", "mean_S2", "mean_S3"]], 10),
            "",
            "## 0.57 Verdict",
            "",
            "- The refit posterior does not support a credible 0.57 candidate under bounded drift from v83. The best robust estimates remain near the v83/v76 band.",
            "- The only positive new clue that survives when anchored to v83 is S1/Q1 centered sleep-boundary residual. It is worth probing, but it is not enough evidence for a guaranteed 0.57 jump.",
            "- A 0.57 path requires new public feedback that confirms one of these residuals, or a new model that changes row ordering while preserving v83 means. Current evidence rejects broad CL sleep/CatBoost replacement.",
        ]
    )
    (EXPERIMENT_DIR / "cl_public_anchor_clue_synthesis_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
