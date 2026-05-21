# Nested Pruned State Decoder

Target-specific feature-family candidates are selected inside each outer fold, then scored on held-out rows.

- Nested target-wise OOF avg: `0.624729`
- Drift vs v83 diagnostic reference: `0.066660`

## Per-target OOF

| avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.624729 | 0.670340 | 0.685659 | 0.672727 | 0.576165 | 0.585703 | 0.537058 | 0.645454 |

## Selection Counts

| target | selected | outer_count |
| --- | --- | --- |
| Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 3 |
| Q1 | no_raw__prior_logit_blend_hgb_w10 | 1 |
| Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 1 |
| Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 4 |
| Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 1 |
| Q3 | no_sleep__prior_logit_blend_hgb_w35 | 2 |
| Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 2 |
| Q3 | no_rank__prior_logit_blend_hgb_w10 | 1 |
| S1 | only_rhythm__prior_logit_blend_hgb_w20 | 3 |
| S1 | no_derivative__prior_logit_blend_hgb_w10 | 1 |
| S1 | only_cross_modal__prior_logit_blend_residual_ridge_w05 | 1 |
| S2 | no_missingness__prior_logit_blend_residual_ridge_w05 | 2 |
| S2 | subject_prior__subject_prior | 2 |
| S2 | only_rhythm__prior_logit_blend_hgb_w20 | 1 |
| S3 | subject_prior__subject_prior | 3 |
| S3 | only_missingness__prior_logit_blend_rank_pairwise_w05 | 2 |
| S4 | no_temporal_delta__prior_logit_blend_hgb_w20 | 2 |
| S4 | only_cross_modal__prior_logit_blend_hgb_w10 | 2 |
| S4 | no_derivative__prior_logit_blend_hgb_w20 | 1 |

## Inner Candidate Scores

| outer_fold | target | candidate | inner_log_loss |
| --- | --- | --- | --- |
| 0 | Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 0.675724 |
| 0 | Q1 | subject_prior__subject_prior | 0.678347 |
| 0 | Q1 | no_raw__prior_logit_blend_hgb_w10 | 0.678538 |
| 0 | Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.683406 |
| 0 | Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.685374 |
| 1 | Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.673959 |
| 1 | Q1 | subject_prior__subject_prior | 0.678340 |
| 1 | Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 0.678445 |
| 1 | Q1 | no_raw__prior_logit_blend_hgb_w10 | 0.679316 |
| 1 | Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.692401 |
| 2 | Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.669682 |
| 2 | Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 0.673434 |
| 2 | Q1 | subject_prior__subject_prior | 0.673652 |
| 2 | Q1 | no_raw__prior_logit_blend_hgb_w10 | 0.673767 |
| 2 | Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.694179 |
| 3 | Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.676493 |
| 3 | Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 0.677275 |
| 3 | Q1 | no_raw__prior_logit_blend_hgb_w10 | 0.677555 |
| 3 | Q1 | subject_prior__subject_prior | 0.678205 |
| 3 | Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.682541 |
| 4 | Q1 | no_raw__prior_logit_blend_hgb_w10 | 0.674657 |
| 4 | Q1 | subject_prior__subject_prior | 0.674800 |
| 4 | Q1 | no_temporal_delta__prior_logit_blend_hgb_w10 | 0.674908 |
| 4 | Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.676556 |
| 4 | Q1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.680291 |
| 0 | Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.692720 |
| 0 | Q2 | subject_prior__subject_prior | 0.694916 |
| 0 | Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 0.695929 |
| 0 | Q2 | no_derivative__prior_logit_blend_hgb_w10 | 0.696178 |
| 0 | Q2 | no_ratio__prior_logit_blend_residual_ridge_w03 | 0.696408 |
| 1 | Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.717965 |
| 1 | Q2 | no_ratio__prior_logit_blend_residual_ridge_w03 | 0.727094 |
| 1 | Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 0.731007 |
| 1 | Q2 | subject_prior__subject_prior | 0.733571 |
| 1 | Q2 | no_derivative__prior_logit_blend_hgb_w10 | 0.735832 |
| 2 | Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.674002 |
| 2 | Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 0.680532 |
| 2 | Q2 | no_derivative__prior_logit_blend_hgb_w10 | 0.682516 |
| 2 | Q2 | no_ratio__prior_logit_blend_residual_ridge_w03 | 0.682675 |
| 2 | Q2 | subject_prior__subject_prior | 0.685157 |
| 3 | Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.703805 |
| 3 | Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 0.704953 |
| 3 | Q2 | no_derivative__prior_logit_blend_hgb_w10 | 0.712238 |
| 3 | Q2 | no_ratio__prior_logit_blend_residual_ridge_w03 | 0.717859 |
| 3 | Q2 | subject_prior__subject_prior | 0.722645 |
| 4 | Q2 | only_rhythm__prior_logit_blend_hgb_w20 | 0.710894 |
| 4 | Q2 | no_derivative__prior_logit_blend_hgb_w10 | 0.713365 |
| 4 | Q2 | subject_prior__subject_prior | 0.713907 |
| 4 | Q2 | no_ratio__prior_logit_blend_residual_ridge_w03 | 0.716837 |
| 4 | Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.719628 |
| 0 | Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 0.675725 |
| 0 | Q3 | no_derivative__prior_logit_blend_hgb_w10 | 0.677035 |
| 0 | Q3 | no_rank__prior_logit_blend_hgb_w10 | 0.679989 |
| 0 | Q3 | subject_prior__subject_prior | 0.680313 |
| 0 | Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.687149 |
| 1 | Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.666505 |
| 1 | Q3 | no_rank__prior_logit_blend_hgb_w10 | 0.667409 |
| 1 | Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 0.667827 |
| 1 | Q3 | subject_prior__subject_prior | 0.670923 |
| 1 | Q3 | no_derivative__prior_logit_blend_hgb_w10 | 0.671076 |
| 2 | Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.680920 |
| 2 | Q3 | no_derivative__prior_logit_blend_hgb_w10 | 0.681168 |
| 2 | Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 0.683559 |
| 2 | Q3 | subject_prior__subject_prior | 0.683578 |
| 2 | Q3 | no_rank__prior_logit_blend_hgb_w10 | 0.684078 |
| 3 | Q3 | no_rank__prior_logit_blend_hgb_w10 | 0.693815 |
| 3 | Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.694816 |
| 3 | Q3 | no_derivative__prior_logit_blend_hgb_w10 | 0.695304 |
| 3 | Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 0.696114 |
| 3 | Q3 | subject_prior__subject_prior | 0.698117 |
| 4 | Q3 | only_rhythm__prior_logit_blend_state_mean_w10 | 0.665007 |
| 4 | Q3 | no_rank__prior_logit_blend_hgb_w10 | 0.667180 |
| 4 | Q3 | subject_prior__subject_prior | 0.668132 |
| 4 | Q3 | no_derivative__prior_logit_blend_hgb_w10 | 0.671088 |
| 4 | Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.678830 |
| 0 | S1 | only_rhythm__prior_logit_blend_hgb_w20 | 0.577734 |
| 0 | S1 | subject_prior__subject_prior | 0.581280 |
| 0 | S1 | no_derivative__prior_logit_blend_hgb_w10 | 0.581862 |
| 0 | S1 | only_cross_modal__prior_logit_blend_residual_ridge_w05 | 0.582062 |
| 0 | S1 | only_rhythm__prior_logit_blend_rank_pairwise_w05 | 0.592556 |
