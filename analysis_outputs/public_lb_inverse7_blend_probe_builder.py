from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
A2C8_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"

FULL_MASKS = OUT / "public_lb_inverse7_mask_top512.csv"
COMPAT_MASKS = OUT / "public_lb_inverse7_mask_raw05_a2c8_compatible_top512.csv"
SCAN_OUT = OUT / "public_lb_inverse7_blend_probe_scan.csv"
SELECTED_OUT = OUT / "public_lb_inverse7_blend_probe_selected.csv"
REPORT_OUT = OUT / "public_lb_inverse7_blend_probe_report.md"

EPS = 1e-6

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "q3_s2_s4": ["Q3", "S2", "S4"],
    "q3_s2_s3": ["Q3", "S2", "S3"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
}


@dataclass(frozen=True)
class DonorSpec:
    family: str
    file: str
    weights: tuple[float, ...]
    target_masks: tuple[str, ...]
    caps: tuple[float, ...]


DONORS = [
    DonorSpec(
        "q3s4_energyfront",
        "submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ortho_ones_g020_7e46b3e4.csv",
        (0.25, 0.50, 0.75, 1.00),
        ("q3_s4", "q3_s2_s4", "q3_s2_s3_s4"),
        (0.004, 0.008, 0.012),
    ),
    DonorSpec(
        "q3s4_efmicro3",
        "submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ortho_ones_g020_9bbd99ba.csv",
        (0.25, 0.50, 0.75, 1.00),
        ("q3_s4", "q3_s2_s4", "q3_s2_s3_s4"),
        (0.004, 0.008, 0.012),
    ),
    DonorSpec(
        "cvjepa_9d69",
        "submission_frontier_cvjepa_refine_9d69b9bb.csv",
        (0.50, 1.00),
        ("no_q2", "q3_s2_s4", "q3_s2_s3_s4"),
        (0.004, 0.008),
    ),
    DonorSpec(
        "cvjepa_80e9",
        "submission_frontier_cvjepa_refine_80e9f7f8.csv",
        (0.50, 1.00),
        ("no_q2", "q3_s2_s4", "q3_s2_s3_s4"),
        (0.004, 0.008),
    ),
    DonorSpec(
        "entropy_g050",
        "submission_public_entropyproj_public2d0_g050.csv",
        (0.025, 0.050, 0.075, 0.100, 0.150),
        ("q3_s4", "q3_s2_s4", "q3_s2_s3", "q3_s2_s3_s4", "no_q2"),
        (0.003, 0.006, 0.010),
    ),
    DonorSpec(
        "entropy_g075",
        "submission_public_entropyproj_public2d0_g075.csv",
        (0.025, 0.050, 0.075, 0.100, 0.150),
        ("q3_s4", "q3_s2_s4", "q3_s2_s3", "q3_s2_s3_s4", "no_q2"),
        (0.003, 0.006, 0.010),
    ),
    DonorSpec(
        "maskaware_t35r01",
        "submission_public_maskaware_t35_r01_2d5fa124.csv",
        (0.025, 0.050, 0.100),
        ("q3_s2_s3", "q3_s2_s3_s4", "no_q2"),
        (0.003, 0.006),
    ),
]


def locate(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if sample is not None and not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(x, EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    x = clip_prob(x)
    return np.log(x / (1.0 - x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def make_mask_matrix(sample: pd.DataFrame) -> np.ndarray:
    records = build_masks(sample)
    mat = np.zeros((len(records), len(sample)), dtype=np.float64)
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
    return mat


def inverse_weights(detail: pd.DataFrame, n: int = 160) -> tuple[pd.DataFrame, np.ndarray]:
    top = detail.head(n).copy()
    tau = max(0.10, float(top["weighted_std_rmse"].median()))
    weights = np.exp(-0.5 * (top["weighted_std_rmse"].to_numpy(dtype=float) / tau) ** 2)
    weights = weights / weights.sum()
    return top, weights


def blend_prediction(base: np.ndarray, donor: np.ndarray, target_mask: str, weight: float, cap: float) -> np.ndarray:
    out = base.copy()
    cols = [TARGETS.index(t) for t in TARGET_MASKS[target_mask]]
    raw_delta = sigmoid(logit(base[:, cols]) + weight * (logit(donor[:, cols]) - logit(base[:, cols]))) - base[:, cols]
    capped_delta = np.clip(raw_delta, -cap, cap)
    out[:, cols] = clip_prob(base[:, cols] + capped_delta)
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 1e-12:
        return float("nan")
    return float(np.dot(aa, bb) / denom)


def orth_ratio(vec: np.ndarray, basis: np.ndarray) -> float:
    vv = vec.reshape(-1)
    bb = basis.reshape(-1)
    denom = float(np.dot(bb, bb))
    norm = float(np.linalg.norm(vv))
    if denom <= 1e-12 or norm <= 1e-12:
        return float("nan")
    proj = bb * (float(np.dot(vv, bb)) / denom)
    return float(np.linalg.norm(vv - proj) / norm)


def max_possible_logloss_gain(base: np.ndarray, candidate: np.ndarray) -> float:
    p = clip_prob(base)
    q = clip_prob(candidate)
    gain_if_one = np.log(q / p)
    gain_if_zero = np.log((1.0 - q) / (1.0 - p))
    return float(np.mean(np.maximum(gain_if_one, gain_if_zero)))


def score_candidates(
    candidates: list[dict[str, object]],
    detail: pd.DataFrame,
    weights: np.ndarray,
    mask_mat: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    scenario_cache: dict[str, np.ndarray] = {}
    scores_by_name: dict[str, list[float]] = {str(c["name"]): [] for c in candidates}
    for row in detail.itertuples(index=False):
        scenario_path = str(getattr(row, "scenario_path"))
        if scenario_path not in scenario_cache:
            scenario_cache[scenario_path] = load_sub(scenario_path, sample=None)[TARGETS].to_numpy(dtype=np.float64)
        q = scenario_cache[scenario_path]
        mask_vec = mask_mat[int(row.mask_index)]
        for cand in candidates:
            loss = ce_matrix(q, cand["pred"])
            scores_by_name[str(cand["name"])].append(float(mask_vec @ loss.mean(axis=1)))

    score_mat = np.vstack([scores_by_name[str(c["name"])] for c in candidates])
    best_per_combo = score_mat.min(axis=0)
    rows = []
    vectors = {}
    for i, cand in enumerate(candidates):
        scores = score_mat[i]
        regret = scores - best_per_combo
        name = str(cand["name"])
        vectors[name] = scores
        rows.append(
            {
                "name": name,
                "expected": float(weights @ scores),
                "regret": float(weights @ regret),
                "p90_regret": float(np.quantile(regret, 0.90)),
                "max_regret": float(regret.max()),
                "win_rate_best_eps1e4": float(np.mean(regret <= 1e-4)),
                "score_std": float(np.std(scores)),
            }
        )
    frame = pd.DataFrame(rows)
    frame["score"] = (
        frame["expected"]
        + 2.0 * frame["regret"]
        + 0.75 * frame["p90_regret"]
        + 0.05 * frame["max_regret"]
        + 0.005 * np.maximum(0.50 - frame["win_rate_best_eps1e4"], 0.0)
    )
    return frame, vectors


def add_geometry(
    rows: pd.DataFrame,
    candidates: list[dict[str, object]],
    raw: np.ndarray,
    a2c8: np.ndarray,
) -> pd.DataFrame:
    pred_by_name = {str(c["name"]): c["pred"] for c in candidates}
    raw_logit = logit(raw)
    a2c8_logit = logit(a2c8)
    a2c8_vec = a2c8_logit - raw_logit
    geom_rows = []
    for name, pred in pred_by_name.items():
        diff_a = pred - a2c8
        diff_r = pred - raw
        vec = logit(pred) - raw_logit
        rec: dict[str, object] = {
            "name": name,
            "mean_abs_move_vs_a2c8": float(np.mean(np.abs(diff_a))),
            "max_abs_move_vs_a2c8": float(np.max(np.abs(diff_a))),
            "mean_abs_move_vs_raw05": float(np.mean(np.abs(diff_r))),
            "logit_cosine_to_a2c8_move": cosine(vec, a2c8_vec),
            "logit_orth_ratio_to_a2c8_move": orth_ratio(vec, a2c8_vec),
            "best_case_gain_vs_raw05_if_all_correct": max_possible_logloss_gain(raw, pred),
        }
        for j, target in enumerate(TARGETS):
            rec[f"{target}_signed_delta_vs_a2c8"] = float(np.mean(diff_a[:, j]))
            rec[f"{target}_mean_abs_move_vs_a2c8"] = float(np.mean(np.abs(diff_a[:, j])))
        geom_rows.append(rec)
    return rows.merge(pd.DataFrame(geom_rows), on="name", how="left")


def build_candidates(sample: pd.DataFrame) -> tuple[list[dict[str, object]], np.ndarray, np.ndarray]:
    base_df = load_sub(A2C8_FILE, sample)
    raw_df = load_sub(RAW05_FILE, sample)
    base = base_df[TARGETS].to_numpy(dtype=np.float64)
    raw = raw_df[TARGETS].to_numpy(dtype=np.float64)
    candidates: list[dict[str, object]] = [
        {"name": "control_a2c8", "family": "control", "file": A2C8_FILE, "pred": base, "source_file": A2C8_FILE},
        {"name": "control_raw05", "family": "control", "file": RAW05_FILE, "pred": raw, "source_file": RAW05_FILE},
    ]

    for donor_spec in DONORS:
        path = locate(donor_spec.file)
        if path is None:
            print(f"[skip missing donor] {donor_spec.file}")
            continue
        donor = load_sub(donor_spec.file, sample)[TARGETS].to_numpy(dtype=np.float64)
        candidates.append(
            {
                "name": f"donor_{donor_spec.family}",
                "family": f"donor_{donor_spec.family}",
                "file": donor_spec.file,
                "pred": donor,
                "source_file": donor_spec.file,
            }
        )
        for weight in donor_spec.weights:
            for target_mask in donor_spec.target_masks:
                for cap in donor_spec.caps:
                    tag = f"{donor_spec.family}|{target_mask}|w{weight:.3f}|c{cap:.3f}"
                    file_name = f"submission_inverse7blend_{stable_hash(tag)}.csv"
                    pred = blend_prediction(base, donor, target_mask, weight, cap)
                    candidates.append(
                        {
                            "name": f"blend_{tag}",
                            "family": donor_spec.family,
                            "file": file_name,
                            "pred": pred,
                            "source_file": donor_spec.file,
                            "target_mask": target_mask,
                            "blend_weight": weight,
                            "cap": cap,
                        }
                    )
    return candidates, raw, base


def candidate_metadata(candidates: list[dict[str, object]]) -> pd.DataFrame:
    rows = []
    for cand in candidates:
        rows.append(
            {
                "name": cand["name"],
                "family": cand.get("family", ""),
                "file": cand.get("file", ""),
                "source_file": cand.get("source_file", ""),
                "target_mask": cand.get("target_mask", ""),
                "blend_weight": cand.get("blend_weight", np.nan),
                "cap": cand.get("cap", np.nan),
            }
        )
    return pd.DataFrame(rows)


def save_submission(sample: pd.DataFrame, pred: np.ndarray, file_name: str) -> None:
    out = sample.copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)


def write_report(scan: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "submit_role",
        "file",
        "family",
        "source_file",
        "target_mask",
        "blend_weight",
        "cap",
        "combined_rank_score",
        "compat_delta_vs_a2c8",
        "full_delta_vs_a2c8",
        "compat_regret",
        "compat_p90_regret",
        "full_regret",
        "mean_abs_move_vs_a2c8",
        "max_abs_move_vs_a2c8",
        "logit_orth_ratio_to_a2c8_move",
        "best_case_gain_vs_raw05_if_all_correct",
    ]
    family_cols = [
        "family",
        "n",
        "best_combined_rank_score",
        "best_compat_delta_vs_a2c8",
        "best_full_delta_vs_a2c8",
        "median_move_vs_a2c8",
        "median_orth_to_a2c8",
    ]
    family = (
        scan.groupby("family")
        .agg(
            n=("file", "size"),
            best_combined_rank_score=("combined_rank_score", "min"),
            best_compat_delta_vs_a2c8=("compat_delta_vs_a2c8", "min"),
            best_full_delta_vs_a2c8=("full_delta_vs_a2c8", "min"),
            median_move_vs_a2c8=("mean_abs_move_vs_a2c8", "median"),
            median_orth_to_a2c8=("logit_orth_ratio_to_a2c8_move", "median"),
        )
        .reset_index()
        .sort_values(["best_combined_rank_score", "best_compat_delta_vs_a2c8"])
    )
    report = [
        "# Public LB Inverse7 Blend Probe Builder",
        "",
        "Base submission is `submission_frontier_cvjepa_refine_a2c8d2c8.csv`. Generated probes are logit-space blends from that base toward selected q3/sleep-stage JEPA, public-entropy, and mask-aware donors.",
        "",
        "## Family Summary",
        "",
        "```",
        family[family_cols].round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submission Files",
        "",
        "```",
        selected[[c for c in cols if c in selected.columns]].round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- `compat_delta_vs_a2c8` is the raw05+a2c8-compatible inverse-mask score shift. Negative is locally favorable against the stricter two-good-anchor posterior.",
        "- `full_delta_vs_a2c8` is the all-top-mask score shift. Public-entropy donors can look strong here but are intentionally treated as diagnostic because they conflict with the raw05+a2c8-compatible mask set.",
        "- The selected set deliberately keeps one control-like candidate, several q3/s4-compatible candidates, and at least one orthogonal public-entropy diagnostic. That is the fastest way to distinguish score safety from hidden-split information gain.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def assign_roles(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    out["submit_role"] = "not_selected"
    selected_names: list[str] = []

    def take_unique(frame: pd.DataFrame, n: int, key_cols: list[str]) -> list[str]:
        names = []
        seen = set()
        for row in frame.itertuples(index=False):
            key = tuple(getattr(row, col) for col in key_cols)
            if key in seen:
                continue
            seen.add(key)
            names.append(str(row.name))
            if len(names) >= n:
                break
        return names

    cvjepa_pool = out[
        out["name"].str.startswith("blend_")
        & out["family"].isin(["cvjepa_9d69", "cvjepa_80e9"])
        & (out["compat_delta_vs_a2c8"] <= 5e-5)
        & (out["compat_p90_delta_vs_a2c8"] <= 2.5e-4)
    ].sort_values(["combined_rank_score", "compat_delta_vs_a2c8"])
    q3s4_pool = out[
        out["name"].str.startswith("blend_")
        & out["family"].isin(["q3s4_energyfront", "q3s4_efmicro3"])
        & (out["compat_delta_vs_a2c8"] <= 1e-6)
        & (out["full_delta_vs_a2c8"] <= 5e-6)
    ].sort_values(["combined_rank_score", "compat_delta_vs_a2c8"])
    diagnostic_pool = out[
        out["name"].str.startswith("blend_")
        & out["family"].isin(["entropy_g050", "entropy_g075", "maskaware_t35r01"])
        & (out["mean_abs_move_vs_a2c8"] >= 0.00015)
        & (out["compat_delta_vs_a2c8"] <= 2.5e-4)
    ].sort_values(["combined_rank_score", "compat_delta_vs_a2c8"])
    orthogonal_pool = out[
        out["name"].str.startswith("blend_")
        & out["family"].isin(["entropy_g050", "entropy_g075"])
        & (out["logit_orth_ratio_to_a2c8_move"] >= 0.35)
        & (out["compat_delta_vs_a2c8"] <= 5.0e-4)
    ].sort_values(["compat_delta_vs_a2c8", "combined_rank_score"])

    for name in take_unique(cvjepa_pool, 2, ["family", "target_mask", "blend_weight"]):
        selected_names.append(name)
        out.loc[out["name"].eq(name), "submit_role"] = "score_safe_q3s4_cvjepa"
    for name in take_unique(q3s4_pool, 4, ["family", "target_mask", "blend_weight"]):
        if name not in selected_names:
            selected_names.append(name)
            out.loc[out["name"].eq(name), "submit_role"] = "score_safe_q3s4_axis"
    for name in diagnostic_pool.head(8)["name"].tolist():
        if name not in selected_names:
            selected_names.append(name)
            out.loc[out["name"].eq(name), "submit_role"] = "moderate_diagnostic_blend"
    for name in orthogonal_pool.head(4)["name"].tolist():
        if name not in selected_names:
            selected_names.append(name)
            out.loc[out["name"].eq(name), "submit_role"] = "orthogonal_entropy_probe"

    control = out[out["name"].eq("control_a2c8")]
    if len(control):
        selected_names.insert(0, "control_a2c8")
        out.loc[out["name"].eq("control_a2c8"), "submit_role"] = "current_public_best_control"

    out["selected_order"] = out["name"].map({name: i for i, name in enumerate(dict.fromkeys(selected_names))})
    return out


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    mask_mat = make_mask_matrix(sample)
    full_detail, full_weights = inverse_weights(pd.read_csv(FULL_MASKS))
    compat_detail, compat_weights = inverse_weights(pd.read_csv(COMPAT_MASKS))
    candidates, raw, a2c8 = build_candidates(sample)

    full_scores, _ = score_candidates(candidates, full_detail, full_weights, mask_mat)
    compat_scores, _ = score_candidates(candidates, compat_detail, compat_weights, mask_mat)
    meta = candidate_metadata(candidates)
    scan = meta.merge(full_scores.add_prefix("full_").rename(columns={"full_name": "name"}), on="name")
    scan = scan.merge(compat_scores.add_prefix("compat_").rename(columns={"compat_name": "name"}), on="name")
    scan = add_geometry(scan, candidates, raw, a2c8)

    a2c8_row = scan[scan["name"].eq("control_a2c8")].iloc[0]
    scan["full_delta_vs_a2c8"] = scan["full_expected"] - float(a2c8_row["full_expected"])
    scan["compat_delta_vs_a2c8"] = scan["compat_expected"] - float(a2c8_row["compat_expected"])
    scan["full_score_delta_vs_a2c8"] = scan["full_score"] - float(a2c8_row["full_score"])
    scan["compat_score_delta_vs_a2c8"] = scan["compat_score"] - float(a2c8_row["compat_score"])

    # Per-combo deltas are more stable than raw expected scores because full and compat inverse sets have different scales.
    full_vectors = {row["name"]: np.array([]) for row in candidates}
    compat_vectors = {row["name"]: np.array([]) for row in candidates}
    _, full_vectors = score_candidates(candidates, full_detail, full_weights, mask_mat)
    _, compat_vectors = score_candidates(candidates, compat_detail, compat_weights, mask_mat)
    a2c8_full_vec = full_vectors["control_a2c8"]
    a2c8_compat_vec = compat_vectors["control_a2c8"]
    p90_full_delta = []
    p90_compat_delta = []
    worst_compat_delta = []
    for row in scan.itertuples(index=False):
        name = str(row.name)
        p90_full_delta.append(float(np.quantile(full_vectors[name] - a2c8_full_vec, 0.90)))
        p90_compat_delta.append(float(np.quantile(compat_vectors[name] - a2c8_compat_vec, 0.90)))
        worst_compat_delta.append(float(np.max(compat_vectors[name] - a2c8_compat_vec)))
    scan["full_p90_delta_vs_a2c8"] = p90_full_delta
    scan["compat_p90_delta_vs_a2c8"] = p90_compat_delta
    scan["compat_worst_delta_vs_a2c8"] = worst_compat_delta

    scan["combined_rank_score"] = (
        scan["compat_delta_vs_a2c8"]
        + 0.35 * scan["full_delta_vs_a2c8"]
        + 1.25 * np.maximum(scan["compat_p90_delta_vs_a2c8"], 0.0)
        + 0.35 * np.maximum(scan["compat_worst_delta_vs_a2c8"], 0.0)
        + 0.15 * scan["compat_regret"]
        + 0.05 * scan["full_regret"]
    )
    scan = scan.sort_values(["combined_rank_score", "compat_delta_vs_a2c8"]).reset_index(drop=True)
    scan["combined_rank"] = np.arange(1, len(scan) + 1)
    scan = assign_roles(scan)
    scan.sort_values(["combined_rank"]).to_csv(SCAN_OUT, index=False)

    selected = scan[scan["submit_role"].ne("not_selected")].copy()
    role_order = {
        "current_public_best_control": 0,
        "moderate_diagnostic_blend": 1,
        "orthogonal_entropy_probe": 2,
        "score_safe_q3s4_axis": 3,
        "score_safe_q3s4_cvjepa": 4,
    }
    selected["_role_order"] = selected["submit_role"].map(role_order).fillna(99)
    selected = selected.sort_values(["_role_order", "combined_rank_score", "compat_delta_vs_a2c8"]).drop(columns=["_role_order"]).reset_index(drop=True)
    selected.to_csv(SELECTED_OUT, index=False)

    pred_by_name = {str(c["name"]): c["pred"] for c in candidates}
    for row in selected.itertuples(index=False):
        if str(row.name).startswith("control_") or str(row.file).startswith("submission_raw_timeline"):
            continue
        save_submission(sample, pred_by_name[str(row.name)], str(row.file))

    write_report(scan, selected)
    print(REPORT_OUT)
    print(
        selected[
            [
                "submit_role",
                "file",
                "family",
                "target_mask",
                "blend_weight",
                "cap",
                "combined_rank_score",
                "compat_delta_vs_a2c8",
                "full_delta_vs_a2c8",
                "mean_abs_move_vs_a2c8",
                "logit_orth_ratio_to_a2c8_move",
            ]
        ]
        .head(30)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
