import argparse
import random

from compgeom import Point2D
from compgeom import DynamicDelaunay

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a dynamic Delaunay triangulation.")
    parser.add_argument("--count", type=int, default=10, help="Number of random points to insert.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducible point generation.")
    args = parser.parse_args(argv)

    random.seed(args.seed)
    dt = DynamicDelaunay()
    points = [Point2D(random.randint(0, 100), random.randint(0, 100), i) for i in range(args.count)]
    print("Adding points incrementally...")
    for p in points:
        dt.add_point(p)
    tris = dt.get_triangles()
    print(f"Final Triangulation: {len(tris)} triangles.")
    for triangle in tris:
        print(f"Triangle: {sorted([vertex.id for vertex in triangle])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
