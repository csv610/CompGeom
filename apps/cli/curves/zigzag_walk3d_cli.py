"""3D Zigzag Curve Walk CLI."""

from __future__ import annotations

import argparse
import json
import math

from compgeom.algo import SpaceFillingCurves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="3D Zigzag Curve Walk.")
    parser.add_argument("-x", "--width", type=int, default=8, help="Width of the grid.")
    parser.add_argument(
        "-y", "--height", type=int, default=8, help="Height of the grid."
    )
    parser.add_argument("-z", "--depth", type=int, default=8, help="Depth of the grid.")
    parser.add_argument("-f", "--output", type=str, help="Output filename (.json)")
    parser.add_argument(
        "-v", "--visualize", action="store_true", help="Visualize path in 3D."
    )
    args = parser.parse_args(argv)

    width, height, depth = args.width, args.height, args.depth

    print(f"--- 3D Zigzag Curve ---")
    print(f"Grid: {width}x{height}x{depth}")

    path_coords = SpaceFillingCurves.zigzag_3d(width, height, depth)

    num_points = len(path_coords)
    start_p, end_p = path_coords[0], path_coords[-1]
    disp = math.sqrt(
        (end_p[0] - start_p[0]) ** 2
        + (end_p[1] - start_p[1]) ** 2
        + (end_p[2] - start_p[2]) ** 2
    )

    print(f"\n--- 3D Walk Results ---")
    print(f"Total Steps: {num_points - 1}")
    print(f"Unique Cells: {len(set(path_coords))}")
    print(f"Final Pos: {end_p}")
    print(f"Displacement: {disp:.4f}")

    if args.output:
        if args.output.lower().endswith(".json"):
            data = {
                "curve": "zigzag_3d",
                "width": width,
                "height": height,
                "depth": depth,
                "coordinates": path_coords,
            }
            with open(args.output, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Saved path data to {args.output}")
        else:
            print(
                f"Error: Unsupported output format '{args.output}'. Supported formats: .json"
            )
            return 1

    if args.visualize:
        import numpy as np
        import pyvista as pv

        coords = np.array(path_coords)
        plotter = pv.Plotter()
        plotter.add_lines(coords, color="blue", width=2)
        plotter.add_points(coords, color="red", point_size=5)
        plotter.show()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
