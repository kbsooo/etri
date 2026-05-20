# Pyramid supervised alignment

- Average log-loss: `0.644260`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Prior alpha: `10.0`
- Full model epochs: `1`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.658883 |
| Q2 | 0.741386 |
| Q3 | 0.703061 |
| S1 | 0.591495 |
| S2 | 0.614425 |
| S3 | 0.541372 |
| S4 | 0.659199 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 228 | 1 | 0.637979 |
| 2 | 222 | 1 | 0.650710 |
