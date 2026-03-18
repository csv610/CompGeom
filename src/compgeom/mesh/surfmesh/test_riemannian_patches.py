"""Test script for Riemannian patch identification on Platonic solids."""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from compgeom.mesh.surfmesh.trimesh.platonic_solids import PlatonicSolid
from compgeom.mesh.surfmesh.riemannian_patches import identify_riemannian_patches

def test_platonic_solids():
    solids = [
        ("Tetrahedron", PlatonicSolid.tetrahedron()),
        ("Cube", PlatonicSolid.cube()),
        ("Octahedron", PlatonicSolid.octahedron()),
        ("Dodecahedron", PlatonicSolid.dodecahedron()),
        ("Icosahedron", PlatonicSolid.icosahedron()),
    ]

    print(f"{'Solid':<15} | {'Patches':<8} | {'Faces/Patch':<12}")
    print("-" * 40)

    for name, mesh in solids:
        # Using default 30 degree threshold
        patches = identify_riemannian_patches(mesh)
        
        # In Platonic solids, all patches should have the same number of faces
        faces_per_patch = len(patches[0].faces) if patches else 0
        
        print(f"{name:<15} | {len(patches):<8} | {faces_per_patch:<12}")

if __name__ == "__main__":
    test_platonic_solids()
