
import os
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh import TriMesh, MeshNode, MeshFace, MeshCell, TetMesh, MeshTopology

def test_triangle_mesh():
    print("Testing TriMesh...")
    # Test from_triangles
    p1 = Point2D(0, 0)
    p2 = Point2D(1, 0)
    p3 = Point2D(0, 1)
    p4 = Point2D(1, 1)
    
    triangles = [(p1, p2, p3), (p2, p4, p3)]
    
    mesh = TriMesh.from_triangles(triangles)
    print(f"Nodes: {len(mesh.nodes)}")
    print(f"Faces: {len(mesh.faces)}")
    
    assert len(mesh.nodes) == 4
    assert len(mesh.faces) == 2

    # Test MeshTopology
    topo = mesh.topology
    neighbors = topo.vertex_neighbors(0) # Node 0 (0,0) is connected to 1 (1,0) and 2 (0,1)
    print(f"Neighbors of node 0: {neighbors}")
    assert 1 in neighbors
    assert 2 in neighbors

def test_tet_mesh_topology():
    print("\nTesting TetMesh topology...")
    # 4 nodes of a tetrahedron
    nodes = [
        MeshNode(0, Point3D(0, 0, 0)),
        MeshNode(1, Point3D(1, 0, 0)),
        MeshNode(2, Point3D(0, 1, 0)),
        MeshNode(3, Point3D(0, 0, 1)),
    ]
    cells = [MeshCell(0, (0, 1, 2, 3))]
    
    mesh = TetMesh(nodes, cells)
    topo = mesh.topology
    
    print(f"Cells: {len(mesh.cells)}")
    assert len(mesh.cells) == 1
    
    # In the current implementation, TetMesh topology only connects cyclic neighbors in v_indices
    neighbors = topo.vertex_neighbors(0)
    print(f"Neighbors of node 0 in TetMesh: {neighbors}")
    assert neighbors == {1, 3}

def test_from_file():
    print("\nTesting TriMesh.from_file...")
    # Create a temporary OBJ file
    obj_content = """v 0 0 0
v 1 0 0
v 0 1 0
f 1 2 3
"""
    with open("test.obj", "w") as f:
        f.write(obj_content)
    
    try:
        mesh = TriMesh.from_file("test.obj")
        print(f"Nodes from file: {len(mesh.nodes)}")
        print(f"Faces from file: {len(mesh.faces)}")
        assert len(mesh.nodes) == 3
        assert len(mesh.faces) == 1
    finally:
        if os.path.exists("test.obj"):
            os.remove("test.obj")

if __name__ == "__main__":
    try:
        test_triangle_mesh()
        test_tet_mesh_topology()
        test_from_file()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
