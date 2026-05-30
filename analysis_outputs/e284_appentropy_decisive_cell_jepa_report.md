# E284 App-Entropy Decisive-Cell JEPA Audit

## Question

Can the validated app-entropy human/social state help learn the hidden Q3/S4 decisive-cell target, rather than directly moving Q3 or re-ranking E247 smoothing cells?

## Feature Views

| view | feature_count | app_feature_count | interaction_count |
| --- | --- | --- | --- |
| latent_no_targetid_featnn1_appstate | 263 | 3 | 0 |
| latent_no_targetid_featnn1_appstate_inter | 273 | 13 | 10 |
| latent_no_targetid_featnn1_appstory_inter | 284 | 24 | 20 |

## OOF Comparison Versus E249 Feature-NN1 Baseline

| view | model | pairs | mean_delta_loss | median_delta_loss | p10_delta_loss | mean_delta_tail_auc | median_delta_tail_auc | promoted_by_app | demoted_by_app | app_better_loss_rate | app_better_tail_auc_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| latent_no_targetid_featnn1_appstate_inter | lr_l2_c0p10 | 624 | -0.000085269 | -0.000080361 | -0.000400437 | 0.003713380 | 0.003196066 | 22 | 3 | 0.650641026 | 0.687500000 |
| latent_no_targetid_featnn1_appstory_inter | lr_l2_c0p10 | 624 | -0.000077312 | -0.000076219 | -0.000408373 | 0.002860060 | 0.002666190 | 22 | 6 | 0.615384615 | 0.562500000 |
| latent_no_targetid_featnn1_appstate | hgb_shallow | 624 | -0.000015102 | -0.000005934 | -0.000332428 | 0.002777693 | 0.001302307 | 38 | 44 | 0.519230769 | 0.812500000 |
| latent_no_targetid_featnn1_appstate | lr_l2_c0p10 | 624 | 0.000035003 | 0.000000000 | -0.000165768 | -0.001539783 | -0.001167976 | 3 | 3 | 0.368589744 | 0.437500000 |
| latent_no_targetid_featnn1_appstory_inter | hgb_shallow | 624 | -0.000020601 | 0.000003673 | -0.000495196 | 0.002074211 | 0.000950142 | 49 | 43 | 0.491987179 | 0.562500000 |
| latent_no_targetid_featnn1_appstate_inter | hgb_shallow | 624 | 0.000018570 | 0.000014585 | -0.000355518 | -0.000771494 | 0.000203752 | 44 | 42 | 0.474358974 | 0.500000000 |

## OOF Promoted Policies

- OOF rows: `3744`
- OOF stress-promoted rows: `409`

| source_scope | view | model | split | target_kind | tail_q | policy | tail_auc | loss_vs_full | subject_win_rate | dropped_cells | dropped_q3 | dropped_s4 | stress_promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p20 | 0.597995411 | -0.000690331 | 0.700000000 | 90 | 90 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top13 | 0.854819885 | -0.000647412 | 0.700000000 | 26 | 13 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top21 | 0.854654227 | -0.000646138 | 0.800000000 | 21 | 9 | 12 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top50 | 0.854654227 | -0.000593038 | 0.900000000 | 50 | 27 | 23 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top25 | 0.854654227 | -0.000589018 | 0.800000000 | 50 | 25 | 25 | True |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p20 | 0.597995411 | -0.000535858 | 0.700000000 | 180 | 92 | 88 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top25 | 0.854654227 | -0.000532876 | 0.800000000 | 25 | 0 | 25 | True |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p15 | 0.597995411 | -0.000488561 | 0.700000000 | 68 | 68 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top25 | 0.854819885 | -0.000488235 | 0.800000000 | 25 | 9 | 16 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top25 | 0.854654227 | -0.000473762 | 0.700000000 | 25 | 11 | 14 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top10 | 0.854654227 | -0.000464191 | 0.700000000 | 20 | 10 | 10 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top10 | 0.854654227 | -0.000460481 | 0.700000000 | 10 | 0 | 10 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top13 | 0.854654227 | -0.000447175 | 0.800000000 | 13 | 5 | 8 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top13 | 0.854654227 | -0.000442834 | 0.700000000 | 13 | 0 | 13 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_top21 | 0.521782447 | -0.000429506 | 0.700000000 | 21 | 21 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | contrast | 0.200000000 | drop_s4_top40 | 0.546857364 | -0.000416957 | 0.800000000 | 40 | 0 | 40 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top13 | 0.849865215 | -0.000410271 | 0.800000000 | 13 | 6 | 7 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.200000000 | drop_global_top10 | 0.472556834 | -0.000409428 | 0.700000000 | 10 | 6 | 4 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top13 | 0.854819885 | -0.000405423 | 0.800000000 | 13 | 0 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top21 | 0.450187175 | -0.000405061 | 0.800000000 | 21 | 11 | 10 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_top25 | 0.851333544 | -0.000402695 | 0.800000000 | 25 | 25 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top13 | 0.468300930 | -0.000395687 | 0.700000000 | 13 | 13 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_p05 | 0.854654227 | -0.000390478 | 0.800000000 | 45 | 23 | 22 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top21 | 0.854819885 | -0.000368570 | 0.800000000 | 21 | 6 | 15 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top40 | 0.854654227 | -0.000367765 | 0.800000000 | 40 | 19 | 21 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_top25 | 0.521782447 | -0.000365842 | 0.700000000 | 25 | 25 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_each_top13 | 0.468300930 | -0.000351997 | 0.800000000 | 26 | 13 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top21 | 0.849865215 | -0.000351146 | 0.800000000 | 21 | 8 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p05 | 0.459062915 | -0.000350888 | 0.700000000 | 22 | 22 | 0 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_p05 | 0.521782447 | -0.000341370 | 0.700000000 | 22 | 22 | 0 | True |

## Best OOF Rows

| source_scope | view | model | split | target_kind | tail_q | policy | tail_auc | loss_vs_full | subject_win_rate | dropped_cells | dropped_q3 | dropped_s4 | stress_promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p20 | 0.597995411 | -0.000690331 | 0.700000000 | 90 | 90 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top13 | 0.854819885 | -0.000647412 | 0.700000000 | 26 | 13 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top21 | 0.854654227 | -0.000646138 | 0.800000000 | 21 | 9 | 12 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top50 | 0.854654227 | -0.000593038 | 0.900000000 | 50 | 27 | 23 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top25 | 0.854654227 | -0.000589018 | 0.800000000 | 50 | 25 | 25 | True |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p20 | 0.597995411 | -0.000535858 | 0.700000000 | 180 | 92 | 88 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top25 | 0.854654227 | -0.000532876 | 0.800000000 | 25 | 0 | 25 | True |
| all3 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p15 | 0.597995411 | -0.000488561 | 0.700000000 | 68 | 68 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top25 | 0.854819885 | -0.000488235 | 0.800000000 | 25 | 9 | 16 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top25 | 0.854654227 | -0.000473762 | 0.700000000 | 25 | 11 | 14 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_each_top10 | 0.854654227 | -0.000464191 | 0.700000000 | 20 | 10 | 10 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top10 | 0.854654227 | -0.000460481 | 0.700000000 | 10 | 0 | 10 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top13 | 0.854654227 | -0.000447175 | 0.800000000 | 13 | 5 | 8 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top13 | 0.854654227 | -0.000442834 | 0.700000000 | 13 | 0 | 13 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_top21 | 0.521782447 | -0.000429506 | 0.700000000 | 21 | 21 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | contrast | 0.200000000 | drop_s4_top40 | 0.546857364 | -0.000416957 | 0.800000000 | 40 | 0 | 40 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top13 | 0.849865215 | -0.000410271 | 0.800000000 | 13 | 6 | 7 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.200000000 | drop_global_top10 | 0.472556834 | -0.000409428 | 0.700000000 | 10 | 6 | 4 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_s4_top13 | 0.854819885 | -0.000405423 | 0.800000000 | 13 | 0 | 13 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top21 | 0.450187175 | -0.000405061 | 0.800000000 | 21 | 11 | 10 | True |
| all3 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_top25 | 0.851333544 | -0.000402695 | 0.800000000 | 25 | 25 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstate | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top13 | 0.468300930 | -0.000395687 | 0.700000000 | 13 | 13 | 0 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_p05 | 0.854654227 | -0.000390478 | 0.800000000 | 45 | 23 | 22 | True |
| q3s4 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top21 | 0.854819885 | -0.000368570 | 0.800000000 | 21 | 6 | 15 | True |
| q3s4 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_global_top40 | 0.854654227 | -0.000367765 | 0.800000000 | 40 | 19 | 21 | True |

## E237 Materialization Stress

- graft rows: `120`
- E237 gate passes: `9`
- selected files: `9`

| candidate_id | view | model | split | target_kind | tail_q | policy | q3_dropped_cells | s4_dropped_cells | oof_loss_vs_full | oof_tail_auc | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | e237_gate | e237_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top25 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_top25 | 25 | 0 | -0.000402695 | 0.851333544 | -0.000021997 | 0.000531054 | 0.010068809 | -0.000021997 | 0.000510444 | 0.008407924 | 0.731859029 | True | 0.056990432 |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top21 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_top21 | 21 | 0 | -0.000339937 | 0.851333544 | -0.000018995 | 0.000450867 | 0.009763909 | -0.000018995 | 0.000441018 | 0.008128766 | 0.748580906 | True | 0.048527142 |
| q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top40 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top40 | 40 | 0 | -0.000213160 | 0.459062915 | -0.000011062 | 0.000418878 | 0.000807834 | -0.000011062 | 0.000380358 | 0.000929725 | 0.796692651 | True | 0.043501146 |
| all3_latent_no_targetid_featnn1_appstate_hgb_shallow_row5_risk_q0p10_drop_q3_top13 | latent_no_targetid_featnn1_appstate | hgb_shallow | row5 | risk | 0.100000000 | drop_q3_top13 | 13 | 0 | -0.000246176 | 0.885251362 | 0.000006130 | 0.000329676 | 0.005842815 | 0.000006130 | 0.000329676 | 0.004855819 | 0.829711335 | True | 0.032576827 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top13 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_top13 | 13 | 0 | -0.000241990 | 0.854819885 | -0.000033007 | 0.000265294 | 0.004771073 | -0.000033007 | 0.000253849 | 0.004058637 | 0.676430877 | True | 0.031532093 |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_p05 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | row5 | risk | 0.200000000 | drop_q3_p05 | 12 | 0 | -0.000264382 | 0.851333544 | -0.000012151 | 0.000277395 | 0.006280561 | -0.000012151 | 0.000267546 | 0.005299481 | 0.789724562 | True | 0.029943134 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top25 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top25 | 25 | 0 | -0.000311701 | 0.450187175 | -0.000004156 | 0.000280095 | 0.000692909 | -0.000004156 | 0.000243841 | 0.000820701 | 0.843908884 | True | 0.028646801 |
| q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top21 | latent_no_targetid_featnn1_appstate_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top21 | 21 | 0 | -0.000339159 | 0.459062915 | -0.000005619 | 0.000240796 | 0.000651319 | -0.000005619 | 0.000212399 | 0.000732697 | 0.833446936 | True | 0.024918307 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top13 | latent_no_targetid_featnn1_appstory_inter | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top13 | 13 | 0 | -0.000299590 | 0.450187175 | -0.000012813 | 0.000170155 | 0.001117084 | -0.000012813 | 0.000164858 | 0.000969058 | 0.785551298 | True | 0.018898597 |

## Selected Q3 Cell Overlap With E247

| candidate_id | submission_file | q3_dropped | e247_overlap | e247_jaccard | e256_overlap | e256_jaccard | e247_missing | extra_vs_e247 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top25 | submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_af1e3537.csv | 25 | 11 | 0.229166667 | 10 | 0.250000000 | 23 | 14 |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top21 | submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_0af544e8.csv | 21 | 9 | 0.195652174 | 8 | 0.210526316 | 25 | 12 |
| all3_latent_no_targetid_featnn1_appstate_hgb_shallow_row5_risk_q0p10_drop_q3_top13 | submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstate_hgb_shallow_row5_risk_q0p10_drop_q3_top13_8ae24a48.csv | 13 | 7 | 0.175000000 | 7 | 0.225806452 | 27 | 6 |
| q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top40 | submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_05d17b9d.csv | 40 | 8 | 0.121212121 | 6 | 0.101694915 | 26 | 32 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top13 | submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_8ed575b4.csv | 13 | 5 | 0.119047619 | 5 | 0.151515152 | 29 | 8 |
| q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top21 | submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_83d5ef9c.csv | 21 | 5 | 0.100000000 | 4 | 0.095238095 | 29 | 16 |
| all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_p05 | submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_58aa0c8f.csv | 12 | 4 | 0.095238095 | 4 | 0.121212121 | 30 | 8 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top25 | submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_5c8ea041.csv | 25 | 5 | 0.092592593 | 4 | 0.086956522 | 29 | 20 |
| q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top13 | submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_b998aeea.csv | 13 | 3 | 0.068181818 | 3 | 0.085714286 | 31 | 10 |

## E247 Current-Anchor Matched Placebo Governor

- selected current-anchor models: `1`
- public-free ready files: `0`

| basename | candidate_id | final_decision | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | matched_placebo_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_0af544e8.csv | all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top21 | below_selector_resolution | below_selector_resolution | 0.000019772 | 0.000025223 | 0.000000000 | 0.037037037 | 0.000000000 | False |
| submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_af1e3537.csv | all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top25 | below_selector_resolution | below_selector_resolution | 0.000014957 | 0.000027736 | 0.000000000 | 0.037037037 | 0.000000000 | False |
| submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_58aa0c8f.csv | all3_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_p05 | below_selector_resolution | below_selector_resolution | 0.000046018 | 0.000072751 | 0.000000000 | 0.444444444 | 0.333333333 | False |
| submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_8ed575b4.csv | q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_row5_risk_q0p20_drop_q3_top13 | below_selector_resolution | below_selector_resolution | 0.000051337 | 0.000099781 | 0.000000000 | 0.370370370 | 0.222222222 | False |
| submission_e284_appentropy_decisive_all3_latent_no_targetid_featnn1_appstate_hgb_shallow_row5_risk_q0p10_drop_q3_top13_8ae24a48.csv | all3_latent_no_targetid_featnn1_appstate_hgb_shallow_row5_risk_q0p10_drop_q3_top13 | block_or_reject | block_or_reject | 0.000095347 | 0.000117282 | 0.000000000 | 0.074074074 | 0.000000000 | False |
| submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_b998aeea.csv | q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top13 | below_selector_resolution | below_selector_resolution | 0.000094362 | 0.000148900 | 0.000000000 | 0.851851852 | 0.666666667 | False |
| submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_83d5ef9c.csv | q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top21 | block_or_reject | block_or_reject | 0.000099823 | 0.000152026 | 0.000000000 | 0.407407407 | 0.222222222 | False |
| submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_5c8ea041.csv | q3s4_latent_no_targetid_featnn1_appstory_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top25 | block_or_reject | block_or_reject | 0.000098126 | 0.000152740 | 0.000000000 | 0.333333333 | 0.111111111 | False |
| submission_e284_appentropy_decisive_q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_05d17b9d.csv | q3s4_latent_no_targetid_featnn1_appstate_inter_hgb_shallow_subject5_contrast_q0p10_drop_q3_top40 | block_or_reject | block_or_reject | 0.000106069 | 0.000155628 | 0.000000000 | 0.185185185 | 0.000000000 | False |

## Decision

App-entropy context can produce E237-gated decisive-cell files, but none survived the E247-current matched-placebo governor. Do not submit E284 files.

## Files

- `e284_appentropy_decisive_cell_jepa_oof_scan.csv`
- `e284_appentropy_decisive_cell_jepa_pair_summary.csv`
- `e284_appentropy_decisive_cell_jepa_materialization_summary.csv`
- `e284_appentropy_decisive_cell_jepa_target_summary.csv`
- `e284_appentropy_decisive_cell_jepa_selected_summary.csv`
- `e284_appentropy_decisive_cell_jepa_overlap_summary.csv`
- `e284_appentropy_decisive_cell_jepa_governor_summary.csv`
