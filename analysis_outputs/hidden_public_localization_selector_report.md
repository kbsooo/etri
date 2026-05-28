# Hidden Public Localization Selector

## Purpose
Direct inverse solutions can fit known public LB anchors, but are underdetermined. This audit treats them as noisy JEPA-style teachers: cells repeatedly selected by low-error inverse views become low-energy hidden-public localization candidates, then submissions are re-ranked while still respecting the previous stress/bad-axis gates.

## Source Ensemble
- selected inverse solutions: 41
- robust_source_score range: 0.002835 .. 0.006483
- structured solution share: 0.439
- subject-like solution share: 0.366

## Localization Shape
- active cells: 1750 / 1750
- top 10 rows energy share: 0.105
- top 25 rows energy share: 0.214

### Target Energy
```text
target  target_energy  target_energy_norm  mean_pseudo_y  mean_a2c8_prob  mean_delta_vs_a2c8  mean_abs_delta_vs_a2c8  mean_signal_to_uncertainty  mean_direction_agreement  cell_count
    Q1       2.183154            0.192863       0.488185        0.497677           -0.009491                0.029795                    0.777672                  0.967219         250
    Q3       2.160758            0.190884       0.608775        0.609575           -0.000800                0.030052                    0.774909                  0.958823         250
    S3       1.978687            0.174800       0.660524        0.641724            0.018800                0.026885                    0.790076                  0.967840         250
    S2       1.547078            0.136671       0.635575        0.634337            0.001238                0.021000                    0.779411                  0.966091         250
    S1       1.436056            0.126863       0.659458        0.660671           -0.001214                0.020518                    0.758105                  0.963446         250
    S4       1.039848            0.091862       0.564799        0.565198           -0.000399                0.015772                    0.727135                  0.943105         250
    Q2       0.974152            0.086058       0.547296        0.548634           -0.001338                0.017578                    0.598897                  0.910063         250
```

### Top Rows
```text
 row_index subject_id sleep_date lifelog_date  subject_pos  subject_n  subject_frac  row_energy  row_energy_norm  target_count  mean_direction_agreement  mean_signal_to_uncertainty  max_cell_energy top_target
         7       id01 2024-08-09   2024-08-08            7         27      0.269231    0.194673         0.017198             7                  0.991371                    0.808913         0.071160         S3
       211       id09 2024-08-16   2024-08-15           10         27      0.384615    0.132610         0.011715             7                  0.982744                    0.765887         0.046712         Q3
        15       id01 2024-09-03   2024-09-02           15         27      0.576923    0.132540         0.011709             7                  0.954392                    0.769897         0.062009         S2
       212       id09 2024-08-17   2024-08-16           11         27      0.423077    0.125294         0.011069             7                  0.863920                    0.605362         0.042814         S1
       220       id09 2024-09-11   2024-09-10           19         27      0.730769    0.113013         0.009984             7                  1.000000                    0.895846         0.047937         S1
       120       id05 2024-11-08   2024-11-07           13         21      0.650000    0.108683         0.009601             7                  1.000000                    0.921472         0.040085         Q1
       114       id05 2024-10-11   2024-10-10            7         21      0.350000    0.100794         0.008904             7                  1.000000                    0.878806         0.040317         Q1
       115       id05 2024-10-14   2024-10-13            8         21      0.400000    0.098281         0.008682             7                  0.973992                    0.854236         0.029204         S1
       167       id07 2024-08-15   2024-08-14           15         30      0.517241    0.094139         0.008316             7                  0.969106                    0.789885         0.024417         S1
       191       id08 2024-08-14   2024-08-13            9         19      0.500000    0.089996         0.007950             7                  0.986780                    0.775492         0.023749         S2
        59       id03 2024-08-17   2024-08-16            0         21      0.000000    0.088946         0.007858             7                  1.000000                    0.884493         0.031880         S3
       139       id06 2024-07-19   2024-07-18           11         24      0.478261    0.086413         0.007634             7                  0.981266                    0.821335         0.026707         Q3
        16       id01 2024-09-04   2024-09-03           16         27      0.615385    0.085646         0.007566             7                  1.000000                    0.778472         0.044135         S2
       242       id10 2024-09-19   2024-09-18           14         22      0.666667    0.085534         0.007556             7                  0.989032                    0.812543         0.034973         Q3
        66       id03 2024-08-25   2024-08-24            7         21      0.350000    0.084175         0.007436             7                  0.913873                    0.714788         0.032226         Q3
       135       id06 2024-07-14   2024-07-13            7         24      0.304348    0.084097         0.007429             7                  0.976128                    0.739262         0.050385         Q1
```

## Candidate Gates
- scored candidates: 368
- submit_gate pass: 0
- research_probe_gate pass: 0
- localization/stress conflicts: 120

### Top Localization Ranking
```text
                                                    basename      source_group candidate_family  localization_score  local_direct_delta_mean  local_direct_delta_p90  energy_ce_delta_top08  selector_p90_delta_vs_a2c8_public  beats_a2c8_scenario_rate  bad_axis_abs_load  submit_gate  research_probe_gate  selector_conflict
       submission_public6entropy_raw05_all_g500_21f375ae.csv universe_priority   public6entropy           -0.003203                -0.000953               -0.000811              -0.006823                           0.001028                  0.011583           0.314244        False                False               True
  submission_public6entropy_compatband_all_g500_c25a1c59.csv universe_priority   public6entropy           -0.003153                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322470        False                False               True
    submission_public6entropy_efmicro3_all_g500_5dab3988.csv universe_priority   public6entropy           -0.003152                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322498        False                False               True
    submission_public6entropy_efmicro5_all_g500_3b4000b8.csv universe_priority   public6entropy           -0.003152                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322383        False                False               True
 submission_public6entropy_energyfront_all_g500_92c9b1dc.csv universe_priority   public6entropy           -0.003151                -0.000917               -0.000802              -0.006788                           0.001016                  0.015444           0.322310        False                False               True
     submission_public6entropy_siggate_all_g500_7d02d74d.csv universe_priority   public6entropy           -0.003150                -0.000916               -0.000802              -0.006786                           0.001016                  0.015444           0.322549        False                False               True
      submission_public6entropy_raw05_noq2_g500_978ce986.csv universe_priority   public6entropy           -0.003132                -0.000907               -0.000787              -0.006789                           0.000986                  0.065637           0.282534        False                False               True
 submission_public6entropy_compatband_noq2_g500_3902f0c0.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291341        False                False               True
   submission_public6entropy_efmicro3_noq2_g500_92d518fb.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291291        False                False               True
   submission_public6entropy_efmicro5_noq2_g500_23f68b31.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291465        False                False               True
submission_public6entropy_energyfront_noq2_g500_bb7fa56f.csv universe_priority   public6entropy           -0.003083                -0.000873               -0.000780              -0.006756                           0.000975                  0.069498           0.291140        False                False               True
    submission_public6entropy_siggate_noq2_g500_6cd6a416.csv universe_priority   public6entropy           -0.003081                -0.000872               -0.000780              -0.006754                           0.000976                  0.069498           0.291421        False                False               True
      submission_public6entropy_stage2_all_g500_1eb42f96.csv universe_priority   public6entropy           -0.003032                -0.000857               -0.000697              -0.006762                           0.001084                  0.015444           0.310041        False                False               True
                           submission_directrob_93de02d3.csv         directrob        directrob           -0.002980                -0.000907               -0.000528              -0.006759                           0.000840                  0.108108           0.135666        False                False               True
     submission_public6entropy_stage2_noq2_g500_0a040ad8.csv universe_priority   public6entropy           -0.002961                -0.000810               -0.000673              -0.006729                           0.001037                  0.073359           0.278331        False                False               True
                           submission_directrob_81846704.csv         directrob        directrob           -0.002921                -0.000870               -0.000505              -0.006733                           0.000814                  0.138996           0.127720        False                False               True
  submission_public6entropy_compatband_ctx_g500_e38f50f2.csv universe_priority   public6entropy           -0.002583                -0.000748               -0.000655              -0.005609                           0.001073                  0.034749           0.269830        False                False               True
    submission_public6entropy_efmicro3_ctx_g500_33d7def9.csv universe_priority   public6entropy           -0.002583                -0.000748               -0.000655              -0.005608                           0.001073                  0.034749           0.269853        False                False               True
    submission_public6entropy_efmicro5_ctx_g500_e5a73a36.csv universe_priority   public6entropy           -0.002582                -0.000748               -0.000654              -0.005608                           0.001073                  0.034749           0.269751        False                False               True
 submission_public6entropy_energyfront_ctx_g500_726372ca.csv universe_priority   public6entropy           -0.002582                -0.000748               -0.000655              -0.005606                           0.001073                  0.034749           0.269643        False                False               True
       submission_public6entropy_raw05_ctx_g500_0ff08a58.csv universe_priority   public6entropy           -0.002579                -0.000749               -0.000667              -0.005558                           0.001066                  0.046332           0.258522        False                False               True
     submission_public6entropy_siggate_ctx_g500_464f0d18.csv universe_priority   public6entropy           -0.002579                -0.000746               -0.000653              -0.005602                           0.001073                  0.034749           0.269872        False                False               True
                           submission_directrob_e047b80b.csv         directrob        directrob           -0.002459                -0.000726               -0.000534              -0.005497                           0.000799                  0.115830           0.111291        False                False               True
                           submission_directrob_aa5a42c6.csv         directrob        directrob           -0.002403                -0.000694               -0.000506              -0.005470                           0.000753                  0.150579           0.109965        False                False               True
                           submission_directrob_1e28f54c.csv         directrob        directrob           -0.002391                -0.000717               -0.000503              -0.005324                           0.000796                  0.115830           0.110352        False                False               True
  submission_public6entropy_compatband_all_g350_4ef1c29c.csv universe_priority   public6entropy           -0.002379                -0.000709               -0.000615              -0.005044                           0.000853                  0.015444           0.233949        False                False               True
    submission_public6entropy_efmicro3_all_g350_d371a065.csv universe_priority   public6entropy           -0.002379                -0.000709               -0.000615              -0.005044                           0.000853                  0.015444           0.233982        False                False               True
    submission_public6entropy_efmicro5_all_g350_f4a18e06.csv universe_priority   public6entropy           -0.002379                -0.000709               -0.000615              -0.005043                           0.000854                  0.015444           0.233847        False                False               True
 submission_public6entropy_energyfront_all_g350_730dfa89.csv universe_priority   public6entropy           -0.002377                -0.000708               -0.000614              -0.005040                           0.000853                  0.015444           0.233730        False                False               True
     submission_public6entropy_siggate_all_g350_c5ad0d4f.csv universe_priority   public6entropy           -0.002375                -0.000707               -0.000614              -0.005037                           0.000853                  0.015444           0.234045        False                False               True
```

### Submit Gate Candidates
None.

### Conflict Diagnostics
```text
                                                    basename      source_group candidate_family  localization_score  local_direct_delta_mean  local_direct_delta_p90  energy_ce_delta_top08  selector_p90_delta_vs_a2c8_public  beats_a2c8_scenario_rate  bad_axis_abs_load  submit_gate  research_probe_gate  selector_conflict
       submission_public6entropy_raw05_all_g500_21f375ae.csv universe_priority   public6entropy           -0.003203                -0.000953               -0.000811              -0.006823                           0.001028                  0.011583           0.314244        False                False               True
  submission_public6entropy_compatband_all_g500_c25a1c59.csv universe_priority   public6entropy           -0.003153                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322470        False                False               True
    submission_public6entropy_efmicro3_all_g500_5dab3988.csv universe_priority   public6entropy           -0.003152                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322498        False                False               True
    submission_public6entropy_efmicro5_all_g500_3b4000b8.csv universe_priority   public6entropy           -0.003152                -0.000917               -0.000803              -0.006791                           0.001016                  0.015444           0.322383        False                False               True
 submission_public6entropy_energyfront_all_g500_92c9b1dc.csv universe_priority   public6entropy           -0.003151                -0.000917               -0.000802              -0.006788                           0.001016                  0.015444           0.322310        False                False               True
     submission_public6entropy_siggate_all_g500_7d02d74d.csv universe_priority   public6entropy           -0.003150                -0.000916               -0.000802              -0.006786                           0.001016                  0.015444           0.322549        False                False               True
      submission_public6entropy_raw05_noq2_g500_978ce986.csv universe_priority   public6entropy           -0.003132                -0.000907               -0.000787              -0.006789                           0.000986                  0.065637           0.282534        False                False               True
 submission_public6entropy_compatband_noq2_g500_3902f0c0.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291341        False                False               True
   submission_public6entropy_efmicro3_noq2_g500_92d518fb.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291291        False                False               True
   submission_public6entropy_efmicro5_noq2_g500_23f68b31.csv universe_priority   public6entropy           -0.003084                -0.000873               -0.000780              -0.006759                           0.000976                  0.069498           0.291465        False                False               True
submission_public6entropy_energyfront_noq2_g500_bb7fa56f.csv universe_priority   public6entropy           -0.003083                -0.000873               -0.000780              -0.006756                           0.000975                  0.069498           0.291140        False                False               True
    submission_public6entropy_siggate_noq2_g500_6cd6a416.csv universe_priority   public6entropy           -0.003081                -0.000872               -0.000780              -0.006754                           0.000976                  0.069498           0.291421        False                False               True
      submission_public6entropy_stage2_all_g500_1eb42f96.csv universe_priority   public6entropy           -0.003032                -0.000857               -0.000697              -0.006762                           0.001084                  0.015444           0.310041        False                False               True
                           submission_directrob_93de02d3.csv         directrob        directrob           -0.002980                -0.000907               -0.000528              -0.006759                           0.000840                  0.108108           0.135666        False                False               True
     submission_public6entropy_stage2_noq2_g500_0a040ad8.csv universe_priority   public6entropy           -0.002961                -0.000810               -0.000673              -0.006729                           0.001037                  0.073359           0.278331        False                False               True
                           submission_directrob_81846704.csv         directrob        directrob           -0.002921                -0.000870               -0.000505              -0.006733                           0.000814                  0.138996           0.127720        False                False               True
  submission_public6entropy_compatband_ctx_g500_e38f50f2.csv universe_priority   public6entropy           -0.002583                -0.000748               -0.000655              -0.005609                           0.001073                  0.034749           0.269830        False                False               True
    submission_public6entropy_efmicro3_ctx_g500_33d7def9.csv universe_priority   public6entropy           -0.002583                -0.000748               -0.000655              -0.005608                           0.001073                  0.034749           0.269853        False                False               True
    submission_public6entropy_efmicro5_ctx_g500_e5a73a36.csv universe_priority   public6entropy           -0.002582                -0.000748               -0.000654              -0.005608                           0.001073                  0.034749           0.269751        False                False               True
 submission_public6entropy_energyfront_ctx_g500_726372ca.csv universe_priority   public6entropy           -0.002582                -0.000748               -0.000655              -0.005606                           0.001073                  0.034749           0.269643        False                False               True
```

## Interpretation
- If directrob-style candidates dominate localization but fail stress/bad-axis gates, the bottleneck is public-subset underidentification rather than representation capacity.
- A submit-safe candidate must be simultaneously good under localized inverse energy and not worse under previous anchor-LOO/blockwise stress. Otherwise it is a diagnostic probe only.
