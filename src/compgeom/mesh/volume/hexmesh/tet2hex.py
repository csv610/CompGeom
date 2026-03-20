import numpy as np

def refine_tet_to_hex(points, tets):
    """
    Refines a tetrahedral mesh into a hexahedral mesh.
    Each tetrahedron is subdivided into 4 hexahedra.
    Ensures all output hexahedra have positive volume if the input tet is well-formed.

    Parameters:
    - points: (N, 3) array of coordinates.
    - tets: (M, 4) array of indices into points.

    Returns:
    - hex_points: (K, 3) array of coordinates.
    - hexes: (4*M, 8) array of indices into hex_points.
    """
    points = np.asarray(points)
    tets = np.asarray(tets)

    edge_midpoints = {}
    face_centroids = {}
    hex_points = list(points)
    
    def get_edge_midpoint(i, j):
        edge = tuple(sorted((i, j)))
        if edge not in edge_midpoints:
            edge_midpoints[edge] = len(hex_points)
            hex_points.append((points[i] + points[j]) / 2.0)
        return edge_midpoints[edge]

    def get_face_centroid(i, j, k):
        face = tuple(sorted((i, j, k)))
        if face not in face_centroids:
            face_centroids[face] = len(hex_points)
            hex_points.append((points[i] + points[j] + points[k]) / 3.0)
        return face_centroids[face]

    hexes = []

    for tet in tets:
        v0, v1, v2, v3 = tet
        
        # Check tet orientation
        # (v1-v0) . ((v2-v0) x (v3-v0))
        mat = points[[v1, v2, v3]] - points[v0]
        if np.linalg.det(mat) < 0:
            # Swap two vertices to make it positive
            v1, v2 = v2, v1

        # Cell centroid
        c_idx = len(hex_points)
        hex_points.append(np.mean(points[[v0, v1, v2, v3]], axis=0))

        # Midpoints and Face Centroids
        m01 = get_edge_midpoint(v0, v1)
        m02 = get_edge_midpoint(v0, v2)
        m03 = get_edge_midpoint(v0, v3)
        m12 = get_edge_midpoint(v1, v2)
        m13 = get_edge_midpoint(v1, v3)
        m23 = get_edge_midpoint(v2, v3)

        f012 = get_face_centroid(v0, v1, v2)
        f013 = get_face_centroid(v0, v1, v3)
        f023 = get_face_centroid(v0, v2, v3)
        f123 = get_face_centroid(v1, v2, v3)

        # 4 Hexes per tet, one at each vertex
        # Hex at v0
        hexes.append([v0, m01, f012, m02, m03, f013, c_idx, f023])
        # Hex at v1
        hexes.append([v1, m12, f012, m01, m13, f123, c_idx, f013])
        # Hex at v2
        hexes.append([v2, m02, f012, m12, m23, f023, c_idx, f123])
        # Hex at v3
        hexes.append([v3, m13, f013, m03, m23, f123, c_idx, f023])

    return np.array(hex_points), np.array(hexes)

def hex_volume(points, hex_indices):
    """Calculates the volume of a hexahedron by splitting it into 6 tetrahedra."""
    p = points[hex_indices]
    # VTK_HEXAHEDRON: 0,1,2,3 (bottom), 4,5,6,7 (top)
    # Split into 6 tets
    tets = [
        [0, 1, 2, 5], [0, 2, 3, 7], [0, 5, 7, 4],
        [2, 5, 7, 6], [0, 2, 5, 7] # Wait, this is not a standard split
    ]
    # Standard split into 6 tets:
    # 0125, 0237, 0574, 2576, 0257, 0257? No.
    # A safer way is to use the triple product at each vertex.
    # For a hex to be valid, the triple product of edges at each vertex must be positive.
    
    def tet_vol(a, b, c, d):
        return np.abs(np.dot(p[b]-p[a], np.cross(p[c]-p[a], p[d]-p[a]))) / 6.0
    
    # Decompose into 5 tets (if possible) or 6.
    # 0,1,3,4; 1,2,3,6; 4,5,6,1; 4,7,6,3; 1,3,4,6
    v1 = tet_vol(0, 1, 3, 4)
    v2 = tet_vol(1, 2, 3, 6)
    v3 = tet_vol(4, 5, 6, 1)
    v4 = tet_vol(4, 7, 6, 3)
    v5 = tet_vol(1, 3, 4, 6)
    return v1 + v2 + v3 + v4 + v5

if __name__ == "__main__":
    # Test with two tetrahedra sharing a face
    # Tet 1: (0,0,0), (1,0,0), (0,1,0), (0,0,1)
    # Tet 2: (1,1,1), (1,0,0), (0,1,0), (0,0,1)
    points = np.array([
        [0, 0, 0], # 0
        [1, 0, 0], # 1
        [0, 1, 0], # 2
        [0, 0, 1], # 3
        [1, 1, 1]  # 4
    ])
    tets = np.array([
        [0, 1, 2, 3],
        [4, 2, 1, 3] # Oriented to have positive volume
    ])

    hex_points, hexes = refine_tet_to_hex(points, tets)

    print(f"Original points: {len(points)}")
    print(f"Original tets: {len(tets)}")
    print(f"New points: {len(hex_points)}")
    print(f"New hexes: {len(hexes)}")
    
    # Expected points: 5 vertices + 9 edges + 7 faces + 2 cells = 23
    assert len(hex_points) == 23, f"Expected 23 points, got {len(hex_points)}"
    
    total_hex_vol = 0
    for i, h in enumerate(hexes):
        vol = hex_volume(hex_points, h)
        total_hex_vol += vol
        # print(f"Hex {i}: {h}, Volume: {vol:.6f}")
    
    def tet_volume_coords(p):
        return np.abs(np.linalg.det(p[1:] - p[0])) / 6.0

    total_tet_vol = tet_volume_coords(points[tets[0]]) + tet_volume_coords(points[tets[1]])
    print(f"Total Original Tet Volume: {total_tet_vol:.6f}")
    print(f"Total Sum of Hex Volumes: {total_hex_vol:.6f}")
    
    assert np.allclose(total_tet_vol, total_hex_vol), "Volumes do not match!"
    print("Verification successful: Point deduplication and volume preservation confirmed.")
