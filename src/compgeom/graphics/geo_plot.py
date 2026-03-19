"""Visualization library for Mesh, polygons, and Voronoi diagrams."""

from __future__ import annotations

import struct
import zlib
from typing import List, Tuple, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import Mesh
from compgeom.mesh.polymesh.voronoi_diagram import VoronoiDiagram
from compgeom.polygon.polygon import Polygon

GeometricObject = Union[Mesh, VoronoiDiagram, Polygon, List[Point2D], List[Point3D]]


class GeomPlot:
    """A lightweight plotting library with a single entry point: `get_image`."""

    @staticmethod
    def get_image(
        objects: GeometricObject | list[GeometricObject],
        format: str = "png",
        width: int = 1000,
        height: int = 1000,
        padding: int = 50,
        **kwargs,
    ) -> Union[str, bytes]:
        """Generate an image for one object or an ordered list of objects."""
        normalized_objects = GeomPlot._normalize_objects(objects)
        min_x, min_y, max_x, max_y = GeomPlot._get_bounds(normalized_objects)
        scale, off_x, off_y = GeomPlot._calculate_transform(
            min_x, min_y, max_x, max_y, width, height, padding
        )

        if format.lower() == "svg":
            return GeomPlot._generate_svg(normalized_objects, width, height, scale, off_x, off_y, **kwargs)
        if format.lower() == "png":
            return GeomPlot._generate_png(normalized_objects, width, height, scale, off_x, off_y, **kwargs)
        raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def _normalize_objects(objects: GeometricObject | list[GeometricObject]) -> list[GeometricObject]:
        if isinstance(objects, list) and not GeomPlot._is_point_list(objects):
            return objects
        return [objects]

    @staticmethod
    def _is_point_list(value: object) -> bool:
        return isinstance(value, list) and (not value or isinstance(value[0], (Point2D, Point3D)))

    @staticmethod
    def _extract_points(obj: GeometricObject) -> list[Point2D]:
        if isinstance(obj, Mesh):
            return list(obj.vertices)
        if isinstance(obj, VoronoiDiagram):
            points = list(obj.points)
            for _, cell in obj.cells:
                points.extend(cell)
            return points
        if isinstance(obj, Polygon):
            return obj.as_list()
        if isinstance(obj, list):
            return list(obj)
        return []

    @staticmethod
    def _get_bounds(objects: list[GeometricObject]) -> Tuple[float, float, float, float]:
        points: list[Point2D] = []
        for obj in objects:
            points.extend(GeomPlot._extract_points(obj))
        if not points:
            return 0, 0, 100, 100
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        return min_x, min_y, max_x, max_y

    @staticmethod
    def _calculate_transform(min_x, min_y, max_x, max_y, width, height, padding):
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0
        canvas_w = width - 2 * padding
        canvas_h = height - 2 * padding
        scale = min(canvas_w / data_w, canvas_h / data_h)
        off_x = padding + (canvas_w - data_w * scale) / 2 - min_x * scale
        off_y = padding + (canvas_h - data_h * scale) / 2 - min_y * scale
        return scale, off_x, off_y

    @staticmethod
    def _to_canvas(x, y, scale, off_x, off_y, height):
        return off_x + x * scale, height - (off_y + y * scale)

    @staticmethod
    def _append_svg(svg: list[str], obj: GeometricObject, height, scale, off_x, off_y, **kwargs) -> None:
        edge_color = kwargs.get("edge_color", "black")
        face_color = kwargs.get("face_color", "none")
        site_color = kwargs.get("site_color", "red")
        site_size = kwargs.get("site_size", 4)
        edge_width = kwargs.get("edge_width", 1.0)
        color = kwargs.get("color", "green")
        size = kwargs.get("size", 5)

        if isinstance(obj, Mesh):
            for face in obj.elements:
                pts = [
                    GeomPlot._to_canvas(obj.vertices[v_idx].x, obj.vertices[v_idx].y, scale, off_x, off_y, height)
                    for v_idx in face
                ]
                points_str = " ".join(f"{px},{py}" for px, py in pts)
                svg.append(
                    f'<polygon points="{points_str}" fill="{face_color}" stroke="{edge_color}" stroke-width="{edge_width}" />'
                )
            return

        if isinstance(obj, VoronoiDiagram):
            for _, cell in obj.cells:
                if not cell:
                    continue
                pts = [GeomPlot._to_canvas(p.x, p.y, scale, off_x, off_y, height) for p in cell]
                points_str = " ".join(f"{px},{py}" for px, py in pts)
                svg.append(
                    f'<polygon points="{points_str}" fill="none" stroke="{edge_color}" stroke-width="{edge_width}" />'
                )
            for p in obj.points:
                cx, cy = GeomPlot._to_canvas(p.x, p.y, scale, off_x, off_y, height)
                svg.append(f'<circle cx="{cx}" cy="{cy}" r="{site_size}" fill="{site_color}" />')
            return

        if isinstance(obj, Polygon):
            polygon = obj.as_list()
            if not polygon:
                return
            pts = [GeomPlot._to_canvas(p.x, p.y, scale, off_x, off_y, height) for p in polygon]
            points_str = " ".join(f"{px},{py}" for px, py in pts)
            svg.append(
                f'<polygon points="{points_str}" fill="{face_color}" stroke="{edge_color}" stroke-width="{edge_width}" />'
            )
            return

        if isinstance(obj, list):
            for p in obj:
                cx, cy = GeomPlot._to_canvas(p.x, p.y, scale, off_x, off_y, height)
                svg.append(f'<circle cx="{cx}" cy="{cy}" r="{size}" fill="{color}" />')

    @staticmethod
    def _generate_svg(objects, width, height, scale, off_x, off_y, **kwargs) -> str:
        svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        for obj in objects:
            GeomPlot._append_svg(svg, obj, height, scale, off_x, off_y, **kwargs)
        svg.append("</svg>")
        return "\n".join(svg)

    @staticmethod
    def _generate_png(objects, width, height, scale, off_x, off_y, **kwargs) -> bytes:
        img_data = bytearray([255, 255, 255] * (width * height))

        def set_pixel(x, y, color):
            x, y = int(x), int(y)
            if 0 <= x < width and 0 <= y < height:
                idx = (y * width + x) * 3
                img_data[idx : idx + 3] = color

        def draw_line(p1, p2, color):
            x1, y1 = GeomPlot._to_canvas(p1.x, p1.y, scale, off_x, off_y, height)
            x2, y2 = GeomPlot._to_canvas(p2.x, p2.y, scale, off_x, off_y, height)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
            err = dx - dy
            while True:
                set_pixel(x1, y1, color)
                if x1 == x2 and y1 == y2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

        def draw_circle(p, r, color):
            cx, cy = GeomPlot._to_canvas(p.x, p.y, scale, off_x, off_y, height)
            cx, cy, r = int(cx), int(cy), int(r)
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r, cx + r + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r**2:
                        set_pixel(x, y, color)

        def parse_color(c):
            colors = {
                "black": (0, 0, 0),
                "red": (255, 0, 0),
                "green": (0, 255, 0),
                "blue": (0, 0, 255),
                "gray": (128, 128, 128),
            }
            return colors.get(c.lower(), (0, 0, 0))

        def draw_object(obj: GeometricObject) -> None:
            if isinstance(obj, Mesh):
                line_color = parse_color(kwargs.get("edge_color", "black"))
                for face in obj.elements:
                    for i in range(len(face)):
                        draw_line(obj.vertices[face[i]], obj.vertices[face[(i + 1) % len(face)]], line_color)
                return

            if isinstance(obj, VoronoiDiagram):
                edge_color = parse_color(kwargs.get("edge_color", "blue"))
                site_color = parse_color(kwargs.get("site_color", "red"))
                for _, cell in obj.cells:
                    for i in range(len(cell)):
                        draw_line(cell[i], cell[(i + 1) % len(cell)], edge_color)
                for p in obj.points:
                    draw_circle(p, kwargs.get("site_size", 4), site_color)
                return

            if isinstance(obj, Polygon):
                line_color = parse_color(kwargs.get("edge_color", "black"))
                polygon = obj.as_list()
                for i in range(len(polygon)):
                    draw_line(polygon[i], polygon[(i + 1) % len(polygon)], line_color)
                return

            if isinstance(obj, list):
                point_color = parse_color(kwargs.get("color", "green"))
                for p in obj:
                    draw_circle(p, kwargs.get("size", 5), point_color)

        for obj in objects:
            draw_object(obj)

        png = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        png += struct.pack(">I", 13) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF)
        rows = [b"\x00" + bytes(img_data[y * width * 3 : (y + 1) * width * 3]) for y in range(height)]
        compressed = zlib.compress(b"".join(rows))
        png += (
            struct.pack(">I", len(compressed))
            + b"IDAT"
            + compressed
            + struct.pack(">I", zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF)
        )
        png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
        return png
