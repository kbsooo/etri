# Direct Label Inverse7 Leave-Two-Anchor CV

This trains direct-label inverse solutions on four known public anchors and predicts the two held-out anchors.

## Overall Policy Error

```
            policy  pair_abs_error_mean  pair_abs_error_max  pair_signed_error_mean  top_l2o_source_score
 oracle_pair_best1             0.000344            0.000552                0.000019              0.002433
         l2o_best1             0.000532            0.000798                0.000189              0.001585
    l2o_best5_mean             0.000556            0.000808                0.000144              0.001585
subject_best3_mean             0.000575            0.000848                0.000121              0.001712
   l2o_best12_mean             0.000598            0.000858                0.000171              0.001585
  structured_best1             0.000607            0.000843                0.000193              0.001712
```

## Best Source Masks

```
         mask_kind                   mask_name  rows   prior_name  l2o_source_score  l2o_mae  l2o_p90  l2o_max  l2o_pair_mae  l2o_pair_p90  l2o_signed_mean  train_solution_score_mean  train_shift_mean
       random_rows             frac0.40_rep009   100 entropy_g075          0.001585 0.000532 0.001109 0.001720      0.000532      0.001112         0.000189                   0.000300          0.009990
       random_rows             frac0.40_rep002   100 entropy_g075          0.001710 0.000569 0.001218 0.001835      0.000569      0.001174         0.000237                   0.000323          0.010773
subject_contiguous             frac0.40_rep052   101 entropy_g075          0.001712 0.000607 0.001287 0.001606      0.000607      0.001205         0.000193                   0.000321          0.010706
       random_rows             frac0.40_rep040   100 entropy_g075          0.001793 0.000622 0.001377 0.001706      0.000622      0.001258         0.000190                   0.000439          0.011024
subject_contiguous             frac0.25_rep099    64 entropy_g075          0.001807 0.000622 0.001393 0.001865      0.000622      0.001159        -0.000088                   0.000433          0.014425
       random_rows             frac0.30_rep221    75 entropy_g075          0.001838 0.000614 0.001407 0.001982      0.000614      0.001245         0.000184                   0.000338          0.011283
       random_rows             frac0.20_rep114    50 entropy_g075          0.001848 0.000589 0.001591 0.002009      0.000589      0.001341         0.000075                   0.000317          0.010553
       random_rows             frac0.40_rep092   100 entropy_g075          0.001897 0.000665 0.001364 0.001866      0.000665      0.001337         0.000227                   0.000437          0.011435
       random_rows             frac0.40_rep197   100 entropy_g075          0.001911 0.000695 0.001442 0.001714      0.000695      0.001319         0.000231                   0.000359          0.011952
       random_rows             frac0.20_rep115    50 entropy_g075          0.001928 0.000604 0.001495 0.002123      0.000604      0.001361         0.000130                   0.000733          0.011768
       random_rows             frac0.50_rep073   125 entropy_g075          0.001967 0.000683 0.001380 0.001897      0.000683      0.001400         0.000232                   0.000766          0.011262
subject_contiguous             frac0.50_rep142   126 entropy_g075          0.001975 0.000671 0.001322 0.002162      0.000671      0.001434         0.000256                   0.000338          0.011258
       random_rows             frac0.40_rep132   100 entropy_g075          0.001989 0.000634 0.001156 0.002318      0.000634      0.001527         0.000291                   0.000723          0.010663
       random_rows             frac0.30_rep056    75 entropy_g075          0.001997 0.000739 0.001505 0.001823      0.000739      0.001382         0.000242                   0.000330          0.011015
      global_order                rowmod4_rem3    62 entropy_g075          0.001999 0.000649 0.001266 0.002283      0.000649      0.001519         0.000330                   0.000316          0.010521
     subject_order per_subject_prefix_frac0.25    64 entropy_g075          0.002001 0.000741 0.001544 0.001746      0.000741      0.001263         0.000216                   0.000682          0.012711
       random_rows             frac0.50_rep115   125 entropy_g075          0.002036 0.000687 0.001418 0.002123      0.000687      0.001475         0.000235                   0.000593          0.011744
subject_contiguous             frac0.25_rep099    64 entropy_g050          0.002044 0.000691 0.001856 0.001978      0.000691      0.001278         0.000067                   0.000456          0.015186
       random_rows             frac0.40_rep027   100 entropy_g075          0.002044 0.000695 0.001459 0.002084      0.000695      0.001388         0.000226                   0.000832          0.012130
       random_rows             frac0.30_rep192    75 entropy_g075          0.002070 0.000741 0.001434 0.001983      0.000741      0.001492         0.000286                   0.000535          0.010922
       random_rows             frac0.50_rep156   125 entropy_g075          0.002114 0.000738 0.001426 0.002186      0.000738      0.001535         0.000296                   0.000422          0.011262
subject_contiguous             frac0.40_rep009   101 entropy_g075          0.002128 0.000739 0.001769 0.002087      0.000739      0.001462         0.000163                   0.000369          0.012314
       random_rows             frac0.60_rep001   150 entropy_g075          0.002135 0.000681 0.001573 0.002249      0.000681      0.001437         0.000198                   0.001262          0.012561
       random_rows             frac0.40_rep052   100 entropy_g075          0.002157 0.000725 0.001445 0.002367      0.000725      0.001622         0.000265                   0.000360          0.012016
       random_rows             frac0.50_rep171   125 entropy_g075          0.002223 0.000721 0.001717 0.002395      0.000721      0.001564         0.000203                   0.000662          0.012563
    single_subject                        id01    27 entropy_g075          0.002239 0.000829 0.001537 0.001964      0.000829      0.001581        -0.000160                   0.000559          0.018618
       random_rows             frac0.30_rep210    75 entropy_g075          0.002252 0.000738 0.001675 0.002317      0.000738      0.001532         0.000265                   0.001014          0.012478
       random_rows             frac0.40_rep009   100 entropy_g050          0.002257 0.000726 0.001806 0.002417      0.000726      0.001456         0.000389                   0.000366          0.012211
       random_rows             frac0.50_rep169   125 entropy_g075          0.002272 0.000777 0.001435 0.002520      0.000777      0.001691         0.000334                   0.000357          0.011886
       random_rows             frac0.20_rep114    50 entropy_g050          0.002282 0.000773 0.001678 0.002600      0.000773      0.001521         0.000266                   0.000357          0.011907
       random_rows             frac0.30_rep077    75 entropy_g075          0.002288 0.000759 0.001632 0.002246      0.000759      0.001524         0.000294                   0.001586          0.011417
       random_rows             frac0.40_rep002   100 entropy_g050          0.002295 0.000747 0.001772 0.002499      0.000747      0.001435         0.000425                   0.000378          0.012616
subject_contiguous             frac0.40_rep052   101 entropy_g050          0.002295 0.000796 0.001667 0.002355      0.000796      0.001525         0.000388                   0.000373          0.012444
       random_rows             frac0.40_rep040   100 entropy_g050          0.002317 0.000802 0.001725 0.002335      0.000802      0.001515         0.000377                   0.000457          0.012844
       random_rows             frac0.40_rep223   100 entropy_g075          0.002347 0.000705 0.001423 0.002725      0.000705      0.001701         0.000366                   0.001615          0.011196
subject_contiguous             frac0.25_rep150    64 entropy_g075          0.002359 0.000821 0.001482 0.002496      0.000821      0.001772         0.000418                   0.000341          0.011367
       random_rows             frac0.40_rep092   100 entropy_g050          0.002386 0.000842 0.001551 0.002479      0.000842      0.001647         0.000413                   0.000451          0.013036
       random_rows             frac0.40_rep197   100 entropy_g050          0.002403 0.000877 0.001566 0.002347      0.000877      0.001660         0.000424                   0.000403          0.013432
       random_rows             frac0.30_rep221    75 entropy_g050          0.002413 0.000807 0.001728 0.002741      0.000807      0.001555         0.000388                   0.000390          0.013008
     subject_order per_subject_prefix_frac0.25    64 entropy_g050          0.002414 0.000882 0.001737 0.002274      0.000882      0.001565         0.000366                   0.000570          0.014063
```

## Per-Pair Policy Error

```
                 heldout_pair             policy  pair_abs_error_mean  pair_abs_error_max  pair_signed_error_mean      top_mask_kind               top_mask_name top_prior_name
        anchor578+cvjepa_a2c8          l2o_best1             0.000466            0.000873            4.069950e-04        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8    l2o_best12_mean             0.000324            0.000552            2.280170e-04        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8     l2o_best5_mean             0.000356            0.000637            2.803480e-04        random_rows             frac0.40_rep009   entropy_g075
        anchor578+cvjepa_a2c8  oracle_pair_best1             0.000135            0.000136           -5.160000e-07        random_rows             frac0.30_rep056   entropy_g075
        anchor578+cvjepa_a2c8   structured_best1             0.000214            0.000332            1.182980e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+cvjepa_a2c8 subject_best3_mean             0.000383            0.000690            3.070140e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+jepa_bad_q2          l2o_best1             0.000958            0.001572            9.584170e-04        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2    l2o_best12_mean             0.001018            0.001619            1.018277e-03        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2     l2o_best5_mean             0.000908            0.001475            9.081150e-04        random_rows             frac0.40_rep009   entropy_g075
        anchor578+jepa_bad_q2  oracle_pair_best1             0.000808            0.001399            5.912090e-04 subject_contiguous             frac0.25_rep099   entropy_g075
        anchor578+jepa_bad_q2   structured_best1             0.001021            0.001326            1.020853e-03 subject_contiguous             frac0.40_rep052   entropy_g075
        anchor578+jepa_bad_q2 subject_best3_mean             0.000937            0.001507            9.372160e-04 subject_contiguous             frac0.40_rep052   entropy_g075
  anchor578+jepa_bad_residual          l2o_best1             0.001307            0.001607            2.999420e-04        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual    l2o_best12_mean             0.001449            0.001669            2.201060e-04        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual     l2o_best5_mean             0.001353            0.001524            1.711200e-04        random_rows             frac0.40_rep009   entropy_g075
  anchor578+jepa_bad_residual  oracle_pair_best1             0.001289            0.001585            2.960490e-04        random_rows             frac0.40_rep002   entropy_g075
  anchor578+jepa_bad_residual   structured_best1             0.001373            0.001464            9.047400e-05 subject_contiguous             frac0.40_rep052   entropy_g075
  anchor578+jepa_bad_residual subject_best3_mean             0.001444            0.001584            1.402350e-04 subject_contiguous             frac0.40_rep052   entropy_g075
          anchor578+ordinal_q          l2o_best1             0.001215            0.001720            1.215169e-03        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q    l2o_best12_mean             0.001403            0.001835            1.402634e-03        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q     l2o_best5_mean             0.001239            0.001653            1.239442e-03        random_rows             frac0.40_rep009   entropy_g075
          anchor578+ordinal_q  oracle_pair_best1             0.000701            0.001399            7.011290e-04 subject_contiguous             frac0.25_rep099   entropy_g075
          anchor578+ordinal_q   structured_best1             0.001328            0.001606            1.327600e-03 subject_contiguous             frac0.40_rep052   entropy_g075
          anchor578+ordinal_q subject_best3_mean             0.001246            0.001722            1.246306e-03 subject_contiguous             frac0.40_rep052   entropy_g075
              anchor578+raw05          l2o_best1             0.000385            0.000701            3.851400e-04        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05    l2o_best12_mean             0.000237            0.000369            2.370220e-04        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05     l2o_best5_mean             0.000267            0.000447            2.671870e-04        random_rows             frac0.40_rep009   entropy_g075
              anchor578+raw05  oracle_pair_best1             0.000086            0.000137            8.577100e-05        random_rows             frac0.30_rep056   entropy_g075
              anchor578+raw05   structured_best1             0.000124            0.000144            1.243190e-04 subject_contiguous             frac0.40_rep052   entropy_g075
              anchor578+raw05 subject_best3_mean             0.000279            0.000469            2.786250e-04 subject_contiguous             frac0.40_rep052   entropy_g075
      cvjepa_a2c8+jepa_bad_q2          l2o_best1             0.000178            0.000277            9.856200e-05        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2    l2o_best12_mean             0.000223            0.000338            1.145190e-04        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2     l2o_best5_mean             0.000176            0.000262            8.558700e-05        random_rows             frac0.40_rep009   entropy_g075
      cvjepa_a2c8+jepa_bad_q2  oracle_pair_best1             0.000042            0.000083           -4.092500e-05        random_rows             frac0.60_rep001          raw05
      cvjepa_a2c8+jepa_bad_q2   structured_best1             0.000364            0.000629            2.641650e-04 subject_contiguous             frac0.40_rep052   entropy_g075
      cvjepa_a2c8+jepa_bad_q2 subject_best3_mean             0.000194            0.000296            1.022780e-04 subject_contiguous             frac0.40_rep052   entropy_g075
cvjepa_a2c8+jepa_bad_residual          l2o_best1             0.000469            0.000863           -4.688780e-04        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual    l2o_best12_mean             0.000587            0.001072           -5.873570e-04        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual     l2o_best5_mean             0.000556            0.001027           -5.558260e-04        random_rows             frac0.40_rep009   entropy_g075
cvjepa_a2c8+jepa_bad_residual  oracle_pair_best1             0.000386            0.000690           -3.857660e-04        random_rows             frac0.40_rep002           a2c8
cvjepa_a2c8+jepa_bad_residual   structured_best1             0.000607            0.001117           -6.073620e-04 subject_contiguous             frac0.40_rep052   entropy_g075
cvjepa_a2c8+jepa_bad_residual subject_best3_mean             0.000625            0.001165           -6.254220e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        cvjepa_a2c8+ordinal_q          l2o_best1             0.000120            0.000160            3.968100e-05        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q    l2o_best12_mean             0.000163            0.000218            5.456100e-05        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q     l2o_best5_mean             0.000143            0.000195            5.209300e-05        random_rows             frac0.40_rep009   entropy_g075
        cvjepa_a2c8+ordinal_q  oracle_pair_best1             0.000043            0.000084           -4.285000e-05      subject_order per_subject_prefix_frac0.25   entropy_g075
        cvjepa_a2c8+ordinal_q   structured_best1             0.000244            0.000386            1.427440e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        cvjepa_a2c8+ordinal_q subject_best3_mean             0.000112            0.000131            1.902000e-05 subject_contiguous             frac0.40_rep052   entropy_g075
            cvjepa_a2c8+raw05          l2o_best1             0.000516            0.000536            5.156000e-04        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05    l2o_best12_mean             0.000538            0.000569            5.376680e-04        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05     l2o_best5_mean             0.000575            0.000596            5.747700e-04        random_rows             frac0.40_rep009   entropy_g075
            cvjepa_a2c8+raw05  oracle_pair_best1             0.000027            0.000031            4.031000e-06        random_rows             frac0.40_rep009          raw05
            cvjepa_a2c8+raw05   structured_best1             0.000529            0.000556            5.287590e-04 subject_contiguous             frac0.40_rep052   entropy_g075
            cvjepa_a2c8+raw05 subject_best3_mean             0.000611            0.000630            6.109120e-04 subject_contiguous             frac0.40_rep052   entropy_g075
jepa_bad_q2+jepa_bad_residual          l2o_best1             0.000583            0.001057           -5.834250e-04        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual    l2o_best12_mean             0.000724            0.001292           -7.239730e-04        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual     l2o_best5_mean             0.000743            0.001277           -7.425080e-04        random_rows             frac0.40_rep009   entropy_g075
jepa_bad_q2+jepa_bad_residual  oracle_pair_best1             0.000368            0.000683           -3.147130e-04       global_order                rowmod4_rem3          raw05
jepa_bad_q2+jepa_bad_residual   structured_best1             0.000622            0.001130           -5.078970e-04 subject_contiguous             frac0.40_rep052   entropy_g075
jepa_bad_q2+jepa_bad_residual subject_best3_mean             0.000808            0.001392           -8.080110e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        jepa_bad_q2+ordinal_q          l2o_best1             0.000364            0.000378            3.635090e-04        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q    l2o_best12_mean             0.000490            0.000576            4.903510e-04        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q     l2o_best5_mean             0.000398            0.000471            3.978570e-04        random_rows             frac0.40_rep009   entropy_g075
        jepa_bad_q2+ordinal_q  oracle_pair_best1             0.000142            0.000215           -7.315600e-05 subject_contiguous             frac0.25_rep099   entropy_g050
        jepa_bad_q2+ordinal_q   structured_best1             0.000637            0.000681            6.365650e-04 subject_contiguous             frac0.40_rep052   entropy_g075
        jepa_bad_q2+ordinal_q subject_best3_mean             0.000341            0.000349            3.406200e-04 subject_contiguous             frac0.40_rep052   entropy_g075
            jepa_bad_q2+raw05          l2o_best1             0.000175            0.000266            1.749430e-04        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05    l2o_best12_mean             0.000218            0.000325            2.183210e-04        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05     l2o_best5_mean             0.000172            0.000248            1.720900e-04        random_rows             frac0.40_rep009   entropy_g075
            jepa_bad_q2+raw05  oracle_pair_best1             0.000039            0.000077            3.785700e-05        random_rows             frac0.60_rep001          raw05
            jepa_bad_q2+raw05   structured_best1             0.000362            0.000619            3.619700e-04 subject_contiguous             frac0.40_rep052   entropy_g075
            jepa_bad_q2+raw05 subject_best3_mean             0.000191            0.000284            1.910680e-04 subject_contiguous             frac0.40_rep052   entropy_g075
  jepa_bad_residual+ordinal_q          l2o_best1             0.000675            0.000983           -3.073650e-04        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q    l2o_best12_mean             0.000860            0.001187           -3.279080e-04        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q     l2o_best5_mean             0.000770            0.001139           -3.691380e-04        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q  oracle_pair_best1             0.000675            0.000983           -3.073650e-04        random_rows             frac0.40_rep009   entropy_g075
  jepa_bad_residual+ordinal_q   structured_best1             0.000838            0.001177           -3.390660e-04 subject_contiguous             frac0.40_rep052   entropy_g075
  jepa_bad_residual+ordinal_q subject_best3_mean             0.000731            0.001244           -5.126860e-04 subject_contiguous             frac0.40_rep052   entropy_g075
      jepa_bad_residual+raw05          l2o_best1             0.000461            0.000842           -3.814690e-04        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05    l2o_best12_mean             0.000577            0.001048           -4.709580e-04        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05     l2o_best5_mean             0.000545            0.001000           -4.550320e-04        random_rows             frac0.40_rep009   entropy_g075
      jepa_bad_residual+raw05  oracle_pair_best1             0.000382            0.000691           -3.091740e-04        random_rows             frac0.40_rep002           a2c8
      jepa_bad_residual+raw05   structured_best1             0.000604            0.001105           -5.015040e-04 subject_contiguous             frac0.40_rep052   entropy_g075
      jepa_bad_residual+raw05 subject_best3_mean             0.000617            0.001143           -5.255960e-04 subject_contiguous             frac0.40_rep052   entropy_g075
              ordinal_q+raw05          l2o_best1             0.000112            0.000139            1.121630e-04        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05    l2o_best12_mean             0.000158            0.000204            1.581540e-04        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05     l2o_best5_mean             0.000135            0.000174            1.352880e-04        random_rows             frac0.40_rep009   entropy_g075
              ordinal_q+raw05  oracle_pair_best1             0.000044            0.000089            4.432600e-05      subject_order per_subject_prefix_frac0.25   entropy_g075
              ordinal_q+raw05   structured_best1             0.000242            0.000378            2.419080e-04 subject_contiguous             frac0.40_rep052   entropy_g075
              ordinal_q+raw05 subject_best3_mean             0.000108            0.000117            1.081190e-04 subject_contiguous             frac0.40_rep052   entropy_g075
```

## Interpretation

- L2O is intentionally harsher than LOO. A source that stays near the top here is less likely to be merely fitting one anchor's idiosyncrasy.
- If L2O-best masks differ from LOO-best masks, candidate generation should shrink or ensemble across both rankings instead of trusting a single mask.
