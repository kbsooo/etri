# Fold-Local Channel MoE Decoder v1

## Goal

Treat the fold-local channel-fusion decoders as expert predictions and train a small fold-safe stacking gate over their probabilities/logits. This tests whether the channel-patch experts contain complementary signal beyond the best single expert.

## Result

- Best source: `baseline_targetwise_hybrid`
- OOF avg logloss: `0.616459`
- Drift vs v83 reference: `0.077083`
- Input sources: `8`

## Top MoE Scores

| source | avg_log_loss | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| moe_ridge_a5_b0.35 | 0.618702 | 0.069869 | 0.666184 | 0.679228 | 0.666059 | 0.570080 | 0.578453 | 0.527844 | 0.643068 |
| moe_ridge_a20_b0.35 | 0.620622 | 0.066650 | 0.666870 | 0.687029 | 0.666376 | 0.570574 | 0.579438 | 0.528634 | 0.645434 |
| moe_ridge_a5_b0.2 | 0.622025 | 0.065053 | 0.668546 | 0.689146 | 0.670186 | 0.572136 | 0.578928 | 0.530516 | 0.644720 |
| moe_logreg_c0.3_b0.35 | 0.622250 | 0.068613 | 0.666608 | 0.690317 | 0.667120 | 0.572861 | 0.581690 | 0.530511 | 0.646643 |
| moe_ridge_a80_b0.35 | 0.622917 | 0.064080 | 0.668703 | 0.693925 | 0.667856 | 0.572321 | 0.580058 | 0.530594 | 0.646961 |
| moe_ridge_a20_b0.2 | 0.623317 | 0.063791 | 0.669200 | 0.694048 | 0.670591 | 0.572533 | 0.579566 | 0.531092 | 0.646186 |
| moe_logreg_c0.1_b0.35 | 0.623708 | 0.066600 | 0.667753 | 0.696056 | 0.667970 | 0.573566 | 0.581037 | 0.531568 | 0.648008 |
| moe_logreg_c0.3_b0.2 | 0.624136 | 0.064392 | 0.668999 | 0.695492 | 0.670952 | 0.573805 | 0.580793 | 0.532073 | 0.646836 |
| moe_ridge_a5_b0.1 | 0.624668 | 0.063017 | 0.670679 | 0.696672 | 0.673687 | 0.573792 | 0.579351 | 0.532550 | 0.645946 |
| moe_ridge_a80_b0.2 | 0.624784 | 0.062802 | 0.670474 | 0.698297 | 0.671704 | 0.573687 | 0.579939 | 0.532301 | 0.647087 |
| moe_logreg_c0.1_b0.2 | 0.625089 | 0.063696 | 0.669774 | 0.699104 | 0.671544 | 0.574315 | 0.580458 | 0.532778 | 0.647652 |
| moe_logreg_c0.03_b0.35 | 0.625226 | 0.064969 | 0.669529 | 0.700479 | 0.669757 | 0.574678 | 0.580551 | 0.532881 | 0.648708 |
| moe_ridge_a20_b0.1 | 0.625380 | 0.062587 | 0.671070 | 0.699283 | 0.673978 | 0.574033 | 0.579695 | 0.532881 | 0.646717 |
| moe_logreg_c0.3_b0.1 | 0.625746 | 0.062808 | 0.670945 | 0.699853 | 0.674108 | 0.574661 | 0.580288 | 0.533341 | 0.647029 |
| moe_logreg_c0.03_b0.2 | 0.626057 | 0.063190 | 0.670919 | 0.701847 | 0.672741 | 0.575034 | 0.580198 | 0.533598 | 0.648060 |
| moe_ridge_a5_b0.05 | 0.626119 | 0.062265 | 0.671886 | 0.700734 | 0.675665 | 0.574714 | 0.579593 | 0.533644 | 0.646597 |
| moe_ridge_a80_b0.1 | 0.626163 | 0.062147 | 0.671777 | 0.701521 | 0.674599 | 0.574666 | 0.579887 | 0.533515 | 0.647177 |
| moe_logreg_c0.1_b0.1 | 0.626265 | 0.062563 | 0.671372 | 0.701778 | 0.674441 | 0.574952 | 0.580134 | 0.533727 | 0.647448 |
| moe_ridge_a20_b0.05 | 0.626490 | 0.062084 | 0.672095 | 0.702082 | 0.675822 | 0.574845 | 0.579771 | 0.533819 | 0.646992 |
| moe_logreg_c0.3_b0.05 | 0.626662 | 0.062292 | 0.672026 | 0.702327 | 0.675875 | 0.575158 | 0.580063 | 0.534042 | 0.647144 |

## Target-Wise Gate

- Target-wise avg logloss: `0.618702`
- Target-wise drift vs v83: `0.069869`

| target | source | loss |
| --- | --- | --- |
| Q1 | moe_ridge_a5_b0.35 | 0.666184 |
| Q2 | moe_ridge_a5_b0.35 | 0.679228 |
| Q3 | moe_ridge_a5_b0.35 | 0.666059 |
| S1 | moe_ridge_a5_b0.35 | 0.570080 |
| S2 | moe_ridge_a5_b0.35 | 0.578453 |
| S3 | moe_ridge_a5_b0.35 | 0.527844 |
| S4 | moe_ridge_a5_b0.35 | 0.643068 |

## Baseline Hybrid Gate

This keeps the fold-local no-PCA selected decoder unless a MoE source beats it for a target.

- Hybrid avg logloss: `0.616459`
- Hybrid drift vs v83: `0.077083`

| target | source | loss |
| --- | --- | --- |
| Q1 | baseline | 0.662785 |
| Q2 | moe_ridge_a5_b0.35 | 0.679228 |
| Q3 | baseline | 0.663960 |
| S1 | baseline | 0.564505 |
| S2 | baseline | 0.575859 |
| S3 | baseline | 0.525808 |
| S4 | moe_ridge_a5_b0.35 | 0.643068 |

## Decision

A positive result means the expert predictions disagree in label-useful ways and the next decoder should become a real latent-level MoE. A flat or negative result means the bottleneck is still the expert latent quality, not the final gate.