# Frontier-Trajectory Active-Silence Solver

## Thesis

The public frontier is a noisy gradient-descent trajectory.  HS-JEPA should learn both the positive frontier tangent and the active-silence field that blocks toxic post-frontier branches before releasing row-target actions.

## Frontier Evidence

- Positive frontier edges: `3`
- Total frontier public gain: `0.0007518`
- Candidate row-target directions: `3355`
- Bad tangent first-mode variance: `0.9629`

## Verdict

- Status: `candidate_ready`
- Recommended variant: `positive_path_overshoot_sensor`

## Generated Candidates

| Rank | Variant | Cells | Rows | Frontier cos | Bad cos | Silence | Energy | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `positive_path_overshoot_sensor` | `38` | `29` | `0.579` | `-0.350` | `0.196` | `-0.0325` | `True` | `submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv` |
| 2 | `active_silence_inversion` | `36` | `31` | `0.585` | `-0.365` | `0.200` | `-0.0335` | `True` | `submission_hsjepa_frontier_silence_active_silence_inversion_9df720c1_uploadsafe.csv` |
| 3 | `frontier_continuation_gate` | `44` | `34` | `0.544` | `-0.328` | `0.202` | `-0.0373` | `True` | `submission_hsjepa_frontier_silence_frontier_continuation_gate_404abf8d_uploadsafe.csv` |
| 4 | `frontier_silence_boundary_probe` | `18` | `18` | `0.185` | `0.080` | `0.700` | `-0.0482` | `True` | `submission_hsjepa_frontier_silence_frontier_silence_boundary_probe_aa9de021_uploadsafe.csv` |

## Sensor Interpretation

- If `positive_path_overshoot_sensor` wins, H057 was an under-stepped frontier trajectory, not a final optimum.
- If `frontier_continuation_gate` wins, the positive public trajectory is real but requires active silence gating.
- If `active_silence_inversion` wins, silence/toxicity is itself an invertible target representation.
- If all fail, the public frontier path is descriptive; the missing module is not continuation but row-support discovery.
