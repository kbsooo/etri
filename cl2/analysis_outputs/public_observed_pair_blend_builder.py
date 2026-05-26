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


OBSERVED = {
    "anchor578": {
        "file": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "oof": "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy",
    },
    "stage2": {
        "file": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "oof": "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
    },
    "ordinal": {
        "file": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "oof": "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy",
    },
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_submission(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / OBSERVED[name]["file"], parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def load_oof(name: str) -> np.ndarray:
    return clip(np.load(OUT / OBSERVED[name]["oof"]))


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    y = train[TARGETS].to_numpy(dtype=int)
    public = pd.read_csv(OUT / "public_probe_observations.csv").set_index("file")["public_lb"].astype(float)

    subs = {name: load_submission(name) for name in OBSERVED}
    oofs = {name: load_oof(name) for name in OBSERVED}
    for name, sub in subs.items():
        assert sub[KEY].equals(sample[KEY]), name
        assert oofs[name].shape == (len(train), len(TARGETS)), name

    anchor = subs["anchor578"][TARGETS].to_numpy(dtype=float)
    rows = []
    weights = [0.05, 0.10, 0.15, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90, 0.95]
    pairs = [("stage2", "ordinal"), ("anchor578", "stage2"), ("anchor578", "ordinal")]
    for left, right in pairs:
        left_public = float(public[OBSERVED[left]["file"]])
        right_public = float(public[OBSERVED[right]["file"]])
        for w_right in weights:
            vals = clip((1.0 - w_right) * subs[left][TARGETS].to_numpy(dtype=float) + w_right * subs[right][TARGETS].to_numpy(dtype=float))
            oof = clip((1.0 - w_right) * oofs[left] + w_right * oofs[right])
            out = subs[left].copy()
            out[TARGETS] = vals
            suffix = f"{left}_to_{right}_w{int(round(w_right * 100)):03d}"
            file_name = f"submission_publicobsblend_{suffix}.csv"
            out.to_csv(OUT / file_name, index=False)
            np.save(OUT / f"final_publicobsblend_{suffix}_oof.npy", oof)
            dist = np.abs(vals - anchor)
            rows.append(
                {
                    "file": file_name,
                    "left": left,
                    "right": right,
                    "right_weight": w_right,
                    "oof_mean_loss": mean_loss(y, oof),
                    "public_convex_upper_bound": (1.0 - w_right) * left_public + w_right * right_public,
                    "public_bound_vs_stage2": (1.0 - w_right) * left_public + w_right * right_public - float(public[OBSERVED["stage2"]["file"]]),
                    "distance_abs_mean_vs_anchor": float(dist.mean()),
                    "distance_abs_p90_vs_anchor": float(np.quantile(dist, 0.9)),
                    "submission_min": float(vals.min()),
                    "submission_max": float(vals.max()),
                }
            )

    catalog = pd.DataFrame(rows).sort_values(
        ["public_convex_upper_bound", "oof_mean_loss", "distance_abs_mean_vs_anchor"],
        ascending=[True, True, True],
    )
    catalog.to_csv(OUT / "public_observed_pair_blend_candidates.csv", index=False)
    print(catalog.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
