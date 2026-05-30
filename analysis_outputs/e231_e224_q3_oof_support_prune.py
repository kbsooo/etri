#!/usr/bin/env python3
"""E231: OOF-learned Q3 support prune for the live E224 JEPA sensor.

E230 showed that hand-pruning a small number of fragile E224 Q3 cells can
improve public-free support-tail geometry. The missing condition is whether
that prune is learnable from train/OOF structure instead of being only an
intervention on the submission tensor.

This experiment trains small OOF support models for the E224-like Q3 movement
and asks whether their low-support rows can prune E224's Q3 tail while keeping
the E224 S4 body intact. Passing here still does not use public LB; it is a
promotion test from "conditional hand-prune" toward "learned translator."
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any, Iterable
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", message="'penalty' was deprecated.*", category=FutureWarning)
warnings.filterwarnings("ignore", message="Inconsistent values: penalty=l1.*", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e209_feature_neighbor_jepa_materialization_stress as e209  # noqa: E402
import e210_jepa_target_dependency_gate as e210  # noqa: E402
import e211_target_specific_jepa_gate as e211  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402


Q3 = TARGETS.index("Q3")
S4 = TARGETS.index("S4")
COMBO = "q3_center_c010_s4_rank"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

RNG = 20260530 + 231
EPS = 1.0e-12

MODEL_OUT = OUT / "e231_e224_q3_oof_support_prune_models.csv"
GATE_OUT = OUT / "e231_e224_q3_oof_support_prune_gate_scan.csv"
SUMMARY_OUT = OUT / "e231_e224_q3_oof_support_prune_summary.csv"
TARGET_OUT = OUT / "e231_e224_q3_oof_support_prune_targets.csv"
SELECTED_OUT = OUT / "e231_e224_q3_oof_support_prune_selected.csv"
REPORT_OUT = OUT / "e231_e224_q3_oof_support_prune_report.md"


@dataclass(frozen=True)
class SplitSpec:
    name: str
    splitter: Any
    use_groups: bool = False


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


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


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


def make_e224_like_tensors() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    train_raw, sub_raw, train_feat, sub_feat = e209.read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    groups = train_raw["subject_id"].astype(str).to_numpy()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    if not sub_feat[e209.SUB_KEY].astype(str).equals(sample[KEYS].astype(str)):
        raise RuntimeError("submission feature order differs from sample order")
    stage2_oof = clip_prob(np.load(OUT / STAGE2_OOF))
    stage2_sub = load_prob(STAGE2_FILE, sample)
    ops = e209.combo_defs()[COMBO]
    ungated_oof = e209.apply_ops_oof(train_feat, stage2_oof, ops)
    ungated_sub = e209.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
    dep_oof = e210.oof_dependency(stage2_oof, y, groups)
    dep_sub = e210.fit_predict_dependency(stage2_oof, y, stage2_sub)
    e224_like_oof = e211.apply_policy(stage2_oof, ungated_oof, dep_oof, 0.625, "closer", 1.0)
    e224_like_sub = e211.apply_policy(stage2_sub, ungated_sub, dep_sub, 0.625, "closer", 1.0)
    return train_raw, sub_raw, train_feat, sub_feat, stage2_oof, e224_like_oof, stage2_sub, e224_like_sub, sample


def feature_matrix(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base_oof: np.ndarray,
    e224_oof: np.ndarray,
    base_sub: np.ndarray,
    e224_sub: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_x = train_feat[[c for c in train_feat.columns if c.startswith("e208_")]].copy()
    sub_x = sub_feat[[c for c in sub_feat.columns if c.startswith("e208_")]].copy()
    train_x = pd.concat([train_x, add_row_features(train_feat)], axis=1)
    sub_x = pd.concat([sub_x, add_row_features(sub_feat)], axis=1)

    for target, j in [("q3", Q3), ("s4", S4)]:
        for name, arr in [(f"base_{target}", base_oof[:, j]), (f"e224_{target}", e224_oof[:, j])]:
            train_x[name] = arr
        for name, arr in [(f"base_{target}", base_sub[:, j]), (f"e224_{target}", e224_sub[:, j])]:
            sub_x[name] = arr

    for x, base, full in [(train_x, base_oof, e224_oof), (sub_x, base_sub, e224_sub)]:
        q3_step = logit(full[:, Q3]) - logit(base[:, Q3])
        s4_step = logit(full[:, S4]) - logit(base[:, S4])
        x["q3_logit_step"] = q3_step
        x["abs_q3_logit_step"] = np.abs(q3_step)
        x["q3_moves_up"] = (q3_step > 0).astype(float)
        x["q3_base_margin"] = np.abs(base[:, Q3] - 0.5)
        x["q3_e224_margin"] = np.abs(full[:, Q3] - 0.5)
        x["q3_prob_gap"] = full[:, Q3] - base[:, Q3]
        x["abs_q3_prob_gap"] = np.abs(x["q3_prob_gap"].to_numpy(dtype=np.float64))
        x["s4_logit_step"] = s4_step
        x["abs_s4_logit_step"] = np.abs(s4_step)
        x["q3_s4_step_product"] = q3_step * s4_step
        x["q3_s4_step_abs_ratio"] = np.abs(q3_step) / (np.abs(s4_step) + 1.0e-6)

    subjects = pd.concat([train_feat["subject_id"], sub_feat["subject_id"]], ignore_index=True)
    dummies = pd.get_dummies(subjects, prefix="subject", dtype=float)
    train_d = dummies.iloc[: len(train_feat)].reset_index(drop=True)
    sub_d = dummies.iloc[len(train_feat) :].reset_index(drop=True)
    train_x = pd.concat([train_x.reset_index(drop=True), train_d], axis=1)
    sub_x = pd.concat([sub_x.reset_index(drop=True), sub_d], axis=1)
    features = list(train_x.columns)
    return train_x[features], sub_x[features], features


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
        "lr_l1_c0p04": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.04,
                        solver="liblinear",
                        penalty="l1",
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
        "gb_shallow": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                (
                    "clf",
                    GradientBoostingClassifier(
                        n_estimators=65,
                        learning_rate=0.035,
                        max_depth=2,
                        subsample=0.75,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
    }


def split_defs() -> list[SplitSpec]:
    return [
        SplitSpec("stratified5", StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG)),
        SplitSpec("rowcontig5", KFold(n_splits=5, shuffle=False)),
        SplitSpec("subject5", GroupKFold(n_splits=5), use_groups=True),
        SplitSpec("subject_loo", LeaveOneGroupOut(), use_groups=True),
    ]


def iter_splits(spec: SplitSpec, x: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> Iterable[tuple[np.ndarray, np.ndarray]]:
    if spec.use_groups:
        return spec.splitter.split(x, y, groups)
    return spec.splitter.split(x, y)


def oof_predict(model: Any, spec: SplitSpec, x: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    prob = np.full(len(y), np.nan, dtype=np.float64)
    for train_idx, val_idx in iter_splits(spec, x, y, groups):
        yy = y[train_idx]
        if len(np.unique(yy)) < 2:
            prob[val_idx] = float(yy.mean())
            continue
        fitted = clone(model)
        fitted.fit(x.iloc[train_idx], yy)
        prob[val_idx] = fitted.predict_proba(x.iloc[val_idx])[:, 1]
    if np.isnan(prob).any():
        raise RuntimeError(f"NaN OOF probabilities for {spec.name}")
    return clip_prob(prob)


def subject_win_rate(train_raw: pd.DataFrame, y_q3: np.ndarray, base: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    deltas: list[float] = []
    for _, idx in train_raw.groupby("subject_id").groups.items():
        arr = np.array(list(idx), dtype=int)
        deltas.append(float(loss_vec(y_q3[arr], pred[arr]).mean() - loss_vec(y_q3[arr], base[arr]).mean()))
    vals = np.asarray(deltas, dtype=np.float64)
    return float(vals.mean()), float((vals < 0.0).mean())


def gate_masks(prob: np.ndarray, step_abs: np.ndarray) -> dict[str, np.ndarray]:
    masks: dict[str, np.ndarray] = {}
    n = len(prob)
    for k in [1, 3, 5, 8, 13, 21, 25, 34, 55, 80, 111]:
        low = np.argsort(prob)
        mask = np.ones(n, dtype=bool)
        mask[low[: min(k, n)]] = False
        masks[f"drop_prob_low{k}"] = mask
        risk = (1.0 - prob) * step_abs
        risk_order = np.argsort(risk)[::-1]
        mask = np.ones(n, dtype=bool)
        mask[risk_order[: min(k, n)]] = False
        masks[f"drop_risk_top{k}"] = mask
    for thr in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        masks[f"keep_prob_ge_{str(thr).replace('.', 'p')}"] = prob >= thr
    for k in [80, 100, 125, 150, 175, 200]:
        order = np.argsort(prob)[::-1]
        mask = np.zeros(n, dtype=bool)
        mask[order[: min(k, n)]] = True
        masks[f"keep_top{k}"] = mask
    return masks


def scan_oof_gates(
    model_split: str,
    prob: np.ndarray,
    train_raw: pd.DataFrame,
    support: np.ndarray,
    benefit: np.ndarray,
    y_q3: np.ndarray,
    base_q3: np.ndarray,
    full_q3: np.ndarray,
) -> pd.DataFrame:
    full_delta = float(loss_vec(y_q3, full_q3).mean() - loss_vec(y_q3, base_q3).mean())
    step_abs = np.abs(logit(full_q3) - logit(base_q3))
    rows: list[dict[str, Any]] = []
    for gate, keep in gate_masks(prob, step_abs).items():
        pred = base_q3.copy()
        pred[keep] = full_q3[keep]
        q3_delta = float(loss_vec(y_q3, pred).mean() - loss_vec(y_q3, base_q3).mean())
        subject_delta, subject_win = subject_win_rate(train_raw, y_q3, base_q3, pred)
        pruned = ~keep
        rec: dict[str, Any] = {
            "model_split": model_split,
            "gate": gate,
            "kept_rows": int(keep.sum()),
            "pruned_rows": int(pruned.sum()),
            "kept_support_precision": float(support[keep].mean()) if keep.any() else np.nan,
            "pruned_bad_rate": float((1 - support[pruned]).mean()) if pruned.any() else np.nan,
            "pruned_mean_support_prob": float(prob[pruned].mean()) if pruned.any() else np.nan,
            "kept_mean_support_prob": float(prob[keep].mean()) if keep.any() else np.nan,
            "pruned_benefit_sum": float(benefit[pruned].sum()) if pruned.any() else 0.0,
            "kept_benefit_sum": float(benefit[keep].sum()) if keep.any() else 0.0,
            "q3_target_delta": q3_delta,
            "loss_vs_full_q3": q3_delta - full_delta,
            "full_q3_target_delta": full_delta,
            "overall_delta": q3_delta / len(TARGETS),
            "subject_delta_mean": subject_delta,
            "subject_win_rate": subject_win,
        }
        rec["oof_gate_pass"] = bool(
            1 <= rec["pruned_rows"] <= 55
            and rec["loss_vs_full_q3"] <= 0.00045
            and rec["q3_target_delta"] <= -0.00340
            and rec["subject_win_rate"] >= 0.72
            and (pd.isna(rec["pruned_bad_rate"]) or rec["pruned_bad_rate"] >= 0.45)
        )
        rec["oof_score"] = (
            -rec["loss_vs_full_q3"] * 4.0
            -rec["q3_target_delta"] * 0.50
            +max(rec["subject_win_rate"] - 0.70, 0.0) * 0.0005
            +max((rec["pruned_bad_rate"] if not pd.isna(rec["pruned_bad_rate"]) else 0.0) - 0.50, 0.0) * 0.0004
            -max(rec["pruned_rows"] - 34, 0) * 1.0e-6
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def apply_keep_to_e224(e224: np.ndarray, e154: np.ndarray, keep: np.ndarray) -> np.ndarray:
    out = e224.copy()
    active = np.abs(logit(e224[:, Q3]) - logit(e154[:, Q3])) > EPS
    rollback = active & ~keep
    out[rollback, Q3] = e154[rollback, Q3]
    return clip_prob(out)


def add_comparison_metrics(summary: pd.DataFrame, target_df: pd.DataFrame, base_row: pd.Series) -> pd.DataFrame:
    out = e222.add_ranking(summary.copy())
    q3 = target_df[target_df["pair_kind"].eq("graft_vs_e154") & target_df["target"].eq("Q3")][
        ["candidate_id", "top1_over_abs_expected", "adverse_delta", "expected_focus", "support_prob_focus_swing_weighted"]
    ].rename(
        columns={
            "top1_over_abs_expected": "q3_top1_over_abs_expected",
            "adverse_delta": "q3_adverse_delta",
            "expected_focus": "q3_expected_focus",
            "support_prob_focus_swing_weighted": "q3_support_prob_focus_swing_weighted",
        }
    )
    s4 = target_df[target_df["pair_kind"].eq("graft_vs_e154") & target_df["target"].eq("S4")][
        ["candidate_id", "expected_focus", "adverse_delta", "support_prob_focus_swing_weighted"]
    ].rename(
        columns={
            "expected_focus": "s4_expected_focus",
            "adverse_delta": "s4_adverse_delta",
            "support_prob_focus_swing_weighted": "s4_support_prob_focus_swing_weighted",
        }
    )
    out = out.merge(q3, on="candidate_id", how="left").merge(s4, on="candidate_id", how="left")
    graft = out["pair_kind"].eq("graft_vs_e154")
    for col in ["expected_focus", "adverse_delta", "support_prob_focus_swing_weighted", "top1_over_abs_expected"]:
        out[f"{col}_vs_e224"] = out[col] - float(base_row[col])
    out["adverse_reduction_vs_e224"] = float(base_row["adverse_delta"]) - out["adverse_delta"]
    out["expected_loss_vs_e224"] = out["expected_focus"] - float(base_row["expected_focus"])
    out["support_gain_vs_e224"] = out["support_prob_focus_swing_weighted"] - float(
        base_row["support_prob_focus_swing_weighted"]
    )
    out["e231_tail_gate"] = False
    out.loc[graft, "e231_tail_gate"] = (
        (out.loc[graft, "expected_focus"] <= -0.00058)
        & (out.loc[graft, "expected_loss_vs_e224"] <= 0.000060)
        & (out.loc[graft, "adverse_reduction_vs_e224"] >= 0.000100)
        & (out.loc[graft, "support_gain_vs_e224"] >= 0.0018)
        & (out.loc[graft, "q3_adverse_delta"].fillna(9.0) <= 0.00210)
        & (out.loc[graft, "q3_top1_over_abs_expected"].fillna(9.0) <= 0.84)
        & (out.loc[graft, "pruned_cells_sub"] <= 55)
    )
    out["e231_score"] = (
        -out["expected_loss_vs_e224"].fillna(0.0) * 2400.0
        +out["adverse_reduction_vs_e224"].fillna(0.0) * 1300.0
        +out["support_gain_vs_e224"].fillna(0.0) * 0.45
        +out["oof_score"].fillna(0.0) * 500.0
        -np.maximum(out["q3_top1_over_abs_expected"].fillna(9.0) - 0.78, 0.0) * 0.08
        -np.maximum(out["pruned_cells_sub"].fillna(0.0) - 25, 0.0) * 0.0008
    )
    return out


def materialize(sample: pd.DataFrame, pred: np.ndarray, tag: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe_tag = tag.replace("__", "_")[:58]
    file_name = f"submission_e231_{safe_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def write_report(
    model_df: pd.DataFrame,
    gate_df: pd.DataFrame,
    summary: pd.DataFrame,
    target_df: pd.DataFrame,
    selected: pd.DataFrame,
    support_rate: float,
    full_q3_delta: float,
) -> None:
    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].sort_values(
        ["joint_gate_pass", "e231_score"], ascending=[False, False]
    )
    target_view = target_df[target_df["pair_kind"].eq("graft_vs_e154")].sort_values(["candidate_id", "target"])
    lines = [
        "# E231 E224 Q3 OOF Support Prune",
        "",
        "## Question",
        "",
        "Can E230-style E224 Q3 tail pruning be learned from train/OOF support labels?",
        "",
        "## Setup",
        "",
        f"- Train Q3 support-label rate: `{support_rate:.6f}`.",
        f"- Full E224-like Q3 target OOF delta versus stage2: `{full_q3_delta:.9f}`.",
        "",
        "## Support Model Stress",
        "",
        md_table(
            model_df.sort_values(["split", "auc"], ascending=[True, False]),
            ["model", "split", "auc", "logloss", "brier", "corr_benefit", "mean_prob"],
            n=40,
        ),
        "",
        "## Best OOF Prune Gates",
        "",
        md_table(
            gate_df.sort_values(["oof_gate_pass", "oof_score"], ascending=[False, False]),
            [
                "model_split",
                "gate",
                "kept_rows",
                "pruned_rows",
                "kept_support_precision",
                "pruned_bad_rate",
                "q3_target_delta",
                "loss_vs_full_q3",
                "subject_win_rate",
                "oof_gate_pass",
            ],
            n=40,
        ),
        "",
        "## Submission-Side Tail Stress",
        "",
        md_table(
            graft,
            [
                "candidate_id",
                "model_split",
                "gate",
                "pruned_cells_sub",
                "expected_focus",
                "expected_loss_vs_e224",
                "adverse_reduction_vs_e224",
                "support_gain_vs_e224",
                "q3_top1_over_abs_expected",
                "q3_adverse_delta",
                "oof_gate_pass",
                "e231_tail_gate",
                "joint_gate_pass",
                "submission_file",
            ],
            n=50,
        ),
        "",
        "## Target Breakdown",
        "",
        md_table(
            target_view,
            ["candidate_id", "target", "moved_cells", "expected_focus", "adverse_delta", "support_prob_focus_swing_weighted", "top1_over_abs_expected"],
            n=50,
        ),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No E231 learned Q3 support prune passed both OOF preservation and submission-side tail stress.")
        lines.append("- E230 remains a conditional hand-prune after E224 feedback, not a first-class learned translator.")
    else:
        files = ", ".join(f"`{x}`" for x in selected["submission_file"].dropna().astype(str).tolist())
        lines.append(f"- E231 found learned Q3 support-prune candidates: {files}.")
        lines.append("- These still answer a narrower question than E224; submit only after deciding to test learned Q3-tail repair.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, _sub_raw, train_feat, sub_feat, stage2_oof, e224_like_oof, stage2_sub, e224_like_sub, sample = make_e224_like_tensors()
    y_q3 = train_raw["Q3"].to_numpy(dtype=int)
    base_q3 = stage2_oof[:, Q3]
    full_q3 = e224_like_oof[:, Q3]
    base_loss = loss_vec(y_q3, base_q3)
    full_loss = loss_vec(y_q3, full_q3)
    loss_delta = full_loss - base_loss
    support = (loss_delta < 0.0).astype(int)
    benefit = -loss_delta
    support_rate = float(support.mean())
    full_q3_delta = float(full_loss.mean() - base_loss.mean())

    train_x, sub_x, features = feature_matrix(train_feat, sub_feat, stage2_oof, e224_like_oof, stage2_sub, e224_like_sub)
    groups = train_raw["subject_id"].astype(str).to_numpy()
    models = model_defs()
    splits = split_defs()

    model_rows: list[dict[str, Any]] = []
    gate_parts: list[pd.DataFrame] = []
    fitted_sub_probs: dict[str, np.ndarray] = {}
    for model_name, model in models.items():
        for spec in splits:
            model_split = f"{model_name}__{spec.name}"
            prob = oof_predict(model, spec, train_x[features], support, groups)
            model_rows.append(
                {
                    "model": model_name,
                    "split": spec.name,
                    "model_split": model_split,
                    "auc": safe_auc(support, prob),
                    "logloss": safe_logloss(support, prob),
                    "brier": float(brier_score_loss(support, prob)),
                    "corr_benefit": corr(prob, benefit),
                    "mean_prob": float(prob.mean()),
                    "n": int(len(prob)),
                }
            )
            gate_parts.append(scan_oof_gates(model_split, prob, train_raw, support, benefit, y_q3, base_q3, full_q3))
            fitted = clone(model)
            fitted.fit(train_x[features], support)
            fitted_sub_probs[model_split] = fitted.predict_proba(sub_x[features])[:, 1]

    model_df = pd.DataFrame(model_rows)
    gate_df = pd.concat(gate_parts, ignore_index=True)

    e95 = load_prob(E95_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e224 = load_prob(E224_FILE, sample)
    priors = e162.prior_arrays(sample)
    base_spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=E224_FILE,
        anchor_file=E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current JEPA-first E224 candidate.",
    )
    base_rec, _base_tgt, _base_top = e222.pair_audit(
        base_spec, "graft_vs_e154", e224, e154, E154_FILE, priors, sample
    )
    base_row = pd.Series(base_rec)

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    pred_cache: dict[str, np.ndarray] = {}
    sub_step_abs = np.abs(logit(e224_like_sub[:, Q3]) - logit(stage2_sub[:, Q3]))
    gate_lookup = gate_df.set_index(["model_split", "gate"])
    for model_split, prob_sub in fitted_sub_probs.items():
        for gate, keep in gate_masks(prob_sub, sub_step_abs).items():
            if (model_split, gate) not in gate_lookup.index:
                continue
            gate_row = gate_lookup.loc[(model_split, gate)]
            if isinstance(gate_row, pd.DataFrame):
                gate_row = gate_row.iloc[0]
            pred = apply_keep_to_e224(e224, e154, keep)
            candidate_id = f"{model_split}__{gate}"
            pred_cache[candidate_id] = pred
            meta = {
                "model_split": model_split,
                "gate": gate,
                "pruned_cells_sub": int((np.abs(logit(e224[:, Q3]) - logit(e154[:, Q3])) > EPS).sum() - keep.sum()),
                "oof_gate_pass": bool(gate_row["oof_gate_pass"]),
                "q3_target_delta": float(gate_row["q3_target_delta"]),
                "loss_vs_full_q3": float(gate_row["loss_vs_full_q3"]),
                "subject_win_rate": float(gate_row["subject_win_rate"]),
                "pruned_bad_rate": float(gate_row["pruned_bad_rate"]) if not pd.isna(gate_row["pruned_bad_rate"]) else np.nan,
                "oof_score": float(gate_row["oof_score"]),
            }
            spec = e222.Candidate(
                candidate_id=candidate_id,
                file_name=candidate_id,
                anchor_file=E154_FILE,
                family="e231_e224_q3_oof_support_prune",
                status="generated",
                note="OOF-learned Q3 support prune of E224; S4 body unchanged.",
            )
            for pair_kind, base_name, base in [("graft_vs_e154", E154_FILE, e154), ("actual_vs_e95", E95_FILE, e95)]:
                rec, tgt, _top = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
                rec.update(meta)
                summary_rows.append(rec)
                if not tgt.empty:
                    tgt = tgt.copy()
                    for key, value in meta.items():
                        tgt[key] = value
                    target_parts.append(tgt)

    summary = pd.DataFrame(summary_rows)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    target_df = e222.add_ranking(target_df) if not target_df.empty else target_df
    summary = add_comparison_metrics(summary, target_df, base_row) if not summary.empty else summary
    summary["joint_gate_pass"] = summary["oof_gate_pass"].astype(bool) & summary["e231_tail_gate"].fillna(False).astype(bool)
    selected = summary[
        summary["pair_kind"].eq("graft_vs_e154") & summary["joint_gate_pass"]
    ].sort_values(["e231_score", "expected_focus"], ascending=[False, True]).head(3).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        files.append(materialize(sample, pred_cache[str(row.candidate_id)], str(row.candidate_id)))
    if not selected.empty:
        selected["submission_file"] = files
        summary = summary.merge(selected[["candidate_id", "submission_file"]], on="candidate_id", how="left")
    else:
        summary["submission_file"] = ""
        selected["submission_file"] = ""

    model_df.to_csv(MODEL_OUT, index=False)
    gate_df.to_csv(GATE_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(model_df, gate_df, summary, target_df, selected, support_rate, full_q3_delta)

    cols = [
        "candidate_id",
        "model_split",
        "gate",
        "pruned_cells_sub",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "oof_gate_pass",
        "e231_tail_gate",
        "joint_gate_pass",
        "submission_file",
    ]
    print("[E231 selected]")
    print(selected[cols].round(9).to_string(index=False) if not selected.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
