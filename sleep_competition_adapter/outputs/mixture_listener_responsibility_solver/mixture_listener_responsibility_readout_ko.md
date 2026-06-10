# Mixture-Listener Responsibility Solver

## Thesis

Public LB is not treated as one monolithic target.  It is treated as a scalar observation emitted by a mixture of latent listeners.  HS-JEPA must decide whether actions are valid under consensus, conflict, or target-specific listener routing.

## Mixture Fit

- Anchor count: `26`
- Candidate cells: `575`
- Mixture train corr: `0.9894`
- Mixture LOO corr: `0.9578`
- Scalar LOO corr: `0.7300`

| Mode | Variance | Cumulative | Beta | Score/Loss corr |
| ---: | ---: | ---: | ---: | ---: |
| 0 | `0.4338` | `0.4338` | `-0.1353` | `-0.9562` |
| 1 | `0.1511` | `0.5849` | `0.0202` | `0.0844` |
| 2 | `0.1212` | `0.7060` | `-0.0212` | `-0.0794` |
| 3 | `0.0854` | `0.7914` | `-0.0516` | `-0.1620` |
| 4 | `0.0713` | `0.8627` | `0.0440` | `0.1264` |
| 5 | `0.0597` | `0.9224` | `0.0358` | `0.0942` |

## Verdict

- Status: `candidate_ready`
- Recommended variant: `target_listener_split_qs`
- Reason: Recommended by mixture-listener predicted improvement, mode confidence, action-health, and upload-safe validation.

## Generated Candidates

| Rank | Variant | Cells | Rows | Scalar delta | Mode delta | Conflict | Confidence | Bad cosine | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `target_listener_split_qs` | `30` | `28` | `-4.34421` | `-0.53670` | `0.200` | `0.500` | `-0.0042` | `True` | `submission_hsjepa_mixture_listener_target_listener_split_qs_7a383104_uploadsafe.csv` |
| 2 | `mixture_consensus_jackpot` | `12` | `11` | `-2.11948` | `-0.55679` | `0.063` | `0.527` | `-0.0075` | `True` | `submission_hsjepa_mixture_listener_mixture_consensus_jackpot_7dd97d06_uploadsafe.csv` |
| 3 | `bad_mode_inside_out_probe` | `16` | `13` | `-1.52620` | `-0.36927` | `0.514` | `0.521` | `-0.0062` | `True` | `submission_hsjepa_mixture_listener_bad_mode_inside_out_probe_ce5085e8_uploadsafe.csv` |
| 4 | `portable_mixture_core` | `11` | `11` | `-0.57108` | `-0.28171` | `0.294` | `0.474` | `-0.0053` | `True` | `submission_hsjepa_mixture_listener_portable_mixture_core_d2b78c96_uploadsafe.csv` |
| 5 | `private_residual_rescue_jackpot` | `5` | `5` | `0.23974` | `0.00081` | `0.812` | `0.473` | `0.0017` | `True` | `submission_hsjepa_mixture_listener_private_residual_rescue_jackpot_2472ad5f_uploadsafe.csv` |

## Sensor Interpretation

- If `mixture_consensus_jackpot` wins, HS-JEPA should require agreement among latent listeners.
- If `private_residual_rescue_jackpot` wins, the breakthrough lives in listener conflict, not consensus.
- If `target_listener_split_qs` wins, Q/S should be routed through different listener heads.
- If all fail, public LB anchors are not enough to identify an action-grade listener mixture.
