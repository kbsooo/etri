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
EPS = 1e-5

BASE = {
    "file": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "oof": "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
}

DONORS = {
    "ordinal": {
        "file": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "oof": "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy",
    },
    "ambnext": {
        "file": "submission_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext.csv",
        "oof": "final_publicgated_q3off650_presleep_core_prectx_s2wlight_s3light_q3hr_ble_ambnext_oof.npy",
    },
    "blend500": {
        "file": "submission_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw500.csv",
        "oof": "final_presleepblend_prectx_s2wlight_s3light_q3hrble_ambnext_q3offw500_oof.npy",
    },
}

TARGET_SETS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "q3": ["Q3"],
    "s": ["S1", "S2", "S3", "S4"],
    "s1_s3_s4": ["S1", "S3", "S4"],
    "q1_q3_s2_s4": ["Q1", "Q3", "S2", "S4"],
}

THRESHOLDS = [0.0, -0.0025, -0.005, -0.01, -0.02]
WEIGHTS = [0.35, 0.50, 0.65, 0.80, 1.00]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(float)
    pp = clip(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    return float(loss_vec(y, p).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def full_gate(train: pd.DataFrame, y: np.ndarray, base: np.ndarray, donor: np.ndarray, target_names: list[str], threshold: float) -> dict[tuple[str, str], bool]:
    gate: dict[tuple[str, str], bool] = {}
    for sid, group in train.groupby("subject_id", sort=False):
        idx = group.index.to_numpy()
        for target in target_names:
            j = TARGETS.index(target)
            delta = loss_col(y[idx, j], donor[idx, j]) - loss_col(y[idx, j], base[idx, j])
            gate[(str(sid), target)] = delta <= threshold
    return gate


def apply_gate_to_pred(rows: pd.DataFrame, base: np.ndarray, donor: np.ndarray, gate: dict[tuple[str, str], bool], target_names: list[str], weight: float) -> np.ndarray:
    pred = base.copy()
    for sid, group in rows.groupby("subject_id", sort=False):
        idx = group.index.to_numpy()
        for target in target_names:
            if not gate.get((str(sid), target), False):
                continue
            j = TARGETS.index(target)
            pred[idx, j] = clip((1.0 - weight) * base[idx, j] + weight * donor[idx, j])
    return clip(pred)


def half_gate_oof(train: pd.DataFrame, y: np.ndarray, base: np.ndarray, donor: np.ndarray, target_names: list[str], threshold: float, weight: float) -> np.ndarray:
    pred = base.copy()
    for sid, group in train.groupby("subject_id", sort=False):
        idx = group.index.to_numpy()
        if len(idx) < 4:
            continue
        halves = [idx[: len(idx) // 2], idx[len(idx) // 2 :]]
        for target in target_names:
            j = TARGETS.index(target)
            for source_half, target_half in [(halves[0], halves[1]), (halves[1], halves[0])]:
                delta = loss_col(y[source_half, j], donor[source_half, j]) - loss_col(y[source_half, j], base[source_half, j])
                if delta <= threshold:
                    pred[target_half, j] = clip((1.0 - weight) * base[target_half, j] + weight * donor[target_half, j])
    return clip(pred)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    base_sub = load_sub(BASE["file"])
    assert base_sub[KEY].equals(sample[KEY])
    base_oof = clip(np.load(OUT / BASE["oof"]))
    base_loss = mean_loss(y, base_oof)
    base_vals = base_sub[TARGETS].to_numpy(dtype=float)
    anchor_vals = load_sub("submission_hybrid_0p578_logit_after_subject_final9_strict.csv")[TARGETS].to_numpy(dtype=float)

    rows = []
    gate_details = []
    for donor_name, donor_info in DONORS.items():
        donor_sub = load_sub(donor_info["file"])
        assert donor_sub[KEY].equals(sample[KEY])
        donor_oof = clip(np.load(OUT / donor_info["oof"]))
        donor_vals = donor_sub[TARGETS].to_numpy(dtype=float)
        for set_name, target_names in TARGET_SETS.items():
            for threshold in THRESHOLDS:
                gate = full_gate(train, y, base_oof, donor_oof, target_names, threshold)
                active = sum(gate.values())
                for weight in WEIGHTS:
                    full_pred = apply_gate_to_pred(train, base_oof, donor_oof, gate, target_names, weight)
                    half_pred = half_gate_oof(train, y, base_oof, donor_oof, target_names, threshold, weight)
                    vals = apply_gate_to_pred(sample, base_vals, donor_vals, gate, target_names, weight)
                    suffix = f"{donor_name}_{set_name}_thr{str(threshold).replace('-', 'm').replace('.', 'p')}_w{int(round(weight * 100)):03d}"
                    file_name = f"submission_subjectgate_{suffix}.csv"
                    out = base_sub.copy()
                    out[TARGETS] = vals
                    out.to_csv(OUT / file_name, index=False)
                    np.save(OUT / f"final_subjectgate_{suffix}_oof.npy", full_pred)
                    dist = np.abs(vals - anchor_vals)
                    rows.append(
                        {
                            "file": file_name,
                            "donor": donor_name,
                            "target_set": set_name,
                            "targets": ",".join(target_names),
                            "threshold": threshold,
                            "weight": weight,
                            "active_subject_targets": active,
                            "full_gate_oof_loss": mean_loss(y, full_pred),
                            "full_gate_oof_delta": mean_loss(y, full_pred) - base_loss,
                            "half_gate_oof_loss": mean_loss(y, half_pred),
                            "half_gate_oof_delta": mean_loss(y, half_pred) - base_loss,
                            "distance_abs_mean_vs_anchor": float(dist.mean()),
                            "distance_abs_p90_vs_anchor": float(np.quantile(dist, 0.9)),
                            "submission_min": float(vals.min()),
                            "submission_max": float(vals.max()),
                        }
                    )
                for (sid, target), is_active in gate.items():
                    if is_active:
                        gate_details.append({"donor": donor_name, "target_set": set_name, "threshold": threshold, "subject_id": sid, "target": target})

    catalog = pd.DataFrame(rows).sort_values(["half_gate_oof_loss", "full_gate_oof_loss", "distance_abs_mean_vs_anchor"]).reset_index(drop=True)
    catalog.to_csv(OUT / "subject_target_gate_donor_candidates.csv", index=False)
    pd.DataFrame(gate_details).drop_duplicates().to_csv(OUT / "subject_target_gate_donor_active_details.csv", index=False)
    print(catalog.head(50).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
