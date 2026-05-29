# E117 E95-Like Neighborhood Audit

## Question

If the E95 hardtail law is real but underexploited, does the documented
submission universe contain another E95-shaped candidate already waiting nearby?

## Method

- Collected submission filenames referenced by root notes and generated reports.
- Resolved files with the existing local locator, deduplicated exact prediction tensors.
- Compared each unique candidate to mixmin and E95 using target-axis movement,
  E95-direction cosine, Q/S share, E72-adverse hard-label exposure, and
  E95-relative edit size.

## Scan Scale

- referenced names: `5277`
- resolved files: `4477`
- unique prediction tensors: `4031`
- duplicate tensors skipped: `446`
- unresolved names skipped: `800`

## Key Observations

- E95 L1 vs mixmin: `1.509562`.
- E95 E72-adverse positive exposure: `0.000788914`.
- E95-like neighborhood count: `10`.
- E95-like candidates with no higher E72-adverse exposure than E95: `4`.
- E95-relative surgical variants within 250 changed cells: `6`.
- E101 is not an E95-like replacement from mixmin; it is an E95-relative micro edit: active cells vs E95 `50`, L1 vs E95 `0.079624`, E95-relative Q2/S3 share `1.000000`.

## Known Public Anchors In This Geometry

| file | public_lb | public_delta_vs_e95 | cosine_with_e95_from_mixmin | l1_prob_vs_mixmin | q_l1_share | s_l1_share | e72_adverse_positive_exposure_all |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000000000 | 1.000000000 | 1.509561520 | 0.019948261 | 0.980051739 | 0.000788914 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000015311 |  | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000116447 | 0.327032788 | 2.203481519 | 0.450787914 | 0.549212086 | 0.002330945 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439321 | 0.001147991 | 0.484351900 | 14.867692665 | 0.466702130 | 0.533297870 | 0.004146123 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.002012035 | 0.075804991 | 38.794470993 | 0.480393820 | 0.519606180 | 0.012885880 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.002136023 | 0.000394014 | 52.586264257 | 0.457003298 | 0.542996702 | 0.025058260 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.003509956 | 0.254631953 | 32.945925696 | 0.618309397 | 0.381690603 | 0.007744391 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.003955489 | 0.241913794 | 47.176291066 | 0.599938751 | 0.400061249 | 0.011812808 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.004935998 | 0.356954846 | 46.149828963 | 0.474392739 | 0.525607261 | 0.011039848 |

## Closest Non-E95 Neighborhood

| file | e95_like_score | cosine_with_e95_from_mixmin | l1_prob_vs_mixmin | l1_prob_vs_e95 | q_l1_share | s_l1_share | q2s3_l1_share | e72_adverse_positive_exposure_all | e72_adverse_weighted_positive_mean | active_cells_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e89_e72decontam_00d7807f.csv | 0.042840290 | 0.993205110 | 1.474759113 | 0.107467968 | 0.000000000 | 1.000000000 | 0.193132572 | 0.000799109 | 0.002497430 | 158 |
| submission_e101_q2s3tail_177569bc.csv | 0.088329676 | 0.990587323 | 1.429937385 | 0.079624135 | 0.015786163 | 0.984213837 | 0.166002525 | 0.000692235 | 0.002072252 | 50 |
| submission_e85_inverse_conflict_pruned_58b23ed1.csv | 0.122773232 | 0.991735766 | 1.296983249 | 0.218941615 | 0.000000000 | 1.000000000 | 0.219605011 | 0.000739201 | 0.002410231 | 444 |
| submission_e108_if_e101win_strict_amp038_64514c53.csv | 0.133613044 | 0.975853129 | 1.388631476 | 0.120930044 | 0.013434472 | 0.986565528 | 0.141194630 | 0.000642186 | 0.001828971 | 50 |
| submission_e108_if_e101win_amp050_079aab57.csv | 0.191779251 | 0.954201468 | 1.350562900 | 0.158998620 | 0.011136879 | 0.988863121 | 0.116987318 | 0.000596122 | 0.001605187 | 50 |
| submission_e87_noq2_source_consensus_a85c4e39.csv | 0.201795908 | 0.992981253 | 1.594531553 | 0.145417412 | 0.000000000 | 1.000000000 | 0.213310098 | 0.000906798 | 0.002924102 | 504 |
| submission_e87_q2_nooverstep_consensus_acd7add0.csv | 0.295975199 | 0.983732849 | 1.366145325 | 0.333351402 | 0.085409990 | 0.914590010 | 0.265508757 | 0.000806856 | 0.002654275 | 579 |
| submission_e90_e72pareto_28925de5.csv | 0.366822692 | 0.988671525 | 1.622697903 | 0.151379680 | 0.054815719 | 0.945184281 | 0.239630650 | 0.000934031 | 0.002988389 | 162 |
| submission_e86_e85_consensus_a3f7c96f.csv | 0.570411720 | 0.983732849 | 1.708091281 | 0.198529761 | 0.085420112 | 0.914579888 | 0.265724434 | 0.001010242 | 0.003325247 | 134 |
| submission_e87_inverse_top_prior_consensus_5445ec28.csv | 0.983964930 | 0.831678809 | 1.043236428 | 0.835138080 | 0.138930512 | 0.861069488 | 0.433426581 | 0.000876340 | 0.003150681 | 578 |

## Interpretation

The useful fact is whether the neighborhood is abundant and clean. If many
large S-heavy, E95-aligned, lower-tail candidates existed, the plateau would
look like a selector failure. If the neighborhood is tiny, dominated by already
known E85/E86/E89/E90/E101-family edits, or does not improve hard-tail exposure,
then E95's small public edge is more natural: it sits near a narrow compromise
between retained structure and public-tail damage.

## Belief Update

- Strengthens H110 if E101 appears as a micro edit rather than a standalone
  E95 replacement: public feedback must decide its branch.
- Strengthens the plateau explanation if no untested, lower-tail, E95-like
  neighbor dominates the current frontier anatomy.
- Weakens the idea that "just search the existing submission universe harder"
  is enough to escape the 0.57629 shelf.

## Outputs

- `e117_e95_like_neighborhood_summary.csv`
- `e117_e95_like_neighborhood_shortlist.csv`
- `e117_e95_like_neighborhood_target_detail.csv`
