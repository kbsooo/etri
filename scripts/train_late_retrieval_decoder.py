"""v81 late-behavior retrieval decoder.

Goal: turn the v80 manual router + retrieval scaffold into a *real* decoder layer.
We keep the v80 routed prediction as the base and learn target-wise residual
decoders on top of it. Each decoder reads:

  - the v80 latent (z_*) geometry through fold-safe KNN retrieval summaries
    (global pool + a late-panel pool, since v80's signal lives in the late
    residual-behavior manifold),
  - a curated set of v80 source predictions (late residual-behavior + the v80
    routing winners) as input features,
  - panel position / early-mid-late basis,
  - the base prediction itself.

It then predicts the residual against the v80 base (not the raw label) with
small, robust models only (Ridge / HistGradientBoosting / ExtraTrees, plus one
LogisticRegression label decoder for contrast). Every retrieval summary for a
validation/sample row is computed using fold-train rows only, and self is
excluded by key, so there is no label leakage.

Fold safety note: we reuse `make_subject_time_folds` from
`train_s2_sleep_retrieval_encoder`, the exact helper the v80 encoder used with
`n_folds=5`. With the same train ordering this produces the identical fold
partition, so the imported v80 source OOF predictions stay fold-safe when used
as decoder input features.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler

from train_s2_sleep_retrieval_encoder import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    load_base_predictions,
    make_subject_time_folds,
    normalize_keys,
    safe_logit,
    sigmoid,
)

# v80 routing winners + late residual-behavior family. Used as decoder input
# features (their per-target OOF predictions), not as the prediction itself.
DEFAULT_SOURCE_FEATURES = [
    "joint_panel_neural_residual_knn_resid",
    "joint_cross_family_late_residual_behavior_neural_metric_knn_resid",
    "joint_family_late_residual_behavior_neural_metric_knn_logitresid",
    "joint_target_late_residual_behavior_neural_metric_knn_logitresid",
    "joint_s23_late_residual_behavior_neural_knn_resid",
    "joint_late_residual_behavior_neural_knn_resid",
    "joint_neural_multiview_q_residual_knn_resid",
    "joint_residual_behavior_neural_knn_resid",
]

REGRESSOR_MODELS = ("ridge", "hgb", "extratrees")
LABEL_MODELS = ("logreg",)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Panel position per row, identical convention to the routing script."""
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    ordered = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["panel_index"] = ordered.groupby("subject_id").cumcount().astype(float)
    denom = ordered.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    ordered["panel_position"] = ordered["panel_index"] / denom
    train_pos = ordered[ordered["_split"].eq("train")].sort_values("_row")["panel_position"].to_numpy(float)
    sample_pos = ordered[ordered["_split"].eq("sample")].sort_values("_row")["panel_position"].to_numpy(float)
    return train_pos, sample_pos


def panel_basis(pos: np.ndarray) -> np.ndarray:
    """[panel_position, early, mid, late] — soft time-of-panel basis."""
    early = (pos < 0.333).astype(float)
    mid = ((pos >= 0.333) & (pos < 0.666)).astype(float)
    late = (pos >= 0.666).astype(float)
    return np.column_stack([pos, early, mid, late])


def key_codes(keys: pd.DataFrame) -> np.ndarray:
    """Stable per-row identity (subject + sleep_date) for self-exclusion."""
    return (keys["subject_id"].astype(str) + "|" + keys["sleep_date"].astype(str)).to_numpy()


def residual_target(y: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    """logit_hard residual: pull base toward a smoothed hard label in logit space."""
    smooth = 0.04 + 0.92 * y.astype(float)
    return safe_logit(smooth) - safe_logit(anchor)


def retrieval_block(
    ref_z: np.ndarray,
    query_z: np.ndarray,
    ref_y: np.ndarray,
    ref_base: np.ndarray,
    query_base: np.ndarray,
    ref_codes: np.ndarray,
    query_codes: np.ndarray,
    ref_subjects: np.ndarray,
    query_subjects: np.ndarray,
    ref_dates: np.ndarray,
    query_dates: np.ndarray,
    k: int,
    temp: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Fold-safe KNN retrieval summaries over the latent space.

    Mirrors the encoder's `neighbor_context_features` weighting (distance softmax
    plus same-subject/recency context), but returns two readable blocks:
      geometry  (n_query, 8)  — pool-shape features, target-agnostic
      per_target(n_query, 7*7) — label/residual summaries for each target

    Self is excluded by key, so a row never sees its own label even when the
    reference pool contains it.
    """
    if ref_z.shape[0] == 0:
        geo = np.zeros((query_z.shape[0], 8), dtype=float)
        per = np.zeros((query_z.shape[0], len(TARGET_COLUMNS) * 7), dtype=float)
        return geo, per

    ref_z = np.clip(np.nan_to_num(ref_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    query_z = np.clip(np.nan_to_num(query_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    d2 = ((query_z[:, None, :] - ref_z[None, :, :]) ** 2).mean(axis=2)
    # self-exclusion by identity: never retrieve the same subject-day
    same_identity = query_codes[:, None] == ref_codes[None, :]
    d2 = np.where(same_identity, np.inf, d2)

    kk = min(k, max(1, ref_z.shape[0] - 1))
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)
    # finite-guard: if a row had fewer than kk valid neighbors, inf creeps in
    chosen = np.where(np.isfinite(chosen), chosen, np.nanmax(np.where(np.isfinite(chosen), chosen, np.nan)) + 1.0)

    same_subject = (query_subjects[:, None] == ref_subjects[idx]).astype(float)
    day_delta = np.abs((query_dates[:, None] - ref_dates[idx]).astype("timedelta64[D]").astype(float))
    recency = np.exp(-np.clip(day_delta, 0.0, 365.0) / 21.0)

    scale = np.maximum(np.nanmedian(chosen, axis=1, keepdims=True), 1e-6) * temp
    distance_weight = np.exp(-chosen / scale)
    distance_weight = distance_weight / np.maximum(distance_weight.sum(axis=1, keepdims=True), 1e-12)

    context_score = -chosen / scale + 0.65 * same_subject + 0.35 * recency
    context_score = context_score - np.max(context_score, axis=1, keepdims=True)
    context_weight = np.exp(np.clip(context_score, -50.0, 50.0))
    context_weight = context_weight / np.maximum(context_weight.sum(axis=1, keepdims=True), 1e-12)

    same_mass = (context_weight * same_subject).sum(axis=1)
    recent_mass = (context_weight * recency).sum(axis=1)
    close_same_mass = (context_weight * same_subject * (day_delta <= 14.0)).sum(axis=1)
    far_cross_mass = (context_weight * (1.0 - same_subject) * (day_delta > 28.0)).sum(axis=1)
    day_mean = (context_weight * np.clip(day_delta, 0.0, 365.0)).sum(axis=1)
    eff_n = 1.0 / np.maximum((context_weight ** 2).sum(axis=1), 1e-12)
    geometry = np.column_stack(
        [
            np.nanmin(chosen, axis=1),
            np.nanmean(chosen, axis=1),
            np.nanstd(chosen, axis=1),
            same_mass,
            recent_mass,
            close_same_mass,
            far_cross_mass,
            day_mean,
        ]
    )
    # eff_n folded into geometry's last slot via day_mean? keep 8 cols stable; expose eff_n in per-target? -> append
    geometry = np.column_stack([geometry[:, :7], eff_n])

    per_target_cols = []
    for t in range(len(TARGET_COLUMNS)):
        y_t = ref_y[:, t]
        base_t = ref_base[:, t]
        residual = y_t - base_t
        y_smooth = y_t * 0.98 + 0.01
        logit_residual = safe_logit(y_smooth) - safe_logit(base_t)

        def weighted(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
            return (weights * values[idx]).sum(axis=1)

        label_ctx = weighted(y_t, context_weight)
        resid_dist = weighted(residual, distance_weight)
        resid_ctx = weighted(residual, context_weight)
        logit_ctx = weighted(logit_residual, context_weight)
        # context-weighted residual spread (uncertainty of the neighborhood)
        resid_mean_grid = resid_ctx[:, None]
        resid_var = (context_weight * (residual[idx] - resid_mean_grid) ** 2).sum(axis=1)
        resid_std = np.sqrt(np.maximum(resid_var, 0.0))
        # the corrected prediction this neighborhood implies
        ctx_pred = np.clip(query_base[:, t] + resid_ctx, EPS, 1.0 - EPS)
        per_target_cols.extend([label_ctx, resid_dist, resid_ctx, logit_ctx, resid_std, ctx_pred, weighted(y_t, distance_weight)])

    per_target = np.column_stack(per_target_cols)
    return np.nan_to_num(geometry, nan=0.0), np.nan_to_num(per_target, nan=0.0)


def per_target_slice(per_target: np.ndarray, t: int) -> np.ndarray:
    """The 7-feature block for target t out of the per_target matrix."""
    width = 7
    return per_target[:, t * width : (t + 1) * width]


def build_target_features(
    t: int,
    panel: np.ndarray,
    base: np.ndarray,
    source_feats: np.ndarray,
    geo_global: np.ndarray,
    per_global: np.ndarray,
    geo_late: np.ndarray,
    per_late: np.ndarray,
) -> np.ndarray:
    """Assemble the decoder input matrix for one target."""
    base_t = base[:, t]
    block = [
        panel,
        source_feats,  # already per-target logit residuals (see prepare_source_features)
        base_t[:, None],
        safe_logit(np.clip(base_t, EPS, 1.0 - EPS))[:, None],
        geo_global,
        per_target_slice(per_global, t),
        geo_late,
        per_target_slice(per_late, t),
    ]
    return np.nan_to_num(np.column_stack(block), nan=0.0, posinf=0.0, neginf=0.0).astype(np.float64)


def load_source_features(source_dir: Path, names: list[str], train: pd.DataFrame, sample: pd.DataFrame) -> dict[str, np.ndarray]:
    """Load curated v80 source OOF/submission predictions as logit-residual features.

    Returns per-target arrays: train_logit[name] shape (n_train, 7), sample_logit[name].
    These are fold-safe because the v80 encoder used the same fold partition.
    """
    feats: dict[str, np.ndarray] = {}
    for name in names:
        oof_path = source_dir / f"oof_{name}.csv"
        sub_path = source_dir / f"submission_{name}.csv"
        if not oof_path.exists() or not sub_path.exists():
            print(f"  [skip missing source] {name}")
            continue
        oof = normalize_keys(pd.read_csv(oof_path))
        sub = normalize_keys(pd.read_csv(sub_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]) or not sub[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"Source key mismatch: {name}")
        oof_mat = np.clip(np.column_stack([oof[f"pred_{tt}"].to_numpy(float) for tt in TARGET_COLUMNS]), EPS, 1 - EPS)
        sub_mat = np.clip(sub[TARGET_COLUMNS].to_numpy(float), EPS, 1 - EPS)
        feats[f"{name}::train"] = oof_mat
        feats[f"{name}::sample"] = sub_mat
    return feats


def stack_source_features(
    feats: dict[str, np.ndarray],
    names: list[str],
    split: str,
    t: int,
    base_logit: np.ndarray,
    rows: np.ndarray | None = None,
) -> np.ndarray:
    """Per-target logit-residual of each available source vs base, for target t.

    `rows` selects which source rows to use (e.g. fit_idx / val_idx for the
    train split); None means use all rows (sample split).
    """
    cols = []
    for name in names:
        key = f"{name}::{split}"
        if key not in feats:
            continue
        col = feats[key][:, t] if rows is None else feats[key][rows, t]
        cols.append((safe_logit(col) - base_logit).astype(float))
    if not cols:
        return np.zeros((len(base_logit), 0), dtype=float)
    return np.column_stack(cols)


def average_log_loss(y_true: np.ndarray, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    per = {t: float(log_loss(y_true[:, i], pred[:, i], labels=[0, 1])) for i, t in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per.values()))), per


def make_regressor(model: str, seed: int):
    if model == "ridge":
        return Ridge(alpha=6.0, solver="svd")
    if model == "hgb":
        return HistGradientBoostingRegressor(
            max_depth=3, max_iter=220, learning_rate=0.045, l2_regularization=1.0,
            min_samples_leaf=25, max_leaf_nodes=15, random_state=seed,
        )
    if model == "extratrees":
        return ExtraTreesRegressor(
            n_estimators=400, max_depth=7, min_samples_leaf=12, max_features=0.6,
            n_jobs=-1, random_state=seed,
        )
    raise ValueError(model)


def build(args: argparse.Namespace) -> None:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    latents_train = normalize_keys(pd.read_parquet(args.latents_train))
    latents_sample = normalize_keys(pd.read_parquet(args.latents_sample))
    if not latents_train[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Latent train keys do not match train")
    if not latents_sample[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Latent sample keys do not match sample")

    base_train, base_sample = load_base_predictions(train, sample, Path(args.base_oof), Path(args.base_submission))
    base_logit_train = safe_logit(base_train)
    base_logit_sample = safe_logit(base_sample)

    z_cols = sorted(c for c in latents_train.columns if c.startswith("z_"))
    z_train = latents_train[z_cols].to_numpy(float)
    z_sample = latents_sample[z_cols].to_numpy(float)
    # standardize latent geometry on full train (geometry only, leakage-free)
    z_mean = z_train.mean(axis=0, keepdims=True)
    z_std = z_train.std(axis=0, keepdims=True) + 1e-6
    z_train = (z_train - z_mean) / z_std
    z_sample = (z_sample - z_mean) / z_std

    train_pos, sample_pos = add_panel_position(train, sample)
    panel_train = panel_basis(train_pos)
    panel_sample = panel_basis(sample_pos)

    source_names = [s.strip() for s in args.source_features.split(",") if s.strip()]
    source_dir = Path(args.source_dir)
    source_feats = load_source_features(source_dir, source_names, train, sample)
    available_sources = sorted({k.split("::")[0] for k in source_feats})
    print(f"source feature count: {len(available_sources)} / {len(source_names)} requested")

    y_train = train[TARGET_COLUMNS].to_numpy(int)
    train_codes = key_codes(train)
    sample_codes = key_codes(sample)
    train_subjects = train["subject_id"].astype(str).to_numpy()
    sample_subjects = sample["subject_id"].astype(str).to_numpy()
    train_dates = pd.to_datetime(train["lifelog_date"]).to_numpy(dtype="datetime64[D]")
    sample_dates = pd.to_datetime(sample["lifelog_date"]).to_numpy(dtype="datetime64[D]")

    n_train = len(train)
    n_sample = len(sample)
    folds = make_subject_time_folds(train, args.folds)

    all_models = list(REGRESSOR_MODELS) + list(LABEL_MODELS)
    oof_pred = {m: base_train.copy() for m in all_models}
    sample_delta_accum = {m: np.zeros((n_sample, len(TARGET_COLUMNS))) for m in REGRESSOR_MODELS}
    sample_proba_accum = {m: np.zeros((n_sample, len(TARGET_COLUMNS))) for m in LABEL_MODELS}

    late_thr = args.late_threshold

    def retrieval_for(query_z, query_base, query_codes_, query_subjects_, query_dates_, ref_sel):
        ref_idx = ref_sel
        geo_g, per_g = retrieval_block(
            z_train[ref_idx], query_z, y_train[ref_idx].astype(float), base_train[ref_idx], query_base,
            train_codes[ref_idx], query_codes_, train_subjects[ref_idx], query_subjects_,
            train_dates[ref_idx], query_dates_, args.knn_k, args.knn_temp,
        )
        late_ref = ref_idx[train_pos[ref_idx] >= late_thr]
        geo_l, per_l = retrieval_block(
            z_train[late_ref], query_z, y_train[late_ref].astype(float), base_train[late_ref], query_base,
            train_codes[late_ref], query_codes_, train_subjects[late_ref], query_subjects_,
            train_dates[late_ref], query_dates_, max(8, args.knn_k - 4), args.knn_temp,
        )
        return geo_g, per_g, geo_l, per_l

    for fold_i, pack in enumerate(folds, start=1):
        fit_idx = pack.train_idx
        val_idx = pack.val_idx

        geo_g_fit, per_g_fit, geo_l_fit, per_l_fit = retrieval_for(
            z_train[fit_idx], base_train[fit_idx], train_codes[fit_idx], train_subjects[fit_idx], train_dates[fit_idx], fit_idx
        )
        geo_g_val, per_g_val, geo_l_val, per_l_val = retrieval_for(
            z_train[val_idx], base_train[val_idx], train_codes[val_idx], train_subjects[val_idx], train_dates[val_idx], fit_idx
        )
        geo_g_smp, per_g_smp, geo_l_smp, per_l_smp = retrieval_for(
            z_sample, base_sample, sample_codes, sample_subjects, sample_dates, fit_idx
        )

        for t in range(len(TARGET_COLUMNS)):
            sf_fit = stack_source_features(source_feats, available_sources, "train", t, base_logit_train[fit_idx, t], rows=fit_idx)
            sf_val = stack_source_features(source_feats, available_sources, "train", t, base_logit_train[val_idx, t], rows=val_idx)
            sf_smp = stack_source_features(source_feats, available_sources, "sample", t, base_logit_sample[:, t], rows=None)

            x_fit = build_target_features(t, panel_train[fit_idx], base_train[fit_idx], sf_fit, geo_g_fit, per_g_fit, geo_l_fit, per_l_fit)
            x_val = build_target_features(t, panel_train[val_idx], base_train[val_idx], sf_val, geo_g_val, per_g_val, geo_l_val, per_l_val)
            x_smp = build_target_features(t, panel_sample, base_sample, sf_smp, geo_g_smp, per_g_smp, geo_l_smp, per_l_smp)

            resid_fit = residual_target(y_train[fit_idx, t], base_train[fit_idx, t])

            # linear models need scaling; trees do not
            imputer = SimpleImputer(strategy="median", keep_empty_features=True)
            scaler = StandardScaler()
            x_fit_s = scaler.fit_transform(imputer.fit_transform(x_fit))
            x_val_s = scaler.transform(imputer.transform(x_val))
            x_smp_s = scaler.transform(imputer.transform(x_smp))

            for model in REGRESSOR_MODELS:
                est = make_regressor(model, args.seed + t)
                if model == "ridge":
                    est.fit(x_fit_s, resid_fit)
                    d_val = est.predict(x_val_s)
                    d_smp = est.predict(x_smp_s)
                else:
                    est.fit(x_fit, resid_fit)
                    d_val = est.predict(x_val)
                    d_smp = est.predict(x_smp)
                d_val = np.clip(d_val, -args.max_delta, args.max_delta)
                d_smp = np.clip(d_smp, -args.max_delta, args.max_delta)
                oof_pred[model][val_idx, t] = sigmoid(base_logit_train[val_idx, t] + d_val)
                sample_delta_accum[model][:, t] += d_smp

            # contrast: a label-classifier decoder over the same features
            est = LogisticRegression(C=0.5, max_iter=4000)
            if len(np.unique(y_train[fit_idx, t])) < 2:
                p_val = np.full(len(val_idx), float(y_train[fit_idx, t].mean()))
                p_smp = np.full(n_sample, float(y_train[fit_idx, t].mean()))
            else:
                est.fit(x_fit_s, y_train[fit_idx, t])
                p_val = est.predict_proba(x_val_s)[:, 1]
                p_smp = est.predict_proba(x_smp_s)[:, 1]
            oof_pred["logreg"][val_idx, t] = np.clip(p_val, EPS, 1 - EPS)
            sample_proba_accum["logreg"][:, t] += p_smp
        print(f"fold {fold_i}/{len(folds)} done")

    # assemble sample predictions
    sample_pred = {}
    for model in REGRESSOR_MODELS:
        mean_delta = sample_delta_accum[model] / len(folds)
        sample_pred[model] = np.clip(sigmoid(base_logit_sample + mean_delta), EPS, 1 - EPS)
    sample_pred["logreg"] = np.clip(sample_proba_accum["logreg"] / len(folds), EPS, 1 - EPS)

    # score + write source outputs
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_score, base_per = average_log_loss(y_train, base_train)
    rows = [{"name": "v80_base", "avg_log_loss": base_score, **base_per}]
    written = []
    for model in all_models:
        score, per = average_log_loss(y_train, oof_pred[model])
        rows.append({"name": f"v81_late_retrieval_{model}", "avg_log_loss": score, **per})
        oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
        sub_df = sample[KEY_COLUMNS].copy()
        for i, tt in enumerate(TARGET_COLUMNS):
            oof_df[f"pred_{tt}"] = oof_pred[model][:, i]
            sub_df[tt] = sample_pred[model][:, i]
        oof_name = f"oof_v81_late_retrieval_{model}.csv"
        sub_name = f"submission_v81_late_retrieval_{model}.csv"
        oof_df.to_csv(output_dir / oof_name, index=False)
        sub_df.to_csv(output_dir / sub_name, index=False)
        written.append({"model": model, "source": f"v81_late_retrieval_{model}", "oof": oof_name, "submission": sub_name})

    score_df = pd.DataFrame(rows)
    score_df.to_csv(output_dir / "score.csv", index=False)

    report = {
        "base_score": {"avg_log_loss": base_score, "per_target": base_per},
        "models": {
            r["name"]: {"avg_log_loss": r["avg_log_loss"], "per_target": {t: r[t] for t in TARGET_COLUMNS}}
            for r in rows
            if r["name"] != "v80_base"
        },
        "source_features_used": available_sources,
        "fold_safety": "make_subject_time_folds reused from train_s2_sleep_retrieval_encoder (n_folds=5) — identical partition to the v80 encoder; self excluded by key in retrieval.",
        "outputs": written,
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    def md_table(df: pd.DataFrame) -> str:
        cols = list(df.columns)
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
        for _, r in df.iterrows():
            lines.append("| " + " | ".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in r) + " |")
        return "\n".join(lines)

    lines = [
        "# v81 late-behavior retrieval decoder",
        "",
        f"- Base (v80) OOF: `{base_score:.6f}`",
        f"- Source features used ({len(available_sources)}): {', '.join(available_sources)}",
        "- Decoder: target-wise residual on the v80 base. Regressors predict the residual; logreg is a label-classifier contrast.",
        "- Fold-safe: retrieval summaries computed from fold-train only, self excluded by key; folds match the v80 encoder partition.",
        "",
        "## Standalone source scores (vs v80 base)",
        "",
        md_table(score_df),
        "",
        "Note: standalone scores start from the base and apply the full (weight=1) residual. The router applies a fractional, target/bin-local weight, so the routed gain is what matters — see the conditional_latent_routing_v81 reports.",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"base={base_score:.6f}")
    for r in rows[1:]:
        print(f"  {r['name']}={r['avg_log_loss']:.6f}")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="v81 late-behavior retrieval decoder over the v80 base.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--source-dir", default="outputs/joint_state_space_encoder_v80_late_behavior_on_v79")
    parser.add_argument("--latents-train", default="outputs/joint_state_space_encoder_v80_late_behavior_on_v79/joint_state_space_latents_train.parquet")
    parser.add_argument("--latents-sample", default="outputs/joint_state_space_encoder_v80_late_behavior_on_v79/joint_state_space_latents_sample.parquet")
    parser.add_argument("--base-oof", default="outputs/conditional_latent_routing_v80_late_behavior_on_v79/oof_conditional_latent_routing.csv")
    parser.add_argument("--base-submission", default="outputs/conditional_latent_routing_v80_late_behavior_on_v79/submission_conditional_latent_routing.csv")
    parser.add_argument("--source-features", default=",".join(DEFAULT_SOURCE_FEATURES))
    parser.add_argument("--output-dir", default="outputs/decoder_v81_late_retrieval_on_v80")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--knn-k", type=int, default=19)
    parser.add_argument("--knn-temp", type=float, default=1.2)
    parser.add_argument("--late-threshold", type=float, default=0.5)
    parser.add_argument("--max-delta", type=float, default=2.5)
    parser.add_argument("--seed", type=int, default=17)
    return parser.parse_args()


def main() -> None:
    build(parse_args())


if __name__ == "__main__":
    main()
