
import math
from compgeom.mesh import TriMesh
from compgeom.kernel import Point3D
from mesh_tunnel_loops import MeshTunnelLoops

def test_mesh_tunnel_loops():
    print("Testing Mesh Tunnel Loops...")
    
    # --- Genus 0 test (Cube) ---
    verts_cube = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1),
    ]
    faces_cube = [
        (0,1,2),(0,2,3), # Bottom
        (4,5,6),(4,6,7), # Top
        (0,1,5),(0,5,4), # Front
        (1,2,6),(1,6,5), # Right
        (2,3,7),(2,7,6), # Back
        (3,0,4),(3,4,7), # Left
    ]
    mesh_cube = TriMesh(verts_cube, faces_cube)
    
    chi_c, genus_c = MeshTunnelLoops._calculate_topology(mesh_cube)
    print(f"Cube - Euler: {chi_c}, Genus: {genus_c}")
    assert genus_c == 0
    
    loops_c = MeshTunnelLoops.identify_tunnels(mesh_cube)
    assert len(loops_c) == 1 # max(1, 2*0)
    
    # --- Genus 1 test (Torus) ---
    def get_idx(r, c):
        return (r % 4) * 4 + (c % 4)
        
    v_torus = []
    for r in range(4):
        for c in range(4):
            theta = 2 * math.pi * r / 4
            phi = 2 * math.pi * c / 4
            R, a = 2.0, 0.5
            x = (R + a * math.cos(phi)) * math.cos(theta)
            y = (R + a * math.cos(phi)) * math.sin(theta)
            z = a * math.sin(phi)
            v_torus.append(Point3D(x, y, z))
            
    f_torus = []
    for r in range(4):
        for c in range(4):
            i1, i2, i3, i4 = get_idx(r,c), get_idx(r+1,c), get_idx(r+1,c+1), get_idx(r,c+1)
            f_torus.append((i1, i2, i3))
            f_torus.append((i1, i3, i4))
            
    mesh_torus = TriMesh(v_torus, f_torus)
    chi_t, genus_t = MeshTunnelLoops._calculate_topology(mesh_torus)
    print(f"Torus - Euler: {chi_t}, Genus: {genus_t}")
    assert genus_t == 1
    
    loops_t = MeshTunnelLoops.identify_tunnels(mesh_torus)
    print(f"Number of loops found for torus: {len(loops_t)}")
    assert len(loops_t) == 2
    for loop in loops_t:
        print(f"Loop (len {len(loop)}): {loop}")

if __name__ == "__main__":
    try:
        test_mesh_tunnel_loops()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
