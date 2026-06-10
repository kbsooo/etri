# Route-Toxicity Fusion Decoder

이 실험은 HS-JEPA sleep adapter의 네 번째 action-decoder 계열이다.

## Verdict

- Status: `route_toxicity_fusion_decoder_alive`
- Recommended variant: `seed_driver_safe_route_fusion`
- Reason: Route-first bundles survive upload safety while also passing factorized hard-world and broad-public toxicity gates. This is an LB sensor for the fused action decoder.

## Worldview

좋은 action은 route frontier 위에 있으면서 broad-public toxicity와 hard-world toxicity를 동시에 통과해야 한다. 따라서 route-first와 action-health-first는 대립이 아니라 순서가 있는 두 단계로 본다.

## Generated Candidates

| Variant | File | Bundles | Changed cells | Route gain | Route rank | Joint safety | Hard safe | Broad safe | Upload-safe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `s2_route_toxicity_fusion` | `submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv` | `4` | `8` | `0.0221` | `0.6735` | `0.7445` | `0.7487` | `0.6532` | `True` |
| `seed_route_toxicity_fusion` | `submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv` | `4` | `8` | `0.0221` | `0.6735` | `0.7445` | `0.7487` | `0.6532` | `True` |
| `open_route_toxicity_fusion` | `submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv` | `2` | `4` | `0.0149` | `0.5328` | `0.7063` | `0.7074` | `0.6176` | `True` |
| `s2_driver_safe_route_fusion` | `submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv` | `10` | `20` | `0.0302` | `0.7902` | `0.6178` | `0.6498` | `0.5074` | `True` |
| `seed_driver_safe_route_fusion` | `submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv` | `10` | `20` | `0.0284` | `0.7732` | `0.5972` | `0.6322` | `0.5096` | `True` |
| `open_driver_safe_route_fusion` | `submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv` | `10` | `20` | `0.0214` | `0.6596` | `0.5588` | `0.5892` | `0.4307` | `True` |

## Null Stress

| Variant | Broad route z | Matched fusion z | Matched safety z | Matched hard-safe z | Matched broad-safe z |
| --- | ---: | ---: | ---: | ---: | ---: |
| `s2_route_toxicity_fusion` | `-0.06` | `0.00` | `0.00` | `-0.00` | `0.00` |
| `seed_route_toxicity_fusion` | `-0.05` | `0.00` | `0.00` | `-0.00` | `0.00` |
| `open_route_toxicity_fusion` | `-0.17` | `0.00` | `0.00` | `-0.00` | `-0.00` |
| `s2_driver_safe_route_fusion` | `2.52` | `3.33` | `1.44` | `1.93` | `1.33` |
| `seed_driver_safe_route_fusion` | `1.96` | `4.04` | `1.14` | `1.71` | `1.74` |
| `open_driver_safe_route_fusion` | `1.25` | `1.87` | `1.19` | `1.72` | `0.83` |

## Interpretation

- 좋아지면 HS-JEPA의 action-grade decoder는 `route invariant -> factorized action-health -> sparse decode` 순서가 맞다는 뜻이다.
- 나빠지면 toxicity gate가 public-good route action까지 과하게 잘랐거나, hard-world toxicity가 아직 private-safe field가 아니라는 뜻이다.
- open fusion이 좋아지면 selected seed 밖에도 안전한 hidden route가 존재한다는 강한 증거다.
