# v81 selection-bias / leakage stress test

- v80 base OOF: `0.477600`
- Train-selected v81 routed OOF (reported): `0.471378` (from outputs/conditional_latent_routing_v81_decoder_only_on_v80)

## 1. Selection-free fixed shrinkage per ablation (HGB source, one uniform weight)

Each row blends the v80 base toward that ablation's HGB OOF with a single weight `s` applied to every row and target. One global knob => negligible selection bias, so this is the honest floor of the gain.

| ablation | best s | avg@best | avg delta | Q1@best | Q1 delta | best-Q1 s | best-Q1 | best-Q1 delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full | 0.250 | 0.472080 | +0.005519 | 0.499245 | +0.021677 | 0.400 | 0.496413 | +0.024509 |
| retrieval_only | 0.000 | 0.477600 | +0.000000 | 0.520922 | +0.000000 | 0.050 | 0.520579 | +0.000343 |
| no_retrieval | 0.250 | 0.469653 | +0.007947 | 0.495462 | +0.025460 | 0.500 | 0.489334 | +0.031588 |
| retrieval_geo_only | 0.250 | 0.471522 | +0.006078 | 0.503462 | +0.017460 | 0.400 | 0.501705 | +0.019217 |
| source_only | 0.250 | 0.470559 | +0.007041 | 0.500067 | +0.020856 | 0.400 | 0.496579 | +0.024344 |
| panel_only | 0.000 | 0.477600 | +0.000000 | 0.520922 | +0.000000 | 0.250 | 0.517288 | +0.003634 |
| base_only | 0.000 | 0.477600 | +0.000000 | 0.520922 | +0.000000 | 0.000 | 0.520922 | +0.000000 |
| no_late | 0.300 | 0.467732 | +0.009868 | 0.495340 | +0.025583 | 0.400 | 0.493339 | +0.027583 |

## 2. Q1 0.019-gain attribution (advisor discriminating ablation)

- full best Q1 gain (selection-free): `+0.024509`
- retrieval_geo_only (geometry, NO neighbor labels): `+0.019217`
- no_retrieval (source-preds + panel + base, NO retrieval): `+0.031588`
- retrieval_only (geometry + neighbor labels, NO source/panel/base): `+0.000343`
- **Interpretation**: v80 source-prediction recombination, NOT neighbor-label smoothing: retrieval-only carries almost no Q1 signal, while source-preds alone reproduce (and exceed) the full gain. The retrieval features are net harmful here — they overfit the HGB decoder.

## 3. Cheap nested-router selection bias (full v81 4-source pool)

- base OOF: `0.477600`
- train-selected router (select & score on full train, in-sample): `0.471070` (delta +0.006529)
- nested router (select on outer-train, score on held-out outer-val): `0.474428` (delta +0.003172)
- **router selection bias** = train-selected - nested = `+0.003357`

Per-target nested vs base:
| target | base | nested | delta |
| --- | --- | --- | --- |
| Q1 | 0.520922 | 0.501839 | +0.019084 |
| Q2 | 0.534345 | 0.532041 | +0.002305 |
| Q3 | 0.497697 | 0.500567 | -0.002871 |
| S1 | 0.467526 | 0.469773 | -0.002248 |
| S2 | 0.449979 | 0.449321 | +0.000658 |
| S3 | 0.407026 | 0.401203 | +0.005823 |
| S4 | 0.465702 | 0.466251 | -0.000548 |

## Honest summary

- The v81 decoder is a **fold-safe decoder, but prior OOF router selection bias remains** in the routed 0.471378 figure.
- Selection-free uniform fixed shrinkage (full, s=0.250) already reaches `0.472080` (+0.005519 vs base), so most of the routed gain reproduces without per-target/bin selection.
- Nested-router selection (selection scored out-of-fold) reaches `0.474428`; the difference to the in-sample train-selected router (`0.471070`) is the router selection bias = `+0.003357`.
