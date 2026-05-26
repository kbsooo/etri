# Public Conservative Frontier
This grid blends public-constraint entropy/minimax predictions back toward observed-safe submissions. Scores use posterior scenarios plus conservative pseudo-posteriors from stage2, public2d0, projblend, and anchor.

## Saved Frontier Submissions
```
                                            file  selection_trust  selection_score                                                     safe_file                                       risky_file blend_mode target_mask  risk_weight  posterior_mean_expected  conservative_mean_expected  posterior_mean_delta_vs_stage2  conservative_mean_delta_vs_stage2  oof_loss
submission_public_consfront_t35_r01_9df5211a.csv             0.35         0.578176        submission_publicobsblend_anchor578_to_stage2_w095.csv submission_public_entropyproj_public2d0_g100.csv       prob         all         0.50                 0.574895                    0.574618                       -0.001256                          -0.000419  0.558073
submission_public_consfront_t35_r02_685b9221.csv             0.35         0.578197 submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv submission_public_entropyproj_public2d0_g100.csv       prob         all         0.50                 0.574915                    0.574618                       -0.001236                          -0.000419  0.558000
submission_public_consfront_t35_r03_58360e62.csv             0.35         0.578239 submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv submission_public_entropyproj_public2d0_g100.csv      logit         all         0.50                 0.574904                    0.574619                       -0.001247                          -0.000418  0.557774
submission_public_consfront_t50_r04_b26d90bf.csv             0.50         0.578029        submission_publicobsblend_anchor578_to_stage2_w095.csv submission_public_entropyproj_public2d0_g100.csv      logit         all         0.50                 0.574884                    0.574620                       -0.001267                          -0.000418  0.557837
submission_public_consfront_t50_r05_2ecf14de.csv             0.50         0.578029          submission_publicobsblend_stage2_to_ordinal_w005.csv submission_public_entropyproj_public2d0_g100.csv       prob         all         0.50                 0.574902                    0.574641                       -0.001249                          -0.000396  0.557885
submission_public_consfront_t50_r06_783c0eda.csv             0.50         0.578055        submission_publicobsblend_anchor578_to_stage2_w095.csv submission_public_entropyproj_public2d0_g100.csv       prob        noq2         0.50                 0.574924                    0.574634                       -0.001227                          -0.000404  0.559036
submission_public_consfront_t65_r07_f8156dce.csv             0.65         0.577851        submission_publicobsblend_anchor578_to_stage2_w095.csv submission_public_entropyproj_public2d0_g075.csv       prob         all         0.65                 0.574803                    0.574641                       -0.001348                          -0.000397  0.557303
submission_public_consfront_t65_r08_c67c491d.csv             0.65         0.577855          submission_publicobsblend_stage2_to_ordinal_w005.csv submission_public_entropyproj_public2d0_g100.csv      logit         all         0.50                 0.574889                    0.574642                       -0.001263                          -0.000395  0.557651
submission_public_consfront_t65_r09_6ab53561.csv             0.65         0.577866        submission_publicobsblend_anchor578_to_stage2_w095.csv submission_public_minimaxens_r05_a10_h506746.csv       prob         all         0.65                 0.574792                    0.574646                       -0.001360                          -0.000391  0.557509
submission_public_consfront_t80_r10_b06ca82f.csv             0.80         0.577604        submission_publicobsblend_anchor578_to_stage2_w095.csv  submission_public_minimaxens_r01_a6_h422045.csv       prob         all         0.65                 0.574792                    0.574646                       -0.001360                          -0.000391  0.557498
submission_public_consfront_t80_r11_cbf95500.csv             0.80         0.577618          submission_publicobsblend_stage2_to_ordinal_w005.csv submission_public_entropyproj_public2d0_g075.csv       prob         all         0.65                 0.574809                    0.574658                       -0.001342                          -0.000380  0.557173
submission_public_consfront_t80_r12_9e52dcea.csv             0.80         0.577620 submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv submission_public_entropyproj_public2d0_g075.csv       prob         all         0.65                 0.574819                    0.574643                       -0.001332                          -0.000394  0.557254
```

## Integrity
```
                                            file  rows  key_match  duplicate_keys  null_predictions  min_prob  max_prob
submission_public_consfront_t35_r01_9df5211a.csv   250       True               0                 0  0.074930  0.977851
submission_public_consfront_t35_r02_685b9221.csv   250       True               0                 0  0.073598  0.977906
submission_public_consfront_t35_r03_58360e62.csv   250       True               0                 0  0.073230  0.977943
submission_public_consfront_t50_r04_b26d90bf.csv   250       True               0                 0  0.074684  0.977885
submission_public_consfront_t50_r05_2ecf14de.csv   250       True               0                 0  0.073958  0.977955
submission_public_consfront_t50_r06_783c0eda.csv   250       True               0                 0  0.074930  0.977851
submission_public_consfront_t65_r07_f8156dce.csv   250       True               0                 0  0.072739  0.977746
submission_public_consfront_t65_r08_c67c491d.csv   250       True               0                 0  0.073625  0.977996
submission_public_consfront_t65_r09_6ab53561.csv   250       True               0                 0  0.073428  0.977967
submission_public_consfront_t80_r10_b06ca82f.csv   250       True               0                 0  0.073391  0.977970
submission_public_consfront_t80_r11_cbf95500.csv   250       True               0                 0  0.072058  0.977819
submission_public_consfront_t80_r12_9e52dcea.csv   250       True               0                 0  0.071806  0.977784
```