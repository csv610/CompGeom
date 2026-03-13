import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point
from compgeom.algo.point_trees import build_kdtree, range_search, PointQuadtree

def naive_range_search(points, min_x, max_x, min_y, max_y):
    return [p for p in points if min_x <= p.x <= max_x and min_y <= p.y <= max_y]

def run_benchmarks():
    sizes = [10**2, 10**3, 10**4, 10**5, 10**6]
    
    print("KD-Tree and Quadtree Scalability Analysis")
    print("=" * 110)
    print(f"{'N Points':<12} | {'KD-Tree Build':<14} | {'KD-Range Search':<16} | {'Naive Search':<14} | {'Quadtree Build':<14}")
    print("-" * 110)
    
    for n in sizes:
        # Generate random 2D points in [0, 1000]
        points = [
            Point(random.uniform(0, 1000), random.uniform(0, 1000), id=i) 
            for i in range(n)
        ]
        
        # Benchmark KD-Tree Construction
        start = time.perf_counter()
        root = build_kdtree(points)
        kd_build_time = time.perf_counter() - start
        
        # Benchmark Range Search (average of 100 queries)
        num_queries = 100
        
        # KD-Tree Range Search
        query_start = time.perf_counter()
        for _ in range(num_queries):
            x = random.uniform(0, 900)
            y = random.uniform(0, 900)
            range_search(root, x, x + 100, y, y + 100)
        kd_query_time = (time.perf_counter() - query_start) / num_queries
        
        # Naive Range Search (only for N <= 10^5 to avoid too long wait)
        if n <= 10**5:
            query_start = time.perf_counter()
            for _ in range(num_queries):
                x = random.uniform(0, 900)
                y = random.uniform(0, 900)
                naive_range_search(points, x, x + 100, y, y + 100)
            naive_query_time = (time.perf_counter() - query_start) / num_queries
        else:
            naive_query_time = float('nan')
            
        # Benchmark Quadtree Construction (Insertion)
        start = time.perf_counter()
        qt = PointQuadtree()
        for p in points:
            qt.insert(p)
        qt_build_time = time.perf_counter() - start
        
        print(f"{n:<12} | {kd_build_time:<14.4f} | {kd_query_time:<16.6f} | {naive_query_time:<14.6f} | {qt_build_time:<14.4f}")

if __name__ == "__main__":
    run_benchmarks()
