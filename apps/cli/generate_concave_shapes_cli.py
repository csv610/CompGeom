from __future__ import annotations

import argparse
from compgeom.kernel import Point2D
from compgeom.polygon import (
    generate_convex_polygon,
    generate_concave_polygon,
    generate_star_shaped_polygon,
)
from compgeom.graphics.visualization import save_png, save_svg


def poly_to_svg(p_list: list[Point2D], width=800, height=600) -> str:
    all_pts = []
    for p in p_list:
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

    pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in p_list)
    svg.append(
        f'<polygon points="{pts_str}" fill="white" stroke="black" stroke-width="2" />'
    )
    for p in p_list:
        svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="3" fill="red" />')

    svg.append("</svg>")
    return "\n".join(svg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate random polygons.")
    parser.add_argument(
        "type",
        choices=["convex", "concave", "star"],
        help="Type of polygon to generate",
    )
    parser.add_argument("--n", type=int, default=15, help="Number of vertices")
    parser.add_argument(
        "--output", default="generated_polygon.png", help="Output visualization file"
    )
    parser.add_argument(
        "--print", action="store_true", help="Print polygon vertices to stdout"
    )

    args = parser.parse_args(argv)

    if not args.print:
        print(f"Generating random {args.type} polygon with {args.n} vertices...")

    if args.type == "convex":
        poly = generate_convex_polygon(args.n)
    elif args.type == "concave":
        poly = generate_concave_polygon(args.n)
    else:
        poly = generate_star_shaped_polygon(args.n)

    if args.print:
        for p in poly:
            print(f"{p.x} {p.y}")
        return 0

    print(f"Result: Polygon with {len(poly)} vertices.")

    svg_content = poly_to_svg(poly)

    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception:
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg_content, out_svg)
            print(f"Warning: PNG generation failed. Saved visualization to {out_svg}")
    else:
        save_svg(svg_content, args.output)
        print(f"Saved visualization to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
