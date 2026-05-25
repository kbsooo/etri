# CoLa-inspired denoising latent signal hunt

No submission files were created. Negative delta means the continuous denoising latent helped over a subject/day anchor.

## Setup

- n_days: `700`
- n_input_features: `451`
- zdim: `8`
- best_recon_mse: `0.47738775610923767`

## Target-level delta: anchor+CoLa latent minus anchor

| target   |    mean |   median |     min |    max |   count |
|:---------|--------:|---------:|--------:|-------:|--------:|
| Q1       |  0.0123 |   0.0041 | -0.0006 | 0.0368 |       7 |
| Q2       |  0.0139 |   0.0083 | -0.0247 | 0.0530 |       7 |
| Q3       |  0.0219 |   0.0261 |  0.0036 | 0.0407 |       7 |
| S1       |  0.0149 |   0.0158 |  0.0087 | 0.0221 |       7 |
| S2       |  0.0021 |   0.0059 | -0.0269 | 0.0227 |       7 |
| S3       |  0.0319 |   0.0379 | -0.0012 | 0.0522 |       7 |
| S4       | -0.0039 |  -0.0079 | -0.0258 | 0.0131 |       7 |

## Split-level deltas

| target   | split          |   delta_cola_minus_anchor |
|:---------|:---------------|--------------------------:|
| Q1       | chrono_last_20 |                    0.0225 |
| Q1       | chrono_last_25 |                    0.0236 |
| Q1       | chrono_last_30 |                    0.0368 |
| Q1       | pattern_0      |                    0.0004 |
| Q1       | pattern_2      |                    0.0041 |
| Q1       | pattern_4      |                   -0.0004 |
| Q1       | tail           |                   -0.0006 |
| Q2       | chrono_last_20 |                    0.0285 |
| Q2       | chrono_last_25 |                    0.0328 |
| Q2       | chrono_last_30 |                    0.0530 |
| Q2       | pattern_0      |                   -0.0012 |
| Q2       | pattern_2      |                   -0.0247 |
| Q2       | pattern_4      |                    0.0007 |
| Q2       | tail           |                    0.0083 |
| Q3       | chrono_last_20 |                    0.0261 |
| Q3       | chrono_last_25 |                    0.0262 |
| Q3       | chrono_last_30 |                    0.0292 |
| Q3       | pattern_0      |                    0.0230 |
| Q3       | pattern_2      |                    0.0043 |
| Q3       | pattern_4      |                    0.0036 |
| Q3       | tail           |                    0.0407 |
| S1       | chrono_last_20 |                    0.0221 |
| S1       | chrono_last_25 |                    0.0158 |
| S1       | chrono_last_30 |                    0.0165 |
| S1       | pattern_0      |                    0.0087 |
| S1       | pattern_2      |                    0.0120 |
| S1       | pattern_4      |                    0.0138 |
| S1       | tail           |                    0.0158 |
| S2       | chrono_last_20 |                    0.0059 |
| S2       | chrono_last_25 |                    0.0049 |
| S2       | chrono_last_30 |                    0.0081 |
| S2       | pattern_0      |                   -0.0269 |
| S2       | pattern_2      |                    0.0067 |
| S2       | pattern_4      |                   -0.0065 |
| S2       | tail           |                    0.0227 |
| S3       | chrono_last_20 |                    0.0522 |
| S3       | chrono_last_25 |                    0.0415 |
| S3       | chrono_last_30 |                    0.0379 |
| S3       | pattern_0      |                   -0.0012 |
| S3       | pattern_2      |                    0.0099 |
| S3       | pattern_4      |                    0.0313 |
| S3       | tail           |                    0.0516 |
| S4       | chrono_last_20 |                   -0.0096 |
| S4       | chrono_last_25 |                   -0.0110 |
| S4       | chrono_last_30 |                    0.0086 |
| S4       | pattern_0      |                   -0.0258 |
| S4       | pattern_2      |                    0.0131 |
| S4       | pattern_4      |                   -0.0079 |
| S4       | tail           |                    0.0054 |

## Subject-local latent nearest-neighbor label purity

| target   |   nn_acc |   subject_majority_acc |    lift |
|:---------|---------:|-----------------------:|--------:|
| Q1       |   0.6154 |                 0.6107 |  0.0047 |
| Q2       |   0.5468 |                 0.6129 | -0.0661 |
| Q3       |   0.5557 |                 0.6257 | -0.0699 |
| S1       |   0.6534 |                 0.6968 | -0.0433 |
| S2       |   0.6684 |                 0.7124 | -0.0440 |
| S3       |   0.6757 |                 0.7310 | -0.0553 |
| S4       |   0.6055 |                 0.6454 | -0.0399 |

## Interpretation

- Potentially useful targets by mean delta < -0.003: `['S4']`
- Likely unsafe/noisy targets by mean delta > +0.003: `['Q1', 'Q2', 'Q3', 'S1', 'S3']`
- Treat this as a microscope. A full diffusion sampler is not justified unless these latent/anomaly features show stable target-local signal.
- If signal exists, next step is not immediate submission; inspect row-level high-shift cases against `test_regime_map.csv` and public-LB constraints.