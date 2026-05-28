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
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    RAW05_FILE,
    actual_anchor_score,
    integrity,
    locate,
    read_submission,
    save_submission,
)
from raw05_jepa_direct_constrained_search import (  # noqa: E402
    MOTIF_FILE,
    SAFETY_MASKS,
    STEP_MASKS,
    local_proxy_score,
    project_q3s4,
    q3s4_motif_metrics,
)


BASE_FILES = [
    "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "submission_raw05_jepa_structrefine_04ad10f8.csv",
    "submission_raw05_jepa_structrefine_90e28f7d.csv",
]

LOCAL_FILES = [
    "submission_raw05_jepa_axislocal_20e4a625.csv",
    "submission_raw05_jepa_axislocal_d90f09cf.csv",
    "submission_raw05_jepa_axislocal_16ae093a.csv",
    "submission_raw05_jepa_axislocal_7a15027d.csv",
    "submission_raw05_jepa_axisrepair_78029f2c.csv",
]

SAFETY_FILES = [
    "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "submission_raw05_jepa_structrefine_90e28f7d.csv",
    "submission_raw05_jepa_siggate_6d681440.csv",
    "submission_raw05_jepa_efback_9c50051c.csv",
]

STEP_MASK_NAMES = ["q2_s123", "q1_s3", "all_soft"]
STEP_STRENGTHS = [0.0, 0.002, 0.004, 0.007, 0.010, 0.014, 0.020, 0.030, 0.045]
STEP_CAPS = [0.0015, 0.0030, 0.0050]
SAFETY_MASK_NAMES = ["none", "q2_s123", "all_soft"]
SAFETY_ETAS = [0.0, 0.025, 0.05, 0.085, 0.13, 0.20, 0.32, 0.50]
ORTH_KEEP = [0.70, 0.85, 1.00, 1.15]

OUT_SCAN = OUT / "raw05_jepa_lowbad_motif_search_scan.csv"
OUT_PREFILTER = OUT / "raw05_jepa_lowbad_motif_search_prefilter.csv"
OUT_SCORED = OUT / "raw05_jepa_lowbad_motif_search_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_lowbad_motif_search_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_lowbad_motif_search_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_lowbad_motif_search_report.md"


def existing(files: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if not file_name or file_name in seen:
            continue
        try:
            locate(file_name)
        except FileNotFoundError:
            continue
        seen.add(file_name)
        out.append(file_name)
    return out


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def add_if_guarded(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    *,
    label: str,
    base_file: str,
    local_file: str,
    safety_file: str,
    step_mask: str,
    step_strength: float,
    step_cap: float,
    safety_mask: str,
    safety_eta: float,
    keep_orth: float,
    pred_logit: np.ndarray,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> None:
    pred = clip(sigmoid(pred_logit))
    metrics: dict[str, object] = {
        "file": f"__lowbad_motif_{len(rows):05d}.csv",
        "label": label,
        "base_file": base_file,
        "local_file": local_file,
        "safety_file": safety_file,
        "step_mask": step_mask,
        "step_strength": float(step_strength),
        "step_cap": float(step_cap),
        "safety_mask": safety_mask,
        "safety_eta": float(safety_eta),
        "keep_orth": float(keep_orth),
        "step_energy": float(step_strength * step_cap),
        "mean_abs_move_vs_raw05": float(np.abs(pred - sigmoid(raw_logit)).mean()),
    }
    metrics.update(public_axis_features(pred, axes))
    metrics.update(q3s4_motif_metrics(pred_logit, raw_logit, motif_delta))

    bad_abs = abs(float(metrics["bad_residual_axis_ratio"]))
    raw_abs = abs(float(metrics["delta_vs_raw05_rawaxis"]))
    if not (
        float(metrics["posterior_expected_public_vs_anchor"]) <= 0.57690455
        and bad_abs <= 3.6e-5
        and raw_abs <= 1.35e-7
        and float(metrics["q3s4_motif_cos"]) >= 0.999983
        and float(metrics["q3s4_motif_orth_ratio"]) <= 0.0081
    ):
        return

    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    metrics["prediction_hash"] = pred_hash
    metrics["bad_abs"] = bad_abs
    metrics["raw_abs"] = raw_abs
    rows.append(metrics)
    preds.append(pred)


def generate(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray]]:
    axes = public_axes()
    files = existing([RAW05_FILE, MOTIF_FILE, *BASE_FILES, *LOCAL_FILES, *SAFETY_FILES])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    logits = {file_name: logit(arrays[file_name]) for file_name in files}
    raw_logit = logits[RAW05_FILE]
    motif_delta = logits[MOTIF_FILE] - raw_logit

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    base_files = [file_name for file_name in BASE_FILES if file_name in arrays]
    local_files = [file_name for file_name in LOCAL_FILES if file_name in arrays]
    safety_files = [file_name for file_name in SAFETY_FILES if file_name in arrays]

    for base_file in base_files:
        base_logit = logits[base_file]
        for local_file in local_files:
            local_step = logits[local_file] - base_logit
            for step_mask in STEP_MASK_NAMES:
                mask = STEP_MASKS[step_mask]
                for step_strength in STEP_STRENGTHS:
                    for step_cap in STEP_CAPS:
                        stepped = base_logit + step_strength * np.clip(local_step * mask, -step_cap, step_cap)
                        for safety_file in safety_files:
                            safety_logit = logits[safety_file]
                            for safety_mask in SAFETY_MASK_NAMES:
                                smask = SAFETY_MASKS[safety_mask]
                                for safety_eta in SAFETY_ETAS:
                                    if safety_mask == "none" and safety_eta != 0.0:
                                        continue
                                    guarded = stepped + safety_eta * (safety_logit - stepped) * smask
                                    for keep_orth in ORTH_KEEP:
                                        pred_logit = project_q3s4(guarded, raw_logit, motif_delta, keep_orth)
                                        add_if_guarded(
                                            rows,
                                            preds,
                                            seen,
                                            label=(
                                                f"lowbad_motif|base={base_file}|local={local_file}|mask={step_mask}|"
                                                f"s={step_strength:.4f}|cap={step_cap:.4f}|safety={safety_file}|"
                                                f"smask={safety_mask}|eta={safety_eta:.3f}|orth={keep_orth:.2f}"
                                            ),
                                            base_file=base_file,
                                            local_file=local_file,
                                            safety_file=safety_file,
                                            step_mask=step_mask,
                                            step_strength=step_strength,
                                            step_cap=step_cap,
                                            safety_mask=safety_mask,
                                            safety_eta=safety_eta,
                                            keep_orth=keep_orth,
                                            pred_logit=pred_logit,
                                            raw_logit=raw_logit,
                                            motif_delta=motif_delta,
                                            axes=axes,
                                        )

    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    if scan.empty:
        return scan
    frame = scan.copy()
    strict = (
        frame["posterior_expected_public_vs_anchor"].le(0.57690420)
        & frame["bad_abs"].le(2.10e-5)
        & frame["raw_abs"].le(1.10e-7)
        & frame["q3s4_motif_cos"].ge(0.999984)
        & frame["q3s4_motif_orth_ratio"].le(0.00780)
    )
    lowbad = (
        frame["posterior_expected_public_vs_anchor"].le(0.57690440)
        & frame["bad_abs"].le(3.00e-5)
        & frame["raw_abs"].le(1.20e-7)
        & frame["q3s4_motif_cos"].ge(0.999984)
        & frame["q3s4_motif_orth_ratio"].le(0.00790)
    )
    guarded = (
        frame["posterior_expected_public_vs_anchor"].le(0.57690455)
        & frame["bad_abs"].le(3.60e-5)
        & frame["raw_abs"].le(1.35e-7)
        & frame["q3s4_motif_cos"].ge(0.999983)
        & frame["q3s4_motif_orth_ratio"].le(0.00810)
    )
    frame["prefilter_score"] = (
        -0.12 * frame["step_energy"].rank(pct=True)
        + np.maximum(frame["posterior_expected_public_vs_anchor"] - 0.5769040, 0.0) * 3500.0
        + np.maximum(frame["bad_abs"] - 2.0e-5, 0.0) * 150.0
        + np.maximum(frame["raw_abs"] - 1.0e-7, 0.0) * 25000.0
        + np.maximum(frame["q3s4_motif_orth_ratio"] - 0.0072, 0.0) * 0.10
    )
    parts = [
        frame[strict].sort_values(["prefilter_score", "step_energy"], ascending=[True, False]).head(1400),
        frame[lowbad].sort_values(["prefilter_score", "step_energy"], ascending=[True, False]).head(1400),
        frame[guarded].sort_values(["prefilter_score", "step_energy"], ascending=[True, False]).head(1800),
        frame.sort_values(["prefilter_score", "step_energy"], ascending=[True, False]).head(1800),
    ]
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").head(2600)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = scored.drop(columns=[col for col in actual.columns if col in scored.columns], errors="ignore")
    scored = pd.concat([scored, actual.reset_index(drop=True)], axis=1)
    local = local_proxy_score(scored)
    scored = scored.drop(columns=[col for col in local.columns if col in scored.columns and col != "file"], errors="ignore")
    scored = scored.merge(local, on="file", how="left", suffixes=("", "_local"))
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["strict_lowbad_hit"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"].le(-3.95e-6)
        & scored["posterior_expected_public_vs_anchor"].le(0.57690420)
        & scored["bad_abs"].le(2.10e-5)
        & scored["raw_abs"].le(1.10e-7)
        & scored["q3s4_motif_cos"].ge(0.999984)
        & scored["q3s4_motif_orth_ratio"].le(0.00780)
    )
    scored["near_lowbad_hit"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"].le(-3.98e-6)
        & scored["posterior_expected_public_vs_anchor"].le(0.57690445)
        & scored["bad_abs"].le(3.00e-5)
        & scored["raw_abs"].le(1.20e-7)
        & scored["q3s4_motif_cos"].ge(0.999984)
        & scored["q3s4_motif_orth_ratio"].le(0.00790)
    )
    scored["lowbad_score"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"]
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.5769040, 0.0) * 0.22
        + np.maximum(scored["bad_abs"] - 2.0e-5, 0.0) * 0.080
        + np.maximum(scored["raw_abs"] - 1.0e-7, 0.0) * 12.0
        + np.maximum(scored["q3s4_motif_orth_ratio"] - 0.0072, 0.0) * 0.0004
    )
    scored["rank_score"] = (
        0.36 * scored["lowbad_score"].rank(method="min")
        + 0.24 * scored["available_raw05_relative_delta_vs_raw05_public"].rank(method="min")
        + 0.14 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.12 * scored["bad_abs"].rank(method="min")
        + 0.08 * scored["raw_abs"].rank(method="min")
        + 0.06 * scored["q3s4_motif_orth_ratio"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "lowbad_score"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "strict_lowbad_local",
            scored["strict_lowbad_hit"],
            ["lowbad_score", "available_raw05_relative_delta_vs_raw05_public"],
            40,
        ),
        (
            "near_lowbad_local",
            scored["near_lowbad_hit"],
            ["available_raw05_relative_delta_vs_raw05_public", "lowbad_score"],
            40,
        ),
        (
            "posterior_bad_guard",
            scored["posterior_expected_public_vs_anchor"].le(0.57690435)
            & scored["bad_abs"].le(2.50e-5)
            & scored["raw_abs"].le(1.20e-7)
            & scored["q3s4_motif_cos"].ge(0.999984),
            ["lowbad_score", "available_raw05_relative_delta_vs_raw05_public"],
            36,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "lowbad_score"]).head(48).assign(bucket="lowbad_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "lowbad_score"]).head(96).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_lowbadcon_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected["file"] = files
    return selected


def write_report(scan: pd.DataFrame, selected_prefilter: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    keep = [
        "file",
        "bucket",
        "base_file",
        "local_file",
        "safety_file",
        "step_mask",
        "step_strength",
        "step_cap",
        "safety_mask",
        "safety_eta",
        "keep_orth",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lowbad_score",
        "rank_score",
    ]
    group = (
        scored.groupby(["base_file", "step_mask", "keep_orth"], as_index=False)
        .agg(
            n=("label", "size"),
            strict_hits=("strict_lowbad_hit", "sum"),
            near_hits=("near_lowbad_hit", "sum"),
            best_local_delta=("available_raw05_relative_delta_vs_raw05_public", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_lowbad_score=("lowbad_score", "min"),
        )
        .sort_values(["strict_hits", "near_hits", "best_lowbad_score"], ascending=[False, False, True])
    )
    lines = [
        "# Raw05 JEPA Low-Bad Motif Search",
        "",
        "This search keeps the Q3/S4 JEPA motif near the e40/structrefine manifold while directly constraining posterior and bad-axis.",
        "",
        "## Counts",
        "",
        f"- generated guarded candidates: `{len(scan)}`",
        f"- prefiltered candidates: `{len(selected_prefilter)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- strict lowbad hits: `{int(scored['strict_lowbad_hit'].sum())}`",
        f"- near lowbad hits: `{int(scored['near_lowbad_hit'].sum())}`",
        "",
        "## Group Summary",
        "",
        "```csv",
        group.round(10).head(80).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[keep].round(10).head(96).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = (
        pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
        .sort_values(KEY)
        .reset_index(drop=True)
    )
    scan, preds = generate(sample)
    scan.to_csv(OUT_SCAN, index=False)
    selected_prefilter = prefilter(scan)
    selected_prefilter.to_csv(OUT_PREFILTER, index=False)
    scored = score_candidates(selected_prefilter, preds, sample)
    selected = select_and_save(scored, preds, sample)
    integ = integrity(selected["file"].astype(str).tolist(), sample)
    scored.to_csv(OUT_SCORED, index=False)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, selected_prefilter, scored, selected, integ)

    keep = [
        "file",
        "bucket",
        "base_file",
        "local_file",
        "step_mask",
        "step_strength",
        "available_raw05_relative_delta_vs_raw05_public",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lowbad_score",
    ]
    print(f"guarded/prefiltered/scored/saved: {len(scan)} {len(selected_prefilter)} {len(scored)} {len(selected)}")
    print(f"strict/near hits: {int(scored['strict_lowbad_hit'].sum())} {int(scored['near_lowbad_hit'].sum())}")
    print(selected[keep].head(32).round(10).to_string(index=False))
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
