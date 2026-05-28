from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import broad_feature_addon_builder as b1
import presleep_multitarget_candidate_builder as pm


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = b1.TARGETS
KEY = b1.KEY
SUB_KEY = b1.SUB_KEY


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = b1.build_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base_oof = pm.clip(np.load(OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"))
    base_sub = pd.read_csv(
        OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        parse_dates=["sleep_date", "lifelog_date"],
    ).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sample[SUB_KEY])

    base_loss = pm.mean_loss(y, base_oof)
    rows = []
    target_rows = []
    saved_rows = []
    for combo in pm.combo_defs():
        pred = pm.apply_combo_oof(train_feat, base_oof, combo.ops)
        row = {
            "combo": combo.name,
            "note": combo.note,
            "ops": "; ".join(f"{x.target}:{x.feature}|{x.mode}|c{x.c_value:g}|w{x.weight:g}" for x in combo.ops),
            "base_loss": base_loss,
            "candidate_loss": pm.mean_loss(y, pred),
            "delta": pm.mean_loss(y, pred) - base_loss,
        }
        row.update(b1.geometry_summary(train_raw, sub_raw, train_feat, base_oof, combo.ops))
        rows.append(row)
        target_rows.extend(pm.summarize_targets(y, base_oof, pred, combo.name))
        if row["delta"] <= -0.002 and row["geometry_delta"] <= 0.0:
            prefix = f"anchor578_{combo.name}"
            np.save(OUT / f"final_{prefix}_oof.npy", pred)
            pd.DataFrame(pm.summarize_targets(y, base_oof, pred, combo.name)).to_csv(OUT / f"{prefix}_cv_estimate.csv", index=False)
            out = pm.apply_combo_submission(train_feat, sub_feat, base_oof, base_sub, combo.ops)
            assert out[SUB_KEY].equals(sample[SUB_KEY])
            assert out[TARGETS].isna().sum().sum() == 0
            assert out.duplicated(SUB_KEY).sum() == 0
            out.to_csv(OUT / f"submission_{prefix}.csv", index=False)
            saved_rows.append({"combo": combo.name, "file": f"submission_{prefix}.csv", "oof_file": f"final_{prefix}_oof.npy"})

    summary = pd.DataFrame(rows).sort_values(["candidate_loss", "geometry_delta"]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    saved_df = pd.DataFrame(saved_rows)
    summary.to_csv(OUT / "presleep_anchor_candidate_summary.csv", index=False)
    target_df.to_csv(OUT / "presleep_anchor_candidate_targets.csv", index=False)
    saved_df.to_csv(OUT / "presleep_anchor_saved_candidates.csv", index=False)
    print(summary.round(9).to_string(index=False))
    print(target_df.sort_values(["combo", "target"]).round(9).to_string(index=False))
    print(saved_df.to_string(index=False))


if __name__ == "__main__":
    main()
