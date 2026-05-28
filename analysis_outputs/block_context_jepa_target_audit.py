from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import block_level_regressor_experiments as blr  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
EPS = 1e-5


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p.astype(float), EPS, 1.0 - EPS)


def mean_logloss(y: np.ndarray, pred: np.ndarray) -> float:
    pred = clip(pred)
    return float(
        np.mean([log_loss(y[:, j], pred[:, j], labels=[0, 1]) for j in range(y.shape[1])])
    )


def per_target_logloss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    pred = clip(pred)
    return {
        target: float(log_loss(y[:, j], pred[:, j], labels=[0, 1]))
        for j, target in enumerate(TARGETS)
    }


def weighted_rate_logloss(rate: np.ndarray, pred: np.ndarray, weight: np.ndarray) -> float:
    p = clip(pred)
    loss = -(rate * np.log(p) + (1.0 - rate) * np.log(1.0 - p))
    w = np.asarray(weight, dtype=float).reshape(-1, 1)
    return float(np.sum(loss * w) / (np.sum(w) * loss.shape[1]))


def weighted_mae(rate: np.ndarray, pred: np.ndarray, weight: np.ndarray) -> float:
    loss = np.abs(rate - pred)
    w = np.asarray(weight, dtype=float).reshape(-1, 1)
    return float(np.sum(loss * w) / (np.sum(w) * loss.shape[1]))


def weighted_r2(rate: np.ndarray, pred: np.ndarray, weight: np.ndarray) -> float:
    vals = []
    for j in range(rate.shape[1]):
        y = rate[:, j]
        p = pred[:, j]
        mu = np.average(y, weights=weight)
        denom = np.sum(weight * (y - mu) ** 2)
        if denom <= 1e-12:
            continue
        vals.append(1.0 - float(np.sum(weight * (y - p) ** 2) / denom))
    return float(np.mean(vals)) if vals else float("nan")


def parse_subject_id(sid: object) -> int:
    return int(str(sid).replace("id", ""))


def make_model(k: int, alpha: float, n_features: int) -> Pipeline:
    return Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("select", SelectKBest(score_func=f_regression, k=min(k, max(1, n_features)))),
            ("ridge", Ridge(alpha=alpha)),
        ]
    )


def feature_views(samples: pd.DataFrame) -> dict[str, list[str]]:
    all_cols = blr.feature_columns(samples)
    structural_prefixes = (
        "sid__",
        "subject_id_code",
        "n_rows",
        "span_days",
        "coverage_density",
        "start_dow",
        "end_dow",
        "start_month",
        "mid_subject_frac",
        "start_subject_day",
        "end_subject_day",
        "has_prev",
        "has_next",
        "prev_gap",
        "next_gap",
    )
    sensor_value_prefixes = ("m__", "s__", "d__")
    sensor_missing_prefixes = ("na__",)
    label_context_tokens = (
        "subj_prior__",
        "base_mean__",
        "base_std__",
        "base_delta__",
        "prev_edge__",
        "next_edge__",
        "edge_same__",
        "edge_mean__",
        "prev_w",
        "next_w",
        "around_w",
    )

    def starts(col: str, prefixes: tuple[str, ...]) -> bool:
        return any(col.startswith(prefix) for prefix in prefixes)

    structure = [col for col in all_cols if starts(col, structural_prefixes)]
    label_context = structure + [
        col
        for col in all_cols
        if col not in structure and any(token in col for token in label_context_tokens)
    ]
    sensor_values = structure + [col for col in all_cols if starts(col, sensor_value_prefixes)]
    missingness = structure + [col for col in all_cols if starts(col, sensor_missing_prefixes)]
    combined = all_cols
    return {
        "label_context_ridge": sorted(set(label_context), key=label_context.index),
        "sensor_values_ridge": sorted(set(sensor_values), key=sensor_values.index),
        "missingness_ridge": sorted(set(missingness), key=missingness.index),
        "combined_ridge": combined,
    }


def fit_predict_view(
    samples: pd.DataFrame,
    pred_features: pd.DataFrame,
    cols: list[str],
    k: int,
    alpha: float,
) -> np.ndarray:
    if not cols:
        raise ValueError("empty feature view")
    X = samples[cols].replace([np.inf, -np.inf], np.nan)
    Xp = pred_features[cols].replace([np.inf, -np.inf], np.nan)
    pred = np.zeros((len(pred_features), len(TARGETS)), dtype=float)
    for j, target in enumerate(TARGETS):
        model = make_model(k=k, alpha=alpha, n_features=len(cols))
        y = samples[f"rate__{target}"].to_numpy(dtype=float)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ConvergenceWarning)
            warnings.simplefilter("ignore", category=UserWarning)
            model.fit(X, y)
        pred[:, j] = model.predict(Xp)
    return clip(pred)


def matrix_geometry(pred: np.ndarray, true_rate: np.ndarray, weight: np.ndarray) -> dict[str, float]:
    z = pred.astype(float).copy()
    z -= np.nanmean(z, axis=0, keepdims=True)
    scale = np.nanstd(z, axis=0, keepdims=True)
    scale[scale < 1e-8] = 1.0
    z /= scale
    z = np.nan_to_num(z)

    cov = (z.T @ z) / max(len(z) - 1, 1)
    eig = np.clip(np.linalg.eigvalsh(cov), 0.0, None)
    eig_sum = float(eig.sum())
    if eig_sum <= 1e-12:
        anisotropy = float("nan")
        effective_rank = float("nan")
    else:
        probs = eig / eig_sum
        anisotropy = float(eig.max() / eig_sum)
        effective_rank = float(np.exp(-(probs[probs > 0] * np.log(probs[probs > 0])).sum()))

    rng = np.random.default_rng(47)
    dirs = rng.normal(size=(pred.shape[1], 64))
    dirs /= np.linalg.norm(dirs, axis=0, keepdims=True)
    proj = z @ dirs
    proj_std = proj.std(axis=0)
    centered = proj - proj.mean(axis=0, keepdims=True)
    denom = np.maximum(proj_std, 1e-8)
    proj_skew = np.mean((centered / denom) ** 3, axis=0)
    proj_kurt = np.mean((centered / denom) ** 4, axis=0) - 3.0

    if len(z) > 1:
        dist = ((z[:, None, :] - z[None, :, :]) ** 2).sum(axis=2)
        np.fill_diagonal(dist, np.inf)
        nn = dist.argmin(axis=1)
        nn_true_mae = float(np.average(np.abs(true_rate - true_rate[nn]).mean(axis=1), weights=weight))
    else:
        nn_true_mae = float("nan")

    return {
        "anisotropy": anisotropy,
        "effective_rank": effective_rank,
        "projection_std_mean": float(np.mean(proj_std)),
        "projection_std_min": float(np.min(proj_std)),
        "projection_skew_abs_mean": float(np.mean(np.abs(proj_skew))),
        "projection_kurt_abs_mean": float(np.mean(np.abs(proj_kurt))),
        "nn_true_rate_mae": nn_true_mae,
    }


def block_energy(true_rate: np.ndarray, pred: np.ndarray) -> np.ndarray:
    p = clip(pred)
    return -(true_rate * np.log(p) + (1.0 - true_rate) * np.log(1.0 - p)).mean(axis=1)


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    train = pd.read_parquet(OUT / "train_deep_features.parquet").copy()
    train["lifelog_date"] = pd.to_datetime(train["lifelog_date"])
    sensor_cols = blr.sensor_feature_cols(train)
    y_all = train[TARGETS].to_numpy(dtype=int)

    pred_rows: dict[str, np.ndarray] = {}
    block_records: list[dict[str, float | int | str]] = []
    block_pred_store: dict[str, list[np.ndarray]] = {
        "label_context_ridge": [],
        "sensor_values_ridge": [],
        "missingness_ridge": [],
        "combined_ridge": [],
    }
    block_true_store: list[np.ndarray] = []
    block_weight_store: list[np.ndarray] = []

    base_oof = np.zeros_like(y_all, dtype=float)
    view_names: list[str] | None = None
    n_features_by_view: dict[str, int] = {}

    folds = list(d.make_folds(train, "subject_blocks"))
    for outer_fold, (tr_idx, val_idx) in enumerate(folds):
        ref = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        samples = blr.make_training_blocks(ref, sensor_cols)
        pred_features, block_locs, base_val = blr.block_features(ref, val, sensor_cols)
        rates = blr.target_rates(val, block_locs)

        views = feature_views(samples)
        if view_names is None:
            view_names = list(views)
            n_features_by_view = {name: len(cols) for name, cols in views.items()}
            for name in view_names:
                pred_rows[name] = np.zeros_like(y_all, dtype=float)
        else:
            assert view_names == list(views)

        base_oof[val_idx] = base_val
        true_rate = rates[[f"rate__{t}" for t in TARGETS]].to_numpy(dtype=float)
        block_weight = rates["n_rows"].to_numpy(dtype=float)
        block_true_store.append(true_rate)
        block_weight_store.append(block_weight)

        fold_predictions: dict[str, np.ndarray] = {}
        for name, cols in views.items():
            k = 60 if name in {"label_context_ridge", "missingness_ridge"} else 120
            alpha = 80.0 if name != "combined_ridge" else 120.0
            block_pred = fit_predict_view(samples, pred_features, cols, k=k, alpha=alpha)
            fold_predictions[name] = block_pred
            block_pred_store[name].append(block_pred)
            for bid, locs in block_locs.items():
                pred_rows[name][val_idx[locs]] = block_pred[int(bid)]

        for bid, locs in block_locs.items():
            rows = val.iloc[locs]
            rec: dict[str, float | int | str] = {
                "outer_fold": outer_fold,
                "block_id": int(bid),
                "subject_id": str(rows["subject_id"].iloc[0]),
                "subject_id_code": parse_subject_id(rows["subject_id"].iloc[0]),
                "n_rows": int(len(rows)),
                "start_date": str(rows["lifelog_date"].min().date()),
                "end_date": str(rows["lifelog_date"].max().date()),
                "has_prev": float(pred_features.loc[bid, "has_prev"]),
                "has_next": float(pred_features.loc[bid, "has_next"]),
            }
            for j, target in enumerate(TARGETS):
                rec[f"true__{target}"] = float(true_rate[int(bid), j])
                rec[f"base__{target}"] = float(base_val[locs, j].mean())
                for name in views:
                    rec[f"pred__{name}__{target}"] = float(fold_predictions[name][int(bid), j])
            block_records.append(rec)

    assert view_names is not None
    block_df = pd.DataFrame(block_records)
    true_block = np.vstack(block_true_store)
    block_weight_all = np.concatenate(block_weight_store)
    base_block = block_df[[f"base__{t}" for t in TARGETS]].to_numpy(dtype=float)
    y = y_all
    temporal_row_loss = mean_logloss(y, base_oof)

    oracle_path = OUT / "block_state_bottleneck_summary.csv"
    oracle_df = pd.read_csv(oracle_path)
    if "metric" in oracle_df.columns:
        oracle = oracle_df.set_index("metric")["value"].to_dict()
        block_oracle_loss = float(oracle.get("validation_block_rate_oracle_logloss", 0.517877556))
    else:
        oracle = oracle_df.set_index("claim")["value"].to_dict()
        block_oracle_loss = float(oracle.get("block_rate_oracle_reaches_0p5_range", 0.517877556))
    oracle_gap = temporal_row_loss - block_oracle_loss

    summary_rows = [
        {
            "view": "temporal_base",
            "n_features": 0,
            "block_weighted_logloss": weighted_rate_logloss(true_block, base_block, block_weight_all),
            "block_rate_mae": weighted_mae(true_block, base_block, block_weight_all),
            "block_rate_r2": weighted_r2(true_block, base_block, block_weight_all),
            "row_direct_logloss": temporal_row_loss,
            "row_blend025_logloss": temporal_row_loss,
            "row_blend050_logloss": temporal_row_loss,
            "delta_direct_vs_temporal": 0.0,
            "delta_blend025_vs_temporal": 0.0,
            "oracle_gap_recovered_blend025": 0.0,
        }
    ]
    target_rows: list[dict[str, float | str]] = []
    geometry_rows: list[dict[str, float | str | int]] = []
    base_target_losses = per_target_logloss(y, base_oof)

    for j, target in enumerate(TARGETS):
        rate = true_block[:, [j]]
        pred = base_block[:, [j]]
        target_rows.append(
            {
                "view": "temporal_base",
                "target": target,
                "block_weighted_logloss": weighted_rate_logloss(rate, pred, block_weight_all),
                "block_rate_mae": weighted_mae(rate, pred, block_weight_all),
                "block_rate_r2": weighted_r2(rate, pred, block_weight_all),
                "row_direct_logloss": base_target_losses[target],
                "row_blend025_logloss": base_target_losses[target],
                "delta_blend025_vs_temporal": 0.0,
            }
        )

    for name in view_names:
        pred_block = np.vstack(block_pred_store[name])
        pred_direct = pred_rows[name]
        pred_blend025 = clip(0.75 * base_oof + 0.25 * pred_direct)
        pred_blend050 = clip(0.50 * base_oof + 0.50 * pred_direct)
        direct_loss = mean_logloss(y, pred_direct)
        blend025_loss = mean_logloss(y, pred_blend025)
        blend050_loss = mean_logloss(y, pred_blend050)
        summary_rows.append(
            {
                "view": name,
                "n_features": n_features_by_view[name],
                "block_weighted_logloss": weighted_rate_logloss(true_block, pred_block, block_weight_all),
                "block_rate_mae": weighted_mae(true_block, pred_block, block_weight_all),
                "block_rate_r2": weighted_r2(true_block, pred_block, block_weight_all),
                "row_direct_logloss": direct_loss,
                "row_blend025_logloss": blend025_loss,
                "row_blend050_logloss": blend050_loss,
                "delta_direct_vs_temporal": direct_loss - temporal_row_loss,
                "delta_blend025_vs_temporal": blend025_loss - temporal_row_loss,
                "oracle_gap_recovered_blend025": (
                    (temporal_row_loss - blend025_loss) / oracle_gap if oracle_gap > 0 else float("nan")
                ),
            }
        )

        geom = matrix_geometry(pred_block, true_block, block_weight_all)
        energy = block_energy(true_block, pred_block)
        top_count = max(1, int(math.ceil(len(energy) * 0.20)))
        top_idx = np.argsort(energy)[-top_count:]
        geom.update(
            {
                "view": name,
                "block_weighted_logloss": weighted_rate_logloss(true_block, pred_block, block_weight_all),
                "energy_mean": float(np.average(energy, weights=block_weight_all)),
                "energy_p90": float(np.quantile(energy, 0.90)),
                "top20_block_energy_share": float(
                    np.sum(energy[top_idx] * block_weight_all[top_idx])
                    / np.sum(energy * block_weight_all)
                ),
                "corr_with_block_size": float(np.corrcoef(energy, block_weight_all)[0, 1])
                if len(np.unique(block_weight_all)) > 1
                else float("nan"),
            }
        )
        geometry_rows.append(geom)

        direct_target = per_target_logloss(y, pred_direct)
        blend_target = per_target_logloss(y, pred_blend025)
        for j, target in enumerate(TARGETS):
            rate = true_block[:, [j]]
            pred = pred_block[:, [j]]
            target_rows.append(
                {
                    "view": name,
                    "target": target,
                    "block_weighted_logloss": weighted_rate_logloss(rate, pred, block_weight_all),
                    "block_rate_mae": weighted_mae(rate, pred, block_weight_all),
                    "block_rate_r2": weighted_r2(rate, pred, block_weight_all),
                    "row_direct_logloss": direct_target[target],
                    "row_blend025_logloss": blend_target[target],
                    "delta_blend025_vs_temporal": blend_target[target] - base_target_losses[target],
                }
            )

    summary_df = pd.DataFrame(summary_rows).sort_values("row_blend025_logloss").reset_index(drop=True)
    target_df = pd.DataFrame(target_rows).sort_values(["target", "row_blend025_logloss"]).reset_index(drop=True)
    geometry_df = pd.DataFrame(geometry_rows).sort_values("block_weighted_logloss").reset_index(drop=True)

    for name in view_names:
        pred_block = np.vstack(block_pred_store[name])
        energy = block_energy(true_block, pred_block)
        block_df[f"energy__{name}"] = energy

    summary_df.to_csv(OUT / "block_context_jepa_target_summary.csv", index=False)
    target_df.to_csv(OUT / "block_context_jepa_target_detail.csv", index=False)
    geometry_df.to_csv(OUT / "block_context_jepa_latent_geometry.csv", index=False)
    block_df.to_csv(OUT / "block_context_jepa_target_blocks.csv", index=False)

    best = summary_df.iloc[0]
    best_non_base = summary_df[summary_df["view"].ne("temporal_base")].iloc[0]
    report = [
        "# E47 Block-Context JEPA Target Audit",
        "",
        "## Question",
        "",
        "Can fold-safe context predict the held-out block-rate representation strongly enough to recover a meaningful part of the validation block-rate oracle gap?",
        "",
        "## Summary",
        "",
        f"- Temporal row LogLoss: `{temporal_row_loss:.6f}`.",
        f"- Validation block-rate oracle LogLoss: `{block_oracle_loss:.6f}`.",
        f"- Temporal-to-oracle gap available to a perfect block-state representation: `{oracle_gap:.6f}`.",
        f"- Best tested view by 25% row blend: `{best['view']}` at `{best['row_blend025_logloss']:.6f}`.",
        f"- Best non-base recovered oracle-gap fraction: `{best_non_base['oracle_gap_recovered_blend025']:.6f}`.",
        "",
        "## View Results",
        "",
        markdown_table(
            summary_df,
            [
                "view",
                "n_features",
                "block_weighted_logloss",
                "block_rate_mae",
                "block_rate_r2",
                "row_blend025_logloss",
                "delta_blend025_vs_temporal",
                "oracle_gap_recovered_blend025",
            ],
        ),
        "",
        "## Latent Geometry",
        "",
        markdown_table(
            geometry_df,
            [
                "view",
                "block_weighted_logloss",
                "anisotropy",
                "effective_rank",
                "nn_true_rate_mae",
                "energy_p90",
                "top20_block_energy_share",
            ],
        ),
        "",
        "## Interpretation",
        "",
        "This is a JEPA-style target-representation test: context consists of fold-safe same-subject label context plus sensor/missingness block summaries; target is the held-out block-rate vector, not raw reconstruction.",
        "",
        "A useful representation should reduce block-rate loss, improve row LogLoss under a conservative blend, and keep a non-collapsed geometry. If it only improves an auxiliary score or shows anisotropic high-energy concentration, it is evidence for a representation bottleneck rather than a submission candidate.",
        "",
    ]
    temporal_block_loss = float(
        summary_df.loc[summary_df["view"].eq("temporal_base"), "block_weighted_logloss"].iloc[0]
    )
    best_non_base_block_gain = temporal_block_loss - float(best_non_base["block_weighted_logloss"])
    if (
        float(best_non_base["delta_blend025_vs_temporal"]) < 0
        and best_non_base_block_gain > 0
        and float(best_non_base["oracle_gap_recovered_blend025"]) >= 0.05
    ):
        report.extend(
            [
                "## Decision",
                "",
                "A non-base block-context representation improved the conservative row blend. It deserves a follow-up gate test against actual submission topology before any candidate promotion.",
            ]
        )
    else:
        report.extend(
            [
                "## Decision",
                "",
                f"No tested fold-safe context representation recovers useful oracle gap under block-rate stress. The best non-base row blend moves only `{float(best_non_base['oracle_gap_recovered_blend025']):.6f}` of the oracle gap, and its block-rate loss is `{abs(best_non_base_block_gain):.6f}` {'worse' if best_non_base_block_gain < 0 else 'better'} than temporal block context.",
                "",
                "The small row-level gains are therefore better interpreted as weak calibration perturbations, not successful hidden block-state recovery.",
                "",
                "Do not submit a file from this audit. The next useful branch is to change the target/context construction itself, not add another ridge-style block regressor.",
            ]
        )
    (OUT / "block_context_jepa_target_report.md").write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
