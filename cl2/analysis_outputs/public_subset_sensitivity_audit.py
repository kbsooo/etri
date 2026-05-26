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

BASE_FILES = [
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "submission_public2dblend_budget0p0.csv",
    "submission_projblend_cap0p0.csv",
]
FOCUS_FILES = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def load_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def ce_matrix(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return -(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))


def row_score(loss_matrix: np.ndarray, row_mask: np.ndarray) -> float:
    return float(loss_matrix[row_mask].mean())


def mask_record(kind: str, name: str, mask: np.ndarray) -> dict[str, object]:
    return {"mask_kind": kind, "mask_name": name, "rows": int(mask.sum()), "mask": mask}


def random_row_masks(n: int, rng: np.random.Generator) -> list[dict[str, object]]:
    rows = []
    for frac in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        k = max(1, int(round(n * frac)))
        for rep in range(240):
            idx = rng.choice(n, size=k, replace=False)
            mask = np.zeros(n, dtype=bool)
            mask[idx] = True
            rows.append(mask_record("random_rows", f"frac{frac:.2f}_rep{rep:03d}", mask))
    return rows


def global_order_masks(sample: pd.DataFrame) -> list[dict[str, object]]:
    n = len(sample)
    rows = []
    order = np.arange(n)
    for frac in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        k = max(1, int(round(n * frac)))
        m = np.zeros(n, dtype=bool)
        m[order[:k]] = True
        rows.append(mask_record("global_order", f"prefix_frac{frac:.2f}", m))
        m = np.zeros(n, dtype=bool)
        m[order[-k:]] = True
        rows.append(mask_record("global_order", f"suffix_frac{frac:.2f}", m))
    for mod in [2, 3, 4, 5]:
        for rem in range(mod):
            m = order % mod == rem
            rows.append(mask_record("global_order", f"rowmod{mod}_rem{rem}", m))
    return rows


def subject_masks(sample: pd.DataFrame, rng: np.random.Generator) -> list[dict[str, object]]:
    rows = []
    n = len(sample)
    sample = sample.copy()
    sample["_row"] = np.arange(n)
    for frac in [0.25, 0.40, 0.50, 0.60]:
        mask_prefix = np.zeros(n, dtype=bool)
        mask_suffix = np.zeros(n, dtype=bool)
        for _sid, group in sample.groupby("subject_id", sort=False):
            idx = group["_row"].to_numpy()
            k = max(1, int(round(len(idx) * frac)))
            mask_prefix[idx[:k]] = True
            mask_suffix[idx[-k:]] = True
        rows.append(mask_record("subject_order", f"per_subject_prefix_frac{frac:.2f}", mask_prefix))
        rows.append(mask_record("subject_order", f"per_subject_suffix_frac{frac:.2f}", mask_suffix))
        for rep in range(160):
            m = np.zeros(n, dtype=bool)
            for _sid, group in sample.groupby("subject_id", sort=False):
                idx = group["_row"].to_numpy()
                k = max(1, int(round(len(idx) * frac)))
                start = int(rng.integers(0, max(1, len(idx) - k + 1)))
                m[idx[start : start + k]] = True
            rows.append(mask_record("subject_contiguous", f"frac{frac:.2f}_rep{rep:03d}", m))
    for sid, group in sample.groupby("subject_id", sort=False):
        m = np.zeros(n, dtype=bool)
        m[group["_row"].to_numpy()] = True
        rows.append(mask_record("single_subject", str(sid), m))
    return rows


def build_masks(sample: pd.DataFrame) -> list[dict[str, object]]:
    rng = np.random.default_rng(260526)
    masks = []
    masks.append(mask_record("all", "all_250", np.ones(len(sample), dtype=bool)))
    masks.extend(global_order_masks(sample))
    masks.extend(subject_masks(sample, rng))
    masks.extend(random_row_masks(len(sample), rng))
    return masks


def rank_score(row: pd.Series) -> float:
    return float(
        row["full_expected"]
        + 0.50 * max(row["subset_p90_delta_vs_full"], 0.0)
        + 1.00 * max(row["subset_p95_delta_vs_full"], 0.0)
        + 0.25 * max(row["worst_structured_delta_vs_full"], 0.0)
        + 0.20 * max(row["loss_vs_prior_p90"], 0.0)
        + 0.01 * max(0.80 - row["win_rate_vs_prior"], 0.0)
    )


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    q_file = "submission_public_entropyproj_public2d0_g100.csv"
    q = load_sub(q_file)[TARGETS].to_numpy(dtype=float)
    prior_file = "submission_public2dblend_budget0p0.csv"
    prior = load_sub(prior_file)[TARGETS].to_numpy(dtype=float)
    stage2_file = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
    stage2 = load_sub(stage2_file)[TARGETS].to_numpy(dtype=float)

    selected = []
    selected_path = OUT / "public_entropy_targetmask_selected.csv"
    if selected_path.exists():
        selected.extend(pd.read_csv(selected_path)["file"].tolist())
    summary_path = OUT / "public_entropy_projection_summary.csv"
    if summary_path.exists():
        selected.extend(pd.read_csv(summary_path)["file"].tolist())
    ensemble_path = OUT / "public_minimax_ensemble_selected.csv"
    if ensemble_path.exists():
        selected.extend(pd.read_csv(ensemble_path)["file"].tolist())
    conservative_path = OUT / "public_conservative_frontier_selected.csv"
    if conservative_path.exists():
        selected.extend(pd.read_csv(conservative_path)["file"].tolist())
    maskaware_path = OUT / "public_maskaware_entropy_selected.csv"
    if maskaware_path.exists():
        selected.extend(pd.read_csv(maskaware_path)["file"].tolist())
    universe_path = OUT / "public_universe_minimax_selected.csv"
    if universe_path.exists():
        selected.extend(pd.read_csv(universe_path)["file"].tolist())
    files = []
    for file_name in BASE_FILES + FOCUS_FILES + selected:
        if file_name not in files and (OUT / file_name).exists():
            files.append(file_name)

    masks = build_masks(sample)
    prior_loss = ce_matrix(q, prior)
    stage2_loss = ce_matrix(q, stage2)
    candidate_losses = {file_name: ce_matrix(q, load_sub(file_name)[TARGETS].to_numpy(dtype=float)) for file_name in files}

    detail_rows = []
    for mask_rec in masks:
        mask = mask_rec["mask"]
        assert isinstance(mask, np.ndarray)
        prior_score = row_score(prior_loss, mask)
        stage2_score = row_score(stage2_loss, mask)
        for file_name, loss in candidate_losses.items():
            score = row_score(loss, mask)
            detail_rows.append(
                {
                    "file": file_name,
                    "mask_kind": mask_rec["mask_kind"],
                    "mask_name": mask_rec["mask_name"],
                    "rows": mask_rec["rows"],
                    "expected_loss": score,
                    "delta_vs_prior": score - prior_score,
                    "delta_vs_stage2": score - stage2_score,
                }
            )
    detail = pd.DataFrame(detail_rows)
    detail.to_csv(OUT / "public_subset_sensitivity_detail.csv", index=False)

    all_scores = detail[detail["mask_kind"] == "all"].set_index("file")["expected_loss"].to_dict()
    structured = detail[~detail["mask_kind"].isin(["all", "random_rows"])]
    summary_rows = []
    for file_name, group in detail.groupby("file"):
        full_expected = float(all_scores[file_name])
        random_group = group[group["mask_kind"] == "random_rows"]
        structured_group = structured[structured["file"] == file_name]
        summary_rows.append(
            {
                "file": file_name,
                "full_expected": full_expected,
                "subset_mean_expected": float(group[group["mask_kind"] != "all"]["expected_loss"].mean()),
                "subset_std_expected": float(group[group["mask_kind"] != "all"]["expected_loss"].std()),
                "subset_p90_expected": float(group[group["mask_kind"] != "all"]["expected_loss"].quantile(0.90)),
                "subset_p95_expected": float(group[group["mask_kind"] != "all"]["expected_loss"].quantile(0.95)),
                "subset_worst_expected": float(group[group["mask_kind"] != "all"]["expected_loss"].max()),
                "subset_p90_delta_vs_full": float(
                    group[group["mask_kind"] != "all"]["expected_loss"].quantile(0.90) - full_expected
                ),
                "subset_p95_delta_vs_full": float(
                    group[group["mask_kind"] != "all"]["expected_loss"].quantile(0.95) - full_expected
                ),
                "random_p95_delta_vs_full": float(random_group["expected_loss"].quantile(0.95) - full_expected),
                "worst_structured_delta_vs_full": float(structured_group["expected_loss"].max() - full_expected),
                "mean_delta_vs_prior": float(group[group["mask_kind"] != "all"]["delta_vs_prior"].mean()),
                "loss_vs_prior_p90": float(group[group["mask_kind"] != "all"]["delta_vs_prior"].quantile(0.90)),
                "win_rate_vs_prior": float((group[group["mask_kind"] != "all"]["delta_vs_prior"] < 0).mean()),
                "mean_delta_vs_stage2": float(group[group["mask_kind"] != "all"]["delta_vs_stage2"].mean()),
                "win_rate_vs_stage2": float((group[group["mask_kind"] != "all"]["delta_vs_stage2"] < 0).mean()),
                "n_masks": int(len(group) - 1),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary["subset_robust_score"] = summary.apply(rank_score, axis=1)
    summary = summary.sort_values(["subset_robust_score", "full_expected"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_subset_sensitivity_summary.csv", index=False)

    worst = (
        detail[detail["mask_kind"] != "all"]
        .assign(delta_vs_full=lambda d: d["expected_loss"] - d["file"].map(all_scores))
        .sort_values(["file", "delta_vs_full"], ascending=[True, False])
        .groupby("file")
        .head(8)
        .reset_index(drop=True)
    )
    worst.to_csv(OUT / "public_subset_sensitivity_worst_masks.csv", index=False)

    report = []
    report.append("# Public Subset Sensitivity Audit\n")
    report.append(
        "Expected losses use `submission_public_entropyproj_public2d0_g100.csv` as the posterior label distribution. "
        "Masks simulate possible public row subsets.\n"
    )
    cols = [
        "file",
        "full_expected",
        "subset_p95_delta_vs_full",
        "worst_structured_delta_vs_full",
        "mean_delta_vs_prior",
        "loss_vs_prior_p90",
        "win_rate_vs_prior",
        "subset_robust_score",
    ]
    report.append("\n## Top Robust Candidates\n")
    report.append("```\n" + summary[cols].head(24).round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Worst Mask Examples For Top 8\n")
    top_files = set(summary.head(8)["file"])
    report.append(
        "```\n"
        + worst[worst["file"].isin(top_files)][
            ["file", "mask_kind", "mask_name", "rows", "expected_loss", "delta_vs_full", "delta_vs_prior"]
        ]
        .round(9)
        .head(48)
        .to_string(index=False)
        + "\n```"
    )
    (OUT / "public_subset_sensitivity_report.md").write_text("".join(report))

    print("[subset sensitivity summary]")
    print(summary[cols].head(30).round(9).to_string(index=False))
    print("\n[worst masks top files]")
    print(
        worst[worst["file"].isin(top_files)][
            ["file", "mask_kind", "mask_name", "rows", "expected_loss", "delta_vs_full", "delta_vs_prior"]
        ]
        .round(9)
        .head(60)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
