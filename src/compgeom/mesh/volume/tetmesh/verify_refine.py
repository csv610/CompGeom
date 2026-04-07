import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

# Extreme mocking to bypass broken project imports
import types
broken_modules = [
    "compgeom.mesh.surface.trimesh.node_move_constraints",
    "compgeom.mesh.mesh_coloring",
    "compgeom.mesh.mesh_reordering",
    "compgeom.mesh.mesh_check",
    "compgeom.mesh.mesh_io",
    "compgeom.mesh.mesh_transfer",
    "compgeom.mesh.mesh_stats",
    "compgeom.mesh.mesh_smoothing",
    "compgeom.mesh.mesh_quality",
    "compgeom.mesh.mesh_deformation",
]

for mod_name in broken_modules:
    mock_mod = types.ModuleType(mod_name)
    sys.modules[mod_name] = mock_mod
    # Add common classes to mocks
    mock_mod.VertexConstraint = type("VertexConstraint", (), {})
    mock_mod.MeshColoring = type("MeshColoring", (), {})
    mock_mod.CuthillMcKee = type("CuthillMcKee", (), {})
    mock_mod.MeshCheck = type("MeshCheck", (), {})
    mock_mod.MeshIO = type("MeshIO", (), {})
    mock_mod.MeshTransfer = type("MeshTransfer", (), {})
    mock_mod.MeshStats = type("MeshStats", (), {})
    mock_mod.MeshSmoothing = type("MeshSmoothing", (), {})
    mock_mod.MeshQuality = type("MeshQuality", (), {})
    mock_mod.MeshDeformation = type("MeshDeformation", (), {})

try:
    from compgeom.kernel import Point3D
    from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh
    from compgeom.mesh.volume.tetmesh.refine import refine_tetmesh_global, refine_tetmesh_local, TetMeshRefiner
    
    print("Testing Global Refinement (Midpoint)...")
    points = [Point3D(0, 0, 0, id=0), Point3D(1, 0, 0, id=1), Point3D(0, 1, 0, id=2), Point3D(0, 0, 1, id=3)]
    mesh = TetMesh(points, [(0, 1, 2, 3)])
    refined_global = refine_tetmesh_global(mesh)
    assert len(refined_global.cells) == 8
    print("✓ Global refinement passed (1 tet -> 8 tets)")

    print("Testing Local Refinement (Centroid)...")
    points_2 = [
        Point3D(0, 0, 0, id=0), Point3D(1, 0, 0, id=1), Point3D(0, 1, 0, id=2),
        Point3D(0, 0, 1, id=3), Point3D(0, 0, -1, id=4)
    ]
    mesh_2 = TetMesh(points_2, [(0, 1, 2, 3), (0, 1, 2, 4)])
    refined_local = refine_tetmesh_local(mesh_2, [0])
    assert len(refined_local.cells) == 5
    assert len(refined_local.vertices) == 6
    print("✓ Local refinement passed (2 tets -> 5 tets, only specified tet refined)")

    print("Testing TetMeshRefiner class...")
    refiner = TetMeshRefiner(mesh)
    refined_class_global = refiner.refine_global()
    assert len(refined_class_global.cells) == 8
    refined_class_centroid = refiner.refine_centroid()
    assert len(refined_class_centroid.cells) == 4
    print("✓ TetMeshRefiner class tests passed")
    
    print("\nALL REFINEMENT TESTS PASSED!")

except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
