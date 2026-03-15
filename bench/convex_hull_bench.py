import time
import random
import sys
import os
import numpy as np
from scipy.spatial import ConvexHull as ScipyConvexHull

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point2D, Point3D, cross_product
from compgeom.polygon.convex_hull import ConvexHull
from compgeom.polygon.polygon import Polygon

def verify_convex_hull_2d(points: list[Point2D], hull: list[Point2D]) -> bool:
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
            return False
            
    return True

def verify_convex_hull_3d(points: list[Point3D], mesh) -> bool:
    if not mesh:
        return len(points) < 4
    return len(mesh.vertices) > 0 and len(mesh.faces) > 0

def run_benchmarks():
    sizes = [10**2, 10**3, 10**4, 10**5]
    
    # Warm-up to handle lazy imports
    warmup_2d = [Point2D(random.random(), random.random()) for _ in range(10)]
    warmup_3d = [Point3D(random.random(), random.random(), random.random()) for _ in range(10)]
    ConvexHull.generate(warmup_2d, algorithm="scipy")
    ConvexHull.generate(warmup_2d, algorithm="graham_scan")
    ConvexHull.generate(warmup_2d, algorithm="monotone_chain")
    ConvexHull.generate(warmup_2d, algorithm="quickhull")
    ConvexHull.generate(warmup_2d, algorithm="chan")
    try:
        ConvexHull.generate(warmup_3d)
    except Exception:
        pass

    print("2D Convex Hull Algorithms Scalability and Correctness Analysis")
    print("=" * 160)
    print(f"{'N Points':<12} | {'Default (SciPy)':<18} | {'Graham Scan':<18} | {'Monotone Chain':<18} | {'Quick Hull':<18} | {'Chan (s)':<18} | {'Correct?'}")
    print("-" * 160)
    
    for n in sizes:
        points_2d = [
            Point2D(random.uniform(0, 1000), random.uniform(0, 1000), id=i) 
            for i in range(n)
        ]
        
        results = {}
        correct = True
        
        # Benchmark Default (SciPy)
        start = time.perf_counter()
        try:
            h = ConvexHull.generate(points_2d) # Uses default "scipy"
            results['default'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull_2d(points_2d, h): correct = False
        except Exception:
            results['default'] = "Error"
            correct = False

        # Benchmark Graham Scan
        start = time.perf_counter()
        try:
            h = ConvexHull.generate(points_2d, algorithm="graham_scan")
            results['graham'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull_2d(points_2d, h): correct = False
        except Exception:
            results['graham'] = "Error"
            correct = False
            
        # Benchmark Monotone Chain
        start = time.perf_counter()
        try:
            h = ConvexHull.generate(points_2d, algorithm="monotone_chain")
            results['monotone'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull_2d(points_2d, h): correct = False
        except Exception:
            results['monotone'] = "Error"
            correct = False

        # Benchmark Quick Hull
        start = time.perf_counter()
        try:
            h = ConvexHull.generate(points_2d, algorithm="quickhull")
            results['quick'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull_2d(points_2d, h): correct = False
        except Exception:
            results['quick'] = "Error"
            correct = False

        # Benchmark Chan
        start = time.perf_counter()
        try:
            h = ConvexHull.generate(points_2d, algorithm="chan")
            results['chan'] = f"{time.perf_counter() - start:.4f}"
            if not verify_convex_hull_2d(points_2d, h): correct = False
        except Exception:
            results['chan'] = "Error"
            correct = False

        print(f"{n:<12} | {results['default']:<18} | {results['graham']:<18} | {results['monotone']:<18} | {results['quick']:<18} | {results['chan']:<18} | {str(correct)}")

    print("\n\n3D Convex Hull Scalability Analysis")
    print("=" * 60)
    print(f"{'N Points':<12} | {'3D Convex Hull (s)':<25} | {'Correct?'}")
    print("-" * 60)

    for n in sizes:
        points_3d = [
            Point3D(random.uniform(0, 1000), random.uniform(0, 1000), random.uniform(0, 1000), id=i) 
            for i in range(n)
        ]
        
        start = time.perf_counter()
        try:
            mesh = ConvexHull.generate(points_3d)
            duration = f"{time.perf_counter() - start:.4f}"
            correct = verify_convex_hull_3d(points_3d, mesh)
        except Exception as e:
            duration = "Error"
            correct = False

        print(f"{n:<12} | {duration:<25} | {str(correct)}")

if __name__ == "__main__":
    run_benchmarks()
