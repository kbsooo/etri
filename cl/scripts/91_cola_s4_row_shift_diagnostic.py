#!/usr/bin/env python3
"""CoLa S4 row-shift diagnostic.

No submission by default? This script *does* create a clearly marked diagnostic
capped candidate only if intersection rows exist, but the report is the main output.

Question:
S4 rows where all three independent signals agree:
1) CoLa denoising latent says the row wants movement (anchor+latent shifts S4),
2) target_action_map says S4 is allowed to move,
3) existing sparse S4 context-token evidence is present.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEATURES = ROOT / "features"
EXP = ROOT / "experiments"
OUT = ROOT / "outputs"
LABEL = "S4"
SEED = 20260525


def load_train_test():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for df in (train, test):
        df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
        df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    train["is_train"] = 1
    test["is_train"] = 0
    return train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True), test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def anchor_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["subject_id", "lifelog_date"]].copy()
    out["dow"] = pd.to_datetime(out["lifelog_date"]).dt.dayofweek.astype(str)
    out["day_rank_subj"] = df.groupby("subject_id")["lifelog_date"].rank(method="first")
    out["day_rank_subj_z"] = out.groupby(df["subject_id"])["day_rank_subj"].transform(lambda s: (s - s.mean()) / (s.std() or 1.0)).fillna(0)
    return out


def fit_predict_s4(full: pd.DataFrame, latent: pd.DataFrame):
    df = full.merge(latent, on=["subject_id", "lifelog_date"], how="left")
    latent_cols = [c for c in latent.columns if c.startswith("cola_")]
    anc = anchor_frame(df)
    X_anchor = anc[["subject_id", "dow", "day_rank_subj_z"]].copy()
    Xa = pd.get_dummies(X_anchor, columns=["subject_id", "dow"], dummy_na=False)
    X_lat = pd.concat([X_anchor, df[latent_cols]], axis=1)
    Xl = pd.get_dummies(X_lat, columns=["subject_id", "dow"], dummy_na=False)
    train_mask = df.is_train.eq(1).to_numpy()
    test_mask = ~train_mask
    y = df.loc[train_mask, LABEL].astype(int).to_numpy()
    def model_predict(X):
        pipe = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler(with_mean=False)),
            ("clf", LogisticRegression(C=0.03, solver="liblinear", max_iter=1000, random_state=SEED)),
        ])
        pipe.fit(X.loc[train_mask], y)
        ptr = np.clip(pipe.predict_proba(X.loc[train_mask])[:, 1], 0.02, 0.98)
        pte = np.clip(pipe.predict_proba(X.loc[test_mask])[:, 1], 0.02, 0.98)
        return ptr, pte
    anchor_tr, anchor_te = model_predict(Xa)
    cola_tr, cola_te = model_predict(Xl)
    train_ll = {
        "anchor_train_logloss": float(log_loss(y, anchor_tr, labels=[0, 1])),
        "cola_train_logloss": float(log_loss(y, cola_tr, labels=[0, 1])),
    }
    return df.loc[test_mask, ["subject_id", "sleep_date", "lifelog_date"]].reset_index(drop=True), anchor_te, cola_te, train_ll


def build_diagnostic():
    train, test = load_train_test()
    latent = pd.read_parquet(FEATURES / "cola_denoising_latent_v1.parquet")
    latent["lifelog_date"] = pd.to_datetime(latent["lifelog_date"])
    full = pd.concat([train, test], ignore_index=True, sort=False)
    base_test, anchor_p, cola_p, info = fit_predict_s4(full, latent)
    diag = base_test.copy()
    diag["row_id"] = np.arange(len(diag))
    diag["s4_anchor_p"] = anchor_p
    diag["s4_cola_p"] = cola_p
    diag["cola_shift"] = diag.s4_cola_p - diag.s4_anchor_p
    diag["cola_abs_shift"] = diag.cola_shift.abs()
    diag["cola_direction"] = np.where(diag.cola_shift > 0, "UP", "DOWN")
    # robust threshold: top shifts but not too tiny. Top 20% or >=0.04.
    q80 = float(diag.cola_abs_shift.quantile(0.80))
    thresh = max(0.04, q80)
    diag["cola_says_move"] = diag.cola_abs_shift >= thresh

    regime = pd.read_csv(EXP / "test_regime_map.csv")
    regime["lifelog_date"] = pd.to_datetime(regime["lifelog_date"])
    s4_action = pd.read_csv(EXP / "target_action_map.csv")
    s4_action = s4_action[s4_action.target.eq("S4")].copy()
    s4_action["lifelog_date"] = pd.to_datetime(s4_action["lifelog_date"])
    keep_cols = ["row_id", "regime", "nearest_label_days", "neighbor_agree_S4", "neighbor_mean_S4", "coverage_anomaly_score", "s4_context_token_count"]
    diag = diag.merge(regime[keep_cols], on="row_id", how="left")
    action_cols = ["row_id", "action", "direction", "strength", "base_subject_prior", "candidate_hint_p", "candidate_delta", "reason"]
    diag = diag.merge(s4_action[action_cols], on="row_id", how="left")
    diag["action_allows_move"] = diag.action.isin(["MOVE", "TINY_MOVE"])
    diag["context_token_evidence"] = diag.s4_context_token_count.fillna(0).astype(int) > 0
    diag["direction_agree"] = diag.direction.eq(diag.cola_direction)
    # For strong context events, direction agreement is required for auto candidate.
    diag["three_way_intersection"] = diag.cola_says_move & diag.action_allows_move & diag.context_token_evidence
    diag["candidate_safe_intersection"] = diag.three_way_intersection & diag.direction_agree
    # Score: large CoLa shift + action strength + token count, penalize temporal disagreement uncertainty.
    diag["s4_cola_context_score"] = (
        diag.cola_abs_shift.rank(pct=True)
        + diag.strength.fillna(0) / max(float(diag.strength.fillna(0).max()), 1e-9)
        + np.minimum(diag.s4_context_token_count.fillna(0), 3) / 3.0
        + diag.direction_agree.astype(float) * 0.5
    )
    diag = diag.sort_values(["candidate_safe_intersection", "three_way_intersection", "s4_cola_context_score"], ascending=[False, False, False])
    return diag, info, thresh


def make_candidate(diag: pd.DataFrame):
    base_path = OUT / "submission_advanced76_context_temporal_prob.csv"
    if not base_path.exists():
        return None, None
    sub = pd.read_csv(base_path)
    out = sub.copy()
    safe = diag[diag.candidate_safe_intersection].copy()
    changes = []
    if len(safe):
        for _, r in safe.iterrows():
            i = int(r.row_id)
            old = float(out.loc[i, LABEL])
            # capped adjustment: do not replace with model; nudge toward CoLa but cap at 0.04.
            raw_delta = float(r.cola_shift) * 0.35
            delta = max(-0.04, min(0.04, raw_delta))
            new = float(np.clip(old + delta, 0.02, 0.98))
            out.loc[i, LABEL] = new
            changes.append({
                "row_id": i,
                "subject_id": r.subject_id,
                "lifelog_date": str(pd.Timestamp(r.lifelog_date).date()),
                "old_S4": old,
                "new_S4": new,
                "delta": new - old,
                "cola_shift": float(r.cola_shift),
                "action": r.action,
                "direction": r.direction,
                "s4_context_token_count": int(r.s4_context_token_count),
                "reason": r.reason,
            })
    cand_path = OUT / "submission_cola_s4_context_capped_diag_prob.csv"
    shift_path = EXP / "submission_cola_s4_context_capped_diag_prob_shift.csv"
    out.to_csv(cand_path, index=False)
    pd.DataFrame(changes).to_csv(shift_path, index=False)
    return cand_path, shift_path


def write_report(diag: pd.DataFrame, info: dict, thresh: float, cand_path, shift_path):
    report = []
    report.append("# CoLa S4 row-shift diagnostic\n")
    report.append("Goal: intersect CoLa latent S4 movement, target action map permission, and sparse S4 context-token evidence.\n")
    report.append("## Model/probe info\n")
    report.append(f"- anchor_train_logloss: `{info['anchor_train_logloss']:.4f}`")
    report.append(f"- cola_train_logloss: `{info['cola_train_logloss']:.4f}`")
    report.append(f"- cola_says_move threshold abs shift: `{thresh:.4f}`")
    report.append("\n## Counts\n")
    counts = pd.DataFrame([
        {"condition": "all_test_rows", "n": len(diag)},
        {"condition": "cola_says_move", "n": int(diag.cola_says_move.sum())},
        {"condition": "action_allows_move", "n": int(diag.action_allows_move.sum())},
        {"condition": "context_token_evidence", "n": int(diag.context_token_evidence.sum())},
        {"condition": "three_way_intersection", "n": int(diag.three_way_intersection.sum())},
        {"condition": "candidate_safe_intersection_direction_agree", "n": int(diag.candidate_safe_intersection.sum())},
    ])
    report.append(counts.to_markdown(index=False))
    cols = ["row_id","subject_id","lifelog_date","regime","s4_anchor_p","s4_cola_p","cola_shift","cola_direction","action","direction","strength","s4_context_token_count","neighbor_agree_S4","candidate_hint_p","candidate_delta","reason"]
    report.append("\n## Safe intersection rows\n")
    safe = diag[diag.candidate_safe_intersection][cols]
    report.append(safe.to_markdown(index=False, floatfmt=".4f") if len(safe) else "None.")
    report.append("\n## Three-way rows with direction conflict/weakness\n")
    weak = diag[diag.three_way_intersection & ~diag.candidate_safe_intersection][cols]
    report.append(weak.to_markdown(index=False, floatfmt=".4f") if len(weak) else "None.")
    report.append("\n## Top CoLa S4 shifts overall\n")
    top = diag.sort_values("cola_abs_shift", ascending=False).head(20)[cols + ["cola_says_move","action_allows_move","context_token_evidence","direction_agree"]]
    report.append(top.to_markdown(index=False, floatfmt=".4f"))
    report.append("\n## Candidate\n")
    if cand_path:
        report.append(f"- wrote diagnostic capped candidate: `{cand_path}`")
        report.append(f"- wrote shift file: `{shift_path}`")
        report.append("- This is not an automatic submit recommendation. It only nudges direction-agreeing intersection rows by `0.35 * cola_shift`, capped at ±0.04.")
    else:
        report.append("- no candidate file created because base anchor file was missing.")
    report.append("\n## Verdict\n")
    n_safe = int(diag.candidate_safe_intersection.sum())
    n_three = int(diag.three_way_intersection.sum())
    if n_safe:
        report.append(f"PARTIAL: {n_safe} row(s) pass strict intersection with direction agreement. Worth inspecting as S4-only capped diagnostic, not broad DL evidence.")
    elif n_three:
        report.append(f"WEAK: {n_three} row(s) pass three-way intersection but direction conflicts. Do not adjust automatically.")
    else:
        report.append("INVALIDATED for S4 adjustment: no row passes the three-way intersection.")
    (EXP / "cola_s4_row_shift_diagnostic_report.md").write_text("\n".join(report))


def main():
    EXP.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    diag, info, thresh = build_diagnostic()
    diag_path = EXP / "cola_s4_row_shift_diagnostic.csv"
    diag.to_csv(diag_path, index=False)
    cand_path, shift_path = make_candidate(diag)
    write_report(diag, info, thresh, cand_path, shift_path)
    print("wrote", diag_path)
    print("wrote", EXP / "cola_s4_row_shift_diagnostic_report.md")
    if cand_path:
        print("wrote", cand_path)
        print("wrote", shift_path)
    print("counts", {
        "cola_says_move": int(diag.cola_says_move.sum()),
        "action_allows_move": int(diag.action_allows_move.sum()),
        "context_token_evidence": int(diag.context_token_evidence.sum()),
        "three_way_intersection": int(diag.three_way_intersection.sum()),
        "safe_direction_agree": int(diag.candidate_safe_intersection.sum()),
    })
    safe_cols = ["row_id","subject_id","lifelog_date","s4_anchor_p","s4_cola_p","cola_shift","action","direction","s4_context_token_count","reason"]
    print(diag[diag.candidate_safe_intersection][safe_cols].to_string(index=False))


if __name__ == "__main__":
    main()
