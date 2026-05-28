from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent

RAW05_PUBLIC = 0.5775263072
STAGE2_PUBLIC = 0.5779449757

RANKER = ROOT / "public_lb_actual_anchor_ranker_scores.csv"
CALIBRATION = ROOT / "public_lb_actual_anchor_ranker_calibration.csv"

OUT_CSV = ROOT / "final_jepa_candidate_priority_20260527.csv"
OUT_MD = ROOT / "final_jepa_candidate_priority_20260527.md"
OUT_FAMILY = ROOT / "final_jepa_candidate_family_summary_20260527.csv"
OUT_CONSTRAINED = ROOT / "final_jepa_constrained_shortlist_20260527.csv"
OUT_TARGET_ASSEMBLY = ROOT / "final_jepa_target_assembly_addendum_20260527.csv"
OUT_TARGET_WEIGHT = ROOT / "final_jepa_target_weight_addendum_20260527.csv"
OUT_Q3_COUNTERWEIGHT = ROOT / "final_jepa_q3stress_counterweight_addendum_20260527.csv"
OUT_Q3_COUNTERWEIGHT_LOCAL = ROOT / "final_jepa_q3stress_counterweight_local_addendum_20260527.csv"
OUT_CONTEXT_TARGET_ENERGY = ROOT / "final_jepa_context_target_energy_gate_addendum_20260527.csv"
OUT_ENERGY_FRONTIER = ROOT / "final_jepa_energy_constrained_frontier_addendum_20260527.csv"
OUT_ENERGYFRONT_MICRO = ROOT / "final_jepa_energyfront_microrefine_addendum_20260527.csv"
OUT_EFMICRO_GATE = ROOT / "final_jepa_efmicro_gate_refine_addendum_20260527.csv"
OUT_EFGATE_BACKOFF = ROOT / "final_jepa_efgate_backoff_frontier_addendum_20260527.csv"
OUT_SIGREG_GATED = ROOT / "final_jepa_sigreg_gated_microrefine_addendum_20260527.csv"
OUT_SIGREG_ANCHOR = ROOT / "final_jepa_sigreg_micro_anchor_refine_addendum_20260527.csv"
OUT_COMPAT_BAND = ROOT / "final_jepa_compat_band_refine_addendum_20260527.csv"
OUT_LEJEPA_SIGREG = ROOT / "final_jepa_lejepa_sigreg_addendum_20260527.csv"
LEJEPA_SIGREG_AUDIT = ROOT / "lejepa_sigreg_candidate_audit.csv"


PREFERRED_SHORTLISTS = [
    "raw05_jepa_lowbad_motif_search_shortlist.csv",
    "raw05_jepa_direct_constrained_search_shortlist.csv",
    "raw05_jepa_axislocal_posterior_sweep_shortlist.csv",
    "raw05_jepa_anchorrobust_motif_graft_shortlist.csv",
    "raw05_jepa_structural_constrained_refine_shortlist.csv",
    "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv",
    "raw05_jepa_axisbridge_posterior_repair_shortlist.csv",
    "raw05_jepa_axisbudget_motif_bridge_shortlist.csv",
    "raw05_jepa_tangent_nullspace_refine_shortlist.csv",
    "raw05_jepa_blockcount_regularized_refine_shortlist.csv",
    "jepa_block_count_shift_actual_anchor_augmented.csv",
    "public_lb_actual_anchor_missing_candidate_augmented.csv",
    "raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv",
    "raw05_jepa_public6_drift_microperturb_shortlist.csv",
    "public_lb_six_anchor_entropy_projection_shortlist.csv",
    "raw05_jepa_compat_band_refine_shortlist.csv",
    "raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv",
    "raw05_jepa_sigreg_gated_microrefine_shortlist.csv",
    "raw05_jepa_efgate_backoff_frontier_shortlist.csv",
    "raw05_jepa_efmicro_gate_refine_shortlist.csv",
    "raw05_jepa_energyfront_microrefine_shortlist.csv",
    "raw05_jepa_energy_constrained_frontier_shortlist.csv",
    "raw05_jepa_q3stress_counterweight_local_shortlist.csv",
    "raw05_jepa_context_target_energy_gate_shortlist.csv",
    "raw05_jepa_q3stress_counterweight_shortlist.csv",
    "jepa_micro_bridge_ensemble_shortlist.csv",
    "jepa_block_consensus_rawcorrector_microrefine_shortlist.csv",
    "jepa_block_consensus_rawcorrector_refine_shortlist.csv",
    "jepa_block_consensus_rawcorrector_shortlist.csv",
    "jepa_block_consensus_gate_shortlist.csv",
    "jepa_bridge_ensemble_shortlist.csv",
    "jepa_bridge_posterior_regularizer_shortlist.csv",
    "jepa_public_minimax_rawsafe_bridge_shortlist.csv",
    "jepa_public_blockentropy_shortlist.csv",
    "jepa_energy_ensemble_shortlist.csv",
    "block_scale_jepa_axis_submission_shortlist.csv",
    "hidden_block_sequence_motif_shortlist.csv",
    "hidden_block_rateprobe_shortlist.csv",
]


PRIORITY = [
    {
        "rank": 0.10,
        "file": "submission_raw05_jepa_energyfront_a190aa25.csv",
        "tier": "A-frontier",
        "role": "energy-constrained q3cw frontier actual/low-bad probe",
        "decision": "Current best actual-anchor proxy in the raw05-compatible JEPA branch; submit as the main new probe if accepting proxy risk.",
    },
    {
        "rank": 0.11,
        "file": "submission_raw05_jepa_efmicro_3eece507.csv",
        "tier": "A-micro",
        "role": "energyfront microrefine best actual/low-bad stitch",
        "decision": "Use as the first bad-axis compensation probe: nearly the same actual-anchor proxy as the frontier, with bad-axis cut to about 5e-4.",
    },
    {
        "rank": 0.12,
        "file": "submission_raw05_jepa_efmicro_1859bae9.csv",
        "tier": "A-micro-guarded",
        "role": "energy-improved micro actual/low-bad stitch",
        "decision": "Use when requiring the micro low-bad structure plus non-positive context-target energy drift.",
    },
    {
        "rank": 0.13,
        "file": "submission_raw05_jepa_efmicro_f88f2cec.csv",
        "tier": "A-micro-posterior",
        "role": "posterior-safe micro low-bad stitch",
        "decision": "Use when posterior proxy below 0.576900 is preferred over the last actual-anchor margin.",
    },
    {
        "rank": 0.135,
        "file": "submission_raw05_jepa_efmicro_5d2d2af0.csv",
        "tier": "A-micro-sigreg-best",
        "role": "stable-SIGReg best efmicro compromise",
        "decision": "Best combined efmicro candidate under deterministic full SIGReg audit: near f88 posterior/actual with substantially stronger residual health.",
    },
    {
        "rank": 0.14,
        "file": "submission_raw05_jepa_efmicro_9f19106d.csv",
        "tier": "A-micro-lowbad",
        "role": "lowest-bad micro actual stitch",
        "decision": "Diagnostic probe for whether public rewards the bad-axis collapse to roughly 4e-4.",
    },
    {
        "rank": 0.141,
        "file": "submission_raw05_jepa_efmicro_9e631d75.csv",
        "tier": "A-micro-health",
        "role": "best LeJEPA-balanced efmicro health/posterior compromise",
        "decision": "Use when residual-health regularization is prioritized with a posterior-safe micro profile; stable full SIGReg ranks it just behind the strongest efmicro compromises.",
    },
    {
        "rank": 0.142,
        "file": "submission_raw05_jepa_siganchor_3644a42f.csv",
        "tier": "A-siganchor-health-lowbad",
        "role": "best stable-SIGReg siganchor compromise",
        "decision": "Best siganchor row under deterministic full SIGReg audit: lower posterior and bad-axis than the efmicro posterior-safe row, at a small actual-anchor cost.",
    },
    {
        "rank": 0.143,
        "file": "submission_raw05_jepa_siganchor_882fa552.csv",
        "tier": "A-siganchor-compromise",
        "role": "actual-best siganchor anchor-preserving compromise",
        "decision": "Use if siganchor actual-anchor preservation matters more than its best health/bad-axis balance; actual-anchor gives up only about 1.5e-7 versus f88.",
    },
    {
        "rank": 0.14302,
        "file": "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
        "tier": "A-graft-local-lowbad",
        "role": "anchor-robust donor graft with best local raw05-relative proxy",
        "decision": "Best graft after local LB validation: slightly improves the structrefine_04ad10f8 raw05-relative proxy, keeps the Q3/S4 motif tight, and holds bad-axis near 2e-5. The margin is only about 3e-8 locally, so treat it as a conservative structural submit probe rather than a proven public-LB gain.",
    },
    {
        "rank": 0.143025,
        "file": "submission_raw05_jepa_lowbadcon_71601b5f.csv",
        "tier": "A-lowbad-balanced",
        "role": "low-bad q1/s3 axislocal micro-injection on the e40 manifold",
        "decision": "Best lowbad-score probe: preserves e40-like posterior, bad-axis, and Q3/S4 motif while adding a tiny q1/s3 axislocal step. It does not beat e40 on local proxy, so use as a stability check rather than a replacement.",
    },
    {
        "rank": 0.14303,
        "file": "submission_raw05_jepa_lowbadcon_2240eb29.csv",
        "tier": "A-lowbad-local-boundary",
        "role": "strict lowbad local-edge boundary probe",
        "decision": "Highest local raw05-relative edge found under the lowbad/motif guardrails, but the gain over e40 is only about 6e-9 and posterior plus Q3/S4 off-motif ratio are weaker. Submit only as a high-information boundary test after the safer e40 probe.",
    },
    {
        "rank": 0.14304,
        "file": "submission_raw05_jepa_structrefine_04ad10f8.csv",
        "tier": "A-structrefine-local-motif",
        "role": "structural constrained micro-refine with local/health balance",
        "decision": "Best submit-shaped structural refine probe after local LB validation: improves the 931a03a1 raw05-relative proxy, keeps the Q3/S4 motif cosine/orthogonal residual tight, and cuts bad-axis by about 4x while holding posterior near 0.576904.",
    },
    {
        "rank": 0.14307,
        "file": "submission_raw05_jepa_structrefine_90e28f7d.csv",
        "tier": "A-structrefine-lowbad-motif",
        "role": "axisrepair-donor structural refine with near-zero bad-axis",
        "decision": "Use as the cleanest JEPA motif/posterior/bad-axis stress probe: posterior is slightly lower than 931a03a1, raw-axis stays inside the 1e-7 guardrail, and bad-axis falls to about 1.6e-6, though LeJEPA residual health is weaker.",
    },
    {
        "rank": 0.143085,
        "file": "submission_raw05_jepa_directcon_a903806a.csv",
        "tier": "A-directcon-motif-lock",
        "role": "direct constrained axislocal injection with exact Q3/S4 motif projection",
        "decision": "Diagnostic structural probe: recovers almost the same local raw05-relative edge as the anchorrobust graft while directly enforcing posterior/raw-axis and exact Q3/S4 motif constraints, but bad-axis is weaker than e40 so do not promote above the graft.",
    },
    {
        "rank": 0.14309,
        "file": "submission_raw05_jepa_directcon_ff079802.csv",
        "tier": "A-directcon-local-edge",
        "role": "direct constrained best local-edge motif lock",
        "decision": "Use only to test the axislocal signal under exact motif lock: local proxy is near the best direct-constrained edge, but bad-axis is around 8e-5 and posterior is slightly higher than the safer graft/structrefine rows.",
    },
    {
        "rank": 0.1431,
        "file": "submission_raw05_jepa_axistrade_931a03a1.csv",
        "tier": "A-axistrade-goal-local",
        "role": "direct motif/posterior tradeoff repair with raw-negative context gate",
        "decision": "Best direct tradeoff goal-hit probe after structural feature audit: preserves the target motif almost exactly, holds posterior below 0.57691 and raw-axis slightly negative, and has the lowest axistrade structural/motif residual; use to test whether the repaired motif survives public LB better than the earlier axisrepair rows.",
    },
    {
        "rank": 0.1432,
        "file": "submission_raw05_jepa_axistrade_80fd659c.csv",
        "tier": "A-axistrade-goal-health",
        "role": "direct motif/posterior tradeoff repair with best axistrade health balance",
        "decision": "Strong direct tradeoff goal-hit probe: keeps posterior near 0.576904, raw-axis negative, and bad-axis near zero with slightly better LeJEPA residual health than 931a03a1, but structural motif residual is a little weaker.",
    },
    {
        "rank": 0.1434,
        "file": "submission_raw05_jepa_axisrepair_2a20d67f.csv",
        "tier": "A-axisrepair-context-probe",
        "role": "axisbridge Q3/S4 motif with posterior-safe context repair",
        "decision": "Best high-information posterior-repair probe: preserves the axisbridge target motif fully while lowering posterior to about 0.576933 and keeping raw-axis slightly negative; local edge remains far below proxy resolution.",
    },
    {
        "rank": 0.1437,
        "file": "submission_raw05_jepa_axisrepair_78029f2c.csv",
        "tier": "A-axisrepair-posterior-safe-probe",
        "role": "posterior-safe A-family donor with partial axisbridge motif injection",
        "decision": "Use to test the safer repair variant: posterior and bad-axis are A-family-like, but only about 37% of the Q3/S4 motif is retained, so it is diagnostic rather than a main replacement.",
    },
    {
        "rank": 0.144,
        "file": "submission_raw05_jepa_axisbridge_45f2ba5a.csv",
        "tier": "A-axisbridge-health-probe",
        "role": "best LeJEPA-balanced raw-negative public6 Q3/S4 motif bridge",
        "decision": "High-information probe for the hidden Q3/S4 motif hypothesis: local raw05-relative proxy is about raw05-4e-6 and LeJEPA health is the best among axisbridge rows, but the gap is far below local proxy resolution.",
    },
    {
        "rank": 0.1445,
        "file": "submission_raw05_jepa_axisbridge_1968b38c.csv",
        "tier": "A-axisbridge-local-proxy",
        "role": "local-proxy-best raw-negative public6 Q3 motif bridge",
        "decision": "Use only to test whether target-block Q3 signal can survive raw-negative motif cancellation; local raw05-relative proxy is about raw05-5e-6, but posterior is weaker than the safer A-family candidates.",
    },
    {
        "rank": 0.145,
        "file": "submission_raw05_jepa_efback_cc265f32.csv",
        "tier": "A-backoff-risknone",
        "role": "efmicro to efgate risk-none posterior/low-bad backoff",
        "decision": "Use as a risk-none compromise: actual-anchor is weaker than micro, but posterior and bad-axis are both cleaner than the micro frontier.",
    },
    {
        "rank": 0.155,
        "file": "submission_raw05_jepa_efback_9c50051c.csv",
        "tier": "A-backoff-ultralowbad",
        "role": "efgate-to-efgate ultra-low-bad stress probe",
        "decision": "Use as the cleanest bad-axis stress test: bad-axis falls to about 3e-5 while staying raw-tight and posterior-safe.",
    },
    {
        "rank": 0.156,
        "file": "submission_raw05_jepa_siggate_fd0e9622.csv",
        "tier": "A-siggate-stable-best",
        "role": "best stable-SIGReg siggate low-bad diagnostic",
        "decision": "Best siggate row under deterministic full SIGReg audit: bad-axis near 2.2e-5 with stronger residual health than the earlier siggate representatives.",
    },
    {
        "rank": 0.157,
        "file": "submission_raw05_jepa_siggate_64220cc6.csv",
        "tier": "A-siggate-health-lowbad",
        "role": "SIGReg-gated low-bad residual-health stress probe",
        "decision": "Representative siggate low-bad candidate: bad-axis is about 2.5e-5, but deterministic full SIGReg now prefers fd0e9622 among siggate rows.",
    },
    {
        "rank": 0.158,
        "file": "submission_raw05_jepa_siggate_78179445.csv",
        "tier": "A-siggate-health",
        "role": "posterior-lowbad SIGReg-gated diagnostic",
        "decision": "Use only to test the LeJEPA low-bad/posterior hypothesis: it stays raw-tight with low bad-axis, but actual-anchor is weaker than efmicro/energyfront.",
    },
    {
        "rank": 0.159,
        "file": "submission_raw05_jepa_siggate_6d681440.csv",
        "tier": "A-siggate-ultralowbad",
        "role": "near-zero bad-axis SIGReg-gated stress probe",
        "decision": "Use if testing whether public strongly rewards near-zero bad-axis: bad-axis is about 6.6e-6 with raw drift below 1e-7, but this is diagnostic rather than frontier.",
    },
    {
        "rank": 0.1595,
        "file": "submission_raw05_jepa_blockcountreg_50b1cf4a.csv",
        "tier": "A-blockcountreg-ultralowbad-diagnostic",
        "role": "JEPA block-count regularized near-zero bad-axis stress probe",
        "decision": "Use only to test whether the block-count compatibility regularizer plus near-zero bad-axis is rewarded on public LB; local proxy is raw05-0.000003, but the gap is far below proxy resolution and actual-anchor is weaker than the main A family.",
    },
    {
        "rank": 0.16,
        "file": "submission_raw05_jepa_efgate_ac60a2e6.csv",
        "tier": "A-gate-posterior-lowbad",
        "role": "row-gated q1light efgate posterior/low-bad probe",
        "decision": "Use as the smooth efgate diagnostic: actual-anchor is weaker than micro, but posterior is lower and bad-axis collapses to roughly 2.4e-4.",
    },
    {
        "rank": 0.17,
        "file": "submission_raw05_jepa_efgate_d592970e.csv",
        "tier": "A-gate-ultralowbad",
        "role": "row-gated context-only ultra-low-bad raw-tight probe",
        "decision": "Use only as a strong bad-axis stress test: raw drift stays under 8e-8 and bad-axis collapses to roughly 5e-5, but actual-anchor gives up more margin.",
    },
    {
        "rank": 0.18,
        "file": "submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_top60_strength_g015_4050287e.csv",
        "tier": "A-public6-q3s4-diagnostic",
        "role": "public6 Q3/S4 target-block direction after raw/bad/ordinal axis correction",
        "decision": "Use only to test whether the public6 Q3/S4 signal survives JEPA-style target/context compatibility constraints; local LB proxy edge is tiny and below proxy noise, so this is not the main submission candidate.",
    },
    {
        "rank": 0.20,
        "file": "submission_raw05_jepa_energyfront_fa0e1e2d.csv",
        "tier": "A-guarded",
        "role": "energy-improved low-bad frontier stitch",
        "decision": "Use when requiring context-target energy improvement along with low raw-axis drift.",
    },
    {
        "rank": 0.30,
        "file": "submission_raw05_jepa_energyfront_ea665780.csv",
        "tier": "A-lowbad",
        "role": "very-low-bad raw-safe energy-improved stitch",
        "decision": "Use if minimizing bad-axis and raw drift matters more than the last tiny actual-proxy gain.",
    },
    {
        "rank": 0.40,
        "file": "submission_raw05_jepa_energyfront_0f7e85a0.csv",
        "tier": "A-strict",
        "role": "strict raw-neutral energy-constrained frontier stitch",
        "decision": "Use when raw-axis drift must be non-positive while keeping the new low-bad structure.",
    },
    {
        "rank": 0.95,
        "file": "submission_jepa_block_countshift_a58efeff.csv",
        "tier": "B-block-count-diagnostic",
        "role": "JEPA block-count constraint with raw-negative and low-bad axes",
        "decision": "Keep as a diagnostic rather than a main probe: local LB proxy is raw05+0.000005, below proxy resolution, while actual-anchor is weaker than the raw05-compatible A family.",
    },
    {
        "rank": 1,
        "file": "submission_jepa_micro_bridge_ensemble_5ffa44a8.csv",
        "tier": "A-aggressive",
        "role": "raw-negative JEPA consensus/bridge ensemble",
        "decision": "Submit when taking the highest JEPA upside shot.",
    },
    {
        "rank": 2,
        "file": "submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv",
        "tier": "A-balanced",
        "role": "best low-bad micro raw-corrector",
        "decision": "Submit as the balanced JEPA candidate if tiny raw-positive drift is acceptable.",
    },
    {
        "rank": 3,
        "file": "submission_jepa_block_consensus_rawcorr_micro_fea06910.csv",
        "tier": "A-strict",
        "role": "strict raw-neutral micro raw-corrector",
        "decision": "Submit when raw05-axis neutrality is the hard constraint.",
    },
    {
        "rank": 4,
        "file": "submission_jepa_block_consensus_rawcorr_4fd8bab2.csv",
        "tier": "B-stable",
        "role": "low-bad raw-corrected consensus",
        "decision": "Use as a stable fallback with lower bad-residual exposure.",
    },
    {
        "rank": 5,
        "file": "submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv",
        "tier": "B-refine",
        "role": "pre-micro refined raw-corrector",
        "decision": "Keep as a pre-micro reference candidate.",
    },
    {
        "rank": 6,
        "file": "submission_jepa_bridge_ensemble_c42fbf1e.csv",
        "tier": "B-baseline",
        "role": "balanced public-minimax/raw05 JEPA bridge",
        "decision": "Keep as the bridge baseline before consensus micro-correction.",
    },
    {
        "rank": 7,
        "file": "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
        "tier": "B-regularized",
        "role": "posterior-regularized bridge",
        "decision": "Use if posterior and bad-axis safety are preferred over focused proxy.",
    },
    {
        "rank": 8,
        "file": "submission_jepa_public_minimax_bridge_84b71a03.csv",
        "tier": "C-bridge",
        "role": "strict raw-negative public-minimax bridge",
        "decision": "Keep as the simplest public-minimax bridge sanity candidate.",
    },
    {
        "rank": 9,
        "file": "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv",
        "tier": "C-conservative",
        "role": "public block-entropy JEPA target-block projection",
        "decision": "Conservative older JEPA-block candidate; lower focused upside.",
    },
    {
        "rank": 10,
        "file": "submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv",
        "tier": "C-conservative",
        "role": "strict raw-negative block-entropy count candidate",
        "decision": "Conservative posterior/raw-safety reference.",
    },
    {
        "rank": 11,
        "file": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "tier": "known-public-control",
        "role": "best observed public LB anchor",
        "decision": "Actual public LB remains the known score to beat.",
    },
    {
        "rank": 12,
        "file": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "tier": "known-public-control",
        "role": "stage2 public anchor",
        "decision": "Public anchor used by the actual-anchor ranker.",
    },
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_metric_rows() -> pd.DataFrame:
    rows = []
    for order, name in enumerate(PREFERRED_SHORTLISTS):
        path = ROOT / name
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "file" not in frame.columns:
            continue
        frame = frame.copy()
        frame["metric_source"] = name
        frame["metric_source_order"] = order
        rows.append(frame)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True, sort=False)


def first_metric(metric_rows: pd.DataFrame, file_name: str) -> dict:
    if metric_rows.empty:
        return {}
    matches = metric_rows[metric_rows["file"].eq(file_name)].sort_values("metric_source_order")
    if matches.empty:
        return {}
    row = matches.iloc[0].to_dict()
    return row


def candidate_family(file_name: str) -> str:
    stem = file_name.replace("submission_", "").replace(".csv", "")
    for suffix in [
        "jepa_micro_bridge_ensemble",
        "jepa_block_consensus_rawcorr_micro",
        "jepa_block_consensus_rawcorr_refine",
        "jepa_block_consensus_rawcorr",
        "jepa_block_consensus_gate",
        "jepa_bridge_posteriorreg",
        "jepa_bridge_ensemble",
        "jepa_public_minimax_bridge",
        "jepa_public_blockentropy",
        "jepa_block_countshift",
        "raw05_jepa_axislocal",
        "raw05_jepa_directcon",
        "raw05_jepa_lowbadcon",
        "raw05_jepa_anchorrobust_graft",
        "raw05_jepa_structrefine",
        "raw05_jepa_axistrade",
        "raw05_jepa_axisrepair",
        "raw05_jepa_axisbridge",
        "raw05_jepa_blockcountreg",
        "raw05_jepa_tangentnull",
        "raw05_jepa_public6q3s4corr",
        "raw05_jepa_public6drift",
        "public6entropy",
        "jepa_energy_ensemble",
        "raw05_jepa_efback",
        "raw05_jepa_efgate",
        "raw05_jepa_compatband",
        "raw05_jepa_siganchor",
        "raw05_jepa_siggate",
        "raw05_jepa_efmicro",
        "raw05_jepa_energyfront",
        "raw_timeline_jepa_rescue",
        "hybrid_0p567",
        "hybrid_0p578",
        "ordinal_q_constraints",
        "jepa_latent",
    ]:
        if stem.startswith(suffix):
            return suffix
    return stem.rsplit("_", 1)[0]


def risk_flag(row: pd.Series) -> str:
    flags = []
    raw_delta = row.get("delta_vs_raw05_rawaxis")
    bad = row.get("bad_residual_axis_ratio")
    posterior = row.get("posterior_expected_public_vs_anchor")
    actual_anchor = row.get("actual_anchor_score_final")
    if pd.notna(raw_delta) and raw_delta > 1e-7:
        flags.append("raw+")
    if pd.notna(bad) and bad > 0.003:
        flags.append("bad-axis")
    if pd.notna(posterior) and posterior > 0.5769:
        flags.append("posterior")
    if pd.notna(actual_anchor) and actual_anchor > STAGE2_PUBLIC:
        flags.append("stage2-worse-ranker")
    return ",".join(flags) if flags else "none"


def build_constrained_shortlist(ranker: pd.DataFrame) -> pd.DataFrame:
    base = ranker[ranker["known_public"].isna()].copy()
    specs = [
        (
            "balanced_raw_le_1e-7_bad_le_0p0025_posterior_le_0p5769",
            (base["delta_vs_raw05_rawaxis"] <= 1e-7)
            & (base["bad_residual_axis_ratio"] <= 0.0025)
            & (base["posterior_expected_public_vs_anchor"] <= 0.5769),
            30,
        ),
        (
            "strict_raw_le_0_bad_le_0p0025_posterior_le_0p5769",
            (base["delta_vs_raw05_rawaxis"] <= 0.0)
            & (base["bad_residual_axis_ratio"] <= 0.0025)
            & (base["posterior_expected_public_vs_anchor"] <= 0.5769),
            30,
        ),
        (
            "public_minimax_bad_le_0p0025",
            (base["family"].eq("jepa_public_minimax_bridge"))
            & (base["bad_residual_axis_ratio"] <= 0.0025),
            12,
        ),
    ]
    cols = [
        "file",
        "source",
        "source_rank",
        "family",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "min_prob",
        "max_prob",
    ]
    rows = []
    for name, mask, limit in specs:
        part = base[mask].sort_values("actual_anchor_score_final").head(limit).copy()
        part.insert(0, "filter", name)
        part.insert(1, "filter_rank", range(1, len(part) + 1))
        rows.append(part[["filter", "filter_rank", *cols]])
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_target_assembly_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_target_ablation_assembly_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "actual_probe_s1_raw",
            frame["bucket"].eq("actual_probe") & frame["label"].str.contains(r"\|S1=raw05", regex=True),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            8,
        ),
        (
            "pair_q2_s1_raw",
            frame["label"].str.contains(r"\|q2_s1=raw05", regex=True),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            8,
        ),
        (
            "conservative_q2_raw",
            frame["label"].str.contains(r"\|Q2=raw05", regex=True)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0012),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            8,
        ),
        (
            "best_target_assembly_overall",
            frame["label"].str.startswith(("donor_full:", "leave_one_raw:")),
            ["selection_score", "actual_anchor_score_final"],
            12,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "label",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file", "label"])


def build_target_weight_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_target_weight_optimizer_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    q3_boost = frame["w_Q3"].gt(1.0) & frame["template"].str.startswith("q2s1q3")
    specs = [
        (
            "q3boost_actual_probe",
            q3_boost,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            10,
        ),
        (
            "q3stress_raw_boundary",
            frame["template"].str.startswith("q2s1q3_stress")
            & (frame["w_Q3"] >= 1.30)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["actual_anchor_score_final", "selection_score"],
            10,
        ),
        (
            "q3boost_posterior_balanced",
            q3_boost
            & (frame["posterior_expected_public_vs_anchor"] <= 0.5770)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0018),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            8,
        ),
        (
            "target_weight_low_bad",
            frame["bucket"].eq("low_bad"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            8,
        ),
        (
            "q2_atten_balanced",
            frame["bucket"].eq("balanced") & frame["w_Q2"].lt(1.0),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            8,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "w_Q2",
        "w_S1",
        "w_Q3",
        "w_S4",
        "label",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file", "label"])


def build_q3_counterweight_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_q3stress_counterweight_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "q3cw_actual_probe",
            frame["bucket"].eq("actual_probe"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cw_raw_boundary",
            frame["bucket"].eq("raw_boundary"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cw_strict_raw",
            frame["delta_vs_raw05_rawaxis"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cw_low_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00165,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            10,
        ),
        (
            "q3cw_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.57690,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "target_mask",
        "cell_gate",
        "alpha",
        "base_file",
        "counter_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_q3_counterweight_local_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_q3stress_counterweight_local_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "q3cwlocal_actual_probe",
            frame["bucket"].eq("actual_probe"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cwlocal_raw_boundary",
            frame["bucket"].eq("raw_boundary"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cwlocal_strict_raw",
            frame["delta_vs_raw05_rawaxis"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "q3cwlocal_low_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00150,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            10,
        ),
        (
            "q3cwlocal_very_low_bad",
            frame["bucket"].eq("very_low_bad"),
            ["bad_residual_axis_ratio", "actual_anchor_score_final"],
            10,
        ),
        (
            "q3cwlocal_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.576895,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "profile",
        "alpha",
        "base_file",
        "counter_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_context_target_energy_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_context_target_energy_gate_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "ctxenergy_actual_probe",
            frame["bucket"].eq("actual_probe"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "ctxenergy_raw_boundary",
            frame["delta_vs_raw05_rawaxis"] <= 1.0e-7,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "ctxenergy_energy_guardrail",
            (frame["energy_delta_vs_base"] <= -0.025)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7),
            ["actual_anchor_score_final", "energy_delta_vs_base"],
            10,
        ),
        (
            "ctxenergy_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.576895,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "ctxenergy_strict_raw",
            frame["delta_vs_raw05_rawaxis"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "ctxenergy_low_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00172,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            10,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "profile",
        "alpha",
        "energy_gate",
        "energy_gate_mean",
        "energy_delta_vs_base",
        "base_file",
        "counter_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_energy_frontier_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_energy_constrained_frontier_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "energyfront_actual_frontier",
            frame["bucket"].eq("frontier_actual"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "energyfront_raw_boundary",
            frame["delta_vs_raw05_rawaxis"] <= 1.0e-7,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "energyfront_energy_improved",
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "energyfront_strict_raw",
            frame["delta_vs_raw05_rawaxis"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "energyfront_very_low_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00085,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            12,
        ),
        (
            "energyfront_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.576895,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_energyfront_microrefine_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_energyfront_microrefine_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "efmicro_actual_lowbad",
            frame["bucket"].eq("micro_actual"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efmicro_lowest_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00050,
            ["bad_residual_axis_ratio", "actual_anchor_score_final"],
            12,
        ),
        (
            "efmicro_energy_improved",
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efmicro_raw_tight",
            frame["delta_vs_raw05_rawaxis"] <= 8.0e-8,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efmicro_strict_lowbad",
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00055),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
        (
            "efmicro_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.57690,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            10,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_efmicro_gate_refine_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_efmicro_gate_refine_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "efgate_actual_guarded",
            frame["bucket"].eq("gate_actual"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efgate_ultralow_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00010,
            ["bad_residual_axis_ratio", "actual_anchor_score_final"],
            12,
        ),
        (
            "efgate_raw_tight",
            frame["delta_vs_raw05_rawaxis"] <= 8.0e-8,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efgate_energy_improved",
            frame["energy_delta_vs_base"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efgate_posterior_safe",
            frame["posterior_expected_public_vs_anchor"] <= 0.57690,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "gate_p10",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_efgate_backoff_frontier_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_efgate_backoff_frontier_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "efback_actual_compromise",
            frame["bucket"].eq("backoff_actual"),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efback_risk_none",
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00060)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57690),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efback_ultralow_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00012,
            ["bad_residual_axis_ratio", "actual_anchor_score_final"],
            12,
        ),
        (
            "efback_raw_tight",
            frame["delta_vs_raw05_rawaxis"] <= 8.0e-8,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efback_energy_improved",
            frame["energy_delta_vs_base"] <= 0.0,
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            12,
        ),
        (
            "efback_posterior_floor",
            frame["posterior_expected_public_vs_anchor"] <= 0.57689,
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            12,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "blend_profile",
        "lambda",
        "row_gate",
        "gate_mean",
        "gate_p10",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_sigreg_gated_microrefine_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_sigreg_gated_microrefine_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame

    rows = []
    specs = [
        (
            "siggate_combined",
            frame["bucket"].eq("siggate_combined"),
            ["sigreg_rank_score", "actual_anchor_score_final"],
            16,
        ),
        (
            "siggate_health",
            frame["quick_lejepa_health"] <= 9.75,
            ["quick_lejepa_health", "actual_anchor_score_final"],
            16,
        ),
        (
            "siggate_ultralow_bad",
            frame["bad_residual_axis_ratio"].abs() <= 0.00003,
            ["bad_residual_axis_ratio", "quick_lejepa_health"],
            16,
        ),
        (
            "siggate_energy_guarded",
            frame["energy_delta_vs_base"] <= 0.0,
            ["actual_anchor_score_final", "quick_lejepa_health"],
            16,
        ),
        (
            "siggate_posterior_floor",
            frame["posterior_expected_public_vs_anchor"] <= 0.57689,
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            12,
        ),
        (
            "siggate_raw_tight",
            frame["delta_vs_raw05_rawaxis"] <= 8.5e-8,
            ["actual_anchor_score_final", "quick_lejepa_health"],
            16,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "quick_lejepa_health",
        "sigreg_rank_score",
        "energy_delta_vs_base",
        "public_norm_delta_mean",
        "row_aniso_delta_mean",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "sig_gate_mean",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_sigreg_micro_anchor_refine_addendum() -> pd.DataFrame:
    path = ROOT / "raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv"
    if not path.exists():
        return pd.DataFrame()

    frame = pd.read_csv(path).copy()
    if frame.empty:
        return frame
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()

    rows = []
    specs = [
        (
            "siganchor_actual_compromise",
            frame["bucket"].isin(["siganchor_balanced", "siganchor_rank_fallback"]),
            ["actual_anchor_score_final", "bad_abs"],
            18,
        ),
        (
            "siganchor_health",
            frame["quick_lejepa_health"] <= 9.75,
            ["quick_lejepa_health", "actual_anchor_score_final"],
            16,
        ),
        (
            "siganchor_lowbad_recovered",
            frame["bucket"].eq("siganchor_recovered_lowbad"),
            ["bad_abs", "actual_anchor_score_final"],
            16,
        ),
        (
            "siganchor_posterior_floor",
            frame["posterior_expected_public_vs_anchor"] <= 0.576895,
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            16,
        ),
        (
            "siganchor_energy_guarded",
            frame["energy_delta_vs_base"] <= 0.0,
            ["actual_anchor_score_final", "quick_lejepa_health"],
            18,
        ),
    ]
    cols = [
        "file",
        "bucket",
        "direction",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "bad_abs",
        "quick_lejepa_health",
        "anchor_rank_score",
        "energy_delta_vs_base",
        "public_norm_delta_mean",
        "row_aniso_delta_mean",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "base_file",
        "donor_file",
    ]
    for category, mask, sort_cols, limit in specs:
        part = frame[mask].sort_values(sort_cols).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def build_lejepa_sigreg_addendum() -> pd.DataFrame:
    if not LEJEPA_SIGREG_AUDIT.exists():
        return pd.DataFrame()

    frame = pd.read_csv(LEJEPA_SIGREG_AUDIT).copy()
    if frame.empty:
        return frame

    rows = []
    actual = pd.to_numeric(frame.get("actual_anchor_score_final"), errors="coerce")
    bad = pd.to_numeric(frame.get("bad_residual_axis_ratio"), errors="coerce")
    specs = [
        (
            "sigreg_combined_best",
            frame["lejepa_combined_rank"].notna(),
            ["lejepa_combined_rank", "actual_anchor_score_final"],
            16,
        ),
        (
            "sigreg_micro_balanced",
            frame["family"].eq("raw05_jepa_efmicro") & actual.notna() & (actual <= 0.5778390),
            ["lejepa_combined_rank", "actual_anchor_score_final"],
            16,
        ),
        (
            "sigreg_actual_frontier_with_health",
            actual.notna() & (actual <= 0.5778390),
            ["actual_anchor_score_final", "lejepa_residual_health"],
            16,
        ),
        (
            "sigreg_lowbad_health",
            actual.notna() & bad.notna() & (bad.abs() <= 0.00012),
            ["lejepa_residual_health", "actual_anchor_score_final"],
            16,
        ),
        (
            "sigreg_energyfront_context",
            frame["family"].eq("raw05_jepa_energyfront"),
            ["actual_anchor_score_final", "lejepa_residual_health"],
            12,
        ),
        (
            "sigreg_axisbridge_health",
            frame["family"].eq("raw05_jepa_axisbridge"),
            ["lejepa_combined_rank", "lejepa_residual_health"],
            12,
        ),
        (
            "sigreg_axisrepair_health",
            frame["family"].eq("raw05_jepa_axisrepair"),
            ["lejepa_combined_rank", "lejepa_residual_health"],
            12,
        ),
        (
            "sigreg_axistrade_health",
            frame["family"].eq("raw05_jepa_axistrade"),
            ["lejepa_combined_rank", "lejepa_residual_health"],
            12,
        ),
        (
            "sigreg_anchorrobust_graft_health",
            frame["family"].eq("raw05_jepa_anchorrobust_graft"),
            ["lejepa_combined_rank", "lejepa_residual_health"],
            12,
        ),
        (
            "sigreg_structrefine_health",
            frame["family"].eq("raw05_jepa_structrefine"),
            ["lejepa_combined_rank", "lejepa_residual_health"],
            12,
        ),
    ]
    cols = [
        "file",
        "family",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "lejepa_residual_health",
        "lejepa_combined_rank",
        "health_rank",
        "actual_rank",
        "bad_rank",
        "all_sigreg_global",
        "target_q3s4_sigreg_global",
        "public_axis_sigreg_global",
        "all_cov_eig_cv",
        "metric_source",
    ]
    use_cols = [col for col in cols if col in frame.columns]
    for category, mask, sort_cols, limit in specs:
        sort_use = [col for col in sort_cols if col in frame.columns]
        part = frame[mask].sort_values(sort_use).head(limit).copy()
        part.insert(0, "category", category)
        part.insert(1, "category_rank", range(1, len(part) + 1))
        rows.append(part[["category", "category_rank", *use_cols]])

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).drop_duplicates(["category", "file"])


def format_markdown_table(frame: pd.DataFrame, cols: list[str]) -> str:
    use = frame[cols].copy()
    for col in use.columns:
        if pd.api.types.is_float_dtype(use[col]):
            use[col] = use[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
    use = use.fillna("").astype(str)
    widths = {
        col: max([len(col), *[len(value) for value in use[col].tolist()]])
        for col in use.columns
    }

    def render_row(values: list[str]) -> str:
        return "| " + " | ".join(
            value.ljust(widths[col]) for value, col in zip(values, use.columns)
        ) + " |"

    header = render_row(list(use.columns))
    separator = "| " + " | ".join("-" * widths[col] for col in use.columns) + " |"
    body = [render_row(row) for row in use.to_numpy().tolist()]
    return "\n".join([header, separator, *body])


def main() -> None:
    ranker = read_csv(RANKER)
    calibration = read_csv(CALIBRATION)
    metric_rows = load_metric_rows()
    sigreg_audit = read_csv(LEJEPA_SIGREG_AUDIT)

    if ranker.empty:
        raise FileNotFoundError(RANKER)

    ranker = ranker.copy()
    ranker["family"] = ranker["file"].map(candidate_family)
    sigreg_by_file = {}
    if not sigreg_audit.empty and "file" in sigreg_audit.columns:
        sigreg_by_file = {
            row["file"]: row
            for row in sigreg_audit.to_dict(orient="records")
        }

    rows = []
    for item in PRIORITY:
        file_name = item["file"]
        row = dict(item)

        rank_matches = ranker[ranker["file"].eq(file_name)]
        if not rank_matches.empty:
            row.update(rank_matches.iloc[0].to_dict())

        metric = first_metric(metric_rows, file_name)
        for col in [
            "label",
            "bucket",
            "mode",
            "profile",
            "gate_mode",
            "base_file",
            "local_file",
            "axis_file",
            "axis_base_file",
            "donor_file",
            "safety_file",
            "robust_file",
            "step_mask",
            "step_strength",
            "step_cap",
            "safety_mask",
            "safety_eta",
            "robust_mask",
            "robust_alpha",
            "robust_cap",
            "keep_orth",
            "raw_mask",
            "donor_mask",
            "motif_mask",
            "graft_mask",
            "mask_name",
            "raw_alpha",
            "donor_alpha",
            "motif_alpha",
            "alpha",
            "strength",
            "cap",
            "q3s4_repair",
            "axislocal_score",
            "axis_prior_score",
            "direct_score",
            "lowbad_score",
            "rank_score",
            "strict_hit",
            "tight_local_hit",
            "strict_lowbad_hit",
            "near_lowbad_hit",
            "available_raw05_relative_delta_vs_raw05_public",
            "available_raw05_relative_model_spread",
            "metric_source",
            "actual_anchor_score_final",
            "mean_actual_anchor",
            "min_set_score",
            "max_set_score",
            "focused_scenario_score",
            "compact_focused_score",
            "posterior_expected_public_vs_anchor",
            "raw_axis_expected_public_vs_stage2",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "ordinal_axis_ratio",
            "mean_abs_move_vs_raw05",
            "mean_abs_move_vs_axis",
            "mean_abs_move_vs_base",
            "mean_abs_move_vs_donor",
            "target_motif_retention",
            "q3s4_motif_proj",
            "q3s4_motif_cos",
            "q3s4_motif_orth_ratio",
            "key_ok",
            "duplicate_keys",
            "null_probs",
            "min_prob_integrity",
            "max_prob_integrity",
        ]:
            if col in metric and pd.notna(metric[col]):
                row[col] = metric[col]

        sigreg_metric = sigreg_by_file.get(file_name, {})
        for col in [
            "lejepa_residual_health",
            "lejepa_combined_rank",
            "health_rank",
            "actual_rank",
            "bad_rank",
            "all_sigreg_global",
            "target_q3s4_sigreg_global",
            "public_axis_sigreg_global",
            "all_cov_eig_cv",
        ]:
            if col in sigreg_metric and pd.notna(sigreg_metric[col]):
                row[col] = sigreg_metric[col]

        row["family"] = candidate_family(file_name)
        row["ranker_gap_vs_raw05_actual"] = row.get("actual_anchor_score_final", pd.NA) - RAW05_PUBLIC
        row["ranker_gap_vs_stage2_actual"] = row.get("actual_anchor_score_final", pd.NA) - STAGE2_PUBLIC
        row["posterior_gap_vs_raw05_actual"] = row.get("posterior_expected_public_vs_anchor", pd.NA) - RAW05_PUBLIC
        row["risk_flags"] = risk_flag(pd.Series(row))
        rows.append(row)

    priority = pd.DataFrame(rows).sort_values("rank").reset_index(drop=True)
    priority["rank"] = np.arange(1, len(priority) + 1)

    shortlist = ranker[ranker["known_public"].isna()].copy()
    family_summary = (
        shortlist.groupby("family", dropna=False)
        .agg(
            candidates=("file", "count"),
            best_actual_anchor_score=("actual_anchor_score_final", "min"),
            median_actual_anchor_score=("actual_anchor_score_final", "median"),
            best_posterior=("posterior_expected_public_vs_anchor", "min"),
            best_raw_delta=("delta_vs_raw05_rawaxis", "min"),
            median_bad_axis=("bad_residual_axis_ratio", "median"),
            best_mean_abs_move=("mean_abs_move_vs_raw05", "min"),
        )
        .reset_index()
        .sort_values(["best_actual_anchor_score", "median_bad_axis"])
    )

    priority.to_csv(OUT_CSV, index=False)
    family_summary.to_csv(OUT_FAMILY, index=False)
    constrained = build_constrained_shortlist(ranker)
    constrained.to_csv(OUT_CONSTRAINED, index=False)
    target_assembly = build_target_assembly_addendum()
    target_assembly.to_csv(OUT_TARGET_ASSEMBLY, index=False)
    target_weight = build_target_weight_addendum()
    target_weight.to_csv(OUT_TARGET_WEIGHT, index=False)
    q3_counterweight = build_q3_counterweight_addendum()
    q3_counterweight.to_csv(OUT_Q3_COUNTERWEIGHT, index=False)
    q3_counterweight_local = build_q3_counterweight_local_addendum()
    q3_counterweight_local.to_csv(OUT_Q3_COUNTERWEIGHT_LOCAL, index=False)
    context_target_energy = build_context_target_energy_addendum()
    context_target_energy.to_csv(OUT_CONTEXT_TARGET_ENERGY, index=False)
    energy_frontier = build_energy_frontier_addendum()
    energy_frontier.to_csv(OUT_ENERGY_FRONTIER, index=False)
    energyfront_micro = build_energyfront_microrefine_addendum()
    energyfront_micro.to_csv(OUT_ENERGYFRONT_MICRO, index=False)
    efmicro_gate = build_efmicro_gate_refine_addendum()
    efmicro_gate.to_csv(OUT_EFMICRO_GATE, index=False)
    efgate_backoff = build_efgate_backoff_frontier_addendum()
    efgate_backoff.to_csv(OUT_EFGATE_BACKOFF, index=False)
    sigreg_gated = build_sigreg_gated_microrefine_addendum()
    sigreg_gated.to_csv(OUT_SIGREG_GATED, index=False)
    sigreg_anchor = build_sigreg_micro_anchor_refine_addendum()
    sigreg_anchor.to_csv(OUT_SIGREG_ANCHOR, index=False)
    lejepa_sigreg = build_lejepa_sigreg_addendum()
    lejepa_sigreg.to_csv(OUT_LEJEPA_SIGREG, index=False)

    raw05_cal = calibration[
        calibration["file"].eq("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv")
    ].iloc[0]
    residual_cal = calibration[
        calibration["file"].eq("submission_jepa_latent_residual_probe.csv")
    ].iloc[0]

    md_cols = [
        "rank",
        "file",
        "tier",
        "actual_anchor_score_final",
        "focused_scenario_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "lejepa_residual_health",
        "lejepa_combined_rank",
        "risk_flags",
    ]
    fam_cols = [
        "family",
        "candidates",
        "best_actual_anchor_score",
        "best_posterior",
        "best_raw_delta",
        "median_bad_axis",
    ]

    md = []
    md.append("# Final JEPA Candidate Priority 2026-05-27")
    md.append("")
    md.append("This table combines the JEPA hidden-block candidate metrics with the actual-public-anchor ranker.")
    md.append("The ranker anchors each inverse-fit public scenario/mask combo to the observed stage2 public LB instead of trusting raw pseudo-public CE as an absolute score.")
    md.append("")
    md.append("## Calibration Caveat")
    md.append("")
    md.append(
        f"- raw05 actual public LB is {RAW05_PUBLIC:.10f}, but the ranker scores it at "
        f"{raw05_cal['actual_anchor_score_final']:.10f}; it is pessimistic by "
        f"{raw05_cal['known_public_error_mean']:.10f}."
    )
    md.append(
        f"- direct JEPA latent residual actual public LB is {residual_cal['known_public']:.10f}, "
        f"but the ranker scores it at {residual_cal['actual_anchor_score_final']:.10f}; "
        f"it is optimistic by {-residual_cal['known_public_error_mean']:.10f}."
    )
    md.append("- Therefore, use `actual_anchor_score_final` as a public-consistency filter, not as proof that a candidate beats raw05.")
    md.append("")
    md.append("## Priority")
    md.append("")
    md.append(format_markdown_table(priority, md_cols))
    md.append("")
    md.append("## Family Summary")
    md.append("")
    md.append(format_markdown_table(family_summary.head(16), fam_cols))
    md.append("")
    md.append("## Constrained Shortlist Checks")
    md.append("")
    constrained_cols = [
        "filter",
        "filter_rank",
        "file",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
    ]
    md.append(format_markdown_table(constrained.head(24), constrained_cols))
    md.append("")
    if not target_assembly.empty:
        md.append("## Target Assembly Addendum")
        md.append("")
        md.append(
            "Target-column ablation shows the JEPA signal is block-level: single-target grafts are weak, "
            "while full donors or leave-one-raw variants preserve most of the gain."
        )
        md.append("")
        target_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "label",
        ]
        md.append(format_markdown_table(target_assembly.head(28), target_cols))
        md.append("")
    if not target_weight.empty:
        md.append("## Target Weight Addendum")
        md.append("")
        md.append(
            "Continuous target weighting found a new JEPA block pattern: keep Q3 slightly above donor strength "
            "while attenuating Q2/S1. This is a higher-upside probe, with posterior-risk tradeoff."
        )
        md.append("")
        weight_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "w_Q2",
            "w_S1",
            "w_Q3",
            "label",
        ]
        md.append(format_markdown_table(target_weight.head(34), weight_cols))
        md.append("")
    if not q3_counterweight.empty:
        md.append("## Q3 Stress Counterweight Addendum")
        md.append("")
        md.append(
            "Counterweight search keeps the Q3 stress signal and blends non-Q3 target blocks toward low-bad/strict candidates. "
            "It did not beat the raw actual-anchor peak, but it sharply lowers bad-axis exposure while staying near the Q3 stress frontier."
        )
        md.append("")
        q3cw_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "target_mask",
            "alpha",
            "base_file",
            "counter_file",
        ]
        md.append(format_markdown_table(q3_counterweight.head(40), q3cw_cols))
        md.append("")
    if not q3_counterweight_local.empty:
        md.append("## Q3 Stress Counterweight Local Addendum")
        md.append("")
        md.append(
            "Local counterweight refine keeps the Q3/S4 stress base, searches nearby non-Q3/S4 target profiles, "
            "and adds very-low-bad candidates so the JEPA signal can be tested with a tighter bad-axis guardrail."
        )
        md.append("")
        q3cwlocal_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "profile",
            "alpha",
            "base_file",
            "counter_file",
        ]
        md.append(format_markdown_table(q3_counterweight_local.head(48), q3cwlocal_cols))
        md.append("")
    if not context_target_energy.empty:
        md.append("## Context-Target Energy Gate Addendum")
        md.append("")
        md.append(
            "This addendum uses the I-JEPA context-target idea directly: non-Q3/S context predictions define the context block, "
            "Q3/S4 defines the target block, and counterweight rows are kept when they lower learned compatibility energy. "
            "The branch is a guardrail/diagnostic branch, not the current actual-anchor frontier."
        )
        md.append("")
        ctxenergy_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "profile",
            "alpha",
            "energy_gate",
            "energy_delta_vs_base",
            "base_file",
            "counter_file",
        ]
        md.append(format_markdown_table(context_target_energy.head(48), ctxenergy_cols))
        md.append("")
    if not energy_frontier.empty:
        md.append("## Energy-Constrained Frontier Addendum")
        md.append("")
        md.append(
            "This branch stitches the strongest local Q3-counterweight frontier toward low-bad/context-energy donors. "
            "It is the first branch in this sequence that improves the local actual-anchor proxy while cutting bad-axis exposure sharply."
        )
        md.append("")
        energyfront_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "energy_delta_vs_base",
            "blend_profile",
            "beta",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(energy_frontier.head(56), energyfront_cols))
        md.append("")
    if not energyfront_micro.empty:
        md.append("## Energyfront Microrefine Addendum")
        md.append("")
        md.append(
            "This branch performs a second-stage local stitch inside the energyfront manifold. "
            "The main value is not a new actual-anchor minimum, but a sharp bad-axis collapse while staying near the frontier."
        )
        md.append("")
        efmicro_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "energy_delta_vs_base",
            "blend_profile",
            "beta",
            "row_gate",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(energyfront_micro.head(58), efmicro_cols))
        md.append("")
    if not efmicro_gate.empty:
        md.append("## Efmicro Row-Gate Refine Addendum")
        md.append("")
        md.append(
            "This branch tightens the row-level gate around the energyfront/micro frontier. "
            "It does not recover the actual-anchor frontier, but it creates the strongest bad-axis collapse seen in the raw05-compatible JEPA branch."
        )
        md.append("")
        efgate_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "energy_delta_vs_base",
            "blend_profile",
            "beta",
            "row_gate",
            "gate_mean",
            "gate_p10",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(efmicro_gate.head(60), efgate_cols))
        md.append("")
    if not efgate_backoff.empty:
        md.append("## EFGate Backoff Frontier Addendum")
        md.append("")
        md.append(
            "This branch interpolates between the actual-anchor micro/energyfront frontier and the efgate low-bad diagnostics. "
            "It is useful as a middle point: weaker actual-anchor than micro, but cleaner posterior/bad-axis than the frontier."
        )
        md.append("")
        efback_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "energy_delta_vs_base",
            "blend_profile",
            "lambda",
            "row_gate",
            "gate_mean",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(efgate_backoff.head(60), efback_cols))
        md.append("")
    if not sigreg_gated.empty:
        md.append("## SIGReg-Gated Microrefine Addendum")
        md.append("")
        md.append(
            "This branch applies the LeJEPA residual-health idea inside the row gate itself. "
            "The candidates are mostly ultra-low-bad diagnostics around the efgate/backoff manifold, not replacements for the actual-anchor frontier."
        )
        md.append("")
        siggate_cols = [
            "category",
            "category_rank",
            "file",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "quick_lejepa_health",
            "sigreg_rank_score",
            "energy_delta_vs_base",
            "blend_profile",
            "beta",
            "row_gate",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(sigreg_gated.head(64), siggate_cols))
        md.append("")
    if not sigreg_anchor.empty:
        md.append("## SIGReg Micro Anchor Refine Addendum")
        md.append("")
        md.append(
            "This branch keeps the LeJEPA/SIGReg gate near the efmicro/energyfront actual anchors. "
            "It recovers most actual-anchor strength from the extreme siggate probes, but the best rows are compromise candidates rather than a new frontier."
        )
        md.append("")
        siganchor_cols = [
            "category",
            "category_rank",
            "file",
            "bucket",
            "direction",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "quick_lejepa_health",
            "anchor_rank_score",
            "energy_delta_vs_base",
            "blend_profile",
            "beta",
            "row_gate",
            "base_file",
            "donor_file",
        ]
        md.append(format_markdown_table(sigreg_anchor.head(64), siganchor_cols))
        md.append("")
    if not lejepa_sigreg.empty:
        md.append("## LeJEPA SIGReg Residual-Health Addendum")
        md.append("")
        md.append(
            "This addendum applies the LeJEPA non-degeneracy idea to row-level logit residual embeddings. "
            "Lower `lejepa_residual_health` means the residual move is less collapsed/anisotropic under random-projection Gaussian tests. "
            "Use this as a regularizer on top of actual-anchor, posterior, raw-axis, and bad-axis checks, not as a standalone submission score."
        )
        md.append("")
        sigreg_cols = [
            "category",
            "category_rank",
            "file",
            "family",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "lejepa_residual_health",
            "lejepa_combined_rank",
            "all_sigreg_global",
            "target_q3s4_sigreg_global",
            "public_axis_sigreg_global",
        ]
        md.append(format_markdown_table(lejepa_sigreg.head(64), sigreg_cols))
        md.append("")
    md.append("## Decision Rule")
    md.append("")
    md.append("- If one JEPA candidate can be submitted, prefer rank 1 for upside, rank 2 for low-bad balance, or rank 3 for strict raw05-axis neutrality.")
    md.append("- Treat `actual_probe_s1_raw` target-assembly rows as high-upside probes only: they slightly improve the actual-anchor proxy, but they raise posterior/bad-axis risk.")
    md.append("- Treat `pair_q2_s1_raw` rows as compromise probes: they keep most of the S1 raw actual-anchor upside while using Q2 raw to cut bad-axis exposure.")
    md.append("- Treat `conservative_q2_raw` rows as risk reducers: they give up a tiny amount of actual-anchor score while sharply lowering bad-axis exposure.")
    md.append("- Treat `q3boost_actual_probe` target-weight rows as the newest high-upside JEPA probe: actual-anchor improves, but posterior proxy is less safe than the main rank-1 candidate.")
    md.append("- Treat `q3stress_raw_boundary` rows as the safer edge of that high-upside branch: Q3 is boosted harder, while raw05-axis and bad-axis constraints are still just inside the guardrail.")
    md.append("- Treat `q3cw_actual_probe` rows as the cleaner Q3-stress compromise: slightly weaker actual-anchor than raw Q3 stress, but much lower bad-axis through non-Q3/S4 counterweighting.")
    md.append("- Treat `q3cwlocal_actual_probe` rows as the refined cleaner branch: they improve posterior/bad-axis versus the coarse counterweight while staying near the Q3-stress actual-anchor frontier.")
    md.append("- Treat `q3cwlocal_raw_boundary` or `q3cwlocal_strict_raw` rows as the guardrail variants when raw05-axis drift must stay under `1e-7` or below zero.")
    md.append("- Treat `q3cwlocal_very_low_bad` rows as diagnostic probes for whether public rewards the lowest bad-axis more than the best actual-anchor proxy.")
    md.append("- Treat `ctxenergy_*` rows as JEPA compatibility guardrails: they lower context-target energy and raw-axis drift, but they do not replace the local counterweight actual-anchor frontier.")
    md.append("- Treat `energyfront_actual_frontier` rows as the current raw05-compatible JEPA frontier: they preserve Q3-stress structure while cutting bad-axis to roughly `8e-4`.")
    md.append("- Treat `energyfront_energy_improved` and `energyfront_strict_raw` rows as the guarded variants when context-target energy or non-positive raw drift is required.")
    md.append("- Treat `efmicro_actual_lowbad` rows as second-stage bad-axis compensation probes: they give up only tiny actual-anchor margin while cutting bad-axis to roughly `4e-4`-`5e-4`.")
    md.append("- Treat `efmicro_energy_improved` and `efmicro_strict_lowbad` rows as diagnostic guardrails when row-level JEPA/bad-axis gates are more important than the best actual-anchor proxy.")
    md.append("- Treat `efgate_actual_guarded` rows as smooth posterior/low-bad diagnostics: q1light soft gates lower posterior and bad-axis but do not beat the micro actual frontier.")
    md.append("- Treat `efgate_ultralow_bad` and `efgate_raw_tight` rows as stress tests for whether public strongly rewards bad-axis collapse down to about `5e-5`.")
    md.append("- Treat `efback_actual_compromise` rows as risk-none middle points between micro and efgate: they give up actual-anchor margin to lower posterior and bad-axis.")
    md.append("- Treat `efback_ultralow_bad` rows as the strongest bad-axis stress tests, with some rows below `4e-5`.")
    md.append("- Treat `siggate_*` rows as LeJEPA-gated stress diagnostics: they can push bad-axis near zero while preserving raw-tightness, but current actual-anchor is weaker than efmicro/energyfront.")
    md.append("- Treat `siganchor_*` rows as compromise probes between efmicro and siggate: they recover most actual-anchor strength while lowering posterior/bad-axis versus the efmicro posterior-safe row, but they do not beat the efmicro frontier.")
    md.append("- Treat `axistrade_*` rows as the strongest direct motif/posterior repair probes so far: they satisfy the high-retention, posterior-safe, raw-tight tradeoff constraint, but their local edge versus raw05 is still below the local proxy resolution.")
    md.append("- Treat LeJEPA SIGReg as residual-health regularization: it demotes one-axis/anisotropic moves even when their actual-anchor proxy is strong.")
    md.append("- If optimizing actual-anchor only, `energyfront_a190aa25` remains the frontier; if choosing the most JEPA-balanced probe, prefer `efmicro_1859bae9` or `efmicro_9f19106d` before the more extreme efgate/backoff stress tests.")
    md.append("- Treat `target_weight_low_bad` rows as the cleaner Q2/S1 attenuation variant when bad-axis exposure matters.")
    md.append("- If preserving known public performance is more important than exploring new JEPA signal, raw05 remains the observed score to beat.")
    md.append("- Do not submit direct JEPA latent residual/Q2-forced variants without an explicit raw05-axis counter; observed public feedback already rejected that direction.")
    md.append("")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_FAMILY}")
    print(f"wrote {OUT_CONSTRAINED}")
    print(f"wrote {OUT_TARGET_ASSEMBLY}")
    print(f"wrote {OUT_TARGET_WEIGHT}")
    print(f"wrote {OUT_Q3_COUNTERWEIGHT}")
    print(f"wrote {OUT_Q3_COUNTERWEIGHT_LOCAL}")
    print(f"wrote {OUT_CONTEXT_TARGET_ENERGY}")
    print(f"wrote {OUT_ENERGY_FRONTIER}")
    print(f"wrote {OUT_ENERGYFRONT_MICRO}")
    print(f"wrote {OUT_EFMICRO_GATE}")
    print(f"wrote {OUT_EFGATE_BACKOFF}")
    print(f"wrote {OUT_SIGREG_GATED}")
    print(f"wrote {OUT_SIGREG_ANCHOR}")
    print(f"wrote {OUT_LEJEPA_SIGREG}")
    print(priority[md_cols].to_string(index=False))


if __name__ == "__main__":
    main()
