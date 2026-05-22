# PSG Q-State S2 Fixed Map Scout

Fixed target-map diagnostic using the current specialist map as the baseline and replacing only S2/S4 with Q-state split probes. This is not source selection; it tests whether the smaller S2 opportunity signal can improve the previous PSG replacement under the same fixed-map accounting.

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | replacements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| opp_s2_old_s4 | 0.609336 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562387 | 0.513590 | 0.631342 | {"S2": "psg_opp__deviation__c0.3_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| opp_mob_s2_old_s4 | 0.609370 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562629 | 0.513590 | 0.631342 | {"S2": "psg_opp_mob__deviation__c0.1_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| qrel_s2_old_s4 | 0.609407 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562888 | 0.513590 | 0.631342 | {"S2": "best_plus_psg_qrel__absolute__c0.1_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| old_psg_s2_s4 | 0.609682 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.564809 | 0.513590 | 0.631342 | {"S2": "psg_q__deviation__c0.1_b0.2", "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2"} |
| opp_s2_qcore_s4 | 0.609986 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562387 | 0.513590 | 0.635896 | {"S2": "psg_opp__deviation__c0.3_b0.2", "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2"} |
| opp_mob_s2_qcore_s4 | 0.610021 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562629 | 0.513590 | 0.635896 | {"S2": "psg_opp_mob__deviation__c0.1_b0.2", "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2"} |
| qrel_s2_best_plus_qcore_s4 | 0.610027 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562888 | 0.513590 | 0.635679 | {"S2": "best_plus_psg_qrel__absolute__c0.1_b0.2", "S4": "best_plus_psg_qcore__absolute_plus_deviation__c0.3_b0.2"} |
| qrel_s2_qcore_s4 | 0.610058 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.562888 | 0.513590 | 0.635896 | {"S2": "best_plus_psg_qrel__absolute__c0.1_b0.2", "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2"} |
| current | 0.610244 | 0.653762 | 0.682062 | 0.665036 | 0.557172 | 0.567195 | 0.513590 | 0.632894 | {} |

## Read

- `opp_s2_*` tests the smaller opportunity-only S2 hypothesis that beat the broad Q-state S2 probe in direct fold means.
- `qcore_s4` tests whether the compact Q-block can replace the earlier PSG core S4 scout.
- If a split variant improves both the fixed map and nested diagnostics, carry it forward; otherwise treat it as OOF selection noise.
