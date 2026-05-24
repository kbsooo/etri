"""Q2 — Are S4 BSSID lifts genuine context-events, or sensor-availability proxies?

Hypothesis to discriminate:
  H_event:  BSSID appearance reflects being at a specific place that
            actually disrupts sleep (place/device → S4=1)
  H_avail:  BSSID appearance just means the phone was running and logging;
            other sensors are coincidentally informative for S4 the same way.

If H_avail, then *after controlling for HR/wifi/usage/light coverage* (which
also reflect phone+wearable presence), BSSID lift should shrink toward zero.
If H_event, the BSSID lift survives the controls.

For each top-N S4-associated subject-debiased BSSID/BLE/app token:
  1. compute raw lift = P(S4=1 | token present) - P(S4=1 | token absent)
  2. fit logistic on coverage controls only -> p_cov
  3. fit logistic on coverage controls + token indicator -> p_full
  4. partial effect = beta_token coefficient + delta-AUC
  5. report which tokens survive shrinkage.

Output:
  experiments/q2_bssid_event_vs_availability_report.md
  experiments/q2_bssid_event_vs_availability_tokens.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
COVERAGE_PARQUET = ROOT / "features" / "observation_coverage_features.parquet"
IDENTITY_PARQUET = ROOT / "features" / "observation_identity_token_features.parquet"
ADV_SUBJ_DEBIASED_CSV = ROOT / "experiments" / "advanced76_subject_debiased_token_association.csv"
REPORT_MD = ROOT / "experiments" / "q2_bssid_event_vs_availability_report.md"
TOKENS_CSV = ROOT / "experiments" / "q2_bssid_event_vs_availability_tokens.csv"


def load_data():
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    cov = pd.read_parquet(COVERAGE_PARQUET)
    if "date" in cov.columns and "lifelog_date" not in cov.columns:
        cov = cov.rename(columns={"date": "lifelog_date"})
    cov["lifelog_date"] = pd.to_datetime(cov["lifelog_date"]).dt.date.astype(str)
    ident = pd.read_parquet(IDENTITY_PARQUET)
    if "date" in ident.columns and "lifelog_date" not in ident.columns:
        ident = ident.rename(columns={"date": "lifelog_date"})
    if "lifelog_date" in ident.columns:
        ident["lifelog_date"] = pd.to_datetime(ident["lifelog_date"]).dt.date.astype(str)
    return tr, cov, ident


def top_s4_tokens(top_n: int = 30) -> list[str]:
    if not ADV_SUBJ_DEBIASED_CSV.exists():
        return []
    df = pd.read_csv(ADV_SUBJ_DEBIASED_CSV)
    s4 = df[df["target"] == "S4"].copy()
    s4["lift"] = s4["raw_rate_present"] - s4["raw_rate_absent"]
    s4 = s4.sort_values("lift", ascending=False)
    return s4["token"].head(top_n).tolist()


def fit_logloss_auc(X: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """5-fold leave-one-subject-block-style: just use in-sample for diagnostic
    relative comparison. Returns (LL, AUC, beta_token)."""
    if y.std() < 1e-6:
        return float("nan"), float("nan"), float("nan")
    means = np.nanmean(X, axis=0)
    Xi = np.where(np.isnan(X), means, X)
    clf = LogisticRegression(C=1.0, max_iter=2000)
    clf.fit(Xi, y)
    p = np.clip(clf.predict_proba(Xi)[:, 1], 0.03, 0.97)
    ll = float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())
    auc = float(roc_auc_score(y, p))
    beta_last = float(clf.coef_[0, -1]) if X.shape[1] > 0 else float("nan")
    return ll, auc, beta_last


def df_to_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    head = "| " + " | ".join(["", *map(str, cols)]) + " |"
    sep = "|" + "|".join(["---"] * (1 + len(cols))) + "|"
    lines = [head, sep]
    for ix, row in df.iterrows():
        cells = [str(ix)] + [f"{v:.4f}" if isinstance(v, (int, float, np.floating)) and not pd.isna(v) else str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    tr, cov, ident = load_data()
    print(f"train n={len(tr)}, coverage cols={cov.shape[1]}, identity cols={ident.shape[1]}")

    # build joined frame for train only
    df = tr.merge(cov, on=["subject_id", "lifelog_date"], how="left", suffixes=("", "_cov"))
    df = df.merge(ident, on=["subject_id", "lifelog_date"], how="left", suffixes=("", "_id"))

    cov_cols = [c for c in cov.columns if c not in ("subject_id", "lifelog_date", "split") and pd.api.types.is_numeric_dtype(cov[c])]
    # subject-block dummies for partialing out subject prevalence
    subj_dummies = pd.get_dummies(df["subject_id"], prefix="subj", drop_first=True)
    X_cov_base = pd.concat([df[cov_cols], subj_dummies], axis=1).to_numpy(dtype=float, na_value=0.0)

    y = df["S4"].astype(int).values

    print("baseline logistic on subject + coverage only...")
    ll_base, auc_base, _ = fit_logloss_auc(X_cov_base, y)
    print(f"  S4 LL={ll_base:.4f}  AUC={auc_base:.4f}")

    tokens = top_s4_tokens(top_n=30)
    print(f"found {len(tokens)} candidate S4 tokens to test")

    # mapping from token string to identity-parquet column
    ident_cols = set(ident.columns)
    rows = []
    for tok in tokens:
        # identity parquet columns are usually 'has_<token>' or just the token name.
        candidates = [tok, f"has_{tok}", tok.replace(":", "_"), f"has_{tok.replace(':', '_')}"]
        col = next((c for c in candidates if c in ident_cols), None)
        if col is None:
            # try a tail-match
            tail = tok.split(":")[-1]
            matches = [c for c in ident.columns if tail in c]
            if not matches:
                continue
            col = matches[0]
        v = df[col].to_numpy(dtype=float, na_value=0.0)
        if v.std() < 1e-6:
            continue
        X_full = np.column_stack([X_cov_base, v.reshape(-1, 1)])
        ll_full, auc_full, beta = fit_logloss_auc(X_full, y)
        # raw lift
        present_mask = v > 0
        n_pres = int(present_mask.sum())
        if n_pres < 5 or (len(present_mask) - n_pres) < 5:
            continue
        rate_pres = float(y[present_mask].mean())
        rate_abs = float(y[~present_mask].mean())
        raw_lift = rate_pres - rate_abs
        rows.append({
            "token": tok,
            "column_used": col,
            "n_present": n_pres,
            "raw_rate_present": rate_pres,
            "raw_rate_absent": rate_abs,
            "raw_lift": raw_lift,
            "ll_base_subj_cov": ll_base,
            "ll_with_token": ll_full,
            "auc_base_subj_cov": auc_base,
            "auc_with_token": auc_full,
            "delta_ll": ll_full - ll_base,
            "delta_auc": auc_full - auc_base,
            "beta_token_after_controls": beta,
        })

    out = pd.DataFrame(rows)
    if out.empty:
        print("no tokens evaluable — check identity parquet column naming")
        REPORT_MD.write_text("# Q2 — No tokens evaluable. Check identity parquet schema.\n")
        return

    out = out.sort_values("beta_token_after_controls", ascending=False, key=lambda s: s.abs())
    out["survives_strong"] = (out["beta_token_after_controls"].abs() > 0.2) & (out["delta_ll"] < -0.001)
    out["survives_any"] = (out["beta_token_after_controls"].abs() > 0.05) & (out["delta_ll"] < 0)

    TOKENS_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(TOKENS_CSV, index=False)
    print(f"wrote {TOKENS_CSV}")

    n_strong = int(out["survives_strong"].sum())
    n_any = int(out["survives_any"].sum())
    raw_lift_mean = float(out["raw_lift"].mean())
    delta_ll_mean = float(out["delta_ll"].mean())
    delta_auc_mean = float(out["delta_auc"].mean())

    lines = []
    lines.append("# Q2 — S4 BSSID tokens: context-event vs availability proxy\n")
    lines.append(
        "For each top S4-debiased token, add it to a logistic with "
        "**subject dummies + all coverage features** already partialled out, "
        "then check whether its coefficient and the model logloss/AUC improve.\n"
    )
    lines.append(
        f"\nBaseline (subject + coverage only): LL={ll_base:.4f}  AUC={auc_base:.4f}\n"
    )
    lines.append(
        f"\nTokens evaluated: **{len(out)}** of {len(tokens)} candidates "
        f"(others not found or constant).\n"
    )
    lines.append(
        f"\n- mean raw lift (P(S4|tok)-P(S4|no tok)): {raw_lift_mean:+.4f}\n"
        f"- mean delta LL after adding token over base: {delta_ll_mean:+.4f}\n"
        f"- mean delta AUC: {delta_auc_mean:+.4f}\n"
        f"- tokens surviving |beta|>0.2 AND delta_LL<-0.001: **{n_strong}** / {len(out)}\n"
        f"- tokens with any partial effect (|beta|>0.05 AND delta_LL<0): **{n_any}** / {len(out)}\n"
    )

    lines.append("\n## 1. Top-15 tokens by |beta_token_after_controls|\n")
    keep = ["token", "n_present", "raw_lift", "beta_token_after_controls", "delta_ll", "delta_auc", "survives_strong"]
    lines.append(df_to_md(out[keep].head(15).round(4).reset_index(drop=True)))

    lines.append("\n\n## 2. Interpretation\n")
    survived_strong_frac = n_strong / len(out) if len(out) else 0
    if survived_strong_frac >= 0.5:
        verdict = (
            "**Mostly context-event.** Majority of high-lift tokens retain their effect "
            "after partialling out subject identity and coverage. S4 context features are "
            "genuinely place/device events and deserve a small capped specialist."
        )
    elif survived_strong_frac >= 0.2:
        verdict = (
            "**Mixed.** Some tokens are true context events; many were sensor-availability "
            "proxies. Use a curated subset, not raw token feature dump."
        )
    else:
        verdict = (
            "**Mostly availability proxy.** Once subject + coverage are controlled, most "
            "BSSID lifts vanish. S4 specialist via raw tokens is brittle; coverage-gated "
            "anchor is enough."
        )
    lines.append(verdict + "\n")
    lines.append(
        "\nDecision rules:\n"
        "- Cap any S4 token-based correction to use only `survives_strong` tokens.\n"
        "- If `n_strong == 0`, do not build an S4 BSSID specialist.\n"
        "- If 1-3 tokens survive strongly, use them as event indicators with cap ±0.10.\n"
        "- The baseline (subject + coverage only) LL is itself an interesting anchor; "
        "compare to subject_prior_a20 to see if coverage controls already buy lift.\n"
    )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")
    print("\nsurvivors_strong:")
    print(out[out["survives_strong"]][["token", "n_present", "raw_lift", "beta_token_after_controls", "delta_ll"]])


if __name__ == "__main__":
    main()
