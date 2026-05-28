from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from hidden_block_latent_audit import TARGETS, clip, logit, read_submission, sigmoid  # noqa: E402
from hidden_block_orthogonal_gate_candidates import Candidate, stable_tag  # noqa: E402
from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402


SAFE_SOURCES = [
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "submission_hiddenblock_paretomix_w0.4_507296eb.csv",
    "submission_hiddenblock_rateprobe_neutral_95ebba6c.csv",
    "submission_hiddenblock_rateprobe_neutral_27ca3bb0.csv",
    "submission_hiddenblock_rateprobe_neutral_605de284.csv",
]


def mix_logits(a: np.ndarray, b: np.ndarray, w_b: float) -> np.ndarray:
    return clip(sigmoid((1.0 - w_b) * logit(a) + w_b * logit(b)))


def sequence_probe_sources() -> list[str]:
    proxy_path = OUT / "hidden_block_sequence_motif_candidate_proxy.csv"
    if not proxy_path.exists():
        return []
    proxy = pd.read_csv(proxy_path)
    if proxy.empty or "file" not in proxy.columns:
        return []
    pool: list[str] = []
    for f in proxy.sort_values(["raw_axis_expected_public_vs_stage2", "posterior_expected_public_vs_anchor"])["file"].head(8):
        if (OUT / str(f)).exists() and str(f) not in pool:
            pool.append(str(f))
    for f in proxy.sort_values(["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2"])["file"].head(8):
        if (OUT / str(f)).exists() and str(f) not in pool:
            pool.append(str(f))
    return pool[:12]


def main() -> None:
    probes = sequence_probe_sources()
    candidates: list[Candidate] = []
    for safe in SAFE_SOURCES:
        if not (OUT / safe).exists():
            continue
        safe_df = read_submission(OUT / safe)
        safe_pred = safe_df[TARGETS].to_numpy(dtype=np.float64)
        for probe in probes:
            probe_pred = read_submission(OUT / probe)[TARGETS].to_numpy(dtype=np.float64)
            for w_probe in [0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]:
                pred = mix_logits(safe_pred, probe_pred, w_probe)
                tag = f"seqmotif_neutral_{stable_tag(safe + probe + str(w_probe))}"
                candidates.append(
                    Candidate(
                        tag=tag,
                        pred=pred,
                        kind="seqmotif_neutral",
                        targets="mixed",
                        params={
                            "safe_source": safe.removeprefix("submission_hiddenblock_").removesuffix(".csv")[:58],
                            "seqmotif_source": probe.removeprefix("submission_hiddenblock_rateprobe_").removesuffix(".csv")[:72],
                            "w_probe": w_probe,
                        },
                    )
                )

    if not candidates:
        print("[seqmotif neutral mix] no candidates")
        return

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
        pd.DataFrame([{"file": f"submission_hiddenblock_{c.tag}.csv", **c.params} for c in candidates]),
        on="file",
        how="left",
    )
    safe_proxy = proxy[proxy["delta_vs_raw05_rawaxis"].le(0.0)].copy()
    safe_proxy = safe_proxy.sort_values(
        ["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2", "bad_residual_axis_ratio"]
    )
    proxy.to_csv(OUT / "hidden_block_sequence_motif_neutral_mix_scores.csv", index=False)
    safe_proxy.to_csv(OUT / "hidden_block_sequence_motif_neutral_mix_safe_scores.csv", index=False)

    report = [
        "# Hidden Block Sequence Motif Neutral Mix",
        "",
        "Mixes sequence-motif block-rate probes with raw-axis-safe hidden-block candidates. The gate is raw-axis delta <= 0 versus raw05.",
        "",
        "## Probe sources",
        "",
        "\n".join(f"- `{p}`" for p in probes),
        "",
        "## Safe Candidates",
        "",
        "```csv",
        safe_proxy.head(40).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "hidden_block_sequence_motif_neutral_mix_report.md").write_text("\n".join(report), encoding="utf-8")
    print("[seqmotif neutral mix] generated", len(saved), "safe", len(safe_proxy))
    print(safe_proxy.head(40).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
