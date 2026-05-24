# Axis 2 — Information hierarchy

Mirror_v1 fold family (3 seeds). Cumulative source additions left→right.
Negative Δ = adding that source helped on that target.


## 1. Cumulative mean logloss per target (mirror_v1, 3 seeds)

| source_set | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| S0_global | 0.6952 | 0.6829 | 0.6665 | 0.6286 | 0.6701 | 0.6570 | 0.6878 | 0.6697 |
| S1_subject | 0.7119 | 0.7660 | 0.7515 | 0.5851 | 0.5894 | 0.5798 | 0.6275 | 0.6587 |
| S2_calendar | 0.7137 | 0.7579 | 0.7467 | 0.5863 | 0.5922 | 0.5823 | 0.6388 | 0.6597 |
| S3_own_neighbor | 0.7184 | 0.7457 | 0.7426 | 0.5842 | 0.6203 | 0.5860 | 0.6460 | 0.6633 |
| S4_other_neighbor | 0.7365 | 0.7378 | 0.7487 | 0.6202 | 0.6268 | 0.6196 | 0.6648 | 0.6792 |
| S5_latent | 0.7402 | 0.7272 | 0.7495 | 0.6378 | 0.7891 | 0.6485 | 0.6791 | 0.7102 |
| S6_engineered | 0.8603 | 0.7732 | 0.8707 | 0.7917 | 0.8186 | 0.7163 | 0.7371 | 0.7954 |
| S7_coverage | 0.9132 | 0.7861 | 0.8878 | 0.8164 | 0.8097 | 0.7352 | 0.7605 | 0.8156 |
| S8_context_tokens | 0.9319 | 0.7924 | 0.9079 | 0.8369 | 0.8007 | 0.7430 | 0.7615 | 0.8249 |


## 2. Incremental Δlogloss when adding each source (cumulative)

WARNING: with 250 train rows, cumulative model overfits as more features are added. Use Section 3 (marginal) for the actual information contribution.

| source_set | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| S0_global | nan | nan | nan | nan | nan | nan | nan | nan |
| S1_subject | 0.0167 | 0.0831 | 0.0850 | -0.0435 | -0.0807 | -0.0772 | -0.0603 | -0.0110 |
| S2_calendar | 0.0018 | -0.0081 | -0.0048 | 0.0012 | 0.0028 | 0.0025 | 0.0113 | 0.0010 |
| S3_own_neighbor | 0.0047 | -0.0122 | -0.0041 | -0.0021 | 0.0281 | 0.0037 | 0.0072 | 0.0036 |
| S4_other_neighbor | 0.0181 | -0.0079 | 0.0061 | 0.0360 | 0.0065 | 0.0336 | 0.0188 | 0.0159 |
| S5_latent | 0.0037 | -0.0106 | 0.0008 | 0.0176 | 0.1623 | 0.0289 | 0.0143 | 0.0310 |
| S6_engineered | 0.1201 | 0.0460 | 0.1212 | 0.1539 | 0.0295 | 0.0678 | 0.0580 | 0.0852 |
| S7_coverage | 0.0529 | 0.0129 | 0.0171 | 0.0247 | -0.0089 | 0.0189 | 0.0234 | 0.0202 |
| S8_context_tokens | 0.0187 | 0.0063 | 0.0201 | 0.0205 | -0.0090 | 0.0078 | 0.0010 | 0.0093 |


## 3. Marginal Δlogloss vs (S0+S1) anchor — each source added ALONE

This is the clean information-contribution table. Each row = (anchor + that source). Negative = that source has real signal on top of (global + subject). Positive = adding that source on top of (global + subject) hurts (likely overfit or signal absorbed by S1).

| source_set | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| S2_calendar | 0.0018 | -0.0081 | -0.0048 | 0.0012 | 0.0028 | 0.0025 | 0.0113 | 0.0010 |
| S3_own_neighbor | 0.0073 | -0.0107 | -0.0027 | -0.0032 | 0.0236 | 0.0023 | 0.0008 | 0.0025 |
| S4_other_neighbor | 0.0134 | -0.0098 | -0.0017 | 0.0233 | 0.0308 | 0.0404 | 0.0141 | 0.0158 |
| S5_latent | 0.0067 | 0.0066 | 0.0114 | 0.0212 | 0.1753 | 0.0150 | 0.0038 | 0.0343 |
| S6_engineered | 0.0865 | 0.0521 | 0.1082 | 0.1160 | 0.0776 | 0.0792 | 0.0552 | 0.0821 |
| S7_coverage | 0.0535 | -0.0180 | 0.0065 | 0.0315 | 0.0107 | 0.0189 | 0.0361 | 0.0199 |
| S8_context_tokens | 0.0188 | 0.0028 | 0.0023 | 0.0009 | 0.0049 | 0.0147 | 0.0028 | 0.0067 |


## 3. Dominant source per target (largest single Δ)

|  | dominant_source |
|---|---|
| Q1 | S2_calendar (+0.0018) |
| Q2 | S3_own_neighbor (-0.0122) |
| Q3 | S2_calendar (-0.0048) |
| S1 | S1_subject (-0.0435) |
| S2 | S1_subject (-0.0807) |
| S3 | S1_subject (-0.0772) |
| S4 | S1_subject (-0.0603) |


## 4. Fold-to-fold std on the full-stack model (CI proxy)

Any Δ inside this std is not a real improvement.


| target | std_ll |
|---|---|
| Q1 | 0.0833 |
| Q2 | 0.0424 |
| Q3 | 0.0754 |
| S1 | 0.0464 |
| S2 | 0.1069 |
| S3 | 0.0561 |
| S4 | 0.0639 |