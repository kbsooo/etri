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
    sys.path.append(str(OUT))

from public_subset_sensitivity_audit import load_sub  # noqa: E402
from public_universe_minimax_optimizer import (  # noqa: E402
    BASELINE_PRIOR,
    PROFILES as SCENARIO_PROFILES,
    TARGETS,
    KEY,
    ce_row_loss,
    clip,
    mean_loss,
    oof_name_for_submission,
)
from public_mask_plausibility_reweight import (  # noqa: E402
    evaluate_scores,
    load_diag_moves,
    make_mask_weights,
    mask_matrix_and_metadata,
    scenario_files,
    scenario_weight_vector,
)


PAIR_WEIGHTS = [0.25, 0.50, 0.75]
TRIPLE_PATTERNS = [
    (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
    (0.50, 0.25, 0.25),
    (0.25, 0.50, 0.25),
    (0.25, 0.25, 0.50),
    (0.60, 0.20, 0.20),
    (0.20, 0.60, 0.20),
    (0.20, 0.20, 0.60),
]


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def oof_name(file_name: str) -> str | None:
    if file_name.startswith("submission_public_universeens_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public_maskplausens_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return oof_name_for_submission(file_name)


def scan_pool() -> list[str]:
    files: list[str] = []
    summary = pd.read_csv(OUT / "public_mask_plausibility_reweight_summary.csv")
    for f in summary["file"].head(8).tolist():
        if (OUT / f).exists() and f not in files:
            files.append(f)
    top = pd.read_csv(OUT / "public_mask_plausibility_top_by_profile.csv")
    for f in top[top["rank"] == 1]["file"].tolist():
        if (OUT / f).exists() and f not in files:
            files.append(f)
    refs = [
        "submission_public_minimaxens_r01_a6_h422045.csv",
        "submission_public_minimaxens_r05_a10_h506746.csv",
        "submission_public_minimaxens_r06_a9_h512521.csv",
        "submission_public_minimaxens_r04_a11_h082844.csv",
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    ]
    for f in refs:
        if (OUT / f).exists() and f not in files:
            files.append(f)

    valid: list[str] = []
    for f in files:
        name = oof_name(f)
        if name is not None and (OUT / name).exists():
            valid.append(f)
    return valid[:10]


def all_candidate_weights(n: int, files: list[str]) -> list[tuple[str, np.ndarray]]:
    out: list[tuple[str, np.ndarray]] = []
    for i, f in enumerate(files):
        w = np.zeros(n, dtype=np.float64)
        w[i] = 1.0
        out.append((f"single::{f}", w))

    for i in range(n):
        for j in range(i + 1, n):
            for a in PAIR_WEIGHTS:
                w = np.zeros(n, dtype=np.float64)
                w[i] = a
                w[j] = 1.0 - a
                out.append((f"pair::{files[i]}={a:.2f}|{files[j]}={1-a:.2f}", w))

    top_n = min(5, n)
    for i in range(top_n):
        for j in range(i + 1, top_n):
            for k in range(j + 1, top_n):
                for pattern in TRIPLE_PATTERNS:
                    w = np.zeros(n, dtype=np.float64)
                    w[i], w[j], w[k] = pattern
                    out.append(
                        (
                            f"triple::{files[i]}={pattern[0]:.3f}|{files[j]}={pattern[1]:.3f}|{files[k]}={pattern[2]:.3f}",
                            w,
                        )
                    )

    anchor_names = [
        "submission_public_universeens_u65_r01_365a84a6.csv",
        "submission_public_universeens_u65_r04_dc6f3303.csv",
        "submission_public_universeens_u80_r01_07c571e6.csv",
    ]
    anchors = [files.index(f) for f in anchor_names if f in files]
    for i in anchors:
        for j in range(n):
            if i == j:
                continue
            for a in [0.70, 0.85]:
                w = np.zeros(n, dtype=np.float64)
                w[i] = a
                w[j] = 1.0 - a
                out.append((f"anchor::{files[i]}={a:.2f}|{files[j]}={1-a:.2f}", w))

    dedup: list[tuple[str, np.ndarray]] = []
    seen = set()
    for name, w in out:
        key = tuple(np.round(w, 6))
        if key in seen:
            continue
        seen.add(key)
        dedup.append((name, w))
    return dedup


def metric_weight_profiles(sample: pd.DataFrame) -> tuple[np.ndarray, list[np.ndarray], list[str], list[np.ndarray], np.ndarray]:
    mask_mat, mask_meta = mask_matrix_and_metadata(sample)
    mask_meta = load_diag_moves(mask_meta)
    q_files, q_groups = scenario_files()
    q_scenarios = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in q_files]

    profiles = []
    profile_names = []
    for mask_profile in [
        "mask_equal",
        "diag_plaus_soft",
        "diag_plaus_sharp",
        "subject_heavy",
        "random_heavy",
        "no_global_no_single",
    ]:
        mask_weights = make_mask_weights(mask_meta, mask_profile)
        for scenario_profile, scenario_profile_weights in SCENARIO_PROFILES.items():
            profiles.append(scenario_weight_vector(q_groups, scenario_profile_weights, mask_weights))
            profile_names.append(f"{mask_profile}__{scenario_profile}")
    return mask_mat, q_scenarios, profile_names, profiles, mask_meta


def scenario_mask_scores(mask_mat: np.ndarray, q_scenarios: list[np.ndarray], pred: np.ndarray) -> np.ndarray:
    parts = []
    for q in q_scenarios:
        parts.append(mask_mat @ ce_row_loss(q, pred))
    return np.concatenate(parts)


def evaluate_prediction(
    scores: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    profile_names: list[str],
    profile_weights: list[np.ndarray],
) -> dict[str, float]:
    vals = []
    expected = []
    regrets = []
    max_regrets = []
    deltas = []
    for name, weights in zip(profile_names, profile_weights, strict=True):
        ev = evaluate_scores(scores, best_scores, prior_scores, weights)
        vals.append(ev["score"])
        expected.append(ev["weighted_expected"])
        regrets.append(ev["weighted_regret"])
        max_regrets.append(ev["max_regret"])
        deltas.append(ev["weighted_delta_vs_prior"])
    vals_arr = np.asarray(vals, dtype=np.float64)
    return {
        "mean_score": float(vals_arr.mean()),
        "p90_score": float(np.quantile(vals_arr, 0.90)),
        "worst_score": float(vals_arr.max()),
        "mean_weighted_expected": float(np.mean(expected)),
        "mean_weighted_regret": float(np.mean(regrets)),
        "worst_max_regret": float(np.max(max_regrets)),
        "mean_delta_vs_prior": float(np.mean(deltas)),
        "objective": float(vals_arr.mean() + 0.20 * vals_arr.max()),
    }


def save_blend(rank: int, weights: np.ndarray, files: list[str], pred_stack: np.ndarray, oof_stack: np.ndarray, sample: pd.DataFrame) -> tuple[str, str]:
    pred = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
    oof = clip(np.tensordot(weights, oof_stack, axes=(0, 0)))
    tag = stable_tag(";".join(f"{f}:{w:.6f}" for f, w in zip(files, weights, strict=True) if w > 1e-6))
    sub_file = f"submission_public_maskplausens_r{rank:02d}_{tag}.csv"
    oof_file = f"final_public_maskplausens_r{rank:02d}_{tag}_oof.npy"
    out = sample[KEY].copy()
    out[TARGETS] = pred
    out.to_csv(OUT / sub_file, index=False)
    np.save(OUT / oof_file, oof)
    return sub_file, oof_file


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=float)

    files = scan_pool()
    pred_stack = np.stack([load_sub(f)[TARGETS].to_numpy(dtype=float) for f in files])
    oof_stack = np.stack([clip(np.load(OUT / oof_name(f))) for f in files if oof_name(f) is not None])

    mask_mat, q_scenarios, profile_names, profile_weights, _mask_meta = metric_weight_profiles(sample)
    prior_scores = scenario_mask_scores(mask_mat, q_scenarios, load_sub(BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float))
    base_scores = [scenario_mask_scores(mask_mat, q_scenarios, pred) for pred in pred_stack]
    best_scores = np.vstack(base_scores).min(axis=0)

    rows = []
    candidates = all_candidate_weights(len(files), files)
    for blend_name, weights in candidates:
        pred = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
        scores = scenario_mask_scores(mask_mat, q_scenarios, pred)
        ev = evaluate_prediction(scores, best_scores, prior_scores, profile_names, profile_weights)
        ev.update(
            {
                "blend_name": blend_name,
                "active_weights": int((weights > 1e-6).sum()),
                "weights": ";".join(f"{files[i]}={weights[i]:.6f}" for i in np.where(weights > 1e-6)[0]),
            }
        )
        rows.append(ev)

    scan = pd.DataFrame(rows).sort_values(["objective", "mean_score", "worst_score"]).reset_index(drop=True)
    scan["rank"] = np.arange(1, len(scan) + 1)
    scan.to_csv(OUT / "public_mask_plausibility_blend_scan.csv", index=False)

    selected_rows = []
    saved = 0
    for row in scan.itertuples(index=False):
        if int(row.active_weights) <= 1:
            continue
        weights = np.zeros(len(files), dtype=np.float64)
        for part in str(row.weights).split(";"):
            f, val = part.rsplit("=", 1)
            weights[files.index(f)] = float(val)
        sub_file, oof_file = save_blend(saved + 1, weights, files, pred_stack, oof_stack, sample)
        selected_rows.append(
            {
                "file": sub_file,
                "oof_file": oof_file,
                "source_rank": int(row.rank),
                "objective": float(row.objective),
                "mean_score": float(row.mean_score),
                "worst_score": float(row.worst_score),
                "mean_weighted_expected": float(row.mean_weighted_expected),
                "mean_weighted_regret": float(row.mean_weighted_regret),
                "mean_delta_vs_prior": float(row.mean_delta_vs_prior),
                "active_weights": int(row.active_weights),
                "oof_loss": mean_loss(y, np.load(OUT / oof_file)),
                "weights": row.weights,
            }
        )
        saved += 1
        if saved >= 5:
            break

    selected = pd.DataFrame(selected_rows)
    selected.to_csv(OUT / "public_mask_plausibility_blend_selected.csv", index=False)

    integ_rows = []
    for row in selected.itertuples(index=False):
        sub = pd.read_csv(OUT / row.file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        oof = np.load(OUT / row.oof_file)
        integ_rows.append(
            {
                "file": row.file,
                "rows": len(sub),
                "key_match": bool(sub[KEY].equals(sample[KEY])),
                "duplicate_keys": int(sub.duplicated(KEY).sum()),
                "null_predictions": int(sub[TARGETS].isna().sum().sum()),
                "min_prob": float(sub[TARGETS].min().min()),
                "max_prob": float(sub[TARGETS].max().max()),
                "oof_shape": str(oof.shape),
                "oof_min": float(oof.min()),
                "oof_max": float(oof.max()),
            }
        )
    integ = pd.DataFrame(integ_rows)
    integ.to_csv(OUT / "public_mask_plausibility_blend_integrity.csv", index=False)

    report = []
    report.append("# Public Mask Plausibility Blend Scan\n")
    report.append(
        "Grid scan over top mask-plausibility candidates. Objective is mean profile score plus 0.20 * worst profile score across 24 scenario/mask plausibility profiles.\n"
    )
    cols = [
        "rank",
        "blend_name",
        "objective",
        "mean_score",
        "worst_score",
        "mean_weighted_expected",
        "mean_weighted_regret",
        "mean_delta_vs_prior",
        "active_weights",
    ]
    report.append("\n## Top Scan Rows\n")
    report.append("```\n" + scan[cols].head(25).round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Saved Blends\n")
    report.append("```\n" + selected.round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Integrity\n")
    report.append("```\n" + integ.round(9).to_string(index=False) + "\n```")
    (OUT / "public_mask_plausibility_blend_report.md").write_text("".join(report))

    print("[blend scan top]")
    print(scan[cols].head(25).round(9).to_string(index=False))
    print("\n[selected]")
    print(selected.round(9).to_string(index=False))
    print("\n[integrity]")
    print(integ.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
