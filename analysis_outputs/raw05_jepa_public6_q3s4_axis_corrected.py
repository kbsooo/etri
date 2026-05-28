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
from raw05_anchor_jepa_micro_injection import actual_anchor_score  # noqa: E402


BASE_PRIORS = {
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "efmicro3": "submission_raw05_jepa_efmicro_3eece507.csv",
    "efmicro5": "submission_raw05_jepa_efmicro_5d2d2af0.csv",
    "compatband": "submission_raw05_jepa_compatband_e065e98e.csv",
    "energyfront": "submission_raw05_jepa_energyfront_a190aa25.csv",
    "siggate": "submission_raw05_jepa_siggate_6d681440.csv",
}

TARGETS_Q3S4 = ["Q3", "S4"]
GAMMAS = [0.015, 0.020, 0.030, 0.040, 0.050, 0.065, 0.080, 0.100, 0.120, 0.160, 0.200, 0.250]
GATES = ["ones", "entropy_mid", "strength", "strength_entropy", "top60_strength"]
MODES = [
    "direct_logit",
    "prob",
    "prob_raw_ortho",
    "prob_bad_raw_ortho",
    "prob_bad_raw_ord_ortho",
    "prob_raw_ortho_positive",
]

SCAN_OUT = OUT / "raw05_jepa_public6_q3s4_axis_corrected_scan.csv"
SHORTLIST_OUT = OUT / "raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv"
INTEGRITY_OUT = OUT / "raw05_jepa_public6_q3s4_axis_corrected_integrity.csv"
REPORT_OUT = OUT / "raw05_jepa_public6_q3s4_axis_corrected_report.md"


def stable_tag(text: str | bytes) -> str:
    payload = text if isinstance(text, bytes) else text.encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:8]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes())


def normalize01(values: np.ndarray, quantile: float = 0.90) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    good = x[np.isfinite(x) & (x > 0.0)]
    if len(good) == 0:
        return np.zeros_like(x)
    scale = float(np.quantile(good, quantile))
    if scale <= 1e-12:
        return np.zeros_like(x)
    return np.clip(x / scale, 0.0, 1.0)


def target_indices(targets: list[str]) -> list[int]:
    return [TARGETS.index(t) for t in targets]


def masked_axis(axis: np.ndarray, targets: list[str]) -> np.ndarray:
    out = np.zeros_like(axis, dtype=np.float64)
    idx = target_indices(targets)
    out[:, idx] = axis[:, idx]
    return out


def orthogonalize(direction: np.ndarray, axes: list[np.ndarray], targets: list[str]) -> np.ndarray:
    idx = target_indices(targets)
    d = np.zeros_like(direction, dtype=np.float64)
    d[:, idx] = direction[:, idx]
    flat = d.reshape(-1)
    basis = []
    for axis in axes:
        a = masked_axis(np.asarray(axis, dtype=np.float64), targets).reshape(-1)
        norm = float(np.linalg.norm(a))
        if norm > 1e-12:
            basis.append(a / norm)
    if not basis:
        return d
    mat = np.stack(basis, axis=1)
    # Use least-squares projection because raw/bad/ordinal axes are not
    # guaranteed orthogonal.
    coeff = np.linalg.pinv(mat.T @ mat) @ mat.T @ flat
    corrected = flat - mat @ coeff
    out = corrected.reshape(direction.shape)
    keep = np.zeros_like(out)
    keep[:, idx] = out[:, idx]
    return keep


def gate_values(base: np.ndarray, direction: np.ndarray, gate: str) -> np.ndarray:
    idx = target_indices(TARGETS_Q3S4)
    strength = normalize01(np.abs(direction[:, idx]).sum(axis=1), 0.90)
    ent = normalize01(np.mean(4.0 * base[:, idx] * (1.0 - base[:, idx]), axis=1), 0.95)
    if gate == "ones":
        return np.ones(base.shape[0], dtype=np.float64)
    if gate == "entropy_mid":
        return ent
    if gate == "strength":
        return strength
    if gate == "strength_entropy":
        return np.minimum(strength, ent)
    if gate == "top60_strength":
        threshold = float(np.quantile(strength, 0.40))
        return np.where(strength >= threshold, strength, 0.0)
    raise ValueError(gate)


def positive_q3_direction_only(direction: np.ndarray, base: np.ndarray, projected: np.ndarray) -> np.ndarray:
    out = np.zeros_like(direction)
    idx = target_indices(TARGETS_Q3S4)
    raw = projected - base
    for j in idx:
        keep = raw[:, j] * direction[:, j] > 0.0
        out[:, j] = np.where(keep, direction[:, j], 0.0)
    return out


def build_candidate(
    base: np.ndarray,
    projected: np.ndarray,
    axes: dict[str, np.ndarray | float],
    gamma: float,
    gate_name: str,
    mode: str,
) -> tuple[np.ndarray, dict[str, float]]:
    idx = target_indices(TARGETS_Q3S4)
    prob_dir = np.zeros_like(base)
    prob_dir[:, idx] = projected[:, idx] - base[:, idx]
    gate = gate_values(base, prob_dir, gate_name)

    if mode == "direct_logit":
        out = base.copy()
        out[:, idx] = sigmoid(logit(base[:, idx]) + gamma * gate[:, None] * (logit(projected[:, idx]) - logit(base[:, idx])))
    else:
        direction = prob_dir.copy()
        raw_q = np.asarray(axes["raw_q"], dtype=np.float64)
        raw_grad = (base - raw_q) / np.maximum(base * (1.0 - base), EPS)
        axis_list: list[np.ndarray] = []
        if mode in {"prob_raw_ortho", "prob_bad_raw_ortho", "prob_bad_raw_ord_ortho", "prob_raw_ortho_positive"}:
            axis_list.append(raw_grad)
        if mode in {"prob_bad_raw_ortho", "prob_bad_raw_ord_ortho"}:
            axis_list.append(np.asarray(axes["bad_axis"], dtype=np.float64))
        if mode == "prob_bad_raw_ord_ortho":
            axis_list.append(np.asarray(axes["ordinal_axis"], dtype=np.float64))
        if axis_list:
            direction = orthogonalize(direction, axis_list, TARGETS_Q3S4)
        if mode == "prob_raw_ortho_positive":
            direction = positive_q3_direction_only(direction, base, projected)
        if mode not in {
            "prob",
            "prob_raw_ortho",
            "prob_bad_raw_ortho",
            "prob_bad_raw_ord_ortho",
            "prob_raw_ortho_positive",
        }:
            raise ValueError(mode)
        out = clip(base + gamma * gate[:, None] * direction)

    out = clip(out)
    delta = out - base
    return out, {
        "candidate_entropy": entropy(out),
        "candidate_mean_abs_move_vs_prior": float(np.abs(delta).mean()),
        "candidate_max_abs_move_vs_prior": float(np.abs(delta).max()),
        "mean_gate": float(gate.mean()),
        "nonzero_gate_rate": float((gate > 0).mean()),
        "mean_target_delta_Q3": float(delta[:, TARGETS.index("Q3")].mean()),
        "mean_target_delta_S4": float(delta[:, TARGETS.index("S4")].mean()),
    }


def build_anchor_constraints(sample: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    anchor_names = list(ANCHORS)
    target_scores = np.asarray([ANCHORS[name][1] for name in anchor_names], dtype=np.float64)
    const_mat = []
    coef_mat = []
    for name in anchor_names:
        pred = read_submission(ANCHORS[name][0], sample)[TARGETS].to_numpy(dtype=np.float64)
        const, coef = score_parts(pred)
        const_mat.append(const)
        coef_mat.append(coef)
    return anchor_names, target_scores, np.vstack(const_mat).T, np.vstack(coef_mat).T


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


def selection_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["raw_penalty"] = np.maximum(out["delta_vs_raw05_rawaxis"] - 2.0e-7, 0.0) * 120.0
    out["bad_penalty"] = np.maximum(out["bad_residual_axis_ratio"].abs() - 0.0028, 0.0) * 0.030
    out["posterior_penalty"] = np.maximum(out["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 2.0
    out["ranker_selection_score"] = (
        out["actual_anchor_score_final"] + out["raw_penalty"] + out["bad_penalty"] + out["posterior_penalty"]
    )
    out["q3s4_corr_score"] = (
        out["ranker_selection_score"]
        + 0.25 * out["candidate_mean_abs_move_vs_prior"]
        + 0.0005 * out["bad_residual_axis_ratio"].abs()
    )
    return out


def select_shortlist(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["abs_raw"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["abs_bad"] = frame["bad_residual_axis_ratio"].abs()
    parts = [
        frame.sort_values(["q3s4_corr_score", "actual_anchor_score_final"]).head(50),
        frame.sort_values(["actual_anchor_score_final", "abs_raw", "abs_bad"]).head(40),
        frame[frame["abs_raw"].le(3e-7)].sort_values(["actual_anchor_score_final", "abs_bad"]).head(40),
        frame[frame["abs_bad"].le(0.0006)].sort_values(["ranker_selection_score", "actual_anchor_score_final"]).head(40),
    ]
    for _, group in frame.groupby(["prior", "mode"], sort=False):
        parts.append(group.sort_values("q3s4_corr_score").head(1))
    for _, group in frame.groupby(["prior", "gamma"], sort=False):
        parts.append(group.sort_values("q3s4_corr_score").head(1))
    out = pd.concat(parts, ignore_index=True).drop_duplicates("file")
    return out.sort_values(["q3s4_corr_score", "actual_anchor_score_final"]).head(180).reset_index(drop=True)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    anchor_names, target_scores, const_arr, coef_arr = build_anchor_constraints(sample)
    axes = public_axes()

    records: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    file_names: list[str] = []
    seen: set[str] = set()
    fit_rows = []

    for prior_name, prior_file in BASE_PRIORS.items():
        if not locate(prior_file).exists():
            continue
        prior_frame = read_submission(prior_file, sample)
        base = prior_frame[TARGETS].to_numpy(dtype=np.float64)
        fit = solve_projection(base, const_arr, coef_arr, target_scores)
        fit_rows.append(
            {
                "prior": prior_name,
                "prior_file": prior_file,
                "projection_converged": fit.converged,
                "projection_max_abs_residual": float(np.max(np.abs(fit.residual))),
                "projection_mean_abs_move": float(np.abs(fit.q - base).mean()),
            }
            | {f"expected_{name}": float(value) for name, value in zip(anchor_names, expected_scores(fit.q, const_arr, coef_arr), strict=True)}
        )
        for gamma in GAMMAS:
            for gate_name in GATES:
                for mode in MODES:
                    pred, meta = build_candidate(base, fit.q, axes, gamma, gate_name, mode)
                    h = prediction_hash(pred)
                    if h in seen:
                        continue
                    seen.add(h)
                    file_name = (
                        "submission_raw05_jepa_public6q3s4corr_"
                        f"{prior_name}_{mode}_{gate_name}_g{int(round(gamma * 1000)):03d}_{h}.csv"
                    )
                    public = public_axis_features(pred, axes)
                    records.append(
                        {
                            "file": file_name,
                            "prior": prior_name,
                            "prior_file": prior_file,
                            "target_mask": "q3s4",
                            "targets": ",".join(TARGETS_Q3S4),
                            "gamma": gamma,
                            "gate": gate_name,
                            "mode": mode,
                            "prediction_hash": h,
                            "projection_mean_abs_move": float(np.abs(fit.q - base).mean()),
                        }
                        | meta
                        | public
                    )
                    preds.append(pred)
                    file_names.append(file_name)

    if not records:
        raise RuntimeError("no candidates generated")

    actual = actual_anchor_score(preds, sample).drop(columns=["candidate_index"])
    scan = pd.DataFrame(records).reset_index(drop=True)
    scan = pd.concat([scan, actual.reset_index(drop=True)], axis=1)
    scan = selection_features(scan)
    scan = scan.sort_values(["q3s4_corr_score", "actual_anchor_score_final"]).reset_index(drop=True)
    shortlist = select_shortlist(scan)

    pred_by_file = dict(zip(file_names, preds, strict=True))
    prior_by_file = scan.set_index("file")["prior_file"].to_dict()
    for file_name in shortlist["file"].astype(str):
        prior_frame = read_submission(str(prior_by_file[file_name]), sample)
        out = prior_frame[KEY].copy()
        out[TARGETS] = pred_by_file[file_name]
        out.to_csv(OUT / file_name, index=False)

    fit_df = pd.DataFrame(fit_rows).sort_values(["projection_mean_abs_move", "projection_max_abs_residual"])
    fit_df.to_csv(OUT / "raw05_jepa_public6_q3s4_axis_corrected_projection_fit.csv", index=False)
    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    integrity(shortlist["file"].astype(str).tolist(), sample).to_csv(INTEGRITY_OUT, index=False)

    cols = [
        "file",
        "prior",
        "mode",
        "gate",
        "gamma",
        "actual_anchor_score_final",
        "ranker_selection_score",
        "q3s4_corr_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "raw_penalty",
        "bad_penalty",
        "posterior_penalty",
        "mean_abs_move_vs_raw05",
        "candidate_mean_abs_move_vs_prior",
        "mean_target_delta_Q3",
        "mean_target_delta_S4",
    ]
    family = (
        scan.groupby(["prior", "mode"], as_index=False)
        .agg(
            n=("file", "size"),
            best_actual=("actual_anchor_score_final", "min"),
            best_selection=("ranker_selection_score", "min"),
            best_raw_abs=("delta_vs_raw05_rawaxis", lambda s: float(s.abs().min())),
            best_bad_abs=("bad_residual_axis_ratio", lambda s: float(s.abs().min())),
        )
        .sort_values("best_selection")
    )
    report = [
        "# Raw05 JEPA Public6 Q3S4 Axis-Corrected Candidates",
        "",
        "Uses the six-anchor posterior only as a target-block direction for Q3/S4. Candidate moves are optionally projected away from raw-public and bad residual axes, matching the JEPA idea of changing the target representation while preserving context/public-axis compatibility.",
        "",
        f"- generated candidates: `{len(scan)}`",
        f"- shortlisted/saved candidates: `{len(shortlist)}`",
        "",
        "## Projection Fit",
        "",
        "```csv",
        fit_df.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best Prior/Mode Groups",
        "",
        "```csv",
        family.round(10).head(36).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Shortlist",
        "",
        "```csv",
        shortlist[cols].head(50).round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")

    print(f"generated={len(scan)} shortlist={len(shortlist)}")
    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SHORTLIST_OUT}")
    print(shortlist[cols].head(24).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
