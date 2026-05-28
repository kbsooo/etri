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
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_submission(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def apply_targets(base: pd.DataFrame, source: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    out = base.copy()
    out[targets] = source[targets].to_numpy(dtype=float)
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out


def apply_targets_oof(base: np.ndarray, source: np.ndarray, targets: list[str]) -> np.ndarray:
    out = base.copy()
    for target in targets:
        j = TARGETS.index(target)
        out[:, j] = source[:, j]
    return clip(out)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    anchor = read_submission("submission_hybrid_0p578_logit_after_subject_final9_strict.csv")
    stage2 = read_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    broad_q1q2 = read_submission("submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv")
    assert anchor[KEY].equals(sample[KEY])
    assert stage2[KEY].equals(sample[KEY])
    assert broad_q1q2[KEY].equals(sample[KEY])

    anchor_oof = clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    stage2_oof = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    broad_q1q2_oof = clip(np.load(OUT / "final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy"))

    candidates: dict[str, tuple[pd.DataFrame, np.ndarray, list[str], str]] = {}
    for target in TARGETS:
        candidates[f"stage2only_{target.lower()}"] = (
            apply_targets(anchor, stage2, [target]),
            apply_targets_oof(anchor_oof, stage2_oof, [target]),
            [target],
            "anchor with only this target copied from full stage2",
        )
    grouped = {
        "stage2only_q": ["Q1", "Q2", "Q3"],
        "stage2only_s": ["S1", "S2", "S3", "S4"],
        "stage2only_q1q2": ["Q1", "Q2"],
        "stage2only_q3s1s4": ["Q3", "S1", "S4"],
        "stage2only_s1s4": ["S1", "S4"],
        "stage2only_s2s3": ["S2", "S3"],
        "stage2_stable_no_q3": ["Q1", "Q2", "S1", "S2", "S3", "S4"],
        "stage2_geo_stable_no_q2q3": ["Q1", "S1", "S2", "S3", "S4"],
        "stage2_geo_top_q1s3s4": ["Q1", "S3", "S4"],
        "stage2_geo_top_s3s4": ["S3", "S4"],
    }
    for drop_target in TARGETS:
        grouped[f"stage2_drop_{drop_target.lower()}"] = [t for t in TARGETS if t != drop_target]
    for name, targets in grouped.items():
        candidates[name] = (
            apply_targets(anchor, stage2, targets),
            apply_targets_oof(anchor_oof, stage2_oof, targets),
            targets,
            "anchor with selected targets copied from full stage2",
        )

    for target in ["Q1", "Q2"]:
        candidates[f"broadq1q2only_{target.lower()}"] = (
            apply_targets(anchor, broad_q1q2, [target]),
            apply_targets_oof(anchor_oof, broad_q1q2_oof, [target]),
            [target],
            "anchor with one target copied from the Q1/Q2 broad file",
        )
    candidates["broadq1q2only_q1q2"] = (
        apply_targets(anchor, broad_q1q2, ["Q1", "Q2"]),
        apply_targets_oof(anchor_oof, broad_q1q2_oof, ["Q1", "Q2"]),
        ["Q1", "Q2"],
        "anchor with Q1/Q2 copied from the Q1/Q2 broad file",
    )

    rows = []
    anchor_mat = anchor[TARGETS].to_numpy(dtype=float)
    for name, (df, oof, targets, note) in candidates.items():
        file_name = f"submission_publicprobe_anchor578_{name}.csv"
        df.to_csv(OUT / file_name, index=False)
        mat = df[TARGETS].to_numpy(dtype=float)
        row = {
            "file": file_name,
            "probe": name,
            "targets_changed": ",".join(targets),
            "note": note,
            "oof_mean_loss": mean_loss(y, oof),
            "oof_delta_vs_anchor": mean_loss(y, oof) - mean_loss(y, anchor_oof),
            "distance_abs_mean_vs_anchor": float(np.abs(mat - anchor_mat).mean()),
            "distance_abs_p90_vs_anchor": float(np.quantile(np.abs(mat - anchor_mat), 0.90)),
            "submission_min": float(mat.min()),
            "submission_max": float(mat.max()),
        }
        for target in TARGETS:
            j = TARGETS.index(target)
            row[f"{target}_oof_loss"] = loss_col(y[:, j], oof[:, j])
            row[f"{target}_mean"] = float(mat[:, j].mean())
            row[f"{target}_abs_delta_mean_vs_anchor"] = float(np.abs(mat[:, j] - anchor_mat[:, j]).mean())
        rows.append(row)

    summary = pd.DataFrame(rows).sort_values(["oof_mean_loss", "distance_abs_mean_vs_anchor"])
    summary.to_csv(OUT / "public_target_switch_probes.csv", index=False)
    display_cols = [
        "probe",
        "targets_changed",
        "oof_mean_loss",
        "oof_delta_vs_anchor",
        "distance_abs_mean_vs_anchor",
        "distance_abs_p90_vs_anchor",
        "submission_min",
        "submission_max",
    ]
    print(summary[display_cols].round(8).to_string(index=False))


if __name__ == "__main__":
    main()
