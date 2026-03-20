
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.mesh import TetMesh
from compgeom.mesh.volume.tetmesh.refine import TetMeshRefiner, refine_tetmesh_centroid, refine_tetmesh_midpoint

@pytest.fixture
def single_tet():
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    c = [(0,1,2,3)]
    return TetMesh(v, c)

def test_refine_centroid(single_tet):
    refined = refine_tetmesh_centroid(single_tet)
    # 4 original + 1 centroid = 5 vertices
    # 1 original split into 4 = 4 tets
    assert len(refined.vertices) == 5
    assert len(refined.cells) == 4
    
    # Check centroid coords
    c = refined.vertices[4]
    assert c.x == 0.25
    assert c.y == 0.25
    assert c.z == 0.25

def test_refine_midpoint(single_tet):
    refined = refine_tetmesh_midpoint(single_tet)
    # 4 original + 6 midpoints = 10 vertices
    # 1 split into 8 = 8 tets
    assert len(refined.vertices) == 10
    assert len(refined.cells) == 8

def test_tetmesh_refiner_class(single_tet):
    refiner = TetMeshRefiner(single_tet)
    
    res_global = refiner.refine_global()
    assert len(res_global.cells) == 8
    
    res_local = refiner.refine_local([0])
    assert len(res_local.cells) == 4
    
    res_cc = refiner.refine_circumcenter([0])
    assert len(res_cc.cells) == 4
    # Circumcenter of this right tet is (0.5, 0.5, 0.5)
    assert res_cc.vertices[4].x == 0.5
