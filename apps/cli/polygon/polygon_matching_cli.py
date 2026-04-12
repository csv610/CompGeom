from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.polygon.polygon_matching import reorder_to_match
from compgeom.polygon.polygon import Polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reorder vertices of one polygon to match another based on shape similarity."
    )
    parser.add_argument(
        "-1", "--poly1", required=True, help="Path to first polygon file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-2", "--poly2", required=True, help="Path to second polygon file."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output reordered polygon file."
    )
    parser.add_argument(
        "--no-reflection", action="store_false", dest="allow_reflection",
        help="Do not allow reflecting the polygon to find a match."
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

    print(f"Reordering {args.poly2} to match {args.poly1}...")
    
    try:
        reordered_vertices = reorder_to_match(poly1, poly2, allow_reflection=args.allow_reflection)
        reordered_poly = Polygon(reordered_vertices)
    except Exception as e:
        print(f"Error during matching: {e}")
        return 1

    try:
        MeshExporter.write(args.output, reordered_poly)
        print(f"Reordered polygon written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
