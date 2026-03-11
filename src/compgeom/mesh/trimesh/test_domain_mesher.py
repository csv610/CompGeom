
import sys
import os

# Add the project root to sys.path to allow importing compgeom
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from compgeom.mesh.trimesh.domain_mesher import DomainMesher

def test_mesher():
    print("Testing DomainMesher.square...")
    mesh_sq = DomainMesher.square(10.0, 1.0)
    print(f"Square mesh: {len(mesh_sq.vertices)} vertices, {len(mesh_sq.faces)} faces")

    print("\nTesting DomainMesher.rectangle...")
    mesh_rect = DomainMesher.rectangle(20.0, 10.0, 2.0)
    print(f"Rectangle mesh: {len(mesh_rect.vertices)} vertices, {len(mesh_rect.faces)} faces")

    print("\nTesting DomainMesher.triangle...")
    mesh_tri = DomainMesher.triangle(10.0, 1.0)
    print(f"Triangle mesh: {len(mesh_tri.vertices)} vertices, {len(mesh_tri.faces)} faces")

    print("\nTesting DomainMesher.circle...")
    mesh_circ = DomainMesher.circle(5.0, 1.0)
    print(f"Circle mesh: {len(mesh_circ.vertices)} vertices, {len(mesh_circ.faces)} faces")

if __name__ == "__main__":
    test_mesher()
