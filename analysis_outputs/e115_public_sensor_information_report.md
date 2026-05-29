# E115 Public Sensor Information Audit

## Question

After E114, raw context no longer supports E101. The remaining question is
whether E101 is still the right next public sensor, or whether E89/E85/E90/E86
would provide more information.

This audit does not predict leaderboard labels. It asks how each pending control
file would split the E95-conditioned broad-plausible worlds that already explain
the E72 miss and the E95 gain.

## Sensor Summary

| sensor | n_broad_worlds | mean_vs_e95 | p05_vs_e95 | p50_vs_e95 | p95_vs_e95 | beat_e95_rate | win_rate | tie_rate | loss_rate | outcome_entropy_bits | decisive_outcome_count | branch_family_count | raw_split_information_score | actionable_rate | actionable_information_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_e101 | 3452 | -0.000016205 | -0.000036566 | -0.000014288 | -0.000001564 | 0.983487833 | 0.911645423 | 0.088354577 | 0.000000000 | 1.728493092 | 4 | 1 | 1.575772816 | 0.933734067 | 1.613952885 |
| control_e89 | 3452 | 0.000003833 | -0.000006046 | 0.000004002 | 0.000012552 | 0.195828505 | 0.086037080 | 0.333719583 | 0.580243337 | 1.380098589 | 3 | 1 | 0.919532664 | 0.169466976 | 0.233881134 |
| control_e85 | 3452 | 0.000009659 | 0.000001148 | 0.000009638 | 0.000018271 | 0.031865585 | 0.012456547 | 0.096755504 | 0.890787949 | 0.702268128 | 2 | 1 | 0.634319822 | 0.036645423 | 0.025734913 |
| control_e90 | 3452 | 0.000013372 | 0.000003056 | 0.000011198 | 0.000031244 | 0.002607184 | 0.000289687 | 0.047508691 | 0.952201622 | 0.963217352 | 3 | 1 | 0.917456157 | 0.012166860 | 0.011719330 |
| control_e86 | 3452 | 0.000020345 | 0.000005543 | 0.000015880 | 0.000046606 | 0.000289687 | 0.000000000 | 0.009849363 | 0.990150637 | 1.044753489 | 2 | 1 | 1.034463333 | 0.002462341 | 0.002572539 |
| control_mixmin | 3452 | 0.000015311 | 0.000015311 | 0.000015311 | 0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | -0.000000000 | 1 | 1 | -0.000000000 | 0.000000000 | -0.000000000 |

## Top Sensor Outcome Map

Top sensor: `control_e101`.

| outcome | n_scenarios | rate | delta_mean | delta_p50 | best_followup_label | best_followup_family | best_followup_mean_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| strong_win | 465 | 0.134704519 | -0.000035496 | -0.000034897 | e104_amp_active_all_a0.500_079aab57 | e104_amp | -0.000066283 |
| edge_win | 1651 | 0.478273465 | -0.000019294 | -0.000018729 | e104_amp_active_all_a0.500_079aab57 | e104_amp | -0.000035686 |
| small_win | 1031 | 0.298667439 | -0.000006992 | -0.000006948 | e104_amp_active_all_a0.500_079aab57 | e104_amp | -0.000012709 |
| tie | 305 | 0.088354577 | -0.000001218 | -0.000001383 | e104_amp_active_all_a0.500_079aab57 | e104_amp | -0.000001703 |

## Interpretation

- `control_e101` has the highest actionable-information score and the largest
  outcome entropy. Its public result separates strong-win, edge-win, small-win,
  and tie worlds instead of collapsing into one obvious loss bucket.
- E89 has some branch value, but its broad-world distribution is centered near
  tie/small-loss and has much lower E95-beat rate.
- E85/E90/E86 mostly ask how badly they lose relative to E95, which is lower
  information because E95-conditioned worlds already made E95 the standing
  winner.

## Decision

No submission is materialized by E115. The next public sensor remains
`submission_e101_q2s3tail_177569bc.csv`.

If E101 improves, the live world is S3-heavy Q2/S3 over-amplification and the
conditional E108 amplitude-up branch becomes meaningful. If E101 ties or loses,
the same-line rollback family should not be amplified; the E99/E101 public-world
model must be rebuilt.
