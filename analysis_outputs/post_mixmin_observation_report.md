# Post-Mixmin Observation Audit

This is an observation-first audit, not a model run. It asks what hidden label world must be true for `submission_mixmin_0c916bb4.csv` to beat the previous a2c8 frontier.

## Dataset Shape

- train rows: `450`
- test/submission rows: `250`
- subjects train/test: `10` / `10`
- train date span: `2024-06-04` to `2024-11-15`
- test date span: `2024-07-07` to `2024-11-20`

## First Observations

- `Q3` carries large mixmin movement: mean abs move `0.011540`, signed mean `0.000061`, move-up rate `0.420`, threshold-for-new-to-win `0.613`.
- `Q1` carries large mixmin movement: mean abs move `0.010345`, signed mean `-0.002884`, move-up rate `0.284`, threshold-for-new-to-win `0.469`.
- `S3` carries large mixmin movement: mean abs move `0.009688`, signed mean `0.006412`, move-up rate `0.624`, threshold-for-new-to-win `0.597`.

## Prior-World Stress

- `Q1`: CE delta if labels followed train/global prior `+0.00125609`, subject prior `+0.00144423`, recent7 prior `+0.00228295`; best proxy `ce_delta_at_train_prevalence`.
- `Q2`: CE delta if labels followed train/global prior `-0.00073280`, subject prior `-0.00086797`, recent7 prior `-0.00121684`; best proxy `ce_delta_at_recent7_prior`.
- `Q3`: CE delta if labels followed train/global prior `+0.00082236`, subject prior `+0.00063620`, recent7 prior `-0.00128763`; best proxy `ce_delta_at_recent7_prior`.
- `S1`: CE delta if labels followed train/global prior `+0.00259178`, subject prior `+0.00467007`, recent7 prior `+0.00685649`; best proxy `ce_delta_at_train_prevalence`.
- `S2`: CE delta if labels followed train/global prior `-0.00519912`, subject prior `-0.00106082`, recent7 prior `-0.00123115`; best proxy `ce_delta_at_train_prevalence`.
- `S3`: CE delta if labels followed train/global prior `-0.00334829`, subject prior `-0.00188758`, recent7 prior `+0.00107572`; best proxy `ce_delta_at_train_prevalence`.
- `S4`: CE delta if labels followed train/global prior `+0.00236841`, subject prior `+0.00018197`, recent7 prior `-0.00158525`; best proxy `ce_delta_at_recent7_prior`.

Negative CE delta means mixmin would beat a2c8 under that proxy label-world. If these simple priors do not favor mixmin, the public gain likely comes from a more structured hidden subset/state rather than ordinary prevalence correction.

## Subject/Row Concentration

- `id05` has the largest mean movement `0.009748` over `21` test rows; dominant target `Q3`.
- `id09` has the largest mean movement `0.009413` over `27` test rows; dominant target `S3`.
- `id08` has the largest mean movement `0.009363` over `19` test rows; dominant target `Q1`.
- `id03` has the largest mean movement `0.009292` over `21` test rows; dominant target `S3`.
- `id01` has the largest mean movement `0.009134` over `27` test rows; dominant target `Q3`.

## Calendar Mask Observation

Train/test is not a simple future split. Test rows are hidden calendar blocks inside each subject's observed timeline, often flanked by train runs.

- `gap_adjacent` / `after_train_end` / run length `5` / dominant `S3`: rows `1`, mean abs move `0.014170`, mixmin-raw05 distance `0.013509`.
- `gap_adjacent` / `inside_train_calendar` / run length `2` / dominant `S4`: rows `1`, mean abs move `0.013618`, mixmin-raw05 distance `0.013921`.
- `gap_adjacent` / `inside_train_calendar` / run length `1` / dominant `S3`: rows `2`, mean abs move `0.012484`, mixmin-raw05 distance `0.013800`.
- `between_train_runs` / `inside_train_calendar` / run length `15` / dominant `S4`: rows `1`, mean abs move `0.012137`, mixmin-raw05 distance `0.011358`.
- `gap_adjacent` / `after_train_end` / run length `8` / dominant `S1`: rows `1`, mean abs move `0.011738`, mixmin-raw05 distance `0.011202`.
- `gap_adjacent` / `inside_train_calendar` / run length `5` / dominant `S4`: rows `2`, mean abs move `0.011505`, mixmin-raw05 distance `0.011908`.

This reframes the JEPA context/target question: the natural context may be the train-labeled calendar flanks around a hidden test block, and the target representation may be the block's label-rate vector rather than individual row probabilities.

## New Questions

1. Is mixmin winning because it moves the right target globally, or because it concentrates movement on a few subject/date blocks?
2. Do the cells where mixmin moves away from a2c8 require label prevalences that resemble train priors, subject priors, or a stranger binary hidden-public world?
3. Does raw05 fail because it stays too close to a measurement-process manifold, while mixmin crosses a block/state boundary that raw05 cannot express?
4. Are the high-movement rows public-like, or are they private-risk rows that happened to align with public?

## Falsifiable Next Experiment

Build a mixmin-relative selector target: add mixmin as a known public anchor, then ask whether target/subject/date movement fingerprints can explain mixmin without breaking raw05, stage2, ordinal, and bad-JEPA anchor order. Success means the selector error drops below the mixmin-a2c8 edge scale; failure means E48 was public-subset luck or an anchor-derived worldview that still lacks private safety.
