# Public Posterior Scenario Robustness
This audit avoids scoring every candidate against only one posterior. It uses multiple public-constraint posterior scenarios and ranks candidates by subset regret.

## Top Scenario-Robust Candidates
```
                                                               file  mean_expected  mean_regret  p90_regret  p95_regret  mean_delta_vs_prior  p90_delta_vs_prior  win_rate_vs_prior  scenario_robust_score
                   submission_public_minimaxens_r05_a10_h506746.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                   submission_public_minimaxens_r03_a12_h597891.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                    submission_public_minimaxens_r06_a9_h512521.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                 submission_public_universeens_u80_r02_4c0e785c.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                 submission_public_universeens_u80_r04_8b6653a9.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                   submission_public_minimaxens_r04_a11_h082844.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                 submission_public_universeens_u80_r03_72e58bdb.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                   submission_public_minimaxens_r07_a12_h981086.csv       0.574634     0.000067    0.000118    0.000122            -0.000731           -0.000269                1.0               0.574917
                   submission_public_minimaxens_r08_a10_h869363.csv       0.574634     0.000067    0.000118    0.000122            -0.000731           -0.000269                1.0               0.574917
                   submission_public_minimaxens_r02_a13_h745897.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                    submission_public_minimaxens_r01_a6_h422045.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                 submission_public_universeens_u80_r01_07c571e6.csv       0.574634     0.000067    0.000118    0.000123            -0.000731           -0.000269                1.0               0.574917
                 submission_public_universeens_u65_r02_c0e2b2f1.csv       0.574634     0.000067    0.000142    0.000147            -0.000731           -0.000298                1.0               0.574947
                 submission_public_universeens_u65_r01_365a84a6.csv       0.574641     0.000073    0.000151    0.000156            -0.000725           -0.000309                1.0               0.574977
                 submission_public_universeens_u65_r03_cf973915.csv       0.574639     0.000072    0.000164    0.000171            -0.000726           -0.000304                1.0               0.574991
                 submission_public_universeens_u65_r04_dc6f3303.csv       0.574648     0.000081    0.000161    0.000167            -0.000717           -0.000304                1.0               0.575013
   submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv       0.574649     0.000082    0.000159    0.000166            -0.000716           -0.000262                1.0               0.575013
                   submission_public_maskaware_t80_r11_544844af.csv       0.574650     0.000083    0.000160    0.000167            -0.000715           -0.000261                1.0               0.575019
                   submission_public_maskaware_t80_r12_dcfaabba.csv       0.574651     0.000084    0.000164    0.000169            -0.000714           -0.000265                1.0               0.575025
                   submission_public_maskaware_t50_r05_fb7b695a.csv       0.574649     0.000082    0.000180    0.000193            -0.000716           -0.000285                1.0               0.575040
                   submission_public_maskaware_t50_r06_8d5b4fe1.csv       0.574649     0.000082    0.000181    0.000194            -0.000716           -0.000284                1.0               0.575042
                   submission_public_entropyproj_public2d0_g075.csv       0.574649     0.000082    0.000187    0.000200            -0.000716           -0.000274                1.0               0.575049
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv       0.574649     0.000082    0.000187    0.000200            -0.000716           -0.000274                1.0               0.575049
                   submission_public_maskaware_t50_r04_6761fb38.csv       0.574651     0.000084    0.000185    0.000198            -0.000715           -0.000277                1.0               0.575053
```