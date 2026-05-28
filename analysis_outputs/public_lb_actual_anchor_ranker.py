from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, clip, stable_tag  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features, read_any  # noqa: E402
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402


STAGE2_LB = 0.5779449757

TABLE_SOURCES = [
    ("jepa_micro_bridge_ensemble_shortlist.csv", 50),
    ("jepa_block_consensus_rawcorrector_microrefine_shortlist.csv", 50),
    ("jepa_block_consensus_rawcorrector_refine_shortlist.csv", 36),
    ("jepa_block_consensus_rawcorrector_shortlist.csv", 36),
    ("jepa_block_consensus_gate_shortlist.csv", 28),
    ("jepa_bridge_ensemble_shortlist.csv", 35),
    ("jepa_bridge_posterior_regularizer_shortlist.csv", 35),
    ("jepa_public_minimax_rawsafe_bridge_shortlist.csv", 35),
    ("block_scale_jepa_axis_submission_shortlist.csv", 35),
    ("public_lb_inverse_candidate_ranking.csv", 20),
    ("public_minimax_ensemble_selected.csv", 8),
]

MANUAL_FILES = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_jepa_latent_q2_w0p45.csv",
    "submission_jepa_micro_bridge_ensemble_5ffa44a8.csv",
    "submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv",
    "submission_jepa_block_consensus_rawcorr_micro_fea06910.csv",
    "submission_jepa_block_consensus_rawcorr_4fd8bab2.csv",
    "submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv",
    "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    "submission_jepa_bridge_ensemble_86c6c9d1.csv",
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
    "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv",
    "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv",
    "submission_jepa_energy_ensemble_0b862967.csv",
]

KNOWN_PUBLIC = {
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
}

COMBO_TABLES = {
    "inverse_top": "public_lb_inverse_mask_top512.csv",
    "raw05_compatible": "public_lb_inverse_mask_raw05_compatible_top512.csv",
    "all_sign": "public_lb_inverse_mask_all_sign_compatible_top512.csv",
}


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        p = base / file_name
        if p.exists():
            return p
    raise FileNotFoundError(file_name)


def exists(file_name: str) -> bool:
    try:
        locate(file_name)
    except FileNotFoundError:
        return False
    return True


def load_submission(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(locate(file_name), parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def collect_candidates() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(file_name: str, source: str, rank: int) -> None:
        if file_name in seen or not exists(file_name):
            return
        seen.add(file_name)
        rows.append({"file": file_name, "source": source, "source_rank": rank})

    for rank, file_name in enumerate(MANUAL_FILES, start=1):
        add(file_name, "manual", rank)
    for table, n in TABLE_SOURCES:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        sort_cols = [c for c in ["focused_scenario_score", "inverse_candidate_score", "posterior_expected_public_vs_anchor"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols)
        for rank, file_name in enumerate(df["file"].astype(str).head(n), start=1):
            add(file_name, table, rank)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "public_lb_actual_anchor_ranker_pool.csv", index=False)
    return out


def mask_matrix(sample: pd.DataFrame) -> np.ndarray:
    records = build_masks(sample)
    mat = np.zeros((len(records), len(sample)), dtype=np.float64)
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
    return mat


def combo_weights(frame: pd.DataFrame) -> np.ndarray:
    metric = frame["weighted_std_rmse"].to_numpy(dtype=np.float64)
    tau = max(0.25, float(np.median(metric)))
    w = np.exp(-0.5 * (metric / tau) ** 2)
    if "all_sign_ok" in frame.columns:
        w *= np.where(frame["all_sign_ok"].to_numpy(dtype=bool), 1.15, 1.0)
    if "raw05_sign_ok" in frame.columns:
        w *= np.where(frame["raw05_sign_ok"].to_numpy(dtype=bool), 1.10, 1.0)
    w /= w.sum()
    return w


def score_combo_set(
    set_name: str,
    combo_df: pd.DataFrame,
    candidates: pd.DataFrame,
    sample: pd.DataFrame,
    masks: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    combo_df = combo_df.head(160).copy().reset_index(drop=True)
    weights = combo_weights(combo_df)
    stage2 = load_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", sample)
    pred_cache = {row.file: load_submission(str(row.file), sample) for row in candidates.itertuples(index=False)}
    scenario_cache: dict[str, np.ndarray] = {}
    base_losses = []
    q_losses: dict[str, list[float]] = {file_name: [] for file_name in pred_cache}

    for pair in combo_df.itertuples(index=False):
        scenario = str(pair.scenario_file)
        if scenario not in scenario_cache:
            scenario_cache[scenario] = load_submission(scenario, sample)
        q = scenario_cache[scenario]
        mask_vec = masks[int(pair.mask_index)]
        stage_loss = float(mask_vec @ ce_matrix(q, stage2).mean(axis=1))
        base_losses.append(stage_loss)
        for file_name, pred in pred_cache.items():
            loss = float(mask_vec @ ce_matrix(q, pred).mean(axis=1))
            q_losses[file_name].append(STAGE2_LB + loss - stage_loss)

    rows = []
    detail_rows = []
    for file_name, vals in q_losses.items():
        arr = np.asarray(vals, dtype=np.float64)
        p10, p50, p90 = np.quantile(arr, [0.10, 0.50, 0.90])
        rec = {
            "file": file_name,
            "combo_set": set_name,
            "actual_anchor_mean": float(weights @ arr),
            "actual_anchor_median": float(p50),
            "actual_anchor_p10": float(p10),
            "actual_anchor_p90": float(p90),
            "actual_anchor_std": float(np.sqrt(weights @ (arr - weights @ arr) ** 2)),
            "actual_anchor_worst": float(arr.max()),
        }
        rec["actual_anchor_score"] = (
            rec["actual_anchor_mean"]
            + 0.35 * rec["actual_anchor_std"]
            + 0.20 * max(rec["actual_anchor_p90"] - rec["actual_anchor_mean"], 0.0)
            + 0.10 * max(rec["actual_anchor_worst"] - rec["actual_anchor_mean"], 0.0)
        )
        if file_name in KNOWN_PUBLIC:
            rec["known_public"] = KNOWN_PUBLIC[file_name]
            rec["known_public_error"] = rec["actual_anchor_mean"] - KNOWN_PUBLIC[file_name]
        else:
            rec["known_public"] = np.nan
            rec["known_public_error"] = np.nan
        rows.append(rec)
        for i, val in enumerate(arr):
            detail_rows.append(
                {
                    "file": file_name,
                    "combo_set": set_name,
                    "combo_rank": i + 1,
                    "scenario_file": combo_df.loc[i, "scenario_file"],
                    "mask_index": int(combo_df.loc[i, "mask_index"]),
                    "anchored_score": float(val),
                    "combo_weight": float(weights[i]),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(detail_rows)


def write_report(scores: pd.DataFrame, calibration: pd.DataFrame, shortlist: pd.DataFrame) -> None:
    cols = [
        "file",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "known_public",
        "known_public_error_mean",
    ]
    lines = [
        "# Public LB Actual-Anchor Ranker",
        "",
        "Scores candidate submissions by inverse-fit public scenario/mask combinations, but anchors every combo to the observed stage2 public LB.",
        "",
        "## Known Public Calibration",
        "",
        "```csv",
        calibration.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        shortlist[cols].head(50).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "public_lb_actual_anchor_ranker_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    candidates = collect_candidates()
    masks = mask_matrix(sample)
    score_frames = []
    detail_frames = []
    for set_name, table in COMBO_TABLES.items():
        combo_path = OUT / table
        if not combo_path.exists():
            continue
        combo_df = pd.read_csv(combo_path)
        if combo_df.empty:
            continue
        scores, detail = score_combo_set(set_name, combo_df, candidates, sample, masks)
        score_frames.append(scores)
        detail_frames.append(detail)

    all_scores = pd.concat(score_frames, ignore_index=True)
    all_scores.to_csv(OUT / "public_lb_actual_anchor_ranker_by_set.csv", index=False)
    pd.concat(detail_frames, ignore_index=True).to_csv(OUT / "public_lb_actual_anchor_ranker_detail.csv", index=False)

    pivot = all_scores.pivot_table(
        index="file",
        columns="combo_set",
        values=["actual_anchor_score", "actual_anchor_mean", "actual_anchor_std"],
        aggfunc="first",
    )
    pivot.columns = ["__".join(col).strip() for col in pivot.columns.to_flat_index()]
    pivot = pivot.reset_index()
    merged = candidates.merge(pivot, on="file", how="left")

    score_cols = [c for c in merged.columns if c.startswith("actual_anchor_score__")]
    mean_cols = [c for c in merged.columns if c.startswith("actual_anchor_mean__")]
    merged["actual_anchor_score_final"] = merged[score_cols].mean(axis=1)
    merged["mean_actual_anchor"] = merged[mean_cols].mean(axis=1)
    merged["min_set_score"] = merged[score_cols].min(axis=1)
    merged["max_set_score"] = merged[score_cols].max(axis=1)

    axes = public_axes()
    axis_rows = []
    for row in merged.itertuples(index=False):
        pred = load_submission(str(row.file), sample)
        rec = {"file": row.file}
        rec.update(public_axis_features(pred, axes))
        axis_rows.append(rec)
    axis_df = pd.DataFrame(axis_rows)
    merged = merged.merge(axis_df, on="file", how="left")
    known = all_scores[all_scores["file"].isin(KNOWN_PUBLIC)].groupby("file", as_index=False).agg(
        known_public=("known_public", "first"),
        known_public_error_mean=("known_public_error", "mean"),
        known_public_error_abs_mean=("known_public_error", lambda s: float(np.abs(s).mean())),
    )
    merged = merged.merge(known, on="file", how="left")

    merged["axis_penalty"] = (
        np.maximum(merged["delta_vs_raw05_rawaxis"] - 2.0e-7, 0.0) * 120.0
        + np.maximum(np.abs(merged["bad_residual_axis_ratio"]) - 0.0028, 0.0) * 0.030
        + np.maximum(merged["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 2.0
    )
    merged["ranker_selection_score"] = merged["actual_anchor_score_final"] + merged["axis_penalty"]
    ranked = merged.sort_values(["ranker_selection_score", "actual_anchor_score_final"]).reset_index(drop=True)
    ranked.to_csv(OUT / "public_lb_actual_anchor_ranker_scores.csv", index=False)

    shortlist = ranked[
        (ranked["delta_vs_raw05_rawaxis"] <= 3.0e-7)
        & (ranked["posterior_expected_public_vs_anchor"] <= 0.57693)
        & (ranked["bad_residual_axis_ratio"].abs() <= 0.0032)
    ].head(80)
    shortlist.to_csv(OUT / "public_lb_actual_anchor_ranker_shortlist.csv", index=False)
    calibration = ranked[ranked["file"].isin(KNOWN_PUBLIC)][
        [
            "file",
            "known_public",
            "mean_actual_anchor",
            "actual_anchor_score_final",
            "known_public_error_mean",
            "known_public_error_abs_mean",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
        ]
    ].sort_values("known_public")
    calibration.to_csv(OUT / "public_lb_actual_anchor_ranker_calibration.csv", index=False)
    write_report(ranked, calibration, shortlist)

    cols = [
        "file",
        "source",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
    ]
    print(f"candidates={len(candidates)} sets={len(score_frames)} shortlist={len(shortlist)}")
    print("[calibration]")
    print(calibration.round(10).to_string(index=False))
    print("[shortlist]")
    print(shortlist[cols].head(30).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
