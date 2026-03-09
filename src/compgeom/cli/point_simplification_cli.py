import argparse
import random
import time
import sys
from compgeom import Point, Point3D
from compgeom import PointSimplifier

def main():
    parser = argparse.ArgumentParser(description="Simplify a large point set (decimation).")
    parser.add_argument("--n", type=int, default=100000, help="Number of random points to generate")
    parser.add_argument("--ratio", type=float, default=0.01, help="Simplification ratio relative to diagonal")
    parser.add_argument("--dim", choices=["2d", "3d"], default="2d", help="Dimensions of points")
    parser.add_argument("--protected", nargs="+", type=int, help="IDs of points that must not be removed")
    
    args = parser.parse_args()
    
    print(f"Generating {args.n} random {args.dim} points...")
    if args.dim == "2d":
        points = [Point(random.uniform(0, 1000), random.uniform(0, 1000), i) for i in range(args.n)]
    else:
        points = [Point3D(random.uniform(0, 1000), random.uniform(0, 1000), random.uniform(0, 1000), i) for i in range(args.n)]
        
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

if __name__ == "__main__":
    main()
