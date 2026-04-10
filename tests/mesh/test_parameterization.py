
import pytest
import math
from compgeom.kernel import Point3D, Point2D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.parameterization import MeshParameterization
from compgeom.mesh.surface.parameterization_bff import BFFParameterizer

@pytest.fixture
def simple_disk():
    # A single square patch triangulated (2 triangles)
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    return TriMesh(verts, faces)

def test_bff_initialization(simple_disk):
    bff = BFFParameterizer(simple_disk)
    assert bff.num_v == 4
    assert bff.L is not None

def test_harmonic_map_quad():
    # Simple open surface: a quad split into two triangles
    v = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0.5, 0.5, 0.5) # Center point, interior
    ]
    f = [
        (0,1,4), (1,2,4), (2,3,4), (3,0,4)
    ]
    mesh = TriMesh(v, f)
    
    uv = MeshParameterization.harmonic_map(mesh)
    assert len(uv) == 5
    # Boundary vertices (0,1,2,3) should be on unit circle
    for i in range(4):
        dist = math.hypot(uv[i].x, uv[i].y)
        assert dist == pytest.approx(1.0)
        
    # Interior vertex (4) should be near the center (0,0) due to symmetry
    assert math.hypot(uv[4].x, uv[4].y) < 1e-7

def test_harmonic_map_closed_fails():
    # A tetrahedron is a closed mesh
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    f = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
    mesh = TriMesh(v, f)
    
    with pytest.raises(ValueError, match="Mesh must have at least one open boundary"):
        MeshParameterization.harmonic_map(mesh)

def test_lscm_placeholder():
    # Simple placeholder test
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)]
    f = [(0,1,2)]
    mesh = TriMesh(v, f)
    uv = MeshParameterization.lscm(mesh)
    assert len(uv) == 3
    assert all(p.x == 0 and p.y == 0 for p in uv)
