import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.geo_math.geometry import Point
from compgeom.mesh.delaunay_triangulation import DelaunayMesher

def run_benchmarks():
    # Note: 10^7+ points usually require significant RAM and time in Python.
    # 10^10 is technically impossible on a single machine's RAM.
    sizes = [10**2, 10**3, 10**4, 10**5, 10**6]
    
    print("Delaunay Triangulation Scalability Analysis")
    print("=" * 60)
    print(f"{'N Points':<12} | {'Incremental (s)':<18} | {'Divide & Conquer (s)':<22}")
    print("-" * 60)
    
    for n in sizes:
        # Generate random 2D points
        points = [
            Point(random.uniform(0, 10000), random.uniform(0, 10000), id=i) 
            for i in range(n)
        ]
        
        results = {}
        
        # Benchmark Divide and Conquer (usually faster, so we do it first)
        start = time.perf_counter()
        try:
            DelaunayMesher.triangulate(points, algorithm="divide_and_conquer")
            results['dc'] = f"{time.perf_counter() - start:.4f}"
        except Exception as e:
            results['dc'] = f"Error: {e}"
            
        # Benchmark Incremental (Bowyer-Watson)
        # We skip incremental for very large N as it is O(N^2) in worst case (though often O(N log N) on average)
        if n <= 10**4: # Reduced limit for incremental to keep benchmark reasonable
            start = time.perf_counter()
            try:
                DelaunayMesher.triangulate(points, algorithm="incremental")
                results['inc'] = f"{time.perf_counter() - start:.4f}"
            except Exception as e:
                results['inc'] = f"Error: {e}"
        else:
            results['inc'] = "Skipped (>10^4)"

        print(f"{n:<12} | {results['inc']:<18} | {results['dc']:<22}")

if __name__ == "__main__":
    run_benchmarks()
