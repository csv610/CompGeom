
import random
import time
from compgeom.geo_math.geometry import Point
from compgeom.mesh.delaunay_mesh_incremental import triangulate_incremental_fast
from compgeom.mesh.delaunay_triangulation import build_topology, is_delaunay

def run_test(num_points=100):
    print(f"\n--- Testing with {num_points} points ---")
    points = [Point(random.uniform(0, 1000), random.uniform(0, 1000), id=i) for i in range(num_points)]
    
    start_time = time.time()
    triangles, skipped = triangulate_incremental_fast(points)
    end_time = time.time()
    
    print(f"Triangulation took: {end_time - start_time:.4f} seconds")
    print(f"Generated {len(triangles)} triangles.")
    if skipped:
        print(f"Skipped {len(skipped)} points.")

    # Verify Delaunay property
    mesh = build_topology(triangles)
    is_valid = is_delaunay(mesh)
    print(f"Delaunay Property Valid: {is_valid}")
    
    # Verify all points are present
    included_ids = {p.id for tri in triangles for p in tri}
    skipped_ids = {p.id for p, msg in skipped}
    missing = [p.id for p in points if p.id not in included_ids and p.id not in skipped_ids]
    
    if not missing:
        print("All points are accounted for.")
    else:
        print(f"Missing points: {missing}")
    
    return is_valid and not missing

if __name__ == "__main__":
    # Test small set
    s1 = run_test(10)
    # Test medium set
    s2 = run_test(100)
    # Test large set for performance
    s3 = run_test(1000)
    
    if all([s1, s2, s3]):
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")
