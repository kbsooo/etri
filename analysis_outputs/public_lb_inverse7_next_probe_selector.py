from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
A2C8_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"

FULL_RANK = OUT / "public_lb_inverse7_candidate_ranking.csv"
COMPAT_RANK = OUT / "public_lb_inverse7_candidate_ranking_raw05_a2c8_compatible.csv"
SHORTLIST_OUT = OUT / "public_lb_inverse7_next_probe_shortlist.csv"
FAMILY_OUT = OUT / "public_lb_inverse7_next_probe_family_summary.csv"
REPORT_OUT = OUT / "public_lb_inverse7_next_probe_report.md"

META_TABLES = [
    OUT / "frontier_cvjepa_surprise_micro_refine_local_proxy.csv",
    OUT / "frontier_cvjepa_surprise_micro_refine_shortlist.csv",
    OUT / "raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv",
    OUT / "raw05_jepa_public6_drift_microperturb_shortlist.csv",
    OUT / "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv",
    OUT / "local_lb_proxy_validation_candidate_predictions.csv",
    OUT / "public_lb_actual_anchor_ranker_scores.csv",
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


def load_sub(name: str | Path, sample: pd.DataFrame) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 1e-6, 1 - 1e-6)


def logit(x: np.ndarray) -> np.ndarray:
    x = clip_prob(x)
    return np.log(x / (1 - x))


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
    gain_if_zero = np.log((1 - q) / (1 - p))
    return float(np.mean(np.maximum(gain_if_one, gain_if_zero)))


def family_name(file_name: str) -> str:
    if file_name == A2C8_FILE:
        return "known_best_a2c8"
    if "frontier_cvjepa_refine" in file_name:
        return "frontier_cvjepa"
    if "public6q3s4corr" in file_name:
        return "public6_q3s4corr"
    if "public6drift" in file_name:
        return "public6_drift"
    if "public_entropy" in file_name or "public_entropytm" in file_name:
        return "public_entropy"
    if "public_maskaware" in file_name:
        return "public_maskaware"
    if "public_minimaxens" in file_name or "public_universeens" in file_name:
        return "public_minimax"
    if "axisrepair" in file_name or "axistrade" in file_name:
        return "axisrepair"
    if "raw_timeline_jepa_rescue" in file_name:
        return "raw05"
    return "other"


def read_ranks() -> pd.DataFrame:
    full = pd.read_csv(FULL_RANK).reset_index().rename(columns={"index": "inverse7_full_rank"})
    full["inverse7_full_rank"] += 1
    compat = pd.read_csv(COMPAT_RANK).reset_index().rename(columns={"index": "inverse7_compat_rank"})
    compat["inverse7_compat_rank"] += 1
    full_cols = [
        "file",
        "path",
        "inverse7_full_rank",
        "inverse7_candidate_score",
        "inverse7_weighted_expected",
        "inverse7_weighted_regret",
        "inverse7_p90_regret",
        "inverse7_win_rate_best_eps1e4",
    ]
    compat_cols = [
        "file",
        "inverse7_compat_rank",
        "inverse7_candidate_score",
        "inverse7_weighted_expected",
        "inverse7_weighted_regret",
        "inverse7_p90_regret",
        "inverse7_win_rate_best_eps1e4",
    ]
    out = full[full_cols].rename(
        columns={
            "inverse7_candidate_score": "inverse7_full_score",
            "inverse7_weighted_expected": "inverse7_full_expected",
            "inverse7_weighted_regret": "inverse7_full_regret",
            "inverse7_p90_regret": "inverse7_full_p90_regret",
            "inverse7_win_rate_best_eps1e4": "inverse7_full_win_rate_eps1e4",
        }
    ).merge(
        compat[compat_cols].rename(
            columns={
                "inverse7_candidate_score": "inverse7_compat_score",
                "inverse7_weighted_expected": "inverse7_compat_expected",
                "inverse7_weighted_regret": "inverse7_compat_regret",
                "inverse7_p90_regret": "inverse7_compat_p90_regret",
                "inverse7_win_rate_best_eps1e4": "inverse7_compat_win_rate_eps1e4",
            }
        ),
        on="file",
        how="outer",
    )
    return out


def load_metadata() -> pd.DataFrame:
    frames = []
    keep = [
        "file",
        "label",
        "anchor_name",
        "basis",
        "target_mask",
        "row_gate",
        "cell_gate",
        "direction",
        "weight",
        "cap",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "raw05_relative_delta_vs_raw05_public",
    ]
    for table in META_TABLES:
        if not table.exists():
            continue
        df = pd.read_csv(table)
        if "file" not in df.columns:
            continue
        sub = df[[c for c in keep if c in df.columns]].copy()
        sub["metadata_source"] = table.name
        frames.append(sub)
    if not frames:
        return pd.DataFrame({"file": []})
    meta = pd.concat(frames, ignore_index=True, sort=False)
    priority = {
        "frontier_cvjepa_surprise_micro_refine_local_proxy.csv": 0,
        "frontier_cvjepa_surprise_micro_refine_shortlist.csv": 1,
        "raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv": 2,
        "raw05_jepa_public6_drift_microperturb_shortlist.csv": 3,
        "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv": 4,
        "local_lb_proxy_validation_candidate_predictions.csv": 5,
        "public_lb_actual_anchor_ranker_scores.csv": 6,
    }
    meta["_priority"] = meta["metadata_source"].map(priority).fillna(99)
    meta = meta.sort_values(["file", "_priority"]).drop_duplicates("file", keep="first")
    return meta.drop(columns=["_priority"])


def movement_features(ranked: pd.DataFrame) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    raw = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=float)
    a2c8 = load_sub(A2C8_FILE, sample)[TARGETS].to_numpy(dtype=float)
    raw_logit = logit(raw)
    a2c8_logit = logit(a2c8)
    a2c8_vec = a2c8_logit - raw_logit

    focus = ranked[
        (ranked["inverse7_full_rank"].fillna(9999) <= 80)
        | (ranked["inverse7_compat_rank"].fillna(9999) <= 120)
        | ranked["file"].eq(A2C8_FILE)
    ].copy()
    rows = []
    for row in focus.itertuples(index=False):
        file_name = str(row.file)
        path = getattr(row, "path", "")
        source = path if isinstance(path, str) and path else file_name
        located = locate(source)
        if located is None:
            continue
        vals = load_sub(located, sample)[TARGETS].to_numpy(dtype=float)
        vec = logit(vals) - raw_logit
        diff_raw = vals - raw
        diff_a2c8 = vals - a2c8
        rec: dict[str, object] = {
            "file": file_name,
            "family": family_name(file_name),
            "mean_abs_move_vs_raw05_calc": float(np.mean(np.abs(diff_raw))),
            "mean_abs_move_vs_a2c8": float(np.mean(np.abs(diff_a2c8))),
            "max_abs_move_vs_a2c8": float(np.max(np.abs(diff_a2c8))),
            "logit_cosine_to_a2c8_move": cosine(vec, a2c8_vec),
            "logit_orth_ratio_to_a2c8_move": orth_ratio(vec, a2c8_vec),
            "best_case_gain_vs_raw05_if_all_correct": max_possible_logloss_gain(raw, vals),
        }
        for j, target in enumerate(TARGETS):
            rec[f"{target}_mean_abs_move_vs_raw05"] = float(np.mean(np.abs(diff_raw[:, j])))
            rec[f"{target}_signed_mean_delta_vs_raw05"] = float(np.mean(diff_raw[:, j]))
            rec[f"{target}_mean_abs_move_vs_a2c8"] = float(np.mean(np.abs(diff_a2c8[:, j])))
        rows.append(rec)
    return pd.DataFrame(rows)


def select_recommendations(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["rank_signal"] = (
        out["inverse7_full_rank"].fillna(2000).clip(upper=2000) / 2000.0
        + out["inverse7_compat_rank"].fillna(2000).clip(upper=2000) / 2000.0
    )
    out["orth_signal"] = out["logit_orth_ratio_to_a2c8_move"].fillna(0.0)
    out["large_move_signal"] = np.minimum(out["mean_abs_move_vs_a2c8"].fillna(0.0) / 0.002, 2.0)
    out["risk_penalty"] = (
        10.0 * out["inverse7_compat_p90_regret"].fillna(out["inverse7_full_p90_regret"]).fillna(0.0)
        + 1000.0 * out["available_raw05_relative_model_spread"].fillna(0.0001)
    )
    out["next_probe_score"] = (
        -out["rank_signal"]
        + 0.35 * out["orth_signal"]
        + 0.15 * out["large_move_signal"]
        - 0.10 * out["risk_penalty"]
    )
    out["probe_role"] = "candidate"
    out.loc[out["file"].eq(A2C8_FILE), "probe_role"] = "current_public_best_control"
    out.loc[out["family"].eq("public_entropy"), "probe_role"] = "full_inverse_high_upside_old_family"
    out.loc[out["family"].eq("public6_q3s4corr"), "probe_role"] = "raw05_a2c8_compatible_q3s4_axis"
    out.loc[out["family"].eq("frontier_cvjepa"), "probe_role"] = "cvjepa_frontier_family_probe"
    out.loc[out["family"].eq("public_maskaware"), "probe_role"] = "maskaware_public_subset_probe"

    picks = []
    picks.append(out[out["file"].eq(A2C8_FILE)])
    for role, n in [
        ("raw05_a2c8_compatible_q3s4_axis", 8),
        ("cvjepa_frontier_family_probe", 8),
        ("full_inverse_high_upside_old_family", 8),
        ("maskaware_public_subset_probe", 4),
    ]:
        picks.append(
            out[out["probe_role"].eq(role)]
            .sort_values(["next_probe_score", "inverse7_compat_rank", "inverse7_full_rank"], ascending=[False, True, True])
            .head(n)
        )
    selected = pd.concat(picks, ignore_index=True, sort=False).drop_duplicates("file")
    return selected.sort_values(["probe_role", "next_probe_score"], ascending=[True, False]).reset_index(drop=True)


def write_report(shortlist: pd.DataFrame, family: pd.DataFrame) -> None:
    cols = [
        "probe_role",
        "file",
        "family",
        "inverse7_full_rank",
        "inverse7_compat_rank",
        "inverse7_full_expected",
        "inverse7_compat_expected",
        "inverse7_compat_p90_regret",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "mean_abs_move_vs_raw05_calc",
        "mean_abs_move_vs_a2c8",
        "logit_cosine_to_a2c8_move",
        "logit_orth_ratio_to_a2c8_move",
        "best_case_gain_vs_raw05_if_all_correct",
        "next_probe_score",
    ]
    report = [
        "# Public LB Inverse7 Next Probe Selector",
        "",
        "This report combines 7-anchor public inverse ranks, local proxy metrics, and movement geometry relative to the current public best `a2c8`.",
        "",
        "## Family Summary",
        "",
        "```",
        family.round(9).to_string(index=False),
        "```",
        "",
        "## Probe Shortlist",
        "",
        "```",
        shortlist[[c for c in cols if c in shortlist.columns]].round(9).to_string(index=False),
        "```",
        "",
        "## Readout",
        "",
        "- Full inverse ranking still prefers old public-entropy/maskaware families. That is not automatically a submit recommendation because those families were built from the old public posterior and are likely to overfit the inverse model.",
        "- The raw05+a2c8-compatible ranking elevates `public6_q3s4corr` and `frontier_cvjepa` variants. These are more useful diagnostics because they share the sign of the two good anchors while moving along different target axes.",
        "- Prefer probes with high orthogonal ratio to `a2c8` when the goal is information gain, and prefer low model spread / low p90 regret when the goal is score safety.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    ranks = read_ranks()
    meta = load_metadata()
    moves = movement_features(ranks)
    merged = ranks.merge(meta, on="file", how="left").merge(moves, on="file", how="left")
    merged["family"] = merged["family"].fillna(merged["file"].map(family_name))

    family = (
        merged.groupby("family")
        .agg(
            n=("file", "size"),
            best_full_rank=("inverse7_full_rank", "min"),
            best_compat_rank=("inverse7_compat_rank", "min"),
            best_full_expected=("inverse7_full_expected", "min"),
            best_compat_expected=("inverse7_compat_expected", "min"),
            median_orth_to_a2c8=("logit_orth_ratio_to_a2c8_move", "median"),
            median_move_vs_a2c8=("mean_abs_move_vs_a2c8", "median"),
            best_actual_anchor=("actual_anchor_score_final", "min"),
            best_raw05_rel_delta=("available_raw05_relative_delta_vs_raw05_public", "min"),
        )
        .reset_index()
        .sort_values(["best_compat_rank", "best_full_rank"])
    )
    shortlist = select_recommendations(merged)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    write_report(shortlist, family)
    print(REPORT_OUT)
    print(shortlist[["probe_role", "file", "inverse7_full_rank", "inverse7_compat_rank", "mean_abs_move_vs_a2c8", "logit_orth_ratio_to_a2c8_move", "next_probe_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
