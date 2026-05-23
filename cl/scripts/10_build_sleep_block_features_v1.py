#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ensure_dirs


def longest_run(flags: list[bool]) -> tuple[int, int, int]:
    best_len = cur_len = 0
    best_start = cur_start = -1
    for i, f in enumerate(flags):
        if f:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
        else:
            cur_len = 0
    return best_len, best_start, best_start + best_len - 1 if best_len else -1


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    rows = con.execute(f"""
        SELECT subject_id, lifelog_date, hour,
               COALESCE(screen_use_sum_h, 0) AS screen_sum,
               COALESCE(steps_sum_h, 0) AS steps_sum,
               COALESCE(mlight_mean_h, 0) AS mlight,
               COALESCE(wlight_mean_h, 0) AS wlight,
               COALESCE(activity_mean_h, 0) AS activity
        FROM read_parquet('{FEATURE_DIR / 'timebin_1h_features.parquet'}')
        WHERE hour BETWEEN 0 AND 5 OR hour BETWEEN 20 AND 23
        ORDER BY subject_id, lifelog_date, CASE WHEN hour >= 20 THEN hour - 20 ELSE hour + 4 END
    """).fetchall()
    by_day = defaultdict(list)
    for r in rows:
        by_day[(r[0], r[1])].append({"hour": int(r[2]), "screen": float(r[3]), "steps": float(r[4]), "mlight": float(r[5]), "wlight": float(r[6]), "activity": float(r[7])})

    out_csv = FEATURE_DIR / "sleep_block_features_v1.csv"
    out_parquet = FEATURE_DIR / "sleep_block_features_v1.parquet"
    fields = [
        "subject_id", "lifelog_date",
        "longest_quiet_run_h", "quiet_run_start_hour", "quiet_run_end_hour",
        "longest_screenoff_run_h", "screenoff_run_start_hour", "screenoff_run_end_hour",
        "sleep_block_fragmentation", "sleep_block_screen_interruptions", "sleep_block_step_interruptions",
        "late_screen_last_hour", "late_activity_last_hour", "dark_hours_count", "bright_interrupt_hours",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for (sid, date), seq in sorted(by_day.items()):
            # sequence order: 20,21,22,23,0,1,2,3,4,5 if present
            quiet = [(x["screen"] <= 0 and x["steps"] <= 0 and x["activity"] <= 1.0) for x in seq]
            screenoff = [(x["screen"] <= 0) for x in seq]
            q_len, q_s, q_e = longest_run(quiet)
            so_len, so_s, so_e = longest_run(screenoff)
            sleep_seg = seq[q_s:q_e+1] if q_len else []
            screen_interrupt = sum(1 for x in sleep_seg if x["screen"] > 0)
            step_interrupt = sum(1 for x in sleep_seg if x["steps"] > 0)
            frag = sum(1 for a, b in zip(quiet, quiet[1:]) if a != b)
            late_screen_hours = [x["hour"] for x in seq if (x["hour"] >= 20 or x["hour"] <= 2) and x["screen"] > 0]
            late_act_hours = [x["hour"] for x in seq if (x["hour"] >= 20 or x["hour"] <= 2) and (x["steps"] > 0 or x["activity"] > 1.0)]
            dark_hours = sum(1 for x in seq if x["mlight"] <= 10 and x["wlight"] <= 10)
            bright_interrupt = sum(1 for x in seq if (x["hour"] >= 21 or x["hour"] <= 5) and max(x["mlight"], x["wlight"]) >= 100)
            row = {
                "subject_id": sid, "lifelog_date": date,
                "longest_quiet_run_h": q_len,
                "quiet_run_start_hour": seq[q_s]["hour"] if q_len else None,
                "quiet_run_end_hour": seq[q_e]["hour"] if q_len else None,
                "longest_screenoff_run_h": so_len,
                "screenoff_run_start_hour": seq[so_s]["hour"] if so_len else None,
                "screenoff_run_end_hour": seq[so_e]["hour"] if so_len else None,
                "sleep_block_fragmentation": frag,
                "sleep_block_screen_interruptions": screen_interrupt,
                "sleep_block_step_interruptions": step_interrupt,
                "late_screen_last_hour": late_screen_hours[-1] if late_screen_hours else None,
                "late_activity_last_hour": late_act_hours[-1] if late_act_hours else None,
                "dark_hours_count": dark_hours,
                "bright_interrupt_hours": bright_interrupt,
            }
            w.writerow(row)
    con.execute(f"COPY (SELECT * FROM read_csv_auto('{out_csv}')) TO '{out_parquet}' (FORMAT PARQUET)")
    print(f"wrote {out_parquet} rows={len(by_day)} cols={len(fields)}")

if __name__ == "__main__":
    main()
