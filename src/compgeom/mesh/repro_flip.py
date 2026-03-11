
import random
from compgeom.kernel import Point
from compgeom.mesh.trimesh.delaunay_triangulation import build_topology, is_delaunay, DelaunayMesher

def test_full_triangulate_flip(num_points=50):
    print(f"\n--- Testing full triangulate with flip algorithm ({num_points} points) ---")
    points = [Point(random.uniform(0, 100), random.uniform(0, 100), id=i) for i in range(num_points)]
    
    mesh_obj = DelaunayMesher.triangulate(points, algorithm="flip")
    
    # Convert back to MeshTriangle list for is_delaunay
    tri_points = []
    for face in mesh_obj.faces:
        v1 = mesh_obj.vertices[face[0]]
        v2 = mesh_obj.vertices[face[1]]
        v3 = mesh_obj.vertices[face[2]]
        tri_points.append((v1, v2, v3))
    
    mesh = build_topology(tri_points)
    is_valid = is_delaunay(mesh)
    print(f"Resulting mesh Delaunay: {is_valid}")
    
    if not is_valid:
        print("BAD TRIANGLES FOUND")

def test_full_triangulate_dc(num_points=50):
    print(f"\n--- Testing full triangulate with divide and conquer algorithm ({num_points} points) ---")
    points = [Point(random.uniform(0, 100), random.uniform(0, 100), id=i) for i in range(num_points)]
    
    mesh_obj = DelaunayMesher.triangulate(points, algorithm="divide_and_conquer")
    
    # Convert back to MeshTriangle list for is_delaunay
    tri_points = []
    for face in mesh_obj.faces:
        v1 = mesh_obj.vertices[face[0]]
        v2 = mesh_obj.vertices[face[1]]
        v3 = mesh_obj.vertices[face[2]]
        tri_points.append((v1, v2, v3))
    
    mesh = build_topology(tri_points)
    is_valid = is_delaunay(mesh)
    print(f"Resulting mesh Delaunay: {is_valid}")
    
    if not is_valid:
        print("BAD TRIANGLES FOUND")

if __name__ == "__main__":
    test_full_triangulate_flip(10)
    test_full_triangulate_flip(100)
    test_full_triangulate_dc(10)
    test_full_triangulate_dc(100)
