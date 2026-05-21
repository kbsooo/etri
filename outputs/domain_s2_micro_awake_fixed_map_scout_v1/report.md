# S2 Micro Awake Fixed Map Scout

## Purpose

Diagnostic fixed target-map substitutions for compact S2 micro-awakening variants. Full-fold mean losses are selection-biased for candidate choice; use as direction finding only.

## Results

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | overrides |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current | 0.610244 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.632894 | {} |
| s2_rolling_micro | 0.610975 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.572312 | 0.513590 | 0.632894 | {"S2": "best_plus_s2ma_rolling_sleep_micro__absolute_plus_deviation__c0.1_b0.2"} |
| s4_micro_runs | 0.611170 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.639373 | {"S4": "best_plus_s2ma_sleep_micro_runs__absolute_plus_deviation__c0.3_b0.2"} |
| s1_sleep_micro_core_dev | 0.611415 | 0.653762 | 0.682062 | 0.665036 | 0.565366 | 0.567195 | 0.513590 | 0.632894 | {"S1": "best_plus_s2ma_sleep_micro_core__deviation__c0.3_b0.2"} |
| s3_subject_micro | 0.611444 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.521985 | 0.632894 | {"S3": "best_plus_s2ma_subject_relative_sleep_micro__absolute_plus_deviation__c0.3_b0.2"} |
| all_s_micro | 0.614271 | 0.653762 | 0.682062 | 0.665036 | 0.565366 | 0.572312 | 0.521985 | 0.639373 | {"S1": "best_plus_s2ma_sleep_micro_core__deviation__c0.3_b0.2", "S2": "best_plus_s2ma_rolling_sleep_micro__absolute_plus_deviation__c0.1_b0.2", "S3": "best_plus_s2ma_subject_relative_sleep_micro__absolute_plus_deviation__c0.3_b0.2", "S4": "best_plus_s2ma_sleep_micro_runs__absolute_plus_deviation__c0.3_b0.2"} |