# Nested Extended Family Decoder

Nested validation of extended family-pruning target candidates. Inner folds select source; outer folds score it.

## Score

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.625206 | 0.670704 | 0.700048 | 0.671970 | 0.574937 | 0.577659 | 0.538350 | 0.642770 | 0.065883 | 0.882567 |

## Selection Counts

| target | selected | count |
| --- | --- | --- |
| Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 4 |
| Q1 | drop_ratio_temporal_delta__prior_logit_blend_hgb_w20 | 1 |
| Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 2 |
| Q2 | drop_raw_ratio__prior_logit_blend_hgb_w35 | 1 |
| Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 1 |
| Q2 | subject_prior__subject_prior | 1 |
| Q3 | drop_sleep_late__prior_logit_blend_hgb_w35 | 2 |
| Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 2 |
| Q3 | subject_prior__subject_prior | 1 |
| S1 | subject_prior__subject_prior | 3 |
| S1 | only_rhythm__prior_logit_blend_hgb_w20 | 2 |
| S2 | no_missingness__prior_logit_blend_residual_ridge_w05 | 2 |
| S2 | subject_prior__subject_prior | 2 |
| S2 | only_rhythm__prior_logit_blend_hgb_w20 | 1 |
| S3 | subject_prior__subject_prior | 3 |
| S3 | drop_ratio_temporal_delta__prior_logit_blend_hgb_w20 | 1 |
| S3 | only_missingness__prior_logit_blend_rank_pairwise_w05 | 1 |
| S4 | no_temporal_delta__prior_logit_blend_hgb_w20 | 3 |
| S4 | only_cross_modal__prior_logit_blend_hgb_w10 | 1 |
| S4 | subject_prior__subject_prior | 1 |
