# Supervised diffusion fine-tune

- Average log-loss: `0.703087`
- Auxiliary days in OOF folds: `train_sample`
- Init checkpoint: `outputs/diffusion_encoder/checkpoints/day_diffusion_encoder.pt`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.730241 |
| Q2 | 0.717130 |
| Q3 | 0.751729 |
| S1 | 0.667022 |
| S2 | 0.668727 |
| S3 | 0.670306 |
| S4 | 0.716453 |

## Fold scores

| fold | valid_rows | auxiliary_days | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- | --- |
| 1 | 228 | 472 | 1 | 0.696453 |
| 2 | 222 | 478 | 1 | 0.709900 |