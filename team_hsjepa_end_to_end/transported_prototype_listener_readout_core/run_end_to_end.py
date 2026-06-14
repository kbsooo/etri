#!/usr/bin/env python3
"""Team-facing entry point for the HS-JEPA transported-prototype listener readout experiment."""

from __future__ import annotations

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / "hsjepa_core" / "run_transported_prototype_listener_readout_core.py"


if __name__ == "__main__":
    runpy.run_path(str(IMPLEMENTATION), run_name="__main__")
