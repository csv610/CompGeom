from __future__ import annotations

from compgeom import farthest_pair
from compgeom.cli._shared import demo_points


def main() -> int:
    points = demo_points()
    dist, (p1, p2) = farthest_pair(points)
    print(f"Farthest Pair (Diameter): {p1} and {p2}\nMaximum Distance:         {dist:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
