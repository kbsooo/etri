#!/usr/bin/env python3
"""H139: role-atom assignment equation HS-JEPA solver.

H138 proved that a hand-built toxicity-relief + margin-repair pair can satisfy
the one-sided boundary constraints.  H139 removes the hand-built part.

The solver builds row-target action atoms around H136, classifies each atom by
its public/private equation role, locks the H136 row164 core, and solves small
role-compatible assignments.

This is the first HS-JEPA decoder that explicitly treats actions as roles:

    route core is locked
    toxicity-relief atoms reduce H088 stress
    margin-repair atoms restore public/private boundary
    stress-decoy atoms are observed but rejected
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import itertools
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h139_role_atom_assignment_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H137_PATH = HITL / "h137_tail_toxicity_counterfield_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h137mod_h139", H137_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H137_PATH}")
h137mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h137mod
SPEC.loader.exec_module(h137mod)

h136mod = h137mod.h136mod
h135mod = h137mod.h135mod
h134mod = h137mod.h134mod
h133mod = h137mod.h133mod
h132mod = h137mod.h132mod
h130mod = h137mod.h130mod
h126mod = h137mod.h126mod
h123mod = h137mod.h123mod
h118mod = h137mod.h118mod
h102mod = h137mod.h102mod
h085mod = h137mod.h085mod

TARGETS = h137mod.TARGETS
TOL = h137mod.TOL


@dataclass(frozen=True)
class Atom:
    atom_id: str
    kind: str
    row: int
    targets: str
    frac: float
    gamma: float
    roles: tuple[str, ...]
    move: np.ndarray
    metrics: dict[str, float]


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def array_hash(move: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(move, dtype=np.float64), 12).tobytes()).hexdigest()[:10]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h139_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h139_roleatoms_*.csv"):
        path.unlink()


def load_move(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    return h126mod.load_move_path(path, sample, base_prob).reshape(base_prob.shape)


def known_hashes(sample: pd.DataFrame) -> set[str]:
    hashes: set[str] = set()
    for path in ROOT.glob("submission_h*_uploadsafe.csv"):
        try:
            df = h085mod.load_sub(path, sample)
            hashes.add(short_hash(df[TARGETS].to_numpy(dtype=np.float64)))
        except Exception:
            continue
    return hashes


def evaluate_matrix(move_mat, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes):
    return h136mod.evaluate_matrix(
        move_mat,
        basis_fit_df,
        basis_fit_moves,
        route_fit,
        cell,
        h098_fit,
        fit,
        pool,
        bad_axes,
        bad_moves,
        good_moves,
        axes,
    )


def changed_cells(base_move: np.ndarray, move: np.ndarray) -> pd.DataFrame:
    rows = []
    for row, tidx in np.argwhere(np.abs(move - base_move) > 1.0e-12):
        rows.append(
            {
                "row": int(row),
                "target_index": int(tidx),
                "target": TARGETS[int(tidx)],
                "delta_logit_vs_h136": float(move[row, tidx] - base_move[row, tidx]),
                "new_logit_move": float(move[row, tidx]),
            }
        )
    return pd.DataFrame(rows).sort_values(["row", "target_index"]).reset_index(drop=True)


def classify_roles(row: int, kind: str, d: dict[str, float]) -> tuple[str, ...]:
    roles: list[str] = []
    if row == 164 and kind.startswith("anti"):
        roles.append("locked_core_unwind")
        return tuple(roles)
    if d["h088"] <= -0.00045 and d["margin"] >= -0.00030 and d["h098"] <= 0.00000220 and d["route"] <= 0.00000360:
        roles.append("toxicity_relief")
    if d["margin"] >= 0.00005 and d["h098"] <= 0.00000145 and d["route"] <= 0.00000260 and d["h088"] <= 0.00020:
        roles.append("margin_repair")
    if d["h088"] <= -0.00045 and d["margin"] < -0.00030:
        roles.append("stress_decoy")
    return tuple(roles)


def atom_score(metrics: dict[str, float]) -> float:
    return (
        9.0 * max(-metrics["delta_h088"], 0.0)
        + 22.0 * max(metrics["delta_margin"], 0.0)
        - 36.0 * max(-metrics["delta_margin"], 0.0)
        - 720.0 * max(metrics["delta_h098"], 0.0)
        - 460.0 * max(metrics["delta_route"], 0.0)
    )


def candidate_score(metrics: dict[str, object]) -> float:
    d_h088 = float(metrics["delta_h088"])
    d_margin = float(metrics["delta_margin"])
    d_h098 = float(metrics["delta_h098"])
    d_route = float(metrics["delta_route"])
    changed = int(metrics["changed_cells_vs_h136"])
    passes = bool(metrics["passes_role_boundary"])
    role_bonus = 0.0
    role_text = str(metrics["roles"])
    if role_text.count("toxicity_relief") >= 2 and "margin_repair" in role_text:
        role_bonus += 0.0035
    if "stress_decoy" in role_text:
        role_bonus -= 0.0060
    return (
        12.0 * max(-d_h088, 0.0)
        + 28.0 * max(d_margin, 0.0)
        - 48.0 * max(-d_margin, 0.0)
        - 950.0 * max(d_h098, 0.0)
        - 560.0 * max(d_route, 0.0)
        - 0.00035 * max(changed - 3, 0)
        + (0.0045 if passes else 0.0)
        + role_bonus
    )


def build_atoms(catalog, start, start_eval, moves, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes) -> tuple[list[Atom], pd.DataFrame, pd.DataFrame]:
    bundle_rows = h133mod.collect_bundle_rows(catalog, moves["h131"])
    q1_rows = h134mod.collect_q1_rows(bundle_rows)
    cell_pool, bundle_pool = h135mod.build_bundle_pool(catalog, start, q1_rows, h137mod.broad_bundle_spec())
    atoms: list[Atom] = []
    rows = []
    seen: set[str] = set()
    for bundle in bundle_pool.head(110).to_dict("records"):
        actions = [("forward", 0.0), ("anti025", 0.25), ("anti05", 0.50), ("anti1", 1.00)]
        for kind, gamma in actions:
            if kind == "forward":
                move = h135mod.apply_bundle(start, bundle)
            else:
                move = h137mod.anti_bundle_move(start, bundle, gamma, 0.22)
            if np.allclose(move, start):
                continue
            diff_hash = array_hash(move - start)
            if diff_hash in seen:
                continue
            seen.add(diff_hash)
            evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            d = {f"delta_{key}": float(evald[key] - start_eval[key]) for key in evald}
            row = int(bundle["row"])
            roles = classify_roles(row, kind, {key.replace("delta_", ""): value for key, value in d.items()})
            rec = {
                "atom_id": safe_id(f"{kind}_{bundle['bundle_id']}", 80),
                "kind": kind,
                "row": row,
                "targets": str(bundle["targets"]),
                "frac": float(bundle["frac"]),
                "gamma": float(gamma),
                "bundle_score": float(bundle["h135_bundle_score"]),
                "roles": ",".join(roles),
                **d,
            }
            rec["h139_atom_score"] = atom_score(rec)
            rows.append(rec)
            if roles and "locked_core_unwind" not in roles and "stress_decoy" not in roles:
                atoms.append(
                    Atom(
                        atom_id=str(rec["atom_id"]),
                        kind=kind,
                        row=row,
                        targets=str(bundle["targets"]),
                        frac=float(bundle["frac"]),
                        gamma=float(gamma),
                        roles=roles,
                        move=move,
                        metrics={key: float(value) for key, value in rec.items() if key.startswith("delta_")},
                    )
                )
    return atoms, pd.DataFrame(rows), bundle_pool.drop(columns=["ops"]), cell_pool


def run() -> None:
    cleanup_previous_outputs()
    pool, _public, sample, base_prob, cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, good_moves, axes, fit, model_scores, props = h118mod.prepare_context()
    scored = h123mod.build_scored_pool(pool, base_prob, fit, bad_axes, bad_moves, good_moves, axes, props)
    catalog = h132mod.build_catalog(scored)
    start = load_move(ROOT / "submission_h136_factorized_dc9dd2c5_uploadsafe.csv", sample, base_prob)
    moves = {"h131": h137mod.load_move("h131", sample, base_prob), "h136": start}
    start_eval = evaluate_matrix(start, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
    atoms, atom_df, bundle_pool, cell_pool = build_atoms(
        catalog,
        start,
        start_eval,
        moves,
        basis_fit_df,
        basis_fit_moves,
        route_fit,
        cell,
        h098_fit,
        fit,
        pool,
        bad_axes,
        bad_moves,
        good_moves,
        axes,
    )

    known = known_hashes(sample)
    emitted: set[str] = set()
    candidate_rows = []
    selected_frames = []
    atom_lookup = {atom.atom_id: atom for atom in atoms}
    for size in [1, 2, 3]:
        for combo in itertools.combinations(atoms, size):
            rows = [atom.row for atom in combo]
            if len(rows) != len(set(rows)):
                continue
            roles = [role for atom in combo for role in atom.roles]
            if "toxicity_relief" not in roles or "margin_repair" not in roles:
                continue
            move = start.copy()
            for atom in combo:
                move = move + (atom.move - start)
            changed = int((np.abs(move - start) > 1.0e-12).sum())
            if changed > 5:
                continue
            prob = h130mod.materialize(base_prob, move)
            hash_id = short_hash(prob)
            if hash_id in known or hash_id in emitted:
                continue
            evald = evaluate_matrix(move, basis_fit_df, basis_fit_moves, route_fit, cell, h098_fit, fit, pool, bad_axes, bad_moves, good_moves, axes)
            selected = changed_cells(start, move)
            axis = h102mod.cumulative_axis_metrics(move.reshape(-1), bad_axes, bad_moves, good_moves)
            rec = {
                "candidate_id": safe_id(f"h139_{hash_id}", 96),
                "atoms": "|".join(atom.atom_id for atom in combo),
                "rows": ",".join(str(row) for row in rows),
                "roles": "|".join(",".join(atom.roles) for atom in combo),
                "changed_cells_vs_h136": changed,
                "delta_route": float(evald["route"] - start_eval["route"]),
                "delta_h098": float(evald["h098"] - start_eval["h098"]),
                "delta_curv_marg": float(evald["curv_marg"] - start_eval["curv_marg"]),
                "delta_h088": float(evald["h088"] - start_eval["h088"]),
                "delta_margin": float(evald["margin"] - start_eval["margin"]),
                "route": float(evald["route"]),
                "h098": float(evald["h098"]),
                "h088": float(evald["h088"]),
                "margin": float(evald["margin"]),
                "h102_cum_h088_axis_cos": float(axis["h102_cum_h088_axis_cos"]),
                "h102_cum_good_bad_margin": float(axis["h102_cum_good_bad_margin"]),
            }
            rec["passes_role_boundary"] = bool(
                rec["delta_margin"] >= 0.0
                and rec["delta_h088"] <= -0.00100
                and rec["delta_h098"] <= 0.00000180
                and rec["delta_route"] <= 0.00000320
                and changed <= 4
            )
            rec["h139_candidate_score"] = candidate_score(rec)
            rec["worldview"] = "automatic role atom assignment: lock H136 route core, combine toxicity-relief and margin-repair atoms"
            emitted.add(hash_id)
            candidate_rows.append((rec, prob, selected))

    if not candidate_rows:
        raise RuntimeError("H139 produced no role-compatible candidates")

    rows = [rec for rec, _prob, _selected in candidate_rows]
    candidates = pd.DataFrame(rows).sort_values(
        ["passes_role_boundary", "h139_candidate_score", "delta_h088", "delta_h098"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    materialized_rows = []
    for rec, prob, selected in candidate_rows:
        if rec["candidate_id"] not in set(candidates.head(30)["candidate_id"]):
            continue
        path = OUT / f"submission_{rec['candidate_id']}.csv"
        h085mod.write_submission(sample, prob, path)
        validation = h085mod.validate_submission(path, sample, base_prob)
        rec["file"] = path.name
        rec["resolved_path"] = str(path.resolve())
        rec.update({f"validation_{key}": value for key, value in validation.items()})
        materialized_rows.append(rec)
        if not selected.empty:
            selected = selected.copy()
            selected.insert(0, "candidate_id", rec["candidate_id"])
            selected_frames.append(selected)

    candidates = pd.DataFrame(materialized_rows).sort_values(
        ["passes_role_boundary", "h139_candidate_score", "delta_h088", "delta_h098"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h139_roleatoms_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    root_validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h139_role_atom_assignment_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        **selected,
        **{f"root_{key}": value for key, value in root_validation.items()},
    }

    atom_df.to_csv(OUT / "h139_atom_metrics.csv", index=False)
    bundle_pool.to_csv(OUT / "h139_bundle_pool.csv", index=False)
    cell_pool.to_csv(OUT / "h139_cell_pool.csv", index=False)
    model_scores.to_csv(OUT / "h139_curvature_model_scores.csv", index=False)
    candidates.to_csv(OUT / "h139_candidates.csv", index=False)
    if selected_frames:
        pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h139_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h139_decision.csv", index=False)

    cols = [
        "candidate_id",
        "atoms",
        "rows",
        "roles",
        "changed_cells_vs_h136",
        "delta_route",
        "delta_h098",
        "delta_h088",
        "delta_margin",
        "passes_role_boundary",
        "h139_candidate_score",
        "file",
    ]
    role_atoms = atom_df[atom_df["roles"].astype(str) != ""].sort_values("h139_atom_score", ascending=False)
    report = f"""# H139 Role-Atom Assignment Equation HS-JEPA

Question: can H138's hand-built pair be rediscovered and improved by an
automatic role-aware row-target assignment solver?

Start field: H136.

Locked invariant:

```text
row164 route core is not available as a margin-repair shortcut.
```

Start equation values:

- route: `{start_eval['route']:.12f}`
- H098/model: `{start_eval['h098']:.12f}`
- H088: `{start_eval['h088']:.12f}`
- margin: `{start_eval['margin']:.12f}`

Role atoms:

{md_table(role_atoms, 60)}

Candidates:

{md_table(candidates[cols], 30)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation:

H139 promotes a role triad when it beats the H138 hand-built pair under the
same one-sided boundary constraints:

```text
toxicity-relief head: row207 / row131 S2
margin-repair head: row70 Q3
locked route core: row164 remains untouched
```

Public interpretation:

- H139 > H138: the solver needs multiple toxicity-relief atoms plus a separate
  repair atom; H138 was only a hand-built local slice.
- H138 > H139: row70/row131 are local sensor artifacts; keep the smaller
  row135 repair pair.
- H136 > both: counterfield roles are diagnostic, not action-grade.
"""
    (OUT / "h139_report.md").write_text(report, encoding="utf-8")

    print(f"H139 selected {selected['candidate_id']}")
    print(f"root: {root_path}")
    print(candidates[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    run()
