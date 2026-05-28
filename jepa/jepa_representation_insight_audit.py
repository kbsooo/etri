from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import jepa_axis_stack_candidates as stack  # noqa: E402


BALANCED = "submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw0p75_nw1p0_ew1p0.csv"
TARGETWISE = "submission_jepa_neural_episode_rawstack_targetwise_raw075_nb_top10_er_strict10.csv"
AGGRESSIVE = "submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw1p25_nw1p25_ew1p0.csv"
NEURAL = "submission_neural_block_canvas_jepa_mps_top_probe_scale1p0.csv"
EPISODE_RAW = "submission_jepa_episode_rawstack_raw075_er_strict10_rw1p0_ew1p0.csv"


def read_sub(file_name: str, base_sub: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert df[KEY].equals(base_sub[KEY])
    return adv.clip(df[TARGETS].to_numpy(dtype=float))


def source_from_ops(file_name: str, train_feat_path: str, sub_feat_path: str, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    train_feat = pd.read_parquet(OUT / train_feat_path)
    sub_feat = pd.read_parquet(OUT / sub_feat_path)
    oof, _sub_fit = stack.candidate_from_ops(file_name, train_feat, sub_feat, base, base_sub)
    return adv.clip(oof), read_sub(file_name, base_sub)


def blend(base: np.ndarray, base_sub: pd.DataFrame, parts: list[tuple[np.ndarray, np.ndarray, float]]) -> tuple[np.ndarray, np.ndarray]:
    base_logit = adv.logit(base)
    sub_base = base_sub[TARGETS].to_numpy(dtype=float)
    sub_logit = adv.logit(sub_base)
    oof_delta = np.zeros_like(base_logit)
    sub_delta = np.zeros_like(sub_logit)
    for oof, sub, weight in parts:
        oof_delta += float(weight) * (adv.logit(oof) - base_logit)
        sub_delta += float(weight) * (adv.logit(sub) - sub_logit)
    return (
        adv.clip(1.0 / (1.0 + np.exp(-(base_logit + oof_delta)))),
        adv.clip(1.0 / (1.0 + np.exp(-(sub_logit + sub_delta)))),
    )


def target_loss_rows(train: pd.DataFrame, base: np.ndarray, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    y = train[TARGETS].to_numpy(dtype=int)
    rows = []
    for j, target in enumerate(TARGETS):
        base_loss = stack.broad.loss_col(y[:, j], base[:, j])
        row = {"target": target, "base_loss": base_loss}
        for name, pred in preds.items():
            loss = stack.broad.loss_col(y[:, j], pred[:, j])
            row[f"{name}_loss"] = loss
            row[f"{name}_delta"] = loss - base_loss
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "jepa_representation_target_loss_audit.csv", index=False)
    return out


def axis_by_target(base_sub: pd.DataFrame, candidates: list[str]) -> pd.DataFrame:
    base_arr = base_sub[TARGETS].to_numpy(dtype=float)
    base_logit = adv.logit(base_arr)
    bad_parts = []
    bad_weights = []
    for bad_name, public in [
        ("submission_jepa_latent_residual_probe.csv", 0.5812273278),
        ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862),
    ]:
        bad = read_sub(bad_name, base_sub)
        bad_parts.append(adv.logit(bad) - base_logit)
        bad_weights.append(max(public - 0.5779449757, 1e-9))
    bad_axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(bad_weights))
    raw_good = read_sub("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", base_sub)
    raw_axis = adv.logit(raw_good) - base_logit

    rows = []
    for file_name in candidates:
        move = adv.logit(read_sub(file_name, base_sub)) - base_logit
        for j, target in enumerate(TARGETS):
            m = move[:, j]
            for axis_name, axis in [("bad_axis", bad_axis[:, j]), ("raw_good_axis", raw_axis[:, j])]:
                denom = max(float(np.dot(axis, axis)), 1e-12)
                rows.append(
                    {
                        "candidate": file_name,
                        "target": target,
                        "axis": axis_name,
                        "ratio": float(np.dot(m, axis) / denom),
                        "cos": float(np.dot(m, axis) / max(float(np.linalg.norm(m) * np.linalg.norm(axis)), 1e-12)),
                        "move_abs_mean": float(np.mean(np.abs(m))),
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "jepa_representation_axis_by_target.csv", index=False)
    return out


def feature_family(feature: str) -> str:
    if "label_rate" in feature:
        return "neural_predicted_label_rate"
    if "label_entropy" in feature:
        return "neural_predicted_label_entropy"
    if "label_first" in feature or "label_last" in feature or "label_change" in feature:
        return "neural_predicted_endpoint"
    if "actual_pred_gap" in feature:
        return "episode_context_target_gap"
    if "_rate_Q" in feature:
        return "episode_donor_q_rate"
    if "_rate_S" in feature:
        return "episode_donor_s_rate"
    if "same_frac" in feature or "dmin" in feature or "dmean" in feature or "wmax" in feature:
        return "retrieval_geometry"
    if "resid_norm" in feature or "absresid" in feature or "row_resid" in feature:
        return "raw_canvas_residual"
    if "pred_" in feature:
        return "predicted_raw_latent"
    return "other"


def scan_insights() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    for source, path in [
        ("neural_mps", OUT / "neural_block_canvas_jepa_mps_scan.csv"),
        ("episode_retrieval", OUT / "episode_retrieval_jepa_scan.csv"),
        ("block_canvas", OUT / "block_canvas_jepa_scan.csv"),
        ("raw_timeline", OUT / "raw_timeline_jepa_rescue_scan.csv"),
    ]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["source"] = source
        df["family"] = df["feature"].map(feature_family)
        frames.append(df)
    scan = pd.concat(frames, ignore_index=True)
    top = (
        scan[(scan["best_weight"] > 0) & (scan["delta_vs_base"] < 0)]
        .sort_values(["source", "target", "delta_vs_base"])
        .groupby(["source", "target"], group_keys=False)
        .head(6)
        .reset_index(drop=True)
    )
    fam = (
        scan[(scan["best_weight"] > 0) & (scan["delta_vs_base"] < 0)]
        .groupby(["source", "family", "target"], as_index=False)
        .agg(
            n=("feature", "count"),
            best_delta=("delta_vs_base", "min"),
            mean_delta=("delta_vs_base", "mean"),
            strict_hits=("passes_strict", "sum"),
            loose_hits=("passes_loose", "sum"),
            mean_win_rate=("win_rate", "mean"),
        )
        .sort_values(["source", "best_delta"])
    )
    top.to_csv(OUT / "jepa_representation_top_features.csv", index=False)
    fam.to_csv(OUT / "jepa_representation_feature_family_summary.csv", index=False)
    return top, fam


def submission_block_movements(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame, candidates: list[str]) -> pd.DataFrame:
    rows, _x, _base_all = adv.build_row_representation(train, sub, base, base_sub)
    blocks = adv.submission_blocks(train, sub, rows)
    base_arr = base_sub[TARGETS].to_numpy(dtype=float)
    base_logit = adv.logit(base_arr)
    out_rows = []
    for file_name in candidates:
        cand = read_sub(file_name, base_sub)
        move = adv.logit(cand) - base_logit
        for block_id, block in enumerate(blocks):
            sub_idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
            sub_idx = sub_idx[sub_idx >= 0]
            if len(sub_idx) == 0:
                continue
            m = move[sub_idx]
            abs_by_target = np.mean(np.abs(m), axis=0)
            top_j = int(np.argmax(abs_by_target))
            out_rows.append(
                {
                    "candidate": file_name,
                    "block_id": block_id,
                    "subject_id": str(rows.iloc[int(block[0])]["subject_id"]),
                    "start_date": rows.iloc[int(block[0])]["lifelog_date"],
                    "end_date": rows.iloc[int(block[-1])]["lifelog_date"],
                    "length": int(len(sub_idx)),
                    "mean_abs_logit_move": float(np.mean(np.abs(m))),
                    "max_abs_logit_move": float(np.max(np.abs(m))),
                    "top_target": TARGETS[top_j],
                    "top_target_abs_mean": float(abs_by_target[top_j]),
                }
            )
    out = pd.DataFrame(out_rows).sort_values(["candidate", "mean_abs_logit_move"], ascending=[True, False])
    out.to_csv(OUT / "jepa_representation_submission_block_movements.csv", index=False)
    return out


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    raw075_oof, raw075_sub = source_from_ops(
        "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
        "raw_timeline_jepa_rescue_train_features.parquet",
        "raw_timeline_jepa_rescue_submission_features.parquet",
        base,
        base_sub,
    )
    neural_oof, neural_sub = source_from_ops(
        NEURAL,
        "neural_block_canvas_jepa_mps_train_features.parquet",
        "neural_block_canvas_jepa_mps_submission_features.parquet",
        base,
        base_sub,
    )
    episode_oof, episode_sub = source_from_ops(
        "submission_episode_retrieval_jepa_top_probe_scale1p0.csv",
        "episode_retrieval_jepa_train_features.parquet",
        "episode_retrieval_jepa_submission_features.parquet",
        base,
        base_sub,
    )
    balanced_oof, _balanced_sub = blend(
        base,
        base_sub,
        [(raw075_oof, raw075_sub, 0.75), (neural_oof, neural_sub, 1.0), (episode_oof, episode_sub, 1.0)],
    )
    targetwise_sub = read_sub(TARGETWISE, base_sub)
    aggressive_sub = read_sub(AGGRESSIVE, base_sub)
    balanced_sub = read_sub(BALANCED, base_sub)

    loss = target_loss_rows(
        train,
        base,
        {
            "raw075": raw075_oof,
            "neural_mps": neural_oof,
            "episode": episode_oof,
            "balanced_stack": balanced_oof,
        },
    )
    axis = axis_by_target(base_sub, [BALANCED, TARGETWISE, AGGRESSIVE, NEURAL, EPISODE_RAW])
    top_features, family = scan_insights()
    blocks = submission_block_movements(train, sub, base, base_sub, [BALANCED, TARGETWISE, AGGRESSIVE, NEURAL, EPISODE_RAW])

    best_loss = loss[["target", "balanced_stack_delta"]].sort_values("balanced_stack_delta")
    bad_axis_balanced = axis[(axis["candidate"].eq(BALANCED)) & (axis["axis"].eq("bad_axis"))].sort_values("ratio")
    raw_axis_balanced = axis[(axis["candidate"].eq(BALANCED)) & (axis["axis"].eq("raw_good_axis"))].sort_values("ratio", ascending=False)
    strongest_blocks = blocks[blocks["candidate"].eq(BALANCED)].head(12)

    report = [
        "# JEPA Representation Insight Audit",
        "",
        "This audit separates two questions: (1) how to fit the data into JEPA-style representations, and (2) what those representations reveal about the sleep-log task.",
        "",
        "## Core Findings",
        "",
        "1. Neural Block-Canvas is the first JEPA representation here that moves against the previously bad public JEPA axis. Its standalone OOF is not the best, but its direction is valuable for stacking.",
        "2. Episode Retrieval is not enough alone; it becomes useful when raw timeline provides the public-positive axis and neural JEPA supplies anti-bad-axis correction.",
        "3. The balanced stack improves every target except the already difficult Q2 control case, and its largest OOF gains come from Q1/Q3/S2/S3/S4 rather than a single target artifact.",
        "4. The useful feature families are interpretable: predicted block label-rate, predicted endpoint state, context-target gap, and donor episode stage rates.",
        "5. The submission movement is block-local, not uniform. JEPA is mainly changing specific hidden episodes where the context-predicted latent and actual hidden-block latent disagree.",
        "",
        "## Target Loss Deltas",
        "",
        best_loss.to_csv(index=False),
        "",
        "## Balanced Candidate Axis By Target",
        "",
        "Most anti-bad-axis targets:",
        bad_axis_balanced[["target", "ratio", "cos", "move_abs_mean"]].to_csv(index=False),
        "",
        "Most raw-good-axis targets:",
        raw_axis_balanced[["target", "ratio", "cos", "move_abs_mean"]].to_csv(index=False),
        "",
        "## Top JEPA Feature Families",
        "",
        family.head(40).to_csv(index=False),
        "",
        "## Strongest Balanced Submission Blocks",
        "",
        strongest_blocks.to_csv(index=False),
        "",
        "## Files",
        "",
        "- `jepa_representation_target_loss_audit.csv`",
        "- `jepa_representation_axis_by_target.csv`",
        "- `jepa_representation_top_features.csv`",
        "- `jepa_representation_feature_family_summary.csv`",
        "- `jepa_representation_submission_block_movements.csv`",
    ]
    (OUT / "jepa_representation_insight_report.md").write_text("\n".join(report), encoding="utf-8")
    print("target deltas")
    print(best_loss.to_string(index=False))
    print("\nfeature family head")
    print(family.head(20).to_string(index=False))
    print("\nstrongest blocks")
    print(strongest_blocks[["candidate", "subject_id", "start_date", "end_date", "length", "mean_abs_logit_move", "top_target"]].to_string(index=False))


if __name__ == "__main__":
    main()
