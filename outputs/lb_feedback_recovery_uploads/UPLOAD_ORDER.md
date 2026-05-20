# LB Feedback Recovery Upload Order

Public LB feedback:

- Rejected: `outputs/sample_portfolio_v38a_v37e_mid_tail_push/submission_sample_support_target_blend.csv`
- Public LB: `0.6335340671`
- Timestamp: `2026-05-19 10:22:03`

## Recommended Order

1. `submission_15_v18_old15_prob_blend.csv`
   - First recovery candidate.
   - Uses `85%` v18 q3-tail signal and `15%` oldbalanced anchor in probability space.
   - Uniform OOF CV: `0.576217`
   - Sample-weighted proxy CV: `0.549805`
   - Submission min/max: `0.090049` / `0.987892`

2. `submission_12_v18_old20_prob_blend.csv`
   - Safer shrink if the first recovery is still poor on public LB.
   - Uses `80%` v18 q3-tail signal and `20%` oldbalanced anchor in probability space.
   - Uniform OOF CV: `0.576410`
   - Sample-weighted proxy CV: `0.551642`
   - Submission min/max: `0.104185` / `0.985883`

3. `submission_13_v18_old30_prob_blend.csv`
   - Even safer shrink if old20 is still poor on public LB.
   - Uniform OOF CV: `0.576820`
   - Sample-weighted proxy CV: `0.555545`
   - Submission min/max: `0.110588` / `0.981866`

4. `submission_11_v18_old10_prob_blend.csv`
   - Stronger upside if the first recovery improves public LB.
   - Uniform OOF CV: `0.576031`
   - Sample-weighted proxy CV: `0.548042`
   - Submission min/max: `0.063825` / `0.989900`

5. `submission_03_v18_q3tail_raw.csv`
   - High-upside raw probe only after blended candidates show public-LB calibration is sane.
   - Uniform OOF CV: `0.575682`
   - Sample-weighted proxy CV: `0.544735`
   - Submission min/max: `0.010386` / `0.993918`

## Notes

- v38a is now source-bank material only, not a direct submission candidate.
- Do not promote a local-CV frontier unless a calibrated blend companion also survives public feedback.
