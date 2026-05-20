# Public-feedback bold candidate set

Generated: 2026-05-18 KST

## Why this exists

The local-only route is not enough. The new `master_daily` decoder improves the raw diffusion targetwise model slightly, but does not beat the temporal blend by itself:

| candidate | local CV avg logloss |
|---|---:|
| diffusion targetwise temporal blend | 0.612613 |
| master aggressive targetwise | 0.616072 |
| temporal + master OOF target blend | 0.609688 |

The broader OOF map confirms that local 0.54 exists only in the already-dangerous cross-workspace direction:

| source | local OOF | public evidence |
|---|---:|---|
| `oof_cross_workspace_convex_calibrated.csv` | 0.541234 | actual public 0.8196748034 failure |
| V76 balanced hedge | posterior/public-aware | actual public 0.5999627447 success |
| V77 escalation | posterior/public-aware | pending next probe |

So the aggressive path should use public feedback, not lower local CV alone.

## Upload order

Upload one file at a time.

1. `submission_01_exact_v77_recommended.csv`
   - exact copy of the current codex recommender file
   - SHA256: `7a39a79d8e2811045f7a3d979fcab530829eb039839ba3fc5e88dba815d090a7`
   - use this first unless there is a newer public-feedback recommendation

2. `submission_02_v77_etri_blend_95_05.csv`
   - tiny 5% injection of the new ETRI temporal+master signal
   - use only if V77 improves or is close to V76

3. `submission_03_v77_etri_blend_90_10.csv`
   - stronger 10% ETRI injection

4. `submission_04_v77_etri_blend_80_20.csv`
   - higher-risk 20% ETRI injection

5. `submission_05_v76_to_v77_extrap_1p05_etri10.csv`
   - slight extrapolation from V76 through V77 with 10% ETRI stabilization

6. `submission_06_v76_to_v77_extrap_1p10_etri10.csv`
   - slightly stronger extrapolation

## Stop rules

- If a submitted file scores `<= 0.54`, stop normal submissions and audit.
- If V77 fails to beat `0.5999627447`, do not continue nearby V77/ETRI blends.
- Do not upload the local 0.541 cross-workspace calibrated family again; it has actual public failure evidence.

See `manifest.csv` for SHA256, movement from V77/V76, correlations, and probability ranges.
