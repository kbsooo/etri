# One-shot 0.57 evidence hunt

This run searches existing model/data outputs as target-isolated residual moves on top of v83.
The score is not ordinary OOF; it is the robust max of old and refit public-feedback posterior BCE.
A credible 0.57 clue must get below `0.585` under this robust posterior while staying near v83.

## Baseline posterior scores

- v83_old_posterior: `0.597813`
- v83_refit_posterior: `0.599765`
- v83_robust: `0.599765`
- v76_old_posterior: `0.599963`
- v76_refit_posterior: `0.599963`
- v76_robust: `0.599963`
- source_pool_size: `169.000000`
- single_moves_scored: `82810.000000`
- beam_count: `160.000000`

## Best single target moves

| source_short | target | mode | mask | gamma | old_bce | refit_bce | robust | drift | max_drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| posterior_refit_values | Q3 | logit_blend | all | 0.160000 | 0.596659 | 0.596760 | 0.596760 | 0.003611 | 0.107076 |
| posterior_refit_values | Q3 | rank_logit | all | 0.160000 | 0.596810 | 0.596763 | 0.596810 | 0.004156 | 0.062024 |
| posterior_old_refit_avg | Q3 | rank_logit | all | 0.160000 | 0.596541 | 0.596824 | 0.596824 | 0.004198 | 0.067188 |
| posterior_refit_values | Q3 | rank_logit | all | 0.120000 | 0.596990 | 0.597442 | 0.597442 | 0.003130 | 0.046441 |
| posterior_refit_values | Q3 | logit_blend | all | 0.120000 | 0.596880 | 0.597444 | 0.597444 | 0.002731 | 0.083436 |
| posterior_old_refit_avg | Q3 | rank_logit | all | 0.120000 | 0.596787 | 0.597487 | 0.597487 | 0.003161 | 0.050362 |
| posterior_old_values | Q3 | rank_logit | all | 0.160000 | 0.596323 | 0.597546 | 0.597546 | 0.004208 | 0.068294 |
| submission_cl_anchor_clue_v85_soft_direction_w006_prob | Q3 | rank_logit | all | 0.160000 | 0.596579 | 0.597637 | 0.597637 | 0.004220 | 0.068848 |
| posterior_old_refit_avg | S1 | rank_logit | all | 0.160000 | 0.597706 | 0.597654 | 0.597706 | 0.003770 | 0.067698 |
| posterior_old_refit_avg | Q3 | logit_blend | all | 0.160000 | 0.596773 | 0.597762 | 0.597762 | 0.002418 | 0.066568 |
| posterior_refit_values | S1 | rank_logit | all | 0.160000 | 0.597817 | 0.597612 | 0.597817 | 0.003782 | 0.068296 |
| posterior_refit_values | Q3 | rank_logit | small_gap5 | 0.160000 | 0.597307 | 0.597975 | 0.597975 | 0.002562 | 0.062024 |
| posterior_refit_values | Q3 | logit_blend | small_gap5 | 0.160000 | 0.597210 | 0.597976 | 0.597976 | 0.002195 | 0.107076 |
| posterior_old_values | Q3 | rank_logit | all | 0.120000 | 0.596623 | 0.598028 | 0.598028 | 0.003165 | 0.051193 |
| posterior_old_refit_avg | Q3 | rank_logit | small_gap5 | 0.160000 | 0.597143 | 0.598044 | 0.598044 | 0.002603 | 0.062024 |
| posterior_refit_values | S1 | rank_logit | all | 0.120000 | 0.597751 | 0.598085 | 0.598085 | 0.002839 | 0.051289 |
| submission_cl_anchor_clue_v85_soft_direction_w006_prob | Q3 | rank_logit | all | 0.120000 | 0.596815 | 0.598096 | 0.598096 | 0.003176 | 0.051609 |
| posterior_old_refit_avg | S1 | rank_logit | all | 0.120000 | 0.597668 | 0.598117 | 0.598117 | 0.002829 | 0.050954 |
| posterior_refit_values | S2 | rank_logit | all | 0.160000 | 0.597511 | 0.598140 | 0.598140 | 0.003677 | 0.067223 |
| posterior_refit_values | Q3 | rank_logit | all | 0.080000 | 0.597217 | 0.598169 | 0.598169 | 0.002096 | 0.030890 |
| posterior_refit_values | Q3 | logit_blend | all | 0.080000 | 0.597146 | 0.598172 | 0.598172 | 0.001835 | 0.057685 |
| posterior_old_refit_avg | Q3 | rank_logit | all | 0.080000 | 0.597081 | 0.598198 | 0.598198 | 0.002115 | 0.033530 |
| posterior_refit_values | Q3 | rank_logit | inside_future | 0.160000 | 0.597605 | 0.598222 | 0.598222 | 0.002361 | 0.062024 |
| posterior_refit_values | Q2 | rank_logit | all | 0.160000 | 0.597446 | 0.598231 | 0.598231 | 0.004418 | 0.068328 |
| posterior_old_refit_avg | Q3 | logit_blend | all | 0.120000 | 0.597004 | 0.598233 | 0.598233 | 0.001822 | 0.050385 |
| posterior_old_refit_avg | S2 | rank_logit | all | 0.160000 | 0.597377 | 0.598239 | 0.598239 | 0.003692 | 0.067223 |
| posterior_refit_values | S1 | rank_logit | small_gap5 | 0.160000 | 0.597833 | 0.598290 | 0.598290 | 0.002484 | 0.068296 |
| posterior_refit_values | S4 | rank_logit | all | 0.160000 | 0.597229 | 0.598292 | 0.598292 | 0.004291 | 0.068275 |
| posterior_refit_values | S1 | logit_blend | all | 0.160000 | 0.597717 | 0.598296 | 0.598296 | 0.002256 | 0.054876 |
| posterior_old_refit_avg | Q2 | rank_logit | all | 0.160000 | 0.597296 | 0.598297 | 0.598297 | 0.004400 | 0.068172 |

## Beam-composed candidates

| name | old_bce | refit_bce | robust | drift_v83 | max_drift_v83 | n_moves | credible_under_0585 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beam_085 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_086 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_087 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_088 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_089 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_090 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_091 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_092 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_093 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_094 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_095 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_096 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_097 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_098 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_099 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_100 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_101 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_102 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_103 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_104 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_105 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_106 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_107 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_108 | 0.594833 | 0.594270 | 0.594833 | 0.014851 | 0.068294 | 5 | False |
| beam_073 | 0.594834 | 0.594270 | 0.594834 | 0.014850 | 0.068294 | 5 | False |

## Model/data-only beam candidates

| name | old_bce | refit_bce | robust | drift_v83 | max_drift_v83 | n_moves | credible_under_0585 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beam_073 | 0.594910 | 0.594906 | 0.594910 | 0.015577 | 0.068848 | 5 | False |
| beam_074 | 0.594910 | 0.594906 | 0.594910 | 0.015577 | 0.068848 | 5 | False |
| beam_077 | 0.594910 | 0.594902 | 0.594910 | 0.015579 | 0.068848 | 5 | False |
| beam_078 | 0.594910 | 0.594902 | 0.594910 | 0.015579 | 0.068848 | 5 | False |
| beam_080 | 0.594910 | 0.594902 | 0.594910 | 0.015579 | 0.068848 | 5 | False |
| beam_057 | 0.594915 | 0.594890 | 0.594915 | 0.015510 | 0.068848 | 5 | False |
| beam_058 | 0.594915 | 0.594890 | 0.594915 | 0.015510 | 0.068848 | 5 | False |
| beam_059 | 0.594915 | 0.594890 | 0.594915 | 0.015509 | 0.068848 | 5 | False |
| beam_060 | 0.594915 | 0.594890 | 0.594915 | 0.015509 | 0.068848 | 5 | False |
| beam_055 | 0.594915 | 0.594890 | 0.594915 | 0.015508 | 0.068848 | 5 | False |
| beam_056 | 0.594915 | 0.594890 | 0.594915 | 0.015508 | 0.068848 | 5 | False |
| beam_064 | 0.594917 | 0.594869 | 0.594917 | 0.015511 | 0.068848 | 5 | False |
| beam_065 | 0.594917 | 0.594869 | 0.594917 | 0.015511 | 0.068848 | 5 | False |
| beam_066 | 0.594917 | 0.594869 | 0.594917 | 0.015511 | 0.068848 | 5 | False |
| beam_067 | 0.594917 | 0.594869 | 0.594917 | 0.015511 | 0.068848 | 5 | False |
| beam_062 | 0.594917 | 0.594869 | 0.594917 | 0.015510 | 0.068848 | 5 | False |
| beam_063 | 0.594917 | 0.594869 | 0.594917 | 0.015510 | 0.068848 | 5 | False |
| beam_041 | 0.594917 | 0.594893 | 0.594917 | 0.015481 | 0.068848 | 5 | False |
| beam_042 | 0.594917 | 0.594893 | 0.594917 | 0.015481 | 0.068848 | 5 | False |
| beam_043 | 0.594917 | 0.594893 | 0.594917 | 0.015481 | 0.068848 | 5 | False |

## Written candidate files

| name | file | old_bce | refit_bce | robust | drift_v83 | max_drift_v83 | n_moves |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beam_001 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_001_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_002 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_002_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_003 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_003_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_004 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_004_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_005 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_005_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_006 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_006_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_007 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_007_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |
| beam_008 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_one_shot_evidence_hunt_beam_008_prob.csv | 0.594835 | 0.594273 | 0.594835 | 0.014823 | 0.068294 | 5 |

## Verdict

- No candidate crossed the credible-under-0.585 gate.
- The best available evidence remains a posterior-level 0.59x neighborhood improvement, not a 0.57 proof.
- This is negative evidence against the current data/model inventory containing a hidden one-shot 0.57 submission.
- The model/data-only beam also failed the 0.585 gate, so the best 0.59x beam depends on public-posterior directions rather than an independent newly discovered model signal.
- Direct S2 opportunity/Q-state remains a strong internal OOF clue, but when anchored safely to v83 it does not generate a large public-posterior jump.
- Large jumps still require either new public feedback to identify a split/row rule or a new independent signal that changes row ordering without importing v80/v85-style coordinate drift.
