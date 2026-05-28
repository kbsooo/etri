from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import block_level_regressor_experiments as blr  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import overnight_feature_experiments as ofe  # noqa: E402
import overnight_legacy_repro as legacy  # noqa: E402


OUT = Path(__file__).resolve().parent
KEY = d.KEY


def run_one(name: str, train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = train.sort_values(KEY).reset_index(drop=True)
    results, selected, _, _ = blr.nested_oof(train)
    results.insert(0, "feature_set", name)
    selected.insert(0, "feature_set", name)
    return results, selected


def main() -> None:
    warnings.filterwarnings("ignore", message="Skipping features without any observed values*")
    legacy_train, _ = legacy.prepare_legacy()
    v2_train, _ = ofe.prepare()
    rows = []
    selections = []
    for name, train in [
        ("legacy_overnight_v1", legacy_train),
        ("overnight_v2", v2_train),
    ]:
        print(f"[overnight block regressor] {name}", flush=True)
        result, selected = run_one(name, train)
        rows.append(result)
        selections.append(selected)
    results = pd.concat(rows, ignore_index=True).sort_values(["mean", "feature_set", "model"])
    selected = pd.concat(selections, ignore_index=True)
    results.to_csv(OUT / "overnight_block_level_regressor_results.csv", index=False)
    selected.to_csv(OUT / "overnight_block_level_regressor_selected.csv", index=False)
    print(results.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
