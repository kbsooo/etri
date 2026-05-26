from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

PRIOR_FILE = "submission_public2dblend_budget0p0.csv"
FILES = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def load_submission(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def main() -> None:
    prior = load_submission(PRIOR_FILE)
    target_rows = []
    subject_target_rows = []
    top_cell_rows = []

    prior_prob = prior[TARGETS].to_numpy(dtype=float)
    prior_logit = logit(prior_prob)

    for file_name in FILES:
        sub = load_submission(file_name)
        if not sub[KEY].equals(prior[KEY]):
            raise ValueError(f"Key mismatch for {file_name}")

        prob = sub[TARGETS].to_numpy(dtype=float)
        delta = prob - prior_prob
        logit_delta = logit(prob) - prior_logit

        for j, target in enumerate(TARGETS):
            target_rows.append(
                {
                    "file": file_name,
                    "target": target,
                    "mean_delta": float(delta[:, j].mean()),
                    "mean_abs_delta": float(np.abs(delta[:, j]).mean()),
                    "p90_abs_delta": float(np.quantile(np.abs(delta[:, j]), 0.90)),
                    "mean_logit_delta": float(logit_delta[:, j].mean()),
                    "positive_move_rate": float((delta[:, j] > 0).mean()),
                }
            )

        tmp = prior[KEY].copy()
        tmp["subject_id"] = tmp["subject_id"].astype(str)
        for j, target in enumerate(TARGETS):
            tmp[target] = delta[:, j]
        for subject_id, group in tmp.groupby("subject_id"):
            for target in TARGETS:
                subject_target_rows.append(
                    {
                        "file": file_name,
                        "subject_id": subject_id,
                        "target": target,
                        "mean_delta": float(group[target].mean()),
                        "mean_abs_delta": float(group[target].abs().mean()),
                    }
                )

        flat = []
        for i in range(len(sub)):
            for j, target in enumerate(TARGETS):
                flat.append(
                    {
                        "file": file_name,
                        "row": int(i),
                        "subject_id": str(sub.loc[i, "subject_id"]),
                        "lifelog_date": sub.loc[i, "lifelog_date"].date().isoformat(),
                        "target": target,
                        "prior": float(prior.loc[i, target]),
                        "projected": float(sub.loc[i, target]),
                        "delta": float(delta[i, j]),
                        "abs_delta": float(abs(delta[i, j])),
                    }
                )
        top_cell_rows.extend(sorted(flat, key=lambda row: row["abs_delta"], reverse=True)[:20])

    target_summary = pd.DataFrame(target_rows).sort_values(["file", "mean_abs_delta"], ascending=[True, False])
    subject_target_summary = pd.DataFrame(subject_target_rows).sort_values(
        ["file", "mean_abs_delta"], ascending=[True, False]
    )
    top_cells = pd.DataFrame(top_cell_rows).sort_values(["file", "abs_delta"], ascending=[True, False])

    target_summary.to_csv(OUT / "public_entropy_projection_target_shift_summary.csv", index=False)
    subject_target_summary.to_csv(OUT / "public_entropy_projection_subject_target_shift_summary.csv", index=False)
    top_cells.to_csv(OUT / "public_entropy_projection_top_shift_cells.csv", index=False)

    print("[target shift summary]")
    print(target_summary.to_string(index=False))
    print("\n[top g075 subject-target shifts]")
    print(subject_target_summary[subject_target_summary["file"].str.contains("g075")].head(20).to_string(index=False))
    print("\n[top g075 cells]")
    print(top_cells[top_cells["file"].str.contains("g075")].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
