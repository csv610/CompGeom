from __future__ import annotations

import argparse
from compgeom import (
    Point2D,
    resample_polygon,
    mean_curvature_flow_polygon,
    OBJFileHandler,
    save_png,
    save_svg,
)
from _shared import read_input_lines, parse_points


def read_polygon(args) -> list[Point2D] | None:
    if args.input:
        print(f"Reading polygon from {args.input}...")
        try:
            mesh = OBJFileHandler.read(args.input)
            return [Point2D(v.x, v.y) for v in mesh.vertices]
        except Exception as e:
            # If OBJ fails, try reading as raw points
            pass

    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            return [Point2D(raw[i], raw[i + 1], i // 2) for i in range(0, len(raw), 2)]
        except (ValueError, IndexError):
            return None

    lines = read_input_lines(args.input)
    if lines:
        return parse_points(lines)

    return None


def poly_to_svg(
    polygon: list[Point2D], smoothed: list[Point2D], width=800, height=600
) -> str:
    all_pts = []
    for p in smoothed:
        all_pts.extend([p.x, p.y])
    if polygon:
        for p in polygon:
            all_pts.extend([p.x, p.y])

    max_coord = max(max(abs(x) for x in all_pts), 1.0) * 1.2

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="{-max_coord} {-max_coord} {2 * max_coord} {2 * max_coord}" xmlns="http://www.w3.org/2000/svg">'
    ]
    svg.append('<rect x="-100%" y="-100%" width="200%" height="200%" fill="white" />')
    svg.append(
        f'<line x1="{-max_coord}" y1="0" x2="{max_coord}" y2="0" stroke="#eee" stroke-width="0.5" />'
    )
    svg.append(
        f'<line x1="0" y1="{-max_coord}" x2="0" y2="{max_coord}" stroke="#eee" stroke-width="0.5" />'
    )

    cx = sum(p.x for p in polygon) / len(polygon)
    cy = sum(p.y for p in polygon) / len(polygon)
    centered_orig = [Point2D(p.x - cx, p.y - cy) for p in polygon]

    def to_pts(pts):
        return " ".join(f"{p.x},{-p.y}" for p in pts)

    svg.append(
        f'<polygon points="{to_pts(centered_orig)}" fill="none" stroke="#ddd" stroke-dasharray="2,2" />'
    )
    svg.append(
        f'<polygon points="{to_pts(smoothed)}" fill="none" stroke="red" stroke-width="2" />'
    )
    svg.append('<circle cx="0" cy="0" r="2" fill="blue" />')
    svg.append("</svg>")
    return "\n".join(svg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Smooth a polygon using Mean Curvature Flow."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--obj", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument(
        "--n_points",
        type=int,
        default=50,
        help="Number of points for uniform resampling",
    )
    parser.add_argument(
        "--iterations", type=int, default=100, help="Number of smoothing iterations"
    )
    parser.add_argument("--dt", type=float, default=0.1, help="Time step for the flow")
    parser.add_argument(
        "--no_center",
        action="store_false",
        dest="fix_centroid",
        help="Do not fix centroid at (0,0)",
    )
    parser.add_argument(
        "--output", default="smoothed_polygon.png", help="Output visualization file"
    )

    args = parser.parse_args(argv)
    fix_centroid = getattr(args, "fix_centroid", True)

    polygon = read_polygon(args)
    if not polygon:
        print(
            "Error: No input polygon provided. Use --input, --poly, or pipe vertices to stdin."
        )
        return 1

    print(f"Initial Polygon: {len(polygon)} vertices.")

    print(f"Resampling to {args.n_points} uniform segments...")
    resampled = resample_polygon(polygon, args.n_points)

    print(f"Applying MCF for {args.iterations} iterations (dt={args.dt})...")
    if fix_centroid:
        print("Constraint: Centroid is fixed at (0,0).")

    smoothed = mean_curvature_flow_polygon(
        resampled,
        args.iterations,
        args.dt,
        keep_perimeter=True,
        fix_centroid=fix_centroid,
    )

    print("Done.")

    svg_content = poly_to_svg(polygon, smoothed)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception:
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg_content, out_svg)
    else:
        save_svg(svg_content, args.output)
        print(f"Saved visualization to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
