# Sample-support Target Blend

The blend is applied by the explicit panel-position range, regardless of sample-support bins.
Position range filter: [0.800000, 1.000001).

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.563751 | 0.563697 | 0.000055 | -0.000736 | 0.000076 | 0.000732 | 0.001117 | 0.000000 |

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
| Q3 | 22 | 120 | 22 | 120 | 0.800000 | 1.000001 | 1.000000 | prob |
