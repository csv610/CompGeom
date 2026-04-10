"""Unit tests for Volume Meshing algorithms."""

import pytest
import numpy as np
from compgeom.mesh.volume.tetmesh.winding_filtered_mesher import WindingFilteredTetMesher

def test_winding_filtered_mesher_init():
    v = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]])
    f = np.array([[0,1,2], [0,2,3], [0,3,1], [1,2,3]])
    mesher = WindingFilteredTetMesher(v, f)
    assert len(mesher.vertices) == 4
