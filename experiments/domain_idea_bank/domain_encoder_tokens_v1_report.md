# Domain Encoder Tokens v1

## Purpose

Create an encoder-first value/mask tensor from the 30-minute lifelog grid. This is the shared input for Transformer/Diffusion/SSL experiments and does not use labels.

## Tensor

- Artifact: `artifacts/domain_encoder_tokens_v1.npz`
- Shape values/mask: `[days=700, channels=110, tokens=48]`
- Observed fraction: `0.886050`
- Date range: `2024-06-03..2024-11-19`

## Channel Groups

| group | channels |
| --- | ---: |
| ambience | 8 |
| body | 31 |
| cross_modal | 2 |
| event | 11 |
| gps_radio | 18 |
| light | 6 |
| missingness | 21 |
| phone | 13 |

## Encoder-First Contract

- `values` contains standardized sensor/event values.
- `mask` explicitly distinguishes observed values from imputed cells.
- `channel_groups` allows family ablation without touching label data.
- Label probes must be separate downstream diagnostics, not part of token construction.