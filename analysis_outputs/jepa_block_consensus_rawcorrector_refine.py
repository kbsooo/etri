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
from jepa_block_consensus_rawcorrector import (  # noqa: E402
    build_consensus_maps,
    exists,
    logit_blend,
    reconstruct_prediction,
    score_record,
)
from jepa_energy_ensemble_optimizer import candidate_key, public_axes  # noqa: E402
from jepa_public_minimax_rawsafe_bridge import (  # noqa: E402
    focused_reference_components,
    integrity,
    normalized_compact_masks,
    save_submission,
)
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


COUNTERS = [
    "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p875_f5e1e1c0.csv",
]
ANCHORS = [
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
]
COUNTER_GRID = np.round(np.arange(0.10, 0.221, 0.01), 3)
ANCHOR_GRID = np.round(np.arange(0.24, 0.501, 0.02), 3)


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    from jepa_block_consensus_gate import load_array as load_base_array

    return load_base_array(file_name, sample)


def select_rows(scan: pd.DataFrame, limit: int = 90) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 8.0e-8)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57686)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0020)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            34,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57688)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0020)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            28,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58207)
                & (scan["delta_vs_raw05_rawaxis"] <= 1.2e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57686)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            20,
        ),
        (
            scan.sort_values(["bridge_score", "compact_focused_score"]),
            8,
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
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    hidden_rates = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")
    pool = pd.read_csv(OUT / "jepa_block_consensus_rawcorrector_unsafe_pool.csv").head(10)

    block_ids = sample_block_ids(train, sample).astype(str)
    blocks = sorted(hidden_rates["hidden_block_id"].astype(str).unique())
    block_to_idx = {block_id: i for i, block_id in enumerate(blocks)}
    row_block_idx = np.asarray([block_to_idx[b] for b in block_ids], dtype=int)

    axes = public_axes()
    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    consensus_maps = build_consensus_maps(hidden_rates, summary, blocks)

    files = sorted(set(pool["base_file"].astype(str)) | set(COUNTERS) | set(ANCHORS))
    arrays = {file_name: load_array(file_name, sample) for file_name in files if exists(file_name)}

    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}
    seen_hash: set[str] = set()

    def add(label: str, pred: np.ndarray, meta: dict[str, object]) -> None:
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
        for counter_file in COUNTERS:
            if counter_file not in arrays:
                continue
            for cw in COUNTER_GRID:
                corrected = logit_blend(unsafe, arrays[counter_file], float(cw))
                for anchor_file in ANCHORS:
                    if anchor_file not in arrays:
                        continue
                    for aw in ANCHOR_GRID:
                        pred = logit_blend(corrected, arrays[anchor_file], float(aw))
                        label = f"refine|{i}|{Path(counter_file).stem}|cw{cw:.3f}|{Path(anchor_file).stem}|aw{aw:.3f}"
                        add(
                            label,
                            pred,
                            {
                                "source": "rawcounter_anchor_refine",
                                "unsafe_rank": i,
                                "base_file": base_file,
                                "counter_file": counter_file,
                                "anchor_file": anchor_file,
                                "weight_counter": float(cw),
                                "weight_anchor": float(aw),
                                "method_set": row["method_set"],
                                "aggregate": row["aggregate"],
                                "target_mask": row["target_mask"],
                                "gate": row["gate"],
                                "gamma": float(row["gamma"]),
                                "cap": float(row["cap"]),
                            },
                        )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_block_consensus_rawcorr_refine_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_focused_scenario.csv", index=False)
    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_block_consensus_rawcorrector_refine_shortlist.csv", index=False)
    (OUT / "jepa_block_consensus_rawcorrector_refine_report.md").write_text(
        "# JEPA Block Consensus Raw-Corrector Refine\n\n"
        + shortlist.head(40).round(10).to_csv(index=False),
        encoding="utf-8",
    )

    cols = [
        "file",
        "unsafe_rank",
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
    print(f"scan={len(scan)} saved={len(saved_files)} pool={len(pool)}")
    print(shortlist[cols].head(24).to_string(index=False))


if __name__ == "__main__":
    main()
