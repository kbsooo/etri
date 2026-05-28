# Direct Label Inverse7 Leave-Two-Anchor CV

This trains direct-label inverse solutions on four known public anchors and predicts the two held-out anchors.

## Overall Policy Error

```
            policy  pair_abs_error_mean  pair_abs_error_max  pair_signed_error_mean  top_l2o_source_score
 oracle_pair_best1             0.000315            0.000511                0.000041              0.002396
         l2o_best1             0.000470            0.000732                0.000168              0.001468
    l2o_best5_mean             0.000493            0.000745                0.000138              0.001468
subject_best3_mean             0.000511            0.000778                0.000099              0.001600
   l2o_best12_mean             0.000533            0.000799                0.000160              0.001468
  structured_best1             0.000562            0.000799                0.000145              0.001600
```

## Best Source Masks

```
         mask_kind                   mask_name  rows   prior_name  l2o_source_score  l2o_mae  l2o_p90  l2o_max  l2o_pair_mae  l2o_pair_p90  l2o_signed_mean  train_solution_score_mean  train_shift_mean
       random_rows             frac0.40_rep009   100 entropy_g075          0.001468 0.000470 0.001039 0.001719      0.000470      0.000958         0.000168                   0.000311          0.010381
subject_contiguous             frac0.40_rep052   101 entropy_g075          0.001600 0.000562 0.001212 0.001615      0.000562      0.001022         0.000145                   0.000342          0.011385
       random_rows             frac0.40_rep002   100 entropy_g075          0.001626 0.000534 0.001163 0.001822      0.000534      0.001000         0.000243                   0.000340          0.011323
       random_rows             frac0.40_rep040   100 entropy_g075          0.001655 0.000556 0.001317 0.001706      0.000556      0.000993         0.000177                   0.000495          0.011585
subject_contiguous             frac0.25_rep099    64 entropy_g075          0.001663 0.000550 0.001390 0.001863      0.000550      0.000894        -0.000045                   0.000444          0.014794
       random_rows             frac0.30_rep221    75 entropy_g075          0.001688 0.000549 0.001327 0.001982      0.000549      0.000964         0.000169                   0.000355          0.011821
       random_rows             frac0.20_rep114    50 entropy_g075          0.001736 0.000536 0.001509 0.001999      0.000536      0.001123         0.000100                   0.000336          0.011197
       random_rows             frac0.40_rep092   100 entropy_g075          0.001802 0.000598 0.001321 0.001860      0.000598      0.001261         0.000195                   0.000458          0.012103
       random_rows             frac0.20_rep115    50 entropy_g075          0.001810 0.000549 0.001418 0.002090      0.000549      0.001140         0.000152                   0.000768          0.012348
       random_rows             frac0.40_rep197   100 entropy_g075          0.001836 0.000629 0.001434 0.001714      0.000629      0.001282         0.000198                   0.000380          0.012680
       random_rows             frac0.50_rep073   125 entropy_g075          0.001844 0.000610 0.001338 0.001890      0.000610      0.001203         0.000218                   0.000845          0.011846
subject_contiguous             frac0.50_rep142   126 entropy_g075          0.001851 0.000625 0.001253 0.002174      0.000625      0.001204         0.000195                   0.000362          0.012083
       random_rows             frac0.40_rep132   100 entropy_g075          0.001852 0.000572 0.001024 0.002317      0.000572      0.001315         0.000269                   0.000823          0.011322
      global_order                rowmod4_rem3    62 entropy_g075          0.001887 0.000597 0.001167 0.002282      0.000597      0.001349         0.000313                   0.000339          0.011298
       random_rows             frac0.50_rep115   125 entropy_g075          0.001903 0.000632 0.001339 0.002125      0.000632      0.001237         0.000192                   0.000639          0.012482
       random_rows             frac0.40_rep027   100 entropy_g075          0.001928 0.000634 0.001416 0.002068      0.000634      0.001138         0.000229                   0.000965          0.012735
     subject_order per_subject_prefix_frac0.25    64 entropy_g075          0.001946 0.000692 0.001587 0.001740      0.000692      0.001110         0.000234                   0.000787          0.013343
subject_contiguous             frac0.25_rep099    64 entropy_g050          0.001956 0.000608 0.001849 0.001977      0.000608      0.001209         0.000087                   0.000467          0.015552
       random_rows             frac0.30_rep056    75 entropy_g075          0.001965 0.000711 0.001520 0.001811      0.000711      0.001280         0.000271                   0.000352          0.011747
       random_rows             frac0.60_rep001   150 entropy_g075          0.001992 0.000611 0.001492 0.002248      0.000611      0.001114         0.000200                   0.001480          0.013178
       random_rows             frac0.50_rep156   125 entropy_g075          0.002009 0.000665 0.001389 0.002188      0.000665      0.001420         0.000267                   0.000466          0.011942
       random_rows             frac0.30_rep192    75 entropy_g075          0.002011 0.000710 0.001410 0.002023      0.000710      0.001411         0.000208                   0.000559          0.011970
subject_contiguous             frac0.40_rep009   101 entropy_g075          0.002036 0.000682 0.001739 0.002092      0.000682      0.001271         0.000188                   0.000389          0.012953
       random_rows             frac0.40_rep052   100 entropy_g075          0.002041 0.000669 0.001371 0.002371      0.000669      0.001396         0.000271                   0.000383          0.012756
       random_rows             frac0.40_rep009   100 entropy_g050          0.002087 0.000631 0.001740 0.002416      0.000631      0.001247         0.000338                   0.000378          0.012585
       random_rows             frac0.30_rep210    75 entropy_g075          0.002101 0.000669 0.001606 0.002287      0.000669      0.001185         0.000267                   0.001232          0.013184
       random_rows             frac0.50_rep171   125 entropy_g075          0.002113 0.000669 0.001650 0.002408      0.000669      0.001277         0.000224                   0.000803          0.013260
       random_rows             frac0.50_rep169   125 entropy_g075          0.002124 0.000699 0.001335 0.002516      0.000699      0.001509         0.000295                   0.000379          0.012640
subject_contiguous             frac0.40_rep052   101 entropy_g050          0.002135 0.000716 0.001601 0.002361      0.000716      0.001311         0.000310                   0.000392          0.013053
       random_rows             frac0.20_rep114    50 entropy_g050          0.002137 0.000689 0.001606 0.002590      0.000689      0.001315         0.000261                   0.000376          0.012524
       random_rows             frac0.40_rep040   100 entropy_g050          0.002138 0.000707 0.001653 0.002335      0.000707      0.001244         0.000335                   0.000519          0.013367
    single_subject                        id01    27 entropy_g075          0.002141 0.000767 0.001485 0.001988      0.000767      0.001526        -0.000061                   0.000592          0.019723
       random_rows             frac0.40_rep002   100 entropy_g050          0.002170 0.000686 0.001684 0.002486      0.000686      0.001267         0.000402                   0.000394          0.013130
       random_rows             frac0.30_rep077    75 entropy_g075          0.002174 0.000687 0.001586 0.002236      0.000687      0.001316         0.000271                   0.001817          0.012178
       random_rows             frac0.30_rep221    75 entropy_g050          0.002225 0.000710 0.001652 0.002741      0.000710      0.001278         0.000341                   0.000406          0.013532
       random_rows             frac0.40_rep223   100 entropy_g075          0.002225 0.000636 0.001282 0.002719      0.000636      0.001519         0.000336                   0.001969          0.011919
       random_rows             frac0.40_rep092   100 entropy_g050          0.002227 0.000746 0.001473 0.002472      0.000746      0.001500         0.000353                   0.000490          0.013641
       random_rows             frac0.40_rep197   100 entropy_g050          0.002253 0.000779 0.001499 0.002345      0.000779      0.001544         0.000363                   0.000422          0.014081
subject_contiguous             frac0.25_rep150    64 entropy_g075          0.002271 0.000765 0.001396 0.002507      0.000765      0.001755         0.000335                   0.000372          0.012410
       random_rows             frac0.20_rep115    50 entropy_g050          0.002273 0.000707 0.001523 0.002785      0.000707      0.001463         0.000315                   0.000782          0.014044
```

## Per-Pair Policy Error

```
                 heldout_pair             policy  pair_abs_error_mean  pair_abs_error_max  pair_signed_error_mean      top_mask_kind               top_mask_name top_prior_name
        anchor578+cvjepa_a2c8          l2o_best1             0.000466            0.000872                0.000407        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8    l2o_best12_mean             0.000325            0.000555                0.000230        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8     l2o_best5_mean             0.000355            0.000634                0.000279        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8  oracle_pair_best1             0.000121            0.000137               -0.000016        random_rows             frac0.30_rep056   entropy_g075
        anchor578+cvjepa_a2c8   structured_best1             0.000229            0.000365                0.000136 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+cvjepa_a2c8 subject_best3_mean             0.000392            0.000709                0.000317 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+jepa_bad_q2          l2o_best1             0.000958            0.001569                0.000958        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2    l2o_best12_mean             0.001017            0.001615                0.001017        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2     l2o_best5_mean             0.000909            0.001474                0.000909        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2  oracle_pair_best1             0.000800            0.001395                0.000595 subject_contiguous             frac0.25_rep099   entropy_g075
        anchor578+jepa_bad_q2   structured_best1             0.001022            0.001338                0.001022 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+jepa_bad_q2 subject_best3_mean             0.000940            0.001514                0.000940 subject_contiguous             frac0.40_rep052   entropy_g075
  anchor578+jepa_bad_residual          l2o_best1             0.001304            0.001609                0.000305        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual    l2o_best12_mean             0.001440            0.001673                0.000232        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual     l2o_best5_mean             0.001345            0.001526                0.000181        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual  oracle_pair_best1             0.001298            0.001580                0.000282        random_rows             frac0.40_rep002   entropy_g075
  anchor578+jepa_bad_residual   structured_best1             0.001346            0.001480                0.000134 subject_contiguous             frac0.40_rep052   entropy_g075
  anchor578+jepa_bad_residual subject_best3_mean             0.001427            0.001598                0.000170 subject_contiguous             frac0.40_rep052   entropy_g075
         anchor578+lejepa_bad          l2o_best1             0.000835            0.001576                0.000835        random_rows             frac0.40_rep009   entropy_g075
         anchor578+lejepa_bad    l2o_best12_mean             0.000872            0.001615                0.000872        random_rows             frac0.40_rep009   entropy_g075
         anchor578+lejepa_bad     l2o_best5_mean             0.000804            0.001464                0.000804        random_rows             frac0.40_rep009   entropy_g075
         anchor578+lejepa_bad  oracle_pair_best1             0.000722            0.001294                0.000572 subject_contiguous             frac0.40_rep052   entropy_g075
         anchor578+lejepa_bad   structured_best1             0.000722            0.001294                0.000572 subject_contiguous             frac0.40_rep052   entropy_g075
         anchor578+lejepa_bad subject_best3_mean             0.000750            0.001490                0.000740 subject_contiguous             frac0.40_rep052   entropy_g075
          anchor578+ordinal_q          l2o_best1             0.001217            0.001719                0.001217        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q    l2o_best12_mean             0.001402            0.001831                0.001402        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q     l2o_best5_mean             0.001241            0.001652                0.001241        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q  oracle_pair_best1             0.000708            0.001398                0.000708 subject_contiguous             frac0.25_rep099   entropy_g075
          anchor578+ordinal_q   structured_best1             0.001333            0.001615                0.001333 subject_contiguous             frac0.40_rep052   entropy_g075
          anchor578+ordinal_q subject_best3_mean             0.001252            0.001729                0.001252 subject_contiguous             frac0.40_rep052   entropy_g075
              anchor578+raw05          l2o_best1             0.000385            0.000701                0.000385        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05    l2o_best12_mean             0.000239            0.000374                0.000239        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05     l2o_best5_mean             0.000267            0.000448                0.000267        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05  oracle_pair_best1             0.000073            0.000139                0.000073        random_rows             frac0.30_rep056   entropy_g075
              anchor578+raw05   structured_best1             0.000140            0.000178                0.000140 subject_contiguous             frac0.40_rep052   entropy_g075
              anchor578+raw05 subject_best3_mean             0.000289            0.000491                0.000289 subject_contiguous             frac0.40_rep052   entropy_g075
      cvjepa_a2c8+jepa_bad_q2          l2o_best1             0.000178            0.000276                0.000098        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2    l2o_best12_mean             0.000221            0.000335                0.000113        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2     l2o_best5_mean             0.000175            0.000260                0.000084        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2  oracle_pair_best1             0.000042            0.000083               -0.000041        random_rows             frac0.60_rep001          raw05
      cvjepa_a2c8+jepa_bad_q2   structured_best1             0.000357            0.000614                0.000257 subject_contiguous             frac0.40_rep052   entropy_g075
      cvjepa_a2c8+jepa_bad_q2 subject_best3_mean             0.000190            0.000290                0.000099 subject_contiguous             frac0.40_rep052   entropy_g075
cvjepa_a2c8+jepa_bad_residual          l2o_best1             0.000460            0.000847               -0.000460        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual    l2o_best12_mean             0.000568            0.001035               -0.000568        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual     l2o_best5_mean             0.000540            0.000997               -0.000540        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual  oracle_pair_best1             0.000372            0.000664               -0.000372        random_rows             frac0.40_rep002           a2c8
cvjepa_a2c8+jepa_bad_residual   structured_best1             0.000565            0.001034               -0.000565 subject_contiguous             frac0.40_rep052   entropy_g075
cvjepa_a2c8+jepa_bad_residual subject_best3_mean             0.000595            0.001105               -0.000595 subject_contiguous             frac0.40_rep052   entropy_g075
       cvjepa_a2c8+lejepa_bad          l2o_best1             0.000059            0.000082               -0.000059        random_rows             frac0.40_rep009   entropy_g075
       cvjepa_a2c8+lejepa_bad    l2o_best12_mean             0.000083            0.000111               -0.000083        random_rows             frac0.40_rep009   entropy_g075
       cvjepa_a2c8+lejepa_bad     l2o_best5_mean             0.000051            0.000092               -0.000051        random_rows             frac0.40_rep009   entropy_g075
       cvjepa_a2c8+lejepa_bad  oracle_pair_best1             0.000028            0.000056               -0.000028        random_rows             frac0.40_rep009          raw05
       cvjepa_a2c8+lejepa_bad   structured_best1             0.000191            0.000279               -0.000191 subject_contiguous             frac0.40_rep052   entropy_g075
       cvjepa_a2c8+lejepa_bad subject_best3_mean             0.000125            0.000157               -0.000125 subject_contiguous             frac0.40_rep052   entropy_g075
        cvjepa_a2c8+ordinal_q          l2o_best1             0.000119            0.000158                0.000039        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q    l2o_best12_mean             0.000164            0.000220                0.000056        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q     l2o_best5_mean             0.000143            0.000196                0.000052        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q  oracle_pair_best1             0.000062            0.000084               -0.000022      subject_order per_subject_prefix_frac0.25   entropy_g075
        cvjepa_a2c8+ordinal_q   structured_best1             0.000244            0.000389                0.000144 subject_contiguous             frac0.40_rep052   entropy_g075
        cvjepa_a2c8+ordinal_q subject_best3_mean             0.000112            0.000132                0.000020 subject_contiguous             frac0.40_rep052   entropy_g075
            cvjepa_a2c8+raw05          l2o_best1             0.000515            0.000535                0.000515        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05    l2o_best12_mean             0.000538            0.000569                0.000538        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05     l2o_best5_mean             0.000575            0.000597                0.000575        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05  oracle_pair_best1             0.000027            0.000031                0.000004        random_rows             frac0.40_rep009          raw05
            cvjepa_a2c8+raw05   structured_best1             0.000531            0.000558                0.000531 subject_contiguous             frac0.40_rep052   entropy_g075
            cvjepa_a2c8+raw05 subject_best3_mean             0.000612            0.000631                0.000612 subject_contiguous             frac0.40_rep052   entropy_g075
jepa_bad_q2+jepa_bad_residual          l2o_best1             0.000574            0.001043               -0.000574        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual    l2o_best12_mean             0.000703            0.001259               -0.000703        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual     l2o_best5_mean             0.000728            0.001253               -0.000728        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual  oracle_pair_best1             0.000374            0.000701               -0.000327       global_order                rowmod4_rem3          raw05
jepa_bad_q2+jepa_bad_residual   structured_best1             0.000589            0.001038               -0.000449 subject_contiguous             frac0.40_rep052   entropy_g075
jepa_bad_q2+jepa_bad_residual subject_best3_mean             0.000766            0.001327               -0.000766 subject_contiguous             frac0.40_rep052   entropy_g075
       jepa_bad_q2+lejepa_bad          l2o_best1             0.000201            0.000351                0.000201        random_rows             frac0.40_rep009   entropy_g075
       jepa_bad_q2+lejepa_bad    l2o_best12_mean             0.000234            0.000412                0.000234        random_rows             frac0.40_rep009   entropy_g075
       jepa_bad_q2+lejepa_bad     l2o_best5_mean             0.000213            0.000332                0.000213        random_rows             frac0.40_rep009   entropy_g075
       jepa_bad_q2+lejepa_bad  oracle_pair_best1             0.000072            0.000101                0.000072        random_rows             frac0.60_rep001          raw05
       jepa_bad_q2+lejepa_bad   structured_best1             0.000478            0.000698                0.000220 subject_contiguous             frac0.40_rep052   entropy_g075
       jepa_bad_q2+lejepa_bad subject_best3_mean             0.000217            0.000358                0.000141 subject_contiguous             frac0.40_rep052   entropy_g075
        jepa_bad_q2+ordinal_q          l2o_best1             0.000365            0.000380                0.000365        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q    l2o_best12_mean             0.000492            0.000579                0.000492        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q     l2o_best5_mean             0.000401            0.000475                0.000401        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q  oracle_pair_best1             0.000144            0.000204               -0.000060 subject_contiguous             frac0.25_rep099   entropy_g050
        jepa_bad_q2+ordinal_q   structured_best1             0.000631            0.000669                0.000631 subject_contiguous             frac0.40_rep052   entropy_g075
        jepa_bad_q2+ordinal_q subject_best3_mean             0.000341            0.000345                0.000341 subject_contiguous             frac0.40_rep052   entropy_g075
            jepa_bad_q2+raw05          l2o_best1             0.000175            0.000265                0.000175        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05    l2o_best12_mean             0.000217            0.000322                0.000217        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05     l2o_best5_mean             0.000171            0.000245                0.000171        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05  oracle_pair_best1             0.000039            0.000077                0.000038        random_rows             frac0.60_rep001          raw05
            jepa_bad_q2+raw05   structured_best1             0.000354            0.000604                0.000354 subject_contiguous             frac0.40_rep052   entropy_g075
            jepa_bad_q2+raw05 subject_best3_mean             0.000187            0.000277                0.000187 subject_contiguous             frac0.40_rep052   entropy_g075
 jepa_bad_residual+lejepa_bad          l2o_best1             0.000545            0.000986               -0.000545        random_rows             frac0.40_rep009   entropy_g075
 jepa_bad_residual+lejepa_bad    l2o_best12_mean             0.000689            0.001198               -0.000689        random_rows             frac0.40_rep009   entropy_g075
 jepa_bad_residual+lejepa_bad     l2o_best5_mean             0.000642            0.001149               -0.000642        random_rows             frac0.40_rep009   entropy_g075
 jepa_bad_residual+lejepa_bad  oracle_pair_best1             0.000426            0.000717               -0.000291       global_order                rowmod4_rem3          raw05
 jepa_bad_residual+lejepa_bad   structured_best1             0.000847            0.001206               -0.000847 subject_contiguous             frac0.40_rep052   entropy_g075
 jepa_bad_residual+lejepa_bad subject_best3_mean             0.000798            0.001256               -0.000798 subject_contiguous             frac0.40_rep052   entropy_g075
  jepa_bad_residual+ordinal_q          l2o_best1             0.000666            0.000971               -0.000305        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q    l2o_best12_mean             0.000847            0.001162               -0.000314        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q     l2o_best5_mean             0.000760            0.001119               -0.000359        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q  oracle_pair_best1             0.000666            0.000971               -0.000305        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q   structured_best1             0.000805            0.001102               -0.000297 subject_contiguous             frac0.40_rep052   entropy_g075
  jepa_bad_residual+ordinal_q subject_best3_mean             0.000707            0.001192               -0.000485 subject_contiguous             frac0.40_rep052   entropy_g075
      jepa_bad_residual+raw05          l2o_best1             0.000453            0.000826               -0.000373        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05    l2o_best12_mean             0.000558            0.001010               -0.000452        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05     l2o_best5_mean             0.000528            0.000968               -0.000439        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05  oracle_pair_best1             0.000368            0.000665               -0.000296        random_rows             frac0.40_rep002           a2c8
      jepa_bad_residual+raw05   structured_best1             0.000561            0.001021               -0.000460 subject_contiguous             frac0.40_rep052   entropy_g075
      jepa_bad_residual+raw05 subject_best3_mean             0.000586            0.001081               -0.000495 subject_contiguous             frac0.40_rep052   entropy_g075
         lejepa_bad+ordinal_q          l2o_best1             0.000215            0.000386                0.000215        random_rows             frac0.40_rep009   entropy_g075
         lejepa_bad+ordinal_q    l2o_best12_mean             0.000337            0.000596                0.000337        random_rows             frac0.40_rep009   entropy_g075
         lejepa_bad+ordinal_q     l2o_best5_mean             0.000301            0.000486                0.000301        random_rows             frac0.40_rep009   entropy_g075
         lejepa_bad+ordinal_q  oracle_pair_best1             0.000177            0.000299                0.000177 subject_contiguous             frac0.25_rep099   entropy_g050
         lejepa_bad+ordinal_q   structured_best1             0.000420            0.000645                0.000224 subject_contiguous             frac0.40_rep052   entropy_g075
         lejepa_bad+ordinal_q subject_best3_mean             0.000205            0.000360                0.000155 subject_contiguous             frac0.40_rep052   entropy_g075
             lejepa_bad+raw05          l2o_best1             0.000061            0.000086                0.000025        random_rows             frac0.40_rep009   entropy_g075
             lejepa_bad+raw05    l2o_best12_mean             0.000089            0.000114                0.000024        random_rows             frac0.40_rep009   entropy_g075
             lejepa_bad+raw05     l2o_best5_mean             0.000062            0.000097                0.000035        random_rows             frac0.40_rep009   entropy_g075
             lejepa_bad+raw05  oracle_pair_best1             0.000030            0.000051                0.000030        random_rows             frac0.40_rep009          raw05
             lejepa_bad+raw05   structured_best1             0.000196            0.000284               -0.000088 subject_contiguous             frac0.40_rep052   entropy_g075
             lejepa_bad+raw05 subject_best3_mean             0.000138            0.000176               -0.000039 subject_contiguous             frac0.40_rep052   entropy_g075
              ordinal_q+raw05          l2o_best1             0.000111            0.000137                0.000111        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05    l2o_best12_mean             0.000159            0.000206                0.000159        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05     l2o_best5_mean             0.000136            0.000175                0.000136        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05  oracle_pair_best1             0.000065            0.000089                0.000065      subject_order per_subject_prefix_frac0.25   entropy_g075
              ordinal_q+raw05   structured_best1             0.000242            0.000380                0.000242 subject_contiguous             frac0.40_rep052   entropy_g075
              ordinal_q+raw05 subject_best3_mean             0.000108            0.000118                0.000108 subject_contiguous             frac0.40_rep052   entropy_g075
```

## Interpretation

- L2O is intentionally harsher than LOO. A source that stays near the top here is less likely to be merely fitting one anchor's idiosyncrasy.
- If L2O-best masks differ from LOO-best masks, candidate generation should shrink or ensemble across both rankings instead of trusting a single mask.
