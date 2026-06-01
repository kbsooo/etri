# H009 S4 Mobility Rank Jackpot

## Question

What if the S4 mobility latent should not be a tiny correction, but should rewrite the S4 row ordering while preserving E247's marginal calibration?

## Big-Bet Hypothesis

E247's S4 probability distribution is treated as the right marginal prior. H009 only changes which rows receive high/low S4 probability, using the HS-JEPA mobility state and latent S4 model.

This is intentionally not a conservative public-safe edit. It is the test for whether the S4 mobility discovery can become a leaderboard-sized move.

## Chosen H007 S4 Latent Model

- feature_set: `mobility_jepa`
- C: `0.05`

## Family Summary

| family | n | jackpot | local_only | best_local_worst | best_local_mean | best_selector_mean | best_selector_p90 | best_jackpot_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qrank_subject | 23 | 0 | 6 | -0.011893361 | -0.027329122 | -0.002683646 | 0.000942441 | -2.167551910 |
| qrank_global | 9 | 0 | 0 | -0.013737895 | -0.015881375 | -0.003336459 | 0.002447223 | -1.897821884 |
| tail_swap | 25 | 0 | 0 | -0.007701565 | -0.011816093 | -0.003444452 | 0.001715899 | -1.185578091 |
| model_blend | 17 | 0 | 17 | -0.005530815 | -0.006469032 | -0.000171617 | 0.000222245 | -0.787454221 |
| qrank_dateblock | 6 | 0 | 3 | -0.004672955 | -0.005862606 | -0.001190919 | 0.000877081 | -0.691666312 |
| reverse_control | 8 | 0 | 0 | 0.026745149 | 0.015018938 | -0.004725825 | 0.006886939 | 3.824034074 |

## Top Local Stress

| candidate_id | family | op | score_signal | strength | group | k | cap | split | delta_logloss | mean_delta | worst_delta | max_abs_prob_delta_local | changed_rows_local |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qrank_plus_prob_global_s1 | qrank_global | quantile | plus_prob | 1.000000000 | global | 0 | 0.000000000 | subject5 | -0.015324830 | -0.014531363 | -0.013737895 | 0.388269613 | 447 |
| qrank_plus_prob_global_s1 | qrank_global | quantile | plus_prob | 1.000000000 | global | 0 | 0.000000000 | dateblock5 | -0.013737895 | -0.014531363 | -0.013737895 | 0.388269613 | 447 |
| qrank_plus_prob_global_s0.85 | qrank_global | quantile | plus_prob | 0.850000000 | global | 0 | 0.000000000 | subject5 | -0.014067360 | -0.013564186 | -0.013061011 | 0.350102207 | 447 |
| qrank_plus_prob_global_s0.85 | qrank_global | quantile | plus_prob | 0.850000000 | global | 0 | 0.000000000 | dateblock5 | -0.013061011 | -0.013564186 | -0.013061011 | 0.350102207 | 447 |
| qrank_consensus_global_s0.35 | qrank_global | quantile | consensus | 0.350000000 | global | 0 | 0.000000000 | subject5 | -0.013042023 | -0.013821865 | -0.013042023 | 0.187986568 | 450 |
| qrank_consensus_global_s0.35 | qrank_global | quantile | consensus | 0.350000000 | global | 0 | 0.000000000 | dateblock5 | -0.014601708 | -0.013821865 | -0.013042023 | 0.187986568 | 450 |
| qrank_consensus_global_s0.6 | qrank_global | quantile | consensus | 0.600000000 | global | 0 | 0.000000000 | subject5 | -0.019038872 | -0.015881375 | -0.012723878 | 0.312389136 | 450 |
| qrank_consensus_global_s0.6 | qrank_global | quantile | consensus | 0.600000000 | global | 0 | 0.000000000 | dateblock5 | -0.012723878 | -0.015881375 | -0.012723878 | 0.312389136 | 450 |
| qrank_consensus_subject_s0.85 | qrank_subject | quantile | consensus | 0.850000000 | subject | 0 | 0.000000000 | subject5 | -0.011893361 | -0.024920108 | -0.011893361 | 0.298366685 | 442 |
| qrank_consensus_subject_s0.85 | qrank_subject | quantile | consensus | 0.850000000 | subject | 0 | 0.000000000 | dateblock5 | -0.037946855 | -0.024920108 | -0.011893361 | 0.298366685 | 442 |
| qrank_consensus_subject_s1 | qrank_subject | quantile | consensus | 1.000000000 | subject | 0 | 0.000000000 | subject5 | -0.011381174 | -0.025676355 | -0.011381174 | 0.351353050 | 442 |
| qrank_consensus_subject_s1 | qrank_subject | quantile | consensus | 1.000000000 | subject | 0 | 0.000000000 | dateblock5 | -0.039971537 | -0.025676355 | -0.011381174 | 0.351353050 | 442 |
| qrank_plus_prob_subject_s1 | qrank_subject | quantile | plus_prob | 1.000000000 | subject | 0 | 0.000000000 | subject5 | -0.011045466 | -0.013126575 | -0.011045466 | 0.245530426 | 425 |
| qrank_plus_prob_subject_s1 | qrank_subject | quantile | plus_prob | 1.000000000 | subject | 0 | 0.000000000 | dateblock5 | -0.015207683 | -0.013126575 | -0.011045466 | 0.245530426 | 425 |
| qrank_consensus_subject_s0.6 | qrank_subject | quantile | consensus | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.011007020 | -0.021240840 | -0.011007020 | 0.208816540 | 442 |
| qrank_consensus_subject_s0.6 | qrank_subject | quantile | consensus | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.031474661 | -0.021240840 | -0.011007020 | 0.208816540 | 442 |
| qrank_delta_pos_subject_s0.85 | qrank_subject | quantile | delta_pos | 0.850000000 | subject | 0 | 0.000000000 | subject5 | -0.010956174 | -0.026818283 | -0.010956174 | 0.322136010 | 438 |
| qrank_delta_pos_subject_s0.85 | qrank_subject | quantile | delta_pos | 0.850000000 | subject | 0 | 0.000000000 | dateblock5 | -0.042680392 | -0.026818283 | -0.010956174 | 0.322136010 | 438 |
| qrank_plus_prob_global_s0.6 | qrank_global | quantile | plus_prob | 0.600000000 | global | 0 | 0.000000000 | subject5 | -0.011154576 | -0.011006427 | -0.010858278 | 0.268761491 | 447 |
| qrank_plus_prob_global_s0.6 | qrank_global | quantile | plus_prob | 0.600000000 | global | 0 | 0.000000000 | dateblock5 | -0.010858278 | -0.011006427 | -0.010858278 | 0.268761491 | 447 |
| qrank_delta_pos_subject_s0.6 | qrank_subject | quantile | delta_pos | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.010748612 | -0.023176490 | -0.010748612 | 0.227802382 | 438 |
| qrank_delta_pos_subject_s0.6 | qrank_subject | quantile | delta_pos | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.035604367 | -0.023176490 | -0.010748612 | 0.227802382 | 438 |
| qrank_plus_prob_subject_s0.85 | qrank_subject | quantile | plus_prob | 0.850000000 | subject | 0 | 0.000000000 | subject5 | -0.010285564 | -0.012144696 | -0.010285564 | 0.212835483 | 425 |
| qrank_plus_prob_subject_s0.85 | qrank_subject | quantile | plus_prob | 0.850000000 | subject | 0 | 0.000000000 | dateblock5 | -0.014003827 | -0.012144696 | -0.010285564 | 0.212835483 | 425 |
| qrank_teacher_rank_global_s0.35 | qrank_global | quantile | teacher_rank | 0.350000000 | global | 0 | 0.000000000 | subject5 | -0.015002727 | -0.012539916 | -0.010077105 | 0.252280948 | 450 |
| qrank_teacher_rank_global_s0.35 | qrank_global | quantile | teacher_rank | 0.350000000 | global | 0 | 0.000000000 | dateblock5 | -0.010077105 | -0.012539916 | -0.010077105 | 0.252280948 | 450 |
| qrank_delta_pos_global_s0.35 | qrank_global | quantile | delta_pos | 0.350000000 | global | 0 | 0.000000000 | subject5 | -0.014804572 | -0.012362367 | -0.009920162 | 0.253390473 | 450 |
| qrank_delta_pos_global_s0.35 | qrank_global | quantile | delta_pos | 0.350000000 | global | 0 | 0.000000000 | dateblock5 | -0.009920162 | -0.012362367 | -0.009920162 | 0.253390473 | 450 |
| qrank_delta_pos_subject_s1 | qrank_subject | quantile | delta_pos | 1.000000000 | subject | 0 | 0.000000000 | subject5 | -0.009885740 | -0.027329122 | -0.009885740 | 0.374237000 | 438 |
| qrank_delta_pos_subject_s1 | qrank_subject | quantile | delta_pos | 1.000000000 | subject | 0 | 0.000000000 | dateblock5 | -0.044772505 | -0.027329122 | -0.009885740 | 0.374237000 | 438 |
| qrank_teacher_rank_subject_s0.6 | qrank_subject | quantile | teacher_rank | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.008975299 | -0.020684968 | -0.008975299 | 0.249391615 | 446 |
| qrank_teacher_rank_subject_s0.6 | qrank_subject | quantile | teacher_rank | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.032394636 | -0.020684968 | -0.008975299 | 0.249391615 | 446 |
| qrank_plus_prob_subject_s0.6 | qrank_subject | quantile | plus_prob | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.008314665 | -0.009734415 | -0.008314665 | 0.154069341 | 425 |
| qrank_plus_prob_subject_s0.6 | qrank_subject | quantile | plus_prob | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.011154164 | -0.009734415 | -0.008314665 | 0.154069341 | 425 |
| qrank_human_state_subject_s0.6 | qrank_subject | quantile | human_state | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.008035121 | -0.019519143 | -0.008035121 | 0.245908976 | 444 |
| qrank_human_state_subject_s0.6 | qrank_subject | quantile | human_state | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.031003165 | -0.019519143 | -0.008035121 | 0.245908976 | 444 |
| qrank_delta_pos_subject_s0.35 | qrank_subject | quantile | delta_pos | 0.350000000 | subject | 0 | 0.000000000 | subject5 | -0.008026741 | -0.015992775 | -0.008026741 | 0.129740770 | 438 |
| qrank_delta_pos_subject_s0.35 | qrank_subject | quantile | delta_pos | 0.350000000 | subject | 0 | 0.000000000 | dateblock5 | -0.023958809 | -0.015992775 | -0.008026741 | 0.129740770 | 438 |
| qrank_consensus_subject_s0.35 | qrank_subject | quantile | consensus | 0.350000000 | subject | 0 | 0.000000000 | subject5 | -0.007937914 | -0.014512548 | -0.007937914 | 0.126813705 | 442 |
| qrank_consensus_subject_s0.35 | qrank_subject | quantile | consensus | 0.350000000 | subject | 0 | 0.000000000 | dateblock5 | -0.021087183 | -0.014512548 | -0.007937914 | 0.126813705 | 442 |
| tailswap_plus_prob_k125_s1 | tail_swap | tail_swap | plus_prob | 1.000000000 | global | 125 | 0.000000000 | subject5 | -0.015930621 | -0.011816093 | -0.007701565 | 0.388269613 | 245 |
| tailswap_plus_prob_k125_s1 | tail_swap | tail_swap | plus_prob | 1.000000000 | global | 125 | 0.000000000 | dateblock5 | -0.007701565 | -0.011816093 | -0.007701565 | 0.388269613 | 245 |
| qrank_teacher_rank_subject_s0.35 | qrank_subject | quantile | teacher_rank | 0.350000000 | subject | 0 | 0.000000000 | subject5 | -0.007421882 | -0.014963862 | -0.007421882 | 0.140071159 | 446 |
| qrank_teacher_rank_subject_s0.35 | qrank_subject | quantile | teacher_rank | 0.350000000 | subject | 0 | 0.000000000 | dateblock5 | -0.022505841 | -0.014963862 | -0.007421882 | 0.140071159 | 446 |
| qrank_teacher_rank_subject_s0.85 | qrank_subject | quantile | teacher_rank | 0.850000000 | subject | 0 | 0.000000000 | subject5 | -0.007392697 | -0.022246773 | -0.007392697 | 0.355232481 | 446 |
| qrank_teacher_rank_subject_s0.85 | qrank_subject | quantile | teacher_rank | 0.850000000 | subject | 0 | 0.000000000 | dateblock5 | -0.037100849 | -0.022246773 | -0.007392697 | 0.355232481 | 446 |
| qrank_plus_prob_global_s0.35 | qrank_global | quantile | plus_prob | 0.350000000 | global | 0 | 0.000000000 | subject5 | -0.007218722 | -0.007256023 | -0.007218722 | 0.166046591 | 447 |
| qrank_plus_prob_global_s0.35 | qrank_global | quantile | plus_prob | 0.350000000 | global | 0 | 0.000000000 | dateblock5 | -0.007293323 | -0.007256023 | -0.007218722 | 0.166046591 | 447 |
| tailswap_plus_prob_k125_s0.75 | tail_swap | tail_swap | plus_prob | 0.750000000 | global | 125 | 0.000000000 | subject5 | -0.013017074 | -0.010058120 | -0.007099166 | 0.320276444 | 245 |
| tailswap_plus_prob_k125_s0.75 | tail_swap | tail_swap | plus_prob | 0.750000000 | global | 125 | 0.000000000 | dateblock5 | -0.007099166 | -0.010058120 | -0.007099166 | 0.320276444 | 245 |
| qrank_human_state_subject_s0.35 | qrank_subject | quantile | human_state | 0.350000000 | subject | 0 | 0.000000000 | subject5 | -0.006877482 | -0.014284037 | -0.006877482 | 0.138072693 | 444 |
| qrank_human_state_subject_s0.35 | qrank_subject | quantile | human_state | 0.350000000 | subject | 0 | 0.000000000 | dateblock5 | -0.021690591 | -0.014284037 | -0.006877482 | 0.138072693 | 444 |
| qrank_human_state_subject_s0.85 | qrank_subject | quantile | human_state | 0.850000000 | subject | 0 | 0.000000000 | subject5 | -0.006053411 | -0.020597585 | -0.006053411 | 0.350667589 | 444 |
| qrank_human_state_subject_s0.85 | qrank_subject | quantile | human_state | 0.850000000 | subject | 0 | 0.000000000 | dateblock5 | -0.035141758 | -0.020597585 | -0.006053411 | 0.350667589 | 444 |
| qrank_low_energy_subject_s0.6 | qrank_subject | quantile | low_energy | 0.600000000 | subject | 0 | 0.000000000 | subject5 | -0.006017445 | -0.017209621 | -0.006017445 | 0.259838962 | 442 |
| qrank_low_energy_subject_s0.6 | qrank_subject | quantile | low_energy | 0.600000000 | subject | 0 | 0.000000000 | dateblock5 | -0.028401798 | -0.017209621 | -0.006017445 | 0.259838962 | 442 |
| qrank_human_state_global_s0.35 | qrank_global | quantile | human_state | 0.350000000 | global | 0 | 0.000000000 | subject5 | -0.012826362 | -0.009287534 | -0.005748707 | 0.250727940 | 450 |
| qrank_human_state_global_s0.35 | qrank_global | quantile | human_state | 0.350000000 | global | 0 | 0.000000000 | dateblock5 | -0.005748707 | -0.009287534 | -0.005748707 | 0.250727940 | 450 |
| tailswap_consensus_k100_s0.5 | tail_swap | tail_swap | consensus | 0.500000000 | global | 100 | 0.000000000 | subject5 | -0.005748673 | -0.005803386 | -0.005748673 | 0.232725199 | 199 |
| tailswap_consensus_k100_s0.5 | tail_swap | tail_swap | consensus | 0.500000000 | global | 100 | 0.000000000 | dateblock5 | -0.005858099 | -0.005803386 | -0.005748673 | 0.232725199 | 199 |

## Jackpot Gate

| candidate_id | h009_decision | family | op | score_signal | strength | group | k | changed_cells | max_abs_prob_delta | mean_s4_before | mean_s4_after | worst_delta | mean_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | jackpot_score | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qrank_delta_pos_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | delta_pos | 0.350000000 | subject | 0 | 242 | 0.126592695 | 0.565498962 | 0.566004566 | -0.008026741 | -0.015992775 | -0.000717963 | 0.000942441 | 0.583333333 | -1.437552349 | submission_h009_qrank_delta_pos_subject_s0_35_a4ae7b8b.csv |
| qrank_consensus_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | consensus | 0.350000000 | subject | 0 | 243 | 0.131129791 | 0.565498962 | 0.565935353 | -0.007937914 | -0.014512548 | -0.000653368 | 0.000993222 | 0.541666667 | -1.368887323 | submission_h009_qrank_consensus_subject_s0_35_4eaca577.csv |
| qrank_teacher_rank_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | teacher_rank | 0.350000000 | subject | 0 | 242 | 0.145237439 | 0.565498962 | 0.565923394 | -0.007421882 | -0.014963862 | -0.000640046 | 0.001207233 | 0.486111111 | -1.333564325 | submission_h009_qrank_teacher_rank_subject_s0_35_3778b1c9.csv |
| qrank_human_state_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | human_state | 0.350000000 | subject | 0 | 242 | 0.145237439 | 0.565498962 | 0.565911832 | -0.006877482 | -0.014284037 | -0.000732357 | 0.001124809 | 0.597222222 | -1.252883678 | submission_h009_qrank_human_state_subject_s0_35_1211e4f2.csv |
| qrank_low_energy_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | low_energy | 0.350000000 | subject | 0 | 246 | 0.138409621 | 0.565498962 | 0.565809672 | -0.005636929 | -0.012815108 | -0.000672969 | 0.001104264 | 0.541666667 | -1.070041567 | submission_h009_qrank_low_energy_subject_s0_35_61cc5e9c.csv |
| qrank_plus_prob_subject_s0.35 | local_only_high_risk | qrank_subject | quantile | plus_prob | 0.350000000 | subject | 0 | 238 | 0.131129791 | 0.565498962 | 0.565992173 | -0.005462824 | -0.006354173 | -0.000555065 | 0.001137452 | 0.375000000 | -0.793472310 | submission_h009_qrank_plus_prob_subject_s0_35_94a9e381.csv |
| modelblend_s0.5_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.500000000 | global | 0 | 250 | 0.034985149 | 0.565498962 | 0.559833051 | -0.005530815 | -0.006033332 | -0.000127418 | 0.000888873 | 0.388888889 | -0.787454221 | submission_h009_modelblend_s0_5_cap0_14_66767de0.csv |
| modelblend_s0.75_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.750000000 | global | 0 | 250 | 0.034985149 | 0.565498962 | 0.559709749 | -0.005168737 | -0.006285811 | -0.000156932 | 0.000967035 | 0.388888889 | -0.760837313 | submission_h009_modelblend_s0_75_cap0_14_d3a87c6d.csv |
| modelblend_s1_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 1.000000000 | global | 0 | 250 | 0.034985149 | 0.565498962 | 0.559765267 | -0.004973698 | -0.006469032 | -0.000171617 | 0.001002871 | 0.388888889 | -0.748434705 | submission_h009_modelblend_s1_cap0_14_325be5f3.csv |
| modelblend_s0.35_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.350000000 | global | 0 | 250 | 0.034985149 | 0.565498962 | 0.560099522 | -0.004949039 | -0.005365458 | -0.000103413 | 0.000828323 | 0.388888889 | -0.702967764 | submission_h009_modelblend_s0_35_cap0_14_6489dfeb.csv |
| qrank_delta_pos_dateblock_s0.6 | local_only_high_risk | qrank_dateblock | quantile | delta_pos | 0.600000000 | dateblock | 0 | 189 | 0.178807601 | 0.565498962 | 0.565674905 | -0.004672955 | -0.005859276 | -0.000586958 | 0.001542740 | 0.361111111 | -0.691666312 | submission_h009_qrank_delta_pos_dateblock_s0_6_297a8cc6.csv |
| modelblend_s1_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 1.000000000 | global | 0 | 250 | 0.022496182 | 0.565498962 | 0.561931767 | -0.003821078 | -0.004762241 | -0.000077504 | 0.000543582 | 0.388888889 | -0.568323930 | submission_h009_modelblend_s1_cap0_09_60cb0e0e.csv |
| modelblend_s0.75_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.750000000 | global | 0 | 250 | 0.022496182 | 0.565498962 | 0.561847151 | -0.003696763 | -0.004648164 | -0.000072006 | 0.000540735 | 0.375000000 | -0.551330356 | submission_h009_modelblend_s0_75_cap0_09_33ed1de1.csv |
| modelblend_s0.35_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.350000000 | global | 0 | 250 | 0.022496182 | 0.565498962 | 0.561872494 | -0.003837277 | -0.004217033 | -0.000047809 | 0.000514279 | 0.388888889 | -0.548254320 | submission_h009_modelblend_s0_35_cap0_09_3807b202.csv |
| qrank_delta_pos_dateblock_s0.35 | local_only_high_risk | qrank_dateblock | quantile | delta_pos | 0.350000000 | dateblock | 0 | 189 | 0.101656497 | 0.565498962 | 0.565665692 | -0.003750260 | -0.004419864 | -0.000258263 | 0.000877081 | 0.361111111 | -0.545833352 | submission_h009_qrank_delta_pos_dateblock_s0_35_404461b1.csv |
| modelblend_s0.5_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.500000000 | global | 0 | 250 | 0.022496182 | 0.565498962 | 0.561826329 | -0.003678226 | -0.004415368 | -0.000063222 | 0.000530305 | 0.388888889 | -0.540217120 | submission_h009_modelblend_s0_5_cap0_09_e8b4c3e3.csv |
| modelblend_s0.2_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.200000000 | global | 0 | 250 | 0.034985149 | 0.565498962 | 0.560847351 | -0.003529029 | -0.003739422 | -0.000060699 | 0.000712962 | 0.388888889 | -0.496731063 | submission_h009_modelblend_s0_2_cap0_14_b8012c9d.csv |
| modelblend_s0.2_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.200000000 | global | 0 | 250 | 0.022496144 | 0.565498962 | 0.562139429 | -0.003120409 | -0.003368575 | -0.000029799 | 0.000475679 | 0.361111111 | -0.442882227 | submission_h009_modelblend_s0_2_cap0_09_0fc5e2a7.csv |
| modelblend_s1_cap0.05 | local_only_high_risk | model_blend | model_blend | delta_pos | 1.000000000 | global | 0 | 250 | 0.012499303 | 0.565498962 | 0.563536432 | -0.002467006 | -0.003013485 | -0.000026774 | 0.000228433 | 0.361111111 | -0.365391422 | submission_h009_modelblend_s1_cap0_05_1ed8b8b8.csv |
| modelblend_s0.75_cap0.05 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.750000000 | global | 0 | 250 | 0.012499303 | 0.565498962 | 0.563536104 | -0.002381107 | -0.002929679 | -0.000025913 | 0.000227834 | 0.361111111 | -0.353447783 | submission_h009_modelblend_s0_75_cap0_05_b581cf4a.csv |
| modelblend_s0.5_cap0.05 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.500000000 | global | 0 | 250 | 0.012499303 | 0.565498962 | 0.563519394 | -0.002312753 | -0.002820674 | -0.000025755 | 0.000225136 | 0.375000000 | -0.342273687 | submission_h009_modelblend_s0_5_cap0_05_92a2a1fc.csv |
| qrank_teacher_rank_dateblock_s0.35 | local_only_high_risk | qrank_dateblock | quantile | teacher_rank | 0.350000000 | dateblock | 0 | 195 | 0.131741255 | 0.565498962 | 0.565701448 | -0.002429285 | -0.002499385 | -0.000251105 | 0.000970888 | 0.361111111 | -0.336096681 | submission_h009_qrank_teacher_rank_dateblock_s0_35_7e41aedd.csv |
| modelblend_s0.35_cap0.05 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.350000000 | global | 0 | 250 | 0.012499303 | 0.565498962 | 0.563492684 | -0.002197524 | -0.002701515 | -0.000023768 | 0.000226205 | 0.388888889 | -0.325970074 | submission_h009_modelblend_s0_35_cap0_05_28a43352.csv |
| modelblend_s0.2_cap0.05 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.200000000 | global | 0 | 250 | 0.012499302 | 0.565498962 | 0.563499052 | -0.002263478 | -0.002484959 | -0.000015994 | 0.000222245 | 0.375000000 | -0.323903359 | submission_h009_modelblend_s0_2_cap0_05_f530fb95.csv |
| modelblend_s0.1_cap0.14 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.100000000 | global | 0 | 250 | 0.034964862 | 0.565498962 | 0.562041340 | -0.002049300 | -0.002176897 | -0.000006434 | 0.000407584 | 0.361111111 | -0.288568975 | submission_h009_modelblend_s0_1_cap0_14_b77451e1.csv |
| modelblend_s0.1_cap0.09 | local_only_high_risk | model_blend | model_blend | delta_pos | 0.100000000 | global | 0 | 250 | 0.022493002 | 0.565498962 | 0.562728994 | -0.001953754 | -0.002084548 | 0.000003145 | 0.000389332 | 0.361111111 | -0.275453788 | submission_h009_modelblend_s0_1_cap0_09_9bb5a080.csv |
| reverse_tailswap_teacher_rank_k50 | reverse_control | reverse_control | tail_swap | teacher_rank | 1.000000000 | global | 50 | 99 | 0.717719703 | 0.565498962 | 0.565498962 | 0.026745149 | 0.015018938 | -0.002058096 | 0.006886939 | 0.472222222 | 3.824034074 | submission_h009_reverse_tailswap_teacher_rank_k50_6fc8bab1.csv |
| reverse_qrank_teacher_rank_s0.6 | reverse_control | reverse_control | quantile | teacher_rank | 0.600000000 | global | 0 | 249 | 0.520365276 | 0.565498962 | 0.570960408 | 0.046279177 | 0.023181344 | -0.002287658 | 0.007049779 | 0.361111111 | 6.103816564 | submission_h009_reverse_qrank_teacher_rank_s0_6_8f99e4ea.csv |
| reverse_tailswap_teacher_rank_k100 | reverse_control | reverse_control | tail_swap | teacher_rank | 1.000000000 | global | 100 | 198 | 0.738384041 | 0.565498962 | 0.565498962 | 0.055789104 | 0.028813936 | -0.003130206 | 0.010095724 | 0.361111111 | 7.301778808 | submission_h009_reverse_tailswap_teacher_rank_k100_b6562c77.csv |
| reverse_qrank_plus_prob_s0.6 | reverse_control | reverse_control | quantile | plus_prob | 0.600000000 | global | 0 | 250 | 0.540947295 | 0.565498962 | 0.576795887 | 0.060942307 | 0.026524804 | -0.004725825 | 0.008350957 | 0.388888889 | 7.706057122 | submission_h009_reverse_qrank_plus_prob_s0_6_ddfdaad9.csv |
| reverse_qrank_consensus_s0.6 | reverse_control | reverse_control | quantile | consensus | 0.600000000 | global | 0 | 249 | 0.542980331 | 0.565498962 | 0.572078645 | 0.063240439 | 0.030869837 | -0.003212777 | 0.007367942 | 0.361111111 | 8.107070247 | submission_h009_reverse_qrank_consensus_s0_6_90159d1b.csv |
| reverse_tailswap_consensus_k50 | reverse_control | reverse_control | tail_swap | consensus | 1.000000000 | global | 50 | 100 | 0.777829393 | 0.565498962 | 0.565498962 | 0.069081324 | 0.042784466 | -0.002224231 | 0.007579443 | 0.472222222 | 9.173203679 | submission_h009_reverse_tailswap_consensus_k50_e66d3dcc.csv |
| reverse_tailswap_consensus_k100 | reverse_control | reverse_control | tail_swap | consensus | 1.000000000 | global | 100 | 198 | 0.809590516 | 0.565498962 | 0.565498962 | 0.098460496 | 0.057209440 | -0.004128497 | 0.011205623 | 0.388888889 | 12.710644484 | submission_h009_reverse_tailswap_consensus_k100_ffaf92d5.csv |
| reverse_qrank_teacher_rank_s1 | reverse_control | reverse_control | quantile | teacher_rank | 1.000000000 | global | 0 | 249 | 0.751319388 | 0.565498962 | 0.565498962 | 0.119828817 | 0.064574657 | -0.003655064 | 0.011660848 | 0.361111111 | 15.146863630 | submission_h009_reverse_qrank_teacher_rank_s1_2ba37d99.csv |
| qrank_consensus_subject_s0.85 | reject | qrank_subject | quantile | consensus | 0.850000000 | subject | 0 | 243 | 0.298276327 | 0.565498962 | 0.565752352 | -0.011893361 | -0.024920108 | -0.001989271 | 0.003295835 | 0.666666667 | -2.167551910 | submission_h009_qrank_consensus_subject_s0_85_07cb83ae.csv |
| qrank_delta_pos_subject_s0.85 | reject | qrank_subject | quantile | delta_pos | 0.850000000 | subject | 0 | 242 | 0.314335649 | 0.565498962 | 0.565769609 | -0.010956174 | -0.026818283 | -0.002063594 | 0.003287792 | 0.666666667 | -2.149899962 | submission_h009_qrank_delta_pos_subject_s0_85_1b6ab313.csv |
| qrank_consensus_subject_s1 | reject | qrank_subject | quantile | consensus | 1.000000000 | subject | 0 | 243 | 0.339242701 | 0.565498962 | 0.565498962 | -0.011381174 | -0.025676355 | -0.002400645 | 0.004109428 | 0.694444444 | -2.141688270 | submission_h009_qrank_consensus_subject_s1_78b5ce45.csv |
| qrank_delta_pos_subject_s1 | reject | qrank_subject | quantile | delta_pos | 1.000000000 | subject | 0 | 242 | 0.375890764 | 0.565498962 | 0.565498962 | -0.009885740 | -0.027329122 | -0.002466478 | 0.004127832 | 0.666666667 | -2.058110577 | submission_h009_qrank_delta_pos_subject_s1_e5fde68c.csv |
| qrank_delta_pos_subject_s0.6 | reject | qrank_subject | quantile | delta_pos | 0.600000000 | subject | 0 | 242 | 0.212633785 | 0.565498962 | 0.566024826 | -0.010748612 | -0.023176490 | -0.001390417 | 0.001961990 | 0.652777778 | -1.991503635 | submission_h009_qrank_delta_pos_subject_s0_6_5293a076.csv |
| qrank_consensus_subject_s0.6 | reject | qrank_subject | quantile | consensus | 0.600000000 | subject | 0 | 243 | 0.219770474 | 0.565498962 | 0.565971640 | -0.011007020 | -0.021240840 | -0.001307459 | 0.001995365 | 0.611111111 | -1.939476277 | submission_h009_qrank_consensus_subject_s0_6_5537a049.csv |
| qrank_plus_prob_global_s1 | reject | qrank_global | quantile | plus_prob | 1.000000000 | global | 0 | 248 | 0.555141923 | 0.565498962 | 0.565498962 | -0.013737895 | -0.014531363 | -0.002739740 | 0.008443728 | 0.375000000 | -1.897821884 | submission_h009_qrank_plus_prob_global_s1_3591550d.csv |
| qrank_consensus_global_s0.6 | reject | qrank_global | quantile | consensus | 0.600000000 | global | 0 | 249 | 0.419965697 | 0.565498962 | 0.568852931 | -0.012723878 | -0.015881375 | -0.003336459 | 0.005870201 | 0.375000000 | -1.873434219 | submission_h009_qrank_consensus_global_s0_6_705aa4fd.csv |
| qrank_consensus_global_s0.35 | reject | qrank_global | quantile | consensus | 0.350000000 | global | 0 | 249 | 0.242925936 | 0.565498962 | 0.568966748 | -0.013042023 | -0.013821865 | -0.001851057 | 0.003495057 | 0.375000000 | -1.836174823 | submission_h009_qrank_consensus_global_s0_35_6c4816a4.csv |
| qrank_plus_prob_global_s0.85 | reject | qrank_global | quantile | plus_prob | 0.850000000 | global | 0 | 248 | 0.492960658 | 0.565498962 | 0.566317002 | -0.013061011 | -0.013564186 | -0.002297323 | 0.007225872 | 0.375000000 | -1.799514173 | submission_h009_qrank_plus_prob_global_s0_85_ef46db0b.csv |
| qrank_teacher_rank_subject_s0.6 | reject | qrank_subject | quantile | teacher_rank | 0.600000000 | subject | 0 | 242 | 0.241774812 | 0.565498962 | 0.565972228 | -0.008975299 | -0.020684968 | -0.001302335 | 0.002168862 | 0.597222222 | -1.712648696 | submission_h009_qrank_teacher_rank_subject_s0_6_0302afd3.csv |
| qrank_teacher_rank_subject_s0.85 | reject | qrank_subject | quantile | teacher_rank | 0.850000000 | subject | 0 | 242 | 0.324764729 | 0.565498962 | 0.565758294 | -0.007392697 | -0.022246773 | -0.001992984 | 0.003503253 | 0.652777778 | -1.608890600 | submission_h009_qrank_teacher_rank_subject_s0_85_9003aad8.csv |
| qrank_plus_prob_subject_s1 | reject | qrank_subject | quantile | plus_prob | 1.000000000 | subject | 0 | 238 | 0.339242701 | 0.565498962 | 0.565498962 | -0.011045466 | -0.013126575 | -0.002123224 | 0.004456398 | 0.541666667 | -1.602172177 | submission_h009_qrank_plus_prob_subject_s1_f1bb841a.csv |
| qrank_human_state_subject_s0.6 | reject | qrank_subject | quantile | human_state | 0.600000000 | subject | 0 | 242 | 0.241774812 | 0.565498962 | 0.565957593 | -0.008035121 | -0.019519143 | -0.001462460 | 0.002041709 | 0.694444444 | -1.573524905 | submission_h009_qrank_human_state_subject_s0_6_81cb6503.csv |
| qrank_plus_prob_global_s0.6 | reject | qrank_global | quantile | plus_prob | 0.600000000 | global | 0 | 248 | 0.359941522 | 0.565498962 | 0.567192669 | -0.010858278 | -0.011006427 | -0.001544436 | 0.004762406 | 0.375000000 | -1.493784554 | submission_h009_qrank_plus_prob_global_s0_6_fe801638.csv |
| qrank_plus_prob_subject_s0.85 | reject | qrank_subject | quantile | plus_prob | 0.850000000 | subject | 0 | 238 | 0.298276327 | 0.565498962 | 0.565764157 | -0.010285564 | -0.012144696 | -0.001753098 | 0.003585642 | 0.527777778 | -1.492434242 | submission_h009_qrank_plus_prob_subject_s0_85_ce5c698b.csv |
| qrank_teacher_rank_global_s0.35 | reject | qrank_global | quantile | teacher_rank | 0.350000000 | global | 0 | 250 | 0.264644081 | 0.565498962 | 0.571446272 | -0.010077105 | -0.012539916 | -0.002377992 | 0.004179316 | 0.375000000 | -1.484627769 | submission_h009_qrank_teacher_rank_global_s0_35_1e164f6d.csv |
| qrank_delta_pos_global_s0.35 | reject | qrank_global | quantile | delta_pos | 0.350000000 | global | 0 | 249 | 0.238122447 | 0.565498962 | 0.571421742 | -0.009920162 | -0.012362367 | -0.001963403 | 0.004907871 | 0.361111111 | -1.453892200 | submission_h009_qrank_delta_pos_global_s0_35_7413e25f.csv |
| qrank_human_state_subject_s0.85 | reject | qrank_subject | quantile | human_state | 0.850000000 | subject | 0 | 242 | 0.324764729 | 0.565498962 | 0.565749526 | -0.006053411 | -0.020597585 | -0.002225184 | 0.003345660 | 0.722222222 | -1.410998705 | submission_h009_qrank_human_state_subject_s0_85_0b5ad0d5.csv |
| qrank_teacher_rank_subject_s1 | reject | qrank_subject | quantile | teacher_rank | 1.000000000 | subject | 0 | 242 | 0.366720894 | 0.565498962 | 0.565498962 | -0.004951236 | -0.021214016 | -0.002408739 | 0.004363307 | 0.652777778 | -1.318182169 | submission_h009_qrank_teacher_rank_subject_s1_97024dd2.csv |
| qrank_low_energy_subject_s0.6 | reject | qrank_subject | quantile | low_energy | 0.600000000 | subject | 0 | 246 | 0.231259950 | 0.565498962 | 0.565853510 | -0.006017445 | -0.017209621 | -0.001340735 | 0.002045542 | 0.597222222 | -1.278933541 | submission_h009_qrank_low_energy_subject_s0_6_2b616a91.csv |
| qrank_plus_prob_subject_s0.6 | reject | qrank_subject | quantile | plus_prob | 0.600000000 | subject | 0 | 238 | 0.219770474 | 0.565498962 | 0.566012070 | -0.008314665 | -0.009734415 | -0.001137314 | 0.002205496 | 0.430555556 | -1.207580928 | submission_h009_qrank_plus_prob_subject_s0_6_bafc0a50.csv |
| tailswap_plus_prob_k125_s1 | reject | tail_swap | tail_swap | plus_prob | 1.000000000 | global | 125 | 248 | 0.555141923 | 0.565498962 | 0.565498962 | -0.007701565 | -0.011816093 | -0.002739740 | 0.008443728 | 0.375000000 | -1.185578091 | submission_h009_tailswap_plus_prob_k125_s1_3591550d.csv |
| qrank_human_state_subject_s1 | reject | qrank_subject | quantile | human_state | 1.000000000 | subject | 0 | 242 | 0.366720894 | 0.565498962 | 0.565498962 | -0.003371747 | -0.019277628 | -0.002683646 | 0.004172905 | 0.722222222 | -1.085182666 | submission_h009_qrank_human_state_subject_s1_3b77b88e.csv |
| tailswap_plus_prob_k125_s0.75 | reject | tail_swap | tail_swap | plus_prob | 0.750000000 | global | 125 | 248 | 0.443836826 | 0.565498962 | 0.566749596 | -0.007099166 | -0.010058120 | -0.001998756 | 0.006315324 | 0.375000000 | -1.069240350 | submission_h009_tailswap_plus_prob_k125_s0_75_427e4634.csv |
| qrank_low_energy_subject_s0.85 | reject | qrank_subject | quantile | low_energy | 0.850000000 | subject | 0 | 246 | 0.312318246 | 0.565498962 | 0.565697690 | -0.003350456 | -0.017618314 | -0.002038499 | 0.003375697 | 0.652777778 | -1.020651077 | submission_h009_qrank_low_energy_subject_s0_85_a58ad4ec.csv |

## Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h009_qrank_delta_pos_subject_s0_35_a4ae7b8b.csv | too_small_to_submit | -0.000717963 | -0.003410757 | 0.000942441 | 0.583333333 | 0.008252554 |
| submission_h009_qrank_human_state_subject_s0_35_1211e4f2.csv | too_small_to_submit | -0.000732357 | -0.003424830 | 0.001124809 | 0.597222222 | 0.007849483 |
| submission_h009_qrank_delta_pos_subject_s0_6_5293a076.csv | too_small_to_submit | -0.001390417 | -0.006379018 | 0.001961990 | 0.652777778 | 0.014147236 |
| submission_h009_qrank_consensus_subject_s0_6_5537a049.csv | too_small_to_submit | -0.001307459 | -0.006135081 | 0.001995365 | 0.611111111 | 0.006314329 |
| submission_h009_qrank_human_state_subject_s0_6_81cb6503.csv | too_small_to_submit | -0.001462460 | -0.006504467 | 0.002041709 | 0.694444444 | 0.013456256 |
| submission_h009_qrank_low_energy_subject_s0_6_2b616a91.csv | too_small_to_submit | -0.001340735 | -0.006335082 | 0.002045542 | 0.597222222 | 0.009723120 |
| submission_h009_qrank_teacher_rank_subject_s0_6_0302afd3.csv | too_small_to_submit | -0.001302335 | -0.006271628 | 0.002168862 | 0.597222222 | 0.006917287 |
| submission_h009_tailswap_plus_prob_k35_s0_75_8ce59748.csv | too_small_to_submit | -0.000682793 | -0.004484377 | 0.002617554 | 0.583333333 | 0.008012899 |
| submission_h009_tailswap_consensus_k75_s0_5_54b2a3cb.csv | too_small_to_submit | -0.001676635 | -0.008017333 | 0.003229507 | 0.638888889 | 0.002143166 |
| submission_h009_qrank_delta_pos_subject_s0_85_1b6ab313.csv | too_small_to_submit | -0.002063594 | -0.009318060 | 0.003287792 | 0.666666667 | 0.020041917 |
| submission_h009_qrank_consensus_subject_s0_85_07cb83ae.csv | too_small_to_submit | -0.001989271 | -0.009005528 | 0.003295835 | 0.666666667 | 0.008945299 |
| submission_h009_qrank_human_state_subject_s0_85_0b5ad0d5.csv | too_small_to_submit | -0.002225184 | -0.009583784 | 0.003345660 | 0.722222222 | 0.019063029 |
| submission_h009_qrank_low_energy_subject_s0_85_a58ad4ec.csv | too_small_to_submit | -0.002038499 | -0.009323451 | 0.003375697 | 0.652777778 | 0.013774420 |
| submission_h009_qrank_teacher_rank_subject_s0_85_9003aad8.csv | too_small_to_submit | -0.001992984 | -0.009247406 | 0.003503253 | 0.652777778 | 0.009799490 |
| submission_h009_tailswap_consensus_k50_s0_75_54633373.csv | too_small_to_submit | -0.001400168 | -0.006868189 | 0.003581484 | 0.652777778 | 0.004413921 |
| submission_h009_tailswap_plus_prob_k35_s1_9ed025c9.csv | too_small_to_submit | -0.001076717 | -0.006030996 | 0.003615414 | 0.638888889 | 0.010683865 |
| submission_h009_qrank_consensus_subject_s1_78b5ce45.csv | too_small_to_submit | -0.002400645 | -0.010703885 | 0.004109428 | 0.694444444 | 0.010523882 |
| submission_h009_qrank_delta_pos_subject_s1_e5fde68c.csv | too_small_to_submit | -0.002466478 | -0.011069097 | 0.004127832 | 0.666666667 | 0.023578726 |
| submission_h009_qrank_human_state_subject_s1_3b77b88e.csv | too_small_to_submit | -0.002683646 | -0.011410155 | 0.004172905 | 0.722222222 | 0.022427093 |
| submission_h009_qrank_teacher_rank_subject_s1_97024dd2.csv | too_small_to_submit | -0.002408739 | -0.011012076 | 0.004363307 | 0.652777778 | 0.011528812 |
| submission_h009_tailswap_consensus_k75_s0_75_09415cfb.csv | too_small_to_submit | -0.002599147 | -0.011816820 | 0.004951864 | 0.680555556 | 0.003214749 |
| submission_h009_tailswap_consensus_k75_s1_9bfc4a43.csv | too_small_to_submit | -0.003444452 | -0.015180933 | 0.006615825 | 0.694444444 | 0.004286331 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h009_modelblend_s0_2_cap0_05_f530fb95.csv | below_selector_resolution | -0.000015994 | -0.000245123 | 0.000222245 | 0.375000000 | -0.006439370 |
| submission_h009_modelblend_s0_5_cap0_05_92a2a1fc.csv | below_selector_resolution | -0.000025755 | -0.000272091 | 0.000225136 | 0.375000000 | -0.006527651 |
| submission_h009_modelblend_s0_35_cap0_05_28a43352.csv | below_selector_resolution | -0.000023768 | -0.000263977 | 0.000226205 | 0.388888889 | -0.006417846 |
| submission_h009_modelblend_s0_75_cap0_05_b581cf4a.csv | below_selector_resolution | -0.000025913 | -0.000275963 | 0.000227834 | 0.361111111 | -0.006552929 |
| submission_h009_modelblend_s1_cap0_05_1ed8b8b8.csv | below_selector_resolution | -0.000026774 | -0.000278680 | 0.000228433 | 0.361111111 | -0.006409111 |
| submission_h009_modelblend_s0_1_cap0_09_9bb5a080.csv | below_selector_resolution | 0.000003145 | -0.000363044 | 0.000389332 | 0.361111111 | -0.008814089 |
| submission_h009_modelblend_s0_1_cap0_14_b77451e1.csv | below_selector_resolution | -0.000006434 | -0.000452646 | 0.000407584 | 0.361111111 | -0.010095856 |
| submission_h009_modelblend_s0_2_cap0_09_0fc5e2a7.csv | below_selector_resolution | -0.000029799 | -0.000526851 | 0.000475679 | 0.361111111 | -0.010773541 |
| submission_h009_modelblend_s0_35_cap0_09_3807b202.csv | below_selector_resolution | -0.000047809 | -0.000631019 | 0.000514279 | 0.388888889 | -0.011587845 |
| submission_h009_modelblend_s0_5_cap0_09_e8b4c3e3.csv | below_selector_resolution | -0.000063222 | -0.000687042 | 0.000530305 | 0.388888889 | -0.011532488 |
| submission_h009_modelblend_s0_75_cap0_09_33ed1de1.csv | below_selector_resolution | -0.000072006 | -0.000756059 | 0.000540735 | 0.375000000 | -0.011732620 |
| submission_h009_modelblend_s1_cap0_09_60cb0e0e.csv | below_selector_resolution | -0.000077504 | -0.000782481 | 0.000543582 | 0.388888889 | -0.011741829 |
| submission_h009_modelblend_s0_2_cap0_14_b8012c9d.csv | below_selector_resolution | -0.000060699 | -0.000840182 | 0.000712962 | 0.388888889 | -0.014390983 |
| submission_h009_modelblend_s0_35_cap0_14_6489dfeb.csv | below_selector_resolution | -0.000103413 | -0.001165353 | 0.000828323 | 0.388888889 | -0.017077763 |
| submission_h009_qrank_delta_pos_dateblock_s0_35_404461b1.csv | below_selector_resolution | -0.000258263 | -0.001772634 | 0.000877081 | 0.361111111 | 0.000178764 |
| submission_h009_modelblend_s0_5_cap0_14_66767de0.csv | below_selector_resolution | -0.000127418 | -0.001304422 | 0.000888873 | 0.388888889 | -0.017964490 |
| submission_h009_modelblend_s0_75_cap0_14_d3a87c6d.csv | below_selector_resolution | -0.000156932 | -0.001419803 | 0.000967035 | 0.388888889 | -0.018013504 |
| submission_h009_qrank_teacher_rank_dateblock_s0_35_7e41aedd.csv | below_selector_resolution | -0.000251105 | -0.001897926 | 0.000970888 | 0.361111111 | 0.002228039 |
| submission_h009_qrank_consensus_subject_s0_35_4eaca577.csv | below_selector_resolution | -0.000653368 | -0.003221687 | 0.000993222 | 0.541666667 | 0.003683359 |
| submission_h009_modelblend_s1_cap0_14_325be5f3.csv | below_selector_resolution | -0.000171617 | -0.001470546 | 0.001002871 | 0.388888889 | -0.017993062 |
| submission_h009_qrank_low_energy_subject_s0_35_61cc5e9c.csv | below_selector_resolution | -0.000672969 | -0.003329787 | 0.001104264 | 0.541666667 | 0.005671820 |
| submission_h009_qrank_plus_prob_subject_s0_35_94a9e381.csv | below_selector_resolution | -0.000555065 | -0.003159908 | 0.001137452 | 0.375000000 | -0.004884041 |
| submission_h009_qrank_teacher_rank_subject_s0_35_3778b1c9.csv | below_selector_resolution | -0.000640046 | -0.003289212 | 0.001207233 | 0.486111111 | 0.004035084 |
| submission_h009_qrank_delta_pos_dateblock_s0_6_297a8cc6.csv | below_selector_resolution | -0.000586958 | -0.003552437 | 0.001542740 | 0.361111111 | 0.000306453 |
| submission_h009_tailswap_plus_prob_k35_s0_5_ce758657.csv | below_selector_resolution | -0.000303478 | -0.002924693 | 0.001715899 | 0.402777778 | 0.005341933 |
| submission_h009_qrank_teacher_rank_dateblock_s0_6_48942451.csv | below_selector_resolution | -0.000593411 | -0.003770878 | 0.001957380 | 0.388888889 | 0.003819495 |
| submission_h009_tailswap_plus_prob_k50_s0_5_a2828055.csv | below_selector_resolution | -0.000396363 | -0.003689823 | 0.002112554 | 0.388888889 | 0.005322249 |
| submission_h009_qrank_plus_prob_subject_s0_6_bafc0a50.csv | below_selector_resolution | -0.001137314 | -0.005976285 | 0.002205496 | 0.430555556 | -0.008372642 |
| submission_h009_qrank_delta_pos_dateblock_s0_85_b43b945f.csv | below_selector_resolution | -0.000964760 | -0.005341936 | 0.002255083 | 0.402777778 | 0.000434142 |
| submission_h009_tailswap_consensus_k50_s0_5_395c1d14.csv | below_selector_resolution | -0.000818218 | -0.004627495 | 0.002368636 | 0.527777778 | 0.002942614 |
| submission_h009_qrank_plus_prob_global_s0_35_1308cf23.csv | below_selector_resolution | -0.000779382 | -0.005458348 | 0.002447223 | 0.361111111 | -0.011048064 |
| submission_h009_tailswap_plus_prob_k75_s0_5_be708aee.csv | below_selector_resolution | -0.000720837 | -0.004879954 | 0.002578577 | 0.388888889 | 0.013930100 |
| submission_h009_qrank_delta_pos_dateblock_s1_4fa5c2f4.csv | below_selector_resolution | -0.001190919 | -0.006411639 | 0.002851772 | 0.444444444 | 0.000510755 |
| submission_h009_tailswap_plus_prob_k100_s0_5_f69351ae.csv | below_selector_resolution | -0.001089674 | -0.006772351 | 0.003122666 | 0.388888889 | 0.001840694 |
| submission_h009_tailswap_plus_prob_k50_s0_75_26e4202c.csv | below_selector_resolution | -0.000792158 | -0.005661007 | 0.003310085 | 0.430555556 | 0.007983374 |
| submission_h009_qrank_consensus_global_s0_35_6c4816a4.csv | below_selector_resolution | -0.001851057 | -0.010624175 | 0.003495057 | 0.375000000 | 0.017291159 |
| submission_h009_qrank_plus_prob_subject_s0_85_ce5c698b.csv | below_selector_resolution | -0.001753098 | -0.008785583 | 0.003585642 | 0.527777778 | -0.011861242 |

## Movement Anatomy

| basename | changed_rows_vs_current | changed_cells_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_h003_tiny | l1_ratio_to_h003_tiny |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h009_modelblend_s0_2_cap0_05_f530fb95.csv | 250 | 250 | 10.703227756 | 0.012499302 | 0.253333248 | 0.790417153 |
| submission_h009_modelblend_s0_35_cap0_05_28a43352.csv | 250 | 250 | 11.481169299 | 0.012499303 | 0.250537715 | 0.847866957 |
| submission_h009_modelblend_s0_5_cap0_05_92a2a1fc.csv | 250 | 250 | 11.802264991 | 0.012499303 | 0.248464501 | 0.871579388 |
| submission_h009_modelblend_s0_75_cap0_05_b581cf4a.csv | 250 | 250 | 12.028437418 | 0.012499303 | 0.247420741 | 0.888281879 |
| submission_h009_modelblend_s1_cap0_05_1ed8b8b8.csv | 250 | 250 | 12.147900620 | 0.012499303 | 0.246347751 | 0.897104055 |
| submission_h009_modelblend_s0_1_cap0_09_9bb5a080.csv | 250 | 250 | 12.288777914 | 0.022493002 | 0.266466255 | 0.907507630 |
| submission_h009_modelblend_s0_1_cap0_14_b77451e1.csv | 250 | 250 | 13.805754616 | 0.034964862 | 0.264609631 | 1.019534061 |
| submission_h009_modelblend_s0_2_cap0_09_0fc5e2a7.csv | 250 | 250 | 16.689088307 | 0.022496144 | 0.256634391 | 1.232463885 |
| submission_h009_modelblend_s0_35_cap0_09_3807b202.csv | 250 | 250 | 19.157093026 | 0.022496182 | 0.253574562 | 1.414722294 |
| submission_h009_modelblend_s0_5_cap0_09_e8b4c3e3.csv | 250 | 250 | 20.193277611 | 0.022496182 | 0.251558957 | 1.491242956 |
| submission_h009_qrank_delta_pos_dateblock_s0_35_404461b1.csv | 189 | 189 | 20.620904983 | 0.101656497 | 0.137454575 | 1.522822590 |
| submission_h009_modelblend_s0_75_cap0_09_33ed1de1.csv | 250 | 250 | 20.974727498 | 0.022496182 | 0.249737419 | 1.548951846 |
| submission_h009_modelblend_s1_cap0_09_60cb0e0e.csv | 250 | 250 | 21.370012270 | 0.022496182 | 0.247976644 | 1.578143028 |
| submission_h009_modelblend_s0_2_cap0_14_b8012c9d.csv | 250 | 250 | 21.878636185 | 0.034985149 | 0.262444068 | 1.615704133 |
| submission_h009_qrank_teacher_rank_dateblock_s0_35_7e41aedd.csv | 195 | 195 | 22.207348565 | 0.131741255 | 0.134215751 | 1.639979044 |
| submission_h009_tailswap_plus_prob_k35_s0_5_ce758657.csv | 68 | 68 | 25.892341400 | 0.298891368 | 0.102673714 | 1.912110182 |
| submission_h009_modelblend_s0_35_cap0_14_6489dfeb.csv | 250 | 250 | 26.837271551 | 0.034985149 | 0.255620670 | 1.981891842 |
| submission_h009_modelblend_s0_5_cap0_14_66767de0.csv | 250 | 250 | 29.280632886 | 0.034985149 | 0.254070670 | 2.162330374 |
| submission_h009_modelblend_s0_75_cap0_14_d3a87c6d.csv | 250 | 250 | 31.284916417 | 0.034985149 | 0.251693677 | 2.310343676 |
| submission_h009_modelblend_s1_cap0_14_325be5f3.csv | 250 | 250 | 32.204073237 | 0.034985149 | 0.250456992 | 2.378222015 |
| submission_h009_qrank_plus_prob_subject_s0_35_94a9e381.csv | 238 | 238 | 32.585972362 | 0.131129791 | 0.234624528 | 2.406424687 |
| submission_h009_tailswap_plus_prob_k50_s0_5_a2828055.csv | 98 | 98 | 32.892766251 | 0.298891368 | 0.132143299 | 2.429080951 |
| submission_h009_qrank_consensus_subject_s0_35_4eaca577.csv | 243 | 243 | 33.227998987 | 0.131129791 | 0.215271220 | 2.453837380 |
| submission_h009_qrank_delta_pos_subject_s0_35_a4ae7b8b.csv | 242 | 242 | 34.214571236 | 0.126592695 | 0.191730053 | 2.526694246 |
| submission_h009_qrank_teacher_rank_subject_s0_35_3778b1c9.csv | 242 | 242 | 34.430372299 | 0.145237439 | 0.190489426 | 2.542630828 |
| submission_h009_qrank_low_energy_subject_s0_35_61cc5e9c.csv | 246 | 246 | 34.470712960 | 0.138409621 | 0.187531336 | 2.545609924 |
| submission_h009_qrank_delta_pos_dateblock_s0_6_297a8cc6.csv | 189 | 189 | 35.350122828 | 0.178807601 | 0.137454575 | 2.610553011 |
| submission_h009_qrank_human_state_subject_s0_35_1211e4f2.csv | 242 | 242 | 35.394384847 | 0.145237439 | 0.200145989 | 2.613821694 |
| submission_h009_tailswap_consensus_k50_s0_5_395c1d14.csv | 97 | 97 | 37.738631270 | 0.271998525 | 0.135749299 | 2.786940740 |
| submission_h009_qrank_teacher_rank_dateblock_s0_6_48942451.csv | 195 | 195 | 38.069740396 | 0.220866947 | 0.134215751 | 2.811392647 |
| submission_h009_tailswap_plus_prob_k35_s0_75_8ce59748.csv | 68 | 68 | 38.838512101 | 0.443836826 | 0.102673714 | 2.868165273 |
| submission_h009_tailswap_plus_prob_k75_s0_5_be708aee.csv | 150 | 150 | 43.431756607 | 0.298891368 | 0.160906813 | 3.207369420 |
| submission_h009_tailswap_plus_prob_k50_s0_75_26e4202c.csv | 98 | 98 | 49.339149376 | 0.443836826 | 0.132143299 | 3.643621426 |
| submission_h009_qrank_plus_prob_global_s0_35_1308cf23.csv | 248 | 248 | 49.628106491 | 0.203905017 | 0.226118259 | 3.664960471 |
| submission_h009_qrank_delta_pos_dateblock_s0_85_b43b945f.csv | 189 | 189 | 50.079340674 | 0.259663317 | 0.137454575 | 3.698283432 |
| submission_h009_tailswap_plus_prob_k35_s1_9ed025c9.csv | 68 | 68 | 51.784682801 | 0.555141923 | 0.102673714 | 3.824220364 |
| submission_h009_qrank_plus_prob_subject_s0_6_bafc0a50.csv | 238 | 238 | 55.861666906 | 0.219770474 | 0.234624528 | 4.125299463 |
| submission_h009_tailswap_consensus_k50_s0_75_54633373.csv | 97 | 97 | 56.607946905 | 0.409297690 | 0.135749299 | 4.180411110 |
| submission_h009_qrank_consensus_subject_s0_6_5537a049.csv | 243 | 243 | 56.962283977 | 0.219770474 | 0.215271220 | 4.206578366 |
| submission_h009_qrank_delta_pos_subject_s0_6_5293a076.csv | 242 | 242 | 58.653550691 | 0.212633785 | 0.191730053 | 4.331475850 |
| submission_h009_qrank_delta_pos_dateblock_s1_4fa5c2f4.csv | 189 | 189 | 58.916871381 | 0.307420340 | 0.137454575 | 4.350921684 |
| submission_h009_tailswap_plus_prob_k100_s0_5_f69351ae.csv | 197 | 197 | 58.950902360 | 0.298891368 | 0.206742320 | 4.353434821 |
| submission_h009_qrank_teacher_rank_subject_s0_6_0302afd3.csv | 242 | 242 | 59.023495370 | 0.241774812 | 0.190489426 | 4.358795704 |
| submission_h009_qrank_low_energy_subject_s0_6_2b616a91.csv | 246 | 246 | 59.092650788 | 0.231259950 | 0.187531336 | 4.363902727 |
| submission_h009_qrank_human_state_subject_s0_6_81cb6503.csv | 242 | 242 | 60.676088309 | 0.241774812 | 0.200145989 | 4.480837189 |
| submission_h009_tailswap_consensus_k75_s0_5_54b2a3cb.csv | 149 | 149 | 63.977083333 | 0.305400159 | 0.161603869 | 4.724610670 |
| submission_h009_tailswap_plus_prob_k75_s0_75_e89983f9.csv | 150 | 150 | 65.147634910 | 0.443836826 | 0.160906813 | 4.811054130 |
| submission_h009_tailswap_plus_prob_k50_s1_fb03fd8f.csv | 98 | 98 | 65.785532501 | 0.555141923 | 0.132143299 | 4.858161901 |
| submission_h009_tailswap_plus_prob_k125_s0_5_135bd875.csv | 248 | 248 | 70.897294987 | 0.298891368 | 0.226118259 | 5.235657816 |
| submission_h009_qrank_plus_prob_subject_s0_85_ce5c698b.csv | 238 | 238 | 79.137361450 | 0.298276327 | 0.234624528 | 5.844174239 |
| submission_h009_qrank_consensus_subject_s0_85_07cb83ae.csv | 243 | 243 | 80.696568968 | 0.298276327 | 0.215271220 | 5.959319352 |
| submission_h009_qrank_delta_pos_subject_s0_85_1b6ab313.csv | 242 | 242 | 83.092530146 | 0.314335649 | 0.191730053 | 6.136257455 |
| submission_h009_qrank_teacher_rank_subject_s0_85_9003aad8.csv | 242 | 242 | 83.616618441 | 0.324764729 | 0.190489426 | 6.174960581 |
| submission_h009_qrank_low_energy_subject_s0_85_a58ad4ec.csv | 246 | 246 | 83.714588616 | 0.312318246 | 0.187531336 | 6.182195530 |
| submission_h009_qrank_plus_prob_global_s0_6_fe801638.csv | 248 | 248 | 85.076753984 | 0.359941522 | 0.226118259 | 6.282789379 |
| submission_h009_qrank_human_state_subject_s0_85_0b5ad0d5.csv | 242 | 242 | 85.957791772 | 0.324764729 | 0.200145989 | 6.347852684 |
| submission_h009_tailswap_plus_prob_k75_s1_32a80ffb.csv | 150 | 150 | 86.863513213 | 0.555141923 | 0.160906813 | 6.414738841 |
| submission_h009_qrank_consensus_global_s0_35_6c4816a4.csv | 249 | 249 | 88.270434628 | 0.242925936 | 0.161728156 | 6.518637855 |
| submission_h009_tailswap_plus_prob_k100_s0_75_468bbf7b.csv | 197 | 197 | 88.426353540 | 0.443836826 | 0.206742320 | 6.530152231 |
| submission_h009_tailswap_consensus_k100_s0_5_40090639.csv | 199 | 199 | 90.044404210 | 0.325218258 | 0.165196609 | 6.649642821 |

## Selection

| candidate_id | basename | file | decision | jackpot_score | worst_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reverse_tailswap_teacher_rank_k50 | submission_h009_reverse_tailswap_teacher_rank_k50_6fc8bab1.csv | hitl/h009_s4_mobility_rank_jackpot/submission_h009_reverse_tailswap_teacher_rank_k50_6fc8bab1.csv | reverse_control | 3.824034074 | 0.026745149 | -0.002058096 | 0.006886939 |
| reverse_qrank_teacher_rank_s0.6 | submission_h009_reverse_qrank_teacher_rank_s0_6_8f99e4ea.csv | hitl/h009_s4_mobility_rank_jackpot/submission_h009_reverse_qrank_teacher_rank_s0_6_8f99e4ea.csv | reverse_control | 6.103816564 | 0.046279177 | -0.002287658 | 0.007049779 |

## Interpretation

- candidate submissions materialized: `88`
- jackpot candidates: `0`
- best candidate: `submission_h009_qrank_delta_pos_subject_s0_35_a4ae7b8b.csv` -> `local_only_high_risk`

No rank-rewrite candidate survived. That would mean the latent is useful only inside a trained model, not as a standalone S4 ordering rewrite.

## Files

- `hitl/h009_s4_mobility_rank_jackpot/h009_local_rank_rewrite_stress.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_candidates.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_selector_scores.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_candidate_anatomy.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_gate_scores.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_family_summary.csv`
- `hitl/h009_s4_mobility_rank_jackpot/h009_selection.csv`
