from __future__ import annotations

import argparse

from compgeom import build_kdtree, display_kdtree
from compgeom.cli._shared import demo_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a 2D KD-tree from demo points.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in point cloud.")
    args = parser.parse_args(argv)
    points = demo_points()
    root = build_kdtree(points)
    print(f"2D KD-Tree built with {len(points)} points.\n")
    display_kdtree(root)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
