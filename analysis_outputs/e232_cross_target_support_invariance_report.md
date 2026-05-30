# E232 Cross-Target Support Invariance

## Question

Do E216 S2, E224 Q3, and E224 S4 support tails share one latent support boundary, or are they target-specific?

## Observed Read

- Max absolute row-label correlation across target support labels: `0.057278`.
- Max absolute benefit correlation: `0.090611`.
- Best held-out target transfer AUC: `0.745452` from `only_q3_e224` to `s4_e224` using `movement` / `lr_l2_c0p10`.
- Best movement-only transfer AUC: `0.745452`; best latent-context transfer AUC: `0.707003`.
- Test-side low-support overlap for Q3-vs-S2 at top25: `1` rows.

Interpretation: support-tail risk is not a shared row/block latent. The transferable part is mostly movement-shape calibration, not row identity or JEPA latent context. This argues for target-specific JEPA support/energy targets with a separate movement-shape regularizer, rather than one shared support gate.

## Label Overlap

| pair | support_rate_a | support_rate_b | label_corr | benefit_corr | good_jaccard | bad_jaccard | same_label_rate | both_good_rate | both_bad_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224__s2_e216 | 0.502222222 | 0.551111111 | 0.012946961 | -0.023987679 | 0.362068966 | 0.314814815 | 0.506666667 | 0.280000000 | 0.226666667 |
| q3_e224__s4_e224 | 0.502222222 | 0.271111111 | 0.057278000 | 0.090611141 | 0.238434164 | 0.441253264 | 0.524444444 | 0.148888889 | 0.375555556 |
| s2_e216__s4_e224 | 0.551111111 | 0.271111111 | -0.002367486 | 0.022246344 | 0.221122112 | 0.383812010 | 0.475555556 | 0.148888889 | 0.326666667 |

## Subject-Level Support Correlation

| pair | subject_rate_corr |
| --- | --- |
| q3_e224__s2_e216 | -0.442383849 |
| q3_e224__s4_e224 | 0.128085380 |
| s2_e216__s4_e224 | -0.491325695 |

## Best Within-Target OOF Models

| view | task | model | split | auc | logloss | brier | corr_benefit | support_rate | n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| movement | q3_e224 | lr_l2_c0p10 | subject5 | 0.602243995 | 0.679288921 | 0.242946145 | -0.003439603 | 0.502222222 | 450 |
| movement | q3_e224 | hgb_shallow | subject5 | 0.597355009 | 0.693477401 | 0.248701589 | -0.053730591 | 0.502222222 | 450 |
| movement | q3_e224 | lr_l2_c0p10 | stratified5 | 0.593611726 | 0.684873951 | 0.245460860 | -0.035123055 | 0.502222222 | 450 |
| movement | s2_e216 | hgb_shallow | subject5 | 0.747494810 | 0.587682404 | 0.201085512 | -0.008037191 | 0.551111111 | 450 |
| movement | s2_e216 | hgb_shallow | stratified5 | 0.745798068 | 0.589563774 | 0.202110306 | -0.033224916 | 0.551111111 | 450 |
| latent_no_targetid | s2_e216 | hgb_shallow | stratified5 | 0.729479400 | 0.607621556 | 0.208467599 | -0.041537714 | 0.551111111 | 450 |
| movement | s4_e224 | hgb_shallow | stratified5 | 0.865816174 | 0.386136998 | 0.130680249 | 0.051505668 | 0.271111111 | 450 |
| movement | s4_e224 | hgb_shallow | subject5 | 0.833491603 | 0.416348407 | 0.143635329 | 0.063184223 | 0.271111111 | 450 |
| movement | s4_e224 | lr_l2_c0p10 | stratified5 | 0.802603958 | 0.534167200 | 0.175808047 | 0.067772472 | 0.271111111 | 450 |

## Best Cross-Target Transfer Rows

| view | source | target | model | source_support_rate | target_support_rate | auc | logloss | brier | corr_benefit | mean_pred | n_source | n_target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| movement | only_q3_e224 | s4_e224 | lr_l2_c0p10 | 0.502222222 | 0.271111111 | 0.745451819 | 0.599141467 | 0.204459197 | 0.018660194 | 0.446225295 | 450 | 450 |
| movement | q3_s4_e224 | s2_e216 | hgb_shallow | 0.386666667 | 0.551111111 | 0.745408815 | 0.606383117 | 0.208042533 | 0.028441089 | 0.498946512 | 900 | 450 |
| movement | only_q3_e224 | s2_e216 | hgb_shallow | 0.502222222 | 0.551111111 | 0.728650990 | 0.603649144 | 0.207175763 | -0.001165743 | 0.514801703 | 450 | 450 |
| movement | s2_q3 | s4_e224 | lr_l2_c0p10 | 0.526666667 | 0.271111111 | 0.710490804 | 0.641826286 | 0.223900576 | -0.037202780 | 0.489459021 | 900 | 450 |
| latent_with_targetid | q3_s4_e224 | s2_e216 | hgb_shallow | 0.386666667 | 0.551111111 | 0.707002555 | 0.637292558 | 0.222920118 | 0.022976671 | 0.482580651 | 900 | 450 |
| latent_no_targetid | q3_s4_e224 | s2_e216 | hgb_shallow | 0.386666667 | 0.551111111 | 0.707002555 | 0.637292558 | 0.222920118 | 0.022976671 | 0.482580651 | 900 | 450 |
| movement | s2_s4 | q3_e224 | hgb_shallow | 0.411111111 | 0.502222222 | 0.683776470 | 0.636307636 | 0.222873496 | 0.014946273 | 0.507652014 | 900 | 450 |
| movement | only_s4_e224 | s2_e216 | hgb_shallow | 0.271111111 | 0.551111111 | 0.682639332 | 0.665714265 | 0.232935366 | -0.007784667 | 0.465108043 | 450 | 450 |
| latent_no_targetid | s2_s4 | q3_e224 | hgb_shallow | 0.411111111 | 0.502222222 | 0.675707174 | 0.641733338 | 0.225481467 | 0.062813022 | 0.512781527 | 900 | 450 |
| latent_with_targetid | s2_s4 | q3_e224 | hgb_shallow | 0.411111111 | 0.502222222 | 0.675707174 | 0.641733338 | 0.225481467 | 0.062813022 | 0.512781527 | 900 | 450 |
| movement | only_q3_e224 | s2_e216 | lr_l2_c0p10 | 0.502222222 | 0.551111111 | 0.675403226 | 0.661369620 | 0.234562692 | 0.050769838 | 0.463375510 | 450 | 450 |
| movement | only_s2_e216 | q3_e224 | hgb_shallow | 0.551111111 | 0.502222222 | 0.674907159 | 0.642419878 | 0.225898850 | 0.030943558 | 0.535409920 | 450 | 450 |
| movement | only_s2_e216 | s4_e224 | lr_l2_c0p10 | 0.551111111 | 0.271111111 | 0.671606357 | 0.629804044 | 0.217747120 | -0.040519820 | 0.468329796 | 450 | 450 |
| movement | only_s2_e216 | q3_e224 | lr_l2_c0p10 | 0.551111111 | 0.502222222 | 0.656822851 | 0.665360271 | 0.236205501 | -0.013570325 | 0.510966384 | 450 | 450 |
| latent_no_targetid | s2_q3 | s4_e224 | lr_l2_c0p10 | 0.526666667 | 0.271111111 | 0.649990004 | 0.679294212 | 0.238163282 | 0.076413239 | 0.468281630 | 900 | 450 |
| latent_with_targetid | s2_q3 | s4_e224 | lr_l2_c0p10 | 0.526666667 | 0.271111111 | 0.647016194 | 0.736297928 | 0.262366720 | 0.073635694 | 0.517888764 | 900 | 450 |
| movement | q3_s4_e224 | s2_e216 | lr_l2_c0p10 | 0.386666667 | 0.551111111 | 0.646937879 | 0.688489756 | 0.238639318 | 0.029733640 | 0.491206141 | 900 | 450 |
| movement | s2_s4 | q3_e224 | lr_l2_c0p10 | 0.411111111 | 0.502222222 | 0.636733565 | 0.695330669 | 0.248453572 | 0.076133663 | 0.597889117 | 900 | 450 |
| movement | only_s4_e224 | q3_e224 | hgb_shallow | 0.271111111 | 0.502222222 | 0.635252054 | 0.671267242 | 0.238879854 | 0.033583288 | 0.462355614 | 450 | 450 |
| latent_with_targetid | s2_s4 | q3_e224 | lr_l2_c0p10 | 0.411111111 | 0.502222222 | 0.632427307 | 0.751154368 | 0.264088557 | 0.138223476 | 0.608820355 | 900 | 450 |

## Weak Single-Source Transfer Rows

| view | source | target | model | source_support_rate | target_support_rate | auc | logloss | brier | corr_benefit | mean_pred | n_source | n_target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| latent_no_targetid | only_s4_e224 | s2_e216 | hgb_shallow | 0.271111111 | 0.551111111 | 0.523554775 | 0.772425066 | 0.284263028 | -0.009858396 | 0.416312067 | 450 | 450 |
| latent_with_targetid | only_s4_e224 | s2_e216 | hgb_shallow | 0.271111111 | 0.551111111 | 0.523554775 | 0.772425066 | 0.284263028 | -0.009858396 | 0.416312067 | 450 | 450 |
| latent_with_targetid | only_s2_e216 | s4_e224 | hgb_shallow | 0.551111111 | 0.271111111 | 0.535360856 | 0.778432044 | 0.288239988 | 0.024586259 | 0.538841711 | 450 | 450 |
| latent_no_targetid | only_s2_e216 | s4_e224 | hgb_shallow | 0.551111111 | 0.271111111 | 0.535360856 | 0.778432044 | 0.288239988 | 0.024586259 | 0.538841711 | 450 | 450 |
| movement | only_q3_e224 | s4_e224 | hgb_shallow | 0.502222222 | 0.271111111 | 0.544782087 | 0.700673114 | 0.253420410 | -0.035527930 | 0.499406836 | 450 | 450 |
| latent_no_targetid | only_s4_e224 | s2_e216 | lr_l2_c0p10 | 0.271111111 | 0.551111111 | 0.562679655 | 0.984103548 | 0.314323182 | -0.025559234 | 0.504757989 | 450 | 450 |
| latent_with_targetid | only_s4_e224 | s2_e216 | lr_l2_c0p10 | 0.271111111 | 0.551111111 | 0.562679655 | 0.984103548 | 0.314323182 | -0.025559234 | 0.504757989 | 450 | 450 |
| latent_with_targetid | only_s4_e224 | q3_e224 | hgb_shallow | 0.271111111 | 0.502222222 | 0.567813685 | 0.722079341 | 0.261276196 | 0.061643322 | 0.454425894 | 450 | 450 |
| latent_no_targetid | only_s4_e224 | q3_e224 | hgb_shallow | 0.271111111 | 0.502222222 | 0.567813685 | 0.722079341 | 0.261276196 | 0.061643322 | 0.454425894 | 450 | 450 |
| latent_with_targetid | only_q3_e224 | s4_e224 | hgb_shallow | 0.502222222 | 0.271111111 | 0.568822471 | 0.712892485 | 0.258422335 | 0.077873253 | 0.495364297 | 450 | 450 |
| latent_no_targetid | only_q3_e224 | s4_e224 | hgb_shallow | 0.502222222 | 0.271111111 | 0.568822471 | 0.712892485 | 0.258422335 | 0.077873253 | 0.495364297 | 450 | 450 |

## Test-Side Low-Support Overlap

| pair | k | low_support_overlap | low_support_jaccard | corr_pred | mean_pred_a | mean_pred_b |
| --- | --- | --- | --- | --- | --- | --- |
| q3_e224__s2_e216 | 10 | 0 | 0.000000000 | -0.143655133 | 0.513882638 | 0.541137512 |
| q3_e224__s2_e216 | 25 | 1 | 0.020408163 | -0.143655133 | 0.513882638 | 0.541137512 |
| q3_e224__s2_e216 | 50 | 8 | 0.086956522 | -0.143655133 | 0.513882638 | 0.541137512 |
| q3_e224__s2_e216 | 80 | 25 | 0.185185185 | -0.143655133 | 0.513882638 | 0.541137512 |
| q3_e224__s2_e216 | 111 | 47 | 0.268571429 | -0.143655133 | 0.513882638 | 0.541137512 |
| q3_e224__s4_e224 | 10 | 0 | 0.000000000 | 0.044020743 | 0.513882638 | 0.214199036 |
| q3_e224__s4_e224 | 25 | 2 | 0.041666667 | 0.044020743 | 0.513882638 | 0.214199036 |
| q3_e224__s4_e224 | 50 | 12 | 0.136363636 | 0.044020743 | 0.513882638 | 0.214199036 |
| q3_e224__s4_e224 | 80 | 28 | 0.212121212 | 0.044020743 | 0.513882638 | 0.214199036 |
| q3_e224__s4_e224 | 111 | 57 | 0.345454545 | 0.044020743 | 0.513882638 | 0.214199036 |
| s2_e216__s4_e224 | 10 | 1 | 0.052631579 | -0.053351595 | 0.541137512 | 0.214199036 |
| s2_e216__s4_e224 | 25 | 4 | 0.086956522 | -0.053351595 | 0.541137512 | 0.214199036 |
| s2_e216__s4_e224 | 50 | 12 | 0.136363636 | -0.053351595 | 0.541137512 | 0.214199036 |
| s2_e216__s4_e224 | 80 | 25 | 0.185185185 | -0.053351595 | 0.541137512 | 0.214199036 |
| s2_e216__s4_e224 | 111 | 47 | 0.268571429 | -0.053351595 | 0.541137512 | 0.214199036 |

## Decision

- Reject a single shared row-support regularizer for S2/Q3/S4 under the current E216/E224 translations.
- Keep the movement-shape signal as a calibration diagnostic: it transfers better than row-label overlap, but it is not enough to select public-safe rows.
- Future JEPA work should create target-specific support/energy heads, especially for S2 and Q3, and should treat S4 as the healthier body component rather than a proxy for Q3/S2 support.
