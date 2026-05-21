# Hourly Transformer Cross-View Diagnostic

## Result

- Full-OOF target-wise avg logloss: `0.617372`
- Drift vs v83 reference: `0.075561`
- Sources searched: `16`

## Selected Sources

| target | source | target_log_loss |
| --- | --- | --- |
| Q1 | full__targetwise | 0.668064 |
| Q2 | no_sleep__targetwise | 0.669603 |
| Q3 | only_rhythm__targetwise | 0.666235 |
| S1 | full__targetwise | 0.572181 |
| S2 | only_rhythm__targetwise | 0.578532 |
| S3 | only_cross_modal__targetwise | 0.521082 |
| S4 | no_gps__targetwise | 0.645909 |

## Top Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm__targetwise | 0.619825 | 0.668831 | 0.671803 | 0.666235 | 0.573140 | 0.578532 | 0.533031 | 0.647202 |
| only_cross_modal__targetwise | 0.620680 | 0.670683 | 0.678873 | 0.673789 | 0.573474 | 0.579856 | 0.521082 | 0.647001 |
| no_sleep__targetwise | 0.620859 | 0.669511 | 0.669603 | 0.673412 | 0.575158 | 0.579856 | 0.531848 | 0.646622 |
| full__targetwise | 0.622449 | 0.668064 | 0.684871 | 0.671984 | 0.572181 | 0.579739 | 0.533031 | 0.647272 |
| no_missingness__targetwise | 0.622597 | 0.671627 | 0.682902 | 0.668653 | 0.575072 | 0.579749 | 0.533031 | 0.647144 |
| only_core__targetwise | 0.623360 | 0.671664 | 0.683420 | 0.672697 | 0.575702 | 0.579856 | 0.533031 | 0.647150 |
| no_phone__targetwise | 0.623444 | 0.671957 | 0.682492 | 0.673823 | 0.575702 | 0.579856 | 0.533009 | 0.647272 |
| no_gps__targetwise | 0.623866 | 0.668818 | 0.690871 | 0.673823 | 0.575224 | 0.579387 | 0.533031 | 0.645909 |
| only_rhythm__best_global | 0.624185 | 0.669874 | 0.682400 | 0.671174 | 0.575115 | 0.579966 | 0.540899 | 0.649865 |
| only_cross_modal__best_global | 0.625056 | 0.672584 | 0.696710 | 0.677422 | 0.573541 | 0.582703 | 0.523655 | 0.648780 |
| no_sleep__best_global | 0.625144 | 0.670239 | 0.681318 | 0.673412 | 0.578301 | 0.586890 | 0.534490 | 0.651355 |
| no_missingness__best_global | 0.626219 | 0.672169 | 0.696362 | 0.673895 | 0.575562 | 0.582154 | 0.535327 | 0.648063 |

## Caveat

This is intentionally a breakthrough-search diagnostic, not an honest final score. It selects the best view per target on full OOF labels, so nested view selection is required before using this as a submission-quality estimate.