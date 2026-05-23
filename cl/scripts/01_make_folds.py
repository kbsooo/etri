#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, OUT_DIR, LABELS, ensure_dirs, read_csv_rows, write_json


def make_subject_chrono_fold(rows: list[dict[str, str]], valid_fraction: float) -> dict:
    train_keys: list[dict[str, str]] = []
    valid_keys: list[dict[str, str]] = []
    by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_subject[r["subject_id"]].append(r)

    subject_summary = {}
    for sid, sub_rows in sorted(by_subject.items()):
        sub_rows = sorted(sub_rows, key=lambda r: r["lifelog_date"])
        n = len(sub_rows)
        n_valid = max(1, round(n * valid_fraction))
        split = n - n_valid
        train_part = sub_rows[:split]
        valid_part = sub_rows[split:]
        for r in train_part:
            train_keys.append({"subject_id": r["subject_id"], "lifelog_date": r["lifelog_date"]})
        for r in valid_part:
            valid_keys.append({"subject_id": r["subject_id"], "lifelog_date": r["lifelog_date"]})
        subject_summary[sid] = {
            "n_total": n,
            "n_train": len(train_part),
            "n_valid": len(valid_part),
            "train_range": [train_part[0]["lifelog_date"], train_part[-1]["lifelog_date"]] if train_part else None,
            "valid_range": [valid_part[0]["lifelog_date"], valid_part[-1]["lifelog_date"]] if valid_part else None,
        }
    return {
        "valid_fraction": valid_fraction,
        "train_keys": train_keys,
        "valid_keys": valid_keys,
        "subject_summary": subject_summary,
    }


def target_means(rows: list[dict[str, str]]) -> dict[str, float]:
    return {y: sum(int(r[y]) for r in rows) / len(rows) for y in LABELS}


def main() -> None:
    ensure_dirs()
    rows = read_csv_rows(DATA_DIR / "ch2026_metrics_train.csv")
    folds = []
    for frac in [0.20, 0.25, 0.30]:
        fold = make_subject_chrono_fold(rows, frac)
        valid_set = {(k["subject_id"], k["lifelog_date"]) for k in fold["valid_keys"]}
        valid_rows = [r for r in rows if (r["subject_id"], r["lifelog_date"]) in valid_set]
        train_rows = [r for r in rows if (r["subject_id"], r["lifelog_date"]) not in valid_set]
        fold["fold_id"] = f"chrono_last_{int(frac * 100)}"
        fold["n_train"] = len(train_rows)
        fold["n_valid"] = len(valid_rows)
        fold["train_target_means"] = target_means(train_rows)
        fold["valid_target_means"] = target_means(valid_rows)
        folds.append(fold)

    out = {
        "description": "Subject-wise chronological folds. For each subject, the last fraction of dates is validation.",
        "labels": LABELS,
        "folds": folds,
    }
    write_json(OUT_DIR / "validation" / "folds_chrono.json", out)
    print(f"wrote {OUT_DIR / 'validation' / 'folds_chrono.json'}")
    for f in folds:
        print(f["fold_id"], "train", f["n_train"], "valid", f["n_valid"])


if __name__ == "__main__":
    main()
