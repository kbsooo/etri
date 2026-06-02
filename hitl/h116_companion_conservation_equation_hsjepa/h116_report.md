# H116 Companion-Conservation Row-Target Equation HS-JEPA

No upload-safe candidate was promoted.

Core finding:

```text
Q2 companion rescue exists, but every positive-rescue bundle is H088-positive.
The available anti-H088 guard cells either cancel too little H088 direction or
create too much bad-axis pressure.  Under the current public/private equation,
Q2 companion conservation is a toxic sector, not a safe assignment field.
```

Audit:

| spec_name | bundle_pool_size | guard_pool_size | positive_rescue_bundles | rescue_and_h088_nonpositive_bundles | max_q2_rescue_marginal | min_full_curv_marginal | min_guard_h088_cos | min_guard_bad_weighted_pos | min_bundle_h088_cos | max_bundle_h088_cos | min_bundle_bad_weighted_pos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q2_conservation_strict_b8_a035 | 26 | 103 | 26 | 0 | 0.000033805 | -0.000036027 | -0.176680564 | 0.000000000 | 0.026329450 | 0.168029061 | 0.001590098 |
| q2_conservation_balanced_b12_a032 | 123 | 110 | 123 | 0 | 0.000050772 | -0.000053340 | -0.176680564 | 0.000000000 | 0.012490028 | 0.245605480 | 0.000754303 |
| q2_conservation_micro_b5_a040 | 18 | 109 | 18 | 0 | 0.000031885 | -0.000034015 | -0.176680564 | 0.000000000 | 0.029872854 | 0.161162287 | 0.001804093 |
| q2_conservation_antidote_b10_a030 | 97 | 109 | 97 | 0 | 0.000033700 | -0.000036014 | -0.176680564 | 0.000000000 | 0.011275643 | 0.168029061 | 0.000680963 |

Interpretation:

- H115's Q2 companion candidate should be treated as high-risk until public
  confirms it.
- The next equation-solver target should not be "more Q2 companion."  It
  should use the H116 positive-rescue/H088-positive bundles as forbidden
  target representations.
- If a future solver can move opposite this forbidden sector while preserving
  H057-positive row-state support, that is a cleaner public/private assignment
  candidate than guarded Q2 reopening.
