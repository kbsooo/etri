# H093 Masked Low-Overlap Support HS-JEPA

Question: can raw human day-block context predict action-grade support outside
the known H087/H088/H091/H092 selected-cell basin?

Worldview:

- H092 learned raw context well but selected mostly known support.
- H093 changes the JEPA target to masked low-overlap support, so the predictor
  must learn route-action candidates that are both locally action-grade and
  outside the current root supports.
- This is a target-representation bet, not a top-k or alpha tweak.

OOF Masked Latent Diagnostics:

| head | target_mean | pred_mean | pred_std | spearman_oof | auc_top25_oof | auc_top10_oof |
| --- | --- | --- | --- | --- | --- | --- |
| white | 0.312224709 | 0.309364561 | 0.100479579 | 0.586722464 | 0.814679471 | 0.787278803 |
| white_private | 0.369684650 | 0.366428628 | 0.127233963 | 0.591538703 | 0.817038339 | 0.782857574 |
| white_public | 0.371653369 | 0.369327308 | 0.111311086 | 0.700087790 | 0.846262212 | 0.851463936 |
| white_objective | 0.390595662 | 0.388436809 | 0.090769329 | 0.704810586 | 0.881769073 | 0.891219843 |
| white_q2 | 0.354059028 | 0.351243799 | 0.117032426 | 0.658096826 | 0.866260215 | 0.919361428 |
| overall | 0.358525572 | 0.355397609 | 0.079230312 | 0.512311389 | 0.757114134 | 0.731614383 |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_masked_lowoverlap_support_bigbet | h093_masked_extreme_white_c420_r140_q80_5f023312 | /Users/kbsoo/Downloads/cl2/submission_h093_masked_lowoverlap_5f023312_uploadsafe.csv | raw context predicts new row-target support beyond known public/private basin |

Candidates:

| candidate_id | spec_name | target_group | value_modes | novelty_bonus | alpha | cap | selected_routes | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | q2_cells | posterior_delta_vs_h057 | hard_delta_vs_h057 | source_proxy_delta_vs_h057 | responsibility_weighted_delta_vs_h057 | max_positive_bad_cosine | source_agree_rate | h082_ratio | mean_bad_same_rank | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | route_templates | h087_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | profile | h093_novelty | h093_score | mean_masked_latent_score | mean_masked_head_score | mean_action_max_known_overlap | mean_action_known_white_rank | masked_head_mix | max_selected_cell_known_overlap | selected_cell_overlap_h087 | selected_cell_overlap_h088 | selected_cell_overlap_h091 | selected_cell_overlap_h092 | min_cells_for_root |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h093_masked_extreme_white_c420_r140_q80_5f023312 | masked_extreme_white_c420_r140_q80 | all | hard_source_bridge,triad_consensus | masked_extreme_new_support | 1.250000000 | 2.250000000 | 3 | 21 | 21 | 3 | 3 | -0.000007881 | 0.000000123 | 0.000000001 | -0.000007699 | 0.000000000 | 0.523809524 | 0.285714286 | 0.562476190 | 0.000111098 | 0.038811945 | 3 | 34,92,136 | full_state:3 | 0.125782278 | submission_h093_masked_extreme_white_c420_r140_q80_5f023312.csv | /Users/kbsoo/Downloads/cl2/hitl/h093_masked_lowoverlap_support_hsjepa/submission_h093_masked_extreme_white_c420_r140_q80_5f023312.csv | 3 | 3 | 3 | 3 | 3 | 3 | 3 | /Users/kbsoo/Downloads/cl2/hitl/h093_masked_lowoverlap_support_hsjepa/submission_h093_masked_extreme_white_c420_r140_q80_5f023312.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999998836 | 21 | True | white_extreme | masked_extreme_new_support | 0.458184263 | 0.532824238 | 0.636441160 | 0.476190476 | 0.841986128 | white_q2:3 | 0.476190476 | 0.190476190 | 0.476190476 | 0.000000000 | 0.000000000 | 70 |
| h093_masked_white_bridge_c1080_r220_q125_1711254c | masked_white_bridge_c1080_r220_q125 | all | h085_hard_bridge | masked_lowoverlap_bridge_to_scale | 1.160000000 | 2.050000000 | 2 | 14 | 14 | 2 | 2 | -0.000005031 | -0.000000322 | -0.000000003 | -0.000004991 | 0.000000000 | 0.714285714 | 0.428571429 | 0.458040816 | 0.000093450 | 0.039281234 | 2 | 37,217 | full_state:2 | 0.174025327 | submission_h093_masked_white_bridge_c1080_r220_q125_1711254c.csv | /Users/kbsoo/Downloads/cl2/hitl/h093_masked_lowoverlap_support_hsjepa/submission_h093_masked_white_bridge_c1080_r220_q125_1711254c.csv | 2 | 2 | 2 | 2 | 2 | 2 | 2 | /Users/kbsoo/Downloads/cl2/hitl/h093_masked_lowoverlap_support_hsjepa/submission_h093_masked_white_bridge_c1080_r220_q125_1711254c.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 14 | True | white_bridge | masked_lowoverlap_bridge_to_scale | 0.341798082 | 0.579286399 | 0.633363091 | 0.857142857 | 0.703682349 | white_q2:2 | 0.857142857 | 0.428571429 | 0.857142857 | 0.428571429 | 0.428571429 | 260 |

Top Masked Route Actions:

| route_id | row | subject_id | route_name | targets | value_mode | masked_head | masked_latent_score | masked_overall_oof | masked_head_score | known_white_rank | max_known_overlap_ratio | mean_known_overlap_ratio | raw_transition_q | posterior_delta_sum | hard_delta_sum | source_proxy_sum | dual_pareto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r140_full_state | 140 | id06 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.656134524 | 0.557628898 | 0.672287766 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.011578987 | -0.012023687 | -0.000007513 | 1.000000000 |
| r140_full_state | 140 | id06 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.656062629 | 0.557446324 | 0.672274748 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.009371618 | -0.007103314 | -0.000005437 | 1.000000000 |
| r140_full_state | 140 | id06 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.655993419 | 0.557281791 | 0.672172528 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.009678972 | -0.012526002 | -0.000006488 | 1.000000000 |
| r140_full_state | 140 | id06 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.640097481 | 0.539573135 | 0.641598553 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.012105337 | -0.011639377 | -0.000007833 | 1.000000000 |
| r140_full_state | 140 | id06 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.640032332 | 0.540113232 | 0.641170870 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.012421581 | -0.011106735 | -0.000008207 | 1.000000000 |
| r099_full_state | 99 | id04 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.638858139 | 0.565387564 | 0.660125856 | 0.184066216 | 1.000000000 | 1.000000000 | 0.792000000 | -0.010304417 | -0.006343444 | -0.000008608 | 1.000000000 |
| r099_full_state | 99 | id04 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.637987507 | 0.564451672 | 0.659123069 | 0.184066216 | 1.000000000 | 1.000000000 | 0.792000000 | -0.010415027 | -0.006140505 | -0.000008598 | 1.000000000 |
| r236_full_state | 236 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.637766764 | 0.552584929 | 0.651812334 | 0.429684297 | 1.000000000 | 0.964285714 | 0.864000000 | -0.009448016 | -0.000191540 | -0.000005218 | 1.000000000 |
| r236_full_state | 236 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.637188345 | 0.551058189 | 0.651120585 | 0.429684297 | 1.000000000 | 0.964285714 | 0.864000000 | -0.008953123 | -0.001024872 | -0.000004730 | 1.000000000 |
| r053_full_state | 53 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.636704923 | 0.549682895 | 0.646476436 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007727303 | -0.003200412 | -0.000006540 | 1.000000000 |
| r053_full_state | 53 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.632906896 | 0.544819179 | 0.641757610 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007935705 | -0.002835775 | -0.000006907 | 1.000000000 |
| r053_full_state | 53 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.628421219 | 0.531395766 | 0.649623998 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007500751 | -0.003424881 | -0.000006284 | 1.000000000 |
| r053_full_state | 53 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.628411014 | 0.531260218 | 0.649721436 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.006270486 | -0.003770951 | -0.000005288 | 1.000000000 |
| r236_full_state | 236 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.627315685 | 0.530705974 | 0.651467288 | 0.429684297 | 1.000000000 | 0.964285714 | 0.864000000 | -0.008185144 | -0.001776508 | -0.000004096 | 1.000000000 |
| r053_full_state | 53 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.627268855 | 0.529843383 | 0.648235323 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.005287330 | -0.003063784 | -0.000004710 | 1.000000000 |
| r236_full_state | 236 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.627051017 | 0.530332407 | 0.651155294 | 0.429684297 | 1.000000000 | 0.964285714 | 0.864000000 | -0.004737135 | -0.002698084 | -0.000002365 | 1.000000000 |
| r236_full_state | 236 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.626582128 | 0.529779401 | 0.650598967 | 0.429684297 | 1.000000000 | 0.964285714 | 0.864000000 | -0.003798765 | -0.001712560 | -0.000001971 | 1.000000000 |
| r099_full_state | 99 | id04 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.625412604 | 0.539704558 | 0.656273969 | 0.184066216 | 1.000000000 | 1.000000000 | 0.792000000 | -0.009776701 | -0.006692478 | -0.000007559 | 1.000000000 |
| r099_full_state | 99 | id04 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.625013328 | 0.539142096 | 0.655803160 | 0.184066216 | 1.000000000 | 1.000000000 | 0.792000000 | -0.008745561 | -0.006926037 | -0.000006911 | 1.000000000 |
| r099_full_state | 99 | id04 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.624853237 | 0.539054865 | 0.655594353 | 0.184066216 | 1.000000000 | 1.000000000 | 0.792000000 | -0.008092958 | -0.006328309 | -0.000007101 | 1.000000000 |
| r054_full_state | 54 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.622196282 | 0.528617047 | 0.654929440 | 0.454130791 | 1.000000000 | 0.857142857 | 0.932000000 | -0.012710525 | -0.005423052 | -0.000002546 | 1.000000000 |
| r054_full_state | 54 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.622109197 | 0.528567094 | 0.654787215 | 0.454130791 | 1.000000000 | 0.857142857 | 0.932000000 | -0.016126150 | -0.003177397 | -0.000003999 | 1.000000000 |
| r054_full_state | 54 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.621879296 | 0.539301780 | 0.641045758 | 0.454130791 | 1.000000000 | 0.857142857 | 0.932000000 | -0.020223239 | -0.000272927 | -0.000004674 | 1.000000000 |
| r054_full_state | 54 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.621466653 | 0.527602540 | 0.653948781 | 0.454130791 | 1.000000000 | 0.857142857 | 0.932000000 | -0.013556671 | -0.005189825 | -0.000002849 | 1.000000000 |
| r218_full_state | 218 | id09 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.619939580 | 0.538016956 | 0.639422778 | 0.184066216 | 1.000000000 | 1.000000000 | 0.836000000 | -0.007103405 | -0.001933959 | -0.000006617 | 1.000000000 |
| r218_full_state | 218 | id09 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.619176132 | 0.537322784 | 0.638127127 | 0.184066216 | 1.000000000 | 1.000000000 | 0.836000000 | -0.007521774 | -0.001217163 | -0.000007379 | 1.000000000 |
| r119_full_state | 119 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.619111738 | 0.531009847 | 0.638018529 | 0.437525625 | 1.000000000 | 0.928571429 | 0.980000000 | -0.007523603 | -0.001391721 | -0.000005920 | 1.000000000 |
| r054_full_state | 54 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.618486108 | 0.535731805 | 0.636557869 | 0.454130791 | 1.000000000 | 0.857142857 | 0.932000000 | -0.019807824 | -0.000372944 | -0.000004909 | 1.000000000 |
| r140_nonq2_full | 140 | id06 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_source_bridge | white_private | 0.617740031 | 0.503172735 | 0.617225926 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.009072170 | -0.011071295 | -0.000005166 | 1.000000000 |
| r140_nonq2_full | 140 | id06 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_q | white_private | 0.617606356 | 0.502966711 | 0.617161712 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.007428865 | -0.011498946 | -0.000004642 | 1.000000000 |
| r140_nonq2_full | 140 | id06 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_binary_edge | white_private | 0.617411382 | 0.502615512 | 0.617035541 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.008756307 | -0.006732613 | -0.000005067 | 1.000000000 |
| r119_full_state | 119 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.616680800 | 0.521118405 | 0.646456146 | 0.437525625 | 1.000000000 | 0.928571429 | 0.980000000 | -0.006732152 | -0.001480220 | -0.000005316 | 1.000000000 |
| r119_full_state | 119 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.616381863 | 0.520640346 | 0.646136935 | 0.437525625 | 1.000000000 | 0.928571429 | 0.980000000 | -0.004926168 | -0.002392564 | -0.000003106 | 1.000000000 |
| r237_full_state | 237 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.616279938 | 0.518744672 | 0.633214424 | 0.184066216 | 1.000000000 | 1.000000000 | 0.976000000 | -0.002077099 | -0.003540261 | -0.000002097 | 1.000000000 |
| r237_full_state | 237 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.615783340 | 0.518132496 | 0.632606554 | 0.184066216 | 1.000000000 | 1.000000000 | 0.976000000 | -0.001021451 | -0.003811806 | -0.000001964 | 1.000000000 |
| r119_full_state | 119 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.615669078 | 0.519716618 | 0.645158359 | 0.437525625 | 1.000000000 | 0.928571429 | 0.980000000 | -0.003254142 | -0.001755663 | -0.000002612 | 1.000000000 |
| r119_full_state | 119 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.615429130 | 0.527101661 | 0.633371229 | 0.437525625 | 1.000000000 | 0.928571429 | 0.980000000 | -0.007820744 | -0.000704321 | -0.000006731 | 1.000000000 |
| r122_full_state | 122 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.615079823 | 0.528248851 | 0.626026818 | 0.393937064 | 1.000000000 | 0.928571429 | 0.892000000 | -0.006331772 | -0.001158118 | -0.000048930 | 1.000000000 |
| r237_full_state | 237 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.614528967 | 0.516597629 | 0.631022846 | 0.184066216 | 1.000000000 | 1.000000000 | 0.976000000 | -0.000977925 | -0.001785265 | -0.000000817 | 1.000000000 |
| r054_nonq2_full | 54 | id02 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_source_bridge | white_private | 0.614343667 | 0.501353230 | 0.618214453 | 0.372488725 | 1.000000000 | 0.958333333 | 0.932000000 | -0.015537777 | -0.003041535 | -0.000003999 | 1.000000000 |
| r054_nonq2_full | 54 | id02 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_q | white_private | 0.614288489 | 0.501260920 | 0.618213178 | 0.372488725 | 1.000000000 | 0.958333333 | 0.932000000 | -0.010936270 | -0.005157168 | -0.000002546 | 1.000000000 |
| r054_nonq2_full | 54 | id02 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | hard_binary_edge | white_private | 0.614171076 | 0.501052329 | 0.618176476 | 0.372488725 | 1.000000000 | 0.958333333 | 0.932000000 | -0.011491291 | -0.004934491 | -0.000002849 | 1.000000000 |
| r217_full_state | 217 | id09 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.613703782 | 0.522369699 | 0.649530928 | 0.597017220 | 0.857142857 | 0.857142857 | 1.000000000 | -0.006573986 | 0.000014155 | -0.000003177 | 0.000000000 |
| r217_full_state | 217 | id09 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.613115014 | 0.521236679 | 0.648849176 | 0.597017220 | 0.857142857 | 0.857142857 | 1.000000000 | -0.002846587 | -0.000972997 | -0.000001403 | 1.000000000 |
| r053_q3_s_stage | 53 | id02 | q3_s_stage | Q3,S1,S2,S3,S4 | h085_hard_bridge | white_objective | 0.612794215 | 0.524001516 | 0.602106249 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007021609 | -0.003239703 | -0.000006059 | 1.000000000 |
| r217_full_state | 217 | id09 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.612228152 | 0.520051888 | 0.647723613 | 0.597017220 | 0.857142857 | 0.857142857 | 1.000000000 | -0.000724897 | -0.000350179 | -0.000000281 | 1.000000000 |
| r053_q3_s_stage | 53 | id02 | q3_s_stage | Q3,S1,S2,S3,S4 | triad_consensus | white_objective | 0.612128909 | 0.523003300 | 0.601920901 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007160082 | -0.002994551 | -0.000006358 | 1.000000000 |
| r189_full_state | 189 | id08 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.611508807 | 0.544769630 | 0.640791376 | 0.184066216 | 1.000000000 | 1.000000000 | 0.712000000 | -0.003888326 | -0.002476464 | -0.000004673 | 1.000000000 |
| r066_full_state | 66 | id03 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.609829012 | 0.536603291 | 0.640315773 | 0.184066216 | 1.000000000 | 1.000000000 | 0.676000000 | -0.016409592 | -0.003487775 | -0.000016665 | 1.000000000 |
| r122_full_state | 122 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.609694547 | 0.525377665 | 0.618920172 | 0.393937064 | 1.000000000 | 0.928571429 | 0.892000000 | -0.006045661 | 0.001205312 | -0.000117119 | 0.000000000 |
| r124_full_state | 124 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.609606615 | 0.545596155 | 0.650104463 | 0.393937064 | 1.000000000 | 0.928571429 | 0.716000000 | -0.011308159 | -0.003966796 | -0.000005142 | 1.000000000 |
| r189_full_state | 189 | id08 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.609422718 | 0.541608592 | 0.637720986 | 0.184066216 | 1.000000000 | 1.000000000 | 0.712000000 | -0.004007532 | -0.002271674 | -0.000004414 | 1.000000000 |
| r237_full_state | 237 | id10 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.609041754 | 0.511751661 | 0.610848831 | 0.184066216 | 1.000000000 | 1.000000000 | 0.976000000 | -0.002502148 | -0.002967705 | -0.000002221 | 1.000000000 |
| r030_full_state | 30 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.608948651 | 0.534554278 | 0.642415753 | 0.454130791 | 1.000000000 | 0.857142857 | 0.812000000 | -0.007945996 | -0.004804736 | -0.000004431 | 1.000000000 |
| r053_s_stage | 53 | id02 | s_stage | S1,S2,S3,S4 | h085_hard_bridge | white_objective | 0.608852448 | 0.519761834 | 0.599668092 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.005183025 | -0.002351226 | -0.000004087 | 1.000000000 |
| r140_nonq2_full | 140 | id06 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_public | 0.608792853 | 0.500634005 | 0.578422154 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.009561000 | -0.010724657 | -0.000005373 | 1.000000000 |
| r140_nonq2_full | 140 | id06 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | triad_consensus | white_public | 0.608572222 | 0.500498213 | 0.578262970 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.009831553 | -0.010272138 | -0.000005557 | 1.000000000 |
| r122_full_state | 122 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_source_bridge | white_q2 | 0.608534895 | 0.511103118 | 0.630721173 | 0.393937064 | 1.000000000 | 0.928571429 | 0.892000000 | -0.005315734 | 0.001282714 | -0.000124313 | 0.000000000 |
| r122_full_state | 122 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_q | white_q2 | 0.608530894 | 0.510836600 | 0.630805504 | 0.393937064 | 1.000000000 | 0.928571429 | 0.892000000 | -0.004591022 | -0.001817072 | -0.000016446 | 1.000000000 |
| r053_s_stage | 53 | id02 | s_stage | S1,S2,S3,S4 | triad_consensus | white_objective | 0.608270900 | 0.518928977 | 0.599571975 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.005301613 | -0.002140621 | -0.000004272 | 1.000000000 |
| r124_full_state | 124 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.608245426 | 0.544082938 | 0.648331365 | 0.393937064 | 1.000000000 | 0.928571429 | 0.716000000 | -0.011497745 | -0.003591071 | -0.000005440 | 1.000000000 |
| r066_full_state | 66 | id03 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.608052257 | 0.534766323 | 0.637884330 | 0.184066216 | 1.000000000 | 1.000000000 | 0.676000000 | -0.017166771 | -0.002153433 | -0.000019403 | 1.000000000 |
| r053_nonq2_full | 53 | id02 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_public | 0.607957681 | 0.514823006 | 0.590812629 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007718592 | -0.003082218 | -0.000006456 | 1.000000000 |
| r122_full_state | 122 | id05 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | hard_binary_edge | white_q2 | 0.607864013 | 0.509684811 | 0.629925886 | 0.393937064 | 1.000000000 | 0.928571429 | 0.892000000 | -0.003554974 | -0.001204638 | -0.000005881 | 1.000000000 |
| r153_full_state | 153 | id07 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.607850794 | 0.553658232 | 0.654308668 | 0.454130791 | 1.000000000 | 0.857142857 | 0.680000000 | -0.005969816 | -0.002526749 | -0.000004217 | 1.000000000 |
| r236_q3_s_stage | 236 | id10 | q3_s_stage | Q3,S1,S2,S3,S4 | h085_hard_bridge | white_objective | 0.607704292 | 0.522174227 | 0.597238571 | 0.184066216 | 1.000000000 | 1.000000000 | 0.864000000 | -0.006207446 | -0.001839767 | -0.000003360 | 1.000000000 |
| r030_full_state | 30 | id02 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | triad_consensus | white_q2 | 0.607689861 | 0.533375676 | 0.640599303 | 0.454130791 | 1.000000000 | 0.857142857 | 0.812000000 | -0.007992811 | -0.004710096 | -0.000004521 | 1.000000000 |
| r014_full_state | 14 | id01 | full_state | Q1,Q2,Q3,S1,S2,S3,S4 | h085_hard_bridge | white_q2 | 0.607553965 | 0.530525925 | 0.630976575 | 0.184066216 | 1.000000000 | 1.000000000 | 0.732000000 | -0.008265028 | -0.002404742 | -0.000005445 | 1.000000000 |
| r053_nonq2_full | 53 | id02 | nonq2_full | Q1,Q3,S1,S2,S3,S4 | triad_consensus | white_public | 0.607510919 | 0.514313885 | 0.590503682 | 0.184066216 | 1.000000000 | 1.000000000 | 0.896000000 | -0.007921151 | -0.002727404 | -0.000006835 | 1.000000000 |
| r140_recovery_route | 140 | id06 | recovery_route | Q1,S2,S3,S4 | hard_source_bridge | white_private | 0.607473660 | 0.495165015 | 0.609183103 | 0.184066216 | 1.000000000 | 1.000000000 | 0.996000000 | -0.007026661 | -0.003432840 | -0.000003260 | 1.000000000 |

Interpretation rule:

- If H093 improves by >= 0.001, HS-JEPA's breakthrough path is target-support
  masking: the architecture can discover new row-target action support outside
  the known public-equation basin.
- If H093 is near H057/H092 but more novel, the low-overlap latent is real but
  needs a stronger value-law solver.
- If H093 loses badly, low-overlap support is not the missing 0.53 mechanism;
  the next big bet must invert the value law/public equation rather than
  searching more route space.
