# Compatibility-Band Local LB Addendum

This addendum merges the raw05 JEPA compatibility-band refinement candidates with the local public-LB proxy and the deterministic LeJEPA/SIGReg audit.

## Local LB Proxy Resolution

- Best independent local proxy: `loocv_ridge_abs_axes_a1`
- LOOCV MAE: `0.0003184931`
- LOOCV RMSE: `0.0004029881`
- Max held-out error: `0.0006141185`
- Practical read: compat-band candidates with raw05-relative deltas around `-0.000003` are locally indistinguishable from raw05 because the validation error is about two orders of magnitude larger.

## Finalist Split

- `compatband_fullsigreg_probe`: best compromise under full LeJEPA/SIGReg audit plus compatibility band.
- `local_lowbad_stress_only`: best local raw05-relative/bad-axis probes, but not primary finalists because full residual health is weaker.
- Full audit coverage: `37` / `88`

## Recommended Compat-Band Probes

```csv
file,selection_role,actual_anchor_score_final,raw05_relative_lb_proxy_mean,raw05_relative_delta_vs_raw05_public,bad_residual_axis_ratio,compat_kl_mean_delta_vs_raw05,quick_lejepa_health,lejepa_residual_health,lejepa_combined_rank,base_file,donor_file,blend_profile,beta,row_gate
submission_raw05_jepa_compatband_e065e98e.csv,compatband_fullsigreg_probe,0.5778387572998541,0.5775238437858066,-2.4634141934098963e-06,0.0004990733682937,-0.0007319736248052,10.098179408409544,10.049556590184928,64.65,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_abc94f31.csv,compatband_fullsigreg_probe,0.5778387566829201,0.5775238490131855,-2.45818681443577e-06,0.0005012897142214,-0.0007319793250465,11.597333937771332,10.1316899678049,67.25,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_a89cd60b.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_57c2f1e7.csv,compatband_fullsigreg_probe,0.5778388247305095,0.5775238247567365,-2.482443263507328e-06,0.000485030141428,-0.0007319930051821,11.475072061520804,10.067782671183608,68.65,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_siganchor_3644a42f.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_1d434b47.csv,local_lowbad_stress_only,0.5778401686624489,0.5775231093271134,-3.1978728866066675e-06,6.991601485786056e-06,-0.0007323989035098,11.951890362720905,10.09563064115722,110.5,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.22,ones
submission_raw05_jepa_compatband_cbdfe8f4.csv,local_lowbad_stress_only,0.5778401652888352,0.5775231069672917,-3.2002327082780724e-06,6.72172083477332e-06,-0.0007323779159005,12.428780280987102,10.18580819304911,111.1,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.58,bad_soft
submission_raw05_jepa_compatband_f61b4f40.csv,local_lowbad_stress_only,0.5778401755028119,0.577523108795663,-3.198404336934857e-06,6.507885815533379e-06,-0.0007323881129403,11.24695920752492,10.277767724215543,113.3,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.32,bad_soft
submission_raw05_jepa_compatband_a5965ec3.csv,local_lowbad_stress_only,0.5778401707992379,0.5775231079875113,-3.1992124887025852e-06,6.632525679575485e-06,-0.0007323832426326,11.005443436195648,10.786224447736426,139.95000000000002,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.44,bad_soft

```

## Best By Full LeJEPA/SIGReg Combined Rank

```csv
file,selection_role,actual_anchor_score_final,raw05_relative_lb_proxy_mean,raw05_relative_delta_vs_raw05_public,bad_residual_axis_ratio,compat_kl_mean_delta_vs_raw05,quick_lejepa_health,lejepa_residual_health,lejepa_combined_rank,base_file,donor_file,blend_profile,beta,row_gate
submission_raw05_jepa_compatband_e065e98e.csv,compatband_fullsigreg_probe,0.5778387572998541,0.5775238437858066,-2.4634141934098963e-06,0.0004990733682937,-0.0007319736248052,10.098179408409544,10.049556590184928,64.65,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_abc94f31.csv,compatband_fullsigreg_probe,0.5778387566829201,0.5775238490131855,-2.45818681443577e-06,0.0005012897142214,-0.0007319793250465,11.597333937771332,10.1316899678049,67.25,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_a89cd60b.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_57c2f1e7.csv,compatband_fullsigreg_probe,0.5778388247305095,0.5775238247567365,-2.482443263507328e-06,0.000485030141428,-0.0007319930051821,11.475072061520804,10.067782671183608,68.65,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_siganchor_3644a42f.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_ccfdbe00.csv,compatband_pool,0.5778387560766769,0.577523854215607,-2.45298439294217e-06,0.0005034922959562,-0.000731986684705,10.829214877773564,10.314340610092474,71.4,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,q1light_context,0.44,compat_soft
submission_raw05_jepa_compatband_bde9d364.csv,compatband_pool,0.5778388116167835,0.5775239408523338,-2.3663476661495153e-06,0.0005608649926032,-0.0007320276133796,11.11414061617294,10.106580235890632,74.85000000000001,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_q3cwlocal_284f5ff5.csv,context_only,0.22,bad_compat_min
submission_raw05_jepa_compatband_978bf9df.csv,compatband_pool,0.5778388255987097,0.577523830001733,-2.4771982669591353e-06,0.00048603867655,-0.0007320128262011,12.782709874136676,10.455450718297916,80.00000000000001,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_siganchor_3644a42f.csv,q2s1_context,0.44,compat_soft
submission_raw05_jepa_compatband_357532d1.csv,compatband_pool,0.5778387626343787,0.5775238511333014,-2.456066698575121e-06,0.0005010032136001,-0.0007319899944612,11.10480744791168,10.529146935603343,82.80000000000001,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,q2s1_context,0.44,compat_soft
submission_raw05_jepa_compatband_fbd328b0.csv,compatband_pool,0.5778388069273392,0.57752392318883,-2.384011170031286e-06,0.0005498803983231,-0.0007320097341588,10.932322929490129,10.496804681350248,85.05000000000001,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_q3cwlocal_284f5ff5.csv,q2s1_context,0.22,bad_compat_min
submission_raw05_jepa_compatband_06684771.csv,compatband_pool,0.5778387929339243,0.5775238259927955,-2.4812072044744227e-06,0.0004887044645213,-0.000731983152284,10.406627945654062,10.617616081561051,88.75,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,all_soft,0.44,compat_soft
submission_raw05_jepa_compatband_41120959.csv,compatband_pool,0.5778387601942303,0.5775238784652981,-2.4287347019091854e-06,0.0005181138935039,-0.0007319730186484,11.41486812708738,10.6418924237758,91.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_1859bae9.csv,q1light_context,0.58,compat_soft
submission_raw05_jepa_compatband_55ef8f0c.csv,compatband_pool,0.5778388072987172,0.5775238374617605,-2.469738239474495e-06,0.000496791184811,-0.000731982743528,11.178569389265556,10.634633211891456,94.05,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_efmicro_1859bae9.csv,all_soft,0.58,compat_soft
submission_raw05_jepa_compatband_7bb594bf.csv,compatband_pool,0.5778388156989211,0.5775239284711925,-2.3787288074839097e-06,0.0005531461009398,-0.0007319917558838,12.35332276300806,10.656331298562527,98.45,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_q3cwlocal_cc8c19b4.csv,q2s1_context,0.22,bad_compat_min

```

## Best By Local Raw05-Relative Proxy

```csv
file,selection_role,actual_anchor_score_final,raw05_relative_lb_proxy_mean,raw05_relative_delta_vs_raw05_public,bad_residual_axis_ratio,compat_kl_mean_delta_vs_raw05,quick_lejepa_health,lejepa_residual_health,lejepa_combined_rank,base_file,donor_file,blend_profile,beta,row_gate
submission_raw05_jepa_compatband_cbdfe8f4.csv,local_lowbad_stress_only,0.5778401652888352,0.5775231069672917,-3.2002327082780724e-06,6.72172083477332e-06,-0.0007323779159005,12.428780280987102,10.18580819304911,111.1,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.58,bad_soft
submission_raw05_jepa_compatband_a5965ec3.csv,local_lowbad_stress_only,0.5778401707992379,0.5775231079875113,-3.1992124887025852e-06,6.632525679575485e-06,-0.0007323832426326,11.005443436195648,10.786224447736426,139.95000000000002,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.44,bad_soft
submission_raw05_jepa_compatband_f61b4f40.csv,local_lowbad_stress_only,0.5778401755028119,0.577523108795663,-3.198404336934857e-06,6.507885815533379e-06,-0.0007323881129403,11.24695920752492,10.277767724215543,113.3,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.32,bad_soft
submission_raw05_jepa_compatband_1d434b47.csv,local_lowbad_stress_only,0.5778401686624489,0.5775231093271134,-3.1978728866066675e-06,6.991601485786056e-06,-0.0007323989035098,11.951890362720905,10.09563064115722,110.5,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.22,ones
submission_raw05_jepa_compatband_436e5e31.csv,compatband_pool,0.5778401758653816,0.577523109334257,-3.197865742987638e-06,6.9567138083412034e-06,-0.0007323944774847,12.25021775403095,10.84139585850652,145.45,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.32,bad_soft
submission_raw05_jepa_compatband_3dfec56f.csv,compatband_pool,0.5778401794161775,0.5775231095475664,-3.1976524336174705e-06,6.4509791024521635e-06,-0.0007323923515037,12.60352982862106,10.784266693940438,140.15,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.22,bad_soft
submission_raw05_jepa_compatband_c3b5e614.csv,compatband_pool,0.5778401796179784,0.5775231099681255,-3.1972318744744044e-06,6.788978612359074e-06,-0.0007323967775211,12.041967756599425,11.260760534379692,158.65,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.22,bad_soft
submission_raw05_jepa_compatband_8c46256d.csv,compatband_pool,0.5778401757240902,0.577523110135783,-3.1970642170309205e-06,6.850840833852312e-06,-0.0007323989286205,13.664029216897625,10.493888730893634,123.1,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.14,ones
submission_raw05_jepa_compatband_c9b2edf0.csv,compatband_pool,0.5778401825580383,0.5775231102478939,-3.19695210604376e-06,6.465790171755079e-06,-0.0007323958212001,9.753877082130582,10.69996426705696,138.0,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.14,bad_soft
submission_raw05_jepa_compatband_5d8e0d75.csv,compatband_pool,0.5778401826316729,0.5775231105436666,-3.1966563334151488e-06,6.699322291033006e-06,-0.0007323984833562,11.403417996918476,10.916305243137328,149.60000000000002,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.14,bad_soft
submission_raw05_jepa_compatband_cd31b43d.csv,compatband_pool,0.577840181021271,0.5775231107424458,-3.1964575541998386e-06,6.745271253993071e-06,-0.0007323989471442,12.135304193692876,10.511109927636635,125.75,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.08,ones
submission_raw05_jepa_compatband_d8194901.csv,compatband_pool,0.5778401786235153,0.5775231107654738,-3.1964345261759064e-06,6.986098619823869e-06,-0.0007323921414589,11.12301791461945,10.790169232998156,143.1,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,all_soft,0.22,bad_soft

```

## Best By Bad-Axis

```csv
file,selection_role,actual_anchor_score_final,raw05_relative_lb_proxy_mean,raw05_relative_delta_vs_raw05_public,bad_residual_axis_ratio,compat_kl_mean_delta_vs_raw05,quick_lejepa_health,lejepa_residual_health,lejepa_combined_rank,base_file,donor_file,blend_profile,beta,row_gate
submission_raw05_jepa_compatband_3dfec56f.csv,compatband_pool,0.5778401794161775,0.5775231095475664,-3.1976524336174705e-06,6.4509791024521635e-06,-0.0007323923515037,12.60352982862106,10.784266693940438,140.15,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.22,bad_soft
submission_raw05_jepa_compatband_c9b2edf0.csv,compatband_pool,0.5778401825580383,0.5775231102478939,-3.19695210604376e-06,6.465790171755079e-06,-0.0007323958212001,9.753877082130582,10.69996426705696,138.0,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.14,bad_soft
submission_raw05_jepa_compatband_f61b4f40.csv,local_lowbad_stress_only,0.5778401755028119,0.577523108795663,-3.198404336934857e-06,6.507885815533379e-06,-0.0007323881129403,11.24695920752492,10.277767724215543,113.3,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.32,bad_soft
submission_raw05_jepa_compatband_a334a5f0.csv,compatband_pool,0.5778401848992286,0.5775231108290116,-3.1963709883342517e-06,6.52132938372048e-06,-0.0007323980355032,12.109834023767604,10.533200725827548,128.54999999999998,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.08,bad_soft
submission_raw05_jepa_compatband_a5965ec3.csv,local_lowbad_stress_only,0.5778401707992379,0.5775231079875113,-3.1992124887025852e-06,6.632525679575485e-06,-0.0007323832426326,11.005443436195648,10.786224447736426,139.95000000000002,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.44,bad_soft
submission_raw05_jepa_compatband_18606df8.csv,compatband_pool,0.577840184896948,0.5775231110265949,-3.1961734050511836e-06,6.672034050690862e-06,-0.0007323993449744,11.809780494211475,10.751343019443151,142.15,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.08,bad_soft
submission_raw05_jepa_compatband_5d8e0d75.csv,compatband_pool,0.5778401826316729,0.5775231105436666,-3.1966563334151488e-06,6.699322291033006e-06,-0.0007323984833562,11.403417996918476,10.916305243137328,149.60000000000002,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.14,bad_soft
submission_raw05_jepa_compatband_d6236d09.csv,compatband_pool,0.5778401846615789,0.5775231112716837,-3.195928316324093e-06,6.707086843264756e-06,-0.0007323980862585,9.665951992953731,10.586905762821765,131.8,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,all_soft,0.08,bad_soft
submission_raw05_jepa_compatband_cbdfe8f4.csv,local_lowbad_stress_only,0.5778401652888352,0.5775231069672917,-3.2002327082780724e-06,6.72172083477332e-06,-0.0007323779159005,12.428780280987102,10.18580819304911,111.1,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.58,bad_soft
submission_raw05_jepa_compatband_cd31b43d.csv,compatband_pool,0.577840181021271,0.5775231107424458,-3.1964575541998386e-06,6.745271253993071e-06,-0.0007323989471442,12.135304193692876,10.511109927636635,125.75,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q1light_context,0.08,ones
submission_raw05_jepa_compatband_c3b5e614.csv,compatband_pool,0.5778401796179784,0.5775231099681255,-3.1972318744744044e-06,6.788978612359074e-06,-0.0007323967775211,12.041967756599425,11.260760534379692,158.65,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,q2s1_context,0.22,bad_soft
submission_raw05_jepa_compatband_f43fefa5.csv,compatband_pool,0.5778401821208262,0.5775231110097174,-3.1961902825505817e-06,6.791682205435815e-06,-0.0007323957793829,11.841482356731056,10.970073328105778,152.15,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_siggate_fd0e9622.csv,all_soft,0.14,bad_soft

```

## Decision

The compatibility-band search produced useful probes but not a new primary frontier. `submission_raw05_jepa_compatband_e065e98e.csv` is the cleanest compat-band full-audit compromise, while `submission_raw05_jepa_compatband_cbdfe8f4.csv` and neighbors are stress-only low-bad probes. Local LB validation cannot prove any of these beats `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`; it can mainly reject candidates that move too far on public-failure axes.
