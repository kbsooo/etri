# E249 Feature-NN1 Decisive OOF Audit

## Question

Can feature-NN1 context rescue the E248 failure when used inside the E237 decisive-cell target, instead of as a direct smoothing selector?

## Headline

- Feature-NN1 OOF rows scanned: `2496`.
- Stress-promoted feature-NN1 rows: `276`.
- Best feature-NN1 OOF loss_vs_full: `-0.000706695` from `latent_no_targetid_featnn1/hgb_shallow/subject5/contrast/q=0.10/drop_q3_top50`.
- Locked E237 selected OOF loss_vs_full: `-0.000271441`, tail_auc `0.901873158`.
- Best paired median delta: `latent_no_targetid/hgb_shallow` has median loss delta `0.000053880` and median tail-AUC delta `0.001857861`.

## Top Rows

| section | source_scope | view | model | split | target_kind | tail_q | policy | tail_auc | loss_vs_full | subject_win_rate | dropped_cells | dropped_q3 | dropped_s4 | dropped_mean_benefit | stress_promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top50 | 0.594251902 | -0.000706695 | 0.800000000 | 50 | 50 | 0 | -0.012720517 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top100 | 0.594251902 | -0.000676320 | 0.800000000 | 100 | 53 | 47 | -0.006086876 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p10 | 0.594251902 | -0.000656307 | 0.800000000 | 45 | 45 | 0 | -0.013126140 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p15 | 0.594251902 | -0.000656203 | 0.700000000 | 68 | 68 | 0 | -0.008685034 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p10 | 0.594251902 | -0.000537159 | 0.800000000 | 90 | 50 | 40 | -0.005371588 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_p10 | 0.521118256 | -0.000488262 | 0.600000000 | 45 | 45 | 0 | -0.009765245 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_top40 | 0.521118256 | -0.000460130 | 0.600000000 | 40 | 40 | 0 | -0.010352920 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top13 | 0.468059413 | -0.000430735 | 0.700000000 | 13 | 13 | 0 | -0.029820140 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top40 | 0.594251902 | -0.000429854 | 0.800000000 | 40 | 40 | 0 | -0.009671717 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.200000000 | drop_q3_top50 | 0.521118256 | -0.000422723 | 0.600000000 | 50 | 50 | 0 | -0.007609013 | True |
| top_nn_loss | q3s4 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_s4_p15 | 0.594750838 | -0.000415604 | 0.700000000 | 68 | 0 | 68 | -0.005500637 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p15 | 0.594251902 | -0.000370722 | 0.800000000 | 135 | 69 | 66 | -0.002471478 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p05 | 0.468059413 | -0.000365271 | 0.700000000 | 22 | 22 | 0 | -0.014942887 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top21 | 0.468059413 | -0.000354929 | 0.700000000 | 21 | 21 | 0 | -0.015211258 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p05 | 0.594251902 | -0.000347705 | 0.700000000 | 45 | 23 | 22 | -0.006954109 | True |
| top_nn_loss | q3s4 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_s4_top40 | 0.594750838 | -0.000340232 | 0.700000000 | 40 | 0 | 40 | -0.007655222 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_p20 | 0.594251902 | -0.000340174 | 0.700000000 | 180 | 94 | 86 | -0.001700868 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top40 | 0.468059413 | -0.000334446 | 0.700000000 | 40 | 40 | 0 | -0.007525030 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top25 | 0.468059413 | -0.000329330 | 0.700000000 | 25 | 25 | 0 | -0.011855890 | True |
| top_nn_loss | all3 | movement_featnn1 | lr_l2_c0p10 | row5 | contrast | 0.200000000 | drop_each_top25 | 0.562585398 | -0.000321942 | 0.700000000 | 50 | 25 | 25 | -0.005794960 | True |
| top_nn_loss | q3s4 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_top10 | 0.468059413 | -0.000317254 | 0.600000000 | 10 | 10 | 0 | -0.028552867 | True |
| top_nn_loss | q3s4 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_s4_p20 | 0.594750838 | -0.000313509 | 0.700000000 | 90 | 0 | 90 | -0.003135087 | True |
| top_nn_loss | all3 | movement_featnn1 | lr_l2_c0p10 | row5 | contrast | 0.200000000 | drop_s4_top25 | 0.562585398 | -0.000312331 | 0.700000000 | 25 | 0 | 25 | -0.011243924 | True |
| top_nn_loss | q3s4 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_global_top40 | 0.594750838 | -0.000308813 | 0.800000000 | 40 | 20 | 20 | -0.006948282 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | lr_l2_c0p10 | row5 | contrast | 0.200000000 | drop_q3_top40 | 0.505524862 | -0.000305736 | 0.800000000 | 40 | 40 | 0 | -0.006879063 | True |
| top_nn_loss | all3 | movement_featnn1 | lr_l2_c0p10 | subject5 | contrast | 0.200000000 | drop_global_top40 | 0.498807475 | -0.000300907 | 0.700000000 | 40 | 13 | 27 | -0.006770403 | True |
| top_nn_loss | all3 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_global_top75 | 0.582263846 | -0.000298511 | 0.700000000 | 75 | 38 | 37 | -0.003582134 | True |
| top_nn_loss | q3s4 | movement_featnn1 | hgb_shallow | row5 | contrast | 0.100000000 | drop_each_top21 | 0.594750838 | -0.000294753 | 0.800000000 | 42 | 21 | 21 | -0.006316128 | True |
| top_nn_loss | all3 | latent_no_targetid_featnn1 | hgb_shallow | subject5 | contrast | 0.100000000 | drop_q3_p20 | 0.594251902 | -0.000294640 | 0.700000000 | 90 | 90 | 0 | -0.002946404 | True |
| top_nn_loss | all3 | movement_featnn1 | lr_l2_c0p10 | subject5 | contrast | 0.200000000 | drop_s4_top21 | 0.498807475 | -0.000294121 | 0.700000000 | 21 | 0 | 21 | -0.012605204 | True |
| top_nn_tail_auc | q3s4 | movement_featnn1 | hgb_shallow | row5 | risk | 0.100000000 | drop_q3_top21 | 0.915177679 | 0.000148091 | 0.700000000 | 21 | 21 | 0 | 0.006346769 | False |
| top_nn_tail_auc | q3s4 | movement_featnn1 | hgb_shallow | row5 | risk | 0.100000000 | drop_global_top50 | 0.915177679 | 0.000912748 | 0.500000000 | 50 | 29 | 21 | 0.016429468 | False |

## Paired Delta Versus Original E237 Views

| base_view | model | pairs | median_delta_loss | mean_delta_loss | p10_delta_loss | median_delta_tail_auc | promoted_by_nn | demoted_by_nn | nn_better_loss_rate | nn_better_tail_auc_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| latent_no_targetid | hgb_shallow | 624 | 0.000053880 | 0.000057349 | -0.000348204 | 0.001857861 | 46 | 52 | 0.424679487 | 0.625000000 |
| movement | hgb_shallow | 624 | 0.000057555 | 0.000122641 | -0.000348714 | -0.010021190 | 26 | 55 | 0.427884615 | 0.125000000 |
| latent_no_targetid | lr_l2_c0p10 | 624 | 0.000062418 | 0.000056997 | -0.000252763 | -0.011697394 | 8 | 7 | 0.386217949 | 0.000000000 |
| movement | lr_l2_c0p10 | 624 | 0.000087045 | 0.000113740 | -0.000311575 | -0.015066046 | 51 | 54 | 0.355769231 | 0.062500000 |

## Decision

- Feature-NN1 context improves the OOF decisive-cell search enough to justify a materialization stress scan. Do not submit directly; next step is an E250 graft/actual gate using only the top OOF survivors.
- No submission file is created by E249.
