# H015 Public-Equation Self Feedback

## Question

After H012's public score is included, does the public-equation posterior still imply a coherent movement beyond H012?

## Evidence

- current anchor: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` public `0.5681234831`
- known public observations loaded: `21`
- equations vs H012: `20`
- posterior configs tested: `119`
- selected posterior scenarios: `10 full configs plus leave-one-out variants from top config`
- generated candidates: `280`
- primary upload-safe file: `submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv`

## Selected Configs

| prior_name | ridge_mult |
| --- | --- |
| h012_sharp | 0.000010000 |
| h012_sharp | 0.000030000 |
| h012_sharp | 0.000100000 |
| h012_sharp | 0.000300000 |
| h012_sharp | 0.001000000 |
| h012_current | 0.000010000 |
| h012_sharp | 0.003000000 |
| h012_sharp | 0.010000000 |
| h012_sharp | 0.030000000 |
| h012_current | 0.000030000 |

## Top Config Diagnostics

| prior_name | ridge_mult | loo_mae | loo_p90_abs | loo_spearman | known_fit_mae | q_l1_from_h012 | q_l1_from_prior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| h012_sharp | 0.000010000 | 0.001312381 | 0.001672037 | 0.986466165 | 0.001263364 | 0.017397934 | 0.010759499 |
| h012_sharp | 0.000030000 | 0.001388626 | 0.001728473 | 0.993984962 | 0.001377035 | 0.017265005 | 0.010144517 |
| h012_sharp | 0.000100000 | 0.001548744 | 0.001920635 | 0.980451128 | 0.001573064 | 0.017260182 | 0.009591656 |
| h012_sharp | 0.000300000 | 0.001630717 | 0.002000748 | 0.968421053 | 0.001678349 | 0.017209009 | 0.008991852 |
| h012_sharp | 0.001000000 | 0.001669443 | 0.002001337 | 0.956390977 | 0.001732761 | 0.017068929 | 0.007922541 |
| h012_current | 0.000010000 | 0.001648122 | 0.002101113 | 0.950375940 | 0.001506643 | 0.009226990 | 0.009226990 |
| h012_sharp | 0.003000000 | 0.001694050 | 0.001984520 | 0.957894737 | 0.001759179 | 0.017039706 | 0.006676578 |
| h012_sharp | 0.010000000 | 0.001722312 | 0.001980568 | 0.960902256 | 0.001776290 | 0.017297939 | 0.004972425 |
| h012_sharp | 0.030000000 | 0.001801371 | 0.002058233 | 0.962406015 | 0.001834373 | 0.017794289 | 0.003077714 |
| h012_current | 0.000030000 | 0.001805336 | 0.002129809 | 0.968421053 | 0.001718793 | 0.008256340 | 0.008256340 |
| h012_sharp | 0.100000000 | 0.001895506 | 0.002161252 | 0.963909774 | 0.001910185 | 0.018345825 | 0.001389012 |
| h012_sharp | 0.300000000 | 0.001943346 | 0.002215149 | 0.962406015 | 0.001948592 | 0.018635446 | 0.000602920 |
| h012_sharp | 1.000000000 | 0.001967380 | 0.002240792 | 0.962406015 | 0.001968450 | 0.018760050 | 0.000295864 |
| h012_sharp | 3.000000000 | 0.001982001 | 0.002256269 | 0.962406015 | 0.001981552 | 0.018792331 | 0.000208030 |
| h012_sharp | 10.000000000 | 0.002003907 | 0.002279201 | 0.962406015 | 0.002002569 | 0.018788679 | 0.000148315 |
| h012_current | 0.000100000 | 0.002040870 | 0.002195622 | 0.987969925 | 0.001989049 | 0.007354548 | 0.007354548 |
| h012_sharp | 30.000000000 | 0.002031020 | 0.002307447 | 0.962406015 | 0.002029567 | 0.018768812 | 0.000088115 |
| h012_sharp | 100.000000000 | 0.002054976 | 0.002332340 | 0.962406015 | 0.002054166 | 0.018748990 | 0.000036780 |
| h012_sharp | 300.000000000 | 0.002065720 | 0.002343490 | 0.962406015 | 0.002065349 | 0.018739878 | 0.000013945 |
| h012_sharp | 1000.000000000 | 0.002070478 | 0.002348401 | 0.962406015 | 0.002070357 | 0.018735997 | 0.000004451 |
| h012_current | 0.000300000 | 0.002220466 | 0.002333279 | 0.992481203 | 0.002187613 | 0.006528403 | 0.006528403 |
| h012_current | 0.001000000 | 0.002378589 | 0.002506849 | 0.992481203 | 0.002357319 | 0.005363679 | 0.005363679 |
| h012_current | 0.003000000 | 0.002567699 | 0.002750138 | 0.996992481 | 0.002555250 | 0.004193316 | 0.004193316 |
| h012_current | 0.010000000 | 0.002792069 | 0.002980930 | 0.996992481 | 0.002790627 | 0.003035746 | 0.003035746 |
| top6_wide_soft | 0.000010000 | 0.002697403 | 0.003742771 | 0.903759398 | 0.002396605 | 0.008991965 | 0.017281473 |

## Candidate Selection

| candidate_id | h015_decision | family | target_subset | changed_cells | posterior_delta_mean_vs_h012 | posterior_delta_p90_vs_h012 | posterior_beats_h012_rate | expected_public_if_posterior | max_abs_prob_delta_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_all_k1600_a0.7 | post_h012_big_bet | top | all | 1600 | -0.001586219 | -0.001149849 | 0.966666667 | 0.566537264 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1600_a0.7_267e5aee.csv |
| top_all_k1200_a0.7 | post_h012_big_bet | top | all | 1200 | -0.001564888 | -0.001129365 | 0.966666667 | 0.566558595 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1200_a0.7_196fff84.csv |
| top_all_k1600_a1 | post_h012_big_bet | top | all | 1600 | -0.001689645 | -0.001066259 | 0.933333333 | 0.566433838 | 0.072220084 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1600_a1_7a034bae.csv |
| top_all_k1200_a1 | post_h012_big_bet | top | all | 1200 | -0.001666928 | -0.001044752 | 0.933333333 | 0.566456555 | 0.072220084 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1200_a1_a39d6e49.csv |
| top_all_k800_a0.7 | post_h012_big_bet | top | all | 800 | -0.001466361 | -0.001021688 | 0.966666667 | 0.566657122 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k800_a0.7_8bdec3ac.csv |
| stable_all_k800_a0.9 | post_h012_big_bet | stable_top | all | 800 | -0.001528860 | -0.001017428 | 0.933333333 | 0.566594623 | 0.065448434 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k800_a0.9_ad515f27.csv |
| stable_all_k800_a0.6 | post_h012_big_bet | stable_top | all | 800 | -0.001330708 | -0.000989753 | 1.000000000 | 0.566792775 | 0.045654676 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k800_a0.6_8c7ca8c6.csv |
| direct_all_a0.45 | post_h012_big_bet | direct | all | 1750 | -0.001237997 | -0.000957277 | 1.000000000 | 0.566885486 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.45_ad724a1d.csv |
| top_all_k1600_a0.45 | post_h012_big_bet | top | all | 1600 | -0.001237643 | -0.000957119 | 1.000000000 | 0.566885840 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1600_a0.45_3e85c1e7.csv |
| top_all_k1200_a0.45 | post_h012_big_bet | top | all | 1200 | -0.001221020 | -0.000941041 | 1.000000000 | 0.566902463 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1200_a0.45_a740d598.csv |
| top_all_k800_a1 | post_h012_big_bet | top | all | 800 | -0.001561537 | -0.000926289 | 0.933333333 | 0.566561946 | 0.072220084 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k800_a1_af900586.csv |
| top_S_k1200_a0.7 | post_h012_big_bet | top | S | 998 | -0.001235364 | -0.000867216 | 0.966666667 | 0.566888120 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1200_a0.7_00d6ac75.csv |
| top_S_k1600_a0.7 | post_h012_big_bet | top | S | 998 | -0.001235364 | -0.000867216 | 0.966666667 | 0.566888120 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1600_a0.7_00d6ac75.csv |
| top_S_k800_a0.7 | post_h012_big_bet | top | S | 800 | -0.001228352 | -0.000863370 | 0.966666667 | 0.566895132 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k800_a0.7_dce4429d.csv |
| top_all_k800_a0.45 | post_h012_big_bet | top | all | 800 | -0.001144374 | -0.000858512 | 1.000000000 | 0.566979109 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k800_a0.45_f30fd4d5.csv |
| stable_S_k800_a0.9 | post_h012_big_bet | stable_top | S | 800 | -0.001255231 | -0.000851704 | 0.933333333 | 0.566868252 | 0.062951066 | hitl/h015_public_equation_self_feedback/submission_h015_stable_S_k800_a0.9_b83e4d7f.csv |
| stable_S_k800_a0.6 | post_h012_big_bet | stable_top | S | 800 | -0.001103451 | -0.000834433 | 1.000000000 | 0.567020032 | 0.045654676 | hitl/h015_public_equation_self_feedback/submission_h015_stable_S_k800_a0.6_7a09741a.csv |
| top_S_k1200_a1 | post_h012_big_bet | top | S | 998 | -0.001307335 | -0.000781410 | 0.933333333 | 0.566816148 | 0.068405476 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1200_a1_48b09c30.csv |
| top_S_k1600_a1 | post_h012_big_bet | top | S | 998 | -0.001307335 | -0.000781410 | 0.933333333 | 0.566816148 | 0.068405476 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1600_a1_48b09c30.csv |
| top_S_k800_a1 | post_h012_big_bet | top | S | 800 | -0.001300031 | -0.000778629 | 0.933333333 | 0.566823452 | 0.068405476 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k800_a1_7e0cd499.csv |
| stable_all_k800_a0.35 | post_h012_big_bet | stable_top | all | 800 | -0.000938625 | -0.000739735 | 1.000000000 | 0.567184858 | 0.028776433 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k800_a0.35_a5df27fc.csv |
| top_S_k1200_a0.45 | post_h012_big_bet | top | S | 998 | -0.000969772 | -0.000733106 | 1.000000000 | 0.567153711 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1200_a0.45_5f411ce3.csv |
| top_S_k1600_a0.45 | post_h012_big_bet | top | S | 998 | -0.000969772 | -0.000733106 | 1.000000000 | 0.567153711 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k1600_a0.45_5f411ce3.csv |
| direct_all_a0.3 | post_h012_big_bet | direct | all | 1750 | -0.000919857 | -0.000732710 | 1.000000000 | 0.567203626 | 0.025050211 | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.3_c8366e21.csv |
| top_S_k800_a0.45 | post_h012_big_bet | top | S | 800 | -0.000964247 | -0.000729616 | 1.000000000 | 0.567159236 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k800_a0.45_339fcd05.csv |
| top_all_k400_a0.7 | post_h012_big_bet | top | all | 400 | -0.001170486 | -0.000716837 | 1.000000000 | 0.566952997 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k400_a0.7_39885b32.csv |
| stable_all_k400_a0.6 | post_h012_big_bet | stable_top | all | 400 | -0.001063908 | -0.000716044 | 1.000000000 | 0.567059575 | 0.045654676 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k400_a0.6_166bdcb4.csv |
| stable_all_k400_a0.9 | post_h012_big_bet | stable_top | all | 400 | -0.001223148 | -0.000701351 | 0.933333333 | 0.566900336 | 0.065448434 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k400_a0.9_7a9d53ff.csv |
| top_S_k400_a0.7 | post_h012_big_bet | top | S | 400 | -0.001045499 | -0.000686475 | 0.966666667 | 0.567077984 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k400_a0.7_a893a45f.csv |
| stable_S_k400_a0.6 | post_h012_big_bet | stable_top | S | 400 | -0.000940352 | -0.000677785 | 1.000000000 | 0.567183131 | 0.045654676 | hitl/h015_public_equation_self_feedback/submission_h015_stable_S_k400_a0.6_76b11330.csv |
| stable_S_k400_a0.9 | post_h012_big_bet | stable_top | S | 400 | -0.001068686 | -0.000674836 | 0.933333333 | 0.567054797 | 0.062951066 | hitl/h015_public_equation_self_feedback/submission_h015_stable_S_k400_a0.9_a824f8fb.csv |
| top_all_k400_a0.45 | post_h012_big_bet | top | all | 400 | -0.000913268 | -0.000621637 | 1.000000000 | 0.567210215 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k400_a0.45_e85644dd.csv |
| top_all_k400_a1 | post_h012_big_bet | top | all | 400 | -0.001246716 | -0.000598647 | 0.933333333 | 0.566876767 | 0.072220084 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k400_a1_a25e29b1.csv |
| top_S_k400_a1 | post_h012_big_bet | top | S | 400 | -0.001105966 | -0.000593074 | 0.933333333 | 0.567017517 | 0.068405476 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k400_a1_30d95344.csv |
| top_S_k400_a0.45 | post_h012_big_bet | top | S | 400 | -0.000821315 | -0.000590514 | 1.000000000 | 0.567302168 | 0.035869661 | hitl/h015_public_equation_self_feedback/submission_h015_top_S_k400_a0.45_83474cb0.csv |
| top_all_k200_a0.7 | post_h012_big_bet | top | all | 200 | -0.000830389 | -0.000408139 | 1.000000000 | 0.567293094 | 0.051641678 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k200_a0.7_22b50f30.csv |
| stable_all_k200_a0.9 | post_h012_big_bet | stable_top | all | 200 | -0.000871947 | -0.000385520 | 0.966666667 | 0.567251536 | 0.065448434 | hitl/h015_public_equation_self_feedback/submission_h015_stable_all_k200_a0.9_94d06989.csv |
| top_all_k200_a1 | post_h012_big_bet | top | all | 200 | -0.000887667 | -0.000284453 | 0.966666667 | 0.567235816 | 0.072220084 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k200_a1_e79c4894.csv |
| top_all_k1600_a0.25 | post_h012_sensor | top | all | 1600 | -0.000794480 | -0.000638633 | 1.000000000 | 0.567329004 | 0.021200429 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1600_a0.25_8565e1a2.csv |
| top_all_k1200_a0.25 | post_h012_sensor | top | all | 1200 | -0.000783950 | -0.000628406 | 1.000000000 | 0.567339533 | 0.021200429 | hitl/h015_public_equation_self_feedback/submission_h015_top_all_k1200_a0.25_7eb69d0c.csv |

## Interpretation

- The post-H012 equation system promotes a new high-information candidate.
- This is not a safe microblend. It tests whether H012 was an under-amplified public-state posterior rather than a one-shot optimum.

## Files

- `hitl/h015_public_equation_self_feedback/h015_posterior_configs.csv`
- `hitl/h015_public_equation_self_feedback/h015_known_equations.csv`
- `hitl/h015_public_equation_self_feedback/h015_cell_posterior.csv`
- `hitl/h015_public_equation_self_feedback/h015_candidates.csv`
- `hitl/h015_public_equation_self_feedback/h015_posterior_scenarios.csv`
