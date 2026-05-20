# Pyramid label-aligned encoder

- Average log-loss: `0.644041`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Teacher OOF: `outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv`
- Teacher submission: `outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv`
- Full model epochs: `1`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.658825 |
| Q2 | 0.740828 |
| Q3 | 0.702418 |
| S1 | 0.591456 |
| S2 | 0.613988 |
| S3 | 0.541334 |
| S4 | 0.659436 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 228 | 1 | 0.637696 |
| 2 | 222 | 1 | 0.650556 |
