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
BEST_AXIS_TRADE = "submission_raw05_jepa_axistrade_931a03a1.csv"

OUT_SCAN = OUT / "raw05_jepa_structural_constrained_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_structural_constrained_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_structural_constrained_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_structural_constrained_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_structural_constrained_refine_report.md"

Q3S4 = ["Q3", "S4"]
CTX = ["Q1", "Q2", "S1", "S2", "S3"]

BASE_FILES = [
    BEST_AXIS_TRADE,
    "submission_raw05_jepa_axistrade_80fd659c.csv",
    "submission_raw05_jepa_axisrepair_2a20d67f.csv",
]

DONOR_FILES = [
    "submission_raw05_jepa_siggate_fd0e9622.csv",
    "submission_raw05_jepa_siganchor_3644a42f.csv",
    "submission_raw05_jepa_efback_9c50051c.csv",
    "submission_raw05_jepa_axisrepair_78029f2c.csv",
]

RAW_ALPHAS = [0.0, 0.006, 0.012, 0.020, 0.032]
DONOR_ALPHAS = [0.0, 0.035, 0.065, 0.095, 0.140]
MOTIF_ALPHAS = [0.0, 0.012, 0.024, 0.040]
CAPS = [0.024, 0.040, 0.065]


def mask(targets: list[str]) -> np.ndarray:
    allowed = set(targets)
    return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)


MASKS = {
    "all": np.ones((1, len(TARGETS)), dtype=np.float64),
    "ctx": mask(CTX),
    "q3s4": mask(Q3S4),
    "ctx_q3light": mask(CTX) + 0.04 * mask(Q3S4),
    "ctx_s4light": mask(CTX) + mask(["S4"]) * 0.08,
}


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


def add_row(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    pred_logit: np.ndarray,
    label: str,
    base_file: str,
    donor_file: str,
    raw_mask_name: str,
    donor_mask_name: str,
    motif_mask_name: str,
    raw_alpha: float,
    donor_alpha: float,
    motif_alpha: float,
    cap: float,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    base_pred: np.ndarray,
    donor_pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
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
        "raw_mask": raw_mask_name,
        "donor_mask": donor_mask_name,
        "motif_mask": motif_mask_name,
        "raw_alpha": raw_alpha,
        "donor_alpha": donor_alpha,
        "motif_alpha": motif_alpha,
        "cap": cap,
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
    files = existing([RAW05_FILE, MOTIF_FILE, *BASE_FILES, *DONOR_FILES])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    logits = {file_name: logit(arrays[file_name]) for file_name in files}
    raw_logit = logits[RAW05_FILE]
    motif_delta = logits[MOTIF_FILE] - raw_logit

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    base_files = [file_name for file_name in BASE_FILES if file_name in arrays]
    donor_files = [file_name for file_name in DONOR_FILES if file_name in arrays]
    for base_file in base_files:
        base_logit = logits[base_file]
        base_pred = arrays[base_file]
        for donor_file in donor_files:
            if donor_file == base_file:
                continue
            donor_logit = logits[donor_file]
            donor_pred = arrays[donor_file]
            donor_step = donor_logit - base_logit
            raw_step = raw_logit - base_logit
            motif_step = logits[MOTIF_FILE] - base_logit

            for raw_mask_name in ["ctx", "ctx_q3light"]:
                raw_mask = MASKS[raw_mask_name]
                for donor_mask_name in ["ctx", "ctx_q3light", "ctx_s4light"]:
                    donor_mask = MASKS[donor_mask_name]
                    for motif_mask_name in ["q3s4"]:
                        motif_mask = MASKS[motif_mask_name]
                        for raw_alpha in RAW_ALPHAS:
                            for donor_alpha in DONOR_ALPHAS:
                                for motif_alpha in MOTIF_ALPHAS:
                                    for cap in CAPS:
                                        raw_part = raw_alpha * np.clip(raw_step * raw_mask, -cap, cap)
                                        donor_part = donor_alpha * np.clip(donor_step * donor_mask, -cap, cap)
                                        motif_part = motif_alpha * np.clip(motif_step * motif_mask, -cap, cap)
                                        pred_logit = base_logit + raw_part + donor_part + motif_part
                                        add_row(
                                            rows,
                                            preds,
                                            seen,
                                            pred_logit,
                                            (
                                                f"structrefine|base={base_file}|donor={donor_file}|"
                                                f"raw={raw_mask_name}:{raw_alpha:.3f}|"
                                                f"donor={donor_mask_name}:{donor_alpha:.3f}|"
                                                f"motif={motif_mask_name}:{motif_alpha:.3f}|cap={cap:.3f}"
                                            ),
                                            base_file,
                                            donor_file,
                                            raw_mask_name,
                                            donor_mask_name,
                                            motif_mask_name,
                                            float(raw_alpha),
                                            float(donor_alpha),
                                            float(motif_alpha),
                                            float(cap),
                                            raw_logit,
                                            motif_delta,
                                            base_pred,
                                            donor_pred,
                                            axes,
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
    frame["struct_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 250.0
        + np.maximum(frame["bad_abs"] - 0.00012, 0.0) * 0.13
        + np.maximum(0.9999 - frame["q3s4_motif_cos"], 0.0) * 0.004
        + np.maximum(frame["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.0008
        + np.maximum(0.94 - frame["q3s4_motif_proj"], 0.0) * 0.0005
        + np.maximum(frame["q3s4_motif_proj"] - 1.08, 0.0) * 0.0005
        + np.maximum(frame["mean_abs_move_vs_base"] - 0.00016, 0.0) * 0.035
    )
    parts = [
        frame[frame["struct_hit"]].sort_values(["struct_score", "posterior_expected_public_vs_anchor"]).head(1200),
        frame[
            frame["q3s4_motif_cos"].ge(0.9999)
            & frame["q3s4_motif_orth_ratio"].le(0.014)
            & frame["posterior_expected_public_vs_anchor"].le(0.576908)
            & frame["delta_vs_raw05_rawaxis"].le(1.5e-7)
            & frame["bad_abs"].le(0.00020)
        ].sort_values("struct_score").head(1200),
        frame.sort_values("struct_score").head(1600),
    ]
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").head(2800)


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
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.95
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(scored["bad_abs"] - 0.00012, 0.0) * 0.13
        + np.maximum(scored["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.0008
        + np.maximum(0.9999 - scored["q3s4_motif_cos"], 0.0) * 0.004
    )
    scored["rank_score"] = (
        0.24 * scored["selection_score"].rank(method="min")
        + 0.20 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.18 * scored["bad_abs"].rank(method="min")
        + 0.16 * scored["raw_abs"].rank(method="min")
        + 0.12 * scored["q3s4_motif_orth_ratio"].rank(method="min")
        + 0.10 * scored["actual_anchor_score_final"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "struct_hit",
            scored["struct_hit"],
            ["selection_score", "actual_anchor_score_final"],
            32,
        ),
        (
            "struct_lowbad",
            scored["q3s4_motif_cos"].ge(0.9999)
            & scored["q3s4_motif_orth_ratio"].le(0.014)
            & scored["posterior_expected_public_vs_anchor"].le(0.576907)
            & scored["delta_vs_raw05_rawaxis"].le(1.5e-7)
            & scored["bad_abs"].le(0.00008),
            ["selection_score"],
            24,
        ),
        (
            "struct_local",
            scored["q3s4_motif_cos"].ge(0.9999)
            & scored["posterior_expected_public_vs_anchor"].le(0.576908)
            & scored["raw_abs"].le(1.2e-7),
            ["actual_anchor_score_final", "selection_score"],
            24,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "selection_score"]).head(32).assign(bucket="struct_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "selection_score"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_structrefine_{tag}.csv"
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
        "raw_mask",
        "donor_mask",
        "motif_mask",
        "raw_alpha",
        "donor_alpha",
        "motif_alpha",
        "cap",
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
        scored.groupby(["base_file", "donor_file"], as_index=False)
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
        "# Raw05 JEPA Structural Constrained Refine",
        "",
        "Micro-refines the unique structural constraint hit `submission_raw05_jepa_axistrade_931a03a1.csv` by combining raw05 shrinkage, posterior-safe donor offsets, and Q3/S4 motif re-anchoring.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- prefilter candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- scan structural hits: `{int(scan.get('struct_hit', pd.Series(dtype=bool)).sum()) if 'struct_hit' in scan.columns else 0}`",
        f"- scored structural hits: `{int(scored['struct_hit'].sum()) if 'struct_hit' in scored.columns else 0}`",
        "",
        "## Pair Summary",
        "",
        "```csv",
        summary.round(10).head(50).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[cols].round(10).head(72).to_csv(index=False).strip(),
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
    print(selected[[
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "selection_score",
    ]].head(16).round(10).to_string(index=False))
    print(f"wrote {OUT_SCAN}")
    print(f"wrote {OUT_SCORED}")
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_INTEGRITY}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
