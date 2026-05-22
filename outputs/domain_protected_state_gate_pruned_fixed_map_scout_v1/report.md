# Protected State Gate Pruned Fixed Map Scout

Diagnostic fixed target-map substitutions for pruned protected-state gate variants.

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | replacements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| psg_s2_s4 | 0.609682 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.564809 | 0.513590 | 0.631342 | {"S2": "psg_q__deviation__c0.1_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| psg_s2_only | 0.609903 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.564809 | 0.513590 | 0.632894 | {"S2": "psg_q__deviation__c0.1_b0.2"} |
| psg_s4_only | 0.610023 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.631342 | {"S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| psg_sleep_s2 | 0.610223 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567043 | 0.513590 | 0.632894 | {"S2": "best_plus_psg_sleep__absolute_plus_deviation__c0.1_b0.2"} |
| current | 0.610244 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.632894 | {} |
| psg_proto_q2_s4 | 0.611241 | 0.653762 | 0.690588 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.631342 | {"Q2": "best_plus_psg_proto__deviation__c0.01_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |