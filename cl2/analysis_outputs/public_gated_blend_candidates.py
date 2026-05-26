from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_submission(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def apply_targets(base: np.ndarray, source: np.ndarray, targets: list[str]) -> np.ndarray:
    out = base.copy()
    for target in targets:
        j = TARGETS.index(target)
        out[:, j] = source[:, j]
    return clip(out)


def candidate_target_sets() -> dict[str, list[str]]:
    return {
        "stage2_full": ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"],
        "stage2_drop_q3": ["Q1", "Q2", "S1", "S2", "S3", "S4"],
        "stage2_drop_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
        "stage2_no_q2q3": ["Q1", "S1", "S2", "S3", "S4"],
        "stage2_s_only": ["S1", "S2", "S3", "S4"],
        "stage2_q1_s_only": ["Q1", "S1", "S2", "S3", "S4"],
        "stage2_q1_s3_s4": ["Q1", "S3", "S4"],
        "stage2_s3_s4": ["S3", "S4"],
        "stage2_s1_s4": ["S1", "S4"],
    }


def geometry_delta_map() -> dict[str, float]:
    path = OUT / "broad_nested_selection_bias_audit_r8_top10_fixed_stage2_summary.csv"
    if not path.exists():
        return {t: 0.0 for t in TARGETS}
    df = pd.read_csv(path)
    out = {t: 0.0 for t in TARGETS}
    for row in df.itertuples(index=False):
        out[str(row.target)] = float(row.holdout_delta_mean)
    return out


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    anchor = read_submission("submission_hybrid_0p578_logit_after_subject_final9_strict.csv")
    stage2 = read_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    assert anchor[KEY].equals(sample[KEY])
    assert stage2[KEY].equals(sample[KEY])

    anchor_pred = anchor[TARGETS].to_numpy(dtype=float)
    stage2_pred = stage2[TARGETS].to_numpy(dtype=float)
    anchor_oof = clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    stage2_oof = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    gdelta = geometry_delta_map()

    weights = [0.35, 0.50, 0.545, 0.65, 0.75, 0.85, 1.00]
    rows = []
    for name, targets in candidate_target_sets().items():
        source_pred = apply_targets(anchor_pred, stage2_pred, targets)
        source_oof = apply_targets(anchor_oof, stage2_oof, targets)
        source_delta = mean_loss(y, source_oof) - mean_loss(y, anchor_oof)
        source_geom_delta = sum(gdelta.get(t, 0.0) for t in targets) / len(TARGETS)
        for w in weights:
            sub_pred = clip((1.0 - w) * anchor_pred + w * source_pred)
            oof_pred = clip((1.0 - w) * anchor_oof + w * source_oof)
            out = anchor.copy()
            out[TARGETS] = sub_pred
            pct = int(round(w * 1000))
            file_name = f"submission_publicgated_anchor578_{name}_prob_w{pct:03d}.csv"
            out.to_csv(OUT / file_name, index=False)
            row = {
                "file": file_name,
                "source": name,
                "targets_changed": ",".join(targets),
                "weight": float(w),
                "oof_mean_loss": mean_loss(y, oof_pred),
                "oof_delta_vs_anchor": mean_loss(y, oof_pred) - mean_loss(y, anchor_oof),
                "source_oof_delta_vs_anchor": float(source_delta),
                "geometry_delta_proxy": float(w * source_geom_delta),
                "distance_abs_mean_vs_anchor": float(np.abs(sub_pred - anchor_pred).mean()),
                "distance_abs_p90_vs_anchor": float(np.quantile(np.abs(sub_pred - anchor_pred), 0.90)),
                "submission_min": float(sub_pred.min()),
                "submission_max": float(sub_pred.max()),
            }
            for j, target in enumerate(TARGETS):
                row[f"{target}_oof_loss"] = loss_col(y[:, j], oof_pred[:, j])
                row[f"{target}_mean"] = float(sub_pred[:, j].mean())
                row[f"{target}_abs_delta_mean_vs_anchor"] = float(np.abs(sub_pred[:, j] - anchor_pred[:, j]).mean())
            rows.append(row)

    summary = pd.DataFrame(rows).sort_values(["geometry_delta_proxy", "oof_mean_loss", "distance_abs_mean_vs_anchor"])
    summary.to_csv(OUT / "public_gated_blend_candidates.csv", index=False)
    display = [
        "source",
        "targets_changed",
        "weight",
        "oof_mean_loss",
        "oof_delta_vs_anchor",
        "geometry_delta_proxy",
        "distance_abs_mean_vs_anchor",
        "submission_min",
        "submission_max",
        "file",
    ]
    print(summary[display].head(40).round(8).to_string(index=False))


if __name__ == "__main__":
    main()
