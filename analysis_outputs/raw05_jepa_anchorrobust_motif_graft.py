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
from raw05_anchor_jepa_micro_injection import actual_anchor_score, integrity, locate, read_submission, save_submission  # noqa: E402


RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
MOTIF_FILE = "submission_raw05_jepa_axisbridge_45f2ba5a.csv"

OUT_SCAN = OUT / "raw05_jepa_anchorrobust_motif_graft_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_anchorrobust_motif_graft_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_anchorrobust_motif_graft_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_anchorrobust_motif_graft_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_anchorrobust_motif_graft_report.md"

BASE_FILES = [
    "submission_raw05_jepa_structrefine_04ad10f8.csv",
    "submission_raw05_jepa_structrefine_90e28f7d.csv",
    "submission_raw05_jepa_structrefine_5d94b630.csv",
    "submission_raw05_jepa_structrefine_2a770fa9.csv",
    "submission_raw05_jepa_structrefine_dd98c58a.csv",
    "submission_raw05_jepa_axistrade_931a03a1.csv",
]

ROBUST_DONOR_FILES = [
    "submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv",
    "submission_public6entropy_raw05_q3s4_g180_15f6d69a.csv",
    "submission_public6entropy_raw05_q3s4_g250_b19cb905.csv",
    "submission_raw05_jepa_public6q3s4corr_raw05_direct_logit_strength_entropy_g100_2884f233.csv",
]

ALPHAS = [0.012, 0.020, 0.032, 0.050, 0.080, 0.120, 0.180]
CAPS = [0.006, 0.010, 0.016, 0.024, 0.040]
Q3S4_REPAIRS = [0.0, 0.35, 0.70, 1.0]


def weighted_mask(weights: dict[str, float]) -> np.ndarray:
    arr = np.zeros((1, len(TARGETS)), dtype=np.float64)
    for target, weight in weights.items():
        arr[0, TARGETS.index(target)] = float(weight)
    return arr


GRAFT_MASKS = {
    "q1": weighted_mask({"Q1": 1.0}),
    "s3": weighted_mask({"S3": 1.0}),
    "q1s3": weighted_mask({"Q1": 1.0, "S3": 1.0}),
    "q1_s3_q3light": weighted_mask({"Q1": 1.0, "S3": 1.0, "Q3": 0.25}),
    "q1_s3_s4light": weighted_mask({"Q1": 1.0, "S3": 1.0, "S4": 0.18}),
    "q1q3s3": weighted_mask({"Q1": 1.0, "Q3": 0.45, "S3": 1.0}),
    "q1q3s3s4light": weighted_mask({"Q1": 1.0, "Q3": 0.35, "S3": 1.0, "S4": 0.15}),
}

Q3S4_MASK = weighted_mask({"Q3": 1.0, "S4": 1.0})


def existing(files: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if file_name in seen:
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


def q3s4_motif_metrics(pred_logit: np.ndarray, raw_logit: np.ndarray, motif_delta: np.ndarray) -> dict[str, float]:
    cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    delta = pred_logit[:, cols] - raw_logit[:, cols]
    motif = motif_delta[:, cols]
    motif_denom = float(np.sum(motif * motif))
    mae = float(np.mean(np.abs(delta)))
    if motif_denom <= 1e-12:
        return {
            "q3s4_motif_proj": 0.0,
            "q3s4_motif_cos": 0.0,
            "q3s4_motif_orth_ratio": 0.0,
            "q3s4_mae_raw05": mae,
        }
    proj = float(np.sum(delta * motif) / motif_denom)
    norm = float(np.sqrt(np.sum(delta * delta)) * np.sqrt(motif_denom))
    cos = float(np.sum(delta * motif) / max(norm, 1e-12))
    orth = float(np.sqrt(np.mean((delta - proj * motif) ** 2)))
    return {
        "q3s4_motif_proj": proj,
        "q3s4_motif_cos": cos,
        "q3s4_motif_orth_ratio": orth / max(mae, 1e-12),
        "q3s4_mae_raw05": mae,
    }


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    pred_logit: np.ndarray,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    base_pred: np.ndarray,
    donor_pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
    label: str,
    base_file: str,
    donor_file: str,
    graft_mask: str,
    alpha: float,
    cap: float,
    q3s4_repair: float,
) -> None:
    pred = clip(sigmoid(pred_logit))
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row: dict[str, object] = {
        "label": label,
        "prediction_hash": pred_hash,
        "base_file": base_file,
        "donor_file": donor_file,
        "graft_mask": graft_mask,
        "alpha": float(alpha),
        "cap": float(cap),
        "q3s4_repair": float(q3s4_repair),
        "mean_abs_move_vs_base": float(np.abs(pred - base_pred).mean()),
        "mean_abs_move_vs_donor": float(np.abs(pred - donor_pred).mean()),
        "mean_abs_move_vs_raw05": float(np.abs(pred - sigmoid(raw_logit)).mean()),
    }
    row.update(q3s4_motif_metrics(pred_logit, raw_logit, motif_delta))
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray]]:
    axes = public_axes()
    files = existing([RAW05_FILE, MOTIF_FILE, *BASE_FILES, *ROBUST_DONOR_FILES])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    logits = {file_name: logit(arrays[file_name]) for file_name in files}
    raw_logit = logits[RAW05_FILE]
    motif_delta = logits[MOTIF_FILE] - raw_logit

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    base_files = [file_name for file_name in BASE_FILES if file_name in arrays]
    donor_files = [file_name for file_name in ROBUST_DONOR_FILES if file_name in arrays]
    for base_file in base_files:
        base_logit = logits[base_file]
        base_pred = arrays[base_file]
        for donor_file in donor_files:
            donor_logit = logits[donor_file]
            donor_pred = arrays[donor_file]
            robust_step = donor_logit - raw_logit
            for graft_mask, mask in GRAFT_MASKS.items():
                for alpha in ALPHAS:
                    for cap in CAPS:
                        graft = alpha * np.clip(robust_step * mask, -cap, cap)
                        grafted_logit = base_logit + graft
                        for q3s4_repair in Q3S4_REPAIRS:
                            pred_logit = grafted_logit + q3s4_repair * (base_logit - grafted_logit) * Q3S4_MASK
                            add_candidate(
                                rows,
                                preds,
                                seen,
                                pred_logit,
                                raw_logit,
                                motif_delta,
                                base_pred,
                                donor_pred,
                                axes,
                                (
                                    f"anchorrobust_graft|base={base_file}|donor={donor_file}|"
                                    f"mask={graft_mask}|a={alpha:.3f}|cap={cap:.3f}|q3s4repair={q3s4_repair:.2f}"
                                ),
                                base_file,
                                donor_file,
                                graft_mask,
                                alpha,
                                cap,
                                q3s4_repair,
                            )
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["struct_hit"] = (
        frame["q3s4_motif_cos"].ge(0.9999)
        & frame["q3s4_motif_orth_ratio"].le(0.010)
        & frame["q3s4_motif_proj"].between(0.94, 1.08)
        & frame["posterior_expected_public_vs_anchor"].le(0.576905)
        & frame["delta_vs_raw05_rawaxis"].le(1.0e-7)
        & frame["bad_abs"].le(0.00012)
    )
    frame["graft_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(frame["bad_abs"] - 0.00012, 0.0) * 0.14
        + np.maximum(0.9999 - frame["q3s4_motif_cos"], 0.0) * 0.006
        + np.maximum(frame["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.001
        + np.maximum(frame["mean_abs_move_vs_base"] - 0.00012, 0.0) * 0.020
    )
    parts = [
        frame[frame["struct_hit"]].sort_values(["graft_score", "mean_abs_move_vs_base"]).head(1400),
        frame[
            frame["q3s4_motif_cos"].ge(0.9999)
            & frame["q3s4_motif_orth_ratio"].le(0.012)
            & frame["posterior_expected_public_vs_anchor"].le(0.576908)
            & frame["delta_vs_raw05_rawaxis"].le(1.2e-7)
            & frame["bad_abs"].le(0.00018)
        ].sort_values("graft_score").head(1400),
        frame.sort_values("graft_score").head(1600),
    ]
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").head(3000)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual.reset_index(drop=True)], axis=1)
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["struct_hit"] = (
        scored["q3s4_motif_cos"].ge(0.9999)
        & scored["q3s4_motif_orth_ratio"].le(0.010)
        & scored["q3s4_motif_proj"].between(0.94, 1.08)
        & scored["posterior_expected_public_vs_anchor"].le(0.576905)
        & scored["delta_vs_raw05_rawaxis"].le(1.0e-7)
        & scored["bad_abs"].le(0.00012)
    )
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.90
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 240.0
        + np.maximum(scored["bad_abs"] - 0.00012, 0.0) * 0.12
        + np.maximum(scored["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.0008
        + np.maximum(0.9999 - scored["q3s4_motif_cos"], 0.0) * 0.004
    )
    scored["rank_score"] = (
        0.24 * scored["selection_score"].rank(method="min")
        + 0.18 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.18 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.16 * scored["bad_abs"].rank(method="min")
        + 0.14 * scored["raw_abs"].rank(method="min")
        + 0.10 * scored["q3s4_motif_orth_ratio"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "graft_strict",
            scored["struct_hit"],
            ["selection_score", "actual_anchor_score_final"],
            36,
        ),
        (
            "graft_lowbad",
            scored["q3s4_motif_cos"].ge(0.9999)
            & scored["q3s4_motif_orth_ratio"].le(0.012)
            & scored["posterior_expected_public_vs_anchor"].le(0.576907)
            & scored["delta_vs_raw05_rawaxis"].le(1.2e-7)
            & scored["bad_abs"].le(0.00008),
            ["selection_score", "bad_abs"],
            28,
        ),
        (
            "graft_local",
            scored["q3s4_motif_cos"].ge(0.9999)
            & scored["posterior_expected_public_vs_anchor"].le(0.576908)
            & scored["delta_vs_raw05_rawaxis"].le(1.2e-7)
            & scored["bad_abs"].le(0.00018),
            ["actual_anchor_score_final", "selection_score"],
            28,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "selection_score"]).head(40).assign(bucket="graft_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "selection_score"]).head(84).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_anchorrobust_graft_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "base_file",
        "donor_file",
        "graft_mask",
        "alpha",
        "cap",
        "q3s4_repair",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_proj",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "mean_abs_move_vs_base",
        "selection_score",
        "rank_score",
    ]
    summary = (
        scored.groupby(["base_file", "donor_file", "graft_mask"], as_index=False)
        .agg(
            n=("label", "size"),
            struct_hits=("struct_hit", "sum"),
            best_actual=("actual_anchor_score_final", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_orth=("q3s4_motif_orth_ratio", "min"),
            best_selection=("selection_score", "min"),
        )
        .sort_values(["struct_hits", "best_selection"], ascending=[False, True])
    )
    lines = [
        "# Raw05 JEPA Anchor-Robust Motif Graft",
        "",
        "This grafts the leave-one-anchor robust public6entropy signal into strict Q3/S4 motif candidates with small target-local logit steps.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- scan structural hits: `{int(scan.get('struct_hit', pd.Series(dtype=bool)).sum()) if 'struct_hit' in scan.columns else 0}`",
        f"- scored structural hits: `{int(scored['struct_hit'].sum()) if 'struct_hit' in scored.columns else 0}`",
        "",
        "## Group Summary",
        "",
        "```csv",
        summary.round(10).head(80).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[cols].round(10).head(84).to_csv(index=False).strip(),
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
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    scan, preds = generate(sample)
    scan = prefilter(scan)
    scan.to_csv(OUT_SCAN, index=False)
    scored = score_candidates(scan, preds, sample)
    selected = select_and_save(scored, preds, sample)
    integ = integrity(selected["file"].astype(str).tolist(), sample)

    scored.to_csv(OUT_SCORED, index=False)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ)

    print(f"generated/scored/saved: {len(scan)} {len(scored)} {len(selected)}")
    print(f"struct hits: scan={int(scan['struct_hit'].sum())} scored={int(scored['struct_hit'].sum())}")
    print(
        selected[
            [
                "file",
                "bucket",
                "base_file",
                "donor_file",
                "graft_mask",
                "alpha",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "q3s4_motif_cos",
                "q3s4_motif_orth_ratio",
                "selection_score",
            ]
        ]
        .head(18)
        .round(10)
        .to_string(index=False)
    )
    print(f"wrote {OUT_SCAN}")
    print(f"wrote {OUT_SCORED}")
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_INTEGRITY}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
