# Raw05 JEPA Axisbridge Posterior Repair

Repairs the posterior/energy weakness of axis-budget motif bridge candidates. Two JEPA-style transforms are tested: inject the axisbridge Q3/S4 target residual into posterior-safe A-family donors, and repair axisbridge context coordinates toward posterior-safe donors while preserving the target motif.

## Counts

- generated candidates: `53136`
- actual-anchor scored candidates: `2374`
- saved shortlist: `72`

## Profile Summary

```csv
mode,profile,n,best_actual,best_posterior,best_selection,best_raw_abs,best_bad_abs,best_motif_retention
donor_plus_axis_motif,inject_q3_sblockmicro,790,0.5778337846,0.5768858212,0.5778337846,0.0,3.888e-06,0.3677269584
donor_plus_axis_motif,inject_q3s4,244,0.5778320805,0.5768829397,0.5778359101,5.07e-08,7.6e-07,0.55
donor_plus_axis_motif,inject_q3_s4half,243,0.5778354662,0.5768847751,0.5778399207,3.55e-08,3.4937e-06,0.2969738243
donor_plus_axis_motif,inject_q3,197,0.5778345727,0.5768869901,0.577845527,6.63e-08,2.12386e-05,0.269579936
axis_plus_context_repair,repair_context_only,453,0.5778274878,0.5769287677,0.5778485463,2.13e-08,0.0002943618,1.0202270611
axis_plus_context_repair,repair_context_s4light,447,0.5778281668,0.5769298622,0.5778501653,1.554e-07,0.0002049825,0.9772708316
```

## Shortlist

```csv
file,bucket,mode,axis_file,donor_file,profile,gate_mode,beta,alpha,max_step,target_motif_retention,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_axis,mean_abs_move_vs_donor,mean_abs_move_vs_raw05,selection_score,rank_score
submission_raw05_jepa_axisrepair_2a20d67f.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778280076,0.5769325329,-4.03e-08,-0.0005638258,7.89957e-05,0.0002662377,0.0015425502,0.5778514105,748.12
submission_raw05_jepa_axisrepair_6b576311.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778280553,0.5769310976,-2.84e-08,-0.0006976461,7.5669e-05,0.0002631657,0.0015479541,0.5778502382,752.2
submission_raw05_jepa_axisrepair_a84ff361.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778280593,0.5769311325,-2.86e-08,-0.0007057498,7.59712e-05,0.0002634447,0.0015476591,0.5778502719,757.66
submission_raw05_jepa_axisrepair_fdbf4693.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.577828072,0.5769311039,-2.93e-08,-0.0007041965,7.59774e-05,0.0002634506,0.001547357,0.5778502603,758.0
submission_raw05_jepa_axisrepair_040eda76.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778283215,0.5769303012,-3.88e-08,-0.0006543408,8.12154e-05,0.0002682862,0.0015421459,0.5778498275,767.74
submission_raw05_jepa_axisrepair_7b48d2fc.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275706,0.5769360096,-3.45e-08,-0.0005396682,7.7703e-05,0.0002650448,0.0015431501,0.5778539288,779.38
submission_raw05_jepa_axisrepair_ec678291.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.577828022,0.576932278,-3.43e-08,-0.0007016408,7.9645e-05,0.0002668365,0.0015435711,0.5778512083,779.8
submission_raw05_jepa_axisrepair_78029f2c.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_fba45696.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3677269584,0.5778342834,0.5768945116,7.73e-08,-5.40195e-05,0.000270777,7.89038e-05,0.0015165162,0.5778342834,780.7
submission_raw05_jepa_axisrepair_07a92ed6.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_energyfront_a190aa25.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275398,0.5769364869,-3.84e-08,-0.0004698562,7.68897e-05,0.0002642926,0.0015418514,0.5778543036,783.58
submission_raw05_jepa_axisrepair_310ad461.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275751,0.5769360505,-3.47e-08,-0.0005484483,7.74005e-05,0.0002647655,0.0015428243,0.5778539681,784.16
submission_raw05_jepa_axisrepair_a225d175.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_04a3de62.csv,submission_raw05_jepa_efback_cc265f32.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778280537,0.5769324644,-3.73e-08,-0.0006920571,7.65475e-05,0.0002639776,0.0015465821,0.5778513984,786.68
submission_raw05_jepa_axisrepair_e0c6d751.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efmicro_9e631d75.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275926,0.5769360104,-3.56e-08,-0.0005462726,7.72867e-05,0.0002646604,0.001542397,0.5778539514,786.96
submission_raw05_jepa_axisrepair_7187ae3d.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_energyfront_a190aa25.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275439,0.5769365219,-3.85e-08,-0.0004779594,7.65986e-05,0.0002640239,0.0015415549,0.5778543374,786.98
submission_raw05_jepa_axisrepair_acf27bd8.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_energyfront_a190aa25.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275565,0.5769364932,-3.92e-08,-0.0004764068,7.66029e-05,0.000264028,0.0015412458,0.5778543257,787.2
submission_raw05_jepa_axisrepair_29fc9edf.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_siganchor_882fa552.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276501,0.5769357421,-3.61e-08,-0.0005579725,7.73199e-05,0.0002646908,0.0015422875,0.5778537808,791.0
submission_raw05_jepa_axisrepair_5d4dd19b.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_blockcountreg_50b1cf4a.csv,repair_context_only,none,,0.52,0.045,1.0081333209,0.5778282697,0.5769310336,-2.13e-08,-0.0009096249,7.85425e-05,0.0002674479,0.0015462113,0.5778539757,792.22
submission_raw05_jepa_axisrepair_c5b80c88.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_energyfront_fa0e1e2d.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778278597,0.5769361681,-5.6e-08,-0.0003495621,8.02454e-05,0.0002673893,0.0015388909,0.5778543527,792.74
submission_raw05_jepa_axisrepair_c167cb39.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_fba45696.csv,submission_raw05_jepa_tangentnull_2733815c.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3677269584,0.5778342552,0.5768943983,8.05e-08,-6.4426e-05,0.0002710634,7.89038e-05,0.0015171578,0.5778342552,795.8
submission_raw05_jepa_axisrepair_a3d71669.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276223,0.5769346091,-2.28e-08,-0.0006815955,7.43648e-05,0.0002619624,0.0015482631,0.5778527901,796.26
submission_raw05_jepa_axisrepair_aae22d53.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_blockcountreg_995c5b77.csv,repair_context_only,none,,0.52,0.045,1.0173378565,0.5778282237,0.5769325525,-3.7e-08,-0.0007669181,7.93742e-05,0.0002699075,0.0015407182,0.5778516433,796.66
submission_raw05_jepa_axisrepair_9b44d436.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276349,0.5769345805,-2.35e-08,-0.000680042,7.44234e-05,0.0002620166,0.0015479599,0.5778527783,796.66
submission_raw05_jepa_axisrepair_7217a889.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_blockcountreg_995c5b77.csv,repair_context_only,none,,0.52,0.045,1.0173378565,0.5778282736,0.5769311173,-2.49e-08,-0.0009007318,7.85287e-05,0.0002691259,0.0015460471,0.5778535173,797.06
submission_raw05_jepa_axisrepair_56b102d0.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_siganchor_3644a42f.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276708,0.5769356638,-3.63e-08,-0.0005735193,7.72401e-05,0.0002646171,0.00154236,0.5778537351,797.46
submission_raw05_jepa_axisrepair_47558ed9.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276227,0.5769346151,-2.29e-08,-0.0006822725,7.43552e-05,0.0002619535,0.0015482338,0.5778527955,797.64
submission_raw05_jepa_axisrepair_269e439d.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_energyfront_fa0e1e2d.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778279073,0.5769347327,-4.42e-08,-0.0004833702,7.71604e-05,0.0002645403,0.0015443494,0.5778531801,798.4
submission_raw05_jepa_axisrepair_3b2013ed.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_efmicro_9e631d75.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778276401,0.576934575,-2.38e-08,-0.0006800959,7.43036e-05,0.0002619057,0.0015478147,0.5778527789,798.72
submission_raw05_jepa_axisrepair_461b5197.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_blockcountreg_50b1cf4a.csv,repair_context_only,none,,0.52,0.045,1.0081333209,0.5778282735,0.5769310685,-2.14e-08,-0.0009177283,7.84341e-05,0.0002673478,0.0015459154,0.5778544955,798.92
submission_raw05_jepa_axisrepair_b7f2d6b9.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_blockcountreg_50b1cf4a.csv,repair_context_only,none,,0.52,0.045,1.0081333209,0.5778282198,0.5769324687,-3.34e-08,-0.0007758112,7.95293e-05,0.0002683599,0.0015408848,0.5778515682,799.34
submission_raw05_jepa_axisrepair_9cf6f179.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_blockcountreg_2bff1b8c.csv,repair_context_only,none,,0.52,0.045,1.0144947291,0.5778282555,0.5769316229,-2.16e-08,-0.0009123492,7.79903e-05,0.0002683048,0.0015455838,0.577854626,799.46
submission_raw05_jepa_axisrepair_a4c7ed33.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_blockcountreg_11801b21.csv,repair_context_only,none,,0.52,0.045,1.0085362766,0.5778282406,0.5769323891,-3.46e-08,-0.0007738885,7.96553e-05,0.000268539,0.0015407321,0.5778515213,800.12
submission_raw05_jepa_axisrepair_393ebf08.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778283695,0.5769288661,-2.67e-08,-0.0007881565,7.79166e-05,0.0002652398,0.0015475266,0.5778486557,800.38
submission_raw05_jepa_axisrepair_b7d70019.csv,repair_rank_fallback,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_energyfront_fa0e1e2d.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778279114,0.5769347676,-4.44e-08,-0.0004914741,7.74675e-05,0.0002648237,0.001544053,0.5778532138,800.5
submission_raw05_jepa_axisrepair_191a9f5d.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_fba45696.csv,submission_raw05_jepa_tangentnull_26c10612.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3677269584,0.5778342364,0.5768943229,8.27e-08,-7.13637e-05,0.0002712717,7.89038e-05,0.0015175858,0.5778342364,802.74
submission_raw05_jepa_axisrepair_74310fcf.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_efmicro_3eece507.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275566,0.576936112,-3e-08,-0.0006579679,7.69701e-05,0.0002643671,0.0015434354,0.5778540019,805.78
submission_raw05_jepa_axisrepair_fec683c9.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778283736,0.576928901,-2.69e-08,-0.0007962601,7.82188e-05,0.0002655188,0.0015472318,0.5778486894,807.04
submission_raw05_jepa_axisrepair_1ab3a7cb.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_energyfront_a190aa25.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275081,0.5769376688,-4.28e-08,-0.0004738367,7.51673e-05,0.0002627027,0.0015375927,0.5778552766,807.74
submission_raw05_jepa_axisrepair_7145daa7.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_efgate_ac60a2e6.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778283862,0.5769288724,-2.75e-08,-0.0007947068,7.819e-05,0.0002654924,0.0015469303,0.5778486778,809.02
submission_raw05_jepa_axisrepair_c9a298a1.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efmicro_3eece507.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275104,0.5769375487,-4.06e-08,-0.0005241311,7.47639e-05,0.0002623312,0.0015381701,0.5778551768,809.64
submission_raw05_jepa_axisrepair_b97ea70c.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275852,0.5769357548,-2.84e-08,-0.0006774855,7.81087e-05,0.0002654188,0.0015441778,0.5778537268,810.52
submission_raw05_jepa_axisrepair_5f8a4419.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_04a3de62.csv,submission_raw05_jepa_energyfront_a190aa25.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275386,0.5769378541,-4.69e-08,-0.0004642696,7.78702e-05,0.0002651983,0.0015404768,0.5778554645,810.56
submission_raw05_jepa_axisrepair_8a6d4b92.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_efmicro_3eece507.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275607,0.576936147,-3.02e-08,-0.000666071,7.6678e-05,0.0002640974,0.0015431391,0.5778540357,810.7
submission_raw05_jepa_axisrepair_51efcb66.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_efmicro_3eece507.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275733,0.5769361184,-3.09e-08,-0.0006645179,7.67221e-05,0.0002641383,0.0015428281,0.5778540239,811.94
submission_raw05_jepa_axisrepair_3668fbb7.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_7217d193.csv,submission_raw05_jepa_efmicro_1859bae9.csv,repair_context_only,none,,0.52,0.045,1.0,0.57782757,0.5769379157,-4.64e-08,-0.0005314527,7.67532e-05,0.0002641669,0.0015412,0.5778555483,822.06
submission_raw05_jepa_axisrepair_72cc9a0d.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_tangentnull_2733815c.csv,repair_context_only,none,,0.52,0.045,0.9999992265,0.5778283541,0.576928807,-2.51e-08,-0.0007935676,7.78533e-05,0.0002651816,0.0015478525,0.57784859,835.66
submission_raw05_jepa_axisrepair_c91ea4b0.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_f411b287.csv,submission_raw05_jepa_tangentnull_26c10612.csv,repair_context_only,none,,0.52,0.045,0.9999987109,0.5778283438,0.5769287677,-2.4e-08,-0.0007971751,7.78243e-05,0.0002651548,0.0015480701,0.5778485463,837.44
submission_raw05_jepa_axisrepair_cec61011.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_04a3de62.csv,submission_raw05_jepa_efmicro_3eece507.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275554,0.5769374792,-3.86e-08,-0.0006523806,7.7894e-05,0.0002652206,0.0015420613,0.5778551626,842.38
submission_raw05_jepa_axisrepair_7881be9d.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_tangentnull_2733815c.csv,repair_context_only,none,,0.52,0.045,0.9999992265,0.5778283581,0.5769288419,-2.53e-08,-0.0008016713,7.81515e-05,0.0002654568,0.0015475578,0.5778486237,842.72
submission_raw05_jepa_axisrepair_eabd4507.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_9d6e707c.csv,submission_raw05_jepa_tangentnull_26c10612.csv,repair_context_only,none,,0.52,0.045,0.9999987109,0.5778283478,0.5769288026,-2.42e-08,-0.0008052787,7.81087e-05,0.0002654174,0.0015477756,0.57784858,844.3
submission_raw05_jepa_axisrepair_2d88dc3f.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_tangentnull_2733815c.csv,repair_context_only,none,,0.52,0.045,0.9999992265,0.5778283206,0.5769299873,-3.11e-08,-0.0007975632,8.18893e-05,0.0002689078,0.0015434834,0.5778495598,845.42
submission_raw05_jepa_axisrepair_c2037857.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_tangentnull_2733815c.csv,repair_context_only,none,,0.52,0.045,0.9999992265,0.5778283708,0.5769288134,-2.59e-08,-0.0008001179,7.81257e-05,0.0002654331,0.0015472553,0.5778486121,845.56
submission_raw05_jepa_axisrepair_e0eadc56.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_0edfd32b.csv,submission_raw05_jepa_tangentnull_26c10612.csv,repair_context_only,none,,0.52,0.045,0.9999987109,0.5778283605,0.576928774,-2.48e-08,-0.0008037254,7.80862e-05,0.0002653968,0.0015474727,0.5778485684,847.28
submission_raw05_jepa_axisrepair_6ebd7c7e.csv,repair_motif_retained,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_tangentnull_26c10612.csv,repair_context_only,none,,0.52,0.045,0.9999987109,0.5778283103,0.576929948,-3e-08,-0.0008011703,8.18336e-05,0.0002688564,0.0015437104,0.5778495161,848.38
submission_raw05_jepa_axisrepair_fe881329.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_705367e9.csv,submission_raw05_jepa_efmicro_1859bae9.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275845,0.5769376608,-4.03e-08,-0.0006692693,7.71514e-05,0.000264534,0.0015422305,0.5778553462,857.04
submission_raw05_jepa_axisrepair_5ab1bbf2.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_fba45696.csv,submission_raw05_jepa_efmicro_5d2d2af0.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275665,0.5769359976,-8.86e-08,-0.0005274977,7.8232e-05,0.0002682343,0.0015468044,0.5778539145,878.14
submission_raw05_jepa_axisrepair_a11231bf.csv,repair_rawnegative,axis_plus_context_repair,submission_raw05_jepa_axisbridge_fba45696.csv,submission_raw05_jepa_efmicro_f88f2cec.csv,repair_context_only,none,,0.52,0.045,1.0,0.5778275709,0.5769360385,-8.88e-08,-0.0005362783,7.85165e-05,0.0002684969,0.0015464804,0.5778539536,882.98
submission_raw05_jepa_axisrepair_ba8ef1b7.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_45f2ba5a.csv,submission_raw05_jepa_efback_cc265f32.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.36674502,0.5778338987,0.5768985571,8.63e-08,6.106e-05,0.0002669837,7.66422e-05,0.0015158181,0.5778338987,908.6
submission_raw05_jepa_axisrepair_9431afdc.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_4bb109a4.csv,submission_raw05_jepa_efback_cc265f32.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3667521062,0.5778338901,0.5768985504,8.67e-08,6.27344e-05,0.0002670621,7.66913e-05,0.0015158721,0.5778338901,909.06
submission_raw05_jepa_axisrepair_3a98e3df.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_2f6bc887.csv,submission_raw05_jepa_efback_cc265f32.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.36674419,0.5778338996,0.5768985588,8.63e-08,6.06277e-05,0.000266986,7.66436e-05,0.0015158168,0.5778338996,911.18
submission_raw05_jepa_axisrepair_d40c2682.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_2574f23d.csv,submission_raw05_jepa_efback_cc265f32.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3667430481,0.5778338995,0.576898559,8.63e-08,6.05513e-05,0.0002669906,7.6646e-05,0.0015158192,0.5778338995,914.06
submission_raw05_jepa_axisrepair_db0a5961.csv,repair_lowbad,donor_plus_axis_motif,submission_raw05_jepa_axisbridge_e34b4795.csv,submission_raw05_jepa_efback_cc265f32.csv,inject_q3_sblockmicro,none,0.55,,0.045,0.3667297135,0.5778339007,0.576898559,8.63e-08,5.95237e-05,0.0002670183,7.66582e-05,0.0015158299,0.5778339007,916.88
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_axisrepair_2a20d67f.csv,250,True,0,0,0.0630768318,0.9798334082
submission_raw05_jepa_axisrepair_6b576311.csv,250,True,0,0,0.0630755978,0.9798310178
submission_raw05_jepa_axisrepair_a84ff361.csv,250,True,0,0,0.0630756147,0.9798310181
submission_raw05_jepa_axisrepair_fdbf4693.csv,250,True,0,0,0.0630754472,0.9798310127
submission_raw05_jepa_axisrepair_040eda76.csv,250,True,0,0,0.0630702585,0.9798315678
submission_raw05_jepa_axisrepair_7b48d2fc.csv,250,True,0,0,0.0630794313,0.9798363299
submission_raw05_jepa_axisrepair_ec678291.csv,250,True,0,0,0.0630782532,0.9798335265
submission_raw05_jepa_axisrepair_78029f2c.csv,250,True,0,0,0.0631481573,0.9798139508
submission_raw05_jepa_axisrepair_07a92ed6.csv,250,True,0,0,0.0630799112,0.9798372592
submission_raw05_jepa_axisrepair_310ad461.csv,250,True,0,0,0.0630794548,0.9798363302
submission_raw05_jepa_axisrepair_a225d175.csv,250,True,0,0,0.0630757517,0.9798335373
submission_raw05_jepa_axisrepair_e0c6d751.csv,250,True,0,0,0.0630792222,0.9798363228
submission_raw05_jepa_axisrepair_7187ae3d.csv,250,True,0,0,0.0630799281,0.9798372595
submission_raw05_jepa_axisrepair_acf27bd8.csv,250,True,0,0,0.0630797607,0.9798372541
submission_raw05_jepa_axisrepair_29fc9edf.csv,250,True,0,0,0.0630791545,0.9798365778
submission_raw05_jepa_axisrepair_5d4dd19b.csv,250,True,0,0,0.0630781113,0.9798360921
submission_raw05_jepa_axisrepair_c5b80c88.csv,250,True,0,0,0.0630680212,0.9798355954
submission_raw05_jepa_axisrepair_c167cb39.csv,250,True,0,0,0.0631497064,0.9798139605
submission_raw05_jepa_axisrepair_a3d71669.csv,250,True,0,0,0.0630782141,0.97983394
submission_raw05_jepa_axisrepair_aae22d53.csv,250,True,0,0,0.0630784093,0.9798384864
submission_raw05_jepa_axisrepair_9b44d436.csv,250,True,0,0,0.0630780467,0.9798339347
submission_raw05_jepa_axisrepair_7217a889.csv,250,True,0,0,0.0630771753,0.9798360966
submission_raw05_jepa_axisrepair_56b102d0.csv,250,True,0,0,0.0630789349,0.9798368253
submission_raw05_jepa_axisrepair_47558ed9.csv,250,True,0,0,0.0630782207,0.9798339401
submission_raw05_jepa_axisrepair_269e439d.csv,250,True,0,0,0.0630667873,0.9798332052
submission_raw05_jepa_axisrepair_3b2013ed.csv,250,True,0,0,0.0630779881,0.9798339327
submission_raw05_jepa_axisrepair_461b5197.csv,250,True,0,0,0.0630781282,0.9798360924
submission_raw05_jepa_axisrepair_b7f2d6b9.csv,250,True,0,0,0.0630793454,0.9798384819
submission_raw05_jepa_axisrepair_9cf6f179.csv,250,True,0,0,0.0630781113,0.9798366605
submission_raw05_jepa_axisrepair_a4c7ed33.csv,250,True,0,0,0.0630787586,0.9798384572
submission_raw05_jepa_axisrepair_393ebf08.csv,250,True,0,0,0.0630690246,0.9798291772
submission_raw05_jepa_axisrepair_b7d70019.csv,250,True,0,0,0.0630668043,0.9798332055
submission_raw05_jepa_axisrepair_191a9f5d.csv,250,True,0,0,0.0631507391,0.979813967
submission_raw05_jepa_axisrepair_74310fcf.csv,250,True,0,0,0.0630818856,0.9798374235
submission_raw05_jepa_axisrepair_fec683c9.csv,250,True,0,0,0.0630690415,0.9798291774
submission_raw05_jepa_axisrepair_1ab3a7cb.csv,250,True,0,0,0.0630825668,0.9798397672
submission_raw05_jepa_axisrepair_7145daa7.csv,250,True,0,0,0.0630688741,0.979829172
submission_raw05_jepa_axisrepair_c9a298a1.csv,250,True,0,0,0.0630831197,0.9798398132
submission_raw05_jepa_axisrepair_b97ea70c.csv,250,True,0,0,0.0630808528,0.9798364481
submission_raw05_jepa_axisrepair_5f8a4419.csv,250,True,0,0,0.0630800651,0.9798397779
submission_raw05_jepa_axisrepair_8a6d4b92.csv,250,True,0,0,0.0630819025,0.9798374237
submission_raw05_jepa_axisrepair_51efcb66.csv,250,True,0,0,0.063081735,0.9798374184
submission_raw05_jepa_axisrepair_3668fbb7.csv,250,True,0,0,0.0630796451,0.9798398281
submission_raw05_jepa_axisrepair_72cc9a0d.csv,250,True,0,0,0.0630698291,0.9798291822
submission_raw05_jepa_axisrepair_c91ea4b0.csv,250,True,0,0,0.0630703655,0.9798291856
submission_raw05_jepa_axisrepair_cec61011.csv,250,True,0,0,0.0630820395,0.9798399421
submission_raw05_jepa_axisrepair_7881be9d.csv,250,True,0,0,0.063069846,0.9798291825
submission_raw05_jepa_axisrepair_eabd4507.csv,250,True,0,0,0.0630703824,0.9798291859
submission_raw05_jepa_axisrepair_2d88dc3f.csv,250,True,0,0,0.0630724844,0.9798316911
submission_raw05_jepa_axisrepair_c2037857.csv,250,True,0,0,0.0630696786,0.9798291771
submission_raw05_jepa_axisrepair_e0eadc56.csv,250,True,0,0,0.063070215,0.9798291805
submission_raw05_jepa_axisrepair_6ebd7c7e.csv,250,True,0,0,0.0630730208,0.9798316945
submission_raw05_jepa_axisrepair_fe881329.csv,250,True,0,0,0.0630810666,0.9798399463
submission_raw05_jepa_axisrepair_5ab1bbf2.csv,250,True,0,0,0.0630763256,0.979831836
submission_raw05_jepa_axisrepair_a11231bf.csv,250,True,0,0,0.0630763491,0.9798318364
submission_raw05_jepa_axisrepair_ba8ef1b7.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_9431afdc.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_3a98e3df.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_d40c2682.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_db0a5961.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_e549ced1.csv,250,True,0,0,0.0630800138,0.9798353201
submission_raw05_jepa_axisrepair_5069cadb.csv,250,True,0,0,0.0630780395,0.9798351558
submission_raw05_jepa_axisrepair_fce0d5e6.csv,250,True,0,0,0.0631507391,0.979813899
submission_raw05_jepa_axisrepair_15648503.csv,250,True,0,0,0.0631507391,0.9798138178
submission_raw05_jepa_axisrepair_416220d6.csv,250,True,0,0,0.0631507391,0.9798138992
submission_raw05_jepa_axisrepair_e1311781.csv,250,True,0,0,0.0631507391,0.9798138217
submission_raw05_jepa_axisrepair_6b6f5f44.csv,250,True,0,0,0.0630765394,0.979835335
submission_raw05_jepa_axisrepair_8feaf48b.csv,250,True,0,0,0.063161515,0.979828392
submission_raw05_jepa_axisrepair_44bbecfe.csv,250,True,0,0,0.0631608134,0.9798173438
submission_raw05_jepa_axisrepair_d2f49b57.csv,250,True,0,0,0.0631608134,0.9798173477
submission_raw05_jepa_axisrepair_5cda393a.csv,250,True,0,0,0.0631608134,0.9798173435
submission_raw05_jepa_axisrepair_4ae69da5.csv,250,True,0,0,0.0631608134,0.979817425
```