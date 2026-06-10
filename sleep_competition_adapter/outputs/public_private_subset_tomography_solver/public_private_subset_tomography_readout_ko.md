# Public/Private Subset Tomography Solver

## Thesis

HS-JEPA should not treat scalar public feedback as direct action truth.  It should decompose the feedback into public subset inclusion, hidden label direction, private-safety, and toxicity fields.

## Evidence

- Anchor count: `26`
- Tomography cells: `115`
- Source responsibility LOO corr: `0.7300`

## Verdict

- Status: `candidate_ready`
- Recommended variant: `subset_label_direction_jackpot`
- Reason: Recommended by public-inclusion, label-direction confidence, private-safety, predicted public delta, and upload-safe validation.

## Generated Candidates

| Rank | Variant | Cells | Rows | Public incl. | Label conf. | Private safe | Toxicity | Pred delta | Bad cosine | Upload-safe | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | `subset_label_direction_jackpot` | `18` | `16` | `0.761` | `0.872` | `0.585` | `0.425` | `-4.92956` | `0.0498` | `True` | `submission_hsjepa_subset_tomography_subset_label_direction_jackpot_d12af8ff_uploadsafe.csv` |
| 2 | `qs_dual_subset_route` | `37` | `26` | `0.634` | `0.781` | `0.631` | `0.376` | `-4.57917` | `-0.0392` | `True` | `submission_hsjepa_subset_tomography_qs_dual_subset_route_288f1d64_uploadsafe.csv` |
| 3 | `private_safe_subset_equation` | `21` | `16` | `0.650` | `0.802` | `0.709` | `0.289` | `-2.11267` | `-0.0071` | `True` | `submission_hsjepa_subset_tomography_private_safe_subset_equation_50a31b06_uploadsafe.csv` |
| 4 | `public_private_boundary_probe` | `8` | `8` | `0.794` | `0.885` | `0.391` | `0.629` | `-0.56022` | `0.1144` | `True` | `submission_hsjepa_subset_tomography_public_private_boundary_probe_ef6a50e5_uploadsafe.csv` |
| 5 | `orthogonal_private_rescue` | `2` | `2` | `0.549` | `0.745` | `0.673` | `0.231` | `-0.03017` | `-0.0051` | `True` | `submission_hsjepa_subset_tomography_orthogonal_private_rescue_3ecd2055_uploadsafe.csv` |

## Sensor Interpretation

- If `subset_label_direction_jackpot` wins, the missing state is mainly public subset inclusion plus label direction.
- If `private_safe_subset_equation` wins, private/action-health constraints are the true bottleneck.
- If `public_private_boundary_probe` wins, previous toxicity vetoes were over-conservative.
- If `qs_dual_subset_route` wins, Q and S require different public/private listener routes.
- If all fail, public subset tomography is descriptive but not yet action-grade.
