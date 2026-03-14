
import numpy as np
from compgeom.mesh import TriangleMesh
from compgeom.kernel import Point3D
from mesh_rigidity import MeshRigidity

def test_triangle_rigidity():
    print("Testing Triangle Rigidity...")
    # Single triangle in XY plane
    v = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(0.5, 0.866, 0.0)
    ]
    f = [(0, 1, 2)]
    mesh = TriangleMesh(v, f)
    
    # If we fix nodes 0 and 1, the triangle is in 2D rigid, 
    # but in 3D node 2 can rotate around edge (0,1).
    # So it should NOT be rigid in 3D.
    rigid = MeshRigidity.is_rigid(mesh, fixed_node_indices=[0, 1])
    dof = MeshRigidity.analyze_degrees_of_freedom(mesh, fixed_node_indices=[0, 1])
    print(f"Triangle (2 nodes fixed): Rigid={rigid}, DOFs={dof}")
    
    # If we fix all 3 nodes, it's rigid.
    rigid_all = MeshRigidity.is_rigid(mesh, fixed_node_indices=[0, 1, 2])
    print(f"Triangle (3 nodes fixed): Rigid={rigid_all}")

def test_tetrahedron_rigidity():
    print("\nTesting Tetrahedron Rigidity...")
    # Standard tetrahedron
    v = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(0.5, 0.866, 0.0),
        Point3D(0.5, 0.288, 0.816)
    ]
    f = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    mesh = TriangleMesh(v, f)
    
    # A tetrahedron with 3 nodes fixed should be rigid in 3D (the 4th node is fixed by 3 edges).
    rigid = MeshRigidity.is_rigid(mesh, fixed_node_indices=[0, 1, 2])
    dof = MeshRigidity.analyze_degrees_of_freedom(mesh, fixed_node_indices=[0, 1, 2])
    print(f"Tetrahedron (3 nodes fixed): Rigid={rigid}, DOFs={dof}")
    
    # Feasibility check: Move node 3 slightly in a way that respects edge lengths (infinitesimally).
    # Since it's rigid, only ZERO movement should be feasible if it was fixed.
    # But here node 3 is NOT in fixed_node_indices, it's the moving_node.
    # The check_movement_feasibility treats moving_node as constrained.
    
    # For a rigid structure, any movement that violates edge lengths should be infeasible.
    # In a rigid tetrahedron, node 3's position is fixed by distances to 0, 1, 2.
    # Infinitesimally, dp_3 must satisfy (p_3 - p_i) . dp_3 = 0 for i=0,1,2.
    # This system has only dp_3 = 0 as solution if the vectors (p_3 - p_i) are linearly independent.
    
    target_pos = (0.5, 0.288, 0.816 + 0.1) # Move UP
    feasible, rigid_after = MeshRigidity.check_movement_feasibility(mesh, [0, 1, 2], 3, target_pos)
    print(f"Tetrahedron Move node 3 UP: Feasible={feasible}, Rigid={rigid_after}")
    
    target_pos_same = (0.5, 0.288, 0.816)
    feasible_same, _ = MeshRigidity.check_movement_feasibility(mesh, [0, 1, 2], 3, target_pos_same)
    print(f"Tetrahedron Move node 3 to SAME pos: Feasible={feasible_same}")

def test_chain_rigidity():
    print("\nTesting Chain Rigidity...")
    # Two triangles sharing an edge (0,1). Node 2 and 3 are free.
    # 0,1 are fixed.
    v = [
        Point3D(0.0, 0.0, 0.0), # 0
        Point3D(1.0, 0.0, 0.0), # 1
        Point3D(0.5, 0.866, 0.0), # 2
        Point3D(0.5, -0.866, 0.0) # 3
    ]
    f = [(0, 1, 2), (0, 1, 3)]
    mesh = TriangleMesh(v, f)
    
    # Each free node (2 and 3) can rotate around edge (0,1) independently.
    # So we should have 2 DOFs (one for each triangle flap).
    rigid = MeshRigidity.is_rigid(mesh, fixed_node_indices=[0, 1])
    dof = MeshRigidity.analyze_degrees_of_freedom(mesh, fixed_node_indices=[0, 1])
    print(f"Triangle Flaps (2 nodes fixed): Rigid={rigid}, DOFs={dof}")

if __name__ == "__main__":
    test_triangle_rigidity()
    test_tetrahedron_rigidity()
    test_chain_rigidity()
