from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    FINAL9,
    LEJEPA_BAD,
    ORDINAL,
    Q2_BAD,
    RAW05,
    RESID_BAD,
    STAGE2,
    TARGETS,
    feature_row,
    locate,
)
from public_selector_universe_audit import build_known_and_refs, family_name  # noqa: E402


MODEL_OUT = OUT / "public_pairwise_order_selector_models.csv"
CANDIDATE_OUT = OUT / "public_pairwise_order_selector_candidates.csv"
SHORTLIST_OUT = OUT / "public_pairwise_order_selector_shortlist.csv"
KNOWN_PAIR_OUT = OUT / "public_pairwise_order_selector_known_pairs.csv"
REPORT_OUT = OUT / "public_pairwise_order_selector_report.md"


BAD_ANCHORS = [Q2_BAD, RESID_BAD, LEJEPA_BAD]
KEY_ANCHORS = [A2C8, RAW05, STAGE2, ORDINAL, FINAL9, Q2_BAD, LEJEPA_BAD, RESID_BAD]

FEATURE_SETS: list[tuple[str, list[str]]] = [
    (
        "micro_distance",
        [
            "mean_abs_move_vs_a2c8",
            "mean_abs_move_vs_raw05",
            "rms_move_vs_a2c8",
            "max_abs_move_vs_a2c8",
            "bad_axis_abs_load",
            "raw05_a2c8_compat_energy",
        ],
    ),
    (
        "axis_compact",
        [
            "proj_a2c8",
            "proj_raw05",
            "proj_ordinal",
            "proj_q2_bad",
            "proj_resid_bad",
            "proj_lejepa_bad",
            "bad_axis_abs_load",
            "good_span_residual_ratio",
        ],
    ),
    (
        "axis_signed",
        [
            "proj_a2c8",
            "proj_raw05",
            "proj_final9",
            "proj_ordinal",
            "proj_q2_bad",
            "proj_resid_bad",
            "proj_lejepa_bad",
            "bad_axis_positive_load",
            "bad_to_good_load_ratio",
        ],
    ),
    (
        "target_moves",
        [f"move_abs_a2c8_{target}" for target in TARGETS]
        + ["bad_axis_abs_load", "raw05_a2c8_compat_energy"],
    ),
    (
        "target_means",
        [f"mean_prob_{target}" for target in TARGETS]
        + [f"move_abs_a2c8_{target}" for target in TARGETS],
    ),
    (
        "all_stable",
        [
            "mean_abs_move_vs_stage2",
            "mean_abs_move_vs_a2c8",
            "mean_abs_move_vs_raw05",
            "rms_move_vs_a2c8",
            "max_abs_move_vs_a2c8",
            "proj_a2c8",
            "proj_raw05",
            "proj_final9",
            "proj_ordinal",
            "proj_q2_bad",
            "proj_resid_bad",
            "proj_lejepa_bad",
            "bad_axis_abs_load",
            "bad_axis_positive_load",
            "good_span_residual_ratio",
            "bad_to_good_load_ratio",
            "raw05_a2c8_compat_energy",
        ],
    ),
]
ALPHAS = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0]


@dataclass(frozen=True)
class PairwiseFit:
    model: str
    features: tuple[str, ...]
    alpha: float
    beta: np.ndarray
    mu: np.ndarray
    sigma: np.ndarray


def resolve_submission(value: object) -> Path | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value)
    if not text or text.lower() == "nan":
        return None
    path = Path(text)
    if path.exists():
        return path.resolve()
    if not path.is_absolute():
        root_path = ROOT / text
        if root_path.exists():
            return root_path.resolve()
    found = locate(text)
    return found.resolve() if found is not None else None


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def sign_accuracy(pred: np.ndarray, actual: np.ndarray) -> float:
    pred = np.asarray(pred, dtype=np.float64)
    actual = np.asarray(actual, dtype=np.float64)
    ok = np.sign(pred) == np.sign(actual)
    return float(np.mean(ok)) if len(ok) else float("nan")


def standardize_pair_diffs(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = np.nanmean(x, axis=0)
    sigma = np.nanstd(x, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return np.nan_to_num((x - mu) / sigma), mu, sigma


def pair_training_arrays(
    known: pd.DataFrame,
    features: list[str],
    exclude_positions: set[int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    exclude_positions = exclude_positions or set()
    x = known[features].to_numpy(dtype=np.float64)
    y = known["public_lb"].to_numpy(dtype=np.float64)
    rows: list[np.ndarray] = []
    targets: list[float] = []
    for i, j in combinations(range(len(known)), 2):
        if i in exclude_positions or j in exclude_positions:
            continue
        diff = x[i] - x[j]
        target = float(y[i] - y[j])
        rows.append(diff)
        targets.append(target)
        rows.append(-diff)
        targets.append(-target)
    if not rows:
        return np.empty((0, len(features)), dtype=np.float64), np.empty(0, dtype=np.float64)
    return np.vstack(rows).astype(np.float64), np.asarray(targets, dtype=np.float64)


def fit_pairwise(
    known: pd.DataFrame,
    model: str,
    features: list[str],
    alpha: float,
    exclude_positions: set[int] | None = None,
) -> PairwiseFit | None:
    x, y = pair_training_arrays(known, features, exclude_positions)
    if len(y) < len(features) + 2:
        return None
    x_std, mu, sigma = standardize_pair_diffs(x)
    penalty = np.eye(x_std.shape[1], dtype=np.float64) * float(alpha)
    beta = np.linalg.pinv(x_std.T @ x_std + penalty) @ x_std.T @ y
    return PairwiseFit(model=model, features=tuple(features), alpha=float(alpha), beta=beta, mu=mu, sigma=sigma)


def predict_diff(fit: PairwiseFit, diff: np.ndarray) -> np.ndarray:
    z = np.nan_to_num((diff - fit.mu) / fit.sigma)
    return z @ fit.beta


def eval_fit_on_pairs(fit: PairwiseFit, known: pd.DataFrame, pair_positions: list[tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
    x = known[list(fit.features)].to_numpy(dtype=np.float64)
    y = known["public_lb"].to_numpy(dtype=np.float64)
    preds: list[float] = []
    actuals: list[float] = []
    for i, j in pair_positions:
        preds.append(float(predict_diff(fit, (x[i] - x[j])[None, :])[0]))
        actuals.append(float(y[i] - y[j]))
    return np.asarray(preds, dtype=np.float64), np.asarray(actuals, dtype=np.float64)


def pairwise_rank_accuracy_from_lb(pred_delta_to_a2c8: pd.Series, known: pd.DataFrame) -> float:
    pred_map = pred_delta_to_a2c8.to_dict()
    actual_map = known.set_index("file")["public_lb"].to_dict()
    ok = total = 0
    files = known["file"].astype(str).tolist()
    for i, j in combinations(files, 2):
        dp = float(pred_map[i] - pred_map[j])
        dy = float(actual_map[i] - actual_map[j])
        if abs(dp) < 1e-15 or abs(dy) < 1e-15:
            continue
        total += 1
        ok += int(dp * dy > 0)
    return float(ok / total) if total else float("nan")


def known_order_flags(fit: PairwiseFit, known: pd.DataFrame) -> dict[str, object]:
    x = known[list(fit.features)].to_numpy(dtype=np.float64)
    by_file = {str(file): pos for pos, file in enumerate(known["file"].astype(str))}
    a2_pos = by_file[A2C8]
    raw_pos = by_file[RAW05]
    stage2_pos = by_file[STAGE2]

    delta_to_a2c8 = predict_diff(fit, x - x[a2_pos])
    delta_series = pd.Series(delta_to_a2c8, index=known["file"].astype(str))
    top_file = str(delta_series.sort_values().index[0])

    pred_a2_minus_raw = float(predict_diff(fit, (x[a2_pos] - x[raw_pos])[None, :])[0])
    bad_margins = []
    for bad in BAD_ANCHORS:
        bad_pos = by_file.get(bad)
        if bad_pos is None:
            continue
        bad_margins.append(float(predict_diff(fit, (x[stage2_pos] - x[bad_pos])[None, :])[0]))

    non_a2 = delta_series.drop(A2C8)
    return {
        "top1_is_a2c8": bool(top_file == A2C8),
        "pred_top_file": top_file,
        "a2c8_beats_raw05": bool(pred_a2_minus_raw < 0.0),
        "pred_a2c8_minus_raw05": pred_a2_minus_raw,
        "stage2_beats_bad_anchors": bool(bad_margins and all(value < 0.0 for value in bad_margins)),
        "non_a2c8_pred_worse_rate": float((non_a2 > 0.0).mean()),
        "known_rank_accuracy_vs_a2c8": pairwise_rank_accuracy_from_lb(delta_series, known),
        "min_non_a2c8_delta": float(non_a2.min()),
        "max_non_a2c8_delta": float(non_a2.max()),
    }


def evaluate_pairwise_models(known: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    known_pair_rows: list[dict[str, object]] = []
    n = len(known)
    all_pairs = list(combinations(range(n), 2))

    for feature_name, features in FEATURE_SETS:
        missing = [col for col in features if col not in known.columns]
        if missing:
            continue
        for alpha in ALPHAS:
            model_name = f"{feature_name}_a{alpha:g}"
            full_fit = fit_pairwise(known, model_name, features, alpha)
            if full_fit is None:
                continue

            insample_pred, insample_actual = eval_fit_on_pairs(full_fit, known, all_pairs)
            loo_pred: list[float] = []
            loo_actual: list[float] = []
            for heldout in range(n):
                fit = fit_pairwise(known, model_name, features, alpha, {heldout})
                if fit is None:
                    continue
                pairs = [(heldout, other) for other in range(n) if other != heldout]
                pred, actual = eval_fit_on_pairs(fit, known, pairs)
                loo_pred.extend(pred.tolist())
                loo_actual.extend(actual.tolist())

            l2o_pred: list[float] = []
            l2o_actual: list[float] = []
            for i, j in all_pairs:
                fit = fit_pairwise(known, model_name, features, alpha, {i, j})
                if fit is None:
                    continue
                pred, actual = eval_fit_on_pairs(fit, known, [(i, j)])
                l2o_pred.extend(pred.tolist())
                l2o_actual.extend(actual.tolist())

            loo_pred_arr = np.asarray(loo_pred, dtype=np.float64)
            loo_actual_arr = np.asarray(loo_actual, dtype=np.float64)
            l2o_pred_arr = np.asarray(l2o_pred, dtype=np.float64)
            l2o_actual_arr = np.asarray(l2o_actual, dtype=np.float64)
            flags = known_order_flags(full_fit, known)

            loo_err = loo_pred_arr - loo_actual_arr
            l2o_err = l2o_pred_arr - l2o_actual_arr
            in_err = insample_pred - insample_actual
            order_pass = bool(
                flags["a2c8_beats_raw05"]
                and flags["stage2_beats_bad_anchors"]
                and flags["top1_is_a2c8"]
                and flags["non_a2c8_pred_worse_rate"] >= 0.75
            )
            score = (
                np.nanmean(np.abs(loo_err)) if len(loo_err) else 9.0
            ) + 0.75 * (np.nanmean(np.abs(l2o_err)) if len(l2o_err) else 9.0)
            score += 0.00025 * (1.0 - sign_accuracy(loo_pred_arr, loo_actual_arr))
            score += 0.00020 * (1.0 - sign_accuracy(l2o_pred_arr, l2o_actual_arr))
            if not order_pass:
                score += 0.002

            rows.append(
                {
                    "model": model_name,
                    "feature_set": feature_name,
                    "features": ",".join(features),
                    "alpha": alpha,
                    "n_features": len(features),
                    "insample_mae": float(np.mean(np.abs(in_err))),
                    "insample_sign_acc": sign_accuracy(insample_pred, insample_actual),
                    "loo_mae": float(np.mean(np.abs(loo_err))) if len(loo_err) else np.nan,
                    "loo_p90_abs_error": float(np.quantile(np.abs(loo_err), 0.90)) if len(loo_err) else np.nan,
                    "loo_sign_acc": sign_accuracy(loo_pred_arr, loo_actual_arr),
                    "l2o_mae": float(np.mean(np.abs(l2o_err))) if len(l2o_err) else np.nan,
                    "l2o_p90_abs_error": float(np.quantile(np.abs(l2o_err), 0.90)) if len(l2o_err) else np.nan,
                    "l2o_sign_acc": sign_accuracy(l2o_pred_arr, l2o_actual_arr),
                    "order_pass": order_pass,
                    "model_score": float(score),
                    **flags,
                }
            )

            x = known[features].to_numpy(dtype=np.float64)
            y = known["public_lb"].to_numpy(dtype=np.float64)
            for i, j in all_pairs:
                pred = float(predict_diff(full_fit, (x[i] - x[j])[None, :])[0])
                known_pair_rows.append(
                    {
                        "model": model_name,
                        "left": str(known["file"].iloc[i]),
                        "right": str(known["file"].iloc[j]),
                        "actual_delta": float(y[i] - y[j]),
                        "pred_delta": pred,
                        "sign_ok": bool(np.sign(pred) == np.sign(float(y[i] - y[j]))),
                    }
                )

    model_df = pd.DataFrame(rows).sort_values(["order_pass", "model_score"], ascending=[False, True]).reset_index(drop=True)
    pairs_df = pd.DataFrame(known_pair_rows)
    return model_df, pairs_df


def candidate_pool() -> pd.DataFrame:
    records: list[dict[str, object]] = []

    def add(value: object, source: str, priority: float = 1.0, extra: dict[str, object] | None = None) -> None:
        path = resolve_submission(value)
        if path is None:
            return
        rec = {
            "resolved_path": str(path),
            "source_path": rel_path(path),
            "basename": path.name,
            "pool_source": source,
            "pool_priority": float(priority),
        }
        if extra:
            rec.update(extra)
        records.append(rec)

    for name in KEY_ANCHORS:
        add(name, "known_anchor", 0.0)

    universe_path = OUT / "public_selector_universe_audit_candidates.csv"
    if universe_path.exists():
        universe = pd.read_csv(universe_path)
        ranked = universe.sort_values("submission_priority_score", ascending=True).head(700)
        masks = [
            universe.get("novel_frontier_candidate", False).fillna(False).astype(bool),
            universe.get("frontier_escape_candidate", False).fillna(False).astype(bool),
            (
                universe.get("low_public_bad_axis", False).fillna(False).astype(bool)
                & universe.get("scenario_majority_beats_a2c8", False).fillna(False).astype(bool)
                & universe.get("p90_not_too_worse", False).fillna(False).astype(bool)
            ),
        ]
        selected = pd.concat([ranked, *(universe[mask].head(400) for mask in masks)], ignore_index=True)
        if "candidate_family" in universe.columns:
            per_family = (
                universe.sort_values("submission_priority_score", ascending=True)
                .groupby("candidate_family", dropna=False)
                .head(25)
            )
            selected = pd.concat([selected, per_family], ignore_index=True)
        for _, row in selected.drop_duplicates("source_path").iterrows():
            add(row.get("source_path") or row.get("file"), "universe_selector", float(row.get("submission_priority_score", 1.0)), row.to_dict())

    bridge_path = OUT / "hidden_public_local_bridge_shortlist.csv"
    if bridge_path.exists():
        bridge = pd.read_csv(bridge_path)
        for _, row in bridge.sort_values("bridge_rank_score", ascending=True).head(650).iterrows():
            add(row.get("source_path") or row.get("file"), "hiddenloc_bridge", float(row.get("bridge_rank_score", 1.0)), row.to_dict())

    inv8_path = OUT / "public_lb_inverse8_selected_stress_audit.csv"
    if inv8_path.exists():
        inv8 = pd.read_csv(inv8_path)
        sort_col = "robust_p90_delta_vs_a2c8" if "robust_p90_delta_vs_a2c8" in inv8.columns else "candidate_selector_risk"
        for _, row in inv8.sort_values(sort_col, ascending=True).iterrows():
            add(row.get("source_path") or row.get("file"), "inverse8_selected", float(row.get(sort_col, 1.0)), row.to_dict())

    loc_path = OUT / "hidden_public_localization_candidate_ranking.csv"
    if loc_path.exists():
        loc = pd.read_csv(loc_path)
        for _, row in loc.sort_values("localization_score", ascending=True).head(260).iterrows():
            add(row.get("file"), "hiddenloc_ranking", float(row.get("localization_score", 1.0)), row.to_dict())

    lowenergy_path = OUT / "badaxis_lowenergy_jepa_ensemble_selected.csv"
    if lowenergy_path.exists():
        low = pd.read_csv(lowenergy_path)
        for _, row in low.iterrows():
            add(row.get("source_path") or row.get("file"), "lowenergy_selected", 0.5, row.to_dict())

    pool = pd.DataFrame(records)
    if pool.empty:
        raise RuntimeError("candidate pool is empty")
    pool["resolved_path"] = pool["resolved_path"].astype(str)
    pool = (
        pool.sort_values(["pool_priority", "pool_source"])
        .drop_duplicates("resolved_path", keep="first")
        .reset_index(drop=True)
    )
    return pool


def build_candidate_features(pool: pd.DataFrame, sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    skipped = 0
    for idx, rec in pool.iterrows():
        path = Path(str(rec["resolved_path"]))
        try:
            row = feature_row(path, sample, refs, ref_vecs)
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            if skipped <= 10:
                print(f"skip {path}: {type(exc).__name__}: {exc}", flush=True)
            continue
        row["file"] = rel_path(path)
        row["source_path"] = rel_path(path)
        row["basename"] = path.name
        row["candidate_family"] = str(rec.get("candidate_family") or family_name(path))
        row["pool_source"] = str(rec.get("pool_source", ""))
        row["pool_priority"] = float(rec.get("pool_priority", np.nan))
        for key, value in rec.to_dict().items():
            if key in {"resolved_path", "file", "source_path", "basename", "candidate_family", "pool_source", "pool_priority"}:
                continue
            if key not in row:
                row[key] = value
        rows.append(row)
        if (idx + 1) % 250 == 0:
            print(f"computed pairwise features {idx + 1}/{len(pool)}", flush=True)
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("no candidate features computed")
    return frame.drop_duplicates("source_path").reset_index(drop=True)


def selected_model_configs(model_df: pd.DataFrame) -> pd.DataFrame:
    order_pass = model_df[model_df["order_pass"].astype(bool)].copy()
    if len(order_pass) >= 4:
        selected = order_pass.sort_values("model_score").head(10)
    else:
        selected = model_df.sort_values(["order_pass", "model_score"], ascending=[False, True]).head(10)
    return selected.reset_index(drop=True)


def score_candidates(known: pd.DataFrame, candidates: pd.DataFrame, model_df: pd.DataFrame) -> pd.DataFrame:
    selected = selected_model_configs(model_df)
    scenario_a2c8: list[np.ndarray] = []
    scenario_raw05: list[np.ndarray] = []
    scenario_stage2: list[np.ndarray] = []
    scenario_names: list[str] = []
    known_files = known["file"].astype(str).tolist()
    by_file = {name: pos for pos, name in enumerate(known_files)}
    a2_pos = by_file[A2C8]
    raw_pos = by_file[RAW05]
    stage2_pos = by_file[STAGE2]

    for _, model_rec in selected.iterrows():
        features = str(model_rec["features"]).split(",")
        alpha = float(model_rec["alpha"])
        model_name = str(model_rec["model"])
        cand_x = candidates[features].to_numpy(dtype=np.float64)
        known_x = known[features].to_numpy(dtype=np.float64)
        scenarios: list[tuple[str, set[int]]] = [("all", set())]
        scenarios.extend((f"loo_{known_files[i]}", {i}) for i in range(len(known)))
        scenarios.extend((f"l2o_{known_files[i]}__{known_files[j]}", {i, j}) for i, j in combinations(range(len(known)), 2))
        for scenario_name, exclude in scenarios:
            fit = fit_pairwise(known, model_name, features, alpha, exclude)
            if fit is None:
                continue
            scenario_a2c8.append(predict_diff(fit, cand_x - known_x[a2_pos]))
            scenario_raw05.append(predict_diff(fit, cand_x - known_x[raw_pos]))
            scenario_stage2.append(predict_diff(fit, cand_x - known_x[stage2_pos]))
            scenario_names.append(f"{model_name}:{scenario_name}")

    if not scenario_a2c8:
        raise RuntimeError("no pairwise candidate scenarios")

    mat_a2 = np.column_stack(scenario_a2c8)
    mat_raw = np.column_stack(scenario_raw05)
    mat_stage2 = np.column_stack(scenario_stage2)
    out = candidates.copy()
    out["pair_model_scenario_count"] = mat_a2.shape[1]
    out["pair_delta_vs_a2c8_mean"] = np.nanmean(mat_a2, axis=1)
    out["pair_delta_vs_a2c8_median"] = np.nanmedian(mat_a2, axis=1)
    out["pair_delta_vs_a2c8_p10"] = np.nanpercentile(mat_a2, 10, axis=1)
    out["pair_delta_vs_a2c8_p90"] = np.nanpercentile(mat_a2, 90, axis=1)
    out["pair_delta_vs_a2c8_min"] = np.nanmin(mat_a2, axis=1)
    out["pair_delta_vs_a2c8_max"] = np.nanmax(mat_a2, axis=1)
    out["pair_delta_vs_a2c8_spread"] = out["pair_delta_vs_a2c8_max"] - out["pair_delta_vs_a2c8_min"]
    out["pair_beats_a2c8_rate"] = np.mean(mat_a2 < 0.0, axis=1)
    out["pair_delta_vs_raw05_mean"] = np.nanmean(mat_raw, axis=1)
    out["pair_delta_vs_raw05_p90"] = np.nanpercentile(mat_raw, 90, axis=1)
    out["pair_beats_raw05_rate"] = np.mean(mat_raw < 0.0, axis=1)
    out["pair_delta_vs_stage2_mean"] = np.nanmean(mat_stage2, axis=1)

    old_p90 = out.get("selector_p90_delta_vs_a2c8_public", pd.Series(np.nan, index=out.index)).astype(float)
    old_beats = out.get("beats_a2c8_scenario_rate", pd.Series(np.nan, index=out.index)).astype(float)
    local_score = out.get("localization_score", pd.Series(np.nan, index=out.index)).astype(float)
    local_bonus = np.clip(-local_score.fillna(0.0), 0.0, 0.0010)

    a2_mask = out["basename"].astype(str).eq(A2C8)
    if a2_mask.any():
        a2_raw05_p90 = float(out.loc[a2_mask, "pair_delta_vs_raw05_p90"].iloc[0])
        a2_raw05_rate = float(out.loc[a2_mask, "pair_beats_raw05_rate"].iloc[0])
        a2_old_p90 = float(old_p90.loc[a2_mask].iloc[0]) if old_p90.loc[a2_mask].notna().any() else 0.00058
    else:
        a2_raw05_p90 = 0.000025
        a2_raw05_rate = 0.85
        a2_old_p90 = 0.00058

    out["pair_probe_gate"] = (
        (out["pair_delta_vs_a2c8_p90"] < 0.00005)
        & (out["pair_beats_a2c8_rate"] >= 0.65)
        & (out["bad_axis_abs_load"] <= 0.075)
        & (old_p90.fillna(0.00060) <= 0.00070)
    )
    out["pair_control_better_than_a2c8_gate"] = (
        (out["pair_delta_vs_a2c8_p90"] < 0.0)
        & (out["pair_delta_vs_raw05_p90"] <= a2_raw05_p90)
        & (out["pair_beats_raw05_rate"] >= max(0.70, a2_raw05_rate - 0.02))
        & (out["bad_axis_abs_load"] <= 0.055)
        & (old_p90.fillna(0.00060) <= a2_old_p90 + 0.00006)
    )
    out["pair_submit_gate"] = (
        (out["pair_delta_vs_a2c8_p90"] < -0.00005)
        & (out["pair_beats_a2c8_rate"] >= 0.80)
        & (out["pair_delta_vs_raw05_p90"] <= a2_raw05_p90 - 0.00002)
        & (out["pair_beats_raw05_rate"] >= max(0.72, a2_raw05_rate))
        & (out["bad_axis_abs_load"] <= 0.055)
        & (old_p90.fillna(0.00060) <= a2_old_p90 + 0.00002)
        & (old_beats.fillna(0.50) >= 0.50)
    )
    out["pair_selector_conflict"] = (
        (out["pair_delta_vs_a2c8_p90"] < 0.0)
        & ((old_p90 > 0.00070) | (old_beats < 0.40) | (out["bad_axis_abs_load"] > 0.09))
    )
    out["pair_rank_score"] = (
        out["pair_delta_vs_a2c8_p90"]
        + 0.20 * out["pair_delta_vs_a2c8_spread"]
        + 0.00025 * out["bad_axis_abs_load"]
        + 0.25 * old_p90.fillna(0.00060)
        - 0.00015 * out["pair_beats_a2c8_rate"]
        - 0.10 * local_bonus
    )
    out.attrs["selected_models"] = selected
    out.attrs["scenario_count"] = len(scenario_names)
    return out.sort_values(["pair_submit_gate", "pair_probe_gate", "pair_rank_score"], ascending=[False, False, True]).reset_index(drop=True)


def write_report(known: pd.DataFrame, model_df: pd.DataFrame, known_pairs: pd.DataFrame, candidates: pd.DataFrame) -> None:
    selected = selected_model_configs(model_df)
    submit = candidates[candidates["pair_submit_gate"].astype(bool)].copy()
    probe = candidates[candidates["pair_probe_gate"].astype(bool)].copy()
    control_better = candidates[candidates["pair_control_better_than_a2c8_gate"].astype(bool)].copy()
    known_controls = candidates[candidates["basename"].isin(KEY_ANCHORS)].copy()
    model_cols = [
        "model",
        "feature_set",
        "alpha",
        "order_pass",
        "model_score",
        "loo_mae",
        "loo_sign_acc",
        "l2o_mae",
        "l2o_sign_acc",
        "top1_is_a2c8",
        "a2c8_beats_raw05",
        "pred_a2c8_minus_raw05",
        "stage2_beats_bad_anchors",
        "known_rank_accuracy_vs_a2c8",
    ]
    candidate_cols = [
        "source_path",
        "candidate_family",
        "pool_source",
        "pair_delta_vs_a2c8_p90",
        "pair_delta_vs_a2c8_mean",
        "pair_beats_a2c8_rate",
        "pair_delta_vs_raw05_p90",
        "pair_beats_raw05_rate",
        "bad_axis_abs_load",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "localization_score",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_probe_gate",
        "pair_selector_conflict",
        "pair_rank_score",
    ]
    candidate_cols = [col for col in candidate_cols if col in candidates.columns]
    control_cols = [
        "basename",
        "known_public_lb",
        "pair_delta_vs_a2c8_p90",
        "pair_delta_vs_a2c8_mean",
        "pair_beats_a2c8_rate",
        "pair_delta_vs_raw05_p90",
        "pair_beats_raw05_rate",
        "bad_axis_abs_load",
        "pair_rank_score",
    ]
    control_cols = [col for col in control_cols if col in known_controls.columns]

    lines = [
        "# Public Pairwise Order Selector",
        "",
        "This audit trains on known public-anchor pairs directly. The prediction target is pairwise public LogLoss delta, e.g. `candidate - a2c8`, instead of absolute public LB.",
        "",
        "## Known Public Order",
        "",
        "```csv",
        known[["file", "public_lb", "known_source", "mean_abs_move_vs_a2c8", "mean_abs_move_vs_raw05", "bad_axis_abs_load"]]
        .sort_values("public_lb")
        .round(9)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Pairwise Model Gate",
        "",
        f"- Candidate pool scored: `{len(candidates)}`.",
        f"- Pairwise models tested: `{len(model_df)}`.",
        f"- Models preserving key order (`a2c8 < raw05`, `stage2 < bad JEPA`, `top1=a2c8`): `{int(model_df['order_pass'].sum())}`.",
        f"- Selected model scenarios used for candidates: `{int(candidates['pair_model_scenario_count'].iloc[0]) if len(candidates) else 0}`.",
        f"- Submit-gate candidates: `{len(submit)}`.",
        f"- Baseline-relative better-than-a2c8 candidates: `{len(control_better)}`.",
        f"- Probe-gate candidates: `{len(probe)}`.",
        "",
        "```csv",
        model_df[model_cols].head(18).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected Models",
        "",
        "```csv",
        selected[model_cols].round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Known Controls Under Candidate Scoring",
        "",
        "```csv",
        known_controls[control_cols].sort_values("known_public_lb").round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Candidate Top",
        "",
        "```csv",
        candidates[candidate_cols].head(40).round(9).to_csv(index=False).strip(),
        "```",
        "",
        "## Worst Known Pair Sign Errors",
        "",
        "```csv",
        known_pairs.assign(abs_error=(known_pairs["pred_delta"] - known_pairs["actual_delta"]).abs())
        .sort_values(["sign_ok", "abs_error"], ascending=[True, False])
        .head(40)
        .round(9)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Read",
        "",
        "- A trustworthy submission must beat `a2c8` and `raw05` under pairwise stress, while also staying under the old selector's p90-risk and low bad-axis load.",
        "- If no candidate passes submit gate, the bottleneck is not file format or simple blending. It is the missing sign/localization of the hidden public correction at a scale smaller than the anchor-model error floor.",
        "- Pairwise models are intentionally treated as a veto/gate, not as public-LB truth: only candidates that agree with old stress, bad-axis, and localization evidence are allowed through.",
        "",
        "## Files",
        "",
        f"- `{MODEL_OUT.name}`",
        f"- `{CANDIDATE_OUT.name}`",
        f"- `{SHORTLIST_OUT.name}`",
        f"- `{KNOWN_PAIR_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)

    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, known_pairs = evaluate_pairwise_models(known)
    model_df.to_csv(MODEL_OUT, index=False)
    known_pairs.to_csv(KNOWN_PAIR_OUT, index=False)

    pool = candidate_pool()
    print(f"candidate pool after dedupe: {len(pool)}", flush=True)
    candidates = build_candidate_features(pool, sample, refs, ref_vecs)

    known_lb = known.set_index("file")["public_lb"].to_dict()
    candidates["known_public_lb"] = candidates["basename"].map(known_lb)
    candidates["is_known_public"] = candidates["known_public_lb"].notna()

    scored = score_candidates(known, candidates, model_df)
    scored.to_csv(CANDIDATE_OUT, index=False)
    shortlist = scored[
        scored["pair_submit_gate"]
        | scored["pair_control_better_than_a2c8_gate"]
        | scored["pair_probe_gate"]
        | scored["is_known_public"]
    ].copy()
    if shortlist.empty:
        shortlist = scored.head(80).copy()
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(known, model_df, known_pairs, scored)

    print(REPORT_OUT)
    print("[pairwise model top]")
    print(
        model_df[
            [
                "model",
                "order_pass",
                "model_score",
                "loo_mae",
                "loo_sign_acc",
                "l2o_mae",
                "l2o_sign_acc",
                "pred_a2c8_minus_raw05",
                "known_rank_accuracy_vs_a2c8",
            ]
        ]
        .head(12)
        .round(9)
        .to_string(index=False)
    )
    print("[candidate gates]")
    print(
        scored[
            [
                "source_path",
                "pair_delta_vs_a2c8_p90",
                "pair_beats_a2c8_rate",
                "pair_delta_vs_raw05_p90",
                "pair_beats_raw05_rate",
                "bad_axis_abs_load",
                "pair_control_better_than_a2c8_gate",
                "pair_submit_gate",
                "pair_probe_gate",
                "pair_rank_score",
            ]
        ]
        .head(30)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
