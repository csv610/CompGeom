from __future__ import annotations

import argparse
from compgeom import Point2D, find_largest_empty_circle, visualize_largest_empty_circle, save_png, save_svg
from _shared import read_input_lines, parse_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find the largest empty circle within the convex hull of points.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--points", nargs="+", help="Point coordinates as x1 y1 x2 y2 ...")
    parser.add_argument("--output", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args(argv)
    
    points = []
    if args.points:
        try:
            raw = [float(x) for x in args.points]
            if len(raw) % 2 != 0:
                print("Error: Points need pairs of coordinates (x1 y1).")
                return 1
            for i in range(0, len(raw), 2):
                points.append(Point2D(raw[i], raw[i+1], i//2))
        except ValueError:
            print("Error: Coordinates must be numeric.")
            return 1
    else:
        lines = read_input_lines(args.input)
        if lines:
            points = parse_points(lines)
            
    if not points:
        print("Error: No input points provided. Use --points or pipe vertices to stdin.")
        return 1
        
    if len(points) < 3:
        print("Error: Need at least 3 points to define a convex hull.")
        return 1
        
    print(f"Finding Largest Empty Circle for {len(points)} points...")
    
    center, radius = find_largest_empty_circle(points)
    
    print(f"\nResults:")
    print(f"  Center: ({center.x:.6f}, {center.y:.6f})")
    print(f"  Radius: {radius:.6f}")
    
    if args.output:
        svg = visualize_largest_empty_circle(points, center, radius)
        if args.output.lower().endswith(".png"):
            try:
                save_png(svg, args.output)
                print(f"\nSaved visualization to {args.output}")
            except Exception as e:
                print(f"\nWarning: Could not save PNG ({e}). Saving as SVG.")
                out_svg = args.output.rsplit('.', 1)[0] + ".svg"
                save_svg(svg, out_svg)
        else:
            save_svg(svg, args.output)
            print(f"\nSaved visualization to {args.output}")
            
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
