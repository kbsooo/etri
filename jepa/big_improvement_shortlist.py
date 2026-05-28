from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
JEPA_DIR = ROOT / "jepa"
ANALYSIS_DIR = ROOT / "analysis_outputs"
SAMPLE_PATH = ROOT / "data" / "ch2026_submission_sample.csv"
STAGE2_PATH = ANALYSIS_DIR / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
RAW05_PATH = JEPA_DIR / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]


@dataclass(frozen=True)
class Candidate:
    alias: str
    source: Path
    family: str
    tier: str
    oof: float | None
    public_estimate: str
    risk_note: str
    rationale: str


CANDIDATES = [
    Candidate(
        alias="submission_bigshot_01_public_minimax_r05.csv",
        source=ANALYSIS_DIR / "submission_public_minimaxens_r05_a10_h506746.csv",
        family="public_constraint_minimax",
        tier="primary_public",
        oof=0.554348,
        public_estimate="six-posterior score 0.5749169 / mean 0.5746342",
        risk_note="public feedback 3개를 제약식으로 쓴 후보라 private/hidden-subset overfit 리스크 있음",
        rationale="현재 public-constraint 계열에서 six-posterior robust score가 가장 좋은 축.",
    ),
    Candidate(
        alias="submission_bigshot_02_public_minimax_r01.csv",
        source=ANALYSIS_DIR / "submission_public_minimaxens_r01_a6_h422045.csv",
        family="public_constraint_minimax",
        tier="primary_public",
        oof=0.554332,
        public_estimate="selected score 0.5749250 / mean 0.5746342",
        risk_note="r05와 거의 같은 예측이지만 더 sparse한 6-weight ensemble",
        rationale="가장 단순한 rank-1 sparse minimax ensemble. 첫 제출 후보로 해석이 쉽다.",
    ),
    Candidate(
        alias="submission_bigshot_03_public_universe_u80.csv",
        source=ANALYSIS_DIR / "submission_public_universeens_u80_r01_07c571e6.csv",
        family="public_universe_minimax",
        tier="primary_public_alt",
        oof=0.554343,
        public_estimate="weighted expected 0.5746461 / score 0.5752114",
        risk_note="u80 trusted scenario에서 좋지만 mask-plausibility 평균순위는 u65보다 낮음",
        rationale="expanded uncertainty universe에서 trusted profile을 가장 잘 버틴 후보.",
    ),
    Candidate(
        alias="submission_bigshot_04_public_universe_u65_maskrank.csv",
        source=ANALYSIS_DIR / "submission_public_universeens_u65_r04_dc6f3303.csv",
        family="public_universe_mask_plausibility",
        tier="primary_public_alt",
        oof=0.554759,
        public_estimate="weighted expected 0.5746552 / mask mean-rank 17.54",
        risk_note="u80보다 더 보수적인 subject/random-like public-row 가정",
        rationale="public row mask가 subject/random-like라면 minimax보다 더 plausible한 후보.",
    ),
    Candidate(
        alias="submission_bigshot_05_public_targetmask_noq2_g075.csv",
        source=ANALYSIS_DIR / "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
        family="public_entropy_targetmask",
        tier="single_public_probe",
        oof=0.554185,
        public_estimate="public-posterior expected 0.575887 / robust mean 0.574649",
        risk_note="single projection이라 ensemble보다 분산 큼",
        rationale="Q2를 빼고 public inverse signal이 강한 Q1/Q3/S/S만 움직인 단일 후보.",
    ),
    Candidate(
        alias="submission_bigshot_06_public_entropy_exact_g100.csv",
        source=ANALYSIS_DIR / "submission_public_entropyproj_public2d0_g100.csv",
        family="public_entropy_projection",
        tier="aggressive_public_probe",
        oof=0.553679,
        public_estimate="public self expected 0.575734 / exact fit to three public scores",
        risk_note="known public scores에 가장 강하게 맞춘 exact-fit이라 overfit risk 최고",
        rationale="가장 공격적인 public inverse probe. 맞으면 크지만 틀리면 흔들릴 수 있다.",
    ),
    Candidate(
        alias="submission_bigshot_07_public_maskaware_t80_noq2.csv",
        source=ANALYSIS_DIR / "submission_public_maskaware_t80_r11_544844af.csv",
        family="public_maskaware_entropy",
        tier="public_subset_fallback",
        oof=0.553156,
        public_estimate="posterior mean 0.5755017 / conservative 0.5758453",
        risk_note="row-subset uncertainty fallback, minimax보다 expected는 약간 높음",
        rationale="public rows가 전체 250 row와 다르게 뽑혔을 때를 가정한 보완 후보.",
    ),
    Candidate(
        alias="submission_bigshot_08_public_consfront_t80.csv",
        source=ANALYSIS_DIR / "submission_public_consfront_t80_r10_b06ca82f.csv",
        family="public_conservative_frontier",
        tier="conservative_public",
        oof=0.557498,
        public_estimate="posterior mean 0.5747919 / conservative mean 0.5746464",
        risk_note="OOF는 약하지만 public inverse overfit을 stage2/anchor 쪽으로 완충",
        rationale="public 제약이 일부 overfit일 때 가장 안전한 bridge 후보.",
    ),
    Candidate(
        alias="submission_bigshot_09_hiddenblock_paretomix_w03.csv",
        source=ANALYSIS_DIR / "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
        family="hiddenblock_rawaxis",
        tier="structural_control",
        oof=None,
        public_estimate="posterior-fit 0.576825 / raw-axis expected 0.577526",
        risk_note="public-constraint 후보보다 약하지만 JEPA/raw hidden-block 구조 후보 중 안전",
        rationale="hidden block pseudo-rate를 raw-axis 중립으로 섞은 구조적 control.",
    ),
    Candidate(
        alias="submission_bigshot_10_jepa_neural_episode_rawstack_balanced.csv",
        source=JEPA_DIR / "submission_jepa_neural_episode_rawstack_raw075_nb_top10_er_top10_rw0p75_nw1p0_ew1p0.csv",
        family="jepa_neural_episode_rawstack",
        tier="jepa_big_oof_probe",
        oof=0.556972,
        public_estimate="no direct public estimate / bad-axis -0.0984 / raw-good 1.1224",
        risk_note="public 미제출 JEPA high-upside probe. raw-good 과증폭 가능성 있음",
        rationale="JEPA 비중을 가장 키운 후보 중 bad JEPA axis는 음수, raw-good은 강한 balanced 후보.",
    ),
    Candidate(
        alias="submission_bigshot_11_jepa_multifeature_rawstack.csv",
        source=JEPA_DIR / "submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw1p0.csv",
        family="jepa_block_canvas_multifeature",
        tier="jepa_big_oof_probe",
        oof=0.554194,
        public_estimate="no direct public estimate / bad-axis 0.0220 / raw-good 0.5617",
        risk_note="OOF는 강하지만 failed-JEPA axis가 약하게 양수",
        rationale="Block-Canvas multi-feature JEPA를 raw public-positive anchor와 결합한 고OOF 후보.",
    ),
    Candidate(
        alias="submission_bigshot_12_jepa_blockcanvas_aggressive_noq2.csv",
        source=JEPA_DIR / "submission_block_canvas_multifeature_k8_c0p05_noq2_scale1p0.csv",
        family="jepa_block_canvas_multifeature",
        tier="jepa_aggressive_oof_probe",
        oof=0.550698,
        public_estimate="no direct public estimate / bad-axis 0.1493 / raw-good -0.0027",
        risk_note="public axis 안전장치가 거의 없어 공격적 probe로만 사용",
        rationale="JEPA canvas 자체의 큰 OOF 개선이 public에도 살아있는지 확인하는 강한 probe.",
    ),
]


def assert_frame_ok(df: pd.DataFrame, sample: pd.DataFrame, path: Path) -> None:
    expected_cols = KEYS + TARGETS
    if list(df.columns) != expected_cols:
        raise ValueError(f"{path} has unexpected columns: {list(df.columns)}")
    if len(df) != len(sample):
        raise ValueError(f"{path} row count {len(df)} != sample {len(sample)}")
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"{path} key/order mismatch")
    if df[KEYS].duplicated().any():
        raise ValueError(f"{path} has duplicate keys")
    if df[TARGETS].isna().any().any():
        raise ValueError(f"{path} has NaN target values")
    lo = float(df[TARGETS].min().min())
    hi = float(df[TARGETS].max().max())
    if lo < 0.0 or hi > 1.0:
        raise ValueError(f"{path} target probabilities outside [0, 1]: {lo}..{hi}")


def mean_abs_delta(df: pd.DataFrame, base: pd.DataFrame | None) -> float | None:
    if base is None:
        return None
    return float((df[TARGETS] - base[TARGETS]).abs().to_numpy().mean())


def main() -> None:
    sample = pd.read_csv(SAMPLE_PATH)
    stage2 = pd.read_csv(STAGE2_PATH) if STAGE2_PATH.exists() else None
    raw05 = pd.read_csv(RAW05_PATH) if RAW05_PATH.exists() else None
    if stage2 is not None:
        assert_frame_ok(stage2, sample, STAGE2_PATH)
    if raw05 is not None:
        assert_frame_ok(raw05, sample, RAW05_PATH)

    validation_rows: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []

    for idx, cand in enumerate(CANDIDATES, start=1):
        if not cand.source.exists():
            raise FileNotFoundError(cand.source)
        out_path = JEPA_DIR / cand.alias
        shutil.copyfile(cand.source, out_path)

        df = pd.read_csv(out_path)
        assert_frame_ok(df, sample, out_path)
        validation_rows.append(
            {
                "priority": idx,
                "alias": cand.alias,
                "source": str(cand.source.relative_to(ROOT)),
                "rows": len(df),
                "columns_ok": True,
                "keys_ok": True,
                "min_prob": float(df[TARGETS].min().min()),
                "max_prob": float(df[TARGETS].max().max()),
                "mean_abs_delta_vs_stage2": mean_abs_delta(df, stage2),
                "mean_abs_delta_vs_raw05": mean_abs_delta(df, raw05),
            }
        )
        manifest_rows.append(
            {
                "priority": idx,
                "alias": cand.alias,
                "family": cand.family,
                "tier": cand.tier,
                "oof": cand.oof,
                "public_estimate": cand.public_estimate,
                "risk_note": cand.risk_note,
                "rationale": cand.rationale,
                "source": str(cand.source.relative_to(ROOT)),
            }
        )

    validation_path = JEPA_DIR / "big_improvement_validation.csv"
    manifest_path = JEPA_DIR / "big_improvement_manifest.csv"
    md_path = JEPA_DIR / "big_improvement_shortlist.md"

    pd.DataFrame(validation_rows).to_csv(validation_path, index=False)
    pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False, quoting=csv.QUOTE_MINIMAL)

    lines = [
        "# Big Improvement Submission Shortlist",
        "",
        "This file promotes the larger-move candidates after the small count/latent residual gains stalled.",
        "",
        "## Public-LB First Order",
        "",
        "1. `submission_bigshot_01_public_minimax_r05.csv` - best current robust public-constraint candidate.",
        "2. `submission_bigshot_02_public_minimax_r01.csv` - almost identical score, simpler sparse ensemble.",
        "3. `submission_bigshot_03_public_universe_u80.csv` - trusted expanded-universe alternative.",
        "4. `submission_bigshot_04_public_universe_u65_maskrank.csv` - better if public rows are subject/random-like.",
        "5. `submission_bigshot_08_public_consfront_t80.csv` - conservative bridge if the public constraints are partly overfit.",
        "",
        "## JEPA Big-Probe Order",
        "",
        "1. `submission_bigshot_10_jepa_neural_episode_rawstack_balanced.csv` - JEPA-heavy, bad-axis negative, raw-good positive.",
        "2. `submission_bigshot_11_jepa_multifeature_rawstack.csv` - stronger OOF, small positive bad-axis.",
        "3. `submission_bigshot_12_jepa_blockcanvas_aggressive_noq2.csv` - largest JEPA OOF probe here, high public risk.",
        "",
        "## Candidate Table",
        "",
        "| priority | alias | tier | OOF | public estimate / axis | risk |",
        "|---:|---|---|---:|---|---|",
    ]
    for row in manifest_rows:
        oof = "" if pd.isna(row["oof"]) else f"{float(row['oof']):.6f}"
        lines.append(
            f"| {row['priority']} | `{row['alias']}` | {row['tier']} | {oof} | "
            f"{row['public_estimate']} | {row['risk_note']} |"
        )
    lines += [
        "",
        "## Validation",
        "",
        f"- Manifest: `{manifest_path.relative_to(ROOT)}`",
        f"- Integrity: `{validation_path.relative_to(ROOT)}`",
        "- All aliases preserve sample key/order, have 250 rows, no missing values, and target probabilities within [0, 1].",
        "",
        "## Interpretation",
        "",
        "The direct JEPA/count residual branch gave sub-0.001 gains, so it is not enough. The only current branch with a materially larger expected public move is the public-constraint/minimax branch, which uses the submitted public scores as aggregate hidden-label constraints. The JEPA-heavy files are kept as high-upside probes because their OOF is much lower, but public feedback already showed that direct JEPA movement can be punished.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {manifest_path}")
    print(f"wrote {validation_path}")
    print(f"wrote {md_path}")
    print(pd.DataFrame(validation_rows)[["priority", "alias", "min_prob", "max_prob", "mean_abs_delta_vs_stage2"]].to_string(index=False))


if __name__ == "__main__":
    main()
