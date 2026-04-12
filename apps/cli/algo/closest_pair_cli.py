from __future__ import annotations

import argparse

from compgeom.algo.proximity import closest_pair
from compgeom.mesh.meshio import MeshImporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find the closest pair in a point set."
    )
    parser.add_argument("input", help="Path to input mesh file")
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    if not mesh.vertices:
        print("Error: No points in mesh.")
        return 1

    (p1, p2), dist = closest_pair(mesh)
    print(f"Closest Pair: {p1} and {p2}\n Distance:     {dist:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
