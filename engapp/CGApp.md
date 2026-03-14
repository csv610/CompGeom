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

### 17. Surgical Planning & Robotics (`surgical_planning.py`)
**The Problem**: In robotic surgery, a drill or needle must reach a target without hitting critical "No-Go" zones like nerves or major blood vessels.
*   **Geometric Principle (Segment-to-Mesh Distance)**: We treat the surgical instrument as a **Line Segment** and the critical anatomy as a **TriangleMesh**. 
*   **Implementation**: For every vertex in the critical mesh, we calculate the shortest distance to the line segment. If the distance falls below a **Safety Margin** (e.g., 2mm), the path is flagged as dangerous.
*   **Surface Mapping**: For robotic navigation, we project the instrument's tip position onto the bone surface to find the **Closest Normal**, allowing the robot to remain perfectly perpendicular to the surface during drilling.

### 18. Orthopedic Knee Alignment (`knee_surgery_alignment.py`)
**The Problem**: In Total Knee Arthroplasty (TKA), the long-term success of the implant depends on achieving a perfect "Mechanical Axis."
*   **Geometric Principle (Vector Alignment)**: We define the **Mechanical Axis** as the 3D line connecting the center of the hip (femoral head) and the center of the knee. 
*   **Resection Planes**: Using the mechanical axis, we define a **Resection Plane** (ax + by + cz + d = 0) where the bone will be cut. This plane is typically adjusted by a **Valgus Angle** (e.g., 6°) to account for the patient's specific anatomy.
*   **Gap Analysis**: By calculating the distance from the furthest points on the bone mesh to the planned resection plane, we can estimate exactly how many millimeters of bone will be removed, ensuring the implant fits perfectly.

### 19. Neurosurgery Burr Hole Planning (`neurosurgery_burr_hole.py`)
**The Problem**: A burr hole is a precise opening drilled in the skull. If the drill is not perfectly perpendicular to the curved skull surface, the drill bit can "skate" or slip, causing trauma.
*   **Geometric Principle (Surface Normals)**: We calculate the **Vertex Normal** at the intended entry point by averaging the normals of all surrounding triangles. This defines the ideal drilling trajectory.
*   **Angle Validation**: Using the **Dot Product**, we ensure the planned drill vector $(\vec{d})$ is within a strict tolerance (e.g., < 15°) of the surface normal $(\vec{n})$.
*   **Volumetric Modeling**: By treating the burr as a **Cylinder**, we estimate the volume of bone removed based on the radius and local skull thickness, aiding in post-operative healing analysis.

### 20. Robotic Extraction & C-Space (`robotics_extraction.py`)
**The Problem**: A robot needs to extract an object from a tight, cluttered environment (like a narrow gap) without colliding with any obstacles.
*   **Geometric Principle (Configuration Space)**: We simplify the object into a single **Reference Point** and expand all obstacles by the object's geometry (radius). This transformed space is the **C-Space**.
*   **Passability Analysis**: By analyzing the narrowest gap in the mesh, we calculate the **C-Space Clearance** ($Width - 2 \times Radius$). If the clearance is negative, the object is physically "trapped."
*   **Path Validation**: We sample points along an extraction trajectory and ensure that every point maintains a minimum distance (the object's radius) from all obstacle vertices, ensuring a collision-free extraction.

### 21. Deployable Space Structures (`deployable_structures.py`)
**The Problem**: Spacecraft like the James Webb Space Telescope need massive solar panels or mirrors, but rockets have very tight cargo fairings. Large structures must be folded for launch and autonomously deployed in space.
*   **Geometric Principle (Origami Kinematics)**: Using patterns like the **Miura-ori** fold, a flat surface is tessellated into identical parallelograms. This rigid origami pattern allows the entire structure to expand or contract simultaneously using only one degree of freedom (the fold angle $\theta$).
*   **Implementation**: By solving the spherical trigonometry equations for a degree-4 vertex, we calculate the exact 3D coordinates $(X, Y, Z)$ of every fold node as a function of $\theta$.
*   **Metric**: We calculate the **Packing Ratio**, which is the total deployed surface area divided by the 2D projected footprint of the packed structure. A higher ratio means a larger panel can fit inside the same rocket.

### 23. VLSI Chip Wire Routing (`chip_wire_routing.py`)
**The Problem**: In microchip design, millions of transistors must be connected by wires. These wires cannot overlap on the same layer and should be as short as possible to reduce signal delay and power consumption.
*   **Geometric Principle (Manhattan Geometry)**: Wires are constrained to a **Rectilinear Grid** (horizontal and vertical movements only). 
*   **A* Pathfinding**: We use the **A* Search Algorithm** with a **Manhattan Distance** ($|x_1 - x_2| + |y_1 - y_2|$) heuristic to find the shortest collision-free path between two pins.
*   **Via Optimization**: Changing layers (using a "Via") is electrically expensive. Our algorithm adds a **Via Cost** to the pathfinding logic to minimize vertical transitions between metal layers.
*   **Congestion Analysis**: By tracking wire density across the grid, we identify "Hot Spots" where the chip is too crowded, helping engineers redesign the component placement.

### 24. Indoor WiFi Placement (`wifi_placement_optimizer.py`)
**The Problem**: WiFi signals are weakened by distance and blocked by physical obstacles like walls. To ensure whole-home coverage, a router must be placed where it has the best "geometric reach" to all rooms.
*   **Geometric Principle (Signal Attenuation)**: We model signal strength using the **Inverse Square Law** for distance and a constant **Attenuation Factor** for every wall the signal passes through.
*   **Line-of-Sight (LoS) Sampling**: We use **Ray Casting** to count the number of triangles in the building mesh (`TriangleMesh`) that intersect the path between the router and a target point.
*   **Coverage Optimization**: By sampling a grid of candidate locations and calculating the average signal strength (dBm) across all rooms, we identify the mathematically optimal router position to eliminate "dead zones."

### 25. Precision Viticulture (`precision_viticulture.py`)
**The Problem**: Drones are used to monitor vine health in large vineyards. To get high-resolution multi-spectral data, the drone must maintain a perfectly constant altitude above the ground, even on steep hillsides.
*   **Geometric Principle (Barycentric Interpolation)**: We find the triangle in the terrain mesh (`TriangleMesh`) directly below the drone's 2D position. We then use **Barycentric Coordinates** to interpolate the exact ground elevation ($Z$) at that point.
*   **Terrain-Following**: By adding the desired survey altitude to the interpolated ground height, we generate a 3D flight path that follows the contours of the land.
*   **FOV Projection**: We calculate the ground "footprint" of the drone's camera based on its 3D altitude and Field of View (FOV) angle, ensuring total coverage of the crop.

### 26. Smart City Visibility (`smart_city_visibility.py`)
**The Problem**: City planners need to place streetlights or security cameras to maximize coverage while minimizing "blind spots" caused by buildings and urban structures.
*   **Geometric Principle (Line-of-Sight)**: We treat the light source as an observer point and the city as a 3D mesh.
*   **Implementation**: Using **Ray Casting** (Moller-Trumbore), we test the visibility from the light to a grid of sample points on the ground. If a ray intersects any building triangle before reaching the ground, that point is in "Shadow."
*   **Illumination Score**: By sampling hundreds of points, we calculate a coverage percentage for different placement candidates, allowing for mathematically optimal streetlight positioning.

### 27. Radiation Oncology (`radiation_oncology.py`)
**The Problem**: In cancer treatment, radiation beams must be aimed at a tumor while avoiding vital organs. Because radiation is absorbed as it travels, doctors must calculate the exact "Tissue Depth" the beam penetrates.
*   **Geometric Principle (Ray-Mesh Intersection)**: We treat the radiation beam as a **Ray** and the patient's anatomy as multiple **TriangleMeshes**.
*   **Dose Calculation**: By intersecting the ray with the "Body Skin" mesh, we calculate the distance from the skin to the tumor center.
*   **Safety Interlock**: We perform an intersection test with "Organs-at-Risk" (OAR) meshes. If the ray hits an OAR mesh before or after the tumor, the treatment angle is flagged as "Dangerous" and must be adjusted.

### 28. Flood Hazard Analysis (`flood_risk_analysis.py`)
**The Problem**: Climate change requires precise models to predict flood damage. Urban planners need to know which areas will be submerged and the total volume of water a basin will hold.
*   **Geometric Principle (Z-Thresholding)**: Using a terrain mesh, we compare every vertex's $Z$-coordinate against a predicted **Water Level**.
*   **Submergence Mapping**: Triangles with vertices below the threshold are identified as high-risk flood zones.
*   **Volumetric Capacity**: We calculate the **Flood Volume** by integrating the height difference ($WaterLevel - MeshHeight$) over the 2D projected area of every submerged triangle. This allows for the design of effective drainage and levee systems.

### 22. Vascular Stenting (`vascular_stenting.py`)
**The Problem**: A stent is a tiny wire mesh tube used to open up clogged arteries. Engineers must ensure the stent expands correctly to the vessel wall and covers enough surface area to keep the artery open without causing excessive irritation.
*   **Geometric Principle (Radial Scaling)**: We simulate the deployment by **Radial Scaling** the stent's vertices in the XY plane while preserving its longitudinal length.
*   **Metal-to-Artery Ratio (MAR)**: This is a critical clinical metric. We calculate the total surface area of the stent mesh $(\sum \text{Triangle Areas})$ and divide it by the internal surface area of the cylindrical vessel $(2\pi rh)$.
*   **Centerline Adaptation**: Real arteries are rarely straight. We use **Coordinate Transformations** to deform the cylindrical stent mesh so it follows a 3D spline representing the vessel's centerline.
