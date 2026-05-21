# Channel Latent Fusion Decoder v1

## Goal

Decode the channel-independent patch encoder without collapsing everything into one day CLS vector. Each modality/channel group becomes an expert feature source, then fold-safe probes and target-wise fusion choose which latent family helps each label.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.618158`
- Drift vs v83 reference: `0.075584`
- Feature candidates: `52`

## Top Candidate Scores

| source | feature | probe | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full__cls_plus_all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_all_groups__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.623735 | 0.666471 | 0.696830 | 0.659397 | 0.568205 | 0.587902 | 0.527192 | 0.660150 |
| full__all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | full__all_groups__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.623980 | 0.670711 | 0.697421 | 0.659809 | 0.570882 | 0.585384 | 0.526661 | 0.656992 |
| full__cls_plus_physio__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_physio__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.624227 | 0.664506 | 0.701632 | 0.673486 | 0.567539 | 0.582966 | 0.529743 | 0.649714 |
| only_event__cls__subrel_train__transformer_ridge_resid_a5_w0p1 | only_event__cls__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.624925 | 0.671903 | 0.696868 | 0.674806 | 0.571870 | 0.579810 | 0.535015 | 0.644202 |
| no_sleep__cls_plus_event__subrel_train__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_event__subrel_train | transformer_logreg_c0p1_w0p1 | 0.624926 | 0.672538 | 0.689042 | 0.670880 | 0.576357 | 0.580099 | 0.537992 | 0.647572 |
| full__cls_plus_event__subrel_train__transformer_logreg_c0p1_w0p1 | full__cls_plus_event__subrel_train | transformer_logreg_c0p1_w0p1 | 0.624968 | 0.671941 | 0.686190 | 0.673054 | 0.576029 | 0.581431 | 0.537898 | 0.648231 |
| no_sleep__phone__subrel_train__transformer_ridge_resid_a5_w0p1 | no_sleep__phone__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625132 | 0.671748 | 0.694336 | 0.676185 | 0.572362 | 0.578830 | 0.535995 | 0.646472 |
| only_event__cls_plus_event__subrel_train__transformer_logreg_c0p1_w0p1 | only_event__cls_plus_event__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625160 | 0.672382 | 0.688360 | 0.667662 | 0.576913 | 0.583378 | 0.540208 | 0.647216 |
| only_event__cls_plus_all_groups__subrel_train__transformer_logreg_c0p1_w0p1 | only_event__cls_plus_all_groups__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625160 | 0.672382 | 0.688360 | 0.667662 | 0.576913 | 0.583378 | 0.540208 | 0.647216 |
| only_event__cls_plus_behavior__subrel_train__transformer_logreg_c0p1_w0p1 | only_event__cls_plus_behavior__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625160 | 0.672382 | 0.688360 | 0.667662 | 0.576913 | 0.583378 | 0.540208 | 0.647216 |
| no_sleep__cls_plus_phone__subrel_train__transformer_ridge_resid_a5_w0p1 | no_sleep__cls_plus_phone__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625192 | 0.670788 | 0.694412 | 0.673555 | 0.571347 | 0.581199 | 0.536543 | 0.648501 |
| full__physio__subrel_train__transformer_ridge_resid_a5_w0p1 | full__physio__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625417 | 0.671027 | 0.703872 | 0.673799 | 0.569480 | 0.581128 | 0.528863 | 0.649750 |
| no_sleep__cls__subrel_train__transformer_ridge_resid_a5_w0p1 | no_sleep__cls__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625466 | 0.673367 | 0.698180 | 0.674751 | 0.572361 | 0.578897 | 0.535592 | 0.645113 |
| full__cls_plus_mobility__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_mobility__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625477 | 0.672711 | 0.699004 | 0.677262 | 0.572594 | 0.579092 | 0.533142 | 0.644530 |
| only_cross_modal__cls_plus_body__subrel_train__transformer_logreg_c0p1_w0p1 | only_cross_modal__cls_plus_body__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625518 | 0.671357 | 0.688551 | 0.673288 | 0.575647 | 0.581663 | 0.540473 | 0.647644 |
| only_cross_modal__cls_plus_physio__subrel_train__transformer_logreg_c0p1_w0p1 | only_cross_modal__cls_plus_physio__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625518 | 0.671357 | 0.688551 | 0.673288 | 0.575647 | 0.581663 | 0.540473 | 0.647644 |
| full__cls__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625602 | 0.672401 | 0.698731 | 0.675061 | 0.572307 | 0.579638 | 0.534639 | 0.646440 |
| only_cross_modal__cls_plus_phone__subrel_train__transformer_ridge_resid_a5_w0p1 | only_cross_modal__cls_plus_phone__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.625628 | 0.670127 | 0.690058 | 0.674944 | 0.573464 | 0.583245 | 0.535993 | 0.651563 |
| full__cls_plus_body__subrel_train__transformer_logreg_c0p1_w0p1 | full__cls_plus_body__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625662 | 0.670276 | 0.692207 | 0.672776 | 0.577367 | 0.580456 | 0.538091 | 0.648462 |
| full__behavior__subrel_train__transformer_logreg_c0p1_w0p1 | full__behavior__subrel_train | transformer_logreg_c0p1_w0p1 | 0.625742 | 0.676776 | 0.689512 | 0.668741 | 0.575254 | 0.582896 | 0.540432 | 0.646584 |

## Target-Wise Fusion

- Target-wise avg logloss: `0.618158`
- Target-wise drift vs v83: `0.075584`

| target | source | loss |
| --- | --- | --- |
| Q1 | full__cls_plus_physio__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.664506 |
| Q2 | full__cls_plus_event__subrel_train__transformer_logreg_c0p1_w0p1 | 0.686190 |
| Q3 | full__cls_plus_all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.659397 |
| S1 | full__cls_plus_physio__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.567539 |
| S2 | full__mobility__subrel_train__transformer_logreg_c0p1_w0p1 | 0.578611 |
| S3 | full__all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.526661 |
| S4 | only_event__cls__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.644202 |

## Channel Groups

| view | group | channels |
| --- | --- | --- |
| no_sleep | ambience | 7 |
| no_sleep | body | 5 |
| no_sleep | cross | 2 |
| no_sleep | event | 37 |
| no_sleep | light | 3 |
| no_sleep | mobility | 11 |
| no_sleep | other | 2 |
| no_sleep | phone | 12 |
| no_sleep | radio | 8 |
| full | ambience | 7 |
| full | body | 17 |
| full | cross | 2 |
| full | event | 45 |
| full | light | 6 |
| full | mobility | 11 |
| full | other | 2 |
| full | phone | 12 |
| full | radio | 8 |
| only_event | event | 45 |
| only_cross_modal | ambience | 7 |
| only_cross_modal | body | 1 |
| only_cross_modal | cross | 2 |
| only_cross_modal | event | 45 |
| only_cross_modal | mobility | 8 |
| only_cross_modal | phone | 6 |

## Decision

This is the first decoder that reads modality/channel latents rather than only the collapsed CLS day embedding. A positive result would mean the encoder should expose expert latents directly; a negative result means the SSL objective still does not make channel latents label-readable enough.