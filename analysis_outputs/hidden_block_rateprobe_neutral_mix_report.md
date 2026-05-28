# Hidden Block Rateprobe Neutral Mix

Mixes endpoint-derived rate-probe candidates with raw-axis-safe hidden-block candidates. The gate is raw-axis delta <= 0 versus raw05.

## Safe Candidates

```csv
file,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,ordinal_axis_ratio,mean_abs_move_vs_raw05,min_prob,max_prob,safe_source,rateprobe_source,w_probe
submission_hiddenblock_rateprobe_neutral_605de284.csv,0.5768399397,0.5775256652,-6.42e-07,0.0042856501,0.024888342,0.0011349738,0.0634466612,0.9797992034,paretomix_w0.4_507296eb,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.1
submission_hiddenblock_rateprobe_neutral_27ca3bb0.csv,0.5768777935,0.5775253527,-9.545e-07,0.0043834087,0.0248523949,0.001081139,0.0634052359,0.9798142361,paretomix_w0.4_507296eb,raw05_endpoint_local_q1q2q3_w0p1_c0ca1f42,0.05
submission_hiddenblock_rateprobe_neutral_7018cfdb.csv,0.5768788114,0.5775247283,-1.5789e-06,0.003202732,0.0247115277,0.0010535991,0.0630791265,0.9798003436,paretomix_w0.4_507296eb,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.05
submission_hiddenblock_rateprobe_neutral_c95eca2a.csv,0.576903272,0.5775260984,-2.088e-07,0.0057200118,0.0249184555,0.0010711575,0.0636943992,0.9798397172,paretomix_w0.4_507296eb,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.15
submission_hiddenblock_rateprobe_neutral_e3cb8900.csv,0.576906349,0.5775261343,-1.729e-07,0.0056378265,0.0248878404,0.0010731201,0.0636996278,0.9798397172,paretomix_w0.4_507296eb,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.15
submission_hiddenblock_rateprobe_neutral_f779eafc.csv,0.5769079749,0.5775252286,-1.0786e-06,0.0045193944,0.0247904444,0.0010329251,0.0633658807,0.9798269806,paretomix_w0.4_507296eb,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.1
submission_hiddenblock_rateprobe_neutral_94be6759.csv,0.5769100208,0.5775252471,-1.0601e-06,0.0044646056,0.024770041,0.0010337319,0.0633693497,0.9798269806,paretomix_w0.4_507296eb,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.1
submission_hiddenblock_rateprobe_neutral_938b6347.csv,0.5769128398,0.5775245208,-1.7864e-06,0.0033196569,0.0246626114,0.0010019553,0.0630389426,0.9798142361,paretomix_w0.4_507296eb,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.05
submission_hiddenblock_rateprobe_neutral_321736ef.csv,0.57691386,0.5775245274,-1.7798e-06,0.0032922632,0.024652413,0.0010019098,0.0630406687,0.9798142361,paretomix_w0.4_507296eb,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.05
submission_hiddenblock_rateprobe_neutral_149aff03.csv,0.5770782916,0.5775251567,-1.1505e-06,0.007407161,0.0268198241,0.0013596214,0.064666923,0.97989022,rawaxis_stage2_raw10_s0p75_0cf1aeac,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.3
submission_hiddenblock_rateprobe_neutral_21e135aa.csv,0.5772114036,0.5775217808,-4.5264e-06,0.0050617265,0.0266396037,0.0011864055,0.0638826415,0.9799061065,rawaxis_stage2_raw10_s0p75_0cf1aeac,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.2
submission_hiddenblock_rateprobe_neutral_e316690f.csv,0.5772771601,0.57752422,-2.0872e-06,0.0074384085,0.0269733628,0.0012974841,0.0644828987,0.979955465,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p1_c0ca1f42,0.15
submission_hiddenblock_rateprobe_neutral_0429b588.csv,0.5772782968,0.5775204301,-5.8771e-06,0.0038906313,0.026549911,0.0011086912,0.0634938323,0.9799140452,rawaxis_stage2_raw10_s0p75_0cf1aeac,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.15
submission_hiddenblock_rateprobe_neutral_be47d7d3.csv,0.5772833973,0.5775248469,-1.4603e-06,0.0081076284,0.0265252604,0.0011677291,0.064420534,0.9799730721,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.3
submission_hiddenblock_rateprobe_neutral_95ebba6c.csv,0.577289678,0.5775250455,-1.2617e-06,0.0079435892,0.026463912,0.0011775234,0.0644311026,0.9799730721,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.3
submission_hiddenblock_rateprobe_neutral_178705d3.csv,0.5773441901,0.5775213639,-4.9433e-06,0.0050830024,0.0267421703,0.001157992,0.0637612915,0.9799495926,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p1_c0ca1f42,0.1
submission_hiddenblock_rateprobe_neutral_38361faa.csv,0.5773454145,0.5775193039,-7.0033e-06,0.0027206187,0.0264604965,0.0010388384,0.06310723,0.9799219808,rawaxis_stage2_raw10_s0p75_0cf1aeac,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.1
submission_hiddenblock_rateprobe_neutral_45639604.csv,0.5773483469,0.5775217806,-4.5266e-06,0.0055291733,0.0264434783,0.0010690172,0.0637201424,0.9799613357,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.2
submission_hiddenblock_rateprobe_neutral_4196fa0e.csv,0.5773525198,0.5775218987,-4.4085e-06,0.0054198516,0.0264025998,0.0010771217,0.0637271166,0.9799613357,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.2
submission_hiddenblock_rateprobe_neutral_d7024e8c.csv,0.5773810815,0.5775205071,-5.8001e-06,0.0042413921,0.0264029108,0.001025373,0.0633726136,0.979955465,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.15
submission_hiddenblock_rateprobe_neutral_b434d0e3.csv,0.5773842059,0.5775205904,-5.7168e-06,0.004159415,0.0263722595,0.0010316313,0.0633778176,0.979955465,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.15
submission_hiddenblock_rateprobe_neutral_9865b7f9.csv,0.5774119114,0.5775191991,-7.1081e-06,0.0027314788,0.0265118833,0.0010321259,0.0630472153,0.9799437185,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p1_c0ca1f42,0.05
submission_hiddenblock_rateprobe_neutral_149b91f7.csv,0.5774127565,0.577518402,-7.9052e-06,0.00155169,0.02637136,0.0009773169,0.062722824,0.9799299133,rawaxis_stage2_raw10_s0p75_0cf1aeac,pareto03_endpoint_local_q1q2q3_w0p05_52ff6884,0.05
submission_hiddenblock_rateprobe_neutral_d882d21a.csv,0.5774139891,0.5775194067,-6.9005e-06,0.0029545764,0.0263625588,0.0009863388,0.0630268526,0.9799495926,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.1
submission_hiddenblock_rateprobe_neutral_41d14b2e.csv,0.5774160684,0.5775194587,-6.8485e-06,0.0028999346,0.0263421298,0.0009905242,0.0630303042,0.9799495926,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.1
submission_hiddenblock_rateprobe_neutral_0dcd3b5b.csv,0.5774470694,0.5775184791,-7.8281e-06,0.0016687274,0.0263224223,0.000952807,0.0626828519,0.9799437185,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_local_q1q2q3_w0p05_120a52ac,0.05
submission_hiddenblock_rateprobe_neutral_f0035e40.csv,0.5774481073,0.5775185033,-7.8039e-06,0.0016414113,0.0263122104,0.0009548124,0.0626845689,0.9799437185,rawaxis_stage2_raw10_s0p75_0cf1aeac,raw05_endpoint_strict_q1q2q3_w0p05_7c58557c,0.05
```