import pytest
from compgeom.kernel import Point, Point3D
from compgeom.mesh.mesh import TriangleMesh, QuadMesh, PolygonMesh, MeshTopology

def test_triangle_mesh_basic():
    vertices = [Point(0, 0, id=0), Point(1, 0, id=1), Point(0, 1, id=2), Point(1, 1, id=3)]
    faces = [(0, 1, 2), (1, 3, 2)]
    mesh = TriangleMesh(vertices, faces)
    assert len(mesh.vertices) == 4
    assert len(mesh.faces) == 2
    assert mesh.euler_characteristic() == 1 # V=4, E=5, F=2 -> 4-5+2 = 1
    assert mesh.is_watertight() is False
    assert len(mesh.topology.boundary_edges()) == 4

def test_mesh_centroid_and_bbox():
    vertices = [Point(0, 0), Point(2, 0), Point(1, 2)]
    mesh = TriangleMesh(vertices, [(0, 1, 2)])
    centroid = mesh.centroid
    assert centroid.x == pytest.approx(1.0)
    assert centroid.y == pytest.approx(2/3)
    
    bbox = mesh.bounding_box()
    assert bbox == ((0.0, 0.0), (2.0, 2.0))

def test_mesh_topology_neighbors():
    vertices = [Point(0, 0, id=0), Point(1, 0, id=1), Point(0, 1, id=2), Point(1, 1, id=3)]
    faces = [(0, 1, 2), (1, 3, 2)]
    mesh = TriangleMesh(vertices, faces)
    topo = mesh.topology
    assert topo.vertex_neighbors(0) == {1, 2}
    assert topo.vertex_elements(1) == {0, 1}
    assert topo.element_neighbors(0) == {1}
    assert topo.shared_edge_neighbors(0) == {1}

def test_quad_mesh_extract_chord():
    # 2x1 grid of quads
    # 0 -- 1 -- 2
    # | Q0 | Q1 |
    # 3 -- 4 -- 5
    vertices = [Point(0,1), Point(1,1), Point(2,1), Point(0,0), Point(1,0), Point(2,0)]
    faces = [(0, 3, 4, 1), (1, 4, 5, 2)]
    mesh = QuadMesh(vertices, faces)
    # Edge index 1 of Q0 is (3,4) - vertical? No, (0,3,4,1) edges are (0,3), (3,4), (4,1), (1,0)
    # Let's check edge index 2 of Q0: (4,1). Neighbor Q1 has edge (1,4).
    chord = mesh.extract_chord(0, 2)
    assert chord == [0, 1]

def test_polygon_mesh_triangulate():
    vertices = [Point(0,0), Point(1,0), Point(1,1), Point(0,1)]
    faces = [(0, 1, 2, 3)]
    mesh = PolygonMesh(vertices, faces)
    tri_mesh = mesh.triangulate()
    assert len(tri_mesh.faces) == 2
    assert tri_mesh.euler_characteristic() == 1

def test_mesh_reorder_nodes():
    vertices = [Point(0,0), Point(1,0), Point(0,1)]
    faces = [(0, 1, 2)]
    mesh = TriangleMesh(vertices, faces)
    mesh.reorder_nodes([2, 0, 1])
    assert mesh.vertices[0] == Point(0, 1)
    assert mesh.faces[0] == (1, 2, 0) # Old 0 is now 1, old 1 is now 2, old 2 is now 0

def test_triangle_mesh_3d():
    vertices = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    mesh = TriangleMesh(vertices, faces)
    assert mesh.is_watertight() is True
    assert mesh.euler_characteristic() == 2 # Tetrahedron V=4, E=6, F=4 -> 4-6+4=2

def test_ensure_even_elements():
    vertices = [Point(0,0), Point(1,0), Point(0,1)]
    mesh = TriangleMesh(vertices, [(0, 1, 2)])
    assert len(mesh.faces) == 1
    even_mesh = mesh.ensure_even_elements()
    assert len(even_mesh.faces) % 2 == 0
