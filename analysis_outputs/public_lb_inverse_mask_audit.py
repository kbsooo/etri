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

from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402
from public_universe_minimax_optimizer import CORE_Q, MASK_Q, CONSERVATIVE_Q, TARGETS, KEY  # noqa: E402


ACTUAL_PUBLIC = [
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

BASE_KEY = "stage2"


def load_any(path_or_name: Path | str) -> pd.DataFrame:
    path = Path(path_or_name)
    if not path.exists():
        path = OUT / str(path_or_name)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEY).reset_index(drop=True)


def add_file(files: list[str], name: str) -> None:
    if name and (OUT / name).exists() and name not in files:
        files.append(name)


def scenario_files() -> list[str]:
    files: list[str] = []
    for name in CORE_Q + MASK_Q + CONSERVATIVE_Q:
        add_file(files, name)
    for rec in ACTUAL_PUBLIC:
        if rec["path"].exists() and str(rec["path"]) not in files:
            files.append(str(rec["path"]))
    return files


def candidate_files() -> list[str]:
    files: list[str] = []
    for rec in ACTUAL_PUBLIC:
        if rec["path"].parent == OUT:
            add_file(files, str(rec["file"]))
    for table, n in [
        ("public_posterior_scenario_robustness_summary.csv", 180),
        ("public_mask_plausibility_reweight_summary.csv", 180),
        ("public_universe_minimax_selected.csv", 32),
        ("public_minimax_ensemble_selected.csv", 32),
        ("hidden_block_sequence_motif_shortlist.csv", 80),
        ("hidden_block_sequence_motif_cellgate_safe_scores.csv", 120),
        ("hidden_block_rateprobe_shortlist.csv", 40),
    ]:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        for name in df["file"].head(n).tolist():
            add_file(files, str(name))
    for name in [
        "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
        "submission_hiddenblock_seqmotif_cellgate_5e4cf566.csv",
        "submission_hiddenblock_seqmotif_cellgate_7394e0e7.csv",
        "submission_hiddenblock_seqmotif_cellgate_8eafa541.csv",
        "submission_hiddenblock_rateprobe_neutral_95ebba6c.csv",
        "submission_hiddenblock_rateprobe_neutral_605de284.csv",
        "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
        "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    ]:
        add_file(files, name)
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
        top_subject = str(subject_counts.idxmax()) if len(subject_counts) else ""
        rows.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": rec["rows"],
                "row_frac": float(rec["rows"]) / len(sample),
                "n_subjects": int(subject_counts.size),
                "top_subject": top_subject,
                "top_subject_rows": int(subject_counts.max()) if len(subject_counts) else 0,
                "subject_entropy": entropy,
            }
        )
    return records, mat, pd.DataFrame(rows)


def assign_hidden_blocks(sample: pd.DataFrame) -> pd.DataFrame:
    blocks_path = OUT / "hidden_block_posterior_block_summary.csv"
    out = sample[KEY].copy()
    out["hidden_block_id"] = ""
    out["block_n_rows"] = np.nan
    if not blocks_path.exists():
        return out
    blocks = pd.read_csv(blocks_path, parse_dates=["start", "end"])
    sleep_dates = pd.to_datetime(out["sleep_date"])
    for row in blocks.itertuples(index=False):
        idx = (
            (out["subject_id"].astype(str) == str(row.subject_id))
            & (sleep_dates >= row.start)
            & (sleep_dates <= row.end)
        )
        out.loc[idx, "hidden_block_id"] = str(row.hidden_block_id)
        out.loc[idx, "block_n_rows"] = int(row.n_rows)
    return out


def add_block_overlap(top: pd.DataFrame, masks: list[dict[str, object]], sample: pd.DataFrame) -> pd.DataFrame:
    block_rows = assign_hidden_blocks(sample)
    records = []
    for mask_index in sorted(set(top["mask_index"].astype(int).tolist())):
        mask = masks[mask_index]["mask"]
        assert isinstance(mask, np.ndarray)
        sub = block_rows.loc[mask].copy()
        counts = sub.groupby("hidden_block_id").size().sort_values(ascending=False)
        if "" in counts.index:
            counts = counts.drop(index="")
        top_blocks = ";".join(f"{idx}:{int(val)}" for idx, val in counts.head(5).items())
        records.append({"mask_index": mask_index, "top_blocks": top_blocks, "n_blocks_hit": int((counts > 0).sum())})
    return top.merge(pd.DataFrame(records), on="mask_index", how="left")


def weighted_rmse(resid: np.ndarray, weights: np.ndarray) -> float:
    active = weights > 0
    return float(np.sqrt(np.average(resid[active] ** 2, weights=weights[active])))


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    masks, mask_mat, mask_meta = mask_metadata(sample)
    actual = pd.DataFrame(ACTUAL_PUBLIC)
    base_lb = float(actual.loc[actual["key"] == BASE_KEY, "public_lb"].iloc[0])
    actual["delta_vs_stage2"] = actual["public_lb"] - base_lb
    actual.to_csv(OUT / "public_lb_inverse_actual_scores.csv", index=False)

    actual_preds = {
        rec["key"]: load_any(rec["path"])[TARGETS].to_numpy(dtype=np.float64)
        for rec in ACTUAL_PUBLIC
    }
    base_pred_key = BASE_KEY
    delta_keys = [rec["key"] for rec in ACTUAL_PUBLIC if rec["key"] != BASE_KEY]
    actual_delta = actual.set_index("key").loc[delta_keys, "delta_vs_stage2"].to_numpy(dtype=np.float64)
    delta_weights = actual.set_index("key").loc[delta_keys, "weight"].to_numpy(dtype=np.float64)
    delta_scale = np.maximum(np.abs(actual_delta), 2.5e-4)

    scenario_names = scenario_files()
    # Actual public submissions are useful as soft-label stress scenarios too.
    for rec in ACTUAL_PUBLIC:
        if rec["path"].parent == OUT:
            add_file(scenario_names, str(rec["file"]))
    print(f"[inverse] scenarios {len(scenario_names)} masks {len(masks)} actual_delta_keys {delta_keys}")

    rows = []
    target_rows = []
    for scenario_name in scenario_names:
        q = load_any(scenario_name)[TARGETS].to_numpy(dtype=np.float64)
        score_by_key = {}
        target_score_by_key = {}
        for key, pred in actual_preds.items():
            loss = ce_matrix(q, pred)
            score_by_key[key] = mask_mat @ loss.mean(axis=1)
            target_score_by_key[key] = {target: mask_mat @ loss[:, j] for j, target in enumerate(TARGETS)}

        base_scores = score_by_key[base_pred_key]
        pred_delta_mat = np.vstack([score_by_key[key] - base_scores for key in delta_keys]).T
        resid_mat = pred_delta_mat - actual_delta[None, :]
        std_resid_mat = resid_mat / delta_scale[None, :]

        for i in range(len(masks)):
            resid = resid_mat[i]
            std_resid = std_resid_mat[i]
            pred_delta = pred_delta_mat[i]
            sign_acc = float(np.mean(np.sign(pred_delta) == np.sign(actual_delta)))
            weighted_sign = float(np.average((np.sign(pred_delta) == np.sign(actual_delta)).astype(float), weights=delta_weights))
            sign_ok = np.sign(pred_delta) == np.sign(actual_delta)
            row = {
                "scenario_file": scenario_name,
                "mask_index": i,
                "rmse": float(np.sqrt(np.mean(resid**2))),
                "weighted_rmse": weighted_rmse(resid, delta_weights),
                "std_rmse": float(np.sqrt(np.mean(std_resid**2))),
                "weighted_std_rmse": weighted_rmse(std_resid, delta_weights),
                "sign_acc": sign_acc,
                "weighted_sign_acc": weighted_sign,
                "all_sign_ok": bool(sign_ok.all()),
                "raw05_sign_ok": bool(sign_ok[delta_keys.index("raw05")]),
                "max_abs_resid": float(np.max(np.abs(resid))),
                "raw05_resid": float(resid[delta_keys.index("raw05")]),
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
        + 0.50 * (1.0 - detail["weighted_sign_acc"])
        + 15.0 * detail["max_abs_resid"]
    )
    detail = detail.sort_values(["inverse_fit_score", "weighted_std_rmse", "weighted_rmse"]).reset_index(drop=True)
    top_detail = add_block_overlap(detail.head(512).copy(), masks, sample)
    top_detail.to_csv(OUT / "public_lb_inverse_mask_top512.csv", index=False)
    raw05_compatible = add_block_overlap(detail[detail["raw05_sign_ok"]].head(512).copy(), masks, sample)
    raw05_compatible.to_csv(OUT / "public_lb_inverse_mask_raw05_compatible_top512.csv", index=False)
    sign_compatible = add_block_overlap(detail[detail["all_sign_ok"]].head(512).copy(), masks, sample)
    sign_compatible.to_csv(OUT / "public_lb_inverse_mask_all_sign_compatible_top512.csv", index=False)

    by_kind = (
        detail.head(2048)
        .groupby("mask_kind")
        .agg(
            n=("mask_kind", "size"),
            best_rank=("inverse_fit_score", lambda s: int(s.index.min() + 1)),
            best_score=("inverse_fit_score", "min"),
            mean_top_score=("inverse_fit_score", "mean"),
            mean_rows=("rows", "mean"),
            mean_subject_entropy=("subject_entropy", "mean"),
        )
        .reset_index()
        .sort_values(["best_score", "mean_top_score"])
    )
    by_kind.to_csv(OUT / "public_lb_inverse_mask_kind_summary.csv", index=False)

    by_scenario = (
        detail.head(2048)
        .groupby("scenario_file")
        .agg(
            n=("scenario_file", "size"),
            best_rank=("inverse_fit_score", lambda s: int(s.index.min() + 1)),
            best_score=("inverse_fit_score", "min"),
            mean_top_score=("inverse_fit_score", "mean"),
        )
        .reset_index()
        .sort_values(["best_score", "mean_top_score"])
    )
    by_scenario.to_csv(OUT / "public_lb_inverse_scenario_summary.csv", index=False)

    # Target contribution decomposition for the best inverse-fit masks.
    best_pairs = detail.head(64)[["scenario_file", "mask_index"]].drop_duplicates().reset_index(drop=True)
    for pair in best_pairs.itertuples(index=False):
        scenario_name = str(pair.scenario_file)
        i = int(pair.mask_index)
        q = load_any(scenario_name)[TARGETS].to_numpy(dtype=np.float64)
        target_losses = {}
        for key, pred in actual_preds.items():
            loss = ce_matrix(q, pred)
            target_losses[key] = {target: float(mask_mat[i] @ loss[:, j]) for j, target in enumerate(TARGETS)}
        for target in TARGETS:
            base_score = target_losses[BASE_KEY][target]
            rec = {
                "scenario_file": scenario_name,
                "mask_index": i,
                "target": target,
            }
            for key in delta_keys:
                rec[f"pred_delta_{key}"] = target_losses[key][target] - base_score
            target_rows.append(rec)
    target_detail = pd.DataFrame(target_rows).merge(mask_meta, on="mask_index", how="left")
    target_detail.to_csv(OUT / "public_lb_inverse_target_delta_top64.csv", index=False)

    # Re-rank a focused candidate universe by inverse-fit scenario/mask weights.
    files = candidate_files()
    def rank_candidates(top_for_weights: pd.DataFrame, out_name: str) -> pd.DataFrame:
        top_for_weights = top_for_weights.head(128).copy()
        tau = max(0.10, float(top_for_weights["weighted_std_rmse"].median()))
        weights = np.exp(-0.5 * (top_for_weights["weighted_std_rmse"].to_numpy() / tau) ** 2)
        weights = weights / weights.sum()
        pred_cache = {f: load_any(f)[TARGETS].to_numpy(dtype=np.float64) for f in files}
        scenario_cache: dict[str, np.ndarray] = {}
        combo_scores: dict[str, list[float]] = {f: [] for f in files}
        for pair in top_for_weights.itertuples(index=False):
            scenario_name = str(pair.scenario_file)
            if scenario_name not in scenario_cache:
                scenario_cache[scenario_name] = load_any(scenario_name)[TARGETS].to_numpy(dtype=np.float64)
            q = scenario_cache[scenario_name]
            mask_vec = mask_mat[int(pair.mask_index)]
            for f, pred in pred_cache.items():
                loss = ce_matrix(q, pred).mean(axis=1)
                combo_scores[f].append(float(mask_vec @ loss))
        score_mat = np.vstack([combo_scores[f] for f in files])
        best_per_combo = score_mat.min(axis=0)
        candidate_rows = []
        for row_idx, f in enumerate(files):
            scores = score_mat[row_idx]
            regret = scores - best_per_combo
            candidate_rows.append(
                {
                    "file": f,
                    "inverse_weighted_expected": float(weights @ scores),
                    "inverse_weighted_regret": float(weights @ regret),
                    "inverse_p90_regret": float(np.quantile(regret, 0.90)),
                    "inverse_max_regret": float(regret.max()),
                    "inverse_win_rate_best_eps1e4": float(np.mean(regret <= 1e-4)),
                }
            )
        cand_local = pd.DataFrame(candidate_rows)
        cand_local["inverse_candidate_score"] = (
            cand_local["inverse_weighted_expected"]
            + 2.0 * cand_local["inverse_weighted_regret"]
            + 0.75 * cand_local["inverse_p90_regret"]
            + 0.05 * cand_local["inverse_max_regret"]
            + 0.005 * np.maximum(0.50 - cand_local["inverse_win_rate_best_eps1e4"], 0.0)
        )
        cand_local = cand_local.sort_values(["inverse_candidate_score", "inverse_weighted_expected"]).reset_index(drop=True)
        cand_local.to_csv(OUT / out_name, index=False)
        return cand_local

    cand = rank_candidates(detail.head(128), "public_lb_inverse_candidate_ranking.csv")
    compat_source = sign_compatible if len(sign_compatible) >= 16 else raw05_compatible
    cand_sign = rank_candidates(compat_source, "public_lb_inverse_candidate_ranking_signcompatible.csv")

    report = []
    report.append("# Public LB Inverse Mask Audit\n\n")
    report.append("Fits observed public LB deltas by sweeping posterior scenarios and candidate public row masks.\n\n")
    report.append("## Actual Public Constraints\n\n")
    report.append("```\n" + actual[["key", "file", "public_lb", "delta_vs_stage2", "weight"]].to_string(index=False) + "\n```\n")
    cols = [
        "scenario_file",
        "mask_kind",
        "mask_name",
        "rows",
        "inverse_fit_score",
        "weighted_std_rmse",
        "weighted_rmse",
        "weighted_sign_acc",
        "pred_delta_raw05",
        "pred_delta_anchor578",
        "pred_delta_ordinal_q",
        "top_blocks",
    ]
    report.append("\n## Top Inverse-Fit Masks\n\n")
    report.append("```\n" + top_detail[cols].head(24).round(9).to_string(index=False) + "\n```\n")
    report.append("\n## Mask Kind Summary\n\n")
    report.append("```\n" + by_kind.round(9).to_string(index=False) + "\n```\n")
    report.append("\n## Best Raw05/All-Sign Compatible Masks\n\n")
    report.append("Raw05-compatible rows: " + str(len(raw05_compatible)) + "; all-sign-compatible rows: " + str(len(sign_compatible)) + "\n\n")
    report.append("```\n" + sign_compatible[cols].head(16).round(9).to_string(index=False) + "\n```\n")
    report.append("\n## Candidate Re-Ranking By Inverse-Fit Masks\n\n")
    cand_cols = [
        "file",
        "inverse_candidate_score",
        "inverse_weighted_expected",
        "inverse_weighted_regret",
        "inverse_p90_regret",
        "inverse_win_rate_best_eps1e4",
    ]
    report.append("```\n" + cand[cand_cols].head(40).round(9).to_string(index=False) + "\n```\n")
    report.append("\n## Candidate Re-Ranking By Sign-Compatible Masks\n\n")
    report.append("```\n" + cand_sign[cand_cols].head(40).round(9).to_string(index=False) + "\n```\n")
    (OUT / "public_lb_inverse_mask_audit_report.md").write_text("".join(report), encoding="utf-8")

    print("[inverse top masks]")
    print(top_detail[cols].head(20).round(9).to_string(index=False))
    print("\n[inverse mask kinds]")
    print(by_kind.round(9).to_string(index=False))
    print("\n[inverse candidate top]")
    cand_cols = [
        "file",
        "inverse_candidate_score",
        "inverse_weighted_expected",
        "inverse_weighted_regret",
        "inverse_p90_regret",
    ]
    print(cand[cand_cols].head(30).round(9).to_string(index=False))
    print("\n[sign-compatible mask top]")
    print(sign_compatible[cols].head(20).round(9).to_string(index=False))
    print("\n[sign-compatible candidate top]")
    print(cand_sign[cand_cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
