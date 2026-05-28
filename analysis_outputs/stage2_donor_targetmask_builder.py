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

BASE = {
    "file": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "oof": "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
}

DONORS = {
    "ambnext": {
        "file": "submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv",
        "oof": "final_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext_oof.npy",
    },
    "ordinal": {
        "file": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "oof": "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy",
    },
    "blend500": {
        "file": "submission_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw500.csv",
        "oof": "final_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw500_oof.npy",
    },
}

MASKS = {
    "q3": ["Q3"],
    "s": ["S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "publicsign_q1_q3_s2_s4": ["Q1", "Q3", "S2", "S4"],
    "q3_s2_s4": ["Q3", "S2", "S4"],
    "s1_s3_s4": ["S1", "S3", "S4"],
    "q1_q3": ["Q1", "Q3"],
    "all": TARGETS,
}

WEIGHTS = [0.05, 0.10, 0.15, 0.20, 0.35, 0.50, 0.65, 0.80, 1.00]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)

    base_sub = load_sub(BASE["file"])
    assert base_sub[KEY].equals(sample[KEY])
    base_pred = clip(np.load(OUT / BASE["oof"]))
    base_vals = base_sub[TARGETS].to_numpy(dtype=float)
    anchor_vals = load_sub("submission_hybrid_0p578_logit_after_subject_final9_strict.csv")[TARGETS].to_numpy(dtype=float)
    base_loss = mean_loss(y, base_pred)

    rows = []
    for donor_name, donor in DONORS.items():
        donor_sub = load_sub(donor["file"])
        assert donor_sub[KEY].equals(sample[KEY]), donor_name
        donor_pred = clip(np.load(OUT / donor["oof"]))
        donor_vals = donor_sub[TARGETS].to_numpy(dtype=float)
        for mask_name, mask_targets in MASKS.items():
            idx = [TARGETS.index(t) for t in mask_targets]
            for weight in WEIGHTS:
                vals = base_vals.copy()
                pred = base_pred.copy()
                vals[:, idx] = clip((1.0 - weight) * base_vals[:, idx] + weight * donor_vals[:, idx])
                pred[:, idx] = clip((1.0 - weight) * base_pred[:, idx] + weight * donor_pred[:, idx])
                out = base_sub.copy()
                out[TARGETS] = vals
                suffix = f"{donor_name}_{mask_name}_w{int(round(weight * 100)):03d}"
                file_name = f"submission_stage2_donor_{suffix}.csv"
                out.to_csv(OUT / file_name, index=False)
                np.save(OUT / f"final_stage2_donor_{suffix}_oof.npy", pred)
                target_losses = {f"{target}_loss": loss_col(y[:, j], pred[:, j]) for j, target in enumerate(TARGETS)}
                target_deltas = {f"{target}_delta_vs_stage2": target_losses[f"{target}_loss"] - loss_col(y[:, j], base_pred[:, j]) for j, target in enumerate(TARGETS)}
                dist = np.abs(vals - anchor_vals)
                rows.append(
                    {
                        "file": file_name,
                        "donor": donor_name,
                        "mask": mask_name,
                        "targets_changed": ",".join(mask_targets),
                        "weight": weight,
                        "oof_mean_loss": mean_loss(y, pred),
                        "oof_delta_vs_stage2": mean_loss(y, pred) - base_loss,
                        "distance_abs_mean_vs_anchor": float(dist.mean()),
                        "distance_abs_p90_vs_anchor": float(np.quantile(dist, 0.9)),
                        "submission_min": float(vals.min()),
                        "submission_max": float(vals.max()),
                        **target_deltas,
                    }
                )

    catalog = pd.DataFrame(rows).sort_values(
        ["oof_mean_loss", "distance_abs_mean_vs_anchor", "weight"],
        ascending=[True, True, True],
    )
    catalog.to_csv(OUT / "stage2_donor_targetmask_candidates.csv", index=False)
    print(catalog.head(40).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
