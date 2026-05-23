#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cl_common import DATA_DIR, EXPERIMENT_DIR, LABELS, OUT_DIR, clip_prob, ensure_dirs, logloss, read_csv_rows


def load_folds() -> list[dict]:
    path = OUT_DIR / "validation" / "folds_chrono.json"
    return json.loads(path.read_text(encoding="utf-8"))["folds"]


def subject_prior(train_rows: list[dict[str, str]], label: str, alpha: float) -> tuple[float, dict[str, float]]:
    global_mean = sum(int(r[label]) for r in train_rows) / len(train_rows)
    by_subject: dict[str, list[int]] = defaultdict(list)
    for r in train_rows:
        by_subject[r["subject_id"]].append(int(r[label]))
    priors = {}
    for sid, vals in by_subject.items():
        priors[sid] = (sum(vals) + alpha * global_mean) / (len(vals) + alpha)
    return global_mean, priors


def evaluate_alpha(rows: list[dict[str, str]], fold: dict, alpha: float, clip: float) -> dict:
    valid_set = {(k["subject_id"], k["lifelog_date"]) for k in fold["valid_keys"]}
    train_rows = [r for r in rows if (r["subject_id"], r["lifelog_date"]) not in valid_set]
    valid_rows = [r for r in rows if (r["subject_id"], r["lifelog_date"]) in valid_set]

    target_scores = {}
    all_losses = []
    for y in LABELS:
        global_mean, priors = subject_prior(train_rows, y, alpha)
        preds = [clip_prob(priors.get(r["subject_id"], global_mean), clip, 1 - clip) for r in valid_rows]
        truth = [int(r[y]) for r in valid_rows]
        score = logloss(truth, preds)
        target_scores[y] = score
        all_losses.append(score)
    return {
        "fold_id": fold["fold_id"],
        "alpha": alpha,
        "clip": clip,
        "mean_logloss": sum(all_losses) / len(all_losses),
        "target_logloss": target_scores,
    }


def main() -> None:
    ensure_dirs()
    rows = read_csv_rows(DATA_DIR / "ch2026_metrics_train.csv")
    folds = load_folds()
    alphas = [0, 1, 3, 5, 10, 20, 50]
    clips = [0.0, 0.03, 0.05, 0.08]
    results = []
    for fold in folds:
        for alpha in alphas:
            for clip in clips:
                # alpha=0 is raw subject mean; global fallback only if missing subject.
                results.append(evaluate_alpha(rows, fold, alpha, clip))

    best = sorted(results, key=lambda x: x["mean_logloss"])[0]
    out_path = EXPERIMENT_DIR / "subject_prior_results.json"
    out_path.write_text(json.dumps({"best": best, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    csv_path = EXPERIMENT_DIR / "subject_prior_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["fold_id", "alpha", "clip", "mean_logloss"] + [f"logloss_{y}" for y in LABELS]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {"fold_id": r["fold_id"], "alpha": r["alpha"], "clip": r["clip"], "mean_logloss": r["mean_logloss"]}
            row.update({f"logloss_{y}": r["target_logloss"][y] for y in LABELS})
            writer.writerow(row)

    print("best", best)
    print(f"wrote {out_path}")
    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
