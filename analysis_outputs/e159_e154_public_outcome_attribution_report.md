# E159 E154 Public Outcome Attribution

## Question

E158 says how to bucket the public score for `submission_e154_s3repair_9f2e2e73.csv`. This audit asks which target/component support pattern would make each bucket happen.

The decomposition is additive in LogLoss: E95 -> E144 inherited body, then E144 -> E154 adjustment/extra body. Duplicate segments on the same row-target share one simulated hidden label.

## Movement Anatomy

- unique E154-vs-E95 moved cells: `294`
- additive LogLoss segments: `479`
- moved rows: `139`
- moved subjects: `9`

### By Component

| component | segments | unique_cells | flip_benefit | abs_delta_prob |
| --- | --- | --- | --- | --- |
| inherited_e144_body | 185 | 185 | 3.292000000 | 0.627045979 |
| e154_extra_body | 109 | 109 | 0.255975083 | 0.059687290 |
| e154_adjustment_on_e144_body | 185 | 185 | 0.203843941 | 0.040502798 |

### By Target

| target | segments | unique_cells | flip_benefit | abs_delta_prob |
| --- | --- | --- | --- | --- |
| Q3 | 151 | 95 | 1.316339056 | 0.291482328 |
| Q1 | 108 | 70 | 0.861514603 | 0.172672127 |
| S3 | 103 | 56 | 0.617644085 | 0.110331970 |
| S2 | 62 | 39 | 0.502753066 | 0.077930386 |
| S4 | 55 | 34 | 0.453568213 | 0.074819256 |

## Outcome Rates

| prior | outcome | world_rate | mean_delta_vs_e95 | p05_delta | p50_delta | p95_delta | support_flip_share_mean | top20_support_rate | inherited_body_support_rate | e154_adjustment_support_rate | e154_extra_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | breakthrough_win | 0.639140000 | -0.000087823 | -0.000179049 | -0.000079243 | -0.000026119 | 0.501431983 | 0.508910020 | 0.501226310 | 0.489555222 | 0.480633236 |
| global | clean_win | 0.065635000 | -0.000013615 | -0.000019374 | -0.000013662 | -0.000007677 | 0.466818128 | 0.467890607 | 0.466260379 | 0.491988660 | 0.475607736 |
| global | micro_win | 0.023775000 | -0.000004496 | -0.000006726 | -0.000004499 | -0.000002264 | 0.462565019 | 0.462166141 | 0.462308239 | 0.492422770 | 0.475808179 |
| global | tie | 0.018165000 | -0.000000004 | -0.000001804 | 0.000000006 | 0.000001791 | 0.460469776 | 0.461271676 | 0.460015920 | 0.492607554 | 0.474516221 |
| global | small_loss | 0.030695000 | 0.000005464 | 0.000002355 | 0.000005390 | 0.000008695 | 0.457919088 | 0.457745561 | 0.457118203 | 0.493749752 | 0.474587948 |
| global | branch_loss | 0.025725000 | 0.000012161 | 0.000009369 | 0.000012133 | 0.000014988 | 0.454795459 | 0.453119534 | 0.454017283 | 0.492672498 | 0.474270023 |
| global | hard_fail | 0.196865000 | 0.000055101 | 0.000017856 | 0.000046666 | 0.000121183 | 0.434766544 | 0.429920250 | 0.433757390 | 0.494522176 | 0.472059626 |
| nearest_hard085 | breakthrough_win | 0.533985000 | -0.000063381 | -0.000126047 | -0.000056899 | -0.000023433 | 0.490031037 | 0.520474826 | 0.474853606 | 0.511740410 | 0.524726367 |
| nearest_hard085 | clean_win | 0.096945000 | -0.000013548 | -0.000019318 | -0.000013576 | -0.000007651 | 0.466787115 | 0.493787715 | 0.451498133 | 0.513691380 | 0.521918462 |
| nearest_hard085 | micro_win | 0.035750000 | -0.000004517 | -0.000006758 | -0.000004504 | -0.000002251 | 0.462574501 | 0.490328671 | 0.447108675 | 0.514581743 | 0.521380638 |
| nearest_hard085 | tie | 0.028060000 | -0.000000029 | -0.000001812 | -0.000000047 | 0.000001812 | 0.460481331 | 0.487722737 | 0.445024176 | 0.513658955 | 0.520545751 |
| nearest_hard085 | small_loss | 0.045650000 | 0.000005457 | 0.000002316 | 0.000005454 | 0.000008661 | 0.457922519 | 0.483313253 | 0.442311951 | 0.514221012 | 0.520757258 |
| nearest_hard085 | branch_loss | 0.036970000 | 0.000012143 | 0.000009342 | 0.000012156 | 0.000014990 | 0.454803580 | 0.479692994 | 0.439195403 | 0.514922253 | 0.520057175 |
| nearest_hard085 | hard_fail | 0.222640000 | 0.000045410 | 0.000017246 | 0.000039109 | 0.000095058 | 0.439286788 | 0.462357393 | 0.423470686 | 0.515792310 | 0.517881749 |
| subject | breakthrough_win | 0.493530000 | -0.000072497 | -0.000149336 | -0.000064291 | -0.000024067 | 0.494283243 | 0.464572569 | 0.488543811 | 0.488843144 | 0.510481502 |
| subject | clean_win | 0.078315000 | -0.000013527 | -0.000019360 | -0.000013501 | -0.000007674 | 0.466777207 | 0.434393156 | 0.461143235 | 0.489749470 | 0.505739875 |
| subject | micro_win | 0.029730000 | -0.000004490 | -0.000006741 | -0.000004485 | -0.000002284 | 0.462562042 | 0.431096535 | 0.456727666 | 0.489727366 | 0.505588523 |
| subject | tie | 0.022815000 | -0.000000007 | -0.000001810 | -0.000000015 | 0.000001814 | 0.460470784 | 0.427657243 | 0.454505393 | 0.490928799 | 0.506085044 |
| subject | small_loss | 0.039485000 | 0.000005515 | 0.000002341 | 0.000005486 | 0.000008703 | 0.457895427 | 0.425281753 | 0.452117636 | 0.489895239 | 0.505380629 |
| subject | branch_loss | 0.033840000 | 0.000012126 | 0.000009328 | 0.000012114 | 0.000014959 | 0.454811578 | 0.422724586 | 0.448870679 | 0.490658744 | 0.504072050 |
| subject | hard_fail | 0.302285000 | 0.000057330 | 0.000018174 | 0.000049520 | 0.000123179 | 0.433726710 | 0.398223531 | 0.427920581 | 0.490598947 | 0.501031516 |

## Top Responsibility Groups

| prior | outcome | rank | direction | group_kind | group | segments | unique_cells | world_rate | delta_shift_per_all | conditional_delta_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | branch_loss | 1 | blame_or_neutral | target | S2 | 62 | 39 | 0.025725000 | 0.000007077 | 0.000021120 |
| global | branch_loss | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.025725000 | 0.000022211 | 0.000013614 |
| global | branch_loss | 3 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.025725000 | 0.000056215 | 0.000006447 |
| global | clean_win | 1 | credit | target | S4 | 55 | 34 | 0.065635000 | 0.000004274 | -0.000034133 |
| global | clean_win | 2 | credit | component | inherited_e144_body | 185 | 185 | 0.065635000 | 0.000031242 | -0.000018526 |
| global | hard_fail | 1 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.196865000 | 0.000098497 | 0.000048728 |
| global | hard_fail | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.196865000 | 0.000036717 | 0.000028120 |
| global | hard_fail | 3 | blame_or_neutral | target | S2 | 62 | 39 | 0.196865000 | 0.000012788 | 0.000026831 |
| global | micro_win | 1 | credit | target | S4 | 55 | 34 | 0.023775000 | 0.000005548 | -0.000032859 |
| global | micro_win | 2 | credit | component | inherited_e144_body | 185 | 185 | 0.023775000 | 0.000040325 | -0.000009444 |
| global | small_loss | 1 | blame_or_neutral | target | S2 | 62 | 39 | 0.030695000 | 0.000006552 | 0.000020595 |
| global | small_loss | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.030695000 | 0.000018954 | 0.000010357 |
| global | small_loss | 3 | blame_or_neutral | component | e154_extra_body | 109 | 109 | 0.030695000 | 0.000001080 | 0.000004717 |
| global | tie | 1 | blame_or_neutral | target | S2 | 62 | 39 | 0.018165000 | 0.000006694 | 0.000020737 |
| global | tie | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.018165000 | 0.000017000 | 0.000008403 |
| global | tie | 3 | blame_or_neutral | component | e154_extra_body | 109 | 109 | 0.018165000 | 0.000001092 | 0.000004728 |
| nearest_hard085 | branch_loss | 1 | blame_or_neutral | target | S3 | 103 | 56 | 0.036970000 | 0.000005267 | 0.000038782 |
| nearest_hard085 | branch_loss | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.036970000 | 0.000013084 | 0.000026653 |
| nearest_hard085 | branch_loss | 3 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.036970000 | 0.000035695 | 0.000013953 |
| nearest_hard085 | clean_win | 1 | credit | target | Q1 | 108 | 70 | 0.096945000 | 0.000002154 | -0.000034576 |
| nearest_hard085 | clean_win | 2 | credit | target | S4 | 55 | 34 | 0.096945000 | 0.000001287 | -0.000023582 |
| nearest_hard085 | clean_win | 3 | credit | component | inherited_e144_body | 185 | 185 | 0.096945000 | 0.000010713 | -0.000011029 |
| nearest_hard085 | hard_fail | 1 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.222640000 | 0.000068313 | 0.000046571 |
| nearest_hard085 | hard_fail | 2 | blame_or_neutral | target | S3 | 103 | 56 | 0.222640000 | 0.000009166 | 0.000042681 |
| nearest_hard085 | hard_fail | 3 | blame_or_neutral | target | Q3 | 151 | 95 | 0.222640000 | 0.000025527 | 0.000039097 |
| nearest_hard085 | micro_win | 1 | credit | target | Q1 | 108 | 70 | 0.035750000 | 0.000004377 | -0.000032353 |
| nearest_hard085 | micro_win | 2 | credit | target | S4 | 55 | 34 | 0.035750000 | 0.000002488 | -0.000022380 |
| nearest_hard085 | micro_win | 3 | credit | target | S2 | 62 | 39 | 0.035750000 | 0.000002481 | -0.000007516 |
| nearest_hard085 | small_loss | 1 | blame_or_neutral | target | S3 | 103 | 56 | 0.045650000 | 0.000004558 | 0.000038073 |
| nearest_hard085 | small_loss | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.045650000 | 0.000011212 | 0.000024782 |
| nearest_hard085 | small_loss | 3 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.045650000 | 0.000029238 | 0.000007496 |
| nearest_hard085 | tie | 1 | blame_or_neutral | target | S3 | 103 | 56 | 0.028060000 | 0.000004004 | 0.000037519 |
| nearest_hard085 | tie | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.028060000 | 0.000009247 | 0.000022817 |
| subject | branch_loss | 1 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.033840000 | 0.000030391 | 0.000010656 |
| subject | branch_loss | 2 | blame_or_neutral | target | S3 | 103 | 56 | 0.033840000 | 0.000003838 | 0.000006051 |
| subject | branch_loss | 3 | blame_or_neutral | target | S2 | 62 | 39 | 0.033840000 | 0.000003099 | 0.000003195 |
| subject | clean_win | 1 | credit | component | inherited_e144_body | 185 | 185 | 0.078315000 | 0.000005198 | -0.000014537 |
| subject | clean_win | 2 | credit | target | Q3 | 151 | 95 | 0.078315000 | 0.000002304 | -0.000007030 |
| subject | clean_win | 3 | credit | target | Q1 | 108 | 70 | 0.078315000 | 0.000001459 | -0.000005485 |
| subject | hard_fail | 1 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.302285000 | 0.000073965 | 0.000054230 |
| subject | hard_fail | 2 | blame_or_neutral | target | Q3 | 151 | 95 | 0.302285000 | 0.000030392 | 0.000021058 |
| subject | hard_fail | 3 | blame_or_neutral | target | Q1 | 108 | 70 | 0.302285000 | 0.000020585 | 0.000013641 |
| subject | micro_win | 1 | credit | component | inherited_e144_body | 185 | 185 | 0.029730000 | 0.000014095 | -0.000005640 |
| subject | micro_win | 2 | credit | target | S4 | 55 | 34 | 0.029730000 | 0.000001528 | -0.000003517 |
| subject | micro_win | 3 | credit | target | Q1 | 108 | 70 | 0.029730000 | 0.000003735 | -0.000003208 |
| subject | small_loss | 1 | blame_or_neutral | target | S3 | 103 | 56 | 0.039485000 | 0.000003223 | 0.000005436 |
| subject | small_loss | 2 | blame_or_neutral | component | inherited_e144_body | 185 | 185 | 0.039485000 | 0.000023753 | 0.000004018 |
| subject | small_loss | 3 | blame_or_neutral | target | S2 | 62 | 39 | 0.039485000 | 0.000002360 | 0.000002456 |
| subject | tie | 1 | blame_or_neutral | target | S3 | 103 | 56 | 0.022815000 | 0.000002320 | 0.000004533 |
| subject | tie | 2 | blame_or_neutral | target | S2 | 62 | 39 | 0.022815000 | 0.000002374 | 0.000002470 |

## Small-Loss Anatomy

| prior | group_kind | group | segments | unique_cells | world_rate | conditional_support_rate | unconditional_support_rate | support_rate_lift | conditional_delta_per_all | delta_shift_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | component | inherited_e144_body | 185 | 185 | 0.030695000 | 0.457118203 | 0.481406838 | -0.024288635 | 0.000000406 | 0.000050175 |
| global | target | Q3 | 151 | 95 | 0.030695000 | 0.479858984 | 0.491346258 | -0.011487274 | 0.000010357 | 0.000018954 |
| global | target | Q1 | 108 | 70 | 0.030695000 | 0.487158603 | 0.498743241 | -0.011584637 | 0.000004049 | 0.000012774 |
| global | target | S3 | 103 | 56 | 0.030695000 | 0.452711219 | 0.460662330 | -0.007951111 | 0.000002795 | 0.000006913 |
| global | target | S2 | 62 | 39 | 0.030695000 | 0.467910083 | 0.470703629 | -0.002793546 | 0.000020595 | 0.000006552 |
| global | target | S4 | 55 | 34 | 0.030695000 | 0.489620756 | 0.496672000 | -0.007051244 | -0.000032333 | 0.000006074 |
| global | component | e154_extra_body | 109 | 109 | 0.030695000 | 0.474587948 | 0.478040459 | -0.003452511 | 0.000004717 | 0.000001080 |
| global | component | e154_adjustment_on_e144_body | 185 | 185 | 0.030695000 | 0.493749752 | 0.491025324 | 0.002724428 | 0.000000341 | 0.000000013 |
| nearest_hard085 | component | inherited_e144_body | 185 | 185 | 0.045650000 | 0.442311951 | 0.456516811 | -0.014204860 | 0.000007496 | 0.000029238 |
| nearest_hard085 | target | Q3 | 151 | 95 | 0.045650000 | 0.490690758 | 0.497655033 | -0.006964275 | 0.000024782 | 0.000011212 |
| nearest_hard085 | target | Q1 | 108 | 70 | 0.045650000 | 0.546143158 | 0.551774028 | -0.005630869 | -0.000030119 | 0.000006611 |
| nearest_hard085 | target | S3 | 103 | 56 | 0.045650000 | 0.416548453 | 0.421914854 | -0.005366401 | 0.000038073 | 0.000004558 |
| nearest_hard085 | target | S4 | 55 | 34 | 0.045650000 | 0.475688539 | 0.480817636 | -0.005129097 | -0.000020880 | 0.000003989 |
| nearest_hard085 | target | S2 | 62 | 39 | 0.045650000 | 0.509290535 | 0.511229597 | -0.001939062 | -0.000006399 | 0.000003599 |
| nearest_hard085 | component | e154_extra_body | 109 | 109 | 0.045650000 | 0.520757258 | 0.522339541 | -0.001582284 | 0.000001010 | 0.000000633 |
| nearest_hard085 | component | e154_adjustment_on_e144_body | 185 | 185 | 0.045650000 | 0.514221012 | 0.513217946 | 0.001003066 | -0.000003050 | 0.000000097 |
| subject | component | inherited_e144_body | 185 | 185 | 0.039485000 | 0.452117636 | 0.463569135 | -0.011451499 | 0.000004018 | 0.000023753 |
| subject | target | Q3 | 151 | 95 | 0.039485000 | 0.488682516 | 0.494829801 | -0.006147285 | 0.000000236 | 0.000009570 |
| subject | target | Q1 | 108 | 70 | 0.039485000 | 0.496912799 | 0.502780046 | -0.005867248 | -0.000000590 | 0.000006354 |
| subject | target | S3 | 103 | 56 | 0.039485000 | 0.466892306 | 0.470846456 | -0.003954150 | 0.000005436 | 0.000003223 |
| subject | target | S4 | 55 | 34 | 0.039485000 | 0.443715105 | 0.447459091 | -0.003743986 | -0.000002024 | 0.000003021 |
| subject | target | S2 | 62 | 39 | 0.039485000 | 0.474306290 | 0.474702984 | -0.000396694 | 0.000002456 | 0.000002360 |
| subject | component | e154_extra_body | 109 | 109 | 0.039485000 | 0.505380629 | 0.506589495 | -0.001208867 | 0.000000669 | 0.000000601 |
| subject | component | e154_adjustment_on_e144_body | 185 | 185 | 0.039485000 | 0.489895239 | 0.489621730 | 0.000273509 | 0.000000828 | 0.000000175 |

## Branch/Hard-Fail Anatomy

| prior | outcome | group_kind | group | segments | unique_cells | world_rate | conditional_support_rate | unconditional_support_rate | support_rate_lift | conditional_delta_per_all | delta_shift_per_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | branch_loss | component | inherited_e144_body | 185 | 185 | 0.025725000 | 0.454017283 | 0.481406838 | -0.027389555 | 0.000006447 | 0.000056215 |
| global | branch_loss | target | Q3 | 151 | 95 | 0.025725000 | 0.477031002 | 0.491346258 | -0.014315257 | 0.000013614 | 0.000022211 |
| global | branch_loss | target | Q1 | 108 | 70 | 0.025725000 | 0.485267970 | 0.498743241 | -0.013475271 | 0.000005249 | 0.000013974 |
| global | branch_loss | target | S4 | 55 | 34 | 0.025725000 | 0.486647230 | 0.496672000 | -0.010024770 | -0.000030344 | 0.000008063 |
| global | branch_loss | target | S2 | 62 | 39 | 0.025725000 | 0.468108718 | 0.470703629 | -0.002594911 | 0.000021120 | 0.000007077 |
| global | branch_loss | target | S3 | 103 | 56 | 0.025725000 | 0.452466812 | 0.460662330 | -0.008195518 | 0.000002522 | 0.000006641 |
| global | branch_loss | component | e154_extra_body | 109 | 109 | 0.025725000 | 0.474270023 | 0.478040459 | -0.003770436 | 0.000005139 | 0.000001503 |
| global | branch_loss | component | e154_adjustment_on_e144_body | 185 | 185 | 0.025725000 | 0.492672498 | 0.491025324 | 0.001647173 | 0.000000575 | 0.000000246 |
| global | hard_fail | component | inherited_e144_body | 185 | 185 | 0.196865000 | 0.433757390 | 0.481406838 | -0.047649448 | 0.000048728 | 0.000098497 |
| global | hard_fail | target | Q3 | 151 | 95 | 0.196865000 | 0.468512813 | 0.491346258 | -0.022833446 | 0.000028120 | 0.000036717 |
| global | hard_fail | target | Q1 | 108 | 70 | 0.196865000 | 0.476295327 | 0.498743241 | -0.022447913 | 0.000016359 | 0.000025083 |
| global | hard_fail | target | S4 | 55 | 34 | 0.196865000 | 0.478958123 | 0.496672000 | -0.017713877 | -0.000024946 | 0.000013460 |
| global | hard_fail | target | S3 | 103 | 56 | 0.196865000 | 0.445257321 | 0.460662330 | -0.015405009 | 0.000008738 | 0.000012856 |
| global | hard_fail | target | S2 | 62 | 39 | 0.196865000 | 0.464462711 | 0.470703629 | -0.006240918 | 0.000026831 | 0.000012788 |
| global | hard_fail | component | e154_extra_body | 109 | 109 | 0.196865000 | 0.472059626 | 0.478040459 | -0.005980832 | 0.000005734 | 0.000002098 |
| global | hard_fail | component | e154_adjustment_on_e144_body | 185 | 185 | 0.196865000 | 0.494522176 | 0.491025324 | 0.003496851 | 0.000000638 | 0.000000310 |
| nearest_hard085 | branch_loss | component | inherited_e144_body | 185 | 185 | 0.036970000 | 0.439195403 | 0.456516811 | -0.017321408 | 0.000013953 | 0.000035695 |
| nearest_hard085 | branch_loss | target | Q3 | 151 | 95 | 0.036970000 | 0.489930085 | 0.497655033 | -0.007724948 | 0.000026653 | 0.000013084 |
| nearest_hard085 | branch_loss | target | Q1 | 108 | 70 | 0.036970000 | 0.544202507 | 0.551774028 | -0.007571521 | -0.000028258 | 0.000008472 |
| nearest_hard085 | branch_loss | target | S3 | 103 | 56 | 0.036970000 | 0.415535031 | 0.421914854 | -0.006379823 | 0.000038782 | 0.000005267 |
| nearest_hard085 | branch_loss | target | S4 | 55 | 34 | 0.036970000 | 0.473969066 | 0.480817636 | -0.006848571 | -0.000019780 | 0.000005089 |
| nearest_hard085 | branch_loss | target | S2 | 62 | 39 | 0.036970000 | 0.509294807 | 0.511229597 | -0.001934789 | -0.000005254 | 0.000004744 |
| nearest_hard085 | branch_loss | component | e154_extra_body | 109 | 109 | 0.036970000 | 0.520057175 | 0.522339541 | -0.002282366 | 0.000001198 | 0.000000820 |
| nearest_hard085 | branch_loss | component | e154_adjustment_on_e144_body | 185 | 185 | 0.036970000 | 0.514922253 | 0.513217946 | 0.001704307 | -0.000003007 | 0.000000140 |
| nearest_hard085 | hard_fail | component | inherited_e144_body | 185 | 185 | 0.222640000 | 0.423470686 | 0.456516811 | -0.033046125 | 0.000046571 | 0.000068313 |
| nearest_hard085 | hard_fail | target | Q3 | 151 | 95 | 0.222640000 | 0.481658241 | 0.497655033 | -0.015996792 | 0.000039097 | 0.000025527 |
| nearest_hard085 | hard_fail | target | Q1 | 108 | 70 | 0.222640000 | 0.536464156 | 0.551774028 | -0.015309872 | -0.000019966 | 0.000016764 |
| nearest_hard085 | hard_fail | target | S2 | 62 | 39 | 0.222640000 | 0.506742767 | 0.511229597 | -0.004486830 | -0.000000524 | 0.000009474 |
| nearest_hard085 | hard_fail | target | S3 | 103 | 56 | 0.222640000 | 0.411136529 | 0.421914854 | -0.010778325 | 0.000042681 | 0.000009166 |
| nearest_hard085 | hard_fail | target | S4 | 55 | 34 | 0.222640000 | 0.468711413 | 0.480817636 | -0.012106223 | -0.000015878 | 0.000008990 |
| nearest_hard085 | hard_fail | component | e154_extra_body | 109 | 109 | 0.222640000 | 0.517881749 | 0.522339541 | -0.004457792 | 0.000001798 | 0.000001421 |
| nearest_hard085 | hard_fail | component | e154_adjustment_on_e144_body | 185 | 185 | 0.222640000 | 0.515792310 | 0.513217946 | 0.002574365 | -0.000002959 | 0.000000188 |
| subject | branch_loss | component | inherited_e144_body | 185 | 185 | 0.033840000 | 0.448870679 | 0.463569135 | -0.014698456 | 0.000010656 | 0.000030391 |
| subject | branch_loss | target | Q3 | 151 | 95 | 0.033840000 | 0.487794138 | 0.494829801 | -0.007035663 | 0.000002632 | 0.000011966 |
| subject | branch_loss | target | Q1 | 108 | 70 | 0.033840000 | 0.494457852 | 0.502780046 | -0.008322195 | 0.000001875 | 0.000008819 |
| subject | branch_loss | target | S3 | 103 | 56 | 0.033840000 | 0.466108357 | 0.470846456 | -0.004738099 | 0.000006051 | 0.000003838 |
| subject | branch_loss | target | S4 | 55 | 34 | 0.033840000 | 0.442375887 | 0.447459091 | -0.005083204 | -0.000001627 | 0.000003419 |
| subject | branch_loss | target | S2 | 62 | 39 | 0.033840000 | 0.473525795 | 0.474702984 | -0.001177189 | 0.000003195 | 0.000003099 |
| subject | branch_loss | component | e154_extra_body | 109 | 109 | 0.033840000 | 0.504072050 | 0.506589495 | -0.002517446 | 0.000000809 | 0.000000741 |
| subject | branch_loss | component | e154_adjustment_on_e144_body | 185 | 185 | 0.033840000 | 0.490658744 | 0.489621730 | 0.001037014 | 0.000000661 | 0.000000008 |
| subject | hard_fail | component | inherited_e144_body | 185 | 185 | 0.302285000 | 0.427920581 | 0.463569135 | -0.035648554 | 0.000054230 | 0.000073965 |
| subject | hard_fail | target | Q3 | 151 | 95 | 0.302285000 | 0.475825465 | 0.494829801 | -0.019004336 | 0.000021058 | 0.000030392 |

## Interpretation

- `global`: win mass `0.728550`, tie `0.018165`, small-loss `0.030695`, branch-or-worse `0.222590`.
- `subject`: win mass `0.601575`, tie `0.022815`, small-loss `0.039485`, branch-or-worse `0.336125`.
- `nearest_hard085`: win mass `0.666680`, tie `0.028060`, small-loss `0.045650`, branch-or-worse `0.259610`.
- If E154 wins, credit only the groups with negative conditional contribution in this table; do not infer that every repaired sibling is validated.
- If E154 ties or small-loses and blame concentrates in `e154_adjustment_on_e144_body` or `e154_extra_body`, E155 is the clean amplitude-control follow-up.
- If E154 branch-loss/hard-fails with blame dominated by `inherited_e144_body`, E155 is not a rescue; use E144 as the unrepaired contrast or leave this branch.
- If target blame is broad Q3/S3/S2 rather than component-local, the bottleneck is hidden public target-prior allocation, not S3 repair exactness.

## Decision

After E154 public feedback, combine E158 score band with this E159 target/component attribution. E155 is justified only when the score says the branch is not dead and the attribution blames E154's added body rather than the inherited E144 branch.
