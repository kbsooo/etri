# Block-State Bottleneck Audit

## Question

Is the 0.577439 plateau caused by lack of row-level features, or by failure to identify hidden subject/block target-rate states?

## Core Findings

- Validation block-rate oracle mean LogLoss: `0.517878`.
- Temporal-to-block-rate oracle gap: `0.106888`.
- Full subject identity explains only `0.291` of that gap.
- Remaining gap after full subject-rate oracle: `0.075753`.
- Best Markov transition model is worse than temporal by `0.002998`.
- Nested single-feature threshold is worse than temporal by `0.044275`.
- Validation-selected cheating threshold improves by `0.056364`, proving fold-specific slices exist but do not transfer.
- Endpoint pseudo-hidden block reconstruction gains only `0.003252` over subject mean.
- Submission blocks with two train flanks: `0.722` of hidden blocks.
- Best simple structured public mask LOO MAE: `0.000429528`.

## Target-Level Stress

| target | oracle_gain_temporal_to_block | block_state_gap_after_subject_identity | subject_identity_gain | best_markov_delta_vs_temporal | nested_threshold_delta_vs_temporal | hidden_endpoint_gain_vs_subject_mean | lag1_corr |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.112371 | 0.080738 | 0.031633 | -0.001570 | 0.060914 | 0.011072 | 0.236578 |
| Q2 | 0.196925 | 0.145121 | 0.051803 | -0.006591 | 0.034760 | 0.027322 | 0.303538 |
| Q3 | 0.116560 | 0.087793 | 0.028767 | -0.002687 | 0.014413 | 0.016491 | 0.276312 |
| S1 | 0.080225 | 0.050090 | 0.030135 | 0.004999 | 0.051907 | -0.003385 | 0.197105 |
| S2 | 0.084579 | 0.062534 | 0.022044 | 0.008442 | 0.064326 | -0.008450 | 0.169491 |
| S3 | 0.076200 | 0.046542 | 0.029659 | 0.013799 | 0.044618 | -0.017805 | 0.232585 |
| S4 | 0.081354 | 0.057451 | 0.023903 | 0.004593 | 0.038989 | -0.002477 | 0.169331 |

## Block Topology

| metric | value | interpretation |
| --- | --- | --- |
| subjects | 10.000000 | same-subject train/test sharing is real |
| all_blocks | 72.000000 | timeline is block-interleaved |
| train_blocks | 36.000000 | known blocks that can provide context |
| submission_blocks | 36.000000 | hidden block-rate targets to infer |
| submission_rows | 250.000000 | rows affected by hidden block state |
| submission_blocks_with_two_train_flanks | 26.000000 | boundary context is often present but not sufficient |
| submission_blocks_with_one_train_flank | 10.000000 | partial context blocks remain common |
| submission_block_median_rows | 5.500000 | target should be block-rate/count, not only row label |
| submission_block_max_rows | 16.000000 | large hidden blocks create high logloss leverage |
| submission_block_mean_rows | 6.944444 | average hidden segment is non-trivial |

## Interpretation

The strongest 0.5-range path is not another row-level model. The oracle that knows validation block rates reaches the required range, while subject identity, Markov transitions, endpoint labels, and nested one-feature rules fail to reconstruct those rates.

This makes the hidden state more specific than user prior and more stable than row label transitions: it is a block-level rate/count latent. JEPA-style work should therefore predict large block target representations from sparse context, not reconstruct raw features or add another row classifier.

## Decision

- Strengthen the block-state bottleneck hypothesis.
- Keep current improvement submission gate closed.
- Next useful representation experiment: context = subject train-block summaries + overnight/raw measurement-process context; target = held-out block rate vector; energy = block-rate prediction residual plus geometry/isotropy diagnostics.
- Do not repeat simple Markov, endpoint propagation, one-feature threshold, or simple public-mask recovery without a new independent anchor.
