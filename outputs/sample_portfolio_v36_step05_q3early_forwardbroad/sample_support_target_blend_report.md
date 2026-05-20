# Sample-support Target Blend

The blend is applied by the explicit panel-position range, regardless of sample-support bins.
Position range filter: [0.000000, 0.333333).

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.565282 | 0.564341 | 0.000940 | -0.000630 | 0.000923 | 0.002523 | 0.001809 | 0.000000 |

## Support bins

| bin | train_count | sample_count | sample_supported |
| --- | --- | --- | --- |
| [0.000,0.333) | 234 | 0 | False |
| [0.333,0.667) | 102 | 130 | True |
| [0.667,0.800) | 92 | 0 | False |
| [0.800,1.000) | 22 | 120 | True |

## Target selection

| target | supported_train_rows | supported_sample_rows | range_train_rows | range_sample_rows | min_position | max_position | weight | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | 234 | 0 | 234 | 0 | 0.000000 | 0.333333 | 1.000000 | prob |
