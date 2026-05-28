# Raw05 JEPA Axis-Local Posterior Sweep

This experiment keeps the local-proxy-useful axisbridge direction but repairs it toward posterior-safe JEPA donors, then re-ranks the scored candidates with the local public-LB proxy.

## Pools

- axis files: `14`
- donor files: `20`

## Counts

- generated/prefiltered candidates: `1600`
- actual-anchor scored candidates: `1600`
- saved shortlist: `81`
- strict hits: `0`
- balanced hits: `193`

## Mode Summary

```csv
mode,mask_name,n,strict_hits,balanced_hits,best_local_delta,best_posterior,best_bad_abs,best_raw_abs,best_axislocal_score
axis_context_repair,q2_s123,320,0,52,-4.3725e-06,0.5769176516,0.0003144164,1.1e-09,3.4028e-06
axis_context_repair,all_soft,320,0,69,-4.3624e-06,0.5769197055,0.0002995617,7.8e-09,1.8432e-06
axis_context_repair,context_s4light,320,0,51,-4.3546e-06,0.5769102078,0.0003294016,1.44e-08,3.4287e-06
axis_context_repair,context,320,0,21,-4.3363e-06,0.5769091865,0.0003445583,1.01e-08,4.5016e-06
donor_axis_inject,q3_s4light,131,0,0,-2.8705e-06,0.5768606035,9.0881e-06,7.961e-07,3.64141e-05
donor_axis_inject,q3_sblockmicro,189,0,0,-2.7767e-06,0.5768571291,3.72753e-05,8.176e-07,3.78209e-05
```

## Shortlist

```csv
file,bucket,mode,axis_file,donor_file,mask_name,strength,cap,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,q3s4_motif_cos,q3s4_motif_orth_ratio,mean_abs_move_vs_raw05,axislocal_score,rank_score
submission_raw05_jepa_axislocal_7a15027d.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.38,0.024,-4.2956e-06,6.78692e-05,0.577827817,0.5769262041,2.8e-08,-0.0003073755,0.9987408385,0.0685942437,0.0015449919,3.1242e-06,284.54
submission_raw05_jepa_axislocal_61adb42f.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,all_soft,0.38,0.024,-4.2777e-06,6.78208e-05,0.5778278289,0.5769260934,2.54e-08,-0.000321339,0.9987408385,0.0685942437,0.0015449471,3.397e-06,290.08
submission_raw05_jepa_axislocal_58dd85e3.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,all_soft,0.38,0.024,-4.2815e-06,6.78185e-05,0.5778278308,0.5769262254,2.5e-08,-0.0003207702,0.9987408385,0.0685942437,0.0015446817,3.4108e-06,293.0
submission_raw05_jepa_axislocal_0951e375.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,all_soft,0.38,0.024,-4.2794e-06,6.78446e-05,0.5778278052,0.5769260867,2.87e-08,-0.0003215125,0.9987408385,0.0685942437,0.0015451761,3.3972e-06,294.52
submission_raw05_jepa_axislocal_8ac340a6.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,all_soft,0.38,0.024,-4.2804e-06,6.78397e-05,0.5778278099,0.5769262163,2.74e-08,-0.0003211462,0.9987408385,0.0685942437,0.0015450514,3.4174e-06,297.14
submission_raw05_jepa_axislocal_68ca6074.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.56,0.024,-4.3098e-06,6.87114e-05,0.5778268848,0.5769192338,2.35e-07,-0.0003144164,0.998734945,0.0688278475,0.0015574247,3.6126e-06,303.86
submission_raw05_jepa_axislocal_a6c20f40.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,all_soft,0.38,0.024,-4.2807e-06,6.78573e-05,0.5778277659,0.5769262933,2.93e-08,-0.0003249328,0.9987408385,0.0685942437,0.0015453184,3.5098e-06,305.04
submission_raw05_jepa_axislocal_90f36fb1.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.38,0.024,-4.3352e-06,6.83407e-05,0.5778270758,0.5769252342,1.232e-07,-0.0003174561,0.998734945,0.0688278475,0.0015517745,3.4028e-06,314.14
submission_raw05_jepa_axislocal_e82848f1.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.56,0.024,-4.2523e-06,6.80198e-05,0.5778279812,0.5769206626,9.42e-08,-0.0002995617,0.9986769403,0.0702789101,0.0015473553,1.8432e-06,315.32
submission_raw05_jepa_axislocal_35929361.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8656f234.csv,all_soft,0.38,0.024,-4.2586e-06,6.7777e-05,0.5778278439,0.5769262277,2.53e-08,-0.000337707,0.9987408385,0.0685942437,0.0015448255,3.773e-06,317.46
submission_raw05_jepa_axislocal_d90f09cf.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,context_s4light,0.1,0.024,-4.2853e-06,6.76685e-05,0.57782777,0.5769315763,1.57e-08,-0.0003626406,0.9999626269,0.0118371028,0.0015418587,5.2143e-06,320.84
submission_raw05_jepa_axislocal_717f9a0f.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,all_soft,0.56,0.024,-4.2257e-06,6.79564e-05,0.5778280063,0.5769204997,9.06e-08,-0.0003201393,0.9986769403,0.0702789101,0.0015472966,2.2454e-06,326.7
submission_raw05_jepa_axislocal_f910365b.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,all_soft,0.56,0.024,-4.2284e-06,6.79843e-05,0.5778279645,0.5769204896,9.53e-08,-0.0003203952,0.9986769403,0.0702789101,0.0015476326,2.2457e-06,326.72
submission_raw05_jepa_axislocal_01db9579.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,all_soft,0.56,0.024,-4.2315e-06,6.79455e-05,0.577828002,0.576920694,8.99e-08,-0.000319301,0.9986769403,0.0702789101,0.0015469061,2.2657e-06,326.78
submission_raw05_jepa_axislocal_c1874132.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,q2_s123,0.38,0.024,-4.312e-06,6.82927e-05,0.5778270821,0.5769249562,1.209e-07,-0.0003342107,0.998734945,0.0688278475,0.0015519872,3.6673e-06,327.12
submission_raw05_jepa_axislocal_d458d8c6.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,q2_s123,0.38,0.024,-4.3172e-06,6.82871e-05,0.577827091,0.5769252101,1.193e-07,-0.0003336738,0.998734945,0.0688278475,0.0015515385,3.6842e-06,327.34
submission_raw05_jepa_axislocal_f3bd9cde.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,q2_s123,0.56,0.024,-4.2832e-06,6.86324e-05,0.5778269072,0.5769191982,2.293e-07,-0.0003383158,0.998734945,0.0688278475,0.0015570764,4.0283e-06,328.2
submission_raw05_jepa_axislocal_dae43698.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,all_soft,0.56,0.024,-4.2299e-06,6.79782e-05,0.5778279725,0.5769206807,9.34e-08,-0.0003198552,0.9986769403,0.0702789101,0.0015474491,2.2754e-06,328.82
submission_raw05_jepa_axislocal_7075b9dc.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,q2_s123,0.56,0.024,-4.2754e-06,6.86406e-05,0.5778268943,0.5769188243,2.318e-07,-0.0003391071,0.998734945,0.0688278475,0.0015577393,4.0055e-06,329.64
submission_raw05_jepa_axislocal_d3d23f68.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.38,0.024,-4.2229e-06,6.77419e-05,0.5778281277,0.5769251121,7.57e-08,-0.000347925,0.999896309,0.0196990193,0.0015434454,3.5603e-06,330.42
submission_raw05_jepa_axislocal_fb6f15f5.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.22,0.024,-4.3564e-06,6.80123e-05,0.5778272479,0.5769305701,2.6e-08,-0.0003201577,0.998734945,0.0688278475,0.0015468362,4.2842e-06,330.78
submission_raw05_jepa_axislocal_e286f237.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,q2_s123,0.38,0.024,-4.3144e-06,6.83011e-05,0.5778270636,0.5769252598,1.222e-07,-0.0003363349,0.998734945,0.0688278475,0.0015518952,3.792e-06,330.92
submission_raw05_jepa_axislocal_e2af4e72.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,q2_s123,0.38,0.024,-4.3122e-06,6.83121e-05,0.5778270548,0.5769250419,1.243e-07,-0.000337259,0.998734945,0.0688278475,0.0015521419,3.7949e-06,331.6
submission_raw05_jepa_axislocal_d620ff36.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_4ea70364.csv,context_s4light,0.1,0.024,-4.2795e-06,6.76467e-05,0.5778277759,0.5769315876,1.44e-08,-0.0003682735,0.9999626269,0.0118371028,0.0015417168,5.3352e-06,332.44
submission_raw05_jepa_axislocal_fdcd8ce0.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,context_s4light,0.1,0.024,-4.2787e-06,6.76581e-05,0.5778277654,0.5769315293,1.6e-08,-0.0003684569,0.9999626269,0.0118371028,0.0015419275,5.3269e-06,333.02
submission_raw05_jepa_axislocal_9563f79c.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.22,0.024,-4.2636e-06,6.76427e-05,0.5778280137,0.5769297661,1.91e-08,-0.0003486138,0.9999471388,0.0140709775,0.0015415173,4.5572e-06,333.9
submission_raw05_jepa_axislocal_48477499.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_4732033b.csv,context_s4light,0.1,0.024,-4.2779e-06,6.76476e-05,0.5778277755,0.5769315366,1.46e-08,-0.0003685197,0.9999626269,0.0118371028,0.0015418253,5.3306e-06,333.98
submission_raw05_jepa_axislocal_180cac45.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,context_s4light,0.1,0.024,-4.2791e-06,6.76563e-05,0.5778277672,0.5769315809,1.55e-08,-0.000368326,0.9999626269,0.0118371028,0.0015418808,5.3352e-06,334.14
submission_raw05_jepa_axislocal_229cea69.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,q2_s123,0.56,0.024,-4.279e-06,6.86531e-05,0.5778268669,0.5769192716,2.335e-07,-0.0003422373,0.998734945,0.0688278475,0.001557603,4.187e-06,336.12
submission_raw05_jepa_axislocal_3b134d1c.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,all_soft,0.56,0.024,-4.2304e-06,6.80038e-05,0.5778279073,0.5769207941,9.61e-08,-0.0003254356,0.9986769403,0.0702789101,0.0015478415,2.4115e-06,336.48
submission_raw05_jepa_axislocal_3ff82bbd.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,q2_s123,0.56,0.024,-4.2758e-06,6.86693e-05,0.5778268539,0.5769189505,2.367e-07,-0.0003435999,0.998734945,0.0688278475,0.0015579668,4.1918e-06,336.82
submission_raw05_jepa_axislocal_20e4a625.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.1,0.024,-4.2943e-06,6.75676e-05,0.5778279293,0.5769332577,-2.23e-08,-0.0003491309,0.9999631914,0.0117455354,0.0015400756,5.3051e-06,336.9
submission_raw05_jepa_axislocal_29b02cca.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.1,0.024,-4.2929e-06,6.76536e-05,0.577827776,0.5769330125,-2.8e-09,-0.0003561172,0.9999623914,0.0118758525,0.0015417688,5.3922e-06,336.96
submission_raw05_jepa_axislocal_c7d00a0e.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,q2_s123,0.22,0.024,-4.3461e-06,6.79811e-05,0.5778272566,0.5769305561,2.37e-08,-0.000329547,0.998734945,0.0688278475,0.0015466921,4.4792e-06,337.72
submission_raw05_jepa_axislocal_e3e6088b.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_d15c7091.csv,context_s4light,0.1,0.024,-4.2793e-06,6.76636e-05,0.5778277494,0.576931612,1.63e-08,-0.0003698055,0.9999626269,0.0118371028,0.0015419905,5.3715e-06,338.06
submission_raw05_jepa_axislocal_fecd54e0.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.22,0.024,-4.2614e-06,6.78317e-05,0.5778276765,0.5769292265,6.2e-08,-0.0003639839,0.9999623914,0.0118758525,0.0015452403,4.7481e-06,338.52
submission_raw05_jepa_axislocal_2aee8450.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_c5b80c88.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.38,0.024,-4.2187e-06,6.8069e-05,0.5778275454,0.5769241802,1.499e-07,-0.0003744737,0.9999623914,0.0118758525,0.0015498993,4.5888e-06,338.68
submission_raw05_jepa_axislocal_85228cf6.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,context_s4light,0.38,0.024,-4.2669e-06,6.82983e-05,0.5778272796,0.5769193846,1.695e-07,-0.0003448849,0.9986754562,0.0703995477,0.0015520756,3.4287e-06,338.76
submission_raw05_jepa_axislocal_8e42ccc3.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,q2_s123,0.22,0.024,-4.3431e-06,6.79844e-05,0.5778272514,0.576930409,2.46e-08,-0.0003298578,0.998734945,0.0688278475,0.0015469529,4.4561e-06,339.6
submission_raw05_jepa_axislocal_f27703fa.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,q2_s123,0.38,0.024,-4.3137e-06,6.8325e-05,0.5778269979,0.5769253809,1.248e-07,-0.000343273,0.998734945,0.0688278475,0.0015522797,3.9944e-06,339.82
submission_raw05_jepa_axislocal_ef97cce5.csv,axislocal_rank_fallback,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.22,0.024,-4.3337e-06,6.77396e-05,0.5778276771,0.5769311317,-2.9e-08,-0.0003143212,0.9987612453,0.06806596,0.0015429209,4.2927e-06,340.0
submission_raw05_jepa_axislocal_e47f3490.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,q2_s123,0.22,0.024,-4.3444e-06,6.79893e-05,0.5778272408,0.5769305849,2.53e-08,-0.0003310876,0.998734945,0.0688278475,0.0015469031,4.5181e-06,342.44
submission_raw05_jepa_axislocal_adfbeee6.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,context_s4light,0.22,0.024,-4.3171e-06,6.7988e-05,0.5778273647,0.5769271825,5.18e-08,-0.0003360373,0.9987293858,0.0689619784,0.0015470037,3.9002e-06,345.88
submission_raw05_jepa_axislocal_219890aa.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,q2_s123,0.22,0.024,-4.344e-06,6.80031e-05,0.5778272028,0.576930655,2.69e-08,-0.0003351043,0.998734945,0.0688278475,0.0015471257,4.6142e-06,347.62
submission_raw05_jepa_axislocal_3446cf38.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,q2_s123,0.56,0.024,-4.278e-06,6.86884e-05,0.57782677,0.5769194498,2.372e-07,-0.0003524625,0.998734945,0.0688278475,0.0015581692,4.4832e-06,350.34
submission_raw05_jepa_axislocal_07a54561.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,context_s4light,0.22,0.024,-4.3008e-06,6.7942e-05,0.5778273766,0.5769270953,4.94e-08,-0.0003489721,0.9987293858,0.0689619784,0.0015469324,4.1561e-06,355.58
submission_raw05_jepa_axislocal_2ebf75c9.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,context_s4light,0.22,0.024,-4.3025e-06,6.79651e-05,0.5778273545,0.5769270791,5.24e-08,-0.0003488338,0.9987293858,0.0689619784,0.0015471599,4.148e-06,356.04
submission_raw05_jepa_axislocal_b1682acb.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,context_s4light,0.22,0.024,-4.3043e-06,6.79402e-05,0.5778273777,0.5769272074,4.91e-08,-0.0003484299,0.9987293858,0.0689619784,0.0015467008,4.1664e-06,356.08
submission_raw05_jepa_axislocal_a9d8e6a1.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,context_s4light,0.22,0.024,-4.3034e-06,6.79612e-05,0.5778273586,0.5769271927,5.13e-08,-0.0003485456,0.9987293858,0.0689619784,0.0015470545,4.1664e-06,357.6
submission_raw05_jepa_axislocal_7cb0aca7.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8656f234.csv,q2_s123,0.38,0.024,-4.2859e-06,6.82356e-05,0.577827101,0.5769251688,1.214e-07,-0.0003570161,0.998734945,0.0688278475,0.0015518206,4.2037e-06,360.74
submission_raw05_jepa_axislocal_d382d3c3.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,context_s4light,0.22,0.024,-4.3038e-06,6.79772e-05,0.5778273193,0.576927261,5.3e-08,-0.0003518011,0.9987293858,0.0689619784,0.0015472954,4.2461e-06,365.66
submission_raw05_jepa_axislocal_73f5bcdc.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8656f234.csv,context_s4light,0.22,0.024,-4.2834e-06,6.7902e-05,0.5778273904,0.5769272143,4.92e-08,-0.000363801,0.9987293858,0.0689619784,0.0015468223,4.4962e-06,381.64
submission_raw05_jepa_axislocal_ca615c9b.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,context,0.22,0.024,-4.2777e-06,6.80482e-05,0.5778271367,0.5769267253,9.74e-08,-0.0003693814,0.998734945,0.0688278475,0.0015501937,4.5016e-06,384.3
submission_raw05_jepa_axislocal_1cdd5a0b.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,context_s4light,0.1,0.024,-4.3546e-06,6.77549e-05,0.5778274311,0.5769330331,-3.42e-08,-0.0003294016,0.9987421398,0.068623705,0.0015432301,5.0071e-06,393.08
submission_raw05_jepa_axislocal_c8630a25.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,context_s4light,0.1,0.024,-4.3479e-06,6.77446e-05,0.5778274264,0.5769329861,-3.4e-08,-0.0003352182,0.9987421398,0.068623705,0.0015433011,5.1197e-06,396.38
submission_raw05_jepa_axislocal_17d1b5e6.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,context_s4light,0.1,0.024,-4.3472e-06,6.7734e-05,0.5778274365,0.5769329935,-3.54e-08,-0.0003352811,0.9987421398,0.068623705,0.001543196,5.1233e-06,398.1
submission_raw05_jepa_axislocal_1cb6d2d9.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,context_s4light,0.1,0.024,-4.3487e-06,6.77332e-05,0.5778274369,0.5769330445,-3.55e-08,-0.0003350346,0.9987421398,0.068623705,0.0015430916,5.128e-06,398.28
submission_raw05_jepa_axislocal_8b94a378.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,context_s4light,0.1,0.024,-4.3483e-06,6.77428e-05,0.5778274283,0.5769330377,-3.45e-08,-0.0003350872,0.9987421398,0.068623705,0.0015432531,5.128e-06,398.48
submission_raw05_jepa_axislocal_f0ee6894.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,context_s4light,0.1,0.024,-4.3485e-06,6.775e-05,0.5778274104,0.5769330688,-3.37e-08,-0.0003365669,0.9987421398,0.068623705,0.0015433627,5.1643e-06,400.38
submission_raw05_jepa_axislocal_85d40821.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,context,0.22,0.024,-4.2648e-06,6.80004e-05,0.5778271496,0.5769267503,9.46e-08,-0.0003817739,0.998734945,0.0688278475,0.0015498908,4.7678e-06,408.08
submission_raw05_jepa_axislocal_2300b0ad.csv,axislocal_balanced,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,context,0.22,0.024,-4.2643e-06,6.80375e-05,0.5778270912,0.5769268038,9.86e-08,-0.0003851451,0.998734945,0.0688278475,0.0015504854,4.8475e-06,413.54
submission_raw05_jepa_axislocal_16ae093a.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,q2_s123,0.1,0.024,-4.3725e-06,6.77658e-05,0.5778273783,0.5769345733,-4.56e-08,-0.0003221836,0.998734945,0.0688278475,0.0015431553,5.1893e-06,421.7
submission_raw05_jepa_axislocal_bea1b0ae.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,q2_s123,0.1,0.024,-4.3665e-06,6.77531e-05,0.5778273799,0.5769345001,-4.63e-08,-0.0003265928,0.998734945,0.0688278475,0.0015432067,5.2674e-06,428.48
submission_raw05_jepa_axislocal_8287e4ac.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,q2_s123,0.1,0.024,-4.3679e-06,6.77516e-05,0.5778273822,0.5769345669,-4.67e-08,-0.0003264516,0.998734945,0.0688278475,0.0015430889,5.2779e-06,428.92
submission_raw05_jepa_axislocal_03d828c3.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,q2_s123,0.1,0.024,-4.3665e-06,6.77583e-05,0.5778273727,0.5769345226,-4.54e-08,-0.0003273948,0.998734945,0.0688278475,0.0015432504,5.2884e-06,429.22
submission_raw05_jepa_axislocal_428d9f63.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,q2_s123,0.1,0.024,-4.3671e-06,6.77554e-05,0.577827375,0.57693458,-4.59e-08,-0.0003271518,0.998734945,0.0688278475,0.0015431856,5.2956e-06,431.3
submission_raw05_jepa_axislocal_c5dc138a.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_c512de3f.csv,all_soft,0.1,0.024,-4.3624e-06,6.76418e-05,0.5778275735,0.5769348286,-7.06e-08,-0.0003195306,0.998754591,0.0682715482,0.0015413752,5.1869e-06,431.4
submission_raw05_jepa_axislocal_4ba01ef7.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,q2_s123,0.1,0.024,-4.3669e-06,6.77616e-05,0.5778273578,0.5769346119,-4.52e-08,-0.0003289775,0.998734945,0.0688278475,0.0015432869,5.3394e-06,433.96
submission_raw05_jepa_axislocal_b5d99684.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_fd3a4de2.csv,all_soft,0.1,0.024,-4.3581e-06,6.76353e-05,0.5778275703,0.5769347977,-7.04e-08,-0.0003232508,0.998754591,0.0682715482,0.0015414237,5.2587e-06,435.78
submission_raw05_jepa_axislocal_976b5643.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4732033b.csv,all_soft,0.1,0.024,-4.3577e-06,6.7629e-05,0.5778275766,0.5769347995,-7.13e-08,-0.0003232052,0.998754591,0.0682715482,0.0015413615,5.2586e-06,435.98
submission_raw05_jepa_axislocal_82b8d670.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_4ea70364.csv,all_soft,0.1,0.024,-4.3587e-06,6.76284e-05,0.5778275771,0.5769348342,-7.14e-08,-0.0003230556,0.998754591,0.0682715482,0.0015412922,5.2623e-06,437.42
submission_raw05_jepa_axislocal_b7afefe6.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_a15f1a0d.csv,all_soft,0.1,0.024,-4.3584e-06,6.7634e-05,0.5778275716,0.5769348318,-7.08e-08,-0.0003231545,0.998754591,0.0682715482,0.0015413907,5.264e-06,437.66
submission_raw05_jepa_axislocal_f1c5cf23.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_d15c7091.csv,all_soft,0.1,0.024,-4.3585e-06,6.76387e-05,0.5778275601,0.5769348521,-7.02e-08,-0.0003241509,0.998754591,0.0682715482,0.0015414613,5.2883e-06,440.9
submission_raw05_jepa_axislocal_ad0a1a9f.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8656f234.csv,q2_s123,0.1,0.024,-4.3596e-06,6.77381e-05,0.5778273848,0.576934556,-4.62e-08,-0.0003325943,0.998734945,0.0688278475,0.0015431634,5.4066e-06,442.24
submission_raw05_jepa_axislocal_9a12f5a1.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8656f234.csv,all_soft,0.1,0.024,-4.3527e-06,6.76175e-05,0.5778275805,0.5769348348,-7.14e-08,-0.0003275126,0.998754591,0.0682715482,0.00154133,5.3576e-06,448.5
submission_raw05_jepa_axislocal_3e965062.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,q2_s123,0.1,0.024,-4.3486e-06,6.77313e-05,0.5778273529,0.5769346608,-4.44e-08,-0.0003456291,0.998734945,0.0688278475,0.0015433564,5.7014e-06,462.42
submission_raw05_jepa_axislocal_4b985b0c.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,all_soft,0.1,0.024,-4.3442e-06,6.7615e-05,0.5778275591,0.5769348637,-6.97e-08,-0.0003365999,0.998754591,0.0682715482,0.0015415254,5.5541e-06,464.14
submission_raw05_jepa_axislocal_cf984b3c.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8fd1c7e0.csv,q2_s123,0.1,0.024,-4.3439e-06,6.76982e-05,0.5778273465,0.5769350546,-4.53e-08,-0.000355483,0.998734945,0.0688278475,0.0015429263,5.9898e-06,503.78
submission_raw05_jepa_axislocal_1b268ffb.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_32fd3e55.csv,q2_s123,0.1,0.024,-4.3438e-06,6.76936e-05,0.57782735,0.5769350578,-4.55e-08,-0.0003557882,0.998734945,0.0688278475,0.0015428563,5.9967e-06,508.44
submission_raw05_jepa_axislocal_722a1204.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_8c9b57cc.csv,q2_s123,0.1,0.024,-4.3437e-06,6.77068e-05,0.5778273375,0.5769350839,-4.46e-08,-0.0003555825,0.998734945,0.0688278475,0.0015430678,5.9985e-06,508.46
submission_raw05_jepa_axislocal_11bde9b8.csv,axislocal_proxy,axis_context_repair,submission_raw05_jepa_axisrepair_5069cadb.csv,submission_raw05_jepa_siggate_78179445.csv,q2_s123,0.1,0.024,-4.3437e-06,6.76942e-05,0.577827349,0.5769350608,-4.55e-08,-0.0003558937,0.998734945,0.0688278475,0.0015428706,5.9996e-06,510.3
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_axislocal_7a15027d.csv,250,True,0,0,0.0630907874,0.9798298846
submission_raw05_jepa_axislocal_61adb42f.csv,250,True,0,0,0.0630875788,0.9798294285
submission_raw05_jepa_axislocal_58dd85e3.csv,250,True,0,0,0.0630879461,0.9798295202
submission_raw05_jepa_axislocal_0951e375.csv,250,True,0,0,0.0630897226,0.9798295081
submission_raw05_jepa_axislocal_8ac340a6.csv,250,True,0,0,0.0630902727,0.9798295618
submission_raw05_jepa_axislocal_68ca6074.csv,250,True,0,0,0.0630780395,0.979823203
submission_raw05_jepa_axislocal_a6c20f40.csv,250,True,0,0,0.0630900781,0.9798296674
submission_raw05_jepa_axislocal_90f36fb1.csv,250,True,0,0,0.0630780395,0.9798270457
submission_raw05_jepa_axislocal_e82848f1.csv,250,True,0,0,0.0630968268,0.9798273873
submission_raw05_jepa_axislocal_35929361.csv,250,True,0,0,0.0630876993,0.9798295347
submission_raw05_jepa_axislocal_d90f09cf.csv,250,True,0,0,0.0630751213,0.9798334175
submission_raw05_jepa_axislocal_717f9a0f.csv,250,True,0,0,0.0630920979,0.9798267151
submission_raw05_jepa_axislocal_f910365b.csv,250,True,0,0,0.0630952574,0.9798268323
submission_raw05_jepa_axislocal_01db9579.csv,250,True,0,0,0.0630926392,0.9798268502
submission_raw05_jepa_axislocal_c1874132.csv,250,True,0,0,0.0630780395,0.979826344
submission_raw05_jepa_axislocal_d458d8c6.csv,250,True,0,0,0.0630780395,0.979826485
submission_raw05_jepa_axislocal_f3bd9cde.csv,250,True,0,0,0.0630780395,0.9798223765
submission_raw05_jepa_axislocal_dae43698.csv,250,True,0,0,0.0630960681,0.9798269115
submission_raw05_jepa_axislocal_7075b9dc.csv,250,True,0,0,0.0630780395,0.9798221686
submission_raw05_jepa_axislocal_d3d23f68.csv,250,True,0,0,0.0630828613,0.9798302157
submission_raw05_jepa_axislocal_fb6f15f5.csv,250,True,0,0,0.0630780395,0.9798304609
submission_raw05_jepa_axislocal_e286f237.csv,250,True,0,0,0.0630780395,0.9798265491
submission_raw05_jepa_axislocal_e2af4e72.csv,250,True,0,0,0.0630780395,0.9798264664
submission_raw05_jepa_axislocal_d620ff36.csv,250,True,0,0,0.0630737621,0.97983327
submission_raw05_jepa_axislocal_fdcd8ce0.csv,250,True,0,0,0.063074612,0.9798332651
submission_raw05_jepa_axislocal_9563f79c.csv,250,True,0,0,0.0630766125,0.979832481
submission_raw05_jepa_axislocal_48477499.csv,250,True,0,0,0.0630735865,0.9798332329
submission_raw05_jepa_axislocal_180cac45.csv,250,True,0,0,0.0630748751,0.9798332869
submission_raw05_jepa_axislocal_229cea69.csv,250,True,0,0,0.0630780395,0.9798224709
submission_raw05_jepa_axislocal_3b134d1c.csv,250,True,0,0,0.0630957814,0.9798270671
submission_raw05_jepa_axislocal_3ff82bbd.csv,250,True,0,0,0.0630780395,0.9798223491
submission_raw05_jepa_axislocal_20e4a625.csv,250,True,0,0,0.0630719262,0.9798341798
submission_raw05_jepa_axislocal_29b02cca.csv,250,True,0,0,0.0630680212,0.9798334175
submission_raw05_jepa_axislocal_c7d00a0e.csv,250,True,0,0,0.0630780395,0.9798301363
submission_raw05_jepa_axislocal_e3e6088b.csv,250,True,0,0,0.063074782,0.9798333296
submission_raw05_jepa_axislocal_fecd54e0.csv,250,True,0,0,0.0630680212,0.9798308038
submission_raw05_jepa_axislocal_2aee8450.csv,250,True,0,0,0.0630680212,0.9798273184
submission_raw05_jepa_axislocal_85228cf6.csv,250,True,0,0,0.0631012193,0.9798270457
submission_raw05_jepa_axislocal_8e42ccc3.csv,250,True,0,0,0.0630780395,0.9798300547
submission_raw05_jepa_axislocal_f27703fa.csv,250,True,0,0,0.0630780395,0.9798267115
submission_raw05_jepa_axislocal_ef97cce5.csv,250,True,0,0,0.0630854196,0.9798321042
submission_raw05_jepa_axislocal_e47f3490.csv,250,True,0,0,0.0630780395,0.9798301734
submission_raw05_jepa_axislocal_adfbeee6.csv,250,True,0,0,0.0630914584,0.9798304609
submission_raw05_jepa_axislocal_219890aa.csv,250,True,0,0,0.0630780395,0.9798302674
submission_raw05_jepa_axislocal_3446cf38.csv,250,True,0,0,0.0630780395,0.9798227103
submission_raw05_jepa_axislocal_07a54561.csv,250,True,0,0,0.063088081,0.9798300547
submission_raw05_jepa_axislocal_2ebf75c9.csv,250,True,0,0,0.0630903376,0.9798301255
submission_raw05_jepa_axislocal_b1682acb.csv,250,True,0,0,0.0630884675,0.9798301363
submission_raw05_jepa_axislocal_a9d8e6a1.csv,250,True,0,0,0.0630909166,0.9798301734
submission_raw05_jepa_axislocal_7cb0aca7.csv,250,True,0,0,0.0630780395,0.9798265074
submission_raw05_jepa_axislocal_d382d3c3.csv,250,True,0,0,0.0630907118,0.9798302674
submission_raw05_jepa_axislocal_73f5bcdc.csv,250,True,0,0,0.0630882078,0.9798301493
submission_raw05_jepa_axislocal_ca615c9b.csv,250,True,0,0,0.0630914584,0.9798304609
submission_raw05_jepa_axislocal_1cdd5a0b.csv,250,True,0,0,0.0630841387,0.9798330219
submission_raw05_jepa_axislocal_c8630a25.csv,250,True,0,0,0.0630836293,0.9798328695
submission_raw05_jepa_axislocal_17d1b5e6.csv,250,True,0,0,0.0630826036,0.9798328373
submission_raw05_jepa_axislocal_1cb6d2d9.csv,250,True,0,0,0.0630827793,0.9798328744
submission_raw05_jepa_axislocal_8b94a378.csv,250,True,0,0,0.0630838924,0.9798328912
submission_raw05_jepa_axislocal_f0ee6894.csv,250,True,0,0,0.0630837994,0.9798329339
submission_raw05_jepa_axislocal_85d40821.csv,250,True,0,0,0.0630884675,0.9798301363
submission_raw05_jepa_axislocal_2300b0ad.csv,250,True,0,0,0.0630907118,0.9798302674
submission_raw05_jepa_axislocal_16ae093a.csv,250,True,0,0,0.0630780395,0.9798330219
submission_raw05_jepa_axislocal_bea1b0ae.csv,250,True,0,0,0.0630780395,0.9798328373
submission_raw05_jepa_axislocal_8287e4ac.csv,250,True,0,0,0.0630780395,0.9798328744
submission_raw05_jepa_axislocal_03d828c3.csv,250,True,0,0,0.0630780395,0.9798328695
submission_raw05_jepa_axislocal_428d9f63.csv,250,True,0,0,0.0630780395,0.9798328912
submission_raw05_jepa_axislocal_c5dc138a.csv,250,True,0,0,0.063081394,0.9798337688
submission_raw05_jepa_axislocal_4ba01ef7.csv,250,True,0,0,0.0630780395,0.9798329339
submission_raw05_jepa_axislocal_b5d99684.csv,250,True,0,0,0.0630811138,0.9798336697
submission_raw05_jepa_axislocal_976b5643.csv,250,True,0,0,0.0630805497,0.9798336488
submission_raw05_jepa_axislocal_82b8d670.csv,250,True,0,0,0.0630806464,0.9798336729
submission_raw05_jepa_axislocal_b7afefe6.csv,250,True,0,0,0.0630812586,0.9798336839
submission_raw05_jepa_axislocal_f1c5cf23.csv,250,True,0,0,0.0630812074,0.9798337116
submission_raw05_jepa_axislocal_ad0a1a9f.csv,250,True,0,0,0.0630780395,0.9798328803
submission_raw05_jepa_axislocal_9a12f5a1.csv,250,True,0,0,0.0630805815,0.9798336767
submission_raw05_jepa_axislocal_3e965062.csv,250,True,0,0,0.0630780395,0.9798328886
submission_raw05_jepa_axislocal_4b985b0c.csv,250,True,0,0,0.0630818941,0.9798336821
submission_raw05_jepa_axislocal_cf984b3c.csv,250,True,0,0,0.0630780395,0.9798342856
submission_raw05_jepa_axislocal_1b268ffb.csv,250,True,0,0,0.0630780395,0.9798342841
submission_raw05_jepa_axislocal_722a1204.csv,250,True,0,0,0.0630780395,0.979834135
submission_raw05_jepa_axislocal_11bde9b8.csv,250,True,0,0,0.0630780395,0.9798342864
```