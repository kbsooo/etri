# E136 Target-Compression Visibility Audit

## Question

E133/E134/E135 tested the same cell-level safe-remainder teacher and found weak visibility. This audit asks whether the target representation itself is too sparse: if we compress the teacher into row, block-target, block-family, or block-total states, does hidden-block-heldout visibility become materially stronger?

Primary teacher remains `all_sign_co_vetonull_density`, aggregated by unit. Contexts tested: metadata, raw block views, old-prediction geometry, and raw+prediction combinations.

## Decision Result

- Best compressed unit: `block_target` with `all_raw_views_raw_pred` / `ridge`.
- Best top10 truth-mass capture: `0.332698`; enrichment over random top10: `3.326980`; capture ratio vs oracle top10: `0.709652`.
- Best block-target top10 enrichment: `3.326980` from `all_raw_views_raw_pred` / `ridge`.
- Best row-total top10 enrichment: `1.181643` from `metadata` / `knn8`.
- Cell-level references: E134 raw/block top50 enrichment `2.572395`, E135 prediction-manifold top50 enrichment `2.220050`.

## Top Overall Predictors

| unit_type | feature_set | model | n_units | n_features | top10_truth_mass | top10_enrichment | top10_capture_ratio | top20_truth_mass | top20_enrichment | cosine | spearman | top10_profile |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block_target | all_raw_views_raw_pred | ridge | 252.000000 | 1030.000000 | 0.332698 | 3.326980 | 0.709652 | 0.492425 | 2.462123 | 0.699725 | 0.647359 | Q1:9,Q3:10,S2:1,S3:2,S4:4 |
| block_family | metadata | knn8 | 108.000000 | 24.000000 | 0.327131 | 3.271312 | 0.881042 | 0.455378 | 2.276888 | 0.857967 | 0.799080 | Q1Q3:10,other:1 |
| block_target | night_all_raw | ridge | 252.000000 | 152.000000 | 0.323609 | 3.236095 | 0.690266 | 0.466161 | 2.330803 | 0.696915 | 0.618694 | Q1:9,Q3:10,S2:1,S3:3,S4:3 |
| block_target | metadata | ridge | 252.000000 | 28.000000 | 0.322721 | 3.227215 | 0.688372 | 0.494831 | 2.474154 | 0.727034 | 0.668004 | Q1:6,Q2:1,Q3:10,S2:3,S3:3,S4:3 |
| block_target | all_raw_views_raw | ridge | 252.000000 | 964.000000 | 0.322666 | 3.226656 | 0.688253 | 0.491766 | 2.458830 | 0.701437 | 0.653626 | Q1:9,Q3:10,S2:1,S3:3,S4:3 |
| block_family | prediction_geometry | knn8 | 108.000000 | 90.000000 | 0.306632 | 3.066319 | 0.825833 | 0.481746 | 2.408732 | 0.826863 | 0.670515 | Q1Q3:7,other:3,Q2S3:1 |
| block_family | all_raw_views_raw_pred | ridge | 108.000000 | 1026.000000 | 0.306460 | 3.064597 | 0.825369 | 0.463609 | 2.318043 | 0.789950 | 0.730325 | Q1Q3:9,other:2 |
| block_target | night_all_raw_pred | ridge | 252.000000 | 218.000000 | 0.304145 | 3.041451 | 0.648748 | 0.440931 | 2.204653 | 0.688439 | 0.600818 | Q1:8,Q3:10,S2:2,S3:3,S4:3 |
| block_family | all_raw_views_raw | ridge | 108.000000 | 960.000000 | 0.292183 | 2.921827 | 0.786917 | 0.450272 | 2.251360 | 0.792229 | 0.729629 | Q1Q3:9,other:2 |
| block_family | night_mobility_raw_pred | knn8 | 108.000000 | 214.000000 | 0.286431 | 2.864308 | 0.771426 | 0.423732 | 2.118658 | 0.779134 | 0.647232 | Q1Q3:6,other:3,Q2S3:2 |
| block_target | night_mobility_raw | ridge | 252.000000 | 152.000000 | 0.284294 | 2.842944 | 0.606407 | 0.458987 | 2.294936 | 0.686847 | 0.562581 | Q1:8,Q2:1,Q3:9,S1:1,S2:2,S3:2,S4:3 |
| block_target | prediction_geometry | ridge | 252.000000 | 94.000000 | 0.280694 | 2.806938 | 0.598726 | 0.470880 | 2.354401 | 0.695164 | 0.564644 | Q1:7,Q3:12,S2:1,S3:2,S4:4 |
| block_target | night_mobility_raw_pred | ridge | 252.000000 | 218.000000 | 0.279966 | 2.799660 | 0.597174 | 0.452656 | 2.263280 | 0.686625 | 0.570804 | Q1:8,Q3:9,S2:2,S3:3,S4:4 |
| block_family | night_mobility_raw_pred | ridge | 108.000000 | 214.000000 | 0.260376 | 2.603756 | 0.701253 | 0.388962 | 1.944808 | 0.773572 | 0.643174 | Q1Q3:8,other:2,Q2S3:1 |
| block_family | night_all_raw | ridge | 108.000000 | 148.000000 | 0.258032 | 2.580321 | 0.694942 | 0.448210 | 2.241048 | 0.787440 | 0.693732 | Q1Q3:7,other:3,Q2S3:1 |
| block_total | night_mobility_raw_pred | knn8 | 36.000000 | 211.000000 | 0.257094 | 2.570938 | 0.839465 | 0.472493 | 2.362467 | 0.910442 | 0.780438 | id01:2,id07:2 |

## Best By Unit Type

| unit_type | feature_set | model | n_units | top10_truth_mass | top10_enrichment | top10_capture_ratio | top20_truth_mass | top20_enrichment | top10_profile |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block_family | metadata | knn8 | 108.000000 | 0.327131 | 3.271312 | 0.881042 | 0.455378 | 2.276888 | Q1Q3:10,other:1 |
| block_family | prediction_geometry | knn8 | 108.000000 | 0.306632 | 3.066319 | 0.825833 | 0.481746 | 2.408732 | Q1Q3:7,other:3,Q2S3:1 |
| block_family | all_raw_views_raw_pred | ridge | 108.000000 | 0.306460 | 3.064597 | 0.825369 | 0.463609 | 2.318043 | Q1Q3:9,other:2 |
| block_family | all_raw_views_raw | ridge | 108.000000 | 0.292183 | 2.921827 | 0.786917 | 0.450272 | 2.251360 | Q1Q3:9,other:2 |
| block_family | night_mobility_raw_pred | knn8 | 108.000000 | 0.286431 | 2.864308 | 0.771426 | 0.423732 | 2.118658 | Q1Q3:6,other:3,Q2S3:2 |
| block_target | all_raw_views_raw_pred | ridge | 252.000000 | 0.332698 | 3.326980 | 0.709652 | 0.492425 | 2.462123 | Q1:9,Q3:10,S2:1,S3:2,S4:4 |
| block_target | night_all_raw | ridge | 252.000000 | 0.323609 | 3.236095 | 0.690266 | 0.466161 | 2.330803 | Q1:9,Q3:10,S2:1,S3:3,S4:3 |
| block_target | metadata | ridge | 252.000000 | 0.322721 | 3.227215 | 0.688372 | 0.494831 | 2.474154 | Q1:6,Q2:1,Q3:10,S2:3,S3:3,S4:3 |
| block_target | all_raw_views_raw | ridge | 252.000000 | 0.322666 | 3.226656 | 0.688253 | 0.491766 | 2.458830 | Q1:9,Q3:10,S2:1,S3:3,S4:3 |
| block_target | night_all_raw_pred | ridge | 252.000000 | 0.304145 | 3.041451 | 0.648748 | 0.440931 | 2.204653 | Q1:8,Q3:10,S2:2,S3:3,S4:3 |
| block_total | night_mobility_raw_pred | knn8 | 36.000000 | 0.257094 | 2.570938 | 0.839465 | 0.472493 | 2.362467 | id01:2,id07:2 |
| block_total | night_all_raw_pred | knn8 | 36.000000 | 0.251709 | 2.517088 | 0.821881 | 0.410951 | 2.054755 | id07:2,id01:1,id02:1 |
| block_total | metadata | ridge | 36.000000 | 0.231636 | 2.316362 | 0.756340 | 0.404776 | 2.023881 | id07:2,id03:1,id09:1 |
| block_total | night_mobility_raw | ridge | 36.000000 | 0.230617 | 2.306172 | 0.753013 | 0.424682 | 2.123410 | id01:1,id03:1,id07:1,id09:1 |
| block_total | night_all_raw | ridge | 36.000000 | 0.223656 | 2.236563 | 0.730284 | 0.388481 | 1.942403 | id07:2,id03:1,id10:1 |
| row_total | metadata | knn8 | 250.000000 | 0.118164 | 1.181643 | 0.433415 | 0.242042 | 1.210208 | id09:9,id03:6,id07:4,id05:3,id04:2,id08:1 |
| row_total | night_all_raw | ridge | 250.000000 | 0.110022 | 1.100220 | 0.403550 | 0.210050 | 1.050249 | id03:11,id05:6,id07:3,id08:2,id10:2,id04:1 |
| row_total | prediction_geometry | knn8 | 250.000000 | 0.109933 | 1.099331 | 0.403224 | 0.215985 | 1.079925 | id09:8,id05:6,id03:5,id07:4,id04:1,id10:1 |
| row_total | metadata | ridge | 250.000000 | 0.108523 | 1.085227 | 0.398051 | 0.204224 | 1.021120 | id03:11,id05:9,id07:5 |
| row_total | night_mobility_raw | ridge | 250.000000 | 0.107895 | 1.078945 | 0.395747 | 0.196759 | 0.983797 | id07:13,id03:11,id10:1 |

## Interpretation

Target compression materially improves hidden-block-heldout visibility. This keeps a JEPA-style target redesign branch alive: the visible context may not identify individual safe cells, but it can identify a coarser hidden state where the safe mass lives. The next experiment should test whether movement can be generated from the best compressed state without translating it back through the weak E133 cell ranking.

## Outputs

- Summary: `e136_target_compression_visibility_summary.csv`
- Predictions: `e136_target_compression_visibility_predictions.csv`
