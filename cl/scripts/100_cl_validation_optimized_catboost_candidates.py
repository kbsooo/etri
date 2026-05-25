#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
EXP = ROOT / "experiments"
DATA = ROOT / "data"
IDS = ["subject_id", "sleep_date", "lifelog_date"]
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in IDS:
        if "date" in c:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
        else:
            out[c] = out[c].astype(str)
    return out


def read_sub(name: str) -> pd.DataFrame:
    return norm_dates(pd.read_csv(OUT / name)).sort_values(IDS).reset_index(drop=True)


def clip(x, lo=0.03, hi=0.97):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def logloss_np(y, p):
    p = clip(p, 1e-15, 1 - 1e-15)
    y = np.asarray(y, dtype=int)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        vals = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                vals.append(f"{float(v):.6f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def predict(anchor, model, mode: str, weight: float, temp: float) -> np.ndarray:
    if mode == "prob":
        return clip((1 - weight) * anchor + weight * model)
    return clip(sigmoid(((1 - weight) * logit(anchor) + weight * logit(model)) / temp))


def search_target_weights(row_pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grid_w = [0.0, 0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70]
    grid_t = [1.00, 1.04, 1.08, 1.12, 1.16]
    for target, g_all in row_pred.groupby("target"):
        anchor_score = {}
        for fam, g in g_all.groupby("family"):
            anchor_score[fam] = logloss_np(g["y"], g["anchor"])
        for mode in ["prob", "logit"]:
            for w in grid_w:
                for temp in (grid_t if mode == "logit" else [1.0]):
                    fam_scores = {}
                    moves = []
                    for fam, g in g_all.groupby("family"):
                        p = predict(g["anchor"].to_numpy(float), g["model"].to_numpy(float), mode, w, temp)
                        fam_scores[fam] = logloss_np(g["y"], p)
                        moves.append(np.abs(p - g["anchor"].to_numpy(float)).mean())
                    mirror_hole = np.mean([fam_scores["mirror_v1"], fam_scores["hole_v1"]])
                    chrono_delta = fam_scores["chrono_tail"] - anchor_score["chrono_tail"]
                    mirror_delta = fam_scores["mirror_v1"] - anchor_score["mirror_v1"]
                    hole_delta = fam_scores["hole_v1"] - anchor_score["hole_v1"]
                    # Penalize target choices that only work on one regime or rely on large unsupported moves.
                    instability = max(0.0, chrono_delta - 0.004) + max(0.0, mirror_delta - 0.004) + max(0.0, hole_delta - 0.004)
                    move = float(np.mean(moves))
                    move_penalty = max(0.0, move - {"Q3": 0.09, "S1": 0.09, "S2": 0.06}.get(target, 0.025)) * 0.35
                    score = mirror_hole + instability + move_penalty
                    rows.append(
                        {
                            "target": target,
                            "mode": mode,
                            "weight": w,
                            "temp": temp,
                            "score": score,
                            "mirror_hole": mirror_hole,
                            "chrono": fam_scores["chrono_tail"],
                            "hole": fam_scores["hole_v1"],
                            "mirror": fam_scores["mirror_v1"],
                            "chrono_delta": chrono_delta,
                            "hole_delta": hole_delta,
                            "mirror_delta": mirror_delta,
                            "mean_abs_move": move,
                        }
                    )
    scores = pd.DataFrame(rows)
    scores.to_csv(EXP / "cl_validation_optimized_weight_grid.csv", index=False)
    return scores


def choose_weights(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    best = scores.sort_values(["target", "score"]).groupby("target", as_index=False).first()
    # Guarded version: do not move targets whose best validation gain is tiny or
    # whose move is known from public feedback to be hazardous.
    guarded = best.copy()
    for i, r in guarded.iterrows():
        if r["target"] == "S2":
            guarded.loc[i, "weight"] = min(float(r["weight"]), 0.25)
        if r["target"] in ["S3", "S4"] and r["mirror_hole"] >= scores[(scores.target == r["target"]) & (scores.weight == 0)]["mirror_hole"].iloc[0] - 0.001:
            guarded.loc[i, "weight"] = 0.0
            guarded.loc[i, "mode"] = "prob"
            guarded.loc[i, "temp"] = 1.0
        if r["target"] in ["Q1", "Q2"] and r["mean_abs_move"] > 0.02:
            guarded.loc[i, "weight"] = min(float(r["weight"]), 0.10)
    best.to_csv(EXP / "cl_validation_optimized_best_weights.csv", index=False)
    guarded.to_csv(EXP / "cl_validation_optimized_guarded_weights.csv", index=False)
    return best, guarded


def build_submission(weights: pd.DataFrame, anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    out = anchor.copy()
    by_target = {r.target: r for r in weights.itertuples(index=False)}
    for y in LABELS:
        r = by_target[y]
        out[y] = predict(anchor[y].to_numpy(float), model[y].to_numpy(float), r.mode, float(r.weight), float(r.temp))
    return out


def summarize_files(files: dict[str, pd.DataFrame], anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    sample = norm_dates(pd.read_csv(DATA / "ch2026_submission_sample.csv")).sort_values(IDS).reset_index(drop=True)
    rows = []
    for name, df in files.items():
        df = norm_dates(df).sort_values(IDS).reset_index(drop=True)
        df.to_csv(OUT / name, index=False)
        for y in LABELS:
            da = df[y].to_numpy(float) - anchor[y].to_numpy(float)
            rows.append(
                {
                    "file": name,
                    "target": y,
                    "keys_ok": bool(df[IDS].equals(sample[IDS])),
                    "no_na": bool(df[LABELS].notna().all().all()),
                    "mean_abs_vs_anchor": float(np.abs(da).mean()),
                    "max_abs_vs_anchor": float(np.abs(da).max()),
                    "mean_abs_vs_model": float(np.abs(df[y] - model[y]).mean()),
                    "mean": float(df[y].mean()),
                    "std": float(df[y].std()),
                    "min": float(df[y].min()),
                    "max": float(df[y].max()),
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(EXP / "cl_validation_optimized_candidate_summary.csv", index=False)
    return summary


def score_weight_set(row_pred: pd.DataFrame, weights: pd.DataFrame, name: str) -> dict:
    rows = []
    by_target = {r.target: r for r in weights.itertuples(index=False)}
    for (family, target), g in row_pred.groupby(["family", "target"]):
        r = by_target[target]
        p = predict(g["anchor"].to_numpy(float), g["model"].to_numpy(float), r.mode, float(r.weight), float(r.temp))
        rows.append({"family": family, "target": target, "n": len(g), "loss": logloss_np(g["y"], p), "move": float(np.abs(p - g["anchor"]).mean())})
    d = pd.DataFrame(rows)
    fam = d.groupby("family").apply(lambda x: np.average(x["loss"], weights=x["n"]), include_groups=False)
    return {
        "candidate": name,
        "local_weighted": float(np.average(d["loss"], weights=d["n"])),
        "chrono_tail": float(fam["chrono_tail"]),
        "hole_v1": float(fam["hole_v1"]),
        "mirror_v1": float(fam["mirror_v1"]),
        "mirror_hole_avg": float((fam["hole_v1"] + fam["mirror_v1"]) / 2),
        "mean_abs_move": float(d["move"].mean()),
    }


def main() -> None:
    row_pred = pd.read_csv(EXP / "cl_public_calibrated_validation_row_predictions.csv")
    anchor = read_sub("submission_meta_anchor_w02_noq3_prob.csv")
    model = read_sub("submission_v38_targetwise_catboost_proto_raw_model_prob.csv")
    scores = search_target_weights(row_pred)
    best, guarded = choose_weights(scores)
    files = {
        "submission_cl_catboost_validation_optimized_targetwise_prob.csv": build_submission(best, anchor, model),
        "submission_cl_catboost_validation_optimized_guarded_prob.csv": build_submission(guarded, anchor, model),
    }
    file_summary = summarize_files(files, anchor, model)
    validation_summary = pd.DataFrame(
        [
            score_weight_set(row_pred, best, "validation_optimized_targetwise"),
            score_weight_set(row_pred, guarded, "validation_optimized_guarded"),
        ]
    )
    validation_summary.to_csv(EXP / "cl_validation_optimized_candidate_validation_scores.csv", index=False)
    report = "\n".join(
        [
            "# CL Validation-Optimized CatBoost Candidates",
            "",
            "## Validation Scores",
            "",
            md_table(validation_summary),
            "",
            "## Best Target Weights",
            "",
            md_table(best),
            "",
            "## Guarded Target Weights",
            "",
            md_table(guarded),
            "",
            "## File Summary",
            "",
            md_table(file_summary),
        ]
    )
    (EXP / "cl_validation_optimized_catboost_report.md").write_text(report, encoding="utf-8")
    print(validation_summary.to_string(index=False))
    print(best[["target", "mode", "weight", "temp", "score", "mirror_hole", "mean_abs_move"]].to_string(index=False))


if __name__ == "__main__":
    main()
