"""Green Architecture and GIS geometry analysis."""

from typing import List, Tuple, Optional
import math

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
    from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
    from compgeom.mesh.surfmesh.mesh_queries import MeshQueries
except ImportError:
    # Standalone fallbacks for external usage/testing
    class TriangleMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []

    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x, self.y, self.z = x, y, z

    class MeshAnalysis:
        @staticmethod
        def compute_face_normals(mesh):
            return [(0, 0, 1)] * len(mesh.faces)

        @staticmethod
        def compute_face_centers(mesh):
            centers = []
            for face in mesh.faces:
                v = [mesh.vertices[i] for i in face]
                centers.append(
                    (
                        sum(p.x for p in v) / 3,
                        sum(p.y for p in v) / 3,
                        sum(getattr(p, "z", 0.0) for p in v) / 3,
                    )
                )
            return centers

    class MeshQueries:
        @staticmethod
        def ray_intersect(mesh, start, dir):
            return []


class SolarAnalysis:
    """Provides algorithms for solar potential and urban visibility analysis."""

    @staticmethod
    def sun_position(
        latitude: float, day_of_year: int, hour: float
    ) -> Tuple[float, float, float]:
        """
        Calculates the sun direction vector based on latitude, day of year, and hour.
        Returns a normalized vector (X=East, Y=North, Z=Up).
        """
        # Declination (delta) in degrees
        delta = 23.45 * math.sin(math.radians(360.0 / 365.0 * (284.0 + day_of_year)))

        # Hour Angle (H) in degrees, solar noon at 12:00
        H = 15.0 * (hour - 12.0)

        lat_rad = math.radians(latitude)
        delta_rad = math.radians(delta)
        H_rad = math.radians(H)

        # Solar Elevation (alpha)
        sin_alpha = math.sin(lat_rad) * math.sin(delta_rad) + math.cos(
            lat_rad
        ) * math.cos(delta_rad) * math.cos(H_rad)
        alpha = math.asin(max(-1.0, min(1.0, sin_alpha)))

        if sin_alpha <= 0:
            return (0.0, 0.0, -1.0)  # Sun below horizon

        # Solar Azimuth (psi) from North (clockwise)
        # cos(psi) = (sin(delta) - sin(lat)*sin(alpha)) / (cos(lat)*cos(alpha))
        cos_alpha = math.cos(alpha)
        if cos_alpha < 1e-6:
            return (0.0, 0.0, 1.0)  # Sun at zenith

        cos_psi = (math.sin(delta_rad) - math.sin(lat_rad) * sin_alpha) / (
            math.cos(lat_rad) * cos_alpha
        )
        psi = math.acos(max(-1.0, min(1.0, cos_psi)))
        if H > 0:  # After noon, sun is in the West
            psi = 2 * math.pi - psi

        # Convert to direction vector (X=East, Y=North, Z=Up)
        dx = math.cos(alpha) * math.sin(psi)
        dy = math.cos(alpha) * math.cos(psi)
        dz = math.sin(alpha)

        return (dx, dy, dz)

    @staticmethod
    def sky_view_factor(
        mesh: TriangleMesh,
        point: Tuple[float, float, float],
        samples: int = 100,
        normal: Tuple[float, float, float] = (0, 0, 1),
    ) -> float:
        """
        Calculates the Sky View Factor (SVF) at a specific point on the surface.
        Ratio of visible sky to the entire hemisphere.
        """
        visible_sky = 0
        # Fibonacci sphere sampling for uniform hemisphere rays
        # For a general surface, we align rays with the surface normal

        # Build local coordinate system (TBN)
        nz = normal
        if abs(nz[0]) < 0.9:
            nx = (1, 0, 0)
        else:
            nx = (0, 1, 0)

        # nx = normalize(cross(nx, nz))
        tx = (
            nx[1] * nz[2] - nx[2] * nz[1],
            nx[2] * nz[0] - nx[0] * nz[2],
            nx[0] * nz[1] - nx[1] * nz[0],
        )
        mag_tx = math.sqrt(tx[0] ** 2 + tx[1] ** 2 + tx[2] ** 2)
        tx = (tx[0] / mag_tx, tx[1] / mag_tx, tx[2] / mag_tx)

        # ty = cross(nz, tx)
        ty = (
            nz[1] * tx[2] - nz[2] * tx[1],
            nz[2] * tx[0] - nz[0] * tx[2],
            nz[0] * tx[1] - nz[1] * tx[0],
        )

        for i in range(samples):
            phi = math.acos(1.0 - (i + 0.5) / samples)
            theta = math.pi * (1 + 5**0.5) * (i + 0.5)

            # Hemisphere ray in local space
            lx = math.sin(phi) * math.cos(theta)
            ly = math.sin(phi) * math.sin(theta)
            lz = math.cos(phi)

            # Transform to world space
            dx = lx * tx[0] + ly * ty[0] + lz * nz[0]
            dy = lx * tx[1] + ly * ty[1] + lz * nz[1]
            dz = lx * tx[2] + ly * ty[2] + lz * nz[2]

            # Cast ray
            if not MeshQueries.ray_intersect(mesh, point, (dx, dy, dz)):
                visible_sky += 1

        return visible_sky / samples

    @staticmethod
    def mesh_sky_view_factor(mesh: TriangleMesh, samples: int = 64) -> List[float]:
        """
        Calculates SVF for every face center of the mesh.
        """
        centers = MeshAnalysis.compute_face_centers(mesh)
        normals = MeshAnalysis.compute_face_normals(mesh)
        svf_values = []

        for i, center in enumerate(centers):
            # Offset center slightly to avoid self-intersection
            eps = 1e-5
            n = normals[i]
            offset_center = (
                center[0] + n[0] * eps,
                center[1] + n[1] * eps,
                center[2] + n[2] * eps,
            )
            svf_values.append(
                SolarAnalysis.sky_view_factor(mesh, offset_center, samples, n)
            )

        return svf_values

    @staticmethod
    def incident_solar_radiation(
        mesh: TriangleMesh,
        sun_dir: Tuple[float, float, float],
        intensity_direct: float = 1000.0,
        intensity_diffuse: Optional[float] = None,
        svf_values: Optional[List[float]] = None,
    ) -> List[float]:
        """
        Calculates solar radiation for each face (Direct + optional Diffuse).
        intensity_direct: W/m^2
        intensity_diffuse: W/m^2 (if None, estimated as 15% of direct)
        """
        normals = MeshAnalysis.compute_face_normals(mesh)
        centers = MeshAnalysis.compute_face_centers(mesh)
        radiation = [0.0] * len(mesh.faces)

        if intensity_diffuse is None:
            intensity_diffuse = intensity_direct * 0.15

        # Normalize sun direction
        s_mag = math.sqrt(sum(x**2 for x in sun_dir))
        if s_mag < 1e-9:
            return radiation
        s = (sun_dir[0] / s_mag, sun_dir[1] / s_mag, sun_dir[2] / s_mag)

        for i, face in enumerate(mesh.faces):
            # 1. Direct Radiation (Cosine law + Shadows)
            n = normals[i]
            dot = n[0] * s[0] + n[1] * s[1] + n[2] * s[2]
            direct = 0.0
            if dot > 0 and s[2] > 0:  # Sun must be above horizon and facing face
                c = centers[i]
                eps = 1e-5
                ray_start = (c[0] + n[0] * eps, c[1] + n[1] * eps, c[2] + n[2] * eps)
                if not MeshQueries.ray_intersect(mesh, ray_start, s):
                    direct = dot * intensity_direct

            # 2. Diffuse Radiation (Isotropic Sky model: Radiation ~ SVF)
            svf = svf_values[i] if svf_values else 0.5  # Default guess if not provided
            diffuse = svf * intensity_diffuse

            radiation[i] = direct + diffuse

        return radiation

    @staticmethod
    def daily_cumulative_radiation(
        mesh: TriangleMesh, latitude: float, day_of_year: int, step_hours: float = 1.0
    ) -> List[float]:
        """
        Simulates radiation over a whole day and returns cumulative Wh/m^2.
        """
        total_radiation = [0.0] * len(mesh.faces)
        svf_values = SolarAnalysis.mesh_sky_view_factor(mesh, samples=32)

        for h in range(0, 240, int(step_hours * 10)):
            hour = h / 10.0
            sun = SolarAnalysis.sun_position(latitude, day_of_year, hour)

            if sun[2] > 0:  # Sun above horizon
                # Simple clear-sky intensity model
                intensity = 1000.0 * sun[2]
                rad = SolarAnalysis.incident_solar_radiation(
                    mesh, sun, intensity, svf_values=svf_values
                )
                for i in range(len(rad)):
                    total_radiation[i] += rad[i] * step_hours

        return total_radiation


def main():
    print("--- solar_analysis.py Demo ---")
    mesh = TriangleMesh(
        vertices=[Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(0, 10, 0)],
        faces=[(0, 1, 2)],
    )
    tools = SolarAnalysis()

    # 1. Sun position
    sun_dir = tools.sun_position(latitude=45.0, day_of_year=172, hour=12.0)
    print(f"Sun position at noon (Summer Solstice, 45N): {sun_dir}")

    # 2. SVF
    svf = tools.sky_view_factor(mesh, (3.33, 3.33, 0.01), samples=100)
    print(f"Sky View Factor (Flat surface): {svf:.3f}")

    # 3. Incident Radiation
    radiation = tools.incident_solar_radiation(mesh, sun_dir)
    print(f"Incident radiation (Direct+Diffuse): {radiation[0]:.2f} W/m^2")

    # 4. Daily Cumulative
    cumulative = tools.daily_cumulative_radiation(mesh, latitude=45.0, day_of_year=172)
    print(f"Daily cumulative radiation: {cumulative[0]:.2f} Wh/m^2")

    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
