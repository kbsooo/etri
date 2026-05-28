from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

import broad_single_feature_residual_probe as broad


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]

BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
FEATURE_OUT = OUT / "cross_view_jepa_surprise_features.parquet"
PREFILTER_OUT = OUT / "cross_view_jepa_surprise_prefilter.csv"
SCAN_OUT = OUT / "cross_view_jepa_surprise_scan.csv"
GUARD_OUT = OUT / "cross_view_jepa_surprise_guardrail.csv"
REPORT_OUT = OUT / "cross_view_jepa_surprise_report.md"

VIEW_SPECS = [
    {
        "name": "deep_phone",
        "path": OUT / "all_keys_deep_features.parquet",
        "tokens": ("phone_", "usage_"),
        "max_cols": 180,
        "prefix": "deep",
    },
    {
        "name": "deep_context",
        "path": OUT / "all_keys_deep_features.parquet",
        "tokens": ("gps_", "loc_", "wifi_", "ble_", "ambience_"),
        "max_cols": 180,
        "prefix": "deep",
    },
    {
        "name": "sleep_proxy",
        "path": OUT / "sleep_interval_proxy_augmented_features.parquet",
        "tokens": ("proxy_",),
        "max_cols": 220,
        "prefix": "sleep",
    },
    {
        "name": "quiet_fragment",
        "path": OUT / "quiet_window_residual_features.parquet",
        "tokens": ("quiet_",),
        "max_cols": 220,
        "prefix": "quiet",
    },
    {
        "name": "rhythm_regular",
        "path": OUT / "rhythm_regular_features.parquet",
        "tokens": ("rr_",),
        "max_cols": 220,
        "prefix": "rr",
    },
    {
        "name": "measurement_process",
        "path": OUT / "measurement_process_features.parquet",
        "tokens": (
            "mp_screen",
            "mp_usage",
            "mp_hr",
            "mp_watch",
            "mp_light",
            "mp_wlight",
            "mp_pedo",
            "mp_activity",
            "mp_ac",
            "mp_active",
            "mp_sensor",
        ),
        "max_cols": 260,
        "prefix": "mp",
    },
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_keys() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train["split"] = "train"
    sub["split"] = "submission"
    keys = pd.concat(
        [train[KEY + ["sleep_date", "split"]], sub[KEY + ["sleep_date", "split"]]],
        ignore_index=True,
    )
    return keys.sort_values(KEY).reset_index(drop=True)


def numeric_candidates(df: pd.DataFrame, tokens: tuple[str, ...]) -> list[str]:
    skip = set(KEY + ["sleep_date", "split"] + TARGETS)
    cols = []
    for col in df.columns:
        if col in skip:
            continue
        if tokens and not any(tok in col for tok in tokens):
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().sum() >= 120 and s.nunique(dropna=True) > 2:
                cols.append(col)
    return cols


def select_unsupervised_columns(df: pd.DataFrame, cols: list[str], max_cols: int) -> list[str]:
    if len(cols) <= max_cols:
        return cols
    scores = []
    n = len(df)
    for col in cols:
        s = pd.to_numeric(df[col], errors="coerce")
        finite = float(s.notna().mean())
        nunique = float(min(s.nunique(dropna=True), n))
        missing_balance = 1.0 - abs(finite - 0.85)
        if not np.isfinite(missing_balance):
            missing_balance = 0.0
        score = finite * np.log1p(nunique) + 0.05 * missing_balance
        scores.append((score, col))
    scores.sort(reverse=True)
    return [col for _, col in scores[:max_cols]]


def read_view(keys: pd.DataFrame, spec: dict[str, object]) -> pd.DataFrame:
    path = Path(spec["path"])
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, parse_dates=["lifelog_date"])
    if "lifelog_date" in df.columns:
        df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
    cols = numeric_candidates(df, tuple(spec["tokens"]))
    cols = select_unsupervised_columns(df, cols, int(spec["max_cols"]))
    view = keys[KEY].merge(df[KEY + cols], on=KEY, how="left")
    renamed = {col: f"{spec['prefix']}__{col}" for col in cols}
    view = view.rename(columns=renamed)
    return view


def embed_view(view: pd.DataFrame, name: str, n_components: int) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    cols = [c for c in view.columns if c not in KEY]
    x = view[cols].apply(pd.to_numeric, errors="coerce")
    if x.shape[1] == 0:
        raise ValueError(f"empty view: {name}")
    imp = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    arr = imp.fit_transform(x)
    arr = scaler.fit_transform(arr)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    k = max(1, min(n_components, arr.shape[0] - 1, arr.shape[1]))
    pcs = PCA(n_components=k, random_state=314159).fit_transform(arr)
    out = view[KEY].copy()
    pc_cols = []
    for i in range(k):
        col = f"cvjepa__{name}__pc{i:02d}"
        out[col] = pcs[:, i]
        pc_cols.append(col)
    out[f"cvjepa__{name}__pc_l2"] = np.sqrt(np.mean(pcs**2, axis=1))
    out[f"cvjepa__{name}__pc_abs_mean"] = np.mean(np.abs(pcs), axis=1)
    return out, pcs, pc_cols


def cos_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.divide((a * b).sum(axis=1), denom, out=np.zeros(len(a)), where=denom > 1e-12)


def residual_features(
    keys: pd.DataFrame,
    source_name: str,
    source: np.ndarray,
    target_name: str,
    target: np.ndarray,
    alpha: float,
) -> pd.DataFrame:
    k = min(source.shape[1], target.shape[1])
    src = source[:, :k]
    tgt = target[:, :k]
    pred = Ridge(alpha=alpha).fit(src, tgt).predict(src)
    resid = tgt - pred
    out = keys[KEY].copy()
    prefix = f"cvjepa__{source_name}_to_{target_name}"
    for i in range(k):
        out[f"{prefix}__resid_pc{i:02d}"] = resid[:, i]
    out[f"{prefix}__resid_l2"] = np.sqrt(np.mean(resid**2, axis=1))
    out[f"{prefix}__resid_abs_mean"] = np.mean(np.abs(resid), axis=1)
    out[f"{prefix}__resid_abs_max"] = np.max(np.abs(resid), axis=1)
    out[f"{prefix}__pred_l2"] = np.sqrt(np.mean(pred**2, axis=1))
    out[f"{prefix}__target_pred_cos"] = cos_rows(tgt, pred)
    out[f"{prefix}__target_minus_pred_l2"] = out[f"{prefix}__resid_l2"]
    return out


def build_cross_view_features(force: bool = False, n_components: int = 8, alpha: float = 10.0) -> pd.DataFrame:
    if FEATURE_OUT.exists() and not force:
        return pd.read_parquet(FEATURE_OUT)

    keys = read_keys()
    embeddings: dict[str, np.ndarray] = {}
    frames = [keys[KEY + ["sleep_date", "split"]].copy()]
    view_meta_rows = []
    for spec in VIEW_SPECS:
        name = str(spec["name"])
        view = read_view(keys, spec)
        embed, pcs, pc_cols = embed_view(view, name, n_components)
        frames.append(embed.drop(columns=KEY))
        embeddings[name] = pcs
        view_meta_rows.append({"view": name, "raw_columns": view.shape[1] - len(KEY), "pc_columns": len(pc_cols)})

    names = list(embeddings)
    for target_name in names:
        others = [name for name in names if name != target_name]
        for source_name in others:
            res = residual_features(
                keys,
                source_name,
                embeddings[source_name],
                target_name,
                embeddings[target_name],
                alpha,
            )
            frames.append(res.drop(columns=KEY))

        # Multi-view context prediction: the LeJEPA-style target is a view latent,
        # and the context is every other sensor view concatenated.
        context = np.concatenate([embeddings[name] for name in others], axis=1)
        res = residual_features(keys, "all_context", context, target_name, embeddings[target_name], alpha)
        frames.append(res.drop(columns=KEY))

    features = pd.concat(frames, axis=1)
    features.to_parquet(FEATURE_OUT, index=False)
    pd.DataFrame(view_meta_rows).to_csv(OUT / "cross_view_jepa_surprise_view_meta.csv", index=False)
    return features


def build_train_frame(features: pd.DataFrame) -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    feat = features[features["split"].eq("train")].drop(columns=["sleep_date", "split"])
    out = train.merge(feat, on=KEY, how="left")
    assert len(out) == len(train)
    return out


def finite_feature_cols(df: pd.DataFrame) -> list[str]:
    skip = set(TARGETS + KEY + ["sleep_date"])
    cols = []
    for col in df.columns:
        if col in skip:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 120 and s.nunique(dropna=True) > 2:
            cols.append(col)
    return cols


def prefilter_features(df: pd.DataFrame, base: np.ndarray, cols: list[str], top_n: int) -> pd.DataFrame:
    y = df[TARGETS].to_numpy(dtype=int)
    rows = []
    for target in TARGETS:
        j = TARGETS.index(target)
        residual = y[:, j].astype(float) - base[:, j]
        for col in cols:
            for mode in broad.MODES:
                try:
                    x_ref, _ = broad.transform_pair(df, df, col, mode)
                except Exception:
                    continue
                r = broad.corr(x_ref, residual)
                if np.isfinite(r):
                    rows.append({"target": target, "feature": col, "mode": mode, "corr": r, "abs_corr": abs(r)})
    pre = pd.DataFrame(rows).sort_values(["target", "abs_corr"], ascending=[True, False])
    return pre.groupby("target", group_keys=False).head(top_n).reset_index(drop=True)


def scan_candidates(df: pd.DataFrame, base: np.ndarray, pre: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str, str, float], np.ndarray]]:
    y = df[TARGETS].to_numpy(dtype=int)
    rows = []
    preds: dict[tuple[str, str, str, float], np.ndarray] = {}
    c_values = [0.03, 0.05, 0.10, 0.20, 0.50]
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in c_values:
            key = (target, feature, mode, float(c_value))
            corrected = broad.oof_corrected(df, base, target, feature, mode, float(c_value))
            preds[key] = corrected
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta": float(losses[best_i] - base_loss),
            }
            rows.append(row)
    scan = pd.DataFrame(rows).sort_values(["target", "delta", "best_loss"]).reset_index(drop=True)
    return scan, preds


def guard_top(
    df: pd.DataFrame,
    base: np.ndarray,
    scan: pd.DataFrame,
    preds: dict[tuple[str, str, str, float], np.ndarray],
    top_k: int,
) -> pd.DataFrame:
    y = df[TARGETS].to_numpy(dtype=int)
    rows = []
    top = scan.groupby("target", group_keys=False).head(top_k)
    for cand in top.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        c_value = float(cand.c_value)
        j = TARGETS.index(target)
        corrected = preds[(target, feature, mode, c_value)]
        guard = broad.repeated_subject_guardrail(df, y, base, corrected, j)
        row = cand._asdict()
        row.update({f"guard_{k}": v for k, v in guard.items()})
        row["strict_pass"] = (
            row["delta"] < 0.0
            and row["guard_mean_delta"] < 0.0
            and row["guard_win_rate"] >= 0.55
            and row["guard_zero_weight_rate"] <= 0.80
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["strict_pass", "delta"], ascending=[False, True]).reset_index(drop=True)


def write_report(df: pd.DataFrame, base: np.ndarray, pre: pd.DataFrame, scan: pd.DataFrame, guard: pd.DataFrame) -> None:
    y = df[TARGETS].to_numpy(dtype=int)
    base_mean = mean_loss(y, base)
    best_target = scan.groupby("target", as_index=False).head(1).copy()
    strict = guard[guard["strict_pass"]].copy()
    lines = [
        "# Cross-View JEPA Surprise Probe",
        "",
        "This probe builds unsupervised cross-view JEPA-style features from existing raw-log representations.",
        "Each sensor view is compressed into PCA latents, then one view predicts another with ridge regression.",
        "The residuals are treated as sensor-view surprise features and tested as fold-safe one-feature logit corrections on top of stage2 OOF.",
        "",
        "## Base",
        "",
        f"- Base OOF: `{BASE_OOF.name}`",
        f"- Base mean log loss: `{base_mean:.10f}`",
        f"- Feature rows/columns: `{df.shape[0]}` / `{df.shape[1]}` train-frame columns",
        f"- Prefilter rows: `{len(pre)}`",
        f"- Scanned rows: `{len(scan)}`",
        f"- Strict repeated-subject passes: `{len(strict)}`",
        "",
        "## Best Per Target",
        "",
        "```csv",
        best_target[
            [
                "target",
                "feature",
                "mode",
                "corr",
                "c_value",
                "base_loss",
                "best_loss",
                "delta",
                "best_weight",
            ]
        ]
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Guarded Top",
        "",
        "```csv",
        guard[
            [
                "target",
                "feature",
                "mode",
                "c_value",
                "delta",
                "best_weight",
                "guard_mean_delta",
                "guard_win_rate",
                "guard_mean_selected_weight",
                "guard_zero_weight_rate",
                "strict_pass",
            ]
        ]
        .head(28)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Interpretation",
        "",
        "- A strict pass means the cross-view residual improves the full subject-block OOF target and survives repeated subject-half weight selection.",
        "- Failing this guard does not make the feature useless; it means it should be treated as a hidden-structure clue rather than a direct submission correction.",
        "- The most valuable features here are residual norms/cosines where sleep/quiet/rhythm latents are not predictable from phone/context/measurement-process latents.",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-features", action="store_true")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--guard-top-k", type=int, default=8)
    args = parser.parse_args()

    features = build_cross_view_features(force=args.force_features)
    df = build_train_frame(features)
    base = clip(np.load(BASE_OOF))
    y = df[TARGETS].to_numpy(dtype=int)
    if base.shape != y.shape:
        raise ValueError(f"base shape {base.shape} does not match y shape {y.shape}")

    cols = finite_feature_cols(df)
    pre = prefilter_features(df, base, cols, args.top_n)
    pre.to_csv(PREFILTER_OUT, index=False)
    scan, preds = scan_candidates(df, base, pre)
    scan.to_csv(SCAN_OUT, index=False)
    guard = guard_top(df, base, scan, preds, args.guard_top_k)
    guard.to_csv(GUARD_OUT, index=False)
    write_report(df, base, pre, scan, guard)

    print(f"base_mean={mean_loss(y, base):.10f}")
    print(f"features={FEATURE_OUT}")
    print("\n[best per target]")
    print(
        scan.groupby("target", as_index=False)
        .head(1)[["target", "feature", "mode", "c_value", "delta", "best_weight"]]
        .round(10)
        .to_string(index=False)
    )
    print("\n[guarded top]")
    keep = [
        "target",
        "feature",
        "mode",
        "c_value",
        "delta",
        "guard_mean_delta",
        "guard_win_rate",
        "strict_pass",
    ]
    print(guard[keep].head(20).round(10).to_string(index=False))
    print(f"\nwrote: {PREFILTER_OUT}")
    print(f"wrote: {SCAN_OUT}")
    print(f"wrote: {GUARD_OUT}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
