# E365 Public-Like Jackknife Stress

## Question

Did E364's donor-graft candidate survive because it captures a public-like hidden lifestyle-action state, or because the known-public sensor overfit one public observation or feature view?

## Method

- Fixed candidate pool: E364/E363 cell-action candidates, no new probability movement generation.
- Stress dimensions: feature view masks plus leave-one-public-file-out training masks.
- Feature views: `all`(129), `axis`(62), `target`(49), `anatomy`(18), `bad_good`(38), `compact`(20).
- Candidate must pass the E363 local gate and relative E363-selected margins under each scenario before it can rank.
- Decision compares E364 donor-graft against E363 source-law-preserving target-scale under jackknife stability.

## Inputs

- known available public files: `13`
- scenario count: `84`
- E364 variant: `e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11`
- E363 variant: `e362_scale_g1.06_q11.08_q20.90_q31.00_s11.30`

## Scenario Summary

| feature_view | scenarios | e364_better_rate | e364_rank_mean | e363_rank_mean | gated_mean | top_e364_rate | top_e363_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 14 | 1.000000 | 1.000000 | 7.214286 | 104.000000 | 1.000000 | 0.000000 |
| anatomy | 14 | 1.000000 | 2.428571 | 43.500000 | 104.000000 | 0.000000 | 0.000000 |
| axis | 14 | 1.000000 | 13.785714 | 46.785714 | 104.000000 | 0.000000 | 0.000000 |
| bad_good | 14 | 1.000000 | 9.142857 | 52.071429 | 104.000000 | 0.071429 | 0.000000 |
| compact | 14 | 1.000000 | 1.000000 | 5.000000 | 80.785714 | 1.000000 | 0.000000 |
| target | 14 | 1.000000 | 1.071429 | 4.928571 | 101.857143 | 0.928571 | 0.000000 |

## Top Jackknife-Supported Candidates

| variant | family | top1_count | top5_count | top10_count | gate_count | rank_mean | score_mean | pred_mean | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | 42 | 62 | 68 | 84 | 4.738095 | 4.618581 | 0.000310 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_07638e6a.csv |
| e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | 34 | 77 | 82 | 83 | 2.626506 | 4.635703 | 0.000318 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_92cfe11c.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.45_s11.00 | target_scale | 8 | 50 | 54 | 81 | 7.469136 | 4.244442 | 0.000297 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_45_s11_00_2ffbb23b.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | 0 | 58 | 83 | 83 | 4.253012 | 4.589847 | 0.000300 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1198dfee.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.45_s11.00 | target_scale | 0 | 29 | 53 | 81 | 11.012346 | 4.177050 | 0.000298 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_45_s11_00_de6e65a6.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.45_s10.90 | target_scale | 0 | 25 | 27 | 74 | 17.256757 | 4.107457 | 0.000224 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_45_s10_90_9cb51509.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.15 | donor_blend | 0 | 23 | 27 | 83 | 15.650602 | 4.088439 | 0.000318 | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_15_51cbdc8c.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.45_s11.00 | target_scale | 0 | 22 | 45 | 81 | 14.481481 | 4.134552 | 0.000298 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_45_s11_00_3743ccda.csv |
| e362_scale_g1.06_q11.08_q20.90_q31.00_s11.30 | target_scale | 0 | 22 | 41 | 84 | 26.583333 | 3.879789 | 0.000321 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q31_00_s11_30_bffaf250.csv |
| e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | 0 | 14 | 27 | 83 | 29.457831 | 3.881624 | 0.000317 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_437d7acc.csv |
| e362_graft_donor_q3_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav | donor_graft | 0 | 11 | 16 | 84 | 43.845238 | 3.690692 | 0.000325 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_90048d2f.csv |
| e362_scale_g0.96_q11.08_q20.90_q31.00_s10.90 | target_scale | 0 | 7 | 37 | 82 | 18.268293 | 3.963237 | 0.000305 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q31_00_s10_90_6cd43bb3.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.75_s11.30 | target_scale | 0 | 4 | 38 | 83 | 20.915663 | 3.981548 | 0.000310 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_75_s11_30_d02aaf2d.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.45_s10.90 | target_scale | 0 | 4 | 26 | 74 | 24.202703 | 4.040362 | 0.000225 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_45_s10_90_97423861.csv |
| e362_scale_g0.96_q11.08_q20.90_q30.75_s10.70 | target_scale | 0 | 3 | 43 | 73 | 14.753425 | 4.122873 | 0.000214 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q30_75_s10_70_b4153387.csv |
| e362_scale_g0.96_q11.08_q20.90_q30.75_s10.90 | target_scale | 0 | 2 | 36 | 80 | 12.537500 | 4.094060 | 0.000286 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q30_75_s10_90_f2243d75.csv |
| e362_scale_g0.96_q11.08_q20.90_q31.00_s10.70 | target_scale | 0 | 2 | 19 | 73 | 19.712329 | 3.950860 | 0.000213 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q31_00_s10_70_5cfec73f.csv |
| e362_graft_donor_s1_e360_e356_halfs3_amp__learned_free_mixture_subjective_he | donor_graft | 0 | 2 | 12 | 70 | 59.757143 | 3.410610 | 0.000278 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_611665e7.csv |
| e362_scale_g1.03_q11.08_q20.90_q31.00_s11.30 | target_scale | 0 | 1 | 31 | 84 | 28.904762 | 3.849353 | 0.000320 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q31_00_s11_30_58916996.csv |
| e362_graft_donor_q2q3_e361_e351_robust_center__learned_story_nonmonotone_s1_co | donor_graft | 0 | 1 | 12 | 84 | 37.083333 | 3.759956 | 0.000320 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e361_e351_robust_center__learned_story_nonmonotone_s1_co_102144c1.csv |
| e362_graft_donor_q3s1_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav | donor_graft | 0 | 1 | 2 | 84 | 62.976190 | 3.414567 | 0.000287 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_b4dcdce7.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.75_s11.00 | target_scale | 0 | 0 | 3 | 83 | 18.602410 | 3.976644 | 0.000317 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_75_s11_00_6b534dd4.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.75_s10.90 | target_scale | 0 | 0 | 1 | 80 | 20.887500 | 3.968485 | 0.000288 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_75_s10_90_7376bcc9.csv |
| e362_scale_g1.06_q11.04_q20.90_q30.45_s11.00 | target_scale | 0 | 0 | 27 | 80 | 21.062500 | 4.061131 | 0.000288 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_04_q20_90_q30_45_s11_00_e0688e7d.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.75_s10.70 | target_scale | 0 | 0 | 3 | 72 | 25.111111 | 3.943266 | 0.000205 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_75_s10_70_fe1c7c0a.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.75_s11.00 | target_scale | 0 | 0 | 0 | 83 | 27.662651 | 3.884101 | 0.000317 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_75_s11_00_6c19969d.csv |
| e362_scale_g1.00_q11.08_q20.90_q31.00_s10.90 | target_scale | 0 | 0 | 0 | 82 | 28.609756 | 3.829046 | 0.000307 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q31_00_s10_90_bac251d6.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.75_s10.90 | target_scale | 0 | 0 | 0 | 80 | 28.962500 | 3.893147 | 0.000289 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_75_s10_90_c4f296a9.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.75_s11.00 | target_scale | 0 | 0 | 0 | 83 | 30.843373 | 3.860913 | 0.000318 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_75_s11_00_f41e5150.csv |
| e362_scale_g1.03_q11.04_q20.90_q30.75_s11.00 | target_scale | 0 | 0 | 0 | 82 | 31.707317 | 3.850092 | 0.000308 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_04_q20_90_q30_75_s11_00_17a39501.csv |

## Decision

| decision | variant | family | selected_uploadsafe_file | scenario_count | e364_better_e363_rate | e364_top1_rate | e364_top10_rate | e363_top10_rate | support_top_variant | support_top1_rate | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| support_e364_publiclike_probe | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv | 84 | 1.000000 | 0.500000 | 0.809524 | 0.488095 | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | 0.500000 | E364 remains ahead of E363 under most leave-public/feature-view stresses and stays frequently in the top10. |

## Interpretation

- If E364 remains top10 across many feature/drop scenarios, the donor-graft S1-recovery hypothesis is not just a one-observation public-sensor artifact.
- If E363 dominates under jackknife, source-law preservation is safer than public-like donor geometry.
- If a third candidate dominates, E364 found the right validation question but not the most stable point inside the basin.

## Files

- `analysis_outputs/e365_public_like_jackknife_scenarios.csv`
- `analysis_outputs/e365_public_like_jackknife_candidate_support.csv`
- `analysis_outputs/e365_public_like_jackknife_selection.csv`