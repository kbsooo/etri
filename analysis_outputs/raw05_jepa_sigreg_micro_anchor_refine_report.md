# Raw05 JEPA SIGReg Micro Anchor Refine

This pass keeps the LeJEPA/SIGReg gate but restricts the search around efmicro/energyfront actual anchors.
It tests whether low-bad siggate moves can be pulled back toward efmicro without losing the residual-health benefit.

## Counts

- generated candidates: 30720
- actual-anchor and quick-SIGReg rescored candidates: 1840
- saved candidates: 63

## Top Saved

```csv
file,bucket,direction,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,quick_lejepa_health,anchor_rank_score,energy_delta_vs_base,public_norm_delta_mean,row_aniso_delta_mean,blend_profile,beta,row_gate,gate_mean,base_file,donor_file
submission_raw05_jepa_siganchor_e9c6f925.csv,siganchor_balanced,micro_to_lowbad,0.577839099,0.5768992339,9.5e-08,0.0003986834,10.5182342828,410.2,-0.0010248547,-0.0041691889,-0.001000683,q2s1heavy,0.32,anchor_energy_f020,0.3858161684,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_747dbe4e.csv,siganchor_balanced,micro_to_lowbad,0.5778390967,0.5768993501,9.57e-08,0.0004018547,9.9375397425,426.14,-0.0001901067,-0.0023151069,-0.0016284624,q2s1heavy,0.32,anchor_balance_f015,0.4098808743,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_9b102b42.csv,siganchor_balanced,micro_to_lowbad,0.5778390807,0.5768993528,9.53e-08,0.0003993854,10.4890987176,435.06,-0.0005100041,-0.0036134704,-0.0010190406,q2s1heavy,0.32,anchor_energy_f020,0.3889054861,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_31a0f6bd.csv
submission_raw05_jepa_siganchor_ff03913f.csv,siganchor_balanced,micro_to_lowbad,0.5778391213,0.5768992682,9.26e-08,0.0004048746,9.7656652631,449.28,-0.0010869958,-0.0052926125,-0.0007260105,q1light,0.32,anchor_energy_f020,0.3885730227,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
submission_raw05_jepa_siganchor_3976f642.csv,siganchor_balanced,micro_to_lowbad,0.5778390984,0.5768993711,9.28e-08,0.0004051731,10.3326786214,459.8,-0.001018197,-0.0049991252,-0.0007205834,target_tiny,0.32,anchor_energy_f020,0.3918754778,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_a67c8ba3.csv
submission_raw05_jepa_siganchor_917d2cf5.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390843,0.576899335,9.51e-08,0.0003996671,10.8861467132,466.3,-0.0006409464,-0.0037274659,-0.0010046395,q2s1heavy,0.32,anchor_energy_f020,0.390516417,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_37659959.csv
submission_raw05_jepa_siganchor_d8591000.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390807,0.5768993741,9.5e-08,0.000399496,10.846476024,473.7,-0.0006868493,-0.0036387606,-0.0009543379,q2s1heavy,0.32,anchor_energy_f020,0.3961003936,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_64220cc6.csv
submission_raw05_jepa_siganchor_e64d77b6.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390939,0.5768992804,9.55e-08,0.0004057565,11.0353309491,480.84,-0.0007297538,-0.0033754105,-0.0013932269,q1light,0.32,anchor_energy_f020,0.4102485679,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_7c006368.csv
submission_raw05_jepa_siganchor_fe55966d.csv,siganchor_balanced,micro_to_lowbad,0.5778391193,0.5768992549,9.29e-08,0.000412236,10.1141709211,484.14,-0.0004574305,-0.003530888,-0.0011140026,q2s1heavy,0.32,anchor_energy_f020,0.3917449386,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_9ce9bb53.csv
submission_raw05_jepa_siganchor_87185273.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390835,0.5768993584,9.5e-08,0.0003984817,11.0154502254,484.46,-0.0004936552,-0.0037574347,-0.001015234,q2s1heavy,0.32,anchor_energy_f020,0.3935218972,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_ff1af2d8.csv
submission_raw05_jepa_siganchor_315c69d5.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778391101,0.5768993175,9.56e-08,0.0003962692,10.90820036,486.6,-0.0001122378,-0.0023151069,-0.0016284624,q2s1heavy,0.32,anchor_bad_f015,0.4022018153,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_e088bd95.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778391053,0.5768993748,9.31e-08,0.0004042494,10.6718354932,493.96,-0.0005619384,-0.0047058283,-0.0007983597,q1light,0.32,anchor_energy_f020,0.3969010825,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_31a0f6bd.csv
submission_raw05_jepa_siganchor_0aedf13d.csv,siganchor_balanced,micro_to_lowbad,0.5778391158,0.5768992477,9.33e-08,0.0004121809,10.5287777938,494.64,-0.0004057514,-0.0032392437,-0.0010522065,q2s1heavy,0.32,anchor_energy_f020,0.3897855601,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_31a0f6bd.csv
submission_raw05_jepa_siganchor_6ec4c4ba.csv,siganchor_balanced,micro_to_lowbad,0.5778390817,0.576899374,9.28e-08,0.0004321852,9.5587829017,495.26,-0.0006507559,-0.0033042157,-0.0004979852,q1light,0.22,anchor_energy_f020,0.3948684947,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_a67c8ba3.csv
submission_raw05_jepa_siganchor_a7d7b0a8.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778391085,0.5768993528,9.3e-08,0.0004046463,10.7788022473,498.5,-0.0006768632,-0.004829168,-0.0007792445,q1light,0.32,anchor_energy_f020,0.3956134188,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_37659959.csv
submission_raw05_jepa_siganchor_6e3db778.csv,siganchor_balanced,micro_to_lowbad,0.5778391031,0.5768993665,9.24e-08,0.0004305461,8.9070091856,501.14,-0.0003739844,-0.0032367013,-0.0005453647,q1light,0.22,anchor_balance_f015,0.4019075186,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_882fa552.csv,siganchor_balanced,micro_to_lowbad,0.5778390518,0.5768993694,9.58e-08,0.0004298864,10.4775312657,511.54,-0.0003555689,-0.0012931168,-0.0010190399,q2s1heavy,0.22,anchor_energy_f020,0.4029868583,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_238cd3c9.csv
submission_raw05_jepa_siganchor_02f8046f.csv,siganchor_balanced,micro_to_lowbad,0.5778391379,0.5768993113,9.35e-08,0.0003921989,10.3150370079,517.28,-0.0003526492,-0.0041697116,-0.0009906304,q2s1heavy,0.32,anchor_bad_f015,0.3785305115,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_78179445.csv
submission_raw05_jepa_siganchor_510ccfe0.csv,siganchor_balanced,micro_to_lowbad,0.5778390688,0.576899365,9.4e-08,0.0004284341,10.5894642959,517.5,-0.0006356285,-0.0025371486,-0.0006792793,q2s1heavy,0.22,anchor_energy_f020,0.3923259737,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_a67c8ba3.csv
submission_raw05_jepa_siganchor_f0311a3d.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390864,0.5768993369,9.49e-08,0.0003988123,11.3564985851,519.74,-0.0006340268,-0.0038355235,-0.0010015915,q2s1heavy,0.32,anchor_energy_f020,0.393096493,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_7386e192.csv
submission_raw05_jepa_siganchor_3644a42f.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778390951,0.5768992188,9.53e-08,0.0003999823,11.5539735081,520.8,-0.0010928617,-0.0039244881,-0.0010476016,q2s1heavy,0.32,anchor_energy_f020,0.3876312825,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_0f356183.csv,siganchor_rank_fallback,micro_to_lowbad,0.5778391065,0.5768991619,9.52e-08,0.0004150811,11.0816376791,522.0,-0.0006415532,-0.0018606382,-0.001515254,q2s1heavy,0.32,anchor_energy_f020,0.3998266981,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_238cd3c9.csv
submission_raw05_jepa_siganchor_0bef12ed.csv,siganchor_balanced,micro_to_lowbad,0.5778391503,0.5768992598,9.21e-08,0.0004034115,9.1697536625,523.88,-0.0007198807,-0.0050831262,-0.0007925767,q1light,0.32,anchor_balance_f015,0.3968209212,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_f100c9ca.csv,siganchor_balanced,micro_to_lowbad,0.5778391322,0.5768993036,9.23e-08,0.0004059635,10.4434995855,525.58,-5.74287e-05,-0.0037505254,-0.0009195972,context_only,0.32,anchor_energy_f020,0.3991792803,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_a2a3ffdd.csv
submission_raw05_jepa_siganchor_14b90145.csv,siganchor_balanced,micro_to_lowbad,0.5778391103,0.5768993636,9.22e-08,0.0004203119,10.3557925284,528.08,-9.11075e-05,-0.0023712668,-0.0009898656,context_only,0.22,anchor_bad_f015,0.4047376687,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_f1d4aa98.csv,siganchor_balanced,micro_to_lowbad,0.5778391225,0.5768993376,9.13e-08,0.0004163311,10.1592221443,530.44,-0.0002760694,-0.0041302521,-0.0008134297,target_tiny,0.32,anchor_energy_f020,0.3980880882,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_ff1af2d8.csv
submission_raw05_jepa_siganchor_18f18dd5.csv,siganchor_balanced,micro_to_lowbad,0.57783911,0.5768993587,9.24e-08,0.0004200226,10.469242192,533.16,-0.0001285599,-0.0022718018,-0.0009043483,context_only,0.22,anchor_bad_f015,0.4000159845,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_238cd3c9.csv
submission_raw05_jepa_siganchor_1fb767c1.csv,siganchor_balanced,micro_to_lowbad,0.5778391317,0.5768991566,9.27e-08,0.0004128357,10.5514366594,533.22,-0.0010405874,-0.0036627593,-0.0010028919,q2s1heavy,0.32,anchor_energy_f020,0.3912582418,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_a67c8ba3.csv
submission_raw05_jepa_siganchor_45720e4a.csv,siganchor_health,micro_to_lowbad,0.577839126,0.5768992793,9.2e-08,0.0004420389,9.2202662578,556.42,-0.0005656347,-0.0032358559,-0.001227275,q1light,0.32,anchor_energy_f020,0.4034304852,submission_raw05_jepa_efmicro_e137a6d9.csv,submission_raw05_jepa_siggate_238cd3c9.csv
submission_raw05_jepa_siganchor_1908f81f.csv,siganchor_health,micro_to_lowbad,0.5778397019,0.5768932185,8.9e-08,0.0004079568,9.7435574219,579.9,0.0003814067,-0.000324294,-0.0002265881,q2s1heavy,0.08,anchor_energy_f020,0.4210492796,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_36c116ba.csv,siganchor_health,micro_to_lowbad,0.5778397814,0.5768932,8.68e-08,0.0003810828,9.6812171728,593.86,0.0004773983,-0.0030202963,-0.0001428768,q1light,0.32,anchor_energy_f020,0.4020791291,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_78179445.csv
submission_raw05_jepa_siganchor_06023fbb.csv,siganchor_health,micro_to_lowbad,0.5778397152,0.5768932254,8.82e-08,0.0004080001,9.6960536092,621.06,0.0003300885,-0.0006870985,-5.29692e-05,q1light,0.08,anchor_bad_f015,0.4093390378,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_872d507b.csv
submission_raw05_jepa_siganchor_249e44ec.csv,siganchor_health,micro_to_lowbad,0.5778391509,0.5768993626,9.04e-08,0.0004265683,9.297482583,626.6,-9.88895e-05,-0.0028972541,-0.0012489782,target_tiny,0.32,anchor_bad_f015,0.4085753976,submission_raw05_jepa_efmicro_2609fc75.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_8a1c62fe.csv,siganchor_posterior,micro_to_lowbad,0.5778397183,0.5768932012,8.82e-08,0.0004078878,10.4455642613,646.9,0.0002843075,-0.0007671658,-5.88081e-05,q1light,0.08,anchor_bad_f015,0.4064065655,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_fc43eebf.csv,siganchor_posterior,micro_to_lowbad,0.5778397086,0.5768932,8.85e-08,0.0004091531,10.8570307689,655.94,0.000244433,-0.0006951085,-7.0591e-05,q1light,0.08,anchor_energy_f020,0.4170845578,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_d0813fd0.csv,siganchor_posterior,micro_to_lowbad,0.5778397821,0.5768931882,8.69e-08,0.0003808977,10.8755246108,658.4,0.0004566452,-0.003034494,-0.0001504743,q1light,0.32,anchor_energy_f020,0.400987377,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_c13da5b5.csv,siganchor_health,micro_to_lowbad,0.5778391868,0.5768992159,9.01e-08,0.0004102488,9.2113499325,666.66,-0.0001568556,-0.0046521836,-0.0007856527,q1light,0.32,anchor_bad_f015,0.3896727584,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_872d507b.csv
submission_raw05_jepa_siganchor_497f5c7f.csv,siganchor_health,micro_to_lowbad,0.5778391526,0.5768993737,8.91e-08,0.0004352628,9.7178676524,671.66,-0.0003174632,-0.0045761814,-0.0008989515,context_only,0.32,anchor_energy_f020,0.4006542858,submission_raw05_jepa_efmicro_2d129b1d.csv,submission_raw05_jepa_siggate_31a0f6bd.csv
submission_raw05_jepa_siganchor_85e81bd1.csv,siganchor_posterior,micro_to_lowbad,0.577839725,0.5768931975,8.82e-08,0.0004021802,10.9434298637,676.72,0.0003578662,-0.0012108315,-0.0001196546,q1light,0.14,anchor_energy_f020,0.4138517277,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_c3be67fc.csv,siganchor_posterior,micro_to_lowbad,0.5778397097,0.5768932027,8.84e-08,0.0004090085,11.1186956362,689.82,0.0002709561,-0.0007671658,-5.88081e-05,q1light,0.08,anchor_energy_f020,0.413232,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_dbbb68c0.csv,siganchor_health,micro_to_lowbad,0.5778391633,0.576899337,8.97e-08,0.0004385012,9.6570235055,695.42,-0.0001383631,-0.0037758818,-0.0010092145,q2s1heavy,0.32,anchor_balance_f015,0.3956032132,submission_raw05_jepa_efmicro_2d129b1d.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_d98671d8.csv,siganchor_health,micro_to_lowbad,0.5778391613,0.5768993576,8.95e-08,0.0004391852,9.6328162067,698.72,-0.0002510048,-0.0037375505,-0.0009802985,q2s1heavy,0.32,anchor_balance_f015,0.396118076,submission_raw05_jepa_efmicro_2d129b1d.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
submission_raw05_jepa_siganchor_48b81e6c.csv,siganchor_posterior,micro_to_lowbad,0.5778397415,0.5768932027,8.77e-08,0.0003998862,11.1275652413,700.44,0.0005059066,-0.0013366657,-9.99786e-05,q1light,0.14,anchor_bad_f015,0.4062804626,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_ce791303.csv,siganchor_posterior,micro_to_lowbad,0.5778397271,0.576893202,8.81e-08,0.0004019263,11.1946500654,707.52,0.0003889037,-0.0013366657,-9.99786e-05,q1light,0.14,anchor_energy_f020,0.4100236662,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_a375979a.csv,siganchor_health,micro_to_lowbad,0.5778391787,0.5768993536,8.8e-08,0.000424712,8.9325462353,713.14,-0.0002588482,-0.004729356,-0.0007388108,target_tiny,0.32,anchor_bad_f015,0.3942893596,submission_raw05_jepa_efmicro_2609fc75.csv,submission_raw05_jepa_siggate_78179445.csv
submission_raw05_jepa_siganchor_175b626c.csv,siganchor_health,micro_to_lowbad,0.5778391749,0.5768992536,8.94e-08,0.0004391938,9.6077096787,713.42,-0.0004153973,-0.0048014189,-0.000812036,q1light,0.32,anchor_balance_f015,0.4052061967,submission_raw05_jepa_efmicro_e137a6d9.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_e258cdbc.csv,siganchor_health,micro_to_lowbad,0.5778391729,0.5768993219,8.9e-08,0.0004342368,9.675941025,719.6,-6.52773e-05,-0.0033682497,-0.0014001293,context_only,0.32,anchor_balance_f015,0.4118251759,submission_raw05_jepa_efmicro_2d129b1d.csv,submission_raw05_jepa_siggate_c335d69e.csv
submission_raw05_jepa_siganchor_82a8730f.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.5778399369,0.576895008,9.64e-08,9.58118e-05,10.8070077887,730.98,-0.0006991695,-0.0002647192,0.0067451886,q2s1heavy,0.8,anchor_energy_f020,0.3376845576,submission_raw05_jepa_siggate_c335d69e.csv,submission_raw05_jepa_efmicro_1859bae9.csv
submission_raw05_jepa_siganchor_12f9ac2c.csv,siganchor_health,micro_to_lowbad,0.5778392119,0.5768993021,8.6e-08,0.0004148227,9.747024849,736.9,-0.0003557992,-0.0055523836,-0.000850412,context_only,0.32,anchor_bad_f015,0.3924355906,submission_raw05_jepa_efmicro_2609fc75.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
submission_raw05_jepa_siganchor_3936f8d3.csv,siganchor_posterior,micro_to_lowbad,0.5778397347,0.5768932007,8.79e-08,0.0004015288,11.4491764652,740.16,0.000457476,-0.0012108315,-0.0001196546,q1light,0.14,anchor_balance_f015,0.4056012917,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_6f73e497.csv,siganchor_posterior,micro_to_lowbad,0.5778397168,0.5768931976,8.83e-08,0.0004080941,11.5440668977,763.12,0.0002528352,-0.0006951085,-7.0591e-05,q1light,0.08,anchor_bad_f015,0.4107263948,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_296c98ae.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.5778399289,0.5768950527,9.75e-08,9.10881e-05,11.1052260819,763.68,-0.000671547,-0.0005987075,0.0068599498,q2s1heavy,0.8,anchor_energy_f020,0.3359820312,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_1859bae9.csv
submission_raw05_jepa_siganchor_28049df6.csv,siganchor_posterior,micro_to_lowbad,0.5778397388,0.5768931961,8.79e-08,0.0004002546,11.8811837139,797.92,0.000451408,-0.0012108315,-0.0001196546,q1light,0.14,anchor_bad_f015,0.4102388817,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_40debb1c.csv,siganchor_posterior,micro_to_lowbad,0.577839751,0.5768931976,8.75e-08,0.0003925288,11.9717876371,802.8,0.0004523398,-0.0020933155,-0.0001245905,q1light,0.22,anchor_energy_f020,0.406040354,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_e2da6744.csv,siganchor_posterior,micro_to_lowbad,0.5778397477,0.5768931909,8.78e-08,0.0003929265,12.1005941976,817.66,0.0004183331,-0.0018958304,-0.0001539777,q1light,0.22,anchor_energy_f020,0.410228762,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_f0ce6329.csv,siganchor_posterior,micro_to_lowbad,0.5778397771,0.5768931778,8.73e-08,0.0003815116,12.1488747586,823.16,0.000421235,-0.0027480038,-0.0001922558,q1light,0.32,anchor_energy_f020,0.4048849171,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_8cf6aa2c.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.5778399422,0.5768949802,9.6e-08,9.8971e-05,11.7621491259,851.76,-0.0009861335,-0.0009511207,0.0068674242,q2s1heavy,0.8,anchor_energy_f020,0.3343291545,submission_raw05_jepa_siggate_c335d69e.csv,submission_raw05_jepa_efmicro_6a71684b.csv
submission_raw05_jepa_siganchor_51613405.csv,siganchor_posterior,micro_to_lowbad,0.5778397144,0.5768932002,8.84e-08,0.0004088379,12.4320413141,877.68,0.0002586771,-0.0006951085,-7.0591e-05,q1light,0.08,anchor_balance_f015,0.4061929047,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_dad41c36.csv
submission_raw05_jepa_siganchor_f570bb2a.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.577839934,0.576895028,9.71e-08,9.40837e-05,11.9691115434,880.78,-0.0009528054,-0.0012851925,0.0069820472,q2s1heavy,0.8,anchor_energy_f020,0.3338426758,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_6a71684b.csv
submission_raw05_jepa_siganchor_c3133dd4.csv,siganchor_posterior,micro_to_lowbad,0.5778397157,0.5768932037,8.82e-08,0.0004086938,12.8519433565,919.86,0.0002887564,-0.0007671658,-5.88081e-05,q1light,0.08,anchor_balance_f015,0.4023045053,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_siggate_bccacd02.csv
submission_raw05_jepa_siganchor_8ac1b90d.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.577839943,0.5768949901,9.6e-08,9.63207e-05,12.2987901213,924.6,-0.0006251743,-0.0012094277,0.0068849485,q2s1heavy,0.8,anchor_energy_f020,0.3353534565,submission_raw05_jepa_siggate_c335d69e.csv,submission_raw05_jepa_efmicro_892e9c0c.csv
submission_raw05_jepa_siganchor_5200f93b.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.5778399347,0.5768950382,9.71e-08,9.1465e-05,12.5917723497,954.88,-0.0005990366,-0.0015435134,0.006999951,q2s1heavy,0.8,anchor_energy_f020,0.334970247,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_892e9c0c.csv
submission_raw05_jepa_siganchor_ff6a3604.csv,siganchor_recovered_lowbad,lowbad_to_micro,0.5778399283,0.5768950424,9.76e-08,9.35552e-05,13.820751839,1019.58,-0.0010577955,-0.0003209559,0.0068475363,q2s1heavy,0.8,anchor_energy_f020,0.3344788159,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_4c25b6c4.csv
```

## Best By Direction / Blend / Gate

```csv
direction,blend_profile,row_gate,beta,actual_anchor_score_final,posterior_expected_public_vs_anchor,bad_residual_axis_ratio,quick_lejepa_health,anchor_rank_score,base_file,donor_file
micro_to_lowbad,q2s1heavy,anchor_energy_f020,0.32,0.577839099,0.5768992339,0.0003986834,10.5182342828,410.2,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_bccacd02.csv
micro_to_lowbad,q2s1heavy,anchor_balance_f015,0.32,0.5778390967,0.5768993501,0.0004018547,9.9375397425,426.14,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_c335d69e.csv
micro_to_lowbad,q1light,anchor_energy_f020,0.32,0.5778391213,0.5768992682,0.0004048746,9.7656652631,449.28,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
micro_to_lowbad,target_tiny,anchor_energy_f020,0.32,0.5778390984,0.5768993711,0.0004051731,10.3326786214,459.8,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_a67c8ba3.csv
micro_to_lowbad,q2s1heavy,anchor_bad_f015,0.32,0.5778391101,0.5768993175,0.0003962692,10.90820036,486.6,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_c335d69e.csv
micro_to_lowbad,q1light,anchor_balance_f015,0.22,0.5778391031,0.5768993665,0.0004305461,8.9070091856,501.14,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_dad41c36.csv
micro_to_lowbad,context_only,anchor_energy_f020,0.32,0.5778391322,0.5768993036,0.0004059635,10.4434995855,525.58,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_a2a3ffdd.csv
micro_to_lowbad,context_only,anchor_bad_f015,0.22,0.5778391103,0.5768993636,0.0004203119,10.3557925284,528.08,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_c335d69e.csv
micro_to_lowbad,q1light,anchor_bad_f015,0.22,0.5778391152,0.5768993646,0.0004263283,10.4160296197,552.9,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
micro_to_lowbad,target_tiny,anchor_bad_f015,0.32,0.577839143,0.5768993482,0.0003964726,10.3891169323,555.96,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_cbd3e2e3.csv
micro_to_lowbad,context_only,anchor_balance_f015,0.32,0.5778391331,0.5768993331,0.000394497,11.024544694,565.34,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_siggate_7c006368.csv
lowbad_to_micro,target_tiny,anchor_bad_f015,0.28,0.5778399744,0.5768946961,2.27155e-05,9.5536838466,567.7,submission_raw05_jepa_siggate_a2a3ffdd.csv,submission_raw05_jepa_efmicro_cfdf196e.csv
lowbad_to_micro,q1light,anchor_bad_f015,0.28,0.5778399686,0.5768947076,2.26456e-05,10.2789988953,576.04,submission_raw05_jepa_siggate_a2a3ffdd.csv,submission_raw05_jepa_efmicro_61a4476f.csv
micro_to_lowbad,target_tiny,anchor_balance_f015,0.32,0.5778391387,0.5768992747,0.0004151218,10.6315465437,591.18,submission_raw05_jepa_efmicro_63fc9157.csv,submission_raw05_jepa_siggate_7c006368.csv
lowbad_to_micro,q2s1heavy,anchor_bad_f015,0.28,0.5778400662,0.576893362,4.02849e-05,9.0461160761,615.22,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_892e9c0c.csv
lowbad_to_micro,q2s1heavy,anchor_energy_f020,0.28,0.5778400511,0.5768935178,4.85387e-05,9.4073082829,631.86,submission_raw05_jepa_siggate_7c006368.csv,submission_raw05_jepa_efmicro_6a71684b.csv
lowbad_to_micro,q1light,anchor_energy_f020,0.28,0.5778401286,0.5768946145,2.27512e-05,9.4253647591,648.68,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_efmicro_61a4476f.csv
lowbad_to_micro,q2s1heavy,anchor_balance_f015,0.28,0.5778400697,0.5768933903,5.24802e-05,10.0813706285,661.5,submission_raw05_jepa_siggate_c335d69e.csv,submission_raw05_jepa_efmicro_4c25b6c4.csv
lowbad_to_micro,q1light,anchor_balance_f015,0.28,0.5778401359,0.5768945397,2.11412e-05,10.5231008686,693.72,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_efmicro_3eece507.csv
lowbad_to_micro,context_only,anchor_bad_f015,0.28,0.5778401389,0.576894514,2.01193e-05,10.3101142322,696.42,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_efmicro_9f19106d.csv
lowbad_to_micro,target_tiny,anchor_energy_f020,0.44,0.5778401235,0.5768937341,5.3443e-05,10.187337121,708.06,submission_raw05_jepa_siggate_238cd3c9.csv,submission_raw05_jepa_efmicro_a89cd60b.csv
lowbad_to_micro,target_tiny,anchor_balance_f015,0.28,0.5778399695,0.5768947577,2.54081e-05,11.4411441901,743.62,submission_raw05_jepa_siggate_a2a3ffdd.csv,submission_raw05_jepa_efmicro_9f19106d.csv
lowbad_to_micro,context_only,anchor_balance_f015,0.28,0.5778401339,0.5768945651,2.37038e-05,10.8561394967,752.72,submission_raw05_jepa_siggate_6d681440.csv,submission_raw05_jepa_efmicro_26253469.csv
lowbad_to_micro,context_only,anchor_energy_f020,0.28,0.5778401398,0.576895516,2.03929e-05,10.038550122,766.92,submission_raw05_jepa_siggate_780f8874.csv,submission_raw05_jepa_efmicro_95f32967.csv
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_siganchor_e9c6f925.csv,250,True,0,0,0.0631649541,0.9798226102
submission_raw05_jepa_siganchor_747dbe4e.csv,250,True,0,0,0.0631656093,0.9798221478
submission_raw05_jepa_siganchor_9b102b42.csv,250,True,0,0,0.0631654307,0.9798227934
submission_raw05_jepa_siganchor_ff03913f.csv,250,True,0,0,0.063165266,0.9798224536
submission_raw05_jepa_siganchor_3976f642.csv,250,True,0,0,0.0631648073,0.9798223564
submission_raw05_jepa_siganchor_917d2cf5.csv,250,True,0,0,0.0631652918,0.9798227474
submission_raw05_jepa_siganchor_d8591000.csv,250,True,0,0,0.0631653299,0.9798228153
submission_raw05_jepa_siganchor_e64d77b6.csv,250,True,0,0,0.0631657296,0.9798220294
submission_raw05_jepa_siganchor_fe55966d.csv,250,True,0,0,0.063164746,0.9798227879
submission_raw05_jepa_siganchor_87185273.csv,250,True,0,0,0.0631653059,0.9798228044
submission_raw05_jepa_siganchor_315c69d5.csv,250,True,0,0,0.0631656106,0.979822146
submission_raw05_jepa_siganchor_e088bd95.csv,250,True,0,0,0.0631656024,0.9798225692
submission_raw05_jepa_siganchor_0aedf13d.csv,250,True,0,0,0.063164921,0.9798227944
submission_raw05_jepa_siganchor_6ec4c4ba.csv,250,True,0,0,0.0631648894,0.9798221887
submission_raw05_jepa_siganchor_a7d7b0a8.csv,250,True,0,0,0.0631655191,0.9798225429
submission_raw05_jepa_siganchor_6e3db778.csv,250,True,0,0,0.0631648978,0.9798221801
submission_raw05_jepa_siganchor_882fa552.csv,250,True,0,0,0.0631652858,0.9798221147
submission_raw05_jepa_siganchor_02f8046f.csv,250,True,0,0,0.0631649707,0.9798225423
submission_raw05_jepa_siganchor_510ccfe0.csv,250,True,0,0,0.0631646275,0.9798223014
submission_raw05_jepa_siganchor_f0311a3d.csv,250,True,0,0,0.0631651982,0.9798227577
submission_raw05_jepa_siganchor_3644a42f.csv,250,True,0,0,0.0631648629,0.9798225909
submission_raw05_jepa_siganchor_0f356183.csv,250,True,0,0,0.0631652874,0.9798223369
submission_raw05_jepa_siganchor_0bef12ed.csv,250,True,0,0,0.0631652596,0.9798224469
submission_raw05_jepa_siganchor_f100c9ca.csv,250,True,0,0,0.0631659439,0.9798224632
submission_raw05_jepa_siganchor_14b90145.csv,250,True,0,0,0.0631651181,0.9798219085
submission_raw05_jepa_siganchor_f1d4aa98.csv,250,True,0,0,0.0631647807,0.979822518
submission_raw05_jepa_siganchor_18f18dd5.csv,250,True,0,0,0.063165287,0.9798219774
submission_raw05_jepa_siganchor_1fb767c1.csv,250,True,0,0,0.06316433,0.9798226117
submission_raw05_jepa_siganchor_45720e4a.csv,250,True,0,0,0.0631649411,0.9798221728
submission_raw05_jepa_siganchor_1908f81f.csv,250,True,0,0,0.0631608808,0.9798164464
submission_raw05_jepa_siganchor_36c116ba.csv,250,True,0,0,0.0631606443,0.9798176373
submission_raw05_jepa_siganchor_06023fbb.csv,250,True,0,0,0.0631607993,0.97981642
submission_raw05_jepa_siganchor_249e44ec.csv,250,True,0,0,0.0631647975,0.9798219635
submission_raw05_jepa_siganchor_8a1c62fe.csv,250,True,0,0,0.0631607787,0.9798163875
submission_raw05_jepa_siganchor_fc43eebf.csv,250,True,0,0,0.0631607651,0.979816419
submission_raw05_jepa_siganchor_d0813fd0.csv,250,True,0,0,0.0631606636,0.9798176366
submission_raw05_jepa_siganchor_c13da5b5.csv,250,True,0,0,0.063164899,0.9798224702
submission_raw05_jepa_siganchor_497f5c7f.csv,250,True,0,0,0.0631642741,0.9798225249
submission_raw05_jepa_siganchor_85e81bd1.csv,250,True,0,0,0.0631607289,0.9798167223
submission_raw05_jepa_siganchor_c3be67fc.csv,250,True,0,0,0.063160776,0.9798164201
submission_raw05_jepa_siganchor_dbbb68c0.csv,250,True,0,0,0.0631639029,0.9798225776
submission_raw05_jepa_siganchor_d98671d8.csv,250,True,0,0,0.0631638252,0.9798225749
submission_raw05_jepa_siganchor_48b81e6c.csv,250,True,0,0,0.0631607527,0.9798166671
submission_raw05_jepa_siganchor_ce791303.csv,250,True,0,0,0.0631607479,0.9798167242
submission_raw05_jepa_siganchor_a375979a.csv,250,True,0,0,0.0631641224,0.9798223069
submission_raw05_jepa_siganchor_175b626c.csv,250,True,0,0,0.0631643789,0.9798224041
submission_raw05_jepa_siganchor_e258cdbc.csv,250,True,0,0,0.063164535,0.9798219578
submission_raw05_jepa_siganchor_82a8730f.csv,250,True,0,0,0.0631643057,0.9798259052
submission_raw05_jepa_siganchor_12f9ac2c.csv,250,True,0,0,0.0631637521,0.9798223781
submission_raw05_jepa_siganchor_3936f8d3.csv,250,True,0,0,0.0631607361,0.9798167427
submission_raw05_jepa_siganchor_6f73e497.csv,250,True,0,0,0.0631607685,0.9798163863
submission_raw05_jepa_siganchor_296c98ae.csv,250,True,0,0,0.0631644782,0.9798258915
submission_raw05_jepa_siganchor_28049df6.csv,250,True,0,0,0.0631607348,0.9798166651
submission_raw05_jepa_siganchor_40debb1c.csv,250,True,0,0,0.0631607102,0.9798171298
submission_raw05_jepa_siganchor_e2da6744.csv,250,True,0,0,0.0631606803,0.9798171267
submission_raw05_jepa_siganchor_f0ce6329.csv,250,True,0,0,0.0631606204,0.9798176322
submission_raw05_jepa_siganchor_8cf6aa2c.csv,250,True,0,0,0.0631641921,0.9798258896
submission_raw05_jepa_siganchor_51613405.csv,250,True,0,0,0.0631607693,0.9798164308
submission_raw05_jepa_siganchor_f570bb2a.csv,250,True,0,0,0.0631643703,0.9798258643
submission_raw05_jepa_siganchor_c3133dd4.csv,250,True,0,0,0.0631607794,0.9798164317
submission_raw05_jepa_siganchor_8ac1b90d.csv,250,True,0,0,0.063164199,0.979825939
submission_raw05_jepa_siganchor_5200f93b.csv,250,True,0,0,0.0631643775,0.9798259166
submission_raw05_jepa_siganchor_ff6a3604.csv,250,True,0,0,0.0631644733,0.9798258056
```
