# E214 JEPA Benefit Gate Translation

## Purpose

Test whether the real Q3/S4 JEPA axes need a learned sample-level benefit gate before being translated into public probability movement.

## Gate Audit

| target | benefit_rate | gate_auc | gate_prob_mean | gate_prob_benefit_mean | gate_prob_harm_mean | margin_keep_rate | hard60_keep_rate | toward_benefit_rate | closer_benefit_rate | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | 0.502222222 | 0.552168932 | 0.301865572 | 0.313166232 | 0.290464014 | 0.057777778 | 0.000000000 | 0.450909091 | 0.433962264 | 450 |
| S4 | 0.533333333 | 0.568968254 | 0.289222957 | 0.305105247 | 0.271071767 | 0.084444444 | 0.031111111 | 0.480349345 | 0.474654378 | 450 |

## OOF / Subject / Geometry Summary

| policy_id | q3_mode | s4_mode | delta | delta_vs_raw | delta_vs_e211_toward | subject_half_delta | subject_half_win_rate | keep_abs_share | geometry_delta | geometry_win_rate | geometry_vs_raw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_q3raw_s4toward | raw | toward_binary | -0.001317984 | -0.000045261 | 0.000000000 | -0.001327501 | 0.965384615 | 0.752038019 | -0.000610954 | 0.875000000 | 0.000296568 |
| baseline_q3raw_s4closer | raw | closer_binary | -0.001315064 | -0.000042340 | 0.000002920 | -0.001320045 | 0.961538462 | 0.736585543 | -0.000629592 | 0.875000000 | 0.000277930 |
| baseline_raw_raw | raw | raw | -0.001272724 | 0.000000000 | 0.000045261 | -0.001297106 | 0.900000000 | 1.000000000 | -0.000907522 | 0.875000000 | 0.000000000 |
| q3raw_s4benefit_rank | raw | rank | -0.000917538 | 0.000355186 | 0.000400446 | -0.000924625 | 0.930769231 | 0.675134736 | -0.000986804 | 0.875000000 | -0.000079281 |
| q3raw_s4benefit_prob | raw | prob | -0.000916042 | 0.000356682 | 0.000401942 | -0.000918015 | 0.923076923 | 0.602262988 | -0.000941985 | 0.875000000 | -0.000034462 |
| q3raw_s4benefit_toward | raw | toward_prob | -0.000888103 | 0.000384621 | 0.000429882 | -0.000885214 | 0.942307692 | 0.536010474 | -0.000703076 | 0.875000000 | 0.000204446 |
| q3raw_s4benefit_closer | raw | closer_prob | -0.000886956 | 0.000385768 | 0.000431028 | -0.000882714 | 0.923076923 | 0.532131991 | -0.000725133 | 0.875000000 | 0.000182390 |
| q3raw_s4benefit_toward_rank | raw | toward_rank | -0.000885365 | 0.000387358 | 0.000432619 | -0.000882997 | 0.946153846 | 0.561512097 | -0.000719001 | 0.875000000 | 0.000188522 |
| q3raw_s4benefit_closer_rank | raw | closer_rank | -0.000885089 | 0.000387634 | 0.000432895 | -0.000880195 | 0.923076923 | 0.554858061 | -0.000771045 | 0.875000000 | 0.000136477 |
| q3raw_s4benefit_margin | raw | margin | -0.000826033 | 0.000446691 | 0.000491951 | -0.000821143 | 0.930769231 | 0.491091578 | -0.000876469 | 0.875000000 | 0.000031054 |
| q3benefit_rank_s4benefit_rank | rank | rank | -0.000289193 | 0.000983531 | 0.001028792 | -0.000308710 | 0.834615385 | 0.332127097 | -0.000770545 | 0.875000000 | 0.000136977 |
| q3benefit_rank_s4benefit_toward_rank | rank | toward_rank | -0.000257020 | 0.001015704 | 0.001060965 | -0.000267082 | 0.880769231 | 0.218504458 | -0.000502742 | 0.875000000 | 0.000404780 |
| q3benefit_prob_s4benefit_prob | prob | prob | -0.000239354 | 0.001033370 | 0.001078631 | -0.000251057 | 0.896153846 | 0.213261997 | -0.000721698 | 0.875000000 | 0.000185824 |
| q3benefit_prob_s4benefit_toward | prob | toward_prob | -0.000211414 | 0.001061310 | 0.001106570 | -0.000218255 | 0.965384615 | 0.147009483 | -0.000482790 | 0.875000000 | 0.000424733 |
| q3benefit_margin_s4benefit_margin | margin | margin | -0.000001928 | 0.001270796 | 0.001316057 | -0.000002046 | 0.657692308 | 0.003799245 | -0.000582201 | 0.750000000 | 0.000325321 |

## Target Deltas

| policy_id | target | delta | moved_abs_logit |
| --- | --- | --- | --- |
| baseline_q3raw_s4closer | Q1 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4closer | Q2 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4closer | Q3 | -0.005775312 | 0.116868497 |
| baseline_q3raw_s4closer | S1 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4closer | S2 | -0.000000000 | 0.000000000 |
| baseline_q3raw_s4closer | S3 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4closer | S4 | -0.003430136 | 0.059674029 |
| baseline_q3raw_s4toward | Q1 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4toward | Q2 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4toward | Q3 | -0.005775312 | 0.116868497 |
| baseline_q3raw_s4toward | S1 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4toward | S2 | -0.000000000 | 0.000000000 |
| baseline_q3raw_s4toward | S3 | 0.000000000 | 0.000000000 |
| baseline_q3raw_s4toward | S4 | -0.003450578 | 0.063377630 |
| baseline_raw_raw | Q1 | 0.000000000 | 0.000000000 |
| baseline_raw_raw | Q2 | 0.000000000 | 0.000000000 |
| baseline_raw_raw | Q3 | -0.005775312 | 0.116868497 |
| baseline_raw_raw | S1 | 0.000000000 | 0.000000000 |
| baseline_raw_raw | S2 | -0.000000000 | 0.000000000 |
| baseline_raw_raw | S3 | 0.000000000 | 0.000000000 |
| baseline_raw_raw | S4 | -0.003133755 | 0.122808384 |
| q3benefit_margin_s4benefit_margin | Q1 | 0.000000000 | 0.000000000 |
| q3benefit_margin_s4benefit_margin | Q2 | 0.000000000 | 0.000000000 |
| q3benefit_margin_s4benefit_margin | Q3 | -0.000006575 | 0.000075790 |
| q3benefit_margin_s4benefit_margin | S1 | 0.000000000 | 0.000000000 |
| q3benefit_margin_s4benefit_margin | S2 | -0.000000000 | 0.000000000 |
| q3benefit_margin_s4benefit_margin | S3 | 0.000000000 | 0.000000000 |
| q3benefit_margin_s4benefit_margin | S4 | -0.000006919 | 0.000834801 |
| q3benefit_prob_s4benefit_prob | Q1 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_prob | Q2 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_prob | Q3 | -0.001038493 | 0.023633953 |
| q3benefit_prob_s4benefit_prob | S1 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_prob | S2 | -0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_prob | S3 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_prob | S4 | -0.000636984 | 0.027480018 |
| q3benefit_prob_s4benefit_toward | Q1 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_toward | Q2 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_toward | Q3 | -0.001038493 | 0.023633953 |
| q3benefit_prob_s4benefit_toward | S1 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_toward | S2 | -0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_toward | S3 | 0.000000000 | 0.000000000 |
| q3benefit_prob_s4benefit_toward | S4 | -0.000441408 | 0.011600822 |
| q3benefit_rank_s4benefit_rank | Q1 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_rank | Q2 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_rank | Q3 | -0.001376893 | 0.034657496 |
| q3benefit_rank_s4benefit_rank | S1 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_rank | S2 | -0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_rank | S3 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_rank | S4 | -0.000647456 | 0.044945691 |
| q3benefit_rank_s4benefit_toward_rank | Q1 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_toward_rank | Q2 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_toward_rank | Q3 | -0.001376893 | 0.034657496 |
| q3benefit_rank_s4benefit_toward_rank | S1 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_toward_rank | S2 | -0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_toward_rank | S3 | 0.000000000 | 0.000000000 |
| q3benefit_rank_s4benefit_toward_rank | S4 | -0.000422246 | 0.017712971 |
| q3raw_s4benefit_closer | Q1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer | Q2 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer | Q3 | -0.005775312 | 0.116868497 |
| q3raw_s4benefit_closer | S1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer | S2 | -0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer | S3 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer | S4 | -0.000433380 | 0.010671239 |
| q3raw_s4benefit_closer_rank | Q1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer_rank | Q2 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer_rank | Q3 | -0.005775312 | 0.116868497 |
| q3raw_s4benefit_closer_rank | S1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer_rank | S2 | -0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer_rank | S3 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_closer_rank | S4 | -0.000420314 | 0.016118153 |
| q3raw_s4benefit_margin | Q1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | Q2 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | Q3 | -0.005775312 | 0.116868497 |
| q3raw_s4benefit_margin | S1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | S2 | -0.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | S3 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | S4 | -0.000006919 | 0.000834801 |
| q3raw_s4benefit_prob | Q1 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_prob | Q2 | 0.000000000 | 0.000000000 |
| q3raw_s4benefit_prob | Q3 | -0.005775312 | 0.116868497 |

## Geometry Fold Aggregate

| policy_id | q3_mode | s4_mode | delta_mean | geometry_win_rate | ungated_delta_mean | keep_abs_share | geometry_vs_raw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3raw_s4benefit_rank | raw | rank | -0.000986804 | 0.875000000 | -0.000907522 | 0.733294613 | -0.000079281 |
| q3raw_s4benefit_prob | raw | prob | -0.000941985 | 0.875000000 | -0.000907522 | 0.744972276 | -0.000034462 |
| baseline_raw_raw | raw | raw | -0.000907522 | 0.875000000 | -0.000907522 | 1.000000000 | 0.000000000 |
| q3raw_s4benefit_margin | raw | margin | -0.000876469 | 0.875000000 | -0.000907522 | 0.625201244 | 0.000031054 |
| q3raw_s4benefit_closer_rank | raw | closer_rank | -0.000771045 | 0.875000000 | -0.000907522 | 0.593787513 | 0.000136477 |
| q3benefit_rank_s4benefit_rank | rank | rank | -0.000770545 | 0.875000000 | -0.000907522 | 0.525399873 | 0.000136977 |
| q3raw_s4benefit_closer | raw | closer_prob | -0.000725133 | 0.875000000 | -0.000907522 | 0.611767650 | 0.000182390 |
| q3benefit_prob_s4benefit_prob | prob | prob | -0.000721698 | 0.875000000 | -0.000907522 | 0.528691289 | 0.000185824 |
| q3raw_s4benefit_toward_rank | raw | toward_rank | -0.000719001 | 0.875000000 | -0.000907522 | 0.607497042 | 0.000188522 |
| q3raw_s4benefit_toward | raw | toward_prob | -0.000703076 | 0.875000000 | -0.000907522 | 0.625281161 | 0.000204446 |
| baseline_q3raw_s4closer | raw | closer_binary | -0.000629592 | 0.875000000 | -0.000907522 | 0.764168849 | 0.000277930 |
| baseline_q3raw_s4toward | raw | toward_binary | -0.000610954 | 0.875000000 | -0.000907522 | 0.790668600 | 0.000296568 |
| q3benefit_margin_s4benefit_margin | margin | margin | -0.000582201 | 0.750000000 | -0.000907522 | 0.318552522 | 0.000325321 |
| q3benefit_rank_s4benefit_toward_rank | rank | toward_rank | -0.000502742 | 0.875000000 | -0.000907522 | 0.399602302 | 0.000404780 |
| q3benefit_prob_s4benefit_toward | prob | toward_prob | -0.000482790 | 0.875000000 | -0.000907522 | 0.409000173 | 0.000424733 |

## Frontier Stress

| policy_id | delta | geometry_delta | anchor | anchor_scale | frontier_keep_abs_share | bad_span_energy | max_bad_cos | vs_e95_expected_delta_focus_mean | vs_e95_top1_over_abs_expected | e214_frontier_gate | survival_score | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e154 | 1.000000000 | 0.750553434 | 0.341820158 | 0.172838781 | -0.001082243 | 0.290769387 | False | 0.051340832 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e95 | 1.000000000 | 0.750553434 | 0.335091202 | 0.158077638 | -0.001060092 | 0.296845243 | False | 0.050344017 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e154 | 1.000000000 | 0.733808559 | 0.342757394 | 0.170465727 | -0.001054137 | 0.298521984 | False | 0.050110428 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e95 | 1.000000000 | 0.737362414 | 0.336099331 | 0.156092210 | -0.001053564 | 0.298684428 | False | 0.050084629 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e154 | 0.750000000 | 0.750553434 | 0.343865602 | 0.177377597 | -0.000912685 | 0.258591338 | False | 0.043710706 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e154 | 0.750000000 | 0.740644573 | 0.344704029 | 0.176540593 | -0.000903082 | 0.261340941 | False | 0.043312951 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e95 | 0.750000000 | 0.750553434 | 0.335091202 | 0.158077638 | -0.000888588 | 0.265603690 | False | 0.042626373 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e95 | 0.750000000 | 0.740644573 | 0.336016411 | 0.157218229 | -0.000879174 | 0.268447870 | False | 0.042237076 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e154 | 0.500000000 | 0.743136435 | 0.348575732 | 0.184276224 | -0.000685115 | 0.229657247 | False | 0.033504415 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e154 | 0.500000000 | 0.750553434 | 0.347624067 | 0.185846211 | -0.000680355 | 0.231263944 | False | 0.033255868 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e95 | 0.500000000 | 0.750553434 | 0.335091202 | 0.158077638 | -0.000654330 | 0.240462280 | False | 0.032084723 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e95 | 0.500000000 | 0.740644573 | 0.336016411 | 0.157218229 | -0.000647387 | 0.243040999 | False | 0.031806664 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e154 | 0.750000000 | 0.647153104 | 0.359947239 | 0.181177713 | -0.000567666 | 0.415758952 | False | 0.027929295 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e154 | 0.750000000 | 0.640807163 | 0.360444174 | 0.180160266 | -0.000565168 | 0.417596806 | False | 0.027859340 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e95 | 0.750000000 | 0.647224204 | 0.352011079 | 0.160051038 | -0.000543106 | 0.434560417 | False | 0.026832015 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e95 | 0.750000000 | 0.640873357 | 0.352576017 | 0.159001379 | -0.000540689 | 0.436503039 | False | 0.026765649 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e154 | 1.000000000 | 0.623203893 | 0.360882442 | 0.176054475 | -0.000524258 | 0.600245385 | False | 0.025924839 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e154 | 1.000000000 | 0.614245799 | 0.361070463 | 0.173907691 | -0.000518087 | 0.607393989 | False | 0.025686387 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e154 | 0.500000000 | 0.663883475 | 0.360220410 | 0.188440577 | -0.000501868 | 0.313512114 | False | 0.025011045 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e95 | 1.000000000 | 0.615422492 | 0.355203034 | 0.157531621 | -0.000502245 | 0.626553679 | False | 0.024969746 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e95 | 1.000000000 | 0.623252271 | 0.354785239 | 0.159479948 | -0.000501073 | 0.628018654 | False | 0.024873744 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e154 | 0.500000000 | 0.669635722 | 0.359493675 | 0.189764783 | -0.000498675 | 0.315519076 | False | 0.024825152 |  |
| q3raw_s4benefit_toward | -0.000888103 | -0.000703076 | e95 | 0.500000000 | 0.669717212 | 0.348181053 | 0.160173320 | -0.000472556 | 0.332958750 | False | 0.023659266 |  |
| q3raw_s4benefit_closer | -0.000886956 | -0.000725133 | e95 | 0.500000000 | 0.662719475 | 0.348856703 | 0.159143517 | -0.000469860 | 0.334868865 | False | 0.023580935 |  |
| q3raw_s4benefit_closer_rank | -0.000885089 | -0.000771045 | e154 | 0.750000000 | 0.605830271 | 0.362242777 | 0.177899838 | -0.000429439 | 0.549583503 | False | 0.021814883 |  |
| q3raw_s4benefit_toward_rank | -0.000885365 | -0.000719001 | e154 | 0.750000000 | 0.611926054 | 0.361319332 | 0.179159607 | -0.000426611 | 0.553226044 | False | 0.021582934 |  |
| q3raw_s4benefit_closer_rank | -0.000885089 | -0.000771045 | e154 | 0.500000000 | 0.627704345 | 0.361570875 | 0.186947994 | -0.000408364 | 0.385297223 | False | 0.020891997 |  |
| q3raw_s4benefit_closer_rank | -0.000885089 | -0.000771045 | e95 | 0.750000000 | 0.606041597 | 0.354901589 | 0.156331760 | -0.000404385 | 0.583632938 | False | 0.020677785 |  |
| q3raw_s4benefit_toward_rank | -0.000885365 | -0.000719001 | e154 | 0.500000000 | 0.633482925 | 0.360623027 | 0.188199513 | -0.000405526 | 0.387993692 | False | 0.020661420 |  |
| q3raw_s4benefit_toward_rank | -0.000885365 | -0.000719001 | e95 | 0.750000000 | 0.612113764 | 0.353925210 | 0.157655990 | -0.000401586 | 0.587700654 | False | 0.020446963 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e154 | 0.250000000 | 0.744767375 | 0.357787916 | 0.205051304 | -0.000387001 | 0.203282980 | False | 0.020076471 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e154 | 0.250000000 | 0.750553434 | 0.356087952 | 0.206289193 | -0.000385838 | 0.203896086 | False | 0.019990210 |  |
| q3raw_s4benefit_closer_rank | -0.000885089 | -0.000771045 | e95 | 0.500000000 | 0.627418918 | 0.351289650 | 0.156866026 | -0.000380446 | 0.413570963 | False | 0.019645978 |  |
| q3raw_s4benefit_toward_rank | -0.000885365 | -0.000719001 | e95 | 0.500000000 | 0.633586315 | 0.350307463 | 0.158128904 | -0.000379412 | 0.414699016 | False | 0.019496578 |  |
| baseline_raw_raw | -0.001272724 | -0.000907522 | e154 | 0.750000000 | 1.000000000 | 0.299792654 | 0.173716753 | -0.000363060 | 0.650065196 | False | 0.019450416 |  |
| baseline_q3raw_s4closer | -0.001315064 | -0.000629592 | e95 | 0.250000000 | 0.744767375 | 0.337412061 | 0.156620626 | -0.000359062 | 0.219100701 | False | 0.018832050 |  |
| baseline_q3raw_s4toward | -0.001317984 | -0.000610954 | e95 | 0.250000000 | 0.750553434 | 0.335091202 | 0.158077638 | -0.000357899 | 0.219813100 | False | 0.018745327 |  |
| baseline_raw_raw | -0.001272724 | -0.000907522 | e95 | 0.750000000 | 1.000000000 | 0.292165174 | 0.155737509 | -0.000338204 | 0.697839989 | False | 0.018308035 |  |
| baseline_raw_raw | -0.001272724 | -0.000907522 | e154 | 0.500000000 | 1.000000000 | 0.303490158 | 0.181787950 | -0.000329155 | 0.478016143 | False | 0.017999761 |  |
| baseline_raw_raw | -0.001272724 | -0.000907522 | e154 | 1.000000000 | 1.000000000 | 0.297903494 | 0.169442818 | -0.000319063 | 0.986273740 | False | 0.017302454 |  |

## Selected Submissions

_empty_

## Decision

- No benefit-gated JEPA translation beat the E214 gate. This weakens the idea that a simple supervised benefit classifier fixes the E211 public-tail translation problem.
