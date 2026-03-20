
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.trimesh.mesh_refinement import TriMeshRefiner

@pytest.fixture
def single_tri():
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)]
    f = [(0,1,2)]
    return TriMesh(v, f)

def test_subdivide_linear(single_tri):
    refined = TriMeshRefiner.subdivide_linear(single_tri)
    # Original: 1 face, 3 vertices
    # After subdivision: 4 faces, 6 vertices (3 original + 3 midpoints)
    assert len(refined.faces) == 4
    assert len(refined.vertices) == 6
    
    # Check that midpoints are correct (e.g. midpoint of (0,0,0) and (1,0,0) is (0.5,0,0))
    pts = {(v.x, v.y, v.z) for v in refined.vertices}
    assert (0.5, 0, 0) in pts
    assert (0, 0.5, 0) in pts
    assert (0.5, 0.5, 0) in pts

def test_refine_uniform(single_tri):
    # Original area is 0.5
    # Request max_area_ratio = 0.3. 
    # One level of subdivision will make each face area 0.5 / 4 = 0.125
    # 0.125 / 0.5 = 0.25, which is < 0.3. 
    # So it should do exactly one level of subdivision.
    refined = TriMeshRefiner.refine_uniform(single_tri, 0.3)
    assert len(refined.faces) == 4
    
    # Request smaller ratio -> more levels
    refined2 = TriMeshRefiner.refine_uniform(single_tri, 0.1)
    # 0.5 / 16 = 0.03125 (< 0.05). Each triangle in level 1 (0.125) will be split.
    # Total 16 faces.
    assert len(refined2.faces) == 16

def test_calculate_face_area():
    v0, v1, v2 = Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)
    area = TriMeshRefiner._calculate_face_area(v0, v1, v2)
    assert area == pytest.approx(0.5)
