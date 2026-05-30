# E231 E224 Q3 OOF Support Prune

## Question

Can E230-style E224 Q3 tail pruning be learned from train/OOF support labels?

## Setup

- Train Q3 support-label rate: `0.502222`.
- Full E224-like Q3 target OOF delta versus stage2: `-0.004262113`.

## Support Model Stress

| model | split | auc | logloss | brier | corr_benefit | mean_prob |
| --- | --- | --- | --- | --- | --- | --- |
| lr_l2_c0p10 | rowcontig5 | 0.551951643 | 0.906186377 | 0.310062881 | 0.067747582 | 0.473410694 |
| hgb_shallow | rowcontig5 | 0.550766435 | 0.711223527 | 0.257466958 | -0.040734209 | 0.506527366 |
| lr_l1_c0p04 | rowcontig5 | 0.528978350 | 0.692051555 | 0.249452026 | -0.047360696 | 0.502517766 |
| gb_shallow | rowcontig5 | 0.524039981 | 0.704307318 | 0.255221154 | -0.058533525 | 0.493633619 |
| lr_l2_c0p10 | stratified5 | 0.565759324 | 0.779133052 | 0.274043035 | 0.014016880 | 0.489918140 |
| hgb_shallow | stratified5 | 0.551951643 | 0.711576163 | 0.257706420 | -0.031852062 | 0.491618827 |
| gb_shallow | stratified5 | 0.551141751 | 0.697242259 | 0.251680180 | -0.014938671 | 0.495846262 |
| lr_l1_c0p04 | stratified5 | 0.541521808 | 0.690525049 | 0.248686214 | -0.106894977 | 0.498513224 |
| hgb_shallow | subject5 | 0.588100506 | 0.691673341 | 0.248513221 | 0.014234434 | 0.493275988 |
| gb_shallow | subject5 | 0.560366625 | 0.694034915 | 0.250165377 | -0.032725716 | 0.497501466 |
| lr_l1_c0p04 | subject5 | 0.550094817 | 0.687982673 | 0.247436818 | -0.029677347 | 0.504620251 |
| lr_l2_c0p10 | subject5 | 0.541798357 | 0.810178995 | 0.289144795 | -0.018524560 | 0.470688890 |
| hgb_shallow | subject_loo | 0.559438211 | 0.701000994 | 0.253152188 | -0.007285893 | 0.504267827 |
| lr_l2_c0p10 | subject_loo | 0.546835493 | 0.787941792 | 0.282897712 | -0.032334885 | 0.476235607 |
| gb_shallow | subject_loo | 0.542667509 | 0.696066747 | 0.251263204 | 0.011200281 | 0.511830906 |
| lr_l1_c0p04 | subject_loo | 0.541492178 | 0.691564202 | 0.249180282 | -0.068965672 | 0.506018019 |

## Best OOF Prune Gates

| model_split | gate | kept_rows | pruned_rows | kept_support_precision | pruned_bad_rate | q3_target_delta | loss_vs_full_q3 | subject_win_rate | oof_gate_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lr_l2_c0p10__rowcontig5 | keep_prob_ge_0p35 | 266 | 184 | 0.545112782 | 0.559782609 | -0.004776026 | -0.000513912 | 0.800000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low13 | 437 | 13 | 0.512585812 | 0.846153846 | -0.004728049 | -0.000465936 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low8 | 442 | 8 | 0.506787330 | 0.750000000 | -0.004733899 | -0.000471786 | 0.700000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low13 | 437 | 13 | 0.508009153 | 0.692307692 | -0.004664730 | -0.000402617 | 0.700000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low8 | 442 | 8 | 0.509049774 | 0.875000000 | -0.004621636 | -0.000359523 | 0.600000000 | False |
| gb_shallow__subject5 | keep_prob_ge_0p35 | 423 | 27 | 0.513002364 | 0.666666667 | -0.004612057 | -0.000349944 | 0.600000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low21 | 429 | 21 | 0.510489510 | 0.666666667 | -0.004564255 | -0.000302142 | 0.600000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low5 | 445 | 5 | 0.505617978 | 0.800000000 | -0.004545346 | -0.000283233 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low21 | 429 | 21 | 0.508158508 | 0.619047619 | -0.004527746 | -0.000265633 | 0.700000000 | False |
| gb_shallow__subject5 | drop_prob_low25 | 425 | 25 | 0.510588235 | 0.640000000 | -0.004517204 | -0.000255091 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low3 | 447 | 3 | 0.505592841 | 1.000000000 | -0.004485046 | -0.000222933 | 0.600000000 | False |
| gb_shallow__subject5 | drop_prob_low21 | 429 | 21 | 0.510489510 | 0.666666667 | -0.004497052 | -0.000234939 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low5 | 445 | 5 | 0.505617978 | 0.800000000 | -0.004459609 | -0.000197496 | 0.600000000 | False |
| hgb_shallow__subject5 | drop_prob_low34 | 416 | 34 | 0.521634615 | 0.735294118 | -0.004464906 | -0.000202793 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low34 | 416 | 34 | 0.509615385 | 0.588235294 | -0.004441418 | -0.000179305 | 0.700000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low3 | 447 | 3 | 0.503355705 | 0.666666667 | -0.004432272 | -0.000170159 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | drop_prob_low13 | 437 | 13 | 0.510297483 | 0.769230769 | -0.004398392 | -0.000136279 | 0.600000000 | False |
| hgb_shallow__subject_loo | keep_prob_ge_0p35 | 389 | 61 | 0.524421594 | 0.639344262 | -0.004405997 | -0.000143884 | 0.600000000 | False |
| gb_shallow__subject5 | drop_prob_low3 | 447 | 3 | 0.505592841 | 1.000000000 | -0.004364822 | -0.000102709 | 0.600000000 | False |
| hgb_shallow__subject_loo | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004356766 | -0.000094653 | 0.600000000 | False |
| gb_shallow__subject_loo | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004356766 | -0.000094653 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__rowcontig5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__rowcontig5 | keep_prob_ge_0p4 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | keep_prob_ge_0p4 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004344441 | -0.000082328 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | drop_prob_low34 | 416 | 34 | 0.521634615 | 0.735294118 | -0.004356108 | -0.000093995 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low25 | 425 | 25 | 0.505882353 | 0.560000000 | -0.004367049 | -0.000104936 | 0.700000000 | False |
| hgb_shallow__subject_loo | drop_prob_low3 | 447 | 3 | 0.503355705 | 0.666666667 | -0.004344234 | -0.000082121 | 0.600000000 | False |
| lr_l1_c0p04__subject_loo | drop_prob_low25 | 425 | 25 | 0.510588235 | 0.640000000 | -0.004343581 | -0.000081468 | 0.600000000 | False |
| gb_shallow__stratified5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004298072 | -0.000035959 | 0.600000000 | False |
| gb_shallow__subject5 | drop_prob_low5 | 445 | 5 | 0.503370787 | 0.600000000 | -0.004332217 | -0.000070104 | 0.600000000 | False |
| hgb_shallow__subject5 | drop_prob_low13 | 437 | 13 | 0.508009153 | 0.692307692 | -0.004323163 | -0.000061050 | 0.600000000 | False |
| gb_shallow__subject5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004293972 | -0.000031859 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | drop_prob_low3 | 447 | 3 | 0.503355705 | 0.666666667 | -0.004302803 | -0.000040690 | 0.600000000 | False |
| hgb_shallow__subject5 | drop_prob_low1 | 449 | 1 | 0.503340757 | 1.000000000 | -0.004266938 | -0.000004825 | 0.600000000 | False |
| lr_l1_c0p04__subject5 | drop_prob_low8 | 442 | 8 | 0.506787330 | 0.750000000 | -0.004285747 | -0.000023634 | 0.600000000 | False |
| lr_l1_c0p04__stratified5 | drop_prob_low3 | 447 | 3 | 0.503355705 | 0.666666667 | -0.004289957 | -0.000027843 | 0.600000000 | False |
| lr_l2_c0p10__rowcontig5 | drop_prob_low111 | 339 | 111 | 0.525073746 | 0.567567568 | -0.004314098 | -0.000051985 | 0.700000000 | False |

## Submission-Side Tail Stress

| candidate_id | model_split | gate | pruned_cells_sub | expected_focus | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | oof_gate_pass | e231_tail_gate | joint_gate_pass | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lr_l2_c0p10__rowcontig5__drop_prob_low8 | lr_l2_c0p10__rowcontig5 | drop_prob_low8 | 8 | -0.000615886 | 0.000007466 | 0.000055755 | 0.000722227 | 0.937402675 | 0.002159882 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low13 | lr_l1_c0p04__subject_loo | drop_prob_low13 | 13 | -0.000570334 | 0.000053017 | 0.000074484 | 0.002528884 | 1.584248929 | 0.002141152 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low13 | lr_l2_c0p10__rowcontig5 | drop_prob_low13 | 13 | -0.000601963 | 0.000021389 | 0.000081745 | 0.001498345 | 1.080852026 | 0.002133892 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low8 | lr_l1_c0p04__subject_loo | drop_prob_low8 | 8 | -0.000585485 | 0.000037866 | 0.000040873 | 0.001539154 | 1.262080121 | 0.002174764 | False | False | False |  |
| gb_shallow__subject5__keep_prob_ge_0p35 | gb_shallow__subject5 | keep_prob_ge_0p35 | 20 | -0.000566384 | 0.000056967 | 0.000080358 | 0.003226973 | 1.774926258 | 0.002135279 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low3 | lr_l2_c0p10__rowcontig5 | drop_prob_low3 | 3 | -0.000628938 | -0.000005587 | 0.000029146 | 0.000474380 | 0.833673505 | 0.002186491 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low5 | lr_l1_c0p04__subject_loo | drop_prob_low5 | 5 | -0.000591668 | 0.000031683 | 0.000036733 | 0.001333290 | 1.165368938 | 0.002178904 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low21 | lr_l2_c0p10__rowcontig5 | drop_prob_low21 | 21 | -0.000580551 | 0.000042800 | 0.000113473 | 0.001773123 | 1.413500507 | 0.002102164 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low5 | lr_l2_c0p10__rowcontig5 | drop_prob_low5 | 5 | -0.000619914 | 0.000003437 | 0.000039670 | 0.000329329 | 0.902733504 | 0.002175967 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low21 | lr_l1_c0p04__subject_loo | drop_prob_low21 | 21 | -0.000545808 | 0.000077544 | 0.000114601 | 0.003616182 | 2.699923977 | 0.002101036 | False | False | False |  |
| gb_shallow__subject5__drop_prob_low25 | gb_shallow__subject5 | drop_prob_low25 | 25 | -0.000559828 | 0.000063524 | 0.000127624 | 0.005036107 | 2.013168262 | 0.002088013 | False | False | False |  |
| gb_shallow__subject5__drop_prob_low21 | gb_shallow__subject5 | drop_prob_low21 | 21 | -0.000563921 | 0.000059430 | 0.000097241 | 0.003633446 | 1.857513456 | 0.002118396 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low34 | lr_l2_c0p10__rowcontig5 | drop_prob_low34 | 34 | -0.000549412 | 0.000073940 | 0.000218511 | 0.003800990 | 2.446740603 | 0.001997126 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low111 | lr_l2_c0p10__rowcontig5 | drop_prob_low111 | 111 | -0.000492608 | 0.000130743 | 0.000753734 | 0.013121480 | 4.798082158 | 0.001461903 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low3 | lr_l1_c0p04__subject_loo | drop_prob_low3 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low1 | lr_l2_c0p10__rowcontig5 | drop_prob_low1 | 1 | -0.000630896 | -0.000007545 | 0.000027449 | 0.000382406 | 0.820060097 | 0.002188188 | False | False | False |  |
| hgb_shallow__subject_loo__drop_prob_low1 | hgb_shallow__subject_loo | drop_prob_low1 | 1 | -0.000622785 | 0.000000566 | 0.000003353 | 0.000362226 | 0.879552630 | 0.002212284 | False | False | False |  |
| gb_shallow__subject_loo__drop_prob_low1 | gb_shallow__subject_loo | drop_prob_low1 | 1 | -0.000621872 | 0.000001480 | 0.000003290 | 0.000091243 | 0.886796386 | 0.002212346 | False | False | False |  |
| gb_shallow__subject5__drop_prob_low3 | gb_shallow__subject5 | drop_prob_low3 | 3 | -0.000612246 | 0.000011105 | 0.000011877 | 0.000441950 | 0.971091494 | 0.002203760 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_prob_low25 | lr_l2_c0p10__rowcontig5 | drop_prob_low25 | 25 | -0.000576872 | 0.000046480 | 0.000158672 | 0.002857582 | 1.492424559 | 0.002056965 | False | False | False |  |
| lr_l1_c0p04__subject5__drop_prob_low13 | lr_l1_c0p04__subject5 | drop_prob_low13 | 13 | -0.000570334 | 0.000053017 | 0.000074484 | 0.002528884 | 1.584248929 | 0.002141152 | False | False | False |  |
| lr_l1_c0p04__rowcontig5__drop_prob_low1 | lr_l1_c0p04__rowcontig5 | drop_prob_low1 | 1 | -0.000604866 | 0.000018486 | 0.000020849 | 0.000760040 | 1.001556212 | 0.002194787 | False | False | False |  |
| lr_l1_c0p04__subject5__drop_prob_low1 | lr_l1_c0p04__subject5 | drop_prob_low1 | 1 | -0.000604866 | 0.000018486 | 0.000020849 | 0.000760040 | 1.001556212 | 0.002194787 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low1 | lr_l1_c0p04__subject_loo | drop_prob_low1 | 1 | -0.000604866 | 0.000018486 | 0.000020849 | 0.000760040 | 1.001556212 | 0.002194787 | False | False | False |  |
| lr_l1_c0p04__rowcontig5__keep_prob_ge_0p4 | lr_l1_c0p04__rowcontig5 | keep_prob_ge_0p4 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |
| lr_l1_c0p04__subject5__keep_prob_ge_0p4 | lr_l1_c0p04__subject5 | keep_prob_ge_0p4 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |
| hgb_shallow__subject_loo__drop_prob_low3 | hgb_shallow__subject_loo | drop_prob_low3 | 3 | -0.000619320 | 0.000004032 | 0.000007975 | 0.000518200 | 0.907689374 | 0.002207662 | False | False | False |  |
| gb_shallow__subject_loo__drop_prob_low111 | gb_shallow__subject_loo | drop_prob_low111 | 111 | -0.000476310 | 0.000147042 | 0.000829677 | 0.020784584 | 2.542493379 | 0.001385960 | False | False | False |  |
| gb_shallow__stratified5__drop_prob_low1 | gb_shallow__stratified5 | drop_prob_low1 | 1 | -0.000621872 | 0.000001480 | 0.000003290 | 0.000091243 | 0.886796386 | 0.002212346 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low13 | hgb_shallow__subject5 | drop_prob_low13 | 13 | -0.000601973 | 0.000021378 | 0.000053901 | 0.002687419 | 1.080725987 | 0.002161736 | False | False | False |  |
| gb_shallow__subject5__drop_prob_low1 | gb_shallow__subject5 | drop_prob_low1 | 1 | -0.000621872 | 0.000001480 | 0.000003290 | 0.000091243 | 0.886796386 | 0.002212346 | False | False | False |  |
| gb_shallow__subject5__drop_prob_low5 | gb_shallow__subject5 | drop_prob_low5 | 5 | -0.000606392 | 0.000016960 | 0.000016065 | 0.000464439 | 1.030677951 | 0.002199572 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low1 | hgb_shallow__subject5 | drop_prob_low1 | 1 | -0.000622785 | 0.000000566 | 0.000003353 | 0.000362226 | 0.879552630 | 0.002212284 | False | False | False |  |
| lr_l1_c0p04__subject5__drop_prob_low3 | lr_l1_c0p04__subject5 | drop_prob_low3 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |
| lr_l1_c0p04__stratified5__drop_prob_low3 | lr_l1_c0p04__stratified5 | drop_prob_low3 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |
| lr_l2_c0p10__rowcontig5__drop_risk_top13 | lr_l2_c0p10__rowcontig5 | drop_risk_top13 | 13 | -0.000554734 | 0.000068617 | 0.000300375 | 0.003805493 | 2.014657323 | 0.001915262 | False | False | False |  |
| hgb_shallow__rowcontig5__drop_prob_low3 | hgb_shallow__rowcontig5 | drop_prob_low3 | 3 | -0.000619320 | 0.000004032 | 0.000007975 | 0.000518200 | 0.907689374 | 0.002207662 | False | False | False |  |
| lr_l1_c0p04__subject5__drop_prob_low8 | lr_l1_c0p04__subject5 | drop_prob_low8 | 8 | -0.000585485 | 0.000037866 | 0.000040873 | 0.001539154 | 1.262080121 | 0.002174764 | False | False | False |  |
| hgb_shallow__rowcontig5__drop_prob_low5 | hgb_shallow__rowcontig5 | drop_prob_low5 | 5 | -0.000615905 | 0.000007447 | 0.000010447 | 0.000632184 | 0.937230333 | 0.002205190 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low25 | hgb_shallow__subject5 | drop_prob_low25 | 25 | -0.000562279 | 0.000061072 | 0.000134811 | 0.004995214 | 1.833012810 | 0.002080826 | False | False | False |  |
| lr_l1_c0p04__stratified5__keep_prob_ge_0p35 | lr_l1_c0p04__stratified5 | keep_prob_ge_0p35 | 0 | -0.000623352 | 0.000000000 | 0.000000000 | 0.000000000 | 0.875120489 | 0.002215637 | False | False | False |  |
| lr_l1_c0p04__rowcontig5__keep_prob_ge_0p35 | lr_l1_c0p04__rowcontig5 | keep_prob_ge_0p35 | 0 | -0.000623352 | 0.000000000 | 0.000000000 | 0.000000000 | 0.875120489 | 0.002215637 | False | False | False |  |
| lr_l1_c0p04__subject5__keep_prob_ge_0p35 | lr_l1_c0p04__subject5 | keep_prob_ge_0p35 | 0 | -0.000623352 | 0.000000000 | 0.000000000 | 0.000000000 | 0.875120489 | 0.002215637 | False | False | False |  |
| lr_l1_c0p04__subject_loo__keep_prob_ge_0p35 | lr_l1_c0p04__subject_loo | keep_prob_ge_0p35 | 0 | -0.000623352 | 0.000000000 | 0.000000000 | 0.000000000 | 0.875120489 | 0.002215637 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low3 | hgb_shallow__subject5 | drop_prob_low3 | 3 | -0.000619320 | 0.000004032 | 0.000007975 | 0.000518200 | 0.907689374 | 0.002207662 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low80 | hgb_shallow__subject5 | drop_prob_low80 | 80 | -0.000461339 | 0.000162012 | 0.000546098 | 0.011441567 | 1.775749307 | 0.001669539 | False | False | False |  |
| hgb_shallow__subject5__drop_prob_low5 | hgb_shallow__subject5 | drop_prob_low5 | 5 | -0.000615905 | 0.000007447 | 0.000010447 | 0.000632184 | 0.937230333 | 0.002205190 | False | False | False |  |
| hgb_shallow__subject_loo__drop_prob_low25 | hgb_shallow__subject_loo | drop_prob_low25 | 25 | -0.000562279 | 0.000061072 | 0.000134811 | 0.004995214 | 1.833012810 | 0.002080826 | False | False | False |  |
| lr_l1_c0p04__subject_loo__drop_prob_low25 | lr_l1_c0p04__subject_loo | drop_prob_low25 | 25 | -0.000538146 | 0.000085205 | 0.000128406 | 0.004076940 | 3.461342035 | 0.002087231 | False | False | False |  |
| lr_l1_c0p04__subject_loo__keep_prob_ge_0p4 | lr_l1_c0p04__subject_loo | keep_prob_ge_0p4 | 3 | -0.000596619 | 0.000026733 | 0.000030690 | 0.001115436 | 1.098007307 | 0.002184947 | False | False | False |  |

## Target Breakdown

| candidate_id | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| gb_shallow__rowcontig5__drop_prob_low1 | Q3 | 249 | -0.000110892 | 0.002212346 | 0.455608013 | 0.886796386 |
| gb_shallow__rowcontig5__drop_prob_low1 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low111 | Q3 | 139 | 0.000034671 | 0.001385960 | 0.493918630 | 2.542493379 |
| gb_shallow__rowcontig5__drop_prob_low111 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low13 | Q3 | 237 | -0.000080457 | 0.002171892 | 0.458942483 | 1.222248080 |
| gb_shallow__rowcontig5__drop_prob_low13 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low21 | Q3 | 229 | -0.000052941 | 0.002118396 | 0.460937282 | 1.857513456 |
| gb_shallow__rowcontig5__drop_prob_low21 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low25 | Q3 | 225 | -0.000048848 | 0.002088013 | 0.463227791 | 2.013168262 |
| gb_shallow__rowcontig5__drop_prob_low25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low3 | Q3 | 247 | -0.000101266 | 0.002203760 | 0.456109011 | 0.971091494 |
| gb_shallow__rowcontig5__drop_prob_low3 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low34 | Q3 | 216 | -0.000013044 | 0.002004884 | 0.466390048 | 7.208881464 |
| gb_shallow__rowcontig5__drop_prob_low34 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low5 | Q3 | 245 | -0.000095411 | 0.002199572 | 0.456102261 | 1.030677951 |
| gb_shallow__rowcontig5__drop_prob_low5 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low55 | Q3 | 195 | 0.000015878 | 0.001865335 | 0.471994317 | 5.922254966 |
| gb_shallow__rowcontig5__drop_prob_low55 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low8 | Q3 | 242 | -0.000090648 | 0.002193410 | 0.456893566 | 1.084833817 |
| gb_shallow__rowcontig5__drop_prob_low8 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_prob_low80 | Q3 | 170 | 0.000023302 | 0.001700580 | 0.479073502 | 3.782952748 |
| gb_shallow__rowcontig5__drop_prob_low80 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top1 | Q3 | 249 | -0.000093885 | 0.002194787 | 0.456566617 | 1.001556212 |
| gb_shallow__rowcontig5__drop_risk_top1 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top111 | Q3 | 139 | -0.000008391 | 0.000587764 | 0.509383153 | 2.983513528 |
| gb_shallow__rowcontig5__drop_risk_top111 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top13 | Q3 | 237 | -0.000081361 | 0.001842094 | 0.463430506 | 0.757972648 |
| gb_shallow__rowcontig5__drop_risk_top13 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top21 | Q3 | 229 | -0.000106140 | 0.001667257 | 0.473217334 | 0.471744446 |
| gb_shallow__rowcontig5__drop_risk_top21 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top25 | Q3 | 225 | -0.000091006 | 0.001614451 | 0.476693375 | 0.550194972 |
| gb_shallow__rowcontig5__drop_risk_top25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top3 | Q3 | 247 | -0.000097744 | 0.002126212 | 0.459113482 | 0.901841848 |
| gb_shallow__rowcontig5__drop_risk_top3 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top34 | Q3 | 216 | -0.000086280 | 0.001485176 | 0.486107616 | 0.580330545 |
| gb_shallow__rowcontig5__drop_risk_top34 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top5 | Q3 | 245 | -0.000062977 | 0.002085916 | 0.457724240 | 1.399721237 |
| gb_shallow__rowcontig5__drop_risk_top5 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top55 | Q3 | 195 | -0.000039540 | 0.001238397 | 0.498825357 | 1.266331703 |
| gb_shallow__rowcontig5__drop_risk_top55 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top8 | Q3 | 242 | -0.000061477 | 0.001981233 | 0.459958386 | 1.164242246 |
| gb_shallow__rowcontig5__drop_risk_top8 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__drop_risk_top80 | Q3 | 170 | -0.000034678 | 0.000866020 | 0.496359882 | 0.910226821 |
| gb_shallow__rowcontig5__drop_risk_top80 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__keep_prob_ge_0p35 | Q3 | 230 | -0.000055404 | 0.002135279 | 0.460317987 | 1.774926258 |
| gb_shallow__rowcontig5__keep_prob_ge_0p35 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__keep_prob_ge_0p4 | Q3 | 210 | -0.000005802 | 0.001970548 | 0.468580744 | 16.205416252 |
| gb_shallow__rowcontig5__keep_prob_ge_0p4 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| gb_shallow__rowcontig5__keep_prob_ge_0p45 | Q3 | 169 | 0.000024156 | 0.001699917 | 0.478986147 | 3.649241250 |
| gb_shallow__rowcontig5__keep_prob_ge_0p45 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |

## Decision

- No E231 learned Q3 support prune passed both OOF preservation and submission-side tail stress.
- E230 remains a conditional hand-prune after E224 feedback, not a first-class learned translator.
