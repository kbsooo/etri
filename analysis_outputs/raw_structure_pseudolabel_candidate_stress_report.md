# E36 Raw-Structure Pseudo-Label Candidate Stress

## Observe

E35 found no certification-grade out-of-anchor evidence for mixmin. The next cheapest independent check is not another public-anchor decomposition, but a train-derived raw-structure pseudo-label stress: do observed subject/date/raw-feature neighborhoods support the candidate movement?

## Wonder

Does mixmin move A2C8 probabilities toward labels implied by train raw-feature neighbors and same-subject temporal priors, or is its support mostly anchor-derived?

## Hypothesis

H35: raw observed structure independently supports mixmin. If true, mixmin should improve soft LogLoss versus A2C8 across subject-temporal, raw-feature KNN, cross-subject KNN, coverage, behavior, and cluster pseudo-label views. If false, support should be sparse, worse than pair sensors, or contradicted by selector veto.

## Method

Built 10 train-derived pseudo-label sources from `analysis_outputs/all_keys_deep_features.parquet`: subject mean, same-subject temporal KNN, all-sensor KNN, cross-subject sensor KNN, coverage-count KNN, sensor-stat KNN, and raw-feature clusters. Scored five candidate sensors against A2C8 using soft LogLoss, movement-to-prior alignment, and row movement anatomy. No public LB scores or known public-anchor losses are used in these pseudo-labels.

## Result

- pseudo-label sources: `10`.
- train/test adversarial AUC from raw sensor features: `0.607876`.
- raw-structure gates passing: `0`.
- best support-rate candidate: `inverse7blend_1040` with support_rate `1.000`, mean_delta `-0.000705727`, worst_delta `-0.000507826`.
- mixmin support_rate `0.500`, mean_delta `0.000065107`, worst_delta `0.000498574`, mean_toward_rate `0.526`.

## Interpretation

Raw-structure pseudo-labels do not support mixmin as an independent validation source. This strengthens the E35 conclusion: mixmin remains a public sensor for anchor-loss/binary-world geometry, not an independently validated improvement.
The surprising positive result is inverse7: it improves against every raw-structure pseudo-label source, including same-subject temporal, raw-feature KNN, cross-subject KNN, coverage, behavior, and cluster priors. That makes inverse7 the current bridge candidate between anchor-loss geometry and raw observed structure, but E35 selector veto and weaker anchor-LOO stability still block a normal-submit claim.

## Decision

Strict submit candidate count remains 0 unless a candidate passes raw-structure support and resolves selector veto. Use this audit to decide whether the next step should search for a better independent raw-structure gate or spend a public sensor.

## Outputs

- `analysis_outputs/raw_structure_pseudolabel_candidate_stress_scores.csv`
- `analysis_outputs/raw_structure_pseudolabel_candidate_stress_summary.csv`
- `analysis_outputs/raw_structure_pseudolabel_candidate_stress_anatomy.csv`
