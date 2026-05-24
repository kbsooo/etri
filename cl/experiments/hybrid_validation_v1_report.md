# Hybrid validation v1 — results report

Three fold families (chrono_tail / hole_v1 / mirror_v1) scored on the
same model zoo. Mirror family weights are sized to mimic the actual
test inside/after composition (156/94 = 62%/38%) per subject.


## 1. Mean logloss by model × family (avg over folds in family)

**Mean over folds:**

| model | chrono_tail | hole_v1 | mirror_v1 |
|---|---|---|---|
| global_mean | 0.6693 | 0.6707 | 0.6697 |
| neighbor_label_avg_k3 | 0.9697 | 0.8118 | 0.9245 |
| subject_prior_a20 | 0.6380 | 0.6259 | 0.6423 |
| tiny_logistic_topk20 | 0.6584 | 0.6314 | 0.6711 |


**Std over folds:**

| model | chrono_tail | hole_v1 | mirror_v1 |
|---|---|---|---|
| global_mean | 0.0028 | 0.0066 | 0.0025 |
| neighbor_label_avg_k3 | 0.0825 | 0.0495 | 0.0303 |
| subject_prior_a20 | 0.0031 | 0.0118 | 0.0100 |
| tiny_logistic_topk20 | 0.0102 | 0.0172 | 0.0202 |


## 2. Regime gap: tail minus hole (positive = tail harder)

| model | tail_minus_hole | mirror |
|---|---|---|
| global_mean | -0.0014 | 0.6697 |
| neighbor_label_avg_k3 | 0.1579 | 0.9245 |
| subject_prior_a20 | 0.0121 | 0.6423 |
| tiny_logistic_topk20 | 0.0270 | 0.6711 |


Interpretation: a *large positive* gap means the model leans on hole-only advantage (neighbor labels). The neighbor_label_avg_k3 row is the canary: if its gap is large, the two regimes are genuinely different and chrono_tail CV alone is systematically too pessimistic *for hole-friendly models* (and too optimistic for hole-fragile models).


## 3. Per-target mean logloss (averaged over folds, by family)


### chrono_tail

| model | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mean |
|---|---|---|---|---|---|---|---|---|
| global_mean | 0.7023 | 0.6758 | 0.6587 | 0.6045 | 0.6920 | 0.6602 | 0.6917 | 0.6693 |
| neighbor_label_avg_k3 | 1.1925 | 1.1195 | 1.1141 | 0.8538 | 0.8099 | 0.8270 | 0.8710 | 0.9697 |
| subject_prior_a20 | 0.6730 | 0.6761 | 0.6810 | 0.5545 | 0.6316 | 0.5946 | 0.6550 | 0.6380 |
| tiny_logistic_topk20 | 0.6934 | 0.6821 | 0.7578 | 0.5544 | 0.6465 | 0.6231 | 0.6515 | 0.6584 |

### hole_v1

| model | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mean |
|---|---|---|---|---|---|---|---|---|
| global_mean | 0.6938 | 0.6853 | 0.6789 | 0.6561 | 0.6486 | 0.6381 | 0.6943 | 0.6707 |
| neighbor_label_avg_k3 | 0.9649 | 0.8187 | 0.7827 | 0.7936 | 0.7254 | 0.6719 | 0.9253 | 0.8118 |
| subject_prior_a20 | 0.6871 | 0.6744 | 0.6654 | 0.6018 | 0.5729 | 0.5320 | 0.6479 | 0.6259 |
| tiny_logistic_topk20 | 0.7036 | 0.7060 | 0.6911 | 0.6127 | 0.5587 | 0.5104 | 0.6375 | 0.6314 |

### mirror_v1

| model | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mean |
|---|---|---|---|---|---|---|---|---|
| global_mean | 0.6952 | 0.6829 | 0.6665 | 0.6286 | 0.6701 | 0.6570 | 0.6878 | 0.6697 |
| neighbor_label_avg_k3 | 1.0517 | 1.0836 | 1.0538 | 0.8580 | 0.7623 | 0.8319 | 0.8302 | 0.9245 |
| subject_prior_a20 | 0.6861 | 0.7073 | 0.6903 | 0.5877 | 0.6039 | 0.5771 | 0.6436 | 0.6423 |
| tiny_logistic_topk20 | 0.7235 | 0.7709 | 0.7627 | 0.6132 | 0.5987 | 0.5989 | 0.6296 | 0.6711 |


## 4. Decision rules suggested by this table

- If `subject_prior_a20` mirror score ≈ subject_prior chrono_tail score, the
  static-subject baseline is regime-stable and is the right anchor.
- If `neighbor_label_avg_k3` has a large negative `tail_minus_hole` (much better on
  hole), confirm: chrono_tail is *not* a substitute for the hole regime.
- If `tiny_logistic_topk20` mirror score is *worse* than its chrono_tail score,
  the public LB gap (CV 0.5933 → LB 0.6421) is at least partly explained by
  hole-regime degradation, not by overfit per se.
- Submission gate proposal: any new submission must satisfy
      mirror_v1_avg ≤ best_known_mirror + 0.005
    AND no per-target hole_v1 logloss worse than subject_prior_a20 + 0.01.
