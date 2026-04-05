# Distance Map (Distance Transform)

## 1. Overview
A distance map (or distance transform) is a representation of a digital image or geometric scene where each point stores its distance to the nearest boundary or obstacle. For a binary image, the distance map calculates the distance from every background pixel to the closest foreground pixel. It is a fundamental tool in image processing, computer vision, and motion planning.

## 2. Definitions
*   **Distance Transform (DT)**: An operator applied to binary images that produces a grayscale image where pixel values represent distance.
*   **Signed Distance Function (SDF)**: A variation where points inside a shape have negative distances and points outside have positive distances.
*   **Euclidean Distance Map (EDM)**: A map where distances are calculated using the true Euclidean metric $\sqrt{\Delta x^2 + \Delta y^2}$.
*   **Manhattan/Chamfer Distance**: Approximations of Euclidean distance using integer steps (e.g., 3-4 chamfer or 5-7-11 chamfer).

## 3. Theory
The most efficient algorithms for computing the Euclidean distance map are based on **separable filters** or **two-pass scanning**.

1.  **Chamfer Matching (Two-Pass)**: A simple algorithm that passes a small mask over the image twice (top-to-bottom and bottom-to-top). Each pixel is updated using the values of its neighbors plus the mask weight.
2.  **Meijster's Algorithm (Separable)**: A more accurate $O(N)$ algorithm that decomposes the 2D problem into 1D problems. First, it computes the distance transform for each row. Then, it uses the row results to compute the final 2D distances using a parabolic lower envelope approach.
3.  **Fast Marching Method**: Can also be used to build a distance map by treating the boundary as a wave front propagating at unit speed.

## 4. Pseudo code
### Meijster's Algorithm (1D Pass)
```python
function DistanceMap2D(binary_grid):
    width, height = grid.size
    
    # 1. Row Pass: Compute 1D distance to nearest foreground pixel in each row
    G = array[width][height]
    for y in range(height):
        for x in range(width):
            if grid[x][y] == FOREGROUND:
                G[x][y] = 0
            else:
                G[x][y] = infinity
                
        # Forward and backward scans for 1D distance
        for x in range(1, width):
            G[x][y] = min(G[x][y], G[x-1][y] + 1)
        for x in range(width-2, -1, -1):
            G[x][y] = min(G[x][y], G[x+1][y] + 1)
            
    # 2. Column Pass: Compute 2D distance using parabolic lower envelope
    final_map = array[width][height]
    for x in range(width):
        final_map[x] = ComputeParabolicEnvelope(G[x])
        
    return sqrt(final_map) # Return actual Euclidean distance
```

## 5. Parameters Selections
*   **Metric**: Choose between Euclidean (accurate), Manhattan (fast), or Chebyshev (fast) based on the application's needs.
*   **Sign**: Decide if an SDF is needed (requires identifying "inside" vs. "outside").

## 6. Complexity
*   **Time Complexity**: $O(N)$, where $N$ is the total number of pixels/grid points, using Meijster's or Felzenszwalb's algorithm.
*   **Space Complexity**: $O(N)$ to store the distance values.

## 7. Usages
*   **Robotics**: Path planning using the "Artificial Potential Field" method (moving away from high-distance regions).
*   **Image Processing**: Skeletonization (medial axis extraction) and morphological thinning.
*   **Computer Graphics**: Rendering anti-aliased text and icons using Signed Distance Fields (SDF fonts).
*   **Computer Vision**: Template matching and object recognition (Chamfer matching).
*   **Medical Imaging**: Calculating the thickness of tissues or the distance between organs.

## 8. Testing methods and Edge cases
*   **Single Point**: The distance map should look like a perfect radial gradient (concentric circles).
*   **Empty Image**: All distances should be infinity (or a defined maximum).
*   **Full Image**: All distances should be zero.
*   **Thin Lines**: Verify that the algorithm correctly identifies the closest point even for 1-pixel-wide features.
*   **Concave Shapes**: Verify that the "shadowing" effect of concavities is handled correctly.

## 9. References
*   Rosenfeld, A., & Pfaltz, J. L. (1966). "Sequential operations in digital picture processing". Journal of the ACM.
*   Meijster, A., Roerdink, J. B., & Hesselink, W. H. (2002). "A general algorithm for computing distance transforms in linear time". Mathematical Morphology and its Applications to Image and Signal Processing.
*   Felzenszwalb, P. F., & Huttenlocher, D. P. (2012). "Distance Transforms of Sampled Functions". Theory of Computing.
*   Wikipedia: [Distance transform](https://en.wikipedia.org/wiki/Distance_transform)
