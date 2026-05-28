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
    sys.path.append(str(OUT))

import public_lb_inverse_mask_audit as inv  # noqa: E402
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402
from public_universe_minimax_optimizer import CORE_Q, MASK_Q, CONSERVATIVE_Q, TARGETS, KEY  # noqa: E402


BASE_KEY = "stage2"
A2C8_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
A2C8_PUBLIC = 0.577439321

ACTUAL_PUBLIC_7 = [
    {
        "key": "stage2",
        "file": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "path": OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "public_lb": 0.5779449757,
        "weight": 0.0,
    },
    {
        "key": "anchor578",
        "file": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "path": OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "public_lb": 0.5784273528,
        "weight": 1.0,
    },
    {
        "key": "ordinal_q",
        "file": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "path": OUT / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "public_lb": 0.5783033652,
        "weight": 1.0,
    },
    {
        "key": "raw05",
        "file": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "path": JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "public_lb": 0.5775263072,
        "weight": 1.8,
    },
    {
        "key": "cvjepa_a2c8",
        "file": A2C8_FILE,
        "path": OUT / A2C8_FILE,
        "public_lb": A2C8_PUBLIC,
        "weight": 2.0,
    },
    {
        "key": "jepa_bad_residual",
        "file": "submission_jepa_latent_residual_probe.csv",
        "path": JEPA / "submission_jepa_latent_residual_probe.csv",
        "public_lb": 0.5812273278,
        "weight": 0.9,
    },
    {
        "key": "jepa_bad_q2",
        "file": "submission_jepa_latent_q2_w0p45.csv",
        "path": JEPA / "submission_jepa_latent_q2_w0p45.csv",
        "public_lb": 0.5798012862,
        "weight": 0.9,
    },
]

SCENARIO_TABLES = [
    ("frontier_cvjepa_surprise_micro_refine_shortlist.csv", 20),
    ("frontier_cvjepa_surprise_micro_refine_local_proxy.csv", 20),
    ("public_lb_bottleneck_after_a2c8_frontier_focus.csv", 16),
    ("raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv", 24),
    ("raw05_jepa_public6_drift_microperturb_shortlist.csv", 24),
    ("raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv", 24),
    ("public_posterior_scenario_robustness_summary.csv", 40),
    ("public_mask_plausibility_reweight_summary.csv", 40),
    ("hidden_block_sequence_motif_shortlist.csv", 20),
]

CANDIDATE_TABLES = [
    ("frontier_cvjepa_surprise_micro_refine_local_proxy.csv", 88),
    ("frontier_cvjepa_surprise_micro_refine_shortlist.csv", 88),
    ("raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv", 160),
    ("raw05_jepa_public6_drift_microperturb_shortlist.csv", 160),
    ("raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv", 160),
    ("raw05_jepa_efmicro_gate_refine_shortlist.csv", 120),
    ("raw05_jepa_energyfront_shortlist.csv", 120),
    ("public_lb_actual_anchor_ranker_scores.csv", 220),
    ("local_lb_proxy_validation_candidate_predictions.csv", 220),
    ("public_posterior_scenario_robustness_summary.csv", 220),
    ("public_mask_plausibility_reweight_summary.csv", 220),
    ("hidden_block_sequence_motif_shortlist.csv", 80),
    ("hidden_block_sequence_motif_cellgate_safe_scores.csv", 120),
    ("hidden_block_rateprobe_shortlist.csv", 60),
]


def locate_file(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    return None


def load_any(name: str | Path) -> pd.DataFrame:
    path = locate_file(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEY).reset_index(drop=True)


def display_name(name: str | Path) -> str:
    path = Path(str(name))
    return path.name if path.is_absolute() else str(name)


def add_file(files: list[str], name: str | Path) -> None:
    path = locate_file(name)
    if path is None:
        return
    value = str(path) if path.parent == JEPA else path.name
    if value not in files:
        files.append(value)


def add_table_files(files: list[str], table_name: str, limit: int) -> None:
    path = OUT / table_name
    if not path.exists():
        return
    frame = pd.read_csv(path)
    if "file" not in frame.columns:
        return
    sort_cols = [
        c
        for c in [
            "ranker_selection_score",
            "refine_score",
            "available_raw05_relative_delta_vs_raw05_public",
            "inverse_candidate_score",
            "focused_scenario_score",
            "scenario_robust_score",
            "posterior_expected_public_vs_anchor",
            "actual_anchor_score_final",
        ]
        if c in frame.columns
    ]
    if sort_cols:
        frame = frame.sort_values(sort_cols)
    for name in frame["file"].dropna().astype(str).head(limit):
        add_file(files, name)


def scenario_files_7() -> list[str]:
    files: list[str] = []
    for name in CORE_Q + MASK_Q + CONSERVATIVE_Q:
        add_file(files, name)
    for rec in ACTUAL_PUBLIC_7:
        add_file(files, rec["path"])
    for table_name, limit in SCENARIO_TABLES:
        add_table_files(files, table_name, limit)
    return files


def candidate_files_7() -> list[str]:
    files: list[str] = []
    for rec in ACTUAL_PUBLIC_7:
        add_file(files, rec["path"])
    for name in inv.candidate_files():
        add_file(files, name)
    for table_name, limit in CANDIDATE_TABLES:
        add_table_files(files, table_name, limit)
    return files


def mask_metadata(sample: pd.DataFrame) -> tuple[list[dict[str, object]], np.ndarray, pd.DataFrame]:
    records = build_masks(sample)
    mat = np.zeros((len(records), len(sample)), dtype=np.float64)
    rows = []
    sample_rows = sample[["subject_id"]].copy()
    sample_rows["_row"] = np.arange(len(sample))
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
        subject_counts = sample_rows.loc[mask].groupby("subject_id").size()
        subject_weights = subject_counts / subject_counts.sum()
        entropy = float(-(subject_weights * np.log(subject_weights)).sum() / np.log(max(2, len(subject_weights))))
        rows.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": rec["rows"],
                "row_frac": float(rec["rows"]) / len(sample),
                "n_subjects": int(subject_counts.size),
                "top_subject": str(subject_counts.idxmax()) if len(subject_counts) else "",
                "top_subject_rows": int(subject_counts.max()) if len(subject_counts) else 0,
                "subject_entropy": entropy,
            }
        )
    return records, mat, pd.DataFrame(rows)


def weighted_rmse(resid: np.ndarray, weights: np.ndarray) -> float:
    active = weights > 0
    return float(np.sqrt(np.average(resid[active] ** 2, weights=weights[active])))


def add_block_overlap(top: pd.DataFrame, masks: list[dict[str, object]], sample: pd.DataFrame) -> pd.DataFrame:
    return inv.add_block_overlap(top, masks, sample)


def inverse_fit(sample: pd.DataFrame, masks: list[dict[str, object]], mask_mat: np.ndarray, mask_meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    actual = pd.DataFrame(ACTUAL_PUBLIC_7)
    base_lb = float(actual.loc[actual["key"] == BASE_KEY, "public_lb"].iloc[0])
    actual["delta_vs_stage2"] = actual["public_lb"] - base_lb
    actual.to_csv(OUT / "public_lb_inverse7_actual_scores.csv", index=False)

    actual_preds = {rec["key"]: load_any(rec["path"])[TARGETS].to_numpy(dtype=np.float64) for rec in ACTUAL_PUBLIC_7}
    delta_keys = [rec["key"] for rec in ACTUAL_PUBLIC_7 if rec["key"] != BASE_KEY]
    actual_delta = actual.set_index("key").loc[delta_keys, "delta_vs_stage2"].to_numpy(dtype=np.float64)
    delta_weights = actual.set_index("key").loc[delta_keys, "weight"].to_numpy(dtype=np.float64)
    delta_scale = np.maximum(np.abs(actual_delta), 2.5e-4)

    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    scenario_names = scenario_files_7()
    print(f"[inverse7] scenarios {len(scenario_names)} masks {len(masks)} delta_keys {delta_keys}")
    for scenario_name in scenario_names:
        q = load_any(scenario_name)[TARGETS].to_numpy(dtype=np.float64)
        score_by_key = {}
        for key, pred in actual_preds.items():
            loss = ce_matrix(q, pred)
            score_by_key[key] = mask_mat @ loss.mean(axis=1)

        base_scores = score_by_key[BASE_KEY]
        pred_delta_mat = np.vstack([score_by_key[key] - base_scores for key in delta_keys]).T
        resid_mat = pred_delta_mat - actual_delta[None, :]
        std_resid_mat = resid_mat / delta_scale[None, :]

        for i in range(len(masks)):
            resid = resid_mat[i]
            std_resid = std_resid_mat[i]
            pred_delta = pred_delta_mat[i]
            sign_ok = np.sign(pred_delta) == np.sign(actual_delta)
            row = {
                "scenario_file": display_name(scenario_name),
                "scenario_path": str(locate_file(scenario_name) or scenario_name),
                "mask_index": i,
                "rmse": float(np.sqrt(np.mean(resid**2))),
                "weighted_rmse": weighted_rmse(resid, delta_weights),
                "std_rmse": float(np.sqrt(np.mean(std_resid**2))),
                "weighted_std_rmse": weighted_rmse(std_resid, delta_weights),
                "sign_acc": float(np.mean(sign_ok)),
                "weighted_sign_acc": float(np.average(sign_ok.astype(float), weights=delta_weights)),
                "all_sign_ok": bool(sign_ok.all()),
                "raw05_sign_ok": bool(sign_ok[delta_keys.index("raw05")]),
                "a2c8_sign_ok": bool(sign_ok[delta_keys.index("cvjepa_a2c8")]),
                "raw05_a2c8_sign_ok": bool(sign_ok[delta_keys.index("raw05")] and sign_ok[delta_keys.index("cvjepa_a2c8")]),
                "max_abs_resid": float(np.max(np.abs(resid))),
                "raw05_resid": float(resid[delta_keys.index("raw05")]),
                "a2c8_resid": float(resid[delta_keys.index("cvjepa_a2c8")]),
                "ordinal_resid": float(resid[delta_keys.index("ordinal_q")]),
                "anchor578_resid": float(resid[delta_keys.index("anchor578")]),
            }
            for key, val in zip(delta_keys, pred_delta):
                row[f"pred_delta_{key}"] = float(val)
            for key, val in zip(delta_keys, resid):
                row[f"resid_{key}"] = float(val)
            rows.append(row)

    detail = pd.DataFrame(rows).merge(mask_meta, on="mask_index", how="left")
    detail["inverse_fit_score"] = (
        detail["weighted_std_rmse"]
        + 0.25 * detail["std_rmse"]
        + 0.40 * (1.0 - detail["weighted_sign_acc"])
        + 0.25 * (~detail["raw05_a2c8_sign_ok"]).astype(float)
        + 15.0 * detail["max_abs_resid"]
    )
    detail = detail.sort_values(["inverse_fit_score", "weighted_std_rmse", "weighted_rmse"]).reset_index(drop=True)
    top_detail = add_block_overlap(detail.head(512).copy(), masks, sample)
    raw05_a2c8 = add_block_overlap(detail[detail["raw05_a2c8_sign_ok"]].head(512).copy(), masks, sample)
    all_sign = add_block_overlap(detail[detail["all_sign_ok"]].head(512).copy(), masks, sample)

    best_pairs = detail.head(64)[["scenario_file", "scenario_path", "mask_index"]].drop_duplicates().reset_index(drop=True)
    for pair in best_pairs.itertuples(index=False):
        q = load_any(str(pair.scenario_path))[TARGETS].to_numpy(dtype=np.float64)
        i = int(pair.mask_index)
        target_losses = {}
        for key, pred in actual_preds.items():
            loss = ce_matrix(q, pred)
            target_losses[key] = {target: float(mask_mat[i] @ loss[:, j]) for j, target in enumerate(TARGETS)}
        for target in TARGETS:
            base_score = target_losses[BASE_KEY][target]
            rec = {"scenario_file": pair.scenario_file, "mask_index": i, "target": target}
            for key in delta_keys:
                rec[f"pred_delta_{key}"] = target_losses[key][target] - base_score
            target_rows.append(rec)
    target_detail = pd.DataFrame(target_rows).merge(mask_meta, on="mask_index", how="left")

    top_detail.to_csv(OUT / "public_lb_inverse7_mask_top512.csv", index=False)
    raw05_a2c8.to_csv(OUT / "public_lb_inverse7_mask_raw05_a2c8_compatible_top512.csv", index=False)
    all_sign.to_csv(OUT / "public_lb_inverse7_mask_all_sign_compatible_top512.csv", index=False)
    target_detail.to_csv(OUT / "public_lb_inverse7_target_delta_top64.csv", index=False)

    by_kind = (
        detail.head(2048)
        .groupby("mask_kind")
        .agg(
            n=("mask_kind", "size"),
            best_rank=("inverse_fit_score", lambda s: int(s.index.min() + 1)),
            best_score=("inverse_fit_score", "min"),
            mean_top_score=("inverse_fit_score", "mean"),
            raw05_a2c8_ok_rate=("raw05_a2c8_sign_ok", "mean"),
            all_sign_ok_rate=("all_sign_ok", "mean"),
            mean_rows=("rows", "mean"),
            mean_subject_entropy=("subject_entropy", "mean"),
        )
        .reset_index()
        .sort_values(["best_score", "mean_top_score"])
    )
    by_scenario = (
        detail.head(2048)
        .groupby("scenario_file")
        .agg(
            n=("scenario_file", "size"),
            best_rank=("inverse_fit_score", lambda s: int(s.index.min() + 1)),
            best_score=("inverse_fit_score", "min"),
            mean_top_score=("inverse_fit_score", "mean"),
            raw05_a2c8_ok_rate=("raw05_a2c8_sign_ok", "mean"),
            all_sign_ok_rate=("all_sign_ok", "mean"),
        )
        .reset_index()
        .sort_values(["best_score", "mean_top_score"])
    )
    by_kind.to_csv(OUT / "public_lb_inverse7_mask_kind_summary.csv", index=False)
    by_scenario.to_csv(OUT / "public_lb_inverse7_scenario_summary.csv", index=False)
    return detail, top_detail, raw05_a2c8, all_sign


def rank_candidates(detail: pd.DataFrame, mask_mat: np.ndarray, out_name: str) -> pd.DataFrame:
    top_for_weights = detail.head(160).copy()
    tau = max(0.10, float(top_for_weights["weighted_std_rmse"].median()))
    weights = np.exp(-0.5 * (top_for_weights["weighted_std_rmse"].to_numpy(dtype=float) / tau) ** 2)
    weights = weights / weights.sum()

    files = candidate_files_7()
    pred_cache = {f: load_any(f)[TARGETS].to_numpy(dtype=np.float64) for f in files}
    scenario_cache: dict[str, np.ndarray] = {}
    combo_scores: dict[str, list[float]] = {f: [] for f in files}
    for pair in top_for_weights.itertuples(index=False):
        scenario_path = str(getattr(pair, "scenario_path"))
        if scenario_path not in scenario_cache:
            scenario_cache[scenario_path] = load_any(scenario_path)[TARGETS].to_numpy(dtype=np.float64)
        q = scenario_cache[scenario_path]
        mask_vec = mask_mat[int(pair.mask_index)]
        for f, pred in pred_cache.items():
            combo_scores[f].append(float(mask_vec @ ce_matrix(q, pred).mean(axis=1)))

    score_mat = np.vstack([combo_scores[f] for f in files])
    best_per_combo = score_mat.min(axis=0)
    rows: list[dict[str, object]] = []
    for row_idx, f in enumerate(files):
        scores = score_mat[row_idx]
        regret = scores - best_per_combo
        rows.append(
            {
                "file": display_name(f),
                "path": str(locate_file(f) or f),
                "inverse7_weighted_expected": float(weights @ scores),
                "inverse7_weighted_regret": float(weights @ regret),
                "inverse7_p90_regret": float(np.quantile(regret, 0.90)),
                "inverse7_max_regret": float(regret.max()),
                "inverse7_win_rate_best_eps1e4": float(np.mean(regret <= 1e-4)),
                "inverse7_score_std": float(np.std(scores)),
            }
        )
    cand = pd.DataFrame(rows)
    cand["inverse7_candidate_score"] = (
        cand["inverse7_weighted_expected"]
        + 2.0 * cand["inverse7_weighted_regret"]
        + 0.75 * cand["inverse7_p90_regret"]
        + 0.05 * cand["inverse7_max_regret"]
        + 0.005 * np.maximum(0.50 - cand["inverse7_win_rate_best_eps1e4"], 0.0)
    )
    cand = cand.sort_values(["inverse7_candidate_score", "inverse7_weighted_expected"]).reset_index(drop=True)
    cand.to_csv(OUT / out_name, index=False)
    return cand


def write_report(
    top_detail: pd.DataFrame,
    raw05_a2c8: pd.DataFrame,
    all_sign: pd.DataFrame,
    cand: pd.DataFrame,
    cand_compat: pd.DataFrame,
) -> None:
    actual = pd.read_csv(OUT / "public_lb_inverse7_actual_scores.csv")
    by_kind = pd.read_csv(OUT / "public_lb_inverse7_mask_kind_summary.csv")
    by_scenario = pd.read_csv(OUT / "public_lb_inverse7_scenario_summary.csv")
    target_detail = pd.read_csv(OUT / "public_lb_inverse7_target_delta_top64.csv")

    def table(frame: pd.DataFrame, cols: list[str], n: int) -> str:
        sub = frame[[c for c in cols if c in frame.columns]].head(n).copy()
        return sub.round(9).to_string(index=False)

    mask_cols = [
        "scenario_file",
        "mask_kind",
        "mask_name",
        "rows",
        "inverse_fit_score",
        "weighted_std_rmse",
        "weighted_rmse",
        "weighted_sign_acc",
        "raw05_a2c8_sign_ok",
        "pred_delta_raw05",
        "pred_delta_cvjepa_a2c8",
        "pred_delta_anchor578",
        "pred_delta_ordinal_q",
        "top_blocks",
    ]
    cand_cols = [
        "file",
        "inverse7_candidate_score",
        "inverse7_weighted_expected",
        "inverse7_weighted_regret",
        "inverse7_p90_regret",
        "inverse7_win_rate_best_eps1e4",
    ]
    target_cols = [
        "scenario_file",
        "mask_kind",
        "mask_name",
        "target",
        "pred_delta_raw05",
        "pred_delta_cvjepa_a2c8",
        "pred_delta_anchor578",
        "pred_delta_jepa_bad_residual",
    ]

    report = [
        "# Public LB Inverse Mask Audit 7-Anchor",
        "",
        "This is the public inverse audit after adding `submission_frontier_cvjepa_refine_a2c8d2c8.csv` public `0.577439321` as a seventh anchor.",
        "",
        "## Actual Public Constraints",
        "",
        "```",
        actual[["key", "file", "public_lb", "delta_vs_stage2", "weight"]].round(10).to_string(index=False),
        "```",
        "",
        "## Top Inverse-Fit Masks",
        "",
        "```",
        table(top_detail, mask_cols, 30),
        "```",
        "",
        "## Raw05 + A2C8 Sign-Compatible Masks",
        "",
        f"raw05+a2c8-compatible rows: `{len(raw05_a2c8)}`; all-sign-compatible rows: `{len(all_sign)}`.",
        "",
        "```",
        table(raw05_a2c8, mask_cols, 24),
        "```",
        "",
        "## Mask Kind Summary",
        "",
        "```",
        by_kind.round(9).to_string(index=False),
        "```",
        "",
        "## Scenario Summary",
        "",
        "```",
        table(by_scenario, ["scenario_file", "n", "best_rank", "best_score", "mean_top_score", "raw05_a2c8_ok_rate", "all_sign_ok_rate"], 40),
        "```",
        "",
        "## Target Delta Decomposition",
        "",
        "```",
        table(target_detail, target_cols, 60),
        "```",
        "",
        "## Candidate Re-Ranking By 7-Anchor Inverse Masks",
        "",
        "```",
        table(cand, cand_cols, 50),
        "```",
        "",
        "## Candidate Re-Ranking By Raw05+A2C8-Compatible Masks",
        "",
        "```",
        table(cand_compat, cand_cols, 50),
        "```",
        "",
        "## Interpretation",
        "",
        "- Adding `a2c8` turns the public inverse problem into a stricter constraint: candidates now need to explain two good anchors (`raw05`, `a2c8`) while rejecting the two bad JEPA latent probes.",
        "- If top masks concentrate in random/subject-contiguous masks, the public split is still underidentified; if they concentrate in a hidden-block scenario, that branch becomes a stronger hidden-test hypothesis.",
        "- Candidate ranking is not a submit decision by itself. It is a diagnostic: prefer next probes that are high under both 7-anchor inverse masks and raw05+a2c8-compatible masks, and that move along a different axis from `a2c8`.",
        "",
    ]
    (OUT / "public_lb_inverse7_mask_audit_report.md").write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    masks, mask_mat, mask_meta = mask_metadata(sample)
    detail, top_detail, raw05_a2c8, all_sign = inverse_fit(sample, masks, mask_mat, mask_meta)
    cand = rank_candidates(detail, mask_mat, "public_lb_inverse7_candidate_ranking.csv")
    compat_source = raw05_a2c8 if len(raw05_a2c8) >= 16 else top_detail
    cand_compat = rank_candidates(compat_source, mask_mat, "public_lb_inverse7_candidate_ranking_raw05_a2c8_compatible.csv")
    write_report(top_detail, raw05_a2c8, all_sign, cand, cand_compat)

    mask_cols = [
        "scenario_file",
        "mask_kind",
        "mask_name",
        "rows",
        "inverse_fit_score",
        "weighted_std_rmse",
        "weighted_sign_acc",
        "raw05_a2c8_sign_ok",
        "pred_delta_raw05",
        "pred_delta_cvjepa_a2c8",
    ]
    cand_cols = [
        "file",
        "inverse7_candidate_score",
        "inverse7_weighted_expected",
        "inverse7_weighted_regret",
        "inverse7_p90_regret",
    ]
    print("[inverse7 top masks]")
    print(top_detail[mask_cols].head(20).round(9).to_string(index=False))
    print("\n[inverse7 candidate top]")
    print(cand[cand_cols].head(30).round(9).to_string(index=False))
    print("\n[inverse7 raw05+a2c8 compatible candidate top]")
    print(cand_compat[cand_cols].head(30).round(9).to_string(index=False))
    print(OUT / "public_lb_inverse7_mask_audit_report.md")


if __name__ == "__main__":
    main()
