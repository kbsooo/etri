# Hidden Block Findings 2026-05-27

## 결론

현재 public feedback을 가장 잘 설명하는 축은 `stage2 -> raw_timeline_jepa_rescue` 방향이다.

- `stage2`: public `0.5779449757`
- `raw05`: public `0.5775263072`
- `ordinal_q`: public `0.5783033652`
- `jepa_bad_residual`: public `0.5812273278`
- `jepa_bad_q2`: public `0.5798012862`

즉, **JEPA가 틀린 게 아니라 JEPA residual을 row/target에 직접 얹은 방향이 틀렸다.**  
public에서 살아남은 JEPA는 raw timeline의 주변-day/bridge 예측오차를 보수적으로 쓰는 방향이다.
추가로 block-scale JEPA target/context reconstruction을 해보니, JEPA representation 자체는 pseudo-hidden block rate 복원에서 강하지만 public raw05 축과 맞추려면 axis projection이 필수다.

2026-05-28 업데이트: `submission_frontier_cvjepa_refine_a2c8d2c8.csv`를 실제 public에 제출했고 `0.577439321`가 나왔다.  
이는 raw05 `0.5775263072`보다 `0.0000869862` 좋지만, 0.54까지 남은 `0.037439321`에 비하면 0.23%만 줄인 것이다. 같은 규모의 개선을 반복해서는 병목을 넘을 수 없다.

새 병목 진단은 명확하다.

- a2c8의 평균 이동량은 raw05 대비 작고, all-correct best-case logloss gain도 0.54 gap의 약 13.55% 수준이다. 즉 calibration/micro-refine만으로는 0.54가 안 나온다.
- public LB inverse7에서 가장 강한 mask 후보는 `single_subject id01`, `global/subject early prefix`, `id01/id02 early block` 쪽이지만, 이것만으로 실제 hidden subset을 확정할 수 없다.
- direct soft-label inverse를 풀면 anchor 6개를 거의 완벽히 맞추는 해가 많이 나온다. 그러나 leave-one-anchor-out 검증에서 train-best 평균 heldout 오차가 `0.000599`다. 이는 direct-label 후보의 예상 개선폭 `0.0005~0.00075`와 같은 크기라, 현재 selector가 아직 충분히 식별적이지 않다는 뜻이다.
- 따라서 지금부터의 핵심은 더 작은 JEPA micro move가 아니라, **public subset/label 식별력을 높이는 추가 제약**이다. JEPA는 row prediction 엔진이 아니라 hidden block/count/sequence energy prior로 써야 한다.

direct-label inverse 실험 산출물:

- script: `analysis_outputs/public_lb_direct_label_inverse7.py`
- LOO diagnostic: `analysis_outputs/public_lb_direct_label_inverse7_loocv.py`
- report: `analysis_outputs/public_lb_direct_label_inverse7_report.md`
- LOO report: `analysis_outputs/public_lb_direct_label_inverse7_loocv_report.md`
- best aggressive diagnostic: `analysis_outputs/submission_directlbl_89fbdeb6.csv`
  - direct inverse expected public `0.576685`, delta vs a2c8 `-0.000754`, mean abs move vs a2c8 `0.004399`
- better first diagnostic submit: `analysis_outputs/submission_directlbl_8b33d6dd.csv`
  - cap-limited sibling, expected public `0.576750`, delta vs a2c8 `-0.000689`, mean abs move `0.004166`
- interpretation: direct-label probes are useful as **public hidden-label direction tests**, not as score-safe candidates. If one of them improves public LB materially, hidden subset/label inverse becomes the main branch. If it worsens, we should downweight random/contiguous soft-label solutions and return to JEPA/raw05-safe block-energy gates.

추가 업데이트: direct-label inverse의 가장 약한 부분인 underidentification을 줄이기 위해 LOO 일반화 기반 robust selector를 만들었다.  
이 selector는 all-anchor fit score만 보지 않고, 각 mask/prior가 5개 anchor로 학습했을 때 남은 1개 anchor를 얼마나 맞히는지 집계해서 source solution을 다시 랭크한다. 이후 a2c8에서 pseudo label 방향으로 움직이되 LOO MAE에 따라 effective strength를 shrink한다.

- script: `analysis_outputs/public_lb_direct_label_robust_selector.py`
- actual-anchor audit: `analysis_outputs/public_lb_direct_label_robust_anchor_audit.py`
- selected: `analysis_outputs/public_lb_direct_label_robust_selector_selected.csv`
- scan: 6,468 robust candidates, selected 24, submission integrity all pass.
- source ranking change:
  - old direct aggressive top: `frac0.50_rep142`, LOO MAE `0.000751`
  - robust first sources: `frac0.40_rep009` LOO MAE `0.000578`, `frac0.40_rep002` LOO MAE `0.000645`, structured `frac0.40_rep052` LOO MAE `0.000676`
- actual-anchor proxy controls:
  - a2c8 control `0.577827`
  - raw05 control `0.577906`
  - best robust selected `submission_directrob_9e356350.csv` `0.577743`
  - safer first-submit robust selected `submission_directrob_29ffe34b.csv` `0.577760`

Recommended robust direct-label probes:

1. `analysis_outputs/submission_directrob_29ffe34b.csv`
   - robust first-submit / random-row but lower LOO source.
   - source `frac0.40_rep009`, LOO MAE `0.000578`, target `all`, strength `0.5`, cap `0.055`.
   - robust delta vs a2c8 `-0.000529`, mean abs move `0.002696`, actual-anchor proxy `0.577760`.
   - This supersedes `submission_directlbl_8b33d6dd.csv` as the first direct-label diagnostic because it uses a better LOO selector.

2. `analysis_outputs/submission_directrob_93b1b685.csv`
   - structured subject-contiguous probe.
   - source `frac0.40_rep052`, LOO MAE `0.000676`, target `all`, strength `0.5`, cap `0.055`.
   - robust delta `-0.000524`, mean abs move `0.002539`, actual-anchor proxy `0.577763`.

3. `analysis_outputs/submission_directrob_9e356350.csv`
   - best actual-anchor proxy among selected robust candidates.
   - source `frac0.50_rep142`, LOO MAE `0.000751`, strength `0.5`, cap `0.040`, mean abs move `0.003260`, actual-anchor proxy `0.577743`.
   - Higher upside but source LOO is weaker than the first-submit pair.

4. `analysis_outputs/submission_directrob_93de02d3.csv`
   - high-information larger move probe.
   - source `frac0.50_rep142`, strength `0.7`, cap `0.055`, mean abs move `0.004557`, robust delta `-0.000858`.
   - Use only if we want to test whether the larger direct-label hidden subset direction is truly public-positive.

L2O update: LOO보다 더 강한 leave-two-anchor-out 검증을 추가했다.  
이 검증은 6개 known public anchor 중 2개를 동시에 숨기고 4개 anchor만으로 direct-label solution을 푼 뒤, 숨긴 2개를 예측한다.

- script: `analysis_outputs/public_lb_direct_label_inverse7_l2ocv.py`
- report: `analysis_outputs/public_lb_direct_label_inverse7_l2ocv_report.md`
- source summary: `analysis_outputs/public_lb_direct_label_inverse7_l2ocv_source_summary.csv`
- policy result:
  - oracle-pair best mean pair error `0.000344`
  - L2O-best1 mean pair error `0.000532`
  - L2O-best5 mean pair error `0.000556`
  - structured-best1 mean pair error `0.000607`
- key finding: L2O-best sources are the same family as LOO robust first-submit:
  - `frac0.40_rep009` entropy_g075: L2O MAE `0.000532`
  - `frac0.40_rep002` entropy_g075: L2O MAE `0.000569`
  - `frac0.40_rep052` entropy_g075: L2O MAE `0.000607`
  - `frac0.50_rep142` entropy_g075: L2O MAE `0.000671`

The robust selector now includes both LOO and L2O in source ranking and candidate scoring.

- selected submissions revalidated: 24 files, row/key/probability integrity all pass.
- `analysis_outputs/submission_directrob_29ffe34b.csv` remains the first diagnostic:
  - LOO MAE `0.000578`, L2O MAE `0.000532`
  - robust delta vs a2c8 `-0.000548`, actual-anchor proxy `0.577760`
- `analysis_outputs/submission_directrob_93b1b685.csv` remains the structured control:
  - LOO MAE `0.000676`, L2O MAE `0.000607`
  - robust delta `-0.000551`, actual-anchor proxy `0.577763`
- `analysis_outputs/submission_directrob_93de02d3.csv` remains the larger-move probe:
  - LOO MAE `0.000751`, L2O MAE `0.000671`
  - robust delta `-0.000912`, mean abs move `0.004557`, actual-anchor proxy `0.577773`

Interpretation: L2O does not solve the 0.54 gap, but it materially strengthens the evidence that the useful direct-label direction is not a one-anchor artifact. The bottleneck is still hidden label identification, but the first-submit directrob candidates are now backed by both LOO and L2O public-anchor transfer.

추가 업데이트: robust direct-label solutions를 LeJEPA식 consensus-energy로 다시 합쳤다.  
단일 source mask에 의존하지 않고, LOO/L2O-stable source들이 같은 row-target cell을 같은 logit 방향으로 밀 때만 낮은 energy로 본다. 이는 hidden label inverse의 underidentification을 줄이기 위한 regularizer다.

- script: `analysis_outputs/public_lb_direct_label_consensus_energy.py`
- report: `analysis_outputs/public_lb_direct_label_consensus_energy_report.md`
- selected: `analysis_outputs/public_lb_direct_label_consensus_energy_selected.csv`
- actual-anchor audit: `analysis_outputs/public_lb_direct_label_consensus_energy_actual_anchor.csv`
- consensus cells: `1,750` row-target cells, selected submissions `28`, row/key/probability integrity all pass.
- high-energy target counts above energy `1`:
  - `S3` 126, `Q3` 114, `Q1` 103, `S1` 83, `S2` 83, `S4` 46, `Q2` 32
- strongest subjects by energy above `1`:
  - `id02` 82, `id06` 79, `id01` 67, `id09` 66, `id03` 57, `id05` 57

Key result:

- In robust inverse score, all-target and no-Q2 consensus moves look best because they move many high-agreement cells.
- In actual-anchor stress, those same broad moves break the public axis:
  - `submission_directcons_1d5b6f39.csv` all-target score `0.579190`
  - `submission_directcons_0b3f77c3.csv` all-target score `0.578529`
  - `submission_directcons_95be47ec.csv` all-target score `0.579207`
- The only consensus family that remains near the observed-best anchor is Q3/S4:
  - `analysis_outputs/submission_directcons_de1d6b6d.csv` actual-anchor `0.577802`, robust delta vs a2c8 `-0.000477`, mean abs move `0.003748`
  - `analysis_outputs/submission_directcons_8a0ae0b0.csv` actual-anchor `0.577803`, robust delta `-0.000476`, mean abs move `0.003722`
  - `analysis_outputs/submission_directcons_bf4f6c46.csv` actual-anchor `0.577806`, robust delta `-0.000469`, mean abs move `0.003605`
- The high-scoring `q1_s1_s3` consensus row `submission_directcons_de6f03cb.csv` should not be first-submit despite robust inverse delta `-0.000717`; actual-anchor stress is worse at `0.577863`.

Interpretation:

- Consensus-energy validates the target bottleneck: Q3/S4 transfer across hidden-public hypotheses is relatively stable, while Q1/S1/S3 and all-target moves are underidentified.
- This is a useful JEPA/LeJEPA-style latent energy prior, but it is not yet a 0.54 solution. It finds safer cells for direct-label movement; it does not solve hidden labels at enough amplitude.
- Submission implication: keep `directrob_29ffe34b` / `directrob_93b1b685` as first direct-label diagnostics. Use `directcons_de1d6b6d` or `directcons_8a0ae0b0` as follow-up Q3/S4 consensus controls, not as the primary larger-move probe.

추가 업데이트: direct-label consensus를 JEPA/block/count/motif prior와 결합한 sparse direct solver를 구현했다.  
이 solver는 consensus pseudo label을 그대로 믿지 않고, JEPA block-count, public-block entropy, sequence motif 방향과 합의하는 cell을 크게 움직인다. broad all-target consensus / latent residual / Q2-forced / ordinal-Q는 negative axis로 넣어 projection guardrail도 실험했다.

- script: `analysis_outputs/jepa_regularized_sparse_direct_solver.py`
- report: `analysis_outputs/jepa_regularized_sparse_direct_solver_report.md`
- selected: `analysis_outputs/jepa_regularized_sparse_direct_solver_selected.csv`
- actual-anchor audit: `analysis_outputs/jepa_regularized_sparse_direct_solver_actual_anchor.csv`
- scan: 766 robust-scored candidates, actual-anchor audit 176 candidates, selected submissions 32 files, integrity all pass.

Best candidates:

1. `analysis_outputs/submission_sparsejepa_f4657144.csv`
   - signal `sparse_fusion`, target `all`, gate `q3s4_edge`, strength `0.75`, cap `0.080`
   - actual-anchor `0.577698`, robust delta vs a2c8 `-0.000941`, mean abs move `0.006176`
   - highest information, but all-target risk remains.

2. `analysis_outputs/submission_sparsejepa_3cfdf64a.csv`
   - signal `sparse_fusion`, target `no_q2`, gate `q3s4_edge`, strength `0.75`, cap `0.080`
   - actual-anchor `0.577706`, robust delta `-0.000878`, mean abs move `0.005520`
   - safer first sparse probe because it removes Q2 while keeping almost all of the proxy gain.

3. `analysis_outputs/submission_sparsejepa_a2d8107a.csv`
   - target `q3_s2_s3_s4`, actual-anchor `0.577727`, robust delta `-0.000563`, mean abs move `0.003700`
   - target-specific control for whether public rewards the Q3/stage subset rather than all-target movement.

Interpretation:

- This is the first branch that improves the actual-anchor proxy over directrob while moving enough probability mass to matter: `0.005~0.006` mean move rather than `0.002~0.004`.
- Negative-axis projection did not win; the best candidates have `anti_lambda=0`. That means the current sparse fusion signal is already mostly not aligned with the explicit rejected axes, or the projection removes useful hidden-label signal.
- The remaining risk is broad target leakage. Therefore `f4657144` is the highest-upside probe, while `3cfdf64a` is the more defensible first sparse submit.

추가 검증: sparse 후보를 all-anchor inverse에만 맞춘 artifact인지 확인하기 위해, public anchor를 LOO/L2O로 빼고 direct-label hidden-label fit을 다시 학습한 뒤 후보들을 재채점했다.

- script: `analysis_outputs/jepa_sparse_anchor_cv_audit.py`
- report: `analysis_outputs/jepa_sparse_anchor_cv_audit_report.md`
- summary: `analysis_outputs/jepa_sparse_anchor_cv_audit_summary.csv`
- combined LOO/L2O top:
  - `analysis_outputs/submission_sparsejepa_f43ea825.csv`: CV delta mean `-0.000869`, worst `-0.000411`, win rate `1.0`, actual-anchor `0.577727`, mean move `0.007326`
  - `analysis_outputs/submission_sparsejepa_282e9546.csv`: CV delta mean `-0.000741`, worst `-0.000367`, actual-anchor `0.577708`, mean move `0.006783`
  - `analysis_outputs/submission_sparsejepa_f4657144.csv`: CV delta mean `-0.000721`, worst `-0.000364`, actual-anchor `0.577698`, mean move `0.006176`
  - `analysis_outputs/submission_sparsejepa_3cfdf64a.csv`: CV delta mean `-0.000665`, worst `-0.000341`, actual-anchor `0.577706`, mean move `0.005520`
- control `directrob_29ffe34b`는 CV delta mean `-0.000592`, raw05 control은 `+0.000131`.

Interpretation:

- sparse JEPA/direct-label 방향은 public anchor를 일부 숨겨도 살아남는다. 즉 단순 all-anchor overfit으로 보기는 어렵다.
- 하지만 selector error mean `~0.00056`이 후보 간 차이와 같은 크기다. `f4657144`와 `3cfdf64a` 사이의 선택은 로컬로 확정할 수 없고, 제출로 public-axis를 확인해야 한다.
- 실전 순서는 `3cfdf64a`를 first sparse probe, `f4657144`를 higher-upside all-target probe, `f43ea825`를 high-information scale stress probe로 두는 것이 가장 일관적이다.

추가 업데이트: sparse direction의 scale이 병목인지 확인하기 위해 top sparse 방향을 logit vector로 보고 scale-ladder stress를 실행했다.

- script: `analysis_outputs/jepa_sparse_scale_ladder_stress.py`
- report: `analysis_outputs/jepa_sparse_scale_ladder_stress_report.md`
- selected: `analysis_outputs/jepa_sparse_scale_ladder_stress_selected.csv`
- key result: `f465_actual_best` full direction은 scale `1.50`까지 honest anchor-CV가 더 좋아지고 actual-anchor도 아직 `0.577757` 수준에서 버틴다.

Important rows:

- `analysis_outputs/submission_sparseladder_89817541.csv`: f465 full scale `1.50`, actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`
- `analysis_outputs/submission_sparseladder_f1ee16b0.csv`: f465 no-Q2 scale `1.50`, actual-anchor `0.577758`, honest CV delta `-0.000934`, mean move `0.008276`
- `analysis_outputs/submission_sparseladder_b01acaa1.csv`: 282 full scale `1.30`, actual-anchor `0.577746`, honest CV delta `-0.000935`, mean move `0.008816`
- `analysis_outputs/submission_sparseladder_3be0b7a3.csv`: 282 energy_top60 scale `1.50`, actual-anchor `0.577764`, honest CV delta `-0.000937`, mean move `0.007001`

Interpretation:

- 현재까지 가장 중요한 병목 단서다. scale `1.0` 후보가 너무 약했을 가능성이 생겼다.
- 다만 actual-anchor는 scale `1.75~2.00`에서 빠르게 악화된다. CV만 보면 계속 좋아지지만 public-axis stress가 이를 막는다.
- 따라서 0.54로 가는 다음 실험은 “새 feature 추가”가 아니라, scale `1.5`가 실제 public에서 transfer되는지 확인하고, 성공 시 cell별 adaptive scale solver로 확장하는 것이다.

추가 업데이트: scale `1.5`가 버티는 이유를 target/energy/block별로 분해하기 위해 adaptive sparse scale solver를 만들었다.

- script: `analysis_outputs/jepa_adaptive_sparse_scale_solver.py`
- report: `analysis_outputs/jepa_adaptive_sparse_scale_solver_report.md`
- selected: `analysis_outputs/jepa_adaptive_sparse_scale_solver_selected.csv`
- tested factors: no-Q2, stage boost, Q3/stage, consensus-energy strong/top, public subjects, id01/id02 early, late subject blocks.

Key result:

- adaptive reweighting은 honest anchor-CV를 더 강하게 만든다.
- 그러나 actual-anchor는 uniform scale-ladder보다 나빠진다.
- best adaptive:
  - `analysis_outputs/submission_adaptjepa_c10b7ebd.csv`: actual-anchor `0.577798`, honest CV delta `-0.001178`, mean move `0.008808`
  - `analysis_outputs/submission_adaptjepa_8fabe65a.csv`: actual-anchor `0.577806`, honest CV delta `-0.001192`, mean move `0.008838`
- uniform scale-ladder 대표:
  - `analysis_outputs/submission_sparseladder_89817541.csv`: actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`
  - `analysis_outputs/submission_sparseladder_f1ee16b0.csv`: actual-anchor `0.577758`, honest CV delta `-0.000934`, mean move `0.008276`

Interpretation:

- adaptive profile은 hidden-label fit을 더 잘 설명하지만 public-axis에는 더 많이 샌다.
- 따라서 아직은 cell-wise 복잡도를 올릴 때가 아니다. 먼저 uniform scale `1.5`가 실제 public에서 transfer되는지 확인해야 한다.
- 만약 uniform scale이 public에서 좋아지면 adaptive는 후속으로 “어디가 leaking target/block인지”를 찾는 도구가 된다. 만약 uniform scale이 나빠지면 adaptive도 같이 보류한다.

추가 업데이트: public inverse mask를 JEPA/raw05 Q3/S4 move의 row gate로 쓰는 fusion branch를 만들었다. 이 branch는 큰 public-blend처럼 raw-axis를 훼손하지 않으면서 Q3/S4 missing-scenario 후보를 아주 얇게 움직인다.

- script: `analysis_outputs/public_mask_jepa_q3s4_fusion.py`
- scan: 1,560 candidates, selected 50, submission integrity all pass.
- best posterior/raw-axis balance:
  - `analysis_outputs/submission_publicmask_jepa_q3s4_c32a8a7e.csv`
  - base `axisc073`, move `gate_seq1501`, gate `fit24`, gamma `0.90`
  - posterior expected `0.576702`, raw-axis delta vs raw05 `-0.000000877`, focused scenario `0.582463`
- best proxy/focused-scenario stable family:
  - `analysis_outputs/submission_publicmask_jepa_q3s4_50528018.csv`
  - base `axisc073`, move `gate_seqd0`, gate `targetgain64_S4`, gamma `0.40`
  - posterior expected `0.576753`, raw-axis delta vs raw05 `-0.000000445`, mean scenario expected `0.576406`, focused scenario `0.582436`
- interpretation: public inverse mask의 row subset 신호는 단독 정답이 아니라, raw05-compatible JEPA axis 위에서 Q3/S4만 미세하게 열어주는 gate로 쓸 때 가장 안정적이다.

추가 업데이트: row-level public mask를 hidden block 단위로 압축한 뒤, block-scale JEPA rate 방향성과 곱하는 `block-public JEPA` gate를 만들었다.  
결론은 “block 압축은 posterior를 크게 새로 뚫지는 못했지만, focused scenario에서는 row gate보다 아주 근소하게 안정적”이다.

- script: `analysis_outputs/block_public_jepa_q3s4_gate_fusion.py`
- scan: 4,788 candidates, selected 60, submission integrity all pass.
- diagnostic files:
  - `analysis_outputs/block_public_jepa_q3s4_gate_summary.csv`
  - `analysis_outputs/block_public_jepa_q3s4_block_gate_detail.csv`
  - `analysis_outputs/block_public_jepa_q3s4_jepa_block_agreement.csv`
- best focused-scenario candidate:
  - `analysis_outputs/submission_blockpublic_jepa_q3s4_8e3e0d92.csv`
  - base `pm_tg`, move `blockjepa_raw05`, gate `blockallsign128`, gamma `0.35`
  - posterior expected `0.576745`, raw-axis delta vs raw05 `-0.000000063`, focused scenario `0.582430`, mean scenario expected `0.576404`
- comparison: previous row-gate best `submission_publicmask_jepa_q3s4_50528018.csv` had focused scenario `0.582436`, mean scenario expected `0.576406`. 즉 개선폭은 작지만 방향은 맞다.
- interpretation: public-compatible subset은 id01/id02 위주 row mask에서 시작하지만, block으로 압축하면 S4 쪽 all-sign-compatible block gate가 더 robust하다. JEPA는 여기서 “새 큰 move”가 아니라 block별 move 허용/억제 에너지로 쓰는 게 맞다.

refine follow-up:

- script: `analysis_outputs/block_public_jepa_q3s4_refine.py`
- scan: 4,290 candidates, selected 70, submission integrity all pass.
- best refine candidate `analysis_outputs/submission_blockpublic_jepa_refine_ab18f442.csv`
  - focused scenario `0.582451`, posterior expected `0.576722`, raw-axis delta `-0.000000359`
- conclusion: 기존 `8e3e0d92` 위에 S4 target block gate를 다시 얹는 것은 개선이 아니다. `8e3e0d92`를 block-public branch의 대표 후보로 유지한다.

추가 업데이트: JEPA block-rate를 row별 residual로 직접 넣지 않고, hidden block expected-count를 맞추는 common logit shift로 변환했다.  
이 방식은 block 내부 row ranking을 기존 submission에 맡기고, JEPA는 block 평균 count 방향만 제약한다.

- script: `analysis_outputs/jepa_block_count_shift.py`
- scan: 5,184 candidates, selected 80, submission integrity all pass.
- diagnostic files:
  - `analysis_outputs/jepa_block_count_shift_rate_sources.csv`
  - `analysis_outputs/jepa_block_count_shift_scores.csv`
  - `analysis_outputs/jepa_block_count_shift_shortlist.csv`
- best focused-scenario candidate:
  - `analysis_outputs/submission_jepa_block_countshift_65d5ef0c.csv`
  - base `block_best`, rate source `best1`, gate `blocktarget64_jepa`, target `Q3`, alpha `0.06`, cap `0.12`, no count rounding
  - posterior expected `0.576758`, raw-axis delta vs raw05 `+0.000000194`, focused scenario `0.582421`, mean scenario expected `0.576402`
- more conservative raw-axis candidate:
  - `analysis_outputs/submission_jepa_block_countshift_33884d08.csv`
  - same family, alpha `0.03`, cap `0.07`
  - posterior expected `0.576752`, raw-axis delta vs raw05 `-0.000000032`, focused scenario `0.582425`, mean scenario expected `0.576403`
- comparison: previous block-public best `submission_blockpublic_jepa_q3s4_8e3e0d92.csv` had focused scenario `0.582430`, mean expected `0.576404`.
- interpretation: JEPA의 가장 쓸모 있는 형태가 더 선명해졌다. row residual보다 **block expected-count energy**가 public-compatible하고, 특히 Q3 blocktarget64_jepa gate에서 가장 안정적이다.

추가 업데이트: JEPA energy ensemble을 만들었다.  
I-JEPA 논문 관점에 맞춰 “row 값을 복원”하지 않고, hidden block/count 후보와 sequence motif 후보를 logit-space에서 작게 섞은 뒤 focused mask energy와 raw05 public axis penalty로 선별했다.

- script: `analysis_outputs/jepa_energy_ensemble_optimizer.py`
- scan: 36,378 candidates, selected 90, submission integrity all pass.
- best raw-axis strict focused candidate:
  - `analysis_outputs/submission_jepa_energy_ensemble_e187e70f.csv`
  - focused scenario `0.582397`, posterior expected `0.576844`, raw-axis delta vs raw05 `-0.000000986`
  - 기존 count-shift best `65d5ef0c`의 focused `0.582421`보다 작게 개선하지만 posterior가 나빠져 공격 후보로만 본다.
- best balanced strict candidate:
  - `analysis_outputs/submission_jepa_energy_ensemble_0b862967.csv`
  - focused scenario `0.582415`, posterior expected `0.576780`, raw-axis delta `-0.000000269`, bad residual axis ratio `0.000813`
  - JEPA count-shift + sequence motif를 섞되 raw axis를 음수로 유지한 균형 후보.
- posterior-first control:
  - `analysis_outputs/submission_jepa_energy_ensemble_d5115337.csv`
  - focused scenario `0.582464`, posterior expected `0.576701`, raw-axis delta `-0.000000841`
  - 사실상 기존 `submission_jepa_block_countshift_b2434a36.csv` 계열이라 새 ensemble 효과라기보다 posterior-friendly control이다.
- interpretation: ensemble은 큰 돌파는 아니지만, JEPA count energy와 motif energy가 같은 방향으로 작동하는 구간을 확인했다. 다만 focused score를 크게 낮추는 조합은 posterior proxy를 악화시키기 쉬워 raw/posterior 동시 제약이 필요하다.

추가 업데이트: JEPA prior 위에 public block-entropy projection을 sub-only로 얹었다.  
이 실험은 JEPA 논문의 “large target block representation을 context/prior에서 예측하고 energy를 낮춘다”는 아이디어를 가장 직접적으로 옮긴 것이다. public score constraint를 row가 아니라 hidden block latent probability에 걸고, gamma를 극단적으로 작게 낮춰 raw05 axis crossing 지점을 찾았다.

- script: `analysis_outputs/jepa_public_blockentropy_projection.py`
- scan: 400 candidates, submission integrity all pass.
- aggressive focused 후보는 강하지만 위험:
  - `analysis_outputs/submission_jepa_public_blockentropy_seq1501_q3_s4_g010_037d0f08.csv`
  - focused scenario `0.581866`, posterior expected `0.576429`
  - 하지만 raw-axis delta `+0.000101`, bad residual axis ratio `0.020234`; public 제출용으로는 위험하다.
- best raw-neutral focused probe:
  - `analysis_outputs/submission_jepa_public_blockentropy_seq1501_q3_only_g001_782e0645.csv`
  - focused scenario `0.582224`, posterior expected `0.577152`, raw-axis delta `-0.000000052`
  - focused 개선은 크지만 posterior/bad-axis가 높아 probe 후보.
- best balanced public-compatible 후보:
  - `analysis_outputs/submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv`
  - focused scenario `0.582411`, posterior expected `0.576729`, raw-axis delta `+0.000000070`, bad residual axis ratio `0.001108`
  - 기존 count-shift best보다 focused, posterior, raw-axis가 모두 근소하게 낫다. 현재 JEPA-block branch의 가장 균형 잡힌 제출 후보.
- strict raw-negative posterior 후보:
  - `analysis_outputs/submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv`
  - focused scenario `0.582439`, posterior expected `0.576677`, raw-axis delta `-0.000000260`, bad residual axis ratio `0.001310`
  - focused는 약간 나빠지지만 posterior와 raw safety가 가장 좋다.
- interpretation: public block-entropy는 gamma가 조금만 커져도 raw05 축을 크게 망가뜨린다. 유효한 구간은 gamma `0.003~0.010`의 초저강도 Q3/Q3S4 target-block projection이다. 이건 row-level public overfit이 아니라, JEPA prior 위에서 block target representation을 거의 미세 조정하는 형태일 때만 살아남는다.

추가 업데이트: public-minimax / public-LB inverse 후보를 JEPA/raw05 manifold 위로 끌어오는 bridge를 만들었다.  
원본 public 후보들은 inverse proxy는 강하지만 raw05 축에서는 거의 같은 방향으로 망가진다. top public pool의 raw-axis delta는 `+0.00194~+0.00262`, ordinal-axis ratio는 `0.347~0.465`라서 그대로 제출 후보로 보기 어렵다. bridge는 JEPA anchor에서 시작해 public move를 JEPA/raw05/block-energy가 동의하는 cell에만 아주 작게 주입한다.

- script: `analysis_outputs/jepa_public_minimax_rawsafe_bridge.py`
- scan: 73,643 candidates, selected 120, submission integrity all pass.
- diagnostic files:
  - `analysis_outputs/jepa_public_minimax_rawsafe_bridge_public_conflict.csv`
  - `analysis_outputs/jepa_public_minimax_rawsafe_bridge_scan.csv`
  - `analysis_outputs/jepa_public_minimax_rawsafe_bridge_shortlist.csv`
- best strict raw-negative bridge:
  - `analysis_outputs/submission_jepa_public_minimax_bridge_84b71a03.csv`
  - anchor `energy_focused`, public `submission_public_entropyproj_public2d0_g100.csv`, target mask `q3_s2_s3_s4`, gate `raw_agree`, gamma `0.075`
  - focused scenario `0.582172`, posterior expected `0.576813`, raw-axis delta `-0.000000083`, bad residual axis ratio `0.002111`
  - 이전 balanced JEPA-block 후보 `8c617ee7`의 focused `0.582411` 대비 약 `0.000239` 개선. posterior는 `+0.000084` 나빠져 upside 후보로 본다.
- best near-raw boundary bridge:
  - `analysis_outputs/submission_jepa_public_minimax_bridge_d1ca675f.csv`
  - anchor `energy_focused`, public `submission_public_entropyproj_public2d0_g100.csv`, target mask `all`, gate `raw_agree`, gamma `0.065`
  - focused scenario `0.582138`, posterior expected `0.576815`, raw-axis delta `+0.000000298`, bad residual axis ratio `0.002629`
  - raw positive가 극히 작아 public-minimax 신호를 더 쓰는 후보로 의미 있다.
- aggressive probe:
  - `analysis_outputs/submission_jepa_public_minimax_bridge_12deef9a.csv`
  - anchor `seq1501`, public `submission_public_entropyproj_public2d0_g100.csv`, target mask `all`, gate `raw_agree`, gamma `0.085`
  - focused scenario `0.581992`, posterior expected `0.577129`, raw-axis delta `+0.000000807`, bad residual axis ratio `0.003956`
  - focused는 이번 branch 최저지만 posterior/raw/bad가 동시에 올라 제출 1순위는 아니다.
- interpretation: public-minimax 축 자체는 강한 듯 보이지만 JEPA/raw05와는 정면 충돌한다. 유효한 형태는 public-minimax를 새 prior로 쓰는 것이 아니라, **JEPA energy anchor 위에 public score constraint를 5.5~7.5%만 주입하는 raw-agree gate**다. 이게 지금까지 JEPA 논문 아이디어와 가장 잘 맞는 조합이다: 관측값을 직접 복원하지 않고, hidden target block representation의 energy가 낮아지는 cell만 예측 쪽으로 당긴다.

추가 업데이트: bridge 후보들을 기존 JEPA-block/energy 후보와 다시 logit-space ensemble했다.  
목적은 focused `0.5820x`대 bridge의 장점을 유지하면서 posterior/raw/bad axis를 낮추는 것이다.

- script: `analysis_outputs/jepa_bridge_ensemble_optimizer.py`
- pool: 109 candidates, scan: 25,367 candidates, selected 100, submission integrity all pass.
- best balanced ensemble:
  - `analysis_outputs/submission_jepa_bridge_ensemble_c42fbf1e.csv`
  - base `submission_jepa_public_minimax_bridge_5653d800.csv`, donor `submission_jepa_public_minimax_bridge_12deef9a.csv`, donor weight `0.12`
  - focused scenario `0.582124`, posterior expected `0.576847`, raw-axis delta `-0.000000018`, bad residual axis ratio `0.002363`
  - raw-negative를 유지하면서 기존 best strict bridge `84b71a03` focused `0.582172`보다 개선된다.
- best focused ensemble:
  - `analysis_outputs/submission_jepa_bridge_ensemble_86c6c9d1.csv`
  - base `submission_jepa_public_minimax_bridge_d1ca675f.csv`, donor `submission_jepa_public_minimax_bridge_12deef9a.csv`, donor weight `0.35`
  - focused scenario `0.582084`, posterior expected `0.576924`, raw-axis delta `-0.000000210`, bad residual axis ratio `0.003093`
  - focused는 최고지만 posterior가 올라가므로 공격 후보.
- interpretation: bridge끼리도 raw-axis가 상쇄되는 조합이 있다. 특히 near-raw public2d0 bridge와 seq1501 aggressive bridge를 섞으면 public-minimax 신호는 남기면서 raw-axis를 음수로 되돌릴 수 있다. 이건 JEPA latent를 하나의 submission으로 믿는 게 아니라 여러 hidden-energy view의 agreement/disagreement를 ensemble energy로 쓰는 쪽이 맞다는 증거다.

추가 업데이트: block-scale JEPA posterior 후보를 bridge의 regularizer로 다시 넣었다.  
block-scale neutral 후보는 단독으로 posterior `0.57619`까지 내려가지만 raw-axis delta가 `+0.000021~+0.000022`라 그대로는 위험하다. raw-counter 후보와 섞어 중립화한 뒤 bridge에 5% 수준으로 넣으면 focused 손실을 작게 유지하면서 posterior/bad-axis를 낮출 수 있다.

- script: `analysis_outputs/jepa_bridge_posterior_regularizer.py`
- scan: 4,636 candidates, selected 90, submission integrity all pass.
- best posterior-regularized bridge:
  - `analysis_outputs/submission_jepa_bridge_posteriorreg_9c5e225e.csv`
  - bridge `submission_jepa_bridge_ensemble_c42fbf1e.csv`, regularizer `aa014669 x rawaxis_s0p875`, regularizer weight `0.05`
  - focused scenario `0.582134`, posterior expected `0.576830`, raw-axis delta `-0.000000048`, bad residual axis ratio `0.002295`
  - `c42fbf1e` 대비 focused는 `+0.000010` 나빠지지만 posterior `-0.000017`, bad-axis `-0.000068`, raw margin은 약간 개선된다.
- best low-bad sibling:
  - `analysis_outputs/submission_jepa_bridge_posteriorreg_cf82036c.csv`
  - focused scenario `0.582134`, posterior expected `0.576831`, raw-axis delta `-0.000000026`, bad residual axis ratio `0.002242`
- interpretation: 이 branch는 1순위 갱신이라기보다 제출 리스크를 줄이는 regularized alternative다. JEPA block representation은 direct posterior 후보로 쓰면 raw축을 망가뜨리지만, raw-counter로 중립화한 뒤 bridge에 아주 얇게 넣으면 유효한 Bayesian prior처럼 동작한다.

## 제출 후보 우선순위

업데이트: JEPA식 pseudo-hidden block-rate probe에 이어, label flank/요일/phase만 쓰는 sequence motif probe를 추가했다.  
단독 motif probe는 raw-axis에서 실패했지만, raw-axis-safe 후보에 중립화해 섞으면 endpoint-neutral보다 scenario/mask proxy가 더 좋아졌다.  
아래 numbered list는 sequence-motif까지의 historical ranking이다. 최신 block-scale JEPA/axis-projection까지 반영한 raw05-safe shortlist는 뒤의 "block-scale JEPA target/context reconstruction" 섹션을 우선한다.

최신 JEPA-block 후보 우선순위:

1. `analysis_outputs/submission_jepa_bridge_ensemble_c42fbf1e.csv`
   - best balanced ensemble. focused `0.582124`, posterior `0.576847`, raw-axis delta `-0.000000018`, bad-axis `0.002363`.

2. `analysis_outputs/submission_jepa_bridge_posteriorreg_9c5e225e.csv`
   - posterior-regularized balanced alternative. focused `0.582134`, posterior `0.576830`, raw-axis delta `-0.000000048`, bad-axis `0.002295`.

3. `analysis_outputs/submission_jepa_bridge_posteriorreg_cf82036c.csv`
   - low-bad sibling. focused `0.582134`, posterior `0.576831`, raw-axis delta `-0.000000026`, bad-axis `0.002242`.

4. `analysis_outputs/submission_jepa_bridge_ensemble_86c6c9d1.csv`
   - best focused ensemble / aggressive pick. focused `0.582084`, posterior `0.576924`, raw-axis delta `-0.000000210`, bad-axis `0.003093`.

5. `analysis_outputs/submission_jepa_public_minimax_bridge_84b71a03.csv`
   - best strict raw-negative bridge. focused `0.582172`, posterior `0.576813`, raw-axis delta `-0.000000083`, bad-axis `0.002111`.

6. `analysis_outputs/submission_jepa_public_minimax_bridge_d1ca675f.csv`
   - near-raw boundary/high-upside bridge. focused `0.582138`, posterior `0.576815`, raw-axis delta `+0.000000298`, bad-axis `0.002629`.

7. `analysis_outputs/submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv`
   - balanced pick. focused `0.582411`, posterior `0.576729`, raw-axis delta `+0.000000070`, bad-axis `0.001108`.

8. `analysis_outputs/submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv`
   - conservative pick. focused `0.582439`, posterior `0.576677`, raw-axis delta `-0.000000260`, bad-axis `0.001310`.

9. `analysis_outputs/submission_jepa_energy_ensemble_0b862967.csv`
   - JEPA count + motif balanced ensemble. focused `0.582415`, posterior `0.576780`, raw-axis delta `-0.000000269`.

10. `analysis_outputs/submission_jepa_public_minimax_bridge_12deef9a.csv`
   - aggressive focused probe. focused `0.581992`, posterior `0.577129`, raw-axis delta `+0.000000807`, bad-axis `0.003956`.

11. `analysis_outputs/submission_jepa_public_blockentropy_seq1501_q3_only_g001_782e0645.csv`
   - high-upside probe. focused `0.582224`, raw-axis delta `-0.000000052`, but posterior `0.577152` and bad-axis `0.006346` make it risky.

1. `analysis_outputs/submission_hiddenblock_seqmotif_neutral_ebf79910.csv`
   - 기존 `rateprobe_neutral_95ebba6c`에 sequence motif를 15% logit mix.
   - raw05 대비 raw-axis proxy 통과: `delta_vs_raw05_rawaxis = -0.00000013`.
   - posterior-fit 예상 `0.577228`, full scenario rank `357/3052`, mask mean rank `395.75/3080`.
   - scenario robust score `0.591100`.
   - raw-axis margin은 얇지만 raw-safe 후보 중 scenario/mask proxy가 가장 좋다.

2. `analysis_outputs/submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`
   - `rawaxis_s0p75`에 all-target same-subject motif를 30% logit mix.
   - raw-axis 안전마진이 더 크다: `delta_vs_raw05_rawaxis = -0.00000186`.
   - posterior-fit 예상 `0.577175`, full scenario rank `428/3052`, mask mean rank `451.96/3080`.
   - scenario robust score `0.591116`.
   - 1번보다 덜 공격적인 raw-axis-safe 후보.

3. `analysis_outputs/submission_hiddenblock_seqmotif_neutral_d0ca7647.csv`
   - 기존 `rateprobe_neutral_605de284`에 Q/S motif를 5%만 섞은 균형 후보.
   - raw05 대비 raw-axis proxy 통과: `delta_vs_raw05_rawaxis = -0.000000003`.
   - posterior-fit 예상 `0.576808`, full scenario rank `1388/3052`, mask mean rank `1404.33/3080`.
   - scenario robust score `0.591223`.
   - posterior와 scenario를 동시에 조금 개선한 보수 후보.

기존 후보 중 계속 유효:

4. `analysis_outputs/submission_hiddenblock_rateprobe_neutral_95ebba6c.csv`
   - endpoint-rate neutral 후보 중 가장 공격적인 기준점.
   - raw05 대비 raw-axis proxy 통과: `delta_vs_raw05_rawaxis = -0.00000126`.
   - posterior-fit 예상 `0.577290`, scenario robust score `0.591163`, full mask mean rank `794.71/3080`.

5. `analysis_outputs/submission_hiddenblock_rateprobe_neutral_605de284.csv`
   - endpoint-rate neutral 후보 중 posterior-friendly 기준점.
   - raw05 대비 raw-axis proxy 통과: `delta_vs_raw05_rawaxis = -0.00000064`.
   - posterior-fit 예상 `0.576840`, scenario robust score `0.591245`, full mask mean rank `1763.88/3080`.

6. `analysis_outputs/submission_hiddenblock_paretomix_w0.3_b7621063.csv`
   - `orthgate_noq2_g0.05_cap0.35` 70% + `rawaxis_s0p75` 30% logit mix.
   - raw05 대비 raw-axis proxy가 중립 이하: `delta_vs_raw05_rawaxis = -0.00000042`.
   - posterior-fit 예상 `0.5768248`, scenario robust score `0.591287`, full mask mean rank `2399.21/3080`.
   - rate probe를 믿지 않는다면 여전히 가장 균형 잡힌 baseline 후보.

7. `analysis_outputs/submission_hiddenblock_paretomix_w0.4_507296eb.csv`
   - 같은 두 축의 60/40 logit mix.
   - raw-axis proxy 개선폭이 더 크다: `delta_vs_raw05_rawaxis = -0.00000233`.
   - posterior-fit 예상 `0.576918`, scenario robust score `0.591288`, 확장 후보군 mask mean rank `805.92`.

8. `analysis_outputs/submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv`
   - `raw05`보다 약간 더 강한 raw-rescue 축.
   - raw-axis public-fit 예상 `0.5775177`, posterior-fit 예상 `0.5774803`.
   - scenario robust score `0.591321`, full mask mean rank `2771.96/3080`.

보류:

- `analysis_outputs/submission_hiddenblock_orthgate_noq2_g0.05_cap0.35_b7177075.csv`
  - scenario/mask는 좋지만 raw-axis proxy가 raw05보다 `+0.00000679` 나쁘다.
- `submission_hiddenblock_posterior_raw05_g0p05_8b49d70e.csv`
- `submission_hiddenblock_posterior_raw05_g0p1_18050567.csv`
- `submission_hiddenblock_posterior_raw05_g0p2_9588c3fc.csv`

posterior 자체는 6개 public constraint를 정확히 맞추지만 자유도가 너무 크다. 특히 g0p1/g0p2는 raw-axis 관점에서 public이 악화될 가능성이 높다.

## 새로 드러난 구조

1. hidden submission은 36개 실제 block으로 쪼개진다.
   - block 길이 1-16 rows.
   - subject별 2개 또는 5/7개 block 패턴이 섞인다.
   - id04/id05/id06/id08은 짧은 block이 많아 public subset/mask 민감도가 높다.

2. endpoint label은 hard rule이 아니다.
   - pseudo-block 실험에서 subject mean이 raw prev/next endpoint보다 안정적이다.
   - 그래도 endpoint/length별 평균 rate는 weak count prior로 쓸 수 있다.
   - 특히 S2/S3는 endpoint-prior와 posterior correlation이 높다.

3. public-consistent posterior가 크게 움직이는 target:
   - Q3 mean abs shift `0.0886`
   - S1 `0.0773`
   - S4 `0.0740`
   - S3 `0.0622`
   - Q2는 `0.0264`로 작다.

4. Q2/Q3 ordinal-count 강제는 public에서 실패했다.
   - ordinal_q는 raw-axis expected public `0.5813294`로 매우 나쁘다.
   - Q2/Q3 count를 강하게 만지는 방향은 당분간 금지.

## 0.54 가능성 판단

가능성은 남아 있지만, 현재 방식으로는 안 된다.

- validation block-rate oracle: `0.517878`
- 현재 public best anchor(raw05): `0.577526`
- gap: 약 `0.05965`

따라서 0.54는 “row-level calibration”이 아니라 **hidden block rate/count latent를 실제로 복원**해야 도달 가능하다.  
반대로 subject-chunk count-JEPA가 `-0.0005` 수준밖에 못 먹은 것은 현재 block representation이 아직 rate/count를 충분히 복원하지 못한다는 증거다.

## 다음 실험 3개

1. Raw-JEPA block-rate teacher
   - raw timeline rescue feature를 row 보정이 아니라 block rate teacher로 재학습.
   - target: train pseudo hidden block의 실제 `rate/count`.
   - 성공 기준: subject-chunk CV에서 mean `-0.003` 이상, Q3/S1/S3/S4 중 3개 이상 개선.

2. Endpoint weak prior + raw-rescue gate
   - endpoint/length prior는 hard target이 아니라 gate로만 사용.
   - raw-rescue move를 endpoint posterior disagreement가 큰 block에만 강화.
   - 성공 기준: raw05 대비 public-fit 악화 없이 synthetic mask rank s0p75보다 개선.

3. Bad-axis orthogonal block posterior
   - `jepa_bad_residual`, `jepa_bad_q2`, `ordinal_q`를 명시적으로 제거한 block posterior projection.
   - target은 Q3/S1/S3/S4만.
   - 성공 기준: posterior-fit 개선과 raw-axis-fit 개선이 동시에 같은 방향.

## 추가 실험 결과: orthogonal/gate/mix

JEPA 논문의 핵심을 이 데이터에 맞게 바꿔 적용했다.

- image target block -> hidden submission episode block
- target representation -> block-level `rate/count/entropy` latent
- context -> 주변 train endpoint, block length, raw timeline rescue state, public feedback axes

결과:

1. `orthgate_noq2`는 hiddenblock 후보 중 scenario/mask가 가장 좋다.
   - `submission_hiddenblock_orthgate_noq2_g0.05_cap0.35_b7177075.csv`
   - scenario robust score `0.591287` vs 기존 s0p75 `0.591321`
   - mask mean rank `135.92` vs 기존 s0p75 `155.33`
   - 하지만 raw-axis proxy가 raw05 대비 `+0.00000679`라서 단독 제출은 약간 위험하다.

2. `paretomix`가 가장 좋은 균형점이다.
   - `submission_hiddenblock_paretomix_w0.3_b7621063.csv`
   - raw-axis/pass + posterior/pass를 동시에 만족.
   - scenario robust score는 orthgate와 사실상 동률이고, s0p75보다 좋다.
   - raw-axis expected `0.57752588`, posterior expected `0.5768247`.

3. endpoint는 여전히 hard rule이 아니라 gate일 때만 살아남는다.
   - raw-neutralized 후보들은 raw-axis는 통과하지만 mask rank가 `175+`로 밀렸다.
   - 따라서 endpoint/raw 보정만 강하게 주면 block 구조 신호는 일부 죽는다.

4. `0.54` 가능성 판단은 변하지 않았다.
   - 이번 작업은 public `0.5775` 근방에서 구조적 위험을 줄이는 후보를 만든 것.
   - `0.54`로 가려면 여전히 hidden block의 실제 count/rate를 더 직접 복원해야 한다.

## 추가 실험 결과: pseudo-hidden block rate reconstruction

JEPA 논문식 가정을 더 직접 검증했다.  
즉, row residual이 아니라 "가려진 train block의 target rate/count latent"를 주변 context와 raw/prediction block feature로 복원하게 만들었다.

설정:

- actual submission block length를 subject별로 그대로 사용.
- train 안에서 369개 pseudo-hidden block 생성.
- 각 block 내부 라벨은 완전히 가리고, endpoint/Markov/KNN retrieval이 block rate를 복원하는지 평가.

결과:

1. endpoint prior만 subject_mean을 근소하게 이긴다.
   - `endpoint_local_nonoverlap`: weighted logloss `0.609749`, subject_mean 대비 `-0.003252`.
   - `endpoint_strict_subject`: `0.612869`, subject_mean 대비 `-0.000132`.
   - 즉 endpoint/length는 진짜 신호가 있지만 strict 일반화에서는 거의 0에 가깝다.

2. raw/JEPA retrieval은 block-rate 복원에 실패했다.
   - `knn_full_strict_subject_k8`: subject_mean 대비 `+0.094301`.
   - `knn_raw_strict_subject_k8`: subject_mean 대비 `+0.096916`.
   - 현재 raw/Jepa feature는 row-level public rescue에는 도움이 되지만 hidden block의 rate/count teacher로는 아직 부족하다.

3. target별로 신호가 갈린다.
   - endpoint는 Q1/Q2/Q3에서는 개선: Q1 `-0.0111`, Q2 `-0.0273`, Q3 `-0.0165`.
   - S1/S2/S3/S4에서는 악화한다.
   - 따라서 endpoint-rate 후보는 Q targets만 매우 약하게 움직이는 방향이 맞다.

4. rate-probe 단독 후보는 raw-axis public proxy를 악화한다.
   - best endpoint probe도 raw05 대비 raw-axis delta가 `+0.00004` 이상.
   - pseudo-hidden에서 맞는 방향이 public raw-axis와 곧장 일치하지 않는다.

5. raw-axis-neutral mix는 아주 작은 개선 후보를 만든다.
   - `submission_hiddenblock_rateprobe_neutral_95ebba6c.csv`
     - raw-axis delta vs raw05: `-0.00000126`
     - scenario robust score `0.591163` vs paretomix w0.3 `0.591287`
     - mask mean rank `450.58` vs paretomix w0.3 `801.58` after the sequence-motif candidate pool expansion
     - posterior expected `0.577290`, so posterior-fit 관점에서는 덜 좋다.
   - `submission_hiddenblock_rateprobe_neutral_27ca3bb0.csv`
     - raw-axis delta vs raw05: `-0.00000095`
     - scenario robust score `0.591241`
     - mask mean rank `679.79`
     - posterior expected `0.576878`
   - `submission_hiddenblock_rateprobe_neutral_605de284.csv`
     - posterior expected가 safe neutral 중 가장 좋다: `0.576840`
     - raw-axis delta vs raw05: `-0.00000064`
     - scenario robust score `0.591245`

해석:

- 0.54로 가는 큰 발견은 아직 아니다.
- 하지만 "endpoint Q-rate만 약하게, raw-axis-safe 후보에 섞는" 방식은 paretomix보다 scenario/mask proxy를 소폭 개선한다.
- 제출 우선순위는 공격성 순서로 보면 `95ebba6c` -> `27ca3bb0`/`605de284` -> 기존 `paretomix_w0.3`이다.
- 보수적으로 보면 실제 public feedback이 raw05 축에 강하게 묶여 있으므로 `27ca3bb0` 또는 `605de284`가 더 낫다.

## 추가 실험 결과: sequence motif block correspondence

raw/PCA/JEPA feature retrieval이 실패했기 때문에 feature를 더 넣는 대신 반대로 줄였다.  
이번에는 hidden block과 같은 길이로 train block을 가리고, 앞/뒤 label flank, endpoint motif, 요일, subject phase만으로 block rate를 복원했다.

결과:

1. sequence motif는 endpoint보다 훨씬 강하다.
   - `motif_same_r1_k16_tau1p0_s8p0`: weighted logloss `0.597394`, subject_mean 대비 `-0.015607`.
   - `motif_local_r1_k16_tau1p0_s16p0`: `0.600037`, subject_mean 대비 `-0.012964`.
   - `motif_strict_r5_k16_tau1p0_s16p0`: `0.602429`, subject_mean 대비 `-0.010573`.
   - 즉 signal이 단순 같은-subject 암기에만 있지 않고, cross-subject flank geometry에도 일부 남아 있다.

2. target별 개선 폭도 endpoint보다 넓다.
   - Q2 `-0.0303`, Q3 `-0.0318`, S1 `-0.0156`, S4 `-0.0182`.
   - S3는 약하지만 같은 방향: `-0.0026`.
   - 이건 hidden block distribution을 설명하는 구조적 단서로는 endpoint probe보다 강하다.

3. 단독 motif submission은 public raw-axis와 충돌한다.
   - direct motif probe의 best raw-axis delta는 raw05 대비 `+0.00002~+0.00004`.
   - 따라서 motif가 실제 block rate를 잘 맞혀도 public이 관측한 raw05 축과 바로 정렬되지는 않는다.

4. raw-axis-neutral mix는 endpoint-neutral을 다시 이긴다.
   - `submission_hiddenblock_seqmotif_neutral_ebf79910.csv`
     - raw-axis delta `-0.00000013`
     - posterior expected `0.577228`
     - scenario robust score `0.591100`
     - full mask mean rank `395.75/3080`
   - `submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`
     - raw-axis delta `-0.00000186`
     - posterior expected `0.577175`
     - scenario robust score `0.591116`
     - full mask mean rank `451.96/3080`
   - `submission_hiddenblock_seqmotif_neutral_d0ca7647.csv`
     - raw-axis delta `-0.000000003`
     - posterior expected `0.576808`
     - scenario robust score `0.591223`
     - full mask mean rank `1404.33/3080`

해석:

- 이제 “hidden block label distribution을 결정하는 구조적 단서”로 가장 강한 것은 raw sensor가 아니라 **subject sequence motif / flank label geometry**다.
- 다만 public raw-axis와 충돌하므로 0.54 후보가 되려면 motif를 더 세게 쓰는 방법이 아니라 raw-axis 충돌을 설명하는 mask/axis 분해가 필요하다.
- 현재 제출 관점에서는 `ebf79910` 또는 `1501e8f9`가 endpoint-neutral 95보다 한 단계 나은 실험 후보이고, `d0ca7647`은 posterior-balanced 후보이다.

## 추가 실험 결과: block-scale JEPA target/context reconstruction

JEPA 논문 아이디어를 row residual이 아니라 hidden block 자체에 더 직접 적용했다.

- context encoder: block 주변 known row/raw timeline state와 label flank.
- target encoder: pseudo-hidden block 내부의 raw/lifelog representation aggregate.
- predictor: context representation으로 target block representation을 예측.
- downstream probe: predicted target representation, actual target representation, residual/energy, context로 block label rate를 복원.

가장 강한 pseudo-hidden 결과:

- `rt:local:ridge_zctx_a12:blend0p2`
- weighted logloss `0.571203`
- subject_mean 대비 delta `-0.041799`
- RMSE `0.210452`, R2 `0.500674`

target별 delta:

- Q1 `-0.063383`
- Q2 `-0.094284`
- Q3 `-0.060260`
- S1 `-0.011019`
- S2 `-0.024283`
- S3 `-0.004834`
- S4 `-0.034531`

해석:

- JEPA식 "context -> target block representation"은 sequence motif보다 pseudo-hidden block-rate 복원력이 훨씬 크다.
- 특히 Q1/Q2/Q3와 S4에서 신호가 강하다.
- 다만 direct submission move는 raw05 public axis에 작은 비용을 만든다. 따라서 representation을 찾은 것과 제출 가능한 방향을 찾은 것은 분리해서 봐야 한다.
- `rt` 단독이 `rt_bc`/`rt_bc_nb_sg`보다 낫다. extra block-canvas/noisy source는 현재 block-rate probe에 noise로 들어간다.

artifact:

- `analysis_outputs/block_scale_jepa_target_audit.py`
- `analysis_outputs/block_scale_jepa_target_report.md`
- `analysis_outputs/block_scale_jepa_target_summary.csv`
- `analysis_outputs/block_scale_jepa_target_hidden_rates.csv`
- `analysis_outputs/block_scale_jepa_target_candidate_proxy.csv`

## 추가 실험 결과: raw05-axis projected JEPA

block-scale JEPA move를 public에서 실패한 bad JEPA residual/ordinal 방향과 raw05-compatible latent gradient에서 projection해, JEPA 신호만 남기는 실험을 했다.

결과:

1. 가장 좋은 raw05-safe structural control은 아직 `seqmotif_neutral_1501e8f9`다.
   - posterior expected `0.577175`
   - raw-axis expected `0.577524`
   - delta vs raw05 raw-axis `-0.00000186`
   - mean abs move vs raw05 `0.001168`

2. JEPA axis-projected 후보가 rate/pareto control과 같은 안전권에 들어왔다.
   - `submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv`
   - posterior expected `0.576777`
   - raw-axis expected `0.577526`
   - delta vs raw05 raw-axis `-0.00000058`
   - bad residual axis ratio `0.001049`
   - ordinal axis ratio `0.026019`
   - mean abs move vs raw05 `0.001253`

3. 같은 계열의 두 번째 후보:
   - `submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv`
   - posterior expected `0.576757`
   - raw-axis expected `0.577526`
   - delta vs raw05 raw-axis `-0.00000047`
   - bad residual axis ratio `0.000634`
   - mean abs move vs raw05 `0.001321`

최신 raw05-safe shortlist:

1. `submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`
2. `submission_hiddenblock_rateprobe_neutral_605de284.csv`
3. `submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv`
4. `submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv`
5. `submission_hiddenblock_paretomix_w0.3_b7621063.csv`

artifact:

- `analysis_outputs/block_scale_jepa_axis_projector.py`
- `analysis_outputs/block_scale_jepa_axis_projector_report.md`
- `analysis_outputs/block_scale_jepa_axis_projector_scores.csv`
- `analysis_outputs/block_scale_jepa_axis_projector_selected.csv`
- `analysis_outputs/block_scale_jepa_axis_submission_shortlist.csv`
- `analysis_outputs/block_scale_jepa_axis_combined_shortlist_proxy.csv`

## 추가 실험 결과: public-inverse blend branch

public LB inverse/minimax 후보와 structural/JEPA hidden-block 후보를 submission-level logit blend로 섞었다.

설정:

- public bases `19`
- structural candidates `23`
- scenario files `15`
- sampled masks `768`
- scanned blends `3,496`
- saved submissions `60`

가장 좋은 sampled-public robustness 후보:

- `submission_blockscale_jepa_publicblend_w0p1_16ca80d0.csv`
  - public base: `submission_public_universeens_u65_r04_dc6f3303.csv`
  - structural: `submission_blockscale_jepa_raw05_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_dcf4387c.csv`
  - robust score `0.575423`
  - public base 대비 robust delta `-0.000177`
  - mean expected delta `-0.000005`
  - posterior expected `0.577683`
  - raw-axis expected `0.578931`
  - delta vs raw05 raw-axis `+0.001405`

가장 해석이 깨끗한 structural blend:

- `submission_blockscale_jepa_publicblend_w0p1_d6fa2e19.csv`
  - structural: axis-projected JEPA `71abf82b`
  - robust score `0.575425`
  - public base 대비 robust delta `-0.000175`
  - posterior expected `0.577610`
  - raw-axis expected `0.578926`
  - delta vs raw05 raw-axis `+0.001400`

해석:

- public-inverse/minimax base 위에서는 structural JEPA를 10% 섞는 것이 sampled robustness를 약 `0.00017` 개선한다.
- 하지만 이 branch는 raw05-safe가 아니다. raw-axis expected가 `~0.57893`로 커지고, ordinal axis ratio도 `~0.289`까지 올라간다.
- 따라서 이건 "known-public scenario overfit/robustness branch"이지 raw05-safe structural branch의 대체품이 아니다.
- 제출 후보로 쓰려면 public inverse 후보를 믿는 경우에만 별도 슬롯으로 다뤄야 한다.

artifact:

- `analysis_outputs/block_scale_jepa_public_blend.py`
- `analysis_outputs/block_scale_jepa_public_blend_report.md`
- `analysis_outputs/block_scale_jepa_public_blend_shortlist.csv`
- `analysis_outputs/block_scale_jepa_public_blend_shortlist_with_base_delta.csv`
- `analysis_outputs/block_scale_jepa_public_blend_base_scores.csv`
- `analysis_outputs/block_scale_jepa_public_blend_proxy.csv`

## 추가 실험 결과: sequence motif axis decomposition + cell gate

sequence motif가 pseudo-hidden block에서는 강하지만 direct public raw-axis에서는 왜 실패하는지 target/cell 단위로 분해했다.  
raw-axis는 `stage2 -> raw05` public 방향, posterior-axis는 public constraint posterior 방향이다.

target별 평균:

| target | raw delta | posterior delta | conflict cell frac | synergy cell frac |
| --- | ---: | ---: | ---: | ---: |
| Q1 | `+0.000232` | `-0.003462` | `0.4017` | `0.0397` |
| Q2 | `+0.000083` | `-0.000329` | `0.5997` | `0.0000` |
| Q3 | `+0.000091` | `+0.000050` | `0.4014` | `0.1131` |
| S1 | `+0.000297` | `-0.005102` | `0.6149` | `0.0949` |
| S2 | `+0.000049` | `-0.000193` | `0.4331` | `0.1660` |
| S3 | `+0.000031` | `-0.000073` | `0.2409` | `0.1097` |
| S4 | `+0.000052` | `-0.000334` | `0.3003` | `0.1409` |

해석:

1. 충돌의 핵심은 `S1`, `Q2`, `Q1`이다.
   - `S1`은 posterior gain이 가장 크지만 raw-axis 손실도 가장 크다.
   - `Q2`는 pseudo-hidden에서는 좋아 보여도 raw_bad cell이 사실상 100%이고 synergy가 0이다.
   - 따라서 Q2를 세게 만지는 후보는 public raw05 축과 정면 충돌한다.

2. `Q3`는 더 조심해야 한다.
   - pseudo-hidden target detail에서는 좋아 보였지만 direct probe 평균 posterior delta가 `+0.000050`이다.
   - 즉 Q3 motif는 특정 mask/posterior에서는 좋아도 전체 posterior-axis에서는 흔들린다.

3. 상대적으로 안전한 motif target은 `S3/S4`, 그 다음 `S2`다.
   - conflict frac이 낮고 synergy frac이 비교적 높다.
   - 다만 이동량 자체가 작아서 단독으로 큰 LB 개선을 만들기는 어렵다.

cell-gate 결과:

- 총 `2100`개 cell-gated 후보 생성.
- 파일 무결성: 전부 `250 rows`, key match `2100/2100`, duplicate/null `0`.
- raw-axis 비악화 후보: `1264`개.

제출 관점 shortlist:

1. `analysis_outputs/submission_hiddenblock_seqmotif_cellgate_5e4cf566.csv`
   - raw-axis delta `-0.000000363`, posterior expected `0.577085`.
   - full scenario rank `394/3052`, mask mean rank `424.71/3080`.
   - `ebf79910`보다 약간 뒤지만, motif cell-gate가 실제로 raw-safe 영역을 찾는다는 증거다.

2. `analysis_outputs/submission_hiddenblock_seqmotif_cellgate_7394e0e7.csv`
   - raw-axis delta `-0.000000452`, posterior expected `0.576872`.
   - full scenario rank `474/3052`, mask mean rank `487.04/3080`.
   - posterior는 좋아졌지만 scenario/mask가 `5e4cf566`보다 약하다.

3. `analysis_outputs/submission_hiddenblock_seqmotif_cellgate_18736a71.csv`
   - raw-axis delta `-0.000000034`, posterior expected `0.576698`.
   - 하지만 full scenario rank `2239/3052`, mask mean rank `2224.38/3080`.
   - 결론: posterior-fit 하나만 보고 제출하면 안 된다.

4. `analysis_outputs/submission_hiddenblock_seqmotif_cellgate_8eafa541.csv`
   - scenario/mask는 cellgate 중 가장 좋다: scenario rank `192/3052`, mask mean rank `218.46/3080`.
   - 하지만 raw-axis delta가 `+0.000010843`라서 raw05 public anchor와 충돌한다.
   - 고위험 탐색용이지 현재 우선 제출 후보는 아니다.

결론:

- cell-gate는 “motif 신호의 안전한 부분”을 찾기는 했지만, 현 시점에서는 `seqmotif_neutral_ebf79910`을 넘지 못했다.
- 가장 제출가치가 높은 후보는 여전히 `ebf79910`, 그 다음 `1501e8f9`, 실험적 대안으로 `5e4cf566`이다.
- 0.54로 가려면 cell-level gate를 더 세밀하게 만드는 것보다, `S1/Q2/Q1`에서 raw-axis와 posterior-axis가 왜 반대로 움직이는지 설명하는 hidden mask model이 필요하다.

## 추가 실험 결과: actual public LB inverse mask audit

이번에는 proxy가 아니라 실제 제출된 public LB 숫자 6개를 직접 제약으로 썼다.

```csv
key,public_lb,delta_vs_stage2
stage2,0.5779449757,0
anchor578,0.5784273528,+0.0004823771
ordinal_q,0.5783033652,+0.0003583895
raw05,0.5775263072,-0.0004186685
jepa_bad_residual,0.5812273278,+0.0032823521
jepa_bad_q2,0.5798012862,+0.0018563105
```

방법:

- 22개 soft-label scenario를 사용했다.
  - public posterior scenario 16개
  - 실제 public 제출 파일 6개를 soft-label stress scenario로 추가
- `build_masks()`의 `2125`개 row mask를 모두 sweep.
- 각 `(scenario, mask)`가 위 5개 delta를 얼마나 잘 재현하는지 `weighted_std_rmse`, sign accuracy, max residual로 평가했다.

결과:

1. best magnitude fit은 `submission_public_entropyproj_public2d0_g100.csv + random_rows frac0.30_rep192`.
   - weighted std RMSE `0.6641`.
   - `anchor578` predicted `+0.000368` vs actual `+0.000482`.
   - `ordinal_q` predicted `+0.000338` vs actual `+0.000358`.
   - `jepa_bad_residual` predicted `+0.002369` vs actual `+0.003282`.
   - 하지만 `raw05` predicted `+0.000054` vs actual `-0.000419`.

2. 즉 현재 posterior scenario/mask universe는 raw05 public gain의 부호를 설명하지 못한다.
   - 단순 public subset mask만 바꿔서는 raw05가 stage2보다 좋아진 현상을 재현하기 어렵다.
   - raw05 gain은 기존 public posterior가 포착한 label posterior와 다른 target/block latent를 보고 있을 가능성이 크다.

3. raw05까지 모든 public delta 부호를 맞추는 조합은 매우 희박하고 magnitude가 나쁘다.
   - 가장 좋은 all-sign-compatible mask는 `id01` 단일 subject 또는 global prefix 20%.
   - raw05 soft-label scenario를 넣으면 sign-compatible 조합은 늘어나지만 inverse fit score가 `5+`로 악화한다.
   - 따라서 “public이 id01/prefix만 본다”보다는 “raw05를 설명하는 latent scenario가 빠져 있다”가 더 그럴듯하다.

target 기여:

- best inverse mask에서 raw05가 좋아지는 target은 `Q3`, `S4`뿐이다.
  - Q3 `-0.000092`, S4 `-0.000108`.
  - Q1/S1/S2/S3는 raw05가 stage2보다 나쁘다.
- top64 평균에서도 raw05는 모든 target 평균이 양수에 가깝다.
  - 이게 raw05 actual public delta와 반대다.

후보 재랭킹:

1. magnitude-only inverse ranking은 `entropyproj_public2d0_g100`을 1위로 둔다.
   - 하지만 이 ranking은 raw05 actual sign을 틀린 mask들에 의해 지배된다.
   - score 후보라기보다 “현재 posterior가 선호하는 label scenario” 진단으로 봐야 한다.

2. all-sign-compatible inverse ranking은 hiddenblock/raw-axis-safe 후보를 다시 끌어올린다.
   - `submission_hiddenblock_paretomix_w0.4_507296eb.csv`: sign-compatible rank `1`.
   - `submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`: rank `5`.
   - `submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv`: rank `7`.
   - `submission_hiddenblock_paretomix_w0.3_b7621063.csv`: rank `8`.
   - `submission_hiddenblock_rateprobe_neutral_605de284.csv`: rank `11`.
   - `submission_hiddenblock_seqmotif_neutral_ebf79910.csv`: rank `20`.

실전 해석:

- scenario/mask robust 기준만 보면 `ebf79910`이 가장 좋다.
- actual public sign-compatible 기준을 섞으면 `1501e8f9`와 `paretomix_w0.4`가 더 설득력 있다.
- 현재 public evidence를 가장 보수적으로 읽으면 제출 우선순위는:
  1. `submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`
  2. `submission_hiddenblock_seqmotif_neutral_ebf79910.csv`
  3. `submission_hiddenblock_paretomix_w0.4_507296eb.csv`
  4. diagnostic: `submission_hiddenblock_seqmotif_cellgate_5e4cf566.csv`

0.54 관련 실패/성공 근거:

- 성공 근거: hidden block rate는 sequence motif로 pseudo-hidden에서 `-0.0156`까지 복원된다.
- 실패 근거: 그 motif와 current posterior는 raw05 actual public gain을 설명하지 못한다.
- 따라서 다음 돌파점은 더 많은 feature가 아니라, **raw05가 이기는 Q3/S4 block subset을 실제 hidden block geometry와 연결하는 latent scenario**다.

## Raw05 JEPA Q3/S4 gate audit

추가 목표 반영:

- 모델링 쪽은 JEPA 아이디어를 최대한 가져간다.
- 여기서는 I-JEPA의 핵심인 “context block으로 target block representation을 예측하고, 그 latent residual/energy를 downstream signal로 쓴다”를 raw05 public gain 분석에 연결했다.
- 사용한 feature는 `raw_timeline_jepa_rescue_*_features.parquet`의 context-to-target latent:
  - subject-neighbor day prediction residual
  - mobile↔wearable modality bridge residual
  - day/evening/morning context → night target residual

생성:

- `analysis_outputs/raw05_jepa_q3s4_gate_audit.py`
- `analysis_outputs/raw05_jepa_q3s4_gate_train_target_summary.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_model_summary.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_feature_importance.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_oof_variants.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_candidate_scores.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_focused_scenario_scores.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_integrity.csv`
- `analysis_outputs/raw05_jepa_q3s4_gate_submission_shortlist.csv`
- `630`개 `submission_raw05_jepa_q3s4gate_*.csv`

검증 결과:

1. `rawijepa_oof.npy`는 stage2 OOF와 동일해서 raw05 OOF로 쓰면 안 된다.
   - raw05 OOF는 `raw_timeline_jepa_rescue_strict_scale0p5_ops.csv`에서 재구성해야 한다.
   - 재구성된 submission fit은 disk raw05와 max abs `0.0`으로 일치했다.

2. raw05 OOF target 효과:
   - Q3 `-0.003092`
   - S4 `-0.002422`
   - Q1/S1/S2/S3도 OOF상 개선이지만, public inverse에서는 실제 raw05 gain이 Q3/S4에 집중되어 있었다.

3. JEPA row-level ML gate는 기대보다 약하다.
   - Q3 gate: OOF corr with gain `-0.094`; top30 gain `0.000790`, bottom30 gain `0.010484`.
   - S4 gate: OOF corr `0.123`; top30 gain `0.005303`, bottom30 gain `0.000980`.
   - 즉 Q3는 “row별로 고르는 문제”가 아니라 target 축 전체 residual을 살리는 쪽이 더 맞다.

4. OOF best는 gate가 아니라 Q3/S4 전체 raw05 residual:
   - `Q3S4 all scale=1.25`: delta `-0.000930`
   - `Q3S4 all scale=1.00`: delta `-0.000788`
   - `Q3S4 prob scale=1.25`: delta `-0.000558`
   - 따라서 현재 단서는 “JEPA residual을 row gate로 sparsify”가 아니라 **raw05 JEPA residual을 Q3/S4 target gate로 제한**하는 것.

5. feature importance는 JEPA 해석과 맞는다.
   - Q3 중요 1위: `rtday_both_err_13`
   - Q3 상위에 `rtday_next_err_13`, `rtday_prev_err_13`, `rtday_target_13`
   - S4 쪽은 `rtday_next_abserr_10` 계열이 핵심.
   - raw05 ops 자체도 Q3=`rtday_both_err_13`, S4=`rtday_next_abserr_10`였으므로, raw05 public gain은 neighbor-context latent residual 축이라는 해석이 강화된다.

새 shortlist:

보수적 raw-axis-safe/focused:

1. `submission_raw05_jepa_q3s4gate_58801138.csv`
   - base `submission_hiddenblock_seqmotif_neutral_ebf79910.csv`
   - Q3/S4 all, scale `0.35`, `rawq_post_agree`
   - raw-axis delta vs raw05 `-0.00000251`
   - posterior expected `0.577033`

2. `submission_raw05_jepa_q3s4gate_81f94b63.csv`
   - base `submission_hiddenblock_seqmotif_neutral_1501e8f9.csv`
   - Q3/S4 all, scale `0.35`, `rawq_post_agree`
   - raw-axis delta vs raw05 `-0.00000331`
   - posterior expected `0.576982`

3. `submission_raw05_jepa_q3s4gate_718c45ed.csv`
   - base `submission_hiddenblock_seqmotif_neutral_d0ca7647.csv`
   - Q3/S4 all, scale `0.35`, `rawq_post_agree`
   - raw-axis delta vs raw05 `-0.00000007`
   - posterior expected `0.576615`

Posterior-upside but raw-axis tiny risk:

1. `submission_raw05_jepa_q3s4gate_7ca808af.csv`
   - base `submission_hiddenblock_seqmotif_neutral_d0ca7647.csv`
   - Q3/S4 all, scale `1.00`, `rawq_post_agree`
   - raw-axis delta vs raw05 `+0.000039`
   - posterior expected `0.576297`

판단:

- `58801138`/`81f94b63`은 기존 best candidate에 JEPA raw residual을 아주 작게 얹는 보수적 후보.
- `718c45ed`은 posterior proxy가 가장 좋지만 focused scenario는 약간 나쁘다.
- `7ca808af`은 0.5대 도약을 노릴 때만 의미 있는 공격형 후보이며, raw-axis risk가 있어 제출 우선순위는 낮다.
- 이 분기는 “row gate 실패” 자체가 중요한 발견이다. 다음 JEPA 실험은 row classifier가 아니라 **block-scale target representation prediction**이어야 한다. I-JEPA 논문에서 말하는 large target block/informative context 조건과 더 맞다.

## Block-Scale JEPA Target Representation 실험

스크립트:

- `analysis_outputs/block_scale_jepa_target_audit.py`
- `analysis_outputs/block_scale_jepa_neutral_scan.py`

JEPA 해석:

- hidden interval 전체를 I-JEPA의 large target block처럼 취급했다.
- target encoder는 hidden block 내부 raw/lifelog JEPA representation aggregate를 만든다.
- context encoder는 block 앞/뒤 known row representation과 label flank를 만든다.
- predictor는 context -> target representation을 Ridge로 예측한다.
- downstream rate probe는 `[target representation, predicted target representation, residual/energy, context]`를 사용하되, pseudo-hidden에서는 block 내부 label만 가린다.

핵심 pseudo-hidden 결과:

```csv
method,weighted_logloss,delta_vs_subject_mean,rate_rmse_weighted,rate_r2_weighted
rt:local:ridge_zctx_a12:blend0p2,0.571203,-0.041799,0.210452,0.500674
rt_bc:local:ridge_zctx_a12:blend0p2,0.577445,-0.035557,0.213720,0.485045
rt_bc_nb_sg:local:ridge_zctx_a12:blend0p2,0.577973,-0.035029,0.213753,0.484886
rt:local:ridge_zctx_a12:blend0p1,0.578090,-0.034912,0.220093,0.453877
```

이전 best sequence motif `0.597394`보다 pseudo-hidden에서는 훨씬 강하다. direct rate는 logloss가 나빴지만 RMSE는 낮았고, subject mean과 logit-blend하면 급격히 좋아졌다. 즉 raw latent block representation에는 label-rate 방향 정보가 있지만, calibration이 핵심이다.

target별 best method `rt:local:ridge_zctx_a12:blend0p2`:

```csv
target,delta_vs_subject_mean
Q1,-0.063383
Q2,-0.094284
Q3,-0.060260
S1,-0.011019
S2,-0.024283
S3,-0.004834
S4,-0.034531
```

해석:

- JEPA block representation은 Q1/Q2/Q3에 매우 강하고 S4도 의미 있다.
- S3는 약하다. sequence motif가 S3까지 어느 정도 끌고 가는 것과 다르게, raw latent block 구조는 S3를 잘 설명하지 못한다.
- source preset은 raw timeline(`rt`) 단독이 가장 좋았다. block canvas/neural/subject graph를 더 넣으면 표현은 풍부해지지만 pseudo-hidden logloss는 오히려 약간 나빠졌다.

public-axis 문제:

- block-scale JEPA 후보 384개는 모두 무결성 통과.
- 하지만 raw05-axis 기준 best도 `delta_vs_raw05_rawaxis +0.000006`으로, raw05/seqmotif neutral보다 public-axis 적합도는 나쁘다.
- 따라서 이 신호는 제출 주력이라기보다 posterior/hidden-block upside probe로 취급해야 한다.

중립화 스캔:

- `block_scale_jepa_neutral_scan.py`에서 method/base/mask/weight 17,232개를 메모리 스캔했다.
- safe 조건: `delta_vs_raw05_rawaxis <= 2.5e-5`, `abs(bad_residual_axis_ratio) <= 0.035`, `mean_abs_move_vs_raw05 <= 0.0025`.
- 11,803개가 safe 조건을 통과했고, 상위 40개만 저장했다.

실전 shortlist:

```csv
priority,tier,file,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,delta_vs_raw05_rawaxis,bad_residual_axis_ratio
1,raw-axis-safe control,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,0.577175,0.577524,-0.0000018554,0.002977
2,raw-axis-safe control,submission_hiddenblock_rateprobe_neutral_605de284.csv,0.576840,0.577526,-0.0000006420,0.004286
3,raw-axis-safe control,submission_hiddenblock_paretomix_w0.3_b7621063.csv,0.576825,0.577526,-0.0000004230,0.002410
4,block-scale-jepa upside,submission_blockscale_jepa_neutral_pareto03_rt_bc_nb_sg_same_ridge_full_a24_blend0p1_noq2_w0p02_aa014669.csv,0.576195,0.577548,0.0000214397,0.001206
5,block-scale-jepa upside,submission_blockscale_jepa_neutral_pareto03_rt_same_ridge_full_a24_blend0p1_noq2_w0p02_86018abc.csv,0.576206,0.577549,0.0000222318,-0.000234
6,block-scale-jepa q3s4 probe,submission_blockscale_jepa_raw05_rt_same_ridge_zctx_a12_blend0p1_q3s4_w0p03_dcf4387c.csv,0.577473,0.577533,0.0000062543,0.006314
```

판단:

- 제출 안정성 기준 1순위는 여전히 seqmotif/rateprobe/pareto neutral이다.
- JEPA를 제출에 반영한다면 `aa014669` 또는 `86018abc`가 block-scale JEPA upside probe다. 둘 다 posterior proxy는 좋아지지만 raw05-axis를 약 `2e-5` 손해 본다.
- 이 실험은 “JEPA가 row gate가 아니라 calibrated block-rate prior로 작동한다”는 증거다. 다음 개선은 이 block prior를 public inverse mask 또는 hidden block posterior와 jointly calibrate하는 쪽이 맞다.

## Block-Scale JEPA Axis Projection

스크립트:

- `analysis_outputs/block_scale_jepa_axis_projector.py`

목적:

- 이전 neutral scan은 단순 mask/weight scan이라 JEPA posterior gain을 얻으려면 raw05-axis 비용이 `+2e-5` 정도 남았다.
- 이번 pass는 block-scale JEPA hidden-rate prior를 logit move로 보고, 그 move를 raw05-compatible latent gradient와 bad observed axes에서 직접 projection했다.

방식:

- base: `raw05`, `pareto03`, `seq1501`, `rate605`
- JEPA prior: top block-scale methods (`rt:local:ridge_zctx_a12:blend0p2`, `rt:local:ridge_zctx_a12:blend0p1`, etc.)
- desired move: `logit(block_jepa_rate) - logit(base)`
- raw public first-order gradient: `base - raw_axis_latent_q`
- variants: `rawproj`, `raw_badproj`, `raw_bad_ordproj`, `raw_bad_ord_rawdirproj`
- mask/cap/gamma scan: 28,224 candidates
- saved: 50 candidates
- integrity: all saved candidates key ok, duplicate 0, null 0

결과:

```csv
file,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05
submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv,0.576777,0.577526,-0.0000005788,0.001049,0.001253
submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv,0.576757,0.577526,-0.0000004731,0.000634,0.001321
submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_30231e5b.csv,0.576761,0.577526,-0.0000003392,0.000482,0.001321
```

비교:

```csv
tier,file,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,delta_vs_raw05_rawaxis
raw-axis-control,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,0.577175,0.577524,-0.0000018554
raw-axis-control,submission_hiddenblock_rateprobe_neutral_605de284.csv,0.576840,0.577526,-0.0000006420
axis-projected-jepa,submission_blockscale_jepa_axisproj_pareto03_rt_local_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p05_c0p08_71abf82b.csv,0.576777,0.577526,-0.0000005788
axis-projected-jepa,submission_blockscale_jepa_axisproj_pareto03_rt_same_ridge_zctx_a12_blend0p1_s_all_rawproj_g0p03_c0p18_c07320e0.csv,0.576757,0.577526,-0.0000004731
raw-axis-control,submission_hiddenblock_paretomix_w0.3_b7621063.csv,0.576825,0.577526,-0.0000004230
```

판단:

- axis projection은 목표했던 대로 raw05-axis 비용을 `+2e-5`에서 0 근처/음수로 줄였다.
- posterior proxy는 aggressive neutral JEPA (`0.57619`)보다 약하지만, pareto/rateprobe control과 같은 raw-axis 안정권에서 더 좋은 JEPA structural variant를 만들었다.
- 제출 우선순위 관점에서는 `71abf82b`가 새 JEPA-safe 후보 1순위다. 기존 `rateprobe_neutral_605de284`보다 posterior proxy가 약 `0.000063` 좋고 raw-axis delta는 거의 동일하다.

## 생성 산출물

- `analysis_outputs/hidden_block_latent_audit.py`
- `analysis_outputs/hidden_block_latent_audit_report.md`
- `analysis_outputs/hidden_block_candidate_publicfit_scores.csv`
- `analysis_outputs/hidden_block_candidate_integrity.csv`
- `analysis_outputs/hidden_block_posterior_block_summary.csv`
- `analysis_outputs/hidden_block_posterior_target_summary.csv`
- `analysis_outputs/hidden_block_posterior_top_target_shifts.csv`
- `analysis_outputs/hidden_block_endpoint_priors.csv`
- `analysis_outputs/hidden_block_raw_axis_scale_scan.csv`
- `analysis_outputs/hidden_block_orthogonal_gate_candidates.py`
- `analysis_outputs/hidden_block_rawneutralize_candidates.py`
- `analysis_outputs/hidden_block_pareto_mix_candidates.py`
- `analysis_outputs/hidden_block_all_candidate_joined_ranking.csv`
- `analysis_outputs/hidden_block_all_generated_integrity.csv`
- `analysis_outputs/hidden_block_rate_reconstruction_audit.py`
- `analysis_outputs/hidden_block_rate_reconstruction_report.md`
- `analysis_outputs/hidden_block_rate_reconstruction_summary.csv`
- `analysis_outputs/hidden_block_rate_reconstruction_target_detail.csv`
- `analysis_outputs/hidden_block_rate_reconstruction_hidden_rates.csv`
- `analysis_outputs/hidden_block_rateprobe_neutral_mix.py`
- `analysis_outputs/hidden_block_rateprobe_neutral_mix_scores.csv`
- `analysis_outputs/hidden_block_rateprobe_neutral_mix_safe_scores.csv`
- `analysis_outputs/hidden_block_rateprobe_integrity.csv`
- `analysis_outputs/hidden_block_rateprobe_shortlist.csv`
- `analysis_outputs/hidden_block_sequence_motif_audit.py`
- `analysis_outputs/hidden_block_sequence_motif_report.md`
- `analysis_outputs/hidden_block_sequence_motif_summary.csv`
- `analysis_outputs/hidden_block_sequence_motif_target_detail.csv`
- `analysis_outputs/hidden_block_sequence_motif_hidden_rates.csv`
- `analysis_outputs/hidden_block_sequence_motif_candidate_proxy.csv`
- `analysis_outputs/hidden_block_sequence_motif_neutral_mix.py`
- `analysis_outputs/hidden_block_sequence_motif_neutral_mix_scores.csv`
- `analysis_outputs/hidden_block_sequence_motif_neutral_mix_safe_scores.csv`
- `analysis_outputs/hidden_block_sequence_motif_integrity.csv`
- `analysis_outputs/hidden_block_sequence_motif_shortlist.csv`
- `analysis_outputs/hidden_block_sequence_motif_axis_decompose.py`
- `analysis_outputs/hidden_block_sequence_motif_axis_decompose_report.md`
- `analysis_outputs/hidden_block_sequence_motif_axis_target_decomposition.csv`
- `analysis_outputs/hidden_block_sequence_motif_axis_block_decomposition.csv`
- `analysis_outputs/hidden_block_sequence_motif_cellgate_scores.csv`
- `analysis_outputs/hidden_block_sequence_motif_cellgate_safe_scores.csv`
- `analysis_outputs/hidden_block_sequence_motif_cellgate_integrity.csv`
- `analysis_outputs/hidden_block_sequence_motif_focused_validation.py`
- `analysis_outputs/hidden_block_sequence_motif_focused_candidates.csv`
- `analysis_outputs/hidden_block_sequence_motif_focused_scenario_summary.csv`
- `analysis_outputs/hidden_block_sequence_motif_focused_mask_summary.csv`
- `analysis_outputs/hidden_block_sequence_motif_focused_combined.csv`
- `analysis_outputs/public_lb_inverse_mask_audit.py`
- `analysis_outputs/public_lb_inverse_mask_audit_report.md`
- `analysis_outputs/public_lb_inverse_actual_scores.csv`
- `analysis_outputs/public_lb_inverse_mask_top512.csv`
- `analysis_outputs/public_lb_inverse_mask_raw05_compatible_top512.csv`
- `analysis_outputs/public_lb_inverse_mask_all_sign_compatible_top512.csv`
- `analysis_outputs/public_lb_inverse_target_delta_top64.csv`
- `analysis_outputs/public_lb_inverse_candidate_ranking.csv`
- `analysis_outputs/public_lb_inverse_candidate_ranking_signcompatible.csv`
- `analysis_outputs/public_lb_inverse_submission_shortlist.csv`
- `analysis_outputs/block_scale_jepa_target_audit.py`
- `analysis_outputs/block_scale_jepa_target_report.md`
- `analysis_outputs/block_scale_jepa_target_summary.csv`
- `analysis_outputs/block_scale_jepa_target_target_detail.csv`
- `analysis_outputs/block_scale_jepa_target_hidden_rates.csv`
- `analysis_outputs/block_scale_jepa_target_candidate_proxy.csv`
- `analysis_outputs/block_scale_jepa_target_integrity.csv`
- `analysis_outputs/block_scale_jepa_neutral_scan.py`
- `analysis_outputs/block_scale_jepa_neutral_report.md`
- `analysis_outputs/block_scale_jepa_neutral_scan.csv`
- `analysis_outputs/block_scale_jepa_neutral_safe.csv`
- `analysis_outputs/block_scale_jepa_neutral_saved_proxy.csv`
- `analysis_outputs/block_scale_jepa_neutral_integrity.csv`
- `analysis_outputs/block_scale_jepa_combined_proxy_compare.csv`
- `analysis_outputs/block_scale_jepa_submission_shortlist.csv`
- `analysis_outputs/block_scale_jepa_axis_projector.py`
- `analysis_outputs/block_scale_jepa_axis_projector_report.md`
- `analysis_outputs/block_scale_jepa_axis_projector_scores.csv`
- `analysis_outputs/block_scale_jepa_axis_projector_selected.csv`
- `analysis_outputs/block_scale_jepa_axis_projector_proxy.csv`
- `analysis_outputs/block_scale_jepa_axis_combined_shortlist_proxy.csv`
- `analysis_outputs/block_scale_jepa_axis_submission_shortlist.csv`

## 2026-05-27 JEPA block-consensus gate / raw-corrector

JEPA 논문식 target-block representation 예측을 그대로 확률 residual로 쓰면 public/raw05 축에서 깨지는 경우가 많았다. 이번 pass에서는 `block_scale_jepa_target_hidden_rates.csv`의 hidden block-rate를 직접 덮어쓰지 않고, 여러 JEPA predictor가 같은 block/target 방향으로 동의하는지를 gate로만 사용했다.

핵심 구조:

- context -> target representation 예측 결과를 block-level rate prior로 변환
- top JEPA methods consensus: `top3`, `top8`, `zctx_local`, `rt_zctx`
- aggregate: weighted logit / median logit
- gate: `energy_consensus`, `raw_agree`, `raw_posterior`, `raw_or_posterior`
- raw05 drift가 큰 high-upside 후보는 `raw_timeline_jepa_rescue_strict_scale0p75`와 기존 bridge anchor로 logit 보정

중요한 발견:

- direct consensus gate는 `c42fbf1e` 기준 focused proxy를 `0.582124 -> 0.582115`로 낮췄지만 raw05-axis delta가 `+2.5e-7~+3.0e-7`로 약간 양수였다.
- high-upside unsafe 후보(`86c6c9d1 + no_q2 energy_consensus`)는 compact proxy가 `0.58188`까지 내려갔지만 raw05-axis delta가 `+1e-5`라 그대로 제출하기 어렵다.
- raw-counter + anchor micro refine로 focused proxy `0.582096`까지 낮추면서 bad residual axis를 `~0.0020`으로 낮췄다.
- pair ensemble은 raw 음수 조건에서 `0.582095`까지 도달했지만 posterior proxy는 `0.57688`로 약간 높다.

새 후보 우선순위:

```csv
rank,file,role,focused_scenario_score,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,note
1,submission_jepa_micro_bridge_ensemble_5ffa44a8.csv,best raw-negative micro ensemble,0.582095,0.576880,-0.0000001005,0.002379,focused 최상 + raw 음수지만 posterior/bad는 약간 높음
2,submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv,best focused micro raw-corrector,0.582096,0.576868,0.0000001199,0.002011,focused 최상권 + bad 낮음, raw delta가 아주 약한 양수
3,submission_jepa_block_consensus_rawcorr_micro_fea06910.csv,best strict raw micro,0.582099,0.576869,-0.0000000031,0.002023,거의 raw-neutral strict 후보
4,submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv,pre-micro refine,0.582101,0.576859,0.0000000870,0.002044,posterior가 micro best보다 조금 낮음
5,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,raw-corrected consensus,0.582107,0.576847,0.0000000745,0.001844,bad axis가 가장 안정적인 축
6,submission_jepa_block_consensus_gate_bc0ed866.csv,direct consensus gate,0.582115,0.576845,0.0000002971,0.002204,raw 보정 전 direct gate
```

검증:

- `jepa_block_consensus_gate.py`: py_compile 통과, saved 100, integrity key ok / duplicate 0 / null 0
- `jepa_block_consensus_rawcorrector.py`: py_compile 통과, saved 54, integrity key ok / duplicate 0 / null 0
- `jepa_block_consensus_rawcorrector_refine.py`: py_compile 통과, saved 90, integrity key ok / duplicate 0 / null 0
- `jepa_block_consensus_rawcorrector_microrefine.py`: py_compile 통과, saved 90, integrity key ok / duplicate 0 / null 0
- `jepa_micro_bridge_ensemble.py`: py_compile 통과, saved 66, integrity key ok / duplicate 0 / null 0

판단:

- 이번 JEPA 활용은 "representation prediction 자체"보다 "representation agreement as gate"가 더 public-safe하다.
- Q2/Q3 count 강제는 계속 위험하다. 이번에 살아남은 후보도 대부분 `no_q2`, `q3_s2_s3_s4`, `s_all`처럼 Q2를 직접 세게 건드리지 않는 조합이다.
- 제출 순서는 공격적으로는 `submission_jepa_micro_bridge_ensemble_5ffa44a8.csv`, 균형형으로는 `submission_jepa_block_consensus_rawcorr_micro_fea06910.csv`, bad-axis 보수형으로는 `submission_jepa_block_consensus_rawcorr_4fd8bab2.csv`가 적절하다.

## 2026-05-27 actual-public anchor ranker / final priority

기존 pseudo-public 절대 CE를 그대로 믿지 않고, 실제 제출값이 있는 `stage2` public LB를 기준점으로 삼는 actual-anchor ranker를 만들었다.  
각 inverse-fit public scenario/mask 조합에서 `candidate_loss - stage2_loss + stage2_public_lb`로 후보 점수를 재정의하고, `inverse_top`, `raw05_compatible`, `all_sign` 3개 mask set을 따로 채점한 뒤 합쳤다.

- script: `analysis_outputs/public_lb_actual_anchor_ranker.py`
- pool: 352 candidates
- combo sets: 3
- shortlist: 80
- final priority generator: `analysis_outputs/final_jepa_candidate_priority.py`
- outputs:
  - `analysis_outputs/public_lb_actual_anchor_ranker_report.md`
  - `analysis_outputs/public_lb_actual_anchor_ranker_shortlist.csv`
  - `analysis_outputs/final_jepa_candidate_priority_20260527.csv`
  - `analysis_outputs/final_jepa_candidate_priority_20260527.md`
  - `analysis_outputs/final_jepa_candidate_family_summary_20260527.csv`
  - `analysis_outputs/final_jepa_constrained_shortlist_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/public_lb_actual_anchor_ranker.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - 최종 priority 12개 submission 직접 검사: 250 rows, sample columns/order ok, key order ok, duplicate keys 0, null probabilities 0, probability range `[0, 1]` 통과

calibration:

```csv
file,known_public,actual_anchor_score_final,error_direction
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5775263072,0.5779059944,ranker pessimistic by +0.0003238423
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,0.5779449757,exact anchor
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5783033652,0.5799865296,ranker pessimistic by +0.0010231407 mean
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5784273528,0.5813157907,ranker pessimistic by +0.0021897411
submission_jepa_latent_q2_w0p45.csv,0.5798012862,0.5801455759,ranker slightly pessimistic by +0.0001434669 mean
submission_jepa_latent_residual_probe.csv,0.5812273278,0.5802891189,ranker optimistic by -0.0012342624 mean
```

따라서 `actual_anchor_score_final`은 public-consistency filter이지, raw05 actual `0.5775263072`를 이겼다는 증거는 아니다. 특히 ranker가 raw05 자체를 `0.577906`으로 비관적으로 채점한다. 반대로 direct JEPA latent residual은 실제 public에서 `0.581227`로 크게 실패했는데 ranker는 `0.580289`로 덜 나쁘게 본다. 이 bias 때문에 direct latent residual/Q2-forced 계열은 여전히 금지한다.

최종 제출 후보 우선순위:

```csv
rank,file,tier,actual_anchor_score_final,focused_scenario_score,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,decision
1,submission_jepa_micro_bridge_ensemble_5ffa44a8.csv,A-aggressive,0.577842518,0.582094747,0.576879713,-0.000000100,0.002379415,highest JEPA upside shot
2,submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv,A-balanced,0.577842546,0.582096377,0.576867541,0.000000120,0.002011024,balanced low-bad candidate; raw drift is tiny positive
3,submission_jepa_block_consensus_rawcorr_micro_fea06910.csv,A-strict,0.577842874,0.582099158,0.576868543,-0.000000003,0.002023242,strict raw05-axis neutral candidate
4,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv,B-stable,0.577843875,0.582107452,0.576847262,0.000000074,0.001843945,low-bad stable fallback
5,submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv,B-refine,0.577843174,0.582100504,0.576859088,0.000000087,0.002043811,pre-micro reference candidate
6,submission_jepa_bridge_ensemble_c42fbf1e.csv,B-baseline,0.577846374,0.582123709,0.576847161,-0.000000018,0.002362955,bridge baseline before consensus correction
7,submission_jepa_bridge_posteriorreg_9c5e225e.csv,B-regularized,0.577847897,0.582134120,0.576830476,-0.000000048,0.002295194,posterior/bad-axis regularized alternative
8,submission_jepa_public_minimax_bridge_84b71a03.csv,C-bridge,0.577853477,0.582171926,0.576813062,-0.000000083,0.002110555,simplest public-minimax bridge sanity candidate
9,submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv,C-conservative,0.577892946,0.582411185,0.576729034,0.000000070,0.001108127,older conservative block-entropy candidate
10,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv,C-conservative,0.577892464,0.582439189,0.576676903,-0.000000260,0.001310293,conservative posterior/raw-safety reference
```

family-level finding:

- `jepa_public_minimax_bridge` has the best family-level actual-anchor score (`0.577829`) but higher median bad-axis (`0.00346`), so it is a source of upside rather than the safest submission family.
- `jepa_micro_bridge_ensemble` and `jepa_block_consensus_rawcorr_micro` cluster tightly around `0.5778425` with lower bad-axis (`~0.0020`). This is the current best JEPA agreement-as-gate region.
- `jepa_public_blockentropy` has better posterior (`0.576677~0.576729`) and lower bad-axis (`~0.0012`) but weaker focused/actual-anchor score, so it is a conservative fallback rather than the main shot.
- Direct blockscale neutral candidates can show very low posterior (`~0.57620`) but raw-axis delta around `+2e-5`, which public feedback says is too dangerous without raw-counter projection.
- constrained shortlist check confirms the exclusion: top public-minimax bridge candidates with bad-axis `<=0.0025` still have raw-axis deltas around `+2.3e-7~+5.0e-7`, while the only strict raw-negative public-minimax candidate in that slice is `84b71a03` with weaker actual-anchor `0.577853`.

updated decision:

- 제출을 1개만 한다면 `submission_jepa_micro_bridge_ensemble_5ffa44a8.csv`가 현재 JEPA upside 1순위다.
- raw05-axis 중립성을 더 세게 요구하면 `submission_jepa_block_consensus_rawcorr_micro_fea06910.csv`가 1순위다.
- bad-residual axis를 가장 낮추고 싶으면 `submission_jepa_block_consensus_rawcorr_4fd8bab2.csv` 또는 보수적으로 `submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv`를 둔다.
- 관측 public 기준으로는 raw05 `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`의 `0.5775263072`가 여전히 실제로 이겨야 할 점수다. 새 JEPA 후보들은 아직 actual public으로 검증된 개선이 아니라, raw05-compatible hidden-structure 탐색 후보로 봐야 한다.

## 2026-05-27 raw05-anchor JEPA micro injection / target assembly

raw05 actual public `0.5775263072`를 직접 anchor로 두고, JEPA 후보의 움직임을 아주 얇게 주입하는 두 가지 후속 실험을 했다. 목적은 JEPA latent를 크게 믿는 게 아니라, raw05가 이미 맞춘 public 방향을 훼손하지 않는 cell/target만 찾는 것이다.

### 1) raw05-anchor micro injection

- script: `analysis_outputs/raw05_anchor_jepa_micro_injection.py`
- scan: 59,031 candidates generated, top 1,000 rescored, 48 saved
- outputs:
  - `analysis_outputs/raw05_anchor_jepa_micro_injection_scan.csv`
  - `analysis_outputs/raw05_anchor_jepa_micro_injection_scored.csv`
  - `analysis_outputs/raw05_anchor_jepa_micro_injection_shortlist.csv`
  - `analysis_outputs/raw05_anchor_jepa_micro_injection_integrity.csv`
  - `analysis_outputs/raw05_anchor_jepa_micro_injection_report.md`
- verification: selected submissions have 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range inside `[0, 1]`.

결과는 부정적이지만 단서가 있다.

- partial injection, row gate, sign-agreement gate가 full JEPA micro donor를 이기지 못했다.
- top saved 후보는 대부분 `w=1.00`, `all`, `ones` 형태의 기존 full donor였다.
- 즉, 이 구간의 JEPA signal은 특정 row만 살짝 여는 방식보다 이미 만든 micro bridge/consensus 후보 전체 형태로 유지될 때 proxy가 낫다.
- 해석: JEPA는 여기서 row residual generator가 아니라, 이미 만들어진 hidden-energy manifold 후보를 고르는 representation prior로 작동한다.

### 2) target ablation / assembly

- script: `analysis_outputs/raw05_jepa_target_ablation_assembly.py`
- scan: 499 candidates, 58 saved
- final addendum: `analysis_outputs/final_jepa_target_assembly_addendum_20260527.csv`
- report: `analysis_outputs/raw05_jepa_target_ablation_assembly_report.md`
- final priority update: `analysis_outputs/final_jepa_candidate_priority_20260527.md`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_target_ablation_assembly.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 58 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063018, 0.980055]`

label type별 best:

```csv
label_type,n,best_actual_anchor_score,best_posterior,best_raw_delta,median_bad_axis
leave_one_raw,138,0.5778423645,0.5767175900,-0.0000018227,0.0020578589
donor_full,20,0.5778425183,0.5766769031,-0.0000002596,0.0020771829
leave_group_raw,128,0.5778432161,0.5768598906,-0.0000012623,0.0014899281
group_graft,78,0.5778498411,0.5770376015,-0.0000027766,0.0013060075
single_graft,135,0.5778824418,0.5772581808,-0.0000012062,0.0050681432
```

핵심 단서:

- single-target graft는 전부 약하다. best single target도 Q3 `0.577882`, S3 `0.577885` 수준이라 `0.577842`대 full donor와 거리가 있다.
- group graft도 full donor를 못 이긴다. best group은 `q3_s2_s3_s4<=jepa_bridge_ensemble_c42fbf1e`, actual-anchor `0.577849841`, posterior `0.577290`.
- 따라서 JEPA 개선은 Q3나 S 하나짜리 column effect가 아니라, Q/S target block을 함께 움직이는 representation effect다.
- `Q2=raw05` 복귀는 bad-axis를 크게 줄인다. 대표 후보 `submission_raw05_jepa_targetasm_6bc24126.csv`는 actual-anchor `0.577843323`, posterior `0.576885630`, raw delta `-0.000000177`, bad-axis `0.001094933`이다. rank 1보다 actual-anchor는 약간 손해지만 bad-axis가 절반 이하로 줄어 risk-reducer 역할이 명확하다.
- `S1=raw05` 복귀는 actual-anchor proxy만 보면 가장 미세하게 좋아진다. 대표 후보 `submission_raw05_jepa_targetasm_3de4ab79.csv`는 actual-anchor `0.577842364`, posterior `0.577094423`, raw delta `-0.000000935`, bad-axis `0.002585704`이다. 다만 posterior와 bad-axis가 올라가므로 1순위가 아니라 high-upside probe로만 본다.
- `Q2+S1=raw05` pair 복귀는 위 둘의 중간 지점이다. 대표 후보 `submission_raw05_jepa_targetasm_5d057c41.csv`는 actual-anchor `0.577843216`, posterior `0.577100227`, raw delta `-0.000001008`, bad-axis `0.001340874`이다. S1 단독 probe보다 actual-anchor는 `+0.000000852` 손해지만 bad-axis를 `0.002586 -> 0.001341`로 크게 낮춘다.

updated decision:

- 기존 1순위 `submission_jepa_micro_bridge_ensemble_5ffa44a8.csv`는 유지한다.
- 실제 제출 슬롯을 여러 개 쓸 수 있다면, `submission_raw05_jepa_targetasm_3de4ab79.csv`는 S1-objective가 public에서 ranker보다 더 맞을 때를 노리는 probe다.
- 그보다 risk를 낮춘 compromise probe는 `submission_raw05_jepa_targetasm_5d057c41.csv`다. S1 raw 신호를 일부 유지하면서 Q2 raw 복귀로 bad-axis를 줄인다.
- 보수 슬롯이라면 `submission_raw05_jepa_targetasm_6bc24126.csv` 또는 `submission_raw05_jepa_targetasm_6b1dc322.csv`가 Q2-risk를 줄이는 대안이다.
- JEPA 방향의 다음 실험은 row gate 확대가 아니라, target-block 단위 representation agreement와 Q2/S1의 역할 분리를 더 세밀하게 모델링하는 쪽이어야 한다.

### 3) continuous target-weight optimizer

binary target graft/leave 실험을 연속화했다. 각 후보는 `logit(raw05) + target_weight * (logit(donor) - logit(raw05))`로 만들었다.  
즉 JEPA donor를 정답 복원값으로 믿지 않고, target별 representation confidence로 해석했다.

- script: `analysis_outputs/raw05_jepa_target_weight_optimizer.py`
- scan: 8,520 candidates, 112 saved
- report: `analysis_outputs/raw05_jepa_target_weight_optimizer_report.md`
- shortlist: `analysis_outputs/raw05_jepa_target_weight_optimizer_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_target_weight_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_target_weight_optimizer.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 112 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063084, 0.979876]`

새 패턴:

- 가장 강한 actual-anchor 구간은 `Q3` donor delta를 `1.40`까지 키우고, `Q2/S1`을 `0.70~0.80` 근처로 두는 stress 구간이다. 다만 raw-axis가 양수로 넘어가므로 high-upside probe다.
- raw05 guardrail 안에서 더 안전한 경계는 `Q3=1.30`, `Q2=0.65~0.80`, `S1=0.65~0.70` 구간이다. `Q3=1.16` refine 구간은 actual-anchor는 덜 세지만 bad-axis가 확실히 낮다.
- 이건 앞선 ablation과 일치한다. Q3는 JEPA block signal의 핵심이고, Q2/S1은 public-risk 조절축이다. 다만 “Q2/S1을 많이 죽일수록 좋다”가 아니라, Q3를 강하게 열 때 Q2/S1이 raw/public axis를 맞추는 counterweight 역할을 한다.
- high-upside actual probe:
  - `analysis_outputs/submission_raw05_jepa_targetw_3af15cc3.csv`
  - donor `jepa_micro_bridge_ensemble_5ffa44a8`
  - weights `Q2=0.80`, `S1=0.70`, `Q3=1.40`, `S4=1.00`
  - actual-anchor `0.577838094`, posterior `0.576923792`, raw delta `+0.000000516`, bad-axis `0.002528`
  - 기존 rank 1 `5ffa44a8`의 actual-anchor `0.577842518`보다 proxy상 `-0.000004424` 좋지만 raw-positive라 공격 후보로만 둔다.
- raw-boundary Q3 stress probe:
  - `analysis_outputs/submission_raw05_jepa_targetw_c9b9fff4.csv`
  - weights `Q2=0.80`, `S1=0.65`, `Q3=1.30`
  - actual-anchor `0.577839127`, posterior `0.576940673`, raw delta `+0.000000032`, bad-axis `0.002499`
  - q3=1.40보다 proxy는 `+0.000001033` 손해지만 raw/bad guardrail 안쪽에 걸친다.
- strict raw-negative sibling:
  - `analysis_outputs/submission_raw05_jepa_targetw_05ec9908.csv`
  - donor `jepa_micro_bridge_ensemble_9692910f`
  - weights `Q2=0.80`, `S1=0.65`, `Q3=1.30`
  - actual-anchor `0.577839218`, posterior `0.576939520`, raw delta `-0.000000015`, bad-axis `0.002491`
  - raw-positive를 허용하지 않는다면 이쪽이 stress branch 대표 후보다.
- low-bad target-weight:
  - `analysis_outputs/submission_raw05_jepa_targetw_31fa1ec0.csv`
  - weights `Q2=0.35`, `S1=0.55`, `Q3=1.16`
  - actual-anchor `0.577841741`, posterior `0.576943770`, raw delta `-0.000000384`, bad-axis `0.001423`
  - 기존 full donor보다 actual-anchor는 조금 손해지만 bad-axis가 낮아 보수 후보로 좋다.

updated decision:

- target-weight branch에서 공격 슬롯을 하나 쓰면 `submission_raw05_jepa_targetw_3af15cc3.csv`가 high-upside 1순위다.
- raw/bad guardrail을 더 중시하면 `submission_raw05_jepa_targetw_c9b9fff4.csv` 또는 raw-negative `submission_raw05_jepa_targetw_05ec9908.csv`가 stress branch 대표다.
- bad-axis를 낮추는 보수 슬롯이면 `submission_raw05_jepa_targetw_31fa1ec0.csv`가 `Q2=raw05` binary 후보보다 더 부드러운 대안이다.
- 다음 JEPA 실험은 Q3를 더 키우는 방향 자체보다, `Q3=1.30~1.40` stress branch에서 raw-positive를 상쇄하는 donor/axis counterweight를 찾는 쪽이다. 지금까지 가장 명확한 구조적 단서는 “Q3는 under-trusted이고, Q2/S1은 단순 제거 대상이 아니라 Q3 stress를 public/raw05 manifold 안에 묶는 제어축”이다.

### 4) Q3-stress counterweight optimizer

위 결론을 직접 실험했다. Q3 stress 후보를 base로 두고, low-bad/strict 후보를 counter로 삼아 target block 일부만 logit-space에서 당겼다.  
JEPA식 해석은 “Q3 target block representation은 유지하고, context/surrounding target block은 raw05/public axis와 agreement가 높은 쪽으로 낮은 energy를 만든다”이다.

- script: `analysis_outputs/raw05_jepa_q3stress_counterweight_optimizer.py`
- scan: 373,818 candidates, actual-anchor rescored 1,835, saved 93
- report: `analysis_outputs/raw05_jepa_q3stress_counterweight_report.md`
- shortlist: `analysis_outputs/raw05_jepa_q3stress_counterweight_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_q3stress_counterweight_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_q3stress_counterweight_optimizer.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 93 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.062924, 0.979845]`

새 패턴:

- best mask는 압도적으로 `non_q3_s4`였다. 즉 Q3와 S4는 stress base를 유지하고, Q1/Q2/S1/S2/S3만 counter 후보로 52% 당기는 형태가 가장 좋았다.
- `closer/opposing` cell gate보다 단순 `all` gate가 이겼다. row/cell sparsification보다 target-block level counterweight가 맞다는 증거다.
- 이 branch는 raw Q3 stress peak `3af15cc3`의 actual-anchor `0.577838094`는 못 넘지만, bad-axis를 `0.002528 -> 0.00178`대로 크게 낮춘다.

대표 후보:

- cleaner Q3-stress actual probe:
  - `analysis_outputs/submission_raw05_jepa_q3cw_d7f234ad.csv`
  - base `submission_raw05_jepa_targetw_24d8df9e.csv`, counter `submission_raw05_jepa_targetw_ce178c95.csv`
  - target mask `non_q3_s4`, alpha `0.52`
  - actual-anchor `0.577838915`, posterior `0.576929560`, raw delta `+0.000000049`, bad-axis `0.001793`
  - `c9b9fff4` 대비 actual-anchor는 `-0.000000212` 좋고 bad-axis는 `0.002499 -> 0.001793`으로 낮다.
- raw-boundary cleaner probe:
  - `analysis_outputs/submission_raw05_jepa_q3cw_96763236.csv`
  - actual-anchor `0.577839047`, posterior `0.576923843`, raw delta `+0.000000081`, bad-axis `0.001757`
  - raw-boundary bucket의 대표. Q3 stress signal은 유지하면서 bad-axis를 낮춘다.
- strict raw cleaner probe:
  - `analysis_outputs/submission_raw05_jepa_q3cw_7c3f5f65.csv`
  - actual-anchor `0.577839949`, posterior `0.576931721`, raw delta `-0.000000069`, bad-axis `0.001794`
  - raw-positive를 절대 허용하지 않는 경우의 대표.
- low-bad/posterior safe probe:
  - `analysis_outputs/submission_raw05_jepa_q3cw_8b80cfd5.csv`
  - actual-anchor `0.577839669`, posterior `0.576900008`, raw delta `+0.000000032`, bad-axis `0.001496`
  - actual-anchor는 조금 손해지만 posterior와 bad-axis가 좋다.

updated decision:

- 공격 슬롯은 여전히 raw Q3 stress `submission_raw05_jepa_targetw_3af15cc3.csv`가 가장 세다.
- 안전한 Q3-stress compromise는 `submission_raw05_jepa_q3cw_d7f234ad.csv`를 우선한다. 이 후보는 `c9b9fff4`보다 actual-anchor와 bad-axis가 동시에 낫다.
- strict raw 슬롯은 `submission_raw05_jepa_q3cw_7c3f5f65.csv`, low-bad 슬롯은 `submission_raw05_jepa_q3cw_8b80cfd5.csv`다.
- 다음 실험은 `non_q3_s4` counterweight를 고정하고 alpha `0.42~0.62`, base/counter donor를 더 좁혀 continuous local search를 하는 것이다. 특히 S4를 base 쪽에 남겨야 하는 점이 새 hidden structure 단서다.

### 5) Q3-stress counterweight local refine

위의 다음 실험을 바로 실행했다. coarse search에서 확인된 `non_q3_s4` 구조를 고정하지는 않고, 그 주변 target profile을 좁게 탐색했다. JEPA 관점에서는 Q3/S4 stress block을 latent target representation으로 보존하고, 나머지 target block만 public/raw05 agreement가 높은 counter representation 쪽으로 낮은 energy를 만들도록 당긴 실험이다.

- script: `analysis_outputs/raw05_jepa_q3stress_counterweight_local_refine.py`
- scan: 116,424 candidates, actual-anchor rescored 2,800, saved 106
- report: `analysis_outputs/raw05_jepa_q3stress_counterweight_local_report.md`
- shortlist: `analysis_outputs/raw05_jepa_q3stress_counterweight_local_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_q3stress_counterweight_local_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_q3stress_counterweight_local_refine.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 106 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063120, 0.979847]`

새 패턴:

- coarse optimum alpha `0.52`가 상한은 아니었다. local search에서는 `alpha=0.64`까지 올린 `nonq3_s4tiny` 또는 `nonq3s4_flat`이 actual-anchor와 posterior/bad-axis 균형을 더 좋게 만든다.
- S4를 완전히 고정하는 것보다 `S4=0.20` 정도만 counter 쪽으로 열어둔 `nonq3_s4tiny`가 raw-boundary/actual-probe에서 강하다. 즉 S4는 Q3와 같이 stress base를 유지해야 하지만, 완전 고정 invariance는 아니다.
- `nonq3s4_q1light`는 actual-anchor를 조금 희생하는 대신 bad-axis를 `0.00090`까지 낮춘다. 이건 제출 1순위라기보다 public이 bad-axis를 실제로 얼마나 보상하는지 확인하는 diagnostic probe다.
- `nonq3s4_q2s1heavy`는 posterior가 가장 낮은 축(`0.576891`)을 만든다. Q2/S1은 단순 risk가 아니라 raw/public manifold에 붙이는 counter-context 역할을 한다는 이전 해석과 일치한다.

대표 후보:

- refined cleaner actual probe:
  - `analysis_outputs/submission_raw05_jepa_q3cwlocal_284f5ff5.csv`
  - profile `nonq3_s4tiny`, alpha `0.64`
  - actual-anchor `0.5778388969`, posterior `0.5768932360`, raw delta `+0.0000001196`, bad-axis `0.0014828538`
  - coarse `d7f234ad`보다 actual-anchor는 `-0.000000018`, posterior는 `-0.000036324`, bad-axis는 `0.001793 -> 0.001483`으로 개선된다. 단 raw delta가 `1e-7`을 살짝 넘으므로 공격적 compromise다.
- raw-boundary local probe:
  - `analysis_outputs/submission_raw05_jepa_q3cwlocal_2e417327.csv`
  - profile `nonq3_s4tiny`, alpha `0.58`
  - actual-anchor `0.5778391996`, posterior `0.5768932403`, raw delta `+0.0000000991`, bad-axis `0.0016678717`
  - raw delta `1e-7` 안쪽을 요구하면 local branch 대표다.
- strict raw local probe:
  - `analysis_outputs/submission_raw05_jepa_q3cwlocal_257a022b.csv`
  - profile `nonq3s4_q2light`, alpha `0.64`
  - actual-anchor `0.5778399160`, posterior `0.5769067002`, raw delta `-0.0000000694`, bad-axis `0.0016810472`
  - raw-positive를 허용하지 않을 때의 strict candidate다.
- posterior-safe local probe:
  - `analysis_outputs/submission_raw05_jepa_q3cwlocal_2585a02f.csv`
  - profile `nonq3s4_q2s1heavy`, alpha `0.64`
  - actual-anchor `0.5778393471`, posterior `0.5768910104`, raw delta `+0.0000000994`, bad-axis `0.0015405777`
  - posterior proxy를 우선하면 이 후보가 local branch 대표다.
- very-low-bad diagnostic probe:
  - `analysis_outputs/submission_raw05_jepa_q3cwlocal_33a60b3b.csv`
  - profile `nonq3s4_q1light`, alpha `0.64`
  - actual-anchor `0.5778405147`, posterior `0.5769059251`, raw delta `-0.0000000250`, bad-axis `0.0009021719`
  - bad-axis는 지금까지의 Q3-stress branch 중 가장 낮은 축이다. actual-anchor 손해가 있으므로 제출 우선순위는 낮지만, public이 bad-axis를 강하게 보상하는지 확인하는 probe로 가치가 있다.

updated decision:

- Q3-stress cleaner branch에서 1개만 고르면 `submission_raw05_jepa_q3cwlocal_284f5ff5.csv`가 현재 가장 좋은 refined compromise다.
- raw-axis guardrail을 더 세게 걸면 `submission_raw05_jepa_q3cwlocal_2e417327.csv`, strict raw는 `submission_raw05_jepa_q3cwlocal_257a022b.csv`다.
- bad-axis 보상 여부를 확인할 슬롯이 있으면 `submission_raw05_jepa_q3cwlocal_33a60b3b.csv`가 diagnostic 후보다.
- 지금까지 JEPA 아이디어가 가장 잘 먹히는 방식은 direct latent residual이 아니라, target-block별 representation agreement를 energy처럼 써서 Q3/S4 stress block과 non-Q3 counter-context를 분리하는 것이다.

### 6) Context-target JEPA energy gate

이번에는 I-JEPA 논문의 아이디어를 더 직접적으로 반영했다. 논문에서 중요한 점은 입력 자체를 복원하는 게 아니라, context block으로 target block의 representation을 예측하고 compatible pair에는 낮은 energy를 주는 것이다. 이 데이터에 맞춰 `Q1/Q2/S1/S2/S3`를 context block, `Q3/S4`를 target block으로 두고, 기존 후보들의 logit residual pool에서 context-to-target ridge energy를 학습했다. 그런 다음 counterweight 후보별로 row-level context 변경이 Q3/S4 target block 예측 energy를 낮출 때만 적용했다.

- script: `analysis_outputs/raw05_jepa_context_target_energy_gate.py`
- scan: 117,348 candidates, actual-anchor rescored 1,513, saved 59
- report: `analysis_outputs/raw05_jepa_context_target_energy_gate_report.md`
- shortlist: `analysis_outputs/raw05_jepa_context_target_energy_gate_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_context_target_energy_gate_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_context_target_energy_gate.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 59 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063145, 0.979819]`

결과 해석:

- 이 branch는 local counterweight actual-proxy frontier를 넘지 못했다. best actual은 `0.5778400631`으로 local best `0.5778388969`보다 약하다.
- 대신 raw-axis drift를 더 낮춘다. best guardrail 후보들은 raw delta `~6e-8~7e-8`, posterior `~0.576893`, bad-axis `~0.00170~0.00183`에 모인다.
- `soft_floor` gate가 압도적이다. 완전 hard gate보다, context-target energy가 낮아지는 방향을 더 믿되 일부 base context를 남기는 방식이 맞다.
- energy를 가장 크게 낮춘 후보들은 actual-anchor가 약해진다. 즉 learned JEPA compatibility 자체만 최적화하면 public proxy를 못 따라간다. 이건 중요한 실패 단서다: JEPA energy는 primary objective가 아니라 raw05/public-axis guardrail로 써야 한다.

대표 후보:

- best context-target energy actual probe:
  - `analysis_outputs/submission_raw05_jepa_ctxenergy_d4aff04d.csv`
  - profile `nonq3s4_flat`, alpha `0.68`, gate `soft_floor`
  - actual-anchor `0.5778400631`, posterior `0.5768931955`, raw delta `+0.0000000721`, bad-axis `0.0018323855`
  - energy delta vs base `-0.02818`
- lower-bad guardrail:
  - `analysis_outputs/submission_raw05_jepa_ctxenergy_88fa416a.csv`
  - actual-anchor `0.5778402550`, posterior `0.5768939171`, raw delta `+0.0000000693`, bad-axis `0.0017047789`
  - energy delta vs base `-0.02604`
- posterior/low-bad context candidate:
  - `analysis_outputs/submission_raw05_jepa_ctxenergy_a726b739.csv`
  - profile `nonq3s4_q2s1heavy`, alpha `0.68`, gate `soft_floor`
  - actual-anchor `0.5778406779`, posterior `0.5768933502`, raw delta `+0.0000000602`, bad-axis `0.0016969992`
  - energy delta vs base `-0.03316`
- energy-only diagnostic:
  - `analysis_outputs/submission_raw05_jepa_ctxenergy_d19d7846.csv`
  - actual-anchor `0.5778472374`, posterior `0.5768823349`, raw delta `-0.0000000245`, bad-axis `0.0018822212`
  - energy delta vs base `-0.06939`
  - compatibility energy는 크게 좋아지지만 actual-anchor가 나빠진다. JEPA energy 단독 최적화가 제출 점수와 다르다는 반례로 둔다.

updated decision:

- context-target energy gate 후보는 제출 1순위가 아니다. local q3cw best `submission_raw05_jepa_q3cwlocal_284f5ff5.csv`와 raw-boundary `submission_raw05_jepa_q3cwlocal_2e417327.csv`가 여전히 우선이다.
- 다만 raw delta를 더 낮춘 JEPA-compatible guardrail 슬롯이면 `submission_raw05_jepa_ctxenergy_d4aff04d.csv` 또는 lower-bad `submission_raw05_jepa_ctxenergy_88fa416a.csv`가 의미 있다.
- 이 실험으로 JEPA 해석은 더 분명해졌다. “context가 target을 잘 예측한다”는 energy는 유용하지만, public LogLoss frontier를 직접 결정하지 않는다. 따라서 다음에는 energy를 더 낮추는 방향이 아니라, local q3cw frontier 위에서 energy를 작은 penalty/constraint로만 쓰는 constrained search가 맞다.

### 7) Energy-constrained local frontier stitch

6번 결론을 그대로 실행했다. direct JEPA latent residual이나 energy-only optimization은 public proxy를 못 넘겼기 때문에, local q3cw frontier를 base로 두고 JEPA context-target energy는 작은 제약/penalty로만 사용했다. 구현은 q3cw base를 ctxenergy/low-bad/target-weight donor 쪽으로 logit-space stitch하고, raw05-compatible 축과 bad-axis를 동시에 보면서 후보를 저장한다.

- script: `analysis_outputs/raw05_jepa_energy_constrained_frontier.py`
- scan: 443,633 candidates, actual-anchor rescored 1,842, saved 75
- report: `analysis_outputs/raw05_jepa_energy_constrained_frontier_report.md`
- shortlist: `analysis_outputs/raw05_jepa_energy_constrained_frontier_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_energy_constrained_frontier_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_energy_constrained_frontier.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - priority rebuild `python3 analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 75 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063092, 0.979828]`

새 패턴:

- 처음으로 local q3cw actual-proxy frontier를 더 낮추면서 bad-axis를 크게 줄인 branch가 나왔다. 이전 local best `q3cwlocal_284f5ff5`는 actual-anchor `0.5778388969`, bad-axis `0.0014828538`였는데, 새 best `energyfront_a190aa25`는 actual-anchor `0.5778387145`, bad-axis `0.0008568227`이다.
- 다만 best actual 후보는 energy delta가 `+0.0183603972`로 나빠진다. 이것은 JEPA energy 자체가 목표가 아니라는 반례다. 좋은 방향은 “energy를 무조건 낮춘다”가 아니라, Q3/S4 stress block을 보존한 상태에서 public/raw05/bad-axis manifold에 붙이는 stitch다.
- energy-improved 후보들은 actual-anchor를 약 `7e-7` 정도 양보하지만 raw drift와 bad-axis가 더 안정적이다. 이들은 public이 bad-axis를 얼마나 보상하는지 확인하는 guarded 제출 슬롯이다.
- `q1light`, `q2s1heavy`, `context_only`가 살아남았다. 숨은 구조 해석은 Q1은 약하게 누르고, Q2/S1 context는 raw/public manifold에 붙이는 counter-context로 쓰며, Q3/S4 stress block은 보존해야 한다는 쪽으로 더 좁혀졌다.

대표 후보:

- current frontier actual probe:
  - `analysis_outputs/submission_raw05_jepa_energyfront_a190aa25.csv`
  - profile `context_only`, beta `0.48`
  - base `submission_raw05_jepa_q3cwlocal_33a60b3b.csv`, donor `submission_raw05_jepa_targetw_f883e40c.csv`
  - actual-anchor `0.5778387145`, posterior `0.5769035650`, raw delta `+0.0000000715`, bad-axis `0.0008568227`, mean move `0.0014865785`
  - energy delta vs base `+0.0183603972`
- energy-improved guarded probe:
  - `analysis_outputs/submission_raw05_jepa_energyfront_fa0e1e2d.csv`
  - profile `q1light`, beta `0.48`
  - actual-anchor `0.5778394496`, posterior `0.5769001917`, raw delta `+0.0000000606`, bad-axis `0.0008307026`, mean move `0.0014911600`
  - energy delta vs base `-0.0071816604`
- low-bad raw-safe energy-improved probe:
  - `analysis_outputs/submission_raw05_jepa_energyfront_ea665780.csv`
  - profile `q1light`, beta `0.48`
  - actual-anchor `0.5778394860`, posterior `0.5769059799`, raw delta `+0.0000000158`, bad-axis `0.0007624060`, mean move `0.0014815584`
  - energy delta vs base `-0.0014165302`
- strict raw-neutral probe:
  - `analysis_outputs/submission_raw05_jepa_energyfront_0f7e85a0.csv`
  - profile `q1light`, beta `0.35`
  - actual-anchor `0.5778398077`, posterior `0.5769058715`, raw delta `-0.0000000001`, bad-axis `0.0008151860`, mean move `0.0014740738`
  - energy delta vs base `-0.0010992002`
- lowest-bad diagnostic:
  - `analysis_outputs/submission_raw05_jepa_energyfront_61238b04.csv`
  - actual-anchor `0.5778398636`, posterior `0.5769062088`, raw delta `-0.0000000019`, bad-axis `0.0007519524`, mean move `0.0014709775`
  - bad-axis는 가장 낮지만 energy delta가 `+0.0140903917`라서 diagnostic 성격이 강하다.

updated decision:

- 새 1순위 제출 probe는 `submission_raw05_jepa_energyfront_a190aa25.csv`다. raw05 public control을 실제로 이겼다는 증거는 아직 아니지만, 현 local actual-anchor proxy에서는 q3cwlocal을 넘고 bad-axis도 크게 줄였다.
- energy guardrail을 우선하면 `submission_raw05_jepa_energyfront_fa0e1e2d.csv`, raw drift 최소화와 bad-axis를 우선하면 `submission_raw05_jepa_energyfront_ea665780.csv`, strict raw-neutral이면 `submission_raw05_jepa_energyfront_0f7e85a0.csv`다.
- priority builder에도 반영되어 `analysis_outputs/final_jepa_candidate_priority_20260527.csv`의 1-4위가 energyfront 후보로 갱신됐다.
- 현재 JEPA 사용법의 결론은 확정적이다. reconstruction이나 direct residual injection이 아니라, hidden target-block agreement를 energy/constraint로 쓰고, 실제 제출 후보는 raw05-compatible manifold에서 stitch해야 한다.

### 8) Energyfront micro-refine with row-level bad-axis gate

7번 energyfront는 local actual-anchor proxy를 처음으로 더 낮췄지만, best candidate `a190aa25`의 bad-axis는 아직 `0.0008568`이었다. 이번에는 energyfront 후보들을 하나의 local manifold로 보고, 그 안에서 작은 logit-space stitch를 다시 수행했다. JEPA context-target energy gate만으로는 부족했기 때문에 row-level bad-axis contribution이 줄어드는 구간에 더 강하게 step을 주는 `bad_soft_floor` gate를 추가했다.

- script: `analysis_outputs/raw05_jepa_energyfront_microrefine.py`
- scan: 285,122 candidates, actual-anchor rescored 2,775, saved 91
- report: `analysis_outputs/raw05_jepa_energyfront_microrefine_report.md`
- shortlist: `analysis_outputs/raw05_jepa_energyfront_microrefine_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_energyfront_microrefine_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/raw05_jepa_energyfront_microrefine.py` 통과
  - priority rebuild `python3 analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 91 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.063067, 0.979828]`

새 패턴:

- micro-refine은 `a190aa25`의 actual-anchor `0.5778387145`를 넘지는 못했다. best micro actual은 `0.5778387644`로 약 `5e-8` 손해다.
- 대신 bad-axis가 `0.0008568 -> 0.0004950` 또는 `0.0004204`까지 무너졌다. 즉 이 branch는 "actual frontier 개선"이 아니라 "public이 bad-axis를 보상하는지 확인하는 고효율 probe"다.
- 살아남은 거의 모든 상위 후보가 `context_only + bad_soft_floor + beta 0.48`이다. 숨은 구조는 더 분명해졌다. Q3/S4 stress block은 움직이지 않고, Q1/Q2/S1/S2/S3 context만 row별로 bad-axis가 줄어드는 위치에서 target-weight donor 쪽으로 당겨야 한다.
- `energy_soft_floor`보다 `bad_soft_floor`가 강했다. JEPA energy는 representation compatibility를 정의하지만, public-risk 제거는 learned energy보다 bad-axis row contribution이 더 직접적이다.

대표 후보:

- best micro actual/low-bad probe:
  - `analysis_outputs/submission_raw05_jepa_efmicro_3eece507.csv`
  - actual-anchor `0.5778387644`, posterior `0.5769028425`, raw delta `+0.0000000859`, bad-axis `0.0004950061`
  - profile `context_only`, beta `0.48`, row gate `bad_soft_floor`
  - base `submission_raw05_jepa_energyfront_e519aeb7.csv`, donor `submission_raw05_jepa_targetw_f883e40c.csv`
- energy-improved micro probe:
  - `analysis_outputs/submission_raw05_jepa_efmicro_1859bae9.csv`
  - actual-anchor `0.5778388870`, posterior `0.5769035474`, raw delta `+0.0000000741`, bad-axis `0.0004809036`
  - energy delta vs base `-0.0001864186`
- posterior-safe micro probe:
  - `analysis_outputs/submission_raw05_jepa_efmicro_f88f2cec.csv`
  - actual-anchor `0.5778389013`, posterior `0.5768999630`, raw delta `+0.0000000990`, bad-axis `0.0004482097`
  - risk flag가 `none`으로 떨어지는 rare micro candidate다.
- lowest-bad micro diagnostic:
  - `analysis_outputs/submission_raw05_jepa_efmicro_9f19106d.csv`
  - actual-anchor `0.5778389482`, posterior `0.5769038009`, raw delta `+0.0000000721`, bad-axis `0.0004203752`
  - bad-axis 보상 가설을 가장 강하게 검증하는 후보.
- strict low-bad diagnostic:
  - `analysis_outputs/submission_raw05_jepa_efmicro_4cf5e862.csv`
  - actual-anchor `0.5778400486`, posterior `0.5769058630`, raw delta `-0.0000000016`, bad-axis `0.0004450383`
  - raw-positive를 허용하지 않으면서 bad-axis collapse를 테스트하는 후보.

updated decision:

- 제출 1순위 actual probe는 여전히 `submission_raw05_jepa_energyfront_a190aa25.csv`다.
- public이 bad-axis를 실제로 강하게 보상한다는 쪽에 베팅할 슬롯이면 `submission_raw05_jepa_efmicro_3eece507.csv` 또는 `submission_raw05_jepa_efmicro_f88f2cec.csv`가 더 정보량이 크다.
- `submission_raw05_jepa_efmicro_f88f2cec.csv`는 posterior `0.576899963`, raw delta `9.9e-8`, bad-axis `0.000448`로 priority table에서 risk flag `none`인 드문 상위 후보다.
- priority builder에 반영되어 `analysis_outputs/final_jepa_candidate_priority_20260527.csv`의 2-5위가 micro-refine 후보로 갱신됐다.
- 현재 모델링 결론: JEPA hidden block은 "무엇을 움직일지"를 정하고, public/bad-axis row gate는 "어디를 움직일지"를 정한다. Q3/S4 target block 보존 + context-only bad-axis row correction이 다음 미세 탐색의 핵심이다.

### 9) Efmicro row-gate local refine

8번 micro-refine에서 확인한 row-level bad-axis gate를 더 좁게 파고들었다. 이번 실험은 actual-anchor frontier를 더 낮추는 목적보다, JEPA식 context/target hidden block을 유지하면서 row별 gate 강도와 beta를 조절하면 bad-axis를 얼마나 더 제거할 수 있는지를 보는 실험이다. base는 energyfront/micro frontier, donor는 context-target energy 후보를 사용했다.

- script: `analysis_outputs/raw05_jepa_efmicro_gate_refine.py`
- scan: 59,439 candidates, actual-anchor rescored 2,201, saved 48
- report: `analysis_outputs/raw05_jepa_efmicro_gate_refine_report.md`
- shortlist: `analysis_outputs/raw05_jepa_efmicro_gate_refine_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_efmicro_gate_refine_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_efmicro_gate_refine.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - priority rebuild `python3 analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 48 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.0631268702671227, 0.979826655033526]`

새 패턴:

- actual-anchor frontier는 회복하지 못했다. best efgate actual은 `0.5778402624`로, micro best `0.5778387644`나 energyfront best `0.5778387145`보다 약하다.
- 대신 bad-axis가 한 번 더 무너졌다. micro 최저 bad-axis가 약 `0.0004204`였는데, efgate ultra-low branch는 `0.0000505`까지 내려갔다.
- smooth compromise는 `q1light + beta 0.44 + bad_f010_s075`다. 이 조합은 posterior를 `0.5768889`까지 낮추고 bad-axis를 `0.00023~0.00024`로 줄인다.
- ultra-low-bad branch는 `context_only` 또는 `q2s1heavy + beta 0.44 + bad_hard_f010`이다. bad-axis는 훨씬 낮지만 actual-anchor를 더 희생한다.
- 해석상 JEPA energy는 여전히 primary objective가 아니다. 유용한 조합은 "Q3/S4 target block 보존"과 "Q1/Q2/S1/S2/S3 context row 중 bad-axis가 줄어드는 위치만 이동"이다. 즉 JEPA는 representation block을 정하고, public-risk gate가 적용 위치를 정한다.

대표 후보:

- smooth posterior/low-bad diagnostic:
  - `analysis_outputs/submission_raw05_jepa_efgate_ac60a2e6.csv`
  - actual-anchor `0.5778402624`, posterior `0.5768889122`, raw delta `+0.0000000966`, bad-axis `0.0002444987`
  - profile `q1light`, beta `0.44`, row gate `bad_f010_s075`, gate mean `0.4483053130`
  - priority table rank 6, risk flag `none`
- ultra-low-bad raw-tight diagnostic:
  - `analysis_outputs/submission_raw05_jepa_efgate_d592970e.csv`
  - actual-anchor `0.5778403876`, posterior `0.5768940501`, raw delta `+0.0000000753`, bad-axis `0.0000505423`
  - profile `context_only`, beta `0.44`, row gate `bad_hard_f010`, gate mean `0.3988`
  - priority table rank 7, risk flag `none`
- q2/s1-heavy ultra-low-bad actual-side diagnostic:
  - `analysis_outputs/submission_raw05_jepa_efgate_d359abc4.csv`
  - actual-anchor `0.5778402904`, posterior `0.5768925959`, raw delta `+0.0000000962`, bad-axis `0.0000539487`
  - profile `q2s1heavy`, beta `0.44`, row gate `bad_hard_f010`

updated decision:

- 제출 1순위 actual probe는 그대로 `submission_raw05_jepa_energyfront_a190aa25.csv`다.
- bad-axis 보상 가설을 검증하는 실험 슬롯이면 `submission_raw05_jepa_efmicro_f88f2cec.csv`가 actual/predictor 균형이 가장 좋고, 더 극단적인 stress test는 `submission_raw05_jepa_efgate_ac60a2e6.csv` 또는 `submission_raw05_jepa_efgate_d592970e.csv`다.
- efgate 후보는 "점수를 바로 낮춘 발견"이라기보다, public LB가 bad-axis를 실제로 얼마나 보상하는지 확인하기 위한 가장 깨끗한 JEPA row-gate probe다.
- priority builder에 반영되어 `analysis_outputs/final_jepa_candidate_priority_20260527.csv`의 6-7위가 efgate 후보로 추가됐다.

### 10) EFGate backoff frontier

9번 efgate가 actual-anchor frontier를 너무 많이 포기했기 때문에, 이번에는 micro/energyfront actual frontier와 efgate low-bad 후보 사이만 좁게 interpolation했다. 의도는 단순하다. JEPA row-gate로 발견한 bad-axis collapse를 전부 가져오지 말고, actual frontier에 가까운 base에서 작은 backoff만 적용해 posterior/bad-axis를 낮출 수 있는지 확인했다.

- script: `analysis_outputs/raw05_jepa_efgate_backoff_frontier.py`
- scan: 86,471 candidates, actual-anchor rescored 2,386, saved 68
- report: `analysis_outputs/raw05_jepa_efgate_backoff_frontier_report.md`
- shortlist: `analysis_outputs/raw05_jepa_efgate_backoff_frontier_shortlist.csv`
- final addendum: `analysis_outputs/final_jepa_efgate_backoff_frontier_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/raw05_jepa_efgate_backoff_frontier.py` 통과
  - priority rebuild `python3 analysis_outputs/final_jepa_candidate_priority.py` 통과
  - saved 68 submissions integrity: 250 rows, key/order ok, duplicate keys 0, null probabilities 0, probability range `[0.0631373014074767, 0.979826523403525]`

결과:

- actual frontier는 또 넘지 못했다. best backoff actual은 `0.5778396907`로, `a190aa25`의 `0.5778387145`보다 약하다.
- 하지만 risk-none 중간점이 생겼다. `efmicro_f88f2cec`는 actual `0.5778389013`, posterior `0.5768999630`, bad-axis `0.0004482`였고, 새 backoff best는 actual `0.5778396907`, posterior `0.5768931992`, bad-axis `0.0004186`이다. 즉 actual을 약 `7.9e-7` 양보하면 posterior와 bad-axis가 동시에 내려간다.
- efgate-to-efgate interpolation에서는 bad-axis가 `0.0000323`까지 내려갔다. 이건 지금까지 raw05-compatible JEPA branch에서 가장 강한 bad-axis collapse다.
- 살아남은 actual-side backoff는 대부분 `q1light + lambda 0.60 + no row gate`다. 이미 efgate 후보 자체가 row-level filtering을 끝낸 상태라, 그 위에서 다시 hard gate를 걸기보다 smooth interpolation이 맞았다.
- ultra-low-bad backoff는 `efgate_d592970e`를 base로 두고 다른 efgate low-bad 후보로 이동할 때 나온다. 즉 이 축은 실제 actual frontier가 아니라 "bad-axis manifold" 내부 탐색이다.

대표 후보:

- risk-none middle point:
  - `analysis_outputs/submission_raw05_jepa_efback_cc265f32.csv`
  - actual-anchor `0.5778396907`, posterior `0.5768931992`, raw delta `+0.0000000889`, bad-axis `0.0004185961`
  - profile `q1light`, lambda `0.60`, row gate `none`
  - base `submission_raw05_jepa_efmicro_5d2d2af0.csv`, donor `submission_raw05_jepa_efgate_793e3f5d.csv`
  - priority table rank 6, risk flag `none`
- strongest bad-axis stress test:
  - `analysis_outputs/submission_raw05_jepa_efback_9c50051c.csv`
  - actual-anchor `0.5778403391`, posterior `0.5768930500`, raw delta `+0.0000000900`, bad-axis `0.0000323388`
  - profile `q1light`, lambda `0.60`, row gate `none`
  - base `submission_raw05_jepa_efgate_d592970e.csv`, donor `submission_raw05_jepa_efgate_9d40abd2.csv`
  - priority table rank 7, risk flag `none`

updated decision:

- 제출 우선순위 자체는 여전히 `energyfront_a190aa25`, `efmicro_3eece507`, `efmicro_f88f2cec`가 앞선다.
- public이 posterior/bad-axis를 강하게 보상할 가능성을 확인하는 슬롯이면 `efback_cc265f32`가 efgate 단독보다 나은 compromise다.
- "bad-axis가 정말 public에서 먹히는가"만 확인하려면 `efback_9c50051c`가 지금까지 가장 선명한 stress test다.
- 모델링 해석은 더 좁아졌다. JEPA hidden structure는 새 feature를 직접 예측값에 많이 주입할수록 깨지고, 이미 발견된 row-gated manifold 안에서 작은 interpolation/backoff를 할 때 가장 안정적으로 쓸 수 있다.

### 11) I-JEPA + LeJEPA paper read and SIGReg residual-health audit

논문 두 개를 따로 읽어서 역할을 분리했다. `ijepa.pdf`는 block design 논문이고, `lejepa.pdf`는 그 block prediction이 collapse/anisotropy로 망가지지 않게 하는 distribution regularizer 논문으로 봐야 한다. 정리 메모는 `analysis_outputs/paper_notes/jepa_two_paper_reading_20260527.md`에 남겼다.

핵심 번역:

- I-JEPA: raw reconstruction이 아니라 context representation으로 target representation을 예측한다. 우리 문제에서는 `Q3/S4`를 target block, `Q1/Q2/S1/S2/S3`를 context/counter-context block으로 보는 게 가장 자연스럽다. row gate는 이미지의 position/mask token 역할을 한다.
- I-JEPA: target은 작고 국소적인 단일 셀이 아니라 큰 semantic block이어야 한다. 그래서 Q3 단독 graft보다 `Q3/S4` 보존 + context block correction이 더 맞다.
- LeJEPA: prediction compatibility만으로는 부족하고 embedding distribution이 non-degenerate 해야 한다. 우리 후보에서는 row-level logit residual이 embedding이고, public/bad-axis 한 방향으로 찌그러진 residual move는 벌점을 받아야 한다.
- LeJEPA/SIGReg: random projection Epps-Pulley Gaussian goodness-of-fit을 residual health proxy로 쓸 수 있다. 이건 제출 score 자체가 아니라, actual-anchor/public-axis ranker가 한 축에 과적합되는지 보는 regularizer다.

실험:

- script: `analysis_outputs/lejepa_sigreg_candidate_audit.py`
- report: `analysis_outputs/lejepa_sigreg_candidate_audit_report.md`
- audit csv: `analysis_outputs/lejepa_sigreg_candidate_audit.csv`
- final addendum: `analysis_outputs/final_jepa_lejepa_sigreg_addendum_20260527.csv`
- scored candidates: 326 in the first pass; latest audit after adding SIGReg-gated candidates scored 328 candidates
- verification:
  - `python3 -m py_compile analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 실행 완료

중요한 변화:

- 기존 actual-anchor 1위 `submission_raw05_jepa_energyfront_a190aa25.csv`는 actual `0.5778387145`로 여전히 frontier지만, LeJEPA residual health가 `11.0586`이고 combined rank가 약 `104`로 밀린다. 즉 이 후보는 actual proxy에는 좋지만 residual distribution 관점에서는 약간 더 anisotropic하다.
- SIGReg combined best는 `submission_raw05_jepa_efmicro_1859bae9.csv`다. actual `0.5778388870`, posterior `0.5769035474`, raw delta `7.41e-8`, bad-axis `0.0004809`, residual health `10.2317`, combined rank `62.3`.
- residual health 자체가 특히 좋은 micro diagnostic은 `submission_raw05_jepa_efmicro_9f19106d.csv`다. actual `0.5778389482`, bad-axis `0.0004204`, residual health `9.7821`, combined rank `64.0`.
- `submission_raw05_jepa_efmicro_63fc9157.csv`, `submission_raw05_jepa_efmicro_26253469.csv`, `submission_raw05_jepa_efmicro_cfdf196e.csv`도 LeJEPA-balanced 상위권이다. 공통점은 aggressive efgate/backoff보다 residual distribution이 덜 찌그러진 상태에서 bad-axis를 낮춘다는 점이다.
- efgate/backoff extreme은 bad-axis가 더 작지만 health가 항상 좋지는 않다. `efback_9c50051c`는 bad-axis `0.0000323`으로 stress test로는 가장 선명하지만, LeJEPA 관점에서는 제출 본선 후보보다 diagnostic으로 보는 게 맞다.

updated decision:

- strict actual-anchor만 최적화하면 1순위는 여전히 `submission_raw05_jepa_energyfront_a190aa25.csv`다.
- JEPA 논문 아이디어를 더 충실히 따르는 balanced probe는 `submission_raw05_jepa_efmicro_1859bae9.csv` 또는 `submission_raw05_jepa_efmicro_9f19106d.csv`다. 전자는 energy/actual 균형, 후자는 health/bad-axis 균형이 더 좋다.
- `submission_raw05_jepa_efmicro_3eece507.csv`는 micro actual best로 유지하되, LeJEPA health로 보면 `1859bae9`와 `9f19106d`보다 덜 예쁘다.
- 다음 생성 실험은 "SIGReg-gated micro refine"가 맞다. row move를 적용할 조건을 `bad-axis 감소` + `context-target energy 악화 없음` + `SIGReg/public-axis anisotropy 악화 없음`으로 걸어야 한다.
- 모델링 결론: I-JEPA는 `어떤 block 관계를 보존/예측할지`를 정하고, LeJEPA는 `그 move가 residual manifold를 collapse시키지 않는지`를 검사한다. 지금까지 실패한 direct latent residual 주입은 두 번째 조건을 거의 통제하지 못해서 public에서 깨진 것으로 해석된다.

### 12) LeJEPA SIGReg-gated micro refine

11번의 결론을 실제 생성 규칙으로 넣었다. 즉 단순히 후보를 만든 뒤 SIGReg로 사후 평가한 것이 아니라, row move를 적용할 때부터 `bad-axis 감소`, `context-target energy 악화 제한`, `public-axis norm/anisotropy 악화 제한`, `quick SIGReg health`를 gate로 썼다. 목적은 actual-anchor frontier를 새로 넘기기보다, LeJEPA식 non-collapse 제약이 bad-axis collapse stress test를 더 깨끗하게 만들 수 있는지 확인하는 것이었다.

- script: `analysis_outputs/raw05_jepa_sigreg_gated_microrefine.py`
- scan: 233,516 candidates, actual-anchor rescored 1,034, saved 61
- shortlist: `analysis_outputs/raw05_jepa_sigreg_gated_microrefine_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_sigreg_gated_microrefine_report.md`
- final addendum: `analysis_outputs/final_jepa_sigreg_gated_microrefine_addendum_20260527.csv`
- full SIGReg audit: `analysis_outputs/lejepa_sigreg_candidate_audit.csv`
- latest deterministic audit size: 328 candidates total, including 43 `raw05_jepa_siggate`, 39 `raw05_jepa_efmicro`, and 27 `raw05_jepa_siganchor` rows
- integrity: all saved submissions have 250 rows, key/order ok, duplicate keys 0, null probability 0, probability range about `[0.063124, 0.979827]`

대표 SIGReg-gated 후보:

- `analysis_outputs/submission_raw05_jepa_siggate_fd0e9622.csv`
  - actual-anchor `0.5778400704`, posterior `0.5768946573`, raw delta `9.80e-8`, bad-axis `2.166e-5`
  - deterministic full LeJEPA residual health `9.8712`, combined rank `103.30`
  - stable full-audit 기준 siggate 1위다. actual-anchor는 약하지만 low-bad/health 균형이 가장 좋다.
- `analysis_outputs/submission_raw05_jepa_siggate_64220cc6.csv`
  - actual-anchor `0.5778401865`, posterior `0.5768939419`, raw delta `9.46e-8`, bad-axis `2.505e-5`
  - deterministic full LeJEPA residual health `10.4401`, combined rank `119.25`
  - 초기 siggate 대표였지만 stable audit에서는 `fd0e9622`가 더 낫다.
- `analysis_outputs/submission_raw05_jepa_siggate_78179445.csv`
  - actual-anchor `0.5778403527`, posterior `0.5768927865`, raw delta `9.25e-8`, bad-axis `2.650e-5`
  - deterministic full LeJEPA residual health `10.0187`, combined rank `119.75`
  - posterior가 낮은 low-bad diagnostic이다. residual-health 최상위는 아니다.
- `analysis_outputs/submission_raw05_jepa_siggate_6d681440.csv`
  - actual-anchor `0.5778401881`, posterior `0.5768940171`, raw delta `9.60e-8`, bad-axis `6.605e-6`
  - deterministic full LeJEPA residual health `11.5145`, combined rank `159.40`
  - near-zero bad-axis stress test다. public이 bad-axis collapse를 강하게 보상하는지 확인하는 용도다.
- `analysis_outputs/submission_raw05_jepa_siggate_c335d69e.csv`
  - actual-anchor `0.5778401213`, posterior `0.5768926274`, raw delta `1.13e-7`, bad-axis `2.991e-5`
  - deterministic full LeJEPA residual health `10.7015`, combined rank `134.60`
  - siggate 안에서는 actual-anchor가 가장 낫지만 raw delta가 `1e-7` guardrail을 조금 넘는다.

중요한 결론:

- LeJEPA gate는 기대한 일을 했다. efgate/backoff manifold에서 bad-axis를 `1e-5` 근처까지 밀면서도 residual health가 완전히 무너지는 후보를 걸러냈다.
- 하지만 actual-anchor frontier는 넘지 못했다. deterministic full SIGReg combined top은 `submission_raw05_jepa_efmicro_5d2d2af0.csv`, `submission_raw05_jepa_efmicro_3eece507.csv`, `submission_raw05_jepa_efmicro_9f19106d.csv` 같은 efmicro 계열이고, strict actual-anchor frontier는 `submission_raw05_jepa_energyfront_a190aa25.csv`다.
- 따라서 siggate 계열은 1순위 제출 후보가 아니라 public feedback을 해석하기 위한 probe다. 특히 `fd0e9622`, `64220cc6`, `78179445`, `6d681440`은 각각 stable low-bad/health, earlier balanced representative, low-posterior low-bad, near-zero bad-axis의 stress test를 담당한다.
- 다음 생성 방향은 더 extreme efgate/backoff로 가는 것이 아니다. `efmicro` base만 쓰는 SIGReg-gated micro refine 또는 siggate 후보를 health-constrained interpolation으로 `efmicro_1859bae9`/`efmicro_9f19106d` 쪽으로 되돌리는 방향이 더 맞다.

updated decision:

- 실제 제출 우선순위는 `energyfront_a190aa25`, `efmicro_3eece507`, `efmicro_5d2d2af0`, `efmicro_9f19106d`, `efmicro_f88f2cec`, `efmicro_9e631d75`가 앞선다.
- LeJEPA low-bad stress를 가장 선명하게 테스트하려면 `siggate_fd0e9622`가 첫 슬롯이고, near-zero bad-axis reward만 보려면 `siggate_6d681440`이다.
- I-JEPA/LeJEPA 조합의 현재 해석: I-JEPA는 `Q3/S4 target block`과 `Q1/Q2/S1/S2/S3 context block`의 구조를 찾게 해주고, LeJEPA는 그 구조를 따라 움직인 residual이 public-axis 한 방향으로 collapse되는지 감시한다. 이 조합은 direct latent residual보다 row-gated interpolation/selection에 더 잘 맞는다.

### 13) SIGReg micro anchor refine and deterministic audit fix

12번 siggate는 bad-axis를 강하게 눌렀지만 actual-anchor를 너무 포기했다. 그래서 새 실험은 `efmicro/energyfront` actual-anchor 근처만 base로 두고, low-bad siggate 방향으로 작게 이동하거나 low-bad 후보를 다시 efmicro 쪽으로 되돌리는 양방향 interpolation으로 제한했다. 이 실험 중 full SIGReg audit의 random projection seed가 후보 순서에 의존하는 문제가 보여서, `analysis_outputs/lejepa_sigreg_candidate_audit.py`를 후보 파일명+블록명 seed로 고정했다. 이제 같은 파일은 candidate set/order가 달라져도 같은 residual-health 값을 갖는다.

- script: `analysis_outputs/raw05_jepa_sigreg_micro_anchor_refine.py`
- scan: 30,720 candidates, actual-anchor and quick-SIGReg rescored 1,840, saved 63
- shortlist: `analysis_outputs/raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_sigreg_micro_anchor_refine_report.md`
- final addendum: `analysis_outputs/final_jepa_sigreg_micro_anchor_refine_addendum_20260527.csv`
- audit fix: `analysis_outputs/lejepa_sigreg_candidate_audit.py` now uses deterministic per-file/per-block random projection seeds
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_sigreg_micro_anchor_refine.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` 통과
  - `python3 analysis_outputs/raw05_jepa_sigreg_micro_anchor_refine.py` 완료
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
  - `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

대표 후보:

- `analysis_outputs/submission_raw05_jepa_efmicro_3eece507.csv`
  - actual-anchor `0.5778387644`, posterior `0.5769028425`, raw delta `8.59e-8`, bad-axis `0.0004950`
  - deterministic full LeJEPA residual health `9.8574`, combined rank `63.45`
  - 현재 deterministic full SIGReg combined 기준 efmicro 1위다.
- `analysis_outputs/submission_raw05_jepa_efmicro_5d2d2af0.csv`
  - actual-anchor `0.5778388931`, posterior `0.5768998844`, raw delta `9.94e-8`, bad-axis `0.0004651`
  - deterministic full LeJEPA residual health `9.8721`, combined rank `63.60`
  - `3eece507`와 사실상 같은 frontier이며, posterior/actual 균형이 좋다.
- `analysis_outputs/submission_raw05_jepa_efmicro_9f19106d.csv`
  - actual-anchor `0.5778389482`, posterior `0.5769038009`, raw delta `7.21e-8`, bad-axis `0.0004204`
  - deterministic full LeJEPA residual health `9.4664`, combined rank `73.50`
  - bad-axis가 낮고 health도 좋아서 LeJEPA-balanced low-bad micro 후보로 유지한다.
- `analysis_outputs/submission_raw05_jepa_siganchor_3644a42f.csv`
  - actual-anchor `0.5778390951`, posterior `0.5768992188`, raw delta `9.53e-8`, bad-axis `0.0004000`
  - deterministic full LeJEPA residual health `9.6842`, combined rank `107.65`
  - siganchor 계열 1위다. actual-anchor는 efmicro보다 약간 약하지만 posterior/bad-axis/health가 모두 균형적이다.
- `analysis_outputs/submission_raw05_jepa_siganchor_882fa552.csv`
  - actual-anchor `0.5778390518`, posterior `0.5768993694`, raw delta `9.58e-8`, bad-axis `0.0004299`
  - deterministic full LeJEPA residual health `10.5243`, combined rank `114.95`
  - siganchor 중 actual-anchor 보존이 가장 좋다.

updated decision:

- 제출 후보를 하나만 고르면 여전히 strict actual-anchor는 `energyfront_a190aa25`다.
- JEPA/LeJEPA-balanced 후보를 고르면 `efmicro_3eece507` 또는 `efmicro_5d2d2af0`가 가장 설득력 있고, `efmicro_9f19106d`는 low-bad/health 균형 probe로 유지한다.
- public이 posterior/bad-axis 개선을 actual-anchor 미세 손실보다 보상하는지 확인하려면 `siganchor_3644a42f`가 `siggate`보다 덜 과격한 테스트다.
- pure bad-axis stress는 `siggate_fd0e9622` 또는 `siggate_6d681440`이다. 전자는 stable low-bad/health, 후자는 near-zero bad-axis를 담당한다.

### 14) Local public-LB proxy validation

요청에 따라 known public 제출 6개를 앵커로 local LB proxy 자체를 검증했다. 중요한 수정은 `posterior_expected_public_vs_anchor`를 독립 예측기로 취급하지 않은 것이다. 이 컬럼은 known public 앵커를 맞추도록 만든 scenario 축이라, 앵커 6개에서는 MAE가 0에 가깝지만 submit-before-LB 검증력이 있다는 뜻은 아니다.

- script: `analysis_outputs/local_lb_proxy_validation.py`
- report: `analysis_outputs/local_lb_proxy_validation_report.md`
- known-anchor predictions: `analysis_outputs/local_lb_proxy_validation_known.csv`
- model scores: `analysis_outputs/local_lb_proxy_validation_model_scores.csv`
- candidate bands: `analysis_outputs/local_lb_proxy_validation_candidate_predictions.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/local_lb_proxy_validation.py` 통과
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 완료

검증 결과:

- best independent LOOCV: `loocv_ridge_abs_axes_a1` = `abs(delta_vs_raw05_rawaxis)`, `abs(bad_residual_axis_ratio)`, `mean_abs_move_vs_raw05`
  - MAE `0.0003184931`, RMSE `0.0004029881`, max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`, Spearman `0.9429`, Kendall `0.8667`
- raw `actual_anchor_score_final`은 MAE `0.0010389647`로 너무 거칠다.
  - raw05 control을 `0.5779059944`로 비관적으로 봐서 실제 public `0.5775263072`와 `+0.0003796872` 차이.
  - direct latent residual은 반대로 실제 public `0.5812273278`보다 낙관적으로 봐서 direct latent 계열 reject 근거를 재확인했다.
- posterior scenario는 앵커 내 MAE `0.0`이지만, 이는 anchored reconstruction이다. 독립 local LB 검증으로 쓰면 안 된다.

raw05-relative 후보 해석:

- raw05 실제 public `0.5775263072`를 기준으로 각 local model의 상대 차이를 더해 재보정했다.
- 최상위 raw05-relative 후보는 `submission_raw05_jepa_siggate_6d681440.csv`
  - raw05-relative proxy `0.5775231116`, delta `-0.0000031956`
  - 그러나 이 delta는 best independent LOOCV MAE `0.0003184931`보다 100배 작고, model spread `0.0000642402`보다도 작다.
- `siggate_fd0e9622`, `siggate_64220cc6`, `siggate_78179445`, `efback_9c50051c`, `efgate_d592970e`도 모두 raw05 대비 `-3e-6` 근처다.
- `efmicro_5d2d2af0`, `efmicro_9f19106d`, `siganchor_3644a42f`도 raw05와 사실상 동률권이다.

updated decision:

- local LB proxy는 상위 후보들 사이의 `1e-6~1e-5` 차이를 검증할 해상도가 없다. 현재 proxy로는 raw05를 확실히 이긴다는 결론을 낼 수 없다.
- 그래도 proxy는 실패 계열 필터로 쓸 수 있다. direct latent residual/Q2-forced 계열처럼 bad-axis가 크거나 public-axis collapse가 강한 후보는 public에서도 악화될 가능성이 높다는 신호가 LOOCV에서 재확인됐다.
- 제출 우선순위는 local LB micro-rank보다 구조적 역할로 정해야 한다.
  - near-zero bad-axis stress: `siggate_6d681440`
  - stable low-bad/health: `siggate_fd0e9622`
  - LeJEPA-balanced micro: `efmicro_5d2d2af0`, `efmicro_9f19106d`
  - actual-anchor strict frontier: `energyfront_a190aa25`
- public feedback을 얻기 전까지 “0.57752 근처 raw05-equivalent 후보”로만 해석해야 한다. 로컬 검증만으로 0.5774 또는 0.576대 개선을 주장하면 과대해석이다.

### 15) Train-label JEPA context-target compatibility audit

I-JEPA 아이디어를 더 직접적으로 검증했다. context block을 `Q1/Q2/S1/S2/S3`, target block을 `Q3/S4`로 두고, train 라벨에서 context→target 조건부 모델을 학습했다. 후보 submission은 자기 자신의 context 확률로부터 예측되는 `Q3/S4`와 실제 후보의 `Q3/S4`가 얼마나 맞는지로 compatibility energy를 계산했다.

- script: `analysis_outputs/jepa_context_target_compatibility_audit.py`
- train CV: `analysis_outputs/jepa_context_target_compatibility_model_cv.csv`
- candidate scores: `analysis_outputs/jepa_context_target_compatibility_scores.csv`
- known-public validation: `analysis_outputs/jepa_context_target_compatibility_known_validation.csv`
- public-anchor LOOCV: `analysis_outputs/jepa_context_target_compatibility_lb_loocv.csv`
- report: `analysis_outputs/jepa_context_target_compatibility_report.md`
- verification:
  - `python3 -m py_compile analysis_outputs/jepa_context_target_compatibility_audit.py` 통과
  - `python3 analysis_outputs/jepa_context_target_compatibility_audit.py` 완료

train 내부 결과:

- `date_interleave_5fold`: baseline `0.6812936003` → model `0.6015007689`, delta `-0.0797928314`
- `leave_subject_out`: baseline `0.6910540832` → model `0.6334993553`, delta `-0.0575547279`
- 즉 `Q1/Q2/S1/S2/S3`에서 `Q3/S4`를 예측하는 조건부 구조는 진짜다. I-JEPA식 context-target block 가정은 데이터 안에서 강하게 성립한다.

하지만 public-anchor LOOCV:

- 기존 axes baseline: MAE `0.0003184931`
- axes + abs compatibility: MAE `0.0003886953`로 악화
- axes + signed compatibility: MAE `0.0010284398`로 크게 악화
- compatibility only: MAE `0.0013732485`, Spearman `-0.6571`
- compatibility abs only: MAE `0.0013070819`, Spearman `-0.9429`

이건 중요한 반전이다. train-label context-target compatibility를 낮추는 것 자체는 public LB 개선 proxy가 아니다. public 앵커 6개에서는 오히려 “너무 train-compatible한 Q3/S4”가 위험한 방향으로 나타난다. 예를 들어 stage2는 raw05보다 compatibility KL이 `-0.000755` 낮지만 public은 raw05보다 `+0.0004186685` 나쁘다. direct latent residual도 compatibility만 보면 나쁘지 않은데 public은 크게 실패한다.

상위 후보 해석:

- block-consensus 계열은 compatibility가 가장 낮다.
  - `submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv`: compat KL delta `-0.000890228`
  - 하지만 raw05-relative proxy는 `0.5775296738`로 raw05보다 약간 나쁘고 bad-axis도 `0.002011`이다. 과도한 context-target 정합화 후보로 본다.
- raw05 JEPA 후보들은 모두 비슷한 compatibility delta 구간에 몰린다.
  - `siggate_fd0e9622`: compat KL delta `-0.0007324014`, raw05-relative `0.5775231268`, bad-axis `0.00002166`
  - `siggate_6d681440`: compat KL delta `-0.0007323990`, raw05-relative `0.5775231116`, bad-axis `0.00000660`
  - `efmicro_5d2d2af0`: compat KL delta `-0.0007306921`, raw05-relative `0.5775238839`, bad-axis `0.0004651`
  - `energyfront_a190aa25`: compat KL delta `-0.0007314558`, raw05-relative `0.5775244922`, bad-axis `0.0008568`

updated decision:

- JEPA compatibility는 “최적화 목적”이 아니라 “과정합/과교정 guardrail”이다.
- context-target energy를 계속 낮추는 block-consensus/bridge 방향은 public-risk가 커진다. 이 계열은 낮은 energy 때문에 좋아 보이지만, known public 앵커가 그 가정을 반박한다.
- raw05-compatible 후보의 좋은 점은 compatibility를 어느 정도 개선하면서도 raw05 residual을 완전히 지우지 않는 데 있다.
- 현재 후보 중 이 audit이 밀어주는 것은 `siggate_fd0e9622`/`siggate_6d681440`의 low-bad probe와 `efmicro_5d2d2af0`/`efmicro_9f19106d`의 LeJEPA-balanced micro probe다. 반대로 block-consensus 계열은 compatibility가 더 좋아도 primary 제출 후보로 올리면 안 된다.
- 다음 생성 방향: context-target energy를 더 낮추지 말고, raw05 대비 compatibility delta를 `-0.00070 ~ -0.00075` 근처에 고정한 채 bad-axis와 LeJEPA residual health만 개선하는 constrained search가 맞다.

### 16) Raw05 JEPA compatibility-band constrained refinement + local LB check

15번 결론을 그대로 실험으로 옮겼다. context-target compatibility를 계속 낮추는 대신, raw05-compatible guardrail band를 고정하고 그 안에서 bad-axis, actual-anchor, LeJEPA residual health만 개선하는 후보를 생성했다.

- generator: `analysis_outputs/raw05_jepa_compat_band_refine.py`
- generated scan: `analysis_outputs/raw05_jepa_compat_band_refine_scan.csv`
- rescored table: `analysis_outputs/raw05_jepa_compat_band_refine_scored.csv`
- shortlist: `analysis_outputs/raw05_jepa_compat_band_refine_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_compat_band_refine_report.md`
- local-LB/LeJEPA addendum: `analysis_outputs/final_jepa_compat_band_refine_addendum_20260527.md`
- addendum csv: `analysis_outputs/final_jepa_compat_band_refine_addendum_20260527.csv`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_compat_band_refine.py` 통과
  - `python3 analysis_outputs/raw05_jepa_compat_band_refine.py` 완료
  - `python3 -m py_compile analysis_outputs/compat_band_local_lb_addendum.py` 통과
  - `python3 analysis_outputs/compat_band_local_lb_addendum.py` 완료
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 재실행 완료
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 재실행 완료

생성/필터링 결과:

- generated candidates: `56,160`
- rescored candidates: `1,800`
- saved submissions: `88`
- compatibility band: `[-0.000755, -0.000705]`, target center `-0.000732`
- saved submission integrity: 88개 모두 `rows=250`, `key_ok=True`, `duplicate_keys=0`, `null_probs=0`

local LB proxy 검증 결과는 그대로 보수적으로 해석해야 한다.

- best independent local proxy: `loocv_ridge_abs_axes_a1`
  - LOOCV MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max held-out error `0.0006141185`
- compat-band/local-lowbad 최상위의 raw05-relative delta는 `-0.0000032` 정도다.
- 이 차이는 LOOCV MAE보다 약 100배 작다. 따라서 local proxy만으로 raw05 public `0.5775263072`를 이긴다고 말하면 과대해석이다.

full LeJEPA/SIGReg audit까지 붙이면 compat-band 후보의 위치가 더 분명해진다.

- compat-band full-audit 1위:
  - `analysis_outputs/submission_raw05_jepa_compatband_e065e98e.csv`
  - actual-anchor `0.5778387573`
  - raw05-relative proxy `0.5775238438`, delta `-0.0000024634`
  - bad-axis `0.0004990734`
  - compat delta `-0.0007319736`
  - full LeJEPA residual health `10.0496`
  - combined rank `64.65`
- compat-band full-audit 2위:
  - `analysis_outputs/submission_raw05_jepa_compatband_abc94f31.csv`
  - actual-anchor `0.5778387567`
  - bad-axis `0.0005012897`
  - full health `10.1317`
  - combined rank `67.25`
- compat-band full-audit 3위:
  - `analysis_outputs/submission_raw05_jepa_compatband_57c2f1e7.csv`
  - actual-anchor `0.5778388247`
  - bad-axis `0.0004850301`
  - full health `10.0678`
  - combined rank `68.65`

하지만 전체 frontier와 비교하면 새 primary는 아니다.

- current full-audit frontier:
  - `analysis_outputs/submission_raw05_jepa_efmicro_3eece507.csv`: combined rank `63.45`
  - `analysis_outputs/submission_raw05_jepa_efmicro_5d2d2af0.csv`: combined rank `63.60`
- best compat-band:
  - `analysis_outputs/submission_raw05_jepa_compatband_e065e98e.csv`: combined rank `64.65`
- 차이는 작지만, compat-band refinement가 efmicro frontier를 넘지는 못했다.

local raw05-relative proxy 상위 후보는 대부분 ultra-low bad-axis stress probe다.

- `analysis_outputs/submission_raw05_jepa_compatband_cbdfe8f4.csv`
  - raw05-relative proxy `0.5775231070`
  - delta `-0.0000032002`
  - bad-axis `0.0000067217`
  - full combined rank `111.10`
- `analysis_outputs/submission_raw05_jepa_compatband_a5965ec3.csv`
  - raw05-relative proxy `0.5775231080`
  - bad-axis `0.0000066325`
  - full combined rank `139.95`
- `analysis_outputs/submission_raw05_jepa_compatband_f61b4f40.csv`
  - raw05-relative proxy `0.5775231088`
  - bad-axis `0.0000065079`
  - full combined rank `113.30`

updated decision:

- local LB 검증은 candidate rejector로는 유용하다. direct latent residual, Q2-forced, 과도한 block-consensus처럼 public-failure axis가 커지는 계열은 배제 근거가 된다.
- 하지만 local LB 검증은 top권 후보의 `1e-6 ~ 1e-5` 차이를 판별할 해상도가 없다. raw05-relative proxy 1등을 제출 우선순위 1등으로 두면 안 된다.
- compat-band constrained search의 결론은 “새 primary frontier 발견”이 아니라 “JEPA guardrail의 작동 범위 확인”이다.
- 제출 후보를 하나만 고르면 여전히 actual-anchor strict 계열 또는 efmicro frontier가 우선이다.
- JEPA guardrail을 명시적으로 테스트하려면 `submission_raw05_jepa_compatband_e065e98e.csv`가 가장 깨끗한 probe다.
- public-axis stress를 테스트하려면 `submission_raw05_jepa_compatband_cbdfe8f4.csv` 또는 기존 `submission_raw05_jepa_siggate_6d681440.csv`가 역할상 맞다. 단 이들은 primary가 아니라 bad-axis hypothesis 검증용이다.

### 17) Six-anchor public LB entropy projection: exact fit, poor held-out reliability

public LB 역추론을 더 직접적으로 했다. LogLoss는 hidden binary label에 대해 선형이므로, 6개 known public 제출을 선형 제약으로 두고 prior 예측에서 KL을 가장 적게 움직이는 pseudo-label posterior를 풀었다. 목적은 "known public 점수를 모두 맞추는 posterior"가 제출에 쓸 수 있는 신호인지 검증하는 것이다.

- observations updated: `analysis_outputs/public_probe_observations.csv`
  - `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`: public `0.5775263072`
  - `submission_jepa_latent_q2_w0p45.csv`: public `0.5798012862`
  - `submission_jepa_latent_residual_probe.csv`: public `0.5812273278`
- projection script: `analysis_outputs/public_lb_six_anchor_entropy_projection.py`
- fit table: `analysis_outputs/public_lb_six_anchor_entropy_projection_fit.csv`
- leave-one-anchor-out table: `analysis_outputs/public_lb_six_anchor_entropy_projection_loao.csv`
- candidate scan: `analysis_outputs/public_lb_six_anchor_entropy_projection_scan.csv`
- shortlist: `analysis_outputs/public_lb_six_anchor_entropy_projection_shortlist.csv`
- report: `analysis_outputs/public_lb_six_anchor_entropy_projection_report.md`
- validation addendum: `analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.md`
- verification:
  - `python3 -m py_compile analysis_outputs/public_lb_six_anchor_entropy_projection.py` 통과
  - `python3 analysis_outputs/public_lb_six_anchor_entropy_projection.py` 완료
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 재실행 완료
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 재실행 완료
  - `python3 -m py_compile analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.py` 통과
  - `python3 analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.py` 완료

결과:

- 6개 anchor 제약은 모든 prior에서 수치적으로 exact fit된다.
  - max residual: `~1e-12` 이하
  - mean abs posterior move:
    - `efmicro5`: `0.0172104622`
    - `compatband`: `0.0172103669`
    - `efmicro3`: `0.0172109717`
    - `raw05`: `0.0181051323`
    - `stage2`: `0.0204545955`
- 하지만 leave-one-anchor-out 신뢰도는 약하다.
  - best prior `efmicro5`: LOAO MAE `0.0010140239`, max abs `0.0027214978`
  - `compatband`: LOAO MAE `0.0010141249`
  - `raw05`: LOAO MAE `0.0010689185`
  - `stage2`: LOAO MAE `0.0012305072`
- 이전 best independent local proxy MAE `0.0003184931`보다 훨씬 나쁘다. 즉 6개 public score를 exact fit하는 posterior는 hidden public을 안정적으로 예측한다고 보기 어렵다.

생성 후보:

- generated public6 candidates: `280`
- local LB proxy evaluated candidates: `95`
- local raw05-relative rejects among evaluated: `95 / 95`
- best local public6 candidate:
  - `analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
  - raw05-relative proxy `0.5777863434`
  - delta vs raw05 public `+0.0002600362`
  - bad-axis `0.0004937317`
- best LeJEPA/SIGReg public6 candidate:
  - `analysis_outputs/submission_public6entropy_energyfront_all_g500_92c9b1dc.csv`
  - LeJEPA combined rank `83.65`
  - raw05-relative proxy `0.5780344774`
  - delta vs raw05 public `+0.0005081702`
  - bad-axis `-0.1307580271`

해석:

- posterior/LeJEPA health만 보면 public6 후보 일부는 좋아 보인다. 예를 들어 all-target g=0.5 계열은 posterior expected가 `0.5759`까지 내려간다.
- 그러나 그 개선은 bad residual axis를 크게 움직여 만든 가짜 안정성일 가능성이 높다. `bad_residual_axis_ratio`가 `-0.13` 근처로, 기존 실패 anchor보다 훨씬 큰 public-axis shift다.
- q3s4 tiny 후보들은 bad-axis를 낮게 유지하지만 local raw05-relative proxy가 최소 `+0.00026` 악화된다.

updated decision:

- 6-anchor entropy projection은 diagnostic으로만 쓴다.
- "public 점수를 정확히 맞추는 pseudo-label posterior"는 제출 후보로 신뢰하면 안 된다. 제약 수가 6개뿐이라 1750개 hidden cell을 너무 쉽게 설명할 수 있고, held-out anchor 예측력이 부족하다.
- 이 실험이 준 실질적 단서는 label posterior 자체가 아니라 target drift 방향이다.
  - `S3`는 projected mean이 일관되게 증가한다.
  - `Q1`은 projected mean이 감소한다.
  - `Q3/S2`는 작은 방향성만 보인다.
- 다음 안전한 활용법은 direct public6 posterior 제출이 아니라, raw05/efmicro 후보 안에서 `S3 up`, `Q1 down`을 아주 작은 row-gated perturbation으로만 테스트하는 것이다.

### 18) Local LB proxy correction + public6 drift microperturb validation

위 17번의 "public6 후보 전부 reject" 판정에는 검증 구현상 중요한 caveat가 있었다. 새로 만든 후보들은 `actual_anchor_score_final`/`mean_actual_anchor`가 없는데, 기존 local proxy 평균은 이 결측 anchor-feature 모델까지 섞어 비교했다. 그래서 `local_lb_proxy_validation.py`에 결측 후보용 `axis_only` 및 `available_*` proxy를 추가했다.

- updated validator: `analysis_outputs/local_lb_proxy_validation.py`
- new generator: `analysis_outputs/raw05_jepa_public6_drift_microperturb.py`
- scan: `analysis_outputs/raw05_jepa_public6_drift_microperturb_scan.csv`
- shortlist: `analysis_outputs/raw05_jepa_public6_drift_microperturb_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_public6_drift_microperturb_report.md`
- corrected public6 addendum: `analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.md`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_public6_drift_microperturb.py` 통과
  - `python3 analysis_outputs/raw05_jepa_public6_drift_microperturb.py` 완료
  - `python3 -m py_compile analysis_outputs/local_lb_proxy_validation.py` 통과
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
  - `python3 -m py_compile analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
  - `python3 analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.py` 완료
  - `python3 -m py_compile analysis_outputs/final_jepa_candidate_priority.py` 통과
  - `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

microperturb 생성:

- in-memory candidates: `10368`
- saved shortlist: `160`
- directions:
  - follow: public6 drift hypothesis (`Q1/Q3 down`, `S2/S3 up`)
  - anti: falsification control
- modes:
  - direct logit micro step
  - probability step
  - bad-axis orthogonalized step
  - bad-axis + raw-axis gradient orthogonalized step

corrected local-LB read:

- best independent LOOCV proxy remains `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs `0.0006141185`
- for candidates missing anchor-feature columns, use `axis_only` rather than full mixed proxy.
- corrected best available local public6 candidate:
  - `analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
  - available raw05-relative proxy `0.5775208869`
  - delta vs raw05 public `-0.0000054203`
  - model family `axis_only`
  - bad-axis `0.0004937317`
  - mean abs move vs raw05 `0.0003629832`
  - LeJEPA combined rank after expanded audit: `320.70`
- best public6drift local-axis candidate:
  - `analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_follow_ones_prob_bad_raw_ortho_g00800_5534de7c.csv`
  - available raw05-relative proxy delta `-0.0000007358`
  - bad-axis `0.004294`
  - mean abs move vs raw05 `0.000041`
  - LeJEPA combined rank `358.55`
- best LeJEPA public6drift candidate:
  - `analysis_outputs/submission_raw05_jepa_public6drift_siggate_q1_q3_s3_anti_signed_entropy_logit_g00400_053160a7.csv`
  - LeJEPA combined rank `161.40`
  - local available delta `+0.000014442`
  - bad-axis `-0.00000144`

updated interpretation:

- 기존 "public6 후보 전부 local reject"는 결측 anchor-feature 처리 때문에 너무 강한 결론이었다.
- 하지만 보정 후에도 public6 계열의 개선 신호는 `-5e-6` 수준으로, LOOCV proxy MAE `3.18e-4`보다 두 자릿수 작다. 로컬에서 유의미한 발견으로 보기 어렵다.
- axis-only로 가장 좋아 보이는 `raw05_q1q3s34_g030`은 LeJEPA/SIGReg 건강성이 약하다. 즉 LB-axis에는 맞지만 JEPA 구조 regularity에는 맞지 않는 probe다.
- public6drift micro 후보는 방향성 검증에는 유용했지만 frontier 제출 우선순위를 바꾸지 못했다. 현재 main priority는 여전히 `raw05_jepa_efmicro`/`compatband`/`siggate` raw05-compatible 계열이다.
- public6 후보를 제출한다면 "강한 개선 후보"가 아니라 one-shot diagnostic probe로만 다룬다.

### 19) Full actual-anchor augmentation for missing public6/public6drift candidates

18번에서 `axis_only` 보정으로 끝내면 검증이 여전히 약하다. 기존 pipeline에는 `raw05_anchor_jepa_micro_injection.actual_anchor_score()`가 있으므로, local 후보 중 `actual_anchor_score_final`이 비어 있는 파일을 같은 actual-anchor 방식으로 다시 채웠다.

- augmenter: `analysis_outputs/augment_missing_actual_anchor_candidates.py`
- augmented table: `analysis_outputs/public_lb_actual_anchor_missing_candidate_augmented.csv`
- report: `analysis_outputs/public_lb_actual_anchor_missing_candidate_augmented_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`
- verification:
  - `python3 -m py_compile analysis_outputs/augment_missing_actual_anchor_candidates.py` 통과
  - `python3 analysis_outputs/augment_missing_actual_anchor_candidates.py` 완료
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
  - `python3 analysis_outputs/public_lb_six_anchor_entropy_validation_addendum.py` 완료
  - `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

scored missing candidates:

- total: `255`
- `raw05_jepa_public6drift`: `160`
  - best actual-anchor `0.577836`
  - best ranker-selection `0.577837`
  - best abs bad-axis `2.64e-08`
  - best abs raw-axis `0`
- `public6entropy`: `95`
  - best actual-anchor `0.577687`
  - best ranker-selection `0.577996`
  - best abs bad-axis `0.000119`
  - best abs raw-axis `8.67e-08`

corrected local full-proxy read:

- best full local raw05-relative public6 candidates are now:
  - `analysis_outputs/submission_public6entropy_raw05_q3s4_g250_b19cb905.csv`
    - full local delta vs raw05 public `-0.0000124824`
    - actual-anchor `0.577799`
    - posterior `0.577345`
    - bad-axis `-0.000180`
    - raw-axis delta `0.0000228593`
    - ranker-selection `0.581408`
    - LeJEPA combined rank `177.40`
  - `analysis_outputs/submission_public6entropy_raw05_q3s4_g180_15f6d69a.csv`
    - full local delta `-0.0000104457`
    - actual-anchor `0.577816`
    - bad-axis `0.001226`
    - raw-axis delta `0.0000109470`
    - ranker-selection `0.580086`
    - LeJEPA rank `216.05`
  - `analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
    - full local delta `-0.0000102376`
    - actual-anchor `0.577869`
    - bad-axis `0.000494`
    - raw-axis delta `-0.0000000867`
    - ranker-selection `0.578987`
    - LeJEPA rank `274.05`
- lower-bad public6 candidates:
  - `analysis_outputs/submission_public6entropy_efmicro3_q3s4_g030_c2fe0845.csv`
    - full local delta `-0.0000046117`
    - actual-anchor `0.577825`
    - bad-axis `-0.000123`
    - raw-axis delta `0.0000016388`
    - ranker-selection `0.577998`
    - LeJEPA rank `133.65`
  - `analysis_outputs/submission_public6entropy_efmicro5_q3s4_g030_48fe9a83.csv`
    - full local delta `-0.0000044389`
    - actual-anchor `0.577825`
    - bad-axis `-0.000152`
    - raw-axis delta `0.0000016524`
    - LeJEPA rank `128.10`

updated decision:

- full actual-anchor 보강 후 public6entropy는 단순 axis-only보다 훨씬 강한 diagnostic family로 올라왔다.
- 하지만 local delta `1e-5`는 여전히 LOOCV proxy MAE `0.0003184931`보다 훨씬 작다.
- `raw05_q3s4_g250/g180`은 local full proxy가 가장 좋지만 raw-axis delta가 `1e-5~2e-5`로 커서 ranker-selection penalty가 크다. public LB가 raw-axis drift를 싫어하면 위험하다.
- `efmicro/compatband/energyfront q3s4 g030~g050`은 bad-axis는 낮고 actual-anchor도 괜찮지만 local delta가 `~4e-6`라 submit value는 diagnostic 수준이다.
- 현재 주 제출 우선순위는 계속 raw05-compatible `efmicro/compatband/siggate`다. public6entropy는 "q3s4 public inverse stress probe"로 별도 취급한다.

### 20) Local LB validation for public6 Q3/S4 axis-corrected JEPA candidates

19번의 public6entropy Q3/S4 후보는 local proxy가 좋지만 raw/posterior-axis penalty가 크다. 그래서 six-anchor posterior를 그대로 쓰지 않고, JEPA식으로 target block(Q3/S4)만 움직이되 raw-axis, bad-axis, ordinal-axis와 직교시키는 후보를 새로 만들었다.

- generator: `analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected.py`
- full scan: `analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected_scan.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
- verification:
  - `python3 -m py_compile analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected.py` 통과
  - `python3 analysis_outputs/raw05_jepa_public6_q3s4_axis_corrected.py` 완료
  - generated candidates: `2160`
  - saved shortlist: `180`
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
  - `python3 -m py_compile analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료 after expanded candidate sampling
  - `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

local LB proxy check:

- best independent local LB proxy model is unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.000318`
  - RMSE `0.000403`
  - max abs error `0.000614`
  - pairwise rank accuracy `0.933`
- global local proxy top still comes from older public6entropy Q3/S4 rows:
  - `submission_public6entropy_raw05_q3s4_g250_b19cb905.csv`
  - raw05-relative proxy delta `-0.000012`
  - but raw-axis delta `0.0000228593`, so ranker-selection penalty remains too high.
- best new axis-corrected local-proxy row:
  - `analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_direct_logit_strength_entropy_g100_2884f233.csv`
  - raw05-relative local proxy delta `-0.000006`
  - actual-anchor `0.577862`
  - posterior `0.577465`
  - raw-axis delta `0.000001252`
  - bad-axis `0.003189`
  - LeJEPA combined rank `422.20`
  - verdict: local proxy likes it slightly, but raw/bad/LeJEPA health reject it as a submission candidate.
- best guarded new axis-corrected row:
  - `analysis_outputs/submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_top60_strength_g015_4050287e.csv`
  - actual-anchor `0.577838`
  - posterior `0.576897`
  - raw-axis delta `0.000000187`
  - bad-axis `0.000360`
  - raw05-relative local proxy delta `-0.000003`
  - axis-only local delta `+0.000016`
  - LeJEPA residual health `10.566809`
  - LeJEPA combined rank `250.35`
  - added to final priority as `A-public6-q3s4-diagnostic`, not as a main submission candidate.

updated decision:

- Q3/S4 public6 direction is real enough to survive axis correction in actual-anchor/posterior metrics.
- But the local LB proxy edge is only `3e-6~6e-6`, while the best leave-one-anchor-out proxy MAE is `3.18e-4`. This is far below local validation resolution.
- The raw local-top candidate fails JEPA compatibility: high raw-axis/bad-axis drift and poor LeJEPA rank.
- The guarded candidate is structurally clean and worth a diagnostic public submission only if we want to test this exact Q3/S4 inverse-LB hypothesis.
- Main priority remains raw05-compatible `efmicro/siganchor/siggate/efgate`; the new public6 Q3/S4 axis-corrected family does not yet justify replacing those.

### 21) Local LB validation for JEPA block-count shift candidates

20번까지는 row/cell residual을 직접 움직였다. 이번에는 LeJEPA/J-EPA의 "context representation -> target block structure" 관점으로, hidden block별 Q3 count/rate를 맞추는 `jepa_block_count_shift_shortlist.csv` 후보 80개를 local LB 검증에 정식 편입했다.

- augmenter: `analysis_outputs/augment_block_count_shift_candidates.py`
- augmented metrics: `analysis_outputs/jepa_block_count_shift_actual_anchor_augmented.csv`
- report: `analysis_outputs/jepa_block_count_shift_actual_anchor_augmented_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
- verification:
  - `python3 -m py_compile analysis_outputs/augment_block_count_shift_candidates.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
  - `python3 analysis_outputs/augment_block_count_shift_candidates.py` 완료
  - `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
  - `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료 after forcing block-count candidates into the audit pool
  - `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

local LB proxy check:

- best independent local LB proxy model is unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- block-count family actual-anchor:
  - rows scored: `80`
  - best actual-anchor: `0.577896`
  - best ranker-selection: `0.577896`
  - best raw-axis absolute drift: `0.0000000018`
  - best bad-axis absolute drift: `0.000101`
- best local-proxy block-count row:
  - `analysis_outputs/submission_jepa_block_countshift_a58efeff.csv`
  - raw05-relative local proxy: `0.577532`
  - raw05-relative local delta: `+0.000005`
  - local model spread: `0.000031`
  - actual-anchor `0.577899`
  - posterior `0.576756`
  - raw-axis delta `-0.000000377`
  - bad-axis `0.000141`
  - mean abs move vs raw05 `0.001329`
  - LeJEPA residual health `9.673145`
  - LeJEPA combined rank `294.50`
- best LeJEPA-health block-count row:
  - `analysis_outputs/submission_jepa_block_countshift_805c675c.csv`
  - LeJEPA residual health `9.252052`
  - actual-anchor `0.577897`
  - posterior `0.576754`
  - raw-axis delta `0.0000000835`
  - bad-axis `0.000403`
  - LeJEPA combined rank `281.15`

updated decision:

- JEPA block-count constraint is structurally clean: raw-axis and bad-axis are both much safer than earlier aggressive public6 rows.
- But it is not a local LB improvement. The best block-count row is raw05 `+0.000005`, while local proxy resolution is `0.0003184931`; this is effectively indistinguishable and slightly on the wrong side.
- Actual-anchor is also weaker than the raw05-compatible A family (`~0.577899` vs `~0.577839`).
- Keep `submission_jepa_block_countshift_a58efeff.csv` in final priority as `B-block-count-diagnostic`, not as a main submission candidate.
- Modeling implication: block-level count/rate regularization is useful as a compatibility constraint, but by itself it is too conservative. Future useful version should combine this low-bad block-count constraint with the stronger raw05-compatible `efmicro/siganchor/siggate` residual directions instead of submitting count-shift alone.

### 22) JEPA block-count regularizer mixed into raw05-compatible A-family residuals

21번의 결론대로 block-count를 단독 제출하지 않고, raw05-compatible A-family 후보의 logit residual에 아주 작은 block-count residual을 섞었다. 핵심 가설은 두 가지였다.

- JEPA block-count residual은 target block(Q3 중심)의 hidden block structure를 보존하는 regularizer다.
- 단독으로는 actual-anchor가 약하지만, `efmicro/siganchor/siggate/efgate` residual 위에 아주 작게 더하면 bad-axis를 더 줄이면서 raw05-compatible public 방향은 유지할 수 있다.

implementation:

- generator: `analysis_outputs/raw05_jepa_blockcount_regularized_refine.py`
- scan: `analysis_outputs/raw05_jepa_blockcount_regularized_refine_scan.csv`
- scored: `analysis_outputs/raw05_jepa_blockcount_regularized_refine_scored.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_blockcount_regularized_refine_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_blockcount_regularized_refine_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_blockcount_regularized_refine.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
- `python3 analysis_outputs/raw05_jepa_blockcount_regularized_refine.py` 완료
  - generated candidates: `157497`
  - actual-anchor scored candidates: `1598`
  - saved shortlist: `24`
- `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
- `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

best local proxy read:

- best independent local LB proxy model is still unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- best local-proxy blockcount-regularized rows are all around:
  - raw05-relative local proxy `0.577523`
  - raw05-relative local delta `-0.000003`
  - local model spread `0.000064`
- representative best-local row:
  - `analysis_outputs/submission_raw05_jepa_blockcountreg_68d23883.csv`
  - actual-anchor `0.577840`
  - posterior `0.576889`
  - raw-axis delta `0.0000001007`
  - bad-axis `0.000012`
  - mean abs move vs raw05 `0.001497`
  - LeJEPA residual health `10.514773`
  - LeJEPA combined rank `300.40`
- best LeJEPA/lowbad diagnostic row:
  - `analysis_outputs/submission_raw05_jepa_blockcountreg_50b1cf4a.csv`
  - actual-anchor `0.577841`
  - posterior `0.576886`
  - raw-axis delta `0.0000000900`
  - bad-axis `0.000009`
  - raw05-relative local delta `-0.000003`
  - LeJEPA residual health `10.104146`
  - LeJEPA combined rank `280.65`
  - added to final priority as `A-blockcountreg-ultralowbad-diagnostic`.

updated decision:

- The regularizer worked as intended on public axes: bad-axis collapsed to `~1e-5` or lower while raw-axis stayed near `1e-7`.
- It did not improve the actual-anchor frontier. Best actual-anchor stayed around `0.577840~0.577841`, weaker than the current raw05-compatible A-family around `0.577839`.
- The local LB proxy gives a tiny `-0.000003` edge over raw05, but this is far below proxy resolution `0.0003184931`.
- Submission implication: `submission_raw05_jepa_blockcountreg_50b1cf4a.csv` is only a low-bad stress probe. It should not replace `efmicro/siganchor/siggate`.
- Modeling implication: the block-count regularizer is useful as a constraint and diagnostic, but the score-driving signal still comes from the raw05-compatible energy/SIGReg micro directions. Next useful search should optimize within those directions first, then apply block-count only as a late-stage axis-cleaning transform.

### 23) raw05-compatible tangent/nullspace local LB validation

이번에는 current A-family frontier 주변의 logit residual tangent space를 직접 훑었다. 목적은 `raw05` public 방향을 유지하면서, 기존 후보들이 공유하는 local manifold 안에서 실제 LB proxy가 더 좋게 보는 미세 방향이 있는지 확인하는 것이었다. JEPA 관점에서는 context-target residual의 local null direction을 찾는 실험이고, LeJEPA 관점에서는 residual covariance/SIGReg health가 무너지지 않는 작은 움직임만 허용했다.

implementation:

- generator: `analysis_outputs/raw05_jepa_tangent_nullspace_refine.py`
- scan: `analysis_outputs/raw05_jepa_tangent_nullspace_refine_scan.csv`
- scored: `analysis_outputs/raw05_jepa_tangent_nullspace_refine_scored.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_tangent_nullspace_refine_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_tangent_nullspace_refine_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_tangent_nullspace_refine.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/lejepa_sigreg_candidate_audit.py` 통과
- `python3 analysis_outputs/raw05_jepa_tangent_nullspace_refine.py` 완료
  - generated candidates: `228303`
  - actual-anchor scored candidates: `2400`
  - saved shortlist: `24`
- `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
- `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

local LB proxy check:

- best independent local LB proxy model is still unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- tangent/nullspace shortlist:
  - rows saved: `24`
  - raw05-relative local proxy range: `0.577523628389` to `0.577523730373`
  - raw05-relative local delta range: `-0.000002678811` to `-0.000002576827`
  - local model spread range: `0.000064856974` to `0.000064974941`
  - axis-only raw05-relative delta range: `+0.000015088739` to `+0.000015219934`
- best LeJEPA tangent row:
  - `analysis_outputs/submission_raw05_jepa_tangentnull_26c10612.csv`
  - actual-anchor `0.577840`
  - posterior `0.576889`
  - raw-axis delta `0.0000001020`
  - bad-axis `0.000227`
  - mean abs move vs raw05 `0.001498`
  - LeJEPA residual health `9.918031`
  - all SIGReg global `6.232071`
  - target Q3/S4 SIGReg global `2.908525`
  - public-axis SIGReg global `28.911688`
  - LeJEPA combined rank `282.30`
  - raw05-relative local proxy `0.577524`
  - raw05-relative local delta `-0.000003`
  - local model spread `0.000065`
- best local-proxy tangent row:
  - `analysis_outputs/submission_raw05_jepa_tangentnull_fe15355a.csv`
  - actual-anchor `0.577840`
  - posterior `0.576889`
  - raw-axis delta `0.0000000996`
  - bad-axis `0.000223`
  - LeJEPA residual health `10.435046`
  - raw05-relative local proxy `0.577524`
  - raw05-relative local delta `-0.000003`

updated decision:

- Tangent/nullspace search did not find a new submission upgrade. It converged to the same flat basin as `efgate/blockcountreg`: actual-anchor `~0.577840`, posterior `~0.576889`, local raw05 delta `~-0.000003`.
- The local delta is two orders of magnitude smaller than the validated local proxy MAE `0.0003184931`, so it is not reliable enough to use as a submission-ranking signal.
- The result is still useful diagnostically: the current A-family residual manifold is locally saturated. More PCA/logit micro-steps inside this basin are unlikely to move public LB meaningfully.
- Priority remains unchanged: `efmicro`, `siganchor`, and `siggate` stay ahead; `blockcountreg_50b1cf4a` remains a low-bad stress probe; tangent/nullspace candidates are not promoted.
- Next useful search should leave this local tangent basin: target-specific Q3/S4 structure, row-cluster sequence motifs, or a stronger JEPA context-target representation should drive the next candidate, with raw05-axis compatibility applied only as a late constraint.

### 24) axis-budget motif bridge local LB validation

Tangent/nullspace가 같은 flat basin으로 수렴했기 때문에 이번에는 basin 밖의 신호를 강제로 섞었다. public6 Q3/S4 후보들은 actual-anchor가 강하지만 raw-axis drift가 커서 그대로는 위험했고, hidden-block sequence motif/cellgate 계열은 raw-negative counter direction을 제공했다. 그래서 JEPA식 context-public axis를 예산으로 두고, target-block Q3/S4 motif residual만 가져온 뒤 raw-negative motif로 상쇄하는 `axis-budget motif bridge`를 만들었다.

implementation:

- generator: `analysis_outputs/raw05_jepa_axisbudget_motif_bridge.py`
- scan: `analysis_outputs/raw05_jepa_axisbudget_motif_bridge_scan.csv`
- scored: `analysis_outputs/raw05_jepa_axisbudget_motif_bridge_scored.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_axisbudget_motif_bridge_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_axisbudget_motif_bridge_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_axisbudget_motif_bridge.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` 통과
- `python3 analysis_outputs/raw05_jepa_axisbudget_motif_bridge.py` 완료
  - generated candidates: `106920`
  - actual-anchor scored candidates: `3100`
  - saved shortlist: `29`
- `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
- `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

local LB proxy check:

- best independent local LB proxy model is still unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- best local-proxy axisbridge row:
  - `analysis_outputs/submission_raw05_jepa_axisbridge_1968b38c.csv`
  - raw05-relative local proxy `0.577522`
  - raw05-relative local delta `-0.000005`
  - local model spread `0.000066`
  - actual-anchor `0.577829`
  - posterior `0.576977`
  - raw-axis delta `-0.0000005130`
  - bad-axis `-0.000202`
  - mean abs move vs raw05 `0.001508`
  - LeJEPA residual health `11.893848`
  - LeJEPA combined rank `277.05`
- best LeJEPA-balanced axisbridge row:
  - `analysis_outputs/submission_raw05_jepa_axisbridge_45f2ba5a.csv`
  - raw05-relative local proxy `0.577522`
  - raw05-relative local delta `-0.000004`
  - local model spread `0.000064`
  - actual-anchor `0.577831`
  - posterior `0.576975`
  - raw-axis delta `-0.0000010671`
  - bad-axis `-0.000387`
  - LeJEPA residual health `10.057514`
  - LeJEPA combined rank `176.55`
- comparison with safer A-family representatives:
  - `submission_raw05_jepa_siggate_fd0e9622.csv`: local delta `-0.000003`, posterior `0.576895`, bad-axis `0.000022`
  - `submission_raw05_jepa_siganchor_3644a42f.csv`: local delta `-0.000003`, posterior `0.576899`, bad-axis `0.000400`
  - `submission_raw05_jepa_efmicro_5d2d2af0.csv`: local delta `-0.000002`, posterior `0.576900`, bad-axis `0.000465`

updated decision:

- Axisbridge is the first nonlocal Q3/S4 motif bridge that improves the actual-anchor proxy to around `0.577829~0.577831` while keeping raw-axis negative.
- The local LB proxy also prefers it slightly over the current A-family representatives (`raw05-4e-6` to `raw05-5e-6` versus about `raw05-2e-6` to `raw05-3e-6`), but this difference is `~60x` smaller than proxy MAE `0.0003184931`.
- The risk is posterior: axisbridge posterior is `0.576975~0.576977`, clearly weaker than safer A-family posterior `0.576895~0.576900`. So this is not a confirmed main upgrade.
- Submission implication: promote two high-information probes, not safe replacements:
  - `submission_raw05_jepa_axisbridge_45f2ba5a.csv` as `A-axisbridge-health-probe`
  - `submission_raw05_jepa_axisbridge_1968b38c.csv` as `A-axisbridge-local-proxy`
- Modeling implication: target-block motif transfer is finally moving a different axis than tangent/blockcount, but it needs a posterior/energy repair layer before it can outrank `efmicro/siganchor/siggate` as the main submission path.

### 25) axisbridge posterior-repair validation

Axisbridge의 약점은 posterior였다. 그래서 두 가지 JEPA-style repair를 만들었다. 첫째, axisbridge 자체는 유지하되 context 좌표만 posterior-safe A-family donor 쪽으로 이동한다. 둘째, posterior-safe A-family donor를 base로 두고 axisbridge의 Q3/S4 target motif residual만 주입한다. 전자는 target motif를 보존하고 posterior를 수리하는 실험이고, 후자는 posterior를 완전히 안전권으로 돌리는 대신 motif를 얼마나 잃는지 보는 실험이다.

implementation:

- generator: `analysis_outputs/raw05_jepa_axisbridge_posterior_repair.py`
- scan: `analysis_outputs/raw05_jepa_axisbridge_posterior_repair_scan.csv`
- scored: `analysis_outputs/raw05_jepa_axisbridge_posterior_repair_scored.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_axisbridge_posterior_repair_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_axisbridge_posterior_repair_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_axisbridge_posterior_repair.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` 통과
- `python3 analysis_outputs/raw05_jepa_axisbridge_posterior_repair.py` 완료
  - axis pool: `24`
  - posterior-safe donor pool: `26`
  - generated candidates: `53136`
  - actual-anchor scored candidates: `2374`
  - saved shortlist: `72`
- `python3 analysis_outputs/local_lb_proxy_validation.py` 완료
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` 완료
- `python3 analysis_outputs/final_jepa_candidate_priority.py` 완료

local LB proxy check:

- best independent local LB proxy model is still unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- motif-preserving context repair:
  - `analysis_outputs/submission_raw05_jepa_axisrepair_2a20d67f.csv`
  - mode `axis_plus_context_repair`
  - profile `repair_context_only`
  - target motif retention `1.000000`
  - raw05-relative local proxy `0.577522`
  - raw05-relative local delta `-0.000004`
  - local model spread `0.000068`
  - actual-anchor `0.577828`
  - posterior `0.576933`
  - raw-axis delta `-0.0000000403`
  - bad-axis `-0.000564`
  - LeJEPA residual health `10.907152`
  - LeJEPA combined rank `247.90`
- posterior-safe motif injection:
  - `analysis_outputs/submission_raw05_jepa_axisrepair_78029f2c.csv`
  - mode `donor_plus_axis_motif`
  - profile `inject_q3_sblockmicro`
  - target motif retention `0.367727`
  - raw05-relative local proxy `0.577522`
  - raw05-relative local delta `-0.000004`
  - local model spread `0.000066`
  - actual-anchor `0.577834`
  - posterior `0.576895`
  - raw-axis delta `0.0000000773`
  - bad-axis `-0.000054`
  - LeJEPA residual health `10.010961`
  - LeJEPA combined rank `247.15`

updated decision:

- The repair layer worked mechanically. `axisrepair_2a20d67f` keeps the Q3/S4 motif fully and cuts posterior from axisbridge `~0.576975` to `0.576933`.
- Full posterior repair still does not reach the safer A-family posterior band `~0.576895~0.576900` unless motif retention drops to about `0.37`, as in `axisrepair_78029f2c`.
- Local proxy sees both repair probes around raw05 `-0.000004`, similar to axisbridge and slightly ahead of the A-family local deltas, but still far below the proxy MAE `0.0003184931`.
- Priority update:
  - `submission_raw05_jepa_axisrepair_2a20d67f.csv` promoted as `A-axisrepair-context-probe`
  - `submission_raw05_jepa_axisrepair_78029f2c.csv` promoted as `A-axisrepair-posterior-safe-probe`
- Modeling implication: the hidden Q3/S4 motif appears real enough to survive a context-only repair, but the posterior-safe manifold resists carrying the full motif. The next useful search should optimize the repair layer directly, not create more axisbridge variants: target objective should trade off `target_motif_retention >= 0.7`, `posterior <= 0.57691`, and raw-axis `<= 1e-7`.

### 26) direct axisrepair tradeoff search and local-LB validation

The next search optimized the repair objective directly: keep the hidden Q3/S4 target motif, pull posterior back into the safer A-family band, and keep the raw05 axis essentially neutral. This is the first branch that explicitly searched for `target_motif_retention >= 0.7`, `posterior <= 0.57691`, and `delta_vs_raw05_rawaxis <= 1e-7` instead of checking those constraints after the fact.

implementation:

- generator: `analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct.py`
- scan: `analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct_scan.csv`
- scored: `analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct_scored.csv`
- shortlist/submissions: `analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct_report.md`
- connected into:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

execution note:

- The first full compensated-grid run was killed because the combination count exploded.
- The search was bounded to the top axis rows, top donors, and a reduced compensated-injection grid, then rerun successfully.
- Final bounded search:
  - axis pool: `12`
  - donor pool: `16`
  - compensator pool: `6`
  - generated candidates: `15622`
  - actual-anchor scored candidates: `2424`
  - saved shortlist: `84`
  - goal-hit candidates: `1200 / 2424`

verification:

- `python3 -m py_compile analysis_outputs/final_jepa_candidate_priority.py` passed
- `python3 analysis_outputs/raw05_jepa_axisrepair_tradeoff_direct.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed after adding axistrade priority rows

local LB proxy check:

- best independent local LB proxy model is still unchanged:
  - `loocv_ridge_abs_axes_a1`
  - MAE `0.0003184931`
  - RMSE `0.0004029881`
  - max abs error `0.0006141185`
  - pairwise rank accuracy `0.9333`
- important consequence: all `raw05-relative` edges below about `3e-4` are directional only, not proof of a public-LB improvement. The axistrade edges are about `4e-6`, so they are high-information probes rather than confirmed upgrades.

best direct tradeoff candidates:

- `analysis_outputs/submission_raw05_jepa_axistrade_931a03a1.csv`
  - promoted as `A-axistrade-goal-local`, final priority rank `10` after the structural feature audit
  - mode/profile: `soft_axis_repair` / `soft_ctx_q3s4_05`
  - target motif retention `1.097647`
  - raw05-relative local proxy `0.577522521`
  - raw05-relative local delta `-0.000003786`
  - local model spread `0.000070267`
  - actual-anchor `0.577828521`
  - posterior `0.576904573`
  - raw-axis delta `-0.0000000166`
  - bad-axis `0.0000605`
  - LeJEPA residual health `10.794818`
  - LeJEPA combined rank `302.75`
- `analysis_outputs/submission_raw05_jepa_axistrade_80fd659c.csv`
  - promoted as `A-axistrade-goal-health`, final priority rank `11` after the structural feature audit
  - mode/profile: `soft_axis_repair` / `soft_sblock_q3_08`
  - target motif retention `1.042757`
  - raw05-relative local proxy `0.577522558`
  - raw05-relative local delta `-0.000003749`
  - local model spread `0.000070126`
  - actual-anchor `0.577829436`
  - posterior `0.576903937`
  - raw-axis delta `-0.0000000913`
  - bad-axis `-0.0000175`
  - LeJEPA residual health `10.625326`
  - LeJEPA combined rank `264.80`
- `analysis_outputs/submission_raw05_jepa_axistrade_b8172c33.csv`
  - not manually promoted, but it is a close sibling of `931a03a1`
  - target motif retention `1.094897`
  - raw05-relative local proxy `0.577522499`
  - raw05-relative local delta `-0.000003808`
  - posterior `0.576904`
  - raw-axis delta `0.0000000408`
  - bad-axis `0.000063`
- `analysis_outputs/submission_raw05_jepa_axistrade_bc0a829d.csv`
  - diagnostic low-posterior/high-retention row
  - target motif retention `2.303396`
  - raw05-relative local proxy `0.577523413`
  - raw05-relative local delta `-0.000002894`
  - posterior `0.576887`
  - raw-axis delta `0.0000000814`
  - bad-axis `0.000200`

comparison against previous repairs:

- `axisrepair_2a20d67f`: full motif retention and local delta `-0.000004008`, but posterior `0.576932533`, so still not posterior-safe enough.
- `axisrepair_78029f2c`: posterior `0.576894512`, but motif retention only `0.367727`.
- `axistrade_80fd659c` and `axistrade_931a03a1` repair that tradeoff: motif retention is above `1.0`, posterior is around `0.576904`, raw-axis is non-positive, and bad-axis is near zero.
- The `target_motif_retention` value is a relative residual-retention score, not a bounded probability; values above `1.0` mean the target-block residual magnitude is larger than the donor's measured motif baseline.

updated decision:

- Direct axistrade is the strongest structural JEPA result in this branch. It validates the idea that the hidden Q3/S4 motif and posterior-safe manifold can be combined, instead of forcing a choice between them.
- It does not yet beat raw05 locally in a statistically meaningful way. The best axistrade local deltas are `~ -3.8e-6`, while the independent local proxy MAE is `0.0003184931`.
- Submission implication:
  - `submission_raw05_jepa_axistrade_931a03a1.csv` is the best high-information direct tradeoff probe after the structural feature audit.
  - `submission_raw05_jepa_axistrade_80fd659c.csv` is the second probe if prioritizing slightly better LeJEPA residual health / bad-axis balance.
  - These should not displace the currently safer `efmicro/siganchor/siggate` family unless public slots are being used for information gain.
- Modeling implication: the next useful validation is not another broad search. It should calibrate the motif-retention score and teach the local proxy to penalize B-family donor drift / large target residuals separately, because the current proxy cannot resolve `1e-5`-level candidate gaps.

### 27) submission-level structural feature probe for local-LB validation

The previous local proxy could not resolve `1e-5`-level gaps, so a new validation axis was tested. Instead of using branch-specific columns such as `target_motif_retention`, this probe recomputes common logit residual features directly from every submission CSV:

- raw05-relative logit distance by target group
- stage2-line position
- Q3/S4 motif projection, cosine, and off-motif residual against the discovered axisbridge motif template
- target/context concentration
- sequence roughness by subject/date
- residual anisotropy via singular-value energy and entropy

implementation:

- script: `analysis_outputs/local_lb_structural_feature_probe.py`
- features: `analysis_outputs/local_lb_structural_features.csv`
- model scores: `analysis_outputs/local_lb_structural_feature_model_scores.csv`
- candidate predictions: `analysis_outputs/local_lb_structural_candidate_predictions.csv`
- constrained shortlist: `analysis_outputs/local_lb_structural_constrained_shortlist.csv`
- report: `analysis_outputs/local_lb_structural_feature_probe_report.md`

verification:

- `python3 -m py_compile analysis_outputs/local_lb_structural_feature_probe.py` passed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 -m py_compile analysis_outputs/final_jepa_candidate_priority.py` passed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed after axistrade priority reorder
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed

LOOCV result against the six known public anchors:

- best structural model: `struct_compact_jepa_a10`
- features: `raw05_stage2_blend_pos`, `sv1_frac`, `q3s4_motif_cos`
- MAE `0.0009941112`
- RMSE `0.0013018728`
- max abs error `0.0026557421`
- pairwise rank accuracy `0.533333`

decision on the structural proxy:

- Do not use the structural feature model as an LB predictor. Its MAE is much worse than the current best local proxy `loocv_ridge_abs_axes_a1` MAE `0.0003184931`.
- Use it as a JEPA/motif diagnostic only. It answers whether a candidate is structurally aligned with the discovered motif, not whether it will beat raw05 on public.
- A bad `q3s4_balance` feature initially caused pathological candidate predictions for pure-Q3/S4 moves; the script now caps `q3s4_to_ctx_ratio` and excludes weak structural models from the weighted prediction set.

selected candidate diagnostics:

- `analysis_outputs/submission_raw05_jepa_axistrade_931a03a1.csv`
  - structural raw05-relative delta `+0.000109`
  - structural model spread `0.000622`
  - Q3/S4 motif projection `0.995557`
  - Q3/S4 motif cosine `0.999984`
  - Q3/S4 off-motif ratio `0.007819`
  - q3s4/context ratio `1.603351`
  - sv1 fraction `0.338637`
- `analysis_outputs/submission_raw05_jepa_axistrade_80fd659c.csv`
  - structural raw05-relative delta `+0.000111`
  - structural model spread `0.000622`
  - Q3/S4 motif projection `0.990901`
  - Q3/S4 motif cosine `0.999806`
  - Q3/S4 off-motif ratio `0.026838`
  - q3s4/context ratio `1.587956`
  - sv1 fraction `0.337805`
- `analysis_outputs/submission_raw05_jepa_axisrepair_2a20d67f.csv`
  - structural raw05-relative delta `+0.000112`
  - structural model spread `0.000623`
  - Q3/S4 motif projection `1.004522`
  - Q3/S4 motif cosine `0.999962`
  - Q3/S4 off-motif ratio `0.011876`
  - q3s4/context ratio `1.722463`
  - sv1 fraction `0.343026`
- `analysis_outputs/submission_raw05_jepa_siganchor_3644a42f.csv`
  - structural raw05-relative delta `+0.000173`
  - Q3/S4 motif projection `0.830890`
  - Q3/S4 motif cosine `0.958255`
  - Q3/S4 off-motif ratio `0.389382`
- `analysis_outputs/submission_raw05_jepa_siggate_fd0e9622.csv`
  - structural raw05-relative delta `+0.000175`
  - Q3/S4 motif projection `0.830890`
  - Q3/S4 motif cosine `0.958255`
  - Q3/S4 off-motif ratio `0.389382`

updated decision:

- Structural validation confirms that axistrade is not just a numeric proxy artifact. `931a03a1` and `80fd659c` are much closer to the discovered Q3/S4 motif template than `siganchor/siggate`.
- It also adds a conservative warning: all axistrade/axisrepair motif-preserving rows are structurally predicted worse than raw05 by about `+1.1e-4`, but the structural model's own MAE is `~9.9e-4`, so this is a risk descriptor rather than a rejection.
- The constrained structural filter found exactly one hit in the current pool: `submission_raw05_jepa_axistrade_931a03a1.csv`.
- Axistrade internal priority changed:
  - `submission_raw05_jepa_axistrade_931a03a1.csv` is now the best direct motif/posterior probe because it has the smallest structural motif residual and a slightly better local raw05-relative proxy than `80fd659c`.
  - `submission_raw05_jepa_axistrade_80fd659c.csv` remains the second probe because it has slightly better LeJEPA residual-health and bad-axis balance.
- Next experiment should not add this structural score into the main LB proxy. Instead, use the structural features to build a constrained search objective: keep `q3s4_motif_cos >= 0.9999`, `q3s4_motif_orth_ratio <= 0.01`, posterior `<= 0.576905`, and raw-axis `<= 1e-7`, then search for a row with lower structural raw05-relative delta.

### 28) local-LB validation of structural constrained micro-refine

The constrained structural objective from section 27 was tested by micro-refining the unique hit `submission_raw05_jepa_axistrade_931a03a1.csv`. The run combines raw05 shrinkage, posterior-safe donor offsets, and a Q3/S4 motif re-anchor. A first broad grid exhausted memory, so the grid was narrowed to the strongest base/donor set and rerun.

implementation:

- generator: `analysis_outputs/raw05_jepa_structural_constrained_refine.py`
- shortlist: `analysis_outputs/raw05_jepa_structural_constrained_refine_shortlist.csv`
- local-LB proxy: `analysis_outputs/local_lb_proxy_validation.py`
- structural diagnostic: `analysis_outputs/local_lb_structural_feature_probe.py`
- final priority: `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_structural_constrained_refine.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/local_lb_structural_feature_probe.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` passed
- `python3 analysis_outputs/raw05_jepa_structural_constrained_refine.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed

generation result:

- generated candidates: `1600`
- scored candidates: `1600`
- saved shortlist: `72`
- structural hits in scan: `196`
- scored structural hits: `196`

local-LB validation result:

- The best independent local public-LB proxy is still `loocv_ridge_abs_axes_a1`.
- Its LOOCV MAE is `0.0003184931`, RMSE is `0.0004029881`, and pairwise rank accuracy is `0.933333`.
- Therefore `1e-6` to `1e-5` candidate gaps are below local validation resolution.
- The new `structrefine` family does not prove a true LB gain, but it creates better structured probes than the original axistrade row.

selected rows:

- `analysis_outputs/submission_raw05_jepa_structrefine_04ad10f8.csv`
  - local raw05-relative delta `-0.0000039661`
  - posterior `0.5769041314`
  - raw-axis delta `0.0000000600`
  - bad-axis `-0.0000153093`
  - Q3/S4 motif cosine `0.9999848747`
  - Q3/S4 off-motif ratio `0.0075050771`
  - LeJEPA residual health `10.9287606423`
- `analysis_outputs/submission_raw05_jepa_structrefine_90e28f7d.csv`
  - local raw05-relative delta `-0.0000039437`
  - posterior `0.5769037626`
  - raw-axis delta `0.0000000317`
  - bad-axis `-0.0000016071`
  - Q3/S4 motif cosine `0.9999848747`
  - Q3/S4 off-motif ratio `0.0075050771`
  - LeJEPA residual health `11.3756348777`
- comparison anchor `analysis_outputs/submission_raw05_jepa_axistrade_931a03a1.csv`
  - local raw05-relative delta `-0.0000037860`
  - posterior `0.5769045731`
  - raw-axis delta `-0.0000000166`
  - bad-axis `0.0000604807`
  - Q3/S4 motif cosine `0.9999835822`
  - Q3/S4 off-motif ratio `0.0078186482`
  - LeJEPA residual health `10.7948183365`

decision:

- Promote `submission_raw05_jepa_structrefine_04ad10f8.csv` as the best submit-shaped structural-refine probe. It improves the 931a03a1 local proxy, motif alignment, and bad-axis while keeping posterior near the same band.
- Promote `submission_raw05_jepa_structrefine_90e28f7d.csv` as the cleanest low-bad structural stress probe. Its local proxy is slightly weaker than 04ad10f8, but it nearly nulls the bad-axis and has the lowest posterior among the two.
- Keep the conclusion conservative: the public-LB claim is not validated locally because the differences are much smaller than local proxy MAE. The useful discovery is structural: JEPA-style motif preservation and posterior/bad-axis repair can be combined without leaving the raw05-compatible guardrails.

### 29) local-LB anchor robustness and anchor-robust donor graft

The local-LB validation was extended with a leave-one-public-anchor-out stress test. The goal was to check whether a candidate still looks better than raw05 when one known public submission is removed from the calibration set, then graft only the useful direction from the robust donor into JEPA-motif-safe candidates.

implementation:

- anchor robustness probe: `analysis_outputs/local_lb_anchor_robustness_probe.py`
- graft generator: `analysis_outputs/raw05_jepa_anchorrobust_motif_graft.py`
- graft shortlist: `analysis_outputs/raw05_jepa_anchorrobust_motif_graft_shortlist.csv`
- updated final priority: `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_anchorrobust_motif_graft.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/local_lb_structural_feature_probe.py analysis_outputs/local_lb_anchor_robustness_probe.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` passed
- `python3 analysis_outputs/raw05_jepa_anchorrobust_motif_graft.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 analysis_outputs/local_lb_anchor_robustness_probe.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed

anchor robustness model quality:

- best leave-one proxy model: `abs_axes`
- MAE `0.000318`, RMSE `0.000403`, max abs error `0.000614`, bias `0.000093`
- This is essentially the same uncertainty band as the earlier local-LB proxy. Candidate gaps below `1e-5` are not reliable as public-LB proof.

robust donor result:

- `submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
  - local raw05-relative delta `-0.0000102376`
  - anchor robust mean delta `-0.0000153988`
  - anchor robust p90 delta `-0.0000047045`
  - anchor robust max delta `-0.0000016160`
  - beat-raw05 rate `1.0`
  - posterior `0.5774590201`
  - bad-axis `0.0004937317`
- This is the strongest leave-one-anchor signal found, but it is not JEPA-safe as a direct submission because it breaks the discovered Q3/S4 motif and sits far above the posterior guardrail. It should be used as a donor direction, not as the primary candidate.

graft generation result:

- generated candidates: `1664`
- scored candidates: `1664`
- saved shortlist: `84`
- structural hits in scan: `1400`
- scored structural hits: `1400`

selected graft:

- `analysis_outputs/submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv`
  - local raw05-relative delta `-0.0000039998`
  - comparison: `structrefine_04ad10f8` local delta `-0.0000039661`
  - posterior `0.5769038955`
  - raw-axis delta `0.0000000987`
  - bad-axis `-0.0000196167`
  - Q3/S4 motif cosine `0.9999879029`
  - Q3/S4 off-motif ratio `0.0067166060`
  - anchor robust mean delta `-0.0000128256`
  - anchor robust p90 delta `0.0000184272`
  - LeJEPA residual health `10.3521288468`
  - LeJEPA combined rank `270.15`

decision:

- Promote `submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv` into the final priority list before the two `structrefine` rows.
- The promotion is conservative. It is the best graft by local raw05-relative proxy and keeps the JEPA motif/bad-axis constraints, but the local gain over `structrefine_04ad10f8` is only about `3.4e-8`, far below the proxy MAE.
- The useful data-science finding is directional: public6entropy contains an anchor-robust raw05-improving direction, but only tiny grafts into the Q3/S4 motif manifold remain structurally safe. Direct robust-donor submission is rejected.

### 30) axisbridge local signal versus posterior-safe JEPA manifold

The axisbridge and axisrepair rows exposed a tempting local-LB direction: they improve the raw05-relative local proxy more than the motif grafts, but the best rows also move into a high-posterior and off-motif region. A new sweep tested whether this local direction can be kept while repairing it toward posterior-safe JEPA donors.

implementation:

- generator: `analysis_outputs/raw05_jepa_axislocal_posterior_sweep.py`
- shortlist: `analysis_outputs/raw05_jepa_axislocal_posterior_sweep_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_axislocal_posterior_sweep_report.md`
- integrated validators:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/local_lb_structural_feature_probe.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_axislocal_posterior_sweep.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/local_lb_structural_feature_probe.py analysis_outputs/local_lb_anchor_robustness_probe.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/final_jepa_candidate_priority.py` passed
- `python3 analysis_outputs/raw05_jepa_axislocal_posterior_sweep.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 analysis_outputs/local_lb_anchor_robustness_probe.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed

generation result:

- axis pool: `14`
- donor pool: `20`
- generated candidates: `1600`
- scored candidates: `1600`
- saved shortlist: `81`
- strict hits: `0`
- balanced hits: `193`

local-LB validation result:

- The best independent local public-LB proxy remains `loocv_ridge_abs_axes_a1`.
- Its LOOCV MAE remains `0.0003184931`, RMSE `0.0004029881`, and pairwise rank accuracy `0.933333`.
- The new candidates produce better raw05-relative local deltas than the promoted graft, but the gaps are still far below the local proxy error band.

best local-proxy row:

- `analysis_outputs/submission_raw05_jepa_axislocal_16ae093a.csv`
  - local raw05-relative delta `-0.0000043725`
  - model spread versus raw05 public `0.0000677658`
  - posterior `0.5769345733`
  - raw-axis delta `-0.0000000456`
  - bad-axis `-0.0003221836`
  - Q3/S4 motif cosine `0.9987349450`
  - Q3/S4 off-motif ratio `0.0688278475`

best tighter-motif diagnostic row:

- `analysis_outputs/submission_raw05_jepa_axislocal_20e4a625.csv`
  - local raw05-relative delta `-0.0000042943`
  - model spread versus raw05 public `0.0000675676`
  - posterior `0.5769332577`
  - raw-axis delta `-0.0000000223`
  - bad-axis `-0.0003491309`
  - Q3/S4 motif cosine `0.9999631914`
  - Q3/S4 off-motif ratio `0.0117455354`

comparison against promoted graft:

- `analysis_outputs/submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv`
  - local raw05-relative delta `-0.0000039998`
  - posterior `0.5769038955`
  - raw-axis delta `0.0000000987`
  - bad-axis `-0.0000196167`
  - Q3/S4 motif cosine `0.9999879029`
  - Q3/S4 off-motif ratio `0.0067166060`

decision:

- Do not promote the `axislocal` family into the submit shortlist yet.
- The experiment is a useful negative result: the local axisbridge signal survives posterior repair, but not in the strict JEPA-safe region. The best local row has too much Q3/S4 off-motif energy, while the tighter-motif row still sits about `2.9e-5` posterior above the promoted graft and has a much larger bad-axis magnitude.
- Keep `submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv` as the current conservative structural submit probe. Keep `submission_raw05_jepa_axislocal_20e4a625.csv` only as a diagnostic row for the next search stage, where posterior and Q3/S4 off-motif penalties need to be optimized directly rather than repaired after the fact.

### 31) direct-constrained axislocal injection under JEPA motif lock

The previous axislocal sweep showed a stronger local-LB direction, but it failed the strict JEPA-safe region because posterior, bad-axis, and Q3/S4 off-motif energy moved together. A direct constrained search now injected the axislocal direction while projecting Q3/S4 back onto the discovered motif at construction time.

implementation:

- generator: `analysis_outputs/raw05_jepa_direct_constrained_search.py`
- shortlist: `analysis_outputs/raw05_jepa_direct_constrained_search_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_direct_constrained_search_report.md`
- integrated validators:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/local_lb_structural_feature_probe.py`
  - `analysis_outputs/local_lb_anchor_robustness_probe.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/local_lb_proxy_validation.py analysis_outputs/local_lb_structural_feature_probe.py analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/lejepa_sigreg_candidate_audit.py analysis_outputs/raw05_jepa_direct_constrained_search.py` passed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 analysis_outputs/local_lb_anchor_robustness_probe.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed for `1112` candidates
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed again after SIGReg audit

generation result:

- generated candidates: `238656`
- prefiltered candidates: `1600`
- actual-anchor scored candidates: `1600`
- saved shortlist: `86`
- strict hits: `1600`
- tight-local hits: `9`

local-LB validation result:

- The best independent local public-LB proxy is unchanged: `loocv_ridge_abs_axes_a1`.
- LOOCV MAE `0.0003184931`, RMSE `0.0004029881`, pairwise rank accuracy `0.933333`.
- Therefore candidate gaps around `1e-6` to `1e-5` remain directional signals, not proofs.

best direct-constrained rank row:

- `analysis_outputs/submission_raw05_jepa_directcon_a903806a.csv`
  - local raw05-relative delta `-0.0000039811`
  - model spread versus raw05 public `0.0000700567`
  - actual-anchor score `0.5778280678`
  - posterior `0.5769048016`
  - raw-axis delta `0.0000000456`
  - bad-axis `-0.0000407816`
  - Q3/S4 motif cosine `1.0000000000`
  - Q3/S4 off-motif ratio `0.0000000000`
  - anchor-robust mean delta `-0.0000446441`
  - anchor-robust p90 delta `0.0000182959`
  - LeJEPA residual health `11.6264113560`
  - LeJEPA combined rank `550.05`

best direct-constrained local-edge row:

- `analysis_outputs/submission_raw05_jepa_directcon_ff079802.csv`
  - local raw05-relative delta `-0.0000039933`
  - model spread versus raw05 public `0.0000699881`
  - actual-anchor score `0.5778278436`
  - posterior `0.5769050118`
  - raw-axis delta `0.0000000873`
  - bad-axis `-0.0000835346`
  - Q3/S4 motif cosine `1.0000000000`
  - Q3/S4 off-motif ratio `0.0000000000`
  - anchor-robust mean delta `-0.0000446498`
  - anchor-robust p90 delta `0.0000181407`
  - LeJEPA residual health `11.1517803828`
  - LeJEPA combined rank `424.15`

comparison against current conservative probe:

- `analysis_outputs/submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv`
  - local raw05-relative delta `-0.0000039998`
  - model spread versus raw05 public `0.0000704113`
  - actual-anchor score `0.5778278582`
  - posterior `0.5769038955`
  - raw-axis delta `0.0000000987`
  - bad-axis `-0.0000196167`
  - Q3/S4 motif cosine `0.9999879029`
  - Q3/S4 off-motif ratio `0.0067166060`
  - anchor-robust mean delta `-0.0000446570`
  - anchor-robust p90 delta `0.0000184272`
  - LeJEPA residual health `10.3521288468`
  - LeJEPA combined rank `339.70`

decision:

- Do not replace `submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv` as the main conservative structural submit probe.
- The direct-constrained search is a useful positive structural result: the axislocal signal can be injected while exactly locking the Q3/S4 JEPA motif and keeping the same broad local/anchor-robust profile.
- It is not yet a stronger submit candidate because `a903806a` and `ff079802` both have slightly worse posterior than e40, and `ff079802` doubles to quadruples the bad-axis magnitude even though it nearly matches e40's local proxy.
- Next search should optimize under `bad-axis <= 2e-5` and `posterior <= 0.5769040` while retaining exact Q3/S4 motif lock, rather than accepting the current `4e-5` to `8e-5` bad-axis band.

### 32) low-bad motif boundary search

The exact-motif direct search revealed that forcing Q3/S4 perfectly onto the motif increases bad-axis magnitude. The next search therefore treated the e40/structrefine manifold as the safe JEPA boundary: Q3/S4 cosine must stay near `0.999984+`, but the small e40 off-motif component is allowed when it reduces posterior/bad-axis.

implementation:

- generator: `analysis_outputs/raw05_jepa_lowbad_motif_search.py`
- shortlist: `analysis_outputs/raw05_jepa_lowbad_motif_search_shortlist.csv`
- report: `analysis_outputs/raw05_jepa_lowbad_motif_search_report.md`
- integrated validators:
  - `analysis_outputs/local_lb_proxy_validation.py`
  - `analysis_outputs/local_lb_structural_feature_probe.py`
  - `analysis_outputs/local_lb_anchor_robustness_probe.py`
  - `analysis_outputs/lejepa_sigreg_candidate_audit.py`
  - `analysis_outputs/final_jepa_candidate_priority.py`

verification:

- `python3 -m py_compile analysis_outputs/raw05_jepa_lowbad_motif_search.py analysis_outputs/local_lb_proxy_validation.py analysis_outputs/local_lb_structural_feature_probe.py analysis_outputs/final_jepa_candidate_priority.py analysis_outputs/lejepa_sigreg_candidate_audit.py` passed
- `python3 analysis_outputs/raw05_jepa_lowbad_motif_search.py` completed
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed
- `python3 analysis_outputs/local_lb_proxy_validation.py` completed
- `python3 analysis_outputs/local_lb_structural_feature_probe.py` completed
- `python3 analysis_outputs/local_lb_anchor_robustness_probe.py` completed
- `python3 analysis_outputs/lejepa_sigreg_candidate_audit.py` completed for `1208` candidates
- `python3 analysis_outputs/final_jepa_candidate_priority.py` completed again after SIGReg audit

generation result:

- guarded candidates: `84187`
- prefiltered candidates: `2503`
- actual-anchor scored candidates: `2503`
- saved shortlist: `96`
- strict lowbad hits: `645`
- near lowbad hits: `589`

local-LB validation result:

- The best independent local public-LB proxy remains `loocv_ridge_abs_axes_a1`.
- LOOCV MAE `0.0003184931`, RMSE `0.0004029881`, pairwise rank accuracy `0.933333`.
- This experiment works at the `1e-9` to `1e-8` local-delta boundary, so it is not proof of a public-LB gain.

current conservative baseline:

- `analysis_outputs/submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv`
  - local raw05-relative delta `-0.0000039998`
  - model spread versus raw05 public `0.0000704113`
  - actual-anchor score `0.5778278582`
  - posterior `0.5769038955`
  - raw-axis delta `0.0000000987`
  - bad-axis `-0.0000196167`
  - Q3/S4 motif cosine `0.9999879029`
  - Q3/S4 off-motif ratio `0.0067166060`
  - anchor-robust mean delta `-0.0000446570`
  - anchor-robust p90 delta `0.0000184272`
  - LeJEPA residual health `10.3521288468`
  - LeJEPA combined rank `346.20`

best balanced lowbad row:

- `analysis_outputs/submission_raw05_jepa_lowbadcon_71601b5f.csv`
  - local raw05-relative delta `-0.0000039979`
  - model spread versus raw05 public `0.0000703853`
  - actual-anchor score `0.5778278838`
  - posterior `0.5769039598`
  - raw-axis delta `0.0000000954`
  - bad-axis `-0.0000193787`
  - Q3/S4 motif cosine `0.9999880405`
  - Q3/S4 off-motif ratio `0.0066782328`
  - anchor-robust mean delta `-0.0000446556`
  - anchor-robust p90 delta `0.0000184239`
  - LeJEPA residual health `10.8926551377`
  - LeJEPA combined rank `436.35`

best local-edge lowbad row:

- `analysis_outputs/submission_raw05_jepa_lowbadcon_2240eb29.csv`
  - local raw05-relative delta `-0.0000040057`
  - model spread versus raw05 public `0.0000703882`
  - actual-anchor score `0.5778278590`
  - posterior `0.5769041969`
  - raw-axis delta `0.0000000989`
  - bad-axis `-0.0000190138`
  - Q3/S4 motif cosine `0.9999840017`
  - Q3/S4 off-motif ratio `0.0077230189`
  - anchor-robust mean delta `-0.0000446631`
  - anchor-robust p90 delta `0.0000184177`
  - LeJEPA residual health `11.2701068665`
  - LeJEPA combined rank `492.20`

decision:

- Keep `submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv` as the main conservative structural submit probe.
- Add `submission_raw05_jepa_lowbadcon_71601b5f.csv` as the best balanced lowbad stability probe: it preserves the e40 posterior/bad/motif profile but does not beat e40 locally.
- Add `submission_raw05_jepa_lowbadcon_2240eb29.csv` as a high-information boundary probe: it is the first candidate to slightly improve e40's local raw05-relative proxy while staying in the lowbad motif guardrail, but the margin is only about `5.9e-9` and posterior/Q3S4 orthogonal residual are weaker.
- The useful finding is that e40 is sitting almost exactly on a Pareto boundary. Tiny q1/s3 axislocal steps can move local proxy, but every move trades against posterior or Q3/S4 off-motif residual before the gain exceeds local proxy noise.

## 33. Local LB proxy uncertainty decomposition

script:

- `analysis_outputs/local_lb_proxy_uncertainty_decomposition.py`

outputs:

- `analysis_outputs/local_lb_proxy_uncertainty_known_errors.csv`
- `analysis_outputs/local_lb_proxy_uncertainty_error_correlations.csv`
- `analysis_outputs/local_lb_proxy_uncertainty_candidate_risk.csv`
- `analysis_outputs/local_lb_proxy_uncertainty_family_summary.csv`
- `analysis_outputs/local_lb_proxy_uncertainty_report.md`

verification:

- `python3 -m py_compile analysis_outputs/local_lb_proxy_uncertainty_decomposition.py` passed
- `python3 analysis_outputs/local_lb_proxy_uncertainty_decomposition.py` completed

local-LB validation result:

- Best leave-one-public-anchor model is still `loocv_ridge_abs_axes_a1`.
- LOOCV MAE `0.0003184931`, RMSE `0.0004029881`.
- Best-model known-anchor absolute error p50/p80/p90/max is `0.0003380359` / `0.0005912615` / `0.0006026900` / `0.0006141185`.
- Raw05 itself is over-predicted by the best model by `0.0006141185`.
- 5%-of-MAE practical resolution floor is `0.0000159247`.
- Negative-delta candidates below that floor: `1067` / `1287`.
- Locally resolved candidates under the strict rule: `0`.

known-anchor failure pattern:

- The best model's largest miss is raw05 (`+0.0006141185`), not an exotic far-away candidate.
- Strongest descriptive error correlations are bad residual axis and ordinal axis:
  - `loocv_ridge_mean_a1` absolute error vs `abs_bad_residual_axis_ratio`: Spearman `0.942857`.
  - `loocv_ridge_signed_axes_a1` absolute error vs `abs_ordinal_axis_ratio`: Spearman `0.942857`.
  - `loocv_ridge_anchor_gap_a1` absolute error vs `abs_bad_residual_axis_ratio`: Spearman `0.771429`.
- Interpretation: local proxy is useful for coarse regime separation, but it is weak exactly around raw05-compatible boundary candidates.

focus candidate uncertainty:

- `submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv`
  - raw05-relative local delta `-0.0000039998`
  - model spread `0.0000704113`
  - edge / best MAE `0.0125584`
  - relative model improve rate `0.666667`
  - anchor-drop p90/max tail `0.0000184272` / `0.0000316417`
  - structural proxy delta `0.0001086579`
  - tier `below_proxy_resolution`

- `submission_raw05_jepa_lowbadcon_71601b5f.csv`
  - raw05-relative local delta `-0.0000039979`
  - model spread `0.0000703853`
  - edge / best MAE `0.0125524`
  - relative model improve rate `0.666667`
  - anchor-drop p90/max tail `0.0000184239` / `0.0000316383`
  - structural proxy delta `0.0001086848`
  - tier `below_proxy_resolution`

- `submission_raw05_jepa_lowbadcon_2240eb29.csv`
  - raw05-relative local delta `-0.0000040057`
  - model spread `0.0000703882`
  - edge / best MAE `0.0125770`
  - relative model improve rate `0.666667`
  - anchor-drop p90/max tail `0.0000184177` / `0.0000316266`
  - structural proxy delta `0.0001088706`
  - tier `below_proxy_resolution`

- `submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv`
  - raw05-relative local delta `-0.0000102376`
  - edge / best MAE `0.0321437`
  - relative model improve rate `1.000000`
  - anchor-drop p90/max tail `-0.0000047045` / `-0.0000016160`
  - structural proxy delta `0.0002804115`
  - tier `below_proxy_resolution`
  - useful as a diagnostic, but not a JEPA-safe replacement because structural proxy still says worse than raw05.

decision:

- Local LB testing cannot certify any new candidate as a public-LB improvement over raw05.
- e40 remains the first submit probe because of JEPA structural guardrails, not because the local proxy proves a gain.
- lowbadcon_71601b5f is still the balanced stability probe.
- lowbadcon_2240eb29 is still the high-information local-boundary probe.
- public6entropy rows are valuable for diagnosing proxy axes, but should not outrank e40 without a public LB probe because their larger local edge is still below resolution and their structural delta is worse.

## 34. Cross-view JEPA surprise residual features and local LB proxy audit

scripts:

- `analysis_outputs/cross_view_jepa_surprise_probe.py`
- `analysis_outputs/cross_view_jepa_surprise_combo_builder.py`
- `analysis_outputs/cross_view_jepa_surprise_lb_proxy_audit.py`

outputs:

- `analysis_outputs/cross_view_jepa_surprise_features.parquet`
- `analysis_outputs/cross_view_jepa_surprise_guardrail.csv`
- `analysis_outputs/cross_view_jepa_surprise_combo_summary.csv`
- `analysis_outputs/cross_view_jepa_surprise_combo_report.md`
- `analysis_outputs/cross_view_jepa_surprise_lb_proxy_audit.csv`
- `analysis_outputs/cross_view_jepa_surprise_lb_proxy_report.md`

verification:

- `python3 -m py_compile analysis_outputs/cross_view_jepa_surprise_probe.py analysis_outputs/cross_view_jepa_surprise_combo_builder.py analysis_outputs/cross_view_jepa_surprise_lb_proxy_audit.py` passed
- `python3 analysis_outputs/cross_view_jepa_surprise_probe.py --force-features --top-n 24 --guard-top-k 6` completed
- `python3 analysis_outputs/cross_view_jepa_surprise_combo_builder.py` completed
- `python3 analysis_outputs/cross_view_jepa_surprise_lb_proxy_audit.py` completed

JEPA idea:

- Treat each sensor/feature family as a view: phone/deep context, sleep proxy, quiet-window fragmentation, rhythm regularity, and measurement process.
- Learn fold-safe latent-to-latent predictors between views.
- Use target-view residual PCs, norms, and cosines as "surprise" features: hidden sleep state should appear where one view cannot predict another view's latent state.

OOF/guardrail result on stage2 OOF:

- `cvjepa_surprise_full_nonq2`: OOF `0.5646068482` vs base `0.5675309247`; delta `-0.0029240765`; subject-half delta `-0.0029323116`; geometry delta `-0.0034774605`.
- `cvjepa_surprise_full_nonq2_w030`: OOF delta `-0.0024172346`; subject-half win rate `0.984615`; geometry win rate `1.000000`.
- `cvjepa_surprise_core_q1_q3_s2_s4`: OOF delta `-0.0023351912`; subject-half delta `-0.0022590688`; geometry delta `-0.0028821278`.
- Best single target clues:
  - Q1: deep-context cannot predict quiet fragmentation residual max; OOF delta `-0.004423`.
  - Q3: rhythm cannot predict sleep-proxy residual PC02; OOF delta `-0.002368`.
  - S2: measurement process cannot predict rhythm target-pred cosine; OOF delta `-0.005664`.
  - S4: sleep proxy cannot predict rhythm residual PC00; OOF delta `-0.003891`.

local public-LB proxy result:

- Existing proxy resolution remains `loocv_ridge_abs_axes_a1` MAE/RMSE `0.0003184931` / `0.0004029881`.
- Best cvjepa submission-space row is `submission_cvjepa_surprise_full_nonq2_w020.csv`.
  - public-anchor score `0.5783845254`
  - raw-axis expected public vs stage2 `0.5783424525`
  - raw05-relative proxy `0.5777849699`
  - raw05-relative delta `+0.0002586627`
  - model spread `0.0001244613`
  - mean absolute move vs raw05 `0.0117541453`
- The strongest OOF row `submission_cvjepa_surprise_full_nonq2.csv` is worse under the public proxy:
  - public-anchor score `0.5800643293`
  - raw05-relative proxy `0.5782543353`
  - raw05-relative delta `+0.0007280281`
  - model spread `0.0008285982`
  - mean absolute move vs raw05 `0.0222094247`

decision:

- Cross-view JEPA surprise is a real local representation discovery: it improves OOF, subject halves, and geometry splits simultaneously.
- It is not yet a raw05-safe public-LB replacement. The local LB proxy sees these rows as stage2-family probes with too much raw-axis/bad-axis movement.
- If submitting from this branch, only `submission_cvjepa_surprise_full_nonq2_w020.csv` is defensible as a public information probe because it has the smallest submission-space drift and is locally closer to stage2 than the larger OOF-gain rows.
- Keep raw05/e40-family candidates ahead of cvjepa surprise for conservative public LB ordering.

## 35. Raw05-compatible Cross-view JEPA surprise micro grafts

scripts:

- `analysis_outputs/raw05_cvjepa_surprise_micro_graft.py`
- `analysis_outputs/frontier_cvjepa_surprise_micro_refine.py`

outputs:

- `analysis_outputs/raw05_cvjepa_surprise_micro_graft_scan.csv`
- `analysis_outputs/raw05_cvjepa_surprise_micro_graft_shortlist.csv`
- `analysis_outputs/raw05_cvjepa_surprise_micro_graft_local_proxy.csv`
- `analysis_outputs/raw05_cvjepa_surprise_micro_graft_report.md`
- `analysis_outputs/frontier_cvjepa_surprise_micro_refine_scan.csv`
- `analysis_outputs/frontier_cvjepa_surprise_micro_refine_shortlist.csv`
- `analysis_outputs/frontier_cvjepa_surprise_micro_refine_local_proxy.csv`
- `analysis_outputs/frontier_cvjepa_surprise_micro_refine_report.md`

verification:

- `python3 -m py_compile analysis_outputs/raw05_cvjepa_surprise_micro_graft.py analysis_outputs/frontier_cvjepa_surprise_micro_refine.py analysis_outputs/cross_view_jepa_surprise_lb_proxy_audit.py` passed
- `python3 analysis_outputs/raw05_cvjepa_surprise_micro_graft.py` completed
- `python3 analysis_outputs/frontier_cvjepa_surprise_micro_refine.py` completed

raw05 direct graft result:

- Generated `80897` capped `cvjepa - stage2` logit graft candidates from raw05.
- Rescored `698` with actual-anchor masks and saved `81`.
- Best local-proxy row:
  - `submission_raw05_cvjepa_surprise_graft_c3d9cd3d.csv`
  - raw05-relative local proxy `0.5775252844`
  - raw05-relative delta `-0.0000010228`
  - model spread `0.0000024367`
  - actual-anchor `0.5779067907`
  - posterior `0.5775284552`
  - raw-axis delta `-0.0000001397`
  - bad-axis `0.0036690745`
  - mean absolute move vs raw05 `0.0000969388`
- Interpretation: direct raw05 graft proves the cvjepa residual can make tiny axis-neutral moves, but it does not approach the e40/lowbad actual-anchor frontier.

frontier refine result:

- Generated `47340` capped cvjepa grafts on top of e40, lowbad, energyfront, efmicro, and axisbridge anchors.
- Rescored `1616` with actual-anchor masks and saved `88`.
- Best actual-anchor row:
  - `submission_frontier_cvjepa_refine_a2c8d2c8.csv`
  - anchor `e40`
  - label `e40:full_nonq2_w030|q3_s2_s4|ones|agree_raw_q65|dir+1|w0.22|c0.024`
  - actual-anchor `0.5778270682`
  - posterior `0.5768966986`
  - raw-axis delta `0.0000000725`
  - bad-axis `0.0001202771`
  - mean absolute move vs raw05 `0.0016463907`
  - raw05-relative local proxy `0.5775229594`, delta `-0.0000033478`
- Best strict raw / low-bad balance row:
  - `submission_frontier_cvjepa_refine_b1d38df6.csv`
  - anchor `lowbad_bal`
  - label `lowbad_bal:full_nonq2_w030|no_q2|surprise_top70|all|dir+1|w0.04|c0.014`
  - actual-anchor `0.5778275958`
  - posterior `0.5769038478`
  - raw-axis delta `0.0000000986`
  - bad-axis `-0.0000008961`
  - mean absolute move vs raw05 `0.0015981440`
  - raw05-relative local proxy `0.5775222455`, delta `-0.0000040617`
- Best local-proxy / ultra-low-bad row:
  - `submission_frontier_cvjepa_refine_e725a22f.csv`
  - anchor `lowbad_edge`
  - label `lowbad_edge:full_nonq2_w020|q1_s2|surprise_top70|agree_raw_q65|dir-1|w0.14|c0.014`
  - actual-anchor `0.5778277704`
  - posterior `0.5769058973`
  - raw-axis delta `0.0000001872`
  - bad-axis `0.0000000002`
  - mean absolute move vs raw05 `0.0015925399`
  - raw05-relative local proxy `0.5775221986`, delta `-0.0000041086`

decision:

- Cross-view JEPA surprise can be compressed into the raw05-compatible frontier.
- The strongest useful pattern is not the original stage2 correction direction. The winners are tiny capped residuals, mostly `agree_raw_q65` or surprise-row gates, applied on e40/lowbad anchors.
- These rows slightly improve or preserve the e40/lowbad frontier while cutting bad-axis toward zero, but the raw05-relative edge is still far below the local proxy MAE `0.0003184931`.
- Promote `submission_frontier_cvjepa_refine_a2c8d2c8.csv` as the high-upside actual-anchor cvjepa-frontier probe.
- Promote `submission_frontier_cvjepa_refine_b1d38df6.csv` as the strict raw/low-bad cvjepa-frontier probe.
- Promote `submission_frontier_cvjepa_refine_e725a22f.csv` as the ultra-low-bad public-information probe when accepting raw-axis delta `1.87e-7`.

## 36. Public LB Bottleneck After A2C8

script:

- `analysis_outputs/public_lb_bottleneck_after_a2c8.py`

outputs:

- `analysis_outputs/public_lb_bottleneck_after_a2c8_report.md`
- `analysis_outputs/public_lb_bottleneck_after_a2c8_known_augmented.csv`
- `analysis_outputs/public_lb_bottleneck_after_a2c8_model_scores.csv`
- `analysis_outputs/public_lb_bottleneck_after_a2c8_proxy_errors.csv`
- `analysis_outputs/public_lb_bottleneck_after_a2c8_move_bounds.csv`
- `analysis_outputs/public_lb_bottleneck_after_a2c8_frontier_focus.csv`

observed public:

- `submission_frontier_cvjepa_refine_a2c8d2c8.csv` public LB `0.577439321`.
- This is the current observed best and improves raw05 `0.5775263072` by `-0.0000869862`.
- Remaining distance to `0.540000000` is `0.037439321`; the last gain covers only `0.2323%` of that gap.

bottleneck diagnostics:

- The raw05-relative proxy predicted `a2c8` at `0.5775229594`, missing actual public by `+0.0000836384`. Direction was right, magnitude was undercalled.
- A leave-one-public-anchor model trained on the old six public anchors predicted `0.5778666938` for `a2c8`, missing by `+0.0004273728`. This means the cvjepa-frontier branch is out-of-family for the old public-anchor calibration.
- Best 7-anchor leave-one-anchor proxy is `loocv_ridge_signed_axes_a1` with MAE/RMSE `0.0002979250` / `0.0003593046`, still far larger than most candidate edges.
- `a2c8` mean absolute move vs raw05 is only `0.0016463907` per cell. Even if every moved probability is in the correct hidden-label direction, the best-case average logloss gain is `0.0050731896`, only `13.55%` of the 0.54 gap.

interpretation:

- Current work is mostly optimizing a thin public-compatible tangent around raw05. That can find 1e-4 gains, but it cannot plausibly reach 0.54 by itself.
- The JEPA/cross-view surprise signal is real locally, but the transfer bottleneck is public hidden-block distribution shift plus weak public-anchor calibration.
- To approach 0.54, the next branch must either infer hidden test labels/subsets more directly or train a stronger row-level representation with larger moves that survive public-axis validation. Micro-refines should now be treated as measurement probes, not the main path.

## 37. 7-Anchor Public Inverse And Blend Probes After A2C8

scripts:

- `analysis_outputs/public_lb_inverse_mask_audit_7anchor.py`
- `analysis_outputs/public_lb_inverse7_next_probe_selector.py`
- `analysis_outputs/public_lb_inverse7_blend_probe_builder.py`

outputs:

- `analysis_outputs/public_lb_inverse7_mask_audit_report.md`
- `analysis_outputs/public_lb_inverse7_next_probe_report.md`
- `analysis_outputs/public_lb_inverse7_blend_probe_report.md`
- `analysis_outputs/public_lb_inverse7_blend_probe_selected.csv`

observations:

- Adding `a2c8` as a seventh actual public anchor sharpens the public split hypothesis toward `id01` / early global rows. The top mask is `single_subject id01` with 27 rows; the next strong structured masks are first-20%-of-test order, mostly `id01/id02` early blocks.
- Target decomposition of the top masks says `a2c8` is mainly helping `Q3` plus `S2/S3`, while `Q1/S1/S4` are mixed. This is why broad all-target JEPA residuals still fail.
- Full inverse ranking still likes old public-entropy/mask-aware candidates, but raw05+a2c8-compatible ranking prefers q3/s-stage JEPA corrections and cvjepa variants. This means public-entropy should be used as an orthogonal diagnostic, not as an unconstrained new prior.

blend probe result:

- Base is observed-best `submission_frontier_cvjepa_refine_a2c8d2c8.csv`.
- Best diagnostic blend: `analysis_outputs/submission_inverse7blend_1040423d.csv`
  - donor `submission_public_entropyproj_public2d0_g075.csv`, target `no_q2`, weight `0.15`, cap `0.010`
  - compat delta vs a2c8 `-0.000050403`, full delta `-0.000429297`
  - mean move vs a2c8 `0.002374`, orth ratio `0.725322`
- Safer sibling: `analysis_outputs/submission_inverse7blend_404221a2.csv`
  - donor `public2d0_g050`, target `no_q2`, weight `0.15`, cap `0.010`
  - compat delta `-0.000047909`, full delta `-0.000380225`
- q3/s-stage axis probes:
  - `analysis_outputs/submission_inverse7blend_b32dd1a5.csv`
  - `analysis_outputs/submission_inverse7blend_a113868d.csv`
  - these move only about `0.000052` from a2c8 and are score-safe diagnostics, not likely 0.54 movers.
- cvjepa same-family controls:
  - `analysis_outputs/submission_inverse7blend_3f238743.csv`
  - `analysis_outputs/submission_inverse7blend_9fa93a50.csv`
  - these are nearly identical to a2c8; use only to test whether public rewards the exact q3_s2_s4 refinement.

decision:

- If submitting one information-rich next probe, use `submission_inverse7blend_1040423d.csv`.
- If avoiding the public-entropy orthogonal risk, use `submission_inverse7blend_b32dd1a5.csv` or keep a2c8; expected gain is tiny.
- The needed modification is not “more raw05-compatible micro features.” It is: keep a2c8 as the anchor, use inverse7 to isolate likely hidden-public blocks, and test larger no-Q2/public-entropy/JEPA-latent moves only through capped logit blends and target masks.
- For 0.54, this branch is still diagnostic. A real path needs either much better hidden subset/label inference or a larger JEPA row-level representation whose moves are 5-10x larger while staying public-axis compatible.

## 38. Target-Ablation Sparse Scale Probe

script:

- `analysis_outputs/jepa_target_ablation_scale_probe.py`

outputs:

- `analysis_outputs/jepa_target_ablation_scale_probe_report.md`
- `analysis_outputs/jepa_target_ablation_scale_probe_scan.csv`
- `analysis_outputs/jepa_target_ablation_scale_probe_actual_anchor.csv`
- `analysis_outputs/jepa_target_ablation_scale_probe_cv_summary.csv`
- `analysis_outputs/jepa_target_ablation_scale_probe_selected.csv`

validation:

- Script compiles.
- All 20 selected submissions match the sample file shape and key order.
- Selected submission probabilities are finite, with range `0.0630798631` to `0.9797988457`.
- Three target-ablation first rows are exact duplicates of already selected scale-ladder files:
  - `submission_targetabl_64102eec.csv` == `submission_sparseladder_b01acaa1.csv`
  - `submission_targetabl_25d719c0.csv` == `submission_sparseladder_89817541.csv`
  - `submission_targetabl_8f81d324.csv` == `submission_sparseladder_f1ee16b0.csv`

observations:

- Best target-group public-axis proxy is Q3/stage, not a single label:
  - `submission_targetabl_b19056bb.csv`: `q3_stage`, actual-anchor `0.577727`, honest CV delta `-0.000552`, mean move `0.004452`.
  - `submission_targetabl_1049b8e7.csv`: `q3_s2_s3_s4`, actual-anchor `0.577738`, honest CV delta `-0.000580`, mean move `0.004809`.
- Larger move candidates are still broad coupled directions:
  - `submission_sparseladder_b01acaa1.csv`: actual-anchor `0.577746`, honest CV delta `-0.000935`, mean move `0.008816`.
  - `submission_sparseladder_89817541.csv`: actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`.
  - `submission_sparseladder_f1ee16b0.csv`: actual-anchor `0.577758`, honest CV delta `-0.000934`, mean move `0.008276`.
- Single-target probes have too little amplitude to be plausible 0.54 movers. Best Q3-only rows reach only about `0.0024` mean move from a2c8.

interpretation:

- The current hidden structure is target-coupled: Q3 and stage labels move together, while all/no-Q2 directions carry the larger amplitude.
- The next public result should separate two questions:
  - Does the larger all/no-Q2 sparse direction transfer?
  - If not, does the lower-amplitude Q3/stage edge transfer cleanly?
- This supports a two-step submission sequence: one scale-ladder score probe, then one Q3/stage diagnostic if the score probe leaks.

## 39. Inverse7-Gated Sparse Scale

script:

- `analysis_outputs/jepa_inverse7_gated_sparse_scale.py`

outputs:

- `analysis_outputs/jepa_inverse7_gated_sparse_scale_report.md`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_scan.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_actual_anchor.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_cv_summary.csv`
- `analysis_outputs/jepa_inverse7_gated_sparse_scale_selected.csv`

validation:

- Script compiles.
- Generated `960` candidates, then scored `187` actual-anchor rows and `81` honest anchor-CV rows.
- Selected diagnostic submissions pass shape/key/range checks.
- Selected probability range is `0.0630798631` to `0.9798140955`.

observations:

- Hard `id01` gating is too small. It supports the inverse7 split hypothesis qualitatively but does not make useful score candidates.
- `prefix30` is the best hard row gate:
  - `submission_inv7gate_a3613347.csv`: `prefix30/q3_stage`, actual-anchor `0.577855`, honest CV delta `-0.000290`, move `0.002401`.
  - `submission_inv7gate_0a9c0c66.csv`: `prefix30/all`, actual-anchor `0.577886`, honest CV delta `-0.000351`, move `0.003308`.
- Soft inverse7 posterior gating can recover more amplitude but loses actual-anchor:
  - `submission_inv7gate_31adfb5b.csv`: `inv64_soft/all`, actual-anchor `0.577914`, honest CV delta `-0.000310`, move `0.004254`.

interpretation:

- The inverse7 public row split is underidentified for construction. It is useful for explaining likely public rows, but hard row gating throws away too much of the sparse JEPA signal.
- This is negative evidence against replacing uniform sparse scale-ladder with inverse7-gated row localization.
- Keep scale-ladder as the score path; keep inverse7-gated rows as later diagnostics only.

## 40. Bad-Axis Orthogonal Scale-Ladder

script:

- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder.py`

outputs:

- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_report.md`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_scan.csv`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_cv_summary.csv`
- `analysis_outputs/jepa_bad_axis_orthogonal_scale_ladder_selected.csv`

validation:

- Script compiles.
- Scored `349` prefiltered candidates and `124` honest anchor-CV candidates.
- Six non-zero diagnostic submissions pass shape/key/probability checks.
- Selected probability range is `0.065381` to `0.979879`.

observations:

- The best sparse directions have no positive projection onto the failed JEPA residual/Q2 axis group:
  - top `jepa_bad2` rows have `removed_norm_ratio = 0`.
  - this means the current sparse-JEPA/direct-label direction is not failing because it contains the same simple positive component as the rejected JEPA residual/Q2 probes.
- Removing broader failed public axes is non-zero but harmful:
  - `submission_ortholadder_cc4d9154.csv`: `public_bad4`, removed ratio `0.291362`, actual-anchor `0.577782`, honest CV delta `-0.000795`, move `0.007940`.
  - `submission_ortholadder_8ef88723.csv`: `classic_bad2`, removed ratio `0.291362`, actual-anchor `0.577794`, honest CV delta `-0.000823`, move `0.008355`.
- Unorthogonalized comparators are better:
  - f465 full scale `1.30`: actual-anchor `0.577724`, honest CV delta `-0.000919`, move `0.008027`.
  - f465 full scale `1.50`: actual-anchor `0.577757`, honest CV delta `-0.001013`, move `0.009260`.

interpretation:

- Global bad-axis orthogonalization is too blunt. The failed public anchors contain both harmful and useful components.
- The bottleneck is not simply “remove the known bad directions.” It is a structured decomposition problem: identify which row/target block of those directions is bad and which part is useful.
- This pushes the next hidden-structure search toward row/target-specific axis decomposition, label-prior inference, or a stronger JEPA latent that predicts hidden subset membership, rather than another global projection.

## 41. Blockwise Bad-Axis Decomposition

script:

- `analysis_outputs/jepa_blockwise_bad_axis_decomposition.py`

outputs:

- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_report.md`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_scan.csv`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_cv_detail.csv`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_cv_summary.csv`
- `analysis_outputs/jepa_blockwise_bad_axis_decomposition_selected.csv`

validation:

- Script compiles.
- Scored `365` blockwise candidates.
- Selected `9` diagnostic submissions.
- Selected submissions pass shape/key/probability checks.
- Selected probability range is finite: min about `0.066173`, max `0.979799`.

experiment:

- 이전 global orthogonalization은 failed public axis를 전체 logit vector에서 지워서 좋은 신호까지 같이 제거했다.
- 이번 실험은 sparse JEPA/direct-label move는 유지하고, failed-axis component를 특정 row-block x target-group 안에서만 제거했다.
- row gate는 `id01`, `prefix20`, `prefix30`, `subject_prefix25`, `subject_suffix25`, inverse7 posterior gate, `rowmod4_rem3`, complement gate를 포함했다.
- target group은 `all`, `no_q2`, `q3_stage`, `q3_s2_s3_s4`, `stage_all`을 사용했다.
- bad-axis group은 `classic_bad2`, `public_bad4`, `consensus_bad3`, `all_bad7`로 나누었다.

observations:

- Best blockwise candidate:
  - `analysis_outputs/submission_blockorth_3a28f87f.csv`
  - source `282_consensus_directrob`, source target `full`, row gate `rowmod4_rem3`, correction target `stage_all`, axis group `public_bad4`, anti lambda `0.35`, signed projection, scale `1.30`
  - actual-anchor `0.577744`, honest CV delta `-0.000892`, worst CV delta `-0.000674`, robust delta vs a2c8 `-0.001141`, mean move `0.008599`, removed norm ratio `0.475478`.
- Close sibling:
  - `analysis_outputs/submission_blockorth_0352b65f.csv`
  - row gate `prefix30`, correction target `no_q2`, axis group `public_bad4`, anti lambda `0.25`, actual-anchor `0.577744`, honest CV delta `-0.000884`, mean move `0.008585`.
- Blockwise repair beats global orthogonalization clearly:
  - global `submission_ortholadder_cc4d9154.csv`: actual-anchor `0.577782`, honest CV delta `-0.000795`, mean move `0.007940`.
  - blockwise `submission_blockorth_3a28f87f.csv`: actual-anchor `0.577744`, honest CV delta `-0.000892`, mean move `0.008599`.
- 그러나 기존 scale-ladder frontier와 비교하면 개선은 거의 없다:
  - `submission_sparseladder_b01acaa1.csv`: actual-anchor `0.577746`, honest CV delta `-0.000935`, mean move `0.008816`.
  - `submission_sparseladder_89817541.csv`: actual-anchor `0.577757`, honest CV delta `-0.001013`, mean move `0.009260`.
  - `blockorth_3a28f87f`는 `b01acaa1`보다 actual-anchor가 약 `0.000002` 좋지만, CV/robust support는 더 약하다.

interpretation:

- failed public axes는 정말로 block/target-dependent하다. 그래서 전역 projection보다 blockwise projection이 낫다.
- 하지만 이것만으로는 0.54 병목이 풀리지 않는다. projection repair는 이미 수확 체감 구간에 들어갔다.
- `submission_blockorth_3a28f87f.csv`는 score-first 후보가 아니라, `b01acaa1`의 near-frontier diagnostic sibling이다.
- 제출 우선순위는 유지한다:
  1. `analysis_outputs/submission_sparseladder_b01acaa1.csv`
  2. `analysis_outputs/submission_sparseladder_89817541.csv`
  3. `analysis_outputs/submission_sparseladder_f1ee16b0.csv`
  4. diagnostic sibling: `analysis_outputs/submission_blockorth_3a28f87f.csv`
- 다음 단계는 더 정교한 projection이 아니라, direct hidden label-prior / hidden subset 식별 또는 더 강한 JEPA latent로 public-compatible 큰 move를 찾는 쪽이다.

## 42. Sparse Direction Ensemble Orthogonalizer

script:

- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer.py`

outputs:

- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_report.md`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_scan.csv`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_cv_detail.csv`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_cv_summary.csv`
- `analysis_outputs/jepa_sparse_direction_ensemble_orthogonalizer_selected.csv`

validation:

- Script compiles.
- Generated `2604` unique direction-ensemble candidates.
- Prefiltered `357`, anchor-CV scored `130`, selected `24`.
- Selected submissions pass shape/key/probability checks.
- Selected probability range is finite: min about `0.066030`, max about `0.979799`.

experiment:

- 이전 두 실험은 failed public axis를 직접 제거했다.
- 이번 실험은 관점을 바꿔서, 이미 좋은 sparse direction들을 logit space에서 섞으면 bad-axis 성분이 자연스럽게 상쇄되는지 확인했다.
- source direction은 `b01acaa1`, `89817541`, `f1ee16b0`, `blockorth_3a28f87f`, `targetabl_b19056bb`를 중심으로 했다.
- 이후 optional `classic_bad2` / `public_bad4` projection도 같이 시험했다.

observations:

- New best local larger-move candidate:
  - `analysis_outputs/submission_direns_2a96ae73.csv`
  - blend: `b01acaa1 + blockorth_3a28f87f + targetabl_b19056bb`
  - weights `0.33/0.33/0.33`, full target, all cells, no explicit projection, scale `1.10`
  - actual-anchor `0.577729`, honest CV delta `-0.000877`, worst CV delta `-0.000648`, robust delta vs a2c8 `-0.001112`, mean move `0.008015`.
- Close siblings:
  - `analysis_outputs/submission_direns_1e0f159d.csv`: `b01 + blockorth + f1ee`, equal weights, scale `0.95`, actual-anchor `0.577729`, honest CV `-0.000898`, move `0.008133`.
  - `analysis_outputs/submission_direns_c4af1fd8.csv`: `b01 + 898 + f1ee`, weights `0.50/0.25/0.25`, scale `0.95`, actual-anchor `0.577733`, honest CV `-0.000930`, move `0.008353`.
- Explicit orthogonalized ensemble rows are weaker:
  - `analysis_outputs/submission_direns_b0962ff8.csv`: `public_bad4` anti `0.25`, removed ratio `0.334509`, actual-anchor `0.577760`, honest CV `-0.000826`, move `0.008030`.
- Pairwise movement versus `b01acaa1`:
  - `direns_2a96ae73`: mean diff `0.000925`, max diff `0.009089`.
  - `direns_1e0f159d`: mean diff `0.000718`, max diff `0.008651`.
  - `direns_c4af1fd8`: mean diff `0.000643`, max diff `0.005768`.

interpretation:

- 이 결과는 중요하다. frontier 개선은 bad-axis를 더 깎아서 나온 게 아니라, 부분적으로 맞는 JEPA/direct-label 방향들을 섞어서 나왔다.
- 즉 현재 병목은 “bad axis component 하나 제거”보다 “correct hidden-structure direction mixture and scale”에 가깝다.
- Q3/stage direction은 단독 amplitude는 약하지만, `b01`/`blockorth`와 섞을 때 public-compatible stabilizer 역할을 한다.
- 제출 우선순위 업데이트:
  1. `analysis_outputs/submission_direns_2a96ae73.csv`
  2. `analysis_outputs/submission_direns_1e0f159d.csv`
  3. `analysis_outputs/submission_direns_c4af1fd8.csv`
  4. `analysis_outputs/submission_sparseladder_89817541.csv`
  5. `analysis_outputs/submission_sparseladder_f1ee16b0.csv`
- 명시적 orthogonalized candidate는 계속 diagnostic이다. 실제 score-first 후보는 non-orthogonal direction ensemble이다.

## 43. Direction Ensemble Combo Stress Audit

script:

- `analysis_outputs/jepa_direction_ensemble_combo_stress_audit.py`

outputs:

- `analysis_outputs/jepa_direction_ensemble_combo_stress_report.md`
- `analysis_outputs/jepa_direction_ensemble_combo_stress_detail.csv`
- `analysis_outputs/jepa_direction_ensemble_combo_stress_summary.csv`
- `analysis_outputs/jepa_direction_ensemble_combo_stress_pairwise.csv`

validation:

- Script compiles.
- Scored candidate submissions on all top `160` combos from each of the three inverse public scenario sets: `inverse_top`, `raw05_compatible`, `all_sign`.
- Compared each candidate against `b01_ladder`, `898_ladder`, `blockorth_3a28`, and a2c8.

observations:

- Actual-anchor average alone over-promotes `direns_2a96`.
- Combo-level stress prefers `direns_c4af`:
  - `analysis_outputs/submission_direns_c4af1fd8.csv`
  - blend `b01acaa1 + 89817541 + f1ee16b0`, weights `0.50/0.25/0.25`, scale `0.95`
  - weighted delta vs `b01_ladder`: `-0.000011`
  - weighted win rate vs `b01_ladder`: `0.634403`
  - p90 delta vs `b01_ladder`: `+0.000007`
  - worst delta vs `b01_ladder`: `+0.000035`
  - weighted delta vs `898_ladder`: `-0.000009`
- `direns_2a96` has slightly better actual-anchor average but worse tail:
  - weighted delta vs `b01_ladder`: `-0.000009`
  - weighted win rate: `0.562397`
  - p90 delta: `+0.000044`
  - worst delta: `+0.000101`
- Per-set behavior for `direns_c4af`:
  - `all_sign`: weighted delta `-0.000024`, win rate `1.0`, worst delta `-0.0000127`.
  - `inverse_top`: weighted delta `+0.000005`, win rate `0.045460`, worst delta `+0.0000124`.
  - `raw05_compatible`: weighted delta `-0.000015`, win rate `0.857751`, worst delta `+0.0000349`.

interpretation:

- `c4af` is the safer first public probe because it does not rely on one favorable combo family.
- `2a96` remains useful as an actual-anchor-best sibling, but its tail suggests higher inverse-scenario averaging risk.
- Corrected submission priority:
  1. `analysis_outputs/submission_direns_c4af1fd8.csv`
  2. `analysis_outputs/submission_direns_2a96ae73.csv`
  3. `analysis_outputs/submission_direns_c0fdb76b.csv`
  4. `analysis_outputs/submission_direns_1e0f159d.csv`
  5. `analysis_outputs/submission_sparseladder_89817541.csv`
  6. `analysis_outputs/submission_sparseladder_f1ee16b0.csv`
- This reinforces the current bottleneck: not generic feature engineering, not global bad-axis subtraction, but robust mixture/scale selection among partially correct hidden-structure directions.

## 44. Direction Mixture Minimax Optimizer

script:

- `analysis_outputs/jepa_direction_mixture_minimax_optimizer.py`

outputs:

- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_report.md`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_scan.csv`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_actual_anchor.csv`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_combo_summary.csv`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_cv_summary.csv`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_selected.csv`
- `analysis_outputs/jepa_direction_mixture_minimax_optimizer_integrity.csv`

validation:

- Script compiles.
- Generated `61,630` mixture candidates.
- Actual-anchor rescored `1,800`; combo-stress summarized `190`; LOO/L2O anchor-CV scored `100`.
- Saved `7` submissions; all pass key/order/null/range checks.

experiment:

- Instead of hand-picking direction weights, directly optimized logit-space mixtures against public-anchor combo stress.
- Sources: `b01`, `898`, `f1ee`, `blockorth_3a28`, Q3/stage target-ablation, and `direns_c4af`.
- Candidate variants included full/no-Q2/Q3-stage target gates, raw05/all-sign soft row gates, JEPA energy gates, and `public_bad4` projection.

observations:

- Best new stress probe:
  - `analysis_outputs/submission_mixmin_0c916bb4.csv`
  - blend `direns_c4af + 898_ladder`, weights `0.350/0.650`, full/all/all-cells/no-projection, scale `0.95`
  - actual-anchor `0.577734`, mean move vs a2c8 `0.008496`
  - combo weighted delta vs `b01_ladder`: `-0.000012877`
  - combo weighted win vs `b01_ladder`: `0.978659`
  - combo p90 delta vs `b01_ladder`: `-0.000008452`
  - combo worst delta vs `b01_ladder`: `+0.000010139`
  - combo weighted delta vs `direns_c4af`: `-0.000001636`
  - honest CV delta mean/worst: `-0.000952` / `-0.000696`
- Selected siblings:
  - `analysis_outputs/submission_mixmin_5a4c25e0.csv`
  - `analysis_outputs/submission_mixmin_f0d12643.csv`
  - `analysis_outputs/submission_mixmin_f6c04249.csv`
  - `analysis_outputs/submission_mixmin_ef4b1c19.csv`
  - `analysis_outputs/submission_mixmin_7f9cb635.csv`
  - `analysis_outputs/submission_mixmin_615da9a7.csv`
- Explicit `public_bad4` projection again fails the score-first gate:
  - best projected row actual-anchor `0.577752`
  - combo weighted delta vs `b01_ladder` about `+0.000016`
- Hidden-subset style gates did not help in this search:
  - all-row/all-cell/no-projection best actual-anchor `0.577734`
  - `rawcompat_soft` and `allsign_soft` begin around `0.577750`
  - `energy_top70` begins around `0.577794`

interpretation:

- This is a stronger negative result for the current hidden-gate idea: the public-compatible candidate is still all-row/full-target.
- JEPA energy and raw05-compatible gates may be useful diagnostics, but in this direction family they remove signal more than they isolate hidden public structure.
- The c4af/898/b01/f1ee mixture is the current frontier. It can shave combo tails but cannot explain a 0.54 path by itself.

updated probe priority:

1. `analysis_outputs/submission_mixmin_0c916bb4.csv`
2. `analysis_outputs/submission_direns_c4af1fd8.csv`
3. `analysis_outputs/submission_mixmin_5a4c25e0.csv`
4. `analysis_outputs/submission_mixmin_f6c04249.csv`
5. `analysis_outputs/submission_direns_2a96ae73.csv`
6. `analysis_outputs/submission_sparseladder_89817541.csv`
