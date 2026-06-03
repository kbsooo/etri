# H153 Gemini Embedding 2 Human-State Narrative HS-JEPA

Date: 2026-06-03

## Question

Can Gemini Embedding 2 turn row narratives into a useful human-state latent for
the HS-JEPA listener/toxicity solver?

The row is not embedded as raw numbers.  It is first translated into a compact
human-readable narrative:

```text
subject/date/calendar state/base target profile/source action disagreement
-> latent human-state route/listener/action-health/anti-shortcut tendency
```

## Embedding Source

```json
{
  "embedding_source": "gemini-embedding-2",
  "output_dim": 768,
  "n_rows": 250,
  "combined_narrative_hash": "d59f4bd28a48351053343506a5b7e89ebc7e1d72",
  "api_key_stored": false
}
```

## Listener Model Comparison

| model_set | variant | n_features | alpha | loo_mae | loo_rmse | loo_spearman | h144_h145_pred_gap_abs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base_listener | all_full | 317 | 1.000000000 | 0.000450715 | 0.000851793 | 0.858471532 | 0.000000922 |
| base_listener | no_pre_h | 317 | 30.000000000 | 0.000716345 | 0.001039922 | 0.605063381 | 0.000000278 |
| base_listener | no_bad | 317 | 0.300000000 | 0.000288111 | 0.000693633 | 0.869411051 | 0.000000915 |
| base_listener | frontier_only | 317 | 0.003000000 | 0.000193230 | 0.000335866 | -0.735612358 | 0.000000002 |
| base_listener | no_human_social | 244 | 0.300000000 | 0.000438975 | 0.000855949 | 0.825413664 | 0.000001117 |
| base_listener | no_subject | 227 | 1.000000000 | 0.000430681 | 0.000820494 | 0.860537649 | 0.000000910 |
| base_listener | no_row_order | 222 | 100.000000000 | 0.000473523 | 0.000781974 | 0.765496276 | 0.000000239 |
| base_listener | no_base_prob | 268 | 1.000000000 | 0.000436497 | 0.000812064 | 0.804752496 | 0.000000931 |
| base_listener | structural_only | 244 | 0.300000000 | 0.000438975 | 0.000855949 | 0.825413664 | 0.000001117 |
| base_listener | human_social_only | 83 | 0.300000000 | 0.000414252 | 0.000763188 | 0.901859985 | 0.000000531 |
| gemini2_semantic_listener | all_full | 884 | 10.000000000 | 0.000469774 | 0.000858609 | 0.691116071 | 0.000000725 |
| gemini2_semantic_listener | no_pre_h | 884 | 0.030000000 | 0.000628486 | 0.001094031 | 0.563045091 | 0.000000619 |
| gemini2_semantic_listener | no_bad | 884 | 1.000000000 | 0.000255699 | 0.000636966 | 0.840788465 | 0.000000742 |
| gemini2_semantic_listener | frontier_only | 884 | 0.003000000 | 0.000204605 | 0.000360431 | -0.529640898 | 0.000000159 |
| gemini2_semantic_listener | no_human_social | 811 | 10.000000000 | 0.000469905 | 0.000860876 | 0.696281363 | 0.000000720 |
| gemini2_semantic_listener | no_subject | 794 | 10.000000000 | 0.000472705 | 0.000860516 | 0.655992086 | 0.000000729 |
| gemini2_semantic_listener | no_row_order | 789 | 30.000000000 | 0.000488286 | 0.000847158 | 0.680785487 | 0.000000550 |
| gemini2_semantic_listener | no_base_prob | 835 | 10.000000000 | 0.000466256 | 0.000847939 | 0.697314422 | 0.000000732 |
| gemini2_semantic_listener | structural_only | 244 | 0.300000000 | 0.000438975 | 0.000855949 | 0.825413664 | 0.000001117 |
| gemini2_semantic_listener | human_social_only | 83 | 0.300000000 | 0.000414252 | 0.000763188 | 0.901859985 | 0.000000531 |

## Candidate Decision

| spec | description | local_path | hash | selected_cells | selected_rows | selected_target_mix | selected_source_mix | semantic_robust_mean_delta | semantic_robust_max_delta | semantic_positive_variants | base_robust_mean_delta | base_robust_max_delta | base_positive_variants | h088_move_cosine | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | decision_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| semantic_listener_balanced | Gemini semantic listener with loose base-listener support | /Users/kbsoo/Downloads/cl2/hitl/h153_gemini2_human_state_embedding_hsjepa/submission_h153_semantic_listener_balanced_8ff9281e.csv | 8ff9281e | 340 | 58 | {'Q2': 78, 'S2': 66, 'S4': 55, 'Q3': 46, 'S3': 35, 'Q1': 34, 'S1': 26} | {'submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv': 59, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 57, 'submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv': 55, 'submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv': 55, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 29, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 27, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 26, 'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 22, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 10} | -0.003871403 | -0.000669428 | 10 | -0.004371780 | -0.001116103 | 10 | 0.002272083 | /Users/kbsoo/Downloads/cl2/hitl/h153_gemini2_human_state_embedding_hsjepa/submission_h153_semantic_listener_balanced_8ff9281e.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 72 | True | 5.032100152 |
| semantic_listener_safe | Gemini semantic listener only where base listener also agrees | /Users/kbsoo/Downloads/cl2/hitl/h153_gemini2_human_state_embedding_hsjepa/submission_h153_semantic_listener_safe_111334f0.csv | 111334f0 | 260 | 41 | {'Q2': 62, 'S4': 42, 'S3': 36, 'Q1': 35, 'S2': 35, 'S1': 31, 'Q3': 19} | {'submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv': 45, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 45, 'submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv': 43, 'submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv': 40, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 24, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 21, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 17, 'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 15, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 10} | -0.002645403 | -0.000428891 | 10 | -0.003145990 | -0.000900464 | 10 | -0.001014048 | /Users/kbsoo/Downloads/cl2/hitl/h153_gemini2_human_state_embedding_hsjepa/submission_h153_semantic_listener_safe_111334f0.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 50 | True | 4.020778541 |

## Semantic Listener Candidate Scores

| spec | file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | robust_positive_variant_count | robust_mean_pred_delta | robust_max_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| semantic_listener_balanced | submission_h153_semantic_listener_balanced_8ff9281e.csv | 86 | 69 | 0.002272083 | 10 | -0.003871403 | -0.000669428 |
| semantic_listener_safe | submission_h153_semantic_listener_safe_111334f0.csv | 64 | 52 | -0.001014048 | 10 | -0.002645403 | -0.000428891 |
| reference | submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 363 | 159 | 0.214751899 | 10 | -0.002374244 | -0.000275078 |
| reference | submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 349 | 154 | 0.121063141 | 10 | -0.002276318 | -0.000121041 |
| reference | submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 364 | 157 | 0.188791860 | 10 | -0.001742269 | -0.000075622 |

## Top Cell Candidates

| source_file | row | target | subject_id | sleep_date | semantic_benefit | base_benefit | semantic_positive_variants | base_positive_variants | h088_alignment | score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000071589 | 0.000082966 | 10 | 10 | 0.000000000 | 15.185401105 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000074058 | 0.000085827 | 10 | 10 | 0.000000000 | 15.182868683 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000123430 | 0.000143045 | 10 | 10 | 0.000000000 | 15.182745578 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000116169 | 0.000134631 | 10 | 10 | 0.000000000 | 15.176551769 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000181514 | 0.000210360 | 10 | 10 | 0.000000000 | 15.175448025 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000175086 | 0.000202910 | 10 | 10 | 0.000000000 | 15.173692905 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 98 | Q2 | id04 | 2024-10-19 00:00:00 | 0.000181514 | 0.000210360 | 10 | 10 | 0.000000000 | 15.173162310 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000129772 | 0.000119769 | 10 | 10 | 0.000000000 | 15.164586766 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000085846 | 0.000079229 | 10 | 10 | 0.000000000 | 15.159351077 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000051182 | 0.000047237 | 10 | 10 | 0.000000000 | 15.155808413 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000134134 | 0.000123796 | 10 | 10 | 0.000000000 | 15.155072023 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000088245 | 0.000081443 | 10 | 10 | 0.000000000 | 15.154558207 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 91 | Q2 | id04 | 2024-09-25 00:00:00 | 0.000052947 | 0.000048866 | 10 | 10 | 0.000000000 | 15.137348529 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000059760 | 0.000067968 | 10 | 10 | 0.000000000 | 15.134917712 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000036827 | 0.000041885 | 10 | 10 | 0.000000000 | 15.133245934 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000063495 | 0.000072216 | 10 | 10 | 0.000000000 | 15.129889553 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000072931 | 0.000082948 | 10 | 10 | 0.000000000 | 15.128753902 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000093375 | 0.000106200 | 10 | 10 | 0.000000000 | 15.121807127 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000042051 | 0.000102797 | 10 | 10 | 0.000000000 | 15.120235309 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000016585 | 0.000040543 | 10 | 10 | 0.000000000 | 15.112324107 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 102 | Q2 | id04 | 2024-10-25 00:00:00 | 0.000020753 | 0.000024250 | 10 | 10 | 0.000000000 | 15.108783615 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 158 | Q2 | id07 | 2024-07-20 00:00:00 | 0.000038097 | 0.000043330 | 10 | 10 | 0.000000000 | 15.098795178 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 8 | Q2 | id01 | 2024-08-10 00:00:00 | 0.000011868 | 0.000020344 | 10 | 10 | 0.000000000 | 15.073343904 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000105083 | 0.000081332 | 10 | 9 | 0.000000000 | 15.065784072 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000060948 | 0.000047173 | 10 | 9 | 0.000000000 | 15.062726519 |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 182 | S2 | id08 | 2024-08-01 00:00:00 | 0.000013073 | 0.000013948 | 10 | 10 | 0.000000000 | 15.059701499 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000026913 | 0.000065790 | 10 | 10 | 0.000000000 | 15.052392377 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000042051 | 0.000102797 | 10 | 10 | 0.000000000 | 15.051663880 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000028595 | 0.000069902 | 10 | 10 | 0.000000000 | 15.045453764 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000063050 | 0.000048799 | 10 | 9 | 0.000000000 | 15.044133602 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 102 | Q2 | id04 | 2024-10-25 00:00:00 | 0.000035782 | 0.000041810 | 10 | 10 | 0.000000000 | 15.039562764 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 79 | Q1 | id03 | 2024-10-10 00:00:00 | 0.000000270 | 0.000000131 | 10 | 9 | 0.000000000 | 15.033319040 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000105083 | 0.000081332 | 10 | 9 | 0.000000000 | 15.031498357 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000105083 | 0.000081332 | 10 | 9 | 0.000000000 | 15.029212643 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000067253 | 0.000052053 | 10 | 9 | 0.000000000 | 15.025239089 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000071456 | 0.000055306 | 10 | 9 | 0.000000000 | 15.017780470 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 78 | Q2 | id03 | 2024-10-06 00:00:00 | 0.000093679 | 0.000072506 | 10 | 9 | 0.000000000 | 15.014715439 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 102 | Q2 | id04 | 2024-10-25 00:00:00 | 0.000021469 | 0.000025086 | 10 | 10 | 0.000000000 | 14.992068441 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 128 | Q1 | id06 | 2024-07-07 00:00:00 | 0.000017157 | 0.000041941 | 10 | 10 | 0.000000000 | 14.977438969 |
| submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 102 | Q2 | id04 | 2024-10-25 00:00:00 | 0.000022900 | 0.000026758 | 10 | 10 | 0.000000000 | 14.975782184 |

## Readout

```json
{
  "embedding_source": "gemini-embedding-2",
  "gemini_embedding_used": true,
  "n_semantic_features": 567,
  "best_spec": "semantic_listener_balanced",
  "best_root_path": "/Users/kbsoo/Downloads/cl2/submission_h153_gemini2_semantic_listener_balanced_8ff9281e_uploadsafe.csv",
  "best_upload_safe": true,
  "best_semantic_robust_mean_delta": -0.0038714032371447217,
  "best_base_robust_mean_delta": -0.004371779758602366,
  "best_h088_move_cosine": 0.002272083115244816
}
```

## Interpretation

If the Gemini semantic listener improves LOO metrics and selects a candidate
with H149-level benefit but lower H088 cosine, then language-model semantic
state is a real HS-JEPA context encoder.  If it only mirrors H149/H152 or
raises H088 alignment, then the narrative embedding is useful for hypothesis
organization but not yet a safe correction decoder.
