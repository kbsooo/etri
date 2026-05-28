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

from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sample_block_ids, sigmoid, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from jepa_block_consensus_gate import (  # noqa: E402
    TARGET_MASKS,
    aggregate_logits,
    build_gates,
    collect_method_sets,
    load_array,
    method_tensor,
    score_record,
    target_mask_matrix,
)
from jepa_energy_ensemble_optimizer import candidate_key, public_axes, read_any  # noqa: E402
from jepa_public_minimax_rawsafe_bridge import (  # noqa: E402
    bridge_score,
    compact_focused_score,
    focused_reference_components,
    integrity,
    normalized_compact_masks,
    save_submission,
)
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


RAW_COUNTERS = [
    "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p875_f5e1e1c0.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale1p0.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
]

ANCHOR_PULLS = [
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
]

COUNTER_WEIGHTS = [0.16, 0.20, 0.24, 0.28, 0.32, 0.36, 0.42, 0.50, 0.60]
ANCHOR_WEIGHTS = [0.10, 0.16, 0.22, 0.30, 0.40]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def logit_blend(a: np.ndarray, b: np.ndarray, weight_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight_b) * logit(a) + weight_b * logit(b)))


def unsafe_pool(scan: pd.DataFrame) -> pd.DataFrame:
    pool = scan[
        scan["source"].eq("consensus_gate")
        & (scan["base_file"].eq("submission_jepa_bridge_ensemble_86c6c9d1.csv"))
        & (scan["target_mask"].isin(["no_q2", "q3_s2_s3_s4"]))
        & (scan["gate"].eq("energy_consensus"))
        & (scan["compact_focused_score"] <= 0.58205)
        & (scan["posterior_expected_public_vs_anchor"] <= 0.57682)
        & (scan["delta_vs_raw05_rawaxis"] > 1.0e-6)
        & (scan["bad_residual_axis_ratio"].abs() <= 0.0023)
    ].copy()
    if pool.empty:
        pool = scan[
            scan["source"].eq("consensus_gate")
            & (scan["compact_focused_score"] <= 0.58210)
            & (scan["posterior_expected_public_vs_anchor"] <= 0.57686)
            & (scan["delta_vs_raw05_rawaxis"] > 1.0e-6)
            & (scan["bad_residual_axis_ratio"].abs() <= 0.0032)
        ].copy()
    pool = pool.sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]).drop_duplicates(
        ["base_file", "method_set", "aggregate", "target_mask", "gate", "gamma", "cap"]
    )
    return pool.head(48).reset_index(drop=True)


def build_consensus_maps(
    hidden_rates: pd.DataFrame,
    summary: pd.DataFrame,
    blocks: list[str],
) -> dict[tuple[str, str], dict[str, np.ndarray]]:
    out: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for set_name, methods in collect_method_sets(summary).items():
        tensor, weights, _kept = method_tensor(hidden_rates, summary, methods, blocks)
        for agg in ["weighted", "median"]:
            center, spread = aggregate_logits(tensor, weights, agg)
            out[(set_name, agg)] = {
                "center": center,
                "spread": spread,
                "tensor_logits": logit(tensor),
            }
    return out


def reconstruct_prediction(
    row: pd.Series,
    base: np.ndarray,
    row_block_idx: np.ndarray,
    consensus_maps: dict[tuple[str, str], dict[str, np.ndarray]],
    axes: dict[str, np.ndarray | float],
) -> np.ndarray:
    key = (str(row["method_set"]), str(row["aggregate"]))
    if key not in consensus_maps:
        raise KeyError(key)
    spec = consensus_maps[key]
    base_logit = logit(base)
    center = np.asarray(spec["center"], dtype=np.float64)[row_block_idx]
    spread = np.asarray(spec["spread"], dtype=np.float64)[row_block_idx]
    method_logits = np.asarray(spec["tensor_logits"], dtype=np.float64)[row_block_idx]
    gates = build_gates(base_logit, center, method_logits, spread, axes)
    gate = gates[str(row["gate"])]
    tmask = target_mask_matrix(TARGET_MASKS[str(row["target_mask"])], len(base))
    capped = np.clip(center - base_logit, -float(row["cap"]), float(row["cap"]))
    return clip(sigmoid(base_logit + float(row["gamma"]) * tmask * gate * capped))


def select_rows(scan: pd.DataFrame, limit: int = 90) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57690)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0032)
                & (scan["compact_focused_score"] <= 0.58212)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            30,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 1.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57688)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0032)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            24,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58202)
                & (scan["delta_vs_raw05_rawaxis"] <= 3.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57695)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0035)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            24,
        ),
        (
            scan[
                (scan["posterior_expected_public_vs_anchor"] <= 0.57678)
                & (scan["delta_vs_raw05_rawaxis"] <= 5.0e-7)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0035)
            ].sort_values(["posterior_expected_public_vs_anchor", "compact_focused_score"]),
            12,
        ),
    ]
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for frame, quota in buckets:
        added = 0
        for rec in frame.itertuples(index=False):
            h = str(rec.prediction_hash)
            if h in seen:
                continue
            rows.append(rec._asdict())
            seen.add(h)
            added += 1
            if added >= quota or len(rows) >= limit:
                break
        if len(rows) >= limit:
            break
    if not rows:
        return scan.sort_values(["bridge_score", "compact_focused_score"]).head(limit)
    return pd.DataFrame(rows)


def write_report(pool: pd.DataFrame, selected: pd.DataFrame, proxy: pd.DataFrame, focused: pd.DataFrame, shortlist: pd.DataFrame) -> None:
    lines = [
        "# JEPA Block Consensus Raw-Corrector",
        "",
        "Goal: rescue high-upside consensus-gate candidates whose compact JEPA/public proxy improves but whose raw05 axis drifts positive.",
        "Method: reconstruct the unsafe consensus candidates, then logit-blend them with raw-counter anchors until raw05-axis compatibility is restored.",
        "",
        "## Unsafe Pool",
        "",
        "```csv",
        pool.head(24).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected Corrected Candidates",
        "",
        "```csv",
        selected.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact Focused Scenario",
        "",
        "```csv",
        focused.head(24).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        shortlist.head(30).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_block_consensus_rawcorrector_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    hidden_rates = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    scan = pd.read_csv(OUT / "jepa_block_consensus_gate_scan.csv")
    pool = unsafe_pool(scan)
    if pool.empty:
        raise RuntimeError("empty unsafe pool")
    pool.to_csv(OUT / "jepa_block_consensus_rawcorrector_unsafe_pool.csv", index=False)

    block_ids = sample_block_ids(train, sample).astype(str)
    blocks = sorted(hidden_rates["hidden_block_id"].astype(str).unique())
    block_to_idx = {block_id: i for i, block_id in enumerate(blocks)}
    row_block_idx = np.asarray([block_to_idx[b] for b in block_ids], dtype=int)

    axes = public_axes()
    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    consensus_maps = build_consensus_maps(hidden_rates, summary, blocks)

    files = sorted(set(pool["base_file"].astype(str)) | set(RAW_COUNTERS) | set(ANCHOR_PULLS))
    arrays = {file_name: load_array(file_name, sample) for file_name in files if exists(file_name)}
    counters = [file_name for file_name in RAW_COUNTERS if file_name in arrays]
    anchors = [file_name for file_name in ANCHOR_PULLS if file_name in arrays]
    if not counters:
        raise RuntimeError("missing raw counters")

    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}
    seen_hash: set[str] = set()

    def add_candidate(label: str, pred: np.ndarray, meta: dict[str, object]) -> None:
        pred = clip(pred)
        h = candidate_key(pred)
        if h in seen_hash:
            return
        seen_hash.add(h)
        predictions[label] = pred
        records.append(score_record(label, pred, q_arrays, best, weight_mat, axes, meta))

    for i, row in pool.iterrows():
        base_file = str(row["base_file"])
        unsafe = reconstruct_prediction(row, arrays[base_file], row_block_idx, consensus_maps, axes)
        unsafe_label = f"unsafe|{i}|{row['label']}"
        add_candidate(
            unsafe_label,
            unsafe,
            {
                "source": "unsafe_original",
                "unsafe_rank": i,
                "base_file": base_file,
                "counter_file": "",
                "anchor_file": "",
                "weight_counter": 0.0,
                "weight_anchor": 0.0,
                "method_set": row["method_set"],
                "aggregate": row["aggregate"],
                "target_mask": row["target_mask"],
                "gate": row["gate"],
                "gamma": float(row["gamma"]),
                "cap": float(row["cap"]),
            },
        )
        for counter_file in counters:
            counter = arrays[counter_file]
            for weight in COUNTER_WEIGHTS:
                corrected = logit_blend(unsafe, counter, weight)
                label = f"counter|{i}|{Path(counter_file).stem}|w{weight:.2f}|{row['label']}"
                add_candidate(
                    label,
                    corrected,
                    {
                        "source": "rawcounter_blend",
                        "unsafe_rank": i,
                        "base_file": base_file,
                        "counter_file": counter_file,
                        "anchor_file": "",
                        "weight_counter": weight,
                        "weight_anchor": 0.0,
                        "method_set": row["method_set"],
                        "aggregate": row["aggregate"],
                        "target_mask": row["target_mask"],
                        "gate": row["gate"],
                        "gamma": float(row["gamma"]),
                        "cap": float(row["cap"]),
                    },
                )
                for anchor_file in anchors:
                    anchor = arrays[anchor_file]
                    for aw in ANCHOR_WEIGHTS:
                        pred = logit_blend(corrected, anchor, aw)
                        label = f"counter_anchor|{i}|{Path(counter_file).stem}|cw{weight:.2f}|{Path(anchor_file).stem}|aw{aw:.2f}"
                        add_candidate(
                            label,
                            pred,
                            {
                                "source": "rawcounter_anchor_blend",
                                "unsafe_rank": i,
                                "base_file": base_file,
                                "counter_file": counter_file,
                                "anchor_file": anchor_file,
                                "weight_counter": weight,
                                "weight_anchor": aw,
                                "method_set": row["method_set"],
                                "aggregate": row["aggregate"],
                                "target_mask": row["target_mask"],
                                "gate": row["gate"],
                                "gamma": float(row["gamma"]),
                                "cap": float(row["cap"]),
                            },
                        )

    scan_out = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan_out.to_csv(OUT / "jepa_block_consensus_rawcorrector_scan.csv", index=False)
    selected = select_rows(scan_out)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_block_consensus_rawcorr_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_block_consensus_rawcorrector_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_block_consensus_rawcorrector_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_block_consensus_rawcorrector_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_block_consensus_rawcorrector_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_block_consensus_rawcorrector_shortlist.csv", index=False)
    write_report(pool, selected, proxy, focused, shortlist)

    cols = [
        "file",
        "source",
        "base_file",
        "counter_file",
        "anchor_file",
        "weight_counter",
        "weight_anchor",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "compact_focused_score",
    ]
    print(f"unsafe={len(pool)} scan={len(scan_out)} saved={len(saved_files)} counters={len(counters)} anchors={len(anchors)}")
    print(shortlist[cols].head(24).to_string(index=False))


if __name__ == "__main__":
    main()
