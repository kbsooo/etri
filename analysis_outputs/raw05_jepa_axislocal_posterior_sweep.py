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
from local_lb_proxy_validation import (  # noqa: E402
    add_derived_features,
    build_model_scores,
    load_known_and_candidates,
    predict_candidates,
)
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    actual_anchor_score,
    integrity,
    locate,
    read_submission,
    save_submission,
)


RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
MOTIF_FILE = "submission_raw05_jepa_axisbridge_45f2ba5a.csv"

AXIS_TABLES = [
    OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv",
    OUT / "raw05_jepa_axisbridge_posterior_repair_shortlist.csv",
]
DONOR_TABLES = [
    OUT / "final_jepa_candidate_priority_20260527.csv",
    OUT / "raw05_jepa_anchorrobust_motif_graft_shortlist.csv",
    OUT / "raw05_jepa_structural_constrained_refine_shortlist.csv",
    OUT / "raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv",
    OUT / "raw05_jepa_sigreg_gated_microrefine_shortlist.csv",
]
LOCAL_PROXY = OUT / "local_lb_proxy_validation_candidate_predictions.csv"

OUT_SCAN = OUT / "raw05_jepa_axislocal_posterior_sweep_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_axislocal_posterior_sweep_scored.csv"
OUT_LOCAL = OUT / "raw05_jepa_axislocal_posterior_sweep_localproxy.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_axislocal_posterior_sweep_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_axislocal_posterior_sweep_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_axislocal_posterior_sweep_report.md"


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


def read_optional(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def as_num(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    return pd.to_numeric(frame[col], errors="coerce").fillna(default).astype(np.float64)


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def weighted_mask(weights: dict[str, float]) -> np.ndarray:
    arr = np.zeros((1, len(TARGETS)), dtype=np.float64)
    for target, weight in weights.items():
        arr[0, TARGETS.index(target)] = float(weight)
    return arr


REPAIR_MASKS = {
    "context": weighted_mask({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0}),
    "context_s4light": weighted_mask({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.20}),
    "q2_s123": weighted_mask({"Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0}),
    "all_soft": weighted_mask({"Q1": 0.55, "Q2": 0.65, "Q3": 0.12, "S1": 0.65, "S2": 0.65, "S3": 0.65, "S4": 0.16}),
}

INJECT_MASKS = {
    "q3": weighted_mask({"Q3": 1.0}),
    "q3_s4light": weighted_mask({"Q3": 1.0, "S4": 0.35}),
    "q3_sblockmicro": weighted_mask({"Q3": 1.0, "S1": 0.08, "S2": 0.08, "S3": 0.08, "S4": 0.30}),
    "q1q3s3": weighted_mask({"Q1": 0.35, "Q3": 1.0, "S3": 0.45}),
}

REPAIR_ALPHAS = [0.10, 0.22, 0.38, 0.56]
INJECT_BETAS = [0.05, 0.10, 0.18, 0.28]
CAPS = [0.024, 0.050, 0.090]


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


def candidate_pools() -> tuple[list[str], list[str]]:
    local = read_optional(LOCAL_PROXY)
    local_rank: dict[str, float] = {}
    if not local.empty and "file" in local.columns:
        local_rank = dict(
            zip(
                local["file"].astype(str),
                as_num(local, "available_raw05_relative_delta_vs_raw05_public", 0.0),
            )
        )

    axis_frames = []
    for path in AXIS_TABLES:
        frame = read_optional(path)
        if frame.empty or "file" not in frame.columns:
            continue
        frame = frame.copy()
        frame["local_delta"] = frame["file"].astype(str).map(local_rank).fillna(0.0)
        frame["raw_abs"] = as_num(frame, "delta_vs_raw05_rawaxis", 0.0).abs()
        frame["bad_abs"] = as_num(frame, "bad_residual_axis_ratio", 0.0).abs()
        frame["posterior"] = as_num(frame, "posterior_expected_public_vs_anchor", np.inf)
        axis_frames.append(frame)
    axis = pd.concat(axis_frames, ignore_index=True, sort=False).drop_duplicates("file")
    axis = axis[
        axis["file"].astype(str).str.contains("axisbridge|axisrepair", regex=True, na=False)
        & axis["raw_abs"].le(1.2e-6)
        & axis["bad_abs"].le(0.0010)
        & axis["posterior"].le(0.57698)
    ].copy()
    axis = axis.sort_values(["local_delta", "posterior", "bad_abs"]).head(14)

    donor_frames = []
    for path in DONOR_TABLES:
        frame = read_optional(path)
        if frame.empty or "file" not in frame.columns:
            continue
        frame = frame.copy()
        frame["raw_abs"] = as_num(frame, "delta_vs_raw05_rawaxis", 0.0).abs()
        frame["bad_abs"] = as_num(frame, "bad_residual_axis_ratio", 0.0).abs()
        frame["posterior"] = as_num(frame, "posterior_expected_public_vs_anchor", np.inf)
        donor_frames.append(frame)
    donors = pd.concat(donor_frames, ignore_index=True, sort=False).drop_duplicates("file")
    files = donors["file"].astype(str)
    donors = donors[
        files.str.startswith("submission_raw05_jepa_")
        & ~files.str.contains("axisbridge|public6q3s4corr", regex=True, na=False)
        & donors["posterior"].le(0.576906)
        & donors["raw_abs"].le(2.0e-7)
        & donors["bad_abs"].le(0.0010)
    ].copy()
    donors = donors.sort_values(["posterior", "bad_abs"]).head(20)

    return existing(axis["file"].astype(str).tolist()), existing(donors["file"].astype(str).tolist())


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    *,
    mode: str,
    axis_file: str,
    donor_file: str,
    mask_name: str,
    strength: float,
    cap: float,
    pred_logit: np.ndarray,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    axis_pred: np.ndarray,
    donor_pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> None:
    pred = clip(sigmoid(pred_logit))
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row: dict[str, object] = {
        "label": f"{mode}|axis={axis_file}|donor={donor_file}|mask={mask_name}|strength={strength:.4f}|cap={cap:.3f}",
        "prediction_hash": pred_hash,
        "mode": mode,
        "axis_file": axis_file,
        "donor_file": donor_file,
        "mask_name": mask_name,
        "strength": float(strength),
        "cap": float(cap),
        "mean_abs_move_vs_axis": float(np.abs(pred - axis_pred).mean()),
        "mean_abs_move_vs_donor": float(np.abs(pred - donor_pred).mean()),
        "mean_abs_move_vs_raw05": float(np.abs(pred - sigmoid(raw_logit)).mean()),
        "min_prob": float(pred.min()),
        "max_prob": float(pred.max()),
    }
    row.update(q3s4_motif_metrics(pred_logit, raw_logit, motif_delta))
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate(sample: pd.DataFrame, axis_files: list[str], donor_files: list[str]) -> tuple[pd.DataFrame, list[np.ndarray]]:
    axes = public_axes()
    files = existing([RAW05_FILE, MOTIF_FILE, *axis_files, *donor_files])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    logits = {file_name: logit(arrays[file_name]) for file_name in files}
    raw_logit = logits[RAW05_FILE]
    motif_delta = logits[MOTIF_FILE] - raw_logit

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for axis_file in axis_files:
        axis_logit = logits[axis_file]
        axis_pred = arrays[axis_file]
        axis_resid = axis_logit - raw_logit
        for donor_file in donor_files:
            donor_logit = logits[donor_file]
            donor_pred = arrays[donor_file]
            for mask_name, mask in REPAIR_MASKS.items():
                donor_step = donor_logit - axis_logit
                for alpha in REPAIR_ALPHAS:
                    for cap in CAPS:
                        repair = alpha * np.clip(donor_step * mask, -cap, cap)
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            mode="axis_context_repair",
                            axis_file=axis_file,
                            donor_file=donor_file,
                            mask_name=mask_name,
                            strength=alpha,
                            cap=cap,
                            pred_logit=axis_logit + repair,
                            raw_logit=raw_logit,
                            motif_delta=motif_delta,
                            axis_pred=axis_pred,
                            donor_pred=donor_pred,
                            axes=axes,
                        )
            for mask_name, mask in INJECT_MASKS.items():
                for beta in INJECT_BETAS:
                    for cap in CAPS:
                        injection = beta * np.clip(axis_resid * mask, -cap, cap)
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            mode="donor_axis_inject",
                            axis_file=axis_file,
                            donor_file=donor_file,
                            mask_name=mask_name,
                            strength=beta,
                            cap=cap,
                            pred_logit=donor_logit + injection,
                            raw_logit=raw_logit,
                            motif_delta=motif_delta,
                            axis_pred=axis_pred,
                            donor_pred=donor_pred,
                            axes=axes,
                        )
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["local_shape_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["raw_abs"] - 1.2e-6, 0.0) * 80.0
        + np.maximum(frame["bad_abs"] - 0.00065, 0.0) * 0.10
        + np.maximum(0.9990 - frame["q3s4_motif_cos"], 0.0) * 0.002
        + np.maximum(frame["q3s4_motif_orth_ratio"] - 0.050, 0.0) * 0.0004
    )
    masks = [
        frame["posterior_expected_public_vs_anchor"].le(0.576910)
        & frame["raw_abs"].le(2.0e-7)
        & frame["bad_abs"].le(0.00025)
        & frame["q3s4_motif_cos"].ge(0.9990),
        frame["posterior_expected_public_vs_anchor"].le(0.576940)
        & frame["raw_abs"].le(6.0e-7)
        & frame["bad_abs"].le(0.00055)
        & frame["q3s4_motif_cos"].ge(0.9980),
        frame["posterior_expected_public_vs_anchor"].le(0.576980)
        & frame["raw_abs"].le(1.1e-6)
        & frame["bad_abs"].le(0.00080),
    ]
    parts = [frame[mask].sort_values("local_shape_score").head(1200) for mask in masks]
    parts.append(frame.sort_values("local_shape_score").head(1600))
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").head(3200)


def local_proxy_score(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    known, _, ranker = load_known_and_candidates()
    model_scores, _ = build_model_scores(known)
    raw05_row = ranker[ranker["file"].astype(str).eq(RAW05_FILE)].copy()
    if raw05_row.empty:
        raise ValueError("raw05 row missing from ranker scores")
    candidates = pd.concat([raw05_row, scored], ignore_index=True, sort=False)
    candidates = add_derived_features(candidates)
    local = predict_candidates(known, model_scores, candidates)
    return local[~local["file"].astype(str).eq(RAW05_FILE)].reset_index(drop=True)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored.insert(0, "file", [f"__axislocal_candidate_{i:05d}.csv" for i in range(len(scored))])
    scored = pd.concat([scored, actual.reset_index(drop=True)], axis=1)
    scored = add_derived_features(scored)
    local = local_proxy_score(scored, sample)
    scored = scored.drop(columns=[col for col in local.columns if col in scored.columns and col != "file"], errors="ignore")
    scored = scored.merge(local, on="file", how="left", suffixes=("", "_local"))
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["axislocal_score"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"]
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.22
        + np.maximum(scored["raw_abs"] - 1.0e-7, 0.0) * 14.0
        + np.maximum(scored["bad_abs"] - 0.00018, 0.0) * 0.020
        + np.maximum(0.9990 - scored["q3s4_motif_cos"], 0.0) * 0.0008
    )
    scored["strict_hit"] = (
        scored["posterior_expected_public_vs_anchor"].le(0.576905)
        & scored["raw_abs"].le(1.0e-7)
        & scored["bad_abs"].le(0.00018)
        & scored["q3s4_motif_cos"].ge(0.9990)
    )
    scored["balanced_hit"] = (
        scored["posterior_expected_public_vs_anchor"].le(0.576930)
        & scored["raw_abs"].le(4.0e-7)
        & scored["bad_abs"].le(0.00045)
        & scored["q3s4_motif_cos"].ge(0.9980)
    )
    scored["rank_score"] = (
        0.34 * scored["axislocal_score"].rank(method="min")
        + 0.20 * scored["available_raw05_relative_delta_vs_raw05_public"].rank(method="min")
        + 0.16 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.12 * scored["bad_abs"].rank(method="min")
        + 0.10 * scored["raw_abs"].rank(method="min")
        + 0.08 * scored["q3s4_motif_orth_ratio"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "axislocal_score"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "axislocal_strict",
            scored["strict_hit"],
            ["axislocal_score", "available_raw05_relative_delta_vs_raw05_public"],
            30,
        ),
        (
            "axislocal_balanced",
            scored["balanced_hit"],
            ["available_raw05_relative_delta_vs_raw05_public", "axislocal_score"],
            30,
        ),
        (
            "axislocal_proxy",
            scored["available_raw05_relative_delta_vs_raw05_public"].le(-4.0e-6)
            & scored["posterior_expected_public_vs_anchor"].le(0.576950)
            & scored["raw_abs"].le(7.0e-7),
            ["available_raw05_relative_delta_vs_raw05_public", "posterior_expected_public_vs_anchor"],
            30,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "axislocal_score"]).head(42).assign(bucket="axislocal_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "axislocal_score"]).head(90).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_axislocal_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected["file"] = files
    return selected


def write_report(
    scan: pd.DataFrame,
    scored: pd.DataFrame,
    selected: pd.DataFrame,
    integ: pd.DataFrame,
    axis_files: list[str],
    donor_files: list[str],
) -> None:
    cols = [
        "file",
        "bucket",
        "mode",
        "axis_file",
        "donor_file",
        "mask_name",
        "strength",
        "cap",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "mean_abs_move_vs_raw05",
        "axislocal_score",
        "rank_score",
    ]
    mode_summary = (
        scored.groupby(["mode", "mask_name"], as_index=False)
        .agg(
            n=("label", "size"),
            strict_hits=("strict_hit", "sum"),
            balanced_hits=("balanced_hit", "sum"),
            best_local_delta=("available_raw05_relative_delta_vs_raw05_public", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_axislocal_score=("axislocal_score", "min"),
        )
        .sort_values(["best_local_delta", "best_axislocal_score"])
    )
    lines = [
        "# Raw05 JEPA Axis-Local Posterior Sweep",
        "",
        "This experiment keeps the local-proxy-useful axisbridge direction but repairs it toward posterior-safe JEPA donors, then re-ranks the scored candidates with the local public-LB proxy.",
        "",
        "## Pools",
        "",
        f"- axis files: `{len(axis_files)}`",
        f"- donor files: `{len(donor_files)}`",
        "",
        "## Counts",
        "",
        f"- generated/prefiltered candidates: `{len(scan)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- strict hits: `{int(scored['strict_hit'].sum())}`",
        f"- balanced hits: `{int(scored['balanced_hit'].sum())}`",
        "",
        "## Mode Summary",
        "",
        "```csv",
        mode_summary.round(10).head(80).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[cols].round(10).head(90).to_csv(index=False).strip(),
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
    axis_files, donor_files = candidate_pools()
    if not axis_files or not donor_files:
        raise RuntimeError(f"empty pools: axis={len(axis_files)} donor={len(donor_files)}")

    scan, preds = generate(sample, axis_files, donor_files)
    scan = prefilter(scan)
    scan.to_csv(OUT_SCAN, index=False)

    scored = score_candidates(scan, preds, sample)
    selected = select_and_save(scored, preds, sample)
    integ = integrity(selected["file"].astype(str).tolist(), sample)

    scored.to_csv(OUT_SCORED, index=False)
    scored.sort_values(["axislocal_score", "available_raw05_relative_delta_vs_raw05_public"]).to_csv(OUT_LOCAL, index=False)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ, axis_files, donor_files)

    keep = [
        "file",
        "bucket",
        "mode",
        "axis_file",
        "donor_file",
        "mask_name",
        "strength",
        "cap",
        "available_raw05_relative_delta_vs_raw05_public",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "axislocal_score",
    ]
    print(f"pools: axis={len(axis_files)} donor={len(donor_files)}")
    print(f"generated/scored/saved: {len(scan)} {len(scored)} {len(selected)}")
    print(f"strict/balanced hits: {int(scored['strict_hit'].sum())} {int(scored['balanced_hit'].sum())}")
    print(selected[keep].head(24).round(10).to_string(index=False))
    print(f"wrote {OUT_SCAN}")
    print(f"wrote {OUT_SCORED}")
    print(f"wrote {OUT_LOCAL}")
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_INTEGRITY}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
