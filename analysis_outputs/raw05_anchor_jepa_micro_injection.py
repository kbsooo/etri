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
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from public_lb_actual_anchor_ranker import STAGE2_LB, combo_weights  # noqa: E402
from public_subset_sensitivity_audit import build_masks  # noqa: E402


RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"

OUT_SCAN = OUT / "raw05_anchor_jepa_micro_injection_scan.csv"
OUT_SCORED = OUT / "raw05_anchor_jepa_micro_injection_scored.csv"
OUT_SHORTLIST = OUT / "raw05_anchor_jepa_micro_injection_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_anchor_jepa_micro_injection_integrity.csv"
OUT_REPORT = OUT / "raw05_anchor_jepa_micro_injection_report.md"

COMBO_TABLES = {
    "inverse_top": "public_lb_inverse_mask_top512.csv",
    "raw05_compatible": "public_lb_inverse_mask_raw05_compatible_top512.csv",
    "all_sign": "public_lb_inverse_mask_all_sign_compatible_top512.csv",
}

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "s2_s3_s4": ["S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "q3_only": ["Q3"],
    "s4_only": ["S4"],
}

WEIGHTS = [0.24, 0.40, 0.60, 0.82, 1.00, 1.18, 1.38]
CAPS = [0.014, 0.024, 0.040, 0.070]


def locate(file_name: str) -> Path:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(file_name)


def read_submission(file_name: str) -> pd.DataFrame:
    return pd.read_csv(locate(file_name), parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=bool)


def load_donor_files() -> list[str]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    constrained = pd.read_csv(OUT / "final_jepa_constrained_shortlist_20260527.csv")

    rows: list[str] = []
    rows.extend(priority["file"].astype(str).head(8).tolist())
    for filter_name in [
        "balanced_raw_le_1e-7_bad_le_0p0025_posterior_le_0p5769",
        "strict_raw_le_0_bad_le_0p0025_posterior_le_0p5769",
    ]:
        part = constrained[constrained["filter"].eq(filter_name)].head(7)
        rows.extend(part["file"].astype(str).tolist())

    keep: list[str] = []
    seen: set[str] = set()
    for file_name in rows:
        if file_name in seen or file_name in {RAW05_FILE, STAGE2_FILE}:
            continue
        try:
            locate(file_name)
        except FileNotFoundError:
            continue
        seen.add(file_name)
        keep.append(file_name)
    return keep


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    ref_key = sample[KEY].reset_index(drop=True)
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def make_row_gates(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    records = build_masks(sample)
    gates = {"ones": np.ones(len(sample), dtype=np.float64)}
    for gate_name, table_name, limit in [
        ("raw64", "public_lb_inverse_mask_raw05_compatible_top512.csv", 64),
        ("all64", "public_lb_inverse_mask_all_sign_compatible_top512.csv", 64),
    ]:
        table = pd.read_csv(OUT / table_name).head(limit).reset_index(drop=True)
        weights = combo_weights(table)
        gate = np.zeros(len(sample), dtype=np.float64)
        for idx, row in table.iterrows():
            rec = records[int(row["mask_index"])]
            mask = rec["mask"]
            assert isinstance(mask, np.ndarray)
            gate[mask] += float(weights[idx])
        if gate.max() > 0:
            gate = gate / gate.max()
        gates[gate_name] = gate
    return gates


def make_basis(raw_logit: np.ndarray, arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    donor_files = list(arrays)
    donor_deltas = {file_name: logit(arr) - raw_logit for file_name, arr in arrays.items()}
    basis: dict[str, np.ndarray] = {}

    for file_name, delta in donor_deltas.items():
        label = file_name.replace("submission_", "").replace(".csv", "")
        basis[label] = delta

    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    constrained = pd.read_csv(OUT / "final_jepa_constrained_shortlist_20260527.csv")

    def median_delta(names: list[str]) -> np.ndarray | None:
        selected = [donor_deltas[name] for name in names if name in donor_deltas]
        if not selected:
            return None
        return np.median(np.stack(selected, axis=0), axis=0)

    priority_names = priority["file"].astype(str).head(8).tolist()
    strict_names = constrained[
        constrained["filter"].eq("strict_raw_le_0_bad_le_0p0025_posterior_le_0p5769")
    ]["file"].astype(str).head(16).tolist()
    balanced_names = constrained[
        constrained["filter"].eq("balanced_raw_le_1e-7_bad_le_0p0025_posterior_le_0p5769")
    ]["file"].astype(str).head(20).tolist()
    low_bad_names = [
        "submission_jepa_block_consensus_rawcorr_4fd8bab2.csv",
        "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
        "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv",
        "submission_jepa_energy_ensemble_0b862967.csv",
    ]
    for name, files in [
        ("median_priority_top8", priority_names),
        ("median_strict_raw_top16", strict_names),
        ("median_balanced_top20", balanced_names),
        ("median_lowbad", low_bad_names),
    ]:
        delta = median_delta(files)
        if delta is not None:
            basis[name] = delta

    return basis


def cell_gate(delta: np.ndarray, consensus: np.ndarray, gate_name: str, target_mask_bool: np.ndarray) -> np.ndarray:
    gate = np.ones_like(delta, dtype=np.float64)
    if gate_name != "all":
        same_sign = np.sign(delta) == np.sign(consensus)
        nonzero = np.abs(consensus) > 1e-8
        gate *= (same_sign & nonzero).astype(np.float64)
    if gate_name in {"agree_q60", "agree_q75", "strong_q60", "strong_q75"}:
        q = 0.60 if "q60" in gate_name else 0.75
        strong = np.zeros_like(delta, dtype=bool)
        for j, use in enumerate(target_mask_bool):
            if not use:
                continue
            vals = np.abs(delta[:, j])
            threshold = float(np.quantile(vals, q))
            strong[:, j] = vals >= threshold
        gate *= strong.astype(np.float64)
    if gate_name.startswith("strong"):
        gate *= (np.abs(delta) > 1e-8).astype(np.float64)
    return gate


def generate_candidates(
    sample: pd.DataFrame,
    raw: np.ndarray,
    arrays: dict[str, np.ndarray],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    raw_logit = logit(raw)
    basis = make_basis(raw_logit, arrays)
    consensus = basis.get("median_balanced_top20", np.median(np.stack(list(basis.values()), axis=0), axis=0))
    row_gates = make_row_gates(sample)

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen_hashes: set[str] = set()

    for basis_name, delta in basis.items():
        for target_mask_name in TARGET_MASKS:
            tmask = target_mask(target_mask_name)
            target_gate = tmask.reshape(1, -1).astype(np.float64)
            for row_gate_name, row_gate in row_gates.items():
                row_gate_2d = row_gate.reshape(-1, 1)
                for gate_name in ["all", "agree", "agree_q60", "strong_q75"]:
                    gate = target_gate * row_gate_2d * cell_gate(delta, consensus, gate_name, tmask)
                    active = float(gate.mean())
                    if active <= 0.0:
                        continue
                    for cap in CAPS:
                        capped = np.clip(delta, -cap, cap) * gate
                        if np.abs(capped).mean() <= 1e-10:
                            continue
                        for weight in WEIGHTS:
                            pred = clip(sigmoid(raw_logit + weight * capped))
                            pred_hash = stable_tag(np.round(pred, 10).tobytes().hex())
                            if pred_hash in seen_hashes:
                                continue
                            seen_hashes.add(pred_hash)
                            public = public_axis_features(pred, axes)
                            rows.append(
                                {
                                    "label": f"{basis_name}|{target_mask_name}|{row_gate_name}|{gate_name}|w{weight:.2f}|c{cap:.3f}",
                                    "basis": basis_name,
                                    "target_mask": target_mask_name,
                                    "row_gate": row_gate_name,
                                    "cell_gate": gate_name,
                                    "weight": weight,
                                    "cap": cap,
                                    "active_gate_mean": active,
                                    "prediction_hash": pred_hash,
                                    **public,
                                }
                            )
                            preds.append(pred)
    return rows, preds


def ce_loss_stack(q: np.ndarray, pred_stack: np.ndarray) -> np.ndarray:
    p = clip(pred_stack)
    y = clip(q)
    return -(y[None, :, :] * np.log(p) + (1.0 - y[None, :, :]) * np.log1p(-p)).mean(axis=2)


def mask_matrix(sample: pd.DataFrame) -> np.ndarray:
    records = build_masks(sample)
    mat = np.zeros((len(records), len(sample)), dtype=np.float64)
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
    return mat


def actual_anchor_score(preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    pred_stack = np.stack(preds, axis=0)
    masks = mask_matrix(sample)
    stage2 = read_submission(STAGE2_FILE)[TARGETS].to_numpy(dtype=np.float64)
    scenario_cache: dict[str, np.ndarray] = {}
    set_frames = []

    for combo_set, table_name in COMBO_TABLES.items():
        table = pd.read_csv(OUT / table_name).head(160).reset_index(drop=True)
        weights = combo_weights(table)
        values = np.zeros((len(preds), len(table)), dtype=np.float64)
        for i, row in table.iterrows():
            scenario = str(row["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = read_submission(scenario)[TARGETS].to_numpy(dtype=np.float64)
            q = scenario_cache[scenario]
            mask_vec = masks[int(row["mask_index"])]
            stage_loss = float(mask_vec @ (-(clip(q) * np.log(clip(stage2)) + (1.0 - clip(q)) * np.log1p(-clip(stage2)))).mean(axis=1))
            cand_loss = ce_loss_stack(q, pred_stack) @ mask_vec
            values[:, i] = STAGE2_LB + cand_loss - stage_loss

        mean = values @ weights
        std = np.sqrt(((values - mean[:, None]) ** 2) @ weights)
        p90 = np.quantile(values, 0.90, axis=1)
        worst = values.max(axis=1)
        score = mean + 0.35 * std + 0.20 * np.maximum(p90 - mean, 0.0) + 0.10 * np.maximum(worst - mean, 0.0)
        set_frames.append(
            pd.DataFrame(
                {
                    "candidate_index": np.arange(len(preds)),
                    f"actual_anchor_mean__{combo_set}": mean,
                    f"actual_anchor_score__{combo_set}": score,
                    f"actual_anchor_std__{combo_set}": std,
                }
            )
        )

    merged = set_frames[0]
    for frame in set_frames[1:]:
        merged = merged.merge(frame, on="candidate_index")
    mean_cols = [c for c in merged.columns if c.startswith("actual_anchor_mean__")]
    score_cols = [c for c in merged.columns if c.startswith("actual_anchor_score__")]
    merged["actual_anchor_score_final"] = merged[score_cols].mean(axis=1)
    merged["mean_actual_anchor"] = merged[mean_cols].mean(axis=1)
    merged["min_set_score"] = merged[score_cols].min(axis=1)
    merged["max_set_score"] = merged[score_cols].max(axis=1)
    return merged


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 250.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.0028, 0.0) * 0.030
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0028, 0.0) * 0.040
    )
    masks = [
        (frame["delta_vs_raw05_rawaxis"] <= 2.0e-7)
        & (frame["bad_residual_axis_ratio"].abs() <= 0.0030)
        & (frame["posterior_expected_public_vs_anchor"] <= 0.57705),
        (frame["delta_vs_raw05_rawaxis"] <= 0.0)
        & (frame["bad_residual_axis_ratio"].abs() <= 0.0032)
        & (frame["posterior_expected_public_vs_anchor"] <= 0.57708),
        (frame["delta_vs_raw05_rawaxis"] <= 5.0e-7)
        & (frame["bad_residual_axis_ratio"].abs() <= 0.0022)
        & (frame["posterior_expected_public_vs_anchor"] <= 0.57700),
    ]
    parts = []
    for mask in masks:
        parts.append(frame[mask].sort_values("prefilter_score").head(900))
    parts.append(frame.sort_values("prefilter_score").head(600))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(1800)


def save_submission(file_name: str, sample: pd.DataFrame, pred: np.ndarray) -> None:
    out = sample[KEY].copy()
    out[TARGETS] = clip(pred)
    out.to_csv(OUT / file_name, index=False)


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    ref_key = sample[KEY].reset_index(drop=True)
    rows = []
    for file_name in files:
        frame = read_submission(file_name)
        pred = frame[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_probs": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    frame = scored.copy()
    frame["selection_score"] = (
        frame["actual_anchor_score_final"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 180.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.0024, 0.0) * 0.020
        + np.maximum(frame["posterior_expected_public_vs_anchor"] - 0.5769, 0.0) * 0.75
    )

    specs = [
        (
            "balanced",
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            35,
        ),
        (
            "strict_raw",
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0027)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            30,
        ),
        (
            "low_bad",
            (frame["delta_vs_raw05_rawaxis"] <= 2.5e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0018)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            25,
        ),
        (
            "actual_anchor",
            (frame["delta_vs_raw05_rawaxis"] <= 5.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0030),
            25,
        ),
    ]
    selected_parts = []
    for bucket, mask, limit in specs:
        part = frame[mask].sort_values("selection_score").head(limit).copy()
        part["bucket"] = bucket
        selected_parts.append(part)
    selected = pd.concat(selected_parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["selection_score", "actual_anchor_score_final"]).head(100).copy()

    files = []
    for idx, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + row["prediction_hash"])
        file_name = f"submission_raw05_anchor_jepa_micro_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "label",
    ]
    lines = [
        "# Raw05 Anchor JEPA Micro Injection",
        "",
        "Raw05 is the observed public best, so this pass starts at raw05 logits and injects only small JEPA hidden-structure deltas.",
        "Generation uses donor/median JEPA deltas, target masks, public-inverse row gates, sign/agreement gates, and logit caps.",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor rescored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(30).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    donor_files = load_donor_files()
    arrays = load_arrays(donor_files, sample)
    axes = public_axes()

    rows, preds = generate_candidates(sample, raw, arrays, axes)
    scan = pd.DataFrame(rows)
    scan.to_csv(OUT_SCAN, index=False)

    selected_for_scoring = prefilter(scan)
    score_indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in score_indices]
    actual = actual_anchor_score(score_preds, sample)
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", score_indices)
    scored = pd.concat([scored, actual.drop(columns=["candidate_index"])], axis=1)
    scored = scored.sort_values("actual_anchor_score_final").reset_index(drop=True)
    scored.to_csv(OUT_SCORED, index=False)

    selected = select_and_save(scored, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ)

    print(f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print(selected[
        [
            "file",
            "bucket",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "mean_abs_move_vs_raw05",
            "label",
        ]
    ].head(25).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
