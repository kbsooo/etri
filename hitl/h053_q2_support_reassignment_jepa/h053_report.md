# H053 Q2 Support-Reassignment HS-JEPA

Question: if H051/H052 amplitude continuation is wrong, is H042's real missing variable support identity rather than amplitude?

Design:

- base = H042 current public best;
- Q1/Q3/S targets are frozen;
- keep the strongest `31` H042 Q2 support rows by H047 support posterior + H036 world score;
- revert the weakest `14` H042 Q2 support rows back to H012;
- add `14` non-H042 rows selected by H047 support posterior and H036/H042 public-world Q2 direction;
- selected branch uses `world_prob` with alpha `0.35`.

Decision:

| decision | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | reason | public_anchor | public_anchor_lb | h050_public_lb | expected_relation | candidate_id | keep_n | add_n | alpha | mode | changed_cells_vs_h042 | q2_changed_cells_vs_h042 | changed_cells_vs_h012 | q2_changed_cells_vs_h012 | kept_h042_support | removed_h042_support | added_new_support | selected_support_size | support_score_gain_add_minus_remove | support_posterior_gain_add_minus_remove | mean_keep_support_posterior | mean_removed_support_posterior | mean_added_support_posterior | mean_added_world_weight | q2_world_delta_vs_h042 | direction_agreement_with_world | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | h053_support_reassignment_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_as_amplitude_failure_branch | h053_swap_keep31_add14_a0p35_world_prob_447af5b3 | submission_h053_swap_keep31_add14_a0p35_world_prob_447af5b3.csv | /Users/kbsoo/Downloads/cl2/hitl/h053_q2_support_reassignment_jepa/submission_h053_swap_keep31_add14_a0p35_world_prob_447af5b3.csv | /Users/kbsoo/Downloads/cl2/submission_h053_q2_support_reassign_k31a14_447af5b3_uploadsafe.csv | Q2 support reassignment branch after H051/H052 amplitude branch | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.567904825 | beats H042 if H042's Q2 phase support is partly misplaced; fails if exact H042 support is the true public subset | h053_swap_keep31_add14_a0p35_world_prob_447af5b3 | 31 | 14 | 0.350000000 | world_prob | 28 | 28 | 45 | 45 | 31 | 14 | 14 | 45 | 0.239130240 | 0.019460000 | 0.751510968 | 0.549065714 | 0.568525714 | 0.294405228 | -0.000386360 | 1.000000000 | 0.002488193 | 0.033847854 | 0.000864515 |

Public-anchor context:

- H012 public LB: `0.5681234831`
- H042 public LB: `0.5679048248`
- H050 public LB: `0.5679048248`
- H050 max Q2 delta vs H042: `0.000000000000` (Q2 was frozen)

Top candidates:

| candidate_id | keep_n | add_n | alpha | mode | changed_cells_vs_h042 | changed_cells_vs_h012 | support_score_gain_add_minus_remove | support_posterior_gain_add_minus_remove | mean_removed_support_posterior | mean_added_support_posterior | mean_added_world_weight | q2_world_delta_vs_h042 | direction_agreement_with_world | mean_abs_prob_move_vs_h042 | max_abs_prob_move_vs_h042 | h053_support_reassignment_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h053_swap_keep25_add20_a0p66_world_logit_45a22da0 | 25 | 20 | 0.660000000 | world_logit | 40 | 45 | 0.171504789 | -0.002182000 | 0.564508000 | 0.562326000 | 0.271187640 | -0.001249652 | 1.000000000 | 0.005032263 | 0.064708277 | 0.001604728 |
| h053_swap_keep25_add20_a0p66_world_prob_2f05b773 | 25 | 20 | 0.660000000 | world_prob | 40 | 45 | 0.171504789 | -0.002182000 | 0.564508000 | 0.562326000 | 0.271187640 | -0.001240489 | 1.000000000 | 0.005018014 | 0.064479135 | 0.001595565 |
| h053_swap_keep39_add6_a0p66_world_logit_9b5328fe | 39 | 6 | 0.660000000 | world_logit | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000695162 | 1.000000000 | 0.001635565 | 0.058671532 | 0.001472749 |
| h053_swap_keep39_add6_a0p66_world_prob_207bb5b3 | 39 | 6 | 0.660000000 | world_prob | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000685900 | 1.000000000 | 0.001623867 | 0.058786528 | 0.001463487 |
| h053_swap_keep35_add10_a0p66_world_logit_21ae3ce0 | 35 | 10 | 0.660000000 | world_logit | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000878484 | 1.000000000 | 0.002539057 | 0.058671532 | 0.001461841 |
| h053_swap_keep35_add10_a0p66_world_prob_50ffbdfa | 35 | 10 | 0.660000000 | world_prob | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000870882 | 1.000000000 | 0.002531468 | 0.059265622 | 0.001454239 |
| h053_swap_keep31_add14_a0p66_world_logit_a3cb7b10 | 31 | 14 | 0.660000000 | world_logit | 28 | 45 | 0.239130240 | 0.019460000 | 0.549065714 | 0.568525714 | 0.294405228 | -0.000963680 | 1.000000000 | 0.003740194 | 0.064708277 | 0.001441835 |
| h053_swap_keep31_add14_a0p66_world_prob_777feb42 | 31 | 14 | 0.660000000 | world_prob | 28 | 45 | 0.239130240 | 0.019460000 | 0.549065714 | 0.568525714 | 0.294405228 | -0.000953127 | 1.000000000 | 0.003723648 | 0.063827382 | 0.001431283 |
| h053_swap_keep39_add6_a0p5_world_logit_11736508 | 39 | 6 | 0.500000000 | world_logit | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000565112 | 1.000000000 | 0.001352152 | 0.044369254 | 0.001342700 |
| h053_swap_keep39_add6_a0p5_world_prob_c5a38dd6 | 39 | 6 | 0.500000000 | world_prob | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000550772 | 1.000000000 | 0.001339449 | 0.044535248 | 0.001328359 |
| h053_swap_keep25_add20_a0p5_world_logit_06e1b2c7 | 25 | 20 | 0.500000000 | world_logit | 40 | 45 | 0.171504789 | -0.002182000 | 0.564508000 | 0.562326000 | 0.271187640 | -0.000937670 | 1.000000000 | 0.004161723 | 0.049289598 | 0.001292745 |
| h053_swap_keep35_add10_a0p5_world_logit_7a98fc78 | 35 | 10 | 0.500000000 | world_logit | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000703024 | 1.000000000 | 0.002095706 | 0.044369254 | 0.001286381 |
| h053_swap_keep25_add20_a0p5_world_prob_17fa40fb | 25 | 20 | 0.500000000 | world_prob | 40 | 45 | 0.171504789 | -0.002182000 | 0.564508000 | 0.562326000 | 0.271187640 | -0.000924110 | 1.000000000 | 0.004147191 | 0.048847829 | 0.001279185 |
| h053_swap_keep35_add10_a0p5_world_prob_48198552 | 35 | 10 | 0.500000000 | world_prob | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000691546 | 1.000000000 | 0.002087816 | 0.044898199 | 0.001274903 |
| h053_swap_keep31_add14_a0p5_world_logit_fb8e77f6 | 31 | 14 | 0.500000000 | world_logit | 28 | 45 | 0.239130240 | 0.019460000 | 0.549065714 | 0.568525714 | 0.294405228 | -0.000719466 | 1.000000000 | 0.003103469 | 0.049289598 | 0.001197621 |
| h053_swap_keep31_add14_a0p5_world_prob_7f4319d5 | 31 | 14 | 0.500000000 | world_prob | 28 | 45 | 0.239130240 | 0.019460000 | 0.549065714 | 0.568525714 | 0.294405228 | -0.000703392 | 1.000000000 | 0.003085994 | 0.048354078 | 0.001181548 |
| h053_swap_keep39_add6_a0p35_world_logit_73ae88d8 | 39 | 6 | 0.350000000 | world_logit | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000396555 | 1.000000000 | 0.001084075 | 0.030991451 | 0.001174142 |
| h053_swap_keep39_add6_a0p35_world_prob_30f3d954 | 39 | 6 | 0.350000000 | world_prob | 12 | 45 | 0.410271371 | 0.062180000 | 0.520480000 | 0.582660000 | 0.336717327 | -0.000380454 | 1.000000000 | 0.001072807 | 0.031174674 | 0.001158041 |
| h053_swap_keep35_add10_a0p35_world_logit_db2e447b | 35 | 10 | 0.350000000 | world_logit | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000476448 | 1.000000000 | 0.001678586 | 0.030991451 | 0.001059806 |
| h053_swap_keep35_add10_a0p35_world_prob_562a4e60 | 35 | 10 | 0.350000000 | world_prob | 20 | 45 | 0.300984866 | 0.031880000 | 0.546220000 | 0.578100000 | 0.298156361 | -0.000463896 | 1.000000000 | 0.001671893 | 0.031428739 | 0.001047253 |

Interpretation rule:

- If H051/H052 improve, H053 is lower priority because exact-support amplitude/edge is alive.
- If H051 fails and H053 improves, H042's Q2 discovery should be interpreted as support/public-subset identity, not amplitude.
- If both amplitude and support reassignment fail, H042 is likely a very narrow local correction and the next branch should infer public subset directly rather than modifying Q2.
