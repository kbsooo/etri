# Target-wise latent portfolio

- Portfolio OOF: `0.575554`

## Target selection

| target | source | target_log_loss |
| --- | --- | --- |
| Q1 | dense_residual_v1 | 0.632599 |
| Q2 | dense_residual_v1 | 0.631156 |
| Q3 | dense_residual_v1 | 0.608870 |
| S1 | pls_residual_v2 | 0.551994 |
| S2 | pls_residual_v2 | 0.522732 |
| S3 | pls_residual_v2 | 0.495088 |
| S4 | dense_residual_v1 | 0.586442 |

## Source scores

| source | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | avg_log_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pls_residual_v2 | 0.632824 | 0.631581 | 0.609107 | 0.551994 | 0.522732 | 0.495088 | 0.586608 | 0.575705 |
| dense_residual_v1 | 0.632599 | 0.631156 | 0.608870 | 0.552357 | 0.523725 | 0.495089 | 0.586442 | 0.575748 |
| anchor | 0.632824 | 0.632493 | 0.609115 | 0.552471 | 0.524865 | 0.495089 | 0.586660 | 0.576217 |

## Blend scores

| name | oof_name | weight_portfolio | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_latent_portfolio_v1 | oof_targetwise_latent_portfolio_v1.csv | 1.000000 | 0.575554 | 0.632599 | 0.631156 | 0.608870 | 0.551994 | 0.522732 | 0.495088 | 0.586442 |
| submission_targetwise_latent_portfolio_w075_anchor_blend.csv | oof_targetwise_latent_portfolio_w075_anchor_blend.csv | 0.750000 | 0.575664 | 0.632615 | 0.631347 | 0.608892 | 0.552103 | 0.523122 | 0.495088 | 0.586482 |
| submission_targetwise_latent_portfolio_w050_anchor_blend.csv | oof_targetwise_latent_portfolio_w050_anchor_blend.csv | 0.500000 | 0.575811 | 0.632658 | 0.631634 | 0.608940 | 0.552219 | 0.523609 | 0.495088 | 0.586531 |
| submission_targetwise_latent_portfolio_w025_anchor_blend.csv | oof_targetwise_latent_portfolio_w025_anchor_blend.csv | 0.250000 | 0.575996 | 0.632727 | 0.632016 | 0.609014 | 0.552342 | 0.524190 | 0.495088 | 0.586591 |
| anchor_public_feedback | outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv | 0.000000 | 0.576217 | 0.632824 | 0.632493 | 0.609115 | 0.552471 | 0.524865 | 0.495089 | 0.586660 |
