from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves
from ._shared import handle_walk3d_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="3D Hilbert Curve Walk.")
    parser.add_argument("-x", "--width", type=int, default=32, help="Width of the grid.")
    parser.add_argument("-y", "--height", type=int, default=32, help="Height of the grid.")
    parser.add_argument("-z", "--depth", type=int, default=32, help="Depth of the grid.")
    parser.add_argument("-o", "--order", type=int, help="Order of the Hilbert curve.")
    parser.add_argument("-f", "--output", type=str, help="Output filename (.json).")
    parser.add_argument("-v", "--visualize", action="store_true", help="Visualize path in 3D.")
    args = parser.parse_args(argv)
    
    order = args.order if args.order is not None else (int(math.log2(min(args.width, args.height, args.depth))) or 1)
    
    print(f"--- 3D Hilbert Curve ---")
    print(f"Order: {order} ({2**order}x{2**order}x{2**order})")
    
    path_coords = SpaceFillingCurves.hilbert_3d(order)
    width = 2**order
    
    return handle_walk3d_output(
        path_coords, width, width, width, args.output, 
        curve_name="hilbert_3d", level=order, visualize=args.visualize
    )

if __name__ == "__main__":
    raise SystemExit(main())
