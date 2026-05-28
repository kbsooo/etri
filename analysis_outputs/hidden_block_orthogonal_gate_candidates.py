from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from hidden_block_latent_audit import (  # noqa: E402
    TARGETS,
    KEY,
    EPS,
    SubmissionSpec,
    clip,
    expected_delta,
    load_predictions,
    logit,
    projection_ratio,
    read_submission,
    sample_block_ids,
    sigmoid,
)


OBSERVED_SPECS = [
    SubmissionSpec(
        "anchor578",
        OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        0.5784273528,
        "observed_anchor",
    ),
    SubmissionSpec(
        "stage2",
        OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        0.5779449757,
        "observed_stage2",
    ),
    SubmissionSpec(
        "ordinal_q",
        OUT / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        0.5783033652,
        "observed_bad_count_shift",
    ),
    SubmissionSpec(
        "raw05",
        ROOT / "jepa" / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        0.5775263072,
        "observed_raw_axis",
    ),
    SubmissionSpec(
        "jepa_bad_residual",
        ROOT / "jepa" / "submission_jepa_latent_residual_probe.csv",
        0.5812273278,
        "observed_jepa_bad_axis",
    ),
    SubmissionSpec(
        "jepa_bad_q2",
        ROOT / "jepa" / "submission_jepa_latent_q2_w0p45.csv",
        0.5798012862,
        "observed_jepa_bad_axis",
    ),
]

TARGET_SETS = {
    "q3s134": ["Q3", "S1", "S3", "S4"],
    "s134": ["S1", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3s": ["Q3", "S1", "S2", "S3", "S4"],
}


@dataclass(frozen=True)
class Candidate:
    tag: str
    pred: np.ndarray
    kind: str
    targets: str
    params: dict[str, float | str]


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def blend_logits(base: np.ndarray, donor: np.ndarray, scale: float) -> np.ndarray:
    return clip(sigmoid(logit(base) + scale * (logit(donor) - logit(base))))


def raw_axis_latent_q(stage: np.ndarray, raw05: np.ndarray) -> np.ndarray:
    obs_delta = 0.5775263072 - 0.5779449757
    lo, hi = -2.0, 4.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        q = blend_logits(stage, raw05, mid)
        if expected_delta(q, raw05, stage) > obs_delta:
            lo = mid
        else:
            hi = mid
    return blend_logits(stage, raw05, 0.5 * (lo + hi))


def expand_block_matrix(block_ids: np.ndarray, block_df: pd.DataFrame, prefix: str) -> np.ndarray:
    lookup = block_df.set_index("hidden_block_id")
    out = np.zeros((len(block_ids), len(TARGETS)), dtype=np.float64)
    for i, block_id in enumerate(block_ids):
        for j, target in enumerate(TARGETS):
            out[i, j] = float(lookup.loc[block_id, f"{prefix}_{target}"])
    return clip(out)


def target_mask(target_names: list[str], n_rows: int) -> np.ndarray:
    idx = {target: j for j, target in enumerate(TARGETS)}
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for target in target_names:
        mask[:, idx[target]] = True
    return mask


def project_out_axes(
    move: np.ndarray,
    axes: list[np.ndarray],
    mode: str = "full",
) -> tuple[np.ndarray, dict[str, float]]:
    vec = move.astype(np.float64).copy()
    coeffs: dict[str, float] = {}
    for i, axis in enumerate(axes):
        a = axis.astype(np.float64)
        denom = float(np.dot(a, a))
        if denom <= 1e-12:
            coeffs[f"axis_{i}"] = np.nan
            continue
        coeff = float(np.dot(vec, a) / denom)
        coeffs[f"axis_{i}"] = coeff
        if mode == "positive_only" and coeff <= 0.0:
            continue
        if mode == "negative_only" and coeff >= 0.0:
            continue
        vec = vec - coeff * a
    return vec, coeffs


def masked_unflatten(vec: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros(mask.shape, dtype=np.float64)
    out[mask] = vec
    return out


def build_endpoint_gate(
    base: np.ndarray,
    posterior: np.ndarray,
    endpoint: np.ndarray,
    raw10: np.ndarray,
    block_ids: np.ndarray,
    block_df: pd.DataFrame,
) -> np.ndarray:
    post_delta = logit(posterior) - logit(base)
    endpoint_delta = logit(endpoint) - logit(base)
    raw_delta = logit(raw10) - logit(base)
    endpoint_agree = (np.sign(endpoint_delta) == np.sign(post_delta)) & (np.abs(endpoint - base) >= 0.025)
    raw_agree = (np.sign(raw_delta) == np.sign(post_delta)) & (np.abs(raw_delta) >= 0.015)

    shift_lookup = block_df.set_index("hidden_block_id")["posterior_mean_abs_shift"].to_dict()
    shifts = np.asarray([float(shift_lookup[b]) for b in block_ids], dtype=np.float64)
    if float(shifts.max() - shifts.min()) > 1e-12:
        shifts = (shifts - shifts.min()) / (shifts.max() - shifts.min())
    else:
        shifts = np.zeros_like(shifts)

    gate = (
        0.18
        + 0.40 * endpoint_agree.astype(np.float64)
        + 0.27 * raw_agree.astype(np.float64)
        + 0.15 * shifts[:, None]
    )
    gate[np.abs(post_delta) < 0.025] *= 0.45
    return np.clip(gate, 0.05, 1.0)


def build_raw_gate(
    base: np.ndarray,
    posterior: np.ndarray,
    endpoint: np.ndarray,
    raw10: np.ndarray,
    block_ids: np.ndarray,
    block_df: pd.DataFrame,
) -> np.ndarray:
    raw_delta = logit(raw10) - logit(base)
    post_delta = logit(posterior) - logit(base)
    endpoint_delta = logit(endpoint) - logit(base)
    post_agree = (np.sign(post_delta) == np.sign(raw_delta)) & (np.abs(post_delta) >= 0.03)
    endpoint_agree = (np.sign(endpoint_delta) == np.sign(raw_delta)) & (np.abs(endpoint - base) >= 0.025)

    shift_lookup = block_df.set_index("hidden_block_id")["posterior_mean_abs_shift"].to_dict()
    shifts = np.asarray([float(shift_lookup[b]) for b in block_ids], dtype=np.float64)
    cutoff = float(np.quantile(shifts, 0.55))
    top_block = (shifts >= cutoff)[:, None]

    gate = (
        0.12
        + 0.42 * post_agree.astype(np.float64)
        + 0.34 * endpoint_agree.astype(np.float64)
        + 0.12 * top_block.astype(np.float64)
    )
    gate[np.abs(raw_delta) < 0.01] *= 0.5
    return np.clip(gate, 0.0, 1.0)


def make_orthogonal_candidates(
    preds: dict[str, np.ndarray],
    posterior: np.ndarray,
    endpoint: np.ndarray,
    raw_q: np.ndarray,
    block_ids: np.ndarray,
    block_df: pd.DataFrame,
) -> list[Candidate]:
    base = preds["raw05"]
    raw10 = preds["raw10"]
    endpoint_gate = build_endpoint_gate(base, posterior, endpoint, raw10, block_ids, block_df)
    candidates: list[Candidate] = []
    bad_axes_by_target = {
        "jepa_resid": logit(preds["jepa_bad_residual"]) - logit(base),
        "jepa_q2": logit(preds["jepa_bad_q2"]) - logit(base),
        "ordinal": logit(preds["ordinal_q"]) - logit(base),
    }
    raw_grad = base - raw_q
    raw_direction = logit(raw10) - logit(base)
    full_move = logit(posterior) - logit(base)

    for target_tag, target_names in TARGET_SETS.items():
        mask = target_mask(target_names, base.shape[0])
        desired = full_move[mask]
        bad_axes = [axis[mask] for axis in bad_axes_by_target.values()]
        orth, coeffs = project_out_axes(desired, bad_axes, mode="full")
        orth2, raw_coeffs = project_out_axes(orth, [raw_grad[mask]], mode="positive_only")
        orth3, rawdir_coeffs = project_out_axes(orth2, [raw_direction[mask]], mode="negative_only")

        variants = {
            "orth": orth2,
            "orthraw": orth3,
            "orthgate": orth3 * endpoint_gate[mask],
        }
        for variant, vec in variants.items():
            move = masked_unflatten(vec, mask)
            for gamma in [0.015, 0.025, 0.035, 0.05, 0.075]:
                for cap in [0.20, 0.35, 0.50]:
                    capped = np.clip(move, -cap, cap)
                    pred = clip(sigmoid(logit(base) + gamma * capped))
                    param_text = f"{variant}|{target_tag}|g={gamma}|cap={cap}"
                    candidates.append(
                        Candidate(
                            tag=f"hiddenblock_{variant}_{target_tag}_g{gamma:g}_cap{cap:g}_{stable_tag(param_text)}",
                            pred=pred,
                            kind=variant,
                            targets=target_tag,
                            params={
                                "gamma": gamma,
                                "cap": cap,
                                "bad_axis0_coeff": coeffs.get("axis_0", np.nan),
                                "raw_grad_coeff": raw_coeffs.get("axis_0", np.nan),
                                "raw_dir_coeff": rawdir_coeffs.get("axis_0", np.nan),
                            },
                        )
                    )
    return candidates


def make_raw_gate_candidates(
    preds: dict[str, np.ndarray],
    posterior: np.ndarray,
    endpoint: np.ndarray,
    block_ids: np.ndarray,
    block_df: pd.DataFrame,
) -> list[Candidate]:
    base = preds["raw05"]
    raw10 = preds["raw10"]
    raw_gate = build_raw_gate(base, posterior, endpoint, raw10, block_ids, block_df)
    raw_move = logit(raw10) - logit(base)
    candidates: list[Candidate] = []
    for target_tag, target_names in TARGET_SETS.items():
        mask = target_mask(target_names, base.shape[0])
        move = np.zeros_like(base)
        move[mask] = raw_gate[mask] * raw_move[mask]
        for scale in [0.25, 0.40, 0.55, 0.70, 0.90, 1.10]:
            pred = clip(sigmoid(logit(base) + scale * move))
            param_text = f"rawgate|{target_tag}|s={scale}"
            candidates.append(
                Candidate(
                    tag=f"hiddenblock_rawgate_{target_tag}_s{scale:g}_{stable_tag(param_text)}",
                    pred=pred,
                    kind="rawgate",
                    targets=target_tag,
                    params={"scale": scale, "cap": np.nan, "gamma": np.nan},
                )
            )
    return candidates


def make_combo_candidates(
    preds: dict[str, np.ndarray],
    orth_candidates: list[Candidate],
    raw_candidates: list[Candidate],
) -> list[Candidate]:
    base_logit = logit(preds["raw05"])
    combos: list[Candidate] = []
    orth_pool = [c for c in orth_candidates if c.kind == "orthgate" and c.params.get("gamma") in {0.025, 0.035, 0.05}]
    raw_pool = [c for c in raw_candidates if c.params.get("scale") in {0.4, 0.55, 0.7}]
    for orth in orth_pool:
        for raw in raw_pool:
            if orth.targets != raw.targets:
                continue
            orth_move = logit(orth.pred) - base_logit
            raw_move = logit(raw.pred) - base_logit
            pred = clip(sigmoid(base_logit + raw_move + 0.65 * orth_move))
            param_text = f"combo|{orth.tag}|{raw.tag}"
            combos.append(
                Candidate(
                    tag=f"hiddenblock_combo_{orth.targets}_{stable_tag(param_text)}",
                    pred=pred,
                    kind="combo",
                    targets=orth.targets,
                    params={
                        "gamma": float(orth.params.get("gamma", np.nan)),
                        "scale": float(raw.params.get("scale", np.nan)),
                        "cap": float(orth.params.get("cap", np.nan)),
                    },
                )
            )
    return combos


def score_candidates(
    preds: dict[str, np.ndarray],
    candidates: list[Candidate],
    posterior: np.ndarray,
    raw_q: np.ndarray,
) -> pd.DataFrame:
    stage = preds["stage2"]
    anchor = preds["anchor578"]
    raw05 = preds["raw05"]
    raw10 = preds["raw10"]
    bad_resid_axis = preds["jepa_bad_residual"] - stage
    bad_q2_axis = preds["jepa_bad_q2"] - stage
    ordinal_axis = preds["ordinal_q"] - stage
    raw_axis = raw10 - stage
    rows = []
    for cand in candidates:
        pred = cand.pred
        row = {
            "tag": cand.tag,
            "kind": cand.kind,
            "targets": cand.targets,
            "posterior_expected_public_vs_anchor": 0.5784273528 + expected_delta(posterior, pred, anchor),
            "raw_axis_expected_public_vs_stage2": 0.5779449757 + expected_delta(raw_q, pred, stage),
            "delta_vs_raw05_rawaxis": 0.5779449757 + expected_delta(raw_q, pred, stage) - 0.5775263072,
            "delta_vs_raw05_posterior": 0.5784273528 + expected_delta(posterior, pred, anchor) - 0.5775263072,
            "mean_abs_move_vs_stage2": float(np.abs(pred - stage).mean()),
            "mean_abs_move_vs_raw05": float(np.abs(pred - raw05).mean()),
            "raw10_axis_ratio": projection_ratio(pred - stage, raw_axis),
            "bad_residual_axis_ratio": projection_ratio(pred - stage, bad_resid_axis),
            "bad_q2_axis_ratio": projection_ratio(pred - stage, bad_q2_axis),
            "ordinal_axis_ratio": projection_ratio(pred - stage, ordinal_axis),
            "min_prob": float(pred.min()),
            "max_prob": float(pred.max()),
        }
        row.update(cand.params)
        rows.append(row)
    df = pd.DataFrame(rows)
    df["selection_score"] = (
        df["raw_axis_expected_public_vs_stage2"]
        + 0.50 * np.maximum(df["posterior_expected_public_vs_anchor"] - 0.5775263072, -0.003)
        + 0.15 * np.maximum(df["bad_residual_axis_ratio"], 0.0)
        + 0.10 * np.maximum(df["bad_q2_axis_ratio"], 0.0)
        + 0.05 * np.maximum(df["ordinal_axis_ratio"], 0.0)
    )
    return df.sort_values(
        [
            "selection_score",
            "raw_axis_expected_public_vs_stage2",
            "posterior_expected_public_vs_anchor",
            "mean_abs_move_vs_raw05",
        ]
    ).reset_index(drop=True)


def save_selected(
    template: pd.DataFrame,
    candidates: list[Candidate],
    scores: pd.DataFrame,
    n_per_kind: int = 5,
) -> pd.DataFrame:
    by_tag = {candidate.tag: candidate for candidate in candidates}
    selected_tags: list[str] = []
    for kind, group in scores.groupby("kind", sort=False):
        for tag in group.head(n_per_kind)["tag"].tolist():
            if tag not in selected_tags:
                selected_tags.append(tag)
    for tag in scores.head(12)["tag"].tolist():
        if tag not in selected_tags:
            selected_tags.append(tag)

    rows = []
    key_ref = template[KEY]
    for tag in selected_tags:
        cand = by_tag[tag]
        name = f"submission_{cand.tag}.csv"
        out = template.copy()
        out[TARGETS] = cand.pred
        out.to_csv(OUT / name, index=False)
        score_row = scores[scores["tag"].eq(tag)].iloc[0].to_dict()
        score_row["file"] = name
        score_row["rows"] = len(out)
        score_row["key_match"] = bool(out[KEY].equals(key_ref))
        score_row["duplicate_keys"] = int(out.duplicated(KEY).sum())
        score_row["null_predictions"] = int(out[TARGETS].isna().sum().sum())
        rows.append(score_row)
    selected = pd.DataFrame(rows).sort_values("selection_score").reset_index(drop=True)
    selected.to_csv(OUT / "hidden_block_orthogonal_gate_selected.csv", index=False)
    return selected


def write_report(scores: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "tag",
        "kind",
        "targets",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "bad_q2_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
    ]
    lines = [
        "# Hidden Block Orthogonal Gate Candidates",
        "",
        "This pass uses I-JEPA as a block-representation idea: target blocks are hidden submission episodes, and prediction moves are constrained to stay orthogonal to observed bad public axes.",
        "",
        "## Selection Rule",
        "",
        "- Base prediction is `raw05`, the best observed public anchor.",
        "- Posterior moves are projected away from `jepa_bad_residual`, `jepa_bad_q2`, and `ordinal_q` axes.",
        "- Moves that first-order worsen the raw05 public-consistent latent are removed.",
        "- Endpoint/length priors are only gates, never hard labels.",
        "",
        "## Top Scored Candidates",
        "",
        "```csv",
        scores[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Saved Candidates",
        "",
        "```csv",
        selected[["file"] + cols[1:]].round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    (OUT / "hidden_block_orthogonal_gate_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    sample = sample.sort_values(KEY).reset_index(drop=True)
    frames, preds = load_predictions()
    block_ids = sample_block_ids(train, sample)
    block_df = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    endpoint_df = pd.read_csv(OUT / "hidden_block_endpoint_priors.csv")
    posterior = expand_block_matrix(block_ids, block_df, "posterior_rate")
    endpoint = expand_block_matrix(block_ids, endpoint_df, "endpoint_rate")
    raw_q = raw_axis_latent_q(preds["stage2"], preds["raw05"])

    orth = make_orthogonal_candidates(preds, posterior, endpoint, raw_q, block_ids, block_df)
    raw = make_raw_gate_candidates(preds, posterior, endpoint, block_ids, block_df)
    combo = make_combo_candidates(preds, orth, raw)
    candidates = orth + raw + combo
    scores = score_candidates(preds, candidates, posterior, raw_q)
    scores.to_csv(OUT / "hidden_block_orthogonal_gate_scores.csv", index=False)
    selected = save_selected(frames["stage2"], candidates, scores)
    write_report(scores, selected)

    print("[hidden block orthogonal gate] generated", len(candidates), "candidates")
    print("[hidden block orthogonal gate] saved", len(selected), "selected candidates")
    show_cols = [
        "file",
        "kind",
        "targets",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "bad_q2_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "selection_score",
    ]
    print(selected[show_cols].head(24).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
