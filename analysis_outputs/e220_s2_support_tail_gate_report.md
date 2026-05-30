# E220 S2 Support Tail Gate Audit

## Question

Can the E219 support/tail diagnosis be converted into a smaller S2 gate that reduces adverse capacity below the observed E216 miss while preserving expected signal?

## Gate Scan

| gate | n_cells | expected_focus | adverse_delta | adverse_over_observed | support_prob_focus_weighted | sim_prob_loss | sim_prob_ge_half_obs | sim_prob_ge_obs | tail_gate_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| focus_support_ge_0p7 | 7 | 0.000018940 | 0.000209735 | 0.210751520 | 0.791501438 | 0.687330000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p75 | 4 | 0.000021291 | 0.000174024 | 0.174866927 | 0.805925926 | 0.576090000 | 0.000000000 | 0.000000000 | False |
| subject_support_ge_0p7 | 12 | 0.000034403 | 0.000292689 | 0.294107283 | 0.689378813 | 0.680130000 | 0.000000000 | 0.000000000 | False |
| nearest_support_ge_0p7 | 15 | 0.000040511 | 0.000471950 | 0.474236773 | 0.649608776 | 0.638450000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p6_expected_neg | 61 | -0.000578857 | 0.001402108 | 1.408900104 | 0.652594384 | 0.004540000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p65_expected_neg | 61 | -0.000578857 | 0.001402108 | 1.408900104 | 0.652594384 | 0.004690000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p5_expected_neg | 62 | -0.000580054 | 0.001425290 | 1.432194852 | 0.651305629 | 0.004460000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p55_expected_neg | 62 | -0.000580054 | 0.001425290 | 1.432194852 | 0.651305629 | 0.004630000 | 0.000000000 | 0.000000000 | False |
| expected_neg_drop_top40 | 109 | -0.000819920 | 0.001663618 | 1.671677454 | 0.495321421 | 0.000990000 | 0.000000000 | 0.000000000 | False |
| expected_neg_drop_top20 | 119 | -0.001032755 | 0.001866077 | 1.875117238 | 0.478987569 | 0.000340000 | 0.000000000 | 0.000000000 | False |
| expected_neg_only | 128 | -0.001204825 | 0.002118163 | 2.128423852 | 0.470328248 | 0.000140000 | 0.000000000 | 0.000000000 | False |
| focus_support_ge_0p65 | 106 | -0.000195629 | 0.003286386 | 3.302306496 | 0.657501400 | 0.239370000 | 0.007830000 | 0.000030000 | False |
| focus_support_ge_0p6 | 110 | -0.000172972 | 0.003457596 | 3.474346324 | 0.655495539 | 0.271940000 | 0.011590000 | 0.000060000 | False |
| focus_support_ge_0p55 | 111 | -0.000174169 | 0.003480779 | 3.497641072 | 0.654762115 | 0.269860000 | 0.011360000 | 0.000050000 | False |
| subject_support_ge_0p6 | 115 | -0.000157509 | 0.003540550 | 3.557702087 | 0.651953735 | 0.291750000 | 0.013070000 | 0.000070000 | False |
| nearest_support_ge_0p6 | 114 | -0.000174057 | 0.003548601 | 3.565791749 | 0.650936641 | 0.275280000 | 0.012200000 | 0.000050000 | False |
| nearest_support_ge_0p5 | 114 | -0.000174057 | 0.003548601 | 3.565791749 | 0.650936641 | 0.274390000 | 0.012000000 | 0.000070000 | False |
| focus_support_ge_0p5 | 116 | -0.000158706 | 0.003563733 | 3.580996835 | 0.651264372 | 0.289240000 | 0.013920000 | 0.000090000 | False |
| subject_support_ge_0p5 | 117 | -0.000150385 | 0.003588350 | 3.605733110 | 0.648525255 | 0.297830000 | 0.014220000 | 0.000060000 | False |
| drop_top60_posterior_risk | 193 | -0.000020206 | 0.003835170 | 3.853749065 | 0.502814361 | 0.473130000 | 0.046240000 | 0.000400000 | False |
| drop_top40_posterior_risk | 210 | -0.000191464 | 0.004441050 | 4.462563817 | 0.496813302 | 0.301940000 | 0.028890000 | 0.000530000 | False |
| drop_top20_posterior_risk | 230 | -0.000275301 | 0.005223065 | 5.248366917 | 0.487215992 | 0.254610000 | 0.031730000 | 0.001110000 | False |
| drop_top10_posterior_risk | 240 | -0.000231673 | 0.005719099 | 5.746803906 | 0.484217843 | 0.303190000 | 0.050490000 | 0.002660000 | False |
| all_s2 | 250 | -0.000288312 | 0.006048480 | 6.077781421 | 0.473944871 | 0.272580000 | 0.047540000 | 0.002920000 | False |

## Diagnostic Rows

_empty_

## Decision

- No simple support/tail gate passes all criteria. E216 remains closed as a submission lane.
- The important stress rule is now explicit: expected delta alone is insufficient; S2 support probability and adverse capacity must be gated before any masked-family S2 JEPA movement is trusted.
