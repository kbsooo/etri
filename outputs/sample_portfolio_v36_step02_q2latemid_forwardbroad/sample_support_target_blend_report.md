# Sample-support Target Blend

The blend is applied by the explicit panel-position range, regardless of sample-support bins.
Position range filter: [0.666667, 0.800000).

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.567782 | 0.566467 | 0.001315 | -0.000121 | 0.001314 | 0.002743 | 0.006432 | 0.000000 |

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
| Q2 | 92 | 0 | 92 | 0 | 0.666667 | 0.800000 | 1.000000 | prob |
