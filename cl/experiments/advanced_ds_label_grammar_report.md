# Advanced Label Grammar & Conditional Dynamics

## 1. Exact 7-bit label grammar

pattern  n  share  dominant_state  state_purity  subjects
1111111 37  0.082               2         1.000         9
0111111 24  0.053               1         1.000         6
0001111 20  0.044               1         1.000         4
1001111 17  0.038               2         1.000         7
1011111 15  0.033               2         1.000         7
1111101 14  0.031               2         1.000         7
0110010 11  0.024               0         1.000         6
1101111 11  0.024               2         1.000         6
1111110 11  0.024               2         1.000         6
0000111 11  0.024               1         1.000         5
0011111 10  0.022               1         1.000         5
0110111 10  0.022               1         1.000         5
1111000  9  0.020               0         1.000         3
0001110  8  0.018               1         1.000         6
0010010  8  0.018               0         1.000         5
0100111  8  0.018               1         1.000         2

## 2. Pairwise label dependence: raw vs conditioned

 a  b  raw_mi_bits  cmi_given_latent_state_bits  fraction_remaining_after_state  cmi_given_S2_bits  fraction_remaining_after_S2
S2 S4       0.1704                       0.0012                          0.0070                NaN                          NaN
S2 S3       0.1106                       0.0011                          0.0101                NaN                          NaN
S1 S2       0.1031                       0.0001                          0.0006                NaN                          NaN
Q1 S1       0.0982                       0.0416                          0.4241             0.1038                       1.0570
Q2 Q3       0.0845                       0.0751                          0.8893             0.0845                       1.0003
Q1 Q2       0.0108                       0.0183                          1.6965             0.0111                       1.0296
Q1 S3       0.0103                       0.0177                          1.7272             0.0191                       1.8652
S1 S3       0.0099                       0.0017                          0.1768             0.0042                       0.4215
S1 S4       0.0082                       0.0043                          0.5284             0.0067                       0.8209
Q1 Q3       0.0075                       0.0101                          1.3506             0.0083                       1.1155
S3 S4       0.0054                       0.0591                         11.0230             0.0498                       9.2818
Q1 S2       0.0038                       0.0003                          0.0750                NaN                          NaN
Q3 S1       0.0031                       0.0046                          1.4564             0.0073                       2.3178
Q2 S3       0.0020                       0.0008                          0.4102             0.0033                       1.6686

Interpretation: if raw MI is high but CMI given latent_state collapses, the relation is mostly common latent-state, not necessarily direct target-target causality. If CMI remains high, there is residual pair-specific structure.

## 3. Neighbor interpolation grammar

target  p_y1_given_00  p_y1_given_11  p_y1_given_conflict_avg  agree_neighbor_spread  conflict_midpoint_bias
    Q3          0.244          0.777                    0.586                  0.534                   0.076
    Q2          0.234          0.739                    0.593                  0.505                   0.106
    Q1          0.294          0.716                    0.498                  0.421                  -0.007
    S3          0.420          0.797                    0.584                  0.377                  -0.025
    S1          0.438          0.801                    0.614                  0.363                  -0.005
    S4          0.337          0.669                    0.589                  0.332                   0.086
    S2          0.507          0.762                    0.592                  0.255                  -0.043

## 4. Persistence summary

    variable  mean_same_next_rate   std
          Q2                0.655 0.114
          Q3                0.649 0.088
          S3                0.645 0.171
          S1                0.645 0.126
          Q1                0.619 0.115
          S2                0.615 0.184
          S4                0.588 0.097
latent_state                0.461 0.150

## 5. Output files

- `experiments/advanced_ds_label_pattern_grammar.csv`
- `experiments/advanced_ds_label_conditional_mi.csv`
- `experiments/advanced_ds_neighbor_dynamics_rows.csv`
- `experiments/advanced_ds_neighbor_interpolation_table.csv`
- `experiments/advanced_ds_neighbor_interpolation_strength.csv`
- `experiments/advanced_ds_persistence_by_subject.csv`
- `experiments/advanced_ds_persistence_summary.csv`
