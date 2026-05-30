# E254 E237/E250 Conflict Atlas

## Question

Why does train OOF prefer the E237/E250 shared Q3 intersection while submission-side materialization rejects it and prefers the union?

## Train OOF Q3 Groups

| group | n | benefit_mean | benefit_median | benefit_min | benefit_max | benefit_negative_rate | true_label_mean | base_prob_mean | full_prob_mean | abs_logit_step_mean | featnn1_dist_mean | featnn1_total_smooth_gain_mean | featnn1_full_pair_abs_logit_mean | p237_bad_mean | p250_bad_mean | pmax_bad_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shared | 12 | -0.028234084 | -0.069954685 | -0.161717290 | 0.132723310 | 0.583333333 | 0.416666667 | 0.533818299 | 0.556212982 | 0.210574932 | 10.409809604 | -0.086783657 | 0.385045457 | 0.483922491 | 0.479051884 | 0.529962545 |
| e237_only | 13 | 0.007270138 | 0.052327050 | -0.092299663 | 0.110995932 | 0.461538462 | 0.846153846 | 0.526850588 | 0.525464492 | 0.163170210 | 8.077835234 | 0.058562462 | 0.437162349 | 0.423845929 | 0.272634915 | 0.423845929 |
| e250_only | 9 | 0.019143125 | 0.038146763 | -0.108784092 | 0.185843015 | 0.444444444 | 0.444444444 | 0.498599325 | 0.506521204 | 0.189447170 | 9.453903987 | 0.090721470 | 0.404366674 | 0.260540436 | 0.467798086 | 0.467798086 |
| union | 34 | -0.002117914 | -0.001329772 | -0.161717290 | 0.185843015 | 0.500000000 | 0.588235294 | 0.521831505 | 0.531302500 | 0.186856954 | 9.265138505 | 0.015776510 | 0.410086944 | 0.401821497 | 0.397148802 | 0.472933247 |
| none | 416 | 0.004783558 | 0.000350381 | -0.120775745 | 0.268232541 | 0.497596154 | 0.600961538 | 0.612448355 | 0.610277445 | 0.063740693 | 7.104939223 | -0.011038266 | 0.396685121 | 0.054045586 | 0.053616959 | 0.062641534 |

## Test Q3 Hard-Tail Anatomy

| group | n_context | base_prob_mean | full_prob_mean | abs_logit_step_mean | featnn1_dist_mean | featnn1_total_smooth_gain_mean | featnn1_full_pair_abs_logit_mean | n_cells | e224_expected_focus_sum | e224_adverse_sum | support_prob_focus_weighted | top1_over_abs_expected | swing_sum | support_delta_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shared | 15 | 0.536178325 | 0.525399759 | 0.213332686 | 10.867345766 | 0.045483688 | 0.521005845 | 15 | -0.000028815 | 0.000379666 | 0.446777341 | 3.412733926 | 0.000914283 | -0.000534617 |
| e237_only | 10 | 0.549414689 | 0.514253567 | 0.144132904 | 8.019274101 | -0.028701735 | 0.380915673 | 10 | 0.000034427 | 0.000196734 | 0.394133226 | 1.791327111 | 0.000411808 | -0.000215074 |
| e250_only | 6 | 0.615787817 | 0.584255734 | 0.175699303 | 10.287034807 | -0.075050387 | 0.656719826 | 6 | 0.000029661 | 0.000144605 | 0.381622909 | 2.971943888 | 0.000301199 | -0.000156594 |
| union | 31 | 0.555856409 | 0.533195692 | 0.183726295 | 9.836294721 | -0.001776269 | 0.502082689 | 31 | 0.000035272 | 0.000721005 | 0.421395437 | 2.787994043 | 0.001627290 | -0.000906285 |
| none | 219 | 0.618352307 | 0.615723208 | 0.055677795 | 7.109991309 | -0.006987004 | 0.477522008 | 219 | -0.000147644 | 0.001494632 | 0.471398253 | 0.506203451 | 0.003483839 | -0.001989207 |

## Largest Train/Test Feature Shifts

| group | feature | train_mean | test_mean | std_diff_test_minus_train | abs_std_diff | train_n | test_n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e250_only | prob_gap | 0.007921878 | -0.031532083 | -1.804341923 | 1.804341923 | 9 | 6 |
| e250_only | logit_step | 0.033605161 | -0.126688563 | -1.665033410 | 1.665033410 | 9 | 6 |
| e237_only | prob_gap | -0.001386096 | -0.035161122 | -1.544628032 | 1.544628032 | 13 | 10 |
| shared | prob_gap | 0.022394683 | -0.010778566 | -1.517107047 | 1.517107047 | 12 | 15 |
| union | prob_gap | 0.009470996 | -0.022660716 | -1.469474610 | 1.469474610 | 34 | 31 |
| shared | logit_step | 0.095319328 | -0.046094061 | -1.468916003 | 1.468916003 | 12 | 15 |
| e237_only | logit_step | -0.008920386 | -0.144132904 | -1.404505133 | 1.404505133 | 13 | 10 |
| union | logit_step | 0.039126864 | -0.093318430 | -1.375760901 | 1.375760901 | 34 | 31 |
| e250_only | featnn1_total_smooth_gain_mean | 0.055087779 | -0.062185635 | -1.350065058 | 1.350065058 | 9 | 6 |
| e250_only | featnn1_total_smooth_gain | 0.090721470 | -0.075050387 | -1.233640625 | 1.233640625 | 9 | 6 |
| e250_only | featnn1_base_prob_absdiff | 0.077654560 | 0.175689627 | 1.075986489 | 1.075986489 | 9 | 6 |
| e250_only | featnn1_base_pair_abs_logit | 0.320596948 | 0.728988685 | 1.010810789 | 1.010810789 | 9 | 6 |
| shared | featnn1_total_smooth_gain | -0.086783657 | 0.045483688 | 0.984306823 | 0.984306823 | 12 | 15 |
| e250_only | base_prob | 0.498599325 | 0.615787817 | 0.886877192 | 0.886877192 | 9 | 6 |
| shared | featnn1_total_smooth_gain_mean | -0.046318986 | 0.023061496 | 0.798716111 | 0.798716111 | 12 | 15 |
| e237_only | featnn1_logit_step_absdiff | 0.126205810 | 0.082084122 | -0.703520498 | 0.703520498 | 13 | 10 |
| e250_only | featnn1_full_prob_absdiff | 0.098533643 | 0.158086360 | 0.679835029 | 0.679835029 | 9 | 6 |
| e250_only | featnn1_full_pair_abs_logit | 0.404366674 | 0.656719826 | 0.650091788 | 0.650091788 | 9 | 6 |
| e237_only | featnn1_total_smooth_gain | 0.058562462 | -0.028701735 | -0.649402502 | 0.649402502 | 13 | 10 |
| e250_only | full_prob | 0.506521204 | 0.584255734 | 0.604533065 | 0.604533065 | 9 | 6 |
| shared | base_margin | 0.074191258 | 0.119914972 | 0.484952184 | 0.484952184 | 12 | 15 |
| e250_only | featnn1_dist | 9.453903987 | 10.287034807 | 0.373235651 | 0.373235651 | 9 | 6 |
| shared | featnn1_full_prob_absdiff | 0.091094171 | 0.123624504 | 0.371356021 | 0.371356021 | 12 | 15 |
| shared | featnn1_full_pair_abs_logit | 0.385045457 | 0.521005845 | 0.350250161 | 0.350250161 | 12 | 15 |
| e250_only | featnn1_logit_step_absdiff | 0.143376071 | 0.123642293 | -0.314655157 | 0.314655157 | 9 | 6 |
| e250_only | base_margin | 0.087634639 | 0.115787817 | 0.298596598 | 0.298596598 | 9 | 6 |
| e237_only | abs_logit_step | 0.163170210 | 0.144132904 | -0.293847159 | 0.293847159 | 13 | 10 |
| union | base_margin | 0.078475830 | 0.105688400 | 0.288620374 | 0.288620374 | 34 | 31 |
| union | featnn1_base_prob_absdiff | 0.092255595 | 0.118182357 | 0.284559865 | 0.284559865 | 34 | 31 |
| union | featnn1_base_pair_abs_logit | 0.387337163 | 0.502101742 | 0.284053925 | 0.284053925 | 34 | 31 |

## Interpretation

- Train shared cells are OOF-harmful to keep: benefit_mean `-0.028234084` and negative-rate `0.583333`.
- Test shared cells look useful to keep under hard-tail priors: E224 expected sum `-0.000028815` and top1/abs `3.412733926`.
- Test union flips the hard-tail anatomy by adding parent-specific cells: E224 expected sum `0.000035272` versus train union benefit_mean `-0.002117914`.
- This is a concrete validation-geometry mismatch: overlap/consensus is a good OOF target but a bad public-free hard-tail target.

## Decision

- Do not build an intersection submission despite its OOF strength.
- Do not promote E252 as OOF-certified despite its materialization strength.
- The next useful target is a contrastive head that explicitly separates OOF-harmful consensus cells from test hard-tail-adverse parent-specific cells.
- Public LB is not used and no submission is created.
