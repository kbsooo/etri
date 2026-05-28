from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(ANALYSIS))
import broad_single_feature_residual_probe as broad  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


C_GRID = [0.05, 0.20]


@dataclass(frozen=True)
class Op:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float
    inner_delta: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def choose_inner(inner: pd.DataFrame, base: np.ndarray, target: str, pre: pd.DataFrame) -> tuple[Op | None, pd.DataFrame]:
    y = inner[target].to_numpy(dtype=int)
    j = TARGETS.index(target)
    base_loss = loss_col(y, base[:, j])
    rows = []
    for cand in pre[pre["target"].eq(target)].itertuples(index=False):
        for c_value in C_GRID:
            corrected = broad.oof_corrected(inner, base, target, str(cand.feature), str(cand.mode), c_value)
            losses = [loss_col(y, (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            rows.append(
                {
                    "target": target,
                    "feature": str(cand.feature),
                    "mode": str(cand.mode),
                    "c_value": float(c_value),
                    "weight": float(broad.GRID[best_i]),
                    "base_loss": float(base_loss),
                    "best_loss": float(losses[best_i]),
                    "inner_delta": float(losses[best_i] - base_loss),
                    "corr": float(cand.corr),
                }
            )
    cand_df = pd.DataFrame(rows).sort_values(["inner_delta", "weight"], ascending=[True, False]) if rows else pd.DataFrame()
    if cand_df.empty:
        return None, cand_df
    top = cand_df.iloc[0]
    if float(top["weight"]) <= 0.0 or float(top["inner_delta"]) >= 0.0:
        return None, cand_df
    return (
        Op(
            str(top["target"]),
            str(top["feature"]),
            str(top["mode"]),
            float(top["c_value"]),
            float(top["weight"]),
            float(top["inner_delta"]),
        ),
        cand_df,
    )


def nested_audit(top_n: int = 5, repeats: int = 4) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    feat = pd.read_parquet(OUT / "train_jepa_features.parquet")
    df = train[SUB_KEY + TARGETS].merge(feat, on=SUB_KEY, how="left")
    base = clip(np.load(ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    y_all = df[TARGETS].to_numpy(dtype=int)

    selected_rows = []
    candidate_rows = []
    fold_rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=repeats):
        inner = df.iloc[tr_idx].reset_index(drop=True)
        hold = df.iloc[val_idx].reset_index(drop=True)
        inner_base = base[tr_idx].copy()
        hold_base = base[val_idx].copy()
        cols = broad.finite_numeric_cols(inner)
        pre = broad.prefilter(inner, inner_base, cols, TARGETS, top_n=top_n)
        pred = hold_base.copy()
        for target in TARGETS:
            op, cand_df = choose_inner(inner, inner_base, target, pre)
            if not cand_df.empty:
                cand_df.insert(0, "fold", fold)
                candidate_rows.append(cand_df)
            if op is None:
                continue
            j = TARGETS.index(target)
            corrected = broad.fit_corrected(inner, hold, inner_base, hold_base, op.target, op.feature, op.mode, op.c_value)
            pred[:, j] = clip((1.0 - op.weight) * hold_base[:, j] + op.weight * corrected)
            hold_delta = loss_col(y_all[val_idx, j], pred[:, j]) - loss_col(y_all[val_idx, j], hold_base[:, j])
            selected_rows.append({**op.__dict__, "fold": fold, "holdout_delta": float(hold_delta), "holdout_rows": int(len(val_idx))})
        fold_rows.append(
            {
                "fold": fold,
                "rows": int(len(val_idx)),
                "base_mean": mean_loss(y_all[val_idx], hold_base),
                "candidate_mean": mean_loss(y_all[val_idx], pred),
                "delta_mean": mean_loss(y_all[val_idx], pred) - mean_loss(y_all[val_idx], hold_base),
            }
        )
        print(f"nested {fold}: delta={fold_rows[-1]['delta_mean']:.6f}", flush=True)

    selected = pd.DataFrame(selected_rows)
    candidates = pd.concat(candidate_rows, ignore_index=True) if candidate_rows else pd.DataFrame()
    folds = pd.DataFrame(fold_rows)
    selected.to_csv(OUT / "jepa_nested_selected.csv", index=False)
    candidates.to_csv(OUT / "jepa_nested_inner_candidates.csv", index=False)
    folds.to_csv(OUT / "jepa_nested_folds.csv", index=False)
    if selected.empty:
        summary = pd.DataFrame()
    else:
        summary = (
            selected.groupby("target")
            .agg(
                n_selected=("target", "size"),
                inner_delta_mean=("inner_delta", "mean"),
                holdout_delta_mean=("holdout_delta", "mean"),
                holdout_delta_median=("holdout_delta", "median"),
                holdout_win_rate=("holdout_delta", lambda s: float((s < 0).mean())),
            )
            .reset_index()
            .sort_values("holdout_delta_mean")
        )
    summary.to_csv(OUT / "jepa_nested_summary.csv", index=False)
    return selected, folds, summary


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    return float(np.dot(aa, bb) / denom) if denom > 1e-12 else 0.0


def public_axis_audit() -> pd.DataFrame:
    files = {
        "anchor578": ANALYSIS / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "stage2_public_best": ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "ordinal_failed": ANALYSIS / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    }
    candidate_files = {
        "submission_jepa_selected.csv": OUT / "submission_jepa_selected.csv",
        "submission_neural_jepa_selected.csv": OUT / "submission_neural_jepa_selected.csv",
        "submission_jepa_nested_q2_probe.csv": OUT / "submission_jepa_nested_q2_probe.csv",
        "submission_jepa_axiscap_cap0p0_scale1p0.csv": OUT / "submission_jepa_axiscap_cap0p0_scale1p0.csv",
        "submission_jepa_axiscap_cap0p1_scale1p0.csv": OUT / "submission_jepa_axiscap_cap0p1_scale1p0.csv",
    }
    candidate_files = {k: v for k, v in candidate_files.items() if v.exists()}
    dfs = {k: pd.read_csv(v, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True) for k, v in files.items()}
    candidates = {k: pd.read_csv(v, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True) for k, v in candidate_files.items()}
    stage2 = logit(dfs["stage2_public_best"][TARGETS].to_numpy(dtype=float))
    anchor = logit(dfs["anchor578"][TARGETS].to_numpy(dtype=float))
    ordinal = logit(dfs["ordinal_failed"][TARGETS].to_numpy(dtype=float))
    good_axis = stage2 - anchor
    bad_axis = ordinal - stage2

    rows = []
    for name, df in candidates.items():
        move = logit(df[TARGETS].to_numpy(dtype=float)) - stage2
        rows.append(
            {
                "file": name,
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "rms_logit_move": float(np.sqrt(np.mean(move**2))),
                "cos_anchor_to_stage2_good_axis": cosine(move, good_axis),
                "cos_stage2_to_ordinal_bad_axis": cosine(move, bad_axis),
                "bad_axis_projection_ratio": float(np.dot(move.reshape(-1), bad_axis.reshape(-1)) / max(np.dot(bad_axis.reshape(-1), bad_axis.reshape(-1)), 1e-12)),
                "good_axis_projection_ratio": float(np.dot(move.reshape(-1), good_axis.reshape(-1)) / max(np.dot(good_axis.reshape(-1), good_axis.reshape(-1)), 1e-12)),
            }
        )
        for target in TARGETS:
            j = TARGETS.index(target)
            rows.append(
                {
                    "file": f"{name}:target_{target}",
                    "mean_abs_logit_move": float(np.mean(np.abs(move[:, j]))),
                    "rms_logit_move": float(np.sqrt(np.mean(move[:, j] ** 2))),
                    "cos_anchor_to_stage2_good_axis": cosine(move[:, j], good_axis[:, j]),
                    "cos_stage2_to_ordinal_bad_axis": cosine(move[:, j], bad_axis[:, j]),
                    "bad_axis_projection_ratio": float(np.dot(move[:, j], bad_axis[:, j]) / max(np.dot(bad_axis[:, j], bad_axis[:, j]), 1e-12)),
                    "good_axis_projection_ratio": float(np.dot(move[:, j], good_axis[:, j]) / max(np.dot(good_axis[:, j], good_axis[:, j]), 1e-12)),
                }
            )
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT / "jepa_public_axis_audit.csv", index=False)
    return audit


def main() -> None:
    selected, folds, summary = nested_audit()
    audit = public_axis_audit()
    q2_probe_path = OUT / "jepa_nested_q2_probe_summary.csv"
    q2_probe = pd.read_csv(q2_probe_path) if q2_probe_path.exists() else pd.DataFrame()
    lines = [
        "# JEPA Guardrail Audit",
        "",
        "## Nested Geometry Folds",
        "",
        folds.to_csv(index=False),
        "",
        "## Nested Target Summary",
        "",
        summary.to_csv(index=False) if not summary.empty else "No selected features.",
        "",
        "## Public Axis Audit",
        "",
        audit.to_csv(index=False),
    ]
    if not q2_probe.empty:
        lines.extend(
            [
                "",
                "## Nested Q2 Probe",
                "",
                q2_probe.to_csv(index=False),
                "",
                "Decision: keep `submission_jepa_nested_q2_probe.csv` as an exploratory Q2-only candidate, not as a strong safe submission.",
            ]
        )
    (OUT / "jepa_guardrail_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(folds.round(9).to_string(index=False))
    print(summary.round(9).to_string(index=False) if not summary.empty else "no selected")
    print(audit.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
