# E192 Shape-Only E72 Score Anatomy

## Question

What does the clean `shape_target_context_abs` E72-neighbor score actually mark:
a deployable contamination motif, a generic tail anomaly, or an E144-specific
pressure artifact?

## Result In One Sentence

The full-data shape score separates known E72-neighbor rows from non-E72 rows
(AUC `1.000`, AP `1.000`), stays low on the exact E95/E101 boundary, and
keeps E176 far below even the non-E72 p95 threshold; the mild E144 alarm is a
target/shape tail signal rather than a support-gate rescue. Treat the perfect
full-data separation as anatomy only; E191's pair-LOO result is the stress
evidence.

## Known Segment Calibration

| segment | n | label_rate | prob_mean | prob_max | prob_p95 |
| --- | --- | --- | --- | --- | --- |
| e72__e95 | 2 | 1.000000000 | 0.932422642 | 0.932422642 | 0.932422642 |
| e72_positive | 6 | 1.000000000 | 0.887863576 | 0.932422642 | 0.932422642 |
| e101__e72 | 2 | 1.000000000 | 0.926318860 | 0.926318860 | 0.926318860 |
| e72__mixmin | 2 | 1.000000000 | 0.804849225 | 0.804849225 | 0.804849225 |
| e101__mixmin | 2 | 0.000000000 | 0.047600922 | 0.047600922 | 0.047600922 |
| non_e72 | 126 | 0.000000000 | 0.005334635 | 0.047600922 | 0.020814665 |
| e95__mixmin | 2 | 0.000000000 | 0.036446680 | 0.036446680 | 0.036446680 |
| e101__e95 | 2 | 0.000000000 | 0.031015959 | 0.031015959 | 0.031015959 |
| exact_e95_e101 | 2 | 0.000000000 | 0.031015959 | 0.031015959 | 0.031015959 |
| a2c8_frontier__mixmin | 2 | 0.000000000 | 0.020814665 | 0.020814665 | 0.020814665 |
| hybrid_stage2__jepa_latent | 4 | 0.000000000 | 0.009366333 | 0.016549209 | 0.016549209 |
| jepa_latent__ordinal | 4 | 0.000000000 | 0.009521890 | 0.014122509 | 0.014122509 |
| jepa_latent__raw_jepa | 4 | 0.000000000 | 0.006276153 | 0.010604197 | 0.010604197 |
| a2c8_frontier__jepa_latent | 4 | 0.000000000 | 0.006017706 | 0.010269981 | 0.010269981 |
| hybrid_stage2__raw_jepa | 2 | 0.000000000 | 0.009734100 | 0.009734100 | 0.009734100 |
| hybrid_final9__jepa_latent | 4 | 0.000000000 | 0.005852502 | 0.008377984 | 0.008377984 |
| e101__jepa_latent | 4 | 0.000000000 | 0.005514927 | 0.008086781 | 0.008086781 |
| e95__jepa_latent | 4 | 0.000000000 | 0.005485493 | 0.008039555 | 0.008039555 |
| jepa_latent__mixmin | 4 | 0.000000000 | 0.005231577 | 0.007523584 | 0.007523584 |
| hybrid_final9__ordinal | 2 | 0.000000000 | 0.007344335 | 0.007344335 | 0.007344335 |
| a2c8_frontier__e95 | 2 | 0.000000000 | 0.006867854 | 0.006867854 | 0.006867854 |
| e72__jepa_latent | 4 | 0.000000000 | 0.004929794 | 0.006815535 | 0.006815535 |
| a2c8_frontier__e72 | 2 | 0.000000000 | 0.006756746 | 0.006756746 | 0.006756746 |
| a2c8_frontier__e101 | 2 | 0.000000000 | 0.006691375 | 0.006691375 | 0.006691375 |
| a2c8_frontier__hybrid_stage2 | 2 | 0.000000000 | 0.004622800 | 0.004622800 | 0.004622800 |
| e101__hybrid_stage2 | 2 | 0.000000000 | 0.002397242 | 0.002397242 | 0.002397242 |
| e95__hybrid_stage2 | 2 | 0.000000000 | 0.002389521 | 0.002389521 | 0.002389521 |
| e72__hybrid_stage2 | 2 | 0.000000000 | 0.002259729 | 0.002259729 | 0.002259729 |
| mixmin__ordinal | 2 | 0.000000000 | 0.002215963 | 0.002215963 | 0.002215963 |
| a2c8_frontier__ordinal | 2 | 0.000000000 | 0.002091186 | 0.002091186 | 0.002091186 |
| e101__ordinal | 2 | 0.000000000 | 0.002051150 | 0.002051150 | 0.002051150 |
| e95__ordinal | 2 | 0.000000000 | 0.002037995 | 0.002037995 | 0.002037995 |
| e72__raw_jepa | 2 | 0.000000000 | 0.001921708 | 0.001921708 | 0.001921708 |
| e72__ordinal | 2 | 0.000000000 | 0.001903465 | 0.001903465 | 0.001903465 |
| hybrid_stage2__mixmin | 2 | 0.000000000 | 0.001831092 | 0.001831092 | 0.001831092 |
| ordinal__raw_jepa | 2 | 0.000000000 | 0.001612747 | 0.001612747 | 0.001612747 |
| a2c8_frontier__hybrid_final9 | 2 | 0.000000000 | 0.001573393 | 0.001573393 | 0.001573393 |
| e95__raw_jepa | 2 | 0.000000000 | 0.001473882 | 0.001473882 | 0.001473882 |
| e101__raw_jepa | 2 | 0.000000000 | 0.001439934 | 0.001439934 | 0.001439934 |
| hybrid_stage2__ordinal | 2 | 0.000000000 | 0.001283748 | 0.001283748 | 0.001283748 |
| hybrid_final9__raw_jepa | 2 | 0.000000000 | 0.001235555 | 0.001235555 | 0.001235555 |
| bad_lejepa__jepa_latent | 4 | 0.000000000 | 0.000757004 | 0.001218330 | 0.001218330 |
| e101__hybrid_final9 | 2 | 0.000000000 | 0.001204983 | 0.001204983 | 0.001204983 |
| e95__hybrid_final9 | 2 | 0.000000000 | 0.001196803 | 0.001196803 | 0.001196803 |
| hybrid_final9__mixmin | 2 | 0.000000000 | 0.001161936 | 0.001161936 | 0.001161936 |
| mixmin__raw_jepa | 2 | 0.000000000 | 0.001158678 | 0.001158678 | 0.001158678 |
| jepa_latent__jepa_latent | 2 | 0.000000000 | 0.001127795 | 0.001127795 | 0.001127795 |
| e72__hybrid_final9 | 2 | 0.000000000 | 0.001097763 | 0.001097763 | 0.001097763 |
| hybrid_final9__hybrid_stage2 | 2 | 0.000000000 | 0.000996404 | 0.000996404 | 0.000996404 |
| a2c8_frontier__raw_jepa | 2 | 0.000000000 | 0.000523915 | 0.000523915 | 0.000523915 |
| bad_lejepa__raw_jepa | 2 | 0.000000000 | 0.000389059 | 0.000389059 | 0.000389059 |
| bad_lejepa__hybrid_stage2 | 2 | 0.000000000 | 0.000324357 | 0.000324357 | 0.000324357 |
| a2c8_frontier__bad_lejepa | 2 | 0.000000000 | 0.000298197 | 0.000298197 | 0.000298197 |
| bad_lejepa__mixmin | 2 | 0.000000000 | 0.000197818 | 0.000197818 | 0.000197818 |
| bad_lejepa__hybrid_final9 | 2 | 0.000000000 | 0.000196009 | 0.000196009 | 0.000196009 |
| bad_lejepa__e72 | 2 | 0.000000000 | 0.000191001 | 0.000191001 | 0.000191001 |
| bad_lejepa__e101 | 2 | 0.000000000 | 0.000170226 | 0.000170226 | 0.000170226 |
| bad_lejepa__e95 | 2 | 0.000000000 | 0.000170027 | 0.000170027 | 0.000170027 |
| bad_lejepa__ordinal | 2 | 0.000000000 | 0.000156533 | 0.000156533 | 0.000156533 |

## Live Branch Summary

| candidate | scenario_count | prob_mean | prob_max | above_non_e72_p95_rate | above_non_e72_p99_rate | above_min_positive_rate | n_diff_cells_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | 3 | 0.022666445 | 0.038722729 | 0.333333333 | 0.000000000 | 0.000000000 | 185.000000000 |
| e154 | 3 | 0.005852728 | 0.007972735 | 0.000000000 | 0.000000000 | 0.000000000 | 294.000000000 |
| e176 | 3 | 0.000006316 | 0.000008338 | 0.000000000 | 0.000000000 | 0.000000000 | 904.000000000 |

## Live Branch Detail

| candidate | scenario | shape_e72_prob | known_non_e72_p95 | known_non_e72_p99 | known_min_positive | above_non_e72_p95 | above_non_e72_p99 | above_min_positive | n_diff_cells | top_targets | contrib_family_shape | contrib_family_target | contrib_family_context | contrib_target_Q1 | contrib_target_Q2 | contrib_target_Q3 | contrib_target_S2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | global_t010_subject_t020 | 0.038722729 | 0.020814665 | 0.044812361 | 0.804849225 | True | False | False | 185 | S2,Q1,Q1,Q3 | -0.672455501 | -1.568767292 | 0.000000000 | -1.120091764 | 0.000000000 | -0.368737852 | 1.214894833 |
| e144 | global_t010 | 0.019367502 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 185 | S2,Q1,Q3,Q1 | -1.063580494 | -1.890407425 | 0.000000000 | -1.096337245 | 0.000000000 | -0.348745820 | 0.871640485 |
| e144 | global_t010_subject_t010 | 0.009909105 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 185 | Q1,Q1,Q1,Q3 | -0.580105493 | -3.053623840 | 0.000000000 | -1.220629008 | 0.000000000 | -0.368213889 | -0.126032545 |
| e154 | global_t010 | 0.007972735 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 294 | Q3,Q3,Q3,Q3 | -0.693164316 | -3.159945326 | 0.000000000 | -1.215495272 | 0.000000000 | -0.283063393 | -0.251039485 |
| e154 | global_t010_subject_t020 | 0.005284086 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 294 | Q3,Q3,Q3,Q3 | -0.879548672 | -3.387595411 | 0.000000000 | -1.217198213 | 0.000000000 | -0.286581746 | -0.242999606 |
| e154 | global_t010_subject_t010 | 0.004301363 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 294 | Q3,Q3,Q3,Q3 | -0.806858876 | -3.667040408 | 0.000000000 | -1.217198213 | 0.000000000 | -0.282605176 | -0.631026980 |
| e176 | global_t010 | 0.000008338 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 904 | S1,Q3,Q3,Q3 | -2.627604805 | -8.096420078 | 0.000000000 | -2.437606230 | -1.095883120 | -0.776350148 | -0.260483247 |
| e176 | global_t010_subject_t020 | 0.000005737 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 904 | S1,Q3,Q3,Q3 | -3.122020364 | -7.976011246 | 0.000000000 | -2.587026749 | -1.123944523 | -0.808596410 | -0.204675288 |
| e176 | global_t010_subject_t010 | 0.000004873 | 0.020814665 | 0.044812361 | 0.804849225 | False | False | False | 904 | S1,Q3,Q3,Q3 | -3.431596614 | -7.829619504 | 0.000000000 | -2.368784561 | -1.229936724 | -0.784428434 | -0.240463183 |

## Nearest Known Rows

| candidate | scenario | top3_label_rate | top3_exact_boundary_rate | top3_contexts | top1_context | top1_label | top1_prob | top1_euclidean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | global_t010 | 0.000000000 | 0.000000000 | a2c8_frontier__mixmin,a2c8_frontier__mixmin,a2c8_frontier__e101 | a2c8_frontier__mixmin | 0 | 0.020814665 | 10.799906135 |
| e144 | global_t010_subject_t010 | 0.000000000 | 0.000000000 | a2c8_frontier__e101,a2c8_frontier__e101,a2c8_frontier__e95 | a2c8_frontier__e101 | 0 | 0.006691375 | 11.063750667 |
| e144 | global_t010_subject_t020 | 0.000000000 | 0.000000000 | a2c8_frontier__mixmin,a2c8_frontier__mixmin,a2c8_frontier__e101 | a2c8_frontier__mixmin | 0 | 0.020814665 | 10.833460749 |
| e154 | global_t010 | 0.000000000 | 0.000000000 | hybrid_stage2__mixmin,hybrid_stage2__mixmin,a2c8_frontier__e95 | hybrid_stage2__mixmin | 0 | 0.001831092 | 10.194770805 |
| e154 | global_t010_subject_t010 | 0.000000000 | 0.000000000 | hybrid_stage2__mixmin,hybrid_stage2__mixmin,a2c8_frontier__e95 | hybrid_stage2__mixmin | 0 | 0.001831092 | 9.862558576 |
| e154 | global_t010_subject_t020 | 0.000000000 | 0.000000000 | hybrid_stage2__mixmin,hybrid_stage2__mixmin,e95__raw_jepa | hybrid_stage2__mixmin | 0 | 0.001831092 | 9.852013054 |
| e176 | global_t010 | 0.000000000 | 0.000000000 | bad_lejepa__jepa_latent,bad_lejepa__jepa_latent,bad_lejepa__ordinal | bad_lejepa__jepa_latent | 0 | 0.000295677 | 14.701578356 |
| e176 | global_t010_subject_t010 | 0.000000000 | 0.000000000 | bad_lejepa__ordinal,bad_lejepa__ordinal,bad_lejepa__jepa_latent | bad_lejepa__ordinal | 0 | 0.000156533 | 14.262205328 |
| e176 | global_t010_subject_t020 | 0.000000000 | 0.000000000 | bad_lejepa__jepa_latent,bad_lejepa__jepa_latent,bad_lejepa__ordinal | bad_lejepa__jepa_latent | 0 | 0.000295677 | 14.341170469 |

## Top Branch Contributions

| candidate | scenario | rank | feature | family | target_family | value_scaled | coef | contribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | global_t010 | 1 | abs__z__target_top1_S2_support_swing | target | S2 | 4.800793585 | 0.289836711 | 1.391446221 |
| e144 | global_t010 | 2 | abs__z__target_between_S4_support_swing | target | S4 | 4.571741849 | 0.149654454 | 0.684181530 |
| e144 | global_t010 | 3 | abs__z__target_between_S2_support_swing | target | S2 | 6.449347603 | 0.092679484 | 0.597722208 |
| e144 | global_t010 | 4 | abs__z__target_all_S4_support_swing | target | S4 | 0.314195284 | 0.252250108 | 0.079255794 |
| e144 | global_t010 | 5 | abs__z__shape_top1_support_label_mean | shape | no_target | 1.000000000 | 0.000051276 | 0.000051276 |
| e144 | global_t010_subject_t010 | 1 | abs__z__target_between_S4_support_swing | target | S4 | 4.800328941 | 0.149654454 | 0.718390607 |
| e144 | global_t010_subject_t010 | 2 | abs__z__target_between_S2_support_swing | target | S2 | 6.449347603 | 0.092679484 | 0.597722208 |
| e144 | global_t010_subject_t010 | 3 | abs__z__target_all_S2_support_swing | target | S2 | 0.648355822 | 0.208879364 | 0.135428151 |
| e144 | global_t010_subject_t010 | 4 | abs__z__target_all_S4_support_swing | target | S4 | 0.281122096 | 0.252250108 | 0.070913079 |
| e144 | global_t010_subject_t010 | 5 | abs__z__target_top16_S2_support_swing | target | S2 | 0.868222715 | 0.009163430 | 0.007955898 |
| e144 | global_t010_subject_t020 | 1 | abs__z__target_top1_S2_support_swing | target | S2 | 4.800793585 | 0.289836711 | 1.391446221 |
| e144 | global_t010_subject_t020 | 2 | abs__z__target_between_S4_support_swing | target | S4 | 5.120350871 | 0.149654454 | 0.766283314 |
| e144 | global_t010_subject_t020 | 3 | abs__z__target_between_S2_support_swing | target | S2 | 6.449347603 | 0.092679484 | 0.597722208 |
| e144 | global_t010_subject_t020 | 4 | abs__z__target_all_S2_support_swing | target | S2 | 0.926222602 | 0.208879364 | 0.193468788 |
| e144 | global_t010_subject_t020 | 5 | abs__z__target_all_S4_support_swing | target | S4 | 0.534131983 | 0.252250108 | 0.134734850 |
| e154 | global_t010 | 1 | abs__z__target_between_S4_support_swing | target | S4 | 5.066519423 | 0.149654454 | 0.758227198 |
| e154 | global_t010 | 2 | abs__z__target_between_S2_support_swing | target | S2 | 5.622538550 | 0.092679484 | 0.521093971 |
| e154 | global_t010 | 3 | abs__z__target_all_S2_support_swing | target | S2 | 0.996679271 | 0.208879364 | 0.208185732 |
| e154 | global_t010 | 4 | abs__z__target_all_S4_support_swing | target | S4 | 0.804381447 | 0.252250108 | 0.202905307 |
| e154 | global_t010 | 5 | abs__z__shape_top1_support_label_swing | shape | no_target | 1.000000000 | 0.000051276 | 0.000051276 |
| e154 | global_t010_subject_t010 | 1 | abs__z__target_between_S4_support_swing | target | S4 | 4.763866371 | 0.149654454 | 0.712933821 |
| e154 | global_t010_subject_t010 | 2 | abs__z__target_between_S2_support_swing | target | S2 | 5.517031840 | 0.092679484 | 0.511315664 |
| e154 | global_t010_subject_t010 | 3 | abs__z__target_all_S4_support_swing | target | S4 | 0.364739144 | 0.252250108 | 0.092005488 |
| e154 | global_t010_subject_t010 | 4 | abs__z__target_all_S2_support_swing | target | S2 | 0.050540006 | 0.208879364 | 0.010556764 |
| e154 | global_t010_subject_t010 | 5 | abs__z__shape_top1_support_label_swing | shape | no_target | 1.000000000 | 0.000051276 | 0.000051276 |
| e154 | global_t010_subject_t020 | 1 | abs__z__target_between_S4_support_swing | target | S4 | 4.536058257 | 0.149654454 | 0.678841322 |
| e154 | global_t010_subject_t020 | 2 | abs__z__target_between_S2_support_swing | target | S2 | 5.728202486 | 0.092679484 | 0.530886850 |
| e154 | global_t010_subject_t020 | 3 | abs__z__target_all_S2_support_swing | target | S2 | 0.988286867 | 0.208879364 | 0.206432732 |
| e154 | global_t010_subject_t020 | 4 | abs__z__target_all_S4_support_swing | target | S4 | 0.090730824 | 0.252250108 | 0.022886860 |
| e154 | global_t010_subject_t020 | 5 | abs__z__shape_top1_support_label_swing | shape | no_target | 1.000000000 | 0.000051276 | 0.000051276 |
| e176 | global_t010 | 1 | abs__z__target_top33_Q2_support_swing | target | Q2 | 3.230004857 | 0.226633354 | 0.732026836 |
| e176 | global_t010 | 2 | abs__z__target_all_S4_support_swing | target | S4 | 2.676149862 | 0.252250108 | 0.675059091 |
| e176 | global_t010 | 3 | abs__z__target_between_S4_support_swing | target | S4 | 3.048070096 | 0.149654454 | 0.456157266 |
| e176 | global_t010 | 4 | abs__z__target_all_S2_support_swing | target | S2 | 1.164213099 | 0.208879364 | 0.243180091 |
| e176 | global_t010 | 5 | abs__z__target_top4_S1_support_swing | target | S1 | 2.386235036 | 0.096078241 | 0.229265265 |
| e176 | global_t010_subject_t010 | 1 | abs__z__target_top33_Q2_support_swing | target | Q2 | 3.230004857 | 0.226633354 | 0.732026836 |
| e176 | global_t010_subject_t010 | 2 | abs__z__target_all_S4_support_swing | target | S4 | 2.139413712 | 0.252250108 | 0.539667339 |
| e176 | global_t010_subject_t010 | 3 | abs__z__target_between_S4_support_swing | target | S4 | 2.154579583 | 0.149654454 | 0.322442431 |
| e176 | global_t010_subject_t010 | 4 | abs__z__target_all_S2_support_swing | target | S2 | 1.445178371 | 0.208879364 | 0.301867938 |
| e176 | global_t010_subject_t010 | 5 | abs__z__target_top4_S1_support_swing | target | S1 | 2.386235036 | 0.096078241 | 0.229265265 |
| e176 | global_t010_subject_t020 | 1 | abs__z__target_top33_Q2_support_swing | target | Q2 | 3.230004857 | 0.226633354 | 0.732026836 |
| e176 | global_t010_subject_t020 | 2 | abs__z__target_all_S4_support_swing | target | S4 | 2.536491655 | 0.252250108 | 0.639830293 |
| e176 | global_t010_subject_t020 | 3 | abs__z__target_between_S4_support_swing | target | S4 | 2.795069711 | 0.149654454 | 0.418294631 |
| e176 | global_t010_subject_t020 | 4 | abs__z__target_all_S2_support_swing | target | S2 | 1.568945122 | 0.208879364 | 0.327720259 |
| e176 | global_t010_subject_t020 | 5 | abs__z__target_top4_S1_support_swing | target | S1 | 2.386235036 | 0.096078241 | 0.229265265 |

## Exact Boundary And Positive Anchors

Exact E95/E101 rows:

| pair_id | new_tag | base_tag | pair_context | shape_e72_prob | actual_delta |
| --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | e95 | e101 | e101__e95 | 0.031015959 | -0.000009036 |
| submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | e101 | e95 | e101__e95 | 0.031015959 | 0.000009036 |

Known positive rows:

| pair_id | new_tag | base_tag | pair_context | shape_e72_prob | actual_delta |
| --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e95 | e72 | e72__e95 | 0.932422642 | -0.000116447 |
| submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | e95 | e72__e95 | 0.932422642 | 0.000116447 |
| submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e101 | e72 | e101__e72 | 0.926318860 | -0.000107411 |
| submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | e101 | e101__e72 | 0.926318860 | 0.000107411 |
| submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | mixmin | e72 | e72__mixmin | 0.804849225 | -0.000101137 |
| submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | mixmin | e72__mixmin | 0.804849225 | 0.000101137 |

## Interpretation

- The clean score is not a support detector. E191 already killed that route,
  and E192 shows the remaining live pressure-branch signal is driven by
  target/shape contribution geometry. Branch context terms are zero in this
  pressure-frame view, so any live alarm must stand without context help.
- E144 crosses the non-E72 p95 in some scenarios, but it does not approach the
  known positive floor. Treat this as tail-risk evidence, not a direct
  contamination proof.
- E176 remains the least E72-like live branch under this score. This supports
  keeping E176 as the next broad shape/prior sensor instead of replacing it
  with an E144/E154 support-repair branch.

## Decision

No submission is created. The next submission sensor remains E176 unless a new
experiment finds a non-support mechanism that explains public sensitivity
better than this shape-safe branch ordering.
