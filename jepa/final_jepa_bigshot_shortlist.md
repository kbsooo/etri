# Final JEPA Big-Shot Shortlist

This round added three JEPA-style directions after the earlier Raw Timeline, Block-Canvas, and latent-residual probes.

## New Ideas Tested

1. Episode Retrieval JEPA
   - Treat each hidden block as an episode.
   - Use actual block canvas latent and predicted context latent to retrieve similar labeled train episodes.
   - Donor label-rate/entropy/endpoint distributions become residual features.
   - Best standalone OOF: `0.563147` from `submission_episode_retrieval_jepa_top_probe_scale1p0.csv`.

2. Episode Raw-Anchor Stack
   - Keep the known public-positive raw timeline rescue as the anchor.
   - Add episode retrieval residual movement in logit space.
   - Best balanced OOF: `0.560901` from `submission_jepa_episode_rawstack_raw075_er_strict10_rw1p0_ew1p0.csv`.

3. Neural Block-Canvas JEPA MPS
   - PyTorch MPS dual-head predictor.
   - Context predicts both hidden block raw latent and hidden block label-rate latent.
   - JEPA latent is used as residual/probe features, not directly as final probability.
   - Best standalone OOF: `0.562353` from `submission_neural_block_canvas_jepa_mps_top_probe_scale1p0.csv`.
   - Important sign: `jepa_bad_ratio=-0.170577`, meaning it is anti-aligned with the previously bad public JEPA axis.

4. Neural + Episode + Raw Stack
   - Raw timeline is the public-good anchor.
   - Neural Block-Canvas supplies anti-bad-axis residual movement.
   - Episode Retrieval supplies block-level label-distribution residual movement.
   - Best OOF reached `0.556389`.

## Submission Priority

| Priority | Candidate | OOF | Bad-Axis | Raw-Good Axis | Notes |
|---:|---|---:|---:|---:|---|
| 1 | `submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw0p75_nw1p0_ew1p0.csv` | 0.556972 | -0.098405 | 1.122391 | Best balanced candidate. Strong OOF, raw-good aligned, bad-axis negative, less aggressive than top. |
| 2 | `submission_jepa_neural_episode_rawstack_targetwise_raw075_nb_top10_er_strict10.csv` | 0.557180 | -0.145768 | 1.329726 | Conservative per-target weights; good when avoiding global overpush. |
| 3 | `submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw1p25_nw1p25_ew1p0.csv` | 0.556389 | -0.137718 | 1.806553 | Highest OOF gain, but aggressive raw-good amplification. Submit only if taking risk. |
| 4 | `submission_jepa_neural_episode_rawstack_raw075_nb_top10_none_rw1p0_nw1p0_ew0p0.csv` | 0.560265 | -0.163915 | 1.444952 | No Episode Retrieval. Useful control to isolate neural JEPA + raw anchor. |
| 5 | `submission_neural_block_canvas_jepa_mps_top_probe_scale1p0.csv` | 0.562353 | -0.170577 | 0.153257 | Pure neural JEPA diagnostic. Not the strongest, but public-axis behavior is very different from failed JEPA probes. |
| 6 | `submission_jepa_episode_rawstack_raw075_er_strict10_rw1p0_ew1p0.csv` | 0.560901 | 0.024856 | 1.361909 | Episode + raw without neural. Useful ablation. |

## Validation

All six priority files:

- shape: `(250, 10)`
- target columns: `Q1, Q2, Q3, S1, S2, S3, S4`
- missing target values: `0`
- probability range across checked files: approximately `0.0709` to `0.9821`

## Interpretation

The key breakthrough was not Episode Retrieval alone. Episode Retrieval found OOF signal, but its standalone public-axis movement was weak. The bigger step came from using MPS to train a neural block-canvas JEPA that predicts hidden block latent state and label-rate latent state together. That neural movement is anti-aligned with the known bad JEPA axis, so stacking it with the raw-timeline public-good anchor and episode retrieval creates a much cleaner direction than the earlier JEPA residual submissions.

The safest first submission from this round is:

`submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw0p75_nw1p0_ew1p0.csv`

