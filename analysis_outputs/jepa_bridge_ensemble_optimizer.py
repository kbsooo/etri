from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
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


BASELINE_FILES = [
    "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv",
    "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv",
    "submission_jepa_energy_ensemble_0b862967.csv",
    "submission_jepa_energy_ensemble_e187e70f.csv",
    "submission_jepa_public_blockentropy_seq1501_q3_only_g001_782e0645.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
]

PAIR_WEIGHTS = [0.05, 0.08, 0.12, 0.18, 0.26, 0.35, 0.50, 0.65, 0.82]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (ROOT / "jepa" / file_name).exists()


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = read_any(file_name)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def add_file(rows: list[dict[str, object]], seen: set[str], file_name: str, source: str, rank: int) -> None:
    if file_name in seen or not exists(file_name):
        return
    seen.add(file_name)
    rows.append({"file": file_name, "source": source, "source_rank": rank})


def collect_pool() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for rank, file_name in enumerate(BASELINE_FILES, start=1):
        add_file(rows, seen, file_name, "baseline", rank)

    path = OUT / "jepa_public_minimax_rawsafe_bridge_shortlist.csv"
    if path.exists():
        df = pd.read_csv(path)
        slices = [
            ("bridge_best_focused", df.sort_values(["focused_scenario_score", "posterior_expected_public_vs_anchor"]).head(30)),
            (
                "bridge_strict_raw",
                df[df["delta_vs_raw05_rawaxis"] <= 0.0].sort_values(
                    ["focused_scenario_score", "posterior_expected_public_vs_anchor"]
                ).head(30),
            ),
            (
                "bridge_near_raw",
                df[
                    (df["delta_vs_raw05_rawaxis"].abs() <= 5.0e-7)
                    & (df["bad_residual_axis_ratio"].abs() <= 0.004)
                    & (df["posterior_expected_public_vs_anchor"] <= 0.5769)
                ]
                .sort_values(["focused_scenario_score", "posterior_expected_public_vs_anchor"])
                .head(30),
            ),
            (
                "bridge_posterior",
                df[df["posterior_expected_public_vs_anchor"] <= 0.57682]
                .sort_values(["posterior_expected_public_vs_anchor", "focused_scenario_score"])
                .head(20),
            ),
        ]
        for source, part in slices:
            for rank, file_name in enumerate(part["file"].astype(str), start=1):
                add_file(rows, seen, file_name, source, rank)

    pool = pd.DataFrame(rows)
    pool.to_csv(OUT / "jepa_bridge_ensemble_pool.csv", index=False)
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


def logit_blend(a: np.ndarray, b: np.ndarray, weight_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight_b) * logit(a) + weight_b * logit(b)))


def select_rows(scan: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57686)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.004)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            32,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 4.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57684)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.003)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            28,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58230)
                & (scan["delta_vs_raw05_rawaxis"] <= 8.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57695)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.005)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            24,
        ),
        (
            scan[scan["posterior_expected_public_vs_anchor"] <= 0.57675].sort_values(
                ["posterior_expected_public_vs_anchor", "compact_focused_score"]
            ),
            16,
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


def write_report(shortlist: pd.DataFrame, proxy: pd.DataFrame, focused: pd.DataFrame) -> None:
    lines = [
        "# JEPA Bridge Ensemble Optimizer",
        "",
        "Goal: blend the new public-minimax raw-safe bridge candidates with earlier JEPA block/energy candidates to recover posterior/raw safety without losing focused-scenario gain.",
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
    (OUT / "jepa_bridge_ensemble_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    pool = collect_pool()
    if pool.empty:
        raise RuntimeError("empty pool")

    weight_mat, _meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    axes = public_axes()

    arrays: dict[str, np.ndarray] = {row.file: load_array(str(row.file), sample) for row in pool.itertuples(index=False)}
    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}
    seen_hash: set[str] = set()

    def add_candidate(label: str, pred: np.ndarray, meta: dict[str, object]) -> None:
        h = candidate_key(pred)
        if h in seen_hash:
            return
        seen_hash.add(h)
        predictions[label] = clip(pred)
        records.append(score_record(label, clip(pred), q_arrays, best, weight_mat, axes, meta))

    for row in pool.itertuples(index=False):
        add_candidate(
            str(row.file),
            arrays[str(row.file)],
            {
                "source": "original",
                "base_file": str(row.file),
                "donor_file": "",
                "weight_donor": 0.0,
                "pool_source": row.source,
                "pool_source_rank": int(row.source_rank),
            },
        )

    original = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"])
    base_files = original.head(28)["label"].astype(str).tolist()
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
                add_candidate(
                    label,
                    pred,
                    {
                        "source": "pair_logit",
                        "base_file": base_file,
                        "donor_file": donor_file,
                        "weight_donor": weight,
                        "pool_source": "",
                        "pool_source_rank": -1,
                    },
                )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_bridge_ensemble_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_bridge_ensemble_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_bridge_ensemble_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_bridge_ensemble_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_bridge_ensemble_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_bridge_ensemble_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_bridge_ensemble_shortlist.csv", index=False)
    write_report(shortlist, proxy, focused)

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
    ]
    print(f"pool={len(pool)} scan={len(scan)} saved={len(saved_files)} masks={weight_mat.shape[0]} q={len(q_arrays)}")
    print(shortlist[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
