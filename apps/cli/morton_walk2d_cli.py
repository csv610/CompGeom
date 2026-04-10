from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves
from _shared import handle_walk_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Morton (Z-Order) Curve Walk.")
    parser.add_argument("-x", "--width", type=int, default=128, help="Width of the grid.")
    parser.add_argument("-y", "--height", type=int, default=128, help="Height of the grid.")
    parser.add_argument("-o", "--output", type=str, help="Output filename. Format depends on extension (.json, .png, .svg).")
    parser.add_argument("-w", "--image_width", type=int, default=1024, help="Width of the output image in pixels (default: 1024).")
    args = parser.parse_args(argv)
    
    side = min(args.width, args.height)
    level = int(math.log2(side)) or 1
    
    print(f"--- 2D Morton (Z-Order) Curve ---")
    print(f"Level: {level} ({2**level}x{2**level})")
    
    path_indices = SpaceFillingCurves.morton(level)
    width = 2**level
    
    return handle_walk_output(
        path_indices, width, width, args.output, 
        image_width=args.image_width, curve_name="morton", level=level
    )

if __name__ == "__main__":
    raise SystemExit(main())
