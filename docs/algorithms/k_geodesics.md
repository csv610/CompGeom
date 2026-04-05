# K-Geodesics (Geodesic K-Means)

## 1. Overview
K-Geodesics is an adaptation of the K-Means clustering algorithm to the surface of a 3D mesh. Instead of using Euclidean distance to cluster points in 3D space, K-Geodesics uses **geodesic distance** (the shortest path along the surface). This allows for the segmentation of a mesh into regions that are intrinsically meaningful, such as the limbs of a character or the functional parts of a machine.

## 2. Definitions
*   **Geodesic Center (Centroid)**: The vertex on the mesh that minimizes the sum of squared geodesic distances to all other vertices in its cluster.
*   **Voronoi Region**: The set of vertices on the mesh that are closer to one specific center than to any other center, using geodesic metrics.
*   **Geodesic Distance ($d_g$)**: The shortest distance between two points restricted to the surface.

## 3. Theory
The K-Geodesics algorithm follows the standard iterative process of Lloyd's algorithm:
1.  **Initialization**: Pick $k$ initial seed vertices as centers.
2.  **Assignment**: Assign every vertex on the mesh to the cluster of its nearest center using a multi-source **Fast Marching Method** or the **Heat Method**.
3.  **Update**: For each cluster, find a new center. This is the "Fréchet mean" on the surface. Since finding the exact mean is expensive, it is often approximated by picking the vertex in the cluster that minimizes the average distance to all other cluster members.
4.  **Repeat**: Continue until the centers no longer change or a maximum number of iterations is reached.

## 4. Pseudo code
```python
function KGeodesics(mesh, k):
    # 1. Initialize k centers randomly
    centers = random.sample(mesh.vertices, k)
    
    while not converged:
        # 2. Assignment Step
        # Compute distances from all centers simultaneously
        # labels[v] = index of center closest to v
        distances, labels = MultiSourceGeodesic(mesh, centers)
        
        new_centers = []
        # 3. Update Step
        for i in range(k):
            cluster_v = [v for v, l in enumerate(labels) if l == i]
            
            # Find the vertex in cluster_v that minimizes sum of distances
            # to all other vertices in the SAME cluster
            best_v = FindLocalCentroid(mesh, cluster_v)
            new_centers.append(best_v)
            
        # 4. Check convergence
        if new_centers == centers:
            break
        centers = new_centers
        
    return labels, centers
```

## 5. Parameters Selections
*   **Number of Clusters ($k$ )**: Depends on the desired level of segmentation.
*   **Distance Solver**: The **Heat Method** is recommended for the assignment step because it is extremely fast after an initial factorization.
*   **Initialization**: Using **K-Means++** logic (picking seeds that are far from each other) significantly improves convergence speed and result quality.

## 6. Complexity
*   **Assignment**: $O(N)$ using the Heat Method or $O(N \log N)$ using Fast Marching.
*   **Update**: $O(k \cdot N_{cluster})$ to find new centers.
*   **Total**: $O(I \cdot N)$ where $I$ is the number of iterations.

## 7. Usages
*   **Mesh Segmentation**: Dividing a model into organic parts (e.g., body, head, arms).
*   **Texture Atlas Generation**: Partitioning a complex mesh into $k$ nearly-flat charts for UV unwrapping.
*   **Shape Analysis**: Identifying repeating structural motifs on a surface.
*   **Remote Sensing**: Clustering geographic regions based on travel time over terrain.
*   **Remeshing**: Using the centers as a basis for generating a coarse, high-quality version of the mesh.

## 8. Testing methods and Edge cases
*   **Convex Shapes**: For a sphere, the regions should look like a spherical Voronoi diagram.
*   **Long Thin Regions**: Verify that the algorithm correctly segments limbs (which Euclidean K-Means might merge if they are physically close but geodesically far).
*   **Number of Iterations**: Monitor the total "energy" (sum of distances) to ensure it decreases monotonically.
*   **Empty Clusters**: Handle cases where a center becomes so isolated that no vertices are assigned to it.
*   **Disconnected Components**: The algorithm should be applied to each component separately or handle infinity distances correctly.

## 9. References
*   Peyré, G., & Cohen, L. D. (2006). "Geodesic remeshing using front propagation". International Journal of Computer Vision.
*   Crane, K., Weischedel, C., & Wardetzky, M. (2013). "Geodesics in Heat: A New Approach to Computing Distance Based on Heat Flow". ACM TOG.
*   Lloyd, S. (1982). "Least squares quantization in PCM". IEEE Transactions on Information Theory.
*   Wikipedia: [K-means clustering](https://en.wikipedia.org/wiki/K-means_clustering)
