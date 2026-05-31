# E330 Target-Residual Lifestyle Latent

## Question

After E328 rejected a broad lifestyle latent, can lifestyle context predict target-specific base-residual states under blocked stress?

## Construction

- Teacher: per-target residual after a subject/calendar base model under the same blocked split.
- Context: masked lifestyle views from family JEPA features, story bundle, raw day features, and combined views.
- Student: Ridge predicts the residual state OOF by subject or dateblock.
- Evaluation: label logloss improvement versus base, plus row/subject/dateblock shuffled residual-state nulls.

## Top Residual-State Rows

| target | view_id | split | context_cols | teacher_resid_std | student_oof_r2 | student_spearman | base_loss | aug_loss | actual_delta | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | jepa_resid | subject | 32 | 0.529534051 | -0.195539000 | -0.234482211 | 0.765899724 | 0.735689108 | -0.030210616 | -0.021406624 | 0.002898194 | -0.002572115 | 1.000000000 | -0.033108810 | True |
| Q1 | jepa_resid | dateblock | 32 | 0.490883367 | -0.166429177 | -0.221202146 | 0.678969360 | 0.653126588 | -0.025842772 | -0.026037033 | -0.000121684 | -0.008620067 | 0.958333333 | -0.025721088 | True |
| S2 | raw_day | subject | 160 | 0.498724340 | -0.296321149 | 0.206834602 | 0.698689330 | 0.682237256 | -0.016452074 | -0.017433356 | 0.000306265 | -0.009405310 | 0.958333333 | -0.016758339 | True |
| S2 | jepa_resid | dateblock | 32 | 0.444832946 | -0.122333143 | -0.165973165 | 0.590404664 | 0.576193446 | -0.014211218 | -0.005020530 | 0.002018470 | -0.000212523 | 1.000000000 | -0.016229688 | True |
| S1 | family_jepa_story | subject | 280 | 0.477844007 | -0.633356974 | 0.172189624 | 0.656678990 | 0.647551344 | -0.009127646 | -0.005946190 | 0.001337255 | -0.001349278 | 1.000000000 | -0.010464902 | True |
| S2 | family | dateblock | 40 | 0.444832946 | -0.147824396 | -0.127379658 | 0.590404664 | 0.582853040 | -0.007551624 | -0.006944294 | 0.000681265 | -0.001390855 | 1.000000000 | -0.008232889 | True |
| S1 | family_story | subject | 248 | 0.477844007 | -0.593627916 | 0.114382985 | 0.656678990 | 0.651570480 | -0.005108509 | -0.004324168 | 0.001935007 | -0.000524559 | 1.000000000 | -0.007043517 | True |
| Q3 | family | dateblock | 40 | 0.493630329 | -0.180633981 | -0.158561507 | 0.684573900 | 0.680066738 | -0.004507162 | -0.006299789 | -0.000085597 | -0.002989001 | 0.875000000 | -0.004421565 | True |
| Q2 | family | subject | 40 | 0.529534051 | -0.332970101 | -0.103548495 | 0.765899724 | 0.761606748 | -0.004292977 | -0.016337431 | 0.000386216 | -0.003524472 | 0.875000000 | -0.004679192 | True |
| S2 | family_story | subject | 248 | 0.498724340 | -1.274644421 | -0.068289983 | 0.698689330 | 0.694832379 | -0.003856951 | -0.005772905 | 0.002217611 | 0.000252748 | 0.958333333 | -0.006074562 | True |
| S1 | story_bundle | dateblock | 208 | 0.441122001 | -0.341165327 | 0.108914118 | 0.581863284 | 0.579225211 | -0.002638073 | -0.002501328 | 0.001378745 | 0.000398989 | 1.000000000 | -0.004016818 | True |
| Q1 | family_story | subject | 248 | 0.511107495 | -0.532496553 | 0.107131722 | 0.718497188 | 0.716310075 | -0.002187114 | 0.000585811 | 0.001902953 | 0.001073332 | 1.000000000 | -0.004090067 | True |
| S3 | jepa_resid | dateblock | 32 | 0.422237711 | -0.089241663 | -0.057182505 | 0.533414862 | 0.531496443 | -0.001918419 | -0.010865765 | 0.001350254 | 0.000506188 | 0.916666667 | -0.003268673 | True |
| S2 | family | subject | 40 | 0.498724340 | -0.288650168 | -0.046753087 | 0.698689330 | 0.696931964 | -0.001757367 | -0.002234528 | 0.000879976 | -0.000432369 | 0.916666667 | -0.002637343 | True |
| Q3 | story_bundle | subject | 208 | 0.508494340 | -0.586941571 | 0.001292451 | 0.717155066 | 0.715560534 | -0.001594532 | -0.007229001 | 0.002951784 | 0.001035525 | 0.916666667 | -0.004546316 | True |
| S2 | family_jepa_story | subject | 280 | 0.498724340 | -1.588075633 | 0.016009495 | 0.698689330 | 0.697569715 | -0.001119616 | -0.001199043 | 0.001316476 | -0.000529866 | 0.958333333 | -0.002436092 | True |
| Q2 | jepa_resid | dateblock | 32 | 0.509602978 | -0.110750906 | -0.088994612 | 0.715333740 | 0.708028054 | -0.007305686 | -0.011864958 | 0.000240725 | -0.003762103 | 0.833333333 | -0.007546410 | False |
| S1 | raw_day | subject | 160 | 0.477844007 | -0.733518096 | 0.152536391 | 0.656678990 | 0.652535907 | -0.004143083 | -0.011136732 | 0.000889166 | -0.003713064 | 0.833333333 | -0.005032250 | False |
| S2 | story_bundle | subject | 208 | 0.498724340 | -0.957782450 | -0.115007580 | 0.698689330 | 0.694893742 | -0.003795588 | -0.007321415 | -0.001528439 | -0.004189765 | 0.708333333 | -0.002267150 | False |
| Q2 | raw_day | dateblock | 160 | 0.509602978 | -0.447152259 | -0.098722397 | 0.715333740 | 0.711928737 | -0.003405003 | -0.013027692 | 0.000493691 | -0.005818185 | 0.750000000 | -0.003898694 | False |
| S2 | family_jepa_story | dateblock | 280 | 0.444832946 | -0.891057401 | -0.054569027 | 0.590404664 | 0.587641918 | -0.002762747 | -0.003838271 | 0.001459519 | -0.001753185 | 0.833333333 | -0.004222266 | False |
| S3 | family | dateblock | 40 | 0.422237711 | -0.136351496 | -0.051768157 | 0.533414862 | 0.531893426 | -0.001521435 | -0.004254983 | 0.001806072 | -0.000032956 | 0.833333333 | -0.003327507 | False |
| S4 | story_bundle | subject | 208 | 0.520107426 | -0.751619045 | -0.064543726 | 0.738700697 | 0.737332333 | -0.001368364 | -0.019164068 | 0.001388092 | -0.001624762 | 0.791666667 | -0.002756456 | False |
| S2 | family_story | dateblock | 248 | 0.444832946 | -0.763267369 | -0.051667021 | 0.590404664 | 0.589196173 | -0.001208492 | -0.007126106 | 0.000678584 | -0.001627622 | 0.666666667 | -0.001887076 | False |
| Q1 | story_bundle | subject | 208 | 0.511107495 | -0.468165103 | 0.114497685 | 0.718497188 | 0.717894580 | -0.000602609 | -0.002919661 | 0.001339820 | -0.000851397 | 0.750000000 | -0.001942429 | False |
| S1 | jepa_resid | subject | 32 | 0.477844007 | -0.023097456 | 0.145106955 | 0.656678990 | 0.656101108 | -0.000577882 | -0.021889585 | 0.002109373 | -0.002588614 | 0.666666667 | -0.002687255 | False |
| Q3 | raw_day | subject | 160 | 0.508494340 | -0.609251100 | -0.040303541 | 0.717155066 | 0.716737816 | -0.000417250 | -0.001071274 | 0.004024450 | 0.000630729 | 0.916666667 | -0.004441700 | False |
| S1 | family_story | dateblock | 248 | 0.441122001 | -0.478699268 | 0.056807984 | 0.581863284 | 0.581563659 | -0.000299625 | -0.004647715 | 0.001375286 | -0.000591753 | 0.750000000 | -0.001674911 | False |
| S2 | raw_day | dateblock | 160 | 0.444832946 | -0.427529545 | -0.042800738 | 0.590404664 | 0.590380855 | -0.000023809 | -0.003336421 | 0.001429383 | 0.000681180 | 0.958333333 | -0.001453192 | False |
| S1 | jepa_resid | dateblock | 32 | 0.441122001 | -0.069786831 | -0.071653687 | 0.581863284 | 0.581948825 | 0.000085541 | -0.004683780 | 0.001290866 | -0.000264205 | 0.750000000 | -0.001205325 | False |

## Selected Local Gates

| target | view_id | split | context_cols | teacher_resid_std | student_oof_r2 | student_spearman | base_loss | aug_loss | actual_delta | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | jepa_resid | subject | 32 | 0.529534051 | -0.195539000 | -0.234482211 | 0.765899724 | 0.735689108 | -0.030210616 | -0.021406624 | 0.002898194 | -0.002572115 | 1.000000000 | -0.033108810 | True |
| Q1 | jepa_resid | dateblock | 32 | 0.490883367 | -0.166429177 | -0.221202146 | 0.678969360 | 0.653126588 | -0.025842772 | -0.026037033 | -0.000121684 | -0.008620067 | 0.958333333 | -0.025721088 | True |
| S2 | raw_day | subject | 160 | 0.498724340 | -0.296321149 | 0.206834602 | 0.698689330 | 0.682237256 | -0.016452074 | -0.017433356 | 0.000306265 | -0.009405310 | 0.958333333 | -0.016758339 | True |
| S2 | jepa_resid | dateblock | 32 | 0.444832946 | -0.122333143 | -0.165973165 | 0.590404664 | 0.576193446 | -0.014211218 | -0.005020530 | 0.002018470 | -0.000212523 | 1.000000000 | -0.016229688 | True |
| S1 | family_jepa_story | subject | 280 | 0.477844007 | -0.633356974 | 0.172189624 | 0.656678990 | 0.647551344 | -0.009127646 | -0.005946190 | 0.001337255 | -0.001349278 | 1.000000000 | -0.010464902 | True |
| S2 | family | dateblock | 40 | 0.444832946 | -0.147824396 | -0.127379658 | 0.590404664 | 0.582853040 | -0.007551624 | -0.006944294 | 0.000681265 | -0.001390855 | 1.000000000 | -0.008232889 | True |
| S1 | family_story | subject | 248 | 0.477844007 | -0.593627916 | 0.114382985 | 0.656678990 | 0.651570480 | -0.005108509 | -0.004324168 | 0.001935007 | -0.000524559 | 1.000000000 | -0.007043517 | True |
| Q3 | family | dateblock | 40 | 0.493630329 | -0.180633981 | -0.158561507 | 0.684573900 | 0.680066738 | -0.004507162 | -0.006299789 | -0.000085597 | -0.002989001 | 0.875000000 | -0.004421565 | True |

## Null Summary

| target | view_id | split | mode | rep | null_delta |
| --- | --- | --- | --- | --- | --- |
| Q1 | family | dateblock | dateblock | 0 | 0.004984722 |
| Q1 | family | dateblock | dateblock | 1 | -0.004282666 |
| Q1 | family | dateblock | dateblock | 2 | -0.010432984 |
| Q1 | family | dateblock | dateblock | 3 | -0.005258675 |
| Q1 | family | dateblock | dateblock | 4 | 0.004112685 |
| Q1 | family | dateblock | dateblock | 5 | 0.003071684 |
| Q1 | family | dateblock | dateblock | 6 | -0.002192684 |
| Q1 | family | dateblock | dateblock | 7 | 0.000417532 |
| Q1 | family | dateblock | row | 0 | 0.000439630 |
| Q1 | family | dateblock | row | 1 | 0.000771560 |
| Q1 | family | dateblock | row | 2 | 0.002825565 |
| Q1 | family | dateblock | row | 3 | 0.001358396 |
| Q1 | family | dateblock | row | 4 | 0.002073175 |
| Q1 | family | dateblock | row | 5 | 0.002565938 |
| Q1 | family | dateblock | row | 6 | -0.000708788 |
| Q1 | family | dateblock | row | 7 | 0.000441570 |
| Q1 | family | dateblock | subject | 0 | 0.001837804 |
| Q1 | family | dateblock | subject | 1 | 0.000995705 |
| Q1 | family | dateblock | subject | 2 | 0.001296116 |
| Q1 | family | dateblock | subject | 3 | 0.000762061 |
| Q1 | family | dateblock | subject | 4 | 0.003492833 |
| Q1 | family | dateblock | subject | 5 | 0.007587219 |
| Q1 | family | dateblock | subject | 6 | -0.003382164 |
| Q1 | family | dateblock | subject | 7 | 0.006187025 |
| Q1 | family | subject | dateblock | 0 | 0.004472630 |
| Q1 | family | subject | dateblock | 1 | 0.002605963 |
| Q1 | family | subject | dateblock | 2 | -0.000619546 |
| Q1 | family | subject | dateblock | 3 | 0.002760363 |
| Q1 | family | subject | dateblock | 4 | -0.003898508 |
| Q1 | family | subject | dateblock | 5 | 0.002677463 |
| Q1 | family | subject | dateblock | 6 | 0.006637708 |
| Q1 | family | subject | dateblock | 7 | -0.005115498 |
| Q1 | family | subject | row | 0 | 0.002181005 |
| Q1 | family | subject | row | 1 | 0.003589347 |
| Q1 | family | subject | row | 2 | 0.004003021 |
| Q1 | family | subject | row | 3 | 0.000707663 |
| Q1 | family | subject | row | 4 | 0.003842999 |
| Q1 | family | subject | row | 5 | 0.001351356 |
| Q1 | family | subject | row | 6 | 0.001027879 |
| Q1 | family | subject | row | 7 | 0.000662068 |
| Q1 | family | subject | subject | 0 | 0.006449170 |
| Q1 | family | subject | subject | 1 | 0.006310561 |
| Q1 | family | subject | subject | 2 | 0.000816158 |
| Q1 | family | subject | subject | 3 | -0.002007530 |
| Q1 | family | subject | subject | 4 | 0.006050137 |
| Q1 | family | subject | subject | 5 | 0.006648281 |
| Q1 | family | subject | subject | 6 | -0.007279023 |
| Q1 | family | subject | subject | 7 | 0.002472366 |
| Q1 | family_jepa_story | dateblock | dateblock | 0 | 0.005104301 |
| Q1 | family_jepa_story | dateblock | dateblock | 1 | 0.000723622 |
| Q1 | family_jepa_story | dateblock | dateblock | 2 | 0.002564996 |
| Q1 | family_jepa_story | dateblock | dateblock | 3 | -0.000938941 |
| Q1 | family_jepa_story | dateblock | dateblock | 4 | -0.005627654 |
| Q1 | family_jepa_story | dateblock | dateblock | 5 | -0.001118979 |
| Q1 | family_jepa_story | dateblock | dateblock | 6 | -0.003968133 |
| Q1 | family_jepa_story | dateblock | dateblock | 7 | 0.006499413 |
| Q1 | family_jepa_story | dateblock | row | 0 | 0.001612251 |
| Q1 | family_jepa_story | dateblock | row | 1 | 0.002940802 |
| Q1 | family_jepa_story | dateblock | row | 2 | 0.000922811 |
| Q1 | family_jepa_story | dateblock | row | 3 | 0.002267754 |
| Q1 | family_jepa_story | dateblock | row | 4 | -0.002373598 |
| Q1 | family_jepa_story | dateblock | row | 5 | 0.000024095 |
| Q1 | family_jepa_story | dateblock | row | 6 | 0.000846864 |
| Q1 | family_jepa_story | dateblock | row | 7 | -0.003017810 |
| Q1 | family_jepa_story | dateblock | subject | 0 | 0.000759701 |
| Q1 | family_jepa_story | dateblock | subject | 1 | 0.001679686 |
| Q1 | family_jepa_story | dateblock | subject | 2 | 0.003054316 |
| Q1 | family_jepa_story | dateblock | subject | 3 | -0.000959858 |
| Q1 | family_jepa_story | dateblock | subject | 4 | -0.000380705 |
| Q1 | family_jepa_story | dateblock | subject | 5 | 0.001685441 |
| Q1 | family_jepa_story | dateblock | subject | 6 | 0.002452429 |
| Q1 | family_jepa_story | dateblock | subject | 7 | -0.004128243 |
| Q1 | family_jepa_story | subject | dateblock | 0 | 0.002716001 |
| Q1 | family_jepa_story | subject | dateblock | 1 | 0.003888341 |
| Q1 | family_jepa_story | subject | dateblock | 2 | 0.002002546 |
| Q1 | family_jepa_story | subject | dateblock | 3 | 0.009572926 |
| Q1 | family_jepa_story | subject | dateblock | 4 | 0.001667711 |
| Q1 | family_jepa_story | subject | dateblock | 5 | 0.001754927 |
| Q1 | family_jepa_story | subject | dateblock | 6 | 0.001973873 |
| Q1 | family_jepa_story | subject | dateblock | 7 | 0.000460300 |

## Candidate Probes

| candidate_id | file | basename | target | view_id | split | scale | source_actual_delta | source_dominance | source_placebo_adjusted | changed_rows | changed_cells | mean_abs_logit_move | max_abs_logit_move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2_jepa_resid_subject_s0p2 | analysis_outputs/submission_e330_targetresid_Q2_jepa_resid_subject_s0p2_817c1bf2.csv | submission_e330_targetresid_Q2_jepa_resid_subject_s0p2_817c1bf2.csv | Q2 | jepa_resid | subject | 0.200000000 | -0.030210616 | 1.000000000 | -0.033108810 | 250 | 250 | 0.012756534 | 0.014000000 |
| Q2_jepa_resid_subject_s0p4 | analysis_outputs/submission_e330_targetresid_Q2_jepa_resid_subject_s0p4_bc503ce8.csv | submission_e330_targetresid_Q2_jepa_resid_subject_s0p4_bc503ce8.csv | Q2 | jepa_resid | subject | 0.400000000 | -0.030210616 | 1.000000000 | -0.033108810 | 250 | 250 | 0.025513068 | 0.028000000 |
| Q2_jepa_resid_subject_s0p65 | analysis_outputs/submission_e330_targetresid_Q2_jepa_resid_subject_s0p65_4dc877bb.csv | submission_e330_targetresid_Q2_jepa_resid_subject_s0p65_4dc877bb.csv | Q2 | jepa_resid | subject | 0.650000000 | -0.030210616 | 1.000000000 | -0.033108810 | 250 | 250 | 0.041458736 | 0.045500000 |
| Q1_jepa_resid_dateblock_s0p2 | analysis_outputs/submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p2_49017863.csv | submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p2_49017863.csv | Q1 | jepa_resid | dateblock | 0.200000000 | -0.025842772 | 0.958333333 | -0.025721088 | 250 | 250 | 0.012472153 | 0.014000000 |
| Q1_jepa_resid_dateblock_s0p4 | analysis_outputs/submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p4_7ec421be.csv | submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p4_7ec421be.csv | Q1 | jepa_resid | dateblock | 0.400000000 | -0.025842772 | 0.958333333 | -0.025721088 | 250 | 250 | 0.024944306 | 0.028000000 |
| Q1_jepa_resid_dateblock_s0p65 | analysis_outputs/submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p65_cb573e97.csv | submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p65_cb573e97.csv | Q1 | jepa_resid | dateblock | 0.650000000 | -0.025842772 | 0.958333333 | -0.025721088 | 250 | 250 | 0.040534497 | 0.045500000 |
| S2_raw_day_subject_s0p2 | analysis_outputs/submission_e330_targetresid_S2_raw_day_subject_s0p2_e2fa851f.csv | submission_e330_targetresid_S2_raw_day_subject_s0p2_e2fa851f.csv | S2 | raw_day | subject | 0.200000000 | -0.016452074 | 0.958333333 | -0.016758339 | 250 | 250 | 0.012209540 | 0.014000000 |
| S2_raw_day_subject_s0p4 | analysis_outputs/submission_e330_targetresid_S2_raw_day_subject_s0p4_5f7fc23b.csv | submission_e330_targetresid_S2_raw_day_subject_s0p4_5f7fc23b.csv | S2 | raw_day | subject | 0.400000000 | -0.016452074 | 0.958333333 | -0.016758339 | 250 | 250 | 0.024419080 | 0.028000000 |
| S2_raw_day_subject_s0p65 | analysis_outputs/submission_e330_targetresid_S2_raw_day_subject_s0p65_f06e6bd5.csv | submission_e330_targetresid_S2_raw_day_subject_s0p65_f06e6bd5.csv | S2 | raw_day | subject | 0.650000000 | -0.016452074 | 0.958333333 | -0.016758339 | 250 | 250 | 0.039681005 | 0.045500000 |
| S2_jepa_resid_dateblock_s0p2 | analysis_outputs/submission_e330_targetresid_S2_jepa_resid_dateblock_s0p2_d7095a60.csv | submission_e330_targetresid_S2_jepa_resid_dateblock_s0p2_d7095a60.csv | S2 | jepa_resid | dateblock | 0.200000000 | -0.014211218 | 1.000000000 | -0.016229688 | 250 | 250 | 0.012340367 | 0.014000000 |
| S2_jepa_resid_dateblock_s0p4 | analysis_outputs/submission_e330_targetresid_S2_jepa_resid_dateblock_s0p4_d0318d11.csv | submission_e330_targetresid_S2_jepa_resid_dateblock_s0p4_d0318d11.csv | S2 | jepa_resid | dateblock | 0.400000000 | -0.014211218 | 1.000000000 | -0.016229688 | 250 | 250 | 0.024680733 | 0.028000000 |
| S2_jepa_resid_dateblock_s0p65 | analysis_outputs/submission_e330_targetresid_S2_jepa_resid_dateblock_s0p65_8379e29c.csv | submission_e330_targetresid_S2_jepa_resid_dateblock_s0p65_8379e29c.csv | S2 | jepa_resid | dateblock | 0.650000000 | -0.014211218 | 1.000000000 | -0.016229688 | 250 | 250 | 0.040106192 | 0.045500000 |
| S1_family_jepa_story_subject_s0p2 | analysis_outputs/submission_e330_targetresid_S1_family_jepa_story_subject_s0p2_04186f40.csv | submission_e330_targetresid_S1_family_jepa_story_subject_s0p2_04186f40.csv | S1 | family_jepa_story | subject | 0.200000000 | -0.009127646 | 1.000000000 | -0.010464902 | 250 | 250 | 0.011984830 | 0.014000000 |
| S1_family_jepa_story_subject_s0p4 | analysis_outputs/submission_e330_targetresid_S1_family_jepa_story_subject_s0p4_24ab1a66.csv | submission_e330_targetresid_S1_family_jepa_story_subject_s0p4_24ab1a66.csv | S1 | family_jepa_story | subject | 0.400000000 | -0.009127646 | 1.000000000 | -0.010464902 | 250 | 250 | 0.023969660 | 0.028000000 |
| S1_family_jepa_story_subject_s0p65 | analysis_outputs/submission_e330_targetresid_S1_family_jepa_story_subject_s0p65_f7357646.csv | submission_e330_targetresid_S1_family_jepa_story_subject_s0p65_f7357646.csv | S1 | family_jepa_story | subject | 0.650000000 | -0.009127646 | 1.000000000 | -0.010464902 | 250 | 250 | 0.038950698 | 0.045500000 |
| S2_family_dateblock_s0p2 | analysis_outputs/submission_e330_targetresid_S2_family_dateblock_s0p2_c327ee69.csv | submission_e330_targetresid_S2_family_dateblock_s0p2_c327ee69.csv | S2 | family | dateblock | 0.200000000 | -0.007551624 | 1.000000000 | -0.008232889 | 250 | 250 | 0.012108437 | 0.014000000 |
| S2_family_dateblock_s0p4 | analysis_outputs/submission_e330_targetresid_S2_family_dateblock_s0p4_84ce9917.csv | submission_e330_targetresid_S2_family_dateblock_s0p4_84ce9917.csv | S2 | family | dateblock | 0.400000000 | -0.007551624 | 1.000000000 | -0.008232889 | 250 | 250 | 0.024216875 | 0.028000000 |
| S2_family_dateblock_s0p65 | analysis_outputs/submission_e330_targetresid_S2_family_dateblock_s0p65_05bbaefe.csv | submission_e330_targetresid_S2_family_dateblock_s0p65_05bbaefe.csv | S2 | family | dateblock | 0.650000000 | -0.007551624 | 1.000000000 | -0.008232889 | 250 | 250 | 0.039352421 | 0.045500000 |
| S1_family_story_subject_s0p2 | analysis_outputs/submission_e330_targetresid_S1_family_story_subject_s0p2_fa388dff.csv | submission_e330_targetresid_S1_family_story_subject_s0p2_fa388dff.csv | S1 | family_story | subject | 0.200000000 | -0.005108509 | 1.000000000 | -0.007043517 | 250 | 250 | 0.012018717 | 0.014000000 |
| S1_family_story_subject_s0p4 | analysis_outputs/submission_e330_targetresid_S1_family_story_subject_s0p4_e9fcbd2b.csv | submission_e330_targetresid_S1_family_story_subject_s0p4_e9fcbd2b.csv | S1 | family_story | subject | 0.400000000 | -0.005108509 | 1.000000000 | -0.007043517 | 250 | 250 | 0.024037435 | 0.028000000 |
| S1_family_story_subject_s0p65 | analysis_outputs/submission_e330_targetresid_S1_family_story_subject_s0p65_2c9000b9.csv | submission_e330_targetresid_S1_family_story_subject_s0p65_2c9000b9.csv | S1 | family_story | subject | 0.650000000 | -0.005108509 | 1.000000000 | -0.007043517 | 250 | 250 | 0.039060832 | 0.045500000 |
| Q3_family_dateblock_s0p2 | analysis_outputs/submission_e330_targetresid_Q3_family_dateblock_s0p2_9bafe653.csv | submission_e330_targetresid_Q3_family_dateblock_s0p2_9bafe653.csv | Q3 | family | dateblock | 0.200000000 | -0.004507162 | 0.875000000 | -0.004421565 | 250 | 250 | 0.011228894 | 0.014000000 |
| Q3_family_dateblock_s0p4 | analysis_outputs/submission_e330_targetresid_Q3_family_dateblock_s0p4_54f8f510.csv | submission_e330_targetresid_Q3_family_dateblock_s0p4_54f8f510.csv | Q3 | family | dateblock | 0.400000000 | -0.004507162 | 0.875000000 | -0.004421565 | 250 | 250 | 0.022457788 | 0.028000000 |
| Q3_family_dateblock_s0p65 | analysis_outputs/submission_e330_targetresid_Q3_family_dateblock_s0p65_e3ec8344.csv | submission_e330_targetresid_Q3_family_dateblock_s0p65_e3ec8344.csv | Q3 | family | dateblock | 0.650000000 | -0.004507162 | 0.875000000 | -0.004421565 | 250 | 250 | 0.036493905 | 0.045500000 |
| combo_top_target_resid_s0p30 | analysis_outputs/submission_e330_targetresid_combo_top_target_resid_s0p30_3ccaf470.csv | submission_e330_targetresid_combo_top_target_resid_s0p30_3ccaf470.csv | Q1,Q2,S2 | Q2:jepa_resid:subject;Q1:jepa_resid:dateblock;S2:raw_day:subject | combo | 0.300000000 | -0.024168488 | 0.972222222 | -0.025196079 | 250 | 750 | 0.008022477 | 0.021000000 |

## Public-Free Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e330_targetresid_S1_family_story_subject_s0p2_fa388dff.csv | below_selector_resolution | 0.000004558 | -0.000028674 | 0.000031889 | 0.444444444 | -0.004684432 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p2_04186f40.csv | below_selector_resolution | -0.000008499 | -0.000060296 | 0.000032176 | 0.472222222 | -0.003749013 |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p2_49017863.csv | below_selector_resolution | 0.000024608 | 0.000009107 | 0.000036416 | 0.027777778 | 0.002817806 |
| submission_e330_targetresid_S2_family_dateblock_s0p2_c327ee69.csv | below_selector_resolution | -0.000064488 | -0.000220959 | 0.000037200 | 0.444444444 | -0.001482338 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p2_d7095a60.csv | below_selector_resolution | -0.000089132 | -0.000284193 | 0.000038238 | 0.472222222 | -0.002766403 |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p4_7ec421be.csv | below_selector_resolution | 0.000052725 | 0.000021720 | 0.000084544 | 0.027777778 | 0.005635612 |
| submission_e330_targetresid_S1_family_story_subject_s0p4_e9fcbd2b.csv | below_selector_resolution | 0.000005808 | -0.000082238 | 0.000084954 | 0.472222222 | -0.009368865 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p4_24ab1a66.csv | below_selector_resolution | -0.000020454 | -0.000135451 | 0.000085666 | 0.472222222 | -0.007498025 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p4_d0318d11.csv | below_selector_resolution | -0.000161164 | -0.000546501 | 0.000095935 | 0.472222222 | -0.005532806 |
| submission_e330_targetresid_S2_family_dateblock_s0p4_84ce9917.csv | below_selector_resolution | -0.000110005 | -0.000421957 | 0.000102612 | 0.444444444 | -0.002964676 |
| submission_e330_targetresid_S2_raw_day_subject_s0p2_e2fa851f.csv | below_selector_resolution | 0.000051938 | 0.000007166 | 0.000120163 | 0.055555556 | -0.000002676 |
| submission_e330_targetresid_S1_family_story_subject_s0p65_2c9000b9.csv | below_selector_resolution | -0.000022796 | -0.000232857 | 0.000178363 | 0.472222222 | -0.015224405 |
| submission_e330_targetresid_Q3_family_dateblock_s0p2_9bafe653.csv | below_selector_resolution | 0.000061702 | -0.000031199 | 0.000179697 | 0.472222222 | 0.004860547 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p65_f7357646.csv | below_selector_resolution | -0.000062192 | -0.000333164 | 0.000181198 | 0.472222222 | -0.012184291 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p65_8379e29c.csv | below_selector_resolution | -0.000214843 | -0.000797452 | 0.000182606 | 0.472222222 | -0.008990810 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p2_817c1bf2.csv | below_selector_resolution | 0.000050909 | -0.000102273 | 0.000188323 | 0.361111111 | -0.009261879 |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p65_cb573e97.csv | below_selector_resolution | 0.000103354 | 0.000044663 | 0.000194120 | 0.027777778 | 0.009157869 |
| submission_e330_targetresid_S2_family_dateblock_s0p65_05bbaefe.csv | below_selector_resolution | -0.000129926 | -0.000599056 | 0.000203829 | 0.430555556 | -0.004817598 |
| submission_e330_targetresid_S2_raw_day_subject_s0p4_5f7fc23b.csv | below_selector_resolution | 0.000127748 | 0.000033754 | 0.000269843 | 0.041666667 | -0.000005353 |
| submission_e330_targetresid_Q3_family_dateblock_s0p4_54f8f510.csv | below_selector_resolution | 0.000113314 | -0.000064045 | 0.000333266 | 0.472222222 | 0.009721094 |
| submission_e330_targetresid_combo_top_target_resid_s0p30_3ccaf470.csv | block_or_reject | 0.000195623 | 0.000072785 | 0.000343363 | 0.055555556 | -0.009670124 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p4_bc503ce8.csv | below_selector_resolution | 0.000088882 | -0.000215128 | 0.000361004 | 0.361111111 | -0.015397741 |
| submission_e330_targetresid_Q3_family_dateblock_s0p65_e3ec8344.csv | below_selector_resolution | 0.000163974 | -0.000093714 | 0.000478072 | 0.486111111 | 0.015796778 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p65_4dc877bb.csv | below_selector_resolution | 0.000102388 | -0.000386846 | 0.000513402 | 0.361111111 | -0.009209303 |
| submission_e330_targetresid_S2_raw_day_subject_s0p65_f06e6bd5.csv | block_or_reject | 0.000270058 | 0.000080389 | 0.000545780 | 0.027777778 | -0.000008698 |

## E323-Negative Anatomy

| basename | changed_rows | changed_cells | mean_abs_logit_delta | max_abs_prob_delta | cos_with_e323_bad_delta | l1_ratio_to_e323_delta |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p65_cb573e97.csv | 250 | 250 | 0.005790642 | 0.011374226 | -0.034638491 | 0.227987568 |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p4_7ec421be.csv | 250 | 250 | 0.003563472 | 0.006999883 | -0.034638491 | 0.140300042 |
| submission_e330_targetresid_Q1_jepa_resid_dateblock_s0p2_49017863.csv | 250 | 250 | 0.001781736 | 0.003499982 | -0.034638491 | 0.070150021 |
| submission_e330_targetresid_combo_top_target_resid_s0p30_3ccaf470.csv | 250 | 750 | 0.008022477 | 0.005249951 | -0.019953389 | 0.315858747 |
| submission_e330_targetresid_S2_family_dateblock_s0p65_05bbaefe.csv | 250 | 250 | 0.005621774 | 0.011373478 | -0.000000000 | 0.221338944 |
| submission_e330_targetresid_S2_family_dateblock_s0p4_84ce9917.csv | 250 | 250 | 0.003459554 | 0.006998534 | -0.000000000 | 0.136208581 |
| submission_e330_targetresid_S2_family_dateblock_s0p2_c327ee69.csv | 250 | 250 | 0.001729777 | 0.003498927 | -0.000000000 | 0.068104291 |
| submission_e330_targetresid_Q3_family_dateblock_s0p65_e3ec8344.csv | 250 | 250 | 0.005213415 | 0.011374468 | -0.000000000 | 0.205261129 |
| submission_e330_targetresid_Q3_family_dateblock_s0p4_54f8f510.csv | 250 | 250 | 0.003208255 | 0.006999843 | -0.000000000 | 0.126314541 |
| submission_e330_targetresid_Q3_family_dateblock_s0p2_9bafe653.csv | 250 | 250 | 0.001604128 | 0.003499986 | -0.000000000 | 0.063157270 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p65_4dc877bb.csv | 250 | 250 | 0.005922677 | 0.011374509 | -0.000000000 | 0.233185977 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p4_bc503ce8.csv | 250 | 250 | 0.003644724 | 0.006999874 | -0.000000000 | 0.143499063 |
| submission_e330_targetresid_Q2_jepa_resid_subject_s0p2_817c1bf2.csv | 250 | 250 | 0.001822362 | 0.003499982 | -0.000000000 | 0.071749532 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p2_d7095a60.csv | 250 | 250 | 0.001762910 | 0.003499622 | 0.000000000 | 0.069408784 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p4_d0318d11.csv | 250 | 250 | 0.003525819 | 0.006999573 | 0.000000000 | 0.138817569 |
| submission_e330_targetresid_S2_jepa_resid_dateblock_s0p65_8379e29c.csv | 250 | 250 | 0.005729456 | 0.011374449 | 0.000000000 | 0.225578549 |
| submission_e330_targetresid_S2_raw_day_subject_s0p2_e2fa851f.csv | 250 | 250 | 0.001744220 | 0.003499622 | 0.000000000 | 0.068672945 |
| submission_e330_targetresid_S2_raw_day_subject_s0p4_5f7fc23b.csv | 250 | 250 | 0.003488440 | 0.006999573 | 0.000000000 | 0.137345891 |
| submission_e330_targetresid_S2_raw_day_subject_s0p65_f06e6bd5.csv | 250 | 250 | 0.005668715 | 0.011374449 | 0.000000000 | 0.223187073 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p2_04186f40.csv | 250 | 250 | 0.001712119 | 0.003499982 | 0.008172669 | 0.067409059 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p4_24ab1a66.csv | 250 | 250 | 0.003424237 | 0.006999856 | 0.008172669 | 0.134818117 |
| submission_e330_targetresid_S1_family_jepa_story_subject_s0p65_f7357646.csv | 250 | 250 | 0.005564385 | 0.011374506 | 0.008172669 | 0.219079440 |
| submission_e330_targetresid_S1_family_story_subject_s0p2_fa388dff.csv | 250 | 250 | 0.001716960 | 0.003499982 | 0.018308338 | 0.067599658 |
| submission_e330_targetresid_S1_family_story_subject_s0p4_e9fcbd2b.csv | 250 | 250 | 0.003433919 | 0.006999856 | 0.018308338 | 0.135199316 |
| submission_e330_targetresid_S1_family_story_subject_s0p65_2c9000b9.csv | 250 | 250 | 0.005580119 | 0.011374037 | 0.018308338 | 0.219698889 |

## Decision

Target-specific residual states exist locally, but their E247 materializations are not submission-grade under the public-free selector and E323-negative anatomy check.

- gated residual-state rows: `16`
- generated candidates: `25`
- selector-promoted candidates: `0`
- E323-negative candidates: `25`

## Files

- `e330_target_residual_lifestyle_latent_summary.csv`
- `e330_target_residual_lifestyle_latent_null_summary.csv`
- `e330_target_residual_lifestyle_latent_candidate_summary.csv`
- `e330_target_residual_lifestyle_latent_candidate_scores.csv`
- `e330_target_residual_lifestyle_latent_candidate_anatomy.csv`
