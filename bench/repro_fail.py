import sys
import os
import time

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from compgeom.kernel import Point2D
from compgeom.polygon.polygon_generator import generate_star_shaped_polygon
from compgeom.polygon.polygon_boolean import (
    polygon_union, 
    polygon_intersection, 
    polygon_difference, 
    polygon_xor, 
    verify_boolean_op
)

def debug_bench():
    n = 500
    p1 = generate_star_shaped_polygon(n, Point2D(50, 50), 40)
    p2 = generate_star_shaped_polygon(n, Point2D(70, 70), 40)
    
    ops = ["union", "intersection", "difference", "xor"]
    funcs = [polygon_union, polygon_intersection, polygon_difference, polygon_xor]
    
    for op, func in zip(ops, funcs):
        start = time.perf_counter()
        res = func(p1, p2)
        elapsed = time.perf_counter() - start
        correct = verify_boolean_op(p1, p2, res, op)
        
        area_a = p1.area
        area_b = p2.area
        area_res = sum(p.area for p in res)
        
        print(f"Op: {op:<12} | Time: {elapsed:.4f}s | Correct: {correct:<5} | Area A: {area_a:.4f} | Area B: {area_b:.4f} | Area Res: {area_res:.4f} | N Polys: {len(res)}")
        for i, p in enumerate(res):
            print(f"  Poly {i}: Area {p.area:.4f}, Vertices {len(p)}")
        
        if not correct:
            if op == "union":
                 print(f"  FAILED: {area_res:.4f} > {area_a + area_b:.4f}")
            elif op == "intersection":
                 print(f"  FAILED: {area_res:.4f} > {min(area_a, area_b):.4f}")
            elif op == "difference":
                 print(f"  FAILED: {area_res:.4f} > {area_a:.4f}")
            elif op == "xor":
                 print(f"  FAILED: {area_res:.4f} > {area_a + area_b:.4f}")

if __name__ == "__main__":
    debug_bench()
