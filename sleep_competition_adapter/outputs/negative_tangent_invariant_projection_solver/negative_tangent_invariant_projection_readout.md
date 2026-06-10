# Negative Tangent Invariant Projection Solver

## Thesis

A low-rank negative public representation is not enough.  HS-JEPA needs an action projector that releases only corrections that remain plausible under the target-route and subject-prior invariant manifold.

## Verdict

- Status: `candidate_ready`
- Recommended variant: `subject_prior_safe_projection`
- Reason: Recommended by joint anti-public-bad direction, invariant energy, subject-prior safety, and upload-safe validation.

## Generated Candidates

| Rank | Variant | Cells | Rows | Bad cosine | Energy delta | Subject delta | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `subject_prior_safe_projection` | `18` | `17` | `-0.2259` | `-0.01685` | `-0.00106` | `True` | `submission_hsjepa_negative_tangent_invariant_subject_prior_safe_projection_ebdccca6_uploadsafe.csv` |
| 2 | `anti_tangent_invariant_projection` | `28` | `26` | `-0.1495` | `-0.01957` | `0.00189` | `True` | `submission_hsjepa_negative_tangent_invariant_anti_tangent_invariant_projection_19dced9c_uploadsafe.csv` |
| 3 | `sign_equation_projection` | `23` | `23` | `-0.0691` | `-0.01867` | `0.00108` | `True` | `submission_hsjepa_negative_tangent_invariant_sign_equation_projection_59cd4b86_uploadsafe.csv` |
| 4 | `energy_descent_negative_space` | `21` | `19` | `-0.0115` | `-0.02954` | `0.00049` | `True` | `submission_hsjepa_negative_tangent_invariant_energy_descent_negative_space_5d8eaf60_uploadsafe.csv` |

## Public LB Sensor Interpretation

- If the recommended candidate improves materially, HS-JEPA needs a negative-representation plus invariant-action projection head.
- If it fails near the previous negative sensors, the public-bad mode is diagnostic but its inverse is not label-valid.
- If the subject-prior variant wins, personal-coordinate safety is more important than global target-route safety.
