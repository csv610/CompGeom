import numpy as np
from tet2hex import refine_tet_to_hex
from hex2tet import hex_to_tet_6, refine_hex_to_tet_24

def get_total_volume(pts, tets):
    vol = 0
    for t in tets:
        p = pts[t]
        vol += np.abs(np.dot(p[1]-p[0], np.cross(p[2]-p[0], p[3]-p[0]))) / 6.0
    return vol

def test_conversions():
    print("Starting Mesh Conversion Tests...")
    
    # 1. Initial Tetrahedron
    pts_tet = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    ])
    tets = np.array([[0, 1, 2, 3]])
    initial_vol = get_total_volume(pts_tet, tets)
    print(f"Step 1: Initial Tet Volume = {initial_vol:.6f}")

    # 2. Tet to Hex (1 Tet -> 4 Hexes)
    pts_hex, hexes = refine_tet_to_hex(pts_tet, tets)
    print(f"Step 2: Refined to {len(hexes)} Hexes. Total Points: {len(pts_hex)}")
    
    # Check hex volume (approximate using the same logic as in tet2hex test)
    # Since we don't have a direct hex_volume here, we'll use the conversion to tets to check
    
    # 3. Hex to Tet (6-Tet decomposition)
    # 4 Hexes * 6 Tets/Hex = 24 Tets
    pts_tet6, tets6 = hex_to_tet_6(pts_hex, hexes)
    vol6 = get_total_volume(pts_tet6, tets6)
    print(f"Step 3: Hex to 6-Tet decomposition. Total Tets: {len(tets6)}, Volume: {vol6:.6f}")
    assert np.allclose(initial_vol, vol6), f"Volume mismatch in 6-Tet! {initial_vol} != {vol6}"

    # 4. Hex to Tet (24-Tet refinement)
    # 4 Hexes * 24 Tets/Hex = 96 Tets
    pts_tet24, tets24 = refine_hex_to_tet_24(pts_hex, hexes)
    vol24 = get_total_volume(pts_tet24, tets24)
    print(f"Step 4: Hex to 24-Tet refinement. Total Tets: {len(tets24)}, Volume: {vol24:.6f}")
    assert np.allclose(initial_vol, vol24), f"Volume mismatch in 24-Tet! {initial_vol} != {vol24}"

    print("\nAll tests passed successfully!")
    print(f"Final Summary:")
    print(f"  - Tet -> Hex (4x) conversion: OK")
    print(f"  - Hex -> Tet (6x) conversion: OK")
    print(f"  - Hex -> Tet (24x) conversion: OK")
    print(f"  - Volume Conservation: Verified (Target: {initial_vol:.6f})")

if __name__ == "__main__":
    test_conversions()
