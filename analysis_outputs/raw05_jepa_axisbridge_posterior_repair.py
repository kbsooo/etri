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


OUT_SCAN = OUT / "raw05_jepa_axisbridge_posterior_repair_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_axisbridge_posterior_repair_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_axisbridge_posterior_repair_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_axisbridge_posterior_repair_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_axisbridge_posterior_repair_report.md"

AXIS_SHORTLIST = OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv"
PRIORITY = OUT / "final_jepa_candidate_priority_20260527.csv"
SIGREG = OUT / "lejepa_sigreg_candidate_audit.csv"
LOCAL_PROXY = OUT / "local_lb_proxy_validation_candidate_predictions.csv"

INJECT_BETAS = [0.18, 0.28, 0.40, 0.55]
REPAIR_ALPHAS = [0.12, 0.22, 0.35, 0.52]
MAX_STEPS = [0.045, 0.075, 0.115]


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


def candidate_pools() -> tuple[pd.DataFrame, list[str]]:
    axis = read_optional(AXIS_SHORTLIST)
    if axis.empty:
        raise FileNotFoundError(AXIS_SHORTLIST)
    axis = axis.copy()
    axis["raw_abs"] = pd.to_numeric(axis["delta_vs_raw05_rawaxis"], errors="coerce").abs()
    axis["bad_abs"] = pd.to_numeric(axis["bad_residual_axis_ratio"], errors="coerce").abs()
    axis_specs = [
        (axis["file"].notna(), ["rank_score", "selection_score"], 16),
        (
            (axis["delta_vs_raw05_rawaxis"] <= 0.0)
            & (axis["raw_abs"] <= 1.3e-6)
            & (axis["bad_abs"] <= 0.00075),
            ["actual_anchor_score_final", "lejepa_residual_health"],
            16,
        ),
        (
            (axis["posterior_expected_public_vs_anchor"] <= 0.576977)
            & (axis["raw_abs"] <= 1.3e-6),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            16,
        ),
    ]
    axis_rows = []
    for mask, sort_cols, limit in axis_specs:
        part = axis[mask].sort_values([col for col in sort_cols if col in axis.columns]).head(limit)
        axis_rows.append(part)
    axis_rows = pd.concat(axis_rows, ignore_index=True).drop_duplicates("file").head(24).copy()

    priority = read_optional(PRIORITY)
    sigreg = read_optional(SIGREG)
    local = read_optional(LOCAL_PROXY)
    donors: list[str] = []
    if not priority.empty:
        priority = priority.copy()
        file_s = priority["file"].astype(str)
        posterior = pd.to_numeric(priority["posterior_expected_public_vs_anchor"], errors="coerce")
        raw_abs = pd.to_numeric(priority["delta_vs_raw05_rawaxis"], errors="coerce").abs()
        bad_abs = pd.to_numeric(priority["bad_residual_axis_ratio"], errors="coerce").abs()
        safe_mask = (
            file_s.str.startswith("submission_raw05_jepa_")
            & ~file_s.str.contains("axisbridge|public6q3s4corr", regex=True, na=False)
            & posterior.le(0.576905)
            & raw_abs.le(2.0e-7)
            & bad_abs.le(0.0010)
        )
        donors.extend(top_files(priority, ["posterior_expected_public_vs_anchor", "lejepa_combined_rank"], 18, safe_mask))
        donors.extend(top_files(priority, ["lejepa_combined_rank", "posterior_expected_public_vs_anchor"], 18, safe_mask))
    if not sigreg.empty and "family" in sigreg.columns:
        sigreg = sigreg.copy()
        posterior = pd.to_numeric(sigreg["posterior_expected_public_vs_anchor"], errors="coerce")
        raw_abs = pd.to_numeric(sigreg["delta_vs_raw05_rawaxis"], errors="coerce").abs()
        bad_abs = pd.to_numeric(sigreg["bad_residual_axis_ratio"], errors="coerce").abs()
        safe_families = sigreg["family"].isin(
            [
                "raw05_jepa_efmicro",
                "raw05_jepa_siganchor",
                "raw05_jepa_siggate",
                "raw05_jepa_efback",
                "raw05_jepa_efgate",
                "raw05_jepa_blockcountreg",
                "raw05_jepa_tangentnull",
                "raw05_jepa_energyfront",
            ]
        )
        safe_mask = safe_families & posterior.le(0.576905) & raw_abs.le(2.0e-7) & bad_abs.le(0.0012)
        donors.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 20, safe_mask))
        donors.extend(top_files(sigreg, ["posterior_expected_public_vs_anchor", "lejepa_residual_health"], 20, safe_mask))
    if not local.empty:
        local = local.copy()
        file_s = local["file"].astype(str)
        posterior = pd.to_numeric(local["posterior_scenario_not_independent"], errors="coerce")
        raw_abs = pd.to_numeric(local["delta_vs_raw05_rawaxis"], errors="coerce").abs()
        bad_abs = pd.to_numeric(local["bad_residual_axis_ratio"], errors="coerce").abs()
        safe_mask = (
            file_s.str.startswith("submission_raw05_jepa_")
            & ~file_s.str.contains("axisbridge|public6q3s4corr", regex=True, na=False)
            & posterior.le(0.576905)
            & raw_abs.le(2.0e-7)
            & bad_abs.le(0.0012)
        )
        donors.extend(top_files(local, ["available_raw05_relative_lb_proxy_mean", "posterior_scenario_not_independent"], 18, safe_mask))

    return axis_rows, unique_existing(donors, 26)


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def mask_from_weights(weights: dict[str, float]) -> np.ndarray:
    return np.asarray([weights.get(target, 0.0) for target in TARGETS], dtype=np.float64).reshape(1, -1)


INJECT_PROFILES = [
    ("inject_q3", mask_from_weights({"Q3": 1.0})),
    ("inject_q3s4", mask_from_weights({"Q3": 1.0, "S4": 1.0})),
    ("inject_q3_s4half", mask_from_weights({"Q3": 1.0, "S4": 0.45})),
    ("inject_q3_sblockmicro", mask_from_weights({"Q3": 1.0, "S1": 0.10, "S2": 0.10, "S3": 0.10, "S4": 0.35})),
]

REPAIR_PROFILES = [
    ("repair_context_only", mask_from_weights({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0})),
    ("repair_context_s4light", mask_from_weights({"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0, "S4": 0.25})),
    ("repair_q2s123", mask_from_weights({"Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0})),
    ("repair_all_tiny", mask_from_weights({"Q1": 0.25, "Q2": 0.35, "Q3": 0.12, "S1": 0.35, "S2": 0.35, "S3": 0.35, "S4": 0.12})),
]


def row_gate(axis_logit: np.ndarray, base_logit: np.ndarray, mode: str) -> np.ndarray:
    target_cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    motif = np.abs(axis_logit[:, target_cols] - base_logit[:, target_cols]).mean(axis=1)
    lo = float(np.quantile(motif, 0.10))
    hi = float(np.quantile(motif, 0.90))
    scaled = np.clip((motif - lo) / max(hi - lo, 1e-12), 0.0, 1.0)
    if mode == "none":
        gate = np.ones_like(scaled)
    elif mode == "motif_soft":
        gate = 0.35 + 0.65 * scaled
    elif mode == "motif_strong":
        gate = 0.15 + 0.85 * scaled
    elif mode == "inverse_motif":
        gate = 0.35 + 0.65 * (1.0 - scaled)
    else:
        raise ValueError(f"unknown gate mode: {mode}")
    return gate.reshape(-1, 1)


def target_motif_retention(pred_logit: np.ndarray, donor_logit: np.ndarray, axis_logit: np.ndarray, base_logit: np.ndarray) -> float:
    cols = [TARGETS.index("Q3"), TARGETS.index("S4")]
    denom = np.abs(axis_logit[:, cols] - base_logit[:, cols]).mean()
    if denom < 1e-12:
        return 0.0
    return float(np.abs(pred_logit[:, cols] - donor_logit[:, cols]).mean() / denom)


def generate_candidates(
    axis_rows: pd.DataFrame,
    donors: list[str],
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
        axis_pred = arrays[axis_file]
        base_logit = logits[base_file]
        target_step = axis_logit - base_logit

        for donor_file in donors:
            if donor_file in {axis_file, base_file}:
                continue
            donor_logit = logits[donor_file]
            donor_pred = arrays[donor_file]

            for gate_mode in ["none", "motif_soft", "inverse_motif"]:
                gate = row_gate(axis_logit, base_logit, gate_mode)
                for profile_name, profile_mask in INJECT_PROFILES:
                    for beta in INJECT_BETAS:
                        for max_step in MAX_STEPS:
                            step = np.clip(target_step * profile_mask * gate, -max_step, max_step)
                            pred_logit = donor_logit + beta * step
                            pred = clip(sigmoid(pred_logit))
                            pred_hash = prediction_hash(pred)
                            if pred_hash in seen:
                                continue
                            seen.add(pred_hash)
                            mean_move_axis = float(np.abs(pred - axis_pred).mean())
                            mean_move_donor = float(np.abs(pred - donor_pred).mean())
                            row: dict[str, object] = {
                                "label": (
                                    f"inject|axis={axis_file}|base={base_file}|donor={donor_file}|"
                                    f"{profile_name}|beta={beta:.2f}|cap={max_step:.3f}|gate={gate_mode}"
                                ),
                                "prediction_hash": pred_hash,
                                "mode": "donor_plus_axis_motif",
                                "axis_file": axis_file,
                                "axis_base_file": base_file,
                                "donor_file": donor_file,
                                "profile": profile_name,
                                "gate_mode": gate_mode,
                                "beta": float(beta),
                                "alpha": np.nan,
                                "max_step": float(max_step),
                                "mean_abs_move_vs_axis": mean_move_axis,
                                "mean_abs_move_vs_donor": mean_move_donor,
                                "target_motif_retention": target_motif_retention(pred_logit, donor_logit, axis_logit, base_logit),
                                "mean_signed_delta_q3_vs_donor": float((pred[:, TARGETS.index("Q3")] - donor_pred[:, TARGETS.index("Q3")]).mean()),
                                "mean_signed_delta_s4_vs_donor": float((pred[:, TARGETS.index("S4")] - donor_pred[:, TARGETS.index("S4")]).mean()),
                            }
                            row.update(public_axis_features(pred, axes))
                            rows.append(row)
                            preds.append(pred)

                for profile_name, profile_mask in REPAIR_PROFILES:
                    for alpha in REPAIR_ALPHAS:
                        for max_step in MAX_STEPS:
                            repair_step = np.clip((donor_logit - axis_logit) * profile_mask * gate, -max_step, max_step)
                            pred_logit = axis_logit + alpha * repair_step
                            pred = clip(sigmoid(pred_logit))
                            pred_hash = prediction_hash(pred)
                            if pred_hash in seen:
                                continue
                            seen.add(pred_hash)
                            mean_move_axis = float(np.abs(pred - axis_pred).mean())
                            mean_move_donor = float(np.abs(pred - donor_pred).mean())
                            row = {
                                "label": (
                                    f"repair|axis={axis_file}|base={base_file}|donor={donor_file}|"
                                    f"{profile_name}|alpha={alpha:.2f}|cap={max_step:.3f}|gate={gate_mode}"
                                ),
                                "prediction_hash": pred_hash,
                                "mode": "axis_plus_context_repair",
                                "axis_file": axis_file,
                                "axis_base_file": base_file,
                                "donor_file": donor_file,
                                "profile": profile_name,
                                "gate_mode": gate_mode,
                                "beta": np.nan,
                                "alpha": float(alpha),
                                "max_step": float(max_step),
                                "mean_abs_move_vs_axis": mean_move_axis,
                                "mean_abs_move_vs_donor": mean_move_donor,
                                "target_motif_retention": target_motif_retention(pred_logit, donor_logit, axis_logit, base_logit),
                                "mean_signed_delta_q3_vs_donor": float((pred[:, TARGETS.index("Q3")] - donor_pred[:, TARGETS.index("Q3")]).mean()),
                                "mean_signed_delta_s4_vs_donor": float((pred[:, TARGETS.index("S4")] - donor_pred[:, TARGETS.index("S4")]).mean()),
                            }
                            row.update(public_axis_features(pred, axes))
                            rows.append(row)
                            preds.append(pred)

    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["posterior_repair_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(frame["raw_abs"] - 1.3e-6, 0.0) * 55.0
        + np.maximum(frame["bad_abs"] - 0.0010, 0.0) * 0.060
        + np.maximum(frame["mean_abs_move_vs_donor"] - 0.0009, 0.0) * 0.020
        + np.maximum(0.22 - frame["target_motif_retention"], 0.0) * 0.00040
    )
    specs = [
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57691)
            & (frame["raw_abs"] <= 3.0e-7)
            & (frame["bad_abs"] <= 0.00075),
            ["posterior_repair_score"],
            900,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57693)
            & (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.0012),
            ["posterior_repair_score"],
            900,
        ),
        (
            (frame["target_motif_retention"] >= 0.45)
            & (frame["raw_abs"] <= 1.5e-6)
            & (frame["bad_abs"] <= 0.0014),
            ["posterior_repair_score"],
            900,
        ),
        (
            frame["mode"].eq("axis_plus_context_repair")
            & (frame["raw_abs"] <= 1.5e-6)
            & (frame["bad_abs"] <= 0.0012),
            ["posterior_repair_score"],
            900,
        ),
        (
            frame["mode"].eq("donor_plus_axis_motif")
            & (frame["posterior_expected_public_vs_anchor"] <= 0.576905)
            & (frame["raw_abs"] <= 1.0e-6),
            ["posterior_repair_score"],
            900,
        ),
    ]
    parts = [frame[mask].sort_values(cols).head(limit) for mask, cols, limit in specs if not frame[mask].empty]
    parts.append(frame.sort_values("posterior_repair_score").head(1400))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("posterior_repair_score").head(3600)


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
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.576905, 0.0) * 0.85
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.2e-7, 0.0) * 260.0
        + np.maximum(scored["raw_abs"] - 9.0e-7, 0.0) * 60.0
        + np.maximum(scored["bad_abs"] - 0.00085, 0.0) * 0.060
        + np.maximum(0.30 - scored["target_motif_retention"], 0.0) * 0.00035
    )
    scored["rank_score"] = (
        0.30 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.24 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.18 * scored["raw_abs"].rank(method="min")
        + 0.14 * scored["bad_abs"].rank(method="min")
        + 0.14 * (-scored["target_motif_retention"]).rank(method="min")
    )
    return scored.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "repair_posterior_safe",
            (scored["posterior_expected_public_vs_anchor"] <= 0.576905)
            & (scored["raw_abs"] <= 5.0e-7)
            & (scored["bad_abs"] <= 0.0009),
            ["actual_anchor_score_final", "selection_score"],
            20,
        ),
        (
            "repair_rawnegative",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_abs"] <= 0.0012)
            & (scored["actual_anchor_score_final"] <= 0.577840),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            20,
        ),
        (
            "repair_motif_retained",
            (scored["target_motif_retention"] >= 0.45)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57693)
            & (scored["raw_abs"] <= 1.3e-6),
            ["selection_score", "actual_anchor_score_final"],
            20,
        ),
        (
            "repair_lowbad",
            (scored["bad_abs"] <= 0.00028)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57693)
            & (scored["raw_abs"] <= 1.3e-6),
            ["selection_score", "actual_anchor_score_final"],
            20,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "selection_score"]).head(32).assign(bucket="repair_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_axisrepair_{tag}.csv"
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
        "mean_abs_move_vs_axis",
        "mean_abs_move_vs_donor",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "rank_score",
    ]
    summary = (
        scored.groupby(["mode", "profile"], as_index=False)
        .agg(
            n=("label", "size"),
            best_actual=("actual_anchor_score_final", "min"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_selection=("selection_score", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_motif_retention=("target_motif_retention", "max"),
        )
        .sort_values(["best_selection", "best_actual"])
    )
    lines = [
        "# Raw05 JEPA Axisbridge Posterior Repair",
        "",
        "Repairs the posterior/energy weakness of axis-budget motif bridge candidates. Two JEPA-style transforms are tested: inject the axisbridge Q3/S4 target residual into posterior-safe A-family donors, and repair axisbridge context coordinates toward posterior-safe donors while preserving the target motif.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
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
        selected[cols].head(60).round(10).to_csv(index=False).strip(),
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
    axis_rows, donors = candidate_pools()
    files = unique_existing([*axis_rows["file"].astype(str).tolist(), *axis_rows["base_file"].astype(str).tolist(), *donors])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}

    if axis_rows.empty or not donors:
        raise RuntimeError(f"empty pool: axis={len(axis_rows)} donors={len(donors)}")

    scan, preds = generate_candidates(axis_rows, donors, arrays, axes)
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
        "gate_mode",
        "target_motif_retention",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "selection_score",
    ]
    print(f"pools axis={len(axis_rows)} donors={len(donors)}")
    print(f"generated={len(scan)} scored={len(scored)} saved={len(shortlist)}")
    print(shortlist[cols].head(35).round(10).to_string(index=False))
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
