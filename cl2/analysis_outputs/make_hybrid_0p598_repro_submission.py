from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import overnight_legacy_repro as legacy  # noqa: E402
import q23_presleep_app_experiments as q23app  # noqa: E402
import q3_soft_app_experiments as q3exp  # noqa: E402
import s2s4_pair_blend_nested_experiments as s2s4  # noqa: E402
from make_hybrid_0p599_submission import q2_combo_predict  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
KEY = d.KEY


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def assert_same_keys(left: pd.DataFrame, right: pd.DataFrame, label: str) -> None:
    if not left[KEY].reset_index(drop=True).equals(right[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {label}")


def legacy_nested_prediction(train: pd.DataFrame, sub: pd.DataFrame, group: str) -> np.ndarray:
    weights = pd.read_csv(OUT / "overnight_legacy_nested_weights.csv")
    mean_weights = weights[weights["group"].eq(group)].filter(like="w_").mean()
    w = np.asarray([mean_weights[f"w_{target}"] for target in TARGETS], dtype=float)
    base = cal.temporal_base(train, sub)
    sensor = legacy.fit_predict_legacy(train, sub, group)
    return clip((1.0 - w) * base + w * sensor)


def q3_fixed_predict(train: pd.DataFrame, sub: pd.DataFrame) -> np.ndarray:
    store = q23app.build_app_feature_store(pd.concat([train[KEY], sub[KEY]], ignore_index=True))
    combo = {"app": "logreg_c0.03", "wa": 0.10, "r": 0.50, "shrink": 1.0, "ws": 0.10}
    return q3exp.predict_combo(train, sub, store, combo)


def main() -> None:
    train_meta, sub_meta = mf.prepare(force_meta=False)
    train_meta = train_meta.sort_values(KEY).reset_index(drop=True)
    sub_meta = sub_meta.sort_values(KEY).reset_index(drop=True)
    train_legacy, sub_legacy = legacy.prepare_legacy()
    train_legacy = train_legacy.sort_values(KEY).reset_index(drop=True)
    sub_legacy = sub_legacy.sort_values(KEY).reset_index(drop=True)
    train_s2s4, sub_s2s4 = s2s4.ofe.prepare()
    train_s2s4 = train_s2s4.sort_values(KEY).reset_index(drop=True)
    sub_s2s4 = sub_s2s4.sort_values(KEY).reset_index(drop=True)

    assert_same_keys(train_meta, train_legacy, "train_meta/train_legacy")
    assert_same_keys(train_meta, train_s2s4, "train_meta/train_s2s4")
    assert_same_keys(sub_meta, sub_legacy, "sub_meta/sub_legacy")
    assert_same_keys(sub_meta, sub_s2s4, "sub_meta/sub_s2s4")

    legacy_phone_sensor = legacy.fit_predict_legacy(train_legacy, sub_legacy, "overnight_phone")
    legacy_phone_blend = legacy_nested_prediction(train_legacy, sub_legacy, "overnight_phone")
    legacy_all_blend = legacy_nested_prediction(train_legacy, sub_legacy, "overnight_all")
    q2 = q2_combo_predict(train_meta, sub_meta)
    q3 = q3_fixed_predict(train_meta, sub_meta)
    s2s4_sources = s2s4.source_predict(train_s2s4, sub_s2s4)
    s2s4_fixed = s2s4.apply_pairs(s2s4_sources, s2s4.fixed_choices())

    out = sub_meta[["subject_id", "sleep_date", "lifelog_date"]].copy()
    out["Q1"] = legacy_phone_sensor[:, TARGETS.index("Q1")]
    out["Q2"] = q2
    out["Q3"] = q3
    out["S1"] = legacy_phone_blend[:, TARGETS.index("S1")]
    out["S2"] = s2s4_fixed[:, TARGETS.index("S2")]
    out["S3"] = legacy_all_blend[:, TARGETS.index("S3")]
    out["S4"] = s2s4_fixed[:, TARGETS.index("S4")]
    out[TARGETS] = out[TARGETS].clip(1e-5, 1 - 1e-5)
    out.to_csv(OUT / "submission_hybrid_0p598_repro.csv", index=False)

    losses = {
        "Q1": 0.625034,
        "Q2": 0.6635717635251487,
        "Q3": 0.657266,
        "S1": 0.524188,
        "S2": 0.5597193509033811,
        "S3": 0.535248,
        "S4": 0.6277842740609245,
    }
    estimate = pd.DataFrame(
        [{"target": target, "source": "repro_hybrid", "cv_loss": losses[target]} for target in TARGETS]
    )
    estimate.loc[len(estimate)] = {
        "target": "mean",
        "source": "repro_hybrid",
        "cv_loss": float(np.mean([losses[t] for t in TARGETS])),
    }
    estimate.to_csv(OUT / "hybrid_0p598_repro_cv_estimate.csv", index=False)

    if (OUT / "submission_hybrid_0p598.csv").exists():
        old = pd.read_csv(OUT / "submission_hybrid_0p598.csv")
        diffs = {
            target: float(np.abs(old[target].to_numpy(dtype=float) - out[target].to_numpy(dtype=float)).max())
            for target in TARGETS
        }
        pd.DataFrame([{"target": k, "max_abs_diff_vs_0p598": v} for k, v in diffs.items()]).to_csv(
            OUT / "hybrid_0p598_repro_diff.csv", index=False
        )
        print("max abs diff vs submission_hybrid_0p598.csv")
        print(pd.Series(diffs).round(12).to_string())

    print("wrote", OUT / "submission_hybrid_0p598_repro.csv")
    print(estimate.round(6).to_string(index=False))
    print("shape", out.shape)
    print("nulls", int(out.isna().sum().sum()))
    print("range", float(out[TARGETS].min().min()), float(out[TARGETS].max().max()))
    print("means")
    print(out[TARGETS].mean().round(6).to_string())


if __name__ == "__main__":
    main()
