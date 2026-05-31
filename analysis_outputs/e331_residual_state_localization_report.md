# E331 Residual-State Localization

## Question

E330 proved target-specific residual states exist, but full-target calibration was too diffuse. Can those states localize row/block/cell actions while preserving E247 and avoiding E323?

## Localized Feature Stress

| target | view_id | split | policy | source_delta | source_dominance | base_loss | localized_loss | actual_delta | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | train_rows | test_rows | gate | threshold | train_blocks | test_blocks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | jepa_resid | dateblock | pos_q80 | -0.025842772 | 0.958333333 | 0.678969360 | 0.649294496 | -0.029674864 | -0.016470316 | 0.001155444 | -0.009169977 | 1.000000000 | -0.030830308 | 90 | 42 | True | 0.085457461 |  |  |
| Q1 | jepa_resid | dateblock | pos_q90 | -0.025842772 | 0.958333333 | 0.678969360 | 0.656010996 | -0.022958364 | -0.017585480 | -0.000350043 | -0.008384730 | 1.000000000 | -0.022608322 | 45 | 11 | True | 0.151840115 |  |  |
| Q2 | jepa_resid | subject | pos_q80 | -0.030210616 | 1.000000000 | 0.765899724 | 0.748418127 | -0.017481597 | -0.027584625 | 0.001308576 | -0.004691506 | 0.900000000 | -0.018790173 | 90 | 51 | True | 0.070994434 |  |  |
| S2 | jepa_resid | dateblock | pos_q80 | -0.014211218 | 1.000000000 | 0.590404664 | 0.573521702 | -0.016882963 | -0.005035200 | 0.001419885 | 0.000527990 | 1.000000000 | -0.018302848 | 90 | 54 | True | 0.083241467 |  |  |
| Q1 | jepa_resid | dateblock | abs_q75 | -0.025842772 | 0.958333333 | 0.678969360 | 0.663917021 | -0.015052339 | -0.014372315 | 0.000705465 | -0.006031438 | 1.000000000 | -0.015757804 | 113 | 37 | True | 0.138890825 |  |  |
| S2 | family | dateblock | neg_q90 | -0.007551624 | 1.000000000 | 0.590404664 | 0.576831656 | -0.013573009 | -0.005870517 | 0.000557666 | -0.002560054 | 1.000000000 | -0.014130675 | 45 | 14 | True | -0.149511171 |  |  |
| S2 | jepa_resid | dateblock | pos_q90 | -0.014211218 | 1.000000000 | 0.590404664 | 0.578606912 | -0.011797753 | -0.008330996 | 0.001149604 | -0.001825904 | 1.000000000 | -0.012947356 | 45 | 14 | True | 0.133015824 |  |  |
| S2 | family | dateblock | neg_q80 | -0.007551624 | 1.000000000 | 0.590404664 | 0.579278036 | -0.011126629 | -0.013949094 | 0.001795847 | 0.000162313 | 0.966666667 | -0.012922475 | 90 | 31 | True | -0.089003669 |  |  |
| S2 | raw_day | subject | pos_q80 | -0.016452074 | 0.958333333 | 0.698689330 | 0.687585295 | -0.011104035 | -0.020109995 | -0.000285617 | -0.005955486 | 0.900000000 | -0.010818418 | 90 | 51 | True | 0.305626391 |  |  |
| Q1 | jepa_resid | dateblock | blockabs_q65 | -0.025842772 | 0.958333333 | 0.678969360 | 0.668067733 | -0.010901627 | -0.010938198 | 0.000747853 | -0.002511898 | 0.966666667 | -0.011649480 | 147 | 46 | True | 0.102806370 | 30.000000000 | 10.000000000 |
| Q2 | jepa_resid | subject | blockabs_q65 | -0.030210616 | 1.000000000 | 0.765899724 | 0.755782960 | -0.010116764 | -0.015147824 | 0.000895487 | -0.002155182 | 0.966666667 | -0.011012251 | 168 | 55 | True | 0.116308787 | 30.000000000 | 12.000000000 |
| Q2 | jepa_resid | subject | abs_q75 | -0.030210616 | 1.000000000 | 0.765899724 | 0.755840672 | -0.010059052 | -0.028058953 | 0.001915919 | -0.007572102 | 0.933333333 | -0.011974971 | 113 | 37 | True | 0.157969944 |  |  |
| S1 | family_story | subject | abs_q75 | -0.005108509 | 1.000000000 | 0.656678990 | 0.647020868 | -0.009658122 | -0.005503951 | 0.002005314 | 0.000123888 | 1.000000000 | -0.011663436 | 113 | 45 | True | 0.471622952 |  |  |
| S2 | jepa_resid | dateblock | abs_q75 | -0.014211218 | 1.000000000 | 0.590404664 | 0.580771417 | -0.009633248 | -0.003239325 | 0.002322839 | -0.001012965 | 1.000000000 | -0.011956087 | 113 | 41 | True | 0.110760563 |  |  |
| Q1 | jepa_resid | dateblock | abs_q85 | -0.025842772 | 0.958333333 | 0.678969360 | 0.672259856 | -0.006709504 | -0.008394263 | 0.000840939 | -0.004457024 | 0.966666667 | -0.007550443 | 68 | 18 | True | 0.180134400 |  |  |
| S1 | family_jepa_story | subject | abs_q75 | -0.009127646 | 1.000000000 | 0.656678990 | 0.650007970 | -0.006671020 | -0.003695098 | 0.000941429 | -0.001043242 | 1.000000000 | -0.007612449 | 113 | 40 | True | 0.519036863 |  |  |
| S1 | family_jepa_story | subject | abs_q92 | -0.009127646 | 1.000000000 | 0.656678990 | 0.650480684 | -0.006198306 | -0.006992975 | 0.000429400 | -0.001932004 | 0.966666667 | -0.006627706 | 36 | 12 | True | 0.763374587 |  |  |
| S2 | raw_day | subject | neg_q80 | -0.016452074 | 0.958333333 | 0.698689330 | 0.692938385 | -0.005750945 | -0.002368786 | 0.003858529 | 0.000451094 | 1.000000000 | -0.009609474 | 90 | 33 | True | -0.304629498 |  |  |
| S1 | family_jepa_story | subject | blockabs_q80 | -0.009127646 | 1.000000000 | 0.656678990 | 0.651105930 | -0.005573060 | -0.005534047 | 0.001299951 | -0.000664802 | 1.000000000 | -0.006873011 | 92 | 22 | True | 0.450541482 | 18.000000000 | 8.000000000 |
| Q1 | jepa_resid | dateblock | blockabs_q80 | -0.025842772 | 0.958333333 | 0.678969360 | 0.673696541 | -0.005272819 | -0.014471919 | 0.000024504 | -0.003291398 | 0.900000000 | -0.005297322 | 89 | 18 | True | 0.131237578 | 18.000000000 | 5.000000000 |
| Q2 | jepa_resid | subject | neg_q80 | -0.030210616 | 1.000000000 | 0.765899724 | 0.760676187 | -0.005223538 | -0.012410450 | 0.002550903 | -0.000652466 | 0.966666667 | -0.007774441 | 90 | 45 | True | -0.128132475 |  |  |
| S2 | raw_day | subject | abs_q75 | -0.016452074 | 0.958333333 | 0.698689330 | 0.693492794 | -0.005196536 | -0.007956263 | 0.001341988 | -0.003804158 | 0.900000000 | -0.006538525 | 113 | 49 | True | 0.430078421 |  |  |
| S1 | family_story | subject | neg_q80 | -0.005108509 | 1.000000000 | 0.656678990 | 0.651602074 | -0.005076916 | -0.015425254 | 0.000429661 | -0.001858432 | 0.900000000 | -0.005506577 | 90 | 37 | True | -0.380988142 |  |  |
| S1 | family_jepa_story | subject | pos_q90 | -0.009127646 | 1.000000000 | 0.656678990 | 0.651879767 | -0.004799223 | -0.007912172 | 0.001133937 | -0.001558901 | 0.933333333 | -0.005933160 | 45 | 22 | True | 0.499752347 |  |  |
| S1 | family_story | subject | abs_q92 | -0.005108509 | 1.000000000 | 0.656678990 | 0.652030432 | -0.004648558 | -0.004625693 | 0.001873630 | 0.000075425 | 1.000000000 | -0.006522189 | 36 | 8 | True | 0.732971813 |  |  |
| S2 | raw_day | subject | abs_q92 | -0.016452074 | 0.958333333 | 0.698689330 | 0.694225934 | -0.004463396 | -0.005648425 | 0.002560552 | -0.001848465 | 0.933333333 | -0.007023948 | 36 | 11 | True | 0.621789524 |  |  |
| S1 | family_jepa_story | subject | pos_q80 | -0.009127646 | 1.000000000 | 0.656678990 | 0.653230457 | -0.003448533 | -0.003763806 | 0.002058478 | -0.000013879 | 0.966666667 | -0.005507011 | 90 | 47 | True | 0.326802795 |  |  |
| S2 | family | dateblock | abs_q75 | -0.007551624 | 1.000000000 | 0.590404664 | 0.587283490 | -0.003121174 | -0.011364678 | 0.001801769 | -0.000226804 | 0.866666667 | -0.004922944 | 113 | 29 | True | 0.137941746 |  |  |
| S1 | family_jepa_story | subject | abs_q85 | -0.009127646 | 1.000000000 | 0.656678990 | 0.653576415 | -0.003102575 | -0.005834006 | 0.001527236 | 0.000242308 | 0.966666667 | -0.004629810 | 68 | 25 | True | 0.620278836 |  |  |
| S1 | family_story | subject | abs_q85 | -0.005108509 | 1.000000000 | 0.656678990 | 0.653696128 | -0.002982862 | -0.004050747 | 0.001793830 | -0.000891936 | 0.900000000 | -0.004776692 | 68 | 26 | True | 0.593667449 |  |  |
| S1 | family_story | subject | pos_q90 | -0.005108509 | 1.000000000 | 0.656678990 | 0.654141476 | -0.002537514 | -0.004378859 | 0.000993816 | 0.000128544 | 0.966666667 | -0.003531331 | 45 | 19 | True | 0.462374667 |  |  |
| S2 | jepa_resid | dateblock | abs_q85 | -0.014211218 | 1.000000000 | 0.590404664 | 0.588049527 | -0.002355137 | -0.006054320 | 0.001884323 | 0.000139765 | 0.900000000 | -0.004239460 | 68 | 23 | True | 0.143317775 |  |  |
| S1 | family_story | subject | pos_q80 | -0.005108509 | 1.000000000 | 0.656678990 | 0.654907615 | -0.001771375 | -0.008995255 | 0.001414262 | 0.000004238 | 0.900000000 | -0.003185637 | 90 | 51 | True | 0.298620399 |  |  |
| S2 | family_story | subject | neg_q80 | -0.003856951 | 0.958333333 | 0.698689330 | 0.696996291 | -0.001693039 | -0.003180410 | 0.002595935 | -0.000679710 | 0.900000000 | -0.004288974 | 90 | 14 | True | -0.583773196 |  |  |
| S2 | family_story | subject | abs_q75 | -0.003856951 | 0.958333333 | 0.698689330 | 0.697022124 | -0.001667207 | -0.001831785 | 0.001586117 | 0.000286563 | 0.966666667 | -0.003253324 | 113 | 28 | True | 0.590942586 |  |  |
| S2 | jepa_resid | dateblock | neg_q80 | -0.014211218 | 1.000000000 | 0.590404664 | 0.589128205 | -0.001276459 | -0.003561282 | 0.001453417 | -0.000641251 | 0.866666667 | -0.002729876 | 90 | 22 | True | -0.069578199 |  |  |
| S1 | family_story | subject | blockabs_q80 | -0.005108509 | 1.000000000 | 0.656678990 | 0.655442188 | -0.001236802 | -0.004489921 | 0.001705105 | 0.000727169 | 0.866666667 | -0.002941907 | 103 | 49 | True | 0.369536048 | 18.000000000 | 14.000000000 |
| Q2 | family | subject | pos_q90 | -0.004292977 | 0.875000000 | 0.765899724 | 0.764809203 | -0.001090522 | -0.011586799 | 0.001347972 | -0.000062786 | 0.900000000 | -0.002438494 | 45 | 21 | True | 0.210753781 |  |  |
| S2 | family_story | subject | neg_q90 | -0.003856951 | 0.958333333 | 0.698689330 | 0.698062092 | -0.000627238 | -0.001601708 | 0.002142746 | -0.000149038 | 0.866666667 | -0.002769984 | 45 | 6 | True | -0.797233074 |  |  |
| Q2 | jepa_resid | subject | abs_q85 | -0.030210616 | 1.000000000 | 0.765899724 | 0.758316557 | -0.007583168 | -0.018785599 | 0.000473113 | -0.009175588 | 0.733333333 | -0.008056281 | 68 | 19 | False | 0.214400208 |  |  |

## Selected Gates

| target | view_id | split | policy | source_delta | source_dominance | base_loss | localized_loss | actual_delta | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | train_rows | test_rows | gate | threshold | train_blocks | test_blocks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | jepa_resid | dateblock | pos_q80 | -0.025842772 | 0.958333333 | 0.678969360 | 0.649294496 | -0.029674864 | -0.016470316 | 0.001155444 | -0.009169977 | 1.000000000 | -0.030830308 | 90 | 42 | True | 0.085457461 |  |  |
| Q1 | jepa_resid | dateblock | pos_q90 | -0.025842772 | 0.958333333 | 0.678969360 | 0.656010996 | -0.022958364 | -0.017585480 | -0.000350043 | -0.008384730 | 1.000000000 | -0.022608322 | 45 | 11 | True | 0.151840115 |  |  |
| Q2 | jepa_resid | subject | pos_q80 | -0.030210616 | 1.000000000 | 0.765899724 | 0.748418127 | -0.017481597 | -0.027584625 | 0.001308576 | -0.004691506 | 0.900000000 | -0.018790173 | 90 | 51 | True | 0.070994434 |  |  |
| S2 | jepa_resid | dateblock | pos_q80 | -0.014211218 | 1.000000000 | 0.590404664 | 0.573521702 | -0.016882963 | -0.005035200 | 0.001419885 | 0.000527990 | 1.000000000 | -0.018302848 | 90 | 54 | True | 0.083241467 |  |  |
| Q1 | jepa_resid | dateblock | abs_q75 | -0.025842772 | 0.958333333 | 0.678969360 | 0.663917021 | -0.015052339 | -0.014372315 | 0.000705465 | -0.006031438 | 1.000000000 | -0.015757804 | 113 | 37 | True | 0.138890825 |  |  |
| S2 | family | dateblock | neg_q90 | -0.007551624 | 1.000000000 | 0.590404664 | 0.576831656 | -0.013573009 | -0.005870517 | 0.000557666 | -0.002560054 | 1.000000000 | -0.014130675 | 45 | 14 | True | -0.149511171 |  |  |
| S2 | jepa_resid | dateblock | pos_q90 | -0.014211218 | 1.000000000 | 0.590404664 | 0.578606912 | -0.011797753 | -0.008330996 | 0.001149604 | -0.001825904 | 1.000000000 | -0.012947356 | 45 | 14 | True | 0.133015824 |  |  |
| S2 | family | dateblock | neg_q80 | -0.007551624 | 1.000000000 | 0.590404664 | 0.579278036 | -0.011126629 | -0.013949094 | 0.001795847 | 0.000162313 | 0.966666667 | -0.012922475 | 90 | 31 | True | -0.089003669 |  |  |
| S2 | raw_day | subject | pos_q80 | -0.016452074 | 0.958333333 | 0.698689330 | 0.687585295 | -0.011104035 | -0.020109995 | -0.000285617 | -0.005955486 | 0.900000000 | -0.010818418 | 90 | 51 | True | 0.305626391 |  |  |
| Q1 | jepa_resid | dateblock | blockabs_q65 | -0.025842772 | 0.958333333 | 0.678969360 | 0.668067733 | -0.010901627 | -0.010938198 | 0.000747853 | -0.002511898 | 0.966666667 | -0.011649480 | 147 | 46 | True | 0.102806370 | 30.000000000 | 10.000000000 |
| Q2 | jepa_resid | subject | blockabs_q65 | -0.030210616 | 1.000000000 | 0.765899724 | 0.755782960 | -0.010116764 | -0.015147824 | 0.000895487 | -0.002155182 | 0.966666667 | -0.011012251 | 168 | 55 | True | 0.116308787 | 30.000000000 | 12.000000000 |
| Q2 | jepa_resid | subject | abs_q75 | -0.030210616 | 1.000000000 | 0.765899724 | 0.755840672 | -0.010059052 | -0.028058953 | 0.001915919 | -0.007572102 | 0.933333333 | -0.011974971 | 113 | 37 | True | 0.157969944 |  |  |
| S1 | family_story | subject | abs_q75 | -0.005108509 | 1.000000000 | 0.656678990 | 0.647020868 | -0.009658122 | -0.005503951 | 0.002005314 | 0.000123888 | 1.000000000 | -0.011663436 | 113 | 45 | True | 0.471622952 |  |  |
| S2 | jepa_resid | dateblock | abs_q75 | -0.014211218 | 1.000000000 | 0.590404664 | 0.580771417 | -0.009633248 | -0.003239325 | 0.002322839 | -0.001012965 | 1.000000000 | -0.011956087 | 113 | 41 | True | 0.110760563 |  |  |

## Candidate Probes

| candidate_id | file | basename | target | view_id | split | policy | scale | source_actual_delta | source_dominance | train_rows | test_rows | changed_rows | changed_cells | mean_abs_logit_move | max_abs_logit_move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2_jepa_resid_subject_abs_q75_s0p4 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p4_38366bc2.csv | submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p4_38366bc2.csv | Q2 | jepa_resid | subject | abs_q75 | 0.400000000 | -0.010059052 | 0.933333333 | 113 | 37 | 37 | 37 | 0.000718857 | 0.034000000 |
| Q2_jepa_resid_subject_abs_q75_s0p7 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p7_c1bceab6.csv | submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p7_c1bceab6.csv | Q2 | jepa_resid | subject | abs_q75 | 0.700000000 | -0.010059052 | 0.933333333 | 113 | 37 | 37 | 37 | 0.001258000 | 0.059500000 |
| Q2_jepa_resid_subject_abs_q75_s1p0 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s1p0_107d1dc1.csv | submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s1p0_107d1dc1.csv | Q2 | jepa_resid | subject | abs_q75 | 1.000000000 | -0.010059052 | 0.933333333 | 113 | 37 | 37 | 37 | 0.001797143 | 0.085000000 |
| Q2_jepa_resid_subject_pos_q80_s0p4 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p4_8fe92177.csv | submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p4_8fe92177.csv | Q2 | jepa_resid | subject | pos_q80 | 0.400000000 | -0.017481597 | 0.900000000 | 90 | 51 | 51 | 51 | 0.000942019 | 0.034000000 |
| Q2_jepa_resid_subject_pos_q80_s0p7 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p7_70c65813.csv | submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p7_70c65813.csv | Q2 | jepa_resid | subject | pos_q80 | 0.700000000 | -0.017481597 | 0.900000000 | 90 | 51 | 51 | 51 | 0.001648533 | 0.059500000 |
| Q2_jepa_resid_subject_pos_q80_s1p0 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s1p0_66fc29df.csv | submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s1p0_66fc29df.csv | Q2 | jepa_resid | subject | pos_q80 | 1.000000000 | -0.017481597 | 0.900000000 | 90 | 51 | 51 | 51 | 0.002355048 | 0.085000000 |
| Q2_jepa_resid_subject_blockabs_q65_s0p4 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p4_b3f7ac13.csv | submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p4_b3f7ac13.csv | Q2 | jepa_resid | subject | blockabs_q65 | 0.400000000 | -0.010116764 | 0.966666667 | 168 | 55 | 55 | 55 | 0.000980067 | 0.034000000 |
| Q2_jepa_resid_subject_blockabs_q65_s0p7 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p7_bdaaf9a2.csv | submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p7_bdaaf9a2.csv | Q2 | jepa_resid | subject | blockabs_q65 | 0.700000000 | -0.010116764 | 0.966666667 | 168 | 55 | 55 | 55 | 0.001715118 | 0.059500000 |
| Q2_jepa_resid_subject_blockabs_q65_s1p0 | analysis_outputs/submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s1p0_161afeb3.csv | submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s1p0_161afeb3.csv | Q2 | jepa_resid | subject | blockabs_q65 | 1.000000000 | -0.010116764 | 0.966666667 | 168 | 55 | 55 | 55 | 0.002450168 | 0.085000000 |
| Q1_jepa_resid_dateblock_abs_q75_s0p4 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p4_b5d2a430.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p4_b5d2a430.csv | Q1 | jepa_resid | dateblock | abs_q75 | 0.400000000 | -0.015052339 | 1.000000000 | 113 | 37 | 37 | 37 | 0.000718857 | 0.034000000 |
| Q1_jepa_resid_dateblock_abs_q75_s0p7 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p7_b44eec88.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p7_b44eec88.csv | Q1 | jepa_resid | dateblock | abs_q75 | 0.700000000 | -0.015052339 | 1.000000000 | 113 | 37 | 37 | 37 | 0.001258000 | 0.059500000 |
| Q1_jepa_resid_dateblock_abs_q75_s1p0 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s1p0_50e0879b.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s1p0_50e0879b.csv | Q1 | jepa_resid | dateblock | abs_q75 | 1.000000000 | -0.015052339 | 1.000000000 | 113 | 37 | 37 | 37 | 0.001797143 | 0.085000000 |
| Q1_jepa_resid_dateblock_pos_q80_s0p4 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p4_04e3c597.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p4_04e3c597.csv | Q1 | jepa_resid | dateblock | pos_q80 | 0.400000000 | -0.029674864 | 1.000000000 | 90 | 42 | 42 | 42 | 0.000816000 | 0.034000000 |
| Q1_jepa_resid_dateblock_pos_q80_s0p7 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p7_0d69fc41.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p7_0d69fc41.csv | Q1 | jepa_resid | dateblock | pos_q80 | 0.700000000 | -0.029674864 | 1.000000000 | 90 | 42 | 42 | 42 | 0.001428000 | 0.059500000 |
| Q1_jepa_resid_dateblock_pos_q80_s1p0 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s1p0_f55d27bb.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s1p0_f55d27bb.csv | Q1 | jepa_resid | dateblock | pos_q80 | 1.000000000 | -0.029674864 | 1.000000000 | 90 | 42 | 42 | 42 | 0.002040000 | 0.085000000 |
| Q1_jepa_resid_dateblock_pos_q90_s0p4 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p4_01f360c3.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p4_01f360c3.csv | Q1 | jepa_resid | dateblock | pos_q90 | 0.400000000 | -0.022958364 | 1.000000000 | 45 | 11 | 11 | 11 | 0.000213714 | 0.034000000 |
| Q1_jepa_resid_dateblock_pos_q90_s0p7 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p7_cf6801db.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p7_cf6801db.csv | Q1 | jepa_resid | dateblock | pos_q90 | 0.700000000 | -0.022958364 | 1.000000000 | 45 | 11 | 11 | 11 | 0.000374000 | 0.059500000 |
| Q1_jepa_resid_dateblock_pos_q90_s1p0 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s1p0_02a5d855.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s1p0_02a5d855.csv | Q1 | jepa_resid | dateblock | pos_q90 | 1.000000000 | -0.022958364 | 1.000000000 | 45 | 11 | 11 | 11 | 0.000534286 | 0.085000000 |
| Q1_jepa_resid_dateblock_blockabs_q65_s0p4 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p4_eaaa6d0d.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p4_eaaa6d0d.csv | Q1 | jepa_resid | dateblock | blockabs_q65 | 0.400000000 | -0.010901627 | 0.966666667 | 147 | 46 | 46 | 46 | 0.000808222 | 0.034000000 |
| Q1_jepa_resid_dateblock_blockabs_q65_s0p7 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p7_4c85cdf0.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p7_4c85cdf0.csv | Q1 | jepa_resid | dateblock | blockabs_q65 | 0.700000000 | -0.010901627 | 0.966666667 | 147 | 46 | 46 | 46 | 0.001414389 | 0.059500000 |
| Q1_jepa_resid_dateblock_blockabs_q65_s1p0 | analysis_outputs/submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s1p0_49d16b09.csv | submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s1p0_49d16b09.csv | Q1 | jepa_resid | dateblock | blockabs_q65 | 1.000000000 | -0.010901627 | 0.966666667 | 147 | 46 | 46 | 46 | 0.002020556 | 0.085000000 |
| S2_raw_day_subject_pos_q80_s0p4 | analysis_outputs/submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p4_f2b28a54.csv | submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p4_f2b28a54.csv | S2 | raw_day | subject | pos_q80 | 0.400000000 | -0.011104035 | 0.900000000 | 90 | 51 | 51 | 51 | 0.000966453 | 0.034000000 |
| S2_raw_day_subject_pos_q80_s0p7 | analysis_outputs/submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p7_5b1f4ee5.csv | submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p7_5b1f4ee5.csv | S2 | raw_day | subject | pos_q80 | 0.700000000 | -0.011104035 | 0.900000000 | 90 | 51 | 51 | 51 | 0.001691293 | 0.059500000 |
| S2_raw_day_subject_pos_q80_s1p0 | analysis_outputs/submission_e331_localresid_S2_raw_day_subject_pos_q80_s1p0_d1be19f0.csv | submission_e331_localresid_S2_raw_day_subject_pos_q80_s1p0_d1be19f0.csv | S2 | raw_day | subject | pos_q80 | 1.000000000 | -0.011104035 | 0.900000000 | 90 | 51 | 51 | 51 | 0.002416133 | 0.085000000 |
| S2_jepa_resid_dateblock_abs_q75_s0p4 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p4_3dee5dcc.csv | submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p4_3dee5dcc.csv | S2 | jepa_resid | dateblock | abs_q75 | 0.400000000 | -0.009633248 | 1.000000000 | 113 | 41 | 41 | 41 | 0.000796571 | 0.034000000 |
| S2_jepa_resid_dateblock_abs_q75_s0p7 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p7_3117892c.csv | submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p7_3117892c.csv | S2 | jepa_resid | dateblock | abs_q75 | 0.700000000 | -0.009633248 | 1.000000000 | 113 | 41 | 41 | 41 | 0.001394000 | 0.059500000 |
| S2_jepa_resid_dateblock_abs_q75_s1p0 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s1p0_de46605b.csv | submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s1p0_de46605b.csv | S2 | jepa_resid | dateblock | abs_q75 | 1.000000000 | -0.009633248 | 1.000000000 | 113 | 41 | 41 | 41 | 0.001991429 | 0.085000000 |
| S2_jepa_resid_dateblock_pos_q80_s0p4 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p4_db9e2c3b.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p4_db9e2c3b.csv | S2 | jepa_resid | dateblock | pos_q80 | 0.400000000 | -0.016882963 | 1.000000000 | 90 | 54 | 54 | 54 | 0.001049143 | 0.034000000 |
| S2_jepa_resid_dateblock_pos_q80_s0p7 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p7_3276d49e.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p7_3276d49e.csv | S2 | jepa_resid | dateblock | pos_q80 | 0.700000000 | -0.016882963 | 1.000000000 | 90 | 54 | 54 | 54 | 0.001836000 | 0.059500000 |
| S2_jepa_resid_dateblock_pos_q80_s1p0 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s1p0_ca12e8d6.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s1p0_ca12e8d6.csv | S2 | jepa_resid | dateblock | pos_q80 | 1.000000000 | -0.016882963 | 1.000000000 | 90 | 54 | 54 | 54 | 0.002622857 | 0.085000000 |
| S2_jepa_resid_dateblock_pos_q90_s0p4 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p4_f93bacb8.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p4_f93bacb8.csv | S2 | jepa_resid | dateblock | pos_q90 | 0.400000000 | -0.011797753 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000272000 | 0.034000000 |
| S2_jepa_resid_dateblock_pos_q90_s0p7 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p7_56200896.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p7_56200896.csv | S2 | jepa_resid | dateblock | pos_q90 | 0.700000000 | -0.011797753 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000476000 | 0.059500000 |
| S2_jepa_resid_dateblock_pos_q90_s1p0 | analysis_outputs/submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s1p0_5d7f5eb2.csv | submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s1p0_5d7f5eb2.csv | S2 | jepa_resid | dateblock | pos_q90 | 1.000000000 | -0.011797753 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000680000 | 0.085000000 |
| S2_family_dateblock_neg_q80_s0p4 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q80_s0p4_2ed25e15.csv | submission_e331_localresid_S2_family_dateblock_neg_q80_s0p4_2ed25e15.csv | S2 | family | dateblock | neg_q80 | 0.400000000 | -0.011126629 | 0.966666667 | 90 | 31 | 31 | 31 | 0.000601839 | 0.034000000 |
| S2_family_dateblock_neg_q80_s0p7 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q80_s0p7_960a1b1d.csv | submission_e331_localresid_S2_family_dateblock_neg_q80_s0p7_960a1b1d.csv | S2 | family | dateblock | neg_q80 | 0.700000000 | -0.011126629 | 0.966666667 | 90 | 31 | 31 | 31 | 0.001053218 | 0.059500000 |
| S2_family_dateblock_neg_q80_s1p0 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q80_s1p0_4f176a4b.csv | submission_e331_localresid_S2_family_dateblock_neg_q80_s1p0_4f176a4b.csv | S2 | family | dateblock | neg_q80 | 1.000000000 | -0.011126629 | 0.966666667 | 90 | 31 | 31 | 31 | 0.001504597 | 0.085000000 |
| S2_family_dateblock_neg_q90_s0p4 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q90_s0p4_4c5567af.csv | submission_e331_localresid_S2_family_dateblock_neg_q90_s0p4_4c5567af.csv | S2 | family | dateblock | neg_q90 | 0.400000000 | -0.013573009 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000272000 | 0.034000000 |
| S2_family_dateblock_neg_q90_s0p7 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q90_s0p7_5b532948.csv | submission_e331_localresid_S2_family_dateblock_neg_q90_s0p7_5b532948.csv | S2 | family | dateblock | neg_q90 | 0.700000000 | -0.013573009 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000476000 | 0.059500000 |
| S2_family_dateblock_neg_q90_s1p0 | analysis_outputs/submission_e331_localresid_S2_family_dateblock_neg_q90_s1p0_7114ebd9.csv | submission_e331_localresid_S2_family_dateblock_neg_q90_s1p0_7114ebd9.csv | S2 | family | dateblock | neg_q90 | 1.000000000 | -0.013573009 | 1.000000000 | 45 | 14 | 14 | 14 | 0.000680000 | 0.085000000 |
| S1_family_story_subject_abs_q75_s0p4 | analysis_outputs/submission_e331_localresid_S1_family_story_subject_abs_q75_s0p4_d1b8887b.csv | submission_e331_localresid_S1_family_story_subject_abs_q75_s0p4_d1b8887b.csv | S1 | family_story | subject | abs_q75 | 0.400000000 | -0.009658122 | 1.000000000 | 113 | 45 | 45 | 45 | 0.000845651 | 0.034000000 |

## Public-Free Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p7_cf6801db.csv | too_small_to_submit | -0.000053263 | -0.000162561 | -0.000008279 | 0.972222222 | 0.003351402 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s1p0_02a5d855.csv | too_small_to_submit | -0.000065115 | -0.000222633 | -0.000005876 | 0.944444444 | 0.004787717 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p4_01f360c3.csv | too_small_to_submit | -0.000032656 | -0.000094751 | -0.000005476 | 1.000000000 | 0.001915087 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p4_04e3c597.csv | too_small_to_submit | -0.000069129 | -0.000285047 | 0.000001092 | 0.861111111 | 0.005878315 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p7_0d69fc41.csv | too_small_to_submit | -0.000112512 | -0.000486716 | 0.000010688 | 0.861111111 | 0.010287052 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s1p0_f55d27bb.csv | too_small_to_submit | -0.000140302 | -0.000669751 | 0.000031608 | 0.819444444 | 0.014695788 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p4_f93bacb8.csv | below_selector_resolution | -0.000051329 | -0.000149850 | 0.000010272 | 0.472222222 | -0.001342845 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p4_3dee5dcc.csv | below_selector_resolution | 0.000004734 | -0.000000996 | 0.000013802 | 0.111111111 | -0.001024353 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p7_56200896.csv | below_selector_resolution | -0.000083644 | -0.000252688 | 0.000023489 | 0.472222222 | -0.002349978 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p4_db9e2c3b.csv | below_selector_resolution | -0.000194429 | -0.000557815 | 0.000031454 | 0.486111111 | -0.003532594 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p4_d1b8887b.csv | below_selector_resolution | -0.000004314 | -0.000072804 | 0.000038245 | 0.388888889 | -0.001763729 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s1p0_5d7f5eb2.csv | below_selector_resolution | -0.000109322 | -0.000343111 | 0.000041000 | 0.472222222 | -0.003357112 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p7_3117892c.csv | below_selector_resolution | 0.000033707 | 0.000017667 | 0.000045059 | 0.055555556 | -0.001792618 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p4_eaaa6d0d.csv | below_selector_resolution | 0.000006684 | -0.000020119 | 0.000048841 | 0.500000000 | 0.003528102 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p4_b5d2a430.csv | below_selector_resolution | 0.000002536 | -0.000016890 | 0.000058629 | 0.611111111 | 0.003437049 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p4_8fe92177.csv | below_selector_resolution | -0.000139872 | -0.000536120 | 0.000060205 | 0.430555556 | 0.005414506 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p7_757d2f5a.csv | below_selector_resolution | -0.000027179 | -0.000167614 | 0.000072499 | 0.444444444 | -0.003086525 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p7_3276d49e.csv | below_selector_resolution | -0.000308496 | -0.000921267 | 0.000079853 | 0.472222222 | -0.006182039 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p7_4c85cdf0.csv | below_selector_resolution | 0.000022389 | -0.000033306 | 0.000101006 | 0.500000000 | 0.006174179 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p7_70c65813.csv | below_selector_resolution | -0.000251926 | -0.000957379 | 0.000102892 | 0.444444444 | 0.009475385 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s1p0_dbbbb40a.csv | below_selector_resolution | -0.000066811 | -0.000315880 | 0.000116254 | 0.472222222 | -0.004409321 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p7_b44eec88.csv | below_selector_resolution | 0.000015951 | -0.000028461 | 0.000117910 | 0.527777778 | 0.006014836 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p4_38366bc2.csv | below_selector_resolution | 0.000058089 | 0.000023881 | 0.000120842 | 0.027777778 | -0.008783645 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p4_b3f7ac13.csv | below_selector_resolution | 0.000060857 | 0.000025465 | 0.000123363 | 0.027777778 | -0.006790979 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s1p0_de46605b.csv | below_selector_resolution | 0.000087372 | 0.000042394 | 0.000124136 | 0.055555556 | -0.002560883 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s1p0_66fc29df.csv | below_selector_resolution | -0.000369768 | -0.001396438 | 0.000145222 | 0.444444444 | 0.013536265 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s1p0_ca12e8d6.csv | below_selector_resolution | -0.000391977 | -0.001230571 | 0.000153464 | 0.472222222 | -0.008831484 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s0p4_4c5567af.csv | below_selector_resolution | 0.000060066 | 0.000000731 | 0.000157845 | 0.097222222 | 0.000203570 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s1p0_49d16b09.csv | below_selector_resolution | 0.000063561 | -0.000033517 | 0.000189796 | 0.500000000 | 0.008820256 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s1p0_50e0879b.csv | below_selector_resolution | 0.000057147 | -0.000024091 | 0.000205959 | 0.458333333 | 0.008592623 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p7_c1bceab6.csv | below_selector_resolution | 0.000096201 | 0.000026420 | 0.000209796 | 0.027777778 | -0.015371379 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p7_bdaaf9a2.csv | below_selector_resolution | 0.000098993 | 0.000025183 | 0.000216231 | 0.027777778 | -0.011884212 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s1p0_107d1dc1.csv | below_selector_resolution | 0.000123923 | 0.000023701 | 0.000277944 | 0.027777778 | -0.019116673 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s1p0_161afeb3.csv | below_selector_resolution | 0.000130550 | 0.000007566 | 0.000303564 | 0.055555556 | -0.016977446 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s0p7_5b532948.csv | below_selector_resolution | 0.000118889 | 0.000007003 | 0.000303656 | 0.055555556 | 0.000356248 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p4_f2b28a54.csv | below_selector_resolution | 0.000119230 | -0.000033845 | 0.000361585 | 0.555555556 | 0.001131457 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s0p4_2ed25e15.csv | below_selector_resolution | 0.000138315 | -0.000000224 | 0.000366671 | 0.111111111 | 0.001446211 |
| submission_e331_localresid_combo_local_top_s0p55_ec217f45.csv | below_selector_resolution | -0.000052905 | -0.000731958 | 0.000375306 | 0.375000000 | -0.009244219 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s1p0_7114ebd9.csv | below_selector_resolution | 0.000182719 | 0.000014726 | 0.000445067 | 0.055555556 | 0.000508926 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s0p7_960a1b1d.csv | below_selector_resolution | 0.000264421 | 0.000010473 | 0.000664239 | 0.055555556 | 0.002530870 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p7_5b1f4ee5.csv | below_selector_resolution | 0.000238022 | -0.000036339 | 0.000680180 | 0.527777778 | 0.001980050 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s1p0_4f176a4b.csv | below_selector_resolution | 0.000398159 | 0.000022104 | 0.000971503 | 0.055555556 | 0.003615528 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s1p0_d1be19f0.csv | below_selector_resolution | 0.000400922 | -0.000007162 | 0.001015888 | 0.138888889 | 0.002828643 |

## E323-Negative Anatomy

| basename | changed_rows | changed_cells | mean_abs_logit_delta | max_abs_prob_delta | cos_with_e323_bad_delta | l1_ratio_to_e323_delta |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s1p0_f55d27bb.csv | 42 | 42 | 0.002040000 | 0.021234383 | -0.055851972 | 0.080318314 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p7_0d69fc41.csv | 42 | 42 | 0.001428000 | 0.014869186 | -0.055851972 | 0.056222820 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q80_s0p4_04e3c597.csv | 42 | 42 | 0.000816000 | 0.008498684 | -0.055851972 | 0.032127326 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s1p0_dbbbb40a.csv | 45 | 45 | 0.002114127 | 0.021234301 | -0.030859662 | 0.083236805 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p7_757d2f5a.csv | 45 | 45 | 0.001479889 | 0.014869144 | -0.030859662 | 0.058265763 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p4_d1b8887b.csv | 45 | 45 | 0.000845651 | 0.008498668 | -0.030859662 | 0.033294722 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s1p0_02a5d855.csv | 11 | 11 | 0.000534286 | 0.021233855 | -0.006876588 | 0.021035749 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p7_cf6801db.csv | 11 | 11 | 0.000374000 | 0.014859556 | -0.006876588 | 0.014725024 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_pos_q90_s0p4_01f360c3.csv | 11 | 11 | 0.000213714 | 0.008487889 | -0.006876588 | 0.008414300 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s1p0_107d1dc1.csv | 37 | 37 | 0.001797143 | 0.021242843 | -0.000000000 | 0.070756610 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p7_c1bceab6.csv | 37 | 37 | 0.001258000 | 0.014867939 | -0.000000000 | 0.049529627 |
| submission_e331_localresid_Q2_jepa_resid_subject_abs_q75_s0p4_38366bc2.csv | 37 | 37 | 0.000718857 | 0.008496499 | -0.000000000 | 0.028302644 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s1p0_d1be19f0.csv | 51 | 51 | 0.002416133 | 0.021245740 | -0.000000000 | 0.095127337 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p7_5b1f4ee5.csv | 51 | 51 | 0.001691293 | 0.014873896 | -0.000000000 | 0.066589136 |
| submission_e331_localresid_S2_raw_day_subject_pos_q80_s0p4_f2b28a54.csv | 51 | 51 | 0.000966453 | 0.008499521 | -0.000000000 | 0.038050935 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s1p0_4f176a4b.csv | 31 | 31 | 0.001504597 | 0.021234863 | -0.000000000 | 0.059238558 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s0p7_960a1b1d.csv | 31 | 31 | 0.001053218 | 0.014860447 | -0.000000000 | 0.041466991 |
| submission_e331_localresid_S2_family_dateblock_neg_q80_s0p4_2ed25e15.csv | 31 | 31 | 0.000601839 | 0.008488504 | -0.000000000 | 0.023695423 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s1p0_66fc29df.csv | 51 | 51 | 0.002355048 | 0.021243700 | -0.000000000 | 0.092722283 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p7_70c65813.csv | 51 | 51 | 0.001648533 | 0.014873418 | -0.000000000 | 0.064905598 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p4_8fe92177.csv | 51 | 51 | 0.000942019 | 0.008499792 | -0.000000000 | 0.037088913 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s1p0_161afeb3.csv | 55 | 55 | 0.002450168 | 0.021244626 | -0.000000000 | 0.096467336 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p7_bdaaf9a2.csv | 55 | 55 | 0.001715118 | 0.014873694 | -0.000000000 | 0.067527135 |
| submission_e331_localresid_Q2_jepa_resid_subject_blockabs_q65_s0p4_b3f7ac13.csv | 55 | 55 | 0.000980067 | 0.008499737 | -0.000000000 | 0.038586934 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s1p0_7114ebd9.csv | 14 | 14 | 0.000680000 | 0.021234863 | -0.000000000 | 0.026772771 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s0p7_5b532948.csv | 14 | 14 | 0.000476000 | 0.014860447 | -0.000000000 | 0.018740940 |
| submission_e331_localresid_S2_family_dateblock_neg_q90_s0p4_4c5567af.csv | 14 | 14 | 0.000272000 | 0.008488504 | -0.000000000 | 0.010709109 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p4_f93bacb8.csv | 14 | 14 | 0.000272000 | 0.008360636 | 0.000000000 | 0.010709109 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p7_56200896.csv | 14 | 14 | 0.000476000 | 0.014653719 | 0.000000000 | 0.018740940 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s1p0_5d7f5eb2.csv | 14 | 14 | 0.000680000 | 0.020963996 | 0.000000000 | 0.026772771 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p4_db9e2c3b.csv | 54 | 54 | 0.001049143 | 0.008499567 | 0.000000000 | 0.041306561 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p7_3276d49e.csv | 54 | 54 | 0.001836000 | 0.014873882 | 0.000000000 | 0.072286483 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s1p0_ca12e8d6.csv | 54 | 54 | 0.002622857 | 0.021245588 | 0.000000000 | 0.103266404 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p4_3dee5dcc.csv | 41 | 41 | 0.000796571 | 0.008493955 | 0.000000000 | 0.031362389 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p7_3117892c.csv | 41 | 41 | 0.001394000 | 0.014858115 | 0.000000000 | 0.054884181 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s1p0_de46605b.csv | 41 | 41 | 0.001991429 | 0.021214582 | 0.000000000 | 0.078405973 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p4_eaaa6d0d.csv | 46 | 46 | 0.000808222 | 0.008493057 | 0.009555583 | 0.031821101 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p7_4c85cdf0.csv | 46 | 46 | 0.001414389 | 0.014856177 | 0.009555583 | 0.055686928 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s1p0_49d16b09.csv | 46 | 46 | 0.002020556 | 0.021211290 | 0.009555583 | 0.079552754 |
| submission_e331_localresid_combo_local_top_s0p55_ec217f45.csv | 121 | 138 | 0.004610720 | 0.034964339 | 0.016373944 | 0.181532006 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p4_b5d2a430.csv | 37 | 37 | 0.000718857 | 0.008493057 | 0.043812075 | 0.028302644 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p7_b44eec88.csv | 37 | 37 | 0.001258000 | 0.014859556 | 0.043812075 | 0.049529627 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s1p0_50e0879b.csv | 37 | 37 | 0.001797143 | 0.021233855 | 0.043812075 | 0.070756610 |

## Movement-Null Stress

| basename | null_count | actual_mean | actual_p90 | actual_beats_rate | actual_strict_promote | null_mean_best | null_mean_median | null_p90_best | null_p90_median | actual_mean_dominance | actual_p90_dominance | null_strict_promote_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e331_localresid_Q1_jepa_resid_dateblock_abs_q75_s0p4_b5d2a430.csv | 12 | 0.000002536 | 0.000058629 | 0.611111111 | False | 0.000014880 | 0.000023829 | 0.000051500 | 0.000085086 | 1.000000000 | 0.916666667 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p4_3dee5dcc.csv | 12 | 0.000004734 | 0.000013802 | 0.111111111 | False | -0.000008428 | 0.000010940 | 0.000010381 | 0.000025527 | 0.750000000 | 0.833333333 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p4_db9e2c3b.csv | 12 | -0.000194429 | 0.000031454 | 0.486111111 | False | -0.000195120 | -0.000181335 | 0.000029113 | 0.000043755 | 0.916666667 | 0.833333333 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q80_s0p7_3276d49e.csv | 12 | -0.000308496 | 0.000079853 | 0.472222222 | False | -0.000300378 | -0.000290227 | 0.000069755 | 0.000089282 | 1.000000000 | 0.833333333 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_abs_q75_s0p7_3117892c.csv | 12 | 0.000033707 | 0.000045059 | 0.055555556 | False | -0.000027243 | 0.000035571 | 0.000032071 | 0.000055506 | 0.500000000 | 0.750000000 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p4_f93bacb8.csv | 12 | -0.000051329 | 0.000010272 | 0.472222222 | False | -0.000059244 | -0.000052919 | 0.000006287 | 0.000011280 | 0.416666667 | 0.666666667 | 0.000000000 |
| submission_e331_localresid_Q1_jepa_resid_dateblock_blockabs_q65_s0p4_eaaa6d0d.csv | 12 | 0.000006684 | 0.000048841 | 0.500000000 | False | 0.000002507 | 0.000018054 | 0.000016311 | 0.000058964 | 0.833333333 | 0.666666667 | 0.000000000 |
| submission_e331_localresid_Q2_jepa_resid_subject_pos_q80_s0p4_8fe92177.csv | 12 | -0.000139872 | 0.000060205 | 0.430555556 | False | -0.000170135 | -0.000141277 | -0.000000303 | 0.000064577 | 0.250000000 | 0.666666667 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s1p0_5d7f5eb2.csv | 12 | -0.000109322 | 0.000041000 | 0.472222222 | False | -0.000122732 | -0.000106903 | 0.000012141 | 0.000047566 | 0.583333333 | 0.583333333 | 0.000000000 |
| submission_e331_localresid_S2_jepa_resid_dateblock_pos_q90_s0p7_56200896.csv | 12 | -0.000083644 | 0.000023489 | 0.472222222 | False | -0.000096604 | -0.000086444 | 0.000008953 | 0.000020403 | 0.250000000 | 0.333333333 | 0.000000000 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p4_d1b8887b.csv | 12 | -0.000004314 | 0.000038245 | 0.388888889 | False | -0.000035255 | -0.000001191 | 0.000008246 | 0.000032632 | 0.583333333 | 0.250000000 | 0.000000000 |
| submission_e331_localresid_S1_family_story_subject_abs_q75_s0p7_757d2f5a.csv | 12 | -0.000027179 | 0.000072499 | 0.444444444 | False | -0.000023898 | -0.000013878 | 0.000023794 | 0.000060428 | 1.000000000 | 0.166666667 | 0.000000000 |

## Decision

Localized residual-state gates exist, but their materialized E247 actions are still not submission-grade under selector/E323/movement-null stress.

- localized gates: `39`
- generated candidates: `43`
- selector-promoted candidates: `0`
- selector+E323-safe candidates: `0`
- selector+E323+movement-null-safe candidates: `0`

## Files

- `e331_residual_state_localization_summary.csv`
- `e331_residual_state_localization_feature_nulls.csv`
- `e331_residual_state_localization_candidates.csv`
- `e331_residual_state_localization_candidate_scores.csv`
- `e331_residual_state_localization_candidate_anatomy.csv`
- `e331_residual_state_localization_movement_nulls.csv`
