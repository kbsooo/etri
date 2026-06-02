# H066 State-Sequence Episode-Route HS-JEPA

Question: is H057's hidden human state generated as independent rows, or as a
subject-level episode sequence with pre/bridge/post target routes?

Design:

- base: H057 public frontier;
- context: H057 seed rows, H064/H065 state graph, H062/H063 expansion
  agreement;
- target representation: H061 post-H057 posterior `q061`;
- sequence model: cluster H057 seeds within each subject, score candidate
  pre/bridge/post rows around each cluster, then select high-energy episodes;
- action: freeze Q2 and move only state-route non-Q2 targets.

Summary:

| candidate_count | persisted_candidate_files | promoted_file | promoted_candidate | promoted_selected_rows | promoted_selected_episodes | promoted_changed_cells | promoted_posterior_delta | promoted_new_rows_vs_h065 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 410 | 120 | submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv | h066_seq_gap4_r8_e0p56_m18_row_top4_a1p0_logit_8ca9b9b6 | 63 | 18 | 252 | -0.000328325 | 39 |

Decision:

| candidate_id | core_gap | radius | min_emission | max_episodes | alpha | mode | route_rule | selected_rows | selected_row_count | selected_episode_count | selected_subjects | changed_cells_vs_h057 | changed_rows_vs_h057 | q2_changed_vs_h057 | posterior_delta_vs_h057 | mean_episode_score | mean_row_emission | mean_segment_distance | pre_rows | bridge_rows | post_rows | phase_balance | bridge_rate | h050_null_rows_selected | h064_overlap_rows | h065_overlap_rows | new_rows_vs_h065 | mean_targets_per_row | mean_route_size | target_specificity | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | hash | posterior_rank | episode_rank | emission_rank | new_row_rate | overlap_strength | size_score | episode_size_score | h066_score | file | resolved_path | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | q2_changed_vs_h057_validation | upload_safe | root_uploadsafe_path | decision | worldview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a1p0_logit_8ca9b9b6 | 4 | 8 | 0.560000000 | 18 | 1.000000000 | logit | row_top4 | 2,5,6,8,38,40,53,54,55,57,62,66,71,73,74,75,84,87,89,92,99,104,113,122,124,128,129,131,132,133,137,138,140,142,145,147,153,154,159,162,189,192,195,199,204,205,206,214,215,217,219,221,222,224,228,229,236,239,244,245,246,247,249 | 63 | 18 | 10 | 252 | 63 | 0 | -0.000328325 | 0.932518465 | 0.735130794 | 3.190476190 | 17 | 10 | 36 | 0.320754717 | 0.158730159 | 0 | 34 | 24 | 39 | 4.000000000 | 4.000000000 | 1.000000000 | 38 | 0 | 38 | 37 | 44 | 46 | 49 | 8ca9b9b6 | 0.919512195 | 0.800000000 | 0.702439024 | 0.619047619 | 0.460317460 | 0.850000000 | 0.887500000 | 0.785496591 | submission_h066_seq_gap4_r8_e0p56_m18_row_top4_a1p0_logit_8ca9b9b6.csv | /Users/kbsoo/Downloads/cl2/hitl/h066_state_sequence_episode_route_jepa/submission_h066_seq_gap4_r8_e0p56_m18_row_top4_a1p0_logit_8ca9b9b6.csv | /Users/kbsoo/Downloads/cl2/submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999999000 | 0 | True | /Users/kbsoo/Downloads/cl2/submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv | promote_state_sequence_episode_route_sensor | H057 state is generated as a subject-level episode sequence with pre/bridge/post target routes, not independent row selections |

Selected Episodes:

| cluster_id | subject_id | start_row | end_row | seed_count | selected_candidate_rows | episode_score | pre_rows | bridge_rows | post_rows | h064_overlap_rows | h065_overlap_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id06_135_151 | id06 | 135 | 151 | 10 | 11 | 1.127498182 | 5 | 6 | 0 | 8 | 7 |
| id07_163_168 | id07 | 163 | 168 | 4 | 2 | 1.117580000 | 2 | 0 | 0 | 2 | 2 |
| id04_91_103 | id04 | 91 | 103 | 6 | 6 | 1.029246667 | 3 | 2 | 1 | 4 | 1 |
| id03_61_61 | id03 | 61 | 61 | 1 | 2 | 1.007280000 | 0 | 0 | 2 | 2 | 1 |
| id03_70_70 | id03 | 70 | 70 | 1 | 6 | 0.986173333 | 2 | 0 | 4 | 4 | 3 |
| id07_158_158 | id07 | 158 | 158 | 1 | 4 | 0.971970000 | 2 | 0 | 2 | 3 | 3 |
| id10_242_242 | id10 | 242 | 242 | 1 | 7 | 0.928045714 | 2 | 0 | 5 | 4 | 2 |
| id02_44_50 | id02 | 44 | 50 | 3 | 6 | 0.909533333 | 2 | 0 | 4 | 2 | 2 |
| id07_152_152 | id07 | 152 | 152 | 1 | 3 | 0.903826667 | 0 | 0 | 3 | 2 | 2 |
| id09_216_216 | id09 | 216 | 216 | 1 | 7 | 0.902777143 | 2 | 0 | 5 | 3 | 2 |
| id03_78_78 | id03 | 78 | 78 | 1 | 4 | 0.895620000 | 4 | 0 | 0 | 2 | 2 |
| id09_225_226 | id09 | 225 | 226 | 2 | 5 | 0.895168000 | 5 | 0 | 0 | 2 | 1 |
| id08_194_196 | id08 | 194 | 196 | 2 | 4 | 0.891730000 | 2 | 1 | 1 | 2 | 1 |
| id02_56_56 | id02 | 56 | 56 | 1 | 4 | 0.879640000 | 3 | 0 | 1 | 2 | 2 |
| id09_203_203 | id09 | 203 | 203 | 1 | 3 | 0.847866667 | 0 | 0 | 3 | 1 | 1 |
| id10_235_235 | id10 | 235 | 235 | 1 | 4 | 0.834580000 | 2 | 0 | 2 | 2 | 1 |
| id05_121_121 | id05 | 121 | 121 | 1 | 3 | 0.833986667 | 1 | 0 | 2 | 1 | 1 |
| id01_0_3 | id01 | 0 | 3 | 2 | 4 | 0.822810000 | 0 | 1 | 3 | 1 | 1 |

Selected Rows:

| row | subject_id | sleep_date | sequence_state | cluster_id | segment_distance | h066_emission | episode_row_score | h064_changed_row_validation | h065_changed_row | h062_changed_row | h063_changed_row |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | id01 | 2024-08-02 | bridge | id01_0_3 | 0 | 0.832320000 | 0.972320000 | 1 | 1 | 0 | 1 |
| 5 | id01 | 2024-08-06 | post | id01_0_3 | 2 | 0.613240000 | 0.603240000 | 0 | 0 | 0 | 1 |
| 6 | id01 | 2024-08-07 | post | id01_0_3 | 3 | 0.649560000 | 0.634560000 | 0 | 0 | 0 | 1 |
| 8 | id01 | 2024-08-10 | post | id01_0_3 | 5 | 0.546120000 | 0.521120000 | 0 | 0 | 0 | 1 |
| 38 | id02 | 2024-09-06 | pre | id02_44_50 | 6 | 0.732200000 | 0.702200000 | 0 | 0 | 1 | 0 |
| 40 | id02 | 2024-09-08 | pre | id02_44_50 | 4 | 0.496440000 | 0.476440000 | 0 | 0 | 0 | 1 |
| 53 | id02 | 2024-10-10 | post | id02_44_50 | 3 | 0.823640000 | 0.948640000 | 1 | 1 | 0 | 1 |
| 54 | id02 | 2024-10-12 | post | id02_44_50 | 4 | 0.883880000 | 1.003880000 | 1 | 1 | 1 | 1 |
| 55 | id02 | 2024-10-13 | post | id02_44_50 | 5 | 0.660560000 | 0.635560000 | 0 | 0 | 0 | 1 |
| 57 | id02 | 2024-10-15 | post | id02_44_50 | 7 | 0.465480000 | 0.430480000 | 0 | 0 | 0 | 1 |
| 62 | id03 | 2024-08-20 | post | id03_61_61 | 1 | 0.851680000 | 0.986680000 | 1 | 1 | 1 | 0 |
| 66 | id03 | 2024-08-25 | post | id03_61_61 | 5 | 0.832880000 | 0.887880000 | 1 | 0 | 1 | 1 |
| 71 | id03 | 2024-09-17 | post | id03_70_70 | 1 | 0.929760000 | 1.064760000 | 1 | 1 | 1 | 1 |
| 73 | id03 | 2024-09-19 | post | id03_70_70 | 3 | 0.659440000 | 0.644440000 | 0 | 0 | 0 | 0 |
| 74 | id03 | 2024-09-21 | post | id03_70_70 | 4 | 0.634440000 | 0.614440000 | 0 | 0 | 0 | 0 |
| 75 | id03 | 2024-09-22 | post | id03_70_70 | 5 | 0.733840000 | 0.848840000 | 1 | 1 | 0 | 1 |
| 84 | id04 | 2024-09-15 | pre | id04_91_103 | 7 | 0.629680000 | 0.674680000 | 1 | 0 | 0 | 1 |
| 87 | id04 | 2024-09-20 | pre | id04_91_103 | 4 | 0.818920000 | 0.878920000 | 1 | 0 | 1 | 0 |
| 89 | id04 | 2024-09-23 | pre | id04_91_103 | 2 | 0.600000000 | 0.590000000 | 0 | 0 | 0 | 0 |
| 92 | id04 | 2024-09-26 | bridge | id04_91_103 | 0 | 0.821120000 | 0.901120000 | 1 | 0 | 1 | 0 |
| 99 | id04 | 2024-10-20 | bridge | id04_91_103 | 0 | 0.953480000 | 1.093480000 | 1 | 1 | 1 | 1 |
| 104 | id04 | 2024-10-28 | post | id04_91_103 | 1 | 0.602280000 | 0.597280000 | 0 | 0 | 0 | 0 |
| 113 | id05 | 2024-10-07 | pre | id05_121_121 | 8 | 0.731120000 | 0.691120000 | 0 | 0 | 0 | 1 |
| 122 | id05 | 2024-11-14 | post | id05_121_121 | 1 | 0.650400000 | 0.645400000 | 0 | 0 | 0 | 1 |
| 124 | id05 | 2024-11-17 | post | id05_121_121 | 3 | 0.770440000 | 0.895440000 | 1 | 1 | 1 | 0 |
| 128 | id06 | 2024-07-07 | pre | id06_135_151 | 7 | 0.816520000 | 0.861520000 | 1 | 0 | 1 | 1 |
| 129 | id06 | 2024-07-08 | pre | id06_135_151 | 6 | 0.620480000 | 0.590480000 | 0 | 0 | 0 | 0 |
| 131 | id06 | 2024-07-10 | pre | id06_135_151 | 4 | 0.596880000 | 0.576880000 | 0 | 0 | 0 | 1 |
| 132 | id06 | 2024-07-11 | pre | id06_135_151 | 3 | 0.899320000 | 1.024320000 | 1 | 1 | 1 | 1 |
| 133 | id06 | 2024-07-12 | pre | id06_135_151 | 2 | 0.856440000 | 0.986440000 | 1 | 1 | 0 | 1 |
| 137 | id06 | 2024-07-17 | bridge | id06_135_151 | 0 | 0.619560000 | 0.619560000 | 0 | 0 | 0 | 0 |
| 138 | id06 | 2024-07-18 | bridge | id06_135_151 | 0 | 1.003120000 | 1.143120000 | 1 | 1 | 1 | 1 |
| 140 | id06 | 2024-07-21 | bridge | id06_135_151 | 0 | 0.894520000 | 1.034520000 | 1 | 1 | 0 | 1 |
| 142 | id06 | 2024-08-12 | bridge | id06_135_151 | 0 | 0.715160000 | 0.855160000 | 1 | 1 | 0 | 1 |
| 145 | id06 | 2024-08-15 | bridge | id06_135_151 | 0 | 0.840600000 | 0.980600000 | 1 | 1 | 0 | 1 |
| 147 | id06 | 2024-08-21 | bridge | id06_135_151 | 0 | 0.949880000 | 1.089880000 | 1 | 1 | 0 | 1 |
| 153 | id07 | 2024-07-15 | post | id07_152_152 | 1 | 0.638000000 | 0.633000000 | 0 | 0 | 0 | 0 |
| 154 | id07 | 2024-07-16 | post | id07_152_152 | 2 | 0.799720000 | 0.929720000 | 1 | 1 | 1 | 1 |
| 159 | id07 | 2024-07-21 | post | id07_152_152 | 7 | 0.773760000 | 0.878760000 | 1 | 1 | 0 | 1 |
| 162 | id07 | 2024-07-24 | post | id07_158_158 | 4 | 0.886400000 | 1.006400000 | 1 | 1 | 1 | 1 |
| 189 | id08 | 2024-08-11 | pre | id08_194_196 | 5 | 0.595680000 | 0.650680000 | 1 | 0 | 0 | 1 |
| 192 | id08 | 2024-09-05 | pre | id08_194_196 | 2 | 0.670440000 | 0.660440000 | 0 | 0 | 0 | 1 |
| 195 | id08 | 2024-09-10 | bridge | id08_194_196 | 0 | 0.977520000 | 1.117520000 | 1 | 1 | 1 | 1 |
| 199 | id08 | 2024-09-18 | post | id08_194_196 | 3 | 0.593280000 | 0.578280000 | 0 | 0 | 0 | 0 |
| 204 | id09 | 2024-08-09 | post | id09_203_203 | 1 | 0.583840000 | 0.578840000 | 0 | 0 | 0 | 0 |
| 205 | id09 | 2024-08-10 | post | id09_203_203 | 2 | 0.975680000 | 1.105680000 | 1 | 1 | 1 | 1 |
| 206 | id09 | 2024-08-11 | post | id09_203_203 | 3 | 0.604080000 | 0.589080000 | 0 | 0 | 0 | 0 |
| 214 | id09 | 2024-08-21 | pre | id09_216_216 | 2 | 0.907400000 | 1.037400000 | 1 | 1 | 1 | 1 |
| 215 | id09 | 2024-09-05 | pre | id09_216_216 | 1 | 0.566200000 | 0.561200000 | 0 | 0 | 0 | 0 |
| 217 | id09 | 2024-09-08 | post | id09_216_216 | 1 | 0.653600000 | 0.648600000 | 0 | 0 | 0 | 0 |
| 219 | id09 | 2024-09-10 | post | id09_216_216 | 3 | 0.725320000 | 0.710320000 | 0 | 0 | 1 | 0 |
| 221 | id09 | 2024-09-13 | post | id09_216_216 | 5 | 0.840160000 | 0.895160000 | 1 | 0 | 1 | 1 |
| 222 | id09 | 2024-09-14 | post | id09_216_216 | 6 | 0.741760000 | 0.851760000 | 1 | 1 | 0 | 1 |
| 224 | id09 | 2024-09-19 | post | id09_216_216 | 8 | 0.605000000 | 0.565000000 | 0 | 0 | 0 | 0 |
| 228 | id10 | 2024-08-05 | pre | id10_235_235 | 7 | 0.738320000 | 0.783320000 | 1 | 0 | 1 | 0 |
| 229 | id10 | 2024-08-06 | pre | id10_235_235 | 6 | 0.545360000 | 0.515360000 | 0 | 0 | 1 | 0 |
| 236 | id10 | 2024-08-19 | post | id10_235_235 | 1 | 0.953280000 | 1.088280000 | 1 | 1 | 1 | 1 |
| 239 | id10 | 2024-09-16 | post | id10_235_235 | 4 | 0.531360000 | 0.511360000 | 0 | 0 | 0 | 1 |
| 244 | id10 | 2024-09-21 | post | id10_242_242 | 2 | 0.907800000 | 1.037800000 | 1 | 1 | 1 | 0 |
| 245 | id10 | 2024-09-22 | post | id10_242_242 | 3 | 0.686880000 | 0.671880000 | 0 | 0 | 0 | 1 |
| 246 | id10 | 2024-09-23 | post | id10_242_242 | 4 | 0.815880000 | 0.875880000 | 1 | 0 | 1 | 1 |
| 247 | id10 | 2024-09-25 | post | id10_242_242 | 5 | 0.597840000 | 0.572840000 | 0 | 0 | 1 | 0 |
| 249 | id10 | 2024-09-27 | post | id10_242_242 | 7 | 0.663280000 | 0.708280000 | 1 | 0 | 1 | 0 |

Top candidates:

| candidate_id | core_gap | radius | min_emission | max_episodes | route_rule | selected_row_count | selected_episode_count | changed_cells_vs_h057 | posterior_delta_vs_h057 | new_rows_vs_h065 | h064_overlap_rows | h065_overlap_rows | phase_balance | h066_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a1p0_logit_8ca9b9b6 | 4 | 8 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000328325 | 39 | 34 | 24 | 0.320754717 | 0.785496591 |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a1p15_logit_b36501be | 4 | 8 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000321470 | 39 | 34 | 24 | 0.320754717 | 0.781545371 |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a1p15_prob_f080c476 | 4 | 8 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000316391 | 39 | 34 | 24 | 0.320754717 | 0.778033176 |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a0p75_logit_ed95ed3c | 4 | 8 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000308951 | 39 | 34 | 24 | 0.320754717 | 0.771447810 |
| h066_seq_gap4_r8_e0p56_m18_row_top4_a0p75_prob_f4c43e56 | 4 | 8 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000304706 | 39 | 34 | 24 | 0.320754717 | 0.767057566 |
| h066_seq_gap4_r6_e0p56_m18_row_top4_a1p0_logit_3a810f65 | 4 | 6 | 0.560000000 | 18 | row_top4 | 58 | 18 | 232 | -0.000292457 | 34 | 30 | 24 | 0.291666667 | 0.738953462 |
| h066_seq_gap1_r6_e0p56_m999_row_top4_a1p0_logit_0cf3f7d9 | 1 | 6 | 0.560000000 | 999 | row_top4 | 64 | 35 | 256 | -0.000319721 | 40 | 31 | 24 | 0.234375000 | 0.736674543 |
| h066_seq_gap1_r8_e0p56_m999_row_top4_a1p0_logit_7f16d6aa | 1 | 8 | 0.560000000 | 999 | row_top4 | 69 | 36 | 276 | -0.000354990 | 45 | 35 | 24 | 0.231884058 | 0.735830947 |
| h066_seq_gap1_r8_e0p56_m999_row_top4_a1p15_logit_f8d1d32c | 1 | 8 | 0.560000000 | 999 | row_top4 | 69 | 36 | 276 | -0.000347535 | 45 | 35 | 24 | 0.231884058 | 0.733635825 |
| h066_seq_gap1_r8_e0p56_m999_row_top4_a1p15_prob_3eedc0c8 | 1 | 8 | 0.560000000 | 999 | row_top4 | 69 | 36 | 276 | -0.000342455 | 45 | 35 | 24 | 0.231884058 | 0.732757777 |
| h066_seq_gap4_r6_e0p56_m18_row_top4_a1p15_logit_5a8012d1 | 4 | 6 | 0.560000000 | 18 | row_top4 | 58 | 18 | 232 | -0.000286332 | 34 | 30 | 24 | 0.291666667 | 0.731051023 |
| h066_seq_gap1_r8_e0p56_m999_row_top4_a0p75_logit_9377c34a | 1 | 8 | 0.560000000 | 999 | row_top4 | 69 | 36 | 276 | -0.000333949 | 45 | 35 | 24 | 0.231884058 | 0.731001679 |
| h066_seq_gap6_r6_e0p56_m18_row_top4_a1p0_logit_d6986b93 | 6 | 6 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000314603 | 39 | 31 | 24 | 0.282608696 | 0.729691280 |
| h066_seq_gap1_r6_e0p56_m999_row_top4_a1p15_logit_9fc1ef47 | 1 | 6 | 0.560000000 | 999 | row_top4 | 64 | 35 | 256 | -0.000312985 | 40 | 31 | 24 | 0.234375000 | 0.729650152 |
| h066_seq_gap4_r8_e0p56_m18_phase_top4_a1p0_logit_26248391 | 4 | 8 | 0.560000000 | 18 | phase_top4 | 63 | 18 | 252 | -0.000271123 | 39 | 34 | 24 | 0.320754717 | 0.729301469 |
| h066_seq_gap1_r8_e0p56_m999_row_top4_a0p75_prob_df615c1f | 1 | 8 | 0.560000000 | 999 | row_top4 | 69 | 36 | 276 | -0.000329705 | 45 | 35 | 24 | 0.231884058 | 0.728367533 |
| h066_seq_gap4_r8_e0p56_m18_episode_route_top4_a1p0_logit_20781c4d | 4 | 8 | 0.560000000 | 18 | episode_route_top4 | 63 | 18 | 252 | -0.000268724 | 39 | 34 | 24 | 0.320754717 | 0.727984395 |
| h066_seq_gap1_r6_e0p56_m999_row_top4_a1p15_prob_e435532c | 1 | 6 | 0.560000000 | 999 | row_top4 | 64 | 35 | 256 | -0.000308258 | 40 | 31 | 24 | 0.234375000 | 0.727016006 |
| h066_seq_gap4_r6_e0p56_m18_row_top4_a1p15_prob_9e335384 | 4 | 6 | 0.560000000 | 18 | row_top4 | 58 | 18 | 232 | -0.000281617 | 34 | 30 | 24 | 0.291666667 | 0.725343706 |
| h066_seq_gap4_r8_e0p56_m18_phase_top4_a1p15_logit_0235db39 | 4 | 8 | 0.560000000 | 18 | phase_top4 | 63 | 18 | 252 | -0.000265530 | 39 | 34 | 24 | 0.320754717 | 0.723155127 |
| h066_seq_gap6_r6_e0p56_m18_row_top4_a1p15_logit_be100109 | 6 | 6 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000307985 | 39 | 31 | 24 | 0.282608696 | 0.722227865 |
| h066_seq_gap4_r8_e0p56_m18_episode_route_top4_a1p15_logit_e8677e9d | 4 | 8 | 0.560000000 | 18 | episode_route_top4 | 63 | 18 | 252 | -0.000263184 | 39 | 34 | 24 | 0.320754717 | 0.720520981 |
| h066_seq_gap6_r8_e0p56_m18_phase_top4_a1p0_logit_578c128f | 6 | 8 | 0.560000000 | 18 | phase_top4 | 69 | 18 | 276 | -0.000293646 | 45 | 35 | 24 | 0.307692308 | 0.720192260 |
| h066_seq_gap4_r6_e0p56_m18_row_top4_a0p75_logit_9b04bf52 | 4 | 6 | 0.560000000 | 18 | row_top4 | 58 | 18 | 232 | -0.000275175 | 34 | 30 | 24 | 0.291666667 | 0.718758340 |
| h066_seq_gap1_r6_e0p56_m999_row_top4_a0p75_logit_fa5b4c63 | 1 | 6 | 0.560000000 | 999 | row_top4 | 64 | 35 | 256 | -0.000300740 | 40 | 31 | 24 | 0.234375000 | 0.718674543 |
| h066_seq_gap6_r6_e0p56_m18_row_top4_a1p15_prob_f8932621 | 6 | 6 | 0.560000000 | 18 | row_top4 | 63 | 18 | 252 | -0.000303250 | 39 | 31 | 24 | 0.282608696 | 0.718276646 |
| h066_seq_gap4_r8_e0p56_m18_phase_top4_a1p15_prob_b3247bd8 | 4 | 8 | 0.560000000 | 18 | phase_top4 | 63 | 18 | 252 | -0.000260548 | 39 | 34 | 24 | 0.320754717 | 0.717008786 |
| h066_seq_gap1_r6_e0p56_m999_row_top4_a0p75_prob_c20fea9b | 1 | 6 | 0.560000000 | 999 | row_top4 | 64 | 35 | 256 | -0.000296979 | 40 | 31 | 24 | 0.234375000 | 0.716040396 |
| h066_seq_gap4_r8_e0p56_m18_episode_route_top4_a1p15_prob_48aea20f | 4 | 8 | 0.560000000 | 18 | episode_route_top4 | 63 | 18 | 252 | -0.000258206 | 39 | 34 | 24 | 0.320754717 | 0.714374639 |
| h066_seq_gap4_r6_e0p56_m18_row_top4_a0p75_prob_7a479d34 | 4 | 6 | 0.560000000 | 18 | row_top4 | 58 | 18 | 232 | -0.000271431 | 34 | 30 | 24 | 0.291666667 | 0.714368096 |

Interpretation rule:

- If H066 improves over H057/H065, row-independent selection was the wrong
  abstraction: HS-JEPA needs a subject-level latent sequence decoder.
- If H066 fails while H065 improves, sequence expansion is too broad and the
  smaller transition-route decoder is the better action translator.
- If H066 and H065 fail together, H057 may be a compact public-specific state,
  and expansion should move back to exact row-target identity or public-subset
  reconstruction.
