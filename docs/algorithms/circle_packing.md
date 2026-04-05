# Circle Packing

## 1. Overview
Circle packing is the study of placing non-overlapping circles within a given container (like a square or another circle) or on a surface (like a mesh) such that the total area of the circles is maximized or the density is optimized. In computational geometry, it is a classic problem in both optimization and discrete geometry, with applications ranging from material science to map labeling and data visualization.

## 2. Definitions
*   **Packing Density**: The ratio of the area covered by the circles to the total area of the container.
*   **Optimal Packing**: A configuration that achieves the maximum possible density for a fixed number of circles or a fixed container size.
*   **Circle Contact Graph**: A graph where each node is a circle and an edge exists between nodes if the corresponding circles touch.
*   **Hexagonal Packing**: The densest possible packing of identical circles in an infinite 2D plane, with a density of approximately $90.69\%$.

## 3. Theory
Finding the optimal packing of $n$ circles in a container is a **non-convex optimization** problem. The most common approaches are:
1.  **Greedy Placement**: Placing circles one by one at the best available position (e.g., using a "front-advancing" algorithm).
2.  **Force-Directed Layout**: Treating circles as repelling particles and using a physics simulation to find an equilibrium state where they are packed tightly.
3.  **Circle Packing on Surfaces**: Using **conformal mapping** and the **Circle Packing Theorem** (Koebe-Andreev-Thurston) to represent any planar graph as a set of tangent circles.
4.  **Vortex-based Packing**: Packing circles into a spiral or vortex to fill a circular container.

For identical circles, the hexagonal lattice is optimal in 2D. For circles of different sizes (Appollonian gaskets), the packing can achieve 100% density in the limit.

## 4. Pseudo code
### Simple Greedy Packing (into a rectangle)
```python
function GreedyCirclePacking(container, radii):
    # Sort radii to place large circles first
    radii.sort(reverse=True)
    
    placed_circles = []
    for r in radii:
        # 1. Find the best position using a candidate search
        best_p = FindCandidatePosition(container, placed_circles, r)
        
        if best_p is not None:
            placed_circles.append(Circle(best_p, r))
            
    return placed_circles

function FindCandidatePosition(container, others, r):
    # Sample many points or use a grid
    for p in SamplePoints(container):
        # 2. Check overlap with container boundary
        if not IsWithin(p, r, container): continue
        
        # 3. Check overlap with other circles
        is_overlapping = False
        for c in others:
            if Distance(p, c.p) < (r + c.r):
                is_overlapping = True
                break
        
        if not is_overlapping:
            return p
    return None
```

## 5. Parameters Selections
*   **Radii Distribution**: Can be fixed (monodisperse) or varying (polydisperse).
*   **Optimization Iterations**: In force-directed methods, more iterations lead to tighter packing but increase computation time.

## 6. Complexity
*   **Greedy Approach**: $O(n^2)$ if each placement is checked against all previous circles. This can be reduced to $O(n \log n)$ using a spatial index like a quadtree.
*   **Force-Directed**: $O(i \cdot n \log n)$ where $i$ is the number of iterations and $n$ is the number of circles.

## 7. Usages
*   **Manufacturing**: Minimizing waste when cutting circular parts from a rectangular sheet of material.
*   **Cartography**: Dorling Cartograms, where regions are represented by circles whose size is proportional to a variable (e.g., population).
*   **Data Visualization**: Packing circles into categories to represent hierarchy (e.g., D3.js circle packing).
*   **Material Science**: Modeling the structure of crystals or granular materials.
*   **Logo Design and Art**: Generative art and "bubble" patterns.

## 8. Testing methods and Edge cases
*   **Overlap Check**: Verify that no two circles have an intersection.
*   **Boundary Check**: Ensure all circles are fully within the container.
*   **Density Calculation**: Measure the final packing efficiency.
*   **Single Circle**: Should be placed in the center of the container.
*   **Radius > Container**: Should result in zero placed circles.
*   **Varying Container Shapes**: Test packing into circles, triangles, or complex polygons.

## 9. References
*   Stephenson, K. (2005). "Introduction to Circle Packing: The Theory of Discrete Analytic Functions". Cambridge University Press.
*   Koebe, P. (1936). "Kontaktprobleme der Konformen Abbildung". Berichte Sächs. Akad. Wiss. Leipzig.
*   Thurston, W. (1985). "The Finite Riemann Mapping Theorem". International Congress of Mathematicians.
*   Wikipedia: [Circle packing](https://en.wikipedia.org/wiki/Circle_packing)
