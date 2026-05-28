from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import raw05_cvjepa_surprise_micro_graft as graft  # noqa: E402
from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sigmoid, stable_tag  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, integrity, read_submission, save_submission  # noqa: E402


ANCHORS = {
    "e40": "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "lowbad_bal": "submission_raw05_jepa_lowbadcon_71601b5f.csv",
    "lowbad_edge": "submission_raw05_jepa_lowbadcon_2240eb29.csv",
    "energyfront": "submission_raw05_jepa_energyfront_a190aa25.csv",
    "efmicro": "submission_raw05_jepa_efmicro_1859bae9.csv",
    "axisbridge": "submission_raw05_jepa_axisbridge_45f2ba5a.csv",
}

BASIS_KEEP = ["full_nonq2_w020", "full_nonq2_w030", "q1_s2", "s_targets"]
MASK_KEEP = ["q1_s2", "s2_only", "q3_s2_s4", "s_targets", "no_q2"]
ROW_KEEP = ["ones", "raw64", "surprise_top50", "surprise_top70"]
CELL_KEEP = ["all", "anti_raw", "anti_raw_q65", "agree_raw_q65", "strong_q65"]
WEIGHTS = [0.04, 0.08, 0.14, 0.22, 0.34]
CAPS = [0.006, 0.014, 0.024]
DIRECTIONS = [1.0, -1.0]

OUT_SCAN = OUT / "frontier_cvjepa_surprise_micro_refine_scan.csv"
OUT_SCORED = OUT / "frontier_cvjepa_surprise_micro_refine_scored.csv"
OUT_SHORTLIST = OUT / "frontier_cvjepa_surprise_micro_refine_shortlist.csv"
OUT_PROXY = OUT / "frontier_cvjepa_surprise_micro_refine_local_proxy.csv"
OUT_INTEGRITY = OUT / "frontier_cvjepa_surprise_micro_refine_integrity.csv"
OUT_REPORT = OUT / "frontier_cvjepa_surprise_micro_refine_report.md"


def existing_anchors() -> dict[str, str]:
    out = {}
    for name, file_name in ANCHORS.items():
        try:
            read_submission(file_name)
        except FileNotFoundError:
            continue
        out[name] = file_name
    if not out:
        raise FileNotFoundError("no anchor files found")
    return out


def generate_for_anchors(
    sample: pd.DataFrame,
    basis: dict[str, np.ndarray],
    stage2: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    row_gates_all = graft.add_cvjepa_row_gates(sample, basis)
    row_gates = {name: row_gates_all[name] for name in ROW_KEEP if name in row_gates_all}
    anchors = existing_anchors()
    ref_key = sample[KEY].reset_index(drop=True)

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    stage2_logit = logit(stage2)

    for anchor_name, anchor_file in anchors.items():
        anchor_frame = read_submission(anchor_file)
        if not anchor_frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"anchor key mismatch: {anchor_file}")
        anchor = clip(anchor_frame[TARGETS].to_numpy(dtype=np.float64))
        anchor_logit = logit(anchor)
        anchor_stage2_delta = anchor_logit - stage2_logit

        for basis_name in BASIS_KEEP:
            delta = basis[basis_name]
            for target_mask_name in MASK_KEEP:
                tmask = graft.target_mask(target_mask_name)
                target_gate = tmask.reshape(1, -1).astype(np.float64)
                for row_gate_name, row_gate in row_gates.items():
                    row_gate_2d = row_gate.reshape(-1, 1)
                    for cell_gate_name in CELL_KEEP:
                        cgate = graft.cell_gate(delta, anchor_stage2_delta, cell_gate_name, tmask)
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
                                    pred = clip(sigmoid(anchor_logit + direction * weight * capped))
                                    h = graft.prediction_hash(pred)
                                    if h in seen:
                                        continue
                                    seen.add(h)
                                    public = public_axis_features(pred, axes)
                                    rows.append(
                                        {
                                            "label": (
                                                f"{anchor_name}:{basis_name}|{target_mask_name}|{row_gate_name}|"
                                                f"{cell_gate_name}|dir{direction:+.0f}|w{weight:.2f}|c{cap:.3f}"
                                            ),
                                            "anchor_name": anchor_name,
                                            "anchor_file": anchor_file,
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
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["prefilter_score"] = (
        frame["actual_anchor_prior"]
        if "actual_anchor_prior" in frame.columns
        else frame["posterior_expected_public_vs_anchor"]
    )
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(frame["raw_abs"] - 1.0e-6, 0.0) * 50.0
        + np.maximum(frame["bad_abs"] - 0.0024, 0.0) * 0.016
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0025, 0.0) * 0.020
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_abs"] <= 0.0026)
            & (frame["mean_abs_move_vs_raw05"] <= 0.0030),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["raw_abs"] <= 8.0e-7)
            & (frame["bad_abs"] <= 0.0015),
            ["bad_abs", "posterior_expected_public_vs_anchor"],
            700,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.0035),
            ["posterior_expected_public_vs_anchor"],
            700,
        ),
    ]
    parts = []
    for mask, sort_cols, n in specs:
        cols = [c for c in sort_cols if c in frame.columns]
        parts.append(frame[mask].sort_values(cols).head(n))
    parts.append(frame.sort_values("prefilter_score").head(500))
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").sort_values("prefilter_score").head(2400)


def score_and_select(prefiltered: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = prefiltered.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[int(i)] for i in idx], sample)
    scored = prefiltered.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", idx)
    scored = pd.concat([scored, actual.drop(columns=["candidate_index"])], axis=1)
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["refine_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 160.0
        + np.maximum(scored["bad_abs"] - 0.0022, 0.0) * 0.014
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.45
    )
    scored = scored.sort_values(["refine_score", "actual_anchor_score_final"]).reset_index(drop=True)

    specs = [
        (
            "actual_frontier",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7) & (scored["bad_abs"] <= 0.0025),
            ["actual_anchor_score_final", "refine_score"],
            28,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0) & (scored["bad_abs"] <= 0.0032),
            ["refine_score", "actual_anchor_score_final"],
            24,
        ),
        (
            "low_bad",
            (scored["raw_abs"] <= 1.0e-6) & (scored["bad_abs"] <= 0.0012),
            ["bad_abs", "actual_anchor_score_final"],
            24,
        ),
        (
            "posterior",
            (scored["raw_abs"] <= 1.5e-6) & (scored["bad_abs"] <= 0.0035),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            24,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        cols = [c for c in sort_cols if c in scored.columns]
        part = scored[mask].sort_values(cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.head(18).assign(bucket="rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["refine_score", "actual_anchor_score_final"]).head(88).copy()
    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_frontier_cvjepa_refine_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return scored, selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, proxy: pd.DataFrame, integ: pd.DataFrame) -> None:
    selected_cols = [
        "file",
        "bucket",
        "anchor_name",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "refine_score",
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
        "# Frontier Cross-View JEPA Surprise Micro Refine",
        "",
        "Injects capped cross-view JEPA surprise residuals into existing raw05-compatible frontier candidates.",
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
        selected[selected_cols].head(32).round(10).to_csv(index=False).strip(),
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
    sample = graft.load_sample()
    basis, _raw, stage2, _raw_stage2_delta = graft.load_basis(sample)
    axes = public_axes()
    scan, preds = generate_for_anchors(sample, basis, stage2, axes)
    scan.to_csv(OUT_SCAN, index=False)
    pre = prefilter(scan)
    scored, selected = score_and_select(pre, preds, sample)
    scored.to_csv(OUT_SCORED, index=False)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].astype(str).tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    proxy = graft.local_proxy(selected)
    proxy.to_csv(OUT_PROXY, index=False)
    write_report(scan, scored, selected, proxy, integ)

    print(f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print("[selected]")
    print(
        selected[
            [
                "file",
                "bucket",
                "anchor_name",
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
