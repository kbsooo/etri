from __future__ import annotations

import public_lb_direct_label_inverse7 as inv
from public_lb_direct_label_inverse8_config import apply_inverse8, apply_robust8


apply_inverse8(inv)

import public_lb_direct_label_robust_selector as robust  # noqa: E402


def main() -> None:
    apply_inverse8(robust.inv)
    apply_robust8(robust)
    robust.main()


if __name__ == "__main__":
    main()
