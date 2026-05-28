# S4/Q3 OOF Top Selector Rescore

Question: do the strongest local Q3/S4 OOF candidates survive direct pairwise and hidden-subset selector scoring?

## Summary

| top_oof_scored | pair_p90_negative | pair_majority | old_majority | pair_probe_gate | pair_control_gate | pair_submit_gate | selector_conflict | q3s4_shape70 | oof_selector_anchor_like | strict_s4q3_oof_anchor_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 399 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Correlations

- corr(oof_q3s4_delta_vs_stage2, pair_delta_vs_a2c8_p90) = `-0.273` over n=399
- corr(oof_q3s4_delta_vs_stage2, selector_p90_delta_vs_a2c8_public) = `-0.064` over n=399

## Top Local OOF Candidates After Selector Scoring

| source_path | oof_rank | oof_q3s4_delta_vs_stage2 | oof_q3s4_scenario_p90 | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | q3s4_move_share | dominant_target | pair_probe_gate | pair_selector_conflict | oof_selector_anchor_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_public_maskaware_t65_r07_768f6df0.csv | 1 | -0.0207719 | -0.00794514 | 0.00105309 | 0.259459 | 0.00144251 | 0.003861 | 0.34603 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t80_r11_544844af.csv | 2 | -0.0207719 | -0.00794514 | 0.00102184 | 0.262162 | 0.0013545 | 0.003861 | 0.35088 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t80_r10_18d78615.csv | 3 | -0.0205851 | -0.00725148 | 0.00108602 | 0.259459 | 0.00143811 | 0.003861 | 0.345614 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t50_r04_6761fb38.csv | 4 | -0.020551 | -0.00811683 | 0.00107639 | 0.259459 | 0.00144717 | 0.003861 | 0.3452 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t80_r12_dcfaabba.csv | 5 | -0.020551 | -0.00811683 | 0.00104089 | 0.262162 | 0.00136038 | 0.003861 | 0.350002 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t65_r08_7f7fa3e2.csv | 6 | -0.0204784 | -0.00745521 | 0.00107856 | 0.259459 | 0.00145228 | 0.003861 | 0.345116 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t50_r05_fb7b695a.csv | 7 | -0.020332 | -0.00830473 | 0.00105367 | 0.262162 | 0.00143871 | 0.003861 | 0.34684 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t50_r06_8d5b4fe1.csv | 8 | -0.0203027 | -0.00842488 | 0.00105303 | 0.262162 | 0.00143974 | 0.003861 | 0.34685 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t65_r09_35ff9a82.csv | 9 | -0.0202532 | -0.00831094 | 0.0011121 | 0.251351 | 0.00147048 | 0.003861 | 0.34336 | Q3 | False | False | False |
| analysis_outputs/submission_public_maskaware_t35_r02_517540cc.csv | 10 | -0.0201498 | -0.00825342 | 0.00101193 | 0.264865 | 0.0013684 | 0 | 0.346771 | Q3 | False | False | False |
| analysis_outputs/submission_public_entropyproj_public2d0_g100.csv | 11 | -0.0200497 | -0.00469374 | 0.00121928 | 0.202703 | 0.00150702 | 0.003861 | 0.341031 | Q3 | False | False | False |
| analysis_outputs/submission_public_entropyproj_proj0_g100.csv | 12 | -0.0197215 | -0.00456818 | 0.00121794 | 0.17027 | 0.00151041 | 0.003861 | 0.33942 | Q3 | False | False | False |
| analysis_outputs/submission_public_minimaxens_r01_a6_h422045.csv | 13 | -0.0196787 | -0.00658878 | 0.000882326 | 0.262162 | 0.00132754 | 0.003861 | 0.356517 | Q3 | False | False | False |
| analysis_outputs/submission_public_minimaxens_r08_a10_h869363.csv | 14 | -0.0196785 | -0.00658514 | 0.000883466 | 0.262162 | 0.00132776 | 0.003861 | 0.356469 | Q3 | False | False | False |
| analysis_outputs/submission_public_minimaxens_r07_a12_h981086.csv | 15 | -0.0196772 | -0.00658431 | 0.000884114 | 0.262162 | 0.00132775 | 0.003861 | 0.356459 | Q3 | False | False | False |
| analysis_outputs/submission_public_minimaxens_r05_a10_h506746.csv | 16 | -0.0196711 | -0.0065787 | 0.000883645 | 0.262162 | 0.00132773 | 0.003861 | 0.356494 | Q3 | False | False | False |
| analysis_outputs/submission_public_universeens_u80_r01_07c571e6.csv | 17 | -0.0196699 | -0.00658434 | 0.000883688 | 0.262162 | 0.00132752 | 0.003861 | 0.356477 | Q3 | False | False | False |
| analysis_outputs/submission_public_universeens_u80_r04_8b6653a9.csv | 18 | -0.0196697 | -0.00657962 | 0.000884626 | 0.262162 | 0.00132768 | 0.003861 | 0.356458 | Q3 | False | False | False |
| analysis_outputs/submission_public_minimaxens_r04_a11_h082844.csv | 19 | -0.0196685 | -0.00658148 | 0.000884786 | 0.262162 | 0.00132767 | 0.003861 | 0.356448 | Q3 | False | False | False |
| analysis_outputs/submission_public_universeens_u80_r03_72e58bdb.csv | 20 | -0.0196685 | -0.00658148 | 0.000884786 | 0.262162 | 0.00132767 | 0.003861 | 0.356448 | Q3 | False | False | False |

## Best Pairwise Among Top OOF Candidates

| source_path | oof_rank | oof_q3s4_delta_vs_stage2 | oof_q3s4_scenario_p90 | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | q3s4_move_share | dominant_target | pair_probe_gate | pair_selector_conflict | oof_selector_anchor_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p005_w065.csv | 315 | -0.00934435 | -0.00308024 | 0.000532604 | 0.0486486 | 0.00117958 | 0.003861 | 0.443945 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thrm0p005_w065.csv | 381 | -0.00858173 | -0.00304924 | 0.000538744 | 0.0459459 | 0.00119035 | 0.003861 | 0.441836 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p0025_w065.csv | 280 | -0.00959676 | -0.00308024 | 0.000539958 | 0.0432432 | 0.00119583 | 0.003861 | 0.44533 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p005_w080.csv | 194 | -0.010943 | -0.00338587 | 0.000541338 | 0.0513514 | 0.00119444 | 0.003861 | 0.471365 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thrm0p0025_w065.csv | 369 | -0.0087057 | -0.00303493 | 0.00055184 | 0.0378378 | 0.00120905 | 0.003861 | 0.43556 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p01_w065.csv | 364 | -0.008748 | -0.000358841 | 0.00055241 | 0.0540541 | 0.00114431 | 0.003861 | 0.440195 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thr0p0_w065.csv | 355 | -0.00881694 | -0.00305297 | 0.000554638 | 0.0378378 | 0.00121245 | 0.00772201 | 0.438453 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thrm0p005_w080.csv | 248 | -0.0100116 | -0.00334299 | 0.000558771 | 0.0486486 | 0.00121203 | 0.003861 | 0.469092 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thr0p0_w065.csv | 273 | -0.009708 | -0.00308024 | 0.000559122 | 0.0378378 | 0.00118941 | 0.003861 | 0.447988 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p0025_w080.csv | 175 | -0.0112283 | -0.00338587 | 0.00056009 | 0.0486486 | 0.00120682 | 0.003861 | 0.472112 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thrm0p0025_w080.csv | 243 | -0.0101556 | -0.00332516 | 0.00056974 | 0.0486486 | 0.00122875 | 0.003861 | 0.461265 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thrm0p01_w080.csv | 230 | -0.01028 | -0.000417572 | 0.000569806 | 0.0594595 | 0.00116988 | 0.003861 | 0.467578 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_blend500_q1_q3_s2_s4_thrm0p005_w065.csv | 389 | -0.00855445 | -0.00354556 | 0.000572119 | 0.0405405 | 0.00118342 | 0.003861 | 0.427406 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_blend500_q1_q3_s2_s4_thr0p0_w065.csv | 333 | -0.00913996 | -0.00358732 | 0.00057509 | 0.0378378 | 0.0011939 | 0.00772201 | 0.434994 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_blend500_q1_q3_s2_s4_thrm0p0025_w065.csv | 334 | -0.00913996 | -0.00358732 | 0.00057509 | 0.0378378 | 0.0011939 | 0.00772201 | 0.434994 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_no_q2_thrm0p005_w065.csv | 314 | -0.00934435 | -0.00308024 | 0.000578004 | 0.0405405 | 0.00115789 | 0.00772201 | 0.407961 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_q1_q3_s2_s4_thr0p0_w080.csv | 168 | -0.0113453 | -0.00338587 | 0.000579169 | 0.0513514 | 0.00122019 | 0.00772201 | 0.474412 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thrm0p01_w080.csv | 311 | -0.00934859 | -0.000429051 | 0.0005843 | 0.0567568 | 0.00118972 | 0.003861 | 0.465168 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ambnext_q1_q3_s2_s4_thr0p0_w080.csv | 234 | -0.0102726 | -0.00334645 | 0.000584467 | 0.0459459 | 0.001227 | 0.00772201 | 0.463893 | Q3 | False | False | False |
| analysis_outputs/submission_subjectgate_ordinal_no_q2_thr0p0_w065.csv | 272 | -0.009708 | -0.00308024 | 0.000591529 | 0.0324324 | 0.00119823 | 0.00772201 | 0.407969 | Q3 | False | False | False |

## OOF Selector Anchor-Like Candidates

_None._

## Interpretation

- The strongest local Q3/S4 OOF candidates do not provide the missing independent S4/Q3 public anchor.
- Local OOF strength and public-sensitive selector support are different views; local Q3/S4 gains alone should not be promoted to public submissions.
- This strengthens the validation-mismatch diagnosis: the missing object is a selector-resolvable public-positive movement, not merely another local-CV strong S4/Q3 candidate.
