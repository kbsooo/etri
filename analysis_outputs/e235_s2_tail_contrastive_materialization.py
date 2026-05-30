#!/usr/bin/env python3
"""E235: materialize E234 S2 tail-contrastive risk drops.

E234 showed that a high-impact tail target, not the old support label, can
improve E216 S2 OOF movement. This script asks the submission-side question:

Can the E234 S2 tail-risk rows be dropped from the failed E216 S2 translator
while passing the E221 public-free tail-capacity gate?

Only E95-anchor S2 grafts are considered because E221 already showed E95-anchor
is the cleaner rescue frame for the failed E216 S2 lane. No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e221_s2_oof_support_classifier as e221  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402
import e234_tail_contrastive_jepa_target as e234  # noqa: E402


S2_IDX = TARGETS.index("S2")
E95_FILE = "submission_e95_hardtail_541e3973.csv"

SCAN_OUT = OUT / "e235_s2_tail_contrastive_materialization_scan.csv"
SELECTED_OUT = OUT / "e235_s2_tail_contrastive_materialization_selected.csv"
REPORT_OUT = OUT / "e235_s2_tail_contrastive_materialization_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def materialize(
    sample: pd.DataFrame,
    base_e95: np.ndarray,
    stage2_sub: np.ndarray,
    full_sub: np.ndarray,
    mask: np.ndarray,
    tag: str,
    scale: float,
) -> str:
    candidate = base_e95.copy()
    dz = logit(full_sub[:, S2_IDX]) - logit(stage2_sub[:, S2_IDX])
    idx = np.where(mask)[0]
    if len(idx):
        candidate[idx, S2_IDX] = sigmoid(logit(base_e95[idx, S2_IDX]) + scale * dz[idx])
    digest = hashlib.sha1(np.round(candidate, 10).tobytes()).hexdigest()[:8]
    scale_tag = str(scale).replace(".", "p")
    file_name = f"submission_e235_s2tail_{tag[:42]}_s{scale_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(candidate)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def e234_s2_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_raw, train_long, sub_long, _ = e232.build_long_frames()
    train_long = e234.add_true_labels(train_long, train_raw)
    feats = e232.feature_sets(train_long)
    feats = {name: [c for c in cols if c != "true_label"] for name, cols in feats.items()}
    tr = train_long[train_long["task_name"].eq("s2_e216")].reset_index(drop=True)
    te = sub_long[sub_long["task_name"].eq("s2_e216")].reset_index(drop=True)
    return tr, te, feats


def candidate_specs() -> pd.DataFrame:
    if not e234.SELECTED_OUT.exists():
        e234.run()
    selected = pd.read_csv(e234.SELECTED_OUT)
    s2 = selected[
        selected["task"].eq("s2_e216")
        & selected["stress_promote"].astype(bool)
        & selected["policy"].astype(str).str.startswith("drop")
    ].copy()
    if s2.empty:
        return s2
    s2 = s2.sort_values(["loss_vs_full", "tail_auc"], ascending=[True, False])
    return s2.head(80).reset_index(drop=True)


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    specs = candidate_specs()
    train_df, sub_df, feats = e234_s2_frames()
    models = e234.model_defs()

    (
        _train_raw,
        _sub_raw,
        _train_feat,
        _sub_feat,
        _stage2_oof,
        _full_oof,
        stage2_sub,
        full_sub,
        sample,
    ) = e221.make_e216_tensors()
    base_e95 = clip_prob(load_sub(E95_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    priors = e162.prior_arrays(sample)

    rows: list[dict[str, Any]] = []
    for i, spec in specs.iterrows():
        cols = feats[str(spec["view"])]
        prob = e234.fit_full_tail_predict(
            models[str(spec["model"])],
            train_df,
            sub_df,
            cols,
            str(spec["target_kind"]),
            float(spec["tail_q"]),
        )
        amp = e234.amplitude_policies(str(spec["target_kind"]), prob)[str(spec["policy"])]
        mask = np.asarray(amp, dtype=np.float64) >= 0.50
        tag = (
            f"e234_{int(i):02d}_{spec['target_kind']}_{spec['policy']}_"
            f"{spec['model']}_{spec['split']}"
        ).replace(".", "p")
        for scale in [0.35, 0.50, 0.75]:
            rec = e221.submission_metrics(
                model_split=f"{spec['model']}__{spec['split']}__{spec['target_kind']}{float(spec['tail_q']):.2f}",
                gate=str(spec["policy"]),
                mask=mask,
                sample=sample,
                base_e95=base_e95,
                stage2_sub=stage2_sub,
                full_sub=full_sub,
                priors=priors,
                scale=scale,
            )
            rec.update(
                {
                    "spec_rank": int(i),
                    "view": spec["view"],
                    "model": spec["model"],
                    "split": spec["split"],
                    "target_kind": spec["target_kind"],
                    "tail_q": float(spec["tail_q"]),
                    "policy": spec["policy"],
                    "e234_tail_auc": float(spec["tail_auc"]),
                    "e234_loss_vs_full": float(spec["loss_vs_full"]),
                    "e234_target_delta": float(spec["target_delta"]),
                    "e234_subject_win_rate": float(spec["subject_win_rate"]),
                    "sub_dropped_rows": int(np.sum(~mask)),
                    "sub_kept_rows": int(np.sum(mask)),
                    "sub_mean_prob": float(np.mean(prob)),
                    "sub_p10_prob": float(np.quantile(prob, 0.10)),
                    "sub_p50_prob": float(np.quantile(prob, 0.50)),
                    "sub_p90_prob": float(np.quantile(prob, 0.90)),
                    "tag": tag,
                }
            )
            rec["joint_gate_pass"] = bool(
                rec["submission_gate_pass"]
                and rec["e234_loss_vs_full"] < -2.5e-4
                and rec["e234_subject_win_rate"] >= 0.70
                and rec["sub_dropped_rows"] >= 10
            )
            rec["joint_score"] = (
                rec["submission_score"]
                - min(rec["e234_loss_vs_full"], 0.0) * 0.50
                + max(rec["e234_subject_win_rate"] - 0.60, 0.0) * 0.0002
                - max(20 - rec["sub_dropped_rows"], 0) * 1.0e-6
            )
            rows.append(rec)
    scan = pd.DataFrame(rows)
    if scan.empty:
        selected = scan.copy()
    else:
        selected = scan[scan["joint_gate_pass"]].sort_values(
            ["joint_score", "expected_focus", "adverse_delta"],
            ascending=[False, True, True],
        ).head(4).copy()
        files: list[str] = []
        for row in selected.itertuples(index=False):
            spec = specs.iloc[int(row.spec_rank)]
            cols = feats[str(spec["view"])]
            prob = e234.fit_full_tail_predict(
                models[str(spec["model"])],
                train_df,
                sub_df,
                cols,
                str(spec["target_kind"]),
                float(spec["tail_q"]),
            )
            amp = e234.amplitude_policies(str(spec["target_kind"]), prob)[str(spec["policy"])]
            mask = np.asarray(amp, dtype=np.float64) >= 0.50
            files.append(materialize(sample, base_e95, stage2_sub, full_sub, mask, str(row.tag), float(row.scale)))
        if not selected.empty:
            selected["submission_file"] = files
            scan = scan.merge(selected[["tag", "scale", "submission_file"]], on=["tag", "scale"], how="left")
        else:
            scan["submission_file"] = ""
            selected["submission_file"] = ""

    scan.to_csv(SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(scan, selected)
    return scan, selected


def write_report(scan: pd.DataFrame, selected: pd.DataFrame) -> None:
    top = scan.sort_values(["joint_gate_pass", "joint_score"], ascending=[False, False]).head(40) if not scan.empty else scan
    lines = [
        "# E235 S2 Tail-Contrastive Materialization",
        "",
        "## Question",
        "",
        "Can E234's S2 tail-risk target rescue the failed E216 S2 translator on submission-side public-free tail stress?",
        "",
        "## Observed Read",
        "",
        f"- scanned rows: `{len(scan)}`.",
        f"- joint gate pass rows: `{int(scan['joint_gate_pass'].sum()) if not scan.empty else 0}`.",
        f"- materialized files: `{len(selected)}`.",
        "",
        "A pass must preserve the E234 OOF tail gain and pass the E221 submission-side tail-capacity gate: negative expected focus, adverse capacity below the observed E216 miss, support probability above `0.5`, and no single-cell dominance.",
        "",
        "## Selected",
        "",
        md_table(
            selected,
            [
                "model_split",
                "gate",
                "scale",
                "selected_rows_sub",
                "sub_dropped_rows",
                "expected_focus",
                "adverse_delta",
                "adverse_over_observed_miss",
                "support_prob_focus_weighted",
                "top1_swing_share",
                "e234_loss_vs_full",
                "e234_tail_auc",
                "joint_gate_pass",
                "joint_score",
                "submission_file",
            ],
            n=20,
        ),
        "",
        "## Top Scan Rows",
        "",
        md_table(
            top,
            [
                "model_split",
                "gate",
                "scale",
                "selected_rows_sub",
                "sub_dropped_rows",
                "expected_focus",
                "adverse_delta",
                "adverse_over_observed_miss",
                "support_prob_focus_weighted",
                "top1_swing_share",
                "e234_loss_vs_full",
                "e234_tail_auc",
                "submission_gate_pass",
                "joint_gate_pass",
                "joint_score",
                "submission_file",
            ],
            n=40,
        ),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.extend(
            [
                "- E234's S2 tail-risk target improves OOF but still does not survive submission-side tail stress.",
                "- Keep E216 S2 closed as a public lane.",
            ]
        )
    else:
        best = selected.iloc[0]
        lines.extend(
            [
                f"- Best materialized file: `{best['submission_file']}`.",
                "- This is not the old E216 support gate. It is a different JEPA target: drop high-adverse S2 tail rows learned from contrastive/risk OOF tails, then apply the remaining S2 movement on the E95 anchor.",
                "- Public interpretation: a win says E216 failed because its target representation was right but its tail-loss was wrong; a loss says even tail-contrastive S2 risk does not transfer to the hidden public subset.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan, selected = run()
    print("[E235 selected]")
    cols = [
        "model_split",
        "gate",
        "scale",
        "selected_rows_sub",
        "sub_dropped_rows",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_weighted",
        "top1_swing_share",
        "e234_loss_vs_full",
        "joint_gate_pass",
        "submission_file",
    ]
    print(selected[cols].to_string(index=False) if not selected.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
