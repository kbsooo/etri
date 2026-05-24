# Q4 — Per-subject logloss attribution

Mirror_v1 fold family (the LB-mimicking fold). subject_prior_a20 anchor.
Averaged across 3 mirror seeds.


## 1. Per-subject totals (sorted by total loss contribution)

Cumulative top subjects covering ≥50% of total loss: top **id08** ranked subject.

| subject_id | n | mean_ll_subj | sum_ll_subj | mean_ll_marg | mean_ll_lift | loss_share | explainability |
|---|---|---|---|---|---|---|---|
| id04 | 546.0000 | 0.7114 | 388.4010 | 0.6907 | -0.0206 | 0.1460 | -0.0300 |
| id07 | 462.0000 | 0.6553 | 302.7454 | 0.6478 | -0.0075 | 0.1140 | -0.0120 |
| id09 | 399.0000 | 0.7093 | 283.0030 | 0.6749 | -0.0344 | 0.1070 | -0.0510 |
| id05 | 420.0000 | 0.6648 | 279.2257 | 0.7879 | 0.1231 | 0.1050 | 0.1560 |
| id08 | 399.0000 | 0.6928 | 276.4141 | 0.7192 | 0.0264 | 0.1040 | 0.0370 |
| id01 | 399.0000 | 0.6797 | 271.2074 | 0.6705 | -0.0092 | 0.1020 | -0.0140 |
| id02 | 462.0000 | 0.5099 | 235.5714 | 0.5627 | 0.0528 | 0.0890 | 0.0940 |
| id10 | 294.0000 | 0.7447 | 218.9422 | 0.7456 | 0.0009 | 0.0820 | 0.0010 |
| id06 | 441.0000 | 0.4902 | 216.1687 | 0.5504 | 0.0602 | 0.0810 | 0.1090 |
| id03 | 315.0000 | 0.5888 | 185.4674 | 0.6911 | 0.1023 | 0.0700 | 0.1480 |


## 2. Per-(subject, target) anchor logloss

| subject_id | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| id01 | 0.7332 | 0.6888 | 0.7369 | 0.6445 | 0.6863 | 0.5719 | 0.6964 |
| id02 | 0.7136 | 0.6420 | 0.5843 | 0.3180 | 0.2975 | 0.4306 | 0.5832 |
| id03 | 0.5236 | 0.5084 | 0.6231 | 0.4557 | 0.7770 | 0.6934 | 0.5403 |
| id04 | 0.7817 | 0.7245 | 0.6093 | 0.7370 | 0.6572 | 0.7145 | 0.7552 |
| id05 | 0.7020 | 0.7175 | 0.6207 | 0.7204 | 0.6420 | 0.5639 | 0.6873 |
| id06 | 0.5390 | 0.8437 | 0.7730 | 0.2891 | 0.2914 | 0.2341 | 0.4610 |
| id07 | 0.6978 | 0.7090 | 0.6938 | 0.5638 | 0.7258 | 0.5013 | 0.6956 |
| id08 | 0.6779 | 0.6151 | 0.7026 | 0.7047 | 0.7448 | 0.7352 | 0.6691 |
| id09 | 0.7314 | 0.8036 | 0.7463 | 0.7224 | 0.5998 | 0.6875 | 0.6739 |
| id10 | 0.7050 | 0.7883 | 0.8933 | 0.7536 | 0.7260 | 0.7225 | 0.6243 |


## 3. Per-subject mean lift vs marginal (subject prior usefulness)

Positive = subject prior beats marginal. Negative = subject prior overfit / wrong.


| subject_id | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| id01 | -0.0356 | -0.0090 | -0.0270 | -0.0056 | 0.0143 | 0.0003 | -0.0018 |
| id02 | -0.0129 | 0.0232 | 0.0307 | 0.0714 | 0.1298 | 0.0719 | 0.0552 |
| id03 | 0.1968 | 0.1262 | 0.0203 | 0.0274 | 0.0381 | 0.0435 | 0.2635 |
| id04 | -0.0972 | -0.0113 | 0.0287 | -0.0684 | -0.0112 | 0.0383 | -0.0232 |
| id05 | 0.0110 | 0.0055 | 0.0079 | 0.0724 | 0.2859 | 0.4380 | 0.0407 |
| id06 | 0.1345 | -0.1717 | -0.1429 | 0.1393 | 0.1370 | 0.1781 | 0.1473 |
| id07 | -0.0056 | -0.0273 | -0.0068 | 0.0018 | -0.0442 | 0.0154 | 0.0141 |
| id08 | 0.0080 | 0.0476 | 0.0311 | 0.1109 | 0.0068 | -0.0224 | 0.0027 |
| id09 | -0.0285 | -0.1362 | -0.0771 | 0.0258 | -0.0011 | -0.0218 | -0.0018 |
| id10 | -0.0156 | -0.0689 | -0.1454 | 0.0677 | 0.1355 | 0.0371 | -0.0038 |


## 4. Interpretation

- top-3 subjects account for 36.7% of total mirror loss
- bottom-3 subjects account for 23.3%
- worst single subject: **id04** (14.6% of total)
- mean subject_prior lift over marginal: +0.0294
  (positive = the smoothing toward per-subject mean is buying something on average)
- per-subject hardest target: {"id01": "Q3", "id02": "Q1", "id03": "S2", "id04": "Q1", "id05": "S1", "id06": "Q2", "id07": "S2", "id08": "S2", "id09": "Q2", "id10": "Q3"}


### Decision implications
- If top-3 subjects > 50% of loss → subject-specialized treatment is high-ROI.
- If any subject has *negative* mean lift (subject prior worse than marginal) → that subject's label distribution is unusual; subject prior is over-confident in the wrong direction. Consider α decay for those subjects only.
- If per-subject hardest targets cluster (e.g., all subjects worst on Q2) → the difficulty is in the target, not the subject. If they vary by subject → there are subject-specific *target weaknesses*.
