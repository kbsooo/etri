# Fixed Consensus Pruned State Decoder

Fixed target maps derived from nested selection counts. No per-fold source search is performed.

| variant | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| consensus_signal | 0.620577 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.529419 | 0.642911 | 0.068282 | 0.871897 |
| consensus_s4_temporal | 0.621674 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.580077 | 0.536285 | 0.640842 | 0.068108 | 0.875326 |
| consensus_conservative | 0.622785 | 0.670652 | 0.685743 | 0.673384 | 0.572511 | 0.580077 | 0.536285 | 0.640842 | 0.067290 | 0.877202 |
