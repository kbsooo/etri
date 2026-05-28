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


MANUAL = [
    "submission_jepa_bridge_ensemble_86c6c9d1.csv",
    "submission_jepa_bridge_ensemble_c42fbf1e.csv",
    "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    "submission_jepa_bridge_posteriorreg_cf82036c.csv",
    "submission_jepa_public_minimax_bridge_84b71a03.csv",
    "submission_jepa_public_minimax_bridge_d1ca675f.csv",
]
TABLES = [
    ("jepa_block_consensus_rawcorrector_microrefine_shortlist.csv", 28),
    ("jepa_block_consensus_rawcorrector_refine_shortlist.csv", 18),
    ("jepa_block_consensus_rawcorrector_shortlist.csv", 18),
    ("jepa_block_consensus_gate_shortlist.csv", 10),
]
PAIR_WEIGHTS = [0.04, 0.07, 0.10, 0.14, 0.18, 0.24, 0.32, 0.42, 0.55]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = read_any(file_name)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def logit_blend(a: np.ndarray, b: np.ndarray, weight_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight_b) * logit(a) + weight_b * logit(b)))


def collect_pool() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(file_name: str, source: str, rank: int) -> None:
        if file_name in seen or not exists(file_name):
            return
        seen.add(file_name)
        rows.append({"file": file_name, "source": source, "rank": rank})

    for rank, file_name in enumerate(MANUAL, start=1):
        add(file_name, "manual", rank)
    for table, n in TABLES:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path).sort_values(["focused_scenario_score", "posterior_expected_public_vs_anchor"])
        for rank, file_name in enumerate(df["file"].astype(str).head(n), start=1):
            add(file_name, table, rank)
    pool = pd.DataFrame(rows)
    pool.to_csv(OUT / "jepa_micro_bridge_ensemble_pool.csv", index=False)
    return pool


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
                (scan["compact_focused_score"] <= 0.58203)
                & (scan["delta_vs_raw05_rawaxis"] <= 3.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57691)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0028)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            34,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 1.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57688)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0024)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            28,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57688)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.0024)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            22,
        ),
        (
            scan.sort_values(["bridge_score", "compact_focused_score"]),
            16,
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
    pool = collect_pool()
    if pool.empty:
        raise RuntimeError("empty pool")

    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    axes = public_axes()
    arrays = {row.file: load_array(str(row.file), sample) for row in pool.itertuples(index=False)}

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

    for row in pool.itertuples(index=False):
        add(
            str(row.file),
            arrays[str(row.file)],
            {
                "source": "original",
                "base_file": str(row.file),
                "donor_file": "",
                "weight_donor": 0.0,
                "pool_source": row.source,
                "pool_rank": int(row.rank),
            },
        )

    original = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"])
    base_files = original.head(34)["label"].astype(str).tolist()
    donor_files = pool["file"].astype(str).tolist()
    for base_file in base_files:
        base = arrays[base_file]
        for donor_file in donor_files:
            if donor_file == base_file:
                continue
            donor = arrays[donor_file]
            for weight in PAIR_WEIGHTS:
                pred = logit_blend(base, donor, weight)
                label = f"pair|{Path(base_file).stem}|{Path(donor_file).stem}|w{weight:.2f}"
                add(
                    label,
                    pred,
                    {
                        "source": "pair_logit",
                        "base_file": base_file,
                        "donor_file": donor_file,
                        "weight_donor": weight,
                        "pool_source": "",
                        "pool_rank": -1,
                    },
                )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_micro_bridge_ensemble_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_micro_bridge_ensemble_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_micro_bridge_ensemble_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_micro_bridge_ensemble_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_micro_bridge_ensemble_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_micro_bridge_ensemble_focused_scenario.csv", index=False)
    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_micro_bridge_ensemble_shortlist.csv", index=False)
    (OUT / "jepa_micro_bridge_ensemble_report.md").write_text(
        "# JEPA Micro Bridge Ensemble\n\n" + shortlist.head(50).round(10).to_csv(index=False),
        encoding="utf-8",
    )

    cols = [
        "file",
        "source",
        "base_file",
        "donor_file",
        "weight_donor",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "compact_focused_score",
    ]
    print(f"pool={len(pool)} scan={len(scan)} saved={len(saved_files)}")
    print(shortlist[cols].head(24).to_string(index=False))


if __name__ == "__main__":
    main()
