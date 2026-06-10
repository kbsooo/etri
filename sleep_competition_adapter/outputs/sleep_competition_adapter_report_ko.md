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
- A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.
- The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.
- Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.
- The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.

## 이 adapter가 아직 증명하지 못한 것

- pure OG-only assignment
- private leaderboard safety
- S2 as a universal human-sleep factor
- that public LB sensors can be used outside this competition
- that listener responsibility alone is an action-grade decoder
- that toxicity diagnostics prove private leaderboard safety
- that a hard-world mixture decoder will improve public/private LB before it is externally submitted
