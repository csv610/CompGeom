from __future__ import annotations

import argparse
from compgeom.kernel import Point2D
from compgeom.algo.points_sampling import PointSampler
from compgeom.mesh.meshio import MeshExporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate random points inside a circle."
    )
    parser.add_argument("-n", "--count", type=int, default=100, help="Number of points")
    parser.add_argument("-r", "--radius", type=float, default=1.0, help="Circle radius")
    parser.add_argument(
        "-c", "--center", nargs=2, type=float, default=[0.0, 0.0], help="Center as x y"
    )
    parser.add_argument(
        "-o", "--output", default="circle_points.off", help="Output OFF file"
    )
    args = parser.parse_args(argv)

    center = Point2D(args.center[0], args.center[1])
    points = PointSampler.in_circle(args.count, args.radius, center)

    MeshExporter.write(args.output, points, edges=[])
    print(f"Generated {len(points)} points to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
