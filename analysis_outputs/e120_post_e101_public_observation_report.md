# E120 Post-E101 Public Observation Audit

## Question

E101 was pre-registered as the smallest Q2/S3 tail rollback sensor after E95. Now that the actual public LB is known, does it open the E108/amplitude branch, revive E89/non-active fallback, or force a public-world rebuild?

## Observation

- E101 public LB: `0.5763003660`
- E95 public LB: `0.5762913298`
- Mixmin public LB: `0.5763066405`
- Delta E101 vs E95: `+0.0000090362`
- Delta E101 vs mixmin: `-0.0000062745`
- Delta E101 vs E72: `-0.0001074112`
- Delta E101 vs a2c8: `-0.0011389550`

E101 is worse than E95 by `+0.0000090362`, but still better than mixmin by `0.0000062745`. It gives back `59.02%` of E95's gain over mixmin and preserves `40.98%` of that gain.

## Decoder Result

E116 classifies the exact observation as `small_loss`.

- E116 world update: E101 active-cell support labels did not realize; the same rollback line is contradicted.
- E116 next action: Keep E95 as frontier, mark E101 branch as model tension, and rebuild the public-world model before any same-family file.
- E116 forbidden action: Do not submit E108, subject-prior gates, active-restored E89/E85, or non-active grafts as automatic followups.

Important nuance: the coarse E116 `small_loss` band as a whole was marked not mixmin-beating, but the exact E101 score does beat mixmin. The branch decision is still loss-side because the active-cell rollback failed to beat the current E95 frontier.

## Stress Contradiction

The pre-feedback local stress expected full active-all E101 to be favorable:

- local mean vs E95: `-0.0000162053`
- local p95 vs E95: `-0.0000015641`
- local beat-E95 rate: `0.983488`

The actual public delta is `+0.0000090362`. That is `+0.0000252415` worse than the local mean and `+0.0000106003` worse than the local p95. This is the main signal: the E99/E101 broad-plausible world model underestimated the loss-side public tail.

## Loss-Side Gates

- E107 small-loss scenario mode: `nearest`, model tension `True`, nearest scenarios `240`.
- E109 subject-prior small-loss mass: `0.355350`.
- E110 non-control strict fallback candidates after tie/loss: `0`.
- E110 non-control diagnostic sensors after tie/loss: `8`.
- E119 E101-pass flank-gate rows: `66`.
- E119 E101-dominating flank-gate rows: `0`.

These prior loss-side audits line up with the observed branch: E108/higher-alpha, subject-prior gates, flank-gates, active-restored E89/E85, and non-active grafts are closed as automatic followups.

## Belief Update

The current best one-sentence model changes from:

> E95 may have over-amplified a Q2/S3/S3-heavy active-cell tail, and E101 is the cleanest public kill-test.

to:

> E95's hard-tail target-axis surgery remains the standing law; E101 shows that Q2/S3 rollback support exists enough to stay above mixmin, but not enough to beat the frontier, so the loss-side public tail is outside the E99/E101 local stress model.

## Decision

Keep `submission_e95_hardtail_541e3973.csv` as the public frontier. Mark `submission_e101_q2s3tail_177569bc.csv` as a resolved negative sensor, not as a failed random file.

Do not submit E108, E104 higher-alpha, E106 subject-prior masks, E119 flank-gated variants, full E89, or E110 non-active grafts as automatic next files.

The next useful experiment is not another same-family submission. It is an exact post-E101 public-world rebuild that treats E95 and E101 as a two-point hard-tail boundary: E95 is right enough to win, E101 is right enough to beat mixmin, and the missing structure is the small public subset of Q2/S3/S3-heavy tail labels that flips that boundary.
