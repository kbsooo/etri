# H011 H010 Public-Inversion Jackpot

## Question

H010 looked locally correct but failed public by `+0.0020128681` versus E247. Is the H010 S1/S4 action axis actually a public-negative target representation?

## Worldview

HS-JEPA should not only predict labels. It should predict whether a proposed human-state action is healthy for the public/test world. H010 becomes the first explicit public-bad action-health teacher.

## Falsifiable Claim

If the public subset wants the opposite objective-stage route, candidates with negative projection onto the H010 action axis should move public LB meaningfully below E247. If they do not, the anti-H010-route worldview is dead and H010 was just an overfit local rank rewrite.

## Output

- generated candidates: `63`
- public inversion jackpot/high-risk candidates: `33`
- primary upload-safe file: `submission_h011_public_inversion_rowtop_all_k50_a1_uploadsafe.csv`

## Top Selection

| candidate_id | h011_decision | family | target_subset | changed_cells | h010_axis_coeff | h010_axis_public_delta_linear | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | max_abs_prob_delta | mean_agreement_on_changed | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rowtop_all_k50_a1 | public_inversion_jackpot | row_top | all | 100 | -0.545892324 | -0.001098809 | 0.000200937 | 0.000573326 | 0.256250000 | 0.098995999 | 0.090000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k50_a1_afd09a35.csv |
| mirror_all_a0.5 | public_inversion_jackpot | mirror | all | 500 | -0.500000000 | -0.001006434 | 0.000134660 | 0.000644352 | 0.385416667 | 0.050603316 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a0.5_c4b10334.csv |
| rowtop_all_k180_a0.5 | public_inversion_jackpot | row_top | all | 360 | -0.482603695 | -0.000971418 | 0.000125261 | 0.000595061 | 0.393750000 | 0.050603316 | 0.091666667 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k180_a0.5_7d8e996f.csv |
| rowtop_all_k35_a1 | public_inversion_jackpot | row_top | all | 70 | -0.438224013 | -0.000882087 | 0.000158134 | 0.000478479 | 0.279166667 | 0.098995999 | 0.128571429 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k35_a1_920ef4b5.csv |
| rowtop_all_k120_a0.5 | public_inversion_jackpot | row_top | all | 240 | -0.417289587 | -0.000839949 | 0.000101805 | 0.000454915 | 0.395833333 | 0.050603316 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k120_a0.5_11852cb0.csv |
| rowtop_all_k20_a1.5 | public_inversion_jackpot | row_top | all | 40 | -0.431664496 | -0.000868884 | 0.000221697 | 0.000595364 | 0.281250000 | 0.144353766 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k20_a1.5_8dcb1350.csv |
| mirror_S4_a0.75 | public_inversion_jackpot | mirror | S4 | 250 | -0.410731952 | -0.000826749 | 0.000177008 | 0.000725562 | 0.391666667 | 0.075132292 | 0.016000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S4_a0.75_e02c9df6.csv |
| rowtop_all_k80_a0.5 | public_inversion_jackpot | row_top | all | 160 | -0.349644340 | -0.000703788 | 0.000081068 | 0.000339343 | 0.404166667 | 0.050603316 | 0.087500000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k80_a0.5_16569978.csv |
| mirror_S1_a0.75 | public_inversion_jackpot | mirror | S1 | 250 | -0.339268048 | -0.000682902 | 0.000089628 | 0.000281111 | 0.295833333 | 0.063385726 | 0.172000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S1_a0.75_d7edc3c8.csv |
| rowbottom_all_k180_a1 | public_inversion_jackpot | row_bottom | all | 360 | -0.342739811 | -0.000689890 | 0.000181361 | 0.000803346 | 0.320833333 | 0.059408762 | 0.097222222 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowbottom_all_k180_a1_b937a65a.csv |
| rowtop_all_k20_a1 | public_inversion_jackpot | row_top | all | 40 | -0.287776331 | -0.000579256 | 0.000104440 | 0.000329821 | 0.387500000 | 0.098995999 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k20_a1_258c5fcc.csv |
| rowtop_all_k50_a0.5 | public_inversion_jackpot | row_top | all | 100 | -0.272946162 | -0.000549405 | 0.000060277 | 0.000237300 | 0.406250000 | 0.050603316 | 0.090000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k50_a0.5_17d445b6.csv |
| mirror_S4_a0.5 | public_inversion_jackpot | mirror | S4 | 250 | -0.273821301 | -0.000551166 | 0.000094421 | 0.000421587 | 0.397916667 | 0.050603316 | 0.016000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S4_a0.5_7c930c9d.csv |
| mirror_all_a0.25 | public_inversion_jackpot | mirror | all | 500 | -0.250000000 | -0.000503217 | 0.000046281 | 0.000237802 | 0.397916667 | 0.025518894 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a0.25_1ec78ee1.csv |
| mirror_S1_a0.5 | public_inversion_jackpot | mirror | S1 | 250 | -0.226178699 | -0.000455268 | 0.000040882 | 0.000163498 | 0.295833333 | 0.041743146 | 0.172000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S1_a0.5_df341751.csv |
| rowtop_all_k35_a0.5 | public_inversion_jackpot | row_top | all | 70 | -0.219112007 | -0.000441044 | 0.000047611 | 0.000203866 | 0.391666667 | 0.050603316 | 0.128571429 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k35_a0.5_bf19446c.csv |
| rowbottom_all_k120_a1.5 | public_inversion_jackpot | row_bottom | all | 240 | -0.206244386 | -0.000415143 | 0.000153471 | 0.000621872 | 0.256250000 | 0.069170198 | 0.087500000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowbottom_all_k120_a1.5_39d485a2.csv |
| rowtop_all_k180_a1.5 | public_inversion_high_risk | row_top | all | 360 | -1.447811084 | -0.002914253 | 0.000750808 | 0.002409902 | 0.250000000 | 0.144353766 | 0.091666667 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k180_a1.5_10a8893c.csv |
| mirror_all_a1.25 | public_inversion_high_risk | mirror | all | 500 | -1.250000000 | -0.002516085 | 0.000589294 | 0.002075646 | 0.250000000 | 0.122097464 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a1.25_af23b4cc.csv |
| rowtop_all_k120_a1.5 | public_inversion_high_risk | row_top | all | 240 | -1.251868762 | -0.002519847 | 0.000632055 | 0.001827425 | 0.245833333 | 0.144353766 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k120_a1.5_b072a4db.csv |
| rowtop_all_k80_a1.5 | public_inversion_high_risk | row_top | all | 160 | -1.048933019 | -0.002111364 | 0.000521916 | 0.001360609 | 0.252083333 | 0.144353766 | 0.087500000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k80_a1.5_cae0d304.csv |
| mirror_all_a1 | public_inversion_high_risk | mirror | all | 500 | -1.000000000 | -0.002012868 | 0.000411564 | 0.001578429 | 0.250000000 | 0.098995999 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a1_7df70546.csv |
| rowtop_all_k180_a1 | public_inversion_high_risk | row_top | all | 360 | -0.965207389 | -0.001942835 | 0.000389283 | 0.001462764 | 0.252083333 | 0.098995999 | 0.091666667 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k180_a1_19240868.csv |
| rowtop_all_k120_a1 | public_inversion_high_risk | row_top | all | 240 | -0.834579174 | -0.001679898 | 0.000324436 | 0.001115580 | 0.252083333 | 0.098995999 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k120_a1_872b5596.csv |
| rowtop_all_k50_a1.5 | public_inversion_high_risk | row_top | all | 100 | -0.818838487 | -0.001648214 | 0.000408665 | 0.001014807 | 0.247916667 | 0.144353766 | 0.090000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k50_a1.5_201837bd.csv |
| mirror_all_a0.75 | public_inversion_high_risk | mirror | all | 500 | -0.750000000 | -0.001509651 | 0.000257437 | 0.001099365 | 0.320833333 | 0.075132292 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a0.75_4978281d.csv |
| rowtop_all_k80_a1 | public_inversion_high_risk | row_top | all | 160 | -0.699288679 | -0.001407576 | 0.000262389 | 0.000834788 | 0.258333333 | 0.098995999 | 0.087500000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k80_a1_28e5258a.csv |
| mirror_S4_a1.25 | public_inversion_high_risk | mirror | S4 | 250 | -0.684553254 | -0.001377915 | 0.000399557 | 0.001371700 | 0.254166667 | 0.122097464 | 0.016000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S4_a1.25_f93d1b7d.csv |
| rowtop_all_k35_a1.5 | public_inversion_high_risk | row_top | all | 70 | -0.657336020 | -0.001323131 | 0.000327288 | 0.000852115 | 0.216666667 | 0.144353766 | 0.128571429 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k35_a1.5_48d796ff.csv |
| mirror_S1_a1.25 | public_inversion_high_risk | mirror | S1 | 250 | -0.565446746 | -0.001138170 | 0.000231298 | 0.000669068 | 0.162500000 | 0.107833879 | 0.172000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S1_a1.25_70b9b8ad.csv |
| mirror_S4_a1 | public_inversion_high_risk | mirror | S4 | 250 | -0.547642603 | -0.001102332 | 0.000280262 | 0.001043006 | 0.318750000 | 0.098995999 | 0.016000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S4_a1_4cef4f0d.csv |
| rowbottom_all_k180_a1.5 | public_inversion_high_risk | row_bottom | all | 360 | -0.514109717 | -0.001034835 | 0.000346757 | 0.001318006 | 0.250000000 | 0.088703324 | 0.097222222 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowbottom_all_k180_a1.5_caff8d61.csv |
| mirror_S1_a1 | public_inversion_high_risk | mirror | S1 | 250 | -0.452357397 | -0.000910536 | 0.000153870 | 0.000462802 | 0.222916667 | 0.085443454 | 0.172000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S1_a1_1e164e2c.csv |
| rowbottom_all_k180_a0.5 | reject | row_bottom | all | 360 | -0.171369906 | -0.000344945 | 0.000061748 | 0.000323033 | 0.387500000 | 0.029772076 | 0.097222222 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowbottom_all_k180_a0.5_b6ec518f.csv |
| rowtop_all_k20_a0.5 | reject | row_top | all | 40 | -0.143888165 | -0.000289628 | 0.000030658 | 0.000143569 | 0.433333333 | 0.050603316 | 0.100000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowtop_all_k20_a0.5_178859bb.csv |
| mirror_S4_a0.25 | reject | mirror | S4 | 250 | -0.136910651 | -0.000275583 | 0.000033168 | 0.000152992 | 0.400000000 | 0.025518894 | 0.016000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S4_a0.25_c5ed9cb5.csv |
| rowbottom_all_k120_a1 | reject | row_bottom | all | 240 | -0.137496258 | -0.000276762 | 0.000076887 | 0.000378760 | 0.283333333 | 0.046253029 | 0.087500000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_rowbottom_all_k120_a1_befdeab2.csv |
| mirror_all_a0.125 | reject | mirror | all | 499 | -0.125000000 | -0.000251609 | 0.000016798 | 0.000090370 | 0.397916667 | 0.012805816 | 0.094000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_all_a0.125_d40b1d96.csv |
| mirror_S1_a0.25 | reject | mirror | S1 | 250 | -0.113089349 | -0.000227634 | 0.000012345 | 0.000070422 | 0.414583333 | 0.020591708 | 0.172000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_mirror_S1_a0.25_0129632a.csv |
| badagree_all_ge1_a1.5 | reject | bad_agree | all | 47 | -0.117318813 | -0.000236147 | 0.000101424 | 0.000403489 | 0.402083333 | 0.113038467 | 1.000000000 | hitl/h011_h010_public_inversion_jackpot/submission_h011_badagree_all_ge1_a1.5_401854da.csv |

## Selector Context

The selector is now calibrated with E368 and H010 as known observations in `analysis_outputs/public_probe_observations.csv`. H011 is still a big-bet extrapolation, not a conservative promotion.

## Files

- `hitl/h011_h010_public_inversion_jackpot/h011_candidates.csv`
- `hitl/h011_h010_public_inversion_jackpot/h011_action_anatomy.csv`
- `hitl/h011_h010_public_inversion_jackpot/h011_selector_scores.csv`
- `hitl/h011_h010_public_inversion_jackpot/h011_selection.csv`
