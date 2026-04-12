from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.polygon.polygon_simplification import resolve_self_intersections
from compgeom.polygon.polygon import Polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve self-intersections in a 2D polygon."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input polygon file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output polygon file."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
        # Assuming input is 2D or we project to XY
        vertices = list(mesh.vertices)
        poly = Polygon(vertices)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Resolving self-intersections for polygon with {len(vertices)} vertices...")
    
    try:
        resolved_vertices = resolve_self_intersections(poly)
        resolved_poly = Polygon(resolved_vertices)
    except Exception as e:
        print(f"Error resolving self-intersections: {e}")
        return 1

    try:
        MeshExporter.write(args.output, resolved_poly)
        print(f"Resolved polygon written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
