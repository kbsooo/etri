from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
ORDINAL = "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_sub(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def oof_name_from_submission(file_name: str) -> str | None:
    if file_name.startswith("submission_stage2_donor_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_publicobsblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_subjectgate_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_orthcap_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_orthcap") and "_exact_" in file_name:
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_label_prior_gate_orthcap"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_projblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public2dblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_publicgated_q3off650_presleep"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_anchor578_presleep"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_presleep_orthcap_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return None


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    obs = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)
    stage2_public = float(obs[STAGE2])
    ordinal_public = float(obs[ORDINAL])
    public_bad_gap = ordinal_public - stage2_public

    stage2_sub = load_sub(STAGE2)
    ordinal_sub = load_sub(ORDINAL)
    stage2_vec = stage2_sub[TARGETS].to_numpy(dtype=float).reshape(-1)
    ordinal_vec = ordinal_sub[TARGETS].to_numpy(dtype=float).reshape(-1)
    bad_dir = ordinal_vec - stage2_vec
    denom = float(np.dot(bad_dir, bad_dir))
    stage2_oof = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    stage2_loss = mean_loss(y, stage2_oof)

    catalog_paths = [
        OUT / "stage2_donor_targetmask_candidates.csv",
        OUT / "public_observed_pair_blend_candidates.csv",
        OUT / "subject_target_gate_donor_candidates.csv",
        OUT / "public_bad_direction_orthcap_candidates.csv",
        OUT / "exact_ordinal_prior_candidates.csv",
        OUT / "label_prior_exact_orthcap_candidates.csv",
        OUT / "projection_constrained_blend_candidates.csv",
        OUT / "public_two_axis_blend_candidates.csv",
        OUT / "presleep_multitarget_saved_candidates.csv",
        OUT / "presleep_anchor_saved_candidates.csv",
        OUT / "presleep_orthcap_candidates.csv",
    ]
    rows = []
    for path in catalog_paths:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for row in df.to_dict("records"):
            file_name = str(row["file"])
            sub_path = OUT / file_name
            oof_name = oof_name_from_submission(file_name)
            if not sub_path.exists() or oof_name is None or not (OUT / oof_name).exists():
                continue
            vals = load_sub(file_name)[TARGETS].to_numpy(dtype=float).reshape(-1)
            move = vals - stage2_vec
            projection = float(np.dot(move, bad_dir) / denom) if denom > 0 else 0.0
            projected = projection * bad_dir
            orth_norm = float(np.linalg.norm(move - projected))
            move_norm = float(np.linalg.norm(move))
            orth_ratio = orth_norm / max(move_norm, 1e-12)
            pred = clip(np.load(OUT / oof_name))
            loss = mean_loss(y, pred)
            linear_public_est = stage2_public + projection * public_bad_gap
            oof_gain = stage2_loss - loss
            rows.append(
                {
                    "file": file_name,
                    "source_catalog": path.name,
                    "oof_mean_loss": loss,
                    "oof_gain_vs_stage2": oof_gain,
                    "bad_direction_projection": projection,
                    "orthogonal_move_ratio": orth_ratio,
                    "linear_public_est_from_bad_direction": linear_public_est,
                    "linear_public_delta_vs_stage2": linear_public_est - stage2_public,
                    "oof_gain_per_1e4_public_risk": oof_gain / max((linear_public_est - stage2_public) * 1e4, 1e-12),
                    "distance_abs_mean_vs_anchor": float(row.get("distance_abs_mean_vs_anchor", np.nan)),
                    "targets_changed": row.get("targets_changed", ""),
                    "donor": row.get("donor", row.get("right", "")),
                    "mask": row.get("mask", row.get("target_set", "")),
                    "weight": row.get("weight", row.get("right_weight", np.nan)),
                    "half_gate_oof_loss": row.get("half_gate_oof_loss", np.nan),
                    "half_gate_oof_delta": row.get("half_gate_oof_delta", np.nan),
                    "active_subject_targets": row.get("active_subject_targets", np.nan),
                    "source_file": row.get("source_file", ""),
                    "projection_cap": row.get("projection_cap", np.nan),
                    "scale": row.get("scale", np.nan),
                }
            )

    out = pd.DataFrame(rows)
    out = out[out["oof_gain_vs_stage2"] > 0].copy()
    out["priority_score"] = (
        out["oof_mean_loss"]
        + 3.0 * np.maximum(out["linear_public_delta_vs_stage2"], 0.0)
        + 0.001 * np.maximum(out["bad_direction_projection"], 0.0)
        - 0.0002 * out["orthogonal_move_ratio"]
    )
    out = out.sort_values(
        ["priority_score", "linear_public_delta_vs_stage2", "oof_mean_loss"],
        ascending=[True, True, True],
    ).reset_index(drop=True)
    out.to_csv(OUT / "public_direction_risk_ranked_candidates.csv", index=False)
    print(out.head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
