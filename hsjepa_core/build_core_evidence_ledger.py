#!/usr/bin/env python3
"""Build a paper-facing evidence ledger for the HS-JEPA core.

This is not a leaderboard adapter.  It reads public-free HS-JEPA core outputs
and classifies each result into one of three layers:

    core evidence       = hidden human-state representation works before action
    adapter evidence    = representation needs a competition-specific decoder
    diagnostic evidence = LeJEPA-style shortcut/collapse boundary

The goal is to keep the paper thesis honest: HS-JEPA should not be presented as
only a bag of row-target submission tweaks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "core_evidence_ledger"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "CORE_EVIDENCE_LEDGER_KO.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return ""
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def collect_cases() -> list[dict[str, Any]]:
    outputs = ROOT / "hsjepa_core" / "outputs"
    lifelog = load_json(outputs / "lifelog_core_state_evidence" / "lifelog_core_state_evidence_summary.json")
    world = load_json(outputs / "masked_context_world_model" / "masked_context_world_model_summary.json")
    manifold = load_json(
        outputs
        / "subject_invariant_listener_manifold_core"
        / "subject_invariant_listener_manifold_core_summary.json"
    )
    responsibility = load_json(
        outputs
        / "subject_invariant_listener_responsibility_field_core"
        / "subject_invariant_listener_responsibility_field_core_summary.json"
    )
    signed = load_json(
        outputs
        / "signed_listener_responsibility_direction_core"
        / "signed_listener_responsibility_direction_core_summary.json"
    )
    counterfactual_direction = load_json(
        outputs
        / "counterfactual_direction_pretext_core"
        / "counterfactual_direction_pretext_core_summary.json"
    )
    human_world = load_json(
        outputs
        / "human_state_world_model_core"
        / "human_state_world_model_summary.json"
    )
    routine_world = load_json(
        outputs
        / "routine_break_world_model_core"
        / "routine_break_world_model_summary.json"
    )
    sleep_pressure = load_json(
        outputs
        / "sleep_pressure_world_model_core"
        / "sleep_pressure_world_model_summary.json"
    )
    cohort_relative = load_json(
        outputs
        / "cohort_relative_world_model_core"
        / "cohort_relative_world_model_summary.json"
    )
    multi_target = load_json(
        outputs
        / "multi_target_human_state_world_model_core"
        / "multi_target_human_state_world_model_summary.json"
    )
    route_responsibility = load_json(
        outputs
        / "route_responsibility_world_model_core"
        / "route_responsibility_world_model_summary.json"
    )
    listener_readout = load_json(
        outputs
        / "listener_conditioned_route_readout_core"
        / "listener_conditioned_route_readout_summary.json"
    )
    subject_drift = load_json(
        outputs
        / "subject_drift_world_model_core"
        / "subject_drift_world_model_summary.json"
    )
    transition_retrieval = load_json(
        outputs
        / "episode_transition_retrieval_core"
        / "episode_transition_retrieval_summary.json"
    )
    prototype_grammar = load_json(
        outputs
        / "human_state_prototype_grammar_core"
        / "human_state_prototype_grammar_summary.json"
    )
    cross_subject_transport = load_json(
        outputs
        / "cross_subject_prototype_transport_core"
        / "cross_subject_prototype_transport_summary.json"
    )
    transported_listener = load_json(
        outputs
        / "transported_prototype_listener_readout_core"
        / "transported_prototype_listener_readout_summary.json"
    )
    label_free_listener = load_json(
        outputs
        / "label_free_transported_listener_responsibility_core"
        / "label_free_transported_listener_responsibility_summary.json"
    )
    learned_listener = load_json(
        outputs
        / "learned_listener_responsibility_pretext_core"
        / "learned_listener_responsibility_pretext_summary.json"
    )
    invariant_listener = load_json(
        outputs
        / "invariant_listener_responsibility_pretext_core"
        / "invariant_listener_responsibility_pretext_summary.json"
    )
    multi_head_listener = load_json(
        outputs
        / "multi_head_listener_responsibility_pretext_core"
        / "multi_head_listener_responsibility_pretext_summary.json"
    )
    listener_head_router = load_json(
        outputs
        / "listener_head_router_pretext_core"
        / "listener_head_router_pretext_summary.json"
    )
    learned_head_router = load_json(
        outputs
        / "learned_listener_head_router_core"
        / "learned_listener_head_router_summary.json"
    )
    global_residual_router = load_json(
        outputs
        / "global_transport_residual_listener_router_core"
        / "global_transport_residual_listener_router_summary.json"
    )
    rhythm_residual = load_json(
        outputs
        / "rhythm_conditioned_residual_listener_core"
        / "rhythm_conditioned_residual_listener_summary.json"
    )

    return [
        {
            "case": "lifelog_core_state_geometry",
            "layer": "core",
            "question": "OG lifelog context에서 만든 human-state geometry가 label/action 구조를 더 잘 모으는가",
            "primary_metric": "neighbor_consistency_lift",
            "value": lifelog["neighbor_consistency"]["lift"],
            "baseline": "random_neighbor",
            "support": "positive",
            "interpretation": "직접 label classifier는 아니지만, 가까운 row가 target manifold를 더 공유한다.",
            "source": "hsjepa_core/outputs/lifelog_core_state_evidence/lifelog_core_state_evidence_summary.json",
            "candidate": None,
        },
        {
            "case": "masked_context_world_model",
            "layer": "core",
            "question": "보이는 semantic lifelog view로 보이지 않는 target-view representation을 예측하는가",
            "primary_metric": "component_corr_lift_vs_null",
            "value": world["best_masked_view"]["component_corr_lift_vs_null"],
            "baseline": "shuffled_target_view",
            "support": "positive",
            "interpretation": "JEPA contract 자체는 성립한다. 단, direct label decoder로 쓰면 망가진다.",
            "source": "hsjepa_core/outputs/masked_context_world_model/masked_context_world_model_summary.json",
            "candidate": world.get("candidate_file"),
        },
        {
            "case": "subject_relative_human_state_world_model",
            "layer": "core",
            "question": "label-free subject-relative world-state가 subject identity를 줄이고 frozen label probe를 개선하는가",
            "primary_metric": "calibrated_subject_heldout_delta_vs_prior",
            "value": human_world["subject_world_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": "positive_but_tiny",
            "interpretation": (
                "absolute state는 subject identity를 강하게 담지만, subject-relative predicted state는 "
                "subject-id leakage를 거의 제거하고 low-trust frozen probe에서 prior를 아주 작게 이긴다."
            ),
            "source": "hsjepa_core/outputs/human_state_world_model_core/human_state_world_model_summary.json",
            "candidate": human_world.get("candidate_file"),
        },
        {
            "case": "subject_invariant_prototype_grammar",
            "layer": "core",
            "question": "subject-relative lifelog 좌표에서 label-free episode prototype grammar를 예측할 수 있는가",
            "primary_metric": "predicted_energy_delta_vs_prior_logloss",
            "value": prototype_grammar["subject_predicted_energy_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": prototype_grammar["verdict"],
            "interpretation": (
                "absolute lifelog 대신 subject-relative 좌표에서 만든 prototype grammar는 masked prototype pretext에서 prior를 이기고, "
                "raw lifelog보다 subject leakage를 크게 줄인다. frozen probe 효과는 작지만 HS-JEPA core가 subject-invariant "
                "human-life episode grammar를 만들 수 있다는 positive-boundary evidence다."
            ),
            "pretext_lift": prototype_grammar["pretext_mean_cross_entropy_lift_vs_prior"],
            "subject_leakage_accuracy": prototype_grammar["predicted_energy_subject_leakage"]["subject_id_accuracy"],
            "raw_leakage_reference": 0.957778,
            "source": "hsjepa_core/outputs/human_state_prototype_grammar_core/human_state_prototype_grammar_summary.json",
            "candidate": None,
        },
        {
            "case": "cross_subject_prototype_transport",
            "layer": "core",
            "question": "train subjects/blocks가 만든 subject-relative episode grammar를 held-out subject/block으로 운반할 수 있는가",
            "primary_metric": "transported_stats_probabilities_delta_vs_prior_logloss",
            "value": cross_subject_transport["subject_stats_probabilities_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": cross_subject_transport["verdict"],
            "interpretation": (
                "prototype grammar를 full cohort에 맞춘 것이 아니라 fold마다 train subjects/blocks에서만 정의한 뒤 "
                "held-out subject로 transport했다. label-free pretext는 prior를 이기고, transported stats+probabilities "
                "frozen probe는 subject-heldout prior와 raw lifelog PCA보다 낮은 logloss를 보인다. "
                "다만 probability-rich readout은 subject leakage가 커질 수 있어 stats-only/readout-risk를 분리해야 한다."
            ),
            "pretext_lift": cross_subject_transport["subject_pretext_mean_cross_entropy_lift_vs_prior"],
            "stats_delta_vs_prior": cross_subject_transport["subject_stats_delta_vs_prior"],
            "stats_probabilities_delta_vs_prior": cross_subject_transport["subject_stats_probabilities_delta_vs_prior"],
            "stats_delta_vs_raw": cross_subject_transport["subject_stats_delta_vs_raw"],
            "subject_leakage_accuracy": cross_subject_transport["transported_stats_subject_leakage"]["subject_id_accuracy"],
            "raw_leakage_reference": cross_subject_transport["raw_subject_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/cross_subject_prototype_transport_core/cross_subject_prototype_transport_summary.json",
            "candidate": None,
        },
        {
            "case": "transported_prototype_listener_readout",
            "layer": "frozen_probe_diagnostic",
            "question": "cross-subject transported prototype grammar는 target/listener별로 다른 view를 읽어야 하는가",
            "primary_metric": "listener_conditioned_delta_vs_global_transport_logloss",
            "value": transported_listener["subject_listener_delta_vs_global_transport"],
            "baseline": "global_transported_prototype_stats_probabilities",
            "support": transported_listener["verdict"],
            "interpretation": (
                "label-free transported prototype grammar를 고정한 뒤 target별 listener가 읽을 view를 frozen probe로 선택했다. "
                "listener-conditioned readout은 global transported grammar와 prior를 이기며, selected routes의 subject leakage는 "
                "global all-view bundle보다 낮다. 단, route 선택에는 labels가 쓰였으므로 core pretext가 아니라 core-interface diagnostic이다."
            ),
            "delta_vs_prior": transported_listener["subject_listener_delta_vs_prior"],
            "delta_vs_raw": transported_listener["subject_listener_delta_vs_raw"],
            "row_block_delta_vs_global": transported_listener["row_block_listener_delta_vs_global_transport"],
            "chronological_delta_vs_global": transported_listener["chronological_listener_delta_vs_global_transport"],
            "fold_wins": f'{transported_listener["selection_win_folds_total"]}/{transported_listener["selection_folds_total"]}',
            "selected_route_counts": transported_listener["selected_route_counts"],
            "source": "hsjepa_core/outputs/transported_prototype_listener_readout_core/transported_prototype_listener_readout_summary.json",
            "candidate": None,
        },
        {
            "case": "label_free_transported_listener_responsibility",
            "layer": "core_boundary",
            "question": "target 설명과 transported prototype reliability만으로 label-free listener responsibility를 만들 수 있는가",
            "primary_metric": "semantic_listener_delta_vs_global_transport_logloss",
            "value": label_free_listener["subject_semantic_delta_vs_global"],
            "baseline": "global_transported_prototype",
            "support": label_free_listener["verdict"],
            "interpretation": (
                "target 설명에서 고정한 human-semantic listener profile은 prior와 raw lifelog PCA를 이기지만 "
                "global transported grammar를 이기지는 못한다. leakage는 global transport보다 낮아지므로 방향은 맞지만, "
                "hand-coded listener responsibility만으로는 충분하지 않다. 다음 core는 listener responsibility를 pretext로 학습해야 한다."
            ),
            "delta_vs_prior": label_free_listener["subject_semantic_delta_vs_prior"],
            "delta_vs_raw": label_free_listener["subject_semantic_delta_vs_raw"],
            "row_block_delta_vs_global": label_free_listener["row_block_semantic_delta_vs_global"],
            "chronological_delta_vs_global": label_free_listener["chronological_semantic_delta_vs_global"],
            "semantic_subject_leakage": label_free_listener["semantic_listener_subject_leakage"]["subject_id_accuracy"],
            "global_subject_leakage": label_free_listener["global_transport_subject_leakage"]["subject_id_accuracy"],
            "raw_subject_leakage": label_free_listener["raw_subject_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/label_free_transported_listener_responsibility_core/label_free_transported_listener_responsibility_summary.json",
            "candidate": None,
        },
        {
            "case": "learned_listener_responsibility_pretext",
            "layer": "core",
            "question": "visible human-life context만으로 hidden listener responsibility field를 label-free pretext로 학습할 수 있는가",
            "primary_metric": "best_learned_delta_vs_handcoded_semantic_logloss",
            "value": learned_listener["subject_best_learned_delta_vs_direct_semantic"],
            "baseline": "hand_coded_semantic_listener_responsibility",
            "support": learned_listener["verdict"],
            "interpretation": (
                "transported prototype reliability로 만든 hidden listener-responsibility teacher를 labels 없이 예측했다. "
                "balanced learned semantic responsibility는 hand-coded semantic listener와 prior/raw를 이기고, row-block/chronological에서는 "
                "global transport보다도 살아남는다. 다만 subject-heldout에서는 global transport를 아직 넘지 못하고 absolute context variant는 "
                "subject leakage가 높다. subject-relative variant는 pretext CE와 leakage가 더 건강하므로 다음 core는 invariance-preserving "
                "responsibility pretext로 가야 한다."
            ),
            "delta_vs_prior": learned_listener["subject_best_learned_delta_vs_prior"],
            "delta_vs_raw": learned_listener["subject_best_learned_delta_vs_raw"],
            "delta_vs_global": learned_listener["subject_best_learned_delta_vs_global"],
            "row_block_delta_vs_global": learned_listener["row_block_best_learned_delta_vs_global"],
            "chronological_delta_vs_global": learned_listener["chronological_best_learned_delta_vs_global"],
            "best_learned_feature_set": learned_listener["subject_best_learned_feature_set"],
            "best_learned_leakage": learned_listener["subject_best_learned_leakage"]["subject_id_accuracy"],
            "relative_balanced_pretext_lift": learned_listener["subject_pretext_all"]["learned_semantic_relative_balanced"]["ce_lift_vs_prior"],
            "relative_balanced_leakage": learned_listener["learned_semantic_relative_balanced_subject_leakage"]["subject_id_accuracy"],
            "global_subject_leakage": learned_listener["global_transport_subject_leakage"]["subject_id_accuracy"],
            "raw_subject_leakage": learned_listener["raw_subject_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/learned_listener_responsibility_pretext_core/learned_listener_responsibility_pretext_summary.json",
            "candidate": None,
        },
        {
            "case": "invariant_listener_responsibility_pretext",
            "layer": "core_boundary",
            "question": "future/cohort consistency를 넣은 listener responsibility teacher가 current-only responsibility보다 더 invariant한가",
            "primary_metric": "best_invariant_delta_vs_current_relative_logloss",
            "value": invariant_listener["subject_best_invariant_delta_vs_current_relative"],
            "baseline": "current_relative_semantic_listener_responsibility",
            "support": invariant_listener["verdict"],
            "interpretation": (
                "same-subject future episode와 cross-subject cohort consistency를 hidden teacher에 넣었다. "
                "future-only invariant responsibility는 current-relative responsibility보다 subject-heldout downstream이 좋고, "
                "row-block/chronological stress에서는 global transport보다도 살아남는다. 다만 direct semantic과 거의 동률이며 "
                "subject-heldout global transport는 아직 넘지 못한다. cohort-only는 pretext/top1은 강하지만 downstream은 약해, "
                "pretext accuracy와 downstream utility가 분리될 수 있음을 보여준다."
            ),
            "delta_vs_prior": invariant_listener["subject_best_invariant_delta_vs_prior"],
            "delta_vs_raw": invariant_listener["subject_best_invariant_delta_vs_raw"],
            "delta_vs_global": invariant_listener["subject_best_invariant_delta_vs_global"],
            "delta_vs_direct_semantic": invariant_listener["subject_best_invariant_delta_vs_direct_semantic"],
            "row_block_delta_vs_global": invariant_listener["row_block_best_invariant_delta_vs_global"],
            "chronological_delta_vs_global": invariant_listener["chronological_best_invariant_delta_vs_global"],
            "best_invariant_feature_set": invariant_listener["subject_best_invariant_feature_set"],
            "best_invariant_leakage": invariant_listener["subject_best_invariant_leakage"]["subject_id_accuracy"],
            "current_relative_leakage": invariant_listener["current_relative_subject_leakage"]["subject_id_accuracy"],
            "global_subject_leakage": invariant_listener["global_transport_subject_leakage"]["subject_id_accuracy"],
            "raw_subject_leakage": invariant_listener["raw_subject_leakage"]["subject_id_accuracy"],
            "cohort_only_pretext_lift": invariant_listener["subject_pretext_all"]["cohort_only_relative_balanced"]["ce_lift_vs_prior"],
            "future_only_pretext_lift": invariant_listener["subject_pretext_all"]["future_only_relative_balanced"]["ce_lift_vs_prior"],
            "source": "hsjepa_core/outputs/invariant_listener_responsibility_pretext_core/invariant_listener_responsibility_pretext_summary.json",
            "candidate": None,
        },
        {
            "case": "multi_head_listener_responsibility_pretext",
            "layer": "core_boundary",
            "question": "current/future/cohort listener responsibility를 세 head로 보존하면 listener가 더 잘 읽는가",
            "primary_metric": "best_single_head_delta_vs_direct_semantic_logloss",
            "value": multi_head_listener["subject_best_single_head_logloss"]
            - multi_head_listener["subject_direct_semantic_logloss"],
            "baseline": "hand_coded_direct_semantic_listener_responsibility",
            "support": "future_head_positive_multihead_concat_boundary",
            "interpretation": (
                "compact future-consistent listener responsibility head는 prior/raw/direct semantic을 이긴다. "
                "하지만 naive current/future/cohort concat은 best single future head를 넘지 못한다. "
                "따라서 HS-JEPA는 더 큰 latent bundle이 아니라 target/listener별 head router가 필요하다."
            ),
            "best_single_head_feature_set": multi_head_listener["subject_best_single_head_feature_set"],
            "best_single_head_logloss": multi_head_listener["subject_best_single_head_logloss"],
            "best_multi_head_feature_set": multi_head_listener["subject_best_multi_head_feature_set"],
            "best_multi_head_logloss": multi_head_listener["subject_best_multi_head_logloss"],
            "single_delta_vs_prior": multi_head_listener["subject_best_single_head_logloss"]
            - multi_head_listener["subject_prior_logloss"],
            "single_delta_vs_raw": multi_head_listener["subject_best_single_head_logloss"]
            - multi_head_listener["subject_raw_logloss"],
            "multi_delta_vs_single": multi_head_listener["subject_best_multi_delta_vs_single"],
            "multi_delta_vs_prior": multi_head_listener["subject_best_multi_delta_vs_prior"],
            "multi_delta_vs_global": multi_head_listener["subject_best_multi_delta_vs_global"],
            "row_block_multi_delta_vs_global": multi_head_listener["row_block_best_multi_delta_vs_global"],
            "chronological_multi_delta_vs_global": multi_head_listener["chronological_best_multi_delta_vs_global"],
            "best_single_leakage": multi_head_listener["subject_best_single_leakage"]["subject_id_accuracy"],
            "best_multi_leakage": multi_head_listener["subject_best_multi_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/multi_head_listener_responsibility_pretext_core/multi_head_listener_responsibility_pretext_summary.json",
            "candidate": None,
        },
        {
            "case": "listener_head_router_pretext",
            "layer": "core_boundary",
            "question": "label-free listener-head router가 current/future/cohort head 중 무엇을 읽을지 정할 수 있는가",
            "primary_metric": "best_router_delta_vs_single_head_logloss",
            "value": listener_head_router["subject_best_router_delta_vs_single"],
            "baseline": "best_single_future_listener_head",
            "support": listener_head_router["verdict"],
            "interpretation": (
                "semantic-prior listener-head router는 best single future head와 naive multi-head concat을 이긴다. "
                "하지만 best router가 dynamic confidence router가 아니라 target semantic prior router였으므로, "
                "현재 결론은 listener routing positive / learned-router objective boundary다."
            ),
            "best_router_feature_set": listener_head_router["subject_best_router_feature_set"],
            "best_router_logloss": listener_head_router["subject_best_router_logloss"],
            "best_single_head_feature_set": listener_head_router["subject_best_single_head_feature_set"],
            "best_single_head_logloss": listener_head_router["subject_best_single_head_logloss"],
            "delta_vs_prior": listener_head_router["subject_best_router_delta_vs_prior"],
            "delta_vs_raw": listener_head_router["subject_best_router_delta_vs_raw"],
            "delta_vs_direct_semantic": listener_head_router["subject_best_router_delta_vs_direct_semantic"],
            "delta_vs_naive_multi": listener_head_router["subject_best_router_delta_vs_naive_multi"],
            "delta_vs_global": listener_head_router["subject_best_router_delta_vs_global"],
            "row_block_delta_vs_global": listener_head_router["row_block_best_router_delta_vs_global"],
            "chronological_delta_vs_global": listener_head_router["chronological_best_router_delta_vs_global"],
            "best_router_leakage": listener_head_router["subject_best_router_leakage"]["subject_id_accuracy"],
            "best_single_leakage": listener_head_router["subject_best_single_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/listener_head_router_pretext_core/listener_head_router_pretext_summary.json",
            "candidate": None,
        },
        {
            "case": "learned_listener_head_router_core",
            "layer": "core_boundary",
            "question": "fixed semantic prior 없이 hidden head-suitability field를 예측해 listener-head routing을 학습할 수 있는가",
            "primary_metric": "best_learned_router_delta_vs_semantic_prior_logloss",
            "value": learned_head_router["subject_best_learned_delta_vs_semantic_prior"],
            "baseline": "fixed_semantic_prior_listener_head_router",
            "support": learned_head_router["verdict"],
            "interpretation": (
                "label-free hidden head-suitability teacher를 만들고 visible context+predicted heads로 router를 학습했다. "
                "best learned semantic router는 fixed semantic-prior router와 best single future head를 이기고 leakage도 낮춘다. "
                "다만 subject-heldout global transport는 아직 넘지 못하므로, learned listener-head routing positive / global-transport boundary로 둔다."
            ),
            "best_learned_router_feature_set": learned_head_router["subject_best_learned_router_feature_set"],
            "best_learned_router_logloss": learned_head_router["subject_best_learned_router_logloss"],
            "semantic_prior_router_logloss": learned_head_router["subject_semantic_prior_router_logloss"],
            "best_single_head_feature_set": learned_head_router["subject_best_single_head_feature_set"],
            "best_single_head_logloss": learned_head_router["subject_best_single_head_logloss"],
            "delta_vs_single": learned_head_router["subject_best_learned_delta_vs_single"],
            "delta_vs_prior": learned_head_router["subject_best_learned_delta_vs_prior"],
            "delta_vs_raw": learned_head_router["subject_best_learned_delta_vs_raw"],
            "delta_vs_direct_semantic": learned_head_router["subject_best_learned_delta_vs_direct_semantic"],
            "delta_vs_naive_multi": learned_head_router["subject_best_learned_delta_vs_naive_multi"],
            "delta_vs_global": learned_head_router["subject_best_learned_delta_vs_global"],
            "row_block_delta_vs_global": learned_head_router["row_block_best_learned_delta_vs_global"],
            "chronological_delta_vs_global": learned_head_router["chronological_best_learned_delta_vs_global"],
            "best_learned_leakage": learned_head_router["subject_best_learned_leakage"]["subject_id_accuracy"],
            "semantic_prior_leakage": learned_head_router["subject_semantic_prior_leakage"]["subject_id_accuracy"],
            "best_single_leakage": learned_head_router["subject_best_single_leakage"]["subject_id_accuracy"],
            "source": "hsjepa_core/outputs/learned_listener_head_router_core/learned_listener_head_router_summary.json",
            "candidate": None,
        },
        {
            "case": "global_transport_residual_listener_router_core",
            "layer": "core",
            "question": "learned listener-head router는 global transport를 대체하는가, 아니면 residual interface로 붙어야 하는가",
            "primary_metric": "best_learned_residual_delta_vs_global_transport_logloss",
            "value": global_residual_router["subject_best_learned_residual_delta_vs_global"],
            "baseline": "global_transported_prototype",
            "support": global_residual_router["verdict"],
            "interpretation": (
                "learned router alone은 subject-heldout global transport를 넘지 못했지만, "
                "global transported grammar 위에 semantic+learned residual listener interface로 붙이면 "
                "subject-heldout과 row-block에서 global transport를 이긴다. "
                "동시에 chronological에서는 악화되므로 HS-JEPA core는 transport backbone + listener residual interface로 "
                "정리하되, temporal drift/action-health decoder는 별도 문제로 남겨야 한다."
            ),
            "best_residual_feature_set": global_residual_router["subject_best_learned_residual_feature_set"],
            "best_residual_logloss": global_residual_router["subject_best_learned_residual_logloss"],
            "global_transport_logloss": global_residual_router["subject_global_transport_logloss"],
            "learned_alone_logloss": global_residual_router["subject_learned_router_logloss"],
            "delta_vs_learned_alone": global_residual_router["subject_best_learned_residual_delta_vs_learned_alone"],
            "row_block_delta_vs_global": global_residual_router["row_block_best_learned_residual_delta_vs_global"],
            "chronological_delta_vs_global": global_residual_router[
                "chronological_best_learned_residual_delta_vs_global"
            ],
            "best_residual_leakage": global_residual_router["subject_best_learned_residual_leakage"][
                "subject_id_accuracy"
            ],
            "global_subject_leakage": global_residual_router["global_transport_subject_leakage"][
                "subject_id_accuracy"
            ],
            "raw_subject_leakage": global_residual_router["raw_subject_leakage"]["subject_id_accuracy"],
            "source": (
                "hsjepa_core/outputs/global_transport_residual_listener_router_core/"
                "global_transport_residual_listener_router_summary.json"
            ),
            "candidate": None,
        },
        {
            "case": "rhythm_conditioned_residual_listener_core",
            "layer": "core",
            "question": (
                "visible rhythm context가 temporal drift decoder와 subject/block residual listener readout을 "
                "분리할 수 있는가"
            ),
            "primary_metric": "chronological_best_rhythm_delta_vs_global_transport_logloss",
            "value": rhythm_residual["chronological_best_rhythm_delta_vs_global"],
            "baseline": "global_transported_prototype",
            "support": rhythm_residual["verdict"],
            "interpretation": (
                "plain residual listener router는 chronological에서 독성을 보였지만, rhythm context는 chronological drift를 "
                "global transport보다 낮은 logloss로 읽는다. subject-heldout과 row-block에서는 rhythm-gated residual이 "
                "plain residual을 더 낮춘다. 따라서 HS-JEPA는 temporal decoder와 listener residual readout을 하나의 "
                "monolithic interface로 합치면 안 되고, rhythm-conditioned temporal decoder와 rhythm-gated residual listener를 "
                "분리해야 한다."
            ),
            "subject_best_rhythm_feature_set": rhythm_residual["subject_best_rhythm_feature_set"],
            "subject_best_rhythm_delta_vs_global": rhythm_residual["subject_best_rhythm_delta_vs_global"],
            "subject_best_rhythm_delta_vs_plain_residual": rhythm_residual[
                "subject_best_rhythm_delta_vs_plain_residual"
            ],
            "row_block_best_rhythm_feature_set": rhythm_residual["row_block_best_rhythm_feature_set"],
            "row_block_best_rhythm_delta_vs_global": rhythm_residual["row_block_best_rhythm_delta_vs_global"],
            "row_block_best_rhythm_delta_vs_plain_residual": rhythm_residual[
                "row_block_best_rhythm_delta_vs_plain_residual"
            ],
            "chronological_best_rhythm_feature_set": rhythm_residual["chronological_best_rhythm_feature_set"],
            "chronological_best_rhythm_logloss": rhythm_residual["chronological_best_rhythm_logloss"],
            "chronological_plain_residual_delta_vs_global": rhythm_residual[
                "chronological_plain_residual_delta_vs_global"
            ],
            "chronological_best_rhythm_delta_vs_plain_residual": rhythm_residual[
                "chronological_best_rhythm_delta_vs_plain_residual"
            ],
            "chronological_best_gated_residual_delta_vs_global": rhythm_residual[
                "chronological_best_gated_residual_delta_vs_global"
            ],
            "rhythm_context_subject_leakage": rhythm_residual["rhythm_context_subject_leakage"][
                "subject_id_accuracy"
            ],
            "best_gated_residual_subject_leakage": rhythm_residual[
                "subject_best_gated_residual_leakage"
            ]["subject_id_accuracy"],
            "plain_residual_subject_leakage": rhythm_residual["plain_residual_subject_leakage"][
                "subject_id_accuracy"
            ],
            "global_subject_leakage": rhythm_residual["global_transport_subject_leakage"]["subject_id_accuracy"],
            "raw_subject_leakage": rhythm_residual["raw_subject_leakage"]["subject_id_accuracy"],
            "source": (
                "hsjepa_core/outputs/rhythm_conditioned_residual_listener_core/"
                "rhythm_conditioned_residual_listener_summary.json"
            ),
            "candidate": None,
        },
        {
            "case": "routine_break_world_model",
            "layer": "core",
            "question": "보이는 human-life context로 보이지 않는 routine-break/episode-reset representation을 예측하는가",
            "primary_metric": "routine_full_delta_vs_prior_logloss",
            "value": routine_world["routine_full_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": "positive_but_small",
            "interpretation": (
                "subject-relative deviation, previous-episode jump, rolling-baseline residual로 만든 "
                "label-free routine-break target이 subject-heldout frozen probe에서 prior를 이긴다."
            ),
            "source": "hsjepa_core/outputs/routine_break_world_model_core/routine_break_world_model_summary.json",
            "candidate": routine_world.get("candidate_file"),
        },
        {
            "case": "sleep_pressure_world_model",
            "layer": "core",
            "question": "보이는 daily human-life context로 label-free sleep-pressure representation을 예측하는가",
            "primary_metric": "sleep_pressure_full_delta_vs_prior_logloss",
            "value": sleep_pressure["sleep_pressure_full_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": "positive_but_small",
            "interpretation": (
                "night disturbance, physiological load, social/cognitive arousal, rest-environment stability로 만든 "
                "label-free sleep-pressure target은 pretext 예측성이 강하지만 Q/S label probe 효과는 작다."
            ),
            "source": "hsjepa_core/outputs/sleep_pressure_world_model_core/sleep_pressure_world_model_summary.json",
            "candidate": sleep_pressure.get("candidate_file"),
        },
        {
            "case": "cohort_relative_world_model",
            "layer": "core",
            "question": "보이는 daily context로 personal-vs-peer cohort-relative representation을 예측하는가",
            "primary_metric": "cohort_relative_predicted_delta_vs_prior_logloss",
            "value": cohort_relative["cohort_relative_predicted_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": "positive_with_leakage_boundary",
            "interpretation": (
                "singleton 없는 peer cohort에서 predicted personal-vs-peer representation은 subject-heldout probe를 "
                "개선하지만, observed/full cohort geometry는 subject shortcut이 강해 core evidence로 쓰면 안 된다."
            ),
            "source": "hsjepa_core/outputs/cohort_relative_world_model_core/cohort_relative_world_model_summary.json",
            "candidate": cohort_relative.get("candidate_file"),
        },
        {
            "case": "multi_target_human_state_world_model",
            "layer": "core",
            "question": "routine-break, sleep-pressure, cohort-relative hidden targets를 함께 예측한 route-preserving bundle이 더 좋은가",
            "primary_metric": "multi_target_predicted_delta_vs_prior_logloss",
            "value": multi_target["multi_target_predicted_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": "positive_with_route_preservation",
            "interpretation": (
                "세 hidden target의 predicted axes를 보존한 bundle은 subject-heldout probe에서 prior와 best single target을 이기지만, "
                "PCA식 compressed core latent는 오히려 악화된다. HS-JEPA core는 route 축을 보존해야 한다."
            ),
            "source": "hsjepa_core/outputs/multi_target_human_state_world_model_core/multi_target_human_state_world_model_summary.json",
            "candidate": multi_target.get("candidate_file"),
        },
        {
            "case": "route_responsibility_world_model",
            "layer": "core_diagnostic",
            "question": "label-free cross-route residual로 route responsibility를 만들면 base multi-target보다 좋아지는가",
            "primary_metric": "route_weighted_delta_vs_base_multi_target_logloss",
            "value": route_responsibility["route_weighted_delta_vs_base_multi_target"],
            "baseline": "route_preserving_multi_target_predicted",
            "support": "pretext_positive_downstream_negative_vs_base",
            "interpretation": (
                "cross-route responsibility pretext는 매우 강하지만, responsibility weighting은 prior만 이기고 "
                "base multi-target predicted bundle보다 나쁘다. route responsibility는 현재 replacement가 아니라 diagnostic이다."
            ),
            "pretext_lift": route_responsibility["best_route_pretext"]["component_corr_lift_vs_null"],
            "source": "hsjepa_core/outputs/route_responsibility_world_model_core/route_responsibility_world_model_summary.json",
            "candidate": route_responsibility.get("candidate_file"),
        },
        {
            "case": "listener_conditioned_route_readout",
            "layer": "frozen_probe_diagnostic",
            "question": "target/listener별로 서로 다른 hidden route를 읽게 하면 route-preserving bundle보다 좋아지는가",
            "primary_metric": "listener_conditioned_delta_vs_multi_target_logloss",
            "value": listener_readout["listener_conditioned_delta_vs_multi_target"],
            "baseline": "route_preserving_multi_target_predicted",
            "support": "strong_positive_probe",
            "interpretation": (
                "core는 label-free route bundle을 만들고, frozen probe에서 target별 route readout을 선택했다. "
                "listener-conditioned readout은 multi-target bundle을 이겨, HS-JEPA route axes가 listener별로 다르게 읽혀야 함을 보인다."
            ),
            "fold_wins": f'{listener_readout["selection_win_folds_total"]}/{listener_readout["selection_folds_total"]}',
            "source": "hsjepa_core/outputs/listener_conditioned_route_readout_core/listener_conditioned_route_readout_summary.json",
            "candidate": listener_readout.get("candidate_file"),
        },
        {
            "case": "subject_drift_world_model",
            "layer": "core_boundary",
            "question": "label-free HS-JEPA world-state가 future recovery/degradation drift를 subject-heldout으로 읽기 쉽게 만드는가",
            "primary_metric": "subject_hsjepa_delta_vs_prior_logloss",
            "value": subject_drift["subject_hsjepa_delta_vs_prior"],
            "baseline": "fold_prior_low_trust_probe",
            "support": subject_drift["core_drift_verdict"],
            "interpretation": (
                "subject-relative predicted world-state가 low-trust drift readout에서 prior를 아주 작게 이긴다. "
                "하지만 calendar low-trust readout이 전체 best이고 효과가 0.001보다 작아, drift consistency public breakthrough를 "
                "core 단독 성과로 과장하면 안 된다."
            ),
            "source": "hsjepa_core/outputs/subject_drift_world_model_core/subject_drift_world_model_summary.json",
            "candidate": None,
        },
        {
            "case": "episode_transition_retrieval",
            "layer": "core_boundary",
            "question": "현재 visible human-life context가 보이지 않는 다음 episode representation을 retrieval할 수 있는가",
            "primary_metric": "subject_rank_pct_lift_vs_random",
            "value": transition_retrieval["subject_relative_predicted_retrieval"]["lift_rank_pct_vs_random"],
            "baseline": "random_episode_candidate",
            "support": "rhythm_dominant_boundary",
            "interpretation": (
                "subject-relative HS-JEPA transition predictor는 random보다 낫지만 persistence와 calendar rhythm을 넘지 못한다. "
                "가장 강한 transition listener는 calendar_to_next_state이며, future-state core는 generic transition보다 "
                "rhythm-conditioned transition으로 정립해야 한다."
            ),
            "calendar_rank_lift": transition_retrieval["subject_best_retrieval"]["lift_rank_pct_vs_random"],
            "persistence_rank_lift": transition_retrieval["subject_persistence_retrieval"]["lift_rank_pct_vs_random"],
            "source": "hsjepa_core/outputs/episode_transition_retrieval_core/episode_transition_retrieval_summary.json",
            "candidate": None,
        },
        {
            "case": "external_action_replay_geometry",
            "layer": "core_to_adapter_probe",
            "question": "core-state geometry가 다른 adapter의 row-action support를 재발견하는가",
            "primary_metric": "row_auc_z_vs_permuted_train",
            "value": lifelog["external_action_replay"]["mean_core_auc_z_vs_permuted_train"],
            "baseline": "permuted_teacher",
            "support": "strong_positive_probe",
            "interpretation": "public 없이도 기존 action-support 구조 일부를 row geometry에서 복원한다.",
            "source": "hsjepa_core/outputs/lifelog_core_state_evidence/lifelog_core_state_evidence_summary.json",
            "candidate": None,
        },
        {
            "case": "subject_invariant_listener_manifold",
            "layer": "core",
            "question": "subject-invariant jury release target이 HS-JEPA listener manifold에서 action-only보다 잘 분리되는가",
            "primary_metric": "hsjepa_listener_ap_lift_minus_action_only",
            "value": manifold["hsjepa_listener_ap_lift"] - manifold["action_only_ap_lift"],
            "baseline": "action_geometry_only",
            "support": "strong_positive",
            "interpretation": "action geometry만 보는 것보다 hidden listener manifold가 훨씬 강하다.",
            "source": "hsjepa_core/outputs/subject_invariant_listener_manifold_core/subject_invariant_listener_manifold_core_summary.json",
            "candidate": manifold.get("candidate_file"),
        },
        {
            "case": "listener_responsibility_field",
            "layer": "core",
            "question": "action을 고르기 전에 어느 row-target listener가 개입해야 하는지 복원하는가",
            "primary_metric": "masked_pretext_ap_lift_minus_listener_only",
            "value": responsibility["masked_pretext_ap_lift"] - responsibility["listener_only_ap_lift"],
            "baseline": "listener_only",
            "support": "positive_but_small",
            "interpretation": "core가 '어디를 볼지'는 더 잘 잡지만, action decoder는 여전히 독성이 있다.",
            "source": "hsjepa_core/outputs/subject_invariant_listener_responsibility_field_core/subject_invariant_listener_responsibility_field_core_summary.json",
            "candidate": responsibility.get("candidate_file"),
        },
        {
            "case": "signed_direction_translation",
            "layer": "adapter_boundary",
            "question": "responsibility-high cell에서 raw/inverse direction 독성을 줄이는가",
            "primary_metric": "gain_sum_repaired_vs_previous_decoder",
            "value": signed["best_responsibility_gain_sum"] - signed["previous_responsibility_decoder_gain_sum"],
            "baseline": "previous_responsibility_decoder",
            "support": "adapter_positive_core_boundary",
            "interpretation": "core가 위치를 좁히고, signed action adapter가 방향 독성을 수리한다. pure core direction 승리는 아니다.",
            "source": "hsjepa_core/outputs/signed_listener_responsibility_direction_core/signed_listener_responsibility_direction_core_summary.json",
            "candidate": signed.get("candidate_file"),
        },
        {
            "case": "counterfactual_direction_pretext",
            "layer": "negative_boundary",
            "question": "raw/inverse counterfactual direction을 action-probability-free HS-JEPA core target으로 복원할 수 있는가",
            "primary_metric": "best_core_responsibility_gain_sum",
            "value": counterfactual_direction["best_core_responsibility_gain_sum"],
            "baseline": "oracle_direction_available_but_hidden",
            "support": "negative",
            "interpretation": (
                "direction oracle은 크지만 현재 human/pretext context는 release-grade direction을 복원하지 못한다. "
                "signed direction은 아직 core보다 adapter boundary에 가깝다."
            ),
            "source": "hsjepa_core/outputs/counterfactual_direction_pretext_core/counterfactual_direction_pretext_core_summary.json",
            "candidate": counterfactual_direction.get("candidate_file"),
        },
        {
            "case": "direct_label_prediction",
            "layer": "negative_boundary",
            "question": "HS-JEPA state를 그대로 label classifier로 쓰면 되는가",
            "primary_metric": "hsjepa_state_delta_vs_prior_logloss",
            "value": lifelog["label_probe"]["hsjepa_state_delta_vs_prior"],
            "baseline": "label_prior",
            "support": "negative",
            "interpretation": "HS-JEPA core는 standalone label predictor가 아니다. action-health geometry로 써야 한다.",
            "source": "hsjepa_core/outputs/lifelog_core_state_evidence/lifelog_core_state_evidence_summary.json",
            "candidate": None,
        },
    ]


def build_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    positive_core = [case for case in cases if case["layer"] == "core" and "positive" in case["support"]]
    negative = [case for case in cases if case["support"] == "negative"]
    adapter = [case for case in cases if case["layer"] == "adapter_boundary"]
    return {
        "package": "core_evidence_ledger",
        "status": "paper_facing_core_evidence_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "core_positive_case_count": len(positive_core),
        "adapter_boundary_case_count": len(adapter),
        "negative_boundary_case_count": len(negative),
        "paper_thesis": (
            "HS-JEPA core is a hidden human-state and listener-responsibility representation, "
            "not a standalone label classifier.  Its strongest evidence is masked context "
            "prediction, subject-invariant prototype grammar, subject-relative routine-break, "
            "cross-subject prototype transport, sleep-pressure, cohort-relative prediction, route-preserving multi-target human-state prediction, "
            "transported-prototype listener readout, learned/invariant/multi-head listener-responsibility pretext, "
            "label-free and learned listener-head routing, "
            "global-transport residual listener routing, "
            "rhythm-conditioned temporal decoding, "
            "and listener-conditioned route readout with subject-invariant listener/action-health separability."
        ),
        "cases": cases,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    cases = summary["cases"]
    by_case = {case["case"]: case for case in cases}
    table_rows = [
        {
            "case": case["case"],
            "layer": case["layer"],
            "metric": case["primary_metric"],
            "value": fmt(case["value"], 6),
            "baseline": case["baseline"],
            "support": case["support"],
        }
        for case in cases
    ]
    candidate_rows = [
        {
            "case": case["case"],
            "candidate": case["candidate"] or "-",
            "role": case["layer"],
        }
        for case in cases
        if case.get("candidate")
    ]
    return f"""# HS-JEPA Core Evidence Ledger

## 한 줄 결론

HS-JEPA core는 label을 직접 맞히는 classifier가 아니다.
현재 증거상 더 정확한 정의는 다음이다.

```text
visible human-life context
  -> hidden human-state / listener-responsibility representation
  -> action-health geometry
  -> competition adapter가 sparse row-target correction으로 번역
```

즉 논문에서 HS-JEPA를 설명할 때, row-target 후처리 트릭이 아니라
`보이는 생활 context로 보이지 않는 인간 상태 표현을 예측하는 core`를 먼저 세워야 한다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probabilities: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Evidence Table

{markdown_table(table_rows, ["case", "layer", "metric", "value", "baseline", "support"])}

## 무엇이 진짜 HS-JEPA Core 증거인가

### 1. Masked Context World Model

생활 로그를 semantic view로 나눈 뒤, 일부 view만 보고 가려진 target-view representation을 예측했다.
best view의 component-correlation lift는 `{fmt(by_case["masked_context_world_model"]["value"], 6)}`로 shuffled target-view null보다 높다.

이것이 JEPA 느낌의 핵심이다.

```text
raw label prediction이 아니라
visible context -> hidden target representation prediction
```

### 2. Subject-Relative Human-State World Model

absolute state는 subject identity를 강하게 담지만, subject-relative world-state는
subject identity leakage를 크게 줄이면서 low-trust frozen probe에서 prior를 아주 작게 이겼다.
subject-heldout delta vs prior는 `{fmt(by_case["subject_relative_human_state_world_model"]["value"], 6)}`이다.

이 결과는 효과 크기가 작다. 하지만 HS-JEPA를 competition adapter가 아니라
label-free human-state world model로 정립하는 데 필요한 첫 positive evidence다.

### 3. Subject-Invariant Prototype Grammar

absolute lifelog feature를 그대로 쓰면 subject identity shortcut이 강해진다.
이 실험은 각 subject 내부에서 raw lifelog를 상대화한 뒤, semantic view별 episode prototype을 만들고
보이는 view들로 가려진 prototype responsibility를 예측했다.

```text
subject-relative visible lifelog views
  -> hidden episode prototype grammar
  -> masked context predicts prototype responsibility
```

masked prototype pretext의 mean cross-entropy lift는
`{fmt(by_case["subject_invariant_prototype_grammar"].get("pretext_lift"), 6)}`이고,
subject-heldout frozen probe에서 predicted grammar energy의 prior 대비 delta는
`{fmt(by_case["subject_invariant_prototype_grammar"]["value"], 6)}`이다.

중요한 점은 subject leakage가 크게 낮다는 것이다.
predicted grammar energy의 subject-id accuracy는
`{fmt(by_case["subject_invariant_prototype_grammar"].get("subject_leakage_accuracy"), 6)}`이고,
raw lifelog PCA reference는 약 `{fmt(by_case["subject_invariant_prototype_grammar"].get("raw_leakage_reference"), 6)}`이다.

따라서 이 실험은 다음 thesis를 지지한다.

```text
HS-JEPA는 사람마다 다른 절대 센서 크기를 외우는 대신,
각자의 평소 기준에서 오늘이 어떤 생활 episode 원형인지 표현한다.
```

다만 label-probe 효과는 아직 작다. LB breakthrough로 번역하려면
이 grammar를 listener/drift decoder가 읽어야 한다.

### 4. Cross-Subject Prototype Transport

이전 prototype grammar 실험이 full cohort 안에서만 성립한 것인지 확인하기 위해,
이번에는 fold마다 train subjects/blocks에서만 prototype grammar를 정의하고 held-out subject/block으로 운반했다.

```text
train subjects define subject-relative episode grammar
  -> held-out subject is transported into that grammar
  -> visible context predicts hidden transported prototype responsibilities
```

subject-heldout label-free pretext의 mean cross-entropy lift는
`{fmt(by_case["cross_subject_prototype_transport"].get("pretext_lift"), 6)}`이다.
transported stats+probabilities frozen probe의 prior 대비 delta는
`{fmt(by_case["cross_subject_prototype_transport"].get("stats_probabilities_delta_vs_prior"), 6)}`이고,
stats-only frozen probe의 prior 대비 delta는
`{fmt(by_case["cross_subject_prototype_transport"].get("stats_delta_vs_prior"), 6)}`이다.

raw lifelog PCA 대비 stats-only delta는
`{fmt(by_case["cross_subject_prototype_transport"].get("stats_delta_vs_raw"), 6)}`이다.
subject-id leakage 기준으로 transported stats accuracy는
`{fmt(by_case["cross_subject_prototype_transport"].get("subject_leakage_accuracy"), 6)}`이고,
raw lifelog PCA reference는 `{fmt(by_case["cross_subject_prototype_transport"].get("raw_leakage_reference"), 6)}`이다.

따라서 이 실험은 HS-JEPA core에 더 강한 문장을 허용한다.

```text
HS-JEPA는 full cohort 안에서만 쓸 수 있는 subject-relative grammar가 아니라,
train subjects가 정의한 생활 episode grammar를 held-out subject로 운반할 수 있다.
```

단, probability-rich readout은 leakage가 커질 수 있다.
논문에서는 transport 가능성과 readout leakage risk를 분리해서 써야 한다.

### 5. Transported Prototype Listener Readout

cross-subject transport가 global representation으로만 의미 있는지, 아니면 target/listener별로
서로 다른 transported grammar view를 읽어야 하는지 검증했다.

```text
transported prototype grammar
  -> Q/S listener chooses a transported view
  -> frozen low-trust probe reads target-specific interface
```

subject-heldout에서 listener-conditioned readout은 global transported grammar 대비
`{fmt(by_case["transported_prototype_listener_readout"]["value"], 6)}` logloss 개선을 보였다.
prior 대비 delta는 `{fmt(by_case["transported_prototype_listener_readout"].get("delta_vs_prior"), 6)}`이고,
raw lifelog PCA 대비 delta는 `{fmt(by_case["transported_prototype_listener_readout"].get("delta_vs_raw"), 6)}`이다.
fold-level route win은 `{by_case["transported_prototype_listener_readout"].get("fold_wins")}`이다.

stress 결과는 더 조심스럽다.

```text
row-block delta vs global: {fmt(by_case["transported_prototype_listener_readout"].get("row_block_delta_vs_global"), 6)}
chronological delta vs global: {fmt(by_case["transported_prototype_listener_readout"].get("chronological_delta_vs_global"), 6)}
```

따라서 이 결과는 core pretext가 아니라 core-interface diagnostic으로 둔다.
정확한 논문 문장은 다음이다.

```text
Transported grammar는 하나의 global latent보다,
listener별로 선택적으로 읽히는 interface일 때 더 강하다.
```

### 6. Label-Free Transported Listener Responsibility

위 listener readout은 frozen labels로 target별 view를 선택했다.
이 실험은 그 선택을 제거하고, target 설명과 transported prototype reliability만으로 listener responsibility를 만들었다.

```text
target description + transported prototype reliability
  -> label-free listener responsibility
  -> frozen low-trust probe
```

결과는 boundary다.

```text
delta vs prior: {fmt(by_case["label_free_transported_listener_responsibility"].get("delta_vs_prior"), 6)}
delta vs raw lifelog PCA: {fmt(by_case["label_free_transported_listener_responsibility"].get("delta_vs_raw"), 6)}
delta vs global transport: {fmt(by_case["label_free_transported_listener_responsibility"]["value"], 6)}
row-block delta vs global: {fmt(by_case["label_free_transported_listener_responsibility"].get("row_block_delta_vs_global"), 6)}
chronological delta vs global: {fmt(by_case["label_free_transported_listener_responsibility"].get("chronological_delta_vs_global"), 6)}
```

subject leakage는 raw/global보다 낮아진다.

```text
semantic listener leakage: {fmt(by_case["label_free_transported_listener_responsibility"].get("semantic_subject_leakage"), 6)}
global transport leakage: {fmt(by_case["label_free_transported_listener_responsibility"].get("global_subject_leakage"), 6)}
raw lifelog leakage: {fmt(by_case["label_free_transported_listener_responsibility"].get("raw_subject_leakage"), 6)}
```

따라서 이 실험이 죽인 믿음은 분명하다.

```text
target 설명만으로 hand-coded listener responsibility를 만들면 충분하다.
```

살아남은 믿음은 이것이다.

```text
label-free listener responsibility 방향은 맞지만, 사람이 고정한 profile보다
pretext로 학습된 listener responsibility가 필요하다.
```

### 7. Learned Listener Responsibility Pretext

직전 boundary를 그대로 실험으로 바꿨다.
이번에는 hand-coded profile을 바로 쓰지 않고, visible human-life context가
transported prototype reliability에서 만든 hidden listener responsibility field를 예측하게 했다.

```text
visible human-life context
  -> hidden transported listener responsibility
  -> frozen low-trust probe
```

핵심 결과:

```text
best learned feature set: {by_case["learned_listener_responsibility_pretext"].get("best_learned_feature_set")}
delta vs hand-coded semantic: {fmt(by_case["learned_listener_responsibility_pretext"]["value"], 6)}
delta vs prior: {fmt(by_case["learned_listener_responsibility_pretext"].get("delta_vs_prior"), 6)}
delta vs raw lifelog PCA: {fmt(by_case["learned_listener_responsibility_pretext"].get("delta_vs_raw"), 6)}
delta vs global transport: {fmt(by_case["learned_listener_responsibility_pretext"].get("delta_vs_global"), 6)}
row-block delta vs global: {fmt(by_case["learned_listener_responsibility_pretext"].get("row_block_delta_vs_global"), 6)}
chronological delta vs global: {fmt(by_case["learned_listener_responsibility_pretext"].get("chronological_delta_vs_global"), 6)}
```

가장 중요한 점은 open-loop prediction이 아니라 calibrated responsibility prediction이다.
open-loop는 top-1은 맞혀도 확률 geometry가 과신되어 pretext CE가 나빠진다.
prior-shrunk balanced responsibility는 pretext CE를 prior보다 이긴다.

subject-relative context variant는 더 논문적이다.

```text
relative balanced pretext CE lift vs prior: {fmt(by_case["learned_listener_responsibility_pretext"].get("relative_balanced_pretext_lift"), 6)}
relative balanced subject leakage: {fmt(by_case["learned_listener_responsibility_pretext"].get("relative_balanced_leakage"), 6)}
global transport subject leakage: {fmt(by_case["learned_listener_responsibility_pretext"].get("global_subject_leakage"), 6)}
raw lifelog subject leakage: {fmt(by_case["learned_listener_responsibility_pretext"].get("raw_subject_leakage"), 6)}
```

따라서 이번 결과는 HS-JEPA thesis를 강화하지만 동시에 제한한다.

```text
강화:
  listener responsibility는 label 없이 visible context에서 학습 가능하다.
  learned responsibility는 hand-coded semantic profile보다 downstream probe가 좋다.

제한:
  absolute context encoder는 subject shortcut을 많이 담는다.
  subject-heldout global transported grammar를 아직 넘지는 못한다.
```

다음 core는 learned responsibility를 유지하되,
subject-relative/future/cohort consistency로 shortcut을 누르는 방향이어야 한다.

### 8. Invariant Listener Responsibility Pretext

직전 learned responsibility는 hand-coded semantic profile을 이겼지만,
teacher가 current transported responsibility에 묶여 있었다.
이번에는 hidden teacher 자체를 더 human-state답게 바꿨다.

```text
current transported responsibility
  + same-subject future episode consistency
  + cross-subject cohort consistency
  -> invariant listener responsibility teacher
```

핵심 결과:

```text
best invariant feature set: {by_case["invariant_listener_responsibility_pretext"].get("best_invariant_feature_set")}
delta vs current-relative responsibility: {fmt(by_case["invariant_listener_responsibility_pretext"]["value"], 6)}
delta vs prior: {fmt(by_case["invariant_listener_responsibility_pretext"].get("delta_vs_prior"), 6)}
delta vs raw lifelog PCA: {fmt(by_case["invariant_listener_responsibility_pretext"].get("delta_vs_raw"), 6)}
delta vs direct semantic responsibility: {fmt(by_case["invariant_listener_responsibility_pretext"].get("delta_vs_direct_semantic"), 6)}
delta vs global transport: {fmt(by_case["invariant_listener_responsibility_pretext"].get("delta_vs_global"), 6)}
row-block delta vs global: {fmt(by_case["invariant_listener_responsibility_pretext"].get("row_block_delta_vs_global"), 6)}
chronological delta vs global: {fmt(by_case["invariant_listener_responsibility_pretext"].get("chronological_delta_vs_global"), 6)}
```

가장 중요한 positive signal은 future-only invariant responsibility다.
같은 사람의 미래 episode에서 반복되는 listener state를 teacher에 넣으면,
current-only subject-relative responsibility보다 subject-heldout downstream이 좋아진다.
또 row-block/chronological stress에서는 global transported grammar도 이긴다.

하지만 cohort-only result는 더 조심스럽다.

```text
cohort-only pretext CE lift vs prior: {fmt(by_case["invariant_listener_responsibility_pretext"].get("cohort_only_pretext_lift"), 6)}
future-only pretext CE lift vs prior: {fmt(by_case["invariant_listener_responsibility_pretext"].get("future_only_pretext_lift"), 6)}
best invariant subject leakage: {fmt(by_case["invariant_listener_responsibility_pretext"].get("best_invariant_leakage"), 6)}
current-relative subject leakage: {fmt(by_case["invariant_listener_responsibility_pretext"].get("current_relative_leakage"), 6)}
global transport subject leakage: {fmt(by_case["invariant_listener_responsibility_pretext"].get("global_subject_leakage"), 6)}
raw lifelog subject leakage: {fmt(by_case["invariant_listener_responsibility_pretext"].get("raw_subject_leakage"), 6)}
```

cohort-only는 pretext/top-1은 강하지만 downstream utility는 약하다.
이 결과가 죽인 믿음은 다음이다.

```text
pretext를 잘 맞히는 invariant teacher는 그대로 downstream label utility가 된다.
```

살아남은 더 정확한 믿음은 이것이다.

```text
HS-JEPA core에서 좋은 human-state teacher는
현재 상태, 개인의 미래 consistency, peer cohort consistency를 한 벡터로 섞는 것이 아니라
multi-head로 보존하고 listener가 필요한 head를 읽게 해야 한다.
```

### 9. Multi-Head Listener Responsibility Pretext

직전 결론을 그대로 반증했다.
이번에는 current/future/cohort responsibility를 하나의 smoothed teacher로 만들지 않고,
세 head를 따로 예측한 뒤 frozen listener probe가 single/concat/delta geometry를 읽게 했다.

```text
subject-relative visible context
  -> current listener responsibility head
  -> future-consistent listener responsibility head
  -> cohort-consistent listener responsibility head
  -> frozen listener reads head geometry
```

결과는 positive와 negative가 같이 나왔다.

```text
best single head: {by_case["multi_head_listener_responsibility_pretext"].get("best_single_head_feature_set")}
best single-head logloss: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("best_single_head_logloss"), 6)}
best multi-head feature set: {by_case["multi_head_listener_responsibility_pretext"].get("best_multi_head_feature_set")}
best multi-head logloss: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("best_multi_head_logloss"), 6)}
single delta vs direct semantic: {fmt(by_case["multi_head_listener_responsibility_pretext"]["value"], 6)}
single delta vs prior: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("single_delta_vs_prior"), 6)}
single delta vs raw lifelog PCA: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("single_delta_vs_raw"), 6)}
multi delta vs single: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("multi_delta_vs_single"), 6)}
multi delta vs global transport: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("multi_delta_vs_global"), 6)}
row-block multi delta vs global: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("row_block_multi_delta_vs_global"), 6)}
chronological multi delta vs global: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("chronological_multi_delta_vs_global"), 6)}
```

살아남은 core evidence:

```text
future-consistent listener responsibility is the strongest compact head.
It beats prior, raw lifelog PCA, and hand-coded direct semantic responsibility.
```

죽은 믿음:

```text
Naively concatenating current/future/cohort heads lets the downstream listener automatically route.
```

leakage 관점에서는 multi-head가 single future head보다 약간 낮지만,
subject-heldout utility는 낮다.

```text
best single-head leakage: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("best_single_leakage"), 6)}
best multi-head leakage: {fmt(by_case["multi_head_listener_responsibility_pretext"].get("best_multi_leakage"), 6)}
```

따라서 다음 architecture 문장은 더 정확해졌다.

```text
HS-JEPA does not need a larger undifferentiated latent bundle.
It needs a listener router that chooses current/future/cohort heads per target.
```

### 10. Listener Head Router Pretext

직전 실험은 "router가 필요하다"는 결론을 남겼다.
이번에는 concat을 버리고 label-free router가 current/future/cohort head를 soft routing하게 했다.

```text
current / future / cohort listener heads
  -> label-free head router
  -> routed human-state interface
```

결과는 작지만 architecture 관점에서 중요하다.

```text
best router: {by_case["listener_head_router_pretext"].get("best_router_feature_set")}
best router logloss: {fmt(by_case["listener_head_router_pretext"].get("best_router_logloss"), 6)}
best single head: {by_case["listener_head_router_pretext"].get("best_single_head_feature_set")}
best single-head logloss: {fmt(by_case["listener_head_router_pretext"].get("best_single_head_logloss"), 6)}
router delta vs single: {fmt(by_case["listener_head_router_pretext"]["value"], 6)}
router delta vs prior: {fmt(by_case["listener_head_router_pretext"].get("delta_vs_prior"), 6)}
router delta vs raw lifelog PCA: {fmt(by_case["listener_head_router_pretext"].get("delta_vs_raw"), 6)}
router delta vs direct semantic: {fmt(by_case["listener_head_router_pretext"].get("delta_vs_direct_semantic"), 6)}
router delta vs naive multi-head: {fmt(by_case["listener_head_router_pretext"].get("delta_vs_naive_multi"), 6)}
router delta vs global transport: {fmt(by_case["listener_head_router_pretext"].get("delta_vs_global"), 6)}
row-block router delta vs global: {fmt(by_case["listener_head_router_pretext"].get("row_block_delta_vs_global"), 6)}
chronological router delta vs global: {fmt(by_case["listener_head_router_pretext"].get("chronological_delta_vs_global"), 6)}
```

살아남은 믿음:

```text
Target-aware listener-head routing is useful.
It beats best single future head and naive multi-head concat without using labels in the router.
```

죽은 믿음 또는 약해진 믿음:

```text
confidence / entropy / energy heuristics alone are already a sufficient learned router.
```

best가 dynamic confidence router가 아니라 semantic-prior router였다는 점을 과장 없이 남긴다.

```text
best router leakage: {fmt(by_case["listener_head_router_pretext"].get("best_router_leakage"), 6)}
best single-head leakage: {fmt(by_case["listener_head_router_pretext"].get("best_single_leakage"), 6)}
```

따라서 다음 core target은 분명하다.

```text
Learn the listener-head router as a JEPA pretext objective,
instead of relying on fixed semantic priors.
```

### 11. Learned Listener-Head Router Core

직전 실험은 fixed semantic-prior router가 best single future head를 이긴다는 결과를 남겼다.
이번 실험은 그 prior를 사람이 고정하지 않고, label-free hidden head-suitability field를
visible context와 predicted current/future/cohort heads에서 예측하게 했다.

```text
visible subject-relative human-life context
  + predicted current/future/cohort listener heads
  -> hidden head-suitability field prediction
  -> learned listener-head router
  -> routed HS-JEPA interface
```

핵심 결과:

```text
best learned router: {by_case["learned_listener_head_router_core"].get("best_learned_router_feature_set")}
best learned router logloss: {fmt(by_case["learned_listener_head_router_core"].get("best_learned_router_logloss"), 6)}
fixed semantic-prior router logloss: {fmt(by_case["learned_listener_head_router_core"].get("semantic_prior_router_logloss"), 6)}
best single head: {by_case["learned_listener_head_router_core"].get("best_single_head_feature_set")}
best single-head logloss: {fmt(by_case["learned_listener_head_router_core"].get("best_single_head_logloss"), 6)}
learned delta vs fixed semantic router: {fmt(by_case["learned_listener_head_router_core"]["value"], 6)}
learned delta vs single: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_single"), 6)}
learned delta vs prior: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_prior"), 6)}
learned delta vs raw lifelog PCA: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_raw"), 6)}
learned delta vs direct semantic: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_direct_semantic"), 6)}
learned delta vs naive multi-head: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_naive_multi"), 6)}
learned delta vs global transport: {fmt(by_case["learned_listener_head_router_core"].get("delta_vs_global"), 6)}
row-block learned delta vs global: {fmt(by_case["learned_listener_head_router_core"].get("row_block_delta_vs_global"), 6)}
chronological learned delta vs global: {fmt(by_case["learned_listener_head_router_core"].get("chronological_delta_vs_global"), 6)}
```

leakage도 의미가 있다.

```text
best learned router leakage: {fmt(by_case["learned_listener_head_router_core"].get("best_learned_leakage"), 6)}
fixed semantic-prior router leakage: {fmt(by_case["learned_listener_head_router_core"].get("semantic_prior_leakage"), 6)}
best single future head leakage: {fmt(by_case["learned_listener_head_router_core"].get("best_single_leakage"), 6)}
```

살아난 믿음:

```text
HS-JEPA can learn listener-head routing as a label-free hidden-state pretext,
not only as a hand-fixed semantic prior.
```

아직 죽지 않은 경계:

```text
The learned router beats semantic prior and best single head,
but it still does not beat global transported prototype grammar on subject-heldout.
```

따라서 논문적으로는 이 실험을 "완성된 decoder"가 아니라
`learned listener routing core evidence with global-transport boundary`로 기록한다.

### 12. Global Transport Residual Listener-Router Core

직전 실험에서 learned listener-head router는 fixed semantic prior와 best single head를 이겼지만,
subject-heldout global transport는 넘지 못했다. 그래서 질문을 replacement가 아니라 interface로 바꿨다.

```text
cross-subject transported prototype grammar
  + semantic listener router
  + learned listener-head router
  + learned-minus-semantic residual delta
  -> residual listener interface
```

핵심 결과:

```text
best residual feature set: {by_case["global_transport_residual_listener_router_core"].get("best_residual_feature_set")}
best residual logloss: {fmt(by_case["global_transport_residual_listener_router_core"].get("best_residual_logloss"), 6)}
global transport logloss: {fmt(by_case["global_transport_residual_listener_router_core"].get("global_transport_logloss"), 6)}
learned router alone logloss: {fmt(by_case["global_transport_residual_listener_router_core"].get("learned_alone_logloss"), 6)}
residual delta vs global: {fmt(by_case["global_transport_residual_listener_router_core"]["value"], 6)}
residual delta vs learned alone: {fmt(by_case["global_transport_residual_listener_router_core"].get("delta_vs_learned_alone"), 6)}
row-block delta vs global: {fmt(by_case["global_transport_residual_listener_router_core"].get("row_block_delta_vs_global"), 6)}
chronological delta vs global: {fmt(by_case["global_transport_residual_listener_router_core"].get("chronological_delta_vs_global"), 6)}
```

subject leakage도 중요한 증거다.

```text
best residual leakage: {fmt(by_case["global_transport_residual_listener_router_core"].get("best_residual_leakage"), 6)}
global transport leakage: {fmt(by_case["global_transport_residual_listener_router_core"].get("global_subject_leakage"), 6)}
raw lifelog leakage: {fmt(by_case["global_transport_residual_listener_router_core"].get("raw_subject_leakage"), 6)}
```

살아난 믿음:

```text
HS-JEPA core는 하나의 monolithic human-state vector가 아니다.
운반 가능한 human-state grammar를 backbone으로 두고,
listener-specific residual router가 target별 readout을 조절해야 한다.
```

하지만 같은 결과가 죽인 믿음도 있다.

```text
residual listener routing만 키우면 temporal drift까지 해결된다.
```

chronological delta가 양수이므로 temporal drift/action-health decoder는 별도 인터페이스로 풀어야 한다.

### 13. Rhythm-Conditioned Residual Listener Core

global residual listener router가 chronological에서 독성을 보였기 때문에,
이번 실험은 visible calendar/rhythm context가 temporal decoder와 residual listener readout을 분리할 수 있는지 검증했다.

```text
calendar rhythm confidence / entropy / energy
  -> rhythm stability gate
  -> stable residual listener channel
  -> unstable residual listener channel
  -> frozen subject-heldout / row-block / chronological probes
```

핵심 결과:

```text
subject best feature: {by_case["rhythm_conditioned_residual_listener_core"].get("subject_best_rhythm_feature_set")}
subject delta vs global: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("subject_best_rhythm_delta_vs_global"), 6)}
subject delta vs plain residual: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("subject_best_rhythm_delta_vs_plain_residual"), 6)}
row-block best feature: {by_case["rhythm_conditioned_residual_listener_core"].get("row_block_best_rhythm_feature_set")}
row-block delta vs global: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("row_block_best_rhythm_delta_vs_global"), 6)}
row-block delta vs plain residual: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("row_block_best_rhythm_delta_vs_plain_residual"), 6)}
chronological best feature: {by_case["rhythm_conditioned_residual_listener_core"].get("chronological_best_rhythm_feature_set")}
chronological best logloss: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("chronological_best_rhythm_logloss"), 6)}
chronological plain residual delta vs global: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("chronological_plain_residual_delta_vs_global"), 6)}
chronological rhythm delta vs global: {fmt(by_case["rhythm_conditioned_residual_listener_core"]["value"], 6)}
chronological rhythm delta vs plain residual: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("chronological_best_rhythm_delta_vs_plain_residual"), 6)}
chronological gated residual delta vs global: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("chronological_best_gated_residual_delta_vs_global"), 6)}
```

subject leakage:

```text
rhythm context leakage: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("rhythm_context_subject_leakage"), 6)}
best gated residual leakage: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("best_gated_residual_subject_leakage"), 6)}
plain residual leakage: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("plain_residual_subject_leakage"), 6)}
global transport leakage: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("global_subject_leakage"), 6)}
raw lifelog leakage: {fmt(by_case["rhythm_conditioned_residual_listener_core"].get("raw_subject_leakage"), 6)}
```

정확한 해석은 다음이다.

```text
temporal drift는 rhythm context가 가장 잘 읽는다.
subject/block readability는 rhythm-gated residual이 더 좋다.
따라서 HS-JEPA core는 rhythm-conditioned temporal decoder와
rhythm-gated listener residual interface를 분리해야 한다.
```

과장하면 안 되는 점도 분명하다.

```text
gated residual이 chronological을 완전히 해결한 것은 아니다.
chronological에서 best는 gated residual이 아니라 rhythm_context다.
```

논문 문장으로는 다음이 가장 안전하다.

```text
HS-JEPA separates human-state readability into two interfaces:
a rhythm-conditioned temporal decoder for chronological drift, and a
rhythm-gated listener residual for subject/block-invariant readout.
```

### 14. Routine-Break World Model

단순 current-state target 대신 subject-relative current state, previous-episode jump,
rolling personal-baseline residual을 hidden target으로 만들었다.
즉 질문을 다음처럼 바꿨다.

```text
visible human-life context
  -> hidden routine-break / episode-reset representation
```

subject-heldout low-trust frozen probe에서 prior 대비 delta는
`{fmt(by_case["routine_break_world_model"]["value"], 6)}`이다.
효과 크기는 여전히 작지만, 이전 subject-relative world model보다 더 선명한 core-positive signal이다.

### 15. Sleep-Pressure World Model

수면 label을 직접 target으로 쓰지 않고, night disturbance, physiological load,
social/cognitive arousal, rest-environment stability, calendar routine pressure를
label-free hidden target으로 만들었다.

```text
visible daily human-life context
  -> hidden sleep-pressure / recovery-load representation
```

subject-heldout low-trust frozen probe에서 prior 대비 delta는
`{fmt(by_case["sleep_pressure_world_model"]["value"], 6)}`이다.
pretext 예측성은 강하지만 label probe 효과는 작다. 이 결과는 HS-JEPA가
sleep-pressure representation을 만들 수 있다는 core evidence이면서,
그 representation을 Q/S label로 번역하려면 listener/action-health adapter가 필요하다는 경계이기도 하다.

### 16. Cohort-Relative World Model

routine-break와 sleep-pressure 기반 subject fingerprint로 singleton 없는 peer cohort를 만들고,
오늘의 state를 개인 기준과 peer 기준에서 동시에 해석했다.

```text
visible daily human-life context
  -> hidden personal-vs-peer cohort-relative representation
```

subject-heldout low-trust frozen probe에서 predicted cohort state의 prior 대비 delta는
`{fmt(by_case["cohort_relative_world_model"]["value"], 6)}`이다.
이는 현재 core world-model 계열에서 가장 강한 축에 속한다.

다만 중요한 경계가 있다.

```text
observed/full cohort geometry는 subject identity shortcut이 강하다.
core evidence는 observed state가 아니라 predicted cohort-relative state에만 둔다.
```

### 17. Multi-Target Human-State World Model

routine-break, sleep-pressure, cohort-relative hidden target을 따로 쓰지 않고,
하나의 route-preserving predicted bundle로 묶었다.

```text
visible human-life context
  -> predicted routine-break state
  -> predicted sleep-pressure state
  -> predicted personal-vs-peer cohort state
  -> route-preserving human-state bundle
```

subject-heldout low-trust frozen probe에서 이 bundle의 prior 대비 delta는
`{fmt(by_case["multi_target_human_state_world_model"]["value"], 6)}`이다.

중요한 ablation은 다음이다.

```text
predicted axes를 그대로 보존하면 positive.
PCA로 하나의 compressed latent로 뭉치면 negative.
```

따라서 HS-JEPA core thesis는 "모든 상태를 하나의 벡터로 압축한다"가 아니다.
더 정확한 thesis는 다음이다.

```text
여러 hidden human-state target representation을 예측하되,
downstream listener가 구분할 수 있도록 route axes를 보존한다.
```

### 18. Route-Responsibility Diagnostic

multi-target bundle 위에서 다른 route들로 held-out route를 예측하고,
그 residual energy로 label-free route responsibility를 만들었다.

```text
other predicted routes
  -> held-out route representation
  -> cross-route residual energy
  -> route responsibility
```

route pretext lift는 `{fmt(by_case["route_responsibility_world_model"].get("pretext_lift"), 6)}`로 매우 강하다.
하지만 responsibility-weighted axes는 base multi-target predicted bundle 대비
`{fmt(by_case["route_responsibility_world_model"]["value"], 6)}`만큼 logloss가 악화된다.

따라서 현재 결론은 다음이다.

```text
route responsibility는 label 없이 관측 가능하다.
하지만 단순 route weighting은 좋은 route-preserving bundle을 대체하지 못한다.
```

이것은 실패라기보다 HS-JEPA architecture boundary다.
다음 core는 route를 누르는 것이 아니라, listener가 route를 선택적으로 읽는 구조여야 한다.

### 19. Listener-Conditioned Route Readout

route-preserving multi-target bundle을 만든 뒤, frozen probe에서 target/listener별 route readout을 선택했다.
이 단계는 label-free core pretext가 아니라 frozen probe diagnostic이다.
하지만 논문적으로 중요하다.

```text
same HS-JEPA route bundle
  -> Q2 reads sleep-pressure
  -> S2 reads routine+cohort
  -> S3 reads cohort-relative
  -> S4 reads routine-break
```

subject-heldout low-trust probe에서 listener-conditioned route readout은
base multi-target bundle 대비 `{fmt(by_case["listener_conditioned_route_readout"]["value"], 6)}` logloss 개선을 보였다.
선택 route는 fold 단위로 `{by_case["listener_conditioned_route_readout"].get("fold_wins")}` wins를 기록했다.

이 결과가 의미하는 바는 다음이다.

```text
HS-JEPA core의 좋은 interface는 하나의 압축 latent도,
하나의 global route bundle도 아니다.
route axes를 보존하고, downstream listener가 target별로 다른 route를 읽게 해야 한다.
```

### 20. Subject-Invariant Listener Manifold

subject-invariant jury release target은 action geometry만으로도 어느 정도 분리될 수 있지만,
HS-JEPA listener manifold는 action-only 대비 AP lift가 `{fmt(by_case["subject_invariant_listener_manifold"]["value"], 6)}` 더 크다.

이 결과는 HS-JEPA core가 단순 action magnitude가 아니라,
row-target listener가 어떤 hidden state에서 반응해야 하는지를 더 잘 표현한다는 증거다.

### 21. Listener Responsibility Field

action을 바로 고르지 않고 먼저 `어느 row-target listener가 책임을 가져야 하는가`를 예측하면,
masked-pretext responsibility가 listener-only보다 AP lift `{fmt(by_case["listener_responsibility_field"]["value"], 6)}`만큼 앞선다.

이 증거는 크지는 않지만 논문적으로 중요하다.
HS-JEPA contribution을 `확률값 보정`이 아니라 `listener responsibility representation`으로 둘 수 있기 때문이다.

## 무엇을 과장하면 안 되는가

### Counterfactual Direction은 아직 Core가 아니다

raw/inverse direction oracle은 responsibility-selected cells에서 큰 양수 gain을 갖지만,
action-probability-free core가 복원한 best direction gain은 `{fmt(by_case["counterfactual_direction_pretext"]["value"], 6)}`이다.

따라서 현재는 다음 문장이 더 정확하다.

```text
HS-JEPA core는 어디를 볼지(listener responsibility)는 일부 복원하지만,
raw/inverse direction 자체는 아직 release-grade core representation으로 복원하지 못했다.
```

이것은 실패가 아니라 중요한 경계다.
논문에서 direction까지 core 성과로 과장하지 않게 해준다.

### Direct Label Classifier는 아니다

HS-JEPA state-only label probe는 prior 대비 logloss가 `{fmt(by_case["direct_label_prediction"]["value"], 6)}` 악화된다.
따라서 다음 문장은 쓰면 안 된다.

```text
HS-JEPA core만으로 Q/S label을 직접 잘 예측한다.
```

정확한 문장은 이렇다.

```text
HS-JEPA core는 label classifier가 아니라,
hidden human-state와 action-health를 더 읽기 쉬운 geometry로 바꾸는 representation module이다.
```

### Signed Direction은 Adapter Boundary다

signed listener direction 실험은 이전 responsibility decoder의 OOF gain을
`{fmt(by_case["signed_direction_translation"]["value"], 6)}`만큼 수리했다.
하지만 best direction family는 action geometry다.

따라서 이것은 pure core 승리가 아니라,
core가 위치를 좁히고 adapter가 방향 독성을 수리한 boundary case다.

## Candidate Files

{markdown_table(candidate_rows, ["case", "candidate", "role"])}

## Paper Thesis로 쓰기 좋은 문장

> HS-JEPA는 생활 로그를 직접 label로 매핑하지 않는다. 대신 보이는 인간 생활 context에서
> 보이지 않는 human-state와 listener-responsibility representation을 예측하고,
> 이 representation이 row-target action-health를 더 잘 분리하도록 만든다.
> 대회 adapter는 이 core geometry를 sparse correction으로 번역하는 별도 층이다.

## 다음 Big Bet

현재 가장 중요한 미해결 문제는 core representation의 효과 크기다.

```text
subject-relative world model: tiny positive
subject-invariant prototype grammar: pretext positive, low subject leakage, weak probe positive
cross-subject prototype transport: train-subject grammar transports to held-out subjects, but readout leakage must be controlled
transported prototype listener readout: global transported grammar보다 listener-specific readout이 subject-heldout에서 강하지만 frozen-probe diagnostic이다
label-free transported listener responsibility: prior/raw는 이기지만 global transport는 못 이겨 hand-coded semantic profile의 한계를 보인다
learned listener responsibility pretext: labels 없이 hand-coded profile보다 좋은 responsibility를 학습하지만 shortcut/leakage control이 남았다
invariant listener responsibility pretext: future consistency는 current-only보다 좋고 row/chron stress에서 강하지만, cohort pretext accuracy는 downstream utility와 분리된다
multi-head listener responsibility pretext: compact future head는 positive지만 naive head concat은 best single을 못 이겨 listener router가 필요하다
listener-head router pretext: semantic-prior router가 best single future head와 naive concat을 이기지만 confidence-only router는 아직 약하다
learned listener-head router core: hidden head-suitability pretext가 fixed semantic-prior router와 best single head를 이기지만 global transport는 아직 못 넘는다
routine-break world model: small positive and stronger hidden target
sleep-pressure world model: strong pretext, small label-probe positive
cohort-relative world model: predicted state positive, observed/full shortcut 위험
multi-target world model: route-preserving bundle positive, compressed latent negative
route responsibility diagnostic: pretext positive, route weighting은 base를 못 이김
listener-conditioned route readout: frozen probe에서 route별 listener interface positive
responsibility field: positive but small
direction/action translation: adapter 의존
direct label prediction: mostly negative without low-trust calibration
```

따라서 다음 실험은 adapter를 더 조정하는 것이 아니라,
subject-relative human-state target을 더 강하게 만들어야 한다.
후보는 global transport를 넘는 stronger head-suitability teacher,
sleep-pressure와 routine-break를 결합한 future-responsibility pretext,
cross-subject sleep-pressure prototype, listener-router를 action-health로 직접 연결하는 learned release gate,
그리고 hidden state를 action-health로 번역하는
open-loop world model이다.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases = collect_cases()
    summary = build_summary(cases)
    (OUT_DIR / "core_evidence_ledger_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    doc = build_markdown(summary)
    (OUT_DIR / "CORE_EVIDENCE_LEDGER_KO.md").write_text(doc, encoding="utf-8")
    PAPER_DOC.write_text(doc, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
