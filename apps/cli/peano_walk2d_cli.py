from __future__ import annotations

import argparse
import math
import json
from compgeom import SpaceFillingCurves

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Peano Curve Walk.")
    parser.add_argument("-l", "--level", type=int, default=1, help="Level of the Peano curve (power of 3, default: 1).")
    parser.add_argument("-o", "--output", type=str, default="path.json", help="Output filename (default: path.json). Format depends on extension (.json, .png, .svg).")
    parser.add_argument("-w", "--image_width", type=int, default=1024, help="Width of the output image in pixels (default: 1024).")
    args = parser.parse_args(argv)
    
    level = args.level
    
    print(f"--- 2D Peano Curve ---")
    print(f"Level: {level} ({3**level}x{3**level})")
    
    path_indices = SpaceFillingCurves.peano(level)
    num_points = len(path_indices)
    
    width = 3**level
    def to_coords(idx):
        return (idx % width, idx // width)
    
    start_p, end_p = to_coords(path_indices[0]), to_coords(path_indices[-1])
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    
    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {num_points-1}")
    print(f"Unique Cells: {len(set(path_indices))}")
    print(f"Final Cell Index: {path_indices[-1]}")
    print(f"Displacement: {disp:.4f}")

    if args.output:
        if args.output.lower().endswith(('.png', '.svg')):
            cell_size = max(1, args.image_width // width)
            SpaceFillingCurves.save_image(path_indices, width, width, args.output, cell_size)
            print(f"Saved path image to {args.output} (cell size: {cell_size})")
        else:
            # Default to JSON
            path_coords = [to_coords(idx) for idx in path_indices]
            with open(args.output, "w") as f:
                json.dump({
                    "curve": "peano",
                    "level": level,
                    "width": width,
                    "height": width,
                    "indices": path_indices,
                    "coordinates": path_coords
                }, f, indent=4)
            print(f"Saved path data to {args.output}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
