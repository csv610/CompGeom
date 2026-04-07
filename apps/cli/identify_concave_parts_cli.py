from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom import get_reflex_vertices, OBJFileHandler
from compgeom import save_png, save_svg
from _shared import read_input_lines, parse_points


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
            return [Point2D(raw[i], raw[i + 1], i // 2) for i in range(0, len(raw), 2)]
        except (ValueError, IndexError):
            return None
            
    lines = read_input_lines(args.input)
    if lines:
        return parse_points(lines)

    return None


def poly_to_svg(poly: list[Point2D], concave_pts: list[Point2D], width=800, height=600) -> str:
    all_pts = []
    for p in poly:
        all_pts.extend([p.x, p.y])
    min_x, max_x = min(all_pts[0::2]), max(all_pts[0::2])
    min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])

    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    ]
    svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')

    def tx(x):
        return (
            50 + (x - min_x) / (max_x - min_x) * (width - 100)
            if max_x > min_x
            else 50
        )

    def ty(y):
        return (
            height - (50 + (y - min_y) / (max_y - min_y) * (height - 100))
            if max_y > min_y
            else 50
        )

    pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in poly)
    svg.append(
        f'<polygon points="{pts_str}" fill="white" stroke="black" stroke-width="2" />'
    )

    for p in poly:
        svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="3" fill="#ccc" />')

    for p in concave_pts:
        svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="6" fill="red" />')
        svg.append(
            f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="8" fill="none" stroke="red" stroke-width="1" />'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Identify vertices forming concave parts of a polygon provided via stdin or file."
    )
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument(
        "--output", default="concave_parts.png", help="Output visualization file"
    )

    args = parser.parse_args(argv)

    polygon = read_polygon(args)
    if not polygon:
        print("Error: No input polygon provided. Use --input, --poly, or pipe vertices to stdin.")
        return 1

    print(f"Initial Polygon: {len(polygon)} vertices.")

    reflex_vertices = get_reflex_vertices(polygon)

    print(f"\nFound {len(reflex_vertices)} reflex (concave) vertices.")
    for i, v in enumerate(reflex_vertices):
        print(f"  {i + 1}: {v}")

    svg_content = poly_to_svg(polygon, reflex_vertices)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception as e:
            print(f"Warning: PNG generation failed ({e}). Saving as SVG.")
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg_content, out_svg)
    else:
        save_svg(svg_content, args.output)
        print(f"Saved visualization to {args.output}")
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
