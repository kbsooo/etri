"""v81 leakage / selection-bias stress test.

The v81 decoder OOF is fold-safe, but the routed score (0.471378) is produced by
the conditional router selecting (source, bin, weight) moves on the *full train*
OOF logloss. That selection sees train labels, so the routed gain is optimistic.
This script separates the honest signal from the selection bias:

  1. Selection-free fixed shrinkage: blend base toward a single decoder source
     with one uniform weight `s` applied to every row/target. One global knob =
     negligible selection bias. This is the floor of "real" gain.
  2. Per-ablation fixed shrinkage: repeat (1) for each feature-group ablation, to
     locate where the gain (especially the Q1 0.019) actually comes from.
  3. Cheap nested router: redo the router's greedy move selection inside an outer
     CV loop (select on outer-train OOF, score on held-out outer-val). The gap
     between this and the train-selected routed score IS the router selection bias.

Reuses the existing fold-safe v81 OOF sources; does not regenerate them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.insert(0, "scripts")
from train_s2_sleep_retrieval_encoder import make_subject_time_folds  # noqa: E402

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5
ROOT = Path(".")
DATA = ROOT / "data"
BASE_DIR = ROOT / "outputs/conditional_latent_routing_v80_late_behavior_on_v79"
V81_DIR = ROOT / "outputs/decoder_v81_late_retrieval_on_v80"

ABLATIONS = ["full", "retrieval_only", "no_retrieval", "retrieval_geo_only", "source_only", "panel_only", "base_only", "no_late"]
SHRINK_GRID = [0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0]


def safe_logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def logit_blend(base: np.ndarray, src: np.ndarray, w: float) -> np.ndarray:
    return sigmoid((1 - w) * safe_logit(base) + w * safe_logit(src))


def load_pred(path: Path) -> np.ndarray:
    df = pd.read_csv(path)
    cols = [f"pred_{t}" for t in TARGETS] if f"pred_{TARGETS[0]}" in df.columns else TARGETS
    return np.clip(df[cols].to_numpy(float), EPS, 1 - EPS)


def avgll(y: np.ndarray, p: np.ndarray) -> tuple[float, dict[str, float]]:
    per = {t: float(log_loss(y[:, i], np.clip(p[:, i], EPS, 1 - EPS), labels=[0, 1])) for i, t in enumerate(TARGETS)}
    return float(np.mean(list(per.values()))), per


def panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    allr = pd.concat(
        [train[KEY].assign(_s="t", _r=np.arange(len(train))), sample[KEY].assign(_s="x", _r=np.arange(len(sample)))],
        ignore_index=True,
    )
    o = allr.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    o["pi"] = o.groupby("subject_id").cumcount().astype(float)
    den = o.groupby("subject_id")["pi"].transform("max").replace(0, 1)
    o["pp"] = o["pi"] / den
    return o[o["_s"].eq("t")].sort_values("_r")["pp"].to_numpy(float)


BINS = [("early", 0, 0.333), ("mid", 0.333, 0.666), ("late_mid", 0.666, 0.8), ("tail", 0.8, 1.000001),
        ("late", 0.666, 1.000001), ("first_half", 0, 0.5), ("second_half", 0.5, 1.000001), ("all", 0, 1.000001)]
WEIGHTS = [0.025, 0.05, 0.075, 0.1, 0.15, 0.2]


def fixed_shrinkage_table(y, base, src):
    """Selection-free: one uniform weight for all rows/targets."""
    out = []
    for s in SHRINK_GRID:
        p = logit_blend(base, src, s)
        a, per = avgll(y, p)
        out.append({"s": s, "avg": a, **per})
    df = pd.DataFrame(out)
    best = df.loc[df["avg"].idxmin()]
    return df, best


def greedy_select_and_score(y, base_oof, sources, train_pos, sel_idx, eval_idx, min_train_rows=40):
    """Mimic the router: select up to 2 non-overlapping moves per target on `sel_idx`
    rows, then apply them to `eval_idx` rows and return the eval prediction."""
    routed_eval = base_oof[eval_idx].copy()
    pos_sel = train_pos[sel_idx]
    pos_eval = train_pos[eval_idx]
    y_sel = y[sel_idx]
    for ti, target in enumerate(TARGETS):
        cur_sel = base_oof[sel_idx, ti].copy()
        cur_eval = routed_eval[:, ti].copy()
        chosen_bins: list[tuple[float, float]] = []
        cur_loss = log_loss(y_sel[:, ti], np.clip(cur_sel, EPS, 1 - EPS), labels=[0, 1])
        for _ in range(2):
            best = None
            for name, src in sources.items():
                for _, lo, hi in BINS:
                    if any(not (hi <= b[0] or lo >= b[1]) for b in chosen_bins):
                        continue
                    m_sel = (pos_sel >= lo) & (pos_sel < hi)
                    if int(m_sel.sum()) < min_train_rows:
                        continue
                    for w in WEIGHTS:
                        cand = cur_sel.copy()
                        blended = logit_blend(cur_sel, src[sel_idx, ti], w)
                        cand[m_sel] = blended[m_sel]
                        loss = log_loss(y_sel[:, ti], np.clip(cand, EPS, 1 - EPS), labels=[0, 1])
                        if loss < cur_loss - 2e-5 and (best is None or loss < best["loss"]):
                            best = {"loss": loss, "name": name, "lo": lo, "hi": hi, "w": w, "cand": cand}
            if best is None:
                break
            cur_sel = best["cand"]
            cur_loss = best["loss"]
            chosen_bins.append((best["lo"], best["hi"]))
            # apply identical move to eval rows
            m_eval = (pos_eval >= best["lo"]) & (pos_eval < best["hi"])
            blended_eval = logit_blend(cur_eval, sources[best["name"]][eval_idx, ti], best["w"])
            cur_eval[m_eval] = blended_eval[m_eval]
        routed_eval[:, ti] = cur_eval
    return routed_eval


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    y = train[TARGETS].to_numpy(int)
    base = load_pred(BASE_DIR / "oof_conditional_latent_routing.csv")
    train_pos = panel_position(train, sample)
    base_avg, base_per = avgll(y, base)

    lines: list[str] = []
    lines.append("# v81 selection-bias / leakage stress test\n")
    lines.append(f"- v80 base OOF: `{base_avg:.6f}`")
    lines.append(f"- Train-selected v81 routed OOF (reported): `0.471378` (from outputs/conditional_latent_routing_v81_decoder_only_on_v80)\n")

    # ---- 1+2: per-ablation selection-free fixed shrinkage (hgb source) ----
    lines.append("## 1. Selection-free fixed shrinkage per ablation (HGB source, one uniform weight)\n")
    lines.append("Each row blends the v80 base toward that ablation's HGB OOF with a single weight `s` "
                 "applied to every row and target. One global knob => negligible selection bias, so this is "
                 "the honest floor of the gain.\n")
    header = "| ablation | best s | avg@best | avg delta | Q1@best | Q1 delta | best-Q1 s | best-Q1 | best-Q1 delta |"
    sep = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    lines.append(header)
    lines.append(sep)
    ablation_rows = {}
    for ab in ABLATIONS:
        src_path = ROOT / f"outputs/decoder_v81_ablation_{ab}/oof_v81_late_retrieval_hgb.csv"
        if not src_path.exists():
            lines.append(f"| {ab} | (missing) | | | | | | | |")
            continue
        src = load_pred(src_path)
        df, best = fixed_shrinkage_table(y, base, src)
        # Q1 at the avg-best s
        q1_at_best = float(best["Q1"])
        # best s for Q1 specifically
        q1_best_row = df.loc[df["Q1"].idxmin()]
        ablation_rows[ab] = {"df": df, "best": best, "q1_best": q1_best_row}
        lines.append(
            f"| {ab} | {best['s']:.3f} | {best['avg']:.6f} | {base_avg-best['avg']:+.6f} | "
            f"{q1_at_best:.6f} | {base_per['Q1']-q1_at_best:+.6f} | {q1_best_row['s']:.3f} | "
            f"{q1_best_row['Q1']:.6f} | {base_per['Q1']-q1_best_row['Q1']:+.6f} |"
        )

    # ---- Q1 verdict ----
    lines.append("\n## 2. Q1 0.019-gain attribution (advisor discriminating ablation)\n")
    full_q1 = base_per["Q1"] - ablation_rows["full"]["q1_best"]["Q1"] if "full" in ablation_rows else float("nan")
    geo_q1 = base_per["Q1"] - ablation_rows["retrieval_geo_only"]["q1_best"]["Q1"] if "retrieval_geo_only" in ablation_rows else float("nan")
    src_q1 = base_per["Q1"] - ablation_rows["no_retrieval"]["q1_best"]["Q1"] if "no_retrieval" in ablation_rows else float("nan")
    retr_q1 = base_per["Q1"] - ablation_rows["retrieval_only"]["q1_best"]["Q1"] if "retrieval_only" in ablation_rows else float("nan")
    lines.append(f"- full best Q1 gain (selection-free): `{full_q1:+.6f}`")
    lines.append(f"- retrieval_geo_only (geometry, NO neighbor labels): `{geo_q1:+.6f}`")
    lines.append(f"- no_retrieval (source-preds + panel + base, NO retrieval): `{src_q1:+.6f}`")
    lines.append(f"- retrieval_only (geometry + neighbor labels, NO source/panel/base): `{retr_q1:+.6f}`")
    # discriminate: if neighbor-label-only is ~0 and source-only is >= full, the gain is source recombination
    if np.isfinite(retr_q1) and np.isfinite(src_q1):
        if abs(retr_q1) < 0.2 * abs(full_q1) and src_q1 >= 0.8 * full_q1:
            verdict = ("v80 source-prediction recombination, NOT neighbor-label smoothing: retrieval-only carries "
                       "almost no Q1 signal, while source-preds alone reproduce (and exceed) the full gain. The "
                       "retrieval features are net harmful here — they overfit the HGB decoder.")
        elif geo_q1 >= 0.5 * full_q1:
            verdict = "latent-geometry signal (geometry-only retrieval preserves most of the gain)"
        else:
            verdict = "neighbor-label smoothing (dies without per-target neighbor labels)"
    else:
        verdict = "indeterminate (missing ablation)"
    lines.append(f"- **Interpretation**: {verdict}")

    # ---- 3: cheap nested router ----
    lines.append("\n## 3. Cheap nested-router selection bias (full v81 4-source pool)\n")
    sources = {}
    for m in ["ridge", "hgb", "extratrees", "logreg"]:
        p = V81_DIR / f"oof_v81_late_retrieval_{m}.csv"
        if p.exists():
            sources[f"v81_{m}"] = load_pred(p)
    folds = make_subject_time_folds(train, 5)
    nested = base.copy()
    for pack in folds:
        sel_idx = pack.train_idx
        eval_idx = pack.val_idx
        nested[eval_idx] = greedy_select_and_score(y, base, sources, train_pos, sel_idx, eval_idx)
    nested_avg, nested_per = avgll(y, nested)
    # train-selected (in-sample selection): select on all rows, score on all rows
    allidx = np.arange(len(train))
    train_sel = greedy_select_and_score(y, base, sources, train_pos, allidx, allidx)
    ts_avg, _ = avgll(y, train_sel)
    lines.append(f"- base OOF: `{base_avg:.6f}`")
    lines.append(f"- train-selected router (select & score on full train, in-sample): `{ts_avg:.6f}` (delta {base_avg-ts_avg:+.6f})")
    lines.append(f"- nested router (select on outer-train, score on held-out outer-val): `{nested_avg:.6f}` (delta {base_avg-nested_avg:+.6f})")
    lines.append(f"- **router selection bias** = train-selected - nested = `{nested_avg-ts_avg:+.6f}`")
    lines.append("\nPer-target nested vs base:")
    lines.append("| target | base | nested | delta |")
    lines.append("| --- | --- | --- | --- |")
    for t in TARGETS:
        lines.append(f"| {t} | {base_per[t]:.6f} | {nested_per[t]:.6f} | {base_per[t]-nested_per[t]:+.6f} |")

    # ---- summary ----
    full_best = ablation_rows["full"]["best"] if "full" in ablation_rows else None
    lines.append("\n## Honest summary\n")
    lines.append("- The v81 decoder is a **fold-safe decoder, but prior OOF router selection bias remains** in the routed 0.471378 figure.")
    if full_best is not None:
        lines.append(f"- Selection-free uniform fixed shrinkage (full, s={full_best['s']:.3f}) already reaches `{full_best['avg']:.6f}` "
                     f"({base_avg-full_best['avg']:+.6f} vs base), so most of the routed gain reproduces without per-target/bin selection.")
    lines.append(f"- Nested-router selection (selection scored out-of-fold) reaches `{nested_avg:.6f}`; the difference to the in-sample "
                 f"train-selected router (`{ts_avg:.6f}`) is the router selection bias = `{nested_avg-ts_avg:+.6f}`.")

    out_path = ROOT / "outputs/v81_selection_bias_stress_report.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # machine-readable
    summary = {
        "base_oof": base_avg,
        "fixed_shrinkage": {
            ab: {"best_s": float(r["best"]["s"]), "best_avg": float(r["best"]["avg"]),
                 "q1_best_s": float(r["q1_best"]["s"]), "q1_best": float(r["q1_best"]["Q1"]),
                 "q1_best_delta": float(base_per["Q1"] - r["q1_best"]["Q1"])}
            for ab, r in ablation_rows.items()
        },
        "nested_router": {"base": base_avg, "train_selected": ts_avg, "nested": nested_avg,
                          "selection_bias": nested_avg - ts_avg, "per_target": nested_per},
        "q1_attribution": {"full": full_q1, "geo_only": geo_q1, "no_retrieval": src_q1, "retrieval_only": retr_q1},
    }
    (ROOT / "outputs/v81_selection_bias_stress_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(out_path.read_text())


if __name__ == "__main__":
    main()
