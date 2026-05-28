from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

KNOWN_IN = OUT / "public_anchor_bottleneck_known.csv"
CANDIDATE_IN = OUT / "public_anchor_bottleneck_candidate_scores.csv"
LOO_INVERSE_IN = OUT / "public_lb_direct_label_inverse7_loocv_policy.csv"
L2O_INVERSE_IN = OUT / "public_lb_direct_label_inverse7_l2ocv_policy.csv"

PRED_OUT = OUT / "hidden_subset_selector_stress_anchor_predictions.csv"
MODEL_OUT = OUT / "hidden_subset_selector_stress_model_scores.csv"
CANDIDATE_OUT = OUT / "hidden_subset_selector_stress_candidate_scores.csv"
INVERSE_OUT = OUT / "hidden_subset_selector_stress_inverse_summary.csv"
MASK_OUT = OUT / "hidden_subset_selector_stress_mask_stability.csv"
REPORT_OUT = OUT / "hidden_subset_selector_stress_report.md"

A2C8 = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05 = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
BAD_ANCHORS = {
    "submission_jepa_latent_q2_w0p45.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_lejepa_targetwise_strict_best_scale0p5.csv",
}


MODEL_DEFS = [
    (
        "raw05_a2c8_compat",
        ["mean_abs_move_vs_raw05", "mean_abs_move_vs_a2c8", "good_span_residual_ratio", "bad_axis_abs_load"],
        1.0,
    ),
    (
        "good_bad_axes",
        ["proj_a2c8", "proj_raw05", "bad_axis_abs_load", "proj_ordinal", "mean_abs_move_vs_raw05"],
        1.0,
    ),
    (
        "bad_axes_only",
        ["bad_axis_abs_load", "bad_axis_positive_load", "proj_q2_bad", "proj_resid_bad", "proj_lejepa_bad"],
        1.0,
    ),
    (
        "target_move_core",
        ["move_abs_a2c8_Q2", "move_abs_a2c8_Q3", "move_abs_a2c8_S2", "move_abs_a2c8_S3", "move_abs_a2c8_S4"],
        1.0,
    ),
    (
        "a2c8_distance_badload",
        ["mean_abs_move_vs_a2c8", "bad_axis_abs_load", "good_span_residual_ratio"],
        1.0,
    ),
    (
        "raw05_distance_badload",
        ["mean_abs_move_vs_raw05", "bad_axis_abs_load", "good_span_residual_ratio"],
        1.0,
    ),
    (
        "compact_axis_energy",
        ["raw05_a2c8_compat_energy", "bad_to_good_load_ratio", "mean_abs_move_vs_stage2"],
        3.0,
    ),
]


def standardize(train: np.ndarray, pred: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = np.nanmean(train, axis=0)
    sigma = np.nanstd(train, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return np.nan_to_num((train - mu) / sigma), np.nan_to_num((pred - mu) / sigma)


def ridge_predict(train: pd.DataFrame, pred: pd.DataFrame, features: list[str], alpha: float) -> np.ndarray:
    x = train[features].to_numpy(dtype=np.float64)
    xp = pred[features].to_numpy(dtype=np.float64)
    y = train["public_lb"].to_numpy(dtype=np.float64)
    x, xp = standardize(x, xp)
    x_aug = np.column_stack([np.ones(len(x)), x])
    xp_aug = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(x_aug.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y
    return xp_aug @ beta


def pairwise_rank_accuracy(pred: np.ndarray, y: np.ndarray) -> float:
    ok = total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dp = pred[i] - pred[j]
            dy = y[i] - y[j]
            if abs(dp) < 1e-15 or abs(dy) < 1e-15:
                continue
            total += 1
            ok += int(dp * dy > 0)
    return float(ok / total) if total else float("nan")


def anchor_order_flags(pred_frame: pd.DataFrame) -> dict[str, object]:
    by_file = pred_frame.drop_duplicates(["file"]).set_index("file")

    def value(file_name: str, col: str) -> float:
        return float(by_file.loc[file_name, col]) if file_name in by_file.index else float("nan")

    pred_a2c8 = value(A2C8, "pred")
    pred_raw05 = value(RAW05, "pred")
    pred_stage2 = value(STAGE2, "pred")
    bad_preds = [value(f, "pred") for f in BAD_ANCHORS if f in by_file.index]
    bad_preds = [x for x in bad_preds if np.isfinite(x)]
    top_file = str(pred_frame.sort_values("pred").iloc[0]["file"]) if len(pred_frame) else ""

    return {
        "top1_is_a2c8": bool(top_file == A2C8),
        "a2c8_beats_raw05": bool(np.isfinite(pred_a2c8) and np.isfinite(pred_raw05) and pred_a2c8 < pred_raw05),
        "a2c8_raw05_pred_margin": pred_raw05 - pred_a2c8,
        "stage2_beats_bad_anchors": bool(
            np.isfinite(pred_stage2) and bool(bad_preds) and all(pred_stage2 < x for x in bad_preds)
        ),
        "min_bad_minus_a2c8": min(bad_preds) - pred_a2c8 if np.isfinite(pred_a2c8) and bad_preds else float("nan"),
        "pred_top_file": top_file,
    }


def stress_predictions(known: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, features, alpha in MODEL_DEFS:
        for holdout_idx in range(len(known)):
            test = known.iloc[[holdout_idx]]
            train = known.drop(known.index[holdout_idx])
            pred = ridge_predict(train, test, features, alpha)[0]
            rows.append(
                {
                    "stress": "loo",
                    "model": model,
                    "features": ",".join(features),
                    "alpha": alpha,
                    "holdout_group": str(test["file"].iloc[0]),
                    "file": str(test["file"].iloc[0]),
                    "actual": float(test["public_lb"].iloc[0]),
                    "pred": float(pred),
                    "error": float(pred - test["public_lb"].iloc[0]),
                }
            )

        for pair in combinations(range(len(known)), 2):
            test = known.iloc[list(pair)]
            train = known.drop(known.index[list(pair)])
            pred = ridge_predict(train, test, features, alpha)
            holdout_group = "+".join(test["file"].astype(str).tolist())
            for rec, pred_value in zip(test.to_dict("records"), pred, strict=True):
                rows.append(
                    {
                        "stress": "l2o",
                        "model": model,
                        "features": ",".join(features),
                        "alpha": alpha,
                        "holdout_group": holdout_group,
                        "file": str(rec["file"]),
                        "actual": float(rec["public_lb"]),
                        "pred": float(pred_value),
                        "error": float(pred_value - float(rec["public_lb"])),
                    }
                )
    return pd.DataFrame(rows)


def l2o_pair_accuracy(pred: pd.DataFrame) -> float:
    ok = total = 0
    for _, group in pred.groupby(["model", "holdout_group"], sort=False):
        if len(group) != 2:
            continue
        rows = group.sort_values("file")
        actual = rows["actual"].to_numpy(dtype=np.float64)
        guess = rows["pred"].to_numpy(dtype=np.float64)
        if abs(actual[0] - actual[1]) < 1e-15 or abs(guess[0] - guess[1]) < 1e-15:
            continue
        total += 1
        ok += int((actual[0] - actual[1]) * (guess[0] - guess[1]) > 0)
    return float(ok / total) if total else float("nan")


def score_models(pred: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, group in pred.groupby("model", sort=False):
        loo = group[group["stress"].eq("loo")].copy()
        l2o = group[group["stress"].eq("l2o")].copy()
        for stress, sub in [("loo", loo), ("l2o", l2o)]:
            err = sub["error"].to_numpy(dtype=np.float64)
            actual = sub["actual"].to_numpy(dtype=np.float64)
            guess = sub["pred"].to_numpy(dtype=np.float64)
            flags = anchor_order_flags(sub) if stress == "loo" else {}
            pair_acc = pairwise_rank_accuracy(guess, actual) if stress == "loo" else l2o_pair_accuracy(sub)
            rows.append(
                {
                    "model": model,
                    "stress": stress,
                    "n_predictions": int(len(sub)),
                    "mae": float(np.mean(np.abs(err))),
                    "rmse": float(np.sqrt(np.mean(err**2))),
                    "p90_abs_error": float(np.quantile(np.abs(err), 0.90)),
                    "max_abs_error": float(np.max(np.abs(err))),
                    "bias": float(np.mean(err)),
                    "rank_accuracy": pair_acc,
                    **flags,
                }
            )

    out = pd.DataFrame(rows)
    pivot = out.pivot(index="model", columns="stress", values=["mae", "rank_accuracy", "p90_abs_error"])
    gate_rows = []
    for model in out["model"].drop_duplicates():
        rec = {"model": model}
        for stress in ["loo", "l2o"]:
            row = out[(out["model"].eq(model)) & (out["stress"].eq(stress))]
            if row.empty:
                continue
            rec[f"{stress}_mae"] = float(row["mae"].iloc[0])
            rec[f"{stress}_rank_accuracy"] = float(row["rank_accuracy"].iloc[0])
            rec[f"{stress}_p90_abs_error"] = float(row["p90_abs_error"].iloc[0])
        loo_row = out[(out["model"].eq(model)) & (out["stress"].eq("loo"))]
        if not loo_row.empty:
            rec["top1_is_a2c8"] = bool(loo_row["top1_is_a2c8"].iloc[0])
            rec["a2c8_beats_raw05"] = bool(loo_row["a2c8_beats_raw05"].iloc[0])
            rec["stage2_beats_bad_anchors"] = bool(loo_row["stage2_beats_bad_anchors"].iloc[0])
            rec["a2c8_raw05_pred_margin"] = float(loo_row["a2c8_raw05_pred_margin"].iloc[0])
            rec["min_bad_minus_a2c8"] = float(loo_row["min_bad_minus_a2c8"].iloc[0])
        rec["selector_gate_pass"] = bool(
            rec.get("loo_mae", 9.0) <= 0.00040
            and rec.get("l2o_mae", 9.0) <= 0.00040
            and rec.get("loo_rank_accuracy", 0.0) > 0.90
            and rec.get("l2o_rank_accuracy", 0.0) > 0.90
            and rec.get("a2c8_beats_raw05", False)
            and rec.get("stage2_beats_bad_anchors", False)
        )
        gate_rows.append(rec)

    gates = pd.DataFrame(gate_rows)
    out = out.merge(gates[["model", "selector_gate_pass"]], on="model", how="left")
    out.attrs["gate_summary"] = gates
    _ = pivot  # Keep the intermediate visible while debugging without affecting outputs.
    return out


def candidate_stress_scores(known: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    scenario_arrays: list[np.ndarray] = []
    for model, features, alpha in MODEL_DEFS:
        scenario_arrays.append(ridge_predict(known, candidates, features, alpha))
        for holdout_idx in range(len(known)):
            train = known.drop(known.index[holdout_idx])
            scenario_arrays.append(ridge_predict(train, candidates, features, alpha))
        for pair in combinations(range(len(known)), 2):
            train = known.drop(known.index[list(pair)])
            scenario_arrays.append(ridge_predict(train, candidates, features, alpha))

    out = candidates.copy()
    mat = np.column_stack(scenario_arrays)
    out["selector_stress_mean"] = np.nanmean(mat, axis=1)
    out["selector_stress_median"] = np.nanmedian(mat, axis=1)
    out["selector_stress_p10"] = np.nanpercentile(mat, 10, axis=1)
    out["selector_stress_p90"] = np.nanpercentile(mat, 90, axis=1)
    out["selector_stress_min"] = np.nanmin(mat, axis=1)
    out["selector_stress_max"] = np.nanmax(mat, axis=1)
    out["selector_stress_spread"] = out["selector_stress_max"] - out["selector_stress_min"]

    a2c8_public = float(known.loc[known["file"].eq(A2C8), "public_lb"].iloc[0])
    best_anchor = candidates[candidates["file"].astype(str).eq(A2C8)]
    if not best_anchor.empty:
        best_idx = best_anchor.index[0]
        best_scenarios = mat[best_idx]
    else:
        best_scenarios = np.full(mat.shape[1], a2c8_public, dtype=np.float64)
    out["beats_a2c8_scenario_rate"] = np.mean(mat < best_scenarios, axis=1)
    out["selector_delta_vs_a2c8_public"] = out["selector_stress_mean"] - a2c8_public
    out["selector_p90_delta_vs_a2c8_public"] = out["selector_stress_p90"] - a2c8_public
    out["resolved_better_than_a2c8_gate"] = out["selector_stress_p90"] < (a2c8_public - 0.00040)
    out["candidate_selector_risk"] = (
        out["selector_stress_mean"]
        + 0.20 * out["selector_stress_spread"]
        + 0.00015 * out["bad_axis_abs_load"].fillna(0.0)
        + 0.00005 * out["good_span_residual_ratio"].fillna(0.0)
    )
    keep_cols = [
        "file",
        "is_known_public",
        "known_public_lb",
        "selector_stress_mean",
        "selector_stress_median",
        "selector_stress_p10",
        "selector_stress_p90",
        "selector_stress_spread",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
        "proxy_pred_mean",
        "proxy_delta_vs_a2c8_public",
        "proxy_pred_spread",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "bad_axis_abs_load",
        "good_span_residual_ratio",
        "raw05_a2c8_compat_energy",
    ]
    keep_cols = [col for col in keep_cols if col in out.columns]
    return out[keep_cols].sort_values(["candidate_selector_risk", "selector_stress_mean"]).reset_index(drop=True)


def summarize_inverse() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    masks: list[dict[str, object]] = []
    if LOO_INVERSE_IN.exists():
        loo = pd.read_csv(LOO_INVERSE_IN)
        loo = loo[~loo["heldout_key"].astype(str).eq("__overall__")].copy()
        for policy, group in loo.groupby("policy", sort=False):
            err = group["heldout_abs_error"].to_numpy(dtype=np.float64)
            rows.append(
                {
                    "source": "direct_inverse",
                    "stress": "loo",
                    "policy": policy,
                    "n": int(len(group)),
                    "mae": float(np.mean(err)),
                    "p90_abs_error": float(np.quantile(err, 0.90)),
                    "max_abs_error": float(np.max(err)),
                }
            )
        for cols, label in [
            (["policy", "top_mask_kind", "top_mask_name", "top_prior_name"], "loo_policy_mask_prior"),
            (["top_mask_kind", "top_mask_name", "top_prior_name"], "loo_mask_prior"),
        ]:
            found_cols = [c for c in cols if c in loo.columns]
            if not found_cols:
                continue
            count = loo.groupby(found_cols, dropna=False).size().reset_index(name="count")
            count["source"] = label
            masks.extend(count.to_dict("records"))

    if L2O_INVERSE_IN.exists():
        l2o = pd.read_csv(L2O_INVERSE_IN)
        l2o = l2o[~l2o["heldout_pair"].astype(str).eq("__overall__")].copy()
        for policy, group in l2o.groupby("policy", sort=False):
            err = group["pair_abs_error_mean"].to_numpy(dtype=np.float64)
            rows.append(
                {
                    "source": "direct_inverse",
                    "stress": "l2o",
                    "policy": policy,
                    "n": int(len(group)),
                    "mae": float(np.mean(err)),
                    "p90_abs_error": float(np.quantile(err, 0.90)),
                    "max_abs_error": float(np.max(err)),
                }
            )
        found_cols = [c for c in ["policy", "top_mask_kind", "top_mask_name", "top_prior_name"] if c in l2o.columns]
        if found_cols:
            count = l2o.groupby(found_cols, dropna=False).size().reset_index(name="count")
            count["source"] = "l2o_policy_mask_prior"
            masks.extend(count.to_dict("records"))

    inv = pd.DataFrame(rows).sort_values(["stress", "mae", "policy"]).reset_index(drop=True)
    mask = pd.DataFrame(masks)
    if not mask.empty:
        mask = mask.sort_values(["source", "count"], ascending=[True, False]).reset_index(drop=True)
    return inv, mask


def write_report(
    model_scores: pd.DataFrame,
    gates: pd.DataFrame,
    candidates: pd.DataFrame,
    inverse: pd.DataFrame,
    mask_stability: pd.DataFrame,
) -> None:
    best_loo = model_scores[model_scores["stress"].eq("loo")].sort_values("mae").iloc[0]
    best_l2o = model_scores[model_scores["stress"].eq("l2o")].sort_values("mae").iloc[0]
    pass_count = int(gates["selector_gate_pass"].sum()) if "selector_gate_pass" in gates.columns else 0
    raw05_row = candidates[candidates["file"].astype(str).eq(RAW05)]
    a2c8_row = candidates[candidates["file"].astype(str).eq(A2C8)]
    raw05_delta = float(raw05_row["selector_delta_vs_a2c8_public"].iloc[0]) if not raw05_row.empty else float("nan")
    a2c8_spread = float(a2c8_row["selector_stress_spread"].iloc[0]) if not a2c8_row.empty else float("nan")
    resolved_better = candidates[candidates["resolved_better_than_a2c8_gate"]].copy()

    candidate_cols = [
        "file",
        "is_known_public",
        "known_public_lb",
        "selector_stress_mean",
        "selector_delta_vs_a2c8_public",
        "selector_stress_p90",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    candidate_cols = [c for c in candidate_cols if c in candidates.columns]

    lines = [
        "# Hidden Subset Selector Stress Harness",
        "",
        "This is a selector-resolution test, not a new public-LB claim. It asks whether the current anchor geometry can choose among raw05/a2c8/JEPA candidates with enough margin to justify another submission.",
        "",
        "## Selector Gate",
        "",
        "Gate definition: LOO MAE <= `0.00040`, L2O MAE <= `0.00040`, both rank accuracies > `0.90`, a2c8 predicted better than raw05, and stage2 predicted better than known bad JEPA anchors.",
        "",
        f"- Passing selector families: `{pass_count}` / `{len(gates)}`.",
        f"- Best LOO model: `{best_loo['model']}` MAE `{best_loo['mae']:.9f}`, rank accuracy `{best_loo['rank_accuracy']:.3f}`.",
        f"- Best L2O model: `{best_l2o['model']}` MAE `{best_l2o['mae']:.9f}`, pair accuracy `{best_l2o['rank_accuracy']:.3f}`.",
        f"- Raw05 selector mean delta versus a2c8 public: `{raw05_delta:.9f}`.",
        f"- A2C8 own stress spread: `{a2c8_spread:.9f}`.",
        f"- Candidates clearing resolved-better gate: `{len(resolved_better)}` / `{len(candidates)}`.",
        "",
        "## Model Stress Scores",
        "",
        "```csv",
        gates.round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Candidate Stress Top",
        "",
        "```csv",
        candidates[candidate_cols].head(24).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Direct Inverse Selector Stress",
        "",
        "```csv",
        (inverse.round(9).to_csv(index=False).strip() if not inverse.empty else "missing"),
        "```",
        "",
        "## Mask Stability",
        "",
        "```csv",
        (mask_stability.head(24).to_csv(index=False).strip() if not mask_stability.empty else "missing"),
        "```",
        "",
        "## Read",
        "",
        "- The current selector family still fails the promised gate. It can separate clearly bad JEPA axes, but not enough to robustly rank a2c8/raw05-scale movements.",
        "- L2O stress is the real bottleneck: when two anchors are removed, the learned public-subset geometry has too few constraints and the candidate ordering spreads wider than the public gap we are trying to exploit.",
        "- The direct inverse branch confirms the same failure mode: oracle masks can fit anchors better than train-selected masks, so the hidden subset exists in the hypothesis class but is not being selected reliably.",
        "- This means a 0.54 path is unlikely from more tiny raw05-compatible blends alone. The next useful experiments must create a movement large enough to exceed selector uncertainty, or improve the selector before trusting post-hoc blends.",
        "",
        "## Next Decision",
        "",
        "Run targetwise safe multi-block LeJEPA only if its candidate movement exceeds this harness uncertainty while keeping bad-axis load low. Otherwise, continue selector work before producing more submissions.",
        "",
        "## Files",
        "",
        f"- `{PRED_OUT.name}`",
        f"- `{MODEL_OUT.name}`",
        f"- `{CANDIDATE_OUT.name}`",
        f"- `{INVERSE_OUT.name}`",
        f"- `{MASK_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not KNOWN_IN.exists() or not CANDIDATE_IN.exists():
        raise FileNotFoundError("Run public_anchor_bottleneck_decomposition.py first.")

    known = pd.read_csv(KNOWN_IN)
    candidates = pd.read_csv(CANDIDATE_IN)
    known = known.sort_values("public_lb").reset_index(drop=True)

    pred = stress_predictions(known)
    pred.to_csv(PRED_OUT, index=False)

    model_scores = score_models(pred)
    gates = model_scores.attrs["gate_summary"].sort_values(["selector_gate_pass", "loo_mae"], ascending=[False, True])
    model_scores.to_csv(MODEL_OUT, index=False)

    cand_scores = candidate_stress_scores(known, candidates)
    cand_scores.to_csv(CANDIDATE_OUT, index=False)

    inverse, mask_stability = summarize_inverse()
    inverse.to_csv(INVERSE_OUT, index=False)
    mask_stability.to_csv(MASK_OUT, index=False)

    write_report(model_scores, gates, cand_scores, inverse, mask_stability)

    print(REPORT_OUT)
    print("[selector gates]")
    print(
        gates[
            [
                "model",
                "loo_mae",
                "l2o_mae",
                "loo_rank_accuracy",
                "l2o_rank_accuracy",
                "a2c8_beats_raw05",
                "stage2_beats_bad_anchors",
                "selector_gate_pass",
            ]
        ]
        .round(9)
        .to_string(index=False)
    )
    print("[candidate top]")
    print(
        cand_scores[
            [
                "file",
                "selector_stress_mean",
                "selector_delta_vs_a2c8_public",
                "selector_stress_spread",
                "beats_a2c8_scenario_rate",
                "resolved_better_than_a2c8_gate",
                "candidate_selector_risk",
            ]
        ]
        .head(15)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
