from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
import public_lb_direct_label_robust_selector as robust  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, read_submission  # noqa: E402


CELL_IN = OUT / "public_lb_direct_label_inverse7_cell_solutions.parquet"
CONSENSUS_OUT = OUT / "public_lb_direct_label_consensus_energy_cells.csv"
SCAN_OUT = OUT / "public_lb_direct_label_consensus_energy_scan.csv"
SELECTED_OUT = OUT / "public_lb_direct_label_consensus_energy_selected.csv"
ANCHOR_OUT = OUT / "public_lb_direct_label_consensus_energy_actual_anchor.csv"
REPORT_OUT = OUT / "public_lb_direct_label_consensus_energy_report.md"


TARGET_MASKS = {
    "all": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_q3_s1_s3": ["Q1", "Q3", "S1", "S3"],
    "q1_s1_s3": ["Q1", "S1", "S3"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
}

GATES = {
    "energy_strict": {"min_count": 4, "min_weight": 0.070, "min_agree": 0.72, "min_abs_logit": 0.030, "max_std": 0.35},
    "energy_balanced": {"min_count": 3, "min_weight": 0.045, "min_agree": 0.67, "min_abs_logit": 0.025, "max_std": 0.45},
    "energy_broad": {"min_count": 2, "min_weight": 0.030, "min_agree": 0.62, "min_abs_logit": 0.020, "max_std": 0.55},
    "energy_structured": {"min_count": 2, "min_structured_weight": 0.018, "min_agree": 0.63, "min_abs_logit": 0.020, "max_std": 0.55},
    "energy_large": {"min_count": 3, "min_weight": 0.040, "min_agree": 0.70, "min_abs_logit": 0.045, "max_std": 0.50},
}

STRENGTHS = [0.45, 0.65, 0.85, 1.10]
CAPS = [0.018, 0.030, 0.045, 0.060]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    total = float(weights.sum())
    if total <= 0:
        return float("nan")
    return float(np.dot(values, weights) / total)


def build_consensus(sample: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    cells = pd.read_parquet(CELL_IN)
    top = sources[
        (sources["loocv_mae"] <= 0.00095)
        & (sources["l2o_mae"] <= 0.00080)
        & (sources["robust_source_score"] <= sources["robust_source_score"].quantile(0.45))
    ].copy()
    top = top.sort_values(["robust_source_score", "l2o_mae"]).head(42).copy()
    top["source_rank"] = np.arange(len(top))
    tau = max(0.0020, float(top["robust_source_score"].median()))
    top["source_weight"] = np.exp(-top["robust_source_score"] / tau)
    top["source_weight"] = top["source_weight"] / top["source_weight"].sum()
    top["structured_weight"] = top["source_weight"] * (top["mask_kind"] != "random_rows").astype(float)

    keep_cols = [
        "solution_id",
        "mask_index",
        "mask_kind",
        "mask_name",
        "prior_name",
        "source_rank",
        "source_weight",
        "structured_weight",
        "robust_source_score",
        "loocv_mae",
        "l2o_mae",
    ]
    joined = cells.merge(top[keep_cols], on=["solution_id", "mask_index"], how="inner")
    joined["base_prob"] = joined["a2c8_prob"].astype(float)
    joined["pseudo_y"] = joined["pseudo_y"].clip(0.02, 0.98)
    joined["logit_delta"] = inv.logit(joined["pseudo_y"].to_numpy()) - inv.logit(joined["base_prob"].to_numpy())
    joined["direction"] = np.sign(joined["logit_delta"]).astype(int)
    joined["abs_logit_delta"] = np.abs(joined["logit_delta"])

    rows: list[dict[str, object]] = []
    for (row_index, target), group in joined.groupby(["row_index", "target"], sort=False):
        weights = group["source_weight"].to_numpy(dtype=float)
        structured_weights = group["structured_weight"].to_numpy(dtype=float)
        deltas = group["logit_delta"].to_numpy(dtype=float)
        pseudo = group["pseudo_y"].to_numpy(dtype=float)
        base = float(group["base_prob"].iloc[0])
        total_w = float(weights.sum())
        if total_w <= 0:
            continue
        mean_delta = weighted_mean(deltas, weights)
        mean_pseudo = weighted_mean(pseudo, weights)
        var = weighted_mean((deltas - mean_delta) ** 2, weights)
        std_delta = float(np.sqrt(max(var, 0.0)))
        up_w = float(weights[deltas > 0].sum())
        down_w = float(weights[deltas < 0].sum())
        agree_w = max(up_w, down_w) / total_w
        sign = 1 if up_w >= down_w else -1
        signed_strength = abs(mean_delta) / (std_delta + 0.060)
        energy = agree_w * np.sqrt(total_w) * signed_strength
        subj = str(sample.loc[int(row_index), "subject_id"])
        rows.append(
            {
                "row_index": int(row_index),
                "subject_id": subj,
                "target": str(target),
                "base_prob": base,
                "consensus_pseudo_y": mean_pseudo,
                "mean_logit_delta": mean_delta,
                "std_logit_delta": std_delta,
                "abs_mean_logit_delta": abs(mean_delta),
                "direction": sign,
                "source_count": int(len(group)),
                "unique_mask_count": int(group["mask_index"].nunique()),
                "weight_sum": total_w,
                "structured_weight_sum": float(structured_weights.sum()),
                "agreement_weight": agree_w,
                "up_weight": up_w,
                "down_weight": down_w,
                "consensus_energy": energy,
                "mean_source_l2o": float(np.dot(group["l2o_mae"].to_numpy(dtype=float), weights) / total_w),
                "mean_source_loo": float(np.dot(group["loocv_mae"].to_numpy(dtype=float), weights) / total_w),
                "top_masks": ";".join(group.sort_values("source_weight", ascending=False)["mask_name"].astype(str).head(4).tolist()),
            }
        )
    consensus = pd.DataFrame(rows)
    consensus = consensus.sort_values(["consensus_energy", "abs_mean_logit_delta"], ascending=[False, False]).reset_index(drop=True)
    return consensus


def gate_mask(consensus: pd.DataFrame, gate_name: str, target_mask: str) -> pd.Series:
    cfg = GATES[gate_name]
    targets = set(TARGET_MASKS[target_mask])
    keep = consensus["target"].isin(targets)
    keep &= consensus["source_count"] >= cfg.get("min_count", 1)
    keep &= consensus["agreement_weight"] >= cfg["min_agree"]
    keep &= consensus["abs_mean_logit_delta"] >= cfg["min_abs_logit"]
    keep &= consensus["std_logit_delta"] <= cfg["max_std"]
    if "min_weight" in cfg:
        keep &= consensus["weight_sum"] >= cfg["min_weight"]
    if "min_structured_weight" in cfg:
        keep &= consensus["structured_weight_sum"] >= cfg["min_structured_weight"]
    return keep


def make_candidate(base: np.ndarray, consensus: pd.DataFrame, gate_name: str, target_mask: str, strength: float, cap: float) -> tuple[str, np.ndarray, dict[str, float]]:
    pred = base.copy()
    keep = gate_mask(consensus, gate_name, target_mask)
    cells = consensus.loc[keep].copy()
    if cells.empty:
        label = f"{gate_name}|{target_mask}|empty"
        return label, pred, {"cell_count": 0}
    row_idx = cells["row_index"].to_numpy(dtype=int)
    target_idx = cells["target"].map({t: i for i, t in enumerate(inv.TARGETS)}).to_numpy(dtype=int)
    old = pred[row_idx, target_idx]
    energy_scale = np.clip(cells["consensus_energy"].to_numpy(dtype=float) / 0.40, 0.35, 1.35)
    ldelta = cells["mean_logit_delta"].to_numpy(dtype=float)
    moved = inv.sigmoid(inv.logit(old) + strength * energy_scale * ldelta)
    delta = np.clip(moved - old, -cap, cap)
    pred[row_idx, target_idx] = inv.clip_prob(old + delta)
    label = f"{gate_name}|{target_mask}|s{strength:.3f}|c{cap:.3f}|n{len(cells)}"
    meta = {
        "cell_count": int(len(cells)),
        "row_count": int(cells["row_index"].nunique()),
        "mean_energy": float(cells["consensus_energy"].mean()),
        "mean_agreement": float(cells["agreement_weight"].mean()),
        "mean_abs_logit_delta": float(cells["abs_mean_logit_delta"].mean()),
        "mean_source_l2o": float(cells["mean_source_l2o"].mean()),
    }
    return label, pred, meta


def score_candidates(sample: pd.DataFrame, consensus: pd.DataFrame, sources: pd.DataFrame, solution_map: dict[str, robust.Solution], preds: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    base = preds["cvjepa_a2c8"]
    raw05 = preds["raw05"]
    stage2 = preds["stage2"]
    ensemble, weights = robust.solution_ensemble(sources, solution_map, limit=44)
    a2_scores = np.asarray([robust.score_under_solution(sol, base, stage2) for sol in ensemble])

    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {"control_a2c8": base, "control_raw05": raw05}
    for gate_name in GATES:
        for target_mask in TARGET_MASKS:
            for strength in STRENGTHS:
                for cap in CAPS:
                    label, pred, meta = make_candidate(base, consensus, gate_name, target_mask, strength, cap)
                    if meta.get("cell_count", 0) == 0:
                        continue
                    name = f"directcons_{stable_hash(label)}"
                    predictions[name] = pred
                    rec = {
                        "name": name,
                        "label": label,
                        "file": f"submission_directcons_{stable_hash(label)}.csv",
                        "gate": gate_name,
                        "target_mask": target_mask,
                        "strength": strength,
                        "cap": cap,
                    }
                    rec.update(meta)
                    records.append(rec)
    meta = pd.DataFrame(records)

    score_rows = []
    for name, pred in predictions.items():
        scores = np.asarray([robust.score_under_solution(sol, pred, stage2) for sol in ensemble])
        delta = scores - a2_scores
        rec = {
            "name": name,
            "robust_expected_public": float(weights @ scores),
            "robust_delta_vs_a2c8": float(weights @ delta),
            "robust_p10_delta_vs_a2c8": float(np.quantile(delta, 0.10)),
            "robust_p50_delta_vs_a2c8": float(np.quantile(delta, 0.50)),
            "robust_p90_delta_vs_a2c8": float(np.quantile(delta, 0.90)),
            "robust_worst_delta_vs_a2c8": float(np.max(delta)),
            "robust_win_rate_vs_a2c8": float(np.mean(delta < 0.0)),
        }
        rec.update(robust.geometric_features(pred, base, raw05))
        score_rows.append(rec)
    scan = meta.merge(pd.DataFrame(score_rows), on="name", how="left")
    scan["selection_score"] = (
        scan["robust_delta_vs_a2c8"]
        + 0.85 * np.maximum(scan["robust_p90_delta_vs_a2c8"], 0.0)
        + 0.35 * np.maximum(scan["robust_worst_delta_vs_a2c8"], 0.0)
        + 0.10 * scan["mean_source_l2o"]
        - 0.0015 * np.minimum(scan["mean_abs_move_vs_a2c8"] / 0.004, 1.4)
        - 0.0010 * np.minimum(scan["logit_orth_ratio_to_a2c8_move"].fillna(0.0), 1.0)
    )
    scan = scan.sort_values(["selection_score", "robust_delta_vs_a2c8"]).reset_index(drop=True)

    selected_rows: list[dict[str, object]] = []
    used: set[str] = set()
    specs = [
        ("consensus_first", scan[(scan["mean_abs_move_vs_a2c8"].between(0.0018, 0.0042)) & (scan["robust_p90_delta_vs_a2c8"] <= 0.00012)], 8),
        ("consensus_strict", scan[(scan["gate"] == "energy_strict") & (scan["robust_p90_delta_vs_a2c8"] <= 0.00016)], 6),
        ("consensus_large", scan[(scan["mean_abs_move_vs_a2c8"] >= 0.0037) & (scan["robust_p90_delta_vs_a2c8"] <= 0.00020)], 8),
        ("consensus_structured", scan[(scan["gate"] == "energy_structured") & (scan["robust_p90_delta_vs_a2c8"] <= 0.00018)], 6),
    ]
    for role, frame, limit in specs:
        seen_keys: set[tuple[object, object, object]] = set()
        for row in frame.itertuples(index=False):
            key = (getattr(row, "gate", ""), getattr(row, "target_mask", ""), getattr(row, "strength", np.nan))
            if key in seen_keys or str(row.name) in used:
                continue
            seen_keys.add(key)
            used.add(str(row.name))
            selected_rows.append({**row._asdict(), "submit_role": role})
            if len([r for r in selected_rows if r["submit_role"] == role]) >= limit:
                break
    selected = pd.DataFrame(selected_rows)
    if not selected.empty:
        for row in selected.itertuples(index=False):
            out = sample.copy()
            out[inv.TARGETS] = inv.clip_prob(predictions[str(row.name)])
            out.to_csv(OUT / str(row.file), index=False)
    return scan, selected, predictions


def actual_anchor_for_selected(sample: pd.DataFrame, selected: pd.DataFrame, predictions: dict[str, np.ndarray]) -> pd.DataFrame:
    files = ["submission_frontier_cvjepa_refine_a2c8d2c8.csv", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"]
    names = ["control_a2c8", "control_raw05"]
    preds = [read_submission(file_name)[inv.TARGETS].to_numpy(dtype=float) for file_name in files]
    if not selected.empty:
        for row in selected.itertuples(index=False):
            names.append(str(row.name))
            files.append(str(row.file))
            preds.append(predictions[str(row.name)])
    scored = actual_anchor_score(preds, sample)
    scored["name"] = names
    scored["file"] = files
    if not selected.empty:
        scored = scored.merge(
            selected[
                [
                    "name",
                    "submit_role",
                    "gate",
                    "target_mask",
                    "strength",
                    "cap",
                    "cell_count",
                    "mean_energy",
                    "robust_delta_vs_a2c8",
                    "mean_abs_move_vs_a2c8",
                ]
            ],
            on="name",
            how="left",
        )
    return scored.sort_values("actual_anchor_score_final").reset_index(drop=True)


def write_report(consensus: pd.DataFrame, scan: pd.DataFrame, selected: pd.DataFrame, anchor: pd.DataFrame) -> None:
    ccols = [
        "row_index",
        "subject_id",
        "target",
        "base_prob",
        "consensus_pseudo_y",
        "mean_logit_delta",
        "std_logit_delta",
        "source_count",
        "weight_sum",
        "structured_weight_sum",
        "agreement_weight",
        "consensus_energy",
        "mean_source_l2o",
        "top_masks",
    ]
    scols = [
        "submit_role",
        "file",
        "gate",
        "target_mask",
        "strength",
        "cap",
        "cell_count",
        "mean_energy",
        "mean_agreement",
        "mean_source_l2o",
        "selection_score",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "robust_worst_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    acols = [
        "file",
        "submit_role",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "gate",
        "target_mask",
        "strength",
        "cap",
        "cell_count",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    report = [
        "# Direct-Label Consensus Energy",
        "",
        "This aggregates robust direct-label pseudo labels across LOO/L2O-stable source masks and moves only cells with high cross-source directional agreement.",
        "",
        "## Top Consensus Cells",
        "",
        "```",
        consensus[ccols].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Consensus Submissions",
        "",
        "```",
        selected[scols].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Actual-Anchor Stress",
        "",
        "```",
        anchor[acols].head(30).round(9).to_string(index=False),
        "```",
        "",
        "## Candidate Scan Top",
        "",
        "```",
        scan[["name", "file", "gate", "target_mask", "strength", "cap", "cell_count", "selection_score", "robust_delta_vs_a2c8", "robust_p90_delta_vs_a2c8", "mean_abs_move_vs_a2c8"]].head(70).round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- Consensus energy is a LeJEPA-style regularizer: high agreement and low dispersion across hidden-label solutions means lower latent energy.",
        "- The branch is less sensitive to a single public-mask assumption, but it may move fewer cells than the single-source directrob branch.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(inv.KEY).reset_index(drop=True)
    sources, solution_map = robust.load_sources()
    preds = inv.load_predictions(sample)
    consensus = build_consensus(sample, sources)
    consensus.to_csv(CONSENSUS_OUT, index=False)
    scan, selected, predictions = score_candidates(sample, consensus, sources, solution_map, preds)
    scan.to_csv(SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    anchor = actual_anchor_for_selected(sample, selected, predictions)
    anchor.to_csv(ANCHOR_OUT, index=False)
    write_report(consensus, scan, selected, anchor)

    print(REPORT_OUT)
    print("[consensus]")
    print(
        consensus[
            [
                "row_index",
                "subject_id",
                "target",
                "source_count",
                "weight_sum",
                "agreement_weight",
                "mean_logit_delta",
                "std_logit_delta",
                "consensus_energy",
                "mean_source_l2o",
                "top_masks",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )
    print("[selected]")
    if selected.empty:
        print("none")
    else:
        print(
            selected[
                [
                    "submit_role",
                    "file",
                    "gate",
                    "target_mask",
                    "strength",
                    "cap",
                    "cell_count",
                    "robust_delta_vs_a2c8",
                    "robust_p90_delta_vs_a2c8",
                    "mean_abs_move_vs_a2c8",
                ]
            ]
            .head(30)
            .round(9)
            .to_string(index=False)
        )
    print("[actual-anchor]")
    print(
        anchor[
            [
                "file",
                "submit_role",
                "actual_anchor_score_final",
                "gate",
                "target_mask",
                "strength",
                "cap",
                "robust_delta_vs_a2c8",
                "mean_abs_move_vs_a2c8",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
