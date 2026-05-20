# v81 late-behavior retrieval decoder

- Base (v80) OOF: `0.477600`
- Source features used (8): joint_cross_family_late_residual_behavior_neural_metric_knn_resid, joint_family_late_residual_behavior_neural_metric_knn_logitresid, joint_late_residual_behavior_neural_knn_resid, joint_neural_multiview_q_residual_knn_resid, joint_panel_neural_residual_knn_resid, joint_residual_behavior_neural_knn_resid, joint_s23_late_residual_behavior_neural_knn_resid, joint_target_late_residual_behavior_neural_metric_knn_logitresid
- Decoder: target-wise residual on the v80 base. Regressors predict the residual; logreg is a label-classifier contrast.
- Fold-safe: retrieval summaries computed from fold-train only, self excluded by key; folds match the v80 encoder partition.

## Standalone source scores (vs v80 base)

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v80_base | 0.477600 | 0.520922 | 0.534345 | 0.497697 | 0.467526 | 0.449979 | 0.407026 | 0.465702 |
| v81_late_retrieval_hgb | 0.516253 | 0.538552 | 0.574879 | 0.540291 | 0.510756 | 0.509143 | 0.436210 | 0.503940 |

Note: standalone scores start from the base and apply the full (weight=1) residual. The router applies a fractional, target/bin-local weight, so the routed gain is what matters — see the conditional_latent_routing_v81 reports.
