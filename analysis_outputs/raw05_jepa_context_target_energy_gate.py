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
from raw05_jepa_q3stress_counterweight_local_refine import (  # noqa: E402
    choose_refine_pool,
    target_profiles,
)


OUT_SCAN = OUT / "raw05_jepa_context_target_energy_gate_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_context_target_energy_gate_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_context_target_energy_gate_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_context_target_energy_gate_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_context_target_energy_gate_report.md"
OUT_MODEL_DIAG = OUT / "raw05_jepa_context_target_energy_gate_model_diag.csv"

TARGET_INDEX = {target: i for i, target in enumerate(TARGETS)}
CONTEXT_TARGETS = ["Q1", "Q2", "S1", "S2", "S3"]
TARGET_BLOCK = ["Q3", "S4"]
CONTEXT_IDX = np.asarray([TARGET_INDEX[target] for target in CONTEXT_TARGETS], dtype=int)
TARGET_IDX = np.asarray([TARGET_INDEX[target] for target in TARGET_BLOCK], dtype=int)

ALPHAS = [0.52, 0.56, 0.58, 0.60, 0.62, 0.64, 0.68]
PROFILE_KEEP = {
    "nonq3_s4tiny",
    "nonq3s4_flat",
    "nonq3s4_q1light",
    "nonq3s4_q2light",
    "nonq3s4_q2s1heavy",
}
GATE_MODES = ["hard_improve", "soft", "soft_floor"]


def file_exists(file_name: str) -> bool:
    try:
        read_submission(file_name)
    except FileNotFoundError:
        return False
    return True


def unique_existing(files: list[str]) -> list[str]:
    keep: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if file_name in seen or not file_exists(file_name):
            continue
        seen.add(file_name)
        keep.append(file_name)
    return keep


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    ref_key = sample[KEY].reset_index(drop=True)
    arrays: dict[str, np.ndarray] = {}
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def training_pool_files() -> list[str]:
    files: list[str] = [RAW05_FILE]
    sources = [
        ("final_jepa_candidate_priority_20260527.csv", 12, None),
        ("raw05_jepa_q3stress_counterweight_local_shortlist.csv", 72, "actual_anchor_score_final"),
        ("raw05_jepa_target_weight_optimizer_shortlist.csv", 72, "actual_anchor_score_final"),
        ("raw05_jepa_q3stress_counterweight_shortlist.csv", 48, "actual_anchor_score_final"),
        ("jepa_energy_ensemble_shortlist.csv", 36, "focused_scenario_score"),
    ]
    for table_name, limit, sort_col in sources:
        path = OUT / table_name
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "file" not in frame.columns:
            continue
        if sort_col and sort_col in frame.columns:
            frame = frame.sort_values(sort_col)
        files.extend(frame["file"].astype(str).head(limit).tolist())
    return unique_existing(files)


def fit_context_target_energy(arrays: dict[str, np.ndarray], raw: np.ndarray) -> dict[str, np.ndarray | float]:
    raw_logit = logit(raw)
    x_parts = []
    y_parts = []
    for file_name, arr in arrays.items():
        if file_name == RAW05_FILE:
            continue
        delta = logit(arr) - raw_logit
        x_parts.append(delta[:, CONTEXT_IDX])
        y_parts.append(delta[:, TARGET_IDX])
    if not x_parts:
        raise ValueError("empty context-target training pool")

    x = np.vstack(x_parts)
    y = np.vstack(y_parts)
    x_mu = x.mean(axis=0)
    x_sd = x.std(axis=0) + 1e-6
    y_mu = y.mean(axis=0)
    xs = (x - x_mu) / x_sd
    yc = y - y_mu
    reg = np.eye(xs.shape[1], dtype=np.float64) * 0.75
    coef = np.linalg.solve(xs.T @ xs + reg, xs.T @ yc)
    pred = xs @ coef + y_mu
    resid = y - pred
    resid_sd = resid.std(axis=0) + 1e-6
    row_energy = ((resid / resid_sd) ** 2).mean(axis=1)

    diag = pd.DataFrame(
        {
            "n_examples": [len(x)],
            "n_files": [len(arrays) - 1],
            "context": ["+".join(CONTEXT_TARGETS)],
            "target_block": ["+".join(TARGET_BLOCK)],
            "train_energy_mean": [float(row_energy.mean())],
            "train_energy_median": [float(np.median(row_energy))],
            "train_energy_p90": [float(np.quantile(row_energy, 0.90))],
            "train_energy_p99": [float(np.quantile(row_energy, 0.99))],
            "resid_sd_Q3": [float(resid_sd[0])],
            "resid_sd_S4": [float(resid_sd[1])],
        }
    )
    OUT_MODEL_DIAG.write_text(diag.to_csv(index=False), encoding="utf-8")
    return {
        "x_mu": x_mu,
        "x_sd": x_sd,
        "y_mu": y_mu,
        "coef": coef,
        "resid_sd": resid_sd,
        "gate_scale": float(max(np.median(row_energy), 0.05)),
        "train_energy_mean": float(row_energy.mean()),
        "train_energy_p90": float(np.quantile(row_energy, 0.90)),
    }


def energy_rows(delta: np.ndarray, model: dict[str, np.ndarray | float]) -> np.ndarray:
    x = delta[:, CONTEXT_IDX]
    y = delta[:, TARGET_IDX]
    xs = (x - np.asarray(model["x_mu"], dtype=np.float64)) / np.asarray(model["x_sd"], dtype=np.float64)
    pred = xs @ np.asarray(model["coef"], dtype=np.float64) + np.asarray(model["y_mu"], dtype=np.float64)
    resid = (y - pred) / np.asarray(model["resid_sd"], dtype=np.float64)
    return (resid**2).mean(axis=1)


def row_gate(e_base: np.ndarray, e_prop: np.ndarray, mode: str) -> np.ndarray:
    diff = e_base - e_prop
    if mode == "hard_improve":
        return (diff > 0.0).astype(np.float64)
    scale = max(float(np.median(np.abs(diff))), 0.03)
    soft = 1.0 / (1.0 + np.exp(-np.clip(diff / scale, -40.0, 40.0)))
    if mode == "soft":
        return soft
    if mode == "soft_floor":
        return 0.20 + 0.80 * soft
    raise ValueError(mode)


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


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
    row = {"label": label, "prediction_hash": pred_hash}
    row.update(meta)
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate_candidates(
    bases: list[str],
    counters: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    raw_logit = logit(raw)
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    profiles = [(name, vec) for name, vec in target_profiles() if name in PROFILE_KEEP]
    base_energy_cache = {
        file_name: energy_rows(logits[file_name] - raw_logit, model)
        for file_name in bases
        if file_name in logits
    }
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        e_base = base_energy_cache[base_file]
        for counter_file in counters:
            if counter_file == base_file:
                continue
            step0 = logits[counter_file] - base_logit
            for profile_name, profile_gate in profiles:
                step = step0 * profile_gate
                if np.abs(step).mean() <= 1e-10:
                    continue
                for alpha in ALPHAS:
                    prop_logit = base_logit + alpha * step
                    e_prop = energy_rows(prop_logit - raw_logit, model)
                    for mode in GATE_MODES:
                        gate = row_gate(e_base, e_prop, mode)
                        if float(gate.mean()) <= 0.03:
                            continue
                        final_logit = base_logit + alpha * step * gate.reshape(-1, 1)
                        pred = sigmoid(final_logit)
                        final_energy = energy_rows(final_logit - raw_logit, model)
                        label = (
                            f"{base_file}|counter={counter_file}|profile={profile_name}|"
                            f"a={alpha:.2f}|egate={mode}"
                        )
                        meta = {
                            "base_file": base_file,
                            "counter_file": counter_file,
                            "profile": profile_name,
                            "alpha": float(alpha),
                            "energy_gate": mode,
                            "energy_gate_mean": float(gate.mean()),
                            "energy_improve_rate": float((e_prop < e_base).mean()),
                            "base_energy_mean": float(e_base.mean()),
                            "full_step_energy_mean": float(e_prop.mean()),
                            "final_energy_mean": float(final_energy.mean()),
                            "energy_delta_vs_base": float(final_energy.mean() - e_base.mean()),
                            "energy_delta_vs_full": float(final_energy.mean() - e_prop.mean()),
                        }
                        add_candidate(rows, preds, seen, label, pred, axes, meta)
    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 240.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.00175, 0.0) * 0.050
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00158, 0.0) * 0.035
        + np.maximum(frame["energy_delta_vs_base"], 0.0) * 0.00030
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.6e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00185)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            1000,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00180)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00185)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            800,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.00135)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57693),
            ["bad_residual_axis_ratio", "prefilter_score"],
            500,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.576895)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00175),
            ["posterior_expected_public_vs_anchor", "prefilter_score"],
            500,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(600))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(2400)


def score_candidates(selected_for_scoring: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00170, 0.0) * 0.055
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.75
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00025
    )
    scored["energy_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.2e-7, 0.0) * 180.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00185, 0.0) * 0.040
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00060
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00125, 0.0) * 0.070
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "actual_probe",
            (scored["delta_vs_raw05_rawaxis"] <= 1.6e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00185)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["actual_anchor_score_final", "selection_score"],
            24,
        ),
        (
            "raw_boundary",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00180)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["actual_anchor_score_final", "selection_score"],
            24,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00190)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["actual_anchor_score_final", "selection_score"],
            22,
        ),
        (
            "energy_improved",
            (scored["energy_delta_vs_base"] <= 0.0)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00185),
            ["energy_score", "actual_anchor_score_final"],
            22,
        ),
        (
            "very_low_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00125)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57693),
            ["lowbad_score", "actual_anchor_score_final"],
            16,
        ),
        (
            "posterior",
            (scored["posterior_expected_public_vs_anchor"] <= 0.576895)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00175),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            14,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["selection_score", "actual_anchor_score_final"]).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_ctxenergy_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(
    scan: pd.DataFrame,
    scored: pd.DataFrame,
    selected: pd.DataFrame,
    integ: pd.DataFrame,
    model: dict[str, np.ndarray | float],
) -> None:
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "profile",
        "alpha",
        "energy_gate",
        "energy_gate_mean",
        "energy_delta_vs_base",
        "base_file",
        "counter_file",
    ]
    best_by_gate = (
        scored.sort_values("actual_anchor_score_final")
        .groupby(["profile", "alpha", "energy_gate"], as_index=False)
        .head(1)
        .sort_values("actual_anchor_score_final")
    )
    lines = [
        "# Raw05 JEPA Context-Target Energy Gate",
        "",
        "This pass applies the I-JEPA idea more literally: non-Q3/S1/S2/S3/Q1 predictions are the context block, Q3/S4 is the target block, and a learned context-to-target compatibility energy decides how much counterweight to apply per row.",
        "",
        "## Model",
        "",
        f"- context targets: {'+'.join(CONTEXT_TARGETS)}",
        f"- target block: {'+'.join(TARGET_BLOCK)}",
        f"- train energy mean: {float(model['train_energy_mean']):.6f}",
        f"- train energy p90: {float(model['train_energy_p90']):.6f}",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor rescored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Profile / Alpha / Energy Gate",
        "",
        "```csv",
        best_by_gate[
            [
                "profile",
                "alpha",
                "energy_gate",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "energy_delta_vs_base",
                "base_file",
                "counter_file",
            ]
        ]
        .head(40)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(40).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    bases, counters = choose_refine_pool()
    train_files = training_pool_files()
    files = unique_existing([RAW05_FILE, *bases, *counters, *train_files])
    arrays = load_arrays(files, sample)
    axes = public_axes()
    model = fit_context_target_energy({name: arrays[name] for name in train_files if name in arrays}, raw)

    rows, preds = generate_candidates(bases, counters, arrays, raw, model, axes)
    scan = pd.DataFrame(rows)
    scan.to_csv(OUT_SCAN, index=False)

    selected_for_scoring = prefilter(scan)
    scored = score_candidates(selected_for_scoring, preds, sample)
    scored.to_csv(OUT_SCORED, index=False)

    selected = select_and_save(scored, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ, model)

    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "profile",
        "alpha",
        "energy_gate",
        "energy_delta_vs_base",
        "base_file",
        "counter_file",
    ]
    print(
        f"train_files={len(train_files)} bases={len(bases)} counters={len(counters)} "
        f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}"
    )
    print(selected[cols].head(30).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
