from __future__ import annotations

import argparse

from compgeom import solve_art_gallery
from compgeom.cli._shared import demo_polygon, parse_points


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve the Art Gallery Problem.")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    args = parser.parse_args()

    if args.poly:
        try:
            raw = [float(value) for value in args.poly]
            if len(raw) % 2 != 0:
                print("Error: Polygon needs pairs of coordinates (x1 y1).")
                return 1
            points = parse_points(
                [f"{raw[index]} {raw[index + 1]}" for index in range(0, len(raw), 2)]
            )
        except ValueError:
            print("Error: Coordinates must be numeric.")
            return 1
    else:
        points = demo_polygon()

    guards = solve_art_gallery(points)
    print(f"Placed {len(guards)} guards (n={len(points)}):")
    for guard in guards:
        print(f"Guard at {guard}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
