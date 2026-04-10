from __future__ import annotations

import argparse
from compgeom import (
    Point2D,
    pack_circles,
    calculate_circle_packing_efficiency,
    visualize_circle_packing,
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
            if len(raw) % 2 != 0:
                print("Error: Polygon needs pairs of coordinates (x1 y1).")
                return None
            return [Point2D(raw[i], raw[i + 1]) for i in range(0, len(raw), 2)]
        except ValueError:
            print("Error: Coordinates must be numeric.")
            return None

    lines = read_input_lines(args.input)
    if lines:
        return parse_points(lines)

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pack circles into a closed polygon.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("-f", "--obj", help="Path to input OBJ file defining the polygon")
    parser.add_argument("-p", "--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument(
        "-r", "--radius", type=float, default=0.5, help="Radius of circles to pack"
    )
    parser.add_argument(
        "--output",
        default="circle_packing.png",
        help="Output visualization file (.svg or .png)",
    )

    args = parser.parse_args(argv)

    polygon = read_polygon(args)
    if not polygon:
        print(
            "Error: No polygon provided. Use --input, --poly, or pipe vertices to stdin."
        )
        return 1

    print(
        f"Packing circles of radius {args.radius} into polygon with {len(polygon)} vertices..."
    )

    centers = pack_circles(polygon, args.radius)
    efficiency = calculate_circle_packing_efficiency(polygon, centers, args.radius)

    print(f"\nResults:")
    print(f"  Circles Packed:     {len(centers)}")
    print(f"  Packing Efficiency: {efficiency:.2f}%")

    print("\nCircle Centers (First 10):")
    for i, c in enumerate(centers[:10]):
        print(f"  {i + 1:2}: ({c.x:.4f}, {c.y:.4f})")
    if len(centers) > 10:
        print(f"  ... and {len(centers) - 10} more.")

    svg = visualize_circle_packing(polygon, centers, args.radius)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg, args.output)
            print(f"\nSaved visualization to {args.output}")
        except Exception as e:
            print(f"\nWarning: Could not save PNG ({e}). Saving as SVG.")
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg, out_svg)
    else:
        save_svg(svg, args.output)
        print(f"\nSaved visualization to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
