# Master aggressive decoder report

- Train rows: 450
- Test rows: 250
- Best global CV: 0.622993 (`blend_w0.3_logreg_finding_core_C0.03_a10`)
- Target-wise CV: 0.616072

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_logreg_finding_core_C0.03_a10 | blend | 0.622993 | 0.665509 | 0.704495 | 0.667975 | 0.569722 | 0.575775 | 0.541995 | 0.635478 |
| blend_w0.1_logreg_finding_core_C0.1_a10 | blend | 0.623735 | 0.667998 | 0.701513 | 0.670407 | 0.571139 | 0.576847 | 0.536087 | 0.642157 |
| blend_w0.1_logreg_finding_core_C0.03_a10 | blend | 0.624181 | 0.668312 | 0.701522 | 0.671626 | 0.572066 | 0.577251 | 0.536929 | 0.641564 |
| blend_w0.3_lgbm1_finding_core_a2 | blend | 0.624849 | 0.663500 | 0.704893 | 0.672240 | 0.570644 | 0.580392 | 0.538851 | 0.643424 |
| blend_w0.3_lgbm2_finding_core_a2 | blend | 0.624891 | 0.665458 | 0.704205 | 0.672707 | 0.570065 | 0.579840 | 0.538514 | 0.643451 |
| blend_w0.3_logreg_finding_core_C0.1_a10 | blend | 0.624895 | 0.668019 | 0.708228 | 0.667577 | 0.570532 | 0.577729 | 0.541893 | 0.640286 |
| blend_w0.3_logreg_finding_core_C0.03_a2 | blend | 0.625098 | 0.668291 | 0.711003 | 0.672278 | 0.569545 | 0.577784 | 0.540039 | 0.636745 |
| blend_w0.1_logreg_latent_master_rankdev_C0.03_a10 | blend | 0.625348 | 0.664345 | 0.703488 | 0.676114 | 0.573127 | 0.577860 | 0.538849 | 0.643653 |
| blend_w0.1_logreg_master_rankdev_C0.03_a10 | blend | 0.625348 | 0.664345 | 0.703488 | 0.676114 | 0.573127 | 0.577860 | 0.538849 | 0.643653 |
| blend_w0.5_lgbm1_finding_core_a2 | blend | 0.625555 | 0.658786 | 0.702415 | 0.667350 | 0.571520 | 0.585412 | 0.548949 | 0.644455 |
| blend_w0.5_lgbm2_finding_core_a2 | blend | 0.625567 | 0.662086 | 0.701277 | 0.668106 | 0.570538 | 0.584458 | 0.548223 | 0.644283 |
| blend_w0.3_lgbm2_finding_core_a10 | blend | 0.626025 | 0.665312 | 0.699346 | 0.669343 | 0.572824 | 0.583587 | 0.545858 | 0.645905 |

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | rankcal_b0.3_lgbm2_latent_master_rankdev_a10 | rankcal | 0.628599 | 0.652042 | 0.705104 | 0.683755 | 0.566099 | 0.588022 | 0.551326 | 0.653843 |
| Q2 | rankcal_b0.3_lgbm2_finding_core_a50 | rankcal | 0.635522 | 0.662564 | 0.691118 | 0.671463 | 0.578526 | 0.605838 | 0.581367 | 0.657778 |
| Q3 | blend_w0.3_logreg_finding_core_C0.1_a50 | blend | 0.627858 | 0.667778 | 0.699524 | 0.661865 | 0.577126 | 0.585684 | 0.559010 | 0.644017 |
| S1 | rankcal_b0.3_lgbm1_latent_master_rankdev_a10 | rankcal | 0.629000 | 0.653549 | 0.706455 | 0.680759 | 0.562864 | 0.586168 | 0.555274 | 0.657931 |
| S2 | blend_w0.3_logreg_finding_core_C0.03_a10 | blend | 0.622993 | 0.665509 | 0.704495 | 0.667975 | 0.569722 | 0.575775 | 0.541995 | 0.635478 |
| S3 | blend_w0.1_lgbm2_finding_core_a2 | blend | 0.627799 | 0.672208 | 0.709738 | 0.679211 | 0.573693 | 0.580258 | 0.533363 | 0.646119 |
| S4 | blend_w0.3_logreg_finding_core_C0.03_a10 | blend | 0.622993 | 0.665509 | 0.704495 | 0.667975 | 0.569722 | 0.575775 | 0.541995 | 0.635478 |

## Feature set sizes

- finding_core: 253
- master_raw: 610
- master_rankdev: 1060
- no_subject_rankdev: 1050
- all_numeric: 1060
- no_subject_all: 1050
- latent: 83
- latent_master_rankdev: 1060
