# Public/Private Toxicity Head HS-JEPA

## 실험 목적

Listener Responsibility JEPA는 public score ledger 없이 row-target support를 일부 복원했다.

하지만 문제는 남아 있다.

> Listener Responsibility가 고른 support 중 어떤 action은 안전하고, 어떤 action은 public/private에서 toxic할 수 있다.

이번 실험은 HS-JEPA를 두 층으로 분리한다.

1. **Listener Responsibility JEPA**
   - public score를 읽지 않는 support generator
   - source/listener consensus + OG human-state context로 후보 cell/sign 생성

2. **Public/Private Toxicity Head**
   - competition-specific decoder
   - public이 벌준 bad-anchor action과의 정렬을 보고 teacher action을 증폭/감쇠하고, LRJ extra action 중 안전한 것만 추가

즉 support는 논문형 architecture에서 만들고, toxicity 판단은 대회용 decoder가 맡는다.

## 핵심 한 줄

Candidate 1 teacher 94개 cell은 모두 유지하되 평균 1.168배로 조정했고, Listener Responsibility extra 56개 cell을 toxicity-safe 조건으로 추가한 high-risk big-bet 후보를 만들었다.

## 코드

```bash
python3 paper_hsjepa_core/public_private_toxicity_head.py
```

## 산출물

- 제출 후보:
  - `submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv`

- 세부 산출물:
  - `paper_hsjepa_core/outputs/public_private_toxicity_head/public_private_toxicity_readout.json`
  - `paper_hsjepa_core/outputs/public_private_toxicity_head/toxicity_candidate_cell_table.csv`
  - `paper_hsjepa_core/outputs/public_private_toxicity_head/toxicity_action_audit.csv`
  - `paper_hsjepa_core/outputs/public_private_toxicity_head/toxicity_anchor_ledger.csv`

## 입력과 역할 분리

### Support generator

Support는 `Listener Responsibility JEPA`가 만든다.

- public score ledger 사용: `false`
- source/listener/human-state context 사용

### Toxicity decoder

Toxicity head는 public-bad anchor를 negative sensor로 사용한다.

- public score ledger 사용: `true`
- 목적: support 생성이 아니라 action toxicity 판단

이 분리가 중요하다. 논문에서는 support generator를 HS-JEPA core로 말하고, public/private toxicity head는 competition-specific decoder로 말한다.

## 사용한 bad-anchor 예

public best 대비 충분히 나빴던 제출들을 toxic anchor로 사용했다.

예:

- H088 dual-state gate
- H010 objective S1/S4 route
- E323 residual branch
- E267 human-social tail
- E247/E256 feature-NN smoothing branch
- 기타 public loss가 큰 pre-HS/JEPAlike 후보들

## 결과

| 항목 | 값 |
|---|---:|
| teacher cells retained | 94 |
| LRJ extra cells added | 56 |
| changed cells | 150 |
| changed rows | 111 |
| mean teacher amp | 1.167986 |
| min teacher amp | 1.021606 |
| max teacher amp | 1.220000 |
| upload-safe | true |

Target별 action:

| target | teacher kept | LRJ extra |
|---|---:|---:|
| Q1 | 9 | 6 |
| Q2 | 20 | 15 |
| Q3 | 11 | 3 |
| S1 | 14 | 5 |
| S2 | 14 | 14 |
| S3 | 11 | 6 |
| S4 | 15 | 7 |

## Listener diagnostic

| Metric | Value |
|---|---:|
| base listener mean delta | -0.019670 |
| base listener max delta | -0.003373 |
| base listener negative count | 10 |
| semantic listener mean delta | -0.018912 |
| semantic listener max delta | -0.002972 |
| semantic listener negative count | 10 |
| hard-world cosine | 0.026719 |

Candidate 1보다 changed cell이 많고 listener delta도 더 강하다. 하지만 listener metric이 강하다고 public LB가 좋아진다는 뜻은 아니다. 이 후보는 extra action이 많아 public risk가 크다.

## 제출 후보로서의 해석

좋아지면:

- Listener Responsibility support와 toxicity head가 Candidate 1의 public-loss teacher를 넘어선다는 뜻이다.
- HS-JEPA를 “support generator + toxicity decoder” 구조로 더 강하게 주장할 수 있다.

나빠지면:

- LRJ extra cell은 listener 관점에서는 좋아도 public/private action toxicity를 충분히 분리하지 못했다는 뜻이다.
- 이 경우 toxicity head는 더 보수적이어야 하고, LRJ는 support generator가 아니라 diagnostic/ranking module로 내려간다.

## 현재 판단

이 후보는 안전 제출이 아니다.

성능 1순위는 여전히 Candidate 1이다.

하지만 이 후보는 논문/대회 양쪽에서 의미가 있다.

- 논문적으로는 architecture role split을 보여준다.
- 대회적으로는 Candidate 1 이후의 큰 움직임을 노리는 high-risk candidate다.
- 실패해도 “extra support toxicity가 병목”이라는 결론을 강화한다.

## 다음 개선 방향

현재 toxicity head는 bad-anchor와 같은 방향을 단순히 벌준다.

다음 단계는 더 명확하다.

1. target별 toxicity head 분리
   - Q2는 aggressive 가능
   - S1/S3/S4는 더 보수적으로

2. private-safe head 도입
   - public-bad anchor만 보지 말고, private에도 안전할 action invariant를 찾는다.

3. extra support를 직접 추가하지 않고 teacher action amp만 조절하는 conservative variant 생성
   - 제출 안정성은 이쪽이 더 높을 수 있다.
