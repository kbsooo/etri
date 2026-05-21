# Routine Pruned Fixed Map Scout

## Purpose

Compare the current protected target map with S4-only substitutions from pruned routine variants using full-fold mean losses. This is diagnostic and still selection-biased for S4 variants.

## S4 Substitution Results

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | S4_source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rr_coverage_best_plus | 0.610244 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.632894 | best_plus_rr_coverage_rhythm__absolute_plus_deviation__c0.3_b0.2 |
| current_scp_s4 | 0.610301 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.633287 | scp_subject_relative_only__absolute__c0.1_b0.2 |
| rr_sleep_break_best_plus | 0.610305 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.633316 | best_plus_rr_sleep_regular_break__absolute_plus_deviation__c0.3_b0.2 |
| rr_coverage_raw | 0.610472 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.634487 | rr_coverage_rhythm__absolute_plus_deviation__c0.3_b0.2 |
| rr_profile_best_plus | 0.610512 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.634764 | best_plus_rr_profile_distance__absolute_plus_deviation__c0.3_b0.2 |