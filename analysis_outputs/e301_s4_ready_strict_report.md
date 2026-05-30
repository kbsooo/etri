# E301 S4 Ready Strict Confirmation

Public LB는 사용하지 않았다. E300의 단일 ready 후보만 대상으로 null budget과 seed prefix를 바꿔 재검증했다.

## Promotion Rule

- `conservative_public_free_ready`: strict gate 유지, 전체 null strict <= 0.10, p90 dominance >= 0.80, mean dominance >= 0.70, worst-mode p90 >= 0.60, worst-mode mean >= 0.50, sign p90 dominance >= 0.75.
- `watchlist_public_free_ready`: 더 느슨한 정보 후보 기준이며 public 제출 기준이 아니다.

## Governor

| basename | actual_strict_promote | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | worst_mode_mean_dominance | sign_p90_dominance | conservative_public_free_ready | watchlist_public_free_ready | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv | True | -0.000161310 | -0.000051307 | 0.164062500 | 0.937500000 | 0.691406250 | 0.843750000 | 0.328125000 | 1.000000000 | False | False | do_not_submit |

## Null Mode Distribution

| mode | n | strict_rate | mean_median | mean_p10 | mean_p90 | p90_median | p90_p10 | p90_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dateblock | 64 | 0.406250000 | -0.000163846 | -0.000169942 | -0.000155178 | -0.000049286 | -0.000051923 | -0.000045059 |
| row | 64 | 0.000000000 | -0.000134321 | -0.000151798 | -0.000107937 | -0.000039038 | -0.000045346 | -0.000007201 |
| sign | 64 | 0.000000000 | 0.000029466 | -0.000034409 | 0.000090256 | 0.000067019 | 0.000013580 | 0.000146256 |
| subject | 64 | 0.250000000 | -0.000161987 | -0.000169511 | -0.000152335 | -0.000047863 | -0.000051257 | -0.000040489 |

## Removed Parent Rows

| row_idx | subject_id | sleep_date | lifelog_date | dateblock_group | parent_S4_logit_delta | candidate_S4_logit_delta |
| --- | --- | --- | --- | --- | --- | --- |
| 169 | id07 | 2024-08-17 | 2024-08-16 | id07_b9 | 0.038800000 | 0.000000000 |
| 171 | id07 | 2024-08-20 | 2024-08-19 | id07_b9 | 0.038800000 | 0.000000000 |
| 172 | id07 | 2024-08-21 | 2024-08-20 | id07_b9 | 0.038800000 | 0.000000000 |

## Candidate Movement Anatomy

| summary_level | subject_id | dateblock_group | nonzero_rows | mean_delta | pos_rows | neg_rows |
| --- | --- | --- | --- | --- | --- | --- |
| dateblock |  | id03_b6 | 5 | 0.024533560 | 4 | 1 |
| dateblock |  | id07_b10 | 5 | 0.045008000 | 5 | 0 |
| dateblock |  | id07_b5 | 5 | 0.036300117 | 5 | 0 |
| dateblock |  | id01_b4 | 4 | 0.031460069 | 3 | 1 |
| dateblock |  | id01_b8 | 4 | 0.045008000 | 4 | 0 |
| dateblock |  | id03_b4 | 4 | -0.042938168 | 0 | 4 |
| dateblock |  | id02_b5 | 3 | 0.045008000 | 3 | 0 |
| dateblock |  | id03_b7 | 3 | -0.007382504 | 1 | 2 |
| dateblock |  | id07_b6 | 3 | 0.004265855 | 1 | 2 |
| dateblock |  | id02_b10 | 2 | 0.045008000 | 2 | 0 |
| dateblock |  | id03_b3 | 2 | -0.000000000 | 1 | 1 |
| dateblock |  | id08_b5 | 2 | -0.045008000 | 0 | 2 |
| dateblock |  | id01_b5 | 1 | 0.045008000 | 1 | 0 |
| dateblock |  | id01_b7 | 1 | 0.045008000 | 1 | 0 |
| dateblock |  | id02_b11 | 1 | 0.045008000 | 1 | 0 |
| dateblock |  | id07_b11 | 1 | 0.045008000 | 1 | 0 |
| dateblock |  | id08_b9 | 1 | -0.045008000 | 0 | 1 |
| subject | id03 |  | 14 | -0.005088027 | 6 | 8 |
| subject | id07 |  | 14 | 0.033167582 | 12 | 2 |
| subject | id01 |  | 10 | 0.039588828 | 9 | 1 |
| subject | id02 |  | 6 | 0.045008000 | 6 | 0 |
| subject | id08 |  | 3 | -0.045008000 | 0 | 3 |
| subject_dateblock | id03 | id03_b6 | 5 | 0.024533560 | 4 | 1 |
| subject_dateblock | id07 | id07_b10 | 5 | 0.045008000 | 5 | 0 |
| subject_dateblock | id07 | id07_b5 | 5 | 0.036300117 | 5 | 0 |
| subject_dateblock | id01 | id01_b4 | 4 | 0.031460069 | 3 | 1 |
| subject_dateblock | id01 | id01_b8 | 4 | 0.045008000 | 4 | 0 |
| subject_dateblock | id03 | id03_b4 | 4 | -0.042938168 | 0 | 4 |
| subject_dateblock | id02 | id02_b5 | 3 | 0.045008000 | 3 | 0 |
| subject_dateblock | id03 | id03_b7 | 3 | -0.007382504 | 1 | 2 |
| subject_dateblock | id07 | id07_b6 | 3 | 0.004265855 | 1 | 2 |
| subject_dateblock | id02 | id02_b10 | 2 | 0.045008000 | 2 | 0 |
| subject_dateblock | id03 | id03_b3 | 2 | -0.000000000 | 1 | 1 |
| subject_dateblock | id08 | id08_b5 | 2 | -0.045008000 | 0 | 2 |
| subject_dateblock | id01 | id01_b5 | 1 | 0.045008000 | 1 | 0 |
| subject_dateblock | id01 | id01_b7 | 1 | 0.045008000 | 1 | 0 |
| subject_dateblock | id02 | id02_b11 | 1 | 0.045008000 | 1 | 0 |
| subject_dateblock | id07 | id07_b11 | 1 | 0.045008000 | 1 | 0 |
| subject_dateblock | id08 | id08_b9 | 1 | -0.045008000 | 0 | 1 |

## Selected Selector Models

| model | feature_set | loo_sign_acc | l2o_sign_acc | model_score | current_order_pass |
| --- | --- | --- | --- | --- | --- |
| target_means_a0.03 | target_means | 0.731617647 | 0.625000000 | 0.004278515 | True |

## Decision

- `submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv` does not survive strict confirmation.
- Treat E300 as a useful anatomy discovery rather than a submission candidate.

## Outputs

- `analysis_outputs/e301_s4_ready_strict_governor.csv`
- `analysis_outputs/e301_s4_ready_strict_null_map.csv`
- `analysis_outputs/e301_s4_ready_strict_scores.csv`
- `analysis_outputs/e301_s4_ready_strict_anatomy.csv`
- `analysis_outputs/e301_s4_ready_strict_removed_rows.csv`
- `analysis_outputs/e301_s4_ready_strict_report.md`
