# E253 E237/E250 Union OOF Analogue

## Question

Does the E252 union have train-OOF support, or is it only a submission-side materialization artifact?

## Headline

- E237 parent OOF loss_vs_full: `-0.000271441`.
- E250 parent OOF loss_vs_full: `-0.000185023`.
- Union OOF loss_vs_full: `-0.000080010`.
- Union minus best parent: `0.000191431`.
- Union stress_promote: `True`.
- Train Q3 overlap: E237 `25`, E250 `21`, shared `12`, union `34`.

## OOF Variants

| candidate_id | source_type | q3_rows | overlap_e237 | overlap_e250 | shared_cells_in_candidate | e237_only_cells_in_candidate | e250_only_cells_in_candidate | loss_vs_full | active_policy_delta | active_full_delta | q3_policy_delta | q3_full_delta | subject_win_rate | dropped_mean_benefit | tail_auc | tail_auc_vs_e237_label_max | tail_auc_vs_e250_label_max | stress_promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shared_intersection | overlap | 12 | 12 | 12 | 12 | 0 | 0 | -0.000376454 | -0.004222579 | -0.003846124 | -0.005015022 | -0.004262113 | 0.700000000 | -0.028234084 | 0.893668754 | 0.883292181 | 0.873923805 | True |
| e237_parent | known_e237_oof | 25 | 25 | 12 | 12 | 13 | 0 | -0.000271441 | -0.004117566 | -0.003846124 | -0.004804996 | -0.004262113 | 0.700000000 | -0.009771889 | 0.901873158 | 0.883292181 | 0.873923805 | True |
| e250_parent | known_e250_oof | 21 | 12 | 21 | 12 | 0 | 9 | -0.000185023 | -0.004031148 | -0.003846124 | -0.004632160 | -0.004262113 | 0.800000000 | -0.007929566 | 0.887356598 | 0.883292181 | 0.873923805 | True |
| union_e237_e250 | union | 34 | 25 | 21 | 12 | 13 | 9 | -0.000080010 | -0.003926134 | -0.003846124 | -0.004422133 | -0.004262113 | 0.800000000 | -0.002117914 | 0.899699806 | 0.883292181 | 0.873923805 | True |
| e237_only | difference | 13 | 13 | 0 | 0 | 13 | 0 | 0.000105013 | -0.003741111 | -0.003846124 | -0.004052087 | -0.004262113 | 0.700000000 | 0.007270138 | 0.901873158 | 0.883292181 | 0.873923805 | False |
| e250_only | difference | 9 | 0 | 9 | 0 | 0 | 9 | 0.000191431 | -0.003654693 | -0.003846124 | -0.003879251 | -0.004262113 | 0.800000000 | 0.019143125 | 0.887356598 | 0.883292181 | 0.873923805 | False |
| symmetric_difference | difference | 22 | 13 | 9 | 0 | 13 | 9 | 0.000296444 | -0.003549680 | -0.003846124 | -0.003669224 | -0.004262113 | 0.800000000 | 0.012127269 | 0.899699806 | 0.883292181 | 0.873923805 | False |

## Decision

- E252 has weak OOF support: union is stress-promoted but does not beat the best parent. Keep it as a complementarity sensor, not as the likely-score leader.
- Public LB is not used and no submission is created.
