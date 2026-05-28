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
    actual_anchor_score,
    integrity,
    locate,
    read_submission,
    save_submission,
)


OUT_SCAN = OUT / "raw05_jepa_axisrepair_tradeoff_direct_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_axisrepair_tradeoff_direct_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_axisrepair_tradeoff_direct_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_axisrepair_tradeoff_direct_report.md"

AXIS_SHORTLIST = OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv"
AXISREPAIR_SHORTLIST = OUT / "raw05_jepa_axisbridge_posterior_repair_shortlist.csv"
PRIORITY = OUT / "final_jepa_candidate_priority_20260527.csv"
SIGREG = OUT / "lejepa_sigreg_candidate_audit.csv"
LOCAL_PROXY = OUT / "local_lb_proxy_validation_candidate_predictions.csv"

BETAS = [0.62, 0.78, 0.96, 1.18]
ALPHAS = [0.18, 0.32, 0.48]
REPAIR_ALPHAS = [0.45, 0.62, 0.82]
MAX_STEPS = [0.055, 0.085, 0.125, 0.180]


def exists(file_name: str) -> bool:
    try:
        locate(file_name)
    except FileNotFoundError:
        return False
    return True


def unique_existing(files: list[str], limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for file_name in files:
        if not file_name or file_name in seen or not exists(file_name):
            continue
        seen.add(file_name)
        out.append(file_name)
        if limit is not None and len(out) >= limit:
            break
    return out


def read_optional(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def top_files(frame: pd.DataFrame, sort_cols: list[str], n: int, mask: pd.Series | None = None) -> list[str]:
    if frame.empty or "file" not in frame.columns:
        return []
    part = frame[mask].copy() if mask is not None else frame.copy()
    if part.empty:
        return []
    cols = [col for col in sort_cols if col in part.columns]
    if cols:
        part = part.sort_values(cols)
    return part["file"].astype(str).head(n).tolist()


def add_abs(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "delta_vs_raw05_rawaxis" in out.columns:
        out["raw_abs"] = pd.to_numeric(out["delta_vs_raw05_rawaxis"], errors="coerce").abs()
    if "bad_residual_axis_ratio" in out.columns:
        out["bad_abs"] = pd.to_numeric(out["bad_residual_axis_ratio"], errors="coerce").abs()
    return out


def candidate_pools() -> tuple[pd.DataFrame, list[str], list[str]]:
    axis = add_abs(read_optional(AXIS_SHORTLIST))
    if axis.empty:
        raise FileNotFoundError(AXIS_SHORTLIST)
    axis_specs = [
        (axis["file"].notna(), ["rank_score", "selection_score"], 18),
        (
            (axis["delta_vs_raw05_rawaxis"] <= 0.0)
            & (axis["raw_abs"] <= 1.4e-6)
            & (axis["bad_abs"] <= 0.00080),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            18,
        ),
        (
            (axis["bad_abs"] <= 0.00035)
            & (axis["raw_abs"] <= 8.0e-7),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            18,
        ),
    ]
    axis_rows = []
    for mask, sort_cols, limit in axis_specs:
        cols = [col for col in sort_cols if col in axis.columns]
        axis_rows.append(axis[mask].sort_values(cols).head(limit))
    axis_rows = pd.concat(axis_rows, ignore_index=True).drop_duplicates("file").head(12).copy()

    sources = [read_optional(PRIORITY), read_optional(SIGREG), read_optional(LOCAL_PROXY)]
    donors: list[str] = []
    compensators: list[str] = []

    for frame in sources:
        if frame.empty or "file" not in frame.columns:
            continue
        frame = add_abs(frame)
        file_s = frame["file"].astype(str)
        posterior_col = (
            "posterior_expected_public_vs_anchor"
            if "posterior_expected_public_vs_anchor" in frame.columns
            else "posterior_scenario_not_independent"
        )
        posterior = pd.to_numeric(frame[posterior_col], errors="coerce")
        raw_abs = pd.to_numeric(frame.get("raw_abs"), errors="coerce")
        bad_abs = pd.to_numeric(frame.get("bad_abs"), errors="coerce")
        not_axis = ~file_s.str.contains("axisbridge|axisrepair|public6q3s4corr", regex=True, na=False)
        usable = not_axis & raw_abs.le(5.0e-7) & bad_abs.le(0.0026)
        posterior_safe = usable & posterior.le(0.576905)
        low_posterior = usable & posterior.le(0.576890)
        broad_low_posterior = not_axis & raw_abs.le(7.0e-7) & bad_abs.le(0.0032) & posterior.le(0.576870)

        donors.extend(top_files(frame, [posterior_col, "actual_anchor_score_final"], 18, posterior_safe))
        donors.extend(top_files(frame, ["lejepa_combined_rank", posterior_col], 18, posterior_safe))
        donors.extend(top_files(frame, ["available_raw05_relative_lb_proxy_mean", posterior_col], 12, posterior_safe))
        compensators.extend(top_files(frame, [posterior_col, "bad_abs"], 16, low_posterior))
        compensators.extend(top_files(frame, [posterior_col, "actual_anchor_score_final"], 16, broad_low_posterior))

    # Add the prior partial motif repair as a donor: it is posterior-safe and already carries some Q3/S4 motif.
    prior_repair = read_optional(AXISREPAIR_SHORTLIST)
    if not prior_repair.empty:
        prior_repair = add_abs(prior_repair)
        safe_partial = (
            prior_repair["target_motif_retention"].ge(0.30)
            & prior_repair["posterior_expected_public_vs_anchor"].le(0.576905)
            & prior_repair["raw_abs"].le(2.0e-7)
            & prior_repair["bad_abs"].le(0.00035)
        )
        donors.extend(top_files(prior_repair, ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"], 12, safe_partial))

    return axis_rows, unique_existing(donors, 16), unique_existing(compensators, 6)


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def mask_from_weights(weights: dict[str, float]) -> np.ndarray:
    return np.asarray([weights.get(target, 0.0) for target in TARGETS], dtype=np.float64).reshape(1, -1)


TARGET_PROFILES = [
    ("q3_only", mask_from_weights({"Q3": 1.0})),
    ("q3_s4half", mask_from_weights({"Q3": 1.0, "S4": 0.50})),
    ("q3s4", mask_from_weights({"Q3": 1.0, "S4": 1.0})),
    ("q3_sblockmicro", mask_from_weights({"Q3": 1.0, "S1": 0.08, "S2": 0.08, "S3": 0.08, "S4": 0.35})),
]

CONTEXT_PROFILES = [
    ("ctx_q1q2s123", mask_from_weights({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0})),
    ("ctx_q2s123", mask_from_weights({"Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0})),
    ("ctx_sblock_q2", mask_from_weights({"Q2": 0.55, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.12})),
]

SOFT_REPAIR_PROFILES = [
    ("soft_ctx_q3s4_05", mask_from_weights({"Q1": 1.0, "Q2": 1.0, "Q3": 0.05, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.05})),
    ("soft_ctx_q3s4_12", mask_from_weights({"Q1": 1.0, "Q2": 1.0, "Q3": 0.12, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.12})),
    ("soft_sblock_q3_08", mask_from_weights({"Q2": 0.65, "Q3": 0.08, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.15})),
]


def row_gate(axis_logit: np.ndarray, base_logit: np.ndarray, mode: str) -> np.ndarray:
    cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    motif = np.abs(axis_logit[:, cols] - base_logit[:, cols]).mean(axis=1)
    lo = float(np.quantile(motif, 0.10))
    hi = float(np.quantile(motif, 0.90))
    scaled = np.clip((motif - lo) / max(hi - lo, 1e-12), 0.0, 1.0)
    if mode == "none":
        gate = np.ones_like(scaled)
    elif mode == "motif_soft":
        gate = 0.35 + 0.65 * scaled
    elif mode == "motif_strong":
        gate = 0.15 + 0.85 * scaled
    else:
        raise ValueError(f"unknown gate mode: {mode}")
    return gate.reshape(-1, 1)


def target_motif_retention(pred_logit: np.ndarray, donor_logit: np.ndarray, axis_logit: np.ndarray, base_logit: np.ndarray) -> float:
    cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    denom = np.abs(axis_logit[:, cols] - base_logit[:, cols]).mean()
    if denom < 1e-12:
        return 0.0
    return float(np.abs(pred_logit[:, cols] - donor_logit[:, cols]).mean() / denom)


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    pred_logit: np.ndarray,
    label: str,
    mode: str,
    axis_file: str,
    base_file: str,
    donor_file: str,
    comp_file: str,
    profile: str,
    gate_mode: str,
    beta: float,
    alpha: float,
    max_step: float,
    axis_logit: np.ndarray,
    base_logit: np.ndarray,
    donor_logit: np.ndarray,
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
        "label": label,
        "prediction_hash": pred_hash,
        "mode": mode,
        "axis_file": axis_file,
        "axis_base_file": base_file,
        "donor_file": donor_file,
        "comp_file": comp_file,
        "profile": profile,
        "gate_mode": gate_mode,
        "beta": beta,
        "alpha": alpha,
        "max_step": max_step,
        "mean_abs_move_vs_axis": float(np.abs(pred - axis_pred).mean()),
        "mean_abs_move_vs_donor": float(np.abs(pred - donor_pred).mean()),
        "target_motif_retention": target_motif_retention(pred_logit, donor_logit, axis_logit, base_logit),
        "mean_signed_delta_q3_vs_donor": float((pred[:, TARGETS.index("Q3")] - donor_pred[:, TARGETS.index("Q3")]).mean()),
        "mean_signed_delta_s4_vs_donor": float((pred[:, TARGETS.index("S4")] - donor_pred[:, TARGETS.index("S4")]).mean()),
    }
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate_candidates(
    axis_rows: pd.DataFrame,
    donors: list[str],
    compensators: list[str],
    arrays: dict[str, np.ndarray],
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for axis_row in axis_rows.to_dict(orient="records"):
        axis_file = str(axis_row["file"])
        base_file = str(axis_row["base_file"])
        axis_logit = logits[axis_file]
        base_logit = logits[base_file]
        axis_pred = arrays[axis_file]
        target_step = axis_logit - base_logit

        for donor_file in donors:
            if donor_file in {axis_file, base_file}:
                continue
            donor_logit = logits[donor_file]
            donor_pred = arrays[donor_file]

            for gate_mode in ["none", "motif_soft", "motif_strong"]:
                gate = row_gate(axis_logit, base_logit, gate_mode)
                for profile_name, profile_mask in TARGET_PROFILES:
                    for beta in BETAS:
                        for max_step in MAX_STEPS:
                            step = np.clip(target_step * profile_mask * gate, -max_step, max_step)
                            pred_logit = donor_logit + beta * step
                            add_candidate(
                                rows,
                                preds,
                                seen,
                                pred_logit,
                                f"inject|axis={axis_file}|base={base_file}|donor={donor_file}|{profile_name}|b={beta:.2f}|cap={max_step:.3f}|gate={gate_mode}",
                                "highret_inject",
                                axis_file,
                                base_file,
                                donor_file,
                                "",
                                profile_name,
                                gate_mode,
                                float(beta),
                                np.nan,
                                float(max_step),
                                axis_logit,
                                base_logit,
                                donor_logit,
                                axis_pred,
                                donor_pred,
                                axes,
                            )

                    if gate_mode != "none" or profile_name not in {"q3_s4half", "q3s4"}:
                        continue
                    for comp_file in compensators:
                        if comp_file in {axis_file, base_file, donor_file}:
                            continue
                        comp_logit = logits[comp_file]
                        for ctx_name, ctx_mask in CONTEXT_PROFILES[:1]:
                            for beta in [0.78, 0.96]:
                                for alpha in [0.18, 0.32]:
                                    for max_step in [0.055, 0.085]:
                                        target = np.clip(target_step * profile_mask * gate, -max_step, max_step)
                                        context = np.clip((comp_logit - donor_logit) * ctx_mask, -max_step, max_step)
                                        pred_logit = donor_logit + beta * target + alpha * context
                                        add_candidate(
                                            rows,
                                            preds,
                                            seen,
                                            pred_logit,
                                            f"compinject|axis={axis_file}|base={base_file}|donor={donor_file}|comp={comp_file}|{profile_name}|{ctx_name}|b={beta:.2f}|a={alpha:.2f}|cap={max_step:.3f}|gate={gate_mode}",
                                            "compensated_inject",
                                            axis_file,
                                            base_file,
                                            donor_file,
                                            comp_file,
                                            f"{profile_name}+{ctx_name}",
                                            gate_mode,
                                            float(beta),
                                            float(alpha),
                                            float(max_step),
                                            axis_logit,
                                            base_logit,
                                            donor_logit,
                                            axis_pred,
                                            donor_pred,
                                            axes,
                                        )

            for repair_name, repair_mask in SOFT_REPAIR_PROFILES:
                for alpha in REPAIR_ALPHAS:
                    for max_step in [0.055, 0.085, 0.125]:
                        repair_step = np.clip((donor_logit - axis_logit) * repair_mask, -max_step, max_step)
                        pred_logit = axis_logit + alpha * repair_step
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            pred_logit,
                            f"softrepair|axis={axis_file}|base={base_file}|donor={donor_file}|{repair_name}|a={alpha:.2f}|cap={max_step:.3f}",
                            "soft_axis_repair",
                            axis_file,
                            base_file,
                            donor_file,
                            "",
                            repair_name,
                            "none",
                            np.nan,
                            float(alpha),
                            float(max_step),
                            axis_logit,
                            base_logit,
                            donor_logit,
                            axis_pred,
                            donor_pred,
                            axes,
                        )

    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["goal_hit"] = (
        (frame["target_motif_retention"] >= 0.70)
        & (frame["posterior_expected_public_vs_anchor"] <= 0.57691)
        & (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
        & (frame["bad_abs"] <= 0.0022)
    )
    frame["tradeoff_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(0.70 - frame["target_motif_retention"], 0.0) * 0.00055
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(frame["raw_abs"] - 6.0e-7, 0.0) * 55.0
        + np.maximum(frame["bad_abs"] - 0.0014, 0.0) * 0.055
        + np.maximum(frame["mean_abs_move_vs_donor"] - 0.0009, 0.0) * 0.018
    )
    specs = [
        (frame["goal_hit"], ["tradeoff_score", "posterior_expected_public_vs_anchor"], 1200),
        (
            (frame["target_motif_retention"] >= 0.70)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.5e-7),
            ["tradeoff_score"],
            1000,
        ),
        (
            (frame["target_motif_retention"] >= 0.90)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.576935)
            & (frame["raw_abs"] <= 1.4e-6),
            ["posterior_expected_public_vs_anchor", "bad_abs"],
            900,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (frame["target_motif_retention"] >= 0.45)
            & (frame["raw_abs"] <= 1.2e-6),
            ["tradeoff_score"],
            900,
        ),
        (frame["mode"].eq("compensated_inject"), ["tradeoff_score"], 900),
    ]
    parts = [frame[mask].sort_values(cols).head(limit) for mask, cols, limit in specs if not frame[mask].empty]
    parts.append(frame.sort_values("tradeoff_score").head(1600))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("tradeoff_score").head(4200)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual.reset_index(drop=True)], axis=1)
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["raw_abs"] = scored["delta_vs_raw05_rawaxis"].abs()
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.90
        + np.maximum(0.70 - scored["target_motif_retention"], 0.0) * 0.00045
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(scored["raw_abs"] - 7.5e-7, 0.0) * 60.0
        + np.maximum(scored["bad_abs"] - 0.00135, 0.0) * 0.055
    )
    scored["rank_score"] = (
        0.28 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.24 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.18 * (-scored["target_motif_retention"]).rank(method="min")
        + 0.16 * scored["raw_abs"].rank(method="min")
        + 0.14 * scored["bad_abs"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "tradeoff_goal_hit",
            (scored["target_motif_retention"] >= 0.70)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57691)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_abs"] <= 0.0022),
            ["actual_anchor_score_final", "selection_score"],
            24,
        ),
        (
            "tradeoff_highret",
            (scored["target_motif_retention"] >= 0.90)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57693)
            & (scored["raw_abs"] <= 1.2e-6),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            18,
        ),
        (
            "tradeoff_postsafe",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (scored["target_motif_retention"] >= 0.45)
            & (scored["raw_abs"] <= 1.0e-6),
            ["selection_score", "actual_anchor_score_final"],
            18,
        ),
        (
            "tradeoff_lowbad",
            (scored["bad_abs"] <= 0.00035)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57691)
            & (scored["target_motif_retention"] >= 0.55),
            ["selection_score", "actual_anchor_score_final"],
            18,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "selection_score"]).head(36).assign(bucket="tradeoff_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).head(84).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_axistrade_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "mode",
        "axis_file",
        "donor_file",
        "comp_file",
        "profile",
        "gate_mode",
        "beta",
        "alpha",
        "max_step",
        "target_motif_retention",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_donor",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "rank_score",
    ]
    summary = (
        scored.groupby(["mode", "profile"], as_index=False)
        .agg(
            n=("label", "size"),
            goal_hits=("goal_hit", "sum"),
            best_actual=("actual_anchor_score_final", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            max_retention=("target_motif_retention", "max"),
            best_selection=("selection_score", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_bad_abs=("bad_abs", "min"),
        )
        .sort_values(["goal_hits", "best_selection", "best_actual"], ascending=[False, True, True])
    )
    lines = [
        "# Raw05 JEPA Axisrepair Direct Tradeoff Search",
        "",
        "Directly optimizes the posterior-safe versus target-motif-retention tradeoff. The main goal is `target_motif_retention >= 0.70`, `posterior <= 0.57691`, and raw-axis drift at or below the raw05 boundary.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        f"- pre-score goal hits: `{int(scan.get('goal_hit', pd.Series(dtype=bool)).sum()) if 'goal_hit' in scan.columns else 'n/a'}`",
        f"- scored goal hits: `{int(scored['goal_hit'].sum()) if 'goal_hit' in scored.columns else 0}`",
        "",
        "## Profile Summary",
        "",
        "```csv",
        summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[cols].head(70).round(10).to_csv(index=False).strip(),
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
    axes = public_axes()
    axis_rows, donors, compensators = candidate_pools()
    files = unique_existing(
        [
            *axis_rows["file"].astype(str).tolist(),
            *axis_rows["base_file"].astype(str).tolist(),
            *donors,
            *compensators,
        ]
    )
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    if axis_rows.empty or not donors:
        raise RuntimeError(f"empty pool: axis={len(axis_rows)} donors={len(donors)} comp={len(compensators)}")

    scan, preds = generate_candidates(axis_rows, donors, compensators, arrays, axes)
    scan.to_csv(OUT_SCAN, index=False)
    selected_for_scoring = prefilter(scan)
    scored = score_candidates(selected_for_scoring, preds, sample)
    scored.to_csv(OUT_SCORED, index=False)
    shortlist = select_and_save(scored, preds, sample)
    integ = integrity(shortlist["file"].astype(str).tolist(), sample)
    shortlist = shortlist.merge(integ, on="file", how="left", suffixes=("", "_integrity"))
    shortlist.to_csv(OUT_SHORTLIST, index=False)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, shortlist, integ)

    cols = [
        "file",
        "bucket",
        "mode",
        "profile",
        "target_motif_retention",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "selection_score",
    ]
    print(f"pools axis={len(axis_rows)} donors={len(donors)} comp={len(compensators)}")
    print(f"generated={len(scan)} scored={len(scored)} saved={len(shortlist)}")
    print(shortlist[cols].head(40).round(10).to_string(index=False))
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
