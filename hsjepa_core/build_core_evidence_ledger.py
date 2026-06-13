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
            "prediction, subject-relative routine-break, sleep-pressure, cohort-relative "
            "prediction, route-preserving multi-target human-state prediction, and "
            "listener-conditioned route readout with subject-invariant listener/action-health separability."
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

### 3. Routine-Break World Model

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

### 4. Sleep-Pressure World Model

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

### 5. Cohort-Relative World Model

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

### 6. Multi-Target Human-State World Model

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

### 7. Route-Responsibility Diagnostic

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

### 8. Listener-Conditioned Route Readout

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

### 9. Subject-Invariant Listener Manifold

subject-invariant jury release target은 action geometry만으로도 어느 정도 분리될 수 있지만,
HS-JEPA listener manifold는 action-only 대비 AP lift가 `{fmt(by_case["subject_invariant_listener_manifold"]["value"], 6)}` 더 크다.

이 결과는 HS-JEPA core가 단순 action magnitude가 아니라,
row-target listener가 어떤 hidden state에서 반응해야 하는지를 더 잘 표현한다는 증거다.

### 10. Listener Responsibility Field

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
후보는 sleep-pressure와 routine-break를 결합한 listener-responsibility pretext,
cross-subject sleep-pressure prototype, 그리고 hidden state를 action-health로 번역하는
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
