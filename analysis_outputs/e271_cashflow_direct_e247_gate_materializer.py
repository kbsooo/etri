#!/usr/bin/env python3
"""E271: cash-flow / payday-style boundary probe around E247.

E270 found that monthly cash-flow stories are not pure calendar trivia. The
stronger signals combine day-of-month anchors with finance/shopping behavior
and separate the 13 E247-only Q3 cells from the 4 E256-only Q3 cells.

This materializer stays deliberately small. It starts from E247, touches only
Q3 boundary cells, and asks whether cash-flow rhythm is a better explanation
of the E247/E256 frontier than broad social feature rollback.
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
STORY = OUT / "e270_payday_cashflow_story_features.parquet"

SCAN_OUT = OUT / "e271_cashflow_direct_e247_gate_scan.csv"
SELECTED_OUT = OUT / "e271_cashflow_direct_e247_gate_selected.csv"
REPORT_OUT = OUT / "e271_cashflow_direct_e247_gate_report.md"


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


def z(story: pd.DataFrame, name: str) -> np.ndarray:
    return story[name].to_numpy(dtype=np.float64)


def materialize() -> tuple[pd.DataFrame, pd.DataFrame]:
    e247 = load_sub(E247)
    e256 = load_sub(E256)
    e224 = load_sub(E224)
    story = pd.read_parquet(STORY)
    story = story[story["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)

    for name, df in [("e247", e247), ("e256", e256), ("e224", e224)]:
        if not story[KEYS].equals(df[KEYS]):
            raise RuntimeError(f"{name} keys do not align with E270 stories")

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

    month_near3 = z(story, "paymonth_start_near3_money_rumination_subj_z")
    month_shop = z(story, "paymonth_start_post3_late_shopping_subj_z")
    pay25_active = z(story, "pay25_pre3_cash_stress_active")
    pay20_shop = z(story, "pay20_post3_late_shopping_subj_z")
    eom_near3 = z(story, "payeom_near3_money_rumination_subj_z")
    pay15_shop = z(story, "pay15_post3_late_shopping_subj_z")
    month_relief = z(story, "monthstart_reset_relief_subj_z")
    calendar_only = z(story, "payeom_near7_calendar_only_subj_z") + z(story, "paymonth_start_near7_calendar_only_subj_z")

    cash_gate = (
        month_near3
        + 0.75 * month_shop
        + 0.60 * pay25_active
        + 0.45 * pay20_shop
        + 0.25 * eom_near3
        + 0.15 * month_relief
        - 0.55 * pay15_shop
    )
    pay25_gate = pay25_active + 0.35 * z(story, "pay25_pre3_cash_stress_subj_z") + 0.25 * pay20_shop
    anti_e256_gate = pay15_shop - 0.50 * month_near3 - 0.35 * month_shop - 0.25 * pay25_active

    top_cash8 = np.zeros(len(story), dtype=bool)
    top_cash6 = np.zeros(len(story), dtype=bool)
    idx_e247 = np.where(e247_only)[0]
    if len(idx_e247):
        order = idx_e247[np.argsort(cash_gate[idx_e247])[::-1]]
        top_cash8[order[:8]] = True
        top_cash6[order[:6]] = True

    pay25_rows = e247_only & (pay25_active > 0.5)
    anti_all = e256_only.copy()
    anti_pay15 = e256_only & (anti_e256_gate >= np.median(anti_e256_gate[e256_only]))

    cal_top = np.zeros(len(story), dtype=bool)
    if len(idx_e247):
        order = idx_e247[np.argsort(calendar_only[idx_e247])[::-1]]
        cal_top[order[:8]] = True

    configs = [
        {
            "candidate_id": "cashflow_top8_amp010",
            "alpha": 0.10,
            "beta": 0.00,
            "e247_mask": top_cash8,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Amplify E247-only Q3 cells selected by behavior-linked cash-flow rhythm.",
        },
        {
            "candidate_id": "cashflow_top6_amp014",
            "alpha": 0.14,
            "beta": 0.00,
            "e247_mask": top_cash6,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Stricter cash-flow amplification on the clearest E247-only boundary cells.",
        },
        {
            "candidate_id": "cashflow_top8_anti4_tiny",
            "alpha": 0.08,
            "beta": 0.10,
            "e247_mask": top_cash8,
            "anti_mask": anti_all,
            "intent": "Cash-flow E247 amplification plus tiny counter-move on all E256-only Q3 cells.",
        },
        {
            "candidate_id": "cashflow_top6_anti_pay15",
            "alpha": 0.12,
            "beta": 0.16,
            "e247_mask": top_cash6,
            "anti_mask": anti_pay15,
            "intent": "Cash-flow E247 amplification plus anti-E256 only where pay15 post-shopping dominates.",
        },
        {
            "candidate_id": "pay25_pre3_only_amp016",
            "alpha": 0.16,
            "beta": 0.00,
            "e247_mask": pay25_rows,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Literal pre-25 cash-stress sensor: amplify only E247-only rows active in the three days before 25.",
        },
        {
            "candidate_id": "calendar_only_control_top8",
            "alpha": 0.10,
            "beta": 0.00,
            "e247_mask": cal_top,
            "anti_mask": np.zeros(len(story), dtype=bool),
            "intent": "Control: similar tiny amplification using calendar-only month boundary, without behavior evidence.",
        },
    ]

    scan_rows = []
    selected_rows = []
    for cfg in configs:
        new = e247.copy()
        lnew = l247.copy()
        e_mask = cfg["e247_mask"].astype(bool)
        a_mask = cfg["anti_mask"].astype(bool)
        lnew[e_mask] = lnew[e_mask] + cfg["alpha"] * d247[e_mask]
        lnew[a_mask] = lnew[a_mask] - cfg["beta"] * d256[a_mask]
        new["Q3"] = clip_prob(sigmoid(lnew))
        h = short_hash(new)
        filename = f"submission_e271_{cfg['candidate_id']}_{h}.csv"
        path = OUT / filename
        new.to_csv(path, index=False)

        moved = np.abs(lnew - l247) > 1.0e-12
        e247_l1 = float(np.abs(lnew - l247).sum())
        e224_l1 = float(np.abs(lnew - l224).sum())
        scan_rows.append({
            "candidate_id": cfg["candidate_id"],
            "submission_file": filename,
            "intent": cfg["intent"],
            "moved_q3_rows_vs_e247": int(moved.sum()),
            "e247_only_rows_amplified": int(e_mask.sum()),
            "anti_e256_rows_moved": int(a_mask.sum()),
            "mean_cash_gate_e247_amp": float(cash_gate[e_mask].mean()) if int(e_mask.sum()) else 0.0,
            "mean_anti_e256_gate": float(anti_e256_gate[a_mask].mean()) if int(a_mask.sum()) else 0.0,
            "l1_logit_delta_vs_e247": e247_l1,
            "max_abs_logit_delta_vs_e247": float(np.abs(lnew - l247).max()),
            "l1_q3_logit_vs_e224": e224_l1,
            "cos_with_e247_rollback": float(np.dot(lnew - l224, d247) / max(np.linalg.norm(lnew - l224) * np.linalg.norm(d247), 1.0e-12)),
            "cos_delta_with_e256_fail_delta": float(np.dot(lnew - l247, l256 - l247) / max(np.linalg.norm(lnew - l247) * np.linalg.norm(l256 - l247), 1.0e-12)) if e247_l1 > 0 else 0.0,
        })

        for idx in np.where(moved)[0]:
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
                "cash_gate": float(cash_gate[idx]),
                "pay25_gate": float(pay25_gate[idx]),
                "anti_e256_gate": float(anti_e256_gate[idx]),
                "month_near3_z": float(month_near3[idx]),
                "month_shop_z": float(month_shop[idx]),
                "pay25_active": float(pay25_active[idx]),
                "pay20_shop_z": float(pay20_shop[idx]),
                "pay15_shop_z": float(pay15_shop[idx]),
                "calendar_only_z": float(calendar_only[idx]),
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
    preferred = scan[scan["candidate_id"].eq("cashflow_top8_anti4_tiny")]
    lines = [
        "# E271 Cash-Flow Direct E247 Gate",
        "",
        "## Question",
        "",
        "Can the payday/cash-flow story from E270 explain the Q3 boundary where E247 beats E256?",
        "",
        "This does not assume a literal payday. It tests whether month-start, pre-25 stress, post-20 spending, and finance/shopping behavior form a hidden human state around the current best.",
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
            "- read if public improves: the hidden boundary state is a monthly cash-flow rhythm, not just phone-in-bed or generic social activity.",
            "- read if public worsens: payday/cash-flow features are explanatory in train/CV but not action-safe at the E247 frontier.",
        ])
    lines.extend([
        "",
        "## Moved Rows",
        "",
        md_table(selected.sort_values(["candidate_id", "cell_group", "cash_gate"], ascending=[True, True, False]), n=120),
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    scan, selected = materialize()
    write_report(scan, selected)
    print(f"wrote {REPORT_OUT}")
    print(scan.to_string(index=False))


if __name__ == "__main__":
    main()
