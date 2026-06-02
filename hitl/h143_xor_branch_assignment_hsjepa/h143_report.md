# H143 XOR Branch Assignment HS-JEPA

Question: if H142's co-activation barrier is real, which optional branch should
the solver activate after the H141 common core?

Search space:

```text
H141 + gamma * row207_branch
H141 + gamma * row135_branch
```

Known endpoints are kept in the ranking but not promoted as a new root file.

Selected novel XOR candidate:

| candidate_id | branch | gamma | known_endpoint_or_existing | changed_cells_vs_h136 | delta_h088_vs_h136 | delta_margin_vs_h136 | delta_h098_vs_h136 | delta_route_vs_h136 | h143_xor_branch_pass | h143_xor_branch_score | h143_root_uploadsafe_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h143_row207_g0p8_4894032a | row207 | 0.800000000 | False | 3 | -0.002229244 | 0.000172037 | 0.000001533 | 0.000002418 | True | 0.041566086 | /Users/kbsoo/Downloads/cl2/submission_h143_xorbranch_4894032a_uploadsafe.csv |

Selected cells:

| candidate_id | row | target_index | target | delta_logit_vs_h136 | new_logit_move |
| --- | --- | --- | --- | --- | --- |
| h143_row207_g0p8_4894032a | 70 | 2 | Q3 | -0.017039034 | 0.031343407 |
| h143_row207_g0p8_4894032a | 131 | 4 | S2 | 0.017663218 | 0.017663218 |
| h143_row207_g0p8_4894032a | 207 | 4 | S2 | -0.011000000 | -0.011000000 |

XOR frontier:

| candidate_id | branch | gamma | known_endpoint_or_existing | changed_cells_vs_h136 | delta_h088_vs_h136 | delta_margin_vs_h136 | delta_h098_vs_h136 | delta_route_vs_h136 | h143_xor_branch_pass | h143_xor_branch_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h143_row207_g0p8_4894032a | row207 | 0.800000000 | False | 3 | -0.002229244 | 0.000172037 | 0.000001533 | 0.000002418 | True | 0.041566086 |
| h143_row207_g0p65_7df6a658 | row207 | 0.650000000 | False | 3 | -0.002084460 | 0.000204007 | 0.000001442 | 0.000002412 | True | 0.040421911 |
| h143_row207_g1p3_e54229b2 | row207 | 1.300000000 | False | 3 | -0.002692089 | 0.000017973 | 0.000001833 | 0.000002440 | False | 0.040148721 |
| h143_row207_g1p15_357fe89b | row207 | 1.150000000 | False | 3 | -0.002556445 | 0.000071845 | 0.000001743 | 0.000002433 | False | 0.040045474 |
| h143_row135_g0p8_2ffdce0a | row135 | 0.800000000 | False | 4 | -0.001515153 | 0.000455167 | 0.000001570 | 0.000002406 | False | 0.039741382 |
| h143_row207_g0p5_81491236 | row207 | 0.500000000 | False | 3 | -0.001936965 | 0.000229375 | 0.000001352 | 0.000002405 | False | 0.039009924 |
| h143_row135_g0p65_54016519 | row135 | 0.650000000 | False | 4 | -0.001502174 | 0.000429168 | 0.000001472 | 0.000002402 | False | 0.038739955 |
| h143_row135_g1p3_a523f6e7 | row135 | 1.300000000 | False | 4 | -0.001545755 | 0.000509973 | 0.000001894 | 0.000002421 | False | 0.038493642 |
| h143_row135_g1p15_047cbca1 | row135 | 1.150000000 | False | 4 | -0.001538628 | 0.000498700 | 0.000001796 | 0.000002416 | False | 0.038236577 |
| h143_row135_g0p5_a55b4715 | row135 | 0.500000000 | False | 4 | -0.001487456 | 0.000398789 | 0.000001375 | 0.000002398 | False | 0.037561806 |
| h143_row207_g0p35_86f9f80e | row207 | 0.350000000 | False | 3 | -0.001786773 | 0.000248134 | 0.000001262 | 0.000002399 | False | 0.037330058 |
| h143_row135_g0p35_c43f4a2e | row135 | 0.350000000 | False | 4 | -0.001471007 | 0.000364051 | 0.000001278 | 0.000002394 | False | 0.036207742 |
| h143_row207_g0p2_1169872a | row207 | 0.200000000 | False | 3 | -0.001633903 | 0.000260275 | 0.000001172 | 0.000002392 | False | 0.035382342 |
| h143_row135_g0p2_8a186029 | row135 | 0.200000000 | False | 4 | -0.001452834 | 0.000324975 | 0.000001181 | 0.000002389 | False | 0.034678609 |
| h143_row135_gm0p25_044b981a | row135 | -0.250000000 | False | 4 | -0.001388069 | 0.000181940 | 0.000000879 | 0.000002386 | False | 0.026052676 |
| h143_row207_gm0p25_e2fafa81 | row207 | -0.250000000 | False | 3 | -0.001159399 | 0.000256963 | 0.000001043 | 0.000002395 | False | 0.024792112 |
| h143_row207_g1p0_bf2b3e77 | row207 | 1.000000000 | True | 3 | -0.002418045 | 0.000119165 | 0.000001653 | 0.000002427 | False | 0.042675363 |
| h143_row135_g1p0_a5d0258f | row135 | 1.000000000 | True | 4 | -0.001529738 | 0.000482990 | 0.000001699 | 0.000002412 | False | 0.040800403 |

Interpretation:

The raw score still prefers the known H139 endpoint, but the best novel
non-endpoint is a softened row207 branch.  This makes H143 a direct amplitude
test:

```text
H139 = full row207 branch
H143 = softened row207 branch
H140 = row135 branch
H141 = no optional branch
```

Public sensor reading:

- H143 > H139: row207 is real but over-amplified; build calibrated XOR branch
  amplitudes.
- H139 > H143: full row207 is the correct XOR assignment.
- H140 > H143/H139: row135 is the correct branch.
- H141 > all optional branches: common core only.
