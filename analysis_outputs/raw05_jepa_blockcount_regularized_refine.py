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
    read_submission,
    save_submission,
)


OUT_SCAN = OUT / "raw05_jepa_blockcount_regularized_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_blockcount_regularized_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_blockcount_regularized_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_blockcount_regularized_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_blockcount_regularized_refine_report.md"

STRENGTHS = [-0.18, -0.10, -0.05, 0.04, 0.08, 0.14, 0.22]
MODES = ["add_count", "center_add", "pull_count", "anti_count"]


def exists(file_name: str) -> bool:
    return (OUT / file_name).exists() or (ROOT / "jepa" / file_name).exists() or Path(file_name).exists()


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


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def read_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def top_files(frame: pd.DataFrame, sort_cols: list[str], n: int, mask: pd.Series | None = None) -> list[str]:
    if frame.empty or "file" not in frame.columns:
        return []
    part = frame[mask] if mask is not None else frame
    if part.empty:
        return []
    cols = [col for col in sort_cols if col in part.columns]
    if cols:
        part = part.sort_values(cols)
    return part["file"].astype(str).head(n).tolist()


def candidate_pools() -> tuple[list[str], list[str]]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    block = pd.read_csv(OUT / "jepa_block_count_shift_actual_anchor_augmented.csv")
    local = pd.read_csv(OUT / "local_lb_proxy_validation_candidate_predictions.csv")
    sigreg = pd.read_csv(OUT / "lejepa_sigreg_candidate_audit.csv")

    bases: list[str] = []
    bases.extend(
        priority[
            priority["tier"].astype(str).str.startswith("A")
            & priority["file"].astype(str).str.startswith("submission_raw05_jepa_")
            & ~priority["file"].astype(str).str.contains("public6q3s4corr", na=False)
        ]["file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    for family in ["raw05_jepa_efmicro", "raw05_jepa_siganchor", "raw05_jepa_siggate", "raw05_jepa_efgate"]:
        bases.extend(
            top_files(
                sigreg,
                ["lejepa_combined_rank", "actual_anchor_score_final"],
                8,
                sigreg["family"].astype(str).eq(family) if "family" in sigreg.columns else None,
            )
        )

    block_files: list[str] = []
    block_files.extend(top_files(block, ["ranker_selection_score", "actual_anchor_score_final"], 16))
    block_files.extend(top_files(block, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 10))
    block_files.extend(top_files(block, ["delta_vs_raw05_rawaxis", "actual_anchor_score_final"], 10))
    local_block = local[local["file"].astype(str).str.contains("jepa_block_countshift", na=False)].copy()
    block_files.extend(top_files(local_block, ["available_raw05_relative_lb_proxy_mean"], 12))
    sig_block = sigreg[sigreg["file"].astype(str).str.contains("jepa_block_countshift", na=False)].copy()
    block_files.extend(top_files(sig_block, ["lejepa_residual_health", "actual_anchor_score_final"], 10))

    return unique_existing(bases, 24), unique_existing(block_files, 24)


def target_profiles() -> list[tuple[str, np.ndarray]]:
    def profile(**weights: float) -> np.ndarray:
        vals = np.zeros(len(TARGETS), dtype=np.float64)
        for target, weight in weights.items():
            vals[TARGETS.index(target)] = float(weight)
        return vals.reshape(1, -1)

    return [
        ("q3_only", profile(Q3=1.0)),
        ("q3_s4_tiny", profile(Q3=1.0, S4=0.20)),
        ("q3_sblock_tiny", profile(Q3=1.0, S1=0.08, S2=0.08, S3=0.08, S4=0.20)),
    ]


def gate_matrix(name: str, base_delta: np.ndarray, count_delta: np.ndarray) -> np.ndarray:
    if name == "all":
        return np.ones_like(count_delta)
    same = np.sign(base_delta) == np.sign(count_delta)
    nonzero = np.abs(count_delta) > 1e-9
    if name == "agree_floor25":
        return np.where(same & nonzero, 1.0, 0.25)
    if name == "disagree_floor20":
        return np.where((~same) & nonzero, 1.0, 0.20)
    if name == "strong_count_q60":
        gate = np.zeros_like(count_delta) + 0.20
        for j in range(count_delta.shape[1]):
            vals = np.abs(count_delta[:, j])
            if np.max(vals) <= 1e-12:
                continue
            threshold = float(np.quantile(vals, 0.60))
            gate[:, j] = np.where(vals >= threshold, 1.0, 0.20)
        return gate
    if name == "agree_strong_q60":
        strong = gate_matrix("strong_count_q60", base_delta, count_delta)
        agree = gate_matrix("agree_floor25", base_delta, count_delta)
        return np.minimum(strong, agree)
    raise ValueError(f"unknown gate: {name}")


def make_candidate(
    mode: str,
    raw_logit: np.ndarray,
    base_logit: np.ndarray,
    count_logit: np.ndarray,
    strength: float,
    profile: np.ndarray,
    gate: np.ndarray,
) -> np.ndarray:
    base_delta = base_logit - raw_logit
    count_delta = count_logit - raw_logit
    centered_count = count_delta - count_delta.mean(axis=0, keepdims=True)
    if mode == "add_count":
        step = count_delta
    elif mode == "center_add":
        step = centered_count
    elif mode == "anti_count":
        step = -centered_count
    elif mode == "pull_count":
        step = count_logit - base_logit
    else:
        raise ValueError(mode)
    proposed = base_logit + strength * step * profile * gate
    if mode == "pull_count":
        proposed = base_logit + abs(strength) * step * profile * gate
    # Keep the search in the raw05-compatible neighborhood.
    max_step = 0.16 if mode in {"add_count", "center_add", "anti_count"} else 0.10
    return clip(sigmoid(base_logit + np.clip(proposed - base_logit, -max_step, max_step)))


def generate_candidates(
    bases: list[str],
    block_files: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    raw_logit = logit(raw)
    logits = {file_name: logit(arr) for file_name, arr in arrays.items()}
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        base_delta = base_logit - raw_logit
        for block_file in block_files:
            count_logit = logits[block_file]
            count_delta = count_logit - raw_logit
            if np.abs(count_delta).mean() <= 1e-10:
                continue
            for profile_name, profile in target_profiles():
                for gate_name in ["all", "agree_floor25", "disagree_floor20", "strong_count_q60", "agree_strong_q60"]:
                    gate = gate_matrix(gate_name, base_delta, count_delta)
                    for mode in MODES:
                        for strength in STRENGTHS:
                            if mode == "pull_count" and strength < 0:
                                continue
                            pred = make_candidate(mode, raw_logit, base_logit, count_logit, strength, profile, gate)
                            mean_move_vs_base = float(np.abs(pred - sigmoid(base_logit)).mean())
                            if mean_move_vs_base < 1e-8:
                                continue
                            pred_hash = prediction_hash(pred)
                            if pred_hash in seen:
                                continue
                            seen.add(pred_hash)
                            label = "|".join([base_file, block_file, mode, profile_name, gate_name, f"{strength:.3f}"])
                            row: dict[str, object] = {
                                "label": label,
                                "prediction_hash": pred_hash,
                                "base_file": base_file,
                                "block_file": block_file,
                                "mode": mode,
                                "profile": profile_name,
                                "gate": gate_name,
                                "strength": strength,
                                "mean_abs_move_vs_base": mean_move_vs_base,
                            }
                            row.update(public_axis_features(pred, axes))
                            rows.append(row)
                            preds.append(pred)
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.10e-7, 0.0) * 260.0
        + np.maximum(frame["bad_abs"] - 0.00062, 0.0) * 0.075
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0022, 0.0) * 0.035
        + np.maximum(frame["mean_abs_move_vs_base"] - 0.00055, 0.0) * 0.025
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.05e-7)
            & (frame["bad_abs"] <= 0.00055)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57691),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.00070)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57693),
            ["prefilter_score"],
            700,
        ),
        (
            (frame["mode"].isin(["center_add", "anti_count"]))
            & (frame["bad_abs"] <= 0.00050)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7),
            ["prefilter_score"],
            650,
        ),
        (
            (frame["mode"].eq("pull_count"))
            & (frame["bad_abs"] <= 0.00038)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.10e-7),
            ["prefilter_score"],
            500,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(1100))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(2600)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.00e-7, 0.0) * 290.0
        + np.maximum(scored["bad_abs"] - 0.00045, 0.0) * 0.090
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 0.90
        + np.maximum(scored["mean_abs_move_vs_base"] - 0.00045, 0.0) * 0.030
    )
    scored["rank_score"] = (
        0.48 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.22 * scored["bad_abs"].rank(method="min")
        + 0.18 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.12 * scored["delta_vs_raw05_rawaxis"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "blockreg_balanced",
            (scored["actual_anchor_score_final"] <= 0.57783940)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.05e-7)
            & (scored["bad_abs"] <= 0.00050)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.576905),
            ["selection_score", "actual_anchor_score_final"],
            18,
        ),
        (
            "blockreg_lowbad",
            (scored["actual_anchor_score_final"] <= 0.57784000)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.10e-7)
            & (scored["bad_abs"] <= 0.00024),
            ["bad_abs", "actual_anchor_score_final"],
            18,
        ),
        (
            "blockreg_rawnegative",
            (scored["actual_anchor_score_final"] <= 0.57784020)
            & (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_abs"] <= 0.00058),
            ["actual_anchor_score_final", "bad_abs"],
            18,
        ),
        (
            "blockreg_actual",
            (scored["actual_anchor_score_final"] <= 0.57783920)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.20e-7)
            & (scored["bad_abs"] <= 0.00070),
            ["actual_anchor_score_final", "selection_score"],
            18,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "actual_anchor_score_final"]).head(24).assign(bucket="blockreg_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "actual_anchor_score_final"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_blockcountreg_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "base_file",
        "block_file",
        "mode",
        "profile",
        "gate",
        "strength",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_base",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "rank_score",
    ]
    mode_summary = (
        scored.groupby(["mode", "profile"], as_index=False)
        .agg(
            n=("label", "size"),
            best_actual=("actual_anchor_score_final", "min"),
            best_selection=("selection_score", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_raw=("delta_vs_raw05_rawaxis", "min"),
        )
        .sort_values(["best_selection", "best_actual"])
    )
    lines = [
        "# Raw05 JEPA Block-Count Regularized Refine",
        "",
        "Mix raw05-compatible A-family residuals with JEPA block-count residuals. The count direction is tested as a small additive residual, centered hidden-block residual, pull-to-count prior, and sign-flipped control.",
        "",
        "## Counts",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- actual-anchor scored candidates: `{len(scored)}`",
        f"- saved shortlist: `{len(selected)}`",
        "",
        "## Mode Summary",
        "",
        "```csv",
        mode_summary.round(10).to_csv(index=False).strip(),
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
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    axes = public_axes()
    raw = read_array(RAW05_FILE, sample)
    bases, block_files = candidate_pools()
    files = unique_existing([RAW05_FILE, *bases, *block_files])
    arrays = {file_name: read_array(file_name, sample) for file_name in files}

    scan, preds = generate_candidates(bases, block_files, arrays, raw, axes)
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
        "base_file",
        "block_file",
        "mode",
        "profile",
        "gate",
        "strength",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_base",
        "selection_score",
    ]
    print(f"generated={len(scan)} scored={len(scored)} saved={len(shortlist)}")
    print(shortlist[cols].head(30).round(10).to_string(index=False))
    print(f"wrote {OUT_SHORTLIST}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
