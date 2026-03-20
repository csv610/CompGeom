
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.mesh_clipper import MeshClipper

@pytest.fixture
def tri_cube():
    # Unit cube split into triangles
    v = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
    ]
    f = [
        (0,1,2), (0,2,3), # bottom (z=0)
        (4,6,5), (4,7,6), # top (z=1)
        (0,4,5), (0,5,1), # front
        (1,5,6), (1,6,2), # right
        (2,6,7), (2,7,3), # back
        (3,7,4), (3,4,0)  # left
    ]
    return TriMesh(v, f)

def test_clip_cube_horizontal(tri_cube):
    # Cut cube at z = 0.5
    origin = (0, 0, 0.5)
    normal = (0, 0, 1)
    
    mesh_above, mesh_below = MeshClipper.clip(tri_cube, origin, normal)
    
    # Each vertical face (8 of them) was cut in half.
    # The 2 horizontal faces (top/bottom) remain untouched.
    # Resulting shells should have many more faces due to splitting.
    assert len(mesh_above.vertices) > 0
    assert len(mesh_below.vertices) > 0
    assert len(mesh_above.faces) > 0
    assert len(mesh_below.faces) > 0
    
    # Check that all vertices in mesh_above have z >= 0.5 (approx)
    for v in mesh_above.vertices:
        assert v.z >= 0.5 - 1e-7
        
    # Check that all vertices in mesh_below have z <= 0.5 (approx)
    for v in mesh_below.vertices:
        assert v.z <= 0.5 + 1e-7

def test_clip_no_intersection(tri_cube):
    # Plane entirely below the cube
    origin = (0, 0, -1)
    normal = (0, 0, 1)
    mesh_above, mesh_below = MeshClipper.clip(tri_cube, origin, normal)
    
    # All cube should be above
    assert len(mesh_above.faces) == 12
    assert len(mesh_below.faces) == 0

def test_clip_all_below(tri_cube):
    # Plane entirely above the cube
    origin = (0, 0, 2)
    normal = (0, 0, 1)
    mesh_above, mesh_below = MeshClipper.clip(tri_cube, origin, normal)
    
    assert len(mesh_above.faces) == 0
    assert len(mesh_below.faces) == 12
