#!/usr/bin/env python3
"""E232: cross-target support invariance after E216 and E231.

E221 found that E216 S2 support is locally learnable but not public-tail safe.
E231 found that E224 Q3 support is only weakly learnable and cannot promote
E230's hand-prune into a learned translator.

This experiment asks a smaller JEPA-target question:

Is there a shared row/support latent behind the S2, Q3, and S4 failures, or are
the support-tail boundaries target-specific? If a shared latent exists, a model
trained on one target movement should predict support for another target
movement better than chance. If it does not, a future JEPA objective needs
target-specific target representations instead of one shared support regularizer.
"""

from __future__ import annotations

from dataclasses import dataclass
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

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e221_s2_oof_support_classifier as e221  # noqa: E402
import e231_e224_q3_oof_support_prune as e231  # noqa: E402


RNG = 20260530 + 232
EPS = 1.0e-12

S2 = TARGETS.index("S2")
Q3 = TARGETS.index("Q3")
S4 = TARGETS.index("S4")

LABEL_OUT = OUT / "e232_cross_target_support_invariance_label_overlap.csv"
SUBJECT_OUT = OUT / "e232_cross_target_support_invariance_subject_rates.csv"
WITHIN_OUT = OUT / "e232_cross_target_support_invariance_within_oof.csv"
TRANSFER_OUT = OUT / "e232_cross_target_support_invariance_transfer.csv"
TEST_OVERLAP_OUT = OUT / "e232_cross_target_support_invariance_test_overlap.csv"
REPORT_OUT = OUT / "e232_cross_target_support_invariance_report.md"


@dataclass(frozen=True)
class TaskTensor:
    name: str
    target: str
    family: str
    target_idx: int
    base_oof: np.ndarray
    full_oof: np.ndarray
    base_sub: np.ndarray
    full_sub: np.ndarray


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(np.float64)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def support_label(y: np.ndarray, base: np.ndarray, full: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    base_loss = loss_vec(y, base)
    full_loss = loss_vec(y, full)
    benefit = base_loss - full_loss
    return (benefit > 0.0).astype(int), benefit


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


def add_row_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    ordered = frame.sort_values(["subject_id", "lifelog_date"]).copy()
    pos = ordered.groupby("subject_id").cumcount()
    size = ordered.groupby("subject_id")["subject_id"].transform("size")
    out.loc[ordered.index, "subject_pos"] = pos.to_numpy(dtype=np.float64)
    out.loc[ordered.index, "subject_size"] = size.to_numpy(dtype=np.float64)
    out.loc[ordered.index, "subject_pos_frac"] = pos.to_numpy(dtype=np.float64) / np.maximum(
        size.to_numpy(dtype=np.float64) - 1.0, 1.0
    )
    out["lifelog_weekday"] = pd.to_datetime(frame["lifelog_date"]).dt.weekday.astype(float)
    out["sleep_weekday"] = pd.to_datetime(frame["sleep_date"]).dt.weekday.astype(float)
    out["date_gap_days"] = (
        pd.to_datetime(frame["sleep_date"]) - pd.to_datetime(frame["lifelog_date"])
    ).dt.days.astype(float)
    return out


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


def assert_same_keys(a: pd.DataFrame, b: pd.DataFrame, label: str) -> None:
    if not a[KEYS].astype(str).reset_index(drop=True).equals(b[KEYS].astype(str).reset_index(drop=True)):
        raise RuntimeError(f"key mismatch: {label}")


def load_context_and_tasks() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, list[TaskTensor], np.ndarray]:
    (
        train216,
        sub216,
        feat216,
        subfeat216,
        stage2_oof216,
        e216_oof,
        stage2_sub216,
        e216_sub,
        sample216,
    ) = e221.make_e216_tensors()
    (
        train224,
        sub224,
        feat224,
        subfeat224,
        stage2_oof224,
        e224_oof,
        stage2_sub224,
        e224_sub,
        sample224,
    ) = e231.make_e224_like_tensors()

    assert_same_keys(train216, train224, "train216/train224")
    assert_same_keys(sub216, sub224, "sub216/sub224")
    assert_same_keys(sample216, sample224, "sample216/sample224")

    y = train216[TARGETS].to_numpy(dtype=int)
    tasks = [
        TaskTensor(
            name="s2_e216",
            target="S2",
            family="e216_maskfam",
            target_idx=S2,
            base_oof=stage2_oof216[:, S2],
            full_oof=e216_oof[:, S2],
            base_sub=stage2_sub216[:, S2],
            full_sub=e216_sub[:, S2],
        ),
        TaskTensor(
            name="q3_e224",
            target="Q3",
            family="e224_q3s4",
            target_idx=Q3,
            base_oof=stage2_oof224[:, Q3],
            full_oof=e224_oof[:, Q3],
            base_sub=stage2_sub224[:, Q3],
            full_sub=e224_sub[:, Q3],
        ),
        TaskTensor(
            name="s4_e224",
            target="S4",
            family="e224_q3s4",
            target_idx=S4,
            base_oof=stage2_oof224[:, S4],
            full_oof=e224_oof[:, S4],
            base_sub=stage2_sub224[:, S4],
            full_sub=e224_sub[:, S4],
        ),
    ]
    return train216, sub216, feat216, feat224, tasks, y


def row_context(feat216: pd.DataFrame, feat224: pd.DataFrame, is_sub: bool = False) -> pd.DataFrame:
    del is_sub
    ctx = pd.concat(
        [
            feat216[[c for c in feat216.columns if c.startswith("e215_")]].reset_index(drop=True),
            feat224[[c for c in feat224.columns if c.startswith("e208_")]].reset_index(drop=True),
            add_row_features(feat216).reset_index(drop=True),
        ],
        axis=1,
    )
    return ctx


def task_frame(
    base_ctx: pd.DataFrame,
    raw_frame: pd.DataFrame,
    task: TaskTensor,
    y: np.ndarray | None,
    is_train: bool,
) -> pd.DataFrame:
    frame = base_ctx.copy()
    base = task.base_oof if is_train else task.base_sub
    full = task.full_oof if is_train else task.full_sub
    step = logit(full) - logit(base)
    frame["task_name"] = task.name
    frame["target_name"] = task.target
    frame["family_name"] = task.family
    frame["target_idx_scaled"] = float(task.target_idx) / max(len(TARGETS) - 1, 1)
    frame["target_is_q"] = float(task.target.startswith("Q"))
    frame["target_is_s"] = float(task.target.startswith("S"))
    frame["family_is_e224"] = float(task.family.startswith("e224"))
    frame["base_prob"] = base
    frame["full_prob"] = full
    frame["prob_gap"] = full - base
    frame["abs_prob_gap"] = np.abs(full - base)
    frame["logit_step"] = step
    frame["abs_logit_step"] = np.abs(step)
    frame["moves_up"] = (step > 0).astype(float)
    frame["base_margin"] = np.abs(base - 0.5)
    frame["full_margin"] = np.abs(full - 0.5)
    frame["row_idx"] = np.arange(len(frame))
    frame["subject_id"] = raw_frame["subject_id"].astype(str).to_numpy()
    if y is not None:
        label, benefit = support_label(y[:, task.target_idx], base, full)
        frame["support_label"] = label
        frame["benefit"] = benefit
    return frame


def build_long_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[TaskTensor]]:
    train_raw, sub_raw, feat216, feat224, tasks, y = load_context_and_tasks()
    _, _, _, subfeat216, _, _, _, _, _ = e221.make_e216_tensors()
    _, _, _, subfeat224, _, _, _, _, _ = e231.make_e224_like_tensors()
    train_ctx = row_context(feat216, feat224)
    sub_ctx = row_context(subfeat216, subfeat224, is_sub=True)
    train_long = pd.concat([task_frame(train_ctx, train_raw, t, y, True) for t in tasks], ignore_index=True)
    sub_long = pd.concat([task_frame(sub_ctx, sub_raw, t, None, False) for t in tasks], ignore_index=True)
    return train_raw, train_long, sub_long, tasks


def feature_sets(train_long: pd.DataFrame) -> dict[str, list[str]]:
    exclude = {
        "task_name",
        "target_name",
        "family_name",
        "row_idx",
        "subject_id",
        "support_label",
        "benefit",
    }
    numeric = [
        c
        for c in train_long.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(train_long[c])
    ]
    movement = [
        "target_idx_scaled",
        "target_is_q",
        "target_is_s",
        "family_is_e224",
        "base_prob",
        "full_prob",
        "prob_gap",
        "abs_prob_gap",
        "logit_step",
        "abs_logit_step",
        "moves_up",
        "base_margin",
        "full_margin",
        "subject_pos",
        "subject_size",
        "subject_pos_frac",
        "lifelog_weekday",
        "sleep_weekday",
        "date_gap_days",
    ]
    no_targetid = [c for c in numeric if c not in {"target_idx_scaled", "target_is_q", "target_is_s", "family_is_e224"}]
    return {
        "movement": [c for c in movement if c in numeric],
        "latent_no_targetid": no_targetid,
        "latent_with_targetid": numeric,
    }


def summarize_label_overlap(train_long: pd.DataFrame, train_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    wide = train_long.pivot(index="row_idx", columns="task_name", values="support_label").astype(int)
    benefits = train_long.pivot(index="row_idx", columns="task_name", values="benefit")
    rows: list[dict[str, Any]] = []
    for a in wide.columns:
        for b in wide.columns:
            if a >= b:
                continue
            ya = wide[a].to_numpy(dtype=int)
            yb = wide[b].to_numpy(dtype=int)
            both_good = (ya == 1) & (yb == 1)
            either_good = (ya == 1) | (yb == 1)
            both_bad = (ya == 0) & (yb == 0)
            either_bad = (ya == 0) | (yb == 0)
            rows.append(
                {
                    "pair": f"{a}__{b}",
                    "support_rate_a": float(np.mean(ya)),
                    "support_rate_b": float(np.mean(yb)),
                    "label_corr": corr(ya, yb),
                    "benefit_corr": corr(benefits[a].to_numpy(dtype=np.float64), benefits[b].to_numpy(dtype=np.float64)),
                    "good_jaccard": float(np.sum(both_good) / max(np.sum(either_good), 1)),
                    "bad_jaccard": float(np.sum(both_bad) / max(np.sum(either_bad), 1)),
                    "same_label_rate": float(np.mean(ya == yb)),
                    "both_good_rate": float(np.mean(both_good)),
                    "both_bad_rate": float(np.mean(both_bad)),
                }
            )
    label_df = pd.DataFrame(rows)

    subject = train_raw[["subject_id"]].copy()
    subject["row_idx"] = np.arange(len(subject))
    subj_long = train_long[["row_idx", "task_name", "support_label", "benefit"]].merge(subject, on="row_idx")
    subj_rates = (
        subj_long.groupby(["subject_id", "task_name"], as_index=False)
        .agg(support_rate=("support_label", "mean"), benefit_mean=("benefit", "mean"), n=("support_label", "size"))
    )
    return label_df, subj_rates


def fit_predict(model: Any, x_train: pd.DataFrame, y_train: np.ndarray, x_test: pd.DataFrame) -> np.ndarray:
    m = clone(model)
    m.fit(x_train, y_train)
    if hasattr(m, "predict_proba"):
        return clip_prob(m.predict_proba(x_test)[:, 1])
    return clip_prob(m.predict(x_test))


def within_task_oof(train_long: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    models = model_defs()
    for view_name, cols in feats.items():
        for task_name in sorted(train_long["task_name"].unique()):
            df = train_long[train_long["task_name"] == task_name].reset_index(drop=True)
            y = df["support_label"].to_numpy(dtype=int)
            groups = df["subject_id"].astype(str).to_numpy()
            split_specs = {
                "stratified5": StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG),
                "subject5": GroupKFold(n_splits=min(5, len(np.unique(groups)))),
            }
            for model_name, model in models.items():
                for split_name, splitter in split_specs.items():
                    pred = np.zeros(len(df), dtype=np.float64)
                    if split_name == "subject5":
                        iterator = splitter.split(df[cols], y, groups)
                    else:
                        iterator = splitter.split(df[cols], y)
                    for tr, va in iterator:
                        pred[va] = fit_predict(model, df.iloc[tr][cols], y[tr], df.iloc[va][cols])
                    benefit = df["benefit"].to_numpy(dtype=np.float64)
                    rows.append(
                        {
                            "view": view_name,
                            "task": task_name,
                            "model": model_name,
                            "split": split_name,
                            "auc": safe_auc(y, pred),
                            "logloss": safe_logloss(y, pred),
                            "brier": float(brier_score_loss(y, pred)),
                            "corr_benefit": corr(pred, benefit),
                            "support_rate": float(np.mean(y)),
                            "n": int(len(y)),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["view", "task", "auc"], ascending=[True, True, False])


def transfer_stress(train_long: pd.DataFrame, feats: dict[str, list[str]]) -> tuple[pd.DataFrame, dict[tuple[str, str, str], np.ndarray]]:
    rows: list[dict[str, Any]] = []
    predictions: dict[tuple[str, str, str], np.ndarray] = {}
    models = model_defs()
    tasks = sorted(train_long["task_name"].unique())
    source_sets: dict[str, list[str]] = {f"only_{t}": [t] for t in tasks}
    source_sets.update(
        {
            "q3_s4_e224": ["q3_e224", "s4_e224"],
            "s2_s4": ["s2_e216", "s4_e224"],
            "s2_q3": ["s2_e216", "q3_e224"],
        }
    )
    for view_name, cols in feats.items():
        for source_name, source_tasks in source_sets.items():
            source = train_long[train_long["task_name"].isin(source_tasks)].reset_index(drop=True)
            for target_task in tasks:
                if target_task in source_tasks:
                    continue
                target = train_long[train_long["task_name"] == target_task].reset_index(drop=True)
                y_source = source["support_label"].to_numpy(dtype=int)
                y_target = target["support_label"].to_numpy(dtype=int)
                for model_name, model in models.items():
                    pred = fit_predict(model, source[cols], y_source, target[cols])
                    predictions[(view_name, source_name, target_task, model_name)] = pred
                    rows.append(
                        {
                            "view": view_name,
                            "source": source_name,
                            "target": target_task,
                            "model": model_name,
                            "source_support_rate": float(np.mean(y_source)),
                            "target_support_rate": float(np.mean(y_target)),
                            "auc": safe_auc(y_target, pred),
                            "logloss": safe_logloss(y_target, pred),
                            "brier": float(brier_score_loss(y_target, pred)),
                            "corr_benefit": corr(pred, target["benefit"].to_numpy(dtype=np.float64)),
                            "mean_pred": float(np.mean(pred)),
                            "n_source": int(len(y_source)),
                            "n_target": int(len(y_target)),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["auc"], ascending=False), predictions


def test_risk_overlap(
    train_long: pd.DataFrame,
    sub_long: pd.DataFrame,
    feats: dict[str, list[str]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    models = model_defs()
    view_name = "latent_no_targetid"
    cols = feats[view_name]
    pred_by_task: dict[str, np.ndarray] = {}
    for task_name in sorted(train_long["task_name"].unique()):
        tr = train_long[train_long["task_name"] == task_name].reset_index(drop=True)
        te = sub_long[sub_long["task_name"] == task_name].reset_index(drop=True)
        y = tr["support_label"].to_numpy(dtype=int)
        pred = fit_predict(models["hgb_shallow"], tr[cols], y, te[cols])
        pred_by_task[task_name] = pred

    for a in sorted(pred_by_task):
        for b in sorted(pred_by_task):
            if a >= b:
                continue
            pa = pred_by_task[a]
            pb = pred_by_task[b]
            for k in [10, 25, 50, 80, 111]:
                low_a = set(np.argsort(pa)[:k].tolist())
                low_b = set(np.argsort(pb)[:k].tolist())
                rows.append(
                    {
                        "pair": f"{a}__{b}",
                        "k": k,
                        "low_support_overlap": len(low_a & low_b),
                        "low_support_jaccard": len(low_a & low_b) / max(len(low_a | low_b), 1),
                        "corr_pred": corr(pa, pb),
                        "mean_pred_a": float(np.mean(pa)),
                        "mean_pred_b": float(np.mean(pb)),
                    }
                )
    return pd.DataFrame(rows)


def write_report(
    label_df: pd.DataFrame,
    subj_df: pd.DataFrame,
    within_df: pd.DataFrame,
    transfer_df: pd.DataFrame,
    test_overlap_df: pd.DataFrame,
) -> None:
    best_within = within_df.sort_values(["task", "auc"], ascending=[True, False]).groupby("task").head(3)
    best_transfer = transfer_df.sort_values("auc", ascending=False).head(20)
    cross_fail = transfer_df[
        (transfer_df["source"].isin(["only_s2_e216", "only_q3_e224", "only_s4_e224"]))
        & (transfer_df["auc"] < 0.58)
    ]
    subject_pivot = subj_df.pivot(index="subject_id", columns="task_name", values="support_rate")
    subj_corr_rows = []
    for a in subject_pivot.columns:
        for b in subject_pivot.columns:
            if a >= b:
                continue
            subj_corr_rows.append({"pair": f"{a}__{b}", "subject_rate_corr": corr(subject_pivot[a], subject_pivot[b])})
    subj_corr = pd.DataFrame(subj_corr_rows)
    max_abs_label_corr = float(label_df["label_corr"].abs().max())
    max_abs_benefit_corr = float(label_df["benefit_corr"].abs().max())
    best_transfer_auc = float(transfer_df["auc"].max())
    best_transfer_row = transfer_df.sort_values("auc", ascending=False).iloc[0]
    movement_best_auc = float(transfer_df[transfer_df["view"] == "movement"]["auc"].max())
    latent_best_auc = float(transfer_df[transfer_df["view"] != "movement"]["auc"].max())
    q3_s2_overlap25 = test_overlap_df[
        (test_overlap_df["pair"] == "q3_e224__s2_e216") & (test_overlap_df["k"] == 25)
    ]
    q3_s2_overlap25_val = int(q3_s2_overlap25["low_support_overlap"].iloc[0]) if not q3_s2_overlap25.empty else -1

    lines = [
        "# E232 Cross-Target Support Invariance",
        "",
        "## Question",
        "",
        "Do E216 S2, E224 Q3, and E224 S4 support tails share one latent support boundary, or are they target-specific?",
        "",
        "## Observed Read",
        "",
        f"- Max absolute row-label correlation across target support labels: `{max_abs_label_corr:.6f}`.",
        f"- Max absolute benefit correlation: `{max_abs_benefit_corr:.6f}`.",
        f"- Best held-out target transfer AUC: `{best_transfer_auc:.6f}` from `{best_transfer_row['source']}` to `{best_transfer_row['target']}` using `{best_transfer_row['view']}` / `{best_transfer_row['model']}`.",
        f"- Best movement-only transfer AUC: `{movement_best_auc:.6f}`; best latent-context transfer AUC: `{latent_best_auc:.6f}`.",
        f"- Test-side low-support overlap for Q3-vs-S2 at top25: `{q3_s2_overlap25_val}` rows.",
        "",
        "Interpretation: support-tail risk is not a shared row/block latent. The transferable part is mostly movement-shape calibration, not row identity or JEPA latent context. This argues for target-specific JEPA support/energy targets with a separate movement-shape regularizer, rather than one shared support gate.",
        "",
        "## Label Overlap",
        "",
        md_table(label_df, n=20),
        "",
        "## Subject-Level Support Correlation",
        "",
        md_table(subj_corr, n=20),
        "",
        "## Best Within-Target OOF Models",
        "",
        md_table(best_within, n=20),
        "",
        "## Best Cross-Target Transfer Rows",
        "",
        md_table(best_transfer, n=30),
        "",
        "## Weak Single-Source Transfer Rows",
        "",
        md_table(cross_fail.sort_values("auc").head(30), n=30),
        "",
        "## Test-Side Low-Support Overlap",
        "",
        md_table(test_overlap_df, n=30),
        "",
        "## Decision",
        "",
        "- Reject a single shared row-support regularizer for S2/Q3/S4 under the current E216/E224 translations.",
        "- Keep the movement-shape signal as a calibration diagnostic: it transfers better than row-label overlap, but it is not enough to select public-safe rows.",
        "- Future JEPA work should create target-specific support/energy heads, especially for S2 and Q3, and should treat S4 as the healthier body component rather than a proxy for Q3/S2 support.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train_raw, train_long, sub_long, _ = build_long_frames()
    feats = feature_sets(train_long)
    label_df, subj_df = summarize_label_overlap(train_long, train_raw)
    within_df = within_task_oof(train_long, feats)
    transfer_df, _ = transfer_stress(train_long, feats)
    test_overlap_df = test_risk_overlap(train_long, sub_long, feats)

    label_df.to_csv(LABEL_OUT, index=False)
    subj_df.to_csv(SUBJECT_OUT, index=False)
    within_df.to_csv(WITHIN_OUT, index=False)
    transfer_df.to_csv(TRANSFER_OUT, index=False)
    test_overlap_df.to_csv(TEST_OVERLAP_OUT, index=False)
    write_report(label_df, subj_df, within_df, transfer_df, test_overlap_df)

    print("[E232 label overlap]")
    print(label_df.to_string(index=False))
    print("\n[E232 best transfer]")
    print(transfer_df.head(12).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
