from __future__ import annotations

import argparse

from compgeom import closest_pair
from compgeom.cli._shared import demo_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find the closest pair in a demo point set.")
    parser.parse_args(argv)
    points = demo_points()
    dist, (p1, p2) = closest_pair(points)
    print(f"Closest Pair: {p1} and {p2}\nDistance:     {dist:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
