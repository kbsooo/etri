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

from hidden_block_latent_audit import (  # noqa: E402
    KEY,
    TARGETS,
    clip,
    logit,
    sample_block_ids,
    sigmoid,
    stable_tag,
)
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from jepa_energy_ensemble_optimizer import (  # noqa: E402
    FOCUSED_REFS,
    Q_SCENARIOS,
    candidate_key,
    public_axes,
    public_axis_features,
    read_any,
)
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


EPS = 1e-5

JEPA_ANCHORS = [
    ("raw05", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"),
    ("blockentropy_publicmask", "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv"),
    ("blockentropy_countb2434", "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv"),
    ("energy_balanced", "submission_jepa_energy_ensemble_0b862967.csv"),
    ("energy_focused", "submission_jepa_energy_ensemble_e187e70f.csv"),
    ("seq1501", "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv"),
    ("seqebf", "submission_hiddenblock_seqmotif_neutral_ebf79910.csv"),
]

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "q1_q3_s3_s4": ["Q1", "Q3", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
}

GAMMAS = [
    0.015,
    0.025,
    0.035,
    0.04,
    0.045,
    0.05,
    0.055,
    0.06,
    0.065,
    0.07,
    0.075,
    0.08,
    0.085,
    0.095,
    0.12,
    0.18,
    0.26,
    0.38,
    0.55,
]


def exists_any(file_name: str) -> bool:
    return (OUT / file_name).exists() or (JEPA / file_name).exists()


def collect_public_candidates() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(file_name: str, source: str, rank: int) -> None:
        if file_name in seen or not exists_any(file_name):
            return
        seen.add(file_name)
        rows.append({"file": file_name, "source": source, "source_rank": rank})

    minimax_path = OUT / "public_minimax_ensemble_selected.csv"
    if minimax_path.exists():
        for rank, file_name in enumerate(pd.read_csv(minimax_path)["file"].astype(str).head(8), start=1):
            add(file_name, "public_minimax_ensemble_selected", rank)

    inverse_path = OUT / "public_lb_inverse_candidate_ranking.csv"
    if inverse_path.exists():
        for rank, file_name in enumerate(pd.read_csv(inverse_path)["file"].astype(str).head(14), start=1):
            add(file_name, "public_lb_inverse_candidate_ranking", rank)

    fallback = [
        "submission_public_entropyproj_public2d0_g100.csv",
        "submission_public_entropyproj_public2d0_g075.csv",
        "submission_public_entropyproj_proj0_g100.csv",
        "submission_public_entropyproj_proj0_g075.csv",
    ]
    for rank, file_name in enumerate(fallback, start=1):
        add(file_name, "manual_public_fallback", rank)

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_public_pool.csv", index=False)
    return out


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = read_any(file_name)
    if not df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def normalized_compact_masks(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    records = build_masks(sample)
    keep: set[int] = set()
    for table in [
        "public_lb_inverse_mask_top512.csv",
        "public_lb_inverse_mask_raw05_compatible_top512.csv",
        "public_lb_inverse_mask_all_sign_compatible_top512.csv",
    ]:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "mask_index" in df.columns:
            keep.update(df["mask_index"].astype(int).head(64).tolist())
    for i, rec in enumerate(records):
        kind = str(rec["mask_kind"])
        rows = int(rec["rows"])
        if kind in {"global_order", "subject_order", "single_subject"}:
            keep.add(i)
        elif kind == "subject_contiguous" and rows in {50, 64, 100, 125, 150} and len(keep) < 260:
            keep.add(i)

    weights = []
    meta = []
    for i in sorted(k for k in keep if k < len(records)):
        rec = records[i]
        if rec["mask_kind"] == "all":
            continue
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        if int(mask.sum()) <= 0:
            continue
        row = np.zeros(len(sample), dtype=np.float64)
        row[mask] = 1.0 / float(mask.sum())
        weights.append(row)
        meta.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": int(mask.sum()),
            }
        )
    mask_mat = np.vstack(weights)
    meta_df = pd.DataFrame(meta)
    meta_df.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_compact_masks.csv", index=False)
    return mask_mat, meta_df


def focused_reference_components(sample: pd.DataFrame, weight_mat: np.ndarray) -> tuple[list[np.ndarray], np.ndarray]:
    q_arrays = [load_array(f, sample) for f in Q_SCENARIOS if exists_any(f)]
    ref_files = [f for f in FOCUSED_REFS if exists_any(f)]
    ref_arrays = [load_array(f, sample) for f in ref_files]
    ref_scores = []
    for q in q_arrays:
        per_ref = []
        for ref in ref_arrays:
            row_loss = ce_matrix(q, ref).mean(axis=1)
            per_ref.append(weight_mat @ row_loss)
        ref_scores.append(np.vstack(per_ref).min(axis=0))
    return q_arrays, np.concatenate(ref_scores)


def compact_focused_score(pred: np.ndarray, q_arrays: list[np.ndarray], best: np.ndarray, weight_mat: np.ndarray) -> dict[str, float]:
    scores = []
    for q in q_arrays:
        row_loss = ce_matrix(q, pred).mean(axis=1)
        scores.append(weight_mat @ row_loss)
    flat = np.concatenate(scores)
    regret = flat - best
    return {
        "compact_mean_expected": float(flat.mean()),
        "compact_p90_expected": float(np.quantile(flat, 0.90)),
        "compact_mean_regret": float(regret.mean()),
        "compact_p90_regret": float(np.quantile(regret, 0.90)),
        "compact_p95_regret": float(np.quantile(regret, 0.95)),
        "compact_max_regret": float(regret.max()),
        "compact_focused_score": float(
            flat.mean()
            + 2.0 * regret.mean()
            + np.quantile(regret, 0.90)
            + 0.25 * np.quantile(regret, 0.95)
        ),
    }


def rank01_by_col(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=np.float64)
    for j in range(values.shape[1]):
        order = np.argsort(values[:, j], kind="mergesort")
        ranks = np.empty(len(values), dtype=np.float64)
        ranks[order] = np.linspace(0.0, 1.0, len(values), endpoint=True)
        out[:, j] = ranks
    return out


def block_energy_gate(anchor_dir: np.ndarray, block_ids: np.ndarray) -> np.ndarray:
    energy = np.zeros_like(anchor_dir, dtype=np.float64)
    unique_blocks = pd.Series(block_ids).drop_duplicates().astype(str).tolist()
    for j in range(anchor_dir.shape[1]):
        block_vals = []
        for block_id in unique_blocks:
            mask = block_ids == block_id
            block_vals.append(float(np.mean(np.abs(anchor_dir[mask, j]))))
        block_rank = rank01_by_col(np.asarray(block_vals, dtype=np.float64).reshape(-1, 1)).reshape(-1)
        rank_map = dict(zip(unique_blocks, block_rank, strict=True))
        for block_id in unique_blocks:
            energy[block_ids == block_id, j] = rank_map[block_id]
    return energy


def target_mask_matrix(target_names: list[str], rows: int) -> np.ndarray:
    mask = np.zeros((rows, len(TARGETS)), dtype=np.float64)
    for target in target_names:
        mask[:, TARGETS.index(target)] = 1.0
    return mask


def make_gates(
    public_dir_stage2: np.ndarray,
    anchor_dir_stage2: np.ndarray,
    raw_dir_stage2: np.ndarray,
    block_energy: np.ndarray,
) -> dict[str, np.ndarray]:
    anchor_mag = np.sqrt(rank01_by_col(np.abs(anchor_dir_stage2)))
    raw_mag = np.sqrt(rank01_by_col(np.abs(raw_dir_stage2)))
    block_mag = np.sqrt(np.clip(block_energy, 0.0, 1.0))
    same_anchor = (public_dir_stage2 * anchor_dir_stage2 > 0.0).astype(np.float64)
    same_raw = (public_dir_stage2 * raw_dir_stage2 > 0.0).astype(np.float64)
    return {
        "uniform": np.ones_like(public_dir_stage2, dtype=np.float64),
        "anchor_agree": 0.03 + 0.97 * same_anchor * anchor_mag,
        "raw_agree": 0.03 + 0.97 * same_raw * raw_mag,
        "block_anchor": 0.03 + 0.97 * same_anchor * block_mag,
        "consensus": 0.015 + 0.985 * same_anchor * same_raw * np.maximum(anchor_mag, block_mag),
    }


def bridge_score(compact: dict[str, float], public: dict[str, float]) -> float:
    posterior = float(public["posterior_expected_public_vs_anchor"])
    raw_delta = float(public["delta_vs_raw05_rawaxis"])
    bad_ratio = abs(float(public["bad_residual_axis_ratio"]))
    ordinal_ratio = abs(float(public["ordinal_axis_ratio"]))
    move_raw05 = float(public["mean_abs_move_vs_raw05"])
    return float(
        compact["compact_focused_score"]
        + max(posterior - 0.57680, 0.0) * 4.0
        + max(raw_delta - 1.0e-7, 0.0) * 300.0
        + max(bad_ratio - 0.0030, 0.0) * 0.040
        + max(ordinal_ratio - 0.0600, 0.0) * 0.010
        + max(move_raw05 - 0.0040, 0.0) * 0.040
    )


def save_submission(file_name: str, sample: pd.DataFrame, pred: np.ndarray) -> None:
    out = sample[KEY].copy()
    out[TARGETS] = clip(pred)
    out.to_csv(OUT / file_name, index=False)


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref_key = sample[KEY].reset_index(drop=True)
    for file_name in files:
        df = read_any(file_name)
        pred = df[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(df),
                "key_ok": bool(df[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(df.duplicated(KEY).sum()),
                "null_probs": int(df[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def select_rows(scan: pd.DataFrame, limit: int = 120) -> pd.DataFrame:
    buckets = [
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"] <= 0.0)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57690)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.006)
            ].sort_values(["compact_focused_score", "posterior_expected_public_vs_anchor"]),
            32,
        ),
        (
            scan[
                (scan["delta_vs_raw05_rawaxis"].abs() <= 5.0e-7)
                & (scan["posterior_expected_public_vs_anchor"] <= 0.57685)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.004)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            28,
        ),
        (
            scan[
                (scan["posterior_expected_public_vs_anchor"] <= 0.57675)
                & (scan["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            ].sort_values(["posterior_expected_public_vs_anchor", "compact_focused_score"]),
            20,
        ),
        (
            scan[
                (scan["compact_focused_score"] <= 0.58235)
                & (scan["delta_vs_raw05_rawaxis"] <= 1.0e-6)
                & (scan["bad_residual_axis_ratio"].abs() <= 0.008)
            ].sort_values(["compact_focused_score", "bridge_score"]),
            24,
        ),
        (scan.sort_values(["bridge_score", "compact_focused_score"]), 16),
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


def write_report(
    conflict: pd.DataFrame,
    selected: pd.DataFrame,
    proxy: pd.DataFrame,
    focused: pd.DataFrame,
    shortlist: pd.DataFrame,
) -> None:
    lines = [
        "# JEPA Public Minimax Raw-Safe Bridge",
        "",
        "Goal: test whether the strong public-LB inverse/minimax axis can be used without leaving the JEPA/raw05-compatible hidden-structure manifold.",
        "Method: start from JEPA/raw05 anchors, then inject public-minimax movement only where JEPA/raw05/block-energy gates agree.",
        "",
        "## Original public-axis conflict",
        "",
        "```csv",
        conflict.head(18).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected bridge candidates",
        "",
        "```csv",
        selected.head(24).round(10).to_csv(index=False).strip(),
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
        "",
        "## Shortlist",
        "",
        "```csv",
        shortlist.head(30).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_public_minimax_rawsafe_bridge_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    public_pool = collect_public_candidates()
    anchors = [(name, file_name) for name, file_name in JEPA_ANCHORS if exists_any(file_name)]
    if public_pool.empty or not anchors:
        raise RuntimeError("missing public pool or JEPA anchors")

    weight_mat, _mask_meta = normalized_compact_masks(sample)
    q_arrays, best = focused_reference_components(sample, weight_mat)
    axes = public_axes()
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    raw05 = np.asarray(axes["raw05"], dtype=np.float64)
    stage2_logit = logit(stage2)
    raw_dir_stage2 = logit(raw05) - stage2_logit
    block_ids = sample_block_ids(train, sample).astype(str)

    public_arrays = {row.file: load_array(str(row.file), sample) for row in public_pool.itertuples(index=False)}
    anchor_arrays = {file_name: load_array(file_name, sample) for _, file_name in anchors}

    conflict_rows = []
    for row in public_pool.itertuples(index=False):
        rec = {"file": row.file, "source": row.source, "source_rank": int(row.source_rank)}
        rec.update(public_axis_features(public_arrays[str(row.file)], axes))
        conflict_rows.append(rec)
    conflict = pd.DataFrame(conflict_rows).sort_values(["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"])
    conflict.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_public_conflict.csv", index=False)

    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}
    seen_hash: set[str] = set()

    def add_candidate(label: str, pred: np.ndarray, meta: dict[str, object]) -> None:
        pred = clip(pred)
        h = candidate_key(pred)
        if h in seen_hash:
            return
        seen_hash.add(h)
        compact = compact_focused_score(pred, q_arrays, best, weight_mat)
        public = public_axis_features(pred, axes)
        rec = {
            "label": label,
            "prediction_hash": h,
            "bridge_score": bridge_score(compact, public),
        }
        rec.update(meta)
        rec.update(compact)
        rec.update(public)
        records.append(rec)
        predictions[label] = pred

    for anchor_name, anchor_file in anchors:
        anchor = anchor_arrays[anchor_file]
        anchor_logit = logit(anchor)
        anchor_dir_stage2 = anchor_logit - stage2_logit
        block_gate = block_energy_gate(anchor_dir_stage2, block_ids)
        for public_row in public_pool.itertuples(index=False):
            public_file = str(public_row.file)
            public = public_arrays[public_file]
            public_logit = logit(public)
            move = public_logit - anchor_logit
            public_dir_stage2 = public_logit - stage2_logit
            gates = make_gates(public_dir_stage2, anchor_dir_stage2, raw_dir_stage2, block_gate)
            for mask_name, target_names in TARGET_MASKS.items():
                target_mask = target_mask_matrix(target_names, len(sample))
                for gate_name, gate in gates.items():
                    for gamma in GAMMAS:
                        cell_gate = target_mask * gate * gamma
                        pred = sigmoid(anchor_logit + cell_gate * move)
                        label = (
                            f"{anchor_name}|{Path(anchor_file).stem}|{Path(public_file).stem}|"
                            f"{mask_name}|{gate_name}|g{gamma:.3f}"
                        )
                        add_candidate(
                            label,
                            pred,
                            {
                                "anchor": anchor_name,
                                "anchor_file": anchor_file,
                                "public_file": public_file,
                                "public_source": public_row.source,
                                "public_source_rank": int(public_row.source_rank),
                                "target_mask": mask_name,
                                "targets": ",".join(target_names),
                                "gate": gate_name,
                                "gamma": gamma,
                            },
                        )

    scan = pd.DataFrame(records).sort_values(["bridge_score", "compact_focused_score"]).reset_index(drop=True)
    scan.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_scan.csv", index=False)
    selected = select_rows(scan)

    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        tag = stable_tag(f"{label}|{row['bridge_score']:.12f}|{i}")
        file_name = f"submission_jepa_public_minimax_bridge_{tag}.csv"
        save_submission(file_name, sample, predictions[label])
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "bridge_score", "posterior_expected_public_vs_anchor"]).reset_index(
        drop=True
    )
    shortlist.to_csv(OUT / "jepa_public_minimax_rawsafe_bridge_shortlist.csv", index=False)
    write_report(conflict, selected, proxy, focused, shortlist)

    cols = [
        "file",
        "anchor",
        "public_file",
        "target_mask",
        "gate",
        "gamma",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
    ]
    print(
        f"public_pool={len(public_pool)} anchors={len(anchors)} scan={len(scan)} "
        f"saved={len(saved_files)} masks={weight_mat.shape[0]} q={len(q_arrays)}"
    )
    print(shortlist[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
