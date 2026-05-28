from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(OUT))
import advanced_jepa_experiments as adv  # noqa: E402


BASES = {
    "raw_rescue05": OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "publicsafe00": OUT / "submission_jepa_public_safe_blend_00.csv",
    "stage2": ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
}
TARGET_SETS = {
    "q_all": ["Q1", "Q2", "Q3"],
    "q23": ["Q2", "Q3"],
    "q2": ["Q2"],
    "q3": ["Q3"],
}
WEIGHTS = [0.20, 0.35, 0.50, 0.75]


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 1e-5, 1.0 - 1e-5)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def read_sub(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def fmt(x: float) -> str:
    return f"{float(x):g}".replace(".", "p")


def main() -> None:
    summary_path = OUT / "mp_count_conditioning_jepa_candidate_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = pd.read_csv(summary_path)
    stage2 = read_sub(BASES["stage2"])
    source_rows = pd.concat(
        [
            summary[summary["cv_mode"].eq("subject_chunk")].head(4),
            summary[summary["cv_mode"].eq("geometry")].head(6),
            summary.sort_values("good_axis_projection_ratio", ascending=False).head(4),
        ],
        ignore_index=True,
    ).drop_duplicates("candidate")
    emitted = []
    for base_name, base_path in BASES.items():
        if not base_path.exists():
            continue
        base_df = read_sub(base_path)
        assert base_df[SUB_KEY].equals(stage2[SUB_KEY])
        base_arr = base_df[TARGETS].to_numpy(dtype=float)
        stage2_arr = stage2[TARGETS].to_numpy(dtype=float)
        for row in source_rows.itertuples(index=False):
            cand_name = str(row.candidate)
            cand_path = OUT / cand_name
            if not cand_path.exists():
                continue
            cand = read_sub(cand_path)
            move = logit(cand[TARGETS].to_numpy(dtype=float)) - logit(stage2_arr)
            for target_set_name, targets in TARGET_SETS.items():
                target_idx = [TARGETS.index(t) for t in targets]
                masked_move = np.zeros_like(move)
                masked_move[:, target_idx] = move[:, target_idx]
                for weight in WEIGHTS:
                    pred = clip(sigmoid(logit(base_arr) + float(weight) * masked_move))
                    file_name = (
                        "submission_mp_count_public_blend"
                        f"_{base_name}_{Path(cand_name).stem}"
                        f"_{target_set_name}_w{fmt(weight)}.csv"
                    )
                    out = base_df.copy()
                    out[TARGETS] = pred
                    out.to_csv(OUT / file_name, index=False)
                    emitted.append(
                        {
                            "candidate": file_name,
                            "base": base_name,
                            "source": cand_name,
                            "target_set": target_set_name,
                            "weight": float(weight),
                            "source_cv_mode": str(row.cv_mode),
                            "source_oof_loss": float(row.oof_loss),
                            "source_oof_delta_vs_stage2": float(row.oof_delta_vs_stage2),
                            **adv.public_axis_for(file_name),
                        }
                    )
    out_df = pd.DataFrame(emitted)
    out_df = out_df.sort_values(
        ["bad_axis_projection_ratio", "good_axis_projection_ratio"],
        ascending=[True, False],
        na_position="last",
    ).reset_index(drop=True)
    out_df.to_csv(OUT / "mp_count_public_blend_summary.csv", index=False)
    print(out_df.head(40).to_string(index=False))


if __name__ == "__main__":
    main()
