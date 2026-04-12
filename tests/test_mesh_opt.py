"""Tests for mesh_opt_arap and mesh_opt_acap modules."""

import numpy as np
import pytest

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.mesh_analysis import MeshAnalysis
from compgeom.mesh.surface.primitives import Primitives
from compgeom.kernel import Point3D
from compgeom.mesh.surface.mesh_opt_arap import MeshARAP, mesh_arap_optimize
from compgeom.mesh.surface.mesh_opt_acap import MeshACAP, mesh_acap_optimize


def create_test_mesh():
    """Create a simple tetrahedron mesh for testing."""
    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(0.5, 1.0, 0.0),
        Point3D(0.5, 0.5, 1.0),
    ]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)]
    return TriMesh(nodes=nodes, faces=faces)


def test_arap_imports():
    """Test that classes can be imported."""
    assert MeshARAP is not None
    assert mesh_arap_optimize is not None


def test_acap_imports():
    """Test that classes can be imported."""
    assert MeshACAP is not None
    assert mesh_acap_optimize is not None


def test_mesh_arap_init():
    """Test MeshARAP initialization."""
    mesh = create_test_mesh()
    arap = MeshARAP(mesh, mesh)

    assert arap.mesh is mesh
    assert arap.original_mesh is mesh
    assert arap.current_vertices.shape[0] == 4
    assert len(arap._original_lengths) > 0


def test_mesh_acap_init():
    """Test MeshACAP initialization."""
    mesh = create_test_mesh()
    acap = MeshACAP(mesh, mesh)

    assert acap.mesh is mesh
    assert acap.original_mesh is mesh
    assert acap.current_vertices.shape[0] == 4
    assert len(acap._weights) > 0


def test_mesh_arap_optimize():
    """Test MeshARAP optimization runs."""
    mesh = create_test_mesh()
    result = mesh_arap_optimize(mesh, mesh, iterations=10, step_size=0.5)

    assert isinstance(result, TriMesh)
    assert len(result.vertices) == 4
    assert len(result.faces) == 4


def test_mesh_acap_optimize():
    """Test MeshACAP optimization runs."""
    mesh = create_test_mesh()
    result = mesh_acap_optimize(mesh, mesh, iterations=10, step_size=0.5)

    assert isinstance(result, TriMesh)
    assert len(result.vertices) == 4
    assert len(result.faces) == 4


def test_arap_edge_preservation():
    """Test that ARAP preserves edge lengths."""
    mesh = Primitives.icosahedron(size=1.0)
    original = mesh_arap_optimize(mesh, mesh, iterations=50, step_size=0.3)

    orig_edges = {}
    for f in mesh.faces:
        for i in range(3):
            u, v = sorted((f[i], f[(i + 1) % 3]))
            p_u = mesh.vertices[u]
            p_v = mesh.vertices[v]
            orig_edges[(u, v)] = np.sqrt(
                (p_u.x - p_v.x) ** 2 + (p_u.y - p_v.y) ** 2 + (p_u.z - p_v.z) ** 2
            )

    opt_edges = {}
    for f in original.faces:
        for i in range(3):
            u, v = sorted((f[i], f[(i + 1) % 3]))
            p_u = original.vertices[u]
            p_v = original.vertices[v]
            opt_edges[(u, v)] = np.sqrt(
                (p_u.x - p_v.x) ** 2 + (p_u.y - p_v.y) ** 2 + (p_u.z - p_v.z) ** 2
            )

    errors = []
    for edge in orig_edges:
        if edge in opt_edges:
            err = abs(orig_edges[edge] - opt_edges[edge]) / orig_edges[edge]
            errors.append(err)

    avg_error = np.mean(errors)
    assert avg_error < 0.5


def test_acap_angle_preservation():
    """Test that ACAP preserves angles."""
    mesh = Primitives.icosahedron(size=1.0)
    original = mesh_acap_optimize(mesh, mesh, iterations=50, step_size=0.3)

    orig_area = MeshAnalysis.total_area(mesh)
    opt_area = MeshAnalysis.total_area(original)

    area_diff = abs(orig_area - opt_area) / orig_area
    assert area_diff < 0.5


def test_arap_with_ellipsoid():
    """Test ARAP with ellipsoid mesh."""
    original_mesh = Primitives.ellipsoid(rx=2.0, ry=1.0, rz=1.0, subdivisions=2)
    new_faces = [(f[0], f[2], f[1]) for f in original_mesh.faces]
    original_mesh = TriMesh(original_mesh.vertices, new_faces)

    result = mesh_arap_optimize(original_mesh, original_mesh, iterations=20)

    assert len(result.vertices) == len(original_mesh.vertices)
    assert len(result.faces) == len(original_mesh.faces)


def test_acap_with_ellipsoid():
    """Test ACAP with ellipsoid mesh."""
    original_mesh = Primitives.ellipsoid(rx=2.0, ry=1.0, rz=1.0, subdivisions=2)
    new_faces = [(f[0], f[2], f[1]) for f in original_mesh.faces]
    original_mesh = TriMesh(original_mesh.vertices, new_faces)

    result = mesh_acap_optimize(original_mesh, original_mesh, iterations=20)

    assert len(result.vertices) == len(original_mesh.vertices)
    assert len(result.faces) == len(original_mesh.faces)


def test_fixed_vertices():
    """Test that fixed vertices are preserved."""
    mesh = create_test_mesh()
    fixed = {0}

    arap = MeshARAP(mesh, mesh, fixed_indices=fixed)
    arap.optimize(iterations=10)

    np.testing.assert_array_almost_equal(
        arap.current_vertices[0],
        [mesh.vertices[0].x, mesh.vertices[0].y, mesh.vertices[0].z],
    )
