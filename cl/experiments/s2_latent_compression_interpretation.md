# S2 latent compression interpretation

No submission files were created.

## What was tested

1. `62_s2_latent_compression_no_submit.py`
   - Fold-local unsupervised compression on S2 feature families:
     - PCA
     - TruncatedSVD
     - NMF
     - KMeans prototype distances
   - Compared against raw SelectK logistic heads.
   - Validation views: chrono, testpattern, random_gap, tail.

2. `63_s2_label_preserving_compression_no_submit.py`
   - Follow-up after unsupervised compression failed:
     - SelectK -> PCA -> logistic
     - SelectK -> PLS latent -> logistic
     - base S2 head blended with robust raw SelectK heads
   - Same no-submit validation style.

## Main finding

S2 does not like low-dimensional latent compression here.

Unsupervised latent-only models are consistently worse than the existing base. The best latent-only model in script 62 was still positive delta vs base across the robust view, and label-preserving SelectK->PCA/PLS in script 63 was much worse again.

So the signal is not a clean low-rank routine axis. It is sparse/high-dimensional: a small number of original features matter, but compressing them into PCA/PLS/NMF factors loses the discriminative pieces.

## Survivor

The survivor is not latent compression; it is a slightly larger sparse S2 head:

- source: `existing_no_flat`
- model: raw SelectK logistic
- k: 32
- C: 0.003

Robust ranking from script 63:

- mean delta vs base: about `-0.0096`
- worst group delta: about `+0.0019`
- best group delta: about `-0.0177`

This is structurally better than previous hand axes and more credible than PCA/PLS compression, but still not a standalone submission trigger by itself.

## Conservative blend

A safer variant is blending base with raw SelectK32/C0.003:

- blend weight 0.5: mean delta about `-0.0065`, worst group about `-0.0006`
- blend weight 0.7: mean delta about `-0.0082`, worst group about `0.0000`

This is more robust than pure raw on worst-case groups, but it is only an S2-local diagnostic unless combined into a public-LB-informed meta candidate.

## Feature interpretation

The selected S2 features are mostly stable person-level routine/context markers:

- screen count/use subject mean
- light exposure subject mean
- app uniqueness/total time/study-work time subject mean
- WiFi/BLE RSSI/device-class proxies
- screen-off start hour
- late activity last hour
- month / date-gap proxies
- app hourly max/std/unique patterns

This supports the idea that S2 is broad routine/context, but in a sparse original-feature form rather than a low-dimensional hand/latent axis.

## Next step

Do not keep pushing PCA/PLS/NMF for S2.

Next useful step is to create a no-submit public-LB-informed meta diagnostic that only modifies S2 with either:

1. raw SelectK32/C0.003 pure S2 replacement, or
2. base + 0.5/0.7 raw SelectK32 blend,

then inspect prediction shift vs the current public-supported anchor. Only consider actual submission if the shift is small and the changed target set matches previous public-LB constraints.
