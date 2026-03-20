import numpy as np

def hex_to_tet_6(points, hexes):
    """
    Decomposes each hexahedron into 6 tetrahedra without adding new points.
    Uses a consistent diagonal (0, 6) for decomposition.
    
    VTK Hex Ordering: 0, 1, 2, 3 (bottom), 4, 5, 6, 7 (top)
    """
    tets = []
    for h in hexes:
        # 6 tets sharing the diagonal (0, 6)
        tets.append([h[0], h[1], h[2], h[6]])
        tets.append([h[0], h[2], h[3], h[6]])
        tets.append([h[0], h[3], h[7], h[6]])
        tets.append([h[0], h[7], h[4], h[6]])
        tets.append([h[0], h[4], h[5], h[6]])
        tets.append([h[0], h[5], h[1], h[6]])
    return points, np.array(tets)

def refine_hex_to_tet_24(points, hexes):
    """
    Refines each hexahedron into 24 tetrahedra by adding:
    - 1 cell centroid
    - 6 face centroids
    
    Each face (4 edges) is split into 4 triangles using the face centroid,
    and each triangle forms a tetrahedron with the cell centroid.
    """
    points = list(points)
    new_tets = []
    
    # Face indices for VTK hexahedron
    # 0: bottom (0,3,2,1), 1: top (4,5,6,7), 2: front (0,1,5,4)
    # 3: right (1,2,6,5), 4: back (2,3,7,6), 5: left (3,0,4,7)
    face_map = [
        [0, 3, 2, 1], # Bottom
        [4, 5, 6, 7], # Top
        [0, 1, 5, 4], # Front
        [1, 2, 6, 5], # Right
        [2, 3, 7, 6], # Back
        [3, 0, 4, 7]  # Left
    ]

    # Dictionary to deduplicate face centroids
    face_centroids = {}

    def get_face_centroid(indices):
        key = tuple(sorted(indices))
        if key not in face_centroids:
            face_centroids[key] = len(points)
            points.append(np.mean(np.array(points)[list(indices)], axis=0))
        return face_centroids[key]

    for h in hexes:
        h_pts = np.array(points)[h]
        cell_centroid_idx = len(points)
        points.append(np.mean(h_pts, axis=0))
        
        for f_indices in face_map:
            # Global indices of face vertices
            v = [h[i] for i in f_indices]
            f_centroid_idx = get_face_centroid(v)
            
            # 4 tets per face (one for each edge of the face)
            for i in range(4):
                v_start = v[i]
                v_end = v[(i + 1) % 4]
                # Tet: Cell Centroid, Face Centroid, Edge Start, Edge End
                new_tets.append([cell_centroid_idx, f_centroid_idx, v_start, v_end])
                
    return np.array(points), np.array(new_tets)

if __name__ == "__main__":
    # Test with a unit cube
    points = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ])
    hexes = np.array([[0, 1, 2, 3, 4, 5, 6, 7]])

    # Method 1: 6 Tets
    pts6, tets6 = hex_to_tet_6(points, hexes)
    print(f"6-Tet decomposition: {len(tets6)} tets")
    
    # Method 2: 24 Tets
    pts24, tets24 = refine_hex_to_tet_24(points, hexes)
    print(f"24-Tet refinement: {len(pts24)} points, {len(tets24)} tets")

    def get_total_volume(pts, tets):
        vol = 0
        for t in tets:
            p = pts[t]
            vol += np.abs(np.dot(p[1]-p[0], np.cross(p[2]-p[0], p[3]-p[0]))) / 6.0
        return vol

    print(f"Original Volume: 1.0")
    print(f"6-Tet Volume: {get_total_volume(pts6, tets6):.6f}")
    print(f"24-Tet Volume: {get_total_volume(pts24, tets24):.6f}")
