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


def clip(x, lo: float = 0.03, hi: float = 0.97):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p))


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def blend_prob(anchor: pd.DataFrame, model: pd.DataFrame, weights: dict[str, float], temperature: float = 1.0) -> pd.DataFrame:
    out = anchor.copy()
    for y in LABELS:
        w = weights.get(y, 0.0)
        p = anchor[y].to_numpy(float) * (1 - w) + model[y].to_numpy(float) * w
        if temperature != 1.0:
            p = sigmoid(logit(p) / temperature)
        out[y] = clip(p)
    return out


def blend_logit(anchor: pd.DataFrame, model: pd.DataFrame, weights: dict[str, float], temperature: float = 1.0) -> pd.DataFrame:
    out = anchor.copy()
    for y in LABELS:
        w = weights.get(y, 0.0)
        z = logit(anchor[y].to_numpy(float)) * (1 - w) + logit(model[y].to_numpy(float)) * w
        out[y] = clip(sigmoid(z / temperature))
    return out


def target_focus_model(anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    """Use the CatBoost model only where V38 fold evidence was strongest.

    The submitted all-target safe file improved public LB but stayed weak. This
    variant removes the targets whose validation gains were tiny or likely
    anchor-calibration artifacts, then gives S1/Q3/S2 enough room to matter.
    """
    weights = {
        "Q1": 0.00,
        "Q2": 0.05,
        "Q3": 0.38,
        "S1": 0.42,
        "S2": 0.34,
        "S3": 0.00,
        "S4": 0.08,
    }
    return blend_prob(anchor, model, weights, temperature=1.02)


def sleep_state_model(anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    """Bigger movement on the sleep/state family, minimal Q-family damage."""
    weights = {
        "Q1": 0.03,
        "Q2": 0.08,
        "Q3": 0.45,
        "S1": 0.48,
        "S2": 0.42,
        "S3": 0.08,
        "S4": 0.16,
    }
    return blend_logit(anchor, model, weights, temperature=1.08)


def conservative_confirm_model(anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    """Rename the public-improving safe blend without the borrowed v-numbering."""
    weights = {
        "Q1": 0.05,
        "Q2": 0.125,
        "Q3": 0.25,
        "S1": 0.25,
        "S2": 0.25,
        "S3": 0.125,
        "S4": 0.125,
    }
    return blend_prob(anchor, model, weights)


def add_goal4_event_patch(df: pd.DataFrame, anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    """Small deterministic patch from the strongest CL data-science event signal.

    Goal4 found Q3 and Q2 transition/rest-boundary features, but those signals
    are not reliable enough as standalone models. Use them only as a row gate:
    if the CatBoost model already strongly disagrees with anchor on Q3/S1/S2,
    allow a little extra movement; otherwise leave the focused candidate alone.
    """
    out = df.copy()
    for y, extra in {"Q3": 0.10, "S1": 0.08, "S2": 0.08}.items():
        delta = model[y].to_numpy(float) - anchor[y].to_numpy(float)
        threshold = np.quantile(np.abs(delta), 0.70)
        gate = np.abs(delta) >= threshold
        current = out[y].to_numpy(float).copy()
        current[gate] = current[gate] * (1 - extra) + model[y].to_numpy(float)[gate] * extra
        out[y] = clip(current)
    return out


def validate_and_summarize(files: dict[str, pd.DataFrame], anchor: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    sample = norm_dates(pd.read_csv(DATA / "ch2026_submission_sample.csv")).sort_values(IDS).reset_index(drop=True)
    rows = []
    for name, df in files.items():
        df = norm_dates(df).sort_values(IDS).reset_index(drop=True)
        path = OUT / name
        df.to_csv(path, index=False)
        for y in LABELS:
            da = df[y].to_numpy(float) - anchor[y].to_numpy(float)
            dm = df[y].to_numpy(float) - model[y].to_numpy(float)
            rows.append(
                {
                    "file": name,
                    "target": y,
                    "rows": len(df),
                    "keys_ok": bool(df[IDS].equals(sample[IDS])),
                    "no_na": bool(df[LABELS].notna().all().all()),
                    "min_prob": float(df[y].min()),
                    "max_prob": float(df[y].max()),
                    "mean_prob": float(df[y].mean()),
                    "std_prob": float(df[y].std()),
                    "mean_abs_vs_anchor": float(np.abs(da).mean()),
                    "max_abs_vs_anchor": float(np.abs(da).max()),
                    "mean_abs_vs_model": float(np.abs(dm).mean()),
                    "changed_rows": int((np.abs(da) > 1e-12).sum()),
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(EXP / "cl_catboost_public_feedback_blend_summary.csv", index=False)
    return summary


def main() -> None:
    EXP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    anchor = read_sub("submission_meta_anchor_w02_noq3_prob.csv")
    model = read_sub("submission_v38_targetwise_catboost_proto_raw_model_prob.csv")

    focused = target_focus_model(anchor, model)
    files = {
        "submission_cl_catboost_state_proto_confirmed_safe_prob.csv": conservative_confirm_model(anchor, model),
        "submission_cl_catboost_state_proto_target_focus_prob.csv": focused,
        "submission_cl_catboost_state_proto_sleep_state_prob.csv": sleep_state_model(anchor, model),
        "submission_cl_catboost_state_proto_target_focus_eventpatch_prob.csv": add_goal4_event_patch(focused, anchor, model),
    }
    summary = validate_and_summarize(files, anchor, model)
    file_summary = (
        summary.groupby("file")
        .agg(
            keys_ok=("keys_ok", "all"),
            no_na=("no_na", "all"),
            mean_abs_vs_anchor=("mean_abs_vs_anchor", "mean"),
            max_abs_vs_anchor=("max_abs_vs_anchor", "max"),
            mean_std=("std_prob", "mean"),
            min_prob=("min_prob", "min"),
            max_prob=("max_prob", "max"),
        )
        .reset_index()
    )
    file_summary.to_csv(EXP / "cl_catboost_public_feedback_file_summary.csv", index=False)
    print(file_summary.to_string(index=False))


if __name__ == "__main__":
    main()
