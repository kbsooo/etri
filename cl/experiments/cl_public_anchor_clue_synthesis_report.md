# CL Public-Anchor Clue Synthesis

## Claim

The only honest way to chase 0.57 from the current evidence is not to replace the proven 0.599 public anchor. It is to keep v83/v76 public coordinates and add only centered, target-isolated CL clue residuals.

## Public Posterior Refit

- Constraints used: v76_anchor, v83_repaired, v18_old15, sample_support, v82_failed, v85_failed, cl_catboost_safe, cl_sleep_state, cl_imported_failed, cl_wcap02
- Max constraint error: `0.000000`
- Posterior entropy: `0.573508`

## Top Scored Anchor+Clue Candidates

| name | selection_score | posterior_old_bce | posterior_refit_bce | robust_posterior | drift_v83 | max_drift_v83 | mean_Q1 | mean_S1 | mean_S2 | mean_S3 |
|---|---|---|---|---|---|---|---|---|---|---|
| anchor_v83_v85_soft_direction_w006 | 0.596626 | 0.595697 | 0.596408 | 0.596408 | 0.008221 | 0.092731 | 0.510126 | 0.682830 | 0.643157 | 0.658429 |
| anchor_v83_v85_soft_direction_w004 | 0.597445 | 0.596321 | 0.597445 | 0.597445 | 0.005487 | 0.060928 | 0.510207 | 0.682770 | 0.643419 | 0.658506 |
| anchor_v83_v85_soft_direction_w008 | 0.598260 | 0.595154 | 0.595452 | 0.595452 | 0.010945 | 0.125104 | 0.510044 | 0.682879 | 0.642889 | 0.658347 |
| anchor_v83_v85_soft_direction_w002 | 0.598564 | 0.597026 | 0.598564 | 0.598564 | 0.002747 | 0.029943 | 0.510288 | 0.682697 | 0.643675 | 0.658576 |
| anchor_v83_to_cl_sleep_prob_w002 | 0.599781 | 0.597753 | 0.599491 | 0.599491 | 0.001683 | 0.010836 | 0.510376 | 0.682599 | 0.643271 | 0.658355 |
| anchor_v83_cl_s1_only_w002 | 0.599782 | 0.597815 | 0.599780 | 0.599780 | 0.000147 | 0.004830 | 0.510368 | 0.682655 | 0.643925 | 0.658641 |
| anchor_v83_v83_minus_v76_w002 | 0.599793 | 0.597803 | 0.599793 | 0.599793 | 0.000370 | 0.002672 | 0.510366 | 0.682516 | 0.643799 | 0.658559 |
| anchor_v83_cl_q1_s1_w002 | 0.599798 | 0.597816 | 0.599784 | 0.599784 | 0.000339 | 0.005133 | 0.510392 | 0.682655 | 0.643925 | 0.658641 |
| anchor_v83_cl_s1_only_w004 | 0.599800 | 0.597818 | 0.599797 | 0.599797 | 0.000295 | 0.009686 | 0.510368 | 0.682695 | 0.643925 | 0.658641 |
| anchor_v83_cl_family_guarded_w002 | 0.599800 | 0.597821 | 0.599791 | 0.599791 | 0.000528 | 0.005133 | 0.510392 | 0.682655 | 0.643914 | 0.658641 |
| anchor_v83_to_cl_sleep_prob_w004 | 0.599816 | 0.597718 | 0.599244 | 0.599244 | 0.003366 | 0.021673 | 0.510383 | 0.682585 | 0.642616 | 0.658069 |
| anchor_v83_cl_s1_only_w006 | 0.599819 | 0.597822 | 0.599815 | 0.599815 | 0.000442 | 0.014565 | 0.510368 | 0.682733 | 0.643925 | 0.658641 |
| anchor_v83_v83_minus_v76_w004 | 0.599823 | 0.597794 | 0.599823 | 0.599823 | 0.000741 | 0.005333 | 0.510363 | 0.682420 | 0.643673 | 0.658477 |
| anchor_v83_cl_q1_s1_w004 | 0.599833 | 0.597822 | 0.599807 | 0.599807 | 0.000678 | 0.010271 | 0.510415 | 0.682695 | 0.643925 | 0.658641 |
| anchor_v83_s1_w004_q1s1_w002 | 0.599835 | 0.597823 | 0.599819 | 0.599819 | 0.000634 | 0.014565 | 0.510392 | 0.682733 | 0.643925 | 0.658641 |
| anchor_v83_cl_family_guarded_w004 | 0.599838 | 0.597833 | 0.599822 | 0.599822 | 0.001057 | 0.010271 | 0.510415 | 0.682695 | 0.643902 | 0.658641 |
| anchor_v83_cl_s1_only_w008 | 0.599839 | 0.597828 | 0.599834 | 0.599834 | 0.000590 | 0.019467 | 0.510368 | 0.682770 | 0.643925 | 0.658641 |
| anchor_v83_v83_minus_v76_w006 | 0.599855 | 0.597786 | 0.599855 | 0.599855 | 0.001110 | 0.007983 | 0.510361 | 0.682323 | 0.643547 | 0.658395 |
| anchor_v83_cl_s1_only_w010 | 0.599860 | 0.597834 | 0.599855 | 0.599855 | 0.000737 | 0.024391 | 0.510368 | 0.682804 | 0.643925 | 0.658641 |
| anchor_v83_to_cl_sleep_prob_w006 | 0.599869 | 0.597707 | 0.599023 | 0.599023 | 0.005049 | 0.032509 | 0.510390 | 0.682571 | 0.641962 | 0.657783 |
| anchor_v83_cl_q1_s1_w006 | 0.599870 | 0.597831 | 0.599833 | 0.599833 | 0.001017 | 0.015415 | 0.510439 | 0.682733 | 0.643925 | 0.658641 |
| anchor_v83_s1_w004_q1s1_w004 | 0.599872 | 0.597832 | 0.599844 | 0.599844 | 0.000973 | 0.019467 | 0.510415 | 0.682770 | 0.643925 | 0.658641 |
| anchor_v83_s1_w008_q1s1_w002 | 0.599876 | 0.597836 | 0.599859 | 0.599859 | 0.000929 | 0.024391 | 0.510392 | 0.682804 | 0.643925 | 0.658641 |
| anchor_v83_cl_family_guarded_w006 | 0.599879 | 0.597849 | 0.599857 | 0.599857 | 0.001585 | 0.015415 | 0.510439 | 0.682733 | 0.643890 | 0.658641 |
| anchor_v83_v83_minus_v76_w008 | 0.599887 | 0.597780 | 0.599887 | 0.599887 | 0.001479 | 0.010620 | 0.510359 | 0.682226 | 0.643420 | 0.658313 |

## Written Candidate Files

| file | selection_score | posterior_old_bce | posterior_refit_bce | drift_v83 | max_drift_v83 | mean_Q1 | mean_S1 | mean_S2 | mean_S3 |
|---|---|---|---|---|---|---|---|---|---|
| submission_cl_anchor_clue_v85_soft_direction_w006_prob.csv | 0.596626 | 0.595697 | 0.596408 | 0.008221 | 0.092731 | 0.510126 | 0.682830 | 0.643157 | 0.658429 |
| submission_cl_anchor_clue_cl_s1_only_w002_prob.csv | 0.599782 | 0.597815 | 0.599780 | 0.000147 | 0.004830 | 0.510368 | 0.682655 | 0.643925 | 0.658641 |
| submission_cl_anchor_clue_cl_q1_s1_w002_prob.csv | 0.599798 | 0.597816 | 0.599784 | 0.000339 | 0.005133 | 0.510392 | 0.682655 | 0.643925 | 0.658641 |

## 0.57 Verdict

- The refit posterior does not support a credible 0.57 candidate under bounded drift from v83. The best robust estimates remain near the v83/v76 band.
- The only positive new clue that survives when anchored to v83 is S1/Q1 centered sleep-boundary residual. It is worth probing, but it is not enough evidence for a guaranteed 0.57 jump.
- A 0.57 path requires new public feedback that confirms one of these residuals, or a new model that changes row ordering while preserving v83 means. Current evidence rejects broad CL sleep/CatBoost replacement.