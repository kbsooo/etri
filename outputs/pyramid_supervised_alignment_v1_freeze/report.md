# Pyramid supervised alignment

- Average log-loss: `0.625713`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Prior alpha: `10.0`
- Full model epochs: `2`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.672559 |
| Q2 | 0.706710 |
| Q3 | 0.670394 |
| S1 | 0.576919 |
| S2 | 0.575051 |
| S3 | 0.533685 |
| S4 | 0.644677 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 95 | 10 | 0.628489 |
| 2 | 92 | 13 | 0.604005 |
| 3 | 91 | 1 | 0.634469 |
| 4 | 87 | 2 | 0.618341 |
| 5 | 85 | 1 | 0.644282 |
