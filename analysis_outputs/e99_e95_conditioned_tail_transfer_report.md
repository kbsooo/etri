# E99 E95-Conditioned Tail Transfer Audit

## Question

E96 explains the E72 public miss with hard-tail worlds. After E95 became public-positive, do those worlds still rank E90/E86/E85 the same way when they must also explain E95?

## Method

For every complete E96 scenario, solve `public_delta = alpha * local_delta + lambda * e96_tail_delta` exactly on failed E72 and E95. Then score unresolved candidates in the same scenario. Positive alpha/lambda means both local structural margin and hard-tail exposure have interpretable signs.

## Filter Summary

| filter | n_scenarios | alpha_median | alpha_p10 | alpha_p90 | lambda_median | lambda_p10 | lambda_p90 | winner_mode | best_mean_candidate | best_p95_candidate | e90_beat_e95_rate | e86_beat_e95_rate | e85_beat_e95_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| solved_all | 3894 | 3.636776433 | 0.947003308 | 8.061445287 | 1.379216614 | 1.098746622 | 1.840588923 | e95 | e95 | e95 | 0.002568053 | 0.000513611 | 0.028505393 |
| positive_transfer | 3849 | 3.690165944 | 1.019401770 | 8.074265977 | 1.384783684 | 1.106295807 | 1.841925771 | e95 | e95 | e95 | 0.002598077 | 0.000519615 | 0.028838659 |
| broad_plausible | 3452 | 3.310469910 | 0.948551319 | 6.794704168 | 1.345191741 | 1.098908037 | 1.708502366 | e95 | e95 | e95 | 0.002607184 | 0.000289687 | 0.031865585 |
| tight_plausible | 2790 | 2.716776749 | 0.923054525 | 5.232244732 | 1.283285733 | 1.096249417 | 1.545580452 | e95 | e95 | e95 | 0.002508961 | 0.000358423 | 0.035842294 |
| near_unit_tail | 2354 | 2.462161245 | 0.972785106 | 4.454604479 | 1.256736279 | 1.101434961 | 1.464493778 | e95 | e95 | e95 | 0.002973662 | 0.000424809 | 0.036108751 |

## Broad Plausible Candidate Summary

| candidate | n_scenarios | mean_pred_delta | p90_pred_delta | p95_pred_delta | mean_vs_e95 | p95_vs_e95 | beat_e95_rate | win_rate_live |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e95 | 3452 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.800405562 |
| e89 | 3452 | -0.000011477 | -0.000004841 | -0.000002759 | 0.000003833 | 0.000012552 | 0.195828505 | 0.188876014 |
| e85 | 3452 | -0.000005652 | 0.000001578 | 0.000002961 | 0.000009659 | 0.000018271 | 0.031865585 | 0.002607184 |
| e90 | 3452 | -0.000001938 | 0.000009905 | 0.000015934 | 0.000013372 | 0.000031244 | 0.002607184 | 0.001738123 |
| noq2 | 3452 | -0.000000021 | 0.000013658 | 0.000016182 | 0.000015290 | 0.000031492 | 0.023174971 | 0.006083430 |
| e86 | 3452 | 0.000005034 | 0.000026676 | 0.000031296 | 0.000020345 | 0.000046606 | 0.000289687 | 0.000289687 |

## Tight Plausible Candidate Summary

| candidate | n_scenarios | mean_pred_delta | p90_pred_delta | p95_pred_delta | mean_vs_e95 | p95_vs_e95 | beat_e95_rate | win_rate_live |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e95 | 2790 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.803942652 |
| e89 | 2790 | -0.000011647 | -0.000005272 | -0.000003706 | 0.000003664 | 0.000011605 | 0.192114695 | 0.183870968 |
| e85 | 2790 | -0.000006781 | -0.000000621 | 0.000001046 | 0.000008530 | 0.000016357 | 0.035842294 | 0.003225806 |
| e90 | 2790 | -0.000003010 | 0.000007225 | 0.000011881 | 0.000012301 | 0.000027192 | 0.002508961 | 0.001433692 |
| noq2 | 2790 | -0.000002495 | 0.000007797 | 0.000010374 | 0.000012816 | 0.000025685 | 0.028315412 | 0.007168459 |
| e86 | 2790 | 0.000003170 | 0.000025195 | 0.000030677 | 0.000018481 | 0.000045987 | 0.000358423 | 0.000358423 |

## Near-Unit Tail Candidate Summary

| candidate | n_scenarios | mean_pred_delta | p90_pred_delta | p95_pred_delta | mean_vs_e95 | p95_vs_e95 | beat_e95_rate | win_rate_live |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e95 | 2354 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.815632965 |
| e89 | 2354 | -0.000011536 | -0.000005409 | -0.000003847 | 0.000003774 | 0.000011464 | 0.180543755 | 0.171622770 |
| e85 | 2354 | -0.000007232 | -0.000001297 | 0.000000071 | 0.000008078 | 0.000015382 | 0.036108751 | 0.003823280 |
| e90 | 2354 | -0.000003626 | 0.000005435 | 0.000009628 | 0.000011685 | 0.000024939 | 0.002973662 | 0.001699235 |
| noq2 | 2354 | -0.000003578 | 0.000005530 | 0.000007497 | 0.000011733 | 0.000022808 | 0.029736619 | 0.006796941 |
| e86 | 2354 | 0.000001978 | 0.000017442 | 0.000029871 | 0.000017288 | 0.000045181 | 0.000424809 | 0.000424809 |

## Transfer Geometry

Solved scenarios: `3894`. Positive-transfer scenarios: `3849`. Broad-plausible scenarios: `3452`.
Alpha median/p10/p90: `3.636776433`, `0.947003308`, `8.061445287`.
Lambda median/p10/p90: `1.379216614`, `1.098746622`, `1.840588923`.
Max public-anchor residual after solving: E72 `0.000e+00`, E95 `0.000e+00`.

## Interpretation

Under broad-plausible E95-conditioned worlds, best mean candidate is `e95` and best p95 candidate is `e95`.
E90/E86/E85 beat-E95 rates are `0.002607`, `0.000290`, `0.031866`.
Read negative `mean_vs_e95` as predicted public improvement over the current E95 frontier and positive `p95_vs_e95` as downside tail relative to E95.

## Outputs

- Scenario table: `e99_e95_conditioned_tail_transfer_scenarios.csv`
- Candidate summary: `e99_e95_conditioned_tail_transfer_summary.csv`
- Filter summary: `e99_e95_conditioned_tail_transfer_filter_summary.csv`

