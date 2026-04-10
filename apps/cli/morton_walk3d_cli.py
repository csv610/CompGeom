from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves
from ._shared import handle_walk3d_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="3D Morton (Z-Order) Curve Walk.")
    parser.add_argument("-x", "--width", type=int, default=32, help="Width of the grid.")
    parser.add_argument("-y", "--height", type=int, default=32, help="Height of the grid.")
    parser.add_argument("-z", "--depth", type=int, default=32, help="Depth of the grid.")
    parser.add_argument("-o", "--output", type=str, help="Output filename (.json).")
    parser.add_argument("-v", "--visualize", action="store_true", help="Visualize path in 3D.")
    args = parser.parse_args(argv)
    
    side = min(args.width, args.height, args.depth)
    level = int(math.log2(side)) or 1
    
    print(f"--- 3D Morton (Z-Order) Curve ---")
    print(f"Level: {level} ({2**level}x{2**level}x{2**level})")
    
    path_coords = SpaceFillingCurves.morton_3d(level)
    width = 2**level
    
    return handle_walk3d_output(
        path_coords, width, width, width, args.output, 
        curve_name="morton_3d", level=level, visualize=args.visualize
    )

if __name__ == "__main__":
    raise SystemExit(main())
