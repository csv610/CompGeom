import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.tetmesh.tetmesh import TetMesh
from compgeom.mesh.volmesh.tetmesh.refine import (
    refine_tetmesh_centroid, 
    refine_tetmesh_midpoint,
    refine_tetmesh_local,
    refine_tetmesh_global,
    TetMeshRefiner
)

def test_tetmesh_refiner_class():
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
    ]
    mesh = TetMesh(points, [(0, 1, 2, 3)])
    refiner = TetMeshRefiner(mesh)
    
    refined_global = refiner.refine_global()
    assert len(refined_global.cells) == 8
    
    refined_centroid = refiner.refine_centroid()
    assert len(refined_centroid.cells) == 4
    
    refined_local = refiner.refine_local([0])
    assert len(refined_local.cells) == 4

def test_refine_local():
    # Two tets sharing a face
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
        Point3D(0, 0, -1, id=4),
    ]
    tets = [(0, 1, 2, 3), (0, 1, 2, 4)]
    mesh = TetMesh(points, tets)
    
    # Refine only the first tet
    refined = refine_tetmesh_local(mesh, [0])
    
    # Tet 0 becomes 4 tets, Tet 1 remains 1. Total = 5 cells.
    assert len(refined.cells) == 5
    # Original 5 vertices + 1 centroid = 6 vertices.
    assert len(refined.vertices) == 6

def test_refine_global_alias():
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
    ]
    mesh = TetMesh(points, [(0, 1, 2, 3)])
    refined = refine_tetmesh_global(mesh)
    assert len(refined.cells) == 8

def test_refine_centroid_single():
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
    ]
    tets = [(0, 1, 2, 3)]
    mesh = TetMesh(points, tets)
    refined = refine_tetmesh_centroid(mesh)
    assert len(refined.cells) == 4
    assert len(refined.vertices) == 5

def test_refine_midpoint_single():
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
    ]
    tets = [(0, 1, 2, 3)]
    mesh = TetMesh(points, tets)
    refined = refine_tetmesh_midpoint(mesh)
    assert len(refined.cells) == 8
    # 4 original + 6 midpoints = 10 vertices
    assert len(refined.vertices) == 10

def test_refine_midpoint_shared_edge():
    # Two tets sharing a face (v0, v1, v2)
    # 5 points: (0,0,0), (1,0,0), (0,1,0), (0,0,1), (0,0,-1)
    points = [
        Point3D(0, 0, 0, id=0),
        Point3D(1, 0, 0, id=1),
        Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3),
        Point3D(0, 0, -1, id=4),
    ]
    tets = [(0, 1, 2, 3), (0, 1, 2, 4)]
    mesh = TetMesh(points, tets)
    refined = refine_tetmesh_midpoint(mesh)
    # Each tet becomes 8: total 16 cells
    assert len(refined.cells) == 16
    
    # Vertices count:
    # Original: 5
    # Edges: 
    # (0,1), (0,2), (1,2) - shared
    # (0,3), (1,3), (2,3) - only in tet 1
    # (0,4), (1,4), (2,4) - only in tet 2
    # Total edges = 3 + 3 + 3 = 9
    # Total vertices = 5 + 9 = 14
    assert len(refined.vertices) == 14
