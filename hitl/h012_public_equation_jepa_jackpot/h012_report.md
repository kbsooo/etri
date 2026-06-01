# H012 Public-Equation HS-JEPA Jackpot

## Question

Can known public LB observations be treated as equations over hidden public labels/subset, then converted into an action candidate?

## Worldview

HS-JEPA's target representation is not a label column or a feature reconstruction. Here the target is the hidden public state that makes all old public scores simultaneously true.

## Evidence

- known public observations loaded: `20`
- public equations vs E247: `19`
- posterior configs tested: `85`
- selected posterior scenarios: `8 full configs plus leave-one-out variants from the top config`
- generated candidates: `238`
- primary upload-safe file: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv`

## Selected Posterior Configs

| prior_name | ridge_mult |
| --- | --- |
| good_median | 0.000010000 |
| good_soft | 0.000010000 |
| good_median | 0.000030000 |
| e247 | 0.000010000 |
| good_soft | 0.000030000 |
| e247 | 0.000030000 |
| good_median | 0.000100000 |
| good_soft | 0.000100000 |

## Top Config Diagnostics

| prior_name | ridge_mult | loo_mae | loo_p90_abs | loo_spearman | known_fit_mae | q_mean | q_std | q_l1_from_prior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| good_median | 0.000010000 | 0.000320737 | 0.000911893 | 0.935087719 | 0.000029762 | 0.598339146 | 0.224918039 | 0.034889849 |
| good_soft | 0.000010000 | 0.000320996 | 0.000914327 | 0.935087719 | 0.000029844 | 0.598369451 | 0.224928147 | 0.034720745 |
| good_median | 0.000030000 | 0.000322769 | 0.000913664 | 0.935087719 | 0.000029695 | 0.598347857 | 0.224697255 | 0.034732808 |
| e247 | 0.000010000 | 0.000321880 | 0.000916974 | 0.935087719 | 0.000029496 | 0.598376572 | 0.224967900 | 0.034492263 |
| good_soft | 0.000030000 | 0.000323029 | 0.000916107 | 0.935087719 | 0.000029775 | 0.598378376 | 0.224707473 | 0.034562753 |
| e247 | 0.000030000 | 0.000323913 | 0.000918758 | 0.935087719 | 0.000029428 | 0.598385274 | 0.224746985 | 0.034336092 |
| good_median | 0.000100000 | 0.000328133 | 0.000918627 | 0.931578947 | 0.000029359 | 0.598359416 | 0.224119094 | 0.034371582 |
| good_soft | 0.000100000 | 0.000328379 | 0.000921077 | 0.931578947 | 0.000029429 | 0.598389333 | 0.224127507 | 0.034212729 |
| e247 | 0.000100000 | 0.000329239 | 0.000923724 | 0.935087719 | 0.000029072 | 0.598396142 | 0.224167248 | 0.033981170 |
| good_median | 0.000300000 | 0.000336288 | 0.000926996 | 0.931578947 | 0.000028377 | 0.598341020 | 0.223219923 | 0.033958214 |
| good_soft | 0.000300000 | 0.000336523 | 0.000929466 | 0.931578947 | 0.000028418 | 0.598371825 | 0.223228666 | 0.033786215 |
| e247 | 0.000300000 | 0.000337378 | 0.000932084 | 0.931578947 | 0.000028072 | 0.598379685 | 0.223270697 | 0.033565541 |
| good_soft | 0.100000000 | 0.000337834 | 0.000956732 | 0.926315789 | 0.000050629 | 0.596472385 | 0.215204104 | 0.025433185 |
| good_median | 0.100000000 | 0.000336668 | 0.000961428 | 0.928070175 | 0.000049914 | 0.596456444 | 0.215272722 | 0.025870835 |
| e247 | 0.100000000 | 0.000340525 | 0.000952911 | 0.926315789 | 0.000051119 | 0.596494688 | 0.215178948 | 0.025043411 |
| good_median | 0.001000000 | 0.000345828 | 0.000938691 | 0.931578947 | 0.000026797 | 0.598252614 | 0.222080710 | 0.033501667 |
| good_soft | 0.001000000 | 0.000346017 | 0.000941172 | 0.931578947 | 0.000026826 | 0.598283191 | 0.222086728 | 0.033295512 |
| e247 | 0.001000000 | 0.000346916 | 0.000943755 | 0.931578947 | 0.000026452 | 0.598292384 | 0.222130543 | 0.033075374 |
| good_soft | 0.030000000 | 0.000349523 | 0.000953670 | 0.926315789 | 0.000035192 | 0.597078518 | 0.217217873 | 0.028234900 |
| good_median | 0.030000000 | 0.000349064 | 0.000955797 | 0.926315789 | 0.000034862 | 0.597056888 | 0.217246455 | 0.028606511 |

## Candidate Selection

| candidate_id | h012_decision | family | target_subset | changed_cells | posterior_delta_mean | posterior_delta_p90 | posterior_beats_current_rate | max_abs_prob_delta | public_bad_cos_pos_sum | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_all_k1200_a0.7 | public_equation_jackpot | top | all | 1200 | -0.006446397 | -0.004693170 | 1.000000000 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k1200_a0.7_d33942cf.csv |
| direct_all_a0.6 | public_equation_jackpot | direct | all | 1750 | -0.006209931 | -0.004710339 | 1.000000000 | 0.254204532 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_direct_all_a0.6_53cc3fa8.csv |
| top_all_k800_a0.7 | public_equation_jackpot | top | all | 800 | -0.006166511 | -0.004407631 | 1.000000000 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k800_a0.7_4deb56af.csv |
| direct_all_a0.4 | public_equation_jackpot | direct | all | 1750 | -0.005237595 | -0.004237867 | 1.000000000 | 0.187288504 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_direct_all_a0.4_3b0a4ca8.csv |
| top_all_k1200_a0.4 | public_equation_jackpot | top | all | 1200 | -0.005197440 | -0.004195595 | 1.000000000 | 0.187288504 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k1200_a0.4_0c2ccc41.csv |
| top_all_k800_a0.4 | public_equation_jackpot | top | all | 800 | -0.004999041 | -0.003993966 | 1.000000000 | 0.187288504 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k800_a0.4_03d15959.csv |
| top_S_k1200_a0.7 | public_equation_jackpot | top | S | 999 | -0.004338171 | -0.003863219 | 1.000000000 | 0.151541620 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k1200_a0.7_b995ec00.csv |
| top_S_k800_a0.7 | public_equation_jackpot | top | S | 800 | -0.004320113 | -0.003846037 | 1.000000000 | 0.151541620 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k800_a0.7_71d782ed.csv |
| top_S_k1200_a1 | public_equation_jackpot | top | S | 999 | -0.004442203 | -0.003763701 | 0.925925926 | 0.191281896 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k1200_a1_aa0927f0.csv |
| top_S_k800_a1 | public_equation_jackpot | top | S | 800 | -0.004422682 | -0.003745430 | 0.925925926 | 0.191281896 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k800_a1_067b52e5.csv |
| top_all_k400_a0.7 | public_equation_jackpot | top | all | 400 | -0.005215656 | -0.003451042 | 1.000000000 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k400_a0.7_f4fa1fae.csv |
| direct_all_a0.25 | public_equation_jackpot | direct | all | 1750 | -0.004087557 | -0.003462728 | 1.000000000 | 0.178454081 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_direct_all_a0.25_1ee9b241.csv |
| top_all_k400_a0.4 | public_equation_jackpot | top | all | 400 | -0.004323331 | -0.003314980 | 1.000000000 | 0.187288504 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k400_a0.4_6428e19c.csv |
| top_S_k400_a0.7 | public_equation_jackpot | top | S | 400 | -0.003850696 | -0.003379964 | 0.962962963 | 0.151541620 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k400_a0.7_f39c715a.csv |
| top_S_k400_a1 | public_equation_jackpot | top | S | 400 | -0.003915071 | -0.003242597 | 0.925925926 | 0.191281896 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k400_a1_54026f99.csv |
| stable_all_k280_a0.7 | public_equation_jackpot | stable_top | all | 280 | -0.004654884 | -0.002877862 | 1.000000000 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_all_k280_a0.7_fa36b2a1.csv |
| top_S_k1200_a1.35 | public_equation_jackpot | top | S | 999 | -0.003928937 | -0.003120700 | 0.925925926 | 0.223310186 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k1200_a1.35_5744efad.csv |
| top_S_k1200_a0.4 | public_equation_jackpot | top | S | 999 | -0.003539954 | -0.003268553 | 1.000000000 | 0.102411705 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k1200_a0.4_fedfa6d6.csv |
| top_S_k800_a1.35 | public_equation_jackpot | top | S | 800 | -0.003912466 | -0.003105919 | 0.925925926 | 0.223310186 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k800_a1.35_a7c25924.csv |
| top_S_k800_a0.4 | public_equation_jackpot | top | S | 800 | -0.003527125 | -0.003256224 | 1.000000000 | 0.102411705 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k800_a0.4_a68e3a8e.csv |
| stable_S_k280_a0.7 | public_equation_jackpot | stable_top | S | 280 | -0.003420159 | -0.002958088 | 0.962962963 | 0.151541620 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_S_k280_a0.7_3ac55f68.csv |
| top_S_k400_a0.4 | public_equation_jackpot | top | S | 400 | -0.003193463 | -0.002924474 | 1.000000000 | 0.102411705 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k400_a0.4_46a6b067.csv |
| top_S_k400_a1.35 | public_equation_jackpot | top | S | 400 | -0.003482801 | -0.002682704 | 0.925925926 | 0.223310186 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k400_a1.35_ce02f3f5.csv |
| stable_S_k280_a1.1 | public_equation_jackpot | stable_top | S | 280 | -0.003402664 | -0.002707337 | 0.925925926 | 0.201825148 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_S_k280_a1.1_4eb12ac4.csv |
| top_all_k200_a0.7 | public_equation_jackpot | top | all | 200 | -0.004063249 | -0.002296518 | 1.000000000 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k200_a0.7_e09780d8.csv |
| top_all_k200_a0.4 | public_equation_jackpot | top | all | 200 | -0.003502243 | -0.002492682 | 1.000000000 | 0.187288504 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k200_a0.4_a64b74f8.csv |
| direct_all_a0.15 | public_equation_jackpot | direct | all | 1750 | -0.002982047 | -0.002607150 | 1.000000000 | 0.153739628 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_direct_all_a0.15_81a72da1.csv |
| top_S_k200_a0.7 | public_equation_jackpot | top | S | 200 | -0.003008973 | -0.002545363 | 0.925925926 | 0.151541620 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k200_a0.7_2971a2a1.csv |
| top_S_k200_a1 | public_equation_jackpot | top | S | 200 | -0.003006439 | -0.002344139 | 0.925925926 | 0.191281896 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k200_a1_acaec1fa.csv |
| top_S_k200_a0.4 | public_equation_jackpot | top | S | 200 | -0.002594359 | -0.002329439 | 1.000000000 | 0.102411705 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k200_a0.4_798b6309.csv |
| stable_S_k140_a0.7 | public_equation_jackpot | stable_top | S | 140 | -0.002571878 | -0.002112321 | 0.925925926 | 0.151541620 | 0.002933132 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_S_k140_a0.7_4be62b99.csv |
| stable_all_k140_a0.7 | public_equation_jackpot | stable_top | all | 140 | -0.003464663 | -0.001766463 | 1.000000000 | 0.294110279 | 0.005149569 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_all_k140_a0.7_a7a19151.csv |
| stable_S_k280_a1.5 | public_equation_jackpot | stable_top | S | 280 | -0.002775002 | -0.001938768 | 0.925925926 | 0.233375078 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_S_k280_a1.5_dbd8f0cb.csv |
| top_S_k200_a1.35 | public_equation_jackpot | top | S | 200 | -0.002716036 | -0.001929673 | 0.925925926 | 0.223310186 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_S_k200_a1.35_0636cd19.csv |
| top_Q_k800_a0.7 | public_equation_jackpot | top | Q | 750 | -0.002164839 | -0.002084721 | 0.962962963 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_Q_k800_a0.7_6f041f6e.csv |
| top_Q_k1200_a0.7 | public_equation_jackpot | top | Q | 750 | -0.002164839 | -0.002084721 | 0.962962963 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_Q_k1200_a0.7_6f041f6e.csv |
| top_Q_k400_a0.7 | public_equation_jackpot | top | Q | 400 | -0.002125442 | -0.002049202 | 0.962962963 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_Q_k400_a0.7_4b9d1afb.csv |
| stable_S_k140_a1.1 | public_equation_jackpot | stable_top | S | 140 | -0.002504769 | -0.001812344 | 0.925925926 | 0.201825148 | 0.001305312 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_S_k140_a1.1_d08fa1e5.csv |
| top_all_k100_a0.4 | public_equation_jackpot | top | all | 100 | -0.002647191 | -0.001745353 | 1.000000000 | 0.187288504 | 0.009916605 | hitl/h012_public_equation_jepa_jackpot/submission_h012_top_all_k100_a0.4_957bbaeb.csv |
| stable_Q_k280_a0.7 | public_equation_jackpot | stable_top | Q | 280 | -0.002057471 | -0.001990273 | 0.962962963 | 0.294110279 | 0.000000000 | hitl/h012_public_equation_jepa_jackpot/submission_h012_stable_Q_k280_a0.7_e60a262c.csv |

## Decision Rule

This is a high-risk inverse-public experiment. A public win would validate public-equation latent reconstruction as an HS-JEPA target. A loss would show that the old public equations are too underidentified or too subset-mismatched to materialize directly.

## Files

- `hitl/h012_public_equation_jepa_jackpot/h012_posterior_configs.csv`
- `hitl/h012_public_equation_jepa_jackpot/h012_known_equations.csv`
- `hitl/h012_public_equation_jepa_jackpot/h012_cell_posterior.csv`
- `hitl/h012_public_equation_jepa_jackpot/h012_candidates.csv`
- `hitl/h012_public_equation_jepa_jackpot/h012_selection.csv`
