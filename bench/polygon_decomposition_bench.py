import time
import sys
import os

try:
    from compgeom.polygon.polygon import Polygon
    from compgeom.polygon.polygon_decomposer import PolygonDecomposer
    from compgeom.polygon.polygon_generator import PolygonGenerator
except ImportError as e:
    print(f"Error importing compgeom: {e}")
    sys.exit(1)

def run_benchmarks():
    sizes = [10, 50, 100, 200, 500]
    
    # Supported algorithms to benchmark (using the new interface)
    algorithm_names = [
        ("Triangulate", "triangulate"),
        ("Convex", "convex"),
        ("Monotone", "monotone"),
        ("Trapezoidal", "trapezoidal"),
        ("Visibility", "visibility"),
    ]

    print("Polygon Decomposition Algorithms Scalability and Area-Correctness Analysis")
    print("=" * 140)
    
    header = f"{'N Vertices':<12} | " + " | ".join(f"{name:<18}" for name, _ in algorithm_names) + " | Correct?"
    print(header)
    print("-" * 140)
    
    for n in sizes:
        # Generate a simple (concave) polygon
        vertices = PolygonGenerator.concave(n, (0, 1000), (0, 1000))
        
        results = []
        all_correct = True
        
        for name, algo_name in algorithm_names:
            start = time.perf_counter()
            try:
                # Use the class as a function or use .decompose()
                # Testing the "PolygonDecomposer function" request by calling it directly
                mesh = PolygonDecomposer(vertices, algo_name)
                duration = time.perf_counter() - start
                
                results.append(f"{duration:.4f}")
                
                if not PolygonDecomposer.verify(vertices, mesh):
                    all_correct = False
            except Exception as e:
                # print(f"Error in {name} for size {n}: {e}")
                results.append("Error")
                all_correct = False
        
        row = f"{n:<12} | " + " | ".join(f"{res:<18}" for res in results) + f" | {all_correct}"
        print(row)

if __name__ == "__main__":
    run_benchmarks()
