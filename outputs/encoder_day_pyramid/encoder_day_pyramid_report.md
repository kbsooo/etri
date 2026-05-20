# Encoder Day Pyramid Report

- integrated input tensor: `(700, 288, 720)`
- base 5-min channels: `120`
- slots per day: `288`
- event tokens per day: max `48`, mean observed `20.73`
- prototype groups: `phone, physiology, mobility, light_ambience, social_place, missingness, sleep_proxy`

## Input Blocks

- `actual__*`: normalized 5-minute sensor values.
- `normal_twin__*`: label-free same-subject normal-day counterfactual baseline.
- `delta__*` and `abs_delta__*`: today minus normal twin.
- `observed__*`: sensor availability as data, not just a mask.
- `gap_since__*`: time since each sensor/channel was last observed.
- `event_tokens`: sparse headline events such as off-wrist gaps, night phone use, HR-at-rest, movement trips, and late light.
- `prototype_mixture`: modality-wise soft assignment to sleep/phone/mobility/physiology/social-place style prototypes.
