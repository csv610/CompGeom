
import pytest
import numpy as np
from compgeom.mesh.volume.hexmesh.hex2tet import hex_to_tet_6, refine_hex_to_tet_24

@pytest.fixture
def unit_cube():
    points = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ])
    hexes = np.array([[0, 1, 2, 3, 4, 5, 6, 7]])
    return points, hexes

def get_total_volume(pts, tets):
    vol = 0
    for t in tets:
        p = pts[t]
        vol += np.abs(np.dot(p[1]-p[0], np.cross(p[2]-p[0], p[3]-p[0]))) / 6.0
    return vol

def test_hex_to_tet_6(unit_cube):
    pts, hexes = unit_cube
    pts6, tets6 = hex_to_tet_6(pts, hexes)
    assert len(tets6) == 6
    assert get_total_volume(pts6, tets6) == pytest.approx(1.0)

def test_refine_hex_to_tet_24(unit_cube):
    pts, hexes = unit_cube
    pts24, tets24 = refine_hex_to_tet_24(pts, hexes)
    # 8 original + 1 cell centroid + 6 face centroids = 15
    assert len(pts24) == 15
    assert len(tets24) == 24
    assert get_total_volume(pts24, tets24) == pytest.approx(1.0)
