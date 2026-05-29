# E83 Q2/S3-Energy Structural Gate Scan

## Observe

E82 showed that pure Q2/S3 movement is coherent across combo, hidden, world, and block stresses, but every evaluated row missed the margin gate.

## Wonder

Is Q2/S3 better used as a row-energy selector for broader structural movements than as the movement itself?

## Hypothesis

If Q2/S3 latent energy marks a real hidden sleep-state block, then older broad JEPA/block/raw movements should become safer when applied only on high-energy E82 rows. The inverse/not-top gate is a falsification control.

## Method

- Use `submission_mixmin_0c916bb4.csv` as the base.
- Build E82 row energy from the top 20 evaluated pure Q2/S3 grafts.
- Load compact-selected broad structural submissions from block consensus, rawcorrector, refine, microrefine, plus manual controls.
- Apply logit movement from each source file to mixmin under row gates, target scopes, and scales.
- Score combo first, then run hidden/world/block stress only on combo-promising rows.

## Energy Summary

| source | source_rows | source_preds | used_top_predictions | best_e82_tag | best_e82_all_delta | energy_mean | energy_p90 | energy_p99 | energy_max | nonzero_rows | source_summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e82_top20_q2s3_energy | 8402 | 8403 | 20 | e82_e76_delta_graft_q2s3_530bf861 | -7.90328e-06 | 0.00574936 | 0.0243902 | 0.0435103 | 0.0507276 | 77 | [{"source":"e72","source_rows":1051,"source_preds":4770},{"source":"e75","source_rows":120,"source_preds":121},{"source":"e76","source_rows":1894,"source_preds":2068}] |

## Gate Summary

| row_gate | target_scope | scale | rows | nonanchor_evaluated | strict | deployable | loose | structural_strict | structural_loose | best_all_delta_vs_mixmin | best_eval_all_delta_vs_mixmin | best_hidden_core | best_hidden_q2s3 | best_world |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e82_energy_top100 | all | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -8.93545e-06 | -8.93545e-06 | -0.00030666 | -0.000295857 | -0.000673957 |
| e82_energy_top50 | all | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -7.80901e-06 | -7.80901e-06 | -0.000218419 | -0.000278336 | -0.000529247 |
| e82_energy_top50 | s_all | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -7.02651e-06 | -7.02651e-06 | -0.000124787 | -0.000147404 | -0.0002258 |
| e82_energy_top100 | all | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.05832e-05 | -6.86132e-06 | -0.000205263 | -0.000198952 | -0.000450417 |
| e82_energy_top100 | s_all | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -6.85775e-06 | -6.85775e-06 | -0.000160548 | -0.000111811 | -0.000297976 |
| e82_energy_top50 | all | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -6.71498e-06 | -6.71498e-06 | -0.000164596 | -0.000210655 | -0.000397991 |
| all_rows | q2s3 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.95383e-06 | -5.95383e-06 | -0.000111727 | -0.000391043 | -0.000281016 |
| e82_energy_top100 | q2s3 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.95383e-06 | -5.95383e-06 | -0.000111727 | -0.000391043 | -0.000281016 |
| e82_energy_top250 | q2s3 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.95383e-06 | -5.95383e-06 | -0.000111727 | -0.000391043 | -0.000281016 |
| e82_energy_top500 | q2s3 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.95383e-06 | -5.95383e-06 | -0.000111727 | -0.000391043 | -0.000281016 |
| e82_energy_top50 | s_all | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.78414e-06 | -5.78414e-06 | -9.4081e-05 | -0.000111811 | -0.000170012 |
| e82_energy_top50 | q2s3 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.68377e-06 | -5.68377e-06 | -7.95245e-05 | -0.000278336 | -0.000170679 |
| e82_energy_top50 | q3_s2_s3_s4 | 1 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.68119e-06 | -5.68119e-06 | -9.88785e-05 | -0.000147404 | -0.00021636 |
| all_rows | q2s3 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.29554e-06 | -5.29554e-06 | -8.45307e-05 | -0.000295857 | -0.000211755 |
| e82_energy_top100 | q2s3 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.29554e-06 | -5.29554e-06 | -8.45307e-05 | -0.000295857 | -0.000211755 |
| e82_energy_top250 | q2s3 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.29554e-06 | -5.29554e-06 | -8.45307e-05 | -0.000295857 | -0.000211755 |
| e82_energy_top500 | q2s3 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.29554e-06 | -5.29554e-06 | -8.45307e-05 | -0.000295857 | -0.000211755 |
| e82_energy_top100 | s_all | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.04135e-05 | -5.05843e-06 | -0.000107455 | -7.53782e-05 | -0.000199222 |
| e82_energy_top50 | all | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -8.63134e-06 | -5.05151e-06 | -0.000110252 | -0.000141703 | -0.000266031 |
| e82_energy_top50 | q3_s2_s3_s4 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -4.88717e-06 | -4.88717e-06 | -7.46608e-05 | -0.000111811 | -0.000162947 |
| e82_energy_top50 | q2s3 | 0.75 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -4.87297e-06 | -4.87297e-06 | -6.0187e-05 | -0.000210655 | -0.000128743 |
| e82_energy_top50 | s_all | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.64845e-06 | -4.1824e-06 | -6.30471e-05 | -7.53782e-05 | -0.000113782 |
| e82_energy_top100 | q3_s2_s3_s4 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -4.15092e-06 | -4.15092e-06 | -7.86797e-05 | -7.53782e-05 | -0.000146198 |
| all_rows | q2s3 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.08074e-05 | -4.11832e-06 | -5.68435e-05 | -0.000198952 | -0.000141831 |
| e82_energy_top100 | q2s3 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -4.11832e-06 | -4.11832e-06 | -5.68435e-05 | -0.000198952 | -0.000141831 |
| e82_energy_top250 | q2s3 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.08074e-05 | -4.11832e-06 | -5.68435e-05 | -0.000198952 | -0.000141831 |
| e82_energy_top500 | q2s3 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.08074e-05 | -4.11832e-06 | -5.68435e-05 | -0.000198952 | -0.000141831 |
| e82_energy_top100 | all | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.27897e-05 | -3.93561e-06 | -0.000103043 | -0.000100332 | -0.000225763 |
| e82_energy_top50 | q3_s2_s3_s4 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -3.69596e-06 | -3.69596e-06 | -5.01081e-05 | -7.53782e-05 | -0.000109083 |
| e82_energy_top50 | q2s3 | 0.5 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -3.67e-06 | -3.67e-06 | -4.04865e-05 | -0.000141703 | -8.63172e-05 |
| e82_energy_top50 | all | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -8.07746e-06 | -2.85188e-06 | -5.53859e-05 | -7.14835e-05 | -0.000133366 |
| e82_energy_top100 | s_all | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -8.91524e-06 | -2.73874e-06 | -5.39391e-05 | -3.81069e-05 | -9.98962e-05 |
| all_rows | q2s3 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.00588e-05 | -2.39284e-06 | -2.86662e-05 | -0.000100332 | -7.12456e-05 |
| e82_energy_top100 | q2s3 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -3.66751e-06 | -2.39284e-06 | -2.86662e-05 | -0.000100332 | -7.12456e-05 |
| e82_energy_top250 | q2s3 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.00588e-05 | -2.39284e-06 | -2.86662e-05 | -0.000100332 | -7.12456e-05 |
| e82_energy_top500 | q2s3 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -1.00588e-05 | -2.39284e-06 | -2.86662e-05 | -0.000100332 | -7.12456e-05 |
| e82_energy_top100 | q3_s2_s3_s4 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -4.28387e-06 | -2.38174e-06 | -3.95574e-05 | -3.81069e-05 | -7.33929e-05 |
| e82_energy_top50 | s_all | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -5.00209e-06 | -2.25974e-06 | -3.16865e-05 | -3.81069e-05 | -5.7111e-05 |
| e82_energy_top50 | q3_s2_s3_s4 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -2.35467e-06 | -2.05815e-06 | -2.52209e-05 | -3.81069e-05 | -5.47666e-05 |
| e82_energy_top50 | q2s3 | 0.25 | 31 | 1 | 0 | 0 | 1 | 0 | 1 | -2.0502e-06 | -2.0502e-06 | -2.04238e-05 | -7.14835e-05 | -4.34024e-05 |

## Source Summary

| source_file | source_table | rows | nonanchor_evaluated | strict | deployable | loose | structural_strict | structural_loose | best_eval_all_delta_vs_mixmin | best_all_delta_vs_mixmin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_gate_299a7455.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.50517e-05 | -3.50517e-05 |
| submission_jepa_block_consensus_gate_5738e95e.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.50487e-05 | -3.50487e-05 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.50335e-05 | -3.50335e-05 |
| submission_jepa_block_consensus_gate_aa97b049.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.50331e-05 | -3.50331e-05 |
| submission_jepa_block_consensus_gate_76aff53b.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.5007e-05 | -3.5007e-05 |
| submission_jepa_block_consensus_gate_c28e6346.csv | jepa_block_consensus_gate_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.50053e-05 | -3.50053e-05 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 6 | -3.49659e-05 | -3.49659e-05 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | manual_controls | 120 | 23 | 0 | 0 | 0 | 0 | 0 | -3.49333e-05 | -3.49333e-05 |
| submission_jepa_block_consensus_gate_cf9e36f2.csv | manual_controls | 120 | 23 | 0 | 0 | 0 | 0 | 3 | -3.48281e-05 | -3.48281e-05 |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 6 | -3.48146e-05 | -3.48146e-05 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 23 | 0 | 0 | 0 | 0 | 6 | -3.48141e-05 | -3.48141e-05 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.48135e-05 | -3.48135e-05 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.48129e-05 | -3.48129e-05 |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.4773e-05 | -3.4773e-05 |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47721e-05 | -3.47721e-05 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47713e-05 | -3.47713e-05 |
| submission_jepa_block_consensus_rawcorr_refine_a4c875f3.csv | jepa_block_consensus_rawcorrector_refine_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.4771e-05 | -3.4771e-05 |
| submission_jepa_block_consensus_rawcorr_micro_d9851c05.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47704e-05 | -3.47704e-05 |
| submission_jepa_block_consensus_rawcorr_micro_cc5b3053.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47695e-05 | -3.47695e-05 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | jepa_block_consensus_rawcorrector_microrefine_shortlist.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47686e-05 | -3.47686e-05 |
| submission_jepa_block_consensus_rawcorr_refine_a2f628d8.csv | manual_controls | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.47532e-05 | -3.47532e-05 |
| submission_jepa_block_consensus_rawcorr_b411b06d.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.46988e-05 | -3.46988e-05 |
| submission_jepa_block_consensus_rawcorr_4fd8bab2.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.469e-05 | -3.469e-05 |
| submission_jepa_block_consensus_rawcorr_01d781e0.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.46879e-05 | -3.46879e-05 |
| submission_jepa_block_consensus_rawcorr_224f8a38.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.46752e-05 | -3.46752e-05 |
| submission_jepa_block_consensus_rawcorr_fd06a9c9.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.46588e-05 | -3.46588e-05 |
| submission_jepa_block_consensus_rawcorr_645f7245.csv | jepa_block_consensus_rawcorrector_selected.csv | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.44146e-05 | -3.44146e-05 |
| submission_jepa_block_consensus_rawcorr_7cc6473a.csv | manual_controls | 120 | 22 | 0 | 0 | 0 | 0 | 6 | -3.43301e-05 | -3.43301e-05 |
| submission_jepa_energy_ensemble_5a01b623.csv | manual_controls | 120 | 16 | 0 | 0 | 0 | 0 | 3 | -3.28752e-05 | -3.28752e-05 |
| submission_hiddenblock_seqmotif_cellgate_b8c9ae2f.csv | manual_controls | 120 | 15 | 0 | 0 | 0 | 0 | 3 | -3.07505e-05 | -3.07505e-05 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | manual_controls | 116 | 42 | 0 | 0 | 40 | 0 | 42 | -8.93545e-06 | -1.05458e-05 |

## E70 Strict Rows

None.

## Structural Strict Rows

None.

## E70 Loose Rows

| source_file | row_gate | target_scope | scale | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | strict_gate | structural_strict_gate | loose_gate | structural_loose_gate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | all | 0.75 | -8.93545e-06 | -8.93545e-06 | 3 | 3 | -0.00030666 | -0.000295857 | -0.000673957 | -0.000332829 | False | False | True | True | 0.00269206 | 0.00360267 | e83_e82_energy_top100_all_0.75_fc354223 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | all | 1 | -7.80901e-06 | -7.80901e-06 | 3 | 3 | -0.000218419 | -0.000278336 | -0.000529247 | -0.000261621 | False | False | True | True | 0.00209089 | 0.00356724 | e83_e82_energy_top50_all_1.00_52b8f72c |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | s_all | 1 | -7.02651e-06 | -7.02651e-06 | 3 | 3 | -0.000124787 | -0.000147404 | -0.0002258 | -0.000114641 | False | False | True | True | 0.00139275 | 0.00264052 | e83_e82_energy_top50_s_all_1.00_00b01914 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | all | 0.5 | -6.86132e-06 | -6.86132e-06 | 3 | 3 | -0.000205263 | -0.000198952 | -0.000450417 | -0.00022271 | False | False | True | True | 0.00179471 | 0.00240178 | e83_e82_energy_top100_all_0.50_62a7e1ec |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | s_all | 0.75 | -6.85775e-06 | -6.85775e-06 | 3 | 3 | -0.000160548 | -0.000111811 | -0.000297976 | -0.000155958 | False | False | True | True | 0.00154765 | 0.00198039 | e83_e82_energy_top100_s_all_0.75_4bcdf406 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | all | 0.75 | -6.71498e-06 | -6.71498e-06 | 3 | 3 | -0.000164596 | -0.000210655 | -0.000397991 | -0.000196998 | False | False | True | True | 0.00156816 | 0.00267543 | e83_e82_energy_top50_all_0.75_3d859632 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top250 | q2s3 | 1 | -5.95383e-06 | -5.95383e-06 | 3 | 3 | -0.000111727 | -0.000391043 | -0.000281016 | -0.000144038 | False | False | True | True | 0.00137245 | 0.00480356 | e83_e82_energy_top250_q2s3_1.00_69dd12a8 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top500 | q2s3 | 1 | -5.95383e-06 | -5.95383e-06 | 3 | 3 | -0.000111727 | -0.000391043 | -0.000281016 | -0.000144038 | False | False | True | True | 0.00137245 | 0.00480356 | e83_e82_energy_top500_q2s3_1.00_69dd12a8 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | all_rows | q2s3 | 1 | -5.95383e-06 | -5.95383e-06 | 3 | 3 | -0.000111727 | -0.000391043 | -0.000281016 | -0.000144038 | False | False | True | True | 0.00137245 | 0.00480356 | e83_all_rows_q2s3_1.00_69dd12a8 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | q2s3 | 1 | -5.95383e-06 | -5.95383e-06 | 3 | 3 | -0.000111727 | -0.000391043 | -0.000281016 | -0.000144038 | False | False | True | True | 0.00137245 | 0.00480356 | e83_e82_energy_top100_q2s3_1.00_69dd12a8 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | s_all | 0.75 | -5.78414e-06 | -5.78414e-06 | 3 | 3 | -9.4081e-05 | -0.000111811 | -0.000170012 | -8.64711e-05 | False | False | True | True | 0.00104456 | 0.00198039 | e83_e82_energy_top50_s_all_0.75_43e8ea12 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | q2s3 | 1 | -5.68377e-06 | -5.68377e-06 | 3 | 3 | -7.95245e-05 | -0.000278336 | -0.000170679 | -6.64385e-05 | False | False | True | True | 0.00101921 | 0.00356724 | e83_e82_energy_top50_q2s3_1.00_5240c5db |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | q3_s2_s3_s4 | 1 | -5.68119e-06 | -5.68119e-06 | 3 | 3 | -9.88785e-05 | -0.000147404 | -0.00021636 | -0.000118296 | False | False | True | True | 0.00135034 | 0.00264052 | e83_e82_energy_top50_q3_s2_s3_s4_1.00_36cabdcb |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | all_rows | q2s3 | 0.75 | -5.29554e-06 | -5.29554e-06 | 3 | 3 | -8.45307e-05 | -0.000295857 | -0.000211755 | -0.000108764 | False | False | True | True | 0.00102933 | 0.00360267 | e83_all_rows_q2s3_0.75_a12c348b |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | q2s3 | 0.75 | -5.29554e-06 | -5.29554e-06 | 3 | 3 | -8.45307e-05 | -0.000295857 | -0.000211755 | -0.000108764 | False | False | True | True | 0.00102933 | 0.00360267 | e83_e82_energy_top100_q2s3_0.75_a12c348b |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top250 | q2s3 | 0.75 | -5.29554e-06 | -5.29554e-06 | 3 | 3 | -8.45307e-05 | -0.000295857 | -0.000211755 | -0.000108764 | False | False | True | True | 0.00102933 | 0.00360267 | e83_e82_energy_top250_q2s3_0.75_a12c348b |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top500 | q2s3 | 0.75 | -5.29554e-06 | -5.29554e-06 | 3 | 3 | -8.45307e-05 | -0.000295857 | -0.000211755 | -0.000108764 | False | False | True | True | 0.00102933 | 0.00360267 | e83_e82_energy_top500_q2s3_0.75_a12c348b |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | s_all | 0.5 | -5.05843e-06 | -5.05843e-06 | 3 | 3 | -0.000107455 | -7.53782e-05 | -0.000199222 | -0.000104395 | False | False | True | True | 0.00103176 | 0.00132026 | e83_e82_energy_top100_s_all_0.50_650ca5b6 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | all | 0.5 | -5.05151e-06 | -5.05151e-06 | 3 | 3 | -0.000110252 | -0.000141703 | -0.000266031 | -0.000131853 | False | False | True | True | 0.00104544 | 0.00178362 | e83_e82_energy_top50_all_0.50_20fea71e |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | q3_s2_s3_s4 | 0.75 | -4.88717e-06 | -4.88717e-06 | 3 | 3 | -7.46608e-05 | -0.000111811 | -0.000162947 | -8.9224e-05 | False | False | True | True | 0.00101275 | 0.00198039 | e83_e82_energy_top50_q3_s2_s3_s4_0.75_f4fa5119 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | q2s3 | 0.75 | -4.87297e-06 | -4.87297e-06 | 3 | 3 | -6.0187e-05 | -0.000210655 | -0.000128743 | -5.03725e-05 | False | False | True | True | 0.000764409 | 0.00267543 | e83_e82_energy_top50_q2s3_0.75_588bb72f |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top50 | s_all | 0.5 | -4.1824e-06 | -4.1824e-06 | 3 | 3 | -6.30471e-05 | -7.53782e-05 | -0.000113782 | -5.79738e-05 | False | False | True | True | 0.000696375 | 0.00132026 | e83_e82_energy_top50_s_all_0.50_c681f0a8 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | q3_s2_s3_s4 | 0.5 | -4.15092e-06 | -4.15092e-06 | 3 | 3 | -7.86797e-05 | -7.53782e-05 | -0.000146198 | -9.27306e-05 | False | False | True | True | 0.000990473 | 0.00132026 | e83_e82_energy_top100_q3_s2_s3_s4_0.50_9c982a76 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | all_rows | q2s3 | 0.5 | -4.11832e-06 | -4.11832e-06 | 3 | 3 | -5.68435e-05 | -0.000198952 | -0.000141831 | -7.2999e-05 | False | False | True | True | 0.000686223 | 0.00240178 | e83_all_rows_q2s3_0.50_563a1a00 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e82_energy_top100 | q2s3 | 0.5 | -4.11832e-06 | -4.11832e-06 | 3 | 3 | -5.68435e-05 | -0.000198952 | -0.000141831 | -7.2999e-05 | False | False | True | True | 0.000686223 | 0.00240178 | e83_e82_energy_top100_q2s3_0.50_563a1a00 |

## Structural Loose Rows

| source_file | row_gate | target_scope | scale | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | strict_gate | structural_strict_gate | loose_gate | structural_loose_gate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.5291e-05 | -2.5291e-05 | 2 | 2 | -0.000182128 | 0 | -3.31539e-05 | -3.08454e-05 | False | False | False | True | 0.0087357 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_903f64a6 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | all_rows | non_q2s3 | 0.25 | -2.5291e-05 | -2.5291e-05 | 2 | 2 | -0.000182128 | 0 | -3.31539e-05 | -3.08454e-05 | False | False | False | True | 0.0087357 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_903f64a6 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.5291e-05 | -2.5291e-05 | 2 | 2 | -0.000182128 | 0 | -3.31539e-05 | -3.08454e-05 | False | False | False | True | 0.0087357 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_903f64a6 |
| submission_jepa_block_consensus_gate_299a7455.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.52257e-05 | -2.52257e-05 | 2 | 2 | -0.000160738 | 0 | -5.29831e-06 | -8.44195e-06 | False | False | False | True | 0.00880391 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_c41df1a9 |
| submission_jepa_block_consensus_gate_299a7455.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.52257e-05 | -2.52257e-05 | 2 | 2 | -0.000160738 | 0 | -5.29831e-06 | -8.44195e-06 | False | False | False | True | 0.00880391 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_c41df1a9 |
| submission_jepa_block_consensus_gate_299a7455.csv | all_rows | non_q2s3 | 0.25 | -2.52257e-05 | -2.52257e-05 | 2 | 2 | -0.000160738 | 0 | -5.29831e-06 | -8.44195e-06 | False | False | False | True | 0.00880391 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_c41df1a9 |
| submission_jepa_block_consensus_gate_5738e95e.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.52233e-05 | -2.52233e-05 | 2 | 2 | -0.000160762 | 0 | -5.17967e-06 | -8.36238e-06 | False | False | False | True | 0.00880374 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_dcb21c92 |
| submission_jepa_block_consensus_gate_5738e95e.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.52233e-05 | -2.52233e-05 | 2 | 2 | -0.000160762 | 0 | -5.17967e-06 | -8.36238e-06 | False | False | False | True | 0.00880374 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_dcb21c92 |
| submission_jepa_block_consensus_gate_5738e95e.csv | all_rows | non_q2s3 | 0.25 | -2.52233e-05 | -2.52233e-05 | 2 | 2 | -0.000160762 | 0 | -5.17967e-06 | -8.36238e-06 | False | False | False | True | 0.00880374 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_dcb21c92 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.52154e-05 | -2.52154e-05 | 2 | 2 | -0.000160781 | 0 | -5.39093e-06 | -8.57561e-06 | False | False | False | True | 0.00880343 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_431a8264 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.52154e-05 | -2.52154e-05 | 2 | 2 | -0.000160781 | 0 | -5.39093e-06 | -8.57561e-06 | False | False | False | True | 0.00880343 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_431a8264 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | all_rows | non_q2s3 | 0.25 | -2.52154e-05 | -2.52154e-05 | 2 | 2 | -0.000160781 | 0 | -5.39093e-06 | -8.57561e-06 | False | False | False | True | 0.00880343 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_431a8264 |
| submission_jepa_block_consensus_gate_aa97b049.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.52146e-05 | -2.52146e-05 | 2 | 2 | -0.00016069 | 0 | -5.44066e-06 | -8.64615e-06 | False | False | False | True | 0.00880333 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_3432ad1b |
| submission_jepa_block_consensus_gate_aa97b049.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.52146e-05 | -2.52146e-05 | 2 | 2 | -0.00016069 | 0 | -5.44066e-06 | -8.64615e-06 | False | False | False | True | 0.00880333 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_3432ad1b |
| submission_jepa_block_consensus_gate_aa97b049.csv | all_rows | non_q2s3 | 0.25 | -2.52146e-05 | -2.52146e-05 | 2 | 2 | -0.00016069 | 0 | -5.44066e-06 | -8.64615e-06 | False | False | False | True | 0.00880333 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_3432ad1b |
| submission_jepa_block_consensus_gate_c28e6346.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.51996e-05 | -2.51996e-05 | 2 | 2 | -0.000160717 | 0 | -5.62976e-06 | -8.92799e-06 | False | False | False | True | 0.00880177 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_a31f8863 |
| submission_jepa_block_consensus_gate_c28e6346.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.51996e-05 | -2.51996e-05 | 2 | 2 | -0.000160717 | 0 | -5.62976e-06 | -8.92799e-06 | False | False | False | True | 0.00880177 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_a31f8863 |
| submission_jepa_block_consensus_gate_c28e6346.csv | all_rows | non_q2s3 | 0.25 | -2.51996e-05 | -2.51996e-05 | 2 | 2 | -0.000160717 | 0 | -5.62976e-06 | -8.92799e-06 | False | False | False | True | 0.00880177 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_a31f8863 |
| submission_jepa_block_consensus_gate_76aff53b.csv | all_rows | non_q2s3 | 0.25 | -2.51991e-05 | -2.51991e-05 | 2 | 2 | -0.000160637 | 0 | -5.54978e-06 | -8.83557e-06 | False | False | False | True | 0.00880197 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_af9c7fa8 |
| submission_jepa_block_consensus_gate_76aff53b.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.51991e-05 | -2.51991e-05 | 2 | 2 | -0.000160637 | 0 | -5.54978e-06 | -8.83557e-06 | False | False | False | True | 0.00880197 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_af9c7fa8 |
| submission_jepa_block_consensus_gate_76aff53b.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.51991e-05 | -2.51991e-05 | 2 | 2 | -0.000160637 | 0 | -5.54978e-06 | -8.83557e-06 | False | False | False | True | 0.00880197 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_af9c7fa8 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | all_rows | non_q2s3 | 0.25 | -2.51921e-05 | -2.51921e-05 | 2 | 2 | -0.000193465 | 0 | -5.11412e-05 | -4.50393e-05 | False | False | False | True | 0.00871799 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_64795ff4 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | e82_energy_top250 | non_q2s3 | 0.25 | -2.51921e-05 | -2.51921e-05 | 2 | 2 | -0.000193465 | 0 | -5.11412e-05 | -4.50393e-05 | False | False | False | True | 0.00871799 | 5.99839e-17 | e83_e82_energy_top250_non_q2s3_0.25_64795ff4 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | e82_energy_top500 | non_q2s3 | 0.25 | -2.51921e-05 | -2.51921e-05 | 2 | 2 | -0.000193465 | 0 | -5.11412e-05 | -4.50393e-05 | False | False | False | True | 0.00871799 | 5.99839e-17 | e83_e82_energy_top500_non_q2s3_0.25_64795ff4 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | all_rows | non_q2s3 | 0.25 | -2.51908e-05 | -2.51908e-05 | 2 | 2 | -0.000192724 | 0 | -5.02472e-05 | -4.43448e-05 | False | False | False | True | 0.00871939 | 5.99839e-17 | e83_all_rows_non_q2s3_0.25_330b86b7 |

## Best Evaluated Rows

| source_file | row_gate | target_scope | scale | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | strict_gate | structural_strict_gate | loose_gate | structural_loose_gate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_gate_299a7455.csv | all_rows | all | 0.25 | -3.50517e-05 | -3.50517e-05 | 2 | 2 | -3.41025e-05 | 0.000443224 | 0.000252206 | 0.000187718 | False | False | False | False | 0.0117957 | 0.0104713 | e83_all_rows_all_0.25_6890f7d7 |
| submission_jepa_block_consensus_gate_299a7455.csv | e82_energy_top250 | all | 0.25 | -3.50517e-05 | -3.50517e-05 | 2 | 2 | -3.41025e-05 | 0.000443224 | 0.000252206 | 0.000187718 | False | False | False | False | 0.0117957 | 0.0104713 | e83_e82_energy_top250_all_0.25_6890f7d7 |
| submission_jepa_block_consensus_gate_299a7455.csv | e82_energy_top500 | all | 0.25 | -3.50517e-05 | -3.50517e-05 | 2 | 2 | -3.41025e-05 | 0.000443224 | 0.000252206 | 0.000187718 | False | False | False | False | 0.0117957 | 0.0104713 | e83_e82_energy_top500_all_0.25_6890f7d7 |
| submission_jepa_block_consensus_gate_5738e95e.csv | all_rows | all | 0.25 | -3.50487e-05 | -3.50487e-05 | 2 | 2 | -3.42105e-05 | 0.000442929 | 0.000252083 | 0.000187702 | False | False | False | False | 0.0117947 | 0.0104683 | e83_all_rows_all_0.25_78608210 |
| submission_jepa_block_consensus_gate_5738e95e.csv | e82_energy_top250 | all | 0.25 | -3.50487e-05 | -3.50487e-05 | 2 | 2 | -3.42105e-05 | 0.000442929 | 0.000252083 | 0.000187702 | False | False | False | False | 0.0117947 | 0.0104683 | e83_e82_energy_top250_all_0.25_78608210 |
| submission_jepa_block_consensus_gate_5738e95e.csv | e82_energy_top500 | all | 0.25 | -3.50487e-05 | -3.50487e-05 | 2 | 2 | -3.42105e-05 | 0.000442929 | 0.000252083 | 0.000187702 | False | False | False | False | 0.0117947 | 0.0104683 | e83_e82_energy_top500_all_0.25_78608210 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | all_rows | all | 0.25 | -3.50335e-05 | -3.50335e-05 | 2 | 2 | -3.42108e-05 | 0.000442995 | 0.000251641 | 0.000187147 | False | False | False | False | 0.0117936 | 0.0104656 | e83_all_rows_all_0.25_19b90367 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | e82_energy_top250 | all | 0.25 | -3.50335e-05 | -3.50335e-05 | 2 | 2 | -3.42108e-05 | 0.000442995 | 0.000251641 | 0.000187147 | False | False | False | False | 0.0117936 | 0.0104656 | e83_e82_energy_top250_all_0.25_19b90367 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | e82_energy_top500 | all | 0.25 | -3.50335e-05 | -3.50335e-05 | 2 | 2 | -3.42108e-05 | 0.000442995 | 0.000251641 | 0.000187147 | False | False | False | False | 0.0117936 | 0.0104656 | e83_e82_energy_top500_all_0.25_19b90367 |
| submission_jepa_block_consensus_gate_aa97b049.csv | all_rows | all | 0.25 | -3.50331e-05 | -3.50331e-05 | 2 | 2 | -3.41173e-05 | 0.000443005 | 0.000251779 | 0.00018714 | False | False | False | False | 0.0117936 | 0.0104661 | e83_all_rows_all_0.25_2ce191a0 |
| submission_jepa_block_consensus_gate_aa97b049.csv | e82_energy_top250 | all | 0.25 | -3.50331e-05 | -3.50331e-05 | 2 | 2 | -3.41173e-05 | 0.000443005 | 0.000251779 | 0.00018714 | False | False | False | False | 0.0117936 | 0.0104661 | e83_e82_energy_top250_all_0.25_2ce191a0 |
| submission_jepa_block_consensus_gate_aa97b049.csv | e82_energy_top500 | all | 0.25 | -3.50331e-05 | -3.50331e-05 | 2 | 2 | -3.41173e-05 | 0.000443005 | 0.000251779 | 0.00018714 | False | False | False | False | 0.0117936 | 0.0104661 | e83_e82_energy_top500_all_0.25_2ce191a0 |
| submission_jepa_block_consensus_gate_76aff53b.csv | all_rows | all | 0.25 | -3.5007e-05 | -3.5007e-05 | 2 | 2 | -3.41959e-05 | 0.000442542 | 0.000251273 | 0.000186879 | False | False | False | False | 0.0117907 | 0.0104604 | e83_all_rows_all_0.25_09e86708 |
| submission_jepa_block_consensus_gate_76aff53b.csv | e82_energy_top250 | all | 0.25 | -3.5007e-05 | -3.5007e-05 | 2 | 2 | -3.41959e-05 | 0.000442542 | 0.000251273 | 0.000186879 | False | False | False | False | 0.0117907 | 0.0104604 | e83_e82_energy_top250_all_0.25_09e86708 |
| submission_jepa_block_consensus_gate_76aff53b.csv | e82_energy_top500 | all | 0.25 | -3.5007e-05 | -3.5007e-05 | 2 | 2 | -3.41959e-05 | 0.000442542 | 0.000251273 | 0.000186879 | False | False | False | False | 0.0117907 | 0.0104604 | e83_e82_energy_top500_all_0.25_09e86708 |
| submission_jepa_block_consensus_gate_c28e6346.csv | e82_energy_top500 | all | 0.25 | -3.50053e-05 | -3.50053e-05 | 2 | 2 | -3.42594e-05 | 0.0004426 | 0.000251088 | 0.000186958 | False | False | False | False | 0.0117905 | 0.0104606 | e83_e82_energy_top500_all_0.25_d691a3ca |
| submission_jepa_block_consensus_gate_c28e6346.csv | all_rows | all | 0.25 | -3.50053e-05 | -3.50053e-05 | 2 | 2 | -3.42594e-05 | 0.0004426 | 0.000251088 | 0.000186958 | False | False | False | False | 0.0117905 | 0.0104606 | e83_all_rows_all_0.25_d691a3ca |
| submission_jepa_block_consensus_gate_c28e6346.csv | e82_energy_top250 | all | 0.25 | -3.50053e-05 | -3.50053e-05 | 2 | 2 | -3.42594e-05 | 0.0004426 | 0.000251088 | 0.000186958 | False | False | False | False | 0.0117905 | 0.0104606 | e83_e82_energy_top250_all_0.25_d691a3ca |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | all_rows | all | 0.25 | -3.49659e-05 | -3.49659e-05 | 2 | 2 | -5.80583e-05 | 0.000434244 | 0.000217644 | 0.000162209 | False | False | False | False | 0.0117016 | 0.0103806 | e83_all_rows_all_0.25_a742b7da |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | e82_energy_top250 | all | 0.25 | -3.49659e-05 | -3.49659e-05 | 2 | 2 | -5.80583e-05 | 0.000434244 | 0.000217644 | 0.000162209 | False | False | False | False | 0.0117016 | 0.0103806 | e83_e82_energy_top250_all_0.25_a742b7da |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | e82_energy_top500 | all | 0.25 | -3.49659e-05 | -3.49659e-05 | 2 | 2 | -5.80583e-05 | 0.000434244 | 0.000217644 | 0.000162209 | False | False | False | False | 0.0117016 | 0.0103806 | e83_e82_energy_top500_all_0.25_a742b7da |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | all_rows | all | 0.25 | -3.49333e-05 | -3.49333e-05 | 2 | 2 | -4.63451e-05 | 0.000442134 | 0.000325808 | 0.000246557 | False | False | False | False | 0.0114036 | 0.0103096 | e83_all_rows_all_0.25_ff459c1d |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | e82_energy_top250 | all | 0.25 | -3.49333e-05 | -3.49333e-05 | 2 | 2 | -4.63451e-05 | 0.000442134 | 0.000325808 | 0.000246557 | False | False | False | False | 0.0114036 | 0.0103096 | e83_e82_energy_top250_all_0.25_ff459c1d |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | e82_energy_top500 | all | 0.25 | -3.49333e-05 | -3.49333e-05 | 2 | 2 | -4.63451e-05 | 0.000442134 | 0.000325808 | 0.000246557 | False | False | False | False | 0.0114036 | 0.0103096 | e83_e82_energy_top500_all_0.25_ff459c1d |
| submission_jepa_block_consensus_gate_cf9e36f2.csv | e82_energy_top250 | all | 0.25 | -3.48281e-05 | -3.48281e-05 | 2 | 2 | -3.80438e-05 | 0.000446032 | 0.000241 | 0.000177631 | False | False | False | False | 0.0118074 | 0.0104718 | e83_e82_energy_top250_all_0.25_6fb7817c |
| submission_jepa_block_consensus_gate_cf9e36f2.csv | all_rows | all | 0.25 | -3.48281e-05 | -3.48281e-05 | 2 | 2 | -3.80438e-05 | 0.000446032 | 0.000241 | 0.000177631 | False | False | False | False | 0.0118074 | 0.0104718 | e83_all_rows_all_0.25_6fb7817c |
| submission_jepa_block_consensus_gate_cf9e36f2.csv | e82_energy_top500 | all | 0.25 | -3.48281e-05 | -3.48281e-05 | 2 | 2 | -3.80438e-05 | 0.000446032 | 0.000241 | 0.000177631 | False | False | False | False | 0.0118074 | 0.0104718 | e83_e82_energy_top500_all_0.25_6fb7817c |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | all_rows | all | 0.25 | -3.48146e-05 | -3.48146e-05 | 2 | 2 | -6.82911e-05 | 0.000430326 | 0.000201438 | 0.000149028 | False | False | False | False | 0.0116774 | 0.0103421 | e83_all_rows_all_0.25_76d122ab |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | e82_energy_top250 | all | 0.25 | -3.48146e-05 | -3.48146e-05 | 2 | 2 | -6.82911e-05 | 0.000430326 | 0.000201438 | 0.000149028 | False | False | False | False | 0.0116774 | 0.0103421 | e83_e82_energy_top250_all_0.25_76d122ab |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | e82_energy_top500 | all | 0.25 | -3.48146e-05 | -3.48146e-05 | 2 | 2 | -6.82911e-05 | 0.000430326 | 0.000201438 | 0.000149028 | False | False | False | False | 0.0116774 | 0.0103421 | e83_e82_energy_top500_all_0.25_76d122ab |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | all_rows | all | 0.25 | -3.48141e-05 | -3.48141e-05 | 2 | 2 | -6.91625e-05 | 0.00042987 | 0.000200319 | 0.000148207 | False | False | False | False | 0.0116749 | 0.010339 | e83_all_rows_all_0.25_bd186ab2 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | e82_energy_top250 | all | 0.25 | -3.48141e-05 | -3.48141e-05 | 2 | 2 | -6.91625e-05 | 0.00042987 | 0.000200319 | 0.000148207 | False | False | False | False | 0.0116749 | 0.010339 | e83_e82_energy_top250_all_0.25_bd186ab2 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | e82_energy_top500 | all | 0.25 | -3.48141e-05 | -3.48141e-05 | 2 | 2 | -6.91625e-05 | 0.00042987 | 0.000200319 | 0.000148207 | False | False | False | False | 0.0116749 | 0.010339 | e83_e82_energy_top500_all_0.25_bd186ab2 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | e82_energy_top500 | all | 0.25 | -3.48135e-05 | -3.48135e-05 | 2 | 2 | -7.00339e-05 | 0.000429414 | 0.000199199 | 0.000147387 | False | False | False | False | 0.0116725 | 0.0103359 | e83_e82_energy_top500_all_0.25_4d5fac04 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | all_rows | all | 0.25 | -3.48135e-05 | -3.48135e-05 | 2 | 2 | -7.00339e-05 | 0.000429414 | 0.000199199 | 0.000147387 | False | False | False | False | 0.0116725 | 0.0103359 | e83_all_rows_all_0.25_4d5fac04 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | e82_energy_top250 | all | 0.25 | -3.48135e-05 | -3.48135e-05 | 2 | 2 | -7.00339e-05 | 0.000429414 | 0.000199199 | 0.000147387 | False | False | False | False | 0.0116725 | 0.0103359 | e83_e82_energy_top250_all_0.25_4d5fac04 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | e82_energy_top500 | all | 0.25 | -3.48129e-05 | -3.48129e-05 | 2 | 2 | -7.09052e-05 | 0.000428958 | 0.000198079 | 0.000146567 | False | False | False | False | 0.0116703 | 0.010333 | e83_e82_energy_top500_all_0.25_009f2c5c |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | all_rows | all | 0.25 | -3.48129e-05 | -3.48129e-05 | 2 | 2 | -7.09052e-05 | 0.000428958 | 0.000198079 | 0.000146567 | False | False | False | False | 0.0116703 | 0.010333 | e83_all_rows_all_0.25_009f2c5c |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | e82_energy_top250 | all | 0.25 | -3.48129e-05 | -3.48129e-05 | 2 | 2 | -7.09052e-05 | 0.000428958 | 0.000198079 | 0.000146567 | False | False | False | False | 0.0116703 | 0.010333 | e83_e82_energy_top250_all_0.25_009f2c5c |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | e82_energy_top500 | all | 0.25 | -3.4773e-05 | -3.4773e-05 | 2 | 2 | -7.43252e-05 | 0.000426466 | 0.000193507 | 0.00014366 | False | False | False | False | 0.0116556 | 0.0103177 | e83_e82_energy_top500_all_0.25_8cc091fb |

## Decision

No strict/deployable E70 candidate was materialized.

If structural strict rows exist without E70 strict rows, they are diagnostic only: the broader movement may repair hidden-core stress while failing the Q2/S3-specific block guard.