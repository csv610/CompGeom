from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Peano Curve Walk.")
    parser.add_argument("--width", type=int, default=81, help="Width of the grid.")
    parser.add_argument("--height", type=int, default=81, help="Height of the grid.")
    parser.add_argument("--level", type=int, help="Level of the Peano curve (power of 3).")
    args = parser.parse_args(argv)
    
    level = args.level if args.level is not None else (int(math.log(min(args.width, args.height), 3)) or 1)
    
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
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
