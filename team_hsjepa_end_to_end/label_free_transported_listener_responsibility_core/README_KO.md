# Label-Free Transported Listener Responsibility Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 히스토리를 몰라도 HS-JEPA core의 `label-free transported listener responsibility` 실험을 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.
또한 성공을 주장하기 위한 실험도 아니다.
이 실험의 역할은 다음 질문을 반증 가능하게 찌르는 것이다.

```text
target 설명과 human-state semantics만으로 listener responsibility를 만들면 충분한가?
```

## 구조

```text
cross-subject transported prototype grammar
  + target description based semantic listener profile
  + row-wise prototype confidence/entropy/energy
  -> label-free listener responsibility
  -> frozen subject-heldout / row-block / chronological probes
```

labels는 listener profile을 만들거나 view를 선택하는 데 쓰지 않는다.
labels는 representation을 고정한 뒤 frozen probe 검증에만 쓴다.

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/label_free_transported_listener_responsibility_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_label_free_transported_listener_responsibility_core.py
```

필요하면 먼저 cross-subject transport 산출물을 자동으로 생성한다.

```text
hsjepa_core/run_cross_subject_prototype_transport_core.py
```

## 출력

```text
hsjepa_core/outputs/label_free_transported_listener_responsibility_core/
paper_hsjepa_core/LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md
```

주요 파일:

- `label_free_transported_listener_responsibility_summary.json`
- `LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md`
- `label_free_transported_listener_probe_metrics.csv`
- `label_free_transported_listener_subject_leakage.csv`

## 현재 결과

```text
verdict:
  label_free_listener_responsibility_prior_positive

subject-heldout:
  semantic listener logloss: 0.677638
  global transport logloss: 0.676724
  prior logloss: 0.677858
  raw lifelog PCA logloss: 0.678707

delta:
  vs prior: -0.000219
  vs raw lifelog PCA: -0.001069
  vs global transport: +0.000914

stress:
  row-block delta vs global: +0.000044
  chronological delta vs global: -0.001343

subject leakage:
  semantic listener: 0.437778
  global transport: 0.542222
  raw lifelog PCA: 0.957778
```

## 해석

이 실험은 약한 positive이자 중요한 boundary다.

좋은 점:

```text
target 설명만으로 만든 semantic listener responsibility도 prior와 raw lifelog PCA는 이긴다.
global transport보다 subject leakage가 낮다.
chronological split에서는 global transport보다 좋다.
```

나쁜 점:

```text
subject-heldout에서는 global transported grammar를 이기지 못한다.
즉 hand-coded human story만으로 listener responsibility를 정하는 것은 부족하다.
```

## 논문 포인트

이 실험은 다음 주장을 막아준다.

```text
HS-JEPA는 사람이 target 설명을 보고 listener profile을 정해주면 충분하다.
```

대신 다음 방향을 강화한다.

```text
HS-JEPA needs a learned label-free listener-responsibility pretext, not only a hand-coded semantic profile.
```

한국어 표현:

```text
인간적인 target 설명은 유용한 inductive bias지만 충분하지 않다.
HS-JEPA가 더 일반적인 architecture가 되려면, listener responsibility 자체를
보이는 생활 context와 hidden grammar 사이의 예측 문제로 학습해야 한다.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
