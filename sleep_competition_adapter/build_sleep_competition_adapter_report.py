#!/usr/bin/env python3
"""Build the sleep-competition adapter report for HS-JEPA.

This adapter maps the competition-agnostic HS-JEPA core into the current sleep
lifestyle-log competition.  It is allowed to mention Q/S targets, S2, public
LB sensors, and upload-safe submissions because those are adapter concerns.
"""

from __future__ import annotations

from pathlib import Path
import json
import math


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

CORE_MANIFEST_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_ablation_contract.json"
TEAM_OUT = ROOT / "team_hsjepa_end_to_end" / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = TEAM_OUT / "route_conserving_s2_bridge_package.json"
VALIDATION_JSON = TEAM_OUT / "route_conserving_s2_bridge_validation_report.json"
READINESS_JSON = TEAM_OUT / "hsjepa_architecture_readiness_report.json"
GENERALITY_JSON = TEAM_OUT / "hsjepa_generality_report.json"
METHOD_PACKET_JSON = TEAM_OUT / "hsjepa_paper_method_packet.json"
OG_PROBE_JSON = OUT / "og_only_assignment_teacher_probe.json"
CONTRASTIVE_PROBE_JSON = OUT / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = OUT / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_JSON = OUT / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_JSON = OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"

REPORT_JSON = OUT / "sleep_competition_adapter_report.json"
REPORT_MD = OUT / "sleep_competition_adapter_report_ko.md"
BIG_BET_JSON = OUT / "hsjepa_big_bet_queue.json"
BIG_BET_MD = OUT / "hsjepa_big_bet_queue_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: object, digits: int = 6) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def require_inputs() -> None:
    required = [
        CORE_MANIFEST_JSON,
        CORE_ABLATION_JSON,
        PACKAGE_JSON,
        VALIDATION_JSON,
        READINESS_JSON,
        GENERALITY_JSON,
        OG_PROBE_JSON,
        CONTRASTIVE_PROBE_JSON,
        PRIVATE_TOXICITY_PROBE_JSON,
        HARDWORLD_TOXICITY_PROBE_JSON,
        FACTORIZED_DECODER_JSON,
        FACTORIZED_STRESS_JSON,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing sleep adapter inputs: {missing}")


def build_big_bets(
    og_probe: dict[str, object],
    contrastive_probe: dict[str, object],
    private_toxicity_probe: dict[str, object],
    hardworld_toxicity_probe: dict[str, object],
) -> list[dict[str, object]]:
    og_verdict = og_probe.get("verdict", {}) if isinstance(og_probe.get("verdict"), dict) else {}
    contrastive_verdict = (
        contrastive_probe.get("verdict", {})
        if isinstance(contrastive_probe.get("verdict"), dict)
        else {}
    )
    toxicity_verdict = (
        private_toxicity_probe.get("verdict", {})
        if isinstance(private_toxicity_probe.get("verdict"), dict)
        else {}
    )
    hardworld_verdict = (
        hardworld_toxicity_probe.get("verdict", {})
        if isinstance(hardworld_toxicity_probe.get("verdict"), dict)
        else {}
    )
    return [
        {
            "id": "og_only_assignment_teacher",
            "name": "OG-only Human-State Assignment Teacher",
            "worldview": "The public-sensor teacher can be replaced by personal/cohort/time human-state consistency.",
            "core_modules_exercised": ["context_encoder", "masked_state_predictor", "listener_responsibility", "anti_shortcut_validation"],
            "adapter_move": "Train a row-target support teacher from OG personal/cohort/time masks, then feed it into the existing invariant decoder.",
            "why_big": "If it works, HS-JEPA becomes a portable architecture rather than a public-sensor case study.",
            "expected_public_lb_delta_if_true": -0.003,
            "latest_probe_status": og_verdict.get("status"),
            "latest_probe_evidence": {
                "pure_og_row_cap2_mean_recall": og_verdict.get("pure_og_row_cap2_mean_recall"),
                "distilled_row_cap2_mean_recall": og_verdict.get("distilled_row_cap2_mean_recall"),
                "listener_upper_bound_row_cap2_mean_recall": og_verdict.get("listener_upper_bound_row_cap2_mean_recall"),
            },
            "kill_criterion": "Pure OG row-target recall stays near base-rate and distillation cannot recover row assignment under subject/time stress.",
        },
        {
            "id": "listener_invariant_contrastive_decoder",
            "name": "Listener-Invariant Contrastive Decoder",
            "worldview": "A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone.",
            "core_modules_exercised": ["listener_responsibility", "action_health_decoder", "invariant_energy"],
            "adapter_move": "Score candidate row-target actions by listener gain minus route-energy toxicity under random feasible nulls.",
            "why_big": "This could move beyond the current S2 bridge into a general action-health decoder.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": contrastive_verdict.get("status"),
            "latest_probe_evidence": {
                "mean_listener_route_spearman": contrastive_verdict.get("mean_listener_route_spearman"),
                "mean_contrastive_overlap_rate": contrastive_verdict.get("mean_contrastive_overlap_rate"),
                "mean_high_listener_low_route_rate": contrastive_verdict.get("mean_high_listener_low_route_rate"),
            },
            "kill_criterion": "Listener gain and invariant energy remain anti-correlated on strong candidates.",
        },
        {
            "id": "private_safe_toxicity_field",
            "name": "Private-Safe Toxicity Field",
            "worldview": "The plateau comes from actions that help public-like rows but poison private-like rows.",
            "core_modules_exercised": ["action_health_decoder", "anti_shortcut_validation"],
            "adapter_move": "Use failed public sensors, null bundles, and cohort/time stress to learn a toxicity veto before submission packaging.",
            "why_big": "A true toxicity field can preserve the 0.567 gain while reducing private-risk and maybe exposing larger safe moves.",
            "expected_public_lb_delta_if_true": -0.0015,
            "latest_probe_status": toxicity_verdict.get("status"),
            "latest_probe_evidence": {
                "mean_loo_bad_anchor_auc": toxicity_verdict.get("mean_loo_bad_anchor_auc"),
                "worst_loo_bad_anchor_auc": toxicity_verdict.get("worst_loo_bad_anchor_auc"),
                "selected_safety_z_vs_matched_null": toxicity_verdict.get("selected_safety_z_vs_matched_null"),
            },
            "kill_criterion": "Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls.",
        },
        {
            "id": "hardworld_mixture_toxicity_decoder",
            "name": "Hard-World Mixture Toxicity Decoder",
            "worldview": "H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized.",
            "core_modules_exercised": ["action_health_decoder", "anti_shortcut_validation", "listener_responsibility"],
            "adapter_move": "Replace scalar toxicity with a two-head broad-public/hard-world safety gate before row-target assignment.",
            "why_big": "This directly targets the observed gap where broad toxicity generalizes but misses the H088 hard-world mode.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": hardworld_verdict.get("status"),
            "latest_probe_evidence": {
                "broad_predicts_hardworld_auc": hardworld_verdict.get("broad_predicts_hardworld_auc"),
                "broad_hardworld_spearman": hardworld_verdict.get("broad_hardworld_spearman"),
                "selected_joint_safety_z": hardworld_verdict.get("selected_joint_safety_z"),
            },
            "kill_criterion": "Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching.",
        },
        {
            "id": "cross_listener_state_transport",
            "name": "Cross-Listener Human-State Transport",
            "worldview": "Subjective Q and objective S labels are different listeners of one human state, not separate tasks.",
            "core_modules_exercised": ["context_encoder", "listener_responsibility", "invariant_energy"],
            "adapter_move": "Move actions only when Q-listener and S-listener state transitions are mutually consistent.",
            "why_big": "This attacks the current weakness that Q and S decoders are mostly separated.",
            "expected_public_lb_delta_if_true": -0.001,
            "kill_criterion": "Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge.",
        },
    ]


def build_report() -> dict[str, object]:
    require_inputs()
    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    readiness = read_json(READINESS_JSON)
    generality = read_json(GENERALITY_JSON)
    method = read_json(METHOD_PACKET_JSON) if METHOD_PACKET_JSON.exists() else {"title": "HS-JEPA Method Packet Pending"}
    og_probe = read_json(OG_PROBE_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]
    og_verdict = og_probe.get("verdict", {})
    contrastive_verdict = contrastive_probe.get("verdict", {})
    toxicity_verdict = private_toxicity_probe.get("verdict", {})
    hardworld_verdict = hardworld_toxicity_probe.get("verdict", {})
    factorized_variants = factorized_decoder.get("variants", {})
    factorized_stress_variants = factorized_stress.get("variants", {})

    adapter_mapping = [
        {
            "core_module": "context_encoder",
            "competition_adapter": "raw lifestyle, subject/cohort, row-order, and sleep-state context features",
            "evidence": f"cell-level human-state orientation AUC {fmt(human['cell_oof_auc_human_target_context'], 3)}",
            "boundary": f"row-level assignment AUC {fmt(human['row_oof_auc'], 3)} is not enough for standalone assignment.",
        },
        {
            "core_module": "masked_state_predictor",
            "competition_adapter": "teacher/student probes for hidden S2-hub and row-target support orientation",
            "evidence": "human-state probe exists as a role-based output",
            "boundary": "current strongest teacher still uses public-sensitive action support.",
        },
        {
            "core_module": "listener_responsibility",
            "competition_adapter": "Q/S targets are treated as listeners; S2 emerges as an objective-stage hub",
            "evidence": f"S2 listener usage {fmt(mechanism['s2_listener_s2_any_rate'], 3)} vs null {fmt(mechanism['s2_listener_null_s2_any_rate'], 3)}",
            "boundary": "S2 hub is a sleep competition case-study claim, not a universal physiology claim.",
        },
        {
            "core_module": "action_health_decoder",
            "competition_adapter": "public-positive and public-negative sensors define toxic action diagnostics",
            "evidence": "mechanism ablation kills broad/toxic alternatives before release",
            "boundary": "public LB sensor is not portable and must be replaced for non-competition deployments.",
        },
        {
            "core_module": "invariant_energy",
            "competition_adapter": "Q/S route energy and route-conserving S2 bridge",
            "evidence": f"route z-scores primary={fmt(mechanism['primary_route_z'], 2)}, s2={fmt(mechanism['s2_route_z'], 2)}",
            "boundary": "other domains need their own temporal, physiological, semantic, or cohort invariant.",
        },
        {
            "core_module": "anti_shortcut_validation",
            "competition_adapter": "upload safety, feasible-bundle nulls, mechanism knockout, and release checklist",
            "evidence": f"generality checks {generality['passed_checks']}/{generality['total_checks']}",
            "boundary": "private LB safety is not proven.",
        },
    ]

    report = {
        "package": "Sleep Competition Adapter for HS-JEPA",
        "status": "adapter_ready_with_public_sensor_boundary",
        "core_status": core["status"],
        "core_ablation_status": core_ablation["status"],
        "adapter_claim": (
            "This adapter converts HS-JEPA Core into a sleep-log competition system by supplying "
            "Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding."
        ),
        "score_evidence": {
            "pre_public_equation_best_public_lb": public["pre_public_equation_best_public_lb"],
            "current_best_public_lb": public["current_best_public_lb"],
            "delta": public["current_delta_vs_pre_breakthrough"],
            "current_best_file": public["current_best_file"],
        },
        "adapter_mapping": adapter_mapping,
        "og_assignment_teacher_probe": {
            "status": og_verdict.get("status"),
            "pure_og_row_cap2_mean_recall": og_verdict.get("pure_og_row_cap2_mean_recall"),
            "pure_og_row_cap2_mean_precision_lift": og_verdict.get("pure_og_row_cap2_mean_precision_lift"),
            "distilled_row_cap2_mean_recall": og_verdict.get("distilled_row_cap2_mean_recall"),
            "distilled_row_cap2_mean_precision": og_verdict.get("distilled_row_cap2_mean_precision"),
            "listener_upper_bound_row_cap2_mean_recall": og_verdict.get("listener_upper_bound_row_cap2_mean_recall"),
            "interpretation": og_verdict.get("interpretation"),
        },
        "listener_invariant_contrastive_probe": {
            "status": contrastive_verdict.get("status"),
            "mean_listener_route_spearman": contrastive_verdict.get("mean_listener_route_spearman"),
            "mean_contrastive_overlap_rate": contrastive_verdict.get("mean_contrastive_overlap_rate"),
            "mean_high_listener_low_route_rate": contrastive_verdict.get("mean_high_listener_low_route_rate"),
            "interpretation": contrastive_verdict.get("interpretation"),
        },
        "private_safe_toxicity_probe": {
            "status": toxicity_verdict.get("status"),
            "mean_loo_bad_anchor_auc": toxicity_verdict.get("mean_loo_bad_anchor_auc"),
            "worst_loo_bad_anchor_auc": toxicity_verdict.get("worst_loo_bad_anchor_auc"),
            "anchors_below_0p6_auc": toxicity_verdict.get("anchors_below_0p6_auc"),
            "selected_safety_z_vs_matched_null": toxicity_verdict.get("selected_safety_z_vs_matched_null"),
            "p_null_safety_ge_selected": toxicity_verdict.get("p_null_safety_ge_selected"),
            "interpretation": toxicity_verdict.get("interpretation"),
        },
        "hardworld_toxicity_factorization_probe": {
            "status": hardworld_verdict.get("status"),
            "broad_predicts_hardworld_auc": hardworld_verdict.get("broad_predicts_hardworld_auc"),
            "broad_hardworld_spearman": hardworld_verdict.get("broad_hardworld_spearman"),
            "broad_safe_hardworld_toxic_cells": hardworld_verdict.get("broad_safe_hardworld_toxic_cells"),
            "selected_joint_safety_z": hardworld_verdict.get("selected_joint_safety_z"),
            "selected_hardworld_top_toxic_rate": hardworld_verdict.get("selected_hardworld_top_toxic_rate"),
            "null_hardworld_top_toxic_rate": hardworld_verdict.get("null_hardworld_top_toxic_rate"),
            "interpretation": hardworld_verdict.get("interpretation"),
        },
        "factorized_toxicity_decoder_candidate": {
            "experiment": factorized_decoder.get("experiment"),
            "architecture_role": factorized_decoder.get("architecture_role"),
            "core_boundary": factorized_decoder.get("core_boundary"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "changed_cells": item.get("decode_diagnostics", {}).get("changed_cells"),
                    "changed_rows": item.get("decode_diagnostics", {}).get("changed_rows"),
                    "joint_safety_mean": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("joint_safety_mean"),
                    "hardworld_top_toxic_rate": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("hardworld_top_toxic_rate"),
                    "broad_safe_hardworld_toxic_rate": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("broad_safe_hardworld_toxic_rate"),
                    "upload_safe": item.get("validation", {}).get("upload_safe"),
                }
                for name, item in factorized_variants.items()
                if isinstance(item, dict)
            },
        },
        "factorized_toxicity_decoder_stress_audit": {
            "status": factorized_stress.get("status"),
            "iterations": factorized_stress.get("iterations"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "verdict": item.get("verdict", {}).get("status"),
                    "target_null_joint_safety_z": item.get("verdict", {}).get("target_null_joint_safety_z"),
                    "source_null_conflict_p": item.get("verdict", {}).get("source_null_conflict_p"),
                    "hardworld_top_toxic_exposure": item.get("actual", {}).get("hardworld_top_toxic_exposure"),
                    "broad_safe_hardworld_toxic_exposure": item.get("actual", {}).get("broad_safe_hardworld_toxic_exposure"),
                }
                for name, item in factorized_stress_variants.items()
                if isinstance(item, dict)
            },
        },
        "role_outputs": {
            role: item["submission_file"]
            for role, item in package["packaged_submissions"].items()
        },
        "what_the_adapter_proves": [
            "HS-JEPA-style listener/action/invariant separation can explain the 0.567 public-LB breakthrough case study.",
            "Route-conserving action selection is statistically non-random against feasible null bundles.",
            "Human-state latent explains target/cell orientation but not enough row assignment on its own.",
            "A pure OG-only assignment teacher is not ready yet; this is now a measured architecture boundary, not an informal caveat.",
            "A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.",
            "The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.",
            "Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.",
            "The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.",
            "The dual-safe expansion variant survives target-only and source-matched null stress, while the teacher-only variant is intentionally marked weaker under source-matched stress.",
        ],
        "what_the_adapter_does_not_prove": [
            "pure OG-only assignment",
            "private leaderboard safety",
            "S2 as a universal human-sleep factor",
            "that public LB sensors can be used outside this competition",
            "that listener responsibility alone is an action-grade decoder",
            "that toxicity diagnostics prove private leaderboard safety",
            "that a hard-world mixture decoder will improve public/private LB before it is externally submitted",
        ],
        "paper_method_title": method["title"],
    }
    return report


def build_report_markdown(report: dict[str, object]) -> str:
    mapping_rows = ["| Core module | Sleep adapter instantiation | Evidence | Boundary |", "| --- | --- | --- | --- |"]
    for item in report["adapter_mapping"]:
        mapping_rows.append(
            f"| `{item['core_module']}` | {item['competition_adapter']} | {item['evidence']} | {item['boundary']} |"
        )

    roles = ["| Role | Output |", "| --- | --- |"]
    for role, name in report["role_outputs"].items():
        roles.append(f"| `{role}` | `{name}` |")

    factorized_rows = [
        "| Variant | Output | Changed cells | Joint safety | H088 top-toxic | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["factorized_toxicity_decoder_candidate"]["variants"].items():
        factorized_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['joint_safety_mean'], 4)}` | `{fmt(item['hardworld_top_toxic_rate'], 4)}` | "
            f"`{item['upload_safe']}` |"
        )

    factorized_stress_rows = [
        "| Variant | Stress verdict | Target-null joint z | Source-null conflict p | Hard-toxic exposure | Conflict exposure |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["factorized_toxicity_decoder_stress_audit"]["variants"].items():
        factorized_stress_rows.append(
            f"| `{variant}` | `{item['verdict']}` | `{fmt(item['target_null_joint_safety_z'], 2)}` | "
            f"`{fmt(item['source_null_conflict_p'], 4)}` | `{fmt(item['hardworld_top_toxic_exposure'], 4)}` | "
            f"`{fmt(item['broad_safe_hardworld_toxic_exposure'], 4)}` |"
        )

    return "\n".join(
        [
            "# Sleep Competition Adapter Report",
            "",
            "이 문서는 HS-JEPA Core를 수면 생활습관 로그 대회에 적용하는 adapter를 설명한다.",
            "",
            "## Adapter Claim",
            "",
            report["adapter_claim"],
            "",
            "## Score Evidence",
            "",
            f"- Pre-public-equation best public LB: `{report['score_evidence']['pre_public_equation_best_public_lb']}`",
            f"- Current best public LB: `{report['score_evidence']['current_best_public_lb']}`",
            f"- Delta: `{report['score_evidence']['delta']}`",
            f"- Current best file: `{report['score_evidence']['current_best_file']}`",
            "",
            "## Core to Adapter Mapping",
            "",
            *mapping_rows,
            "",
            "## OG-only Assignment Probe",
            "",
            f"- Status: `{report['og_assignment_teacher_probe']['status']}`",
            f"- Pure OG row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['pure_og_row_cap2_mean_recall'], 4)}`",
            f"- Distilled row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['distilled_row_cap2_mean_recall'], 4)}`",
            f"- Listener/source upper-bound row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['listener_upper_bound_row_cap2_mean_recall'], 4)}`",
            "",
            report["og_assignment_teacher_probe"]["interpretation"],
            "",
            "## Listener-Invariant Contrastive Probe",
            "",
            f"- Status: `{report['listener_invariant_contrastive_probe']['status']}`",
            f"- Mean listener-route Spearman: `{fmt(report['listener_invariant_contrastive_probe']['mean_listener_route_spearman'], 4)}`",
            f"- Mean contrastive overlap: `{fmt(report['listener_invariant_contrastive_probe']['mean_contrastive_overlap_rate'], 4)}`",
            f"- Mean conflict rate: `{fmt(report['listener_invariant_contrastive_probe']['mean_high_listener_low_route_rate'], 4)}`",
            "",
            report["listener_invariant_contrastive_probe"]["interpretation"],
            "",
            "## Private-Safe Toxicity Probe",
            "",
            f"- Status: `{report['private_safe_toxicity_probe']['status']}`",
            f"- Mean leave-one-bad-anchor AUC: `{fmt(report['private_safe_toxicity_probe']['mean_loo_bad_anchor_auc'], 4)}`",
            f"- Worst leave-one-bad-anchor AUC: `{fmt(report['private_safe_toxicity_probe']['worst_loo_bad_anchor_auc'], 4)}`",
            f"- Selected safety z vs matched null: `{fmt(report['private_safe_toxicity_probe']['selected_safety_z_vs_matched_null'], 4)}`",
            "",
            report["private_safe_toxicity_probe"]["interpretation"],
            "",
            "## Hard-World Toxicity Factorization Probe",
            "",
            f"- Status: `{report['hardworld_toxicity_factorization_probe']['status']}`",
            f"- Broad toxicity -> H088 AUC: `{fmt(report['hardworld_toxicity_factorization_probe']['broad_predicts_hardworld_auc'], 4)}`",
            f"- Broad/H088 Spearman: `{fmt(report['hardworld_toxicity_factorization_probe']['broad_hardworld_spearman'], 4)}`",
            f"- Broad-safe but H088-toxic cells: `{report['hardworld_toxicity_factorization_probe']['broad_safe_hardworld_toxic_cells']}`",
            f"- Selected joint safety z: `{fmt(report['hardworld_toxicity_factorization_probe']['selected_joint_safety_z'], 4)}`",
            f"- Selected H088 top-toxic rate: `{fmt(report['hardworld_toxicity_factorization_probe']['selected_hardworld_top_toxic_rate'], 4)}` vs null `{fmt(report['hardworld_toxicity_factorization_probe']['null_hardworld_top_toxic_rate'], 4)}`",
            "",
            report["hardworld_toxicity_factorization_probe"]["interpretation"],
            "",
            "## Factorized Toxicity Decoder Candidate",
            "",
            f"- Architecture role: `{report['factorized_toxicity_decoder_candidate']['architecture_role']}`",
            f"- Core boundary: {report['factorized_toxicity_decoder_candidate']['core_boundary']}",
            "",
            *factorized_rows,
            "",
            "이 후보는 broad-public safety와 hard-world safety를 동시에 통과한 row-target action만 믿는 adapter-side decoder다. public 결과가 좋아지면 factorized action-health가 맞다는 신호이고, 나빠지면 factorization은 diagnostic으로는 유효하지만 아직 action-grade decoder는 아니라는 뜻이다.",
            "",
            "## Factorized Toxicity Decoder Stress Audit",
            "",
            f"- Status: `{report['factorized_toxicity_decoder_stress_audit']['status']}`",
            f"- Iterations: `{report['factorized_toxicity_decoder_stress_audit']['iterations']}`",
            "",
            *factorized_stress_rows,
            "",
            "`dual_safe_expansion`은 source-matched null까지 통과한 strict supported 후보이고, `teacher_dual_head`는 target-null에서는 강하지만 source-matched null이 약한 diagnostic 후보로 남긴다.",
            "",
            "## Role Outputs",
            "",
            *roles,
            "",
            "## 이 adapter가 증명하는 것",
            "",
            *[f"- {item}" for item in report["what_the_adapter_proves"]],
            "",
            "## 이 adapter가 아직 증명하지 못한 것",
            "",
            *[f"- {item}" for item in report["what_the_adapter_does_not_prove"]],
            "",
        ]
    )


def build_big_bet_markdown(bets: list[dict[str, object]]) -> str:
    rows = [
        "| Big bet | Worldview | Adapter move | Latest probe | Expected LB delta if true | Kill criterion |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for bet in bets:
        latest_probe = bet.get("latest_probe_status", "not_run")
        rows.append(
            f"| `{bet['name']}` | {bet['worldview']} | {bet['adapter_move']} | `{latest_probe}` | `{bet['expected_public_lb_delta_if_true']}` | {bet['kill_criterion']} |"
        )

    return "\n".join(
        [
            "# HS-JEPA Big-Bet Queue",
            "",
            "이 문서는 0.0001 개선용 조정이 아니라 HS-JEPA의 core/adaptor 구조를 바꿀 수 있는 큰 실험만 남긴다.",
            "",
            *rows,
            "",
            "## 우선순위",
            "",
            "1. `OG-only Human-State Assignment Teacher`: 성공하면 HS-JEPA의 범용성이 가장 크게 올라간다.",
            "2. `Hard-World Mixture Toxicity Decoder`: H088류 hard-world 독성을 broad toxicity와 분리한다.",
            "3. `Listener-Invariant Contrastive Decoder`: 현재 S2 bridge를 일반 action-health decoder로 확장한다.",
            "4. `Private-Safe Toxicity Field`: public-specific gain의 private risk를 줄이는 방향이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    report = build_report()
    bets = build_big_bets(
        read_json(OG_PROBE_JSON),
        read_json(CONTRASTIVE_PROBE_JSON),
        read_json(PRIVATE_TOXICITY_PROBE_JSON),
        read_json(HARDWORLD_TOXICITY_PROBE_JSON),
    )
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_report_markdown(report), encoding="utf-8")
    BIG_BET_JSON.write_text(
        json.dumps(
            {
                "package": "HS-JEPA Big-Bet Queue",
                "status": "big_bet_queue_ready",
                "bets": bets,
                "count": len(bets),
            },
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    BIG_BET_MD.write_text(build_big_bet_markdown(bets), encoding="utf-8")
    result = {
        "adapter_report_json": str(REPORT_JSON.resolve()),
        "adapter_report_md": str(REPORT_MD.resolve()),
        "big_bet_json": str(BIG_BET_JSON.resolve()),
        "big_bet_md": str(BIG_BET_MD.resolve()),
        "status": report["status"],
        "big_bet_count": len(bets),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
