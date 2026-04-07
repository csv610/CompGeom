from __future__ import annotations

import argparse
import time
from compgeom import PointSimplifier
from _shared import read_input_lines, parse_points

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simplify a point set (decimation).")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--ratio", type=float, default=0.01, help="Simplification ratio relative to diagonal.")
    parser.add_argument("--protected", nargs="+", type=int, help="IDs of points that must not be removed.")
    
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1
            
    start_time = time.time()
    
    protected_set = set(args.protected) if args.protected else set()
    if protected_set:
        print(f"Simplifying with ratio {args.ratio} (Protected IDs: {len(protected_set)})...")
    else:
        print(f"Simplifying with ratio {args.ratio}...")
    
    simplified = PointSimplifier.simplify(points, args.ratio, protected_ids=protected_set)
    
    elapsed = time.time() - start_time
    reduction = (1 - len(simplified) / len(points)) * 100
    
    print(f"\nResults:")
    print(f"  Original Points:   {len(points)}")
    print(f"  Simplified Points: {len(simplified)}")
    print(f"  Reduction:         {reduction:.2f}%")
    print(f"  Time Taken:        {elapsed:.4f} seconds")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
