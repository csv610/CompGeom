
import random
import time
import sys
import os

# Add the src directory to sys.path to allow imports from compgeom
# Assuming the script is in src/compgeom/mesh/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from compgeom.geo_math.geometry import Point
from compgeom.mesh.delaunay_mesh_incremental import triangulate_incremental_fast
from compgeom.mesh.delaunay_triangulation import build_topology, is_delaunay

def run_perf_test(num_points):
    print(f"\n>>> Testing Incremental Delaunay with {num_points} random points")
    
    # Generate random points
    random.seed(42) # For reproducibility
    points = [Point(random.uniform(0, 10000), random.uniform(0, 10000), id=i) for i in range(num_points)]
    
    start_time = time.time()
    triangles, skipped = triangulate_incremental_fast(points)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"    Triangulation time: {duration:.4f} seconds")
    print(f"    Number of triangles: {len(triangles)}")
    if skipped:
        print(f"    Number of skipped points: {len(skipped)}")
        for p, reason in skipped[:5]:
            print(f"      - Point {p} skipped: {reason}")
        if len(skipped) > 5:
            print(f"      ... and {len(skipped) - 5} more")

    # Verification
    print("    Verifying Delaunay property...")
    v_start = time.time()
    mesh = build_topology(triangles)
    valid = is_delaunay(mesh)
    v_end = time.time()
    print(f"    Verification took: {v_end - v_start:.4f} seconds")
    print(f"    Delaunay Valid: {valid}")
    
    # Check if all points are included
    included_ids = {p.id for tri in triangles for p in tri}
    skipped_ids = {p.id for p, msg in skipped}
    missing = [p.id for p in points if p.id not in included_ids and p.id not in skipped_ids]
    
    if not missing:
        print("    All points accounted for.")
    else:
        print(f"    MISSING {len(missing)} points!")
        
    return valid and not missing

if __name__ == "__main__":
    results = []
    for n in [1000, 50000]:
        success = run_perf_test(n)
        results.append(success)
        
    if all(results):
        print("\nSUCCESS: All performance tests passed.")
    else:
        print("\nFAILURE: Some tests failed.")
