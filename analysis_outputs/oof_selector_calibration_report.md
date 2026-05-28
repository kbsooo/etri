# E39 OOF Selector Calibration Audit

## Observe

E38 ranked public sensors but could not certify any candidate. The next question is whether train OOF history can create an independent selector calibration target.

## Wonder

Do label-free train OOF stresses such as future-tail rows, train/test-domain-like rows, density, missingness, subject blocks, and date blocks select candidates whose sign is stable and whose known-public analogues agree with public LB?

## Hypothesis

H38: if selector identity can be calibrated locally, OOF improvements should be stable across label-free pseudo-public subsets, and known public OOF files should have OOF signs consistent with their public sign relative to the baseline.

## Method

- Baseline OOF: `analysis_outputs/final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy`.
- OOF rows scored: `4172` after hash dedupe plus known-public aliases.
- Unique prediction hashes: `4171`.
- Label-free subsets: `24` plus random blocks.
- Train/test domain AUC from raw features: `1.000000`.
- Gates use real train labels only through OOF predictions; public LB is only used for the known-public sanity table.

## Result

- strict OOF selector gates: `1311`.
- conservative OOF gates: `1115`.
- known-public nonbaseline sign match rate: `1.000000`.
- known-public nonbaseline pairwise rank agreement: `0.000000`.

## Known Public OOF Sanity

| file                                                                            | known_public_role                 | known_public_lb | known_public_delta_vs_final9 | full_delta | stress_p90_delta | stress_worst_delta | label_free_better_rate | subject_better_rate | order_better_rate | random_better_rate | strict_oof_selector_gate | conservative_gate | sign_matches_public |
| ------------------------------------------------------------------------------- | --------------------------------- | --------------- | ---------------------------- | ---------- | ---------------- | ------------------ | ---------------------- | ------------------- | ----------------- | ------------------ | ------------------------ | ----------------- | ------------------- |
| analysis_outputs/final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy   | stage2_public_better_than_final9  | 0.577945        | -0.000482377                 | -0.0107727 | -0.00576057      | 0.00111612         | 1                      | 0.9                 | 1                 | 1                  | False                    | False             | True                |
| analysis_outputs/final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy | ordinal_public_better_than_final9 | 0.578303        | -0.000123988                 | -0.0163999 | -0.0105806       | -0.00562309        | 1                      | 1                   | 1                 | 1                  | True                     | True              | True                |
| analysis_outputs/final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy   | final9_baseline                   | 0.578427        | 0                            | 0          | 0                | 0                  | 0                      | 0                   | 0                 | 0                  | False                    | False             | True                |

## Family Summary

| family      | n    | strict_oof_gates | conservative_gates | median_full_delta | median_stress_p90_delta | best_file                                                                                                  | best_full_delta | best_stress_p90_delta | best_stress_worst_delta | best_score  |
| ----------- | ---- | ---------------- | ------------------ | ----------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------- | --------------- | --------------------- | ----------------------- | ----------- |
| orthcap     | 2626 | 612              | 463                | -0.0124575        | -0.00678013             | analysis_outputs/final_orthcap030_exact_q2q3_exact_value_nearest_w1_oof.npy                                | -0.0189487      | -0.011433             | -0.00836646             | -0.0135251  |
| subjectgate | 250  | 189              | 185                | -0.0146314        | -0.00909667             | analysis_outputs/final_subjectgate_blend500_all_thr0p0_w100_oof.npy                                        | -0.0187826      | -0.0118592            | -0.0048721              | -0.0130775  |
| stage2      | 238  | 154              | 128                | -0.0120993        | -0.00739281             | analysis_outputs/final_mp_stage2_nonq2_oof.npy                                                             | -0.0166602      | -0.0128106            | -0.00181284             | -0.0132642  |
| publicblend | 127  | 113              | 113                | -0.0213283        | -0.0125971              | analysis_outputs/final_public_maskaware_t50_r05_fb7b695a_oof.npy                                           | -0.0250919      | -0.0154115            | -0.0127569              | -0.0186012  |
| ordinal     | 131  | 111              | 111                | -0.0150496        | -0.00934903             | analysis_outputs/final_subjectgate_ordinal_all_thrm0p005_w100_oof.npy                                      | -0.0197198      | -0.012329             | -0.00653425             | -0.0139629  |
| presleep    | 639  | 91               | 83                 | -0.00931972       | -0.00424925             | analysis_outputs/final_publicgated_q3off650_presleep_core_prectx_s2charge_s3light_q3hr_ble_ambnext_oof.npy | -0.0158989      | -0.00938204           | -0.003554               | -0.0102709  |
| other       | 33   | 23               | 22                 | -0.010001         | -0.00640727             | analysis_outputs/final_projblend_cap0p3_oof.npy                                                            | -0.0189223      | -0.0114115            | -0.00837786             | -0.0135063  |
| rhythm      | 13   | 13               | 7                  | -0.0105593        | -0.00637718             | analysis_outputs/final_rhythm_q3off650_nonq2_strict_oof.npy                                                | -0.0142918      | -0.00897615           | -0.00197045             | -0.0094691  |
| jepa        | 12   | 3                | 3                  | -0.0129173        | -0.00685035             | jepa/jepa_latent_residual_probe_risky_top_oof.npy                                                          | -0.0175471      | -0.0104467            | -0.00767905             | -0.012367   |
| hybrid      | 89   | 2                | 0                  | 0.00121095        | 0.00248725              | analysis_outputs/final_hybrid_0p573_foldsafe_broad_q1_calltime_oof.npy                                     | -0.0052126      | -0.00256631           | 0.00040122              | -0.00246619 |
| block       | 14   | 0                | 0                  | 0.00257727        | 0.0198398               | analysis_outputs/final_public_blockentropy_minimax_all_g035_fd4765c6_oof.npy                               | -0.00738299     | 0.00454199            | 0.0116091               | 0.00744376  |

## Top OOF-Stable Candidates

| file                                                               | family      | full_delta | stress_p90_delta | stress_worst_delta | stress_better_rate | mean_abs_move_vs_baseline | strict_oof_selector_gate | conservative_gate |
| ------------------------------------------------------------------ | ----------- | ---------- | ---------------- | ------------------ | ------------------ | ------------------------- | ------------------------ | ----------------- |
| analysis_outputs/final_public_maskaware_t50_r05_fb7b695a_oof.npy   | publicblend | -0.0250919 | -0.0154115       | -0.0127569         | 1                  | 0.0564562                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t50_r06_8d5b4fe1_oof.npy   | publicblend | -0.0250421 | -0.0153469       | -0.0127057         | 1                  | 0.0567948                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t50_r04_6761fb38_oof.npy   | publicblend | -0.0251823 | -0.0153627       | -0.0124106         | 1                  | 0.0586658                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t65_r09_35ff9a82_oof.npy   | publicblend | -0.0250097 | -0.0153137       | -0.0125254         | 1                  | 0.0572162                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t65_r07_768f6df0_oof.npy   | publicblend | -0.0252588 | -0.015155        | -0.0122625         | 1                  | 0.0600956                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t35_r02_517540cc_oof.npy   | publicblend | -0.0244876 | -0.0153317       | -0.0114982         | 1                  | 0.0560126                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t65_r08_7f7fa3e2_oof.npy   | publicblend | -0.0250213 | -0.0151547       | -0.0117842         | 1                  | 0.0599799                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t80_r10_18d78615_oof.npy   | publicblend | -0.0251266 | -0.0150097       | -0.0115945         | 1                  | 0.0596462                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t35_r01_2d5fa124_oof.npy   | publicblend | -0.0240489 | -0.0145659       | -0.0118765         | 1                  | 0.0538687                 | True                     | True              |
| analysis_outputs/final_public_universeens_u65_r01_365a84a6_oof.npy | publicblend | -0.0239859 | -0.0146393       | -0.0108715         | 1                  | 0.0554518                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t80_r12_dcfaabba_oof.npy   | publicblend | -0.0250455 | -0.014853        | -0.00959125        | 1                  | 0.0567855                 | True                     | True              |
| analysis_outputs/final_public_maskaware_t80_r11_544844af_oof.npy   | publicblend | -0.0251478 | -0.0148332       | -0.00951602        | 1                  | 0.0580824                 | True                     | True              |

## Decision

OOF stress is useful as a negative calibration target but not as a submission selector. It can expose local stability and local overfit, but it does not resolve the public selector/worldview conflict because known-public sign can match while known-public ordering still reverses.

## Outputs

- `analysis_outputs/oof_selector_calibration_scores.csv`
- `analysis_outputs/oof_selector_calibration_family_summary.csv`
- `analysis_outputs/oof_selector_calibration_known_public.csv`
- `analysis_outputs/oof_selector_calibration_subsets.csv`
