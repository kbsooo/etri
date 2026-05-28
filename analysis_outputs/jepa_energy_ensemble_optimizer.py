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
    expected_delta,
    load_predictions,
    logit,
    projection_ratio,
    read_submission as read_path_submission,
    sample_block_ids,
    sigmoid,
    stable_tag,
)
from hidden_block_orthogonal_gate_candidates import raw_axis_latent_q  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


EPS = 1e-5

Q_SCENARIOS = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]

FOCUSED_REFS = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
]

MANUAL_CANDIDATES = [
    "submission_jepa_block_countshift_65d5ef0c.csv",
    "submission_jepa_block_countshift_e5550364.csv",
    "submission_jepa_block_countshift_805c675c.csv",
    "submission_jepa_block_countshift_33884d08.csv",
    "submission_jepa_block_countshift_13fe468e.csv",
    "submission_jepa_block_countshift_ddaef42d.csv",
    "submission_jepa_block_countshift_86b18d2b.csv",
    "submission_blockpublic_jepa_q3s4_8e3e0d92.csv",
    "submission_blockpublic_jepa_q3s4_628c1513.csv",
    "submission_blockpublic_jepa_q3s4_7b2a0e14.csv",
    "submission_publicmask_jepa_q3s4_50528018.csv",
    "submission_publicmask_jepa_q3s4_5def572e.csv",
    "submission_publicmask_jepa_q3s4_c32a8a7e.csv",
    "submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv",
    "submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv",
    "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
    "submission_hiddenblock_rateprobe_neutral_605de284.csv",
    "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
]

TABLE_SOURCES = [
    ("jepa_block_count_shift_shortlist.csv", 18, ["focused_scenario_score", "delta_vs_raw05_rawaxis"]),
    ("jepa_block_count_shift_proxy.csv", 12, ["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"]),
    ("block_public_jepa_q3s4_focused_scenario.csv", 14, ["focused_scenario_score", "mean_expected"]),
    ("block_public_jepa_q3s4_proxy.csv", 12, ["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"]),
    ("public_mask_jepa_q3s4_fusion_focused_scenario.csv", 14, ["focused_scenario_score", "mean_expected"]),
    ("public_mask_jepa_q3s4_fusion_proxy.csv", 12, ["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"]),
]


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        p = base / file_name
        if p.exists():
            return p
    raise FileNotFoundError(file_name)


def read_any(file_name: str) -> pd.DataFrame:
    return read_path_submission(locate(file_name))


def add_unique(rows: list[dict[str, object]], seen: set[str], file_name: str, source: str) -> None:
    if not file_name or file_name in seen:
        return
    try:
        locate(file_name)
    except FileNotFoundError:
        return
    seen.add(file_name)
    rows.append({"file": file_name, "source": source})


def collect_pool() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for name in MANUAL_CANDIDATES:
        add_unique(rows, seen, name, "manual")

    for table_name, n, sort_cols in TABLE_SOURCES:
        path = OUT / table_name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        cols = [c for c in sort_cols if c in df.columns]
        if cols:
            df = df.sort_values(cols)
        for file_name in df["file"].astype(str).head(n):
            if file_name in Q_SCENARIOS:
                continue
            add_unique(rows, seen, file_name, table_name)

    pool = pd.DataFrame(rows)
    pool.to_csv(OUT / "jepa_energy_ensemble_pool.csv", index=False)
    return pool


def compact_mask_weights(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
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

    rows_meta = []
    weights = []
    for i in sorted(k for k in keep if k < len(records)):
        rec = records[i]
        if rec["mask_kind"] == "all":
            continue
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        if int(mask.sum()) <= 0:
            continue
        w = np.zeros(len(sample), dtype=np.float64)
        w[mask] = 1.0 / float(mask.sum())
        weights.append(w)
        rows_meta.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": int(mask.sum()),
            }
        )
    mat = np.vstack(weights)
    meta = pd.DataFrame(rows_meta)
    meta.to_csv(OUT / "jepa_energy_ensemble_compact_masks.csv", index=False)
    return mat, meta


def focused_components(files: list[str], weight_mat: np.ndarray) -> tuple[list[np.ndarray], np.ndarray]:
    q_arrays = [read_any(f)[TARGETS].to_numpy(dtype=np.float64) for f in Q_SCENARIOS if (OUT / f).exists()]
    ref_arrays = [read_any(f)[TARGETS].to_numpy(dtype=np.float64) for f in FOCUSED_REFS if (OUT / f).exists()]
    ref_scores = []
    for q in q_arrays:
        per_ref = []
        for pred in ref_arrays:
            row_loss = ce_matrix(q, pred).mean(axis=1)
            per_ref.append(weight_mat @ row_loss)
        ref_scores.append(np.vstack(per_ref).min(axis=0))
    best = np.concatenate(ref_scores)
    return q_arrays, best


def compact_focused_score(pred: np.ndarray, q_arrays: list[np.ndarray], best: np.ndarray, weight_mat: np.ndarray) -> dict[str, float]:
    all_scores = []
    for q in q_arrays:
        row_loss = ce_matrix(q, pred).mean(axis=1)
        all_scores.append(weight_mat @ row_loss)
    scores = np.concatenate(all_scores)
    regret = scores - best
    return {
        "compact_mean_expected": float(scores.mean()),
        "compact_p90_expected": float(np.quantile(scores, 0.90)),
        "compact_mean_regret": float(regret.mean()),
        "compact_p90_regret": float(np.quantile(regret, 0.90)),
        "compact_p95_regret": float(np.quantile(regret, 0.95)),
        "compact_max_regret": float(regret.max()),
        "compact_focused_score": float(
            scores.mean()
            + 2.0 * regret.mean()
            + np.quantile(regret, 0.90)
            + 0.25 * np.quantile(regret, 0.95)
        ),
    }


def public_axes() -> dict[str, np.ndarray | float]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    _frames, preds = load_predictions()
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])
    raw05_delta = expected_delta(raw_q, preds["raw05"], preds["stage2"])
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv").set_index("hidden_block_id")
    posterior = np.zeros_like(preds["raw05"])
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            posterior[i, j] = float(block_df.loc[block_id, f"posterior_rate_{target}"])
    return {
        "stage2": preds["stage2"],
        "anchor578": preds["anchor578"],
        "raw05": preds["raw05"],
        "raw_q": raw_q,
        "raw05_delta": raw05_delta,
        "posterior": clip(posterior),
        "bad_axis": preds["jepa_bad_residual"] - preds["stage2"],
        "ordinal_axis": preds["ordinal_q"] - preds["stage2"],
    }


def public_axis_features(pred: np.ndarray, axes: dict[str, np.ndarray | float]) -> dict[str, float]:
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    raw05 = np.asarray(axes["raw05"], dtype=np.float64)
    raw_q = np.asarray(axes["raw_q"], dtype=np.float64)
    raw05_delta = float(axes["raw05_delta"])
    return {
        "posterior_expected_public_vs_anchor": 0.5784273528
        + expected_delta(np.asarray(axes["posterior"], dtype=np.float64), pred, np.asarray(axes["anchor578"], dtype=np.float64)),
        "raw_axis_expected_public_vs_stage2": 0.5779449757 + expected_delta(raw_q, pred, stage2),
        "delta_vs_raw05_rawaxis": expected_delta(raw_q, pred, stage2) - raw05_delta,
        "bad_residual_axis_ratio": projection_ratio(pred - stage2, np.asarray(axes["bad_axis"], dtype=np.float64)),
        "ordinal_axis_ratio": projection_ratio(pred - stage2, np.asarray(axes["ordinal_axis"], dtype=np.float64)),
        "mean_abs_move_vs_raw05": float(np.abs(pred - raw05).mean()),
        "min_prob": float(pred.min()),
        "max_prob": float(pred.max()),
    }


def candidate_key(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def score_record(
    label: str,
    pred: np.ndarray,
    q_arrays: list[np.ndarray],
    best: np.ndarray,
    weight_mat: np.ndarray,
    axes: dict[str, np.ndarray | float],
    source: str,
) -> dict[str, object]:
    compact = compact_focused_score(pred, q_arrays, best, weight_mat)
    public = public_axis_features(pred, axes)
    posterior_penalty = max(float(public["posterior_expected_public_vs_anchor"]) - 0.57678, 0.0) * 2.0
    raw_penalty = max(float(public["delta_vs_raw05_rawaxis"]) - 5.0e-8, 0.0) * 150.0
    bad_penalty = max(abs(float(public["bad_residual_axis_ratio"])) - 0.0025, 0.0) * 0.025
    move_penalty = max(float(public["mean_abs_move_vs_raw05"]) - 0.0025, 0.0) * 0.05
    selection_score = float(compact["compact_focused_score"] + posterior_penalty + raw_penalty + bad_penalty + move_penalty)
    out = {
        "label": label,
        "source": source,
        "prediction_hash": candidate_key(pred),
        "selection_score": selection_score,
    }
    out.update(compact)
    out.update(public)
    return out


def logit_blend(base: np.ndarray, donor: np.ndarray, weight: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight) * logit(base) + weight * logit(donor)))


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


def write_report(selected: pd.DataFrame, proxy: pd.DataFrame, focused: pd.DataFrame) -> None:
    lines = [
        "# JEPA Energy Ensemble Optimizer",
        "",
        "Goal: use JEPA as a latent block/count energy and blend only raw05-compatible hidden-structure candidates.",
        "The scan penalizes movement that is worse than the observed raw05 public axis, then reruns the existing proxy/focused verifiers.",
        "",
        "## Top selected by compact search",
        "",
        "```csv",
        selected.head(20).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact public proxy",
        "",
        "```csv",
        proxy.head(20).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Exact focused scenario",
        "",
        "```csv",
        focused.head(24).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_energy_ensemble_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    pool = collect_pool()
    weight_mat, _mask_meta = compact_mask_weights(sample)
    q_arrays, best = focused_components(pool["file"].astype(str).tolist(), weight_mat)
    axes = public_axes()

    arrays: dict[str, np.ndarray] = {}
    logits: dict[str, np.ndarray] = {}
    for file_name in pool["file"].astype(str):
        frame = read_any(file_name)
        if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
            raise ValueError(f"key mismatch: {file_name}")
        arr = clip(frame[TARGETS].to_numpy(dtype=np.float64))
        arrays[file_name] = arr
        logits[file_name] = logit(arr)

    records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}
    seen_hash: set[str] = set()

    def add_candidate(label: str, pred: np.ndarray, source: str) -> None:
        h = candidate_key(pred)
        if h in seen_hash:
            return
        seen_hash.add(h)
        predictions[label] = pred
        records.append(score_record(label, pred, q_arrays, best, weight_mat, axes, source))

    for file_name, arr in arrays.items():
        add_candidate(file_name, arr, "pool_original")

    original_scores = pd.DataFrame(records).sort_values("selection_score")
    base_files = original_scores.head(18)["label"].tolist()
    donor_files = pool["file"].astype(str).tolist()
    pair_weights = [0.025, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.24, 0.32]
    for base_name in base_files:
        base = arrays[base_name]
        for donor_name in donor_files:
            if donor_name == base_name:
                continue
            donor = arrays[donor_name]
            for w in pair_weights:
                pred = logit_blend(base, donor, w)
                label = f"pair::{base_name}::{donor_name}::w{w:g}"
                add_candidate(label, pred, "pair_logit")

    scan1 = pd.DataFrame(records).sort_values("selection_score").reset_index(drop=True)
    top_pair_labels = [x for x in scan1.head(90)["label"].astype(str).tolist() if x in predictions]
    small_weights = [0.02, 0.035, 0.05, 0.075, 0.10, 0.14]
    for base_label in top_pair_labels:
        base = predictions[base_label]
        for donor_name in donor_files:
            donor = arrays[donor_name]
            for w in small_weights:
                pred = logit_blend(base, donor, w)
                label = f"triple::{base_label}::{donor_name}::w{w:g}"
                add_candidate(label, pred, "triple_logit")

    scan = pd.DataFrame(records).sort_values("selection_score").reset_index(drop=True)
    scan.to_csv(OUT / "jepa_energy_ensemble_scan.csv", index=False)

    keep = []
    taken_hash: set[str] = set()
    buckets = [
        (scan.sort_values("selection_score"), 22),
        (
            scan[(scan["delta_vs_raw05_rawaxis"] <= 0.0) & (scan["posterior_expected_public_vs_anchor"] <= 0.57685)].sort_values(
                ["compact_focused_score", "posterior_expected_public_vs_anchor"]
            ),
            24,
        ),
        (
            scan[(scan["posterior_expected_public_vs_anchor"] <= 0.57676)].sort_values(
                ["delta_vs_raw05_rawaxis", "compact_focused_score"]
            ),
            20,
        ),
        (scan[scan["delta_vs_raw05_rawaxis"] <= 0.0].sort_values(["posterior_expected_public_vs_anchor", "compact_focused_score"]), 16),
        (scan.sort_values(["posterior_expected_public_vs_anchor", "selection_score"]), 8),
    ]
    for frame, quota in buckets:
        added = 0
        for row in frame.itertuples(index=False):
            h = str(row.prediction_hash)
            if h in taken_hash:
                continue
            taken_hash.add(h)
            keep.append(row._asdict())
            added += 1
            if added >= quota or len(keep) >= 90:
                break
        if len(keep) >= 90:
            break

    selected = pd.DataFrame(keep)
    saved_files = []
    for i, row in selected.iterrows():
        label = str(row["label"])
        pred = predictions[label]
        tag = stable_tag(f"{label}|{row['selection_score']:.12f}|{i}")
        file_name = f"submission_jepa_energy_ensemble_{tag}.csv"
        save_submission(file_name, sample, pred)
        saved_files.append(file_name)
    selected.insert(0, "file", saved_files)
    selected.to_csv(OUT / "jepa_energy_ensemble_selected.csv", index=False)

    integ = integrity(saved_files, sample)
    integ.to_csv(OUT / "jepa_energy_ensemble_integrity.csv", index=False)
    proxy = public_proxy_scores(saved_files)
    proxy.to_csv(OUT / "jepa_energy_ensemble_proxy.csv", index=False)
    focused = focused_scenario_scores(saved_files)
    focused.to_csv(OUT / "jepa_energy_ensemble_focused_scenario.csv", index=False)

    shortlist = (
        selected.merge(proxy, on="file", how="left", suffixes=("", "_proxy"))
        .merge(focused, on="file", how="left", suffixes=("", "_focused"))
        .merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    )
    shortlist = shortlist.sort_values(["focused_scenario_score", "selection_score"]).reset_index(drop=True)
    shortlist.to_csv(OUT / "jepa_energy_ensemble_shortlist.csv", index=False)
    write_report(shortlist, proxy, focused)
    print(f"pool={len(pool)} scan={len(scan)} saved={len(saved_files)} masks={weight_mat.shape[0]} q={len(q_arrays)}")
    print(shortlist.head(12)[["file", "selection_score", "focused_scenario_score", "delta_vs_raw05_rawaxis"]].to_string(index=False))


if __name__ == "__main__":
    main()
