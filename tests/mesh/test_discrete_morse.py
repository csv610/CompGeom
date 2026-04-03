"""Unit tests for Discrete Morse Theory."""

import pytest
import numpy as np
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D
from compgeom.mesh.algorithms.discrete_morse import DiscreteMorse


@pytest.fixture
def sphere_like_mesh():
    # A simple octahedron (sphere-like topology, chi=2)
    verts = [
        Point3D(1, 0, 0),
        Point3D(-1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, -1, 0),
        Point3D(0, 0, 1),
        Point3D(0, 0, -1),
    ]
    faces = [
        (4, 0, 2),
        (4, 2, 1),
        (4, 1, 3),
        (4, 3, 0),
        (5, 2, 0),
        (5, 1, 2),
        (5, 3, 1),
        (5, 0, 3),
    ]
    return TriMesh(verts, faces)


def test_discrete_morse_euler_sphere(sphere_like_mesh):
    # Height function f(x,y,z) = z
    v_vals = np.array([v.z for v in sphere_like_mesh.vertices])

    dm = DiscreteMorse(sphere_like_mesh, v_vals)
    chi = dm.get_euler_characteristic()

    # For any manifold mesh with sphere topology, chi must be 2.
    # The Morse relation says Sum (-1)^i C_i = chi.
    assert chi == 2


def test_discrete_morse_critical_points(sphere_like_mesh):
    # Height function f(x,y,z) = z
    v_vals = np.array([v.z for v in sphere_like_mesh.vertices])
    # Vertex 4 is at z=1 (max), vertex 5 is at z=-1 (min)
    # Others are at z=0.

    dm = DiscreteMorse(sphere_like_mesh, v_vals)
    crit = dm.get_critical_points()

    # We expect at least one minimum and one maximum
    assert len(crit["minima"]) >= 1
    assert len(crit["maxima"]) >= 1


def test_discrete_morse_flat_patch():
    # 2x2 square patch (9 vertices, 8 faces)
    verts = []
    for i in range(3):
        for j in range(3):
            verts.append(Point3D(i, j, 0))
    faces = []
    for i in range(2):
        for j in range(2):
            v0 = i * 3 + j
            v1 = (i + 1) * 3 + j
            v2 = (i + 1) * 3 + (j + 1)
            v3 = i * 3 + (j + 1)
            faces.append((v0, v1, v2))
            faces.append((v0, v2, v3))
    mesh = TriMesh(verts, faces)

    # Function f(x,y) = x + y (diagonal ramp)
    v_vals = np.array([v.x + v.y for v in mesh.vertices])

    dm = DiscreteMorse(mesh, v_vals)
    crit = dm.get_critical_points()

    assert len(crit["minima"]) >= 1
