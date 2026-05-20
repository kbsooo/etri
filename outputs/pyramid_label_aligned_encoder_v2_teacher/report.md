# Pyramid label-aligned encoder

- Average log-loss: `0.624964`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Teacher OOF: `outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv`
- Teacher submission: `outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv`
- Full model epochs: `22`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.672726 |
| Q2 | 0.701697 |
| Q3 | 0.671691 |
| S1 | 0.577184 |
| S2 | 0.573551 |
| S3 | 0.534073 |
| S4 | 0.643828 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 95 | 30 | 0.629166 |
| 2 | 92 | 43 | 0.606107 |
| 3 | 91 | 1 | 0.633025 |
| 4 | 87 | 5 | 0.617258 |
| 5 | 85 | 22 | 0.639936 |
