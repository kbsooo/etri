"""Build three validation fold families that *together* approximate the
actual public+private split:

  1. chrono_tail_v2          — per subject, last 20/25/30% of dates as valid (forecast regime)
  2. interleaved_hole_v1     — per subject, random 25% of dates from the middle 50% as valid
                                with both train neighbors guaranteed (hole-filling regime)
  3. subject_mirror_v1       — per subject, valid composed of ~`inside_s` middle hole rows
                                + ~`after_s` tail rows, matching the actual test inside/after
                                ratio measured directly from the submission sample

Each family writes a JSON identical in shape to outputs/validation/folds_chrono.json:
    {"description":..., "labels":[Q1..S4], "folds":[{"name":..., "train_keys":[{subject_id,lifelog_date}], "valid_keys":[...]}, ...]}

No labels are touched. No submission generated. Diagnostic-only.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, ensure_dirs  # noqa: E402

OUT_DIR = ROOT / "outputs" / "validation"
TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
TEST_CSV = ROOT / "data" / "ch2026_submission_sample.csv"


def load_keys() -> tuple[pd.DataFrame, pd.DataFrame]:
    tr = pd.read_csv(TRAIN_CSV)
    te = pd.read_csv(TEST_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    te["lifelog_date"] = pd.to_datetime(te["lifelog_date"]).dt.date.astype(str)
    return tr, te


def to_records(df: pd.DataFrame) -> list[dict]:
    return df[["subject_id", "lifelog_date"]].to_dict("records")


def measure_test_inside_after(tr: pd.DataFrame, te: pd.DataFrame) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for s in sorted(tr["subject_id"].unique()):
        a = pd.to_datetime(tr[tr["subject_id"] == s]["lifelog_date"])
        b = pd.to_datetime(te[te["subject_id"] == s]["lifelog_date"])
        inside = int(((b >= a.min()) & (b <= a.max())).sum())
        after = int((b > a.max()).sum())
        counts[s] = {"inside": inside, "after": after, "test_total": int(len(b))}
    return counts


def build_chrono_tail(tr: pd.DataFrame, fractions: list[float]) -> dict:
    folds = []
    tr_sorted = tr.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for frac in fractions:
        train_keys, valid_keys = [], []
        for s, g in tr_sorted.groupby("subject_id"):
            n = len(g)
            n_valid = max(1, int(round(n * frac)))
            split = n - n_valid
            train_keys.extend(to_records(g.iloc[:split]))
            valid_keys.extend(to_records(g.iloc[split:]))
        folds.append(
            {
                "name": f"chrono_tail_last_{int(frac*100)}",
                "valid_fraction": frac,
                "train_keys": train_keys,
                "valid_keys": valid_keys,
                "n_train": len(train_keys),
                "n_valid": len(valid_keys),
            }
        )
    return {
        "description": "Per-subject chronological tail. Forecast regime only. Mirrors current folds_chrono.json.",
        "labels": LABELS,
        "folds": folds,
    }


def build_interleaved_hole(tr: pd.DataFrame, seeds: list[int], hole_frac: float = 0.25) -> dict:
    """Per subject: pick valid indices from the middle 50% of the chronological
    list, sampling ~`hole_frac` of all the subject's rows. Both train neighbors
    exist by construction (we never pick the first/last index)."""
    folds = []
    tr_sorted = tr.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for seed in seeds:
        rng = random.Random(seed)
        train_keys, valid_keys = [], []
        for s, g in tr_sorted.groupby("subject_id"):
            n = len(g)
            n_valid = max(1, int(round(n * hole_frac)))
            lo = max(1, int(n * 0.25))
            hi = min(n - 1, int(n * 0.75))
            candidates = list(range(lo, hi))
            if len(candidates) < n_valid:
                # subject too short; fall back to "any middle index"
                candidates = list(range(1, n - 1))
            valid_idx = set(rng.sample(candidates, min(n_valid, len(candidates))))
            for i in range(n):
                rec = {"subject_id": s, "lifelog_date": str(g.iloc[i]["lifelog_date"])}
                if i in valid_idx:
                    valid_keys.append(rec)
                else:
                    train_keys.append(rec)
        folds.append(
            {
                "name": f"hole_v1_seed{seed}",
                "valid_fraction": hole_frac,
                "seed": seed,
                "train_keys": train_keys,
                "valid_keys": valid_keys,
                "n_train": len(train_keys),
                "n_valid": len(valid_keys),
            }
        )
    return {
        "description": (
            "Per-subject middle-50%-window random holes. Hole-filling regime. "
            "Both immediate train neighbors are guaranteed to exist."
        ),
        "labels": LABELS,
        "folds": folds,
    }


def build_subject_mirror(
    tr: pd.DataFrame, te: pd.DataFrame, seeds: list[int]
) -> dict:
    """Per subject: build a valid set with (~inside_s, ~after_s) composition,
    matching the actual test split mix. The 'after' part is the chronological
    tail of that subject's train rows; the 'inside' part is a random hole from
    the middle. Sizes scale down by 0.5 to avoid eating more than half of train.
    """
    counts = measure_test_inside_after(tr, te)
    folds = []
    tr_sorted = tr.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for seed in seeds:
        rng = random.Random(seed)
        train_keys, valid_keys = [], []
        per_subject_audit = {}
        for s, g in tr_sorted.groupby("subject_id"):
            n = len(g)
            inside_target = counts[s]["inside"]
            after_target = counts[s]["after"]
            # scale so we never take more than ~45% of subject rows as valid
            scale = min(1.0, 0.45 * n / max(1, inside_target + after_target))
            n_after = max(0, int(round(after_target * scale)))
            n_inside = max(0, int(round(inside_target * scale)))
            # tail block as 'after'
            after_idx = set(range(n - n_after, n)) if n_after > 0 else set()
            # inside hole from middle 50%, excluding tail
            lo = max(1, int(n * 0.25))
            hi = min(n - n_after, int(n * 0.75))
            candidates = [i for i in range(lo, hi) if i not in after_idx]
            if len(candidates) < n_inside:
                candidates = [i for i in range(1, n - n_after) if i not in after_idx]
            inside_idx = set(rng.sample(candidates, min(n_inside, len(candidates))))
            valid_idx = after_idx | inside_idx
            per_subject_audit[s] = {
                "n": n,
                "n_after": n_after,
                "n_inside": n_inside,
                "target_inside": inside_target,
                "target_after": after_target,
            }
            for i in range(n):
                rec = {"subject_id": s, "lifelog_date": str(g.iloc[i]["lifelog_date"])}
                (valid_keys if i in valid_idx else train_keys).append(rec)
        folds.append(
            {
                "name": f"mirror_v1_seed{seed}",
                "seed": seed,
                "train_keys": train_keys,
                "valid_keys": valid_keys,
                "n_train": len(train_keys),
                "n_valid": len(valid_keys),
                "per_subject": per_subject_audit,
            }
        )
    return {
        "description": (
            "Per-subject valid composed of a chronological tail block + a "
            "middle-window random hole, sized to mirror the actual test "
            "inside/after ratio measured from ch2026_submission_sample.csv."
        ),
        "labels": LABELS,
        "test_inside_after_per_subject": counts,
        "folds": folds,
    }


def main():
    ensure_dirs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tr, te = load_keys()
    counts = measure_test_inside_after(tr, te)
    inside_total = sum(c["inside"] for c in counts.values())
    after_total = sum(c["after"] for c in counts.values())
    print(f"test composition measured: inside={inside_total}  after={after_total}  total={inside_total+after_total}")

    chrono = build_chrono_tail(tr, [0.20, 0.25, 0.30])
    hole = build_interleaved_hole(tr, seeds=[0, 1, 2], hole_frac=0.25)
    mirror = build_subject_mirror(tr, te, seeds=[0, 1, 2])

    (OUT_DIR / "folds_chrono_tail_v2.json").write_text(json.dumps(chrono, indent=2))
    (OUT_DIR / "folds_interleaved_hole_v1.json").write_text(json.dumps(hole, indent=2))
    (OUT_DIR / "folds_subject_mirror_v1.json").write_text(json.dumps(mirror, indent=2))

    for fam in (chrono, hole, mirror):
        print(f"\n--- {fam['description'][:80]}")
        for f in fam["folds"]:
            print(f"  {f['name']}: train={f['n_train']}  valid={f['n_valid']}")


if __name__ == "__main__":
    main()
