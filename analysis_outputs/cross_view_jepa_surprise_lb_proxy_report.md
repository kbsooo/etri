# Cross-View JEPA Surprise Local LB Proxy Audit

This audits the new cross-view JEPA surprise submissions with the existing public-anchor ranker and LOOCV local LB proxy.

## Proxy Resolution

- Best independent LOOCV proxy model: `loocv_ridge_abs_axes_a1`.
- MAE/RMSE: `0.0003184931` / `0.0004029881`.
- Candidate gaps materially below this are not locally resolvable.

## CVJEPA Candidates

```csv
file,actual_anchor_score_final,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,ordinal_axis_ratio,mean_abs_move_vs_raw05,available_raw05_relative_lb_proxy_mean,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,independent_lb_proxy_mean,independent_lb_proxy_model_spread
submission_cvjepa_surprise_full_nonq2_w020.csv,0.5783845254,0.5786423899,0.5783424525,0.0008161453,0.018048883,0.0330960981,0.0117541453,0.5777849699,0.0002586627,0.0001244613,0.5781360542,0.0004612443
submission_cvjepa_surprise_q_targets.csv,0.5787230977,0.5792566252,0.5787119912,0.001185684,0.0319912898,0.0483191107,0.0135014166,0.5778935508,0.0003672436,0.0001847623,0.5782446351,0.0005805576
submission_cvjepa_surprise_q1_s2.csv,0.5789535411,0.5794949104,0.5788048267,0.0012785195,0.0319622408,0.010303807,0.0135099451,0.5779337041,0.0004073969,0.0002968763,0.5782847884,0.0006892204
submission_cvjepa_surprise_full_nonq2_w030.csv,0.5789021661,0.5792922908,0.5788353267,0.0013090195,0.0270733245,0.0496441471,0.0157102687,0.5779416736,0.0004153664,0.0002464498,0.578292758,0.000642245
submission_cvjepa_surprise_s_targets.csv,0.5793425218,0.5793399546,0.5791824164,0.0016561092,0.0086186969,0.02614711,0.0161622292,0.5779874877,0.0004611805,0.0005540405,0.578338572,0.0009463846
submission_cvjepa_surprise_core_q1_q3_s2_s4.csv,0.5795249304,0.5799284131,0.5795189815,0.0019926743,0.0563117042,0.0690924445,0.0187748263,0.5781496076,0.0006233004,0.0005213784,0.578500692,0.0009137225
submission_cvjepa_surprise_full_nonq2.csv,0.5800643293,0.5806516041,0.5799494319,0.0024231247,0.0406099867,0.0744662207,0.0222094247,0.5782543353,0.0007280281,0.0008285982,0.5786054197,0.0012209424
```

## Movement Summary

```csv
file,mean_target_abs_move_vs_stage2,max_target_abs_move_vs_stage2,mean_target_abs_move_vs_raw05,max_target_abs_move_vs_raw05
submission_cvjepa_surprise_full_nonq2_w020.csv,0.0093811409,0.013750619,0.0117541453,0.0158710875
submission_cvjepa_surprise_q_targets.csv,0.0082160121,0.0309388928,0.0135014166,0.0307586931
submission_cvjepa_surprise_q1_s2.csv,0.0083365794,0.0309388928,0.0135099451,0.0307586931
submission_cvjepa_surprise_full_nonq2_w030.csv,0.0140717113,0.0206259285,0.0157102687,0.0211131429
submission_cvjepa_surprise_s_targets.csv,0.0128915549,0.0274171631,0.0161622292,0.0284928163
submission_cvjepa_surprise_core_q1_q3_s2_s4.csv,0.0155167383,0.0309388928,0.0187748263,0.0307586931
submission_cvjepa_surprise_full_nonq2.csv,0.0211075669,0.0309388928,0.0222094247,0.0307586931
```

## Known Controls

```csv
file,actual_anchor_score_final,known_public,available_raw05_relative_lb_proxy_mean,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5779059944,0.5775263072,0.5775263072,0.0,0.0
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,0.5779449757,0.5776262549,9.99477e-05,0.0001672532
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5799865296,0.5783033652,0.5780705286,0.0005442214,0.000569107
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5813157907,0.5784273528,0.5785096132,0.000983306,0.0009317985
submission_jepa_latent_q2_w0p45.csv,0.5801455759,0.5798012862,0.5791915481,0.0016652409,0.0009891107
submission_jepa_latent_residual_probe.csv,0.5802891189,0.5812273278,0.5801998569,0.0026735497,0.0020526906
```

## Read

- These candidates are locally strong on OOF/subject-half/geometry, but their submission-space movement is much closer to stage2 than raw05.
- The proxy therefore treats them as stage2-family structural probes, not raw05-compatible LB-safe replacements.
- Use the proxy ranking as a risk screen; public LB is still needed to know whether this new JEPA signal transfers.
