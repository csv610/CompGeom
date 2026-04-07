from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Morton (Z-Order) Curve Walk.")
    parser.add_argument("--width", type=int, default=128, help="Width of the grid.")
    parser.add_argument("--height", type=int, default=128, help="Height of the grid.")
    args = parser.parse_args(argv)
    
    side = min(args.width, args.height)
    level = int(math.log2(side)) or 1
    
    print(f"--- 2D Morton (Z-Order) Curve ---")
    print(f"Level: {level} ({2**level}x{2**level})")
    
    path_indices = SpaceFillingCurves.morton(level)
    num_points = len(path_indices)
    
    width = 2**level
    def to_coords(idx):
        return (idx % width, idx // width)
        
    start_p, end_p = to_coords(path_indices[0]), to_coords(path_indices[-1])
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    
    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {num_points-1}")
    print(f"Unique Cells: {len(set(path_indices))}")
    print(f"Final Cell Index: {path_indices[-1]}")
    print(f"Displacement: {disp:.4f}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
