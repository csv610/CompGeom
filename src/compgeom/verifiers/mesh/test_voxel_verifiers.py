import unittest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.volume.voxelmesh.voxelization import MeshVoxelizer
from compgeom.verifiers.mesh.voxel_verifiers import verify_mesh_voxelization


class TestVoxelVerifiers(unittest.TestCase):
    def setUp(self):
        # A simple unit cube mesh
        # Vertices (0,0,0) to (1,1,1)
        vertices = [
            Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
            Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
        ]
        faces = [
            (0, 2, 1), (0, 3, 2), # Bottom (Down)
            (4, 5, 6), (4, 6, 7), # Top (Up)
            (0, 1, 5), (0, 5, 4), # Front (South)
            (2, 3, 7), (2, 7, 6), # Back (North)
            (0, 4, 7), (0, 7, 3), # Left (West)
            (1, 2, 6), (1, 6, 5)  # Right (East)
        ]
        self.mesh = TriMesh(vertices, faces)

    def test_voxelize_native_surface(self):
        voxel_size = 0.2
        voxels = MeshVoxelizer.voxelize_native(self.mesh, voxel_size, fill_interior=False)
        self.assertTrue(verify_mesh_voxelization(self.mesh, voxel_size, voxels, fill_interior=False))

    def test_voxelize_native_interior(self):
        voxel_size = 0.2
        voxels = MeshVoxelizer.voxelize_native(self.mesh, voxel_size, fill_interior=True)
        self.assertTrue(verify_mesh_voxelization(self.mesh, voxel_size, voxels, fill_interior=True))

    def test_invalid_voxel_outside(self):
        voxel_size = 0.5
        voxels = MeshVoxelizer.voxelize_native(self.mesh, voxel_size)
        # Add a voxel far away
        voxels.add((10, 10, 10))
        with self.assertRaises(ValueError) as cm:
            verify_mesh_voxelization(self.mesh, voxel_size, voxels)
        self.assertIn("outside mesh bounding box", str(cm.exception))

    def test_invalid_voxel_not_on_surface(self):
        # Small cube, large voxel size
        # Voxel (1,1,1) covers [0.5, 1.0]^3. This is on surface.
        # Voxel (2,2,2) covers [1.0, 1.5]^3. This is outside.
        voxel_size = 0.5
        voxels = {(0,0,0), (1,0,0), (0,1,0), (0,0,1)} # Some surface voxels
        voxels.add((3,3,3)) # Clearly outside
        
        with self.assertRaises(ValueError):
             verify_mesh_voxelization(self.mesh, voxel_size, voxels, fill_interior=False)


if __name__ == "__main__":
    unittest.main()
