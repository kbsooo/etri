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
import sleep_interval_proxy_experiments as sip  # noqa: E402
import sleep_interval_proxy_model_search as search  # noqa: E402


OUT = Path(__file__).resolve().parent


def main() -> None:
    train, _ = sip.prepare_frames()
    cfg = search.ETConfig("et_leaf6_mf0.8", 420, 6, 0.80, None, 260526 + 6 * 10 + 80)
    cols = sip.feature_columns(train)
    cat = [c for c in cols if c in {"subject_id", "dow", "month"}]
    num = [c for c in cols if c not in cat]
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
            ("num", SimpleImputer(strategy="median"), num),
        ],
        sparse_threshold=0.2,
    )
    rows = []
    for target in ["Q1", "S1"]:
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
            pipe.fit(train[cols], train[target])
        names = pipe.named_steps["pre"].get_feature_names_out()
        importances = pipe.named_steps["clf"].feature_importances_
        tmp = pd.DataFrame({"target": target, "feature": names, "importance": importances})
        rows.append(tmp.sort_values("importance", ascending=False).head(50))
    result = pd.concat(rows, ignore_index=True)
    result.to_csv(OUT / "sleep_interval_proxy_feature_importance.csv", index=False)
    print(result.groupby("target").head(20).to_string(index=False))
    print("wrote", OUT / "sleep_interval_proxy_feature_importance.csv")


if __name__ == "__main__":
    main()
