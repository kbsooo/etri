# Boundary Consensus Audit

## Decision

Boundary-consensus is not promoted as a score candidate. Apparent same-boundary gains do not survive enough nested target-wise validation to outrank existing public-safe probes.

## Base Losses

```csv
base,mean,Q1,Q2,Q3,S1,S2,S3,S4
stage2,0.567531,0.574631,0.642999,0.630348,0.478943,0.538953,0.503438,0.603404
public2d0,0.561702,0.571993,0.633169,0.61647,0.473598,0.53654,0.500358,0.599785
proj0,0.562144,0.572196,0.633291,0.617797,0.474099,0.536773,0.50075,0.600098
minimax,0.554332,0.564572,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
```

## Best Apparent Weight Scans

```csv
base,mode,scheme,weights,mean,delta_vs_base,Q1,Q2,Q3,S1,S2,S3,S4
minimax,zeros_only,target_best_apparent,Q1:0.1|Q2:0.3|Q3:0|S1:0.1|S2:0|S3:0.01|S4:0,0.553996,-0.000337,0.564307,0.630749,0.601563,0.466342,0.531352,0.490824,0.592832
minimax,same_or_single,target_best_apparent,Q1:0|Q2:0|Q3:0.035|S1:0|S2:0.02|S3:0|S4:0.1,0.554163,-0.000169,0.564572,0.632552,0.601284,0.46663,0.531336,0.490826,0.591941
minimax,ones_only,target_best_apparent,Q1:0.075|Q2:0|Q3:0.1|S1:0|S2:0.05|S3:0|S4:0,0.554171,-0.000161,0.564293,0.632552,0.600769,0.46663,0.531293,0.490826,0.592832
minimax,same,target_best_apparent,Q1:0.1|Q2:0|Q3:0|S1:0|S2:0|S3:0|S4:0,0.554256,-7.7e-05,0.564034,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
minimax,zeros_only,global_weight,0.01,0.554329,-4e-06,0.564524,0.632422,0.601692,0.466581,0.531413,0.490824,0.592845
minimax,zeros_only,global_weight,0.02,0.55433,-2e-06,0.564481,0.632297,0.601829,0.466537,0.531477,0.490827,0.592863
minimax,same,global_weight,0,0.554332,0.0,0.564572,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
minimax,same_or_single,global_weight,0,0.554332,0.0,0.564572,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
minimax,ones_only,global_weight,0,0.554332,0.0,0.564572,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
minimax,zeros_only,global_weight,0,0.554332,0.0,0.564572,0.632552,0.601563,0.46663,0.531352,0.490826,0.592832
minimax,zeros_only,global_weight,0.035,0.554342,1e-05,0.564425,0.632119,0.60205,0.466478,0.531582,0.490838,0.592901
minimax,zeros_only,global_weight,0.05,0.554365,3.3e-05,0.56438,0.631952,0.602288,0.46643,0.531696,0.490858,0.592952
```

## Nested Mean Rows

```csv
base,mode,target,base_loss,nested_loss,delta
stage2,zeros_only,mean,0.567531,0.567797,0.000266
proj0,zeros_only,mean,0.562144,0.562472,0.000328
public2d0,zeros_only,mean,0.561702,0.562036,0.000334
minimax,zeros_only,mean,0.554332,0.554762,0.00043
stage2,ones_only,mean,0.567531,0.56844,0.000909
proj0,ones_only,mean,0.562144,0.563131,0.000988
minimax,ones_only,mean,0.554332,0.555324,0.000991
public2d0,ones_only,mean,0.561702,0.562695,0.000993
stage2,same,mean,0.567531,0.568688,0.001157
proj0,same,mean,0.562144,0.56348,0.001337
public2d0,same,mean,0.561702,0.563047,0.001345
minimax,same,mean,0.554332,0.55573,0.001398
minimax,same_or_single,mean,0.554332,0.556207,0.001875
stage2,same_or_single,mean,0.567531,0.56951,0.00198
public2d0,same_or_single,mean,0.561702,0.563724,0.002022
proj0,same_or_single,mean,0.562144,0.564166,0.002022
```

## Actual Submission Boundary Exposure

```csv
target,diff01,diff10,prev0,prev1,same0,same1
Q1,35,24,31,63,64,33
Q2,36,21,28,66,31,68
Q3,14,57,13,81,28,57
S1,31,11,13,81,36,78
S2,3,31,36,58,36,86
S3,13,19,19,75,17,107
S4,10,77,36,58,29,40
```