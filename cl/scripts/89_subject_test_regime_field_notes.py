#!/usr/bin/env python3
"""Subject/test-regime field notes for the cl data-science track.

No submission is generated. This script creates human-readable maps that decide
which test row/target pairs deserve movement and which should be frozen.
"""

from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEATURES = ROOT / "features"
EXP = ROOT / "experiments"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ID_COLS = ["subject_id", "sleep_date", "lifelog_date"]

# Tokens that survived earlier subject-debiased/context diagnostics.
S4_CONTEXT_TOKENS = [
    # Keep only the sparse WiFi/context tokens here. The BLE device-class tokens
    # are too broad/ubiquitous for a row-level "strong event" gate.
    "wifi_bssid:98:25:4a:80:6f:62",
    "wifi_bssid:9e:25:4a:80:6f:61",
    "wifi_bssid:80:ca:4b:59:3b:52",
    "wifi_bssid:50:46:ae:5f:2e:14",
    "wifi_bssid:9e:25:4a:80:73:13",
    "wifi_bssid:ee:5c:68:90:0c:eb",
    "wifi_bssid:60:29:d5:4a:47:d3",
]

Q2_COVERAGE_COLS = [
    "usage_active_hours",
    "usage_night_hours",
    "usage_longest_missing_hours",
    "w_light_longest_missing_hours",
    "hr_night_hours",
    "pedo_active_hours",
    "gps_active_hours",
    "wifi_active_hours",
    "any_sensor_active_hours",
]


def sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + math.exp(-max(min(x, 30), -30))))


def logit(p: float) -> float:
    p = min(max(float(p), 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def load_inputs():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for df in (train, test):
        df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
        df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    test = test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)

    coverage = pd.read_parquet(FEATURES / "observation_coverage_features.parquet")
    coverage["date"] = pd.to_datetime(coverage["date"])
    tokens = pd.read_parquet(FEATURES / "observation_identity_token_features.parquet")
    tokens["date"] = pd.to_datetime(tokens["date"])
    return train, test, coverage, tokens


def subject_profile_cards(train: pd.DataFrame, coverage: pd.DataFrame, tokens: pd.DataFrame) -> pd.DataFrame:
    rows = []
    token_cols = [c for c in S4_CONTEXT_TOKENS if c in tokens.columns]
    cov_cols = [c for c in Q2_COVERAGE_COLS if c in coverage.columns]

    for sid, g in train.groupby("subject_id"):
        g = g.sort_values("lifelog_date")
        cov_g = coverage[coverage.subject_id == sid]
        tok_g = tokens[tokens.subject_id == sid]
        row = {"subject_id": sid, "n_train": len(g), "train_start": g.lifelog_date.min().date(), "train_end": g.lifelog_date.max().date()}
        for y in LABELS:
            p = g[y].mean()
            ent = -(p * math.log2(p) + (1 - p) * math.log2(1 - p)) if 0 < p < 1 else 0.0
            row[f"prev_{y}"] = round(float(p), 4)
            row[f"entropy_{y}"] = round(float(ent), 4)
            vals = g[y].to_numpy()
            if len(vals) > 1:
                row[f"flip_rate_{y}"] = round(float(np.mean(vals[1:] != vals[:-1])), 4)
                row[f"stickiness_{y}"] = round(float(np.mean(vals[1:] == vals[:-1])), 4)
            else:
                row[f"flip_rate_{y}"] = np.nan
                row[f"stickiness_{y}"] = np.nan
        # Coverage reliability: high missingness means less trustworthy sensor-day evidence.
        if len(cov_g) and cov_cols:
            row["coverage_mean_active_hours"] = round(float(cov_g[[c for c in cov_cols if c.endswith("active_hours")]].mean(axis=1).mean()), 3)
            missing_cols = [c for c in cov_cols if c.endswith("longest_missing_hours")]
            row["coverage_mean_longest_missing"] = round(float(cov_g[missing_cols].mean(axis=1).mean()), 3) if missing_cols else np.nan
        else:
            row["coverage_mean_active_hours"] = np.nan
            row["coverage_mean_longest_missing"] = np.nan
        if len(tok_g) and token_cols:
            token_present = tok_g[token_cols].gt(0).any(axis=1)
            row["s4_context_token_days"] = int(token_present.sum())
            row["s4_context_token_rate"] = round(float(token_present.mean()), 4)
        else:
            row["s4_context_token_days"] = 0
            row["s4_context_token_rate"] = 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def build_test_regime_map(train: pd.DataFrame, test: pd.DataFrame, coverage: pd.DataFrame, tokens: pd.DataFrame) -> pd.DataFrame:
    # Coverage z-score relative to subject's full 700-day record as a descriptive anomaly proxy.
    cov_cols = [c for c in Q2_COVERAGE_COLS if c in coverage.columns]
    coverage_score = coverage[["subject_id", "date"]].copy()
    if cov_cols:
        z_parts = []
        for sid, cg in coverage.groupby("subject_id"):
            idx = cg.index
            base = cg[cov_cols].astype(float)
            mu = base.mean(axis=0)
            sd = base.std(axis=0).replace(0, np.nan)
            z = ((base - mu) / sd).abs().mean(axis=1)
            z_parts.append(pd.Series(z.values, index=idx))
        coverage_score["coverage_anomaly_score"] = pd.concat(z_parts).sort_index().fillna(0).values
    else:
        coverage_score["coverage_anomaly_score"] = 0.0

    token_cols = [c for c in S4_CONTEXT_TOKENS if c in tokens.columns]
    token_score = tokens[["subject_id", "date"]].copy()
    if token_cols:
        token_score["s4_context_token_count"] = tokens[token_cols].gt(0).sum(axis=1).astype(int)
    else:
        token_score["s4_context_token_count"] = 0

    rows = []
    for i, r in test.reset_index(drop=True).iterrows():
        sid = r.subject_id
        d = r.lifelog_date
        tg = train[train.subject_id == sid].sort_values("lifelog_date")
        prev_g = tg[tg.lifelog_date < d]
        next_g = tg[tg.lifelog_date > d]
        prev_row = prev_g.iloc[-1] if len(prev_g) else None
        next_row = next_g.iloc[0] if len(next_g) else None
        train_min, train_max = tg.lifelog_date.min(), tg.lifelog_date.max()
        regime = "hole" if train_min <= d <= train_max else "tail" if d > train_max else "pretrain"
        days_prev = int((d - prev_row.lifelog_date).days) if prev_row is not None else 999
        days_next = int((next_row.lifelog_date - d).days) if next_row is not None else 999
        nearest_days = min(days_prev, days_next)
        both_sides = prev_row is not None and next_row is not None

        row = {
            "row_id": i,
            "subject_id": sid,
            "sleep_date": r.sleep_date.date(),
            "lifelog_date": d.date(),
            "regime": regime,
            "days_to_prev_label": days_prev if days_prev != 999 else np.nan,
            "days_to_next_label": days_next if days_next != 999 else np.nan,
            "nearest_label_days": nearest_days if nearest_days != 999 else np.nan,
            "has_both_neighbor_sides": bool(both_sides),
        }
        for y in LABELS:
            row[f"prev_{y}"] = int(prev_row[y]) if prev_row is not None else np.nan
            row[f"next_{y}"] = int(next_row[y]) if next_row is not None else np.nan
            row[f"neighbor_agree_{y}"] = bool(both_sides and int(prev_row[y]) == int(next_row[y]))
            row[f"neighbor_mean_{y}"] = np.nanmean([row[f"prev_{y}"], row[f"next_{y}"]])

        cv = coverage_score[(coverage_score.subject_id == sid) & (coverage_score.date == d)]
        tv = token_score[(token_score.subject_id == sid) & (token_score.date == d)]
        row["coverage_anomaly_score"] = round(float(cv.coverage_anomaly_score.iloc[0]), 4) if len(cv) else 0.0
        row["s4_context_token_count"] = int(tv.s4_context_token_count.iloc[0]) if len(tv) else 0
        rows.append(row)
    return pd.DataFrame(rows)


def build_action_map(train: pd.DataFrame, regime: pd.DataFrame) -> pd.DataFrame:
    subject_prev = train.groupby("subject_id")[LABELS].mean()
    rows = []
    for _, r in regime.iterrows():
        sid = r.subject_id
        for target in LABELS:
            base_p = float(subject_prev.loc[sid, target])
            action = "FREEZE"
            strength = 0.0
            direction = "HOLD"
            reason = []
            candidate_p = base_p

            nearest = r.nearest_label_days if pd.notna(r.nearest_label_days) else 999
            neigh_mean = r[f"neighbor_mean_{target}"]
            agree = bool(r[f"neighbor_agree_{target}"])

            if target == "Q2":
                # Most movable: small coverage/deviation and neighbor grammar evidence.
                if r.regime == "hole" and nearest <= 7:
                    strength += 0.45
                    reason.append("hole row with close labeled neighbor")
                if agree and pd.notna(neigh_mean):
                    strength += 0.25
                    reason.append("prev/next Q2 agree")
                if r.coverage_anomaly_score >= 0.65:
                    strength += 0.20
                    reason.append("coverage/deviation anomaly present")
                if strength >= 0.55:
                    action = "MOVE"
                elif strength >= 0.30:
                    action = "TINY_MOVE"
                if pd.notna(neigh_mean):
                    candidate_p = 0.65 * base_p + 0.35 * float(neigh_mean)
                if r.coverage_anomaly_score >= 0.65:
                    candidate_p = sigmoid(logit(candidate_p) + 0.18)

            elif target == "Q3":
                # Move only when the temporal completion evidence is clean.
                if r.regime == "hole" and nearest <= 7 and agree and pd.notna(neigh_mean):
                    strength = 0.55
                    action = "MOVE"
                    reason.append("close prev/next Q3 agree; temporal completion looks credible")
                    candidate_p = 0.55 * base_p + 0.45 * float(neigh_mean)
                elif nearest <= 7 and pd.notna(neigh_mean):
                    strength = 0.25
                    action = "TINY_MOVE"
                    reason.append("near Q3 neighbor exists but evidence is not clean")
                    candidate_p = 0.80 * base_p + 0.20 * float(neigh_mean)
                else:
                    reason.append("no clean Q3 neighbor grammar")

            elif target == "S4":
                # Sparse context event: capped movement only.
                if r.s4_context_token_count >= 2:
                    strength = 0.35
                    action = "TINY_MOVE"
                    reason.append("multiple S4 context tokens present; capped only")
                    candidate_p = sigmoid(logit(base_p) + 0.25)
                elif r.s4_context_token_count == 1:
                    strength = 0.18
                    action = "TINY_MOVE"
                    reason.append("one S4 context token present; very small cap")
                    candidate_p = sigmoid(logit(base_p) + 0.12)
                else:
                    reason.append("no strong S4 context event")

            elif target == "Q1":
                # Q1 remains mostly frozen because coverage can be misleading.
                if agree and nearest <= 3 and pd.notna(neigh_mean):
                    strength = 0.15
                    action = "TINY_MOVE"
                    reason.append("very close Q1 neighbors agree; tiny only")
                    candidate_p = 0.90 * base_p + 0.10 * float(neigh_mean)
                else:
                    reason.append("Q1 signal unreliable; avoid coverage-driven movement")

            elif target == "S1":
                if agree and nearest <= 3 and pd.notna(neigh_mean):
                    strength = 0.12
                    action = "TINY_MOVE"
                    reason.append("very close S1 neighbors agree; tiny only")
                    candidate_p = 0.92 * base_p + 0.08 * float(neigh_mean)
                else:
                    reason.append("S1 mostly subject/static; keep stable")

            elif target in {"S2", "S3"}:
                action = "FREEZE"
                strength = 0.0
                candidate_p = base_p
                reason.append(f"{target} is subject/static dominated; day-level features are brittle")

            # Decide up/down label for explanations.
            delta = candidate_p - base_p
            if abs(delta) < 0.015:
                direction = "HOLD"
            elif delta > 0:
                direction = "UP"
            else:
                direction = "DOWN"

            rows.append({
                "row_id": int(r.row_id),
                "subject_id": sid,
                "lifelog_date": r.lifelog_date,
                "regime": r.regime,
                "target": target,
                "action": action,
                "direction": direction,
                "strength": round(float(strength), 3),
                "base_subject_prior": round(base_p, 4),
                "candidate_hint_p": round(float(candidate_p), 4),
                "candidate_delta": round(float(delta), 4),
                "nearest_label_days": r.nearest_label_days,
                "coverage_anomaly_score": r.coverage_anomaly_score,
                "s4_context_token_count": int(r.s4_context_token_count),
                "reason": "; ".join(reason),
            })
    return pd.DataFrame(rows)


def write_report(profiles: pd.DataFrame, regime: pd.DataFrame, actions: pd.DataFrame):
    action_counts = actions.groupby(["target", "action"]).size().unstack(fill_value=0).reindex(LABELS)
    regime_counts = regime["regime"].value_counts().to_frame("n_rows")
    top_moves = actions[actions.action != "FREEZE"].sort_values(["strength", "target"], ascending=[False, True]).head(40)

    lines = []
    lines.append("# Subject/test-regime field notes\n")
    lines.append("No submission generated. This is a row/target action map for deciding what is allowed to move.\n")
    lines.append("## Easy glossary\n")
    lines.append("- **MOVE**: prediction may be changed meaningfully from the subject prior, because the row has specific evidence.\n")
    lines.append("- **TINY_MOVE**: prediction may move only a little; useful as a capped correction, not a new belief.\n")
    lines.append("- **FREEZE**: keep close to the stable subject/base prediction. This does **not** mean impossible to improve; it means current evidence says changing it is more likely to overfit than help.\n")
    lines.append("\n## Target rule in plain words\n")
    lines.append("- **Q2**: most movable. It is the best target for day-level clues like nearby labels, coverage, and deviation.\n")
    lines.append("- **Q3**: move only when neighbor-label grammar is clear, especially close prev/next labels agreeing.\n")
    lines.append("- **Q1**: mostly keep stable. Our current signals for Q1 are weak and coverage can mislead.\n")
    lines.append("- **S1**: mostly keep stable. Only tiny neighbor-based correction if very close evidence agrees.\n")
    lines.append("- **S2/S3**: freeze. These behave like subject/static-response targets more than day-behavior targets.\n")
    lines.append("- **S4**: tiny capped move only when strong context tokens appear.\n")
    lines.append("\n## Test regime counts\n")
    lines.append(regime_counts.to_markdown())
    lines.append("\n\n## Action counts by target\n")
    lines.append(action_counts.to_markdown())
    lines.append("\n\n## Top non-freeze row/target candidates\n")
    if len(top_moves):
        cols = ["row_id", "subject_id", "lifelog_date", "regime", "target", "action", "direction", "strength", "candidate_delta", "reason"]
        lines.append(top_moves[cols].to_markdown(index=False))
    else:
        lines.append("No non-freeze candidates.")
    lines.append("\n\n## Outputs\n")
    lines.append("- `experiments/subject_profile_cards.csv`\n")
    lines.append("- `experiments/test_regime_map.csv`\n")
    lines.append("- `experiments/target_action_map.csv`\n")
    (EXP / "subject_test_regime_field_notes_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    EXP.mkdir(exist_ok=True)
    train, test, coverage, tokens = load_inputs()
    profiles = subject_profile_cards(train, coverage, tokens)
    regime = build_test_regime_map(train, test, coverage, tokens)
    actions = build_action_map(train, regime)

    profiles.to_csv(EXP / "subject_profile_cards.csv", index=False)
    regime.to_csv(EXP / "test_regime_map.csv", index=False)
    actions.to_csv(EXP / "target_action_map.csv", index=False)
    write_report(profiles, regime, actions)

    print("Wrote:")
    for p in [
        EXP / "subject_profile_cards.csv",
        EXP / "test_regime_map.csv",
        EXP / "target_action_map.csv",
        EXP / "subject_test_regime_field_notes_report.md",
    ]:
        print("-", p.relative_to(ROOT))
    print("\nAction counts:")
    print(actions.groupby(["target", "action"]).size().unstack(fill_value=0).reindex(LABELS).fillna(0).astype(int))


if __name__ == "__main__":
    main()
