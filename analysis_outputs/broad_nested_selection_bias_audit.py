from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import broad_feature_addon_builder as b1  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
C_GRID = [0.05, 0.10, 0.20, 0.50]


@dataclass(frozen=True)
class SelectedOp:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float
    inner_delta: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def known_stage2_ops() -> list[b1.FeatureOp]:
    return [
        b1.FeatureOp("Q1", "deep__watch_light_w_light_all_log_mean", "subject_center", 0.50, 0.45),
        b1.FeatureOp("Q3", "deep__ble_morning_unique_max", "subject_rank", 0.20, 0.45),
        b1.FeatureOp("S1", "deep__ambience_all_hour_mean", "subject_z", 0.50, 0.45),
        b1.FeatureOp("S2", "deep__phone_light_m_light_late_median", "subject_z", 0.50, 0.45),
        b1.FeatureOp("S3", "deep__hr_all_rows", "subject_rank", 0.50, 0.45),
        b1.FeatureOp("S4", "deep__ambience_evening_top_is_outside_mean", "subject_center", 0.50, 0.45),
    ]


def choose_best_inner(
    inner: pd.DataFrame,
    inner_base: np.ndarray,
    target: str,
    pre: pd.DataFrame,
) -> tuple[SelectedOp | None, pd.DataFrame]:
    j = TARGETS.index(target)
    y = inner[target].to_numpy(dtype=int)
    base_loss = loss_col(y, inner_base[:, j])
    rows = []
    for cand in pre[pre["target"].eq(target)].itertuples(index=False):
        feature = str(cand.feature)
        mode = str(cand.mode)
        for c_value in C_GRID:
            corrected = broad.oof_corrected(inner, inner_base, target, feature, mode, c_value)
            losses = [loss_col(y, (1.0 - w) * inner_base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            rows.append(
                {
                    "target": target,
                    "feature": feature,
                    "mode": mode,
                    "corr": float(cand.corr),
                    "abs_corr": float(cand.abs_corr),
                    "c_value": float(c_value),
                    "base_loss": float(base_loss),
                    "best_weight": float(broad.GRID[best_i]),
                    "best_blend_loss": float(losses[best_i]),
                    "inner_delta": float(losses[best_i] - base_loss),
                }
            )
    cand_df = pd.DataFrame(rows)
    if cand_df.empty:
        return None, cand_df
    cand_df = cand_df.sort_values(["inner_delta", "best_weight"], ascending=[True, False]).reset_index(drop=True)
    top = cand_df.iloc[0]
    if float(top["best_weight"]) <= 0.0 or float(top["inner_delta"]) >= 0.0:
        return None, cand_df
    return (
        SelectedOp(
            target=str(top["target"]),
            feature=str(top["feature"]),
            mode=str(top["mode"]),
            c_value=float(top["c_value"]),
            weight=float(top["best_weight"]),
            inner_delta=float(top["inner_delta"]),
        ),
        cand_df,
    )


def apply_selected_to_holdout(
    inner: pd.DataFrame,
    holdout: pd.DataFrame,
    inner_base: np.ndarray,
    holdout_base: np.ndarray,
    op: SelectedOp,
) -> np.ndarray:
    j = TARGETS.index(op.target)
    corrected = broad.fit_corrected(
        inner,
        holdout,
        inner_base,
        holdout_base,
        op.target,
        op.feature,
        op.mode,
        op.c_value,
    )
    return clip((1.0 - op.weight) * holdout_base[:, j] + op.weight * corrected)


def evaluate_fixed_ops(
    inner: pd.DataFrame,
    holdout: pd.DataFrame,
    inner_base: np.ndarray,
    holdout_base: np.ndarray,
    y_holdout: np.ndarray,
    fold: str,
) -> tuple[pd.DataFrame, np.ndarray]:
    pred = holdout_base.copy()
    ref_pred = inner_base.copy()
    rows = []
    for op in known_stage2_ops():
        j = TARGETS.index(op.target)
        before_target = pred[:, j].copy()
        pred = b1.apply_op_fit_predict(inner, holdout, ref_pred, pred, op)
        ref_pred = b1.apply_op_fit_predict(inner, inner, ref_pred, ref_pred, op)
        rows.append(
            {
                "fold": fold,
                "target": op.target,
                "feature": op.feature,
                "mode": op.mode,
                "c_value": op.c_value,
                "weight": op.weight,
                "holdout_base_loss": loss_col(y_holdout[:, j], before_target),
                "holdout_candidate_loss": loss_col(y_holdout[:, j], pred[:, j]),
                "holdout_delta": loss_col(y_holdout[:, j], pred[:, j]) - loss_col(y_holdout[:, j], before_target),
            }
        )
    return pd.DataFrame(rows), pred


def summarize_selected(selected: pd.DataFrame) -> pd.DataFrame:
    if selected.empty:
        return pd.DataFrame()
    rows = []
    for target, g in selected.groupby("target", sort=False):
        rows.append(
            {
                "target": str(target),
                "n_selected": int(len(g)),
                "inner_delta_mean": float(g["inner_delta"].mean()),
                "holdout_delta_mean": float(g["holdout_delta"].mean()),
                "holdout_delta_median": float(g["holdout_delta"].median()),
                "holdout_win_rate": float((g["holdout_delta"] < 0.0).mean()),
                "mean_weight": float(g["weight"].mean()),
                "top_features": "; ".join(
                    f"{idx[0]}|{idx[1]}:{cnt}"
                    for idx, cnt in g.groupby(["feature", "mode"]).size().sort_values(ascending=False).head(5).items()
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["holdout_delta_mean", "target"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity_oof.npy")
    parser.add_argument("--prefix", default="broad_nested_selection_bias_audit")
    parser.add_argument("--targets", default="Q1,Q2,Q3,S1,S2,S3,S4")
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--outer-repeats", type=int, default=8)
    args = parser.parse_args()

    train_raw, sub_raw, train_feat, _sub_feat = b1.build_frames()
    assert train_raw[["subject_id", "lifelog_date"]].equals(train_feat[["subject_id", "lifelog_date"]])
    base = clip(np.load(args.base_oof))
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    targets = [t for t in args.targets.split(",") if t]

    candidate_rows: list[pd.DataFrame] = []
    selected_rows = []
    fold_rows = []
    fixed_rows: list[pd.DataFrame] = []

    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=args.outer_repeats):
        inner = train_feat.iloc[tr_idx].reset_index(drop=True)
        holdout = train_feat.iloc[val_idx].reset_index(drop=True)
        inner_base = base[tr_idx].copy()
        holdout_base = base[val_idx].copy()
        y_holdout = y_all[val_idx]
        cols = broad.finite_numeric_cols(inner)
        pre = broad.prefilter(inner, inner_base, cols, targets, args.top_n)
        pre.to_csv(OUT / f"{args.prefix}_{fold}_prefilter.csv", index=False)

        nested_pred = holdout_base.copy()
        selected_targets = []
        for target in targets:
            op, cand_df = choose_best_inner(inner, inner_base, target, pre)
            if not cand_df.empty:
                cand_df.insert(0, "fold", fold)
                candidate_rows.append(cand_df)
            if op is None:
                continue
            j = TARGETS.index(target)
            holdout_pred_col = apply_selected_to_holdout(inner, holdout, inner_base, holdout_base, op)
            base_loss = loss_col(y_holdout[:, j], holdout_base[:, j])
            cand_loss = loss_col(y_holdout[:, j], holdout_pred_col)
            nested_pred[:, j] = holdout_pred_col
            selected_targets.append(target)
            selected_rows.append(
                {
                    "fold": fold,
                    "target": target,
                    "feature": op.feature,
                    "mode": op.mode,
                    "c_value": op.c_value,
                    "weight": op.weight,
                    "inner_delta": op.inner_delta,
                    "holdout_base_loss": base_loss,
                    "holdout_candidate_loss": cand_loss,
                    "holdout_delta": cand_loss - base_loss,
                }
            )

        fixed_df, fixed_pred = evaluate_fixed_ops(inner, holdout, inner_base, holdout_base, y_holdout, fold)
        fixed_rows.append(fixed_df)
        fold_rows.append(
            {
                "fold": fold,
                "train_rows": int(len(tr_idx)),
                "holdout_rows": int(len(val_idx)),
                "selected_targets": ",".join(selected_targets),
                "base_mean_loss": mean_loss(y_holdout, holdout_base),
                "nested_mean_loss": mean_loss(y_holdout, nested_pred),
                "nested_delta": mean_loss(y_holdout, nested_pred) - mean_loss(y_holdout, holdout_base),
                "fixed_stage2_mean_loss": mean_loss(y_holdout, fixed_pred),
                "fixed_stage2_delta": mean_loss(y_holdout, fixed_pred) - mean_loss(y_holdout, holdout_base),
            }
        )
        print(
            f"[{fold}] nested_delta={fold_rows[-1]['nested_delta']:.6f} "
            f"fixed_stage2_delta={fold_rows[-1]['fixed_stage2_delta']:.6f} "
            f"selected={fold_rows[-1]['selected_targets']}",
            flush=True,
        )

    cand = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    selected = pd.DataFrame(selected_rows)
    folds = pd.DataFrame(fold_rows)
    fixed = pd.concat(fixed_rows, ignore_index=True) if fixed_rows else pd.DataFrame()
    selected_summary = summarize_selected(selected)
    fixed_summary = (
        fixed.groupby("target", as_index=False)
        .agg(
            holdout_delta_mean=("holdout_delta", "mean"),
            holdout_delta_median=("holdout_delta", "median"),
            holdout_win_rate=("holdout_delta", lambda s: float((s < 0.0).mean())),
            n_folds=("holdout_delta", "size"),
        )
        .sort_values(["holdout_delta_mean", "target"])
        if not fixed.empty
        else pd.DataFrame()
    )
    overall = pd.DataFrame(
        [
            {
                "base_mean_loss": float(folds["base_mean_loss"].mean()),
                "nested_mean_loss": float(folds["nested_mean_loss"].mean()),
                "nested_delta_mean": float(folds["nested_delta"].mean()),
                "nested_win_rate": float((folds["nested_delta"] < 0.0).mean()),
                "fixed_stage2_mean_loss": float(folds["fixed_stage2_mean_loss"].mean()),
                "fixed_stage2_delta_mean": float(folds["fixed_stage2_delta"].mean()),
                "fixed_stage2_win_rate": float((folds["fixed_stage2_delta"] < 0.0).mean()),
            }
        ]
    )

    cand.to_csv(OUT / f"{args.prefix}_inner_candidates.csv", index=False)
    selected.to_csv(OUT / f"{args.prefix}_selected.csv", index=False)
    selected_summary.to_csv(OUT / f"{args.prefix}_selected_summary.csv", index=False)
    fixed.to_csv(OUT / f"{args.prefix}_fixed_stage2_outer.csv", index=False)
    fixed_summary.to_csv(OUT / f"{args.prefix}_fixed_stage2_summary.csv", index=False)
    folds.to_csv(OUT / f"{args.prefix}_folds.csv", index=False)
    overall.to_csv(OUT / f"{args.prefix}_overall.csv", index=False)

    print("\n[overall]")
    print(overall.round(9).to_string(index=False))
    print("\n[nested selected summary]")
    print(selected_summary.round(9).to_string(index=False))
    print("\n[fixed stage2 summary]")
    print(fixed_summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
