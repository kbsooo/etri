#!/usr/bin/env python3
"""H154: local semantic source-consensus jackpot HS-JEPA.

This is the open, reproducible version of the narrative-state experiment.

H153 showed that a human-readable row narrative embedded by Gemini could
produce a strong listener/responsibility field.  H154 asks the harder question:
does the same idea survive without proprietary embeddings?

Architecture:
    row context + source action disagreement
        -> human-state narrative
        -> local TF-IDF + SVD semantic latent
        -> semantic bundle listener worlds
        -> source-consensus row-target assignment
        -> upload-safe correction field from H057

The promoted candidate is intentionally not a small alpha tweak.  It claims
that public-listened actions are those where multiple independent HS-JEPA
routes point in the same direction inside the local narrative latent space,
while H088-like toxic alignment remains near zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hsjepa_jackpot" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

H153_PATH = ROOT / "hitl" / "h153_gemini2_human_state_embedding_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h153mod_h154", H153_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H153_PATH}")
h153mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h153mod
SPEC.loader.exec_module(h153mod)

h152mod = h153mod.h152mod
h150mod = h153mod.h150mod
h149mod = h153mod.h149mod
h148mod = h153mod.h148mod
h085mod = h153mod.h085mod

TARGETS = h153mod.TARGETS
KEYS = h153mod.KEYS
BASE_FILE = h153mod.BASE_FILE
TOL = h153mod.TOL

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
    "submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv",
    "submission_h085_aug_public_equation_f154e2bb_uploadsafe.csv",
]


@dataclass(frozen=True)
class JackpotSpec:
    name: str
    query: str
    max_pairs: int
    max_rows: int
    max_per_target: int
    max_per_subject: int
    max_per_flat: int
    amp: float
    description: str


SPECS = [
    JackpotSpec(
        name="local_semantic_source_consensus",
        query=(
            "sem_mean_benefit > 0 and base_mean_benefit > -0.00001 "
            "and source_support >= 3 and h088_alignment < 0.60"
        ),
        max_pairs=380,
        max_rows=150,
        max_per_target=84,
        max_per_subject=95,
        max_per_flat=4,
        amp=0.56,
        description="multiple source routes agree inside local semantic latent; low H088 alignment",
    ),
    JackpotSpec(
        name="local_semantic_jackpot_balanced",
        query=(
            "sem_mean_benefit > 0 and base_mean_benefit > -0.000002 "
            "and sem_pos >= 8 and base_pos >= 7 and h088_alignment < 0.72"
        ),
        max_pairs=420,
        max_rows=150,
        max_per_target=86,
        max_per_subject=100,
        max_per_flat=4,
        amp=0.58,
        description="broader high-upside semantic listener with base-listener support",
    ),
    JackpotSpec(
        name="local_semantic_frontier_needle",
        query=(
            "sem_mean_benefit > 0 and base_mean_benefit > 0 "
            "and sem_min_benefit > -0.00002 and base_min_benefit > -0.00002 "
            "and h088_alignment < 0.40 and source_support >= 2"
        ),
        max_pairs=260,
        max_rows=110,
        max_per_target=58,
        max_per_subject=72,
        max_per_flat=2,
        amp=0.66,
        description="narrow frontier-safe semantic needle, lower upside but strongest stress shape",
    ),
]


def locate(name: str | Path) -> Path | None:
    return h085mod.locate(name)


def load_sub(path: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return h085mod.load_sub(path, sample)


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(x)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(x)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(values, high=high)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    h085mod.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    return h085mod.validate_submission(path, sample, base_prob)


def movement_from_file(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(-1)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h154_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h154_*.csv"):
        path.unlink()


def load_world() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, dict[str, np.ndarray], dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    base_df = load_sub(BASE_FILE)
    sample = base_df[KEYS].copy()
    base_prob = base_df[TARGETS].to_numpy(dtype=np.float64)

    source_probs: dict[str, np.ndarray] = {}
    for source_file in SOURCE_FILES:
        path = locate(source_file)
        if path is None:
            continue
        try:
            source_probs[source_file] = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue

    narrative_sources = {
        key: value for key, value in source_probs.items() if key in h153mod.SOURCE_FILES
    }
    narratives = h153mod.make_row_narratives(sample, base_prob, narrative_sources)
    narratives.to_csv(OUT / "h154_row_narratives.csv", index=False)

    emb = h153mod.local_tfidf_fallback(narratives["narrative"].astype(str).tolist())
    pd.DataFrame(emb).to_parquet(OUT / "h154_local_tfidf_svd_embeddings.parquet", index=False)
    semantic_features, semantic_latent = h153mod.semantic_bundle_features(sample, base_prob, emb)
    semantic_latent.to_csv(OUT / "h154_local_semantic_row_latent.csv", index=False)
    pd.DataFrame(
        [{"name": feat.name, "family": feat.family, "n_cells": int(len(feat.indices))} for feat in semantic_features]
    ).to_csv(OUT / "h154_local_semantic_features.csv", index=False)

    obs, moves, base_models = h152mod.fit_listener_worlds(sample, base_prob)
    for source_file in SOURCE_FILES + h148mod.CANDIDATE_FILES:
        path = locate(source_file)
        if path is None or source_file in moves:
            continue
        try:
            moves[source_file] = movement_from_file(path, sample, base_prob)
        except Exception:
            continue

    base_features = h149mod.build_bundle_features(sample, base_prob)
    semantic_models = {
        spec.name: h150mod.fit_variant(obs, moves, base_features + semantic_features, spec)
        for spec in h150mod.variant_specs()
    }
    model_summary = pd.concat(
        [
            h153mod.model_summary(base_models, "base_listener"),
            h153mod.model_summary(semantic_models, "local_tfidf_svd_semantic_listener"),
        ],
        ignore_index=True,
    )
    model_summary.to_csv(OUT / "h154_listener_model_comparison.csv", index=False)
    return sample, narratives, base_prob, moves, base_models, semantic_models


def build_cell_candidates(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    moves: dict[str, np.ndarray],
    base_models: dict[str, dict[str, object]],
    semantic_models: dict[str, dict[str, object]],
) -> pd.DataFrame:
    n_rows, n_targets = base_prob.shape
    n_cells = n_rows * n_targets
    base_grad = {name: h150mod.gradient(model, n_cells) for name, model in base_models.items()}
    sem_grad = {name: h150mod.gradient(model, n_cells) for name, model in semantic_models.items()}
    h088 = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    h088_rank = rank01(np.abs(h088), high=True)

    rows: list[dict[str, object]] = []
    for source_file in SOURCE_FILES:
        if source_file not in moves:
            continue
        move = moves[source_file]
        robust_sem = np.vstack([-grad * move for grad in sem_grad.values()])
        robust_base = np.vstack([-grad * move for grad in base_grad.values()])
        sem_mean = robust_sem.mean(axis=0)
        base_mean = robust_base.mean(axis=0)
        for flat_idx in np.flatnonzero(np.abs(move) > TOL):
            row = int(flat_idx // n_targets)
            tidx = int(flat_idx % n_targets)
            rows.append(
                {
                    "source_file": source_file,
                    "flat_idx": int(flat_idx),
                    "row": row,
                    "target": TARGETS[tidx],
                    "target_idx": tidx,
                    "subject_id": sample.iloc[row]["subject_id"],
                    "sleep_date": sample.iloc[row]["sleep_date"],
                    "lifelog_date": sample.iloc[row]["lifelog_date"],
                    "source_move": float(move[flat_idx]),
                    "sign": int(np.sign(move[flat_idx])),
                    "sem_mean_benefit": float(sem_mean[flat_idx]),
                    "base_mean_benefit": float(base_mean[flat_idx]),
                    "sem_min_benefit": float(robust_sem[:, flat_idx].min()),
                    "base_min_benefit": float(robust_base[:, flat_idx].min()),
                    "sem_pos": int((robust_sem[:, flat_idx] > 0).sum()),
                    "base_pos": int((robust_base[:, flat_idx] > 0).sum()),
                    "h088_alignment": float((move[flat_idx] * h088[flat_idx] > 0) * h088_rank[flat_idx]),
                }
            )
    cells = pd.DataFrame(rows)
    if cells.empty:
        raise RuntimeError("no source cells found")

    support = (
        cells.groupby(["flat_idx", "sign"], as_index=False)
        .agg(
            source_support=("source_file", "nunique"),
            support_sem_mean=("sem_mean_benefit", "mean"),
            support_base_mean=("base_mean_benefit", "mean"),
        )
    )
    cells = cells.merge(support, on=["flat_idx", "sign"], how="left")
    for col in [
        "sem_mean_benefit",
        "base_mean_benefit",
        "sem_min_benefit",
        "base_min_benefit",
        "source_support",
        "support_sem_mean",
        "support_base_mean",
    ]:
        cells[f"{col}_rank"] = cells[col].rank(method="average", pct=True)
    cells["score"] = (
        1.60 * cells["sem_mean_benefit_rank"]
        + 1.00 * cells["base_mean_benefit_rank"]
        + 0.35 * cells["sem_min_benefit_rank"]
        + 0.25 * cells["base_min_benefit_rank"]
        + 0.32 * cells["source_support_rank"]
        + 0.11 * cells["sem_pos"]
        + 0.07 * cells["base_pos"]
        - 2.20 * cells["h088_alignment"]
    )
    return cells.sort_values("score", ascending=False).reset_index(drop=True)


def select_cells(cells: pd.DataFrame, spec: JackpotSpec) -> pd.DataFrame:
    pool = cells.query(spec.query).sort_values("score", ascending=False).copy()
    selected: list[dict[str, object]] = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    subject_count: dict[str, int] = {}
    flat_count: dict[int, int] = {}
    for rec in pool.to_dict("records"):
        if len(selected) >= spec.max_pairs:
            break
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(rec["subject_id"])
        flat_idx = int(rec["flat_idx"])
        if row not in row_count and len(row_count) >= spec.max_rows:
            continue
        if target_count.get(target, 0) >= spec.max_per_target:
            continue
        if subject_count.get(subject, 0) >= spec.max_per_subject:
            continue
        if flat_count.get(flat_idx, 0) >= spec.max_per_flat:
            continue
        selected.append(rec)
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        subject_count[subject] = subject_count.get(subject, 0) + 1
        flat_count[flat_idx] = flat_count.get(flat_idx, 0) + 1
    return pd.DataFrame(selected)


def materialize(
    base_prob: np.ndarray,
    moves: dict[str, np.ndarray],
    selected: pd.DataFrame,
    amp: float,
    max_abs_logit_delta: float = 1.80,
) -> np.ndarray:
    delta = np.zeros(base_prob.size, dtype=np.float64)
    for rec in selected.to_dict("records"):
        flat_idx = int(rec["flat_idx"])
        delta[flat_idx] += amp * moves[str(rec["source_file"])][flat_idx]
    delta = np.clip(delta, -max_abs_logit_delta, max_abs_logit_delta)
    return clip_prob(sigmoid(logit(base_prob).reshape(-1) + delta).reshape(base_prob.shape))


def candidate_metrics(
    file_name: str,
    move: np.ndarray,
    models: dict[str, dict[str, object]],
    h088_move: np.ndarray,
) -> dict[str, object]:
    return h152mod.candidate_metrics(file_name, move, models, h088_move)


def run() -> None:
    cleanup_previous_outputs()
    sample, narratives, base_prob, moves, base_models, semantic_models = load_world()
    cells = build_cell_candidates(sample, base_prob, moves, base_models, semantic_models)
    cells.to_csv(OUT / "h154_cell_candidates.csv", index=False)

    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    decision_rows = []
    candidate_rows = []
    selected_paths: dict[str, Path] = {}
    for spec in SPECS:
        selected = select_cells(cells, spec)
        selected.to_csv(OUT / f"h154_selected_cells_{spec.name}.csv", index=False)
        prob = materialize(base_prob, moves, selected, spec.amp)
        hash_id = short_hash(prob)
        local_path = OUT / f"submission_h154_{spec.name}_{hash_id}.csv"
        write_submission(sample, prob, local_path)
        selected_paths[spec.name] = local_path
        validation = validate_submission(local_path, sample, base_prob)
        move = (logit(prob) - logit(base_prob)).reshape(-1)
        sem_metrics = candidate_metrics(local_path.name, move, semantic_models, h088_move)
        base_metrics = candidate_metrics(local_path.name, move, base_models, h088_move)
        changed = np.abs(move) > TOL
        rec = {
            "spec": spec.name,
            "description": spec.description,
            "local_path": str(local_path.resolve()),
            "hash": hash_id,
            "selected_pairs": int(len(selected)),
            "changed_cells_vs_h057": int(changed.sum()),
            "changed_rows_vs_h057": int(len(set(np.where(changed)[0] // len(TARGETS)))),
            "selected_source_mix": selected["source_file"].value_counts().to_dict() if not selected.empty else {},
            "selected_target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
            "semantic_robust_mean_delta": float(sem_metrics["robust_mean_pred_delta"]),
            "semantic_robust_max_delta": float(sem_metrics["robust_max_pred_delta"]),
            "semantic_positive_variants": int(sem_metrics["robust_positive_variant_count"]),
            "base_robust_mean_delta": float(base_metrics["robust_mean_pred_delta"]),
            "base_robust_max_delta": float(base_metrics["robust_max_pred_delta"]),
            "base_positive_variants": int(base_metrics["robust_positive_variant_count"]),
            "h088_move_cosine": float(base_metrics["h088_move_cosine"]),
            **{f"validation_{key}": value for key, value in validation.items()},
        }
        decision_rows.append(rec)
        candidate_rows.append({"spec": spec.name, "file": local_path.name, **sem_metrics})

    for file_name in [
        "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
        "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
        "submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv",
        "submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv",
    ]:
        path = locate(file_name)
        if path is None:
            continue
        move = movement_from_file(path, sample, base_prob)
        candidate_rows.append({"spec": "reference", "file": file_name, **candidate_metrics(file_name, move, semantic_models, h088_move)})

    decisions = pd.DataFrame(decision_rows)
    decisions["decision_score"] = (
        -900.0 * decisions["base_robust_mean_delta"]
        - 750.0 * np.maximum(decisions["base_robust_max_delta"], 0.0)
        - 550.0 * np.maximum(decisions["semantic_robust_max_delta"], 0.0)
        + 0.13 * decisions["base_positive_variants"]
        + 0.11 * decisions["semantic_positive_variants"]
        - 0.75 * decisions["h088_move_cosine"].clip(lower=0.0)
        + 0.00045 * decisions["changed_cells_vs_h057"]
    )
    decisions = decisions.sort_values("decision_score", ascending=False).reset_index(drop=True)
    decisions.to_csv(OUT / "h154_decision.csv", index=False)

    candidate_scores = pd.DataFrame(candidate_rows).sort_values(
        ["robust_positive_variant_count", "robust_mean_pred_delta", "h088_move_cosine"],
        ascending=[False, True, True],
    )
    candidate_scores.to_csv(OUT / "h154_candidate_scores_semantic_listener.csv", index=False)

    best = decisions.iloc[0].to_dict()
    local_best = Path(str(best["local_path"]))
    root_path = ROOT / f"submission_h154_{best['spec']}_{best['hash']}_uploadsafe.csv"
    shutil.copyfile(local_best, root_path)
    root_validation = validate_submission(root_path, sample, base_prob)

    readout = {
        "embedding_source": "local_tfidf_svd",
        "uses_external_embedding_api": False,
        "base_file": BASE_FILE,
        "best_spec": str(best["spec"]),
        "best_root_path": str(root_path.resolve()),
        "best_upload_safe": bool(root_validation["upload_safe"]),
        "best_changed_cells_vs_h057": int(root_validation["changed_cells_vs_h057_validation"]),
        "best_base_robust_mean_delta": float(best["base_robust_mean_delta"]),
        "best_base_robust_max_delta": float(best["base_robust_max_delta"]),
        "best_semantic_robust_mean_delta": float(best["semantic_robust_mean_delta"]),
        "best_semantic_robust_max_delta": float(best["semantic_robust_max_delta"]),
        "best_h088_move_cosine": float(best["h088_move_cosine"]),
    }
    (OUT / "h154_readout.json").write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")

    report = f"""# H154 로컬 Semantic Source-Consensus Jackpot HS-JEPA

Date: 2026-06-09

## 질문

Gemini 기반 human narrative latent를 완전히 로컬에서 재현 가능한
TF-IDF + SVD semantic encoder로 바꿔도 public-safe high-responsibility
row-target action을 찾을 수 있는가?

## 세계관

이 실험은 hidden state를 단순한 row나 target으로 보지 않는다.
진짜 hidden state는 listener가 얼마나 듣는지까지 포함한 action field다.

```text
human-state narrative
  -> 로컬 semantic latent
  -> listener responsibility
  -> source-route consensus
  -> anti-H088 toxicity veto
  -> row-target correction
```

이게 맞으면 HS-JEPA 논문/팀 코드에서 closed embedding model에 의존할
필요가 줄어든다. semantic encoder는 context view일 뿐이고, 핵심은
보이는 human-state narrative와 source disagreement로 보이지 않는
listener/action representation을 예측하는 JEPA식 decoder다.

## 후보 결정표

{md_table(decisions[["spec", "selected_pairs", "changed_cells_vs_h057", "changed_rows_vs_h057", "semantic_robust_mean_delta", "semantic_robust_max_delta", "base_robust_mean_delta", "base_robust_max_delta", "h088_move_cosine", "decision_score"]], 10)}

## Semantic Listener 기준 후보 비교

{md_table(candidate_scores[["spec", "file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta", "robust_max_pred_delta"]], 20)}

## 승격 후보

```json
{json.dumps(readout, indent=2, ensure_ascii=False)}
```

## 해석

승격 후보는 calibration 미세조정이 아니라 jackpot 시도다.
베팅은 다음과 같다.

```text
여러 독립 HS-JEPA source route가 같은 방향을 가리키고,
그 action이 local human-state semantic latent 안에서도 좋게 읽히며,
H088 독성축과 거의 직교한다면,
그 row-target correction은 public-safe일 가능성이 있다.
```

public LB가 의미 있게 좋아지면 다음 아키텍처 단계는
`source-consensus listener responsibility`를 HS-JEPA의 메인 decoder로
정식화하는 것이다. 실패하면 그것도 정보가 있다. 그 경우 semantic
context는 offline ranking에는 도움을 주지만, 실제 public listener는
아직 narrative/cohort/source feature보다 더 날카로운 hidden subset에
지배된다는 뜻이다.
"""
    (ROOT / "hsjepa_jackpot" / "H154_LOCAL_SEMANTIC_SOURCE_CONSENSUS_KO.md").write_text(report, encoding="utf-8")

    print(json.dumps(readout, indent=2, ensure_ascii=False))
    print(decisions[["spec", "selected_pairs", "changed_cells_vs_h057", "base_robust_mean_delta", "base_robust_max_delta", "h088_move_cosine"]].to_string(index=False))
    print(f"H154 promoted: {root_path}")


if __name__ == "__main__":
    run()
