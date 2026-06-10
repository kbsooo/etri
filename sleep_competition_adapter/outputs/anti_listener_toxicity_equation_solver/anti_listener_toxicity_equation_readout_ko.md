# Anti-Listener Toxicity Equation Solver

## Thesis

Listener responsibility is not an action generator.  Failed listener releases define an anti-listener toxicity field, and HS-JEPA should release only row-target moves that invert that field while preserving public/private action health.

## Evidence

- Toxic anchors loaded: `5`
- Candidate row-target directions: `938`
- Source responsibility LOO corr: `0.7682`

## Verdict

- Status: `candidate_ready`
- Recommended variant: `private_safe_anti_listener_bridge`

## Generated Candidates

| Rank | Variant | Cells | Rows | Listener inverse | Listener safety | Private safety | Hardworld tox | Broad tox | Pred delta | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `private_safe_anti_listener_bridge` | `30` | `29` | `0.503` | `0.527` | `0.789` | `0.200` | `0.427` | `-0.69071` | `True` | `submission_hsjepa_anti_listener_toxicity_private_safe_anti_listener_bridge_0b72cf91_uploadsafe.csv` |
| 2 | `q2s2_listener_toxicity_route` | `5` | `5` | `0.961` | `0.527` | `0.537` | `0.356` | `0.281` | `-0.01109` | `True` | `submission_hsjepa_anti_listener_toxicity_q2s2_listener_toxicity_route_61c3a6d1_uploadsafe.csv` |
| 3 | `listener_inverse_jackpot` | `4` | `4` | `0.952` | `0.527` | `0.454` | `0.433` | `0.359` | `-0.11494` | `True` | `submission_hsjepa_anti_listener_toxicity_listener_inverse_jackpot_e1f39e61_uploadsafe.csv` |
| 4 | `listener_toxicity_boundary_probe` | `7` | `7` | `0.960` | `0.527` | `0.467` | `0.354` | `0.502` | `-0.01285` | `True` | `submission_hsjepa_anti_listener_toxicity_listener_toxicity_boundary_probe_372faa12_uploadsafe.csv` |
| 5 | `public_subset_veto_listener_toxicity` | `8` | `7` | `0.531` | `0.527` | `0.630` | `0.268` | `0.508` | `-0.09881` | `True` | `submission_hsjepa_anti_listener_toxicity_public_subset_veto_listener_toxicity_b8eac215_uploadsafe.csv` |

## Sensor Interpretation

- If `listener_inverse_jackpot` wins, the failed listener submissions were pointing at the toxic direction and should be inverted.
- If `private_safe_anti_listener_bridge` wins, anti-listener only works after private/action-health filtering.
- If `q2s2_listener_toxicity_route` wins, Q2/S2 are the listener-toxicity route.
- If `public_subset_veto_listener_toxicity` wins, subset tomography is useful only after listener-toxic cells are removed.
- If all fail, listener toxicity is descriptive but not action-grade.
