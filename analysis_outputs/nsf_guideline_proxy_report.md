# NSF Guideline Proxy Audit

Date: 2026-05-26

## Question

Can a small, interpretable proxy for the National Sleep Foundation objective metrics improve the current public-best stage2 file?

The tested mapping was deliberately narrow:

- `S1`: total sleep time proxy from quiet/screen-step duration.
- `S2`: sleep efficiency proxy from quiet fraction and in-core screen/step activity.
- `S3`: sleep onset latency proxy from quiet-window start phase and pre-sleep screen use.
- `S4`: WASO proxy from quiet fragmentation and wake-after-quiet activity.

## Evidence

Script: `nsf_guideline_proxy_audit.py`

Outputs:

- `nsf_guideline_proxy_audit.csv`
- `nsf_guideline_proxy_top_by_target.csv`
- `nsf_guideline_proxy_selected.csv`

Validation base:

- OOF: `final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy`
- Submission: `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv`

Result:

```text
tested configs        48
loose passes          0
strict passes         0
selected candidates   0
```

Best apparent row:

```text
config                 S4_waso_relative_c0p3_bal
target                 S4
stage2 S4 loss          0.603404
proxy-only S4 loss      0.705546
best blend weight       0.02
OOF delta               -0.000188
subject guard delta     +0.000582
subject guard win-rate   0.102778
geometry mean delta     -0.000187
geometry win-rate        0.625
```

## Decision

Reject as a score candidate.

The interpretable NSF proxy features are structurally meaningful, but stage2 has already absorbed the stable S-target signal. On top of stage2, `S1`, `S2`, and `S3` all choose zero blend weight. `S4` gives a tiny full-OOF improvement, but the repeated subject-half guardrail is strongly positive, which means the effect is subject-split fragile.

This is useful negative evidence: future S-target work should not add another direct guideline proxy layer to stage2. It needs either a new raw sleep-stage-like source, a public-safe projection blend, or a block-rate/state signal not already represented by quiet-window and broad residual features.
