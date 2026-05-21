# Stable Extended Consensus Decoder

Fixed maps that combine stable nested selection counts with extended feature-family candidates. No target selection is performed inside this run.

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| extended_full_oof_winners | 0.616766 | 0.664980 | 0.689098 | 0.665606 | 0.565500 | 0.572205 | 0.534513 | 0.625461 | 0.069892 | 0.860714 |
| stable_signal_s4_temporal | 0.620281 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.529419 | 0.640842 | 0.068726 | 0.871113 |
| stable_prior_guarded | 0.622146 | 0.670652 | 0.685743 | 0.665606 | 0.575821 | 0.580077 | 0.536285 | 0.640842 | 0.066633 | 0.878825 |
| stable_nested_vote | 0.622837 | 0.670652 | 0.693460 | 0.665606 | 0.575821 | 0.577195 | 0.536285 | 0.640842 | 0.066150 | 0.879003 |
| q1_s4_only | 0.626191 | 0.670652 | 0.703140 | 0.676523 | 0.575821 | 0.580077 | 0.536285 | 0.640842 | 0.064413 | 0.882640 |
