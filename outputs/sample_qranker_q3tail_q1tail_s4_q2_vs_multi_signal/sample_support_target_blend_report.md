# Sample-support Target Blend

The blend is applied only to train/sample panel-position bins that exist in the submission sample.
Position range filter: [0.333333, 1.000001).

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.580908 | 0.580868 | 0.000039 | -0.000006 | 0.000039 | 0.000086 | 0.000142 | 0.000000 |

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
| Q2 | 124 | 250 | 216 | 250 | 0.333333 | 1.000001 | 1.000000 | logit |
