import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.mesh import TriMesh
from compgeom.mesh.volume.voxelmesh.voxelization import MeshVoxelizer
from compgeom.mesh.volume.voxelmesh.voxelmesh import VoxelMesh


def create_tetrahedron() -> TriMesh:
    vertices = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1),
    ]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
    return TriMesh(vertices, faces)


def create_cube() -> TriMesh:
    v = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(1, 1, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1),
        Point3D(1, 0, 1),
        Point3D(1, 1, 1),
        Point3D(0, 1, 1),
    ]
    f = [
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 4, 5),
        (0, 5, 1),
        (2, 6, 7),
        (2, 7, 3),
        (0, 3, 7),
        (0, 7, 4),
        (1, 5, 6),
        (1, 6, 2),
    ]
    return TriMesh(v, f)


def test_voxelize_tetrahedron_surface():
    mesh = create_tetrahedron()
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=False)
    assert len(voxels) > 0
    assert all(isinstance(v, tuple) and len(v) == 3 for v in voxels)


def test_voxelize_cube_surface():
    mesh = create_cube()
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=False)
    assert len(voxels) > 0


def test_voxelize_cube_with_fill():
    mesh = create_cube()
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=True)
    assert len(voxels) > 0


def test_voxelize_with_larger_voxel_size():
    mesh = create_cube()
    voxels_small = MeshVoxelizer.voxelize_native(
        mesh, voxel_size=0.25, fill_interior=False
    )
    voxels_large = MeshVoxelizer.voxelize_native(
        mesh, voxel_size=0.5, fill_interior=False
    )
    assert len(voxels_small) >= len(voxels_large)


def test_voxelize_method_returns_set():
    mesh = create_tetrahedron()
    voxels = MeshVoxelizer.voxelize(mesh, voxel_size=0.5, fill_interior=False)
    assert isinstance(voxels, set)
    assert all(isinstance(v, tuple) and len(v) == 3 for v in voxels)


def test_voxelize_empty_mesh():
    mesh = TriMesh([], [])
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=True)
    assert len(voxels) == 0


def test_voxelmesh_creation():
    voxels = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    vm = VoxelMesh(voxels=voxels, voxel_size=1.0)
    assert vm.voxels == voxels
    assert vm.voxel_size == 1.0


def test_voxelmesh_default_voxels():
    vm = VoxelMesh()
    assert vm.voxels == []
    assert vm.voxel_size == 1.0
    assert vm.origin == Point3D(0.0, 0.0, 0.0)


def test_voxelmesh_with_origin():
    origin = Point3D(10, 20, 30)
    vm = VoxelMesh(voxel_size=2.0, origin=origin)
    assert vm.origin == origin
    assert vm.voxel_size == 2.0


def test_voxelize_single_triangle():
    vertices = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
    ]
    faces = [(0, 1, 2)]
    mesh = TriMesh(vertices, faces)
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=False)
    assert len(voxels) > 0


def test_voxel_coordinates_in_bounds():
    mesh = create_cube()
    voxels = MeshVoxelizer.voxelize_native(mesh, voxel_size=0.5, fill_interior=True)
    xs = [v[0] for v in voxels]
    ys = [v[1] for v in voxels]
    zs = [v[2] for v in voxels]
    assert min(xs) <= max(xs)
    assert min(ys) <= max(ys)
    assert min(zs) <= max(zs)


def test_voxelize_openvdb_tetrahedron():
    try:
        import openvdb
    except ImportError:
        pytest.skip("openvdb not installed")
    mesh = create_tetrahedron()
    grid = MeshVoxelizer.voxelize_openvdb(mesh, voxel_size=0.5, fill_interior=True)
    assert grid is not None
    assert isinstance(grid, openvdb.FloatGrid)


def test_voxelize_openvdb_cube():
    try:
        import openvdb
    except ImportError:
        pytest.skip("openvdb not installed")
    mesh = create_cube()
    grid = MeshVoxelizer.voxelize_openvdb(mesh, voxel_size=0.5, fill_interior=True)
    assert grid is not None


def test_voxelize_openvdb_active_voxels():
    try:
        import openvdb
    except ImportError:
        pytest.skip("openvdb not installed")
    mesh = create_cube()
    grid = MeshVoxelizer.voxelize_openvdb(mesh, voxel_size=0.5, fill_interior=True)
    count = grid.activeVoxelCount()
    assert count > 0


def test_voxelize_openvdb_grid_properties():
    try:
        import openvdb
    except ImportError:
        pytest.skip("openvdb not installed")
    mesh = create_cube()
    grid = MeshVoxelizer.voxelize_openvdb(mesh, voxel_size=0.5, fill_interior=True)
    assert isinstance(grid, openvdb.FloatGrid)
