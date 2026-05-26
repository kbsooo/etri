from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import breakthrough_structure_probe as bsp  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def summarize_blocks(blocks: pd.DataFrame, split_name: str) -> dict[str, float | str]:
    g = blocks[blocks["split"].eq(split_name)].copy()
    out: dict[str, float | str] = {"split": split_name, "n_blocks": float(len(g)), "n_rows": float(g["n"].sum())}
    if g.empty:
        return out
    out.update(
        {
            "n_min": float(g["n"].min()),
            "n_q25": float(g["n"].quantile(0.25)),
            "n_median": float(g["n"].median()),
            "n_q75": float(g["n"].quantile(0.75)),
            "n_max": float(g["n"].max()),
            "both_boundaries_frac": float(g["prev_train_gap_days"].notna().mul(g["next_train_gap_days"].notna()).mean()),
            "prev_gap_median": float(g["prev_train_gap_days"].median()) if g["prev_train_gap_days"].notna().any() else np.nan,
            "next_gap_median": float(g["next_train_gap_days"].median()) if g["next_train_gap_days"].notna().any() else np.nan,
        }
    )
    return out


def subject_block_cv_geometry(train: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sorted_train = train.sort_values(["subject_id", "lifelog_date"]).copy()
    for fold_id, (_, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        val_set = set(int(x) for x in val_idx)
        val = sorted_train[sorted_train.index.isin(val_set)].copy()
        for sid, g in val.groupby("subject_id", sort=False):
            breaks = g.groupby("subject_id").cumcount()
            # make_folds produces one contiguous validation chunk per subject/fold.
            rows.append(
                {
                    "fold": fold_id,
                    "subject_id": sid,
                    "n": int(len(g)),
                    "start": g["lifelog_date"].min(),
                    "end": g["lifelog_date"].max(),
                    "span_days": int((g["lifelog_date"].max() - g["lifelog_date"].min()).days) + 1,
                    "density": float(len(g) / (int((g["lifelog_date"].max() - g["lifelog_date"].min()).days) + 1)),
                }
            )
    return pd.DataFrame(rows)


def oracle_by_geometry(train: pd.DataFrame) -> pd.DataFrame:
    folds = d.make_folds(train, "subject_blocks")
    base = cal.base_oof(train, folds)
    oracle = bsp.validation_block_oracle(train, folds)
    y = train[TARGETS].to_numpy(dtype=int)
    sorted_train = train.sort_values(["subject_id", "lifelog_date"]).copy()
    sorted_train["orig_index"] = sorted_train.index
    sorted_train["subject_pos"] = sorted_train.groupby("subject_id").cumcount()

    records = []
    for fold_id, (_, val_idx) in enumerate(folds):
        val_set = set(int(x) for x in val_idx)
        val_rows = sorted_train[sorted_train["orig_index"].isin(val_set)].copy()
        for sid, g in val_rows.groupby("subject_id", sort=False):
            breaks = g["subject_pos"].diff().fillna(1).ne(1).cumsum()
            for _, block in g.groupby(breaks):
                idx = block["orig_index"].to_numpy(dtype=int)
                rec = {
                    "fold": fold_id,
                    "subject_id": sid,
                    "n": int(len(idx)),
                    "start": block["lifelog_date"].min(),
                    "end": block["lifelog_date"].max(),
                }
                for j, target in enumerate(TARGETS):
                    rec[f"rate__{target}"] = float(y[idx, j].mean())
                    rec[f"base_loss__{target}"] = float(log_loss(y[idx, j], clip(base[idx, j]), labels=[0, 1]))
                    rec[f"oracle_loss__{target}"] = float(log_loss(y[idx, j], clip(oracle[idx, j]), labels=[0, 1]))
                records.append(rec)
    out = pd.DataFrame(records)
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    blocks = bsp.split_block_summary(train, sub)
    sub_cv = subject_block_cv_geometry(train)
    oracle_geom = oracle_by_geometry(train)

    blocks.to_csv(OUT / "split_geometry_actual_blocks.csv", index=False)
    sub_cv.to_csv(OUT / "split_geometry_subjectblock_cv.csv", index=False)
    oracle_geom.to_csv(OUT / "split_geometry_oracle_by_cv_block.csv", index=False)

    rows = []
    rows.append(summarize_blocks(blocks, "train"))
    rows.append(summarize_blocks(blocks, "submission"))
    cv_summary = {
        "split": "subjectblock_cv_val",
        "n_blocks": float(len(sub_cv)),
        "n_rows": float(sub_cv["n"].sum()),
        "n_min": float(sub_cv["n"].min()),
        "n_q25": float(sub_cv["n"].quantile(0.25)),
        "n_median": float(sub_cv["n"].median()),
        "n_q75": float(sub_cv["n"].quantile(0.75)),
        "n_max": float(sub_cv["n"].max()),
        "both_boundaries_frac": np.nan,
        "prev_gap_median": np.nan,
        "next_gap_median": np.nan,
    }
    rows.append(cv_summary)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "split_geometry_summary.csv", index=False)

    oracle_rows = []
    for target in TARGETS:
        oracle_rows.append(
            {
                "target": target,
                "block_rate_std": float(oracle_geom[f"rate__{target}"].std()),
                "base_block_loss_mean": float(oracle_geom[f"base_loss__{target}"].mean()),
                "oracle_block_loss_mean": float(oracle_geom[f"oracle_loss__{target}"].mean()),
                "oracle_gain": float(
                    oracle_geom[f"base_loss__{target}"].mean() - oracle_geom[f"oracle_loss__{target}"].mean()
                ),
            }
        )
    oracle_summary = pd.DataFrame(oracle_rows).sort_values("oracle_gain", ascending=False)
    oracle_summary.to_csv(OUT / "split_geometry_oracle_gain_summary.csv", index=False)

    print("Geometry summary")
    print(summary.round(3).to_string(index=False))
    print("\nOracle gain by target")
    print(oracle_summary.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
