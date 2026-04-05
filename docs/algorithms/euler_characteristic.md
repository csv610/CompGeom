# Euler Characteristic

## 1. Overview
The Euler characteristic ($\chi$) is a topological invariant, a number that describes a topological space's shape or structure regardless of the way it is bent or twisted. For a 3D surface mesh (a polyhedral surface), it relates the number of vertices ($V$), edges ($E$), and faces ($F$). It is a fundamental tool for classifying surfaces and verifying the topological integrity of meshes.

## 2. Definitions
*   **Euler Formula**: For a convex polyhedron (topologically equivalent to a sphere), $\chi = V - E + F = 2$.
*   **Genus (g)**: The number of "handles" or "holes" through a surface (e.g., a torus has $g=1$, a sphere has $g=0$).
*   **Boundary Components (b)**: The number of connected boundary loops in a mesh.
*   **Topological Invariant**: A property that remains unchanged under continuous deformation (homeomorphism).

## 3. Theory
For a general connected orientable surface, the Euler characteristic is related to its genus and boundary count by the formula:
$$\chi = V - E + F = 2 - 2g - b$$
This allows us to determine the global topology of a mesh simply by counting its elements:
*   **Sphere**: $V - E + F = 2$ ($g=0, b=0$).
*   **Disk**: $V - E + F = 1$ ($g=0, b=1$).
*   **Torus**: $V - E + F = 0$ ($g=1, b=0$).
*   **Cylinder**: $V - E + F = 0$ ($g=0, b=2$).

The Gauss-Bonnet theorem further relates the Euler characteristic to the total curvature of the surface: $\int_M K dA = 2\pi \chi$. In the discrete case, this means the sum of angle defects at all vertices is exactly $2\pi \chi$.

## 4. Pseudo code
```python
function CalculateEulerCharacteristic(mesh):
    # 1. Count elements
    V = len(mesh.vertices)
    F = len(mesh.faces)
    
    # 2. Extract unique edges
    edges = set()
    for face in mesh.faces:
        for i in range(len(face)):
            v1 = face[i]
            v2 = face[(i+1) % len(face)]
            edges.add(tuple(sorted((v1, v2))))
    E = len(edges)
    
    # 3. Apply Euler formula
    chi = V - E + F
    
    # 4. Infer Genus (assuming orientable, connected, no boundaries)
    # g = (2 - chi) / 2
    
    return chi
```

## 5. Parameters Selections
*   **Element Counting**: Ensure that duplicate vertices or edges are correctly merged before counting, as they will artificially deflate/inflate $\chi$.
*   **Component Handling**: If the mesh has $C$ disconnected components, the formula becomes $\chi = V - E + F = 2C - 2g - b$.

## 6. Complexity
*   **Time Complexity**: $O(F)$, where $F$ is the number of faces, to iterate through the mesh and identify unique edges.
*   **Space Complexity**: $O(E)$ to store the set of unique edges.

## 7. Usages
*   **Mesh Verification**: Detecting if a mesh has unexpected holes or disconnected parts.
*   **Surface Classification**: Automatically determining if a scanned object is a "donut" (torus) or a "ball" (sphere).
*   **Topology-Preserving Operations**: Ensuring that operations like mesh simplification or remeshing do not change the number of holes in the model.
*   **Shape Matching**: Using $\chi$ as a fast, first-pass filter to distinguish between objects with different topologies.
*   **Theoretical Physics**: Used in string theory and condensed matter physics to classify manifold structures.

## 8. Testing methods and Edge cases
*   **Platonic Solids**: Verify that the Tetrahedron, Cube, Octahedron, Dodecahedron, and Icosahedron all yield $\chi = 2$.
*   **Open Meshes**: A single triangle has $V=3, E=3, F=1 \Rightarrow \chi=1$ (a disk).
*   **Disconnected Parts**: A mesh consisting of two separate spheres should have $\chi = 4$.
*   **Non-Orientable Surfaces**: For a Möbius strip, $\chi = 0$ ($V-E+F = 0$, $g_{non-orient}=1, b=1$).
*   **Non-Manifold Edges**: Ensure the edge counting logic correctly handles edges shared by 3+ faces (though the standard formula is defined for 2-manifolds).

## 9. References
*   Euler, L. (1758). "Elementa doctrinae solidorum". Novi Commentarii Academiae Scientiarum Petropolitanae.
*   Poincaré, H. (1895). "Analysis situs". Journal de l'École Polytechnique.
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   Wikipedia: [Euler characteristic](https://en.wikipedia.org/wiki/Euler_characteristic)
