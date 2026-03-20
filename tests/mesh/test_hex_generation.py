"""Unit tests for Conforming Hexahedral Mesh Generation."""
import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.volume.hexmesh.conforming_generator import ConformingHexMesher

def test_extrude_quad_mesh():
    # Single quad at z=0
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2, 3)]
    mesh = QuadMesh(verts, faces)
    
    # Extrude along Z by 1.0 unit
    hex_mesh = ConformingHexMesher.extrude_quad_mesh(mesh, (0, 0, 1), steps=1)
    
    assert len(hex_mesh.nodes) == 8
    assert len(hex_mesh.cells) == 1
    
    # Verify hex vertices
    cell = hex_mesh.cells[0]
    assert len(cell.v_indices) == 8
    
    # Verify some coordinates
    # Bottom vertices should be original
    # Top vertices should be shifted by (0,0,1)
    v4 = hex_mesh.nodes[cell.v_indices[4]].point
    assert v4.x == 0.0
    assert v4.y == 0.0
    assert v4.z == 1.0

def test_generate_shell():
    # Single quad at z=0
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2, 3)]
    mesh = QuadMesh(verts, faces)
    
    # Generate shell with thickness 0.1
    # For a flat quad at z=0, normal is (0,0,1)
    # Shell should have inner vertices at z=-0.1
    hex_mesh = ConformingHexMesher.generate_shell(mesh, 0.1)
    
    assert len(hex_mesh.nodes) == 8
    assert len(hex_mesh.cells) == 1
    
    cell = hex_mesh.cells[0]
    # Check inner vertex (vertex 4 in hex should be vertex 0 shifted)
    v4 = hex_mesh.nodes[cell.v_indices[4]].point
    assert v4.z == pytest.approx(-0.1)
