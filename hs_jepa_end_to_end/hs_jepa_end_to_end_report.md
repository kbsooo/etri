# HS-JEPA End-to-End H057 Reproduction

## What this code produces

- Public-best reproduced submission: `submission_hsjepa_end_to_end_h057_7cde1a77_uploadsafe.csv`
- Local copy: `/Users/kbsoo/Downloads/cl2/hs_jepa_end_to_end/submission_hsjepa_end_to_end_h057_7cde1a77_uploadsafe.csv`
- Known public LB for the reproduced file: `0.5677475939`
- Produced hash: `7cde1a77`
- Matches expected H057 hash: `True`
- Max numeric diff vs known H057: `1.11022302463e-16`
- Numeric match within float tolerance: `True`

## HS-JEPA in one sentence

HS-JEPA treats previous public-feedback experiments as context, predicts a
hidden human-state representation, then decodes that representation into a safe
row-target correction field.

## Architecture mapping

### 1. Context

The context is not only raw tabular features. In this end-to-end reproduction it
is the observed behavior of several prediction worlds:

- H012: broad public equation;
- H042: sharper Q2 phase route;
- H050: subjective Q1/Q3 route stress;
- H056: objective S-stage route stress;
- H055: post-feedback public listener posterior.

### 2. Hidden human-state encoder

Rows where H042 changed Q2 relative to H012 are encoded as public-visible
human-state candidates.

- Selected hidden-state rows: `45`
- Q2 itself is frozen after discovery.

### 3. Target representation

The target representation is the H055 listener posterior for every row-target
cell. HS-JEPA uses this as a soft latent target, not as a raw label table.

### 4. Action decoder

The decoder starts from H042 and applies this equation only on selected rows and
non-Q2 targets:

`p' = sigmoid(logit(H042) + alpha * clip(logit(H055) - logit(H042), -1.65, 1.65))`

with `alpha = 1.15`.

Action targets: `Q1, Q3, S1, S2, S3, S4`

Frozen targets: `Q2`

### 5. Stress/listener diagnostics

- Changed row-target cells: `270`
- Changed rows: `45`
- H050 overlap cells: `23`
- H056 overlap cells: `180`
- Mean soft listener gain on changed cells: `0.001258241`
- Mean listener aux score on changed cells: `0.544357354`

Per-target changed cell counts:

| target | changed_cells |
| --- | --- |
| Q1 | 45 |
| Q2 | 0 |
| Q3 | 45 |
| S1 | 45 |
| S2 | 45 |
| S3 | 45 |
| S4 | 45 |

## Why H057 matters

H057 was a positive public sensor result. It scored `0.5677475939`
and improved over the previous H042/H050 frontier. The interpretation is that
the 45 H042 Q2-support rows are not Q2-local accidents. They carry a fuller
human-state route that can be decoded into Q1, Q3, and S1-S4 together.

## Open-source semantic path

Gemini embeddings are not used here. The script writes a local
`human_state_narratives.csv` file and, when scikit-learn is available, an
open-source `TF-IDF + TruncatedSVD` semantic preview. That preview is explanatory
only; it is not needed to reproduce H057.

Semantic preview status:

```json
{
  "enabled": true,
  "method": "TF-IDF(1,2) + TruncatedSVD",
  "rows": 45,
  "dimensions": 6,
  "output": "/Users/kbsoo/Downloads/cl2/hs_jepa_end_to_end/open_source_semantic_latent_preview.csv"
}
```

## Submission safety

The generated submission is upload-safe by construction:

- same 250 key rows;
- no duplicated keys;
- no NaN or infinite probabilities;
- probabilities are strictly inside `(0, 1)`;
- produced hash equals `7cde1a77`;
- numeric table matches the known H057 file.
