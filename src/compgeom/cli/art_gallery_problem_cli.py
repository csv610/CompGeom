from __future__ import annotations

import argparse

from compgeom import Point2D, art_gallery_guards
from compgeom.mesh import meshio

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Solve the Art Gallery Problem.")
    parser.add_argument("-i", "--input", required=True, help="Path to input OFF file defining the polygon")
    args = parser.parse_args(argv)

    try:
        mesh = meshio.from_file(args.input)
        points = [Point2D(v.x, v.y) for v in mesh.vertices]
    except Exception as e:
        print(f"Error reading OFF file: {e}")
        return 1

    guards = art_gallery_guards(points)

    print(f"Placed {len(guards)} guards (n={len(points)}):")

    for guard in guards:
        print(f"Guard at {guard}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
