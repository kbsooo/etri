from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ITEM_DIR = DATA_DIR / "ch2025_data_items"
OUT_DIR = ROOT / "outputs"
FEATURE_DIR = ROOT / "features"
EXPERIMENT_DIR = ROOT / "experiments"

LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ID_COLS = ["subject_id", "sleep_date", "lifelog_date"]


def ensure_dirs() -> None:
    for d in [OUT_DIR, FEATURE_DIR, EXPERIMENT_DIR, OUT_DIR / "validation"]:
        d.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def logloss(y_true: Iterable[int], y_pred: Iterable[float], eps: float = 1e-15) -> float:
    vals = []
    for y, p in zip(y_true, y_pred):
        p = min(max(float(p), eps), 1.0 - eps)
        vals.append(-(int(y) * math.log(p) + (1 - int(y)) * math.log(1 - p)))
    return sum(vals) / len(vals) if vals else float("nan")


def clip_prob(p: float, lo: float = 0.03, hi: float = 0.97) -> float:
    return min(max(float(p), lo), hi)
