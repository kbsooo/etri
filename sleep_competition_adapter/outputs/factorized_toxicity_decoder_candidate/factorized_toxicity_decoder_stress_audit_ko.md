# Factorized Toxicity Decoder Stress Audit

이 audit은 factorized toxicity decoder가 단순히 upload-safe인지가 아니라, target/source 구조를 맞춘 feasible null보다 hard-world/conflict exposure를 더 잘 피하는지 검증한다.

## Verdict Table

| Variant | Verdict | Cells | Joint safety | Target-null joint z | Hard-toxic exposure | Conflict exposure |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `dual_safe_expansion` | `factorized_decoder_stress_supported` | `114` | `0.7125` | `13.67` | `0.0000` | `0.0000` |
| `teacher_dual_head` | `factorized_decoder_alive_but_source_null_weak` | `94` | `0.7099` | `12.07` | `0.0000` | `0.0000` |

## Scalar Toxicity Baseline

- Cells: `150`
- Joint safety weighted: `0.6513`
- H088 top-toxic exposure: `0.0274`
- Broad-safe/H088-toxic exposure: `0.0672`

## Interpretation

- target-only null은 같은 target count만 보존하므로 선택 자체가 얼마나 특이한지 본다.
- source-matched null은 teacher/LRJ source 구조까지 보존하므로 더 보수적이다.
- source-matched null이 약하거나 degenerate해도, target-null에서 hard/conflict exposure가 낮으면 decoder 방향은 살아 있다.
- 이 결과는 public/private LB를 보장하지 않는다. 외부 제출 전 local action-health stress만 검증한다.
