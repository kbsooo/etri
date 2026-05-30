#!/usr/bin/env python3
"""Stress E193's evidence ledger against arbitrary weighting choices.

E193 intentionally used interpretive weights.  E194 asks whether E176 stays
the next public sensor under weight perturbations, leave-one-source removal,
and adversarial family emphasis.  This is a robustness audit, not a public LB
forecast and not a submission generator.
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
LEDGER_PATH = OUT / "e193_live_candidate_evidence_ledger_signal_audit.csv"
CANDIDATES = ["e176", "e154", "e144"]
RNG_SEED = 194

SOURCE_FAMILY = {
    "E179": "visible_body_q2",
    "E180": "known_winner_topcell",
    "E181": "binary_world",
    "E182/E183": "pressure_branch",
    "E183": "pressure_branch",
    "E186": "antisymmetric_pair",
    "E192": "clean_e72_tail",
}


def fmt(x: float | int | str | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    if isinstance(x, str):
        return x
    return f"{x:.9g}"


def markdown_table(df: pd.DataFrame) -> str:
    safe = df.copy()
    for col in safe.columns:
        safe[col] = safe[col].map(lambda x: fmt(x) if isinstance(x, (float, int)) else str(x))
        safe[col] = safe[col].str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(safe.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(safe.columns)) + " |"
    rows = [header, sep]
    for _, row in safe.iterrows():
        rows.append("| " + " | ".join(row.astype(str).tolist()) + " |")
    return "\n".join(rows)


def load_ledger() -> pd.DataFrame:
    if not LEDGER_PATH.exists():
        raise FileNotFoundError(LEDGER_PATH)
    df = pd.read_csv(LEDGER_PATH)
    df["family"] = df["source"].map(SOURCE_FAMILY).fillna(df["source"])
    return df


def score(df: pd.DataFrame, family_weights: dict[str, float] | None = None, missing_penalty: float = 0.0) -> pd.Series:
    family_weights = family_weights or {}
    tmp = df.copy()
    tmp["family_weight"] = tmp["family"].map(family_weights).fillna(1.0)
    tmp["contrib"] = tmp["evidence_balance_contribution"] * tmp["family_weight"]
    if missing_penalty:
        tmp.loc[tmp["direction"].eq("missing"), "contrib"] = missing_penalty * tmp.loc[
            tmp["direction"].eq("missing"), "family_weight"
        ]
    return tmp.groupby("candidate")["contrib"].sum().reindex(CANDIDATES)


def winner(scores: pd.Series) -> str:
    return str(scores.sort_values(ascending=False).index[0])


def build_leaveout(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    families = sorted(df["family"].unique())

    scenarios: list[tuple[str, set[str]]] = [("baseline", set())]
    scenarios += [(f"drop_{family}", {family}) for family in families]
    scenarios += [
        ("drop_visible_plus_topcell", {"visible_body_q2", "known_winner_topcell"}),
        ("drop_visible_topcell_pair", {"visible_body_q2", "known_winner_topcell", "antisymmetric_pair"}),
        ("drop_binary_and_local_pressure", {"binary_world", "pressure_branch"}),
    ]
    for r in [2, 3]:
        for combo in combinations(families, r):
            if len(scenarios) >= 1 + len(families) + 4 + 30:
                break
            scenarios.append((f"drop_{'+'.join(combo)}", set(combo)))

    for name, dropped in scenarios:
        kept = df.loc[~df["family"].isin(dropped)].copy()
        scores = score(kept)
        row = {
            "scenario": name,
            "dropped_families": ",".join(sorted(dropped)) if dropped else "",
            "winner": winner(scores),
        }
        for c in CANDIDATES:
            row[f"{c}_balance"] = float(scores[c])
        row["e176_minus_e154"] = float(scores["e176"] - scores["e154"])
        row["e176_minus_e144"] = float(scores["e176"] - scores["e144"])
        rows.append(row)
    return pd.DataFrame(rows)


def build_missing_penalty(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for penalty in [0.0, -0.1, -0.25, -0.5, -1.0, -2.0]:
        scores = score(df, missing_penalty=penalty)
        rows.append(
            {
                "missing_penalty": penalty,
                "winner": winner(scores),
                "e176_balance": float(scores["e176"]),
                "e154_balance": float(scores["e154"]),
                "e144_balance": float(scores["e144"]),
                "e176_minus_e154": float(scores["e176"] - scores["e154"]),
                "e176_minus_e144": float(scores["e176"] - scores["e144"]),
            }
        )
    return pd.DataFrame(rows)


def build_adversarial_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    base = score(df)
    rows = []
    families = sorted(df["family"].unique())
    family_contrib = {
        family: score(df.loc[df["family"].eq(family)]).fillna(0.0) for family in families
    }
    total_diff_e154 = float(base["e176"] - base["e154"])
    total_diff_e144 = float(base["e176"] - base["e144"])
    for family, contrib in family_contrib.items():
        for challenger, total_diff in [("e154", total_diff_e154), ("e144", total_diff_e144)]:
            family_diff = float(contrib["e176"] - contrib[challenger])
            non_family_diff = total_diff - family_diff
            if abs(family_diff) < 1e-12:
                threshold = np.nan
                read = "family has no relative effect"
            else:
                threshold = -non_family_diff / family_diff
                if threshold < 0:
                    read = "cannot flip by positive multiplier alone"
                else:
                    read = "positive multiplier can flip ranking"
            rows.append(
                {
                    "family_scaled": family,
                    "challenger": challenger,
                    "baseline_e176_minus_challenger": total_diff,
                    "family_diff_component": family_diff,
                    "non_family_diff_component": non_family_diff,
                    "flip_multiplier": threshold,
                    "interpretation": read,
                }
            )

    conservative = df.loc[~df["family"].isin({"visible_body_q2", "known_winner_topcell"})].copy()
    conservative_base = score(conservative)
    pair_contrib = score(conservative.loc[conservative["family"].eq("antisymmetric_pair")]).fillna(0.0)
    for challenger in ["e154", "e144"]:
        total_diff = float(conservative_base["e176"] - conservative_base[challenger])
        family_diff = float(pair_contrib["e176"] - pair_contrib[challenger])
        non_family_diff = total_diff - family_diff
        threshold = -non_family_diff / family_diff if abs(family_diff) > 1e-12 else np.nan
        rows.append(
            {
                "family_scaled": "antisymmetric_pair_after_dropping_noncomparable_visible",
                "challenger": challenger,
                "baseline_e176_minus_challenger": total_diff,
                "family_diff_component": family_diff,
                "non_family_diff_component": non_family_diff,
                "flip_multiplier": threshold,
                "interpretation": "conservative stress: pair evidence must stay above this multiplier",
            }
        )
    return pd.DataFrame(rows)


def build_monte_carlo(df: pd.DataFrame, n: int = 20000) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    families = sorted(df["family"].unique())
    fam_idx = {family: i for i, family in enumerate(families)}
    cand_idx = {candidate: i for i, candidate in enumerate(CANDIDATES)}
    contrib = np.zeros((len(families), len(CANDIDATES)), dtype=float)
    for _, row in df.iterrows():
        contrib[fam_idx[row["family"]], cand_idx[row["candidate"]]] += float(
            row["evidence_balance_contribution"]
        )
    rows = []

    for design in ["family_loguniform_0p25_4", "family_loguniform_0p5_2", "family_dropout_20pct"]:
        if design == "family_loguniform_0p25_4":
            weights = np.exp(rng.uniform(np.log(0.25), np.log(4.0), size=(n, len(families))))
        elif design == "family_loguniform_0p5_2":
            weights = np.exp(rng.uniform(np.log(0.5), np.log(2.0), size=(n, len(families))))
        else:
            weights = (rng.random(size=(n, len(families))) >= 0.20).astype(float)
        scores_matrix = weights @ contrib
        winners = scores_matrix.argmax(axis=1)
        margins = scores_matrix[:, cand_idx["e176"]] - np.maximum(
            scores_matrix[:, cand_idx["e154"]], scores_matrix[:, cand_idx["e144"]]
        )
        rows.append(
            {
                "design": design,
                "n": n,
                "e176_win_rate": float(np.mean(winners == cand_idx["e176"])),
                "e154_win_rate": float(np.mean(winners == cand_idx["e154"])),
                "e144_win_rate": float(np.mean(winners == cand_idx["e144"])),
                "e176_margin_mean": float(np.mean(margins)),
                "e176_margin_p05": float(np.quantile(margins, 0.05)),
                "e176_margin_p50": float(np.quantile(margins, 0.50)),
                "e176_margin_p95": float(np.quantile(margins, 0.95)),
            }
        )

    family_summary = []
    for family in families:
        kept = df.loc[df["family"].eq(family)]
        scores = score(kept)
        family_summary.append(
            {
                "family": family,
                "winner_if_alone": winner(scores),
                "e176_balance": float(scores["e176"]),
                "e154_balance": float(scores["e154"]),
                "e144_balance": float(scores["e144"]),
                "e176_minus_e154": float(scores["e176"] - scores["e154"]),
                "e176_minus_e144": float(scores["e176"] - scores["e144"]),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(family_summary)


def write_report(
    leaveout: pd.DataFrame,
    missing: pd.DataFrame,
    thresholds: pd.DataFrame,
    mc: pd.DataFrame,
    family: pd.DataFrame,
) -> Path:
    path = OUT / "e194_evidence_ledger_robustness_report.md"
    baseline = leaveout.loc[leaveout["scenario"].eq("baseline")].iloc[0]
    single_drop = leaveout.loc[
        leaveout["dropped_families"].ne("") & ~leaveout["dropped_families"].str.contains(",", regex=False)
    ]
    single_drop_e176_rate = float(single_drop["winner"].eq("e176").mean())
    binary_flip = thresholds.loc[
        thresholds["family_scaled"].eq("binary_world") & thresholds["challenger"].eq("e154")
    ].iloc[0]
    conservative_pair = thresholds.loc[
        thresholds["family_scaled"].eq("antisymmetric_pair_after_dropping_noncomparable_visible")
        & thresholds["challenger"].eq("e154")
    ].iloc[0]

    body = f"""# E194 Evidence Ledger Robustness

## Question

Is E193's E176-first decision robust, or is it an artifact of arbitrary evidence weights?

## Result

E176 remains first under every single-source leaveout and wins most random family-weight perturbations. The result is not unconditional: if non-comparable visible/top-cell evidence is removed and the antisymmetric pair sensor is discounted below about `{fmt(float(conservative_pair['flip_multiplier']))}` of its E193 weight, E154 becomes the stronger repaired-branch worldview.

Baseline E176 balance is `{fmt(float(baseline['e176_balance']))}` versus E154 `{fmt(float(baseline['e154_balance']))}` and E144 `{fmt(float(baseline['e144_balance']))}`.

## Leaveout Stress

Single-source leaveout E176 win rate: `{fmt(single_drop_e176_rate)}`.

{markdown_table(leaveout.head(16))}

## Monte Carlo Weight Stress

{markdown_table(mc)}

## Family-Alone Stress

{markdown_table(family)}

## Missing-Penalty Stress

{markdown_table(missing)}

## Adversarial Thresholds

{markdown_table(thresholds)}

## Interpretation

- E176's first-slot status is robust to ordinary weight uncertainty.
- The most important challenger is not E144; it is E154 under a high-trust binary-world / low-trust pair-geometry worldview.
- E181 binary-world evidence would flip E176 versus E154 if its family weight were multiplied above `{fmt(float(binary_flip['flip_multiplier']))}` while all other families stayed fixed.
- If E176-only visible/top-cell evidence is excluded as non-comparable, E176 still leads, but then it depends materially on the antisymmetric pair geometry staying above about `{fmt(float(conservative_pair['flip_multiplier']))}` of its current weight.
- This means E176 is a robust sensor-priority choice, not a theorem. The live alternative remains: trust inherited binary worlds more than pair/visible/clean-shape geometry and submit an E154-style repaired-branch sensor instead.

## Decision

No new submission is created. E176 remains the next single public sensor by robustness stress. The exact worldview is now more explicit: E176 bets that pair/shape/broad-body evidence is not a shortcut, while E154 bets that inherited binary-world counterprior is the cleaner hidden-label proxy.
"""
    path.write_text(body, encoding="utf-8")
    return path


def main() -> None:
    df = load_ledger()
    leaveout = build_leaveout(df)
    missing = build_missing_penalty(df)
    thresholds = build_adversarial_thresholds(df)
    mc, family = build_monte_carlo(df)

    leaveout_path = OUT / "e194_evidence_ledger_robustness_leaveout.csv"
    missing_path = OUT / "e194_evidence_ledger_robustness_missing_penalty.csv"
    thresholds_path = OUT / "e194_evidence_ledger_robustness_thresholds.csv"
    mc_path = OUT / "e194_evidence_ledger_robustness_monte_carlo.csv"
    family_path = OUT / "e194_evidence_ledger_robustness_family_alone.csv"
    leaveout.to_csv(leaveout_path, index=False)
    missing.to_csv(missing_path, index=False)
    thresholds.to_csv(thresholds_path, index=False)
    mc.to_csv(mc_path, index=False)
    family.to_csv(family_path, index=False)
    report_path = write_report(leaveout, missing, thresholds, mc, family)

    print("wrote", leaveout_path)
    print("wrote", missing_path)
    print("wrote", thresholds_path)
    print("wrote", mc_path)
    print("wrote", family_path)
    print("wrote", report_path)
    print(leaveout.loc[leaveout["scenario"].eq("baseline")].to_string(index=False))
    print(mc.to_string(index=False))


if __name__ == "__main__":
    main()
