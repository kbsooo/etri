#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, ID_COLS, LABELS, OUT_DIR, logloss

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}

PUBLIC_FEEDBACK = {
    "anchor_proxy_wcap02": 0.6311869686,
    "catboost_safe": 0.6218639574,
    "catboost_sleep_state": 0.6146217599,
    "imported_v81_raw": 0.6610032443,
}


def import_v38():
    path = ROOT / "scripts" / "96_v38_targetwise_catboost_prototype.py"
    spec = importlib.util.spec_from_file_location("cl_v38_module", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def clip(x, lo=0.03, hi=0.97):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        vals = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                vals.append(f"{float(v):.6f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["sleep_date", "lifelog_date"]:
        out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def build_full_frame(v38, train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    ordered_keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).copy()
    ordered_keys["_row_order"] = np.arange(len(ordered_keys))
    features = v38.load_feature_frame(train, test)
    features = v38.add_calendar_features(features)
    full_frame, pca_cols = v38.build_state_embedding(features, len(train))
    full_frame = v38.add_trajectory_features(full_frame, pca_cols)
    full_frame = ordered_keys.merge(full_frame, on=KEYS, how="left")
    full_frame = full_frame.sort_values("_row_order").drop(columns=["_row_order"]).reset_index(drop=True)
    return full_frame, pca_cols


def fold_row_regime(fold_train: pd.DataFrame, valid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, r in valid.reset_index(drop=True).iterrows():
        g = fold_train[fold_train["subject_id"].eq(r.subject_id)]
        d = pd.to_datetime(r.lifelog_date)
        trd = pd.to_datetime(g["lifelog_date"])
        before = trd[trd < d]
        after = trd[trd > d]
        inside = int(len(trd) and d >= trd.min() and d <= trd.max())
        rows.append(
            {
                "valid_pos": i,
                "inside_fold_train": inside,
                "after_fold_train": int(len(trd) and d > trd.max()),
                "has_future_fold_train": int(len(after) > 0),
                "nearest_fold_train_gap": float(
                    np.nanmin(
                        [
                            (d - before.max()).days if len(before) else np.nan,
                            (after.min() - d).days if len(after) else np.nan,
                        ]
                    )
                )
                if len(before) or len(after)
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def collect_row_predictions(v38, train: pd.DataFrame, full_frame: pd.DataFrame, pca_cols: list[str]) -> pd.DataFrame:
    base_cols = [
        c
        for c in full_frame.columns
        if c not in KEYS and pd.api.types.is_numeric_dtype(full_frame[c]) and not c.startswith("_")
    ]
    always_proto = [
        "anchor",
        "anchor_logit",
        "v38_global_dist",
        "v38_t_margin_dist_low_minus_high",
        "v38_t_margin_cos_high_minus_low",
        "v38_subject_mean_dist",
        "v38_subject_margin_dist_low_minus_high",
        "v38_subject_volatility",
        "v38_recent3_dist",
        "v38_recent7_dist",
        "v38_traj_prev_dist",
        "v38_traj_next_dist",
        "v38_traj_speed3",
    ]
    Z_all = full_frame[pca_cols].to_numpy(float)
    records = []
    for family, path in FOLD_FILES.items():
        folds = json.loads(path.read_text())["folds"]
        for fold in folds:
            tr_idx, va_idx = v38.fold_indices(train, fold)
            local_idx = np.r_[tr_idx, va_idx]
            meta = full_frame.iloc[local_idx].reset_index(drop=True).copy()
            meta["_full_index"] = local_idx
            model_local = np.arange(len(tr_idx))
            valid_local = np.arange(len(tr_idx), len(local_idx))
            fold_train = train.iloc[tr_idx].reset_index(drop=True)
            valid = train.iloc[va_idx].reset_index(drop=True)
            regime = fold_row_regime(fold_train, valid)
            for target in LABELS:
                ytr = train.iloc[tr_idx][target].astype(int).to_numpy()
                yva = train.iloc[va_idx][target].astype(int).to_numpy()
                proto = v38.build_prototype_features(
                    meta,
                    Z_all,
                    np.arange(len(tr_idx)),
                    target,
                    train.iloc[local_idx].reset_index(drop=True),
                    model_idx=model_local,
                )
                anchor_tr = v38.subject_prior(train.iloc[tr_idx], train.iloc[tr_idx], target)
                anchor_va = v38.subject_prior(train.iloc[tr_idx], train.iloc[va_idx], target)
                X = pd.concat([meta[base_cols].reset_index(drop=True), proto], axis=1)
                X["anchor"] = np.r_[anchor_tr, anchor_va]
                X["anchor_logit"] = v38.safe_logit(X["anchor"].to_numpy())
                keep = v38.select_features(X.iloc[model_local], ytr, [c for c in always_proto if c in X.columns], k=320)
                model, used = v38.fit_catboost(X.iloc[model_local][keep], ytr)
                pva = clip(model.predict_proba(X.iloc[valid_local][used].replace([np.inf, -np.inf], np.nan))[:, 1])
                for j, row_i in enumerate(va_idx):
                    rec = {
                        "family": family,
                        "fold": fold["name"],
                        "row_index": int(row_i),
                        "subject_id": train.iloc[row_i]["subject_id"],
                        "sleep_date": train.iloc[row_i]["sleep_date"],
                        "lifelog_date": train.iloc[row_i]["lifelog_date"],
                        "target": target,
                        "y": int(yva[j]),
                        "anchor": float(anchor_va[j]),
                        "model": float(pva[j]),
                    }
                    rec.update(regime.iloc[j].to_dict())
                    records.append(rec)
    out = pd.DataFrame(records)
    out.to_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv", index=False)
    return out


def candidate_pred(name: str, anchor: np.ndarray, model: np.ndarray) -> np.ndarray:
    if name == "anchor":
        return clip(anchor)
    if name == "catboost_safe":
        weights = {"Q1": 0.05, "Q2": 0.125, "Q3": 0.25, "S1": 0.25, "S2": 0.25, "S3": 0.125, "S4": 0.125}
        raise RuntimeError("target-specific call required")
    return clip(anchor)


def apply_recipe(df: pd.DataFrame, recipe: str) -> np.ndarray:
    y = df["target"].iloc[0]
    a = df["anchor"].to_numpy(float)
    m = df["model"].to_numpy(float)
    prob_weights = {
        "catboost_safe": {"Q1": 0.05, "Q2": 0.125, "Q3": 0.25, "S1": 0.25, "S2": 0.25, "S3": 0.125, "S4": 0.125},
    }
    logit_weights = {
        "sleep_state": {"Q1": 0.03, "Q2": 0.08, "Q3": 0.45, "S1": 0.48, "S2": 0.42, "S3": 0.08, "S4": 0.16},
        "public_axis_step2": {"Q1": 0.00, "Q2": 0.04, "Q3": 0.62, "S1": 0.64, "S2": 0.56, "S3": 0.00, "S4": 0.22},
        "public_axis_step3": {"Q1": 0.00, "Q2": 0.02, "Q3": 0.78, "S1": 0.76, "S2": 0.68, "S3": 0.00, "S4": 0.26},
    }
    temps = {"sleep_state": 1.08, "public_axis_step2": 1.10, "public_axis_step3": 1.15}
    if recipe == "anchor":
        return clip(a)
    if recipe in prob_weights:
        w = prob_weights[recipe].get(y, 0.0)
        return clip(a * (1 - w) + m * w)
    if recipe in logit_weights:
        w = logit_weights[recipe].get(y, 0.0)
        return clip(sigmoid(((1 - w) * logit(a) + w * logit(m)) / temps[recipe]))
    if recipe == "rowgate":
        base = apply_recipe(df, "sleep_state")
        specs = {"Q3": (0.40, 0.22), "S1": (0.35, 0.20), "S2": (0.35, 0.20), "S4": (0.25, 0.10)}
        if y not in specs:
            return base
        top_frac, extra_w = specs[y]
        delta = np.abs(m - a)
        gate = delta >= np.quantile(delta, 1 - top_frac)
        out = base.copy()
        out[gate] = out[gate] * (1 - extra_w) + m[gate] * extra_w
        return clip(out)
    if recipe == "consensus":
        if y not in ["Q3", "S1", "S2", "S4"]:
            return apply_recipe(df, "sleep_state")
        return clip(0.5 * apply_recipe(df, "sleep_state") + 0.25 * apply_recipe(df, "public_axis_step2") + 0.25 * apply_recipe(df, "rowgate"))
    raise ValueError(recipe)


def score_recipes(row_pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    recipes = ["anchor", "catboost_safe", "sleep_state", "public_axis_step2", "public_axis_step3", "rowgate", "consensus"]
    score_rows = []
    target_rows = []
    for recipe in recipes:
        all_losses = []
        for (family, fold, target), g in row_pred.groupby(["family", "fold", "target"]):
            pred = apply_recipe(g, recipe)
            loss = float(logloss(g["y"].to_numpy(int), pred))
            base = float(logloss(g["y"].to_numpy(int), g["anchor"].to_numpy(float)))
            inside = g["inside_fold_train"].eq(1).to_numpy(bool)
            tail = g["after_fold_train"].eq(1).to_numpy(bool)
            target_rows.append(
                {
                    "recipe": recipe,
                    "family": family,
                    "fold": fold,
                    "target": target,
                    "n": len(g),
                    "loss": loss,
                    "anchor_loss": base,
                    "delta_vs_anchor": loss - base,
                    "inside_loss": float(logloss(g.loc[inside, "y"], pred[inside])) if inside.any() else np.nan,
                    "tail_loss": float(logloss(g.loc[tail, "y"], pred[tail])) if tail.any() else np.nan,
                    "mean_abs_move": float(np.abs(pred - g["anchor"].to_numpy(float)).mean()),
                }
            )
            all_losses.append({"family": family, "fold": fold, "target": target, "n": len(g), "loss": loss, "anchor_loss": base})
        d = pd.DataFrame(all_losses)
        fam = d.groupby("family").apply(lambda x: np.average(x["loss"], weights=x["n"]), include_groups=False).to_dict()
        score_rows.append(
            {
                "recipe": recipe,
                "local_weighted": float(np.average(d["loss"], weights=d["n"])),
                "chrono_tail": fam.get("chrono_tail", np.nan),
                "hole_v1": fam.get("hole_v1", np.nan),
                "mirror_v1": fam.get("mirror_v1", np.nan),
                "mirror_hole_avg": float(np.nanmean([fam.get("mirror_v1", np.nan), fam.get("hole_v1", np.nan)])),
                "worst_family": float(np.nanmax(list(fam.values()))),
                "mean_abs_move": float(pd.DataFrame(target_rows).query("recipe == @recipe")["mean_abs_move"].mean()),
            }
        )
    return pd.DataFrame(score_rows), pd.DataFrame(target_rows)


def public_calibration(score: pd.DataFrame) -> pd.DataFrame:
    known_map = {"anchor": "anchor_proxy_wcap02", "catboost_safe": "catboost_safe", "sleep_state": "catboost_sleep_state"}
    known = []
    for recipe, public_name in known_map.items():
        row = score[score["recipe"].eq(recipe)].iloc[0].to_dict()
        row["public_name"] = public_name
        row["public_lb"] = PUBLIC_FEEDBACK[public_name]
        known.append(row)
    known_df = pd.DataFrame(known)
    # Fit a deliberately tiny affine bridge from mirror/hole validation to public.
    x = known_df["mirror_hole_avg"].to_numpy(float)
    y = known_df["public_lb"].to_numpy(float)
    if len(np.unique(np.round(x, 8))) >= 2:
        slope, intercept = np.polyfit(x, y, 1)
    else:
        slope, intercept = 1.0, float(y.mean() - x.mean())
    out = score.copy()
    out["public_calibrated_lb_estimate"] = intercept + slope * out["mirror_hole_avg"]
    out["calibration_slope"] = slope
    out["calibration_intercept"] = intercept
    out["known_public_lb"] = out["recipe"].map({k: PUBLIC_FEEDBACK[v] for k, v in known_map.items()})
    return out.sort_values("public_calibrated_lb_estimate")


def write_report(calibrated: pd.DataFrame, target_scores: pd.DataFrame) -> None:
    known = calibrated[calibrated["known_public_lb"].notna()][
        ["recipe", "mirror_hole_avg", "public_calibrated_lb_estimate", "known_public_lb"]
    ].copy()
    target_avg = (
        target_scores.groupby(["recipe", "target"])
        .agg(loss=("loss", "mean"), delta_vs_anchor=("delta_vs_anchor", "mean"), mean_abs_move=("mean_abs_move", "mean"))
        .reset_index()
    )
    lines = [
        "# CL Public-Calibrated Validation",
        "",
        "## What Changed",
        "",
        "This validation keeps fold-local CatBoost predictions for every validation row instead of only aggregate fold losses. It then scores the same blend recipes used for tomorrow's candidate files.",
        "",
        "Public labels are unavailable, so this is not a literal perfect validator. The improvement is that the validator is now calibrated against today's observed public feedback and explicitly reports when a candidate is an extrapolation beyond known feedback.",
        "",
        "## Known Public Bridge",
        "",
        md_table(known),
        "",
        "## Candidate Ranking",
        "",
        md_table(calibrated[["recipe", "local_weighted", "chrono_tail", "hole_v1", "mirror_v1", "mirror_hole_avg", "worst_family", "mean_abs_move", "public_calibrated_lb_estimate", "known_public_lb"]]),
        "",
        "## Target Diagnostics",
        "",
        md_table(target_avg),
        "",
        "## Decision Rule",
        "",
        "- Trust only rank/order among `anchor`, `catboost_safe`, and `sleep_state`; those are public-anchored.",
        "- Treat `public_axis_step2`, `rowgate`, `consensus`, and `public_axis_step3` as extrapolations. They need movement in the same Q3/S1/S2 axis without turning Q1/Q2/S3 into the failed imported-v81 shape.",
        "- A candidate is valid for the 0.57 attempt only if it improves calibrated estimate versus `sleep_state` and does not make `worst_family` worse than `sleep_state` by more than 0.015.",
    ]
    (EXPERIMENT_DIR / "cl_public_calibrated_validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    v38 = import_v38()
    train, test = v38.load_data()
    full_frame, pca_cols = build_full_frame(v38, train, test)
    row_pred = collect_row_predictions(v38, train, full_frame, pca_cols)
    score, target_scores = score_recipes(row_pred)
    calibrated = public_calibration(score)
    score.to_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_recipe_scores_raw.csv", index=False)
    calibrated.to_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_recipe_scores.csv", index=False)
    target_scores.to_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_target_scores.csv", index=False)
    write_report(calibrated, target_scores)
    print(calibrated.to_string(index=False))


if __name__ == "__main__":
    main()
