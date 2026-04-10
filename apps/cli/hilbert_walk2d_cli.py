from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves
from ._shared import handle_walk_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Hilbert Curve Walk.")
    parser.add_argument("-x", "--width", type=int, default=128, help="Width of the grid.")
    parser.add_argument("-y", "--height", type=int, default=128, help="Height of the grid.")
    parser.add_argument("-o", "--order", type=int, help="Order of the Hilbert curve.")
    parser.add_argument("-f", "--output", type=str, help="Output filename (.json, .png, .svg).")
    parser.add_argument("-w", "--image_width", type=int, default=1024, help="Width of output image (pixels).")
    args = parser.parse_args(argv)
    
    order = args.order if args.order is not None else (int(math.log2(min(args.width, args.height))) or 1)
    
    print(f"--- 2D Hilbert Curve ---")
    print(f"Order: {order} ({2**order}x{2**order})")
    
    path_indices = SpaceFillingCurves.hilbert(order)
    width = 2**order
    
    return handle_walk_output(
        path_indices, width, width, args.output, 
        image_width=args.image_width, curve_name="hilbert", level=order
    )

if __name__ == "__main__":
    raise SystemExit(main())
