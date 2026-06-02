# H117 Forbidden Companion-Sector Inversion HS-JEPA

No candidate was promoted.

Core finding:

```text
The H116 forbidden companion sector is not practically invertible in the
current proposal space.  Only 4 of 2192 proposal cells
have positive forbidden-antipode gap, and none can pass H102/H112/H115 stress
as a submission candidate.
```

Forbidden axes:

| source_spec | bundle_id | targets | q2_rescue_marginal | full_curv_marginal | h088_cos | bad_weighted_pos | weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q2_conservation_balanced_b12_a032 | r140_minimum_companions_1 | Q2,S3,S2 | 0.000050772 | -0.000053340 | 0.245605480 | 0.014832701 | 2.980043126 |
| q2_conservation_balanced_b12_a032 | r140_q_stage_balanced_2 | Q2,Q3,S3,S2 | 0.000049817 | -0.000052385 | 0.242741435 | 0.014659734 | 2.943836311 |
| q2_conservation_balanced_b12_a032 | r129_minimum_companions_1 | Q2,S2,S1 | 0.000048776 | -0.000049885 | 0.243907651 | 0.014730165 | 2.882551524 |
| q2_conservation_balanced_b12_a032 | r129_top_companions_0 | Q2,S2,S1,S3 | 0.000048350 | -0.000049459 | 0.243609388 | 0.014712152 | 2.860368913 |
| q2_conservation_balanced_b12_a032 | r140_combo3_8 | Q2,S3,S2,S1 | 0.000048323 | -0.000050891 | 0.240191435 | 0.014505734 | 2.887292687 |
| q2_conservation_balanced_b12_a032 | r140_top_companions_0 | Q2,S3,S2,Q3,S1 | 0.000047496 | -0.000050065 | 0.237792996 | 0.014360886 | 2.856425358 |
| q2_conservation_balanced_b12_a032 | r128_combo2_2 | Q2,S2,S1 | 0.000035285 | -0.000034982 | 0.175500031 | 0.010598866 | 2.356592335 |
| q2_conservation_balanced_b12_a032 | r129_combo2_2 | Q2,S2,S3 | 0.000034733 | -0.000035843 | 0.168313413 | 0.010164848 | 2.352491104 |
| q2_conservation_balanced_b12_a032 | r138_combo2_3 | Q2,S3,S2 | 0.000034562 | -0.000036839 | 0.171814832 | 0.010376308 | 2.367082794 |
| q2_conservation_balanced_b12_a032 | r138_minimum_companions_1 | Q2,S3,S1 | 0.000033828 | -0.000036105 | 0.167295768 | 0.010103390 | 2.345830074 |
| q2_conservation_strict_b8_a035 | r138_minimum_companions_1 | Q2,S3,S1 | 0.000033805 | -0.000036027 | 0.166919419 | 0.010080662 | 2.344327658 |
| q2_conservation_antidote_b10_a030 | r138_combo2_3 | Q2,S3,S1 | 0.000033700 | -0.000036014 | 0.166919419 | 0.010080662 | 2.341552545 |
| q2_conservation_balanced_b12_a032 | r138_combo3_8 | Q2,S3,S1,S2 | 0.000033698 | -0.000035975 | 0.167277768 | 0.010102303 | 2.334689983 |
| q2_conservation_balanced_b12_a032 | r147_minimum_companions_1 | Q2,S2,S1 | 0.000033528 | -0.000035867 | 0.167405358 | 0.010110009 | 2.337067357 |
| q2_conservation_balanced_b12_a032 | r147_combo2_2 | Q2,S2,Q1 | 0.000033269 | -0.000035608 | 0.168512182 | 0.010176853 | 2.323063342 |
| q2_conservation_balanced_b12_a032 | r140_combo2_3 | Q2,S3,Q3 | 0.000033036 | -0.000035604 | 0.167574870 | 0.010120246 | 2.321620595 |
| q2_conservation_strict_b8_a035 | r140_minimum_companions_1 | Q2,S3,Q3 | 0.000032972 | -0.000035480 | 0.167207461 | 0.010098057 | 2.318527875 |
| q2_conservation_antidote_b10_a030 | r140_combo2_3 | Q2,S3,Q3 | 0.000032939 | -0.000035547 | 0.167207461 | 0.010098057 | 2.318509147 |
| q2_conservation_balanced_b12_a032 | r140_combo2_5 | Q2,S2,Q3 | 0.000032828 | -0.000035396 | 0.167574870 | 0.010120246 | 2.312230976 |
| q2_conservation_antidote_b10_a030 | r138_minimum_companions_1 | Q2,S3,S4 | 0.000032745 | -0.000035059 | 0.162315757 | 0.009802636 | 2.310402206 |

Positive antipode cells:

| row | subject_id | target | proposal_move | h117_forbidden_gap | h117_forbidden_opp | h117_forbidden_same | h112_residual_safety | h112_residual_toxicity | proposal_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38 | id02 | S3 | -0.075338011 | 0.001881808 | 0.001881808 | 0.000000000 | 0.619258349 | 0.361878000 | h114_selected::h114_null_novel_lowoverlap_c64_a058_73fe7866 |
| 38 | id02 | S3 | -0.017809738 | 0.000444855 | 0.000444855 | 0.000000000 | 0.619258349 | 0.361878000 | h114_selected::h114_null_q2_companion_micro_c26_a032_a7e5c28d |
| 137 | id06 | S1 | -0.044728926 | 0.000134916 | 0.000134916 | 0.000000000 | 0.646109709 | 0.369945429 | h114_selected::h114_null_h010_e216_antidote_c72_a060_4232eefa |
| 54 | id02 | S1 | 0.016331162 | 0.000016447 | 0.000016447 | 0.000000000 | 0.649342480 | 0.370293429 | h112_pool |
