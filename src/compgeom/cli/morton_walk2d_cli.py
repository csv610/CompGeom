from __future__ import annotations

import argparse
import json
import math
from compgeom.algo import SpaceFillingCurves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Morton (Z-Order) Curve Walk.")
    parser.add_argument(
        "-x", "--width", type=int, default=128, help="Width of the grid."
    )
    parser.add_argument(
        "-y", "--height", type=int, default=128, help="Height of the grid."
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output filename (.json, .png)"
    )
    parser.add_argument(
        "-w",
        "--image_width",
        type=int,
        default=1024,
        help="Width of the output image in pixels (default: 1024).",
    )
    args = parser.parse_args(argv)

    side = min(args.width, args.height)
    level = int(math.log2(side)) or 1

    print(f"--- 2D Morton (Z-Order) Curve ---")
    print(f"Level: {level} ({2**level}x{2**level})")

    path_indices = SpaceFillingCurves.morton(level)
    width = 2**level

    num_points = len(path_indices)

    def to_coords_func(idx):
        return (idx % width, idx // width)

    start_p, end_p = to_coords_func(path_indices[0]), to_coords_func(path_indices[-1])
    disp = math.sqrt((end_p[0] - start_p[0]) ** 2 + (end_p[1] - start_p[1]) ** 2)

    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {num_points - 1}")
    print(f"Unique Cells: {len(set(path_indices))}")
    print(f"Final Cell Index: {path_indices[-1]}")
    print(f"Displacement: {disp:.4f}")

    if args.output:
        ext = args.output.lower()
        if ext.endswith(".png"):
            cell_size = max(1, args.image_width // width)
            SpaceFillingCurves.save_image(
                path_indices, width, width, args.output, cell_size
            )
            print(f"Saved path image to {args.output} (cell size: {cell_size})")
        elif ext.endswith(".json"):
            path_coords = [to_coords_func(idx) for idx in path_indices]
            data = {
                "curve": "morton",
                "width": width,
                "height": width,
                "level": level,
                "indices": path_indices,
                "coordinates": path_coords,
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
