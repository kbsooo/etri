# HS-JEPA Pipeline Manifest

이 문서는 팀원이 OG 데이터에서 최종 제출/논문 산출물까지 어떤 경로로 이어지는지 한눈에 추적하도록 만든 역할 기반 pipeline manifest다.

## One-Command Entry

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

## Pipeline Diagram

```mermaid
flowchart TD
    CORE["HS-JEPA core architecture"] --> A["OG raw lifestyle context"]
    CORE --> C["Human-state listener context"]
    CORE --> D["Q/S route energy model"]
    A["OG raw lifestyle context"] --> C["Human-state listener context"]
    A --> D["Q/S route energy model"]
    B["Public LB sensor ledger"] --> E["Public-sensitive driver action field"]
    C --> E
    D --> F["Route-conserving S2 bridge decoder"]
    E --> F
    F --> G["Role-based submission packager"]
    G --> ADAPT["Sleep competition adapter"]
    CORE --> ADAPT
    B --> ADAPT
    ADAPT --> H["Claim readiness and paper packet"]
    G --> H["Claim readiness and paper packet"]
    F --> H
```

## Stage Table

| Stage | Role | Key Evidence | Boundary |
| --- | --- | --- | --- |
| `hsjepa_core_architecture` | Defines the reusable human-understanding mechanism before any sleep-competition target names are introduced. | Core status: core_ready_for_adapter<br>Core gates: 5/5<br>Ablation status: ablation_contract_ready | The core must not depend on S2, public LB sensors, submission files, or manual row ids. |
| `og_raw_lifestyle_context` | Provides train labels, submission key contract, and raw lifelog items. | OG records in contract: 3<br>Required missing: 0 | This stage is competition data, not external/private data. |
| `public_lb_sensor` | Uses public submission observations as a sensor for hidden row-target action response. | Ledger rows: 26<br>Pre-public-equation best: 0.5761589494<br>Current best: 0.5677475939 | This is not an OG-only claim; it is the competition-specific sensor path. |
| `human_state_listener_context` | Turns lifestyle/cohort context into target/cell orientation diagnostics. | Cell OOF AUC: 0.775<br>Row OOF AUC: 0.545 | Human-state is an orientation diagnostic, not a standalone row selector. |
| `route_energy_model` | Learns a target-route manifold from train labels and scores whether an action breaks it. | Primary route z-score: -9.66<br>S2 route z-score: -9.46 | Route energy proves candidate-pool structure, not private leaderboard safety. |
| `driver_action_field` | Selects sparse row-target cells that public sensor evidence says are worth moving. | Score breakthrough delta: -0.0084113555<br>Evidence roles: competition_primary, interpretable_s2_hub, human_state_probe | This stage is deliberately separated from the OG human-state representation claim. |
| `route_conserving_s2_bridge_decoder` | Pairs driver cells with same-row bridge cells that lower route energy and repeatedly use S2 as listener/hub. | Primary route delta vs null: -0.02457 vs -0.01090<br>S2 usage vs null: 1.000 vs 0.615 | S2 is a decoder listener/hub in this action space, not a universal sleep physiology claim. |
| `submission_packager` | Packages three role-based outputs without requiring historical version names. | Upload-safe roles: competition_primary, human_state_probe, interpretable_s2_hub<br>Validation passed: True | Upload safety is a format guarantee, not a score guarantee. |
| `mechanism_ablation_knockout` | Records which alternative worldviews public sensors and local stress audits killed or preserved. | Public worldviews killed: 5<br>Public worldviews survived: 2<br>Ablation status: mechanism_ablation_ready | This explains mechanism evidence; it is not a new private-score guarantee. |
| `general_architecture_boundary` | Separates reusable HS-JEPA modules from the sleep-competition S2/public-sensor instantiation. | Generality status: general_architecture_separated_with_case_boundary<br>Portability checks: 5/6<br>Nonblocking boundaries: remaining_generality_gap | The current strongest case study still uses a public-sensor assignment teacher. |
| `sleep_competition_adapter` | Maps HS-JEPA Core into Q/S listeners, route energy, public-sensor action evidence, and upload-safe sparse row-target outputs. | Adapter status: adapter_ready_with_public_sensor_boundary<br>Adapter score delta: -0.0084113555<br>Big-bet count: 4 | This adapter is a competition case study; it is not the general HS-JEPA architecture. |
| `claim_readiness_and_paper_packet` | Converts the runnable package into paper/team-facing evidence and method text. | Readiness status: paper_ready_with_boundary<br>Readiness gates: 7/7<br>Method title: Human-State JEPA: General Architecture with a Route-Conserving S2 Bridge Case Study | Paper claims must keep representation, public sensor, and action decoder separated. |

## Role-Based Outputs

| Role | Output file |
| --- | --- |
| `competition_primary` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` |
| `human_state_probe` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` |
| `interpretable_s2_hub` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` |

## Boundary

- Pure OG-only model: `False`
- Uses public LB sensor: `True`
- Human-state role: `orientation diagnostic, not complete row-target assignment solver`
- Competition decoder role: `public-sensitive row-target action solver with route-conserving S2 bridge`

## Summary

```text
The reusable mechanism is HS-JEPA Core: hidden state -> listener -> action-health -> invariant decoder.
The sleep competition adapter supplies Q/S listeners, public-sensor actions, route energy, and upload format.
The current LB breakthrough is adapter evidence; the paper claim must remain core-first.
The next jackpot is replacing public-sensor assignment with an OG-only human-state teacher.
```
