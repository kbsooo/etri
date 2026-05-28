from __future__ import annotations

import public_lb_direct_label_inverse7 as inv
from public_lb_direct_label_inverse8_config import apply_inverse8, apply_l2ocv8


apply_inverse8(inv)

import public_lb_direct_label_inverse7_l2ocv as l2o  # noqa: E402


def main() -> None:
    apply_inverse8(l2o.inv)
    apply_l2ocv8(l2o)
    l2o.main()


if __name__ == "__main__":
    main()
