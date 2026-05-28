# E57 Mixmin-Hard Raw Posterior Safety Stress

## Observe

E56 generated a posterior candidate because mixmin-hard/raw-prior worlds agree internally. The selected file was `analysis_outputs/submission_mixhard_rawposterior_af1502f9.csv`.

## Wonder

Is the E56 posterior a real public-subset hypothesis, or did the generated world family create an overconfident self-consistent label prior?

## Method

- Reconstructed all E56 posterior variants from the saved mixmin-hard labels.
- Scored each variant with the independent actual-anchor/public-shape proxy used by previous raw05/JEPa frontier searches.
- Required three gates for a public candidate: E56 world-LOO strict pass, actual-anchor score better than mixmin, and mean abs logit movement vs mixmin <= 0.08.

## Safety Scores

| candidate | actual_anchor_score_final | anchor_delta_vs_mixmin | world_loo_strict_gate | world_loo_median_delta | mean_abs_logit_move_vs_mixmin | movement_guard | joint_candidate_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin | 0.577734 | 0 | False |  | 0 | True | False |
| a2c8 | 0.577827 | 9.25805e-05 | False |  | 0.0456142 | True | False |
| posterior_all_w0.05 | 0.577857 | 0.000122931 | True | -0.00470969 | 0.0286317 | True | False |
| raw05 | 0.577906 | 0.000171507 | False |  | 0.0490298 | True | False |
| posterior_raw_energy_half_w0.05 | 0.578026 | 0.00029172 | True | -0.0104133 | 0.0444813 | True | False |
| posterior_all_w0.10 | 0.578252 | 0.000517073 | True | -0.00915513 | 0.0572635 | True | False |
| posterior_raw_energy_quarter_w0.05 | 0.578357 | 0.00062288 | True | -0.0303963 | 0.0680998 | True | False |
| posterior_raw_energy_half_w0.10 | 0.578929 | 0.00119487 | True | -0.0202348 | 0.0889627 | False | False |
| posterior_all_w0.18 | 0.579458 | 0.00172352 | True | -0.0157166 | 0.103074 | False | False |
| posterior_raw_energy_quarter_w0.10 | 0.580275 | 0.00254098 | True | -0.0595652 | 0.1362 | False | False |
| posterior_raw_energy_half_w0.18 | 0.581659 | 0.00392437 | True | -0.0347101 | 0.160133 | False | False |
| posterior_all_w0.28 | 0.58198 | 0.00424514 | True | -0.0229634 | 0.160338 | False | False |
| posterior_raw_energy_quarter_w0.18 | 0.586082 | 0.00834703 | True | -0.103658 | 0.245159 | False | False |
| posterior_raw_energy_half_w0.28 | 0.587304 | 0.00956941 | True | -0.0506513 | 0.249096 | False | False |
| posterior_raw_energy_quarter_w0.28 | 0.598116 | 0.0203811 | True | -0.154291 | 0.381359 | False | False |

## Decision

- joint candidate gates: `0`.
- best actual-anchor posterior: `posterior_all_w0.05` with anchor delta `0.000123` versus mixmin.
- Do not submit the E56 posterior files. The world-internal signal is strong but independent anchor geometry says the movement is public-risk adverse.

## Interpretation

E56 is still useful: mixmin-hard raw worlds are coherent enough to expose a hidden binary-world direction. E57 says that direction is not yet calibrated to public anchors. The next version should use the E56 posterior as an energy axis or teacher, then constrain it by public-anchor geometry before producing a submission.

## Outputs

- `analysis_outputs/mixmin_hard_raw_posterior_safety_stress_scores.csv`
