#!/usr/bin/env python3
"""Team-facing entry point for the HS-JEPA cross-subject prototype transport experiment."""

from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "hsjepa_core" / "run_cross_subject_prototype_transport_core.py"


if __name__ == "__main__":
    runpy.run_path(str(IMPLEMENTATION), run_name="__main__")
