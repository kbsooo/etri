# Multires 30min Token Grid

- Output: `artifacts/multires_30min_grid.parquet`
- Shape: `33108 x 68`
- Dates: `2024-06-03` to `2024-11-19`
- Subjects: `10`

This grid keeps raw stream coverage as signal instead of hiding missingness. Object-list streams are first summarized row-wise, then aggregated into fixed within-day tokens.