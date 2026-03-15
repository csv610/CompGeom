"""Provides efficient spatial range searching for points in 2D and 3D."""

import numpy as np
from scipy.spatial import KDTree
from typing import List, Union, Any, Optional

class RangeSearch:
    """
    A class for performing range search queries on a set of points.
    
    Supports finding points within:
    - Sphere (Euclidean distance)
    - Box (Axis-aligned bounding box)
    - Cube (Equi-sided axis-aligned box)
    - Square (2D equi-sided axis-aligned box)
    """

    def __init__(self, points: Union[np.ndarray, List[Any]]):
        """
        Initializes the RangeSearch with a set of points.
        
        Args:
            points: A list of Point2D/Point3D objects (with .x, .y, .z attributes) 
                   or an (N, D) numpy array.
        """
        if isinstance(points, np.ndarray):
            self.points = points
        else:
            self.points = self._convert_points_to_numpy(points)
            
        self.tree = KDTree(self.points)

    def _convert_points_to_numpy(self, points: List[Any]) -> np.ndarray:
        """Converts a list of Point2D/Point3D objects to a numpy array."""
        coords = []
        for p in points:
            if hasattr(p, 'z'):
                coords.append([p.x, p.y, p.z])
            elif hasattr(p, 'x'):
                coords.append([p.x, p.y])
            elif isinstance(p, (list, tuple)):
                coords.append(p)
            elif isinstance(p, np.ndarray):
                coords.append(p.tolist())
            else:
                try:
                    coords.append(list(p))
                except TypeError:
                    raise ValueError(f"Unsupported point type: {type(p)}")
        return np.array(coords)

    def _to_coords(self, pt: Any) -> np.ndarray:
        """Converts a single point-like object to a numpy coordinate array."""
        if isinstance(pt, np.ndarray):
            return pt
        if hasattr(pt, 'z'):
            return np.array([pt.x, pt.y, pt.z])
        if hasattr(pt, 'x'):
            return np.array([pt.x, pt.y])
        return np.asarray(pt)

    def within_sphere(self, center: Any, radius: float) -> List[int]:
        """
        Finds indices of points within a sphere of given radius.
        
        Args:
            center: Center of the sphere (Point object, list, or numpy array).
            radius: Radius of the sphere.
            
        Returns:
            Indices of points within the sphere.
        """
        center_coords = self._to_coords(center)
        return self.tree.query_ball_point(center_coords, radius, p=2)

    def within_cube(self, center: Any, half_side: float) -> List[int]:
        """
        Finds indices of points within an axis-aligned cube.
        
        Args:
            center: Center of the cube (Point object, list, or numpy array).
            half_side: Half of the side length (distance from center to any face).
            
        Returns:
            Indices of points within the cube.
        """
        center_coords = self._to_coords(center)
        return self.tree.query_ball_point(center_coords, half_side, p=np.inf)

    def within_square(self, center: Any, half_side: float) -> List[int]:
        """
        Finds indices of points within an axis-aligned square (2D).
        
        Args:
            center: Center of the square (Point object, list, or numpy array).
            half_side: Half of the side length.
            
        Returns:
            Indices of points within the square.
        """
        return self.within_cube(center, half_side)

    def within_box(self, min_pt: Any, max_pt: Any) -> List[int]:
        """
        Finds indices of points within an axis-aligned bounding box.
        
        Args:
            min_pt: Minimum coordinates of the box.
            max_pt: Maximum coordinates of the box.
            
        Returns:
            Indices of points within the box.
        """
        min_coords = self._to_coords(min_pt)
        max_coords = self._to_coords(max_pt)
        
        # Efficiently filter using numpy's vectorized comparison
        mask = np.all((self.points >= min_coords) & (self.points <= max_coords), axis=1)
        return np.where(mask)[0].tolist()

    def get_points(self, indices: List[int]) -> np.ndarray:
        """Returns the coordinates of the points at the specified indices."""
        return self.points[indices]
