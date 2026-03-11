import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.geo_math.geometry import Point
from compgeom.mesh.delaunay_triangulation import DelaunayMesher

def run_benchmarks():
    # 10^7 points usually require significant RAM and time in Python.
    sizes = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7]
    
    print("Delaunay Triangulation Scalability Analysis")
    print("=" * 100)
    print(f"{'N Points':<12} | {'Incremental (s)':<18} | {'Divide & Conquer (s)':<22} | {'Delaunay Flip* (s)':<22}")
    print("-" * 100)
    
    for n in sizes:
        # Generate random 2D points
        points = [
            Point(random.uniform(0, 10000), random.uniform(0, 10000), id=i) 
            for i in range(n)
        ]
        
        results = {}
        
        # Benchmark Divide and Conquer
        start = time.perf_counter()
        try:
            mesh = DelaunayMesher.triangulate(points, algorithm="divide_and_conquer")
            results['dc'] = f"{time.perf_counter() - start:.4f}"
        except Exception as e:
            results['dc'] = f"Error"
            
        # Benchmark Incremental (Bowyer-Watson)
        # Note: This is O(N^2) in this implementation and will be very slow for large N.
        start = time.perf_counter()
        try:
            mesh = DelaunayMesher.triangulate(points, algorithm="incremental")
            results['inc'] = f"{time.perf_counter() - start:.4f}"
        except Exception as e:
            results['inc'] = f"Error"

        
        """

        # Benchmark Delaunay Flip (Topology Build + Flip)
        # *Note: This benchmarks building topology and verifying/flipping an existing Delaunay mesh.
        start = time.perf_counter()
        try:
           mesh = DelaunayMesher.triangulate(points, algorithm="flip")
           results['flip'] = f"{time.perf_counter() - start:.4f}"
        except Exception as e:
           results['flip'] = f"Error"
        print(f"{n:<12} | {results['inc']:<18} | {results['dc']:<22} | {results['flip']:<22}")
        """
        print(f"{n:<12} | {results['inc']:<18} | {results['dc']:<22}")


if __name__ == "__main__":
    run_benchmarks()
