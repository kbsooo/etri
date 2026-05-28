# Final JEPA Experiment Summary

## Executive Read

세 JEPA 방향을 모두 실제 submission 산출물까지 실험했다. 직접적인 block-rate/rank 대체는 실패했고, raw timeline I-JEPA도 독립 feature로는 guardrail을 못 넘었다. 대신 중요한 발견은 따로 나왔다.

BlockRate/Q-Rank가 예측한 latent를 확률에 직접 섞지 않고 residual correction feature로 쓰면 full OOF는 크게 좋아진다. 하지만 7-target 전체 조합은 nested guardrail에서 무너졌고, Q2 한 target만 nested에서 살아남았다.

현재 제출 후보로 볼 수 있는 것은 `submission_jepa_latent_q2_w0p45.csv` 또는 보수형 `submission_jepa_latent_q2_w0p3.csv`다.

## 1. BlockRate-JEPA Minimal

실험 파일:
`advanced_jepa_experiments.py`, `blockrate_jepa_minimal_summary.csv`, `submission_blockrate_jepa_minimal.csv`

구조:
subject timeline의 실제 hidden submission block geometry를 target block으로 놓고, 주변 known labels + sensor/rhythm/measurement-process + block position으로 7-target block rate/entropy/endpoint latent를 예측했다.

결과:

```text
best nonzero: alpha=100, weight=0.05
geometry base_loss      0.560886
geometry candidate_loss 0.561706
delta                  +0.000820
```

판정:
직접 rate를 probability에 섞으면 악화된다. block-rate predictor가 oracle gap의 정답 모양을 겨냥하긴 하지만, row probability replacement로 쓰기엔 bias/variance가 너무 크다.

## 2. Q-Rank Count JEPA

실험 파일:
`qrank_count_jepa_selection_summary.csv`, `submission_qrank_count_jepa.csv`

구조:
Q1/Q2/Q3를 row binary가 아니라 subject-relative count/rank latent로 보고, block의 Q count/rank/entropy/endpoint를 예측했다.

결과:

```text
best nonzero: alpha=100, weight=0.05
Q-only delta  +0.000911
mean7 delta   +0.000390
```

판정:
직접 count/rank를 확률에 반영하는 방식은 실패했다. ordinal postprocess 실패와 같은 축으로, 사후 확률 보정식으로 쓰면 안정적이지 않다.

## 3. True Raw-Timeline I-JEPA

실험 파일:
`rawijepa_training_history.csv`, `train_rawijepa_features.parquet`, `submission_rawijepa_features.parquet`, `rawijepa_scan.csv`

구조:
subject별 days x 30분 bins x sensor canvas를 만들었다. 12:00-36:00 window, count/value channel, 12개 sensor modality를 사용했고, context encoder + EMA target encoder + masked target token prediction으로 I-JEPA에 가깝게 학습했다.

학습:

```text
epoch 1    loss 1.387846
epoch 25   loss 0.527304
epoch 100  loss 0.436988
epoch 220  loss 0.380304
```

Residual scan 결과:

```text
best raw feature: Q1 rawijepa__z21 subject_rank
target OOF delta       -0.001094
subject guardrail mean +0.000372
guardrail win-rate      0.431
```

판정:
raw timeline representation은 학습은 됐지만, 현재 feature scan 기준으로는 submit-safe signal이 아니다. Q1 쪽 약한 probe는 있으나 public 제출 후보로 쓰면 안 된다.

## 4. Latent Residual Discovery

실험 파일:
`jepa_latent_residual_probe.py`, `jepa_latent_residual_probe_report.md`, `jepa_latent_nested_guardrail.py`

구조:
직접 block-rate를 섞지 않고, BlockRate/Q-Rank JEPA가 예측한 latent를 residual correction feature로 재사용했다. 즉 `predicted block rate / entropy / endpoint / logit_delta`의 subject-rank나 subject-z가 stage2 residual을 설명하는지 봤다.

Full OOF 결과:

```text
submission_jepa_latent_residual_probe.csv
OOF loss             0.560757
delta vs stage2     -0.006774
bad-axis projection -0.002190
good-axis projection 0.035537
ops                 7
```

하지만 nested guardrail:

```text
all-target latent residual
nested base_loss      0.563588
nested candidate_loss 0.563874
mean_delta           +0.000286
win_rate              0.50
```

판정:
7-target 전체 latent residual 후보는 OOF가 매우 좋아 보여도 nested에서 탈락이다. 이건 selection overfit 또는 feature-generation leakage 가능성이 큰 probe로 분류한다.

## 5. Surviving Slice: Q2 Only

Nested target slice:

```text
Q2 target delta mean -0.004808
Q2 target win-rate    0.75
mean7 nested delta   -0.000687
```

Q2-only candidate sweep:

```text
candidate                                  mean_oof  mean_delta  bad_axis
submission_jepa_latent_q2_w0p1.csv          0.567049  -0.000482  -0.000989
submission_jepa_latent_q2_w0p15.csv         0.566858  -0.000673  -0.001473
submission_jepa_latent_q2_w0p2.csv          0.566697  -0.000833  -0.001954
submission_jepa_latent_q2_w0p3.csv          0.566465  -0.001066  -0.002922
submission_jepa_latent_q2_w0p45.csv         0.566334  -0.001197  -0.004435
```

Recommended candidates:

```text
Primary:      jepa/submission_jepa_latent_q2_w0p45.csv
Conservative: jepa/submission_jepa_latent_q2_w0p3.csv
Hold only:    jepa/submission_jepa_latent_residual_probe.csv
Do not use:   submission_blockrate_jepa_minimal.csv, submission_qrank_count_jepa.csv, submission_rawijepa_selected.csv
```

## Interpretation

JEPA 아이디어 자체는 맞는 방향이었다. 다만 “latent rate를 정답 확률로 직접 쓰기”가 아니라, “hidden block state를 설명하는 latent를 residual correction의 조건 변수로 쓰기”가 맞았다.

핵심 단서는 Q2다. Q2는 수면 개입 정도라서 row event보다 subject/block state 성격이 강하고, `brlatent_a100p0_logit_delta_Q3`의 subject-z가 Q2 residual을 안정적으로 설명했다. 반대로 Q3/S-stage latent들은 full OOF에서는 강해 보여도 nested에서는 깨졌다.
