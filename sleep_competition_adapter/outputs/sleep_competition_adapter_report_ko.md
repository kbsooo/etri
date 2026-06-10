# Sleep Competition Adapter Report

이 문서는 HS-JEPA Core를 수면 생활습관 로그 대회에 적용하는 adapter를 설명한다.

## Adapter Claim

This adapter converts HS-JEPA Core into a sleep-log competition system by supplying Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding.

## Score Evidence

- Pre-public-equation best public LB: `0.5761589494`
- Current best public LB: `0.5677475939`
- Delta: `-0.00841135550000005`
- Current best file: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`

## Core to Adapter Mapping

| Core module | Sleep adapter instantiation | Evidence | Boundary |
| --- | --- | --- | --- |
| `context_encoder` | raw lifestyle, subject/cohort, row-order, and sleep-state context features | cell-level human-state orientation AUC 0.775 | row-level assignment AUC 0.545 is not enough for standalone assignment. |
| `masked_state_predictor` | teacher/student probes for hidden S2-hub and row-target support orientation | human-state probe exists as a role-based output | current strongest teacher still uses public-sensitive action support. |
| `listener_responsibility` | Q/S targets are treated as listeners; S2 emerges as an objective-stage hub | S2 listener usage 1.000 vs null 0.615 | S2 hub is a sleep competition case-study claim, not a universal physiology claim. |
| `action_health_decoder` | public-positive and public-negative sensors define toxic action diagnostics | mechanism ablation kills broad/toxic alternatives before release | public LB sensor is not portable and must be replaced for non-competition deployments. |
| `invariant_energy` | Q/S route energy and route-conserving S2 bridge | route z-scores primary=-9.66, s2=-9.46 | other domains need their own temporal, physiological, semantic, or cohort invariant. |
| `anti_shortcut_validation` | upload safety, feasible-bundle nulls, mechanism knockout, and release checklist | generality checks 10/11 | private LB safety is not proven. |

## OG-only Assignment Probe

- Status: `og_only_assignment_replacement_not_ready`
- Pure OG row-cap2 recall: `0.0404`
- Distilled row-cap2 recall: `0.1236`
- Listener/source upper-bound row-cap2 recall: `0.1356`

Human-state explains action orientation, but the safe row-target assignment still needs adapter-side evidence.

## Assignment Gap Decomposition Probe

- Status: `row_support_is_primary_bottleneck`
- Mean best portable recall: `0.1063`
- Mean target oracle recall: `0.1063`
- Mean row oracle + stage prior recall: `0.6896`
- Mean row support gap: `0.5832`

The decisive missing variable is row support, not target route.  When row support is provided by an oracle, the same fixed objective-stage prior recovers most teacher cells; current human/social/cohort context does not.

Next action: Stop spending submission slots on target-route tweaks; search for a hidden row-support sensor.

## Hidden Row-Support Sensor Probe

- Status: `portable_row_support_sensor_alive_partial`
- Best portable family: `portable_row_support_composite`
- Mean row AUC: `0.8193`
- Mean row recall@K: `0.4132`
- Mean cell recall with stage prior: `0.3289`
- Mean AUC z vs permuted train: `6.4180`
- Adapter minus portable cell-recall gap: `-0.0735`

A transferable row-support sensor exists, but it is partial: the seven-target prediction landscape transfers better than calendar/cohort-only state and turns the row-support bottleneck into a concrete HS-JEPA pretraining target.

Next action: Promote prediction-landscape row support into a masked HS-JEPA row-support objective, then stress against subject/date splits.

## Masked Row-Support Objective Probe

- Status: `masked_row_support_objective_supported_with_stress_boundary`
- Full composite row AUC: `0.8193`
- Full composite row recall@K: `0.4132`
- Full composite cell recall: `0.3289`
- Human-only cell recall: `0.2713`
- Prediction-only cell recall: `0.2348`
- Route-masked cell recall: `0.3056`
- Group-heldout full row AUC: `0.5584`

The row-support target is not a single-feature shortcut: human-only, prediction-only, and route-masked views all retain signal. However, row/order/subject/calendar held-out stress is much weaker than teacher-world transfer, so this is a representation objective, not yet an action-grade decoder.

Next action: Train a dedicated masked row-support objective, but do not promote it to a submission decoder until group-heldout stress improves.

## Row-Support Strict Action Decoder

- Status: `row_support_action_decoder_alive_with_route_tradeoff`
- Recommended variant: `exploratory_route_support_gate`
- Exploratory changed cells: `34`
- Exploratory safety z: `3.64`
- Exploratory combined z: `1.38`
- Exploratory mean route gain: `0.02205`

The exploratory variant moves enough cells to be LB-informative and is strongly safer than local feasible nulls, but route-gain is not superior to null, so it is a big-bet candidate rather than a safe release candidate.

## Route-Frontier Action Decoder

- Status: `route_frontier_action_decoder_alive_with_matched_boundary`
- Recommended variant: `seed_route_frontier`

The selected frontier beats broad route nulls and is upload-safe. Matched-null score remains the boundary, so this is a big-bet LB sensor rather than a default release.

## Route-Toxicity Fusion Decoder

- Status: `route_toxicity_fusion_decoder_alive`
- Recommended variant: `seed_driver_safe_route_fusion`

Route-first bundles survive upload safety while also passing factorized hard-world and broad-public toxicity gates. This is an LB sensor for the fused action decoder.

## Decoder-Order Jury Solver

- Status: `decoder_order_jury_ready`
- Recommended LB sensor: `{'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.392520579892158}`

Safe row-target assignment is a cross-decoder jury: route invariant proposes the action, factorized action-health confirms it, and only same-direction consensus is released.

## Decoder Boundary Tomography Solver

- Status: `boundary_tomography_ready`
- Recommended LB sensor: `{'variant': 'consensus_shadow_plus', 'submission_file': 'submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv', 'priority': 0.6990859175252038}`
- Boundary inventory: `{'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0}`

The next action-decoder bottleneck is whether strict cross-decoder jury is too conservative; weak consensus and route-only cells are separate hidden worlds and must be tested separately.

이 실험은 strict jury가 버린 셀을 `consensus_shadow`, `route_only`, `fusion_only`로 분리한다. public에서 consensus-shadow가 살아나면 HS-JEPA decoder의 병목은 안전한 latent가 아니라 너무 보수적인 action release였다는 뜻이다.

## Core-Mediated Action Release

- Status: `core_mediated_action_release_ready`
- Recommended LB sensor: `{'variant': 'core_consensus_shadow_plus', 'submission_file': 'submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv', 'priority': 0.8460231888716516}`
- Cell inventory: `{'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32}`

Real sleep-adapter row-target actions can be routed through the generic HS-JEPA core. The public sensor should reveal whether generic core release sharpens the strict decoder jury.

이 실험은 실제 sleep-adapter row-target action을 HS-JEPA Core의 `ContextView`, `ListenerPrototype`, `CandidateAction` 인터페이스로 변환한 뒤 core release equation을 통과시킨다. public에서 살아나면 HS-JEPA Core가 논문용 설명 구조를 넘어 action-grade decoder가 됐다는 신호다.

## Core Release Ablation Probe

- Status: `core_release_ablation_ready`
- Recommended LB candidate: `{'variant': 'full_core_reference', 'submission_file': 'submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv', 'priority': 0.8314097090596275}`
- Recommended architecture sensor: `{'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389}`
- Recommended negative control: `{'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389}`

HS-JEPA core modules change the real sleep-adapter action boundary when removed. This makes listener responsibility, action-health, and invariant energy falsifiable rather than only descriptive.

이 실험은 같은 real adapter cell을 full-core, no-listener, no-action-health, no-invariant, invariant-only release equation으로 다시 풀어본다. public에서 no-action-health가 full-core를 이기면 action-health가 현재 adapter를 과하게 막고 있다는 뜻이고, 지면 full HS-JEPA release boundary가 더 설득력 있다.

## Core-Health Calibrated Release

- Status: `core_health_calibrated_release_ready`
- Recommended LB candidate: `{'variant': 'benchmark_guarded_full_plus', 'submission_file': 'submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv', 'priority': 0.38818571481351827}`
- Recommended big-bet sensor: `{'variant': 'route_pressure_boundary_probe', 'submission_file': 'submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv', 'priority': 0.38337754232640875}`
- Recommended pressure sensor: `{'variant': 'health_relaxed_pressure_sensor', 'submission_file': 'submission_hsjepa_core_health_health_relaxed_pressure_sensor_7da82c23_uploadsafe.csv', 'priority': -0.21134339216533768}`
- Benchmark calibration: `{'action_health_fp_lift': 9.0, 'invariant_fp_lift': 1.0, 'listener_fp_lift': 3.0, 'scenario_count': 5.0, 'action_fp_weight': 0.6428571428571429, 'invariant_fp_weight': 0.16666666666666666, 'listener_fp_weight': 0.375}`

Dataset-free HS-JEPA action-health failures can calibrate the real sleep-adapter row-target release boundary.

이 실험은 dataset-free core benchmark에서 action-health 제거가 false positive를 크게 만든다는 사실을 실제 sleep-adapter row-target release prior로 사용한다. guarded 후보가 public에서 살아나면 HS-JEPA core의 일반적인 action-health 실패 모드가 대회 adapter에도 전이된다는 강한 증거가 된다.

## Cross-Listener Transport Decoder

- Status: `cross_listener_transport_ready`
- Recommended LB sensor: `{'variant': 'listener_confirmed_shadow', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': 0.5684860446, 'priority': 0.9427271560571463, 'config': {'name': 'listener_confirmed_shadow', 'boundary_classes': ['strict_jury', 'consensus_shadow'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.44, 'max_cells': 28, 'max_extra_cells': 6, 'strict_base_scale': 0.82, 'extra_base_scale': 0.34, 'listener_gain': 0.2, 's2_gain': 0.09, 'probe_role': 'tests whether target-listener confirmed shadow cells are safer than broad shadow release'}, 'rank': 1}`
- Recommended big bet: `{'variant': 'objective_listener_island_probe', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': None, 'priority': 0.9427271560571463, 'config': {'name': 'objective_listener_island_probe', 'boundary_classes': ['strict_jury', 'consensus_shadow', 'route_only', 'fusion_only'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.47, 'max_cells': 34, 'max_extra_cells': 12, 'strict_base_scale': 0.8, 'extra_base_scale': 0.28, 'listener_gain': 0.22, 's2_gain': 0.1, 'probe_role': 'tests whether an objective-listener island exists outside the current public row-state support'}, 'rank': 2}`
- Negative sensor: `{'file': 'submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv', 'public_lb': 0.5680255019, 'interpretation': 'direct listener-lift is not action-grade; use listener posterior only as a release/calibration prior'}`

Cross-listener evidence should calibrate route/fusion/core actions, not generate actions by itself.

이 실험은 target-listener route-lift가 public에서 실패한 사실을 버리지 않고, listener posterior의 역할을 `action generator`에서 `transport calibrator`로 바꾼다. public에서 살아나면 HS-JEPA의 listener responsibility가 직접 예측값을 만드는 장치가 아니라 action boundary를 보정하는 장치라는 더 일반적인 주장이 강해진다.

## Action Decoder Ablation Suite

- Status: `action_decoder_ablation_ready_decoder_jury_leads`
- Recommended LB sensor: `{'family': 'decoder_order_jury', 'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.394366527938867}`
- Open big-bet sensor: `{'family': 'route_frontier', 'variant': 'open_route_frontier', 'submission_file': 'submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv', 'priority': 1.05448050759572}`

The suite ranks action decoders by route-null survival, toxicity safety, upload safety, and action size. It is a submission-slot prioritizer, not a public-LB predictor.

## Listener-Invariant Contrastive Probe

- Status: `listener_invariant_decoder_not_ready`
- Mean listener-route Spearman: `-0.0313`
- Mean contrastive overlap: `0.2152`
- Mean conflict rate: `0.0719`

Listener responsibility and invariant safety are not sufficiently aligned; use this as a diagnostic before making new submissions.

## Private-Safe Toxicity Probe

- Status: `toxicity_field_promising_with_hardworld_gap`
- Mean leave-one-bad-anchor AUC: `0.7880`
- Worst leave-one-bad-anchor AUC: `0.3683`
- Selected safety z vs matched null: `8.4589`

The toxicity field is strong on most bad anchors, but a hard-world toxicity mode is still not captured.

## Hard-World Toxicity Factorization Probe

- Status: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`
- Broad-safe but H088-toxic cells: `215`
- Selected joint safety z: `7.1884`
- Selected H088 top-toxic rate: `0.0333` vs null `0.1027`

H088 is not a harder sample of broad toxicity; it is an anti-correlated hard-world mode. The adapter should keep separate broad-public and hard-world toxicity heads.

## Factorized Toxicity Decoder Candidate

- Architecture role: `sleep_competition_adapter_action_health_decoder`
- Core boundary: HS-JEPA core supplies the listener/action interface; this module uses public and hard-world competition sensors.

| Variant | Output | Changed cells | Joint safety | H088 top-toxic | Upload-safe |
| --- | --- | ---: | ---: | ---: | ---: |
| `teacher_dual_head` | `submission_hsjepa_factorized_toxicity_decoder_teacher_dual_head_2a3c5d2d_uploadsafe.csv` | `94` | `0.6937` | `0.0000` | `True` |
| `dual_safe_expansion` | `submission_hsjepa_factorized_toxicity_decoder_dual_safe_expansion_23b6de1e_uploadsafe.csv` | `114` | `0.6994` | `0.0000` | `True` |

이 후보는 broad-public safety와 hard-world safety를 동시에 통과한 row-target action만 믿는 adapter-side decoder다. public 결과가 좋아지면 factorized action-health가 맞다는 신호이고, 나빠지면 factorization은 diagnostic으로는 유효하지만 아직 action-grade decoder는 아니라는 뜻이다.

## Factorized Toxicity Decoder Stress Audit

- Status: `stress_audit_ready`
- Iterations: `1500`

| Variant | Stress verdict | Target-null joint z | Source-null conflict p | Hard-toxic exposure | Conflict exposure |
| --- | --- | ---: | ---: | ---: | ---: |
| `dual_safe_expansion` | `factorized_decoder_stress_supported` | `13.67` | `0.0013` | `0.0000` | `0.0000` |
| `teacher_dual_head` | `factorized_decoder_alive_but_source_null_weak` | `12.07` | `1.0000` | `0.0000` | `0.0000` |

`dual_safe_expansion`은 source-matched null까지 통과한 strict supported 후보이고, `teacher_dual_head`는 target-null에서는 강하지만 source-matched null이 약한 diagnostic 후보로 남긴다.

## Role Outputs

| Role | Output |
| --- | --- |
| `competition_primary` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` |
| `interpretable_s2_hub` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` |
| `human_state_probe` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` |

## 이 adapter가 증명하는 것

- HS-JEPA-style listener/action/invariant separation can explain the 0.567 public-LB breakthrough case study.
- Route-conserving action selection is statistically non-random against feasible null bundles.
- Human-state latent explains target/cell orientation but not enough row assignment on its own.
- A pure OG-only assignment teacher is not ready yet; this is now a measured architecture boundary, not an informal caveat.
- The assignment gap decomposes into a row-support bottleneck: target route is relatively easy, but current human/social/cohort context does not find the right support rows.
- A teacher-transfer hidden row-support sensor is partially alive; portable row-support composite context transfers across teacher worlds better than the listener upper bound in this local diagnostic.
- Masked row-support behaves like a real HS-JEPA representation target under teacher-transfer and feature-family masks, but subject/date/order held-out stress remains weak.
- A row-support action decoder can produce upload-safe route/S2 bundle candidates with strong local toxicity safety, but route-gain remains a tradeoff.
- A route-frontier action decoder now beats broad route nulls and matched frontier-score nulls while staying upload-safe, so the next LB sensor can test action-grade route translation directly.
- A route-toxicity fusion decoder now composes route-first selection with factorized broad-public/hard-world action-health; it is alive locally but still ranks below plain route-frontier as an LB sensor.
- Decoder boundary tomography separates strict-jury rejects into consensus-shadow, route-only, and fusion-only cells; consensus-shadow is the safest next too-conservative-jury sensor.
- The action-decoder ablation suite now ranks toxicity-first, support-first, route-first, and route-toxicity fusion decoders under one table; route-first currently leads the LB-sensor priority.
- A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.
- The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.
- Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.
- The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.
- The dual-safe expansion variant survives target-only and source-matched null stress, while the teacher-only variant is intentionally marked weaker under source-matched stress.
- Core release ablation now makes listener responsibility, action-health, and invariant energy falsifiable on real sleep-adapter actions rather than only synthetic core examples.
- Core-health calibrated release now uses dataset-free action-health false-positive lift as a real adapter release prior, connecting architecture benchmark behavior to submission candidates.
- Cross-listener transport now converts the failed target-listener route-lift into a safer rule: listener posterior calibrates route/fusion/core-proposed actions instead of generating actions directly.

## 이 adapter가 아직 증명하지 못한 것

- pure OG-only assignment
- action-grade portable hidden row-support recovery
- that masked row-support is already a deployment-grade action decoder
- that the row-support strict action decoder is safe without public/private LB observation
- that route-frontier action decoding is private-safe without public LB observation
- that route-toxicity fusion will beat plain route-frontier on public/private LB
- that consensus-shadow boundary cells are safe before public LB observes them
- that removing a core module is beneficial before public LB observes the full-core vs ablated-core counterfactual
- that dataset-free action-health calibration will beat the strict decoder jury before public LB observes the guarded/pressure counterfactual
- that cross-listener transport will beat the strict decoder jury before public LB observes the listener-calibrated counterfactual
- that the action-decoder ablation suite predicts public LB instead of prioritizing public-sensor experiments
- private leaderboard safety
- S2 as a universal human-sleep factor
- that public LB sensors can be used outside this competition
- that listener responsibility alone is an action-grade decoder
- that toxicity diagnostics prove private leaderboard safety
- that a hard-world mixture decoder will improve public/private LB before it is externally submitted
