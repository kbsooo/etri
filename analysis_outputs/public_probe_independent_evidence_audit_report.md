# E35 Public Probe Independent Evidence Audit

## Observe

E32-E34 made `analysis_outputs/submission_mixmin_0c916bb4.csv` the leading high-risk probe under binary frontier-box and anchor-loss geometry. The unresolved question is whether that support is independent enough to turn the file into a normal improvement submission.

## Wonder

Is there any currently available non-public, non-anchor-derived validation source that supports mixmin strongly enough to override the pairwise/old selector veto?

## Hypothesis

H34: mixmin has enough out-of-anchor evidence for a normal submission. If true, at least one local/representation source should support it, the public selector veto should not be hard, and the anchor-loss evidence should be corroborative rather than primary.

## Method

The audit joined direction-probe metadata, focused label-flow pairwise scores, focused survival review, scale-curve scores, mixture combo stress, actual-anchor scores, binary anchor-loss bands, LOO stability, and family/null summaries. Each evidence source was tagged as local-independent-ish, local/representation, quasi-public, known-public-derived, anchor-derived, or anchor-derived robustness.

## Result

- candidates audited: `5`.
- normal submit gates passing: `0`.
- top sensor by diagnostic score: `mixmin_0c916`.
- mixmin local direction support: `yes`; honest CV mean/worst `-0.0009519634945673` / `-0.000695966348303`.
- mixmin selector hard veto: `yes`; pair p90 `0.0008791999010828`, old p90 `0.0010419327951444`.
- mixmin anchor-loss support: `yes`; low-half better_rate `1.0`, low-half max_delta `-0.0005370960828407`.
- mixmin LOO support: `yes`; LOO low-half min better_rate `1.0`, worst max_delta `-0.0003153376627865`.

## Interpretation

The audit rejects H34 as a normal-submit claim. Mixmin does have one local-independent-ish positive signal from honest CV and very strong anchor-derived support from E32-E34. But the strongest support is still built from known-public anchor geometry, while both selector families veto it on unobserved candidate deltas. Pair-only S4/Q3 sensors have local dependency-energy and pairwise support, but fail old/independent survival and are weak under binary/anchor-loss geometry.

## Decision

E35 result: normal_submit_gate remains 0. Mixmin has the strongest sensor score, but its strongest evidence is still known-public/anchor-derived rather than certification-grade independent evidence.

Submission implication: keep strict submit candidate count at 0. If a public diagnostic slot is deliberately spent, mixmin is now more information-rich than another S4/Q3 pair-only variant because it directly tests the binary/actual-anchor/anchor-loss worldview. That is a sensor decision, not a validated improvement claim.

## Outputs

- `analysis_outputs/public_probe_independent_evidence_audit_summary.csv`
- `analysis_outputs/public_probe_independent_evidence_source_inventory.csv`
