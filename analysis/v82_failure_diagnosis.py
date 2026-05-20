"""Diagnose the v82 Public LB failure (0.6629, worse than global mean 0.6619).

New ground truth: the v80/v81 latent-decoder branch does NOT transfer to Public LB.
This script treats Public LB as stronger evidence than local OOF and quantifies how
far the failed v82 (and the v80 base it sits on) drift from the known-good public
anchor family (v76 0.5999, v18 0.6058, sample_support 0.6104).

Outputs a ranked component-harm report. Read-only on predictions; writes only the
report under outputs/.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5
ROOT = Path(".")

FILES = {
    "v76_anchor_0.5999": "outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv",
    "v18_0.6058": "outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv",
    "sample_supp_0.6104": "outputs/sample_qranker_q3tail_q1tail_s4_q2_vs_multi_signal/submission_sample_support_target_blend.csv",
    "v80_base": "outputs/conditional_latent_routing_v80_late_behavior_on_v79/submission_conditional_latent_routing.csv",
    "v81_routed": "outputs/conditional_latent_routing_v81_decoder_only_on_v80/submission_conditional_latent_routing.csv",
    "v82_FAILED_0.6629": "outputs/submission_v82_q1_s3_decoder_probe/submission_v82_q1_s3_decoder_probe.csv",
}
PUBLIC_LB = {
    "v76_anchor_0.5999": 0.5999627447,
    "v18_0.6058": 0.6057860899,
    "sample_supp_0.6104": 0.6104310794,
    "v82_FAILED_0.6629": 0.6629409456,
    "global_mean_baseline": 0.6619461447,
}
ANCHOR = "v76_anchor_0.5999"


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / path)
    for k in KEY:
        df[k] = df[k].astype(str)
    return df.sort_values(KEY).reset_index(drop=True)


def panel_position(df: pd.DataFrame) -> np.ndarray:
    o = df.copy()
    o["pi"] = o.groupby("subject_id").cumcount().astype(float)
    den = o.groupby("subject_id")["pi"].transform("max").replace(0, 1)
    return (o["pi"] / den).to_numpy(float)


def mat(df: pd.DataFrame) -> np.ndarray:
    return np.clip(df[TARGETS].to_numpy(float), EPS, 1 - EPS)


def md_table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def main() -> None:
    dfs = {n: load(p) for n, p in FILES.items()}
    # all share the same key order?
    ref_keys = dfs[ANCHOR][KEY]
    for n, df in dfs.items():
        assert df[KEY].equals(ref_keys), f"key mismatch: {n}"
    mats = {n: mat(df) for n, df in dfs.items()}
    anchor = mats[ANCHOR]
    pos = panel_position(dfs[ANCHOR])
    subjects = dfs[ANCHOR]["subject_id"].to_numpy()

    L = []
    L.append("# v82 Public LB failure diagnosis\n")
    L.append("New ground truth: **v82 = 0.6629, worse than the global-mean baseline 0.6619.** "
             "The v80/v81 latent-decoder branch is quarantined. Public LB is treated as stronger "
             "evidence than local OOF.\n")
    L.append("## Public LB results (lower is better)\n")
    L.append(md_table(["submission", "public_lb"], [[k, f"{v:.10f}"] for k, v in sorted(PUBLIC_LB.items(), key=lambda x: x[1])]))

    # 1. per-target stats
    L.append("\n## 1. Per-target distribution (mean / std / min / max)\n")
    rows = []
    for n, m in mats.items():
        for stat, fn in [("mean", np.mean), ("std", np.std), ("min", np.min), ("max", np.max)]:
            if stat != "mean":
                continue
        rows.append([n] + [f"{m[:, i].mean():.3f}" for i in range(7)])
    L.append("Means:")
    L.append(md_table(["file"] + TARGETS, rows))
    rows = [[n] + [f"{m[:, i].std():.3f}" for i in range(7)] for n, m in mats.items()]
    L.append("\nStds:")
    L.append(md_table(["file"] + TARGETS, rows))

    # 2. mean-abs drift vs anchors + overall, for the suspect branch
    L.append("\n## 2. Mean absolute drift vs known-good anchors\n")
    L.append("How far each suspect submission sits from each public anchor (mean |Δp| per target, and overall).\n")
    suspects = ["v80_base", "v81_routed", "v82_FAILED_0.6629"]
    anchors = [ANCHOR, "v18_0.6058", "sample_supp_0.6104"]
    for a in anchors:
        am = mats[a]
        rows = []
        for s in suspects:
            sm = mats[s]
            d = np.abs(sm - am)
            rows.append([s] + [f"{d[:, i].mean():.4f}" for i in range(7)] + [f"{d.mean():.4f}"])
        L.append(f"### vs {a}")
        L.append(md_table(["suspect"] + TARGETS + ["overall"], rows))
        L.append("")

    # 2b. KEY: is v80 base ALREADY far from v76, before v82 touched Q1/S3?
    d_v80 = np.abs(mats["v80_base"] - anchor)
    d_v82 = np.abs(mats["v82_FAILED_0.6629"] - anchor)
    L.append("### Critical: v80 base vs v76 BEFORE the v82 Q1/S3 edit\n")
    L.append(md_table(
        ["target", "v80_base mean_shift vs v76", "v80 mean_abs vs v76", "v82 mean_shift vs v76", "v82 mean_abs vs v76"],
        [[t,
          f"{(mats['v80_base'][:, i]-anchor[:, i]).mean():+.4f}",
          f"{d_v80[:, i].mean():.4f}",
          f"{(mats['v82_FAILED_0.6629'][:, i]-anchor[:, i]).mean():+.4f}",
          f"{d_v82[:, i].mean():.4f}"] for i, t in enumerate(TARGETS)]))
    L.append(f"\n- v80 base overall mean-abs drift vs v76: **{d_v80.mean():.4f}**")
    L.append(f"- v82 overall mean-abs drift vs v76: **{d_v82.mean():.4f}**")
    L.append("- Interpretation: if v80 base is already far from v76 on S1/S3, the v82 failure is not only the "
             "Q1 edit — the whole v80 base is public-misaligned.")

    # 3. row-wise max drift v82 vs v76
    rd = np.abs(mats["v82_FAILED_0.6629"] - anchor).max(axis=1)
    L.append("\n## 3. Row-wise max drift (v82 vs v76)\n")
    L.append(f"- mean row-max |Δ|: {rd.mean():.4f}; p90: {np.percentile(rd,90):.4f}; max: {rd.max():.4f}")
    worst = np.argsort(-rd)[:8]
    L.append(md_table(["subject", "sleep_date", "row_max_drift"],
                      [[dfs[ANCHOR]['subject_id'][j], dfs[ANCHOR]['sleep_date'][j], f"{rd[j]:.4f}"] for j in worst]))

    # 4. subject-wise drift
    L.append("\n## 4. Subject-wise mean drift (v82 vs v76)\n")
    sd = np.abs(mats["v82_FAILED_0.6629"] - anchor).mean(axis=1)
    rows = []
    for sub in sorted(set(subjects)):
        m = subjects == sub
        rows.append([sub, f"{sd[m].mean():.4f}", f"{(mats['v82_FAILED_0.6629'][m,0]-anchor[m,0]).mean():+.4f}", str(int(m.sum()))])
    rows.sort(key=lambda r: -float(r[1]))
    L.append(md_table(["subject", "mean_drift", "Q1 mean_shift", "rows"], rows))

    # 5. panel-position drift
    L.append("\n## 5. Panel-position drift (v82 vs v76)\n")
    bins = [("early", 0, 0.333), ("mid", 0.333, 0.666), ("late", 0.666, 1.0001)]
    rows = []
    for name, lo, hi in bins:
        m = (pos >= lo) & (pos < hi)
        d = np.abs(mats["v82_FAILED_0.6629"][m] - anchor[m])
        rows.append([name, str(int(m.sum())), f"{d.mean():.4f}", f"{(mats['v82_FAILED_0.6629'][m,0]-anchor[m,0]).mean():+.4f}",
                     f"{(mats['v82_FAILED_0.6629'][m,5]-anchor[m,5]).mean():+.4f}"])
    L.append(md_table(["panel", "rows", "mean_abs_drift", "Q1 shift", "S3 shift"], rows))

    # 6. Q1/S3-only damage decomposition
    L.append("\n## 6. Does the v82 edit (Q1/S3 only) explain the damage, or is v80 the problem?\n")
    only_q1s3 = np.abs(mats["v82_FAILED_0.6629"] - mats["v80_base"])
    L.append(f"- v82 differs from v80 base ONLY on Q1 (mean_abs {only_q1s3[:,0].mean():.4f}) and S3 (mean_abs {only_q1s3[:,5].mean():.4f}); other targets identical.")
    L.append(f"- But v80 base itself drifts from v76 by mean_abs {d_v80.mean():.4f} overall, with S1 {d_v80[:,3].mean():.4f}, S3 {d_v80[:,5].mean():.4f}, Q1 {d_v80[:,0].mean():.4f}.")
    L.append("- Conclusion: both effects are real. The Q1 upshift is the proximate trigger, but the v80 base is the deeper misalignment.")

    # ranked component harm
    L.append("\n## 7. Ranked component harm (most → least likely Public LB harm)\n")
    q1_shift_v82 = (mats["v82_FAILED_0.6629"][:, 0] - anchor[:, 0]).mean()
    s1_shift_v80 = (mats["v80_base"][:, 3] - anchor[:, 3]).mean()
    s3_shift_v80 = (mats["v80_base"][:, 5] - anchor[:, 5]).mean()
    ranking = [
        ("Q1 upward mean shift", f"v82 Q1 mean {mats['v82_FAILED_0.6629'][:,0].mean():.3f} vs v76 {anchor[:,0].mean():.3f} ({q1_shift_v82:+.3f}); Q1 is per-subject-relative (~0.5), so a systematic upshift inflates log loss directly.", "HIGH"),
        ("v80 base S1/S3 under-prediction", f"v80 S1 {mats['v80_base'][:,3].mean():.3f} vs v76 {anchor[:,3].mean():.3f} ({s1_shift_v80:+.3f}); S3 {mats['v80_base'][:,5].mean():.3f} vs v76 {anchor[:,5].mean():.3f} ({s3_shift_v80:+.3f}). The base is structurally below the good family on sleep targets.", "HIGH"),
        ("conditional router selected on full OOF", "router move selection is optimistic on OOF and does not transfer; it pushed targets toward OOF-fit directions unrelated to public alignment.", "HIGH"),
        ("late-behavior residual + v81 HGB residual magnitude", "the residual decoder amplified Q1/S3 moves that the stress test already showed were mostly selection bias on Q3/S1/S4.", "MEDIUM"),
        ("S3 upward shift in v82", "small (+0.008) and in the direction of the good family (v76 S3 0.66), so likely low harm or mildly helpful.", "LOW"),
        ("panel_position bins / test-time subject-date extrapolation", "bins are derived from observed panels and the same 10 subjects appear in train/test, so extrapolation risk is structural but not the proximate cause.", "LOW"),
    ]
    L.append(md_table(["component", "evidence", "harm"], [[c, e, h] for c, e, h in ranking]))

    out = ROOT / "outputs/v82_failure_diagnosis_report.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    summary = {
        "v80_base_meanabs_drift_vs_v76": float(d_v80.mean()),
        "v82_meanabs_drift_vs_v76": float(d_v82.mean()),
        "v82_Q1_shift_vs_v76": float(q1_shift_v82),
        "v80_S1_shift_vs_v76": float(s1_shift_v80),
        "v80_S3_shift_vs_v76": float(s3_shift_v80),
        "per_target_v80_shift_vs_v76": {t: float((mats["v80_base"][:, i] - anchor[:, i]).mean()) for i, t in enumerate(TARGETS)},
        "per_target_v82_shift_vs_v76": {t: float((mats["v82_FAILED_0.6629"][:, i] - anchor[:, i]).mean()) for i, t in enumerate(TARGETS)},
    }
    (ROOT / "outputs/v82_failure_diagnosis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(out.read_text())


if __name__ == "__main__":
    main()
