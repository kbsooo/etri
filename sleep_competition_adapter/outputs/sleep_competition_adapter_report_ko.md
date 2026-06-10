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
| `anti_shortcut_validation` | upload safety, feasible-bundle nulls, mechanism knockout, and release checklist | generality checks 5/6 | private LB safety is not proven. |

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

## Action Decoder Ablation Suite

- Status: `action_decoder_ablation_ready_route_frontier_leads`
- Recommended LB sensor: `{'family': 'route_frontier', 'variant': 's2_route_frontier', 'submission_file': 'submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv', 'priority': 1.1177646805596027}`
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
- The action-decoder ablation suite now ranks toxicity-first, support-first, route-first, and route-toxicity fusion decoders under one table; route-first currently leads the LB-sensor priority.
- A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.
- The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.
- Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.
- The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.
- The dual-safe expansion variant survives target-only and source-matched null stress, while the teacher-only variant is intentionally marked weaker under source-matched stress.

## 이 adapter가 아직 증명하지 못한 것

- pure OG-only assignment
- action-grade portable hidden row-support recovery
- that masked row-support is already a deployment-grade action decoder
- that the row-support strict action decoder is safe without public/private LB observation
- that route-frontier action decoding is private-safe without public LB observation
- that route-toxicity fusion will beat plain route-frontier on public/private LB
- that the action-decoder ablation suite predicts public LB instead of prioritizing public-sensor experiments
- private leaderboard safety
- S2 as a universal human-sleep factor
- that public LB sensors can be used outside this competition
- that listener responsibility alone is an action-grade decoder
- that toxicity diagnostics prove private leaderboard safety
- that a hard-world mixture decoder will improve public/private LB before it is externally submitted
