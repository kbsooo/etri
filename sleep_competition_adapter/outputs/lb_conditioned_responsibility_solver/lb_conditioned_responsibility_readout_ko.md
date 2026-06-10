# LB-Conditioned Responsibility Solver

## Thesis

Public LB is treated as an external listener that emits scalar observations after seeing row-target action fields.  HS-JEPA can use these observations to estimate action responsibility, then invert only the actions that remain valid under target-route and subject-prior invariants.

## Anchor Fit

- Anchor count: `26`
- Candidate features: `115`
- LOO correlation: `0.7300`
- LOO MSE: `0.4829`
- Loss delta range: `0.000157` to `0.013480`

## Verdict

- Status: `candidate_ready`
- Recommended variant: `pure_lb_gradient_jackpot`
- Reason: Recommended by predicted public-listener improvement, LOO sign stability, invariant energy, and upload-safe validation.

## Generated Candidates

| Rank | Variant | Cells | Rows | Predicted loss delta | Sign stability | Energy delta | Bad cosine | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `pure_lb_gradient_jackpot` | `24` | `22` | `-7.11879` | `0.992` | `-0.03290` | `0.0551` | `True` | `submission_hsjepa_lb_responsibility_pure_lb_gradient_jackpot_f0a8129d_uploadsafe.csv` |
| 2 | `jackpot_public_equation_release` | `29` | `21` | `-3.85464` | `0.995` | `-0.02435` | `-0.0583` | `True` | `submission_hsjepa_lb_responsibility_jackpot_public_equation_release_6dd65162_uploadsafe.csv` |
| 3 | `stable_public_listener_inverse` | `13` | `10` | `-1.72587` | `0.997` | `-0.03576` | `-0.0052` | `True` | `submission_hsjepa_lb_responsibility_stable_public_listener_inverse_b3a3a98e_uploadsafe.csv` |
| 4 | `subject_safe_public_private_equation` | `12` | `11` | `-1.41804` | `0.997` | `-0.03055` | `-0.0054` | `True` | `submission_hsjepa_lb_responsibility_subject_safe_public_private_equation_bb70d5b8_uploadsafe.csv` |
| 5 | `route_invariant_responsibility_core` | `11` | `11` | `-0.91323` | `0.997` | `-0.03354` | `-0.0035` | `True` | `submission_hsjepa_lb_responsibility_route_invariant_responsibility_core_8572f8a4_uploadsafe.csv` |

## Public LB Sensor Interpretation

- If this beats H057, the paper claim strengthens: listener responsibility can be estimated from scalar outcome observations, not only from explicit labels.
- If it fails like listener transport, the bottleneck is not responsibility estimation but an unobserved public/private row-support assignment.
- If only the subject-safe variant survives, personal-coordinate invariance is the missing action-health constraint.
