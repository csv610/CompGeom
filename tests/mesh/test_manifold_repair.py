
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.manifold_repair import ManifoldValidator, ManifoldFixer

@pytest.fixture
def clean_mesh():
    # Two triangles sharing an edge (1,2) - manifold
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(1,1,0)]
    f = [(0,1,2), (1,3,2)]
    return TriMesh(v, f)

@pytest.fixture
def non_manifold_edge_mesh():
    # Three triangles sharing edge (0,1)
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,-1,0), Point3D(0,0,1)]
    f = [(0,1,2), (0,1,3), (0,1,4)]
    return TriMesh(v, f)

@pytest.fixture
def pinched_vertex_mesh():
    # Two cones meeting at a single vertex (0,0,0)
    # Cone 1 base: (1,0,1), (0,1,1), (-1,0,1)
    # Apex: (0,0,0)
    # Cone 2 base: (1,0,-1), (0,1,-1), (-1,0,-1)
    v = [
        Point3D(0,0,0), # 0: pinched apex
        Point3D(1,0,1), Point3D(0,1,1), Point3D(-1,0,1), # Cone 1
        Point3D(1,0,-1), Point3D(0,1,-1), Point3D(-1,0,-1) # Cone 2
    ]
    f = [
        (0,1,2), (0,2,3), (0,3,1), # Cone 1
        (0,4,5), (0,5,6), (0,6,4)  # Cone 2
    ]
    return TriMesh(v, f)

def test_validator_manifold(clean_mesh):
    val = ManifoldValidator(clean_mesh)
    assert val.find_non_manifold_edges() == []
    assert len(val.find_boundary_edges()) == 4
    assert val.find_non_manifold_vertices() == []

def test_validator_non_manifold_edge(non_manifold_edge_mesh):
    val = ManifoldValidator(non_manifold_edge_mesh)
    nm_edges = val.find_non_manifold_edges()
    assert len(nm_edges) == 1
    assert tuple(sorted(nm_edges[0])) == (0, 1)

def test_validator_pinched_vertex(pinched_vertex_mesh):
    val = ManifoldValidator(pinched_vertex_mesh)
    nm_vertices = val.find_non_manifold_vertices()
    assert nm_vertices == [0]

def test_fix_pinched_vertex(pinched_vertex_mesh):
    val_before = ManifoldValidator(pinched_vertex_mesh)
    assert val_before.find_non_manifold_vertices() == [0]
    
    fixed = ManifoldFixer.fix_non_manifold_vertices(pinched_vertex_mesh)
    assert len(fixed.vertices) == len(pinched_vertex_mesh.vertices) + 1
    
    val_after = ManifoldValidator(fixed)
    assert val_after.find_non_manifold_vertices() == []

def test_fix_already_manifold(clean_mesh):
    fixed = ManifoldFixer.fix_non_manifold_vertices(clean_mesh)
    assert fixed is clean_mesh

def test_resolve_branching_placeholder(non_manifold_edge_mesh):
    # This is a placeholder test for the method that does nothing yet
    fixed = ManifoldFixer.resolve_branching_edges(non_manifold_edge_mesh)
    assert fixed is non_manifold_edge_mesh
