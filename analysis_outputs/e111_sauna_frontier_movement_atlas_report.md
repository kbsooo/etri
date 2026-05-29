# E111 Sauna Frontier Movement Atlas

## Question

If the E95 plateau is a hard-tail calibration phenomenon, public-positive movement should look less like a broad model upgrade and more like a sparse target/cell risk edit. This audit observes only submission geometry: no new model, no CV, no feature generation.

## Key Observations

- Known public anchors versus mixmin:
  - E72 failed sparse movement: public delta `+0.0001011367`, active cells `893`, L1 prob `2.203482`, Q-share `0.450788`, S-share `0.549212`, Q2/S3 share `0.198389`, E95-confident share `0.222567`, cosine with E95 direction `0.327033`.
  - E95 frontier hardtail: public delta `-0.0000153107`, active cells `550`, L1 prob `1.509562`, Q-share `0.019948`, S-share `0.980052`, Q2/S3 share `0.209993`, E95-confident share `0.386257`.
- E101 relative to E95 changes only `50` cells across `48` rows, Q2/S3 share `1.000000`, S-target share `0.905306`, entropy delta `-0.0000243763`.
- Full E89 relative to E95 has active cells `158`, L1 prob `0.107468`, Q2/S3 share `0.299376`, E95-confident share `0.277739`.

## Sauna Interpretation

The strange point sharpens: public-positive E95 is not a high-magnitude global model movement. It is target-axis surgery. E72 failed with broad Q/Q3/S4 contamination and low directional cosine to E95, while E95 keeps almost all movement on the S side plus a tiny Q2 component. E101 is even more surgical: it asks only whether E95's selective Q2/S3 cells should roll back toward the older mixmin geometry. Full E89 remains a larger diffuse-tail move, not a cleaner strict successor.

## Belief Update

- Strengthen: the 0.576 plateau is shaped by target-axis hard-tail calibration, especially Q2/S3/S-family movement, not by generic capacity.
- Weaken: broad movement along an apparently good latent/structure direction should be trusted without target/cell tail stress.
- Next kill-test: submit E101, because it is the smallest public sensor that can falsify whether E95's Q2/S3 hardtail localization is over-tight.

## Outputs

- `e111_sauna_frontier_movement_atlas_summary.csv`
- `e111_sauna_frontier_movement_atlas_target_detail.csv`
