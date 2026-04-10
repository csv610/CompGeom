from __future__ import annotations

import argparse
from compgeom import SpaceFillingCurves
from ._shared import handle_walk_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Peano Curve Walk.")
    parser.add_argument("-l", "--level", type=int, default=1, help="Level of the Peano curve (power of 3, default: 1).")
    parser.add_argument("-o", "--output", type=str, help="Output filename (.json, .png, .svg).")
    parser.add_argument("-w", "--image_width", type=int, default=1024, help="Width of output image (pixels).")
    args = parser.parse_args(argv)
    
    level = args.level
    print(f"--- 2D Peano Curve ---")
    print(f"Level: {level} ({3**level}x{3**level})")
    
    path_indices = SpaceFillingCurves.peano(level)
    width = 3**level
    
    return handle_walk_output(
        path_indices, width, width, args.output, 
        image_width=args.image_width, curve_name="peano", level=level
    )

if __name__ == "__main__":
    raise SystemExit(main())
