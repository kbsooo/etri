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
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
ALPHAS = [1.0, 10.0, 100.0]
C_GRID = [0.05, 0.10, 0.20, 0.50]
WEIGHT_GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45])

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def qrank_latent(y_block: np.ndarray) -> np.ndarray:
    q_idx = [TARGETS.index(t) for t in Q_TARGETS]
    rates = np.nanmean(y_block[:, q_idx], axis=0)
    counts = np.nansum(y_block[:, q_idx], axis=0) / max(len(y_block), 1)
    ent = -(rates * np.log(adv.clip(rates)) + (1.0 - rates) * np.log(adv.clip(1.0 - rates)))
    return np.r_[rates, counts, ent, y_block[0, q_idx], y_block[-1, q_idx]].astype(np.float32)


def latent_names(prefix: str, alpha: float, kind: str) -> list[str]:
    a = str(alpha).replace(".", "p")
    if kind == "blockrate":
        groups = ["rate", "entropy", "first", "last"]
        return [f"{prefix}_a{a}_{group}_{target}" for group in groups for target in TARGETS]
    groups = ["rate", "count", "entropy", "first", "last"]
    return [f"{prefix}_a{a}_{group}_{target}" for group in groups for target in Q_TARGETS]


def fit_predict_latent(
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    train_blocks: list[np.ndarray],
    pred_blocks: list[np.ndarray],
    known: np.ndarray,
    alpha: float,
    kind: str,
) -> np.ndarray:
    x_train = np.vstack([adv.block_context_features(rows, x, y, b, known) for b in train_blocks])
    if kind == "blockrate":
        z_train = np.vstack([adv.target_latent(y[b]) for b in train_blocks])
    elif kind == "qrank":
        z_train = np.vstack([qrank_latent(y[b]) for b in train_blocks])
    else:
        raise ValueError(kind)
    scaler, model = adv.fit_block_model(x_train, z_train, alpha)
    x_pred = np.vstack([adv.block_context_features(rows, x, y, b, known) for b in pred_blocks])
    z_pred = model.predict(scaler.transform(np.asarray(x_pred, dtype=np.float64)))
    return np.nan_to_num(z_pred, nan=np.nan, posinf=np.nan, neginf=np.nan)


def build_latent_features(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    base: np.ndarray,
    base_sub: pd.DataFrame,
    kind: str,
    repeats: int = 16,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_dim = 28 if kind == "blockrate" else 15
    prefix = "brlatent" if kind == "blockrate" else "qrlatent"
    lengths = adv.actual_lengths_by_subject(rows)
    train_feat = train[SUB_KEY + TARGETS].copy()
    sub_feat = sub[SUB_KEY].copy()
    for alpha in ALPHAS:
        names = latent_names(prefix, alpha, kind)
        acc = np.zeros((len(train), n_dim), dtype=float)
        cnt = np.zeros(len(train), dtype=float)
        for tr_idx, val_idx, fold in adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=260991 + int(alpha * 17)):
            known = adv.known_mask_for_train(rows, tr_idx)
            train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths)
            val_blocks = adv.contiguous_val_blocks(rows, val_idx)
            if not train_blocks or not val_blocks:
                continue
            z_val = fit_predict_latent(rows, x, y, train_blocks, val_blocks, known, alpha, kind)
            for block_i, block in enumerate(val_blocks):
                idx = rows.iloc[block]["train_idx"].to_numpy(dtype=int)
                acc[idx] += z_val[block_i]
                cnt[idx] += 1.0
            print(f"{kind} alpha={alpha:g} {fold}: val_blocks={len(val_blocks)} covered={int((cnt > 0).sum())}", flush=True)
        latent = np.full((len(train), n_dim), np.nan, dtype=float)
        ok = cnt > 0
        latent[ok] = acc[ok] / cnt[ok, None]
        for i, name in enumerate(names):
            train_feat[name] = latent[:, i]
        for j, target in enumerate(TARGETS if kind == "blockrate" else Q_TARGETS):
            rate_col = names[j]
            train_feat[f"{prefix}_a{str(alpha).replace('.', 'p')}_logit_delta_{target}"] = adv.logit(latent[:, j]) - adv.logit(base[:, TARGETS.index(target)])

        known = adv.known_mask_for_train(rows, np.arange(len(train)))
        train_blocks = adv.make_training_blocks(rows, y, np.arange(len(train)), lengths, max_blocks_per_subject=240)
        sub_blocks = adv.submission_blocks(train, sub, rows)
        z_sub = fit_predict_latent(rows, x, y, train_blocks, sub_blocks, known, alpha, kind)
        sub_latent = np.full((len(sub), n_dim), np.nan, dtype=float)
        for block_i, block in enumerate(sub_blocks):
            idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
            sub_latent[idx] = z_sub[block_i]
        for i, name in enumerate(names):
            sub_feat[name] = sub_latent[:, i]
        sub_base = base_sub[TARGETS].to_numpy(dtype=float)
        for j, target in enumerate(TARGETS if kind == "blockrate" else Q_TARGETS):
            sub_feat[f"{prefix}_a{str(alpha).replace('.', 'p')}_logit_delta_{target}"] = adv.logit(sub_latent[:, j]) - adv.logit(sub_base[:, TARGETS.index(target)])
    return train_feat, sub_feat


def scan_latent_features(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub: pd.DataFrame,
    prefix: str,
    top_n: int = 50,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_rows = train_feat.sort_values(KEY).reset_index(drop=True)
    sub_rows = sub_feat.sort_values(KEY).reset_index(drop=True)
    y = train_rows[TARGETS].to_numpy(dtype=int)
    cols = broad.finite_numeric_cols(train_rows)
    pre = broad.prefilter(train_rows, base, cols, TARGETS, top_n=top_n)
    pre.to_csv(OUT / f"{prefix}_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = broad.loss_col(y[:, j], base[:, j])
        for c_value in C_GRID:
            corrected = broad.oof_corrected(train_rows, base, target, feature, mode, c_value)
            losses = [broad.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in WEIGHT_GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": broad.loss_col(y[:, j], corrected),
                "best_weight": float(WEIGHT_GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_rows, y, base, corrected, j))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.56)
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.00035 and row["mean_delta"] <= -0.00005 and row["win_rate"] >= 0.62)
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / f"{prefix}_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, name: str) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
        used = []
        for op in ops.itertuples(index=False):
            target = str(op.target)
            if target in {u["target"] for u in used}:
                continue
            j = TARGETS.index(target)
            corrected = broad.oof_corrected(train_rows, pred, target, str(op.feature), str(op.mode), float(op.c_value))
            pred[:, j] = adv.clip((1.0 - float(op.best_weight)) * pred[:, j] + float(op.best_weight) * corrected)
            sub_corr = broad.fit_corrected(train_rows, sub_rows, pred, sub_pred, target, str(op.feature), str(op.mode), float(op.c_value))
            sub_pred[:, j] = adv.clip((1.0 - float(op.best_weight)) * sub_pred[:, j] + float(op.best_weight) * sub_corr)
            used.append({"target": target, "feature": str(op.feature), "mode": str(op.mode), "c_value": float(op.c_value), "weight": float(op.best_weight), "delta_vs_base": float(op.delta_vs_base), "mean_delta": float(op.mean_delta), "win_rate": float(op.win_rate)})
        out = base_sub.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / name, index=False)
        used_cols = ["target", "feature", "mode", "c_value", "weight", "delta_vs_base", "mean_delta", "win_rate"]
        return pred, out, pd.DataFrame(used, columns=used_cols)

    safe_ops = result[(result["passes_strict"] | result["passes_loose"]) & (result["best_weight"] > 0)].copy()
    safe_ops = safe_ops.sort_values(["passes_strict", "delta_vs_base"], ascending=[False, True])
    pred_safe, _sub_safe, used_safe = apply_ops(safe_ops, f"submission_{prefix}.csv")
    used_safe.to_csv(OUT / f"{prefix}_selected_ops.csv", index=False)

    risky_ops = result[result["best_weight"] > 0].copy().sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    pred_risky, _sub_risky, used_risky = apply_ops(risky_ops, f"submission_{prefix}_risky_top.csv")
    used_risky.to_csv(OUT / f"{prefix}_risky_top_ops.csv", index=False)

    cv_rows = []
    for label, pred in [("safe", pred_safe), ("risky_top", pred_risky)]:
        for j, target in enumerate(TARGETS):
            cv_rows.append({"candidate": label, "target": target, "base_loss": broad.loss_col(y[:, j], base[:, j]), "candidate_loss": broad.loss_col(y[:, j], pred[:, j]), "delta_vs_base": broad.loss_col(y[:, j], pred[:, j]) - broad.loss_col(y[:, j], base[:, j])})
        cv_rows.append({"candidate": label, "target": "mean", "base_loss": adv.mean_loss(y, base), "candidate_loss": adv.mean_loss(y, pred), "delta_vs_base": adv.mean_loss(y, pred) - adv.mean_loss(y, base)})
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / f"{prefix}_cv_estimate.csv", index=False)
    np.save(OUT / f"{prefix}_safe_oof.npy", pred_safe)
    np.save(OUT / f"{prefix}_risky_top_oof.npy", pred_risky)
    return result, cv, used_safe


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, x, _base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    block_train, block_sub = build_latent_features(train, sub, rows, x, y, base, base_sub, "blockrate")
    q_train, q_sub = build_latent_features(train, sub, rows, x, y, base, base_sub, "qrank")
    train_feat = block_train.merge(q_train.drop(columns=SUB_KEY + TARGETS), left_index=True, right_index=True)
    sub_feat = block_sub.merge(q_sub.drop(columns=SUB_KEY), left_index=True, right_index=True)
    train_feat.to_parquet(OUT / "jepa_latent_residual_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / "jepa_latent_residual_submission_features.parquet", index=False)
    scan, cv, ops = scan_latent_features(train_feat, sub_feat, base, base_sub, "jepa_latent_residual_probe")

    summary = pd.DataFrame(
        [
            {
                "candidate": "submission_jepa_latent_residual_probe.csv",
                "oof_loss": float(cv[(cv["candidate"].eq("safe")) & (cv["target"].eq("mean"))]["candidate_loss"].iloc[0]),
                "oof_delta_vs_stage2": float(cv[(cv["candidate"].eq("safe")) & (cv["target"].eq("mean"))]["delta_vs_base"].iloc[0]),
                **adv.public_axis_for("submission_jepa_latent_residual_probe.csv"),
                "ops": int(len(ops)),
                "risk_class": "safe_selected",
            },
            {
                "candidate": "submission_jepa_latent_residual_probe_risky_top.csv",
                "oof_loss": float(cv[(cv["candidate"].eq("risky_top")) & (cv["target"].eq("mean"))]["candidate_loss"].iloc[0]),
                "oof_delta_vs_stage2": float(cv[(cv["candidate"].eq("risky_top")) & (cv["target"].eq("mean"))]["delta_vs_base"].iloc[0]),
                **adv.public_axis_for("submission_jepa_latent_residual_probe_risky_top.csv"),
                "ops": int(pd.read_csv(OUT / "jepa_latent_residual_probe_risky_top_ops.csv").shape[0]),
                "risk_class": "oof_top_guardrail_failed",
            },
        ]
    )
    summary.to_csv(OUT / "jepa_latent_residual_probe_candidate_summary.csv", index=False)
    report = [
        "# JEPA Latent Residual Probe",
        "",
        "BlockRate/Q-Rank direct blending was harmful, so this probe uses their predicted latent state as residual-correction features instead of replacing probabilities with the latent rates.",
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Safe Ops",
        "",
        ops.to_csv(index=False) if not ops.empty else "No operations passed the subject guardrail.",
        "",
        "## Top Risky Ops",
        "",
        pd.read_csv(OUT / "jepa_latent_residual_probe_risky_top_ops.csv").to_csv(index=False),
        "",
        "## CV Estimate",
        "",
        cv.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(30).to_csv(index=False),
    ]
    (OUT / "jepa_latent_residual_probe_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
