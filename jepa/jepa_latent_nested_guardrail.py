from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
ALPHA = 100.0

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def selected_ops() -> pd.DataFrame:
    ops = pd.read_csv(OUT / "jepa_latent_residual_probe_selected_ops.csv")
    return ops[ops["feature"].astype(str).str.startswith("brlatent_a100p0")].reset_index(drop=True)


def predict_blockrate_latent(
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    train_indices: np.ndarray,
    pred_indices: np.ndarray,
    lengths: dict[str, list[int]],
) -> np.ndarray:
    known = adv.known_mask_for_train(rows, train_indices)
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths)
    pred_blocks = adv.contiguous_val_blocks(rows, pred_indices)
    n_train = int(rows["train_idx"].max()) + 1
    out = np.full((n_train, 28), np.nan, dtype=float)
    if not train_blocks or not pred_blocks:
        return out
    x_train = np.vstack([adv.block_context_features(rows, x, y, b, known) for b in train_blocks])
    z_train = np.vstack([adv.target_latent(y[b]) for b in train_blocks])
    scaler, model = adv.fit_block_model(x_train, z_train, ALPHA)
    x_pred = np.vstack([adv.block_context_features(rows, x, y, b, known) for b in pred_blocks])
    z_pred = model.predict(scaler.transform(np.asarray(x_pred, dtype=np.float64)))
    for block_i, block in enumerate(pred_blocks):
        idx = rows.iloc[block]["train_idx"].to_numpy(dtype=int)
        out[idx] = z_pred[block_i]
    return out


def inner_oof_latent(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    outer_train: np.ndarray,
    lengths: dict[str, list[int]],
    seed: int,
    repeats: int = 8,
) -> np.ndarray:
    outer_set = set(int(i) for i in outer_train)
    acc = np.zeros((len(train), 28), dtype=float)
    cnt = np.zeros(len(train), dtype=float)
    for tr_idx, val_idx, fold in adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=seed):
        inner_val = np.array([int(i) for i in val_idx if int(i) in outer_set], dtype=int)
        if len(inner_val) == 0:
            continue
        inner_val_set = set(int(i) for i in inner_val)
        inner_train = np.array([int(i) for i in outer_train if int(i) not in inner_val_set], dtype=int)
        if len(inner_train) < 100:
            continue
        latent = predict_blockrate_latent(rows, x, y, inner_train, inner_val, lengths)
        ok = np.isfinite(latent).any(axis=1)
        acc[ok] += latent[ok]
        cnt[ok] += 1.0
        print(f"nested inner {fold}: outer_covered={int((cnt > 0).sum())}", flush=True)
    out = np.full((len(train), 28), np.nan, dtype=float)
    ok = cnt > 0
    out[ok] = acc[ok] / cnt[ok, None]
    return out


def add_latent_columns(df: pd.DataFrame, latent: np.ndarray, base_slice: np.ndarray, prefix_indices: np.ndarray) -> pd.DataFrame:
    out = df.copy()
    groups = ["rate", "entropy", "first", "last"]
    for gi, group in enumerate(groups):
        for tj, target in enumerate(TARGETS):
            out[f"brlatent_a100p0_{group}_{target}"] = latent[prefix_indices, gi * len(TARGETS) + tj]
    for tj, target in enumerate(TARGETS):
        out[f"brlatent_a100p0_logit_delta_{target}"] = adv.logit(latent[prefix_indices, tj]) - adv.logit(base_slice[:, tj])
    return out


def main() -> None:
    ops = selected_ops()
    if ops.empty:
        raise SystemExit("No alpha=100 blockrate ops available for nested guardrail.")
    train, sub, base, base_sub = adv.read_data()
    rows, x, _base_all = adv.build_row_representation(train, sub, base, base_sub)
    y_all = adv.train_label_matrix(rows, train)
    y = train[TARGETS].to_numpy(dtype=int)
    lengths = adv.actual_lengths_by_subject(rows)
    fold_rows = []
    pred_all = base.copy()
    for fold_i, (outer_train, outer_val, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=4, seed=261777)):
        train_latent = inner_oof_latent(train, sub, rows, x, y_all, outer_train, lengths, seed=880000 + fold_i, repeats=8)
        val_latent = predict_blockrate_latent(rows, x, y_all, outer_train, outer_val, lengths)
        train_frame = add_latent_columns(train.iloc[outer_train][SUB_KEY + TARGETS].copy().reset_index(drop=True), train_latent, base[outer_train], outer_train)
        val_frame = add_latent_columns(train.iloc[outer_val][SUB_KEY + TARGETS].copy().reset_index(drop=True), val_latent, base[outer_val], outer_val)
        pred_val = base[outer_val].copy()
        for op in ops.itertuples(index=False):
            target = str(op.target)
            j = TARGETS.index(target)
            corr = broad.fit_corrected(
                train_frame,
                val_frame,
                base[outer_train],
                pred_val,
                target,
                str(op.feature),
                str(op.mode),
                float(op.c_value),
            )
            pred_val[:, j] = adv.clip((1.0 - float(op.weight)) * pred_val[:, j] + float(op.weight) * corr)
        pred_all[outer_val] = pred_val
        base_loss = adv.mean_loss(y[outer_val], base[outer_val])
        cand_loss = adv.mean_loss(y[outer_val], pred_val)
        row = {
            "fold": fold,
            "n_train": int(len(outer_train)),
            "n_val": int(len(outer_val)),
            "base_loss": base_loss,
            "candidate_loss": cand_loss,
            "delta": cand_loss - base_loss,
            "train_feature_coverage": float(np.isfinite(train_latent[outer_train]).any(axis=1).mean()),
            "val_feature_coverage": float(np.isfinite(val_latent[outer_val]).any(axis=1).mean()),
        }
        for j, target in enumerate(TARGETS):
            row[f"{target}_delta"] = broad.loss_col(y[outer_val, j], pred_val[:, j]) - broad.loss_col(y[outer_val, j], base[outer_val, j])
        fold_rows.append(row)
        print(f"nested {fold}: delta={row['delta']:.6f} train_cov={row['train_feature_coverage']:.3f} val_cov={row['val_feature_coverage']:.3f}", flush=True)
    folds = pd.DataFrame(fold_rows)
    folds.to_csv(OUT / "jepa_latent_nested_guardrail_folds.csv", index=False)
    np.save(OUT / "jepa_latent_nested_guardrail_oof.npy", pred_all)
    summary = pd.DataFrame(
        [
            {
                "folds": int(len(folds)),
                "base_loss": float(folds["base_loss"].mean()),
                "candidate_loss": float(folds["candidate_loss"].mean()),
                "mean_delta": float(folds["delta"].mean()),
                "median_delta": float(folds["delta"].median()),
                "win_rate": float((folds["delta"] < 0).mean()),
                "mean_train_feature_coverage": float(folds["train_feature_coverage"].mean()),
                "mean_val_feature_coverage": float(folds["val_feature_coverage"].mean()),
            }
        ]
    )
    summary.to_csv(OUT / "jepa_latent_nested_guardrail_summary.csv", index=False)
    report = [
        "# JEPA Latent Nested Guardrail",
        "",
        "This re-generates BlockRate latent features inside each outer geometry fold. Outer validation labels are never used for the latent generator or residual logistic fit.",
        "",
        "## Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Folds",
        "",
        folds.to_csv(index=False),
        "",
        "## Fixed Ops",
        "",
        ops.to_csv(index=False),
    ]
    (OUT / "jepa_latent_nested_guardrail_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
