# Hard-World Toxicity Factorization Probe

이 프로브는 H088 hard-world 실패가 broad bad-anchor toxicity의 한 사례인지, 아니면 별도 action-health mode인지 검증한다.

## Verdict

- Status: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`
- Broad-safe but H088-toxic cells: `215`
- Selected joint safety z: `7.1884`
- Selected H088 top-toxic rate: `0.0333` vs null `0.1027`

H088 is not a harder sample of broad toxicity; it is an anti-correlated hard-world mode. The adapter should keep separate broad-public and hard-world toxicity heads.

## Mode Separation

- Hard-world anchor: `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv`
- H088 active cells: `737` / `0.8540`
- H088 active rate in broad top quartile: `0.7454`
- H088 active rate in broad bottom quartile: `0.8928`
- Existing decoder selected H088 top-toxic rate: `0.0333`
- All candidates H088 top-toxic rate: `0.2503`

## Matched-Null Stress

- Selected cells: `150` / candidates `863`
- Selected hard-world safety mean: `0.7363` vs null `0.6995`
- Hard-world safety z: `2.8521`
- Selected joint safety mean: `0.6372` vs null `0.5606`
- Joint safety z: `7.1884`
- Selected broad-safe/H088-toxic rate: `0.0800` vs null `0.1042`

## Sectors

| Sector | Cells | Selected | Mean broad toxic | Mean hard toxic |
| --- | ---: | ---: | ---: | ---: |
| `broad_safe_hardworld_toxic` | `215` | `12` | `0.2005` | `0.8376` |
| `broad_toxic_hardworld_safe` | `193` | `33` | `0.8285` | `0.1925` |
| `dual_safe` | `78` | `53` | `0.2005` | `0.1948` |
| `dual_toxic` | `80` | `0` | `0.7777` | `0.7354` |

## Decoder Implication

Scalar toxicity is not enough.  HS-JEPA action-health should be represented as at least two listener-conditioned heads:

```text
broad public-bad toxicity head
  + hard-world / H088 toxicity head
  -> joint safety or mixture-gated action decoder
```

이 probe는 새 submission을 만들지 않는다. 다음 big-bet은 이 factorized toxicity를 실제 row-target assignment solver에 넣는 것이다.
