#!/usr/bin/env python3
"""Factorized toxicity decoder candidate for the sleep competition adapter.

This script translates the hard-world factorization probe into real
upload-safe submissions.

HS-JEPA core stays competition-agnostic.  This file is a competition adapter:
it takes a public-sensor action field and asks whether the action is safe under
two separate toxicity heads:

    1. broad-public toxicity from the bad-anchor bundle
    2. hard-world toxicity from the H088-like anchor

The point is not to tune an alpha.  The claim being tested is that row-target
actions live in quadrants, and a cell that is safe in broad-public space can
still be toxic in hard-world space.  The decoder therefore only trusts actions
that survive both heads, or keeps teacher actions after damping their unsafe
quadrants.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "factorized_toxicity_decoder_candidate"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"
HARDWORLD_PROBE = HERE / "hardworld_toxicity_factorization_probe.py"
SECTORS_CSV = HERE / "outputs" / "hardworld_toxicity_factorization_sectors.csv"
PROBE_JSON = HERE / "outputs" / "hardworld_toxicity_factorization_probe.json"


@dataclass(frozen=True)
class FactorizedDecoderConfig:
    teacher_min_amp: float = 0.58
    teacher_max_amp: float = 1.18
    teacher_conflict_amp: float = 0.48
    teacher_hard_top_amp: float = 0.52
    teacher_dual_safe_bonus: float = 0.12
    expansion_top_cells: int = 42
    expansion_min_selection: float = 0.64
    expansion_min_joint_safety: float = 0.55
    expansion_min_hard_safety: float = 0.58
    expansion_min_broad_safety: float = 0.50
    expansion_max_cells_per_row: int = 2
    expansion_target_caps: tuple[tuple[str, int], ...] = (
        ("Q2", 16),
        ("Q3", 8),
        ("S2", 10),
        ("Q1", 4),
        ("S1", 2),
        ("S3", 1),
        ("S4", 1),
    )
    expansion_max_logit_step: float = 0.86
    expansion_objective_tail_penalty: float = 0.14


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "factorized_toxicity_candidate1")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def write_submission(path: Path, sample: pd.DataFrame, prob: np.ndarray) -> None:
    out = sample[KEYS].copy()
    for idx, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, idx])
    out.to_csv(path, index=False)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    keys_match = df[KEYS].equals(sample[KEYS])
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(keys_match),
        "duplicate_keys": int(df[KEYS].duplicated().sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def ensure_inputs() -> tuple[pd.DataFrame, dict[str, object]]:
    if not SECTORS_CSV.exists() or not PROBE_JSON.exists():
        probe = import_module(HARDWORLD_PROBE, "factorized_hardworld_probe")
        probe.run()
    sectors = pd.read_csv(SECTORS_CSV)
    for col in [
        "teacher_has_action",
        "lrj_has_cell",
        "lrj_teacher_sign_match",
        "broad_safe_hardworld_toxic",
        "broad_toxic_hardworld_safe",
        "hardworld_top_toxic",
        "broad_top_toxic",
        "selected_by_existing_decoder",
    ]:
        if col in sectors:
            sectors[col] = as_bool(sectors[col])
    probe_readout = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
    return sectors, probe_readout.get("verdict", probe_readout)


def target_caps(config: FactorizedDecoderConfig) -> dict[str, int]:
    return {target: cap for target, cap in config.expansion_target_caps}


def teacher_amp(row: pd.Series, config: FactorizedDecoderConfig) -> float:
    broad_safe = float(row["broad_safe_rank_ex_hardworld"])
    hard_safe = float(row["hardworld_safe_rank"])
    joint_safe = float(row["joint_safety_min_rank"])
    agreement = float(bool(row.get("lrj_teacher_sign_match", False)))
    amp = (
        0.72
        + 0.12 * agreement
        + 0.15 * broad_safe
        + 0.18 * hard_safe
        + 0.16 * joint_safe
        - 0.10 * float(row["broad_toxic_rank_ex_hardworld"])
        - 0.14 * float(row["hardworld_toxic_rank"])
    )
    if bool(row.get("broad_safe_hardworld_toxic", False)):
        amp *= config.teacher_conflict_amp
    if bool(row.get("hardworld_top_toxic", False)):
        amp *= config.teacher_hard_top_amp
    if broad_safe >= 0.65 and hard_safe >= 0.65:
        amp += config.teacher_dual_safe_bonus
    target = str(row["target"])
    if target == "Q2":
        amp += 0.04 * float(row.get("listener_benefit_rank", 0.0))
    if target in {"S1", "S3", "S4"}:
        amp -= 0.08 + 0.08 * float(row.get("hardworld_toxic_rank", 0.0))
    return float(np.clip(amp, config.teacher_min_amp, config.teacher_max_amp))


def expansion_score(frame: pd.DataFrame, config: FactorizedDecoderConfig) -> pd.Series:
    score = (
        0.26 * frame["selection_score"].astype(float)
        + 0.18 * frame["listener_benefit_rank"].astype(float)
        + 0.18 * frame["human_state_responsibility"].astype(float)
        + 0.24 * frame["joint_safety_min_rank"].astype(float)
        + 0.08 * frame["hardworld_safe_rank"].astype(float)
        + 0.06 * frame["broad_safe_rank_ex_hardworld"].astype(float)
    )
    score = score.where(~frame["target"].isin(["S1", "S3", "S4"]), score - config.expansion_objective_tail_penalty)
    score = score.where(~frame["broad_safe_hardworld_toxic"], score - 0.22)
    score = score.where(~frame["hardworld_top_toxic"], score - 0.28)
    score = score.where(~frame["broad_top_toxic"], score - 0.16)
    score = score.where(frame["target"].ne("Q2"), score + 0.05)
    score = score.where(frame["target"].ne("S2"), score + 0.04)
    return score


def decode_variant(
    sectors: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    variant: str,
    config: FactorizedDecoderConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    move = np.zeros(base_prob.size, dtype=np.float64)
    audit_rows: list[dict[str, object]] = []

    teacher = sectors[sectors["teacher_has_action"]].copy()
    teacher["amp"] = teacher.apply(lambda row: teacher_amp(row, config), axis=1)
    for rec in teacher.to_dict("records"):
        flat = int(rec["flat_idx"])
        decoded = float(rec["teacher_logit_move"]) * float(rec["amp"])
        move[flat] = decoded
        audit_rows.append({**rec, "decoded_logit_move": decoded, "action_source": "teacher_factorized_toxicity"})

    if variant == "dual_safe_expansion":
        pool = sectors[
            (~sectors["teacher_has_action"])
            & sectors["lrj_has_cell"]
            & (sectors["selection_score"] >= config.expansion_min_selection)
            & (sectors["joint_safety_min_rank"] >= config.expansion_min_joint_safety)
            & (sectors["hardworld_safe_rank"] >= config.expansion_min_hard_safety)
            & (sectors["broad_safe_rank_ex_hardworld"] >= config.expansion_min_broad_safety)
            & (~sectors["broad_safe_hardworld_toxic"])
            & (~sectors["hardworld_top_toxic"])
        ].copy()
        pool["factorized_expansion_score"] = expansion_score(pool, config)
        pool = pool.sort_values("factorized_expansion_score", ascending=False)

        row_count = {
            int(row): count
            for row, count in pd.Series([flat // len(TARGETS) for flat in np.flatnonzero(np.abs(move) > TOL)])
            .value_counts()
            .items()
        }
        target_count: dict[str, int] = {}
        caps = target_caps(config)
        added = 0
        for rec in pool.to_dict("records"):
            row = int(rec["row"])
            target = str(rec["target"])
            if row_count.get(row, 0) >= config.expansion_max_cells_per_row:
                continue
            if target_count.get(target, 0) >= caps.get(target, 0):
                continue
            magnitude = min(
                config.expansion_max_logit_step,
                0.12
                + 0.30 * float(rec["responsibility_score"])
                + 0.18 * float(rec["listener_benefit_rank"])
                + 0.26 * float(rec["joint_safety_min_rank"]),
            )
            flat = int(rec["flat_idx"])
            decoded = int(rec["candidate_sign"]) * float(magnitude)
            move[flat] = decoded
            audit_rows.append({**rec, "decoded_logit_move": decoded, "action_source": "dual_safe_lrj_expansion"})
            row_count[row] = row_count.get(row, 0) + 1
            target_count[target] = target_count.get(target, 0) + 1
            added += 1
            if added >= config.expansion_top_cells:
                break

    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    audit = pd.DataFrame(audit_rows)
    diagnostics = build_decode_diagnostics(audit, sectors, variant)
    return prob, audit, diagnostics


def action_counts(audit: pd.DataFrame) -> dict[str, dict[str, int]]:
    if audit.empty:
        return {}
    return {
        source: {target: int(count) for target, count in group["target"].value_counts().reindex(TARGETS).fillna(0).items()}
        for source, group in audit.groupby("action_source")
    }


def safety_summary(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {
            "cells": 0,
            "joint_safety_mean": None,
            "broad_safe_mean": None,
            "hardworld_safe_mean": None,
            "hardworld_top_toxic_rate": None,
            "broad_safe_hardworld_toxic_rate": None,
            "dual_safe_rate": None,
        }
    dual_safe = (frame["broad_safe_rank_ex_hardworld"] >= 0.65) & (frame["hardworld_safe_rank"] >= 0.65)
    return {
        "cells": int(len(frame)),
        "joint_safety_mean": float(frame["joint_safety_min_rank"].mean()),
        "broad_safe_mean": float(frame["broad_safe_rank_ex_hardworld"].mean()),
        "hardworld_safe_mean": float(frame["hardworld_safe_rank"].mean()),
        "hardworld_top_toxic_rate": float(frame["hardworld_top_toxic"].mean()),
        "broad_safe_hardworld_toxic_rate": float(frame["broad_safe_hardworld_toxic"].mean()),
        "dual_safe_rate": float(dual_safe.mean()),
    }


def build_decode_diagnostics(audit: pd.DataFrame, sectors: pd.DataFrame, variant: str) -> dict[str, object]:
    changed = audit[np.abs(audit["decoded_logit_move"].astype(float)) > TOL] if not audit.empty else audit
    existing = sectors[sectors["selected_by_existing_decoder"]]
    expansion = audit[audit["action_source"].eq("dual_safe_lrj_expansion")] if not audit.empty else audit
    teacher = audit[audit["action_source"].eq("teacher_factorized_toxicity")] if not audit.empty else audit
    return {
        "variant": variant,
        "changed_cells": int(len(changed)),
        "changed_rows": int(changed["row"].nunique()) if not changed.empty else 0,
        "target_action_counts": action_counts(changed),
        "teacher_cells": int(len(teacher)),
        "expansion_cells": int(len(expansion)),
        "teacher_mean_amp": float(teacher["amp"].mean()) if not teacher.empty and "amp" in teacher else 0.0,
        "teacher_min_amp": float(teacher["amp"].min()) if not teacher.empty and "amp" in teacher else 0.0,
        "teacher_max_amp": float(teacher["amp"].max()) if not teacher.empty and "amp" in teacher else 0.0,
        "selected_safety": safety_summary(changed),
        "existing_decoder_safety": safety_summary(existing),
        "teacher_safety": safety_summary(teacher),
        "expansion_safety": safety_summary(expansion),
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Variant | File | Changed cells | Joint safety | H088 top-toxic rate | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in readout["variants"].items():
        diag = item["decode_diagnostics"]
        safety = diag["selected_safety"]
        rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{diag['changed_cells']}` | "
            f"`{safety['joint_safety_mean']:.4f}` | `{safety['hardworld_top_toxic_rate']:.4f}` | "
            f"`{item['validation']['upload_safe']}` |"
        )

    verdict = readout["probe_verdict"]
    return "\n".join(
        [
            "# Factorized Toxicity Decoder Candidate",
            "",
            "이 산출물은 HS-JEPA core가 아니라 sleep competition adapter의 action-health decoder다.",
            "",
            "## Worldview",
            "",
            "H088류 hard-world 독성은 broad public-bad 독성과 같은 축이 아니라 반상관된 별도 축이다. 따라서 row-target action은 scalar safety가 아니라 broad-public safety와 hard-world safety를 동시에 통과해야 한다.",
            "",
            "## Probe Input",
            "",
            f"- Hard-world factorization status: `{verdict['status']}`",
            f"- Broad toxicity -> H088 AUC: `{verdict['broad_predicts_hardworld_auc']:.4f}`",
            f"- Broad/H088 Spearman: `{verdict['broad_hardworld_spearman']:.4f}`",
            f"- Broad-safe but H088-toxic cells: `{verdict['broad_safe_hardworld_toxic_cells']}`",
            "",
            "## Generated Candidates",
            "",
            *rows,
            "",
            "## Interpretation",
            "",
            "- `teacher_dual_head`: 기존 public-sensor teacher support는 유지하되 hard-world 독성축에서 위험한 cell을 강하게 damp한다.",
            "- `dual_safe_expansion`: teacher support에 더해 broad/hard 두 safety head를 모두 통과한 LRJ cell만 확장한다.",
            "- 이 후보가 public에서 좋아지면 scalar toxicity가 아니라 factorized action-health decoder가 맞다는 증거다.",
            "- 나빠지면 hard-world factorization은 diagnostic으로는 맞지만, 아직 action-grade decoder로 번역되지 않았다는 뜻이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sectors, probe_verdict = ensure_inputs()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    config = FactorizedDecoderConfig()

    variants: dict[str, object] = {}
    for variant in ["teacher_dual_head", "dual_safe_expansion"]:
        prob, audit, diag = decode_variant(sectors, sample, base_prob, base_logit, variant, config)
        digest = short_hash(prob)
        name = f"submission_hsjepa_factorized_toxicity_decoder_{variant}_{digest}_uploadsafe.csv"
        local_path = OUT / name
        root_path = ROOT / name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        audit.to_csv(OUT / f"factorized_toxicity_decoder_{variant}_audit.csv", index=False)
        move = logit(prob).reshape(-1) - base_logit
        variants[variant] = {
            "submission_file": name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "decode_diagnostics": diag,
            "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
            "validation": validate_submission(root_path, sample, base_prob),
        }

    readout = {
        "experiment": "Factorized Toxicity Decoder Candidate",
        "architecture_role": "sleep_competition_adapter_action_health_decoder",
        "core_boundary": "HS-JEPA core supplies the listener/action interface; this module uses public and hard-world competition sensors.",
        "config": config.__dict__,
        "probe_verdict": probe_verdict,
        "variants": variants,
    }
    (OUT / "factorized_toxicity_decoder_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    (OUT / "factorized_toxicity_decoder_readout_ko.md").write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
