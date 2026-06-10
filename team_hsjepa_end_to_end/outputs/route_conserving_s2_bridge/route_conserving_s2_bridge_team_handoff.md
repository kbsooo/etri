# Route-Conserving S2 Bridge HS-JEPA Team Handoff

이 파일은 팀원이 과거 실험 버전명을 몰라도 현재 HS-JEPA 패키지의 실행 결과와 논문용 주장을 한 번에 이해하도록 만든 최종 핸드오프 요약이다.

## One-Command Reproduction

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

전체 dependency까지 재생성하려면:

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py --refresh
```

## Core Mechanism

```text
HS-JEPA Core:
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation

Sleep Competition Adapter:
public-sensitive driver action
  + route-conserving bridge action
  + S2 listener/hub constraint
  + upload-safe sparse row-target decoder
```

축구 비유로 말하면, HS-JEPA Core는 `상황을 읽고, listener와 action 위험을 분리한 뒤, 궤적 불변성을 보존하는 슛 기술`이다. Sleep Adapter의 S2 bridge는 그 기술이 이번 경기장에서 구현된 case-study 궤적이다.

## Core / Adapter Separation

- Core status: `core_ready_for_adapter` (`5/5` gates)
- Core ablation contract: `6` modules, `4` big-bet followups
- Adapter status: `adapter_ready_with_public_sensor_boundary`
- Adapter score delta: `-0.00841135550000005`
- OG-only assignment probe: `og_only_assignment_replacement_not_ready`
- Listener-invariant contrastive probe: `listener_invariant_decoder_not_ready`
- Private-safe toxicity probe: `toxicity_field_promising_with_hardworld_gap`

Core 문서:

```text
hsjepa_core/outputs/hsjepa_core_manifest_ko.md
hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md
```

Adapter 문서:

```text
sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md
sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md
sleep_competition_adapter/outputs/og_only_assignment_teacher_probe_ko.md
sleep_competition_adapter/outputs/listener_invariant_contrastive_probe_ko.md
sleep_competition_adapter/outputs/private_safe_toxicity_probe_ko.md
```

## Generated Submission Roles

| Role | File | Upload-safe | Changed cells |
| --- | --- | ---: | ---: |
| `competition_primary` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` | `True` | `82` |
| `interpretable_s2_hub` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` | `True` | `68` |
| `human_state_probe` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` | `True` | `68` |

## Mechanism Evidence

| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage | Route p | S2 p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `route_conserving_objective_bridge_primary` | `-0.02457` | `-0.01090` | `0.780` | `0.615` | `0.0000` | `0.0006` |
| `s2_listener_bridge_interpretable` | `-0.02696` | `-0.01082` | `1.000` | `0.615` | `0.0000` | `0.0000` |

자동 validator가 확인한 핵심 수치:

- Primary route z-score: `-9.66`
- S2 listener route z-score: `-9.46`
- S2 listener usage: `1.000` vs null `0.615`
- Package validation passed: `True`
- Architecture readiness: `paper_ready_with_boundary` (`7/7` gates)
- Mechanism ablation: `mechanism_ablation_ready` (`5` public worldviews killed, `2` survived)
- Generality boundary: `general_architecture_separated_with_case_boundary` (`5/6` portability checks, nonblocking boundaries: `1`)
- Core/adapter boundary: core `core_ready_for_adapter`, adapter `adapter_ready_with_public_sensor_boundary`
- OG-only assignment boundary: pure recall `0.0404`, distilled recall `0.1236`
- Listener-invariant boundary: listener-route rho `-0.0313`, contrastive overlap `0.2152`
- Private-safe toxicity boundary: mean LOO AUC `0.7880`, worst LOO AUC `0.3683`
- Release checklist: `release_ready_with_boundary` (`37/37` checks)

## Paper Claim

강하게 주장할 수 있는 내용:

```text
HS-JEPA is a core architecture for human-understanding prediction.
It predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations.
The sleep competition adapter instantiates the invariant as Q/S route energy and the listener bridge as S2.
The current LB breakthrough is evidence for this adapter, while the reusable claim is the core/action separation.
```

## Big-Bet Queue

다음 큰 실험은 단순 alpha 조정이 아니라 core/adaptor 경계를 바꾸는 실험이다.

- `OG-only Human-State Assignment Teacher`: The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. Expected LB delta if true `-0.003`.
- `Listener-Invariant Contrastive Decoder`: A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. Expected LB delta if true `-0.002`.
- `Private-Safe Toxicity Field`: The plateau comes from actions that help public-like rows but poison private-like rows. Expected LB delta if true `-0.0015`.
- `Cross-Listener Human-State Transport`: Subjective Q and objective S labels are different listeners of one human state, not separate tasks. Expected LB delta if true `-0.001`.

## Competition Use

제출 슬롯이 있다면 우선순위는 다음이다.

1. `competition_primary`: 성능 중심 Route-Conserving Objective Bridge
2. `interpretable_s2_hub`: 논문 설명력이 가장 강한 S2 Listener Bridge
3. `human_state_probe`: OG human-state orientation diagnostic

## Reproducibility Contract

이 패키지는 입력을 다음처럼 분리해서 기록한다.

```text
OG raw data != public-LB sensor != generated action artifact
```

계약 문서:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md
```

## Boundary

이 패키지가 증명하지 않는 것:

- private leaderboard safety
- OG human-state encoder 단독으로 row-target assignment 해결
- S2가 모든 수면 생리학적 factor의 중심이라는 주장

정확한 결론은 더 좁고 강하다.

```text
Given a public-sensitive action field, route conservation plus S2 listener usage selects a statistically unusual and interpretable correction path.
```

## Architecture Readiness Report

논문/팀 공유용 gate 판정:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md
```

## Paper Method Packet

논문 초안/발표에 바로 옮길 수 있는 method packet:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md
```

## Mechanism Ablation Report

대체 세계관 중 무엇이 public sensor/stress audit에서 죽었고 무엇이 살아남았는지 정리한 knockout report:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report_ko.md
```

## Generality Report

HS-JEPA의 범용 아키텍처와 이번 대회의 Route-Conserving S2 Bridge case study를 분리한 portability report:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report_ko.md
```

## Pipeline Manifest

OG 데이터에서 public sensor, latent/context, route decoder, submission, paper packet까지 이어지는 역할 기반 pipeline:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest_ko.md
```

## Release Checklist

팀 공유/논문 발표/제출 논의용 최종 release gate:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist_ko.md
```
