from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter
from compgeom.polygon.polygon_similarity import polygons_are_similar
from compgeom.polygon.polygon import Polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check if two polygons are geometrically similar."
    )
    parser.add_argument(
        "-1", "--poly1", required=True, help="Path to first polygon file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-2", "--poly2", required=True, help="Path to second polygon file."
    )
    parser.add_argument(
        "-t", "--tolerance", type=float, default=1e-7, help="Tolerance for similarity check."
    )

    args = parser.parse_args(argv)

    try:
        mesh1 = MeshImporter.read(args.poly1)
        poly1 = Polygon(list(mesh1.vertices))
        
        mesh2 = MeshImporter.read(args.poly2)
        poly2 = Polygon(list(mesh2.vertices))
    except Exception as e:
        print(f"Error reading input files: {e}")
        return 1

    print(f"Checking similarity between {args.poly1} and {args.poly2}...")
    
    try:
        similar = polygons_are_similar(poly1, poly2, tolerance=args.tolerance)
        if similar:
            print("The polygons are SIMILAR.")
        else:
            print("The polygons are NOT similar.")
    except Exception as e:
        print(f"Error during similarity check: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
