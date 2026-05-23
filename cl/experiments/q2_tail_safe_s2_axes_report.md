# Q2 tail-safe / S2 routine-axes further experiments

No submission files were created.

## Q2
### testpattern
               subset  model       k      C  logloss   delta    auc
q2_tail_safe_longterm logreg 60.0000 0.0300   0.6807 -0.0493 0.5774
q2_tail_safe_longterm logreg 15.0000 0.0100   0.6809 -0.0492 0.5519
q2_tail_safe_longterm logreg 60.0000 0.0100   0.6810 -0.0491 0.5568
q2_tail_safe_longterm logreg  8.0000 0.0100   0.6811 -0.0490 0.5528
q2_tail_safe_longterm logreg 30.0000 0.0030   0.6825 -0.0475 0.5434
q2_tail_safe_longterm logreg 15.0000 0.0030   0.6826 -0.0475 0.5524
q2_tail_safe_longterm logreg 30.0000 0.0100   0.6827 -0.0473 0.5466
q2_tail_safe_longterm logreg  8.0000 0.0300   0.6828 -0.0473 0.5536

### random_gap
               subset  model       k      C  logloss   delta    auc
q2_tail_safe_longterm logreg 60.0000 0.1000   0.6347 -0.0663 0.6803
q2_tail_safe_longterm logreg 60.0000 0.0300   0.6462 -0.0548 0.6511
q2_tail_safe_longterm logreg 30.0000 0.1000   0.6548 -0.0462 0.6258
q2_tail_safe_longterm logreg 60.0000 0.0100   0.6575 -0.0435 0.6235
q2_tail_safe_longterm logreg 30.0000 0.0300   0.6587 -0.0423 0.6120
q2_tail_safe_longterm logreg 30.0000 0.0100   0.6631 -0.0379 0.6018
q2_tail_safe_longterm logreg 15.0000 0.0300   0.6632 -0.0379 0.6058
q2_tail_safe_longterm logreg 15.0000 0.1000   0.6633 -0.0377 0.6107

### tail
                    subset   model       k      C  logloss   delta    auc
q2_day_flat_plus_tail_safe  logreg 60.0000 0.0030   0.6578 -0.0037 0.6058
         existing_base_cfg basecfg     NaN    NaN   0.6616  0.0000 0.6239
      q2_existing_day_flat  logreg 15.0000 0.0030   0.6628  0.0012 0.6060
      q2_existing_day_flat  logreg 30.0000 0.0030   0.6628  0.0012 0.6174
      q2_existing_day_flat  logreg  8.0000 0.0030   0.6647  0.0031 0.5786
      q2_existing_day_flat  logreg  8.0000 0.0100   0.6656  0.0040 0.5823
      q2_existing_day_flat  logreg 15.0000 0.0100   0.6659  0.0043 0.6034
q2_day_flat_plus_tail_safe  logreg 30.0000 0.0030   0.6681  0.0065 0.5242

### robust coarse ranking across split groups
               subset  model       k      C  mean_delta  worst_delta
q2_tail_safe_longterm logreg  8.0000 0.0100     -0.0174       0.0290
q2_tail_safe_longterm logreg  5.0000 0.0100     -0.0172       0.0244
q2_tail_safe_longterm logreg 30.0000 0.0030     -0.0170       0.0264
q2_tail_safe_longterm logreg 15.0000 0.0030     -0.0166       0.0254
q2_tail_safe_longterm logreg 15.0000 0.0100     -0.0158       0.0371
q2_tail_safe_longterm logreg  5.0000 0.0300     -0.0158       0.0324
q2_compact_hypotheses logreg  5.0000 0.1000     -0.0156       0.0084
q2_tail_safe_longterm logreg 60.0000 0.0030     -0.0156       0.0326
q2_tail_safe_longterm logreg  8.0000 0.0030     -0.0150       0.0244
q2_compact_hypotheses logreg  5.0000 0.0300     -0.0148       0.0128
q2_compact_hypotheses logreg  8.0000 0.1000     -0.0146       0.0090
q2_compact_hypotheses logreg  8.0000 0.0300     -0.0143       0.0132

## S2
### testpattern
                    subset  model       k      C  logloss   delta    auc
s2_existing_no_flat_hourly logreg  8.0000 0.1000   0.5951 -0.0250 0.7074
     s2_existing_plus_axes logreg  8.0000 0.1000   0.5951 -0.0250 0.7074
s2_existing_no_flat_hourly logreg 15.0000 0.0300   0.5962 -0.0239 0.7087
     s2_existing_plus_axes logreg 15.0000 0.0300   0.5962 -0.0239 0.7087
s2_existing_no_flat_hourly logreg 15.0000 0.1000   0.5995 -0.0206 0.7071
     s2_existing_plus_axes logreg 15.0000 0.1000   0.5995 -0.0206 0.7071
     s2_existing_plus_axes logreg 60.0000 0.0030   0.5996 -0.0205 0.7094
s2_existing_no_flat_hourly logreg 60.0000 0.0030   0.5996 -0.0205 0.7094

### random_gap
                    subset  model       k      C  logloss   delta    auc
s2_existing_no_flat_hourly logreg 30.0000 0.0100   0.5736 -0.0143 0.7364
     s2_existing_plus_axes logreg 30.0000 0.0100   0.5736 -0.0143 0.7364
s2_existing_no_flat_hourly logreg 30.0000 0.0300   0.5741 -0.0137 0.7338
     s2_existing_plus_axes logreg 30.0000 0.0300   0.5741 -0.0137 0.7338
s2_existing_no_flat_hourly logreg 15.0000 0.0300   0.5749 -0.0129 0.7303
     s2_existing_plus_axes logreg 15.0000 0.0300   0.5749 -0.0129 0.7303
     s2_existing_plus_axes logreg 15.0000 0.1000   0.5764 -0.0114 0.7271
s2_existing_no_flat_hourly logreg 15.0000 0.1000   0.5764 -0.0114 0.7271

### tail
                    subset   model       k      C  logloss   delta    auc
     s2_existing_plus_axes  logreg 30.0000 0.0030   0.5849 -0.0166 0.7133
s2_existing_no_flat_hourly  logreg 30.0000 0.0030   0.5849 -0.0166 0.7133
     s2_existing_plus_axes  logreg 30.0000 0.0100   0.5987 -0.0028 0.7142
s2_existing_no_flat_hourly  logreg 30.0000 0.0100   0.5987 -0.0028 0.7142
         existing_base_cfg basecfg     NaN    NaN   0.6015  0.0000 0.6948
     s2_existing_plus_axes  logreg 60.0000 0.0030   0.6044  0.0029 0.6947
s2_existing_no_flat_hourly  logreg 60.0000 0.0030   0.6044  0.0029 0.6947
     s2_existing_plus_axes  logreg 30.0000 0.0300   0.6186  0.0171 0.7013

### robust coarse ranking across split groups
                    subset   model       k      C  mean_delta  worst_delta
s2_existing_no_flat_hourly  logreg 30.0000 0.0030     -0.0131      -0.0096
     s2_existing_plus_axes  logreg 30.0000 0.0030     -0.0131      -0.0096
s2_existing_no_flat_hourly  logreg 30.0000 0.0100     -0.0114      -0.0028
     s2_existing_plus_axes  logreg 30.0000 0.0100     -0.0114      -0.0028
s2_existing_no_flat_hourly  logreg 60.0000 0.0030     -0.0077       0.0029
     s2_existing_plus_axes  logreg 60.0000 0.0030     -0.0077       0.0029
s2_existing_no_flat_hourly  logreg 30.0000 0.0300     -0.0030       0.0171
     s2_existing_plus_axes  logreg 30.0000 0.0300     -0.0030       0.0171
         existing_base_cfg basecfg     NaN    NaN      0.0000       0.0000
s2_existing_no_flat_hourly  logreg 15.0000 0.0300      0.0011       0.0403
     s2_existing_plus_axes  logreg 15.0000 0.0300      0.0011       0.0403
s2_existing_no_flat_hourly  logreg 60.0000 0.0100      0.0016       0.0271
