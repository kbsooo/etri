from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.append(str(Path(__file__).resolve().parent))
import sleep_interval_proxy_augmented_experiments as aug  # noqa: E402


OUT = Path(__file__).resolve().parent


def main() -> None:
    train, _ = aug.prepare_frames()
    cfg = aug.ETConfig("aug_leaf10_mf0.6", 520, 10, 0.60, None, 260705)
    cols = aug.feature_columns(train)
    cat = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num = [c for c in cols if c not in cat]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            ("num", SimpleImputer(strategy="median"), num),
        ],
        sparse_threshold=0.2,
    )
    clf = ExtraTreesClassifier(
        n_estimators=cfg.n_estimators,
        min_samples_leaf=cfg.min_samples_leaf,
        max_features=cfg.max_features,
        max_depth=cfg.max_depth,
        random_state=cfg.seed,
        n_jobs=-1,
    )
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pipe.fit(train[cols], train["Q1"])
    result = pd.DataFrame(
        {
            "target": "Q1",
            "feature": pipe.named_steps["pre"].get_feature_names_out(),
            "importance": pipe.named_steps["clf"].feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    result.head(80).to_csv(OUT / "sleep_interval_proxy_augmented_feature_importance.csv", index=False)
    print(result.head(30).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_augmented_feature_importance.csv")


if __name__ == "__main__":
    main()
