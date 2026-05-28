# Cross-View JEPA Surprise Combo Report

Target-wise strict cross-view JEPA surprise corrections are combined on top of the stage2 public anchor.

## Summary

```csv
combo,n_ops,targets,base_loss,candidate_loss,delta,subject_half_delta,subject_half_win_rate,geometry_delta,geometry_win_rate
cvjepa_surprise_full_nonq2,6,"Q1,Q3,S1,S2,S3,S4",0.5675309247,0.5646068482,-0.0029240765,-0.0029323116,0.9423076923,-0.0034774605,0.875
cvjepa_surprise_full_nonq2_w030,6,"Q1,Q3,S1,S2,S3,S4",0.5675309247,0.56511369,-0.0024172346,-0.002423604,0.9846153846,-0.0027401668,1.0
cvjepa_surprise_core_q1_q3_s2_s4,4,"Q1,Q3,S2,S4",0.5675309247,0.5651957335,-0.0023351912,-0.0022590688,0.9115384615,-0.0028821278,0.875
cvjepa_surprise_s_targets,4,"S1,S2,S3,S4",0.5675309247,0.5655769948,-0.0019539299,-0.0020376131,0.8615384615,-0.0021378571,0.875
cvjepa_surprise_full_nonq2_w020,6,"Q1,Q3,S1,S2,S3,S4",0.5675309247,0.5657135547,-0.00181737,-0.0018219395,1.0,-0.0020147718,1.0
cvjepa_surprise_q1_s2,2,"Q1,S2",0.5675309247,0.5660898414,-0.0014410833,-0.0013572346,0.9615384615,-0.0021182518,0.875
cvjepa_surprise_q_targets,2,"Q1,Q3",0.5675309247,0.5665607781,-0.0009701466,-0.0008946985,0.9846153846,-0.0013396034,0.875
```

## Best Candidate

- Best by OOF/geometry: `cvjepa_surprise_full_nonq2`.
- OOF mean: `0.5646068482` vs base `0.5675309247`; delta `-0.0029240765`.
- Subject-half mean delta/win-rate: `-0.0029323116` / `0.942308`.
- Geometry mean delta/win-rate: `-0.0034774605` / `0.875000`.

## Target Deltas

```csv
combo,target,base_loss,candidate_loss,delta
cvjepa_surprise_q1_s2,Q1,0.5746308241,0.5702075973,-0.0044232268
cvjepa_surprise_q1_s2,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_q1_s2,Q3,0.630348489,0.630348489,0.0
cvjepa_surprise_q1_s2,S1,0.4789432759,0.4789432759,0.0
cvjepa_surprise_q1_s2,S2,0.5389534496,0.5332890935,-0.0056643561
cvjepa_surprise_q1_s2,S3,0.5034376795,0.5034376795,0.0
cvjepa_surprise_q1_s2,S4,0.6034040622,0.6034040622,0.0
cvjepa_surprise_core_q1_q3_s2_s4,Q1,0.5746308241,0.5702075973,-0.0044232268
cvjepa_surprise_core_q1_q3_s2_s4,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_core_q1_q3_s2_s4,Q3,0.630348489,0.6279806894,-0.0023677995
cvjepa_surprise_core_q1_q3_s2_s4,S1,0.4789432759,0.4789432759,0.0
cvjepa_surprise_core_q1_q3_s2_s4,S2,0.5389534496,0.5332890935,-0.0056643561
cvjepa_surprise_core_q1_q3_s2_s4,S3,0.5034376795,0.5034376795,0.0
cvjepa_surprise_core_q1_q3_s2_s4,S4,0.6034040622,0.599513106,-0.0038909562
cvjepa_surprise_s_targets,Q1,0.5746308241,0.5746308241,0.0
cvjepa_surprise_s_targets,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_s_targets,Q3,0.630348489,0.630348489,0.0
cvjepa_surprise_s_targets,S1,0.4789432759,0.4769337805,-0.0020094954
cvjepa_surprise_s_targets,S2,0.5389534496,0.5332890935,-0.0056643561
cvjepa_surprise_s_targets,S3,0.5034376795,0.501324978,-0.0021127015
cvjepa_surprise_s_targets,S4,0.6034040622,0.599513106,-0.0038909562
cvjepa_surprise_full_nonq2,Q1,0.5746308241,0.5702075973,-0.0044232268
cvjepa_surprise_full_nonq2,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_full_nonq2,Q3,0.630348489,0.6279806894,-0.0023677995
cvjepa_surprise_full_nonq2,S1,0.4789432759,0.4769337805,-0.0020094954
cvjepa_surprise_full_nonq2,S2,0.5389534496,0.5332890935,-0.0056643561
cvjepa_surprise_full_nonq2,S3,0.5034376795,0.501324978,-0.0021127015
cvjepa_surprise_full_nonq2,S4,0.6034040622,0.599513106,-0.0038909562
cvjepa_surprise_full_nonq2_w030,Q1,0.5746308241,0.5710043843,-0.0036264398
cvjepa_surprise_full_nonq2_w030,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_full_nonq2_w030,Q3,0.630348489,0.6282780286,-0.0020704603
cvjepa_surprise_full_nonq2_w030,S1,0.4789432759,0.4772221712,-0.0017211047
cvjepa_surprise_full_nonq2_w030,S2,0.5389534496,0.534503382,-0.0044500676
cvjepa_surprise_full_nonq2_w030,S3,0.5034376795,0.5016042118,-0.0018334677
cvjepa_surprise_full_nonq2_w030,S4,0.6034040622,0.6001849597,-0.0032191025
cvjepa_surprise_full_nonq2_w020,Q1,0.5746308241,0.5719189733,-0.0027118507
cvjepa_surprise_full_nonq2_w020,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_full_nonq2_w020,Q3,0.630348489,0.6287497882,-0.0015987008
cvjepa_surprise_full_nonq2_w020,S1,0.4789432759,0.4776285713,-0.0013147046
cvjepa_surprise_full_nonq2_w020,S2,0.5389534496,0.5356882831,-0.0032651666
cvjepa_surprise_full_nonq2_w020,S3,0.5034376795,0.5020278151,-0.0014098644
cvjepa_surprise_full_nonq2_w020,S4,0.6034040622,0.6009827593,-0.0024213029
cvjepa_surprise_q_targets,Q1,0.5746308241,0.5702075973,-0.0044232268
cvjepa_surprise_q_targets,Q2,0.6429986926,0.6429986926,0.0
cvjepa_surprise_q_targets,Q3,0.630348489,0.6279806894,-0.0023677995
cvjepa_surprise_q_targets,S1,0.4789432759,0.4789432759,0.0
cvjepa_surprise_q_targets,S2,0.5389534496,0.5389534496,0.0
cvjepa_surprise_q_targets,S3,0.5034376795,0.5034376795,0.0
cvjepa_surprise_q_targets,S4,0.6034040622,0.6034040622,0.0
```

## Interpretation

- This is the first explicitly cross-view JEPA residual feature family that opens stage2 OOF while passing repeated subject-half checks on multiple targets.
- Public risk is still nontrivial because stage2's broad residual public transfer was weak; these files should be audited against public-axis/ranker tools before promotion.
- The main latent clue is view mismatch: context cannot predict quiet-window structure for Q1, measurement-process cannot predict rhythm for S2, and sleep/rhythm residuals explain Q3/S4.