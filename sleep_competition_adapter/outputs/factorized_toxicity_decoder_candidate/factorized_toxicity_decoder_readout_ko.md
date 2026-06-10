# Factorized Toxicity Decoder Candidate

이 산출물은 HS-JEPA core가 아니라 sleep competition adapter의 action-health decoder다.

## Worldview

H088류 hard-world 독성은 broad public-bad 독성과 같은 축이 아니라 반상관된 별도 축이다. 따라서 row-target action은 scalar safety가 아니라 broad-public safety와 hard-world safety를 동시에 통과해야 한다.

## Probe Input

- Hard-world factorization status: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`
- Broad-safe but H088-toxic cells: `215`

## Generated Candidates

| Variant | File | Changed cells | Joint safety | H088 top-toxic rate | Upload-safe |
| --- | --- | ---: | ---: | ---: | ---: |
| `teacher_dual_head` | `submission_hsjepa_factorized_toxicity_decoder_teacher_dual_head_2a3c5d2d_uploadsafe.csv` | `94` | `0.6937` | `0.0000` | `True` |
| `dual_safe_expansion` | `submission_hsjepa_factorized_toxicity_decoder_dual_safe_expansion_23b6de1e_uploadsafe.csv` | `114` | `0.6994` | `0.0000` | `True` |

## Interpretation

- `teacher_dual_head`: 기존 public-sensor teacher support는 유지하되 hard-world 독성축에서 위험한 cell을 강하게 damp한다.
- `dual_safe_expansion`: teacher support에 더해 broad/hard 두 safety head를 모두 통과한 LRJ cell만 확장한다.
- 이 후보가 public에서 좋아지면 scalar toxicity가 아니라 factorized action-health decoder가 맞다는 증거다.
- 나빠지면 hard-world factorization은 diagnostic으로는 맞지만, 아직 action-grade decoder로 번역되지 않았다는 뜻이다.
