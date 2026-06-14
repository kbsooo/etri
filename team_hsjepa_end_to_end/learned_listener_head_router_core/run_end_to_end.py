#!/usr/bin/env python3
"""Team-facing end-to-end runner for the learned listener-head router core."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_learned_listener_head_router_core import run  # noqa: E402
from hsjepa_core.run_learned_listener_responsibility_pretext_core import json_safe  # noqa: E402


if __name__ == "__main__":
    print(json.dumps(json_safe(run()), ensure_ascii=False, indent=2))
