# JEPA Experiments

This folder contains JEPA-style latent prediction experiments adapted to the sleep/lifelog tabular data.

## Feature Families

- Input feature count: `5707`
- JEPA-derived feature count: `1542`
- Image-like sensor/time grid cells: `147`
- Families: modality block prediction, time-block prediction, sensor-time cell prediction, prefix block prediction, image-grid row/column prediction, subject temporal-neighbor prediction.

## Best Single-Feature Residual Scans

| target | feature | mode | c_value | best_weight | delta_vs_base | mean_delta | win_rate | passes_strict | passes_loose |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | jepa_grid__prectx_other__pre3h__pred | subject_rank | 0.2 | 0.45 | -0.0106371162 | -0.0103164053 | 0.992307692 | True | True |
| Q3 | jepa_grid__prectx_hr__pre6h__pred | subject_rank | 0.2 | 0.45 | -0.00914381563 | -0.00906417153 | 1 | True | True |
| Q3 | jepa_grid__prectx_other__pre3h__pred | subject_rank | 0.05 | 0.45 | -0.00794387546 | -0.00752383839 | 0.984615385 | True | True |
| S4 | jepa_grid__prectx_mlight__pre3h__pred | subject_rank | 0.2 | 0.45 | -0.0074159077 | -0.00638917712 | 0.984615385 | True | True |
| Q3 | jepa_prefix__prectx__resid_pc0 | subject_z | 0.2 | 0.45 | -0.00735938327 | -0.00661045534 | 0.965384615 | True | True |
| Q3 | jepa_grid__prectx_hr__pre6h__pred | subject_z | 0.2 | 0.45 | -0.00731236476 | -0.00723706479 | 1 | True | True |
| S4 | jepa_grid__prectx_mlight__pre3h__pred | subject_center | 0.2 | 0.45 | -0.00698776144 | -0.00441646906 | 0.784615385 | True | True |
| Q3 | jepa_grid__prectx_hr__pre6h__pred | subject_rank | 0.05 | 0.45 | -0.00672907535 | -0.00659791353 | 1 | True | True |
| Q3 | jepa_prefix__prectx__resid_pc0 | subject_rank | 0.2 | 0.45 | -0.00671499983 | -0.00580233772 | 0.934615385 | True | True |
| Q3 | jepa_grid__prectx_other__pre3h__pred | subject_z | 0.2 | 0.45 | -0.00669624788 | -0.00566526553 | 0.923076923 | True | True |
| Q3 | jepa_grid__prectx_hr__pre6h__pred | subject_center | 0.2 | 0.45 | -0.00664479538 | -0.00625828297 | 0.969230769 | True | True |
| S4 | jepa_grid__prectx_mlight__pre3h__pred | subject_rank | 0.05 | 0.45 | -0.00606368065 | -0.00460619736 | 0.946153846 | True | True |
| S4 | jepa_grid__prectx_mlight__pre3h__pred | subject_z | 0.2 | 0.45 | -0.0059812488 | -0.00416285138 | 0.857692308 | True | True |
| S4 | jepa_grid__presleep_mlight__pre3h__value | subject_rank | 0.2 | 0.45 | -0.00578122402 | -0.0049238372 | 0.996153846 | True | True |
| Q3 | jepa_grid__prectx_wlight__pre6h__pred | subject_rank | 0.2 | 0.45 | -0.00564073804 | -0.00496375849 | 0.942307692 | True | True |

## Selected Combined Candidate

- Q3: `jepa_grid__prectx_other__pre3h__pred` / `subject_rank` / C=0.2 / w=0.45
- S4: `jepa_grid__prectx_mlight__pre3h__pred` / `subject_rank` / C=0.2 / w=0.45
- S2: `jepa_modality__presleep_mlight__pred_pc1` / `subject_rank` / C=0.2 / w=0.45
- Q1: `jepa_modality__ambience__resid_norm` / `subject_rank` / C=0.2 / w=0.45
- S1: `jepa_grid__presleep_activity__pre1h__resid` / `subject_z` / C=0.2 / w=0.45
- S3: `jepa_sensor_time__prectx_usage__pre3h__resid_abs_mean` / `subject_z` / C=0.2 / w=0.45

## CV Estimate

| target | base_loss | candidate_loss | delta_vs_base |
| --- | --- | --- | --- |
| Q1 | 0.574630824 | 0.569412153 | -0.00521867067 |
| Q2 | 0.642998693 | 0.642998693 | 0 |
| Q3 | 0.630348489 | 0.619711373 | -0.0106371162 |
| S1 | 0.478943276 | 0.475867397 | -0.00307587866 |
| S2 | 0.53895345 | 0.533990106 | -0.00496334372 |
| S3 | 0.503437679 | 0.499448089 | -0.00398959058 |
| S4 | 0.603404062 | 0.595988155 | -0.0074159077 |
| mean | 0.567530925 | 0.562487995 | -0.00504292964 |
