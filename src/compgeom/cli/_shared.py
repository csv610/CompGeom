from __future__ import annotations

import sys
import numpy as np
from collections.abc import Iterable, Sequence

from compgeom import Point2D


def read_stdin_lines() -> list[str]:
    return sys.stdin.readlines()


def read_nonempty_stdin_lines() -> list[str]:
    return [line.strip() for line in sys.stdin if line.strip()]


def read_input_lines(file_path: str | None = None) -> list[str]:
    """Read lines from a file or stdin if file_path is None."""
    if file_path:
        try:
            with open(file_path, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return []
    return read_nonempty_stdin_lines()


def print_lines(lines: Iterable[str]) -> None:
    for line in lines:
        print(line)


def parse_points(lines: Iterable[str], *, with_ids: bool = False) -> list[Point2D]:
    points: list[Point2D] = []
    for line in lines:
        point = parse_point_line(line, point_id=len(points) if not with_ids else None, with_id=with_ids)
        if point is not None:
            points.append(point)
    return points


def parse_point_line(
    line: str,
    *,
    point_id: int | None = None,
    with_id: bool = False,
) -> Point2D | None:
    return parse_point_fields(line.strip().split(), point_id=point_id, with_id=with_id)


def parse_point_fields(
    fields: Sequence[str],
    *,
    point_id: int | None = None,
    with_id: bool = False,
) -> Point2D | None:
    expected = 3 if with_id else 2
    if len(fields) < expected:
        return None

    try:
        if with_id:
            return Point2D(float(fields[1]), float(fields[2]), int(fields[0]))
        if point_id is None:
            return Point2D(float(fields[0]), float(fields[1]))
        return Point2D(float(fields[0]), float(fields[1]), point_id)
    except ValueError:
        return None


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def demo_points() -> list[Point2D]:
    coordinates = [
        (0.0, 0.0),
        (2.0, 1.0),
        (1.0, 3.0),
        (-1.0, 2.0),
        (3.5, 2.5),
        (2.25, 2.0),
    ]
    return [Point2D(x, y, index) for index, (x, y) in enumerate(coordinates)]


def demo_polygon() -> list[Point2D]:
    coordinates = [
        (0.0, 0.0),
        (5.0, 0.0),
        (6.0, 2.0),
        (4.0, 5.0),
        (1.5, 4.0),
        (-1.0, 2.0),
    ]
    return [Point2D(x, y, index) for index, (x, y) in enumerate(coordinates)]


def demo_mesh_lines() -> list[str]:
    return [
        "0 0 0\n",
        "1 1 0\n",
        "2 0 1\n",
        "3 1 1\n",
        "T\n",
        "0 1 2\n",
        "1 3 2\n",
    ]


def handle_walk_output(
    path_indices: list[int],
    width: int,
    height: int,
    output_path: str | None,
    image_width: int = 1024,
    curve_name: str = "curve",
    level: int | None = None,
    to_coords_func: callable | None = None,
) -> int:
    """Handle standard output for space-filling curve walks (stats, image, JSON)."""
    import json
    import math
    from compgeom import SpaceFillingCurves

    num_points = len(path_indices)

    if to_coords_func is None:

        def to_coords_func(idx):
            return (idx % width, idx // width)

    start_p, end_p = to_coords_func(path_indices[0]), to_coords_func(path_indices[-1])
    disp = math.sqrt((end_p[0] - start_p[0]) ** 2 + (end_p[1] - start_p[1]) ** 2)

    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {num_points - 1}")
    print(f"Unique Cells: {len(set(path_indices))}")
    print(f"Final Cell Index: {path_indices[-1]}")
    print(f"Displacement: {disp:.4f}")

    if output_path:
        ext = output_path.lower()
        if ext.endswith((".png", ".svg")):
            cell_size = max(1, image_width // width)
            SpaceFillingCurves.save_image(path_indices, width, height, output_path, cell_size)
            print(f"Saved path image to {output_path} (cell size: {cell_size})")
        elif ext.endswith(".json"):
            path_coords = [to_coords_func(idx) for idx in path_indices]
            data = {
                "curve": curve_name,
                "width": width,
                "height": height,
                "indices": path_indices,
                "coordinates": path_coords,
            }
            if level is not None:
                data["level"] = level

            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Saved path data to {output_path}")
        else:
            print(f"Error: Unsupported output format '{output_path}'. Supported formats: .json, .png, .svg")
            return 1
    return 0


def handle_walk3d_output(
    path_coords: list[tuple[int, int, int]],
    width: int,
    height: int,
    depth: int,
    output_path: str | None,
    curve_name: str = "curve",
    level: int | None = None,
    visualize: bool = False,
) -> int:
    """Handle standard output for 3D space-filling curve walks."""
    import json
    import math
    import numpy as np

    num_points = len(path_coords)
    start_p, end_p = path_coords[0], path_coords[-1]
    disp = math.sqrt((end_p[0] - start_p[0]) ** 2 + (end_p[1] - start_p[1]) ** 2 + (end_p[2] - start_p[2]) ** 2)

    print(f"\n--- 3D Walk Results ---")
    print(f"Total Steps: {num_points - 1}")
    print(f"Unique Cells: {len(set(path_coords))}")
    print(f"Final Pos: {end_p}")
    print(f"Displacement: {disp:.4f}")

    if output_path:
        if output_path.lower().endswith(".json"):
            data = {"curve": curve_name, "width": width, "height": height, "depth": depth, "coordinates": path_coords}
            if level is not None:
                data["level"] = level

            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Saved path data to {output_path}")
        else:
            print(f"Error: Unsupported output format '{output_path}'. Supported formats: .json")
            return 1

    if visualize:
        import pyvista as pv

        coords = np.array(path_coords)
        plotter = pv.Plotter()
        plotter.add_lines(coords, color="blue", width=2)
        plotter.add_points(coords, color="red", point_size=5)
        plotter.show()

    return 0


def visualize_with_pyvista(
    points: list[Point2D] | None = None,
    faces: list[list[int]] | None = None,
    polygons: list[list[Point2D]] | None = None,
) -> None:
    """Visualize points, meshes, and polygons using pyvista."""
    import pyvista as pv

    plotter = pv.Plotter()

    if points:
        coords = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in points])
        plotter.add_points(coords, color="red", point_size=10.0, render_points_as_spheres=True)

    if faces and points:
        coords = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in points])
        # PyVista expects faces in a specific format: [n_points, i1, i2, ..., in, ...]
        pv_faces = []
        for face in faces:
            pv_faces.append(len(face))
            pv_faces.extend(face)

        mesh = pv.PolyData(coords, pv_faces)
        plotter.add_mesh(mesh, show_edges=True, color="lightblue", opacity=0.7)

    if polygons:
        for i, poly in enumerate(polygons):
            poly_coords = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in poly])
            # Create a closed loop for the polygon edges
            loop = np.vstack([poly_coords, poly_coords[0]])
            plotter.add_lines(loop, color="blue", width=2)
            # Optionally add a label or different color for each polygon

    plotter.show()
