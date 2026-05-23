# Deeper Label Information Hierarchy

## 1. Per-target information sources

Higher info_gain_bits means that source reduces more uncertainty about the target. Some sources are oracle-like diagnostics, not submission-safe.

target                source  H_y_bits  H_y_given_source_bits  info_gain_bits  explained_entropy_share  n_groups
    Q1          latent_state     1.000                  0.562           0.438                    0.438         3
    Q1         subject+state     1.000                  0.563           0.437                    0.437        30
    Q1      subject+prevnext     1.000                  0.859           0.141                    0.141        58
    Q1 same_row_other_labels     1.000                  0.865           0.135                    0.135        53
    Q1          prevnext+gap     1.000                  0.918           0.082                    0.082        19
    Q1              prevnext     1.000                  0.919           0.081                    0.081         8
    Q2        Q2Q3_pair_axis     0.989                  0.802           0.187                    0.189        16
    Q2      subject+prevnext     0.989                  0.808           0.181                    0.183        60
    Q2          prevnext+gap     0.989                  0.868           0.121                    0.123        20
    Q2 same_row_other_labels     0.989                  0.871           0.117                    0.119        53
    Q2              prevnext     0.989                  0.872           0.117                    0.118         8
    Q2         subject+state     0.989                  0.874           0.115                    0.116        30
    Q3        Q2Q3_pair_axis     0.971                  0.801           0.170                    0.175        15
    Q3      subject+prevnext     0.971                  0.831           0.140                    0.144        60
    Q3 same_row_other_labels     0.971                  0.855           0.116                    0.119        53
    Q3              prevnext     0.971                  0.864           0.106                    0.110         8
    Q3          prevnext+gap     0.971                  0.866           0.105                    0.108        21
    Q3         subject+state     0.971                  0.885           0.086                    0.089        30
    S1         subject+state     0.902                  0.562           0.340                    0.377        30
    S1          latent_state     0.902                  0.675           0.227                    0.252         3
    S1 same_row_other_labels     0.902                  0.687           0.215                    0.238        57
    S1      subject+prevnext     0.902                  0.772           0.130                    0.144        57
    S1            subject_id     0.902                  0.801           0.101                    0.112        10
    S1          prevnext+gap     0.902                  0.845           0.057                    0.063        19
    S2          latent_state     0.933                  0.046           0.887                    0.951         3
    S2         subject+state     0.933                  0.181           0.752                    0.806        30
    S2 same_row_other_labels     0.933                  0.588           0.345                    0.370        62
    S2      subject+prevnext     0.933                  0.746           0.187                    0.201        58
    S2            subject_id     0.933                  0.801           0.132                    0.142        10
    S2          prevnext+gap     0.933                  0.885           0.048                    0.051        20
    S3         subject+state     0.923                  0.675           0.248                    0.269        30
    S3      subject+prevnext     0.923                  0.731           0.191                    0.207        57
    S3            subject_id     0.923                  0.745           0.178                    0.193        10
    S3 same_row_other_labels     0.923                  0.768           0.155                    0.168        59
    S3          latent_state     0.923                  0.778           0.144                    0.156         3
    S3          prevnext+gap     0.923                  0.856           0.066                    0.072        20
    S4         subject+state     0.990                  0.743           0.247                    0.249        30
    S4 same_row_other_labels     0.990                  0.801           0.188                    0.190        59
    S4          latent_state     0.990                  0.812           0.178                    0.180         3
    S4      subject+prevnext     0.990                  0.865           0.125                    0.126        60
    S4            subject_id     0.990                  0.899           0.091                    0.092        10
    S4          prevnext+gap     0.990                  0.938           0.052                    0.052        20

## 2. Source synergy

extra_over_best_single_bits > 0 means the pair adds structure beyond the stronger single source.

target source_a     source_b  joint_info_bits  max_single_info_bits  extra_over_best_single_bits  n_groups
    Q1  subject other_labels            0.252                 0.135                        0.117       203
    Q1 prevnext other_labels            0.202                 0.135                        0.067       172
    Q1  subject     prevnext            0.141                 0.081                        0.060        58
    Q1    state     prevnext            0.446                 0.438                        0.008        22
    Q2  subject other_labels            0.235                 0.117                        0.118       205
    Q2 prevnext other_labels            0.200                 0.117                        0.082       164
    Q2  subject     prevnext            0.181                 0.117                        0.064        60
    Q2  subject        state            0.115                 0.056                        0.059        30
    Q3  subject other_labels            0.229                 0.116                        0.113       202
    Q3 prevnext other_labels            0.222                 0.116                        0.107       161
    Q3  subject        state            0.086                 0.043                        0.043        30
    Q3  subject     prevnext            0.140                 0.106                        0.033        60
    S1  subject        state            0.340                 0.227                        0.113        30
    S1  subject other_labels            0.280                 0.215                        0.065       222
    S1    state other_labels            0.260                 0.227                        0.033        63
    S1    state     prevnext            0.258                 0.227                        0.031        21
    S2  subject     prevnext            0.187                 0.132                        0.055        58
    S2 prevnext other_labels            0.322                 0.345                       -0.023       189
    S2  subject other_labels            0.298                 0.345                       -0.047       230
    S2    state     prevnext            0.808                 0.887                       -0.079        21
    S3  subject        state            0.248                 0.178                        0.070        30
    S3  subject other_labels            0.235                 0.178                        0.057       210
    S3 prevnext other_labels            0.208                 0.155                        0.054       165
    S3    state other_labels            0.194                 0.155                        0.039        63
    S4  subject        state            0.247                 0.178                        0.069        30
    S4  subject other_labels            0.240                 0.188                        0.052       211
    S4    state other_labels            0.230                 0.188                        0.041        62
    S4  subject     prevnext            0.125                 0.091                        0.034        60

## 3. Interpretation guide

- `same_row_other_labels` high: target is mostly part of a multi-label grammar/common state.
- `prevnext` high: interpolation target.
- `subject_id` high: stable person-specific prevalence dominates.
- `state` high but feature state-pred weak: labels have grammar but current sensors do not recover it well.
- `extra_over_best_single` high for subject+prevnext: temporal behavior is personalized, not globally shared.

## 4. Output files

- `experiments/deeper_label_information_hierarchy.csv`
- `experiments/deeper_label_information_synergy.csv`
