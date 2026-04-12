from __future__ import annotations

import argparse
import math
import random

from compgeom.kernel import Point2D
from compgeom.polygon import Polygon


def generate_square(size: float = 100.0, center: Point2D = Point2D(50, 50)) -> Polygon:
    half = size / 2
    points = [
        Point2D(center.x - half, center.y - half, 0),
        Point2D(center.x + half, center.y - half, 1),
        Point2D(center.x + half, center.y + half, 2),
        Point2D(center.x - half, center.y + half, 3),
    ]
    return Polygon(points)


def generate_rectangle(
    width: float = 100.0, height: float = 60.0, center: Point2D = Point2D(50, 50)
) -> Polygon:
    half_w, half_h = width / 2, height / 2
    points = [
        Point2D(center.x - half_w, center.y - half_h, 0),
        Point2D(center.x + half_w, center.y - half_h, 1),
        Point2D(center.x + half_w, center.y + half_h, 2),
        Point2D(center.x - half_w, center.y + half_h, 3),
    ]
    return Polygon(points)


def generate_equilateral_triangle(
    size: float = 100.0, center: Point2D = Point2D(50, 50)
) -> Polygon:
    h = size * math.sqrt(3) / 2
    points = [
        Point2D(center.x, center.y + 2 * h / 3, 0),
        Point2D(center.x - size / 2, center.y - h / 3, 1),
        Point2D(center.x + size / 2, center.y - h / 3, 2),
    ]
    return Polygon(points)


def generate_regular_polygon(
    n_sides: int = 6,
    radius: float = 40.0,
    center: Point2D = Point2D(50, 50),
) -> Polygon:
    points = []
    for i in range(n_sides):
        angle = 2 * math.pi * i / n_sides - math.pi / 2
        points.append(
            Point2D(
                center.x + radius * math.cos(angle),
                center.y + radius * math.sin(angle),
                i,
            )
        )
    return Polygon(points)


def generate_star(
    n_points: int = 5,
    outer_radius: float = 40.0,
    inner_radius: float = 20.0,
    center: Point2D = Point2D(50, 50),
) -> Polygon:
    points = []
    for i in range(n_points * 2):
        angle = math.pi * i / n_points - math.pi / 2
        r = outer_radius if i % 2 == 0 else inner_radius
        points.append(
            Point2D(center.x + r * math.cos(angle), center.y + r * math.sin(angle), i)
        )
    return Polygon(points)


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
    parser = argparse.ArgumentParser(description="Generate primitive polygons.")
    parser.add_argument(
        "type",
        choices=["square", "rectangle", "triangle", "regular", "star"],
        help="Type of primitive polygon",
    )
    parser.add_argument(
        "--n", type=int, default=6, help="Number of vertices (for regular/star)"
    )
    parser.add_argument(
        "--size",
        type=float,
        default=100.0,
        help="Size parameter (side length or radius)",
    )
    parser.add_argument(
        "--height", type=float, default=60.0, help="Height (for rectangle)"
    )
    parser.add_argument(
        "--inner-radius", type=float, default=20.0, help="Inner radius (for star)"
    )
    parser.add_argument(
        "--output", default="generated_polygon.png", help="Output visualization file"
    )
    parser.add_argument(
        "--print", action="store_true", help="Print polygon vertices to stdout"
    )

    args = parser.parse_args(argv)

    center = Point2D(50, 50)

    if args.type == "square":
        poly = generate_square(args.size, center)
    elif args.type == "rectangle":
        poly = generate_rectangle(args.size, args.height, center)
    elif args.type == "triangle":
        poly = generate_equilateral_triangle(args.size, center)
    elif args.type == "regular":
        poly = generate_regular_polygon(args.n, args.size / 2, center)
    else:
        poly = generate_star(args.n, args.size / 2, args.inner_radius, center)

    if args.print:
        for p in poly.vertices:
            print(f"{p.x} {p.y}")
        return 0

    print(f"Generated {args.type} polygon with {len(poly.points)} vertices.")

    svg_content = poly_to_svg(list(poly.vertices))

    if args.output.lower().endswith(".png"):
        try:
            from compgeom.graphics.visualization import save_png, save_svg

            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception:
            out_svg = args.output.rsplit(".", 1)[0] + ".svg"
            save_svg(svg_content, out_svg)
            print(f"Warning: PNG generation failed. Saved visualization to {out_svg}")
    else:
        from compgeom.graphics.visualization import save_svg

        save_svg(svg_content, args.output)
        print(f"Saved visualization to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
