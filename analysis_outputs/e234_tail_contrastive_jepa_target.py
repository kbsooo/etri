#!/usr/bin/env python3
"""E234: tail-contrastive JEPA target representation.

E233 rejected reusing support probabilities as soft amplitude heads. This
experiment changes the target representation instead of the post-hoc gate:

- risk target: predict high-adverse OOF tail membership.
- contrastive target: train only on high-positive vs high-adverse OOF tails.

The question is whether a target-specific tail representation can identify rows
where the E216/E224 movement should be dropped, and whether Q3 drops align with
the public-free E230 Q3 tail anatomy. No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
import sys
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import TARGETS, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402


RNG = 20260530 + 234
EPS = 1.0e-12

OOF_OUT = OUT / "e234_tail_contrastive_jepa_target_oof.csv"
SELECTED_OUT = OUT / "e234_tail_contrastive_jepa_target_selected.csv"
ALIGN_OUT = OUT / "e234_tail_contrastive_jepa_target_test_alignment.csv"
REPORT_OUT = OUT / "e234_tail_contrastive_jepa_target_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(np.float64)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    yy = np.asarray(y)
    mask = ~pd.isna(yy)
    yy = yy[mask].astype(int)
    pp = np.asarray(p, dtype=np.float64)[mask]
    if len(yy) == 0 or len(np.unique(yy)) < 2:
        return float("nan")
    return float(roc_auc_score(yy, pp))


def safe_logloss(y: np.ndarray, p: np.ndarray) -> float:
    yy = np.asarray(y)
    mask = ~pd.isna(yy)
    yy = yy[mask].astype(int)
    pp = clip_prob(np.asarray(p, dtype=np.float64)[mask])
    if len(yy) == 0:
        return float("nan")
    return float(log_loss(yy, pp, labels=[0, 1]))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if float(np.std(aa)) <= EPS or float(np.std(bb)) <= EPS:
        return 0.0
    return float(np.corrcoef(aa, bb)[0, 1])


def rank01(values: np.ndarray) -> np.ndarray:
    vals = np.asarray(values, dtype=np.float64)
    if len(vals) <= 1:
        return np.zeros_like(vals)
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(len(vals), dtype=np.float64)
    ranks[order] = np.arange(len(vals), dtype=np.float64)
    return ranks / max(len(vals) - 1, 1)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def model_defs() -> dict[str, Any]:
    return {
        "lr_l2_c0p10": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.10,
                        solver="lbfgs",
                        class_weight="balanced",
                        max_iter=3000,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
        "hgb_shallow": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                (
                    "clf",
                    HistGradientBoostingClassifier(
                        max_iter=80,
                        learning_rate=0.035,
                        max_leaf_nodes=7,
                        min_samples_leaf=16,
                        l2_regularization=0.8,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
    }


def model_fit_predict(model: Any, x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    yy = np.asarray(y_train, dtype=int)
    if len(yy) == 0:
        return np.full(len(x_pred), 0.5, dtype=np.float64)
    if len(np.unique(yy)) < 2:
        return np.full(len(x_pred), float(np.mean(yy)), dtype=np.float64)
    fitted = clone(model)
    fitted.fit(x_train, yy)
    return clip_prob(fitted.predict_proba(x_pred)[:, 1])


def add_true_labels(train_long: pd.DataFrame, train_raw: pd.DataFrame) -> pd.DataFrame:
    y = train_raw[TARGETS].to_numpy(dtype=int)
    out = train_long.copy()
    idx = [TARGETS.index(t) for t in out["target_name"]]
    out["true_label"] = y[out["row_idx"].to_numpy(dtype=int), np.asarray(idx, dtype=int)]
    return out


def fold_iterator(split_name: str, df: pd.DataFrame) -> Any:
    y_split = df["support_label"].to_numpy(dtype=int)
    groups = df["subject_id"].astype(str).to_numpy()
    if split_name == "subject5":
        return GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(df, y_split, groups)
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG).split(df, y_split)


def labels_from_benefit(benefit: np.ndarray, kind: str, q: float) -> tuple[np.ndarray, np.ndarray, float, float]:
    low = float(np.quantile(benefit, q))
    high = float(np.quantile(benefit, 1.0 - q))
    if kind == "risk":
        return (benefit <= low).astype(int), np.ones(len(benefit), dtype=bool), low, high
    if kind == "contrast":
        mask = (benefit <= low) | (benefit >= high)
        label = (benefit >= high).astype(int)
        return label, mask, low, high
    raise ValueError(kind)


def oof_tail_predict(
    model: Any,
    split_name: str,
    df: pd.DataFrame,
    cols: list[str],
    kind: str,
    q: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pred = np.full(len(df), np.nan, dtype=np.float64)
    eval_label = np.full(len(df), np.nan, dtype=np.float64)
    eval_mask = np.zeros(len(df), dtype=bool)
    benefit = df["benefit"].to_numpy(dtype=np.float64)
    for train_idx, val_idx in fold_iterator(split_name, df):
        y_train_all, train_mask, low, high = labels_from_benefit(benefit[train_idx], kind, q)
        if kind == "risk":
            x_fit = df.iloc[train_idx][cols]
            y_fit = y_train_all
            eval_label[val_idx] = (benefit[val_idx] <= low).astype(float)
            eval_mask[val_idx] = True
        else:
            fit_idx = np.asarray(train_idx, dtype=int)[train_mask]
            x_fit = df.iloc[fit_idx][cols]
            y_fit = y_train_all[train_mask]
            val_tail = (benefit[val_idx] <= low) | (benefit[val_idx] >= high)
            eval_label[val_idx[val_tail]] = (benefit[val_idx[val_tail]] >= high).astype(float)
            eval_mask[val_idx[val_tail]] = True
        pred[val_idx] = model_fit_predict(model, x_fit, y_fit, df.iloc[val_idx][cols])
    if np.isnan(pred).any():
        raise RuntimeError(f"NaN OOF prediction for {kind} q={q} {split_name}")
    return clip_prob(pred), eval_label, eval_mask


def fit_full_tail_predict(
    model: Any,
    train_df: pd.DataFrame,
    sub_df: pd.DataFrame,
    cols: list[str],
    kind: str,
    q: float,
) -> np.ndarray:
    labels, mask, _, _ = labels_from_benefit(train_df["benefit"].to_numpy(dtype=np.float64), kind, q)
    fit_df = train_df if kind == "risk" else train_df.loc[mask]
    y_fit = labels if kind == "risk" else labels[mask]
    return model_fit_predict(model, fit_df[cols], y_fit, sub_df[cols])


def amplitude_policies(kind: str, prob: np.ndarray) -> dict[str, np.ndarray]:
    p = clip_prob(prob)
    n = len(p)
    policies: dict[str, np.ndarray] = {}
    if kind == "risk":
        risk = p
        policies["soft_inverse_risk"] = 1.0 - risk
        policies["soft_inverse_risk_pow2"] = np.square(1.0 - risk)
        policies["risk_linear_t0p50"] = 1.0 - np.clip((risk - 0.50) / 0.50, 0.0, 1.0)
        policies["risk_linear_t0p60"] = 1.0 - np.clip((risk - 0.60) / 0.40, 0.0, 1.0)
        order = np.argsort(-risk, kind="mergesort")
        for k in [10, 13, 21, 25, 50]:
            kk = min(k, n)
            amp = np.ones(n, dtype=np.float64)
            amp[order[:kk]] = 0.0
            policies[f"drop_risk_top{kk}"] = amp
        for frac in [0.05, 0.10, 0.15, 0.20]:
            kk = max(1, int(round(n * frac)))
            amp = np.ones(n, dtype=np.float64)
            amp[order[:kk]] = 0.0
            policies[f"drop_risk_p{int(frac * 100):02d}"] = amp
    else:
        pos = p
        policies["soft_positive_tail"] = pos
        policies["soft_positive_tail_pow2"] = np.square(pos)
        policies["pos_linear_t0p40"] = np.clip((pos - 0.40) / 0.60, 0.0, 1.0)
        policies["pos_linear_t0p50"] = np.clip((pos - 0.50) / 0.50, 0.0, 1.0)
        order = np.argsort(pos, kind="mergesort")
        for k in [10, 13, 21, 25, 50]:
            kk = min(k, n)
            amp = np.ones(n, dtype=np.float64)
            amp[order[:kk]] = 0.0
            policies[f"drop_lowpos_top{kk}"] = amp
        for frac in [0.05, 0.10, 0.15, 0.20]:
            kk = max(1, int(round(n * frac)))
            amp = np.ones(n, dtype=np.float64)
            amp[order[:kk]] = 0.0
            policies[f"drop_lowpos_p{int(frac * 100):02d}"] = amp
    return policies


def scaled_prob(base: np.ndarray, full: np.ndarray, amp: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base) + np.asarray(amp, dtype=np.float64) * (logit(full) - logit(base))))


def subject_stats(df: pd.DataFrame, y: np.ndarray, base: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    vals: list[float] = []
    for _, idx in df.groupby("subject_id").groups.items():
        arr = np.asarray(list(idx), dtype=int)
        vals.append(float(loss_vec(y[arr], pred[arr]).mean() - loss_vec(y[arr], base[arr]).mean()))
    vv = np.asarray(vals, dtype=np.float64)
    return float(vv.mean()), float(np.mean(vv < 0.0))


def eval_policy(
    df: pd.DataFrame,
    task: str,
    view: str,
    model_name: str,
    split: str,
    kind: str,
    q: float,
    policy: str,
    prob: np.ndarray,
    eval_label: np.ndarray,
    amp: np.ndarray,
) -> dict[str, Any]:
    true_y = df["true_label"].to_numpy(dtype=int)
    base = df["base_prob"].to_numpy(dtype=np.float64)
    full = df["full_prob"].to_numpy(dtype=np.float64)
    benefit = df["benefit"].to_numpy(dtype=np.float64)
    pred = scaled_prob(base, full, amp)
    base_loss = loss_vec(true_y, base)
    full_loss = loss_vec(true_y, full)
    pred_loss = loss_vec(true_y, pred)
    full_delta = float(full_loss.mean() - base_loss.mean())
    target_delta = float(pred_loss.mean() - base_loss.mean())
    full_subject_delta, full_subject_win = subject_stats(df, true_y, base, full)
    subject_delta, subject_win = subject_stats(df, true_y, base, pred)
    dropped = np.asarray(amp) < 0.05
    moved = ~dropped
    eval_mask = ~pd.isna(eval_label)
    return {
        "task": task,
        "view": view,
        "model": model_name,
        "split": split,
        "target_kind": kind,
        "tail_q": q,
        "policy": policy,
        "tail_auc": safe_auc(eval_label, prob),
        "tail_logloss": safe_logloss(eval_label, prob),
        "tail_brier": float(brier_score_loss(eval_label[eval_mask].astype(int), clip_prob(prob[eval_mask])))
        if eval_mask.any()
        else np.nan,
        "corr_benefit": corr(prob, benefit),
        "prob_mean": float(np.mean(prob)),
        "target_delta": target_delta,
        "full_target_delta": full_delta,
        "loss_vs_full": target_delta - full_delta,
        "overall_delta": target_delta / len(TARGETS),
        "full_subject_delta": full_subject_delta,
        "full_subject_win": full_subject_win,
        "subject_delta": subject_delta,
        "subject_win_rate": subject_win,
        "mean_amp": float(np.mean(amp)),
        "dropped_rows": int(np.sum(dropped)),
        "kept_rows": int(np.sum(moved)),
        "dropped_mean_benefit": float(np.mean(benefit[dropped])) if dropped.any() else np.nan,
        "kept_mean_benefit": float(np.mean(benefit[moved])) if moved.any() else np.nan,
        "dropped_support_rate": float(np.mean(df["support_label"].to_numpy(dtype=int)[dropped])) if dropped.any() else np.nan,
        "beats_full": bool(target_delta < full_delta - 1.0e-5),
        "stress_promote": bool(
            target_delta < full_delta - 1.0e-5
            and subject_win >= max(0.60, full_subject_win - 0.05)
            and (not dropped.any() or float(np.mean(benefit[dropped])) < 0.0)
        ),
    }


def q3_prior_sets() -> dict[str, set[int]]:
    sample = e230.load_sub(e230.A2C8).sort_values(e230.KEYS).reset_index(drop=True)
    priors = e230.e162.prior_arrays(sample)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)
    base_spec = e230.e222.Candidate(
        candidate_id="e224_original",
        file_name=e230.E224_FILE,
        anchor_file=e230.E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current JEPA-first E224 candidate.",
    )
    cells = e230.e222.cell_table(base_spec, "graft_vs_e154", e224, e154, e230.E154_FILE, priors, sample)
    q3 = cells[cells["target"].eq("Q3")].copy()
    q3["risk"] = (0.5 - q3["support_prob_focus"]) * q3["swing"]
    return {
        "e230_q3_risk_top21": set(q3.sort_values("risk", ascending=False).head(21)["row_idx"].astype(int)),
        "e230_q3_swing_top25": set(q3.sort_values("swing", ascending=False).head(25)["row_idx"].astype(int)),
        "e230_q3_expected_positive": set(q3[q3["expected_focus"] > 0]["row_idx"].astype(int)),
    }


def test_alignment(
    selected: pd.DataFrame,
    train_long: pd.DataFrame,
    sub_long: pd.DataFrame,
    feats: dict[str, list[str]],
) -> pd.DataFrame:
    if selected.empty:
        return pd.DataFrame()
    prior_sets = q3_prior_sets()
    rows: list[dict[str, Any]] = []
    models = model_defs()
    for _, row in selected.head(30).iterrows():
        task = str(row["task"])
        tr = train_long[train_long["task_name"] == task].reset_index(drop=True)
        te = sub_long[sub_long["task_name"] == task].reset_index(drop=True)
        cols = feats[str(row["view"])]
        prob = fit_full_tail_predict(
            models[str(row["model"])],
            tr,
            te,
            cols,
            str(row["target_kind"]),
            float(row["tail_q"]),
        )
        amps = amplitude_policies(str(row["target_kind"]), prob)
        amp = amps[str(row["policy"])]
        dropped = set(np.where(amp < 0.05)[0].astype(int).tolist())
        rec: dict[str, Any] = {
            "task": task,
            "view": row["view"],
            "model": row["model"],
            "target_kind": row["target_kind"],
            "tail_q": float(row["tail_q"]),
            "policy": row["policy"],
            "sub_mean_prob": float(np.mean(prob)),
            "sub_mean_amp": float(np.mean(amp)),
            "sub_dropped_rows": int(len(dropped)),
            "sub_p10_prob": float(np.quantile(prob, 0.10)),
            "sub_p50_prob": float(np.quantile(prob, 0.50)),
            "sub_p90_prob": float(np.quantile(prob, 0.90)),
        }
        if task == "q3_e224":
            for name, prior in prior_sets.items():
                rec[f"{name}_overlap"] = int(len(dropped & prior))
                rec[f"{name}_jaccard"] = float(len(dropped & prior) / max(len(dropped | prior), 1))
        rows.append(rec)
    return pd.DataFrame(rows)


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_raw, train_long, sub_long, _ = e232.build_long_frames()
    train_long = add_true_labels(train_long, train_raw)
    feats = e232.feature_sets(train_long)
    feats = {name: [c for c in cols if c != "true_label"] for name, cols in feats.items()}

    models = model_defs()
    rows: list[dict[str, Any]] = []
    for task in sorted(train_long["task_name"].unique()):
        df = train_long[train_long["task_name"] == task].reset_index(drop=True)
        for view, cols in feats.items():
            for model_name, model in models.items():
                for split in ["stratified5", "subject5"]:
                    for kind in ["risk", "contrast"]:
                        for q in [0.20, 0.30]:
                            prob, eval_label, _ = oof_tail_predict(model, split, df, cols, kind, q)
                            for policy, amp in amplitude_policies(kind, prob).items():
                                rows.append(
                                    eval_policy(
                                        df,
                                        task,
                                        view,
                                        model_name,
                                        split,
                                        kind,
                                        q,
                                        policy,
                                        prob,
                                        eval_label,
                                        amp,
                                    )
                                )
    out = pd.DataFrame(rows).sort_values(["stress_promote", "loss_vs_full"], ascending=[False, True])
    selected = pd.concat(
        [
            out[out["stress_promote"]],
            out.sort_values(["task", "loss_vs_full"], ascending=[True, True]).groupby("task").head(8),
        ],
        ignore_index=True,
    ).drop_duplicates(
        ["task", "view", "model", "split", "target_kind", "tail_q", "policy"]
    ).sort_values(["stress_promote", "task", "loss_vs_full"], ascending=[False, True, True])
    align = test_alignment(selected, train_long, sub_long, feats)

    out.to_csv(OOF_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    align.to_csv(ALIGN_OUT, index=False)
    write_report(out, selected, align)
    return out, selected, align


def write_report(out: pd.DataFrame, selected: pd.DataFrame, align: pd.DataFrame) -> None:
    task_summary = (
        out.groupby("task", as_index=False)
        .agg(
            best_loss_vs_full=("loss_vs_full", "min"),
            best_delta=("target_delta", "min"),
            full_delta=("full_target_delta", "first"),
            max_tail_auc=("tail_auc", "max"),
            promote_count=("stress_promote", "sum"),
        )
        .sort_values("best_loss_vs_full")
    )
    best = out.sort_values(["task", "loss_vs_full"], ascending=[True, True]).groupby("task").head(5)
    promoted = out[out["stress_promote"]].sort_values("loss_vs_full")
    q3_align = align[align["task"].eq("q3_e224")].copy() if not align.empty else pd.DataFrame()
    q3_best_overlap = (
        int(q3_align.get("e230_q3_risk_top21_overlap", pd.Series([0])).max()) if not q3_align.empty else 0
    )
    lines = [
        "# E234 Tail-Contrastive JEPA Target",
        "",
        "## Question",
        "",
        "Does changing the JEPA target from all-row support to high-impact tail representation make the E216/E224 movement more translatable?",
        "",
        "## Observed Read",
        "",
        f"- Promoted tail-contrastive policies: `{int(out['stress_promote'].sum())}`.",
        f"- Best Q3 dropped-row overlap with E230 risk-top21 among selected rows: `{q3_best_overlap}`.",
        "",
        "A healthy result needs more than tail AUC: it must beat the full movement OOF, keep subject stress alive, and for Q3 it should drop rows that resemble the E230 public-free fragile tail.",
        "",
        "## Task Summary",
        "",
        md_table(task_summary),
        "",
        "## Promoted Policies",
        "",
        md_table(
            promoted,
            [
                "task",
                "view",
                "model",
                "split",
                "target_kind",
                "tail_q",
                "policy",
                "tail_auc",
                "target_delta",
                "loss_vs_full",
                "subject_win_rate",
                "dropped_rows",
                "dropped_mean_benefit",
            ],
            n=60,
        ),
        "",
        "## Best Policies By Task",
        "",
        md_table(
            best,
            [
                "task",
                "view",
                "model",
                "split",
                "target_kind",
                "tail_q",
                "policy",
                "tail_auc",
                "corr_benefit",
                "target_delta",
                "full_target_delta",
                "loss_vs_full",
                "subject_win_rate",
                "dropped_rows",
                "dropped_mean_benefit",
                "stress_promote",
            ],
            n=30,
        ),
        "",
        "## Selected Test Alignment",
        "",
        md_table(align, n=40),
        "",
        "## Decision",
        "",
    ]
    if promoted.empty:
        lines.extend(
            [
                "- Tail-contrastive labels did not create a deployable JEPA amplitude/drop head.",
                "- Keep the E230 Q3 hand-prune as conditional anatomy, not as a learned tail representation.",
                "- The next JEPA target should move beyond per-row tail classification, for example toward pairwise/cell-level decisive-label representation or block-level world modeling.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one tail-contrastive policy beat full OOF movement under stress.",
                "- Treat promoted rows as materialization candidates only after checking target-side public-free tail anatomy and collinearity with E224/E216.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    out, _, _ = run()
    print("[E234 task best]")
    cols = [
        "task",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "tail_auc",
        "target_delta",
        "loss_vs_full",
        "subject_win_rate",
        "stress_promote",
    ]
    print(out.sort_values(["task", "loss_vs_full"]).groupby("task").head(3)[cols].to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
