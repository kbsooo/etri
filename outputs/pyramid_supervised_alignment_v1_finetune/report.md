# Pyramid supervised alignment

- Average log-loss: `0.624731`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Prior alpha: `10.0`
- Full model epochs: `2`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.676283 |
| Q2 | 0.697101 |
| Q3 | 0.671384 |
| S1 | 0.575733 |
| S2 | 0.575749 |
| S3 | 0.533611 |
| S4 | 0.643255 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 95 | 26 | 0.625714 |
| 2 | 92 | 16 | 0.605339 |
| 3 | 91 | 1 | 0.632732 |
| 4 | 87 | 2 | 0.618383 |
| 5 | 85 | 1 | 0.642552 |
