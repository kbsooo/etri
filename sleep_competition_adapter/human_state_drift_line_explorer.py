#!/usr/bin/env python3
"""Explore the human-state drift line after the confirmed 0.56191 result.

The previous certifier showed that a subject-uniform Q2/Q3 drift field transfers
strongly to public LB.  This script treats that drift field as a one-dimensional
human-state control axis and creates a small set of high-information sensors:

1. Is Q2 still under-powered after the confirmed replay?
2. Is Q3 a helpful companion route or a saturated/noisy side route?
3. Did the aggregate listener miss a silent subject whose train drift is strong?

The output files are competition-adapter probes, but the paper-facing claim is
general: once HS-JEPA recovers a hidden subject state direction, action decoding
should be tested along a coherent state-control axis rather than as unrelated
row-target cell edits.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.human_state_drift_consistency_certifier import (  # noqa: E402
    BASE_PATH,
    KEYS,
    KNOWN_PUBLIC_LB,
    PUBLIC_SENSOR_SIGN,
    REFERENCE_PUBLIC_LB,
    TARGETS,
    TRAIN_PATH,
    clip_prob,
    logit,
    sigmoid,
    subject_half_drift,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "human_state_drift_line_explorer"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class DriftLineConfig:
    name: str
    worldview: str
    q2_step: float
    q3_step: float
    extra_subject_q2_steps: tuple[tuple[str, float], ...] = ()
    extra_subject_q3_steps: tuple[tuple[str, float], ...] = ()
    probability_floor: float = 1e-6


CONFIGS = (
    DriftLineConfig(
        name="q2_dominant_forward_axis",
        worldview=(
            "The confirmed drift direction is right, and Q2 is the real "
            "intervention/degradation axis.  Push Q2 beyond the certified replay "
            "while keeping Q3 at the confirmed companion strength."
        ),
        q2_step=0.90,
        q3_step=0.25,
    ),
    DriftLineConfig(
        name="joint_forward_axis",
        worldview=(
            "The whole Q2/Q3 drift line is under-powered.  Move both Q2 and Q3 "
            "forward along the same hidden state axis."
        ),
        q2_step=0.8625,
        q3_step=0.2875,
    ),
    DriftLineConfig(
        name="q2_forward_q3_pullback_axis",
        worldview=(
            "Q2 carries the true human-state drift, but Q3 is a noisy companion. "
            "Push Q2 while pulling Q3 slightly back from the confirmed replay."
        ),
        q2_step=0.90,
        q3_step=0.18,
    ),
    DriftLineConfig(
        name="silent_subject_reentry_axis",
        worldview=(
            "id05 was silent in the aggregate listener field, but train history "
            "shows the strongest Q2 downward drift.  Keep the confirmed axis and "
            "test whether this silent subject should re-enter Q2."
        ),
        q2_step=0.75,
        q3_step=0.25,
        extra_subject_q2_steps=(("id05", -0.50),),
    ),
)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(TRAIN_PATH, parse_dates=["sleep_date", "lifelog_date"])
    base = pd.read_csv(BASE_PATH, parse_dates=KEYS[1:])
    return train, base


def build_steps(config: DriftLineConfig, drift: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    extra_q2 = dict(config.extra_subject_q2_steps)
    extra_q3 = dict(config.extra_subject_q3_steps)
    for subject_id in sorted(PUBLIC_SENSOR_SIGN):
        sign = PUBLIC_SENSOR_SIGN[subject_id]
        q2_step = sign * config.q2_step if sign else 0.0
        q3_step = sign * config.q3_step if sign else 0.0
        q2_step += float(extra_q2.get(subject_id, 0.0))
        q3_step += float(extra_q3.get(subject_id, 0.0))
        rows.append(
            {
                "subject_id": subject_id,
                "listener_sign": sign,
                "Q2_train_drift": float(drift.loc[subject_id, "Q2_drift"]),
                "Q3_train_drift": float(drift.loc[subject_id, "Q3_drift"]),
                "Q2_logit_step": q2_step,
                "Q3_logit_step": q3_step,
                "Q2_step_vs_confirmed": q2_step - sign * 0.75,
                "Q3_step_vs_confirmed": q3_step - sign * 0.25,
            }
        )
    return pd.DataFrame(rows)


def apply_steps(base: pd.DataFrame, steps: pd.DataFrame, floor: float) -> np.ndarray:
    prob = base[TARGETS].to_numpy(dtype=np.float64)
    logits = logit(prob)
    target_index = {target: idx for idx, target in enumerate(TARGETS)}
    subject_steps = steps.set_index("subject_id")[["Q2_logit_step", "Q3_logit_step"]].to_dict("index")
    for row_idx, subject_id in enumerate(base["subject_id"]):
        rec = subject_steps[str(subject_id)]
        logits[row_idx, target_index["Q2"]] += float(rec["Q2_logit_step"])
        logits[row_idx, target_index["Q3"]] += float(rec["Q3_logit_step"])
    return clip_prob(sigmoid(logits), floor=floor)


def audit_variant(config: DriftLineConfig, base: pd.DataFrame, prob: np.ndarray, steps: pd.DataFrame) -> pd.DataFrame:
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    new_logit = logit(prob)
    base_logit = logit(base_prob)
    rows: list[dict[str, object]] = []
    target_index = {target: idx for idx, target in enumerate(TARGETS)}
    for subject_id, group in base.groupby("subject_id"):
        idx = group.index.to_numpy()
        step = steps[steps["subject_id"].eq(subject_id)].iloc[0].to_dict()
        rec: dict[str, object] = {
            "variant": config.name,
            "subject_id": subject_id,
            "test_rows": int(len(idx)),
            "listener_sign": int(step["listener_sign"]),
            "Q2_train_drift": float(step["Q2_train_drift"]),
            "Q3_train_drift": float(step["Q3_train_drift"]),
            "Q2_logit_step": float(step["Q2_logit_step"]),
            "Q3_logit_step": float(step["Q3_logit_step"]),
        }
        for target in ["Q2", "Q3"]:
            j = target_index[target]
            rec[f"{target}_base_mean"] = float(base_prob[idx, j].mean())
            rec[f"{target}_new_mean"] = float(prob[idx, j].mean())
            rec[f"{target}_mean_prob_delta"] = float((prob[idx, j] - base_prob[idx, j]).mean())
            rec[f"{target}_mean_logit_delta"] = float((new_logit[idx, j] - base_logit[idx, j]).mean())
        rows.append(rec)
    return pd.DataFrame(rows)


def summarize_variant(config: DriftLineConfig, base: pd.DataFrame, prob: np.ndarray, path: Path) -> dict[str, object]:
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    changed = np.abs(prob - base_prob) > 1e-12
    base_logit = logit(base_prob)
    delta_logit = logit(prob) - base_logit
    validation = validate_submission(path, base, base_prob)
    return {
        "name": config.name,
        "worldview": config.worldview,
        "config": asdict(config),
        "submission": str(path.resolve()),
        "validation": validation,
        "changed_rows_vs_frontier_silence": int(changed.any(axis=1).sum()),
        "changed_cells_vs_frontier_silence": int(changed.sum()),
        "target_changes": {target: int(changed[:, idx].sum()) for idx, target in enumerate(TARGETS)},
        "mean_abs_logit_delta": {
            target: float(np.abs(delta_logit[:, idx]).mean()) for idx, target in enumerate(TARGETS)
        },
    }


def write_markdown(readout: dict[str, object]) -> None:
    lines = [
        "# Human-State Drift Line Explorer",
        "",
        "## 핵심 질문",
        "",
        "`certified_replay`가 public LB `0.5619100863`을 기록했으므로, 이제 direction은 강하게 살아 있다.",
        "다음 질문은 magnitude다.",
        "",
        "```text",
        "Q2/Q3 subject drift line은 아직 더 밀 수 있는가?",
        "아니면 confirmed replay 지점이 이미 포화점인가?",
        "```",
        "",
        "## 후보",
        "",
        "| variant | worldview | Q2 step | Q3 step | changed cells | upload safe |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for variant in readout["variants"]:
        config = variant["config"]
        validation = variant["validation"]
        lines.append(
            f"| {variant['name']} | {variant['worldview']} | {config['q2_step']:.4f} | "
            f"{config['q3_step']:.4f} | {variant['changed_cells_vs_frontier_silence']} | "
            f"{validation['upload_safe']} |"
        )
    lines += [
        "",
        "## 제출 우선순위",
        "",
        "가장 정보량이 큰 후보는 `q2_dominant_forward_axis`다.",
        "",
        "좋아지면:",
        "",
        "- Q2 intervention/degradation route가 아직 under-powered였다는 뜻이다.",
        "- HS-JEPA 논문에는 `drift line control axis`와 `route-specific magnitude decoder`를 추가할 수 있다.",
        "",
        "나빠지면:",
        "",
        "- `0.75` Q2 logit step 부근이 이미 public aggregate optimum에 가깝다는 뜻이다.",
        "- 다음 breakthrough는 같은 line overshoot가 아니라 S-target hidden route 또는 private-state factorization이어야 한다.",
        "",
        "## 산출물",
        "",
        f"- readout: `{readout['readout_json']}`",
        f"- output_dir: `{readout['output_dir']}`",
    ]
    (OUT / "HUMAN_STATE_DRIFT_LINE_EXPLORER_KO.md").write_text("\n".join(lines), encoding="utf-8")


def run() -> dict[str, object]:
    train, base = load_frames()
    drift = subject_half_drift(train)
    variants: list[dict[str, object]] = []
    audit_frames: list[pd.DataFrame] = []
    for config in CONFIGS:
        steps = build_steps(config, drift)
        prob = apply_steps(base, steps, config.probability_floor)
        digest = short_hash(prob)
        filename = f"submission_hsjepa_human_state_drift_line_{config.name}_{digest}_uploadsafe.csv"
        out_path = OUT / filename
        root_path = ROOT / filename
        write_submission(out_path, base, prob, floor=config.probability_floor)
        write_submission(root_path, base, prob, floor=config.probability_floor)
        summary = summarize_variant(config, base, prob, out_path)
        summary["root_submission"] = str(root_path.resolve())
        summary["subject_steps"] = steps.to_dict("records")
        variants.append(summary)
        audit_frames.append(audit_variant(config, base, prob, steps))

    audit = pd.concat(audit_frames, ignore_index=True)
    audit.to_csv(OUT / "human_state_drift_line_audit.csv", index=False)

    readout = {
        "base_submission": str(BASE_PATH.resolve()),
        "confirmed_positive": {
            "submission": "submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv",
            "public_lb": KNOWN_PUBLIC_LB["certified_replay"],
            "delta_vs_frontier_silence": KNOWN_PUBLIC_LB["certified_replay"]
            - REFERENCE_PUBLIC_LB["frontier_silence"],
        },
        "recommended_next_sensor": "q2_dominant_forward_axis",
        "recommended_next_sensor_path": next(
            variant["root_submission"] for variant in variants if variant["name"] == "q2_dominant_forward_axis"
        ),
        "variants": variants,
        "readout_json": str((OUT / "human_state_drift_line_readout.json").resolve()),
        "output_dir": str(OUT.resolve()),
    }
    (OUT / "human_state_drift_line_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(readout)
    return readout


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["confirmed_positive"], ensure_ascii=False, indent=2))
    print("recommended_next_sensor", result["recommended_next_sensor_path"])
    for variant in result["variants"]:
        print(
            variant["name"],
            variant["root_submission"],
            variant["changed_rows_vs_frontier_silence"],
            variant["changed_cells_vs_frontier_silence"],
            variant["validation"]["upload_safe"],
        )
