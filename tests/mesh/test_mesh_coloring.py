
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriMesh, TetMesh
from compgeom.mesh.algorithms.mesh_coloring import MeshColoring

@pytest.fixture
def tri_mesh():
    # Two triangles sharing edge (1,2)
    v = [Point2D(0,0,0), Point2D(1,0,1), Point2D(0,1,2), Point2D(1,1,3)]
    f = [(0,1,2), (1,3,2)]
    return TriMesh(v, f)

def test_color_elements_surface(tri_mesh):
    coloring = MeshColoring.color_elements(tri_mesh)
    assert len(coloring) == 2
    # Neighbors 0 and 1 must have different colors
    assert coloring[0] != coloring[1]

def test_color_vertices_surface(tri_mesh):
    coloring = MeshColoring.color_vertices(tri_mesh)
    assert len(coloring) == 4
    # Vertices 1 and 2 share an edge, must be different
    assert coloring[1] != coloring[2]
    # Vertex 0 and 1 share an edge, must be different
    assert coloring[0] != coloring[1]

def test_color_elements_volume():
    # Two tetrahedra sharing a face
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1), Point3D(0,0,-1)]
    # Tet 0: (0,1,2,3), Tet 1: (0,1,2,4). Shared face (0,1,2).
    cells = [(0,1,2,3), (0,1,2,4)]
    mesh = TetMesh(v, cells)
    
    coloring = MeshColoring.color_elements(mesh)
    assert len(coloring) == 2
    assert coloring[0] != coloring[1]
