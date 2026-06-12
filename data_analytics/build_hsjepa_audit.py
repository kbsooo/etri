#!/usr/bin/env python3
"""Build a Data Analytics audit package for the HS-JEPA competition work.

The goal is not to produce a new submission.  It creates source-backed score,
data, and experiment summaries that can be read by teammates and rendered by
the Data Analytics artifact app.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_analytics"
TODAY = "2026-06-12"


LATE_PUBLIC_OBSERVATIONS = [
    {
        "file": "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
        "public_lb": 0.5679048248,
        "note": "Q2 phase route. README/lb log records this as the first post-public-equation Q2-support improvement.",
        "family": "HS-JEPA public equation",
        "worldview": "Q2 changed rows are a public-visible state marker.",
        "source": "README.md and lb_observation_log.md",
        "observed_stage": "H042",
    },
    {
        "file": "submission_h050_target_route_phase_b140216b_uploadsafe.csv",
        "public_lb": 0.5679048248,
        "note": "Subjective route expansion tied the Q2 phase route despite adding Q1/Q3 route cells; the target route was plausible but row placement was not.",
        "family": "HS-JEPA target route stress",
        "worldview": "Subjective Q route alone is not enough unless row support is correct.",
        "source": "README.md and lb_observation_log.md",
        "observed_stage": "H050",
    },
    {
        "file": "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
        "public_lb": 0.5677475939,
        "note": "Row-state vector frontier. It freezes Q2 and moves Q1/Q3/S1-S4 on the 45 Q2-support rows.",
        "family": "HS-JEPA row-state decoder",
        "worldview": "Q2-support rows encode a complete hidden human-state vector.",
        "source": "README.md, lb_observation_log.md, hs_jepa_end_to_end_report.md",
        "observed_stage": "H057",
    },
    {
        "file": "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        "public_lb": 0.5684942019,
        "note": "Negative sensor. Dual-head Pareto gate looked coherent locally but public punished the broad action field.",
        "family": "HS-JEPA action toxicity stress",
        "worldview": "Hard-world is a stress diagnostic, not an action-grade private head.",
        "source": "lb_observation_log.md and h088_report.md",
        "observed_stage": "H088",
    },
    {
        "file": "submission_h144_targetxor_def80b88_uploadsafe.csv",
        "public_lb": 0.5679296410,
        "note": "Target-split XOR tie sensor. Public tied the Q3 repair-only branch, so the branch distinction did not explain the loss.",
        "family": "HS-JEPA target assignment stress",
        "worldview": "The common target-assignment body is below the row-state frontier; row135/row207 split is not the decisive axis.",
        "source": "lb_observation_log.md and h144_report.md",
        "observed_stage": "H144",
    },
    {
        "file": "submission_h145_q3repair_2d818e46_uploadsafe.csv",
        "public_lb": 0.5679296410,
        "note": "Q3 repair-only veto tied the target-split XOR branch exactly at displayed precision.",
        "family": "HS-JEPA target assignment stress",
        "worldview": "Q3-only repair versus S2 relief is underidentified; the shared body is the public-loss source.",
        "source": "lb_observation_log.md and h145_report.md",
        "observed_stage": "H145",
    },
    {
        "file": "submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv",
        "public_lb": 0.5684860446,
        "note": "Cross-listener transport sensor. Listener-confirmed shadow cells were locally coherent but public did not reward the listener-calibrated release.",
        "family": "HS-JEPA cross-listener transport",
        "worldview": "Target-listener posterior is useful as a diagnostic, but listener-confirmed shadow release is not enough to beat the row-state action field.",
        "source": "user-provided public LB on 2026-06-11 and cross_listener_transport_readout.md",
        "observed_stage": "CrossListener",
    },
]


SEMANTIC_STAGE_LABELS = {
    "H012": "public-equation jump",
    "H042": "Q2 phase route",
    "H050": "subjective route expansion",
    "H057": "row-state vector frontier",
    "H088": "dual-head toxicity stress",
    "H144": "target-split XOR stress",
    "H145": "Q3 repair-only stress",
    "FrontierSilence": "frontier active-silence",
    "CrossListener": "cross-listener transport",
}


DAILY_REPORTS = {
    "2026-06-04": {
        "title": "2026-06-04 HS-JEPA 점수 센서 정리",
        "summary": "public-equation jump, Q2 phase route, row-state vector frontier는 public LB를 직접 최적화한 파일이 아니라, public-visible hidden state를 점점 더 정확히 좁힌 sensor로 해석해야 한다.",
        "findings": [
            "public-equation jump는 pre-HS feature-NN frontier 대비 약 0.0080을 줄여 단순 모델 개선보다 훨씬 큰 구조 발견임을 보였다.",
            "Q2 phase route와 subjective route expansion은 같은 0.5679048248에 묶여, Q2 support는 맞았지만 Q1/Q3 route만 추가하는 방식은 부족하다는 신호를 줬다.",
            "row-state vector frontier는 Q2를 freeze한 채 45개 row에서 non-Q2 전체 벡터를 움직여 0.5677475939까지 내려갔다. 이는 row 자체가 hidden human-state라는 해석을 강화한다.",
        ],
        "next_action": "row-state vector frontier의 45개 row를 seed로 보되, 무작정 확장하지 말고 public-toxic action을 분리하는 decoder를 우선한다.",
    },
    "2026-06-05": {
        "title": "2026-06-05 HS-JEPA 병목 재정의",
        "summary": "dual-head toxicity stress와 target-assignment stress는 숨은 상태를 찾는 문제보다, 그 상태를 안전한 row-target action으로 번역하는 문제가 병목임을 보여준다.",
        "findings": [
            "dual-head toxicity stress는 로컬 Pareto gate가 좋아 보여도 public LB가 0.5684942019로 후퇴했다. hard-world head는 action head가 아니라 toxic/collapse stress로 써야 한다.",
            "target-split XOR와 Q3 repair-only stress가 둘 다 0.567929641에 묶인 것은 target-level micro-branch보다 공통 action body가 문제였다는 뜻이다.",
            "V131C식 cohort-relative anomaly는 좋은 context view지만, 바로 Q2/Q3/S2를 보정하는 decoder가 아니라 HS-JEPA의 action-health 입력으로 들어가야 한다.",
        ],
        "next_action": "Cohort-relative outlier, human-social route, source responsibility를 모두 action-health/assignment solver 입력으로 통합한다.",
    },
    "2026-06-07": {
        "title": "2026-06-07 현재 상태와 재현성 점검",
        "summary": "오늘 기준으로 가장 강한 산출물은 최고점 제출을 재현하는 end-to-end HS-JEPA 코드와, 이후 실험들이 왜 row-state vector frontier를 크게 넘지 못했는지 설명하는 negative sensor ledger다.",
        "findings": [
            "hs_jepa_end_to_end.py는 row-state vector frontier hash 7cde1a77을 재현하고, 45 hidden row와 270 row-target action을 cell-level로 설명한다.",
            "Gemini embedding 실험은 narrative latent 가능성을 보였지만, 오픈소스 재현성 때문에 논문/팀 공유용 핵심 경로에서는 제외해야 한다.",
            "다음 breakthrough는 더 큰 blend가 아니라 safe assignment field다. row-state seed를 유지하면서 cohort outlier나 social latent가 어느 target action에 안전한지 판별해야 한다.",
        ],
        "next_action": "오픈소스 semantic/cohort encoder를 HS-JEPA context view로 만들고, public-toxic 방향과 H057-positive 방향을 동시에 보는 row-target solver를 설계한다.",
    },
    "2026-06-11": {
        "title": "2026-06-11 Cross-Listener Transport 결과 해석",
        "summary": "Cross-listener transport는 listener posterior를 직접 action generator가 아니라 boundary prior로 쓰는 실험이었지만, public LB 0.5684860446으로 row-state frontier를 넘지 못했다.",
        "findings": [
            "점수는 H088 0.5684942019와 거의 같은 손실대다. 즉 listener-calibrated shadow release는 broad Pareto/hard-world gate와 비슷한 public-toxic action 폭을 가진다.",
            "Direct listener-lift 0.5680255019보다는 나빠졌기 때문에, target-listener posterior를 안전한 release gate로 바꾸는 현재 transport 식은 충분하지 않다.",
            "다만 0.570+로 붕괴하지 않았으므로 listener가 완전히 무의미한 것은 아니다. listener는 action 생성기나 최종 gate가 아니라, strict jury/core-health 후보의 diagnostic feature로 남기는 게 맞다.",
        ],
        "next_action": "다음 big bet은 listener 추가가 아니라, row-state-positive action과 listener/toxicity가 충돌하는 cell을 명시적으로 금지하는 anti-listener toxicity field를 만든다.",
    },
    "2026-06-12": {
        "title": "2026-06-12 Frontier Active-Silence 센서 해석",
        "summary": "frontier active-silence positive-path는 0.5677269444로 새 public best를 만들었지만, 이 결과는 breakthrough라기보다 row-state frontier 근처의 보수적 continuation이 아직 조금 남아 있음을 보여준다.",
        "findings": [
            "active-silence positive-path는 이전 row-state vector frontier 대비 약 0.00002065를 줄였다. active silence를 action-health의 일부로 보는 가설은 살아 있다.",
            "개선 폭이 매우 작기 때문에 0.53급 도약을 설명하지는 못한다. 현재 방향은 hidden-state 구조 발견이라기보다 frontier-local trajectory continuation이다.",
            "따라서 다음 실험은 current best를 anchor로 삼아 근처를 미세 조정하는 방식이 아니라, 여러 positive/negative listener world에서 fresh row-target field를 합성하는 anchor-free transport가 되어야 한다.",
        ],
        "next_action": "semantic naming을 고정하고, row-state frontier를 하나의 listener로만 취급하는 anchor-free state transport solver를 만든다.",
    },
}


def read_public_score_ledger() -> pd.DataFrame:
    base_path = ROOT / "analysis_outputs" / "public_probe_observations.csv"
    base = pd.read_csv(base_path)
    base["family"] = base["file"].map(classify_family)
    base["worldview"] = base["note"].map(short_worldview_from_note)
    base["source"] = "analysis_outputs/public_probe_observations.csv"
    base["observed_stage"] = base["file"].map(stage_from_file)
    late = pd.DataFrame(LATE_PUBLIC_OBSERVATIONS)
    ledger = pd.concat([base, late], ignore_index=True)
    ledger = ledger.drop_duplicates(subset=["file"], keep="last")
    ledger["sequence"] = range(1, len(ledger) + 1)
    ledger["best_so_far"] = ledger["public_lb"].cummin()
    prev_best = ledger["best_so_far"].shift(1)
    ledger["delta_vs_previous_best"] = ledger["public_lb"] - prev_best
    ledger.loc[ledger["delta_vs_previous_best"].isna(), "delta_vs_previous_best"] = 0.0
    ledger["improved_previous_best"] = ledger["public_lb"] < prev_best.fillna(math.inf)
    ledger["score_rank"] = ledger["public_lb"].rank(method="min", ascending=True).astype(int)
    ledger["public_lb_display"] = ledger["public_lb"].map(lambda x: f"{x:.10f}")
    ledger["delta_display"] = ledger["delta_vs_previous_best"].map(lambda x: f"{x:+.10f}")
    ledger["semantic_stage"] = ledger["observed_stage"].map(lambda x: SEMANTIC_STAGE_LABELS.get(str(x), str(x)))
    return ledger


def classify_family(filename: str) -> str:
    text = filename.lower()
    if "frontier_silence" in text or "frontier_trajectory" in text:
        return "HS-JEPA frontier active-silence"
    if "cross_listener_transport" in text:
        return "HS-JEPA cross-listener transport"
    if "h057" in text:
        return "HS-JEPA row-state"
    if "h012" in text or "public_equation" in text:
        return "HS-JEPA public equation"
    if "h042" in text or "q2_phase" in text:
        return "HS-JEPA Q2 phase"
    if "h088" in text or "dual" in text:
        return "HS-JEPA toxicity stress"
    if "h144" in text or "h145" in text or "xor" in text or "repair" in text:
        return "HS-JEPA assignment stress"
    if "jepa" in text or "lejepa" in text:
        return "Direct JEPA/LeJEPA"
    if "human" in text or "social" in text:
        return "Human-social latent"
    if "e247" in text or "featnn" in text:
        return "Feature NN smoothing"
    return "Pre-HS baseline / other"


def short_worldview_from_note(note: str) -> str:
    note = str(note)
    if "validates" in note:
        return note.split("validates", 1)[-1].strip()[:140]
    if "reject" in note:
        return note.split("reject", 1)[-1].strip()[:140]
    return note[:140]


def stage_from_file(filename: str) -> str:
    text = filename.lower()
    if "frontier_silence" in text or "frontier_trajectory" in text:
        return "FrontierSilence"
    if "cross_listener_transport" in text:
        return "CrossListener"
    m = re.search(r"submission_([a-z]?\d+|h\d+|e\d+)", filename.lower())
    if m:
        return m.group(1).upper()
    return "other"


def build_data_inventory() -> pd.DataFrame:
    rows = []
    for path in sorted((ROOT / "data").rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix == ".csv":
            df = pd.read_csv(path)
            rows.append(
                {
                    "source": rel,
                    "kind": "csv",
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "column_sample": ", ".join(df.columns[:8]),
                }
            )
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path)
            rows.append(
                {
                    "source": rel,
                    "kind": "parquet",
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "column_sample": ", ".join(df.columns[:8]),
                }
            )
    return pd.DataFrame(rows)


def build_target_inventory() -> pd.DataFrame:
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    targets = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
    rows = []
    for target in targets:
        s = train[target]
        rows.append(
            {
                "target": target,
                "positive_rate": float(s.mean()),
                "positives": int(s.sum()),
                "negatives": int((1 - s).sum()),
                "rows": int(len(s)),
                "interpretation": target_interpretation(target),
            }
        )
    return pd.DataFrame(rows)


def target_interpretation(target: str) -> str:
    return {
        "Q1": "subjective satisfaction",
        "Q2": "sleep intervention/friction",
        "Q3": "subjective quality",
        "S1": "objective stage ratio",
        "S2": "objective stage ratio",
        "S3": "objective stage ratio",
        "S4": "objective stage ratio",
    }[target]


def build_experiment_inventory() -> pd.DataFrame:
    rows = []
    for p in (ROOT / "hitl").glob("h*_*/h*_decision.csv"):
        try:
            df = pd.read_csv(p)
        except Exception:
            continue
        h = p.parent.name.split("_", 1)[0].upper()
        rec = {
            "stage": h,
            "path": p.relative_to(ROOT).as_posix(),
            "decision_rows": int(len(df)),
            "columns": int(len(df.columns)),
        }
        for col in [
            "changed_cells_vs_h057",
            "changed_rows_vs_h057",
            "selected_cells",
            "selected_rows",
            "root_upload_safe",
            "upload_safe",
            "worldview",
            "decision",
            "spec",
        ]:
            if col in df.columns:
                rec[col] = df.iloc[0][col]
        rows.append(rec)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["stage_num"] = out["stage"].str.extract(r"(\d+)").astype(int)
        out = out.sort_values("stage_num")
    return out


def build_day_file_inventory() -> pd.DataFrame:
    rows = []
    for p in ROOT.glob("submission_h*.csv"):
        st = p.stat()
        day = pd.to_datetime(st.st_mtime, unit="s").strftime("%Y-%m-%d")
        rows.append({"date": day, "file_type": "root_submission", "count": 1})
    for p in (ROOT / "hitl").rglob("h*_report.md"):
        st = p.stat()
        day = pd.to_datetime(st.st_mtime, unit="s").strftime("%Y-%m-%d")
        rows.append({"date": day, "file_type": "hitl_report", "count": 1})
    if not rows:
        return pd.DataFrame(columns=["date", "file_type", "count"])
    return pd.DataFrame(rows).groupby(["date", "file_type"], as_index=False)["count"].sum()


def write_markdown(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 12) -> str:
    view = df[columns].head(max_rows).copy()
    headers = [str(c) for c in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        values = [str(row[c]).replace("\n", " ").replace("|", "/") for c in view.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_daily_reports(ledger: pd.DataFrame, inventory: pd.DataFrame, experiments: pd.DataFrame) -> None:
    best = ledger.sort_values("public_lb").head(8)
    best_public = ledger.sort_values("public_lb").iloc[0]
    for day, meta in DAILY_REPORTS.items():
        body = f"""# {meta['title']}

## Executive Summary

**핵심 판단:** {meta['summary']}

**현재 public best:** `{best_public['file']}` = `{best_public['public_lb_display']}`

## 점수 근거

{markdown_table(best, ['score_rank', 'semantic_stage', 'file', 'public_lb_display', 'delta_display', 'family'], 8)}

## 분석 결과

"""
        for item in meta["findings"]:
            body += f"- {item}\n"
        body += f"""
## 데이터/실험 범위

- 원본 metric train: `{int(inventory.loc[inventory['source'].eq('data/ch2026_metrics_train.csv'), 'rows'].iloc[0])}` rows.
- test/sample submission: `{int(inventory.loc[inventory['source'].eq('data/ch2026_submission_sample.csv'), 'rows'].iloc[0])}` rows.
- raw lifelog parquet sources: `{int((inventory['kind'] == 'parquet').sum())}` files.
- HITL decision files reviewed: `{len(experiments)}`.

## 다음 행동

{meta['next_action']}

## Caveat

이 문서는 repo 안에 기록된 public LB, README/lb log, decision/report 산출물만 사용한다. 실제 private LB나 미기록 제출 결과는 포함하지 않는다.
"""
        write_markdown(OUT / f"{day}_hsjepa_audit.md", body)


def build_manifest_and_snapshot(
    ledger: pd.DataFrame,
    inventory: pd.DataFrame,
    targets: pd.DataFrame,
    experiments: pd.DataFrame,
    day_inventory: pd.DataFrame,
) -> tuple[dict, dict]:
    best_public = ledger.sort_values("public_lb").iloc[0]
    best_file = str(best_public["file"])
    best_score = str(best_public["public_lb_display"])

    def dataset_source(dataset_file: str, description: str, metric_definitions: list[str]) -> dict:
        csv_path = (OUT / dataset_file).as_posix()
        return {
            "label": dataset_file,
            "path": csv_path,
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "description": description,
                "sql": f"SELECT * FROM read_csv_auto('{csv_path}');",
                "tables_used": [csv_path],
                "filters": ["Generated from local repo artifacts by python3 data_analytics/build_hsjepa_audit.py"],
                "metric_definitions": metric_definitions,
            },
        }

    score_source = dataset_source(
        "hsjepa_public_score_ledger.csv",
        "Curated public LB sensor ledger with exact public log-loss values and HS-JEPA interpretation fields.",
        [
            "public_lb: competition public leaderboard log loss; lower is better",
            "best_so_far: cumulative minimum public_lb in curated observation order",
            "delta_vs_previous_best: current public_lb minus previous best before the observation",
        ],
    )
    target_source = dataset_source(
        "hsjepa_target_inventory.csv",
        "Target prevalence summary computed from data/ch2026_metrics_train.csv.",
        [
            "positive_rate: mean of binary target over 450 training rows",
            "positives: count of rows where target equals 1",
            "negatives: count of rows where target equals 0",
        ],
    )
    day_source = dataset_source(
        "hsjepa_day_file_inventory.csv",
        "Local artifact activity grouped by filesystem modification date and artifact type.",
        [
            "count: number of matching root submission files or HITL report files for each local file date",
        ],
    )
    best_source = dataset_source(
        "hsjepa_public_score_ledger.csv",
        "Top public LB observations selected from the curated sensor ledger.",
        [
            "score_rank: rank of public_lb, lower public_lb is better",
            "public_lb: competition public leaderboard log loss; lower is better",
        ],
    )

    score_rows = ledger[
        [
            "sequence",
            "observed_stage",
            "file",
            "public_lb",
            "best_so_far",
            "delta_vs_previous_best",
            "improved_previous_best",
            "family",
            "worldview",
            "source",
        ]
    ].to_dict("records")
    best_rows = ledger.sort_values("public_lb").head(12)[
        ["score_rank", "observed_stage", "file", "public_lb", "family", "note", "source"]
    ].to_dict("records")
    target_rows = targets.to_dict("records")
    day_rows = day_inventory.to_dict("records")
    exp_rows = experiments.tail(35).fillna("").to_dict("records")
    inventory_rows = inventory.to_dict("records")

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "HS-JEPA 데이터·점수 분석 리포트",
        "generatedAt": f"{TODAY}T00:00:00+09:00",
        "description": "수면 생활습관 예측 대회 HS-JEPA 실험의 public LB, 데이터 범위, action-decoder 병목을 한국어로 정리한 Data Analytics 리포트",
        "sources": [
            {
                "id": "repo_sources",
                "label": "Local repo analysis sources",
                "path": "/Users/kbsoo/Downloads/cl2",
                "query": {
                    "engine": "local_python",
                    "language": "python",
                    "description": "Read local CSV/Markdown/parquet experiment artifacts and summarize score/data/experiment inventory.",
                    "sql": "python3 data_analytics/build_hsjepa_audit.py",
                    "tables_used": [
                        "analysis_outputs/public_probe_observations.csv",
                        "lb_observation_log.md",
                        "README.md",
                        "hitl/*/*_decision.csv",
                        "data/ch2026_metrics_train.csv",
                        "data/ch2026_submission_sample.csv",
                        "data/ch2025_data_items/*.parquet",
                    ],
                    "filters": [
                        "Public LB observations explicitly recorded in repo or user-provided late observations",
                        "HITL decision files under hitl/",
                    ],
                    "metric_definitions": [
                        "public_lb: competition public leaderboard log loss; lower is better",
                        "delta_vs_previous_best: current public_lb minus previous best in curated observation order",
                        "best_so_far: cumulative minimum public_lb",
                    ],
                },
            }
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# HS-JEPA 데이터·점수 분석 리포트"},
            {
                "id": "summary",
                "type": "markdown",
                "body": (
                    "## Executive Summary\n\n"
                    f"- **현재 public best는 `{best_score}`다.** 파일은 `{best_file}`이며, 역할 이름으로는 frontier active-silence positive-path sensor다.\n"
                    "- **가장 중요한 구조 발견은 public-equation jump와 row-state vector frontier다.** pre-HS feature-NN frontier 0.5761589494에서 public-equation jump 0.5681234831로 크게 내려왔고, row-state vector frontier가 0.5677475939까지 좁혔다.\n"
                    "- **현재 병목은 latent 발견보다 action 안전성이다.** dual-head toxicity stress는 로컬 proxy가 좋아 보여도 0.5684942019로 후퇴해, hard-world/Pareto head가 action-grade decoder가 아님을 보여줬다.\n"
                    "- **target-assignment tie는 micro branch가 아니라 common action body가 문제였다는 증거다.** target-split XOR와 Q3 repair-only가 0.567929641로 같아 row135 Q3 vs row207 S2 선택만으로는 row-state frontier를 넘지 못한다.\n"
                    "- **frontier active-silence는 양성 신호지만 anchor-local이다.** 0.5677269444 새 best는 active silence 가설을 살리지만, 0.53급 breakthrough를 위해서는 anchor-free state transport가 필요하다."
                ),
            },
            {
                "id": "score_chart_intro",
                "type": "markdown",
                "body": "## Public LB는 public-equation jump에서 세계관을 바꾸고 row-state frontier에서 구조를 좁혔다\n\n아래 chart는 기록된 public LB 관측값의 흐름이다. 낮을수록 좋다. public-equation 이전의 0.576대 plateau가 0.568대로 내려왔고, row-state/frontier active-silence 계열에서 한 번 더 좁혀졌다.",
            },
            {"id": "score_chart_block", "type": "chart", "chartId": "score_timeline"},
            {
                "id": "best_table_intro",
                "type": "markdown",
                "body": "## Best 관측값과 negative sensor\n\n현재 best는 frontier active-silence positive-path지만, dual-head toxicity stress와 target-assignment stress 같은 실패도 의미가 크다. 이 실패들은 어떤 action family가 public-toxic인지 알려주는 stress sensor다.",
            },
            {"id": "best_table_block", "type": "table", "tableId": "best_scores"},
            {
                "id": "target_chart_intro",
                "type": "markdown",
                "body": "## 원본 target은 7개지만 HS-JEPA의 실제 단위는 row-target action이다\n\ntrain target 분포는 label 예측 문제의 기본 배경이다. 하지만 H057 이후 핵심 단위는 label 자체가 아니라 특정 row-target cell을 움직여도 되는지 여부로 바뀌었다.",
            },
            {"id": "target_chart_block", "type": "chart", "chartId": "target_prevalence"},
            {
                "id": "daily",
                "type": "markdown",
                "body": (
                    "## 날짜별 정리\n\n"
                    "### 2026-06-04\n"
                    "public-equation jump/Q2 phase route/row-state vector frontier public sensor를 정리했다. 결론은 Q2 support row가 단순 Q2 보정이 아니라 hidden human-state marker라는 것.\n\n"
                    "### 2026-06-05\n"
                    "dual-head toxicity stress와 target-assignment stress를 기준으로 병목을 재정의했다. 결론은 context encoder보다 safe row-target assignment decoder가 병목이라는 것.\n\n"
                    "### 2026-06-07\n"
                    "row-state vector frontier를 재현 가능한 end-to-end HS-JEPA 코드로 만들었고, Data Analytics report로 점수/데이터/실험을 정리했다.\n\n"
                    "### 2026-06-11\n"
                    "Cross-listener transport 후보가 0.5684860446으로 후퇴했다. 결론은 listener posterior를 final action gate로 쓰지 말고, row-state-positive action과 충돌하는 cell을 찾는 anti-listener/toxicity diagnostic으로 써야 한다는 것.\n\n"
                    "### 2026-06-12\n"
                    "frontier active-silence positive-path가 0.5677269444로 새 best를 만들었다. 결론은 active silence가 유효하지만 anchor-local ceiling이 낮으므로, 다음은 anchor-free state transport여야 한다는 것."
                ),
            },
            {"id": "day_activity_block", "type": "chart", "chartId": "day_activity"},
            {
                "id": "next_steps",
                "type": "markdown",
                "body": (
                    "## Recommended Next Steps\n\n"
                    "1. row-state vector frontier의 45개 row를 하나의 listener seed로만 취급하고, V131C cohort-relative outlier를 context view로 추가한다.\n"
                    "2. cohort outlier를 직접 Q2/Q3/S2에 꽂지 말고, action-health와 toxicity gate 입력으로 사용한다.\n"
                    "3. dual-head-positive 방향과 cross-listener-positive 방향을 forbidden/toxic diagnostic으로 쓰고, row-state-positive 방향과 동시에 만족하는 assignment field를 찾는다.\n"
                    "4. Gemini embedding은 논문/오픈소스 재현성 경로에서 제외하고, TF-IDF/SVD 또는 공개 sentence-transformer 계열로 semantic context encoder를 대체한다."
                ),
            },
            {
                "id": "caveats",
                "type": "markdown",
                "body": (
                    "## Caveats and Assumptions\n\n"
                    "- 이 리포트는 local repo에 남아 있는 파일과 사용자가 알려준 public LB 관측값만 사용한다.\n"
                    "- private LB는 관측 불가하므로 public/private factorization은 가설로 남긴다.\n"
                    "- Gemini 계열 실험은 기록에는 남기지만, 오픈소스 재현 가능한 HS-JEPA 핵심 경로로 보지는 않는다."
                ),
            },
        ],
        "charts": [
            {
                "id": "score_timeline",
                "type": "line",
                "title": "Public LB trajectory",
                "dataset": "score_ledger",
                "encodings": {
                    "x": {"field": "sequence"},
                    "y": {"field": "public_lb"},
                    "color": {"field": "family"},
                },
                "options": {"showLegend": True},
                "sourceId": "repo_sources",
                "source": score_source,
            },
            {
                "id": "target_prevalence",
                "type": "bar",
                "title": "Train target positive rate",
                "dataset": "target_inventory",
                "encodings": {
                    "x": {"field": "target"},
                    "y": {"field": "positive_rate"},
                },
                "options": {"orientation": "vertical"},
                "sourceId": "repo_sources",
                "source": target_source,
            },
            {
                "id": "day_activity",
                "type": "bar",
                "title": "Repo artifact activity by file date",
                "dataset": "day_file_inventory",
                "encodings": {
                    "x": {"field": "date"},
                    "y": {"field": "count"},
                    "color": {"field": "file_type"},
                },
                "options": {"grouping": "stacked"},
                "sourceId": "repo_sources",
                "source": day_source,
            },
        ],
        "tables": [
            {
                "id": "best_scores",
                "title": "Top public observations and sensors",
                "dataset": "best_scores",
                "columns": [
                    {"field": "score_rank", "label": "rank"},
                    {"field": "observed_stage", "label": "stage"},
                    {"field": "public_lb", "label": "public LB"},
                    {"field": "family", "label": "family"},
                    {"field": "file", "label": "file"},
                    {"field": "note", "label": "interpretation"},
                ],
                "sourceId": "repo_sources",
                "source": best_source,
            }
        ],
    }
    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": f"{TODAY}T00:00:00+09:00",
        "datasets": {
            "score_ledger": score_rows,
            "best_scores": best_rows,
            "target_inventory": target_rows,
            "data_inventory": inventory_rows,
            "experiment_inventory": exp_rows,
            "day_file_inventory": day_rows,
        },
    }
    return manifest, snapshot


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ledger = read_public_score_ledger()
    inventory = build_data_inventory()
    targets = build_target_inventory()
    experiments = build_experiment_inventory()
    day_inventory = build_day_file_inventory()

    ledger.to_csv(OUT / "hsjepa_public_score_ledger.csv", index=False)
    inventory.to_csv(OUT / "hsjepa_data_inventory.csv", index=False)
    targets.to_csv(OUT / "hsjepa_target_inventory.csv", index=False)
    experiments.to_csv(OUT / "hsjepa_experiment_inventory.csv", index=False)
    day_inventory.to_csv(OUT / "hsjepa_day_file_inventory.csv", index=False)
    build_daily_reports(ledger, inventory, experiments)

    manifest, snapshot = build_manifest_and_snapshot(ledger, inventory, targets, experiments, day_inventory)
    (OUT / "hsjepa_data_analytics_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (OUT / "hsjepa_data_analytics_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))

    best_public = ledger.sort_values("public_lb", ascending=True).iloc[0]
    summary = {
        "best_public_file": str(best_public["file"]),
        "best_public_lb": float(best_public["public_lb"]),
        "public_observations": int(len(ledger)),
        "hitl_decision_files": int(len(experiments)),
        "root_h_submission_files": int(len(list(ROOT.glob("submission_h*.csv")))),
        "data_sources_reviewed": int(len(inventory)),
        "artifact_manifest": str(OUT / "hsjepa_data_analytics_manifest.json"),
        "artifact_snapshot": str(OUT / "hsjepa_data_analytics_snapshot.json"),
    }
    (OUT / "hsjepa_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
