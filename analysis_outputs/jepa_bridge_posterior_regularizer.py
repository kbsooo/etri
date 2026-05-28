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

from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sigmoid, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from jepa_energy_ensemble_optimizer import candidate_key, public_axes, public_axis_features, read_any  # noqa: E402
from jepa_public_minimax_rawsafe_bridge import (  # noqa: E402
    bridge_score,
    compact_focused_score,
    focused_reference_components,
    integrity,
    normalized_compact_masks,
    save_submission,
)
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


BRIDGE_FILES = [
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_bridge_ensemble_86c6c9d1.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
    "submission_jepa_public_minimax_bridge_d1ca675f.csv",
    "submission_jepa_public_minimax_bridge_5653d800.csv",
    "submission_jepa_public_minimax_bridge_c15454a4.csv",
    "submission_jepa_public_minimax_bridge_12deef9a.csv",
    "submission_jepa_public_minimax_bridge_f61f3a1d.csv",
]

POSTERIOR_NEUTRAL_BASES = [
    "submission_blockscale_jepa_neutral_pareto03_rt_bc_nb_sg_same_ridge_full_a24_blend0p1_noq2_w0p02_aa014669.csv",
    "submission_blockscale_jepa_neutral_pareto03_rt_same_ridge_full_a24_blend0p1_noq2_w0p02_86018abc.csv",
]

RAW_COUNTERS = [
    "submission_raw_timeline_jepa_rescue_strict_scale0p75.csv",
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p875_f5e1e1c0.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale1p0.csv",
]

AXIS_REGULARIZERS = [
    "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
    "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p08_c0p08_abf00936.csv",
    "submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p12_99eed13d.csv",
    "submission_blockscale_jepa_axisproj_pareto03_rt_bc_nb_sg_same_ridge_full_a24_blend0p1_s_all_rawproj_g0p05_c0p12_2feee0f6.csv",
]

RAWCOUNTER_WEIGHTS = [0.26, 0.28, 0.30, 0.32, 0.35, 0.40, 0.45, 0.50]
REGULARIZER_WEIGHTS = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.22, 0.26, 0.32, 0.40, 0.50]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = read_any(file_name)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def logit_blend(a: np.ndarray, b: np.ndarray, weight_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight_b) * logit(a) + weight_b * logit(b)))


def score_record(
    label: str,
    pred: np.ndarray,
    q_arrays: list[np.ndarray],
    best: np.ndarray,
    weight_mat: np.ndarray,
    axes: dict[str, np.ndarray | float],
    meta: dict[str, object],
) -> dict[str, object]:
    compact = compact_focused_score(pred, q_arrays, best, weight_mat)
    public = public_axis_features(pred, axes)
    rec = {"label": label, "prediction_hash": candidate_key(pred), "bridge_score": bridge_score(compact, public)}
    rec.update(meta)
    rec.update(compact)
    rec.update(public)
    return rec


def build_regularizers(sample: pd.DataFrame, axes: dict[str, np.ndarray | float]) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    regularizers: dict[str, np.ndarray] = {}
    rows = []
    for file_name in AXIS_REGULARIZERS:
        if not exists(file_name):
            continue
        pred = load_array(file_name, sample)
        label = f"axis::{file_name}"
        regularizers[label] = pred
        rec = {"label": label, "kind": "axis_regularizer", "base_file": file_name, "counter_file": "", "weight_counter": 0.0}
        rec.update(public_axis_features(pred, axes))
        rows.append(rec)

    for base_file in POSTERIOR_NEUTRAL_BASES:
        if not exists(base_file):
            continue
        base = load_array(base_file, sample)
        for counter_file in RAW_COUNTERS:
            if not exists(counter_file):
                continue
            counter = load_array(counter_file, sample)
            for weight in RAWCOUNTER_WEIGHTS:
                pred = logit_blend(base, counter, weight)
                label = f"rawcounter::{base_file}::{counter_file}::w{weight:.2f}"
                regularizers[label] = pred
                rec = {
                    "label": label,
                    "kind": "rawcounter_regularizer",
                    "base_file": base_file,
                    "counter_file": counter_file,
                    "weight_counter": weight,
                }
                rec.update(public_axis_features(pred, axes))
                rows.append(rec)

    reg = pd.DataFrame(rows).sort_values(
        ["posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis", "bad_residual_axis_ratio"]
    )
    reg.to_csv(OUT / "jepa_bridge_posterior_regularizers.csv", index=False)
    return regularizers, reg


def select_rows(scan: pd.DataFrame, limit: int = 90) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57684)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0026)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            26,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 1.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57682)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0027)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            24,
        ),
        (
            scan[
                (scan["posterior_expected_public_vs_anchor"] <= 0.57678)
                & (scan["delta_vs_raw05_rawaxis"] <= 2.0e-7)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0027)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            20,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58220)
                & (scan["delta_vs_raw05_rawaxis"] <= 2.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57686)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            20,
        ),
    ]
    rows = []
    seen: set[str] = set()
    for frame, quota in buckets:
        added = 0
        for row in frame.itertuples(index=False):
            h = str(row.prediction_hash)
            if h in seen:
                continue
            rows.append(row._asdict())
            seen.add(h)
            added += 1
            if added >= quota or len(rows) >= limit:
                break
        if len(rows) >= limit:
            break
    return pd.DataFrame(rows)


def write_report(reg: pd.DataFrame, shortlist: pd.DataFrame, proxy: pd.DataFrame, focused: pd.DataFrame) -> None:
    lines = [
        "# JEPA Bridge Posterior Regularizer",
        "",
        "Goal: use block-scale JEPA candidates with strong posterior proxy as regularizers for the public-minimax bridge, while preserving raw05 compatibility.",
        "",
        "## Regularizer Pool",
        "",
        "```csv",
        reg.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        shortlist.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact public proxy",
        "",
        "```csv",
        proxy.head(24).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact focused scenario",
        "",
        "```csv",
        focused.head(24).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_bridge_posterior_regularizer_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    axes = public_axes()

    regularizers, reg_table = build_regularizers(sample, axes)
    bridges = {f: load_array(f, sample) for f in BRIDGE_FILES if exists(f)}
    if not bridges or not regularizers:
        raise RuntimeError("missing bridge or regularizer pool")

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

    for bridge_file, pred in bridges.items():
        add_candidate(
            f"bridge::{bridge_file}",
            pred,
            {"source": "bridge_original", "bridge_file": bridge_file, "regularizer": "", "weight_regularizer": 0.0},
        )
    for label, pred in regularizers.items():
        add_candidate(
            label,
            pred,
            {"source": "regularizer_original", "bridge_file": "", "regularizer": label, "weight_regularizer": 1.0},
        )

    for bridge_file, bridge in bridges.items():
        for reg_label, reg_pred in regularizers.items():
            for weight in REGULARIZER_WEIGHTS:
                pred = logit_blend(bridge, reg_pred, weight)
                label = f"pair::{bridge_file}::{reg_label}::w{weight:.2f}"
                add_candidate(
                    label,
                    pred,
                    {
                        "source": "bridge_regularized",
                        "bridge_file": bridge_file,
                        "regularizer": reg_label,
                        "weight_regularizer": weight,
                    },
                )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_bridge_posterior_regularizer_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_bridge_posteriorreg_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_bridge_posterior_regularizer_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_bridge_posterior_regularizer_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_bridge_posterior_regularizer_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_bridge_posterior_regularizer_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "posterior_expected_public_vs_anchor"]).reset_index(drop=True)
    shortlist.to_csv(OUT / "jepa_bridge_posterior_regularizer_shortlist.csv", index=False)
    write_report(reg_table, shortlist, proxy, focused)

    cols = [
        "file",
        "source",
        "bridge_file",
        "regularizer",
        "weight_regularizer",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
    ]
    print(
        f"bridges={len(bridges)} regularizers={len(regularizers)} scan={len(scan)} "
        f"saved={len(saved_files)} masks={weight_mat.shape[0]} q={len(q_arrays)}"
    )
    print(shortlist[cols].head(24).to_string(index=False))


if __name__ == "__main__":
    main()
