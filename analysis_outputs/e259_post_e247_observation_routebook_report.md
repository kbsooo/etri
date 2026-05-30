# E259 Post-E247 Observation Routebook

## Question

E247 is the public frontier, but what exactly did public reward: E224's body, E247's Q3 rollback, or the exact interaction?

This routebook pre-registers how to read the next two clean observations before those scores are known:

- `E256`: `submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` tests high-amplitude Q3 smoothing versus E247's broader top34 smoothing.
- `E224`: `submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv` tests whether the E224 body alone carried the E247 win.

## Current Public Anchors

| anchor | public LB | delta vs E247 |
| --- | ---: | ---: |
| E247 current best | 0.5761589494 | 0.0000000000 |
| E95 previous hardtail | 0.5762913298 | 0.0001323804 |
| E101 Q2/S3 tail | 0.5763003660 | 0.0001414166 |
| mixmin | 0.5763066405 | 0.0001476911 |
| E216 bad JEPA S2 | 0.5772865088 | 0.0011275594 |

## Observed Anatomy Being Split

### E247 vs E256 Cell Groups

| group | n_rows | rollback_amp_mean | smooth_gain_sum | affected_pair_abs_delta | support_prob_focus_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| common | 21.000000000 | 0.084600496 | 2.553030589 | -0.082355825 | 0.427641668 | 1.377017065 |
| e247_only | 13.000000000 | 0.039125051 | 1.002858981 | -0.032350290 | 0.453917630 | 17.859802610 |
| e256_only | 4.000000000 | 0.110316918 | 0.049289874 | -0.008214979 | 0.531582541 | 4.055804917 |
| e247_all | 34.000000000 | 0.067212826 | 3.555889570 | -0.057353058 | 0.433489917 | 1.413603067 |
| e256_all | 25.000000000 | 0.088715124 | 2.602320463 | -0.070332985 | 0.448321681 | 1.983036023 |
| neither | 212.000000000 | 0.029330058 | -4.715437421 | 0.018688672 | 0.458158603 | 0.622308837 |

### Body/Rollback Components

| component_id | moved_cells | targets_moved | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| e224_body_vs_e95 | 534.000000000 | Q1,Q3,S2,S3,S4 | -0.000653189 | 0.004094069 | 0.465789507 | 0.150551319 |
| e247_rollback_vs_e224 | 34.000000000 | Q3 | -0.000066519 | 0.000673258 | 0.566510083 | 1.413603067 |
| e256_rollback_vs_e224 | 25.000000000 | Q3 | -0.000047418 | 0.000651756 | 0.551678319 | 1.983036023 |
| e247_total_vs_e95 | 513.000000000 | Q1,Q3,S2,S3,S4 | -0.000719708 | 0.003497893 | 0.470775642 | 0.136636606 |
| e256_total_vs_e95 | 520.000000000 | Q1,Q3,S2,S3,S4 | -0.000700607 | 0.003501586 | 0.468433641 | 0.140361815 |
| e224_body_vs_e154 | 355.000000000 | Q3,S4 | -0.000623352 | 0.003400775 | 0.465984132 | 0.157757659 |

### Rollback Opposes Body

| component_id | selected_cells | cos_body_rollback_selected | rollback_abs_over_selected_body_abs | opposite_sign_share_selected |
| --- | --- | --- | --- | --- |
| e247_rollback_vs_e224 | 34.000000000 | -0.992683110 | 0.984581403 | 1.000000000 |
| e256_rollback_vs_e224 | 25.000000000 | -0.995302880 | 0.982187223 | 1.000000000 |

## Routebook

| candidate_id | outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | world_update_class | next_action |
| --- | --- | --- | --- | --- | --- |
| E256 | amplitude_smoothing_breakthrough | -inf | 0.576138949 | strong_support | Promote amplitude-constrained smoothing. Search around high-amplitude cells only after auditing private risk; do not restore E247-only broad cells. |
| E256 | clean_win | 0.576138949 | 0.576155949 | support | Use E256 as new operational anchor, then run an E256-vs-E247-only attribution audit before any sibling. |
| E256 | tie | 0.576155949 | 0.576161949 | underresolved | Do not tune smoothing siblings. Use E224 if attribution is still needed, or switch to a non-collinear question. |
| E256 | near_loss | 0.576161949 | 0.576188949 | weak_rejection | Keep E247 as anchor. Do not submit high-amplitude siblings. If continuing, isolate E247-only cells rather than increasing amplitude. |
| E256 | same_family_loss | 0.576188949 | 0.576291330 | rejection | Stop sibling sweeps. Submit E224 only if the next question is body attribution; otherwise search non-collinear structure. |
| E256 | hard_loss | 0.576291330 | inf | hard_rejection | Close E256-like refinements. Treat E247 as a fragile public observation until E224 attribution or another independent sensor confirms the body. |
| E224 | body_breakthrough | -inf | 0.576138949 | strong_support | Promote E224 body as the core law. Audit rollback harm cells; do not add Q3 smoothing until a body-preserving gate exists. |
| E224 | body_tie_or_micro_win | 0.576138949 | 0.576161949 | support | Use E224 as attribution-confirmed anchor. Revisit Q3 rollback only as a private-risk reducer, not as a score requirement. |
| E224 | rollback_helped | 0.576161949 | 0.576291330 | mixed_support | Keep E247 as anchor. Use E256 result if available to decide broad vs amplitude rollback; otherwise do not remove rollback. |
| E224 | body_not_enough | 0.576291330 | 0.576306641 | weak_rejection | Demote body-only candidates. Keep E247; if exploring, target Q3 tail correction rather than larger body. |
| E224 | body_loss | 0.576306641 | 0.577286509 | rejection | Do not submit E224 siblings. Treat E247 as a specific body-plus-trim construction and move to non-collinear structure. |
| E224 | body_collapse | 0.577286509 | inf | hard_rejection | Close current E211/E224 translator lane as submissions. Keep it only as a diagnostic latent. |

## Score Examples

| candidate_id | score | delta_vs_e247 | outcome | world_update_class |
| --- | --- | --- | --- | --- |
| E256 | 0.576108949 | -0.000050000 | amplitude_smoothing_breakthrough | strong_support |
| E256 | 0.576148949 | -0.000010000 | clean_win | support |
| E256 | 0.576158949 | 0.000000000 | tie | underresolved |
| E256 | 0.576168949 | 0.000010000 | near_loss | weak_rejection |
| E256 | 0.576281330 | 0.000122380 | same_family_loss | rejection |
| E256 | 0.576301330 | 0.000142380 | hard_loss | hard_rejection |
| E256 | 0.576326641 | 0.000167691 | hard_loss | hard_rejection |
| E224 | 0.576108949 | -0.000050000 | body_breakthrough | strong_support |
| E224 | 0.576148949 | -0.000010000 | body_tie_or_micro_win | support |
| E224 | 0.576158949 | 0.000000000 | body_tie_or_micro_win | support |
| E224 | 0.576168949 | 0.000010000 | rollback_helped | mixed_support |
| E224 | 0.576281330 | 0.000122380 | rollback_helped | mixed_support |
| E224 | 0.576301330 | 0.000142380 | body_not_enough | weak_rejection |
| E224 | 0.576326641 | 0.000167691 | body_loss | rejection |

## Decoded Future Scores

_No future score was supplied._

## Decision

- If the next public slot should still try to improve score while answering a clean question, use E256.
- If the next public slot should maximize attribution information, use E224.
- Do not blend E247/E256/E224 before one of these two axes is observed; blending would hide the only clean causal split left.

## Interpretation Shortcut

- E256 win: high-amplitude constrained feature-NN1 smoothing is stronger than broad top34 smoothness.
- E256 close loss: E247-only low-amplitude broad smoothing is public signal.
- E256 hard loss: exact E247 top34 or body interaction matters.
- E224 win/tie: E224 body carried most of the win; rollback is optional or over-pruning.
- E224 better than E95 but worse than E247: body is real, rollback is necessary.
- E224 worse than mixmin: body-only translator is unsafe; E247 was a rescued interaction, not a general body law.
