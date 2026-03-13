from __future__ import annotations

import argparse

from compgeom import farthest_pair
from compgeom.cli._shared import demo_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find the farthest pair in a demo point set.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in point set.")
    args = parser.parse_args(argv)
    points = demo_points()
    dist, (p1, p2) = farthest_pair(points)
    print(f"Farthest Pair (Diameter): {p1} and {p2}\nMaximum Distance:         {dist:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
