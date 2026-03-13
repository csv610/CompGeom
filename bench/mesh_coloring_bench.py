import time
import random
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.kernel import Point2D
from compgeom.mesh.delaunay_triangulation import DelaunayMesher
from compgeom.mesh.voronoi_diagram import VoronoiDiagram
from compgeom.mesh.mesh_coloring import MeshColoring

def run_benchmarks():
    # sizes from 10^2 to 10^4
    sizes = [100, 500, 1000, 2500, 5000, 10000]

    print("Mesh Coloring (Greedy Algorithm) Scalability Analysis")
    print("=" * 110)
    header = f"{'N Points':<10} | {'Mesh Type':<15} | {'Target':<10} | {'Elements/Vertices':<20} | {'Time (s)':<15} | {'Colors':<8}"
    print(header)
    print("-" * 110)

    for n in sizes:
        # Generate random 2D points within a range
        points = [
            Point2D(random.uniform(0, 10000), random.uniform(0, 10000), id=i) 
            for i in range(n)
        ]

        # 1. Triangle Mesh (Delaunay)
        try:
            # Using 'incremental' for better reliability in benchmark
            mesh = DelaunayMesher.triangulate(points, algorithm="incremental")
            
            # Element Coloring
            start = time.perf_counter()
            coloring = MeshColoring.color_elements(mesh)
            elapsed = time.perf_counter() - start
            n_colors = len(set(coloring.values()))
            print(f"{n:<10} | {'Triangle':<15} | {'Elements':<10} | {len(mesh.elements):<20} | {elapsed:<15.4f} | {n_colors:<8}")

            # Vertex Coloring
            start = time.perf_counter()
            coloring = MeshColoring.color_vertices(mesh)
            elapsed = time.perf_counter() - start
            n_colors = len(set(coloring.values()))
            print(f"{n:<10} | {'Triangle':<15} | {'Vertices':<10} | {len(mesh.vertices):<20} | {elapsed:<15.4f} | {n_colors:<8}")
        except Exception as e:
            print(f"{n:<10} | {'Triangle':<15} | Error: {e}")

        # 2. Voronoi Diagram
        try:
            vd = VoronoiDiagram()
            # VoronoiDiagram.compute returns a PolygonMesh
            mesh = vd.compute(points, boundary_type="square")
            
            # Element Coloring
            start = time.perf_counter()
            coloring = MeshColoring.color_elements(mesh)
            elapsed = time.perf_counter() - start
            n_colors = len(set(coloring.values()))
            print(f"{n:<10} | {'Voronoi':<15} | {'Elements':<10} | {len(mesh.elements):<20} | {elapsed:<15.4f} | {n_colors:<8}")

            # Vertex Coloring
            start = time.perf_counter()
            coloring = MeshColoring.color_vertices(mesh)
            elapsed = time.perf_counter() - start
            n_colors = len(set(coloring.values()))
            print(f"{n:<10} | {'Voronoi':<15} | {'Vertices':<10} | {len(mesh.vertices):<20} | {elapsed:<15.4f} | {n_colors:<8}")
        except Exception as e:
            print(f"{n:<10} | {'Voronoi':<15} | Error: {e}")
        
        print("-" * 110)
    return 0

def main():
    return run_benchmarks()

if __name__ == "__main__":
    sys.exit(main())
