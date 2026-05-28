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


OUT_SCAN = OUT / "raw05_jepa_axisbudget_motif_bridge_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_axisbudget_motif_bridge_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_axisbudget_motif_bridge_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_axisbudget_motif_bridge_report.md"

RISK_WEIGHTS = [0.22, 0.40, 0.68]
COUNTER_WEIGHTS = [0.22, 0.55, 0.95]
MAX_STEPS = [0.10, 0.18]


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


def read_optional(name: str) -> pd.DataFrame:
    path = OUT / name
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


def candidate_pools() -> tuple[list[str], list[str], list[str]]:
    priority = read_optional("final_jepa_candidate_priority_20260527.csv")
    sigreg = read_optional("lejepa_sigreg_candidate_audit.csv")
    public6 = read_optional("raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv")
    public6_scan = read_optional("raw05_jepa_public6_q3s4_axis_corrected_scan.csv")
    cellgate = read_optional("hidden_block_sequence_motif_cellgate_safe_scores.csv")
    q3s4gate = read_optional("raw05_jepa_q3s4_gate_candidate_scores.csv")
    blockrefine = read_optional("block_public_jepa_q3s4_refine_shortlist.csv")

    bases: list[str] = []
    if not priority.empty:
        bases.extend(
            priority[
                priority["tier"].astype(str).str.startswith("A")
                & priority["file"].astype(str).str.startswith("submission_raw05_jepa_")
                & ~priority["file"].astype(str).str.contains("public6q3s4corr", na=False)
            ]["file"]
            .astype(str)
            .head(16)
            .tolist()
        )
    if not sigreg.empty and "family" in sigreg.columns:
        for family in ["raw05_jepa_efmicro", "raw05_jepa_siganchor", "raw05_jepa_siggate", "raw05_jepa_efgate"]:
            bases.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 4, sigreg["family"].eq(family)))

    risk: list[str] = []
    for table in [public6, public6_scan]:
        if table.empty:
            continue
        table = table.copy()
        if "delta_vs_raw05_rawaxis" in table.columns:
            raw_abs = table["delta_vs_raw05_rawaxis"].abs()
            risk.extend(top_files(table, ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"], 18, raw_abs.le(8.0e-5)))
            risk.extend(top_files(table, ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"], 8, raw_abs.le(8.0e-5)))
            risk.extend(top_files(table, ["delta_vs_raw05_rawaxis", "actual_anchor_score_final"], 8))
        else:
            risk.extend(top_files(table, ["actual_anchor_score_final"], 20))

    counter: list[str] = []
    if not cellgate.empty:
        counter.extend(top_files(cellgate, ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"], 24))
        counter.extend(top_files(cellgate, ["bad_residual_axis_ratio", "posterior_expected_public_vs_anchor"], 10))
    if not q3s4gate.empty:
        counter.extend(top_files(q3s4gate, ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"], 18))
        counter.extend(top_files(q3s4gate, ["focused_scenario_score", "delta_vs_raw05_rawaxis"], 10))
    if not blockrefine.empty:
        counter.extend(top_files(blockrefine, ["delta_vs_raw05_rawaxis", "focused_scenario_score"], 12))

    return unique_existing(bases, 10), unique_existing(risk, 16), unique_existing(counter, 18)


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def profile_masks() -> list[tuple[str, np.ndarray, np.ndarray]]:
    def mask(*targets: str) -> np.ndarray:
        allowed = set(targets)
        return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)

    return [
        ("risk_q3s4_counter_q3s4", mask("Q3", "S4"), mask("Q3", "S4")),
        ("risk_q3s4_counter_sblock", mask("Q3", "S4"), mask("S1", "S2", "S3", "S4")),
        ("risk_q3s4_counter_noq2", mask("Q3", "S4"), mask("Q1", "Q3", "S1", "S2", "S3", "S4")),
        ("risk_q3_counter_noq2", mask("Q3"), mask("Q1", "Q3", "S1", "S2", "S3", "S4")),
    ]


def build_candidate(
    base_logit: np.ndarray,
    risk_logit: np.ndarray,
    counter_logit: np.ndarray,
    risk_weight: float,
    counter_weight: float,
    risk_mask: np.ndarray,
    counter_mask: np.ndarray,
    max_step: float,
) -> np.ndarray:
    risk_step = (risk_logit - base_logit) * risk_mask
    counter_step = (counter_logit - base_logit) * counter_mask
    step = risk_weight * risk_step + counter_weight * counter_step
    return clip(sigmoid(base_logit + np.clip(step, -max_step, max_step)))


def generate_candidates(
    bases: list[str],
    risk_files: list[str],
    counter_files: list[str],
    arrays: dict[str, np.ndarray],
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        base_pred = arrays[base_file]
        for risk_file in risk_files:
            risk_logit = logits[risk_file]
            if np.abs(sigmoid(risk_logit) - base_pred).mean() <= 1e-9:
                continue
            for counter_file in counter_files:
                if counter_file == risk_file:
                    continue
                counter_logit = logits[counter_file]
                if np.abs(sigmoid(counter_logit) - base_pred).mean() <= 1e-9:
                    continue
                for profile_name, risk_mask, counter_mask in profile_masks():
                    for max_step in MAX_STEPS:
                        for risk_weight in RISK_WEIGHTS:
                            for counter_weight in COUNTER_WEIGHTS:
                                pred = build_candidate(
                                    base_logit,
                                    risk_logit,
                                    counter_logit,
                                    risk_weight,
                                    counter_weight,
                                    risk_mask,
                                    counter_mask,
                                    max_step,
                                )
                                mean_move = float(np.abs(pred - base_pred).mean())
                                if mean_move < 1e-8:
                                    continue
                                pred_hash = prediction_hash(pred)
                                if pred_hash in seen:
                                    continue
                                seen.add(pred_hash)
                                row: dict[str, object] = {
                                    "label": (
                                        f"{base_file}|risk={risk_file}|counter={counter_file}|{profile_name}|"
                                        f"rw={risk_weight:.2f}|cw={counter_weight:.2f}|cap={max_step:.2f}"
                                    ),
                                    "prediction_hash": pred_hash,
                                    "base_file": base_file,
                                    "risk_file": risk_file,
                                    "counter_file": counter_file,
                                    "profile": profile_name,
                                    "risk_weight": float(risk_weight),
                                    "counter_weight": float(counter_weight),
                                    "max_step": float(max_step),
                                    "mean_abs_move_vs_base": mean_move,
                                    "mean_signed_delta_q3": float((pred[:, TARGETS.index("Q3")] - base_pred[:, TARGETS.index("Q3")]).mean()),
                                    "mean_signed_delta_s4": float((pred[:, TARGETS.index("S4")] - base_pred[:, TARGETS.index("S4")]).mean()),
                                }
                                row.update(public_axis_features(pred, axes))
                                rows.append(row)
                                preds.append(pred)

    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["raw_abs"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 160.0
        + np.maximum(frame["raw_abs"] - 2.5e-6, 0.0) * 40.0
        + np.maximum(frame["bad_abs"] - 0.0012, 0.0) * 0.055
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0026, 0.0) * 0.030
        + np.maximum(frame["mean_abs_move_vs_base"] - 0.0012, 0.0) * 0.020
    )
    specs = [
        (
            (frame["raw_abs"] <= 2.5e-7)
            & (frame["bad_abs"] <= 0.00085)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.0014)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57696),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["raw_abs"] <= 1.5e-6)
            & (frame["bad_abs"] <= 0.0018),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["raw_abs"] <= 6.0e-6)
            & (frame["bad_abs"] <= 0.0045)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57690),
            ["posterior_expected_public_vs_anchor", "raw_abs"],
            900,
        ),
        (
            frame["profile"].astype(str).str.contains("counter_noq2|counter_sblock", regex=True),
            ["prefilter_score"],
            700,
        ),
    ]
    parts = [frame[mask].sort_values(cols).head(limit) for mask, cols, limit in specs if not frame[mask].empty]
    parts.append(frame.sort_values("prefilter_score").head(1500))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(4200)


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
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.2e-7, 0.0) * 280.0
        + np.maximum(scored["raw_abs"] - 8.0e-7, 0.0) * 55.0
        + np.maximum(scored["bad_abs"] - 0.0010, 0.0) * 0.060
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 0.75
        + np.maximum(scored["mean_abs_move_vs_base"] - 0.0010, 0.0) * 0.020
    )
    scored["rank_score"] = (
        0.42 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.22 * scored["raw_abs"].rank(method="min")
        + 0.18 * scored["bad_abs"].rank(method="min")
        + 0.18 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "axisbridge_strict_actual",
            (scored["actual_anchor_score_final"] <= 0.577835)
            & (scored["raw_abs"] <= 3.0e-7)
            & (scored["bad_abs"] <= 0.0010),
            ["actual_anchor_score_final", "selection_score"],
            18,
        ),
        (
            "axisbridge_rawnegative",
            (scored["actual_anchor_score_final"] <= 0.577830)
            & (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_abs"] <= 0.0018),
            ["actual_anchor_score_final", "bad_abs"],
            18,
        ),
        (
            "axisbridge_budgetprobe",
            (scored["actual_anchor_score_final"] <= 0.577805)
            & (scored["raw_abs"] <= 6.0e-6)
            & (scored["bad_abs"] <= 0.0045),
            ["actual_anchor_score_final", "raw_abs"],
            18,
        ),
        (
            "axisbridge_lowbad",
            (scored["raw_abs"] <= 1.2e-6)
            & (scored["bad_abs"] <= 0.00045),
            ["selection_score", "actual_anchor_score_final"],
            18,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "selection_score"]).head(28).assign(bucket="axisbridge_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "actual_anchor_score_final"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_axisbridge_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "base_file",
        "risk_file",
        "counter_file",
        "profile",
        "risk_weight",
        "counter_weight",
        "max_step",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_base",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "rank_score",
    ]
    profile_summary = (
        scored.groupby("profile", as_index=False)
        .agg(
            n=("label", "size"),
            best_actual=("actual_anchor_score_final", "min"),
            best_selection=("selection_score", "min"),
            best_raw_abs=("raw_abs", "min"),
            best_bad_abs=("bad_abs", "min"),
        )
        .sort_values(["best_selection", "best_actual"])
    )
    lines = [
        "# Raw05 JEPA Axis-Budget Motif Bridge",
        "",
        "Bridges high-actual public6 Q3/S4 target moves with raw-axis-negative motif/cellgate counter moves on top of raw05-compatible A-family bases. This is a nonlocal JEPA residual test: keep the context/public axes stable while importing a target-block motif direction.",
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
        profile_summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Shortlist",
        "",
        "```csv",
        selected[cols].head(50).round(10).to_csv(index=False).strip(),
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
    bases, risk_files, counter_files = candidate_pools()
    files = unique_existing([RAW05_FILE, *bases, *risk_files, *counter_files])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}

    if not bases or not risk_files or not counter_files:
        raise RuntimeError(f"empty pool: bases={len(bases)} risk={len(risk_files)} counter={len(counter_files)}")

    scan, preds = generate_candidates(bases, risk_files, counter_files, arrays, axes)
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
        "profile",
        "risk_weight",
        "counter_weight",
        "max_step",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_base",
        "selection_score",
    ]
    print(f"pools bases={len(bases)} risk={len(risk_files)} counter={len(counter_files)}")
    print(f"generated={len(scan)} scored={len(scored)} saved={len(shortlist)}")
    print(shortlist[cols].head(30).round(10).to_string(index=False))
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
