"""Image-based triangulation algorithms."""

from __future__ import annotations

import cv2
import numpy as np
from typing import List, Tuple, Optional
from compgeom.kernel import Point2D
from compgeom.mesh.surface.trimesh.delaunay_constrained import constrained_delaunay_triangulation


class BinaryImageTriangulation:
    """Class to perform triangulation from binary image contours."""

    def __init__(self, kernel_size: int = 3, approx_epsilon: float = 0.02):
        self.kernel_size = kernel_size
        self.approx_epsilon = approx_epsilon
        self.original_image: Optional[np.ndarray] = None
        self.cleaned_image: Optional[np.ndarray] = None
        self.edges: Optional[np.ndarray] = None
        self.contours: List[np.ndarray] = []
        self.hierarchy: Optional[np.ndarray] = None
        self.bbox: List[Point2D] = []
        self.white_triangles: List[Tuple[Point2D, Point2D, Point2D]] = []
        self.black_triangles: List[Tuple[Point2D, Point2D, Point2D]] = []

    def read_image(self, path: str) -> np.ndarray:
        """Reads image from path as grayscale."""
        self.original_image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if self.original_image is None:
            raise FileNotFoundError(f"Could not read image at {path}")
        return self.original_image

    def clean_image(self) -> np.ndarray:
        """Applies binary threshold and morphological cleaning."""
        if self.original_image is None:
            raise ValueError("No image loaded. Call read_image() first.")

        # Binary thresholding
        _, binary = cv2.threshold(self.original_image, 127, 255, cv2.THRESH_BINARY)

        # Morphological opening and closing
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        self.cleaned_image = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        self.cleaned_image = cv2.morphologyEx(self.cleaned_image, cv2.MORPH_CLOSE, kernel)
        return self.cleaned_image

    def detect_edges(self, low_threshold: int = 100, high_threshold: int = 200) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Performs Canny edge detection and finds contours."""
        if self.cleaned_image is None:
            self.clean_image()

        self.edges = cv2.Canny(self.cleaned_image, low_threshold, high_threshold)

        # RETR_CCOMP is used to get two levels of hierarchy: outer and holes
        self.contours, self.hierarchy = cv2.findContours(self.cleaned_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return self.edges, self.contours

    def create_bounding_box(self) -> List[Point2D]:
        """Creates a bounding box for the entire image."""
        if self.cleaned_image is None:
            self.clean_image()

        h, w = self.cleaned_image.shape
        # Add small padding to avoid overlapping with image borders if needed
        self.bbox = [
            Point2D(0.0, 0.0),
            Point2D(float(w - 1), 0.0),
            Point2D(float(w - 1), float(h - 1)),
            Point2D(0.0, float(h - 1)),
        ]
        return self.bbox

    def compute_triangulations(
        self,
    ) -> Tuple[List[Tuple[Point2D, Point2D, Point2D]], List[Tuple[Point2D, Point2D, Point2D]]]:
        """Constructs constrained triangulations for black and white parts."""
        if self.contours is None or self.hierarchy is None:
            self.detect_edges()
        if not self.bbox:
            self.create_bounding_box()

        self.white_triangles = []
        self.black_triangles = []

        hierarchy = self.hierarchy[0]

        # Collect white islands (top-level contours) and their black holes
        white_islands: List[Tuple[List[Point2D], List[List[Point2D]]]] = []

        for i, h in enumerate(hierarchy):
            # h: [Next, Previous, First_Child, Parent]
            if h[3] == -1:  # Outer boundary in RETR_CCOMP
                outer = self._to_point2d(self.contours[i])
                if len(outer) < 3:
                    continue

                holes: List[List[Point2D]] = []
                child_idx = h[2]
                while child_idx != -1:
                    hole = self._to_point2d(self.contours[child_idx])
                    if len(hole) >= 3:
                        holes.append(hole)
                    child_idx = hierarchy[child_idx][0]

                white_islands.append((outer, holes))

        # Triangulate white parts
        for outer, holes in white_islands:
            tri, _ = constrained_delaunay_triangulation(outer, holes)
            self.white_triangles.extend(tri)

            # Holes in white islands are black parts
            for hole in holes:
                h_tri, _ = constrained_delaunay_triangulation(hole, None)
                self.black_triangles.extend(h_tri)

        # Triangulate the rest of the black part (Bounding Box minus all white islands)
        all_islands_outer = [island[0] for island in white_islands]
        remaining_black, _ = constrained_delaunay_triangulation(self.bbox, all_islands_outer)
        self.black_triangles.extend(remaining_black)

        return self.white_triangles, self.black_triangles

    def _to_point2d(self, contour: np.ndarray) -> List[Point2D]:
        """Converts opencv contour to list of Point2D with simplification."""
        epsilon = self.approx_epsilon * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        return [Point2D(float(pt[0][0]), float(pt[0][1])) for pt in approx]
