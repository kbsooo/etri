# Pyramid Encoder Training Report

- device: `mps`
- temporal pairs: `2740`
- best loss: `1.825553`
- final loss: `1.825553`
- latent path: `outputs/encoder_day_pyramid_ssl_smoke/day_latents.parquet`

## Objectives

- Masked reconstruction of actual 5-minute sensor channels.
- Masked reconstruction of actual-minus-normal-day-twin deviation channels.
- Same-subject neighboring-day contrastive learning.
- Robustness through slot/channel/event/prototype corruption.
