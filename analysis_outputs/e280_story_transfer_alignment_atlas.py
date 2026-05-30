#!/usr/bin/env python3
"""E280: story transfer and row-alignment atlas.

Public LB slots are scarce, so this audit treats existing human/social and
cash-flow stories as hypotheses, not candidate submissions. It asks:

1. Does a story carry local label/CV signal?
2. Is the story stable enough across train/test to transfer?
3. Does it align with the q-sleep row placement that looked real on train?
4. Does the mapped JEPA family look reconstructable rather than collapsed?
5. Did previous materializations fail because the story is weak, or because the
   action/gate was too small or placebo-sensitive?

No submission is produced by this script.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

SOCIAL_VERDICTS = OUT / "e268_human_social_story_verdicts.csv"
SOCIAL_FEATURES = OUT / "e268_human_social_story_features.parquet"
SOCIAL_CV = OUT / "e268_human_social_story_cv.csv"
SOCIAL_LABEL = OUT / "e268_human_social_story_label_probe.csv"

CASH_VERDICTS = OUT / "e270_payday_cashflow_story_verdicts.csv"
CASH_FEATURES = OUT / "e270_payday_cashflow_story_features.parquet"
CASH_CV = OUT / "e270_payday_cashflow_cv.csv"
CASH_LABEL = OUT / "e270_payday_cashflow_label_probe.csv"

E273_FAMILY = OUT / "e273_human_diary_state_jepa_audit_family_summary.csv"
E275_CELLS = OUT / "e275_q_sleep_diary_energy_amplitude_cells.csv"
E278_SUMMARY = OUT / "e278_train_row_alignment_null_summary.csv"
E279_SUMMARY = OUT / "e279_public_free_governor_summary.csv"

SUMMARY_OUT = OUT / "e280_story_transfer_alignment_summary.csv"
FAMILY_OUT = OUT / "e280_story_transfer_alignment_family_summary.csv"
CONTRADICTIONS_OUT = OUT / "e280_story_transfer_alignment_contradictions.csv"
NEXT_TESTS_OUT = OUT / "e280_story_transfer_alignment_next_tests.csv"
REPORT_OUT = OUT / "e280_story_transfer_alignment_report.md"


SOCIAL_FAMILY_MAP = {
    "social_overstim": "social_comm",
    "social_isolation": "social_comm",
    "social_outing": "social_comm",
    "sleep_fragment": "bedtime_phone",
    "cognitive_load": "cognitive_money",
    "media_binge": "media_game",
    "routine_anchor": "routine_calendar",
    "routine_break": "routine_calendar",
    "workday_commute": "mobility_context",
    "nightlife_mobility": "mobility_context",
    "calendar_social": "routine_calendar",
    "nextday_echo": "diary_global",
    "environment": "mobility_context",
    "physical_fatigue": "physiology_activity",
    "physiology_stress": "physiology_activity",
    "physiology_recovery": "physiology_activity",
    "sedentary_screen": "media_game",
    "measurement_state": "sensor_measurement",
}

CASH_FAMILY_MAP = {
    "post_pay_spend": "cognitive_money",
    "pre_pay_stress": "cognitive_money",
    "cashflow_transition": "cognitive_money",
    "bill_cycle": "cognitive_money",
    "calendar_only": "routine_calendar",
    "post_pay_relief": "routine_calendar",
}


def clip01(x: float) -> float:
    if not np.isfinite(x):
        return 0.0
    return float(np.clip(x, 0.0, 1.0))


def cohen_d(group: pd.Series, neutral: pd.Series) -> float:
    a = pd.to_numeric(group, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    b = pd.to_numeric(neutral, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(a) < 3 or len(b) < 3:
        return 0.0
    var = ((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / max(len(a) + len(b) - 2, 1)
    sd = float(np.sqrt(max(var, 1.0e-12)))
    return float((np.mean(a) - np.mean(b)) / sd)


def md_table(frame: pd.DataFrame, n: int = 25, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def load_story_tables() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    social = pd.read_csv(SOCIAL_VERDICTS).copy()
    social["source"] = "human_social"
    social["mapped_family"] = social["family"].map(SOCIAL_FAMILY_MAP).fillna("diary_global")
    social["anchor"] = ""
    social["phase"] = ""
    social = social.rename(columns={"subject_split_best_delta": "subject_best_delta"})

    cash = pd.read_csv(CASH_VERDICTS).copy()
    cash["source"] = "cashflow"
    cash["mapped_family"] = cash["family"].map(CASH_FAMILY_MAP).fillna("cognitive_money")

    common_cols = [
        "source",
        "story_id",
        "family",
        "mapped_family",
        "anchor",
        "phase",
        "human_story",
        "best_label_target",
        "best_label_abs_effect",
        "best_dateblock_target",
        "best_dateblock_delta",
        "subject_best_delta",
        "e247_only_d",
        "e256_only_d",
        "e247_vs_e256_d",
        "e267_moved_d",
        "train_test_gap",
        "public_align_score",
        "verdict",
    ]
    stories = pd.concat([social[common_cols], cash[common_cols]], ignore_index=True)

    features = {
        "human_social": pd.read_parquet(SOCIAL_FEATURES),
        "cashflow": pd.read_parquet(CASH_FEATURES),
    }
    for df in features.values():
        for col in ["sleep_date", "lifelog_date"]:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")

    cv = pd.concat(
        [
            pd.read_csv(SOCIAL_CV).assign(source="human_social"),
            pd.read_csv(CASH_CV).assign(source="cashflow"),
        ],
        ignore_index=True,
    )
    label = pd.concat(
        [
            pd.read_csv(SOCIAL_LABEL).assign(source="human_social"),
            pd.read_csv(CASH_LABEL).assign(source="cashflow"),
        ],
        ignore_index=True,
    )
    return stories, features, cv, label


def feature_stats(stories: pd.DataFrame, features: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cells = pd.read_csv(E275_CELLS)
    cells = cells[cells["candidate_id"].eq("q_sleep_amp_m160")].copy()
    for col in ["sleep_date", "lifelog_date"]:
        cells[col] = pd.to_datetime(cells[col]).dt.strftime("%Y-%m-%d")
    selected_any = set(map(tuple, cells[KEYS].drop_duplicates().to_numpy()))
    selected_q3 = set(map(tuple, cells[cells["target"].eq("Q3")][KEYS].drop_duplicates().to_numpy()))

    rows: list[dict[str, object]] = []
    for row in stories.itertuples(index=False):
        df = features[row.source]
        score_col = f"{row.story_id}_subj_z"
        if score_col not in df.columns:
            score_col = row.story_id if row.story_id in df.columns else ""
        if not score_col:
            rows.append({"source": row.source, "story_id": row.story_id, "score_col": "", "feature_available": False})
            continue

        score = pd.to_numeric(df[score_col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
        train = df["split"].eq("train")
        test = df["split"].eq("test")
        train_score = score[train]
        test_score = score[test]
        train_sd = float(train_score.std(ddof=0))
        if not np.isfinite(train_sd) or train_sd < 1.0e-9:
            train_sd = 1.0
        train_mean = float(train_score.mean())
        test_mean = float(test_score.mean())
        train_test_z_gap = abs(test_mean - train_mean) / train_sd

        test_keys = list(map(tuple, df.loc[test, KEYS].to_numpy()))
        selected_any_mask = pd.Series([key in selected_any for key in test_keys], index=df.index[test])
        selected_q3_mask = pd.Series([key in selected_q3 for key in test_keys], index=df.index[test])
        test_score_indexed = score[test]
        any_d = cohen_d(test_score_indexed[selected_any_mask], test_score_indexed[~selected_any_mask])
        q3_d = cohen_d(test_score_indexed[selected_q3_mask], test_score_indexed[~selected_q3_mask])
        high_cut = float(train_score.quantile(0.80))
        high_test_rate = float((test_score >= high_cut).mean())
        high_train_rate = float((train_score >= high_cut).mean())

        rows.append(
            {
                "source": row.source,
                "story_id": row.story_id,
                "score_col": score_col,
                "feature_available": True,
                "score_train_mean": train_mean,
                "score_test_mean": test_mean,
                "score_train_sd": train_sd,
                "score_train_test_z_gap": train_test_z_gap,
                "score_high_train_rate": high_train_rate,
                "score_high_test_rate": high_test_rate,
                "e275_qsleep_selected_any_d": any_d,
                "e275_qsleep_selected_q3_d": q3_d,
            }
        )
    return pd.DataFrame(rows)


def cv_label_stats(cv: pd.DataFrame, label: pd.DataFrame) -> pd.DataFrame:
    cv_rows = []
    for (source, story_id), sub in cv.groupby(["source", "story_id"]):
        date = sub[sub["split"].astype(str).str.contains("dateblock", na=False)]
        subj = sub[sub["split"].astype(str).str.contains("subject", na=False)]
        cv_rows.append(
            {
                "source": source,
                "story_id": story_id,
                "cv_delta_min": float(sub["delta_logloss"].min()),
                "cv_delta_mean": float(sub["delta_logloss"].mean()),
                "cv_negative_rate": float((sub["delta_logloss"] < 0).mean()),
                "cv_dateblock_min": float(date["delta_logloss"].min()) if not date.empty else np.nan,
                "cv_subject_min": float(subj["delta_logloss"].min()) if not subj.empty else np.nan,
                "cv_best_target": str(sub.sort_values("delta_logloss").iloc[0]["target"]),
            }
        )
    cv_stat = pd.DataFrame(cv_rows)

    label_rows = []
    for (source, story_id), sub in label.groupby(["source", "story_id"]):
        best = sub.sort_values("abs_effect", ascending=False).iloc[0]
        label_rows.append(
            {
                "source": source,
                "story_id": story_id,
                "label_best_variant": best.get("variant", ""),
                "label_best_target": best["target"],
                "label_best_signed_effect": float(best.get("high_minus_low", np.nan)),
                "label_best_abs_effect": float(best["abs_effect"]),
                "label_abs_effect_mean_top5": float(sub.sort_values("abs_effect", ascending=False).head(5)["abs_effect"].mean()),
            }
        )
    return cv_stat.merge(pd.DataFrame(label_rows), on=["source", "story_id"], how="outer")


def family_train_support() -> pd.DataFrame:
    e278 = pd.read_csv(E278_SUMMARY)
    rows = []
    families = sorted({str(f) for f in e278["family"].dropna().unique() if str(f)})
    families.extend(["diary_global"])
    families = sorted(set(families))
    for family in families:
        only = e278[e278["candidate_id"].eq(f"only_{family}")]
        leave = e278[e278["candidate_id"].eq(f"no_{family}")]
        pieces = []
        if not only.empty:
            pieces.append(("only", only))
        if not leave.empty:
            pieces.append(("leaveout", leave))
        out = {
            "mapped_family": family,
            "e278_only_gate_count": int(only["train_align_gate"].fillna(False).sum()) if not only.empty else 0,
            "e278_leaveout_gate_count": int(leave["train_align_gate"].fillna(False).sum()) if not leave.empty else 0,
            "e278_only_actual_delta_mean": float(only["actual_delta"].mean()) if not only.empty else np.nan,
            "e278_leaveout_actual_delta_mean": float(leave["actual_delta"].mean()) if not leave.empty else np.nan,
            "e278_only_min_dominance": float(only["dominance"].min()) if not only.empty else np.nan,
            "e278_leaveout_min_dominance": float(leave["dominance"].min()) if not leave.empty else np.nan,
        }
        if pieces:
            all_part = pd.concat([p[1] for p in pieces], ignore_index=True)
            out["e278_any_train_gate"] = bool(all_part["train_align_gate"].fillna(False).any())
            out["e278_best_actual_delta"] = float(all_part["actual_delta"].min())
            out["e278_best_dominance"] = float(all_part["dominance"].max())
        else:
            out["e278_any_train_gate"] = False
            out["e278_best_actual_delta"] = np.nan
            out["e278_best_dominance"] = np.nan
        rows.append(out)
    return pd.DataFrame(rows)


def jepa_family_stats() -> pd.DataFrame:
    fam = pd.read_csv(E273_FAMILY)
    ctx = fam[fam["split"].notna()].copy()
    rows = []
    for family, sub in ctx.groupby("family"):
        train_resid = float(sub["resid_train_mean"].mean())
        test_resid = float(sub["resid_test_mean"].mean())
        rows.append(
            {
                "mapped_family": family,
                "jepa_context_oof_r2_mean": float(sub["oof_r2"].mean()),
                "jepa_context_oof_r2_min": float(sub["oof_r2"].min()),
                "jepa_resid_train_mean": train_resid,
                "jepa_resid_test_mean": test_resid,
                "jepa_resid_gap_ratio": abs(test_resid - train_resid) / max(abs(train_resid), 1.0e-9),
            }
        )
    return pd.DataFrame(rows)


def e279_materialization_context() -> dict[str, object]:
    e279 = pd.read_csv(E279_SUMMARY)
    active = e279[~e279["final_governor_decision"].eq("current_anchor")].copy()
    return {
        "audited_candidates": int(len(e279)),
        "submission_ready": int(e279["public_free_submission_ready"].fillna(False).sum()),
        "matched_placebo_gate_passes": int(e279["matched_placebo_gate"].fillna(False).sum()),
        "social_tiny_candidates": int(active["basename"].astype(str).str.contains("e269").sum()),
        "cashflow_tiny_candidates": int(active["basename"].astype(str).str.contains("e271").sum()),
        "qsleep_blocked_by_placebo": int(active["final_governor_decision"].astype(str).str.contains("matched_placebo").sum()),
    }


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["label_score"] = out["best_label_abs_effect"].map(lambda x: clip01(float(x) / 0.22))
    out["cv_score"] = [
        clip01((max(0.0, -float(d if np.isfinite(d) else 0.0)) / 0.012 + max(0.0, -float(s if np.isfinite(s) else 0.0)) / 0.025) / 2.0)
        for d, s in zip(out["best_dateblock_delta"], out["subject_best_delta"])
    ]
    out["stability_score"] = out["score_train_test_z_gap"].map(lambda x: clip01(1.0 - float(x) / 0.35))
    out["family_support_score"] = [
        clip01(0.75 * (1.0 if only > 0 else 0.0) + 0.25 * (1.0 if leave > 0 else 0.0))
        for only, leave in zip(out["e278_only_gate_count"].fillna(0), out["e278_leaveout_gate_count"].fillna(0))
    ]
    out["jepa_context_score"] = out["jepa_context_oof_r2_mean"].fillna(0.0).map(lambda x: clip01((float(x) + 0.10) / 1.05))
    out["e275_row_alignment_score"] = out["e275_qsleep_selected_q3_d"].fillna(0.0).abs().map(lambda x: clip01(float(x) / 0.80))
    out["public_sensor_score"] = out["public_align_score"].fillna(0.0).map(lambda x: clip01(float(x) / 1.50))

    out["transfer_survival_score"] = (
        0.24 * out["label_score"]
        + 0.24 * out["cv_score"]
        + 0.18 * out["stability_score"]
        + 0.14 * out["family_support_score"]
        + 0.10 * out["jepa_context_score"]
        + 0.07 * out["e275_row_alignment_score"]
        + 0.03 * out["public_sensor_score"]
    )

    verdicts = []
    next_actions = []
    for row in out.itertuples(index=False):
        if row.stability_score < 0.20:
            verdict = "blocked_transfer_gap"
            action = "Normalize by subject/block or discard as a direct gate."
        elif row.label_score < 0.35 and row.cv_score < 0.20:
            verdict = "weak_local_signal"
            action = "Keep only as a narrative prior, not as a feature/action."
        elif row.public_sensor_score > 0.65 and row.cv_score < 0.30:
            verdict = "public_anchor_diagnostic_only"
            action = "Use to interpret old public-boundary behavior, not to create a submission."
        elif row.cv_score >= 0.45 and row.label_score >= 0.50 and row.family_support_score >= 0.50:
            verdict = "alive_for_story_state_gate"
            action = "Build a row selector and require matched row/subject/dateblock null survival."
        elif row.cv_score >= 0.35 and row.label_score >= 0.45:
            verdict = "alive_but_needs_transfer_test"
            action = "Run a masked context->story-state test before any materialization."
        else:
            verdict = "diagnostic_story_only"
            action = "Use for hypothesis graph and slice analysis only."
        verdicts.append(verdict)
        next_actions.append(action)
    out["e280_verdict"] = verdicts
    out["next_public_free_test"] = next_actions
    return out.sort_values("transfer_survival_score", ascending=False).reset_index(drop=True)


def make_family_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, sub in summary.groupby("mapped_family"):
        rows.append(
            {
                "mapped_family": family,
                "n_stories": int(len(sub)),
                "max_transfer_survival_score": float(sub["transfer_survival_score"].max()),
                "mean_transfer_survival_score": float(sub["transfer_survival_score"].mean()),
                "alive_story_state_gate_n": int(sub["e280_verdict"].eq("alive_for_story_state_gate").sum()),
                "alive_needs_transfer_test_n": int(sub["e280_verdict"].eq("alive_but_needs_transfer_test").sum()),
                "blocked_transfer_gap_n": int(sub["e280_verdict"].eq("blocked_transfer_gap").sum()),
                "top_story_id": str(sub.sort_values("transfer_survival_score", ascending=False).iloc[0]["story_id"]),
                "top_story_human": str(sub.sort_values("transfer_survival_score", ascending=False).iloc[0]["human_story"]),
                "e278_only_gate_count": int(sub["e278_only_gate_count"].fillna(0).max()),
                "jepa_context_oof_r2_mean": float(sub["jepa_context_oof_r2_mean"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["alive_story_state_gate_n", "max_transfer_survival_score"], ascending=False)


def make_next_tests(summary: pd.DataFrame) -> pd.DataFrame:
    alive = summary[summary["e280_verdict"].isin(["alive_for_story_state_gate", "alive_but_needs_transfer_test"])].copy()
    alive = alive.sort_values("transfer_survival_score", ascending=False)
    rows = []
    for _, row in alive.head(12).iterrows():
        rows.append(
            {
                "priority": len(rows) + 1,
                "story_id": row["story_id"],
                "source": row["source"],
                "mapped_family": row["mapped_family"],
                "test_name": f"masked_context_to_{row['mapped_family']}_story_state",
                "belief_that_can_die": "Story row placement transfers from train hidden state to test hidden state.",
                "success_rule": "OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed.",
                "do_not_do": "Do not create a direct Q3 boundary edit from this story alone.",
                "transfer_survival_score": row["transfer_survival_score"],
                "reason": row["next_public_free_test"],
            }
        )
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame(
        [
            {
                "priority": 1,
                "story_id": "",
                "source": "",
                "mapped_family": "",
                "test_name": "no_story_submission",
                "belief_that_can_die": "Existing story set is insufficient for transfer.",
                "success_rule": "A new story must beat current atlas thresholds before materialization.",
                "do_not_do": "Do not submit a tiny public-boundary gate.",
                "transfer_survival_score": 0.0,
                "reason": "No story passed the E280 alive criteria.",
            }
        ]
    )


def write_report(summary: pd.DataFrame, family: pd.DataFrame, contradictions: pd.DataFrame, next_tests: pd.DataFrame) -> None:
    ctx = e279_materialization_context()
    alive = summary[summary["e280_verdict"].eq("alive_for_story_state_gate")]
    needs = summary[summary["e280_verdict"].eq("alive_but_needs_transfer_test")]
    blocked_gap = summary[summary["e280_verdict"].eq("blocked_transfer_gap")]
    diagnostic_public = summary[summary["e280_verdict"].eq("public_anchor_diagnostic_only")]

    lines = [
        "# E280 Story Transfer and Row-Alignment Atlas",
        "",
        "## Question",
        "",
        "Public LB cannot be used as the iteration loop. The question here is whether the human/social and payday stories are transferable hidden-state signals or only public-boundary diagnostics.",
        "",
        "## Method",
        "",
        "- Combine E268 human/social stories and E270 payday/cash-flow stories.",
        "- Score each story by label lift, blocked CV delta, train/test feature stability, E278 train row-alignment support, E273 JEPA family reconstructability, and E275 q-sleep row overlap.",
        "- Treat E247/E256/E267 movement alignment as a weak diagnostic only, not as a promotion rule.",
        "- Produce no submission file.",
        "",
        "## Public-Free Guardrail",
        "",
        f"- E279 audited candidates: `{ctx['audited_candidates']}`",
        f"- E279 submission-ready candidates: `{ctx['submission_ready']}`",
        f"- E279 matched-placebo gate passes: `{ctx['matched_placebo_gate_passes']}`",
        f"- prior social direct gates in E269: `{ctx['social_tiny_candidates']}` tiny/materialization candidates",
        f"- prior cash-flow direct gates in E271: `{ctx['cashflow_tiny_candidates']}` tiny/materialization candidates",
        f"- q-sleep candidates blocked by matched placebo: `{ctx['qsleep_blocked_by_placebo']}`",
        "",
        "Read: a story can be real and still not be submission-ready. Direct row edits remain blocked unless they beat matched row/subject/dateblock nulls.",
        "",
        "## Summary Counts",
        "",
        f"- total stories audited: `{len(summary)}`",
        f"- alive for story-state gate: `{len(alive)}`",
        f"- alive but needs transfer test: `{len(needs)}`",
        f"- blocked by train/test transfer gap: `{len(blocked_gap)}`",
        f"- public-anchor diagnostic only: `{len(diagnostic_public)}`",
        "",
        "## Top Transfer Stories",
        "",
        md_table(
            summary[
                [
                    "story_id",
                    "source",
                    "mapped_family",
                    "transfer_survival_score",
                    "e280_verdict",
                    "best_label_target",
                    "best_label_abs_effect",
                    "best_dateblock_delta",
                    "subject_best_delta",
                    "score_train_test_z_gap",
                    "e275_qsleep_selected_q3_d",
                    "jepa_context_oof_r2_mean",
                ]
            ],
            n=20,
        ),
        "",
        "## Family-Level Read",
        "",
        md_table(
            family[
                [
                    "mapped_family",
                    "n_stories",
                    "alive_story_state_gate_n",
                    "alive_needs_transfer_test_n",
                    "blocked_transfer_gap_n",
                    "max_transfer_survival_score",
                    "top_story_id",
                    "e278_only_gate_count",
                    "jepa_context_oof_r2_mean",
                ]
            ],
            n=20,
        ),
        "",
        "## Main Contradictions",
        "",
        md_table(
            contradictions[
                [
                    "story_id",
                    "source",
                    "mapped_family",
                    "contradiction_type",
                    "transfer_survival_score",
                    "best_label_abs_effect",
                    "best_dateblock_delta",
                    "score_train_test_z_gap",
                    "public_align_score",
                    "e280_verdict",
                ]
            ],
            n=20,
        ),
        "",
        "## Next Public-Free Tests",
        "",
        md_table(next_tests, n=12),
        "",
        "## Decision",
        "",
        "No submission is recommended from E280. The strongest surviving direction is not a tiny public-boundary edit; it is a masked context-to-story-state row selector whose row placement must beat matched nulls before public LB is touched.",
        "",
        "## Files",
        "",
        "- `e280_story_transfer_alignment_summary.csv`",
        "- `e280_story_transfer_alignment_family_summary.csv`",
        "- `e280_story_transfer_alignment_contradictions.csv`",
        "- `e280_story_transfer_alignment_next_tests.csv`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    stories, features, cv, label = load_story_tables()
    stats = feature_stats(stories, features)
    cv_label = cv_label_stats(cv, label)
    train_support = family_train_support()
    jepa_stats = jepa_family_stats()

    merged = stories.merge(stats, on=["source", "story_id"], how="left")
    merged = merged.merge(cv_label, on=["source", "story_id"], how="left")
    merged = merged.merge(train_support, on="mapped_family", how="left")
    merged = merged.merge(jepa_stats, on="mapped_family", how="left")
    summary = add_scores(merged)

    contradiction_rows = []
    for _, row in summary.iterrows():
        if row["best_label_abs_effect"] >= 0.18 and row["score_train_test_z_gap"] >= 0.35:
            ctype = "strong_label_but_transfer_gap"
        elif row["public_align_score"] >= 1.0 and row["cv_score"] < 0.30:
            ctype = "public_sensor_without_local_cv"
        elif row["cv_score"] >= 0.50 and row["family_support_score"] < 0.50:
            ctype = "local_cv_without_qsleep_family_support"
        elif abs(row["e275_qsleep_selected_q3_d"]) >= 0.80 and row["cv_score"] < 0.35:
            ctype = "aligns_qsleep_rows_but_weak_local_cv"
        else:
            continue
        item = row.to_dict()
        item["contradiction_type"] = ctype
        contradiction_rows.append(item)
    contradictions = pd.DataFrame(contradiction_rows)
    if contradictions.empty:
        contradictions = summary.head(0).copy()
        contradictions["contradiction_type"] = []
    else:
        contradictions = contradictions.sort_values("transfer_survival_score", ascending=False)

    family = make_family_summary(summary)
    next_tests = make_next_tests(summary)

    summary.to_csv(SUMMARY_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    contradictions.to_csv(CONTRADICTIONS_OUT, index=False)
    next_tests.to_csv(NEXT_TESTS_OUT, index=False)
    write_report(summary, family, contradictions, next_tests)

    print(f"stories={len(summary)}")
    print(f"alive_for_story_state_gate={int(summary['e280_verdict'].eq('alive_for_story_state_gate').sum())}")
    print(f"alive_but_needs_transfer_test={int(summary['e280_verdict'].eq('alive_but_needs_transfer_test').sum())}")
    print(f"blocked_transfer_gap={int(summary['e280_verdict'].eq('blocked_transfer_gap').sum())}")
    print(f"top_story={summary.iloc[0]['story_id']} score={summary.iloc[0]['transfer_survival_score']:.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
