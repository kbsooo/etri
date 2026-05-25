# CL v83 residual ranker

Purpose: keep the v83 public coordinate fixed and inject only centered CL residual rank signals.

Formula:

`candidate_t = sigmoid(logit(v83_t) + gamma * rank_center(CL_residual_signal_t))`

The CL model is not used as direct probability. Each injected signal is target-wise mean-zero and rank-normalized.

## OOF stress over CL validation anchors

| candidate | delta_mean | delta_worst | move_mean |
| --- | --- | --- | --- |
| s1_rank_g100_stress | -0.009180 | -0.007302 | 0.016008 |
| s1_rank_g050 | -0.004822 | -0.003878 | 0.008034 |
| q1s1_rank_g050 | -0.004520 | -0.003676 | 0.009146 |
| sleep_family_rank_g050 | -0.003694 | -0.003432 | 0.009149 |
| s1_rank_g030 | -0.002949 | -0.002381 | 0.004827 |
| q1s1_rank_g030 | -0.002776 | -0.002268 | 0.005495 |
| q1_rank_g030 | -0.002602 | -0.002155 | 0.006162 |
| sleep_family_rank_g030 | -0.002280 | -0.002122 | 0.005497 |
| s1_rank_g010 | -0.001002 | -0.000812 | 0.001611 |
| q1s1_rank_g010 | -0.000946 | -0.000777 | 0.001834 |
| s1_rank_g005 | -0.000503 | -0.000408 | 0.000806 |
| q1s1_rank_g005 | -0.000476 | -0.000391 | 0.000917 |
| q1_rank_g005 | -0.000448 | -0.000374 | 0.001028 |
| sleep_family_rank_g005 | -0.000393 | -0.000367 | 0.000918 |

## Candidate files

| candidate | file | gamma | mean_abs_move_v83 | max_abs_move_v83 | dmean_Q1 | dmean_Q2 | dmean_Q3 | dmean_S1 | dmean_S2 | dmean_S3 | dmean_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s1_rank_g005 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g005_prob.csv | 0.005000 | 0.000119 | 0.002108 | 0.000000 | 0.000000 | 0.000000 | -0.000115 | 0.000000 | 0.000000 | 0.000000 |
| q1_rank_g005 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1_rank_g005_prob.csv | 0.005000 | 0.000141 | 0.002147 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| s1_rank_g010 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g010_prob.csv | 0.010000 | 0.000238 | 0.004218 | 0.000000 | 0.000000 | 0.000000 | -0.000231 | 0.000000 | 0.000000 | 0.000000 |
| q1s1_rank_g005 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1s1_rank_g005_prob.csv | 0.005000 | 0.000260 | 0.002147 | 0.000000 | 0.000000 | 0.000000 | -0.000115 | 0.000000 | 0.000000 | 0.000000 |
| sleep_family_rank_g005 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_sleep_family_rank_g005_prob.csv | 0.005000 | 0.000515 | 0.002147 | 0.000000 | 0.000000 | 0.000000 | -0.000115 | -0.000115 | 0.000000 | -0.000032 |
| q1s1_rank_g010 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1s1_rank_g010_prob.csv | 0.010000 | 0.000519 | 0.004295 | 0.000000 | 0.000000 | 0.000000 | -0.000231 | 0.000000 | 0.000000 | 0.000000 |
| s1_rank_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g030_prob.csv | 0.030000 | 0.000714 | 0.012669 | 0.000000 | 0.000000 | 0.000000 | -0.000706 | 0.000000 | 0.000000 | 0.000000 |
| q1_rank_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1_rank_g030_prob.csv | 0.030000 | 0.000842 | 0.012897 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| s1_rank_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g050_prob.csv | 0.050000 | 0.001188 | 0.021136 | 0.000000 | 0.000000 | 0.000000 | -0.001200 | 0.000000 | 0.000000 | 0.000000 |
| q1s1_rank_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1s1_rank_g030_prob.csv | 0.030000 | 0.001556 | 0.012897 | 0.000000 | 0.000000 | 0.000000 | -0.000706 | 0.000000 | 0.000000 | 0.000000 |
| s1_rank_g100_stress | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_s1_rank_g100_stress_prob.csv | 0.100000 | 0.002369 | 0.042344 | 0.000000 | 0.000000 | 0.000000 | -0.002510 | 0.000000 | 0.000000 | 0.000000 |
| q1s1_rank_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_q1s1_rank_g050_prob.csv | 0.050000 | 0.002590 | 0.021513 | -0.000001 | 0.000000 | 0.000000 | -0.001200 | 0.000000 | 0.000000 | 0.000000 |
| sleep_family_rank_g030 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_sleep_family_rank_g030_prob.csv | 0.030000 | 0.003086 | 0.012897 | 0.000000 | 0.000000 | 0.000000 | -0.000706 | -0.000701 | 0.000000 | -0.000203 |
| sleep_family_rank_g050 | /Users/kbsoo/Downloads/dacon/etri/cl/outputs/submission_cl_v83_residual_ranker_sleep_family_rank_g050_prob.csv | 0.050000 | 0.005137 | 0.021513 | -0.000001 | 0.000000 | 0.000000 | -0.001200 | -0.001184 | 0.000000 | -0.000349 |

## Public-posterior diagnostics

| posterior | candidate | posterior_bce | vs_v83 |
| --- | --- | --- | --- |
| old_public_anchor | q1_rank_g005 | 0.597813 | -0.000001 |
| old_public_anchor | v83_base | 0.597813 | 0.000000 |
| old_public_anchor | q1s1_rank_g005 | 0.597814 | 0.000001 |
| old_public_anchor | s1_rank_g005 | 0.597815 | 0.000002 |
| old_public_anchor | q1s1_rank_g010 | 0.597817 | 0.000003 |
| old_public_anchor | s1_rank_g010 | 0.597817 | 0.000004 |
| old_public_anchor | q1_rank_g030 | 0.597822 | 0.000008 |
| old_public_anchor | sleep_family_rank_g005 | 0.597825 | 0.000011 |
| old_public_anchor | s1_rank_g030 | 0.597833 | 0.000020 |
| old_public_anchor | q1s1_rank_g030 | 0.597842 | 0.000028 |
| old_public_anchor | s1_rank_g050 | 0.597861 | 0.000047 |
| old_public_anchor | q1s1_rank_g050 | 0.597891 | 0.000077 |
| old_public_anchor | sleep_family_rank_g030 | 0.597926 | 0.000112 |
| old_public_anchor | s1_rank_g100_stress | 0.597977 | 0.000163 |
| old_public_anchor | sleep_family_rank_g050 | 0.598060 | 0.000247 |
| refit_public_anchor | s1_rank_g100_stress | 0.599481 | -0.000283 |
| refit_public_anchor | s1_rank_g050 | 0.599589 | -0.000176 |
| refit_public_anchor | s1_rank_g030 | 0.599651 | -0.000114 |
| refit_public_anchor | q1s1_rank_g050 | 0.599673 | -0.000092 |
| refit_public_anchor | q1s1_rank_g030 | 0.599691 | -0.000073 |
| refit_public_anchor | s1_rank_g010 | 0.599724 | -0.000041 |
| refit_public_anchor | q1s1_rank_g010 | 0.599734 | -0.000030 |
| refit_public_anchor | s1_rank_g005 | 0.599744 | -0.000021 |
| refit_public_anchor | q1s1_rank_g005 | 0.599749 | -0.000016 |
| refit_public_anchor | sleep_family_rank_g005 | 0.599759 | -0.000006 |
| refit_public_anchor | v83_base | 0.599765 | 0.000000 |
| refit_public_anchor | q1_rank_g005 | 0.599769 | 0.000005 |
| refit_public_anchor | sleep_family_rank_g030 | 0.599776 | 0.000011 |
| refit_public_anchor | q1_rank_g030 | 0.599805 | 0.000041 |
| refit_public_anchor | sleep_family_rank_g050 | 0.599843 | 0.000079 |

Read: negative OOF delta means the residual rank helped over the CL validation anchor. Upload trust still depends on staying close to v83; these files are diagnostic candidates, not a 0.57 claim.
