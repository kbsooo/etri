from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
Q2_IDX = TARGETS.index("Q2")
EPS = 1e-5

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def oof_name_for_submission(file_name: str) -> str:
    return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def load_oof(file_name: str) -> np.ndarray:
    return clip(np.load(OUT / oof_name_for_submission(file_name)))


def blend_col(base: np.ndarray, donor: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip((1.0 - weight) * base + weight * donor)
    if mode == "logit":
        return clip(sigmoid((1.0 - weight) * logit(base) + weight * logit(donor)))
    raise ValueError(mode)


def dedupe_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    rows = []
    seen: set[str] = set()
    for row in df.itertuples(index=False):
        key = str(row.donor_file)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row._asdict())
        if len(rows) >= n:
            break
    return pd.DataFrame(rows)


def main() -> None:
    scan = pd.read_csv(OUT / "q2_publicsafe_residual_blend_scan.csv")
    scan = scan[scan["base_file"].eq(STAGE2)].copy()
    scan["abs_bad_axis"] = scan["bad_axis_coef"].abs()

    aggressive = scan[
        (scan["donor_file"].str.contains("public_maskaware", na=False))
        & (scan["mean_delta"] < -0.00145)
        & (scan["geom_q2_win_rate"] >= 1.0)
        & (scan["two_axis_public_delta_vs_stage2"] <= 0.00002)
        & (scan["submission_q2_abs_move"] <= 0.013)
    ].sort_values(["mean_delta", "geom_q2_delta_mean"])

    conservative = scan[
        (scan["two_axis_public_delta_vs_stage2"] <= 0.000005)
        & (scan["mean_delta"] < -0.00070)
        & (scan["geom_q2_win_rate"] >= 1.0)
        & (scan["submission_q2_abs_move"] <= 0.012)
        & (scan["abs_bad_axis"] <= 0.010)
    ].sort_values(["two_axis_public_delta_vs_stage2", "mean_delta"])

    selected = pd.concat(
        [
            dedupe_rows(aggressive, 4).assign(bucket="aggressive_oof_neutral"),
            dedupe_rows(conservative, 8).assign(bucket="conservative_axis_safe"),
        ],
        ignore_index=True,
    ).drop_duplicates(["donor_file", "mode", "weight"]).reset_index(drop=True)

    base_sub = load_sub(STAGE2)
    base_oof = load_oof(STAGE2)
    out_rows = []
    for idx, row in selected.iterrows():
        donor_file = str(row["donor_file"])
        mode = str(row["mode"])
        weight = float(row["weight"])
        donor_sub = load_sub(donor_file)
        donor_oof = load_oof(donor_file)
        if not base_sub[KEY].equals(donor_sub[KEY]):
            continue

        out = base_sub.copy()
        oof = base_oof.copy()
        out["Q2"] = blend_col(
            base_sub["Q2"].to_numpy(dtype=float),
            donor_sub["Q2"].to_numpy(dtype=float),
            weight,
            mode,
        )
        oof[:, Q2_IDX] = blend_col(base_oof[:, Q2_IDX], donor_oof[:, Q2_IDX], weight, mode)

        tag = stable_tag(f"{donor_file}|{mode}|{weight:.5f}")
        file_name = f"submission_q2_stage2safe_r{idx + 1:02d}_{tag}.csv"
        out.to_csv(OUT / file_name, index=False)
        np.save(OUT / oof_name_for_submission(file_name), oof)
        rec = row.to_dict()
        rec["file"] = file_name
        out_rows.append(rec)

    materialized = pd.DataFrame(out_rows)
    materialized.to_csv(OUT / "q2_stage2safe_candidate_selected.csv", index=False)
    cols = [
        "file",
        "bucket",
        "donor_file",
        "mode",
        "weight",
        "mean_delta",
        "Q2_delta",
        "geom_q2_delta_mean",
        "geom_q2_win_rate",
        "submission_q2_abs_move",
        "two_axis_public_delta_vs_stage2",
        "bad_axis_coef",
    ]
    print(materialized[cols].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
