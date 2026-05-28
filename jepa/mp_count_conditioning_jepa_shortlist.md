# MP Count Conditioning JEPA Shortlist

## What Changed

This run converted the data-dissection finding into a JEPA-style count solver:

1. Build a measurement-process row latent from stage2 probabilities, measurement-process/rhythm/quiet/pre-sleep features, and the strongest forensic features.
2. Predict each hidden-like block latent from surrounding context only.
3. Use actual target-block latent minus predicted latent as the JEPA residual.
4. Predict hidden block label rates/counts.
5. Apply exact count conditioning to the row-level stage2 probabilities.

## CV Result

- Subject-chunk full OOF best: `0.567060`, delta `-0.000471` vs stage2 OOF `0.567531`.
- Geometry subset best: `0.544881`, delta `-0.003334` vs geometry base `0.548215`.
- The useful signal is concentrated in `Q1/Q2/Q3`; stage-only and S2/S3 variants did not help.

## Recommended Files

1. `submission_mpcount_recommended_01_rawrescue_q3_geom.csv`
   - Starts from the public-tested raw rescue file (`0.5775263072`) and adds only the geometry-Q3 count move.
   - Axis: bad `0.006698`, good `0.016138`.
   - Most practical first submission from this batch.

2. `submission_mpcount_recommended_02_publicsafe_q3_geom.csv`
   - Starts from `submission_jepa_public_safe_blend_00.csv` and adds the same Q3 move.
   - Axis: bad `0.002020`, good `0.014972`.
   - Good if the public-safe blend itself is submitted or trusted.

3. `submission_mpcount_recommended_03_stage2_q3_geom.csv`
   - Pure stage2 plus geometry-Q3 count move.
   - Axis: bad `-0.012591`, good `0.022010`.
   - Cleanest directionally, but base is weaker than raw rescue on public.

4. `submission_mpcount_recommended_04_direct_geom_qonly.csv`
   - Direct geometry count-conditioned Q1/Q2/Q3 candidate.
   - Geometry CV is strongest, but axis bad is higher (`0.026692`), so it is exploratory.

5. `submission_mpcount_recommended_05_direct_subject_qonly.csv`
   - Best full OOF direct count candidate.
   - Improvement is small and good-axis is negative, so it is lower priority.

## Interpretation

This confirms the earlier suspicion only partially: hidden block count/rate is real, but our current measurement-process JEPA latent does not yet recover enough of the oracle count gap. The best direct full OOF gain is only about `0.0005`; geometry CV sees a bigger `0.0033` gain, but mostly on Q targets.

Expected public range for the best practical file is still around the high `0.576` to mid `0.578` zone, not `0.54`.
