# Label-temporal diagnostics, no submission

This experiment uses train labels only under masked validation. It does not produce submission files.

## testpattern best methods

target               method  logloss  delta_vs_subject    auc
    Q1 both_exp_tau7_alpha5   0.6684           -0.0162 0.6409
    Q1       both_exp_tau30   0.6819           -0.0027 0.6199
    Q1         subject_mean   0.6846            0.0000 0.6034
    Q2 both_exp_tau7_alpha5   0.6503           -0.0580 0.6459
    Q2       both_exp_tau30   0.6858           -0.0224 0.6144
    Q2               global   0.6859           -0.0223 0.5000
    Q3 both_exp_tau7_alpha5   0.6474           -0.0400 0.6161
    Q3               global   0.6704           -0.0170 0.5000
    Q3       both_exp_tau30   0.6779           -0.0094 0.5991
    S1         subject_mean   0.5918            0.0000 0.6794
    S1 both_exp_tau7_alpha5   0.5981            0.0063 0.6537
    S1       both_exp_tau30   0.5991            0.0073 0.6809
    S2       both_exp_tau30   0.5765           -0.0106 0.7367
    S2         subject_mean   0.5871            0.0000 0.7242
    S2 both_exp_tau7_alpha5   0.6062            0.0191 0.6945
    S3         subject_mean   0.5596            0.0000 0.7590
    S3       both_exp_tau30   0.5753            0.0157 0.7452
    S3 both_exp_tau7_alpha5   0.5880            0.0284 0.7212
    S4         subject_mean   0.6523            0.0000 0.6537
    S4       both_exp_tau30   0.6571            0.0048 0.6635
    S4 both_exp_tau7_alpha5   0.6576            0.0053 0.6480

## random_gap best methods

target               method  logloss  delta_vs_subject    auc
    Q1        both_exp_tau7   0.6407           -0.0173 0.6778
    Q1       both_exp_tau30   0.6483           -0.0097 0.6517
    Q1 both_exp_tau7_alpha5   0.6489           -0.0091 0.6749
    Q2 both_exp_tau7_alpha5   0.6320           -0.0476 0.6852
    Q2        both_exp_tau7   0.6428           -0.0369 0.6799
    Q2       both_exp_tau30   0.6526           -0.0271 0.6539
    Q3 both_exp_tau7_alpha5   0.6344           -0.0269 0.6620
    Q3        both_exp_tau7   0.6459           -0.0154 0.6594
    Q3       both_exp_tau30   0.6463           -0.0150 0.6475
    S1         subject_mean   0.5675            0.0000 0.7143
    S1       both_exp_tau30   0.5685            0.0010 0.7187
    S1 both_exp_tau7_alpha5   0.5836            0.0161 0.6937
    S2       both_exp_tau30   0.5675           -0.0104 0.7465
    S2         subject_mean   0.5779            0.0000 0.7300
    S2 both_exp_tau7_alpha5   0.5851            0.0071 0.7182
    S3         subject_mean   0.5430            0.0000 0.7740
    S3       both_exp_tau30   0.5526            0.0096 0.7687
    S3 both_exp_tau7_alpha5   0.5718            0.0288 0.7477
    S4       both_exp_tau30   0.6408           -0.0080 0.6859
    S4 both_exp_tau7_alpha5   0.6446           -0.0042 0.6848
    S4         subject_mean   0.6488            0.0000 0.6601

## tail best methods

target               method  logloss  delta_vs_subject    auc
    Q1         subject_mean   0.6557            0.0000 0.6194
    Q1       both_exp_tau30   0.6950            0.0393 0.5991
    Q1       past_exp_tau30   0.6950            0.0393 0.5991
    Q2 both_exp_tau7_alpha5   0.6734           -0.0261 0.5715
    Q2               global   0.6782           -0.0213 0.5000
    Q2                next1   0.6782           -0.0213 0.5000
    Q3               global   0.6617           -0.0480 0.5000
    Q3                next1   0.6617           -0.0480 0.5000
    Q3 both_exp_tau7_alpha5   0.6617           -0.0480 0.5687
    S1         subject_mean   0.5644            0.0000 0.7057
    S1       both_exp_tau30   0.5660            0.0016 0.6881
    S1       past_exp_tau30   0.5660            0.0016 0.6881
    S2       both_exp_tau30   0.6295           -0.0146 0.7273
    S2       past_exp_tau30   0.6295           -0.0146 0.7273
    S2         subject_mean   0.6441            0.0000 0.6959
    S3         subject_mean   0.5971            0.0000 0.7253
    S3       both_exp_tau30   0.6084            0.0114 0.7270
    S3       past_exp_tau30   0.6084            0.0114 0.7270
    S4       both_exp_tau30   0.6533           -0.0137 0.6665
    S4       past_exp_tau30   0.6533           -0.0137 0.6665
    S4         subject_mean   0.6669            0.0000 0.6374
