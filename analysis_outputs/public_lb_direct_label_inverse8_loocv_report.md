# Direct Label Inverse7 Leave-One-Anchor CV

This checks whether soft-label inverse solutions selected on five public anchors predict the sixth public anchor.

## Overall Policy Error

```
              policy  heldout_abs_error  heldout_signed_error  top_solution_score
        oracle_best1           0.000317              0.000098            0.000541
         train_best1           0.000521              0.000200            0.000339
    train_best5_mean           0.000773              0.000366            0.000339
   train_best12_mean           0.000845              0.000462            0.000339
    structured_best1           0.000881              0.000461            0.000364
nonrandom_best5_mean           0.000933              0.000524            0.000364
```

## Per-Anchor Policy Error

```
      heldout_key               policy  heldout_abs_error  heldout_signed_error  heldout_public_pred  heldout_public_actual      top_mask_kind   top_mask_name top_prior_name
        anchor578 nonrandom_best5_mean       3.153175e-03          3.153175e-03             0.581581               0.578427 subject_contiguous frac0.25_rep150           a2c8
        anchor578         oracle_best1       1.302617e-03          1.302617e-03             0.579730               0.578427 subject_contiguous frac0.40_rep052   entropy_g075
        anchor578     structured_best1       3.220964e-03          3.220964e-03             0.581648               0.578427 subject_contiguous frac0.25_rep150           a2c8
        anchor578          train_best1       1.573751e-03          1.573751e-03             0.580001               0.578427        random_rows frac0.40_rep009   entropy_g075
        anchor578    train_best12_mean       2.835957e-03          2.835957e-03             0.581263               0.578427        random_rows frac0.40_rep009   entropy_g075
        anchor578     train_best5_mean       2.496540e-03          2.496540e-03             0.580924               0.578427        random_rows frac0.40_rep009   entropy_g075
      cvjepa_a2c8 nonrandom_best5_mean       1.371920e-04         -1.371920e-04             0.577302               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8         oracle_best1       3.326200e-05         -3.326200e-05             0.577406               0.577439 subject_contiguous frac0.25_rep099          raw05
      cvjepa_a2c8     structured_best1       1.461670e-04         -1.461670e-04             0.577293               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8          train_best1       1.461670e-04         -1.461670e-04             0.577293               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8    train_best12_mean       1.291830e-04         -1.291830e-04             0.577310               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8     train_best5_mean       1.322480e-04         -1.322480e-04             0.577307               0.577439       global_order    rowmod4_rem3   entropy_g075
      jepa_bad_q2 nonrandom_best5_mean       7.719090e-04          7.719090e-04             0.580573               0.579801 subject_contiguous frac0.40_rep052   entropy_g075
      jepa_bad_q2         oracle_best1       4.563300e-05          4.563300e-05             0.579847               0.579801        random_rows frac0.60_rep001          raw05
      jepa_bad_q2     structured_best1       6.861140e-04          6.861140e-04             0.580487               0.579801 subject_contiguous frac0.40_rep052   entropy_g075
      jepa_bad_q2          train_best1       3.521840e-04          3.521840e-04             0.580153               0.579801        random_rows frac0.40_rep009   entropy_g075
      jepa_bad_q2    train_best12_mean       6.493690e-04          6.493690e-04             0.580451               0.579801        random_rows frac0.40_rep009   entropy_g075
      jepa_bad_q2     train_best5_mean       5.797710e-04          5.797710e-04             0.580381               0.579801        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual nonrandom_best5_mean       1.270313e-03         -1.270313e-03             0.579957               0.581227 subject_contiguous frac0.40_rep052   entropy_g075
jepa_bad_residual         oracle_best1       7.316000e-04         -7.316000e-04             0.580496               0.581227       global_order    rowmod4_rem3          raw05
jepa_bad_residual     structured_best1       1.129899e-03         -1.129899e-03             0.580097               0.581227 subject_contiguous frac0.40_rep052   entropy_g075
jepa_bad_residual          train_best1       9.756010e-04         -9.756010e-04             0.580252               0.581227        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual    train_best12_mean       1.212383e-03         -1.212383e-03             0.580015               0.581227        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual     train_best5_mean       1.289644e-03         -1.289644e-03             0.579938               0.581227        random_rows frac0.40_rep009   entropy_g075
       lejepa_bad nonrandom_best5_mean       2.446100e-05         -2.446100e-05             0.580222               0.580247 subject_contiguous frac0.40_rep052   entropy_g075
       lejepa_bad         oracle_best1       2.360000e-07         -2.360000e-07             0.580247               0.580247        random_rows frac0.40_rep197   entropy_g050
       lejepa_bad     structured_best1       1.952700e-04         -1.952700e-04             0.580052               0.580247 subject_contiguous frac0.40_rep052   entropy_g075
       lejepa_bad          train_best1       6.307500e-05          6.307500e-05             0.580310               0.580247        random_rows frac0.40_rep009   entropy_g075
       lejepa_bad    train_best12_mean       1.136560e-04          1.136560e-04             0.580360               0.580247        random_rows frac0.40_rep009   entropy_g075
       lejepa_bad     train_best5_mean       7.318000e-05          7.318000e-05             0.580320               0.580247        random_rows frac0.40_rep009   entropy_g075
        ordinal_q nonrandom_best5_mean       1.033483e-03          1.033483e-03             0.579337               0.578303 subject_contiguous frac0.40_rep052   entropy_g075
        ordinal_q         oracle_best1       6.834500e-05          6.834500e-05             0.578372               0.578303 subject_contiguous frac0.25_rep099   entropy_g050
        ordinal_q     structured_best1       6.444550e-04          6.444550e-04             0.578948               0.578303 subject_contiguous frac0.40_rep052   entropy_g075
        ordinal_q          train_best1       3.892600e-04          3.892600e-04             0.578693               0.578303        random_rows frac0.40_rep009   entropy_g075
        ordinal_q    train_best12_mean       8.408620e-04          8.408620e-04             0.579144               0.578303        random_rows frac0.40_rep009   entropy_g075
        ordinal_q     train_best5_mean       6.990470e-04          6.990470e-04             0.579002               0.578303        random_rows frac0.40_rep009   entropy_g075
            raw05 nonrandom_best5_mean       1.433430e-04          1.433430e-04             0.577670               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05         oracle_best1       3.631300e-05          3.631300e-05             0.577563               0.577526 subject_contiguous frac0.25_rep099          raw05
            raw05     structured_best1       1.439610e-04          1.439610e-04             0.577670               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05          train_best1       1.439610e-04          1.439610e-04             0.577670               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05    train_best12_mean       1.327160e-04          1.327160e-04             0.577659               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05     train_best5_mean       1.379350e-04          1.379350e-04             0.577664               0.577526       global_order    rowmod4_rem3   entropy_g075
```

## Train-Selected Top Fits By Heldout Anchor

```
      heldout_key          mask_kind       mask_name  rows   prior_name  train_solution_score  train_weighted_std_rmse  train_mean_abs_shift_vs_prior  heldout_abs_error  heldout_pred_delta  heldout_obs_delta
        anchor578        random_rows frac0.40_rep009   100 entropy_g075              0.000331                      0.0                       0.011042           0.001574            0.002056           0.000482
        anchor578        random_rows frac0.40_rep002   100         a2c8              0.000359                      0.0                       0.011977           0.002589            0.003072           0.000482
        anchor578        random_rows frac0.40_rep009   100 entropy_g050              0.000363                      0.0                       0.012084           0.002157            0.002639           0.000482
        anchor578        random_rows frac0.40_rep009   100         a2c8              0.000372                      0.0                       0.012416           0.002708            0.003190           0.000482
        anchor578        random_rows frac0.30_rep223    75         a2c8              0.000374                      0.0                       0.012482           0.003455            0.003938           0.000482
      cvjepa_a2c8       global_order    rowmod4_rem3    62 entropy_g075              0.000304                      0.0                       0.010132           0.000146           -0.000652          -0.000506
      cvjepa_a2c8        random_rows frac0.20_rep114    50 entropy_g075              0.000310                      0.0                       0.010327           0.000145           -0.000651          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep132   100 entropy_g075              0.000315                      0.0                       0.010491           0.000137           -0.000642          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep009   100 entropy_g075              0.000317                      0.0                       0.010574           0.000082           -0.000587          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep223   100 entropy_g075              0.000322                      0.0                       0.010733           0.000152           -0.000658          -0.000506
      jepa_bad_q2        random_rows frac0.40_rep009   100 entropy_g075              0.000377                      0.0                       0.012551           0.000352            0.002208           0.001856
      jepa_bad_q2 subject_contiguous frac0.40_rep052   101 entropy_g075              0.000408                      0.0                       0.013592           0.000686            0.002542           0.001856
      jepa_bad_q2        random_rows frac0.30_rep056    75 entropy_g075              0.000434                      0.0                       0.014473           0.001092            0.002948           0.001856
      jepa_bad_q2        random_rows frac0.40_rep002   100 entropy_g075              0.000442                      0.0                       0.014719           0.000420            0.002276           0.001856
      jepa_bad_q2        random_rows frac0.40_rep009   100 entropy_g050              0.000444                      0.0                       0.014793           0.000349            0.002205           0.001856
jepa_bad_residual        random_rows frac0.40_rep009   100 entropy_g075              0.000338                      0.0                       0.011272           0.000976            0.002307           0.003282
jepa_bad_residual subject_contiguous frac0.40_rep052   101 entropy_g075              0.000372                      0.0                       0.012385           0.001130            0.002152           0.003282
jepa_bad_residual        random_rows frac0.30_rep056    75 entropy_g075              0.000384                      0.0                       0.012789           0.001592            0.001690           0.003282
jepa_bad_residual subject_contiguous frac0.40_rep009   101 entropy_g075              0.000390                      0.0                       0.012987           0.001621            0.001661           0.003282
jepa_bad_residual        random_rows frac0.20_rep114    50 entropy_g075              0.000396                      0.0                       0.013190           0.001129            0.002153           0.003282
       lejepa_bad        random_rows frac0.40_rep009   100 entropy_g075              0.000384                      0.0                       0.012806           0.000063            0.002365           0.002302
       lejepa_bad subject_contiguous frac0.40_rep052   101 entropy_g075              0.000419                      0.0                       0.013974           0.000195            0.002107           0.002302
       lejepa_bad        random_rows frac0.40_rep002   100 entropy_g075              0.000442                      0.0                       0.014726           0.000341            0.002643           0.002302
       lejepa_bad        random_rows frac0.40_rep009   100 entropy_g050              0.000449                      0.0                       0.014976           0.000080            0.002382           0.002302
       lejepa_bad        random_rows frac0.30_rep221    75 entropy_g075              0.000452                      0.0                       0.015073           0.000077            0.002379           0.002302
        ordinal_q        random_rows frac0.40_rep009   100 entropy_g075              0.000381                      0.0                       0.012690           0.000389            0.000748           0.000358
        ordinal_q subject_contiguous frac0.40_rep052   101 entropy_g075              0.000413                      0.0                       0.013782           0.000644            0.001003           0.000358
        ordinal_q        random_rows frac0.40_rep040   100 entropy_g075              0.000430                      0.0                       0.014335           0.000926            0.001285           0.000358
        ordinal_q        random_rows frac0.30_rep221    75 entropy_g075              0.000432                      0.0                       0.014404           0.000803            0.001161           0.000358
        ordinal_q        random_rows frac0.40_rep002   100 entropy_g075              0.000434                      0.0                       0.014468           0.000733            0.001091           0.000358
            raw05       global_order    rowmod4_rem3    62 entropy_g075              0.000255                      0.0                       0.008500           0.000144           -0.000275          -0.000419
            raw05        random_rows frac0.40_rep223   100 entropy_g075              0.000273                      0.0                       0.009101           0.000151           -0.000267          -0.000419
            raw05        random_rows frac0.40_rep132   100 entropy_g075              0.000274                      0.0                       0.009131           0.000138           -0.000280          -0.000419
            raw05        random_rows frac0.20_rep114    50 entropy_g075              0.000274                      0.0                       0.009136           0.000140           -0.000278          -0.000419
            raw05        random_rows frac0.40_rep002   100 entropy_g075              0.000282                      0.0                       0.009415           0.000115           -0.000303          -0.000419
```

## Interpretation

- If `train_best*` is much worse than `oracle_best1`, the inverse problem is still underidentified: useful label assignments exist, but the current selector cannot reliably choose them.
- A high error on `cvjepa_a2c8` means the direct-label solver can reproduce older anchors while missing the new best anchor, so direct-label probes should be treated as diagnostic larger moves.
