# Q2 — S4 BSSID tokens: context-event vs availability proxy

For each top S4-debiased token, add it to a logistic with **subject dummies + all coverage features** already partialled out, then check whether its coefficient and the model logloss/AUC improve.


Baseline (subject + coverage only): LL=0.5772  AUC=0.7582


Tokens evaluated: **25** of 25 candidates (others not found or constant).


- mean raw lift (P(S4|tok)-P(S4|no tok)): +0.1772
- mean delta LL after adding token over base: -0.0039
- mean delta AUC: +0.0045
- tokens surviving |beta|>0.2 AND delta_LL<-0.001: **5** / 25
- tokens with any partial effect (|beta|>0.05 AND delta_LL<0): **11** / 25


## 1. Top-15 tokens by |beta_token_after_controls|

|  | token | n_present | raw_lift | beta_token_after_controls | delta_ll | delta_auc | survives_strong |
|---|---|---|---|---|---|---|---|
| 0 | usage_app_name:카카오 T | 50.0000 | 0.1575 | 0.3964 | -0.0078 | 0.0062 | 1.0000 |
| 1 | wifi_bssid:b4:a9:4f:3f:32:5b | 60.0000 | 0.2769 | 0.3639 | -0.0069 | 0.0123 | 1.0000 |
| 2 | wifi_bssid:60:29:d5:4a:47:d3 | 63.0000 | 0.3086 | 0.3318 | -0.0071 | 0.0078 | 1.0000 |
| 3 | usage_app_name:Google Play 서비스 | 79.0000 | -0.1419 | -0.2731 | -0.0014 | -0.0001 | 1.0000 |
| 4 | usage_app_name:LG ThinQ | 61.0000 | -0.2306 | -0.2537 | -0.0166 | 0.0122 | 1.0000 |
| 5 | wifi_bssid:94:53:30:29:33:cc | 56.0000 | 0.2578 | 0.1698 | -0.0031 | 0.0012 | 0.0000 |
| 6 | wifi_bssid:70:5d:cc:11:99:ac | 74.0000 | 0.2517 | 0.1318 | -0.0069 | 0.0103 | 0.0000 |
| 7 | wifi_bssid:80:ca:4b:59:3b:52 | 67.0000 | 0.2890 | 0.1227 | -0.0019 | 0.0037 | 0.0000 |
| 8 | wifi_bssid:50:46:ae:5f:2e:14 | 61.0000 | 0.2814 | 0.1131 | 0.0012 | 0.0013 | 0.0000 |
| 9 | wifi_bssid:00:07:89:28:de:d9 | 53.0000 | 0.2635 | 0.1111 | 0.0030 | -0.0033 | 0.0000 |
| 10 | usage_app_name:시계 | 331.0000 | -0.1526 | -0.1044 | -0.0002 | 0.0015 | 0.0000 |
| 11 | wifi_bssid:08:5d:dd:8b:94:91 | 83.0000 | 0.2293 | 0.0700 | -0.0026 | 0.0012 | 0.0000 |
| 12 | wifi_bssid:9e:7b:ef:5a:2f:35 | 86.0000 | 0.2421 | 0.0531 | -0.0071 | 0.0097 | 0.0000 |
| 13 | wifi_bssid:ee:5c:68:90:0c:eb | 51.0000 | 0.2751 | 0.0479 | -0.0006 | 0.0022 | 0.0000 |
| 14 | wifi_bssid:9e:25:4a:80:73:13 | 85.0000 | 0.2524 | 0.0341 | -0.0031 | 0.0052 | 0.0000 |


## 2. Interpretation

**Mixed.** Some tokens are true context events; many were sensor-availability proxies. Use a curated subset, not raw token feature dump.


Decision rules:
- Cap any S4 token-based correction to use only `survives_strong` tokens.
- If `n_strong == 0`, do not build an S4 BSSID specialist.
- If 1-3 tokens survive strongly, use them as event indicators with cap ±0.10.
- The baseline (subject + coverage only) LL is itself an interesting anchor; compare to subject_prior_a20 to see if coverage controls already buy lift.
