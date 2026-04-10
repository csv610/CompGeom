"""Unit tests for Stochastic PDE solvers (Walk on Spheres and Walk on Stars)."""

import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.stochastic_pde import WalkOnSpheres, WalkOnStars

@pytest.fixture
def simple_disk():
    # A single square patch triangulated (2 triangles)
    verts = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    return TriMesh(verts, faces)

@pytest.fixture
def simple_trimesh():
    # Tetrahedron
    verts = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1)]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return TriMesh(verts, faces)

def test_walk_on_spheres_laplace(simple_disk):
    wos = WalkOnSpheres(simple_disk)
    # Solve Laplace for boundary values = constant 1.0
    # Expected result for any interior point should be 1.0
    val = wos.solve_laplace(Point3D(0.5, 0.5, 0), lambda p: 1.0, num_walks=100)
    assert pytest.approx(val, rel=0.1) == 1.0

def test_walk_on_stars_gradient(simple_trimesh):
    wost = WalkOnStars(simple_trimesh)
    # For a linear function u(x,y,z) = x, the gradient should be (1, 0, 0)
    grad = wost.solve_gradient(Point3D(0.1, 0.1, 0.1), lambda p: p.x, num_walks=200)
    assert len(grad) == 3
    # Check that it is roughly in the right direction (Monte Carlo has high variance)
    assert grad[0] > 0.0
    assert abs(grad[1]) < 0.6
    assert abs(grad[2]) < 0.6
