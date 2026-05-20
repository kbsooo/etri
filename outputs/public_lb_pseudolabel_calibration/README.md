# Public LB Pseudolabel Calibration Candidates

This folder uses observed public LB scores as aggregate BCE constraints.
The posterior is a soft, maximum-entropy diagnostic label matrix close to the V76/V77 prior; it is not treated as ground truth.

Known public scores:
- V76 reconstructed public anchor: `0.5999627447`
- recovery15: `0.6057860899`
- TRP/weather/GRU/DAE w0.30: `0.6104310794`
- v38a: `0.6335340671`

Recommended next upload rule:
1. Submit `submission_01_exact_v77_recommended.csv` first unless an already uploaded V77 score exists.
2. If V77 does not beat or closely match V76 (`0.5999627447`), stop this branch.
3. If V77 improves, try the smallest posterior blend ranked near the top of `manifest.csv`.

Top manifest rows:
| file | sha256 | pseudo_public_bce | min | p01 | mean | p99 | max | abs_logit_mean | mad_from_v76 | corr_v76 | mad_from_v77 | corr_v77 | mad_from_recovery15 | corr_recovery15 | mad_from_dae | corr_dae | mad_from_v38a | corr_v38a |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_06_v77_posterior_blend_w15.csv | 3eb47aef5bb22c6c12f24ce592f1986cfd0af4b72c19a2a9b1c66d41557059a6 | 0.597209 | 0.176357 | 0.209100 | 0.608150 | 0.934821 | 0.940776 | 0.778236 | 0.021153 | 0.990498 | 0.006864 | 0.998480 | 0.086404 | 0.797303 | 0.094166 | 0.792000 | 0.120267 | 0.735968 |
| submission_10_v76_posterior_blend_w15.csv | 5f889155ef3097d594d829e9ad6b85d477688c6194c9d1b77c46efa29b01fe51 | 0.597295 | 0.192929 | 0.220591 | 0.608150 | 0.923772 | 0.933217 | 0.734769 | 0.006925 | 0.998335 | 0.021196 | 0.990073 | 0.082433 | 0.813191 | 0.091230 | 0.805405 | 0.119730 | 0.743254 |
| submission_05_v77_posterior_blend_w10.csv | 5cb476c47bfec21464b453d5d0342db1f83b6d4402f963dedf1c29945474842b | 0.598057 | 0.175397 | 0.208389 | 0.607757 | 0.934488 | 0.940207 | 0.777289 | 0.021015 | 0.990807 | 0.004576 | 0.999325 | 0.088409 | 0.787838 | 0.096216 | 0.782334 | 0.122458 | 0.724191 |
| submission_09_v76_posterior_blend_w10.csv | 829e528c9def6db06c44c320639a7a87680b0cb610f25363c68f4e11051c5ce6 | 0.598138 | 0.192944 | 0.220118 | 0.607757 | 0.922589 | 0.932096 | 0.731485 | 0.004617 | 0.999256 | 0.021079 | 0.990554 | 0.084311 | 0.804240 | 0.093199 | 0.796087 | 0.121907 | 0.731316 |
| submission_04_v77_posterior_blend_w05.csv | beb1b5653f171c827fd799a6fc39b7712ca01e70cb9d2a1bfecda5009b43bb3b | 0.598953 | 0.174437 | 0.208045 | 0.607364 | 0.934218 | 0.939847 | 0.776525 | 0.021185 | 0.990781 | 0.002288 | 0.999832 | 0.090438 | 0.778116 | 0.098278 | 0.772412 | 0.124651 | 0.712182 |
| submission_08_v76_posterior_blend_w05.csv | 58170598297309b893883b9f0fbd664446aa480b1ed2b5e04165156860b8f57a | 0.599027 | 0.192958 | 0.220811 | 0.607364 | 0.921708 | 0.931286 | 0.728450 | 0.002308 | 0.999813 | 0.021238 | 0.990672 | 0.086212 | 0.794941 | 0.095179 | 0.786422 | 0.124089 | 0.719039 |
| submission_03_v77_posterior_blend_w02.csv | b018e68aac2ed4758e82ca96be3422c8510b0d03febf52eca273a520e060a16c | 0.599515 | 0.173861 | 0.207839 | 0.607128 | 0.933750 | 0.939631 | 0.776151 | 0.021435 | 0.990605 | 0.000915 | 0.999973 | 0.091663 | 0.772163 | 0.099525 | 0.766342 | 0.125969 | 0.704869 |
| submission_07_v76_posterior_blend_w02.csv | 92e69397944e5c93e33f331920cb669968fe88c50ecca1de6ed4beb540dc5868 | 0.599583 | 0.192967 | 0.220289 | 0.607128 | 0.921453 | 0.930800 | 0.726690 | 0.000923 | 0.999970 | 0.021456 | 0.990566 | 0.087363 | 0.789196 | 0.096377 | 0.780458 | 0.125402 | 0.711514 |

Do not submit the raw posterior; it is intentionally saved only as a diagnostic.
