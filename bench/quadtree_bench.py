import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point
from compgeom.algo.point_trees import PointQuadtree, QuadNode

def quadtree_range_search(node: QuadNode | None, min_x, max_x, min_y, max_y):
    if node is None:
        return []
    
    result = []
    if min_x <= node.point.x <= max_x and min_y <= node.point.y <= max_y:
        result.append(node.point)
    
    # Check quadrants
    # This is a naive traversal that checks all children. 
    # A better implementation would check if the quadrant overlaps with the query box.
    # However, since PointQuadtree doesn't store bounding boxes in nodes, 
    # we use the point itself to prune.
    
    # NE: x >= px, y >= py
    if max_x >= node.point.x and max_y >= node.point.y:
        result.extend(quadtree_range_search(node.ne, min_x, max_x, min_y, max_y))
    # NW: x < px, y >= py
    if min_x < node.point.x and max_y >= node.point.y:
        result.extend(quadtree_range_search(node.nw, min_x, max_x, min_y, max_y))
    # SE: x >= px, y < py
    if max_x >= node.point.x and min_y < node.point.y:
        result.extend(quadtree_range_search(node.se, min_x, max_x, min_y, max_y))
    # SW: x < px, y < py
    if min_x < node.point.x and min_y < node.point.y:
        result.extend(quadtree_range_search(node.sw, min_x, max_x, min_y, max_y))
        
    return result

def run_benchmarks():
    sizes = [10**2, 10**3, 10**4, 10**5]
    
    print("Point Quadtree Scalability Analysis")
    print("=" * 80)
    print(f"{'N Points':<12} | {'Build Time (s)':<18} | {'Range Search (s)':<18}")
    print("-" * 80)
    
    for n in sizes:
        points = [
            Point(random.uniform(0, 1000), random.uniform(0, 1000), id=i) 
            for i in range(n)
        ]
        
        # Benchmark Construction
        start = time.perf_counter()
        qt = PointQuadtree()
        for p in points:
            qt.insert(p)
        build_time = time.perf_counter() - start
        
        # Benchmark Range Search
        num_queries = 100
        query_start = time.perf_counter()
        for _ in range(num_queries):
            x = random.uniform(0, 900)
            y = random.uniform(0, 900)
            quadtree_range_search(qt.root, x, x + 100, y, y + 100)
        query_time = (time.perf_counter() - query_start) / num_queries
        
        print(f"{n:<12} | {build_time:<18.4f} | {query_time:<18.6f}")

if __name__ == "__main__":
    run_benchmarks()
