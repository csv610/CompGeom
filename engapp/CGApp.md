# Educational Guide: Computational Geometry Applications (CGApp)

Welcome, students! This guide explores how abstract geometric principles are applied to solve complex problems in engineering, science, and design. Each application below uses the `compgeom` library's core primitives: `Point3D` and `TriangleMesh`.

---

## Part 1: Manufacturing & Industrial Design

### 1. Additive Manufacturing (`additive_mfg.py`)
**The Problem**: 3D printers cannot print in thin air; they need "supports" for overhanging parts.
*   **Geometric Principle (Face Normal Analysis)**: Every triangle in a mesh has a "normal" vector $(\vec{n})$ pointing outward. We compare this to the gravity vector $(\vec{g} = [0, 0, -1])$ using the **Dot Product**: $\cos(\theta) = \vec{n} \cdot \vec{g}$.
*   **Thresholding**: If the angle $\theta$ is greater than a threshold (e.g., 45°), the face is an "overhang."
*   **Optimal Orientation (Quaternion Sampling)**: The number of supports depends heavily on the object's orientation. We use **Quaternion Sampling** to randomly rotate the mesh and find the orientation that minimizes the total number of overhang faces.
*   **Structural Stability**: To prevent heavy structures from being printed above thin, unstable ones, we also optimize for **"Bottom-Heavy"** orientations. By minimizing the **Area-Weighted Average Height** (the Z-centroid of the surface), we ensure the object's bulk is as close to the print bed as possible, reducing bending and support requirements.
*   **Metrics**: We use the mesh's **Bounding Box** ($Z_{max} - Z_{min}$) to calculate the number of layers, which combined with **Total Surface Area**, allows us to estimate material volume and print time.

### 2. Drafting & Mold Analysis (`drafting_tools.py`)
**The Problem**: To remove a part from a physical mold, its sides must be slightly tapered (the "Draft Angle").
*   **Geometric Principle (Draft Analysis)**: Similar to 3D printing, we analyze the angle between face normals and the "Pull Direction" of the mold. Faces with a 0° or negative angle are "trapped" and would break the mold.
*   **Silhouette Edges**: These are the edges where the part's visibility "turns the corner." We find them by identifying edges shared by two triangles where one face points toward the viewer ($\vec{n}_1 \cdot \vec{v} > 0$) and the other points away ($\vec{n}_2 \cdot \vec{v} < 0$).

### 3. Metrology & Quality Control (`metrology_tools.py`)
**The Problem**: Sensors like LIDAR produce "noisy" point clouds. How do we find a perfectly flat plane in a mess of points?
*   **Geometric Principle (RANSAC)**: Random Sample Consensus is a robust iterative algorithm.
    1.  **Sample**: Pick 3 random points (the minimum needed to define a plane).
    2.  **Model**: Calculate the plane equation $ax + by + cz + d = 0$.
    3.  **Validate**: Count how many other points lie within a small distance $\epsilon$ of this plane (the "Inliers").
    4.  **Iterate**: Repeat many times and keep the plane with the most inliers.

---

## Part 2: Engineering & Simulation

### 4. Aerospace & Planetary Geometry (`aerospace_geometry.py`)
**The Problem**: Navigation on Earth requires converting flat Latitude/Longitude to 3D $X, Y, Z$ coordinates.
*   **Geometric Principle (Ellipsoid Projection)**: The Earth isn't a sphere; it's an **Oblate Spheroid**. We use the WGS84 model which involves semi-major and semi-minor axes.
*   **Rotational Stability**: We calculate the **Inertia Tensor** (a 3x3 matrix representing mass distribution). By finding the **Eigenvalues** of this matrix, we determine the principal axes of rotation. A spacecraft is only stable rotating around its "Major" (maximum inertia) or "Minor" (minimum) axes—the "Intermediate" axis is unstable!

### 5. Computational Fluid Dynamics (`cfd_analysis.py`)
**The Problem**: Aerodynamic drag depends on the "shadow" an object casts against the wind.
*   **Geometric Principle (Projected Area)**: We project all triangles onto a plane perpendicular to the flow direction. This is essentially a 2D **Polygon Union** problem. The sum of these non-overlapping areas gives the "Frontal Area" used in the drag equation: $F_d = \frac{1}{2} \rho v^2 C_d A$.

### 6. Radar Engineering (`radar_engineering.py`)
**The Problem**: How "visible" is a stealth aircraft to radar?
*   **Geometric Principle (Visibility & Backscattering)**: Radar waves travel in straight lines. We use **Ray Casting** from the radar source. If a ray hits a face, we check the angle. If the face normal points directly back at the source, the "Radar Cross Section" (RCS) is high. We ignore "Back Faces" ($\vec{n} \cdot \vec{ray} > 0$) because they are occluded.

### 7. Solar & Urban Analysis (`solar_analysis.py`)
**The Problem**: How do we design energy-efficient cities that maximize solar gain while minimizing heat islands?
*   **Geometric Principle (Sun Position & Vector Analysis)**: The sun's position changes every minute. We calculate the **Solar Elevation** ($\alpha$) and **Azimuth** ($\psi$) based on the Earth's **Declination** (tilt) for any day of the year. This gives us a time-varying **Sun Vector** $(\vec{s})$.
*   **Sky View Factor (SVF)**: This measures how much "open sky" a point can see. We use **Fibonacci Sphere Sampling** to cast hundreds of rays in a hemisphere around a point. If 80% of rays escape into space without hitting a building, the SVF is 0.8. Low SVF leads to "Urban Heat Islands" because heat gets trapped.
*   **Cumulative Radiation**: By integrating the **Dot Product** ($\vec{n} \cdot \vec{s}$) over every hour of the year and accounting for **Shadowing** (occlusion), we calculate the total energy (Wh/m²) a roof or facade can collect for solar panels.

---

## Part 3: Specialized Sciences

### 8. Medical Device Design (`medical_device.py`)
**The Problem**: Designing stents that must expand inside a cylindrical artery.
*   **Geometric Principle (Cylindrical Mapping)**: We define a pattern in 2D ($u, v$) and wrap it around a cylinder using: $x = r \cos(u)$, $y = r \sin(u)$, $z = v$.
*   **Porosity**: Calculated by comparing the volume of the 3D-printed lattice structure to the total volume of the bounding cylinder. This ensures the device allows enough blood flow.

### 9. Molecular Geometry (`molecular_geometry.py`)
**The Problem**: How do drugs "dock" into a protein?
*   **Geometric Principle (SAS & Pockets)**: We treat every atom as a sphere. The **Solvent Accessible Surface** (SAS) is the boundary traced by a "probe" sphere (representing water) rolling over the atoms.
*   **Pocket Detection**: We use **Skeletonization**. By "eroding" the volume of the protein, the last points to disappear represent the "centers" or "medial axis" of the protein's shape. Deep cavities (pockets) are where drug molecules can bind.

### 10. Robotics & Path Planning (`robotics_geometry.py`)
**The Problem**: A robot needs to find the shortest path from A to B while avoiding obstacles.
*   **Geometric Principle (Configuration Space)**: We "inflate" obstacles by the robot's radius to treat the robot as a single point.
*   **Visibility Graphs**: We connect the start, the end, and all visible vertices of the obstacles. Finding the shortest path in this graph using **Dijkstra's Algorithm** gives the optimal collision-free path.

### 11. Swarovski Crystal Generation (`swarovski_crystals.py`)
**The Problem**: Converting a 'raw' (noisy/organic) gemstone mesh into a precision-cut crystal.
*   **Geometric Principle (Convex Hull & Facetting)**: A perfect crystal is a convex polyhedron with large, planar facets.
    1.  **Symmetry**: We mirror the raw points across principal planes (e.g., $XY, YZ$) to ensure a balanced cut.
    2.  **Convexity**: We compute the **Convex Hull** of these symmetric points to get the base gemstone shape.
    3.  **Facetting (Decimation)**: By simplifying the hull to a target number of faces, we create the signature "faceted" look of a crystal.
    4.  **Corner Rounding**: Using **Taubin Smoothing**, we round off sharp vertices and edges to make the crystal safer to handle and more aesthetically pleasing while maintaining the overall faceted structure.

---

## Part 4: Core Data Structures (The "Engine")

### 12. Spatial Acceleration (`spatial_acceleration.py`)
**The Problem**: If a mesh has 1 million triangles, checking if a ray hits it would take 1 million calculations. This is too slow for real-time apps.
*   **The Solution (AABB Tree)**: We organize the triangles into a hierarchy of **Axis-Aligned Bounding Boxes**.
    *   **Divide and Conquer**: We wrap the whole mesh in one big box. Then we split it into two boxes, each containing half the triangles, and so on.
    *   **Early Exit**: When casting a ray, if the ray misses the "Parent" box, we know it misses all 1 million triangles inside. We only "traverse" into the boxes the ray actually touches, reducing the search from $O(N)$ to $O(\log N)$.
    *   **SAH (Surface Area Heuristic)**: We split the boxes in a way that minimizes the surface area of the children, making it mathematically more likely for rays to miss them, further speeding up the system.

---

## Part 5: Expanding Domains

### 13. 5G Network Planning (`telecom_propagation.py`)
**The Problem**: 5G signals are high-frequency and easily blocked by buildings. Engineers need to find the best placement for small-cell towers to maximize coverage.
*   **Geometric Principle (Fresnel Zone Analysis)**: Treat the signal as an ellipsoid between the tower and the user. 
*   **Implementation**: Use **Ray Casting** to check if any triangles in the city mesh (`TriangleMesh`) intersect the "Fresnel Zone" ellipsoid.
*   **Metric**: Calculate the **Signal-to-Interference-plus-Noise Ratio (SINR)** by analyzing the "Line-of-Sight" (LoS) percentage across a grid of points.

### 14. Wildfire Spread Simulation (`wildfire_modeling.py`)
**The Problem**: Predicting how a fire will climb a mountain is critical for evacuation. Fire moves faster uphill due to pre-heating.
*   **Geometric Principle (Slope and Aspect Analysis)**: For every face in a terrain mesh, calculate its **Steepest Descent Vector**.
*   **Implementation**: Use the **Face Normal** $(\vec{n})$ to find the slope angle. A fire's "Rate of Spread" (ROS) is then adjusted using a vector dot product between the wind vector $(\vec{w})$ and the face's uphill vector.
*   **Metric**: Generate a **Heatmap** on the `TriangleMesh` where color represents the time it takes for the fire front to reach that specific triangle.

### 15. Acoustic Room Treatment (`acoustic_raytracing.py`)
**The Problem**: Architects need to place sound-absorbing panels to prevent "echo chambers" in large halls or recording studios.
*   **Geometric Principle (Specular Reflection)**: When a sound ray hits a wall, it reflects at the same angle: $\vec{r} = \vec{d} - 2(\vec{d} \cdot \vec{n})\vec{n}$.
*   **Implementation**: Use recursive **Ray Tracing**. For a sound source point, cast rays in all directions. Track each ray as it bounces off the `TriangleMesh` faces. 
*   **Metric**: Calculate **Reverberation Time (RT60)** by measuring how long it takes for the ray energy to decay. Identify "Hot Spots" where many reflected rays converge.

### 16. Marine Archaeology & Shipwreck Mapping (`bathymetric_reconstruction.py`)
**The Problem**: Sonar data from shipwrecks is often "holey" and noisy. We need to reconstruct a watertight 3D model from sonar pings.
*   **Geometric Principle (Poisson Surface Reconstruction)**: Converting a sparse point cloud into a smooth, continuous surface.
*   **Implementation**: Use the **Point3D** pings to create a **Signed Distance Function (SDF)**. Then, use the **Marching Cubes** algorithm to extract the 0-level isosurface as a new `TriangleMesh`.
*   **Metric**: Calculate the **Estimated Displaced Volume** of the wreck to guess the original weight/size of the vessel.
