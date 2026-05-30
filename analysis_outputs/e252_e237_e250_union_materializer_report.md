# E252 E237/E250 Union Materializer

## Question

Can the E251 union of E237 and E250 Q3 rollback cells be preserved as an exact, schema-clean public sensor?

## Artifact

- submission: `analysis_outputs/submission_e252_e237_e250_union_q3top31_67707aef.csv`
- SHA256: `5da8e3c9dbe79b62c18b3372fd542ca98369d66f225617356dc335ff1a49a58c`
- E237 cells: `25`
- E250 cells: `21`
- shared cells: `15`
- union cells: `31`

## Schema Audit

| check | ok | value |
| --- | --- | --- |
| shape | True | (250, 10) |
| columns | True | subject_id,sleep_date,lifelog_date,Q1,Q2,Q3,S1,S2,S3,S4 |
| key_order | True | exact_sample_order |
| finite | True | finite |
| prob_min | True | 0.068110176672 |
| prob_max | True | 0.979776651464 |

## Movement Audit

| target | changed_cells_vs_e224 | abs_logit_sum | max_abs_logit_delta |
| --- | --- | --- | --- |
| Q1 | 0 | 0.000000000 | 0.000000000 |
| Q2 | 0 | 0.000000000 | 0.000000000 |
| Q3 | 31 | 2.847757568 | 0.172092355 |
| S1 | 0 | 0.000000000 | 0.000000000 |
| S2 | 0 | 0.000000000 | 0.000000000 |
| S3 | 0 | 0.000000000 | 0.000000000 |
| S4 | 0 | 0.000000000 | 0.000000000 |

## Decision

- The file is a clean E251 union artifact. It is not OOF-certified as a standalone selector.
- Submit only if the explicit question is whether E237 and E250 feature-NN/context cell sets are complementary on public.
- For likely score without that question, keep E237 first.
