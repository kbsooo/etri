from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_rate_reconstruction_audit import public_proxy_scores  # noqa: E402
from public_block_entropy_projection import (  # noqa: E402
    CONSTRAINT_FILES,
    KEY,
    TARGETS,
    blend_probs,
    expected_scores,
    load_public_scores,
    load_sub,
    sample_block_ids,
    solve_block_projection,
    stable_tag,
)
from raw05_jepa_q3s4_gate_audit import focused_scenario_scores  # noqa: E402


PRIORS = [
    ("count65", "submission_jepa_block_countshift_65d5ef0c.csv"),
    ("count3388", "submission_jepa_block_countshift_33884d08.csv"),
    ("countb2434", "submission_jepa_block_countshift_b2434a36.csv"),
    ("energy_balanced", "submission_jepa_energy_ensemble_0b862967.csv"),
    ("energy_focused", "submission_jepa_energy_ensemble_e187e70f.csv"),
    ("blockpublic", "submission_blockpublic_jepa_q3s4_8e3e0d92.csv"),
    ("publicmask", "submission_publicmask_jepa_q3s4_50528018.csv"),
    ("seq1501", "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv"),
]

TARGET_MASKS = {
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "core_q1_q3_s3_s4": ["Q1", "Q3", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "q3_only": ["Q3"],
    "s_only": ["S1", "S2", "S3", "S4"],
}

GAMMAS = [0.003, 0.006, 0.010, 0.015, 0.020, 0.030, 0.060, 0.10, 0.18, 0.28]


def file_exists(file_name: str) -> bool:
    return (OUT / file_name).exists()


def integrity(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ref_key = sample[KEY].reset_index(drop=True)
    for file_name in files:
        df = load_sub(file_name)
        pred = df[TARGETS].to_numpy(dtype=float)
        rows.append(
            {
                "file": file_name,
                "rows": len(df),
                "key_ok": bool(df[KEY].reset_index(drop=True).equals(ref_key)),
                "duplicate_keys": int(df.duplicated(KEY).sum()),
                "null_probs": int(df[TARGETS].isna().sum().sum()),
                "min_prob": float(np.nanmin(pred)),
                "max_prob": float(np.nanmax(pred)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        ["subject_id", "lifelog_date"]
    ).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    block_ids = sample_block_ids(train, sample)
    constraint_subs = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in CONSTRAINT_FILES]
    public_scores = load_public_scores()

    rows = []
    saved = []
    for prior_name, prior_file in PRIORS:
        if not file_exists(prior_file):
            continue
        prior_df = load_sub(prior_file)
        if not prior_df[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
            raise ValueError(f"key mismatch: {prior_file}")
        prior = prior_df[TARGETS].to_numpy(dtype=float)
        for mask_name, target_names in TARGET_MASKS.items():
            fit = solve_block_projection(prior, constraint_subs, public_scores, block_ids, target_names)
            projected = fit.expanded_prob
            for gamma in GAMMAS:
                pred = blend_probs(prior, projected, gamma)
                expected = expected_scores(pred, constraint_subs)
                tag = stable_tag(f"{prior_name}:{prior_file}:{mask_name}:{gamma:.4f}")
                file_name = f"submission_jepa_public_blockentropy_{prior_name}_{mask_name}_g{int(round(gamma*100)):03d}_{tag}.csv"
                out = sample[KEY].copy()
                out[TARGETS] = pred
                out.to_csv(OUT / file_name, index=False)
                saved.append(file_name)
                rec = {
                    "file": file_name,
                    "prior": prior_name,
                    "prior_file": prior_file,
                    "target_mask": mask_name,
                    "targets": ",".join(target_names),
                    "gamma": gamma,
                    "blocks": int(pd.Series(block_ids).nunique()),
                    "converged": fit.converged,
                    "iterations": fit.iterations,
                    "max_abs_constraint_residual_full_projection": float(np.max(np.abs(fit.residual))),
                    "mean_abs_move_vs_prior": float(np.mean(np.abs(pred - prior))),
                    "max_abs_move_vs_prior": float(np.max(np.abs(pred - prior))),
                }
                for name, score, target in zip(CONSTRAINT_FILES, expected, public_scores, strict=True):
                    rec[f"expected__{name}"] = float(score)
                    rec[f"target__{name}"] = float(target)
                    rec[f"residual__{name}"] = float(score - target)
                rows.append(rec)

    scores = pd.DataFrame(rows)
    scores.to_csv(OUT / "jepa_public_blockentropy_scores.csv", index=False)
    integ = integrity(saved, sample)
    integ.to_csv(OUT / "jepa_public_blockentropy_integrity.csv", index=False)
    proxy = public_proxy_scores(saved)
    proxy.to_csv(OUT / "jepa_public_blockentropy_proxy.csv", index=False)
    focused = focused_scenario_scores(saved)
    focused.to_csv(OUT / "jepa_public_blockentropy_focused_scenario.csv", index=False)

    shortlist = (
        scores.merge(proxy, on="file", how="left")
        .merge(focused, on="file", how="left")
        .merge(integ, on="file", how="left")
    )
    shortlist["known_public_constraint_mae"] = shortlist[
        [f"residual__{name}" for name in CONSTRAINT_FILES]
    ].abs().mean(axis=1)
    shortlist = shortlist.sort_values(
        ["posterior_expected_public_vs_anchor", "raw_axis_expected_public_vs_stage2", "focused_scenario_score"]
    ).reset_index(drop=True)
    shortlist.to_csv(OUT / "jepa_public_blockentropy_shortlist.csv", index=False)

    report = [
        "# JEPA Public Block Entropy Projection",
        "",
        "Sub-only experiment: use JEPA count/energy candidates as priors, solve observed public score constraints at hidden-block latent level, then apply a small gamma.",
        "",
        "## Top Posterior/Raw Proxy",
        "",
        "```csv",
        shortlist.head(24).round(10).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "jepa_public_blockentropy_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"saved={len(saved)}")
    cols = [
        "file",
        "prior",
        "target_mask",
        "gamma",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "focused_scenario_score",
        "mean_abs_move_vs_prior",
        "known_public_constraint_mae",
    ]
    print(shortlist[cols].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
