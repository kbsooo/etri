#!/usr/bin/env python3
"""Stress audit for the factorized toxicity decoder.

The candidate generator already creates upload-safe submissions.  This audit
asks a stricter question:

    Did the factorized decoder choose a genuinely safer action field than
    feasible null action fields with similar target/source structure?

The audit treats the existing decoded logit magnitudes as an exposure budget.
For each variant it compares the selected cells against:

1. target-only nulls: preserve target counts, ignore source structure.
2. source-matched nulls: preserve target + teacher/LRJ source structure.

This keeps the claim honest.  A good candidate should not only be upload-safe;
its hard-world toxic exposure should be unusually low under matched feasible
action nulls.
"""

from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "factorized_toxicity_decoder_candidate"
OUT.mkdir(parents=True, exist_ok=True)

SECTORS_CSV = HERE / "outputs" / "hardworld_toxicity_factorization_sectors.csv"
READOUT_JSON = OUT / "factorized_toxicity_decoder_readout.json"
SCALAR_TOXICITY_AUDIT = ROOT / "paper_hsjepa_core" / "outputs" / "public_private_toxicity_head" / "toxicity_action_audit.csv"

AUDIT_JSON = OUT / "factorized_toxicity_decoder_stress_audit.json"
AUDIT_MD = OUT / "factorized_toxicity_decoder_stress_audit_ko.md"
SUMMARY_CSV = OUT / "factorized_toxicity_decoder_stress_summary.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def load_sectors() -> pd.DataFrame:
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
    return sectors


def load_variant_audit(readout: dict[str, object], variant: str) -> pd.DataFrame:
    path = OUT / f"factorized_toxicity_decoder_{variant}_audit.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    audit = pd.read_csv(path)
    for col in [
        "teacher_has_action",
        "lrj_has_cell",
        "broad_safe_hardworld_toxic",
        "broad_toxic_hardworld_safe",
        "hardworld_top_toxic",
        "broad_top_toxic",
        "selected_by_existing_decoder",
    ]:
        if col in audit:
            audit[col] = as_bool(audit[col])
    audit["variant"] = variant
    audit["abs_move"] = audit["decoded_logit_move"].astype(float).abs()
    audit["source_class"] = np.where(audit["teacher_has_action"], "teacher", "lrj_extra")
    return audit


def load_scalar_baseline(sectors: pd.DataFrame) -> pd.DataFrame | None:
    if not SCALAR_TOXICITY_AUDIT.exists():
        return None
    audit = pd.read_csv(SCALAR_TOXICITY_AUDIT)
    if audit.empty:
        return None
    for col in [
        "teacher_has_action",
        "lrj_has_cell",
        "broad_safe_hardworld_toxic",
        "broad_toxic_hardworld_safe",
        "hardworld_top_toxic",
        "broad_top_toxic",
    ]:
        if col in audit:
            audit[col] = as_bool(audit[col])
    audit["variant"] = "scalar_public_private_toxicity_baseline"
    audit["abs_move"] = audit["decoded_logit_move"].astype(float).abs()
    audit["source_class"] = np.where(audit["teacher_has_action"], "teacher", "lrj_extra")
    needed_cols = [
        "flat_idx",
        "candidate_sign",
        "hardworld_toxic_rank",
        "hardworld_safe_rank",
        "broad_toxic_rank_ex_hardworld",
        "broad_safe_rank_ex_hardworld",
        "joint_safety_min_rank",
        "broad_safe_hardworld_toxic",
        "broad_toxic_hardworld_safe",
        "hardworld_top_toxic",
        "broad_top_toxic",
    ]
    missing = [col for col in needed_cols if col not in audit.columns]
    if missing:
        sector_cols = [col for col in needed_cols if col in sectors.columns]
        audit = audit.drop(columns=[col for col in sector_cols if col in audit.columns and col not in {"flat_idx", "candidate_sign"}])
        audit = audit.merge(
            sectors[sector_cols].drop_duplicates(["flat_idx", "candidate_sign"]),
            on=["flat_idx", "candidate_sign"],
            how="left",
            validate="many_to_one",
        )
    return audit


def weighted_mean(frame: pd.DataFrame, col: str, weight_col: str = "abs_move") -> float | None:
    if frame.empty:
        return None
    weights = frame[weight_col].astype(float).to_numpy()
    vals = frame[col].astype(float).to_numpy()
    denom = float(weights.sum())
    if denom <= 0:
        return float(np.mean(vals))
    return float(np.average(vals, weights=weights))


def weighted_rate(frame: pd.DataFrame, col: str, weight_col: str = "abs_move") -> float | None:
    if frame.empty:
        return None
    weights = frame[weight_col].astype(float).to_numpy()
    vals = frame[col].astype(bool).astype(float).to_numpy()
    denom = float(weights.sum())
    if denom <= 0:
        return float(np.mean(vals))
    return float(np.average(vals, weights=weights))


def summarize(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {"cells": 0}
    dual_safe = (frame["broad_safe_rank_ex_hardworld"] >= 0.65) & (frame["hardworld_safe_rank"] >= 0.65)
    return {
        "cells": int(len(frame)),
        "rows": int(frame["row"].nunique()),
        "abs_move_sum": float(frame["abs_move"].sum()),
        "abs_move_mean": float(frame["abs_move"].mean()),
        "target_counts": frame["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "source_counts": frame["source_class"].value_counts().to_dict() if "source_class" in frame else {},
        "joint_safety_mean": float(frame["joint_safety_min_rank"].mean()),
        "joint_safety_weighted": weighted_mean(frame, "joint_safety_min_rank"),
        "hardworld_safe_weighted": weighted_mean(frame, "hardworld_safe_rank"),
        "broad_safe_weighted": weighted_mean(frame, "broad_safe_rank_ex_hardworld"),
        "joint_risk_weighted": float(1.0 - weighted_mean(frame, "joint_safety_min_rank")),
        "hardworld_toxic_weighted": weighted_mean(frame, "hardworld_toxic_rank"),
        "broad_toxic_weighted": weighted_mean(frame, "broad_toxic_rank_ex_hardworld"),
        "hardworld_top_toxic_rate": float(frame["hardworld_top_toxic"].mean()),
        "hardworld_top_toxic_exposure": weighted_rate(frame, "hardworld_top_toxic"),
        "broad_top_toxic_exposure": weighted_rate(frame, "broad_top_toxic"),
        "broad_safe_hardworld_toxic_rate": float(frame["broad_safe_hardworld_toxic"].mean()),
        "broad_safe_hardworld_toxic_exposure": weighted_rate(frame, "broad_safe_hardworld_toxic"),
        "dual_safe_rate": float(dual_safe.mean()),
        "dual_safe_exposure": float(np.average(dual_safe.astype(float), weights=frame["abs_move"])) if frame["abs_move"].sum() > 0 else float(dual_safe.mean()),
    }


def z_and_p(actual: float, null_values: list[float], higher_is_better: bool) -> dict[str, float]:
    arr = np.asarray(null_values, dtype=np.float64)
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = float((actual - float(arr.mean())) / (std + 1e-12))
    p = float((arr >= actual).mean()) if higher_is_better else float((arr <= actual).mean())
    return {"z": z, "p": p, "null_mean": float(arr.mean()), "null_std": std}


def sample_group_null(
    sectors: pd.DataFrame,
    selected: pd.DataFrame,
    group_cols: list[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    sampled_parts = []
    selected = selected.copy()
    selected["_draw_group"] = [
        tuple(row) for row in selected[group_cols].itertuples(index=False, name=None)
    ]
    group_counts = selected["_draw_group"].value_counts().to_dict()

    for group_key, count in group_counts.items():
        pool_mask = np.ones(len(sectors), dtype=bool)
        for col, value in zip(group_cols, group_key):
            pool_mask &= sectors[col].to_numpy() == value
        pool = sectors[pool_mask]
        if pool.empty:
            target = group_key[group_cols.index("target")] if "target" in group_cols else None
            pool = sectors[sectors["target"].eq(target)] if target is not None else sectors
        sampled = pool.sample(
            n=int(count),
            replace=len(pool) < int(count),
            random_state=int(rng.integers(0, 2**31 - 1)),
        ).copy()

        selected_group = selected[selected["_draw_group"].map(lambda value: value == group_key)]
        abs_moves = selected_group["abs_move"].astype(float).to_numpy()
        if len(abs_moves) == 0:
            sampled["abs_move"] = 1.0
        else:
            sampled["abs_move"] = rng.permutation(abs_moves) if len(abs_moves) == len(sampled) else rng.choice(abs_moves, size=len(sampled), replace=True)
        sampled["source_class"] = np.where(sampled["teacher_has_action"], "teacher", "lrj_extra")
        sampled_parts.append(sampled)

    out = pd.concat(sampled_parts, ignore_index=True)
    return out


def null_distribution(
    sectors: pd.DataFrame,
    selected: pd.DataFrame,
    group_cols: list[str],
    iterations: int,
    seed: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    rng = np.random.default_rng(seed)
    rows = []
    for idx in range(iterations):
        draw = sample_group_null(sectors, selected, group_cols, rng)
        summary = summarize(draw)
        rows.append(
            {
                "iteration": idx,
                "joint_safety_weighted": summary["joint_safety_weighted"],
                "hardworld_safe_weighted": summary["hardworld_safe_weighted"],
                "broad_safe_weighted": summary["broad_safe_weighted"],
                "joint_risk_weighted": summary["joint_risk_weighted"],
                "hardworld_top_toxic_exposure": summary["hardworld_top_toxic_exposure"],
                "broad_top_toxic_exposure": summary["broad_top_toxic_exposure"],
                "broad_safe_hardworld_toxic_exposure": summary["broad_safe_hardworld_toxic_exposure"],
                "dual_safe_exposure": summary["dual_safe_exposure"],
            }
        )
    null = pd.DataFrame(rows)
    actual = summarize(selected)
    stats = {
        "group_cols": group_cols,
        "iterations": iterations,
        "joint_safety_weighted": z_and_p(float(actual["joint_safety_weighted"]), null["joint_safety_weighted"].tolist(), True),
        "hardworld_safe_weighted": z_and_p(float(actual["hardworld_safe_weighted"]), null["hardworld_safe_weighted"].tolist(), True),
        "broad_safe_weighted": z_and_p(float(actual["broad_safe_weighted"]), null["broad_safe_weighted"].tolist(), True),
        "joint_risk_weighted": z_and_p(float(actual["joint_risk_weighted"]), null["joint_risk_weighted"].tolist(), False),
        "hardworld_top_toxic_exposure": z_and_p(float(actual["hardworld_top_toxic_exposure"]), null["hardworld_top_toxic_exposure"].tolist(), False),
        "broad_safe_hardworld_toxic_exposure": z_and_p(float(actual["broad_safe_hardworld_toxic_exposure"]), null["broad_safe_hardworld_toxic_exposure"].tolist(), False),
        "dual_safe_exposure": z_and_p(float(actual["dual_safe_exposure"]), null["dual_safe_exposure"].tolist(), True),
    }
    return null, stats


def verdict_for_variant(actual: dict[str, object], target_null: dict[str, object], source_null: dict[str, object]) -> dict[str, object]:
    hard_exposure = float(actual["hardworld_top_toxic_exposure"])
    conflict_exposure = float(actual["broad_safe_hardworld_toxic_exposure"])
    joint_z = float(target_null["joint_safety_weighted"]["z"])
    source_conflict_p = float(source_null["broad_safe_hardworld_toxic_exposure"]["p"])
    target_conflict_p = float(target_null["broad_safe_hardworld_toxic_exposure"]["p"])
    target_hard_p = float(target_null["hardworld_top_toxic_exposure"]["p"])

    if (
        hard_exposure <= 1e-12
        and conflict_exposure <= 1e-12
        and joint_z >= 2.0
        and target_conflict_p <= 0.05
        and source_conflict_p <= 0.05
    ):
        status = "factorized_decoder_stress_supported"
        interpretation = "Selected exposure is safer than target-matched feasible nulls; factorized action-health is action-grade locally."
    elif hard_exposure <= 1e-12 and conflict_exposure <= 1e-12 and target_conflict_p <= 0.15:
        status = "factorized_decoder_alive_but_source_null_weak"
        interpretation = "The decoder removes hard/conflict exposure, but matched-source null separation is weaker or partly degenerate."
    else:
        status = "factorized_decoder_not_supported_by_stress"
        interpretation = "The decoder does not beat feasible nulls on the intended hard-world/conflict safety axes."

    return {
        "status": status,
        "interpretation": interpretation,
        "hardworld_top_toxic_exposure": hard_exposure,
        "broad_safe_hardworld_toxic_exposure": conflict_exposure,
        "target_null_joint_safety_z": joint_z,
        "target_null_conflict_p": target_conflict_p,
        "target_null_hard_top_p": target_hard_p,
        "source_null_conflict_p": source_conflict_p,
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Variant | Verdict | Cells | Joint safety | Target-null joint z | Hard-toxic exposure | Conflict exposure |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in readout["variants"].items():
        actual = item["actual"]
        verdict = item["verdict"]
        rows.append(
            f"| `{variant}` | `{verdict['status']}` | `{actual['cells']}` | "
            f"`{fmt(actual['joint_safety_weighted'], 4)}` | `{fmt(verdict['target_null_joint_safety_z'], 2)}` | "
            f"`{fmt(actual['hardworld_top_toxic_exposure'], 4)}` | `{fmt(actual['broad_safe_hardworld_toxic_exposure'], 4)}` |"
        )

    baseline = readout.get("scalar_baseline", {})
    baseline_lines = []
    if baseline:
        baseline_lines = [
            "## Scalar Toxicity Baseline",
            "",
            f"- Cells: `{baseline['cells']}`",
            f"- Joint safety weighted: `{fmt(baseline['joint_safety_weighted'], 4)}`",
            f"- H088 top-toxic exposure: `{fmt(baseline['hardworld_top_toxic_exposure'], 4)}`",
            f"- Broad-safe/H088-toxic exposure: `{fmt(baseline['broad_safe_hardworld_toxic_exposure'], 4)}`",
            "",
        ]

    return "\n".join(
        [
            "# Factorized Toxicity Decoder Stress Audit",
            "",
            "이 audit은 factorized toxicity decoder가 단순히 upload-safe인지가 아니라, target/source 구조를 맞춘 feasible null보다 hard-world/conflict exposure를 더 잘 피하는지 검증한다.",
            "",
            "## Verdict Table",
            "",
            *rows,
            "",
            *baseline_lines,
            "## Interpretation",
            "",
            "- target-only null은 같은 target count만 보존하므로 선택 자체가 얼마나 특이한지 본다.",
            "- source-matched null은 teacher/LRJ source 구조까지 보존하므로 더 보수적이다.",
            "- source-matched null이 약하거나 degenerate해도, target-null에서 hard/conflict exposure가 낮으면 decoder 방향은 살아 있다.",
            "- 이 결과는 public/private LB를 보장하지 않는다. 외부 제출 전 local action-health stress만 검증한다.",
            "",
        ]
    )


def run(iterations: int = 1500, seed: int = 20260610) -> dict[str, object]:
    sectors = load_sectors()
    readout = read_json(READOUT_JSON)
    scalar_baseline = load_scalar_baseline(sectors)
    variants: dict[str, object] = {}
    summary_rows = []

    for offset, variant in enumerate(sorted(readout.get("variants", {}))):
        audit = load_variant_audit(readout, variant)
        target_null_df, target_null = null_distribution(
            sectors,
            audit,
            ["target"],
            iterations=iterations,
            seed=seed + 10 * offset,
        )
        source_null_df, source_null = null_distribution(
            sectors,
            audit,
            ["target", "teacher_has_action", "lrj_has_cell"],
            iterations=iterations,
            seed=seed + 10 * offset + 1,
        )
        target_null_df.to_csv(OUT / f"factorized_toxicity_decoder_{variant}_target_null.csv", index=False)
        source_null_df.to_csv(OUT / f"factorized_toxicity_decoder_{variant}_source_matched_null.csv", index=False)
        actual = summarize(audit)
        verdict = verdict_for_variant(actual, target_null, source_null)
        variants[variant] = {
            "actual": actual,
            "target_only_null": target_null,
            "source_matched_null": source_null,
            "verdict": verdict,
            "submission_file": readout["variants"][variant]["submission_file"],
        }
        summary_rows.append(
            {
                "variant": variant,
                "submission_file": readout["variants"][variant]["submission_file"],
                "verdict": verdict["status"],
                "cells": actual["cells"],
                "joint_safety_weighted": actual["joint_safety_weighted"],
                "target_null_joint_safety_z": verdict["target_null_joint_safety_z"],
                "hardworld_top_toxic_exposure": actual["hardworld_top_toxic_exposure"],
                "target_null_hard_top_p": verdict["target_null_hard_top_p"],
                "broad_safe_hardworld_toxic_exposure": actual["broad_safe_hardworld_toxic_exposure"],
                "target_null_conflict_p": verdict["target_null_conflict_p"],
                "source_null_conflict_p": verdict["source_null_conflict_p"],
            }
        )

    baseline_summary = summarize(scalar_baseline) if scalar_baseline is not None else {}
    result = {
        "audit": "Factorized Toxicity Decoder Stress Audit",
        "status": "stress_audit_ready",
        "iterations": iterations,
        "seed": seed,
        "scalar_baseline": baseline_summary,
        "variants": variants,
    }
    pd.DataFrame(summary_rows).to_csv(SUMMARY_CSV, index=False)
    AUDIT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    AUDIT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
