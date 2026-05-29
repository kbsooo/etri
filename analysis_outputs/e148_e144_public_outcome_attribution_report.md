# E148 E144 Public Outcome Attribution

## Question

Before E144 public feedback is known, map each E145 score band to the target/component support pattern that would make that band plausible under public-free priors.

This is not a submission generator. It is a pre-registered interpretation guardrail for `submission_e144_activeboundary_d7b4b331.csv`.

## Outcome Rates

### Global Prior

| outcome | world_rate | mean_delta_vs_e95 | p05_delta | p50_delta | p95_delta | support_flip_share_mean | top20_support_rate | fine_tail_support_rate | body_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breakthrough_win | 0.662544000 | -0.000089002 | -0.000180245 | -0.000080817 | -0.000026531 | 0.504958722 | 0.507013270 | 0.462519974 | 0.505907663 |
| clean_win | 0.064664000 | -0.000013441 | -0.000018531 | -0.000013388 | -0.000007102 | 0.464791022 | 0.464530496 | 0.459441626 | 0.464910636 |
| micro_win | 0.018352000 | -0.000004594 | -0.000005959 | -0.000005388 | -0.000003674 | 0.460088312 | 0.460385789 | 0.466960913 | 0.459934639 |
| tie | 0.021772000 | -0.000000502 | -0.000001959 | -0.000000245 | 0.000001469 | 0.457912880 | 0.459452508 | 0.415686815 | 0.458857065 |
| fine_loss_branch_alive | 0.027696000 | 0.000005606 | 0.000002612 | 0.000006041 | 0.000007755 | 0.454665978 | 0.454946563 | 0.480592865 | 0.454086246 |
| branch_loss | 0.023448000 | 0.000011561 | 0.000009469 | 0.000011183 | 0.000014612 | 0.451500292 | 0.453258274 | 0.429553338 | 0.451991032 |
| hard_fail | 0.181524000 | 0.000053411 | 0.000017469 | 0.000045469 | 0.000117469 | 0.429253282 | 0.428364293 | 0.453485490 | 0.428711444 |

### Subject Prior

| outcome | world_rate | mean_delta_vs_e95 | p05_delta | p50_delta | p95_delta | support_flip_share_mean | top20_support_rate | fine_tail_support_rate | body_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breakthrough_win | 0.497248000 | -0.000071980 | -0.000148817 | -0.000062531 | -0.000024817 | 0.495910075 | 0.471818489 | 0.429737609 | 0.497389707 |
| clean_win | 0.079392000 | -0.000013397 | -0.000018531 | -0.000013388 | -0.000007102 | 0.464767852 | 0.440810157 | 0.426136554 | 0.465631658 |
| micro_win | 0.023120000 | -0.000004548 | -0.000006531 | -0.000003674 | -0.000003674 | 0.460063717 | 0.435337370 | 0.456415802 | 0.460145286 |
| tie | 0.033068000 | -0.000000546 | -0.000001959 | -0.000000245 | 0.000001469 | 0.457936560 | 0.435490504 | 0.390856215 | 0.459436493 |
| fine_loss_branch_alive | 0.033340000 | 0.000005800 | 0.000002612 | 0.000006041 | 0.000007755 | 0.454563061 | 0.431289742 | 0.458098380 | 0.454484010 |
| branch_loss | 0.036668000 | 0.000011455 | 0.000009469 | 0.000011183 | 0.000014612 | 0.451556881 | 0.430571616 | 0.391708483 | 0.452895106 |
| hard_fail | 0.297164000 | 0.000056481 | 0.000019183 | 0.000048326 | 0.000122041 | 0.427621513 | 0.405247607 | 0.423490620 | 0.427713881 |

### Nearest-Hard Prior

| outcome | world_rate | mean_delta_vs_e95 | p05_delta | p50_delta | p95_delta | support_flip_share_mean | top20_support_rate | fine_tail_support_rate | body_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breakthrough_win | 0.514704000 | -0.000061765 | -0.000124245 | -0.000055674 | -0.000023102 | 0.490479909 | 0.556493441 | 0.358602226 | 0.493428726 |
| clean_win | 0.102048000 | -0.000013221 | -0.000019674 | -0.000011674 | -0.000008245 | 0.464674225 | 0.531367592 | 0.346361516 | 0.467319727 |
| micro_win | 0.018864000 | -0.000005131 | -0.000006531 | -0.000005388 | -0.000003674 | 0.460373582 | 0.526950806 | 0.343431934 | 0.462988426 |
| tie | 0.047832000 | -0.000000033 | -0.000001959 | -0.000000245 | 0.000001469 | 0.457663614 | 0.522470313 | 0.369748983 | 0.459629407 |
| fine_loss_branch_alive | 0.031700000 | 0.000004918 | 0.000003183 | 0.000004898 | 0.000007755 | 0.455031603 | 0.521886435 | 0.326892744 | 0.457896820 |
| branch_loss | 0.054456000 | 0.000012099 | 0.000009469 | 0.000012898 | 0.000014612 | 0.451214429 | 0.517221243 | 0.353217888 | 0.453405656 |
| hard_fail | 0.230396000 | 0.000046662 | 0.000019183 | 0.000039183 | 0.000094612 | 0.432840841 | 0.497868887 | 0.349935907 | 0.434694615 |

## Top Responsibility Groups

| prior | outcome | rank | direction | group_kind | group | cells | world_rate | support_rate_lift | delta_shift_per_all | conditional_delta_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | branch_loss | 1 | blame | target | S2 | 23 | 0.023448000 | -0.030687604 | 0.000008066 | 0.000020133 |
| global | branch_loss | 2 | blame | component | inherited_e143_body | 161 | 0.023448000 | -0.032685068 | 0.000060141 | 0.000011780 |
| global | branch_loss | 3 | blame | target | Q3 | 56 | 0.023448000 | -0.032523839 | 0.000020815 | 0.000011119 |
| global | clean_win | 1 | credit | target | S4 | 21 | 0.064664000 | -0.018866671 | 0.000004528 | -0.000031815 |
| global | clean_win | 2 | credit | component | inherited_e143_body | 161 | 0.064664000 | -0.019765463 | 0.000036368 | -0.000011992 |
| global | clean_win | 3 | credit | component | e144_fine_tail_delta | 24 | 0.064664000 | -0.000028707 | 0.000000001 | -0.000001449 |
| global | fine_loss_branch_alive | 1 | blame | target | S2 | 23 | 0.027696000 | -0.029258610 | 0.000007691 | 0.000019757 |
| global | fine_loss_branch_alive | 2 | blame | target | Q3 | 56 | 0.027696000 | -0.031257386 | 0.000020005 | 0.000010308 |
| global | hard_fail | 1 | blame | component | inherited_e143_body | 161 | 0.181524000 | -0.055964655 | 0.000102975 | 0.000054615 |
| global | hard_fail | 2 | blame | target | S2 | 23 | 0.181524000 | -0.053724992 | 0.000014122 | 0.000026188 |
| global | hard_fail | 3 | blame | target | Q3 | 56 | 0.181524000 | -0.055824806 | 0.000035728 | 0.000026031 |
| global | micro_win | 1 | credit | target | S4 | 21 | 0.018352000 | -0.024298042 | 0.000005832 | -0.000030511 |
| global | micro_win | 2 | credit | component | inherited_e143_body | 161 | 0.018352000 | -0.024741460 | 0.000045524 | -0.000002836 |
| global | micro_win | 3 | credit | component | e144_fine_tail_delta | 24 | 0.018352000 | 0.007490579 | -0.000000308 | -0.000001758 |
| global | tie | 1 | blame | target | S2 | 23 | 0.021772000 | -0.025094794 | 0.000006596 | 0.000018663 |
| global | tie | 2 | blame | target | Q3 | 56 | 0.021772000 | -0.025806291 | 0.000016516 | 0.000006819 |
| nearest_hard085 | branch_loss | 1 | blame | target | S3 | 47 | 0.054456000 | -0.010004896 | 0.000005121 | 0.000039896 |
| nearest_hard085 | branch_loss | 2 | blame | target | Q3 | 56 | 0.054456000 | -0.018362155 | 0.000011752 | 0.000020197 |
| nearest_hard085 | clean_win | 1 | credit | target | Q1 | 38 | 0.102048000 | -0.003736163 | 0.000001623 | -0.000033764 |
| nearest_hard085 | clean_win | 2 | credit | target | S4 | 21 | 0.102048000 | -0.004595824 | 0.000001103 | -0.000021241 |
| nearest_hard085 | fine_loss_branch_alive | 1 | blame | target | S3 | 47 | 0.031700000 | -0.021329271 | 0.000005066 | 0.000039842 |
| nearest_hard085 | fine_loss_branch_alive | 2 | blame | target | Q3 | 56 | 0.031700000 | -0.013764482 | 0.000008809 | 0.000017255 |
| nearest_hard085 | hard_fail | 1 | blame | target | S3 | 47 | 0.230396000 | -0.019677441 | 0.000009551 | 0.000044327 |
| nearest_hard085 | hard_fail | 2 | blame | component | inherited_e143_body | 161 | 0.230396000 | -0.037040863 | 0.000068155 | 0.000043606 |
| nearest_hard085 | hard_fail | 3 | blame | target | Q3 | 56 | 0.230396000 | -0.037077613 | 0.000023730 | 0.000032175 |
| nearest_hard085 | micro_win | 1 | credit | target | Q1 | 38 | 0.018864000 | -0.008459711 | 0.000003674 | -0.000031713 |
| nearest_hard085 | micro_win | 2 | credit | target | S4 | 21 | 0.018864000 | -0.008422597 | 0.000002021 | -0.000020322 |
| nearest_hard085 | tie | 1 | blame | target | S3 | 47 | 0.047832000 | 0.001606114 | 0.000002738 | 0.000037514 |
| nearest_hard085 | tie | 2 | blame | target | Q3 | 56 | 0.047832000 | -0.012407632 | 0.000007941 | 0.000016386 |
| subject | branch_loss | 1 | blame | component | inherited_e143_body | 161 | 0.036668000 | -0.016089987 | 0.000029606 | 0.000010117 |
| subject | branch_loss | 2 | blame | target | S3 | 47 | 0.036668000 | -0.024596441 | 0.000005106 | 0.000006582 |
| subject | branch_loss | 3 | blame | target | S2 | 23 | 0.036668000 | -0.012089080 | 0.000003178 | 0.000003003 |
| subject | clean_win | 1 | credit | component | inherited_e143_body | 161 | 0.079392000 | -0.003353435 | 0.000006170 | -0.000013319 |
| subject | clean_win | 2 | credit | target | Q3 | 56 | 0.079392000 | -0.004186254 | 0.000002679 | -0.000007058 |
| subject | clean_win | 3 | credit | target | Q1 | 38 | 0.079392000 | -0.002603785 | 0.000001131 | -0.000006283 |
| subject | fine_loss_branch_alive | 1 | blame | component | inherited_e143_body | 161 | 0.033340000 | -0.014501083 | 0.000026682 | 0.000007193 |
| subject | fine_loss_branch_alive | 2 | blame | target | S3 | 47 | 0.033340000 | 0.009189752 | 0.000002436 | 0.000003912 |
| subject | fine_loss_branch_alive | 3 | blame | target | S2 | 23 | 0.033340000 | -0.009825087 | 0.000002583 | 0.000002408 |
| subject | hard_fail | 1 | blame | component | inherited_e143_body | 161 | 0.297164000 | -0.041271212 | 0.000075939 | 0.000056450 |
| subject | hard_fail | 2 | blame | target | Q3 | 56 | 0.297164000 | -0.044874376 | 0.000028720 | 0.000018982 |
| subject | hard_fail | 3 | blame | target | Q1 | 38 | 0.297164000 | -0.047723785 | 0.000020726 | 0.000013312 |
| subject | micro_win | 1 | credit | target | Q3 | 56 | 0.023120000 | -0.008574897 | 0.000005488 | -0.000004249 |
| subject | micro_win | 2 | credit | component | inherited_e143_body | 161 | 0.023120000 | -0.008839807 | 0.000016265 | -0.000003224 |
| subject | micro_win | 3 | credit | target | Q1 | 38 | 0.023120000 | -0.010834559 | 0.000004705 | -0.000002709 |
| subject | tie | 1 | blame | target | S3 | 47 | 0.033068000 | -0.021625826 | 0.000003311 | 0.000004787 |
| subject | tie | 2 | blame | target | S2 | 23 | 0.033068000 | -0.006063991 | 0.000001594 | 0.000001420 |

## Fine-Loss Anatomy

| prior | group_kind | group | cells | world_rate | conditional_support_rate | unconditional_support_rate | support_rate_lift | conditional_delta_per_all | delta_shift_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | component | inherited_e143_body | 161 | 0.027696000 | 0.454086246 | 0.484676099 | -0.030589853 | 0.000007925 | 0.000056285 |
| global | target | Q3 | 56 | 0.027696000 | 0.447122328 | 0.478379714 | -0.031257386 | 0.000010308 | 0.000020005 |
| global | target | Q1 | 38 | 0.027696000 | 0.466497157 | 0.497728421 | -0.031231264 | 0.000003220 | 0.000013563 |
| global | target | S2 | 23 | 0.027696000 | 0.503780172 | 0.533038783 | -0.029258610 | 0.000019757 | 0.000007691 |
| global | target | S4 | 21 | 0.027696000 | 0.477057027 | 0.508480381 | -0.031423354 | -0.000028801 | 0.000007542 |
| global | target | S3 | 47 | 0.027696000 | 0.431302777 | 0.434451404 | -0.003148628 | 0.000001122 | 0.000006616 |
| global | component | e144_fine_tail_delta | 24 | 0.027696000 | 0.480592865 | 0.459470333 | 0.021122532 | -0.000002319 | -0.000000869 |
| nearest_hard085 | component | inherited_e143_body | 161 | 0.031700000 | 0.457896820 | 0.471735478 | -0.013838658 | 0.000000913 | 0.000025463 |
| nearest_hard085 | target | Q3 | 56 | 0.031700000 | 0.436268589 | 0.450033071 | -0.013764482 | 0.000017255 | 0.000008809 |
| nearest_hard085 | target | Q1 | 38 | 0.031700000 | 0.541992363 | 0.555394000 | -0.013401637 | -0.000029566 | 0.000005820 |
| nearest_hard085 | target | S3 | 47 | 0.031700000 | 0.292505537 | 0.313834809 | -0.021329271 | 0.000039842 | 0.000005066 |
| nearest_hard085 | target | S2 | 23 | 0.031700000 | 0.592390619 | 0.606195826 | -0.013805208 | -0.000003535 | 0.000003629 |
| nearest_hard085 | target | S4 | 21 | 0.031700000 | 0.436538982 | 0.450150857 | -0.013611876 | -0.000019077 | 0.000003267 |
| nearest_hard085 | component | e144_fine_tail_delta | 24 | 0.031700000 | 0.326892744 | 0.354305000 | -0.027412256 | 0.000004005 | 0.000001128 |
| subject | component | inherited_e143_body | 161 | 0.033340000 | 0.454484010 | 0.468985093 | -0.014501083 | 0.000007193 | 0.000026682 |
| subject | target | Q3 | 56 | 0.033340000 | 0.462434656 | 0.478443286 | -0.016008630 | 0.000000508 | 0.000010246 |
| subject | target | Q1 | 38 | 0.033340000 | 0.475174439 | 0.490983895 | -0.015809456 | -0.000000548 | 0.000006866 |
| subject | target | S4 | 21 | 0.033340000 | 0.359053904 | 0.372600190 | -0.013546287 | -0.000000481 | 0.000003251 |
| subject | target | S2 | 23 | 0.033340000 | 0.569781696 | 0.579606783 | -0.009825087 | 0.000002408 | 0.000002583 |
| subject | target | S3 | 47 | 0.033340000 | 0.416344816 | 0.407155064 | 0.009189752 | 0.000003912 | 0.000002436 |
| subject | component | e144_fine_tail_delta | 24 | 0.033340000 | 0.458098380 | 0.426477500 | 0.031620880 | -0.000001393 | -0.000001301 |

## Branch/Hard-Fail Anatomy

| prior | outcome | group_kind | group | cells | world_rate | conditional_support_rate | unconditional_support_rate | support_rate_lift | conditional_delta_per_all | delta_shift_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | branch_loss | component | inherited_e143_body | 161 | 0.023448000 | 0.451991032 | 0.484676099 | -0.032685068 | 0.000011780 | 0.000060141 |
| global | branch_loss | target | Q3 | 56 | 0.023448000 | 0.445855876 | 0.478379714 | -0.032523839 | 0.000011119 | 0.000020815 |
| global | branch_loss | target | Q1 | 38 | 0.023448000 | 0.464404999 | 0.497728421 | -0.033323422 | 0.000004129 | 0.000014472 |
| global | branch_loss | target | S3 | 47 | 0.023448000 | 0.403703623 | 0.434451404 | -0.030747781 | 0.000004047 | 0.000009541 |
| global | branch_loss | target | S4 | 21 | 0.023448000 | 0.473160469 | 0.508480381 | -0.035319912 | -0.000027866 | 0.000008477 |
| global | branch_loss | target | S2 | 23 | 0.023448000 | 0.502351179 | 0.533038783 | -0.030687604 | 0.000020133 | 0.000008066 |
| global | branch_loss | component | e144_fine_tail_delta | 24 | 0.023448000 | 0.429553338 | 0.459470333 | -0.029916995 | -0.000000219 | 0.000001231 |
| global | hard_fail | component | inherited_e143_body | 161 | 0.181524000 | 0.428711444 | 0.484676099 | -0.055964655 | 0.000054615 | 0.000102975 |
| global | hard_fail | target | Q3 | 56 | 0.181524000 | 0.422554908 | 0.478379714 | -0.055824806 | 0.000026031 | 0.000035728 |
| global | hard_fail | target | Q1 | 38 | 0.181524000 | 0.439057500 | 0.497728421 | -0.058670921 | 0.000015137 | 0.000025480 |
| global | hard_fail | target | S2 | 23 | 0.181524000 | 0.479313791 | 0.533038783 | -0.053724992 | 0.000026188 | 0.000014122 |
| global | hard_fail | target | S4 | 21 | 0.181524000 | 0.449683683 | 0.508480381 | -0.058796698 | -0.000022232 | 0.000014111 |
| global | hard_fail | target | S3 | 47 | 0.181524000 | 0.406199145 | 0.434451404 | -0.028252259 | 0.000008286 | 0.000013780 |
| global | hard_fail | component | e144_fine_tail_delta | 24 | 0.181524000 | 0.453485490 | 0.459470333 | -0.005984844 | -0.000001204 | 0.000000246 |
| nearest_hard085 | branch_loss | component | inherited_e143_body | 161 | 0.054456000 | 0.453405656 | 0.471735478 | -0.018329823 | 0.000009177 | 0.000033727 |
| nearest_hard085 | branch_loss | target | Q3 | 56 | 0.054456000 | 0.431670916 | 0.450033071 | -0.018362155 | 0.000020197 | 0.000011752 |
| nearest_hard085 | branch_loss | target | Q1 | 38 | 0.054456000 | 0.537780381 | 0.555394000 | -0.017613619 | -0.000027737 | 0.000007649 |
| nearest_hard085 | branch_loss | target | S3 | 47 | 0.054456000 | 0.303829912 | 0.313834809 | -0.010004896 | 0.000039896 | 0.000005121 |
| nearest_hard085 | branch_loss | target | S2 | 23 | 0.054456000 | 0.588096652 | 0.606195826 | -0.018099174 | -0.000002406 | 0.000004757 |
| nearest_hard085 | branch_loss | target | S4 | 21 | 0.054456000 | 0.431432629 | 0.450150857 | -0.018718228 | -0.000017851 | 0.000004492 |
| nearest_hard085 | branch_loss | component | e144_fine_tail_delta | 24 | 0.054456000 | 0.353217888 | 0.354305000 | -0.001087112 | 0.000002922 | 0.000000045 |
| nearest_hard085 | hard_fail | component | inherited_e143_body | 161 | 0.230396000 | 0.434694615 | 0.471735478 | -0.037040863 | 0.000043606 | 0.000068155 |
| nearest_hard085 | hard_fail | target | Q3 | 56 | 0.230396000 | 0.412955458 | 0.450033071 | -0.037077613 | 0.000032175 | 0.000023730 |
| nearest_hard085 | hard_fail | target | Q1 | 38 | 0.230396000 | 0.518229026 | 0.555394000 | -0.037164974 | -0.000019246 | 0.000016140 |
| nearest_hard085 | hard_fail | target | S2 | 23 | 0.230396000 | 0.567946907 | 0.606195826 | -0.038248919 | 0.000002891 | 0.000010054 |
| nearest_hard085 | hard_fail | target | S3 | 47 | 0.230396000 | 0.294157368 | 0.313834809 | -0.019677441 | 0.000044327 | 0.000009551 |
| nearest_hard085 | hard_fail | target | S4 | 21 | 0.230396000 | 0.413233861 | 0.450150857 | -0.036916996 | -0.000013484 | 0.000008860 |
| nearest_hard085 | hard_fail | component | e144_fine_tail_delta | 24 | 0.230396000 | 0.349935907 | 0.354305000 | -0.004369093 | 0.000003057 | 0.000000180 |
| subject | branch_loss | component | inherited_e143_body | 161 | 0.036668000 | 0.452895106 | 0.468985093 | -0.016089987 | 0.000010117 | 0.000029606 |
| subject | branch_loss | target | Q3 | 56 | 0.036668000 | 0.460062491 | 0.478443286 | -0.018380794 | 0.000002026 | 0.000011764 |
| subject | branch_loss | target | Q1 | 38 | 0.036668000 | 0.473046913 | 0.490983895 | -0.017936982 | 0.000000376 | 0.000007790 |
| subject | branch_loss | target | S3 | 47 | 0.036668000 | 0.382558623 | 0.407155064 | -0.024596441 | 0.000006582 | 0.000005106 |
| subject | branch_loss | target | S4 | 21 | 0.036668000 | 0.359270053 | 0.372600190 | -0.013330138 | -0.000000532 | 0.000003199 |
| subject | branch_loss | target | S2 | 23 | 0.036668000 | 0.567517703 | 0.579606783 | -0.012089080 | 0.000003003 | 0.000003178 |
| subject | branch_loss | component | e144_fine_tail_delta | 24 | 0.036668000 | 0.391708483 | 0.426477500 | -0.034769017 | 0.000001338 | 0.000001430 |
| subject | hard_fail | component | inherited_e143_body | 161 | 0.297164000 | 0.427713881 | 0.468985093 | -0.041271212 | 0.000056450 | 0.000075939 |

## Interpretation

- `global`: win-rate mass `0.745560`, non-win mass `0.254440`, fine-loss-alive `0.027696`, branch-or-worse `0.204972`.
- `subject`: win-rate mass `0.599760`, non-win mass `0.400240`, fine-loss-alive `0.033340`, branch-or-worse `0.333832`.
- `nearest_hard085`: win-rate mass `0.635616`, non-win mass `0.364384`, fine-loss-alive `0.031700`, branch-or-worse `0.284852`.
- A future E144 win should be credited to the groups with the most negative conditional LogLoss delta in this table, not to the whole branch by default.
- A fine loss should be read as a narrow support shortfall; E143 remains a contrast only if the shortfall concentrates in `e144_fine_tail_delta` or S3.
- A branch loss or hard fail should be read as a broad target/component failure only if the adverse shift is not isolated to the fine-tail component.

## Decision

No submission is created. E144 remains the next public sensor. After E144 public feedback, read the score through E145 bands and this E148 attribution table before creating any E143/E142 follow-up or closing the branch.
