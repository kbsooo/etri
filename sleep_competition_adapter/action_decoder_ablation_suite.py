#!/usr/bin/env python3
"""Compare HS-JEPA sleep-adapter action decoders as module ablations.

This script does not create a new prediction file.  It answers a more
paper-facing and teammate-facing question:

    Which part of the HS-JEPA action decoder is currently carrying evidence?

The comparison is adapter-specific because it reads public-sensor submission
artifacts, Q/S route bridge candidates, and toxicity probes.  The reusable
HS-JEPA core remains competition-agnostic.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "action_decoder_ablation_suite"
OUT.mkdir(parents=True, exist_ok=True)

ROW_SUPPORT_JSON = HERE / "outputs" / "row_support_strict_action_decoder" / "row_support_strict_action_decoder_readout.json"
ROUTE_FRONTIER_JSON = HERE / "outputs" / "route_frontier_action_decoder" / "route_frontier_action_decoder_readout.json"
ROUTE_TOXICITY_FUSION_JSON = HERE / "outputs" / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_readout.json"
FACTORIZED_JSON = HERE / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = HERE / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"
LEDGER_CSV = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"

SUITE_JSON = OUT / "hsjepa_action_decoder_ablation_suite.json"
SUITE_MD = OUT / "hsjepa_action_decoder_ablation_suite_ko.md"
SUITE_CSV = OUT / "hsjepa_action_decoder_ablation_suite.csv"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def maybe_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def nested(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = mapping
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def fmt(value: Any, digits: int = 4) -> str:
    val = maybe_float(value)
    if val is None:
        return "n/a"
    return f"{val:.{digits}f}"


def rank01(values: pd.Series, higher: bool = True) -> pd.Series:
    if values.notna().sum() <= 1:
        return pd.Series([0.5] * len(values), index=values.index)
    ranks = values.rank(pct=True, method="average", ascending=not higher)
    return ranks.fillna(0.0)


def public_score_map() -> dict[str, float]:
    if not LEDGER_CSV.exists():
        return {}
    ledger = pd.read_csv(LEDGER_CSV)
    if not {"file", "public_lb"}.issubset(ledger.columns):
        return {}
    return {
        str(row["file"]): float(row["public_lb"])
        for row in ledger.to_dict("records")
        if pd.notna(row.get("file")) and pd.notna(row.get("public_lb"))
    }


def base_row(
    *,
    family: str,
    variant: str,
    submission_file: str | None,
    upload_safe: bool,
    changed_cells: int,
    architecture_claim: str,
    decoder_order: str,
    core_modules: list[str],
    public_lb: float | None,
) -> dict[str, Any]:
    return {
        "family": family,
        "variant": variant,
        "submission_file": submission_file,
        "upload_safe": bool(upload_safe),
        "changed_cells": int(changed_cells),
        "architecture_claim": architecture_claim,
        "decoder_order": decoder_order,
        "core_modules_exercised": ",".join(core_modules),
        "public_lb_observed": public_lb,
        "route_z": None,
        "matched_route_z": None,
        "matched_score_z": None,
        "safety_z": None,
        "toxicity_clear": None,
        "broad_hard_conflict_exposure": None,
        "hardworld_top_toxic_exposure": None,
        "route_boundary": "not_measured",
        "safety_boundary": "not_measured",
        "lb_sensor_priority": None,
        "module_ablation_interpretation": "",
    }


def collect_rows() -> list[dict[str, Any]]:
    public_scores = public_score_map()
    row_support = read_json(ROW_SUPPORT_JSON)
    route_frontier = read_json(ROUTE_FRONTIER_JSON)
    route_toxicity_fusion = read_json(ROUTE_TOXICITY_FUSION_JSON)
    factorized = read_json(FACTORIZED_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)
    rows: list[dict[str, Any]] = []

    for variant, item in sorted(factorized.get("variants", {}).items()):
        diag = item.get("decode_diagnostics", {})
        stress = factorized_stress.get("variants", {}).get(variant, {}).get("verdict", {})
        submission = item.get("submission_file")
        row = base_row(
            family="factorized_toxicity",
            variant=str(variant),
            submission_file=str(submission) if submission else None,
            upload_safe=bool(nested(item, "validation", "upload_safe", default=False)),
            changed_cells=int(nested(item, "validation", "changed_cells_vs_current_best", default=diag.get("changed_cells", 0))),
            architecture_claim="action-health must be factorized into broad-public and hard-world toxicity heads",
            decoder_order="toxicity_first",
            core_modules=["action_health_decoder", "anti_shortcut_validation"],
            public_lb=public_scores.get(str(submission)),
        )
        row.update(
            {
                "safety_z": maybe_float(stress.get("target_null_joint_safety_z")),
                "toxicity_clear": bool(
                    finite(stress.get("hardworld_top_toxic_exposure"), 1.0) == 0.0
                    and finite(stress.get("broad_safe_hardworld_toxic_exposure"), 1.0) == 0.0
                ),
                "broad_hard_conflict_exposure": maybe_float(stress.get("broad_safe_hardworld_toxic_exposure")),
                "hardworld_top_toxic_exposure": maybe_float(stress.get("hardworld_top_toxic_exposure")),
                "route_boundary": "route_not_claimed",
                "safety_boundary": str(stress.get("status", "unknown")),
                "module_ablation_interpretation": (
                    "Keeps action-health and anti-shortcut validation, but does not prove invariant route placement."
                ),
            }
        )
        rows.append(row)

    for variant, item in sorted(row_support.get("variants", {}).items()):
        stress = row_support.get("stress", {}).get(variant, {})
        submission = item.get("submission_file")
        row = base_row(
            family="row_support_strict",
            variant=str(variant),
            submission_file=str(submission) if submission else None,
            upload_safe=bool(nested(item, "validation", "upload_safe", default=False)),
            changed_cells=int(nested(item, "validation", "changed_cells_vs_current_best", default=0)),
            architecture_claim="masked row-support can choose safe route-conserving actions",
            decoder_order="row_support_first",
            core_modules=["masked_state_predictor", "action_health_decoder", "invariant_energy"],
            public_lb=public_scores.get(str(submission)),
        )
        row.update(
            {
                "route_z": maybe_float(nested(stress, "route_gain", "z")),
                "safety_z": maybe_float(nested(stress, "bundle_joint_safety", "z")),
                "matched_score_z": maybe_float(nested(stress, "support_route_safety_score", "z")),
                "toxicity_clear": True,
                "route_boundary": "route_tradeoff" if finite(nested(stress, "route_gain", "z"), -999.0) < 0 else "route_supported",
                "safety_boundary": "safety_supported" if finite(nested(stress, "bundle_joint_safety", "z"), 0.0) >= 2.0 else "safety_weak",
                "module_ablation_interpretation": (
                    "Shows row-support is real enough to select safe actions, but support-first decoding can lose route-null separation."
                ),
            }
        )
        rows.append(row)

    for variant, item in sorted(route_frontier.get("variants", {}).items()):
        stress = route_frontier.get("stress", {}).get(variant, {})
        broad = stress.get("broad", {}) if isinstance(stress, dict) else {}
        matched = stress.get("matched", {}) if isinstance(stress, dict) else {}
        submission = item.get("submission_file")
        row = base_row(
            family="route_frontier",
            variant=str(variant),
            submission_file=str(submission) if submission else None,
            upload_safe=bool(nested(item, "validation", "upload_safe", default=False)),
            changed_cells=int(nested(item, "validation", "changed_cells_vs_current_best", default=0)),
            architecture_claim="route-frontier selection should precede row-support and toxicity gates",
            decoder_order="route_first",
            core_modules=["action_health_decoder", "invariant_energy", "anti_shortcut_validation"],
            public_lb=public_scores.get(str(submission)),
        )
        row.update(
            {
                "route_z": maybe_float(nested(broad, "route_gain", "z")),
                "matched_route_z": maybe_float(nested(matched, "route_gain", "z")),
                "matched_score_z": maybe_float(nested(matched, "route_frontier_score", "z")),
                "safety_z": maybe_float(nested(broad, "bundle_joint_safety", "z")),
                "toxicity_clear": True,
                "route_boundary": (
                    "route_and_matched_score_supported"
                    if finite(nested(broad, "route_gain", "z"), 0.0) >= 2.0
                    and finite(nested(matched, "route_frontier_score", "z"), 0.0) >= 2.0
                    else "route_or_matched_boundary"
                ),
                "safety_boundary": "safety_supported" if finite(nested(broad, "bundle_joint_safety", "z"), 0.0) >= 2.0 else "safety_weak",
                "module_ablation_interpretation": (
                    "Keeps route invariant first. If this wins LB, the missing mechanism was action translation order, not more latent capacity."
                ),
            }
        )
        rows.append(row)

    for variant, item in sorted(route_toxicity_fusion.get("variants", {}).items()):
        stress = route_toxicity_fusion.get("stress", {}).get(variant, {})
        broad = stress.get("broad_route", {}) if isinstance(stress, dict) else {}
        matched = stress.get("toxicity_matched", {}) if isinstance(stress, dict) else {}
        actual = stress.get("actual", {}) if isinstance(stress, dict) else {}
        submission = item.get("submission_file")
        row = base_row(
            family="route_toxicity_fusion",
            variant=str(variant),
            submission_file=str(submission) if submission else None,
            upload_safe=bool(nested(item, "validation", "upload_safe", default=False)),
            changed_cells=int(nested(item, "validation", "changed_cells_vs_current_best", default=0)),
            architecture_claim="route-frontier selection should be translated through a factorized action-health field",
            decoder_order="route_first_then_factorized_toxicity",
            core_modules=["invariant_energy", "action_health_decoder", "anti_shortcut_validation"],
            public_lb=public_scores.get(str(submission)),
        )
        conflict_rate = finite(actual.get("conflict_bundle_rate"))
        hard_top_rate = finite(actual.get("hardworld_top_toxic_bundle_rate"))
        row.update(
            {
                "route_z": maybe_float(nested(broad, "route_gain", "z")),
                "matched_route_z": maybe_float(nested(matched, "route_gain", "z")),
                "matched_score_z": maybe_float(nested(matched, "route_toxicity_fusion_score", "z")),
                "safety_z": maybe_float(nested(matched, "bundle_joint_safety", "z")),
                "toxicity_clear": bool(conflict_rate == 0.0 and hard_top_rate == 0.0),
                "broad_hard_conflict_exposure": conflict_rate,
                "hardworld_top_toxic_exposure": hard_top_rate,
                "route_boundary": (
                    "route_and_fusion_supported"
                    if finite(nested(broad, "route_gain", "z"), 0.0) >= 1.5
                    and finite(nested(matched, "route_toxicity_fusion_score", "z"), 0.0) >= 2.0
                    else "route_fusion_boundary"
                ),
                "safety_boundary": (
                    "safety_supported"
                    if finite(nested(broad, "bundle_joint_safety", "z"), 0.0) >= 2.0
                    or finite(nested(matched, "bundle_joint_safety", "z"), 0.0) >= 1.0
                    else "safety_weak"
                ),
                "module_ablation_interpretation": (
                    "Fuses invariant route ordering with factorized broad-public/hard-world action-health. "
                    "If this beats route-frontier on LB, toxicity was the missing action decoder stage."
                ),
            }
        )
        rows.append(row)

    return rows


def score_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    route_component = (
        frame["route_z"].apply(lambda x: max(-1.0, min(1.4, finite(x) / 3.0)))
        + frame["matched_route_z"].apply(lambda x: max(-0.5, min(0.8, finite(x) / 4.0)))
        + frame["matched_score_z"].apply(lambda x: max(-0.5, min(0.9, finite(x) / 4.0)))
    )
    safety_component = frame["safety_z"].apply(lambda x: max(-0.5, min(1.5, finite(x) / 4.0)))
    changed_component = (frame["changed_cells"].clip(lower=0, upper=80) / 80.0).astype(float)
    upload_component = frame["upload_safe"].astype(float)
    toxicity_component = frame["toxicity_clear"].fillna(False).astype(float)
    public_component = pd.Series([0.0] * len(frame), index=frame.index)
    if frame["public_lb_observed"].notna().any():
        public_component = rank01(-frame["public_lb_observed"], higher=True).where(frame["public_lb_observed"].notna(), 0.0)

    route_missing_penalty = frame["route_z"].isna().astype(float) * 0.20
    route_tradeoff_penalty = frame["route_boundary"].eq("route_tradeoff").astype(float) * 0.35
    no_upload_penalty = (~frame["upload_safe"]).astype(float) * 1.00

    frame["lb_sensor_priority"] = (
        0.28 * route_component
        + 0.24 * safety_component
        + 0.16 * toxicity_component
        + 0.14 * changed_component
        + 0.12 * upload_component
        + 0.06 * public_component
        - route_missing_penalty
        - route_tradeoff_penalty
        - no_upload_penalty
    )
    frame = frame.sort_values(
        ["lb_sensor_priority", "route_z", "matched_score_z", "safety_z", "changed_cells"],
        ascending=[False, False, False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)
    frame["ablation_rank"] = range(1, len(frame) + 1)
    return frame


def build_findings(frame: pd.DataFrame) -> list[dict[str, Any]]:
    top = frame.iloc[0].to_dict() if not frame.empty else {}
    route_rows = frame.loc[frame["family"].isin(["route_frontier", "route_toxicity_fusion"])]
    row_support_rows = frame.loc[frame["family"].eq("row_support_strict")]
    factorized_rows = frame.loc[frame["family"].eq("factorized_toxicity")]
    fusion_rows = frame.loc[frame["family"].eq("route_toxicity_fusion")]
    best_route = route_rows.iloc[0].to_dict() if not route_rows.empty else {}
    best_support = row_support_rows.iloc[0].to_dict() if not row_support_rows.empty else {}
    best_factorized = factorized_rows.iloc[0].to_dict() if not factorized_rows.empty else {}
    best_fusion = fusion_rows.iloc[0].to_dict() if not fusion_rows.empty else {}

    return [
        {
            "claim": "Support-first decoding is not the full HS-JEPA action rule.",
            "evidence": (
                f"Best row-support route_z={fmt(best_support.get('route_z'))}, "
                f"while best route-frontier route_z={fmt(best_route.get('route_z'))}."
            ),
            "status": "survived_as_partial_module",
            "next_test": "Submit route-frontier before expanding support-first amplitudes.",
        },
        {
            "claim": "Invariant route energy is currently the sharper action-ordering signal.",
            "evidence": (
                f"Top ablation row is {top.get('family')}.{top.get('variant')} with priority "
                f"{fmt(top.get('lb_sensor_priority'))} and matched_score_z={fmt(top.get('matched_score_z'))}."
            ),
            "status": "alive",
            "next_test": "Use route-frontier as the next LB sensor; interpret failure as public/private toxicity dominance.",
        },
        {
            "claim": "Factorized action-health is necessary but not sufficient.",
            "evidence": (
                f"Best factorized decoder safety_z={fmt(best_factorized.get('safety_z'))}, "
                f"route boundary={best_factorized.get('route_boundary')}."
            ),
            "status": "alive_with_route_gap",
            "next_test": "Do not ship factorized toxicity alone unless route-preserving assignment is added.",
        },
        {
            "claim": "Route-first and toxicity-first are not alternatives; they compose into a decoder order.",
            "evidence": (
                f"Best fusion row is {best_fusion.get('variant')} with route_z={fmt(best_fusion.get('route_z'))} "
                f"and matched_score_z={fmt(best_fusion.get('matched_score_z'))}."
            ),
            "status": "alive" if best_fusion else "missing",
            "next_test": "Use route-toxicity fusion as the next adapter LB sensor if it outranks plain route-frontier.",
        },
        {
            "claim": "Open candidate route frontier is a true big-bet boundary.",
            "evidence": (
                "The open-route variant is upload-safe and route-supported locally, but it is outside the "
                "selected public seed set."
            ),
            "status": "high_information_if_submitted",
            "next_test": "If seed-route fails but open-route wins, the public-selected candidate pool was too narrow.",
        },
    ]


def build_verdict(frame: pd.DataFrame, findings: list[dict[str, Any]]) -> dict[str, Any]:
    if frame.empty:
        return {
            "status": "action_decoder_ablation_missing",
            "recommended_lb_sensor": None,
            "big_bet_sensor": None,
            "reason": "No decoder rows were available.",
        }
    safe = frame.loc[frame["upload_safe"].astype(bool)]
    top = safe.iloc[0] if not safe.empty else frame.iloc[0]
    big_bet = safe.loc[safe["family"].eq("route_frontier") & safe["variant"].eq("open_route_frontier")]
    big_bet_row = big_bet.iloc[0] if not big_bet.empty else top
    status = "action_decoder_ablation_ready_route_frontier_leads"
    if str(top["family"]) == "route_toxicity_fusion":
        status = "action_decoder_ablation_ready_route_toxicity_fusion_leads"
    elif str(top["family"]) != "route_frontier":
        status = "action_decoder_ablation_ready_non_route_leads"
    return {
        "status": status,
        "recommended_lb_sensor": {
            "family": str(top["family"]),
            "variant": str(top["variant"]),
            "submission_file": top.get("submission_file"),
            "priority": float(top["lb_sensor_priority"]),
        },
        "big_bet_sensor": {
            "family": str(big_bet_row["family"]),
            "variant": str(big_bet_row["variant"]),
            "submission_file": big_bet_row.get("submission_file"),
            "priority": float(big_bet_row["lb_sensor_priority"]),
        },
        "reason": (
            "The suite ranks action decoders by route-null survival, toxicity safety, upload safety, and action size. "
            "It is a submission-slot prioritizer, not a public-LB predictor."
        ),
        "findings": findings,
    }


def build_markdown(readout: dict[str, Any], frame: pd.DataFrame) -> str:
    rows = [
        "| Rank | Family | Variant | Changed | Route z | Matched score z | Safety z | Upload | Priority | File |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rec in frame.to_dict("records"):
        rows.append(
            f"| `{rec['ablation_rank']}` | `{rec['family']}` | `{rec['variant']}` | `{rec['changed_cells']}` | "
            f"`{fmt(rec['route_z'])}` | `{fmt(rec['matched_score_z'])}` | `{fmt(rec['safety_z'])}` | "
            f"`{rec['upload_safe']}` | `{fmt(rec['lb_sensor_priority'])}` | `{rec['submission_file']}` |"
        )

    finding_rows = ["| Claim | Status | Evidence | Next test |", "| --- | --- | --- | --- |"]
    for item in readout["findings"]:
        finding_rows.append(
            f"| {item['claim']} | `{item['status']}` | {item['evidence']} | {item['next_test']} |"
        )

    verdict = readout["verdict"]
    rec = verdict["recommended_lb_sensor"]
    big = verdict["big_bet_sensor"]
    return "\n".join(
        [
            "# HS-JEPA Action Decoder Ablation Suite",
            "",
            "이 문서는 HS-JEPA sleep adapter의 action decoder 후보들을 같은 좌표계에서 비교한다. 목적은 점수 예측이 아니라, 어떤 모듈이 현재 evidence를 들고 있는지 분해하는 것이다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Recommended LB sensor: `{rec['family']}.{rec['variant']}` -> `{rec['submission_file']}`",
            f"- Open big-bet sensor: `{big['family']}.{big['variant']}` -> `{big['submission_file']}`",
            f"- Reason: {verdict['reason']}",
            "",
            "## Decoder Ranking",
            "",
            *rows,
            "",
            "## Module Ablation Findings",
            "",
            *finding_rows,
            "",
            "## How To Read This",
            "",
            "- route-frontier가 이기면, HS-JEPA의 병목은 latent 발견보다 action ordering에 가깝다.",
            "- route-toxicity fusion이 이기면, action ordering 다음 병목은 factorized action-health gate였다는 뜻이다.",
            "- factorized toxicity가 이기면, public/private toxicity field가 route보다 강한 병목이다.",
            "- row-support strict가 이기면, masked row-support representation이 action-grade decoder로 번역되기 시작한 것이다.",
            "- open-route가 public에서 이기면, 기존 public-selected seed 후보 공간 자체가 좁았다는 큰 발견이다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    rows = collect_rows()
    frame = score_rows(rows)
    findings = build_findings(frame)
    verdict = build_verdict(frame, findings)
    frame.to_csv(SUITE_CSV, index=False)
    ranking = frame.astype(object).where(pd.notna(frame), None).to_dict("records")
    readout = {
        "experiment": "HS-JEPA Action Decoder Ablation Suite",
        "architecture_role": "sleep_competition_adapter_action_decoder_ablation_harness",
        "core_boundary": "This suite reads competition adapter outputs and must not be imported by HS-JEPA core.",
        "status": verdict["status"],
        "verdict": verdict,
        "findings": findings,
        "ranking": ranking,
        "inputs": {
            "row_support": str(ROW_SUPPORT_JSON.resolve()),
            "route_frontier": str(ROUTE_FRONTIER_JSON.resolve()),
            "route_toxicity_fusion": str(ROUTE_TOXICITY_FUSION_JSON.resolve()),
            "factorized_toxicity": str(FACTORIZED_JSON.resolve()),
            "factorized_stress": str(FACTORIZED_STRESS_JSON.resolve()),
        },
        "outputs": {
            "json": str(SUITE_JSON.resolve()),
            "markdown": str(SUITE_MD.resolve()),
            "csv": str(SUITE_CSV.resolve()),
        },
    }
    SUITE_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    SUITE_MD.write_text(build_markdown(readout, frame), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
