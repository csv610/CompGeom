import time
import sys
import os
import random

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from compgeom.kernel import Point2D
    from compgeom.polygon.polygon import Polygon
    from compgeom.polygon.polygon_generator import (
        generate_convex_polygon, 
        generate_star_shaped_polygon
    )
    from compgeom.polygon.polygon_boolean import (
        polygon_union, 
        polygon_intersection, 
        polygon_difference, 
        polygon_xor, 
        verify_boolean_op
    )
except ImportError as e:
    print(f"Error importing compgeom: {e}")
    sys.exit(1)

def run_benchmarks():
    sizes = [10, 50, 100, 200, 500]
    
    # Warm-up
    p1 = generate_convex_polygon(10, (0, 50), (0, 50))
    p2 = generate_convex_polygon(10, (25, 75), (25, 75))
    try:
        polygon_union(p1, p2)
    except Exception:
        pass
    
    print("Polygon Boolean Operations Scalability and Correctness Analysis")
    print("=" * 140)
    print(f"{'N Vertices':<12} | {'Union (s)':<18} | {'Intersection':<18} | {'Difference':<18} | {'XOR (s)':<18} | {'Correct?'}")
    print("-" * 140)
    
    for n in sizes:
        # Generate two overlapping convex polygons
        p1 = generate_convex_polygon(n, (0, 60), (0, 60))
        p2 = generate_convex_polygon(n, (30, 90), (30, 90))
        
        results = {}
        all_correct = True
        
        # Benchmark Union
        start = time.perf_counter()
        try:
            res = polygon_union(p1, p2)
            results['union'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "union"): all_correct = False
        except Exception:
            results['union'] = "Error"
            all_correct = False
            
        # Benchmark Intersection
        start = time.perf_counter()
        try:
            res = polygon_intersection(p1, p2)
            results['intersection'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "intersection"): all_correct = False
        except Exception:
            results['intersection'] = "Error"
            all_correct = False

        # Benchmark Difference
        start = time.perf_counter()
        try:
            res = polygon_difference(p1, p2)
            results['difference'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "difference"): all_correct = False
        except Exception:
            results['difference'] = "Error"
            all_correct = False

        # Benchmark XOR
        start = time.perf_counter()
        try:
            res = polygon_xor(p1, p2)
            results['xor'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "xor"): all_correct = False
        except Exception:
            results['xor'] = "Error"
            all_correct = False

        print(f"{n:<12} | {results['union']:<18} | {results['intersection']:<18} | {results['difference']:<18} | {results['xor']:<18} | {str(all_correct)}")

    print("\nComplex Polygon Boolean Operations (Star-Shaped)")
    print("=" * 140)
    print(f"{'N Vertices':<12} | {'Union (s)':<18} | {'Intersection':<18} | {'Difference':<18} | {'XOR (s)':<18} | {'Correct?'}")
    print("-" * 140)

    for n in sizes:
        # Generate two overlapping star-shaped polygons
        p1 = generate_star_shaped_polygon(n, Point2D(50, 50), 40)
        p2 = generate_star_shaped_polygon(n, Point2D(70, 70), 40)
        
        results = {}
        all_correct = True
        
        # Benchmark Union
        start = time.perf_counter()
        try:
            res = polygon_union(p1, p2)
            results['union'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "union"): all_correct = False
        except Exception:
            results['union'] = "Error"
            all_correct = False
            
        # Benchmark Intersection
        start = time.perf_counter()
        try:
            res = polygon_intersection(p1, p2)
            results['intersection'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "intersection"): all_correct = False
        except Exception:
            results['intersection'] = "Error"
            all_correct = False

        # Benchmark Difference
        start = time.perf_counter()
        try:
            res = polygon_difference(p1, p2)
            results['difference'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "difference"): all_correct = False
        except Exception:
            results['difference'] = "Error"
            all_correct = False

        # Benchmark XOR
        start = time.perf_counter()
        try:
            res = polygon_xor(p1, p2)
            results['xor'] = f"{time.perf_counter() - start:.4f}"
            if not verify_boolean_op(p1, p2, res, "xor"): all_correct = False
        except Exception:
            results['xor'] = "Error"
            all_correct = False

        print(f"{n:<12} | {results['union']:<18} | {results['intersection']:<18} | {results['difference']:<18} | {results['xor']:<18} | {str(all_correct)}")

if __name__ == "__main__":
    run_benchmarks()
