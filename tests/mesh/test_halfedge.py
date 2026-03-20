
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.mesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh

@pytest.fixture
def simple_he_mesh():
    # Two triangles sharing edge (1,2)
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(1,1,0)]
    f = [(0,1,2), (1,3,2)]
    tm = TriMesh(v, f)
    return HalfEdgeMesh.from_triangle_mesh(tm)

def test_he_mesh_init(simple_he_mesh):
    assert len(simple_he_mesh.vertices) == 4
    assert len(simple_he_mesh.faces) == 2
    assert len(simple_he_mesh.edges) == 6
    
    # Check half-edge pointers
    he = simple_he_mesh.edges[0]
    assert he.next is not None
    assert he.next.next.next == he
    
    # Shared edge (1,2) should have a twin
    # Edge 1 from T0: (1,2). Edge 2 from T1: (2,1).
    he_1_2 = simple_he_mesh.get_half_edge(1, 2)
    assert he_1_2 is not None
    assert he_1_2.twin is not None
    assert he_1_2.twin.vertex.idx == 2

def test_he_mesh_to_trimesh(simple_he_mesh):
    tm = simple_he_mesh.to_triangle_mesh()
    assert len(tm.vertices) == 4
    assert len(tm.faces) == 2

def test_vertex_neighbors(simple_he_mesh):
    # Vertex 1 is connected to 0, 2, 3
    nbs = simple_he_mesh.vertex_neighbors(1)
    assert nbs == {0, 2, 3}
    
    # Vertex 0 is connected to 1, 2
    nbs0 = simple_he_mesh.vertex_neighbors(0)
    assert nbs0 == {1, 2}

def test_get_half_edge_invalid(simple_he_mesh):
    # (0,3) is not an edge
    assert simple_he_mesh.get_half_edge(0, 3) is None
    
    # (1,2) is an edge
    assert simple_he_mesh.get_half_edge(1, 2) is not None

def test_he_mesh_closed():
    # Tetrahedron
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    f = [(0,1,2), (0,2,3), (0,3,1), (1,3,2)]
    tm = TriMesh(v, f)
    he_mesh = HalfEdgeMesh.from_triangle_mesh(tm)
    
    # Every edge should have a twin
    for he in he_mesh.edges:
        assert he.twin is not None
    
    # Vertex 0 neighbors are 1, 2, 3
    assert he_mesh.vertex_neighbors(0) == {1, 2, 3}
