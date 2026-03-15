import argparse

from compgeom import generate_random_convex_polygon
from compgeom.cli._shared import visualize_with_pyvista

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a random convex polygon.")
    parser.add_argument(
        "-n", "--num_poly",
        type=int,
        default=20,
        help="Number of random samples used to generate the polygon.",
    )
    parser.add_argument("--visualize", action="store_true", help="Visualize the generated polygon using pyvista.")
    args = parser.parse_args(argv)

    hull = generate_random_convex_polygon(args.num_poly)

    print(f"Generated Random Convex Polygon with {len(hull)} vertices:")
    for point in hull:
        print(f"{point.x:.4f} {point.y:.4f}")
        
    if args.visualize:
        visualize_with_pyvista(polygons=[hull])
        
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
