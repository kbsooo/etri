# S4/Q3 OOF Anchor Audit

Question: can existing OOF validation act as the missing independent S4/Q3 anchor?

## Summary

| n_oof | matched_submission | matched_pairwise | matched_old | local_q3s4_strong | pair_public_positive | old_public_positive | oof_anchor_like | strict_s4q3_anchor_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5167 | 5155 | 9 | 2 | 1578 | 0 | 2 | 0 | 0 |

## Correlations

- corr(q3s4_delta_vs_stage2_oof, pair_delta_vs_a2c8_p90) = `0.388` over n=9
- corr(q3s4_scenario_p90, pair_delta_vs_a2c8_p90) = `0.884` over n=9
- corr(overall_delta_vs_stage2_oof, pair_delta_vs_a2c8_p90) = `0.594` over n=9

## Top Local Q3/S4 OOF Improvements

| oof_path | matched_submission | q3s4_delta_vs_stage2_oof | q3s4_scenario_p90 | q3s4_scenario_win_rate | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | local_q3s4_strong | oof_anchor_like | strict_s4q3_anchor_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/final_public_maskaware_t65_r07_768f6df0_oof.npy | submission_public_maskaware_t65_r07_768f6df0.csv | -0.0207719 | -0.00794514 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t80_r11_544844af_oof.npy | submission_public_maskaware_t80_r11_544844af.csv | -0.0207719 | -0.00794514 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t80_r10_18d78615_oof.npy | submission_public_maskaware_t80_r10_18d78615.csv | -0.0205851 | -0.00725148 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t50_r04_6761fb38_oof.npy | submission_public_maskaware_t50_r04_6761fb38.csv | -0.020551 | -0.00811683 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t80_r12_dcfaabba_oof.npy | submission_public_maskaware_t80_r12_dcfaabba.csv | -0.020551 | -0.00811683 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t65_r08_7f7fa3e2_oof.npy | submission_public_maskaware_t65_r08_7f7fa3e2.csv | -0.0204784 | -0.00745521 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t50_r05_fb7b695a_oof.npy | submission_public_maskaware_t50_r05_fb7b695a.csv | -0.020332 | -0.00830473 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t50_r06_8d5b4fe1_oof.npy | submission_public_maskaware_t50_r06_8d5b4fe1.csv | -0.0203027 | -0.00842488 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t65_r09_35ff9a82_oof.npy | submission_public_maskaware_t65_r09_35ff9a82.csv | -0.0202532 | -0.00831094 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_maskaware_t35_r02_517540cc_oof.npy | submission_public_maskaware_t35_r02_517540cc.csv | -0.0201498 | -0.00825342 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_entropyproj_public2d0_g100_oof.npy | submission_public_entropyproj_public2d0_g100.csv | -0.0200497 | -0.00469374 | 0.954545 |  |  |  |  | True | False | False |
| analysis_outputs/final_public_entropyproj_proj0_g100_oof.npy | submission_public_entropyproj_proj0_g100.csv | -0.0197215 | -0.00456818 | 0.954545 |  |  |  |  | True | False | False |

## OOF Anchor-Like Candidates

_None._

## Interpretation

- Existing OOF files can be used as local sensors, but they do not currently provide a strict S4/Q3 public anchor.
- If local Q3/S4 gains do not overlap with both public-sensitive selectors, OOF is another validation view rather than a resolution of the selector conflict.
- The next useful action is to inspect the strongest local Q3/S4 OOF families and ask whether their signal is row-order/blockwise stable or only local-CV favorable.
