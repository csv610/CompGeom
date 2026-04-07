"""Boolean operations (CSG) for surface meshes."""
from typing import List, Tuple, Set

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D

class MeshBooleans:
    """Constructive Solid Geometry operations for triangle meshes."""

    @staticmethod
    def boolean_operation(mesh_a: TriMesh, mesh_b: TriMesh, operation: str = 'union') -> TriMesh:
        """
        Performs a boolean operation ('union', 'intersection', 'difference') on two meshes.
        Note: This is a simplified CSG algorithm using ray-casting classification.
        For production, a robust exact arithmetic kernel is required.
        """
        from compgeom.mesh.surface.mesh_queries import MeshQueries
        
        # 1. Classify vertices/faces of A against B
        # For simplicity, we classify based on centroids
        def classify_faces(mesh_target: TriMesh, mesh_tester: TriMesh) -> Tuple[List[int], List[int]]:
            inside_faces = []
            outside_faces = []
            
            for i, face in enumerate(mesh_target.faces):
                v0, v1, v2 = [mesh_target.vertices[idx] for idx in face]
                cx = (v0.x + v1.x + v2.x) / 3.0
                cy = (v0.y + v1.y + v2.y) / 3.0
                cz = (getattr(v0, 'z', 0.0) + getattr(v1, 'z', 0.0) + getattr(v2, 'z', 0.0)) / 3.0
                
                sdf = MeshQueries.compute_sdf(mesh_tester, (cx, cy, cz))
                if sdf < 0:
                    inside_faces.append(i)
                else:
                    outside_faces.append(i)
            return inside_faces, outside_faces

        inside_A, outside_A = classify_faces(mesh_a, mesh_b)
        inside_B, outside_B = classify_faces(mesh_b, mesh_a)
        
        # 2. Extract retained faces based on operation
        kept_faces_A = []
        kept_faces_B = []
        reverse_B = False
        
        if operation == 'union':
            kept_faces_A = outside_A
            kept_faces_B = outside_B
        elif operation == 'intersection':
            kept_faces_A = inside_A
            kept_faces_B = inside_B
        elif operation == 'difference': # A - B
            kept_faces_A = outside_A
            kept_faces_B = inside_B
            reverse_B = True
            
        # 3. Reconstruct combined mesh
        vertices = list(mesh_a.vertices)
        offset = len(vertices)
        vertices.extend([Point3D(v.x, v.y, getattr(v, 'z', 0.0)) for v in mesh_b.vertices])
        
        faces = []
        for f_idx in kept_faces_A:
            faces.append(mesh_a.faces[f_idx])
            
        for f_idx in kept_faces_B:
            f = mesh_b.faces[f_idx]
            if reverse_B:
                faces.append((f[0]+offset, f[2]+offset, f[1]+offset))
            else:
                faces.append((f[0]+offset, f[1]+offset, f[2]+offset))
                
        # Note: A complete CSG engine requires computing the exact intersection lines
        # and re-triangulating the intersecting faces. This version approximates it
        # by keeping or dropping whole faces (works well for dense meshes or voxel-like structures).
        
        from compgeom.mesh.surface.repair import remove_isolated_vertices
        combined = TriMesh(vertices, faces)
        # Clean up isolated vertices left over from dropped faces
        return remove_isolated_vertices(combined)

    @staticmethod
    def union(mesh_a: TriMesh, mesh_b: TriMesh) -> TriMesh:
        return MeshBooleans.boolean_operation(mesh_a, mesh_b, 'union')

    @staticmethod
    def intersection(mesh_a: TriMesh, mesh_b: TriMesh) -> TriMesh:
        return MeshBooleans.boolean_operation(mesh_a, mesh_b, 'intersection')

    @staticmethod
    def difference(mesh_a: TriMesh, mesh_b: TriMesh) -> TriMesh:
        return MeshBooleans.boolean_operation(mesh_a, mesh_b, 'difference')
