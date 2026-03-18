import time
import random
import math
import sys
import os

# Ensure local imports work if run as a script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.voronoi_3d import VoronoiDiagram3D
from compgeom.mesh.volmesh.bounded_voronoi_3d import BoundedVoronoi3D

def generate_random_points(n, size=100.0):
    return [Point3D(random.uniform(0, size), 
                    random.uniform(0, size), 
                    random.uniform(0, size)) for _ in range(n)]

def benchmark_voronoi_3d(n_points_list):
    print(f"{'Points':<10} | {'Unbounded (s)':<15} | {'Bounded Box (s)':<15}")
    print("-" * 45)
    
    for n in n_points_list:
        points = generate_random_points(n)
        
        # Benchmark Unbounded
        start = time.perf_counter()
        voronoi = VoronoiDiagram3D()
        voronoi.compute(points)
        unbounded_time = time.perf_counter() - start
        
        # Benchmark Bounded (Box)
        # Bounded is O(N) with Delaunay neighbors, but clipping many small polygons is still slower than pure Delaunay.
        start = time.perf_counter()
        bv = BoundedVoronoi3D.from_box(Point3D(0, 0, 0), Point3D(100, 100, 100))
        bv.compute(points)
        bounded_time = time.perf_counter() - start
        
        print(f"{n:<10} | {unbounded_time:<15.4f} | {bounded_time:<15.4f}")


if __name__ == "__main__":
    random.seed(42)
    # 10, 10^2, 10^3, 10^4, 10^5
    n_list = [10, 100, 1000, 10000, 100000]
    print("Benchmarking 3D Voronoi Implementation...")
    benchmark_voronoi_3d(n_list)
