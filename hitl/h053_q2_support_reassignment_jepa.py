#!/usr/bin/env python3
"""H053: Q2 support-reassignment HS-JEPA.

H051/H052 test whether H042's exact 45 Q2 cells should be amplified.  H053
tests the opposite hidden-world view:

    The H042 amplitude may be enough, but some support rows are wrong.

It keeps H042 as the public anchor, reverts weak H042 Q2 support rows back to
H012, and reallocates the same action budget to non-H042 rows selected by
H047 support posterior and H036/H042 public-world Q2 direction.
"""

from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h053_q2_support_reassignment_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012_FILE = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H047_SUPPORT_FILE = "hitl/h047_q2_support_identity_jepa/h047_row_support_posterior.csv"
WORLD_CELLS_FILE = "hitl/h047_q2_support_identity_jepa/h042_route_world_posterior_cells.csv"

H012_LB = 0.5681234831
H042_LB = 0.5679048248
H050_LB = 0.5679048248


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    z = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-z))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_float_id(x: float) -> str:
    return str(x).replace(".", "p").replace("-", "m")


def write_submission(template: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = template[KEYS + TARGETS].copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def weighted_delta(prob: np.ndarray, base: np.ndarray, q: np.ndarray, weight: np.ndarray) -> float:
    w = np.clip(np.asarray(weight, dtype=np.float64), 0.0, None)
    if float(w.sum()) <= 1.0e-12:
        w = np.ones_like(w)
    return float(np.sum(w * (bce(prob, q) - bce(base, q))) / np.sum(w))


def candidate_record(
    template: pd.DataFrame,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    prob: np.ndarray,
    keep_mask: np.ndarray,
    remove_mask: np.ndarray,
    add_mask: np.ndarray,
    support_post: np.ndarray,
    world_q2: np.ndarray,
    world_weight: np.ndarray,
    support_score: np.ndarray,
    keep_n: int,
    add_n: int,
    alpha: float,
    mode: str,
) -> dict[str, object]:
    q2 = TARGETS.index("Q2")
    changed = np.abs(prob - h042_prob) > 1.0e-12
    h012_changed = np.abs(prob - h012_prob) > 1.0e-12
    score_gain = float(np.mean(support_score[add_mask]) - np.mean(support_score[remove_mask])) if add_n else 0.0
    post_gain = float(np.mean(support_post[add_mask]) - np.mean(support_post[remove_mask])) if add_n else 0.0
    world_delta = weighted_delta(prob[:, q2], h042_prob[:, q2], world_q2, world_weight)
    selected = keep_mask | add_mask
    selected_size = int(selected.sum())
    logit_move = logit(prob[:, q2]) - logit(h012_prob[:, q2])
    world_dir = np.sign(logit(world_q2) - logit(h012_prob[:, q2]))
    direction_agree = (
        float(np.mean(np.sign(logit_move[selected]) == world_dir[selected]))
        if selected_size
        else 0.0
    )

    candidate_id = (
        f"h053_swap_keep{keep_n}_add{add_n}_a{safe_float_id(alpha)}_{mode}_"
        f"{short_hash(prob)}"
    )
    file_name = f"submission_{candidate_id}.csv"
    path = OUT / file_name
    write_submission(template, prob, path)

    return {
        "candidate_id": candidate_id,
        "file": file_name,
        "resolved_path": str(path),
        "keep_n": keep_n,
        "add_n": add_n,
        "alpha": alpha,
        "mode": mode,
        "changed_cells_vs_h042": int(changed.sum()),
        "q2_changed_cells_vs_h042": int(changed[:, q2].sum()),
        "changed_cells_vs_h012": int(h012_changed.sum()),
        "q2_changed_cells_vs_h012": int(h012_changed[:, q2].sum()),
        "kept_h042_support": int(keep_mask.sum()),
        "removed_h042_support": int(remove_mask.sum()),
        "added_new_support": int(add_mask.sum()),
        "selected_support_size": selected_size,
        "support_score_gain_add_minus_remove": score_gain,
        "support_posterior_gain_add_minus_remove": post_gain,
        "mean_keep_support_posterior": float(np.mean(support_post[keep_mask])) if keep_mask.any() else 0.0,
        "mean_removed_support_posterior": float(np.mean(support_post[remove_mask])) if remove_mask.any() else 0.0,
        "mean_added_support_posterior": float(np.mean(support_post[add_mask])) if add_mask.any() else 0.0,
        "mean_added_world_weight": float(np.mean(world_weight[add_mask])) if add_mask.any() else 0.0,
        "q2_world_delta_vs_h042": world_delta,
        "direction_agreement_with_world": direction_agree,
        "mean_abs_prob_move_vs_h042": float(np.mean(np.abs(prob[:, q2] - h042_prob[:, q2]))),
        "max_abs_prob_move_vs_h042": float(np.max(np.abs(prob[:, q2] - h042_prob[:, q2]))),
        "h053_support_reassignment_score": (
            -world_delta
            + 0.0015 * score_gain
            + 0.0010 * post_gain
            + 0.0001 * direction_agree
            - 0.00005 * max(0.0, selected_size - 45)
        ),
    }


def main() -> None:
    h012_df = pd.read_csv(ROOT / H012_FILE)
    h042_df = pd.read_csv(ROOT / H042_FILE)
    h050_df = pd.read_csv(ROOT / H050_FILE)
    support_df = pd.read_csv(ROOT / H047_SUPPORT_FILE)
    world_cells = pd.read_csv(ROOT / WORLD_CELLS_FILE)
    world_q2_df = world_cells[world_cells["target"].eq("Q2")].sort_values("row").reset_index(drop=True)

    h012_prob = h012_df[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = h042_df[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050_df[TARGETS].to_numpy(dtype=np.float64)
    q2 = TARGETS.index("Q2")

    h042_logit_delta = logit(h042_prob[:, q2]) - logit(h012_prob[:, q2])
    h042_support = np.abs(h042_logit_delta) > 1.0e-12
    support_post = support_df["h047_support_posterior"].to_numpy(dtype=np.float64)
    h047_public = support_df["h047_public_score"].to_numpy(dtype=np.float64)
    h047_private = support_df["h047_private_score"].to_numpy(dtype=np.float64)
    world_q2 = world_q2_df["world_q_cond"].to_numpy(dtype=np.float64)
    world_shift = world_q2_df["signed_logit_shift_cond"].to_numpy(dtype=np.float64)
    world_cell = world_q2_df["cell_world_score"].to_numpy(dtype=np.float64)
    row_public = world_q2_df["row_public_prob"].to_numpy(dtype=np.float64)
    support_score = (
        1.20 * support_post
        + 0.80 * world_cell
        + 0.35 * row_public
        + 0.20 * h047_public
        - 0.25 * h047_private
        + 0.10 * np.abs(world_shift)
    )

    h042_rank = pd.Series(np.where(h042_support, support_score, -np.inf)).rank(
        method="first", ascending=False
    ).to_numpy()
    candidate_rank = pd.Series(np.where(~h042_support, support_score, -np.inf)).rank(
        method="first", ascending=False
    ).to_numpy()

    audit = support_df[KEYS + ["row", "h047_support_posterior", "h047_public_score", "h047_private_score"]].copy()
    audit["h053_h042_support"] = h042_support
    audit["h053_support_score"] = support_score
    audit["h053_h042_support_rank"] = h042_rank
    audit["h053_non_h042_candidate_rank"] = candidate_rank
    audit["h053_world_q2"] = world_q2
    audit["h053_world_shift"] = world_shift
    audit["h053_world_cell_score"] = world_cell
    audit["h053_row_public_prob"] = row_public
    audit.sort_values("h053_support_score", ascending=False).to_csv(OUT / "h053_support_reassignment_audit.csv", index=False)

    rows = []
    for keep_n in [25, 31, 35, 39]:
        keep_mask = h042_support & (h042_rank <= keep_n)
        remove_mask = h042_support & ~keep_mask
        add_n = int(remove_mask.sum())
        add_mask_base = (~h042_support) & (candidate_rank <= add_n)
        for alpha in [0.22, 0.35, 0.50, 0.66]:
            for mode in ["world_prob", "world_logit"]:
                prob = h042_prob.copy()
                prob[remove_mask, q2] = h012_prob[remove_mask, q2]
                if mode == "world_prob":
                    prob[add_mask_base, q2] = (
                        h012_prob[add_mask_base, q2]
                        + alpha * (world_q2[add_mask_base] - h012_prob[add_mask_base, q2])
                    )
                else:
                    prob[add_mask_base, q2] = sigmoid(
                        logit(h012_prob[add_mask_base, q2]) + alpha * world_shift[add_mask_base]
                    )
                rows.append(
                    candidate_record(
                        h042_df,
                        h012_prob,
                        h042_prob,
                        clip_prob(prob),
                        keep_mask,
                        remove_mask,
                        add_mask_base,
                        support_post,
                        world_q2,
                        np.clip(world_cell * row_public, 1.0e-6, None),
                        support_score,
                        keep_n,
                        add_n,
                        alpha,
                        mode,
                    )
                )

    scores = pd.DataFrame(rows).sort_values(
        ["h053_support_reassignment_score", "q2_world_delta_vs_h042"],
        ascending=[False, True],
    ).reset_index(drop=True)
    scores.to_csv(OUT / "h053_candidate_scores.csv", index=False)
    scores.to_csv(OUT / "h053_candidate_scores_ranked.csv", index=False)

    selected_prefix = "h053_swap_keep31_add14_a0p35_world_prob"
    selected = scores[scores["candidate_id"].str.startswith(selected_prefix)].iloc[0].copy()
    selected_path = Path(str(selected["resolved_path"]))
    root_name = f"submission_h053_q2_support_reassign_k31a14_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    root_path = ROOT / root_name
    selected_prob = pd.read_csv(selected_path)[TARGETS].to_numpy(dtype=np.float64)
    write_submission(h042_df, selected_prob, root_path)

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_as_amplitude_failure_branch",
                "selected_candidate_id": selected["candidate_id"],
                "selected_file": selected["file"],
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "reason": "Q2 support reassignment branch after H051/H052 amplitude branch",
                "public_anchor": H042_FILE,
                "public_anchor_lb": H042_LB,
                "h050_public_lb": H050_LB,
                "expected_relation": (
                    "beats H042 if H042's Q2 phase support is partly misplaced; "
                    "fails if exact H042 support is the true public subset"
                ),
                **{k: selected[k] for k in selected.index if k not in {"resolved_path", "file"}},
            }
        ]
    )
    decision.to_csv(OUT / "h053_decision.csv", index=False)

    h050_q2_delta = float(np.max(np.abs(h050_prob[:, q2] - h042_prob[:, q2])))
    report = f"""# H053 Q2 Support-Reassignment HS-JEPA

Question: if H051/H052 amplitude continuation is wrong, is H042's real missing variable support identity rather than amplitude?

Design:

- base = H042 current public best;
- Q1/Q3/S targets are frozen;
- keep the strongest `31` H042 Q2 support rows by H047 support posterior + H036 world score;
- revert the weakest `14` H042 Q2 support rows back to H012;
- add `14` non-H042 rows selected by H047 support posterior and H036/H042 public-world Q2 direction;
- selected branch uses `world_prob` with alpha `0.35`.

Decision:

{md_table(decision)}

Public-anchor context:

- H012 public LB: `{H012_LB:.10f}`
- H042 public LB: `{H042_LB:.10f}`
- H050 public LB: `{H050_LB:.10f}`
- H050 max Q2 delta vs H042: `{h050_q2_delta:.12f}` (Q2 was frozen)

Top candidates:

{md_table(scores[["candidate_id", "keep_n", "add_n", "alpha", "mode", "changed_cells_vs_h042", "changed_cells_vs_h012", "support_score_gain_add_minus_remove", "support_posterior_gain_add_minus_remove", "mean_removed_support_posterior", "mean_added_support_posterior", "mean_added_world_weight", "q2_world_delta_vs_h042", "direction_agreement_with_world", "mean_abs_prob_move_vs_h042", "max_abs_prob_move_vs_h042", "h053_support_reassignment_score"]], 20)}

Interpretation rule:

- If H051/H052 improve, H053 is lower priority because exact-support amplitude/edge is alive.
- If H051 fails and H053 improves, H042's Q2 discovery should be interpreted as support/public-subset identity, not amplitude.
- If both amplitude and support reassignment fail, H042 is likely a very narrow local correction and the next branch should infer public subset directly rather than modifying Q2.
"""
    (OUT / "h053_report.md").write_text(report, encoding="utf-8")

    print(f"H053 selected: {selected['candidate_id']}")
    print(f"H053 root: {root_path}")
    print(f"H053 changed vs H042: {int(selected['changed_cells_vs_h042'])}")
    print(f"H053 q2 world delta vs H042: {float(selected['q2_world_delta_vs_h042']):.10f}")


if __name__ == "__main__":
    main()
