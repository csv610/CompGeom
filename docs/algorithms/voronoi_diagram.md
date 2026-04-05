# Voronoi Diagram (Delaunay Duality)

## 1. Overview
A Voronoi diagram is a fundamental partition of a plane into regions based on distance to a specific set of points, called sites. For each site, there is a corresponding region (Voronoi cell) consisting of all points closer to that site than to any other. The Voronoi diagram is the geometric dual of the Delaunay triangulation, a property that allows for efficient construction.

## 2. Definitions
*   **Voronoi Site**: One of the input points used to define the diagram.
*   **Voronoi Cell**: A convex polygon associated with a site, containing all points in the plane for which that site is the nearest neighbor.
*   **Voronoi Vertex**: A point where three or more Voronoi cells meet; it is the circumcenter of a Delaunay triangle.
*   **Voronoi Edge**: The boundary between two adjacent Voronoi cells; it lies on the perpendicular bisector of the segment connecting the two sites.

## 3. Theory
The duality between the Delaunay triangulation (DT) and the Voronoi diagram (VD) is the most common way to compute the latter:
1.  Each **vertex** in the DT corresponds to a **cell** in the VD.
2.  Each **triangle** in the DT corresponds to a **vertex** in the VD (its circumcenter).
3.  Each **edge** in the DT corresponds to an **edge** in the VD (the perpendicular bisector).

By constructing the DT first, we can find the Voronoi vertices and connect them in the correct order to form the boundaries of the Voronoi cells.

## 4. Pseudo code
```python
function ComputeVoronoi(sites, bounding_box):
    # 1. Compute Delaunay Triangulation
    DT = DelaunayTriangulation(sites)
    
    # 2. Map triangles to their circumcenters (Voronoi vertices)
    Circumcenters = {}
    for T in DT.triangles:
        Circumcenters[T] = CalculateCircumcenter(T.v1, T.v2, T.v3)
        
    # 3. Build cells for each site
    VoronoiCells = []
    for site in sites:
        # Find triangles sharing this vertex (site)
        Star = FindTrianglesSharingVertex(site, DT)
        # Sort triangles in CCW order around the site
        SortedStar = SortAround(site, Star)
        # Sequence of circumcenters forms the cell boundary
        CellBoundary = [Circumcenters[T] for T in SortedStar]
        
        # 4. Clip the cell against the bounding box
        ClippedCell = ClipPolygon(CellBoundary, bounding_box)
        VoronoiCells.append(ClippedCell)
        
    return VoronoiCells
```

## 5. Parameters Selections
*   **Bounding Box**: Essential for "capping" the infinite cells belonging to sites on the convex hull.
*   **Precision**: Circumcenter calculations can be sensitive to nearly collinear sites; robust geometric predicates are recommended.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$, which is the complexity of building the Delaunay triangulation. The extraction of the Voronoi diagram from the triangulation is $O(n)$.
*   **Space Complexity**: $O(n)$ to store both the triangulation and the resulting Voronoi cells.

## 7. Usages
*   **Facility Location**: Determining the optimal placement of a new service center (e.g., a hospital or cell tower).
*   **Robotics**: Path planning (staying as far away from obstacles as possible by following Voronoi edges).
*   **Biology/Ecology**: Modeling territory of animals or growth patterns of cells.
*   **Data Science**: K-nearest neighbors search and clustering.

## 8. Testing methods and Edge cases
*   **Sites on Convex Hull**: These cells are naturally open/infinite and require clipping.
*   **Co-circular Sites**: Four or more points on a circle results in a single Voronoi vertex shared by more than three cells.
*   **Collinear Sites**: Result in parallel perpendicular bisectors; the Delaunay triangulation may be degenerate.
*   **Duplicate Sites**: Should be merged or handled to avoid zero-area triangles.

## 9. References
*   Voronoi, G. (1908). "Nouvelles applications des paramètres continus à la théorie des formes quadratiques". Journal für die reine und angewandte Mathematik.
*   Fortune, S. (1987). "A sweepline algorithm for Voronoi diagrams". Algorithmica.
*   Aurenhammer, F. (1991). "Voronoi Diagrams: A Survey of a Fundamental Geometric Data Structure". ACM Computing Surveys.
*   [Wikipedia: Voronoi diagram](https://en.wikipedia.org/wiki/Voronoi_diagram)
