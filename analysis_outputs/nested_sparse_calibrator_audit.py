from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import deep_dive_analysis as d  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = d.TARGETS
KEY = d.KEY
SUBMISSION_KEY = ["subject_id", "sleep_date", "lifelog_date"]

warnings.filterwarnings("ignore", message="Skipping features without any observed values.*")


@dataclass(frozen=True)
class CalConfig:
    pool: str
    k: int
    c: float

    @property
    def name(self) -> str:
        return f"{self.pool}_k{self.k}_c{self.c:g}"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(int)
    return float(log_loss(yy, pp, labels=[0, 1]))


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_feature_frames(base_oof: Path, base_submission: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_parquet(OUT / "train_deep_features.parquet").sort_values(KEY).reset_index(drop=True)
    sub = pd.read_parquet(OUT / "submission_deep_features.parquet").sort_values(KEY).reset_index(drop=True)
    proxy_path = OUT / "sleep_interval_proxy_augmented_features.parquet"
    if proxy_path.exists():
        proxy = pd.read_parquet(proxy_path)
        train = train.merge(proxy, on=KEY, how="left", suffixes=("", "_proxydup"))
        sub = sub.merge(proxy, on=KEY, how="left", suffixes=("", "_proxydup"))
        drop = [c for c in train.columns if c.endswith("_proxydup")]
        if drop:
            train = train.drop(columns=drop)
            sub = sub.drop(columns=drop)

    base = clip(np.load(base_oof))
    base_sub = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUBMISSION_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUBMISSION_KEY).reset_index(drop=True)
    assert base.shape == (len(train), len(TARGETS))
    assert base_sub[SUBMISSION_KEY].equals(sample[SUBMISSION_KEY])
    for j, target in enumerate(TARGETS):
        train[f"base_prob_{target}"] = base[:, j]
        train[f"base_logit_{target}"] = logit(base[:, j])
        sub[f"base_prob_{target}"] = base_sub[target].to_numpy(dtype=float)
        sub[f"base_logit_{target}"] = logit(base_sub[target].to_numpy(dtype=float))
    protected = set(TARGETS + KEY + ["sleep_date", "split", "subject_id", "dow", "month"])
    drop_all_nan = [
        c
        for c in train.columns
        if c not in protected and c in sub.columns and train[c].isna().all() and sub[c].isna().all()
    ]
    if drop_all_nan:
        train = train.drop(columns=drop_all_nan)
        sub = sub.drop(columns=drop_all_nan)
    return train, sub


def feature_columns(rows: pd.DataFrame, pool: str) -> list[str]:
    excluded = set(TARGETS + ["sleep_date", "split", "lifelog_date"])
    base_cols = [c for c in rows.columns if c.startswith("base_prob_") or c.startswith("base_logit_")]
    calendar = ["subject_id", "dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"]
    calendar = [c for c in calendar if c in rows.columns]
    if pool == "base_calendar":
        return calendar + base_cols
    if pool == "proxy":
        cols = calendar + base_cols + [c for c in rows.columns if c.startswith("proxy_")]
        return [c for c in cols if c not in excluded]
    if pool == "deep_proxy":
        return [c for c in rows.columns if c not in excluded and c not in KEY]
    raise ValueError(pool)


def configs() -> list[CalConfig]:
    out: list[CalConfig] = []
    for pool in ["base_calendar", "proxy", "deep_proxy"]:
        for k in [5, 10, 20, 40]:
            if pool == "base_calendar" and k > 10:
                continue
            for c in [0.02, 0.05, 0.10, 0.20]:
                out.append(CalConfig(pool, k, c))
    return out


def make_pipe(rows: pd.DataFrame, cols: list[str], cfg: CalConfig) -> Pipeline:
    cat = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num = [c for c in cols if c not in cat]
    k = min(cfg.k, max(1, len(num)))
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                        ("select", SelectKBest(score_func=f_classif, k=k)),
                    ]
                ),
                num,
            ),
        ],
        sparse_threshold=0.25,
    )
    clf = LogisticRegression(max_iter=2000, C=cfg.c, solver="liblinear")
    return Pipeline([("pre", pre), ("clf", clf)])


def predict_cfg(train_rows: pd.DataFrame, y: np.ndarray, rows: pd.DataFrame, cfg: CalConfig) -> np.ndarray:
    if len(np.unique(y)) < 2:
        return np.full(len(rows), float(np.mean(y)))
    cols = feature_columns(train_rows, cfg.pool)
    pipe = make_pipe(train_rows, cols, cfg)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train_rows[cols], y)
    proba = pipe.predict_proba(rows[cols])
    classes = list(pipe.named_steps["clf"].classes_)
    if 1 not in classes:
        return np.zeros(len(rows), dtype=float)
    return clip(proba[:, classes.index(1)])


def inner_select(rows: pd.DataFrame, y: np.ndarray, target: str, cfgs: list[CalConfig]) -> tuple[CalConfig, float, float]:
    folds = d.make_folds(rows.reset_index(drop=True), "subject_blocks")
    base = rows[f"base_prob_{target}"].to_numpy(dtype=float)
    grid = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0]
    best: tuple[float, CalConfig, float] | None = None
    for cfg in cfgs:
        pred = np.zeros(len(rows), dtype=float)
        for tr_idx, val_idx in folds:
            pred[val_idx] = predict_cfg(rows.iloc[tr_idx].copy(), y[tr_idx], rows.iloc[val_idx].copy(), cfg)
        for w in grid:
            blended = (1.0 - w) * base + w * pred
            score = loss_col(y, blended)
            if best is None or score < best[0]:
                best = (score, cfg, float(w))
    assert best is not None
    return best[1], best[2], best[0]


def nested_outer(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    targets: list[str],
    repeats: int,
    cfgs: list[CalConfig],
) -> tuple[pd.DataFrame, np.ndarray]:
    y_all = train[TARGETS].to_numpy(dtype=int)
    pred_sum = np.zeros((len(train), len(TARGETS)), dtype=float)
    pred_count = np.zeros((len(train), len(TARGETS)), dtype=float)
    rows = []
    for target in targets:
        j = TARGETS.index(target)
        for outer_id, (tr_idx, val_idx, fold_meta) in enumerate(geom.geometry_folds(train, sub, n_repeats=repeats)):
            tr = train.iloc[tr_idx].copy()
            val = train.iloc[val_idx].copy()
            cfg, weight, inner_score = inner_select(tr, tr[target].to_numpy(dtype=int), target, cfgs)
            model_pred = predict_cfg(tr, tr[target].to_numpy(dtype=int), val, cfg)
            base_val = val[f"base_prob_{target}"].to_numpy(dtype=float)
            cand = clip((1.0 - weight) * base_val + weight * model_pred)
            base_loss = loss_col(y_all[val_idx, j], base_val)
            cand_loss = loss_col(y_all[val_idx, j], cand)
            pred_sum[val_idx, j] += cand
            pred_count[val_idx, j] += 1.0
            rows.append(
                {
                    "target": target,
                    "outer_id": outer_id,
                    "fold_meta": str(fold_meta),
                    "selected_config": cfg.name,
                    "selected_pool": cfg.pool,
                    "selected_k": cfg.k,
                    "selected_c": cfg.c,
                    "selected_weight": weight,
                    "inner_score": inner_score,
                    "base_loss": base_loss,
                    "candidate_loss": cand_loss,
                    "delta": cand_loss - base_loss,
                    "n_val": len(val_idx),
                }
            )
        print(f"[nested sparse] target={target} outer={repeats}", flush=True)
    base = train[[f"base_prob_{t}" for t in TARGETS]].to_numpy(dtype=float)
    avg = base.copy()
    mask = pred_count > 0
    avg[mask] = pred_sum[mask] / pred_count[mask]
    return pd.DataFrame(rows), clip(avg)


def global_select_and_submission(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    base_submission: Path,
    summary: pd.DataFrame,
    cfgs: list[CalConfig],
    prefix: str,
) -> tuple[str, pd.DataFrame]:
    chosen = summary[(summary["delta_mean"] < -0.0008) & (summary["win_rate"] >= 0.625)].copy()
    if chosen.empty:
        return "", pd.DataFrame()
    base_sub = pd.read_csv(base_submission, parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUBMISSION_KEY).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SUBMISSION_KEY).reset_index(drop=True)
    assert base_sub[SUBMISSION_KEY].equals(sample[SUBMISSION_KEY])
    out = base_sub.copy()
    ops = []
    for row in chosen.itertuples(index=False):
        target = str(row.target)
        cfg, weight, inner_score = inner_select(train.copy(), train[target].to_numpy(dtype=int), target, cfgs)
        model_sub = predict_cfg(train.copy(), train[target].to_numpy(dtype=int), sub.copy(), cfg)
        base_col = base_sub[target].to_numpy(dtype=float)
        out[target] = clip((1.0 - weight) * base_col + weight * model_sub)
        ops.append(
            {
                "target": target,
                "outer_delta_mean": float(row.delta_mean),
                "outer_win_rate": float(row.win_rate),
                "global_config": cfg.name,
                "global_weight": weight,
                "global_inner_score": inner_score,
            }
        )
    op_name = "_".join(f"{r['target']}__{r['global_config']}__w{r['global_weight']:g}" for r in ops)
    file_path = OUT / f"submission_{prefix}_{op_name}.csv"
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    out.to_csv(file_path, index=False)
    ops_df = pd.DataFrame(ops)
    ops_df.to_csv(OUT / f"{prefix}_{op_name}_ops.csv", index=False)
    return str(file_path), ops_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, required=True)
    parser.add_argument("--base-submission", type=Path, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--targets", default="Q1,Q2,Q3,S1,S2,S3,S4")
    parser.add_argument("--outer-repeats", type=int, default=8)
    args = parser.parse_args()

    train, sub = load_feature_frames(args.base_oof, args.base_submission)
    targets = [t for t in args.targets.split(",") if t]
    cfgs = configs()
    fold_rows, avg_pred = nested_outer(train, sub, targets, args.outer_repeats, cfgs)
    fold_rows.to_csv(OUT / f"{args.prefix}_folds.csv", index=False)
    np.save(OUT / f"{args.prefix}_avg_outer_oof.npy", avg_pred)
    summary = (
        fold_rows.groupby("target")
        .agg(
            delta_mean=("delta", "mean"),
            delta_median=("delta", "median"),
            win_rate=("delta", lambda s: float((s < 0).mean())),
            weight_mean=("selected_weight", "mean"),
            inner_score_mean=("inner_score", "mean"),
        )
        .reset_index()
        .sort_values("delta_mean")
    )
    config_mode = fold_rows.groupby("target")["selected_config"].agg(lambda s: s.value_counts().index[0]).rename("mode_config")
    summary = summary.merge(config_mode, on="target", how="left")
    y = train[TARGETS].to_numpy(dtype=int)
    base = train[[f"base_prob_{t}" for t in TARGETS]].to_numpy(dtype=float)
    cv_rows = []
    for j, target in enumerate(TARGETS):
        cv_rows.append(
            {
                "target": target,
                "base_loss": loss_col(y[:, j], base[:, j]),
                "avg_outer_loss": loss_col(y[:, j], avg_pred[:, j]),
                "delta": loss_col(y[:, j], avg_pred[:, j]) - loss_col(y[:, j], base[:, j]),
            }
        )
    cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base), "avg_outer_loss": mean_loss(y, avg_pred), "delta": mean_loss(y, avg_pred) - mean_loss(y, base)})
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / f"{args.prefix}_avg_outer_cv_estimate.csv", index=False)
    submission, ops = global_select_and_submission(train, sub, args.base_submission, summary, cfgs, args.prefix)
    summary["submission"] = submission
    summary.to_csv(OUT / f"{args.prefix}_summary.csv", index=False)
    print("\n[summary]")
    print(summary.round(9).to_string(index=False))
    print("\n[avg outer cv]")
    print(cv.round(9).to_string(index=False))
    if not ops.empty:
        print("\n[ops]")
        print(ops.round(9).to_string(index=False))
        print("submission", submission)


if __name__ == "__main__":
    main()
