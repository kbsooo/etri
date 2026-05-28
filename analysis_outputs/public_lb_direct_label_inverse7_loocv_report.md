# Direct Label Inverse7 Leave-One-Anchor CV

This checks whether soft-label inverse solutions selected on five public anchors predict the sixth public anchor.

## Overall Policy Error

```
              policy  heldout_abs_error  heldout_signed_error  top_solution_score
        oracle_best1           0.000363              0.000113            0.000541
         train_best1           0.000599              0.000221            0.000330
    train_best5_mean           0.000928              0.000448            0.000330
   train_best12_mean           0.000967              0.000512            0.000330
    structured_best1           0.001009              0.000558            0.000351
nonrandom_best5_mean           0.001095              0.000607            0.000351
```

## Per-Anchor Policy Error

```
      heldout_key               policy  heldout_abs_error  heldout_signed_error  heldout_public_pred  heldout_public_actual      top_mask_kind   top_mask_name top_prior_name
        anchor578 nonrandom_best5_mean           0.003149              0.003149             0.581577               0.578427 subject_contiguous frac0.25_rep150           a2c8
        anchor578         oracle_best1           0.001294              0.001294             0.579721               0.578427 subject_contiguous frac0.40_rep052   entropy_g075
        anchor578     structured_best1           0.003211              0.003211             0.581639               0.578427 subject_contiguous frac0.25_rep150           a2c8
        anchor578          train_best1           0.001576              0.001576             0.580004               0.578427        random_rows frac0.40_rep009   entropy_g075
        anchor578    train_best12_mean           0.002810              0.002810             0.581237               0.578427        random_rows frac0.40_rep009   entropy_g075
        anchor578     train_best5_mean           0.002502              0.002502             0.580929               0.578427        random_rows frac0.40_rep009   entropy_g075
      cvjepa_a2c8 nonrandom_best5_mean           0.000145             -0.000145             0.577294               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8         oracle_best1           0.000032             -0.000032             0.577407               0.577439 subject_contiguous frac0.25_rep099          raw05
      cvjepa_a2c8     structured_best1           0.000147             -0.000147             0.577292               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8          train_best1           0.000147             -0.000147             0.577292               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8    train_best12_mean           0.000128             -0.000128             0.577311               0.577439       global_order    rowmod4_rem3   entropy_g075
      cvjepa_a2c8     train_best5_mean           0.000133             -0.000133             0.577307               0.577439       global_order    rowmod4_rem3   entropy_g075
      jepa_bad_q2 nonrandom_best5_mean           0.000782              0.000782             0.580583               0.579801 subject_contiguous frac0.40_rep052   entropy_g075
      jepa_bad_q2         oracle_best1           0.000043              0.000043             0.579845               0.579801        random_rows frac0.60_rep001          raw05
      jepa_bad_q2     structured_best1           0.000698              0.000698             0.580499               0.579801 subject_contiguous frac0.40_rep052   entropy_g075
      jepa_bad_q2          train_best1           0.000351              0.000351             0.580153               0.579801        random_rows frac0.40_rep009   entropy_g075
      jepa_bad_q2    train_best12_mean           0.000651              0.000651             0.580453               0.579801        random_rows frac0.40_rep009   entropy_g075
      jepa_bad_q2     train_best5_mean           0.000788              0.000788             0.580589               0.579801        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual nonrandom_best5_mean           0.001319             -0.001319             0.579909               0.581227 subject_contiguous frac0.40_rep052   entropy_g075
jepa_bad_residual         oracle_best1           0.000717             -0.000717             0.580510               0.581227       global_order    rowmod4_rem3          raw05
jepa_bad_residual     structured_best1           0.001206             -0.001206             0.580022               0.581227 subject_contiguous frac0.40_rep052   entropy_g075
jepa_bad_residual          train_best1           0.000986             -0.000986             0.580241               0.581227        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual    train_best12_mean           0.001237             -0.001237             0.579990               0.581227        random_rows frac0.40_rep009   entropy_g075
jepa_bad_residual     train_best5_mean           0.001307             -0.001307             0.579920               0.581227        random_rows frac0.40_rep009   entropy_g075
        ordinal_q nonrandom_best5_mean           0.001032              0.001032             0.579336               0.578303 subject_contiguous frac0.40_rep052   entropy_g075
        ordinal_q         oracle_best1           0.000054              0.000054             0.578358               0.578303 subject_contiguous frac0.25_rep099   entropy_g050
        ordinal_q     structured_best1           0.000645              0.000645             0.578948               0.578303 subject_contiguous frac0.40_rep052   entropy_g075
        ordinal_q          train_best1           0.000386              0.000386             0.578690               0.578303        random_rows frac0.40_rep009   entropy_g075
        ordinal_q    train_best12_mean           0.000841              0.000841             0.579144               0.578303        random_rows frac0.40_rep009   entropy_g075
        ordinal_q     train_best5_mean           0.000698              0.000698             0.579001               0.578303        random_rows frac0.40_rep009   entropy_g075
            raw05 nonrandom_best5_mean           0.000144              0.000144             0.577671               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05         oracle_best1           0.000035              0.000035             0.577562               0.577526 subject_contiguous frac0.25_rep099          raw05
            raw05     structured_best1           0.000145              0.000145             0.577671               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05          train_best1           0.000145              0.000145             0.577671               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05    train_best12_mean           0.000135              0.000135             0.577661               0.577526       global_order    rowmod4_rem3   entropy_g075
            raw05     train_best5_mean           0.000138              0.000138             0.577665               0.577526       global_order    rowmod4_rem3   entropy_g075
```

## Train-Selected Top Fits By Heldout Anchor

```
      heldout_key          mask_kind       mask_name  rows   prior_name  train_solution_score  train_weighted_std_rmse  train_mean_abs_shift_vs_prior  heldout_abs_error  heldout_pred_delta  heldout_obs_delta
        anchor578        random_rows frac0.40_rep009   100 entropy_g075              0.000332                      0.0                       0.011052           0.001576            0.002059           0.000482
        anchor578        random_rows frac0.40_rep002   100         a2c8              0.000359                      0.0                       0.011962           0.002593            0.003076           0.000482
        anchor578        random_rows frac0.40_rep009   100 entropy_g050              0.000363                      0.0                       0.012088           0.002160            0.002642           0.000482
        anchor578        random_rows frac0.40_rep009   100         a2c8              0.000372                      0.0                       0.012398           0.002711            0.003194           0.000482
        anchor578        random_rows frac0.30_rep223    75         a2c8              0.000375                      0.0                       0.012506           0.003467            0.003949           0.000482
      cvjepa_a2c8       global_order    rowmod4_rem3    62 entropy_g075              0.000303                      0.0                       0.010087           0.000147           -0.000653          -0.000506
      cvjepa_a2c8        random_rows frac0.20_rep114    50 entropy_g075              0.000309                      0.0                       0.010311           0.000145           -0.000651          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep132   100 entropy_g075              0.000313                      0.0                       0.010448           0.000137           -0.000643          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep009   100 entropy_g075              0.000317                      0.0                       0.010561           0.000082           -0.000587          -0.000506
      cvjepa_a2c8        random_rows frac0.40_rep223   100 entropy_g075              0.000322                      0.0                       0.010720           0.000152           -0.000658          -0.000506
      jepa_bad_q2        random_rows frac0.40_rep009   100 entropy_g075              0.000377                      0.0                       0.012564           0.000351            0.002208           0.001856
      jepa_bad_q2 subject_contiguous frac0.40_rep052   101 entropy_g075              0.000403                      0.0                       0.013427           0.000698            0.002554           0.001856
      jepa_bad_q2        random_rows frac0.30_rep056    75 entropy_g075              0.000436                      0.0                       0.014524           0.001080            0.002936           0.001856
      jepa_bad_q2        random_rows frac0.40_rep002   100 entropy_g075              0.000439                      0.0                       0.014630           0.000412            0.002269           0.001856
      jepa_bad_q2 subject_contiguous frac0.25_rep150    64 entropy_g075              0.000441                      0.0                       0.014707           0.001398            0.003254           0.001856
jepa_bad_residual        random_rows frac0.40_rep009   100 entropy_g075              0.000337                      0.0                       0.011236           0.000986            0.002296           0.003282
jepa_bad_residual subject_contiguous frac0.40_rep052   101 entropy_g075              0.000361                      0.0                       0.012032           0.001206            0.002077           0.003282
jepa_bad_residual        random_rows frac0.30_rep056    75 entropy_g075              0.000384                      0.0                       0.012793           0.001580            0.001702           0.003282
jepa_bad_residual subject_contiguous frac0.40_rep009   101 entropy_g075              0.000389                      0.0                       0.012962           0.001633            0.001649           0.003282
jepa_bad_residual        random_rows frac0.20_rep114    50 entropy_g075              0.000396                      0.0                       0.013186           0.001130            0.002153           0.003282
        ordinal_q        random_rows frac0.40_rep009   100 entropy_g075              0.000381                      0.0                       0.012701           0.000386            0.000745           0.000358
        ordinal_q subject_contiguous frac0.40_rep052   101 entropy_g075              0.000410                      0.0                       0.013652           0.000645            0.001003           0.000358
        ordinal_q        random_rows frac0.40_rep040   100 entropy_g075              0.000431                      0.0                       0.014353           0.000925            0.001284           0.000358
        ordinal_q        random_rows frac0.40_rep002   100 entropy_g075              0.000431                      0.0                       0.014360           0.000730            0.001089           0.000358
        ordinal_q        random_rows frac0.30_rep221    75 entropy_g075              0.000433                      0.0                       0.014417           0.000801            0.001159           0.000358
            raw05       global_order    rowmod4_rem3    62 entropy_g075              0.000253                      0.0                       0.008430           0.000145           -0.000274          -0.000419
            raw05        random_rows frac0.40_rep132   100 entropy_g075              0.000272                      0.0                       0.009080           0.000139           -0.000279          -0.000419
            raw05        random_rows frac0.40_rep223   100 entropy_g075              0.000273                      0.0                       0.009096           0.000152           -0.000267          -0.000419
            raw05        random_rows frac0.20_rep114    50 entropy_g075              0.000274                      0.0                       0.009124           0.000141           -0.000278          -0.000419
            raw05        random_rows frac0.40_rep002   100 entropy_g075              0.000282                      0.0                       0.009413           0.000115           -0.000304          -0.000419
```

## Interpretation

- If `train_best*` is much worse than `oracle_best1`, the inverse problem is still underidentified: useful label assignments exist, but the current selector cannot reliably choose them.
- A high error on `cvjepa_a2c8` means the direct-label solver can reproduce older anchors while missing the new best anchor, so direct-label probes should be treated as diagnostic larger moves.
