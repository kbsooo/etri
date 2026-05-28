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

import local_lb_proxy_validation as lbv  # noqa: E402
from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sigmoid, stable_tag  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    actual_anchor_score,
    integrity,
    make_row_gates,
    read_submission,
    save_submission,
)


RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"

CVJEPA_FILES = {
    "full_nonq2": "submission_cvjepa_surprise_full_nonq2.csv",
    "full_nonq2_w030": "submission_cvjepa_surprise_full_nonq2_w030.csv",
    "full_nonq2_w020": "submission_cvjepa_surprise_full_nonq2_w020.csv",
    "core_q1_q3_s2_s4": "submission_cvjepa_surprise_core_q1_q3_s2_s4.csv",
    "q1_s2": "submission_cvjepa_surprise_q1_s2.csv",
    "q_targets": "submission_cvjepa_surprise_q_targets.csv",
    "s_targets": "submission_cvjepa_surprise_s_targets.csv",
}

TARGET_MASKS = {
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_s2": ["Q1", "S2"],
    "q_targets": ["Q1", "Q3"],
    "s_targets": ["S1", "S2", "S3", "S4"],
    "core_q1_q3_s2_s4": ["Q1", "Q3", "S2", "S4"],
    "q3_s2_s4": ["Q3", "S2", "S4"],
    "q1_only": ["Q1"],
    "q3_only": ["Q3"],
    "s2_only": ["S2"],
    "s4_only": ["S4"],
}

WEIGHTS = [0.04, 0.08, 0.14, 0.22, 0.34, 0.52, 0.78]
CAPS = [0.004, 0.008, 0.014, 0.024, 0.040]
DIRECTIONS = [1.0, -1.0]

OUT_SCAN = OUT / "raw05_cvjepa_surprise_micro_graft_scan.csv"
OUT_SCORED = OUT / "raw05_cvjepa_surprise_micro_graft_scored.csv"
OUT_SHORTLIST = OUT / "raw05_cvjepa_surprise_micro_graft_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_cvjepa_surprise_micro_graft_integrity.csv"
OUT_PROXY = OUT / "raw05_cvjepa_surprise_micro_graft_local_proxy.csv"
OUT_REPORT = OUT / "raw05_cvjepa_surprise_micro_graft_report.md"


def load_sample() -> pd.DataFrame:
    return (
        pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
        .sort_values(KEY)
        .reset_index(drop=True)
    )


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=bool)


def row_energy_gate(delta: np.ndarray, quantile: float) -> np.ndarray:
    energy = np.mean(np.abs(delta), axis=1)
    threshold = float(np.quantile(energy, quantile))
    return (energy >= threshold).astype(np.float64)


def load_basis(sample: pd.DataFrame) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    raw = read_submission(RAW05_FILE)
    stage2 = read_submission(STAGE2_FILE)
    ref_key = sample[KEY].reset_index(drop=True)
    if not raw[KEY].reset_index(drop=True).equals(ref_key):
        raise ValueError("raw05 key mismatch")
    if not stage2[KEY].reset_index(drop=True).equals(ref_key):
        raise ValueError("stage2 key mismatch")

    raw_arr = clip(raw[TARGETS].to_numpy(dtype=np.float64))
    stage2_arr = clip(stage2[TARGETS].to_numpy(dtype=np.float64))
    stage2_logit = logit(stage2_arr)
    basis: dict[str, np.ndarray] = {}
    for name, file_name in CVJEPA_FILES.items():
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"cvjepa key mismatch: {file_name}")
        arr = clip(frame[TARGETS].to_numpy(dtype=np.float64))
        basis[name] = logit(arr) - stage2_logit
    raw_stage2_delta = logit(raw_arr) - stage2_logit
    return basis, raw_arr, stage2_arr, raw_stage2_delta


def add_cvjepa_row_gates(sample: pd.DataFrame, basis: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    gates = make_row_gates(sample)
    full = basis["full_nonq2"]
    gates["surprise_top50"] = row_energy_gate(full, 0.50)
    gates["surprise_top70"] = row_energy_gate(full, 0.70)
    gates["surprise_top85"] = row_energy_gate(full, 0.85)
    return gates


def cell_gate(delta: np.ndarray, raw_stage2_delta: np.ndarray, gate_name: str, tmask: np.ndarray) -> np.ndarray:
    gate = np.ones_like(delta, dtype=np.float64)
    if gate_name in {"agree_raw", "agree_raw_q65", "agree_raw_q80"}:
        agree = np.sign(delta) == np.sign(raw_stage2_delta)
        active = np.abs(raw_stage2_delta) > 1e-8
        gate *= (agree & active).astype(np.float64)
    elif gate_name in {"anti_raw", "anti_raw_q65"}:
        anti = np.sign(delta) == -np.sign(raw_stage2_delta)
        active = np.abs(raw_stage2_delta) > 1e-8
        gate *= (anti & active).astype(np.float64)

    if gate_name in {"strong_q65", "agree_raw_q65", "anti_raw_q65", "strong_q80", "agree_raw_q80"}:
        q = 0.80 if "q80" in gate_name else 0.65
        strong = np.zeros_like(delta, dtype=bool)
        for j, use in enumerate(tmask):
            if not use:
                continue
            vals = np.abs(delta[:, j])
            threshold = float(np.quantile(vals, q))
            strong[:, j] = vals >= threshold
        gate *= strong.astype(np.float64)
    return gate


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def generate_candidates(
    sample: pd.DataFrame,
    basis: dict[str, np.ndarray],
    raw: np.ndarray,
    raw_stage2_delta: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    raw_logit = logit(raw)
    row_gates = add_cvjepa_row_gates(sample, basis)
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for basis_name, delta in basis.items():
        for target_mask_name in TARGET_MASKS:
            tmask = target_mask(target_mask_name)
            target_gate = tmask.reshape(1, -1).astype(np.float64)
            for row_gate_name, row_gate in row_gates.items():
                row_gate_2d = row_gate.reshape(-1, 1)
                for cell_gate_name in [
                    "all",
                    "agree_raw",
                    "anti_raw",
                    "strong_q65",
                    "agree_raw_q65",
                    "anti_raw_q65",
                    "strong_q80",
                    "agree_raw_q80",
                ]:
                    cgate = cell_gate(delta, raw_stage2_delta, cell_gate_name, tmask)
                    gate = target_gate * row_gate_2d * cgate
                    active = float(gate.mean())
                    if active <= 0.0:
                        continue
                    for cap in CAPS:
                        capped = np.clip(delta, -cap, cap) * gate
                        if float(np.abs(capped).mean()) <= 1e-12:
                            continue
                        for direction in DIRECTIONS:
                            for weight in WEIGHTS:
                                pred = clip(sigmoid(raw_logit + direction * weight * capped))
                                h = prediction_hash(pred)
                                if h in seen:
                                    continue
                                seen.add(h)
                                public = public_axis_features(pred, axes)
                                rows.append(
                                    {
                                        "label": (
                                            f"{basis_name}|{target_mask_name}|{row_gate_name}|"
                                            f"{cell_gate_name}|dir{direction:+.0f}|w{weight:.2f}|c{cap:.3f}"
                                        ),
                                        "basis": basis_name,
                                        "target_mask": target_mask_name,
                                        "row_gate": row_gate_name,
                                        "cell_gate": cell_gate_name,
                                        "direction": direction,
                                        "weight": weight,
                                        "cap": cap,
                                        "active_gate_mean": active,
                                        "prediction_hash": h,
                                        **public,
                                    }
                                )
                                preds.append(pred)
    scan = pd.DataFrame(rows)
    return scan, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["selection_score"] = (
        frame["actual_like_anchor_prefilter"]
        if "actual_like_anchor_prefilter" in frame.columns
        else frame["posterior_expected_public_vs_anchor"]
    )
    frame["selection_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(frame["raw_abs"] - 1.5e-6, 0.0) * 80.0
        + np.maximum(frame["bad_abs"] - 0.0025, 0.0) * 0.025
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0030, 0.0) * 0.040
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_abs"] <= 0.0030)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0030),
            ["selection_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.0040)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0040),
            ["posterior_expected_public_vs_anchor"],
            700,
        ),
        (
            (frame["raw_abs"] <= 1.5e-6)
            & (frame["bad_abs"] <= 0.0020)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0035),
            ["bad_abs", "posterior_expected_public_vs_anchor"],
            700,
        ),
        (
            frame["mean_abs_move_vs_raw05"] <= 0.0020,
            ["selection_score"],
            500,
        ),
    ]
    parts = []
    for mask, sort_cols, n in specs:
        cols = [c for c in sort_cols if c in frame.columns]
        parts.append(frame[mask].sort_values(cols).head(n))
    parts.append(frame.sort_values("selection_score").head(500))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("selection_score").head(2200)


def score_candidates(prefiltered: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    score_indices = prefiltered.index.to_numpy(dtype=int)
    score_preds = [preds[int(i)] for i in score_indices]
    actual = actual_anchor_score(score_preds, sample)
    scored = prefiltered.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", score_indices)
    scored = pd.concat([scored, actual.drop(columns=["candidate_index"])], axis=1)
    scored["score_raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["score_bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["graft_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 160.0
        + np.maximum(scored["score_raw_abs"] - 1.0e-6, 0.0) * 45.0
        + np.maximum(scored["score_bad_abs"] - 0.0022, 0.0) * 0.018
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57710, 0.0) * 0.50
    )
    return scored.sort_values(["graft_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    frame = scored.copy()
    specs = [
        (
            "raw_tight_lowbad",
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["score_bad_abs"] <= 0.0022)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0030),
            ["graft_score", "actual_anchor_score_final"],
            24,
        ),
        (
            "strict_raw",
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["score_bad_abs"] <= 0.0032)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0035),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            24,
        ),
        (
            "actual_probe",
            (frame["delta_vs_raw05_rawaxis"] <= 5.0e-7)
            & (frame["score_bad_abs"] <= 0.0040)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0040),
            ["actual_anchor_score_final", "graft_score"],
            28,
        ),
        (
            "posterior_probe",
            (frame["score_raw_abs"] <= 2.0e-6)
            & (frame["score_bad_abs"] <= 0.0040),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            24,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        cols = [c for c in sort_cols if c in frame.columns]
        part = frame[mask].sort_values(cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(frame.sort_values(["graft_score", "actual_anchor_score_final"]).head(16).assign(bucket="rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["graft_score", "actual_anchor_score_final"]).head(88).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_cvjepa_surprise_graft_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def local_proxy(selected: pd.DataFrame) -> pd.DataFrame:
    known, _, _ = lbv.load_known_and_candidates()
    model_scores, _ = lbv.build_model_scores(known)
    ranker_scores = pd.read_csv(OUT / "public_lb_actual_anchor_ranker_scores.csv")
    raw05_row = ranker_scores[ranker_scores["file"].astype(str).eq(RAW05_FILE)].copy()
    cols = sorted(set(raw05_row.columns).union(selected.columns))
    cand = pd.concat(
        [raw05_row.reindex(columns=cols), selected.reindex(columns=cols)],
        ignore_index=True,
        sort=False,
    )
    pred = lbv.predict_candidates(known, model_scores, lbv.add_derived_features(cand))
    return pred[pred["file"].astype(str).ne(RAW05_FILE)].copy()


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, proxy: pd.DataFrame, integ: pd.DataFrame) -> None:
    top_cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "graft_score",
        "label",
    ]
    proxy_cols = [
        "file",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
    ]
    lines = [
        "# Raw05 Cross-View JEPA Surprise Micro Graft",
        "",
        "Starts from the observed raw05 public-best submission and injects capped `cvjepa - stage2` logit residuals.",
        "This tests whether the strong cross-view JEPA OOF signal can survive under raw05-axis and bad-axis constraints.",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor rescored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved By Graft Score",
        "",
        "```csv",
        selected[top_cols].head(32).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Local LB Proxy",
        "",
        "```csv",
        proxy.sort_values("available_raw05_relative_lb_proxy_mean")[proxy_cols].head(32).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(32).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sample()
    basis, raw, _stage2, raw_stage2_delta = load_basis(sample)
    axes = public_axes()
    scan, preds = generate_candidates(sample, basis, raw, raw_stage2_delta, axes)
    scan.to_csv(OUT_SCAN, index=False)

    pre = prefilter(scan)
    scored = score_candidates(pre, preds, sample)
    scored.to_csv(OUT_SCORED, index=False)

    selected = select_and_save(scored, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].astype(str).tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    proxy = local_proxy(selected)
    proxy.to_csv(OUT_PROXY, index=False)
    write_report(scan, scored, selected, proxy, integ)

    print(f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print("[selected]")
    print(
        selected[
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
        ]
        .head(24)
        .round(10)
        .to_string(index=False)
    )
    print("[local proxy]")
    print(
        proxy.sort_values("available_raw05_relative_lb_proxy_mean")[
            [
                "file",
                "available_raw05_relative_lb_proxy_mean",
                "available_raw05_relative_delta_vs_raw05_public",
                "available_raw05_relative_model_spread",
                "actual_anchor_score_final",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
            ]
        ]
        .head(24)
        .round(10)
        .to_string(index=False)
    )
    print("wrote:", OUT_REPORT)


if __name__ == "__main__":
    main()
