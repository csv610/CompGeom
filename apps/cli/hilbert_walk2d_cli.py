from __future__ import annotations

import argparse
import math
from compgeom import SpaceFillingCurves

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Hilbert Curve Walk.")
    parser.add_argument("--width", type=int, default=128, help="Width of the grid.")
    parser.add_argument("--height", type=int, default=128, help="Height of the grid.")
    parser.add_argument("--order", type=int, help="Order of the Hilbert curve.")
    args = parser.parse_args(argv)
    
    order = args.order if args.order is not None else (int(math.log2(min(args.width, args.height))) or 1)
    
    print(f"--- 2D Hilbert Curve ---")
    print(f"Order: {order} ({2**order}x{2**order})")
    
    path_indices = SpaceFillingCurves.hilbert(order)
    num_points = len(path_indices)
    
    width = 2**order
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
