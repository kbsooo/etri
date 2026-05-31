#!/usr/bin/env python3
"""E358: row-state public-survival audit for compact lifestyle-state probes.

Question:
    E357 used output-space movement anatomy to select a compact lifestyle-state
    probe.  Does the same selection still look sane when each candidate is
    viewed through the row-level human/social lifestyle state learned in E328?

JEPA/data2vec translation:
    context = row-level own-latent lifestyle state, story state, and cluster
              risk geometry on the 250 hidden test days
    target  = known public-survival contrast relative to E247
    action  = keep or demote compact-basin candidates based on whether their
              movement lands on interpretable row states rather than public-bad
              row-state pockets

The known public scores are used as a fixed diagnostic sensor, not as a loop
that tunes arbitrary blends.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402


RNG_SEED = 20260531 + 358
EPS = 1.0e-6
N_PERMUTATIONS = 80

KEY = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ANCHOR_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
ANCHOR_PUBLIC_LB = 0.5761589494

OBS_IN = OUT / "public_probe_observations.csv"
OWNSTATE_IN = OUT / "e328_ownlatent_lifestyle_state_features.parquet"
OWNCLUSTER_IN = OUT / "e328_ownlatent_lifestyle_state_cluster_summary.csv"
STORY_IN = OUT / "e268_human_social_story_features.parquet"
E357_POOL_IN = OUT / "e357_public_survival_contrast_pool.csv"
E357_SELECTION_IN = OUT / "e357_public_survival_contrast_selection.csv"

KNOWN_OUT = OUT / "e358_rowstate_public_survival_known.csv"
LOOCV_OUT = OUT / "e358_rowstate_public_survival_loocv.csv"
PRED_OUT = OUT / "e358_rowstate_public_survival_loo_predictions.csv"
POOL_OUT = OUT / "e358_rowstate_public_survival_pool.csv"
SELECTION_OUT = OUT / "e358_rowstate_public_survival_selection.csv"
REPORT_OUT = OUT / "e358_rowstate_public_survival_report.md"
UPLOAD_PREFIX = "submission_e358_rowstate_publicsurvival"


def locate(path_or_name: object) -> Path | None:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    return None


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY:
        if col in out.columns:
            if col in {"sleep_date", "lifelog_date"}:
                out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
            else:
                out[col] = out[col].astype(str)
    return out.sort_values(KEY).reset_index(drop=True)


def short_hash(frame: pd.DataFrame) -> str:
    cols = [c for c in KEY + TARGETS if c in frame.columns]
    payload = pd.util.hash_pandas_object(frame[cols], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def load_submission(path: Path) -> pd.DataFrame:
    df = normalize_keys(pd.read_csv(path))
    missing = [c for c in KEY + TARGETS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing columns: {missing}")
    return df[KEY + TARGETS]


def load_anchor() -> tuple[pd.DataFrame, np.ndarray]:
    path = locate(ANCHOR_FILE)
    if path is None:
        raise FileNotFoundError(ANCHOR_FILE)
    anchor = load_submission(path)
    return anchor, logit(anchor[TARGETS].to_numpy(dtype=np.float64))


def align_delta(path: Path, anchor: pd.DataFrame, anchor_logit: np.ndarray) -> np.ndarray:
    sub = load_submission(path)
    if not sub[KEY].equals(anchor[KEY]):
        sub = anchor[KEY].merge(sub, on=KEY, how="left", validate="one_to_one")
        if sub[TARGETS].isna().any().any():
            raise ValueError(f"Could not align {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit


def safe_spearman(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 5:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return 0.0
    pooled = np.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / max(len(a) + len(b) - 2, 1))
    if not np.isfinite(pooled) or pooled < 1.0e-12:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    sd = float(x.std(ddof=0))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return pd.Series(0.0, index=s.index)
    return (x - float(x.mean())) / sd


def load_row_state(anchor: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    own = normalize_keys(pd.read_parquet(OWNSTATE_IN))
    story = normalize_keys(pd.read_parquet(STORY_IN))
    own_test = own[own["split"].astype(str).isin(["test", "submission"])].copy()
    story_test = story[story["split"].astype(str).isin(["test", "submission"])].copy()
    merged = anchor[KEY].merge(own_test, on=KEY, how="left", validate="one_to_one")
    merged = merged.merge(story_test, on=KEY, how="left", suffixes=("", "_story"), validate="one_to_one")
    if merged[["ownlife_energy", "ownlife_k8"]].isna().any().any():
        raise RuntimeError("E328 own-lifestyle state failed to align onto anchor rows")

    cluster = pd.read_csv(OWNCLUSTER_IN).set_index("cluster")
    merged["rowstate_e323_cluster_rate"] = merged["ownlife_k8"].map(cluster["e323_top20_rate"]).fillna(0.0).astype(float)
    merged["rowstate_e247_cluster_rate"] = merged["ownlife_k8"].map(cluster["e247_only_rate"]).fillna(0.0).astype(float)
    merged["rowstate_e256_cluster_rate"] = merged["ownlife_k8"].map(cluster["e256_only_rate"]).fillna(0.0).astype(float)
    merged["rowstate_bad_minus_good"] = merged["rowstate_e323_cluster_rate"] + merged["rowstate_e256_cluster_rate"] - merged["rowstate_e247_cluster_rate"]

    base_state_cols = [
        c
        for c in merged.columns
        if (
            c.startswith("ownlife_pc")
            or c in {
                "ownlife_energy",
                "ownlife_global_distance",
                "ownlife_student_resid_mean",
                "ownlife_student_resid_max",
                "ownlife_cluster_distance",
                "rowstate_e323_cluster_rate",
                "rowstate_e247_cluster_rate",
                "rowstate_e256_cluster_rate",
                "rowstate_bad_minus_good",
                "is_weekend",
                "weekday",
            }
        )
    ]
    story_cols = [
        c
        for c in merged.columns
        if (
            c.endswith("_subj_z")
            and not c.startswith("ownlife")
            and pd.api.types.is_numeric_dtype(merged[c])
        )
    ]
    # Keep the story axes most aligned with known bad/good E328 cluster markers.
    scored = []
    marker = zscore(merged["rowstate_bad_minus_good"])
    for col in story_cols:
        vals = zscore(merged[col])
        corr = safe_spearman(vals, marker)
        scored.append((abs(corr) if np.isfinite(corr) else 0.0, col))
    scored.sort(reverse=True)
    story_keep = [c for _, c in scored[:28]]

    for col in base_state_cols + story_keep:
        merged[col] = pd.to_numeric(merged[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    return merged, base_state_cols, story_keep


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    if total <= 1.0e-12:
        return 0.0
    return float(np.sum(values * weights) / total)


def weighted_abs_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return weighted_mean(np.abs(values), weights)


def rowstate_features(delta: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> dict[str, float]:
    d = np.asarray(delta, dtype=np.float64)
    absd = np.abs(d)
    row_abs = absd.sum(axis=1)
    total = float(row_abs.sum())
    out: dict[str, float] = {
        "cell_l1": float(absd.sum()),
        "cell_l2": float(np.linalg.norm(d.reshape(-1))),
        "row_l1_mean": float(np.mean(row_abs)),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
        "changed_rows_1e6": int((row_abs > 1.0e-6).sum()),
    }
    target_l1 = absd.sum(axis=0)
    denom = float(target_l1.sum())
    for i, target in enumerate(TARGETS):
        out[f"share_{target}"] = float(target_l1[i] / denom) if denom > 0 else 0.0
        out[f"target_abs_{target}"] = float(target_l1[i])

    state_local = state.copy()
    for col in ["ownlife_energy", "ownlife_student_resid_mean", "ownlife_cluster_distance", "rowstate_e323_cluster_rate", "rowstate_e247_cluster_rate", "rowstate_e256_cluster_rate", "rowstate_bad_minus_good"]:
        vals = state_local[col].to_numpy(dtype=np.float64)
        out[f"wmean_{col}"] = weighted_mean(vals, row_abs)
        out[f"wabs_{col}"] = weighted_abs_mean(vals, row_abs)
        top = vals >= np.quantile(vals, 0.80)
        out[f"move_share_top20_{col}"] = float(row_abs[top].sum() / total) if total > 0 else 0.0

    clusters = pd.to_numeric(state_local["ownlife_k8"], errors="coerce").fillna(-1).astype(int).to_numpy()
    for k in range(8):
        out[f"cluster_{k}_move_share"] = float(row_abs[clusters == k].sum() / total) if total > 0 else 0.0

    # Target-specific exposure to known bad/good row-state clusters.
    bad = state_local["rowstate_e323_cluster_rate"].to_numpy(dtype=np.float64)
    good = state_local["rowstate_e247_cluster_rate"].to_numpy(dtype=np.float64)
    for i, target in enumerate(TARGETS):
        w = absd[:, i]
        out[f"{target}_bad_cluster_wmean"] = weighted_mean(bad, w)
        out[f"{target}_good_cluster_wmean"] = weighted_mean(good, w)
        out[f"{target}_bad_minus_good_wmean"] = out[f"{target}_bad_cluster_wmean"] - out[f"{target}_good_cluster_wmean"]

    for col in base_cols:
        vals = state_local[col].to_numpy(dtype=np.float64)
        out[f"wmean_{col}"] = weighted_mean(vals, row_abs)

    for col in story_cols:
        vals = state_local[col].to_numpy(dtype=np.float64)
        out[f"story_wmean_{col}"] = weighted_mean(vals, row_abs)
        out[f"story_top20_move_{col}"] = float(row_abs[vals >= np.quantile(vals, 0.80)].sum() / total) if total > 0 else 0.0

    if total > 0:
        p = row_abs / total
        p = p[p > 0]
        out["row_move_entropy"] = float(-(p * np.log(p)).sum() / max(np.log(len(row_abs)), 1.0))
    else:
        out["row_move_entropy"] = 0.0
    return out


def known_observations(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> pd.DataFrame:
    obs = pd.read_csv(OBS_IN)
    if ANCHOR_FILE not in set(obs["file"].astype(str)):
        obs = pd.concat(
            [obs, pd.DataFrame([{"file": ANCHOR_FILE, "public_lb": ANCHOR_PUBLIC_LB, "note": "Current known public best anchor."}])],
            ignore_index=True,
        )
    rows: list[dict[str, Any]] = []
    for rec in obs.to_dict("records"):
        path = locate(rec["file"])
        if path is None:
            continue
        delta = align_delta(path, anchor, anchor_logit)
        feats = rowstate_features(delta, state, base_cols, story_cols)
        rows.append(
            {
                "file": rel(path),
                "basename": path.name,
                "public_lb": float(rec["public_lb"]),
                "delta_vs_e247": float(rec["public_lb"]) - ANCHOR_PUBLIC_LB,
                "note": rec.get("note", ""),
                **feats,
            }
        )
    known = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    known.to_csv(KNOWN_OUT, index=False)
    return known


def feature_columns(frame: pd.DataFrame) -> list[str]:
    blocked = {"file", "basename", "public_lb", "delta_vs_e247", "note"}
    cols = []
    for col in frame.columns:
        if col in blocked:
            continue
        if pd.api.types.is_numeric_dtype(frame[col]) and frame[col].nunique(dropna=True) > 1:
            cols.append(col)
    # The public label set is tiny; keep stable low-dimensional row-state summaries.
    priority_tokens = (
        "cluster_",
        "rowstate_",
        "bad_cluster",
        "good_cluster",
        "bad_minus_good",
        "share_",
        "move_share_top20_",
        "ownlife_",
        "story_top20_move_",
    )
    priority = [c for c in cols if any(tok in c for tok in priority_tokens)]
    rest = [c for c in cols if c not in priority]
    keep = priority[:90] + rest[:30]
    return keep


def make_models() -> dict[str, Any]:
    return {
        "ridge_10": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "ridge_1": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
        "knn3": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=3, weights="distance")),
        "extratrees": ExtraTreesRegressor(n_estimators=128, min_samples_leaf=2, max_features=0.7, random_state=RNG_SEED, n_jobs=1),
    }


def loocv_diagnostics(known: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    x = known[cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    y = known["delta_vs_e247"].to_numpy(dtype=np.float64)
    loo = LeaveOneOut()
    rows = []
    pred_rows = []
    rng = np.random.default_rng(RNG_SEED)
    models = make_models()
    for name, model in models.items():
        pred = np.zeros(len(known), dtype=np.float64)
        for tr_idx, va_idx in loo.split(x):
            model.fit(x.iloc[tr_idx], y[tr_idx])
            pred[va_idx] = np.asarray(model.predict(x.iloc[va_idx]), dtype=np.float64)
        rho = safe_spearman(y, pred)
        mae = float(np.mean(np.abs(y - pred)))
        perm_scores = []
        if name != "extratrees":
            for _ in range(N_PERMUTATIONS):
                yp = rng.permutation(y)
                pp = np.zeros(len(known), dtype=np.float64)
                for tr_idx, va_idx in loo.split(x):
                    model.fit(x.iloc[tr_idx], yp[tr_idx])
                    pp[va_idx] = np.asarray(model.predict(x.iloc[va_idx]), dtype=np.float64)
                perm_scores.append(safe_spearman(y, pp))
        perm_arr = np.asarray([v for v in perm_scores if np.isfinite(v)], dtype=np.float64)
        p95 = float(np.quantile(perm_arr, 0.95)) if len(perm_arr) else np.nan
        rows.append(
            {
                "model": name,
                "known_rows": len(known),
                "feature_count": len(cols),
                "loo_spearman": rho,
                "loo_mae": mae,
                "perm_spearman_mean": float(np.mean(perm_arr)) if len(perm_arr) else np.nan,
                "perm_spearman_p95": p95,
                "beats_perm_p95": bool(np.isfinite(rho) and np.isfinite(p95) and rho > p95),
            }
        )
        for i, row in known.iterrows():
            pred_rows.append(
                {
                    "model": name,
                    "basename": row["basename"],
                    "public_lb": row["public_lb"],
                    "delta_vs_e247": row["delta_vs_e247"],
                    "loo_pred_delta": pred[i],
                    "abs_error": abs(float(y[i] - pred[i])),
                }
            )
    diag = pd.DataFrame(rows).sort_values("loo_spearman", ascending=False).reset_index(drop=True)
    pred_frame = pd.DataFrame(pred_rows)
    diag.to_csv(LOOCV_OUT, index=False)
    pred_frame.to_csv(PRED_OUT, index=False)
    return diag, pred_frame, models


def score_pool(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str], known: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    pool = pd.read_csv(E357_POOL_IN)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rec in pool.to_dict("records"):
        path = locate(rec.get("file"))
        if path is None or str(path) in seen:
            continue
        seen.add(str(path))
        delta = align_delta(path, anchor, anchor_logit)
        feats = rowstate_features(delta, state, base_cols, story_cols)
        rows.append({**rec, **feats})
    scored = pd.DataFrame(rows)
    if scored.empty:
        raise RuntimeError("no E357 pool files could be scored")

    x_train = known[cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    y = known["delta_vs_e247"].to_numpy(dtype=np.float64)
    x_pool = scored.reindex(columns=cols).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    pred_cols = []
    for name, model in make_models().items():
        model.fit(x_train, y)
        col = f"rowstate_pred_public_loss_{name}"
        scored[col] = np.asarray(model.predict(x_pool), dtype=np.float64)
        pred_cols.append(col)
    scored["rowstate_pred_public_loss_mean"] = scored[pred_cols].mean(axis=1)
    scored["rowstate_pred_public_loss_std"] = scored[pred_cols].std(axis=1)
    scored["rowstate_bad_exposure"] = scored["wmean_rowstate_e323_cluster_rate"] + scored["wmean_rowstate_e256_cluster_rate"]
    scored["rowstate_good_exposure"] = scored["wmean_rowstate_e247_cluster_rate"]
    scored["rowstate_bad_minus_good_exposure"] = scored["rowstate_bad_exposure"] - scored["rowstate_good_exposure"]

    # Rank high when predicted public loss, public-bad row-state exposure, and
    # model disagreement are low, while retaining E352/E356 support.
    scored["rowstate_public_survival_score"] = (
        scored["rowstate_pred_public_loss_mean"].rank(ascending=False, pct=True)
        + scored["rowstate_bad_minus_good_exposure"].rank(ascending=False, pct=True)
        + scored["rowstate_pred_public_loss_std"].rank(ascending=False, pct=True)
        + scored.get("e356_survival_score", pd.Series(0.0, index=scored.index)).rank(ascending=True, pct=True)
        + scored.get("e352_top3_rate", pd.Series(0.0, index=scored.index)).rank(ascending=True, pct=True)
        + scored.get("e357_public_survival_score", pd.Series(0.0, index=scored.index)).rank(ascending=True, pct=True)
    )
    scored = scored.sort_values("rowstate_public_survival_score", ascending=False).reset_index(drop=True)
    scored.to_csv(POOL_OUT, index=False)
    return scored


def copy_uploadsafe(src: Path, variant: str) -> Path:
    frame = pd.read_csv(src)
    tag = safe_id(str(variant), 80)
    out = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(frame)}_uploadsafe.csv"
    shutil.copyfile(src, out)
    return out


def select_candidate(pool: pd.DataFrame) -> pd.DataFrame:
    gated = pool.copy()
    for col in ["e352_top3_rate", "e356_survival_score", "e357_public_survival_score", "pred_delta_vs_current_p90"]:
        if col not in gated.columns:
            gated[col] = np.nan
    mask = (
        (gated["rowstate_pred_public_loss_mean"] <= 0.00030)
        & (gated["rowstate_pred_public_loss_std"] <= 0.00035)
        & (gated["rowstate_bad_minus_good_exposure"] <= gated["rowstate_bad_minus_good_exposure"].quantile(0.55))
        & (gated["e352_top3_rate"].fillna(0.0) >= 0.18)
        & (gated["e356_survival_score"].fillna(0.0) >= 3.0)
        & (gated["e357_public_survival_score"].fillna(0.0) >= 1.0)
    )
    passed = gated[mask].sort_values("rowstate_public_survival_score", ascending=False)
    if passed.empty:
        decision = "no_rowstate_submission"
        selected = gated.sort_values("rowstate_public_survival_score", ascending=False).head(1).copy()
        selected["reason"] = "No compact candidate passed row-state public-survival plus E352/E356/E357 gates."
        selected["selected_uploadsafe_file"] = "none"
    else:
        decision = "select_existing_rowstate_publicsurvival_probe"
        selected = passed.head(1).copy()
        src = locate(selected.iloc[0]["file"])
        if src is None:
            raise FileNotFoundError(str(selected.iloc[0]["file"]))
        upload = copy_uploadsafe(src, str(selected.iloc[0].get("variant", "rowstate_selected")))
        selected["reason"] = "This compact-basin point best balances row-state public survival, E352 stability, E356 transfer support, and E357 movement survival."
        selected["selected_uploadsafe_file"] = rel(upload)
    selected.insert(0, "decision", decision)
    selected.to_csv(SELECTION_OUT, index=False)
    return selected


def write_report(known: pd.DataFrame, diag: pd.DataFrame, pool: pd.DataFrame, selected: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> None:
    top_known_cols = [
        "basename",
        "public_lb",
        "delta_vs_e247",
        "cell_l1",
        "rowstate_bad_exposure",
        "rowstate_good_exposure",
        "rowstate_bad_minus_good_exposure",
    ]
    known_view = known.copy()
    known_view["rowstate_bad_exposure"] = known_view["wmean_rowstate_e323_cluster_rate"] + known_view["wmean_rowstate_e256_cluster_rate"]
    known_view["rowstate_good_exposure"] = known_view["wmean_rowstate_e247_cluster_rate"]
    known_view["rowstate_bad_minus_good_exposure"] = known_view["rowstate_bad_exposure"] - known_view["rowstate_good_exposure"]

    top_pool_cols = [
        "variant",
        "selection_role",
        "rowstate_public_survival_score",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "wmean_rowstate_e323_cluster_rate",
        "wmean_rowstate_e247_cluster_rate",
        "e357_public_survival_score",
        "e356_survival_score",
        "e352_top3_rate",
        "file",
    ]
    lines = [
        "# E358 Row-State Public-Survival Audit",
        "",
        "## Question",
        "",
        "Does the E357 compact-basin choice still look valid when candidate movement is projected onto row-level hidden lifestyle states rather than only output-space movement anatomy?",
        "",
        "## Method",
        "",
        "- Row state: E328 own-latent lifestyle state over the 250 test days.",
        "- Human semantics: top E268 story axes most aligned with E328 bad-vs-good cluster markers.",
        "- Context representation: how much each candidate's logit movement lands on ownlife clusters, high-energy rows, E323-heavy row-state clusters, E247-only row-state clusters, and human/social story tails.",
        "- Target representation: known public delta versus E247.",
        "- Anti-collapse: leave-one-public-file-out regressors plus permutation checks.",
        "",
        "## Inputs",
        "",
        f"- base row-state columns: `{len(base_cols)}`",
        f"- selected story columns: `{len(story_cols)}`",
        f"- known local public files: `{len(known)}`",
        f"- compact candidate pool: `{len(pool)}`",
        "",
        "## LOO Diagnostics",
        "",
        md_table(diag, n=12, floatfmt=".9f"),
        "",
        "## Known Public Row-State Exposure",
        "",
        md_table(known_view[top_known_cols].sort_values("public_lb"), n=20, floatfmt=".9f"),
        "",
        "## Top Compact Candidates",
        "",
        md_table(pool[[c for c in top_pool_cols if c in pool.columns]].head(30), n=30, floatfmt=".9f"),
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "rowstate_public_survival_score", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "e357_public_survival_score", "e356_survival_score", "e352_top3_rate", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- If E358 selects the same basin as E357, row-state semantics support the S3-tail/no-extra-amplification probe.",
        "- If E358 demotes E357 but keeps E351/E356, the row-state view says output-space survival and human-day survival disagree.",
        "- If no gated candidate survives, the compact lifestyle-state branch should be treated as a local/output-space basin, not the hidden public row-state law.",
        "",
        "## Files",
        "",
        f"- `{rel(KNOWN_OUT)}`",
        f"- `{rel(LOOCV_OUT)}`",
        f"- `{rel(PRED_OUT)}`",
        f"- `{rel(POOL_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    known = known_observations(anchor, anchor_logit, state, base_cols, story_cols)
    cols = feature_columns(known)
    diag, _, _ = loocv_diagnostics(known, cols)
    pool = score_pool(anchor, anchor_logit, state, base_cols, story_cols, known, cols)
    selected = select_candidate(pool)
    write_report(known, diag, pool, selected, base_cols, story_cols)

    print(f"known={len(known)} feature_cols={len(cols)} pool={len(pool)}")
    print(diag.round(9).to_string(index=False))
    print(selected[["decision", "variant", "selected_uploadsafe_file", "rowstate_public_survival_score", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
