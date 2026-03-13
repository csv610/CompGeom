import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point2D
from compgeom.mesh.voronoi_diagram import VoronoiDiagram
from compgeom.graphics.geo_plot import GeomPlot

def run_benchmarks():
    # sizes from 10^1 to 10^5
    sizes = [10, 100, 1000, 10000, 100000]

    print("Voronoi Diagram Scalability Analysis (Clipping Algorithm)")
    print("WARNING: This algorithm is O(N^2). N=100,000 may take a very long time in Python.")
    print("=" * 60)
    print(f"{'N Points':<12} | {'Time (s)':<18} | {'Avg Time/Point (ms)':<22}")
    print("-" * 60)

    for n in sizes:
        # Generate random 2D points within a range
        points = [
            Point2D(random.uniform(1, 100000), random.uniform(100, 100000), id=i) 
            for i in range(n)
        ]

        vd = VoronoiDiagram()

        start = time.perf_counter()
        try:
            # For N=100,000, we might want to alert the user it's starting
            if n >= 10000:
                print(f"Starting N={n}... (this will take a while)")

            vd.compute(points, boundary_type="square")
            elapsed = time.perf_counter() - start

            # Save a plot for N=100
            if n == 100:
                svg_data = GeomPlot.get_image(vd, format="svg")
                with open("voronoi_100.svg", "w") as f:
                    f.write(svg_data)
                png_data = GeomPlot.get_image(vd, format="png")
                with open("voronoi_100.png", "wb") as f:
                    f.write(png_data)
                print(f"Saved voronoi_100.svg and voronoi_100.png")

            avg_ms = (elapsed / n) * 1000
            print(f"{n:<12} | {elapsed:<18.4f} | {avg_ms:<22.4f}")
        except KeyboardInterrupt:
            print(f"\nBenchmark interrupted at N={n}")
            break
        except Exception as e:
            print(f"{n:<12} | Error: {e}")

if __name__ == "__main__":
    run_benchmarks()
