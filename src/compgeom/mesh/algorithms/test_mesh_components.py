
from compgeom.mesh import TriMesh
from compgeom.kernel import Point3D
from mesh_components import MeshComponents

def test_mesh_components():
    print("Testing Mesh Components...")
    # Two separate triangles
    v = [
        Point3D(0.0, 0.0, 0.0), Point3D(1.0, 0.0, 0.0), Point3D(0.5, 1.0, 0.0),
        Point3D(2.0, 0.0, 0.0), Point3D(3.0, 0.0, 0.0), Point3D(2.5, 1.0, 0.0)
    ]
    f = [(0, 1, 2), (3, 4, 5)]
    mesh = TriMesh(v, f)
    
    v_comp = MeshComponents.identify_vertex_components(mesh)
    f_comp = MeshComponents.identify_face_components(mesh)
    stats = MeshComponents.get_component_statistics(mesh)
    
    print(f"Vertex components (2 separate triangles): {v_comp}")
    print(f"Face components (2 separate triangles): {f_comp}")
    print(f"Stats: {stats}")
    
    assert len(v_comp) == 2
    assert len(f_comp) == 2
    assert stats["num_vertex_components"] == 2
    assert stats["num_face_components"] == 2
    
    # Connected triangles (sharing an edge)
    v2 = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(1, 1, 0)
    ]
    f2 = [(0, 1, 2), (1, 3, 2)] # Shared edge (1, 2)
    mesh2 = TriMesh(v2, f2)
    
    v_comp2 = MeshComponents.identify_vertex_components(mesh2)
    f_comp2 = MeshComponents.identify_face_components(mesh2)
    stats2 = MeshComponents.get_component_statistics(mesh2)
    
    print(f"\nVertex components (connected): {v_comp2}")
    print(f"Face components (connected): {f_comp2}")
    print(f"Stats: {stats2}")
    
    assert len(v_comp2) == 1
    assert len(f_comp2) == 1
    assert stats2["num_vertex_components"] == 1
    assert stats2["num_face_components"] == 1

    # Vertices sharing a point but no edges (though usually vertex_neighbors would connect them)
    # If two faces share ONLY one vertex, face components should be 2, but vertex component should be 1.
    v3 = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0),
        Point3D(-1, 0, 0), Point3D(0, -1, 0)
    ]
    f3 = [(0, 1, 2), (0, 3, 4)] # Shared vertex 0
    mesh3 = TriMesh(v3, f3)
    
    v_comp3 = MeshComponents.identify_vertex_components(mesh3)
    f_comp3 = MeshComponents.identify_face_components(mesh3)
    
    print(f"\nVertex components (shared vertex only): {v_comp3}")
    print(f"Face components (shared vertex only): {f_comp3}")
    
    assert len(v_comp3) == 1
    assert len(f_comp3) == 2 # They don't share an edge

if __name__ == "__main__":
    try:
        test_mesh_components()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
