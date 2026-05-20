# Sample-support Target Blend

The blend is applied only to train/sample panel-position bins that exist in the submission sample.

## Summary

| base_avg | final_avg | improvement | p025 | p500 | p975 | support_delta | non_support_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.581592 | 0.581445 | 0.000148 | -0.000074 | 0.000148 | 0.000374 | 0.000536 | 0.000000 |

## Support bins

| bin | train_count | sample_count | sample_supported |
| --- | --- | --- | --- |
| [0.000,0.333) | 234 | 0 | False |
| [0.333,0.667) | 102 | 130 | True |
| [0.667,0.800) | 92 | 0 | False |
| [0.800,1.000) | 22 | 120 | True |

## Target selection

| target | supported_train_rows | supported_sample_rows | weight | mode |
| --- | --- | --- | --- | --- |
| S4 | 124 | 250 | 1.000000 | logit |
