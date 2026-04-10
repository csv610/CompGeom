from __future__ import annotations

import argparse
from compgeom import (
    Point2D,
    solve_distance_map,
    visualize_distance_map_svg,
    OBJFileHandler,
    save_png,
    save_svg,
)
from ._shared import read_input_lines, parse_points


def read_polygon(args) -> list[Point2D] | None:
    if args.obj:
        print(f"Reading polygon from {args.obj}...")
        try:
            mesh = OBJFileHandler.read(args.obj)
            return [Point2D(v.x, v.y) for v in mesh.vertices]
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            return [Point2D(raw[i], raw[i + 1]) for i in range(0, len(raw), 2)]
        except Exception as e:
            print(f"Error parsing coordinates: {e}")
            return None

    lines = read_input_lines(args.input)
    if lines:
        return parse_points(lines)

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculate distance map from polygon boundaries."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--obj", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--res", type=int, default=100, help="Grid resolution")
    parser.add_argument(
        "--output", default="distance_map.png", help="Output visualization file"
    )

    args = parser.parse_args(argv)

    polygon = read_polygon(args)
    if not polygon:
        print(
            "Error: No polygon provided. Use --input, --poly, or pipe vertices to stdin."
        )
        return 1

    print(f"Solving Eikonal equation for polygon with {len(polygon)} vertices...")
    grid, extent = solve_distance_map(polygon, resolution=args.res)

    print(f"Grid size: {len(grid)} x {len(grid[0])}")

    svg = visualize_distance_map_svg(grid, extent)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg, args.output)
            print(f"Saved distance map to {args.output}")
        except Exception as e:
            print(f"Warning: Could not save PNG ({e}). Saving as SVG.")
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg, out_svg)
    else:
        save_svg(svg, args.output)
        print(f"Saved distance map to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
