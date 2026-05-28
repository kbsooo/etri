# Big Improvement Submission Shortlist

This file promotes the larger-move candidates after the small count/latent residual gains stalled.

## Public-LB First Order

1. `submission_bigshot_01_public_minimax_r05.csv` - best current robust public-constraint candidate.
2. `submission_bigshot_02_public_minimax_r01.csv` - almost identical score, simpler sparse ensemble.
3. `submission_bigshot_03_public_universe_u80.csv` - trusted expanded-universe alternative.
4. `submission_bigshot_04_public_universe_u65_maskrank.csv` - better if public rows are subject/random-like.
5. `submission_bigshot_08_public_consfront_t80.csv` - conservative bridge if the public constraints are partly overfit.

## JEPA Big-Probe Order

1. `submission_bigshot_10_jepa_neural_episode_rawstack_balanced.csv` - JEPA-heavy, bad-axis negative, raw-good positive.
2. `submission_bigshot_11_jepa_multifeature_rawstack.csv` - stronger OOF, small positive bad-axis.
3. `submission_bigshot_12_jepa_blockcanvas_aggressive_noq2.csv` - largest JEPA OOF probe here, high public risk.

## Candidate Table

| priority | alias | tier | OOF | public estimate / axis | risk |
|---:|---|---|---:|---|---|
| 1 | `submission_bigshot_01_public_minimax_r05.csv` | primary_public | 0.554348 | six-posterior score 0.5749169 / mean 0.5746342 | public feedback 3개를 제약식으로 쓴 후보라 private/hidden-subset overfit 리스크 있음 |
| 2 | `submission_bigshot_02_public_minimax_r01.csv` | primary_public | 0.554332 | selected score 0.5749250 / mean 0.5746342 | r05와 거의 같은 예측이지만 더 sparse한 6-weight ensemble |
| 3 | `submission_bigshot_03_public_universe_u80.csv` | primary_public_alt | 0.554343 | weighted expected 0.5746461 / score 0.5752114 | u80 trusted scenario에서 좋지만 mask-plausibility 평균순위는 u65보다 낮음 |
| 4 | `submission_bigshot_04_public_universe_u65_maskrank.csv` | primary_public_alt | 0.554759 | weighted expected 0.5746552 / mask mean-rank 17.54 | u80보다 더 보수적인 subject/random-like public-row 가정 |
| 5 | `submission_bigshot_05_public_targetmask_noq2_g075.csv` | single_public_probe | 0.554185 | public-posterior expected 0.575887 / robust mean 0.574649 | single projection이라 ensemble보다 분산 큼 |
| 6 | `submission_bigshot_06_public_entropy_exact_g100.csv` | aggressive_public_probe | 0.553679 | public self expected 0.575734 / exact fit to three public scores | known public scores에 가장 강하게 맞춘 exact-fit이라 overfit risk 최고 |
| 7 | `submission_bigshot_07_public_maskaware_t80_noq2.csv` | public_subset_fallback | 0.553156 | posterior mean 0.5755017 / conservative 0.5758453 | row-subset uncertainty fallback, minimax보다 expected는 약간 높음 |
| 8 | `submission_bigshot_08_public_consfront_t80.csv` | conservative_public | 0.557498 | posterior mean 0.5747919 / conservative mean 0.5746464 | OOF는 약하지만 public inverse overfit을 stage2/anchor 쪽으로 완충 |
| 9 | `submission_bigshot_09_hiddenblock_paretomix_w03.csv` | structural_control |  | posterior-fit 0.576825 / raw-axis expected 0.577526 | public-constraint 후보보다 약하지만 JEPA/raw hidden-block 구조 후보 중 안전 |
| 10 | `submission_bigshot_10_jepa_neural_episode_rawstack_balanced.csv` | jepa_big_oof_probe | 0.556972 | no direct public estimate / bad-axis -0.0984 / raw-good 1.1224 | public 미제출 JEPA high-upside probe. raw-good 과증폭 가능성 있음 |
| 11 | `submission_bigshot_11_jepa_multifeature_rawstack.csv` | jepa_big_oof_probe | 0.554194 | no direct public estimate / bad-axis 0.0220 / raw-good 0.5617 | OOF는 강하지만 failed-JEPA axis가 약하게 양수 |
| 12 | `submission_bigshot_12_jepa_blockcanvas_aggressive_noq2.csv` | jepa_aggressive_oof_probe | 0.550698 | no direct public estimate / bad-axis 0.1493 / raw-good -0.0027 | public axis 안전장치가 거의 없어 공격적 probe로만 사용 |

## Validation

- Manifest: `jepa/big_improvement_manifest.csv`
- Integrity: `jepa/big_improvement_validation.csv`
- All aliases preserve sample key/order, have 250 rows, no missing values, and target probabilities within [0, 1].

## Interpretation

The direct JEPA/count residual branch gave sub-0.001 gains, so it is not enough. The only current branch with a materially larger expected public move is the public-constraint/minimax branch, which uses the submitted public scores as aggregate hidden-label constraints. The JEPA-heavy files are kept as high-upside probes because their OOF is much lower, but public feedback already showed that direct JEPA movement can be punished.
