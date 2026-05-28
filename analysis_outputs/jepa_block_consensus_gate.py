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


MANUAL_BASES = [
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    "submission_jepa_bridge_posteriorreg_cf82036c.csv",
    "submission_jepa_bridge_ensemble_86c6c9d1.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
    "submission_jepa_public_minimax_bridge_d1ca675f.csv",
    "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv",
    "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv",
    "submission_jepa_energy_ensemble_0b862967.csv",
]

TARGET_MASKS = {
    "q3_s4": ["Q3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "q1_q3_s3_s4": ["Q1", "Q3", "S3", "S4"],
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
}

GAMMAS = [0.010, 0.016, 0.024, 0.035, 0.050, 0.075]
CAPS = [0.025, 0.045, 0.075, 0.120]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = read_any(file_name)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def collect_bases() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(file_name: str, source: str, rank: int) -> None:
        if file_name in seen or not exists(file_name):
            return
        seen.add(file_name)
        rows.append({"file": file_name, "source": source, "source_rank": rank})

    for rank, file_name in enumerate(MANUAL_BASES, start=1):
        add(file_name, "manual", rank)

    for table_name in ["jepa_bridge_posterior_regularizer_shortlist.csv", "jepa_bridge_ensemble_shortlist.csv"]:
        path = OUT / table_name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        sort_cols = [c for c in ["focused_scenario_score", "posterior_expected_public_vs_anchor"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols)
        for rank, file_name in enumerate(df["file"].astype(str).head(8), start=1):
            add(file_name, table_name, rank)

    out = pd.DataFrame(rows).head(8)
    out.to_csv(OUT / "jepa_block_consensus_gate_base_pool.csv", index=False)
    return out


def collect_method_sets(summary: pd.DataFrame) -> dict[str, list[str]]:
    summary = summary.sort_values(["weighted_logloss", "delta_vs_subject_mean"]).reset_index(drop=True)
    sets: dict[str, list[str]] = {
        "top3": summary.head(3)["method"].tolist(),
        "top8": summary.head(8)["method"].tolist(),
        "zctx_local": summary[summary["method"].str.contains("local:ridge_zctx_a12", regex=False)]
        .head(10)["method"]
        .tolist(),
        "rt_zctx": summary[
            summary["preset"].eq("rt") & summary["method"].str.contains("ridge_zctx_a12", regex=False)
        ]
        .head(10)["method"]
        .tolist(),
    }
    return {name: methods for name, methods in sets.items() if methods}


def target_mask_matrix(target_names: list[str], n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=np.float64)
    for target in target_names:
        mask[:, TARGETS.index(target)] = 1.0
    return mask


def method_tensor(
    hidden_rates: pd.DataFrame,
    summary: pd.DataFrame,
    methods: list[str],
    blocks: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rate_cols = [f"rate_{target}" for target in TARGETS]
    arrays = []
    kept: list[str] = []
    for method in methods:
        mdf = hidden_rates[hidden_rates["method"].eq(method)].set_index("hidden_block_id").reindex(blocks)
        vals = mdf[rate_cols].to_numpy(dtype=np.float64)
        if vals.shape != (len(blocks), len(TARGETS)) or not np.isfinite(vals).all():
            continue
        arrays.append(clip(vals))
        kept.append(method)
    if not arrays:
        raise ValueError("empty method tensor")
    loss = summary.set_index("method").loc[kept, "weighted_logloss"].to_numpy(dtype=np.float64)
    weights = np.exp(-(loss - loss.min()) / 0.010)
    weights /= weights.sum()
    return np.stack(arrays, axis=1), weights, kept


def aggregate_logits(tensor: np.ndarray, weights: np.ndarray, agg: str) -> tuple[np.ndarray, np.ndarray]:
    logits = logit(tensor)
    if agg == "weighted":
        center = np.sum(logits * weights.reshape(1, -1, 1), axis=1)
    elif agg == "median":
        center = np.median(logits, axis=1)
    elif agg == "trimmed":
        if logits.shape[1] <= 4:
            center = logits.mean(axis=1)
        else:
            ordered = np.sort(logits, axis=1)
            center = ordered[:, 1:-1, :].mean(axis=1)
    else:
        raise ValueError(f"unknown aggregate: {agg}")
    spread = logits.std(axis=1)
    return center, spread


def rank01_by_col(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=np.float64)
    for j in range(values.shape[1]):
        order = np.argsort(values[:, j], kind="mergesort")
        ranks = np.empty(len(values), dtype=np.float64)
        ranks[order] = np.linspace(0.0, 1.0, len(values), endpoint=True)
        out[:, j] = ranks
    return out


def build_gates(
    base_logit: np.ndarray,
    consensus_logit: np.ndarray,
    method_logits: np.ndarray,
    spread: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> dict[str, np.ndarray]:
    move = consensus_logit - base_logit
    sign = np.sign(move)
    method_dir = method_logits - base_logit[:, None, :]
    sign_frac = (np.sign(method_dir) * sign[:, None, :] > 0.0).mean(axis=1)
    agreement = np.exp(-np.clip(spread, 0.0, 3.0) / 0.75) * (0.25 + 0.75 * sign_frac)

    raw_dir = logit(np.asarray(axes["raw05"], dtype=np.float64)) - base_logit
    posterior_dir = logit(np.asarray(axes["posterior"], dtype=np.float64)) - base_logit
    same_raw = (move * raw_dir > 0.0).astype(np.float64)
    same_posterior = (move * posterior_dir > 0.0).astype(np.float64)
    energy = np.sqrt(rank01_by_col(np.abs(move)))

    return {
        "energy_consensus": 0.015 + 0.985 * agreement * energy,
        "raw_agree": 0.010 + 0.990 * agreement * same_raw,
        "raw_posterior": 0.005 + 0.995 * agreement * same_raw * same_posterior,
        "raw_or_posterior": 0.010 + 0.990 * agreement * np.maximum(same_raw, same_posterior),
    }


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


def select_rows(scan: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57684)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0028)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            28,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 1.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57683)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0027)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            26,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58213)
                & (scan["delta_vs_raw05_rawaxis"] <= 3.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57688)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0032)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            24,
        ),
        (
            scan[
                (scan["posterior_expected_public_vs_anchor"] <= 0.57678)
                & (scan["delta_vs_raw05_rawaxis"] <= 2.0e-7)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0030)
            ].sort_values(["posterior_expected_public_vs_anchor", "compact_focused_score"]),
            16,
        ),
        (scan.sort_values(["bridge_score", "compact_focused_score"]), 16),
    ]
    rows: list[dict[str, object]] = []
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


def write_report(
    method_diag: pd.DataFrame,
    selected: pd.DataFrame,
    proxy: pd.DataFrame,
    focused: pd.DataFrame,
    shortlist: pd.DataFrame,
) -> None:
    lines = [
        "# JEPA Block Consensus Gate",
        "",
        "Goal: use block-scale JEPA target-rate predictions as a representation agreement gate, not as direct row residual correction.",
        "A candidate moves a strong raw05/public-safe base only when multiple JEPA target-block predictors agree on the hidden block/target direction.",
        "",
        "## Method Sets",
        "",
        "```csv",
        method_diag.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected Candidates",
        "",
        "```csv",
        selected.head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact Public Proxy",
        "",
        "```csv",
        proxy.head(24).round(10).to_csv(index=False).strip(),
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
    (OUT / "jepa_block_consensus_gate_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    summary = pd.read_csv(OUT / "block_scale_jepa_target_summary.csv")
    hidden_rates = pd.read_csv(OUT / "block_scale_jepa_target_hidden_rates.csv")

    base_pool = collect_bases()
    if base_pool.empty:
        raise RuntimeError("empty base pool")

    block_ids = sample_block_ids(train, sample).astype(str)
    blocks = sorted(hidden_rates["hidden_block_id"].astype(str).unique())
    block_to_idx = {block_id: i for i, block_id in enumerate(blocks)}
    row_block_idx = np.asarray([block_to_idx[b] for b in block_ids], dtype=int)

    method_sets = collect_method_sets(summary)
    method_diag_rows = []
    consensus_specs: list[dict[str, object]] = []
    for set_name, methods in method_sets.items():
        tensor, weights, kept = method_tensor(hidden_rates, summary, methods, blocks)
        for agg in ["weighted", "median"]:
            center, spread = aggregate_logits(tensor, weights, agg)
            consensus_specs.append(
                {
                    "set_name": set_name,
                    "agg": agg,
                    "methods": kept,
                    "center": center,
                    "spread": spread,
                    "tensor_logits": logit(tensor),
                }
            )
        method_diag_rows.append(
            {
                "set_name": set_name,
                "n_methods": len(kept),
                "best_weighted_logloss": float(summary[summary["method"].isin(kept)]["weighted_logloss"].min()),
                "mean_weighted_logloss": float(summary[summary["method"].isin(kept)]["weighted_logloss"].mean()),
                "mean_rate_std": float(tensor.std(axis=1).mean()),
                "mean_logit_std": float(logit(tensor).std(axis=1).mean()),
            }
        )
    method_diag = pd.DataFrame(method_diag_rows)
    method_diag.to_csv(OUT / "jepa_block_consensus_gate_method_sets.csv", index=False)

    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    axes = public_axes()

    arrays: dict[str, np.ndarray] = {row.file: load_array(str(row.file), sample) for row in base_pool.itertuples(index=False)}
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

    for row in base_pool.itertuples(index=False):
        add_candidate(
            str(row.file),
            arrays[str(row.file)],
            {
                "source": "base_original",
                "base_file": str(row.file),
                "base_source": row.source,
                "base_source_rank": int(row.source_rank),
                "method_set": "",
                "aggregate": "",
                "target_mask": "",
                "gate": "",
                "gamma": 0.0,
                "cap": 0.0,
                "mean_gate": 0.0,
                "mean_abs_logit_move": 0.0,
            },
        )

    for row in base_pool.itertuples(index=False):
        base_file = str(row.file)
        base = arrays[base_file]
        base_logit = logit(base)
        for spec in consensus_specs:
            set_name = str(spec["set_name"])
            agg = str(spec["agg"])
            center = np.asarray(spec["center"], dtype=np.float64)[row_block_idx]
            spread = np.asarray(spec["spread"], dtype=np.float64)[row_block_idx]
            method_logits = np.asarray(spec["tensor_logits"], dtype=np.float64)[row_block_idx]
            raw_move = center - base_logit
            gates = build_gates(base_logit, center, method_logits, spread, axes)
            for mask_name, target_names in TARGET_MASKS.items():
                tmask = target_mask_matrix(target_names, len(sample))
                for gate_name, gate in gates.items():
                    gated_mask = tmask * gate
                    if float(gated_mask.mean()) <= 0.0:
                        continue
                    for cap in CAPS:
                        capped = np.clip(raw_move, -cap, cap)
                        for gamma in GAMMAS:
                            delta = gamma * gated_mask * capped
                            if float(np.abs(delta).mean()) < 1e-7:
                                continue
                            pred = sigmoid(base_logit + delta)
                            label = (
                                f"{Path(base_file).stem}|{set_name}|{agg}|{mask_name}|"
                                f"{gate_name}|g{gamma:.3f}|c{cap:.3f}"
                            )
                            add_candidate(
                                label,
                                pred,
                                {
                                    "source": "consensus_gate",
                                    "base_file": base_file,
                                    "base_source": row.source,
                                    "base_source_rank": int(row.source_rank),
                                    "method_set": set_name,
                                    "aggregate": agg,
                                    "target_mask": mask_name,
                                    "targets": ",".join(target_names),
                                    "gate": gate_name,
                                    "gamma": gamma,
                                    "cap": cap,
                                    "mean_gate": float(gated_mask.mean()),
                                    "mean_abs_logit_move": float(np.abs(delta).mean()),
                                },
                            )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_block_consensus_gate_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_block_consensus_gate_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_block_consensus_gate_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_block_consensus_gate_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_block_consensus_gate_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_block_consensus_gate_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_block_consensus_gate_shortlist.csv", index=False)
    write_report(method_diag, selected, proxy, focused, shortlist)

    cols = [
        "file",
        "base_file",
        "method_set",
        "aggregate",
        "target_mask",
        "gate",
        "gamma",
        "cap",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_logit_move",
    ]
    print(
        f"bases={len(base_pool)} specs={len(consensus_specs)} scan={len(scan)} "
        f"saved={len(saved_files)} masks={weight_mat.shape[0]} q={len(q_arrays)}"
    )
    print(shortlist[cols].head(24).to_string(index=False))


if __name__ == "__main__":
    main()
