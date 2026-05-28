# Raw05 JEPA Energy-Constrained Frontier

This pass uses context-target JEPA energy only as a constraint on the stronger local Q3-counterweight frontier.
It stitches local q3cw bases toward ctxenergy/low-bad donors with small logit-space blends.

## Counts

- generated candidates: 443633
- actual-anchor rescored candidates: 1842
- saved candidates: 75

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,energy_delta_vs_base,blend_profile,beta,base_file,donor_file
submission_raw05_jepa_energyfront_fa0e1e2d.csv,frontier_actual,0.5778394496,0.5769001917,6.06e-08,0.0008307026,0.00149116,-0.0071816604,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_927f1461.csv,frontier_actual,0.5778394551,0.5769002317,6.03e-08,0.0008195078,0.001490731,-0.0085481285,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_978f51e5.csv,frontier_actual,0.5778394606,0.5769002716,6.01e-08,0.0008083131,0.0014903021,-0.0099958455,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_dfb59446.csv,frontier_actual,0.5778394804,0.5769059399,1.6e-08,0.0007736001,0.0014819874,-0.0001573469,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_ea665780.csv,frontier_actual,0.577839486,0.5769059799,1.58e-08,0.000762406,0.0014815584,-0.0014165302,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_e007a868.csv,energy_guarded,0.5778394934,0.5769001117,5.83e-08,0.0008443253,0.0014899422,-0.0071852878,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_energyfront_1d2ca574.csv,energy_guarded,0.5778394961,0.5769001144,5.8e-08,0.0008500484,0.0014902322,-0.006127587,q1light,0.48,submission_raw05_jepa_q3cwlocal_bd44fb94.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_155843d4.csv,energy_guarded,0.5778394989,0.5769001517,5.8e-08,0.0008331305,0.0014895133,-0.0085496101,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_energyfront_af5ff1b1.csv,energy_guarded,0.5778395019,0.5769001565,5.77e-08,0.0008382315,0.0014897794,-0.0075059148,q1light,0.48,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_3d6d00c1.csv,energy_guarded,0.5778395044,0.5769000917,5.77e-08,0.000847731,0.0014896382,-0.0071859071,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_energyfront_71ba4826.csv,energy_guarded,0.5778395044,0.5769001916,5.77e-08,0.0008219358,0.0014890844,-0.0099951811,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_energyfront_867b4ff6.csv,energy_guarded,0.5778395077,0.5769001987,5.74e-08,0.0008264148,0.0014893267,-0.0089747698,q1light,0.48,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_energyfront_85e196a0.csv,energy_guarded,0.5778395099,0.5769001317,5.74e-08,0.0008365362,0.0014892093,-0.0085496929,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_energyfront_b168f082.csv,energy_guarded,0.5778395153,0.5769000718,5.72e-08,0.0008511367,0.0014893356,-0.0071864114,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_energyfront_96dcb0e4.csv,energy_guarded,0.5778395154,0.5769001716,5.72e-08,0.0008253415,0.0014887804,-0.0099947275,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_energyfront_e54ea079.csv,energy_guarded,0.5778395208,0.5769001117,5.69e-08,0.0008399419,0.0014889067,-0.0085496607,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_energyfront_7404c124.csv,energy_guarded,0.5778395233,0.5769058566,1.38e-08,0.000787255,0.0014807926,-0.0001792732,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_energyfront_6236c7e4.csv,energy_guarded,0.5778395263,0.5769000518,5.66e-08,0.0008545424,0.0014890332,-0.0071868006,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_4a27604e.csv
submission_raw05_jepa_energyfront_9ed3ec2b.csv,energy_guarded,0.5778395264,0.5769001516,5.66e-08,0.0008287472,0.0014884778,-0.0099941588,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_energyfront_d71b3804.csv,energy_guarded,0.5778395288,0.5769058966,1.36e-08,0.0007760609,0.0014803636,-0.0014370057,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_energyfront_65f1910f.csv,energy_guarded,0.5778395318,0.5769000917,5.63e-08,0.0008433476,0.0014886043,-0.0085495135,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_4a27604e.csv
submission_raw05_jepa_energyfront_3f395d76.csv,energy_guarded,0.5778395331,0.576905907,1.32e-08,0.0007805069,0.001480583,-0.0005158985,q1light,0.48,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_4f44a4de.csv,energy_guarded,0.577839534,0.5769058358,1.32e-08,0.0007906687,0.0014804943,-0.0001845001,q1light,0.48,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_339ccb2f.csv
submission_raw05_jepa_energyfront_95cf1cda.csv,energy_guarded,0.5778395373,0.5769001317,5.6e-08,0.0008321528,0.0014881754,-0.0099934751,q1light,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_4a27604e.csv
submission_raw05_jepa_energyfront_d8fe48cd.csv,frontier_actual,0.5778394748,0.5769058999,1.62e-08,0.0007847944,0.0014824163,0.0010205875,q1light,0.48,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_0f7e85a0.csv,strict_raw,0.5778398077,0.5769058715,-1e-10,0.000815186,0.0014740738,-0.0010992002,q1light,0.35,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_energyfront_eab109d0.csv,strict_raw,0.5778398086,0.5769058064,-2e-10,0.0008316678,0.0014744,-0.000180899,q1light,0.35,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_energyfront_aad75da6.csv,strict_raw,0.5778398148,0.5769058519,-5e-10,0.0008242848,0.0014742367,-0.0004293246,q1light,0.35,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_352af1e7.csv,strict_raw,0.5778398156,0.5769058564,-5e-10,0.0008176752,0.0014738637,-0.0011013381,q1light,0.35,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_energyfront_7515a755.csv,strict_raw,0.5778398463,0.5769057915,-1.8e-09,0.0008342418,0.0014734016,-0.0004383754,q1light,0.35,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_energyfront_32708895.csv,strict_raw,0.5778398541,0.5769057764,-2.1e-09,0.000836731,0.0014731933,-0.0004405027,q1light,0.35,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_339ccb2f.csv
submission_raw05_jepa_energyfront_370ba633.csv,strict_raw,0.577839859,0.5769059021,-2.6e-09,0.0008298768,0.0014735897,-0.0001550127,q1light,0.3,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_7d8de5f5.csv,strict_raw,0.5778398619,0.5769057613,-2.5e-09,0.0008392203,0.0014729851,-0.0004425759,q1light,0.35,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_energyfront_b7ef9b88.csv,strict_raw,0.5778398118,0.5769056734,-2e-10,0.0008462677,0.0014741614,0.0002299138,q1light,0.4,submission_raw05_jepa_q3cwlocal_24b6b87f.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_energyfront_065ad9ec.csv,strict_raw,0.5778398207,0.5769056562,-5e-10,0.0008491125,0.0014739224,0.0002271679,q1light,0.4,submission_raw05_jepa_q3cwlocal_24b6b87f.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_energyfront_78872711.csv,strict_raw,0.5778398074,0.5769057991,-2e-10,0.0008390549,0.0014748028,0.0004977521,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_b8cf34d3.csv,strict_raw,0.577839839,0.5769057388,-1.5e-09,0.0008490119,0.0014739677,0.0004873056,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_5f4882be.csv
submission_raw05_jepa_energyfront_303edc6e.csv,strict_raw,0.5778398468,0.5769057237,-1.8e-09,0.0008515012,0.0014737594,0.0004848294,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_339ccb2f.csv
submission_raw05_jepa_energyfront_4cf0eacc.csv,strict_raw,0.5778398546,0.5769057086,-2.2e-09,0.0008539904,0.0014735513,0.0004824073,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_eca8ad07.csv
submission_raw05_jepa_energyfront_8e28f73b.csv,strict_raw,0.5778398624,0.5769056935,-2.5e-09,0.0008564796,0.0014733432,0.0004800393,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_e164c924.csv
submission_raw05_jepa_energyfront_217541ea.csv,strict_raw,0.5778398515,0.5769058483,-2.3e-09,0.000844946,0.0014741673,0.0005806405,q1light,0.3,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_08506e08.csv,frontier_actual,0.577839455,0.5769019246,4.68e-08,0.0008149421,0.0014885304,0.0061879605,q1light,0.48,submission_raw05_jepa_q3cwlocal_a1430cf5.csv,submission_raw05_jepa_targetw_ce178c95.csv
submission_raw05_jepa_energyfront_c7b4058d.csv,frontier_actual,0.5778394617,0.5769046651,2.13e-08,0.0008317461,0.0014744407,0.0150103109,q2s1heavy,0.35,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_61238b04.csv,strict_raw,0.5778398636,0.5769062088,-1.9e-09,0.0007519524,0.0014709775,0.0140903917,q1light,0.35,submission_raw05_jepa_q3cwlocal_a3303e68.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_a55d3d2c.csv,frontier_actual,0.5778394549,0.5769046191,2.14e-08,0.0008446074,0.0014749336,0.0157194438,q2s1heavy,0.35,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_a190aa25.csv,frontier_actual,0.5778387145,0.576903565,7.15e-08,0.0008568227,0.0014865785,0.0183603972,context_only,0.48,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_94f25adf.csv,strict_raw,0.5778398562,0.5769061559,-1.7e-09,0.0007667216,0.0014715436,0.0145916927,q1light,0.35,submission_raw05_jepa_q3cwlocal_bd44fb94.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_3968d2f2.csv,frontier_actual,0.577839448,0.576904573,2.16e-08,0.0008574689,0.0014754266,0.0163569724,q2s1heavy,0.35,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_488d3a06.csv,frontier_actual,0.5778392977,0.5769044877,3.05e-08,0.0008217017,0.0014767701,0.0173721784,q2s1heavy,0.4,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
submission_raw05_jepa_energyfront_7ef34ca2.csv,frontier_actual,0.5778393447,0.576904351,2.78e-08,0.0008461144,0.0014756478,0.017987993,q2s1heavy,0.4,submission_raw05_jepa_q3cwlocal_d9239cc6.csv,submission_raw05_jepa_targetw_f883e40c.csv
```

## Best By Blend Profile / Beta

```csv
blend_profile,beta,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,energy_delta_vs_base,base_file,donor_file
context_only,0.48,0.5778387145,0.576903565,7.15e-08,0.0008568227,0.0183603972,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
q2s1heavy,0.48,0.5778390068,0.5769007108,7.26e-08,0.0008508927,0.0276769817,submission_raw05_jepa_q3cwlocal_a1430cf5.csv,submission_raw05_jepa_targetw_f883e40c.csv
q2s1heavy,0.4,0.5778392852,0.5769044044,3.07e-08,0.0008449487,0.018985784,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_f883e40c.csv
q2s1heavy,0.35,0.577839448,0.576904573,2.16e-08,0.0008574689,0.0163569724,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.48,0.5778394496,0.5769001917,6.06e-08,0.0008307026,-0.0071816604,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
q2s1heavy,0.3,0.5778396028,0.5769047927,1.29e-08,0.0008558939,0.013283799,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.4,0.5778396187,0.5769012896,4.27e-08,0.0008463139,0.0050863044,submission_raw05_jepa_q3cwlocal_a1430cf5.csv,submission_raw05_jepa_targetw_ce178c95.csv
q2s1heavy,0.26,0.577839728,0.5769049861,6.4e-09,0.0008498365,0.0108959979,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.35,0.5778397344,0.5769017494,3.4e-08,0.0008477192,-0.0064404859,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
q2s1heavy,0.22,0.5778398465,0.5769051294,4e-10,0.0008578809,0.0091239741,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.3,0.5778398501,0.5769023877,2.41e-08,0.0008435016,-0.0065398843,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
q1light,0.26,0.5778399355,0.5769058374,-5.9e-09,0.0008583147,0.0004922004,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_ce178c95.csv
q1light,0.22,0.5778400279,0.5769058866,-9.6e-09,0.0008548927,-0.0001321465,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_ce178c95.csv
q1light,0.18,0.5778401213,0.5769059422,-1.31e-08,0.0008497493,-0.0005933274,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_ce178c95.csv
q1light,0.15,0.5778401909,0.5769059838,-1.55e-08,0.000857751,0.0057369594,submission_raw05_jepa_q3cwlocal_390b7d62.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.125,0.5778402492,0.5769060155,-1.75e-08,0.0008534936,0.0045997301,submission_raw05_jepa_q3cwlocal_41bd5210.csv,submission_raw05_jepa_targetw_f883e40c.csv
q1light,0.1,0.5778403095,0.5769060511,-1.94e-08,0.0008481601,0.0035211947,submission_raw05_jepa_q3cwlocal_33a60b3b.csv,submission_raw05_jepa_targetw_f883e40c.csv
s4tiny_only_context,0.48,0.5778411787,0.5768794139,9.98e-08,0.0015802373,-0.0315352415,submission_raw05_jepa_q3cwlocal_e15cadf3.csv,submission_raw05_jepa_ctxenergy_95d33a86.csv
context_only,0.35,0.5778411789,0.5768795568,7.78e-08,0.0015817863,-0.0292736149,submission_raw05_jepa_q3cwlocal_284f5ff5.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
nonq3_s4tiny,0.35,0.5778412174,0.5768798971,7.06e-08,0.0015908529,-0.0276737505,submission_raw05_jepa_q3cwlocal_284f5ff5.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
nonq3_s4tiny,0.4,0.5778412637,0.5768790496,9.86e-08,0.0015852574,-0.0318298357,submission_raw05_jepa_q3cwlocal_e15cadf3.csv,submission_raw05_jepa_ctxenergy_95d33a86.csv
nonq3_s4tiny,0.48,0.5778413104,0.57687926,8.66e-08,0.0016073994,-0.0313235745,submission_raw05_jepa_q3cwlocal_1abbbc4b.csv,submission_raw05_jepa_ctxenergy_0cb74d63.csv
context_only,0.4,0.5778414064,0.57687975,6.67e-08,0.0015548044,-0.032417126,submission_raw05_jepa_q3cwlocal_1abbbc4b.csv,submission_raw05_jepa_ctxenergy_d0c2fe5e.csv
all,0.48,0.5778431944,0.5768799208,1e-08,0.0015994216,-0.0428360133,submission_raw05_jepa_q3cwlocal_284f5ff5.csv,submission_raw05_jepa_ctxenergy_2ad3af53.csv
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_energyfront_fa0e1e2d.csv,250,True,0,0,0.06314385,0.979820224
submission_raw05_jepa_energyfront_927f1461.csv,250,True,0,0,0.06314385,0.979820224
submission_raw05_jepa_energyfront_978f51e5.csv,250,True,0,0,0.06314385,0.979820224
submission_raw05_jepa_energyfront_dfb59446.csv,250,True,0,0,0.06314385,0.9798280243
submission_raw05_jepa_energyfront_ea665780.csv,250,True,0,0,0.06314385,0.9798280243
submission_raw05_jepa_energyfront_e007a868.csv,250,True,0,0,0.0631432012,0.9798201744
submission_raw05_jepa_energyfront_1d2ca574.csv,250,True,0,0,0.0631429016,0.9798201791
submission_raw05_jepa_energyfront_155843d4.csv,250,True,0,0,0.0631432012,0.9798201744
submission_raw05_jepa_energyfront_af5ff1b1.csv,250,True,0,0,0.0631429016,0.9798201791
submission_raw05_jepa_energyfront_3d6d00c1.csv,250,True,0,0,0.063143039,0.979820162
submission_raw05_jepa_energyfront_71ba4826.csv,250,True,0,0,0.0631432012,0.9798201744
submission_raw05_jepa_energyfront_867b4ff6.csv,250,True,0,0,0.0631429016,0.9798201791
submission_raw05_jepa_energyfront_85e196a0.csv,250,True,0,0,0.063143039,0.979820162
submission_raw05_jepa_energyfront_b168f082.csv,250,True,0,0,0.0631428768,0.9798201496
submission_raw05_jepa_energyfront_96dcb0e4.csv,250,True,0,0,0.063143039,0.979820162
submission_raw05_jepa_energyfront_e54ea079.csv,250,True,0,0,0.0631428768,0.9798201496
submission_raw05_jepa_energyfront_7404c124.csv,250,True,0,0,0.0631432012,0.9798279781
submission_raw05_jepa_energyfront_6236c7e4.csv,250,True,0,0,0.0631427146,0.9798201372
submission_raw05_jepa_energyfront_9ed3ec2b.csv,250,True,0,0,0.0631428768,0.9798201496
submission_raw05_jepa_energyfront_d71b3804.csv,250,True,0,0,0.0631432012,0.9798279781
submission_raw05_jepa_energyfront_65f1910f.csv,250,True,0,0,0.0631427146,0.9798201372
submission_raw05_jepa_energyfront_3f395d76.csv,250,True,0,0,0.0631429016,0.9798279795
submission_raw05_jepa_energyfront_4f44a4de.csv,250,True,0,0,0.063143039,0.9798279665
submission_raw05_jepa_energyfront_95cf1cda.csv,250,True,0,0,0.0631427146,0.9798201372
submission_raw05_jepa_energyfront_d8fe48cd.csv,250,True,0,0,0.06314385,0.9798280243
submission_raw05_jepa_energyfront_0f7e85a0.csv,250,True,0,0,0.0631375423,0.979827772
submission_raw05_jepa_energyfront_eab109d0.csv,250,True,0,0,0.063137424,0.9798277636
submission_raw05_jepa_energyfront_aad75da6.csv,250,True,0,0,0.0631372328,0.9798277666
submission_raw05_jepa_energyfront_352af1e7.csv,250,True,0,0,0.063137424,0.9798277636
submission_raw05_jepa_energyfront_7515a755.csv,250,True,0,0,0.0631367598,0.9798277328
submission_raw05_jepa_energyfront_32708895.csv,250,True,0,0,0.0631366415,0.9798277244
submission_raw05_jepa_energyfront_370ba633.csv,250,True,0,0,0.0631360988,0.979827745
submission_raw05_jepa_energyfront_7d8de5f5.csv,250,True,0,0,0.0631365233,0.979827716
submission_raw05_jepa_energyfront_b7ef9b88.csv,250,True,0,0,0.0631376103,0.9798277389
submission_raw05_jepa_energyfront_065ad9ec.csv,250,True,0,0,0.0631374751,0.9798277293
submission_raw05_jepa_energyfront_78872711.csv,250,True,0,0,0.0631372328,0.9798277666
submission_raw05_jepa_energyfront_b8cf34d3.csv,250,True,0,0,0.0631367598,0.9798277328
submission_raw05_jepa_energyfront_303edc6e.csv,250,True,0,0,0.0631366415,0.9798277244
submission_raw05_jepa_energyfront_4cf0eacc.csv,250,True,0,0,0.0631365233,0.979827716
submission_raw05_jepa_energyfront_8e28f73b.csv,250,True,0,0,0.063136405,0.9798277076
submission_raw05_jepa_energyfront_217541ea.csv,250,True,0,0,0.0631360988,0.979827745
submission_raw05_jepa_energyfront_08506e08.csv,250,True,0,0,0.06314385,0.9798226164
submission_raw05_jepa_energyfront_c7b4058d.csv,250,True,0,0,0.063149975,0.9798279041
submission_raw05_jepa_energyfront_61238b04.csv,250,True,0,0,0.0631372328,0.9798277666
submission_raw05_jepa_energyfront_a55d3d2c.csv,250,True,0,0,0.063149975,0.9798279041
submission_raw05_jepa_energyfront_a190aa25.csv,250,True,0,0,0.0631691192,0.9798280243
submission_raw05_jepa_energyfront_94f25adf.csv,250,True,0,0,0.0631372328,0.9798277666
submission_raw05_jepa_energyfront_3968d2f2.csv,250,True,0,0,0.063149975,0.9798279041
submission_raw05_jepa_energyfront_488d3a06.csv,250,True,0,0,0.0631538034,0.9798279933
submission_raw05_jepa_energyfront_7ef34ca2.csv,250,True,0,0,0.0631529807,0.9798279467
```
