# E321 Mode-Specific Adversarial Action-Health Learner

Public LB was not used. No submission was created.

## Question

Can E319 row/subject/dateblock failures be predicted from candidate geometry and route metadata under held-out-candidate stress?

## Dataset

- pair rows: `564`
- candidates: `47`
- modes: `row, subject, dateblock`
- positive p90-win rate: `0.689716`
- positive pair-health rate: `0.251773`

## Pair OOF Metrics

| level | mode | task | feature_block | n | groups | positive_rate | auc | average_precision | logloss | spearman | pred_mean | pearson | rmse | top10_actual_ready_like | top10_mean_actual_health |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair | dateblock | null_not_strict | actual_geometry | 188 | 47 | 0.313830 | 0.853699 | 0.741493 | 0.468704 | 0.568703 | 0.402460 |  |  |  |  |
| pair | dateblock | null_not_strict | full_pair_geometry | 188 | 47 | 0.313830 | 0.841677 | 0.701138 | 0.509132 | 0.549256 | 0.384391 |  |  |  |  |
| pair | dateblock | null_not_strict | route_meta_only | 188 | 47 | 0.313830 | 0.833202 | 0.696389 | 0.477545 | 0.535747 | 0.408188 |  |  |  |  |
| pair | row | null_not_strict | route_meta_only | 188 | 47 | 0.510638 | 0.547554 | 0.585927 | 0.719383 | 0.082367 | 0.491087 |  |  |  |  |
| pair | row | null_not_strict | full_pair_geometry | 188 | 47 | 0.510638 | 0.544044 | 0.574864 | 0.872603 | 0.076271 | 0.483544 |  |  |  |  |
| pair | row | null_not_strict | actual_geometry | 188 | 47 | 0.510638 | 0.540761 | 0.611283 | 0.735983 | 0.070600 | 0.477968 |  |  |  |  |
| pair | subject | null_not_strict | full_pair_geometry | 188 | 47 | 0.457447 | 0.739398 | 0.718681 | 0.706705 | 0.413151 | 0.480424 |  |  |  |  |
| pair | subject | null_not_strict | route_meta_only | 188 | 47 | 0.457447 | 0.704742 | 0.623945 | 0.646689 | 0.353418 | 0.495361 |  |  |  |  |
| pair | subject | null_not_strict | actual_geometry | 188 | 47 | 0.457447 | 0.674191 | 0.611185 | 0.689393 | 0.300680 | 0.485159 |  |  |  |  |
| pair | dateblock | p90_win | full_pair_geometry | 188 | 47 | 0.702128 | 0.915720 | 0.962172 | 0.345946 | 0.658598 | 0.638551 |  |  |  |  |
| pair | dateblock | p90_win | route_meta_only | 188 | 47 | 0.702128 | 0.857684 | 0.917129 | 0.483652 | 0.566776 | 0.570461 |  |  |  |  |
| pair | dateblock | p90_win | actual_geometry | 188 | 47 | 0.702128 | 0.854437 | 0.900704 | 0.486144 | 0.561631 | 0.593548 |  |  |  |  |
| pair | row | p90_win | full_pair_geometry | 188 | 47 | 0.755319 | 0.821035 | 0.932172 | 0.556454 | 0.478095 | 0.603330 |  |  |  |  |
| pair | row | p90_win | actual_geometry | 188 | 47 | 0.755319 | 0.626761 | 0.841838 | 0.794494 | 0.188816 | 0.534572 |  |  |  |  |
| pair | row | p90_win | route_meta_only | 188 | 47 | 0.755319 | 0.606552 | 0.842946 | 0.758798 | 0.158715 | 0.526195 |  |  |  |  |
| pair | subject | p90_win | full_pair_geometry | 188 | 47 | 0.611702 | 0.930077 | 0.959419 | 0.332801 | 0.726099 | 0.588788 |  |  |  |  |
| pair | subject | p90_win | actual_geometry | 188 | 47 | 0.611702 | 0.828767 | 0.861134 | 0.504799 | 0.555175 | 0.556347 |  |  |  |  |
| pair | subject | p90_win | route_meta_only | 188 | 47 | 0.611702 | 0.812091 | 0.857875 | 0.529805 | 0.527014 | 0.529548 |  |  |  |  |
| pair | dateblock | pair_health | full_pair_geometry | 188 | 47 | 0.164894 | 0.841175 | 0.594181 | 0.445613 | 0.438578 | 0.297758 |  |  |  |  |
| pair | dateblock | pair_health | actual_geometry | 188 | 47 | 0.164894 | 0.798336 | 0.539721 | 0.484035 | 0.383590 | 0.313608 |  |  |  |  |
| pair | dateblock | pair_health | route_meta_only | 188 | 47 | 0.164894 | 0.779433 | 0.428140 | 0.506106 | 0.359285 | 0.322311 |  |  |  |  |
| pair | row | pair_health | full_pair_geometry | 188 | 47 | 0.404255 | 0.680569 | 0.650922 | 0.674184 | 0.306971 | 0.451845 |  |  |  |  |
| pair | row | pair_health | route_meta_only | 188 | 47 | 0.404255 | 0.607143 | 0.522313 | 0.687637 | 0.182184 | 0.471681 |  |  |  |  |
| pair | row | pair_health | actual_geometry | 188 | 47 | 0.404255 | 0.600094 | 0.518488 | 0.723500 | 0.170198 | 0.451441 |  |  |  |  |
| pair | subject | pair_health | full_pair_geometry | 188 | 47 | 0.186170 | 0.727731 | 0.459970 | 0.603711 | 0.307073 | 0.295757 |  |  |  |  |
| pair | subject | pair_health | route_meta_only | 188 | 47 | 0.186170 | 0.715126 | 0.400157 | 0.589045 | 0.290137 | 0.341453 |  |  |  |  |
| pair | subject | pair_health | actual_geometry | 188 | 47 | 0.186170 | 0.674043 | 0.357136 | 0.676225 | 0.234729 | 0.324722 |  |  |  |  |

## Candidate-Level Readout

| level | mode | task | feature_block | n | groups | positive_rate | auc | average_precision | logloss | spearman | pred_mean | pearson | rmse | top10_actual_ready_like | top10_mean_actual_health |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate | placement | pred_worst_placement_dominance_vs_worst_mode_p90_dominance | full_pair_geometry | 47 | 47 |  |  |  |  | 0.614177 |  | 0.614583 |  | 0.000000 | 0.300000 |
| candidate | placement | pred_null_strict_rate_vs_null_strict_rate | full_pair_geometry | 47 | 47 |  |  |  |  | 0.548433 |  | 0.567388 |  | 0.000000 | 0.300000 |
| candidate | placement | pred_adversarial_health_vs_actual_adversarial_health | full_pair_geometry | 47 | 47 |  |  |  |  | 0.508146 |  | 0.499586 |  | 0.000000 | 0.300000 |

- local ready-like candidates in E319 governed set: `0`
- ready-like candidates inside predicted top10: `0`
- best actual adversarial health: `0.722222`
- best actual adversarial health inside predicted top10: `0.638889`

## Predicted Top Candidates

| basename | policy | recipe | base_variant | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | pred_worst_placement_dominance | pred_null_strict_rate | pred_adversarial_health | actual_adversarial_health | ready_like_actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w8_00_ce1c1638.csv | human_identity_action_p90_rank | policy_all | selected_tbal | -0.002091 | 0.333333 | 0.944444 | 1.000000 | 0.750000 | 0.892126 | 0.360560 | 0.531566 | 0.416667 | False |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_tbal__c64__w3_00_8eb17e14.csv | human_regime_only | policy_recipe | selected_tbal | -0.001171 | 0.055556 | 0.888889 | 0.833333 | 0.000000 | 0.773445 | 0.301248 | 0.472197 | -0.055556 | False |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w5_00_ec3ac8dd.csv | human_identity_action_p90_rank | policy_all | selected_tbal | -0.001718 | 0.555556 | 0.944444 | 1.000000 | 0.750000 | 0.933826 | 0.473725 | 0.460101 | 0.194444 | False |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w1_50_83ddd459.csv | human_regime_only | policy_recipe | selected_maxmean | -0.001297 | 0.111111 | 0.944444 | 0.944444 | 0.750000 | 0.595161 | 0.219629 | 0.375532 | 0.638889 | False |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__call__w3_00_30eb2465.csv | regime_then_geometry | policy_recipe | selected_maxmean | -0.001489 | 0.388889 | 0.888889 | 0.777778 | 0.750000 | 0.402622 | 0.104906 | 0.297716 | 0.361111 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w8_00_7cf38a1d.csv | human_action_p90_rank | policy_top | selected_tbal | -0.001852 | 0.555556 | 1.000000 | 0.888889 | 1.000000 | 0.947884 | 0.653185 | 0.294699 | 0.444444 | False |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w5_00_3ba4b8d2.csv | regime_then_geometry | policy_mode | selected_maxmean | -0.001980 | 0.444444 | 0.944444 | 0.888889 | 0.750000 | 0.655662 | 0.428287 | 0.227376 | 0.305556 | False |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__call__w1_50_09016658.csv | regime_then_geometry | policy_recipe | selected_maxmean | -0.001259 | 0.111111 | 0.722222 | 0.833333 | 0.250000 | 0.611066 | 0.425362 | 0.185704 | 0.138889 | False |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w3_00_bddd61ce.csv | human_regime_only | policy_recipe | selected_maxmean | -0.001553 | 0.166667 | 0.944444 | 0.833333 | 0.750000 | 0.299301 | 0.142715 | 0.156586 | 0.583333 | False |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w5_00_b43c1dd0.csv | human_identity_action_p90_rank | policy_all | selected_maxmean | -0.002312 | 0.277778 | 0.722222 | 0.722222 | 0.250000 | 0.678010 | 0.524739 | 0.153271 | -0.027778 | False |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w8_00_2f5f5a54.csv | regime_then_geometry | policy_mode | selected_maxmean | -0.001960 | 0.277778 | 1.000000 | 0.944444 | 1.000000 | 0.711117 | 0.558969 | 0.152148 | 0.722222 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w5_00_fd5d9107.csv | human_action_p90_rank | policy_top | selected_tbal | -0.001566 | 0.611111 | 1.000000 | 1.000000 | 1.000000 | 0.907655 | 0.763992 | 0.143663 | 0.388889 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__call__w8_00_3ee568b1.csv | human_action_p90_rank | policy_top | selected_row2 | -0.001998 | 0.500000 | 0.944444 | 1.000000 | 0.750000 | 0.676205 | 0.688508 | -0.012303 | 0.250000 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c128__w3_00_7a6bc150.csv | human_action_p90_rank | policy_top | selected_maxmean | -0.001597 | 0.555556 | 0.944444 | 0.888889 | 0.750000 | 0.686740 | 0.699623 | -0.012883 | 0.194444 | False |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w8_00_d150a0e8.csv | human_identity_action_p90_rank | policy_all | selected_maxmean | -0.002547 | 0.333333 | 0.555556 | 0.611111 | 0.000000 | 0.453937 | 0.482180 | -0.028243 | -0.333333 | False |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__c128__w5_00_4c1487aa.csv | regime_then_geometry | policy_mode | selected_maxmean | -0.002083 | 0.350000 | 0.850000 | 0.900000 | 0.250000 | 0.375041 | 0.441933 | -0.066891 | -0.100000 | False |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w3_00_1dcc4429.csv | regime_then_geometry | policy_mode | selected_maxmean | -0.001799 | 0.555556 | 0.833333 | 0.888889 | 0.500000 | 0.446702 | 0.536387 | -0.089685 | -0.055556 | False |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w8_00_9d8aa4da.csv | human_identity_action_p90_rank | policy_all | selected_tbal | -0.002656 | 0.000000 | 0.777778 | 0.555556 | 0.500000 | 0.080193 | 0.185777 | -0.105585 | 0.500000 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__c128__w8_00_c4221343.csv | human_action_p90_rank | policy_top | selected_row2 | -0.001541 | 0.500000 | 0.888889 | 0.722222 | 0.750000 | 0.680647 | 0.793458 | -0.112812 | 0.250000 | False |
| submission_e319_modespec_human_action_p90_rank__top24__selected_vote2__c128__w8_00_fc7b441d.csv | human_action_p90_rank | policy_top | selected_vote2 | -0.001548 | 0.722222 | 0.888889 | 0.833333 | 0.500000 | 0.705587 | 0.823267 | -0.117680 | -0.222222 | False |

## Decision

- Pairwise placement health is learnable enough to use as a local target: full-pair p90-win AUC by mode is `row=0.821, subject=0.930, dateblock=0.916`.
- Candidate-level adversarial health ranking is useful but not sufficient: Spearman is `0.508146` and predicted top10 still contains `0` ready-like candidates.
- E321 is therefore a checker/diagnostic, not a submission source.
- The next branch should use this adversarial health model before materialization or as a preselector for extra local null evaluation. It should not spend public LB.

## Outputs

- `analysis_outputs/e321_mode_adversarial_action_health_pair_audit.csv`
- `analysis_outputs/e321_mode_adversarial_action_health_candidate_audit.csv`
- `analysis_outputs/e321_mode_adversarial_action_health_summary.csv`
- `analysis_outputs/e321_mode_adversarial_action_health_report.md`
