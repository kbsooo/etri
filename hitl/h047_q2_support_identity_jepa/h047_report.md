# H047 Q2 Support-Identity Posterior HS-JEPA

Question: after rejecting Q2 amplitude bifurcation, can we infer the hidden Q2 support identity directly?

- support observations: `720`
- generated candidates: `262`
- scored candidates: `240`
- promotable candidates: `74`

Top row support posterior:

| row | h047_support_posterior | h047_direct_support_contrast | h047_feature_support_prior | h047_h042_support | h047_h043_support | h047_h045_support | h047_public_score | h047_private_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 164 | 0.988240000 | 0.025368648 | 1.122400000 | True | True | True | 0.657160000 | 0.383120000 |
| 0 | 0.982480000 | 0.025368648 | 1.119280000 | True | True | True | 0.704860000 | 0.263080000 |
| 168 | 0.980080000 | 0.013997567 | 1.105000000 | True | True | True | 0.575740000 | 0.399640000 |
| 70 | 0.971680000 | 0.013997567 | 1.105680000 | True | True | True | 0.862360000 | 0.126400000 |
| 146 | 0.964480000 | 0.072032862 | 0.996240000 | True | True | True | 0.793100000 | 0.304920000 |
| 136 | 0.954760000 | 0.025368648 | 0.844360000 | True | True | True | 0.349580000 | 0.497960000 |
| 56 | 0.950920000 | 0.013997567 | 0.894960000 | True | True | True | 0.526640000 | 0.503520000 |
| 10 | 0.839200000 | 0.000000000 | 1.186280000 | True | True | True | 0.753080000 | 0.256320000 |
| 226 | 0.837040000 | 0.000000000 | 1.131720000 | True | True | True | 0.726020000 | 0.275240000 |
| 148 | 0.835840000 | 0.000000000 | 1.115560000 | True | True | True | 0.822820000 | 0.199320000 |
| 44 | 0.831280000 | 0.000000000 | 1.095200000 | True | True | True | 0.791900000 | 0.285000000 |
| 152 | 0.827560000 | 0.000000000 | 1.069960000 | True | True | True | 0.632180000 | 0.224120000 |
| 150 | 0.825520000 | 0.000000000 | 1.059880000 | True | True | True | 0.812300000 | 0.294600000 |
| 48 | 0.820240000 | 0.000000000 | 1.066920000 | True | True | True | 0.825840000 | 0.292000000 |
| 216 | 0.818080000 | 0.000000000 | 1.056280000 | True | True | True | 0.527080000 | 0.414800000 |
| 139 | 0.661120000 | -0.029289199 | 1.006560000 | True | True | True | 0.665460000 | 0.447000000 |
| 163 | 0.658600000 | -0.047021335 | 1.035120000 | True | True | True | 0.827860000 | 0.097640000 |
| 110 | 0.658600000 | -0.029289199 | 0.897400000 | True | True | True | 0.389780000 | 0.490760000 |
| 149 | 0.644440000 | -0.083070720 | 0.942200000 | True | True | True | 0.663400000 | 0.466320000 |
| 167 | 0.641320000 | -0.029289199 | 0.970360000 | True | True | True | 0.745740000 | 0.173240000 |

Top H047 candidates:

| candidate_id | changed_cells_vs_h012 | full_known_cond_margin_vs_h012_median | full_known_cond_support_better_than_h012 | pre_h042_cond_margin_vs_h012_median | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | h025_score | h045_jaccard | h047_beats_h045_axes | h047_promotable | h047_support_identity_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h047_h042core_support_tail14_a0.66_0.44_c59_98737e9b | 59 | -0.000211862 | 0.583333333 | -0.000383048 | -0.000178002 | 0.000552020 | -1.154530177 | 0.740259740 | 2 | True | 0.677875000 |
| h047_support_top55_a0.78_c55_b7181c0a | 55 | -0.000190999 | 0.583333333 | -0.000587344 | -0.000188434 | 0.000621626 | -1.108974351 | 0.733333333 | 2 | True | 0.681041667 |
| h047_support_top55_a0.66_c55_07e99aa0 | 55 | -0.000210952 | 0.583333333 | -0.000516472 | -0.000167662 | 0.000525926 | -1.092897005 | 0.733333333 | 2 | True | 0.683458333 |
| h047_support_top55_a0.92_c55_74596baa | 55 | -0.000166968 | 0.583333333 | -0.000669702 | -0.000208950 | 0.000732978 | -1.093907101 | 0.733333333 | 2 | True | 0.710708333 |
| h047_h043_support_sieve_q0.45_a0.66_c58_ee9f1cd9 | 58 | -0.000202953 | 0.583333333 | -0.000533293 | -0.000173988 | 0.000545017 | -1.141429706 | 0.750000000 | 3 | True | 0.716083333 |
| h047_h042core_support_tail14_a0.78_0.44_c59_30499909 | 59 | -0.000187104 | 0.583333333 | -0.000421022 | -0.000199873 | 0.000649955 | -1.156323105 | 0.740259740 | 2 | True | 0.754041667 |
| h047_h043_support_sieve_q0.45_a0.78_c58_1be8b0aa | 58 | -0.000181046 | 0.583333333 | -0.000606066 | -0.000195596 | 0.000644238 | -1.150994111 | 0.750000000 | 2 | True | 0.757083333 |
| h047_h042core_support_tail14_a0.66_0.32_c59_67b48af5 | 59 | -0.000214278 | 0.583333333 | -0.000325237 | -0.000177220 | 0.000548164 | -1.146572566 | 0.740259740 | 2 | True | 0.759625000 |
| h047_h043_support_sieve_q0.35_a0.78_c68_4ab6cba0 | 68 | -0.000165948 | 0.583333333 | -0.000705863 | -0.000198780 | 0.000658710 | -1.481354227 | 0.881578947 | 2 | True | 0.776833333 |
| h047_support_top65_a0.78_c65_39862122 | 65 | -0.000166146 | 0.583333333 | -0.000688521 | -0.000198456 | 0.000654299 | -1.425788863 | 0.842105263 | 2 | True | 0.786208333 |
| h047_support_top65_a0.66_c65_43573727 | 65 | -0.000187890 | 0.583333333 | -0.000614436 | -0.000176571 | 0.000553441 | -1.420555797 | 0.842105263 | 2 | True | 0.787791667 |
| h047_h042core_support_tail14_a0.78_0.32_c59_243b5529 | 59 | -0.000188733 | 0.583333333 | -0.000370784 | -0.000199092 | 0.000646340 | -1.148365494 | 0.740259740 | 2 | True | 0.788291667 |
| h047_h043_support_sieve_q0.35_a0.66_c68_fb0e0fa1 | 68 | -0.000186556 | 0.583333333 | -0.000630191 | -0.000176876 | 0.000557133 | -1.476121161 | 0.881578947 | 2 | True | 0.790083333 |
| h047_h042core_support_tail8_a0.66_0.44_c53_692895e7 | 53 | -0.000205753 | 0.583333333 | -0.000375577 | -0.000176281 | 0.000551439 | -0.978958472 | 0.662337662 | 2 | True | 0.791041667 |
| h047_support_top65_a0.58_c65_04eb52ca | 65 | -0.000202167 | 0.583333333 | -0.000564952 | -0.000160251 | 0.000486061 | -1.411846590 | 0.842105263 | 2 | True | 0.794125000 |
| h047_h042core_support_tail14_a0.58_0.44_c59_1a537766 | 59 | -0.000211303 | 0.583333333 | -0.000364150 | -0.000161751 | 0.000486710 | -1.148894019 | 0.740259740 | 2 | True | 0.798291667 |
| h047_h042core_support_tail8_a0.58_0.44_c53_32f47fb7 | 53 | -0.000221233 | 0.583333333 | -0.000350957 | -0.000160031 | 0.000485998 | -0.973322314 | 0.662337662 | 2 | True | 0.801375000 |
| h047_h043_support_sieve_q0.45_a0.92_c58_8cb85279 | 58 | -0.000155458 | 0.583333333 | -0.000690953 | -0.000216968 | 0.000759696 | -1.134042221 | 0.750000000 | 2 | True | 0.806750000 |
| h047_h042core_support_tail14_a0.92_0.44_c59_09f4bc57 | 59 | -0.000157247 | 0.583333333 | -0.000474934 | -0.000221615 | 0.000764089 | -1.140319435 | 0.740259740 | 2 | True | 0.815541667 |
| h047_h042core_support_tail14_a0.66_0.22_c59_0f459641 | 59 | -0.000216639 | 0.583333333 | -0.000275529 | -0.000176472 | 0.000545328 | -1.142709397 | 0.740259740 | 3 | True | 0.817125000 |

Decision:

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | root_uploadsafe_path | reason | expected_relation | changed_cells_vs_h012 | full_known_cond_margin_vs_h012_median | full_known_cond_support_better_than_h012 | pre_h042_cond_margin_vs_h012_median | pre_h042_cond_support_better_than_h012 | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | h025_score | h045_jaccard | support_score_mean | h047_beats_h045_axes | h047_support_identity_score | h047_promotable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote | True | h047_h042core_support_tail14_a0.66_0.44_c59_98737e9b | submission_h047_h042core_support_tail14_a0.66_0.44_c59_98737e9b.csv | /Users/kbsoo/Downloads/cl2/hitl/h047_q2_support_identity_jepa/submission_h047_h042core_support_tail14_a0.66_0.44_c59_98737e9b.csv | /Users/kbsoo/Downloads/cl2/submission_h047_q2_support_identity_98737e9b_uploadsafe.csv | support identity posterior gate passed | beats H045 if Q2 support identity is the missing hidden state | 59 | -0.000211862 | 0.583333333 | -0.000383048 | 0.583333333 | -0.000178002 | 0.000552020 | -1.154530177 | 0.740259740 | 0.634773559 | 2 | 0.677875000 | True |

Interpretation:

- If promoted, support identity is the next hidden-state variable after H046 killed amplitude bifurcation.
- If not promoted, current evidence says H045's route-pruned support is still a stronger next public sensor than a new contrastive support posterior.
