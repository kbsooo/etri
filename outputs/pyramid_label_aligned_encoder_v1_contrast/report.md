# Pyramid label-aligned encoder

- Average log-loss: `0.624656`
- Init checkpoint: `outputs/encoder_day_pyramid_ssl_v1/checkpoints/best_pyramid_encoder.pt`
- Teacher OOF: ``
- Teacher submission: ``
- Full model epochs: `7`

## Target scores

| target | log_loss |
| --- | --- |
| Q1 | 0.671430 |
| Q2 | 0.699490 |
| Q3 | 0.671458 |
| S1 | 0.575904 |
| S2 | 0.576187 |
| S3 | 0.533263 |
| S4 | 0.644856 |

## Fold scores

| fold | valid_rows | best_epoch | final_val_avg_log_loss |
| --- | --- | --- | --- |
| 1 | 95 | 21 | 0.627373 |
| 2 | 92 | 38 | 0.605461 |
| 3 | 91 | 1 | 0.632740 |
| 4 | 87 | 4 | 0.616860 |
| 5 | 85 | 7 | 0.641718 |
