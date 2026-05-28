from __future__ import annotations

import public_lb_direct_label_inverse7 as inv
from public_lb_direct_label_inverse8_config import apply_inverse8, apply_loocv8


apply_inverse8(inv)

import public_lb_direct_label_inverse7_loocv as loo  # noqa: E402


def main() -> None:
    apply_inverse8(loo.inv)
    apply_loocv8(loo)
    loo.main()


if __name__ == "__main__":
    main()
