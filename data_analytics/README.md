# HS-JEPA Data Analytics Audit

This directory contains the source-backed Data Analytics audit package for the
HS-JEPA competition work.

## Generated Files

- `build_hsjepa_audit.py`: reproducible local analysis script.
- `hsjepa_public_score_ledger.csv`: curated public LB sensor ledger with exact
  public log-loss values.
- `hsjepa_data_inventory.csv`: reviewed data source inventory.
- `hsjepa_target_inventory.csv`: train target prevalence summary.
- `hsjepa_experiment_inventory.csv`: reviewed HITL decision-file inventory.
- `hsjepa_day_file_inventory.csv`: local artifact activity by file date.
- `hsjepa_data_analytics_manifest.json`: MCP Data Analytics report manifest.
- `hsjepa_data_analytics_snapshot.json`: bounded report snapshot.
- `hsjepa_audit_summary.json`: compact generation summary.

## Date Splits

- `2026-06-04_hsjepa_audit.md`: H012/H042/H057 public score sensor audit.
- `2026-06-05_hsjepa_audit.md`: action-decoder bottleneck and negative sensor audit.
- `2026-06-07_hsjepa_audit.md`: current reproducibility and next-action audit.

## Main Finding

The biggest score movement is not from model capacity. It comes from changing
the unit of reasoning from row-level labels to row-target actions:

1. H012 moves the frontier from the E247 plateau (`0.5761589494`) to
   `0.5681234831`.
2. H057 reaches the current best public LB `0.5677475939` by treating the H042
   Q2-support rows as compact hidden human-state carriers.
3. H088 and H144/H145 show the active bottleneck is no longer discovering
   latent state. It is translating latent state into safe row-target actions.

The Data Analytics artifact was validated and rendered through the plugin using
the manifest/snapshot generated here.
