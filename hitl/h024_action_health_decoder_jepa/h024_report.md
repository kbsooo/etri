# H024 Action-Health Decoder JEPA
## Question
H012 proved that a hidden public-state posterior can be materialized. H023 showed that public-compatible vector worlds are human-state aligned. H024 asks whether we can decode which post-H012 action is healthy rather than just public-equation attractive.
## Known public sensors
- known public files used: 20
- current best sensor: `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` = 0.5681234831
- bad anchors include H010, E323, E216, E267 when their files are locally available.
## Model stress
- best LOO decoder: `geometry` alpha=100.0 MAE=0.000773, Spearman=0.970, pairwise=0.947
- H012 leave-one-out sanity among top decoders:
  - geometry a=100.0: pred 0.561120 vs actual 0.568123
  - state a=100.0: pred 0.567631 vs actual 0.568123
  - state a=10.0: pred 0.561250 vs actual 0.568123
  - geometry a=10.0: pred 0.548709 vs actual 0.568123
  - geometry a=1.0: pred 0.541320 vs actual 0.568123
## Candidate ranking
- `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` score=0.570201, pred=0.568133 [0.566993,0.569306], support<H012=0.15, source=known_or_root
- `submission_e95_hardtail_541e3973.csv` score=0.577001, pred=0.576297 [0.576272,0.576621], support<H012=0.00, source=known_or_root
- `submission_e101_q2s3tail_177569bc.csv` score=0.577008, pred=0.576303 [0.576273,0.576643], support<H012=0.00, source=known_or_root
- `submission_mixmin_0c916bb4.csv` score=0.577034, pred=0.576334 [0.576282,0.576755], support<H012=0.00, source=known_or_root
- `submission_e176_abl_q2_to0p75_91e49725.csv` score=0.577109, pred=0.576346 [0.576308,0.576819], support<H012=0.00, source=known_or_root
- `submission_e72_topabs50_q2s3_gate_4e48cba2.csv` score=0.577177, pred=0.576427 [0.576356,0.576881], support<H012=0.00, source=known_or_root
- `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` score=0.578183, pred=0.577268 [0.576909,0.577421], support<H012=0.00, source=known_or_root
- `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv` score=0.578431, pred=0.577686 [0.577534,0.577924], support<H012=0.00, source=known_or_root
- `submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv` score=0.578830, pred=0.577993 [0.577910,0.578221], support<H012=0.00, source=known_or_root
- `submission_h015_top_all_k100_a0.7_a3e35d5c.csv` score=0.578925, pred=0.570054 [0.559653,0.580761], support<H012=0.15, source=h015_public_equation_self_feedback
## Null stress
- selected median margin vs H012: 0.001930; permutation p(lower-is-better)=0.841; null median margin=-0.000007
## Decision
- decision: `diagnostic_only_decoder_not_stable_enough`
- selected diagnostic file: `hitl/h015_public_equation_self_feedback/submission_h015_top_all_k100_a0.7_a3e35d5c.csv`

Interpretation: this is an action-health decoder, not a new posterior generator. A candidate is promoted only if the decoder also survives leave-one-out and permutation stress; otherwise it remains a sensor.
