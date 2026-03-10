import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.geo_math.geometry import Point
from compgeom.mesh.triangulation import VoronoiDiagram

def run_benchmarks():
    # sizes from 10^1 to 10^5
    sizes = [10, 100, 1000, 10000, 100000]
    
    print("Voronoi Diagram Scalability Analysis (Clipping Algorithm)")
    print("WARNING: This algorithm is O(N^2). N=100,000 may take a very long time in Python.")
    print("=" * 60)
    print(f"{'N Points':<12} | {'Time (s)':<18} | {'Avg Time/Point (ms)':<22}")
    print("-" * 60)
    
    # Square boundary for all tests
    boundary = VoronoiDiagram.get_square_boundary(size=100000, center=(50000, 50000))
    
    for n in sizes:
        # Generate random 2D points within the boundary
        points = [
            Point(random.uniform(1000, 99000), random.uniform(1000, 99000), id=i) 
            for i in range(n)
        ]
        
        vd = VoronoiDiagram(points, boundary)
        
        start = time.perf_counter()
        try:
            # For N=100,000, we might want to alert the user it's starting
            if n >= 10000:
                print(f"Starting N={n}... (this will take a while)")
            
            vd.compute()
            elapsed = time.perf_counter() - start
            avg_ms = (elapsed / n) * 1000
            print(f"{n:<12} | {elapsed:<18.4f} | {avg_ms:<22.4f}")
        except KeyboardInterrupt:
            print(f"\nBenchmark interrupted at N={n}")
            break
        except Exception as e:
            print(f"{n:<12} | Error: {e}")

if __name__ == "__main__":
    run_benchmarks()
