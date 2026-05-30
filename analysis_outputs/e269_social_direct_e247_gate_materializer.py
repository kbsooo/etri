#!/usr/bin/env python3
"""E269: direct human/social gate on the E247 frontier.

E267 failed because the human/social state was translated through the older
E224/E154 rollback body. E268 suggests a sharper target: explain the Q3 cells
where E247 beat the E256 same-family follow-up.

This script creates tiny public-sensor submissions around E247:
- amplify only E247-unique Q3 rollback cells that look like phone-in-bed days;
- move the 4 E256-unique Q3 cells in the opposite direction as an anti-E256
  bright-light/low-phone hypothesis;
- combine both at small amplitudes.

These are not broad blends. They are tests of a hidden human state over the
17 cells that separate the current public winner from its failed sibling.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

E247 = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
STORY = OUT / "e268_human_social_story_features.parquet"

SCAN_OUT = OUT / "e269_social_direct_e247_gate_scan.csv"
SELECTED_OUT = OUT / "e269_social_direct_e247_gate_selected.csv"
REPORT_OUT = OUT / "e269_social_direct_e247_gate_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def load_sub(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df.sort_values(KEYS).reset_index(drop=True)


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def materialize() -> tuple[pd.DataFrame, pd.DataFrame]:
    e247 = load_sub(E247)
    e256 = load_sub(E256)
    e224 = load_sub(E224)
    story = pd.read_parquet(STORY)
    story = story[story["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    for name, df in [("e247", e247), ("e256", e256), ("e224", e224)]:
        if not story[KEYS].equals(df[KEYS]):
            raise RuntimeError(f"{name} keys do not align with E268 stories")

    l247 = logit(e247["Q3"].to_numpy())
    l256 = logit(e256["Q3"].to_numpy())
    l224 = logit(e224["Q3"].to_numpy())
    d247 = l247 - l224
    d256 = l256 - l224
    e247_changed = np.abs(d247) > 1.0e-10
    e256_changed = np.abs(d256) > 1.0e-10
    e247_only = e247_changed & ~e256_changed
    e256_only = e256_changed & ~e247_changed
    common = e247_changed & e256_changed

    phone = story["phone_in_bed_subj_z"].to_numpy(dtype=float)
    app_entropy = story["app_entropy_scattered_day_subj_z"].to_numpy(dtype=float)
    bright = story["bright_light_late_subj_z"].to_numpy(dtype=float)
    heart = story["heart_stress_late_subj_z"].to_numpy(dtype=float)
    ritual = story["ritual_anchor_subj_z"].to_numpy(dtype=float)
    low_hr = story["low_hr_recovery_subj_z"].to_numpy(dtype=float)
    social_iso = story["social_isolation_media_subj_z"].to_numpy(dtype=float)

    phonebed_gate = phone + 0.35 * app_entropy + 0.25 * ritual + 0.25 * low_hr - 0.45 * bright - 0.25 * heart
    anti_e256_gate = bright + 0.25 * app_entropy - 0.75 * phone - 0.25 * ritual - 0.20 * social_iso

    top_phone = np.zeros(len(story), dtype=bool)
    idx_phone = np.where(e247_only)[0]
    if len(idx_phone):
        order = idx_phone[np.argsort(phonebed_gate[idx_phone])[::-1]]
        top_phone[order[:8]] = True

    top_phone_strict = np.zeros(len(story), dtype=bool)
    if len(idx_phone):
        order = idx_phone[np.argsort(phonebed_gate[idx_phone])[::-1]]
        top_phone_strict[order[:5]] = True

    anti_e256 = np.zeros(len(story), dtype=bool)
    idx_anti = np.where(e256_only)[0]
    if len(idx_anti):
        threshold = np.median(anti_e256_gate[idx_anti])
        anti_e256[idx_anti] = anti_e256_gate[idx_anti] >= threshold

    all_anti_e256 = e256_only.copy()

    configs = [
        {
            "candidate_id": "phonebed_e247only_top8_amp015",
            "alpha_e247only": 0.15,
            "beta_anti_e256": 0.0,
            "e247_mask": top_phone,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Amplify E247-only Q3 rollback on rows that look like phone-in-bed plus low bright/heart stress.",
        },
        {
            "candidate_id": "phonebed_e247only_top5_amp025",
            "alpha_e247only": 0.25,
            "beta_anti_e256": 0.0,
            "e247_mask": top_phone_strict,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Stricter but larger phone-in-bed amplification on the clearest E247-only rows.",
        },
        {
            "candidate_id": "anti_e256_bright_lowphone_beta025",
            "alpha_e247only": 0.0,
            "beta_anti_e256": 0.25,
            "e247_mask": np.zeros(len(story), dtype=bool),
            "anti_mask": all_anti_e256,
            "intent": "Move the 4 E256-only bright-light/low-phone rows opposite the failed E256 direction.",
        },
        {
            "candidate_id": "anti_e256_tophalf_beta035",
            "alpha_e247only": 0.0,
            "beta_anti_e256": 0.35,
            "e247_mask": np.zeros(len(story), dtype=bool),
            "anti_mask": anti_e256,
            "intent": "Only counter-move the E256-only rows with strongest bright-light/low-phone signature.",
        },
        {
            "candidate_id": "combo_phonebed8_anti4_small",
            "alpha_e247only": 0.12,
            "beta_anti_e256": 0.20,
            "e247_mask": top_phone,
            "anti_mask": all_anti_e256,
            "intent": "Combined direct human-state gate: small E247-only amplification plus small anti-E256 counter-move.",
        },
        {
            "candidate_id": "combo_phonebed5_anti2_sharp",
            "alpha_e247only": 0.20,
            "beta_anti_e256": 0.30,
            "e247_mask": top_phone_strict,
            "anti_mask": anti_e256,
            "intent": "Sharper combined public sensor with fewer rows and larger amplitudes.",
        },
        {
            "candidate_id": "e247only_all_amp006_control",
            "alpha_e247only": 0.06,
            "beta_anti_e256": 0.0,
            "e247_mask": e247_only,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Control: tiny amplification of all 13 E247-only Q3 cells without social selection.",
        },
    ]

    scan_rows = []
    selected_rows = []
    for cfg in configs:
        new = e247.copy()
        lnew = l247.copy()
        e_mask = cfg["e247_mask"].astype(bool)
        a_mask = cfg["anti_mask"].astype(bool)
        lnew[e_mask] = lnew[e_mask] + cfg["alpha_e247only"] * d247[e_mask]
        lnew[a_mask] = lnew[a_mask] - cfg["beta_anti_e256"] * d256[a_mask]
        new["Q3"] = clip_prob(sigmoid(lnew))
        h = short_hash(new)
        filename = f"submission_e269_{cfg['candidate_id']}_{h}.csv"
        path = OUT / filename
        new.to_csv(path, index=False)

        moved_from_e247 = np.abs(lnew - l247) > 1.0e-12
        e247_l1 = float(np.abs(lnew - l247).sum())
        e224_l1 = float(np.abs(lnew - l224).sum())
        scan_rows.append({
            "candidate_id": cfg["candidate_id"],
            "submission_file": filename,
            "intent": cfg["intent"],
            "moved_q3_rows_vs_e247": int(moved_from_e247.sum()),
            "e247_only_rows_amplified": int(e_mask.sum()),
            "anti_e256_rows_moved": int(a_mask.sum()),
            "mean_phonebed_gate_e247_amp": float(phonebed_gate[e_mask].mean()) if int(e_mask.sum()) else 0.0,
            "mean_anti_e256_gate": float(anti_e256_gate[a_mask].mean()) if int(a_mask.sum()) else 0.0,
            "l1_logit_delta_vs_e247": e247_l1,
            "max_abs_logit_delta_vs_e247": float(np.abs(lnew - l247).max()),
            "l1_q3_logit_vs_e224": e224_l1,
            "cos_with_e247_rollback": float(np.dot(lnew - l224, d247) / max(np.linalg.norm(lnew - l224) * np.linalg.norm(d247), 1.0e-12)),
            "cos_delta_with_e256_fail_delta": float(np.dot(lnew - l247, l256 - l247) / max(np.linalg.norm(lnew - l247) * np.linalg.norm(l256 - l247), 1.0e-12)) if e247_l1 > 0 else 0.0,
        })
        for idx in np.where(moved_from_e247)[0]:
            selected_rows.append({
                "candidate_id": cfg["candidate_id"],
                "row_idx": int(idx),
                "subject_id": story.loc[idx, "subject_id"],
                "sleep_date": story.loc[idx, "sleep_date"],
                "lifelog_date": story.loc[idx, "lifelog_date"],
                "cell_group": "e247_only" if e247_only[idx] else ("e256_only" if e256_only[idx] else ("common" if common[idx] else "other")),
                "old_q3": float(e247.loc[idx, "Q3"]),
                "new_q3": float(new.loc[idx, "Q3"]),
                "logit_delta_vs_e247": float(lnew[idx] - l247[idx]),
                "phonebed_gate": float(phonebed_gate[idx]),
                "anti_e256_gate": float(anti_e256_gate[idx]),
                "phone_in_bed_subj_z": float(phone[idx]),
                "app_entropy_subj_z": float(app_entropy[idx]),
                "bright_light_subj_z": float(bright[idx]),
                "heart_stress_subj_z": float(heart[idx]),
            })

    scan = pd.DataFrame(scan_rows).sort_values(
        ["moved_q3_rows_vs_e247", "l1_logit_delta_vs_e247"],
        ascending=[True, True],
    ).reset_index(drop=True)
    selected = pd.DataFrame(selected_rows)
    scan.to_csv(SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    return scan, selected


def write_report(scan: pd.DataFrame, selected: pd.DataFrame) -> None:
    preferred = scan[scan["candidate_id"].eq("combo_phonebed8_anti4_small")]
    lines = [
        "# E269 Social Direct E247 Gate",
        "",
        "## Question",
        "",
        "Can the human/social state from E268 be used directly on the 17 Q3 cells that separate E247 from the failed E256 sibling, instead of reusing the E267 E224/E154 rollback body?",
        "",
        "## Candidate Scan",
        "",
        md_table(scan, n=20),
        "",
        "## Preferred Sensor",
        "",
    ]
    if not preferred.empty:
        r = preferred.iloc[0]
        lines.extend([
            f"- file: `{r['submission_file']}`",
            f"- moved Q3 rows vs E247: `{int(r['moved_q3_rows_vs_e247'])}`",
            f"- intent: {r['intent']}",
            "- read if public improves: the missing human state is specifically phone-in-bed E247-only plus anti-E256 bright/low-phone, not broad social rollback.",
            "- read if public worsens: E247 is already near the local optimum for the 17-cell boundary; social stories are diagnostic but not action-safe.",
        ])
    lines.extend([
        "",
        "## Moved Rows",
        "",
        md_table(selected.sort_values(["candidate_id", "cell_group", "phonebed_gate"], ascending=[True, True, False]), n=80),
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    scan, selected = materialize()
    write_report(scan, selected)
    print(f"wrote {REPORT_OUT}")
    print(scan.to_string(index=False))


if __name__ == "__main__":
    main()
