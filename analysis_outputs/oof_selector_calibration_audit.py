#!/usr/bin/env python3
"""E39 OOF selector calibration audit.

This experiment asks whether the existing train OOF archive can provide an
independent selector/worldview calibration target. It deliberately avoids using
unobserved public LB scores. Known public scores are used only as a sanity check
for a few OOF files that can be matched by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

BASELINE_OOF = OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy"
BASELINE_PUBLIC = 0.5784273528

KNOWN_PUBLIC_OOF = {
    "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy": {
        "public_lb": 0.5784273528,
        "public_role": "final9_baseline",
    },
    "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy": {
        "public_lb": 0.5779449757,
        "public_role": "stage2_public_better_than_final9",
    },
    "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy": {
        "public_lb": 0.5783033652,
        "public_role": "ordinal_public_better_than_final9",
    },
}

DETAIL_OUT = OUT / "oof_selector_calibration_scores.csv"
FAMILY_OUT = OUT / "oof_selector_calibration_family_summary.csv"
KNOWN_OUT = OUT / "oof_selector_calibration_known_public.csv"
SUBSET_OUT = OUT / "oof_selector_calibration_subsets.csv"
REPORT_OUT = OUT / "oof_selector_calibration_report.md"


@dataclass
class Subset:
    name: str
    tier: str
    idx: np.ndarray
    detail: str


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p.astype(np.float64), 1e-5, 1 - 1e-5)


def logloss(y: np.ndarray, p: np.ndarray, idx: np.ndarray | None = None) -> float:
    if idx is not None:
        y = y[idx]
        p = p[idx]
    p = clip(p)
    return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))


def array_hash(arr: np.ndarray) -> str:
    rounded = np.round(clip(arr), 10)
    return sha1(rounded.tobytes()).hexdigest()[:16]


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(ROOT / "data/ch2026_metrics_train.csv")
    features = pd.read_parquet(OUT / "all_keys_deep_features.parquet")
    for df in (train, features):
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    train_feat = features.loc[features["split"].eq("train")].merge(
        train[KEYS + TARGETS], on=KEYS, how="inner", validate="one_to_one"
    )
    test_feat = features.loc[features["split"].eq("submission")].copy()
    if len(train_feat) != len(train):
        raise RuntimeError(f"train feature alignment failed: {len(train_feat)}/{len(train)}")
    return train.reset_index(drop=True), train_feat.reset_index(drop=True), test_feat.reset_index(drop=True)


def numeric_cols(frame: pd.DataFrame) -> list[str]:
    skip = set(KEYS + TARGETS + ["split"])
    out: list[str] = []
    for col in frame.columns:
        if col in skip:
            continue
        if not pd.api.types.is_numeric_dtype(frame[col]):
            continue
        vals = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if int(vals.notna().sum()) >= 40:
            out.append(col)
    return out


def make_domain_and_density(train_feat: pd.DataFrame, test_feat: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    all_feat = pd.concat([train_feat, test_feat], axis=0, ignore_index=True)
    cols = numeric_cols(all_feat)
    x = all_feat[cols].replace([np.inf, -np.inf], np.nan)
    y_domain = np.r_[np.zeros(len(train_feat), dtype=int), np.ones(len(test_feat), dtype=int)]
    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced", solver="lbfgs"),
    )
    pipe.fit(x, y_domain)
    domain_prob = pipe.predict_proba(x)[:, 1]
    domain_auc = roc_auc_score(y_domain, domain_prob)

    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    x_train = prep.fit_transform(train_feat[cols].replace([np.inf, -np.inf], np.nan))
    nn = NearestNeighbors(n_neighbors=min(8, len(train_feat)), metric="euclidean")
    nn.fit(x_train)
    dist, _ = nn.kneighbors(x_train)
    # First neighbor is the row itself; use a robust local radius.
    density_radius = dist[:, -1]
    return domain_prob[: len(train_feat)], density_radius, np.array([domain_auc], dtype=float)


def quantile_idx(values: np.ndarray, q: float, side: str) -> np.ndarray:
    cut = float(np.nanquantile(values, q))
    if side == "high":
        return np.flatnonzero(values >= cut)
    if side == "low":
        return np.flatnonzero(values <= cut)
    raise ValueError(side)


def build_subsets(train_feat: pd.DataFrame, domain_prob: np.ndarray, density_radius: np.ndarray) -> list[Subset]:
    n = len(train_feat)
    subject_day = train_feat["subject_day_index"].to_numpy(float)
    missing_frac = train_feat[numeric_cols(train_feat)].replace([np.inf, -np.inf], np.nan).isna().mean(axis=1).to_numpy()

    subsets = [
        Subset("all_train", "full", np.arange(n), "all OOF rows"),
        Subset("subject_future_tail40", "label_free_time", quantile_idx(subject_day, 0.60, "high"), "top 40% subject_day_index"),
        Subset("subject_future_tail25", "label_free_time", quantile_idx(subject_day, 0.75, "high"), "top 25% subject_day_index"),
        Subset("subject_early_head25", "label_free_time", quantile_idx(subject_day, 0.25, "low"), "bottom 25% subject_day_index"),
        Subset("domain_testlike_high30", "label_free_domain", quantile_idx(domain_prob, 0.70, "high"), "top 30% train rows by train/test domain score"),
        Subset("domain_trainlike_low30", "label_free_domain", quantile_idx(domain_prob, 0.30, "low"), "bottom 30% train rows by train/test domain score"),
        Subset("raw_density_low30", "label_free_density", quantile_idx(density_radius, 0.70, "high"), "top 30% raw-feature NN radius"),
        Subset("raw_density_high30", "label_free_density", quantile_idx(density_radius, 0.30, "low"), "bottom 30% raw-feature NN radius"),
        Subset("missing_high30", "label_free_missingness", quantile_idx(missing_frac, 0.70, "high"), "top 30% missingness"),
        Subset("missing_low30", "label_free_missingness", quantile_idx(missing_frac, 0.30, "low"), "bottom 30% missingness"),
    ]

    # Contiguous date/order blocks are a cheap proxy for hidden public block stress.
    order = np.argsort(pd.to_datetime(train_feat["sleep_date"]).to_numpy())
    for i, block in enumerate(np.array_split(order, 5)):
        subsets.append(Subset(f"date_quintile_{i}", "label_free_order_block", np.asarray(block, dtype=int), "sleep_date quintile"))

    for subject, group in train_feat.groupby("subject_id", sort=True):
        idx = group.index.to_numpy(dtype=int)
        if len(idx) >= 20:
            subsets.append(Subset(f"subject_{subject}", "label_free_subject_block", idx, "single subject block"))

    rng = np.random.default_rng(20260528)
    for seed_i in range(6):
        perm = rng.permutation(n)
        for fold_i, fold in enumerate(np.array_split(perm, 5)):
            subsets.append(Subset(f"random_s{seed_i}_f{fold_i}", "random_block", np.asarray(fold, dtype=int), "random OOF block"))
    return subsets


def family_name(path: Path) -> str:
    name = path.name.lower()
    if "stage2" in name:
        return "stage2"
    if "ordinal" in name:
        return "ordinal"
    if "hybrid" in name:
        return "hybrid"
    if "cvjepa" in name or "jepa" in name:
        return "jepa"
    if "subjectgate" in name:
        return "subjectgate"
    if "presleep" in name:
        return "presleep"
    if "orthcap" in name:
        return "orthcap"
    if "block" in name:
        return "block"
    if "rhythm" in name:
        return "rhythm"
    if "public" in name:
        return "publicblend"
    return "other"


def discover_oof_files() -> list[Path]:
    files = sorted(OUT.glob("*_oof.npy")) + sorted(JEPA.glob("*_oof.npy"))
    return [p for p in files if p.is_file()]


def score_archive(y: np.ndarray, subsets: list[Subset], base: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_losses = {s.name: logloss(y, base, s.idx) for s in subsets}
    label_free_names = [
        s.name
        for s in subsets
        if s.tier.startswith("label_free_") and not s.tier.endswith("subject_block") and not s.tier.endswith("order_block")
    ]
    subject_names = [s.name for s in subsets if s.tier == "label_free_subject_block"]
    order_names = [s.name for s in subsets if s.tier == "label_free_order_block"]
    random_names = [s.name for s in subsets if s.tier == "random_block"]

    rows: list[dict[str, Any]] = []
    subset_rows: list[dict[str, Any]] = []
    seen_hashes: dict[str, str] = {}
    known_names = set(KNOWN_PUBLIC_OOF)
    skipped = 0

    for path in discover_oof_files():
        try:
            pred = np.load(path)
        except Exception:  # noqa: BLE001
            skipped += 1
            continue
        if pred.shape != y.shape:
            skipped += 1
            continue
        pred = clip(pred)
        h = array_hash(pred)
        duplicate_of = seen_hashes.get(h, "")
        if h in seen_hashes and path.name not in known_names:
            continue
        if h not in seen_hashes:
            seen_hashes[h] = str(path.relative_to(ROOT))

        deltas: dict[str, float] = {}
        for subset in subsets:
            delta = logloss(y, pred, subset.idx) - base_losses[subset.name]
            deltas[subset.name] = delta
            if subset.name in {
                "all_train",
                "subject_future_tail25",
                "domain_testlike_high30",
                "raw_density_low30",
                "missing_high30",
            }:
                subset_rows.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "subset": subset.name,
                        "tier": subset.tier,
                        "n_rows": int(len(subset.idx)),
                        "delta_vs_baseline": delta,
                    }
                )

        label_free = np.array([deltas[n] for n in label_free_names], dtype=float)
        subject = np.array([deltas[n] for n in subject_names], dtype=float)
        order = np.array([deltas[n] for n in order_names], dtype=float)
        random = np.array([deltas[n] for n in random_names], dtype=float)
        stress = np.r_[label_free, subject, order]

        file_name = path.name
        known = KNOWN_PUBLIC_OOF.get(file_name, {})
        public_lb = known.get("public_lb", np.nan)
        public_delta = float(public_lb - BASELINE_PUBLIC) if np.isfinite(public_lb) else np.nan
        rows.append(
            {
                "file": str(path.relative_to(ROOT)),
                "basename": file_name,
                "family": family_name(path),
                "hash": h,
                "duplicate_of": duplicate_of,
                "known_public_lb": public_lb,
                "known_public_delta_vs_final9": public_delta,
                "known_public_role": known.get("public_role", ""),
                "full_delta": deltas["all_train"],
                "label_free_mean_delta": float(label_free.mean()),
                "label_free_median_delta": float(np.median(label_free)),
                "label_free_worst_delta": float(label_free.max()),
                "label_free_p90_delta": float(np.quantile(label_free, 0.90)),
                "label_free_better_rate": float((label_free < 0).mean()),
                "subject_worst_delta": float(subject.max()) if len(subject) else np.nan,
                "subject_better_rate": float((subject < 0).mean()) if len(subject) else np.nan,
                "order_worst_delta": float(order.max()) if len(order) else np.nan,
                "order_better_rate": float((order < 0).mean()) if len(order) else np.nan,
                "random_worst_delta": float(random.max()),
                "random_p90_delta": float(np.quantile(random, 0.90)),
                "random_better_rate": float((random < 0).mean()),
                "stress_mean_delta": float(stress.mean()),
                "stress_worst_delta": float(stress.max()),
                "stress_p90_delta": float(np.quantile(stress, 0.90)),
                "stress_better_rate": float((stress < 0).mean()),
                "mean_abs_move_vs_baseline": float(np.abs(pred - base).mean()),
                "max_abs_move_vs_baseline": float(np.abs(pred - base).max()),
                "strict_oof_selector_gate": bool(
                    deltas["all_train"] < 0
                    and (label_free < 0).mean() >= 0.70
                    and (random < 0).mean() >= 0.60
                    and (subject < 0).mean() >= 0.50
                    and (order < 0).mean() >= 0.60
                    and float(stress.max()) <= 0.00050
                ),
                "conservative_gate": bool(
                    deltas["all_train"] < 0
                    and (label_free < 0).mean() >= 0.85
                    and (subject < 0).mean() >= 0.70
                    and (order < 0).mean() >= 0.80
                    and float(stress.max()) <= 0.00010
                ),
            }
        )

    scores = pd.DataFrame(rows)
    if scores.empty:
        raise RuntimeError(f"no OOF arrays scored; skipped={skipped}")
    scores["selector_calibration_score"] = (
        scores["stress_p90_delta"].fillna(9.0)
        + 0.25 * scores["stress_worst_delta"].fillna(9.0)
        + 0.10 * np.maximum(scores["full_delta"].fillna(9.0), 0.0)
        - 0.00001 * np.minimum(scores["mean_abs_move_vs_baseline"].fillna(0.0), 0.05)
    )
    scores = scores.sort_values(
        ["strict_oof_selector_gate", "conservative_gate", "selector_calibration_score"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    return scores, pd.DataFrame(subset_rows)


def family_summary(scores: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for family, group in scores.groupby("family", sort=False):
        best = group.sort_values("selector_calibration_score").iloc[0]
        rows.append(
            {
                "family": family,
                "n": int(len(group)),
                "strict_oof_gates": int(group["strict_oof_selector_gate"].sum()),
                "conservative_gates": int(group["conservative_gate"].sum()),
                "median_full_delta": float(group["full_delta"].median()),
                "median_stress_p90_delta": float(group["stress_p90_delta"].median()),
                "best_file": best["file"],
                "best_full_delta": float(best["full_delta"]),
                "best_stress_p90_delta": float(best["stress_p90_delta"]),
                "best_stress_worst_delta": float(best["stress_worst_delta"]),
                "best_score": float(best["selector_calibration_score"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["strict_oof_gates", "best_score"], ascending=[False, True])


def known_public_summary(scores: pd.DataFrame) -> pd.DataFrame:
    known = scores[scores["basename"].isin(KNOWN_PUBLIC_OOF)].copy()
    known["oof_sign"] = np.sign(known["full_delta"])
    known["public_sign"] = np.sign(known["known_public_delta_vs_final9"].fillna(0.0))
    known["sign_matches_public"] = known["oof_sign"].eq(known["public_sign"])
    cols = [
        "file",
        "known_public_role",
        "known_public_lb",
        "known_public_delta_vs_final9",
        "full_delta",
        "stress_p90_delta",
        "stress_worst_delta",
        "label_free_better_rate",
        "subject_better_rate",
        "order_better_rate",
        "random_better_rate",
        "strict_oof_selector_gate",
        "conservative_gate",
        "sign_matches_public",
    ]
    return known[cols].sort_values("known_public_lb")


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6g}")
        else:
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else str(x))
    headers = [str(c) for c in out.columns]
    rows = out.astype(str).values.tolist()
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def fmt(row: list[str]) -> str:
        return "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(row))) + " |"

    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    return "\n".join([fmt(headers), sep] + [fmt(row) for row in rows])


def write_report(
    scores: pd.DataFrame,
    fam: pd.DataFrame,
    known: pd.DataFrame,
    subsets: list[Subset],
    domain_auc: float,
) -> None:
    strict_n = int(scores["strict_oof_selector_gate"].sum())
    conservative_n = int(scores["conservative_gate"].sum())
    known_nonbase = known[known["known_public_role"].ne("final9_baseline")]
    known_match_rate = float(known_nonbase["sign_matches_public"].mean()) if len(known_nonbase) else np.nan
    known_rank_agreement = np.nan
    if len(known_nonbase) >= 2:
        agree = 0
        total = 0
        vals = known_nonbase[["known_public_lb", "full_delta"]].to_numpy(float)
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                public_sign = np.sign(vals[i, 0] - vals[j, 0])
                oof_sign = np.sign(vals[i, 1] - vals[j, 1])
                if public_sign == 0 or oof_sign == 0:
                    continue
                agree += int(public_sign == oof_sign)
                total += 1
        known_rank_agreement = float(agree / total) if total else np.nan
    top = scores.head(12)[
        [
            "file",
            "family",
            "full_delta",
            "stress_p90_delta",
            "stress_worst_delta",
            "stress_better_rate",
            "mean_abs_move_vs_baseline",
            "strict_oof_selector_gate",
            "conservative_gate",
        ]
    ]
    lines = [
        "# E39 OOF Selector Calibration Audit",
        "",
        "## Observe",
        "",
        "E38 ranked public sensors but could not certify any candidate. The next question is whether train OOF history can create an independent selector calibration target.",
        "",
        "## Wonder",
        "",
        "Do label-free train OOF stresses such as future-tail rows, train/test-domain-like rows, density, missingness, subject blocks, and date blocks select candidates whose sign is stable and whose known-public analogues agree with public LB?",
        "",
        "## Hypothesis",
        "",
        "H38: if selector identity can be calibrated locally, OOF improvements should be stable across label-free pseudo-public subsets, and known public OOF files should have OOF signs consistent with their public sign relative to the baseline.",
        "",
        "## Method",
        "",
        f"- Baseline OOF: `{BASELINE_OOF.relative_to(ROOT)}`.",
        f"- OOF rows scored: `{len(scores)}` after hash dedupe plus known-public aliases.",
        f"- Unique prediction hashes: `{scores['hash'].nunique()}`.",
        f"- Label-free subsets: `{sum(s.tier.startswith('label_free') for s in subsets)}` plus random blocks.",
        f"- Train/test domain AUC from raw features: `{domain_auc:.6f}`.",
        "- Gates use real train labels only through OOF predictions; public LB is only used for the known-public sanity table.",
        "",
        "## Result",
        "",
        f"- strict OOF selector gates: `{strict_n}`.",
        f"- conservative OOF gates: `{conservative_n}`.",
        f"- known-public nonbaseline sign match rate: `{known_match_rate:.6f}`.",
        f"- known-public nonbaseline pairwise rank agreement: `{known_rank_agreement:.6f}`.",
        "",
        "## Known Public OOF Sanity",
        "",
        df_to_markdown(known),
        "",
        "## Family Summary",
        "",
        df_to_markdown(fam.head(20)),
        "",
        "## Top OOF-Stable Candidates",
        "",
        df_to_markdown(top),
        "",
        "## Decision",
        "",
    ]
    if (
        strict_n == 0
        or (np.isfinite(known_match_rate) and known_match_rate < 1.0)
        or (np.isfinite(known_rank_agreement) and known_rank_agreement < 1.0)
    ):
        lines.append(
            "OOF stress is useful as a negative calibration target but not as a submission selector. It can expose local stability and local overfit, but it does not resolve the public selector/worldview conflict because known-public sign can match while known-public ordering still reverses."
        )
    else:
        lines.append(
            "OOF stress creates a candidate selector that deserves comparison with the E38 sensor lanes before any public diagnostic is spent."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{DETAIL_OUT.relative_to(ROOT)}`",
        f"- `{FAMILY_OUT.relative_to(ROOT)}`",
        f"- `{KNOWN_OUT.relative_to(ROOT)}`",
        f"- `{SUBSET_OUT.relative_to(ROOT)}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train, train_feat, test_feat = load_data()
    y = train[TARGETS].to_numpy(np.float64)
    if not BASELINE_OOF.exists():
        raise FileNotFoundError(BASELINE_OOF)
    base = clip(np.load(BASELINE_OOF))
    if base.shape != y.shape:
        raise RuntimeError(f"baseline shape mismatch: {base.shape} vs {y.shape}")

    domain_prob, density_radius, domain_auc_arr = make_domain_and_density(train_feat, test_feat)
    subsets = build_subsets(train_feat, domain_prob, density_radius)
    subset_meta = pd.DataFrame(
        [
            {
                "subset": s.name,
                "tier": s.tier,
                "n_rows": int(len(s.idx)),
                "detail": s.detail,
            }
            for s in subsets
        ]
    )

    scores, subset_scores = score_archive(y, subsets, base)
    fam = family_summary(scores)
    known = known_public_summary(scores)

    scores.to_csv(DETAIL_OUT, index=False)
    fam.to_csv(FAMILY_OUT, index=False)
    known.to_csv(KNOWN_OUT, index=False)
    subset_meta.merge(subset_scores, on=["subset", "tier", "n_rows"], how="left").to_csv(SUBSET_OUT, index=False)
    write_report(scores, fam, known, subsets, float(domain_auc_arr[0]))

    print(f"scored_oof_rows={len(scores)}")
    print(f"unique_prediction_hashes={scores['hash'].nunique()}")
    print(f"strict_oof_gates={int(scores['strict_oof_selector_gate'].sum())}")
    print(f"conservative_gates={int(scores['conservative_gate'].sum())}")
    print("known_public:")
    print(known.to_string(index=False))
    print("top:")
    print(
        scores.head(10)[
            [
                "file",
                "family",
                "full_delta",
                "stress_p90_delta",
                "stress_worst_delta",
                "stress_better_rate",
                "strict_oof_selector_gate",
                "conservative_gate",
            ]
        ].to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
