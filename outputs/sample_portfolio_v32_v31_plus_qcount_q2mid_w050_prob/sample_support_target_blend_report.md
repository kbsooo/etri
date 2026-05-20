# Sample-support Target Blend

The blend is applied only to train/sample panel-position bins that exist in the submission sample.
Position range filter: [0.333333, 0.666667).

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.571703 | 0.571554 | 0.000149 | -0.000045 | 0.000149 | 0.000346 | 0.000656 | 0.000000 |

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
| Q2 | 102 | 130 | 102 | 130 | 0.333333 | 0.666667 | 0.500000 | prob |
