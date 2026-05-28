from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

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


OUT_SCAN = OUT / "raw05_jepa_tangent_nullspace_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_tangent_nullspace_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_tangent_nullspace_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_tangent_nullspace_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_tangent_nullspace_refine_report.md"

STEP_WEIGHTS = [-0.28, -0.18, -0.10, -0.055, 0.045, 0.08, 0.13, 0.20, 0.30]
COMP_WEIGHTS = [-0.20, -0.12, -0.06, 0.05, 0.09, 0.15, 0.24]


def exists(file_name: str) -> bool:
    path = Path(file_name)
    return path.exists() or (OUT / file_name).exists() or (JEPA / file_name).exists()


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
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


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


def candidate_pool() -> list[str]:
    priority = read_optional("final_jepa_candidate_priority_20260527.csv")
    sigreg = read_optional("lejepa_sigreg_candidate_audit.csv")
    tables = [
        read_optional("raw05_jepa_energyfront_microrefine_shortlist.csv"),
        read_optional("raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv"),
        read_optional("raw05_jepa_sigreg_gated_microrefine_shortlist.csv"),
        read_optional("raw05_jepa_efmicro_gate_refine_shortlist.csv"),
        read_optional("raw05_jepa_efgate_backoff_frontier_shortlist.csv"),
        read_optional("raw05_jepa_energy_constrained_frontier_shortlist.csv"),
    ]

    files: list[str] = []
    if not priority.empty:
        mask = (
            priority["file"].astype(str).str.startswith("submission_raw05_jepa_")
            & ~priority["file"].astype(str).str.contains("public6q3s4corr|blockcountreg", regex=True, na=False)
            & priority["tier"].astype(str).str.startswith("A")
        )
        files.extend(top_files(priority, ["rank"], 22, mask))
    if not sigreg.empty and "family" in sigreg.columns:
        for family in [
            "raw05_jepa_efmicro",
            "raw05_jepa_siganchor",
            "raw05_jepa_siggate",
            "raw05_jepa_efgate",
            "raw05_jepa_efback",
            "raw05_jepa_energyfront",
        ]:
            fam_mask = sigreg["family"].astype(str).eq(family)
            files.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 8, fam_mask))
            files.extend(top_files(sigreg, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 5, fam_mask))
    for table in tables:
        if table.empty:
            continue
        files.extend(top_files(table, ["actual_anchor_score_final", "bad_residual_axis_ratio"], 10))
        files.extend(top_files(table, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 8))
    files.append(RAW05_FILE)
    return unique_existing(files, 56)


def target_profiles() -> list[tuple[str, np.ndarray]]:
    def make(**weights: float) -> np.ndarray:
        vals = np.ones(len(TARGETS), dtype=np.float64)
        for target, weight in weights.items():
            vals[TARGETS.index(target)] = float(weight)
        return vals.reshape(1, -1)

    return [
        ("all", np.ones((1, len(TARGETS)), dtype=np.float64)),
        ("context_only", make(Q3=0.0, S4=0.0)),
        ("q1light_context", make(Q1=0.42, Q3=0.0, S4=0.0)),
        ("q2s1heavy", make(Q1=0.70, Q2=1.22, Q3=0.05, S1=1.22, S2=0.82, S3=0.82, S4=0.05)),
        ("target_tiny", make(Q1=0.72, Q2=0.90, Q3=0.08, S1=0.90, S2=0.88, S3=0.88, S4=0.08)),
    ]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def flatten(x: np.ndarray) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).reshape(-1)


def tangent_axes(axes: dict[str, np.ndarray | float]) -> np.ndarray:
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    raw05 = np.asarray(axes["raw05"], dtype=np.float64)
    raw_q = np.asarray(axes["raw_q"], dtype=np.float64)
    bad = np.asarray(axes["bad_axis"], dtype=np.float64)
    ordinal = np.asarray(axes["ordinal_axis"], dtype=np.float64)
    stage_axis = stage2 - raw05
    mat = np.vstack([flatten(raw_q), flatten(bad), flatten(ordinal), flatten(stage_axis)])
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(norms, 1e-12)


def null_project_probability_step(dp: np.ndarray, axis_mat: np.ndarray) -> np.ndarray:
    vec = flatten(dp)
    gram = axis_mat @ axis_mat.T
    coeff = np.linalg.pinv(gram + np.eye(gram.shape[0]) * 1e-10) @ (axis_mat @ vec)
    resid = vec - axis_mat.T @ coeff
    return resid.reshape(dp.shape)


def logit_step_from_probability_step(base: np.ndarray, dp: np.ndarray) -> np.ndarray:
    denom = np.maximum(base * (1.0 - base), 2.5e-3)
    return dp / denom


def residual_components(arrays: dict[str, np.ndarray], files: list[str], raw: np.ndarray, n_comp: int = 10) -> list[tuple[str, np.ndarray]]:
    raw_logit = logit(raw)
    residuals = []
    names = []
    for file_name in files:
        if file_name == RAW05_FILE:
            continue
        residuals.append(flatten(logit(arrays[file_name]) - raw_logit))
        names.append(file_name)
    if len(residuals) < 3:
        return []
    mat = np.vstack(residuals)
    mat = mat - mat.mean(axis=0, keepdims=True)
    _, singular, vt = np.linalg.svd(mat, full_matrices=False)
    comps = []
    for i in range(min(n_comp, len(vt))):
        comp = vt[i].reshape(raw.shape)
        scale = float(np.median([np.mean(np.abs(logit(arrays[name]) - raw_logit)) for name in names]))
        comps.append((f"pca{i + 1}_s{singular[i]:.4f}", comp * scale))
    return comps


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
    meta: dict[str, object],
) -> None:
    pred = clip(pred)
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row: dict[str, object] = {"label": label, "prediction_hash": pred_hash}
    row.update(meta)
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def make_pred(
    base_pred: np.ndarray,
    raw_pred: np.ndarray,
    raw_logit: np.ndarray,
    step_logit: np.ndarray,
    weight: float,
    profile: np.ndarray,
    mode: str,
    axis_mat: np.ndarray,
) -> tuple[np.ndarray, float]:
    base_logit = logit(base_pred)
    step = step_logit * profile
    if mode == "null_prob":
        prop = sigmoid(base_logit + weight * step)
        dp = prop - base_pred
        dp_null = null_project_probability_step(dp, axis_mat)
        step = logit_step_from_probability_step(base_pred, dp_null)
    elif mode == "centered":
        step = step - step.mean(axis=0, keepdims=True)
    elif mode == "raw":
        pass
    else:
        raise ValueError(mode)
    max_abs = 0.12 if mode == "null_prob" else 0.10
    final_step = np.clip(weight * step, -max_abs, max_abs)
    pred = sigmoid(base_logit + final_step)
    return clip(pred), float(np.abs(pred - base_pred).mean())


def generate_candidates(
    files: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    raw_logit = logit(raw)
    axis_mat = tangent_axes(axes)

    pca_steps = residual_components(arrays, files, raw, n_comp=10)
    bases = [f for f in files if f != RAW05_FILE][:28]
    donors = [f for f in files if f != RAW05_FILE][:42]
    donor_steps = []
    for donor_file in donors:
        donor_steps.append((f"raw_to_{donor_file}", logit(arrays[donor_file]) - raw_logit, donor_file))

    for base_file in bases:
        base = arrays[base_file]
        base_logit = logit(base)
        for donor_file in donors:
            if donor_file == base_file:
                continue
            step0 = logit(arrays[donor_file]) - base_logit
            for profile_name, profile in target_profiles():
                for mode in ["raw", "centered", "null_prob"]:
                    for weight in STEP_WEIGHTS:
                        pred, move = make_pred(base, raw, raw_logit, step0, weight, profile, mode, axis_mat)
                        if move < 1e-8:
                            continue
                        label = f"pair|base={base_file}|donor={donor_file}|profile={profile_name}|mode={mode}|w={weight:.3f}"
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            label,
                            pred,
                            axes,
                            {
                                "source": "pair",
                                "base_file": base_file,
                                "direction_file": donor_file,
                                "direction_name": donor_file,
                                "profile": profile_name,
                                "mode": mode,
                                "weight": float(weight),
                                "mean_abs_move_vs_base": move,
                            },
                        )

        for direction_name, step0, direction_file in donor_steps + [(name, step, "") for name, step in pca_steps]:
            for profile_name, profile in target_profiles():
                for mode in ["centered", "null_prob"]:
                    for weight in COMP_WEIGHTS:
                        pred, move = make_pred(base, raw, raw_logit, step0, weight, profile, mode, axis_mat)
                        if move < 1e-8:
                            continue
                        label = f"basis|base={base_file}|dir={direction_name}|profile={profile_name}|mode={mode}|w={weight:.3f}"
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            label,
                            pred,
                            axes,
                            {
                                "source": "basis",
                                "base_file": base_file,
                                "direction_file": direction_file,
                                "direction_name": direction_name,
                                "profile": profile_name,
                                "mode": mode,
                                "weight": float(weight),
                                "mean_abs_move_vs_base": move,
                            },
                        )
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.05e-7, 0.0) * 320.0
        + np.maximum(frame["bad_abs"] - 0.00052, 0.0) * 0.090
        + np.maximum(frame["mean_abs_move_vs_base"] - 0.00050, 0.0) * 0.035
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.0021, 0.0) * 0.030
    )
    specs = [
        (
            (frame["actual_anchor_proxy"].notna() if "actual_anchor_proxy" in frame.columns else True)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_abs"] <= 0.00048)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.576905),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["mode"].eq("null_prob"))
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_abs"] <= 0.00055),
            ["prefilter_score"],
            850,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_abs"] <= 0.00075),
            ["prefilter_score"],
            650,
        ),
        (
            (frame["profile"].isin(["context_only", "q1light_context", "target_tiny"]))
            & (frame["bad_abs"] <= 0.00050)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.1e-7),
            ["prefilter_score"],
            700,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(1000))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(2400)


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
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.00e-7, 0.0) * 300.0
        + np.maximum(scored["bad_abs"] - 0.00048, 0.0) * 0.095
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 0.90
        + np.maximum(scored["mean_abs_move_vs_base"] - 0.00045, 0.0) * 0.035
    )
    scored["rank_score"] = (
        0.52 * scored["actual_anchor_score_final"].rank(method="min")
        + 0.18 * scored["bad_abs"].rank(method="min")
        + 0.18 * scored["posterior_expected_public_vs_anchor"].rank(method="min")
        + 0.12 * scored["delta_vs_raw05_rawaxis"].rank(method="min")
    )
    return scored.sort_values(["rank_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "tangent_actual",
            (scored["actual_anchor_score_final"] <= 0.57783915)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.10e-7)
            & (scored["bad_abs"] <= 0.00062),
            ["actual_anchor_score_final", "selection_score"],
            18,
        ),
        (
            "tangent_balanced",
            (scored["actual_anchor_score_final"] <= 0.57783945)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.05e-7)
            & (scored["bad_abs"] <= 0.00050)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.576905),
            ["selection_score", "actual_anchor_score_final"],
            18,
        ),
        (
            "tangent_null_lowbad",
            (scored["mode"].eq("null_prob"))
            & (scored["actual_anchor_score_final"] <= 0.57784000)
            & (scored["bad_abs"] <= 0.00025)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.10e-7),
            ["bad_abs", "actual_anchor_score_final"],
            18,
        ),
        (
            "tangent_rawnegative",
            (scored["actual_anchor_score_final"] <= 0.57784020)
            & (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_abs"] <= 0.00070),
            ["actual_anchor_score_final", "bad_abs"],
            18,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["rank_score", "actual_anchor_score_final"]).head(24).assign(bucket="tangent_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["rank_score", "actual_anchor_score_final"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_tangentnull_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "source",
        "base_file",
        "direction_name",
        "profile",
        "mode",
        "weight",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_base",
        "mean_abs_move_vs_raw05",
        "selection_score",
        "rank_score",
    ]
    summary = (
        scored.groupby(["source", "mode", "profile"], as_index=False)
        .agg(
            n=("label", "size"),
            best_actual=("actual_anchor_score_final", "min"),
            best_selection=("selection_score", "min"),
            best_bad_abs=("bad_abs", "min"),
            best_raw=("delta_vs_raw05_rawaxis", "min"),
        )
        .sort_values(["best_actual", "best_selection"])
    )
    lines = [
        "# Raw05 JEPA Tangent Nullspace Refine",
        "",
        "Explore the local logit-residual tangent space of the raw05-compatible A-family. Probability-space steps are optionally projected away from raw/bad/ordinal public axes before converting back into logit space.",
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
        summary.round(10).to_csv(index=False).strip(),
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
    files = candidate_pool()
    raw = read_array(RAW05_FILE, sample)
    arrays = {file_name: read_array(file_name, sample) for file_name in files}
    if RAW05_FILE not in arrays:
        arrays[RAW05_FILE] = raw

    scan, preds = generate_candidates(files, arrays, raw, axes)
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
        "source",
        "base_file",
        "direction_name",
        "profile",
        "mode",
        "weight",
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
