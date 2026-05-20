# v82 Q1/S3 decoder probe submission

- CSV: `outputs/submission_v82_q1_s3_decoder_probe/submission_v82_q1_s3_decoder_probe.csv`
- Construction: start from v80 late-behavior routed submission, replace only `Q1` and `S3` with v81 decoder-only routed predictions.
- Rationale: v81 stress test showed the most credible nested/fixed-shrinkage signal on Q1 and S3; other v81 target moves had higher router-selection-bias risk.
- Shape: `250 x 10`
- Probability range: `0.011738` to `0.997647`
- NaN count: `0`
- Mean absolute drift vs v80 all-target average: `0.008362`
- Max absolute drift vs v80: `0.113662`

## Drift vs v80

| target | mean_abs | mean_shift |
| --- | --- | --- |
| Q1 | 0.044317 | +0.040256 |
| Q2 | 0.000000 | +0.000000 |
| Q3 | 0.000000 | +0.000000 |
| S1 | 0.000000 | +0.000000 |
| S2 | 0.000000 | +0.000000 |
| S3 | 0.014215 | +0.008420 |
| S4 | 0.000000 | +0.000000 |

## OOF estimate from reports

- v80 report avg: `0.477600`
- v81 full routed report avg: `0.471378` but selection-biased.
- Q1/S3-only report-composed avg: `0.474006`
