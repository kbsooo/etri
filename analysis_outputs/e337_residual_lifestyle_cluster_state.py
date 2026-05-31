#!/usr/bin/env python3
"""E337: residual lifestyle-cluster state.

E336 rejected the direct output-space reversal of public-bad movement.  This
experiment moves one level upstream:

    context = human/social/raw/JEPA views
    target  = target-residual lifestyle state predicted by E330
    state   = clusters over those residual-state latents
    action  = tiny E247 edits only if cluster state survives label/null stress

The goal is not raw feature reconstruction and not another blind blend.  The
question is whether repeated lifestyle episodes can be recovered before
probability materialization, while E323/E216 public-bad movement remains a
veto coordinate.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import entropy
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import log_loss, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e337_residual_cluster_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id  # noqa: E402
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    cv_logloss,
    fit_logistic_predict,
    fit_ridge_full_predict,
    groups_for,
    oof_proba,
    oof_ridge_scalar,
)
from e331_residual_state_localization import train_test_state  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 337
EPS = 1.0e-12
NULL_REPS = 8
MOVEMENT_NULL_REPS = 4
TOP_NULL_CANDIDATES = 12
MAX_SOURCE_ROWS = 18
MAX_GATE_ROWS = 10
CAP = 0.11

E216 = OUT / "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"

LATENT_OUT = OUT / "e337_residual_lifestyle_cluster_latents.csv"
VIEW_OUT = OUT / "e337_residual_lifestyle_cluster_view_r2.csv"
CLUSTER_OUT = OUT / "e337_residual_lifestyle_cluster_summary.csv"
STRESS_OUT = OUT / "e337_residual_lifestyle_cluster_label_stress.csv"
CANDIDATE_OUT = OUT / "e337_residual_lifestyle_cluster_candidates.csv"
SCORE_OUT = OUT / "e337_residual_lifestyle_cluster_scores.csv"
ANATOMY_OUT = OUT / "e337_residual_lifestyle_cluster_anatomy.csv"
MOVE_NULL_OUT = OUT / "e337_residual_lifestyle_cluster_movement_nulls.csv"
REPORT_OUT = OUT / "e337_residual_lifestyle_cluster_report.md"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def logits_for(path: Path, sample: pd.DataFrame) -> np.ndarray:
    return logit(load_sub_frame(path, sample)[TARGETS].to_numpy(dtype=np.float64))


def target_abs(delta: np.ndarray) -> dict[str, float]:
    total = float(np.sum(np.abs(delta))) + EPS
    out: dict[str, float] = {}
    for i, target in enumerate(TARGETS):
        val = float(np.sum(np.abs(delta[:, i])))
        out[f"abs_{target}"] = val
        out[f"share_{target}"] = val / total
    return out


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    return float((aa @ bb) / (np.linalg.norm(aa) * np.linalg.norm(bb) + EPS))


def safe_logit_prob(p: np.ndarray) -> np.ndarray:
    return logit(clip_prob(np.asarray(p, dtype=np.float64)))


def source_rows() -> pd.DataFrame:
    src = pd.read_csv(OUT / "e330_target_residual_lifestyle_latent_summary.csv")
    src = src.sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).head(MAX_SOURCE_ROWS)
    return src.reset_index(drop=True)


def build_residual_latents() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    train, test, train_views, test_views = train_test_state()
    base_x_train, _base_x_test = base_label_matrix_all(train, test)
    src = source_rows()
    train_cols: dict[str, np.ndarray] = {}
    test_cols: dict[str, np.ndarray] = {}
    latent_rows: list[dict[str, Any]] = []
    for idx, rec in src.iterrows():
        target = str(rec["target"])
        view_id = str(rec["view_id"])
        split_name = str(rec["split"])
        y = train[target].astype(int).to_numpy()
        groups = groups_for(train, split_name).reset_index(drop=True)
        base_oof = oof_proba(base_x_train, y, groups)
        teacher = y.astype(float) - base_oof
        pred_train, _pred_full, r2 = oof_ridge_scalar(train_views[view_id], teacher, groups)
        pred_test = fit_ridge_full_predict(train_views[view_id], teacher, test_views[view_id])
        col = f"rs{idx:02d}_{target}_{view_id}_{split_name}"
        train_cols[col] = pred_train
        test_cols[col] = pred_test
        latent_rows.append(
            {
                "latent_col": col,
                "target": target,
                "view_id": view_id,
                "split": split_name,
                "source_delta": float(rec["actual_delta"]),
                "source_dominance": float(rec["dominance"]),
                "student_oof_r2": float(r2),
                "train_std": float(np.std(pred_train)),
                "test_std": float(np.std(pred_test)),
                "test_abs_p90": float(np.quantile(np.abs(pred_test), 0.90)),
            }
        )
    train_lat = pd.DataFrame(train_cols)
    test_lat = pd.DataFrame(test_cols)
    latent_df = pd.DataFrame(latent_rows)
    out = pd.concat(
        [
            pd.concat([train[KEYS + ["split", "dateblock_group"]], test[KEYS + ["split", "dateblock_group"]]], ignore_index=True),
            pd.concat([train_lat, test_lat], ignore_index=True),
        ],
        axis=1,
    )
    latent_df.to_csv(LATENT_OUT, index=False)
    out.to_parquet(OUT / "e337_residual_lifestyle_cluster_latent_matrix.parquet", index=False)
    return train_lat, test_lat, train_views, test_views


def oof_ridge_multi(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> tuple[np.ndarray, float]:
    x = x.reset_index(drop=True)
    y = np.asarray(y, dtype=np.float64)
    pred = np.zeros_like(y, dtype=np.float64)
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(x, groups=groups):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0))
        model.fit(x.iloc[tr_idx], y[tr_idx])
        pred[va_idx] = model.predict(x.iloc[va_idx])
    try:
        score = float(r2_score(y, pred, multioutput="variance_weighted"))
    except ValueError:
        score = 0.0
    return pred, score


def view_diagnostics(train_lat: pd.DataFrame, train_views: dict[str, pd.DataFrame], train: pd.DataFrame) -> pd.DataFrame:
    y = train_lat.to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for view_id in ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]:
        x = train_views[view_id]
        for split_name in ["subject", "dateblock"]:
            groups = groups_for(train, split_name).reset_index(drop=True)
            pred, r2 = oof_ridge_multi(x, y, groups)
            resid = y - pred
            rows.append(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "context_cols": int(x.shape[1]),
                    "latent_dims": int(y.shape[1]),
                    "oof_latent_r2": r2,
                    "resid_energy_mean": float(np.sqrt(np.mean(resid**2, axis=1)).mean()),
                    "pred_energy_mean": float(np.sqrt(np.mean(pred**2, axis=1)).mean()),
                }
            )
    out = pd.DataFrame(rows).sort_values("oof_latent_r2", ascending=False)
    out.to_csv(VIEW_OUT, index=False)
    return out


def z_latent(train_lat: pd.DataFrame, test_lat: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    z_train = pipe.fit_transform(train_lat)
    z_test = pipe.transform(test_lat)
    return np.asarray(z_train, dtype=np.float64), np.asarray(z_test, dtype=np.float64)


def cluster_entropy(labels: np.ndarray) -> float:
    vc = pd.Series(labels).value_counts(normalize=True).to_numpy(dtype=np.float64)
    if len(vc) <= 1:
        return 0.0
    return float(entropy(vc) / np.log(len(vc)))


def make_clusters(train_z: np.ndarray, test_z: np.ndarray, train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, tuple[np.ndarray, np.ndarray]]]:
    rows: list[dict[str, Any]] = []
    store: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for k in [4, 6, 8, 10, 12]:
        km = KMeans(n_clusters=k, random_state=stable_seed("kmeans", k), n_init=32)
        tr_lab = km.fit_predict(train_z)
        te_lab = km.predict(test_z)
        store[k] = (tr_lab, te_lab)
        for split_name, labels, frame in [("train", tr_lab, train), ("test", te_lab, test)]:
            vc = pd.Series(labels).value_counts().sort_index()
            rows.append(
                {
                    "k": k,
                    "split": split_name,
                    "rows": int(len(labels)),
                    "cluster_entropy": cluster_entropy(labels),
                    "min_cluster_rows": int(vc.min()),
                    "max_cluster_rows": int(vc.max()),
                    "subject_entropy": float(frame.groupby("subject_id").size().pipe(lambda s: entropy(s / s.sum()) / np.log(len(s)))),
                    "dateblock_entropy": float(frame.groupby("dateblock_group").size().pipe(lambda s: entropy(s / s.sum()) / np.log(len(s)))),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(CLUSTER_OUT, index=False)
    return out, store


def align_dummies(train_labels: np.ndarray, test_labels: np.ndarray, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    tr = pd.get_dummies(pd.Series(train_labels, name=prefix).astype(str), prefix=prefix, dtype=float)
    te = pd.get_dummies(pd.Series(test_labels, name=prefix).astype(str), prefix=prefix, dtype=float)
    tr, te = tr.align(te, join="outer", axis=1, fill_value=0.0)
    return tr.reset_index(drop=True), te.reset_index(drop=True)


def shuffle_labels(labels: np.ndarray, mode: str, groups: pd.Series, rng: np.random.Generator) -> np.ndarray:
    arr = np.asarray(labels).copy()
    if mode == "row":
        return arr[rng.permutation(len(arr))]
    out = arr.copy()
    for _, idx in groups.groupby(groups).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
    return out


def cv_logloss_with_clusters(base_x: pd.DataFrame, labels: np.ndarray, y: np.ndarray, groups: pd.Series, prefix: str) -> float:
    dummies = pd.get_dummies(pd.Series(labels, name=prefix).astype(str), prefix=prefix, dtype=float)
    x = pd.concat([base_x.reset_index(drop=True), dummies.reset_index(drop=True)], axis=1)
    return cv_logloss(x, y, groups)


def full_delta_with_clusters(
    base_x_train: pd.DataFrame,
    base_x_test: pd.DataFrame,
    train_labels: np.ndarray,
    test_labels: np.ndarray,
    y: np.ndarray,
    prefix: str,
) -> np.ndarray:
    tr_dum, te_dum = align_dummies(train_labels, test_labels, prefix)
    x_aug_train = pd.concat([base_x_train.reset_index(drop=True), tr_dum], axis=1)
    x_aug_test = pd.concat([base_x_test.reset_index(drop=True), te_dum], axis=1)
    base_p = fit_logistic_predict(base_x_train, y, base_x_test)
    aug_p = fit_logistic_predict(x_aug_train, y, x_aug_test)
    return safe_logit_prob(aug_p) - safe_logit_prob(base_p)


def cluster_label_stress(
    store: dict[int, tuple[np.ndarray, np.ndarray]],
    train: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    base_x_train, base_x_test = base_label_matrix_all(train, test)
    stress_rows: list[dict[str, Any]] = []
    materializers: list[dict[str, Any]] = []
    null_groups = {
        "row": pd.Series(["all"] * len(train)),
        "subject": groups_for(train, "subject").reset_index(drop=True),
        "dateblock": groups_for(train, "dateblock").reset_index(drop=True),
    }
    for k, (tr_lab, te_lab) in store.items():
        prefix = f"cl{k}"
        for split_name in ["subject", "dateblock"]:
            groups = groups_for(train, split_name).reset_index(drop=True)
            for target in TARGETS:
                y = train[target].astype(int).to_numpy()
                base_loss = cv_logloss(base_x_train, y, groups)
                actual_loss = cv_logloss_with_clusters(base_x_train, tr_lab, y, groups, prefix)
                actual_delta = float(actual_loss - base_loss)
                null_vals: list[float] = []
                rng = np.random.default_rng(stable_seed("cluster_null", k, split_name, target))
                for mode, mgroups in null_groups.items():
                    for rep in range(NULL_REPS):
                        nul = shuffle_labels(tr_lab, mode, mgroups, rng)
                        val = float(cv_logloss_with_clusters(base_x_train, nul, y, groups, f"{prefix}_n") - base_loss)
                        null_vals.append(val)
                null_arr = np.asarray(null_vals, dtype=np.float64)
                dominance = float(np.mean(actual_delta < null_arr))
                placebo_adjusted = actual_delta - float(np.median(null_arr))
                train_counts = pd.Series(tr_lab).value_counts()
                test_counts = pd.Series(te_lab).value_counts()
                gate = bool(actual_delta < -0.0008 and dominance >= 0.80 and placebo_adjusted < -0.0004)
                rec = {
                    "k": k,
                    "target": target,
                    "split": split_name,
                    "base_loss": base_loss,
                    "aug_loss": actual_loss,
                    "actual_delta": actual_delta,
                    "null_best": float(np.min(null_arr)),
                    "null_median": float(np.median(null_arr)),
                    "null_q20": float(np.quantile(null_arr, 0.20)),
                    "dominance": dominance,
                    "placebo_adjusted_vs_median": placebo_adjusted,
                    "train_cluster_entropy": cluster_entropy(tr_lab),
                    "test_cluster_entropy": cluster_entropy(te_lab),
                    "train_min_cluster_rows": int(train_counts.min()),
                    "test_min_cluster_rows": int(test_counts.min()),
                    "gate": gate,
                }
                stress_rows.append(rec)
                if gate:
                    delta = full_delta_with_clusters(base_x_train, base_x_test, tr_lab, te_lab, y, prefix)
                    materializers.append({**rec, "delta": delta, "train_labels": tr_lab, "test_labels": te_lab})
    out = pd.DataFrame(stress_rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False])
    out.to_csv(STRESS_OUT, index=False)
    return out, materializers


def bad_axes(base: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sample = base[KEYS]
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    e323_bad = logits_for(E323, sample) - base_logit
    e216_bad = logits_for(E216, sample) - base_logit
    return base_logit, e323_bad, e216_bad


def cell_bad_veto(delta: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray, strength: float = 0.25) -> np.ndarray:
    out = np.asarray(delta, dtype=np.float64).copy()
    bad_mag = np.maximum(np.abs(e323_bad), np.abs(e216_bad))
    same_sign = ((out * e323_bad) > 0.0) | ((out * e216_bad) > 0.0)
    for j in range(out.shape[1]):
        thr = float(np.quantile(bad_mag[:, j], 0.75))
        mask = same_sign[:, j] & (bad_mag[:, j] >= thr) & (np.abs(out[:, j]) > EPS)
        out[mask, j] *= strength
    return out


def center_by_target(delta: np.ndarray) -> np.ndarray:
    out = np.asarray(delta, dtype=np.float64).copy()
    for j in range(out.shape[1]):
        nz = np.abs(out[:, j]) > EPS
        if np.any(nz):
            out[nz, j] -= float(np.mean(out[nz, j]))
    return out


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = expit(np.clip(base_logit + np.clip(delta, -CAP, CAP), -40.0, 40.0))
    path = OUT / f"submission_e337_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(materializers: list[dict[str, Any]], base: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], np.ndarray, np.ndarray, np.ndarray]:
    base_logit, e323_bad, e216_bad = bad_axes(base)
    chosen = sorted(materializers, key=lambda r: (float(r["actual_delta"]), -float(r["dominance"])))[:MAX_GATE_ROWS]
    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    if not chosen:
        pd.DataFrame().to_csv(CANDIDATE_OUT, index=False)
        return pd.DataFrame(), paths, base_logit, e323_bad, e216_bad
    configs: list[tuple[str, int | str]] = [("top1", 1), ("top3", 3), ("top6", 6), ("topall", "all")]
    families = ["raw_cluster", "bad_veto", "target_centered", "veto_centered"]
    scales = [0.20, 0.35, 0.55, 0.80]
    for cfg_name, n in configs:
        selected = chosen if n == "all" else chosen[: int(n)]
        raw_delta = np.zeros_like(base_logit)
        source_desc: list[str] = []
        for rec in selected:
            j = TARGETS.index(str(rec["target"]))
            raw_delta[:, j] += np.asarray(rec["delta"], dtype=np.float64)
            source_desc.append(f"k{rec['k']}:{rec['target']}:{rec['split']}:{rec['actual_delta']:.5f}")
        variants = {
            "raw_cluster": raw_delta,
            "bad_veto": cell_bad_veto(raw_delta, e323_bad, e216_bad),
            "target_centered": center_by_target(raw_delta),
            "veto_centered": center_by_target(cell_bad_veto(raw_delta, e323_bad, e216_bad)),
        }
        for family in families:
            direction = variants[family]
            for scale in scales:
                delta = direction * float(scale)
                if float(np.sum(np.abs(delta))) <= EPS:
                    continue
                candidate_id = f"{family}_{cfg_name}_s{scale:.2f}"
                path = write_candidate(base, base_logit, delta, candidate_id)
                paths.append(path)
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "file": rel(path),
                        "basename": path.name,
                        "family": family,
                        "config": cfg_name,
                        "scale": float(scale),
                        "sources": ";".join(source_desc),
                        "source_count": int(len(selected)),
                        "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                        "changed_cells": int((np.abs(delta) > EPS).sum()),
                        "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                        "max_abs_logit_delta": float(np.max(np.abs(delta))),
                        "l1_logit_delta": float(np.sum(np.abs(delta))),
                        "cos_with_e323_bad": cos(delta, e323_bad),
                        "cos_with_e216_bad": cos(delta, e216_bad),
                        **target_abs(delta),
                    }
                )
    cand = pd.DataFrame(rows).sort_values(["family", "config", "scale"]).reset_index(drop=True)
    cand.to_csv(CANDIDATE_OUT, index=False)
    return cand, paths, base_logit, e323_bad, e216_bad


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(p) for p in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": cos(delta, e323_bad),
                "cos_with_e216_bad": cos(delta, e216_bad),
                "signed_bad_overlap": float(np.mean((delta * e323_bad > 0.0) | (delta * e216_bad > 0.0))),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "cos_with_e216_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def make_null_delta(delta: np.ndarray, mode: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return arr[rng.permutation(arr.shape[0]), :]
    if mode == "target_perm":
        return arr[:, rng.permutation(arr.shape[1])]
    if mode == "sign_flip":
        return -arr
    if mode == "row_sign":
        return arr * rng.choice([-1.0, 1.0], size=(arr.shape[0], 1))
    if mode == "cell_perm":
        flat = arr.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(arr.shape)
    raise ValueError(mode)


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(TOP_NULL_CANDIDATES)
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    for rec in chosen.to_dict("records"):
        path = ROOT / str(rec.get("file_meta", rec.get("file", "")))
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm"]:
            for rep in range(MOVEMENT_NULL_REPS):
                nd = make_null_delta(delta, mode, stable_seed(rec["basename"], mode, rep))
                npth = write_candidate(base, base_logit, nd, f"null_{Path(rec['basename']).stem}_{mode}_{rep}")
                null_paths.append(npth)
                null_rows.append({"basename": rec["basename"], "null_basename": npth.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True])
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(
    latent: pd.DataFrame,
    view: pd.DataFrame,
    clusters: pd.DataFrame,
    stress: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anat: pd.DataFrame,
    nulls: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(nulls):
        null_safe = nulls[
            (nulls["actual_strict_promote"].astype(bool))
            & (nulls["actual_p90_dominance"] >= 0.70)
            & (nulls["null_strict_promote_rate"] <= 0.05)
        ]
    lines = [
        "# E337 Residual Lifestyle-Cluster State",
        "",
        "## Question",
        "",
        "Can target-residual lifestyle states be clustered into repeated hidden episodes that survive subject/dateblock label stress, while E323/E216 public-bad anatomy only acts as a veto?",
        "",
        "## Latent Sources",
        "",
        md_table(latent.sort_values(["source_delta", "source_dominance"], ascending=[True, False]), n=25),
        "",
        "## Masked-Context JEPA Diagnostic",
        "",
        md_table(view, n=20),
        "",
        "## Cluster Geometry",
        "",
        md_table(clusters, n=20),
        "",
        "## Label/Null Stress",
        "",
        f"- gated cluster-target rows: `{int(stress['gate'].sum()) if len(stress) else 0}`",
        "",
        md_table(stress, n=30),
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(null_safe)}`",
        "",
        md_table(candidates, n=30),
        "",
        "## Public-Free Selector Scores",
        "",
        md_table(
            non_current.sort_values(["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, False, True, True])
            if len(non_current)
            else non_current,
            n=35,
        ),
        "",
        "## Anatomy",
        "",
        md_table(anat, n=35),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=20),
        "",
        "## Decision",
        "",
    ]
    if len(null_safe):
        lines.append("At least one E337 candidate clears selector and movement-null gates. Treat it as a submission candidate only after checking public-bad anatomy and candidate diversity.")
    elif len(promoted):
        lines.append("E337 creates selector-promoted cluster-state movement, but movement-null stress does not certify it yet. Do not submit without a stricter null-safe pass.")
    elif int(stress["gate"].sum()) if len(stress) else 0:
        lines.append("Residual lifestyle clusters are label-useful under subject/dateblock nulls, but the action translator still fails public-free visibility. This supports hidden-state existence and rejects current cluster-prior materialization.")
    else:
        lines.append("Residual lifestyle clustering does not survive label/null stress strongly enough. The current residual-state axes do not form a stable episode latent.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{LATENT_OUT.name}`",
            f"- `{VIEW_OUT.name}`",
            f"- `{CLUSTER_OUT.name}`",
            f"- `{STRESS_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train, test, _train_views, _test_views = train_test_state()
    train_lat, test_lat, train_views, _ = build_residual_latents()
    latent = pd.read_csv(LATENT_OUT)
    view = view_diagnostics(train_lat, train_views, train)
    train_z, test_z = z_latent(train_lat, test_lat)
    clusters, store = make_clusters(train_z, test_z, train, test)
    stress, materializers = cluster_label_stress(store, train, test)
    base = load_current()
    candidates, paths, base_logit, e323_bad, e216_bad = materialize_candidates(materializers, base)
    scores = score_paths(paths)
    anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    nulls = movement_null_stress(scores, candidates, base, base_logit)
    write_report(latent, view, clusters, stress, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]
        print(non_current[cols].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
