import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point2D
from compgeom.kernel import Point2D, cross_product
from compgeom.polygon.convex_hull import ConvexHullGenerator, GrahamScan, MonotoneChain, QuickHull, Chan
from compgeom.polygon.polygon import Polygon

def verify_convex_hull(points: list[Point2D], hull: list[Point2D]) -> bool:
    if not hull:
        return len(points) == 0
    
    # 1. All hull vertices must be in the original points
    point_set = set((p.x, p.y) for p in points)
    for p in hull:
        if (p.x, p.y) not in point_set:
            return False
            
    # 2. Hull must be convex and CCW (all cross products >= 0)
    n = len(hull)
    if n >= 3:
        for i in range(n):
            if cross_product(hull[i-1], hull[i], hull[(i+1)%n]) < -1e-9:
                return False
                
    # 3. All original points must be inside or on the boundary of the hull
    hull_poly = Polygon(hull)
    for p in points:
        if not hull_poly.contains_point(p):
            # Precision issues can happen, but for random points in large range it's usually fine
            return False
            
    return True

def run_benchmarks():
    # Chan's algorithm with large N and many hull points can be slow if t gets large.
    # Quickhull is also sensitive to point distribution.
    sizes = [10**2, 10**3, 10**4, 10**5] # Reduced size for verification overhead
    
    print("Convex Hull Algorithms Scalability and Correctness Analysis")
    print("=" * 125)
    print(f"{'N Points':<12} | {'Graham Scan':<18} | {'Monotone Chain':<18} | {'Quick Hull':<18} | {'Chan (s)':<18} | {'Correct?'}")
    print("-" * 125)
    
    for n in sizes:
        # Generate random 2D points in [0, 1000]
        points = [
            Point2D(random.uniform(0, 1000), random.uniform(0, 1000), id=i) 
            for i in range(n)
        ]
        
        results = {}
        correct = True
        
        # Benchmark Graham Scan
        start = time.perf_counter()
        try:
            h = GrahamScan().generate(points)
            results['graham'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull(points, h): correct = False
        except Exception:
            results['graham'] = "Error"
            correct = False
            
        # Benchmark Monotone Chain
        start = time.perf_counter()
        try:
            h = MonotoneChain().generate(points)
            results['monotone'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull(points, h): correct = False
        except Exception:
            results['monotone'] = "Error"
            correct = False

        # Benchmark Quick Hull
        start = time.perf_counter()
        try:
            h = QuickHull().generate(points)
            results['quick'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull(points, h): correct = False
        except Exception:
            results['quick'] = "Error"
            correct = False

        # Benchmark Chan
        start = time.perf_counter()
        try:
            h = Chan().generate(points)
            results['chan'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull(points, h): correct = False
        except Exception:
            results['chan'] = "Error"
            correct = False

        print(f"{n:<12} | {results['graham']:<18} | {results['monotone']:<18} | {results['quick']:<18} | {results['chan']:<18} | {str(correct)}")

if __name__ == "__main__":
    run_benchmarks()
