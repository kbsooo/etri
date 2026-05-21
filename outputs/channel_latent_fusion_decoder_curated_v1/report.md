# Channel Latent Fusion Decoder v1

## Goal

Decode the channel-independent patch encoder without collapsing everything into one day CLS vector. Each modality/channel group becomes an expert feature source, then fold-safe probes and target-wise fusion choose which latent family helps each label.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.616980`
- Drift vs v83 reference: `0.077224`
- Feature candidates: `102`

## Top Candidate Scores

| source | feature | probe | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full__cls_plus_all_groups__transformer_logreg_c0p1_w0p1 | full__cls_plus_all_groups | transformer_logreg_c0p1_w0p1 | 0.622843 | 0.670723 | 0.690626 | 0.668694 | 0.573381 | 0.578684 | 0.526235 | 0.651554 |
| full__cls_plus_all_groups__abs_plus_subrel_train__transformer_logreg_c0p1_w0p1 | full__cls_plus_all_groups__abs_plus_subrel_train | transformer_logreg_c0p1_w0p1 | 0.623583 | 0.670733 | 0.693817 | 0.668460 | 0.574761 | 0.580277 | 0.526221 | 0.650813 |
| no_sleep__cls_plus_behavior__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_behavior | transformer_logreg_c0p1_w0p1 | 0.623729 | 0.670727 | 0.690833 | 0.670917 | 0.571633 | 0.577315 | 0.531961 | 0.652719 |
| full__cls_plus_all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_all_groups__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.623735 | 0.666471 | 0.696830 | 0.659397 | 0.568205 | 0.587902 | 0.527192 | 0.660150 |
| full__all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | full__all_groups__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.623980 | 0.670711 | 0.697421 | 0.659809 | 0.570882 | 0.585384 | 0.526661 | 0.656992 |
| full__cls_plus_physio__transformer_logreg_c0p1_w0p1 | full__cls_plus_physio | transformer_logreg_c0p1_w0p1 | 0.624003 | 0.669612 | 0.698600 | 0.672249 | 0.572655 | 0.576579 | 0.530236 | 0.648088 |
| full__all_groups__transformer_logreg_c0p1_w0p1 | full__all_groups | transformer_logreg_c0p1_w0p1 | 0.624214 | 0.673449 | 0.692011 | 0.669738 | 0.576420 | 0.579381 | 0.527804 | 0.650697 |
| full__cls_plus_physio__subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_physio__subrel_train | transformer_ridge_resid_a5_w0p1 | 0.624227 | 0.664506 | 0.701632 | 0.673486 | 0.567539 | 0.582966 | 0.529743 | 0.649714 |
| full__cls_plus_behavior__transformer_logreg_c0p1_w0p1 | full__cls_plus_behavior | transformer_logreg_c0p1_w0p1 | 0.624359 | 0.673787 | 0.692178 | 0.671369 | 0.575466 | 0.578427 | 0.530688 | 0.648602 |
| only_cross_modal__cls_plus_mobility__transformer_logreg_c0p1_w0p1 | only_cross_modal__cls_plus_mobility | transformer_logreg_c0p1_w0p1 | 0.624382 | 0.673320 | 0.693487 | 0.673903 | 0.574703 | 0.576064 | 0.531626 | 0.647571 |
| full__cls_plus_physio__abs_plus_subrel_train__transformer_ridge_resid_a5_w0p1 | full__cls_plus_physio__abs_plus_subrel_train | transformer_ridge_resid_a5_w0p1 | 0.624389 | 0.662714 | 0.705333 | 0.676063 | 0.564499 | 0.581118 | 0.529225 | 0.651773 |
| full__all_groups__abs_plus_subrel_train__transformer_logreg_c0p1_w0p1 | full__all_groups__abs_plus_subrel_train | transformer_logreg_c0p1_w0p1 | 0.624488 | 0.675478 | 0.695032 | 0.668229 | 0.575337 | 0.580238 | 0.526269 | 0.650836 |
| no_sleep__cls_plus_event__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_event | transformer_logreg_c0p1_w0p1 | 0.624513 | 0.673810 | 0.692248 | 0.672676 | 0.575775 | 0.577142 | 0.531304 | 0.648635 |
| only_event__cls__abs_plus_subrel_train__transformer_ridge_resid_a5_w0p1 | only_event__cls__abs_plus_subrel_train | transformer_ridge_resid_a5_w0p1 | 0.624579 | 0.671344 | 0.697021 | 0.675438 | 0.569983 | 0.579365 | 0.535085 | 0.643818 |
| only_event__cls__transformer_ridge_resid_a5_w0p1 | only_event__cls | transformer_ridge_resid_a5_w0p1 | 0.624591 | 0.672394 | 0.695996 | 0.674121 | 0.572653 | 0.577357 | 0.533711 | 0.645908 |
| no_sleep__cls_plus_behavior__abs_plus_subrel_train__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_behavior__abs_plus_subrel_train | transformer_logreg_c0p1_w0p1 | 0.624606 | 0.670828 | 0.693703 | 0.670671 | 0.572134 | 0.579692 | 0.533625 | 0.651590 |
| no_sleep__cls_plus_all_groups__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_all_groups | transformer_logreg_c0p1_w0p1 | 0.624708 | 0.678290 | 0.688375 | 0.675439 | 0.571058 | 0.580714 | 0.530487 | 0.648594 |
| only_cross_modal__cls_plus_behavior__transformer_logreg_c0p1_w0p1 | only_cross_modal__cls_plus_behavior | transformer_logreg_c0p1_w0p1 | 0.624759 | 0.676821 | 0.690924 | 0.668564 | 0.575899 | 0.578130 | 0.530999 | 0.651975 |
| no_sleep__cls_plus_phone__abs_plus_subrel_train__transformer_logreg_c0p1_w0p1 | no_sleep__cls_plus_phone__abs_plus_subrel_train | transformer_logreg_c0p1_w0p1 | 0.624772 | 0.670099 | 0.693343 | 0.673983 | 0.571417 | 0.580217 | 0.535166 | 0.649181 |
| only_cross_modal__cls_plus_all_groups__transformer_logreg_c0p1_w0p1 | only_cross_modal__cls_plus_all_groups | transformer_logreg_c0p1_w0p1 | 0.624845 | 0.677913 | 0.690620 | 0.669107 | 0.574779 | 0.578381 | 0.531296 | 0.651819 |

## Target-Wise Fusion

- Target-wise avg logloss: `0.616980`
- Target-wise drift vs v83: `0.077224`

| target | source | loss |
| --- | --- | --- |
| Q1 | full__cls_plus_physio__abs_plus_subrel_train__transformer_ridge_resid_a5_w0p1 | 0.662714 |
| Q2 | only_cross_modal__cls_plus_all_groups__subrel_train__transformer_logreg_c0p1_w0p1 | 0.686355 |
| Q3 | full__cls_plus_all_groups__subrel_train__transformer_ridge_resid_a5_w0p1 | 0.659397 |
| S1 | full__cls_plus_physio__abs_plus_subrel_train__transformer_ridge_resid_a5_w0p1 | 0.564499 |
| S2 | full__cls_plus_body__transformer_logreg_c0p1_w0p1 | 0.575857 |
| S3 | full__cls_plus_all_groups__abs_plus_subrel_train__transformer_logreg_c0p1_w0p1 | 0.526221 |
| S4 | only_event__cls__abs_plus_subrel_train__transformer_ridge_resid_a5_w0p1 | 0.643818 |

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