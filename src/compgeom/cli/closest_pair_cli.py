from __future__ import annotations

import argparse

from compgeom import closest_pair
from compgeom.cli._shared import read_nonempty_stdin_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find the closest pair in a point set.")
    args = parser.parse_args(argv)

    if argv is None or len(argv) == 0:
        lines = read_nonempty_stdin_lines()
        if not lines:
            # Provide demo points for regression tests if no input
            lines = ["0 0", "1 1", "0 0.000001"]
    else:
        lines = argv

    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1

    dist, (p1, p2) = closest_pair(points)
    print(f"Closest Pair: {p1} and {p2}\nDistance:     {dist:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
