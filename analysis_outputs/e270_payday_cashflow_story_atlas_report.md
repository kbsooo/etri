# E270 Payday / Cash-Flow Story Atlas

## Question

Could monthly cash-flow events such as payday, card bills, or budget squeeze create sleep-relevant hidden states?

No single payday is assumed. Anchors tested: `10`, `15`, `20`, `25`, `eom`, and `month_start`, with post/pre/near windows and finance-shopping-social interactions.

## Best Verdicts

| story_id | anchor | phase | family | active_train_n | active_test_n | best_label_target | best_label_abs_effect | best_dateblock_target | best_dateblock_delta | subject_best_delta | e247_only_d | e256_only_d | e247_vs_e256_d | e267_moved_d | train_test_gap | public_align_score | verdict | human_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paymonth_start_near3_money_rumination | month_start | near3 | cashflow_transition | 119 | 38 | S1 | 0.093810 | S1 | -0.003751 | -0.011324 | 0.820306 | -0.036706 | 0.939235 | 0.204705 | 0.067918 | 1.660679 | promising_cashflow_gate | Near anchor month_start: finance/shopping/search rumination. |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | 66 | 23 | S2 | 0.238756 | S2 | -0.008061 | -0.002187 | 0.651014 | -0.505080 | 0.899993 | 0.177052 | 0.068398 | 1.463087 | promising_cashflow_gate | After anchor month_start: late shopping or finance phone use. |
| paymonth_start_near7_calendar_only | month_start | near7 | calendar_only | 239 | 99 | S2 | 0.111189 | S2 | -0.005058 | -0.001005 | 0.129339 | -1.257353 | 1.339695 | -0.037138 | 0.247822 | 1.392224 | promising_cashflow_gate | Near anchor month_start: pure monthly-cycle calendar state. |
| pay15_pre7_budget_squeeze | 15 | pre7 | pre_pay_stress | 96 | 70 | S2 | 0.226608 | S4 | 0.003088 | 0.000226 | -0.587936 | -0.248860 | -0.812020 | -0.018930 | 0.286506 | 1.320757 | promising_cashflow_gate | Week before anchor 15: budget squeeze and late money rumination. |
| pay25_pre3_cash_stress | 25 | pre3 | pre_pay_stress | 44 | 19 | Q2 | 0.151622 | Q3 | -0.008576 | -0.004351 | 0.482648 | -0.348351 | 0.836841 | 0.099227 | 0.027231 | 1.272991 | promising_cashflow_gate | Last 3 days before anchor 25: finance/checking stress. |
| pay20_post3_late_shopping | 20 | post3 | post_pay_spend | 56 | 28 | Q1 | 0.149974 | S1 | -0.006337 | -0.004689 | 0.522631 | -0.367925 | 0.783882 | 0.105113 | 0.004853 | 1.263255 | promising_cashflow_gate | After anchor 20: late shopping or finance phone use. |
| pay20_pre7_budget_squeeze | 20 | pre7 | pre_pay_stress | 87 | 81 | S3 | 0.074543 | S3 | -0.003470 | -0.000234 | -0.110366 | 1.064640 | -1.158045 | -0.054830 | 0.241721 | 1.186049 | promising_cashflow_gate | Week before anchor 20: budget squeeze and late money rumination. |
| pay10_near7_calendar_only | 10 | near7 | calendar_only | 207 | 147 | S4 | 0.052104 | S1 | -0.006299 | -0.007100 | -0.473372 | 0.275790 | -0.752423 | 0.006359 | 0.263579 | 1.157356 | promising_cashflow_gate | Near anchor 10: pure monthly-cycle calendar state. |
| pay15_post3_relief_home | 15 | post3 | post_pay_relief | 50 | 46 | Q2 | 0.205985 | S1 | -0.000694 | -0.000016 | -0.148754 | 0.682636 | -1.015769 | -0.168808 | 0.042709 | 1.086322 | promising_cashflow_gate | After anchor 15: money available but quiet home/charging routine. |
| pay15_post3_spend_outing | 15 | post3 | post_pay_spend | 50 | 46 | S1 | 0.113021 | S2 | -0.002574 | 0.002890 | 0.059313 | 0.932069 | -1.006232 | 0.015431 | 0.036939 | 1.050137 | promising_cashflow_gate | First 3 days after anchor 15: spending/social outing state. |
| monthstart_reset_relief | month_start | post3 | bill_cycle | 66 | 23 | S3 | 0.119715 | S2 | -0.003304 | -0.008087 | 0.425489 | -0.356237 | 0.643284 | 0.040630 | 0.152666 | 1.014354 | promising_cashflow_gate | Month-start reset: quiet home after monthly cycle rolls over. |
| pay20_post3_relief_home | 20 | post3 | post_pay_relief | 56 | 28 | Q2 | 0.160145 | S1 | -0.011568 | -0.003110 | 0.247052 | -0.289697 | 0.807443 | 0.022463 | 0.131549 | 1.012623 | promising_cashflow_gate | After anchor 20: money available but quiet home/charging routine. |
| pay10_pre3_cash_stress | 10 | pre3 | pre_pay_stress | 39 | 30 | Q2 | 0.166667 | S4 | 0.000071 | -0.005441 | -0.383154 | -0.192068 | -0.704819 | -0.098393 | 0.389242 | 0.951306 | promising_cashflow_gate | Last 3 days before anchor 10: finance/checking stress. |
| payeom_near3_money_rumination | eom | near3 | cashflow_transition | 123 | 34 | S1 | 0.103114 | Q3 | -0.005666 | -0.002147 | 0.434946 | -0.075268 | 0.568919 | -0.063264 | 0.115818 | 0.949604 | promising_cashflow_gate | Near anchor eom: finance/shopping/search rumination. |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | 50 | 46 | S3 | 0.326243 | Q2 | -0.008158 | -0.012072 | -0.216084 | 0.600922 | -0.802698 | -0.005243 | 0.300791 | 0.941488 | promising_cashflow_gate | After anchor 15: late shopping or finance phone use. |
| paymonth_start_post3_relief_home | month_start | post3 | post_pay_relief | 66 | 23 | S4 | 0.153408 | S3 | -0.004433 | -0.012132 | 0.370638 | -0.458071 | 0.576840 | 0.060423 | 0.066919 | 0.906579 | promising_cashflow_gate | After anchor month_start: money available but quiet home/charging routine. |
| pay25_near7_calendar_only | 25 | near7 | calendar_only | 233 | 100 | Q1 | 0.089040 | S1 | -0.007581 | -0.010192 | 0.342239 | -0.233524 | 0.573527 | -0.016023 | 0.240444 | 0.849246 | promising_cashflow_gate | Near anchor 25: pure monthly-cycle calendar state. |
| payeom_post3_late_shopping | eom | post3 | post_pay_spend | 67 | 21 | Q2 | 0.178912 | S2 | -0.006909 | -0.003353 | 0.248526 | -0.412698 | 0.606333 | 0.017986 | 0.043329 | 0.836833 | promising_cashflow_gate | After anchor eom: late shopping or finance phone use. |
| pay20_near3_money_rumination | 20 | near3 | cashflow_transition | 94 | 61 | S2 | 0.084255 | S1 | -0.002335 | -0.004386 | 0.130045 | -0.572123 | 0.744024 | 0.087314 | 0.041040 | 0.828883 | promising_cashflow_gate | Near anchor 20: finance/shopping/search rumination. |
| pay20_post3_spend_outing | 20 | post3 | post_pay_spend | 56 | 28 | S2 | 0.144109 | S1 | -0.008311 | -0.000258 | 0.396293 | 0.015385 | 0.454612 | 0.101833 | 0.038632 | 0.800514 | promising_cashflow_gate | First 3 days after anchor 20: spending/social outing state. |
| pay10_post7_spend_outing | 10 | post7 | post_pay_spend | 106 | 84 | S3 | 0.124946 | S3 | -0.000706 | 0.001305 | -0.080947 | 0.603131 | -0.779421 | -0.050453 | 0.179422 | 0.795332 | promising_cashflow_gate | First week after anchor 10: broader spending/social state. |
| payeom_post3_spend_outing | eom | post3 | post_pay_spend | 67 | 21 | Q1 | 0.136338 | S2 | -0.006937 | -0.000688 | 0.346724 | -0.002813 | 0.391632 | 0.085182 | 0.072066 | 0.686266 | promising_cashflow_gate | First 3 days after anchor eom: spending/social outing state. |
| pay25_post3_spend_outing | 25 | post3 | post_pay_spend | 67 | 23 | Q1 | 0.204064 | Q2 | -0.005598 | -0.008499 | -0.233299 | 0.128734 | -0.564196 | -0.289076 | 0.165781 | 0.640419 | promising_cashflow_gate | First 3 days after anchor 25: spending/social outing state. |
| payeom_post3_relief_home | eom | post3 | post_pay_relief | 67 | 21 | S4 | 0.207557 | S3 | -0.004216 | 0.004841 | 0.234448 | -0.419247 | 0.412799 | -0.001598 | 0.146256 | 0.610043 | promising_cashflow_gate | After anchor eom: money available but quiet home/charging routine. |
| pay15_near7_calendar_only | 15 | near7 | calendar_only | 198 | 150 | S3 | 0.088622 | S3 | -0.000839 | -0.004656 | -0.581976 | 1.232981 | -2.094842 | -0.002942 | 0.311208 | 2.597839 | public_boundary_diagnostic_only | Near anchor 15: pure monthly-cycle calendar state. |
| payeom_near7_calendar_only | eom | near7 | calendar_only | 240 | 96 | Q1 | 0.091384 | S2 | -0.000188 | 0.000551 | 0.274311 | -1.233775 | 1.545802 | -0.090007 | 0.282063 | 1.713594 | public_boundary_diagnostic_only | Near anchor eom: pure monthly-cycle calendar state. |
| pay10_near3_money_rumination | 10 | near3 | cashflow_transition | 97 | 69 | S2 | 0.157214 | Q2 | 0.000240 | 0.001599 | -0.506037 | -0.412138 | -0.126005 | -0.009250 | 0.152342 | 0.590257 | real_but_not_public_action_safe | Near anchor 10: finance/shopping/search rumination. |
| pay15_near3_money_rumination | 15 | near3 | cashflow_transition | 89 | 80 | S2 | 0.151203 | Q2 | -0.006055 | -0.000315 | -0.209759 | 0.204886 | -0.406952 | 0.017972 | 0.126679 | 0.577851 | real_but_not_public_action_safe | Near anchor 15: finance/shopping/search rumination. |
| paymonth_start_pre3_cash_stress | month_start | pre3 | pre_pay_stress | 53 | 15 | S2 | 0.128365 | S1 | -0.003386 | 0.000697 | 0.139271 | -0.335543 | 0.450781 | 0.041015 | 0.154591 | 0.534998 | real_but_not_public_action_safe | Last 3 days before anchor month_start: finance/checking stress. |
| pay10_post3_late_shopping | 10 | post3 | post_pay_spend | 58 | 39 | S3 | 0.172842 | S4 | -0.002143 | -0.000698 | -0.375512 | -0.519907 | 0.192109 | -0.017143 | 0.158613 | 0.521110 | real_but_not_public_action_safe | After anchor 10: late shopping or finance phone use. |

## Strongest Label Lifts

| story_id | anchor | phase | family | variant | target | high_minus_low | abs_effect | high_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | score_subj_z | S3 | -0.326243 | 0.326243 | 122 |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | score_subj_z | S2 | -0.284650 | 0.284650 | 122 |
| pay10_post3_spend_outing | 10 | post3 | post_pay_spend | score_subj_z | S4 | 0.255901 | 0.255901 | 139 |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | score_subj_z | S2 | -0.238756 | 0.238756 | 151 |
| pay10_post3_spend_outing | 10 | post3 | post_pay_spend | score_subj_z | S2 | 0.237852 | 0.237852 | 139 |
| pay25_pre3_cash_stress | 25 | pre3 | pre_pay_stress | score_active | Q3 | -0.236789 | 0.236789 | 44 |
| pay15_pre7_budget_squeeze | 15 | pre7 | pre_pay_stress | score_subj_z | S2 | 0.226608 | 0.226608 | 114 |
| pay15_pre7_budget_squeeze | 15 | pre7 | pre_pay_stress | score_subj_z | S3 | 0.218202 | 0.218202 | 114 |
| pay15_pre7_budget_squeeze | 15 | pre7 | pre_pay_stress | score_subj_z | S4 | 0.211623 | 0.211623 | 114 |
| pay10_post3_spend_outing | 10 | post3 | post_pay_spend | score_subj_z | Q1 | -0.211157 | 0.211157 | 139 |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | score_subj_z | S3 | -0.208926 | 0.208926 | 151 |
| payeom_post3_relief_home | eom | post3 | post_pay_relief | score_subj_z | S4 | 0.207557 | 0.207557 | 130 |
| pay10_post3_spend_outing | 10 | post3 | post_pay_spend | score_subj_z | S3 | 0.206614 | 0.206614 | 139 |
| pay15_post3_relief_home | 15 | post3 | post_pay_relief | score_subj_z | Q2 | -0.205985 | 0.205985 | 131 |
| pay25_post3_spend_outing | 25 | post3 | post_pay_spend | score_subj_z | Q1 | 0.204064 | 0.204064 | 133 |
| payeom_pre7_budget_squeeze | eom | pre7 | pre_pay_stress | score_subj_z | Q1 | 0.204019 | 0.204019 | 145 |
| pay25_post3_late_shopping | 25 | post3 | post_pay_spend | score_subj_z | Q1 | 0.197556 | 0.197556 | 140 |
| pay25_pre7_budget_squeeze | 25 | pre7 | pre_pay_stress | score_subj_z | S2 | 0.195504 | 0.195504 | 127 |
| payeom_pre3_cash_stress | eom | pre3 | pre_pay_stress | score_subj_z | S1 | -0.189189 | 0.189189 | 134 |
| pay15_pre3_cash_stress | 15 | pre3 | pre_pay_stress | score_subj_z | S1 | -0.184655 | 0.184655 | 129 |
| payeom_post3_late_shopping | eom | post3 | post_pay_spend | score_subj_z | Q2 | 0.178912 | 0.178912 | 113 |
| paymonth_start_post3_spend_outing | month_start | post3 | post_pay_spend | score_subj_z | Q1 | -0.177727 | 0.177727 | 138 |
| pay15_post3_relief_home | 15 | post3 | post_pay_relief | score_subj_z | S3 | -0.174046 | 0.174046 | 131 |
| pay10_post3_late_shopping | 10 | post3 | post_pay_spend | score_subj_z | S3 | 0.172842 | 0.172842 | 134 |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | score_subj_z | Q2 | -0.169421 | 0.169421 | 122 |
| pay20_near7_calendar_only | 20 | near7 | calendar_only | score_subj_z | Q1 | 0.168515 | 0.168515 | 122 |
| pay10_pre3_cash_stress | 10 | pre3 | pre_pay_stress | score_subj_z | Q2 | 0.166667 | 0.166667 | 126 |
| pay20_post3_relief_home | 20 | post3 | post_pay_relief | score_subj_z | Q2 | 0.160145 | 0.160145 | 130 |
| payeom_pre7_budget_squeeze | eom | pre7 | pre_pay_stress | score_subj_z | S1 | 0.157281 | 0.157281 | 145 |
| pay10_near3_money_rumination | 10 | near3 | cashflow_transition | score_subj_z | S2 | 0.157214 | 0.157214 | 152 |

## Best Blocked CV Deltas

| story_id | anchor | phase | family | split | target | delta_logloss | loss_base | loss_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paymonth_start_post7_spend_outing | month_start | post7 | post_pay_spend | subject5 | S2 | -0.021504241 | 0.672004287 | 0.650500046 |
| monthstart_spending_reset | month_start | post7 | bill_cycle | subject5 | S2 | -0.020994040 | 0.672004287 | 0.651010247 |
| pay10_pre7_budget_squeeze | 10 | pre7 | pre_pay_stress | subject5 | S4 | -0.018210461 | 0.701422564 | 0.683212103 |
| paymonth_start_post7_spend_outing | month_start | post7 | post_pay_spend | dateblock5 | S2 | -0.015116879 | 0.586702519 | 0.571585640 |
| monthstart_spending_reset | month_start | post7 | bill_cycle | dateblock5 | S2 | -0.014515803 | 0.586702519 | 0.572186716 |
| pay20_post7_spend_outing | 20 | post7 | post_pay_spend | subject5 | S2 | -0.013858167 | 0.672004287 | 0.658146120 |
| paymonth_start_post3_relief_home | month_start | post3 | post_pay_relief | subject5 | Q1 | -0.012132400 | 0.708061974 | 0.695929575 |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | subject5 | Q2 | -0.012071501 | 0.699451360 | 0.687379859 |
| payeom_post7_spend_outing | eom | post7 | post_pay_spend | subject5 | S2 | -0.011747511 | 0.672004287 | 0.660256777 |
| pay20_post3_relief_home | 20 | post3 | post_pay_relief | dateblock5 | S1 | -0.011567570 | 0.583258774 | 0.571691204 |
| paymonth_start_near3_money_rumination | month_start | near3 | cashflow_transition | subject5 | S2 | -0.011323699 | 0.672004287 | 0.660680588 |
| pay25_near7_calendar_only | 25 | near7 | calendar_only | subject5 | S1 | -0.010192232 | 0.648143005 | 0.637950773 |
| pay15_post7_spend_outing | 15 | post7 | post_pay_spend | subject5 | S2 | -0.009094733 | 0.672004287 | 0.662909554 |
| pay10_post3_relief_home | 10 | post3 | post_pay_relief | dateblock5 | S3 | -0.008995597 | 0.530847570 | 0.521851973 |
| pay20_near7_calendar_only | 20 | near7 | calendar_only | subject5 | S3 | -0.008988622 | 0.662421956 | 0.653433333 |
| payeom_pre7_budget_squeeze | eom | pre7 | pre_pay_stress | dateblock5 | Q2 | -0.008878903 | 0.700602370 | 0.691723467 |
| pay25_pre3_cash_stress | 25 | pre3 | pre_pay_stress | dateblock5 | Q3 | -0.008575642 | 0.678070564 | 0.669494922 |
| pay25_post3_spend_outing | 25 | post3 | post_pay_spend | subject5 | Q2 | -0.008498982 | 0.699451360 | 0.690952378 |
| pay20_post3_spend_outing | 20 | post3 | post_pay_spend | dateblock5 | S1 | -0.008310599 | 0.583258774 | 0.574948175 |
| eom_bill_anxiety | eom | pre7 | bill_cycle | dateblock5 | Q2 | -0.008267019 | 0.700602370 | 0.692335351 |
| pay15_post3_late_shopping | 15 | post3 | post_pay_spend | dateblock5 | Q2 | -0.008158195 | 0.700602370 | 0.692444175 |
| monthstart_reset_relief | month_start | post3 | bill_cycle | subject5 | Q1 | -0.008087128 | 0.708061974 | 0.699974847 |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | dateblock5 | S2 | -0.008061397 | 0.586702519 | 0.578641121 |
| pay25_post3_spend_outing | 25 | post3 | post_pay_spend | subject5 | S3 | -0.007926340 | 0.662421956 | 0.654495616 |
| pay25_near7_calendar_only | 25 | near7 | calendar_only | dateblock5 | S1 | -0.007580584 | 0.583258774 | 0.575678190 |
| paymonth_start_post3_spend_outing | month_start | post3 | post_pay_spend | dateblock5 | S2 | -0.007454763 | 0.586702519 | 0.579247756 |
| pay10_near7_calendar_only | 10 | near7 | calendar_only | subject5 | S1 | -0.007100328 | 0.648143005 | 0.641042677 |
| payeom_post3_spend_outing | eom | post3 | post_pay_spend | dateblock5 | S2 | -0.006937489 | 0.586702519 | 0.579765030 |
| payeom_post3_late_shopping | eom | post3 | post_pay_spend | dateblock5 | S2 | -0.006909476 | 0.586702519 | 0.579793043 |
| pay20_post7_spend_outing | 20 | post7 | post_pay_spend | dateblock5 | Q3 | -0.006662035 | 0.678070564 | 0.671408529 |

## E247-Only Q3 Alignment

| story_id | anchor | phase | family | n_group | mean_group | mean_neutral | cohen_d_group_vs_neutral |
| --- | --- | --- | --- | --- | --- | --- | --- |
| paymonth_start_near3_money_rumination | month_start | near3 | cashflow_transition | 13 | 0.853600 | -0.106489 | 0.820306 |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | 13 | 1.083379 | -0.107995 | 0.651014 |
| pay20_post3_late_shopping | 20 | post3 | post_pay_spend | 13 | 0.827893 | -0.025710 | 0.522631 |
| pay25_pre3_cash_stress | 25 | pre3 | pre_pay_stress | 13 | 0.663478 | 0.007738 | 0.482648 |
| payeom_near3_money_rumination | eom | near3 | cashflow_transition | 13 | 0.310998 | -0.102272 | 0.434946 |
| monthstart_reset_relief | month_start | post3 | bill_cycle | 13 | 1.748601 | 0.142550 | 0.425489 |
| pay25_pre7_budget_squeeze | 25 | pre7 | pre_pay_stress | 13 | 0.534512 | 0.032212 | 0.417222 |
| pay20_post3_spend_outing | 20 | post3 | post_pay_spend | 13 | 0.563452 | 0.015350 | 0.396293 |
| paymonth_start_post3_relief_home | month_start | post3 | post_pay_relief | 13 | 1.025484 | 0.052676 | 0.370638 |
| payeom_post3_spend_outing | eom | post3 | post_pay_spend | 13 | 0.747780 | 0.047602 | 0.346724 |
| pay25_near7_calendar_only | 25 | near7 | calendar_only | 13 | 0.135041 | -0.229572 | 0.342239 |
| payeom_near7_calendar_only | eom | near7 | calendar_only | 13 | 0.050883 | -0.251613 | 0.274311 |
| payeom_post3_late_shopping | eom | post3 | post_pay_spend | 13 | 0.376310 | -0.040207 | 0.248526 |
| pay20_post3_relief_home | 20 | post3 | post_pay_relief | 13 | 0.536599 | 0.130081 | 0.247052 |
| payeom_post3_relief_home | eom | post3 | post_pay_relief | 13 | 1.046929 | 0.156147 | 0.234448 |
| pay15_post7_spend_outing | 15 | post7 | post_pay_spend | 13 | 0.407535 | 0.158883 | 0.220928 |
| pay20_post7_spend_outing | 20 | post7 | post_pay_spend | 13 | 0.129636 | -0.114682 | 0.215492 |
| pay10_pre7_budget_squeeze | 10 | pre7 | pre_pay_stress | 13 | 0.412509 | 0.159859 | 0.212114 |
| monthstart_spending_reset | month_start | post7 | bill_cycle | 13 | 0.322952 | 0.076007 | 0.200614 |
| pay25_near3_money_rumination | 25 | near3 | cashflow_transition | 13 | 0.092489 | -0.073257 | 0.143920 |
| paymonth_start_post3_spend_outing | month_start | post3 | post_pay_spend | 13 | 0.763458 | 0.133763 | 0.142289 |
| paymonth_start_pre3_cash_stress | month_start | pre3 | pre_pay_stress | 13 | -0.051288 | -0.157368 | 0.139271 |
| pay20_near3_money_rumination | 20 | near3 | cashflow_transition | 13 | 0.177352 | 0.029142 | 0.130045 |
| paymonth_start_near7_calendar_only | month_start | near7 | calendar_only | 13 | -0.079466 | -0.227768 | 0.129339 |
| payeom_pre3_cash_stress | eom | pre3 | pre_pay_stress | 13 | -0.082551 | -0.160905 | 0.111406 |

## E247 vs E256 Separation

| story_id | anchor | phase | family | mean_group | mean_neutral | cohen_d_group_vs_neutral |
| --- | --- | --- | --- | --- | --- | --- |
| payeom_near7_calendar_only | eom | near7 | calendar_only | 0.050883 | -1.191956 | 1.545802 |
| paymonth_start_near7_calendar_only | month_start | near7 | calendar_only | -0.079466 | -1.209056 | 1.339695 |
| paymonth_start_near3_money_rumination | month_start | near3 | cashflow_transition | 0.853600 | -0.128341 | 0.939235 |
| paymonth_start_post3_late_shopping | month_start | post3 | post_pay_spend | 1.083379 | -0.448395 | 0.899993 |
| pay25_pre3_cash_stress | 25 | pre3 | pre_pay_stress | 0.663478 | -0.265534 | 0.836841 |
| pay20_post3_relief_home | 20 | post3 | post_pay_relief | 0.536599 | -0.253846 | 0.807443 |
| pay20_post3_late_shopping | 20 | post3 | post_pay_spend | 0.827893 | -0.305403 | 0.783882 |
| pay20_near3_money_rumination | 20 | near3 | cashflow_transition | 0.177352 | -0.440521 | 0.744024 |
| monthstart_reset_relief | month_start | post3 | bill_cycle | 1.748601 | -0.440301 | 0.643284 |
| payeom_post3_late_shopping | eom | post3 | post_pay_spend | 0.376310 | -0.446529 | 0.606333 |
| paymonth_start_post3_relief_home | month_start | post3 | post_pay_relief | 1.025484 | -0.386239 | 0.576840 |
| pay25_near7_calendar_only | 25 | near7 | calendar_only | 0.135041 | -0.474514 | 0.573527 |
| payeom_near3_money_rumination | eom | near3 | cashflow_transition | 0.310998 | -0.143457 | 0.568919 |
| pay25_post3_late_shopping | 25 | post3 | post_pay_spend | -0.155841 | -0.371023 | 0.488448 |
| pay25_post3_relief_home | 25 | post3 | post_pay_relief | 0.030007 | -0.299950 | 0.482558 |
| pay20_post3_spend_outing | 20 | post3 | post_pay_spend | 0.563452 | 0.027105 | 0.454612 |
| paymonth_start_pre3_cash_stress | month_start | pre3 | pre_pay_stress | -0.051288 | -0.318245 | 0.450781 |
| payeom_post3_relief_home | eom | post3 | post_pay_relief | 1.046929 | -0.416990 | 0.412799 |
| payeom_post3_spend_outing | eom | post3 | post_pay_spend | 0.747780 | 0.044893 | 0.391632 |
| payeom_pre3_cash_stress | eom | pre3 | pre_pay_stress | -0.082551 | -0.278401 | 0.365853 |
| pay10_pre7_budget_squeeze | 10 | pre7 | pre_pay_stress | 0.412509 | 0.087459 | 0.356950 |
| monthstart_spending_reset | month_start | post7 | bill_cycle | 0.322952 | 0.002456 | 0.320562 |
| pay10_post3_relief_home | 10 | post3 | post_pay_relief | 0.019078 | -0.308846 | 0.319496 |
| payeom_pre7_budget_squeeze | eom | pre7 | pre_pay_stress | -0.059983 | -0.204169 | 0.281960 |
| paymonth_start_pre7_budget_squeeze | month_start | pre7 | pre_pay_stress | -0.159880 | -0.265400 | 0.253306 |

## Read

- promising cashflow gates: `24`
- public-boundary diagnostics only: `2`
- real but not action-safe: `23`

A useful result here would not prove a literal payday. It would indicate that monthly financial rhythm is a proxy for a human state: relief/spend/social outing, pre-pay stress, bill anxiety, or budget squeeze.
