# Supervised diffusion fine-tune

- Average log-loss: `0.628352`
- Auxiliary days in OOF folds: `train_sample`
- Init checkpoint: `outputs/diffusion_encoder/checkpoints/day_diffusion_encoder.pt`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.664184 |
| Q2 | 0.704723 |
| Q3 | 0.676444 |
| S1 | 0.586480 |
| S2 | 0.586606 |
| S3 | 0.538630 |
| S4 | 0.641400 |

## Fold scores

| fold | valid_rows | auxiliary_days | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- | --- |
| 1 | 95 | 605 | 57 | 0.624375 |
| 2 | 92 | 608 | 48 | 0.612569 |
| 3 | 91 | 609 | 41 | 0.640539 |
| 4 | 87 | 613 | 49 | 0.618304 |
| 5 | 85 | 615 | 23 | 0.647118 |