# E92 Hidden-Block Posterior Alignment Audit

## Observe

E91 killed the known-public movement proxy as a submission selector. The remaining E86/E90/E89 choice is not score forecast but hidden-world interpretation: maximum structural retention, row-coherent decontamination, or minimum E72 contamination.

## Wonder

If hidden blocks are part of the true data-generating process, do the post-mixmin candidates move toward the block posterior representation or only optimize local combo stress?

## Hypothesis

H87: E90's row-coherent repair should preserve more hidden-block posterior alignment than E89 while reducing E72 failed-direction agreement versus E86.

## Method

- Use `hidden_block_posterior_block_summary.csv` as the target representation, not as a public-LB label.
- For each candidate, compare its probabilities against mixmin using row-repeated block posterior rates and endpoint rates.
- Measure posterior CE delta, posterior-direction mass agreement, hidden-block/target R2 of logit movement, movement concentration in high-posterior-shift blocks, and agreement with the failed E72 direction.
- Join the existing E89/E90 local stress metrics only as context; no public score regression is fit.

## Candidate Scores

| role | file | hidden_block_alignment_score | posterior_ce_delta_all_vs_mixmin | endpoint_ce_delta_all_vs_mixmin | posterior_direction_mass_agree | block_target_r2 | posterior_shift_topquartile_mass_lift | e72_direction_mass_agree | local_all_delta_vs_mixmin | local_e72_failed_contamination_index | local_hidden_q2s3_mean_minus_base | local_world_support_minus_base |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| failed_e72 | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 5.98837 | -0.0002873 | -0.000757074 | 0.584266 | 0.349984 | 1.01233 | 1 |  |  |  |  |
| noq2_contrast | submission_e87_noq2_source_consensus_a85c4e39.csv | 5.60519 | -0.000257196 | -0.000226515 | 0.639058 | 0.342148 | 0.940266 | 0.650503 | -2.69461e-05 | 0.730408 | -0.000254206 | -0.000171638 |
| max_upside_e86 | submission_e86_e85_consensus_a3f7c96f.csv | 5.56267 | -0.000255621 | -0.000223351 | 0.633337 | 0.352179 | 0.939023 | 0.668166 | -2.77059e-05 | 0.772379 | -0.000377585 | -0.000307439 |
| balanced_e90 | submission_e90_e72pareto_28925de5.csv | 5.47151 | -0.000250767 | -0.000214599 | 0.637513 | 0.348014 | 0.931241 | 0.65799 | -2.69324e-05 | 0.715784 | -0.000299838 | -0.000250999 |
| min_contam_e89 | submission_e89_e72decontam_00d7807f.csv | 5.19781 | -0.000235903 | -0.00019902 | 0.644757 | 0.356204 | 0.94492 | 0.635838 | -2.5896e-05 | 0.676361 | -0.00021606 | -0.000140452 |
| conservative_e85 | submission_e85_inverse_conflict_pruned_58b23ed1.csv | 4.59978 | -0.000207023 | -0.000181365 | 0.636952 | 0.339599 | 0.940523 | 0.649469 | -2.38758e-05 | 0.734771 | -0.00021606 | -0.000130361 |
| frontier | submission_mixmin_0c916bb4.csv | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  |  |

## E86/E90/E89/E85 Lens

| role | file | hidden_block_alignment_score | posterior_ce_delta_all_vs_mixmin | endpoint_ce_delta_all_vs_mixmin | posterior_direction_mass_agree | block_target_r2 | posterior_shift_topquartile_mass_lift | e72_direction_mass_agree | local_all_delta_vs_mixmin | local_e72_failed_contamination_index | local_hidden_q2s3_mean_minus_base | local_world_support_minus_base |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| noq2_contrast | submission_e87_noq2_source_consensus_a85c4e39.csv | 5.60519 | -0.000257196 | -0.000226515 | 0.639058 | 0.342148 | 0.940266 | 0.650503 | -2.69461e-05 | 0.730408 | -0.000254206 | -0.000171638 |
| max_upside_e86 | submission_e86_e85_consensus_a3f7c96f.csv | 5.56267 | -0.000255621 | -0.000223351 | 0.633337 | 0.352179 | 0.939023 | 0.668166 | -2.77059e-05 | 0.772379 | -0.000377585 | -0.000307439 |
| balanced_e90 | submission_e90_e72pareto_28925de5.csv | 5.47151 | -0.000250767 | -0.000214599 | 0.637513 | 0.348014 | 0.931241 | 0.65799 | -2.69324e-05 | 0.715784 | -0.000299838 | -0.000250999 |
| min_contam_e89 | submission_e89_e72decontam_00d7807f.csv | 5.19781 | -0.000235903 | -0.00019902 | 0.644757 | 0.356204 | 0.94492 | 0.635838 | -2.5896e-05 | 0.676361 | -0.00021606 | -0.000140452 |
| conservative_e85 | submission_e85_inverse_conflict_pruned_58b23ed1.csv | 4.59978 | -0.000207023 | -0.000181365 | 0.636952 | 0.339599 | 0.940523 | 0.649469 | -2.38758e-05 | 0.734771 | -0.00021606 | -0.000130361 |

## Best Posterior-Aligned Blocks

| role | hidden_block_id | n_rows | posterior_ce_delta_vs_mixmin | posterior_direction_agreement | mean_abs_logit_move | posterior_mean_abs_shift |
| --- | --- | --- | --- | --- | --- | --- |
| balanced_e90 | id08_b12 | 2 | -0.0014856 | 0.768226 | 0.00864542 | 0.147381 |
| balanced_e90 | id08_b6 | 2 | -0.000646619 | 0.645524 | 0.00699155 | 0.0824311 |
| balanced_e90 | id01_b2 | 14 | -0.00061267 | 0.845524 | 0.00647256 | 0.101772 |
| balanced_e90 | id08_b4 | 6 | -0.000574656 | 0.659835 | 0.00555551 | 0.103521 |
| balanced_e90 | id05_b8 | 2 | -0.000523132 | 0.996898 | 0.00502935 | 0.090076 |
| max_upside_e86 | id08_b12 | 2 | -0.0014856 | 0.768226 | 0.00864542 | 0.147381 |
| max_upside_e86 | id08_b6 | 2 | -0.000646619 | 0.645524 | 0.00699155 | 0.0824311 |
| max_upside_e86 | id01_b2 | 14 | -0.000616166 | 0.847077 | 0.00655093 | 0.101772 |
| max_upside_e86 | id08_b4 | 6 | -0.000603091 | 0.668325 | 0.00616159 | 0.103521 |
| max_upside_e86 | id05_b8 | 2 | -0.000523132 | 0.996898 | 0.00502935 | 0.090076 |
| min_contam_e89 | id08_b12 | 2 | -0.00128193 | 0.760339 | 0.00773636 | 0.147381 |
| min_contam_e89 | id08_b6 | 2 | -0.00066746 | 0.780565 | 0.0052947 | 0.0824311 |
| min_contam_e89 | id01_b2 | 14 | -0.000561862 | 0.835863 | 0.00583012 | 0.101772 |
| min_contam_e89 | id05_b8 | 2 | -0.000523132 | 0.996898 | 0.00502935 | 0.090076 |
| min_contam_e89 | id08_b10 | 4 | -0.000506953 | 0.809099 | 0.00477476 | 0.0919332 |

## Falsification Read

- Overall hidden-block alignment leader: `failed_e72`.
- Best posterior CE delta: `failed_e72`.
- Highest block-target movement R2: `min_contam_e89`.
- Since `failed_e72` is a known public-negative anchor, any representation score that ranks it first is not public-safe as a selector.
- E86 posterior CE delta `-0.000255621`, E72 mass agreement `0.668166`.
- E90 posterior CE delta `-0.000250767`, E72 mass agreement `0.657990`.
- E89 posterior CE delta `-0.000235903`, E72 mass agreement `0.635838`.

## Decision

H87 is not supported as a selector. The hidden-block posterior representation prefers the known public-negative E72 file, so this posterior is E72-tainted for submission ranking. Use it as a representation diagnostic, not as a public-safe target.

No E92 submission is materialized. This audit updates the ordering rationale for already materialized E86/E90/E89 sensors.
