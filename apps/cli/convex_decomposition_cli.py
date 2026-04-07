from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom.polygon import convex_decompose_polygon
from compgeom import OBJFileHandler, save_png, save_svg
from _shared import read_input_lines, parse_points


def read_polygon(args) -> list[Point2D] | None:
    if args.input:
        print(f"Reading polygon from {args.input}...")
        try:
            mesh = OBJFileHandler.read(args.input)
            return [Point2D(v.x, v.y) for v in mesh.vertices]
        except Exception:
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


def pieces_to_svg(poly_pieces: list[list[Point2D]], width=800, height=600) -> str:
    all_pts = []
    for piece in poly_pieces:
        for p in piece:
            all_pts.extend([p.x, p.y])

    min_x, max_x = min(all_pts[0::2]), max(all_pts[0::2])
    min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])

    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    ]
    svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')

    def tx(x):
        return (
            50 + (x - min_x) / (max_x - min_x) * (width - 100) if max_x > min_x else 50
        )

    def ty(y):
        return (
            height - (50 + (y - min_y) / (max_y - min_y) * (height - 100))
            if max_y > min_y
            else 50
        )

    colors = [
        "#e74c3c",
        "#3498db",
        "#2ecc71",
        "#f1c40f",
        "#9b59b6",
        "#1abc9c",
        "#e67e22",
    ]

    for i, piece in enumerate(poly_pieces):
        pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in piece)
        color = colors[i % len(colors)]
        svg.append(
            f'<polygon points="{pts_str}" fill="{color}" fill-opacity="0.5" stroke="black" stroke-width="1" />'
        )

        cx = sum(p.x for p in piece) / len(piece)
        cy = sum(p.y for p in piece) / len(piece)
        svg.append(
            f'<text x="{tx(cx)}" y="{ty(cy)}" font-size="12" text-anchor="middle" fill="black">{i + 1}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Decompose a polygon into convex pieces using Hertel-Mehlhorn."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--obj", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument(
        "--output", default="convex_decomposition.png", help="Output visualization file"
    )

    args = parser.parse_args(argv)

    polygon = read_polygon(args)
    if not polygon:
        print(
            "Error: No input polygon provided. Use --input, --poly, or pipe vertices to stdin."
        )
        return 1

    print(f"Initial Polygon: {len(polygon)} vertices.")

    mesh = convex_decompose_polygon(polygon)
    pieces = [[mesh.vertices[index] for index in face] for face in mesh.faces]

    print(f"\nDecomposed into {len(pieces)} convex pieces.")
    for i, piece in enumerate(pieces):
        print(f"  Piece {i + 1}: {len(piece)} vertices")

    svg_content = pieces_to_svg(pieces)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"\nSaved visualization to {args.output}")
        except Exception:
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg_content, out_svg)
            print(f"\nSaved visualization to {out_svg}")
    else:
        save_svg(svg_content, args.output)
        print(f"\nSaved visualization to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
