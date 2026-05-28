from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import jepa_axis_stack_candidates as stack  # noqa: E402
import block_canvas_multifeature_probe as multi  # noqa: E402


def safe_label(x: float) -> str:
    return str(x).replace("-", "m").replace(".", "p")


def main() -> None:
    train, _sub, base, base_sub = adv.read_data()
    y = train[TARGETS].to_numpy(dtype=int)
    base_loss = adv.mean_loss(y, base)
    base_sub_arr = base_sub[TARGETS].to_numpy(dtype=float)
    raw_train = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_train_features.parquet")
    raw_sub = pd.read_parquet(OUT / "raw_timeline_jepa_rescue_submission_features.parquet")
    raw_oof, raw_sub_pred = stack.candidate_from_ops(
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        raw_train,
        raw_sub,
        base,
        base_sub,
    )
    raw_oof_move = adv.logit(raw_oof) - adv.logit(base)
    raw_sub_move = adv.logit(raw_sub_pred) - adv.logit(base_sub_arr)

    train_feat = pd.read_parquet(OUT / "block_canvas_jepa_train_features.parquet")
    sub_feat = pd.read_parquet(OUT / "block_canvas_jepa_submission_features.parquet")
    scan = pd.read_csv(OUT / "block_canvas_jepa_scan.csv")
    specs = [
        (8, 0.02, True),
        (8, 0.05, True),
        (5, 0.02, True),
        (3, 0.02, True),
    ]
    rows = []
    base_logit = adv.logit(base)
    sub_base_logit = adv.logit(base_sub_arr)
    for k, c_value, no_q2 in specs:
        feature_sets = multi.choose_feature_sets(scan, k)
        mf_oof, mf_sub, details = multi.build_variant(
            train_feat,
            sub_feat,
            base,
            base_sub_arr,
            feature_sets,
            c_value,
            no_q2=no_q2,
        )
        mf_oof_move = adv.logit(mf_oof) - base_logit
        mf_sub_move = adv.logit(mf_sub) - sub_base_logit
        for raw_weight in [0.35, 0.5, 0.75, 1.0]:
            for mf_weight in [0.35, 0.5, 0.75, 1.0]:
                oof = adv.clip(1.0 / (1.0 + np.exp(-(base_logit + raw_weight * raw_oof_move + mf_weight * mf_oof_move))))
                sub = adv.clip(1.0 / (1.0 + np.exp(-(sub_base_logit + raw_weight * raw_sub_move + mf_weight * mf_sub_move))))
                stats = multi.axis_stats(sub, base_sub)
                name = (
                    "submission_jepa_multifeature_rawstack_"
                    f"k{k}_c{safe_label(c_value)}_{'noq2' if no_q2 else 'all'}_"
                    f"rw{safe_label(raw_weight)}_mw{safe_label(mf_weight)}.csv"
                )
                out = base_sub.copy()
                out[TARGETS] = sub
                out.to_csv(OUT / name, index=False)
                rows.append(
                    {
                        "candidate": name,
                        "k": k,
                        "c_value": c_value,
                        "no_q2": no_q2,
                        "raw_weight": raw_weight,
                        "mf_weight": mf_weight,
                        "oof_loss": adv.mean_loss(y, oof),
                        "oof_delta_vs_stage2": adv.mean_loss(y, oof) - base_loss,
                        **stats,
                    }
                )
    summary = pd.DataFrame(rows)
    summary["public_safety_rank"] = (
        summary["oof_delta_vs_stage2"]
        + 0.006 * np.maximum(summary["jepa_bad_ratio"], 0.0)
        + 0.0015 * np.maximum(-summary["raw_good_ratio"], 0.0)
        - 0.0005 * np.minimum(summary["raw_good_ratio"], 0.8)
    )
    summary = summary.sort_values(["public_safety_rank", "oof_delta_vs_stage2"]).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_multifeature_rawstack_summary.csv", index=False)
    report = [
        "# Multi-Feature Raw-Anchor Stack",
        "",
        "Combines the stronger Block-Canvas multi-feature residual with the only public-positive raw-rescue direction. The aim is to retain the OOF gain while pulling submission geometry back toward the known good axis.",
        "",
        summary.head(80).to_csv(index=False),
    ]
    (OUT / "jepa_multifeature_rawstack_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(30).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
