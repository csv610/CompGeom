"""Additive Manufacturing (3D Printing) geometry algorithms."""

import math
import argparse
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    # Standalone execution
    TriangleMesh = object
    Point3D = object


class AdditiveMfg:
    """Provides algorithms for 3D printing analysis and support generation."""

    @staticmethod
    def detect_overhangs(
        mesh: TriangleMesh,
        threshold_angle_deg: float = 45.0,
        gravity_dir: Tuple[float, float, float] = (0, 0, -1),
    ) -> Tuple[List[int], float]:
        """
        Identifies faces that require support structures.
        Returns a tuple of (list of face indices, total overhang area).
        """
        from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

        face_normals = MeshAnalysis.compute_face_normals(mesh)
        faces = mesh.faces()
        verts = mesh.vertices()

        # Normalize gravity
        g_mag = math.sqrt(sum(x**2 for x in gravity_dir))
        if g_mag == 0:
            raise ValueError("Gravity direction cannot be a zero vector.")
        g = (gravity_dir[0] / g_mag, gravity_dir[1] / g_mag, gravity_dir[2] / g_mag)

        # Overhang if angle between normal and gravity is small (normal points down)
        # Cos(theta) > cos(90 - threshold)
        limit_cos = math.cos(math.radians(90.0 - threshold_angle_deg))

        overhang_faces = []
        total_overhang_area = 0.0
        for i, n in enumerate(face_normals):
            # Dot product with -gravity (upward vector)
            dot = n[0] * (-g[0]) + n[1] * (-g[1]) + n[2] * (-g[2])
            if dot < limit_cos:  # Points mostly "down"
                overhang_faces.append(i)
                f = faces[i]
                v0, v1, v2 = [verts[idx] for idx in f]
                total_overhang_area += AdditiveMfg._calculate_triangle_area(
                    (v0.x, v0.y, v0.z), (v1.x, v1.y, v1.z), (v2.x, v2.y, v2.z)
                )

        return overhang_faces, total_overhang_area

    @staticmethod
    def estimate_print_time(
        mesh: TriangleMesh, layer_height: float, speed: float
    ) -> float:
        """
        Provides a very rough estimate of 3D printing time based on surface area and layers.
        """
        from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

        bbox = mesh.bounding_box()
        height = bbox[1][2] - bbox[0][2]
        num_layers = height / layer_height

        area = MeshAnalysis.total_area(mesh)
        # Simplified: proportional to (Area * Layers) / Speed
        return (area * num_layers) / (speed * 100.0)

    @staticmethod
    def sample_quaternions(
        num_samples: int = 100, seed: int = 42
    ) -> List[Tuple[float, float, float, float]]:
        """
        Samples unit quaternions uniformly on the S3 sphere using Shoemake's algorithm.
        Returns a list of quaternions as (w, x, y, z) tuples.
        """
        import random

        rng = random.Random(seed)
        quaternions = []
        for _ in range(num_samples):
            u1, u2, u3 = rng.random(), rng.random(), rng.random()
            q = (
                math.sqrt(u1) * math.cos(2 * math.pi * u3),  # w
                math.sqrt(1 - u1) * math.sin(2 * math.pi * u2),  # x
                math.sqrt(1 - u1) * math.cos(2 * math.pi * u2),  # y
                math.sqrt(u1) * math.sin(2 * math.pi * u3),  # z
            )
            quaternions.append(q)
        return quaternions

    @staticmethod
    def _rotate_vector_by_quaternion(
        v: Tuple[float, float, float], q: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Rotates a vector v by a unit quaternion q = (w, x, y, z).
        """
        w, x, y, z = q
        vx, vy, vz = v
        # v' = v + 2 * q_vec x (q_vec x v + w * v)
        # where q_vec = (x, y, z)

        # t = 2 * (x, y, z) x (vx, vy, vz)
        tx = 2 * (y * vz - z * vy)
        ty = 2 * (z * vx - x * vz)
        tz = 2 * (x * vy - y * vx)

        # v' = v + w * t + (x, y, z) x t
        rvx = vx + w * tx + (y * tz - z * ty)
        rvy = vy + w * ty + (z * tx - x * tz)
        rvz = vz + w * tz + (x * ty - y * tx)

        return (rvx, rvy, rvz)

    @staticmethod
    def _calculate_triangle_area(
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> float:
        """Calculates the area of a 3D triangle."""
        # cross product (v1-v0) x (v2-v0)
        ax, ay, az = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
        bx, by, bz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
        cx = ay * bz - az * by
        cy = az * bx - ax * bz
        cz = ax * by - ay * bx
        return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)

    @staticmethod
    def find_optimal_rotation(
        mesh: TriangleMesh,
        num_samples: int = 100,
        threshold_angle_deg: float = 45.0,
        gravity_dir: Tuple[float, float, float] = (0, 0, -1),
        alpha: float = 0.0,
    ) -> Tuple[Tuple[float, float, float, float], float, float]:
        """
        Finds the optimal rotation of the mesh using normalized objective functions.
        Returns (best_quaternion, min_overhang_area, stability_score_0_to_1).
        """
        from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

        face_normals = MeshAnalysis.compute_face_normals(mesh)
        faces = mesh.faces()
        verts = mesh.vertices()

        # Precompute face areas, centroids, and vertex positions
        face_data = []
        total_mesh_area = 0.0
        for f in faces:
            v0, v1, v2 = [verts[idx] for idx in f]
            v0t, v1t, v2t = (v0.x, v0.y, v0.z), (v1.x, v1.y, v1.z), (v2.x, v2.y, v2.z)
            area = AdditiveMfg._calculate_triangle_area(v0t, v1t, v2t)
            centroid = (
                (v0t[0] + v1t[0] + v2t[0]) / 3.0,
                (v0t[1] + v1t[1] + v2t[1]) / 3.0,
                (v0t[2] + v1t[2] + v2t[2]) / 3.0,
            )
            face_data.append((area, centroid))
            total_mesh_area += area

        verts_t = [(v.x, v.y, v.z) for v in verts]

        # Normalize gravity and find "up" vector (-gravity)
        g_mag = math.sqrt(sum(x**2 for x in gravity_dir))
        if g_mag == 0:
            raise ValueError("Gravity direction cannot be a zero vector.")
        up = (-gravity_dir[0] / g_mag, -gravity_dir[1] / g_mag, -gravity_dir[2] / g_mag)

        limit_cos = math.cos(math.radians(90.0 - threshold_angle_deg))

        best_q = (1.0, 0.0, 0.0, 0.0)
        best_total_score = float("inf")
        best_overhang_area = total_mesh_area
        best_stability_ratio = 1.0

        samples = AdditiveMfg.sample_quaternions(num_samples)
        if (1.0, 0.0, 0.0, 0.0) not in samples:
            samples.insert(0, (1.0, 0.0, 0.0, 0.0))

        for q in samples:
            q_inv = (q[0], -q[1], -q[2], -q[3])
            up_rot = AdditiveMfg._rotate_vector_by_quaternion(up, q_inv)

            # Find the "print bed" and "top" for height normalization
            heights = [
                v[0] * up_rot[0] + v[1] * up_rot[1] + v[2] * up_rot[2] for v in verts_t
            ]
            min_h = min(heights)
            max_h = max(heights)
            total_height = max_h - min_h

            overhang_area = 0.0
            total_moment = 0.0

            for i, (area, centroid) in enumerate(face_data):
                n = face_normals[i]
                # Overhang check
                if (n[0] * up_rot[0] + n[1] * up_rot[1] + n[2] * up_rot[2]) < limit_cos:
                    overhang_area += area

                # Height above print bed
                h = (
                    centroid[0] * up_rot[0]
                    + centroid[1] * up_rot[1]
                    + centroid[2] * up_rot[2]
                ) - min_h
                total_moment += area * h

            # Normalized Overhang Score (0 to 1)
            overhang_ratio = (
                overhang_area / total_mesh_area if total_mesh_area > 0 else 0
            )

            # Normalized Stability Score (0 to 1)
            avg_h = total_moment / total_mesh_area if total_mesh_area > 0 else 0
            stability_ratio = avg_h / total_height if total_height > 0 else 0

            # Combined Weighted Score
            total_score = (1 - alpha) * overhang_ratio + alpha * stability_ratio

            if total_score < best_total_score:
                best_total_score = total_score
                best_q = q
                best_overhang_area = overhang_area
                best_stability_ratio = stability_ratio

        return best_q, best_overhang_area, best_stability_ratio

    @staticmethod
    def _ray_triangle_intersection(
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> float:
        """
        Moller-Trumbore intersection algorithm.
        Returns distance to intersection, or -1.0 if no intersection.
        """
        eps = 1e-6
        edge1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        edge2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        h = (
            ray_dir[1] * edge2[2] - ray_dir[2] * edge2[1],
            ray_dir[2] * edge2[0] - ray_dir[0] * edge2[2],
            ray_dir[0] * edge2[1] - ray_dir[1] * edge2[0],
        )
        a = edge1[0] * h[0] + edge1[1] * h[1] + edge1[2] * h[2]

        if -eps < a < eps:
            return -1.0

        f = 1.0 / a
        s = (ray_origin[0] - v0[0], ray_origin[1] - v0[1], ray_origin[2] - v0[2])
        u = f * (s[0] * h[0] + s[1] * h[1] + s[2] * h[2])

        if u < 0.0 or u > 1.0:
            return -1.0

        q = (
            s[1] * edge1[2] - s[2] * edge1[1],
            s[2] * edge1[0] - s[0] * edge1[2],
            s[0] * edge1[1] - s[1] * edge1[0],
        )
        v = f * (ray_dir[0] * q[0] + ray_dir[1] * q[1] + ray_dir[2] * q[2])

        if v < 0.0 or u + v > 1.0:
            return -1.0

        t = f * (edge2[0] * q[0] + edge2[1] * q[1] + edge2[2] * q[2])

        if t > eps:
            return t
        return -1.0

    @staticmethod
    def identify_thin_structures(mesh: TriangleMesh, min_thickness: float) -> List[int]:
        """
        Identifies faces that belong to thin walls (thickness < min_thickness).
        Uses ray casting inward from each face.
        """
        from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

        face_normals = MeshAnalysis.compute_face_normals(mesh)
        faces = mesh.faces()
        verts = mesh.vertices()

        thin_faces = []

        for i, face_indices in enumerate(faces):
            v0, v1, v2 = [verts[idx] for idx in face_indices]
            # Convert Point3D/objects to tuples if necessary
            v0 = (v0.x, v0.y, v0.z)
            v1 = (v1.x, v1.y, v1.z)
            v2 = (v2.x, v2.y, v2.z)

            centroid = (
                (v0[0] + v1[0] + v2[0]) / 3.0,
                (v0[1] + v1[1] + v2[1]) / 3.0,
                (v0[2] + v1[2] + v2[2]) / 3.0,
            )
            n = face_normals[i]
            # Ray direction is inward (opposite to normal)
            ray_dir = (-n[0], -n[1], -n[2])

            # Start slightly inside the face to avoid hitting itself
            eps = 1e-4
            ray_origin = (
                centroid[0] + ray_dir[0] * eps,
                centroid[1] + ray_dir[1] * eps,
                centroid[2] + ray_dir[2] * eps,
            )

            min_dist = float("inf")
            for j, target_face_indices in enumerate(faces):
                if i == j:
                    continue
                tv0, tv1, tv2 = [verts[idx] for idx in target_face_indices]
                tv0 = (tv0.x, tv0.y, tv0.z)
                tv1 = (tv1.x, tv1.y, tv1.z)
                tv2 = (tv2.x, tv2.y, tv2.z)

                dist = AdditiveMfg._ray_triangle_intersection(
                    ray_origin, ray_dir, tv0, tv1, tv2
                )
                if 0 < dist < min_dist:
                    min_dist = dist

            if min_dist < min_thickness:
                thin_faces.append(i)

        return thin_faces

    @staticmethod
    def filter_printable_mesh(mesh: TriangleMesh, min_thickness: float) -> TriangleMesh:
        """
        Returns a new mesh with thin structures removed.
        """
        thin_face_indices = set(
            AdditiveMfg.identify_thin_structures(mesh, min_thickness)
        )

        from compgeom.mesh import TriangleMesh

        all_faces = mesh.faces()
        verts = mesh.vertices()

        printable_triangles = []
        for i, f in enumerate(all_faces):
            if i not in thin_face_indices:
                v0, v1, v2 = [verts[idx] for idx in f]
                printable_triangles.append((v0, v1, v2))

        if not printable_triangles:
            # If everything is thin, return empty mesh or similar?
            # Let's return empty if all thin.
            return TriangleMesh.from_triangles([])

        return TriangleMesh.from_triangles(printable_triangles)


def main():
    """Demonstrates the Additive Manufacturing algorithms."""
    parser = argparse.ArgumentParser(
        description="Additive Manufacturing Algorithm Demo"
    )
    parser.add_argument("mesh_file", help="Path to the mesh file (e.g., model.stl)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=45.0,
        help="Threshold angle for overhang detection in degrees (default: 45.0)",
    )
    parser.add_argument(
        "--gravity",
        type=float,
        nargs=3,
        default=[0.0, 0.0, -1.0],
        metavar=("X", "Y", "Z"),
        help="Gravity direction vector (default: 0 0 -1)",
    )
    parser.add_argument(
        "--layer-height",
        type=float,
        default=0.2,
        help="Layer height for print time estimation (default: 0.2)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=50.0,
        help="Print speed for time estimation (default: 50.0)",
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Find the optimal rotation of the mesh."
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of quaternion samples for optimization (default: 100)",
    )
    parser.add_argument(
        "--min-thickness",
        type=float,
        help="Minimum wall thickness. If set, will identify and filter thin structures.",
    )
    parser.add_argument(
        "--out-mesh", type=str, help="Path to save the filtered printable mesh."
    )
    parser.add_argument(
        "--stable",
        action="store_true",
        help="Optimize for stability (bottom-heavy) instead of just support count.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.0,
        help="Weight for stability optimization (0.0 to 1.0). Default 0.0 (supports only).",
    )

    args = parser.parse_args()

    alpha = args.alpha
    if args.stable and alpha == 0.0:
        alpha = 1.0

    print(f"Opening mesh file: {args.mesh_file}")

    try:
        # Load the actual mesh from the file
        mesh = TriangleMesh.from_file(args.mesh_file)
    except Exception as e:
        print(f"Error loading mesh: {e}")
        return

    # Thin structure analysis
    if args.min_thickness:
        print(f"Analyzing wall thickness (min: {args.min_thickness})...")
        thin_faces = AdditiveMfg.identify_thin_structures(mesh, args.min_thickness)
        print(f"Number of thin faces identified: {len(thin_faces)}")

        if args.out_mesh:
            print(f"Filtering mesh and saving to {args.out_mesh}...")
            AdditiveMfg.filter_printable_mesh(mesh, args.min_thickness)
            print("Filtered mesh generated.")

    if args.optimize:
        print(f"Detecting initial overhangs for mesh: {args.mesh_file}...")
        initial_overhangs, initial_area = AdditiveMfg.detect_overhangs(
            mesh, threshold_angle_deg=args.threshold, gravity_dir=tuple(args.gravity)
        )
        print(f"Initial number of faces requiring support: {len(initial_overhangs)}")
        print(f"Initial overhang area: {initial_area:.4f}")

        print(
            f"Finding optimal rotation using {args.samples} quaternion samples (alpha={alpha})..."
        )
        best_q, min_area, stability_ratio = AdditiveMfg.find_optimal_rotation(
            mesh,
            num_samples=args.samples,
            threshold_angle_deg=args.threshold,
            gravity_dir=tuple(args.gravity),
            alpha=alpha,
        )
        print(f"Optimal rotation found (quaternion [w, x, y, z]): {best_q}")
        print(f"Overhang area in this orientation: {min_area:.4f}")
        print(f"Normalized stability score (0=bottom, 1=top): {stability_ratio:.4f}")

        if alpha == 0:
            reduction = initial_area - min_area
            if reduction > 0:
                print(
                    f"Optimization reduced support area by {reduction:.4f} ({reduction/initial_area*100:.1f}%)"
                )
            else:
                print(
                    "Initial orientation is already optimal for supports among samples."
                )
        else:
            print("Optimization completed for stability/combined objective.")
    else:
        # Overhang detection
        print(
            f"Detecting overhangs for mesh: {args.mesh_file} (threshold: {args.threshold} deg, gravity: {args.gravity})..."
        )
        overhangs, area = AdditiveMfg.detect_overhangs(
            mesh, threshold_angle_deg=args.threshold, gravity_dir=tuple(args.gravity)
        )
        print(f"Number of faces requiring support: {len(overhangs)}")
        print(f"Total overhang area: {area:.4f}")
        if len(overhangs) > 0:
            # Display a sample of overhang faces
            print(f"Indices of first 10 faces requiring support: {overhangs[:10]}")

    # Print time estimation
    print(
        f"Estimating print time (layer height: {args.layer_height}, speed: {args.speed})..."
    )
    est_time = AdditiveMfg.estimate_print_time(mesh, args.layer_height, args.speed)

    print(f"Estimated 3D printing time for {args.mesh_file}: {est_time:.4f} hours")
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
