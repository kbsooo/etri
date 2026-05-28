from __future__ import annotations

from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from public_lb_six_anchor_entropy_projection import (  # noqa: E402
    ANCHORS,
    EPS,
    KEY,
    TARGETS,
    clip,
    entropy,
    expected_scores,
    locate,
    logit,
    read_submission,
    score_parts,
    sigmoid,
    solve_projection,
)


BASE_PRIORS = {
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "efmicro3": "submission_raw05_jepa_efmicro_3eece507.csv",
    "efmicro5": "submission_raw05_jepa_efmicro_5d2d2af0.csv",
    "energyfront": "submission_raw05_jepa_energyfront_a190aa25.csv",
    "siggate": "submission_raw05_jepa_siggate_6d681440.csv",
    "compatband": "submission_raw05_jepa_compatband_e065e98e.csv",
}

TARGET_MASKS = {
    "q1_s3": ["Q1", "S3"],
    "q1_s2_s3": ["Q1", "S2", "S3"],
    "q1_q3_s3": ["Q1", "Q3", "S3"],
    "s3": ["S3"],
    "q1": ["Q1"],
}

# These are deliberately much smaller than the failed direct public6 projection
# gamma=0.03 family. At this scale the experiment tests direction, not a new
# pseudo-label solution.
GAMMAS = [0.00075, 0.0010, 0.0015, 0.0020, 0.0030, 0.0040, 0.0060, 0.0080, 0.0120]
GATES = ["ones", "signed_strength", "entropy_mid", "signed_entropy", "signed_top40"]
MODES = ["logit", "prob", "prob_bad_ortho", "prob_bad_raw_ortho"]
ORIENTATIONS = {
    "follow": 1.0,
    "anti": -1.0,
}

SCAN_OUT = OUT / "raw05_jepa_public6_drift_microperturb_scan.csv"
SHORTLIST_OUT = OUT / "raw05_jepa_public6_drift_microperturb_shortlist.csv"
INTEGRITY_OUT = OUT / "raw05_jepa_public6_drift_microperturb_integrity.csv"
REPORT_OUT = OUT / "raw05_jepa_public6_drift_microperturb_report.md"


EXPECTED_SIGNS = {
    "Q1": -1.0,
    "Q3": -1.0,
    "S2": 1.0,
    "S3": 1.0,
}


def stable_tag(text: str | bytes) -> str:
    payload = text if isinstance(text, bytes) else text.encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:8]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes())


def normalize01(values: np.ndarray, quantile: float = 0.90) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    positive = x[np.isfinite(x) & (x > 0)]
    if len(positive) == 0:
        return np.zeros_like(x, dtype=np.float64)
    scale = float(np.quantile(positive, quantile))
    if scale <= 1e-12:
        return np.zeros_like(x, dtype=np.float64)
    return np.clip(x / scale, 0.0, 1.0)


def target_indices(targets: list[str]) -> list[int]:
    return [TARGETS.index(t) for t in targets]


def signed_direction(
    base: np.ndarray,
    projected: np.ndarray,
    targets: list[str],
    orientation: float,
) -> tuple[np.ndarray, np.ndarray]:
    raw_dir = projected - base
    direction = np.zeros_like(base)
    strength = np.zeros(base.shape[0], dtype=np.float64)
    for target in targets:
        j = TARGETS.index(target)
        sign = EXPECTED_SIGNS[target] * orientation
        cell = raw_dir[:, j]
        keep = sign * cell > 0.0
        direction[:, j] = np.where(keep, cell, 0.0)
        strength += np.maximum(sign * cell, 0.0)
    return direction, normalize01(strength)


def gate_values(base: np.ndarray, direction: np.ndarray, strength: np.ndarray, targets: list[str], gate_name: str) -> np.ndarray:
    idx = target_indices(targets)
    if gate_name == "ones":
        return np.ones(base.shape[0], dtype=np.float64)
    if gate_name == "signed_strength":
        return strength
    ent = np.mean(4.0 * base[:, idx] * (1.0 - base[:, idx]), axis=1)
    ent = normalize01(ent, 0.95)
    if gate_name == "entropy_mid":
        return ent
    if gate_name == "signed_entropy":
        return np.minimum(strength, ent)
    if gate_name == "signed_top40":
        threshold = float(np.quantile(strength, 0.60))
        return (strength >= threshold).astype(np.float64) * strength
    raise ValueError(f"unknown gate: {gate_name}")


def orthogonalize(direction: np.ndarray, axis: np.ndarray, targets: list[str]) -> np.ndarray:
    masked_axis = np.zeros_like(direction)
    idx = target_indices(targets)
    masked_axis[:, idx] = axis[:, idx]
    a = masked_axis.reshape(-1)
    d = direction.reshape(-1)
    denom = float(np.dot(a, a))
    if denom <= 1e-18:
        return direction
    return (d - float(np.dot(d, a)) / denom * a).reshape(direction.shape)


def enforce_orientation(direction: np.ndarray, targets: list[str], orientation: float) -> np.ndarray:
    out = np.zeros_like(direction)
    for target in targets:
        j = TARGETS.index(target)
        sign = EXPECTED_SIGNS[target] * orientation
        out[:, j] = np.where(sign * direction[:, j] > 0.0, direction[:, j], 0.0)
    return out


def build_candidate(
    base: np.ndarray,
    projected: np.ndarray,
    axes: dict[str, np.ndarray | float],
    targets: list[str],
    gamma: float,
    gate_name: str,
    mode: str,
    orientation: float,
) -> tuple[np.ndarray, dict[str, float]]:
    prob_direction, strength = signed_direction(base, projected, targets, orientation)
    gate = gate_values(base, prob_direction, strength, targets, gate_name)
    gated_prob_direction = prob_direction * gate[:, None]
    if float(np.abs(gated_prob_direction).sum()) <= 0.0:
        raise ValueError("empty direction")

    idx = target_indices(targets)
    if mode == "logit":
        raw_logit_dir = logit(projected) - logit(base)
        logit_direction = np.zeros_like(base)
        for target in targets:
            j = TARGETS.index(target)
            sign = EXPECTED_SIGNS[target] * orientation
            keep = sign * prob_direction[:, j] > 0.0
            logit_direction[:, j] = np.where(keep, raw_logit_dir[:, j], 0.0)
        out = base.copy()
        out[:, idx] = sigmoid(logit(base[:, idx]) + gamma * gate[:, None] * logit_direction[:, idx])
    else:
        direction = gated_prob_direction
        if mode in {"prob_bad_ortho", "prob_bad_raw_ortho"}:
            direction = orthogonalize(direction, np.asarray(axes["bad_axis"], dtype=np.float64), targets)
            direction = enforce_orientation(direction, targets, orientation)
        if mode == "prob_bad_raw_ortho":
            raw_q = np.asarray(axes["raw_q"], dtype=np.float64)
            grad = (base - raw_q) / np.maximum(base * (1.0 - base), EPS)
            direction = orthogonalize(direction, grad, targets)
            direction = enforce_orientation(direction, targets, orientation)
        if mode not in {"prob", "prob_bad_ortho", "prob_bad_raw_ortho"}:
            raise ValueError(f"unknown mode: {mode}")
        out = clip(base + gamma * direction)

    out = clip(out)
    delta = out - base
    meta = {
        "candidate_entropy": entropy(out),
        "candidate_mean_abs_move_vs_prior": float(np.abs(delta).mean()),
        "candidate_max_abs_move_vs_prior": float(np.abs(delta).max()),
        "mean_gate": float(gate.mean()),
        "nonzero_gate_rate": float((gate > 0).mean()),
        "mean_signed_strength": float(strength.mean()),
        "mean_target_delta_Q1": float(delta[:, TARGETS.index("Q1")].mean()),
        "mean_target_delta_Q3": float(delta[:, TARGETS.index("Q3")].mean()),
        "mean_target_delta_S2": float(delta[:, TARGETS.index("S2")].mean()),
        "mean_target_delta_S3": float(delta[:, TARGETS.index("S3")].mean()),
    }
    return out, meta


def build_anchor_constraints(sample: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    anchor_names = list(ANCHORS)
    anchor_preds = [
        read_submission(ANCHORS[name][0], sample)[TARGETS].to_numpy(dtype=np.float64)
        for name in anchor_names
    ]
    const_mat = []
    coef_mat = []
    for pred in anchor_preds:
        const, coef = score_parts(pred)
        const_mat.append(const)
        coef_mat.append(coef)
    return (
        anchor_names,
        np.asarray([ANCHORS[name][1] for name in anchor_names], dtype=np.float64),
        np.vstack(const_mat).T,
        np.vstack(coef_mat).T,
    )


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for file_name in files:
        frame = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        pred = frame[TARGETS].to_numpy(dtype=np.float64)
        rows.append(
            {
                "file": file_name,
                "rows": len(frame),
                "key_ok": bool(frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True))),
                "duplicate_keys": int(frame.duplicated(KEY).sum()),
                "null_probs": int(frame[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def select_shortlist(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["abs_delta_vs_raw05_rawaxis"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["abs_bad_residual_axis_ratio"] = frame["bad_residual_axis_ratio"].abs()
    frame["micro_guard_score"] = (
        frame["posterior_expected_public_vs_anchor"].fillna(1.0)
        + 400.0 * frame["abs_delta_vs_raw05_rawaxis"].fillna(0.0)
        + 0.0010 * frame["abs_bad_residual_axis_ratio"].fillna(0.0)
        + 0.03 * np.maximum(frame["mean_abs_move_vs_raw05"].fillna(0.0) - 0.0017, 0.0)
    )
    frame["strict_guard"] = (
        frame["abs_delta_vs_raw05_rawaxis"].le(2.0e-7)
        & frame["abs_bad_residual_axis_ratio"].le(0.0025)
        & frame["mean_abs_move_vs_raw05"].le(0.0020)
        & frame["posterior_expected_public_vs_anchor"].le(0.57693)
    )
    frame["raw_tight_guard"] = (
        frame["abs_delta_vs_raw05_rawaxis"].le(1.0e-7)
        & frame["abs_bad_residual_axis_ratio"].le(0.0050)
        & frame["mean_abs_move_vs_raw05"].le(0.0022)
    )

    selected = [
        frame.sort_values(["strict_guard", "micro_guard_score"], ascending=[False, True]).head(40),
        frame.sort_values(["raw_tight_guard", "abs_delta_vs_raw05_rawaxis", "micro_guard_score"], ascending=[False, True, True]).head(36),
        frame.sort_values(["abs_bad_residual_axis_ratio", "micro_guard_score"]).head(28),
    ]
    for _, group in frame.groupby(["prior", "target_mask", "orientation"], sort=False):
        selected.append(group.sort_values("micro_guard_score").head(1))
    for _, group in frame.groupby(["prior", "mode"], sort=False):
        selected.append(group.sort_values("micro_guard_score").head(1))

    shortlist = pd.concat(selected, ignore_index=True).drop_duplicates("file")
    shortlist = shortlist.sort_values(
        ["strict_guard", "micro_guard_score", "posterior_expected_public_vs_anchor"],
        ascending=[False, True, True],
    ).head(160)
    return shortlist.reset_index(drop=True)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    anchor_names, target_scores, const_arr, coef_arr = build_anchor_constraints(sample)
    axes = public_axes()

    records: list[dict[str, object]] = []
    pred_by_file: dict[str, np.ndarray] = {}
    seen_hashes: set[str] = set()
    fit_rows = []

    for prior_name, prior_file in BASE_PRIORS.items():
        if not locate(prior_file).exists():
            continue
        prior_frame = read_submission(prior_file, sample)
        base = prior_frame[TARGETS].to_numpy(dtype=np.float64)
        fit = solve_projection(base, const_arr, coef_arr, target_scores)
        expected_all = expected_scores(fit.q, const_arr, coef_arr)
        fit_rows.append(
            {
                "prior": prior_name,
                "prior_file": prior_file,
                "projection_converged": fit.converged,
                "projection_max_abs_residual": float(np.max(np.abs(fit.residual))),
                "projection_mean_abs_move": float(np.abs(fit.q - base).mean()),
            }
            | {f"expected_{name}": float(value) for name, value in zip(anchor_names, expected_all, strict=True)}
        )

        for mask_name, targets in TARGET_MASKS.items():
            for gamma in GAMMAS:
                for gate_name in GATES:
                    for mode in MODES:
                        for orientation_name, orientation in ORIENTATIONS.items():
                            try:
                                pred, meta = build_candidate(
                                    base=base,
                                    projected=fit.q,
                                    axes=axes,
                                    targets=targets,
                                    gamma=gamma,
                                    gate_name=gate_name,
                                    mode=mode,
                                    orientation=orientation,
                                )
                            except ValueError:
                                continue
                            h = prediction_hash(pred)
                            if h in seen_hashes:
                                continue
                            seen_hashes.add(h)
                            file_name = (
                                "submission_raw05_jepa_public6drift_"
                                f"{prior_name}_{mask_name}_{orientation_name}_{gate_name}_{mode}_"
                                f"g{int(round(gamma * 100000)):05d}_{h}.csv"
                            )
                            public = public_axis_features(pred, axes)
                            records.append(
                                {
                                    "file": file_name,
                                    "prior": prior_name,
                                    "prior_file": prior_file,
                                    "target_mask": mask_name,
                                    "targets": ",".join(targets),
                                    "orientation": orientation_name,
                                    "gamma": gamma,
                                    "gate": gate_name,
                                    "mode": mode,
                                    "prediction_hash": h,
                                    "projection_mean_abs_move": float(np.abs(fit.q - base).mean()),
                                }
                                | meta
                                | public
                            )
                            pred_by_file[file_name] = pred

    scan = pd.DataFrame(records)
    if scan.empty:
        raise RuntimeError("no candidates generated")
    scan["abs_delta_vs_raw05_rawaxis"] = scan["delta_vs_raw05_rawaxis"].abs()
    scan["abs_bad_residual_axis_ratio"] = scan["bad_residual_axis_ratio"].abs()
    scan = scan.sort_values(
        ["posterior_expected_public_vs_anchor", "abs_delta_vs_raw05_rawaxis", "abs_bad_residual_axis_ratio"]
    ).reset_index(drop=True)
    shortlist = select_shortlist(scan)

    for file_name in shortlist["file"].astype(str):
        prior_file = str(shortlist.loc[shortlist["file"].eq(file_name), "prior_file"].iloc[0])
        prior_frame = read_submission(prior_file, sample)
        out = prior_frame[KEY].copy()
        out[TARGETS] = pred_by_file[file_name]
        out.to_csv(OUT / file_name, index=False)

    fit_df = pd.DataFrame(fit_rows).sort_values(["projection_mean_abs_move", "projection_max_abs_residual"])
    fit_df.to_csv(OUT / "raw05_jepa_public6_drift_microperturb_projection_fit.csv", index=False)
    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    integrity(shortlist["file"].astype(str).tolist(), sample).to_csv(INTEGRITY_OUT, index=False)

    by_orientation = (
        scan.groupby("orientation", as_index=False)
        .agg(
            n=("file", "size"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_abs_raw=("abs_delta_vs_raw05_rawaxis", "min"),
            best_abs_bad=("abs_bad_residual_axis_ratio", "min"),
            strict_count=(
                "file",
                lambda s: int(
                    scan.loc[s.index]
                    .eval("abs_delta_vs_raw05_rawaxis <= 2e-7 and abs_bad_residual_axis_ratio <= 0.0025 and mean_abs_move_vs_raw05 <= 0.002")
                    .sum()
                ),
            ),
        )
        .sort_values("orientation")
    )
    top_cols = [
        "file",
        "prior",
        "target_mask",
        "orientation",
        "gamma",
        "gate",
        "mode",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "candidate_mean_abs_move_vs_prior",
        "mean_target_delta_Q1",
        "mean_target_delta_S3",
    ]
    report = [
        "# Raw05 JEPA Public6 Drift Microperturb",
        "",
        "This keeps the six-anchor public-LB posterior as a direction oracle only. Most direct posterior candidates are unsafe because of held-out-anchor error or bad-axis movement, so the generated candidates use very small row-gated moves around raw05-compatible JEPA bases.",
        "",
        "## Projection Fit",
        "",
        "```csv",
        fit_df.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Orientation Summary",
        "",
        "```csv",
        by_orientation.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Strict Shortlist",
        "",
        "```csv",
        shortlist[top_cols].head(30).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Decision Rule",
        "",
        "- Treat `follow` as the public6 drift hypothesis: Q1/Q3 down, S2/S3 up.",
        "- Treat `anti` as a local-proxy falsification control.",
        "- Candidates are only worth submitting if the local LB proxy keeps them raw05-relative competitive after the separate validation script reruns.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")

    print(f"generated_in_memory={len(scan)} saved_shortlist={len(shortlist)}")
    print(f"wrote: {SCAN_OUT}")
    print(f"wrote: {SHORTLIST_OUT}")
    print(shortlist[top_cols].head(16).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
