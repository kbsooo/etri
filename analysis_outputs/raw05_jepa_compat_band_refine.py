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
from jepa_context_target_compatibility_audit import (  # noqa: E402
    CONTEXT_IDX,
    TARGET_IDX,
    poly_context_features,
    soft_kl,
)
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    RAW05_FILE,
    actual_anchor_score,
    integrity,
    read_submission,
    save_submission,
)
from raw05_jepa_q3stress_counterweight_local_refine import unique_existing  # noqa: E402
from raw05_jepa_sigreg_gated_microrefine import quick_health  # noqa: E402


OUT_SCAN = OUT / "raw05_jepa_compat_band_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_compat_band_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_compat_band_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_compat_band_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_compat_band_refine_report.md"

COMPAT_CENTER = -0.000732
COMPAT_LOW = -0.000755
COMPAT_HIGH = -0.000705
BETAS = [0.08, 0.14, 0.22, 0.32, 0.44, 0.58]


class ContextTargetModel:
    def __init__(self, train: pd.DataFrame) -> None:
        x = poly_context_features(train[["Q1", "Q2", "S1", "S2", "S3"]].to_numpy(dtype=np.float64))
        y = train[["Q3", "S4"]].to_numpy(dtype=np.float64)
        self.mu = x.mean(axis=0)
        self.sd = np.where(x.std(axis=0) < 1e-12, 1.0, x.std(axis=0))
        xs = (x - self.mu) / self.sd
        x_aug = np.column_stack([np.ones(len(xs)), xs])
        penalty = np.eye(x_aug.shape[1]) * 2.0
        penalty[0, 0] = 0.0
        self.beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y

    def predict(self, context: np.ndarray) -> np.ndarray:
        x = poly_context_features(context)
        xs = (x - self.mu) / self.sd
        x_aug = np.column_stack([np.ones(len(xs)), xs])
        return np.clip(x_aug @ self.beta, 1e-4, 1.0 - 1e-4)

    def score(self, pred: np.ndarray) -> dict[str, np.ndarray | float]:
        implied = self.predict(pred[:, CONTEXT_IDX])
        target = clip(pred[:, TARGET_IDX])
        kl = soft_kl(implied, target)
        abs_logit = np.abs(logit(implied) - logit(target))
        return {
            "row_kl": kl.mean(axis=1),
            "compat_kl_mean": float(kl.mean()),
            "compat_abslogit_mean": float(abs_logit.mean()),
            "compat_q3_kl": float(kl[:, 0].mean()),
            "compat_s4_kl": float(kl[:, 1].mean()),
        }


def profile_vector(**weights: float) -> np.ndarray:
    values = np.ones(len(TARGETS), dtype=np.float64)
    for target, value in weights.items():
        values[TARGETS.index(target)] = value
    return values.reshape(1, -1)


def blend_profiles() -> list[tuple[str, np.ndarray]]:
    return [
        ("all_soft", profile_vector()),
        ("context_only", profile_vector(Q3=0.0, S4=0.0)),
        ("target_tiny", profile_vector(Q3=0.06, S4=0.06)),
        ("q2s1_context", profile_vector(Q1=0.55, Q2=1.15, Q3=0.04, S1=1.15, S2=0.86, S3=0.86, S4=0.04)),
        ("q1light_context", profile_vector(Q1=0.42, Q3=0.05, S4=0.05)),
    ]


def locate_existing(file_name: str) -> bool:
    try:
        read_submission(file_name)
        return True
    except FileNotFoundError:
        return False


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
    local = pd.read_csv(OUT / "local_lb_proxy_validation_candidate_predictions.csv")
    sigreg = pd.read_csv(OUT / "lejepa_sigreg_candidate_audit.csv")
    compat = pd.read_csv(OUT / "jepa_context_target_compatibility_scores.csv")

    local_raw = local[local["file"].astype(str).str.contains("raw05_jepa", regex=False)].copy()
    local_raw["bad_abs"] = local_raw["bad_residual_axis_ratio"].abs()
    sigreg_raw = sigreg[sigreg["file"].astype(str).str.contains("raw05_jepa", regex=False)].copy()
    compat_band = compat[
        compat["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW - 0.00004, COMPAT_HIGH + 0.00004)
    ].copy()

    bases: list[str] = []
    bases.extend(top_files(local_raw, ["raw05_relative_lb_proxy_mean"], 18))
    bases.extend(top_files(local_raw, ["actual_anchor_score_final", "bad_abs"], 14))
    bases.extend(top_files(sigreg_raw, ["lejepa_combined_rank", "actual_anchor_score_final"], 18))
    bases.extend(top_files(compat_band, ["compat_kl_mean_delta_vs_raw05"], 16))

    donors: list[str] = []
    donors.extend(top_files(local_raw, ["bad_abs", "raw05_relative_lb_proxy_mean"], 18))
    donors.extend(top_files(local_raw, ["lejepa_residual_health", "actual_anchor_score_final"], 18))
    donors.extend(top_files(sigreg_raw, ["lejepa_combined_rank", "actual_anchor_score_final"], 24))
    donors.extend(top_files(sigreg_raw, ["bad_residual_axis_ratio", "lejepa_residual_health"], 20))
    donors.extend(top_files(compat_band, ["compat_kl_mean_delta_vs_raw05"], 24))

    bases = [f for f in unique_existing(bases) if locate_existing(f)][:22]
    donors = [f for f in unique_existing(donors) if locate_existing(f)][:28]
    return bases, donors


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    ref_key = sample[KEY].reset_index(drop=True)
    arrays: dict[str, np.ndarray] = {}
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def axis_row_pressure(pred: np.ndarray, axes: dict[str, np.ndarray | float]) -> np.ndarray:
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    bad_axis = np.asarray(axes["bad_axis"], dtype=np.float64)
    return np.mean(np.abs((pred - stage2) * bad_axis), axis=1)


def logistic_gate(diff: np.ndarray, floor: float = 0.12) -> np.ndarray:
    scale = max(float(np.median(np.abs(diff))), 1e-8)
    gate = 1.0 / (1.0 + np.exp(-np.clip(diff / scale, -40.0, 40.0)))
    return floor + (1.0 - floor) * gate


def row_gate(
    mode: str,
    base_pred: np.ndarray,
    prop_pred: np.ndarray,
    base_compat: np.ndarray,
    prop_compat: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[np.ndarray, dict[str, float]]:
    if mode == "ones":
        gate = np.ones(len(base_pred), dtype=np.float64)
    else:
        bad_gate = logistic_gate(axis_row_pressure(base_pred, axes) - axis_row_pressure(prop_pred, axes), 0.10)
        compat_gate = logistic_gate(base_compat - prop_compat, 0.16)
        if mode == "bad_soft":
            gate = bad_gate
        elif mode == "compat_soft":
            gate = compat_gate
        elif mode == "bad_compat_min":
            gate = np.minimum(bad_gate, compat_gate)
        elif mode == "bad_compat_mix":
            gate = 0.65 * bad_gate + 0.35 * compat_gate
        else:
            raise ValueError(mode)
    return gate, {
        "row_gate": mode,
        "gate_mean": float(gate.mean()),
        "gate_p10": float(np.quantile(gate, 0.10)),
    }


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def generate_candidates(
    bases: list[str],
    donors: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
    compat_model: ContextTargetModel,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    raw_logit = logit(raw)
    raw_compat = compat_model.score(raw)
    logits = {name: logit(arrays[name]) for name in arrays}
    compat_cache = {name: compat_model.score(arrays[name])["row_kl"] for name in arrays}
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        base_pred = arrays[base_file]
        base_compat = np.asarray(compat_cache[base_file], dtype=np.float64)
        for donor_file in donors:
            if donor_file == base_file:
                continue
            donor_logit = logits[donor_file]
            for profile_name, profile in blend_profiles():
                step = (donor_logit - base_logit) * profile
                if float(np.abs(step).mean()) <= 1e-10:
                    continue
                for beta in BETAS:
                    prop_logit = base_logit + beta * step
                    prop_pred = sigmoid(prop_logit)
                    prop_compat = np.asarray(compat_model.score(prop_pred)["row_kl"], dtype=np.float64)
                    for mode in ["ones", "bad_soft", "compat_soft", "bad_compat_min", "bad_compat_mix"]:
                        gate, gate_meta = row_gate(mode, base_pred, prop_pred, base_compat, prop_compat, axes)
                        pred = sigmoid(base_logit + (prop_logit - base_logit) * gate.reshape(-1, 1))
                        h = prediction_hash(pred)
                        if h in seen:
                            continue
                        seen.add(h)
                        compat = compat_model.score(pred)
                        public = public_axis_features(pred, axes)
                        row = {
                            "label": f"{base_file}|donor={donor_file}|profile={profile_name}|b={beta:.2f}|gate={mode}",
                            "prediction_hash": h,
                            "base_file": base_file,
                            "donor_file": donor_file,
                            "blend_profile": profile_name,
                            "beta": beta,
                            "compat_kl_mean": compat["compat_kl_mean"],
                            "compat_abslogit_mean": compat["compat_abslogit_mean"],
                            "compat_q3_kl": compat["compat_q3_kl"],
                            "compat_s4_kl": compat["compat_s4_kl"],
                            "compat_kl_mean_delta_vs_raw05": float(compat["compat_kl_mean"] - raw_compat["compat_kl_mean"]),
                            "compat_abslogit_mean_delta_vs_raw05": float(
                                compat["compat_abslogit_mean"] - raw_compat["compat_abslogit_mean"]
                            ),
                        }
                        row.update(gate_meta)
                        row.update(public)
                        rows.append(row)
                        preds.append(pred)
    return pd.DataFrame(rows), preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["compat_band_distance"] = (frame["compat_kl_mean_delta_vs_raw05"] - COMPAT_CENTER).abs()
    frame["prefilter_score"] = (
        frame["actual_proxy_placeholder"] if "actual_proxy_placeholder" in frame.columns else 0.0
    )
    masks = [
        frame["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW, COMPAT_HIGH)
        & (frame["bad_abs"] <= 0.00010)
        & (frame["delta_vs_raw05_rawaxis"] <= 1.10e-7),
        frame["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW, COMPAT_HIGH)
        & (frame["bad_abs"] <= 0.00034)
        & (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7),
        frame["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW, COMPAT_HIGH)
        & (frame["bad_abs"] <= 0.00058)
        & (frame["posterior_expected_public_vs_anchor"] <= 0.57691),
    ]
    parts = []
    for mask in masks:
        part = frame[mask].sort_values(["compat_band_distance", "bad_abs", "posterior_expected_public_vs_anchor"]).head(700)
        parts.append(part)
    parts.append(
        frame[frame["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW - 0.00001, COMPAT_HIGH + 0.00001)]
        .sort_values(["bad_abs", "compat_band_distance"])
        .head(700)
    )
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values(["compat_band_distance", "bad_abs", "posterior_expected_public_vs_anchor"]).head(1800)


def score_candidates(
    selected_for_scoring: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["compat_band_distance"] = (scored["compat_kl_mean_delta_vs_raw05"] - COMPAT_CENTER).abs()

    rng = np.random.default_rng(2026052704)
    raw_logit = logit(raw)
    health_rows = [quick_health(preds[int(row["candidate_index"])], raw, raw_logit, axes, rng) for _, row in scored.iterrows()]
    scored = pd.concat([scored, pd.DataFrame(health_rows)], axis=1)
    scored["actual_rank"] = scored["actual_anchor_score_final"].rank(method="min")
    scored["health_rank"] = scored["quick_lejepa_health"].rank(method="min")
    scored["bad_rank"] = scored["bad_abs"].rank(method="min")
    scored["compat_rank"] = scored["compat_band_distance"].rank(method="min")
    scored["compat_selection_rank"] = (
        0.38 * scored["actual_rank"]
        + 0.24 * scored["health_rank"]
        + 0.23 * scored["bad_rank"]
        + 0.15 * scored["compat_rank"]
    )
    return scored.sort_values(["compat_selection_rank", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "compat_lowbad",
            (scored["bad_abs"] <= 0.00008)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (scored["compat_kl_mean_delta_vs_raw05"].between(COMPAT_LOW, COMPAT_HIGH)),
            ["bad_abs", "actual_anchor_score_final"],
            18,
        ),
        (
            "compat_balanced",
            (scored["bad_abs"] <= 0.00036)
            & (scored["quick_lejepa_health"] <= 10.30)
            & (scored["actual_anchor_score_final"] <= 0.57784020),
            ["compat_selection_rank", "actual_anchor_score_final"],
            22,
        ),
        (
            "compat_health",
            (scored["quick_lejepa_health"] <= 9.90)
            & (scored["bad_abs"] <= 0.00062)
            & (scored["actual_anchor_score_final"] <= 0.57784010),
            ["quick_lejepa_health", "actual_anchor_score_final"],
            18,
        ),
        (
            "compat_actual",
            (scored["actual_anchor_score_final"] <= 0.57783915)
            & (scored["bad_abs"] <= 0.00062)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.15e-7),
            ["actual_anchor_score_final", "compat_selection_rank"],
            18,
        ),
        (
            "compat_posterior",
            (scored["posterior_expected_public_vs_anchor"] <= 0.576895)
            & (scored["bad_abs"] <= 0.00036)
            & (scored["actual_anchor_score_final"] <= 0.57784020),
            ["posterior_expected_public_vs_anchor", "compat_selection_rank"],
            18,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    selected = pd.concat(parts, ignore_index=True).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["compat_selection_rank", "actual_anchor_score_final"]).reset_index(drop=True)
    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = row["prediction_hash"]
        file_name = f"submission_raw05_jepa_compatband_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "compat_kl_mean_delta_vs_raw05",
        "quick_lejepa_health",
        "compat_selection_rank",
        "base_file",
        "donor_file",
        "blend_profile",
        "beta",
        "row_gate",
    ]
    lines = [
        "# Raw05 JEPA Compatibility-Band Refine",
        "",
        "Goal: keep train-label JEPA context-target compatibility in the raw05-compatible guardrail band while improving bad-axis and LeJEPA residual health.",
        "",
        f"- generated: {len(scan)}",
        f"- rescored: {len(scored)}",
        f"- saved: {len(selected)}",
        f"- compatibility band: [{COMPAT_LOW}, {COMPAT_HIGH}], center {COMPAT_CENTER}",
        "",
        "## Selected",
        "",
        "```csv",
        selected[[c for c in cols if c in selected.columns]].head(80).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Scored Top",
        "",
        "```csv",
        scored[[c for c in cols if c in scored.columns and c != "file"]].head(80).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    axes = public_axes()
    compat_model = ContextTargetModel(train)
    bases, donors = candidate_pools()
    arrays = load_arrays(unique_existing([RAW05_FILE, *bases, *donors]), sample)
    scan, preds = generate_candidates(bases, donors, arrays, raw, axes, compat_model)
    scan.to_csv(OUT_SCAN, index=False)
    selected_for_scoring = prefilter(scan)
    scored = score_candidates(selected_for_scoring, preds, sample, raw, axes)
    scored.to_csv(OUT_SCORED, index=False)
    selected = select_and_save(scored, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ)

    show_cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "compat_kl_mean_delta_vs_raw05",
        "quick_lejepa_health",
        "compat_selection_rank",
        "base_file",
        "donor_file",
        "blend_profile",
        "beta",
        "row_gate",
    ]
    print(f"bases={len(bases)} donors={len(donors)} generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print(selected[show_cols].head(50).round(10).to_string(index=False))
    print(integ.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
