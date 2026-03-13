import argparse

from compgeom import generate_random_convex_polygon

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a random convex polygon.")
    parser.add_argument(
        "--samples",
        type=int,
        default=20,
        help="Number of random samples used to generate the polygon.",
    )
    args = parser.parse_args(argv)

    hull = generate_random_convex_polygon(args.samples)
    print(f"Generated Random Convex Polygon with {len(hull)} vertices:")
    for point in hull:
        print(f"{point.x:.4f} {point.y:.4f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
