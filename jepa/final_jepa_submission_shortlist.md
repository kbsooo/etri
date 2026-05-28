# Final JEPA Submission Shortlist

Known public anchor:

- `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`: public `0.5775263072`, OOF `0.565609`.

Priority candidates produced after that anchor:

| priority | candidate | reason | OOF | bad-axis | raw-good |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | `submission_jepa_axis_stack_raw05_bc_noq2_10_rw0p5_bw1p0.csv` | Best conservative stack: raw public-positive anchor + Block-Canvas no-Q2, negative failed-JEPA axis | 0.559026 | -0.028320 | 0.665770 |
| 2 | `submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv` | Best balanced multi-feature/raw stack: much lower OOF while keeping bad-axis small | 0.555633 | 0.017892 | 0.608782 |
| 3 | `submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p75.csv` | More conservative multi-feature stack; lower raw-good exposure and small bad-axis | 0.556054 | 0.016051 | 0.358782 |
| 4 | `submission_jepa_axis_stack_raw05_bc_noq2_10_rw0p5_bw0p75.csv` | Safer global stack than priority 1; still negative failed-JEPA axis | 0.560162 | -0.020319 | 0.624328 |
| 5 | `submission_block_canvas_jepa_strict_noq2_scale1p0.csv` | Pure Block-Canvas no-Q2 reference; strongest single Block-Canvas candidate | 0.559936 | -0.032003 | 0.165770 |
| 6 | `submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw1p0.csv` | Aggressive raw-anchored multi-feature candidate; submit only after safer ones | 0.554194 | 0.022015 | 0.561710 |

Interpretation:

- The old failed JEPA latent submissions showed that low OOF alone is not enough. The shortlist therefore prioritizes candidates with either negative failed-JEPA-axis projection or small positive projection.
- `noq2` is deliberate. The public result for `submission_jepa_latent_q2_w0p45.csv` made Q2 JEPA movement suspect, so the best candidates leave Q2 at the stage2 baseline.
- The multi-feature rawstack candidates are the highest-upside branch, but the global axis-stack candidate is the cleaner first submission because its bad-axis projection is negative.

