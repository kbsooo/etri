#!/usr/bin/env python3
"""E221: trainable OOF gate for the failed E216 S2 JEPA movement.

E216 proved that the masked-family JEPA S2 representation can improve local
OOF loss, but the submitted probability translation was public-adverse. E219
and E220 narrowed the failure to S2 hard-label support/tail risk, and rejected
simple public-prior threshold gates.

This experiment asks the next falsifiable question:

Can the rows where the E216 S2 movement helps be predicted from train-only,
OOF-reproducible JEPA/state features well enough to keep local gain and reduce
submission-side hard-label tail capacity?
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any, Iterable

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


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e216_masked_family_jepa_materialization as e216  # noqa: E402


S2_IDX = TARGETS.index("S2")
N_PUBLIC_CELLS = 250 * len(TARGETS)
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E95_PUBLIC = 0.5762913298
E216_PUBLIC = 0.5772865088
OBS_MISS = E216_PUBLIC - E95_PUBLIC
RNG = 20260530 + 221
EPS = 1.0e-12

MODEL_OUT = OUT / "e221_s2_oof_support_classifier_models.csv"
GATE_OUT = OUT / "e221_s2_oof_support_classifier_gate_scan.csv"
SUB_SCAN_OUT = OUT / "e221_s2_oof_support_classifier_submission_scan.csv"
SELECTED_OUT = OUT / "e221_s2_oof_support_classifier_selected.csv"
REPORT_OUT = OUT / "e221_s2_oof_support_classifier_report.md"


@dataclass(frozen=True)
class SplitSpec:
    name: str
    splitter: Any
    use_groups: bool = False


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(np.float64)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    dy1 = -np.log(p_new) + np.log(p_base)
    dy0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return dy1 / N_PUBLIC_CELLS, dy0 / N_PUBLIC_CELLS


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, p))


def safe_logloss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(np.asarray(p, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)
    labels = [0, 1]
    return float(log_loss(y.astype(int), p, labels=labels))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if float(np.std(aa)) <= EPS or float(np.std(bb)) <= EPS:
        return 0.0
    return float(np.corrcoef(aa, bb)[0, 1])


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(view.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in view.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def make_e216_tensors() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    train_raw, sub_raw, train_feat, sub_feat = e216.read_frames()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    if not sub_feat[e216.SUB_KEY].astype(str).equals(sample[KEYS].astype(str)):
        raise RuntimeError("submission feature order differs from sample order")
    stage2_oof = clip_prob(np.load(OUT / e216.STAGE2_OOF))
    stage2_sub = e216.load_prob(e216.STAGE2_FILE, sample)
    ops = e216.combo_defs()["s2_rank"]
    full_oof = e216.apply_ops_oof(train_feat, stage2_oof, ops)
    full_sub = e216.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
    return train_raw, sub_raw, train_feat, sub_feat, stage2_oof, full_oof, stage2_sub, full_sub, sample


def add_row_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    ordered = frame.sort_values(["subject_id", "lifelog_date"]).copy()
    pos = ordered.groupby("subject_id").cumcount()
    size = ordered.groupby("subject_id")["subject_id"].transform("size")
    out.loc[ordered.index, "subject_pos"] = pos.to_numpy(dtype=np.float64)
    out.loc[ordered.index, "subject_size"] = size.to_numpy(dtype=np.float64)
    out.loc[ordered.index, "subject_pos_frac"] = pos.to_numpy(dtype=np.float64) / np.maximum(size.to_numpy(dtype=np.float64) - 1.0, 1.0)
    out["lifelog_weekday"] = pd.to_datetime(frame["lifelog_date"]).dt.weekday.astype(float)
    out["sleep_weekday"] = pd.to_datetime(frame["sleep_date"]).dt.weekday.astype(float)
    out["date_gap_days"] = (
        pd.to_datetime(frame["sleep_date"]) - pd.to_datetime(frame["lifelog_date"])
    ).dt.days.astype(float)
    return out


def feature_matrix(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    stage2_oof: np.ndarray,
    full_oof: np.ndarray,
    stage2_sub: np.ndarray,
    full_sub: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_x = train_feat[[c for c in train_feat.columns if c.startswith("e215_")]].copy()
    sub_x = sub_feat[[c for c in sub_feat.columns if c.startswith("e215_")]].copy()
    train_x = pd.concat([train_x, add_row_features(train_feat)], axis=1)
    sub_x = pd.concat([sub_x, add_row_features(sub_feat)], axis=1)

    for name, arr in [
        ("base_s2", stage2_oof[:, S2_IDX]),
        ("full_s2", full_oof[:, S2_IDX]),
    ]:
        train_x[name] = arr
    for name, arr in [
        ("base_s2", stage2_sub[:, S2_IDX]),
        ("full_s2", full_sub[:, S2_IDX]),
    ]:
        sub_x[name] = arr

    train_delta_z = logit(full_oof[:, [S2_IDX]]).reshape(-1) - logit(stage2_oof[:, [S2_IDX]]).reshape(-1)
    sub_delta_z = logit(full_sub[:, [S2_IDX]]).reshape(-1) - logit(stage2_sub[:, [S2_IDX]]).reshape(-1)
    for x, dz in [(train_x, train_delta_z), (sub_x, sub_delta_z)]:
        x["delta_s2_logit"] = dz
        x["abs_delta_s2_logit"] = np.abs(dz)
        x["moves_s2_up"] = (dz > 0).astype(float)
        x["base_s2_margin"] = np.abs(x["base_s2"].to_numpy(dtype=np.float64) - 0.5)
        x["full_s2_margin"] = np.abs(x["full_s2"].to_numpy(dtype=np.float64) - 0.5)
        x["base_full_s2_gap"] = x["full_s2"].to_numpy(dtype=np.float64) - x["base_s2"].to_numpy(dtype=np.float64)
        x["abs_base_full_s2_gap"] = np.abs(x["base_full_s2_gap"].to_numpy(dtype=np.float64))

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
        "lr_l2_c0p15": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.15,
                        l1_ratio=0.0,
                        solver="lbfgs",
                        class_weight="balanced",
                        max_iter=3000,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
        "lr_l1_c0p05": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.05,
                        l1_ratio=1.0,
                        solver="liblinear",
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
                        min_samples_leaf=18,
                        l2_regularization=0.5,
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
                        n_estimators=70,
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
    return np.clip(prob, 1.0e-6, 1.0 - 1.0e-6)


def subject_win_rate(train_raw: pd.DataFrame, y_s2: np.ndarray, base: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    rows: list[float] = []
    for _, idx in train_raw.groupby("subject_id").groups.items():
        arr = np.array(list(idx), dtype=int)
        rows.append(float(loss_vec(y_s2[arr], pred[arr]).mean() - loss_vec(y_s2[arr], base[arr]).mean()))
    vals = np.asarray(rows, dtype=np.float64)
    return float(vals.mean()), float((vals < 0.0).mean())


def scan_oof_gates(
    name: str,
    prob: np.ndarray,
    train_raw: pd.DataFrame,
    support: np.ndarray,
    benefit: np.ndarray,
    y_s2: np.ndarray,
    base_s2: np.ndarray,
    full_s2: np.ndarray,
) -> pd.DataFrame:
    gates: dict[str, np.ndarray] = {}
    for thr in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        gates[f"prob_ge_{str(thr).replace('.', 'p')}"] = prob >= thr
    order = np.argsort(prob)[::-1]
    for k in [10, 20, 30, 40, 50, 75, 100, 125, 150, 175, 200, 250]:
        mask = np.zeros(len(prob), dtype=bool)
        mask[order[: min(k, len(prob))]] = True
        gates[f"top{k}"] = mask
    score = prob * np.abs(full_s2 - base_s2)
    order_score = np.argsort(score)[::-1]
    for k in [20, 40, 60, 80, 100, 125, 150]:
        mask = np.zeros(len(prob), dtype=bool)
        mask[order_score[: min(k, len(prob))]] = True
        gates[f"score_top{k}"] = mask

    rows: list[dict[str, Any]] = []
    base_loss = float(loss_vec(y_s2, base_s2).mean())
    full_loss = float(loss_vec(y_s2, full_s2).mean())
    for gate, mask in gates.items():
        pred = base_s2.copy()
        pred[mask] = full_s2[mask]
        s_delta = float(loss_vec(y_s2, pred).mean() - base_loss)
        sub_delta_mean, sub_win = subject_win_rate(train_raw, y_s2, base_s2, pred)
        rec: dict[str, Any] = {
            "model_split": name,
            "gate": gate,
            "selected_rows": int(mask.sum()),
            "support_precision": float(support[mask].mean()) if mask.any() else np.nan,
            "support_recall": float(support[mask].sum() / max(support.sum(), 1)),
            "mean_support_prob": float(prob[mask].mean()) if mask.any() else np.nan,
            "benefit_sum": float(benefit[mask].sum()) if mask.any() else 0.0,
            "benefit_mean": float(benefit[mask].mean()) if mask.any() else np.nan,
            "s2_target_delta": s_delta,
            "overall_delta": s_delta / len(TARGETS),
            "subject_delta_mean": sub_delta_mean,
            "subject_win_rate": sub_win,
            "full_s2_target_delta": full_loss - base_loss,
        }
        rec["oof_gate_pass"] = bool(
            rec["selected_rows"] >= 10
            and rec["s2_target_delta"] < -7.5e-4
            and rec["subject_win_rate"] >= 0.60
            and rec["support_precision"] >= 0.55
        )
        rec["oof_score"] = (
            -rec["s2_target_delta"]
            + max(rec["subject_win_rate"] - 0.5, 0.0) * 0.0005
            + max(rec["support_precision"] - 0.5, 0.0) * 0.0008
            - max(rec["selected_rows"] - 160, 0) * 1.0e-6
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def submission_metrics(
    model_split: str,
    gate: str,
    mask: np.ndarray,
    sample: pd.DataFrame,
    base_e95: np.ndarray,
    stage2_sub: np.ndarray,
    full_sub: np.ndarray,
    priors: dict[str, np.ndarray],
    scale: float,
) -> dict[str, Any]:
    candidate = base_e95.copy()
    dz = logit(full_sub[:, [S2_IDX]]).reshape(-1) - logit(stage2_sub[:, [S2_IDX]]).reshape(-1)
    idx = np.where(mask)[0]
    if len(idx):
        z = logit(base_e95[idx, [S2_IDX]]).reshape(-1) + scale * dz[idx]
        candidate[idx, S2_IDX] = sigmoid(z)

    dy1, dy0 = hard_loss_deltas(candidate[idx, S2_IDX], base_e95[idx, S2_IDX]) if len(idx) else (np.array([]), np.array([]))
    swing = np.abs(dy1 - dy0)
    support_label = (dy1 < dy0).astype(int)
    support_delta = np.minimum(dy1, dy0)
    adverse_delta = np.maximum(dy1, dy0)
    focus_py = priors["focus_mean"][idx, S2_IDX] if len(idx) else np.array([])
    expected_focus = focus_py * dy1 + (1.0 - focus_py) * dy0 if len(idx) else np.array([])
    support_prob = np.where(support_label == 1, focus_py, 1.0 - focus_py) if len(idx) else np.array([])
    rec: dict[str, Any] = {
        "model_split": model_split,
        "gate": gate,
        "scale": scale,
        "selected_rows_sub": int(len(idx)),
        "expected_focus": float(expected_focus.sum()) if len(idx) else 0.0,
        "adverse_delta": float(adverse_delta.sum()) if len(idx) else 0.0,
        "support_delta": float(support_delta.sum()) if len(idx) else 0.0,
        "total_swing": float(swing.sum()) if len(idx) else 0.0,
        "support_prob_focus_weighted": float(np.average(support_prob, weights=swing)) if len(idx) and float(swing.sum()) > EPS else np.nan,
        "top1_swing_share": float(np.max(swing) / max(float(swing.sum()), EPS)) if len(idx) else 0.0,
        "adverse_over_observed_miss": float(adverse_delta.sum() / OBS_MISS) if len(idx) else 0.0,
    }
    rec["submission_gate_pass"] = bool(
        rec["selected_rows_sub"] >= 10
        and rec["expected_focus"] < -1.0e-5
        and rec["adverse_delta"] < OBS_MISS
        and rec["support_prob_focus_weighted"] >= 0.50
        and rec["top1_swing_share"] <= 0.35
    )
    rec["submission_score"] = (
        -rec["expected_focus"] * 8.0
        - max(rec["adverse_delta"] - OBS_MISS, 0.0) * 25.0
        + max(rec["support_prob_focus_weighted"] - 0.5, 0.0) * 0.001
        - rec["top1_swing_share"] * 0.0002
    )
    return rec


def materialize(
    sample: pd.DataFrame,
    base_e95: np.ndarray,
    stage2_sub: np.ndarray,
    full_sub: np.ndarray,
    mask: np.ndarray,
    tag: str,
    scale: float,
) -> str:
    candidate = base_e95.copy()
    idx = np.where(mask)[0]
    dz = logit(full_sub[:, [S2_IDX]]).reshape(-1) - logit(stage2_sub[:, [S2_IDX]]).reshape(-1)
    if len(idx):
        candidate[idx, S2_IDX] = sigmoid(logit(base_e95[idx, [S2_IDX]]).reshape(-1) + scale * dz[idx])
    digest = hashlib.sha1(np.round(candidate, 10).tobytes()).hexdigest()[:8]
    scale_tag = str(scale).replace(".", "p")
    file_name = f"submission_e221_s2oofgate_{tag[:38]}_s{scale_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(candidate)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def write_report(
    model_df: pd.DataFrame,
    gate_df: pd.DataFrame,
    sub_df: pd.DataFrame,
    selected: pd.DataFrame,
    support_rate: float,
    full_delta: float,
) -> None:
    lines = [
        "# E221 S2 OOF Support Classifier",
        "",
        "## Question",
        "",
        "Can E216's S2 masked-family JEPA movement be rescued by a train/OOF-reproducible classifier that predicts where the movement helps?",
        "",
        "## Setup",
        "",
        f"- Train support-label rate: `{support_rate:.6f}`.",
        f"- Full E216 S2 target OOF delta versus stage2: `{full_delta:.9f}`.",
        f"- Public miss to explain: E216-E95 `+{OBS_MISS:.10f}`.",
        "",
        "## Support Classifier Stress",
        "",
        md(
            model_df.sort_values(["split", "auc"], ascending=[True, False]),
            ["model", "split", "auc", "logloss", "brier", "corr_benefit", "mean_prob", "n"],
            n=40,
        ),
        "",
        "## Best OOF Gates",
        "",
        md(
            gate_df.sort_values(["oof_gate_pass", "oof_score"], ascending=[False, False]),
            [
                "model_split",
                "gate",
                "selected_rows",
                "support_precision",
                "support_recall",
                "s2_target_delta",
                "overall_delta",
                "subject_win_rate",
                "oof_gate_pass",
            ],
            n=40,
        ),
        "",
        "## Submission-Side Tail Stress",
        "",
        md(
            sub_df.sort_values(["joint_gate_pass", "joint_score"], ascending=[False, False]),
            [
                "model_split",
                "gate",
                "scale",
                "selected_rows_sub",
                "expected_focus",
                "adverse_delta",
                "adverse_over_observed_miss",
                "support_prob_focus_weighted",
                "top1_swing_share",
                "oof_gate_pass",
                "submission_gate_pass",
                "joint_gate_pass",
                "submission_file",
            ],
            n=40,
        ),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No E221 gate passed both OOF support reproduction and submission-side tail capacity stress.")
        lines.append("- This rejects the simplest trainable rescue of E216 S2. The masked-family JEPA representation remains diagnostic, but S2 probability translation should stay closed until a different target representation or non-S2 translator appears.")
    else:
        files = ", ".join(f"`{f}`" for f in selected["submission_file"].dropna().astype(str).tolist())
        lines.append(f"- E221 found trainable S2 OOF support gates that also pass tail stress. Candidate files: {files}.")
        lines.append("- These are E95-anchor S2-only grafts; the bet is that E216 failed because it moved too many low-support S2 cells, not because all masked-family S2 signal is false.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, _sub_raw, train_feat, sub_feat, stage2_oof, full_oof, stage2_sub, full_sub, sample = make_e216_tensors()
    y_s2 = train_raw["S2"].to_numpy(dtype=int)
    base_s2 = stage2_oof[:, S2_IDX]
    full_s2 = full_oof[:, S2_IDX]
    base_loss = loss_vec(y_s2, base_s2)
    full_loss = loss_vec(y_s2, full_s2)
    loss_delta = full_loss - base_loss
    support = (loss_delta < 0.0).astype(int)
    benefit = -loss_delta
    support_rate = float(support.mean())
    full_delta = float(full_loss.mean() - base_loss.mean())

    train_x, sub_x, features = feature_matrix(train_feat, sub_feat, stage2_oof, full_oof, stage2_sub, full_sub)
    groups = train_raw["subject_id"].astype(str).to_numpy()

    model_rows: list[dict[str, Any]] = []
    gate_parts: list[pd.DataFrame] = []
    sub_rows: list[dict[str, Any]] = []
    fitted_sub_probs: dict[str, np.ndarray] = {}
    models = model_defs()
    splits = split_defs()
    priors = e162.prior_arrays(sample)
    base_e95 = e216.load_prob(E95_FILE, sample)

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
            gate_parts.append(scan_oof_gates(model_split, prob, train_raw, support, benefit, y_s2, base_s2, full_s2))
            fitted = clone(model)
            fitted.fit(train_x[features], support)
            fitted_sub_probs[model_split] = fitted.predict_proba(sub_x[features])[:, 1]

    model_df = pd.DataFrame(model_rows)
    gate_df = pd.concat(gate_parts, ignore_index=True)

    for row in gate_df.itertuples(index=False):
        model_split = str(row.model_split)
        gate = str(row.gate)
        prob_sub = fitted_sub_probs[model_split]
        if gate.startswith("prob_ge_"):
            thr = float(gate.replace("prob_ge_", "").replace("p", "."))
            mask = prob_sub >= thr
        elif gate.startswith("top"):
            k = int(gate.replace("top", ""))
            order = np.argsort(prob_sub)[::-1]
            mask = np.zeros(len(prob_sub), dtype=bool)
            mask[order[: min(k, len(prob_sub))]] = True
        elif gate.startswith("score_top"):
            k = int(gate.replace("score_top", ""))
            score = prob_sub * np.abs(full_sub[:, S2_IDX] - stage2_sub[:, S2_IDX])
            order = np.argsort(score)[::-1]
            mask = np.zeros(len(prob_sub), dtype=bool)
            mask[order[: min(k, len(prob_sub))]] = True
        else:
            continue
        for scale in [0.35, 0.50, 0.75, 1.00]:
            rec = submission_metrics(model_split, gate, mask, sample, base_e95, stage2_sub, full_sub, priors, scale)
            rec["oof_gate_pass"] = bool(getattr(row, "oof_gate_pass"))
            rec["s2_target_delta"] = float(getattr(row, "s2_target_delta"))
            rec["subject_win_rate"] = float(getattr(row, "subject_win_rate"))
            rec["support_precision"] = float(getattr(row, "support_precision")) if not pd.isna(getattr(row, "support_precision")) else np.nan
            rec["joint_gate_pass"] = bool(rec["oof_gate_pass"] and rec["submission_gate_pass"])
            rec["joint_score"] = float(getattr(row, "oof_score")) + rec["submission_score"]
            sub_rows.append(rec)

    sub_df = pd.DataFrame(sub_rows)
    selected = sub_df[sub_df["joint_gate_pass"]].sort_values(["joint_score", "expected_focus"], ascending=[False, True]).head(3).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        prob_sub = fitted_sub_probs[str(row.model_split)]
        gate = str(row.gate)
        if gate.startswith("prob_ge_"):
            thr = float(gate.replace("prob_ge_", "").replace("p", "."))
            mask = prob_sub >= thr
        elif gate.startswith("top"):
            k = int(gate.replace("top", ""))
            order = np.argsort(prob_sub)[::-1]
            mask = np.zeros(len(prob_sub), dtype=bool)
            mask[order[: min(k, len(prob_sub))]] = True
        else:
            k = int(gate.replace("score_top", ""))
            score = prob_sub * np.abs(full_sub[:, S2_IDX] - stage2_sub[:, S2_IDX])
            order = np.argsort(score)[::-1]
            mask = np.zeros(len(prob_sub), dtype=bool)
            mask[order[: min(k, len(prob_sub))]] = True
        tag = f"{str(row.model_split).replace('__', '_')}_{gate}"
        files.append(materialize(sample, base_e95, stage2_sub, full_sub, mask, tag, float(row.scale)))
    if not selected.empty:
        selected = selected.copy()
        selected["submission_file"] = files
        sub_df = sub_df.merge(
            selected[["model_split", "gate", "scale", "submission_file"]],
            on=["model_split", "gate", "scale"],
            how="left",
        )
    else:
        sub_df["submission_file"] = ""
        selected["submission_file"] = ""

    model_df.to_csv(MODEL_OUT, index=False)
    gate_df.to_csv(GATE_OUT, index=False)
    sub_df.to_csv(SUB_SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(model_df, gate_df, sub_df, selected, support_rate, full_delta)

    print("[support]")
    print({"support_rate": round(support_rate, 6), "full_s2_target_delta": round(full_delta, 9), "n_features": len(features)})
    print("\n[model stress]")
    print(model_df.sort_values(["split", "auc"], ascending=[True, False]).round(9).to_string(index=False))
    print("\n[oof gate top]")
    print(
        gate_df.sort_values(["oof_gate_pass", "oof_score"], ascending=[False, False])[
            ["model_split", "gate", "selected_rows", "support_precision", "s2_target_delta", "subject_win_rate", "oof_gate_pass"]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )
    print("\n[submission stress top]")
    cols = [
        "model_split",
        "gate",
        "scale",
        "selected_rows_sub",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_weighted",
        "oof_gate_pass",
        "submission_gate_pass",
        "joint_gate_pass",
        "submission_file",
    ]
    print(sub_df.sort_values(["joint_gate_pass", "joint_score"], ascending=[False, False])[cols].head(25).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
