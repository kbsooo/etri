"""Q2/Q3 event-residual diagnostic prototype.

No submission generation. This script translates Phase 3 insights into a small
OOF diagnostic:

  anchor subject prior
  + same-subject nearest-label grammar
  + subject-normalized event/deviation features
  + capped movement back toward anchor

The goal is not to win local CV; it is to check whether Q2/Q3 can move in a
controlled way across the three hybrid validation regimes while Q1/S-family stay
protected.

Outputs:
  experiments/q2q3_event_residual_diagnostic_results.csv
  experiments/q2q3_event_residual_diagnostic_shifts.csv
  experiments/q2q3_event_residual_diagnostic_selected_features.csv
  experiments/q2q3_event_residual_diagnostic_report.md
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
FEAT_PARQUET = ROOT / "features" / "model_features_v0.parquet"
VAL_DIR = ROOT / "outputs" / "validation"
EXP = ROOT / "experiments"

FOLD_FILES = {
    "chrono_tail": VAL_DIR / "folds_chrono_tail_v2.json",
    "hole_v1": VAL_DIR / "folds_interleaved_hole_v1.json",
    "mirror_v1": VAL_DIR / "folds_subject_mirror_v1.json",
}

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
MOVE_CAP = {"Q1": 0.03, "Q2": 0.10, "Q3": 0.055, "S1": 0.0, "S2": 0.0, "S3": 0.0, "S4": 0.035}
EVENT_KEYWORDS = [
    "gps", "wifi", "ble", "app", "screen", "usage",
    "quiet", "screenoff", "sleep_block", "sleepwin", "longest", "s4x", "prevnight",
    "entropy", "fragment", "weekday", "roll", "dev_", "prev_delta",
    "steps", "pedo", "activity", "distance", "speed",
]
DROP_LABELS = set(LABELS)


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1 / (1 + np.exp(-np.asarray(x)))


def logit(p: np.ndarray | float, eps: float = 1e-4) -> np.ndarray | float:
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    return np.log(p / (1 - p))


def clip_prob(x: np.ndarray, lo: float = 0.03, hi: float = 0.97) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def load_df() -> pd.DataFrame:
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    feats = pd.read_parquet(FEAT_PARQUET)
    feats["lifelog_date"] = pd.to_datetime(feats["lifelog_date"]).dt.date.astype(str)
    df = tr.merge(feats, on=["subject_id", "lifelog_date"], how="left")
    if len(df) != len(tr):
        raise RuntimeError("feature join changed row count")
    df["_date"] = pd.to_datetime(df["lifelog_date"])
    return df


def key_index(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = key_index(df)
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


def subject_prior(train: pd.DataFrame, valid: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    sm = ((pos + alpha * g) / (cnt + alpha)).to_dict()
    return np.array([sm.get(s, g) for s in valid["subject_id"]], dtype=float)


def nearest_label_features(train: pd.DataFrame, valid: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    """Nearest same-subject known labels from the fold train rows only.

    For a held-out row in a hole fold this can use both earlier and later train
    dates; for a tail fold it mostly uses past dates. This mirrors the diagnostic
    regime split rather than leaking validation labels.
    """
    out = []
    by_subj = {s: g.sort_values("_date").reset_index(drop=True) for s, g in train.groupby("subject_id")}
    glob = {lab: float(train[lab].mean()) for lab in LABELS}
    for _, row in valid.iterrows():
        g = by_subj.get(row["subject_id"])
        rec = {}
        if g is None or len(g) == 0:
            for lab in LABELS:
                rec[f"near_{lab}_mean"] = glob[lab]
                rec[f"past_{lab}_mean"] = glob[lab]
                rec[f"future_{lab}_mean"] = glob[lab]
            rec["near_min_abs_daydiff"] = np.nan
            rec["near_has_future"] = 0
            out.append(rec)
            continue
        diff = (g["_date"] - row["_date"]).dt.days
        absdiff = diff.abs().to_numpy()
        order = np.argsort(absdiff)[: min(k, len(g))]
        past = g.loc[diff < 0].tail(k)
        future = g.loc[diff > 0].head(k)
        for lab in LABELS:
            rec[f"near_{lab}_mean"] = float(g.iloc[order][lab].mean())
            rec[f"past_{lab}_mean"] = float(past[lab].mean()) if len(past) else glob[lab]
            rec[f"future_{lab}_mean"] = float(future[lab].mean()) if len(future) else glob[lab]
        rec["near_min_abs_daydiff"] = float(absdiff[order[0]]) if len(order) else np.nan
        rec["near_has_future"] = int((diff > 0).any())
        out.append(rec)
    return pd.DataFrame(out, index=valid.index)


def event_feature_cols(df: pd.DataFrame) -> list[str]:
    cols = []
    for c in df.columns:
        if c in DROP_LABELS or c in {"subject_id", "sleep_date", "lifelog_date", "_date"}:
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            continue
        cl = c.lower()
        # Keep day-level / within-subject movement features. Deliberately exclude
        # `__subj_mean`: Phase 3 already showed subject anchors are strong, but this
        # diagnostic is about event/deviation residuals rather than re-learning static
        # subject fingerprints.
        is_deviation = (
            c.endswith("__subj_z")
            or c.endswith("__subj_delta")
            or "__prev_delta" in cl
            or "__prev_abs_delta" in cl
            or "__dev_roll" in cl
            or "__dev_weekday" in cl
            or "__weekday_vs_subject" in cl
            or c in {"longest_screenoff_run_h", "longest_quiet_run_h", "s4x_cross_quiet_longest_h", "s4x_cross_screenoff_longest_h"}
        )
        if is_deviation and any(k in cl for k in EVENT_KEYWORDS) and not c.endswith("__subj_mean"):
            x = df[c].replace([np.inf, -np.inf], np.nan)
            if x.notna().mean() > 0.45 and x.std(skipna=True) > 1e-8:
                cols.append(c)
    # keep deterministic and bounded; SelectKBest later chooses per fold/target.
    return sorted(set(cols))


def build_design(train: pd.DataFrame, valid: pd.DataFrame, target: str, ev_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, list[str]]:
    p_tr = subject_prior(train, train, target)
    p_va = subject_prior(train, valid, target)
    nf_tr = nearest_label_features(train, train, k=3)
    nf_va = nearest_label_features(train, valid, k=3)

    base_tr = pd.DataFrame({
        "anchor_logit": logit(p_tr),
        "anchor_p": p_tr,
    }, index=train.index)
    base_va = pd.DataFrame({
        "anchor_logit": logit(p_va),
        "anchor_p": p_va,
    }, index=valid.index)

    grammar_cols = [c for c in nf_tr.columns if c.startswith("near_") or c.startswith("past_") or c.startswith("future_") or c in ["near_min_abs_daydiff", "near_has_future"]]
    Xtr = pd.concat([base_tr.reset_index(drop=True), nf_tr[grammar_cols].reset_index(drop=True), train[ev_cols].reset_index(drop=True)], axis=1)
    Xva = pd.concat([base_va.reset_index(drop=True), nf_va[grammar_cols].reset_index(drop=True), valid[ev_cols].reset_index(drop=True)], axis=1)
    return Xtr, Xva, p_va, list(Xtr.columns)


def fit_predict_residual(train: pd.DataFrame, valid: pd.DataFrame, target: str, ev_cols: list[str], k_features: int = 35) -> tuple[np.ndarray, np.ndarray, list[str]]:
    Xtr, Xva, anchor_va, all_cols = build_design(train, valid, target, ev_cols)
    y = train[target].astype(int).to_numpy()
    if y.std() < 1e-8:
        return anchor_va, anchor_va, []
    k = min(k_features, Xtr.shape[1])
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("select", SelectKBest(f_classif, k=k)),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(C=0.12, max_iter=3000, solver="lbfgs")),
    ])
    pipe.fit(Xtr, y)
    raw = pipe.predict_proba(Xva)[:, 1]
    mask = pipe.named_steps["select"].get_support()
    selected = [c for c, m in zip(all_cols, mask) if m]
    return clip_prob(raw), anchor_va, selected


def capped_toward_anchor(anchor: np.ndarray, raw: np.ndarray, cap: float) -> np.ndarray:
    if cap <= 0:
        return clip_prob(anchor)
    delta = np.clip(raw - anchor, -cap, cap)
    return clip_prob(anchor + delta)


def score_preds(valid: pd.DataFrame, preds: dict[str, np.ndarray]) -> dict[str, float]:
    out = {}
    for t in LABELS:
        out[t] = float(logloss(valid[t].astype(int).values, clip_prob(preds[t])))
    out["mean"] = float(np.mean([out[t] for t in LABELS]))
    out["mean_Q"] = float(np.mean([out[t] for t in ["Q1", "Q2", "Q3"]]))
    out["mean_Q2Q3"] = float(np.mean([out[t] for t in ["Q2", "Q3"]]))
    out["mean_S"] = float(np.mean([out[t] for t in ["S1", "S2", "S3", "S4"]]))
    return out


def markdown_table(df: pd.DataFrame, index: bool = False, floatfmt: str = ".4f") -> str:
    d = df.copy()
    if index:
        d = d.reset_index()
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        cells = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and not pd.isna(v):
                cells.append(format(float(v), floatfmt))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    EXP.mkdir(exist_ok=True)
    df = load_df()
    ev_cols = event_feature_cols(df)
    rows = []
    shift_rows = []
    selected_rows = []

    for family, fpath in FOLD_FILES.items():
        cfg = json.loads(fpath.read_text())
        for fold in cfg["folds"]:
            train, valid = split_by_fold(df, fold)
            if len(valid) == 0:
                continue

            # Baseline: subject prior for all labels.
            anchor_preds = {t: subject_prior(train, valid, t) for t in LABELS}
            neighbor_preds = {}
            nf = nearest_label_features(train, valid, k=3)
            for t in LABELS:
                neighbor_preds[t] = nf[f"near_{t}_mean"].to_numpy(dtype=float)

            # Event model only moves Q1/Q2/Q3/S4; S1/S2/S3 are deliberately frozen to anchor.
            raw_preds = {t: anchor_preds[t].copy() for t in LABELS}
            capped_preds = {t: anchor_preds[t].copy() for t in LABELS}
            for t in ["Q1", "Q2", "Q3", "S4"]:
                raw, anchor, selected = fit_predict_residual(train, valid, t, ev_cols, k_features=35)
                raw_preds[t] = raw
                capped_preds[t] = capped_toward_anchor(anchor, raw, MOVE_CAP[t])
                for s in selected:
                    selected_rows.append({"family": family, "fold": fold.get("name"), "target": t, "feature": s})
                for i, (_, r) in enumerate(valid.iterrows()):
                    shift_rows.append({
                        "family": family,
                        "fold": fold.get("name"),
                        "target": t,
                        "subject_id": r["subject_id"],
                        "lifelog_date": r["lifelog_date"],
                        "y": int(r[t]),
                        "anchor": float(anchor_preds[t][i]),
                        "raw": float(raw_preds[t][i]),
                        "capped": float(capped_preds[t][i]),
                        "delta_raw": float(raw_preds[t][i] - anchor_preds[t][i]),
                        "delta_capped": float(capped_preds[t][i] - anchor_preds[t][i]),
                    })

            models = {
                "anchor_subject_prior": anchor_preds,
                "neighbor_k3_canary": neighbor_preds,
                "event_raw_q1q2q3s4": raw_preds,
                "event_capped_q1q2q3s4": capped_preds,
            }
            for model_name, preds in models.items():
                sc = score_preds(valid, preds)
                rec = {
                    "family": family,
                    "fold": fold.get("name"),
                    "model": model_name,
                    "n_train": len(train),
                    "n_valid": len(valid),
                    **{f"ll_{k}": v for k, v in sc.items()},
                }
                rows.append(rec)
                print(f"{family:12s} {fold.get('name'):24s} {model_name:24s} mean={sc['mean']:.4f} Q2Q3={sc['mean_Q2Q3']:.4f}")

    res = pd.DataFrame(rows)
    shifts = pd.DataFrame(shift_rows)
    selected = pd.DataFrame(selected_rows)
    res.to_csv(EXP / "q2q3_event_residual_diagnostic_results.csv", index=False)
    shifts.to_csv(EXP / "q2q3_event_residual_diagnostic_shifts.csv", index=False)
    selected.to_csv(EXP / "q2q3_event_residual_diagnostic_selected_features.csv", index=False)
    write_report(res, shifts, selected, len(ev_cols))


def write_report(res: pd.DataFrame, shifts: pd.DataFrame, selected: pd.DataFrame, n_event_cols: int):
    summary = res.groupby(["family", "model"])[["ll_mean", "ll_mean_Q", "ll_mean_Q2Q3", "ll_Q1", "ll_Q2", "ll_Q3", "ll_S4"]].mean().reset_index()
    anchor = summary[summary.model.eq("anchor_subject_prior")].set_index("family")
    rows = []
    for _, r in summary.iterrows():
        a = anchor.loc[r.family]
        rec = r.to_dict()
        for c in ["ll_mean", "ll_mean_Q2Q3", "ll_Q1", "ll_Q2", "ll_Q3", "ll_S4"]:
            rec[f"delta_{c}_vs_anchor"] = r[c] - a[c]
        rows.append(rec)
    comp = pd.DataFrame(rows)
    comp.to_csv(EXP / "q2q3_event_residual_diagnostic_summary.csv", index=False)

    shift_sum = shifts.groupby(["family", "target"]).agg(
        mean_abs_delta_raw=("delta_raw", lambda x: float(np.mean(np.abs(x)))),
        p95_abs_delta_raw=("delta_raw", lambda x: float(np.quantile(np.abs(x), 0.95))),
        mean_abs_delta_capped=("delta_capped", lambda x: float(np.mean(np.abs(x)))),
        p95_abs_delta_capped=("delta_capped", lambda x: float(np.quantile(np.abs(x), 0.95))),
        mean_delta_capped=("delta_capped", "mean"),
    ).reset_index()

    feat_top = pd.DataFrame()
    if len(selected):
        feat_top = selected.groupby(["target", "feature"]).size().reset_index(name="selected_count").sort_values(["target", "selected_count"], ascending=[True, False])

    lines = []
    lines.append("# Q2/Q3 event-residual diagnostic\n")
    lines.append("## 목적\n")
    lines.append("Phase 3의 `Q2/Q3 event/deviation residual` 가설을 submission 없이 OOF로만 점검했다. S-family는 보호하고, Q1은 tiny residual만 허용했다.\n")
    lines.append(f"- candidate event/deviation numeric features: {n_event_cols}\n")
    lines.append("- folds: chrono_tail, interleaved hole, subject mirror\n")
    lines.append("- models: subject anchor, nearest-label canary, raw event residual, capped event residual\n")

    lines.append("\n## 1. Mean scores by family/model\n")
    view_cols = ["family", "model", "ll_mean", "ll_mean_Q2Q3", "ll_Q1", "ll_Q2", "ll_Q3", "ll_S4"]
    lines.append(markdown_table(summary[view_cols].sort_values(["family", "model"])))

    lines.append("\n## 2. Delta vs subject-anchor (negative is improvement)\n")
    dcols = ["family", "model", "delta_ll_mean_vs_anchor", "delta_ll_mean_Q2Q3_vs_anchor", "delta_ll_Q1_vs_anchor", "delta_ll_Q2_vs_anchor", "delta_ll_Q3_vs_anchor", "delta_ll_S4_vs_anchor"]
    lines.append(markdown_table(comp[dcols].sort_values(["family", "model"])))

    lines.append("\n## 3. Movement audit\n")
    lines.append(markdown_table(shift_sum.sort_values(["family", "target"])))

    lines.append("\n## 4. Most frequently selected features\n")
    if len(feat_top):
        lines.append(markdown_table(feat_top.groupby("target").head(12)))
    else:
        lines.append("No selected feature rows.\n")

    lines.append("\n## 5. Interpretation guide\n")
    lines.append("- `neighbor_k3_canary`가 hole/mirror에서 강하고 chrono_tail에서 약하면, test가 hole-filling 성격일 때만 강한 temporal completion signal이다.\n")
    lines.append("- `event_raw`가 좋아도 movement가 크면 public/private brittle 가능성이 크다. 최종 번역은 `event_capped` 쪽만 본다.\n")
    lines.append("- Q1은 negative-control에서 coverage가 깨졌으므로, Q1 개선처럼 보여도 큰 의미를 두지 않는다.\n")
    lines.append("- S-family는 freeze가 기본이다. 여기서는 S4만 tiny diagnostic residual을 허용했지만 anchor 대비 악화하면 즉시 폐기한다.\n")

    # brief automatic conclusion
    capped = comp[comp.model.eq("event_capped_q1q2q3s4")]
    lines.append("\n## 6. Automatic coarse conclusion\n")
    for _, r in capped.iterrows():
        lines.append(
            f"- {r.family}: capped delta Q2={r.delta_ll_Q2_vs_anchor:+.4f}, "
            f"Q3={r.delta_ll_Q3_vs_anchor:+.4f}, Q2Q3={r.delta_ll_mean_Q2Q3_vs_anchor:+.4f}, "
            f"mean={r.delta_ll_mean_vs_anchor:+.4f}.\n"
        )

    lines.append("\n## Outputs\n")
    lines.append("- `experiments/q2q3_event_residual_diagnostic_results.csv`\n")
    lines.append("- `experiments/q2q3_event_residual_diagnostic_summary.csv`\n")
    lines.append("- `experiments/q2q3_event_residual_diagnostic_shifts.csv`\n")
    lines.append("- `experiments/q2q3_event_residual_diagnostic_selected_features.csv`\n")

    (EXP / "q2q3_event_residual_diagnostic_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote report", EXP / "q2q3_event_residual_diagnostic_report.md")


if __name__ == "__main__":
    main()
