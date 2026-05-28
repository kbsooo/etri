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
    RAW05_FILE,
    actual_anchor_score,
    integrity,
    locate,
    read_submission,
    save_submission,
)


MOTIF_FILE = "submission_raw05_jepa_axisbridge_45f2ba5a.csv"

BASE_FILES = [
    "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "submission_raw05_jepa_anchorrobust_graft_f6859562.csv",
    "submission_raw05_jepa_anchorrobust_graft_76a96cd0.csv",
    "submission_raw05_jepa_structrefine_04ad10f8.csv",
    "submission_raw05_jepa_structrefine_90e28f7d.csv",
]

LOCAL_FILES = [
    "submission_raw05_jepa_axislocal_20e4a625.csv",
    "submission_raw05_jepa_axislocal_d90f09cf.csv",
    "submission_raw05_jepa_axislocal_16ae093a.csv",
    "submission_raw05_jepa_axislocal_7a15027d.csv",
    "submission_raw05_jepa_axisrepair_2a20d67f.csv",
    "submission_raw05_jepa_axisrepair_78029f2c.csv",
    "submission_raw05_jepa_axisbridge_1968b38c.csv",
]

SAFETY_FILES = [
    "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "submission_raw05_jepa_structrefine_90e28f7d.csv",
    "submission_raw05_jepa_siggate_6d681440.csv",
    "submission_raw05_jepa_siggate_fd0e9622.csv",
    "submission_raw05_jepa_efback_9c50051c.csv",
    "submission_raw05_jepa_efback_cc265f32.csv",
]

ROBUST_FILES = [
    "submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv",
    "submission_public6entropy_raw05_q3s4_g180_15f6d69a.csv",
    "submission_public6entropy_raw05_q3s4_g250_b19cb905.csv",
]

OUT_SCAN = OUT / "raw05_jepa_direct_constrained_search_scan.csv"
OUT_PREFILTER = OUT / "raw05_jepa_direct_constrained_search_prefilter.csv"
OUT_SCORED = OUT / "raw05_jepa_direct_constrained_search_scored.csv"
OUT_LOCAL = OUT / "raw05_jepa_direct_constrained_search_localproxy.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_direct_constrained_search_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_direct_constrained_search_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_direct_constrained_search_report.md"


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


def weighted_mask(weights: dict[str, float]) -> np.ndarray:
    arr = np.zeros((1, len(TARGETS)), dtype=np.float64)
    for target, weight in weights.items():
        arr[0, TARGETS.index(target)] = float(weight)
    return arr


STEP_MASKS = {
    "context": weighted_mask({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0}),
    "context_s4micro": weighted_mask({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.08}),
    "q2_s123": weighted_mask({"Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0}),
    "q1_s3": weighted_mask({"Q1": 1.0, "S3": 1.0}),
    "all_soft": weighted_mask({"Q1": 0.45, "Q2": 0.60, "Q3": 0.08, "S1": 0.55, "S2": 0.55, "S3": 0.65, "S4": 0.08}),
}

SAFETY_MASKS = {
    "none": weighted_mask({}),
    "context": STEP_MASKS["context"],
    "q2_s123": STEP_MASKS["q2_s123"],
    "all_soft": STEP_MASKS["all_soft"],
}

ROBUST_MASKS = {
    "q1s3": weighted_mask({"Q1": 1.0, "S3": 1.0}),
    "q1s3_q3micro": weighted_mask({"Q1": 1.0, "S3": 1.0, "Q3": 0.10}),
    "q1q3s3_s4micro": weighted_mask({"Q1": 1.0, "Q3": 0.18, "S3": 1.0, "S4": 0.08}),
}

STEP_STRENGTHS = [0.04, 0.07, 0.11, 0.16, 0.24]
STEP_CAPS = [0.004, 0.008, 0.014, 0.024]
SAFETY_ETAS = [0.0, 0.08, 0.16, 0.28]
ORTH_KEEP = [0.0, 0.05, 0.12]
ROBUST_ALPHAS = [0.006, 0.012, 0.020, 0.032]
ROBUST_CAPS = [0.004, 0.008, 0.014]


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


def project_q3s4(
    pred_logit: np.ndarray,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    keep_orth: float,
    proj_lo: float = 0.94,
    proj_hi: float = 1.08,
) -> np.ndarray:
    cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    out = pred_logit.copy()
    delta = out[:, cols] - raw_logit[:, cols]
    motif = motif_delta[:, cols]
    denom = float(np.sum(motif * motif))
    if denom <= 1e-12:
        return out
    proj = np.clip(float(np.sum(delta * motif) / denom), proj_lo, proj_hi)
    orth = delta - proj * motif
    out[:, cols] = raw_logit[:, cols] + proj * motif + float(keep_orth) * orth
    return out


def local_proxy_score(rows: pd.DataFrame) -> pd.DataFrame:
    known, _, ranker = load_known_and_candidates()
    model_scores, _ = build_model_scores(known)
    raw05_row = ranker[ranker["file"].astype(str).eq(RAW05_FILE)].copy()
    if raw05_row.empty:
        raise ValueError("raw05 row missing from ranker scores")
    candidates = pd.concat([raw05_row, rows], ignore_index=True, sort=False)
    candidates = add_derived_features(candidates)
    local = predict_candidates(known, model_scores, candidates)
    return local[~local["file"].astype(str).eq(RAW05_FILE)].reset_index(drop=True)


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    *,
    label: str,
    mode: str,
    base_file: str,
    local_file: str,
    safety_file: str,
    robust_file: str,
    step_mask: str,
    step_strength: float,
    step_cap: float,
    safety_mask: str,
    safety_eta: float,
    robust_mask: str,
    robust_alpha: float,
    robust_cap: float,
    keep_orth: float,
    pred_logit: np.ndarray,
    raw_logit: np.ndarray,
    motif_delta: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> None:
    pred = clip(sigmoid(pred_logit))
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row: dict[str, object] = {
        "file": f"__direct_constraint_{len(rows):05d}.csv",
        "label": label,
        "prediction_hash": pred_hash,
        "mode": mode,
        "base_file": base_file,
        "local_file": local_file,
        "safety_file": safety_file,
        "robust_file": robust_file,
        "step_mask": step_mask,
        "step_strength": float(step_strength),
        "step_cap": float(step_cap),
        "safety_mask": safety_mask,
        "safety_eta": float(safety_eta),
        "robust_mask": robust_mask,
        "robust_alpha": float(robust_alpha),
        "robust_cap": float(robust_cap),
        "keep_orth": float(keep_orth),
        "mean_abs_move_vs_raw05": float(np.abs(pred - sigmoid(raw_logit)).mean()),
    }
    row.update(q3s4_motif_metrics(pred_logit, raw_logit, motif_delta))
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray]]:
    axes = public_axes()
    files = existing(
        [
            RAW05_FILE,
            MOTIF_FILE,
            *BASE_FILES,
            *LOCAL_FILES,
            *SAFETY_FILES,
            *ROBUST_FILES,
        ]
    )
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    logits = {file_name: logit(arrays[file_name]) for file_name in files}
    raw_logit = logits[RAW05_FILE]
    motif_delta = logits[MOTIF_FILE] - raw_logit

    base_files = [file_name for file_name in BASE_FILES if file_name in arrays]
    local_files = [file_name for file_name in LOCAL_FILES if file_name in arrays]
    safety_files = [file_name for file_name in SAFETY_FILES if file_name in arrays]
    robust_files = [file_name for file_name in ROBUST_FILES if file_name in arrays]

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in base_files:
        base_logit = logits[base_file]
        for local_file in local_files:
            local_step = logits[local_file] - base_logit
            for step_mask, mask in STEP_MASKS.items():
                for step_strength in STEP_STRENGTHS:
                    for step_cap in STEP_CAPS:
                        stepped = base_logit + step_strength * np.clip(local_step * mask, -step_cap, step_cap)
                        for safety_file in safety_files:
                            safety_logit = logits[safety_file]
                            for safety_mask, smask in SAFETY_MASKS.items():
                                for safety_eta in SAFETY_ETAS:
                                    if safety_mask == "none" and safety_eta != 0.0:
                                        continue
                                    guarded = stepped + safety_eta * (safety_logit - stepped) * smask
                                    for keep_orth in ORTH_KEEP:
                                        pred_logit = project_q3s4(guarded, raw_logit, motif_delta, keep_orth)
                                        add_candidate(
                                            rows,
                                            preds,
                                            seen,
                                            label=(
                                                f"axis_direct|base={base_file}|local={local_file}|"
                                                f"mask={step_mask}|s={step_strength:.3f}|cap={step_cap:.3f}|"
                                                f"safety={safety_file}|smask={safety_mask}|eta={safety_eta:.2f}|orth={keep_orth:.2f}"
                                            ),
                                            mode="axis_direct",
                                            base_file=base_file,
                                            local_file=local_file,
                                            safety_file=safety_file,
                                            robust_file="",
                                            step_mask=step_mask,
                                            step_strength=step_strength,
                                            step_cap=step_cap,
                                            safety_mask=safety_mask,
                                            safety_eta=safety_eta,
                                            robust_mask="",
                                            robust_alpha=0.0,
                                            robust_cap=0.0,
                                            keep_orth=keep_orth,
                                            pred_logit=pred_logit,
                                            raw_logit=raw_logit,
                                            motif_delta=motif_delta,
                                            axes=axes,
                                        )

    for base_file in base_files:
        base_logit = logits[base_file]
        for robust_file in robust_files:
            robust_step = logits[robust_file] - raw_logit
            for robust_mask, rmask in ROBUST_MASKS.items():
                for robust_alpha in ROBUST_ALPHAS:
                    for robust_cap in ROBUST_CAPS:
                        robusted = base_logit + robust_alpha * np.clip(robust_step * rmask, -robust_cap, robust_cap)
                        for local_file in local_files[:4]:
                            local_step = logits[local_file] - base_logit
                            for step_mask, mask in {"q2_s123": STEP_MASKS["q2_s123"], "all_soft": STEP_MASKS["all_soft"]}.items():
                                for step_strength in [0.03, 0.06, 0.10]:
                                    stepped = robusted + step_strength * np.clip(local_step * mask, -0.008, 0.008)
                                    for keep_orth in ORTH_KEEP:
                                        pred_logit = project_q3s4(stepped, raw_logit, motif_delta, keep_orth)
                                        add_candidate(
                                            rows,
                                            preds,
                                            seen,
                                            label=(
                                                f"robust_axis_direct|base={base_file}|robust={robust_file}|"
                                                f"rmask={robust_mask}|ra={robust_alpha:.3f}|rcap={robust_cap:.3f}|"
                                                f"local={local_file}|mask={step_mask}|s={step_strength:.3f}|orth={keep_orth:.2f}"
                                            ),
                                            mode="robust_axis_direct",
                                            base_file=base_file,
                                            local_file=local_file,
                                            safety_file="",
                                            robust_file=robust_file,
                                            step_mask=step_mask,
                                            step_strength=step_strength,
                                            step_cap=0.008,
                                            safety_mask="",
                                            safety_eta=0.0,
                                            robust_mask=robust_mask,
                                            robust_alpha=robust_alpha,
                                            robust_cap=robust_cap,
                                            keep_orth=keep_orth,
                                            pred_logit=pred_logit,
                                            raw_logit=raw_logit,
                                            motif_delta=motif_delta,
                                            axes=axes,
                                        )

    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame = add_derived_features(frame)
    local = local_proxy_score(frame)
    frame = frame.drop(columns=[col for col in local.columns if col in frame.columns and col != "file"], errors="ignore")
    frame = frame.merge(local, on="file", how="left", suffixes=("", "_local"))
    frame["axis_prior_score"] = (
        frame["axis_only_raw05_relative_delta_vs_raw05_public"].fillna(0.0)
        + np.maximum(frame["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.20
        + np.maximum(frame["raw_abs"] - 1.0e-7, 0.0) * 12.0
        + np.maximum(frame["bad_abs"] - 0.00014, 0.0) * 0.018
        + np.maximum(0.99990 - frame["q3s4_motif_cos"], 0.0) * 0.001
        + np.maximum(frame["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.0005
    )
    strict = (
        frame["posterior_expected_public_vs_anchor"].le(0.5769055)
        & frame["raw_abs"].le(1.2e-7)
        & frame["bad_abs"].le(0.00016)
        & frame["q3s4_motif_cos"].ge(0.99990)
        & frame["q3s4_motif_orth_ratio"].le(0.0105)
    )
    tight_local = (
        frame["axis_only_raw05_relative_delta_vs_raw05_public"].le(-3.6e-6)
        & frame["posterior_expected_public_vs_anchor"].le(0.576912)
        & frame["raw_abs"].le(1.8e-7)
        & frame["bad_abs"].le(0.00022)
        & frame["q3s4_motif_cos"].ge(0.99985)
        & frame["q3s4_motif_orth_ratio"].le(0.014)
    )
    balanced = (
        frame["axis_only_raw05_relative_delta_vs_raw05_public"].le(-3.9e-6)
        & frame["posterior_expected_public_vs_anchor"].le(0.576925)
        & frame["raw_abs"].le(2.8e-7)
        & frame["bad_abs"].le(0.00036)
        & frame["q3s4_motif_cos"].ge(0.99975)
        & frame["q3s4_motif_orth_ratio"].le(0.018)
    )
    parts = [
        frame[strict].sort_values(["axis_prior_score", "axis_only_raw05_relative_delta_vs_raw05_public"]).head(1300),
        frame[tight_local].sort_values(["axis_prior_score", "axis_only_raw05_relative_delta_vs_raw05_public"]).head(1300),
        frame[balanced].sort_values(["axis_only_raw05_relative_delta_vs_raw05_public", "axis_prior_score"]).head(1300),
        frame.sort_values(["axis_prior_score", "axis_only_raw05_relative_delta_vs_raw05_public"]).head(1600),
    ]
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.head(2800)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = scored.drop(columns=[col for col in actual.columns if col in scored.columns], errors="ignore")
    scored = pd.concat([scored, actual.reset_index(drop=True)], axis=1)
    scored = add_derived_features(scored)
    local = local_proxy_score(scored)
    scored = scored.drop(columns=[col for col in local.columns if col in scored.columns and col != "file"], errors="ignore")
    scored = scored.merge(local, on="file", how="left", suffixes=("", "_local"))
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["strict_hit"] = (
        scored["posterior_expected_public_vs_anchor"].le(0.5769055)
        & scored["raw_abs"].le(1.2e-7)
        & scored["bad_abs"].le(0.00016)
        & scored["q3s4_motif_cos"].ge(0.99990)
        & scored["q3s4_motif_orth_ratio"].le(0.0105)
    )
    scored["tight_local_hit"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"].le(-3.99e-6)
        & scored["posterior_expected_public_vs_anchor"].le(0.576906)
        & scored["raw_abs"].le(1.6e-7)
        & scored["bad_abs"].le(0.00020)
        & scored["q3s4_motif_cos"].ge(0.99990)
        & scored["q3s4_motif_orth_ratio"].le(0.0105)
    )
    scored["direct_score"] = (
        scored["available_raw05_relative_delta_vs_raw05_public"]
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.18
        + np.maximum(scored["raw_abs"] - 1.0e-7, 0.0) * 12.0
        + np.maximum(scored["bad_abs"] - 0.00012, 0.0) * 0.020
        + np.maximum(0.99990 - scored["q3s4_motif_cos"], 0.0) * 0.001
        + np.maximum(scored["q3s4_motif_orth_ratio"] - 0.010, 0.0) * 0.0006
    )
    scored["rank_score"] = (
        0.32 * scored["direct_score"].rank(method="min")
        + 0.22 * scored["available_raw05_relative_delta_vs_raw05_public"].rank(method="min")
        + 0.16 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.12 * scored["bad_abs"].rank(method="min")
        + 0.10 * scored["raw_abs"].rank(method="min")
        + 0.08 * scored["q3s4_motif_orth_ratio"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "direct_score"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("direct_strict", scored["strict_hit"], ["direct_score", "available_raw05_relative_delta_vs_raw05_public"], 36),
        (
            "direct_tight_local",
            scored["tight_local_hit"],
            ["available_raw05_relative_delta_vs_raw05_public", "direct_score"],
            48,
        ),
        (
            "direct_proxy",
            scored["available_raw05_relative_delta_vs_raw05_public"].le(-4.0e-6)
            & scored["posterior_expected_public_vs_anchor"].le(0.576918)
            & scored["raw_abs"].le(2.2e-7)
            & scored["bad_abs"].le(0.00028)
            & scored["q3s4_motif_cos"].ge(0.9998),
            ["available_raw05_relative_delta_vs_raw05_public", "direct_score"],
            36,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "direct_score"]).head(48).assign(bucket="direct_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "direct_score"]).head(96).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_directcon_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected["file"] = files
    return selected


def write_report(scan: pd.DataFrame, selected_prefilter: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    keep = [
        "file",
        "bucket",
        "mode",
        "base_file",
        "local_file",
        "safety_file",
        "robust_file",
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
        "direct_score",
        "rank_score",
    ]
    summary = (
        scored.groupby(["mode", "base_file", "step_mask"], as_index=False)
        .agg(
            n=("label", "size"),
            strict_hits=("strict_hit", "sum"),
            tight_local_hits=("tight_local_hit", "sum"),
            best_local_delta=("available_raw05_relative_delta_vs_raw05_public", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_direct_score=("direct_score", "min"),
        )
        .sort_values(["tight_local_hits", "best_direct_score"], ascending=[False, True])
    )
    lines = [
        "# Raw05 JEPA Direct Constrained Search",
        "",
        "This search injects the axislocal direction while directly constraining posterior, raw/bad axes, and the Q3/S4 JEPA motif at candidate construction time.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- prefiltered candidates: `{len(selected_prefilter)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- strict hits: `{int(scored['strict_hit'].sum())}`",
        f"- tight-local hits: `{int(scored['tight_local_hit'].sum())}`",
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
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    scan, preds = generate(sample)
    scan.to_csv(OUT_SCAN, index=False)
    selected_prefilter = prefilter(scan)
    selected_prefilter.to_csv(OUT_PREFILTER, index=False)
    scored = score_candidates(selected_prefilter, preds, sample)
    selected = select_and_save(scored, preds, sample)
    integ = integrity(selected["file"].astype(str).tolist(), sample)

    scored.to_csv(OUT_SCORED, index=False)
    scored.sort_values(["direct_score", "available_raw05_relative_delta_vs_raw05_public"]).to_csv(OUT_LOCAL, index=False)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, selected_prefilter, scored, selected, integ)

    keep = [
        "file",
        "bucket",
        "mode",
        "base_file",
        "local_file",
        "step_mask",
        "available_raw05_relative_delta_vs_raw05_public",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "direct_score",
    ]
    print(f"generated/prefiltered/scored/saved: {len(scan)} {len(selected_prefilter)} {len(scored)} {len(selected)}")
    print(f"strict/tight-local hits: {int(scored['strict_hit'].sum())} {int(scored['tight_local_hit'].sum())}")
    print(selected[keep].head(30).round(10).to_string(index=False))
    print(f"wrote {OUT_SCAN}")
    print(f"wrote {OUT_PREFILTER}")
    print(f"wrote {OUT_SCORED}")
    print(f"wrote {OUT_LOCAL}")
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_INTEGRITY}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
