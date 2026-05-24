# Q3 — Irreducible noise floor

Goal: estimate the *lowest* mean logloss anyone could reach on this dataset, given that labels are noisy binary self-reports.


## 1. Nested entropy / oracle bounds (lower is better)

Bounds become progressively tighter as the predictor uses more info. The *achievable floor* is somewhere between `subject_3day_H` (lots of info) and `oracle_subj_LOO_ll` (subject-only info, no temporal structure).

| target | marginal_H | subject_H | subject_3day_H | oracle_subj_LOO_ll |
|---|---|---|---|---|
| Q1 | 0.6931 | 0.6372 | 0.8480 | 0.6605 |
| Q2 | 0.6854 | 0.6445 | 0.7141 | 0.6677 |
| Q3 | 0.6730 | 0.6417 | 0.7656 | 0.6649 |
| S1 | 0.6252 | 0.5519 | 0.7734 | 0.5757 |
| S2 | 0.6468 | 0.5505 | 0.7740 | 0.5742 |
| S3 | 0.6396 | 0.5098 | 0.7082 | 0.5326 |
| S4 | 0.6859 | 0.6197 | 0.8504 | 0.6430 |
| __mean__ | 0.6641 | 0.5936 | 0.7762 | 0.6170 |


## 2. Bootstrap CI on `subject_prior_a20` (B=2000, train-on-bootstrap, score-on-original)

| target | mean | lo | hi |
|---|---|---|---|
| Q1 | 0.6504 | 0.6435 | 0.6596 |
| Q2 | 0.6547 | 0.6485 | 0.6638 |
| Q3 | 0.6503 | 0.6448 | 0.6588 |
| S1 | 0.5654 | 0.5581 | 0.5755 |
| S2 | 0.5676 | 0.5596 | 0.5785 |
| S3 | 0.5317 | 0.5228 | 0.5427 |
| S4 | 0.6342 | 0.6267 | 0.6438 |
| __avg__ | 0.6078 | 0.6042 | 0.6120 |


## 3. Interpretation

- **marginal H** (no info): 0.6641 — random baseline.
- **subject H** (E_s[H(Y|s)]): 0.5936 — what subject-only prior buys *if* labels are pure Bernoulli at the per-subject rate.
- **subject+3-day-neighbor H**: 0.7762 — what tightening with same-subject ±3-day local labels buys.
- **oracle subject LOO**: 0.6170 — actually-achieved logloss using the LOO subject mean on the real train labels. This is `subject_prior_a∞`.
- **subject_prior_a20 bootstrap CI**: 0.6078 [0.6042, 0.6120].


Delta available *below the subject anchor*: `subject_3day_H − subject_H` = +0.1826.
If this delta is negative, exploiting same-subject local temporal info is mathematically allowed to lower mean logloss by ~|delta|.
If near zero, local temporal info adds nothing on top of subject prior.


### Decision implication
- If `subject_3day_H ≈ subject_H` → Q-family hole interpolation is *not* a free lunch; the anchor already captures what neighbor labels would add.
- If `subject_3day_H < subject_H` by >0.02 → there is real, measurable headroom for Q-family hole specialists.
- If `oracle_subj_LOO_ll < subject_prior_a20_bootstrap_mean − 0.01` → α=20 smoothing is throwing away some subject signal; try smaller α.
- The bootstrap CI width tells how much fold-to-fold noise to expect on the anchor alone; differences inside that CI are *not* real improvements.
