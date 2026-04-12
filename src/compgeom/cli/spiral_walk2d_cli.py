from __future__ import annotations

import argparse
import json
import math
from compgeom.algo.random_walker import generate_spiral_path
from compgeom.algo import SpaceFillingCurves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Spiral Walk generator")
    parser.add_argument("-x", "--width", type=int, default=10)
    parser.add_argument("-y", "--height", type=int, default=10)
    parser.add_argument("-sx", "--start_x", type=int)
    parser.add_argument("-sy", "--start_y", type=int)
    parser.add_argument("-o", "--output", help="Output filename (.json, .png)")
    parser.add_argument("-w", "--image_width", type=int, default=1024)
    args = parser.parse_args(argv)

    n, m = args.width, args.height
    print(f"--- 2D Spiral Walk ({n}x{m}) ---")
    path = generate_spiral_path(n, m, args.start_x, args.start_y)

    path_indices = [y * n + x for x, y in path]

    num_points = len(path_indices)
    start_p, end_p = path[0], path[-1]
    disp = math.sqrt((end_p[0] - start_p[0]) ** 2 + (end_p[1] - start_p[1]) ** 2)

    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {num_points - 1}")
    print(f"Unique Cells: {len(set(path_indices))}")
    print(f"Final Cell Index: {path_indices[-1]}")
    print(f"Displacement: {disp:.4f}")

    if args.output:
        ext = args.output.lower()
        if ext.endswith(".png"):
            cell_size = max(1, args.image_width // n)
            SpaceFillingCurves.save_image(path_indices, n, m, args.output, cell_size)
            print(f"Saved path image to {args.output} (cell size: {cell_size})")
        elif ext.endswith(".json"):
            data = {
                "curve": "spiral",
                "width": n,
                "height": m,
                "indices": path_indices,
                "coordinates": path,
            }
            with open(args.output, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Saved path data to {args.output}")
        else:
            print(
                f"Error: Unsupported output format '{args.output}'. Supported formats: .json, .png"
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
