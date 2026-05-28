# JEPA Ready Data Audit

This audit asks a stricter question than earlier JEPA-style experiments: if the hidden block itself is not visible, which data representation is still predictable from surrounding context, and does that predicted representation preserve label information?

## Interpretation Rule

- `current_visible_target`: partly-JEPA, because target-block raw/base information is visible.
- `strict_surround`: closer to JEPA, because only surrounding context and position are visible.
- `strict_rawonly`: only surrounding sensor-state latent.
- `strict_labelonly`: only surrounding label/base statistics.
- `strict_prior`: subject routine prior only.

## Best Representations Under Strict Surround

representation,context_variant,repr_r2,repr_cos,rate_chain_r2,rate_chain_cos,label_chain_r2,repr_to_true_rate_r2,repr_to_true_rate_cos,strict_rank_score
proto_hist,strict_surround,0.15914338747816797,0.4186709299683571,-0.06252808812215593,0.8757176548242569,-0.06672208911959726,-0.039604685377834264,0.8781243115663528,-0.002525538673210625
mean_latent,strict_surround,-0.34379841875724043,0.463808573782444,-0.020976664700740194,0.8784085363149643,-0.06260586396403134,0.022947292729355806,0.8898794800043106,-0.09289731172884606
proto_trans,strict_surround,-0.04020316912829147,0.31714530289173126,-0.08603324867356837,0.8793227225542068,-0.13412341803300004,-0.19337689204373543,0.867482140660286,-0.09604445746128257
window_state,strict_surround,-0.5256401014342011,0.4437455087900162,0.026872500033129354,0.8835072666406631,-0.050333285735724875,-0.0799628930835509,0.8760913014411926,-0.13262272895703933
modality_state,strict_surround,-0.5396154043978028,0.3965678885579109,-0.028655159119175655,0.8761908859014511,-0.05790188748966035,-0.031603542750442415,0.8797884583473206,-0.1569848971650858
label_state,strict_surround,-0.6568165765772384,0.25340503081679344,-0.5973736206562581,0.8199631124734879,-0.5933942737446531,0.8462709715186322,0.9799191504716873,-0.32350544120152513


## Visibility Gap

representation,current_visible_target_rate_chain_r2,strict_surround_rate_chain_r2,strict_gap,strict_rawonly_rate_chain_r2,strict_labelonly_rate_chain_r2,strict_prior_rate_chain_r2
window_state,0.02332300071581278,0.026872500033129354,-0.0035494993173165734,0.01975566415135857,0.057155386647750356,-0.04125866999954941
mean_latent,0.06247672232558407,-0.020976664700740194,0.08345338702632427,-0.022311855054783974,0.09678388177000508,-0.01811312354712205
modality_state,0.020341125742794702,-0.028655159119175655,0.04899628486197036,-0.024758149754448483,0.08097012236574491,-0.015554098987146048
proto_hist,-0.05758988295217751,-0.06252808812215593,0.004938205169978421,-0.06722317794912194,0.01304176317309566,-0.03374819138793034
proto_trans,-0.11120001921138839,-0.08603324867356837,-0.025166770537820016,-0.0791913913837658,0.026789208101049067,-0.038426345416187696
label_state,-0.5480510161144013,-0.5973736206562581,0.049322604541856774,-0.6195026293314113,0.04539011460484077,-0.1460982759573499


## Recommendations

1. If `strict_gap` is large, that representation is not a true JEPA target here; it depends on target-block-visible raw signal.
2. If `strict_surround_rate_chain_r2` stays strong, the representation is JEPA-ready and should be the next target latent.
3. If `strict_prior` is also strong, the data is better cast as subject routine tokens/prototypes rather than a raw hidden canvas.

## Files

- `jepa_ready_data_audit_folds.csv`
- `jepa_ready_data_audit_summary.csv`
- `jepa_ready_data_audit_gap.csv`