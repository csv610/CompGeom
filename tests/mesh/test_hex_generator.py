
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.volume.hexmesh.conforming_generator import ConformingHexMesher

@pytest.fixture
def single_quad():
    # A unit square in XY plane
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    f = [(0,1,2,3)]
    return QuadMesh(v, f)

def test_extrude_quad_mesh(single_quad):
    # Extrude by 1 unit in Z with 2 steps
    vector = (0, 0, 1.0)
    steps = 2
    hex_mesh = ConformingHexMesher.extrude_quad_mesh(single_quad, vector, steps)
    
    # 4 base vertices * (2 steps + 1) = 12 vertices
    # 1 base quad * 2 steps = 2 hexes
    assert len(hex_mesh.vertices) == 12
    assert len(hex_mesh.cells) == 2
    
    # Check top vertices are at z=1.0
    for i in range(8, 12):
        assert hex_mesh.vertices[i].z == pytest.approx(1.0)

def test_generate_shell(single_quad):
    # Shell with thickness 0.1
    hex_mesh = ConformingHexMesher.generate_shell(single_quad, 0.1)
    
    # 4 base vertices * 2 layers = 8 vertices
    # 1 base quad = 1 hex
    assert len(hex_mesh.vertices) == 8
    assert len(hex_mesh.cells) == 1
    
    # Vertex normal for XY plane is (0,0,1)
    # Inner vertices should be at z = -0.1
    for i in range(4, 8):
        assert hex_mesh.vertices[i].z == pytest.approx(-0.1)

def test_extrude_errors(single_quad):
    with pytest.raises(ValueError):
        ConformingHexMesher.extrude_quad_mesh(single_quad, (0,0,1), steps=0)
