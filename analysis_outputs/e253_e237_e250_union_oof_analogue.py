#!/usr/bin/env python3
"""E253: OOF analogue for the E237/E250 union sensor.

E252's weakness is provenance: the union of E237 and E250 Q3 cells passed
submission-side materialization stress, but the union was not itself produced by
a single OOF policy. This script reconstructs the two parent OOF bad-cell
scores and audits parent, intersection, difference, and union amplitudes on
train OOF labels.

No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402
import e249_feature_nn1_decisive_oof_audit as e249  # noqa: E402


SUMMARY_OUT = OUT / "e253_e237_e250_union_oof_analogue_summary.csv"
REPORT_OUT = OUT / "e253_e237_e250_union_oof_analogue_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def binary_drop(amp: np.ndarray) -> np.ndarray:
    return np.asarray(amp, dtype=np.float64) < 0.05


def amp_from_drop(drop: np.ndarray) -> np.ndarray:
    return np.where(np.asarray(drop, dtype=bool), 0.0, 1.0).astype(np.float64)


def parent_oof(
    train_df: pd.DataFrame,
    feats: dict[str, list[str]],
    spec: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    model = e237.model_defs()[str(spec["model"])]
    bad_prob, eval_label, _ = e237.oof_bad_predict(
        model,
        train_df,
        feats[str(spec["view"])],
        str(spec["source_scope"]),
        str(spec["split"]),
        str(spec["target_kind"]),
        float(spec["tail_q"]),
    )
    amp = e237.policy_amplitudes(train_df, bad_prob)[str(spec["policy"])]
    return bad_prob, eval_label, amp


def evaluate_variant(
    train_df: pd.DataFrame,
    name: str,
    amp: np.ndarray,
    score: np.ndarray,
    eval_label: np.ndarray,
    eval_label_e237: np.ndarray,
    eval_label_e250: np.ndarray,
    p237: np.ndarray,
    p250: np.ndarray,
    drop237: np.ndarray,
    drop250: np.ndarray,
    source_type: str,
) -> dict[str, Any]:
    rec = e237.evaluate_oof_policy(
        train_df,
        {
            "source_scope": "all3",
            "view": "e237_e250_oof_union",
            "model": "mixed_hgb_shallow",
            "split": "mixed_subject5_row5",
            "target_kind": "risk",
            "tail_q": 0.10,
        },
        score,
        eval_label,
        amp,
        name,
    )
    drop = binary_drop(amp)
    active_q3 = train_df["task_name"].eq("q3_e224").to_numpy()
    dropped_q3 = drop & active_q3
    rec.update(
        {
            "candidate_id": name,
            "source_type": source_type,
            "q3_rows": int(dropped_q3.sum()),
            "overlap_e237": int(np.sum(dropped_q3 & drop237 & active_q3)),
            "overlap_e250": int(np.sum(dropped_q3 & drop250 & active_q3)),
            "e237_only_cells_in_candidate": int(np.sum(dropped_q3 & drop237 & ~drop250 & active_q3)),
            "e250_only_cells_in_candidate": int(np.sum(dropped_q3 & ~drop237 & drop250 & active_q3)),
            "shared_cells_in_candidate": int(np.sum(dropped_q3 & drop237 & drop250 & active_q3)),
            "tail_auc_vs_e237_label_max": e237.safe_auc(eval_label_e237[active_q3], np.maximum(p237, p250)[active_q3]),
            "tail_auc_vs_e250_label_max": e237.safe_auc(eval_label_e250[active_q3], np.maximum(p237, p250)[active_q3]),
            "tail_auc_vs_e237_label_avg": e237.safe_auc(eval_label_e237[active_q3], ((p237 + p250) / 2.0)[active_q3]),
            "tail_auc_vs_e250_label_avg": e237.safe_auc(eval_label_e250[active_q3], ((p237 + p250) / 2.0)[active_q3]),
        }
    )
    return rec


def main() -> None:
    train_aug, _, feats, _ = e249.build_augmented_frames()
    train_df = train_aug[train_aug["task_name"].isin(e237.CONTROL_TASKS)].reset_index(drop=True)

    spec237 = {
        "source_scope": "all3",
        "view": "latent_no_targetid",
        "model": "hgb_shallow",
        "split": "subject5",
        "target_kind": "risk",
        "tail_q": 0.10,
        "policy": "drop_q3_top25",
    }
    spec250 = {
        "source_scope": "all3",
        "view": "latent_no_targetid_featnn1",
        "model": "hgb_shallow",
        "split": "row5",
        "target_kind": "risk",
        "tail_q": 0.10,
        "policy": "drop_q3_top21",
    }
    p237, y237, amp237 = parent_oof(train_df, feats, spec237)
    p250, y250, amp250 = parent_oof(train_df, feats, spec250)
    d237 = binary_drop(amp237)
    d250 = binary_drop(amp250)
    active_q3 = train_df["task_name"].eq("q3_e224").to_numpy()

    variants = [
        ("e237_parent", d237, p237, y237, "known_e237_oof"),
        ("e250_parent", d250, p250, y250, "known_e250_oof"),
        ("shared_intersection", d237 & d250, np.minimum(p237, p250), y237, "overlap"),
        ("union_e237_e250", d237 | d250, np.maximum(p237, p250), y237, "union"),
        ("e237_only", d237 & ~d250, p237, y237, "difference"),
        ("e250_only", ~d237 & d250, p250, y250, "difference"),
        ("symmetric_difference", d237 ^ d250, np.maximum(p237, p250), y237, "difference"),
    ]
    rows = [
        evaluate_variant(
            train_df,
            name,
            amp_from_drop(drop),
            score,
            label,
            y237,
            y250,
            p237,
            p250,
            d237,
            d250,
            source_type,
        )
        for name, drop, score, label, source_type in variants
    ]
    summary = pd.DataFrame(rows).sort_values(["stress_promote", "loss_vs_full"], ascending=[False, True])
    summary.to_csv(SUMMARY_OUT, index=False)

    e237_row = summary[summary["candidate_id"].eq("e237_parent")].iloc[0]
    e250_row = summary[summary["candidate_id"].eq("e250_parent")].iloc[0]
    union_row = summary[summary["candidate_id"].eq("union_e237_e250")].iloc[0]
    best_parent = min(float(e237_row["loss_vs_full"]), float(e250_row["loss_vs_full"]))
    union_delta_vs_best_parent = float(union_row["loss_vs_full"]) - best_parent
    cols = [
        "candidate_id",
        "source_type",
        "q3_rows",
        "overlap_e237",
        "overlap_e250",
        "shared_cells_in_candidate",
        "e237_only_cells_in_candidate",
        "e250_only_cells_in_candidate",
        "loss_vs_full",
        "active_policy_delta",
        "active_full_delta",
        "q3_policy_delta",
        "q3_full_delta",
        "subject_win_rate",
        "dropped_mean_benefit",
        "tail_auc",
        "tail_auc_vs_e237_label_max",
        "tail_auc_vs_e250_label_max",
        "stress_promote",
    ]
    lines = [
        "# E253 E237/E250 Union OOF Analogue",
        "",
        "## Question",
        "",
        "Does the E252 union have train-OOF support, or is it only a submission-side materialization artifact?",
        "",
        "## Headline",
        "",
        f"- E237 parent OOF loss_vs_full: `{float(e237_row['loss_vs_full']):.9f}`.",
        f"- E250 parent OOF loss_vs_full: `{float(e250_row['loss_vs_full']):.9f}`.",
        f"- Union OOF loss_vs_full: `{float(union_row['loss_vs_full']):.9f}`.",
        f"- Union minus best parent: `{union_delta_vs_best_parent:.9f}`.",
        f"- Union stress_promote: `{bool(union_row['stress_promote'])}`.",
        f"- Train Q3 overlap: E237 `{int(d237[active_q3].sum())}`, E250 `{int(d250[active_q3].sum())}`, shared `{int((d237 & d250 & active_q3).sum())}`, union `{int(((d237 | d250) & active_q3).sum())}`.",
        "",
        "## OOF Variants",
        "",
        md_table(summary, cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if bool(union_row["stress_promote"]) and union_delta_vs_best_parent <= -1.0e-5:
        lines.append(
            "- E252 gains OOF provenance: union is better than both parents on train OOF. Promote E252 above E250 and consider it a stronger complementarity candidate, while still keeping public feedback decoding fixed."
        )
    elif bool(union_row["stress_promote"]):
        lines.append(
            "- E252 has weak OOF support: union is stress-promoted but does not beat the best parent. Keep it as a complementarity sensor, not as the likely-score leader."
        )
    else:
        lines.append(
            "- E252 does not have OOF support. Materialization anatomy alone is insufficient; keep E237 first and demote E252 to diagnostic unless public feedback says otherwise."
        )
    lines.append("- Public LB is not used and no submission is created.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("[E253 summary]")
    print(summary[cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
