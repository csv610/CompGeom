from __future__ import annotations

from compgeom import build_kdtree, display_kdtree
from compgeom.cli._shared import demo_points


def main() -> int:
    points = demo_points()
    root = build_kdtree(points)
    print(f"2D KD-Tree built with {len(points)} points.\n")
    display_kdtree(root)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
