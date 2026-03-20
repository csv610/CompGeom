
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriMesh, PolygonMesh, TetMesh, HexMesh
from compgeom.mesh.mesh_topology import MeshTopology, mesh_neighbors, get_mesh_edges

@pytest.fixture
def simple_tri_mesh():
    # Two triangles sharing an edge (1,2)
    # T0: (0,1,2), T1: (1,3,2)
    vertices = [Point2D(0,0, id=0), Point2D(1,0, id=1), Point2D(0,1, id=2), Point2D(1,1, id=3)]
    faces = [(0,1,2), (1,3,2)]
    return TriMesh(vertices, faces)

def test_mesh_neighbors_util():
    p1, p2, p3, p4 = Point2D(0,0), Point2D(1,0), Point2D(0,1), Point2D(1,1)
    triangles = [(p1, p2, p3), (p2, p4, p3)]
    res = mesh_neighbors(triangles)
    assert len(res["vertex_neighbors"]) == 4
    assert len(res["triangle_neighbors"]) == 2
    # Triangle 0 neighbors triangle 1
    assert 1 in res["triangle_neighbors"][0]

def test_get_mesh_edges():
    p1 = Point2D(0,0, id=0)
    p2 = Point2D(1,0, id=1)
    p3 = Point2D(0,1, id=2)
    edges = get_mesh_edges([(p1, p2, p3)])
    assert len(edges) == 3
    assert (0, 1) in edges

def test_topology_v2v(simple_tri_mesh):
    topo = MeshTopology(simple_tri_mesh)
    # Vertex 1 is connected to 0, 2, 3
    neighbors = topo.vertex_neighbors(1)
    assert neighbors == {0, 2, 3}

def test_topology_v2e(simple_tri_mesh):
    topo = MeshTopology(simple_tri_mesh)
    # Vertex 1 is in both faces
    elements = topo.vertex_elements(1)
    assert elements == {0, 1}
    # Vertex 0 is only in face 0
    assert topo.vertex_elements(0) == {0}

def test_topology_e2e(simple_tri_mesh):
    topo = MeshTopology(simple_tri_mesh)
    # Both triangles share vertices 1 and 2
    assert topo.element_neighbors(0) == {1}
    assert topo.shared_edge_neighbors(0) == {1}

def test_watertight_and_boundary(simple_tri_mesh):
    topo = MeshTopology(simple_tri_mesh)
    assert topo.is_watertight() is False
    # Boundary edges: (0,1), (0,2), (1,3), (2,3)
    b_edges = topo.boundary_edges()
    assert len(b_edges) == 4

def test_orientable():
    # Simple orientable mesh
    v = [Point2D(0,0), Point2D(1,0), Point2D(0,1)]
    m1 = TriMesh(v, [(0,1,2)])
    assert MeshTopology(m1).is_orientable() is True
    
    # Non-orientable: edge (0,1) shared by 2 faces with same orientation
    m2 = TriMesh(v, [(0,1,2), (0,1,2)]) 
    assert MeshTopology(m2).is_orientable() is False

def test_volume_topology():
    # Single tetrahedron
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    cells = [(0,1,2,3)]
    mesh = TetMesh(v, cells)
    topo = MeshTopology(mesh)
    
    assert len(topo.get_edges()) == 6
    assert len(topo.boundary_faces()) == 4
    # A single cell has boundary faces, so it is NOT watertight in terms of being "closed"
    assert topo.is_watertight() is False
    
def test_hexahedron_edges():
    # Standard unit cube
    v = [Point3D(x,y,z) for z in [0,1] for y in [0,1] for x in [0,1]]
    mesh = HexMesh(v, [tuple(range(8))])
    topo = MeshTopology(mesh)
    assert len(topo.get_edges()) == 12
