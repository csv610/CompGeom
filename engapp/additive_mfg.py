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
    def detect_overhangs(mesh: TriangleMesh, threshold_angle_deg: float = 45.0, 
                         gravity_dir: Tuple[float,float,float] = (0,0,-1)) -> List[int]:
        """
        Identifies faces that require support structures.
        An overhang is a face whose normal points too far away from the gravity vector.
        """
        from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        
        # Normalize gravity
        g_mag = math.sqrt(sum(x**2 for x in gravity_dir))
        if g_mag == 0:
            raise ValueError("Gravity direction cannot be a zero vector.")
        g = (gravity_dir[0]/g_mag, gravity_dir[1]/g_mag, gravity_dir[2]/g_mag)
        
        # Overhang if angle between normal and gravity is small (normal points down)
        # Cos(theta) > cos(90 - threshold)
        limit_cos = math.cos(math.radians(90.0 - threshold_angle_deg))
        
        overhang_faces = []
        for i, n in enumerate(face_normals):
            # Dot product with -gravity (upward vector)
            dot = n[0]*(-g[0]) + n[1]*(-g[1]) + n[2]*(-g[2])
            if dot < limit_cos: # Points mostly "down"
                overhang_faces.append(i)
                
        return overhang_faces

    @staticmethod
    def estimate_print_time(mesh: TriangleMesh, layer_height: float, speed: float) -> float:
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

def main():
    """Demonstrates the Additive Manufacturing algorithms."""
    parser = argparse.ArgumentParser(description="Additive Manufacturing Algorithm Demo")
    parser.add_argument("mesh_file", help="Path to the mesh file (e.g., model.stl)")
    parser.add_argument("--threshold", type=float, default=45.0, help="Threshold angle for overhang detection in degrees (default: 45.0)")
    parser.add_argument("--gravity", type=float, nargs=3, default=[0.0, 0.0, -1.0], metavar=('X', 'Y', 'Z'), help="Gravity direction vector (default: 0 0 -1)")
    parser.add_argument("--layer-height", type=float, default=0.2, help="Layer height for print time estimation (default: 0.2)")
    parser.add_argument("--speed", type=float, default=50.0, help="Print speed for time estimation (default: 50.0)")
    
    args = parser.parse_args()
    
    print(f"Opening mesh file: {args.mesh_file}")

    try:
        # Load the actual mesh from the file
        mesh = TriangleMesh.from_file(args.mesh_file)
    except Exception as e:
        print(f"Error loading mesh: {e}")
        return

    # Overhang detection
    print(f"Detecting overhangs for mesh: {args.mesh_file} (threshold: {args.threshold} deg, gravity: {args.gravity})...")
    overhangs = AdditiveMfg.detect_overhangs(mesh, threshold_angle_deg=args.threshold, gravity_dir=tuple(args.gravity))
    print(f"Number of faces requiring support: {len(overhangs)}")
    if len(overhangs) > 0:
        # Display a sample of overhang faces
        print(f"Indices of first 10 faces requiring support: {overhangs[:10]}")
    
    # Print time estimation
    print(f"Estimating print time (layer height: {args.layer_height}, speed: {args.speed})...")
    est_time = AdditiveMfg.estimate_print_time(mesh, args.layer_height, args.speed)
    
    print(f"Estimated 3D printing time for {args.mesh_file}: {est_time:.4f} hours")
    print("Demo completed successfully.")

if __name__ == "__main__":
    main()
