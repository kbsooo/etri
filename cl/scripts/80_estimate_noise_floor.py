"""Q3 — irreducible noise floor.

Question: how low can mean logloss possibly go on this dataset?
Compute four nested upper bounds + a bootstrap CI on the current anchor.

1. marginal_entropy           = H(Y_t)                 (no info)
2. subject_entropy            = E_s[H(Y_t | subject)]  (subject-only info)
3. subject_3day_entropy       = E[H(Y_t | subject, nearest-3-day-labels mean)]
                                 (subject + local temporal info)
4. oracle_LOO_logloss         = mean logloss of LOO empirical (subject, target) rate
                                 over the actual train labels
                                 — this is the achievable floor if labels are
                                   pure noisy reads of a stable per-(subj,target) p

Plus:
5. bootstrap CI on subject_prior_a20 over the full train (n=450) and over the
   mirror_v1 valid sets

Output:
  experiments/q3_noise_floor_report.md
  experiments/q3_noise_floor_per_target.csv

This is diagnostic only. No model is trained. No submission generated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
MIRROR_FOLDS = ROOT / "outputs" / "validation" / "folds_subject_mirror_v1.json"
REPORT_MD = ROOT / "experiments" / "q3_noise_floor_report.md"
PER_TARGET_CSV = ROOT / "experiments" / "q3_noise_floor_per_target.csv"

CLIP = (0.03, 0.97)


def H_of_rate(p: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Bernoulli entropy at rate p. Stable around 0/1."""
    p = np.clip(p, eps, 1 - eps)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


def clip_p(p):
    return np.clip(p, CLIP[0], CLIP[1])


def marginal_entropy(df: pd.DataFrame) -> dict[str, float]:
    out = {}
    for t in LABELS:
        p = float(df[t].mean())
        out[t] = float(H_of_rate(np.array([p]))[0])
    return out


def subject_entropy(df: pd.DataFrame) -> dict[str, float]:
    """E_s[H(Y|subject)] weighted by subject row counts."""
    out = {}
    for t in LABELS:
        per_s = df.groupby("subject_id")[t].agg(["mean", "count"])
        H = H_of_rate(per_s["mean"].values)
        w = per_s["count"].values / per_s["count"].sum()
        out[t] = float((H * w).sum())
    return out


def subject_3day_entropy(df: pd.DataFrame, k: int = 3) -> dict[str, float]:
    """Conditional entropy when prediction uses the average of the k nearest
    same-subject train labels (LOO). Stable for binary Y."""
    out = {}
    df = df.copy()
    df["_d"] = pd.to_datetime(df["lifelog_date"])
    df = df.sort_values(["subject_id", "_d"]).reset_index(drop=True)
    for t in LABELS:
        preds = np.zeros(len(df))
        for s, g in df.groupby("subject_id"):
            idx = g.index.values
            dates = g["_d"].values
            labels = g[t].values.astype(float)
            global_p = float(labels.mean())
            for i, gi in enumerate(idx):
                others_mask = np.ones(len(g), dtype=bool)
                others_mask[i] = False
                if not others_mask.any():
                    preds[gi] = global_p
                    continue
                diffs = np.abs((dates - dates[i]).astype("timedelta64[D]").astype(int))
                diffs_others = diffs[others_mask]
                labels_others = labels[others_mask]
                order = np.argsort(diffs_others)[:k]
                preds[gi] = float(labels_others[order].mean())
        # this preds *is* the LOO oracle for this conditioning;
        # its logloss against the true labels is the achievable bound.
        out[t] = float(logloss(df[t].astype(int).values, clip_p(preds)))
    return out


def oracle_LOO_logloss(df: pd.DataFrame) -> dict[str, float]:
    """LOO empirical (subject) rate as predictor. With clip. Per target."""
    out = {}
    for t in LABELS:
        per_s = df.groupby("subject_id")[t].agg(["sum", "count"]).rename(columns={"sum": "pos", "count": "n"})
        per_s = per_s.to_dict("index")
        preds = np.zeros(len(df))
        ys = df[t].astype(int).values
        for i, (s, y) in enumerate(zip(df["subject_id"].values, ys)):
            d = per_s[s]
            n_loo = d["n"] - 1
            if n_loo <= 0:
                preds[i] = float(df[t].mean())
            else:
                preds[i] = (d["pos"] - y) / n_loo
        out[t] = float(logloss(ys, clip_p(preds)))
    return out


def bootstrap_subject_prior_CI(df: pd.DataFrame, alpha: float = 20.0, B: int = 2000, seed: int = 0) -> dict[str, dict[str, float]]:
    """Bootstrap rows -> recompute subject_prior_a20 -> score on the original
    train. Tells us how unstable the anchor itself is at n=450."""
    rng = np.random.default_rng(seed)
    n = len(df)
    out = {t: [] for t in LABELS}
    overall = []
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        sub = df.iloc[idx]
        per_t = {}
        for t in LABELS:
            g = float(sub[t].mean())
            ps = sub.groupby("subject_id")[t].sum()
            ns = sub.groupby("subject_id")[t].count()
            smoothed = ((ps + alpha * g) / (ns + alpha)).to_dict()
            preds = np.array([smoothed.get(s, g) for s in df["subject_id"]])
            per_t[t] = float(logloss(df[t].astype(int).values, clip_p(preds)))
        for t, v in per_t.items():
            out[t].append(v)
        overall.append(float(np.mean(list(per_t.values()))))
    res = {}
    for t in LABELS:
        a = np.array(out[t])
        res[t] = {
            "mean": float(a.mean()),
            "lo": float(np.quantile(a, 0.025)),
            "hi": float(np.quantile(a, 0.975)),
        }
    overall_a = np.array(overall)
    res["__avg__"] = {
        "mean": float(overall_a.mean()),
        "lo": float(np.quantile(overall_a, 0.025)),
        "hi": float(np.quantile(overall_a, 0.975)),
    }
    return res


def df_to_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    head = "| target | " + " | ".join(map(str, cols)) + " |"
    sep = "|" + "|".join(["---"] * (1 + len(cols))) + "|"
    lines = [head, sep]
    for ix, row in df.iterrows():
        cells = [str(ix)] + [f"{v:.4f}" if isinstance(v, (int, float, np.floating)) and not pd.isna(v) else str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    df = pd.read_csv(TRAIN_CSV)
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"]).dt.date.astype(str)

    print("computing nested entropies / oracle...")
    H1 = marginal_entropy(df)
    H2 = subject_entropy(df)
    H3 = subject_3day_entropy(df, k=3)
    O = oracle_LOO_logloss(df)

    per_t = pd.DataFrame({
        "marginal_H": pd.Series(H1),
        "subject_H": pd.Series(H2),
        "subject_3day_H": pd.Series(H3),
        "oracle_subj_LOO_ll": pd.Series(O),
    })
    per_t.loc["__mean__"] = per_t.mean(axis=0)
    print(per_t.round(4))

    print("\nbootstrap subject_prior_a20 CI on train (B=2000)...")
    boot = bootstrap_subject_prior_CI(df, alpha=20.0, B=2000)
    boot_df = pd.DataFrame(boot).T[["mean", "lo", "hi"]]
    print(boot_df.round(4))

    PER_TARGET_CSV.parent.mkdir(parents=True, exist_ok=True)
    per_t.to_csv(PER_TARGET_CSV)
    boot_df.to_csv(PER_TARGET_CSV.with_suffix(".bootstrap.csv"))

    lines = []
    lines.append("# Q3 — Irreducible noise floor\n")
    lines.append(
        "Goal: estimate the *lowest* mean logloss anyone could reach on this dataset, "
        "given that labels are noisy binary self-reports.\n"
    )
    lines.append("\n## 1. Nested entropy / oracle bounds (lower is better)\n")
    lines.append(
        "Bounds become progressively tighter as the predictor uses more info. The "
        "*achievable floor* is somewhere between `subject_3day_H` (lots of info) and "
        "`oracle_subj_LOO_ll` (subject-only info, no temporal structure).\n"
    )
    lines.append(df_to_md(per_t.round(4)))

    lines.append("\n\n## 2. Bootstrap CI on `subject_prior_a20` (B=2000, train-on-bootstrap, score-on-original)\n")
    lines.append(df_to_md(boot_df.round(4)))

    avg_subj = per_t.loc["__mean__", "subject_H"]
    avg_3day = per_t.loc["__mean__", "subject_3day_H"]
    avg_oracle = per_t.loc["__mean__", "oracle_subj_LOO_ll"]
    boot_mean = boot["__avg__"]["mean"]
    boot_lo = boot["__avg__"]["lo"]
    boot_hi = boot["__avg__"]["hi"]

    lines.append("\n\n## 3. Interpretation\n")
    lines.append(
        f"- **marginal H** (no info): {per_t.loc['__mean__','marginal_H']:.4f} — random baseline.\n"
        f"- **subject H** (E_s[H(Y|s)]): {avg_subj:.4f} — what subject-only prior buys *if* labels are pure Bernoulli at the per-subject rate.\n"
        f"- **subject+3-day-neighbor H**: {avg_3day:.4f} — what tightening with same-subject ±3-day local labels buys.\n"
        f"- **oracle subject LOO**: {avg_oracle:.4f} — actually-achieved logloss using the LOO subject mean on the real train labels. This is `subject_prior_a∞`.\n"
        f"- **subject_prior_a20 bootstrap CI**: {boot_mean:.4f} [{boot_lo:.4f}, {boot_hi:.4f}].\n"
    )
    lines.append(
        f"\nDelta available *below the subject anchor*: "
        f"`subject_3day_H − subject_H` = {avg_3day - avg_subj:+.4f}.\n"
        f"If this delta is negative, exploiting same-subject local temporal info "
        f"is mathematically allowed to lower mean logloss by ~|delta|.\n"
        f"If near zero, local temporal info adds nothing on top of subject prior.\n"
    )
    lines.append(
        "\n### Decision implication\n"
        "- If `subject_3day_H ≈ subject_H` → Q-family hole interpolation is *not* a free lunch; "
        "the anchor already captures what neighbor labels would add.\n"
        "- If `subject_3day_H < subject_H` by >0.02 → there is real, measurable headroom for "
        "Q-family hole specialists.\n"
        "- If `oracle_subj_LOO_ll < subject_prior_a20_bootstrap_mean − 0.01` → α=20 smoothing "
        "is throwing away some subject signal; try smaller α.\n"
        "- The bootstrap CI width tells how much fold-to-fold noise to expect on the anchor "
        "alone; differences inside that CI are *not* real improvements.\n"
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {REPORT_MD}")
    print(f"wrote {PER_TARGET_CSV}")


if __name__ == "__main__":
    main()
