from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, logit, read_submission, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import Candidate, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402


SAFE_SOURCES = [
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "submission_hiddenblock_paretomix_w0.4_507296eb.csv",
]

RATEPROBE_SOURCES = [
    "submission_hiddenblock_rateprobe_raw05_endpoint_local_q1q2q3_w0p1_c0ca1f42.csv",
    "submission_hiddenblock_rateprobe_raw05_endpoint_local_q1q2q3_w0p05_120a52ac.csv",
    "submission_hiddenblock_rateprobe_raw05_endpoint_strict_q1q2q3_w0p05_7c58557c.csv",
    "submission_hiddenblock_rateprobe_pareto03_endpoint_local_q1q2q3_w0p05_52ff6884.csv",
]


def mix_logits(a: np.ndarray, b: np.ndarray, w_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - w_b) * logit(a) + w_b * logit(b)))


def main() -> None:
    candidates: list[Candidate] = []
    for safe in SAFE_SOURCES:
        if not (OUT / safe).exists():
            continue
        safe_df = read_submission(OUT / safe)
        safe_pred = safe_df[TARGETS].to_numpy(dtype=np.float64)
        for probe in RATEPROBE_SOURCES:
            if not (OUT / probe).exists():
                continue
            probe_pred = read_submission(OUT / probe)[TARGETS].to_numpy(dtype=np.float64)
            for w_probe in [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]:
                pred = mix_logits(safe_pred, probe_pred, w_probe)
                tag = f"rateprobe_neutral_{stable_tag(safe + probe + str(w_probe))}"
                candidates.append(
                    Candidate(
                        tag=tag,
                        pred=pred,
                        kind="rateprobe_neutral",
                        targets="mixed",
                        params={
                            "safe_source": safe.removeprefix("submission_hiddenblock_").removesuffix(".csv")[:48],
                            "rateprobe_source": probe.removeprefix("submission_hiddenblock_rateprobe_").removesuffix(".csv")[:48],
                            "w_probe": w_probe,
                        },
                    )
                )

    template = read_submission(OUT / SAFE_SOURCES[0])
    saved = []
    for cand in candidates:
        out = template.copy()
        out[TARGETS] = cand.pred
        name = f"submission_hiddenblock_{cand.tag}.csv"
        out.to_csv(OUT / name, index=False)
        saved.append(name)

    proxy = public_proxy_scores(saved)
    proxy = proxy.merge(
        pd.DataFrame(
            [
                {
                    "file": f"submission_hiddenblock_{c.tag}.csv",
                    **c.params,
                }
                for c in candidates
            ]
        ),
        on="file",
        how="left",
    )
    safe_proxy = proxy[proxy["delta_vs_raw05_rawaxis"].le(0.0)].copy()
    safe_proxy = safe_proxy.sort_values(["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2"])
    proxy.to_csv(OUT / "hidden_block_rateprobe_neutral_mix_scores.csv", index=False)
    safe_proxy.to_csv(OUT / "hidden_block_rateprobe_neutral_mix_safe_scores.csv", index=False)

    report = [
        "# Hidden Block Rateprobe Neutral Mix",
        "",
        "Mixes endpoint-derived rate-probe candidates with raw-axis-safe hidden-block candidates. The gate is raw-axis delta <= 0 versus raw05.",
        "",
        "## Safe Candidates",
        "",
        "```csv",
        safe_proxy.head(30).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "hidden_block_rateprobe_neutral_mix_report.md").write_text("\n".join(report), encoding="utf-8")
    print("[rateprobe neutral mix] generated", len(saved), "safe", len(safe_proxy))
    print(safe_proxy.head(30).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
