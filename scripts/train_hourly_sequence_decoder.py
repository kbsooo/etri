from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class ModelSpec:
    name: str
    kind: str
    value: float
    selector_k: int
    weight_mode: str


@dataclass(frozen=True)
class Window:
    name: str
    lo: float
    hi: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        if col in out.columns:
            out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_windows(value: str) -> list[Window]:
    windows: list[Window] = []
    for item in value.split(","):
        if not item.strip():
            continue
        name, lo, hi = item.split(":")
        windows.append(Window(name, float(lo), float(hi)))
    return windows


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = sample_pos
    return train_out, sample_out


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    folds = []
    for indices in val_indices:
        val_idx = np.array(sorted(indices), dtype=int)
        train_idx = np.setdiff1d(all_idx, val_idx, assume_unique=False)
        folds.append((train_idx, val_idx))
    return folds


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing prediction columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    missing = sorted(set(TARGET_COLUMNS) - set(submission.columns))
    if missing:
        raise ValueError(f"Submission file missing target columns: {missing}")
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(args.base_oof))
    submission = normalize_keys(pd.read_csv(args.base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return prediction_matrix(oof), submission_matrix(submission)


def hourly_feature_table(hourly_path: str) -> pd.DataFrame:
    hourly = pd.read_parquet(hourly_path).copy()
    hourly["lifelog_date"] = pd.to_datetime(hourly["date"]).dt.strftime("%Y-%m-%d")
    hourly = hourly.drop(columns=["date"])
    numeric_cols = [
        col
        for col in hourly.columns
        if col not in ["subject_id", "lifelog_date", "hod", "in_keys"] and pd.api.types.is_numeric_dtype(hourly[col])
    ]
    parts = []
    for col in numeric_cols:
        pivot = hourly.pivot_table(index=["subject_id", "lifelog_date"], columns="hod", values=col, aggfunc="mean")
        pivot = pivot.reindex(columns=range(24))
        pivot.columns = [f"h{hour:02d}__{col}" for hour in pivot.columns]
        parts.append(pivot)
        observed = pivot.notna().astype(float)
        observed.columns = [f"obs__h{hour:02d}__{col}" for hour in range(24)]
        parts.append(observed)
    wide = pd.concat(parts, axis=1).reset_index()
    return normalize_keys(wide)


def add_optional_daily_features(
    args: argparse.Namespace,
    train_x: pd.DataFrame,
    test_x: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if args.include_master:
        master = normalize_keys(pd.read_parquet(args.master_path))
        drop_cols = set(TARGET_COLUMNS + ["role"])
        keep_cols = [col for col in master.columns if col not in drop_cols]
        rename = {
            col: f"master__{col}"
            for col in keep_cols
            if col not in KEY_COLUMNS and pd.api.types.is_numeric_dtype(master[col])
        }
        master_features = master[keep_cols].rename(columns=rename)
        train_x = train_x.merge(master_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_x = test_x.merge(master_features, on=KEY_COLUMNS, how="left", validate="one_to_one")

    if args.include_latent:
        latent_path = Path(args.latent_path)
        if not latent_path.exists():
            raise FileNotFoundError(f"Latent path does not exist: {latent_path}")
        latents = normalize_keys(pd.read_parquet(latent_path))
        latent_cols = [col for col in latents.columns if col.startswith("z_")]
        latent_features = latents[KEY_COLUMNS + latent_cols].rename(
            columns={col: f"latent__{col}" for col in latent_cols}
        )
        train_x = train_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")
        test_x = test_x.merge(latent_features, on=KEY_COLUMNS, how="left", validate="one_to_one")

    return train_x, test_x


def build_joined(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    train_raw = normalize_keys(pd.read_csv(args.train_path))
    sample_raw = normalize_keys(pd.read_csv(args.sample_path))
    train_raw, sample_raw = add_panel_position(train_raw, sample_raw)
    base_oof, base_test = load_base_predictions(args, train_raw, sample_raw)

    hourly = hourly_feature_table(args.hourly_path)
    train_x = train_raw.merge(hourly, on=["subject_id", "lifelog_date"], how="left", validate="one_to_one")
    test_x = sample_raw.merge(hourly, on=["subject_id", "lifelog_date"], how="left", validate="one_to_one")
    if train_x.filter(like="h00__").isna().all(axis=1).any() or test_x.filter(like="h00__").isna().all(axis=1).any():
        raise ValueError("Some rows failed to join with hourly grid")
    train_x, test_x = add_optional_daily_features(args, train_x, test_x)

    for frame in [train_x, test_x]:
        lifelog = pd.to_datetime(frame["lifelog_date"])
        frame["weekday"] = lifelog.dt.weekday.astype(float)
        frame["is_weekend"] = lifelog.dt.weekday.isin([5, 6]).astype(float)
        frame["weekday_sin"] = np.sin(2.0 * np.pi * frame["weekday"] / 7.0)
        frame["weekday_cos"] = np.cos(2.0 * np.pi * frame["weekday"] / 7.0)
        frame["date_ord"] = lifelog.map(pd.Timestamp.toordinal).astype(float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        train_x[f"base_pred_{target}"] = base_oof[:, target_i]
        test_x[f"base_pred_{target}"] = base_test[:, target_i]
        train_x[f"base_logit_{target}"] = safe_logit(base_oof[:, target_i])
        test_x[f"base_logit_{target}"] = safe_logit(base_test[:, target_i])
    return train_x, test_x, base_oof, base_test


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    blocked = set(KEY_COLUMNS + TARGET_COLUMNS)
    return [
        col
        for col in frame.columns
        if col not in blocked and pd.api.types.is_numeric_dtype(frame[col])
    ]


def make_ohe() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def make_model(spec: ModelSpec, numeric_cols: list[str], categorical_cols: list[str]) -> Pipeline:
    num_steps: list[tuple[str, object]] = [
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
    ]
    if spec.kind in {"logreg"}:
        num_steps.append(("scaler", StandardScaler()))
    if spec.selector_k > 0:
        num_steps.append(("select", SelectKBest(score_func=f_classif, k=spec.selector_k)))
    steps = [("num", Pipeline(num_steps), numeric_cols)]
    if categorical_cols:
        steps.append(("cat", make_ohe(), categorical_cols))
    preprocessor = ColumnTransformer(steps, remainder="drop")
    if spec.kind == "logreg":
        model = LogisticRegression(C=spec.value, solver="lbfgs", max_iter=5000, random_state=2026)
    elif spec.kind == "hgb":
        model = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.025,
            max_leaf_nodes=7,
            min_samples_leaf=10,
            l2_regularization=spec.value,
            random_state=2026,
        )
    elif spec.kind == "et":
        model = ExtraTreesClassifier(
            n_estimators=240,
            max_depth=4 if spec.value <= 4 else None,
            min_samples_leaf=max(2, int(spec.value)),
            max_features="sqrt",
            bootstrap=True,
            class_weight=None,
            random_state=2026,
            n_jobs=-1,
        )
    else:
        raise ValueError(f"Unknown model kind: {spec.kind}")
    return make_pipeline(preprocessor, model)


def fit_predict(model: Pipeline, x_train: pd.DataFrame, y: np.ndarray, x_eval: pd.DataFrame, sample_weight: np.ndarray) -> np.ndarray:
    classes = np.unique(y)
    if len(classes) < 2:
        return np.full(len(x_eval), float(classes[0]), dtype=float)
    model.fit(x_train, y, **{f"{model.steps[-1][0]}__sample_weight": sample_weight})
    return model.predict_proba(x_eval)[:, 1]


def position_bins(value: str) -> np.ndarray:
    bins = np.asarray(parse_float_list(value), dtype=float)
    if len(bins) < 2:
        raise ValueError("At least two position bins are required")
    bins[-1] = bins[-1] + 1e-6
    return bins


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if float(weights.mean()) > 0:
        weights = weights / float(weights.mean())
    return np.clip(weights, 0.0, 12.0)


def sample_support_mask(frame: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> np.ndarray:
    frame_bin = np.digitize(frame["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_counts = np.bincount(sample_bin, minlength=len(bins) - 1)
    return (sample_counts > 0)[frame_bin]


def fit_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray, mode: str) -> np.ndarray:
    sample_w = sample_position_weights(train, sample, bins)
    pos = train["panel_position"].to_numpy(dtype=float)
    supported = sample_support_mask(train, sample, bins)
    if mode == "uniform":
        weights = np.ones(len(train), dtype=float)
    elif mode == "sample":
        weights = sample_w
    elif mode == "midtail":
        weights = np.where(pos >= (1.0 / 3.0), sample_w + 0.5, 0.25)
    elif mode == "tail":
        weights = sample_w * np.where(pos >= 0.8, 4.0, 0.5)
    elif mode == "support":
        weights = np.where(supported, 2.5, 0.35)
    else:
        raise ValueError(f"Unknown weight mode: {mode}")
    if float(weights.mean()) > 0:
        weights = weights / float(weights.mean())
    return np.clip(weights, 0.05, 20.0)


def train_source(
    train_x: pd.DataFrame,
    test_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    spec: ModelSpec,
    bins: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    numeric_cols = numeric_columns(train_x)
    categorical_cols = ["subject_id"]
    if spec.selector_k > len(numeric_cols):
        spec = ModelSpec(spec.name, spec.kind, spec.value, len(numeric_cols), spec.weight_mode)
    oof = np.zeros((len(train_x), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(test_x), len(TARGET_COLUMNS)), dtype=float)
    y = train_x[TARGET_COLUMNS].astype(int).reset_index(drop=True)
    full_weights = fit_weights(train_x, sample_x, bins, spec.weight_mode)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            model = make_model(spec, numeric_cols, categorical_cols)
            oof[val_idx, target_i] = fit_predict(
                model,
                train_x.iloc[train_idx],
                y.loc[train_idx, target].to_numpy(),
                train_x.iloc[val_idx],
                full_weights[train_idx],
            )
        full_model = make_model(spec, numeric_cols, categorical_cols)
        test[:, target_i] = fit_predict(full_model, train_x, y[target].to_numpy(), test_x, full_weights)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def row_losses(y_arr: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def blend_values(base: np.ndarray, source: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = base + weight * (source - base)
    elif mode == "logit":
        out = sigmoid(safe_logit(base) + weight * (safe_logit(source) - safe_logit(base)))
    else:
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def weighted_bootstrap(diff: np.ndarray, weights: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    weights = np.clip(weights.astype(float), 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    prob = weights / weights.sum()
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(diff), size=len(diff), replace=True, p=prob)
        boot[i] = float(diff[idx].mean())
    return {
        "p025": float(np.quantile(boot, 0.025)),
        "p500": float(np.quantile(boot, 0.500)),
        "p975": float(np.quantile(boot, 0.975)),
    }


def score_windows(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    base_oof: np.ndarray,
    source_oof: np.ndarray,
    source_name: str,
    bins: np.ndarray,
    windows: list[Window],
    weights_to_try: list[float],
    mode: str,
    seed: int,
    bootstrap: int,
) -> list[dict[str, float | int | str]]:
    y_arr = train_x[TARGET_COLUMNS].to_numpy(dtype=float)
    base_loss = row_losses(y_arr, base_oof)
    sample_w = sample_position_weights(train_x, sample_x, bins)
    support = sample_support_mask(train_x, sample_x, bins)
    pos = train_x["panel_position"].to_numpy(dtype=float)
    rows: list[dict[str, float | int | str]] = []
    for window in windows:
        mask = support & (pos >= window.lo) & (pos < window.hi)
        if not bool(mask.any()):
            continue
        for target_i, target in enumerate(TARGET_COLUMNS):
            for weight in weights_to_try:
                final = base_oof.copy()
                final[mask, target_i] = blend_values(base_oof[:, target_i], source_oof[:, target_i], weight, mode)[mask]
                cand_loss = row_losses(y_arr, final)
                diff = base_loss - cand_loss
                boot = weighted_bootstrap(diff, sample_w, seed, bootstrap)
                target_base = log_loss(y_arr[:, target_i], base_oof[:, target_i], labels=[0, 1])
                target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1])
                weighted_target_base = log_loss(y_arr[:, target_i], base_oof[:, target_i], labels=[0, 1], sample_weight=sample_w)
                weighted_target_cand = log_loss(y_arr[:, target_i], final[:, target_i], labels=[0, 1], sample_weight=sample_w)
                row: dict[str, float | int | str] = {
                    "source": source_name,
                    "target": target,
                    "window": window.name,
                    "blend_weight": float(weight),
                    "applied_rows": int(mask.sum()),
                    "uniform_improvement": float(diff.mean()),
                    "uniform_avg_log_loss": float(cand_loss.mean()),
                    "weighted_improvement": float(np.average(diff, weights=sample_w)),
                    "weighted_p025": boot["p025"],
                    "weighted_p500": boot["p500"],
                    "weighted_p975": boot["p975"],
                    "target_delta": float(target_base - target_cand),
                    "weighted_target_delta": float(weighted_target_base - weighted_target_cand),
                }
                for block_name, lo, hi in [("mid", 1 / 3, 2 / 3), ("late", 2 / 3, 1.01), ("tail20", 0.8, 1.01)]:
                    idx = train_x.index[(pos >= lo) & (pos < hi)].to_numpy(dtype=int)
                    row[f"{block_name}_delta"] = float(diff[idx].mean()) if len(idx) else 0.0
                rows.append(row)
    return rows


def save_source(
    output_dir: Path,
    spec: ModelSpec,
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    oof: np.ndarray,
    test: np.ndarray,
) -> tuple[Path, Path]:
    oof_df = train_x[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = oof[:, target_i]
    oof_path = output_dir / f"oof_{spec.name}.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = sample_x[KEY_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = test[:, target_i]
    submission_path = output_dir / f"submission_{spec.name}.csv"
    submission.to_csv(submission_path, index=False)
    return oof_path, submission_path


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *body])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_x, test_x, base_oof, _ = build_joined(args)
    sample_x = normalize_keys(pd.read_csv(args.sample_path))
    _, sample_x = add_panel_position(normalize_keys(pd.read_csv(args.train_path)), sample_x)
    folds = make_subject_time_folds(train_x, args.folds)
    bins = position_bins(args.position_bins)
    windows = parse_windows(args.windows)
    weights_to_try = parse_float_list(args.blend_weights)

    specs = [
        ModelSpec("hourly_logreg_k80_c003_sample", "logreg", 0.03, 80, "sample"),
        ModelSpec("hourly_logreg_k120_c01_midtail", "logreg", 0.10, 120, "midtail"),
        ModelSpec("hourly_hgb_k80_l2_1_support", "hgb", 1.0, 80, "support"),
        ModelSpec("hourly_hgb_k120_l2_5_midtail", "hgb", 5.0, 120, "midtail"),
        ModelSpec("hourly_et_leaf4_k160_sample", "et", 4.0, 160, "sample"),
        ModelSpec("hourly_et_leaf8_k160_midtail", "et", 8.0, 160, "midtail"),
    ]
    if args.wide_specs:
        specs.extend(
            [
                ModelSpec("fused_logreg_k200_c003_sample", "logreg", 0.03, 200, "sample"),
                ModelSpec("fused_logreg_k260_c01_midtail", "logreg", 0.10, 260, "midtail"),
                ModelSpec("fused_logreg_k320_c03_tail", "logreg", 0.30, 320, "tail"),
                ModelSpec("fused_hgb_k200_l2_5_midtail", "hgb", 5.0, 200, "midtail"),
                ModelSpec("fused_hgb_k260_l2_15_sample", "hgb", 15.0, 260, "sample"),
                ModelSpec("fused_et_leaf12_k260_midtail", "et", 12.0, 260, "midtail"),
            ]
        )
    if args.quick:
        specs = specs[:3]

    score_rows = []
    source_rows = []
    for spec in specs:
        print(f"[source] {spec.name}")
        oof, test = train_source(train_x, test_x, sample_x, folds, spec, bins)
        oof_path, submission_path = save_source(output_dir, spec, train_x, test_x, oof, test)
        source_rows.append({"source": spec.name, "oof_path": str(oof_path), "submission_path": str(submission_path)})
        score_rows.extend(
            score_windows(
                train_x,
                sample_x,
                base_oof,
                oof,
                spec.name,
                bins,
                windows,
                weights_to_try,
                args.mode,
                args.seed,
                args.bootstrap,
            )
        )

    scores = pd.DataFrame(score_rows).sort_values(["weighted_p025", "weighted_improvement"], ascending=[False, False])
    sources = pd.DataFrame(source_rows)
    scores.to_csv(output_dir / "hourly_window_scores.csv", index=False)
    sources.to_csv(output_dir / "hourly_sources.csv", index=False)
    report = {
        "args": vars(args),
        "sources": source_rows,
        "top_scores": scores.head(30).to_dict(orient="records"),
    }
    (output_dir / "hourly_sequence_decoder_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Hourly Sequence Decoder Report",
        "",
        "## Sources",
        "",
        dataframe_to_markdown(sources),
        "",
        "## Top Window Scores",
        "",
        dataframe_to_markdown(scores.head(20)),
        "",
    ]
    (output_dir / "hourly_sequence_decoder_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(scores.head(args.print_top).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train hourly-grid source decoders and score sample-position target windows.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--hourly-path", default="artifacts/03_hourly_grid.parquet")
    parser.add_argument("--master-path", default="artifacts/10_master_daily.parquet")
    parser.add_argument("--latent-path", default="outputs/diffusion_encoder_id_long/day_latents.parquet")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/hourly_sequence_decoder")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--windows", default="mid:0.3333333333:0.6666666667,tail:0.8:1.000001,mid_tail:0.3333333333:1.000001")
    parser.add_argument("--blend-weights", default="1.0,0.8,0.65,0.5,0.3")
    parser.add_argument("--mode", default="logit", choices=["prob", "logit"])
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--print-top", type=int, default=40)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--include-master", action="store_true")
    parser.add_argument("--include-latent", action="store_true")
    parser.add_argument("--wide-specs", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
