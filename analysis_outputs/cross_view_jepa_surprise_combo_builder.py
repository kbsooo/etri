from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import broad_single_feature_residual_probe as broad
import geometry_mask_cv_experiments as geom


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

FEATURES = OUT / "cross_view_jepa_surprise_features.parquet"
GUARD = OUT / "cross_view_jepa_surprise_guardrail.csv"
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"

SUMMARY_OUT = OUT / "cross_view_jepa_surprise_combo_summary.csv"
TARGET_OUT = OUT / "cross_view_jepa_surprise_combo_targets.csv"
SUBJECT_OUT = OUT / "cross_view_jepa_surprise_combo_subject_halves.csv"
GEOMETRY_OUT = OUT / "cross_view_jepa_surprise_combo_geometry.csv"
REPORT_OUT = OUT / "cross_view_jepa_surprise_combo_report.md"


@dataclass(frozen=True)
class Op:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_raw = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub_raw = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train_raw = train_raw.sort_values(KEY).reset_index(drop=True)
    sub_raw = sub_raw.sort_values(KEY).reset_index(drop=True)
    features = pd.read_parquet(FEATURES)
    features["lifelog_date"] = pd.to_datetime(features["lifelog_date"])
    train_feat = train_raw.merge(
        features[features["split"].eq("train")].drop(columns=["sleep_date", "split"]),
        on=KEY,
        how="left",
    )
    sub_feat = sub_raw.merge(
        features[features["split"].eq("submission")].drop(columns=["sleep_date", "split"]),
        on=KEY,
        how="left",
    )
    assert len(train_feat) == len(train_raw)
    assert len(sub_feat) == len(sub_raw)
    return train_raw, sub_raw, train_feat, sub_feat


def top_ops() -> dict[str, Op]:
    guard = pd.read_csv(GUARD)
    guard = guard[guard["strict_pass"].astype(bool)].copy()
    # Use only the best strict row per target. Q2 has no improving strict row in
    # the scan because its best blend selected zero weight.
    guard = guard[guard["target"].ne("Q2")]
    best = guard.sort_values(["target", "delta", "guard_mean_delta"]).groupby("target", as_index=False).head(1)
    return {
        str(row.target): Op(
            target=str(row.target),
            feature=str(row.feature),
            mode=str(row.mode),
            c_value=float(row.c_value),
            weight=float(row.best_weight),
        )
        for row in best.itertuples(index=False)
    }


def combo_defs() -> dict[str, list[Op]]:
    ops = top_ops()
    strong = [ops[t] for t in ["Q1", "Q3", "S1", "S2", "S3", "S4"] if t in ops]
    core = [ops[t] for t in ["Q1", "Q3", "S2", "S4"] if t in ops]
    qs = [ops[t] for t in ["Q1", "Q3"] if t in ops]
    sside = [ops[t] for t in ["S1", "S2", "S3", "S4"] if t in ops]
    top2 = [ops[t] for t in ["Q1", "S2"] if t in ops]

    def cap(op: Op, weight: float) -> Op:
        return Op(op.target, op.feature, op.mode, op.c_value, min(op.weight, weight))

    return {
        "cvjepa_surprise_q1_s2": top2,
        "cvjepa_surprise_core_q1_q3_s2_s4": core,
        "cvjepa_surprise_s_targets": sside,
        "cvjepa_surprise_full_nonq2": strong,
        "cvjepa_surprise_full_nonq2_w030": [cap(op, 0.30) for op in strong],
        "cvjepa_surprise_full_nonq2_w020": [cap(op, 0.20) for op in strong],
        "cvjepa_surprise_q_targets": qs,
    }


def apply_op_oof(rows: pd.DataFrame, pred: np.ndarray, op: Op) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.oof_corrected(rows, out, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_op_fit_predict(ref: pd.DataFrame, rows: pd.DataFrame, ref_pred: np.ndarray, row_pred: np.ndarray, op: Op) -> np.ndarray:
    out = row_pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.fit_corrected(ref, rows, ref_pred, row_pred, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_ops_oof(rows: pd.DataFrame, base: np.ndarray, ops: list[Op]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        out = apply_op_oof(rows, out, op)
    return clip(out)


def subject_half_summary(train: pd.DataFrame, y: np.ndarray, base: np.ndarray, pred: np.ndarray, name: str) -> pd.DataFrame:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(270528)
    rows = []
    for repeat in range(260):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        hold = ~train["subject_id"].astype(str).isin(picked).to_numpy()
        row = {
            "combo": name,
            "repeat": repeat,
            "base_mean": mean_loss(y[hold], base[hold]),
            "candidate_mean": mean_loss(y[hold], pred[hold]),
        }
        row["delta_mean"] = row["candidate_mean"] - row["base_mean"]
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y[hold, j], pred[hold, j]) - loss_col(y[hold, j], base[hold, j])
        rows.append(row)
    return pd.DataFrame(rows)


def geometry_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    base: np.ndarray,
    ops: list[Op],
    name: str,
) -> pd.DataFrame:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=270528):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_pred = base[tr_idx].copy()
        val_pred = base[val_idx].copy()
        for op in ops:
            val_pred = apply_op_fit_predict(ref, val, ref_pred, val_pred, op)
            ref_pred = apply_op_fit_predict(ref, ref, ref_pred, ref_pred, op)
        y = y_all[val_idx]
        row = {
            "combo": name,
            "fold": fold,
            "base_mean": mean_loss(y, base[val_idx]),
            "candidate_mean": mean_loss(y, val_pred),
        }
        row["delta_mean"] = row["candidate_mean"] - row["base_mean"]
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = loss_col(y[:, j], val_pred[:, j]) - loss_col(y[:, j], base[val_idx, j])
        rows.append(row)
    return pd.DataFrame(rows)


def save_submission(name: str, train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base_oof: np.ndarray, ops: list[Op], pred_oof: np.ndarray) -> None:
    out = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert out[SUB_KEY].equals(sample[SUB_KEY])
    pred_sub = out[TARGETS].to_numpy(dtype=float)
    ref_pred = base_oof.copy()
    for op in ops:
        pred_sub = apply_op_fit_predict(train_feat, sub_feat, ref_pred, pred_sub, op)
        ref_pred = apply_op_fit_predict(train_feat, train_feat, ref_pred, ref_pred, op)
    out[TARGETS] = clip(pred_sub)
    assert out[TARGETS].isna().sum().sum() == 0
    assert out.duplicated(SUB_KEY).sum() == 0
    np.save(OUT / f"final_{name}_oof.npy", pred_oof)
    out.to_csv(OUT / f"submission_{name}.csv", index=False)


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, subject_df: pd.DataFrame, geometry_df: pd.DataFrame) -> None:
    best = summary.sort_values(["candidate_loss", "geometry_delta", "subject_half_delta"]).iloc[0]
    lines = [
        "# Cross-View JEPA Surprise Combo Report",
        "",
        "Target-wise strict cross-view JEPA surprise corrections are combined on top of the stage2 public anchor.",
        "",
        "## Summary",
        "",
        "```csv",
        summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best Candidate",
        "",
        f"- Best by OOF/geometry: `{best['combo']}`.",
        f"- OOF mean: `{best['candidate_loss']:.10f}` vs base `{best['base_loss']:.10f}`; delta `{best['delta']:.10f}`.",
        f"- Subject-half mean delta/win-rate: `{best['subject_half_delta']:.10f}` / `{best['subject_half_win_rate']:.6f}`.",
        f"- Geometry mean delta/win-rate: `{best['geometry_delta']:.10f}` / `{best['geometry_win_rate']:.6f}`.",
        "",
        "## Target Deltas",
        "",
        "```csv",
        target_df.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Interpretation",
        "",
        "- This is the first explicitly cross-view JEPA residual feature family that opens stage2 OOF while passing repeated subject-half checks on multiple targets.",
        "- Public risk is still nontrivial because stage2's broad residual public transfer was weak; these files should be audited against public-axis/ranker tools before promotion.",
        "- The main latent clue is view mismatch: context cannot predict quiet-window structure for Q1, measurement-process cannot predict rhythm for S2, and sleep/rhythm residuals explain Q3/S4.",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    base = clip(np.load(BASE_OOF))
    if base.shape != y.shape:
        raise ValueError(f"base shape {base.shape} != y shape {y.shape}")
    base_loss = mean_loss(y, base)

    summary_rows = []
    target_rows = []
    subject_parts = []
    geometry_parts = []
    preds = {}
    combos = combo_defs()
    for name, ops in combos.items():
        pred = apply_ops_oof(train_feat, base, ops)
        preds[name] = pred
        subj = subject_half_summary(train_raw, y, base, pred, name)
        geo = geometry_summary(train_raw, sub_raw, train_feat, base, ops, name)
        subject_parts.append(subj)
        geometry_parts.append(geo)

        row = {
            "combo": name,
            "n_ops": len(ops),
            "targets": ",".join(op.target for op in ops),
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred),
            "delta": mean_loss(y, pred) - base_loss,
            "subject_half_delta": float(subj["delta_mean"].mean()),
            "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
            "geometry_delta": float(geo["delta_mean"].mean()),
            "geometry_win_rate": float((geo["delta_mean"] < 0).mean()),
        }
        summary_rows.append(row)
        for j, target in enumerate(TARGETS):
            target_rows.append(
                {
                    "combo": name,
                    "target": target,
                    "base_loss": loss_col(y[:, j], base[:, j]),
                    "candidate_loss": loss_col(y[:, j], pred[:, j]),
                    "delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j]),
                }
            )

    summary = pd.DataFrame(summary_rows).sort_values(["candidate_loss", "geometry_delta"]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    subject_df = pd.concat(subject_parts, ignore_index=True)
    geometry_df = pd.concat(geometry_parts, ignore_index=True)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    subject_df.to_csv(SUBJECT_OUT, index=False)
    geometry_df.to_csv(GEOMETRY_OUT, index=False)

    # Save all combos with OOF and both robustness layers improving on average.
    for row in summary.itertuples(index=False):
        if float(row.delta) < 0.0 and float(row.subject_half_delta) < 0.0 and float(row.geometry_delta) < 0.0:
            save_submission(str(row.combo), train_feat, sub_feat, base, combos[str(row.combo)], preds[str(row.combo)])

    write_report(summary, target_df, subject_df, geometry_df)
    print("[summary]")
    print(summary.round(10).to_string(index=False))
    print(f"\nwrote: {SUMMARY_OUT}")
    print(f"wrote: {TARGET_OUT}")
    print(f"wrote: {SUBJECT_OUT}")
    print(f"wrote: {GEOMETRY_OUT}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
