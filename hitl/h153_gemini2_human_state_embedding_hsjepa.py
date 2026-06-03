#!/usr/bin/env python3
"""H153: Gemini Embedding 2 human-state narrative latent HS-JEPA.

This experiment does not embed raw numbers directly.  It first translates each
test row into a compact human-state narrative, then embeds that narrative with
Gemini Embedding 2.  The resulting semantic row latent is used as bundle
features for the public/private listener equation.

The key question is whether a human-readable lifestyle-state representation
adds listener/toxicity structure beyond the existing subject/date/row-order
bundles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h153_gemini2_human_state_embedding_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H152_PATH = HITL / "h152_source_responsibility_route_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h152mod_h153", H152_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H152_PATH}")
h152mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h152mod
SPEC.loader.exec_module(h152mod)

h150mod = h152mod.h150mod
h149mod = h152mod.h149mod
h148mod = h152mod.h148mod
h085mod = h152mod.h085mod

TARGETS = h152mod.TARGETS
KEYS = h149mod.KEYS
BASE_FILE = h152mod.BASE_FILE
EPS = h149mod.EPS
TOL = h152mod.TOL

MODEL_NAME = "gemini-embedding-2"
OUTPUT_DIM = 768
EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:embedContent"

SOURCE_FILES = [
    "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv",
    "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv",
    "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv",
    "submission_h075_antibad_transport_f6863945_uploadsafe.csv",
    "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
    "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
    "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
    "submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv",
    "submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv",
]


@dataclass(frozen=True)
class H153Spec:
    name: str
    max_cells: int
    max_rows: int
    max_per_target: int
    max_per_subject: int
    max_per_source: int
    amp: float
    min_semantic_benefit: float
    min_base_benefit: float
    max_h088_alignment: float
    description: str


SPECS = [
    H153Spec(
        name="semantic_listener_balanced",
        max_cells=340,
        max_rows=150,
        max_per_target=78,
        max_per_subject=95,
        max_per_source=120,
        amp=0.58,
        min_semantic_benefit=0.0,
        min_base_benefit=-1.0e-5,
        max_h088_alignment=0.72,
        description="Gemini semantic listener with loose base-listener support",
    ),
    H153Spec(
        name="semantic_listener_safe",
        max_cells=260,
        max_rows=125,
        max_per_target=62,
        max_per_subject=75,
        max_per_source=90,
        amp=0.54,
        min_semantic_benefit=0.0,
        min_base_benefit=0.0,
        max_h088_alignment=0.50,
        description="Gemini semantic listener only where base listener also agrees",
    ),
]


def locate(name: str | Path) -> Path | None:
    return h085mod.locate(name)


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(x)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(x)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(values, high=high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def load_sub(path: Path | str, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return h085mod.load_sub(path, sample)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    h085mod.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    return h085mod.validate_submission(path, sample, base_prob)


def movement_from_file(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(-1)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h153_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h153_gemini2_*.csv"):
        path.unlink()


def prob_tag(value: float) -> str:
    if value < 0.12:
        return "very_low"
    if value < 0.35:
        return "low"
    if value < 0.65:
        return "mid"
    if value < 0.88:
        return "high"
    return "very_high"


def date_story(row: pd.Series, row_idx: int, n_rows: int) -> list[str]:
    lifelog = pd.to_datetime(row["lifelog_date"])
    dow = int(lifelog.dayofweek)
    day = int(lifelog.day)
    out = []
    if dow >= 5:
        out.append("weekend_recovery_or_social_disruption")
    elif dow == 4:
        out.append("friday_evening_transition")
    elif dow == 0:
        out.append("monday_work_rhythm_reset")
    else:
        out.append("weekday_routine_pressure")
    if abs(day - 25) <= 1:
        out.append("possible_payday_or_monthly_spending_window_25")
    if abs(day - 10) <= 1:
        out.append("possible_payday_or_settlement_window_10")
    if day <= 3:
        out.append("month_start_schedule_reset")
    if day >= 28:
        out.append("month_end_admin_or_financial_pressure")
    frac = row_idx / max(1, n_rows - 1)
    if frac < 0.20:
        out.append("early_sequence_regime")
    elif frac > 0.80:
        out.append("late_sequence_regime")
    else:
        out.append("middle_sequence_regime")
    return out


def source_row_summary(
    source_probs: dict[str, np.ndarray],
    base_prob: np.ndarray,
    row_idx: int,
) -> list[str]:
    out = []
    for name, prob in source_probs.items():
        diff = prob[row_idx] - base_prob[row_idx]
        changed = np.flatnonzero(np.abs(diff) > TOL)
        if len(changed) == 0:
            continue
        top = changed[np.argsort(-np.abs(diff[changed]))[:4]]
        parts = [f"{TARGETS[i]}:{'up' if diff[i] > 0 else 'down'}:{abs(diff[i]):.3f}" for i in top]
        label = name.replace("submission_", "").replace("_uploadsafe.csv", "")
        out.append(f"{label} changes " + ",".join(parts))
    return out[:8]


def make_row_narratives(sample: pd.DataFrame, base_prob: np.ndarray, source_probs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for row_idx, row in sample.reset_index(drop=True).iterrows():
        probs = base_prob[row_idx]
        q_mean = float(np.mean(probs[:3]))
        s_mean = float(np.mean(probs[3:]))
        target_profile = ", ".join(f"{t}={probs[i]:.3f}/{prob_tag(float(probs[i]))}" for i, t in enumerate(TARGETS))
        q_s_relation = "Q_dominant" if q_mean > s_mean + 0.08 else "S_dominant" if s_mean > q_mean + 0.08 else "Q_S_balanced"
        stories = date_story(row, row_idx, len(sample))
        source_story = source_row_summary(source_probs, base_prob, row_idx)
        text = (
            "task: classification | query: "
            "Infer hidden human lifestyle and sleep-state regime for one competition row. "
            f"subject={row['subject_id']}; sleep_date={pd.to_datetime(row['sleep_date']).date()}; "
            f"lifelog_date={pd.to_datetime(row['lifelog_date']).date()}; "
            f"calendar_state={','.join(stories)}; "
            f"row_index={row_idx}; row_fraction={row_idx / max(1, len(sample)-1):.3f}; "
            f"base_target_profile=[{target_profile}]; "
            f"q_mean={q_mean:.3f}; s_mean={s_mean:.3f}; relation={q_s_relation}; "
            f"source_action_disagreement=[{'; '.join(source_story) if source_story else 'none'}]. "
            "Represent this as a latent human-state route, listener responsibility, "
            "action-health risk, anti-shortcut risk, and safe row-target correction tendency."
        )
        rows.append(
            {
                "row": int(row_idx),
                "subject_id": row["subject_id"],
                "sleep_date": row["sleep_date"],
                "lifelog_date": row["lifelog_date"],
                "narrative": text,
                "narrative_sha1": hashlib.sha1(text.encode("utf-8")).hexdigest(),
                "calendar_state": ",".join(stories),
                "q_mean": q_mean,
                "s_mean": s_mean,
                "q_s_relation": q_s_relation,
            }
        )
    return pd.DataFrame(rows)


def parse_embedding_response(payload: dict[str, object]) -> list[float]:
    if "embedding" in payload:
        emb = payload["embedding"]
        if isinstance(emb, dict) and "values" in emb:
            return list(emb["values"])  # type: ignore[arg-type]
    if "embeddings" in payload:
        embeddings = payload["embeddings"]
        if isinstance(embeddings, list) and embeddings:
            first = embeddings[0]
            if isinstance(first, dict) and "values" in first:
                return list(first["values"])  # type: ignore[arg-type]
    raise RuntimeError(f"unexpected embedding response keys: {sorted(payload.keys())}")


def call_gemini_embedding(text: str, api_key: str, retries: int = 4) -> list[float]:
    body = {
        "model": f"models/{MODEL_NAME}",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": OUTPUT_DIM,
    }
    data = json.dumps(body).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(
            EMBED_URL,
            data=data,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return parse_embedding_response(payload)
        except urllib.error.HTTPError as exc:
            err = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"Gemini embedding HTTP {exc.code}: {err[:500]}") from exc
        except Exception:
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def local_tfidf_fallback(texts: list[str]) -> np.ndarray:
    vec = TfidfVectorizer(max_features=2048, ngram_range=(1, 2), lowercase=True)
    x = vec.fit_transform(texts)
    n_comp = min(128, max(2, min(x.shape) - 1))
    emb = TruncatedSVD(n_components=n_comp, random_state=153).fit_transform(x)
    return np.asarray(emb, dtype=np.float64)


def load_or_create_embeddings(narratives: pd.DataFrame, allow_fallback: bool) -> tuple[np.ndarray, dict[str, object]]:
    cache = OUT / "h153_gemini2_row_embeddings.npy"
    meta_path = OUT / "h153_embedding_meta.json"
    combined_hash = hashlib.sha1("".join(narratives["narrative_sha1"].astype(str)).encode("utf-8")).hexdigest()
    if cache.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        emb = np.load(cache)
        if meta.get("combined_narrative_hash") == combined_hash and emb.shape[0] == len(narratives):
            return emb, meta

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    texts = narratives["narrative"].astype(str).tolist()
    if api_key:
        vectors = []
        for i, text in enumerate(texts):
            vectors.append(call_gemini_embedding(text, api_key))
            if (i + 1) % 25 == 0:
                print(f"embedded {i + 1}/{len(texts)} rows with {MODEL_NAME}")
            time.sleep(0.04)
        emb = np.asarray(vectors, dtype=np.float64)
        meta = {
            "embedding_source": MODEL_NAME,
            "output_dim": int(emb.shape[1]),
            "n_rows": int(emb.shape[0]),
            "combined_narrative_hash": combined_hash,
            "api_key_stored": False,
        }
    elif allow_fallback:
        emb = local_tfidf_fallback(texts)
        meta = {
            "embedding_source": "local_tfidf_svd_fallback",
            "output_dim": int(emb.shape[1]),
            "n_rows": int(emb.shape[0]),
            "combined_narrative_hash": combined_hash,
            "api_key_stored": False,
        }
    else:
        raise RuntimeError("GEMINI_API_KEY is not set; refusing to create non-Gemini H153 embeddings")

    np.save(cache, emb)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return emb, meta


def normalized_embedding(emb: np.ndarray) -> np.ndarray:
    x = np.asarray(emb, dtype=np.float64)
    x = x - np.nanmean(x, axis=0, keepdims=True)
    sd = np.nanstd(x, axis=0, keepdims=True)
    x = np.divide(x, np.where(sd < 1.0e-8, 1.0, sd))
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    return np.divide(x, np.where(norm < 1.0e-8, 1.0, norm))


def add_feature(features: list[h149mod.BundleFeature], name: str, family: str, mask: np.ndarray) -> None:
    idx = np.flatnonzero(mask)
    if len(idx):
        features.append(h149mod.BundleFeature(name=name, family=family, indices=idx.astype(int)))


def semantic_bundle_features(sample: pd.DataFrame, base_prob: np.ndarray, emb: np.ndarray) -> tuple[list[h149mod.BundleFeature], pd.DataFrame]:
    n_rows, n_targets = base_prob.shape
    x = normalized_embedding(emb)
    n_pca = min(12, x.shape[1], x.shape[0] - 1)
    pcs = PCA(n_components=n_pca, random_state=153).fit_transform(x)
    rows = []
    features: list[h149mod.BundleFeature] = []
    row_grid = np.repeat(np.arange(n_rows), n_targets)
    target_grid = np.tile(np.arange(n_targets), n_rows)
    q_mask = target_grid <= 2
    s_mask = target_grid >= 3

    for k in [8, 12, 16]:
        labels = KMeans(n_clusters=k, n_init=40, random_state=153 + k).fit_predict(pcs[:, : min(8, n_pca)])
        for row, label in enumerate(labels):
            rows.append({"row": int(row), "cluster_k": int(k), "cluster": int(label)})
        label_grid = np.repeat(labels, n_targets)
        for label in sorted(set(labels)):
            cmask = label_grid == label
            add_feature(features, f"gemini2_cluster{k}={label}|Q", "gemini2_cluster_group", cmask & q_mask)
            add_feature(features, f"gemini2_cluster{k}={label}|S", "gemini2_cluster_group", cmask & s_mask)
            for tidx, target in enumerate(TARGETS):
                add_feature(features, f"gemini2_cluster{k}={label}|target={target}", "gemini2_cluster_target", cmask & (target_grid == tidx))

    for pc in range(min(6, n_pca)):
        vals = pcs[:, pc]
        q20, q40, q60, q80 = np.quantile(vals, [0.20, 0.40, 0.60, 0.80])
        bins = np.digitize(vals, [q20, q40, q60, q80])
        bin_grid = np.repeat(bins, n_targets)
        for b in range(5):
            bmask = bin_grid == b
            add_feature(features, f"gemini2_pc{pc}_bin{b}|Q", "gemini2_pc_group", bmask & q_mask)
            add_feature(features, f"gemini2_pc{pc}_bin{b}|S", "gemini2_pc_group", bmask & s_mask)
            for tidx, target in enumerate(TARGETS):
                add_feature(features, f"gemini2_pc{pc}_bin{b}|target={target}", "gemini2_pc_target", bmask & (target_grid == tidx))

    # Remove duplicate masks to avoid over-weighting identical semantic bundles.
    unique = []
    seen = set()
    for feat in features:
        key = tuple(feat.indices.tolist())
        if key in seen:
            continue
        seen.add(key)
        unique.append(feat)

    cluster_df = pd.DataFrame(rows).drop_duplicates(["row", "cluster_k"]).sort_values(["cluster_k", "row"])
    pc_df = pd.DataFrame(pcs[:, : min(8, n_pca)], columns=[f"gemini2_pc{i}" for i in range(min(8, n_pca))])
    pc_df.insert(0, "row", np.arange(n_rows))
    cluster_wide = cluster_df.pivot(index="row", columns="cluster_k", values="cluster").reset_index()
    cluster_wide.columns = ["row"] + [f"cluster_k{c}" for c in cluster_wide.columns[1:]]
    latent = cluster_wide.merge(pc_df, on="row", how="left")
    return unique, latent


def fit_models_with_features(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[h149mod.BundleFeature],
) -> dict[str, dict[str, object]]:
    return {spec.name: h150mod.fit_variant(obs, moves, features, spec) for spec in h150mod.variant_specs()}


def model_summary(models: dict[str, dict[str, object]], prefix: str) -> pd.DataFrame:
    rows = []
    for name, model in models.items():
        best = model["best"]
        rows.append(
            {
                "model_set": prefix,
                "variant": name,
                "n_features": int(len(model["features"])),
                "alpha": float(best["alpha"]),
                "loo_mae": float(best["loo_mae"]),
                "loo_rmse": float(best["loo_rmse"]),
                "loo_spearman": float(best["loo_spearman"]),
                "h144_h145_pred_gap_abs": float(best["h144_h145_pred_gap_abs"]),
            }
        )
    return pd.DataFrame(rows)


def gradients(models: dict[str, dict[str, object]], n_cells: int) -> dict[str, np.ndarray]:
    return {name: h150mod.gradient(model, n_cells) for name, model in models.items()}


def build_cell_candidates(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    moves: dict[str, np.ndarray],
    semantic_models: dict[str, dict[str, object]],
    base_models: dict[str, dict[str, object]],
) -> pd.DataFrame:
    n_rows, n_targets = base_prob.shape
    sem_grad = gradients(semantic_models, n_rows * n_targets)
    base_grad = gradients(base_models, n_rows * n_targets)
    h088 = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    rows = []
    for source_file in SOURCE_FILES:
        if source_file not in moves:
            continue
        move = moves[source_file]
        sem_benefit = -sem_grad["all_full"] * move
        base_benefit = -base_grad["all_full"] * move
        robust_sem = np.vstack([-g * move for g in sem_grad.values()])
        robust_base = np.vstack([-g * move for g in base_grad.values()])
        changed = np.flatnonzero(np.abs(move) > TOL)
        for flat in changed:
            row = flat // n_targets
            tidx = flat % n_targets
            toxic_alignment = float((move[flat] * h088[flat] > 0) * rank01(np.abs(h088), high=True)[flat])
            sem_pos = int((robust_sem[:, flat] > 0).sum())
            base_pos = int((robust_base[:, flat] > 0).sum())
            score = (
                8.0 * rank01(sem_benefit, high=True)[flat]
                + 4.0 * rank01(base_benefit, high=True)[flat]
                + 0.22 * sem_pos
                + 0.10 * base_pos
                - 2.8 * toxic_alignment
                - 0.05 * np.log1p(abs(move[flat]))
            )
            rows.append(
                {
                    "source_file": source_file,
                    "row": int(row),
                    "target": TARGETS[tidx],
                    "target_idx": int(tidx),
                    "subject_id": sample.iloc[row]["subject_id"],
                    "sleep_date": sample.iloc[row]["sleep_date"],
                    "flat_idx": int(flat),
                    "move": float(move[flat]),
                    "semantic_benefit": float(sem_benefit[flat]),
                    "base_benefit": float(base_benefit[flat]),
                    "semantic_positive_variants": sem_pos,
                    "base_positive_variants": base_pos,
                    "h088_alignment": toxic_alignment,
                    "score": float(score),
                }
            )
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def select_cells(cell_df: pd.DataFrame, spec: H153Spec) -> pd.DataFrame:
    selected = []
    used_cells = set()
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    subject_count: dict[str, int] = {}
    source_count: dict[str, int] = {}
    for rec in cell_df.to_dict("records"):
        if len(selected) >= spec.max_cells:
            break
        if float(rec["semantic_benefit"]) < spec.min_semantic_benefit:
            continue
        if float(rec["base_benefit"]) < spec.min_base_benefit:
            continue
        if float(rec["h088_alignment"]) > spec.max_h088_alignment:
            continue
        key = (int(rec["flat_idx"]), str(rec["source_file"]))
        if key in used_cells:
            continue
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(rec["subject_id"])
        source = str(rec["source_file"])
        if row not in row_count and len(row_count) >= spec.max_rows:
            continue
        if target_count.get(target, 0) >= spec.max_per_target:
            continue
        if subject_count.get(subject, 0) >= spec.max_per_subject:
            continue
        if source_count.get(source, 0) >= spec.max_per_source:
            continue
        used_cells.add(key)
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        subject_count[subject] = subject_count.get(subject, 0) + 1
        source_count[source] = source_count.get(source, 0) + 1
        selected.append(rec)
    return pd.DataFrame(selected)


def materialize(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    moves: dict[str, np.ndarray],
    selected: pd.DataFrame,
    amp: float,
) -> np.ndarray:
    n_rows, n_targets = base_prob.shape
    delta = np.zeros(n_rows * n_targets, dtype=np.float64)
    for rec in selected.to_dict("records"):
        flat = int(rec["flat_idx"])
        delta[flat] += amp * moves[str(rec["source_file"])][flat]
    return clip_prob(sigmoid(logit(base_prob).reshape(-1) + delta).reshape(n_rows, n_targets))


def candidate_metrics(
    file_name: str,
    move: np.ndarray,
    models: dict[str, dict[str, object]],
    h088_move: np.ndarray,
) -> dict[str, object]:
    return h152mod.candidate_metrics(file_name, move, models, h088_move)


def run() -> None:
    cleanup_previous_outputs()
    base_df = load_sub(BASE_FILE)
    sample = base_df[KEYS].copy()
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)

    source_probs = {}
    for source_file in SOURCE_FILES:
        path = locate(source_file)
        if path is not None:
            source_probs[source_file] = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)

    narratives = make_row_narratives(sample, base_prob, source_probs)
    narratives.to_csv(OUT / "h153_row_narratives.csv", index=False)
    allow_fallback = os.environ.get("H153_ALLOW_LOCAL_FALLBACK", "").strip() == "1"
    emb, emb_meta = load_or_create_embeddings(narratives, allow_fallback=allow_fallback)
    pd.DataFrame(emb).to_parquet(OUT / "h153_row_embeddings.parquet", index=False)

    sem_features, sem_latent = semantic_bundle_features(sample, base_prob, emb)
    sem_latent.to_csv(OUT / "h153_semantic_row_latent.csv", index=False)
    pd.DataFrame(
        [{"name": f.name, "family": f.family, "n_cells": int(len(f.indices))} for f in sem_features]
    ).to_csv(OUT / "h153_semantic_bundle_features.csv", index=False)

    obs, moves, base_models = h152mod.fit_listener_worlds(sample, base_prob)
    for source_file in SOURCE_FILES + h148mod.CANDIDATE_FILES:
        path = locate(source_file)
        if path is None or source_file in moves:
            continue
        try:
            moves[source_file] = movement_from_file(path, sample, base_prob)
        except Exception:
            pass
    base_features = h149mod.build_bundle_features(sample, base_prob)
    semantic_models = fit_models_with_features(obs, moves, base_features + sem_features)
    summaries = pd.concat(
        [model_summary(base_models, "base_listener"), model_summary(semantic_models, "gemini2_semantic_listener")],
        ignore_index=True,
    )
    summaries.to_csv(OUT / "h153_listener_model_comparison.csv", index=False)

    cell_df = build_cell_candidates(sample, base_prob, moves, semantic_models, base_models)
    cell_df.to_csv(OUT / "h153_cell_candidates.csv", index=False)

    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    decision_rows = []
    candidate_rows = []
    for spec in SPECS:
        selected = select_cells(cell_df, spec)
        selected.to_csv(OUT / f"h153_selected_cells_{spec.name}.csv", index=False)
        prob = materialize(sample, base_prob, moves, selected, spec.amp)
        local_path = OUT / f"submission_h153_{spec.name}_{short_hash(prob)}.csv"
        write_submission(sample, prob, local_path)
        validation = validate_submission(local_path, sample, base_prob)
        move = (logit(prob) - logit(base_prob)).reshape(-1)
        sem_metrics = candidate_metrics(local_path.name, move, semantic_models, h088_move)
        base_metrics = candidate_metrics(local_path.name, move, base_models, h088_move)
        rec = {
            "spec": spec.name,
            "description": spec.description,
            "local_path": str(local_path.resolve()),
            "hash": short_hash(prob),
            "selected_cells": int(len(selected)),
            "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
            "selected_target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
            "selected_source_mix": selected["source_file"].value_counts().to_dict() if not selected.empty else {},
            "semantic_robust_mean_delta": float(sem_metrics["robust_mean_pred_delta"]),
            "semantic_robust_max_delta": float(sem_metrics["robust_max_pred_delta"]),
            "semantic_positive_variants": int(sem_metrics["robust_positive_variant_count"]),
            "base_robust_mean_delta": float(base_metrics["robust_mean_pred_delta"]),
            "base_robust_max_delta": float(base_metrics["robust_max_pred_delta"]),
            "base_positive_variants": int(base_metrics["robust_positive_variant_count"]),
            "h088_move_cosine": float(base_metrics["h088_move_cosine"]),
            **{f"validation_{k}": v for k, v in validation.items()},
        }
        decision_rows.append(rec)
        candidate_rows.append({"spec": spec.name, "file": local_path.name, **sem_metrics})

    for file_name in [
        "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
        "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
        "submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv",
    ]:
        path = locate(file_name)
        if path is None:
            continue
        move = movement_from_file(path, sample, base_prob)
        candidate_rows.append({"spec": "reference", "file": file_name, **candidate_metrics(file_name, move, semantic_models, h088_move)})

    decisions = pd.DataFrame(decision_rows)
    decisions["decision_score"] = (
        -800.0 * decisions["semantic_robust_mean_delta"]
        - 450.0 * np.maximum(decisions["semantic_robust_max_delta"], 0.0)
        - 350.0 * np.maximum(decisions["base_robust_max_delta"], 0.0)
        + 0.10 * decisions["semantic_positive_variants"]
        + 0.08 * decisions["base_positive_variants"]
        - 0.45 * decisions["h088_move_cosine"]
        + 0.0004 * decisions["selected_cells"]
    )
    decisions = decisions.sort_values("decision_score", ascending=False).reset_index(drop=True)
    decisions.to_csv(OUT / "h153_decision.csv", index=False)

    candidate_scores = pd.DataFrame(candidate_rows).sort_values(
        ["robust_positive_variant_count", "robust_mean_pred_delta", "h088_move_cosine"],
        ascending=[False, True, True],
    )
    candidate_scores.to_csv(OUT / "h153_candidate_scores_semantic_listener.csv", index=False)

    best = decisions.iloc[0].to_dict()
    best_path = Path(str(best["local_path"]))
    root_path = ROOT / f"submission_h153_gemini2_{best['spec']}_{best['hash']}_uploadsafe.csv"
    shutil.copyfile(best_path, root_path)
    root_validation = validate_submission(root_path, sample, base_prob)

    readout = {
        "embedding_source": emb_meta["embedding_source"],
        "gemini_embedding_used": emb_meta["embedding_source"] == MODEL_NAME,
        "n_semantic_features": int(len(sem_features)),
        "best_spec": str(best["spec"]),
        "best_root_path": str(root_path.resolve()),
        "best_upload_safe": bool(root_validation["upload_safe"]),
        "best_semantic_robust_mean_delta": float(best["semantic_robust_mean_delta"]),
        "best_base_robust_mean_delta": float(best["base_robust_mean_delta"]),
        "best_h088_move_cosine": float(best["h088_move_cosine"]),
    }
    (OUT / "h153_readout.json").write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")

    report = f"""# H153 Gemini Embedding 2 Human-State Narrative HS-JEPA

Date: 2026-06-03

## Question

Can Gemini Embedding 2 turn row narratives into a useful human-state latent for
the HS-JEPA listener/toxicity solver?

The row is not embedded as raw numbers.  It is first translated into a compact
human-readable narrative:

```text
subject/date/calendar state/base target profile/source action disagreement
-> latent human-state route/listener/action-health/anti-shortcut tendency
```

## Embedding Source

```json
{json.dumps(emb_meta, indent=2, ensure_ascii=False)}
```

## Listener Model Comparison

{md_table(summaries, 30)}

## Candidate Decision

{md_table(decisions, 10)}

## Semantic Listener Candidate Scores

{md_table(candidate_scores[["spec", "file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta", "robust_max_pred_delta"]], 20)}

## Top Cell Candidates

{md_table(cell_df[["source_file", "row", "target", "subject_id", "sleep_date", "semantic_benefit", "base_benefit", "semantic_positive_variants", "base_positive_variants", "h088_alignment", "score"]], 40)}

## Readout

```json
{json.dumps(readout, indent=2, ensure_ascii=False)}
```

## Interpretation

If the Gemini semantic listener improves LOO metrics and selects a candidate
with H149-level benefit but lower H088 cosine, then language-model semantic
state is a real HS-JEPA context encoder.  If it only mirrors H149/H152 or
raises H088 alignment, then the narrative embedding is useful for hypothesis
organization but not yet a safe correction decoder.
"""
    (OUT / "h153_report.md").write_text(report, encoding="utf-8")

    print(json.dumps(readout, indent=2, ensure_ascii=False))
    print(decisions[["spec", "selected_cells", "selected_rows", "semantic_robust_mean_delta", "base_robust_mean_delta", "h088_move_cosine"]].to_string(index=False))
    print(f"H153 promoted: {root_path}")


if __name__ == "__main__":
    run()
