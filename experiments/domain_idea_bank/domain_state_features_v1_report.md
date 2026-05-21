# Domain State Features v1

## Goal

Convert the 300 imported data-engineering ideas into a traceable feature bank focused on behavioral-day state rather than raw sensor totals.

## Implemented Families

- Day/time slicing proxies from existing night/evening/prebed/sleep-window columns.
- Subject-relative routine rupture via median/MAD residuals.
- 3/7/14/28-day past-only rolling deltas and z-scores.
- Episode/missingness features from the 30-minute event-hybrid token grid.
- Cross-modal contradiction features such as phone-active while not moving and moving while phone-silent.
- App/place entropy and prebed usage ratios.
- Unsupervised motif cluster distances over the domain-state feature space.

## Output

- Feature path: `artifacts/domain_state_features_v1.parquet`
- Shape: `700 x 2006`
- Numeric features: `2002`
- Parsed ideas: `340`