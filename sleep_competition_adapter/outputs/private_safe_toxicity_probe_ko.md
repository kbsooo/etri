# Private-Safe Toxicity Probe

이 프로브는 public/private toxicity head가 단순히 나쁜 제출을 기억하는 장치인지, 아니면 action-health field로 볼 수 있는지 확인한다.

## Verdict

- Status: `toxicity_field_promising_with_hardworld_gap`
- Mean leave-one-bad-anchor AUC: `0.7880`
- Median leave-one-bad-anchor AUC: `0.7986`
- Mean leave-one-bad-anchor AP: `0.6118`
- Worst leave-one-bad-anchor AUC: `0.3683`
- Anchors below 0.60 AUC: `2`
- Selected safety z vs matched null: `8.4589`
- P(null safety >= selected): `0.0000`

The toxicity field is strong on most bad anchors, but a hard-world toxicity mode is still not captured.

## Matched-Null Selection Stress

- Selected cells: `150` / candidate cells `863`
- Selected toxicity safety mean: `0.7631`
- Null toxicity safety mean: `0.6547`
- Selected toxicity rank mean: `0.2369`
- Null toxicity rank mean: `0.3453`
- Selected listener score mean: `0.7672`
- Null listener score mean: `0.6297`

## Boundary

- `leave-one-anchor`가 높아도 이는 bad public anchors 사이의 일반화일 뿐 private LB 증거는 아니다.
- matched null 대비 safety가 높지 않으면 toxicity head는 action decoder가 아니라 diagnostic으로만 써야 한다.
- 이 probe는 새 submission을 만들지 않는다.
