#!/usr/bin/env python3
"""E233: target-specific soft support-energy heads.

E232 rejected a single shared S2/Q3/S4 support latent. This experiment asks the
next smaller JEPA-translation question:

Can target-specific support probabilities act as a soft amplitude/energy head,
rather than a hard gate, and preserve or improve the OOF movement? For Q3, does
the learned energy naturally downweight the same test rows that E230 identified
as fragile by public-free support-tail geometry?

No public LB is used, and no submission is created. Passing here is only a
promotion test for a later public-tail materialization audit.
"""

from __future__ import annotations

from pathlib import Path
import sys
import warnings
from typing import Any, Callable

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


RNG = 20260530 + 233
EPS = 1.0e-12

OOF_OUT = OUT / "e233_target_specific_soft_energy_heads_oof.csv"
ALIGN_OUT = OUT / "e233_target_specific_soft_energy_heads_test_alignment.csv"
SELECTED_OUT = OUT / "e233_target_specific_soft_energy_heads_selected.csv"
REPORT_OUT = OUT / "e233_target_specific_soft_energy_heads_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(np.float64)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, p))


def safe_logloss(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip_prob(p), labels=[0, 1]))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if float(np.std(aa)) <= EPS or float(np.std(bb)) <= EPS:
        return 0.0
    return float(np.corrcoef(aa, bb)[0, 1])


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
                        max_iter=70,
                        learning_rate=0.035,
                        max_leaf_nodes=7,
                        min_samples_leaf=18,
                        l2_regularization=0.6,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
    }


def split_defs(groups: np.ndarray) -> dict[str, Any]:
    return {
        "stratified5": StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG),
        "subject5": GroupKFold(n_splits=min(5, len(np.unique(groups)))),
    }


def oof_predict(model: Any, split_name: str, splitter: Any, x: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    pred = np.full(len(y), np.nan, dtype=np.float64)
    iterator = splitter.split(x, y, groups) if split_name == "subject5" else splitter.split(x, y)
    for train_idx, val_idx in iterator:
        yy = y[train_idx]
        if len(np.unique(yy)) < 2:
            pred[val_idx] = float(np.mean(yy))
            continue
        fitted = clone(model)
        fitted.fit(x.iloc[train_idx], yy)
        pred[val_idx] = fitted.predict_proba(x.iloc[val_idx])[:, 1]
    if np.isnan(pred).any():
        raise RuntimeError(f"NaN OOF prediction for {split_name}")
    return clip_prob(pred)


def amplitude_policies(prob: np.ndarray) -> dict[str, np.ndarray]:
    p = clip_prob(prob)
    return {
        "soft_prob": p,
        "soft_prob_pow2": np.square(p),
        "soft_linear_t0p35": np.clip((p - 0.35) / 0.65, 0.0, 1.0),
        "soft_linear_t0p45": np.clip((p - 0.45) / 0.55, 0.0, 1.0),
        "soft_linear_t0p50": np.clip((p - 0.50) / 0.50, 0.0, 1.0),
        "soft_center_x1p5": np.clip(0.5 + 1.5 * (p - 0.5), 0.0, 1.0),
        "soft_center_x2p0": np.clip(0.5 + 2.0 * (p - 0.5), 0.0, 1.0),
    }


def scaled_prob(base: np.ndarray, full: np.ndarray, amp: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base) + np.asarray(amp, dtype=np.float64) * (logit(full) - logit(base))))


def subject_win(df: pd.DataFrame, y: np.ndarray, base: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    vals: list[float] = []
    for _, idx in df.groupby("subject_id").groups.items():
        arr = np.asarray(list(idx), dtype=int)
        vals.append(float(loss_vec(y[arr], pred[arr]).mean() - loss_vec(y[arr], base[arr]).mean()))
    vv = np.asarray(vals, dtype=np.float64)
    return float(vv.mean()), float(np.mean(vv < 0.0))


def eval_amplitude(
    df: pd.DataFrame,
    task: str,
    view: str,
    model_name: str,
    split: str,
    policy: str,
    prob: np.ndarray,
    amp: np.ndarray,
) -> dict[str, Any]:
    y = df["support_label"].to_numpy(dtype=int)
    true_y = df["true_label"].to_numpy(dtype=int)
    base = df["base_prob"].to_numpy(dtype=np.float64)
    full = df["full_prob"].to_numpy(dtype=np.float64)
    benefit = df["benefit"].to_numpy(dtype=np.float64)
    pred = scaled_prob(base, full, amp)
    base_loss = loss_vec(true_y, base)
    full_loss = loss_vec(true_y, full)
    pred_loss = loss_vec(true_y, pred)
    full_delta = float(full_loss.mean() - base_loss.mean())
    delta = float(pred_loss.mean() - base_loss.mean())
    subject_delta, subject_win_rate = subject_win(df, true_y, base, pred)
    moved = np.asarray(amp) > 0.05
    return {
        "task": task,
        "view": view,
        "model": model_name,
        "split": split,
        "policy": policy,
        "support_auc": safe_auc(y, prob),
        "support_logloss": safe_logloss(y, prob),
        "support_brier": float(brier_score_loss(y, clip_prob(prob))),
        "corr_benefit": corr(prob, benefit),
        "target_delta": delta,
        "full_target_delta": full_delta,
        "loss_vs_full": delta - full_delta,
        "overall_delta": delta / len(TARGETS),
        "subject_delta_mean": subject_delta,
        "subject_win_rate": subject_win_rate,
        "mean_amp": float(np.mean(amp)),
        "p10_amp": float(np.quantile(amp, 0.10)),
        "p50_amp": float(np.quantile(amp, 0.50)),
        "p90_amp": float(np.quantile(amp, 0.90)),
        "active_rows_amp_gt_0p05": int(np.sum(moved)),
        "active_support_rate": float(np.mean(y[moved])) if moved.any() else np.nan,
        "soft_beats_full": bool(delta < full_delta - 1.0e-5),
        "soft_keeps_signal": bool(delta <= full_delta + 2.5e-4 and delta < 0.0 and subject_win_rate >= 0.60),
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


def fit_full_prob(model: Any, train_x: pd.DataFrame, y: np.ndarray, sub_x: pd.DataFrame) -> np.ndarray:
    fitted = clone(model)
    fitted.fit(train_x, y)
    return clip_prob(fitted.predict_proba(sub_x)[:, 1])


def test_alignment_rows(
    train_long: pd.DataFrame,
    sub_long: pd.DataFrame,
    feats: dict[str, list[str]],
    selected: pd.DataFrame,
) -> pd.DataFrame:
    prior_sets = q3_prior_sets()
    rows: list[dict[str, Any]] = []
    models = model_defs()
    for rec in selected.itertuples(index=False):
        task = str(rec.task)
        view = str(rec.view)
        model_name = str(rec.model)
        policy = str(rec.policy)
        tr = train_long[train_long["task_name"].eq(task)].reset_index(drop=True)
        te = sub_long[sub_long["task_name"].eq(task)].reset_index(drop=True)
        y = tr["support_label"].to_numpy(dtype=int)
        prob = fit_full_prob(models[model_name], tr[feats[view]], y, te[feats[view]])
        amp = amplitude_policies(prob)[policy]
        low_orders = np.argsort(amp)
        row: dict[str, Any] = {
            "task": task,
            "view": view,
            "model": model_name,
            "policy": policy,
            "sub_mean_prob": float(np.mean(prob)),
            "sub_mean_amp": float(np.mean(amp)),
            "sub_p10_amp": float(np.quantile(amp, 0.10)),
            "sub_p50_amp": float(np.quantile(amp, 0.50)),
            "sub_p90_amp": float(np.quantile(amp, 0.90)),
        }
        if task == "q3_e224":
            for name, prior in prior_sets.items():
                for k in [13, 21, 25, 50]:
                    low = set(low_orders[: min(k, len(low_orders))].tolist())
                    row[f"{name}_low{k}_overlap"] = len(low & prior)
                    row[f"{name}_low{k}_jaccard"] = len(low & prior) / max(len(low | prior), 1)
        rows.append(row)
    return pd.DataFrame(rows)


def prepare_long_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_raw, train_long, sub_long, tasks = e232.build_long_frames()
    target_lookup = {t.name: t.target_idx for t in tasks}
    y = train_raw[TARGETS].to_numpy(dtype=int)
    train_long = train_long.copy()
    train_long["true_label"] = [
        int(y[int(row_idx), target_lookup[str(task)]])
        for row_idx, task in zip(train_long["row_idx"].to_numpy(), train_long["task_name"].to_numpy())
    ]
    feats = e232.feature_sets(train_long)
    feats = {name: [c for c in cols if c != "true_label"] for name, cols in feats.items()}
    return train_long, sub_long, feats


def oracle_rows(train_long: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for task in sorted(train_long["task_name"].unique()):
        df = train_long[train_long["task_name"].eq(task)].reset_index(drop=True)
        support = df["support_label"].to_numpy(dtype=int)
        rows.append(
            eval_amplitude(
                df,
                task=task,
                view="oracle",
                model_name="oracle",
                split="oracle",
                policy="oracle_support",
                prob=support.astype(float),
                amp=support.astype(float),
            )
        )
        rows.append(
            eval_amplitude(
                df,
                task=task,
                view="constant",
                model_name="constant",
                split="constant",
                policy="constant_support_rate",
                prob=np.full(len(df), float(np.mean(support))),
                amp=np.full(len(df), float(np.mean(support))),
            )
        )
        rows.append(
            eval_amplitude(
                df,
                task=task,
                view="full",
                model_name="full",
                split="full",
                policy="full_amp",
                prob=np.ones(len(df)),
                amp=np.ones(len(df)),
            )
        )
    return pd.DataFrame(rows)


def run_oof(train_long: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    models = model_defs()
    for task in sorted(train_long["task_name"].unique()):
        df = train_long[train_long["task_name"].eq(task)].reset_index(drop=True)
        y = df["support_label"].to_numpy(dtype=int)
        groups = df["subject_id"].astype(str).to_numpy()
        for view in ["movement", "latent_no_targetid", "latent_with_targetid"]:
            cols = feats[view]
            for model_name, model in models.items():
                for split_name, splitter in split_defs(groups).items():
                    prob = oof_predict(model, split_name, splitter, df[cols], y, groups)
                    for policy, amp in amplitude_policies(prob).items():
                        rows.append(eval_amplitude(df, task, view, model_name, split_name, policy, prob, amp))
    learned = pd.DataFrame(rows)
    all_rows = pd.concat([oracle_rows(train_long), learned], ignore_index=True)
    all_rows["energy_score"] = (
        -all_rows["target_delta"]
        -np.maximum(all_rows["loss_vs_full"], 0.0) * 2.0
        +np.maximum(all_rows["subject_win_rate"] - 0.60, 0.0) * 0.0008
        -np.maximum(all_rows["mean_amp"] - 0.90, 0.0) * 0.0005
    )
    all_rows["promote_to_tail_audit"] = (
        all_rows["soft_beats_full"].fillna(False).astype(bool)
        & all_rows["soft_keeps_signal"].fillna(False).astype(bool)
        & all_rows["view"].ne("oracle")
        & all_rows["model"].ne("full")
        & all_rows["model"].ne("constant")
    )
    return all_rows.sort_values(["task", "promote_to_tail_audit", "energy_score"], ascending=[True, False, False])


def select_for_alignment(oof_df: pd.DataFrame) -> pd.DataFrame:
    learned = oof_df[
        ~oof_df["view"].isin(["oracle", "constant", "full"])
    ].copy()
    selected = (
        learned.sort_values(["task", "promote_to_tail_audit", "energy_score"], ascending=[True, False, False])
        .groupby("task")
        .head(3)
        .reset_index(drop=True)
    )
    return selected


def write_report(oof_df: pd.DataFrame, selected: pd.DataFrame, align_df: pd.DataFrame) -> None:
    learned = oof_df[~oof_df["view"].isin(["oracle", "constant", "full"])].copy()
    best_by_task = learned.sort_values(["task", "energy_score"], ascending=[True, False]).groupby("task").head(5)
    promote = learned[learned["promote_to_tail_audit"].fillna(False).astype(bool)]
    full_rows = oof_df[oof_df["policy"].eq("full_amp")][
        ["task", "target_delta", "subject_win_rate"]
    ].rename(columns={"target_delta": "full_target_delta", "subject_win_rate": "full_subject_win_rate"})
    oracle = oof_df[oof_df["policy"].eq("oracle_support")][
        ["task", "target_delta", "subject_win_rate"]
    ].rename(columns={"target_delta": "oracle_target_delta", "subject_win_rate": "oracle_subject_win_rate"})
    task_summary = (
        best_by_task.groupby("task", as_index=False)
        .agg(
            best_learned_delta=("target_delta", "min"),
            best_loss_vs_full=("loss_vs_full", "min"),
            best_subject_win=("subject_win_rate", "max"),
            best_support_auc=("support_auc", "max"),
            promote_count=("promote_to_tail_audit", "sum"),
        )
        .merge(full_rows, on="task", how="left")
        .merge(oracle, on="task", how="left")
    )
    q3_align = align_df[align_df["task"].eq("q3_e224")].copy()
    q3_best_overlap = (
        int(q3_align.filter(like="e230_q3_risk_top21_low25_overlap").max().max())
        if not q3_align.empty and not q3_align.filter(like="e230_q3_risk_top21_low25_overlap").empty
        else -1
    )
    lines = [
        "# E233 Target-Specific Soft Energy Heads",
        "",
        "## Question",
        "",
        "Can target-specific support probabilities be used as soft JEPA amplitude/energy heads after E232 rejected one shared support gate?",
        "",
        "## Observed Read",
        "",
        f"- Learned policies promoted to tail audit: `{len(promote)}`.",
        f"- Best Q3 overlap with E230 risk-top21 inside learned low-amp top25 rows: `{q3_best_overlap}` rows.",
        "",
        "Interpretation rule: a healthy soft head should beat the full target movement in OOF, keep subject stability, and for Q3 should downweight E230's fragile rows without being hand-coded from E230.",
        "",
        "## Task Summary",
        "",
        md_table(task_summary, n=20),
        "",
        "## Best Learned Soft Policies",
        "",
        md_table(
            best_by_task,
            [
                "task",
                "view",
                "model",
                "split",
                "policy",
                "support_auc",
                "corr_benefit",
                "target_delta",
                "full_target_delta",
                "loss_vs_full",
                "subject_win_rate",
                "mean_amp",
                "promote_to_tail_audit",
            ],
            n=30,
        ),
        "",
        "## Selected Test Alignment Probes",
        "",
        md_table(align_df, n=20),
        "",
        "## Decision",
        "",
    ]
    if promote.empty:
        lines.append("- No learned soft support-energy policy beat the full movement while preserving signal and subject stability.")
        lines.append("- This blocks the cheap target-specific support-head rescue. The next JEPA step should change the target representation/loss, not only soften the existing support classifiers.")
    else:
        lines.append("- Some learned soft policies deserve a later public-tail materialization audit, but E233 itself creates no submission.")
        lines.append("- Promotion is conditional on Q3 alignment with E230 risk cells and target-specific tail anatomy, not just OOF delta.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_long, sub_long, feats = prepare_long_frames()
    oof_df = run_oof(train_long, feats)
    selected = select_for_alignment(oof_df)
    align_df = test_alignment_rows(train_long, sub_long, feats, selected)
    oof_df.to_csv(OOF_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    align_df.to_csv(ALIGN_OUT, index=False)
    write_report(oof_df, selected, align_df)

    print("[E233 task best]")
    cols = ["task", "view", "model", "split", "policy", "target_delta", "loss_vs_full", "subject_win_rate", "promote_to_tail_audit"]
    print(selected[cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
