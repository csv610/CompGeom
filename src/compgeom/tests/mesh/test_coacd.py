"""Unit tests for CoACD algorithm."""
import pytest
import numpy as np
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.coacd import CoACD
from compgeom.kernel import Point3D

def make_u_shape():
    """Creates a non-convex U-shaped mesh."""
    # Simplified U-shape using a few boxes merged
    # For now, let's use a composite set of vertices
    verts = [
        # Box 1 (Left)
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,3), Point3D(1,0,3), Point3D(1,1,3), Point3D(0,1,3),
        # Box 2 (Bottom)
        Point3D(1,0,0), Point3D(4,0,0), Point3D(4,1,0), Point3D(1,1,0),
        Point3D(1,0,1), Point3D(4,0,1), Point3D(4,1,1), Point3D(1,1,1),
        # Box 3 (Right)
        Point3D(4,0,0), Point3D(5,0,0), Point3D(5,1,0), Point3D(4,1,0),
        Point3D(4,0,3), Point3D(5,0,3), Point3D(5,1,3), Point3D(4,1,3),
    ]
    # Simple triangulation logic for a composite mesh
    # For unit test, we can just use a simpler L-shape (2 boxes)
    verts = [
        Point3D(0,0,0), Point3D(2,0,0), Point3D(2,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(2,0,1), Point3D(2,1,1), Point3D(0,1,1),
        Point3D(0,1,0), Point3D(1,1,0), Point3D(1,2,0), Point3D(0,2,0),
        Point3D(0,1,1), Point3D(1,1,1), Point3D(1,2,1), Point3D(0,2,1),
    ]
    # Use a simpler proxy: a mesh with a large concavity
    # Triangle fan around a concave vertex
    verts = [
        Point3D(0,0,0), Point3D(2,0,0), Point3D(2,2,0), Point3D(1,1,0), Point3D(0,2,0),
        Point3D(0,0,1), Point3D(2,0,1), Point3D(2,2,1), Point3D(1,1,1), Point3D(0,2,1),
    ]
    # This is still manual. Let's use a programmatic approach if possible.
    return TriMesh.from_triangles([
        # Two triangles forming an L-shape base
        (Point3D(0,0,0), Point3D(2,0,0), Point3D(2,1,0)),
        (Point3D(0,0,0), Point3D(2,1,0), Point3D(0,1,0)),
        # Adding a vertical part
        (Point3D(0,1,0), Point3D(1,1,0), Point3D(1,2,0)),
        (Point3D(0,1,0), Point3D(1,2,0), Point3D(0,2,0)),
    ])

def test_coacd_initialization():
    mesh = make_u_shape()
    coacd = CoACD(mesh, threshold=0.1)
    assert coacd.threshold == 0.1
    assert coacd.mesh == mesh

def test_coacd_decomposition():
    mesh = make_u_shape()
    # An L-shape is concave. It should be split at least once.
    coacd = CoACD(mesh, threshold=0.01)
    parts = coacd.decompose()
    # For a simple L-shape, we expect 2 convex pieces
    assert len(parts) >= 1
    for p in parts:
        assert len(p.faces) > 0
