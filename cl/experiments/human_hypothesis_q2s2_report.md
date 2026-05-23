# Human-hypothesis Q2/S2 features, no submission

Generated feature table: `features/human_hypothesis_q2s2_features_v1.parquet`

Evaluation files:
- `experiments/human_hypothesis_q2s2_eval_results.csv`
- `experiments/human_hypothesis_q2s2_eval_summary.csv`

## Coarse takeaway
This experiment tests human-behavior hypotheses, not a submission. Treat only split-consistent, mechanism-consistent effects as real; ignore tiny third-decimal differences.

## Q2
### testpattern
   subset       k      C  logloss   delta    auc
 human_q2 15.0000 0.0100   0.6811 -0.0522 0.5703
 human_q2 30.0000 0.0030   0.6817 -0.0516 0.5667
human_all 15.0000 0.0100   0.6821 -0.0512 0.5653
 human_q2  8.0000 0.0100   0.6823 -0.0510 0.5580
human_all  8.0000 0.0100   0.6824 -0.0510 0.5571

### random_gap
                subset        k      C  logloss   delta    auc
              human_q2 120.0000 0.0300   0.6596 -0.0311 0.6462
              human_q2 120.0000 0.0100   0.6600 -0.0308 0.6336
             human_all  60.0000 0.0100   0.6610 -0.0298 0.6262
             human_all  60.0000 0.0300   0.6616 -0.0291 0.6314
q2_existing_plus_human 120.0000 0.0030   0.6617 -0.0291 0.6481

### tail
                subset       k      C  logloss  delta    auc
     existing_base_cfg     NaN    NaN   0.6581 0.0000 0.6266
  q2_existing_day_flat 30.0000 0.0030   0.6582 0.0002 0.6296
q2_existing_plus_human 60.0000 0.0030   0.6592 0.0012 0.5977
  q2_existing_day_flat 15.0000 0.0100   0.6595 0.0014 0.6281
  q2_existing_day_flat 30.0000 0.0100   0.6596 0.0015 0.6257

## S2
### testpattern
                    subset       k      C  logloss   delta    auc
s2_existing_no_flat_hourly 60.0000 0.0030   0.5922 -0.0365 0.7120
    s2_existing_plus_human 60.0000 0.0030   0.5932 -0.0355 0.7103
s2_existing_no_flat_hourly 15.0000 0.0300   0.5984 -0.0303 0.7048
s2_existing_no_flat_hourly  8.0000 0.1000   0.5987 -0.0300 0.7041
    s2_existing_plus_human  8.0000 0.1000   0.5987 -0.0300 0.7041

### random_gap
                    subset       k      C  logloss   delta    auc
    s2_existing_plus_human 15.0000 0.0300   0.5635 -0.0278 0.7358
s2_existing_no_flat_hourly 15.0000 0.0300   0.5635 -0.0278 0.7358
    s2_existing_plus_human 15.0000 0.1000   0.5639 -0.0274 0.7341
s2_existing_no_flat_hourly 15.0000 0.1000   0.5639 -0.0274 0.7341
    s2_existing_plus_human  8.0000 0.1000   0.5692 -0.0221 0.7358

### tail
                    subset       k      C  logloss   delta    auc
s2_existing_no_flat_hourly 30.0000 0.0030   0.5855 -0.0250 0.7116
    s2_existing_plus_human 30.0000 0.0030   0.5867 -0.0238 0.7107
    s2_existing_plus_human 60.0000 0.0030   0.5890 -0.0216 0.7080
s2_existing_no_flat_hourly 60.0000 0.0030   0.5902 -0.0204 0.7125
    s2_existing_plus_human 30.0000 0.0100   0.5976 -0.0129 0.7073
