from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.polygon.straight_skeleton import StraightSkeleton
from compgeom.kernel.polygon import Polygon2D
from compgeom.kernel.point import Point2D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the straight skeleton of a 2D polygon."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input polygon file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output mesh file representing the skeleton."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
        vertices = [Point2D(v.x, v.y) for v in mesh.vertices]
        polygon = Polygon2D(tuple(vertices))
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Computing straight skeleton for polygon with {len(vertices)} vertices...")
    
    try:
        skel = StraightSkeleton(polygon)
        skel.compute()
    except Exception as e:
        print(f"Error computing straight skeleton: {e}")
        return 1

    try:
        # Save skeleton as a mesh with edges
        MeshExporter.write(args.output, skel.skeleton_points, edges=skel.skeleton_edges)
        print(f"Straight skeleton written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
