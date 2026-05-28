from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import public_universe_minimax_optimizer as pum  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY
EPS = hbr.EPS


@dataclass(frozen=True)
class Candidate:
    file: str
    public_base: str
    structural: str
    weight: float
    pred: np.ndarray


def clip(x: np.ndarray | float) -> np.ndarray:
    return hbr.clip(x)


def logit(x: np.ndarray | float) -> np.ndarray:
    return hbr.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return hbr.sigmoid(x)


def stable_tag(text: str) -> str:
    return hbr.stable_tag(text)


def read_sub(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        raise FileNotFoundError(file_name)
    return pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def public_base_files() -> list[str]:
    files: list[str] = []
    for table, n in [
        ("public_minimax_ensemble_selected.csv", 4),
        ("public_universe_minimax_selected.csv", 8),
        ("public_mask_plausibility_reweight_summary.csv", 6),
        ("public_posterior_scenario_robustness_summary.csv", 8),
    ]:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        for f in df["file"].head(n).tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    for f in [
        "submission_public_minimaxens_r05_a10_h506746.csv",
        "submission_public_universeens_u65_r04_dc6f3303.csv",
        "submission_public_maskaware_t80_r11_544844af.csv",
        "submission_public_consfront_t80_r10_b06ca82f.csv",
    ]:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    return files


def structural_files() -> list[str]:
    files: list[str] = []
    for table, n in [
        ("block_scale_jepa_axis_submission_shortlist.csv", 10),
        ("block_scale_jepa_submission_shortlist.csv", 6),
        ("hidden_block_sequence_motif_shortlist.csv", 8),
        ("hidden_block_rateprobe_shortlist.csv", 6),
    ]:
        path = OUT / table
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        for f in df["file"].head(n).tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    for f in [
        "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
        "submission_hiddenblock_rateprobe_neutral_605de284.csv",
        "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    ]:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    return files


def ce_row_loss(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return (-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))).mean(axis=1)


def score_candidate(
    pred: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    weights_by_profile: dict[str, np.ndarray],
) -> dict[str, float]:
    parts = [mask_mat @ ce_row_loss(q, pred) for q in q_scenarios]
    scores = np.concatenate(parts)
    regret = scores - best_scores
    delta_prior = scores - prior_scores
    out: dict[str, float] = {
        "mean_expected": float(np.mean(scores)),
        "mean_regret": float(np.mean(regret)),
        "p90_regret": float(np.quantile(regret, 0.90)),
        "p95_regret": float(np.quantile(regret, 0.95)),
        "max_regret": float(np.max(regret)),
        "mean_delta_vs_prior": float(np.mean(delta_prior)),
        "win_rate_vs_prior": float(np.mean(delta_prior < 0.0)),
    }
    out["robust_score"] = (
        out["mean_expected"]
        + 1.75 * out["mean_regret"]
        + 0.85 * out["p90_regret"]
        + 0.25 * out["p95_regret"]
        + 0.04 * out["max_regret"]
        + 0.10 * max(float(np.quantile(delta_prior, 0.90)), 0.0)
    )
    for profile, w in weights_by_profile.items():
        out[f"{profile}_expected"] = float(np.sum(w * scores))
        out[f"{profile}_regret"] = float(np.sum(w * regret))
        out[f"{profile}_delta_vs_prior"] = float(np.sum(w * delta_prior))
    return out


def build_reference_scores(
    reference_preds: list[np.ndarray],
    q_scenarios: list[np.ndarray],
    prior_pred: np.ndarray,
    mask_mat: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    best_parts = []
    prior_parts = []
    for q in q_scenarios:
        ref = []
        for pred in reference_preds:
            ref.append(mask_mat @ ce_row_loss(q, pred))
        best_parts.append(np.vstack(ref).min(axis=0))
        prior_parts.append(mask_mat @ ce_row_loss(q, prior_pred))
    return np.concatenate(best_parts), np.concatenate(prior_parts)


def blend_logits(public_pred: np.ndarray, structural_pred: np.ndarray, weight: float) -> np.ndarray:
    return clip(sigmoid((1.0 - weight) * logit(public_pred) + weight * logit(structural_pred)))


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    mask_mat = pum.normalized_mask_matrix(sample, max_masks=768)
    q_files, q_groups = pum.scenario_files()
    q_scenarios = [pum.load_sub(f)[TARGETS].to_numpy(dtype=float) for f in q_files]
    weights_by_profile = {
        name: pum.scenario_weights(q_groups, profile, mask_mat.shape[0])
        for name, profile in pum.PROFILES.items()
    }

    public_files = public_base_files()
    struct_files = structural_files()
    public_frames = {f: read_sub(f) for f in public_files}
    struct_frames = {f: read_sub(f) for f in struct_files}
    key_ref = sample[KEY].reset_index(drop=True)
    for f, frame in {**public_frames, **struct_frames}.items():
        if not frame[KEY].equals(key_ref):
            raise ValueError(f"key mismatch: {f}")

    public_preds = {f: frame[TARGETS].to_numpy(dtype=np.float64) for f, frame in public_frames.items()}
    struct_preds = {f: frame[TARGETS].to_numpy(dtype=np.float64) for f, frame in struct_frames.items()}
    reference_files = list(dict.fromkeys(public_files + struct_files))
    reference_preds = [read_sub(f)[TARGETS].to_numpy(dtype=np.float64) for f in reference_files]
    prior_pred = pum.load_sub(pum.BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float)
    best_scores, prior_scores = build_reference_scores(reference_preds, q_scenarios, prior_pred, mask_mat)

    rows = []
    candidates: dict[str, Candidate] = {}
    for pub_file, pub_pred in public_preds.items():
        for struct_file, struct_pred in struct_preds.items():
            for weight in [0.01, 0.02, 0.035, 0.05, 0.075, 0.10, 0.15, 0.20]:
                pred = blend_logits(pub_pred, struct_pred, weight)
                score = score_candidate(pred, q_scenarios, mask_mat, best_scores, prior_scores, weights_by_profile)
                tag = stable_tag(f"{pub_file}|{struct_file}|{weight}")
                wtag = str(weight).replace(".", "p")
                file_name = f"submission_blockscale_jepa_publicblend_w{wtag}_{tag}.csv"
                rec = {
                    "file": file_name,
                    "public_base": pub_file,
                    "structural": struct_file,
                    "weight": weight,
                    **score,
                    "mean_abs_move_vs_public": float(np.abs(pred - pub_pred).mean()),
                    "mean_abs_move_vs_structural": float(np.abs(pred - struct_pred).mean()),
                    "min_prob": float(pred.min()),
                    "max_prob": float(pred.max()),
                }
                rows.append(rec)
                candidates[file_name] = Candidate(file_name, pub_file, struct_file, weight, pred)

    scan = pd.DataFrame(rows).sort_values(["robust_score", "mean_expected", "mean_regret"]).reset_index(drop=True)
    scan.to_csv(OUT / "block_scale_jepa_public_blend_scan.csv", index=False)

    # Keep two families: public-robust near-best and structural-injection probes with tiny movement.
    top_public = scan.head(80)
    tiny = scan[(scan["mean_abs_move_vs_public"] <= 0.0015) & (scan["weight"] <= 0.05)].head(80)
    selected = pd.concat([top_public, tiny], ignore_index=True).drop_duplicates("file").head(60).reset_index(drop=True)

    saved_rows = []
    for rec in selected.itertuples(index=False):
        cand = candidates[rec.file]
        out = sample[KEY].copy()
        out[TARGETS] = cand.pred
        out.to_csv(OUT / cand.file, index=False)
        row = rec._asdict()
        row["rows"] = len(out)
        row["key_ok"] = bool(out[KEY].equals(key_ref))
        row["duplicate_keys"] = int(out.duplicated(KEY).sum())
        row["null_probs"] = int(out[TARGETS].isna().sum().sum())
        saved_rows.append(row)
    saved = pd.DataFrame(saved_rows)
    saved.to_csv(OUT / "block_scale_jepa_public_blend_selected.csv", index=False)

    proxy = hbr.public_proxy_scores(saved["file"].tolist())
    proxy.to_csv(OUT / "block_scale_jepa_public_blend_proxy.csv", index=False)

    merged = saved.merge(proxy, on="file", how="left", suffixes=("", "_axis"))
    merged["combined_rank_score"] = (
        merged["robust_score"].rank(method="average")
        + merged["raw_axis_expected_public_vs_stage2"].rank(method="average")
        + 0.5 * merged["posterior_expected_public_vs_anchor"].rank(method="average")
    )
    shortlist = merged.sort_values(["combined_rank_score", "robust_score"]).reset_index(drop=True)
    shortlist.to_csv(OUT / "block_scale_jepa_public_blend_shortlist.csv", index=False)

    lines = [
        "# Block-Scale JEPA Public Blend",
        "",
        "Submission-level logit blends between public-inverse/minimax candidates and structural JEPA hidden-block candidates.",
        "",
        "## Inputs",
        "",
        f"- public bases: {len(public_files)}",
        f"- structural candidates: {len(struct_files)}",
        f"- scenario files: {len(q_files)}",
        f"- sampled masks: {mask_mat.shape[0]}",
        "",
        "## Shortlist",
        "",
        "```csv",
        shortlist[
            [
                "file",
                "public_base",
                "structural",
                "weight",
                "robust_score",
                "mean_expected",
                "mean_regret",
                "posterior_expected_public_vs_anchor",
                "raw_axis_expected_public_vs_stage2",
                "delta_vs_raw05_rawaxis",
                "mean_abs_move_vs_public",
            ]
        ].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        saved[["file", "rows", "key_ok", "duplicate_keys", "null_probs", "min_prob", "max_prob"]].round(8).to_csv(index=False).strip(),
        "```",
    ]
    (OUT / "block_scale_jepa_public_blend_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("[public blend] public", len(public_files), "structural", len(struct_files), "scan", len(scan), "saved", len(saved))
    print(shortlist.head(24)[[
        "file",
        "public_base",
        "structural",
        "weight",
        "robust_score",
        "mean_expected",
        "mean_regret",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "mean_abs_move_vs_public",
    ]].round(10).to_string(index=False))
    bad = saved[(~saved["key_ok"]) | (saved["duplicate_keys"] > 0) | (saved["null_probs"] > 0)]
    print("\n[integrity]", "ok" if bad.empty else bad[["file", "key_ok", "duplicate_keys", "null_probs"]].to_string(index=False))


if __name__ == "__main__":
    main()
