# E108 E101-Win Amplitude Follow-Up

## Question

E107 says E104 amplitude-up should only become actionable if E101 wins. This
materializes the two useful post-feedback branches without changing the current
pre-feedback recommendation.

## Candidate Files

| role | output_file | risk_posture | graft_alpha | e101_pass | active_cells_vs_e95 | edge_win_mean_vs_e101 | edge_win_p95_vs_e101 | edge_win_beat_e101_rate | edge_win_rank_vs_e101 | small_win_mean_vs_e101 | small_win_p95_vs_e101 | small_win_beat_e101_rate | small_win_rank_vs_e101 | tie_p95_vs_e101 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| if_e101win_risk_amp050 | submission_e108_if_e101win_amp050_079aab57.csv | risk_tolerant_top_conditional | 0.500000000 | False | 50 | -0.000012556 | -0.000009546 | 1.000000000 | 1.000000000 | -0.000004165 | -0.000001459 | 0.997304582 | 1.000000000 | 0.000001588 |
| if_e101win_strict_amp038 | submission_e108_if_e101win_strict_amp038_64514c53.csv | strict_e101_pass_conservative | 0.380000000 | True | 50 | -0.000006864 | -0.000005293 | 1.000000000 | 54.000000000 | -0.000002316 | -0.000000954 | 1.000000000 | 49.000000000 | 0.000000680 |

## Outcome Decision Table

| public_outcome | e107_outcome_refs | e101_delta_vs_e95_range | world_status | recommended_action | why | selection_modes | scenario_counts | any_model_tension |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E101 improves by roughly E95 edge or small-win scale | e95_edge_win,small_win_5e_minus6 | [-0.000020, -0.000002] | coherent | Submit E108 risk amp050 if upside is prioritized; submit strict amp038 if conservative. | E107 matched many broad-plausible worlds and ranked active_all amp050 first versus both E95 and E101. | within_tolerance | e95_edge_win:841,small_win_5e_minus6:742 | False |
| E101 is effectively tied with E95 | tie | near 0 | weak direction evidence | Do not submit amplitude-up automatically; treat E108 files as conditional probes only. | Amplitude rows still rank high in E107, but p95 becomes positive and the public sign evidence is weak. | within_tolerance | tie:305 | False |
| E101 loses to E95 | small_loss_1e_minus5,large_loss_4e_minus5 | > 0 | model tension | Do not rescue with E104/E106 masks; rebuild the public-world model around the failed rollback. | E107 needed nearest/tension worlds for loss cases, so the hidden-tail model would be falsified rather than refined. | nearest | small_loss_1e_minus5:240,large_loss_4e_minus5:240 | True |
| E101 wins much more than expected | strong_win_5e_minus5 | < -0.000020 | possible model tension | Inspect first; amp050 is likely directionally right, but the win magnitude exceeds the current world support. | The strong-win hypothetical was top-ranked for amp050 but required nearest scenario selection. | nearest | strong_win_5e_minus5:240 | True |

## E107 Conditioned Behavior

| role | outcome | mean_vs_e95 | p95_vs_e95 | beat_e95_rate | mean_vs_e101 | p95_vs_e101 | beat_e101_rate | rank_vs_e101 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| if_e101win_risk_amp050 | strong_win_5e_minus5 | -0.000071860 | -0.000065345 | 1.000000000 | -0.000033448 | -0.000030270 | 1.000000000 | 1.000000000 |
| if_e101win_risk_amp050 | e95_edge_win | -0.000027498 | -0.000021294 | 1.000000000 | -0.000012556 | -0.000009546 | 1.000000000 | 1.000000000 |
| if_e101win_risk_amp050 | small_win_5e_minus6 | -0.000009398 | -0.000004101 | 1.000000000 | -0.000004165 | -0.000001459 | 0.997304582 | 1.000000000 |
| if_e101win_risk_amp050 | tie | -0.000001703 | 0.000001947 | 0.750819672 | -0.000000485 | 0.000001588 | 0.685245902 | 1.000000000 |
| if_e101win_risk_amp050 | small_loss_1e_minus5 | -0.000000937 | 0.000002321 | 0.683333333 | -0.000000116 | 0.000001849 | 0.608333333 | 37.000000000 |
| if_e101win_risk_amp050 | large_loss_4e_minus5 | -0.000000937 | 0.000002321 | 0.683333333 | -0.000000116 | 0.000001849 | 0.608333333 | 37.000000000 |
| if_e101win_strict_amp038 | strong_win_5e_minus5 | -0.000056501 | -0.000051513 | 1.000000000 | -0.000018089 | -0.000016405 | 1.000000000 | 55.000000000 |
| if_e101win_strict_amp038 | e95_edge_win | -0.000021806 | -0.000016919 | 1.000000000 | -0.000006864 | -0.000005293 | 1.000000000 | 54.000000000 |
| if_e101win_strict_amp038 | small_win_5e_minus6 | -0.000007548 | -0.000003463 | 1.000000000 | -0.000002316 | -0.000000954 | 1.000000000 | 49.000000000 |
| if_e101win_strict_amp038 | tie | -0.000001573 | 0.000001201 | 0.783606557 | -0.000000355 | 0.000000680 | 0.734426230 | 25.000000000 |
| if_e101win_strict_amp038 | small_loss_1e_minus5 | -0.000000980 | 0.000001301 | 0.725000000 | -0.000000160 | 0.000000745 | 0.662500000 | 7.000000000 |
| if_e101win_strict_amp038 | large_loss_4e_minus5 | -0.000000980 | 0.000001301 | 0.725000000 | -0.000000160 | 0.000000745 | 0.662500000 | 7.000000000 |

## Interpretation

- Current next public sensor is still E101, not E108.
- If E101 wins by edge/small-win scale, `if_e101win_risk_amp050` is the
  highest-upside branch: it ranks first in E107 for both edge and small-win
  outcomes, but it is not E101-pass unconditionally.
- If E101 wins but the next submission should preserve strict local stress,
  `if_e101win_strict_amp038` is the conservative branch: it is E101-pass, but
  ranks around the middle of the conditional E104 amplitude family.
- If E101 ties or loses, these files should not be used as a rescue. That would
  mean the E99/E101 public-world model needs revision before another submission.
