# CL2 0.5779 Public LB Analysis

Date: 2026-05-26

## Result

`submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` is the first confirmed CL2 submission that breaks the old 0.59 plateau.

| submission | public LB | offline estimate | note |
| --- | ---: | ---: | --- |
| `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` | 0.5779449757 | 0.567530925 | current public best |
| previous project anchor `v83_repaired` | 0.5997645835 | 0.5997645835 | old robust reference |

Improvement versus the old v83 anchor is `-0.0218196078` public LB. The filename says `0p567` because the offline fold-safe analogue is `0.567530925`; the submitted public score is `0.5779449757`.

## Integrity

The submitted file is structurally clean:

| check | value |
| --- | ---: |
| rows | 250 |
| columns | 10 |
| duplicate keys | 0 |
| null predictions | 0 |
| min probability | 0.065940657 |
| max probability | 0.979202418 |

Target-level distribution and drift versus `outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv` are saved in `cl2_0577_target_validation.csv`.

## Construction

The winning stage is not a generic CatBoost stack. It is a fold-safe residual feature stack built from the CL2 sensor feature work:

1. `broad_feature_addon_builder.py` starts from `submission_hybrid_0p575_foldsafe_quiet_s3_subject_q3_s4_s1_logit_s1.csv` and adds broad Q1/Q2 residual corrections.
2. That produces the stage1 base `submission_hybrid_0p573_foldsafe_broad_q1_calltime_q2_activity.csv`.
3. `broad_stage2_addon_builder.py` adds target-wise residual corrections on top of that base:

| target | feature | transform | weight |
| --- | --- | --- | ---: |
| Q1 | `deep__watch_light_w_light_all_log_mean` | subject_center | 0.45 |
| Q3 | `deep__ble_morning_unique_max` | subject_rank | 0.45 |
| S1 | `deep__ambience_all_hour_mean` | subject_z | 0.45 |
| S2 | `deep__phone_light_m_light_late_median` | subject_z | 0.45 |
| S3 | `deep__hr_all_rows` | subject_rank | 0.45 |
| S4 | `deep__ambience_evening_top_is_outside_mean` | subject_center | 0.45 |

Q2 is intentionally unchanged in stage2. The selected combo improves fold-safe OOF by `-0.0051198065` and has geometry win-rate `1.0`.

## What The Score Means

This is real progress, but the report should not overclaim the offline score. Public transfer is weak:

| comparison | public delta |
| --- | ---: |
| stage2 versus 0.578 anchor | -0.0004823771 |
| ordinal count correction versus stage2 | +0.0003583895 |

So the stage2 direction transfers only slightly to public, while larger OOF-only moves remain fragile. The saved `broad_nested_selection_bias_audit.py` result explains the risk: full-train broad residual mining is selection-biased, but this specific fixed stage2 direction still has positive public evidence.

## Direction

Use this file as the new public anchor. The next work should avoid blind residual mining and should instead treat stage2 as a coordinate system:

- Keep stage2 as the baseline for public-direction audits.
- Prefer target/projection gating over large raw OOF jumps.
- Focus public-constraint work on Q1, Q3, S3, and S4; Q2 carries little observed public benefit.
- Treat entropy/minimax public-constraint files as high-upside probes, not ordinary validation winners.
- Preserve the small OOF arrays and compact summary CSVs, but keep raw data, parquet feature caches, and massive generated grids out of git.
